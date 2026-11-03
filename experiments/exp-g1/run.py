#!/usr/bin/env python3
"""Compile ExpG1.lean as is and under each mutant; write the saved evidence (usage: python3 experiments/exp-g1/run.py)."""
import json, os, re, subprocess, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "experiments/exp-g1/ExpG1.lean"
OUT = ROOT / "docs/profile-composition/exp-g1"
ENV = {**os.environ, "PATH": f"{Path.home()}/.elan/bin:{os.environ['PATH']}"}
ATOM = ".unary attBelieves (.var 0)"
COND = f"def mixedCondition : VE.Formula := {ATOM}"
BRIDGE = 'def bridgePremise : VE.Formula := .all "user" (.implies (.unary attKnows (.var 0)) (.unary attBelieves (.var 0)))'
PREMISE = 'def mixedPremise : VE.Formula := .all "agent" (.all "user" (.implies mixedCondition mixedGuard))'
KNOWS_GUARD = "(.implies (.unary attKnows (.var 0)) (.binary guardName (.var 1) (.var 0)))"
# name, what it plants, old text, new text, the declaration that must fail
MUTANTS = [
    ("vacuous-never", "the condition mentions the atom and never holds", COND, f"def mixedCondition : VE.Formula := .and ({ATOM}) .bottom", "#guard nonVacuous"),
    ("vacuous-always", "the condition mentions the atom and always holds", COND, f"def mixedCondition : VE.Formula := .or ({ATOM}) (.not ({ATOM}))", "#guard nonVacuous"),
    ("same-pack-mention", "weighing declares the atom itself, so no cross-pack mention", '[(guardName, ["agent", "user"])], []', '[(guardName, ["agent", "user"]), (attBelieves, ["user"])], []', "#guard (preds mixedPremise)"),
    ("bridge-silent", "the bridge says nothing, so the two packs together no longer entail the conclusion", BRIDGE, "def bridgePremise : VE.Formula := .top", "#guard certOK uV (fullEnvX uV mixedV) mixedV"),
    ("attitudes-alone-entails", "the bridge gives the guard itself, so attitudes alone entails the conclusion", BRIDGE, f'def bridgePremise : VE.Formula := .all "agent" (.all "user" {KNOWS_GUARD})', "theorem single_pack_refuted"),
    ("weighing-alone-entails", "weighing's premise also gives the guard from knows, so weighing alone entails the conclusion", PREMISE, f'def mixedPremise : VE.Formula := .all "agent" (.all "user" (.and (.implies mixedCondition mixedGuard) {KNOWS_GUARD}))', "theorem single_pack_refuted"),
    ("review-probe-F1", "the review's probe: weighing alone is the conclusion itself", "[weighingC]", '[{ weighingC with labelled := [("w", mixedφ)] }]', "theorem single_pack_refuted"),
    ("trace-index", "the trace expands the wrong premise", '.expand ia (some "w:1")', '.expand iw (some "w:1")', "#guard certOK uV (fullEnvX uV mixedV) mixedV"),
    ("dup-same-arity", "the duplicate name has one signature, so the order does not matter", '(dupName, ["agent", "agent"])', '(dupName, ["agent"])', "theorem dup_order_matters"),
    ("frame-undeclared", "the readings frame does not declare the names", "fun n => match namesG.lookup n with | some s => some s | none => E₀.predicates n", "fun n => E₀.predicates n", "theorem mixedC_packs_transfer"),
    ("base-off-reading", "the Transfers base spells no reading", 'if p == "ve__bit__1__0" then [["e"]] else if p == ex₂', 'if p == "ve__bit__1__0" then [] else if p == ex₂', "#guard [(false, false)"),
]
DECL = re.compile(r"^(theorem \S+|#guard .*|def \S+)")


def compile_lean(path: Path) -> tuple[int, str]:
    r = subprocess.run(["lake", "env", "lean", str(path)], cwd=ROOT / "lean", env=ENV, capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def failing_decls(text: str, output: str) -> list[str]:
    lines, seen = text.splitlines(), []
    for m in re.finditer(r"^\S*ExpG1\.lean:(\d+):\d+: error", output, re.M):
        decl = next((d.group(0) for i in range(int(m.group(1)) - 1, -1, -1) if (d := DECL.match(lines[i]))), "?")
        if decl not in seen:
            seen.append(decl)
    return seen


def mutant(source: str, name: str) -> str:
    """`source` with mutant `name` planted; its old text must occur exactly once."""
    _, _, old, new, _ = next(m for m in MUTANTS if m[0] == name)
    assert source.count(old) == 1, name
    return source.replace(old, new)


def verdict(mutated: str, rc: int, output: str, test: str) -> tuple[bool, list[str]]:
    """Caught: the mutant does not compile and `test` is among the declarations that fail."""
    failing = failing_decls(mutated, output)
    return rc != 0 and any(f.startswith(test) for f in failing), failing


def main() -> None:
    rc, output = compile_lean(SRC)
    (OUT / "lean-run.txt").write_text(f"$ cd lean && PATH=~/.elan/bin:$PATH lake env lean ../experiments/exp-g1/ExpG1.lean\nrc={rc}\n{output}")
    assert rc == 0, output
    source, rows = SRC.read_text(), []
    for name, plants, old, new, test in MUTANTS:
        mutated = mutant(source, name)
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "ExpG1.lean"
            path.write_text(mutated)
            mrc, mout = compile_lean(path)
        caught, failing = verdict(mutated, mrc, mout, test)
        rows.append({"name": name, "plants": plants, "file": "experiments/exp-g1/ExpG1.lean", "test": test, "rc": mrc, "caught": caught, "failing": [f[:70] for f in failing[:4]]})
    (OUT / "mutants.json").write_text("[\n" + ",\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n]\n")
    assert all(r["caught"] for r in rows), rows


if __name__ == "__main__":
    main()
