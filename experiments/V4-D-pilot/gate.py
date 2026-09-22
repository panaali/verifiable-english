"""One preregistered, content-free Opus identity gate; permanently stop on failure."""
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess

from ve_experiments.claude_cli import ClaudeCLI, Controls, EndpointError, MODELS

HERE = Path(__file__).resolve().parent


def dump(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def identities(raw):
    found = set()
    for line in raw.splitlines():
        try:
            row = json.loads(line)
        except ValueError:
            continue
        if row.get("type") == "system" and row.get("subtype") == "init":
            found.add(row.get("model"))
        if row.get("type") == "assistant":
            found.add(row.get("message", {}).get("model"))
        if row.get("type") == "result":
            found.update(row.get("modelUsage", {}))
    return sorted(str(model) for model in found)


def main():
    out = HERE / "results"
    out.mkdir(exist_ok=True)
    if (out / "STOP.json").exists():
        raise EndpointError("D pilot permanently stopped; see results/STOP.json")
    prereg = HERE / "PREREG-D-pilot.md"
    receipt = HERE / "PREREG-D-pilot.md.ots"
    for path in (prereg, receipt):
        if not path.is_file():
            raise EndpointError("Missing preregistration or OTS receipt")
        subprocess.run(["git", "ls-files", "--error-unmatch", str(path)],
                       check=True, capture_output=True)
        subprocess.run(["git", "diff", "--exit-code", "HEAD", "--", str(path)],
                       check=True, capture_output=True)
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    controls = Controls(model=MODELS["opus"], thinking_tokens=1024,
                        output_tokens=24000, timeout_s=300,
                        context_date=datetime.now(timezone.utc).date().isoformat())
    client = ClaudeCLI(out / "gate-ledger.jsonl", controls, max_calls=1)
    manifest = {"prereg_commit": commit, "prereg_sha256": hashlib.sha256(prereg.read_bytes()).hexdigest(),
                "ots_sha256": hashlib.sha256(receipt.read_bytes()).hexdigest(),
                "controls": asdict(controls), "planned_calls": 673, "hard_max_calls": 790}
    manifest_path = out / "gate-manifest.json"
    if manifest_path.exists():
        old = json.loads(manifest_path.read_text())
        # A later commit does not invalidate a completed, immutable gate.
        manifest["prereg_commit"] = old["prereg_commit"]
        if manifest != old:
            raise EndpointError("Gate manifest drift")
    else:
        dump(manifest_path, manifest)
    try:
        row = client.sample("d-opus-identity-gate", "You are an experimental text endpoint.",
                            "Reply with exactly OK.")
        if row["text"].strip() != "OK":
            raise EndpointError("Content-free gate did not return OK")
    except Exception as exc:
        rows = [json.loads(x) for x in client.ledger.read_text().splitlines()] if client.ledger.exists() else []
        final = rows[-1] if rows else {}
        stop = {"status": "stopped", "stage": "opus_identity_gate", "error": str(exc),
                "expected_model": MODELS["opus"], "observed_model_ids": identities(final.get("raw_stream", "")),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "started_calls": sum(r["status"] == "started" for r in rows),
                "accepted_experimental_samples": 0, "substituted_models": False}
        dump(out / "STOP.json", stop)
        print(json.dumps(stop), flush=True)
        raise SystemExit(2) from exc
    result = {"status": "passed", "served_model": row["served_model"],
              "key": row["key"], "timestamp": row["timestamp"],
              "input_tokens": row["input_tokens"], "output_tokens": row["output_tokens"]}
    dump(out / "gate-pass.json", result)
    print(json.dumps(result), flush=True)


if __name__ == "__main__":
    main()
