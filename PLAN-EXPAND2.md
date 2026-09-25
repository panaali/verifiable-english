> Status: PLAN (2026-09-25), for review by GPT-6 Astra xhigh and Claude Fable 5.1 xhigh before any build.
> Numbers round 2 (integer quantifiers, Rust order@0, grammar export, Lean order parser) runs separately on
> `codex/numbers2` and is not repeated here. Round 1 is [PLAN-EXPAND](PLAN-EXPAND.md); status lives in ROADMAP.md.

# Language expansion, round 2: seven parallel workstreams

## 1. Aim

Make VE cover what constitutions, policies, papers and news actually say, so that a document becomes a map of
commitments: every sentence is either checked (a formula with exact semantics) or a labelled judgement call, and
nothing is silently dropped. The checker stays small and Lean-proved; the English stays readable; `ve assist`
and `ve propose` can author every new construct.

Evidence for what is missing, from the use cases and E0 (details in `usecases/*/GAPS.md`, `experiments/E0/SURVEY.md`):

| Gap | Where it bites | Rows affected |
|---|---|---|
| Obligation, prohibition, permission, exceptions, priorities | 14th s1 (3/4 clauses), Claude constitution (~10/21), Cedar permit/forbid/default-deny, Gatekeeper deny rules | the normative force of every policy |
| Attribution, hedges, causal and evaluative statements | news 11/26 NO, constitution 12/23 NO, debate (every claim) | most NO rows |
| Definitions, lemma citation | constitution 5/21, math paper T7, every "term of art" | usability of long documents |
| Arity above two | FOLIO 216 atoms, constitution ternary conflict (a real defect), time-indexed relations, math | statements |
| Attributes, strings, sets | Cedar 14/30 reified, Gatekeeper 20 string items, K8s | policy data |
| Time, counting, proportions | news 7 numeric + 1 counting rows, FRET 65 temporal, Art. I s7 ("ten days", "two thirds") | quantities in prose |
| English surface unproved | sign-off rests on a tested, unproved parser | trust of the surface |

## 2. Design rules (binding for every workstream)

1. **Three trust tiers.** (a) *Checker*: Lean tableau checkers, decoders, identity. Only W4 (and numbers2) change
   it. (b) *Statement layer*: everything that decides what a signed-off sentence means: elaborations, generated
   axioms, definitions, register schema. Each new piece is either a Lean-proved elaboration with a faithfulness
   theorem or a reviewed schema; every theorem statement gets a statement review. (c) *Surface and tools*:
   English, `ve assist`, `ve propose`, Rust, search: untrusted, differentially tested.
2. **Elaborate, do not extend the logic.** New constructs (norms, definitions, attributes, counting sugar, dates)
   elaborate deterministically into the existing checked language. The checker sees only formulas it already
   proves sound. The elaboration runs in Lean on the certificate route so the certificate binds the elaborated
   premises to the hash of what the author saw. Modal or non-monotonic proof theory is out of scope this round.
3. **Identity freeze.** Existing envelopes (`ve.core@0`, `ve.core@0.1` closure, order) keep every identity,
   canonical byte, certificate and theorem statement. New constructs live in new profiles under `ve.core@0.2`
   with a `profiles` list; the identity domain is `ve-<kind>-v0.2:<sorted profiles>`. The existing Lean
   profile-gate theorems already reject unknown profiles on the old routes; each new route gets its own gate.
4. **Sugar is input-only for strict text.** The canonical strict printer never changes for existing ASTs. Sugar
   (`iff`, "every x that is P", "at least 3", dates) is accepted on input, expanded before identity, and shown
   again only in the English and fluent views, where the reverse mapping is audited.
5. **Every construct is authorable.** Each workstream ships English wordings, `ve assist` tool support, five
   worked examples for the proposer prompt, grammar-export support or an explicit `UnsupportedProfile`, and Rust
   parity for evaluation and search (never for certificates).
6. **Gates.** Spec section reviewed by Astra + Fable xhigh before build; cross-family code review before merge;
   full suite green; `lean/audit.py` allowlist unchanged (`propext`, `Classical.choice`, `Quot.sound`); no
   `sorry`; identity and parser fixtures byte-identical; each new Lean theorem listed in plain words in the
   profile's `.md`.

## 3. P0: extension points (prerequisite, 1-2 days, GPT-6 Sol)

Before the parallel start, one small refactor with zero behaviour change (all fixtures identical):

- `Environment.axioms()`: generated implicit premises from declarations (empty today), bound to identity through
  the declarations that generate them; `prove_entailment`, `check_entailment_certificate`, search and evaluation
  prepend them. W3 (definitions) and W5 (functional flags, string distinctness) populate it.
- A registry of statement forms and atom forms in `ve/parser.py`, `ve/printer.py`, `ve/fluent.py`,
  `ve/english.py`, `ve/grammar.py`, so each workstream adds a module under `ve/surface/<feature>.py` instead of
  editing the same functions.
- `ve.core@0.2` envelope validation with an ordered profile registry (W4 owns the checker route; others register
  statement-layer profiles).
- `lean/Main.lean`: one subcommand per route, one file per route.

## 4. Workstreams, ordered by value

### W1. Norms: obligations, prohibitions, permissions, exceptions and priorities (Catala-style defaults)

**Goal.** Write "must", "must not", "may", "unless", "except when", "takes precedence over", "by default" and
have the checker decide what a policy requires in a situation, and whether two rules ever conflict.

**Deliverables.** Profile `norms@0`. Norm statements in strict and English surfaces. Elaboration to FOL
(Python untrusted mirror + Lean `Norms.elaborate` on the certificate route). Static conflict check with a
witness situation. Cedar policy-set adapter (permit/forbid/default deny). Reformalised 14th-s1 clauses 2-4 and
Claude-constitution priority rule. `ve assist` `add_norm`. Spec `docs/spec/norms.md`, Lean `lean/NORMS.md`.

**Semantics sketch.** A norm is a finite tree, no modal operator:

```text
norm N   := guard G_N(x̄)          a VE formula open in the declared situation variables
            consequence C_N(x̄)    one literal over a declared *regulated* predicate (permitted, required, valid, ...)
            exceptions E_1..E_k   norms over the same variables and regulated predicate
active_N(x̄)  := G_N(x̄) ∧ ¬active_E1(x̄) ∧ ... ∧ ¬active_Ek(x̄)        (inlined; the tree is finite)
elab(N)      := ∀x̄. active_N(x̄) → C_N(x̄)                          plus elab(E_i) for each exception
precedence "N' over N" (complementary consequences only) := N gets N' as an extra exception
default for regulated p: completion  ∀x̄. p(x̄) → ⋁_{N with C_N = p} active_N(x̄)   (deny by default),
                         or the dual for "permitted unless forbidden"; declared per predicate
conflict(N, N') := ∃x̄. active_N ∧ active_N' with complementary consequences: CHECKED, never assumed
```

Deontic reading is Anderson's reduction over ordinary predicates: fixed profile axioms such as
`∀a. (required(a) ∧ ¬done(a)) → violation(a)` and `permitted(a) ↔ ¬forbidden(a)` are implicit premises bound
into the environment identity. Cedar is one exception layer plus completion: `permit` norms conclude
`permitted(r)` for the reified request `r`; `forbid` norms conclude `¬permitted(r)` and take precedence over all
permits; default deny is the completion. "Generally", "holistic" and similar hedges are not norms: they become
W2 register labels on the norm, and the document says so.

**Trusted core.** Checker unchanged. New Lean: `Norms.Tree`, `active`, `holdsDefaults` (direct default
semantics by recursion on the tree), `elaborate`, theorem `elaborate_iff : S ⊨ elaborate T ↔ holdsDefaults T S`,
`conflictFree_iff`, the norms certificate route (decode norm AST bound by identity, elaborate, replay with the
unchanged checker) and its gate theorem. Statement review of `holdsDefaults` and the fixed axiom list.

**Depends on / conflicts.** P0. Uses W3 definitions for readable elaboration when available (inline expansion
until then). Touches `ve/surface/norms.py`, `ve/norms.py`, `lean/VE/Norms/*`, `lean/Main.lean` (one line),
`usecases/us-constitution-14th-s1`, `usecases/claude-constitution-excerpt`, `ve/assist/*` (tool `add_norm`).
Conflicts: `ve/assist/api.py` with W2 (W2 owns the assist schema; W1 sends a patch).

**Acceptance.** (1) `elaborate_iff` and `conflictFree_iff` audited, no new axioms. (2) Cedar: at least 100
policy sets from `cedar-integration-tests` translated by the adapter; for every test request in VE's fragment
(no extension functions), evaluation of the elaborated norms equals the Cedar authorizer's decision; the fraction
of policy sets in fragment is reported. (3) Gatekeeper: 10 deny-style templates reproduce their fixture
violations. (4) 14th-s1: countermodel showing a law that violates clause 2 and a model of one that does not;
constitution: the priority rule is now satisfiable with three contending properties (the recorded defect) and
the "holistic" hedge is a labelled register. (5) A hand-written conflicting pair yields a witness situation; a
repaired pair proves conflict-free. (6) 2,000 generated norm trees round-trip through English. (7) All existing
identity fixtures unchanged; a norm document's `meaning_id` binds the norm AST, not its elaboration. (8) A
certificate replayed on the Lean norms route is rejected if the norm document hash changes.

**Effort and model.** L: Python and adapter 4-5 days (GPT-6 Sol), Lean 4-6 days (Opus 5.5), reviews 1 day.

### W2. Documents: registers, the commitment-map format and the three-document pilot

**Goal.** Turn a whole document into a map of commitments: each source sentence is a unit that is either checked
content or a labelled judgement call, with a measured coverage table that is re-run after every merge.

**Deliverables.** Document format `ve-document@1` (`.ve.md`: JSON frontmatter with environment and units,
fenced `ve` blocks, prose between them meaning nothing). Unit kinds and schema (below). CLI `ve document
check|render|coverage`. English rendering of units ("According to the Fed's statement, ..."; "Reuters infers
that ..."). `ve assist` roles mapped to unit kinds; tool `add_unit`. Pilot: US Constitution Art. I s7
(clauses 1-3), one Claude-constitution section (a norm-heavy one: hard constraints or corrigibility), the
existing Reuters Fed article; each as `usecases/<doc>/commitments.ve.md` with `coverage.json`.
`tools/coverage_dashboard.py` writing the ROADMAP table. Blind cross-family fidelity audit of the pilot.

**Semantics sketch.** Registers are metadata, not operators:

```text
unit := span + kind + content, where content is a checked VE formula or `opaque`
kind ∈ asserted | norm (W1) | definition (W3)                      checked
      | attributed(agent, act ∈ {says, promised, believes, intends, expects, denies})
      | hedged(modality ∈ {could, likely, generally, typically, effectively})
      | causal(cause, effect, kind ∈ {because, in order to, prevents})
      | evaluative(predicate, decided_by, evidence)                 open texture, named decider
      | evidential(records)                                         reserved for the evidence layer schema (§2.1 of the design)
      | unformalised(reason code)                                   NO
```

The content of an attributed or hedged unit is quoted by `meaning_id`: the checker verifies the quoted formula is
the displayed one, and never infers content from attribution. Using such content in a deduction needs an explicit
*bridge leaf* ("accept the Fed's statement as true"), which is a labelled judgement. Coverage metric per document:
formalised = asserted/norm/definition with DIRECT or REIFIED content; labelled = attributed/hedged/causal/
evaluative/evidential/opaque; NO = unformalised, each with its reason.

**Trusted core.** None. Statement review of the unit schema and of the quoting rule (identity of content bound
into the unit). Bridge leaves appear in the argument graph as ordinary assumptions with a `register` field.

**Depends on / conflicts.** P0. Baseline pilot uses today's language and starts immediately; re-measured after
W1, W3, W4, W5, W6 merge. Touches new `ve/document.py`, `ve/surface/registers.py`, `ve/assist/*` (owner),
`usecases/*` (new directories), `tools/`. Low conflict.

**Acceptance.** (1) Schema validation and identity tests. (2) Three documents with unit tables; at least 90% of
source sentences assigned a unit kind, the NO residue listed with reason codes. (3) Every attributed/hedged
content parses and type-checks; a deduction that uses attributed content without a bridge leaf is rejected.
(4) Baseline coverage table today, then after each merge, with a second rater (Astra) on the labels and the
agreement rate reported (E0's single-rater caveat). (5) Blind fidelity audit: Astra reads the English rendering
against the source; disagreement rate is a headline number. (6) `ve assist` authors a unit end to end.

**Effort and model.** M-L: format, CLI, rendering 3 days (Sol); pilot authoring 3-4 days (Opus 5.5 with
`ve assist`, no paid API); write-up by Codex (lead's rule); dashboard 1 day.

### W3. Definitions, lemma citation and statement-layer sugar (the Lean statement layer)

**Goal.** Name a property once and use it everywhere; cite a certified theorem by `meaning_id` in a later
argument; write `iff` and "every point that is prime". Closes math gaps G4, G7, G8 and the constitution's
name-versus-content gap.

**Deliverables.** Profile `definitions@0`: vocabulary entry `{"defined": {"arguments": [...], "body": AST}}`;
strict `define p(x) as (φ).`; English "call a point prime if ...". Lemma bundles: a DAG of
`(environment_id, premises, conclusion, certificate)` with a `cite` premise form; `ve bundle check`; English
"by Theorem 3". Sugar `iff`, "every s x that is P", "no s is P" (input-only). Lean: conservativity, optional
`define-unfold@0` rule, and the extended claim-graph theorem. Math mini-paper re-run.

**Semantics sketch.**

```text
definition p(x̄) := φ(x̄)     p new; φ over earlier symbols only (acyclic order); no recursion; closed under x̄
Σ+D structures := those satisfying ∀x̄. p(x̄) ↔ φ(x̄); elaboration = these biconditionals as implicit premises
conservativity: every Σ-structure expands uniquely to Σ+D, so Σ+D ⊨ ψ iff Σ ⊨ ψ for ψ over Σ
citation: a deduction may add lemma L's conclusion iff L is in the same bundle, strictly earlier in the DAG, has the
          same environment_id, and every hypothesis of L is among the citing deduction's premises or itself cited;
          the whole bundle is re-checked in one Lean run; soundness is cut (entails_cut) through the claim-graph theorem
```

**Trusted core.** Checker unchanged if definitions stay implicit premises. New Lean: `Definitions.expand` and
`conservative`; `unfold_sound` only if the optimisation rule is added (then a checker version bump, W4's
checker); `ClaimGraph` theorem generalised over the closure and order checkers (today proved for v0 only, see
`lean/CLOSURE.md`: "extended claim-graph theorem remains open"). Statement review of the citation rule.

**Depends on / conflicts.** P0 (`Environment.axioms`). Touches `ve/environment.py` (definitions entry: shared
hunk with W5 flags and W4 arity, merge order in §5), `ve/definitions.py`, `ve/argument.py` (bundle/cite),
`ve/surface/definitions.py`, `lean/VE/Definitions.lean`, `lean/VE/ClaimGraph*.lean`, `usecases/math-mini-paper`.

**Acceptance.** (1) `conservative` audited; a definition mentioning its own symbol, a later symbol or a free
variable is rejected in Python and Lean. (2) Math paper: D2-D5 become definitions, T7 is certified by citing
T7a and T7b; certified count rises from 15/19 to at least 17/19; C1 stays honestly uncertified. (3) Forged
citations rejected by both checkers: lemma absent from the bundle, hypothesis not on the branch, other
environment, cyclic bundle. (4) Definition bodies change `environment_id`; existing fixtures unchanged.
(5) 1,000 sugar round trips; canonical strict text of expanded forms unchanged. (6) Constitution: the four
property definitions connect `@safety` etc. to their content, and the priority rule uses them.

**Effort and model.** M-L: Python 3 days (Sol); Lean 3-5 days (Opus 5.5).

### W4. Unified core checker: n-ary atoms, then closure and order in one checker

**Goal.** Predicates of any arity, and one checker that a single document can use with closure, arithmetic and
n-ary atoms together. Today closure and order are incompatible and each new construct would need three proofs.

**Deliverables.** Profile `nary@0` with `Atom(p, [t1..tk])`, `k ≤ 6`, wire `["atom", p, [terms]]`, strict
`p(t1, ..., tk)` for `k ≥ 3` (forms for k = 1, 2 unchanged), English templates with k placeholders and the
generalised lint. Lean `lean/VE/Core/*`: stage 1 = the closure checker plus n-ary atoms as
`ve-tableau-core-checker@1` accepting `{relational-fol@0, closure@0, nary@0}`; stage 2 = Farkas rules and
integer quantifiers ported from the order checker after numbers2 merges, accepting `order@0` too. Conservativity
embeddings of v0, closure and order. Python evaluation, search, printer, parser; Rust parity; conformance
generator. FOLIO and constitution witnesses.

**Semantics sketch.** Signatures become sort lists; relation extensions are sets of k-tuples; equality congruence
substitutes per position; finite models supply k-tuples. Unary and Binary embed as length-1 and length-2 atoms
(theorem, not convention). Everything else (quantifiers, closure over binary homogeneous edges, arithmetic) is
unchanged.

**Trusted core.** The largest change of the round. New checker and route only; the four original v0 files, the
closure checker and the order checker stay byte-identical with their theorem statements. New theorems:
`Core.eval_iff_denote`, `check_iff_wellFormed`, `Tableau.checkCertificate_sound` (stage 1 and 2),
`entails_v0`, `entails_closure`, `entails_order`, route gates. Statement review of the unified `Entails`.

**Depends on / conflicts.** P0. Stage 2 waits for numbers2 (order Lean files). Touches `ve/ast.py` (Atom),
`ve/environment.py` (arity), `ve/evaluate.py`, `ve/search.py`, `ve/model.py`, `ve/entailment.py` (route),
`ve/surface/nary.py`, `lean/VE/Core/*`, `rust/ve-core/src/*`. Conflicts: `ve/ast.py` with W6 (W6 starts
later), `ve/environment.py` with W3 and W5, Rust with numbers2 then W5 (serialised in §5).

**Acceptance.** (1) Audit passes; old checker files unchanged (test compares hashes). (2) At least 500 generated
n-ary certificates accepted by Python and Lean; at least 2,000 mutations rejected by both, including argument
permutations `p(a,b,c)` vs `p(b,a,c)`; zero disagreements. (3) Existing v0, closure and order corpora replay
unchanged on their own routes and also through the embeddings. (4) Rust: 5,000 fuzz pairs agree; arity-6
tables. (5) E0 mechanical re-run: FOLIO's 216 arity>2 atoms parse directly; report the new direct-fit number.
(6) Constitution `conflict(situation, property, property)` replaces the binary workaround. (7) Stage 2: a
document mixing `tc[...]` and `<` certifies; the closure × order rejection remains on the old routes.

**Effort and model.** XL: stage 1 Lean 6-8 days, stage 2 Lean 5-8 days (Opus 5.5); Python 3 days and Rust
2 days (Sol). Start day 1; it is the long pole.

### W5. Policy data: attributes, strings, sets and adapters (Cedar, Gatekeeper, K8s)

**Goal.** Say "the department of that person is finance", compare string-valued fields, and keep regex or glob
checks outside the checker but inside the audit trail. Moves Cedar's reified half toward direct fit and gives
Gatekeeper's 20 string items an honest home.

**Deliverables.** Profile `data@0`: predicate flags `functional: true` and `total: true` (attributes); built-in
sort `$string` with literals and equality only; adapter records for computed string predicates (`glob@1`,
`prefix@1`, `regex@1`: function id and version, input hashes, parameters, output table hash) with `ve adapter
run` recomputation; set conventions (`member`, optional `extensional` flag). English definite descriptions.
Cedar attribute and context translation; Gatekeeper `is_exempt` end to end; new use cases `usecases/cedar-*`,
`usecases/gatekeeper-*`.

**Semantics sketch.**

```text
functional r : (s1,s2)   adds  ∀x∀y∀z. r(x,y) ∧ r(x,z) → y = z        total adds  ∀x∃y. r(x,y)      (implicit premises, identity-bound)
"the r of t is P"        sugar only when functional ∧ total:  ∃y. r(t,y) ∧ P(y)   (≡ ∀y. r(t,y) → P(y) under the axioms; otherwise the author writes the quantifier)
$string literals         denote themselves; distinct literals are distinct; no operations, no order
literal distinctness     stage 1: implicit premises ¬(l1 = l2) for each pair of literals in the query (n ≤ 64), proved true in every structure;
                         stage 2: a `string-distinct` close rule in the W4 checker
adapter table            a relation in the model plus a record; VE checks formulas over the table, never the regex; entailment over
                         adapter predicates without a table is UNKNOWN
```

**Trusted core.** Checker unchanged in stage 1. Lean: `$string` in the decoder of the W4 checker (stage 2),
`literals_distinct` (as `numerals_distinct`), and a theorem that a finite model passing the functional/total
table check satisfies the generated axioms. Statement review of the adapter record schema (provenance only).

**Depends on / conflicts.** P0. Stage 2 needs W4 stage 1. Cedar acceptance needs W1 for permit/forbid
decisions (attributes alone are tested by evaluation). Touches `ve/environment.py` (flags, `$string`: shared
with W3, W4), `ve/model.py`, `ve/adapters.py`, `ve/surface/data.py`, `rust/ve-core/src/*` (after W4).

**Acceptance.** (1) Non-functional or partial tables are rejected as invalid models; the generated axioms are
in `Environment.axioms()` and change `environment_id`. (2) 1,000 English round trips with definite descriptions;
"the r of t" is refused for non-total attributes with a diagnostic. (3) Cedar: of the 143 policies, report
DIRECT/REIFIED after W5 (E0 baseline 15/14) and, with W1, decisions matching the authorizer. (4) Gatekeeper: the
20 string items run with adapter tables; a tampered input hash or table hash is rejected; entailment over
`prefix_of` without a table returns UNKNOWN. (5) Existing fixtures unchanged.

**Effort and model.** M: Python and adapters 4 days (Sol); Lean 1-2 days (Opus 5.5); use cases 2 days.

### W6. Quantities in documents: time, events and counting on top of order@0

**Goal.** "On 16 September 2026", "within ten days, Sundays excepted", "16 of the 18 policymakers", "two thirds of
the members present" as checked statements, with entailment honest about what it cannot decide.

**Deliverables.** Date literals (ISO date to day number, proleptic Gregorian) with a display unit on integer
positions; temporal wordings ("on", "before", "after", "within n days of", "no later than"); event-sort and
time-indexed relation conventions (`occurs_at(e, t)`, with W4: `value(signal, t, v)`); FRET-style `always`/
`eventually` over finite traces as quantification over time points. Counting: sugar "at least/exactly n s are
P" for literal `n ≤ 8` (expansion with distinctness, certifiable) and profile `count@0` with a term
`count(s x | φ)` for evaluation only. Re-rated news article and FRET sample; Art. I s7 timing clause.

**Semantics sketch.**

```text
date(2026-09-16)  ↦  Num(20712)   the AST holds the integer; the unit is identity-bound display metadata like verbalisation
"within n days of d": d ≤ t ∧ t ≤ d + n;   "Sunday": ∃q. d = 7q + k   (linear arithmetic with integer quantifiers, from numbers2)
at least n s x, φ   ↦  ∃x1..xn (distinct ∧ φ(xi))                                        Lean: expand_atLeast_iff
count(s x | φ) ⋈ t  evaluation only: |{d ∈ D_s : φ(d)}| ⋈ t on finite models; certificate, countermodel and compare routes reject it
```

**Trusted core.** Checker unchanged. Lean: `expand_atLeast_iff` (finite and general structures), `count@0`
evaluator extension of P6 for finite models only, date conversion mirrored and tested (or a small Lean
`dayNumber` with monotonicity). Statement review: "evaluation only" gate for `count@0`.

**Depends on / conflicts.** numbers2 merged (integer quantifiers); W4 stage 1 for time-indexed n-ary relations;
W5 adapters optional for calendars. Touches `ve/ast.py` (Count, after W4), `ve/surface/time.py`,
`ve/surface/count.py`, `ve/evaluate.py`, `lean/VE/Order/*` or `lean/VE/Core/*` evaluator, `usecases/news-article`.
Starts after numbers2 merges; date and wording work can start on the surface registry earlier.

**Acceptance.** (1) News rows 7, 7b, 8, 21, 22, 22b, 23 become DIRECT or REIFIED with numbers and counting.
(2) FRET: the 30 sampled items re-rated with time-indexed relations and integer time; real-valued items stay NO
and are said to. (3) Art. I s7 "ten days, Sundays excepted" formalised with a checked countermodel for a bill
returned on day 11. (4) No certificate is produced or accepted for a formula containing `count`; the sugar
expansion certifies. (5) Date conversion agrees with Python's `datetime` on 10,000 dates; English round trips.

**Effort and model.** M: 4-5 days total (Sol for Python and wordings, Opus 5.5 for the Lean evaluator).

### W7. English surface: Lean round-trip proof and the grammar extension discipline

**Goal.** The sentence the author signs is provably the formula the checker checks: `parse (render A) = A` and
renderer injectivity for the English surface, in Lean, plus a rule that every later surface construct carries
its own production and lemma.

**Deliverables.** `lean/VE/English/*`: an abstract lexicon (templates as token lists with placeholder positions,
sort nouns, constants), `render` and `parse` mirroring `ve/english.py` for the core fragment (declarations,
first/second and labelled references, connectives with `(a)/(b)/(i)/(ii)` lists, negation fallback, relative
guards with one to three atoms, existentials, equality, closure phrases); theorems `parse_render`,
`render_injective`, `unique_derivation` for the Lean grammar; a differential test that the Lean parser agrees with
Python on the 85,000-pair corpus and the 8,500 all-derivations texts; `docs/english-surface.md` section
"Extension discipline": every new surface construct is keyword-led with a disjoint prefix and ships a production
plus lemma, or is labelled "unproved surface" in the legend.

**Semantics sketch.** Structural induction as sketched in `docs/english-surface.md`: disjoint prefixes recover
the constructor, marker arity recovers association, the finite lexicon identifies predicate and argument order,
declarations and unique references invert the scope stack, each contracted guard has one inverse.

**Trusted core.** Surface only; no checker change. The theorem is about the Lean model of the grammar; the
differential test is the evidence that Python implements the same grammar. Statement review of the lexicon
abstraction (what a template may contain).

**Depends on / conflicts.** None to start (core skeleton). Full coverage after W1, W3, W5, W6 wordings merge;
each of those must add its production and lemma under the discipline. Touches `lean/VE/English/*`,
`conformance/english_lean.py`, `docs/english-surface.md` (owner; others append sections).

**Acceptance.** (1) Theorems audited. (2) Differential agreement on the full corpus with zero mismatches.
(3) Every merged workstream's wording is either covered by a lemma or labelled in the legend. (4) Human
readability is still unmeasured and is stated as such.

**Effort and model.** L-XL: 8-10 days (Opus 5.5).

## 5. Dependencies, conflicts and merge order

| | P0 | numbers2 | W1 | W2 | W3 | W4 | W5 | W6 | W7 |
|---|---|---|---|---|---|---|---|---|---|
| depends on | - | - | P0; W3 optional | P0 | P0 | P0; numbers2 for stage 2 | P0; W4.1 for stage 2; W1 for Cedar decisions | numbers2; W4.1 | none; wordings from W1/W3/W5/W6 later |
| shared files | all | `lean/VE/Order`, `ve/order.py`, `rust` | `ve/assist` (with W2) | `ve/assist` (owner), `usecases` | `ve/environment.py`, `ve/argument.py` | `ve/ast.py`, `ve/environment.py`, `ve/entailment.py`, `rust` | `ve/environment.py`, `ve/model.py`, `rust` | `ve/ast.py`, `ve/evaluate.py` | `docs/english-surface.md` (owner) |

Hotspots and rule: `ve/environment.py` (W3, W4, W5) and `rust/` (numbers2, W4, W5) are merged in this order:
**P0 → W2 baseline (docs only) → W5 stage 1 → W3 → W1 → numbers2 → W4.1 → W6 → W4.2 → W5 stage 2 → W7**.
W7 may merge earlier for the core skeleton. Surface modules under `ve/surface/` and Lean directories are
disjoint per workstream, so branches rebase cleanly. One integration agent merges; each merge re-runs the full
suite, `lean/audit.py`, Rust conformance and the W2 coverage dashboard.

## 6. Start plan

Start now in parallel after P0 (no conflicts): **W1** (Sol + Opus), **W2** (Sol, then Opus for authoring),
**W3** (Opus + Sol), **W4 stage 1** (Opus), **W5 stage 1** (Sol), **W7** (Opus). **W6** starts when numbers2
merges. Seven agents at peak; Lean-heavy work on the three Claude accounts (Opus 5.5), Python/Rust on Codex
(GPT-6 Sol). Reviews: Astra + Fable xhigh on each spec section before build, cross-family review before merge.
No paid API calls: the pilot uses `ve assist` through the claude CLI and Codex for audits. Wall clock about
three weeks for W1-W3, W5, W6; W4.2 and W7 four to five weeks.

## 7. Out of scope this round (recorded, not forgotten)

Modal or Kripke semantics for belief and possibility (attitudes are registers; upgrade only if inference across
attitudes is needed); default logic as a consequence relation ("normally" beyond static exception trees); real
numbers, units and dimensional analysis; metric-time LTL beyond finite traces; probability inside formulas (the
evidence layer stays an assessment layer over W2's `evidential` units); second-order sets and comprehension
(schematic relation parameters are already expressible with a fresh symbol); general arithmetic induction;
open-vocabulary parsing (reviewed out on 2026-09-21); human readability studies (deferred by the lead).

## 8. After review

To be filled with the Astra and Fable verdicts; the adopted version of this section is binding.
