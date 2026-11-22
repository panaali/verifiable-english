"""Builds the ten-sentence writer's prompt: source clause text (verbatim, by cite) and the
environment's constant names. Nothing else (no rule formula, gloss, grammar or rendered wording)."""
import json, sys
ROOT = str(__import__("pathlib").Path(__file__).resolve().parents[4] / "usecases/eligibility")
S = {"S1": "source/uksi-2025-969-made.txt", "S2": "source/wfp-print.txt", "S3": "source/uksi-2005-3360-reg2.txt"}
lines = {k: open(f"{ROOT}/{v}", encoding="utf-8").read().splitlines() for k, v in S.items()}
def L(src, *nums):
    return "\n".join(lines[src][n - 1] for n in nums)
CLAUSES = [  # (rule id, cite, line numbers in the source text file)
    ("R2.applicant", "S1 reg. 2(a)", ("S1", 60, 61)),
    ("R3.applicant", "S1 reg. 2(b)", ("S1", 60, 62)),
    ("R14.1", "S1 reg. 3(1)", ("S1", 64)),
    ("R14.2", "S1 reg. 3(2)", ("S1", 65, 66, 67, 68, 69)),
    ("R15.4", "S1 reg. 3(4)", ("S1", 73)),
    ("R9.applicant", "S1 reg. 4(2)(c)", ("S1", 84, 87)),
    ("R12.applicant", "S1 reg. 4(5) and (6)", ("S1", 90, 91, 92, 93)),
    ("R8a.applicant", "S3 reg. 2(5)", ("S3", 13)),
    ("R16a", "S2 'If your income is over £35,000'", ("S2", 138, 139)),
    ("G7", "S2:166", ("S2", 166)),
]
DEFS = [("S1 reg. 1(3), the definition of the qualifying week", ("S1",)), ("S2 (the guide)", ("S2", 38))]
qw = next(l for l in lines["S1"] if "“qualifying week”" in l)
env = json.load(open(f"{ROOT}/environment.json", encoding="utf-8"))
consts = env["vocabulary"]["constants"]
out = {"clauses": [{"n": i + 1, "rule": rid, "cite": cite, "text": L(src[0], *src[1:])} for i, (rid, cite, src) in enumerate(CLAUSES)],
       "definitions": [qw, L("S2", 38)],
       "constants": [{"name": k, "words": v.get("verbalisation")} for k, v in sorted(consts.items())]}
json.dump(out, open(sys.argv[1], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
txt = ["You will read ten short passages from UK legislation and from a GOV.UK guide about the Winter Fuel Payment.",
       "For each passage, write ONE plain English sentence that states the rule the passage makes, for one person called",
       "the applicant (the passages call this person \"P\" or \"you\").",
       "",
       "Some dates and amounts have fixed names, listed at the end. When your sentence mentions one of them, use its name",
       "exactly as listed (the words in quotes). Otherwise write the sentence as you think best. Write each sentence on its",
       "own; do not refer to the other passages.",
       "",
       "Answer with exactly ten lines and nothing else, one per passage, in this form:",
       "1. <your sentence>",
       "2. <your sentence>",
       "...",
       "",
       "Definitions from the same sources:"]
txt += ["- " + d for d in out["definitions"]] + [""]
for c in out["clauses"]:
    txt += [f"Passage {c['n']} ({c['cite']}):", c["text"], ""]
txt += ["Named dates, amounts, people and benefits (name: \"words\"):"]
txt += [f"- {c['name']}: \"{c['words']}\"" for c in out["constants"] if c["words"]]
open(sys.argv[2], "w", encoding="utf-8").write("\n".join(txt) + "\n")
