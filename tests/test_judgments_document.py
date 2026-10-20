"""`judgments@0` in Lean's `document` mode (judgment-terms-PLAN.md JT-2; docs/spec/judgment-terms.md 8): the
fixtures of spec 11.2 and 11.3 replayed through the service, with the values the spec computed in its stub.

Each row is one `ve-document@1` text over spec 11's environment (J-ω's over its own). The rows marked *internal* in
the spec are inputs W2 refuses on the wire, so they are not here (11). Lean decides every value; this file only
sends the documents and compares Lean's answer with the spec's.
"""
from __future__ import annotations

from copy import deepcopy
import json

import pytest

from conformance.p0 import LANGUAGE, SPEC_REVISION
from ve.backends.lean_service import LeanService
from ve.wire import digest

PROFILES = ["definitions@0", "documents@1", "judgments@0", "norms@0", "relational-fol@0"]


def u(p, i=0):
    return ["unary", p, ["var", i]]


def conj(*fs):
    out = fs[-1]
    for f in reversed(fs[:-1]):
        out = ["and", f, out]
    return out


def regulated(act, *args):
    return {"arguments": list(args), "description": "regulated",
            "regulated": {"role": "permission", "default": "deny", "act": act}}


def defined(body):
    return {"arguments": ["act"], "description": "defined", "defined": {"arguments": ["act"], "body": body}}


ACTS = ["arrest", "arbitrary", "unreasonable", "detention", "unlawful", "court_ordered", "gives_serious_uplift",
        "deprivation", "denial"]
VOCAB = {
    "sorts": {s: {"description": s} for s in ("person", "act", "thing")},
    "predicates": {**{p: {"arguments": ["act"], "description": p} for p in ACTS},
                   "natural_and_fundamental_group_unit": {"arguments": ["thing"], "description": "unit"},
                   "treats_unfairly": {"arguments": ["person", "person"], "description": "unfair"},
                   "subjects": regulated("{0} prevent {1}", "person", "act"),
                   "reports": regulated("{0} help {1}", "person", "act"),
                   "make_reasonable_efforts": regulated("{0} do y to {1}", "person", "act"),
                   "wrongful_detention": defined(conj(u("detention"), u("arbitrary"))),
                   "unlawful_detention": defined(conj(u("unlawful"), u("detention")))},
    "constants": {"the_family": {"sort": "thing", "description": "the family"}}}
# J-ω's environment (spec 11): two sorts of `arbitrary`, each regulated act over its own sort.
OMEGA = {
    "sorts": {s: {"description": s} for s in ("person", "measure", "interference")},
    "predicates": {"measure_taken": {"arguments": ["measure"], "description": "taken"},
                   "interference_with_privacy": {"arguments": ["interference"], "description": "privacy"},
                   "arbitrary_measure": {"arguments": ["measure"], "description": "arbitrary"},
                   "arbitrary_interference": {"arguments": ["interference"], "description": "arbitrary"},
                   "subjects_to_measure": regulated("{0} prevent {1}", "person", "measure"),
                   "subjects_to_interference": regulated("{0} help {1}", "person", "interference")},
    "constants": {}}


def environment(vocabulary=VOCAB, profiles=PROFILES):
    return {"language": LANGUAGE, "profiles": list(profiles), "spec_revision": SPEC_REVISION,
            "vocabulary": deepcopy(vocabulary)}


def record(name, *args, decided_by="unresolved_decider", necessary=(), sufficient=(), factors=()):
    return {"name": name, "arguments": list(args or ("act",)), "decided_by": decided_by,
            "necessary": list(necessary), "sufficient": list(sufficient), "factors": list(factors),
            "precedents": [], "jurisdiction": "document", "version": 1}


def norm(guard, predicate="subjects", name="r"):
    return {"norm": {"name": name, "predicate": predicate, "sign": False, "guard": guard, "unless": [], "over": []}}


# A rule on `subjects` is typed in [act, person]: the act is variable 0 (spec 11).
ALPHA = norm(conj(u("arrest"), u("arbitrary")))
UPSILON = ["forall", "act", ["implies", conj(u("arrest"), u("arbitrary")), ["bottom"]]]
WIDE = ["forall", "act", ["implies", conj(["or", u("deprivation"), u("denial")], u("arbitrary")), ["bottom"]]]
NARROW = ["forall", "act", conj(["implies", conj(u("deprivation"), u("arbitrary")), ["bottom"]],
                                ["implies", u("denial"), ["bottom"]])]


def unit(uid, meaning="specified", content=None, kind=None):
    kind = kind or ("norm" if content and "norm" in content else "asserted" if content else "explanation")
    return {"id": uid, "kind": kind, "meaning": meaning, "support": "assumption",
            **({"content": content} if content else {})}


def opened(*names):
    return {"open": list(names)}


def bound(sets, environment_id, profiles):
    """The sets with the identities W2 checks (`Loader.compileReading`, `Loader.modelId`), over the environment id
    Lean's `environment` mode answered."""
    version = "v0.2:" + ",".join(profiles)
    model_id = digest(f"ve-model-{version}\n", {"environment_id": environment_id, "model": MODEL})
    out = deepcopy(list(sets))
    for s in out:
        for r in s["readings"]:
            if r["content"] is not None:
                r["meaning_id"] = digest(f"ve-meaning-{version}\n",
                                         {"environment_id": environment_id, "ast": r["content"]})
            r["admission"]["distinguishing_models"] = dict.fromkeys(r["admission"]["distinguishing_models"], model_id)
        if "models" in s:
            s["models"] = {model_id: MODEL}
    return out


def document(service, units, records, *, sets=(), vocabulary=VOCAB, profiles=PROFILES):
    """The text of a document whose units are one line each, over `vocabulary` with `profiles`."""
    env = environment(vocabulary, profiles)
    if sets:
        row = service.run("environment", [{"id": "e", "environment": env}])[0]
        sets = bound(sets, row["environment_id"], profiles)
    lines, cursor, placed = [], 0, []
    for item in units:
        line = f"Unit {item['id']}.\n"
        placed.append({**item, "span": [cursor, cursor + len(line)]})
        lines.append(line)
        cursor += len(line)
    front = {"format": "ve-document@1", "environment": env, "units": placed,
             "open_terms": list(records), **({"reading_sets": list(sets)} if sets else {})}
    return "---\n" + json.dumps(front) + "\n---\n" + "".join(lines)


# J-ξ′'s distinguishing model: one act, `denial` true, `deprivation` and `arbitrary` false (wide true, narrow false).
MODEL = {"complete": True, "domains": {"person": ["p"], "act": ["a"], "thing": ["t"]},
         "constants": {"the_family": "t"},
         "relations": {**{p: [] for p in ACTS}, "denial": [["a"]], "natural_and_fundamental_group_unit": [],
                       "treats_unfairly": [], "subjects": [], "reports": [], "make_reasonable_efforts": []}}


def reading(rid, ast, others=()):
    """A reading; `bound` fills its identities."""
    return {"id": rid, "kind": "asserted", "meaning_id": "pending", "content": ast,
            "admission": {"who": "reviewer", "why": "a recorded reading",
                          "distinguishing_models": dict.fromkeys(others)}}


def authored(unit_id, ast):
    return {"id": "s", "unit": unit_id, "version": 1, "status": "authored", "signature": "reviewer",
            "readings": [reading("only", ast)]}


def open_set(unit_id, *asts):
    ids = [f"r{i}" for i in range(len(asts))]
    return {"id": "s", "unit": unit_id, "version": 1, "status": "open",
            "readings": [reading(rid, ast, [o for o in ids if o != rid]) for rid, ast in zip(ids, asts)],
            **({"models": {}} if len(asts) > 1 else {})}


J1 = [record("arbitrary")]
J2 = [record("arbitrary"), record("unreasonable")]

# Spec 11.2: admission, in record order, each record's first failing check.
ADMISSION = {
    "J-alpha": (J1, "ok"),
    "J-delta": ([record("reasonable_limitation")], "JudgmentUnbound: reasonable_limitation"),
    "J-pi": ([record("wrongful_detention")], "JudgmentUnbound: wrongful_detention"),
    "J-epsilon": ([record("arbitrary", "person")], "JudgmentArguments: arbitrary"),
    "J-rho": ([record("subjects", "person", "act")], "JudgmentRegulated: subjects"),
    "J-zeta": ([record("arbitrary", necessary=[UPSILON])], "JudgmentCriterionAsUnit: arbitrary"),
    "J-zeta-prime": ([record("arbitrary", sufficient=[UPSILON, UPSILON])], "JudgmentCriterionAsUnit: arbitrary"),
    "J-eta": ([record("arbitrary", decided_by="unstated")], "JudgmentDecider: arbitrary"),
    "J-omicron": ([record("treats_unfairly", "person", "person")], "ok"),
    "J-nu": ([record("gives_serious_uplift")], "ok"),
    "J-theta": ([record("natural_and_fundamental_group_unit", "thing")], "ok"),
    "order-1": ([record("arbitrary"), record("reasonable_limitation"), record("unreasonable", "person")],
                "JudgmentUnbound: reasonable_limitation"),
    "order-2": ([record("arbitrary", "person", decided_by="unstated", necessary=[UPSILON])],
                "JudgmentArguments: arbitrary"),
}

# Spec 11.3 and 11.9: (records, units, reading sets) -> each unit's status and the usage map, or the refusal.
STATUS = {
    "J-alpha": (J1, [unit("u1", opened("arbitrary"), ALPHA)], (), ["OPEN"], ([("arbitrary", ["u1"])], [])),
    "J-beta": (J1, [unit("u1", content=ALPHA)], (), "JudgmentNotChecked: u1 arbitrary", None),
    "J-gamma": (J1, [unit("u1", content={"ast": ["forall", "act", ["implies", u("wrongful_detention"),
                                                                   ["not", u("court_ordered")]]]})], (),
                "JudgmentNotChecked: u1 arbitrary", None),
    "J-gamma-prime": (J1, [unit("u1", content=norm(u("wrongful_detention")))], (),
                      "JudgmentNotChecked: u1 arbitrary", None),
    "J-gamma-second": (J1, [unit("u1", content={"ast": ["forall", "act", ["implies", u("unlawful_detention"),
                                                                          ["not", u("court_ordered")]]]})], (),
                       ["CHECKED"], ([], ["arbitrary"])),
    "J-theta": ([record("natural_and_fundamental_group_unit", "thing")],
                [unit("u1", opened("natural_and_fundamental_group_unit"),
                      {"ast": ["unary", "natural_and_fundamental_group_unit", ["const", "the_family"]]})], (),
                ["OPEN"], ([("natural_and_fundamental_group_unit", ["u1"])], [])),
    "J-mu": (J1, [unit("u1", content=norm(u("arrest")))], (), ["CHECKED"], ([], ["arbitrary"])),
    "J-xi": (J1, [unit("u055", opened("arbitrary"), kind="asserted")],
             [authored("u055", ["forall", "act", ["implies", conj(u("deprivation"), u("arbitrary")), ["bottom"]]])],
             ["OPEN"], ([("arbitrary", ["u055"])], [])),
    "J-xi-prime": (J1, [unit("u055", opened("arbitrary"), kind="asserted")], [open_set("u055", WIDE, NARROW)],
                   ["OPEN"], ([("arbitrary", ["u055"])], [])),
    "J-upsilon": (J1, [unit("u1", {"contextual": "a quoted rule"}, {"ast": UPSILON})], (), ["OPEN"],
                  ([("arbitrary", ["u1"])], [])),
    "J-sigma": (J2, [unit("u1", opened("arbitrary"), norm(conj(u("arrest"), u("arbitrary"), u("unreasonable"))))],
                (), "JudgmentNotListed: u1 unreasonable", None),
    "J-tau": (J2, [unit("u1", opened("arbitrary", "unreasonable"), ALPHA)], (),
              "JudgmentListedUnused: u1 unreasonable", None),
    "J-tau-prime-a": (J2, [unit("u1", opened("arbitrary", "unreasonable"))], (), ["OPEN"],
                      ([], ["arbitrary", "unreasonable"])),
    "J-tau-prime-b": (J2, [unit("u1", opened("arbitrary", "unreasonable"), kind="asserted")],
                      [open_set("u1", None, None)], ["OPEN"], ([], ["arbitrary", "unreasonable"])),
    "J-tau-prime-c": (J2, [unit("u1", opened("arbitrary", "unreasonable"), kind="asserted")],
                      [open_set("u1", UPSILON, None)], ["OPEN"], ([("arbitrary", ["u1"])], ["unreasonable"])),
    "J-tau-prime-d": (J2, [unit("u1", opened("arbitrary", "unreasonable"), ALPHA)], [open_set("u1", None)],
                      ["OPEN"], ([], ["arbitrary", "unreasonable"])),
    "J-tau-prime-e": (J2, [unit("u1", opened("arbitrary", "unreasonable"), kind="asserted")],
                      [authored("u1", UPSILON)], "JudgmentListedUnused: u1 unreasonable", None),
    "J-chi": (J1, [unit("u1", opened("arbitrary"), ALPHA),
                   unit("u2", content=norm(["binary", "subjects", ["var", 1], ["var", 0]], "reports", "q"))], (),
              ["OPEN", "CHECKED"], ([("arbitrary", ["u1"])], [])),
    # Which judgment a refusal names, and both lists' order, with two candidates each (spec 8.2, 8.3).
    "two-specified": (J2, [unit("u1", content=norm(conj(u("arrest"), u("unreasonable"), u("arbitrary"))))], (),
                      "JudgmentNotChecked: u1 arbitrary", None),
    "two-unlisted": (J2 + [record("gives_serious_uplift")],
                     [unit("u1", opened("gives_serious_uplift"),
                           norm(conj(u("unreasonable"), u("arbitrary"), u("gives_serious_uplift"))))], (),
                     "JudgmentNotListed: u1 arbitrary", None),
    "two-unused": (J2, [unit("u1", opened("unreasonable", "arbitrary"), norm(u("arrest")))], (),
                   "JudgmentListedUnused: u1 unreasonable", None),
    "two-rows": (J2 + [record("gives_serious_uplift"), record("court_ordered")],
                 [unit("u1", opened("unreasonable"), norm(conj(u("arrest"), u("unreasonable")))),
                  unit("u2", opened("unreasonable", "arbitrary"), norm(conj(u("unreasonable"), u("arbitrary")), name="s"))],
                 (), ["OPEN", "OPEN"],
                 ([("arbitrary", ["u2"]), ("unreasonable", ["u1", "u2"])], ["gives_serious_uplift", "court_ordered"])),
}


@pytest.fixture(scope="module")
def service():
    with LeanService() as instance:
        yield instance


def answer(service, text):
    return service.run("document", [{"id": "d", "document": text, "admit": False}])[0]


def outcome(row):
    """A refusal's text, or each unit's status and the usage map as pairs."""
    if row["status"] == "error":
        return row["error"], None
    usage = row.get("judgments")
    return ([u["status"] for u in row["units"]],
            None if usage is None else ([(t["term"], t["units"]) for t in usage["used"]], usage["unused"]))


@pytest.mark.parametrize("name", ADMISSION)
def test_admission_of_each_record_in_record_order(service, name):
    records, expected = ADMISSION[name]
    text = document(service, [unit("u1", kind="meta")], records)
    got = outcome(answer(service, text))
    if expected == "ok":
        assert got == (["LABELLED"], ([], [r["name"] for r in records]))
    else:
        assert got == (expected, None)


@pytest.mark.parametrize("name", STATUS)
def test_status_and_usage_of_each_unit(service, name):
    records, units, sets, statuses, usage = STATUS[name]
    got = outcome(answer(service, document(service, units, records, sets=sets)))
    assert got == (statuses, usage)


def test_omega_one_word_over_two_sorts_is_two_terms_with_one_row_each(service):
    """J-ω (spec 11.2, 11.3): each term has its own row, and `arbitrary_measure` over the other sort is refused."""
    measure = {"norm": {"name": "m", "predicate": "subjects_to_measure", "sign": False, "unless": [], "over": [],
                        "guard": conj(u("measure_taken"), u("arbitrary_measure"))}}
    privacy = {"norm": {"name": "i", "predicate": "subjects_to_interference", "sign": False, "unless": [],
                        "over": [], "guard": conj(u("interference_with_privacy"), u("arbitrary_interference"))}}
    records = [record("arbitrary_measure", "measure"), record("arbitrary_interference", "interference")]
    units = [unit("u037", opened("arbitrary_measure"), measure), unit("u045a", opened("arbitrary_interference"), privacy)]
    got = outcome(answer(service, document(service, units, records, vocabulary=OMEGA)))
    assert got == (["OPEN", "OPEN"], ([("arbitrary_measure", ["u037"]), ("arbitrary_interference", ["u045a"])], []))
    wrong = document(service, units[:1], [record("arbitrary_measure", "interference")], vocabulary=OMEGA)
    assert outcome(answer(service, wrong)) == ("JudgmentArguments: arbitrary_measure", None)


LEGACY = {"J-alpha": "OPEN", "J-beta": "CHECKED", "J-gamma": "CHECKED", "J-theta": "OPEN", "J-mu": "CHECKED",
          "J-xi": "CHECKED", "J-xi-prime": "OPEN", "J-upsilon": "LABELLED"}


@pytest.mark.parametrize("name", LEGACY)
def test_without_the_profile_every_answer_is_todays(service, name):
    """J-λ (spec 11.3, `status_legacy`): the same documents without `judgments@0` keep today's statuses, and the
    answer has no `judgments` field."""
    records, units, sets, _, _ = STATUS[name]
    plain = [p for p in PROFILES if p != "judgments@0"]
    row = answer(service, document(service, units, records, sets=sets, profiles=plain))
    assert outcome(row) == ([LEGACY[name]], None)
    assert set(row) == {"id", "status", "document_id", "source_id", "source", "units", "coverage"}


READINGS = PROFILES[:4] + ["readings@1", "relational-fol@0"]
DEPRIVATION = {"norm": {"name": "d", "predicate": "subjects", "sign": False, "unless": [], "over": [],
                        "guard": conj(u("deprivation"), u("arbitrary"))}}


def test_readings_sets_are_read_from_their_raw_candidates(service):
    """Under `readings@1` a set's norm candidate is read as its rule, never as `readingsSets`' `top` (spec 4.2): the
    norm variant of J-ξ uses `arbitrary`, as J-ξ's formula does."""
    rule = {**authored("u055", DEPRIVATION), "readings": [{**reading("only", DEPRIVATION), "kind": "norm"}]}
    for kind, chosen in (("norm", rule), ("asserted", STATUS["J-xi"][2][0])):
        text = document(service, [unit("u055", opened("arbitrary"), kind=kind)], J1, sets=[chosen], profiles=READINGS)
        assert outcome(answer(service, text)) == (["OPEN"], ([("arbitrary", ["u055"])], []))


PILOT = ["documents@1", "judgments@0", "norm-defaults@0", "norms@0", "readings@1", "relational-fol@0"]
PLAIN = {**VOCAB, "predicates": {k: v for k, v in VOCAB["predicates"].items() if "defined" not in v}}


@pytest.mark.parametrize("name", ["J-alpha", "J-beta", "J-mu", "J-sigma"])
def test_the_pilots_profiles_compose_with_judgments(service, name):
    """The pilots' list (norm defaults and readings) with `judgments@0`: the same answers."""
    records, units, sets, statuses, usage = STATUS[name]
    got = outcome(answer(service, document(service, units, records, sets=sets, vocabulary=PLAIN, profiles=PILOT)))
    assert got == (statuses, usage)


def test_the_profile_requires_documents_and_its_records_are_w2s(service):
    """The row requires `documents@1` (`gate_judgments`); W2's own texts come first (`records_names`)."""
    alone = [p for p in PROFILES if p != "documents@1"]
    rows = service.run("environment", [{"id": "e", "environment": environment(profiles=p)} for p in (PROFILES, alone)])
    assert rows[0]["profiles"] == PROFILES
    assert rows[1]["error"] == "UnsupportedProfile: judgments@0 requires documents@1"
    text = document(service, [unit("u1", kind="meta")], J1, profiles=alone)
    assert outcome(answer(service, text)) == ("UnsupportedProfile: judgments@0 requires documents@1", None)
    text = document(service, [unit("u1", kind="meta")], [record("arbitrary"), record("arbitrary")])
    assert outcome(answer(service, text)) == ("duplicate or invalid open term", None)


def test_layers_judgments_does_not_compose_with_are_unavailable(service):
    soft = sorted(PROFILES + ["soft-norms@0"])
    text = document(service, [unit("u1", kind="meta")], J1, profiles=soft)
    assert outcome(answer(service, text)) == (
        "CheckerUnavailable: judgments@0 with soft-norms@0 needs its composed Lean route", None)
    front, body = document(service, [unit("u1", kind="meta")], J1).split("\n---\n")
    senses = front[:-1] + ', "senses": []}\n---\n' + body
    assert outcome(answer(service, senses)) == (
        "CheckerUnavailable: judgments@0 with senses needs its composed Lean route", None)


def test_the_answer_fits_its_schema_and_models_never_see_the_profile(service):
    """The genuine answer passes the generated `document.json`; Python's model projection drops the profile."""
    from ve.backends.service_schema import check_row
    from ve.profiles import model_environment
    case = {"id": "d", "document": document(service, [unit("u1", opened("arbitrary"), ALPHA)], J1), "admit": False}
    check_row("document", service.run("document", [case])[0], case, 0)
    assert model_environment(environment())["profiles"] == [p for p in PROFILES if p != "judgments@0"]


def test_python_never_decides_a_judgments_document(service, tmp_path):
    """Python's own loader refuses the profile, and the Lean answer is not relayed before jt-2b."""
    from ve import document as D
    from ve.errors import CheckerUnavailable
    path = tmp_path / "j.ve.md"
    path.write_text(document(service, [unit("u1", opened("arbitrary"), ALPHA)], J1))
    with pytest.raises(CheckerUnavailable, match="judgments@0 documents are checked by Lean's document mode"):
        D._load_document(path.read_bytes(), path, None)
    with pytest.raises(CheckerUnavailable):
        D.load_document(path)


@pytest.mark.parametrize("name", ["J-alpha", "J-gamma-second"])
def test_the_claim_graph_is_admitted_over_the_same_environment(service, name):
    """`admit` (the claim graph): the norms route and the plain route read the environment without the layer."""
    records, units, sets, statuses, _ = STATUS[name]
    text = document(service, units, records, sets=sets)
    front, body = text.split("\n---\n")
    meta = json.loads(front[4:])
    meta["graph"] = {"root": "c", "nodes": [{"name": "c", "ast": units[0]["content"].get("ast", ["top"]),
                                              "label": "open:arbitrary"}]}
    row = service.run("document", [{"id": "d", "document": "---\n" + json.dumps(meta) + "\n---\n" + body}])[0]
    assert outcome(row)[0] == statuses
