"""ME-0: build each target's ledger as a `ve-document@1` and let today's VE (Lean) check and measure it.

For a labels module `labels/<name>.py`, per source file:
  1. segment the pinned source into sentence units (`segment.py`; rules fixed before labelling);
  2. attach each unit's plan kind and status from the labels: LABELLED (W2 `meta`/`exposition`, no content),
     UNFORMALISED with one `missing_feature` (W2 `["unformalised", feature]`), CHECKED (W2 `asserted` with W6a
     `ve-quantity@1` content, support `testimony`), or MIXED parts at the labels' anchors;
  3. write `<source>.ve.md`, whose prose is the pinned source byte for byte, with the labels' certified
     consequences as graph nodes (certificates from `ve.units.prove_quantity`; Lean replays them);
  4. run `ve document check` and `ve document coverage` in today's VE (`VE_CHECKOUT`, default the built
     `main` checkout) under `prlimit --as=6442450944`, and write `<source>.check.json`, `<source>.coverage.json`
     and `<source>.units.json` (unit, span, bytes, plan kind, status, feature).

Run with today's VE's interpreter, so `ve` is importable from that checkout:

    prlimit --as=6442450944 $VE_CHECKOUT/.venv/bin/python -I research/math-evidence/ledger.py <labels> [--control]

`--control` builds a copy with the labels' `CONTROL` mutation (one printed number changed while the certificate
built for the true number is kept) and records Lean's answer: the negative control that Lean, not this script,
checks the certificates.
"""
from __future__ import annotations

import copy
import hashlib
import importlib
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
EVIDENCE = ROOT / "docs/research/evidence/math-evidence"
CHECKOUT = Path(os.environ.get("VE_CHECKOUT", "/home/seyran/code/ve-pilot-20261013T0600Z"))
LIMIT = ["prlimit", "--as=6442450944"]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(CHECKOUT))

from segment import units as segment_units  # noqa: E402
from ve.environment import Environment  # noqa: E402
from ve.units import prove_quantity, quantity_meaning_id  # noqa: E402

PLAN_KINDS = {"exposition", "definition", "theorem", "proof step", "equation", "quantity", "table",
              "empirical claim", "comparison", "hedge", "citation", "caption", "meta"}
FEATURES = {"calc", "calc-data", "calc-derive", "calc-dimension", "calc-stats", "calc-algebra", "arith",
            "arith-import", "approximation", "quantities", "attitudes", "events", "attribution"}
BASE_ENV = {"language": "ve.core@0.2", "profiles": ["documents@1", "order@0", "relational-fol@0", "time@0"],
            "spec_revision": "ve-v0.2-expand2-2026-09-25"}


def q(formula):
    return {"format": "ve-quantity@1", "formula": formula}


def _w2(kind: str, status: str, arg, env) -> dict:
    assert kind in PLAN_KINDS, kind
    if status == "L":
        return {"kind": "meta" if kind in ("meta", "citation", "caption") else "exposition",
                "meaning": "specified", "support": "none"}
    if status == "U":
        assert arg in FEATURES, arg
        return {"kind": ["unformalised", arg], "meaning": {"unformalised": arg}, "support": "none"}
    if status == "C":
        content = q(arg)
        return {"kind": "asserted", "meaning": "specified", "support": "testimony",
                "content": {"quantity": content}, "meaning_id": quantity_meaning_id(env, content)}
    raise ValueError(status)


STATUS = {"L": "LABELLED", "U": "UNFORMALISED", "C": "CHECKED"}


def _units(specs, seg, data, env, source_name):
    missing = [u["id"] for u in seg if u["id"] not in specs]
    if missing:
        raise SystemExit(f"{source_name}: unlabelled {missing[:10]}")
    doc_units, ledger = [], []
    for u in seg:
        a, b = u["span"]
        spec = specs[u["id"]]
        if spec[0] != "mixed":
            kind, status = spec[0], spec[1]
            arg = spec[2] if len(spec) > 2 else None
            doc_units.append({"id": u["id"], "span": [a, b], **_w2(kind, status, arg, env)})
            ledger.append({"id": u["id"], "span": [a, b], "bytes": b - a, "kind": kind, "status": STATUS[status],
                           "feature": arg if status == "U" else None, "text": u["text"]})
            continue
        text = data[a:b]
        cuts = [a]
        for anchor, *_ in spec[1][1:]:
            at = text.find(anchor.encode(), cuts[-1] - a + 1)
            if at < 0:
                raise SystemExit(f"{u['id']}: anchor {anchor!r} not found")
            cuts.append(a + at)
        cuts.append(b)
        parts = []
        for i, ((_, kind, status, *rest), lo, hi) in enumerate(zip(spec[1], cuts, cuts[1:])):
            arg = rest[0] if rest else None
            pid = f"{u['id']}.p{i + 1}"
            parts.append({"id": pid, "span": [lo, hi], "status": STATUS[status], **_w2(kind, status, arg, env)})
            ledger.append({"id": pid, "parent": u["id"], "span": [lo, hi], "bytes": hi - lo, "kind": kind,
                           "status": STATUS[status], "feature": arg if status == "U" else None,
                           "text": data[lo:hi].decode("utf-8")})
        doc_units.append({"id": u["id"], "span": [a, b], "status": "MIXED", "parts": parts})
    return doc_units, ledger


def _content(doc_units):
    content = {}
    for du in doc_units:
        for p in du.get("parts", [du]):
            if "content" in p:
                content[p["id"]] = p["content"]["quantity"]
    return content


def build(labels, source_name: str, prefix: str, env, env_raw, mutate=None):
    path = EVIDENCE / labels.TARGET / source_name
    data = path.read_bytes()
    seg = segment_units(path, prefix)
    specs = {k: v for k, v in labels.LABELS.items() if k.startswith(prefix)}
    extra = sorted(set(specs) - {u["id"] for u in seg})
    if extra:
        raise SystemExit(f"{source_name}: labels for no unit {extra[:10]}")
    doc_units, ledger = _units(specs, seg, data, env, source_name)
    true_content = _content(doc_units)
    if mutate:
        doc_units, ledger = _units(mutate(copy.deepcopy(specs)), seg, data, env, source_name)
    meta = {"format": "ve-document@1", "environment": env_raw, "units": doc_units}
    graph = getattr(labels, "graph", None)
    if graph is not None:
        built = graph(true_content, prefix, env, prove_quantity, q)
        if built is not None:
            content = _content(doc_units)
            for node in built["nodes"]:
                if "unit" in node:
                    node["quantity"] = content[node["unit"]]
            meta["graph"] = built
    document = b"---\n" + json.dumps(meta, indent=1, ensure_ascii=False).encode() + b"\n---\n" + data
    return document, ledger


RAISED_RUST_TIMEOUT = "1800"


def run_ve(args: list[str], rust_timeout: str | None = None) -> tuple[int, str]:
    env = dict(os.environ)
    env.pop("VE_RUST_TIMEOUT", None)
    if rust_timeout:
        env["VE_RUST_TIMEOUT"] = rust_timeout
    proc = subprocess.run([*LIMIT, str(CHECKOUT / ".venv/bin/python"), "-m", "ve", *args], cwd=CHECKOUT,
                          capture_output=True, text=True, env=env)
    return proc.returncode, proc.stdout + proc.stderr


def check(path: Path, out: Path) -> tuple[int, str, str | None]:
    """`ve document check` at today's default limits; if the untrusted Rust accelerator's default wall-clock
    limit stops it, again with `VE_RUST_TIMEOUT` raised. Both answers are kept."""
    code, text = run_ve(["document", "check", str(path)])
    if "Rust checker failed" in text and "timed out" in text:
        out.with_suffix(".default-limit.json").write_text(text)
        code, text = run_ve(["document", "check", str(path)], RAISED_RUST_TIMEOUT)
        return code, text, RAISED_RUST_TIMEOUT
    return code, text, None


def environment(labels):
    raw = dict(BASE_ENV)
    raw["vocabulary"] = {"sorts": {}, "predicates": {}, "constants": {
        name: {"sort": "$int", "unit": tag, "description": desc, "verbalisation": verbal}
        for name, (tag, desc, verbal) in sorted(labels.CONSTANTS.items())}}
    if labels.UNITS:
        raw["unit_schema"] = "ve-units@1"
        raw["units"] = labels.UNITS
    return raw, Environment(raw)


def main() -> int:
    name = sys.argv[1]
    control = "--control" in sys.argv
    labels = importlib.import_module(f"labels.{name}")
    out = EVIDENCE / labels.TARGET
    env_raw, env = environment(labels)
    summary = {}
    for source_name, prefix in labels.SOURCES:
        stem = source_name.rsplit(".", 1)[0]
        if control:
            if not getattr(labels, "CONTROL", None) or labels.CONTROL[0] != source_name:
                continue
            document, _ = build(labels, source_name, prefix, env, env_raw, mutate=labels.CONTROL[1])
            target = out / f"{stem}.control.ve.md"
            target.write_bytes(document)
            code, text, raised = check(target, out / f"{stem}.control.check.txt")
            (out / f"{stem}.control.check.txt").write_text(f"exit {code}; VE_RUST_TIMEOUT={raised}\n{text}")
            print(f"control {source_name}: exit {code}; {text.strip().splitlines()[-1][:300]}")
            continue
        document, ledger = build(labels, source_name, prefix, env, env_raw)
        doc_path = out / f"{stem}.ve.md"
        doc_path.write_bytes(document)
        code, text, raised = check(doc_path, out / f"{stem}.check.json")
        (out / f"{stem}.check.json").write_text(text)
        ccode, ctext = run_ve(["document", "coverage", str(doc_path)])
        (out / f"{stem}.coverage.json").write_text(ctext)
        source = (out / source_name).read_bytes()
        (out / f"{stem}.units.json").write_text(json.dumps(
            {"source": source_name, "source_sha256": hashlib.sha256(source).hexdigest(),
             "source_bytes": len(source), "units": ledger}, indent=1, ensure_ascii=False) + "\n")
        try:
            checked = json.loads(text)
            admitted = checked.get("admission", {}).get("admitted")
            coverage = json.loads(ctext)
        except json.JSONDecodeError:
            checked, admitted, coverage = {}, None, None
        graph = json.loads(document.split(b"\n---\n", 1)[0][4:]).get("graph")
        summary[source_name] = {
            "document": doc_path.name, "document_bytes": len(document),
            "document_sha256": hashlib.sha256(document).hexdigest(),
            "check_exit": code, "accepted": code == 0 and not checked.get("error") and "format" in checked,
            "graph_admitted": admitted, "check_error": checked.get("error"),
            "premises": checked.get("premises"), "rust_timeout_raised_to": raised,
            "graph_nodes": len(graph["nodes"]) if graph else 0,
            "certified_consequences": [n["name"] for n in graph["nodes"] if "certificate" in n] if graph else [],
            "coverage_exit": ccode, "coverage": coverage}
        print(source_name, "check exit", code, "graph admitted", admitted, "VE_RUST_TIMEOUT", raised)
        print(json.dumps(coverage)[:600] if coverage else ctext[-2000:])
    if summary:
        (out / "run.json").write_text(json.dumps({"checkout": str(CHECKOUT), "checkout_head": subprocess.run(
            ["git", "-C", str(CHECKOUT), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip(),
            "product_tree_equals_main_406736a4": subprocess.run(
                ["git", "-C", str(CHECKOUT), "diff", "--quiet", "406736a4", "HEAD", "--", "lean", "rust", "ve"]
            ).returncode == 0,
            "sources": summary}, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
