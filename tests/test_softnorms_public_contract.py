"""The public soft-source rejection boundary of wire-contract-s4.md item 1."""

from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys

import pytest

from conformance.soft_norms import multi_fault_base
from ve.admission import admit_document
from ve.errors import VEError
from ve.soft_route import admit_soft_document
from ve.softnorms import SoftEnvironment, load_soft_document
from ve.softnorms_contract import REGISTRY, public_rejection
from ve.wire_contract.engine import Registry, load


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = load("soft-norms@0")
SPEC = ROOT / "docs/spec/wire-contract-s4.md"
SWITCH = ROOT / "conformance/wire-contract/soft-norms@0-switch.json"


def spec_quote(heading):
    """The block quote under the spec's heading `### heading`, its lines joined by spaces."""
    body = SPEC.read_text().split(f"\n### {heading}\n", 1)[1].split("\n#", 1)[0]
    return " ".join(line[2:] for line in body.splitlines() if line.startswith("> "))


def release_note(signed):
    """Spec 3.3: its text, with the placeholder replaced by each signed check, in table order, as `id: sentence`."""
    from conformance.wire_contract_gate import all_checks
    before, rest = spec_quote("3.3 The release note").split("⟨", 1)
    order = all_checks(CONTRACT)
    return before + " ".join(f"{check}: {signed[check]}" for check in sorted(signed, key=order.index)) \
        + rest.split("⟩", 1)[1]


def document(norms):
    return {"units": [{"kind": "norm", "content": unit} for unit in norms]}


def bad_party(name="Q!"):
    raw, norms = multi_fault_base()
    raw["vocabulary"]["soft"]["parties"] = ["p", name]
    return raw, norms


def legacy(raw, norms):
    with pytest.raises(VEError) as caught:
        load_soft_document(deepcopy(raw), deepcopy(norms))
    return caught.value


def test_public_call_reports_the_first_fault_and_keeps_the_legacy_error():
    cases = []
    cases.append(bad_party())
    raw, norms = multi_fault_base()
    norms[0]["norm"]["extra"] = 1
    cases.append((raw, norms))
    raw, norms = multi_fault_base()
    raw["language"] = "x"
    cases.append((raw, norms))
    raw, norms = multi_fault_base()
    norms[3]["norm"]["over"] = ["b1"]
    cases.append((raw, norms))
    expected = [
        ("2.7a", "SOFT_INVALID_NAME", "/environment/vocabulary/soft/parties/1",
         "InvalidInput: invalid soft name Q!"),
        ("4.1c", "SOFT_INVALID_INPUT", "/norms/0/norm", "InvalidInput: invalid norm fields"),
        ("1.2", "SOFT_UNSUPPORTED_PROFILE", "/environment/language",
         "UnsupportedProfile: Unsupported language"),
        ("6.8", "SOFT_OVER_HARD", "", "SoftOverHard: rule d3 over b1"),
    ]
    for (raw, norms), (check, code, path, text) in zip(cases, expected):
        old = legacy(raw, norms)
        with pytest.raises(VEError) as caught:
            admit_soft_document(raw, document(norms))
        error = caught.value
        with pytest.raises(VEError) as admitted:
            admit_document(raw, document(norms))
        # The public API routes submitted soft sources through this same boundary.
        assert type(admitted.value) is type(error)
        assert admitted.value.to_dict() == error.to_dict()
        record = error.diagnostic
        assert type(error) is type(old) and error.code == old.code == code
        assert (record["check"], record["code"], record["path"], record["text"]) == (
            check, code, path, text)
        assert record["revision"] == 4
        assert error.message == str(error) == error.to_dict()["message"] == text
        assert error.to_dict()["diagnostic"] == record
        assert error.path == old.path and error.span == old.span
    assert cases[1][0] is not None and str(legacy(*cases[1])) != expected[1][3]


def test_public_boundary_residual_deferred_failure_shadow_and_purity():
    raw, norms = multi_fault_base()
    handmade = VEError("legacy says no")
    handmade.code = "SOFT_INVALID_INPUT"
    assert public_rejection(raw, norms, handmade) is handmade
    assert handmade.diagnostic == {
        "contract": "soft-norms@0", "revision": 4, "check": "residual", "phase": "residual",
        "code": "SOFT_INVALID_INPUT", "class": "InvalidInput", "path": "",
        "text": "legacy says no", "args": {}}
    assert str(handmade) == "legacy says no"

    duplicate_raw, duplicate_norms = multi_fault_base()
    duplicate_norms[3]["norm"]["name"] = "b1"
    source_before = deepcopy((duplicate_raw, duplicate_norms))
    original = legacy(duplicate_raw, duplicate_norms)
    missing = Registry().register(
        hooks={k: v for k, v in REGISTRY.hooks.items() if k != "w1_declarations"},
        classifiers=REGISTRY.classifiers, views=REGISTRY.views, adapters=REGISTRY.adapters)
    assert public_rejection(duplicate_raw, duplicate_norms, original, registry=missing) is original
    assert original.diagnostic == {"contract": "soft-norms@0", "revision": 4,
                                   "deferred": "2.3", "text": "DuplicateDeclaration: rule b1"}
    assert str(original) == "DuplicateDeclaration: rule b1"
    assert (duplicate_raw, duplicate_norms) == source_before
    again = original.diagnostic
    assert public_rejection(duplicate_raw, duplicate_norms, original) is original
    assert original.diagnostic is again

    broken = Registry().register(hooks={**REGISTRY.hooks, "w1_declarations": lambda *_: 1 / 0},
                                 classifiers=REGISTRY.classifiers, views=REGISTRY.views,
                                 adapters=REGISTRY.adapters)
    error = legacy(duplicate_raw, duplicate_norms)
    assert public_rejection(duplicate_raw, duplicate_norms, error, registry=broken) is error
    assert error.diagnostic is None and str(error) == "DuplicateDeclaration: rule b1"
    shadow = {**CONTRACT, "status": "shadow", "revision": 3}
    error = legacy(*bad_party())
    assert public_rejection(*bad_party(), error, contract=shadow) is error
    assert error.diagnostic is None


def test_prevalidated_and_later_errors_keep_their_legacy_message(monkeypatch):
    raw, norms = multi_fault_base()
    norms[3]["norm"]["name"] = "b1"
    with pytest.raises(VEError) as caught:
        admit_soft_document(SoftEnvironment(raw), document(norms))
    assert caught.value.diagnostic is None
    assert str(caught.value) == "DuplicateDeclaration: rule b1"

    raw, norms = multi_fault_base()
    def fail(_case):
        raise VEError("x")
    monkeypatch.setattr("ve.soft_route._run", fail)
    with pytest.raises(VEError) as caught:
        admit_soft_document(raw, document(norms))
    assert caught.value.diagnostic is None and str(caught.value) == "x"


def test_accepted_call_does_not_import_diagnostics():
    code = """import sys
from conformance.soft_norms import multi_fault_base
from ve.ast import formula_to_data
from ve.admission import admit_document
from ve.soft_route import admit_soft_document
from ve.softnorms import SoftEnvironment, SoftNormDocument
raw, norms = multi_fault_base()
soft = SoftNormDocument(SoftEnvironment(raw), norms)
label, formula = soft.elaborated.premises()[0]
ast = formula_to_data(soft.extended_env, formula, _generated=True)
document = {'units': [{'id': f'u{i}', 'span': [i, i + 1], 'kind': 'norm', 'content': n}
                      for i, n in enumerate(norms)],
            'graph': {'root': 'leaf', 'nodes': [{'name': 'leaf', 'ast': ast, 'label': label}]}}
direct = admit_soft_document(raw, document)
assert admit_document(raw, document) == direct
assert 've.softnorms_contract' not in sys.modules
assert 've.wire_contract' not in sys.modules
"""
    result = subprocess.run([sys.executable, "-c", code], cwd=ROOT, capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr


def test_new_entry_paths_have_distinct_corpus_inputs():
    raw, norms = bad_party("R!")
    with pytest.raises(VEError) as caught:
        admit_soft_document(raw, document(norms))
    assert caught.value.diagnostic["text"] == "InvalidInput: invalid soft name R!"

    raw, norms = bad_party("T!")
    error = VEError("x")
    assert public_rejection(raw, norms, error) is error
    assert error.code == "InvalidInput"
    assert error.diagnostic["text"] == str(error) == "InvalidInput: invalid soft name T!"


def test_release_note_is_the_spec_text_with_the_signed_sentences():
    """Astra B1 and B2, Fable B4: the release note is spec 3.3 word for word, with the `signed` sentences
    themselves. It limits the record to errors of the source's validation, scopes the unchanged `code` to the
    switch, and discloses S4-pre's code changes."""
    switch = json.loads(SWITCH.read_text())
    assert (switch["contract"], switch["revision"]) == (CONTRACT["contract"], CONTRACT["revision"])
    note = switch["release_note"]
    assert note == release_note(switch["signed"])
    for check, sentence in switch["signed"].items():
        assert f"{check}: {sentence}" in note
    assert '"first" is its order' in note
    assert "while it validates that source" in note and "has no record" in note
    assert "The public switch does not change the error's `code`." in note
    assert "The error's `code` has not changed" not in note
    assert "speech-acts@0" in note and "norm-defaults@0" in note


def test_soft_norms_paragraph_is_spec_3_4():
    text = (ROOT / "docs/spec/soft-norms.md").read_text()
    paragraph = text[text.index("**The public record.**"):].split("\n\n", 1)[0]
    assert " ".join(paragraph.splitlines()) == spec_quote("3.4 The paragraph added to soft-norms.md, section 8")
