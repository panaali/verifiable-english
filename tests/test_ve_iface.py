import random

import pytest

from ve_experiments.ve_iface import StubBackend, VeBackend, backend_name, get_backend

ENV = {
    "language": "ve.core@0", "profile": "relational-fol@0", "spec_revision": "ve-v0-draft-2026-09-20",
    "vocabulary": {
        "sorts": {"person": {"description": "p"}, "service": {"description": "s"}},
        "predicates": {
            "deployed": {"arguments": ["service"], "description": "d"},
            "reviewed": {"arguments": ["service"], "description": "r"},
            "owns": {"arguments": ["person", "service"], "description": "o"},
        },
        "constants": {},
    },
}  # fmt: skip
VOCAB = ENV["vocabulary"]
S1 = ["exists", "service", ["unary", "deployed", ["var", 0]]]
S2 = ["forall", "service", ["implies", ["unary", "deployed", ["var", 0]], ["exists", "person", ["binary", "owns", ["var", 0], ["var", 1]]]]]
S3 = ["forall", "service", ["implies", ["unary", "deployed", ["var", 0]], ["unary", "reviewed", ["var", 0]]]]
MODEL = {
    "complete": True,
    "domains": {"person": ["alice"], "service": ["api"]},
    "constants": {},
    "relations": {"deployed": [["api"]], "reviewed": [["api"]], "owns": [["alice", "api"]]},
}
BACKENDS = [StubBackend(), VeBackend(ENV)]


def test_get_backend_is_the_real_adapter_and_never_a_silent_stub():
    assert backend_name() == "ve"
    assert get_backend(ENV).name == "ve"
    with pytest.raises(ValueError):
        get_backend()


@pytest.mark.parametrize("b", BACKENDS, ids=lambda b: b.name)
def test_strict_rendering_matches_the_spec_worked_example(b):
    assert b.render(S1) == "there exists service x0, (x0 is deployed)."
    assert b.render(S2) == "for every service x0, (if (x0 is deployed), then (there exists person x1, (x1 owns x0)))."


@pytest.mark.parametrize("b", BACKENDS, ids=lambda b: b.name)
def test_evaluation_matches_the_spec_worked_example(b):
    assert all(b.evaluate(s, MODEL) for s in (S1, S2, S3))
    assert not b.evaluate(S3, {**MODEL, "relations": {**MODEL["relations"], "reviewed": []}})
    assert not b.evaluate(S2, {**MODEL, "relations": {**MODEL["relations"], "owns": []}})
    empty = {"complete": True, "domains": {"person": [], "service": []}, "constants": {},
             "relations": {"deployed": [], "reviewed": [], "owns": []}}  # fmt: skip
    assert not b.evaluate(S1, empty) and b.evaluate(S2, empty) and b.evaluate(S3, empty)


@pytest.mark.parametrize("b", BACKENDS, ids=lambda b: b.name)
def test_countermodel_search(b):
    cm = b.find_countermodel([S2], S3, VOCAB, max_domain=1)
    assert cm is not None and b.evaluate(S2, cm) and not b.evaluate(S3, cm)
    assert b.find_countermodel([S3, S1], ["exists", "service", ["unary", "reviewed", ["var", 0]]], VOCAB, max_domain=1) is None


def test_stub_and_real_evaluators_agree_on_random_models():
    stub, real = BACKENDS
    rng = random.Random(0)
    for _ in range(100):
        dom = {"person": [f"p{i}" for i in range(rng.randint(0, 2))], "service": [f"s{i}" for i in range(rng.randint(0, 2))]}
        rel = {"deployed": [[s] for s in dom["service"] if rng.random() < 0.5], "reviewed": [[s] for s in dom["service"] if rng.random() < 0.5],
               "owns": [[p, s] for p in dom["person"] for s in dom["service"] if rng.random() < 0.5]}  # fmt: skip
        m = {"complete": True, "domains": dom, "constants": {}, "relations": rel}
        for f in (S1, S2, S3):
            assert stub.evaluate(f, m) == real.evaluate(f, m)


def test_distinguishing_model():
    real = VeBackend(ENV)
    m = real.find_distinguishing_model(S2, S3)
    assert m is not None and real.evaluate(S2, m) != real.evaluate(S3, m)
    assert real.find_distinguishing_model(S2, S2, max_models=300) is None
