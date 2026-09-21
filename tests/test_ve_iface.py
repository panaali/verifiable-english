from ve_experiments.ve_iface import StubBackend, get_backend

VOCAB = {
    "sorts": {"person": {}, "service": {}},
    "predicates": {
        "deployed": {"arguments": ["service"]},
        "reviewed": {"arguments": ["service"]},
        "owns": {"arguments": ["person", "service"]},
    },
    "constants": {},
}
S1 = ["exists", "service", ["unary", "deployed", ["var", 0]]]
S2 = ["forall", "service", ["implies", ["unary", "deployed", ["var", 0]], ["exists", "person", ["binary", "owns", ["var", 0], ["var", 1]]]]]
S3 = ["forall", "service", ["implies", ["unary", "deployed", ["var", 0]], ["unary", "reviewed", ["var", 0]]]]
MODEL = {
    "complete": True,
    "domains": {"person": ["alice"], "service": ["api"]},
    "constants": {},
    "relations": {"deployed": [["api"]], "reviewed": [["api"]], "owns": [["alice", "api"]]},
}


def test_strict_rendering_matches_the_spec_worked_example():
    b = StubBackend()
    assert b.render(S1) == "there exists service x0, (x0 is deployed)."
    assert b.render(S2) == "for every service x0, (if (x0 is deployed), then (there exists person x1, (x1 owns x0)))."
    assert b.render(S2, "fol") == "∀x0:service. (deployed(x0) → ∃x1:person. owns(x1, x0))"


def test_evaluation_matches_the_spec_worked_example():
    b = StubBackend()
    assert all(b.evaluate(s, MODEL) for s in (S1, S2, S3))
    assert not b.evaluate(S3, {**MODEL, "relations": {**MODEL["relations"], "reviewed": []}})
    assert not b.evaluate(S2, {**MODEL, "relations": {**MODEL["relations"], "owns": []}})
    empty = {"complete": True, "domains": {"person": [], "service": []}, "constants": {},
             "relations": {"deployed": [], "reviewed": [], "owns": []}}  # fmt: skip
    assert not b.evaluate(S1, empty) and b.evaluate(S2, empty) and b.evaluate(S3, empty)


def test_countermodel_search():
    b = StubBackend()
    cm = b.find_countermodel([S2], S3, VOCAB, max_domain=1)
    assert cm is not None and b.evaluate(S2, cm) and not b.evaluate(S3, cm)
    assert b.find_countermodel([S3, S1], ["exists", "service", ["unary", "reviewed", ["var", 0]]], VOCAB, max_domain=1) is None


def test_get_backend_falls_back_to_stub():
    assert get_backend().name in ("stub", "ve")
