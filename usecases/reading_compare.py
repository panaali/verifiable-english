"""The sealed-answer gate of feature C (answers under each named reading): compares every per-reading answer with the sealed
per-reading answers, and FAILS on any mismatch, on a stale run or check, or on a reading replaced after it was checked.
Outside VE core and the kernel; it reads files only and decides nothing (an answer is the law's Lean-checked run, made by
usecases/reading_runs.py).

Ruling: orchestrator 2026-11-24T00:00Z (feature C resumes on after-release under six gates). This module is gates (1), (2)
and the counting half of (4) and (6):
  (1) every per-reading answer of every table's run is compared with the sealed answer of the reading the match graders
      matched it to; a mismatch is WRONG and fails. A run made on another version of the table (table_sha256) is STALE and
      fails, so a change to a table cannot pass until the table is run again and compared again.
  (2) a reading's name is frozen in READINGS.tsv when it is first checked. A table whose reading has another name fails
      (SWAP): a fix round may not replace a reading. A block whose reading was replaced, or that a checker judged not
      careful, is STOPPED there: its questions are DISPUTED, never answered. Every check named in CHECKS.tsv (the table
      check, the source check by an uninvolved session, both match graders) must have run on the current table; one that
      ran on another version is STALE and fails.
  (4) where the graders find that VE's reading is not the question writer's (NO MATCH), or they disagree, the question is
      DISPUTED (both readings listed by the report), not answered.
  (6) the counts are per reading and stand apart: nothing here returns or adds to a single-answer (headline) count.

Directory (usecases/reading_tables/): <law>.tsv (reading tables), runs/<law>.json (reading_runs.py output),
match/<grader>.txt (`# table <law> <sha256>` lines, then `<law>:<record>:<block>: A=a B=b | A=b B=a | NO MATCH` lines),
SEALED.tsv (question, law, sealed_a, sealed_b: JSON or `blocked`; every value may be stored as "sha256:<hex>", see
seal()), READINGS.tsv (law, block, reading, name_sha256, status LIVE|STOPPED, since, note), CHECKS.tsv (law, check,
table_sha256, utc, verdict, file), FINDINGS.tsv (HIGH findings of a check that move no listed answer, with their
disposition).

Usage: python -B usecases/reading_compare.py [--dir usecases/reading_tables] [--json out.json]   (rc 1 on any failure)
       python -B usecases/reading_compare.py --seal <plain key tsv> <out tsv>
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent / "reading_tables"
CHECKS_NEEDED = ("source-check",)  # the table checklist and the answers against the SOURCE, by an uninvolved session
CHECK_OK = {"source-check": {"SOUND"}}
# A source check may also pass with HIGH findings that move no listed answer, each recorded with its disposition in
# FINDINGS.tsv (law, table_sha256, check, severity, moves_listed_answer, finding, disposition) for that table version.
HIGH_NO_MOVE = re.compile(r"0 WRONG, (\d+) HIGH \(no listed answer moves\)")
UNDECIDED = {"OPEN", "UNSUPPORTED", "REFUSED", "UNKNOWN", "INCONSISTENT", "CANNOT", "ERROR", "N/A", ""}
MATCHES = ("A=a B=b", "A=b B=a", "NO MATCH")


def sha(b):
    return hashlib.sha256(b if isinstance(b, bytes) else b.encode("utf-8")).hexdigest()


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


def canon(v):
    return json.dumps(sorted(v) if isinstance(v, list) else v, sort_keys=True, ensure_ascii=False)


def seal(question, reading, field, value):
    """The stored form of one sealed value: sha256 of question|reading|field|canonical value (a reader of the file does
    not see the answer; the comparison hashes VE's value the same way)."""
    return "sha256:" + sha(f"{question}|{reading}|{field}|{canon(value)}")


def _tsv(path):
    rows = [ln.split("\t") for ln in Path(path).read_text(encoding="utf-8").splitlines()
            if ln.strip() and not ln.startswith("#")]
    return [dict(zip(rows[0], r)) for r in rows[1:]] if rows else []


def load_key(path):
    """-> {question: (law, {"a": value | None, "b": value | None})}; None = blocked (no provision to write)."""
    key = {}
    for r in _tsv(path):
        key[r["question"]] = (r["law"], {x: None if r[f"sealed_{x}"] == "blocked" else json.loads(r[f"sealed_{x}"])
                                         for x in "ab"})
    return key


def same(question, reading, ve, sealed):
    """VE's value equals the sealed one: a dict on every field the sealed record gives (null fields are not compared),
    a list as a set, else exactly. A sealed "sha256:" value is compared by hashing VE's value."""
    def eq(field, v, s):
        return seal(question, reading, field, v) == s if isinstance(s, str) and s.startswith("sha256:") else (
            sorted(v) == sorted(s) if isinstance(s, list) and isinstance(v, list) else v == s)
    if isinstance(sealed, dict):
        return isinstance(ve, dict) and all(eq(k, ve.get(k), s) for k, s in sealed.items() if s is not None)
    return eq("", ve, sealed)


def decided(v):
    if isinstance(v, dict):
        if v.get("lean_rejected"):
            return False
        v = v.get("answer")
    return isinstance(v, list) or (isinstance(v, str) and v.strip().upper() not in UNDECIDED)


def load_matches(path):
    """-> ({law: table sha256 the grader saw}, {item: match})."""
    tables, out = {}, {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        m = re.match(r"#\s*table\s+(\S+)\s+([0-9a-f]{64})\s*$", line)
        if m:
            tables[m.group(1)] = m.group(2)
            continue
        m = re.match(r"\s*`?([\w.-]+:[\w-]+:B\d+)`?\s*:\s*(A=a B=b|A=b B=a|NO MATCH)", line)
        if m:
            out[m.group(1)] = m.group(2)
    return tables, out


def table_readings(path):
    """-> {(block, reading): name} from a reading table (the columns reading_runs.py reads)."""
    out, header = {}, None
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        cells = line.split("\t")
        if header is None:
            header = cells
            continue
        row = dict(zip(header, cells))
        out[(row["block"], row["reading"])] = row["name"]
    return out


def check(d=HERE):
    """-> {"failures": [...], "laws": {law: {...}}, "questions": [...]} over every table in d. Failures: STALE, SWAP,
    WRONG, MISSING."""
    d = Path(d)
    key = load_key(d / "SEALED.tsv")
    register = {(r["law"], r["block"], r["reading"]): r for r in _tsv(d / "READINGS.tsv")}
    checks = {}
    for r in _tsv(d / "CHECKS.tsv"):
        checks.setdefault((r["law"], r["check"]), []).append(r)
    findings = _tsv(d / "FINDINGS.tsv") if (d / "FINDINGS.tsv").exists() else []
    graders = sorted((d / "match").glob("*.txt"))
    matches = [load_matches(p) for p in graders]
    fails, laws, questions = [], {}, []
    if len(graders) != 2:
        fails.append(f"MISSING: {len(graders)} match grader files in match/ (two needed)")
    for table in sorted(d.glob("*.tsv")):
        law = table.stem
        if law.isupper():
            continue
        tsha, readings = sha(table.read_bytes()), table_readings(table)
        run_path = d / "runs" / f"{law}.json"
        run = json.loads(run_path.read_text(encoding="utf-8")) if run_path.exists() else None
        if run is None:
            fails.append(f"STALE {law}: no run of the table (runs/{law}.json)")
        elif run.get("table_sha256") != tsha:
            fails.append(f"STALE {law}: the run was made on table {str(run.get('table_sha256'))[:12]}, the table is "
                         f"{tsha[:12]}: run it again")
        stopped = set()
        for (bid, r), name in sorted(readings.items()):
            reg = register.get((law, bid, r))
            if reg is None:
                fails.append(f"MISSING {law} {bid} {r}: reading not in READINGS.tsv (freeze its name when first checked)")
            elif reg["name_sha256"] != sha(norm(name)):
                fails.append(f"SWAP {law} {bid} {r}: the reading's name is not the one frozen {reg['since']} (a fix round"
                             " may not replace a reading; a reading judged not careful STOPS its block)")
            if reg is not None and reg["status"] == "STOPPED":
                stopped.add(bid)
        live = {bid for bid, _ in readings} - stopped
        for c in CHECKS_NEEDED if live else ():
            rs = [x for x in checks.get((law, c), []) if x["table_sha256"] == tsha]
            if not rs:
                fails.append(f"STALE {law}: no {c} on table {tsha[:12]} (every check runs again on the final table)")
            elif rs[-1]["verdict"] not in CHECK_OK[c]:
                m = HIGH_NO_MOVE.fullmatch(rs[-1]["verdict"])
                rec = [f for f in findings if (f["law"], f["table_sha256"], f["check"], f["severity"]) == (law, tsha, c, "HIGH")
                       and f["moves_listed_answer"] == "no" and f["disposition"].strip()]
                if not m or int(m.group(1)) != len(rec):
                    fails.append(f"{c.upper()} {law}: verdict {rs[-1]['verdict']!r} on table {tsha[:12]} ({len(rec)} HIGH "
                                 "findings recorded with a disposition in FINDINGS.tsv)")
        for i, (seen, _) in enumerate(matches):
            if live and seen.get(law) != tsha:
                fails.append(f"STALE {law}: match grader {graders[i].name} saw table {str(seen.get(law))[:12]}, the "
                             f"table is {tsha[:12]}")
        per = {"answered": 0, "disputed": 0, "wrong": 0, "not answered": 0}
        for bid, blk in sorted(((run or {}).get("blocks") or {}).items()):
            for q, res in sorted(blk["questions"].items()):
                row = _grade(law, bid, q, res, key, [m for _, m in matches], bid in stopped)
                questions.append(row)
                for r in "AB":
                    per[row["status"][r]] += 1
                    if row["status"][r] == "wrong":
                        fails.append(f"WRONG {law} {q} reading {r}: VE {row['ve'][r]!r} differs from the sealed "
                                     f"answer of the matched reading")
        laws[law] = {"table_sha256": tsha, "per_reading": per, "stopped": sorted(stopped)}
    return {"failures": fails, "laws": laws, "questions": questions}


def _grade(law, bid, q, res, key, matches, stopped):
    case, rec = q.split("/", 1)
    row = {"law": law, "block": bid, "question": q, "ve": res.get("answers", {}), "status": {}, "why": ""}
    found = [m.get(f"{law}:{rec}:{bid}") or m.get(f"{law}:{case}:{bid}") for m in matches]
    row["match"] = found
    if q not in key or key[q][1]["a"] is None:
        row.update(status={"A": "not answered", "B": "not answered"}, why="no sealed per-reading answer")
    elif stopped:
        row.update(status={"A": "disputed", "B": "disputed"}, why="block STOPPED (READINGS.tsv): our readings are not "
                   "the question writer's; both are listed, none is counted")
    elif res.get("status") != "per-reading":
        row.update(status={"A": "not answered", "B": "not answered"}, why="a guard failed")
    elif len(found) != 2 or found[0] != found[1] or found[0] is None or found[0] == "NO MATCH":
        row.update(status={"A": "disputed", "B": "disputed"}, why=f"graders: {found} (our reading is not the question "
                   "writer's, or the graders differ): both readings listed, none counted")
    else:
        row["why"] = f"matched {found[0]}"
    if row["status"]:
        if not stopped and res.get("status") == "per-reading" and q in key and key[q][1]["a"] is not None:
            _wrong_any(row, q, res, key, found)  # a mismatch under ANY grader's match fails, even when not counted
        return row
    for r in "AB":
        row["status"][r] = _one(q, r, res, key, PAIRS[found[0]])
    return row


PAIRS = {"A=a B=b": {"A": "a", "B": "b"}, "A=b B=a": {"A": "b", "B": "a"}}


def _one(q, r, res, key, pair):
    v = res["answers"].get(r)
    if not res.get("decided", {}).get(r, decided(v)):
        return "not answered"
    return "answered" if same(q, pair[r], v, key[q][1][pair[r]]) else "wrong"


def _wrong_any(row, q, res, key, found):
    for m in {f for f in found if f in PAIRS}:
        for r in "AB":
            if _one(q, r, res, key, PAIRS[m]) == "wrong":
                row["status"][r] = "wrong"
                row["why"] += f"; under grader match {m} reading {r} differs from the sealed answer"


def seal_file(plain, out):
    """Write the sealed key with every value hashed (seal())."""
    lines = []
    for ln in Path(plain).read_text(encoding="utf-8").splitlines():
        if ln.startswith("#") or ln.startswith("question\t") or not ln.strip():
            if not ln.startswith("#"):
                lines.append("question\tlaw\tsealed_a\tsealed_b")
            continue
        q, law, a, b = ln.split("\t")[:4]
        cells = []
        for x, v in (("a", a), ("b", b)):
            if v == "blocked":
                cells.append(v)
                continue
            v = json.loads(v)
            cells.append(json.dumps({k: None if s is None else seal(q, x, k, s) for k, s in v.items()}
                                    if isinstance(v, dict) else seal(q, x, "", v)))
        lines.append("\t".join([q, law, *cells]))
    Path(out).write_text("# sealed per-reading answers, each value hashed (usecases/reading_compare.py seal())\n"
                         + "\n".join(lines) + "\n", encoding="utf-8")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=str(HERE))
    ap.add_argument("--json")
    ap.add_argument("--seal", nargs=2, metavar=("PLAIN", "OUT"))
    a = ap.parse_args(argv)
    if a.seal:
        seal_file(*a.seal)
        return 0
    res = check(a.dir)
    for law, v in res["laws"].items():
        print(law, " ".join(f"{k} {n}" for k, n in v["per_reading"].items()), "(per reading; never in a headline)")
    for f in res["failures"]:
        print("FAIL", f)
    if a.json:
        Path(a.json).write_text(json.dumps(res, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print("PASS" if not res["failures"] else f"FAILED: {len(res['failures'])}")
    return 1 if res["failures"] else 0


if __name__ == "__main__":
    sys.exit(main())
