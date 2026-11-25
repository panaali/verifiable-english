"""Compare a run file with the sealed answers (sha256 checked). Committed BEFORE the headline run (and before this file
first read sealed/answers.jsonl). Copied from usecases/posthog_leave/grade.py; the comparison forms are this text's.

usage: python3 -I grade.py RUN.json <manage-agents>/reviews/spare/statute-corpus/batch4/pensions-auto-enrolment [--out G.json]
Reads <dir>/sealed/answers.jsonl (sha256 must equal the seal) and <dir>/questions.jsonl (scope, kind and the writer's tags).
Per in-scope question: match (VE's answer equals the sealed one: Q1 yes/no; Q2 the amount as a decimal (pounds, "£" and
thousands commas dropped); Q3 the list of failed conditions in the brief's order, "; "-separated, case and spacing
ignored, or "none"; Q4 the date YYYY-MM-DD, or "none in the window" (value null)), disagree (VE answered, differently: two
fresh graders; VE certain and graded wrong = a WRONG answer), refused (OPEN), unsupported, writer-ambiguous (the writer
filled "ambiguous": not correct whatever VE says). Probes apart.
"Without anything computed outside Lean": a match counts only if its documents use no bridged value (run record "bridged"
vs "uses": ages, prescribed-period first days, window days), its case has no encoder judgement, and the writer tagged it
"none"; the denominator drops questions that lean on any of these (as posthog_leave/grade.py).
"Excluding table rows": the text has no table: equal to the headline.
"""
import hashlib
import json
import re
import sys
from decimal import Decimal, InvalidOperation

SEALED_SHA256 = "197e498bbaaddea73adda27c7eb6dac443a45df4d94b2e7ca09f903bd3b5e546"
QUESTIONS_SHA256 = "6a0d471ffd395e11e4dca42e5c7b8c7db309624452539db6dda9c120fd18d398"
TABLE = set()


def norm(a, kind):
    ans = str(a.get("answer", ""))
    if kind == "Q1":
        m = re.match(r"\s*(yes|no)\b", ans.lower())
        return m[1] if m else " ".join(ans.lower().split())
    v = a.get("value")
    if kind == "Q4":
        if v is None or "none in the window" in ans.lower():
            return "none in the window" if (v is None and "none" in ans.lower()) or "none in the window" in ans.lower() \
                else " ".join(ans.lower().split())
        return str(v).strip()
    if v is None:
        v = ans
    if kind == "Q2":
        t = str(v).replace("£", "").replace(",", "").strip()
        try:
            return Decimal(t)
        except InvalidOperation:
            return " ".join(str(v).lower().split())
    if kind == "Q3":
        parts = [" ".join(p.lower().split()).rstrip(".") for p in str(v).split(";")]
        return tuple(p for p in parts if p)
    return " ".join(str(v).lower().split())


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
            meta[x["qid"]] = {"scope": c["scope"], "kind": x["kind"], "tag": x["tag"], "covers": x.get("covers", [])}
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
            status = "writer-ambiguous" + ("-match" if norm(v, m["kind"]) == norm(w, m["kind"]) else "-differ")
        elif norm(v, m["kind"]) == norm(w, m["kind"]):
            status = "match"
        else:
            status = "disagree"
        r = rec_of[qid]
        used_bridge = sorted(set(r.get("uses", {}).get(qid, [])) & set(r.get("bridged", [])))
        judged = bool(r.get("encoder_judgement"))
        inside = status == "match" and not used_bridge and not judged and m["tag"] == "none"
        table_only = bool(m["covers"]) and set(m["covers"]) <= TABLE | {"40"} and bool(set(m["covers"]) & TABLE)
        rows.append({"qid": qid, **m, "status": status, "ve": v.get("value", v["answer"]), "writer": w.get("answer"),
                     "writer_value": w.get("value"), "ambiguous": w.get("ambiguous"), "uses_bridge": used_bridge,
                     "encoder_judgement": judged, "inside_lean": inside, "table_only": table_only})
    ins = [r for r in rows if r["scope"] == "in"]
    count = lambda rs, st: sum(r["status"] == st for r in rs)  # noqa: E731
    outside_den = [r for r in ins if not (r["uses_bridge"] or r["encoder_judgement"] or r["tag"] != "none")]
    notab = [r for r in ins if not r["table_only"]]
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
               "excluding_table_rows": {"written": len(notab), "match": count(notab, "match")},
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
