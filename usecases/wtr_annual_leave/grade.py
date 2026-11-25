"""Compare a run file with the sealed answers (sha256 checked). Committed BEFORE the headline run.

usage: python3 -I grade.py RUN.json <manage-agents>/reviews/spare/statute-corpus/batch4/wtr-annual-leave [--out GRADES.json]
Reads <dir>/sealed/answers.jsonl (sha256 must equal the seal) and <dir>/questions.jsonl (scope, kind and the writer's tags).
Per in-scope question: match (VE's answer equals the sealed one: Q4 yes/no; Q1 days as a decimal; Q2 an amount of money as a
decimal, "no payment" as 0; Q3 a date), disagree (VE answered, differently: two fresh graders; VE certain and graded wrong =
a WRONG answer), refused (OPEN), unsupported, writer-ambiguous (the writer filled "ambiguous": not correct whatever VE says).
Probes apart. A writer answer whose form cannot be read mechanically is compared as text (a mismatch goes to the graders).
"Without anything computed outside Lean": a match counts only if its documents use no bridged value (run record "bridged" vs
"uses"), its case has no encoder judgement, and the writer tagged it "none"; the denominator drops questions that lean on any
of these (as posthog_leave/grade.py). "Excluding table rows": the text has no table rows (units.jsonl: 0), so it equals the
headline.
"""
import datetime as dt
import hashlib
import json
import re
import sys
from decimal import Decimal, InvalidOperation

SEALED_SHA256 = "eebea071731c740b8ca8a9f42f954277e78df9ab79035c23fa20df1141d25d8c"
QUESTIONS_SHA256 = "8cdfe73b7bbc79b1433e7bea065502c05df50d6f8be3802592c62d8f60acfe00"
TABLE = set()
NUM = re.compile(r"-?\d[\d,]*(?:\.\d+)?")
NOPAY = re.compile(r"\b(no payment|nothing|nil|none|zero|not required|no sum)\b")


def _dec(s):
    try:
        return Decimal(s.replace(",", ""))
    except (InvalidOperation, AttributeError):
        return None


def _date(s):
    s = " ".join(str(s).split()).strip(" .")
    for fmt in ("%Y-%m-%d", "%d %B %Y", "%A %d %B %Y", "%A, %d %B %Y", "%B %d, %Y", "%d %b %Y"):
        try:
            return dt.datetime.strptime(s, fmt).date().isoformat()
        except ValueError:
            pass
    m = re.search(r"\d{4}-\d{2}-\d{2}", s)
    if m:
        return m[0]
    m = re.search(r"\d{1,2} [A-Z][a-z]+ \d{4}", s)
    return _date(m[0]) if m else None


def norm(a, kind):
    ans, val = a.get("answer"), a.get("value")
    if kind == "Q4":
        for x in (val, ans):
            m = re.match(r"\s*(yes|no)\b", str(x).lower()) if x is not None else None
            if m:
                return m[1]
        return " ".join(str(ans).lower().split())
    if kind == "Q3":
        for x in (val, ans):
            d = _date(x) if x is not None else None
            if d:
                return d
        return " ".join(str(ans).lower().split())
    for x in (val, ans):              # Q1 days, Q2 money
        if isinstance(x, (int, float)):
            return Decimal(str(x))
        if isinstance(x, str):
            m = NUM.search(x)
            if m:
                return _dec(m[0])
            if kind == "Q2" and NOPAY.search(x.lower()):
                return Decimal(0)
    return " ".join(str(ans).lower().split())


def same(v, w, kind):
    a, b = norm(v, kind), norm(w, kind)
    if isinstance(a, Decimal) and isinstance(b, Decimal):
        return a == b
    return a == b


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
            meta[x["qid"]] = {"scope": c["scope"], "kind": x["kind"], "tag": x.get("tag"), "covers": x.get("covers", [])}
    ve, rec_of = {}, {}
    for r in run["records"]:
        for q, a in r["answers"].items():
            ve[q], rec_of[q] = a, r
    rows = []
    for qid, m in meta.items():
        w, v = sealed[qid], ve[qid]
        if m["scope"] == "out":
            status = "probe-unsupported" if v["answer"] == "UNSUPPORTED" else "probe-answered"
        elif v["answer"] == "UNSUPPORTED":
            status = "unsupported"
        elif v["answer"] == "OPEN":
            status = "refused"
        elif w.get("ambiguous"):
            status = "writer-ambiguous" + ("-match" if same(v, w, m["kind"]) else "-differ")
        elif same(v, w, m["kind"]):
            status = "match"
        else:
            status = "disagree"
        r = rec_of[qid]
        used_bridge = sorted(set(r.get("uses", {}).get(qid, [])) & set(r.get("bridged", [])))
        judged = bool(r.get("encoder_judgement"))
        inside = status == "match" and not used_bridge and not judged and m["tag"] == "none"
        rows.append({"qid": qid, **m, "status": status, "ve": v.get("value", v["answer"]), "writer": w.get("answer"),
                     "writer_value": w.get("value"), "ambiguous": w.get("ambiguous"), "uses_bridge": used_bridge,
                     "encoder_judgement": judged, "inside_lean": inside, "table_only": False})
    ins = [r for r in rows if r["scope"] == "in"]
    count = lambda rs, st: sum(r["status"] == st for r in rs)  # noqa: E731
    outside_den = [r for r in ins if not (r["uses_bridge"] or r["encoder_judgement"] or r["tag"] != "none")]
    summary = {"in_scope_written": len(ins), "match": count(ins, "match"), "disagree": count(ins, "disagree"),
               "refused": count(ins, "refused"), "unsupported": count(ins, "unsupported"),
               "writer_ambiguous": sum(r["status"].startswith("writer-ambiguous") for r in ins),
               "writer_ambiguous_rows": [(r["qid"], r["status"]) for r in ins if r["status"].startswith("writer-ambiguous")],
               "refused_rows": [r["qid"] for r in ins if r["status"] == "refused"],
               "disagree_rows": [r["qid"] for r in ins if r["status"] == "disagree"],
               "by_tag": {t: {"written": sum(r["tag"] == t for r in ins),
                              "match": sum(r["tag"] == t and r["status"] == "match" for r in ins)}
                          for t in ("none", "bridge-only", "stated-judgment")},
               "by_question_kind": {k: {"written": sum(r["kind"] == k for r in ins),
                                        "match": sum(r["kind"] == k and r["status"] == "match" for r in ins)}
                                    for k in ("Q1", "Q2", "Q3", "Q4")},
               "without_outside_lean": {"written": len(outside_den), "match": sum(r["inside_lean"] for r in ins)},
               "excluding_table_rows": {"written": len(ins), "match": count(ins, "match")},
               "probes": {"written": len(rows) - len(ins),
                          "unsupported": sum(r["status"] == "probe-unsupported" for r in rows)},
               "run_commit": run["commit"], "run_tree_clean": run["tree_clean"]}
    out = {"summary": summary, "rows": rows}
    text = json.dumps(out, indent=1, sort_keys=True) + "\n"
    if "--out" in argv:
        open(argv[argv.index("--out") + 1], "w", encoding="utf-8").write(text)
    print(json.dumps(summary, indent=1, sort_keys=True))


if __name__ == "__main__":
    main(sys.argv[1:])
