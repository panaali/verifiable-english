"""The pilot's defaults probe (defeasible plan DF-1b "Pilot", 4.2's P-1 and P-3; df-1bb).

Asks each probe question with `ve document readings <document> --conclusion <question> --assume-no-exception` and
records every answer verbatim: P-1 on df-03's three probe documents (`docs/research/evidence/defeasible/baseline/`),
P-3 on u0073.s05 (`probe/`, one default rule with three stated exception conditions), asked where none of the three
holds and with no condition stated. Prints the pilot's `default_answer_probe` (questions, strict answers, default
answers by verdict, UNKNOWN with reasons, and each answer); every verdict in it is Lean's.

Run from the repository root: `uv run python docs/defeasible/df-1bb/probe_defaults.py [OUT.json]`.
"""
from __future__ import annotations

import contextlib
import io
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASELINE = ROOT / "docs/research/evidence/defeasible/baseline"
P1 = ("force-u0036-s05", "force-u0156-s03", "force-u0263-s04-p2")
P3 = ("none-holds", "always")


def questions():
    """(probe, set, document, question) of every probe question, as paths relative to the root."""
    out = [("P-1", s, BASELINE / f"p1-{s}.ve.md", BASELINE / f"question-{s}.json") for s in P1]
    out += [("P-3", f"force-u0073-s05/{q}", HERE / "probe/p3-force-u0073-s05.ve.md",
             HERE / f"probe/question-p3-{q}.json") for q in P3]
    return [(probe, s, d.relative_to(ROOT).as_posix(), q.relative_to(ROOT).as_posix()) for probe, s, d, q in out]


def ask(document, question):
    from ve.document import main
    argv = ["readings", document, "--conclusion", question, "--assume-no-exception"]
    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        code = main(argv)
    return ["ve", "document", *argv], code, stdout.getvalue()


def probe():
    answers, verdicts, unknown = [], {}, []
    for name, set_id, document, question in questions():
        argv, code, stdout = ask(document, question)
        out = json.loads(stdout)
        answers.append({"probe": name, "set": set_id, "argv": argv, "exit": code, "stdout": stdout})
        if out["question"] == "default":
            verdict = out["answer"]["verdict"]
            verdicts[verdict] = verdicts.get(verdict, 0) + 1
            if verdict == "UNKNOWN":
                unknown.append({"set": set_id, "reason": out["answer"]["reason"]})
    return {"questions": len(answers), "strict_answers": sum(json.loads(a["stdout"])["question"] == "strict"
                                                             for a in answers),
            "default_answers": verdicts, "unknown": unknown, "answers": answers}


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT))
    import os
    os.chdir(ROOT)
    result = json.dumps({"default_answer_probe": probe()}, ensure_ascii=False, indent=2) + "\n"
    if len(sys.argv) > 1:
        Path(sys.argv[1]).write_text(result)
    print(result, end="")
