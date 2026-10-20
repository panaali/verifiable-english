#!/usr/bin/env python3
"""speed-trustmut: the sentences of this batch's documents that `CLAIM` reads as saying a budget is met, a probe or
test passes, a run used the final tool or a count holds, the step-1 table, and the sentences `named()` lists, each
against the saved evidence (review F14 and its later forms F15, F16: the DRI's notes 2026-10-20 and 2026-10-20b).
A number in a form `CLAIM` does not read, outside the table and `named()`, is not checked.

    uv run python docs/speed/trustmut/claims.py [--report FILE]

`CLAIM` finds its words in REPORT.md and hunt/README.md. Each must lie inside a text `bound()` writes from the
saved evidence (the replays and their profiles, the sweep, the seeded bugs, the probes, the selected tests, and the
evidence an earlier round saved, as git keeps it) or from this checkout (`sweep.py`'s and `F14.sh`'s exit codes, the
test file's collected tests), or inside one of `NOT_CLAIMS`, the words with the reason they report no result. It
prints one line per sentence that has one, OK or UNBOUND with the words no evidence gives. `tabled()` compares the
step-1 table cell by cell with `replay.table()`, and `bindings()` each sentence of `named()` with the numbers its
evidence gives (a line per row and per sentence). It exits 1 when any line is UNBOUND. --report checks FILE in place
of REPORT.md (`hunt/F14c.sh`: an earlier round's report). A number `CLAIM` reads that the evidence does not give is
UNBOUND, since `bound()` writes each number from the evidence. Batch
evidence is checked at the gate and merge, never by a permanent test (D4): this is run by hand and by `hunt/F14c.sh`.
"""
from __future__ import annotations

from collections import Counter
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import re
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path[:0] = [str(HERE), str(HERE / "hunt"), str(ROOT / "tools")]
import nested_pytest  # noqa: E402
import replay  # noqa: E402
import run as probes  # noqa: E402
import sweep  # noqa: E402

DOCS = [HERE / "REPORT.md", HERE / "hunt/README.md"]
# a count: a number or a range, then up to three words ("of each replay's", "former", "of the"), then what it counts
# (review F15: "21–35 of each replay's mutants" put three words between them and was never checked)
# (not a number inside a name: ap-2, F14, TM82, Lean 4.24, section 4, step 1)
COUNT = r"(?<![\w.,–-])(?<![Ss]ection )(?<![Ss]tep )\d[\d,]*(?:–\d[\d,]*)?"
COUNTED = ("s|h|tests?|units|functions|mutants|seeds|seeded bugs|survivors|kills|definitions|files|probes|lines|"
           "replays|findings|rows|KILLED|SURVIVOR|UNKNOWN|INVALID")
CLAIM = re.compile("|".join([
    r"\bwithin (?:the |step 1's |its )?(?:20-minute |time )?budget\b", r"\bwithin it\b", r"\bmeets? the budget\b",
    r"\bbudget (?:is|was) met\b",
    r"\b(?:PROBE|[Pp]robes?|tests?|units|file)\b[^.;]{0,80}?\bpass(?:es|ed)?\b", r"\bpass(?:es|ed)? (?:on|at|there|after)\b",
    r"\bexits? 0\b", r"\bexit 0\b",
    r"\b(?:on|with) the final tool\b",
    r"\bload \d",
    COUNT + r" of (?:the )?\d[\d,]*\b",
    COUNT + rf" (?:[\w'’-]+ ){{0,3}}?(?:{COUNTED})\b",
    COUNT + r" each\b", r"\b(?:all|every one of) (?:the )?\d", r"\babout \d[\d,]*",
]))
# (words, why they report no result)
NOT_CLAIMS = [
    ("until it exits 0", "an instruction to a builder (section 2), not a result"),
    ("(default 1,800 s, the suite's hang bound)", "the tool's default limit, a constant"),
    ("(1,800 s by default)", "the tool's default limit, a constant"),
    ("the nested run's 1,800 s limit", "`tools/mutants.py`'s limit, a constant"),
    ("among the first 60 mutants of the tool's order", "defines a column of the table"),
    ("Exit 3 means mutants were NOT RUN", "the tool's exit codes"),
    ("| 3 tests in a new", "the task line's own words"),
    ("| 4 orchestrator lines", "the task line's own words"),
    ("25 seeded bugs still killed", "the task line quotes the DRI note's ask"),
    ("at most ~500 changed lines", "the task's size rule"),
    ("an outside `--test` file kills only when it passes without the mutant", "a rule of the tool (TM22)"),
    ("(the probe), and the control pass elaborates", "describes the tool's control pass"),
    ("that PROBE F14 then passed", "describes the first F14 fix's overclaim"),
    ("(a budget met, a probe or test that passes, a run on the final tool, a count)", "names the class"),
    ("left out): a sentence that says a probe passes quotes that file", "states the rule"),
    ("a range expanded, exits 0 in `evidence/probes.json`", "a seeded bug's rule (TM83)"),
    ("counts only the probes that exit 0", "a seeded bug's rule (TM85)"),
    ("sampled every 15 s", "`profiled`'s sampling interval, a constant"),
    ('"on the final tool" for the sweep and the seeded bugs', "quotes an overclaim the check found"),
]
WORDS = dict(enumerate("zero one two three four five six seven eight nine ten eleven twelve".split()))
# what the size rule counts: every changed file but the generated one and the saved evidence (REPORT section 5)
SIZE_OUT = re.compile(r"tests/history-dependent\.json|docs/speed/trustmut/(?:evidence/.*\.json|mutants-evidence\.json|"
                      r"hunt/.*\.sh)")


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout


def saved(name: str, commit: str | None = None) -> dict:
    """A replay's evidence (`evidence/<name>.json`), as this checkout has it or as `commit` saved it."""
    path = f"docs/speed/trustmut/evidence/{name}.json"
    return json.loads(git("show", f"{commit}:{path}") if commit else (ROOT / path).read_text())


def num(x: int) -> str:
    return f"{x:,}"


def span(xs: list[int]) -> str:
    return f"{min(xs)}–{max(xs)}" if min(xs) != max(xs) else str(xs[0])


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


TOOL = sha((ROOT / "tools/trust_mutants.py").read_bytes())


def tool_commit(digest: str) -> str | None:
    """The newest commit whose `tools/trust_mutants.py` has this sha256."""
    for commit in git("log", "--format=%h", "--", "tools/trust_mutants.py").split():
        if sha(git("show", f"{commit}:tools/trust_mutants.py").encode()) == digest:
            return commit
    return None


def replays() -> list[tuple[str, str]]:
    texts = [(row, "replay.py table()") for row in replay.table()]
    texts.append((f"each replay within {num(replay.BUDGET)} s or over it", "replay.py BUDGET"))
    texts.append((f"the {num(replay.BUDGET)} s budget", "replay.py BUDGET"))
    texts += [(f"> {replay.budget()}", "replay.py budget()"), (f"> {replay.profile()}", "replay.py profile()")]
    texts += [(replay.f9().split(": ", 1)[1].rstrip("."), "replay.py f9()"),
              (replay.f10().split(": ", 1)[1].rstrip("."), "replay.py f10()")]
    rows = [cells(row) for row in replay.table()[2:]]
    flagged, first = sum(c[5] == "yes" for c in rows), sum(c[6] == "yes" for c in rows)
    texts += [(f"the tool flags {'all ' if flagged == len(rows) else ''}{flagged} of the {len(rows)} findings",
               "replay.py table()"), (f"At the default `--max-mutants 60` it flags {first}", "replay.py table()"),
              (f"{flagged} of {len(rows)} flagged", "replay.py table()")]
    data = {head[:8]: saved(head[:8]) for _, head, _, _ in replay.FINDINGS}
    ap2 = {len(data[head[:8]]["mutants"]) for finding, head, _, _ in replay.FINDINGS if finding.startswith("ap-2")}
    if len(ap2) == 1:
        texts.append((f"ap-2 has {ap2.pop()} mutants", "evidence/*.json"))
    final = [(f, h) for f, h, _, _ in replay.FINDINGS if data[h[:8]].get("profile", {}).get("tool_sha256") == TOOL]
    for finding, head in final:
        texts.append((f"{finding} (`{head[:9]}`) with the final tool", f"evidence/{head[:8]}.json profile"))
        texts.append((f"{finding} took {num(data[head[:8]]['seconds'])} s with the final tool",
                      f"evidence/{head[:8]}.json profile"))
    texts.append((f"only {' and '.join(f for f, _ in final)} ran on the final tool", "evidence/*.json profile"))
    for finding, head in final:
        d = data[head[:8]]
        t, jobs = d["profile"]["thread_seconds"], d["jobs"]
        probe, build = round(t["probe"] / jobs, -1), round(t["lake build"] / jobs, -1)
        texts += [(f"the threads spent {num(t['probe'])} s in it against {num(t['lake build'])} s in builds, so at "
                   f"{jobs} jobs it is about {num(int(probe))} s of the {num(d['seconds'])}, and the builds alone about "
                   f"{num(int(build))} s", f"evidence/{head[:8]}.json profile"),
                  (f"about {num(int(probe))} s of it", f"evidence/{head[:8]}.json profile"),
                  (f"({d['counts']['KILLED']} kills here)", f"evidence/{head[:8]}.json")]
    others = len(replay.FINDINGS) - len(final)
    texts.append((f"The other {WORDS[others]} replays were not rerun on the final tool", "evidence/*.json profile"))
    qt = data["b20a8e30"]["counts"]
    if not qt["KILLED"]:
        texts.append((f"qt-a1: {qt['SURVIVOR']} survivors, no kill", "evidence/b20a8e30.json"))
    invalid = [d["counts"]["INVALID"] for d in data.values()]
    texts.append((f"{span(invalid)} of each replay's mutants are INVALID", "evidence/*.json"))
    texts += f11(data["aa2fd56e"])
    # the rounds before, as git keeps their evidence: F1 (bd74c0fac), F7 (167deb649), F8 (15fed9b89)
    def times(commit: str) -> tuple[int, str, int, int]:
        got = {f: saved(h[:8], commit)["seconds"] for f, h, _, _ in replay.FINDINGS}
        return got["qt-a1 F1"], span([s for f, s in got.items() if f.startswith("ap-2")]), got["pk-1 F1"], \
            got["ap-2 F11"]
    q, a, p, last = times("15fed9b89")
    texts.append((f"qt-a1 took {q} s, the four ap-2 HEADs {a} s (ap-2 F11 {last} s), and pk-1 {p} s",
                  "evidence at 15fed9b89 (F8)"))
    texts.append((f"{last} s with the F8 tool", "evidence at 15fed9b89 (F8)"))
    for commit, round_ in (("167deb649", "F7"), ("bd74c0fac", "F1")):
        q, a, p, _ = times(commit)
        texts.append((f"{q} s, {a} s and {p} s", f"evidence at {commit} ({round_})"))
    texts.append((f"{sum(former_kills().values())} former kills are no longer kills",
                  "evidence at 51714c923 and bd74c0fac (F1)"))
    texts.append((f"ap-2 F11 took {num(saved('aa2fd56e-f11round')['seconds'])} s",
                  "evidence/aa2fd56e-f11round.json"))
    return texts


def former_kills() -> Counter:
    """Review F1's former kills, the evidence at 51714c923 against bd74c0fac's: (finding, the file the kill was at, the
    verdict now) and how many."""
    got = Counter()
    for finding, head, _, _ in replay.FINDINGS:
        now = {m["id"]: m["status"] for m in saved(head[:8], "bd74c0fac")["mutants"]}
        for m in saved(head[:8], "51714c923")["mutants"]:
            if m["status"] == "KILLED" and now[m["id"]] != "KILLED":
                got[finding, m["detail"].split(":")[0].split("/")[-1], now[m["id"]]] += 1
    return got


def f11(now: dict) -> list[tuple[str, str]]:
    """ap-2 F11 on the final tool against the F8 tool's run (15fed9b89) and the F11 round's (aa2fd56e-f11round)."""
    def ids(d: dict, status: str) -> set[str]:
        return {m["id"] for m in d["mutants"] if m["status"] == status}
    before, f11round = saved("aa2fd56e", "15fed9b89"), saved("aa2fd56e-f11round")
    texts = []
    if all(ids(now, s) == ids(before, s) for s in ("KILLED", "SURVIVOR")) and \
            ids(now, "UNKNOWN") <= ids(before, "INVALID") and ids(now, "INVALID") <= ids(before, "INVALID"):
        k, s, u, i = (len(ids(now, x)) for x in ("KILLED", "SURVIVOR", "UNKNOWN", "INVALID"))
        texts += [(f"all {k} kills and {s} survivors are the same mutants as before; {u} former INVALID are now UNKNOWN",
                   "evidence/aa2fd56e.json against 15fed9b89's"),
                  (f"the same {k} kills and {s} survivors; {u} INVALID now UNKNOWN",
                   "evidence/aa2fd56e.json against 15fed9b89's"),
                  (f"{u} of ap-2 F11's {len(ids(before, 'INVALID'))} are now UNKNOWN",
                   "evidence/aa2fd56e.json against 15fed9b89's")]
    def rows(d: dict) -> list:
        return [(m["id"], m["status"], m["detail"]) for m in d["mutants"]]
    if rows(now) == rows(f11round):
        texts.append((f"every one of the {len(rows(now))} mutants has the verdict and detail of the F11 round's run",
                      "evidence/aa2fd56e.json against aa2fd56e-f11round.json"))
    return texts


def sweeps() -> list[tuple[str, str]]:
    data = sweep.load()
    by_def, kills, unknown, survivors = sweep.survivors_of(data)
    c, texts = data["counts"], []
    texts.append((f"{num(len(data['mutants']))} mutants, {num(data['seconds'])} s at {data['jobs']} jobs",
                  "evidence/sweep.json"))
    texts.append((f"{num(c['KILLED'])} KILLED, {num(c['SURVIVOR'])} SURVIVOR, {num(c['UNKNOWN'])} UNKNOWN, "
                  f"{num(c['INVALID'])} INVALID", "evidence/sweep.json"))
    with contextlib.redirect_stdout(io.StringIO()):
        if sweep.report() == 0:
            texts.append(("`sweep.py` exits 0", "sweep.py on evidence/sweep.json"))
    each = {sum(m["status"] == "SURVIVOR" for m in by_def[d]) for d in kills | unknown}
    if len(each) == 1:
        texts.append((f"keep {each.pop()} survivors each ({len(kills)} + {len(unknown - kills)} such definitions)",
                      "evidence/sweep.json"))
    killed = {sum(m["status"] == "KILLED" for row in data["rows"] if row["form"] == form and row["expected"] == "KILLED"
                  for m in by_def[f"{sweep.SPACE[row['setting']]}.{row['d']}"])
              for form in {row["form"] for row in data["rows"] if row["expected"] == "KILLED"}}
    if len(killed) == 1:
        texts.append((f"({killed.pop()} each)", "evidence/sweep.json"))
    if commit := tool_commit(data["sources"]["tools/trust_mutants.py"]):
        texts.append((f"the tool of `{commit}`" + (" (the final tool)" if commit == tool_commit(TOOL) else ""),
                      "evidence/sweep.json sources"))
        if commit != tool_commit(TOOL):
            texts.append(("The sweep was not rerun on the final tool", "evidence/sweep.json sources"))
    per = {len(v) for v in by_def.values()}
    if len(per) == 1:
        texts.append((f"({per.pop()} mutants each)", "evidence/sweep.json"))
    lines = data["lines"]
    lc = lines["counts"]
    if not lc["NOT RUN"]:
        texts.append((f"{len(lines['rows'])} definitions, {len(lines['mutants'])} mutants, every one run: "
                      f"{lc['KILLED']} KILLED, {lc['SURVIVOR']} SURVIVOR, {lc['UNKNOWN']} UNKNOWN, "
                      f"{lc['INVALID']} INVALID", "evidence/sweep.json lines"))
    def statuses(row: dict) -> str:
        got = Counter(m["status"] for m in lines["mutants"] if m["definition"] == f"{row['space']}.{row['d']}")
        return ", ".join(f"{got[s]} {s}" for s in ("KILLED", "SURVIVOR", "UNKNOWN", "INVALID") if got[s])
    shapes: dict[str, dict[bool, set[str]]] = {}
    for row in lines["rows"]:
        shapes.setdefault(row["shape"], {}).setdefault(bool(row["reads"]), set()).add(statuses(row))
    for shape, by in shapes.items():
        if all(len(v) == 1 for v in by.values()):
            texts.append((f"| {next(iter(by[True]))} | {next(iter(by[False]))} |", f"evidence/sweep.json lines {shape}"))
    compared = [(row["shape"], m) for row in lines["rows"] if row["reads"] for m in lines["mutants"]
                if m["definition"] == f"{row['space']}.{row['d']}" and m["status"] == "SURVIVOR"]
    if {shape for shape, _ in compared} == {"arm-bool"}:
        texts.append((f"The {len(compared)} survivors of the compared rows are all `arm-bool`'s",
                      "evidence/sweep.json lines"))
    # the rounds before: F9 (70c8e39b0), F10 (3ca6bd87b)
    f9, f10 = (sweep.load(git("show", f"{c}:docs/speed/trustmut/evidence/sweep.json")) for c in ("70c8e39b0", "3ca6bd87b"))
    texts.append((f"All {num(len(f9['mutants']))} mutants ran ({num(f9['seconds'])} s at {f9['jobs']} jobs",
                  "evidence/sweep.json at 70c8e39b0 (F9)"))
    texts.append((f"in {num(f10['seconds'])} s", "evidence/sweep.json at 3ca6bd87b (F10)"))
    c = f10["counts"]
    texts.append((f"{num(c['KILLED'])} KILLED, {num(c['SURVIVOR'])} SURVIVOR, {num(c['UNKNOWN'])} UNKNOWN, "
                  f"{num(c['INVALID'])} INVALID", "evidence/sweep.json at 3ca6bd87b (F10)"))
    by_def, _, unknown, _ = sweep.survivors_of(f10)
    each = {sum(m["status"] == "UNKNOWN" for m in by_def[d]) for d in unknown}
    if len(each) == 1:
        texts.append((f"({each.pop()} each)", "evidence/sweep.json at 3ca6bd87b (F10)"))
    return texts


def seeds() -> list[tuple[str, str]]:
    data = json.loads((HERE / "mutants-evidence.json").read_text())
    rows = data["mutants"]
    killed = sum(m["killed"] is True for m in rows)
    texts = []
    if killed == data["killed"] and len(rows) == data["total"]:
        texts.append((f"kills {killed} of {len(rows)}", "mutants-evidence.json"))
        texts.append((f"(the `tools/mutants.py` format), {len(rows)} of them", "mutants-evidence.json"))
        top = max(int(m["id"][2:]) for m in rows)
        texts.append((f"seeded bugs TM1–TM{top}, {len(rows)}", "mutants-evidence.json"))
        part = [m for m in rows if 41 <= int(m["id"][2:]) <= 79]
        texts.append((f"TM41–TM79 ({len(part)} seeds)", "mutants-evidence.json"))
    if "the test file passes there" in data["runs"]:
        texts.append(("since the whole test file passes there", "mutants-evidence.json runs"))
    for commit in ("46159c58b", "bd7cc3a73"):  # F9, F10
        old = json.loads(git("show", f"{commit}:docs/speed/trustmut/mutants-evidence.json"))["mutants"]
        texts.append((f"({sum(m['killed'] is True for m in old)} of {len(old)})", f"mutants-evidence.json at {commit}"))
    return texts


LISTED = re.compile(r"PROBEs? ((?:[A-Z]\d+[a-z]?|–[A-Z]?\d+|, | and )+) exits? 0 on the final tool")


def names(listed: str) -> list[str]:
    """`F1, F6–F9 and N4` -> F1, F6, F7, F8, F9, N4."""
    out = []
    for part in re.split(r", | and ", listed):
        if m := re.fullmatch(r"([A-Z])(\d+)–[A-Z]?(\d+)", part):
            out += [f"{m[1]}{i}" for i in range(int(m[2]), int(m[3]) + 1)]
        else:
            out.append(part)
    return out


def hunted() -> list[tuple[str, str]]:
    """The hunt table's failing probes (REPORT section 1e), counted per hunt, each one a saved probe."""
    rows = re.findall(r"^\| (\d) \| ([^|]+) \|", DOCS[0].read_text(), re.M)
    counts = [len([n for n in re.sub(r"\(.*?\)", "", cell).split(",") if n.strip()]) for _, cell in rows]
    every = {n.strip() for _, cell in rows for n in re.sub(r"\(.*?\)", "", cell).split(",") if n.strip()}
    if rows and all((HERE / "hunt" / f"{n}.sh").is_file() for n in every):
        return [(f"{', '.join(map(str, counts))} failing probes", "REPORT section 1e's hunt table, hunt/*.sh")]
    return []


def size() -> list[tuple[str, str]]:
    base = git("merge-base", "HEAD", "main").strip()
    rows = [line.split("\t") for line in git("diff", "--numstat", base, "HEAD").splitlines()]
    total = sum(int(a) + int(b) for a, b, f in rows if not SIZE_OUT.fullmatch(f))
    return [*((f"about {near:,} changed lines", "git diff --numstat against the merge base")  # the hundred either side
              for near in {total // 100 * 100, -(-total // 100) * 100}),
            (f"That is over {WORDS[total // 500]} times the guideline", "git diff --numstat against the merge base"),
            *parts()]


# the review rounds' tables in the test file, each a run of lines from one top-level name to another (REPORT section 5)
PARTS = [("the F7 truth table and its package", [("FORMS", "ARMS")]),
         ("F9's line axis", [("ARMS", "GUARD"), ("LINES", "NO_ANSWERS")]),
         ("F10's budget table", [("NO_ANSWERS", "STUCK")])]


def parts() -> list[tuple[str, str]]:
    lines = (ROOT / "tests/test_trust_mutants.py").read_text().splitlines()
    at = {re.match(r"\w+", line)[0]: n for n, line in enumerate(lines) if re.match(r"[A-Z_]+ = ", line)}
    (first, size), *rest = [(what, round(sum(at[end] - at[start] for start, end in runs), -1)) for what, runs in PARTS]
    text = f"{first} are about {size} of the test's lines" + "".join(f", {what} about {n}" for what, n in rest)
    return [(text, "tests/test_trust_mutants.py, measured now")]


def hunt() -> list[tuple[str, str]]:
    data = json.loads(probes.SAVED.read_text()) if probes.SAVED.is_file() else {"sources": {}, "probes": {}}
    texts = [(probes.summary(data), "evidence/probes.json")] if data["probes"] else []
    current = data["sources"] == probes.shas()
    for name, p in data["probes"].items():
        if current and p["exit"] == 0:
            texts += [(f"PROBE {name} exits 0", "evidence/probes.json"), (f"`{p['last']}`", f"evidence/probes.json {name}")]
    if current:
        texts.append(("The probes ran on the final tool", "evidence/probes.json"))
        for doc in DOCS:
            for m in LISTED.finditer(" ".join(doc.read_text().split())):
                if all(data["probes"].get(n, {}).get("exit") == 0 for n in names(m[1])):
                    texts.append((m[0], "evidence/probes.json"))
    done = subprocess.run(["bash", str(HERE / "hunt/F14.sh")], cwd=ROOT, capture_output=True, text=True)
    texts.append((f"`hunt/F14.sh` exits {done.returncode}", "F14.sh rerun now"))
    return texts


def tests() -> list[tuple[str, str]]:
    done = subprocess.run(nested_pytest.command(["--collect-only", "-q", "-p", "no:cacheprovider",
                                                 "tests/test_trust_mutants.py"]),
                          cwd=ROOT, env=nested_pytest.environment(os.environ), capture_output=True, text=True)
    texts = [(f"{sum('::' in line for line in done.stdout.splitlines())} tests at this checkout",
              "the test file's ids, collected now")]
    path = HERE / "evidence/selected.json"
    if path.is_file():
        run = json.loads(path.read_text())
        texts.append((f"on `{run['commit'][:9]}`: {run['units']} units, exit {run['exit']}", "evidence/selected.json"))
        texts.append((f"`lake build` exits {run['lake_build_exit']} and `python3 lean/audit.py` exits "
                      f"{run['audit_exit']} there", "evidence/selected.json"))
        texts.append((f"`tools/gate_collection.py --check`: {run['gate_collection']}", "evidence/selected.json"))
    return texts


def bound() -> list[tuple[str, str]]:
    return [(" ".join(t.split()), source) for t, source in [*replays(), *sweeps(), *seeds(), *hunt(), *hunted(),
                                                                 *size(), *tests()]]


def named() -> list[tuple[str, tuple[int, ...] | None, str]]:
    """Numbers `CLAIM` does not read, each sentence bound by name (review F16; the DRI's note 2026-10-20b: one entry
    per sentence, no general rule): (the sentence's words, `{}` for each number; the numbers the evidence gives, or
    None when it gives no such sentence; the evidence). Each must be in the report with these numbers."""
    gone = former_kills()
    pk1 = saved("6b58a0ff")["mutants"]
    seeded = json.loads((HERE / "mutants-evidence.json").read_text())
    rows = seeded["mutants"]
    every = all(m["killed"] is True for m in rows) and seeded["killed"] == seeded["total"] == len(rows)
    collected = "`tools/gate_collection.py --check`: {} added, {} removed by a trailer, {} refused, {} stale and {} " \
                "malformed trailers"
    run = json.loads((HERE / "evidence/selected.json").read_text())
    said = re.fullmatch(pattern(collected), f"`tools/gate_collection.py --check`: {run['gate_collection']}")
    return [
        ("pk-1 {} at `PacksLegacy.lean` now SURVIVOR and {} at `LayeredAdmission.lean` now UNKNOWN (with those proofs "
         "cut, a proof term inside the `def` at `Readings/UnspecifiedWire.lean:526` fails; it cannot be cut, so the "
         "tool fails closed); qt-a1 {} at `Cardinality/Theorems.lean` and {} at the tactic-proved `example`s of "
         "`Cardinality/Examples.lean`",
         (gone["pk-1 F1", "PacksLegacy.lean", "SURVIVOR"], gone["pk-1 F1", "LayeredAdmission.lean", "UNKNOWN"],
          sum(n for (f, file, _), n in gone.items() if (f, file) == ("qt-a1 F1", "Theorems.lean")),
          sum(n for (f, file, _), n in gone.items() if (f, file) == ("qt-a1 F1", "Examples.lean"))),
         "evidence at 51714c923 and bd74c0fac (F1)"),
        ("(pk-1: {}, at `Readings/UnspecifiedWire.lean:526`)",
         (sum(m["status"] == "UNKNOWN" and m["detail"].startswith("lean/VE/Readings/UnspecifiedWire.lean:526:")
              for m in pk1),), "evidence/6b58a0ff.json"),
        ("seeded bugs TM{}–TM{}, {} (`mutants.json`, `mutants-evidence.json`), each failing its named test or command",
         (1, max(int(m["id"][2:]) for m in rows), len(rows)) if every else None, "mutants-evidence.json"),
        (collected, tuple(int(n) for n in said.groups()) if said else None, "evidence/selected.json"),
    ]


def pattern(words: str) -> str:
    return r"(\d[\d,]*)".join(map(re.escape, words.split("{}")))


def cells(row: str) -> list[str]:
    """A table row's cells, every column."""
    return [c.strip() for c in row.strip().strip("|").split("|")]


def tabled(doc: Path) -> list[str]:
    """The step-1 table (REPORT section 1) cell by cell against `replay.table()`, which writes it from the saved
    replays (review F16): one line per row, UNBOUND with the cells that differ, or when a row is missing or extra."""
    want = [cells(row) for row in replay.table()]
    lines = doc.read_text().splitlines()
    head = [n for n, line in enumerate(lines) if " ".join(line.split()) == " ".join(replay.table()[0].split())]
    where = doc.relative_to(HERE) if doc.is_relative_to(HERE) else doc
    if len(head) != 1:
        return [f"{where}:0 UNBOUND ['the step-1 table']: {len(head)} tables with its header"]
    rows = []
    for n in range(head[0], len(lines)):
        if not lines[n].lstrip().startswith("|"):
            break
        rows.append((n + 1, cells(lines[n])))
    out = []
    for i in range(max(len(rows), len(want))):
        line, got = rows[i] if i < len(rows) else (head[0] + 1 + i, None)
        given = want[i] if i < len(want) else None
        diff = [] if got == given else ["the row is extra" if given is None else "the row is missing" if got is None
                                        else f"{want[0][j]}: {a!r}, the evidence {b!r}"
                                        for j, (a, b) in enumerate(zip(got, given)) if a != b] or ["its cells"]
        status = f"UNBOUND {diff}" if diff else "OK (replay.py table())"
        out.append(f"{where}:{line} {status}: {' | '.join(got or given)[:120]}")
    return out


def bindings(doc: Path) -> list[str]:
    """Each of `named()`'s sentences in `doc` with the numbers the evidence gives: one line per sentence, UNBOUND when
    a number differs or the sentence is not there."""
    where = doc.relative_to(HERE) if doc.is_relative_to(HERE) else doc
    paras = list(paragraphs(doc.read_text()))
    out = []
    for words, numbers, source in named():
        found = [(line, m) for line, para in paras for m in re.finditer(pattern(words), para)]
        for line, m in found:
            got = tuple(int(n.replace(",", "")) for n in m.groups())
            status = f"OK (named: {source})" if got == numbers else \
                f"UNBOUND {list(m.groups())}: the evidence gives {numbers or 'no such sentence'} ({source})"
            out.append(f"{where}:{line} {status}: {m[0][:120]}")
        if not found:
            out.append(f"{where}:0 UNBOUND ['a named sentence']: not in the report: {words[:100]}")
    return out


def verdict(texts: list[tuple[str, str]]) -> list[str]:
    """What `claims.py` checks: the sentences `CLAIM` reads, the step-1 table and the named sentences."""
    return check(texts) + tabled(DOCS[0]) + bindings(DOCS[0])


def paragraphs(text: str):
    """(line, paragraph) for each paragraph, table row and list item of `text`, its whitespace normalized."""
    start, part = 1, []
    for n, line in enumerate(text.split("\n") + [""], 1):
        if not line.strip() or line.lstrip().startswith(("|", "- ", "> ")) or re.match(r"\s*\d+\. ", line):
            if part:
                yield start, " ".join(" ".join(part).split())
            start, part = n, ([line] if line.strip() else [])
            if line.lstrip().startswith("|"):
                yield start, " ".join(line.split())
                start, part = n + 1, []
        else:
            part.append(line)


def check(texts: list[tuple[str, str]]) -> list[str]:
    out = []
    for doc in DOCS:
        for line, para in paragraphs(doc.read_text()):
            covered = []  # (start, end, source)
            for t, source in [*texts, *NOT_CLAIMS]:
                for m in re.finditer(re.escape(" ".join(t.split())), para):
                    covered.append((m.start(), m.end(), source))
            at = 0
            for sentence in re.split(r"(?<=[.;])\s+(?=[A-Z`(*>\d])", para):
                begin = para.index(sentence, at)
                at = begin + len(sentence)
                found = [m for m in CLAIM.finditer(para, begin, at)]
                if not found:
                    continue
                loose = [m.group() for m in found if not any(s <= m.start() and m.end() <= e for s, e, _ in covered)]
                sources = sorted({src for s, e, src in covered if s < at and e > begin})
                status = f"UNBOUND {loose}" if loose else f"OK ({'; '.join(sources)})"
                where = doc.relative_to(HERE) if doc.is_relative_to(HERE) else doc
                out.append(f"{where}:{line} {status}: {sentence[:120]}")
    return out


def main() -> int:
    if sys.argv[1:2] == ["--report"]:
        DOCS[0] = Path(sys.argv[2]).resolve()
    out = verdict(bound())
    print("\n".join(out))
    bad = sum(" UNBOUND " in line for line in out)
    print(f"claims: {len(out)} sentences, {len(out) - bad} bound to evidence, {bad} UNBOUND")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
