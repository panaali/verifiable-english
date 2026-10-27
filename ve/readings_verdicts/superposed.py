"""The superposed route (4.5): Python generates evidence on `sup D` and Lean's readings route checks it."""
from __future__ import annotations

from itertools import product

from ..errors import CheckerUnavailable, VEError
from .binding import _check_sup_answer
from .choice import _ChoiceDocument
from .route import BUDGET, _Route, _request_key


def _found(search, premise_check):
    """A search's Found result, or None (NotFound or a spent budget). In the premise check (`premise_check`: no
    Γ and no conclusion) a Rust call that timed out is no witness too, and the answer is then Lean's alone (DRI
    decision ME1, DELTA row 4); in any other query (an entailment's countermodel) it is CheckerUnavailable, as
    before premise-scale."""
    from ..backends.rust_jsonl import RustTimeout
    try:
        found = search()
    except RustTimeout:
        if not premise_check:
            raise
        return None
    return found if found.status == "Found" else None


def _scaled(env, premises, phi):
    """premise-scale, in the premise check only (DELTA row 1), after the route's own searches found no model:
    the search again over `sup D`
    within the route's budget (`BUDGET`) with the sorts Lean raises (`ve.search.premise_budget`, only
    at Lean's own domain bound), then the ground-fact route (the premises' stated facts as their own
    model). Each runs only when every earlier search found nothing, so no model an earlier search
    finds changes; Lean checks whatever is found."""
    from ..search import find_countermodel, premise_budget
    lean = premise_budget(env, premises)
    sort_bounds = lean.sort_bounds if BUDGET["max_domain_size"] == lean.max_domain_size else {}
    options = {"max_domain_size": BUDGET["max_domain_size"], "max_models": BUDGET["max_models"],
               "max_evaluations": BUDGET["max_evaluations"], "sort_bounds": sort_bounds}
    found = None
    if sort_bounds:
        found = _found(lambda: find_countermodel(env, premises, phi, **options), True)
    if found is None:
        found = _found(lambda: find_countermodel(env, premises, phi, **options, ground_only=True), True)
    return found


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
        from ..readings_sup import superposed_document
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
        from ..ast import formula_from_data
        return [formula_from_data(env, ast, _generated=True) for ast in asts]

    def _atoms(self, A):
        from ..readings_sup import choice_atom
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
        from ..ast import Top
        from ..entailment import prove_entailment
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
        from ..ast import Not
        from ..entailment import prove_entailment
        from ..norms import _bind
        from ..readings_sup import CHECK_BUDGET_TEXT
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
        from ..ast import Not
        from ..evaluate import _Evaluator, _Exhausted
        from ..norms import _bind
        from ..search import find_countermodel
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
        from ..ast import Bottom, formula_from_data
        from ..search import find_countermodel
        key = (tuple(tuple(x) for x in A), repr(gamma), repr(conclusion))
        if key in self._models:
            return self._models[key]
        usable = self.checked and (not A or self.taken(A))
        # The premise check (no Γ, no conclusion) is premise-scale's only scope: there alone a Rust timeout is no
        # witness and the scaled search runs; an entailment's countermodel search is as before (review F1).
        premise_check = conclusion is None and not gamma
        # Under the completion a choice's own document is Lean's `choiceU N c`, whose models carry a separate filling;
        # the search runs on `sup (fillDoc N)` itself, `Fill_T` in its slot (plan RD-6b).
        result = self._lifted(A, gamma, conclusion, premise_check) if usable and not self.completion else None
        if result is None and usable:
            phi = Bottom() if conclusion is None else formula_from_data(self.ext, conclusion, _generated=True)
            full = self._full(A, gamma)
            found = _found(lambda: find_countermodel(
                self.ext, full, phi, max_domain_size=BUDGET["max_domain_size"], max_models=BUDGET["max_models"],
                max_evaluations=BUDGET["max_evaluations"]), premise_check)
            if found is None and premise_check:
                found = _scaled(self.ext, full, phi)
            if found is not None:
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
        from ..ast import Exists, _to_data, formula_from_data
        from ..backends.rust_jsonl import configured_timeout, run
        from ..norms import _bind
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

    def _lifted(self, A, gamma, conclusion, premise_check):
        from ..ast import Bottom, formula_from_data
        from ..search import check_countermodel, find_countermodel
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
                found = _found(lambda: find_countermodel(
                    own.env, premises, phi, max_domain_size=BUDGET["max_domain_size"],
                    max_models=BUDGET["max_models"], max_evaluations=BUDGET["max_evaluations"]), premise_check)
                valid = found is not None and check_countermodel(
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
        from ..readings_sup import HERE, READING_SORT, bit_name, bits_of
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
        from ..ast import Bottom, formula_from_data
        from ..entailment import prove_entailment
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
        from ..background import background
        from ..environment import Environment
        from ..readings_sup import choice_vocabulary
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
        from ..readings_route import run_lean
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

    def _settle(self, question, A, generate, gamma=(), conclusion=None, asked_first=True):
        """Lean's answer once every scope it lists has evidence. Lean lists the scopes its answer can use (the
        complete choices only while the asked scope leaves the answer open); Python generates evidence for each
        listed scope once, the asked scope alone first when `asked_first`, and asks again until none is new."""
        def key(choice):
            return tuple(tuple(x) for x in choice)
        row = self._ask(question, A, gamma=gamma, conclusion=conclusion)
        done = set()
        while True:
            todo = [scope["row"]["choice"] for scope in row["scopes"] if key(scope["row"]["choice"]) not in done]
            if asked_first and not done:
                todo = todo[:1]
            if not todo:
                return row
            for choice in todo:
                done.add(key(choice))
                generate(choice)
            row = self._ask(question, A, gamma=gamma, conclusion=conclusion)

    def _prepare(self, question, A=(), gamma=(), conclusion=None):
        return self._settle(question, A, self._prepare_conflict, gamma, conclusion)

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
            def generate(A):
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
            # Every scope a premises answer lists is a candidate's or the global one: generated in one round.
            row = self._settle("premises", None, generate, asked_first=False)
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
        def generate(A):
            self._prepare_conflict(A)
            proof = self._generate_certificate(A, premises, conclusion_ast)
            if proof is not None:
                self._pieces(A)["certificate"] = proof
            else:
                found = self.model(A, premises, conclusion_ast)
                if found is not None:
                    self._pieces(A)["countermodel"] = {"model": found["model"]}
        row = self._settle("query", assumed, generate, premises, conclusion_ast)
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


def _dead_certificates(route, untaken):
    """Certificates of `¬χ` from `choiceCore D` for the candidates Lean names untaken (1.9; Python's prover,
    untrusted), or None as soon as one is not found within the budget (Lean reports no incomplete list)."""
    from ..ast import Not, formula_from_data
    from ..entailment import prove_entailment
    from ..readings_sup import choice_atom, choice_core
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
