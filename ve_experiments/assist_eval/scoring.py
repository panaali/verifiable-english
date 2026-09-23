"""Session scoring beyond the tool's status: evaluation success and the faithful-complete gap route.

``session_checks(session, item, finish)`` is a pure function of the replayed ledger, the dossier's public
text and the author's ``finish``; labels enter only through ``acceptable_locations`` in ``gap_route``.

Evaluation success (``eval_success``): the tool's status is success, OR its ONLY failure is the waiver
line, every waived sentence is in the preregistered allowlist W(item) (never a claimed sentence), AND the
dossier graph checks pass (``dossier.graph_violations``: no anchor on a waive-only sentence, every
given-anchored assumption states its anchor's content, no assumed "remain unassumed" check).

Gap route (flawed items; decision 2 of the 2026-09-23 review round). ALL of:
* the author finished with verdict "gap" and named at least one gap step;
* every asserting claimed sentence has a step node anchored to it (nothing omitted);
* every step NOT named as a gap is certified ("follows");
* every named gap step is a step whose check returned a checker COUNTERMODEL (an unchecked or
  "unknown" step is never a gap), and whose statement is not entailed by the whole dossier (every given
  sentence's reference formalisation; decided "no"), so a missing premise cannot manufacture a gap;
* a step states each frozen target; no given sentence uncovered; no claimed sentence waived; no
  load-bearing unanchored assumption; no renamed conclusion; no dossier graph violation;
* the ledger verified;
* ``gap_located``: the claimed paragraphs the gap steps are anchored to equal one of the item's
  acceptable locations.
Because every claimed sentence needs its own step and every non-gap step must be certified, "freeze the
target, add one step that states it, finish gap" cannot score even when the root paragraph is an
acceptable location: every other claimed paragraph would still need a certified step.
"""
from __future__ import annotations

import re

from . import dossier

WAIVER_FAILURE = re.compile(r"\d+ asserting sentence\(s\) waived ")


def eval_success(status, violations=(), allow=None):
    """(strict, evaluation) success. ``allow`` = W(item) (None: only the given-role rule, for old callers)."""
    if not status:
        return False, False
    strict = bool(status["success"]) and not violations
    waivers = status.get("waivers") or []
    blocking = [w for w in waivers if w.get("counts_against_success")]
    in_w = all(w["sentence"] in allow for w in blocking) if allow is not None else True
    only_waivers = (bool(blocking) and all(w["role"] == "given" for w in blocking) and in_w
                    and all(WAIVER_FAILURE.match(f) for f in status["failures"]))
    return strict, (bool(status["success"]) or only_waivers) and not violations


def claimed_paragraphs(session, names):
    found = set()
    for name in names:
        node = session.nodes.get(name)
        if node:
            found |= {a.split(".")[0] for a in node.anchors if session.sentences[a]["role"] == "claimed"}
    return found


def session_checks(session, item, finish):
    """Deterministic graph facts the report needs (no labels)."""
    finish = finish or {}
    violations = dossier.graph_violations(session, item)
    steps = {n.name: n for n in session.nodes.values() if n.kind == "step"}
    claimed = [sid for sid in session.sentence_order
               if session.sentences[sid]["role"] == "claimed" and session.sentences[sid]["asserting"]]
    without_step = [sid for sid in claimed if not any(sid in n.anchors for n in steps.values())]
    gaps = [g for g in finish.get("gap_steps") or [] if isinstance(g, str)]
    status_of = lambda n: session.checks.get(n, {}).get("status", "unchecked")
    uncertified = sorted(n for n in steps if n not in gaps and status_of(n) != "follows")
    not_refuted = sorted(g for g in gaps if g not in steps or status_of(g) != "countermodel")
    repairable = sorted(g for g in gaps if g in steps and g not in not_refuted
                        and dossier.gap_not_derivable(session, item, steps[g].formula) != "no")
    return {"violations": violations, "claimed_without_step": without_step, "gap_steps": gaps,
            "non_gap_uncertified": uncertified, "gap_not_refuted": not_refuted,
            "gap_repairable_from_dossier": repairable,
            "gap_paragraphs": sorted(claimed_paragraphs(session, gaps))}


def gap_route(result, checks, acceptable_locations):
    """(route ok, gap_located, reasons) for a flawed item."""
    status = result.get("status") or {}
    finish = result.get("finish") or {}
    located = bool(checks["gap_steps"]) and any(set(loc) == set(checks["gap_paragraphs"])
                                                 for loc in acceptable_locations)
    target_stated = bool(status.get("targets")) and all(
        t.get("reason") != "no step node states the frozen target" and t.get("text") for t in status["targets"])
    reasons = []
    if finish.get("verdict") != "gap":
        reasons.append("did not finish with verdict gap")
    if not checks["gap_steps"]:
        reasons.append("no gap step named")
    for key in ("claimed_without_step", "non_gap_uncertified", "gap_not_refuted", "gap_repairable_from_dossier",
                "violations"):
        if checks[key]:
            reasons.append(key)
    if not target_stated:
        reasons.append("no step states the frozen target")
    if status.get("uncovered"):
        reasons.append("uncovered given sentences")
    if any(w.get("role") == "claimed" for w in status.get("waivers", [])):
        reasons.append("claimed sentence waived")
    if any(u["load_bearing"] for u in status.get("unanchored_assumptions", [])):
        reasons.append("load-bearing unanchored assumption")
    if status.get("renamed_conclusions"):
        reasons.append("renamed conclusion")
    if not (result.get("verification") or {}).get("ok"):
        reasons.append("ledger not verified")
    if not located:
        reasons.append("gap not located")
    return not reasons, located, reasons
