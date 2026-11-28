"""Tour stop 9: a planted mistake in a translation, caught by a same-family AI reader. Runs from branch after-release
(the GitLab relocation translation) until it reaches main.

One mistake is planted in the translation of GitLab's relocation policy (usecases/gitlab_relocation/translation.py):
a stay's days are counted without its last day. `plant` makes that copy from the translation as written, the same
way every time (its comments are changed to match, and the list of test mistakes the file carries is removed, since it
would name this one). Then:

1. The reader's check. An AI model, given only the policy's text, a short brief and the translation's files, and not
   told that anything was planted, compared the translation with the policy and flagged where they differ. Its flags
   are recorded in tour/data/reader-planted.json, with the SHA-256 of the file it read; this stop checks that the copy
   it makes now is that same file, then shows the flag on the planted part with the policy's words and the
   translation's side by side. Running the reader again needs an AI model account, so the stop shows the recording.
2. The answers. The case's two questions are answered by the translation as written and by the planted copy, and
   compared with the answers a separate writer gave from the policy alone before the translation ran
   (tour/data/relocation-R009-sealed.jsonl). Lean reads the rules and facts, but is not asked to check the proofs here.

Before both, the stop prints where those answers come from (tour/data/relocation-R009-sealed-provenance.json: when and
by which model they were written and sealed, the translation's freeze, who could read them) and checks that the two
rows are the recorded rows of the sealed set.

Run from the after-release checkout: python tour/stops/planted.py (tour/stops/09-planted-mistake.sh does this).
"""
from datetime import datetime
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import textwrap

TOUR = Path(__file__).resolve().parents[1]
CASE = "R009"
POLICY = Path("usecases") / "gitlab_relocation"
# The planted mistake, as edits of the translation as written: (old text, new text), each found exactly once
EDITS = (
    ("R1  Days (D9; the brief's counting convention): a stay's days = elapsed days from its first to its last day + 1 "
     "(both days\n    count); the days outside the primary location in the year = the sum over every stay of the year; "
     "the year's days =",
     "R1  Days (D9; the brief's counting convention): a stay's days = elapsed days from its first to its last day; the "
     "days\n    outside the primary location in the year = the sum over every stay of the year; the year's days ="),
    ("181/185 by D4, one year by the bridge) or the counting convention's +1.", "181/185 by D4, one year by the bridge)."),
    ('"sn": (NDAYS, "the stay\'s days (both the first and the last day counted)"),', '"sn": (NDAYS, "the stay\'s days"),'),
    ("def _days(ctx, plus=1):", "def _days(ctx):"),
    ('out.append((Eq(k("sn", s), add(NDAYS, k("sg", s), nd(plus))), f"sn_{s}"))',
     'out.append((Eq(k("sn", s), k("sg", s)), f"sn_{s}"))'),
    ("    t = dict(UNITS)\n    if mutant is not None:\n        t = MUTANTS[mutant][1](t)\n    return t",
     "    t = dict(UNITS)\n    if mutant is not None:\n        raise KeyError(mutant)\n    return t"),
)
# The file's own list of test mistakes, removed from the copy: from this line up to the next function
CUT = ("# --- planted errors (run.py --mutants)", "def tg_item(tg):")


def plant(source: str) -> str:
    for old, new in EDITS:
        assert source.count(old) == 1, old[:60]
        source = source.replace(old, new)
    start, end = source.index(CUT[0]), source.index(CUT[1])
    return source[:start] + source[end:]


def answers(directory: Path) -> dict:
    """The case's answers from the translation in DIRECTORY (its runner, cases and translation)."""
    for name in ("cases", "run", "translation", "encode", "bridge"):
        sys.modules.pop(name, None)
    sys.path.insert(0, str(directory))
    try:
        import cases
        import run
        case = next(c for c in cases.CASES if c["id"] == CASE)
        out = {}
        for sub in case["subs"]:
            out.update(run.run_sub(sub, None)[0])
        return {qid: a["answer"] for qid, a in sorted(out.items())}
    finally:
        sys.path.remove(str(directory))


def wrapped(label: str, text: str) -> str:
    return textwrap.fill(text, width=116, initial_indent=f"  {label:<22}", subsequent_indent=" " * 24)


def other_flags_line(record, as_written):
    """The reader's other flags on the planted copy, from the record, and whether it raised the same flag (same part,
    kind and confidence) on the translation as written (tour/data/reader-as-written.json)."""
    hit = [f for f in record["flags"] if f["unit"] == record["planted_unit"] and f["confidence"] == "high"]
    others = [f for f in record["flags"] if f not in hit]
    before = {(f["unit"], f["kind"], f["confidence"]) for f in as_written["flags"]}
    parts = ", ".join(f"part {f['unit'][1:]} ({f['confidence']})" for f in others)
    same = sum((f["unit"], f["kind"], f["confidence"]) in before for f in others)
    return (f"  It raised {len(others)} other flags: {parts}. It raised {same} of them (same part, kind and confidence) "
            "on the translation as written too.")


def _when(stamp: str) -> datetime:
    return datetime.strptime(stamp, "%Y-%m-%dT%H:%M:%SZ")


def _day(stamp: str) -> str:
    return f"{_when(stamp).day} {_when(stamp):%b %Y}"


def _short(commit: str) -> str:
    return commit[:10]


def provenance_lines(record: dict, rows: bytes) -> list:
    """Stop 9's header: where the answers written from the policy alone come from (RECORD, the file
    tour/data/relocation-R009-sealed-provenance.json), and whether ROWS (the bytes of
    tour/data/relocation-R009-sealed.jsonl) are exactly the recorded rows of the sealed set."""
    written, sealed_set, frozen = record["written"], record["set"], record["translation_frozen"]
    got = [(json.loads(line)["qid"], hashlib.sha256(line).hexdigest()) for line in rows.splitlines(keepends=True)
           if line.strip()]
    same = got == [(row["qid"], row["sha256"]) for row in sealed_set["rows"]]
    # "a different model family" only when the writer's maker is not the translators' maker
    family = (f"a different model family from the translators' ({written['translators']})"
              if written["maker"] != written["translators_maker"] else
              f"the translators' own model family ({written['translators']})")
    numbers = " and ".join(str(row["row"]) for row in sealed_set["rows"])
    first = record["first_commit_here"]
    return [
        "Where the answers written from the policy alone come from (tour/data/relocation-R009-sealed-provenance.json):",
        wrapped("Written:", f"{_day(written['from'])}, {_when(written['from']):%H:%M}-{_when(written['to']):%H:%M} "
                f"UTC, by {written['model']}, an {written['maker']} model: {family}. It read "
                f"{written['read']}."),
        wrapped("Sealed:", f"{_day(record['sealed'])}, {_when(record['sealed']):%H:%M} UTC, as one set of "
                f"{sealed_set['answers']} answers to {sealed_set['cases']} cases (SHA-256 {sealed_set['sha256']}), "
                f"kept {sealed_set['kept']}. The two answers here are its rows {numbers}, unchanged: "
                + ("yes (each row's SHA-256 is the recorded one)." if same else "NO (a row differs from the record).")),
        wrapped("Translation frozen:", f"commit {_short(frozen['commit'])}, {_day(frozen['time'])}, "
                f"{_when(frozen['time']):%H:%M} UTC, before {frozen['before']}. {record['after_the_seal']}"),
        wrapped("Who could read them:", record["who_could_read"]),
        wrapped("In this repository:", f"since commit {_short(first['commit'])} ({_day(first['time'])}), as a copy of "
                "the two rows."),
    ]


def main():
    sys.setrecursionlimit(200000)
    provenance = json.loads((TOUR / "data" / "relocation-R009-sealed-provenance.json").read_text(encoding="utf-8"))
    for line in provenance_lines(provenance, (TOUR / "data" / "relocation-R009-sealed.jsonl").read_bytes()):
        print(line)
    print()
    record = json.loads((TOUR / "data" / "reader-planted.json").read_text(encoding="utf-8"))
    planted = plant((POLICY / "translation.py").read_text(encoding="utf-8"))
    same = hashlib.sha256(planted.encode("utf-8")).hexdigest() == record["translation_sha256"]
    print("The planted mistake: a stay's days are counted without its last day, so Ivo's 184 days in Spain count as 183.")
    print("The reader read exactly this planted file:", "yes (same SHA-256)" if same else "NO (the file differs)")
    print()
    print(f"1. The reader's check: an AI model of the translators' own model family (recorded {record['read_on']}; "
          "running it again needs an AI model account).")
    hit = [f for f in record["flags"] if f["unit"] == record["planted_unit"] and f["confidence"] == "high"]
    for flag in hit:
        print(f"  It flags part {flag['unit'][1:]} of the policy (the 183-day rule), with {flag['confidence']} "
              "confidence:")
        print(wrapped("The policy says:", flag["source"]))
        print(wrapped("The translation says:", flag["translation"]))
        print(wrapped("Why it matters:", flag["why"]))
    print(other_flags_line(record, json.loads((TOUR / "data" / "reader-as-written.json").read_text(encoding="utf-8"))))
    print()
    print("2. The answers, compared with answers written from the policy alone before the translation ran:")
    questions = {q["qid"]: q["text"] for line in open(POLICY / "questions-enc.jsonl", encoding="utf-8")
                 if line.strip() and json.loads(line)["id"] == CASE for q in json.loads(line)["questions"]}
    sealed = {a["qid"]: a["answer"] for a in map(json.loads, open(TOUR / "data" / "relocation-R009-sealed.jsonl"))}
    as_written = answers(POLICY.resolve())
    with tempfile.TemporaryDirectory() as tmp:
        copy = Path(tmp) / "gitlab_relocation"
        shutil.copytree(POLICY, copy, ignore=shutil.ignore_patterns("__pycache__"))
        (copy / "translation.py").write_text(planted, encoding="utf-8")
        with_mistake = answers(copy)
    for qid in sorted(questions):
        caught = "caught" if with_mistake[qid] != sealed[qid] else "NOT caught"
        print(f"  {questions[qid]}")
        print(f"    policy alone: {sealed[qid]}; translation as written: {as_written[qid]}; "
              f"with the mistake: {with_mistake[qid]} ({caught})")


if __name__ == "__main__":
    main()
