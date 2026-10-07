"""The 11b public projection against the frozen pre-switch W2 checker."""
from __future__ import annotations

import json
import subprocess
import sys

import pytest

from subprocesses import HANG_TIMEOUT
from test_speech_source_lean import base_env, templates
from test_speech_acts_lean import U, unit
from tests.frozen_speech.speech_document import SpeechSource as FrozenSource
from ve.speech_document import SpeechSource
from ve.speech_english import legend


@pytest.mark.parametrize("name,metadata,source", templates(), ids=lambda case: case if isinstance(case, str) else None)
def test_public_speech_projection_matches_frozen(name, metadata, source):
    old = FrozenSource(metadata, source.encode(), {})
    new = SpeechSource(metadata, source.encode(), {})
    assert new.document_id == old.document_id
    assert new.source_id == old.source_id
    assert new.report["environment_id"] == old.document.env.environment_id
    assert new.legend == legend(old.document.env)
    assert new.report["warnings"] == old.document.warnings
    assert new.answer_lines == old.answer_lines
    assert new.compliance_lines == old.compliance_lines
    assert new.coverage() == old.coverage()
    assert [{"norm": rule} for rule in new.report["rules"]] == [r.to_dict() for r in old.document.policy.rules]


def test_fenced_english_is_checked_after_resolution():
    source = "Is atlas reviewed?\n"
    metadata = {"format": "ve-document@2", "environment": base_env(),
                "units": [{**unit("q", 0, "question", {"fence": "q"}),
                           "span": [0, len(source)], "surface": "english"}]}
    fences = {"q": source}
    old = FrozenSource(metadata, source.encode(), fences)
    new = SpeechSource(metadata, source.encode(), fences)
    assert new.document_id == old.document_id
    assert new.answer_lines == old.answer_lines
    assert new.report["questions"][0]["mode"] == "polar"


def test_inconsistent_premises_keep_the_checked_certificate():
    import copy
    from test_speech_source_lean import certified, core
    from test_speech_acts_lean import U
    from ve.ast import And
    from ve.entailment import prove_entailment

    env = base_env()
    metadata, source = certified(env)
    metadata = copy.deepcopy(metadata)
    line = "Atlas is not reviewed.\n"
    metadata["units"].append({**unit("anti", 0, "asserted", {"ast": ["not", U("reviewed", "atlas")]}),
                              "span": [len(source.encode()), len((source + line).encode())]})
    source += line
    py = core(env, {"units": metadata["units"], "queries": metadata["queries"]})
    q = py.questions[0]
    proof = prove_entailment(py.env, py._caller_premises(), And(py.presupposition(q), py.correct(q, "yes")))
    assert proof.status == "Found"
    metadata["answers"][0]["evidence"]["certificate"] = proof.certificate
    old = FrozenSource(metadata, source.encode(), {})
    new = SpeechSource(metadata, source.encode(), {})
    assert old.answer_lines == new.answer_lines
    assert new.answer_lines[0]["premises"]["status"] == "INCONSISTENT"
    assert new.answer_lines[0]["vacuous"] == "yes"


def test_lean_only_record_kinds_are_available_with_their_evidence():
    from test_speech_source_lean import done_document, judged, nominated
    from ve.errors import VEError

    nomination = {"question": "r", "by": "alice", "support": "testimony", "nominate": 1}
    for kind, (metadata, source) in {
        "gap": judged(base_env()),
        "external": done_document(base_env()),
        "nomination": nominated([nomination]),
    }.items():
        with pytest.raises(VEError):
            FrozenSource(metadata, source.encode(), {})
        new = SpeechSource(metadata, source.encode(), {})
        if kind == "gap":
            assert new.answer_lines[0]["status"] == "gap"
            assert new.answer_lines[0]["line"].startswith("gap (model ")
        elif kind == "external":
            assert new.compliance_lines == [{"command": "u1", "unit": "d",
                                             "line": "external: unit d (observation)"}]
        else:
            assert new.report["nominations"][0]["narrowing"]["keeps"] == ["r2"]


def test_cli_shows_checked_nomination(tmp_path):
    from test_speech_source_lean import nominated

    metadata, source = nominated([{"question": "r", "by": "alice", "support": "testimony", "nominate": 1}])
    path = tmp_path / "speech.ve.md"
    path.write_text("---\n" + json.dumps(metadata) + "\n---\n" + source)
    done = subprocess.run([sys.executable, "-m", "ve", "speech-acts", str(path)],
                          capture_output=True, text=True, timeout=HANG_TIMEOUT)
    assert done.returncode == 0, done.stderr
    result = json.loads(done.stdout)
    assert result["nominations"][0]["narrowing"]["keeps"] == ["r2"]
