"""Tour stop 9: a planted mistake in a translation, caught by a same-family AI reader. Runs from branch after-release
(the GitLab relocation translation) until it reaches main.

One mistake is planted in the translation of GitLab's relocation policy (usecases/gitlab_relocation/translation.py):
a stay's days are counted without its last day. `plant` makes that copy from the translation as written, the same
way every time (its comments are changed to match). Both copies the reader read have the list of test mistakes the
file carries removed (`without_list`), since that list would name this one. Then:

1. The reader's check. An AI model, given only the policy's text, a short brief and the translation's files, and not
   told that anything was planted, compared the translation with the policy and flagged where they differ. It ran five
   times on the planted copy and five times on the translation as written, with one prompt
   (tour/data/reader-prompt.txt, the translation as written; the planted copy's prompt is the same with the PLANT
   edits made). Its flags and their scores are recorded in tour/data/reader-runs.json; this stop checks that both
   copies it makes now are the files in those prompts, then counts the runs that raised the day-count problem and
   named the planted rule. Running the reader again needs an AI model account, so the stop shows the recording.
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
PLANT = (
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
)
# The file's own list of test mistakes, removed from both copies: from CUT's first line up to the next function, and
# the one line that uses the list
CUT = ("# --- planted errors (run.py --mutants)", "def tg_item(tg):")
LIST_USE = ("    t = dict(UNITS)\n    if mutant is not None:\n        t = MUTANTS[mutant][1](t)\n    return t",
            "    t = dict(UNITS)\n    if mutant is not None:\n        raise KeyError(mutant)\n    return t")
# What the parts named by the reader's day-count flags say, for the line on the parts it blamed besides the planted one
PARTS = {"U8": "the last allowed day of a planned stay"}
NUMBERS = ("none", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten")


def edited(text: str, edits) -> str:
    for old, new in edits:
        assert text.count(old) == 1, old[:60]
        text = text.replace(old, new)
    return text


def without_list(source: str) -> str:
    source = edited(source, (LIST_USE,))
    start, end = source.index(CUT[0]), source.index(CUT[1])
    return source[:start] + source[end:]


def plant(source: str) -> str:
    return edited(without_list(source), PLANT)


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def counts(record) -> dict:
    """The recorded runs, counted: per copy, the runs, the runs that raised the day-count problem, and (planted copy)
    the runs whose day-count flags include the planted rule, at any and at high confidence."""
    out = {}
    for copy in ("planted", "as written"):
        runs = [r for r in record["runs"] if r["copy"] == copy]
        right = [r["flags"][r["right_rule_flag"]] for r in runs if r["right_rule_flag"] is not None]
        assert all(f["unit"] == record["planted_unit"] for f in right)
        out[copy] = {"runs": len(runs), "day_count": sum(bool(r["day_count_flags"]) for r in runs),
                     "right_rule": len(right), "right_rule_high": sum(f["confidence"] == "high" for f in right)}
    return out


def sentence(c) -> str:
    """The stop's one-sentence result, worked out from counts(record)."""
    planted, written = c["planted"], c["as written"]
    noticed = ("every time" if planted["day_count"] == planted["runs"] else
               f"in {NUMBERS[planted['day_count']]} of them")
    return (f"With the same prompt and no mistake list, in {NUMBERS[planted['runs']]} runs the reader noticed the "
            f"day-count problem {noticed} and named the right rule in {NUMBERS[planted['right_rule']]} "
            f"({NUMBERS[planted['right_rule_high']]} at high confidence); on the unaltered translation it raised the "
            f"day-count problem in {NUMBERS[written['day_count']]} of {NUMBERS[written['runs']]}.")


def run_rows(record) -> list:
    """One line per run number: what the planted run raised, and whether the run on the translation as written raised
    the day-count problem."""
    by = {(r["copy"], r["run"]): r for r in record["runs"]}
    rule = f"right rule (part {record['planted_unit'][1:]})"
    lines = [f"  {'run':<5}{'planted copy: day-count problem':<34}{rule:<22}"
             "translation as written: day-count problem"]
    for n in sorted({r["run"] for r in record["runs"]}):
        p, w = by[("planted", n)], by[("as written", n)]
        parts = sorted({int(p["flags"][i]["unit"][1:]) for i in p["day_count_flags"]})
        raised = (f"yes (part{'s' if len(parts) > 1 else ''} {', '.join(map(str, parts))})" if parts else "no")
        right = f"yes, {p['flags'][p['right_rule_flag']]['confidence']}" if p["right_rule_flag"] is not None else "no"
        lines.append(f"  {n:<5}{raised:<34}{right:<22}{'yes' if w['day_count_flags'] else 'no'}")
    return lines


def other_flags_line(record) -> str:
    """The reader's flags that are not about the day count, per copy, from the record."""
    other = {copy: sum(len(r["flags"]) - len(r["day_count_flags"]) for r in record["runs"] if r["copy"] == copy)
             for copy in ("planted", "as written")}
    runs = {copy: NUMBERS[sum(r["copy"] == copy for r in record["runs"])] for copy in other}
    return (f"  Its other flags, not about the day count: {other['planted']} in the {runs['planted']} planted runs and "
            f"{other['as written']} in the {runs['as written']} runs on the translation as written; a person still has "
            "to read them.")


def elsewhere_line(record) -> str:
    """The planted runs that raised the day-count problem only on parts other than the planted one, from the record."""
    only = {}
    for r in record["runs"]:
        parts = {r["flags"][i]["unit"] for i in r["day_count_flags"]}
        if r["copy"] == "planted" and parts and record["planted_unit"] not in parts:
            only[r["run"]] = parts
    if not only:
        return ""
    units = sorted({u for p in only.values() for u in p}, key=lambda u: int(u[1:]))
    named = " and ".join(map(str, sorted(only)))
    what = "; ".join(f"part {u[1:]} ({PARTS[u]})" if u in PARTS else f"part {u[1:]}" for u in units)
    return (f"  {what[0].upper()}{what[1:]} {'are' if len(units) > 1 else 'is'} right as written: "
            f"run{'s' if len(only) > 1 else ''} {named} raised the day-count problem only under "
            f"{'them' if len(units) > 1 else 'it'}.")


def main():
    sys.setrecursionlimit(200000)
    provenance = json.loads((TOUR / "data" / "relocation-R009-sealed-provenance.json").read_text(encoding="utf-8"))
    for line in provenance_lines(provenance, (TOUR / "data" / "relocation-R009-sealed.jsonl").read_bytes()):
        print(line)
    print()
    record = json.loads((TOUR / "data" / "reader-runs.json").read_text(encoding="utf-8"))
    prompt = (TOUR / "data" / "reader-prompt.txt").read_text(encoding="utf-8")
    source = (POLICY / "translation.py").read_text(encoding="utf-8")
    planted = plant(source)
    prompts = {"as written": prompt, "planted": edited(prompt, PLANT)}
    same = (without_list(source) in prompts["as written"] and planted in prompts["planted"]
            and all(r["prompt_sha256"] == sha256(prompts[r["copy"]]) for r in record["runs"]))
    print("The planted mistake: a stay's days are counted without its last day, so Ivo's 184 days in Spain count as 183.")
    print("The reader read exactly these two copies, in two prompts that differ only by the planted lines:",
          "yes (same SHA-256)" if same else "NO (the files differ)")
    print()
    c = counts(record)
    print(f"1. The reader's check: an AI model of the translators' own model family, run {c['planted']['runs']} times "
          f"on the planted copy and {c['as written']['runs']} times on the translation as written (recorded "
          f"{record['read_on']}; running it again needs an AI model account).")
    print("  " + sentence(c))
    for line in run_rows(record):
        print(line)
    if elsewhere_line(record):
        print(elsewhere_line(record))
    print(other_flags_line(record))
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
                f"UTC, by {written['model']}, an {written['maker']} model: {family}. It {written['how']}."),
        wrapped("Sealed:", f"{_day(record['sealed'])}, {_when(record['sealed']):%H:%M} UTC, as one set of "
                f"{sealed_set['answers']} answers to {sealed_set['cases']} cases (SHA-256 {sealed_set['sha256']}), "
                f"kept {sealed_set['kept']}. The two answers here are its rows {numbers}; each row's SHA-256 was taken "
                f"from the sealed set on {_day(sealed_set['rows_hashed'] + 'T00:00:00Z')} (the seal covers the whole "
                "set). Unchanged since: "
                + ("yes (each row's SHA-256 is the recorded one)." if same else "NO (a row differs from the record).")),
        wrapped("Translation frozen:", f"commit {_short(frozen['commit'])}, {_day(frozen['time'])}, "
                f"{_when(frozen['time']):%H:%M} UTC, before {frozen['before']}. {record['after_the_seal']}"),
        wrapped("Who could read them:", record["who_could_read"]),
        wrapped("In this repository:", f"since commit {_short(first['commit'])} ({_day(first['time'])}), as a copy of "
                f"the two rows. Commit IDs here are those of {record['commit_ids']}."),
    ]


if __name__ == "__main__":
    main()
