"""The 120 pinned rule blocks: Lean's node against Python's recorded node (en-e3-norm EN-1; spec english-lean-s6 f22).

`tests/data/norm-blocks/rsp.jsonl` (76) and `fsf.jsonl` (44) hold each block's id and text, the commit it was read
at and Python's `norm` object (`docs/english-lean/en-s6/capture_blocks.py`). Lean reads each block with
`VE.EnglishGrammar.Norm.readNorm` in its use case's environment, with the lexicon Python selects, and gives its node
through `toNodes` (the one decoder, `decodeNorm`); both nodes are compared in Lean. A block headed by `should` is
EN-4's and has no derivation (f4). A block Lean reads differently is listed in `DIFFERENT` with both nodes printed,
never skipped. f21 reads the constitution's u0125.s04.p2 block in its route case's environment.
"""
from __future__ import annotations

from functools import cache
import importlib.util
from itertools import permutations
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

import pytest

from tests.lean_build import lean_build
from tests.subprocesses import HANG_TIMEOUT
from tests.test_norms import environment, permission
from ve.english_grammar import export
from ve.environment import Environment
from ve.norm_english import _words, parse_english

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "tests/data/norm-blocks"
CASES = {"rsp": ("anthropic-rsp", "rsp_translation", 76), "fsf": ("safety-framework", "translation", 44)}
W1 = {"name", "predicate", "sign", "guard", "unless", "over"}
SOFT = W1 | {"mode", "exception"}
# Blocks whose Lean node differs from Python's, with the reason (EN-2's delta); none today.
DIFFERENT: dict[str, str] = {}
F21 = ("Rule 1. Every instance of Claude must not directly deny being Claude.",
       [{"name": "rule-1", "predicate": "denial_of_being_claude_permitted", "sign": False, "guard": ["top"],
         "unless": [], "over": []}])


def blocks(name: str) -> list[dict]:
    return [json.loads(line) for line in (DATA / f"{name}.jsonl").read_text().splitlines()]


def source_blocks(case: str) -> list[tuple[str, str]]:
    lines = (ROOT / "usecases" / case / "rules.d1.ve").read_text().splitlines()
    return [(re.match(r"## ([a-z0-9-]+) \|", h)[1], t) for h, t in zip(lines[::2], lines[1::2])]


def case_of(env) -> dict:
    """The reader's inputs: the environment and the lexicon Python selects for it."""
    return {"environment": env.to_dict(), "lexicon": export(_words(env))}


@cache
def use_case(name: str) -> dict:
    """The use case's environment, by its own loader (which imports its siblings), as the capture read it."""
    case, module, _ = CASES[name]
    folder = str(ROOT / "usecases" / case)
    sys.path.insert(0, folder)
    try:
        spec = importlib.util.spec_from_file_location(f"pinned_{module}", f"{folder}/{module}.py")
        loader = sys.modules[spec.name] = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(loader)
        return case_of(loader.environment())
    finally:
        sys.path.remove(folder)


def constitution() -> dict:
    """f21's environment: the route case's declaration of `denial_of_being_claude_permitted` and its sort, in a W1
    environment (`norms@0`; its `unspecified` default is `norm-defaults@0`'s and no reading reads a default)."""
    for line in (ROOT / "tests/data/route-cases.jsonl").read_text().splitlines():
        _, case = json.loads(line)
        environment = case.get("environment")
        predicates = environment.get("vocabulary", {}).get("predicates", {}) if type(environment) is dict else {}
        if "denial_of_being_claude_permitted" in predicates:
            predicate = predicates["denial_of_being_claude_permitted"]
            predicate = {**predicate, "regulated": {**predicate["regulated"], "default": "deny"}}
            sorts = {s: environment["vocabulary"]["sorts"][s] for s in predicate["arguments"]}
            return case_of(Environment({
                "language": environment["language"], "profiles": ["norms@0", "relational-fol@0"],
                "spec_revision": environment["spec_revision"],
                "vocabulary": {"sorts": sorts, "predicates": {"denial_of_being_claude_permitted": predicate},
                               "constants": {}}}))
    raise AssertionError("no route case declares denial_of_being_claude_permitted")


@pytest.mark.parametrize("name", CASES)
def test_every_pinned_block_has_its_python_node(name):
    case, _, count = CASES[name]
    rows = blocks(name)
    assert len(rows) == count
    assert [(r["id"], r["text"]) for r in rows] == source_blocks(case)
    assert len({r["commit"] for r in rows}) == 1
    for r in rows:
        assert set(r) == {"commit", "id", "text", "node"}, r["id"]
        [node] = r["node"]
        soft = " should " in r["text"]
        assert set(node) == (SOFT if soft else W1), r["id"]
        assert node["name"] == "rule-1" and node["over"] == [] and type(node["sign"]) is bool, r["id"]
        assert node.get("mode", "strict") == ("default" if soft else "strict"), r["id"]


@pytest.fixture(scope="module")
def lake():
    found = shutil.which("lake")
    if found is None:
        pytest.skip("lake is not available")
    lean_build("VE")
    return found


def lean_literal(text: str) -> str:
    """A Lean string literal of `text` (JSON's escapes are Lean's)."""
    return json.dumps(text)


def readings(lake: str, tmp_path: Path, groups: list[tuple[dict, list[tuple[str, str, list]]]]) -> dict[str, str]:
    """Lean's verdict on each block: `same`, `differs` with both nodes, or where the reader stopped."""
    lines = ["import VE.EnglishGrammar.Norm.Examples", "import VE.EnglishGrammar.Run",
             "open Lean VE.EnglishGrammar VE.EnglishGrammar.Norm VE.EnglishGrammar.Norm.Examples",
             "def flat {α : Type} [Repr α] (x : α) : String := (reprStr x).replace \"\\n\" \" \"",
             "def verdict (k : Run.Case) (text : String) (node : String) : String :=",
             "  let o := readNorm k.E k.O k.L workBudget text",
             "  match nodes o, python node with",
             "  | .ok a, .ok b => if a != b then s!\"differs lean={flat a} python={flat b}\"",
             "      else if authored k.E o then \"same\" else \"same, not authored\"",
             "  | .ok a, .error _ => s!\"differs lean={flat a}\"",
             "  | .error e, _ => e.replace \"\\n\" \" \""]
    for k, (case, rows) in enumerate(groups):
        lines.append(f"#eval show IO Unit from do")
        lines.append(f"  let k ← IO.ofExcept (do Run.decodeCase (← Json.parse {lean_literal(json.dumps(case))}))")
        for ident, text, node in rows:
            lines.append(f"  IO.println (\"{ident}|\" ++ verdict k {lean_literal(text)} {lean_literal(json.dumps(node))})")
    source = tmp_path / "Blocks.lean"
    source.write_text("\n".join(lines) + "\n")
    run = subprocess.run([lake, "env", "lean", str(source)], cwd=ROOT / "lean", capture_output=True, text=True,
                         timeout=HANG_TIMEOUT)
    assert run.returncode == 0, run.stdout[-2000:] + run.stderr[-2000:]
    out = dict(line.split("|", 1) for line in run.stdout.splitlines())
    assert len(out) == sum(len(rows) for _, rows in groups)
    return out


def test_lean_reads_each_pinned_block_as_python(lake, tmp_path):
    groups = [(use_case(name), [(r["id"], r["text"], r["node"]) for r in blocks(name)]) for name in CASES]
    groups.append((constitution(), [("f21", *F21)]))
    out = readings(lake, tmp_path, groups)
    soft = {r["id"] for name in CASES for r in blocks(name) if " should " in r["text"]}
    assert len(out) == 121 and len(soft) == 17
    assert {i: v for i, v in out.items() if i in soft and v != "stopped 1 noDerivation"} == {}
    different = {i: v for i, v in out.items() if i not in soft and v != "same"}
    assert set(different) == set(DIFFERENT), "\n".join(f"{i}: {v}" for i, v in different.items())
    assert sum(v == "same" for v in out.values()) == 104 - len(DIFFERENT)


def header(targets: tuple[int, ...]) -> str:
    if len(targets) < 2:
        return f" (exception to rule {targets[0]})" if targets else ""
    return f" (exception to rules {', '.join(map(str, targets[:-1]))} and {targets[-1]})"


def over_text(order: tuple[int, ...], split: int, lines_first: bool) -> str:
    """Rule 5 over `order`: the first `split` targets in its header, the rest as precedence lines."""
    rules = [f"Rule {n}. Every act must not be done." for n in range(1, 5)]
    rules.append(f"Rule 5{header(order[:split])}. Every act may be done.")
    lines = [f"Rule 5 takes precedence over rule {n}." for n in order[split:]]
    return "\n".join(lines + rules if lines_first else rules + lines)


def test_lean_orders_over_as_python(lake, tmp_path):
    """Every pinned node has `over = []`, so `over`'s order is compared here, with Python's node read live: f7, f8, and
    rule 5 over every order of four targets, at every split between its header and its precedence lines (those lines
    before the rules at an odd split, after them at an even one)."""
    env = environment({"permitted": permission()})
    f7 = ("Rule 1. Every act must not be done.\nRule 2. Every act may be done.\n"
          "Rule 2 takes precedence over rule 1.")
    f8 = ("Rule 1. Every act must not be done.\nRule 2. Every act must not be done.\n"
          "Rule 3 (exception to rules 1 and 2). Every act may be done.")
    texts = {"f7": f7, "f8": f8} | {
        f"{''.join(map(str, order))}-{split}": over_text(order, split, lines_first=split % 2 == 1)
        for order in permutations(range(1, 5)) for split in range(5)}
    nodes = {i: [r.to_dict()["norm"] for r in parse_english(env, text).rules] for i, text in texts.items()}
    assert {tuple(n[-1]["over"]) for i, n in nodes.items() if i not in ("f7", "f8")} == {
        tuple(f"rule-{n}" for n in order) for order in permutations(range(1, 5))}
    swapped = [*nodes["1234-2"][:4], {**nodes["1234-2"][4], "over": ["rule-3", "rule-4", "rule-1", "rule-2"]}]
    rows = [(i, text, nodes[i]) for i, text in texts.items()] + [("swapped", texts["1234-2"], swapped)]
    out = readings(lake, tmp_path, [(case_of(env), rows[k:k + 50]) for k in range(0, len(rows), 50)])
    assert out.pop("swapped").startswith("differs")
    assert {i: v for i, v in out.items() if v != "same"} == {}


def test_the_comparison_fails_on_a_changed_node(lake, tmp_path):
    rows = blocks("rsp")[:2]
    [plain, retyped] = [dict(r["node"][0]) for r in rows]
    retyped["sign"] = not retyped["sign"]
    out = readings(lake, tmp_path, [(use_case("rsp"), [("kept", rows[0]["text"], [plain]),
                                                       ("changed", rows[1]["text"], [retyped]),
                                                       ("empty", rows[0]["text"], [])])])
    assert out["kept"] == "same"
    assert out["changed"].startswith("differs") and out["empty"].startswith("differs")




def answers(lake: str, tmp_path: Path, groups: list[tuple[dict, list[tuple[str, str]]]], *, whole: bool) -> dict:
    """`english.statement`'s row for each `(id, source)` of each case, by id: the whole mode
    (`Norm.Run.statementCaseReported`, en-e3-norm 2.3) when `whole`, else its answer on the case decoded once per
    chunk (`Norm.Run.answer`), since the mode decodes the environment on every request."""
    lines = ["import VE.EnglishGrammar.Norm.Run", "open Lean VE.EnglishGrammar.Norm"]
    for case, rows in groups:
        for k in range(0, len(rows), 20):
            lines += ["#eval show IO Unit from do",
                      f"  let j ← IO.ofExcept (Json.parse {lean_literal(json.dumps({**case, 'kind': 'blocks'}))})",
                      "  let c ← IO.ofExcept (VE.EnglishGrammar.Run.decodeCase j)" if not whole else ""]
            lines += [f"  IO.println (Run.statementCaseReported ((j.setObjVal! \"id\" {lean_literal(i)}).setObjVal! "
                      f"\"source\" {lean_literal(t)})).compress" if whole else
                      f"  IO.println (Run.answer {lean_literal(i)} c {lean_literal(t)}).compress" for i, t in rows[k:k + 20]]
    source = tmp_path / "Mode.lean"
    source.write_text("\n".join(line for line in lines if line) + "\n")
    run = subprocess.run([lake, "env", "lean", str(source)], cwd=ROOT / "lean", capture_output=True, text=True,
                         timeout=HANG_TIMEOUT)
    assert run.returncode == 0, run.stdout[-2000:] + run.stderr[-2000:]
    out = {row["id"]: row for row in map(json.loads, run.stdout.splitlines())}
    assert len(out) == sum(len(rows) for _, rows in groups)
    return out


def test_each_pinned_block_through_the_mode(lake, tmp_path):
    """The 120 pinned blocks and f21 through `english.statement` kind `blocks` (EN-2; en-e3a REPORT, R-pinned): a block
    headed by `should` is `none` at its rule sentence; every other block is `one`, with Python's node and the block's
    byte span. Through the whole mode: a block of each kind, and a request whose lexicon was selected for another
    environment, which `decodeCase` refuses (R-stale)."""
    texts = {r["id"]: r["text"] for name in CASES for r in blocks(name)} | {"f21": F21[0]}
    nodes = {r["id"]: r["node"] for name in CASES for r in blocks(name)} | {"f21": F21[1]}
    groups = [(use_case(name), [(r["id"], r["text"]) for r in blocks(name)]) for name in CASES]
    out = answers(lake, tmp_path, [*groups, (constitution(), [("f21", F21[0])])], whole=False)
    soft = next(i for i in texts if " should " in texts[i])
    whole = answers(lake, tmp_path, [(use_case("rsp"), [("rows-cond", texts["rows-cond"]), (soft, texts[soft])]),
                                     ({**use_case("rsp"), "lexicon": use_case("fsf")["lexicon"]}, [("stale", F21[0])])],
                    whole=True)
    assert whole.pop("stale")["status"] == "error"
    assert whole == {i: out[i] for i in whole}
    for ident, row in out.items():
        result = row["result"]
        if " should " in texts[ident]:
            assert (result["status"], result["code"], result["sentence"]) == ("none", "NoDerivation", 1), ident
            continue
        assert result["status"] == "one", (ident, result)
        [statement] = result["statements"]
        assert [statement["node"]["norm"]] == nodes[ident], ident
        assert statement["span"] == [0, len(texts[ident].encode())], ident
    statuses = [row["result"]["status"] for row in out.values()]
    assert (len(out), statuses.count("one"), statuses.count("none")) == (121, 104, 17)
