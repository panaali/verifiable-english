"""Recovery state is derived by replaying recorded commands, never imported.

A ledger is accepted only when it is byte-equal to its own replay from
genesis. Tampering with any derived field (event snapshots, approvals,
revisions, versions), even with every digest recomputed, is rejected; changed
command inputs are replayed through the same checks as live calls.
"""
import hashlib
import json
import random
import time
from copy import deepcopy

import pytest

from ve.assist.ambiguity_patterns import Budget, review
from ve.assist import recovery as recovery_module
from ve.assist.recovery import RecoveryService
from ve.ast import Unary, Const, Not
from ve.identity import meaning_id
from ve.search import find_countermodel
from test_assist_recovery import environment

ENV = environment()
BINDINGS = {"discourse.reference@1": {"predicate": "safe", "antecedents": ["api", "carol"]}}
API = Unary("safe", Const("api"))
CAROL = Unary("safe", Const("carol"))
API_ID, CAROL_ID = meaning_id(ENV, API), meaning_id(ENV, CAROL)
SITUATION = find_countermodel(ENV, (), Not(API)).model.to_dict()
SELECT_API = dict(actor="translator", paraphrase="Api is safe.", presentation="Api is safe.",
                  situation=SITUATION)


def service():
    return RecoveryService(ENV, grammar_version="g1", glossary_version="v1", reading_set_version="r1")


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     separators=(",", ":")).encode()).hexdigest()


def rehash(ledger):
    """Recompute both hash chains, as an attacker editing an export would."""
    for chain, key in (("commands", "command_digest"), ("events", "event_digest")):
        previous = None
        for row in ledger.get(chain) or []:
            if isinstance(row, dict):
                row["previous_digest"] = previous
                row[key] = digest({k: v for k, v in row.items() if k != key})
                previous = row[key]
    return ledger


def rejected(ledger):
    try:
        RecoveryService.from_ledger(ENV, ledger)
    except ValueError:
        return True
    return False


# -- recheck 3, finding A1: missing snapshot fields bypass obligations ------

@pytest.mark.parametrize("field", ["readings", "pending"])
def test_import_rejects_cancel_and_start_snapshots_missing_obligation_field(field):
    recovery = service()
    recovery.add("u", "It is safe.", {}, mode="translation")
    recovery.start("u")
    if field == "readings":
        recovery.classify("u", parse_outcome="one", catalogue_bindings=BINDINGS)
    else:
        recovery.classify("u", parse_outcome="one", discourse="incomplete", catalogue_bindings=BINDINGS)
    recovery.cancel("u")
    recovery.start("u")
    ledger = recovery.to_ledger()
    cancel, start = ledger["events"][-2:]
    assert (cancel["action"], start["action"]) == ("cancel", "start")
    del cancel["unit_snapshot"][field]
    start["unit_snapshot"][field] = []
    forged = rehash(ledger)
    assert rejected(forged)
    assert not recovery.verify_ledger(forged)


@pytest.mark.parametrize("field", ["readings", "pending", "narrowings", "catalogue_results",
                                   "catalogue_reviewed", "rejected", "approval", "state"])
@pytest.mark.parametrize("mutation", ["delete", "empty"])
def test_import_rejects_missing_or_emptied_field_in_every_event(field, mutation):
    recovery = service()
    recovery.add("u", "It is safe.", {}, mode="translation")
    recovery.start("u")
    recovery.classify("u", parse_outcome="one", discourse="incomplete", catalogue_bindings=BINDINGS)
    recovery.cancel("u")
    recovery.start("u")
    recovery.classify("u", parse_outcome="one", catalogue_bindings=BINDINGS)
    recovery.resolve_pending("u", 0, actor="translator", reason="antecedent named",
                             disposition="resolved", wording="Api is safe.",
                             cited_spans=[{"start": 0, "end": 2}])
    record = recovery.record_narrowing("u", keeps=[API_ID], actor="translator", reason="cited",
                                       cited_spans=[{"start": 0, "end": 2}])
    recovery.approve("u", API, narrowing=record["id"], **SELECT_API)
    original = recovery.to_ledger()
    assert not rejected(deepcopy(original))
    for index in range(len(original["events"])):
        ledger = deepcopy(original)
        snapshot = ledger["events"][index]["unit_snapshot"]
        if mutation == "delete":
            del snapshot[field]
        elif snapshot[field] in ([], {}, None, ""):
            continue
        else:
            snapshot[field] = type(snapshot[field])()
        assert rejected(rehash(ledger)), (index, ledger["events"][index]["action"])


# -- recheck 3, finding A2: classify validation trusted altered candidates --

def test_import_rejects_classify_with_readings_and_candidates_cleared_but_card_kept():
    recovery = service()
    recovery.add("u", "It is safe.", {}, mode="translation")
    recovery.start("u")
    recovery.classify("u", parse_outcome="one", catalogue_bindings=BINDINGS)
    ledger = recovery.to_ledger()
    snapshot = ledger["events"][-1]["unit_snapshot"]
    result = snapshot["catalogue_results"]["discourse.reference@1"]
    assert len(result["cards"]) == 1 and len(snapshot["readings"]) == 2
    snapshot["readings"] = []
    result["candidates"] = []
    forged = rehash(ledger)
    assert rejected(forged)
    # Even a service that trusted this import could not approve by restarting.
    recovery.cancel("u")
    recovery.start("u")
    recovery.classify("u", parse_outcome="one", catalogue_dispositions={
        "discourse.reference@1": {"disposition": "not_applicable", "actor": "t", "reason": "r"}})
    with pytest.raises(ValueError, match="narrowing"):
        recovery.approve("u", API, **SELECT_API)


def test_restart_without_bindings_keeps_readings_and_requires_narrowing():
    recovery = service()
    recovery.add("u", "It is safe.", {}, mode="translation")
    recovery.start("u")
    recovery.classify("u", parse_outcome="one", catalogue_bindings=BINDINGS)
    recovery.cancel("u")
    recovery.start("u")
    recovery.classify("u", parse_outcome="one")
    pattern = next(i for i, row in enumerate(recovery.units["u"].pending) if row.get("pattern_id"))
    recovery.resolve_pending("u", pattern, actor="t", reason="no pronoun", disposition="not_applicable")
    assert {row["meaning_id"] for row in recovery.units["u"].readings} == {API_ID, CAROL_ID}
    with pytest.raises(ValueError, match="narrowing"):
        recovery.approve("u", API, **SELECT_API)


# -- the ledger is derived: every structural edit is rejected ---------------

def test_import_rejects_extra_missing_or_retyped_ledger_fields():
    recovery = service()
    recovery.add("u", "Api is safe.", {})
    recovery.start("u")
    recovery.classify("u", parse_outcome="one")
    recovery.approve("u", API, **SELECT_API)
    original = recovery.to_ledger()
    assert RecoveryService.from_ledger(ENV, json.loads(json.dumps(original))).approval_valid("u")
    edits = [
        lambda l: l.pop("events"),
        lambda l: l.update(extra=1),
        lambda l: l["events"][-1].update(extra=1),
        lambda l: l["events"][-1]["unit_snapshot"].update(extra=1),
        lambda l: l["events"][-1]["unit_snapshot"]["approval"]["snapshot"].update(extra=1),
        lambda l: l["events"].pop(),
        lambda l: l["commands"].pop(),
        lambda l: l["commands"][-1].pop("observed"),
        lambda l: l["commands"][-1]["observed"].update(extra=[]),
        lambda l: l["commands"][-1]["args"].update(extra=None),
        lambda l: l["commands"][-1]["args"].pop("narrowing"),
        lambda l: l["commands"][-1]["observed"]["deadlines"].append(None),
        lambda l: l.update(revision=True),
        lambda l: l["events"][-1].update(revision=float(l["events"][-1]["revision"])),
        lambda l: l["events"][-1]["unit_snapshot"].update(replies=False),
        lambda l: l["versions"].update(glossary="v2"),
        lambda l: l["genesis_versions"].update(glossary="v2"),
    ]
    for number, edit in enumerate(edits):
        ledger = deepcopy(original)
        edit(ledger)
        assert rejected(rehash(ledger)), number


def test_import_keeps_prior_deadline_layout_and_accepts_new_commands():
    recovery = service()
    recovery.add("u", "Api is safe.", {})
    recovery.start("u")
    recovery.classify("u", parse_outcome="one")
    recovery.approve("u", API, **SELECT_API)
    ledger = recovery.to_ledger()
    # Before the command-entry budget, add and start had no deadline slot.
    for command in ledger["commands"][:2]:
        command["observed"]["deadlines"] = []
    restored = RecoveryService.from_ledger(ENV, rehash(ledger))
    assert restored.approval_valid("u")
    restored.edit("u", source="Carol is safe.")
    assert restored.verify_ledger()


def test_recorded_command_failures_must_recur_on_replay():
    recovery = service()
    recovery.add("u", "Api is safe.", {})
    recovery.start("u")
    recovery.classify("u", parse_outcome="one")
    recovery.clock = lambda: 10.0 ** 12
    with pytest.raises(ValueError, match="task cap"):
        recovery.approve("u", API, **SELECT_API)
    ledger = recovery.to_ledger()
    assert ledger["commands"][-1]["error"]["message"] == "clarification task cap"
    assert RecoveryService.from_ledger(ENV, deepcopy(ledger)).units["u"].state == "unresolved"
    ledger["commands"][-1]["observed"]["now"] = recovery.units["u"].started
    assert rejected(rehash(ledger))


def test_failed_command_without_events_leaves_no_state_or_record():
    recovery = service()
    recovery.add("u", "It is safe.", {})
    recovery.start("u")
    before = (deepcopy(recovery.to_ledger()), deepcopy(recovery.units["u"]))
    with pytest.raises(ValueError, match="disposition"):
        recovery.classify("u", parse_outcome="one", pending=[{"reason": "author check"}],
                          catalogue_dispositions={"discourse.reference@1": {"disposition": "maybe"}})
    assert (recovery.to_ledger(), recovery.units["u"]) == before
    assert recovery.verify_ledger()


def test_in_memory_state_must_equal_the_replayed_ledger():
    recovery = service()
    recovery.add("u", "It is safe.", {})
    recovery.start("u")
    recovery.classify("u", parse_outcome="one", discourse="incomplete")
    assert recovery.verify_ledger()
    recovery.units["u"].pending.clear()
    assert not recovery.verify_ledger()


def test_proposer_result_must_answer_the_latest_reservation():
    class Suggest:
        def request(self, source, *, timeout_seconds):
            return "Api is safe."
    recovery = service()
    recovery.add("u", "Unknown wording.", {})
    recovery.start("u")
    recovery.classify("u", parse_outcome="zero")
    assert recovery.request_proposer("u", Suggest())["status"] == "suggestion"
    ledger = recovery.to_ledger()
    assert not rejected(deepcopy(ledger))
    ledger["commands"][-1]["args"]["reserved_revision"] -= 1
    assert rejected(rehash(ledger))
    forged = recovery.to_ledger()
    forged["commands"].insert(3, deepcopy(forged["commands"][-1]))
    for number, command in enumerate(forged["commands"], 1):
        command["sequence"] = number
    assert rejected(rehash(forged))


# -- property: random histories and random tampering ------------------------

UNITS = {"t": ("It is safe.", "translation", []), "a": ("It is safe.", "authoring", []),
         "p": ("Api is safe.", "authoring", ["t"])}


def random_history(rng):
    """Interleave perturbed journeys towards approval: steps are skipped,
    repeated or disrupted (cancel, restart, undo, wrong narrowing)."""
    recovery = service()
    for unit_id, (source, mode, dependencies) in UNITS.items():
        recovery.add(unit_id, source, {}, mode=mode, dependencies=dependencies)
    def classify(u):
        recovery.classify(u, parse_outcome=rng.choice(["one", "one", "multiple"]),
                          discourse=rng.choice(["complete", "complete", "incomplete"]),
                          pending=rng.choice([[], [], [{"reason": "author check"}]]),
                          catalogue_bindings=rng.choice([BINDINGS, BINDINGS, None]))
    def resolve(u):
        while recovery.units[u].pending:
            pending = recovery.units[u].pending
            index = rng.randrange(len(pending))
            if pending[index].get("pattern_id"):
                recovery.resolve_pending(u, index, actor="t", reason="none", disposition="not_applicable")
            else:
                recovery.resolve_pending(u, index, actor="t", reason="rewrite", disposition="resolved",
                                         wording="Api is safe.", cited_spans=[{"start": 0, "end": 2}])
    def narrow(u):
        recovery.record_narrowing(u, keeps=[rng.choice([API_ID, API_ID, CAROL_ID])], actor="t",
                                  reason="cited", cited_spans=[{"start": 0, "end": 2}])
    def approve(u):
        narrowings = recovery.units[u].narrowings
        recovery.approve(u, API, narrowing=narrowings[-1]["id"] if narrowings else None,
                         rejected=rng.choice([[], [{"meaning_id": CAROL_ID, "reason": "cited"}]] * 2
                                             if u != "p" else [[]]),
                         **SELECT_API)
    def undo(u):
        revisions = [e["revision"] for e in recovery.events if e["unit"] == u]
        recovery.undo(u, rng.choice(revisions))
    journey = [lambda u: recovery.start(u), classify, resolve, narrow, approve]
    disruptions = [undo, lambda u: recovery.cancel(u), lambda u: recovery.start(u), classify,
                   lambda u: recovery.edit(u, presentation="Api is safe."),
                   lambda u: recovery.reply(u, "none of these"), narrow, resolve, approve]
    queues = {u: [] for u in UNITS}
    for u in UNITS:
        for _ in range(rng.randrange(1, 3)):
            for step in journey:
                if rng.random() < 0.85:
                    queues[u].append(step)
                if rng.random() < 0.2:
                    queues[u].append(rng.choice(disruptions))
    while any(queues.values()):
        u = rng.choice([u for u in sorted(queues) if queues[u]])
        try:
            queues[u].pop(0)(u)
        except (ValueError, IndexError):
            pass
    return recovery


def obligations_hold(recovery, ledger):
    """Independent oracle over command inputs: approval implies its review work."""
    for unit_id, unit in recovery.units.items():
        if unit.state != "approved":
            continue
        commands = [c for c in ledger["commands"]
                    if c["args"].get("unit_id") == unit_id and c["error"] is None]
        seen, introduced, resolved = set(), 0, 0
        for command in commands:
            args = command["args"]
            if command["command"] == "classify":
                if not any(command["observed"]["deadlines"]):
                    for pattern_id, bindings in (args["catalogue_bindings"] or {}).items():
                        seen |= {row["meaning_id"] for row in
                                 review(ENV, unit.source, bindings, pattern_id=pattern_id)["candidates"]}
                introduced += (len(args["pending"]) + (args["discourse"] != "complete")
                               + (args["parse_outcome"] == "multiple"))
            elif command["command"] == "set_readings":
                introduced += len(args["pending"])
            elif command["command"] == "resolve_pending" and args["disposition"] == "resolved":
                resolved += 1
        considered = {row["meaning_id"] for row in unit.readings}
        if unit.pending or resolved < introduced or not seen <= considered:
            return False
        others = (seen | considered) - {unit.meaning_id}
        if unit.mode == "translation" and others:
            narrowed = [c for c in commands if c["command"] == "record_narrowing"
                        and c["args"]["keeps"] == [unit.meaning_id]]
            if not narrowed or not any(n["keeps"] == [unit.meaning_id] and n["actor"] and n["cited_spans"]
                                       for n in unit.narrowings):
                return False
        if unit.mode == "authoring" and others - {row["meaning_id"] for row in unit.rejected}:
            return False
    return True


def paths(value, prefix=()):
    yield prefix
    if isinstance(value, dict):
        for key, child in value.items():
            if key not in {"event_digest", "command_digest", "previous_digest"}:
                yield from paths(child, prefix + (key,))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from paths(child, prefix + (index,))


def tamper(ledger, rng):
    """Delete, empty or alter one field; retry until the ledger really changed.

    Half the tampers target command inputs, the only part replay does not derive.
    """
    before = json.dumps(ledger, sort_keys=True)
    inputs = rng.random() < 0.5
    while True:
        path = _tamper(ledger, rng, inputs)
        if json.dumps(ledger, sort_keys=True) != before:
            return path


def _tamper(ledger, rng, inputs):
    path = rng.choice([p for p in paths(ledger) if p and (
        not inputs or (p[0] == "commands" and len(p) > 2 and p[2] in {"args", "observed"}))])
    parent = ledger
    for key in path[:-1]:
        parent = parent[key]
    key, value = path[-1], parent[path[-1]]
    operation = rng.choice(["delete", "empty", "alter"])
    if operation == "delete":
        del parent[key]
    elif operation == "empty":
        parent[key] = type(value)() if isinstance(value, (str, list, dict, int, float)) else None
    elif isinstance(value, bool):
        parent[key] = not value
    elif isinstance(value, (int, float)):
        parent[key] = value + 1
    elif isinstance(value, str):
        parent[key] = value + "x"
    elif isinstance(value, list):
        parent[key] = value[:-1] if value and rng.random() < 0.5 else value + deepcopy(value[-1:] or [None])
    elif isinstance(value, dict):
        parent[key] = {**value, "x": None}
    else:
        parent[key] = "x"
    return path


def regenerate(ledger):
    """Replay command inputs leniently to rebuild a self-consistent cache."""
    recovery = service()
    for record in ledger.get("commands") or []:
        if not isinstance(record, dict) or not isinstance(record.get("args"), dict):
            continue
        recovery._replaying = {**record, "observed": {"now": 0.0, "deadlines": [None] * 4, "external": []}}
        try:
            recovery._command(record.get("command"), **record["args"])
        except Exception:
            pass
        finally:
            recovery._replaying = None
    return recovery.to_ledger()


@pytest.mark.parametrize("seed", range(10))
def test_random_histories_and_tampering_never_approve_without_review(seed):
    rng = random.Random(seed)
    recovery = random_history(rng)
    original = recovery.to_ledger()
    imported = RecoveryService.from_ledger(ENV, json.loads(json.dumps(original)))
    assert imported.verify_ledger() and obligations_hold(imported, original)
    for _ in range(25):
        ledger = deepcopy(original)
        path = tamper(ledger, rng)
        rehash(ledger)
        try:
            restored = RecoveryService.from_ledger(ENV, ledger)
        except ValueError:
            pass
        else:
            # Only command inputs can change a history; derived state cannot.
            assert path[0] == "commands" and path[2] in {"args", "observed"}, path
            assert obligations_hold(restored, ledger), path
        if path[:1] == ("commands",):
            consistent = regenerate(ledger)
            restored = RecoveryService.from_ledger(ENV, consistent)
            assert obligations_hold(restored, consistent), path


# -- z3b recheck 1, finding A: approval validity trusted the live cache ------

def observable(recovery):
    """What a transition could read: the ledger and every unit's fields."""
    try:
        return json.dumps({"ledger": recovery.to_ledger(), "revision": recovery.revision,
                           "units": {k: vars(u) | {f: getattr(u, f) for f in vars(type(u))
                                                   .get("__dataclass_fields__", {})}
                                     for k, u in recovery.units.items()}},
                          sort_keys=True)
    except (AttributeError, TypeError, ValueError):
        return None


def test_edited_cache_after_import_cannot_approve_without_narrowing():
    recovery = service()
    recovery.add("t", "It is safe.", {}, mode="translation")
    recovery.add("p", "Api is safe.", {}, dependencies=["t"])
    for unit_id in ("t", "p"):
        recovery.start(unit_id)
    recovery.classify("t", parse_outcome="one", catalogue_bindings=BINDINGS)
    recovery.classify("p", parse_outcome="one")
    imported = RecoveryService.from_ledger(ENV, json.loads(json.dumps(recovery.to_ledger())))
    assert imported.units["t"].state == "ready" and len(imported.units["t"].readings) == 2
    unit = imported.units["t"]
    unit.readings.clear()
    result = unit.catalogue_results["discourse.reference@1"]
    result["candidates"].clear()
    result["cards"].clear()
    before = imported.to_ledger()
    for unit_id in ("t", "p"):
        with pytest.raises(ValueError, match="ledger replay"):
            imported.approve(unit_id, API, **SELECT_API)
    assert imported.to_ledger() == before
    assert not any(e["action"] in {"approve", "narrowing"} for e in imported.events)
    assert not imported.approval_valid("t") and not imported.approval_valid("p")
    assert not imported.verify_ledger()


def test_edited_cache_invalidates_an_approved_parent_and_its_dependent():
    recovery = service()
    recovery.add("t", "It is safe.", {}, mode="translation")
    recovery.add("p", "Api is safe.", {}, dependencies=["t"])
    recovery.start("t")
    recovery.classify("t", parse_outcome="one", catalogue_bindings=BINDINGS)
    record = recovery.record_narrowing("t", keeps=[API_ID], actor="translator", reason="cited",
                                       cited_spans=[{"start": 0, "end": 2}])
    recovery.approve("t", API, narrowing=record["id"], **SELECT_API)
    recovery.start("p")
    recovery.classify("p", parse_outcome="one")
    recovery.approve("p", API, **SELECT_API)
    assert recovery.approval_valid("t") and recovery.approval_valid("p")
    edits = [lambda r: r.units["t"].narrowings.clear(),
             lambda r: r.units["t"].readings.pop(),
             lambda r: r.units["t"].catalogue_results.clear(),
             lambda r: r.units["t"].approval["snapshot"].update(narrowing=None),
             lambda r: setattr(r, "revision", r.revision + 1),
             lambda r: r.events.pop(),
             lambda r: r.commands[-1]["args"].update(actor="someone"),
             lambda r: r.versions.update(reading_set="r2"),
             lambda r: r.limits.update(max_replies=99)]
    for number, edit in enumerate(edits):
        live = RecoveryService.from_ledger(ENV, recovery.to_ledger())
        edit(live)
        assert not live.approval_valid("t") and not live.approval_valid("p"), number
        assert not live.verify_ledger(), number
        with pytest.raises(ValueError, match="ledger replay"):
            live.undo("p", live.units["p"].revision)
        with pytest.raises(ValueError, match="ledger replay"):
            live.edit("t", presentation="Api is safe.")


def test_substituted_cache_objects_are_replaced_by_derived_state():
    recovery = service()
    recovery.add("u", "Api is safe.", {})
    recovery.start("u")
    unit = recovery.units["u"]
    unit.pending = ()  # serialises like the derived [] but is not a list
    recovery.classify("u", parse_outcome="one", pending=[{"reason": "author check"}])
    assert recovery.units["u"] is unit and type(unit.pending) is list
    assert recovery.verify_ledger() and unit.state == "reading_review"


@pytest.mark.parametrize("seed", range(5))
def test_random_live_cache_edits_never_reach_a_transition_or_validate(seed):
    rng = random.Random(1000 + seed)
    ledger = random_history(rng).to_ledger()
    for _ in range(6):
        live = RecoveryService.from_ledger(ENV, deepcopy(ledger))
        before = observable(live)
        while True:
            cache = {"units": {k: vars(u) for k, u in live.units.items()}, "events": live.events,
                     "commands": live.commands, "versions": live.versions,
                     "genesis_versions": live.genesis_versions, "limits": live.limits}
            path = _tamper(cache, rng, False)
            if observable(live) != before:
                break
        assert not any(live.approval_valid(unit_id) for unit_id in UNITS), path
        assert not live.verify_ledger(), path
        tampered = observable(live)
        for unit_id in UNITS:
            for attempt in (lambda: live.approve(unit_id, API, **SELECT_API),
                            lambda: live.start(unit_id), lambda: live.cancel(unit_id)):
                with pytest.raises(ValueError, match="ledger replay"):
                    attempt()
        assert observable(live) == tampered, path


@pytest.mark.parametrize("operation", ["import", "verify"])
def test_recorded_deadline_cannot_swallow_enclosing_replay_deadline(monkeypatch, operation):
    monkeypatch.setattr(recovery_module, "OPERATION_SECONDS", 0.25)
    recovery = service()
    recovery.add("u", "Api is safe.", {})
    recovery.start("u")
    recovery.classify("u", parse_outcome="one")
    recovery.approve("u", API, actor="author", paraphrase="Api is safe.",
                     presentation="Api is safe.", situation=SITUATION)

    original_hit = Budget._hit
    phase = {"record": True, "delay": False, "delayed": False}

    def hit(self, ordinal):
        if phase["record"] and not self.replay:
            self.fired = ordinal
            return True
        if phase["delay"] and self.replay and self.fire_at is not None and not phase["delayed"]:
            phase["delayed"] = True
            time.sleep(0.30)
        return original_hit(self, ordinal)

    monkeypatch.setattr(Budget, "_hit", hit)
    with pytest.raises(ValueError, match="edit operation deadline"):
        recovery.edit("u", source="Api is reviewed.")
    phase["record"] = False
    ledger = recovery.to_ledger()
    assert ledger["commands"][-1]["observed"]["deadlines"] == [1]
    assert recovery.units["u"].state == "approved"
    assert RecoveryService.from_ledger(ENV, ledger).approval_valid("u")

    phase["delay"] = True
    if operation == "import":
        with pytest.raises(ValueError, match="recovery import operation deadline"):
            RecoveryService.from_ledger(ENV, ledger)
    else:
        assert not recovery.verify_ledger()
    assert phase["delayed"]
