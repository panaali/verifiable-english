"""The 11b public projection against the frozen pre-switch W2 checker."""
from __future__ import annotations

import pytest

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
