"""AP-7 blind calls and scoring (PRE-REGISTRATION.md); the call and record handling is jt-e1r's runner's, for Opus.

    python3 docs/act-phrases/ap-7/runner.py --run      # the calls, resumable; never repeats a saved call
    python3 docs/act-phrases/ap-7/runner.py --score    # every number, recomputed from raw/ and lean-readings.json

Seats A and B list each phrase's readings blind; after every listing call, each seat judges Lean's readings in
batches; seat M (the matcher) pairs A's and B's readings and matches each pair to Lean's. Each seat is its own
`claude -p` session from its own picker call. A failed call is recorded and scored as no reading listed.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw"
MODEL = "claude-opus-5-5"
PICKER = "/home/seyran/code/manage-agents/pick-claude-account.sh"
CALL_CAP, CW_CAP, RESERVE_CW, RAW_CAP = 160, 4_000_000, 25_000, 2_000_000
JUDGE_BATCH = 8
USAGE_KEYS = ("input_tokens", "output_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")
RULES = "Use only the text below; do not use tools or outside knowledge."
LIST_PROMPT = (
    "You are auditing how an English sentence can be read. Below are a SENTENCE and, inside it, one DEMAND: a modal "
    "word (shall, should, must, may, can, has the right to, or their negations) and the acts it applies to; BEARER "
    "names who or what the demand is on. List every reading of the DEMAND that a careful reader of this English could "
    "take. Readings differ when they require, forbid or permit different things: for example each joined act on its "
    "own, or only the acts done together, or any one of several ways at the bearer's choice; or a modifier or phrase "
    "applying to one of the joined acts, or to all of them. Count readings that differ only in wording as one. Do not "
    "list a reading this English does not support. " + RULES + " Answer only with the readings, one per line, "
    "numbered `1.`, `2.`, ..., each a plain-English sentence saying what is required, forbidden or permitted.")
JUDGE_PROMPT = (
    "You are auditing how English sentences can be read. For each PHRASE below you get a SENTENCE, the DEMAND inside "
    "it, what {0} (and any {1}) stands for, and numbered candidate readings L1, L2, ... For every candidate, decide "
    "whether it is a reading of the DEMAND that a careful reader of this English could take (YES) or not a reading of "
    "this English (NO). Judge each candidate on its own. " + RULES + " Answer with exactly one line per candidate "
    "and nothing else, in the form `<phrase id> L<n>: YES` or `<phrase id> L<n>: NO`.")
MATCH_PROMPT = (
    "You match readings by paraphrase. Below are a SENTENCE, the DEMAND inside it, and three numbered lists of "
    "readings of the DEMAND: A and B (from two auditors) and L (from a parser). Two readings match when they require, "
    "forbid or permit the same acts, each on its own or together in the same way, with every modifier applying to the "
    "same acts; wording does not matter. Pair the A and B readings that match, each A and each B reading in at most "
    "one pair. For each pair name the L reading that matches it, or NONE; each L reading in at most one pair. Then "
    "name every L reading in which a modifier applies to some of the joined items but not to an item between them (a "
    "skipped middle). " + RULES + " Answer with one line per pair, `PAIR A<i> B<j> L<k>` or `PAIR A<i> B<j> NONE`, "
    "then exactly one line `SKIPPED: NONE` or `SKIPPED: L<k>, L<m>, ...`, and nothing else.")


def phrases() -> list[dict]:
    """The sample in order, each with its source (a draw's from population.json) and Lean's readings."""
    texts = {u["id"]: u["text"] for u in json.loads((HERE / "population.json").read_text())}
    lean = {r["id"]: r for r in json.loads((HERE / "lean-readings.json").read_text())}
    return [p | {"source": p.get("source", texts.get(p["id"]))} |
            {k: lean[p["id"]].get(k) for k in ("status", "raw", "meanings")} |
            {"readings": lean[p["id"]].get("readings", [])}
            for p in json.loads((HERE / "sample.json").read_text())]


def head(p: dict) -> str:
    return f"SENTENCE: {p['source']}\nDEMAND: {p['focus']}\n"


def parties(p: dict) -> str:
    slots = "".join(f"; {{{k}}} stands for {v}" for k, v in sorted(p.get("slots", {}).items()))
    return f"{{0}} stands for {p['bearer']}{slots}.\n"


def numbered(tag: str, xs: list[str], empty: str) -> str:
    return "".join(f"{tag}{i}. {x}\n" for i, x in enumerate(xs, 1)) if xs else f"{tag}: ({empty})\n"


def batches(ps: list[dict]) -> list[list[dict]]:
    read = [p for p in ps if p["readings"]]
    return [read[i:i + JUDGE_BATCH] for i in range(0, len(read), JUDGE_BATCH)]


def keys(ps: list[dict]) -> list[str]:
    """Every call in order: both seats' listings, then both seats' judgements, then the matcher."""
    return ([f"list-{s}-{p['id']}" for p in ps for s in "AB"] +
            [f"judge-{s}-{n}" for n in range(1, len(batches(ps)) + 1) for s in "AB"] +
            [f"match-{p['id']}" for p in ps])


def prompt(key: str, ps: list[dict], records: dict) -> str:
    kind, rest = key.split("-", 1)
    if kind == "list":
        p = next(p for p in ps if p["id"] == rest[2:])
        return LIST_PROMPT + "\n\n" + head(p) + f"BEARER: {p['bearer']}\n"
    if kind == "judge":
        batch = batches(ps)[int(rest[2:]) - 1]
        return JUDGE_PROMPT + "".join(f"\n\nPHRASE {p['id']}\n" + head(p) + parties(p) +
                                      numbered("L", p["readings"], "") for p in batch)
    p = next(p for p in ps if p["id"] == rest)
    a, b = (listed(records.get(f"list-{s}-{p['id']}")) for s in "AB")
    return (MATCH_PROMPT + "\n\n" + head(p) + "In list L, " + parties(p) + numbered("A", a, "none listed") +
            numbered("B", b, "none listed") + numbered("L", p["readings"], "none: the parser lists no reading"))


def answer(record: dict | None) -> str | None:
    return None if record is None or record.get("error") else record["answer"]


def listed(record: dict | None) -> list[str]:
    """A seat's numbered readings; a failed or unnumbered answer lists none."""
    text = answer(record)
    found = re.findall(r"^(\d+)[.)]\s+(\S.*)$", text or "", re.M)
    return [t.strip() for _, t in found] if [int(n) for n, _ in found] == list(range(1, len(found) + 1)) else []


def judged(record: dict | None, batch: list[dict]) -> dict:
    """(phrase, n) -> YES; a failed answer, or one that misses, repeats or adds a candidate, says NO to every one."""
    want = {(p["id"], n) for p in batch for n in range(1, len(p["readings"]) + 1)}
    found = re.findall(r"^\s*(\S+)\s+L(\d+)\s*:\s*(YES|NO)\s*$", answer(record) or "", re.M | re.I)
    got = [((i, int(n)), v.upper() == "YES") for i, n, v in found]
    if len(got) != len(want) or set(dict(got)) != want:
        return {k: False for k in want}
    return dict(got)


def matched(record: dict | None, na: int, nb: int, nl: int) -> dict | None:
    """The pairs `(a, b, l or None)` and the skipped-middle readings, or None when the answer is failed or unbound."""
    text = answer(record)
    if text is None:
        return None
    pairs = [(int(a), int(b), int(lk) if lk else None)
             for a, b, lk in re.findall(r"^\s*PAIR A(\d+) B(\d+) (?:L(\d+)|NONE)\s*$", text, re.M)]
    skips = re.findall(r"^\s*SKIPPED:\s*(NONE|L\d+(?:\s*,\s*L\d+)*)\s*$", text, re.M)
    if len(skips) != 1 or len(pairs) != len(re.findall(r"^\s*PAIR\b", text, re.M)):
        return None
    skipped = [] if skips[0] == "NONE" else [int(x) for x in re.findall(r"L(\d+)", skips[0])]
    ls = [lk for _, _, lk in pairs if lk is not None]
    a, b = [x for x, _, _ in pairs], [y for _, y, _ in pairs]
    if (len(set(a)) < len(a) or len(set(b)) < len(b) or len(set(ls)) < len(ls) or len(set(skipped)) < len(skipped)
            or not all(1 <= x <= na for x in a) or not all(1 <= y <= nb for y in b)
            or not all(1 <= k <= nl for k in ls + skipped)):
        return None
    return {"pairs": pairs, "skipped": skipped}


def score(ps: list[dict], records: dict) -> dict:
    rows, rejected, lean_total = [], [], 0
    for p in ps:
        a, b = (listed(records.get(f"list-{s}-{p['id']}")) for s in "AB")
        nl = len(p["readings"])
        m = matched(records.get(f"match-{p['id']}"), len(a), len(b), nl)
        agreed = min(len(a), len(b)) if m is None else len(m["pairs"])
        hits = 0 if m is None else sum(lk is not None for _, _, lk in m["pairs"])
        rows.append({"id": p["id"], "status": p["status"], "lean": nl, "A": len(a), "B": len(b), "agreed": agreed,
                     "matched": hits, "matcher_failed": m is None, "skipped": [] if m is None else m["skipped"]})
        lean_total += nl
    for n, batch in enumerate(batches(ps), 1):
        a, b = (judged(records.get(f"judge-{s}-{n}"), batch) for s in "AB")
        rejected += sorted(f"{i} L{k}" for (i, k) in a if not a[(i, k)] and not b[(i, k)])
    agreed, hits = sum(r["agreed"] for r in rows), sum(r["matched"] for r in rows)
    skipped = [f"{r['id']} L{k}" for r in rows for k in r["skipped"]]
    recall = hits / agreed if agreed else 0.0
    return {"recall": [hits, agreed], "bar_recall": recall >= 0.9,
            "not_a_reading": [len(rejected), lean_total], "bar_not_a_reading": len(rejected) <= 0.1 * lean_total,
            "skipped_middle": skipped, "bar_skipped": not skipped,
            "with_reading": [sum(r["lean"] > 0 for r in rows), len(rows)],
            "parsed_no_meaning": [p["id"] for p in ps if p["status"] == "none" and p["raw"] and not p["meanings"]],
            "rejected": rejected, "calls": len(records), "cw": sum(r["charged_cw"] or 0 for r in records.values()),
            "failed": sorted(k for k, r in records.items() if r.get("error")), "phrases": rows}


def usage_cw(cli: object) -> int:
    usage = cli.get("usage") if isinstance(cli, dict) else None
    if not isinstance(usage, dict) or usage.get("fallback_credit", "missing") is not None:
        raise RuntimeError("missing usage or paid-credit fallback")
    if any(type(usage.get(k)) is not int or usage[k] < 0 for k in USAGE_KEYS):
        raise RuntimeError("malformed usage counters")
    return sum(usage[k] for k in USAGE_KEYS)


def save(path: Path, record: dict) -> None:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as out:
        json.dump(record, out, indent=1, ensure_ascii=False)
        out.write("\n")
    os.replace(out.name, path)


def records() -> dict:
    found = {p.stem: json.loads(p.read_text()) for p in RAW.glob("*.json")} if RAW.is_dir() else {}
    if any(r.get("state") == "dispatched" for r in found.values()):
        raise RuntimeError("a dispatched call has no saved result; inspect before continuing")
    return found


def call(key: str, body: str) -> dict:
    picked = subprocess.run(["zsh", PICKER], capture_output=True, text=True,
                            env=os.environ | {"PICK_NOWAIT": "1", "PICK_SHORT": "1"})
    cfg = picked.stdout.strip()
    if picked.returncode or not cfg.startswith("/home/seyran/.agent-accounts/claude-"):
        raise RuntimeError(f"account picker unavailable: {picked.stderr.strip()}")
    auth = json.loads((Path(cfg) / ".claude.json").read_text())
    if not auth.get("oauthAccount") or auth.get("primaryApiKey"):
        raise RuntimeError("picked account is not an OAuth subscription")
    save(RAW / f"{key}.json", {"key": key, "account": Path(cfg).name, "prompt": body, "state": "dispatched"})
    env = {k: v for k, v in os.environ.items() if not k.endswith("API_KEY")
           and k not in {"ANTHROPIC_BASE_URL", "OPENAI_BASE_URL"}} | {"CLAUDE_CONFIG_DIR": cfg}
    cmd = ["claude", "-p", "--model", MODEL, "--effort", "high", "--max-turns", "1", "--restricted",
           "--no-session-persistence", "--output-format", "json", body]
    try:
        done = subprocess.run(cmd, capture_output=True, text=True, cwd="/tmp", env=env, timeout=1800)
        out, err, code = done.stdout, done.stderr, done.returncode
    except (subprocess.TimeoutExpired, OSError) as exc:
        out, err, code = "", f"CLI did not complete: {type(exc).__name__}", -1
    try:
        cli = json.loads(out) if len(out.encode()) <= RAW_CAP else {}
    except ValueError:
        cli = {"raw_stdout": out[:4096]}
    cli = cli if isinstance(cli, dict) else {}
    models = cli.get("modelUsage")
    error = (err if code == -1 else f"CLI exit {code} or unsuccessful result"
             if code or cli.get("subtype") != "success" or cli.get("is_error") is not False
             else "CLI did not use Opus 5.5 alone" if not isinstance(models, dict) or not models
             or not all(m.startswith(MODEL) for m in models)
             else "CLI result is not text" if type(cli.get("result")) is not str else None)
    try:
        cw = usage_cw(cli)
    except RuntimeError as exc:
        error, cw = error or str(exc), None
    charged = max(RESERVE_CW, cw or 0) if error else cw
    return {"key": key, "account": Path(cfg).name, "prompt": body, "cli": cli, "stderr": err[-4096:], "exit_code": code,
            "charged_cw": charged, "answer": "" if error else cli["result"], **({"error": error} if error else {})}


def run() -> None:
    for name in ("PRE-REGISTRATION.md", "sample.json", "draw.json", "lean-readings.json", "runner.py"):
        saved = subprocess.run(["git", "show", f"HEAD:docs/act-phrases/ap-7/{name}"], capture_output=True).stdout
        if saved != (HERE / name).read_bytes():
            raise RuntimeError(f"commit {name} before any call")
    RAW.mkdir(exist_ok=True)
    ps, saved = phrases(), records()
    order = keys(ps)
    if set(saved) - set(order):
        raise RuntimeError("an extra raw record")
    for key, record in saved.items():
        if record["prompt"] != prompt(key, ps, saved):
            raise RuntimeError(f"rebound raw record: {key}")
    failures = 0
    for key in order:
        if key in saved:
            continue
        charged = sum(r["charged_cw"] for r in saved.values())
        if len(saved) >= CALL_CAP or charged + RESERVE_CW > CW_CAP:
            raise RuntimeError(f"cap reached before {key}: {len(saved)} calls, {charged} CW")
        saved[key] = call(key, prompt(key, ps, saved))
        save(RAW / f"{key}.json", saved[key])
        failures = failures + 1 if saved[key].get("error") else 0
        print(f"{key}: {saved[key].get('error', 'ok')}; {len(saved)} calls", flush=True)
        if failures >= 3:
            raise RuntimeError("three failed calls in a row; inspect (a rerun goes on with the next call)")


if __name__ == "__main__":
    if sys.argv[1:] == ["--run"]:
        run()
    elif sys.argv[1:] == ["--score"]:
        print(json.dumps(score(phrases(), records()), indent=1))
    else:
        raise SystemExit("usage: runner.py --run|--score")
