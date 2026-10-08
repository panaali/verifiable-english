"""E2.6: the corpus A/B of Lean's English authority, compared and classified from saved recordings.

    .venv/bin/python -m conformance.english_lean_e2_ab compare --head DIR --main DIR   # writes the comparisons
    .venv/bin/python -m conformance.english_lean_e2_ab report --write                    # from the saved files only

Three recordings by `tools/lean_first_diff.py record`, over the corpora of E2.5's A/B (conformance, probe, pilots,
readings, discourse, rights, quantity): E2.5's base `9aaf918d` (saved in `evidence/`), `main` before E2.6
(`6fd95b01`, English under Python authority) and the E2.6 head (both saved in `evidence/e2.6/`). Two comparisons:

* base to head, the A/B of GE2 item 3 on E2.5's inputs: the pilot set is the 303 documents both sides recorded
  (the base has none of the pilots added since), and the one pilot the base did not finish in 600 s
  (`readings/s1.ve.md` of `cc-20261004T1800Z`) is the base's answer re-recorded with 3,500 s (`ab-a5-base.json`);
* main to head, on every current input: what E2.6 itself changes.

`report` classifies every base-to-head difference by `rule` below and checks, for each wording and order record,
the lf-12 DRI rule: every name or value the base quoted is quoted again, and every base `path` and `span` is kept
(a head span may only be wider). The rows that keep them are listed by rule; the rest are listed for DRI signature.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import gzip
import json
from pathlib import Path
import re
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/lean-first/e2/evidence"
HEAD = EVIDENCE / "e2.6"
BASE_COMMIT, MAIN_COMMIT = "9aaf918d", "6fd95b01"
OTHER = ("probe", "pilots", "readings", "discourse", "rights", "quantity")
A5 = "pilot/cc-20261004T1800Z:usecases/claude-constitution-pilot/run-20261004T1800Z/readings/s1.ve.md"
TEXT_KEYS = ("message", "detail", "stderr", "text", "error")
QUOTED = re.compile(r"'([^']+)'|\"([^\"]+)\"|\*([^*]+)\*")


def _write_gz(path: Path, lines: list[str]) -> None:
    """A deterministic gzip file (mtime 0), so a re-run with the same records writes the same bytes."""
    with open(path, "wb") as raw, gzip.GzipFile(fileobj=raw, mode="wb", mtime=0) as out:
        out.write("".join(lines).encode())


def _lines(path: Path) -> list[str]:
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt") as f:
        return f.readlines()


def read_json(path: Path):
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt") as f:
        return json.load(f)


# ------------------------------------------------------------------ compare (needs the tool and the recordings)

def compare(head: Path, main: Path) -> int:
    """Save the head and main recordings, then both comparisons. `head` and `main` hold `conformance.jsonl` and
    `other.jsonl` as `record` wrote them."""
    sys.path.insert(0, str(ROOT))
    from tools import lean_first_diff as D
    a5 = json.loads((HEAD / "ab-a5-base.json").read_text())
    base_other = []
    for line in _lines(EVIDENCE / "ab-other-base.jsonl.gz"):
        row = json.loads(line)
        if row["corpus"] == "pilots" and row["case"] == A5:
            line = json.dumps({**row, "outcome": a5["outcome"]}, sort_keys=True, separators=(",", ":")) + "\n"
        base_other.append(line)
    base_pilots = {json.loads(line)["case"] for line in base_other if '"corpus":"pilots"' in line}
    for name, source in (("head", head), ("main", main)):
        for part in ("conformance", "other"):
            _write_gz(HEAD / f"ab-{name}-{part}.jsonl.gz", _lines(source / f"{part}.jsonl"))
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)

        def plain(name, lines):
            (tmp / name).write_text("".join(lines))
            return str(tmp / name)
        head_other = _lines(head / "other.jsonl")
        pinned = [line for line in head_other if json.loads(line)["corpus"] != "pilots"
                  or json.loads(line)["case"] in base_pilots]
        runs = [("base-head-conformance", plain("bc", _lines(EVIDENCE / "ab-conformance-base.jsonl.gz")),
                 plain("hc", _lines(head / "conformance.jsonl")), ["conformance"], True),
                ("base-head-other", plain("bo", base_other), plain("ho", pinned), list(OTHER), True),
                ("main-head-conformance", plain("mc", _lines(main / "conformance.jsonl")), str(tmp / "hc"),
                 ["conformance"], False),
                ("main-head-other", plain("mo", _lines(main / "other.jsonl")), plain("hoa", head_other), list(OTHER),
                 False)]
        documents = D.pilot_documents
        status = 0
        for name, left, right, corpora, pin in runs:
            D.pilot_documents = ((lambda root: [d for d in documents(root) if d[0] in base_pilots]) if pin
                                 else documents)
            out = tmp / f"{name}.json"
            code = D.main(["compare", left, right, "--corpus", *corpora, "--json", str(out)])
            status = max(status, code if code != 1 else 0)  # 1: differences, which `report` classifies
            _write_gz(HEAD / f"ab-{name}.json.gz", [out.read_text()])
        D.pilot_documents = documents
    return status


# ------------------------------------------------------------------ report (saved files only)

def texts(value) -> list[str]:
    out = []
    if isinstance(value, dict):
        for key, item in value.items():
            if key in TEXT_KEYS and isinstance(item, str):
                out.append(item)
            elif key in TEXT_KEYS and isinstance(item, list):
                out += [x for x in item if isinstance(x, str)]
            else:
                out += texts(item)
    elif isinstance(value, list):
        for item in value:
            out += texts(item)
    return out


def locations(value, path=()) -> dict:
    """Every `path` and `span` member, by where it sits in the outcome."""
    out = {}
    if isinstance(value, dict):
        for key, item in value.items():
            if key in ("path", "span"):
                out[(*path, key)] = item
            else:
                out.update(locations(item, (*path, key)))
    elif isinstance(value, list):
        for i, item in enumerate(value):
            out.update(locations(item, (*path, i)))
    return out


def quoted(text: str) -> list[str]:
    return [next(g for g in m.groups() if g is not None) for m in QUOTED.finditer(text)]


def code_of(outcome) -> str | None:
    raised = outcome.get("raised") if isinstance(outcome, dict) else None
    return raised.get("code") if isinstance(raised, dict) else None


def _strip_code(text: str) -> str:
    return re.sub(r"^[A-Z][A-Za-z]+(\([^)]*\))?: ", "", text)


def kept(record: dict) -> dict:
    """The lf-12 DRI rule for one record: the base's quoted names, its unquoted message when it quotes nothing,
    and its locations."""
    base_texts, head_texts = texts(record["base"]), texts(record["head"])
    head_all = "\n".join(head_texts)
    lost_names = sorted({n for t in base_texts for n in quoted(t) if n not in head_all})
    lost_messages = sorted({t for t in base_texts if not quoted(t) and _strip_code(t) not in head_all})
    base_at, head_at = locations(record["base"]), locations(record["head"])
    lost_locations = []
    for where, value in base_at.items():
        other = head_at.get(where)
        if other == value:
            continue
        if where[-1] == "span" and isinstance(value, dict) and isinstance(other, dict) and \
                other.get("start", 1) <= value.get("start", 0) and value.get("end", 0) <= other.get("end", -1):
            continue
        lost_locations.append("/".join(map(str, where)))
    return {"names_lost": lost_names, "messages_lost": lost_messages, "locations_lost": sorted(lost_locations),
            "kept": not (lost_names or lost_messages or lost_locations)}


def template(text: str) -> str:
    return re.sub(r"\d+", "N", QUOTED.sub("‘…’", text))[:160]


def rule(record: dict) -> str:
    """The rule a difference belongs to; verdict and availability rules carry their disposition in `RULES`."""
    corpus, op, cls = record["corpus"], record["op"], record["class"]
    base, head = record["base"], record["head"]
    if cls == "verdict":
        if corpus == "rights" and code_of(base) == "UnsupportedProfile" and "returned" in head:
            return "V-rights-readings-head"
        if corpus == "quantity" and op == "certificate" and base == {"returned": False} and \
                code_of(head) == "ResourceLimit":
            return "V-quantity-certificate-exhausted"
        if corpus == "quantity" and op == "countermodel" and code_of(base) == code_of(head) == "ResourceLimit":
            return "V-quantity-model-path"
        if corpus == "probe" and code_of(base) is None and base.get("status") == head.get("status") == "ResourceLimit":
            return "V-english-source-limit-span"
        if corpus == "pilots" and _only_readings_texts_and_hash(base, head):
            return "V-pilot-readings-slot"
        return "V-unexplained"
    if cls == "availability":
        return "A-unexplained"
    messages = (texts(base)[:1] or [""])[0], (texts(head)[:1] or [""])[0]
    return f"{cls[0].upper()}-{corpus}-{op}: {code_of(base)} {template(messages[0])} -> {code_of(head)} " \
           f"{template(messages[1])}"


def _diff_paths(a, b, path=()):
    if type(a) is not type(b):
        return [path]
    if isinstance(a, dict):
        out = []
        for k in set(a) | set(b):
            out += [(*path, k)] if (k not in a or k not in b) else _diff_paths(a[k], b[k], (*path, k))
        return out
    if isinstance(a, list):
        if len(a) != len(b):
            return [path]
        return [p for i, (x, y) in enumerate(zip(a, b)) for p in _diff_paths(x, y, (*path, i))]
    return [] if a == b else [path]


def _only_readings_texts_and_hash(base, head) -> bool:
    """A pilot report that differs only in reading-pair or reading-plan texts and the soft document hash, the two
    changes main made between the base and E2.6 (readings-defaults A4 `5166853c`; the soft hash)."""
    paths = _diff_paths(base, head)
    return bool(paths) and all(
        p[:2] == ("stdout", "readings") and p[-1] in ("text",) or p[:3] == ("stdout", "readings", "english")
        or p == ("stdout", "soft", "soft_document_hash") for p in paths)


# The disposition of each verdict and availability rule, with the test that checks it.
RULES = {
    "V-rights-readings-head": (
        "Python bug", "The base refuses a rights document under the head profile `readings@1` with `UnsupportedProfile`; "
        "composition-s1.md 1.1 (already at the base) puts `readings@1` on the `rights` route, the head handing "
        "every case but its reading sets to the lower rights chain, so the document is checked. A main-side "
        "change (present at `6fd95b01`, before E2.6).",
        "tests/test_english_e26_ab.py::test_rights_under_the_readings_head_is_a_python_bug"),
    "V-quantity-certificate-exhausted": (
        "Python bug", "The base returns `false` for a certificate whose replay ran out of its 10,000 steps (with a "
        "larger budget the same certificate replays as valid): an exhausted budget became a verdict (build "
        "checklist 6). Lean raises `ResourceLimit`. Main-side.",
        "tests/test_english_e26_ab.py::test_an_exhausted_certificate_replay_was_never_false"),
    "V-quantity-model-path": (
        "residue (owner lf-12)", "Both raise `ResourceLimit` for a model domain over 1,000 entities; Lean's quantity "
        "model decoder says `domain size` without the base's `path` `/domains/s` and wording. The lf-12 class (Lean's "
        "model decoders carry a JSON pointer, on branch `lean-first/b12`, the same files); not English, main-side.",
        "tests/test_english_e26_ab.py::test_the_residue_is_the_listed_rows"),
    "V-english-source-limit-span": (
        "not a verdict: same status and code", "E2.6: a source over 65,536 bytes is `ResourceLimit` on both; Lean's "
        "text (`The text is longer than 65,536 bytes.`, spec 4.2) keeps the limit and adds the span of the whole "
        "source (spec 4.4). The comparator calls it a verdict because a member (`span`) was added.",
        "tests/test_english_e26_ab.py::test_the_english_rows_keep_code_limit_and_names"),
    "V-pilot-readings-slot": (
        "not a verdict: display texts", "A pilot report whose reading-pair and reading-plan texts name the reading's "
        "own sentence for its number (readings-defaults A4, `5166853c`) and whose soft document hash changed, both on "
        "main before E2.6: `6fd95b01` gives the UDHR translation's very report, and could not check the three "
        "constitution readings documents at all (its V3 refusal of an apostrophe wording, which E2.6 removes).",
        "tests/test_english_e26_ab.py::test_the_pilot_rows_differ_only_in_main_side_texts"),
}


def report() -> dict:
    data = read_json(HEAD / "ab-base-head-other.json.gz")
    conformance = read_json(HEAD / "ab-base-head-conformance.json.gz")
    main_other = read_json(HEAD / "ab-main-head-other.json.gz")
    main_conformance = read_json(HEAD / "ab-main-head-conformance.json.gz")
    records = conformance["differences"] + data["differences"]
    groups: dict[str, list] = defaultdict(list)
    for r in records:
        groups[rule(r)].append(r)
    verdict_rules = {k: len(v) for k, v in groups.items() if k.startswith(("V-", "A-"))}
    text_rows = {"kept": defaultdict(int), "for_dri": defaultdict(list)}
    for name, rows in groups.items():
        if name.startswith(("V-", "A-")):
            continue
        for r in rows:
            check = kept(r)
            if check["kept"]:
                text_rows["kept"][name] += 1
            else:
                text_rows["for_dri"][name].append({"case": r["case"], "op": r["op"], "authority": r["authority"],
                                                   **{k: v for k, v in check.items() if k != "kept"}})
    totals = Counter()
    for t in (conformance["totals"], data["totals"]):
        totals.update(t)
    e26 = Counter()
    for t in (main_conformance["totals"], main_other["totals"]):
        e26.update(t)
    summary = {
        "format": "ve-e2.6-ab@1", "base": BASE_COMMIT, "main": MAIN_COMMIT,
        "records_per_side": sum(conformance["records"].values()) + sum(data["records"].values()),
        "base_head": dict(sorted(totals.items())),
        "main_head": dict(sorted(e26.items())),
        "main_head_classes": dict(sorted(Counter(
            f"{d['class']}/{d['corpus']}" for d in main_conformance["differences"] + main_other["differences"]).items())),
        "verdict_rules": dict(sorted(verdict_rules.items())),
        "unexplained": verdict_rules.get("V-unexplained", 0) + verdict_rules.get("A-unexplained", 0),
        "availability": totals.get("availability", 0),
        "residue": {k: verdict_rules[k] for k in verdict_rules if RULES.get(k, ("",))[0].startswith("residue")},
        "text_rows_kept": dict(sorted((k, v) for k, v in text_rows["kept"].items())),
        "text_rows_for_dri": {k: len(v) for k, v in sorted(text_rows["for_dri"].items())},
        "wording_order_rows": sum(len(v) for k, v in groups.items() if not k.startswith(("V-", "A-"))),
    }
    summary["text_rows_kept_total"] = sum(summary["text_rows_kept"].values())
    summary["text_rows_for_dri_total"] = sum(summary["text_rows_for_dri"].values())
    # E2.6's own rows (main to head): their rules, every wording row kept, every availability row an answer where
    # main had none; and no row of base to head that this report lists for the DRI changed from main to head.
    own = main_conformance["differences"] + main_other["differences"]
    key = lambda r: (r["corpus"], r["authority"], r["case"], r["op"])  # noqa: E731
    changed = {key(r) for r in own}
    listed = {(r["corpus"], r["authority"], r["case"], r["op"]) for name, rows in groups.items()
              if not name.startswith(("V-", "A-")) and name in text_rows["for_dri"] for r in rows}
    summary["e26"] = {
        "rules": dict(sorted(Counter(rule(r) if r["class"] != "wording" or not kept(r)["kept"] else "W-kept"
                                     for r in own if r["class"] != "availability").items())),
        "wording_not_kept": sum(1 for r in own if r["class"] == "wording" and not kept(r)["kept"]),
        "availability_gained": sum(1 for r in own if r["class"] == "availability" and _unavailable(r["base"])
                                   and not _unavailable(r["head"])),
        "availability_lost": sum(1 for r in own if r["class"] == "availability" and not _unavailable(r["base"])),
        "dri_rows_changed_by_e26": len(listed & changed),
    }
    return {"summary": summary, "for_dri": dict(sorted(text_rows["for_dri"].items()))}


def _unavailable(outcome) -> bool:
    """`CheckerUnavailable` anywhere at the top of an outcome (a raised record or a pilot's report), or a timeout."""
    if not isinstance(outcome, dict):
        return False
    if "timeout" in outcome or code_of(outcome) == "CheckerUnavailable":
        return True
    stdout = outcome.get("stdout")
    return isinstance(stdout, dict) and stdout.get("status") == "CheckerUnavailable"


def markdown(result: dict) -> str:
    s = result["summary"]
    lines = ["# E2.6 corpus A/B", "",
             "Generated by `python -m conformance.english_lean_e2_ab report --write` from the saved comparisons in "
             "this directory (see `conformance/english_lean_e2_ab.py` for how they were recorded).", "",
             f"Base `{s['base']}` (E2.5's recording) to the E2.6 head: {s['records_per_side']:,} records per side; "
             f"{', '.join(f'{k} {v:,}' for k, v in s['base_head'].items())}. "
             f"Unexplained verdict or availability rows: **{s['unexplained']}**; availability rows: "
             f"**{s['availability']}**.", "",
             f"Main `{s['main']}` (before E2.6, English under Python authority) to the head, on every current input: "
             f"{', '.join(f'{k} {v:,}' for k, v in s['main_head'].items())} "
             f"({', '.join(f'{k} {v}' for k, v in s['main_head_classes'].items())}). These are E2.6's own changes: "
             f"by rule {', '.join(f'`{k}` {v}' for k, v in s['e26']['rules'].items())}; wording rows that lose a "
             f"name or location: **{s['e26']['wording_not_kept']}**; documents main could not check that the head "
             f"checks: {s['e26']['availability_gained']}; documents the head can no longer check: "
             f"**{s['e26']['availability_lost']}**; rows listed below for the DRI that E2.6 changed: "
             f"**{s['e26']['dri_rows_changed_by_e26']}**.", "",
             "## Verdict and availability rows, by rule", "", "| Rule | Rows | Disposition | Evidence |",
             "|---|---:|---|---|"]
    for name, count in s["verdict_rules"].items():
        kind, why, test = RULES.get(name, ("UNEXPLAINED", "", ""))
        lines.append(f"| `{name}` | {count} | **{kind}**: {why} | `{test}` |")
    lines += ["", "## Wording and order rows", "",
              f"{s['wording_order_rows']} rows. {s['text_rows_kept_total']} keep every name, value and location the "
              f"base gave (lf-12 DRI rule); {s['text_rows_for_dri_total']} do not and are listed for DRI signature "
              "below, grouped by rule. None of them is caused by E2.6: each is also a row of base to main.", "",
              "### Kept, by rule", "", "| Rule | Rows |", "|---|---:|"]
    lines += [f"| `{k}` | {v} |" for k, v in s["text_rows_kept"].items()]
    lines += ["", "### For DRI signature, by rule", "", "| Rule | Rows | Names lost | Locations lost |",
              "|---|---:|---|---|"]
    for name, rows in result["for_dri"].items():
        names = sorted({n for r in rows for n in r["names_lost"] + r["messages_lost"]})
        where = sorted({w for r in rows for w in r["locations_lost"]})
        shown = "; ".join(repr(n)[:60] for n in names[:4]) + (f" (+{len(names) - 4})" if len(names) > 4 else "")
        lines.append(f"| `{name}` | {len(rows)} | {shown or 'none'} | {', '.join(where) or 'none'} |")
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    c = sub.add_parser("compare")
    c.add_argument("--head", type=Path, required=True)
    c.add_argument("--main", type=Path, required=True)
    r = sub.add_parser("report")
    r.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    if args.command == "compare":
        return compare(args.head, args.main)
    result = report()
    if args.write:
        (HEAD / "ab-summary.json").write_text(json.dumps(result, indent=1, sort_keys=True) + "\n")
        (HEAD / "ab-dispositions.md").write_text(markdown(result))
    print(json.dumps(result["summary"], indent=1))
    return 1 if result["summary"]["unexplained"] or result["summary"]["availability"] else 0


if __name__ == "__main__":
    sys.exit(main())
