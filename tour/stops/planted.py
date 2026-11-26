"""Tour stop 9: a planted mistake in a translation, caught by an independent check against the source.
Runs from branch after-release (the GitLab relocation translation) until it reaches main.

The translation of GitLab's relocation policy (usecases/gitlab_relocation) is run on one case twice: as written, and
with one planted mistake (its MUTANTS["M3"]: a stay's days counted without the last day). Both runs are compared with
the answers a separate question writer wrote from the policy's own text before the translation was run
(tour/data/relocation-R009-sealed.jsonl: the case's rows of that writer's sealed answer file, whose SHA-256 is
SEALED_SHA256). This stop runs the translation's rules only, without Lean: Lean checks that each answer follows from
the rules it is given, so it cannot tell that a rule says something the policy does not; the outside answers can.
Run from the after-release checkout: python tour/stops/planted.py (tour/stops/09-planted-mistake.sh does this).
"""
import json
from pathlib import Path
import sys

TOUR = Path(__file__).resolve().parents[1]
CASE, MUTANT = "R009", "M3"
SEALED_SHA256 = "676029e9c450294154812a0169711ad991b2e40bc58dd8460673fdbb4b32499e"


def answers(run, case, mutant=None):
    out = {}
    for sub in case["subs"]:
        out.update(run.run_sub(sub, mutant)[0])
    return {qid: a["answer"] for qid, a in sorted(out.items())}


def main():
    sys.path.insert(0, str(Path.cwd() / "usecases" / "gitlab_relocation"))
    sys.setrecursionlimit(200000)
    import cases
    import run
    case = next(c for c in cases.CASES if c["id"] == CASE)
    questions = {q["qid"]: q["text"] for line in open("usecases/gitlab_relocation/questions-enc.jsonl", encoding="utf-8")
                 if line.strip() and json.loads(line)["id"] == CASE for q in json.loads(line)["questions"]}
    sealed = {a["qid"]: a["answer"] for a in map(json.loads, open(TOUR / "data" / "relocation-R009-sealed.jsonl"))}
    print("The case:", next(json.loads(line)["facts"] for line in open("usecases/gitlab_relocation/questions-enc.jsonl",
                                                                       encoding="utf-8")
                            if line.strip() and json.loads(line)["id"] == CASE).split(" Spain is outside")[0])
    print("The planted mistake:", run.T.MUTANTS[MUTANT][0])
    as_written, planted = answers(run, case), answers(run, case, MUTANT)
    caught = 0
    for qid in sorted(questions):
        print()
        print("Question:", questions[qid])
        print("  answer written from the policy alone, before the translation ran:", sealed[qid])
        print("  the translation as written:", as_written[qid], "(agrees)" if as_written[qid] == sealed[qid] else "(DISAGREES)")
        flag = "(agrees)" if planted[qid] == sealed[qid] else "(DISAGREES: the planted mistake is caught)"
        caught += planted[qid] != sealed[qid]
        print("  the translation with the planted mistake:", planted[qid], flag)
    print()
    print(f"Caught on {caught} of {len(questions)} questions.")


if __name__ == "__main__":
    main()
