import pytest

import ve.authoring as authoring
from ve.authoring import AuthoringRequest, gatekeep
from ve.environment import Environment, LANGUAGE, PROFILE, SPEC_REVISION
from ve.errors import ResourceLimit
from ve.limits import MAX_SOURCE_BYTES


@pytest.fixture
def env():
    return Environment.from_dict({
        "language": LANGUAGE,
        "profile": PROFILE,
        "spec_revision": SPEC_REVISION,
        "vocabulary": {
            "sorts": {
                "service": {"description": "service"},
                "person": {"description": "person"},
            },
            "predicates": {
                "deployed": {"arguments": ["service"], "description": "deployed"},
            },
            "constants": {
                "api": {"sort": "service", "description": "the API"},
                "alice": {"sort": "person", "description": "Alice"},
            },
        },
    })


def test_gatekeeper_repairs_with_located_stable_diagnostic(env):
    requests = []

    def propose(request):
        requests.append(request)
        if request.round == 1:
            return "@missing is deployed.\n"
        assert request.previous_text == "@missing is deployed.\n"
        assert request.diagnostic.code == "UnknownSymbol"
        assert request.diagnostic.span.line == 1
        assert request.diagnostic.span.column == 2
        assert "declared" in request.diagnostic.repair_hint
        return "@api is deployed.\n"

    result = gatekeep(env, propose, max_rounds=3)

    assert result.accepted
    assert result.text == "@api is deployed.\n"
    assert result.canonical_text == result.text
    assert result.document is not None
    assert [item.accepted for item in result.rounds] == [False, True]
    assert result.acceptance_rate == 0.5
    assert requests[0] == AuthoringRequest(1, None, None)
    assert result.rounds[0].to_dict()["diagnostic"]["code"] == "UnknownSymbol"


def test_gatekeeper_exhaustion_preserves_every_raw_proposal(env):
    proposals = iter(["true.\n\n", "x is deployed.\n"])
    result = gatekeep(env, lambda request: next(proposals), max_rounds=2)

    assert not result.accepted
    assert result.text == "x is deployed.\n"
    assert result.document is None
    assert result.canonical_text is None
    assert result.acceptance_rate == 0.0
    assert [item.text for item in result.rounds] == ["true.\n\n", "x is deployed.\n"]
    assert [item.diagnostic.code for item in result.rounds] == [
        "SyntaxError", "UnboundVariable",
    ]


def test_valid_noncanonical_binder_is_accepted_and_canonical_form_exposed(env):
    raw = "there exists service svc, (svc is deployed).\n"
    result = gatekeep(env, lambda request: raw, max_rounds=1)

    assert result.accepted
    assert result.text == raw
    assert result.canonical_text == "there exists service x0, (x0 is deployed).\n"


def test_type_mismatch_and_multiline_location_are_reported(env):
    proposals = iter(["@api equals @alice.\n", "true.\n@missing is deployed.\n"])
    result = gatekeep(env, lambda request: next(proposals), max_rounds=2)

    first, second = (item.diagnostic for item in result.rounds)
    assert first.code == "TypeMismatch"
    assert "sorts" in first.repair_hint
    assert second.code == "UnknownSymbol"
    assert (second.span.line, second.span.column) == (2, 2)


def test_source_limit_rejection_is_located(env):
    oversized = "x" * (MAX_SOURCE_BYTES + 1)
    result = gatekeep(env, lambda request: oversized, max_rounds=1)

    diagnostic = result.rounds[0].diagnostic
    assert not result.accepted
    assert diagnostic.code == "ResourceLimit"
    assert diagnostic.span.start == diagnostic.span.end == 0
    assert (diagnostic.span.line, diagnostic.span.column) == (1, 1)
    assert "Shorten" in diagnostic.repair_hint


def test_canonical_render_failure_is_a_repairable_rejection(env, monkeypatch):
    def fail_to_render(env, document):
        raise ResourceLimit("canonical form exceeds source limit")

    monkeypatch.setattr(authoring, "print_document", fail_to_render)
    result = gatekeep(env, lambda request: "true.\n", max_rounds=1)

    assert not result.accepted
    assert result.rounds[0].diagnostic.code == "ResourceLimit"
    assert result.rounds[0].text == "true.\n"


@pytest.mark.parametrize("rounds", [0, -1, True, 1.5])
def test_max_rounds_must_be_positive_integer(env, rounds):
    with pytest.raises(ValueError):
        gatekeep(env, lambda request: "true.\n", max_rounds=rounds)


def test_proposer_contract_errors_are_not_mislabeled_as_ve_rejections(env):
    with pytest.raises(TypeError, match="return str"):
        gatekeep(env, lambda request: b"true.\n")

    def unavailable(request):
        raise RuntimeError("provider unavailable")

    with pytest.raises(RuntimeError, match="provider unavailable"):
        gatekeep(env, unavailable)


def test_invalid_environment_fails_before_proposal_is_called():
    called = False

    def propose(request):
        nonlocal called
        called = True
        return "true.\n"

    with pytest.raises(TypeError, match="validated Environment"):
        gatekeep(object(), propose)
    assert not called
