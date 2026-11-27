"""Compare a run file with the sealed answers (sha256 checked). CROSS-FAMILY questions (Codex writer). Committed BEFORE the
headline run.

usage: python3 -I grade.py RUN.json <manage-agents>/reviews/spare/statute-corpus/batch4/ftr-per-diem [--out GRADES.json]
Reads <dir>/sealed/answers.jsonl (sha256 must equal the seal) and <dir>/questions.jsonl (scope and the writer's tags).
Per in-scope question: match (VE's answer equals the sealed answer after norm(): Q1 / Q4 yes / no; Q2 an amount compared
as a decimal; Q3 a share compared as a decimal ("none" = 0) or a location by its first name word, a leading "the" dropped),
disagree (VE
answered, differently: goes to two fresh graders; VE certain and graded wrong = a WRONG answer), refused (OPEN),
unsupported, writer-ambiguous (the writer filled "ambiguous": not correct whatever VE says). Probes apart.
"Without anything computed outside Lean": a question leaves the denominator if its own sub-case carries an encoder
judgement, the writer tagged it other than "none", its sub-case states a stated judgment (translation.STATED_JUDGMENT; run
file subs[].uses_stated_judgment), or VE's answer documents use a bridged fact (none: this translation has no bridge); a
refused question stays in the denominator (not correct).
"""
import hashlib
import json
import re
import sys
from decimal import Decimal, InvalidOperation

SEALED_SHA256 = "2b60aef5e89158b5080a54ea2f0b3ab4a253cc8b8fd1d9dd21846af5d433c1f8"
QUESTIONS_SHA256 = "194e8358093348c26744d8a8917b9e3a7d21466ab9d974ce7dc00bfb238cb98c"
DATE = re.compile(r"\d{4}-\d{2}-\d{2}(?:T\d{2}:\d{2})?")


def norm(a, kind):
    """-> a comparable value: 'yes' / 'no' / a date text / a Decimal / a location word / the lower-cased text."""
    if kind == "Q3":
        for v in (a.get("value"), a.get("answer")):
            if v is None:
                continue
            t = " ".join(str(v).strip().lower().split())
            m = re.search(r"-?\d+(?:\.\d+)?", t)
            if m:
                return Decimal(m[0])
            if t.startswith("none") or t.startswith("no per diem"):
                return Decimal(0)
            t = t[4:] if t.startswith("the ") else t
            m = re.match(r"[a-z]+", t)
            if m:
                return m[0]
    if kind == "Q2":
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
                                    for k in ("Q1", "Q2", "Q3", "Q4")},
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
