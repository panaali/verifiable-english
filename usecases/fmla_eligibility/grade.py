"""Compare a run file with the sealed answers (sha256 checked). SAME-FAMILY. Committed BEFORE the headline run.

usage: python3 -I grade.py RUN.json <manage-agents>/reviews/spare/statute-corpus/stock/fmla-eligibility [--out GRADES.json]
Reads <dir>/sealed/answers.jsonl (sha256 must equal the seal) and <dir>/questions.jsonl (scope and the writer's tags).
Per in-scope question: match (VE's yes/no equals the sealed answer), disagree (VE answered, differently: goes to two fresh
graders; VE certain and graded wrong = a WRONG answer), refused (OPEN), unsupported, writer-ambiguous (the writer filled
"ambiguous": not correct whatever VE says, ISOLATION.md D6). Probes apart.
"Without anything computed outside Lean": a match counts only if its documents use no bridged value (run record "bridged"
vs "uses"), its case has no encoder judgement, and the writer tagged it "none".
"""
import hashlib
import json
import sys

SEALED_SHA256 = "041a59c1c8c66c77a66f5e9574ac5d08e5a722ae3267ec9c1fd372f0bc67010d"
QUESTIONS_SHA256 = "277afd75ba327630e7ee68f7bb892a6e67ae78f7ebbb4056d3622f088025570a"


def norm(v):
    return str(v).strip().lower().rstrip(".")


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
            status = "writer-ambiguous" + ("-match" if norm(v["answer"]) == norm(w["answer"]) else "-differ")
        elif norm(v["answer"]) == norm(w["answer"]):
            status = "match"
        else:
            status = "disagree"
        r = rec_of[qid]
        used_bridge = sorted(set(r.get("uses", {}).get(qid, [])) & set(r.get("bridged", [])))
        judged = bool(r.get("encoder_judgement"))
        inside = status == "match" and not used_bridge and not judged and m["tag"] == "none"
        rows.append({"qid": qid, **m, "status": status, "ve": v["answer"], "writer": w.get("answer"),
                     "ambiguous": w.get("ambiguous"), "uses_bridge": used_bridge, "encoder_judgement": judged,
                     "inside_lean": inside})
    ins = [r for r in rows if r["scope"] == "in"]
    plain = [r for r in ins if r["tag"] == "none"]
    count = lambda rs, st: sum(r["status"] == st for r in rs)  # noqa: E731
    outside_den = [r for r in ins if not (r["uses_bridge"] or r["encoder_judgement"] or r["tag"] != "none")]
    summary = {"in_scope_written": len(ins), "match": count(ins, "match"), "disagree": count(ins, "disagree"),
               "refused": count(ins, "refused"), "unsupported": count(ins, "unsupported"),
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
                                    for k in ("Q1", "Q2", "Q3")},
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
