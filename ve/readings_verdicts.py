"""S2a's verdicts across readings (docs/spec/composition-s2.md 4.5, 4.6, 5, 6, 8.6).

Python's prover and model search are untrusted generators. On the superposed route every certificate and model they
find on `sup D` is checked by Lean's readings route (`readings-conflict`, `readings-certificate`, `readings-model`,
`readings-dead`) before a verdict is reported; on the enumerated route each compatible choice's own document is checked
as an ordinary document of the lower route through `readings-choice`, on the document Lean regenerates for the
choice: its conflict status, every certificate (the chain's certificate kind) and every model (`choice-model`). A Lean
refusal of evidence that Python's own check accepted is `CheckerUnavailable`, never a verdict; an exhausted search
budget is UNKNOWN, which asserts nothing, and an absence that cannot be certified is reported as not computed.
Nothing here is computed for W2's, the pending or the abstaining route (1.1).
"""
from __future__ import annotations

import json
from contextlib import contextmanager
from itertools import product

from .errors import CheckerUnavailable, ResourceLimit, VEError

BUDGET = {"max_steps": 10_000, "max_domain_size": 2, "max_models": 10_000, "max_evaluations": 100_000}
PENDING = {"status": "UNKNOWN", "reason": "non-assertion reading elaboration pending"}
_NOT_SUPERPOSABLE = "ReadingsNotSuperposable: "


def context(doc):
    """The verdict context of a loaded document with a content-bearing set, by its route; None on W2's route. A
    document whose readings carry their own vocabulary is the product of its cases (readings-defaults RD-4b)."""
    if doc.get("readings_components") is not None:
        from .readings_components import context as components_context
        return components_context(doc)
    if "_readings_s2_context" not in doc:
        row = doc.get("readings_s2")
        route = row["route"] if row is not None else None
        doc["_readings_s2_context"] = (Superposed(doc) if route == "superposed" else
                                       Enumerated(doc) if route == "enumerated" else
                                       Pending(doc) if route in ("pending", "abstention") else None)
    return doc["_readings_s2_context"]


def dead_finding(set_id, index):
    """The finding of a dead reading (1.9), Lean's `deadReadingsJson` text; both routes report it."""
    return f"DeadReading: {set_id}:{index}"


def _dropped(sets, narrowings, set_id, index):
    """The first narrowing in force (document order) that drops candidate `index` of `set_id`, if any (Lean's
    `droppedBy`; E7, not `DeadReading`)."""
    R = next(R for R in sets if R.id == set_id)
    for narrowing in narrowings:
        if (narrowing["set"], narrowing["version"]) == (R.id, R.version) and \
                R.candidates[index].id not in narrowing["keeps"]:
            return narrowing["id"]
    return None


class _Route:
    """What every route past the first three rows of 1.1 shares: the decoded document, its open sets and the
    compatible choices (at most 64, else None)."""

    def __init__(self, doc):
        from .readings_route import document_wire
        from .readings_s1 import Document, S1Environment, wire
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
        # Under the unspecified completion (readings-defaults 3) the route's row carries Lean's filled document, and
        # each choice is checked on Lean's `choiceU N c` (`_FilledChoiceDocument`).
        filled = self.row.get("filled")
        self.completion = filled is not None
        self.source = Document(S1Environment(self.environment, filled), self.document, filled)
        self.sets = self.source.sets
        self.choices = None if self.row["choices"] == "over" else [
            {s: i for s, i in choice} for choice in self.row["choices"]]
        self.numbers = {unit["id"]: n for n, unit in enumerate(doc["units"], 1)}

    def lean(self, kind, **fields):
        from .readings_route import run_lean
        [row] = run_lean([{"id": kind, "kind": kind, "environment": self.environment, "document": self.document,
                           **fields}])
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
        return _dropped(self.sets, self.narrowings, set_id, index)

    def candidates(self):
        return [(R.id, i) for R in self.sets for i in range(len(R.candidates))]

    def restrictions(self, A=()):
        return (self._ask("conflict", A) if self.route == "superposed" else
                self._verdicts("conflict", assumed=[list(x) for x in A]))["restrictions"]

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

def _public_sup_conflict(result):
    """Keep the service envelope out of the established public conflict display.

    Lean supplies every value.  The limit result has a reason in place of the
    successful conflict's status text; that text still feeds the report status.
    """
    return {key: value for key, value in result.items()
            if key != "route" and (key != "status_text" or "reason" not in result)}


class Superposed(_Route):
    def __init__(self, doc):
        super().__init__(doc)
        from .readings_sup import superposed_document
        _, contents, soft = superposed_document(self.source)
        self.soft = soft
        self.ext = soft.extended_env
        self.base = soft.elaborated.base_environment()
        self.slot = [(entry["label"], entry["ast"]) for entry in self.row.get("slot", [])]
        # Under the completion `Fill_T` of the superposed filled document follows the assumed atoms (Lean's
        # `slotUnder D A ++ Fill_T`, `supCertificateCheckExtra`, plan RD-6b); Lean's row carries it apart (`fill`).
        self.fill = [(entry["label"], entry["ast"]) for entry in self.row.get("fill", [])]
        self.labelled = self.slot + self.fill
        self.layers = [formula for _, formula in soft.elaborated.premises()]
        self.assertions = [content.body for content in contents if content.kind == "assertion"]
        # DRI ruling 5: past the checked choices no superposed verdict is claimed.
        self.checked = type(self.row.get("choices_checked")) is int
        self._evidence = {}
        self._answers = {}
        self.requests = {}
        self._taken = {}
        self._proposals = {}
        self._conflicts = {}
        self._models = {}
        self._choice_docs = {}
        self._small_search = {}

    def taken(self, A):
        if not A:
            return self.checked
        key = tuple(tuple(x) for x in A)
        if key in self._taken:
            return self._taken[key]
        try:
            self._ask("conflict", A)
        except VEError as exc:
            if str(exc).startswith("ReadingsUnsatisfiable:"):
                self._taken[key] = False
                return False
            raise
        self._taken[key] = True
        return True

    # -- premise lists in Lean's order (8.4 `supCertificateCheck`, `supModelCheck`, `slotConflictFreeCheck`)

    def _formulas(self, env, asts):
        from .ast import formula_from_data
        return [formula_from_data(env, ast, _generated=True) for ast in asts]

    def _atoms(self, A):
        from .readings_sup import choice_atom
        return [choice_atom(self.sets, s, i) for s, i in A]

    def _labelled(self, env, A):
        """slot ++ atoms ++ `Fill_T` over `env` in Lean's order, each slot and `Fill_T` premise with its label (an
        atom has none). Outside the completion `Fill_T` is empty."""
        slot = list(zip((label for label, _ in self.slot), self._formulas(env, [ast for _, ast in self.slot])))
        atoms = [(None, f) for f in self._formulas(env, self._atoms(A))]
        fill = list(zip((label for label, _ in self.fill), self._formulas(env, [ast for _, ast in self.fill])))
        return slot + atoms + fill

    def _full(self, A, gamma=()):
        """slot ++ atoms ++ `Fill_T` ++ layers ++ assertions ++ Γ over E′ (the prover prepends background′)."""
        return ([f for _, f in self._labelled(self.ext, A)] + self.layers +
                self._formulas(self.ext, self.assertions + list(gamma)))

    def _prove(self, env, labelled, rest, conclusion):
        """A certificate of `conclusion` from the labelled premises ++ rest (the prover prepends the Background) that
        needs as few labelled premises as the prover finds: each is replaced by ⊤ in turn and stays replaced when a
        proof remains. The certificate returned never expands a replaced premise, so it checks against the full
        list as well; its conditions are computed by Lean's joint replay."""
        from .ast import Top
        from .entailment import prove_entailment
        current = [f for _, f in labelled]
        proof = prove_entailment(env, current + rest, conclusion, max_steps=BUDGET["max_steps"])
        if proof.status != "Found":
            return None
        for k, (label, _) in enumerate(labelled):
            if label is None:
                continue
            trial = current[:k] + [Top()] + current[k + 1:]
            again = prove_entailment(env, trial + rest, conclusion, max_steps=BUDGET["max_steps"])
            if again.status == "Found":
                current, proof = trial, again
        return proof.certificate

    def _generate_conflict(self, A=()):
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
        labelled = self._labelled(self.base, A)
        premises = [f for _, f in labelled]
        certificates, missing = {}, None
        for target, sorts, formula in self.soft.elaborated.conflict_targets():
            certificate = self._prove(self.base, labelled, [], _bind(Not(formula), sorts))
            if certificate is not None:
                certificates[target] = certificate
            elif missing is None:
                missing = target
        assumed = [list(x) for x in A]
        if missing is None:
            row = self.lean("readings-conflict", assumed=assumed, conflict_certificates=certificates)
            if row["verdict"] != "CONFLICT-FREE":
                raise CheckerUnavailable("ReadingsConformance: Lean does not confirm the conflict certificates "
                                         "Python's prover found on the superposed document")
            result = {"status": "CONFLICT-FREE", "certificates": certificates}
        else:
            result = self._witness(A, premises, missing)
            result["certificates"] = certificates
        self._conflicts[key] = result
        return result

    def _witness(self, A, premises, missing):
        from .ast import Not
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
            self._shadow(data, A, target=(target, sorts, formula))
            gaps = self._lean_gaps(row, data)
            return {"status": "CONFLICT", "assumed": [list(x) for x in A],
                    "target": target, "sorts": list(sorts), "tuple": list(values), "choice": row["choice"],
                    "model": data, "gaps": gaps}
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
        # Under the completion a choice's own document is Lean's `choiceU N c`, whose models carry a separate filling;
        # the search runs on `sup (fillDoc N)` itself, `Fill_T` in its slot (plan RD-6b).
        result = self._lifted(A, gamma, conclusion) if usable and not self.completion else None
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
                self._shadow(data, A, gamma, conclusion)
                result = {"choice": row["choice"], "model": data, "gaps": self._lean_gaps(row, data)}
        self._models[key] = result
        return result

    def _lean_gaps(self, row, model):
        """The filled gaps a checked model's result depends on, Lean's (`ndModelGaps`, `gapsOf`; readings-defaults
        2.2), bound to the request: each names an unspecified predicate of the request and elements of the model, as
        many as the predicate's arguments. None outside the completion. Python never chooses them (review B3 of
        rd-6b: listing every point of every filled table showed gaps the result does not depend on)."""
        if not self.completion:
            return []
        gaps = row.get("gaps")
        elements = {element for values in model["domains"].values() for element in values}
        unspecified = {name: decl for name, decl in self.doc["environment"].predicates.items()
                       if decl.regulated is not None and decl.regulated.default == "unspecified"}
        if type(gaps) is not list or not all(
                type(gap) is list and len(gap) == 3 and gap[0] in unspecified and type(gap[1]) is list and len(gap[1]) == len(unspecified[gap[0]].arguments)
                and all(type(e) is str and e in elements for e in gap[1]) and type(gap[2]) is bool for gap in gaps):
            raise CheckerUnavailable("ReadingsConformance: Lean's filled gaps of a superposed model are not bound to "
                                     "the request")
        return gaps

    def _shadow(self, data, A=(), gamma=(), conclusion=None, target=None):
        """Rust evaluates the Python-generated formulas of `sup D` on a model shown, untrusted (4.2, 10): the slot
        with the assumed atoms, the assertions and Γ and the conclusion read on the base through the outcome
        substitution, and a witness's target closed existentially. Its values must be the ones Lean's check
        established; a difference is `CheckerUnavailable`, never a verdict."""
        from .ast import Exists, _to_data, formula_from_data
        from .backends.rust_jsonl import configured_timeout, run
        from .norms import _bind
        environment = self.base.to_dict()
        environment["profiles"] = ["relational-fol@0"]
        for key in ("soft", "rights"):
            environment["vocabulary"].pop(key, None)

        def base(asts):
            return [_to_data(self.soft.elaborated._expand(formula_from_data(self.ext, ast, _generated=True), ""))
                    for ast in asts]

        case = {"id": "readings-s2-shadow", "kind": "readings-superposed-evaluate", "untrusted": True,
                "environment": environment, "model": data,
                "slot": [ast for _, ast in self.slot] + self._atoms(A) + [ast for _, ast in self.fill],
                "assertions": base(self.assertions + list(gamma)),
                "conflict_targets": [], "conclusions": base([conclusion]) if conclusion is not None else []}
        if target is not None:
            name, sorts, formula = target
            case["conflict_targets"] = [_to_data(_bind(formula, sorts, Exists))]
        try:
            record = run(case, timeout=configured_timeout(60.0))
        except VEError as exc:
            raise CheckerUnavailable(f"ReadingsConformance: Rust did not evaluate the model shown: "
                                     f"{getattr(exc, 'message', exc)}") from None
        values = record.get("values") or {}
        expected = {"slot": [True] * len(case["slot"]),
                    "assertions": [True] * len(case["assertions"]) if target is None else values.get("assertions"),
                    "conflict_targets": [True] * len(case["conflict_targets"]),
                    "conclusions": [False] * len(case["conclusions"])}
        if record.get("untrusted") is not True or any(values.get(k) != v for k, v in expected.items()):
            raise CheckerUnavailable("ReadingsConformance: Rust's untrusted evaluation differs from Lean's on a "
                                     "model of the superposed document")

    def _lifted(self, A, gamma, conclusion):
        from .ast import Bottom, formula_from_data
        from .search import check_countermodel, find_countermodel
        key = tuple(tuple(x) for x in A)
        if key not in self._proposals:
            self._ask("premises" if conclusion is None else "query", A,
                      gamma=gamma, conclusion=conclusion)
        for reading in self._proposals[key]:
            reading_key = tuple(tuple(x) for x in reading)
            choice = dict(reading)
            own = self._choice_docs.get(reading_key)
            if own is None:
                own = _ChoiceDocument(self, choice)
                self._choice_docs[reading_key] = own
            search_key = (reading_key, repr(gamma), repr(conclusion))
            if search_key not in self._small_search:
                premises = own._all(gamma) + own.searched
                phi = Bottom() if conclusion is None else formula_from_data(own.env, conclusion, _generated=True)
                found = find_countermodel(own.env, premises, phi, max_domain_size=BUDGET["max_domain_size"],
                                          max_models=BUDGET["max_models"], max_evaluations=BUDGET["max_evaluations"])
                valid = found.status == "Found" and check_countermodel(
                    own.env, premises, phi, found.model,
                    max_evaluations=BUDGET["max_evaluations"]).valid
                self._small_search[search_key] = (found, valid)
            found, valid = self._small_search[search_key]
            if not valid:
                continue
            data = self._lift(choice, found.model.to_dict(), own)
            row = self.lean("readings-model", assumed=[list(x) for x in A], premises=list(gamma),
                            conclusion=conclusion, model=data)
            if row["valid"] is True and row["conclusion_value"] is False:
                self._shadow(data, A, gamma, conclusion)
                return {"choice": row["choice"], "model": data, "gaps": self._lean_gaps(row, data)}
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

    def _generate_certificate(self, A=(), gamma=(), conclusion=None):
        """A certificate of `conclusion` (⊥ when None) under `A`, checked by `readings-certificate`; only when the
        conflict status under `A` is CONFLICT-FREE (4.5, 14.8). None within the budget."""
        from .ast import Bottom, formula_from_data
        from .entailment import prove_entailment
        conflict = self._generate_conflict(A)
        if conflict["status"] != "CONFLICT-FREE":
            return None
        phi = Bottom() if conclusion is None else formula_from_data(self.ext, conclusion, _generated=True)
        full = self._full(A, gamma)
        labelled = self._labelled(self.ext, A)
        rest = full[len(labelled):]
        certificate = self._prove(self.ext, labelled, rest, phi)
        if certificate is None:
            return None
        row = self.lean("readings-certificate", assumed=[list(x) for x in A], premises=list(gamma),
                        conclusion=conclusion, conflict_certificates=conflict["certificates"],
                        certificate=certificate)
        if row["accepted"] is not True:
            raise CheckerUnavailable("ReadingsConformance: Lean does not confirm the certificate Python's prover "
                                     "found on the superposed document")
        return {"certificate": certificate, "assumed": [list(x) for x in A]}

    # -- the questions of 4.5

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

    def _ask(self, question, A=(), *, gamma=(), conclusion=None):
        """Request Lean's whole answer. The evidence map is proposals only; no fold is computed here."""
        from .readings_route import run_lean
        allowed = {"conflict", "witness"} | ({"unsat", "model"} if question == "premises" else
                                           {"certificate", "countermodel"} if question == "query" else set())
        case = {"id": "readings-verdicts", "kind": "readings-verdicts", "environment": self.environment,
                "document": self.document, "question": question,
                "evidence": [{"choice": [list(x) for x in key], **{k: v for k, v in pieces.items() if k in allowed}}
                             for key, pieces in self._evidence.items()],
                "premises": list(gamma), "conclusion": conclusion, "budget": dict(BUDGET)}
        if A is not None:
            case["assumed"] = [list(x) for x in A]
        if question == "premises" and getattr(self, "_dead", None) is not None:
            case["dead"] = self._dead
        [row] = run_lean([case])
        if row.get("status") != "ok":
            error = row.get("error", "")
            if error.startswith("ReadingsUnsatisfiable:"):
                raise VEError(error)
            raise CheckerUnavailable(f"ReadingsConformance: Lean refused readings-verdicts: {error}")
        _check_sup_answer(row, case, self)
        # Every listed scope is Lean's accepted choice, already typed and bound
        # above. Reuse that answer while preparing evidence for the same scopes.
        for scope in row["scopes"]:
            key = tuple(tuple(x) for x in scope["row"]["choice"])
            self._taken[key] = True
            # Lean returned the bounded compatible choices for this scope.
            # Reuse them when generating its untrusted model evidence.
            self._proposals[key] = scope["model_proposals"]
        self.requests[id(row)] = case
        return row

    def _pieces(self, A):
        return self._evidence.setdefault(tuple(tuple(x) for x in A), {})

    def _prepare_conflict(self, A):
        result = self._generate_conflict(A)
        pieces = self._pieces(A)
        if "certificates" in result:
            pieces["conflict"] = {"conflict_certificates": result["certificates"]}
        if "model" in result:
            pieces["witness"] = {"witness": {"model": result["model"], "target": result["target"],
                                              "tuple": result["tuple"]}}
        return result

    def _prepare(self, question, A=(), gamma=(), conclusion=None):
        row = self._ask(question, A, gamma=gamma, conclusion=conclusion)
        for scope in row["scopes"]:
            own = scope["row"]["choice"]
            self._prepare_conflict(own)
        return self._ask(question, A, gamma=gamma, conclusion=conclusion)

    def conflict_answer(self):
        if "conflict" not in self._answers:
            self._answers["conflict"] = self._prepare("conflict", None)
        return self._answers["conflict"]

    def conflict(self, A=()):
        row = self._prepare("conflict", A) if A else self.conflict_answer()
        # Retained solely for callers proposing certificates; the report excludes the traces.
        result = _public_sup_conflict(row["result"])
        generated = self._generate_conflict(A)
        if generated.get("status") == "CONFLICT-FREE" and "certificates" in generated:
            result["certificates"] = generated["certificates"]
        return result

    def certificate(self, A=(), gamma=(), conclusion=None):
        for pieces in self._evidence.values():
            pieces.pop("certificate", None)
            pieces.pop("countermodel", None)
        piece = self._generate_certificate(A, gamma, conclusion)
        if piece is None:
            return None
        self._prepare_conflict(A)
        self._pieces(A)["certificate" if conclusion is not None else "unsat"] = piece
        row = self._ask("query" if conclusion is not None else "premises", A, gamma=gamma, conclusion=conclusion)
        scope = next(s for s in row["scopes"] if s["row"]["choice"] == [list(x) for x in A])
        name = "certificate" if conclusion is not None else "unsat"
        labels = scope["used"].get(name, [])
        return {**piece, "reading_premises_used": labels, "conditional_on": labels,
                "mentions": scope["mentions"].get(name, [])}

    def premises_answer(self):
        if "premises" not in self._answers:
            row = self._ask("premises", None)
            for scope in row["scopes"]:
                A = scope["row"]["choice"]
                # A model settles this evidence slot without conflict certificates or a tableau
                # proof search. Lean checks the model and decides the premise status from the row.
                found = self.model(A)
                if found is not None:
                    self._pieces(A)["model"] = {"model": found["model"]}
                else:
                    self._prepare_conflict(A)
                    proof = self._generate_certificate(A)
                    if proof is not None:
                        self._pieces(A)["unsat"] = proof
            row = self._ask("premises", None)
            if row["untaken"]:
                self._dead = _dead_certificates(self, row["untaken"])
                if self._dead is not None:
                    row = self._ask("premises", None)
            self._answers["premises"] = row
        return self._answers["premises"]

    def premises(self):
        return self.premises_answer()["result"]

    def candidate_premises(self):
        return self.premises()["candidates"]

    def dead_readings(self):
        return self.premises_answer()["dead_readings"]

    def entailment(self, conclusion_ast, premises=(), assumed=None):
        # Query evidence is tied to this query, never reused under a different formula.
        for pieces in self._evidence.values():
            pieces.pop("certificate", None)
            pieces.pop("countermodel", None)
        row = self._prepare("query", assumed, premises, conclusion_ast)
        for scope in row["scopes"]:
            A = scope["row"]["choice"]
            proof = self._generate_certificate(A, premises, conclusion_ast)
            if proof is not None:
                self._pieces(A)["certificate"] = proof
            else:
                found = self.model(A, premises, conclusion_ast)
                if found is not None:
                    self._pieces(A)["countermodel"] = {"model": found["model"]}
        row = self._ask("query", assumed, gamma=premises, conclusion=conclusion_ast)
        self._answers[("query", _request_key(conclusion_ast, premises, assumed))] = row
        return row["result"]

    def query_answer(self, conclusion_ast, assumed=None, premises=()):
        key = ("query", _request_key(conclusion_ast, premises, assumed))
        if key not in self._answers:
            self.entailment(conclusion_ast, premises, assumed)
        return self._answers[key]

    def answer_for(self, result, conclusion):
        """The exact answer returned for this query, including its premises and whether --under was supplied."""
        for answer in self._answers.values():
            if answer.get("question") == "query" and answer["result"] is result:
                if self.requests[id(answer)]["conclusion"] != conclusion:
                    raise CheckerUnavailable("ReadingsConformance: the displayed conclusion differs from the bound query")
                return answer
        raise CheckerUnavailable("ReadingsConformance: this query result has no bound Lean answer")

    def report_fields(self):
        conflict = self.conflict_answer()["result"]
        dead = self.dead_readings()
        return {"status": conflict["status_text"],
                "conflict": {key: value for key, value in _public_sup_conflict(conflict).items()
                             if key not in ("certificates", "model", "gaps", "selected")},
                "dead_readings": None if dead is None else [d["finding"] for d in dead]}


# ---------------------------------------------------------------------------------------------------------------
# The enumerated route (4.6; readings-defaults 3.5, RD-3)

class Enumerated(_Route):
    """The enumerated route: every verdict is Lean's (`readings-verdicts`, one request per question). Lean
    enumerates the compatible choices taking `assumed`, checks every piece of evidence on the choice's document it
    regenerates, folds the rows, computes the restrictions and the labels an answer uses, and plans its English.
    Python only generates evidence (each choice's document below: conflict packages, witnesses, certificates and
    models, its own untrusted prover and search) and relays Lean's answer; a piece Lean refuses that Python's own
    check accepted is `CheckerUnavailable`, never a verdict."""

    def __init__(self, doc):
        super().__init__(doc)
        self._docs = {}
        self._conflict = {}  # choice key → its conflict packages and witness (inner cases)
        self._premise = {}   # choice key → its certificate of ⊥ or model
        self._dead = None    # the dead readings' certificates, once Lean names the untaken candidates
        self._answers = {}
        self._notes = None   # choice → Lean's notes on its conflict package and witness, once the conflict is asked
        self.requests = {}   # id of an answer → the request it answers

    def _choice(self, choice):
        key = self._key(choice)
        if key not in self._docs:
            self._docs[key] = (_FilledChoiceDocument if self.completion else _ChoiceDocument)(self, choice)
        return self._docs[key]

    def _key(self, choice):
        return tuple(choice[R.id] for R in self.sets)

    @staticmethod
    def _of(choice_json):
        return {s: i for s, i in choice_json}

    def _verdicts(self, question, query=None, **fields):
        """Lean's `readings-verdicts` answer, the evidence generated so far sent with it, checked against the request
        (`_check_answer`); the request is kept beside it (`requests`, by the answer's identity)."""
        from .readings_route import run_lean
        evidence = []
        for choice in self.choices or []:
            key = self._key(choice)
            pieces = {**self._conflict.get(key, {}), **self._premise.get(key, {}), **(query or {}).get(key, {})}
            if pieces:
                evidence.append({"choice": self.choice_json(choice), **pieces})
        case = {"id": "readings-verdicts", "kind": "readings-verdicts", "environment": self.environment,
                "document": self.document, "question": question, "evidence": evidence, **fields}
        if self._dead is not None:
            case["dead"] = self._dead
        [row] = run_lean([case])
        if row.get("status") != "ok":
            error = row.get("error")
            if isinstance(error, str) and error.startswith("ReadingsUnsatisfiable: "):
                raise VEError(error)
            raise CheckerUnavailable(f"ReadingsConformance: Lean refused the readings-verdicts case Python built: "
                                     f"{error}")
        self.check_answer(row, case)
        if self._notes is not None and any(self._notes[json.dumps(e["choice"])] != _conflict_notes(e)
                                           for e in row["per_choice"]):
            raise CheckerUnavailable("ReadingsConformance: Lean notes a reading's conflict evidence differently from "
                                     "one request to the next")
        self.requests[id(row)] = case
        return row

    def check_answer(self, row, case):
        """`_check_answer` with this route's frame."""
        _check_answer(row, case, self.frame(case))

    def frame(self, case):
        """The frame `case` is answered in: the request's document, Lean's compatible choices (the route's row, bound
        to its request), the completion and the sets its finding names (none on the rights chain)."""
        finding = (self.row.get("finding") or {}).get("text")
        if finding is not None and not finding.startswith(_NOT_SUPERPOSABLE):
            raise CheckerUnavailable("ReadingsConformance: the enumerated route's finding names no sets")
        return _Frame(case, None if self.choices is None else [self.choice_json(c) for c in self.choices],
                      self.completion, [] if finding is None else finding.removeprefix(_NOT_SUPERPOSABLE).split(", "))

    def _conflict_answer(self):
        """The conflict question: each choice's packages, then a witness for every choice Lean leaves without
        CONFLICT-FREE (`readings-choice`'s order of 4.3)."""
        if "conflict" not in self._answers:
            for choice in self.choices or []:
                case = self._choice(choice).conflict_case()
                if case is not None:
                    self._conflict.setdefault(self._key(choice), {})["conflict"] = case
            row = self._verdicts("conflict")
            found = False
            for entry in row["per_choice"]:
                if entry["conflict"] != "CONFLICT-FREE":
                    choice = self._of(entry["choice"])
                    witness = self._choice(choice).witness_case()
                    if witness is not None:
                        self._conflict.setdefault(self._key(choice), {})["witness"] = witness
                        found = True
            final = self._verdicts("conflict") if found else row
            # The witnesses change no package's note (the same packages are sent).
            if [e["evidence"].get("conflict") for e in final["per_choice"]] != \
                    [e["evidence"].get("conflict") for e in row["per_choice"]]:
                raise CheckerUnavailable("ReadingsConformance: Lean notes a reading's conflict packages differently "
                                         "from one request to the next")
            self._notes = {json.dumps(e["choice"]): _conflict_notes(e) for e in final["per_choice"]}
            self._answers["conflict"] = final
        return self._answers["conflict"]

    def conflict(self, A=()):
        if A:
            self._conflict_answer()
            return self._verdicts("conflict", assumed=[list(x) for x in A])["result"]
        return self._conflict_answer()["result"]

    def _free(self):
        return {self._key(self._of(e["choice"])): e["conflict"] == "CONFLICT-FREE"
                for e in self._conflict_answer()["per_choice"]}

    def _premises_answer(self):
        """The premises question: per choice a certificate of ⊥ (only under a CONFLICT-FREE reading, S2a 14.8; the
        quick proof first), else a model, as `premise_status` orders them; then, for the candidates Lean finds no
        compatible choice takes, the dead readings' certificates."""
        if "premises" not in self._answers:
            free = self._free()
            for choice in self.choices or []:
                document, key = self._choice(choice), self._key(choice)
                piece = None
                if free.get(key):
                    piece = document.certificate_case(None, max_steps=min(BUDGET["max_steps"], 128))
                    piece = piece and {"unsat": piece}
                if piece is None:
                    found = document.model_case(None)
                    piece = found and {"model": found}
                if piece is None and free.get(key) and BUDGET["max_steps"] > 128:
                    found = document.certificate_case(None)
                    piece = found and {"unsat": found}
                if piece is not None:
                    self._premise[key] = piece
            row = self._verdicts("premises")
            if row["untaken"] and self._dead is None:
                dead = _dead_certificates(self, [tuple(x) for x in row["untaken"]])
                if dead is not None:
                    self._dead = dead
                    row = self._verdicts("premises")
            self._answers["premises"] = row
        return self._answers["premises"]

    def premises(self):
        return self._premises_answer()["result"]

    def dead_readings(self):
        """Lean's dead readings (1.9): every candidate no compatible choice takes and no narrowing drops, each with
        its certificate; None when one has none or the choices are too many (an incomplete list is never reported)."""
        return self._premises_answer()["dead_readings"]

    def entailment(self, conclusion_ast, premises=(), assumed=None):
        """ALL, SOME, NONE or UNKNOWN across the compatible choices taking `assumed` (4.6), Lean's. A first request
        names the choices and their conflict rows; a certificate or a countermodel is generated for each choice past
        the gate (14.8), and the second request folds them."""
        self._conflict_answer()
        fields = {"premises": list(premises), "conclusion": conclusion_ast}
        if assumed is not None:
            fields["assumed"] = [list(x) for x in assumed]
        row = self._verdicts("query", **fields)
        result = row["result"]
        if "conflict_status" not in result and "budget" not in result:
            query = {}
            for entry in row["per_choice"]:
                choice = self._of(entry["choice"])
                document = self._choice(choice)
                found = document.certificate_case(conclusion_ast, premises)
                if found is not None:
                    query[self._key(choice)] = {"certificate": found}
                    continue
                found = document.model_case(conclusion_ast, premises)
                if found is not None:
                    query[self._key(choice)] = {"countermodel": found}
            if query:
                row = self._verdicts("query", query=query, **fields)
        self._answers[("query", _request_key(conclusion_ast, premises, assumed))] = row
        return row["result"]

    def query_answer(self, conclusion_ast, assumed=None, premises=()):
        """Lean's whole answer to the `entailment` request for this conclusion (its English plan included), asked
        when this route has not asked it yet."""
        key = ("query", _request_key(conclusion_ast, premises, assumed))
        if key not in self._answers:
            self.entailment(conclusion_ast, premises, assumed)
        return self._answers[key]

    def conflict_answer(self):
        return self._conflict_answer()

    def premises_answer(self):
        return self._premises_answer()

    @property
    def base(self):
        """`_core_environment` reads the frame's identity fields from a base environment."""
        return self.source.senv.author_environment()

    def report_fields(self):
        conflict = self.conflict(())
        dead = self.dead_readings()
        return {"status": conflict["status_text"],
                "conflict": {key: value for key, value in conflict.items() if key not in ("status_text", "witnesses")},
                "dead_readings": None if dead is None else [d["finding"] for d in dead]}


def _conflict_notes(entry):
    """A row's notes on its conflict evidence: the same packages and witness get the same notes in every answer."""
    return {name: entry["evidence"].get(name) for name in ("conflict", "witness")}


def _request_key(conclusion_ast, premises, assumed):
    return json.dumps([conclusion_ast, list(premises), None if assumed is None else [list(x) for x in assumed]],
                      sort_keys=True)


# The piece each row word rests on (Lean's `lowerInfo`; under the completion `ndConflictRow`, `ndQueryRow`,
# `ndPremiseRow`), per row field. A word other than UNKNOWN names that piece: the request must have sent it for the
# row's choice and the row must note it accepted (the evidence a row names exists in the request). Which word the
# pieces give, and every verdict, condition and line folded from the rows, is Lean's (`readings_wire_verdicts_*`,
# `verdicts_conditions_*`, DRI ruling of rd-3 round 3); the client never re-derives them.
ROW_PIECES = {"conflict": {"CONFLICT-FREE": "conflict", "CONFLICT": "witness"},
              "query": {"proved": "certificate", "refuted": "countermodel"},
              "premises": {"INCONSISTENT": "unsat", "model": "model"}}
PAIR_LABEL = "unsaid:pair:"


class _Frame:
    """What a `readings-verdicts` answer is bound to: the request's document as Lean decodes it (its open sets at their
    active versions, in unit order; its couplings and narrowings), the request's environment, the compatible choices
    `choices` (Lean's elaborate row, bound to the request; None past 64), whether the unspecified completion applies,
    and the sets the route's finding names (E29)."""

    def __init__(self, case, choices, completion, finding_sets):
        from types import SimpleNamespace
        from .readings_s1 import active_sets, wire
        document = wire(case["document"])
        active = active_sets(document.get("reading_sets") or [])
        self.sets = []
        for unit in document["units"]:
            R = next((r for r in active if r["unit"] == unit["id"]), None)
            if R is not None and R["status"] == "open":
                self.sets.append(SimpleNamespace(id=R["id"], unit=R["unit"], version=R["version"], candidates=[
                    SimpleNamespace(id=a["id"], labels=a.get("labels") or {}) for a in R["readings"]]))
        self.couplings = list(document.get("couplings") or [])
        self.narrowings = list(document.get("narrowings") or [])
        self.predicates = set((((case.get("environment") or {}).get("vocabulary") or {}).get("predicates") or {}))
        self.choices, self.completion, self.finding_sets = choices, completion, list(finding_sets)
        self.candidates = [[R.id, i] for R in self.sets for i in range(len(R.candidates))]

    def label(self, label):
        """A condition label the request names: a coupling or narrowing of its document, or the pair label of two
        predicates of its environment (`unsaid:pair:<required>,<permission>`)."""
        _need(type(label) is str)
        if label.startswith("coupling:"):
            _need(any(K["id"] == label[len("coupling:"):] for K in self.couplings))
        elif label.startswith("narrowing:"):
            _need(any(N["id"] == label[len("narrowing:"):] for N in self.narrowings))
        else:
            required, comma, permission = label.removeprefix(PAIR_LABEL).partition(",")
            _need(label.startswith(PAIR_LABEL) and comma and {required, permission} <= self.predicates)

    def reading(self, reading):
        """A candidate the request's document has: `[set, index]`."""
        _need(type(reading) is list and len(reading) == 2 and reading in self.candidates)


def _shown_of(piece, name):
    """`Readings.Run.shownOf`: the model Lean shows of a piece Python sent, its `shown` member else its checked
    model."""
    if type(piece) is not dict:
        raise ValueError
    if "shown" in piece:
        return piece["shown"]
    holder = piece.get("witness") if name == "witness" else piece
    return holder.get("model") if type(holder) is dict else None


def _need(condition):
    if not condition:
        raise ValueError


INVALID_ANSWER = "the Lean readings route returned an invalid answer"


@contextmanager
def relayed():
    """Checking an answer Lean sent (build checklist 4 and 5): every failure inside is `CheckerUnavailable`, never a
    crash and never a verdict, whatever the answer holds (a type its schema did not fix, a missing or duplicated
    row, a decoder's refusal of a value Lean sent). A resource limit stays a resource limit (checklist 6). The one
    guard of every check of a `readings-verdicts` answer and of the split's answers at load."""
    try:
        yield
    except (CheckerUnavailable, ResourceLimit):
        raise
    except Exception as exc:  # noqa: BLE001 - any failure of the check is an invalid answer
        raise CheckerUnavailable(INVALID_ANSWER) from exc


def _labels(value):
    _need(type(value) is list and all(type(x) is str for x in value))
    return value


def _check_rows(row, case, frame):
    """The rows, bound to the request: the compatible choices exactly the ones taking `assumed`, in order, at least
    one; past 64 only choices the request's evidence names, in its order. Each row notes only pieces the request sent
    for its choice (every conflict package sent is noted); its refusals, shown models and gaps are of noted pieces;
    a shown model is the one the request's piece shows; its word fields are the question's; and a word other than
    UNKNOWN names a piece the row notes accepted (`ROW_PIECES`). Returns the rows by choice."""
    question, assumed = case["question"], case.get("assumed")
    sent = {json.dumps(e["choice"]): e for e in case.get("evidence", [])}
    rows = row["per_choice"]
    seen = [entry["choice"] for entry in rows]
    _need(len({json.dumps(c) for c in seen}) == len(seen))

    def takes(choice):
        return all(x in choice for x in assumed or [])
    if frame.choices is None:
        order = [json.loads(k) for k in sent]
        _need(all(takes(c) for c in seen))
        _need([order.index(c) for c in seen] == sorted(order.index(c) for c in seen))  # ValueError if not sent
    else:
        expected = [c for c in frame.choices if takes(c)]
        _need(expected and seen == expected)
    for entry in rows:
        piece_of = sent.get(json.dumps(entry["choice"]), {})
        pieces = {name for name in piece_of if name != "choice"}
        noted = entry["evidence"]
        _need(set(noted) <= pieces and ("conflict" not in pieces or "conflict" in noted))
        _need(set(entry["errors"]) <= set(noted) and all(noted[name] is False for name in entry["errors"]))
        _need(set(entry["shown"]) <= set(noted) and set(entry["gaps"]) <= set(noted))
        # A witness's status text is the lower route's own, relayed with the witness.
        _need(entry["status_text"] is None or "witness" in noted)
        for name, shown in entry["shown"].items():
            _need(shown == _shown_of(piece_of.get(name), name))
        _need(set(entry) & {"query", "premises"} == {question} - {"conflict"})
        for field in {"conflict", question}:
            word = entry[field]
            _need(word == "UNKNOWN" or (word in ROW_PIECES[field] and noted.get(ROW_PIECES[field][word]) is True))
    return {json.dumps(entry["choice"]): entry for entry in rows}


def _walk(value):
    """Every object inside a JSON value, the value's own first."""
    if type(value) is dict:
        yield value
        for item in value.values():
            yield from _walk(item)
    elif type(value) is list:
        for item in value:
            yield from _walk(item)


# The piece whose shown model a result member shows, by the member that holds it.
SHOWN_IN = {"witnesses": "witness", "countermodels": "countermodel", "countermodel": "countermodel"}


def _check_result(row, case, frame, rows):
    """The result, bound to the request and the rows: it is the over-budget form exactly when the request has more
    than 64 compatible choices, it assumes exactly the readings the request named, every choice it names is a row's,
    a list restating the rows (`choices`, `proofs`, `countermodels`) restates every row once, in order, each status
    the row's word, and `witnesses` the rows in conflict; a SOME names its proof and its countermodel; every model it shows is that row's shown model (the request's piece's), a witness's status text
    is its row's, its candidates are the document's, every narrowing, unit and label it names is the request's, and
    its restrictions are the answer's."""
    result, question = row["result"], case["question"]
    _need(("budget" in result) == (frame.choices is None))
    _need(result.get("assumed") == (case.get("assumed") if question == "query" else None))
    for obj in _walk(result):
        if "choice" in obj:
            _need(json.dumps(obj["choice"]) in rows)
    for member in ("choices", "proofs", "countermodels"):
        if member in result:
            _need([json.dumps(item["choice"]) for item in result[member]] == list(rows))
    for item in result.get("choices", []):
        _need(item["status"] == rows[json.dumps(item["choice"])]["conflict" if question == "conflict" else question])
    if "witnesses" in result:
        _need([json.dumps(w["choice"]) for w in result["witnesses"]] ==
              [key for key, entry in rows.items() if entry["conflict"] == "CONFLICT"])
    if result.get("verdict") == "SOME":
        _need(type(result["proof"]) is dict and type(result["countermodel"]) is dict)
    for member, piece in SHOWN_IN.items():
        items = result.get(member)
        for item in items if type(items) is list else [items] if type(items) is dict else []:
            entry = rows[json.dumps(item["choice"])]
            if "model" in item:
                _need(item["model"] == entry["shown"].get(piece))
            if member == "witnesses":
                _need(item["status_text"] == entry["status_text"])
    if question == "premises" and "model" in result:
        _need(result["model"] == rows[json.dumps(result["choice"])]["shown"].get("model"))
    if "candidates" in result:
        _need([[c["set"], c["index"]] for c in result["candidates"]] == frame.candidates)
    for candidate in result.get("candidates", []):
        if "narrowing" in candidate:
            _need(any(N["id"] == candidate["narrowing"] for N in frame.narrowings))
    for unit in result.get("units", []):
        _need(any(R.unit == unit for R in frame.sets))
    for name in ("restrictions", "reading_premises_used"):
        if name in result:
            _need(result[name] == row["restrictions"])
    for obj in _walk(result):
        for label in obj.get("conditional_on", []):
            # Under the completion every condition is a pair label or a restriction of the request; on the lower route
            # a choice's own answer may add its route's labels (coherence, alternatives, risk), which only it reads.
            if frame.completion:
                frame.label(label)
            else:
                _need(type(label) is str and label)


def _check_dead(row, case, frame):
    """The premises question's dead evidence, bound to the request: one note per dead certificate sent, naming its
    candidate; each untaken candidate a candidate of the document no row takes; a dead reading untaken, with a
    certificate the request sent and Lean noted accepted, and the finding that names it (`dead_finding`). Every
    other question has none."""
    sent = case.get("dead", [])
    if case["question"] != "premises" or frame.choices is None:
        _need(row["dead"] == [] and row["untaken"] == [] and row["dead_readings"] is None)
        return
    _need(len(row["dead"]) == len(sent))
    for d, note in zip(sent, row["dead"]):
        s, i = d.get("set"), d.get("index")
        if type(s) is not str or type(i) is not int or i < 0:
            _need(note == {"accepted": False})
        else:
            _need((note.get("set"), note.get("index")) == (s, i))
    for reading in row["untaken"]:
        frame.reading(reading)
        # An untaken candidate is one no row takes.
        _need(not any(reading in entry["choice"] for entry in row["per_choice"]))
    accepted = {(n["set"], n["index"]) for n in row["dead"] if n.get("accepted") is True}
    for d in row["dead_readings"] or []:
        frame.reading([d["set"], d["index"]])
        _need([d["set"], d["index"]] in row["untaken"] and (d["set"], d["index"]) in accepted)
        _need(d["finding"] == dead_finding(d["set"], d["index"]))


def _check_english(row, frame, rows):
    """The plan's lines name only what the request and the answer have: each reading a candidate, each shown model a
    row's shown piece (`<piece>@<k>`, the `k`th row), each label a condition label of the request (a `status` line: a
    row's status text), an E17 line one of the answer's dead readings. Which lines the plan has, and the conditions it
    states, are Lean's (`verdictsPlan_cites`, `plan_conditions_only`)."""
    from .ast import decimal_value
    ordered = list(rows.values())
    dead = [[d["set"], d["index"]] for d in row["dead_readings"] or []]
    for line in row["english"]:
        for reading in line["readings"]:
            frame.reading(reading)
        if line["frame"] == "E17":
            _need(line["readings"] and all(reading in dead for reading in line["readings"]))
        if line["model"] is not None:
            piece, at, k = line["model"].partition("@")
            _need(at and k.isdigit() and decimal_value(k) < len(ordered) and piece in ordered[decimal_value(k)]["shown"])
        if line["label"] is not None:
            if line["frame"] == "status":
                _need(any(entry["status_text"] == line["label"] for entry in ordered))
            else:
                frame.label(line["label"])


def _check_answer(row, case, frame):
    """Lean's answer to the `readings-verdicts` request `case`, as untrusted output: its schema and its binding to the
    request, nothing else (DRI ruling of rd-3 round 3; build checklist 4).

    Its shape is `Readings.Run.verdictsAnswer`'s (the generated, proved response schema: every field, its type, the
    result's form for the question, the status words). It answers this request (its id and question), for the route's
    finding, and names only what the request has: its rows are exactly the request's compatible choices (no empty,
    missing or extra row), each piece a row notes or shows was sent for that row's choice, a row's word names a piece
    it notes accepted, and every choice, reading, sentence, model, label and dead reading in the result, the
    conditions and the plan is the request's (`_check_rows`, `_check_result`, `_check_dead`, `_check_english`). What
    the answer concludes from the rows (the verdict, its conditions, which lines the plan says) is Lean's, by theorem
    (`readings_wire_verdicts_*`, `verdicts_conditions_*`, `verdictsPlan_cites`); the client never re-derives it, and
    relays Lean's English unchanged. Every piece of evidence sent is accepted: a refused or unanswered piece (a
    witness, certificate or model Python's own check accepted, or a dead reading's certificate) is
    `CheckerUnavailable`. A conflict package that does not certify CONFLICT-FREE is not refused: the witness search
    follows (4.3)."""
    sent = {json.dumps(e["choice"]): e for e in case.get("evidence", [])}
    with relayed():
        from .backends.service_schema import check_row
        # The producer's generated, proved response shape owns every field,
        # status spelling and JSON type.
        check_row("readings-route", row, {"id": row.get("id"), "kind": "readings-verdicts"}, 0)
        _need(row["id"] == case["id"] and row["question"] == case["question"])
        _need(row["finding_sets"] == frame.finding_sets)
        rows = _check_rows(row, case, frame)
        for label in row["restrictions"] + row["labels"]:
            frame.label(label)
        _check_result(row, case, frame, rows)
        _check_dead(row, case, frame)
        _check_english(row, frame, rows)
    for entry in row["per_choice"]:
        pieces = {k for k in sent.get(json.dumps(entry["choice"]), {}) if k != "choice"}
        for piece, error in entry["errors"].items():
            raise CheckerUnavailable(f"ReadingsConformance: Lean refused the {piece} Python built on a reading's "
                                     f"document: {error}")
        for piece in sorted(pieces - {"conflict"}):
            # The lower route checks no witness of a choice its packages certify CONFLICT-FREE.
            if piece == "witness" and entry["conflict"] == "CONFLICT-FREE" and piece not in entry["evidence"]:
                continue
            if entry["evidence"].get(piece) is not True:
                raise CheckerUnavailable(f"ReadingsConformance: Lean does not confirm the {piece} Python's "
                                         "generators found on a reading's document")
    for note in row["dead"]:
        if note.get("accepted") is not True:
            raise CheckerUnavailable("ReadingsConformance: Lean does not confirm the dead reading Python's prover "
                                     "certified")


def _check_sup_answer(row, case, route):
    """The generated shape and request relations only; Lean owns every derived result and English line."""
    from .backends.service_schema import check_row
    from .readings_s2_wording import PLAN_FRAMES, PLAN_RESULTS
    A = case.get("assumed") or []
    sent = {json.dumps(e["choice"]): e for e in case["evidence"]}
    candidates = [[R.id, i] for R in route.sets for i in range(len(R.candidates))]
    labels = {name for name, _ in route.labelled} | {name for name, _ in getattr(route.base, "soft_premises", ())}
    sets = {R.id for R in route.sets}
    versions = {R.id: R.version for R in route.sets}
    rules = {u["content"]["norm"]["name"] for u in route.document["units"]
             if isinstance(u.get("content"), dict) and "norm" in u["content"]}
    rules.update(obj["name"] for envelope in (route.environment, route.row.get("filled", {}))
                 for obj in _walk(envelope) if isinstance(obj.get("name"), str))
    for entry in route.row.get("names", []):
        for candidate in entry["candidates"]:
            for original, qualified in candidate["names"]:
                rules.update((original, qualified,
                              f"{original} under {entry['set']}@{versions[entry['set']]}:{candidate['index']}"))

    def choice(c, complete=False):
        _need(type(c) is list and all(x in candidates for x in c))
        _need(len({x[0] for x in c}) == len(c))
        if complete:
            _need([x[0] for x in c] == [R.id for R in route.sets])
            if route.choices is not None:
                _need(c in [route.choice_json(x) for x in route.choices])

    def label(value):
        _need(value in labels)

    with relayed():
        check_row("readings-route", row, case, 0)
        _need(row["id"] == case["id"] and row["question"] == case["question"] and row["route"] == "superposed")
        scopes = row["scopes"]
        proposals = row["model_proposals"]
        _need(proposals or not route.checked)
        _need(len({json.dumps(c) for c in proposals}) == len(proposals))
        for c in proposals:
            choice(c, complete=True)
            _need(all(x in c for x in A))
        scope_choices = [x["row"]["choice"] for x in scopes]
        _need(scopes and scope_choices[0] == A)
        _need(len({json.dumps(x) for x in scope_choices}) == len(scope_choices))
        if route.choices is not None:
            full = [route.choice_json(c) for c in route.choices]
            required = [c for c in full if all(x in c for x in A)]
            if case["question"] == "premises":
                required += [[c] for c in candidates if any(c in x for x in full)]
            expected = [A]
            for c in required:
                if c not in expected:
                    expected.append(c)
            _need(scope_choices == expected)
        else:
            _need(all(c == A or case["question"] == "premises" and len(c) == 1 for c in scope_choices))
        for scope in scopes:
            entry = scope["row"]
            choice(entry["choice"])
            scope_proposals = scope["model_proposals"]
            _need(scope_proposals or not route.checked)
            _need(len({json.dumps(c) for c in scope_proposals}) == len(scope_proposals))
            for c in scope_proposals:
                choice(c, complete=True)
                _need(all(x in c for x in entry["choice"]))
            pieces = sent.get(json.dumps(entry["choice"]), {})
            noted = entry["evidence"]
            _need(set(noted) == set(pieces) - {"choice"})
            _need(set(entry["errors"]) <= set(noted))
            _need(set(entry["shown"]) == set(scope["encoded"]))
            _need(set(entry["shown"]) <= set(noted) and set(entry["gaps"]) <= set(entry["shown"]))
            _need(set(scope["used"]) <= set(noted) and set(scope["mentions"]) == set(scope["used"]))
            for key, model in entry["shown"].items():
                _need(model == _shown_of(pieces[key], key))
                choice(scope["encoded"][key], complete=True)
                _need(all(c in scope["encoded"][key] for c in entry["choice"]))
                _bound_gaps(entry["gaps"].get(key, []), model, route)
            for ls in scope["used"].values():
                for l in ls:
                    label(l)
            for mentioned in scope["mentions"].values():
                _need(set(mentioned) <= sets)
        result = row["result"]
        if "budget" in result and "max_choices" not in result["budget"]:
            _need(result["budget"] == case["budget"])
        if "target" in result:
            _need(any(p.get("witness", {}).get("target") == result["target"] and
                      p.get("witness", {}).get("tuple") == result.get("tuple")
                      for e in case["evidence"] for p in [e.get("witness", {})]))
        _need(result["route"] == "superposed")
        _need("verdict" in result if case["question"] == "query" else "status" in result)
        if case["question"] == "query":
            _need(result.get("assumed", []) == A)
        references = [result]
        references += [result[name] for name in ("proof", "countermodel") if name in result]
        references += [obj for name in ("proofs", "countermodels", "choices", "candidates")
                       for obj in result.get(name, [])]
        for obj in references:
            _need(set(obj.get("mentions", [])) <= sets)
            _need(all(s in route.base.sorts for s in obj.get("sorts", [])))
            _need(all(name in rules for name, _ in obj.get("selected") or []))
            if "choice" in obj:
                choice(obj["choice"], complete=True)
            for key in ("conditional_on", "reading_premises_used", "restrictions"):
                for l in obj.get(key, []):
                    label(l)
            if "model" in obj:
                _need(any(obj["model"] == s["row"]["shown"].get(k) and obj.get("choice") == s["encoded"].get(k)
                          for s in scopes for k in ("witness", "model", "countermodel")))
                _bound_gaps(obj.get("gaps", []), obj["model"], route)
        for member in ("proofs", "countermodels", "choices"):
            if member in result:
                _need(route.choices is not None)
                _need([obj["choice"] for obj in result[member]] ==
                      [route.choice_json(c) for c in route.choices if all(x in route.choice_json(c) for x in A)])
        for proof in ([result["proof"]] if "proof" in result else []) + result.get("proofs", []):
            _need(any(s["row"]["choice"] == proof["choice"] and "certificate" in s["row"]["evidence"]
                      for s in scopes))
        for l in row["restrictions"]:
            label(l)
        sent_dead = case.get("dead", []) if case["question"] == "premises" else []
        _need(len(row["dead"]) == len(sent_dead))
        for note, sent_note in zip(row["dead"], sent_dead):
            _need((note.get("set"), note.get("index")) == (sent_note.get("set"), sent_note.get("index")))
        _need(len({(d["set"], d["index"]) for d in row["dead_readings"] or []}) == len(row["dead_readings"] or []))
        _need(len({tuple(c) for c in row["untaken"]}) == len(row["untaken"]))
        if case["question"] == "premises":
            _need("candidates" not in result or [[c["set"], c["index"]] for c in result["candidates"]] == candidates)
            for c in result.get("candidates", []):
                if "choice" in c:
                    _need([c["set"], c["index"]] in c["choice"])
                if "narrowing" in c:
                    _need(any(n["id"] == c["narrowing"] and n["set"] == c["set"] for n in route.narrowings))
        for d in row["dead_readings"] or []:
            _need([d["set"], d["index"]] in candidates)
            _need(any(e.get("set") == d["set"] and e.get("index") == d["index"] for e in case.get("dead", [])))
        _need(all(c in candidates for c in row["untaken"]))
        for note in row["dead"]:
            _need(any(e.get("set") == note.get("set") and e.get("index") == note.get("index")
                      for e in case.get("dead", [])))
        for line in row["english"]:
            _need(line["frame"] in PLAN_FRAMES and (line["result"] is None or line["result"] in PLAN_RESULTS))
            choice(line["readings"])
            if line["label"] is not None:
                if line["frame"] == "status":
                    _need(any(s["row"]["status_text"] == line["label"] for s in scopes))
                else:
                    label(line["label"])
            if line["model"] is not None:
                from .ast import decimal_value
                piece, sep, index = line["model"].partition("@")
                _need(sep and index.isascii() and index.isdecimal())
                scope = scopes[decimal_value(index)]
                _need(piece in scope["encoded"] and line["readings"] == scope["encoded"][piece])
                _bound_gaps(line["gaps"], scope["row"]["shown"][piece], route)


def _bound_gaps(gaps, model, route):
    predicates = route.doc["environment"].predicates
    for name, values, answer in gaps:
        _need(name in predicates and predicates[name].regulated is not None and
              predicates[name].regulated.default == "unspecified" and len(values) == len(predicates[name].arguments) and
              all(e in model["domains"].get(sort, []) for sort, e in zip(predicates[name].arguments, values)) and
              type(answer) is bool)


def _dead_certificates(route, untaken):
    """Certificates of `¬χ` from `choiceCore D` for the candidates Lean names untaken (1.9; Python's prover,
    untrusted), or None as soon as one is not found within the budget (Lean reports no incomplete list)."""
    from .ast import Not, formula_from_data
    from .entailment import prove_entailment
    from .readings_sup import choice_atom, choice_core
    env = Superposed._core_environment(route)
    core = [formula_from_data(env, ast, _generated=True)
            for _, ast in choice_core(route.sets, route.couplings, route.narrowings)]
    out = []
    for s, i in untaken:
        atom = formula_from_data(env, choice_atom(route.sets, s, i), _generated=True)
        proof = prove_entailment(env, core, Not(atom), max_steps=BUDGET["max_steps"])
        if proof.status != "Found":
            return None
        out.append({"set": s, "index": i, "certificate": proof.certificate})
    return out


class _ChoiceDocument:
    """`choiceDoc D c` as an ordinary document of the lower route (4.6): its own rules and assertions under their
    own names. Python's prover and model search generate evidence on it (untrusted); Lean checks each piece through
    the lower route on the document it regenerates for the choice (`readings-verdicts`)."""

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
            self.side._elaborate(deferred=False)
        # The layer premises in the lower route's certificate order: its Background (the soft premises, and `Lim_D`
        # on the rights chain, are the environment's, which the prover prepends) ++ these ++ assertions ++ Γ.
        if self.chain == "soft":
            from .softnorms import SoftEnvironment
            self.lower_env = SoftEnvironment(lower)
            self.soft = self.side.soft
            self.env = self.soft.extended_env
            self.layers = [f for _, f in self.soft.elaborated.premises()]
            self.searched = [f for _, f in self.soft.extended_env.soft_premises]
        elif self.chain == "norms":
            from .environment import Environment
            from .norms import NormDocument
            self.lower_env = Environment(lower)
            self.norms = NormDocument(self.lower_env, [c.raw for c in contents if c.kind == "norm"])
            self.env = self.lower_env
            self.layers = [f for _, f in self.norms.premises()]
            self.searched = []
        else:
            from .document import _environment
            self.lower_env = _environment(lower)
            self.rights = self.side.rights
            self.soft = self.rights.soft_document
            self.env = self.soft.extended_env
            self.layers = [f for _, f in self.soft.elaborated.premises()]
            self.searched = ([f for _, f in self.soft.extended_env.soft_premises] +
                             [f for _, f in self.rights.limitation_premises])

    def _all(self, gamma=()):
        from .ast import formula_from_data
        return self.layers + [formula_from_data(self.env, ast, _generated=True)
                              for ast in self.assertions + list(gamma)]

    def _phi(self, conclusion_ast):
        from .ast import Bottom, formula_from_data
        return Bottom() if conclusion_ast is None else formula_from_data(self.env, conclusion_ast, _generated=True)

    def certificate_case(self, conclusion_ast, gamma=(), max_steps=None):
        """A certificate of `conclusion_ast` (⊥ when None) from the choice's document and Γ, found by Python's prover
        and checked by its own replay: the lower route's certificate kind Lean runs on the choice's regenerated
        document with its assertions and conflict packages, or None within the budget."""
        from .entailment import check_entailment_certificate, prove_entailment
        steps = BUDGET["max_steps"] if max_steps is None else max_steps
        premises, phi = self._all(gamma), self._phi(conclusion_ast)
        proof = prove_entailment(self.env, premises, phi, max_steps=steps)
        if proof.status != "Found" or not check_entailment_certificate(self.env, premises, phi, proof.certificate,
                                                                       max_steps=steps).valid:
            return None
        return {"kind": f"{self.chain}-certificate", "certificate": self._bound(proof.certificate, premises, phi)}

    def _bound(self, certificate, premises, phi):
        """The certificate as the lower route binds it. The rights route binds `E″′` (the source environment's
        profiles and rights block with the generated declarations, `expected_environment_prime`), which no Python
        environment decodes, so the bindings are recomputed over it: the trace is unchanged, and Lean checks it
        against the premises it regenerates."""
        if self.chain != "rights":
            return certificate
        from .ast import formula_to_data
        from .background import background
        from .rights_route import expected_environment_prime
        from .wire import digest
        prime = expected_environment_prime(self.rights)
        version = "v0.2:" + ",".join(prime["profiles"])
        environment_id = digest(f"ve-environment-{version}\n", prime)

        def meaning(formula):
            return digest(f"ve-meaning-{version}\n", {"environment_id": environment_id,
                                                      "ast": formula_to_data(self.env, formula, _generated=True)})
        listed = [premise.formula for premise in background(self.env)] + list(premises)
        return {**certificate, "environment_id": environment_id,
                "premise_meaning_ids": [meaning(f) for f in listed], "conclusion_meaning_id": meaning(phi)}

    def model_case(self, conclusion_ast, gamma=()):
        """A model of the choice's document and Γ with `conclusion_ast` false (any model when None), found by Python's
        search and checked by its own evaluator: `choice-model` with the model's base (the chain decoder's form) and
        the complete model shown, or None within the budget."""
        from .search import check_countermodel, find_countermodel
        # The Background's soft and limitation premises are searched as premises too, so that the search
        # interprets the predicates only they use (it fixes unused predicates empty).
        premises, phi = self._all(gamma) + self.searched, self._phi(conclusion_ast)
        found = find_countermodel(self.env, premises, phi, max_domain_size=BUDGET["max_domain_size"],
                                  max_models=BUDGET["max_models"], max_evaluations=BUDGET["max_evaluations"])
        if found.status != "Found" or not check_countermodel(self.env, premises, phi, found.model,
                                                             max_evaluations=BUDGET["max_evaluations"]).valid:
            return None
        data = found.model.to_dict()
        return {"kind": "choice-model", "model": self._base_model(data), "shown": data}

    def _base_model(self, data):
        """The model's base, the chain decoder's form: the regulated (layer) tables are the outcome substitution's."""
        document = self.norms if self.chain == "norms" else self.soft.elaborated
        keep = document.base_environment().predicates
        return {**data, "relations": {name: rows for name, rows in data["relations"].items() if name in keep}}

    def conflict_case(self):
        """The lower route's conflict kind with Python's packages for the choice's document (a certificate of each
        target's closed negation, bound to the choice's document hash)."""
        from .ast import Not, _to_data, formula_from_data
        from .entailment import prove_entailment
        from .norms import _bind, _prove_targets
        if self.chain == "norms":
            packages = _prove_targets(self.norms, self.norms.base_environment(), BUDGET["max_steps"])
            return {"kind": "norms-conflict", "packages": packages if isinstance(packages, dict) else {}}
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
        return ({"kind": "soft-conflict", "packages": packages, "pairs": {}} if self.chain == "soft" else
                {"kind": "rights-conflict", "packages": packages})

    def witness_case(self):
        """The lower route's conflict kind with a witness: a finite base model where a conflict target holds."""
        witness = self._witness()
        if witness is None:
            return None
        kind = {"norms": "norms-conflict", "soft": "soft-conflict", "rights": "rights-conflict"}[self.chain]
        return {"kind": kind, "witness": witness}

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

    def _witness(self):
        """A finite base model where some conflict target holds, with its tuple (Python's search, untrusted)."""
        from .ast import Not
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


class _FilledView:
    """What `norm_defaults_route.filled_certificate` reads of a document, from Lean's rows: the source environment,
    `Fill_T` and the filled layers over E‴."""

    def __init__(self, env, filled_env, fill, layers):
        from types import SimpleNamespace
        self.env = env
        self.fill_premises = [(None, f) for f in fill]
        self.filled = SimpleNamespace(env=filled_env, premises=lambda: [(None, f) for f in layers])


class _FilledChoiceDocument:
    """A choice's document under the unspecified completion (readings-defaults 3.4): `choiceU N c` as Lean
    regenerates it. Lean's `norm-defaults-elaborate` row for the choice (a `readings-choice` inner kind) gives
    `E‴_base`, the base Background, `Fill_T`, the filled layers and the conflict targets; Python's prover and model
    search run on those formulas only (untrusted generators, D12: Python builds no `fill`), and every certificate,
    witness and model goes back to `readings-choice` with norm-defaults' inner kinds, which checks it on the choice's
    document. A refusal of evidence Python's own check accepted is `CheckerUnavailable`, never a verdict."""

    chain = "norms"

    def __init__(self, route, choice):
        from .ast import _Decoder, formula_from_data
        from .environment import Environment
        self.route, self.choice = route, choice
        self.side = None  # a choice's decision tables: none on the norms chain (`S2Wording._choice_decisions`)
        senv = route.source.senv
        row = self._inner({"kind": "norm-defaults-elaborate"})
        self.elaboration = row
        self.base = Environment(row["base_environment"])
        # E‴: the filled frame, the same for every choice (the frame's unspecified predicates), Lean's.
        self.env = Environment(route.row["filled"]["environment"])
        self.source_env = Environment(senv.lower_data)
        self.tables = [item["name"] for item in row["unsaid"]]
        self.fill = [formula_from_data(self.env, item["ast"], _generated=True) for item in row["fill"]]
        self.layers = [formula_from_data(self.env, item["ast"], _generated=True) for item in row["premises"]]
        # A target is open over its sorts (Lean's `conflict_targets`); it is typed once closed (`_bind`).
        self.targets = [(t["target"], tuple(t["sorts"]), _Decoder().decode(t["ast"]))
                        for t in row["conflict_targets"]]
        self.assertions = [c.body for c in self._contents() if c.kind == "assertion"]
        self.view = _FilledView(self.source_env, self.env, self.fill, self.layers)

    def _contents(self):
        from .readings_sup import choice_contents
        return choice_contents(self.route.source, self.choice)

    def _row(self, inner):
        row = self.route.lean("readings-choice", choice=self.route.choice_json(self.choice), inner=inner)
        answer = row["inner"]
        if answer.get("status") != "ok":
            raise CheckerUnavailable(f"ReadingsConformance: Lean refused a case Python built on a reading's filled "
                                     f"document: {answer.get('error')}")
        return row

    def _inner(self, inner):
        return self._row(inner)["inner"]

    def _gamma(self, gamma=()):
        from .ast import formula_from_data
        return [formula_from_data(self.env, ast, _generated=True) for ast in self.assertions + list(gamma)]

    def _phi(self, conclusion_ast):
        from .ast import Bottom, formula_from_data
        return Bottom() if conclusion_ast is None else formula_from_data(self.env, conclusion_ast, _generated=True)

    def _split(self, data):
        """A model of E‴ as `choice-model` and a witness read it: the base over `E‴_base` without the filled tables,
        and the filling (the tables) beside it; the regulated tables are the outcome substitution's."""
        base = set(self.base.predicates) - set(self.tables)
        relations = data.get("relations", {})
        model = {**data, "relations": {name: rows for name, rows in relations.items() if name in base}}
        return model, {name: relations.get(name, []) for name in self.tables}

    # -- the conflict status (`norm-defaults-conflict`: packages, else a filled witness)

    def conflict_case(self):
        return {"kind": "norm-defaults-conflict", "packages": self._packages()}

    def _packages(self):
        """A certificate of each target's closed negation from `Fill_T` over `E‴_base` (norm-defaults 3.1: on the norms
        chain the base Background is `Fill_T`, Lean's `baseBackgroundU`), bound as Lean binds a package
        (`decodePackageX`): to the choice's environment id and document hash (the row's), and its certificate to
        `E‴_base` and the ASTs of `Fill_T`."""
        from .ast import Not, formula_to_data
        from .entailment import prove_entailment
        from .norms import _bind
        from .wire import digest
        row = self.elaboration

        def meaning(ast):
            return digest(f"ve-meaning-{self.base.identity_version}\n",
                          {"environment_id": self.base.environment_id, "ast": ast})
        fill = self._base_fill()
        packages = {}
        for target, sorts, formula in self.targets:
            conclusion = _bind(Not(formula), sorts)
            proof = prove_entailment(self.base, fill, conclusion, max_steps=BUDGET["max_steps"], _background=False)
            if proof.status != "Found":
                continue
            certificate = {**proof.certificate, "environment_id": self.base.environment_id,
                           "premise_meaning_ids": [meaning(item["ast"]) for item in row["fill"]],
                           "conclusion_meaning_id": meaning(formula_to_data(self.base, conclusion, _generated=True))}
            packages[target] = {"environment_id": row["environment_id"], "document_hash": row["document_hash"],
                                "target": target, "certificate": certificate}
        return packages

    def witness_case(self):
        """A filled witness: the base model and its filling apart, the complete model shown."""
        witness = self._witness()
        if witness is None:
            return None
        model, filling = self._split(witness["model"])
        return {"kind": "norm-defaults-conflict", "witness": {"target": witness["target"], "model": model,
                                                              "filling": filling, "tuple": witness["tuple"]},
                "shown": witness["model"]}

    def _base_fill(self):
        """`Fill_T` over `E‴_base`: it reads base predicates and the filled tables only."""
        from .ast import formula_from_data
        return [formula_from_data(self.base, item["ast"], _generated=True) for item in self.elaboration["fill"]]

    def _witness(self):
        """A base model and filling where `Fill_T` holds and some conflict target holds, with its tuple."""
        from .evaluate import _Evaluator, _Exhausted
        from .ast import Not
        from .norms import _bind
        from .search import find_countermodel
        fill = self._base_fill()
        for target, sorts, formula in self.targets:
            found = find_countermodel(self.base, fill, _bind(Not(formula), sorts),
                                      max_domain_size=BUDGET["max_domain_size"], max_models=BUDGET["max_models"],
                                      max_evaluations=BUDGET["max_evaluations"])
            if found.status != "Found":
                continue
            model = found.model
            evaluator = _Evaluator(self.base, model, BUDGET["max_evaluations"], trace=False)
            try:
                values = next((values for values in product(*(model.domains[s] for s in sorts))
                               if evaluator.formula(formula, tuple(zip(reversed(sorts), reversed(values))))[0]),
                              None)
            except _Exhausted:
                values = None
            if values is not None:
                return {"target": target, "model": model.to_dict(), "tuple": list(values)}
        return None

    # -- certificates and models (`norm-defaults-certificate`, `choice-model`)

    def certificate_case(self, conclusion_ast, gamma=(), max_steps=None):
        """A certificate of `conclusion_ast` (⊥ when None) from the choice's filled document and Γ, bound to the source
        environment as Lean binds a norm-defaults certificate; Lean accepts it only with the choice's conflict
        packages (S2a 14.8). None within the budget."""
        from .norm_defaults_route import filled_certificate
        steps = BUDGET["max_steps"] if max_steps is None else max_steps
        own, phi = self._gamma(gamma), self._phi(conclusion_ast)
        # The prover replays the trace it generated before it returns it (`prove_entailment`).
        certificate = filled_certificate(self.view, own, phi, max_steps=steps)
        if certificate is None:
            return None
        return {"kind": "norm-defaults-certificate", "certificate": certificate}

    def model_case(self, conclusion_ast, gamma=()):
        """A model of the choice's filled document and Γ with `conclusion_ast` false (any model when None): its base
        and its filling apart (`choice-model`), the complete model shown. None within the budget."""
        from .search import check_countermodel, find_countermodel
        premises, phi = self.fill + self.layers + self._gamma(gamma), self._phi(conclusion_ast)
        found = find_countermodel(self.env, premises, phi, max_domain_size=BUDGET["max_domain_size"],
                                  max_models=BUDGET["max_models"], max_evaluations=BUDGET["max_evaluations"])
        if found.status != "Found" or not check_countermodel(self.env, premises, phi, found.model,
                                                             max_evaluations=BUDGET["max_evaluations"]).valid:
            return None
        data = found.model.to_dict()
        model, filling = self._split(data)
        return {"kind": "choice-model", "model": model, "filling": filling, "shown": data}


__all__ = ["BUDGET", "Enumerated", "PENDING", "Pending", "Superposed", "context"]
