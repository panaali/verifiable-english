"""pf-f16-without-fix: the condition tests of the PF f16-without round (architect ruling pf-f16-without-n2-20261116,
reading (c), signed by the DRI 2026-11-16; PLAN 12 item 30).

N2 decides which rule wins where RS6=req and RS7=noinput meet; the clause's own "i.e." limit decides where they meet:
a decision with no SAG recommendation given. So f16-without-noinput reads "need not ... if leadership_decision,
unless sag_recommendations_given", f16-without-nodelib "need not ... if leadership_decision", and run.py witness_for
tries the overriding exception's own `unless` atoms before every atom. Each test below is one condition of the task
(a to g); the answers come from results.json or from a live query on the Lean service.
"""
import json

import pytest

from tests.test_pf_f7_timed_act import SNAPSHOT as F7_SNAPSHOT
from tests.test_pf_f7_timed_act import guard_atoms
from tests.test_pf_fidelity_fix import LEAN_SERVICE, PF, REPO, R, T, key_item, pf  # noqa: F401 (pf is a fixture)

needs_lean = pytest.mark.skipif(not LEAN_SERVICE.exists(), reason="the Lean service is not built")

SNAPSHOT = REPO / "docs/usecases/openai-preparedness/pf-f16-without-fix/answers-at-merge-base.json"
F16 = ("f16-informed", "f16-without-noinput", "f16-without-nodelib")


def results():
    return json.loads((PF / "results.json").read_text())


def rows():
    return {row["id"]: row for row in results()["comparison"]}


def blocks():
    return {b.id: b for b in T.rule_blocks()}


def unless_atoms(block_id):
    """The base predicates of the rule's `unless` list, read entry by entry (each entry is one guard)."""
    out = {True: set(), False: set()}
    for exception in json.loads(T.parsed_rule(block_id))["unless"]:
        for negative, found in R.guard_atoms(exception).items():
            out[negative] |= found
    return out


def situation_atoms(model):
    return {atom[0] for atom in model if atom[1:] == ["s"]}


def use(mutant):
    """Run under `mutant` from empty caches, as run.py's run() does: the document cache is not keyed by the mutant."""
    R.MUTANT, R.WITHOUT_NARROWING = mutant, None
    for cached in (R.document, R.opposite_pairs, R._conflict):
        cached.cache_clear()
    R._MODELS.clear()
    R._PREMISES.clear()


@pytest.fixture
def fresh(pf):
    """Every run.py cache cleared before and after: a document or answer built under a mutant, a patched rule or a
    patched witness must not leak into another test."""
    use(None)
    yield
    use(None)


def live(id_):
    return R.verdict(R.answer(key_item(id_)))


def selects(predicate, choice, extra):
    """The rule names VE selects for `predicate` on the model {extra situation atoms} plus every level reached, under
    `choice` over BASE, for each completion default."""
    choice = {**R.BASE, **choice}
    names_ = tuple(sorted(choice.items()))
    situation = {n for n, d in R.vocabulary()["vocabulary"]["predicates"].items()
                 if "regulated" not in d and d["arguments"] == ["situation"]}
    base = {a for a in R.atoms({"id": "probe", "levels": list(R.LEVEL_IDS), "activity": None, "findings": {}}, choice)
            if a[0] not in situation}
    found = frozenset(base | {(n, "s") for n in extra})
    return {default: {r.name for r in R.pick(R.document(names_, default), found, predicate,
                                              (R.subject(predicate)[1],))}
            for default in ("deny", "allow")}


# --- (a) N3 and the three witnesses -----------------------------------------------------------------------------

def test_a_n3_is_none_in_results():
    """N3 (a witness model for every F1-F17 rule) is NONE, as the frozen key says; the run's witnesses for the f16 rules
    are the models the ruling measured."""
    n3 = rows()["N3"]
    assert n3["ve"] == n3["key"] == "NONE"
    witnesses = results()["items"]["N3"]["witnesses"]
    assert "sag_recommendations_given" in situation_atoms(witnesses["f16-informed"])
    for block_id in ("f16-without-noinput", "f16-without-nodelib"):
        assert situation_atoms(witnesses[block_id]) == {"leadership_decision"}


@needs_lean
def test_a_witness_for_returns_a_model_for_each_f16_rule(fresh):
    """Live: witness_for finds f16-informed on a decision with SAG recommendations given, and both f16-without rules on
    a decision with neither `sag_recommendations_given` nor `decided_without_sag`."""
    models = {block_id: R.witness_for(blocks()[block_id]) for block_id in F16}
    assert all(model is not None for model in models.values()), models
    assert "sag_recommendations_given" in situation_atoms(models["f16-informed"])
    for block_id in ("f16-without-noinput", "f16-without-nodelib"):
        assert not situation_atoms(models[block_id]) & {"sag_recommendations_given", "decided_without_sag"}


# --- (b), (c) which rule a leadership decision selects ----------------------------------------------------------

@needs_lean
def test_b_noinput_selects_need_not_on_a_case_silent_on_sag_input(fresh):
    """RS6=req, RS7=noinput, both defaults: a leadership decision that states no SAG recommendation gets "need not"
    (architect P4; the closed world reads none stated as none given); one that states them gets S1's "must"."""
    choice = {"RS6": "req", "RS7": "noinput"}
    for picked in selects("recommendation_informed", choice, ["leadership_decision"]).values():
        assert "f16-without-noinput" in picked and "f16-informed" not in picked
    for picked in selects("recommendation_informed", choice,
                          ["leadership_decision", "sag_recommendations_given"]).values():
        assert "f16-informed" in picked and "f16-without-noinput" not in picked


@needs_lean
def test_c_nodelib_selects_on_every_leadership_decision(fresh):
    """RS7=nodelib: "need not have the SAG take part" holds on a leadership decision, with no further condition."""
    for picked in selects("sag_participation", {"RS7": "nodelib"}, ["leadership_decision"]).values():
        assert "f16-without-nodelib" in picked


# --- (d) C2, C-doc, m6 and the narrowing reruns -----------------------------------------------------------------

def test_d_c2_and_c_doc_mutants_and_narrowings_in_results():
    """C2 and C-doc stay NONE; every mutant stays exact with its merge-base change set; without N2 exactly C-doc and C2
    change, C2 to SOME(RS6=req&RS7=noinput); without N1 the same 35 items change as at the merge base, N3 among them."""
    data, snapshot = results(), json.loads(SNAPSHOT.read_text())
    assert rows()["C2"]["ve"] == rows()["C-doc"]["ve"] == "NONE"
    assert {k: (m["changed"], m["exact"]) for k, m in data["mutants"].items()} == {
        k: (m["changed"], m["exact"]) for k, m in snapshot["mutants"].items()}
    assert all(m["exact"] for m in data["mutants"].values())
    assert data["mutants"]["m6"]["changed"] == ["C-doc", "C2"]
    n2 = data["without_narrowings"]["N2"]["changed"]
    assert sorted(n2) == ["C-doc", "C2"] and n2["C2"]["without"] == "SOME(RS6=req&RS7=noinput)"
    n1 = set(data["without_narrowings"]["N1"]["changed"])
    assert n1 == set(snapshot["without_narrowings"]["N1"]) and len(n1) == 35 and "N3" in n1


@needs_lean
def test_d_m6_moves_c2_and_c_doc_live(fresh):
    """Live, as PLAN m6: removing N2's precedence makes C2 SOME(RS6=req&RS7=noinput) and moves C-doc off NONE."""
    assert live("C2") == "NONE"
    use("m6")
    assert live("C2") == "SOME(RS6=req&RS7=noinput)"
    assert live("C-doc") != "NONE"


# --- (e) moved ---------------------------------------------------------------------------------------------------

def test_e_no_answer_moved_against_the_key_and_the_merge_base():
    """Every keyed answer equals the merge-base one (this round's snapshot and the f7 round's), the key column equals
    answer-key.json, and VE agrees with the key on 236 of 239, as on main."""
    current = rows()
    key = {item["id"]: item["key"] for item in json.loads((PF / "answer-key.json").read_text())["items"]}
    for path in (SNAPSHOT, F7_SNAPSHOT):
        snapshot = json.loads(path.read_text())["answers"]
        assert len(snapshot) == len(current) == len(key) == 239
        assert {i: s["key"] for i, s in snapshot.items()} == key == {i: r["key"] for i, r in current.items()}
        assert sorted(i for i, s in snapshot.items() if current[i]["ve"] != s["ve"]) == []
    assert sum(r["agree"] for r in current.values()) == 236


# --- (f) the guards ----------------------------------------------------------------------------------------------

def test_f_guards_drop_decided_without_sag_and_noinput_names_its_limit():
    for block_id in ("f16-without-noinput", "f16-without-nodelib"):
        assert "decided_without_sag" not in guard_atoms(block_id)
    assert unless_atoms("f16-without-noinput") == {False: {"sag_recommendations_given"}, True: set()}


# --- (g) witness_for's exception attempt ----------------------------------------------------------------------------

def attempts(block_id):
    rule = json.loads(T.parsed_rule(block_id))
    names, unless = R.guard_atoms(rule["guard"]), R.guard_atoms(rule["unless"])
    return R.witness_attempts(blocks()[block_id], names, names[True] | unless[False] | unless[True], {"every"})


def test_g_only_f16_informed_has_the_exception_attempt(fresh):
    """(ii) On the current rules the attempt exists for f16-informed alone (F11's exceptions add no atom the f2 rules
    do not already name), and it adds exactly noinput's `unless` atom."""
    have = {b: attempts(b) for b in blocks()}
    assert sorted(b for b, a in have.items() if len(a) == 3) == ["f16-informed"]
    first, second, _ = have["f16-informed"]
    assert second - first == {"sag_recommendations_given"}


@needs_lean
def test_g_f16_informed_is_witnessed_by_the_exception_attempt(fresh):
    """(ii) f16-informed's witness is the second attempt's model exactly: its guard atom plus the exception's limit."""
    model = R.witness_for(blocks()["f16-informed"])
    assert situation_atoms(model) == {"leadership_decision", "sag_recommendations_given"}


@needs_lean
def test_g_an_exception_whose_limit_contradicts_the_guard_gives_no_witness(fresh, monkeypatch):
    """(i) Negative: with f16-informed's guard patched to require that no SAG recommendation was given, noinput's
    `unless` atom is one the guard negates, so the attempt is skipped (never sets a negated atom) and, noinput
    overriding f16-informed on every case the guard admits, no witness exists."""
    parsed = T.parsed_rule

    def patched(block_id):
        if block_id != "f16-informed":
            return parsed(block_id)
        rule = json.loads(parsed(block_id))
        rule["guard"] = ["and", rule["guard"], ["not", ["unary", "sag_recommendations_given", ["var", 0]]]]
        return json.dumps(rule)
    monkeypatch.setattr(T, "parsed_rule", patched)
    assert len(attempts("f16-informed")) == 2
    assert R.witness_for(blocks()["f16-informed"]) is None


@needs_lean
def test_g_decided_without_sag_is_inert_in_the_c2_witness(fresh, monkeypatch):
    """(iii) No rule reads `decided_without_sag`: C2 and C-doc give the same verdict with it removed from WITNESS["C2"],
    with N2, and C2 without it (m6, where the witness must still show the conflict). The verdicts with the atom are
    results.json's (run with WITNESS as committed)."""
    assert "decided_without_sag" in R.WITNESS["C2"]
    data = results()
    with_atom = {None: (rows()["C2"]["ve"], rows()["C-doc"]["ve"]), "m6": data["mutants"]["m6"]["changes"]["C2"]["to"]}
    assert with_atom == {None: ("NONE", "NONE"), "m6": "SOME(RS6=req&RS7=noinput)"}
    monkeypatch.setitem(R.WITNESS, "C2", tuple(a for a in R.WITNESS["C2"] if a != "decided_without_sag"))
    use(None)
    assert (live("C2"), live("C-doc")) == with_atom[None]
    use("m6")
    assert live("C2") == with_atom["m6"]
