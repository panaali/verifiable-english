"""The `acts@0` wire table in shadow (ap-1bf): the legacy validator still owns the verdict; the engines name the
member of 1.1 at and around each limit of `VE.Acts.Lexical`, the limits read from Lean and never copied."""

from copy import deepcopy
import json
import os
from pathlib import Path
import re
import subprocess

import pytest

from conformance.acts_contract import REGISTRY, acts_source
from conformance.wire_contract_engine import CLEAN, Fault, load, run
from conformance.wire_contract_faults import catalogue, catalogue_index, expected_record, route
from conformance.wire_contract_faults_acts import D31, EXAMPLES, at_count, at_frames, at_limits, base, limits
from tests import lean_routes
from tests.subprocesses import HANG_TIMEOUT
from tools import nested_pytest
from ve.errors import UnsupportedProfile, VEError
from ve.norms_contract import OUTSIDE, legacy_validation

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = load("acts@0")
UNIT_FILES = ("ve/wire_contract/acts@0.json", "conformance/acts_contract.py", "conformance/wire_contract_faults_acts.py",
              "lean/VE/WireContract/Hooks/Acts.lean", "tests/test_acts_contract.py")
# Lean is the oracle of the limits (`limits`) and the legacy validator's decoder.
pytestmark = pytest.mark.skipif(not lean_routes.SERVICE.exists(), reason="ve_service is not built")


def legacy(raw, norms):
    try:
        legacy_validation(deepcopy(raw), deepcopy(norms))
    except VEError as exc:
        return exc
    return None


def accepted():
    examples = [json.loads(p.read_text()) for p in sorted(EXAMPLES.glob("*.json"))]
    return [(e["environment"], e["norms"]) for e in examples] + [at_count(), at_frames()]


def case(raw, norms, kind="norms-elaborate"):
    return {"id": "c", "kind": kind, "environment": raw, "norms": norms}


def engine_records(sources):
    """Each source's record in Python's engine and in Lean's (`None` when clean), as pairs."""
    python = [run(CONTRACT, {"environment": deepcopy(raw), "norms": deepcopy(norms)}, registry=REGISTRY)
              for raw, norms in sources]
    lean = lean_routes.diagnose("acts@0", [case(raw, norms) for raw, norms in sources])
    assert [row["status"] for row in lean] == ["ok"] * len(sources)
    return [(outcome.record if isinstance(outcome, Fault) else None, row.get("diagnostic"))
            for outcome, row in zip(python, lean)]


def test_a_source_without_norms_gives_one_record_in_both_engines():
    """F1 of ap-1bf's review: without `norms@0` both engines give one check, outcome and text, the profile
    row's, which Lean writes and Python relays."""
    raw, norms = base()
    raw["profiles"].remove("norms@0")
    [(python, lean)] = engine_records([(raw, norms)])
    assert python is not None and python == lean
    assert lean["check"] == "1.1d" and lean["text"] == str(legacy(raw, norms))


# The test files whose `acts@0` sources the recorded corpus holds (F2 of ap-1bf's review): `-k acts` selects this
# file and the unit's row of the s5 tests, and the corpus test itself is left out of its own run.
RECORDED_TESTS = ("tests/test_acts_contract.py", "tests/test_wire_contract_s5_lean.py")


def recorded_sources(output):
    """The `[test id, environment, norms]` rows `tests/contract_input_recorder.py` records for `acts@0` while the
    recorded test files run."""
    # An outer recorder's settings (this file runs under `tests/test_wire_gate_corpus.py`'s) are not this run's.
    outer = {k: v for k, v in os.environ.items() if not k.startswith("VE_CONTRACT_")}
    environment = nested_pytest.environment(outer, VE_CONTRACT_INPUTS=str(output), VE_CONTRACT_UNIT="acts@0",
                                            VE_NATIVE_PREBUILT="1", PYTHONPATH=str(ROOT))
    result = subprocess.run(nested_pytest.command(["-q", "-p", "tests.contract_input_recorder", "-p",
                                                   "no:cacheprovider", "-o", "addopts=", "-m", "not live", "-k",
                                                   "acts and not recorded_corpus", *RECORDED_TESTS]),
                            cwd=ROOT, env=environment, capture_output=True, text=True, timeout=HANG_TIMEOUT)
    # A recorded test that fails (exit 1) still records its sources; the comparison below is this test's own.
    assert result.returncode in (0, 1), result.stdout[-4000:]
    return json.loads(output.read_text())


def test_the_saved_wording_delta_keeps_the_base_path_and_quoted_names():
    """R1 over the saved delta of A1 (docs/act-phrases/ap-1bfb/delta.json): the head record keeps the base's path,
    check and every profile it quoted, and is Lean's record today, at any revision."""
    rows = json.loads((ROOT / "docs/act-phrases/ap-1bfb/delta.json").read_text())["rows"]
    quoted = re.compile(r"[a-z][a-z-]*@[0-9]+")
    for row in rows:
        base_record, head = row["base"], row["head"]
        assert (head["path"], head["check"]) == (base_record["path"], base_record["check"])
        assert set(quoted.findall(base_record["text"])) <= set(quoted.findall(head["text"]))
        [(_, lean)] = engine_records([(row["source"]["environment"], row["source"]["norms"])])
        assert {k: v for k, v in lean.items() if k != "revision"} == {k: v for k, v in head.items() if k != "revision"}


def test_the_recorded_corpus_gives_one_record_in_both_engines(tmp_path):
    """F2 of ap-1bf's review: every `acts@0` source the tests submit gives one record, or none, in both engines."""
    recorded = recorded_sources(tmp_path / "inputs.json")
    # each recorded file adds sources of its own (the s5 row's: its base without rules), and F1's source is one
    assert {label.split("::")[0] for label, _, _ in recorded} == set(RECORDED_TESTS)
    assert any("norms@0" not in raw["profiles"] for _, raw, _ in recorded)
    pairs = engine_records([(raw, norms) for _, raw, norms in recorded])
    assert sum(lean is not None for _, lean in pairs) > len(catalogue("acts@0"))
    assert [label for (label, _, _), (python, lean) in zip(recorded, pairs)
            if comparable(python) != comparable(lean)] == []


def _frame(head, **extra):
    return {"head": head, "markers": [], "split": [], "modifiers": [], **extra}


# Edits of `base()` by where the decoder refuses them: before the `acts` block's frames and adverbs (the envelope,
# the block's members, `fixed`), at them (D-31), and after them (the sorts and predicates). Several share a generic
# text with each other, "String expected" among them (ap-1bfb review F1).
BEFORE = {"language": lambda raw, block: raw.update(language=5),
          "spec_revision": lambda raw, block: raw.update(spec_revision=5),
          "member": lambda raw, block: raw.update(x=5),
          "fixed": lambda raw, block: block["fixed"].append(5),
          "fixed absent": lambda raw, block: block.pop("fixed"),
          "fixed phrase": lambda raw, block: block["fixed"].append("Naive"),
          "block member": lambda raw, block: block.update(x=5)}
AT = {"head": lambda raw, block: block.update(frames=[_frame(5)]),
      "adverb": lambda raw, block: block.update(adverbs=[5]),
      "frames": lambda raw, block: block.update(frames=5),
      "frame member": lambda raw, block: block.update(frames=[_frame("give", x=5)]),
      "head case": lambda raw, block: block.update(frames=[_frame("Give")]),
      "adverbs repeated": lambda raw, block: block.update(adverbs=["promptly", "promptly"])}
AFTER = {"description": lambda raw, block: raw["vocabulary"]["predicates"]["c"].update(description=5),
         "sort": lambda raw, block: raw["vocabulary"]["sorts"]["person"].update(description=5)}


def test_the_frames_members_name_only_the_first_refusal():
    """F1 of ap-1bfb's review, as a class: 1.1e and 1.1f name a refusal of the frames and adverbs only when the
    decoder refuses there first. An earlier refusal stays 1.1d in both engines though the frames are refused with the
    same text; a later refusal does not hide the frames'. Every pair of edits from two of the three stages, and each
    edit alone."""
    rows = [((b, at, after), "1.1d" if b else "1.1f" if at else "1.1d")
            for b in (None, *BEFORE) for at in (None, *AT) for after in (None, *AFTER)
            if (b, at, after) != (None, None, None) and sum(x is not None for x in (b, at, after)) <= 2]
    sources = []
    for edits, _ in rows:
        raw, norms = base()
        for stage, name in zip((BEFORE, AT, AFTER), edits):
            if name is not None:
                stage[name](raw, raw["vocabulary"]["acts"])
        sources.append((raw, norms))
    pairs = engine_records(sources)
    got = [(edits, python and python["check"], lean and lean["check"]) for (edits, _), (python, lean) in zip(rows, pairs)]
    assert [(edits, p, l) for (edits, want), (_, p, l) in zip(rows, got) if (p, l) != (want, want)] == []
    assert [edits for (edits, _), (python, lean) in zip(rows, pairs) if comparable(python) != comparable(lean)] == []
    # the pairs the review found: a shared text before the frames, and one after them
    assert ("language", "head", None) in [edits for edits, _ in rows]
    assert ("fixed", "adverb", None) in [edits for edits, _ in rows]


def test_the_limits_are_leans_and_never_copied():
    numerals = re.compile(r"(?<![0-9])(" + "|".join(str(v) for v in limits().values()) + r")(?![0-9])")
    for relative in UNIT_FILES:
        assert not numerals.search((ROOT / relative).read_text()), relative


def test_the_limit_example_is_the_source_at_the_limits_and_the_catalogue_is_current():
    assert json.loads((EXAMPLES / "limit.json").read_text()) == dict(zip(("environment", "norms"), at_limits()))
    index = ROOT / "conformance/wire-contract/acts@0-catalogue.json"
    assert json.loads(index.read_text()) == catalogue_index("acts@0")


def test_the_sources_at_each_limit_are_accepted_and_clean_in_python():
    for raw, norms in accepted():
        assert legacy(raw, norms) is None
        assert run(CONTRACT, {"environment": raw, "norms": norms}, registry=REGISTRY) is CLEAN


def own_texts(check):
    """Whether a record at `check` keeps its text and args to each language: an inherited member of an included
    `norms@0` phase (2.7). 1.1's inherited members carry the text of Lean's decoder in both."""
    _, steps = route(CONTRACT, check)
    return check.startswith("norms/") and bool(steps[-1][1].get("inherited"))


def comparable(record):
    """A record as both engines must give it (`own_texts`)."""
    if record is None or not own_texts(record["check"]):
        return record
    return {k: v for k, v in record.items() if k not in ("text", "args")}


def expected(fault, lean=False):
    """The fault's expected record: the catalogue's fields, and for an inherited member (a record without its
    own `text`) the legacy validator's text, unless the language keeps its own (`own_texts`) and is Lean."""
    record = expected_record(CONTRACT, fault)
    if "text" not in record and not (lean and own_texts(fault.check)):
        error = legacy(*fault.source())
        assert error is not None, fault.name
        record["text"] = str(error)
    return record


def test_every_fault_gives_its_member_in_python_with_leans_text():
    for fault in catalogue("acts@0"):
        raw, norms = fault.source()
        outcome = run(CONTRACT, {"environment": raw, "norms": norms}, registry=REGISTRY)
        assert legacy(raw, norms) is not None and isinstance(outcome, Fault), fault.name
        record = expected(fault)
        assert {k: outcome.record[k] for k in record} == record, fault.name


def test_every_fault_gives_its_record_in_lean_and_the_sources_at_each_limit_are_clean():
    faults = catalogue("acts@0")
    rows = lean_routes.diagnose("acts@0", [case(*f.source()) for f in faults] + [case(*s) for s in accepted()])
    for fault, row in zip(faults, rows):
        assert row["outcome"] == "fault", fault.name
        record = expected(fault, lean=True)
        assert {k: row["diagnostic"][k] for k in record} == record, fault.name
    # each condition of D-31 after 31a has a text of its own, which its fault reaches
    texts = {row["diagnostic"]["text"] for f, row in zip(faults, rows) if f.name.startswith("frames-31")}
    assert len(texts) == len(D31)
    assert [row["outcome"] for row in rows[len(faults):]] == ["clean"] * len(accepted())


def test_the_adapters_read_acts_sources_of_the_norms_route_only():
    raw, norms = base()
    plain, defaults = deepcopy(raw), deepcopy(raw)
    plain["profiles"] = ["norms@0", "relational-fol@0"]
    defaults["profiles"] = ["acts@0", "norm-defaults@0", "norms@0", "relational-fol@0"]
    cases = [case(raw, norms), case(raw, norms, "norms-conflict"), case(plain, norms), case(defaults, norms),
             case(raw, norms, "norm-defaults-elaborate")]
    rows = lean_routes.diagnose("acts@0", cases)
    assert [row["status"] for row in rows] == ["ok", "ok", "error", "error", "error"]
    assert acts_source(cases[0]) == {"environment": raw, "norms": norms}
    for c, row in zip(cases[2:], rows[2:]):
        with pytest.raises(UnsupportedProfile) as raised:
            acts_source(c)
        assert str(raised.value) == row["error"]
    assert rows[2]["error"] == OUTSIDE
