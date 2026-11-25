"""Compare a run file with the sealed answers (sha256 checked). CROSS-FAMILY questions. Written with the translation, BEFORE the
encoder's question file was opened; committed before the headline run. (hipaa_breach_notice/grade.py, adapted.)

usage: python3 -I grade.py RUN.json <manage-agents>/reviews/spare/statute-corpus/batch4/canada-vacations [--out GRADES.json]
Reads <dir>/sealed/answers.jsonl (sha256 must equal the seal) and <dir>/questions.jsonl (scope, kind and the writer's tags).
Per in-scope question: match (VE's answer equals the sealed one: Q1 the number of weeks, "none" = 0; Q2 the amount as a
decimal number of dollars, "none" = 0; Q3 the day YYYY-MM-DD (the sealed "value", else a day in its answer); Q4 yes/no by the
answer's first word), disagree (VE answered, differently: two fresh graders; VE certain and graded wrong = a WRONG answer),
refused (OPEN), unsupported, writer-ambiguous (the writer filled "ambiguous": not correct whatever VE says, ISOLATION.md D9).
Probes apart.
"Without anything computed outside Lean": a match counts only if its documents use no bridged value (run record "bridged" vs
"uses"), its case has no encoder judgement for it, and the writer tagged it "none".
"""
import hashlib
import json
import re
import sys

SEALED_SHA256 = "4abe5f89001fa923e229a33922ddc9715662c5d6dd61210d8187a561e820e75b"
QUESTIONS_SHA256 = "b694f88a4af3d40b908861a2de8b7113562c2d2b9ac929e98d05a35c89007d7b"


def norm_yn(v):
    m = re.match(r"\W*([A-Za-z]+)", str(v))
    return m.group(1).lower() if m else str(v).strip().lower()


MONTHS = {m: i for i, m in enumerate(["january", "february", "march", "april", "may", "june", "july", "august",
                                        "september", "october", "november", "december"], 1)}


def number(a):
    """-> Decimal of the value (else the first number in the answer); "none" / "no ..." = 0; else None."""
    from decimal import Decimal, InvalidOperation
    for v in (a.get("value"), a.get("answer")):
        if v is None:
            continue
        t = str(v).strip().lower()
        if t.startswith("none") or t in ("0", "nil"):
            return Decimal(0)
        m = re.search(r"-?\d[\d,]*(?:\.\d+)?", t)
        if m:
            try:
                return Decimal(m[0].replace(",", ""))
            except InvalidOperation:
                pass
    return None


def day(a):
    for v in (a.get("value"), a.get("answer")):
        if v is None:
            continue
        t = str(v).strip()
        m = re.search(r"(\d{4})-(\d{2})-(\d{2})", t)
        if m:
            return m[0]
        m = re.search(r"(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})", t)
        if m and m[2].lower() in MONTHS:
            return f"{int(m[3]):04d}-{MONTHS[m[2].lower()]:02d}-{int(m[1]):02d}"
    return None


def same(kind, ve, w):
    if kind in ("Q1", "Q2"):
        a, b = number(ve), number(w)
        return a is not None and a == b
    if kind == "Q3":
        a, b = day(ve), day(w)
        return a is not None and a == b
    return norm_yn(ve.get("answer")) == norm_yn(w.get("answer"))


def judged_for(r, qid):
    return [j for j in r.get("encoder_judgement", []) if j.split(":", 1)[0] in (qid, r["id"])]


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
        if m["scope"] == "out":
            status = "probe-unsupported" if v["answer"] == "UNSUPPORTED" else "probe-answered"
        elif v["answer"] == "UNSUPPORTED":
            status = "unsupported"
        elif v["answer"] == "OPEN":
            status = "refused"
        elif w.get("ambiguous"):
            status = "writer-ambiguous" + ("-match" if same(m["kind"], v, w) else "-differ")
        elif same(m["kind"], v, w):
            status = "match"
        else:
            status = "disagree"
        r = rec_of[qid]
        used_bridge = sorted(set(r.get("uses", {}).get(qid, [])) & set(r.get("bridged", [])))
        judged = bool(judged_for(r, qid))
        inside = status == "match" and not used_bridge and not judged and m["tag"] == "none"
        rows.append({"qid": qid, **m, "status": status, "ve": v["answer"], "no_form": bool(v.get("no_form")),
                     "writer": w.get("answer"), "writer_value": w.get("value"), "ambiguous": w.get("ambiguous"),
                     "uses_bridge": used_bridge, "encoder_judgement": judged, "inside_lean": inside})
    ins = [r for r in rows if r["scope"] == "in"]
    plain = [r for r in ins if r["tag"] == "none"]
    count = lambda rs, st: sum(r["status"] == st for r in rs)  # noqa: E731
    outside_den = [r for r in ins if not (r["uses_bridge"] or r["encoder_judgement"] or r["tag"] != "none")]
    summary = {"in_scope_written": len(ins), "match": count(ins, "match"), "disagree": count(ins, "disagree"),
               "refused": count(ins, "refused"), "refused_no_form": sum(r["status"] == "refused" and r["no_form"] for r in ins),
               "unsupported": count(ins, "unsupported"),
               "writer_ambiguous": sum(r["status"].startswith("writer-ambiguous") for r in ins),
               "writer_ambiguous_rows": [(r["qid"], r["status"]) for r in ins if r["status"].startswith("writer-ambiguous")],
               "refused_rows": [r["qid"] for r in ins if r["status"] == "refused"],
               "disagree_rows": [r["qid"] for r in ins if r["status"] == "disagree"],
               "excluding_bridge_and_stated": {"written": len(plain), "match": count(plain, "match"),
                                               "disagree": count(plain, "disagree")},
               "by_tag": {t: {"written": sum(r["tag"] == t for r in ins),
                              "match": sum(r["tag"] == t and r["status"] == "match" for r in ins)}
                          for t in ("none", "bridge-only", "stated-judgment")},
               "by_question_kind": {k: {"written": sum(r["kind"] == k for r in ins),
                                        "match": sum(r["kind"] == k and r["status"] == "match" for r in ins)}
                                    for k in ("Q1", "Q2", "Q3", "Q4")},
               "without_outside_lean": {"written": len(outside_den), "match": sum(r["inside_lean"] for r in ins)},
               "uses_bridge_matches": sum(bool(r["uses_bridge"]) and r["status"] == "match" for r in ins),
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
