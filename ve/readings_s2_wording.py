"""The English of S2a across readings (docs/spec/composition-s2.md 2.3), from checked verdicts only, every sentence
through W7's gate (`ve/readings_s2_english.py`).

S2's own Python construction, kept apart from `ve/readings_route.py`, whose S1 answer is relayed from Lean
(lean-first batch 3, `tools/relay_lint.py`): S2 is not relayed yet, so its wording failures are its own diagnostics.
"""
from __future__ import annotations

from .errors import VEError
from .readings_route import Wording, _article


def report_english(doc, route):
    """The sentences of 2.3 for the report's verdicts across readings: the conflict status, the premise status, the
    dead readings and the finding of 1.8."""
    from .readings_verdicts import Enumerated, Superposed
    if not isinstance(route, (Superposed, Enumerated)):
        return []
    return S2Wording(doc, route).report()


def query_english(doc, conclusion, data):
    """The sentences of 2.3 for one ALL, SOME or NONE query across readings."""
    from .readings_verdicts import Enumerated, Superposed, context
    route = context(doc)
    if not isinstance(route, (Superposed, Enumerated)):
        return []
    return S2Wording(doc, route).query(conclusion, data)


class S2Wording:
    """2.1's slots on one document: sentence numbers, reading names, conclusions and pulled situations."""

    def __init__(self, doc, route):
        from . import readings_s2_english as E
        from .environment import wording_reserved_prefixes
        self.E = E
        self.doc, self.route = doc, route
        self.s1 = Wording(doc)
        self.numbers = {unit["id"]: n for n, unit in enumerate(doc["units"], 1)}
        self.sets = route.sets
        self.set_number = {R.id: self.numbers[R.unit] for R in self.sets}
        self.names = {R.id: self.s1.reading_names(R.id) for R in self.sets}
        self.slots = E.Slots(numbers={str(n) for n in self.numbers.values()},
                             readings={name for names in self.names.values() for name in names if type(name) is str},
                             reserved=wording_reserved_prefixes(doc["environment"].profiles),
                             author_names=frozenset(self.s1.admission.senv.author_environment().predicates))
        senv = self.s1.admission.senv
        self.frame = senv.frame
        # Under the completion the filled tables (Lean's, `filled_tables`) are base predicates of the filled frame
        # but no author fact: a shown situation is followed by their points instead (`gaps`).
        self.tables = route.source.filled_tables
        self.author = set(senv.author_environment().predicates) - set(self.tables)
        # Lean's elaboration names each generated declaration and its producing
        # layer. A spelling is never evidence that a model table is a decision.
        self.generated = _active_generated(route.row["generated_predicates"], doc["environment"].profiles)
        self.decisions = self._decision_names()

    # -- slots

    def readings(self, choice):
        """[(sentence number, reading name)] for a choice or assumed list, in source order."""
        chosen = {s: i for s, i in choice}
        return [(self.set_number[R.id], self.name(R.id, chosen[R.id])) for R in self.sets if R.id in chosen]

    def name(self, set_id, i):
        """The `<reading>` name of candidate `i` of `set_id`; a reading the slot cannot show is refused here."""
        return self.E.shown(self.names[set_id][i])

    def conclusion(self, ast):
        """`<conclusion>`: the conclusion's canonical sentence on the existing English surface, in italics; it is
        read back by that surface's all-derivations parser to the conclusion itself before it is shown."""
        from .ast import formula_from_data
        text = self.E.canonical_sentence(self.frame, formula_from_data(self.frame, ast),
                                         "the conclusion's sentence does not read back to the conclusion",
                                         statement_layer=True)
        slot = f"*{text}*"
        self.slots.conclusions.add(slot)
        return slot

    def _decision_names(self):
        """Every decision predicate a rule of the document or of a candidate generates, with what it decides:
        (kind, rule name, party or ranks, owner (set, index) or None)."""
        from .readings_sup import position, qualify
        out = {}

        def add(rule, owner, name):
            root = name.replace("-", "_")
            if rule.get("mode", "strict") == "default":
                out[f"soft__excepted__{root}"] = ("excepted", rule, None, owner)
            for party in rule.get("alterable", []):
                out[f"soft__off__{root}__{party}"] = ("off", rule, party, owner)

        source = self.route.source
        for _, content in source.fixed_units():
            for rule in content.rules():
                add(rule, None, rule["name"])
        for R in self.sets:
            for i, a in enumerate(R.candidates):
                for rule in (a.content.rules() if a.content is not None else []):
                    add(rule, (R.id, i), rule["name"])
                    add(rule, (R.id, i), qualify(position(self.sets, R.id, i), rule["name"]))
        return out

    def situation(self, data, choice):
        """`<situation>` (2.1): the pulled situation of a model of the reading `choice` names: the elements by
        sort, the author's base facts, and each decision as a supposition attributed to who decides; no choice
        vocabulary and no generated name."""
        words = self.s1.words
        facts = []
        for sort in sorted(data["domains"]):
            if sort == "ve__reading":
                continue
            noun = words.sorts[sort]
            for name in sorted(data["domains"][sort]):
                facts.append(f"{name} is {_article(noun)} {noun}")
        relations = data.get("relations", {})
        for predicate in sorted(relations):
            if predicate in self.author:
                for row in sorted(relations[predicate]):
                    facts.append(words.predicates[predicate].format(*row))
        chosen = {(s, i) for s, i in choice}
        own = self._choice_decisions(choice)
        for predicate in sorted(relations):
            if predicate in self.author or predicate not in self.generated:
                continue
            for row in sorted(relations[predicate]):
                phrase = (self._decision(predicate, row, chosen) if own is None else
                          self._choice_decision(own, predicate, row, chosen))
                if phrase is not None:
                    facts.append("suppose " + phrase)
                elif self.generated[predicate]["layer"] in ("soft", "rights"):
                    # Review A of compose-s2 looprecheck2: a decision the situation needs is never left out.
                    raise VEError(f"InvalidInput: a situation's decision table {predicate} has no wording")
        text = "; ".join(facts) if facts else "nothing exists"
        self.slots.situations.add(text)
        return text

    def gaps(self, data):
        """The filled gaps shown after a situation of `data` under the completion (readings-defaults 2.2): every point
        of every filled table, with the model's answer; none outside the completion."""
        found = filled_gaps(self.frame, self.tables, data)
        self.slots.clauses.update(clause for clause, _ in found)
        return found

    def _choice_decisions(self, choice):
        """On the enumerated route a model is one of the choice's own document, so its decision tables are the ones
        that document generates (`gen_keys`: exceptions, switches, outweighing, limitations, their conditions and
        the bar, on every chain): (the choice's side, generated name → key). None on the superposed route."""
        from .readings_verdicts import Enumerated
        if not isinstance(self.route, Enumerated):
            return None
        own = self.route._choice({s: i for s, i in choice})
        if own.chain == "norms":
            return own.side, {}
        return own.side, {generated: key for key, generated, _ in own.side.gen_keys()}

    def _rule_owner(self, name, chosen):
        """(True, None) when the rule named `name` is a candidate's of the choice, (False, n) when sentence n's. Every
        rule a content states is found (`Content.rules`: a norm, and every rule-bearing field of every line kind, a
        power line's liberty and recognition included; compose-s2 fix4 A2)."""
        def names(content):
            return [] if content is None else [rule["name"] for rule in content.rules()]
        for R in self.sets:
            for i, a in enumerate(R.candidates):
                if (R.id, i) in chosen and name in names(a.content):
                    return True, None
        for uid, content in self.route.source.fixed_units():
            if name in names(content):
                return False, self.numbers[uid]
        raise VEError(f"InvalidInput: no sentence of the reading states rule {name}")

    def _choice_decision(self, own, predicate, row, chosen):
        """`<decision>` (2.1) for a decision table of a choice's own document, as S1 words it for a reading."""
        side, keys = own
        key = keys.get(predicate)
        if key is None:
            return None
        subject = _series(list(row))
        soft = side.soft.env.soft or {}
        if key[0] in ("excepted", "off"):
            mine, number = self._rule_owner(key[1], chosen)
            sentence = "this sentence" if mine else f"sentence {number}"
            if key[0] == "off":
                return f"{key[3]} has turned {sentence} off for {subject}"
            rule = next((r for r, name, bearer in side.keyed_rules() if name == key[1] and bearer == key[2]), None)
            decided = ((rule.exception or {}).get("decided_by") if rule is not None else None) or \
                soft.get("exception_decider")
            target = "the exception" if mine else f"the exception to {sentence}"
            return f"{self.s1.decider(decided)} decides {target} applies to {subject}"
        if key[0] == "outweighs":
            who = self.s1.decider(soft.get("outranking", {}).get("decided_by"))
            return f"{who} decides that {key[2]} outweighs {key[3]} for {subject}"
        rd = side.rights
        if key[0] == "lim":
            limit = next(item for item in rd.limitations if item["name"] == key[1])
            who = limit["decided_by"]
        elif key[0] == "cond":
            limit = next(item for item in rd.limitations if item["name"] == key[1])
            condition = next(item for item in limit["conditions"] if item["name"] == key[3])
            who = condition.get("decided_by") or limit["decided_by"]
        else:
            who = rd.bar["decided_by"]
        return f"{self.s1.decider(who)} decides that " + rd.wordings[predicate].format(*row)

    def _decision(self, predicate, row, chosen):
        subject = _series(list(row))
        soft = getattr(self.frame, "soft", None) or {}
        key = self.generated[predicate]["key"]
        if key is not None and "outweighs" in key:
            low, high = key["lower"], key["higher"]
            outranking = soft.get("outranking", {})
            return f"{self.s1.decider(outranking.get('decided_by'))} decides that {low} outweighs {high} for {subject}"
        entry = self.decisions.get(predicate)
        if entry is None:
            return None
        kind, rule, party, owner = entry
        own = owner is not None
        if own and owner not in chosen:
            return None  # an unchosen reading's table is empty (quiescence); never shown
        sentence = "this sentence" if own else f"sentence {self.s1.rule_unit(rule['name'])}"
        if kind == "off":
            return f"{party} has turned {sentence} off for {subject}"
        decided = (rule.get("exception") or {}).get("decided_by") or soft.get("exception_decider")
        target = "the exception" if own else f"the exception to {sentence}"
        return f"{self.s1.decider(decided)} decides {target} applies to {subject}"

    def classification(self, conflict):
        """The lower route's classification line of a witness (R4 follows it), each rule of a candidate named as
        the author named it with ` under <set>@<v>:<i>` (6)."""
        sorts, values = conflict.get("sorts", []), conflict["tuple"]
        setting = ", ".join(f"{sort} {value}" for sort, value in zip(sorts, values))
        target = conflict["target"]
        kind = f"pair conflict on {target}" if "->" in target else f"strict collision on {target}"
        rules = conflict.get("selected")
        if not rules:
            return f"CONFLICT: {kind} at {setting}"
        return (f"CONFLICT: {kind} at {setting}: " +
                "; ".join(f"rule {self._rule_name(name)} {verb}" for name, verb in rules))

    def _rule_name(self, name):
        versions = {R.id: R.version for R in self.sets}
        for entry in self.route.row.get("names", []):
            for candidate in entry["candidates"]:
                for original, qualified in candidate["names"]:
                    if qualified == name:
                        return f"{original} under {entry['set']}@{versions[entry['set']]}:{candidate['index']}"
        return name

    # -- E3's lines (2.3 item 1)

    def provided(self, used):
        """E3's lines for the slot labels an answer uses, each read by its kind (`slot_label`), never by its ending:
        a coupling or narrowing id may itself be `one` or `quiet` (compose-s2 looprecheck1 A)."""
        from .readings_sup import slot_label
        E, lines = self.E, []
        quiet = False
        for label in used:
            if label.startswith(PAIR_LABEL):
                lines.append(E.pair_line(self.pair_premise(label), self.slots))
                continue
            decoded = slot_label(label)
            if decoded.kind == "one":
                R = self._set(decoded.set, decoded.version, label)
                lines.append(E.one_reading(self.set_number[R.id], len(R.candidates), self.slots))
            elif decoded.kind in ("own", "shared"):
                quiet = True
            elif decoded.kind == "coupling":
                from .readings_english import coupling_sentence
                coupling = self._restriction(self.route.couplings, decoded, label)
                sets = {R.id: {"unit": R.unit} for R in self.sets}
                lines.append(E.gated("E5", coupling_sentence(coupling, sets, self.doc["units"]), self.slots))
            elif decoded.kind == "narrowing":
                narrowing = self._restriction(self.route.narrowings, decoded, label)
                R = self._set(narrowing["set"], narrowing["version"], label)
                cited = [self.numbers[u] for u in narrowing["reason_spans"]]
                for i, a in enumerate(R.candidates):
                    if a.id not in narrowing["keeps"]:
                        lines.append(E.narrowed(self.set_number[R.id], self.name(R.id, i), cited, self.slots))
            else:
                raise VEError(f"InvalidInput: unknown slot label kind {decoded.kind}")
        if quiet:
            lines.append(E.quiet(self.slots))
        return ([E.provided(self.slots)] + lines) if lines else []

    def pair_premise(self, label):
        """norm-defaults 4.1's pair sentence for a used `Fill_T` label `unsaid:pair:<r>,<m>` (readings-defaults 2.2):
        `r` must be a regulated obligation of the frame whose declared permission is `m`; any other label is refused,
        never worded."""
        from .norm_english import pair_sentence
        body = label[len(PAIR_LABEL):]
        required, _, permission = body.partition(",")
        decl = self.frame.predicates.get(required) if required else None
        regulated = getattr(decl, "regulated", None)
        if (regulated is None or regulated.role != "obligation" or not permission
                or regulated.permission != permission):
            raise VEError(f"InvalidInput: slot label {label} names no declared pair")
        return pair_sentence(self.frame, required)

    def _set(self, set_id, version, label):
        R = next((R for R in self.sets if (R.id, R.version) == (set_id, version)), None)
        if R is None:
            raise VEError(f"InvalidInput: slot label {label} names no open reading set")
        return R

    @staticmethod
    def _restriction(items, decoded, label):
        found = next((item for item in items if item["id"] == decoded.key), None)
        if found is None:
            raise VEError(f"InvalidInput: slot label {label} names no {decoded.kind}")
        return found

    def independent(self, mentions):
        return [self.E.independent(self.set_number[R.id], self.slots) for R in self.sets if R.id not in mentions]

    def _mentions(self, used):
        """The open sets the used labels mention: a slot leaf by its bit predicates, and on the enumerated route a
        coupling or narrowing label by the sets it restricts."""
        from .readings_sup import bit_name, bits_of, in_force
        asts = {entry["label"]: entry["ast"] for entry in self.route.row.get("slot", [])}
        from .readings_sup import slot_label
        restricted = set()
        for label in used:
            if label.startswith(PAIR_LABEL):
                continue  # a pair premise of the completion mentions no open set
            decoded = slot_label(label)
            if decoded.kind == "coupling":
                coupling = self._restriction(self.route.couplings, decoded, label)
                restricted.update(ref["set"] for ref in coupling["sets"])
            elif decoded.kind == "narrowing":
                narrowing = self._restriction(self.route.narrowings, decoded, label)
                restricted.update(R.id for R in self.sets if in_force(R, narrowing))
        out = []
        for position, R in enumerate(self.sets, 1):
            bits = {bit_name(position, j) for j in range(bits_of(len(R.candidates)))}
            if R.id in restricted or any(bits & _predicates(asts.get(label, [])) for label in used):
                out.append(R.id)
        return out

    # -- the report (2.3 items 1, 3 and 6)

    def report(self):
        from .readings_verdicts import Enumerated
        if isinstance(self.route, Enumerated):
            # readings-defaults RD-3: Lean's plan for the conflict question, then for the premises.
            return (self.plan(self.route.conflict_answer()) + self.plan(self.route.premises_answer()))
        E, route, lines = self.E, self.route, []
        k = len(self.sets)
        finding = route.row.get("finding")
        if finding is not None:
            sets = finding["text"].split(": ", 1)[1].split(", ")
            lines.append(E.not_superposed([self.set_number[s] for s in sets], self.slots))
        conflict = route.conflict(())
        if conflict["status"] == "CONFLICT-FREE":
            lines.append(E.every_result(k, "conflict_free", self.slots))
            used = self._dependencies(conflict)
            lines += self.provided(used)
            lines += self.independent(self._mentions(used))
        elif conflict["status"] == "CONFLICT" and "model" in conflict:
            lines.append(E.named_result(self.readings(conflict["choice"]), "conflict", self.slots,
                                        situation=self.situation(conflict["model"], conflict["choice"]),
                                        gaps=self.gaps(conflict["model"])))
            lines.append(self.classification(conflict))
        elif conflict["status"] == "CONFLICT":
            for witness in conflict.get("witnesses", []):
                lines.append(E.named_result(self.readings(witness["choice"]), "conflict", self.slots,
                                            situation=self.situation(witness["model"], witness["choice"]),
                                            gaps=self.gaps(witness["model"])))
                if witness.get("status_text"):
                    lines.append(witness["status_text"])
        premises = route.premises()
        if premises["status"] == "model" and "model" in premises:
            lines.append(E.named_result(self.readings(premises["choice"]), "premise_model", self.slots,
                                        situation=self.situation(premises["model"], premises["choice"]),
                                        gaps=self.gaps(premises["model"])))
        elif premises["status"] == "INCONSISTENT" and premises.get("evidence") == "certificate":
            # A certificate with A = [] (2.3 item 1): E3 and E13 from what it and its conflict certificates rely on.
            lines.append(E.every_result(k, "inconsistent", self.slots))
            used = self._dependencies(premises)
            lines += self.provided(used)
            lines += self.independent(self._mentions(used))
        for dead in route.dead_readings() or []:
            lines.append(E.dead_reading(self.set_number[dead["set"]], self.name(dead["set"], dead["index"]),
                                        self.slots))
        return lines

    # -- a query (2.3 items 1, 2, 4, 5 and 7)

    def query(self, conclusion_ast, data):
        from .readings_verdicts import Enumerated
        if isinstance(self.route, Enumerated):
            slot = self.conclusion(conclusion_ast)
            return self.plan(self.route.query_answer(conclusion_ast, data.get("assumed")), slot)
        E, lines = self.E, []
        k = len(self.sets)
        verdict = data["verdict"]
        # Review A of compose-s2 looprecheck1: a result under named readings is worded under exactly those readings
        # (2.3 item 2, on either route); E10, E26, E27 and E28 speak of every reading and never word one.
        assumed = data.get("assumed") or []
        slot = self.conclusion(conclusion_ast)
        if verdict == "ALL":
            if assumed:
                lines.append(E.named_result(self.readings(assumed), "follows", self.slots, conclusion=slot))
            else:
                lines.append(E.every_result(k, "follows", self.slots, conclusion=slot))
            # Review A1 of compose-s2 fix4: the conditions and the independence statement are both worded from the
            # answer's one dependency set, its conflict certificates' included. Combined over the compatible choices
            # (review A of compose-s2 looprecheck2) the set holds the couplings and narrowings that excluded the
            # others (E3 with E5 and E7), and no independence is claimed.
            used = self._dependencies(data)
            lines += self.provided(used)
            if data.get("evidence") == "certificate":
                lines += self.independent(set(self._mentions(used)) | {s for s, _ in assumed})
        elif verdict == "SOME":
            lines.append(E.named_result(self.readings(data["proof"]["choice"]), "follows", self.slots,
                                        conclusion=slot))
            lines += self.provided(self._dependencies(data["proof"]))
            lines.append(self._countermodel(data["countermodel"]))
        elif verdict == "NOT ALL":
            lines.append(self._countermodel(data["countermodel"]))
        elif verdict == "NONE":
            if k >= 2 and not assumed:
                lines.append(E.none_result(k, self.slots))
            lines += [self._countermodel(c) for c in data["countermodels"]]
            lines += self.provided(self._restrictions(data))
        elif verdict == "UNKNOWN" and "countermodel" in data and data.get("budget") == {"max_choices": 64} \
                and not assumed:
            lines.append(E.over_budget(self.slots))
            lines.append(self._countermodel(data["countermodel"]))
        return lines

    # -- Lean's English plan (readings-defaults 2.4; the enumerated route from RD-3)

    def plan(self, answer, slot=None):
        """The sentences of Lean's plan of `answer` (`Readings.englishPlan`), each rendered as its frame says and
        through its gate; which sentences an answer gets, the readings and the model each names, its filled gaps and
        its labels are Lean's. A line Python cannot render as planned is `CheckerUnavailable`, never left out."""
        from .errors import CheckerUnavailable
        out = []
        for line in answer["english"]:
            try:
                out.append(self._plan_line(line, answer, slot))
            except (KeyError, TypeError, ValueError, IndexError) as exc:
                raise CheckerUnavailable(f"ReadingsConformance: Lean's English plan has a line Python cannot render: "
                                         f"{line}") from exc
        return out

    def _plan_line(self, line, answer, slot):
        from .errors import CheckerUnavailable
        from .readings_sup import slot_label
        E = self.E
        frame, label = line["frame"], line["label"]
        kind = PLAN_RESULTS[line["result"]] if line["result"] is not None else None
        readings = [(s, i) for s, i in line["readings"]]
        if line["model"] is not None:
            from .ast import decimal_value
            piece, _, k = line["model"].partition("@")
            entry = answer["per_choice"][decimal_value(k)]
            model, choice = entry["shown"][piece], [(s, i) for s, i in entry["choice"]]
            if frame != "E12" or readings != choice:
                raise CheckerUnavailable("ReadingsConformance: Lean's plan shows a model under another frame")
            return E.named_result(self.readings(choice), kind, self.slots, situation=self.situation(model, choice),
                                  gaps=self.plan_gaps(model, line["gaps"]))
        if frame in ("E26", "E10"):
            text = E.every_result(len(self.sets), kind, self.slots, conclusion=slot)
            if not text.startswith("Under every reading of the open sentence" if frame == "E26" else
                                   f"Under every reading of the {len(self.sets)} open sentences"):
                raise CheckerUnavailable("ReadingsConformance: Lean's plan names the wrong every-reading frame")
            return text
        if frame == "E12":
            return E.named_result(self.readings(readings), kind, self.slots, conclusion=slot)
        if frame == "E29":
            return E.not_superposed([self.set_number[s] for s, _ in readings], self.slots)
        if frame == "E3":
            return E.provided(self.slots)
        if frame == "P1":
            return E.pair_line(self.pair_premise(label), self.slots)
        if frame == "E5":
            from .readings_english import coupling_sentence
            coupling = self._restriction(self.route.couplings, slot_label(label), label)
            sets = {R.id: {"unit": R.unit} for R in self.sets}
            return E.gated("E5", coupling_sentence(coupling, sets, self.doc["units"]), self.slots)
        if frame == "E7":
            narrowing = self._restriction(self.route.narrowings, slot_label(label), label)
            [(s, i)] = readings
            cited = [self.numbers[u] for u in narrowing["reason_spans"]]
            return E.narrowed(self.set_number[s], self.name(s, i), cited, self.slots)
        if frame == "E13":
            [(s, _)] = readings
            return E.independent(self.set_number[s], self.slots)
        if frame == "E17":
            [(s, i)] = readings
            return E.dead_reading(self.set_number[s], self.name(s, i), self.slots)
        if frame == "E27":
            return E.none_result(len(self.sets), self.slots)
        if frame == "E28":
            return E.over_budget(self.slots)
        if frame == "status" and type(label) is str:
            return label
        raise CheckerUnavailable(f"ReadingsConformance: Lean's English plan has an unknown frame {frame}")

    def plan_gaps(self, model, gaps):
        """The filled gaps Lean's plan lists after a shown situation (readings-defaults 2.2): each point's clause
        (norm-defaults' `point_clause`) and the filling's answer, in Lean's order."""
        from types import SimpleNamespace
        from .norm_defaults_english import point_clause
        situation = SimpleNamespace(constants={name: value for name, value in (model.get("constants") or {}).items()
                                               if name in self.frame.constants})
        found = [(point_clause(self.frame, situation, predicate, tuple(ids)), value) for predicate, ids, value in gaps]
        self.slots.clauses.update(clause for clause, _ in found)
        return found

    @staticmethod
    def _dependencies(data):
        """The slot labels a Lean-checked answer depends on (`reading_premises_used`, `Superposed._dependencies` on
        the superposed route, the restrictions on the enumerated route); an answer without them is refused, never
        worded as depending on no reading."""
        if "reading_premises_used" not in data:
            raise VEError("InvalidInput: a checked answer's wording needs the reading premises it depends on")
        return data["reading_premises_used"]

    @staticmethod
    def _restrictions(data):
        """The restrictions a combined verdict keeps; a combined verdict without the field is refused, never worded
        as if no coupling or narrowing had selected its choices."""
        if "restrictions" not in data:
            raise VEError("InvalidInput: a verdict combined over the compatible choices needs its restrictions")
        return data["restrictions"]

    def _countermodel(self, counter):
        model = counter.get("model")
        if model is None:
            raise VEError("InvalidInput: a countermodel's wording needs its checked model")
        return self.E.named_result(self.readings(counter["choice"]), "countermodel", self.slots,
                                   situation=self.situation(model, counter["choice"]), gaps=self.gaps(model))


PAIR_LABEL = "unsaid:pair:"
# The result ids of Lean's plan (`Readings.Line.result`) and the kinds `result_sentence` renders.
PLAN_RESULTS = {"R1": "conflict_free", "R2": "follows", "R3": "countermodel", "R4": "conflict", "R5": "premise_model",
                "R6": "inconsistent", "R7": "undecided"}


def filled_gaps(frame, tables, model):
    """[(clause, answer)] for every point of every filled table (`tables`: table → its predicate, from Lean's filled
    document) over the elements of `model`, a situation's or model's JSON: the point's clause (norm-defaults'
    `point_clause`) and whether the model's table holds there. In table order, then tuple order."""
    from itertools import product
    from types import SimpleNamespace
    from .norm_defaults_english import point_clause
    situation = SimpleNamespace(constants={name: value for name, value in (model.get("constants") or {}).items()
                                           if name in frame.constants})
    relations = model.get("relations") or {}
    out = []
    for table in sorted(tables):
        predicate = tables[table]
        rows = {tuple(row) for row in relations.get(table, ())}
        domains = [sorted(model["domains"].get(sort, ())) for sort in frame.predicates[predicate].arguments]
        for values in product(*domains):
            out.append((point_clause(frame, situation, predicate, values), values in rows))
    return out


def _active_generated(entries, profiles):
    """Read Lean's declaration provenance only for layers this document activates."""
    active = {"readings"}
    if "soft-norms@0" in profiles:
        active.add("soft")
    if "rights@0" in profiles:
        active.add("rights")
    return {entry["name"]: entry for entry in entries if entry["layer"] in active}


def _series(values):
    values = list(values)
    if len(values) == 1:
        return values[0]
    if len(values) == 2:
        return f"{values[0]} and {values[1]}"
    return ", ".join(values[:-1]) + " and " + values[-1]


def _predicates(ast):
    out, stack = set(), [ast]
    while stack:
        node = stack.pop()
        if type(node) is list and node:
            if node[0] in ("unary", "binary") and type(node[1]) is str:
                out.add(node[1])
            stack.extend(item for item in node[1:] if type(item) is list)
    return out


__all__ = ["S2Wording", "filled_gaps", "query_english", "report_english"]
