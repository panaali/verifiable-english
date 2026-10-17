"""Batch 16f: a document with `senses` is decided by Lean's `document` mode, which composes the senses route.

The seven senses documents of the 16c residue ledger (`tests/data/b16f-senses/*.senses.md`, named so that the
wrapper's seed corpus, which reads every `*.ve.md`, does not take them; copied from
`pilot/cc-20261008T0600Z:usecases/claude-constitution-pilot/run-20261008T0600Z/probes/senses-documents/` with the pack
beside them) are over a frozen `ve.core@0` envelope. Python reads the pack files beside a document and sends their
texts (`packs`); Lean reads the English fences with the senses route (`Service.Document.sensesLayer`) and every unit
in its projected environment. Loaded in place, four are valid and three are genuinely invalid (lf-16f review F2: the
batch's measurement wrote each document alone, without its pack, and listed all seven as a missing file)."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import shutil
from unittest.mock import patch

import pytest

from tools.lean_first_diff import outcome
from ve import document as D
from ve.backends import relay
from ve.errors import CheckerUnavailable, VEError

DATA = Path(__file__).parent / "data" / "b16f-senses"
VALID = ["a_front_matter_default", "c_written_definition_line", "d_parenthetical_switch",
         "e_the_rejected_sense_negated"]
# A senses refusal carries the route's diagnostic object (`{"unit", "code"}`, or the refused reading), which the mode's
# error row cannot hold: these two genuinely invalid documents keep the retained path.
REFUSED = ["b_no_choice_made", "f_two_words_one_default"]
MODERN = {"language": "ve.core@0.2", "profiles": ["relational-fol@0"], "spec_revision": "ve-v0.2-expand2-2026-09-25"}


def _parts(name: str) -> tuple[dict, str]:
    text = (DATA / f"{name}.senses.md").read_text()
    end = text.index("\n---\n", 4)
    return json.loads(text[4:end]), text[end + 5:]


def _write(directory: Path, front: dict, body: str, pack: bytes | None = None) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    if pack is None:
        shutil.copy(DATA / "pack.json", directory / "pack.json")
    elif pack:
        (directory / "pack.json").write_bytes(pack)
    path = directory / "document.ve.md"
    path.write_text("---\n" + json.dumps(front) + "\n---\n" + body)
    return path


def _modern(front: dict) -> dict:
    """The same document over a `ve.core@0.2` envelope."""
    front = deepcopy(front)
    environment = front["environment"]
    front["environment"] = {**MODERN, "vocabulary": environment["vocabulary"]}
    return front


def _public(path: Path):
    """(Lean decides, the public check and render on the Lean path, the same on the retained path)."""
    raw = path.read_bytes()
    try:
        decided = D._lean_answer(raw, True, path.parent) is not None
    except VEError:
        decided = True
    new = [outcome(lambda: D.check_document(path)), outcome(lambda: D.render_document(path))]
    with patch.object(D, "_lean_answer", return_value=None):
        old = [outcome(lambda: D.check_document(path)), outcome(lambda: D.render_document(path))]
    return decided, new, old


def _lean_error(path: Path):
    return relay.answer("document", D._document_case(path.read_bytes(), True, path.parent))[1]


@pytest.mark.parametrize("envelope", ["frozen", "modern"])
@pytest.mark.parametrize("name", VALID)
def test_a_valid_senses_document_is_decided_by_lean(tmp_path, name, envelope):
    front, body = _parts(name)
    path = _write(tmp_path, front if envelope == "frozen" else _modern(front), body)
    decided, new, old = _public(path)
    assert decided and new == old and "returned" in new[0], (new, old)


@pytest.mark.parametrize("envelope", ["frozen", "modern"])
def test_a_senses_rejection_the_row_can_carry_is_lean_s(tmp_path, envelope):
    front, body = _parts("g_bad_default")
    path = _write(tmp_path, front if envelope == "frozen" else _modern(front), body)
    decided, new, old = _public(path)
    assert decided and new == old and "raised" in new[0], (new, old)
    assert "default 3, which is not one of its senses" in new[0]["raised"]["message"]


@pytest.mark.parametrize("name", REFUSED)
def test_a_senses_refusal_with_its_diagnostic_keeps_the_retained_path(tmp_path, name):
    front, body = _parts(name)
    path = _write(tmp_path, front, body)
    error = _lean_error(path)
    assert isinstance(error, CheckerUnavailable) and "senses refusal" in error.message, error
    decided, new, old = _public(path)
    assert not decided and new == old and new[0]["raised"]["diagnostic"], (new, old)


def _fault(front: dict, fault: str):
    """A one-fault variant of a valid senses document: (front matter, pack bytes or None for the pilot's, or b"" for
    no pack file)."""
    senses = front["senses"]
    pack = None
    if fault == "missing pack":
        pack = b""
    elif fault == "pack not UTF-8":
        pack = b"\xff\xfe"
    elif fault == "pack not JSON":
        pack = b"{"
    elif fault == "pack entry not a string":
        senses["packs"] = [7]
    elif fault == "unknown bundled pack":
        senses["packs"] = ["absent@1"]
    elif fault == "senses not an object":
        front["senses"] = []
    elif fault == "unknown senses key":
        senses["extra"] = 1
    elif fault == "packs not a list":
        senses["packs"] = "pack.json"
    elif fault == "own not a list":
        senses["own"] = {}
    elif fault == "own entry malformed":
        senses["own"] = [7]
    elif fault == "defaults not an object":
        senses["defaults"] = [1]
    elif fault == "defaults null":
        senses["defaults"] = None
    elif fault == "one-part MIXED":
        unit = front["units"][0]
        front["units"][0] = {"id": "whole", "span": unit["span"], "status": "MIXED", "parts": [unit]}
    elif fault == "a claim graph":
        front["graph"] = {"nodes": [], "edges": []}
    elif fault == "norms profile":
        front["environment"]["profiles"] = ["norms@0", "relational-fol@0"]
    elif fault == "soft-norms profile":
        front["environment"]["profiles"] = ["norms@0", "relational-fol@0", "soft-norms@0"]
    elif fault == "unknown kind":
        front["units"][0]["kind"] = "bogus"
    elif fault == "fence not its id":
        front["units"][0]["content"] = {"fence": "u9"}
    elif fault == "reading set":
        front["reading_sets"] = [{"id": "s", "unit": "u1", "status": "open", "readings": []}]
    else:
        raise AssertionError(fault)
    return front, pack


FAULTS = ["missing pack", "pack not UTF-8", "pack not JSON", "pack entry not a string", "unknown bundled pack",
          "senses not an object", "unknown senses key", "packs not a list", "own not a list", "own entry malformed",
          "defaults not an object", "defaults null", "one-part MIXED", "a claim graph", "norms profile",
          "soft-norms profile", "unknown kind", "fence not its id", "reading set"]
# The faults the mode decides (the rest keep the retained path, which reads the pack file, or whose answer carries
# the senses route's diagnostic object, or which the mode does not compose: a claim graph, norms, frozen reading sets).
DECIDED = {"pack not JSON", "senses not an object", "unknown senses key", "packs not a list", "own not a list",
           "own entry malformed", "defaults not an object", "one-part MIXED", "unknown kind"}
DECIDED_MODERN = {"reading set"}
# A frozen envelope names one profile, so the profile faults are written over the modern envelope only.
MODERN_ONLY = {"norms profile", "soft-norms profile"}


@pytest.mark.parametrize("fault,envelope", [
    pytest.param(fault, envelope, id=f"{fault}-{envelope}")
    for envelope in ("frozen", "modern") for fault in FAULTS
    if not (envelope == "frozen" and fault in MODERN_ONLY)])
def test_every_senses_fault_has_the_retained_path_s_public_outcome(tmp_path, fault, envelope):
    """Each fault of a senses document, on both envelopes (the profile faults on the modern one): the public check
    and render equal the retained path's, in Python's order (`_parts`' faults, then `read_senses`: the shape of
    `senses`, the packs, `own`, the route), and the mode decides the faults its rows can carry."""
    front, body = _parts("a_front_matter_default")
    front = front if envelope == "frozen" else _modern(front)
    front, pack = _fault(deepcopy(front), fault)
    path = _write(tmp_path, front, body, pack)
    decided, new, old = _public(path)
    assert new == old, (new, old)
    if fault in DECIDED or envelope == "modern" and fault in DECIDED_MODERN:
        assert decided and "raised" in new[0], new
    elif fault not in ("soft-norms profile",):
        assert not decided, new


@pytest.mark.parametrize("packs", [None, [], ["{}", "{}"], [7], [None], "pack"],
                         ids=["absent", "none", "two", "a number", "a null", "a string"])
def test_a_request_without_the_pack_texts_keeps_the_retained_path(tmp_path, packs):
    """The pack texts are the request's (Python reads the files): absent, of another count, or not strings, the mode
    answers `CheckerUnavailable`, never a verdict."""
    front, body = _parts("a_front_matter_default")
    path = _write(tmp_path, front, body)
    case = D._document_case(path.read_bytes(), True, path.parent)
    assert "packs" in case and "lexicon" in case
    if packs is None:
        case.pop("packs")
    else:
        case["packs"] = packs
    error = relay.answer("document", case)[1]
    assert isinstance(error, CheckerUnavailable) and "pack files are read by its loader" in error.message, error


def test_a_senses_unit_s_meaning_id_is_bound_to_the_projected_environment(tmp_path, monkeypatch):
    """A fence's formula is read in the senses route's projected environment, so its `meaning_id` is bound there; the
    document environment's identity is refused (`_lean_document`)."""
    front, body = _parts("a_front_matter_default")
    path = _write(tmp_path, front, body)
    raw = path.read_bytes()
    row = D._lean_answer(raw, True, path.parent)
    D._lean_document(raw, path, row, admitted=True)
    env = D._environment(front["environment"])
    forged = deepcopy(row)
    unit = forged["units"][0]
    unit["meaning_id"] = D.digest(f"ve-meaning-{env.identity_version}\n",
                                  {"environment_id": env.environment_id, "ast": unit["content"]})
    assert unit["meaning_id"] != row["units"][0]["meaning_id"]
    with pytest.raises(CheckerUnavailable):
        D._lean_document(raw, path, forged, admitted=True)


def test_a_fence_without_a_formula_may_have_no_content_but_others_must(tmp_path):
    """A preamble line or an open unit of a senses document has no content (the route's reading); a unit that is not
    an English fence still needs its content."""
    front, body = _parts("c_written_definition_line")
    path = _write(tmp_path, front, body)
    raw = path.read_bytes()
    row = D._lean_answer(raw, True, path.parent)
    assert "content" not in row["units"][0] and "content" in row["units"][1]
    meta, source, fences = D._split(raw)
    declared = list(D._parts(meta["units"]))
    senses = _reading(raw, path)
    D._bind_document_answer(source, meta, declared, row, senses)
    without = deepcopy(meta)
    without.pop("senses")
    with pytest.raises(ValueError):
        D._bind_document_answer(source, without, declared, row, senses)
    with pytest.raises(ValueError):  # a senses row is bound only to the reading Python holds
        D._bind_document_answer(source, meta, declared, row)


def _reading(raw: bytes, path: Path):
    """The senses route's reading of a document's English fences, as `_lean_document` holds it."""
    from ve.senses_document import read_senses
    meta, _, fences = D._split(raw)
    return read_senses(D._environment(meta["environment"]), meta["senses"], D._english_fences(meta["units"], fences),
                       path.parent, meta.get("reading_sets", []))


def _two_fences(tmp_path: Path, modern: bool = False) -> tuple[bytes, Path, dict]:
    """A senses document with two English fences, each read to a formula, and Lean's answer for it (review F7)."""
    front, body = _parts("a_front_matter_default")
    front["units"].append({"id": "u2", "span": [12, 24], "kind": "asserted", "meaning": "specified",
                           "support": "assumption", "surface": "english", "content": {"fence": "u2"}})
    path = _write(tmp_path, _modern(front) if modern else front,
                  body + "Sentence 2.\n```ve u2\nClaude is not corrigible.\n```\n")
    raw = path.read_bytes()
    row = D._lean_answer(raw, True, path.parent)
    assert row is not None and all("content" in unit for unit in row["units"]), row
    return raw, path, row


@pytest.mark.parametrize("modern", [False, True], ids=["frozen", "modern"])
@pytest.mark.parametrize("unit", [0, 1])
def test_a_fence_the_route_read_keeps_its_formula(tmp_path, modern, unit):
    """lf-16f looprecheck1 F7: a fence the senses route read to a formula has that formula as its content. Dropped
    (with its `meaning_id`, so the unit is still well formed), or replaced by another fence's formula with that
    formula's identity, the answer is not bound to the document sent; the premises no longer flip to `model`."""
    raw, path, row = _two_fences(tmp_path, modern)
    D._lean_document(raw, path, row, admitted=True)
    dropped = deepcopy(row)
    for key in ("content", "meaning_id"):
        dropped["units"][unit].pop(key)
    with pytest.raises(CheckerUnavailable, match="not bound"):
        D._lean_document(raw, path, dropped, admitted=True)
    swapped = deepcopy(row)
    other = row["units"][1 - unit]
    assert other["content"] != row["units"][unit]["content"]
    swapped["units"][unit].update(content=other["content"], meaning_id=other["meaning_id"])
    with pytest.raises(CheckerUnavailable, match="not bound"):
        D._lean_document(raw, path, swapped, admitted=True)


def test_a_fence_the_route_read_to_no_formula_has_no_content(tmp_path):
    """A preamble line (or an open unit) has no formula: a content given it, even a formula the route read for
    another fence with that formula's identity, is not bound (review F7, the converse)."""
    front, body = _parts("c_written_definition_line")
    path = _write(tmp_path, front, body)
    raw = path.read_bytes()
    row = D._lean_answer(raw, True, path.parent)
    assert "content" not in row["units"][0] and "content" in row["units"][1]
    forged = deepcopy(row)
    forged["units"][0].update(content=row["units"][1]["content"], meaning_id=row["units"][1]["meaning_id"])
    with pytest.raises(CheckerUnavailable, match="not bound"):
        D._lean_document(raw, path, forged, admitted=True)


def _shown(document) -> str:
    """What the relay shows of a document built from Lean's answer: its report and every unit as built."""
    return json.dumps({"report": D._report(document), "units": document["units"]}, sort_keys=True, default=repr)


@pytest.mark.parametrize("name", ["two fences", "c_written_definition_line"])
def test_every_mutant_of_a_senses_answer_is_refused_or_changes_nothing(tmp_path, name):
    """Review F7's class: the relay mutation gate's mutants (`tools/relay_mutation_gate.mutants`: every field dropped,
    emptied, duplicated, retyped and rebound), one at a time and every pair of a unit's members dropped together,
    of genuine senses answers. Each mutant the response schema types is `CheckerUnavailable` from `_lean_document`,
    or the document it builds shows exactly what the genuine one does."""
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
    import relay_mutation_gate as G
    from ve.backends.service_schema import ROWS, Context, Invalid
    if name == "two fences":
        raw, path, row = _two_fences(tmp_path / "doc")
    else:
        front, body = _parts(name)
        path = _write(tmp_path / "doc", front, body)
        raw = path.read_bytes()
        row = D._lean_answer(raw, True, path.parent)
    genuine = _shown(D._lean_document(raw, path, row, admitted=True))
    request = D._document_case(raw, True, path.parent)
    case, schema, named = Context(request), ROWS["document"][0], G._strings(request)
    found = [answer for _, answer in G.mutants(row, named, {})]
    for index, unit in enumerate(row["units"]):
        keys = sorted(unit)
        for i, first in enumerate(keys):
            for second in keys[i + 1:]:
                pair = deepcopy(row)
                pair["units"][index].pop(first)
                pair["units"][index].pop(second)
                found.append(pair)
    typed = 0
    for mutant in found:
        try:
            schema(mutant, case, {})
        except Invalid:
            continue
        typed += 1
        try:
            shown = _shown(D._lean_document(raw, path, mutant, admitted=True))
        except CheckerUnavailable:
            continue
        assert shown == genuine, json.dumps(mutant)[:400]
    assert typed >= 20, typed


def test_a_pilot_is_written_with_the_files_it_names_beside_it(tmp_path):
    """The recorders write each pilot where a checker reads it (`lean_first_diff.write_pilot`, used by the A/B
    recorder, the batch's measurement and the words A/B): a senses document with the pack its `senses.packs` names
    beside it, as its branch holds it, and no other file; a document that names no file alone (review F2: written
    alone, every senses pilot read as a missing pack)."""
    import subprocess
    from tools.lean_first_diff import write_pilot
    repo = tmp_path / "repo"
    (repo / "usecases" / "p").mkdir(parents=True)
    document = (DATA / "a_front_matter_default.senses.md").read_bytes()
    (repo / "usecases" / "p" / "a.ve.md").write_bytes(document)
    (repo / "usecases" / "p" / "pack.json").write_bytes((DATA / "pack.json").read_bytes())
    (repo / "usecases" / "p" / "other.json").write_text("{}")

    def git(*args):
        subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.invalid", *args], cwd=repo,
                       check=True, capture_output=True)
    git("init", "-q", "-b", "pilot/t")
    git("add", ".")
    git("commit", "-q", "-m", "pilot")
    scratch = tmp_path / "scratch"
    scratch.mkdir()
    path = write_pilot(repo, scratch, "pilot/t:usecases/p/a.ve.md", "abc", document)
    assert path == scratch / "abc" / "usecases" / "p" / "a.ve.md" and path.read_bytes() == document
    assert (path.parent / "pack.json").read_bytes() == (DATA / "pack.json").read_bytes()
    assert not (path.parent / "other.json").exists()
    decided, new, old = _public(path)
    assert decided and new == old and "returned" in new[0], (new, old)
    plain = document.replace(b', "senses": {"packs": ["pack.json"], "defaults": {"corrigible": 1}}', b"")
    assert plain != document
    assert write_pilot(repo, scratch, "pilot/t:usecases/p/b.ve.md", "def", plain) == scratch / "def.ve.md"
