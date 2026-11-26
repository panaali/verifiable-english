"""Compare a run file with the sealed answers (sha256 checked). CROSS-FAMILY questions (Codex writer), Opus translator.
Committed BEFORE the headline run.

usage: python3 -I grade.py RUN.json <manage-agents>/reviews/spare/statute-corpus/batch4/github-copilot-ext [--out GRADES.json]
Reads <dir>/sealed/answers.jsonl (sha256 must equal the seal) and <dir>/questions.jsonl (scope and the writer's tags).
Per in-scope question: match (VE's answer equals the sealed answer after norm(): yes / no; a date as YYYY-MM-DD), disagree
(VE answered, differently: goes to two fresh graders; VE certain and graded wrong = a WRONG answer), refused (OPEN, encoder
refusals included), unsupported, writer-ambiguous (the writer filled "ambiguous": not correct whatever VE says). Probes apart.
"Without anything computed outside Lean": a question leaves the denominator if its case has an encoder judgement, the writer
tagged it other than "none", or its answer uses a bridged fact (none: this text has no bridge); a refused question stays in
the denominator (not correct).
"""
import hashlib
import json
import re
import sys
from decimal import Decimal, InvalidOperation

SEALED_SHA256 = "1438647442badf1d333423e979cd90ab7799308645c895e5a8273df08ef3dc73"
QUESTIONS_SHA256 = "c47303e2479068c9f3c1398275d1046282a288fec8138c685443956f379f4a5a"


MONTHS = {m: i + 1 for i, m in enumerate(["january", "february", "march", "april", "may", "june", "july", "august",
                                           "september", "october", "november", "december"])}


def _date(v):
    if v is None:
        return None
    t = str(v).strip()
    m = re.search(r"(\d{4})-(\d{2})-(\d{2})", t)
    if m:
        return m[0]
    m = re.search(r"(\d{1,2}) ([A-Za-z]+),? (\d{4})", t)
    if m and m[2].lower() in MONTHS:
        return f"{int(m[3]):04d}-{MONTHS[m[2].lower()]:02d}-{int(m[1]):02d}"
    return None


def norm(a, kind):
    """-> a comparable value: 'yes' / 'no' / an ISO date / the lower-cased text."""
    if a.get("answer") == "DATE":
        return a.get("value")
    d = _date(a.get("value")) or (_date(a.get("answer")) if kind == "Q3" else None)
    if d:
        return d
    t = " ".join(str(a.get("answer")).strip().lower().split())
    w = re.match(r"[a-z]+", t)
    if w and w[0] in ("yes", "no"):
        return w[0]
    return t.rstrip(".")


def main(argv):
    run = json.load(open(argv[0], encoding="utf-8"))
    d = argv[1]
    raw = open(d + "/sealed/answers.jsonl", "rb").read()
    if hashlib.sha256(raw).hexdigest() != SEALED_SHA256:
        raise SystemExit("sealed answers.jsonl sha256 differs from the seal")
    qraw = open(d + "/questions.jsonl", "rb").read()
    if hashlib.sha256(qraw).hexdigest() != QUESTIONS_SHA256:
        raise SystemExit("questions.jsonl sha256 differs from the seal")
    sealed = {a["qid"]: a for a in map(json.loads, raw.decode().splitlines()) if a}
    meta = {}
    for c in map(json.loads, qraw.decode().splitlines()):
        for x in c["questions"]:
            meta[x["qid"]] = {"scope": c["scope"], "kind": x["kind"], "tag": x["tag"]}
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
        judged = bool(rec_of[qid].get("encoder_judgement"))
        bridged = any(sub.get("uses_bridge", {}).get(qid) for sub in rec_of[qid].get("subs", []))
        inside = status == "match" and not judged and m["tag"] == "none" and not bridged
        rows.append({"qid": qid, **m, "status": status, "ve": v, "writer": {"answer": w.get("answer"),
                     "value": w.get("value")}, "ambiguous": w.get("ambiguous"), "encoder_judgement": judged, "uses_bridge": bridged,
                     "refused_why": v.get("refused"), "inside_lean": inside})
    ins = [r for r in rows if r["scope"] == "in"]
    plain = [r for r in ins if r["tag"] == "none"]
    count = lambda rs, st: sum(r["status"] == st for r in rs)  # noqa: E731
    outside_den = [r for r in ins if not (r["encoder_judgement"] or r["tag"] != "none" or r["uses_bridge"])]
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
               "run_commit": run["commit"], "run_tree_clean": run["tree_clean"]}
    out = {"summary": summary, "rows": rows}
    text = json.dumps(out, indent=1, sort_keys=True, default=str) + "\n"
    if "--out" in argv:
        open(argv[argv.index("--out") + 1], "w", encoding="utf-8").write(text)
    print(json.dumps(summary, indent=1, sort_keys=True, default=str))


if __name__ == "__main__":
    main(sys.argv[1:])
