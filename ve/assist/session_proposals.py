"""The authoring actions of an assist session: targets, nodes, vocabulary, checks and proposals.

Split out of ``ve.assist.session`` (AR-9). The checks themselves (``_check``,
``_decide``) stay in ``session`` with the other trust-boundary code.
"""
from __future__ import annotations

from copy import deepcopy
import json
import warnings

from ..environment import Environment
from ..errors import VEError
from .session_state import AssistError, Node, _ident, _names


class _Proposals:
    """The actions that change an ``AssistSession``'s graph, targets and vocabulary."""

    # ------------------------------------------------------------------ actions
    def _do_freeze_target(self, target, text=None, surface="auto", candidate=None):
        """Commit the formal target for a target sentence. Irreversible."""
        if candidate is not None:
            if candidate not in self.candidates:
                raise AssistError(f"Unknown candidate {candidate!r}")
            if text is None:
                text = self._canonical(self.candidates[candidate]["formula"])
        if text is None:
            raise AssistError("freeze_target needs text or a candidate")
        if target not in self.targets:
            raise AssistError(f"Unknown target {target!r}")
        row = self.targets[target]
        if row["formula"] is not None:
            raise AssistError(f"Target {target} is already frozen and cannot change")
        if self.nodes:
            raise AssistError("Targets must be frozen before any node is added")
        formula, used = self._parse(text, surface)
        vacuity = self._reject_vacuous(target, formula)
        origin = "hand-written"
        if candidate is not None:
            origin = "proposer-verbatim" if formula == self.candidates[candidate]["formula"] else "proposer-edited"
        elif self._offered(formula):
            origin = self._offered(formula)[0] + "-verbatim"
        row.update(formula=formula, text=self._canonical(formula), frozen_by="author", origin=origin,
                   vacuity=vacuity)
        result = {"target": target, "sentence": self._sentence_view(row["sentence"]), "text": row["text"],
                  "paraphrase": self.paraphrase_formula(formula), "surface": used, "origin": origin}
        if vacuity == "unknown":
            result["warning"] = ("Could not decide within budget whether this target is provable from no "
                                 "premises; the item cannot succeed (fail closed).")
        return result

    def _do_add_node(self, name, text=None, anchors=(), parents=(), candidate=None, suggestion=None,
                     surface="auto"):
        self._require_frozen()
        _ident(name, "node name")
        if name in self.nodes:
            raise AssistError(f"Node {name} already exists; use rewrite")
        anchors, parents = self._anchors(anchors), _names(parents, "parents")
        for p in parents:
            if p not in self.nodes:
                raise AssistError(f"Unknown parent node {p!r}")
        if candidate and suggestion:
            raise AssistError("Give at most one of candidate and suggestion")
        ref = candidate or suggestion
        if ref:
            pool = self.candidates if candidate else self.suggestions
            if ref not in pool:
                raise AssistError(f"Unknown {'candidate' if candidate else 'suggestion'} {ref!r}")
            offered = pool[ref]["formula"]
            formula = offered if text is None else self._parse(text, surface)[0]
            kind = "proposer" if candidate else "suggestion"
            origin = f"{kind}-verbatim" if formula == offered else f"{kind}-edited"
        else:
            if text is None:
                raise AssistError("add_node needs text, a candidate, or a suggestion")
            formula, _ = self._parse(text, surface)
            origin = "hand-written"
            offered = self._offered(formula)
            if offered:
                origin, ref = offered[0] + "-verbatim", offered[1]
        self.nodes[name] = Node(name, formula, self._canonical(formula), anchors, parents, origin, ref)
        return {"node": self.node_view(name)}

    def _do_accept(self, candidate, name, anchors=(), parents=()):
        """Accept a proposer candidate verbatim (alias of add_node with candidate)."""
        return self._do_add_node(name, anchors=anchors, parents=parents, candidate=candidate)

    def _do_rewrite(self, name, text=None, anchors=None, parents=None, surface="auto"):
        if name not in self.nodes:
            raise AssistError(f"Unknown node {name!r}")
        node = self.nodes[name]
        formula = node.formula if text is None else self._parse(text, surface)[0]
        new_anchors = node.anchors if anchors is None else self._anchors(anchors)
        new_parents = node.parents if parents is None else _names(parents, "parents")
        if parents is not None:
            below = self._descendants(name) | {name}
            for p in new_parents:
                if p not in self.nodes:
                    raise AssistError(f"Unknown parent node {p!r}")
                if p in below:
                    raise AssistError(f"Parent {p} would create a cycle")
        if (formula, new_anchors, new_parents) == (node.formula, node.anchors, node.parents):
            raise AssistError("Rewrite changes nothing")
        node.history.append({"text": node.text, "anchors": list(node.anchors), "parents": list(node.parents),
                             "origin": node.origin})
        if formula != node.formula:
            offered = self._offered(formula)
            if offered:
                node.origin, node.source_ref = offered[0] + "-verbatim", offered[1]
            elif node.origin.endswith("-verbatim"):
                node.origin = node.origin.replace("-verbatim", "-edited")
        node.formula, node.text, node.anchors, node.parents = formula, self._canonical(formula), new_anchors, new_parents
        self._invalidate(name)
        return {"node": self.node_view(name), "invalidated_checks": sorted(
            {name, *(n.name for n in self.nodes.values() if name in n.parents)})}

    def _do_remove_node(self, name):
        if name not in self.nodes:
            raise AssistError(f"Unknown node {name!r}")
        children = sorted(n.name for n in self.nodes.values() if name in n.parents)
        if children:
            raise AssistError(f"Node {name} is a parent of {', '.join(children)}; rewrite those first")
        del self.nodes[name]
        self.checks.pop(name, None)
        return {"removed": name}

    def _do_declare(self, name, gloss, kind="predicate", arguments=(), sort=None, verbalisation=None,
                    acknowledge=()):
        """Add vocabulary through the ``ve propose``-style gates. Gloss required."""
        from ..english import EnglishVocabulary
        from ..english_phrases import BLOCKED, content_tokens, nearest
        # Targets are frozen in the original vocabulary, never in newly invented words.
        self._require_frozen()
        _ident(name, "symbol")
        if kind not in ("predicate", "constant", "sort"):
            raise AssistError("kind must be predicate, constant or sort")
        taken = {*self.env.sorts, *self.env.predicates, *self.env.constants}
        if name in taken:
            raise AssistError(f"Symbol {name} is already declared")
        if type(gloss) is not str or len(gloss.strip()) < 3 or gloss.strip().lower() == name.replace("_", " "):
            raise AssistError("A gloss is required: say in words what the symbol means (not just its name)")
        acknowledge = set(_names(acknowledge, "acknowledge"))
        data = self.env.to_dict()
        if kind == "predicate":
            arguments = _names(arguments, "arguments")
            if len(arguments) not in (1, 2) or any(a not in self.env.sorts for a in arguments):
                raise AssistError("A predicate needs one or two declared argument sorts")
            data["vocabulary"]["predicates"][name] = {"arguments": list(arguments), "description": gloss.strip()}
        elif kind == "constant":
            if sort not in self.env.sorts:
                raise AssistError("A constant needs a declared sort")
            data["vocabulary"]["constants"][name] = {"sort": sort, "description": gloss.strip()}
        else:
            data["vocabulary"]["sorts"][name] = {"description": gloss.strip()}
        flags = []
        # Gate 1 (as in ve propose): near-duplicates of existing wording need acknowledgement.
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            words = EnglishVocabulary(self.env, vocabulary=self.overlay, accept_suggested_vocabulary=True)
        phrase = (verbalisation or "").replace("{0}", "").replace("{1}", "").strip() or name.replace("_", " ")
        for row in nearest(phrase, words):
            if row["near_duplicate"]:
                flags.append({"flag": row["symbol"], "reason": "near-duplicate of existing " + row["kind"],
                              "detail": {k: row[k] for k in ("wording", "edit_distance", "shared_stem",
                                                             "content_overlap")}})
        if kind == "predicate" and set(content_tokens(phrase)) & BLOCKED:
            raise AssistError("Wording contains blocked relational or negative content; declare a neutral name")
        # Gate 2: the new symbol must not be a target conclusion under another name.
        for tid, row in self.targets.items():
            target_words = content_tokens(self.sentences[row["sentence"]]["text"])
            target_words -= {c.lower() for c in self.env.constants}
            symbol_words = content_tokens(gloss + " " + name.replace("_", " ") + " " + phrase)
            symbol_words -= {c.lower() for c in self.env.constants}
            if target_words and symbol_words and (target_words <= symbol_words or symbol_words <= target_words):
                flags.append({"flag": "conclusion:" + tid, "reason": "gloss/name restates target sentence " + tid,
                              "detail": {"target_sentence": self.sentences[row["sentence"]]["text"]}})
        missing = sorted({f["flag"] for f in flags} - acknowledge)
        if missing:
            raise AssistError("Declaration blocked; acknowledge each flag if intended: " + ", ".join(missing)
                              + ". Flags: " + json.dumps(flags, ensure_ascii=False))
        stray = acknowledge - {f["flag"] for f in flags}
        if stray:
            raise AssistError("Acknowledgement names no raised flag: " + ", ".join(sorted(stray)))
        new_env = Environment(data)
        overlay = deepcopy(self.overlay)
        if overlay is not None or verbalisation:
            overlay = overlay or {"format": "ve.english-vocabulary@1", "sorts": {}, "predicates": {}}
            overlay["environment_id"] = new_env.environment_id
            if verbalisation and kind == "predicate":
                overlay["predicates"][name] = {"verbalisation": verbalisation, "suggested": True}
            if verbalisation and kind == "sort":
                raise AssistError("Sort wording is not supported here; use the sort name")
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                try:
                    EnglishVocabulary(new_env, vocabulary=overlay, accept_suggested_vocabulary=True)
                except VEError as exc:
                    raise AssistError("Verbalisation fails the English template linter: " + exc.message) from exc
        self.env, self.overlay = new_env, overlay
        self.declared[name] = {"kind": kind, "gloss": gloss.strip(), "acknowledged": sorted(acknowledge)}
        # Certificates and models bind the environment identity: recheck silently.
        rechecked = sorted(self.checks)
        for step in rechecked:
            self.checks[step] = self._check(self.nodes[step], self.checks[step].get("invariants") or ())
        return {"declared": name, "kind": kind, "gloss": gloss.strip(), "acknowledged": sorted(acknowledge),
                "environment_id": self.env.environment_id, "rechecked": rechecked}

    def _do_check_step(self, name, invariants=(), suggest_premises=False):
        """Does node ``name`` follow from its parents? follows / countermodel / unknown."""
        if name not in self.nodes:
            raise AssistError(f"Unknown node {name!r}")
        node = self.nodes[name]
        if node.kind != "step":
            raise AssistError(f"{name} is an assumption (no parents); only steps are checked")
        if suggest_premises and not self.options["premise_suggestions"]:
            raise AssistError("Premise suggestions are disabled in this session (option premise_suggestions)")
        record = self._check(node, tuple(_names(invariants, "invariants")))
        self.checks[name] = record
        result = {"node": name, "status": record["status"], "parents": list(node.parents),
                  "conclusion": node.text, "conclusion_paraphrase": self.paraphrase_formula(node.formula)}
        if record["status"] == "follows":
            result["certificate_digest"] = record["certificate_digest"]
            if record.get("contradictory_parents"):
                result["warning"] = "The parents are jointly contradictory; the step follows vacuously."
        elif record["status"] == "countermodel":
            result["countermodel"] = record["explanation"]
            result["model_id"] = record["model_id"]
        else:
            result["detail"] = "No certificate and no countermodel within budget (not a refutation)."
        if suggest_premises and record["status"] != "follows":
            result["premise_suggestions"] = self._suggest_premises(node)
        return result

    def _suggest_premises(self, node):
        """Off by default. Suggestions can assume the gap away: each is labelled."""
        from .premises import suggest_premises
        rows = suggest_premises(self, node)
        out = []
        for row in rows:
            sid = f"s{len(self.suggestions) + 1}"
            self.suggestions[sid] = {"formula": row["formula"], "for": node.name, "kind": row["kind"]}
            view = {k: v for k, v in row.items() if k != "formula"}
            out.append({"id": sid, **view, "text": self._canonical(row["formula"]),
                        "paraphrase": self.paraphrase_formula(row["formula"])})
        return out

    def _do_waive(self, sentence, reason):
        if sentence not in self.sentences:
            raise AssistError(f"Unknown sentence id {sentence!r}")
        if type(reason) is not str or len(reason.strip()) < 3:
            raise AssistError("A waiver needs a reason")
        if any(row["sentence"] == sentence for row in self.targets.values()):
            raise AssistError("A target sentence cannot be waived")
        self.waivers[sentence] = reason.strip()
        return {"waived": sentence, "reason": reason.strip()}

    def _resolve(self, ref):
        if ref in self.nodes:
            return self.nodes[ref].formula
        if ref in self.candidates:
            return self.candidates[ref]["formula"]
        if ref in self.targets and self.targets[ref]["formula"] is not None:
            return self.targets[ref]["formula"]
        return self._parse(ref, "auto")[0]

    def _do_compare(self, a, b):
        """Compare two formulas (node names, candidate ids, target ids or VE text)."""
        from .proposer import compare_formulas
        return compare_formulas(self, self._resolve(a), self._resolve(b))

    def _do_propose(self, sentence, k=None, note=None):
        from .proposer import run_propose
        return run_propose(self, sentence, k=k, note=note)

    def _do_record_usage(self, role, input_tokens=0, output_tokens=0, note=None):
        if role not in ("author", "proposer", "auditor"):
            raise AssistError("role must be author, proposer or auditor")
        if any(type(v) is not int or v < 0 for v in (input_tokens, output_tokens)):
            raise AssistError("Token counts must be nonnegative integers")
        return {"recorded": role}
