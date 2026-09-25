# P0-Lean notes (PLAN-EXPAND2 section 3, Lean half)

Owner: P0-Lean (Opus 5.5), branch `expand/p0-lean`. Spec: [PLAN-EXPAND2.md](../PLAN-EXPAND2.md)
sections 2, 3 and 5; [VISION.md](../VISION.md). The Python half (P0-Py) is built in parallel on
`~/code/ve-p0-py`. This file records what is built, the wire contract P0-Py must match, and every
place where the spec was ambiguous and the conservative reading that was chosen.

## Status (2026-09-25)

| Deliverable (3.10(5) and 3.4-3.6) | State |
|---|---|
| `Layer` (E_in, E_out, premises, restrict, faithful, expands) and the composition theorem | done: `lean/VE/Route/Layer.lean` (`comp_faithful`, `comp_expands`, `compose`) |
| Parametric `CertificateSound` with three compiled instances | done: `lean/VE/Route/Checker.lean` (FOL `tableauValid`, closure, order; each by its existing theorem) |
| DAG order, `Route.dag_acyclic` | done: `lean/VE/Route/Route.lean` (`dependencyOrder`, `dag_acyclic`) |
| Abstract route acceptance theorem | done: `route_acceptance`, `route_base`, `route_entails_iff`, `route_countermodel_restricts`, `route_countermodel_expands` |
| `route_gate` | done: envelope level in `Gate.lean` (`route_gate_envelope`, `classify_sound`, `classify_complete`, `legacy_routes_reject_v02`); runner level in `Run.lean` (`route_gate`, `route_gate_rejects`, `route_rejects_before_checking`) |
| Background on the Lean route (`literals` generator) and end-to-end route theorems | done: `Background.lean` (`literals_sat_iff`, `fol_route_acceptance`, `fol_route_entails_iff`, `fol_route_countermodel`, `closure_route_acceptance`, `order_route_acceptance`) |
| `Claim.label` | done: `lean/VE/ClaimGraph.lean` (defaulted field, part of `DecidableEq`; existing theorem statements textually unchanged) |
| Executable admission, nested kinds, `admit_report_sound` | done: `Admission.lean` (`decodeKind_render`, `parseLabel_render`, `admit_report_sound`, `admit_labels_decoded`, `admit_string_sound`) |
| `route` subcommand | done: `lean/Main.lean` gains one import and one dispatch line; `Run.lean` |
| `METATHEORY.md` lists every new theorem in plain words | done |
| v0, closure, order files and `Main.lean` subcommands unchanged (hash test) | done: `lean/VE/Route/frozen.py` + `frozen-sources.sha256` (54 files); P0-Py should call it from a pytest |
| Evidence that `Layer` is inhabited beyond the identity | done: `Examples.copyLayer` (a defined unary predicate, unique expansion by structure equality) and `twoCopies` (composition) |
| Seed cases for the `elaborated-document` / `invalid-background-model` families | done: `lean/VE/Route/examples/route-cases.json` (33 cases, all verdicts as expected), generator `generate.py` |
| Cross-family review by Astra (3.10(7)) | not done (reviewer task) |
| `ROADMAP.md` freeze announcement (3.10(7)) | not done here: `ROADMAP.md` is shared; the text to paste is below |

Counts: `python3 lean/audit.py`: PASS, 70 source files, 380 named theorems (69 new under
`VE.Route`), allowlist unchanged (`propext`, `Classical.choice`, `Quot.sound`), no `sorry`.

### Freeze announcement (for ROADMAP.md)

> **P0-Lean interfaces frozen (2026-09-25).** `VE.Route.Semantics`, `VE.Route.Layer` (fields as in
> `lean/VE/Route/Layer.lean`), `VE.Route.Layer.comp`/`compose`, `VE.Route.CertificateSound` and
> `VE.Route.Checker`, the route acceptance shape (`checkedPremises`, `BackgroundSound`,
> `BackgroundComplete`, `route_acceptance`, `route_entails_iff`), and `VE.Route.dependencyOrder`
> with `dag_acyclic` are frozen: the three existing checker instances compile and `lean/audit.py`
> passes. W1, W3 and W5 Lean work may start against them; W4's Core instance is a later
> `Checker` instance.

## The frozen Lean interfaces

- `Semantics.{u}`: `Env`, `Formula`, `Model : Type (u+1)`, `Admissible`, `WellFormed` (closed), `Holds`
  (closed). Instances `fol`, `closure`, `order`.
- `Layer L Doc`: the plan's fields plus five coherence obligations (see "Decisions" 1).
- `Layer.comp l₁ l₂ (hE : l₂.E_in = l₁.E_out) (hA : ∀ S, l₂.Admissible_in S ↔ l₁.Admissible_out S)`;
  `Layer.compose l ls (h : Compatible (l :: ls))` folds a chain innermost first; premises concatenate
  (`compose_premises`).
- `CertificateSound L formula E valid := ∀ c ps r, valid c ps r → L.Entails E (ps.map formula) (formula r)`,
  generalising `Graph.CertificateSound` (`graph_certificateSound_iff` is `Iff.rfl`).
- `checkedPremises R background d Γ := background ++ R.premises d ++ Γ`.
- `dependencyOrder : List DepNode → Except String (List String)`.

How a workstream instantiates it: W3 builds a `Layer fol Doc` per definition (or per DAG level) with
`expands` = its `conservative` theorem, W1 a `Layer` with `expands` = `conflictFree_expands` under its
no-conflict hypothesis, W5 a base admissibility (`StringAdmissible` extended by flags) with
`BackgroundSound`/`BackgroundComplete`; then `route_acceptance` gives the end-to-end theorem.
`Examples.copyLayer` is a worked miniature of W3's layer.

## Wire contract of `ve_conformance route` (what P0-Py must match)

Input: a JSON array of cases (same reader as the other subcommands); output: a JSON array of results;
exit 1 if any result has `status: error` (same convention as the existing routes).

**Envelope.** Exactly the fields `language`, `profiles`, `spec_revision`, `vocabulary`;
`language = "ve.core@0.2"`; `spec_revision = "ve-v0.2-expand2-2026-09-25"`; `profiles` a JSON string
array. Checks and diagnostics, in this order (all errors are prefixed `UnsupportedProfile: `):

1. not a string array → `profiles must be a sorted unique array`
2. not strictly increasing (Python `sorted(set(ps)) == ps`) → `profiles must be sorted and unique`
3. first unregistered profile `p` → `Unsupported profile p`; registry: `closure@0`, `data@0`,
   `definitions@0`, `documents@1`, `nary@0`, `norms@0`, `order@0`, `relational-fol@0`, `time@0`
4. no `relational-fol@0` → `Missing profile relational-fol@0`
5. `order@0` with `closure@0` → `Unsupported profile combination closure@0 x order@0`; else with
   `nary@0` → `Unsupported profile combination nary@0 x order@0`
6. `nary@0` without `closure@0` → `Unsupported profile nary@0 without closure@0`
7. family: `order@0` → order; `nary@0` → closure+n-ary; `closure@0` → closure; otherwise FOL
8. revision mismatch → `Unsupported specification revision <r>`; language mismatch → `Unsupported language`

This mirrors the in-progress `ve/profiles.py` on `ve-p0-py` (read 2026-09-25). The Lean runner
rejects closure+n-ary with `UnsupportedProfile: the closure+n-ary checker is gated until W4 stage 1
lands` (the gate itself accepts the family, per 3.10(4)).

**Vocabulary (FOL and closure families).** As v0, plus: a constant may have sort `$string` (a
declared literal); a predicate argument may be `$string`; at most 64 literals (`ResourceLimit: At most
64 declared $string literals`). `$string` is never added to `sorts`, so `forall`/`exists` over it is
rejected at type-check (`ill-typed or unbound formula`). **Order family:** exactly the numbers2 order
vocabulary; `$string` is not available (P0).

**Models.** As v0 tables; `domains` lists `$string` iff at least one literal is declared (Python
`Environment.model_sorts`). After the structural admissibility gate, Background is evaluated in the
model; a false premise gives `status: error`, `error: "InvalidModel(<generator>): the model violates a
background premise"`, and a separate `generator` field (e.g. `"literals"`).

**Background.** Regenerated, never read: generator order `flags`, `definitions`, `literals`,
`profile`. P0: `literals` only, as `["not", ["eq", ["const", a], ["const", b]]]` for each pair
`a < b` of the **sorted** literal names, in lexicographic pair order (Python
`itertools.combinations(sorted(lits), 2)`).

**Identity.** `identity_version = "v0.2:" + ",".join(profiles)`; environment id
`sha256("ve-environment-<identity_version>\n" + canonical(environment))`; meaning id
`sha256("ve-meaning-<identity_version>\n" + canonical({"environment_id", "ast"}))` (as in
`ve/environment.py` on `ve-p0-py`). Report id: domain `ve-report-<identity_version>\n` over
`{"root", "assumptions"}` of the admitted report.

**Case kinds** (`kind` absent = `evaluate`):

| kind | fields | ok result |
|---|---|---|
| `evaluate` | `model`, `ast` (nonempty list) | `values` |
| `countermodel` | `model`, `premises`, `conclusion` | `refutes` (premises true, conclusion false, model valid incl. Background) |
| `certificate` | `premises`, `conclusion`, `certificate` | `valid`, `background` (count) |
| `dependency-order` | `nodes: [{"name", "mentions"}]` | `order` |
| `admission` (FOL only) | `document` | `admitted`, `report`, `report_id`, `kinds` |

The certificate's checked premise list is **Background ++ premises**; its `premise_meaning_ids` bind
that whole list (Background ASTs as above), `conclusion_meaning_id` the conclusion, and
`environment_id` the v0.2 environment id. A certificate bound only to the case's premises is
rejected as stale. Certificate formats are unchanged (v0 tableau, closure, order).

**Dependency order.** Edges run from a node to each mentioned symbol that is itself a node; other
mentions are ignored. Duplicate node names → `DuplicateDeclaration: dependency node <n>` (first
duplicated name in list order). Algorithm (must be replicated exactly): repeatedly place the
lexicographically smallest unplaced node all of whose node-dependencies are placed; if none is
ready, fail with `DependencyCycle: ` + `", ".join(sorted(unplaced names))`. The order is then
re-verified. The same function serves the norm precedence graph (rule names as nodes).

**Admission document.** Fields `units`, `graph` (required), `lemmas`, `open_terms`, `reading_sets`,
`narrowings` (optional).

- unit: `{"id", "span": [start, stop], "kind", "content"?}`; ids unique tokens; `start ≤ stop`;
  spans sorted and non-overlapping (`stop_i ≤ start_{i+1}`); `content` a closed typed AST.
- kind: `"asserted" | "norm" | "definition" | "question" | "instruction" | "example" | "exposition" |
  "analogy" | "explanation" | "meta"`, `["attributed", agent, act, kind]` (act ∈ says, promised,
  believes, intends, expects, denies), `["hedged", modality, kind]` (could, likely, generally,
  typically, effectively), `["causal", relation, kind, kind]` (because, in order to, prevents),
  `["unformalised", reason]`; depth ≤ 16. The result's `kinds` renders each unit's kind back; it is
  byte-identical to the input (theorem `decodeKind_render`).
- lemma: `{"name": "<bundle>/<lemma>", "conclusion", "leaves": [{"ast", "label"}]}`; leaves are the
  transitive undischarged leaves (a `cite:` label there is rejected).
- reading set: `{"id", "version": n, "readings": [ast, ...]}` (1-64 readings).
- graph: `{"root", "nodes": [{"name", "ast", "label"?, "unit"?, "premises"?, "certificate"?}]}`;
  premises and certificate come together; each certificate binds the premise nodes' ASTs and the
  node's AST (v0.2 meaning ids); at most 1000 nodes; nodes in topological order (unchanged
  `Graph.check`).
- tokens (names inside labels and kinds): nonempty, ≤ 64 bytes, `[A-Za-z0-9_.-]`.

**Labels** (only canonical strings parse): `asserted` (default; **omitted** on the wire, an explicit
`"label": "asserted"` is rejected as non-canonical), `bridge:accepts(<agent>,<unit>)`,
`background:<flags|definitions|literals|profile>`, `cite:<bundle>/<lemma>`, `open:<term>`,
`readings:<set>@<version>:<choice|all>` (decimal, no leading zeros), `narrowing:<id>`.

**Admission rules.** A deduction node has label `asserted`; if it names a unit, that unit is
`asserted` with exactly the node's formula. A leaf, by label: `asserted` names an asserted unit with
exactly its formula; `bridge:accepts(a,u)` names (or omits) unit `u`, `u` is quoted (root kind
attributed or hedged) with exactly the leaf's formula, and for an attributed `u` the agent `a` is
the attributed agent; `background:g` has no unit and its formula is a regenerated Background premise
of generator `g`; `cite:b/l` has no unit and its formula is lemma `b/l`'s conclusion; `open:t` names
a declared open term; `readings:s@v:i` is reading `i` of set `s` version `v` (`all`: the right-nested
disjunction of the readings); `narrowing:n` names a declared narrowing. After `Graph.checkTableau`:
every leaf of every cited lemma appears among the report's assumptions with the same formula and
label (so the citing step lists them as premises), and no two assumptions name the same reading set
with different versions or different concrete choices (`all` is compatible with any choice).

**Admission diagnostics.** First failing node in graph order:
`AdmissionError: quoted content of unit <u> is used without a bridge leaf` when the node names a
quoted unit and is not a bridge leaf naming it; `AdmissionError: invalid label <l>`;
otherwise `AdmissionError: node <name> is not admitted under label <l>`. Report level:
`AdmissionError: a cited lemma's leaves are missing from the report`,
`AdmissionError: incompatible reading choices`. Graph failure:
`graph rejected: cycle, duplicate name, dangling premise, ill-typed claim or invalid certificate`.

**Report.** `{"root": claim, "assumptions": [claim]}`, claim = `{"name", "ast", "label"?}` with the
default label omitted. Stripping a label from a leaf changes admission (the leaf becomes an asserted
leaf, which must name an asserted unit) and so changes the report and `report_id`.

## Decisions on ambiguous points (conservative readings, flagged)

1. **Layer coherence fields.** The plan lists `E_in, E_out, premises, Admissible_in/out, restrict,
   Intended, faithful, expands`. Composition and the acceptance theorem also need: `extends_env`
   (E_in ⊆ E_out on well-formed formulas), `premises_wellFormed`, `admissible_out` (output
   admissibility implies structural admissibility, so the checker's `Entails` applies),
   `restrict_admissible` and `restrict_holds` ("forget the new symbols" does not change old truths).
   All are obligations the plan's prose already implies; adding them only strengthens the contract.
2. **Structures are not indexed by environments** (as in the existing code): `Structure E_in` is
   read as "a model satisfying `Admissible_in`". Unique expansion is equality of structures
   (`Unique`), shown workable by `Examples.copyLayer`.
3. **Where Background goes.** The certificate checks and binds `Background ++ premises` (the plan's
   `Entails E_out (Background ++ premises Γ)`); the alternative (binding only Γ and prepending
   silently) would let a certificate be replayed against a different Background.
4. **Background order**: sorted literals, pairs in lexicographic order.
5. **`$string`** is never quantifiable and never in `sorts`; model tables list it as a domain iff a
   literal is declared; `$string` is unavailable on `order@0` in P0.
6. **Explicit default label** is rejected (one canonical wire form per claim, so one hash).
7. **Reading choices**: versions of one set must agree; `all` is compatible with any concrete choice
   (a result under all readings holds under each). A stricter reading (reject `all` with a concrete
   choice) is a one-line change in `compatible` if the reviewers prefer it.
8. **Bridge agent**: for an attributed unit the bridge's agent must be the attributed agent; for a
   hedged unit (no agent) the agent is recorded as given.
9. **Citation leaves are "present"** means present in the report (the citing step takes them as
   premises), not merely present somewhere in the graph.
10. **Admission is FOL-only in P0**; closure/order admission is deferred (their graphs need a
    parametric claim type, which would change existing theorem statements). The closure and order
    families run evaluate/countermodel/certificate.
11. **`route_gate` placement**: the envelope gate is in `Gate.lean`; the runner-level `route_gate`
    is in `Run.lean`, because the runner imports `Gate.lean`.
12. **Case kind name `admission`** (not `admit`): `lean/audit.py` forbids the token `admit` anywhere in
    Lean source, including strings.
13. **Span partition**: Lean checks sorted, non-overlapping spans; 100% source coverage needs the
    source text and stays with W2's Python check.
14. **Edits outside `lean/VE/Route/*`**: `VE/GraphChecks.lean` and `VE/TableauChecks.lean` switch
    their `Claim` literals to structure-instance syntax (anonymous constructors need all three
    fields once the label exists); `VE/Audit.lean` and `VE.lean` gain imports and audit lines;
    `lean/axioms.txt` is regenerated. No theorem statement outside `VE/Route/*` changed.

## Soundness-relevant statements needing statement review

- `Layer` (every field) and the acceptance shape `route_acceptance` / `route_entails_iff`, especially
  the hypotheses `BackgroundSound` and `BackgroundComplete`.
- `Background.LiteralsDistinct` / `StringAdmissible`: the stage-1 meaning of `$string` (W5 owns the
  final wording; P0 ships it for the literal generator).
- `Admission.LeafAdmitted`, `NodeAdmitted`, `CitationsClosed`, `compatible`: the admission rules.
- `Gate.AllowedFamily`: the four families.
- `Graph.Claim.label`: now part of `Claim` equality, which changes the meaning of every claim-graph
  theorem to also track labels (statements unchanged).

## Tests

- `lake build` (includes `VE/Route/Checks.lean`: guards for the gate, DAG, labels, kinds, literals).
- `python3 lean/audit.py` (380 theorems).
- `python3 lean/VE/Route/frozen.py` (frozen sources and `Main.lean` subcommands).
- `uv run python lean/VE/Route/examples/generate.py`, then
  `lean/.lake/build/bin/ve_conformance route lean/VE/Route/examples/route-cases.json` and compare with
  each case's `expected` (33/33).
- For P0-Py: the `invalid-background-model` and `elaborated-document` families in `conformance/` can
  start from `route-cases.json`; the Lean verdicts are the `expected` objects.
