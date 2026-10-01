"""Executable forms of the risk@0 fixtures (docs/spec/risk.md 8.1) for the Lean route.

Lean owns the semantics (risk.md 7). These builders only write the environments,
norm objects, log entries and decision records of 8.1 in the wire forms of 3.
"""
from __future__ import annotations

import hashlib
from copy import deepcopy

from ve.profiles import LANGUAGE, SPEC_REVISION
from ve.wire import canonical_json

DAY = "2026-09-29"


def base(arguments, wording):
    return {"arguments": arguments, "description": wording, "verbalisation": wording}


def const(sort, description):
    return {"sort": sort, "description": description}


def rule(name, predicate, sign, guard, unless=(), over=()):
    return {"norm": {"name": name, "predicate": predicate, "sign": sign, "guard": guard,
                     "unless": list(unless), "over": list(over)}}


AGENT_OPS_HARMS = {"data_loss": ("data loss", "severe"), "server_outage": ("a server outage", "serious"),
                   "job_failure": ("a job failure", "minor"), "task_delay": ("a task delay", "minor"),
                   "task_abandonment": ("task abandonment", "minor")}


def agent_ops(*, scale="1", harms=None, risk=None, extra_constants=None):
    """Environment `agent-ops` (8.1); `scale="10"` gives `agent-ops-fine`."""
    harms = AGENT_OPS_HARMS if harms is None else harms
    predicates = {
        "available": base(["action", "agent"], "{0} is available to {1}"),
        "leads_to": base(["action", "harm"], "{0} leads to {1}"),
        "inaction": base(["action"], "{0} is inaction"),
        "taken": base(["action"], "{0} is taken"),
        "confirmed": base(["action"], "the user has confirmed {0}"),
        "permitted": {"arguments": ["action"], "description": "permission", "regulated":
                      {"role": "permission", "default": "allow", "act": "{0} be performed"}},
        "required": {"arguments": ["action"], "description": "obligation", "regulated":
                     {"role": "obligation", "default": "deny", "act": "{0} be performed",
                      "permission": "permitted"}},
    }
    constants = {h: const("harm", text) for h, (text, _) in harms.items()}
    constants.update(extra_constants or {})
    block = {
        "severity": {"sort": "severity", "classes": ["severe", "serious", "minor"],
                     "more_severe": [["severe", "serious"], ["serious", "minor"]], "unranked": [],
                     "decided_by": "the platform team"},
        "harm_classes": [[h, c] for h, (_, c) in harms.items()],
        "unexamined": {"ruled_out_by": "chooser"},
        "always_possible": ["severe", "serious"],
        "combination": "hull",
        "alternative_kinds": {"run": "running the job", "run_limited": "running the job with the memory limit",
                              "ask": "asking the user"},
        "required_alternatives": [{"when": "run", "require": ["run_limited"]}],
        "quantity_kinds": {"peak_memory": "gb", "free_memory": "gb", "memory_limit": "gb"},
        "required_estimators": [{"quantity_kind": "peak_memory", "estimators": ["memory profiler"]}],
        "use_all_recorded": False,
    }
    if risk:
        block.update(risk)
    return {"language": LANGUAGE,
            "profiles": ["alternatives@0", "norms@0", "relational-fol@0", "risk@0"],
            "spec_revision": SPEC_REVISION,
            "vocabulary": {"sorts": {s: {"description": s} for s in ("agent", "action", "harm")},
                           "predicates": predicates, "constants": constants},
            "alternatives": {"chooser": "agent", "action": "action", "harm": "harm",
                             "available": "available", "leads_to": "leads_to", "outcomes": "signed",
                             "decided_by": "the build agent",
                             "performed": {"permission": "permitted", "obligation": "required"},
                             "inaction": "inaction", "taken": "taken"},
            "risk": block,
            "unit_schema": "ve-units@1",
            "units": {"gb": {"scale": scale, "display": {"kind": "decimal", "label": "GB"}}}}


def agent_ops_rules():
    """Rules 1 to 3 of 2.5, as W1 norm objects (guards in the context `[action]`)."""
    rule1 = rule("rule-1", "permitted", False,
                 ["exists", "harm", ["and", ["binary", "risk__class", ["var", 0], ["const", "severe"]],
                                     ["binary", "risk__might_lead_to", ["var", 1], ["var", 0]]]])
    rule2 = rule("rule-2", "permitted", False,
                 ["exists", "agent", ["and", ["binary", "available", ["var", 1], ["var", 0]],
                                      ["exists", "action", ["and", ["and",
                                          ["binary", "available", ["var", 0], ["var", 1]],
                                          ["not", ["eq", ["var", 0], ["var", 2]]]],
                                          ["binary", "risk__less_worst", ["var", 0], ["var", 2]]]]]],
                 unless=[["unary", "confirmed", ["var", 0]]])
    rule3 = rule("rule-3", "permitted", False, ["binary", "allows", ["var", 0], ["const", "task_abandonment"]])
    return [rule1, rule2, rule3]


def cell_env(harms=None):
    """Environment `cell-env`: agent-ops with no rules, `unexamined: possible`, no kinds or requirements."""
    env = agent_ops(harms=harms)
    env["risk"] = {"severity": env["risk"]["severity"], "harm_classes": env["risk"]["harm_classes"],
                   "unexamined": "possible"}
    return env


def entry_hash(entry):
    body = {k: entry[k] for k in ("seq", "day", "id", "kind", "content", "prev")}
    return hashlib.sha256(canonical_json(body)).hexdigest()


class Log:
    """An append-only, hash-chained log (3.3)."""

    def __init__(self):
        self.entries = []

    def add(self, seq, id_, kind, content):
        prev = self.entries[-1]["hash"] if self.entries else ""
        entry = {"seq": seq, "day": DAY, "id": id_, "kind": kind, "content": content, "prev": prev}
        entry["hash"] = entry_hash(entry)
        self.entries.append(entry)
        return entry

    def get(self, id_):
        return next(e for e in self.entries if e["id"] == id_)

    def cite(self, *ids):
        return [{"id": e["id"], "seq": e["seq"], "hash": e["hash"]} for e in (self.get(i) for i in ids)]

    def json(self):
        return {"format": "ve-risk-log@0", "entries": deepcopy(self.entries)}


def estimate(quantity, lo, hi, estimator, support, version=None, supersedes=None):
    content = {"quantity": quantity, "lo": lo, "hi": hi, "method": "stated", "basis": [], "support": support}
    if estimator is not None:
        content["estimator"] = {"name": estimator, **({"version": version} if version else {})}
    if supersedes:
        content["supersedes"] = supersedes
    if support is None:
        del content["support"]
    return content


def condition(action, harm, form, cond, author="the build agent", support="assumption"):
    return {"action": action, "harm": harm, "form": form, "condition": cond, "author": author, "support": support}


def statement(action, harm, stated, author="the build agent", support="assumption"):
    return {"action": action, "harm": harm, "stated": stated, "author": author, "support": support}


def q(name):
    return ["quantity", name]


def dec(tag, value):
    return ["decimal", tag, value]


def gt(a, b):
    """`a is greater than b` is `lt` with the operands exchanged (3.2)."""
    return ["lt", b, a]


def record(id_, chooser, label, policy, alternatives, quantities, cites, facts=()):
    return {"format": "ve-risk-decision@0", "id": id_, "chooser": chooser, "chooser_label": label,
            "policy": {"environment_id": policy[0], "document_hash": policy[1]},
            "alternatives": alternatives, "quantities": quantities, "cites": cites, "facts": list(facts)}


D17_ALTERNATIVES = [{"name": "run", "label": "running the job", "kind": "run"},
                    {"name": "run_limited", "label": "running the job with the memory limit", "kind": "run_limited"},
                    {"name": "ask", "label": "asking the user", "kind": "ask"},
                    {"name": "nothing", "label": "not running the job", "inaction": True}]

D17_QUANTITIES = [{"name": "peak_memory", "label": "the peak memory of the job", "tag": "gb", "kind": "peak_memory"},
                  {"name": "free_memory", "label": "the free memory of the server during the job", "tag": "gb",
                   "kind": "free_memory"},
                  {"name": "memory_limit", "label": "the memory limit", "tag": "gb", "kind": "memory_limit"}]


def log_l17(*, fine=False, e1=("6", "12"), e2=("8", "10"), s1="7", with_39=True, extra=None):
    """Log `L17` up to entry 40 (the entries decision 17 cites, and entry 39)."""
    log = Log()
    if extra:
        extra(log)
    log.add(25, "S1", "setting", {"quantity": "memory_limit", "value": s1, "alternative": "run_limited"})
    log.add(26, "C1", "condition", condition("run", "server_outage", "necessary", gt(q("peak_memory"), q("free_memory"))))
    log.add(27, "C2", "condition", condition("run_limited", "server_outage", "necessary",
                                             gt(q("memory_limit"), q("free_memory"))))
    log.add(28, "C3", "condition", condition("run_limited", "job_failure", "exact", gt(q("peak_memory"), q("memory_limit"))))
    log.add(29, "C4", "condition", condition("run", "job_failure", "necessary", gt(q("peak_memory"), q("free_memory"))))
    log.add(30, "T1", "statement", statement("ask", "task_delay", "leads"))
    log.add(31, "T2", "statement", statement("nothing", "task_abandonment", "leads"))
    log.add(32, "T3", "statement", statement("ask", "server_outage", "cannot"))
    log.add(33, "T4", "statement", statement("nothing", "server_outage", "cannot"))
    for seq, (tid, action) in zip(range(34, 38), [("T5", "run"), ("T6", "run_limited"), ("T7", "ask"), ("T8", "nothing")]):
        log.add(seq, tid, "statement", statement(action, "data_loss", "cannot", author="the platform team",
                                                 support="testimony"))
    log.add(38, "E1", "estimate", estimate("peak_memory", *e1, "memory profiler", "statistical", version="2.3"))
    if with_39:
        log.add(39, "39", "estimate", estimate("free_memory", "4", "10", "the scheduler", "calculation"))
    log.add(40, "E2", "estimate", estimate("free_memory", *e2, "server monitor", "observation"))
    return log


D17_CITES = ["S1", "C1", "C2", "C3", "C4", "T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8", "E1", "E2"]


def decision_17(log, policy, *, cites=None, alternatives=None, facts=(), seq=41, id_="D17", record_id="17",
                chooser="build_agent", label="the build agent"):
    cites = D17_CITES if cites is None else cites
    content = record(record_id, chooser, label, policy, alternatives or D17_ALTERNATIVES, D17_QUANTITIES,
                     log.cite(*cites), facts)
    return log.add(seq, id_, "decision", content)


def asimov_risk(harms, classes=("fatal", "injuring"), fulfilment=None):
    """Environment `asimov-risk` (8.1) with one variant's harm constants and classes."""
    predicates = {
        "available": base(["action", "robot"], "{0} is available to {1}"),
        "leads_to": base(["action", "harm"], "{0} leads to {1}"),
        "inaction": base(["action"], "{0} is inaction"),
        "taken": base(["action"], "{0} is taken"),
        "harms_human": base(["harm"], "{0} is a harm to a human being"),
        "lawful": base(["action"], "{0} is lawful"),
        "permitted": {"arguments": ["action"], "description": "permission", "regulated":
                      {"role": "permission", "default": "allow", "act": "{0} be performed"}},
        "required": {"arguments": ["action"], "description": "obligation", "regulated":
                     {"role": "obligation", "default": "deny", "act": "{0} be performed", "permission": "permitted"}},
        "prevent_required": {"arguments": ["robot", "harm"], "description": "prevention", "regulated":
                             {"role": "obligation", "default": "deny", "act": "{0} prevent {1}"}},
    }
    alternatives = {"chooser": "robot", "action": "action", "harm": "harm", "available": "available",
                    "leads_to": "leads_to", "outcomes": "signed", "decided_by": "Asimov case annotator",
                    "performed": {"permission": "permitted", "obligation": "required"},
                    "inaction": "inaction", "taken": "taken"}
    if fulfilment:
        alternatives["fulfilments"] = [{"obligation": "prevent_required", "body": fulfilment}]
    return {"language": LANGUAGE, "profiles": ["alternatives@0", "norms@0", "relational-fol@0", "risk@0"],
            "spec_revision": SPEC_REVISION,
            "vocabulary": {"sorts": {s: {"description": s} for s in ("robot", "action", "harm")},
                           "predicates": predicates,
                           "constants": {h: const("harm", text) for h, (text, _) in harms.items()}},
            "alternatives": alternatives,
            "risk": {"severity": {"sort": "severity", "classes": list(classes),
                                  "more_severe": [[classes[0], classes[1]]], "unranked": [],
                                  "decided_by": "the Asimov case annotator"},
                     "harm_classes": [[h, c] for h, (_, c) in harms.items()],
                     "unexamined": "possible"}}


def asimov_rules():
    """Rules 1, 2, 3, 2x and 8 of 2.5 (guards in the rule's context, reversed)."""
    human_might = ["exists", "harm", ["and", ["unary", "harms_human", ["var", 0]],
                                      ["binary", "risk__might_lead_to", ["var", 1], ["var", 0]]]]
    human_allows = ["exists", "harm", ["and", ["unary", "harms_human", ["var", 0]],
                                       ["binary", "allows", ["var", 1], ["var", 0]]]]
    unbeaten = ["exists", "robot", ["and", ["binary", "available", ["var", 1], ["var", 0]],
                                    ["not", ["exists", "action", ["and", ["and",
                                        ["binary", "available", ["var", 0], ["var", 1]],
                                        ["not", ["eq", ["var", 0], ["var", 2]]]],
                                        ["binary", "risk__less_worst", ["var", 0], ["var", 2]]]]]]]
    return {
        "1": rule("rule-1", "permitted", False, human_might),
        "2": rule("rule-2", "permitted", False, human_allows),
        "2x": rule("rule-2", "permitted", False, human_allows, over=["rule-3"]),
        "3": rule("rule-3", "permitted", True, unbeaten, over=["rule-1"]),
        "8": rule("rule-8", "prevent_required", True,
                  ["and", ["unary", "harms_human", ["var", 0]], ["binary", "avoidable", ["var", 0], ["var", 1]]]),
    }
