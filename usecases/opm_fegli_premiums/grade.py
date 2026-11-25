"""Compare a run file with the sealed answers (sha256 checked). CROSS-FAMILY questions (Codex writer). Committed BEFORE the
headline run.

usage: python3 -I grade.py RUN.json <manage-agents>/reviews/spare/statute-corpus/batch4/opm-fegli-premiums [--out GRADES.json]
Reads <dir>/sealed/answers.jsonl (sha256 must equal the seal) and <dir>/questions.jsonl (scope and the writer's tags).
Per in-scope question: match (VE's answer equals the sealed answer after norm(): yes / no; an amount or a number of days
compared as a decimal; a date (YYYY-MM-DD) or a date and time (YYYY-MM-DDTHH:MM) compared as text), disagree (VE
answered, differently: goes to two fresh graders; VE certain and graded wrong = a WRONG answer), refused (OPEN),
unsupported, writer-ambiguous (the writer filled "ambiguous": not correct whatever VE says). Probes apart.
"Without anything computed outside Lean": a question leaves the denominator if its own sub-case carries an encoder
judgement, the writer tagged it other than "none", its sub-case states a stated judgment (translation.STATED_JUDGMENT; run
file subs[].uses_stated_judgment), or VE's answer documents use a bridged fact (none: this translation has no bridge); a
refused question stays in the denominator (not correct).
"Excluding table rows": the in-scope questions whose sealed "covers" (questions.jsonl, the writer's) name no table-row
unit (<dir>/units.jsonl table_row; batch 2 CHALLENGE B4, uc-award ISOLATION D9).
"""
import hashlib
import json
import re
import sys
from decimal import Decimal, InvalidOperation

SEALED_SHA256 = "2ed659bb73cae94f94c153c0d53a33796cd93ec764bfce7b76699a5901d3ff40"
QUESTIONS_SHA256 = "e3b3e9811163d93fc45840a2d54d5e369fc4de35b4addd75a5db5817760ac1b6"
UNITS_SHA256 = "25f080faa5bdff8dcb6e29cc4a8865dd16c6e381d389e47ff47f2cb5da0bf840"
DATE = re.compile(r"\d{4}-\d{2}-\d{2}(?:T\d{2}:\d{2})?")


def norm(a, kind):
    """-> a comparable value: 'yes' / 'no' / a date text / a Decimal / the lower-cased text."""
    if kind in ("Q2", "Q3"):
        for v in (a.get("value"), a.get("answer")):
            if v is None:
                continue
            m = DATE.search(str(v))
            if m:
                return m[0]
            m = re.search(r"-?\d[\d,]*(?:\.\d+)?", str(v))
            if m:
                try:
                    return Decimal(m[0].replace(",", ""))
                except InvalidOperation:
                    pass
    t = " ".join(str(a.get("answer")).strip().lower().rstrip(".").split())
    for yn in ("yes", "no"):
        if t == yn or t.startswith(yn + ",") or t.startswith(yn + ";") or t.startswith(yn + " "):
            return yn
    return t


def main(argv):
    run = json.load(open(argv[0], encoding="utf-8"))
    d = argv[1]
    raw = open(d + "/sealed/answers.jsonl", "rb").read()
    if hashlib.sha256(raw).hexdigest() != SEALED_SHA256:
        raise SystemExit("sealed answers.jsonl sha256 differs from the seal")
    qraw = open(d + "/questions.jsonl", "rb").read()
    if hashlib.sha256(qraw).hexdigest() != QUESTIONS_SHA256:
        raise SystemExit("questions.jsonl sha256 differs from the seal")
    uraw = open(d + "/units.jsonl", "rb").read()
    if hashlib.sha256(uraw).hexdigest() != UNITS_SHA256:
        raise SystemExit("units.jsonl sha256 differs from the pin")
    table = {str(u["n"]) for u in map(json.loads, uraw.decode().splitlines()) if u and u.get("table_row")}
    sealed = {a["qid"]: a for a in map(json.loads, raw.decode().splitlines()) if a}
    meta = {}
    for c in map(json.loads, qraw.decode().splitlines()):
        for x in c["questions"]:
            meta[x["qid"]] = {"scope": c["scope"], "kind": x["kind"], "tag": x["tag"],
                              "table": any(str(u) in table for u in x.get("covers", []))}
    ve, rec_of = {}, {}
    for r in run["records"]:
        for q, a in r["answers"].items():
            ve[q], rec_of[q] = a, r
    rows = []
    for qid, m in meta.items():
        w, v = sealed[qid], ve[qid]
        same = norm(v, m["kind"]) == norm(w, m["kind"])
        if m["scope"] == "out":
            status = "probe-unsupported" if v["answer"] == "UNSUPPORTED" else "probe-answered"
        elif v["answer"] == "UNSUPPORTED":
            status = "unsupported"
        elif v["answer"] == "OPEN":
            status = "refused"
        elif w.get("ambiguous"):
            status = "writer-ambiguous" + ("-match" if same else "-differ")
        elif same:
            status = "match"
        else:
            status = "disagree"
        judged = qid in rec_of[qid].get("encoder_judgement_q", {})
        sj = any(sub.get("uses_stated_judgment", {}).get(qid) for sub in rec_of[qid].get("subs", []))
        bridged = any(sub.get("uses_bridge", {}).get(qid) for sub in rec_of[qid].get("subs", []))
        inside = status == "match" and not judged and m["tag"] == "none" and not bridged and not sj
        rows.append({"qid": qid, **m, "status": status, "ve": v, "writer": {"answer": w.get("answer"),
                     "value": w.get("value")}, "ambiguous": w.get("ambiguous"), "encoder_judgement": judged,
                     "stated_judgment": sj, "uses_bridge": bridged, "refused_why": v.get("refused"), "inside_lean": inside})
    ins = [r for r in rows if r["scope"] == "in"]
    plain = [r for r in ins if r["tag"] == "none"]
    count = lambda rs, st: sum(r["status"] == st for r in rs)  # noqa: E731
    outside_den = [r for r in ins if not (r["encoder_judgement"] or r["tag"] != "none" or r["uses_bridge"]
                                          or r["stated_judgment"])]
    summary = {"in_scope_written": len(ins), "match": count(ins, "match"), "disagree": count(ins, "disagree"),
               "refused": count(ins, "refused"), "unsupported": count(ins, "unsupported"),
               "writer_ambiguous": sum(r["status"].startswith("writer-ambiguous") for r in ins),
               "writer_ambiguous_rows": [(r["qid"], r["status"]) for r in ins if r["status"].startswith("writer-ambiguous")],
               "refused_rows": [(r["qid"], r["refused_why"]) for r in ins if r["status"] == "refused"],
               "disagree_rows": [r["qid"] for r in ins if r["status"] == "disagree"],
               "excluding_bridge_and_stated": {"written": len(plain), "match": count(plain, "match"),
                                               "disagree": count(plain, "disagree")},
               "by_tag": {t: {"written": sum(r["tag"] == t for r in ins),
                              "match": sum(r["tag"] == t and r["status"] == "match" for r in ins)}
                          for t in ("none", "bridge-only", "stated-judgment")},
               "by_question_kind": {k: {"written": sum(r["kind"] == k for r in ins),
                                        "match": sum(r["kind"] == k and r["status"] == "match" for r in ins)}
                                    for k in ("Q1", "Q2", "Q3")},
               "without_outside_lean": {"written": len(outside_den), "match": sum(r["inside_lean"] for r in ins)},
               "probes": {"written": len(rows) - len(ins),
                          "unsupported": sum(r["status"] == "probe-unsupported" for r in rows)},
               "excluding_table_rows": {"written": sum(not r["table"] for r in ins),
                                        "match": sum(not r["table"] and r["status"] == "match" for r in ins)},
               "run_commit": run["commit"], "run_tree_clean": run["tree_clean"]}
    out = {"summary": summary, "rows": rows}
    text = json.dumps(out, indent=1, sort_keys=True, default=str) + "\n"
    if "--out" in argv:
        open(argv[argv.index("--out") + 1], "w", encoding="utf-8").write(text)
    print(json.dumps(summary, indent=1, sort_keys=True, default=str))


if __name__ == "__main__":
    main(sys.argv[1:])
