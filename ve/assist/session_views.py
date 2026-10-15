"""The read-only views of an assist session: nodes, targets, models, status and export.

Split out of ``ve.assist.session`` (AR-9). ``paraphrase_formula`` stays in ``session``
with the other reviewed exception boundaries.
"""
from __future__ import annotations

from .. import ast
from ..argument import ArgumentGraph, Claim, Deduction, check_argument, deduction_identity
from ..printer import print_formula
from .session_state import ORIGINS, AssistError, _predicates_of, _symbols_of


class _Views:
    """Views, the status report and export of an ``AssistSession``."""

    def _sentence_view(self, sid):
        s = self.sentences[sid]
        return {"id": sid, "role": s["role"], "text": s["text"]}

    def node_view(self, name):
        node = self.nodes[name]
        check = self.checks.get(name)
        view = {"name": name, "kind": node.kind, "text": node.text,
                "paraphrase": self.paraphrase_formula(node.formula),
                "anchors": [self._sentence_view(a) for a in node.anchors],
                "parents": list(node.parents), "origin": node.origin}
        if node.source_ref:
            view["source_ref"] = node.source_ref
        if node.kind == "step":
            view["check"] = check["status"] if check else "unchecked"
        matches = [t for t, row in self.targets.items() if row["formula"] == node.formula]
        if matches:
            view["matches_targets"] = matches
        return view

    def describe_model(self, model, formulas):
        """Readable model: named entities, true atoms, and the false atoms the formulas mention."""
        from .ground import _atoms
        used, mentioned = set(), {}
        for f in formulas:
            _predicates_of(f, used)
            _atoms(f, mentioned)  # ground atoms (constants only); stops at binders
        names = {}
        for const, entity in model.constants.items():
            names.setdefault(entity, []).append(const)
        label = lambda e: " = ".join(sorted(names[e])) if e in names else e
        spell = lambda p, args: (f"{label(args[0])} is {p}" if len(args) == 1
                                 else f"{label(args[0])} {p} {label(args[1])}")
        true_atoms = [spell(p, row) for p in sorted(used) if p in self.env.predicates
                      for row in sorted(model.relations[p])]
        false_atoms = []
        for (p, consts) in mentioned:
            row = tuple(model.constants[c] for c in consts)
            text = spell(p, row)
            if row not in model.relations[p] and text not in false_atoms:
                false_atoms.append(text)
        return {"entities": {sort: [label(e) for e in model.domains[sort]] for sort in sorted(model.domains)},
                "true": true_atoms, "false": sorted(false_atoms)}

    def _do_show(self, name=None):
        if name is not None:
            if name not in self.nodes:
                raise AssistError(f"Unknown node {name!r}")
            view = self.node_view(name)
            view["history"] = self.nodes[name].history
            check = self.checks.get(name)
            if check and check["status"] == "countermodel":
                view["countermodel"] = check["explanation"]
            return {"node": view}
        return {"targets": [self._target_view(t) for t in self.targets],
                "nodes": [self.node_view(n) for n in self.nodes]}

    def _target_view(self, tid):
        row = self.targets[tid]
        view = {"id": tid, "sentence": self._sentence_view(row["sentence"]), "frozen": row["formula"] is not None}
        if row["formula"] is not None:
            view.update(text=row["text"], paraphrase=self.paraphrase_formula(row["formula"]),
                        vacuity=row.get("vacuity", "invalid"))
        return view

    def _do_paraphrase(self, text, surface="auto"):
        formula, used = self._parse(text, surface)
        return {"text": self._canonical(formula), "paraphrase": self.paraphrase_formula(formula), "surface": used}

    def _do_sentences(self):
        return {"sentences": [self._sentence_view(s) | {"asserting": self.sentences[s]["asserting"]}
                              for s in self.sentence_order],
                "targets": [self._target_view(t) for t in self.targets],
                "vocabulary": self.vocabulary()}

    def vocabulary(self):
        return {"sorts": {k: v.description for k, v in self.env.sorts.items()},
                "predicates": {k: {"arguments": list(v.arguments), "gloss": v.description}
                               for k, v in self.env.predicates.items()},
                "constants": {k: v.sort for k, v in self.env.constants.items()}}

    # ------------------------------------------------------------------ status
    def _support(self, root):
        found, pending = [], [root]
        while pending:
            name = pending.pop()
            if name in found:
                continue
            found.append(name)
            pending.extend(self.nodes[name].parents)
        return found

    def _anchor_state(self, node):
        """``anchored`` only when every anchor is given: an anchor to any claimed sentence means the
        assumption states (part of) a conclusion, which must be derived, not assumed."""
        roles = {self.sentences[a]["role"] for a in node.anchors}
        if "claimed" in roles:
            return "anchored_to_claim_only"
        if "given" in roles:
            return "anchored"
        return "unanchored"

    def _is_anchored_parent(self, name):
        node = self.nodes[name]
        return node.kind == "step" or self._anchor_state(node) == "anchored"

    def target_graph(self, tid):
        """Build the checked ArgumentGraph for one target, or (None, reason)."""
        row = self.targets[tid]
        if row["formula"] is None:
            return None, "target not frozen", None
        matches = [n for n in self.nodes.values() if n.formula == row["formula"] and n.kind == "step"]
        if not matches:
            return None, "no step node states the frozen target", None
        certified = [n for n in matches if self.checks.get(n.name, {}).get("status") == "follows"]
        # Deterministic in the graph (by name), never by insertion order; every other matching step is
        # still evaluated by status as a witness.
        root = min(certified or matches, key=lambda n: n.name)
        support = self._support(root.name)
        claims = tuple(Claim.create(self.env, n, print_formula(self.env, self.nodes[n].formula) + ".\n")
                       for n in support)
        steps = [n for n in support if self.nodes[n].kind == "step"]
        # Deduction premises in the canonical parent order _check proved them in.
        parents = {n: self._ordered_parents(self.nodes[n]) for n in steps}
        bare = ArgumentGraph(self.env, claims, tuple(Deduction("d_" + n, parents[n], n) for n in steps),
                             root.name, target_scope="assist:" + tid)
        deductions = []
        for n in steps:
            plain = Deduction("d_" + n, parents[n], n)
            check = self.checks.get(n)
            certs = ()
            if check and check["status"] == "follows":
                certs = ({"edge_id": deduction_identity(bare, plain), "direction": "follows",
                          "proof": check["certificate"]},)
            deductions.append(Deduction("d_" + n, parents[n], n, certs))
        graph = ArgumentGraph(self.env, claims, tuple(deductions), root.name, target_scope="assist:" + tid)
        return graph, None, root.name

    def _do_status(self):
        failures = []
        targets, support_all = [], set()
        for tid in self.targets:
            view = self._target_view(tid)
            graph, reason, root = self.target_graph(tid) if view["frozen"] else (None, "target not frozen", None)
            if graph is None:
                view.update(certified=False, reason=reason)
                failures.append(f"target {tid}: {reason}")
            else:
                result = check_argument(graph, search=False).require_available()
                support = self._support(root)
                support_all.update(support)
                view.update(node=root, replay=result.status, certified=result.status == "Checked",
                            support=support, assumptions=list(result.remaining_assumptions))
                if result.status != "Checked":
                    failures.append(f"target {tid}: graph replay status {result.status}")
                failures += self._consistency_failures(f"target {tid}", result.remaining_assumptions, view)
                # Vacuity through the graph: tautological assumptions add nothing, so a target they
                # entail on their own is vacuous even when the direct empty-premise check ran out of budget.
                # An assumption whose validity is undecided counts as possibly tautological (fail closed).
                verdicts = {n: self._validity(self.nodes[n].formula) for n in sorted(result.remaining_assumptions)}
                trivial = [n for n, v in verdicts.items() if v != "invalid"]
                if trivial:
                    verdict = self._decide([self.nodes[n].formula for n in trivial], self.targets[tid]["formula"])
                    undecided = [n for n in trivial if verdicts[n] == "unknown"]
                    if verdict == "yes" and not undecided:
                        view["vacuous"] = True
                        failures.append(f"target {tid}: provable from tautological assumptions only "
                                        f"({', '.join(trivial)})")
                    elif verdict != "no":
                        view["vacuous"] = "unknown"
                        failures.append(f"target {tid}: vacuity through assumptions undecided within budget "
                                        f"({', '.join(trivial)} may be tautologies that entail it; fail closed)")
            if view["frozen"] and view.get("vacuity") == "unknown":
                failures.append(f"target {tid}: vacuity unknown (the empty-premise check exhausted its budget; "
                                "fail closed)")
            targets.append(view)
        steps = [n for n in self.nodes.values() if n.kind == "step"]
        # Outcome is a FUNCTION OF THE GRAPH: every certified step that states a frozen target or is anchored
        # to a claimed sentence is a WITNESS, and ALL witnesses are evaluated (never "the first found"), in
        # name order. Each witness joins the load-bearing analysis, has its assumptions checked for
        # consistency, and must be entailed by its ANCHORED assumptions alone (decided by ``_decide``): a
        # witness that needs an unanchored assumption blocks success whatever other witnesses exist.
        witnesses = self._witnesses()
        dependence = {}
        for w in witnesses:
            support = self._support(w)
            support_all.update(support)
            leaves = [n for n in support if self.nodes[n].kind == "assumption"]
            failures += self._consistency_failures(f"step {w}", leaves)
            verdict, loose = self._anchored_entailment(w)
            dependence[w] = {"verdict": verdict, "unanchored_assumptions": loose}
            if verdict == "no":
                failures.append(f"step {w}: its anchored assumptions alone do not entail it (it needs "
                                f"unanchored {', '.join(loose)})")
            elif verdict == "unknown":
                failures.append(f"step {w}: undecided within budget whether its anchored assumptions alone "
                                f"entail it (unanchored {', '.join(loose) or 'none'}; fail closed)")
        # A claimed sentence is DERIVED when some witness anchored to it is independent of unanchored
        # assumptions (decided) and no single assumption in its support already states it (decided "no").
        # Covering it with an idle node, restating it, or waiving it never counts.
        derived, derivation_unknown = {}, {}
        for sid in self.sentence_order:
            if self.sentences[sid]["role"] == "claimed" and self.sentences[sid]["asserting"]:
                by, undecided = self._derivation(sid, dependence)
                if by:
                    derived[sid] = by
                elif undecided:
                    derivation_unknown[sid] = undecided
        unproved = [{"node": n.name, "check": self.checks.get(n.name, {}).get("status", "unchecked"),
                     "parents": list(n.parents)} for n in steps
                    if self.checks.get(n.name, {}).get("status") != "follows"]
        if unproved:
            failures.append(f"{len(unproved)} unproved step(s)")
        # Load-bearing: a certified step whose anchored parents ALONE (every unanchored parent removed at
        # once, so duplicates cannot hide each other) no longer entail it needs its unanchored parents.
        needs, undecided_needs = {}, {}
        for s in steps:
            if s.name not in support_all or self.checks.get(s.name, {}).get("status") != "follows":
                continue
            loose = [p for p in s.parents if not self._is_anchored_parent(p)]
            if not loose:
                continue
            anchored = [self.nodes[p].formula for p in s.parents if self._is_anchored_parent(p)]
            verdict = self._decide(anchored, s.formula)
            if verdict != "yes":  # "unknown" counts as needed (fail closed)
                for p in loose:
                    needs.setdefault(p, []).append(s.name)
                    undecided_needs.setdefault(p, []).extend([s.name] if verdict == "unknown" else [])
        unanchored = []
        for n in self.nodes.values():
            if n.kind != "assumption" or self._anchor_state(n) == "anchored":
                continue
            needed_by = needs.get(n.name, [])
            row = {"node": n.name, "anchor_state": self._anchor_state(n), "text": n.text,
                   "paraphrase": self.paraphrase_formula(n.formula),
                   "supports_target": n.name in support_all, "load_bearing": bool(needed_by),
                   "needed_by": needed_by}
            if undecided_needs.get(n.name):
                row["load_bearing_undecided_for"] = undecided_needs[n.name]
            unanchored.append(row)
            if needed_by:
                failures.append(f"load-bearing unanchored assumption {n.name}"
                                + (" (undecided within budget; fail closed)"
                                   if set(needed_by) <= set(undecided_needs.get(n.name, ())) else ""))
        coverage, uncovered, underived, waived = [], [], [], []
        for sid in self.sentence_order:
            s = self.sentences[sid]
            if not s["asserting"]:
                continue
            by = [n.name for n in self.nodes.values() if sid in n.anchors]
            if s["role"] == "claimed":
                state = "derived" if sid in derived else "underived"
            else:
                state = "covered" if by else "uncovered"
            # Waiving ANY asserting sentence blocks success, even one that is already covered or derived.
            state = "waived" if sid in self.waivers else state
            coverage.append({"sentence": sid, "role": s["role"], "state": state, "nodes": by,
                             **({"derived_by": derived[sid]} if sid in derived else {}),
                             **({"derivation_undecided": derivation_unknown[sid]}
                                if sid in derivation_unknown else {}),
                             **({"waiver": self.waivers[sid]} if state == "waived" else {})})
            {"uncovered": uncovered, "underived": underived, "waived": waived}.get(state, []).append(sid)
        if uncovered:
            failures.append(f"{len(uncovered)} given sentence(s) not covered by any node: {', '.join(uncovered)}")
        if underived:
            failures.append(f"{len(underived)} claimed sentence(s) not derived by a certified step: "
                            f"{', '.join(underived)}")
        for sid, rows in derivation_unknown.items():
            if sid in underived:
                failures.append(f"claimed sentence {sid}: undecided within budget whether it is derived "
                                f"({'; '.join(rows)}; fail closed)")
        if waived:
            failures.append(f"{len(waived)} asserting sentence(s) waived (a waiver is reported, never success): "
                            f"{', '.join(waived)}")
        waivers = [{"sentence": sid, "role": self.sentences[sid]["role"],
                    "asserting": self.sentences[sid]["asserting"], "reason": reason,
                    "counts_against_success": sid in waived}
                   for sid, reason in self.waivers.items()]
        for tid, row in self.targets.items():
            if row["formula"] is None:
                continue
            for n in self.nodes.values():
                if n.kind != "assumption":
                    continue
                verdict = self._decide([n.formula], row["formula"])
                if verdict == "yes":
                    failures.append(f"assumption {n.name} alone entails target {tid}")
                elif verdict == "unknown":
                    failures.append(f"assumption {n.name}: undecided within budget whether it alone entails "
                                    f"target {tid} (fail closed)")
        renamed = self._renamed_conclusions()
        failures += [f"declared vocabulary carries target {r['target']} ({', '.join(r['assumptions'])})"
                     if not r.get("undecided") else
                     f"declared vocabulary may carry target {r['target']} ({', '.join(r['assumptions'])}): "
                     "undecided within budget (fail closed)"
                     for r in renamed]
        origins = {o: sum(1 for n in self.nodes.values() if n.origin == o) for o in ORIGINS}
        return {"success": not failures, "failures": failures, "targets": targets,
                "unproved_steps": unproved, "unanchored_assumptions": unanchored,
                "coverage": {"covered": sum(r["state"] == "covered" for r in coverage),
                             "derived": sum(r["state"] == "derived" for r in coverage),
                             "waived": sum(r["state"] == "waived" for r in coverage),
                             "uncovered": uncovered, "underived": underived, "sentences": coverage},
                "waivers": waivers,
                "renamed_conclusions": renamed, "provenance": origins,
                "declared": self.declared, "usage": self.usage()}

    def _witnesses(self):
        """Every certified step that states a frozen target or is anchored to a claimed sentence, by name."""
        targets = [row["formula"] for row in self.targets.values() if row["formula"] is not None]
        return sorted(n.name for n in self.nodes.values()
                      if n.kind == "step" and self.checks.get(n.name, {}).get("status") == "follows"
                      and (n.formula in targets or any(self.sentences[a]["role"] == "claimed" for a in n.anchors)))

    def _anchored_entailment(self, name):
        """``(verdict, unanchored)``: do the ANCHORED assumptions under step ``name`` alone entail it?

        ``yes`` without search when its support is fully certified and every assumption is anchored (the
        certified chain is the proof); otherwise decided by ``_decide`` on the anchored assumptions only.
        An uncertified step in the support makes the chain no proof: ``unknown`` (fail closed)."""
        support = [self.nodes[n] for n in self._support(name)]
        loose = sorted(m.name for m in support if m.kind == "assumption" and self._anchor_state(m) != "anchored")
        if not all(self.checks.get(m.name, {}).get("status") == "follows" for m in support if m.kind == "step"):
            return "unknown", loose
        if not loose:
            return "yes", loose
        anchored = [m.formula for m in support if m.kind == "assumption" and m.name not in loose]
        return self._decide(anchored, self.nodes[name].formula), loose

    def _derivation(self, sid, dependence):
        """``(steps, undecided)``: EVERY witness that derives claimed sentence ``sid`` (sorted), and, when
        none does, the witnesses rejected only because a decision is still undecided within budget."""
        derived, undecided = [], []
        for name in sorted(n.name for n in self.nodes.values() if sid in n.anchors):
            if name not in dependence:  # not a certified step
                continue
            node = self.nodes[name]
            verdicts = {m: self._decide([self.nodes[m].formula], node.formula)
                        for m in self._support(name) if self.nodes[m].kind == "assumption"}
            if dependence[name]["verdict"] == "no" or any(v == "yes" for v in verdicts.values()):
                continue
            unknown = sorted(m for m, v in verdicts.items() if v == "unknown")
            if dependence[name]["verdict"] == "unknown":
                unknown.append("independence of unanchored assumptions")
            if unknown:
                undecided.append(f"{name}: {', '.join(unknown)}")
                continue
            derived.append(name)
        return derived, [] if derived else undecided

    def _consistency_failures(self, label, names, view=None):
        """Assumptions ``names`` must be decided consistent; contradictory or undecided fails."""
        leaves = [self.nodes[n].formula for n in sorted(names)]
        if not leaves:
            return []
        verdict = self._decide(leaves, ast.Bottom())
        if view is not None and verdict != "no":
            view["inconsistent_assumptions"] = True if verdict == "yes" else "unknown"
        if verdict == "yes":
            return [f"{label}: its assumptions are jointly contradictory"]
        if verdict == "unknown":
            return [f"{label}: consistency of its assumptions undecided within budget (fail closed)"]
        return []

    def _renamed_conclusions(self):
        """Declared vocabulary that carries a target.

        The suspect assumptions are every assumption that mentions a declared symbol (predicate,
        constant or sort) plus every
        assumption not anchored to given prose. If they jointly entail a target WITHOUT the anchored,
        undeclared premises, the target was carried in, not derived; the reported set is a minimal
        entailing subset (so chains through ordinary assumptions are caught, not only pairs).
        """
        if not self.declared:
            return []
        declared = set(self.declared)
        carriers = [n for n in self.nodes.values() if n.kind == "assumption" and _symbols_of(n.formula) & declared]
        if not carriers:
            return []
        names = {n.name for n in carriers}
        suspects = [n for n in self.nodes.values() if n.kind == "assumption"
                    and (n.name in names or self._anchor_state(n) != "anchored")]
        found = []
        for tid, row in self.targets.items():
            if row["formula"] is None:
                continue
            verdict = self._decide([g.formula for g in suspects], row["formula"])
            if verdict == "no":
                continue
            if verdict == "unknown":
                found.append({"target": tid, "assumptions": [g.name for g in suspects], "undecided": True})
                continue
            group = list(suspects)
            # Drop ordinary assumptions before declared carriers, so a carrier stays in the witness set.
            # A member is dropped only when the rest is PROVED to still entail the target.
            for member in sorted(group, key=lambda g: (g.name in names, g.name)):  # graph order, not insertion
                rest = [g for g in group if g is not member]
                if self._decide([g.formula for g in rest], row["formula"]) == "yes":
                    group = rest
            if any(g.name in names for g in group):
                found.append({"target": tid, "assumptions": [g.name for g in group]})
        return found

    def usage(self):
        totals = {}
        for event in self.events:
            for role, row in event.get("tokens", {}).items():
                acc = totals.setdefault(role, {"input_tokens": 0, "output_tokens": 0, "calls": 0})
                for key in acc:
                    acc[key] += row.get(key, 0) or 0
        actions = {}
        for event in self.events:
            actions[event["action"]] = actions.get(event["action"], 0) + 1
        return {"tokens": totals, "actions": actions, "events": len(self.events),
                "rejected_actions": sum(1 for e in self.events if not e["result"]["ok"]),
                "tool_result_chars": sum(e.get("result_chars", 0) for e in self.events)}

    def _do_export(self):
        graphs = {}
        for tid in self.targets:
            graph, reason, _ = self.target_graph(tid)
            graphs[tid] = graph.to_dict() if graph is not None else {"missing": reason}
        return {"graphs": graphs,
                "nodes": [{**self.node_view(n), "anchors": list(self.nodes[n].anchors)} for n in self.nodes],
                "environment": self.env.to_dict(), "english_vocabulary": self.overlay}
