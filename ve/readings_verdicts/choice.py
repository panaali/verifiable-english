"""A compatible choice's own document, on which Python's untrusted prover and model search generate evidence that
Lean checks (4.6; readings-defaults 3.4): `_ChoiceDocument`, and under a completion `_FilledChoiceDocument`."""
from __future__ import annotations

import copy
from itertools import product

from ..errors import CheckerUnavailable
from .route import BUDGET


class _ChoiceDocument:
    """`choiceDoc D c` as an ordinary document of the lower route (4.6): its own rules and assertions under their
    own names. Python's prover and model search generate evidence on it (untrusted); Lean checks each piece through
    the lower route on the document it regenerates for the choice (`readings-verdicts`)."""

    def __init__(self, route, choice):
        from ..readings_s1 import Content
        from ..readings_sup import choice_contents
        self.route, self.choice = route, choice
        senv = route.source.senv
        self.chain = senv.chain
        contents = choice_contents(route.source, choice)
        self.assertions = [c.body for c in contents if isinstance(c, Content) and c.kind == "assertion"]
        lower = senv.lower_data
        # The chain's own check of the choice's document (the route refused any choice it rejects at load, 4.1
        # step 5), and its hash as the lower route binds a package to it.
        from ..readings_s1 import Side
        self.side = Side(senv, contents, route.source.unit_ids)
        if self.chain != "norms":
            self.side._elaborate(deferred=False)
        # The layer premises in the lower route's certificate order: its Background (the soft premises, and `Lim_D`
        # on the rights chain, are the environment's, which the prover prepends) ++ these ++ assertions ++ Γ.
        if self.chain == "soft":
            from ..softnorms import SoftEnvironment
            self.lower_env = SoftEnvironment(lower)
            self.soft = self.side.soft
            self.env = self.soft.extended_env
            self.layers = [f for _, f in self.soft.elaborated.premises()]
            self.searched = [f for _, f in self.soft.extended_env.soft_premises]
        elif self.chain == "norms":
            from ..environment import Environment
            from ..norms import NormDocument
            self.lower_env = Environment(lower)
            self.norms = NormDocument(self.lower_env, [c.raw for c in contents if c.kind == "norm"])
            self.env = self.lower_env
            self.layers = [f for _, f in self.norms.premises()]
            self.searched = []
        else:
            from ..document import _environment
            self.lower_env = _environment(lower)
            self.rights = self.side.rights
            self.soft = self.rights.soft_document
            self.env = self.soft.extended_env
            self.layers = [f for _, f in self.soft.elaborated.premises()]
            self.searched = ([f for _, f in self.soft.extended_env.soft_premises] +
                             [f for _, f in self.rights.limitation_premises])

    def _all(self, gamma=()):
        from ..ast import formula_from_data
        return self.layers + [formula_from_data(self.env, ast, _generated=True)
                              for ast in self.assertions + list(gamma)]

    def _phi(self, conclusion_ast):
        from ..ast import Bottom, formula_from_data
        return Bottom() if conclusion_ast is None else formula_from_data(self.env, conclusion_ast, _generated=True)

    def certificate_case(self, conclusion_ast, gamma=(), max_steps=None):
        """A certificate of `conclusion_ast` (⊥ when None) from the choice's document and Γ, found by Python's prover
        and checked by its own replay: the lower route's certificate kind Lean runs on the choice's regenerated
        document with its assertions and conflict packages, or None within the budget."""
        from ..entailment import check_entailment_certificate, prove_entailment
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
        from ..ast import formula_to_data
        from ..background import background
        from ..rights_route import expected_environment_prime
        from ..wire import digest
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
        from ..search import check_countermodel, find_countermodel
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
        from ..ast import Not, _to_data, formula_from_data
        from ..entailment import prove_entailment
        from ..norms import _bind, _prove_targets
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
        from ..ast import _to_data, formula_from_data
        from ..environment import Environment
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
        from ..ast import Not
        from ..evaluate import _Evaluator, _Exhausted
        from ..norms import _bind
        from ..search import find_countermodel
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
    the extra base premises `X` (`Soft_T` on the soft chain, none on the norms chain), `Fill_T` and the filled layers
    over E‴."""

    def __init__(self, env, filled_env, fill, layers, base_premises=()):
        from types import SimpleNamespace
        self.env = env
        self.base_premises = [(None, f) for f in base_premises]
        self.fill_premises = [(None, f) for f in fill]
        self.filled = SimpleNamespace(env=filled_env, premises=lambda: [(None, f) for f in layers])


class _FilledChoiceDocument:
    """A choice's document under the unspecified or the soft completion (readings-defaults 3.4, rd-9-soft-chain
    4.3): `choiceU N c` as Lean regenerates it on its layered source. Lean's `norm-defaults-elaborate` row for the
    choice (a `readings-choice` inner kind) gives `E‴_base`, the base Background, `Soft_T` on the filled tree (the
    extra base premises `X`, none on the norms chain), `Fill_T`, the filled layers and the conflict targets; Python's
    prover and model search run on those formulas only (untrusted generators, D12: Python builds no `fill`, `X` or
    `Coh_T`), and every certificate, witness and model goes back to `readings-choice` with norm-defaults' inner kinds,
    which checks it on the choice's document. A refusal of evidence Python's own check accepted is
    `CheckerUnavailable`, never a verdict."""

    def __init__(self, route, choice):
        from ..ast import _Decoder, formula_from_data
        from ..environment import Environment
        self.route, self.choice = route, choice
        senv = route.source.senv
        self.chain = senv.chain
        prefetched = (route._prefetched.pop(route._key(choice), None)
                      if hasattr(route, "_prefetched") else None)
        if prefetched is not None:
            route._checked(prefetched, "readings-choice")
        row = self._answer(prefetched) if prefetched is not None else self._inner({"kind": "norm-defaults-elaborate"})
        self.elaboration = row
        self.base = Environment(row["base_environment"])
        # E‴: the filled frame (the frame's unspecified predicates), Lean's, with the choice's own base predicates
        # (on the soft chain its decision tables) from its `E‴_base`.
        filled = copy.deepcopy(route.row["filled"]["environment"])
        for name, declaration in row["base_environment"]["vocabulary"]["predicates"].items():
            filled["vocabulary"]["predicates"].setdefault(name, declaration)
        if self.chain == "norms":
            self.env = Environment(filled)
        else:
            from ..softnorms import SoftEnvironment
            self.env = SoftEnvironment(filled, generated=True)
        self.source_env = Environment(senv.lower_data)
        self.tables = [item["name"] for item in row["unsaid"]]
        self.soft = [formula_from_data(self.env, item["ast"], _generated=True) for item in row["soft"]]
        self.fill = [formula_from_data(self.env, item["ast"], _generated=True) for item in row["fill"]]
        self.layers = [formula_from_data(self.env, item["ast"], _generated=True) for item in row["premises"]]
        # A choice's decision tables for the wording (`S2Wording._choice_decisions`): none on the norms chain.
        self.side = None
        if self.chain != "norms":
            from ..readings_s1 import Side
            self.side = Side(senv, self._contents(), route.source.unit_ids)
            self.side._elaborate()
        # A target is open over its sorts (Lean's `conflict_targets`); it is typed once closed (`_bind`).
        self.targets = [(t["target"], tuple(t["sorts"]), _Decoder().decode(t["ast"]))
                        for t in row["conflict_targets"]]
        self.assertions = [c.body for c in self._contents() if c.kind == "assertion"]
        self.view = _FilledView(self.source_env, self.env, self.fill, self.layers, self.soft)

    def _contents(self):
        from ..readings_sup import choice_contents
        return choice_contents(self.route.source, self.choice)

    def _row(self, inner):
        row = self.route.lean("readings-choice", choice=self.route.choice_json(self.choice), inner=inner)
        self._answer(row)
        return row

    @staticmethod
    def _answer(row):
        answer = row["inner"]
        if answer.get("status") != "ok":
            raise CheckerUnavailable(f"ReadingsConformance: Lean refused a case Python built on a reading's filled "
                                     f"document: {answer.get('error')}")
        return answer

    def _inner(self, inner):
        return self._row(inner)["inner"]

    def _gamma(self, gamma=()):
        from ..ast import formula_from_data
        return [formula_from_data(self.env, ast, _generated=True) for ast in self.assertions + list(gamma)]

    def _phi(self, conclusion_ast):
        from ..ast import Bottom, formula_from_data
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
        """A certificate of each target's closed negation from the layered base background over `E‴_base`
        (`L.background`: `Background_base(E‴)`'s literals, `X`, then `Fill_T`; on the norms chain Lean's
        `baseBackgroundU` and `LayeredU.background`), bound as Lean binds a package (`decodePackageX`,
        `decodePackageU`): to the choice's environment id and document hash (the row's), and its certificate to
        `E‴_base` and the ASTs of that background."""
        from ..ast import Not, formula_from_data, formula_to_data
        from ..entailment import prove_entailment
        from ..norms import _bind
        from ..wire import digest
        row = self.elaboration

        def meaning(ast):
            return digest(f"ve-meaning-{self.base.identity_version}\n",
                          {"environment_id": self.base.environment_id, "ast": ast})
        listed = self._base_background()
        fill = [formula_from_data(self.base, ast, _generated=True) for ast in listed]
        packages = {}
        for target, sorts, formula in self.targets:
            conclusion = _bind(Not(formula), sorts)
            proof = prove_entailment(self.base, fill, conclusion, max_steps=BUDGET["max_steps"], _background=False)
            if proof.status != "Found":
                continue
            certificate = {**proof.certificate, "environment_id": self.base.environment_id,
                           "premise_meaning_ids": [meaning(ast) for ast in listed],
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

    def _base_literals(self):
        """`Background_base` of the filled document, as Lean's elaboration row lists it: the literals' distinctness
        (their ASTs)."""
        return [item["ast"] for item in self.elaboration["background"] if item["generator"] == "literals"]

    def _base_background(self):
        """The ASTs of the layered base background, Lean's `L.background`: the row's literal Background
        (`_base_literals`), `X` (its `soft`), then `Fill_T`; each reads base predicates and the filled tables only.
        The plain `norm-defaults-elaborate` row of the zero-set route (`ask._zero_generator`) has no layered source,
        so no `soft`: there `X` is empty (Lean's `baseBackgroundU`)."""
        row = self.elaboration
        return (self._base_literals() + [item["ast"] for item in row.get("soft", ())] +
                [item["ast"] for item in row["fill"]])

    def _base_fill(self):
        """The layered base background over `E‴_base` (`_base_background`)."""
        from ..ast import formula_from_data
        return [formula_from_data(self.base, ast, _generated=True) for ast in self._base_background()]

    def _witness(self):
        """A base model and filling where `Fill_T` holds and some conflict target holds, with its tuple."""
        from ..evaluate import _Evaluator, _Exhausted
        from ..ast import Not
        from ..norms import _bind
        from ..search import find_countermodel
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
        from ..norm_defaults_route import filled_certificate
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
        from ..search import check_countermodel, find_countermodel
        premises, phi = self.soft + self.fill + self.layers + self._gamma(gamma), self._phi(conclusion_ast)
        found = find_countermodel(self.env, premises, phi, max_domain_size=BUDGET["max_domain_size"],
                                  max_models=BUDGET["max_models"], max_evaluations=BUDGET["max_evaluations"])
        if found.status != "Found" or not check_countermodel(self.env, premises, phi, found.model,
                                                             max_evaluations=BUDGET["max_evaluations"]).valid:
            return None
        data = found.model.to_dict()
        model, filling = self._split(data)
        return {"kind": "choice-model", "model": model, "filling": filling, "shown": data}
