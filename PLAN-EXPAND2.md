> Status: PLAN v3 (2026-09-25), **adopted and binding**. v2 was reviewed by GPT-6 Astra xhigh (REVISE) and Claude
> Fable 5.1 xhigh (ADOPT WITH CHANGES); the two then converged in two rounds on one numbered change list and the
> verdict **BUILD, P0 first** (`~/code/manage-agents/debates/expand2-v2/`: `astra.md` round 1 items 1-12 as amended
> by round 2, `fable.md` round 2; `result.txt`: CONVERGED after round 2). v3 applies exactly that list; section 8
> records each change; section 9 is binding. Supersedes v2 (commit 3606cfd) and v1 (f901398). The goal of record is
> [VISION.md](VISION.md). Numbers round 2 (integer quantifiers, Rust order@0, grammar export, Lean order parser)
> runs separately on `codex/numbers2` and is not repeated here. Round 1 is [PLAN-EXPAND](PLAN-EXPAND.md); status
> lives in ROADMAP.md.

# Language expansion, round 2 (v3): eight workstreams

## 0. Change log

| Date | Change |
|---|---|
| 2026-09-25 | v1 (f901398): seven workstreams, for review. |
| 2026-09-25 | v2 (3606cfd). Reordered per the vision reviews: documents with 100% span accounting, open-term schema and non-assertive kinds first; then definitions and citation; n-ary atoms; narrowed norms; numbers continue; unified checker stage 2 and the English Lean proof deferred. Norm semantics rewritten: Catala applicability, stratified regulated predicates, no precedence cycles, one completion per dual pair, `required → permitted`, three-valued conflict status. P0 background premises, composed `ve.core@0.2` route, dispatch sites, claim labels, vacuity. Strings restricted. Reading sets and narrowings. W8 authoring. Ownership matrix. Response table. |
| 2026-09-25 | v3 (this file), the converged Astra + Fable change list applied, nothing else. **Debate item 1 (P0):** the `Layer` contract now carries source and target environments, model restriction and expansion maps and compositional faithfulness (premise concatenation kept); the checker is parametric over syntax and semantics with four allowed families (FOL, closure, closure+n-ary, order; other mixes rejected); the interface freezes after the existing v0, closure and order instances compile; W4's Core instance is gated later. **Item 2:** one dependency DAG over definitions ∪ regulated predicates (definitions may sit above norms); both reversed-order statements deleted; precedence is a DAG; stable rule names, numbers display-only. **Item 3:** executable Lean document/graph decoding and admission for the new route with an end-to-end report theorem (nested kinds, bridge leaves, transitive provenance); "structurally impossible" dropped; citation binds reading choices and narrowings; a general legacy graph decoder deferred (section 7). **Item 4:** `$string` literals declared in the identity-bound vocabulary, `Background(env)` only; Rust decodes declarations, regenerates Background and checks elaborated documents (new conformance family); Python/Lean differential elaboration tests added as W3(7) and W5(7). **Item 5 (W1):** completed outcomes `O_p` from selection disjunctions `P_p`/`N_p`; conflict := `P_p ∧ N_p` or `O_required ∧ ¬O_permitted` after recursive substitution of lower outcomes; theorem: no conflict ⇔ unique admissible expansion (profile premises included), quantified over base structures; both default counterexamples added to W1(5). **Item 6:** small-model claim restated as a proof-gated fragment theorem `conflict_smallModel` (quantifier-free after expansion; universal, function-free, closure-free, `$int`-free admissibility theory; `total` excluded; per-sort bound `max(1, constants + witness variables)`); completeness enabled only after the Lean proof; the total-functional `¬r(x,x)` regression must report CONFLICT with a two-element witness, never CONFLICT-FREE. **Item 7 (W2, VISION §3):** ALL by disjunction and the shared-model NONE only for assertion readings under identical backgrounds; other kinds enumerate complete choices up to 64 or UNKNOWN; nested kinds; labels carry the choice; citations require compatible choices. **Item 8 (P0/W7):** prefix disjointness replaced by longest-match registration plus complete all-derivations checking on every accepted English input; ambiguity rejects; budget exhaustion rejects with a diagnostic naming the budget; corpus stays regression evidence. **Item 9 (W6):** integer-time n-ary examples deferred to W4 stage 2; FRET re-rates with user-sort time; units are identity-bound tags on signature slots and statement occurrences/binders with Lean admission before integer erasure; conversions deferred. **Item 10:** distinctness nested under each binder; caps at-least ≤ 8, exactly/at-most ≤ 7, both applied to "n of m"; row 8 stays REIFIED and says so. **Item 11:** numbers2 merges first and is in the matrix; Cedar acceptance is a joint W1+W5 gate; `ve/adapters/` is a package; `p(a,a,b)` valid; `UnsupportedProfile` dispatch and checker-build hash fixed. **Item 12:** Cedar evidence pinned at `1999ea2` (115 decisions, 11 scenarios); math baseline 17/19 today, target 18/19; rows 7b and 22b both stay NO for the same reason; 85,000 round trips versus 12,750 Earley texts; "without it" removed. P0 (section 3) rewritten as a hand-off spec: files, interfaces, tests, acceptance. |

## 1. Aim

Make VE cover what policies, constitutions, papers and news actually say, so that a document has a checked spine
and an explicit residual: every source span is one unit with a declared kind; every commitment is checked, or rests
on named open terms, named assumptions and admitted readings; nothing is silently dropped. The checker stays small
and Lean-proved; the English stays readable; `ve assist` and `ve propose` author every construct.

Evidence for what is missing (`usecases/*/GAPS.md`, `experiments/E0/SURVEY.md`, `paper/sources/e0-second-rater.md`):

| Gap | Where it bites |
|---|---|
| No document format; coverage tables are hand-made per use case; "nothing dropped" unmeasured | every pilot |
| Obligation, prohibition, permission, exceptions, priorities | 14th s1 (3/4 clauses), Claude constitution (about 10/21 rows), Cedar permit/forbid/default deny, Gatekeeper deny rules |
| Attribution, hedges, causal and evaluative statements, figurative and meta prose | news 11/26 NO, constitution 12/23 NO, debate (every claim) |
| Definitions and lemma citation | constitution 5/21, math paper T7mono, every "term of art" |
| Arity above two | FOLIO: 216 of 3,235 sentence pairs contain an arity>2 atom; time-indexed relations; math |
| Attributes, strings, sets | Cedar (second rater, 30-item sample: 0 DIRECT, 13 REIFIED, 17 OPAQUE; closure is the main blocker, attributes second), Gatekeeper 20 string items |
| Dates, scaled decimals, counting | news 7 numeric rows and 1 counting row, FRET 65 temporal, Art. I s7 ("ten days, Sundays excepted", "two thirds") |
| Ambiguous source sentences resolved silently by the translator | every translated pilot (VISION.md section 3) |
| English surface unproved and its extension discipline unchecked | trust of the surface |

## 2. Design rules (binding for every workstream)

1. **Three trust tiers.** (a) *Checker*: Lean tableau checkers, decoders, identity. Only W4 (and numbers2) change
   it. (b) *Statement layer*: everything that decides what a signed-off sentence means: elaborations, generated
   premises, definitions, unit schema, reading-set rules. Each piece is a Lean-proved elaboration with a
   faithfulness theorem or a reviewed schema; every theorem statement gets a statement review. (c) *Surface and
   tools*: English, `ve assist`, `ve propose`, Rust, search: untrusted, differentially tested.
2. **Elaborate, do not extend the logic** (VISION.md section 6 and its converged rule). New constructs elaborate
   deterministically into the checked language through one route of typed layers (section 3.4): each layer
   extends an environment `E_in → E_out`, generates premises that are concatenated, and carries a Lean faithfulness
   theorem stated as a unique-expansion (model correspondence) result relative to the admissible structures of the
   layer below; the checker is a parameter of the route. The certificate binds the elaborated premises to the hash
   of what the author saw.
3. **Identity freeze.** Existing envelopes (`ve.core@0`, `ve.core@0.1` closure, order) keep every identity,
   canonical byte, certificate, wire hash and theorem statement. New constructs live in profiles under
   `ve.core@0.2` with a sorted `profiles` list; the identity domain is `ve-<kind>-v0.2:<sorted profiles>`. Each
   new route gets its own gate theorem; the existing gates are unchanged.
4. **Sugar is input-only for strict text.** The canonical strict printer never changes for existing ASTs. Sugar
   (`iff`, "every x that is P", "at least 3", dates, decimals) is accepted on input and expanded before identity.
   The English and fluent views show sugar only when the environment's profile list enables that profile, so
   every existing environment renders byte-identically and `conformance/english-surface-report.json` does not move.
5. **Background premises invalidate models.** Every premise generated from declarations (flags, definitions,
   `$string` literal distinctness, fixed profile premises) is both an implicit premise at every entailment site
   and a validity condition on every finite model at every evaluation, search, equivalence, composition and
   conformance site (section 3.1). Lean and Rust regenerate them from the decoded declarations; a list supplied on
   the wire is never trusted.
6. **100% span accounting.** A document's units partition its source; `unformalised(reason)` is a unit kind, never
   an omission. Coverage sums to the source length.
7. **Three-valued results and vacuity.** Every undecidable check (entailment, norm conflict, premise consistency)
   reports YES with a certificate, NO with a checked witness, or UNKNOWN with the exhausted budget. Every document
   check reports whether its premise set has a satisfying finite model (model id), is proved inconsistent
   (certificate; dependent certificates are flagged `vacuous`), or UNKNOWN.
8. **Every construct is authorable.** A construct is offered by `ve assist` only after passing its W8 fidelity
   gate; until then it is "strict only" and listed as such.
9. **Lean wording.** `lean/audit.py:12` scans raw source text, so Lean files and comments say "profile premises"
   or "background premises" and never use the forbidden tokens, even in prose.
10. **Gates.** Spec section reviewed by Astra + Fable xhigh before build; cross-family code review before merge;
    full suite green; `lean/audit.py` allowlist unchanged (`propext`, `Classical.choice`, `Quot.sound`); no
    `sorry`; identity and parser fixtures byte-identical; an end-to-end Lean acceptance theorem for every enabled
    route; each new theorem listed in plain words in the profile's `.md`; the ownership matrix (section 5)
    respected; one integration agent merges. Unambiguity of accepted English is checked per input (section 3.2),
    never inferred from a corpus.

## 3. P0: contracts and extension points (hand-off spec; Python 3 days GPT-6 Sol, Lean 3 days Opus 5.5)

Zero behaviour change for existing artefacts: every fixture under `conformance/`, `tests/`, `usecases/` and
`docs/prover-fair/` replays byte-identically, and `conformance/english-surface-report.json` does not move. P0
publishes the frozen interfaces (3.8) on day one so the Lean workstreams can start against them. Two agents:
**P0-Py** (Sol) owns everything under `ve/`, `rust/`, `conformance/`, `tests/`; **P0-Lean** (Opus 5.5) owns
`lean/VE/Route/*`, `lean/VE/ClaimGraph.lean`, `lean/Main.lean`, `lean/METATHEORY.md`. numbers2 merges before
P0-Py touches `ve/entailment.py`, `ve/grammar.py` or `rust/`; P0-Py rebases on it (section 5).

### 3.1 Background premises and model validity

```text
Background(env) := flag premises (W5: functional / total)            from predicate declarations
               ++ definition biconditionals (W3)                   from `defined` vocabulary entries
               ++ literal distinctness (W5: ¬(l1 = l2) per pair)   from the `$string` constants declared in env
               ++ fixed profile premises (W1: ∀a. required(a) → permitted(a))   when `norms@0` is enabled
depends on env only; bound into environment_id; at most 64 declared $string literals, else ResourceLimit
model validity: a FiniteModel is valid only if it satisfies Background: functional/total tables checked
                structurally, defined predicates computed from their bodies (a supplied table is rejected),
                two literals never share a denotation; otherwise InvalidModel, never a truth value
```

**Files (P0-Py).** New `ve/background.py`: `background(env) -> tuple[Premise, ...]` where
`Premise = (formula: Formula, generator: str)` and `generator ∈ {"flags", "definitions", "literals", "profile"}`;
`validate_background(env, model) -> None | raises InvalidModel(generator, detail)`; a per-generator hook table
that W3, W5 and W1 fill (P0 ships the table with the `literals` generator implemented for declared `$string`
constants and the other three generators returning `()` until their workstreams land). `ve/errors.py` gains
`InvalidModel` if absent (it exists: `ve/argument.py:18` imports it) with a `generator` attribute.

**Sites**, each with a test asserting it consults `background` and reports `InvalidModel` rather than a truth
value: `ve/evaluate.py` (`_validate_model`, line 163), `ve/search.py` (`check_countermodel` 108, the
distinguishing-model search, `_subsets`), `ve/equivalence.py`, `ve/argument.py` (every edge; background leaves
appear in the report with label `background:<generator>`; `ContradictoryPremises` at 519 feeds the vacuity
report), `ve/entailment.py` (`prove_entailment` 515, `check_entailment_certificate` 620), `ve/check.py`; the Lean
route (3.4); Rust `eval.rs`, `search.rs`, `model.rs` (3.7).

**Tests.** `tests/test_background.py`: for each site, an environment whose Background is non-empty (a declared
pair of `$string` literals) and a model aliasing them is rejected with `InvalidModel("literals")` at that site;
an environment with empty Background produces byte-identical results to today (fixture replay);
`environment_id` changes when a `$string` constant is added and is unchanged for every existing fixture.
`conformance/generate.py` gains the case family `invalid-background-model` (aliasing literals, a partial `total`
table, a supplied table for a defined predicate), expected rejected by Python, Lean and Rust; the second and third
cases are generated now and asserted once W5 and W3 land (marked `pending:<workstream>` in the family file).

### 3.2 Surface registry: longest-match registration and per-input unambiguity

Each feature registers one record in `ve/surface/registry.py` (new package `ve/surface/`):

```text
SurfaceRecord := wire_tag, strict_form, english_keywords (statement-initial), fluent_form, grammar_production,
                 evaluator_hook, traversal_hooks (map_free, predicates, substitute), witness_renderer (W8)
register(record): refuses a wire tag already taken; orders English keywords by longest match (a longer keyword
                  that begins with a shorter one is tried first, so `both of the following hold:` precedes `both `,
                  `if the following holds:` precedes `if `); duplicates rejected
KEYWORDS: the statement-initial keyword list extracted from ve/english.py:773-849 into the registry, with a test
          that every statement-initial `take('...')` in english.py is listed and dispatched in longest-match order
```

**Per-input unambiguity (mandatory).** Every English input accepted on any route runs the all-derivations
parser (the Lark Earley grammar of `docs/english-surface.md`, exported from the environment's profiles) before the
AST is admitted: more than one derivation rejects the input with a diagnostic showing both derivations; exhaustion
of the derivation budget (`MAX_NODES`, `ve/limits.py`, plus the Earley time limit) rejects the input with a diagnostic naming the budget, and
the author falls back to strict text. A sentence whose unambiguity is unverified is never admitted. The corpus
(`conformance/english_mixed.py`, W7) remains regression evidence, never the guarantee.

**Dispatch sites** that read the registry instead of hard-coding constructors: `ve/parser.py`, `ve/printer.py`,
`ve/fluent.py`, `ve/english.py` (prefix parsing at 773-849 and rendering), `ve/grammar.py`, `ve/evaluate.py:74-160`,
`ve/fol.py`, `ve/search.py` (`_used_predicates` 129), `ve/closure.py:78` (`map_free`), `ve/argument.py:587`
(`_predicates`), `ve/wire.py` and `ve/ast.py` (tags), `tests/explicit_inverse.py`, `tests/fluent_inverse.py`,
`conformance/generate.py`, `rust/ve-core/src/{ast,wire,surface}.rs`.

**Tests.** `tests/test_surface_registry.py`: keyword-list completeness; longest-match order (the four pairs above
parse as today); a registration whose keyword equals an existing one is refused; a registration of `both x` after
`both ` is dispatched after `both of the following hold:`. `tests/test_english_unambiguity.py`: every English
fixture in the tree (the 85,000 round-trip pairs are regenerated, the 12,750 Earley texts replayed) is accepted
with exactly one derivation; a constructed two-derivation input is rejected naming both; an input exceeding the
budget is rejected naming the budget and never yields an AST.

### 3.3 `ve.core@0.2` envelope and profile registry

Sorted unique `profiles`; an ordered profile registry (`ve/profiles.py`, new) naming each profile's
statement-layer generator, its layer and its checker family; unknown profile or unsupported combination →
`UnsupportedProfile` with the offending profile named (today `ve.core@0.2` fails as a generic `InvalidInput` at
`ve/environment.py:103`, which P0 fixes); identity domain per rule 3. Allowed checker families: FOL (`tableauValid`),
closure, closure+n-ary (W4's Core route, gated until it lands), order; any other mix is rejected with
`UnsupportedProfile` naming the pair. W4 owns the checker route; other workstreams register statement-layer
profiles (`documents@1`, `definitions@0`, `norms@0`, `data@0`, `time@0`, `nary@0`). `ve/argument.py:32-33`
`_checker_build` includes `order`, `background`, `profiles`, `surface/registry` and every new semantic module
(test: the hash changes when any listed module changes; the list is asserted against the `ve/` directory).
Rust mirrors the envelope check (`rust/ve-core/src/environment.rs:102-115`) with the same diagnostic.

**Tests.** `tests/test_profiles.py`: sorted-unique enforcement; `UnsupportedProfile` for an unknown profile, for
`order@0` with `nary@0`, and for `closure@0` with `order@0`; identity domain string; Rust parity on the same
envelopes through `tests/test_rust_conformance.py`.

### 3.4 The Lean route (`lean/VE/Route/`): typed, environment-extending layers

```text
structure Layer where
  E_in  E_out   : Environment                     -- the layer extends the vocabulary (definitions, regulated
                                                  --   predicates, $string constants); E_in ⊆ E_out
  premises      : Doc → List Formula              -- executable, over E_out; mirrored in Python; concatenated on the route
  Admissible_in : Structure E_in  → Prop           -- structures admissible for the layer below
  Admissible_out: Structure E_out → Prop
  restrict      : Structure E_out → Structure E_in  -- forget the new symbols
  Intended      : Doc → Structure E_out → Prop     -- the reviewed statement of meaning
  faithful      : ∀ d S, Admissible_out S → ((∀ a ∈ premises d, a.denote S []) ↔ Intended d S)
  expands       : ∀ d S₀, Admissible_in S₀ → ∃! S, restrict S = S₀ ∧ Admissible_out S ∧ ∀ a ∈ premises d, a.denote S []
                  -- unique expansion: model correspondence behind proof and countermodel results;
                  -- `Definitions.conservative` (W3) and `Norms.conflictFree_expands` (W1) are instances
route  := layers ordered by one dependency DAG over definitions ∪ regulated predicates (3.5); premises of all
          layers concatenated after Background; a cycle rejects the document
checker := any (Syntax, Semantics, valid) with `CertificateSound Syntax Semantics E valid`: the abstract contract
          generalises lean/VE/ClaimGraph.lean:41 over the formula type and its denotation, so today's FOL, closure
          and order checkers are instances without rewriting them; W4's Core checker is a later instance
acceptance theorem per enabled route: accepted certificate ⇒ Entails E_out (Background ++ premises Γ) (premises φ)
          ⇒ (expands, layer by layer, innermost first) the document-level statement holds in every intended
          structure of E_in satisfying the premises, and every countermodel restricts to one
```

**Files (P0-Lean).** `lean/VE/Route/Layer.lean` (the structure, composition of two layers, the composition
theorem over abstract layers), `lean/VE/Route/Checker.lean` (parametric `CertificateSound`, instances for
`tableauValid`, the closure checker and the order checker, each proved by the existing theorem), `lean/VE/Route/
Route.lean` (DAG ordering, concatenation, the abstract acceptance theorem), `lean/VE/Route/Admission.lean` (3.6),
`lean/VE/Route/Gate.lean` (`route_gate`: an envelope whose profiles are not an allowed family is rejected before
any checking, in the style of `lean/VE/Order/ProfileGate.lean:218-264`). `lean/Main.lean` gains one subcommand
`route` that reads the envelope's profiles; the v0, closure and order files and the `check-certificate` and
`order` subcommands are untouched (hash test). Each layer's `Intended` gets a statement review (rule 1b).

**Freeze.** The `Layer` and parametric `CertificateSound` signatures freeze when the three existing instances
compile and `lean/audit.py` passes; that is P0-Lean's day-three deliverable and the start signal for W1, W3, W5
Lean work. W4's Core instance is gated on its own theorems and does not hold P0.

### 3.5 One dependency DAG over definitions and regulated predicates

Definitions (W3) and regulated predicates (W1) share one declared order: a node is a defined predicate or a
regulated predicate; an edge runs from a symbol to every symbol mentioned in its body or guard (after expansion).
The graph must be acyclic; definitions may sit above norms (`violation(a) := required(a) ∧ ¬done(a)`) and below
them (definitions used in guards); a p-norm's guard may mention regulated predicates only strictly below p. The
route orders layers by this DAG. Precedence between norms is also a DAG (a norm may take precedence over several
rules); identities use stable rule names (`rule:<name>`), and rule numbers are display-only. Cycles in either
graph are rejected in Python (`ve/background.py:dependency_order`) and Lean (`Route.dag_acyclic`) with the same
diagnostic. There is no fixed `data ∘ definitions ∘ norms` order.

**Tests.** A definition above a norm and a norm whose guard uses a definition are both accepted; a
definition mentioning a regulated predicate of its own stratum is rejected; a cycle through a definition and a
norm is rejected with the same diagnostic from Python and Lean (differential test over 200 generated graphs).

### 3.6 Claim labels and executable admission

`Graph.Claim` gains `label : String` (`asserted`, `bridge:accepts(<agent>,<unit>)`, `background:<generator>`,
`cite:<bundle>/<lemma>`, `open:<term>`, `readings:<set>@<version>:<choice|all>`, `narrowing:<id>`), part of
`DecidableEq`, carried through `Report.assumptions` and `Unfolds` unchanged, and part of the wire hash. The wire
omits the default label so every existing graph artefact hashes identically (test). Python `check_argument`
mirrors it. Bridge admission is enforced twice: by Python and by the executable Lean admission of the new route
(`lean/VE/Route/Admission.lean`): a JSON document on `ve.core@0.2` is decoded to units, nested kind trees
(`attributed(agent, act, kind)`, `hedged(modality, kind)`, `causal(kind, kind)`), bridge leaves and a claim graph;
admission checks that a node naming a quoted unit is a bridge leaf whose label names the unit (an independent formula-equal leaf retains its own provenance), that every cited
lemma's transitive leaves are present with their labels, and that reading choices along a citation are compatible
(3.6 of W2); the end-to-end theorem `admit_report_sound` states that an admitted document's report is a
`SoundReport` whose assumption list carries exactly the decoded labels. A general-purpose decoder for legacy graph
artefacts is deferred (section 7); Python replay remains their path. Stripping a label changes the report and the
hash. `lean/METATHEORY.md` is updated; existing theorem names and meanings are unchanged (they quantify over
`Claim`).

**Tests.** Wire-hash identity for every existing graph fixture; a graph referencing quoted content without a
bridge leaf is rejected by Python and by `route` with the same diagnostic; stripping a bridge or background label
changes the report and the hash; a nested kind tree of depth 3 decodes and renders back byte-identically;
`admit_report_sound` audited.

### 3.7 Rust scope

Rust checks elaborated documents: it decodes the `ve.core@0.2` envelope and declarations (flags, `defined`
entries, `$string` constants), regenerates `Background` from them (never from the wire), validates models against
it, and evaluates and searches over the elaborated premises. Rust never elaborates English or norms. New
conformance family `elaborated-document`: Python, Lean and Rust verdicts (entailment, countermodel, invalid model,
`UnsupportedProfile`) must agree on every case; P0 ships the family with `$string` literal cases and the envelope
cases; W3, W4 and W5 add theirs. Rust work in P0 starts after numbers2's Rust `order@0` merges.
The order route also checks supplied countermodels against the same declared
model and formulas; Rust still does not replay order proof certificates.

### 3.8 Vacuity report

`ve check`, `ve document check`, `check_argument` and assist `status` report
`premises: model <id> | INCONSISTENT(<certificate>) | UNKNOWN(<budget>)`; a certificate whose premise set is
proved inconsistent is reported `vacuous` and never counted as coverage. Test: a premise set with a contradiction
reports INCONSISTENT and its dependent certificates `vacuous`; the existing fixtures report a model id.

### 3.9 Frozen interfaces (published on P0 day one)

Certificate premise order is **Background(env) ++ composed layer premises in
composition order ++ Γ**. Python's current layer segment is empty; every new
generator must choose either the fixed Background hook order (flags,
definitions, literals, profile) or a layer segment, and both routes must bind
the identical ordered list before issuing a certificate. The report identity
payload is `{"environment_id", "document", "report"}` under the v0.2 report
domain. The full validated document binds unit kinds, reading sets and graph
provenance even when the displayed report is unchanged.

| Interface | Producer | Consumers |
|---|---|---|
| `background(env)`, `validate_background`, generator hook table, `InvalidModel(generator)` | P0-Py | W3, W5, W1 (generators); every site; Rust |
| `SurfaceRecord`, `register`, longest-match `KEYWORDS`, per-input all-derivations check | P0-Py | W1, W2, W3, W5, W6, W7, W8 |
| Profile registry, `ve.core@0.2` envelope, allowed checker families | P0-Py | all |
| Lean `Layer` (E_in, E_out, premises, restrict, faithful, expands), parametric `CertificateSound`, route acceptance theorem shape, DAG order | P0-Lean | W1, W3, W5, W4 |
| `Claim.label`, admission decoder, report format | P0 | W2, W3, W8 |
| Unit schema `ve-document@1` (nested kinds) | W2, by P0 + 2 days | W1, W3, W8 |
| n-ary wire form `["atom", p, [terms]]`, `k ≤ 6`, repeated arguments allowed | W4, by P0 day one | W5, W6, Rust |

### 3.10 P0 acceptance

1. Every existing fixture, identity, certificate, wire hash and `conformance/english-surface-report.json`
   byte-identical; `lean/audit.py` allowlist unchanged; no `sorry`; the v0, closure and order Lean files and
   `Main.lean` subcommands unchanged (hash test).
2. `Background` consulted at every site in 3.1 with `InvalidModel` tests; the `invalid-background-model` and
   `elaborated-document` conformance families run in Python, Lean and Rust with zero disagreements on the shipped
   cases.
3. Registry: keyword list complete against `english.py`; longest-match order test; per-input all-derivations check
   on all routes with all existing English inputs accepted and the two rejection diagnostics tested.
4. `ve.core@0.2`: `UnsupportedProfile` names the profile or pair; the four allowed families accepted; the checker
   build hash covers every module; Rust parity.
5. Lean: `Layer`, parametric `CertificateSound` with three compiled instances, composition theorem, DAG order,
   `route_gate`, `admit_report_sound` with the label field and nested kinds; `METATHEORY.md` lists each in plain
   words; the `route` subcommand runs the shipped elaborated-document cases.
6. Vacuity report present in the four commands.
7. Cross-family review of P0-Py by Fable, of P0-Lean by Astra; interfaces in 3.9 announced frozen in ROADMAP.md.

## 4. Workstreams, in build order

### W2. Documents: format, 100% span accounting, content kinds, open terms, reading sets, pilots

**Goal.** Turn a whole document into a checked spine with an explicit residual, measured after every merge.

**Deliverables.** Format `ve-document@1` (`.ve.md`: JSON front matter with environment, units and open terms;
fenced `ve` blocks; the prose between them is the source and is spanned). Unit schema below. Open-term schema.
Reading sets and narrowings. CLI `ve document check|render|coverage|readings`. English rendering of units
("According to the Fed's statement, ..."; "Rule 3. ..."; "This sentence could mean (a) ... or (b) ..."). Coverage
dashboard `tools/coverage_dashboard.py` writing the ROADMAP table. Pilots: US Constitution Art. I s7 (clauses 1-3),
one norm-heavy Claude-constitution section, the Reuters Fed article; each as `usecases/<doc>/commitments.ve.md`
with `coverage.json`, baseline now with today's language, re-measured after each merge, second rater on labels,
blind cross-family fidelity audit.

**Unit schema.**

```text
unit := span [start, end) + kind + meaning ∈ {specified, contextual(context), open(terms), unformalised(reason)}
        + support ∈ {assumption, certificate, observation, calculation, statistical, testimony, adapter, none}
        + content (a VE formula, a norm, a definition, a reading set, or none)
kind := asserted | norm (W1) | definition (W3)
      | attributed(agent, act ∈ {says, promised, believes, intends, expects, denies}, kind)
      | hedged(modality ∈ {could, likely, generally, typically, effectively}, kind)
      | causal(relation ∈ {because, in order to, prevents}, kind, kind)
      | question | instruction | example | exposition | analogy | explanation | meta | unformalised(reason code)
      kinds nest (recursive): "Alice believes Bob probably caused X" = attributed(alice, believes, hedged(likely,
      causal(because, asserted, asserted))); the Lean admission decoder (3.6) checks the tree
open term := name, arguments, decided_by, necessary conditions (VE), sufficient conditions (VE, optional), factors,
             precedents (meaning ids of pinned facts), jurisdiction, version
partition: units sorted, non-overlapping, contiguous modulo whitespace and punctuation; the checker verifies it
residual  := open terms + assumptions + bridge leaves + unresolved reading sets (the headline number)
```

Attributed and hedged content is quoted by `meaning_id`; the checker verifies the quoted formula is the displayed
one and never infers content from attribution. Using a quoted unit as a premise in a deduction needs a bridge leaf
(`bridge:accepts(agent, unit)`), which is a labelled assumption (3.6), enforced by Python and by the Lean
admission decoder.

**Reading sets (VISION.md section 3).**

```text
readings unit := span + readings [r1..rk] (k ≥ 1; each a unit content with its own meaning_id and its own kind)
                 + admission per reading: (who, why, distinguishing model id versus each other reading)
                 + status ∈ {authored (k = 1, signed by the author; rejected readings kept as history), open}
                 + version; the set is "readings considered so far"; anyone may propose an extension
narrowing unit := cites (set id, version), keeps ⊆ readings, by whom, reason (cited spans); never edits the set
weights unit   := optional, attributed, removable; ignored by every check; never in the evidence layer
checking a conclusion C whose dependency cone contains ambiguous units U1..Un (readings R_i1..R_ik_i):
  assertion readings under identical backgrounds (every R_ij a closed formula over one environment; no reading
  changes Background, a completion or a definition):
    ALL     Γ_all := { ⋁_j R_ij : i } ⊨ C   one certificate; Lean `readings_all_iff`:
            S ⊨ ⋀_i ⋁_j R_ij ↔ ∃ choice c, S ⊨ ⋀_i R_i,c(i); k^n is never enumerated
    NONE    one finite model M with M ⊨ R_ij for all i, j and M ⊭ C (the shared-model witness)
  any other reading kind (a norm, a definition, a reading that changes Background) or differing backgrounds:
    the complete choices are enumerated (≤ 64, else UNKNOWN); each choice is elaborated separately on its own
    route; ALL = a certificate per choice; NONE = a countermodel per choice
  SOME    a certificate for a named choice c, plus a checked countermodel for some other choice c' (else ALL or UNKNOWN)
  UNKNOWN otherwise (budget)
  a choice is global per unit within one argument; results under a narrowing are labelled `narrowing:<id>`
  labels: `readings:<set>@<version>:<choice|all>`; a cited lemma carries them; citing under an incompatible
  choice map (a different choice for a shared unit) is rejected; a later set version marks dependants STALE
```

**Trusted core.** None in the checker. Lean statement layer: `readings_all_iff` (small) in `lean/VE/Route/Readings.lean`,
stated for assertion readings under one environment; the label field and admission decoder (P0). Statement review
of the unit schema, the open-term schema and the reading-set rules.

**Depends on / files.** P0 (labels, admission, vacuity). Owns `ve/document.py`, `ve/readings.py`, `ve/openterms.py`,
`ve/surface/registers.py`, `usecases/*/commitments.ve.md`, `tools/coverage_dashboard.py`, `docs/spec/document.md`,
`lean/VE/Route/Readings.lean`. Assist tools (`add_unit`, `add_reading`, `narrow`) are specified here and built by W8.

**Acceptance.** (1) Schema and identity tests; the partition check rejects overlapping, missing and out-of-order
spans; nested kinds of depth 3 round-trip through the format and the Lean admission decoder. (2) Three pilots with
100% of source bytes in units (whitespace and punctuation excepted); the residual listed by kind with reason
codes; the count of open terms per document reported. (3) Every attributed or hedged content parses and
type-checks; a graph that references quoted content without a bridge leaf is rejected by Python and by the Lean
route; stripping a bridge or background label changes the report and the wire hash (tamper test). (4) Coverage
table at baseline, then after each merge; second-rater agreement on kinds reported. (5) Blind fidelity audit of
the English rendering against the source; the disagreement rate is a headline number. (6) Reading sets: a
translated paragraph with three ambiguous assertion sentences shows ALL, SOME and NONE each with its certificate
or witness; 12 ambiguous units with two assertion readings each check ALL with one certificate and no enumeration;
a unit whose readings are a norm and an open-term form (the constitution's priority rule) is checked per choice
with two elaborations and never by disjunction (norm-reading test); 7 such units report UNKNOWN once 2^7 exceeds
64. (7) A narrowing is recorded and every result under it is labelled; removing a weights unit changes no verdict;
citing a lemma under an incompatible choice map is rejected. (8) `ve assist` authors a unit and a reading set end
to end (with W8).

**Effort and model.** Format, CLI, rendering 3 days (Sol); pilot authoring 3-4 days (Opus 5.5 through `ve assist`,
no paid API); dashboard 1 day (Sol); Lean readings theorem 1 day (Opus); write-up by Codex.

### W3. Definitions, lemma citation and statement-layer sugar

**Goal.** Name a property once and use it everywhere; cite a certified lemma by `meaning_id`; write `iff` and
"every point that is prime". Closes math gaps G4, G7, G8 and the constitution's name-versus-content gap.

**Deliverables.** Profile `definitions@0`: vocabulary entry `{"defined": {"arguments": [...], "body": AST}}`;
strict `define p(x) as (φ).`; English "call a point prime if ...". Lemma bundles: a DAG of
`(environment_id, premises, conclusion, certificate, leaf labels)` with a `cite` premise form; `ve bundle check`;
English "by Theorem 3". Sugar `iff`, "every s x that is P", "no s is P" (input-only; rendered only under
`definitions@0`). Versioned definitions: a redefinition is a new vocabulary version; documents pin the version.
Lean: `Definitions` layer (`expand`, `conservative` as the `expands` field of the P0 `Layer`, `faithful`); the
route acceptance theorem instantiated for definitions. Math mini-paper re-run.

**Semantics.**

```text
definition p(x̄) := φ(x̄)    p new; φ over symbols strictly below p in the shared dependency DAG (3.5); no recursion;
                            closed under x̄; p may not carry W5 flags (functional/total) and may not be regulated by
                            W1 norms; p may mention regulated predicates below it (violation := required ∧ ¬done)
Σ+D structures := those satisfying ∀x̄. p(x̄) ↔ φ(x̄); elaboration = these biconditionals as background premises
conservativity : every Σ-structure admissible below expands uniquely to Σ+D (the Layer's `expands`), so Σ+D ⊨ ψ iff Σ ⊨ ψ for ψ over Σ
citation       : a deduction may add lemma L's conclusion iff L is in the same bundle, strictly earlier in the DAG, has
                 the same environment_id (hence the same definitions version), every hypothesis of L is among the
                 citing deduction's premises or itself cited, and L's reading-choice map is compatible with the citing
                 deduction's (same choice for every shared unit; incompatible maps are rejected); the citing report
                 inherits every transitive undischarged leaf of L with its label (bridge, background, open, readings,
                 narrowing); the bundle is re-checked in one Lean run
```

**Trusted core.** Checker unchanged (definitions stay premises; the `define-unfold@0` optimisation rule is deferred).
New Lean: `Definitions.expand`, `conservative`, `faithful`; citation soundness through the parametric route
(`entails_cut`, `lean/VE/Consequence.lean:37`) rather than a per-checker rewrite; citation admission (labels and
choice maps) in the P0 admission decoder. Statement review of the citation rule.

**Depends on / files.** P0 (`Background`, labels, registry, DAG order). Owns `ve/definitions.py`, `ve/bundle.py`,
`ve/surface/definitions.py`, `lean/VE/Definitions/*`, `usecases/math-mini-paper`; edits `ve/environment.py` only
through the P0 declaration-extension hook and `ve/argument.py` only for `cite` (patch reviewed by P0's owner).

**Acceptance.** (1) `conservative` and `faithful` audited; a definition mentioning its own symbol, a symbol not
below it in the DAG, or a free variable is rejected in Python and Lean with the same diagnostic; a flag on a
defined predicate is rejected; a definition above a norm (`violation`) is accepted. (2) Math paper: D2-D5 become
definitions with zero copied axiom statements in theorem hypotheses; T7mono is certified by citing T7a, T7b and
T7; the certified count rises from 17/19 today (15 by tableau, T9 and T9e by closure induction since 2026-09-22)
to 18/19; C1 stays honestly uncertified. (3) Forged citations rejected by both checkers: lemma absent from the
bundle, hypothesis not on the branch, other environment or definitions version, cyclic bundle, a cited lemma whose
leaf labels were stripped (provenance tampering), a cited lemma under an incompatible reading-choice map.
(4) Definition bodies change `environment_id`; existing fixtures unchanged. (5) 1,000 sugar round trips; canonical
strict text of expanded forms unchanged; English renderings of environments without `definitions@0`
byte-identical. (6) Constitution: the four property definitions connect `@safety` and the others to their
content, and the corrected priority norm (W1) uses them. (7) Differential elaboration: Python `expand` versus Lean
`Definitions.expand` on 1,000 generated definition sets (depth up to 4, definitions above and below norms);
mutations (swap a body, change the version) change `environment_id` and are rejected by the bound hash.

**Effort and model.** Python 3 days (Sol); Lean 3-4 days (Opus 5.5).

### W4. Stage 1: n-ary atoms (stage 2, the unified checker, deferred)

**Goal.** Predicates of any arity up to 6 in one checker route, with the existing checkers untouched.

**Deliverables.** Profile `nary@0` with `Atom(p, [t1..tk])`, wire `["atom", p, [terms]]`, strict `p(t1, ..., tk)`
for `k ≥ 3` (forms for k = 1, 2 unchanged), English templates with k placeholders and the generalised lint. Lean
`lean/VE/Core/*`: the closure checker plus n-ary atoms as `ve-tableau-core-checker@1` accepting
`{relational-fol@0, closure@0, nary@0}` (the closure+n-ary family of 3.3); conservativity embeddings of v0 and
closure; the Core instance of the P0 parametric `CertificateSound`. Python evaluation, search, printer, parser;
Rust parity; conformance generator. FOLIO witnesses.

**Semantics.** Signatures become sort lists; relation extensions are sets of k-tuples; equality congruence
substitutes per position; finite models supply k-tuples; repeated arguments (`p(a,a,b)`) are valid. Unary and
Binary embed as length-1 and length-2 atoms (theorem). Quantifiers, closure over binary homogeneous edges and
arithmetic are unchanged.

**Trusted core.** The one checker change of the round. New checker and route only; the v0, closure and order files
stay byte-identical (hash test). New theorems: `Core.eval_iff_denote`, `check_iff_wellFormed`,
`Tableau.checkCertificate_sound`, `entails_v0`, `entails_closure`, the route gate, and the Core instance of
`CertificateSound`. Statement review of the unified `Entails`.

**Depends on / files.** P0; numbers2 merged before any Rust or `ve/entailment.py` edit (rebase). Owns `ve/ast.py`
(Atom), `ve/evaluate.py`, `ve/search.py`, `ve/model.py`, `ve/entailment.py` (route), `ve/surface/nary.py`,
`lean/VE/Core/*`, `rust/ve-core/src/*` (after numbers2's Rust lands); edits `ve/environment.py` through the P0 hook.

**Acceptance.** (1) Audit passes; old checker files unchanged. (2) At least 500 generated n-ary certificates
accepted by Python and Lean; at least 2,000 mutations rejected by both, including argument permutations
`p(a,b,c)` versus `p(b,a,c)`; zero disagreements. (3) Existing v0 and closure corpora replay unchanged on their own
routes and through the embeddings. (4) Rust: 5,000 fuzz pairs agree; arity-6 tables. (5) FOLIO: the 216 sentence
pairs containing an arity>2 atom parse directly; the new direct-fit number on the frozen 30-item sample is
reported. (6) N-ary witnesses over user sorts: a FOLIO ternary event predicate and FRET's `value(signal, t, v)`
with `t` a user sort (integer time is W4 stage 2, section 7); the constitution's `conflict` is not among them
(its defect is the rule's pairwise shape, fixed in W1). (7) Mixed-feature model validation: models with n-ary
tables plus background premises (flags, literals) accepted or rejected identically by Python, Lean and Rust.
(8) Hostile wire: arity mismatch, arity 7, non-list terms, unknown sort in position 3, all rejected with the same
diagnostic; `p(a,a,b)` is accepted. (9) Mixed-profile rejection: an envelope declaring `order@0` with `nary@0` is
rejected on this route with `UnsupportedProfile` naming the pair (stage 2 is deferred).

**Effort and model.** Lean 6-8 days (Opus 5.5); Python 3 days and Rust 2 days (Sol). Stage 2 (Farkas rules and
integer quantifiers ported from the order checker, closure × order in one document, integer-time n-ary relations)
is deferred: trigger in section 7.

### W1. Norms: obligations, prohibitions, permissions, exceptions and priorities (narrowed)

**Goal.** Write "must", "must not", "may", "unless", "except when", "takes precedence over", "by default" as
named rules and have the checker decide what a policy requires in a situation, and whether rules conflict, with
a witness situation when they do.

**Deliverables.** Profile `norms@0`. Norm statements in strict and English surfaces as numbered rule blocks
("Rule 3. ...", "Exception to rule 3: ...", "Rule 5 takes precedence over rule 2."), never inline `unless` chains;
numbers are display-only, identities use stable rule names. Elaboration to FOL (Python mirror plus the Lean
`Norms` layer). Static conflict check, three-valued, with the witness rendered as a situation (W8). Cedar
policy-set adapter (permit, forbid, default deny, missing-attribute and error behaviour). Reformalised 14th-s1
clauses 2-4 and the Claude-constitution priority rule. Spec `docs/spec/norms.md` (reviewed by Astra + Fable before
Lean starts, rule 10), Lean `lean/NORMS.md`.

**Semantics.**

```text
norm N   := name (number display-only); guard G_N(x̄) (a VE formula over the situation variables x̄; regulated
            predicates only strictly below p in the shared DAG, 3.5); consequence C_N(x̄) = one literal p(x̄) or ¬p(x̄)
            over a regulated predicate p; exceptions E_1..E_k (norms on the same p and x̄); "N' takes precedence over N"
            makes N' an exception of N (same p); precedence is a DAG (a rule may take precedence over several);
            cycles are rejected
yields_N(x̄)  := G_N(x̄) ∨ ⋁_i yields_{E_i}(x̄)        some norm in N's subtree applies (Catala: the subtree yields a value)
selects_N(x̄) := G_N(x̄) ∧ ¬⋁_i yields_{E_i}(x̄)        N's own consequence is the selected one
P_p(x̄)       := ⋁_{N: C_N = p(x̄)} selects_N(x̄)        some node selects the positive literal
N_p(x̄)       := ⋁_{N: C_N = ¬p(x̄)} selects_N(x̄)       some node selects the negative literal
completion   := one per dual pair, declared per predicate:
                deny-by-default   O_p(x̄) := P_p(x̄)      (p holds exactly when some node selects it)
                allow-by-default  O_p(x̄) := ¬N_p(x̄)     (p holds unless some node selects ¬p)
                elab(p)  := ∀x̄. p(x̄) ↔ O_p(x̄)          the completed outcome is the elaboration of p
duals        := forbidden(a) is the W3 definition ¬permitted(a), never a second regulated predicate;
                violation(a) := required(a) ∧ ¬done(a) is a W3 definition above the norms (3.5)
profile premise := ∀a. required(a) → permitted(a)  (background, identity-bound)
outcome substitution := in a guard, every regulated predicate q below p is replaced by O_q (recursively, terminating
                by the DAG); after substitution and definition expansion a guard is over base symbols only
conflict(x̄)  := P_p(x̄) ∧ N_p(x̄) for some regulated p, or O_required(x̄) ∧ ¬O_permitted(x̄)
                (both after outcome substitution), evaluated over admissible base structures, that is, structures of
                the layer below satisfying Background without the completions or the profile premise being tested;
                two selecting nodes with the same consequence are a redundancy warning, not a conflict (a stated
                deviation from Catala's error)
status       := CONFLICT-FREE (certificate) | CONFLICT (checked witness base structure) | UNKNOWN (budget)
theorem      := Norms.conflictFree_expands: for every admissible base structure S₀, an expansion S of S₀ satisfying
                elab ++ profile premise exists and is unique iff conflict(x̄) is false at every x̄ in S₀; this is the
                `expands` field of the P0 Layer, so CONFLICT-FREE means every base structure has exactly one
                admissible outcome assignment
fragment     := (proof-gated small-model theorem `conflict_smallModel`) after outcome substitution and definition
                expansion the conflict formulas are quantifier-free, and the admissibility theory of the layer below
                is universal, function-free and relational: functional flags allowed, `total` excluded, no closure,
                no $int; then a conflict witness restricts to its witnesses plus constants, so enumeration up to the
                per-sort bound max(1, |constants of the sort| + |witness variables of the sort|) is complete.
                Completeness (CONFLICT-FREE from exhausted enumeration) is enabled only once `conflict_smallModel`
                is proved in Lean and audited; until then, and always outside the fragment, CONFLICT-FREE needs a
                tableau certificate, the enumerator is W1(5)'s oracle, and a checked witness of any size is CONFLICT
Cedar        := permit norms conclude permitted(r) for the reified request r; forbid norms conclude ¬permitted(r) and
                take precedence over all permits; deny-by-default completion; each policy condition c is translated
                to (def_c, val_c) by Cedar's error rules (`has`, short-circuit `&&`/`||`, missing attribute = error)
                and the guard is def_c ∧ val_c, so an erroneous policy is inapplicable, as Cedar skips it
```

Worked check of the reviewers' cases. Astra's parent/child/grandchild with consequences `¬p, ¬p, p` and true
guards: `yields_gc`, so `selects_child` and `selects_parent` are false and only `p` is concluded. Fable's
"if not p(x) then p(x)" mentions `p` in a `p`-norm's guard and is rejected by the DAG. **Both default
counterexamples (v2's check missed them):** (a) an unconditional rule selects `required(a)`; `permitted` is
deny-by-default with no permit rule; then `O_required(a)` and `¬O_permitted(a)`, the profile premise fails, and
v2's "selects `¬permitted`" test saw nothing: v3 reports CONFLICT with witness `a`. (b) `required` is
allow-by-default with no rule selecting `¬required(a)` (required by default) and `permitted` deny-by-default
with no permit rule: no node selects anything, `O_required(a) ∧ ¬O_permitted(a)` holds, CONFLICT. **The
total-functional regression:** complementary rules guarded by `¬r(x,x)` with `r` total and functional lie outside
the fragment (`total` is existential); one-element enumeration finds nothing and must report UNKNOWN, never
CONFLICT-FREE; the two-element structure `r = {(1,2),(2,1)}` is a checked witness and the reported status is
CONFLICT. The constitution's priority rule becomes one norm "follow property x in situation s unless a contending
property y outranks x", whose guard has an existential (outside the fragment, so its conflict status is
three-valued); it is satisfiable with three or more contending properties. The document's own "holistic, not
strict" caveat is an open term `weighs_higher(s, x, y)` with the constitution's authors as decider, and the
strict-dominance norm is one reading in a reading set whose other reading is the open-term form (W2; a norm
reading, so checked per choice).

**Trusted core.** Checker unchanged. New Lean: `Norms.Tree`, `yields`, `selects`, `outcome` (`P_p`, `N_p`,
`O_p` by recursion on the DAG), `holdsCatala` (the direct default semantics by recursion on the tree),
`elaborate`, theorems `elaborate_iff : S ⊨ elaborate T ↔ holdsCatala T S`, `precedence_acyclic`,
`conflictFree_expands` (existence and uniqueness of the expansion exactly when no conflict), the `Norms` layer of
the P0 route and its acceptance theorem; `conflict_smallModel` (the fragment theorem) in the same trusted core,
audited in W1(1), gating completeness. Statement review of `holdsCatala`, `outcome`, the conflict formula, the
fragment and the profile premise, as part of the `docs/spec/norms.md` review before Lean starts.

**Depends on / files.** P0; W3 merged (definitions for `forbidden`, `violation`, readable elaboration); W2 unit
schema (a norm is a unit kind). Owns `ve/norms.py`, `ve/surface/norms.py`, `ve/adapters/cedar.py` (inside the
`ve/adapters/` package owned jointly with W5), `lean/VE/Norms/*`, `usecases/us-constitution-14th-s1`,
`usecases/claude-constitution-excerpt` (norm units, through W2's format), `docs/spec/norms.md`. Assist tool
`add_norm` is specified here and built by W8.

**Acceptance.** (1) `elaborate_iff`, `precedence_acyclic`, `conflictFree_expands` and (when claimed)
`conflict_smallModel` audited, no new axioms. (2) Cedar, in two gates. W1's own gate: the no-attribute subset of
the pinned corpus (`cedar-policy/cedar-integration-tests@1999ea2`, 11 scenarios, 115 recorded decisions, already
under `experiments/P3-formalisation-tax/`): for every decision in the fragment (no extension functions, no
attribute or context access), the elaborated decision equals the recorded Cedar decision and
`experiments/P3-formalisation-tax/reference_cedar.py`; the excluded decisions are listed by reason. Joint W1+W5
gate (after W5): all 115 decisions, including missing-attribute and error cases, with the in-fragment fraction
reported. (3) Gatekeeper: 10 deny-style templates reproduce their fixture violations. (4) 14th-s1: a countermodel
showing a law that violates clause 2 and a model of one that does not; constitution: the corrected priority norm
is satisfiable with three contending properties, and the holistic caveat is an open term in a reading set. (5) A
hand-written conflicting pair yields a witness situation; the repaired pair yields a CONFLICT-FREE certificate;
counterexamples (a) and (b) above each report CONFLICT with witness `a`; the total-functional `¬r(x,x)` regression
reports CONFLICT with a two-element witness and never CONFLICT-FREE, and with the witness search disabled reports
UNKNOWN; a pair outside the fragment with the budget exhausted reports UNKNOWN (budget-to-UNKNOWN test); an
independent brute-force finite-model enumerator agrees with the tableau on 500 generated pairs inside the
fragment. (6) 2,000 generated norm trees round-trip through English as numbered rule blocks; renumbering changes
no identity. (7) All existing identity fixtures unchanged; a norm document's `meaning_id` binds the norm AST, not
its elaboration. (8) A certificate replayed on the route is rejected if the norm document hash changes.
(9) Differential elaboration: Python mirror versus Lean on 1,000 generated trees with nesting depth up to 4,
including the `¬p, ¬p, p` case and both completions; mutations (drop an exception, flip a completion, swap a
precedence) flip a verdict and are rejected by the bound hash. (10) DAG violations and precedence cycles rejected
by Python and Lean with the same diagnostics.

**Effort and model.** Spec review 2 days (Astra + Fable); Python and adapter 5 days (Sol); Lean 5-7 days (Opus 5.5).

### W6. Quantities in documents: dates, scaled decimals, counting sugar and finite traces on top of order@0

**Goal.** "On 16 September 2026", "within ten days, Sundays excepted", "3.75%", "16 of the 18 policymakers" as
checked statements, with conventions stated and entailment honest about what it cannot decide.

**Deliverables.** Date literals (ISO date to day number, proleptic Gregorian) and scaled decimals (percent as basis
points, money as minor units) as `Num` under an identity-bound unit tag (schema below). Temporal wordings with
stated endpoint conventions. Event-sort and time-indexed relation conventions with time as a user sort
(`occurs_at(e, t)`; with W4, `holds(signal, t)` over user sorts). Integer-time n-ary relations
(`value(signal, t, v)` with `t : $int`) are W4 stage 2 (section 7) and are not promised here. Finite traces: a
declared horizon `H` per document; `always` and `eventually` as bounded quantification over `[0, H]`. Counting
sugar for literal n: "at least n" (n ≤ 8), "exactly n" and "at most n" (n ≤ 7), "n of the m S are P" (both bounds
apply: m ≤ 8 for the outer at-least, n ≤ 7 and m ≤ 7 for the exactly forms, so m ≤ 7). The excluded-day rule as a
weekday case-split elaboration. Re-rated news article and FRET sample (FRET with user-sort time); Art. I s7
timing clause. Evaluation-only `count@0` is deferred (section 7).

**Semantics.**

```text
unit schema (identity-bound, statement layer; the checker sees $int):
  declaration   env.units: tag ↦ (integer scale, display form)   e.g. day ↦ (1, ISO date), bp ↦ (100, "%"), cent ↦ (100, "$")
  annotation    a unit tag on each $int slot of a predicate signature and on each $int statement occurrence or binder;
                unannotated $int variables and slots are dimensionless and render as bare integers
  lowering      a literal lowers by its declared scale: 3.75% ↦ Num(375):bp;  $12.30 ↦ Num(1230):cent;  date(2026-09-16) ↦ Num(20712):day
  compatibility a comparison or equality between two occurrences needs the same tag (dimensionless matches only
                dimensionless); Python rejects at type-check; Lean admission checks the annotations before erasing
                them to $int; conversions between tags are not provided (section 7)
  rendering     the tag restores the decimal or date form; identity binds tags through environment_id
"within n days of d"   d ≤ t ∧ t ≤ d + n (both ends inclusive);  "before d"  t < d;  "no later than d"  t ≤ d;  "after d"  t > d
"Sunday(t)"            ∃q. t = 7q + k_sunday (integer quantifier, from numbers2)
"n days, Sundays excepted, from d" ↦ ⋀_{k=0..6} (d ≡ k (mod 7) → deadline = d + off(k)), off(k) computed by the elaborator
                       and proved in Lean equal to the counting definition "the least D with n non-Sundays in (d, D]"
at least n s x, φ      ↦ ∃x1. φ(x1) ∧ ∃x2. x2 ≠ x1 ∧ φ(x2) ∧ ... ∃xn. (⋀_{i<n} xn ≠ xi) ∧ φ(xn)
                       (distinctness nested under each binder, so evaluation prunes per binder; capture-avoiding:
                       φ's free indices shifted; Lean `expand_atLeast_iff`)
exactly n              ↦ at least n ∧ ¬ at least n+1;   at most n ↦ ¬ at least n+1;   n of the m S are P ↦ exactly m S ∧ exactly n (S ∧ P)
finite trace           always φ ↦ ∀t. 0 ≤ t ∧ t ≤ H → φ(t);  eventually φ ↦ ∃t. 0 ≤ t ∧ t ≤ H ∧ φ(t)
```

**Trusted core.** Checker unchanged. Lean: `expand_atLeast_iff` (finite and general structures, with the
substitution lemmas), `excludedDays_iff` (case split equals the counting definition), a small `dayNumber` with
monotonicity and its differential test against Python's `datetime`; unit-annotation admission (`Time.units_admit`)
in the route decoder before erasure; the `time@0` layer registers no new formulas beyond order@0, so it rides the
existing order route. Statement review of the endpoint conventions and the unit schema (rule 10) before Lean
starts.

**Depends on / files.** numbers2 merged (integer quantifiers); W4 stage 1 for n-ary relations over user sorts; P0
registry and admission. Owns `ve/surface/time.py`, `ve/surface/count.py`, `ve/units.py`, `lean/VE/Time/*`,
`usecases/news-article` (through W2's format). Does not edit `ve/ast.py` or `ve/evaluate.py` (no `Count` node this
round).

**Acceptance.** (1) News rows 7, 21, 22 and 23 (REIFIED today) become DIRECT with scaled decimals; row 8 ("16 of
the 18") stays REIFIED because 18 exceeds the counting bound, and the coverage table says so; rows 7b and 22b
both stay NO for the same reason (their comparison operand is absent from the source), and the table says so.
(2) FRET: the 30 sampled items re-rated with time-indexed relations over a user time sort; items needing integer
time or real values stay NO and are said to. (3) Art. I s7: for each of the seven presentment weekdays, a checked
model of the elaboration agrees with a brute-force calendar computation of the deadline; a certified entailment
that a bill returned on elapsed day 11 is always timely; a countermodel for "returned on elapsed day 12 is always
timely" (presented on a Sunday, days 1-12 contain one Sunday). (4) No certificate is produced or accepted for an
unexpanded counting form; the expansion certifies; "at least 8", "exactly 7" and "7 of the 7" evaluate within
`MAX_EVALUATIONS`; "at least 9" and "exactly 8" are rejected at parse with a diagnostic naming the bound;
scope-capture tests: φ mentioning an outer variable, nested counting, a bound variable named like an outer one.
(5) Date conversion agrees with Python's `datetime` on 10,000 dates including year ends and leap days; negative
day numbers and pre-Gregorian dates are rejected with a diagnostic; English round trips. (6) Units: a comparison
between occurrences of different tags (`$3.75` versus `3.75%`, both `375`) is rejected by Python type-check and by
Lean admission with the same diagnostic; a dimensionless integer variable renders as a bare integer; rendering
restores the decimal form; adding a unit declaration changes `environment_id`.

**Effort and model.** Python and wordings 4 days (Sol); Lean 2-3 days (Opus 5.5).

### W5. Policy data, stage 1: attributes, strings and adapters (Cedar, Gatekeeper)

**Goal.** Say "the department of that person is finance", compare string-valued fields, and keep regex or glob
checks outside the checker but inside the audit trail.

**Deliverables.** Profile `data@0`: predicate flags `functional: true` and `total: true` (attributes; never on a
defined predicate); built-in sort `$string` whose literals are declared constants of sort `$string` in the
vocabulary (identity-bound; at most 64 per environment), with equality only and no quantification over `$string`
in stage 1 (as `$int` began); adapter records for computed string predicates (`glob@1`, `prefix@1`, `regex@1`) with
`ve adapter run` recomputation; `member` convention for sets (the `extensional` flag is dropped). English definite
descriptions. Cedar attribute and context translation with `has` and missing-attribute semantics (W1's
`(def, val)` rule); Gatekeeper `is_exempt` end to end; use cases `usecases/cedar-*`, `usecases/gatekeeper-*`.

**Semantics.**

```text
functional r : (s1,s2)  adds  ∀x∀y∀z. r(x,y) ∧ r(x,z) → y = z      total adds  ∀x∃y. r(x,y)      (background premises, identity-bound)
"the r of t is P"       sugar only when functional ∧ total:  ∃y. r(t,y) ∧ P(y);  otherwise the author writes the quantifier
$string stage 1         literals are declared constants ("finance": {"sort": "$string"}) so every formula type-checks in
                        the unchanged checker (lean/VE/Syntax.lean:38-41) and Background depends on env only;
                        StringAdmissible(S) := S admissible ∧ distinct literals denote distinct elements (the reviewed
                        stage-1 meaning of strings; no other string property); Background adds ¬(l1 = l2) per pair of
                        declared literals; theorem `string_encoding_sound`: Entails E (Γ ++ distinct(lits)) φ →
                        EntailsString E Γ φ (entailment over StringAdmissible structures); completeness is not claimed
adapter record          function id and version, parameters, the input domain it was run over, input hashes, output
                        table hash; the table is total over the listed domain with explicit error rows; adapter truth
                        is a labelled assumption leaf `adapter:<id>@<version>`; entailment over an adapter predicate
                        without a table is UNKNOWN
```

**Trusted core.** Checker unchanged. Lean: `lean/VE/Data/Background.lean` is the named generator that regenerates
flag premises and literal distinctness from the decoded environment on the route (never from the wire);
`string_encoding_sound`; `flags_model_valid` (a finite model passing the functional/total table check satisfies
the generated premises). Statement review of `StringAdmissible` and the adapter record schema.

**Depends on / files.** P0. Python may land after P0 behind the profile gate; the merge waits for W4 stage 1
(Rust parity and n-ary tables); the joint Cedar gate needs W1. Owns `ve/adapters/` as a package (`ve/adapters/
__init__.py`, `ve/adapters/records.py`, `ve/adapters/gatekeeper.py`; W1 owns `ve/adapters/cedar.py` inside it),
`ve/surface/data.py`, `lean/VE/Data/*`, `usecases/cedar-*`, `usecases/gatekeeper-*`; edits `ve/environment.py`
through the P0 hook and `ve/model.py` through the `Background` validity hook; Rust declaration decoding and
background validation for flags and `$string` (owned here, after W4, on the P0 Rust scope of 3.7).

**Acceptance.** (1) Non-functional or partial-total tables and literal-aliasing models are rejected as invalid
models at every site (Python, Lean, Rust); the generated premises are in `Background` and change `environment_id`;
an undeclared string literal in a formula is rejected at type-check by all three. (2) 1,000 English round trips
with definite descriptions; "the r of t" is refused for non-total attributes with a diagnostic. (3) Cedar: the
frozen 30-item second-rater sample (0 DIRECT, 13 REIFIED, 17 OPAQUE at baseline) is re-rated after W5 and, with
W1, after permit/forbid; the 143 policies of the pinned corpora (`cedar-examples@c251f7d`,
`cedar-integration-tests@1999ea2`) run mechanically through the adapter with the in-fragment fraction reported;
the joint W1+W5 gate: all 115 recorded decisions match `reference_cedar.py` and the recorded Cedar decisions, with
exclusions listed by reason. (4) Gatekeeper: the 20 string items run with adapter tables; a tampered input hash,
table hash or domain list is rejected; entailment over `prefix_of` without a table returns UNKNOWN; an input
outside the listed domain is rejected. (5) Existing fixtures unchanged. (6) `$string` quantification is rejected
with a diagnostic naming stage 2. (7) Differential elaboration: Python versus Lean `Data.Background` on 1,000
generated flag sets and literal sets; the `elaborated-document` conformance family (3.7) extended with flag and
literal cases, Python/Lean/Rust verdicts identical; mutations (drop a flag, alias two literals) change
`environment_id` and are rejected by the bound hash.

**Effort and model.** Python and adapters 4 days (Sol); Lean 2 days (Opus 5.5); Rust 1-2 days after W4 (Sol);
use cases 2 days. Stage 2 (string quantification, a `string-distinct` close rule in the unified checker) is deferred.

### W7. English surface: extension discipline and harness now, the Lean round-trip proof later

**Goal.** Every accepted English input is checked unambiguous in the whole grammar at parse time (P0, 3.2), the
discipline for adding wordings is enforced mechanically, and the Lean theorem waits until the wordings settle.

**Deliverables this round.** `lean/VE/English/Lexicon.lean`: the abstract lexicon (templates as token lists with
placeholder positions, sort nouns, constants) and the `render`/`parse` skeleton for the core fragment; the
longest-match registry (P0, 3.2) and the per-input all-derivations check (P0); a harness
`conformance/english_mixed.py` that generates mixed-construct texts (every merged profile, nested to depth 3) and
runs the all-derivations parser, failing on any text with more than one derivation, as regression evidence; the
Python-versus-Lean differential parse for the core skeleton over the 85,000 round-trip pairs (the Earley
derivation check today covers 12,750 texts: 8,500 directed and 4,250 sampled); `docs/english-surface.md` section
"Extension discipline": every new surface construct is keyword-led with a registered keyword in longest-match
order, ships a grammar production, passes the per-input check on its fixtures and the mixed harness, and is either
covered by a Lean lemma or listed in the legend as "Lean coverage pending" (a label about proof coverage, never a
substitute for the per-input check).

**Deferred.** Theorems `parse_render`, `render_injective`, `unique_derivation` over the full lexicon: trigger in
section 7.

**Depends on / files.** P0 registry to start the harness; the Lean skeleton starts now. Owns `lean/VE/English/*`,
`conformance/english_mixed.py`, `conformance/english_lean.py`, `docs/english-surface.md` (others append sections).

**Acceptance.** (1) The mixed harness runs at every merge with zero multi-derivation texts; the per-input check is
what admits inputs. (2) Core-skeleton differential agreement on the full 85,000-pair corpus with zero mismatches.
(3) Every merged workstream's wording is registered, in the harness, and either covered or listed. (4) Human
readability is still unmeasured and is stated as such.

**Effort and model.** 4-5 days (Opus 5.5 for Lean, Sol for the harness).

### W8. Authoring: `ve assist` and `ve propose` keep pace with every construct

**Goal.** Every construct of this round is authorable through the assistant by someone writing English, with
measured fidelity, and every witness the checker produces is readable in document terms.

**Deliverables.** Tools per construct: `add_unit` (kind, meaning status, support), `add_reading`, `narrow`,
`define`, `cite`, `add_norm` (named rules, exceptions, precedence), `declare` extended (arity up to 6, flags,
`$string` constants, unit tags, open-term schema), date, decimal and counting sugar accepted on input. Proposer
prompt examples: five per construct. Grammar-constrained proposer (grammar export of the environment's profiles).
For every accept: the deterministic paraphrase, an **example situation** (a checked finite model rendered in
document terms) and the **rejected readings** ("read as A, not B", with the distinguishing model). A residual
panel in `status` (open terms, assumptions, bridge leaves, unresolved reading sets, vacuity). Approval binds the
`meaning_id`; any edit invalidates the approval and its dependants. Translation mode: `propose` returns readings
with distinguishing models feeding `add_reading`; for a unit marked translation, accepting a single reading is
refused unless a `narrow` record with a reason is written. **De-elaboration** `ve/deelaborate.py`: per-construct
witness renderers registered in the surface registry (day numbers to dates, scaled integers to decimals with
units, defined predicates by name, norm witnesses as "Rule 3 applies; its exception 3a does not", attributes as
"the department of Alice is finance", reading choices by name, adapter rows by input). The assistant highlights
the parts of a translation that change meaning most (the distinguishing model is that highlight; V4 recorded Haiku
approving 4/24 mistranslated claims).

**Per-construct held-out fidelity gate.** For each construct: 20 English sentences written by a model not used for
tuning, sealed by hash before any prompt tuning; authored through the assistant by Opus 5.5 and, as the weak-author
check, Haiku 4.5; blind cross-family fidelity audit (Astra) of the deterministic paraphrase against the prose without
seeing proof status. Pass: at least 80% faithful (the authoring gate already adopted for the frontier plan) and zero
"certified but unfaithful" load-bearing nodes. A failing construct stays "strict only", is listed in the ROADMAP
table, and is re-gated after the fix. De-elaboration gate: a second rater reads 20 rendered witnesses per construct
against the model and reports the disagreement rate; witnesses that a reader cannot map back to the document fail
the construct.

**Trusted core.** None. Statement review of the approval-binding rule (what an approval hash covers).

**Depends on / files.** Owns `ve/assist/*`, `ve/propose.py`, `ve/deelaborate.py`, `tests/test_assist*.py`,
`experiments/authoring-gates/` (sealed sentence sets, audits). Each workstream sends its tool spec and five
examples; W8 builds and gates them. The harness and sealed sets start now; per-construct work starts when the
construct merges.

**Acceptance.** (1) Every construct of W1-W6 has its tool, examples, paraphrase, example situation and rejected
readings; a construct without them cannot be offered (test). (2) Gates run and reported per construct; the ROADMAP
table lists offered versus strict-only constructs. (3) Approval tamper tests: editing an approved node's text,
anchors or environment invalidates the approval and every dependant. (4) Translation mode: a unit marked translation
cannot be collapsed without a narrowing; removing weights changes nothing. (5) De-elaboration: every pilot witness
renders as a situation; the second-rater disagreement rate is reported. (6) Ledger verification
(`ve/assist/verify.py`) covers the new tools.

**Effort and model.** Base 3 days plus 1 day per construct (Sol); audits Astra xhigh; no paid API (claude CLI and
Codex).

## 5. Ownership and dependency matrix

Files by owner. "Via owner" means the other workstream sends a reviewed patch; hotspots are edited only through
the P0 hooks.

| Path | Owner | Others write via owner | Frozen interface consumed |
|---|---|---|---|
| `ve/order.py`, `ve/entailment.py` (order route), `ve/grammar.py` (export), `lean/VE/Order/*`, `rust/ve-core/src/*` (order@0) | numbers2 (`codex/numbers2`) | none; merges first when green, P0 and W4 rebase | none |
| `ve/background.py` (new), `ve/profiles.py` (new), `ve/environment.py` hooks, `ve/argument.py` (labels, vacuity, background, checker build), `ve/surface/registry.py` (new), `ve/wire.py` tags, `lean/VE/Route/*` (Layer, Checker, Route, Admission, Gate), `lean/VE/ClaimGraph.lean` label field, `lean/Main.lean` `route`, `rust/ve-core/src/{environment,model,eval,search}.rs` (envelope, Background) | P0 | W3 (`cite`), W5 (validity hook, flag and `$string` decoding) | numbers2 Rust after its merge |
| `ve/document.py`, `ve/readings.py`, `ve/openterms.py`, `ve/surface/registers.py`, `usecases/*/commitments.ve.md`, `tools/coverage_dashboard.py`, `docs/spec/document.md`, `lean/VE/Route/Readings.lean` | W2 | W1, W3, W6 (units of their kinds) | labels, admission decoder, vacuity |
| `ve/definitions.py`, `ve/bundle.py`, `ve/surface/definitions.py`, `lean/VE/Definitions/*`, `usecases/math-mini-paper` | W3 | none | Background, registry, Layer, DAG order, labels |
| `ve/ast.py` (Atom), `ve/evaluate.py`, `ve/search.py`, `ve/model.py`, `ve/entailment.py` (Core route), `ve/surface/nary.py`, `lean/VE/Core/*`, `rust/ve-core/src/*` (n-ary, after numbers2) | W4 | W5 (Rust parity, after W4.1) | Background, registry, Layer, parametric `CertificateSound` |
| `ve/norms.py`, `ve/surface/norms.py`, `ve/adapters/cedar.py`, `lean/VE/Norms/*`, `docs/spec/norms.md`, `usecases/us-constitution-14th-s1`, `usecases/claude-constitution-excerpt` | W1 | W5 (attribute translation inside the adapter) | Background, registry, Layer, DAG order, unit schema |
| `ve/surface/time.py`, `ve/surface/count.py`, `ve/units.py`, `lean/VE/Time/*`, `usecases/news-article` | W6 | none | registry, admission (unit tags), n-ary wire form, numbers2 |
| `ve/adapters/` package (`__init__`, `records`, `gatekeeper`), `ve/surface/data.py`, `lean/VE/Data/*`, `usecases/cedar-*`, `usecases/gatekeeper-*`, Rust flag and `$string` decoding | W5 | W1 (`cedar.py`) | Background, registry, Layer, n-ary wire form, Rust scope |
| `lean/VE/English/*`, `conformance/english_mixed.py`, `conformance/english_lean.py`, `docs/english-surface.md` | W7 | all append a section | registry keyword list, per-input check |
| `ve/assist/*`, `ve/propose.py`, `ve/deelaborate.py`, `tests/test_assist*.py`, `experiments/authoring-gates/` | W8 | each workstream sends tool specs and examples | registry witness renderers, unit schema |

**W4 stage-1 integration amendment (2026-09-26).** Enabling the fourth P0 checker
family required W4 to edit P0-owned dispatch and gate files:
`lean/VE/Route/Run.lean` and `ve/profiles.py`. W4 also updated the corresponding
P0 conformance fixtures and tests in `conformance/p0.py`,
`conformance/elaborated-document.json`, and `tests/test_p0_three_way.py`.
These edits lift the closure+n-ary gate after the Core checker landed; the
v0, closure, and order checker contracts remain frozen. The gate-lift regression
runs the shared P0 family through Python, Rust, and Lean.

Dependencies and start conditions:

| Workstream | Depends on | Blocks | Starts | Model |
|---|---|---|---|---|
| numbers2 | none (in flight) | P0 Rust and `entailment.py` edits, W4, W6 | merges first when green | Sol (Codex) |
| P0 Python | numbers2 merged before Rust, `entailment.py`, `grammar.py` edits; everything else now | every Python workstream | now | GPT-6 Sol (Codex) |
| P0 Lean | none | W1, W3, W4, W5 Lean route instantiation | now | Opus 5.5 |
| W2 | P0 (labels, admission, vacuity) for checking; format and pilots start now | W1 (unit schema), W8 (unit tools) | now (new files) | Sol (format), Opus 5.5 (pilots) |
| W3 | P0 | W1 (definitions for duals) | Lean now against the day-one Layer draft; Python after P0 | Opus 5.5 (Lean), Sol (Python) |
| W4 stage 1 | P0, numbers2 | W5 merge, W6 n-ary relations, Rust for W5 | Lean now; Python after P0 and numbers2 | Opus 5.5 (Lean), Sol (Python, Rust) |
| W1 | P0, W3 merged, W2 unit schema, `docs/spec/norms.md` review | joint Cedar gate in W5 | spec now; Lean after spec review; Python after W3 | Opus 5.5 (Lean), Sol (Python, adapter) |
| W6 | numbers2 merged, W4 stage 1, P0 registry and admission, unit-schema review | none | after numbers2 | Sol (Python), Opus 5.5 (Lean) |
| W5 stage 1 | P0; merge after W4 stage 1; joint Cedar gate after W1 | none | Python after P0 (behind the gate) | Sol (Python, Rust), Opus 5.5 (Lean) |
| W7 | P0 registry (harness); Lean skeleton none | none | now | Opus 5.5 (Lean), Sol (harness) |
| W8 | none (harness, sealed sets); per construct after its merge | offering of every construct | now | Sol; audits Astra xhigh |

Merge order: **numbers2 → P0 → W2 baseline (format and pilots in today's language) → W3 → W4 stage 1 → W1 →
W6 → W5 stage 1 (Python earlier behind the gate; Rust after W4; joint Cedar gate with W1) → W7 harness (any time
after P0) → W8 per construct**. Each merge re-runs the full suite, `lean/audit.py`, Rust conformance, the
per-input unambiguity check on every English fixture, the mixed English harness, the coverage dashboard and the
vacuity report on every pilot.

## 6. Start plan

Start now, in parallel, on disjoint files:

- **numbers2** (Sol, in flight): merges first when green; P0-Py and W4 rebase on it.
- **P0 Python** (GPT-6 Sol via Codex): `ve/background.py`, `ve/profiles.py`, the surface registry with the
  extracted longest-match keyword list and the per-input all-derivations check, the `ve.core@0.2` envelope with
  `UnsupportedProfile` dispatch, `Claim` labels and vacuity in `ve/argument.py`, the checker-build hash, all
  sites in 3.1 and 3.2, the two conformance families, Rust after numbers2. Everything Python waits for it
  (3 days). If the Codex sandbox on the VM is still blocked after one day, P0 moves to Opus 5.5; nothing else
  moves off Codex.
- **P0 Lean** (Opus 5.5): `lean/VE/Route/*` (the `Layer` with `E_in → E_out`, `restrict`, `faithful`, `expands`;
  the parametric `CertificateSound` with the v0, closure and order instances; the composition theorem; the DAG
  order; `route_gate`; the admission decoder with nested kinds and `admit_report_sound`), the `Claim.label` field
  with `METATHEORY.md`, the `route` subcommand. Day-one draft of the signatures; freeze on day three when the
  three instances compile.
- **W2** (Sol for the format and CLI; Opus 5.5 for the three pilots through `ve assist`): new files only; the
  baseline coverage table in today's language is the first output.
- **W3 Lean** (Opus 5.5): `lean/VE/Definitions/*` against the Layer draft.
- **W4 stage 1 Lean** (Opus 5.5): `lean/VE/Core/*`; publishes the n-ary wire form on day one.
- **W1 spec** (planner, then Astra + Fable xhigh review of `docs/spec/norms.md`: outcomes, conflict formula,
  `conflictFree_expands`, the fragment); **W1 Lean** (Opus 5.5) after the spec review, in `lean/VE/Norms/*`.
- **W6 unit schema** (planner, then Astra + Fable xhigh review) alongside the W1 spec.
- **W7 skeleton** (Opus 5.5): `lean/VE/English/*`; harness (Sol) after P0's registry.
- **W8 harness and sealed sets** (Sol): `experiments/authoring-gates/`, `ve/deelaborate.py` skeleton.

After P0 lands: W3 Python, W4 stage 1 Python, W5 stage 1 Python (Sol). After W3 merges: W1 Python and the Cedar
adapter (Sol). After numbers2 and W4 stage 1 merge: W6 (Sol, Opus) and W5 Rust (Sol). W8 gates each construct as
it merges. Peak: four Opus 5.5 Lean agents on the three Claude accounts and three to four Sol agents on Codex.
Reviews: Astra + Fable xhigh on each spec section before build (W1 norms spec and W6 unit schema are the two
section reviews that remain; no further whole-plan review) and cross-family review before merge; write-ups by
Codex. No paid API calls: pilots use `ve assist` through the claude CLI; audits through Codex. Wall clock: P0 in
three days; W2 baseline, W3 and W4 stage 1 by the end of week 2; W1 by week 3; W6 and W5 stage 1 by week 4; W8
gates continuous.

## 7. Deferred and out of scope, with triggers

| Item | Trigger to schedule |
|---|---|
| W4 stage 2: Farkas rules and integer quantifiers in the unified checker; closure × order in one document; integer-time n-ary relations (`value(signal, t, v)` with `t : $int`, FRET integer time) | numbers2 merged and a pilot row that needs `tc[...]` and `<` together, or a FRET item that needs integer time with a ternary relation |
| W5 stage 2: `$string` quantification, a `string-distinct` close rule | W4 stage 1 merged and a Gatekeeper item that needs it |
| Evaluation-only `count@0` (unbounded counts, reported distinctly from entailment) | a pilot row whose count exceeds the sugar bounds (at-least 8, exactly/at-most 7); news row 8 is the first candidate |
| Unit conversions between declared tags (cents to dollars, basis points to percent) | a pilot row that compares two differently tagged quantities |
| General-purpose Lean decoder for legacy graph artefacts (Python `check_argument` replay refinement) | a legacy graph artefact that must be admitted on the Lean route |
| W1 completeness in the fragment (CONFLICT-FREE from exhausted enumeration) | `conflict_smallModel` proved and audited |
| W7 theorems `parse_render`, `render_injective`, `unique_derivation` | no wording change for two weeks after W1, W3, W5 and W6 merge |
| `define-unfold@0` optimisation rule (checker bump) | a certified bundle whose expanded premises exceed the replay budget |
| Workflows, state machines, fulfilment over event sequences | stage 3 (VISION.md) |
| Argument-scheme units for analogy and precedent | stage 3 |
| Modal or Kripke semantics for belief and possibility (attitudes are kinds; upgrade only if inference across attitudes is needed); defeasible "normally" as a consequence relation; real numbers and units beyond scaled decimals; metric-time LTL beyond finite traces; probability inside formulas; second-order sets; general arithmetic induction; open-vocabulary parsing (reviewed out 2026-09-21); human readability studies (deferred by the lead) | research track |

## 8. Response table (finding → change)

### 8.1 v2 → v3: the converged change list (`debates/expand2-v2/`, Astra round 1 items 1-12 as amended by Astra round 2 and Fable round 2)

| Debate item (source findings) | Change in v3 | Where |
|---|---|---|
| 1. P0 composition contract (Astra A3, Fable A2; Astra R2 §1, Fable R2 §5) | `Layer` carries `E_in`, `E_out`, `restrict`, `faithful` and `expands` (unique expansion; `conservative` and `conflictFree_expands` are instances); premises concatenate; `CertificateSound` parametric over syntax and semantics with v0, closure and order instances; four allowed checker families, other mixes rejected; freeze when the three instances compile; W4's Core instance gated separately | 3.3, 3.4, rule 2, 3.9, 3.10(5) |
| 2. One dependency DAG (Astra A3 order, Fable B4, C7 precedence DAG and stable names) | shared DAG over definitions ∪ regulated predicates, definitions above norms allowed, cycles rejected in Python and Lean with one diagnostic; both reversed-order statements (v2 rule 2 and 3.4) deleted; precedence is a DAG; rule names stable, numbers display-only | 3.5, W3 semantics, W1 semantics and deliverables, W1(6) |
| 3. Executable admission and provenance (Astra A3 decoder, B1 nested kinds and choice maps; Fable C4; Astra R2 §2, Fable R1 §4) | `lean/VE/Route/Admission.lean` decodes documents, nested kind trees, bridge leaves and claim graphs; `admit_report_sound`; bridge admission enforced by Python and Lean; "structurally impossible" dropped; labels carry `<choice|all>` and `narrowing:<id>`; citation under an incompatible choice map rejected; legacy graph decoder deferred | 3.6, W2 schema and (1), (3), (6), (7), W3 citation and (3), section 7 |
| 4. Literals, Rust scope, differential tests (Fable B1, B5, C5 table claim; Astra B3 last point) | `$string` literals are declared constants; `Background(env)` only; Rust decodes declarations, regenerates Background, checks elaborated documents; `elaborated-document` conformance family; W3(7) and W5(7) differential elaboration tests | 3.1, 3.7, rule 5, W5 deliverables and semantics, W3(7), W5(7) |
| 5. Norm conflict over completed outcomes (Astra A1, Fable A1; Astra R2 §3, Fable R2 §1) | `P_p`, `N_p`, `O_p` (deny-default `P_p`, allow-default `¬N_p`); conflict := `P_p ∧ N_p` or `O_required ∧ ¬O_permitted` after recursive outcome substitution, over admissible base structures without the completions or the profile premise; `conflictFree_expands`: expansion exists and is unique iff no conflict; counterexamples (a) selected `required(a)` with deny-default `permitted` and (b) required-by-default with deny-default `permitted` in W1(5) | W1 semantics, worked check, trusted core, (1), (5), (9) |
| 6. Small-model claim (Astra A2, Fable C7; Astra R2 §4, Fable R2 §2) | v2's fragment claim replaced by the proof-gated `conflict_smallModel`: quantifier-free after outcome substitution and definition expansion; universal, function-free, relational admissibility theory; `total`, closure and `$int` excluded; per-sort bound `max(1, constants + witness variables)`; completeness only after the Lean proof; the total-functional `¬r(x,x)` case reports CONFLICT with a two-element witness, UNKNOWN without it, never CONFLICT-FREE | W1 semantics (fragment), worked check, (1), (5), section 7 |
| 7. Reading sets by kind (Fable A2, Astra B1; Astra R1 §7, Fable R1 §7) | ALL by disjunction and the shared-model NONE only for assertion readings under identical backgrounds; other kinds enumerate complete choices ≤ 64 or UNKNOWN, each choice elaborated separately; nested kinds; labels `readings:<set>@<version>:<choice|all>`; norm-reading test in W2(6); VISION.md section 3 point 3 amended | W2 reading sets, (1), (6), (7); VISION.md §3 |
| 8. Surface unambiguity per input (Astra A5, Fable C1; Astra R2 §5, Fable R2 §3) | prefix disjointness replaced by longest-match registration with the extracted keyword list and a test; the all-derivations parser runs on every accepted English input on every route; more than one derivation rejects; budget exhaustion rejects with a diagnostic naming the budget and the author falls back to strict text (Astra R2 wrote "UNKNOWN" for this outcome, Fable R2 "reject naming the budget"; the plan records rejection, since a parser that cannot verify unambiguity admits no AST either way, and the diagnostic names the budget as both asked; Astra R2 scoped the check to `ve.core@0.2` with legacy routes preserved, Fable R2 to all routes with P0's fixture replay as the evidence that nothing existing is rejected; the plan takes all routes, which the replay makes identical for every existing input); corpus and mixed harness stay regression evidence | 3.2, rule 10, W7, 3.10(3) |
| 9. W6 route and units (Astra A4, B2; Fable B3, B6; Astra R2 §6, Fable R2 §4) | integer-time n-ary examples moved to W4 stage 2 with a trigger; FRET re-rated with user-sort time; W4(6) witnesses over user sorts; unit schema: declared tags `(scale, display)`, annotations on signature slots and occurrences/binders, identity-bound, Python type-check and Lean admission before erasure, dimensionless default, conversions deferred with a trigger; unit-schema statement review before Lean | W6 deliverables, semantics, trusted core, (2), (6); W4(6); section 7 |
| 10. Counting bounds (Fable B2; Astra R2 §7) | distinctness nested under each binder; at-least ≤ 8, exactly/at-most ≤ 7, both applied to "n of m"; row 8 stays REIFIED and says so; `count@0` trigger restated; resource limits and UNKNOWN unchanged | W6 deliverables, semantics, (1), (4); section 7 |
| 11. Scheduling and code facts (Astra B3; Fable C2, C3, C6; Fable R1 §8) | numbers2 first in the merge order and in both matrices, P0 and W4 rebase; W1(2) split into W1's no-attribute gate and the joint W1+W5 gate; `ve/adapters/` a package (W5 owns it, W1 owns `cedar.py` inside); `p(a,a,b)` valid in W4 semantics and (8); `UnsupportedProfile` dispatch fixed with the profile named; `_checker_build` covers order and every new module | 3.3, 5, 6, W1(2), W4, W5 |
| 12. Evidence corrections (Fable B7, C5; Astra B3 table claim) | Cedar: `cedar-integration-tests@1999ea2`, 11 scenarios, 115 recorded decisions, plus `cedar-examples@c251f7d` for the 143-policy mechanical run, exclusions listed by reason; math baseline 17/19 today (T9, T9e certified by closure induction 2026-09-22), target 18/19; rows 7b and 22b both NO for the absent operand; 85,000 round trips distinguished from 12,750 Earley texts (8,500 + 4,250); "without it" removed from the W8 Haiku 4/24 sentence; acceptance lists, this table and VISION.md updated together | W1(2), W3(2), W5(3), W6(1), W7, W8 |

Retained from the debate without change: W1 and W6 keep their rule-10 section reviews (`docs/spec/norms.md`,
the unit schema) before Lean starts; certificate, witness and UNKNOWN semantics; `ve.core@0.2` identity freeze;
all v2 provisions not named above.

### 8.2 v1 → v2 (retained for the record)

| Finding | Change | Where |
|---|---|---|
| Astra A: W1 recurrence not faithful (`¬p, ¬p, p`); cyclic priorities; unstratified guards; UNKNOWN needed | `yields`/`selects` semantics; precedence DAG; stratification (now the shared DAG, 3.5); three-valued status; worked check | W1 |
| Astra A: P0 semantic boundary incomplete; background must invalidate models across countermodel replay, equivalence, composition, Lean/Rust validation | `Background(env)` with `InvalidModel` at every listed site; Lean and Rust regenerate; invalid-background conformance family | 3.1, rule 5 |
| Astra A: W5 string semantics precede implementation; adapter hashes not regex correctness; table completeness; Cedar error behaviour | `StringAdmissible` + `string_encoding_sound`; no `$string` quantification in stage 1; adapter domain list, error rows, truth as labelled leaf; `(def, val)` translation of conditions | W5, W1 |
| Astra A: W2 can lose judgement provenance; Lean report has only named formulas; 90% contradicts "nothing dropped" | `Claim.label` through `Report`/`Unfolds` and the wire hash; bridge admission (now executable in Lean, 3.6); 100% span accounting with partition check | 3.6, rule 6, W2 |
| Astra B: W3 conservativity broken by flags on defined predicates; citations must keep transitive leaves with labels | flags forbidden on defined predicates; citation inherits labelled leaves; tampering test | W3 |
| Astra B: W6 horizons, endpoints, capture-avoiding expansion, exact counts, denominators; 16-of-18 not certifiable by `count@0`; Sunday counting | conventions stated; horizon `H`; `expand_atLeast_iff` with substitution lemmas; "n of the m"; sugar bounds (now 8/7); weekday case-split elaboration with `excludedDays_iff`; `count@0` deferred | W6 |
| Astra B: W7 composition guarantees; global ambiguity rejection; label no substitute | registry (now longest-match) and per-input all-derivations check; mixed-construct harness at every merge; theorem deferred with trigger | 3.2, W7 |
| Astra B: parallelism overstated; W5 before W4/Rust; W6 edits W4's evaluator; W2/W3 share provenance; no frozen interfaces; W4 tests too narrow | frozen interfaces (3.9); merge order; W6 no longer edits `ast.py`/`evaluate.py`; provenance owned by P0; W4 mixed-feature, hostile-wire and mixed-profile tests | 3.9, 5, W4 |
| Astra concrete 1-5 | priority order W2, P0, W3, W4.1, narrowed W1; independent conflict check; W4.2, string optimisation and general counting deferred; oracle, mixed-profile, invalid-background, tampering, scope-capture, calendar-boundary and budget-to-UNKNOWN tests; ownership matrix; end-to-end route theorems | 4, 5, 7, rule 10 |
| Fable A1: norm elaboration inconsistent while conflict check passes; precedence cycles | DAG; cycle rejection; `conflictFree_expands` (v3 form) | W1 |
| Fable A2: no composition of elaborations | typed `Layer` route, parametric `CertificateSound`; W4 instantiates | 3.4 |
| Fable B1: dual regulated predicates over-determine | `forbidden` a definition; one completion per pair; `required → permitted` premise; cross-predicate conflicts checked over outcomes | W1 |
| Fable B2: vacuity unreported | vacuity report at every document check; `vacuous` certificates | 3.8, rule 7 |
| Fable B3: W5 stage 1 overclaims; who generates premises on the Lean route | distinctness as reviewed statement-layer meaning plus proved encoding; `lean/VE/Data/Background.lean` named | W5 |
| Fable B4: acceptance tests met or mis-sourced | W3(2) T7mono by citation; W1(4) corrected norm; W4(5) 216 sentence pairs; W4(6) other n-ary witnesses; W5(3) 30-item sample and 143 mechanical; W6(1) rows 7, 21, 22, 23 REIFIED today | W3, W1, W4, W5, W6 |
| Fable B5: no differential elaboration test | Python-versus-Lean on generated trees, definitions and flag sets (W1(9), W3(7), W5(7)); verdict-flipping mutations rejected by the bound hash | W1, W3, W5 |
| Fable B6: P0 registry under-specified; prefix parsing | dispatch sites enumerated; registry with extracted keyword list (longest-match in v3) | 3.2 |
| Fable C1-C7 | three-valued conflict (W1); numbered rule blocks (W1); W7 skeleton now, theorem later; "profile premises" wording (rule 9); sugar rendering gated by profile so hashes do not move (rule 4); `extensional` dropped (W5); `reference_cedar.py` as oracle (W1, W5) | as listed |
| Vision reviews (both): typed kinds, meaning status, support; open-term schema; 100% accounting; pilots and authoring first; defer unified stage 2 and English proof; de-elaboration; versioned definitions; per-construct fidelity gates | W2 schema; order of section 4; W8; W3 versioning; section 7 | VISION.md, 4 |
| Lead proposal: authoring versus translation modes; reading sets; probabilities as a removable layer | reading sets, narrowings, weights; ALL/SOME/NONE/UNKNOWN (scoped by kind in v3); `readings_all_iff`; translation-mode rule in the assistant | VISION.md 3, W2, W8 |

## 9. After review (adopted, binding)

**Verdict of record.** GPT-6 Astra xhigh and Claude Fable 5.1 xhigh reviewed v2 independently (REVISE; ADOPT WITH
CHANGES), then converged in two rounds (`~/code/manage-agents/debates/expand2-v2/`, `result.txt`: CONVERGED after
round 2) on the twelve-item change list of section 8.1 and the verdict **BUILD, P0 first**, with no further
whole-plan review. v3 applies that list and nothing else.

**Binding decisions.**

1. This plan is adopted. Section 3 is the hand-off spec for P0 (P0-Py: Sol; P0-Lean: Opus 5.5); work starts per
   section 6 with numbers2 merging first.
2. The gates of rule 10 stay in force: theorem-statement reviews, proofs audited under the unchanged allowlist,
   Python/Rust/Lean conformance, cross-family code review before merge.
3. Two section reviews remain before their Lean work starts, both Astra + Fable xhigh: W1's `docs/spec/norms.md`
   (outcomes, conflict formula, `conflictFree_expands`, the fragment theorem statement) and W6's unit schema.
   No other pre-build review is scheduled; a workstream that wants to depart from its section here files the
   change in this file's change log and gets that section re-reviewed.
4. W1 completeness within the fragment is claimed only after `conflict_smallModel` is proved and audited; until
   then every CONFLICT-FREE needs a certificate.
5. English inputs are admitted only after the per-input all-derivations check (3.2) on every route; corpora are
   evidence, never the guarantee.
6. VE's properties are unchanged by this plan: one reading per VE sentence (source ambiguity lives in reading
   sets), mechanical checking, a small Lean-verified checker changed only by W4 stage 1 (and numbers2), and
   Python, Rust and Lean agreement on every conformance family.
