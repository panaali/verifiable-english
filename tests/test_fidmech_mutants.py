"""fid-mech-b4: the mutant record (plan 2d), its edits, the declarations of equivalents.json (Opus round 2 point 4)
and the fp-1 port (tools/fidmech/fp1.py). No Lean: records are built from fixture text."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from tools.fidmech import fp1
from tools.fidmech import mutants as M
from tools.fidmech import records as R
from tools.fidmech import structural as S

DATA = Path(__file__).resolve().parent / "data" / "fidmech"
RSP = "anthropic-rsp"


def fixture_files(directory):
    """{name: text} of a fixture directory; `x.py.txt` is read as `x.py`."""
    return {p.name[:-4] if p.name.endswith(".py.txt") else p.name: p.read_text(encoding="utf-8")
            for p in sorted(Path(directory).iterdir()) if p.is_file()}


def test_fp1_equals_uc_audits_values_on_the_frozen_inputs():
    """The port gives the inputs seat's fp-1 values (fp1.json, sha256 2a0a6dcb...) for every FSF unit at 0f6d59d441."""
    golden = json.loads((DATA / "fp1-golden.json").read_text())
    assert golden["source_sha256"] == "2a0a6dcb9e1f94ecce820bbcfe4a6deef4107435ce51417cbe4c829c0c35988b"
    files = {name: text.encode("utf-8") for name, text in fixture_files(DATA / "fp1-inputs" / "safety-framework").items()}
    got = fp1.fingerprints_of(files)
    assert len(golden["fp1"]) == 45 and got == golden["fp1"]


def test_an_edit_widens_until_its_find_occurs_once():
    old = "## a | x\nRule 1. Same line.\n## b | y\nRule 1. Same line.\n"
    new = "## a | x\nRule 1. Same line.\n## b | y\nRule 1. Other line.\n"
    edits = M.line_edits("rules.d1.ve", old, new)
    assert edits == [{"file": "rules.d1.ve", "find": "## b | y\nRule 1. Same line.\n",
                      "replace": "## b | y\nRule 1. Other line.\n", "file_sha256": M.sha256_text(old)}]
    assert M.apply_edits({"rules.d1.ve": old}, edits)["rules.d1.ve"] == new


def test_runs_whose_context_meets_merge_into_one_edit():
    old = "p\nq\nr\ns\nq\n"
    new = "P\nq\nR\ns\nq\n"
    edits = M.line_edits("f", old, new)
    assert all(old.count(e["find"]) == 1 for e in edits)
    assert M.apply_edits({"f": old}, edits)["f"] == new


def test_a_record_refuses_a_find_that_is_not_unique_a_stale_sha_and_overlapping_edits():
    files = {"rules.d1.ve": "Rule 1. A.\nRule 1. A.\nRule 1. B.\n"}
    sha = M.sha256_text(files["rules.d1.ve"])
    with pytest.raises(ValueError, match="occurs 2 times"):
        M.record(RSP, "u", "structural", "rule-drop", "rule",
                 [{"file": "rules.d1.ve", "find": "Rule 1. A.", "replace": "x", "file_sha256": sha}], files)
    with pytest.raises(ValueError, match="file_sha256"):
        M.record(RSP, "u", "structural", "rule-drop", "rule",
                 [{"file": "rules.d1.ve", "find": "B.", "replace": "x", "file_sha256": "0" * 64}], files)
    with pytest.raises(ValueError, match="overlapping"):
        M.record(RSP, "u", "structural", "rule-drop", "rule",
                 [{"file": "rules.d1.ve", "find": "1. B", "replace": "x", "file_sha256": sha},
                  {"file": "rules.d1.ve", "find": "B.\n", "replace": "y", "file_sha256": sha}], files)
    rec = M.record(RSP, "u", "structural", "rule-drop", "rule",
                   [{"file": "rules.d1.ve", "find": "B.", "replace": "x", "file_sha256": sha}], files)
    assert list(rec) == list(M.RECORD_KEYS) and rec["id"] == f"{RSP}:u:rule-drop:1" and rec["generator"] == "fidmech/1"


def test_a_wording_mutant_is_never_equivalent():
    files = {"rules.d1.ve": "Rule 1. B.\n"}
    edit = [{"file": "rules.d1.ve", "find": "B.", "replace": "x", "file_sha256": M.sha256_text(files["rules.d1.ve"])}]
    with pytest.raises(ValueError, match="never equivalent"):
        M.record(RSP, "u", "wording", "actor", "act", edit, files, equivalent="syntactic")
    assert M.record(RSP, "u", "wording", "actor", "act", edit, files)["equivalent"] is None


def test_stillborn_records_are_never_scored():
    files = {"rules.d1.ve": "Rule 1. B.\n"}
    edit = [{"file": "rules.d1.ve", "find": "B.", "replace": "x", "file_sha256": M.sha256_text(files["rules.d1.ve"])}]
    ok = M.record(RSP, "u", "structural", "rule-drop", "rule", edit, files)
    dead = M.record(RSP, "u", "structural", "flip-force", "rule", edit, files, parse="stillborn")
    assert M.scorable([ok, dead]) == [ok]


# ---- declarations ---------------------------------------------------------------------------------------------------

def case_dir(tmp_path):
    """A case directory: the structural fixture's rules and PRECEDENCE, the frozen RSP vocabulary and environment, a
    facts file, bindings.json and an empty equivalents.json."""
    case = tmp_path / RSP
    (case / "fidmech").mkdir(parents=True)
    for source in (DATA / "wording-inputs" / RSP, DATA / "structural" / RSP):  # the fixture rules win
        for name, text in fixture_files(source).items():
            (case / name).write_text(text, encoding="utf-8")
    (case / "facts.d1.ve").write_text("## T1 | always | RS0 | fixture\nT1 is listed.\n", encoding="utf-8")
    (case / "fidmech" / "bindings.json").write_text('{"tables": {"SITUATIONS": {"K2": ["a"]}}}\n', encoding="utf-8")
    (case / "fidmech" / "equivalents.json").write_text("[]\n", encoding="utf-8")
    return case


def drop_record(case):
    files = M.case_files(case)
    block = next(b for b in S.rule_blocks(files[S.RULES]) if b.id == "f12-final")
    line = block.text[:-1] + ", if this is impossible."
    return M.record(RSP, block.id, "structural", "rule-drop", "rule", M.rule_edit(files, block, line), files)


def declare(case, rec, reason="unprobed"):
    return {"id": rec["id"], "reason": reason, "binding": M.binding(rec, M.binding_inputs(case))}


def applied(case, rec, entry):
    records, report = M.apply_declarations([rec], [entry], M.binding_inputs(case))
    return records[0]["equivalent"], report


def edit_file(path, old, new):
    text = path.read_text(encoding="utf-8")
    assert text.count(old) == 1
    path.write_text(text.replace(old, new), encoding="utf-8")


def test_a_bound_declaration_applies(tmp_path):
    case = case_dir(tmp_path)
    rec = drop_record(case)
    assert applied(case, rec, declare(case, rec)) == ("declared:unprobed", {
        "applied": [rec["id"]], "stale": [], "unknown": [], "not-structural": [], "already-equivalent": []})


@pytest.mark.parametrize("change", ["fp1", "facts", "precedence", "bindings"])
def test_a_declaration_stops_applying_when_what_it_rests_on_changes(tmp_path, change):
    """fp-1 of the unit (its block), facts.d1.ve, PRECEDENCE and bindings.json each enter the binding."""
    case = case_dir(tmp_path)
    rec = drop_record(case)
    entry = declare(case, rec)
    if change == "fp1":
        edit_file(case / S.RULES, "## f12-final | RS7=final | RS0 | fixture: no guard",
                  "## f12-final | RS7=final | RS0 | fixture: no guard at all")
    elif change == "facts":
        edit_file(case / "facts.d1.ve", "T1 is listed.", "T2 is listed.")
    elif change == "precedence":
        edit_file(case / "rsp_translation.py", '("f12-final",)', '("f12-final", "f18-either")')
    else:
        edit_file(case / "fidmech" / "bindings.json", '"K2"', '"K3"')
    equivalent, report = applied(case, rec, entry)
    assert equivalent is None and report["stale"] == [rec["id"]] and not report["applied"]


def test_a_declaration_stops_applying_when_the_mutants_edits_change(tmp_path):
    case = case_dir(tmp_path)
    rec = drop_record(case)
    entry = declare(case, rec)
    other = {**rec, "edits": [{**rec["edits"][0], "replace": rec["edits"][0]["replace"].replace("impossible", "so")}]}
    assert applied(case, other, entry)[1]["stale"] == [rec["id"]]


@pytest.mark.parametrize("key", ["fp1", "facts_sha256", "precedence", "bindings_sha256"])
def test_each_binding_input_alone_changes_the_binding(tmp_path, key):
    case = case_dir(tmp_path)
    rec = drop_record(case)
    inputs = M.binding_inputs(case)
    changed = {**inputs, key: {**inputs["fp1"], rec["unit"]: "fp1:0"} if key == "fp1" else "other"}
    assert M.binding(rec, changed) != M.binding(rec, inputs)


def test_equivalents_json_and_the_commit_are_left_out_of_the_binding(tmp_path):
    """Opus round 2 point 4: a binding that held equivalents.json or the commit could never be written."""
    case = case_dir(tmp_path)
    git = lambda *a: subprocess.run(["git", "-C", str(tmp_path), *a], check=True, capture_output=True)  # noqa: E731
    git("init", "-q")
    git("-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "--allow-empty", "-m", "a")
    rec = drop_record(case)
    entry = declare(case, rec)
    (case / "fidmech" / "equivalents.json").write_text(json.dumps([entry, {**entry, "id": "x:y:z:1"}]) + "\n")
    git("add", "-A")
    git("-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-m", "b")
    assert applied(case, rec, entry)[0] == "declared:unprobed"
    assert M.load_declarations(case / "fidmech" / "equivalents.json")[0] == entry


def test_a_declaration_names_a_structural_mutant_with_no_equivalence(tmp_path):
    case = case_dir(tmp_path)
    rec = drop_record(case)
    wording = {**rec, "id": f"{RSP}:f12-final:actor:1", "class": "wording", "op": "actor"}
    syntactic = {**rec, "id": f"{RSP}:f12-final:rule-drop:2", "equivalent": "syntactic"}
    entries = [declare(case, wording), declare(case, syntactic), {**declare(case, rec), "id": "nowhere:x:y:1"}]
    records, report = M.apply_declarations([wording, syntactic], entries, M.binding_inputs(case))
    assert [r["equivalent"] for r in records] == [None, "syntactic"]
    assert report["not-structural"] == [wording["id"]] and report["already-equivalent"] == [syntactic["id"]]
    assert report["unknown"] == ["nowhere:x:y:1"] and not report["applied"]


def test_a_malformed_declaration_is_refused(tmp_path):
    path = tmp_path / "equivalents.json"
    path.write_text(json.dumps([{"id": "a", "reason": "", "binding": "0" * 64}]))
    with pytest.raises(ValueError, match="malformed"):
        M.load_declarations(path)


@pytest.mark.parametrize("document", ["anthropic-rsp", "openai-preparedness", "safety-framework"])
def test_b4_ships_no_declaration(document):
    path = Path(__file__).resolve().parents[1] / "usecases" / document / M.EQUIVALENTS
    assert M.load_declarations(path) == []


def test_the_generator_version_and_mutant_edits_enter_inputs_sha256(tmp_path):
    """Plan 2e through B3's collect_inputs: the generator version and each record's id and edits."""
    tree = tmp_path / "tree"
    case = case_dir(tree / "usecases")
    (tree / "usecases" / "pinned_sources.json").write_text('{"sources": {}}\n')
    subprocess.run(["git", "init", "-q", str(tree)], check=True)
    subprocess.run(["git", "-C", str(tree), "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q",
                    "--allow-empty", "-m", "a"], check=True)
    rec = drop_record(case)
    from types import SimpleNamespace
    as_input = lambda r: SimpleNamespace(id=r["id"], edits=r["edits"])  # noqa: E731
    inputs = R.collect_inputs(tree, RSP, generator_version=S.GENERATOR, mutants=[as_input(rec)])
    assert inputs["generator_version"] == "fidmech/1"
    assert inputs["mutants"] == [[rec["id"], M.sha256_text(R.canonical(rec["edits"]).decode())]]
    other = {**rec, "edits": [{**rec["edits"][0], "replace": "Rule 1. Other."}]}
    changed = R.collect_inputs(tree, RSP, generator_version=S.GENERATOR, mutants=[as_input(other)])
    assert R.inputs_sha256(inputs) != R.inputs_sha256(changed)


def test_a_record_turns_into_the_workers_mutant(tmp_path):
    case = case_dir(tmp_path)
    rec = drop_record(case)
    files = M.case_files(case)
    mutant = M.to_worker(rec, files)
    assert mutant.id == rec["id"] and list(mutant.edits) == [f"{RSP}/{S.RULES}"]
    assert mutant.edits[f"{RSP}/{S.RULES}"].count("if this is impossible") == 1


def test_an_unanswered_parse_is_undecided_and_unscored_and_any_other_error_propagates():
    """A CheckerUnavailable parse is listed as `undecided` (stillborn: never scored); a VE refusal is plain
    stillborn; an error that is neither (a bug) is not turned into a stillborn mutant."""
    from tools.fidmech import wording as W
    from ve.errors import CheckerUnavailable, SyntaxError as VESyntaxError
    files = {p.name[:-4] if p.name.endswith(".py.txt") else p.name: p.read_text(encoding="utf-8")
             for p in sorted((DATA / "wording-inputs" / RSP).iterdir())}
    files["rules.d1.ve"] = (DATA / "structural" / RSP / "rules.d1.ve").read_text(encoding="utf-8")
    actors = W.load_actors(Path(__file__).resolve().parents[1] / "usecases" / RSP / "fidmech" / "actors.json")

    def raising(error):
        def parse_env(text):
            raise error
        return parse_env
    records, report = M.wording_mutants(RSP, files, actors, parse_env=raising(CheckerUnavailable("no answer")))
    assert records and all(r["parse"] == "stillborn" for r in records) and M.scorable(records) == []
    assert all(s["reason"].startswith("undecided: CheckerUnavailable") for s in report["stillborn"])
    records, report = M.wording_mutants(RSP, files, actors, parse_env=raising(VESyntaxError("refused")))
    assert all(s["reason"].startswith("SyntaxError") for s in report["stillborn"]) and len(report["stillborn"]) == len(records)
    with pytest.raises(TypeError):
        M.wording_mutants(RSP, files, actors, parse_env=raising(TypeError("a bug")))
