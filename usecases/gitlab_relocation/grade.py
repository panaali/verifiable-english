"""Compare a run file with the sealed answers (sha256 checked). CROSS-FAMILY questions (Codex writer). Copied from
usecases/gitlab_expenses/grade.py (batch 4); changed: the seals, Q2 = a number of days or a date, Q3 = WHICH CONDITION fails
(see below), and VE's refusal by a declared limit ("refuse" form) shown as refused. Written by the encoder
(dri-statute-corpus-gitlab-relocation-cw-1125) AFTER cases.py and BEFORE the sealed answers were opened; committed before the
headline run.

usage: python3 -I grade.py RUN.json <manage-agents>/reviews/spare/statute-corpus/batch5/gitlab-relocation [--out GRADES.json]
Q3 (which condition the request fails): VE's answer is the "; "-list of translation.CONDITIONS labels it fails, or "none".
It is a match only when VE says "none" and the sealed answer (answer, else value) starts with "none" / "no condition" /
"no policy condition"; every other answered Q3 has status "compare" (free text on the writer's side): it goes to the two fresh
graders like a disagreement and counts correct only if both side with VE (a VE answer both reject = a WRONG answer).
Reads <dir>/sealed/answers.jsonl (sha256 must equal the seal) and <dir>/questions.jsonl (scope and the writer's tags).
Per in-scope question: match (VE's answer equals the sealed answer after norm(): yes / no; an amount or a number of days
compared as a decimal; a date (YYYY-MM-DD) or a date and time (YYYY-MM-DDTHH:MM) compared as text), disagree (VE
answered, differently: goes to two fresh graders; VE certain and graded wrong = a WRONG answer), refused (OPEN),
unsupported, writer-ambiguous (the writer filled "ambiguous": not correct whatever VE says). Probes apart.
"Without anything computed outside Lean": a question leaves the denominator if its own sub-case carries an encoder
judgement, the writer tagged it other than "none", its sub-case states a stated judgment (translation.STATED_JUDGMENT; run
file subs[].uses_stated_judgment), or VE's answer documents use a bridged fact (unit 33: the first anniversary, bridge/bridge.py); a
refused question stays in the denominator (not correct).
"""
import hashlib
import json
import re
import sys
from decimal import Decimal, InvalidOperation

SEALED_SHA256 = "676029e9c450294154812a0169711ad991b2e40bc58dd8460673fdbb4b32499e"
QUESTIONS_SHA256 = "7cedaa327713f371bc02832ea5c05b3298c2abba2a019d08d7de14411358b81b"
DATE = re.compile(r"\d{4}-\d{2}-\d{2}(?:T\d{2}:\d{2})?")


def norm(a, kind):
    """-> a comparable value: 'yes' / 'no' / a date text / a Decimal / the lower-cased text."""
    if kind == "Q3":
        t = " ".join(str(a.get("value") if a.get("answer") == "CONDITIONS" else a.get("answer") or a.get("value")).lower().split())
        return "none" if re.match(r"\W*(none|no condition|no policy condition)\b", t) else ("q3:" + t)
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
        elif same and not (m["kind"] == "Q3" and norm(v, "Q3") != "none"):
            status = "match"
        elif m["kind"] == "Q3":
            status = "compare"
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
               "compare": count(ins, "compare"), "compare_rows": [r["qid"] for r in ins if r["status"] == "compare"],
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
