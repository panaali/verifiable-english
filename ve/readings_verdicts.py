"""S2a's verdicts across readings (docs/spec/composition-s2.md 4.5, 4.6, 5, 6, 8.6).

Python's prover and model search are untrusted generators. On the superposed route every certificate and model they
find on `sup D` is checked by Lean's readings route (`readings-conflict`, `readings-certificate`, `readings-model`,
`readings-dead`) before a verdict is reported; on the enumerated route each compatible choice's own document is checked
as an ordinary document of the lower route, its conflict status through `readings-choice`. A Lean refusal of
evidence that Python's own check accepted is `CheckerUnavailable`, never a verdict; an exhausted search budget is
UNKNOWN, which asserts nothing. Nothing here is computed for W2's, the pending or the abstaining route (1.1).
"""
from __future__ import annotations

from itertools import product

from .errors import CheckerUnavailable, VEError

BUDGET = {"max_steps": 10_000, "max_domain_size": 2, "max_models": 10_000, "max_evaluations": 100_000}
PENDING = {"status": "UNKNOWN", "reason": "non-assertion reading elaboration pending"}


def context(doc):
    """The verdict context of a loaded document with a content-bearing set, by its route; None on W2's route."""
    if "_readings_s2_context" not in doc:
        row = doc.get("readings_s2")
        route = row["route"] if row is not None else None
        doc["_readings_s2_context"] = (Superposed(doc) if route == "superposed" else
                                       Enumerated(doc) if route == "enumerated" else
                                       Pending(doc) if route in ("pending", "abstention") else None)
    return doc["_readings_s2_context"]


def _used(certificate, count):
    """The indices below `count` that the certificate's trace expands. A literal is closed against without an
    `expand`, so callers count literal premises as used too (an over-approximation, never an omission)."""
    found, stack = set(), [certificate.get("trace")]
    while stack:
        node = stack.pop()
        if type(node) is dict:
            if type(node.get("at")) is int and node["at"] < count:
                found.add(node["at"])
            stack.extend(node.get("children") or [])
            for value in node.values():
                if type(value) is dict:
                    stack.append(value)
    return found


def _literal(formula):
    from .ast import Binary, Bottom, Not, Top, Unary
    inner = formula.body if isinstance(formula, Not) else formula
    return isinstance(inner, (Unary, Binary, Top, Bottom))


class _Route:
    """What every route past the first three rows of 1.1 shares: the decoded document, its open sets and the
    compatible choices (at most 64, else None)."""

    def __init__(self, doc):
        from .readings_route import document_wire
        from .readings_s1 import Document, S1Environment, wire
        from .readings_sup import MAX_CHOICES, choices
        meta = doc["meta"]
        self.doc = doc
        self.row = doc["readings_s2"]
        self.route = self.row["route"]
        self.couplings = list(meta.get("couplings", []))
        self.narrowings = list(meta.get("narrowings", []))
        self.environment = wire(doc["environment"].to_dict())
        units = [{"id": u["id"], "kind": u["kind"], "content": u["content"]} for u in doc["units"]]
        self.document = wire(document_wire(units, meta.get("reading_sets", []), couplings=self.couplings,
                                           narrowings=self.narrowings))
        self.source = Document(S1Environment(self.environment), self.document)
        self.sets = self.source.sets
        found, over = choices(self.sets, self.couplings, self.narrowings, limit=MAX_CHOICES)
        self.choices = None if over else found
        self.numbers = {unit["id"]: n for n, unit in enumerate(doc["units"], 1)}

    def lean(self, kind, **fields):
        from .readings_route import run_lean
        [row] = run_lean([{"id": kind, "kind": kind, "environment": self.environment, "document": self.document,
                           **fields}], timeout=300)
        if row.get("status") != "ok":
            raise CheckerUnavailable(f"ReadingsConformance: Lean refused the {kind} case Python built: "
                                     f"{row.get('error')}")
        return row

    def choice_json(self, choice):
        return [[R.id, choice[R.id]] for R in self.sets]

    def choice_text(self, choice_json):
        versions = {R.id: R.version for R in self.sets}
        return ", ".join(f"{s}@{versions[s]}:{i}" for s, i in choice_json)

    def dropped(self, set_id, index):
        """The narrowing in force that drops candidate `index` of `set_id`, if any (E7, not `DeadReading`)."""
        R = next(R for R in self.sets if R.id == set_id)
        for narrowing in self.narrowings:
            if (narrowing["set"], narrowing["version"]) == (R.id, R.version) and \
                    R.candidates[index].id not in narrowing["keeps"]:
                return narrowing["id"]
        return None

    def candidates(self):
        return [(R.id, i) for R in self.sets for i in range(len(R.candidates))]

    def report_fields(self):
        return {}

    def untaken_text(self, A):
        """Lean's `untakenText`: the named readings, as given, that no compatible choice takes."""
        versions = {R.id: R.version for R in self.sets}
        return "ReadingsUnsatisfiable: no compatible reading takes " + ", ".join(
            f"{s}@{versions[s]}:{i}" if s in versions else f"{s}:{i}" for s, i in A)


class Pending(_Route):
    """1.1 row 2: a pending candidate; every verdict across readings is UNKNOWN with today's reason."""

    def __init__(self, doc):  # noqa: D401 - nothing of 1.2 to 1.9 is computed
        self.doc = doc
        self.route = doc["readings_s2"]["route"]

    def premises(self):
        return dict(PENDING)

    def conflict(self, A=()):
        return dict(PENDING)

    def entailment(self, conclusion_ast, premises=(), assumed=None):
        return {"verdict": "UNKNOWN", "route": self.route, "reason": PENDING["reason"]}

    def report_fields(self):
        return {"status": "UNKNOWN: " + PENDING["reason"]}


# ---------------------------------------------------------------------------------------------------------------
# The superposed route (4.5)

class Superposed(_Route):
    def __init__(self, doc):
        super().__init__(doc)
        from .readings_sup import MAX_CHOICE_CHECKS, choices, superposed_document
        _, contents, soft = superposed_document(self.source)
        self.soft = soft
        self.ext = soft.extended_env
        self.base = soft.elaborated.base_environment()
        self.slot = [(entry["label"], entry["ast"]) for entry in self.row.get("slot", [])]
        self.layers = [formula for _, formula in soft.elaborated.premises()]
        self.assertions = [content.body for content in contents if content.kind == "assertion"]
        # DRI ruling 5: past the checked choices no superposed verdict is claimed.
        self.checked = type(self.row.get("choices_checked")) is int
        found, over = choices(self.sets, self.couplings, self.narrowings, limit=MAX_CHOICE_CHECKS)
        self.all_choices = None if over else found
        self._conflicts = {}
        self._models = {}

    def taken(self, A):
        """Some compatible choice takes every candidate of `A` (Lean's `takenBy`; exact while `checked`)."""
        return self.all_choices is not None and any(all(c.get(s) == i for s, i in A) for c in self.all_choices)

    # -- premise lists in Lean's order (8.4 `supCertificateCheck`, `supModelCheck`, `slotConflictFreeCheck`)

    def _formulas(self, env, asts):
        from .ast import formula_from_data
        return [formula_from_data(env, ast, _generated=True) for ast in asts]

    def _atoms(self, A):
        from .readings_sup import choice_atom
        return [choice_atom(self.sets, s, i) for s, i in A]

    def _full(self, A, gamma=()):
        """slot ++ atoms ++ layers ++ assertions ++ Γ over E′ (the prover prepends background′)."""
        return (self._formulas(self.ext, [ast for _, ast in self.slot] + self._atoms(A)) + self.layers +
                self._formulas(self.ext, self.assertions + list(gamma)))

    def _prove(self, env, slot, rest, conclusion):
        """A certificate of `conclusion` from slot ++ rest (the prover prepends the Background), and the slot labels
        it needs: each slot premise is replaced by ⊤ in turn and dropped when a proof remains. The certificate
        returned is one that never expands a dropped premise, so it checks against the full list as well."""
        from .ast import Top
        from .entailment import prove_entailment
        proof = prove_entailment(env, slot + rest, conclusion, max_steps=BUDGET["max_steps"])
        if proof.status != "Found":
            return None, []
        current = list(slot)
        for k in range(len(slot)):
            trial = current[:k] + [Top()] + current[k + 1:]
            again = prove_entailment(env, trial + rest, conclusion, max_steps=BUDGET["max_steps"])
            if again.status == "Found":
                current, proof = trial, again
        used = [label for k, (label, _) in enumerate(self.slot) if not isinstance(current[k], Top)
                or isinstance(slot[k], Top)]
        return proof.certificate, used

    def _coherence(self, certificate, env):
        """The coherence labels of the Background a certificate expands, or that are literals (a literal is closed
        against without an `expand`): an over-approximation, never an omission."""
        from .background import background
        prefix = [p.formula for p in background(env)]
        used = _used(certificate, len(prefix))
        return [label for label, formula in getattr(env, "soft_premises", ())
                if label.startswith("soft:coherence:") and any(
                    prefix[k] == formula and (k in used or _literal(formula)) for k in range(len(prefix)))]

    def conflict(self, A=()):
        """The conflict status under the atoms of `A` (4.5): certificates for every target over
        Background_base′ ++ slot ++ atoms, or a witness model, each checked by `readings-conflict`."""
        from .ast import Not
        from .entailment import prove_entailment
        from .norms import _bind
        from .readings_sup import CHECK_BUDGET_TEXT
        key = tuple(tuple(x) for x in A)
        if key in self._conflicts:
            return self._conflicts[key]
        if not self.checked or (A and not self.taken(A)):
            result = {"status": "UNKNOWN", "reason": CHECK_BUDGET_TEXT if not self.checked else self.untaken_text(A)}
            self._conflicts[key] = result
            return result
        slot = self._formulas(self.base, [ast for _, ast in self.slot])
        atoms = self._formulas(self.base, self._atoms(A))
        premises = slot + atoms
        certificates, missing, needed = {}, None, set()
        for target, sorts, formula in self.soft.elaborated.conflict_targets():
            certificate, used = self._prove(self.base, slot, atoms, _bind(Not(formula), sorts))
            if certificate is not None:
                certificates[target] = certificate
                needed.update(used)
            elif missing is None:
                missing = target
        assumed = [list(x) for x in A]
        if missing is None:
            row = self.lean("readings-conflict", assumed=assumed, conflict_certificates=certificates)
            if row["verdict"] != "CONFLICT-FREE":
                raise CheckerUnavailable("ReadingsConformance: Lean does not confirm the conflict certificates "
                                         "Python's prover found on the superposed document")
            coherence = set()
            for certificate in certificates.values():
                coherence.update(self._coherence(certificate, self.base))
            used = [label for label, _ in self.slot if label in needed]
            coh = [label for label, _ in self.soft.extended_env.soft_premises if label in coherence]
            result = {"status": "CONFLICT-FREE", "evidence": "certificates", "assumed": assumed,
                      "certificates": certificates, "conditional_on": coh + used, "reading_premises_used": used,
                      "status_text": f"CONFLICT-FREE among rules on the same act, conditional on {len(coh)} "
                                     f"coherence premises" + (f" and {len(used)} reading premises" if used else "")}
        else:
            result = self._witness(A, premises, missing)
        self._conflicts[key] = result
        return result

    def _witness(self, A, premises, missing):
        from .ast import Not, _Checker
        from .evaluate import _Evaluator, _Exhausted
        from .norms import _bind
        from .search import find_countermodel
        for target, sorts, formula in self.soft.elaborated.conflict_targets():
            found = find_countermodel(self.base, premises, _bind(Not(formula), sorts),
                                      max_domain_size=BUDGET["max_domain_size"], max_models=BUDGET["max_models"],
                                      max_evaluations=BUDGET["max_evaluations"])
            if found.status != "Found":
                continue
            model = found.model
            _Checker(self.base, generated=True).formula(formula, tuple(reversed(sorts)))
            evaluator = _Evaluator(self.base, model, BUDGET["max_evaluations"], trace=False)
            try:
                values = next((values for values in product(*(model.domains[s] for s in sorts))
                               if evaluator.formula(formula, tuple(zip(reversed(sorts), reversed(values))))[0]),
                              None)
            except _Exhausted:
                values = None
            if values is None:
                continue
            data = model.to_dict()
            row = self.lean("readings-conflict", assumed=[list(x) for x in A],
                            witness={"model": data, "target": target, "tuple": list(values)})
            if row["verdict"] != "CONFLICT":
                raise CheckerUnavailable("ReadingsConformance: Lean does not confirm the conflict witness Python's "
                                         "search found on the superposed document")
            kind = f"pair conflict on {target}" if "->" in target else f"strict collision on {target}"
            selected = None
            if target in self.soft.elaborated.order:
                role = self.soft.elaborated.env.predicates[target].regulated.role
                pos = "permits" if role == "permission" else "requires" if role == "obligation" else "affirms"
                neg = "forbids" if role == "permission" else "releases" if role == "obligation" else "denies"
                selected = [(rule.name, pos if rule.sign else neg)
                            for rule in self.soft.elaborated.selected_rules(target, model, values)]
            return {"status": "CONFLICT", "evidence": "witness", "assumed": [list(x) for x in A],
                    "target": target, "sorts": list(sorts), "tuple": list(values), "choice": row["choice"],
                    "model": data, "selected": selected,
                    "status_text": f"CONFLICT: {kind} at {', '.join(values)} under "
                                   f"{self.choice_text(row['choice'])}"}
        return {"status": "UNKNOWN", "assumed": [list(x) for x in A],
                "detail": f"tableau budget or open branch: {missing}",
                "status_text": f"UNKNOWN: tableau budget or open branch: {missing}, budget {BUDGET['max_steps']}",
                "budget": dict(BUDGET)}

    def _lean_model(self, model):
        """A model of E′ read over `sup D`'s base vocabulary: the regulated tables are the outcome substitution's
        on the base, so they are dropped (`supVocabulary`)."""
        data = model.to_dict()
        regulated = {name for name, decl in self.ext.predicates.items() if decl.regulated is not None}
        data["relations"] = {name: rows for name, rows in data["relations"].items() if name not in regulated}
        return data

    def model(self, A=(), gamma=(), conclusion=None):
        """A checked model of the premises under `A` (with `conclusion` false when given): its encoded choice and
        the model, or None within the budget. The search runs first on the documents of compatible choices that
        take `A` (smaller vocabularies), each model found there lifted to `sup D` as `base_up` builds it; then on
        `sup D` itself. Lean checks the model on `sup D` either way."""
        from .ast import Bottom, formula_from_data
        from .search import find_countermodel
        key = (tuple(tuple(x) for x in A), repr(gamma), repr(conclusion))
        if key in self._models:
            return self._models[key]
        usable = self.checked and (not A or self.taken(A))
        result = self._lifted(A, gamma, conclusion) if usable else None
        if result is None and usable:
            phi = Bottom() if conclusion is None else formula_from_data(self.ext, conclusion, _generated=True)
            found = find_countermodel(self.ext, self._full(A, gamma), phi,
                                      max_domain_size=BUDGET["max_domain_size"], max_models=BUDGET["max_models"],
                                      max_evaluations=BUDGET["max_evaluations"])
            if found.status == "Found":
                data = self._lean_model(found.model)
                row = self.lean("readings-model", assumed=[list(x) for x in A], premises=list(gamma),
                                conclusion=conclusion, model=data)
                if row["valid"] is not True or row["conclusion_value"] is not False:
                    raise CheckerUnavailable("ReadingsConformance: Lean does not confirm the model Python's search "
                                             f"found on the superposed document ({row.get('first_failing')})")
                result = {"choice": row["choice"], "model": data}
        self._models[key] = result
        return result

    MAX_LIFTS = 16

    def _lifted(self, A, gamma, conclusion):
        from .ast import Bottom, formula_from_data
        from .search import check_countermodel, find_countermodel
        pool = self.all_choices if self.all_choices is not None else self.choices
        if pool is None:
            from .readings_sup import choices
            pool, _ = choices(self.sets, self.couplings, self.narrowings, limit=self.MAX_LIFTS)
        taking = [c for c in pool if all(c.get(s) == i for s, i in A)][:self.MAX_LIFTS]
        for choice in taking:
            own = _ChoiceDocument(self, choice)
            premises = own._all(gamma)
            phi = Bottom() if conclusion is None else formula_from_data(own.env, conclusion, _generated=True)
            found = find_countermodel(own.env, premises, phi, max_domain_size=BUDGET["max_domain_size"],
                                      max_models=BUDGET["max_models"], max_evaluations=BUDGET["max_evaluations"])
            if found.status != "Found" or not check_countermodel(own.env, premises, phi, found.model,
                                                                 max_evaluations=BUDGET["max_evaluations"]).valid:
                continue
            data = self._lift(choice, found.model.to_dict(), own)
            row = self.lean("readings-model", assumed=[list(x) for x in A], premises=list(gamma),
                            conclusion=conclusion, model=data)
            if row["valid"] is True and row["conclusion_value"] is False:
                return {"choice": row["choice"], "model": data}
        return None

    def _lift(self, choice, data, own):
        """`base_up` (4.3) on a model of a choice's document: the bits spell the choice, `ve__here` is one element
        of `ve__reading`, the chosen candidates' decision tables move to their names in `sup D`, every other
        decision table of `sup D` is empty, and the regulated tables are dropped (the outcome substitution)."""
        from .readings_sup import HERE, READING_SORT, bit_name, bits_of
        rename = {}
        for entry in self.row.get("names", []):
            for candidate in entry["candidates"]:
                if choice.get(entry["set"]) == candidate["index"]:
                    rename.update({original: qualified for original, qualified in candidate["names"]})
        regulated = {name for name, decl in own.env.predicates.items() if decl.regulated is not None}
        relations = {name: [] for name in self.base.predicates}
        for name, rows in data["relations"].items():
            if name in regulated:
                continue
            target = rename.get(name, name)
            if target in relations:
                relations[target] = rows
        for position, R in enumerate(self.sets, 1):
            for j in range(bits_of(len(R.candidates))):
                relations[bit_name(position, j)] = [["here"]] if choice[R.id] >> j & 1 else []
        return {"complete": True, "domains": {**data["domains"], READING_SORT: ["here"]},
                "constants": {**data.get("constants", {}), HERE: "here"}, "relations": relations}

    def certificate(self, A=(), gamma=(), conclusion=None):
        """A certificate of `conclusion` (⊥ when None) under `A`, checked by `readings-certificate`; only when the
        conflict status under `A` is CONFLICT-FREE (4.5, 14.8). None within the budget."""
        from .ast import Bottom, formula_from_data
        from .entailment import prove_entailment
        conflict = self.conflict(A)
        if conflict["status"] != "CONFLICT-FREE":
            return None
        phi = Bottom() if conclusion is None else formula_from_data(self.ext, conclusion, _generated=True)
        full = self._full(A, gamma)
        certificate, used = self._prove(self.ext, full[:len(self.slot)], full[len(self.slot):], phi)
        if certificate is None:
            return None
        row = self.lean("readings-certificate", assumed=[list(x) for x in A], premises=list(gamma),
                        conclusion=conclusion, conflict_certificates=conflict["certificates"],
                        certificate=certificate)
        if row["accepted"] is not True:
            raise CheckerUnavailable("ReadingsConformance: Lean does not confirm the certificate Python's prover "
                                     "found on the superposed document")
        return {"certificate": certificate, "assumed": [list(x) for x in A],
                "reading_premises_used": used, "mentions": self._mentions(A, used),
                "conditional_on": list(dict.fromkeys(conflict["conditional_on"] + used))}

    def _mentions(self, A, used):
        """The open sets a used leaf mentions (2.3: a leaf mentions a set when its formula contains a bit
        predicate of that set), with whether an atom of it was assumed."""
        from .readings_sup import bit_name, bits_of
        asts = dict(self.slot)
        mentioned = []
        for position, R in enumerate(self.sets, 1):
            bits = {bit_name(position, j) for j in range(bits_of(len(R.candidates)))}
            if any(R.id == s for s, _ in A) or any(bits & _predicates(asts[label]) for label in used):
                mentioned.append(R.id)
        return mentioned

    # -- the questions of 4.5

    def premises(self):
        from .readings_sup import CHECK_BUDGET_TEXT
        if not self.checked:
            return {"status": "UNKNOWN", "route": "superposed", "reason": CHECK_BUDGET_TEXT}
        found = self.model(())
        if found is not None:
            result = {"status": "model", "route": "superposed", "evidence": "model", "choice": found["choice"],
                      "model": found["model"]}
        else:
            proof = self.certificate((), (), None)
            if proof is not None:
                result = {"status": "INCONSISTENT", "route": "superposed", "evidence": "certificate",
                          "conditional_on": proof["conditional_on"]}
            else:
                conflict = self.conflict(())
                result = {"status": "UNKNOWN", "route": "superposed", "budget": dict(BUDGET),
                          **({"reason": f"conflict status: {conflict['status']}"}
                             if conflict["status"] != "CONFLICT-FREE" else {})}
        result["candidates"] = self.candidate_premises()
        return result

    def candidate_premises(self):
        """Per candidate (4.5): `model`, `dead` (finding), `narrowed` (a narrowing in force drops it, E7),
        `INCONSISTENT` (⊥ certified under its atom, only when CONFLICT-FREE there) or `UNKNOWN`."""
        dead = {(d["set"], d["index"]) for d in (self.dead_readings() or [])}
        out = []
        for s, i in self.candidates():
            entry = {"set": s, "index": i}
            narrowing = self.dropped(s, i)
            if narrowing is not None:
                entry.update(status="narrowed", narrowing=narrowing)
            elif (s, i) in dead:
                entry.update(status="dead")
            elif not self.taken([(s, i)]):
                entry.update(status="UNKNOWN", reason=self.untaken_text([(s, i)]))
            else:
                found = self.model([(s, i)])
                if found is not None:
                    entry.update(status="model", choice=found["choice"])
                elif self.certificate([(s, i)], (), None) is not None:
                    entry.update(status="INCONSISTENT")
                else:
                    entry.update(status="UNKNOWN")
            out.append(entry)
        return out

    def dead_readings(self):
        """`DeadReading: <set>:<i>` for every candidate no compatible choice takes and no narrowing in force drops,
        each with a certificate of ¬χ from `choiceCore D` checked by `readings-dead` (1.9, 14.7). None when the
        compatible choices exceed the checked budget (not computed)."""
        if "_dead" in self.__dict__:
            return self._dead
        from .entailment import prove_entailment
        from .readings_sup import choice_core
        if self.all_choices is None:
            self._dead = None
            return None
        taken = {(R.id, choice[R.id]) for choice in self.all_choices for R in self.sets}
        env = self._core_environment()
        core = self._formulas(env, [ast for _, ast in choice_core(self.sets, self.couplings, self.narrowings)])
        dead = []
        for s, i in self.candidates():
            if (s, i) in taken or self.dropped(s, i) is not None:
                continue
            from .ast import Not, formula_from_data
            from .readings_sup import choice_atom
            atom = formula_from_data(env, choice_atom(self.sets, s, i), _generated=True)
            proof = prove_entailment(env, core, Not(atom), max_steps=BUDGET["max_steps"])
            if proof.status != "Found":
                continue
            row = self.lean("readings-dead", set=s, index=i, certificate=proof.certificate)
            if row["accepted"] is not True or row["finding"] != f"DeadReading: {s}:{i}":
                raise CheckerUnavailable("ReadingsConformance: Lean does not confirm the dead reading Python's "
                                         "prover certified")
            dead.append({"set": s, "index": i, "finding": row["finding"]})
        self._dead = dead
        return dead

    def _core_environment(self):
        """The choice vocabulary alone, with no generated Background: `deadCheck` replays a certificate over the
        premises `choiceCore D` and nothing else."""
        from .background import background
        from .environment import Environment
        from .readings_sup import choice_vocabulary
        data = self.base.to_dict()
        vocabulary = choice_vocabulary(self.sets)
        data["profiles"] = ["relational-fol@0"]
        data["vocabulary"] = {"sorts": {sort: {"description": sort} for sort in vocabulary["sorts"]},
                              "constants": {name: {"sort": sort, "description": name}
                                            for name, sort in vocabulary["constants"].items()},
                              "predicates": {name: {"arguments": sorts, "description": name}
                                             for name, sorts in vocabulary["predicates"].items()}}
        env = Environment(data)
        if background(env):
            raise CheckerUnavailable("ReadingsConformance: the choice vocabulary has a generated Background")
        return env

    def entailment(self, conclusion_ast, premises=(), assumed=None):
        """ALL, SOME or NONE for `conclusion_ast` over the shared vocabulary (4.5); with `assumed`, whether it
        follows under the named readings. An entailment is certified only under readings whose conflict status is
        CONFLICT-FREE: otherwise `UNKNOWN (conflict status: <status>)` (14.8)."""
        from .readings_sup import CHECK_BUDGET_TEXT
        if not self.checked:
            return {"verdict": "UNKNOWN", "route": "superposed", "reason": CHECK_BUDGET_TEXT}
        if assumed is not None:
            A = [tuple(x) for x in assumed]
            if not self.taken(A):
                # Review A1's class: every verdict under readings no compatible choice takes would be vacuous.
                raise VEError(self.untaken_text(A))
            conflict = self.conflict(A)
            if conflict["status"] != "CONFLICT-FREE":
                return {"verdict": "UNKNOWN", "route": "superposed", "assumed": [list(x) for x in A],
                        "status": f"UNKNOWN (conflict status: {conflict['status']})",
                        "conflict_status": conflict["status"]}
            proof = self.certificate(A, premises, conclusion_ast)
            if proof is not None:
                return {"verdict": "ALL", "route": "superposed", "evidence": "certificate",
                        "assumed": [list(x) for x in A], "conditional_on": proof["conditional_on"],
                        "reading_premises_used": proof["reading_premises_used"], "mentions": proof["mentions"]}
            found = self.model(A, premises, conclusion_ast)
            if found is not None:
                return {"verdict": "NOT ALL", "route": "superposed", "assumed": [list(x) for x in A],
                        "countermodel": found}
            return {"verdict": "UNKNOWN", "route": "superposed", "assumed": [list(x) for x in A],
                    "budget": dict(BUDGET)}
        conflict = self.conflict(())
        if conflict["status"] != "CONFLICT-FREE":
            return {"verdict": "UNKNOWN", "route": "superposed",
                    "status": f"UNKNOWN (conflict status: {conflict['status']})",
                    "conflict_status": conflict["status"]}
        proof = self.certificate((), premises, conclusion_ast)
        if proof is not None:
            return {"verdict": "ALL", "route": "superposed", "evidence": "certificate", "assumed": [],
                    "conditional_on": proof["conditional_on"],
                    "reading_premises_used": proof["reading_premises_used"], "mentions": proof["mentions"]}
        if self.choices is None:
            found = self.model((), premises, conclusion_ast)
            if found is not None:
                return {"verdict": "UNKNOWN", "route": "superposed", "budget": {"max_choices": 64},
                        "status": f"UNKNOWN (not ALL: countermodel under {self.choice_text(found['choice'])})",
                        "countermodel": found}
            return {"verdict": "UNKNOWN", "route": "superposed", "budget": {"max_choices": 64}}
        proofs, counters, unknown = [], [], []
        for choice in self.choices:
            A = [(R.id, choice[R.id]) for R in self.sets]
            found = self.model(A, premises, conclusion_ast)
            if found is not None:
                counters.append(found)
                continue
            proof = self.certificate(A, premises, conclusion_ast)
            if proof is not None:
                proofs.append({"choice": self.choice_json(choice), "conditional_on": proof["conditional_on"]})
            else:
                unknown.append({"choice": self.choice_json(choice)})
        if proofs and counters:
            return {"verdict": "SOME", "route": "superposed", "proof": proofs[0], "countermodel": counters[0]}
        if unknown:
            return {"verdict": "UNKNOWN", "route": "superposed", "choice": unknown[0]["choice"],
                    "budget": dict(BUDGET)}
        if proofs:
            return {"verdict": "ALL", "route": "superposed", "evidence": "certificates", "proofs": proofs}
        return {"verdict": "NONE", "route": "superposed", "countermodels": counters}

    def report_fields(self):
        conflict = self.conflict(())
        dead = self.dead_readings()
        return {"status": conflict["status_text"] if "status_text" in conflict else
                f"UNKNOWN: {conflict.get('reason', '')}",
                "conflict": {key: value for key, value in conflict.items()
                             if key not in ("certificates", "model", "selected")},
                "dead_readings": None if dead is None else [d["finding"] for d in dead]}


def _predicates(ast):
    out, stack = set(), [ast]
    while stack:
        node = stack.pop()
        if type(node) is list and node:
            if node[0] in ("unary", "binary") and type(node[1]) is str:
                out.add(node[1])
            stack.extend(item for item in node[1:] if type(item) is list)
    return out


# ---------------------------------------------------------------------------------------------------------------
# The enumerated route (4.6)

class Enumerated(_Route):
    def __init__(self, doc):
        super().__init__(doc)
        self._docs = {}

    def _choice(self, choice):
        key = tuple(choice[R.id] for R in self.sets)
        if key not in self._docs:
            self._docs[key] = _ChoiceDocument(self, choice)
        return self._docs[key]

    def over_budget(self):
        return {"status": "UNKNOWN", "route": "enumerated", "budget": {"max_choices": 64},
                "units": [R.unit for R in self.sets]}

    def conflict(self, A=()):
        if self.choices is None:
            return {**self.over_budget(), "status_text": "UNKNOWN: more than 64 compatible readings"}
        rows = [(self.choice_json(c), self._choice(c).conflict()) for c in self.choices]
        conflicts = [(c, r) for c, r in rows if r["verdict"] == "CONFLICT"]
        if all(r["verdict"] == "CONFLICT-FREE" for _, r in rows):
            conditional = list(dict.fromkeys(label for _, r in rows for label in r.get("conditional_on", [])))
            return {"status": "CONFLICT-FREE", "route": "enumerated", "conditional_on": conditional,
                    "status_text": f"CONFLICT-FREE among rules on the same act under every reading ({len(rows)} "
                                   "readings checked one at a time)",
                    "choices": [{"choice": c, "status": "CONFLICT-FREE"} for c, _ in rows]}
        status = "CONFLICT" if conflicts else "UNKNOWN"
        return {"status": status, "route": "enumerated",
                "status_text": (f"CONFLICT under {self.choice_text(conflicts[0][0])}" if conflicts else
                                "UNKNOWN: a reading's conflict status is not certified"),
                "choices": [{"choice": c, "status": r["verdict"]} for c, r in rows],
                "witnesses": [{"choice": c, "model": r["model"], "status_text": r["status_text"]}
                              for c, r in conflicts]}

    def premises(self):
        if self.choices is None:
            return self.over_budget()
        rows = [(self.choice_json(c), self._choice(c).premises()) for c in self.choices]
        statuses = [r["status"] for _, r in rows]
        overall = ("model" if "model" in statuses else
                   "INCONSISTENT" if all(s == "INCONSISTENT" for s in statuses) else "UNKNOWN")
        result = {"status": overall, "route": "enumerated", "evidence": "per choice",
                  "choices": [{"choice": c, "status": r["status"]} for c, r in rows]}
        if overall == "model":
            result["choice"] = next(c for c, r in rows if r["status"] == "model")
            model = self._choice(dict(result["choice"])).premise_model()
            if model is not None:
                result["model"] = model
        candidates = []
        for s, i in self.candidates():
            taking = [r["status"] for c, r in rows if [s, i] in c]
            narrowing = self.dropped(s, i)
            status = ("narrowed" if narrowing is not None else "dead" if not taking else
                      "model" if "model" in taking else
                      "INCONSISTENT" if all(t == "INCONSISTENT" for t in taking) else "UNKNOWN")
            candidates.append({"set": s, "index": i, "status": status,
                               **({"narrowing": narrowing} if narrowing is not None else {})})
        result["candidates"] = candidates
        return result

    def dead_readings(self):
        """On the enumerated route a candidate no compatible choice takes is found by the enumeration itself; the
        finding is still certified by `readings-dead` (1.9), on the soft and norms chains and the rights chain
        alike, since `choiceCore D` is over the bits alone."""
        if "_dead" in self.__dict__:
            return self._dead
        if self.choices is None:
            self._dead = None
            return None
        from .ast import Not, formula_from_data
        from .entailment import prove_entailment
        from .readings_sup import choice_atom, choice_core
        taken = {(R.id, choice[R.id]) for choice in self.choices for R in self.sets}
        dead = []
        env = Superposed._core_environment(self)
        core = [formula_from_data(env, ast, _generated=True)
                for _, ast in choice_core(self.sets, self.couplings, self.narrowings)]
        for s, i in self.candidates():
            if (s, i) in taken or self.dropped(s, i) is not None:
                continue
            atom = formula_from_data(env, choice_atom(self.sets, s, i), _generated=True)
            proof = prove_entailment(env, core, Not(atom), max_steps=BUDGET["max_steps"])
            if proof.status != "Found":
                continue
            row = self.lean("readings-dead", set=s, index=i, certificate=proof.certificate)
            if row["accepted"] is not True or row["finding"] != f"DeadReading: {s}:{i}":
                raise CheckerUnavailable("ReadingsConformance: Lean does not confirm the dead reading Python's "
                                         "prover certified")
            dead.append({"set": s, "index": i, "finding": row["finding"]})
        self._dead = dead
        return dead

    @property
    def base(self):
        """`_core_environment` reads the frame's identity fields from a base environment."""
        return self.source.senv.author_environment()

    def entailment(self, conclusion_ast, premises=(), assumed=None):
        """ALL, SOME, NONE or UNKNOWN combined over the compatible choices (4.6); with `assumed`, over the choices
        that take the named candidates."""
        if self.choices is None:
            return {"verdict": "UNKNOWN", **self.over_budget()}
        chosen = [c for c in self.choices if all(c.get(s) == i for s, i in (assumed or ()))]
        if not chosen:
            raise VEError("InvalidInput: no compatible choice takes the named readings")
        rows = [(self.choice_json(c), self._choice(c).entailment(conclusion_ast, premises)) for c in chosen]
        proofs = [{"choice": c, **r} for c, r in rows if r["outcome"] == "proof"]
        counters = [{"choice": c, **r} for c, r in rows if r["outcome"] == "countermodel"]
        unknown = [c for c, r in rows if r["outcome"] == "unknown"]
        if len(proofs) == len(rows):
            return {"verdict": "ALL", "route": "enumerated", "evidence": "certificates", "proofs": proofs}
        if len(counters) == len(rows):
            return {"verdict": "NONE", "route": "enumerated", "countermodels": counters}
        if proofs and counters:
            return {"verdict": "SOME", "route": "enumerated", "proof": proofs[0], "countermodel": counters[0]}
        return {"verdict": "UNKNOWN", "route": "enumerated", "choice": unknown[0]}

    def report_fields(self):
        conflict = self.conflict(())
        dead = self.dead_readings()
        return {"status": conflict["status_text"],
                "conflict": {key: value for key, value in conflict.items() if key not in ("status_text", "witnesses")},
                "dead_readings": None if dead is None else [d["finding"] for d in dead]}


class _ChoiceDocument:
    """`choiceDoc D c` as an ordinary document of the lower route (4.6): its own rules and assertions under their
    own names, checked by the lower route's logic; its conflict status through `readings-choice`."""

    def __init__(self, route, choice):
        from .readings_s1 import Content
        from .readings_sup import choice_contents
        self.route, self.choice = route, choice
        senv = route.source.senv
        self.chain = senv.chain
        contents = choice_contents(route.source, choice)
        self.assertions = [c.body for c in contents if isinstance(c, Content) and c.kind == "assertion"]
        lower = senv.lower_data
        # The chain's own check of the choice's document (the route refused any choice it rejects at load, 4.1
        # step 5), and its hash as the lower route binds a package to it.
        from .readings_s1 import Side
        self.side = Side(senv, contents, route.source.unit_ids)
        if self.chain != "norms":
            self.side._elaborate()
        if self.chain == "soft":
            from .softnorms import SoftEnvironment
            self.lower_env = SoftEnvironment(lower)
            self.soft = self.side.soft
            self.env = self.soft.extended_env
            self.premises_ = ([f for _, f in self.soft.elaborated.premises()] +
                              [f for _, f in self.soft.extended_env.soft_premises])
        elif self.chain == "norms":
            from .environment import Environment
            from .norms import NormDocument
            self.lower_env = Environment(lower)
            self.norms = NormDocument(self.lower_env, [c.raw for c in contents if c.kind == "norm"])
            self.env = self.lower_env
            self.premises_ = [f for _, f in self.norms.premises()]
        else:
            from .document import _environment
            self.lower_env = _environment(lower)
            self.rights = self.side.rights
            self.soft = self.rights.soft_document
            self.env = self.soft.extended_env
            self.premises_ = ([f for _, f in self.soft.elaborated.premises()] +
                              [f for _, f in self.soft.extended_env.soft_premises] +
                              [f for _, f in self.rights.limitation_premises])

    def _all(self, gamma=()):
        from .ast import formula_from_data
        return self.premises_ + [formula_from_data(self.env, ast, _generated=True)
                                 for ast in self.assertions + list(gamma)]

    def premises(self):
        from .vacuity import premise_status
        return premise_status(self.env, self._all(), max_proof_steps=BUDGET["max_steps"],
                              max_domain_size=BUDGET["max_domain_size"], max_models=BUDGET["max_models"],
                              max_evaluations=BUDGET["max_evaluations"])

    def premise_model(self):
        """The model behind a `model` premise status, found again and checked, for the wording (R5)."""
        from .ast import Bottom
        from .search import check_countermodel, find_countermodel
        premises = self._all()
        found = find_countermodel(self.env, premises, Bottom(), max_domain_size=BUDGET["max_domain_size"],
                                  max_models=BUDGET["max_models"], max_evaluations=BUDGET["max_evaluations"])
        if found.status == "Found" and check_countermodel(self.env, premises, Bottom(), found.model,
                                                          max_evaluations=BUDGET["max_evaluations"]).valid:
            return found.model.to_dict()
        return None

    def conflict(self):
        """The lower route's conflict check on the choice's document, with Python's packages, run by Lean's
        `readings-choice` on the document Lean builds for the choice."""
        from .ast import Not, _to_data, formula_from_data
        from .entailment import prove_entailment
        from .norms import _bind, _prove_targets
        if self.chain == "norms":
            packages = _prove_targets(self.norms, self.norms.base_environment(), BUDGET["max_steps"])
            inner = {"kind": "norms-conflict", "packages": packages if isinstance(packages, dict) else {}}
        else:
            base, premises = self._conflict_base()
            packages = {}
            document_hash = self.side.document_hash()
            for target, sorts, formula in self.soft.elaborated.conflict_targets():
                closed = formula_from_data(base, _to_data(_bind(Not(formula), sorts)), _generated=True)
                proof = prove_entailment(base, premises, closed, max_steps=BUDGET["max_steps"])
                if proof.status == "Found":
                    packages[target] = {"environment_id": self.lower_env.environment_id,
                                        "document_hash": document_hash, "target": target,
                                        "certificate": proof.certificate}
            inner = ({"kind": "soft-conflict", "packages": packages, "pairs": {}} if self.chain == "soft" else
                     {"kind": "rights-conflict", "packages": packages})
        answer = self._inner(inner)
        if answer["verdict"] == "CONFLICT-FREE":
            return {"verdict": "CONFLICT-FREE", "conditional_on": answer.get("conditional_on", []),
                    "status_text": answer.get("status_text")}
        witness = self._witness()
        if witness is not None:
            answer = self._inner({**{k: v for k, v in inner.items() if k not in ("packages", "pairs")},
                                  "witness": witness})
            if answer["verdict"] != "CONFLICT":
                raise CheckerUnavailable("ReadingsConformance: the lower route does not confirm the conflict "
                                         "witness Python's search found on a reading's document")
            return {"verdict": "CONFLICT", "target": witness["target"], "tuple": witness["tuple"],
                    "model": witness["model"], "status_text": answer.get("status_text")}
        return {"verdict": "UNKNOWN", "status_text": answer.get("status_text")}

    def _conflict_base(self):
        """`E′_base` and `Background_base′` (with Lim_D on the rights chain) as the lower route binds a conflict
        package: the elaborated environment without its statement layers and regulated predicates, the soft
        premises and the limitation premises as explicit premises after its own Background."""
        from .ast import _to_data, formula_from_data
        from .environment import Environment
        data = self.soft.extended_env.to_dict()
        data["profiles"] = [p for p in data["profiles"] if p not in ("norms@0", "soft-norms@0", "rights@0", "readings@1")]
        data["vocabulary"].pop("soft", None)
        data["vocabulary"].pop("rights", None)
        data["vocabulary"]["predicates"] = {n: {k: v for k, v in e.items() if k != "instruction_of"}
                                            for n, e in data["vocabulary"]["predicates"].items()
                                            if "regulated" not in e}
        base = Environment(data)
        formulas = [f for _, f in self.soft.extended_env.soft_premises]
        if self.chain == "rights":
            formulas += [f for _, f in self.rights.limitation_premises]
        return base, [formula_from_data(base, _to_data(f), _generated=True) for f in formulas]

    def _inner(self, inner):
        row = self.route.lean("readings-choice", choice=self.route.choice_json(self.choice), inner=inner)
        answer = row["inner"]
        if answer.get("status") != "ok":
            raise CheckerUnavailable(f"ReadingsConformance: the lower route refused a reading's document: "
                                     f"{answer.get('error')}")
        return answer

    def _witness(self):
        """A finite base model where some conflict target holds, with its tuple (Python's search, untrusted)."""
        from .ast import Not, _Checker
        from .evaluate import _Evaluator, _Exhausted
        from .norms import _bind
        from .search import find_countermodel
        document = self.norms if self.chain == "norms" else self.soft.elaborated
        base = document.base_environment()
        for target, sorts, formula in document.conflict_targets():
            found = find_countermodel(base, (), _bind(Not(formula), sorts),
                                      max_domain_size=BUDGET["max_domain_size"], max_models=BUDGET["max_models"],
                                      max_evaluations=BUDGET["max_evaluations"])
            if found.status != "Found":
                continue
            model = found.model
            _Checker(base, generated=True).formula(formula, tuple(reversed(sorts)))
            evaluator = _Evaluator(base, model, BUDGET["max_evaluations"], trace=False)
            try:
                values = next((values for values in product(*(model.domains[s] for s in sorts))
                               if evaluator.formula(formula, tuple(zip(reversed(sorts), reversed(values))))[0]),
                              None)
            except _Exhausted:
                values = None
            if values is not None:
                return {"target": target, "model": model.to_dict(), "tuple": list(values)}
        return None

    def entailment(self, conclusion_ast, gamma=()):
        """A replayed certificate or a checked countermodel of the choice's document, as an ordinary document's
        query gets them (`ve document readings`), or unknown within the budget."""
        from .ast import formula_from_data
        from .entailment import check_entailment_certificate, prove_entailment
        from .search import check_countermodel, find_countermodel
        premises = self._all(gamma)
        phi = formula_from_data(self.env, conclusion_ast, _generated=True)
        proof = prove_entailment(self.env, premises, phi, max_steps=BUDGET["max_steps"])
        if proof.status == "Found" and check_entailment_certificate(self.env, premises, phi, proof.certificate,
                                                                    max_steps=BUDGET["max_steps"]).valid:
            return {"outcome": "proof"}
        found = find_countermodel(self.env, premises, phi, max_domain_size=BUDGET["max_domain_size"],
                                  max_models=BUDGET["max_models"], max_evaluations=BUDGET["max_evaluations"])
        if found.status == "Found" and check_countermodel(self.env, premises, phi, found.model,
                                                          max_evaluations=BUDGET["max_evaluations"]).valid:
            return {"outcome": "countermodel", "model_id": found.model.model_id, "model": found.model.to_dict()}
        return {"outcome": "unknown"}


__all__ = ["BUDGET", "Enumerated", "PENDING", "Pending", "Superposed", "context"]
