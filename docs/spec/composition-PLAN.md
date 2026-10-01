# Feature composition: plan (one stack for references, readings and norms)

> Status: planning draft 2 (2026-10-01), design only: no code, Lean or frozen contract changes. Draft 2 applies the
> converged Astra + Fable design debate and nothing else (`manage-agents/debates/design-compose/{astra,fable}.md`,
> CONVERGED after round 3; the Astra seat was held in all three rounds by Sol xhigh as the recorded cross-family
> stand-in): REVISE draft 1 into draft 2, then BUILD through statement review with no second design debate.
> Section 10 maps each converged edit to its change. The statement specification of the stack contract and of stage
> S0 is [composition.md](composition.md). Its statement review converged on FIX after round 3
> (`manage-agents/debates/compose-spec/{astra,fable}.md`, the Astra seat again held by Sol xhigh) and amended this
> plan in one respect, the label of a gated relation premise (2.3, 2.7), with pointers in sections 3, 4 (S0's
> acceptance) and 9; nothing else changed (change log). Baseline `main` at
> `2205be39`. Trigger: ARCH-ROADMAP "P1 FEATURE COMPOSITION" and the UDHR-audit feature list
> (`manage-agents/ARCH-ROADMAP.md`, entries of 2026-09-30T06), from the pilots
> `manage-agents/pilots/{claude-constitution,udhr}/run-20260930T{0600,1800}Z` (`FEATURE-REVIEW.md`, `AUDIT.md`,
> `metrics.json`; cited `C:` and `U:`). Inputs read: [document.md](document.md) (W2), [norms.md](norms.md) (W1),
> [soft-norms.md](soft-norms.md), [rights.md](rights.md) with [rights-PY-STATUS.md](rights-PY-STATUS.md),
> [discourse.md](discourse.md), [speech-acts.md](speech-acts.md), [attribution.md](attribution.md),
> [alternatives.md](alternatives.md) with [causation-PLAN.md](causation-PLAN.md), [risk.md](risk.md),
> [units-schema.md](units-schema.md), [INTEGRATION-GAPS.md](../INTEGRATION-GAPS.md), `ve/readings.py`,
> `ve/profiles.py`, `lean/VE/Route/{Layer,Readings}.lean`, `lean/VE/Rights/*`, `lean/VE/Discourse/*`.
> `norm-defaults@0` is **not merged** (branch `design/norm-defaults`, `860d3077`, spec draft 1); section 2.9 keeps
> this plan compatible with it. Theorem statements below are obligations for an item-1 specification and its
> Astra + Fable statement review (PLAN-EXPAND2 rule 10), not claims of proofs. No coverage number is predicted:
> section 6 lists which measured blockers each stage removes, and only a rerun measures a gain.

## 0. Summary

Every merged feature is a wrapper with its own route, and the wrappers were never given one order. Rights sits on
soft norms, which sits on norms, which sits on the frozen route; discourse and reading sets each sit directly on the
frozen route and so see neither norm content nor each other. The four pilot failures are four faces of that.

The plan fixes one order, **the stack**, and one owner per concern:

```text
source bytes + front matter
  1 RESOLVE     ve.discourse@1     owns references   every formula position of every content becomes closed
  2 STRUCTURE   right-clauses@0    owns line shape   clauses and the bearer–holder relation become guard conjuncts
  3 SUPERPOSE   readings@1         owns readings     all candidates in one document, each behind its choice atom
  4 CHAIN       rights@0 → soft-norms@0 → [norm-defaults@0] → norms@0     owns norms (unchanged, reused)
  5 CHECK       relational-fol@0   frozen route: certificates and finite models
```

Each step is a total function regenerated at every trusted site, each has an identity theorem when its input uses
nothing of it, and each hands its successor an ordinary document of the successor's existing kind. The one new idea
is step 3: a reading set over norms or rights is checked as **one superposed document** in which candidate `i` of
set `s` is guarded by generated choice atoms that spell exactly one candidate per set. That gives the
candidates one vocabulary (so a strict and a defeasible candidate share a situation), makes limitations, the bar and
"this right includes" apply to every candidate without enumeration, and turns "under every reading" into one
certificate instead of a product of documents (the pilots' reading plans are over the 64-choice budget on both
texts). Two new profiles (`readings@1`, `right-clauses@0`), no new logic, no change to a frozen file.

Stages, in order of measured unlock (section 6): S0 the base-premise slot, the dispatcher and the shared candidate
content type (enabler); S1 content-bearing norm candidates with Lean-checked separating situations; S2a superposed
verdicts for soft documents; S2b the same for rights documents, which stay on the enumerated fallback until the
rights case of `superpose_faithful`, bar case included, is proved; S3 structured right lines; S4 discourse on the
chain. S3 and S4 depend on S0 only.

## 1. The four failures and their causes

| # | Pilot evidence | Cause at `2205be39` |
|---|---|---|
| 1 | `ve.discourse@1` with the constitution translation: `UnsupportedProfile: Unsupported profile soft-norms@0`; on the norms-only variant `fields do not match: … got [arguments, description, regulated]`; `UnrecordedSlot: u0078.s01: [48274, 48278)`; `u0214.s02` fails four ways (C: `FEATURE-REVIEW.md`, `discourse_probe`) | The discourse wrapper strips its profile and calls the **frozen** gate and decoder (discourse 3.5), which know no norm profile; its loader answers `NotImplemented` for norm content, fenced content and a document without a claim graph (discourse 11). Discourse 5 specifies the norm composition; nothing implements it. Slot discovery reads the prose bytes of every unit with meaning, which a translated norm unit cannot satisfy |
| 2 | Force readings: "a situation is accepted only for the candidate it was built for" (C: `rights_reading_probe`, `u0156.s03`); 14 constitution sets keep placeholder models and two companion documents; U: 43 units, 4,175 bytes (38%) `force_variants_in_one_reading_set` | (a) A candidate of kind `norm` has `content: null`: `ve/readings.py` identifies only formulas, quantities and `{"right": …}`. (b) `_right_situation` builds its model over the candidate's **own** regenerated base vocabulary; a default rule adds `soft__excepted__<rule>` and a strict one does not, and a finite model must list exactly the base predicates |
| 3 | U audits: Art. 8, 10 scope lost; Art. 11(1), 12, 21(2) weakened or strengthened; Art. 15(1) "every state must grant"; `u076`, `u108` blocked on `act_phrase_grammar` | A line is one rule `∀ bearer ∀ holder` whose content beyond the guard lives in an 80-character act phrase (norms 2.4) or in a sort's prose description. No field ties a clause to its source bytes, and no relation says *which* bearer owes a holder |
| 4 | U: `limitation_terms: 0` (`u111` inert), `right_lines` units `u067`, `u068`, `u071a`, `u071b` blocked, `rights_report: UNKNOWN: per-choice rights elaboration pending`; premises UNKNOWN on both texts | rights 6.3 specifies per-choice elaboration; it is not built (rights-PY-STATUS). A limitation's scope ranges over rights fixed in the document, and every right of the translation is a candidate. Enumeration could not rescue it: both reading plans exceed 64 choices at the first few sets |

One correction to the roadmap entry, from the pilot's own review: the constitution's 80 `other:discourse` units are
14 heading titles, 2 connectives and 64 list lead-ins, list items and sentences built on "such", "these", "it"; the
review expects none of them to change status from reference resolution alone. Failure 1 is real (a norm and a
resolved reference cannot share a document) but its measured unlock is the smallest of the four (section 6).

## 2. The composition model

### 2.1 The stack and what each layer owns

| Concern | Owner | Consumes | Produces | Identity case |
|---|---|---|---|---|
| References (names, pronouns, descriptions, section, rule and document references) | `ve.discourse@1` | source, manifest, every content with slots | the same document with every formula position closed; uniqueness premises as W2 units (discourse 4.5) | no formula-producing mention: contents unchanged |
| Line shape (scope, trigger and object clauses; bearer–holder relation) | `right-clauses@0` | right lines with `clauses`, `relation` | `rights@0` lines with larger guards; relation premises `Rel_D` (gated by its atom when the line is a candidate's, 2.3) | no clause, no relation: the line unchanged |
| Readings (which candidate each unit takes; couplings, constraints, narrowings) | `readings@1` | fixed units, reading sets with content | one reading-free document `sup D`; choice premises `Choice_D` | no reading set: `sup D = D` and `Choice_D` is empty (`sup_no_sets`). A document whose sets are all formula-only is not superposed: it keeps W2's route verbatim (2.5) |
| Holders, incidents, limitations, the bar | `rights@0` | rights document | soft document; `Lim_D` | rights 9.2 `correlate_identity_top` |
| Force, exceptions, switches, ranks | `soft-norms@0` | soft document | W1 tree; `Soft_T` | soft-norms 5.1 (all rules hard: `T′ = T`) |
| Silence (unmerged) | `norm-defaults@0` | W1 tree with `unspecified` | W1 tree; `Fill_T` | no unspecified predicate |
| Applicability, completion, conflict | `norms@0` | W1 tree | layer premises `elab_p` | no regulated predicate |
| Truth, proof, countermodels | frozen route | premises, conclusion | certificate or finite model | — |

Rules of the stack (the contract a layer signs to be placed in it):

1. **One position.** A profile has one rank in the order above. A wrapper validates and strips its own profile,
   then calls `dispatch` on the remaining profiles (S0), never a specific route. `dispatch` returns today's route
   on every list that has one, and today's diagnostic on every list today's gate rejects: the `alternatives@0`,
   `risk@0` and `speech-acts@0` lists contain `norms@0` and keep their own routes, and so does `reports@0`. On a
   validated chain list it returns the head of the stack. Its error branch is new only for a combination outside
   both (rule 6).
2. **Source in, same kind out.** A layer's output is a document its successor already accepts. No layer reads a
   later layer's generated vocabulary, and later layers never see an earlier layer's constructs, with **one stated
   exception**: the quiescence premises of `Choice_D` (2.3) name predicates the chain generates on `sup D`
   (`soft__excepted__…`, `soft__off__…`, `soft__outweighs__…` and the positional `rights__lim__<k>`,
   `rights__cond__<k>`, `rights__bar__<k>`). They are computed by the chain's own naming functions after these have
   run on `sup D`, and are regenerated with them (rule 3). Source-level gating cannot replace them: a limitation's
   conditions are named predicates per act (rights 1.3), not formulas a guard could be conjoined to, and the bar's
   node is generated by `correlate` without a guard.
3. **Regenerated, never trusted.** Every derived object (resolved contents, `sup D`, `Choice_D`, `E″`, `T′`, layers)
   is recomputed from the decoded document at every trusted site and bound to the document hash; none is on the wire
   as authority.
4. **Premises only through slots.** A layer may add closed formulas over the base vocabulary to base admissibility
   (as `Soft_T` and `Lim_D` do). They are labelled, listed in `conditional_on` when used, and enter through one
   generic lemma (S0), so a new layer restates no route theorem. The combined slot of the full stack is
   `Lim_D ++ Choice_D ++ gated Rel_D`, each formula with its label (2.3, 2.7); a premise a candidate brings enters
   gated by that candidate's atom, so that under each compatible choice the slot's models are that choice's models.
5. **Identity when unused**, as a Lean theorem, so every existing document keeps its bytes, identities and verdicts.
6. **Abstention is named.** A combination outside both today's lists and the validated chain is
   `UnsupportedProfile: <a> with <b>`, never a silent drop of a block (INTEGRATION-GAPS's rule). A list today's gate
   rejects keeps today's diagnostic.

The order is forced, not chosen. References must close before readings, because a candidate is an admitted content
(discourse 2.4: "a reading set holds admitted formulas only") and its meaning identity is that of the closed
content. Clauses come before superposition because both only conjoin guards and the clause is the author's.
Readings come before the chain because the chain's elaborations (`correlate`, `soften`) are frozen functions of a
whole document, and the only way to give them every candidate at once is to hand them one document.

### 2.2 Candidates carry content

Under `readings@1` a candidate's `content` is one of the existing unit contents, in the existing wire form:

```text
formula | {"quantity": …}            as today (W2, W6)
{"norm": {…}}                        a soft norm object (soft-norms 3.2; norms 3.2 when soft is off)
{"right": {…}} | {"right_lines": …}  rights 3.2            (requires rights@0)
{"limitation": {…}}                  rights 3.2            (requires rights@0)
{"bar": {…}}                         rights 3.2            (requires rights@0; enumerated, 2.6)
```

Its `meaning_id` is W1's digest over `{environment_id, ast: content}` (norms 11.2, rights 3.5), so a candidate and
the same content as a fixed unit have one identity. `labels` are allowed on every candidate and `couplings` on
every labelled set (today both need `rights@0`), so the constitution's fourteen force sets can be coupled on
`force` exactly as the UDHR's are. A candidate with `content: null` stays what it is today: pending, and every
verdict that needs it UNKNOWN. A set may mix kinds (`rs_u114`: a norm and an assertion; `u054`: a right and an
assertion): a candidate is a content, and the unit takes the kind of the candidate chosen.

Admission conditions on a set, checked per candidate in the context of the fixed units, so linear in candidates,
plus one check across sets:

- **Closure.** A candidate names (in `over`, `cites`, `scope`, `right_lines.right`) only fixed names or names it
  declares. A fixed unit may name something a set declares only if every candidate of that set declares it
  (`ReadingInterface: <set>: <name>` otherwise); such a name is an **interface name** of the set, and 2.3 maps the
  fixed reference to every qualified copy. So `Right 18 includes: …` is admissible exactly when every
  candidate of `rs_u066` declares right 18.
- **Distinct declarations across sets.** Every name a candidate declares (a rule, right or limitation name) is
  distinct from every fixed name of its kind and from every name declared by a candidate of another set
  (`DuplicateDeclaration: <name> in reading sets <s> and <t>`). Candidates of one set may share a name: that is
  the interface. The check runs once over all active sets, because per-candidate admission never sees two sets
  together, and it is a precondition of `choice_wellFormed` (S2): without it a compatible choice could select two
  candidates that declare the same name.
- **Each candidate elaborates.** Fixed units plus the candidate pass the chain's well-formedness
  (`WellFormedRights`, hence `WellFormedSoft` and W1's). A default candidate that takes precedence over a hard
  fixed rule is `SoftOverHard` there, reported with the reading named.
- **Separation** (2.4) for every pair of candidates.

### 2.3 The superposed document

For a document `D` with fixed units `F`, active sets `R_1 … R_n` and candidates `a_{s,i}`:

```text
choice vocabulary   one fresh sort ve__reading with one constant ve__here; for the n-th set (source order) with k
                    candidates, ⌈log₂ k⌉ unary base predicates ve__bit__<n>__<j> over ve__reading.
                    χ_{s,i} := the conjunction of the set's bit literals at ve__here that spells i in binary
                    ("candidate i of s is chosen"); a two-candidate set has one bit: χ_{s,0} = ¬b, χ_{s,1} = b.
                    Every structure spells exactly one pattern per set, so "exactly one candidate" needs no
                    distinctness premise and no constant per candidate.
sup D               one rule: sup gates everything a candidate owns or causes, namely its guards, its exception
                    conditions, the predicates generated for it, the premises it brings and the nodes generated
                    because of it.
                    F unchanged, except that an over or cites entry of a fixed rule (like a limitation scope or a
                    right_lines target) that names an interface name of a set (2.2) names every qualified copy of
                    it; then for every candidate a_{s,i} (k its position in the canonical order: sets in source
                    order, candidates by index):
  formula φ           the assertion  χ_{s,i} → φ
  norm N              N with name q(N) (candidate-qualified, reserved prefix rd-<k>-), guard G_N ∧ χ_{s,i}, every
                      sufficient exception condition C replaced by C ∧ χ_{s,i}; over, cites mapped through q
  right R             R with name q(R); every line's norm (both units of a power) as above; holder guard unchanged
  right_lines         lines as above, attached to q(R); a fixed right_lines unit on a set-declared right is copied
                      once per candidate of that set, each copy guarded by that candidate's atom
  limitation L        L with name q(L); a scope naming a set-declared right names all its copies
Choice_D            base premises, slot `readings`, regenerated, never on the wire:
  unused patterns     ¬(pattern) for every bit pattern of a set that spells no candidate (none when k is a
                      power of two)                                                      readings:<set>@<v>:one
  couplings           ¬(χ_{s,i} ∧ χ_{t,j}) for s, t consecutive in the coupling's list and candidates i, j that
                      differ on the axis (equality of labels is transitive, so a chain suffices)   coupling:<id>
  constraints         discourse 1.5: requires χ_a → χ_b; excludes ¬(χ_a ∧ χ_b)            constraint:<n>
  narrowings          ¬χ_{s,i} for every reading a recorded narrowing drops               narrowing:<id>
  quiescence          ∀x̄. g(x̄) → ⋁ χ(owners(g)) for every predicate g generated on sup D that the document of some
                      compatible choice lacks. owners(g): the candidates whose choice puts g into the choice's
                      document. A disjunct is one atom, or the conjunction of the atoms of candidates of different
                      sets that generate g only together (a candidate limitation and a candidate line in its
                      scope; two candidate default rules whose collision generates an outweighs predicate).
                      Covered: a candidate rule's soft__excepted__…, soft__off__…; soft__outweighs__…; the
                      rights__lim__…, rights__cond__… of a candidate limitation, or of a fixed limitation on an act
                      only candidate lines have; and the bar's rights__bar__… (aimed_m) when the permission
                      predicate m is right-derived only through candidate liberties. No premise for a g that the
                      fixed units alone generate.
                                      readings:<set>@<v>:<i>:quiet (one owner), readings:quiet:<source key of g>
Rel_D, gated        a totality premise ρ of a relation (2.7) on a line of candidate a_{s,i} enters the slot as
                    χ_{s,i} → ρ, under the label rights:relation:<line>:total under <set>@<v>:<i>, which names the
                    reading: candidates of one set may share a line name (2.2), and slot labels are pairwise
                    distinct. A fixed line's ρ enters as it is, under rights:relation:<line>:total
combined slot       slotP D := Lim_D ++ Choice_D ++ gated Rel_D, in this order, each formula with its label:
                    rights:limitation:… | readings:…, coupling:…, constraint:…, narrowing:… |
                    rights:relation:<line>:total[ under <set>@<v>:<i>]. conditional_on lists these labels
                    verbatim. Model correspondence, per compatible choice c: the base
                    structures of sup D satisfying the slot in which exactly c's atoms hold are, up to the name
                    map and the choice vocabulary, the base structures of c's own document (base_down, base_up, S2)
```

Names beginning `ve__` (sorts, constants, predicates) and rule, right and limitation names beginning `rd-` are
rejected in author input under the profile (`InvalidInput`), as `soft__` and `rights-` are. Nothing generated is
shown to a reader: reports say "sentence 12 read as *must*", never an atom. The cost in vocabulary is one sort, one
constant, one predicate per two-way set and up to three per five-way set, beside the decision predicates the chain
already generates per default rule. Whether the UDHR after S1 stays inside the 256-predicate limit is measured in
S2's acceptance, not assumed.

Why this is the per-choice semantics. Fix a complete choice `c` satisfying couplings, constraints and narrowings,
and let `choiceDoc D c` be the ordinary document: fixed units plus the chosen contents under their own names (what
rights 6.3 calls a complete choice elaborated separately). In any base structure where exactly the atoms of `c`
hold, a rule of an unchosen candidate has a false guard: it never applies, so it never selects, never yields above
its parents except through chosen children (closure forbids those), never blocks a default rule and is never
eligible to dominate one. Quiescence empties its decision tables, the gated sufficient conditions make its
exception premises hold, and an unchosen limitation's predicates are empty, so its packed carve-out is false. A
node generated because of an unchosen candidate is silenced the same way, and `correlate` is not touched: a fixed
bar's node on `m` is strict and guarded only by `aimed_m`, and exists in `sup D` as soon as any candidate has a
liberty on `m`; under a choice without such a liberty quiescence empties `aimed_m`, so the node never applies,
which is what that choice's document says by having no such node (F21). A premise an unchosen candidate brings is
implied by its false atom. What
remains is `choiceDoc D c` with renamed generated predicates. `superpose_faithful` (S2) states exactly this, and its
two corollaries carry proofs and countermodels across: a base structure of `sup D` satisfying `Choice_D` **is** a
complete compatible choice together with a situation of that choice's document, and conversely.

When superposition is unavailable. The dependency order of norms 4.1(4) is computed on `sup D`; two candidates that
each stratify may form a cycle together (one guard reads regulated `q` under `p`, the other `p` under `q`). That is
`ReadingsNotSuperposable: <sets>`, and the route falls back to enumerating complete choices (at most 64, UNKNOWN
beyond, as W2 says today). Size is checked before construction (the limits contract): `sup D` holds every candidate,
and soft's unfolded carve-outs grow with colliding ranked rules.

### 2.4 Separating situations

A separating situation must be about the author's vocabulary and must not depend on how generated predicates are
named. So it has a shared part and a private part:

```text
situation        base: a finite model over the shared vocabulary: the author's base vocabulary (E_base, flags,
                 literals) and the decision, limitation and bar tables of the fixed units, keyed by source key
                 (rule; limitation, act, condition; act), so both candidates read the same fixed decisions
                 decisions: tables for the generated predicates the witnessing candidate owns, and no others
probe            the outcome of a regulated predicate at a tuple | whether some rule or line of a given kind on a
                 given predicate selects at a tuple: the key (kind, predicate, tuple), today's key
                 (`ve/readings.py`), never a rule name | (formula candidates) the candidate's own truth
Achieves(a, B, q, v)   some assignment to a's own generated predicates over B makes "fixed units + a" admissible
                       with probe q = v
Separated(a, b)        ∃ B, q, v. Achieves(a, B, q, v) ∧ ¬ Achieves(b, B, q, v), or the same with a and b exchanged
```

The checker is given `(base, decisions, probe)` for one side, evaluates it, then enumerates every assignment to
the other side's own generated predicates on the same finite base (at most 2¹² assignments, `ResourceLimit:
decision assignments` beyond, never a verdict) and requires that none reaches the same probe value. The fixed
units' decision tables are part of the base and are never enumerated: were they free, the tables of a dozen fixed
default rules would exceed the bound on every set. A probe never names a rule, so two candidates that differ only
in a rule name do not separate (F22), as S1's acceptance and `separation_conservative` require. Lean's `separates`
is the authority (`separates_sound`, S1); Python searches for the situation and Rust replays the evaluation
untrusted.

- **Force.** For `u0156.s03` the base situation has one instance of Claude and one user. Suppose the decider
  decides the exception applies there: under the defeasible candidate avoiding the deception is then not
  required; the strict candidate has no decision to make and requires it. One shared situation, checked. If a
  default candidate's exception can never
  apply (a necessary condition that is unsatisfiable), nothing separates it from the strict candidate and the set
  is rejected: the two wordings then say the same thing.
- **Finding `SeparatedByDecisionOnly`.** When every separating situation of two candidates separates them through a
  decision table of the witnessing side (the strict and the default reading of one rule agree wherever no decider
  says the exception applies), the set is admitted and the report says so. The IDE then says "suppose *the decider*
  decides the exception applies", with the declared decider named; it never says "Ruritania lacks the resources
  and the exception applies", which presents a decision as a fact. It is a report line, not an error.
  Decision-based separation is kept: demanding a sufficient condition would block the 43 units again and add no
  truth.
- **Formula sets** have no decisions; the definition is W2's rule (the two formulas differ in the model).
- **Existing right sets** whose candidates generate no predicate (every right candidate of the UDHR run) are
  accepted and rejected exactly as by today's comparison of outcomes and selected lines (`separation_conservative`).
- **Finding `SeparatedByActOnly`.** When two candidates regulate disjoint predicates and every probe that separates
  them is on a predicate only one of them regulates, the report says so in English ("these two readings are about
  different acts: *avoid denying equal protection* / *give equal protection*; no situation separates them on a
  shared act"). It is a report line, not an error. It would have flagged the label-only defects of U `u032`,
  `u033a`, `u049` that the audit found by hand.

### 2.5 Verdicts across readings

All statuses are W2's; no new status.

**Formula-only documents keep W2's route verbatim.** When every active set holds only formulas (or quantities),
nothing is superposed: ALL is one certificate from the per-unit disjunctions, NONE is one checked finite model
that satisfies every reading and refutes the conclusion, SOME is a named choice proof with a checked model under
another choice, and coupled sets enumerate, exactly as [document.md](document.md) and `ve/readings.py` do today
(`readings_all_iff`). The table below is the route for a document with at least one content-bearing norm, right or
limitation set; `superpose_assertions` (S2) relates the two routes on the formula sets of such a document.

| Question | Evidence on `sup D` | Report |
|---|---|---|
| Does φ follow under every reading? (ALL) | one certificate from `background ++ Choice_D ++ layers ++ Γ`; its used leaves name the sets it needed | `readings:<set>@<v>:all` for a set some used leaf mentions with no atom of it assumed; `readings:<set>@<v>:<i>` when an atom was assumed; nothing for a set no used leaf mentions ("does not depend on how sentence 7 is read") |
| Under a named reading? | the same with that choice's atoms as premises | the choice listed |
| SOME | a certificate under one named choice and a checked countermodel whose atoms encode another | both choices listed |
| NONE | a countermodel per compatible choice, enumerated up to 64 (a formula-only document: W2's one shared model, above) | beyond 64: `UNKNOWN (not ALL: countermodel under <choice>)` |
| Can the rules contradict each other? | W1's conflict targets on `sup D` over `Background_base ++ Choice_D`: one certificate per target covers every reading; a witness's atoms name the reading it is a conflict of | CONFLICT-FREE under every reading, conditional on the listed coherence, limitation and choice premises / CONFLICT under <choice> at <situation> / UNKNOWN |
| Are the premises consistent? | one model (a reading and a situation); then one model per candidate with its atom true | consistent under <choice>; `DeadReading: <set>:<i>` with a certificate of `¬χ_{s,i}` for a candidate no compatible choice can use |

Soft's classification of colliding default pairs runs on `sup D` with `Choice_D` among its premises. A pair of
rules from two candidates of one set has contradictory atoms in its two guards, so it is DISJOINT by a certificate
that needs no premise, and is never listed as a weighing point.

"Under every reading" is said without a side condition. The choice vocabulary needs one element for `ve__here`,
and W2's entailment also ranges over structures with no element, so `superpose_all` covers them through a lifting
lemma (S2): adjoining one element that lies in no author sort preserves base admissibility and the truth of every
author formula. If that lemma fails in statement review, the non-emptiness hypothesis stays in `superpose_all` and
every such report says "under every reading with at least one individual", never "under every reading".
`superpose_conflict_free` needs no such hypothesis (section 7, question 16).

### 2.6 Rights per reading

Nothing is added to `rights@0`; it receives `sup D`. This section is the target of S2b. Soft documents get
superposition first (S2a); until `superpose_faithful` is proved for rights, the bar case included, a rights
document with a content-bearing set is checked by the enumerated fallback of 2.3 (at most 64 compatible choices,
UNKNOWN beyond).

- **Limitations** (Art. 29(2)). A fixed limitation with scope `all` covers every candidate line of every right, so
  `lim_{L,a}` exists per act and `limitationScope` runs over all candidate lines; a finding names the reading that
  produced the line (`UnlicensedLimitation … under <set>:<i>`), which is how rights 2.4 expects the uncited exception
  of Art. 25's default candidate to be reported "under that choice".
- **"This right includes"** is the closure rule of 2.2 plus the copy rule of 2.3.
- **Limitation candidates** (Art. 29(3): on the liberties, or on every line) are superposed; quiescence keeps the
  unchosen one silent.
- **The bar** (Art. 30). `correlate` generates the bar's nodes without a guard, and `aimed_m` is shared by both bar
  readings on purpose (rights 1.4), so a bar candidate cannot be gated without changing `correlate`. A set whose
  candidates are bar units is therefore the one **enumerated axis**: at most one such set (there is at most one
  bar), two documents, each superposing everything else. `bar_blocks` then applies to every candidate liberty line.
  A **fixed** bar keeps `correlate`'s implementation intact as well: its node on `m` is generated as soon as any
  candidate has a liberty on `m` (`rs_u048`), and quiescence empties `aimed_m` under every choice without such a
  liberty (2.3, F21).
- **Couplings** are premises of `Choice_D`; `CouplingUnsatisfiable` becomes "`Choice_D` has no model", checked on
  atoms alone as today.

### 2.7 Structured right lines (`right-clauses@0`)

A line may carry clauses and one relation; both elaborate to guard conjuncts, so the rights theorems apply to the
result unchanged.

```json
{"kind": "claim",
 "norm": {"name": "remedy", "predicate": "remedy_required", "sign": true, "guard": ["top"], "unless": [], "over": []},
 "clauses": [{"role": "trigger", "span": [3541, 3635],
              "formula": ["exists", "act", ["and", ["binary", "violates_right_of", ["var", 0], ["var", 1]],
                                                   ["unary", "right_granted_by_law", ["var", 0]]]]}],
 "relation": {"predicate": "has_tribunals_competent_for", "slots": [0, 1], "total": 1, "cites": ["u035"]},
 "elided": [], "cites": {}}
```

- `clauses[i]`: `role ∈ {scope, trigger, object}` (rendering order and audit accounting only); `formula` a base
  formula over the line's context; `span` the source bytes it accounts for, inside the unit's span, disjoint from
  the other clauses' spans.
- `relation`: a declared binary base predicate between two slots of the line (bearer and holder for a claim; holder
  and object for a liberty such as "the government of his country"). `total: j` adds to `Rel_D` the premise "every
  element of slot `j`'s sort satisfying the holder guard is related to at least one element of the other slot's
  sort", labelled `rights:relation:<line>:total`, listed in `conditional_on` and in the residual. The relation may
  be an open term with a decider. On a line of a reading candidate the premise enters the slot gated by the
  candidate's atom, `χ_{s,i} → ρ` (2.3): ungated, the claim candidate of Art. 15(1) would impose "every person has a
  responsible state" on the two assertion readings of its own set (F13). The gated premise's label is
  `rights:relation:<line>:total under <set>@<v>:<i>`: it names the reading in the slot itself, because candidates
  of one set may share a line name, and `conditional_on` lists the slot label verbatim.
- `elided`: the spans of the unit that neither the act phrase, a clause nor the relation accounts for. It is
  mandatory under the profile, an empty list when nothing is left out, and reported as `elided_bytes` per unit.
  An elision is no longer a sentence in a reason field; it is a number the audit can sort by.
- Elaboration `plain`: `guard := G ∧ clause₁ ∧ … ∧ clauseₙ ∧ relation atom`. No act phrase rule changes: the
  80-character linter stays, and the clause carries what did not fit.

What the relation buys is the reading the audits kept asking for. "Every state must give each person equal access
to public service, where that state is the country of that person" owes the duty only along the relation, and a
situation with a state that is not the person's country separates it from the unscoped candidate (the "strengthened"
defect of `u077` becomes a checkable difference). With `total`, "some state owes this to each person" is a theorem
(`relation_some_bearer`), without any rule quantifying over duties: Art. 15(1) gets a claim candidate beside its
two assertions. The totality premise is existential, so the document leaves norms 7's fragment
(`fragment: no (<label>)`, with the premise's slot label: `rights:relation:<line>:total`, or its gated form ending
` under <set>@<v>:<i>`); certificates and witnesses still decide, completeness does not.

### 2.8 References on the chain

Discourse 5 already states the contract (an elaborated norm unit enters W1 as ordinary content; soft's coherence
premises are retained; anything touching the `soft` block is `UnsupportedTarget`). What is missing is the route and
three definitions.

- **Dispatch.** After validating and stripping `ve.discourse@1`, the wrapper calls `dispatch` (S0) on the base pair
  instead of the frozen admission: the chain's admission when `norms@0` is enabled, the frozen one otherwise, and
  `UnsupportedProfile: ve.discourse@1 with <b>` when the base list has a route of its own that discourse does not
  compose with (2.9). The environment is decoded by the chain's decoder, which knows `regulated`, `soft` and
  `rights`.
- **Positions.** The formula positions of a content, in canonical order: a norm's guard, each carve-out, each
  exception condition; a right's holder guard; each line's positions and clauses; a formula itself. Each position
  has a context (the rule's situation variables). A slot inside a position elaborates as discourse 4.4 says, with
  `binder:<i>` meaning the rule's own variables. W1's "that state" inside a rule block is W1's wording and is not a
  slot. A slot as the subject or object noun phrase of a rule header with an entity target `c` elaborates to the
  binder plus the guard conjunct `x_i equals c` (norms 3.3). A `rule` target in a header option ("exception to the
  rule above") elaborates to the stable name in `over`.
- **Wording source.** For a unit whose content is a fence, slot discovery and the wording checks of discourse
  4.1(4) read the **fence text**, and mention spans index it; the prose span stays the unit's source span. This
  removes two of the four failures of `u0214.s02` (fenced content; the curly apostrophe in pinned prose) and is
  the form a translation uses: the VE sentence in the fence may say "It must not …".
- **Translated units.** A unit whose content is JSON (no fence) is not parsed, so its prose pronouns cannot be
  slots. They are recorded as **provenance mentions** (`binding: "translated"`, `by`, `position`: a path into the
  content): the validator checks accessibility, the type at that position and that the term there is the target's
  elaboration. No uniqueness claim is made about the prose, and the report says "resolved by the translator". A
  provenance mention is reported only as attributed, is counted separately from checked resolutions, and never
  changes a status. Whether such mentions are admitted at all is decided in S4's specification, after the tally of
  open question 14. The
  one-reading property is a property of VE text; source prose never had it (open question 7).
- A document without a claim graph is admitted with an empty graph (the third abstention).

### 2.9 Other profiles: where they would attach (not built here)

| Profile | Attaches | Blocker that stays |
|---|---|---|
| `norm-defaults@0` (unmerged) | inside the chain, `fill` last (its D3). `unsaid__p` is per predicate, shared by all candidates, so no quiescence; probes read its three-valued status, and "not required" in 2.4's force example becomes "the text does not say" | merge order only |
| `time@0`, quantities | a content elaboration like RESOLVE (annotated formula → erased formula) at guard positions | the norm routes admit FOL only; needs the order checker under layers |
| `reports@0` | a wrapper kind around a content; a quoted norm contributes no layer (document.md) | reports rejects norm layers; no attribution wrapper for rules (C: `u0087.s06`) |
| `speech-acts@0` | a front elaboration producing one W1 rule per command, before SUPERPOSE | excludes soft norms; no speech semantics over soft decisions |
| `alternatives@0`, `risk@0` | siblings of soft norms inside the chain | alternatives excludes soft norms; no proved hard-to-soft bridge |
| `definitions@0`, `data@0` | below the chain | the mixed W1/W3/W5 order and proofs of INTEGRATION-GAPS |

Each row is a separate design. The stack only fixes where it goes, so that the next composition is one adapter and
one instance of the slot lemma, not a new route. Until then `dispatch` (S0) returns today's route for each of these
lists unchanged, and a stack wrapper beside one of them is the named abstention of rule 6.

## 3. VE's properties under composition

- **One reading per sentence.** Every candidate is a VE content with one derivation; superposition never lets one
  sentence be read two ways inside one argument, because `Choice_D` makes each choice global per unit (W2's rule).
  Resolution closes references before anything is a candidate. Provenance mentions (2.8) claim nothing about prose.
- **Zero-training English.** No new norm word. The force question the IDE asks is English with one situation:
  "This sentence says *shall*. (1) *Every state must secure social security for each person.* (2) *Every state
  should secure social security for each person, unless an exception applies.* They differ here: suppose the
  decider decides the exception applies to Ruritania. Under (1) Ruritania still must. Under (2) it is not required
  to." The question names the decision as a decision; it never states it as a fact of the situation (finding
  `SeparatedByDecisionOnly`, 2.4). This wording is for the strict and default candidates of one rule with an
  outcome probe. Every other pair is shown in the wording of its probe (outcome, selection, assertion), which
  states only what the check established, and a permission outcome reads "is permitted to" or "is not permitted
  to", never "may not" ([composition.md](composition.md) 2.1, E14 and E19 to E21).
  Verdicts read "Under every reading of the 14 open sentences, no two rules contradict" and "Read sentence 12 as
  *must* and sentence 15 as *should*: rules 12 and 15 contradict when …". Clauses are ordinary "if … and …"
  sentences; the relation is "where that state is the country of that person"; totality is "Every person has at
  least one country." W7 registers each wording and each passes the all-derivations gate before it is offered.
- **Small verified core.** No new operator, checker rule or judgment kind. New Lean is three elaborations
  (`sup`, `plain`, position-wise `resolve`), one executable check (`separates`), the dispatcher and their theorems;
  every route theorem is the generic slot lemma instantiated at `Lim_D ++ Choice_D ++ gated Rel_D` or a prefix of
  it.
- **Python, Lean and Rust agree.** Lean is the authority for all new semantics (SEMANTICS-MIGRATION section 6;
  discourse 3.4's "Python's admission is Lean's" is extended to the composed route). Python checks shape, searches
  for situations and certificates, renders English. Rust evaluates the regenerated formulas of `sup D` marked
  untrusted. Diagnostics follow one order: stack order, then each layer's own table.
- **Conservativity.** Profiles off: every construct here is rejected as today. Profiles on with nothing used: the
  identity theorems (`sup_no_sets`, `plain_identity`, `resolve_identity`, `dispatch_today`) give byte-identical
  elaboration, and a formula-only document keeps W2's ALL and NONE route (2.5). No frozen file, canonical byte,
  identity or theorem statement changes; `rights@0`'s right sets keep
  today's validation when `readings@1` is off. The only verdict that moves is UNKNOWN ("elaboration pending"), in
  documents that opt in.

## 4. Stages

Each stage is one branch, mergeable alone, with its own item-1 specification (statements and fixtures reviewed by
Astra and Fable before Lean starts), Lean, Python, conformance and a pilot rerun as acceptance.

### S0. The slot lemma, the dispatcher and the content type (enabler; no behaviour change)

Scope: `lean/VE/Compose/{Slot,Dispatch,Content}.lean`, `lean/COMPOSE.md`. No executable changes its answers. The
statements below are the plan's sketch; [composition.md](composition.md) section 9 holds them in exact form for the
statement review.

```lean
namespace VE.Compose
open VE.Norms (Sat ConflictFree envAt size elaborate)
open VE.SoftNorms (SoftDoc soften WellFormedSoft BaseAdmissible' background' softPremises holdsSoft)

def BaseAdmissibleP (X : SoftDoc) (P : List VE.Formula) (B : VE.Structure) : Prop := BaseAdmissible' X B ∧ Sat B P
def ConflictFreeP (X : SoftDoc) (P : List VE.Formula) : Prop := ∀ B, BaseAdmissibleP X P B → ConflictFree (soften X) B

/-- One statement for every base-premise slot: the soft route relative to extra closed base premises P. -/
theorem slot_route_acceptance (X : SoftDoc) (h : WellFormedSoft X = true) (P : List VE.Formula)
    (hP : ∀ a ∈ P, a.WellFormed (envAt (soften X) 0) []) (hc : ConflictFreeP X P)
    (Γ : List VE.Formula) (φ : VE.Formula) (c : VE.Tableau.Certificate)
    (accepted : VE.Tableau.checkCertificate (envAt (soften X) (size (soften X)))
                  (background' X ++ P ++ elaborate (soften X).T ++ Γ) φ c = true) :
  (∀ S : VE.Structure, S.Admissible (envAt (soften X) (size (soften X))) → holdsSoft X S →
     VE.Norms.definitionsHold (soften X) S → VE.Norms.profileHold (soften X) S →
     Sat S (VE.Norms.backgroundBase (soften X)) → Sat S (softPremises X) → Sat S P → Sat S Γ → φ.denote S []) ∧
  ((∀ a ∈ Γ, a.WellFormed (envAt (soften X) 0) []) → φ.WellFormed (envAt (soften X) 0) [] →
     ∀ B : VE.Structure, BaseAdmissibleP X P B → Sat B Γ → φ.denote B [])

theorem slot_route_countermodel (X) (h) (P) (hP) (hc : ConflictFreeP X P) (Γ) (φ)
    (hΓ : ∀ a ∈ Γ, a.WellFormed (envAt (soften X) 0) []) (hφ : φ.WellFormed (envAt (soften X) 0) [])
    (B : VE.Structure) (hB : BaseAdmissibleP X P B) (hs : Sat B Γ) (hn : ¬ φ.denote B []) :
  ∃ S, VE.Norms.DocumentExpansion (soften X) B S ∧ Sat S (softPremises X) ∧ Sat S P ∧ Sat S Γ ∧ ¬ φ.denote S []

theorem slot_conflict_free (X) (h) (P) (hP) (certs) (hc : slotConflictFreeCheck X P certs = true) : ConflictFreeP X P

/-- The rights route is the instance P := Lim_D (definitional; rights 9.1). -/
theorem rights_is_slot (D : VE.Rights.RightsDoc) (B : VE.Structure) :
  VE.Rights.BaseAdmissibleR D B ↔ BaseAdmissibleP (VE.Rights.correlate D) (VE.Rights.limPremises D) B

/-- The route of a profile list. A list today's gate accepts keeps today's route, a list it rejects keeps today's
    diagnostic; a validated chain list gets the head of the stack; only a stack wrapper beside a route outside the
    chain is the new named abstention. -/
inductive Route
  | frozen | reports | speechActs | alternatives | risk      -- today's routes outside the chain
  | norms | soft | rights                                    -- the chain, today's routes
  | readings | clauses | discourse                           -- the stack wrappers (S1 to S4 build their heads)
def today (ps : List String) : Except String Route          -- ve/profiles.py checker_family, then the head
def dispatch (ps : List String) : Except String Route
/-- Today's lists: alternatives@0, risk@0 and speech-acts@0 contain norms@0 and keep their own routes; reports@0
    keeps its own. -/
theorem dispatch_today (ps) (h : ∀ w ∈ wrapperProfiles, w ∉ ps) : dispatch ps = today ps
theorem today_sound (ps) (r) (h : today ps = .ok r) :
  TodayList ps ∧
  r = if "risk@0" ∈ ps then .risk else if "alternatives@0" ∈ ps then .alternatives
      else if "speech-acts@0" ∈ ps then .speechActs else if "reports@0" ∈ ps then .reports
      else if "rights@0" ∈ ps then .rights else if "soft-norms@0" ∈ ps then .soft
      else if "norms@0" ∈ ps then .norms else .frozen
theorem dispatch_chain (ps) (h : ChainList ps) : dispatch ps = .ok (stackHead ps)
/-- Every error is the order error, today's error on the base list, or a wrapper's named refusal: a `with b` for a
    route outside the chain, a `requires b` for a missing lower layer. -/
theorem dispatch_error (ps) (e) (h : dispatch ps = .error e) :
  e = "UnsupportedProfile: profiles must be sorted and unique" ∨ today (base ps) = .error e ∨
  ∃ a ∈ wrapperProfiles, a ∈ ps ∧ ∃ b, (b ∈ ps ∧ e = "UnsupportedProfile: " ++ a ++ " with " ++ b) ∨
                                         (b ∉ ps ∧ e = "UnsupportedProfile: " ++ a ++ " requires " ++ b)

/-- A reading candidate's content (2.2), shared by S1, S2 and S4; S3 and S4 therefore depend on S0 only. -/
inductive Content
  | assertion (φ : VE.Formula) | norm (N : VE.SoftNorms.SoftNode) | right (R : VE.Rights.Right)
  | rightLines (right : String) (ls : List VE.Rights.SourceLine) | limitation (L : VE.Rights.Limitation)
end VE.Compose
```

Acceptance: the Lean audit passes with the unchanged allowlist; `rights_route_acceptance` and
`rights_route_countermodel` are re-derived as instances (their statements untouched); `dispatch` equals
`ve/profiles.py` `checker_family` followed by today's route choice on every sorted subset of the registered
profiles, diagnostics included (composition.md fixture D-all, whose Lean half guards `today` against Python's
32,768 outcomes); no conformance output moves.

### S1. Content-bearing candidates and separating situations (`readings@1`, part A)

Scope: the wire of 2.2, admission of a set (closure, distinct declarations across sets, each candidate elaborates,
separation), `labels` and `couplings` on every kind, the findings `SeparatedByActOnly` and
`SeparatedByDecisionOnly`. The statement specification starts from the probe key and the shared base of 2.4.
Document verdicts over such sets stay UNKNOWN
("superposition pending") until S2, as rights sets are today. Files `lean/VE/Readings/{Doc,Separate,Wire,Run}.lean`,
target `ve_readings_route` (root `ReadingsMain.lean`), `lean/READINGS.md`; Python `ve/readings.py` gains the
situation search and delegates the verdict to Lean.

```lean
namespace VE.Readings
open VE.Norms (Regulated Sat tupleVal)
open VE.SoftNorms (ValueSoft SelectsSoftD)
open VE.Rights (RightsDoc correlate limPremises WellFormedRights)
open VE.Compose (BaseAdmissibleP Content)                      -- Content is S0's (VE.Compose.Content)

structure Candidate where id : String; content : Content; labels : List (String × String)
structure ReadingSet where id : String; unit : String; version : Nat; candidates : List Candidate
structure Doc where
  base : RightsDoc                 -- the environment with its blocks and the fixed norm, right, limitation, bar units
  asserted : List VE.Formula       -- the fixed assertion units
  sets : List ReadingSet           -- active versions, source order
  couplings : List Coupling; constraints : List Constraint; narrowings : List Narrowing

/-- Fixed units plus candidate i of set s, and the assertions in force (the candidate's own, if it is a formula). -/
def one (D : Doc) (s : String) (i : Nat) : RightsDoc × List VE.Formula
/-- The shared vocabulary of 2.4: the base predicate names of E and the generated predicates of the fixed units
    alone, under the names the fixed units' own document gives them. No predicate a candidate owns. -/
def sharedBase (D : Doc) : List String
/-- The name candidate i's document gives to a shared predicate: itself for an author name, the name with the same
    source key for a generated one (rights' generated names are positional, so the two documents may differ). -/
def sharedName (D : Doc) (s : String) (i : Nat) : String → String
/-- The probe key is today's: an outcome at (predicate, tuple), or a selection at (kind, predicate, tuple) with
    kind an instance kind of rights 1.2 or `norm` for a rule outside rights. A probe never names a rule. -/
inductive Probe (α : Type) | outcome (p : String) (vs : List α) | selects (kind p : String) (vs : List α) | holds
def selectable (X : RightsDoc) (kind p : String) : List VE.SoftNorms.SoftNode   -- the nodes of that kind on p

/-- Probe q has value v in S for the document X with assertions A. -/
def Observes (X : RightsDoc) (A : List VE.Formula) (S : VE.Structure) : Probe S.Carrier → Bool → Prop
  | .outcome p vs, v => ∃ r ∈ (correlate X).T.regulated, r.name = p ∧ ValueSoft (correlate X) r S vs = some v
  | .selects k p vs, v => ((∃ N ∈ selectable X k p,
      SelectsSoftD (correlate X) S (tupleVal vs) (VE.SoftNorms.fuel (correlate X)) N) ↔ v = true)
  | .holds, v        => ((∀ a ∈ A, a.denote S []) ↔ v = true)

/-- Some assignment to the candidate's own generated predicates over the shared base B makes the candidate's
    document admissible with q = v. The fixed units' decision tables are B's and are not reassigned. -/
def Achieves (D : Doc) (s : String) (i : Nat) (B : VE.Structure) (q : Probe B.Carrier) (v : Bool) : Prop :=
  ∃ R : String → List B.Carrier → Prop, (∀ p ∈ sharedBase D, ∀ vs, R (sharedName D s i p) vs ↔ B.relation p vs) ∧
    BaseAdmissibleP (correlate (one D s i).1) (limPremises (one D s i).1) { B with relation := R } ∧
    Observes (one D s i).1 (one D s i).2 { B with relation := R } q v
def Separated (D : Doc) (s : String) (i j : Nat) : Prop :=
  ∃ (B : VE.Structure) (q : Probe B.Carrier) (v : Bool),
    (Achieves D s i B q v ∧ ¬ Achieves D s j B q v) ∨ (Achieves D s j B q v ∧ ¬ Achieves D s i B q v)

/-- The executable check: evaluate the witnessing side on base + decisions, then every assignment to the other
    side's own generated predicates on the same finite base (bounded; false when the bound is exceeded). M is over
    the shared vocabulary, the fixed units' decision tables included. -/
def separates {α} [DecidableEq α] (D : Doc) (s : String) (i j : Nat) (M : VE.FiniteModel α)
    (decisions : List (String × List (List α))) (q : Probe α) : Bool
theorem separates_sound {α} [DecidableEq α] (D : Doc) (hD : WellFormedDoc D = true) (s) (i j) (M) (decisions) (q)
    (valid : M.Valid (sharedEnv D)) (h : separates D s i j M decisions q = true) : Separated D s i j

/-- No generated predicate on either side: the check is today's comparison of outcomes and selected lines. -/
theorem separation_conservative {α} [DecidableEq α] (D) (s) (i j) (M : VE.FiniteModel α)
    (hi : generated D s i = []) (hj : generated D s j = []) :
  (∃ q, separates D s i j M [] q = true) ↔ observeAll D s i M ≠ observeAll D s j M

/-- The force axis is real exactly where the exception can apply: a default rule alone and its strict twin agree
    wherever the rule's exception does not hold. -/
theorem force_agrees_off_exception (X : VE.SoftNorms.SoftDoc) (h : WellFormedSoft X = true) (N : SoftNode)
    (hN : X.T.nodes = [N]) (hd : N.mode = .default) (ha : N.alterable = []) (r : Regulated)
    (hr : r ∈ X.T.regulated) (S : VE.Structure) (vs : List S.Carrier)
    (he : ¬ (VE.SoftNorms.exceptedF X N).denote S (tupleVal vs)) :
  ValueSoft X r S vs = ValueSoft (strictTwin X N) r S vs
end VE.Readings
```

`force_agrees_off_exception` is deliberately about a rule alone. In a document the two readings also differ where
a strict rule decides the act (a default gives way, a strict twin conflicts) and where the twin itself blocks other
defaults; the IDE's paraphrase of the force question says so, and no theorem claims otherwise (open question 3).

Case kinds on `ve_readings_route`: `readings-validate` (a document's sets: per set the closure, elaboration and
separation results, findings), `readings-separate` (one pair, a situation, a probe). Limits: 64 candidates per set
(W2), decision assignments ≤ 2¹², couplings ≤ 8 (rights 11) raised only with the limits contract.

Acceptance: fixtures F1 to F6, F15, F19, F20, F22; differential `readings-validate` Python search versus Lean check
on 1,000 generated sets (strict/default twins, mixed kinds, renamed twins that must **not** separate); the
constitution's 14 sets and the UDHR's 4 norm-candidate sets validate in-document with their stored situations.

### S2. Superposed verdicts and per-reading rights (`readings@1`, part B), in two milestones

Scope: `sup`, `Choice_D`, the verdict table of 2.5, 2.6 including the enumerated bar axis and the fallback, W2
`readings:` labels on certificates, `DeadReading`. Files `lean/VE/Readings/{Superpose,Choice,Route,Admission}.lean`.

- **S2a, soft documents.** Documents without a right, limitation or bar unit (the constitution): generated names
  derive from rule names, so the name map is the qualification alone. Shipped first.
- **S2b, rights documents.** The statements below with `nameMap` over rights' positional names and the bar case.
  Until `superpose_faithful` is proved for rights, the fixed-bar case of F21 included, a rights document with a
  content-bearing set uses the enumerated fallback (2.6).

The statement review of S2 attacks `superpose_faithful` first, with F21 before any other rights case, then the
lifting lemma behind `superpose_all`.

```lean
namespace VE.Readings
abbrev Choice := List (String × Nat)                       -- one candidate index per set, source order
def Compatible (D : Doc) (c : Choice) : Prop              -- complete; couplings, constraints and narrowings hold
def choiceDoc (D : Doc) (c : Choice) : RightsDoc × List VE.Formula    -- fixed units plus the chosen contents, own names
def sup (D : Doc) : RightsDoc × List VE.Formula            -- 2.3
def atom (D : Doc) (s : String) (i : Nat) : VE.Formula     -- χ_{s,i}: the set's bit literals at ve__here spelling i
def choicePremises (D : Doc) : List VE.Formula             -- Choice_D
/-- S' is S with only the choice vocabulary (sort ve__reading, constant ve__here, the bit predicates) reinterpreted. -/
def ChoiceExtension (D : Doc) (S S' : VE.Structure) : Prop :=
  ∃ R dom k, S' = { S with relation := R, domain := dom, constant := k } ∧
    (∀ p, ¬ p.startsWith "ve__bit__" → ∀ vs, R p vs ↔ S.relation p vs) ∧
    (∀ σ, σ ≠ "ve__reading" → dom σ = S.domain σ) ∧ (∀ x, x ≠ "ve__here" → k x = S.constant x)
def gatedRel (D : Doc) : List VE.Formula                   -- χ_{s,i} → ρ per candidate totality premise; a fixed line's ρ
                                                           -- as it is; [] until right-clauses@0 is merged (S3)
/-- The combined slot Lim_D ++ Choice_D ++ gated Rel_D; slotLabels D gives each formula its label (2.3). -/
def slotP (D : Doc) : List VE.Formula := limPremises (sup D).1 ++ choicePremises D ++ gatedRel D
def Encodes (D : Doc) (c : Choice) (S : VE.Structure) : Prop :=
  ∀ R ∈ D.sets, ∀ i, i < R.candidates.length → ((atom D R.id i).denote S [] ↔ (R.id, i) ∈ c)
def nameMap (D : Doc) (c : Choice) : String → String       -- a generated name of choiceDoc D c ↦ its name in sup D
def pull (ν : String → String) (S : VE.Structure) : VE.Structure := { S with relation := fun p vs => S.relation (ν p) vs }

theorem sup_wellFormed (D : Doc) (h : WellFormedDoc D = true) (hs : superposable D = true) :
  WellFormedRights (sup D).1 = true
/-- Needs the cross-set check of 2.2: per-candidate admission alone admits two sets whose chosen candidates declare
    one name. WellFormedDoc runs it; it is named here because the proof uses it. -/
theorem choice_wellFormed (D) (h : WellFormedDoc D = true) (hx : distinctAcrossSets D = true)
    (hs : superposable D = true) (c) (hc : Compatible D c) :
  WellFormedRights (choiceDoc D c).1 = true
theorem sup_no_sets (D : Doc) (h : D.sets = []) : sup D = (D.base, D.asserted) ∧ choicePremises D = []

/-- Every admissible base of sup D is one compatible choice. -/
theorem encodes_unique (D) (h) (hs) (B : VE.Structure) (hB : BaseAdmissibleP (correlate (sup D).1) (slotP D) B) :
  ∃ c, Compatible D c ∧ Encodes D c B ∧ ∀ c', Encodes D c' B → c' = c

/-- 2.3: where exactly c's atoms hold, the superposed document decides every act as c's document does. With a fixed
    bar this holds only through the owner-based quiescence of aimed_m in choicePremises D (hq): under a choice
    without a liberty on m, the bar's node in sup D has an empty guard and c's document has no such node (F21). -/
theorem superpose_faithful (D : Doc) (h : WellFormedDoc D = true) (hs : superposable D = true) (c : Choice)
    (hc : Compatible D c) (S : VE.Structure) (he : Encodes D c S) (hq : Sat S (choicePremises D))
    (r : Regulated) (hr : r ∈ (correlate (choiceDoc D c).1).T.regulated) (vs : List S.Carrier) :
  ValueSoft (correlate (sup D).1) r S vs = ValueSoft (correlate (choiceDoc D c).1) r (pull (nameMap D c) S) vs

/-- Bases correspond in both directions. -/
theorem base_down (D) (h) (hs) (c) (hc : Compatible D c) (B) (hB : BaseAdmissibleP (correlate (sup D).1) (slotP D) B)
    (he : Encodes D c B) :
  VE.Rights.BaseAdmissibleR (choiceDoc D c).1 (pull (nameMap D c) B) ∧
  (Sat B (sup D).2 ↔ Sat (pull (nameMap D c) B) (choiceDoc D c).2)
theorem base_up (D) (h) (hs) (c) (hc : Compatible D c) (B₀ : VE.Structure) (hne : Nonempty B₀.Carrier)
    (hB : VE.Rights.BaseAdmissibleR (choiceDoc D c).1 B₀) :
  ∃ (R : String → List B₀.Carrier → Prop) (B : VE.Structure),
    ChoiceExtension D { B₀ with relation := R } B ∧ BaseAdmissibleP (correlate (sup D).1) (slotP D) B ∧
    Encodes D c B ∧ ∀ p ∈ names (choiceDoc D c).1, ∀ vs, R (nameMap D c p) vs ↔ B₀.relation p vs

/-- Conflict-free under every reading, in one check. No non-emptiness hypothesis is needed on either side: a
    regulated predicate has arity 1 or 2 (W1's well-formedness), so ConflictFree quantifies over typed tuples of
    length at least 1 and is vacuous on an empty carrier; and every admissible structure of sup D interprets
    ve__here, so it has an element. -/
theorem superpose_conflict_free (D) (h) (hs) :
  VE.Compose.ConflictFreeP (correlate (sup D).1) (slotP D) ↔
    ∀ c, Compatible D c → VE.Rights.RightsConflictFree (choiceDoc D c).1

/-- The lifting lemma. adjoinOne B is B with one new element that lies in no sort: every domain, constant and
    relation is B's on the old elements, and the new element is in no domain and no tuple. -/
def adjoinOne (B : VE.Structure) : VE.Structure            -- Carrier := Option B.Carrier
theorem adjoin_denote (B : VE.Structure) (φ : VE.Formula) (ρ : VE.Valuation B) :
  φ.denote (adjoinOne B) (ρ.map some) ↔ φ.denote B ρ
theorem adjoin_baseAdmissible (X : RightsDoc) (B : VE.Structure) :
  VE.Rights.BaseAdmissibleR X (adjoinOne B) ↔ VE.Rights.BaseAdmissibleR X B

/-- ALL: a certificate on sup D proves φ in every reading's document. Γ and φ are over the author's vocabulary.
    No non-emptiness hypothesis, to match W2's entailment over all structures: B is lifted by adjoinOne
    (adjoin_baseAdmissible, adjoin_denote), then base_up applies. Fallback if the lifting lemma fails in statement
    review: (hne : Nonempty B.Carrier) returns and reports say "every reading with at least one individual". -/
theorem superpose_all (D) (h) (hs) (hcf : VE.Compose.ConflictFreeP (correlate (sup D).1) (slotP D))
    (Γ : List VE.Formula) (φ : VE.Formula) (hΓ : ∀ a ∈ Γ, AuthorFormula D a) (hφ : AuthorFormula D φ)
    (cert : VE.Tableau.Certificate) (accepted : supCertificateCheck D Γ φ cert = true)
    (c : Choice) (hc : Compatible D c) (B : VE.Structure)
    (hB : VE.Rights.BaseAdmissibleR (choiceDoc D c).1 B) (hA : Sat B (choiceDoc D c).2) (hs' : Sat B Γ) :
  φ.denote B []

/-- A checked countermodel on sup D is a countermodel of the reading its atoms encode. -/
theorem superpose_countermodel {α} [DecidableEq α] (D) (h) (hs) (Γ) (φ) (hΓ) (hφ) (M : VE.FiniteModel α)
    (valid : supModelCheck D Γ M = true) (hn : φ.eval M (fun _ => none) = false) :
  ∃ c, Compatible D c ∧ Encodes D c M.asStructure ∧
    VE.Rights.BaseAdmissibleR (choiceDoc D c).1 (pull (nameMap D c) M.asStructure) ∧
    Sat (pull (nameMap D c) M.asStructure) ((choiceDoc D c).2 ++ Γ) ∧ ¬ φ.denote (pull (nameMap D c) M.asStructure) []

/-- Formula-only sets without couplings: superposition is W2's shortcut (Route.readings_all_iff). -/
theorem superpose_assertions (D) (hk : ∀ R ∈ D.sets, ∀ a ∈ R.candidates, ∃ φ, a.content = .assertion φ)
    (hn : D.couplings = [] ∧ D.constraints = [] ∧ D.narrowings = []) (S : VE.Structure) (hne : Nonempty S.Carrier)
    (hS : S.Admissible (authorEnv D)) :
  (∃ S', ChoiceExtension D S S' ∧ Sat S' ((sup D).2 ++ choicePremises D)) ↔
  (Sat S D.asserted ∧ ∀ R ∈ D.sets, ∃ a ∈ R.candidates, ∃ φ, a.content = .assertion φ ∧ φ.denote S [])
end VE.Readings
```

`supCertificateCheck` is `checkCertificate` on `background' ++ slotP D ++ layers ++ (sup D).2 ++ Γ` for
`correlate (sup D).1`; `supModelCheck` is the finite validity of that base background plus `Γ`. Both regenerate
everything. `superpose_all` and `superpose_countermodel` are `slot_route_acceptance` and `slot_route_countermodel`
at `P := slotP D` composed with `base_up`, `base_down` and `superpose_faithful`.

Case kinds: `readings-elaborate` (`sup D`, `Choice_D`, the name map, sizes; compared byte for byte with Python's),
`readings-certificate`, `readings-conflict`, `readings-model`, and `admission` (a W2 document with graph). A document
with a bar set runs each kind once per bar candidate and reports per candidate.

Acceptance, S2a: fixtures F3 and F18; `readings-elaborate` differential on 1,000
generated soft documents with faulty sources rejected by both; on every generated document with at most 64
choices, the superposed verdict equals the enumerated one (ALL, conflict status, premise status), which is the
executable shadow of the theorems; pilot rerun: the constitution's main document leaves `premises: UNKNOWN`.
Acceptance, S2b: fixtures F6 to F10 and F21, the same differential and shadow test on generated rights documents
(fixed bars with candidate liberties among them); pilot rerun: the UDHR's main document leaves
`premises: UNKNOWN`; U `limitation_terms > 0`; load time reported against the 85 s the 20 right sets cost today.
Before S2b the UDHR's rights report stays UNKNOWN: its reading plan is over the enumeration budget.

### S3. Structured right lines (`right-clauses@0`, requires `rights@0`)

Scope: 2.7. Files `lean/VE/RightClauses/{Tree,Plain,Relation,Wire}.lean`; case kind `clauses-elaborate` on
`ve_readings_route` (or `ve_rights_route`'s successor under `dispatch`); English: the clause and relation wordings,
the totality sentence, `elided` in the reader's checklist ("this line leaves out: *in full equality*").

```lean
namespace VE.RightClauses
inductive Role | scope | trigger | object
structure Clause where role : Role; formula : VE.Formula; span : Nat × Nat
structure Relation where pred : String; slots : Nat × Nat; total : Option Nat; cites : List String
structure CLine where line : VE.Rights.SourceLine; clauses : List Clause; relation : Option Relation; elided : List (Nat × Nat)
structure ClauseDoc where doc : VE.Rights.RightsDoc; lines : List (String × String × CLine)   -- right, rule name, line

def plain (D : ClauseDoc) : VE.Rights.RightsDoc            -- guard := G ∧ clauses ∧ relation atom, nothing else
def relPremises (D : ClauseDoc) : List VE.Formula          -- Rel_D: one totality premise per relation with total
def WellFormedClauses (D : ClauseDoc) : Bool               -- typing in the line's context; spans inside the unit,
                                                           -- disjoint; the relation's sorts are its slots' sorts
theorem plain_identity (D) (h : ∀ x ∈ D.lines, x.2.2.clauses = [] ∧ x.2.2.relation = none) : plain D = D.doc
theorem plain_guard (D) (h : WellFormedClauses D = true) (R n) (L : CLine) (hL : (R, n, L) ∈ D.lines)
    (S : VE.Structure) (ρ : VE.Valuation S) :
  (guardOf (plain D) n).denote S ρ ↔
    (guardOf D.doc n).denote S ρ ∧ (∀ c ∈ L.clauses, c.formula.denote S ρ) ∧
    (∀ rel, L.relation = some rel → (relAtom rel).denote S ρ)
theorem plain_wellFormed (D) (h : WellFormedClauses D = true) (h0 : VE.Rights.WellFormedRights D.doc = true) :
  VE.Rights.WellFormedRights (plain D) = true

/-- "Some bearer owes it": under totality, every holder of the right has a related bearer, and that bearer owes
    the act wherever the line's own clauses hold and nothing narrows the line. -/
theorem relation_some_bearer (D : ClauseDoc) (h : WellFormedClauses D = true) (R n : String) (L : CLine)
    (hL : (R, n, L) ∈ D.lines) (N : VE.Rights.Line) (hN : (R, N) ∈ VE.Rights.linesOf (plain D)) (hn : N.node.name = n)
    (hk : VE.Rights.dutyKind N = true) (rel : Relation) (hr : L.relation = some rel)
    (ht : rel.total = some (VE.Rights.holderSlot (plain D) N)) (hs : rel.slots = (0, VE.Rights.holderSlot (plain D) N))
    (S : VE.Structure) (hS : Sat S (relPremises D)) (hv : S.Carrier) (hH : (holderGuardOf D R).denote S (fun _ => hv)) :
  ∃ bv, S.relation rel.pred [bv, hv] ∧
    ∀ vs, VE.TupleTyped S (VE.Rights.sortsOf (plain D) N) vs → vs.head? = some bv →
      vs.get? (VE.Rights.holderSlot (plain D) N) = some hv →
      (VE.Rights.ownGuard (plain D) N).denote S (tupleVal vs) →
      (¬ ∃ m ∈ VE.Rights.narrowings (plain D) N, VE.Rights.NarrowsAt (plain D) S (tupleVal vs) N m) →
      VE.Rights.owes (plain D) S N vs
end VE.RightClauses
```

The last theorem is `narrowings_complete` (rights 9.2) read contrapositively, plus the totality premise; it is
stated for a binary claim. The route is the slot lemma at `P := limPremises (plain D) ++ relPremises D` for a
document without reading sets. With sets, `relPremises` enters the combined slot gated (2.3): each candidate
line's totality premise as `χ_{s,i} → ρ`, so that `relation_some_bearer` is available under the claim reading and
nothing is imposed on the others (F13).

Acceptance: fixtures F11 to F14; rights' seventeen fixture shapes unchanged with the profile on and no clause
(`plain_identity`); every unit of the UDHR rerun reports `elided_bytes`; the audit's seven units are re-audited.

### S4. Discourse on the chain (`ve.discourse@1`, amendment; `ve-document@2`)

Scope: 2.8. Files `lean/VE/Discourse/{Positions,Compose}.lean`; the discourse loader's three abstentions become
implementations; `ve/profiles.py` and the Lean gate admit `ve.discourse@1` beside the chain. The specification
starts with the tally of open question 14 and then decides open question 7 (provenance mentions: attributed,
counted separately, never changing a status, or not admitted at all).

```lean
namespace VE.Discourse
/-- The formula positions of a content with their contexts, in canonical order (2.8). Content is S0's, so this
    stage imports nothing of S1 or S2. -/
def positions : VE.Compose.Content → List (List String × VE.Formula)
def resolveContent (E) (K : Manifest) (unit : String) (c : VE.Compose.Content) : Except String VE.Compose.Content

theorem resolve_identity (E) (K) (u) (c) (h : formulaMentions K u = []) : resolveContent E K u c = .ok c
/-- Position-wise: discourse 9.3's elaborate_faithful under the rule's context instead of the empty one. -/
theorem resolve_position_faithful (E) (K) (u) (c c') (h : resolveContent E K u c = .ok c') (k : Nat)
    (ctx) (A) (hk : (positions c')[k]? = some (ctx, A)) (S : VE.Structure) (hS : S.Admissible E)
    (ρ : VE.Valuation S) (hρ : ρ.Typed S ctx) :
  A.denote S ρ ↔ IntendedAt E K u k S ρ
theorem resolve_no_new_symbols (E) (K) (u) (c c') (h : resolveContent E K u c = .ok c') :
  ∀ x ∈ positions c', ∀ p ∈ x.2.symbols, p ∈ E.symbols
/-- The composed admission is the chain's admission of the resolved document. -/
theorem composed_admission (profiles) (environment) (j : Json) (res) (h : admitComposed profiles environment j = .ok res) :
  ∃ resolved, resolveDocument environment j = .ok resolved ∧
    VE.Compose.dispatchAdmission (baseProfiles profiles) (baseEnvironment environment) resolved = .ok res.inner
/-- Existing discourse documents are untouched. -/
theorem composed_base_unchanged (profiles) (environment) (j) (h : "norms@0" ∉ profiles) (fuel) :
  admitComposed profiles environment j = admitDiscourse profiles environment (rvOf j) j fuel
/-- Discourse 5: no binding discharges, hides or reorders a coherence, limitation or choice premise. -/
theorem conditions_retained (profiles) (environment) (j) (res) (h : admitComposed profiles environment j = .ok res) :
  res.report.conditionalOn = res.inner.report.conditionalOn
end VE.Discourse
```

Acceptance: fixtures F16, F17; discourse's fixtures α to ω unchanged (`composed_base_unchanged`); the constitution
translation with the `discourse` block checks through the Lean route with its 15 norm units and `u0214.s02`.

## 5. Fixtures from the pilot units

Spans are UTF-8 byte offsets into the pinned sources (constitution SHA-256 `fa10ed48…50dd`, 184,893 bytes; UDHR
`d6495201…7d3a`, 10,916 bytes). "Today" is the verdict at `2205be39`.

| # | Unit | Input | Expected | Today |
|---|---|---|---|---|
| F1 | C `u0156.s03` [95093, 95193) "Claude shouldn't actively deceive the user …" | set {strict, default} of rule `no-system-prompt-deception` on `system_prompt_deception_avoidance_required(claude_instance, user)`; situation: one instance, one user; default's decision: excepted there; probe: the outcome at that pair | `separates = true` (strict: required; no default assignment reaches required = false on the strict side; default reaches it) | "relations must contain exactly the base predicates" |
| F2 | C `u0165.s03` [101609, 101698) with narrowing `narrow-u0165-s03` (keeps strict, cites `u0166.s01`, `u0166.s04`) | the set of F1's shape plus the narrowing | `Choice_D` holds `¬χ_default` labelled `narrowing:narrow-u0165-s03`; every result that uses it lists it; removing the narrowing changes no identity of the set | narrowing recorded, nothing checked |
| F3 | C main document, 14 force sets (`metrics.json` `reading_sets.units`), 7 narrowed | `readings-conflict`, `readings-model` | a conflict status under every reading from one certificate or one witness per target (15 obligation predicates, no dual pair), never "pending"; a model for one choice and one per candidate not excluded by a narrowing (21 of 28); with the atoms of the all-strict and of the all-default choice assumed, the premise and conflict results equal those of `readings/all-strict.ve.md` and `readings/all-default.ve.md` (a model each; 1 and 15 default exceptions) | `premises: UNKNOWN`, plan over budget |
| F4 | U `u017` [2179, 2244) "and should act towards one another in a spirit of brotherhood." | `rs_u017` v2 {strict, default} as norm contents | set admitted in-document with one situation; verdicts equal the two companions' | candidates `content: null`; two companion files |
| F5 | U `u091` [8275, 8476) Art. 25(1) | right candidates {strict, default} of the claim "secure … a standard of living adequate …", labels `force` (rights 2.4 `rs_u091`) | separated where the exception applies; unit READINGS; under the default candidate `UnlicensedLimitation` (uncited exception), under the strict one none | UNFORMALISED, `force_variants_in_one_reading_set` |
| F6 | U coupling `c-force` over F5's set and the Art. 22 to 27 sets, citing `u013a` ("a common standard of achievement") | `couplings` on `force` | `Choice_D` carries the coupling premises; ALL results list `coupling:c-force`; without the coupling the document still gets a verdict | couplings need right candidates; force sets cannot exist |
| F7 | U `u111` [10218, 10555) Art. 29(2), limitation `l29`, scope `all` | `readings-elaborate` | one `lim` per act in scope of some candidate line; `limitation_terms > 0`; under candidate `liberty` of `rs_u048`, where limitation 29 holds the liberty is silent; `limitationScope` findings name their reading | `limitation_terms: 0` |
| F8 | U `u067` [6104, 6166), `u068` [6166, 6329), `u071a` [6405, 6470), `u071b` [6470, 6573) "this right includes …" | `right_lines` on rights 18 and 19, declared by every candidate of `rs_u066` and `rs_u070` | one copy per candidate, guarded by its atom; a candidate set in which one candidate omits the right: `ReadingInterface: rs_u066: r18` | UNFORMALISED, `right_lines_in_reading_sets` |
| F9 | U `u114` [10691, 10916) Art. 30 | bar set {rule, query} (rights 2.4 `rs_u114`) | enumerated: two superposed documents; under `rule`, every candidate liberty line on `m` is barred where `aimed_m` holds (`bar_blocks` on `sup D`); under `query` a certificate or countermodel per `m` | bar unused; companion document |
| F10 | U `u112` [10555, 10676) Art. 29(3) | limitation candidates {on the liberties, on every line} | superposed with quiescence; separated by a situation where the limitation holds for a claim line: silent under "every line", selecting under "liberties" | companion document |
| F11 | U `u035` [3469, 3637) Art. 8 | claim with a trigger clause for "for acts violating the fundamental rights granted him by the constitution or by law" and its span; relation to the state whose tribunals are competent | `elided: []`; the clause is in the guard (`plain_guard`); a person with no violated right is owed nothing by this line | scope in a sort's prose description |
| F12 | U `u039` [3734, 3935) Art. 10 | scope clause "in the determination of his rights and obligations and of any criminal charge against him"; "in full equality" as a clause over the open term `full_equality` | both clauses in the guard with spans; `elided: []`; unit OPEN through the open term | weakened and unscoped, then prose-scoped |
| F13 | U `u054` [5239, 5284) Art. 15(1) | set {assertion "each person has some nationality", assertion "some state grants each person one", claim with relation `responsible_for` and `total`} | mixed-kind set admitted; under the claim, `relation_some_bearer` gives a bearer per person; the claim candidate is separated from "every state must grant" by a two-state situation; the totality premise is in the slot as `χ_claim → ρ`, so a situation with a person no state is responsible for is a model under each assertion reading and under none of the claim reading | strengthened, then assertions only |
| F14 | U `u077` [6861, 6938) Art. 21(2) "in his country" | claim with relation `country_of`; second candidate without it | separated by a situation with a state that is not the person's country | "strengthened": relation dropped |
| F15 | U `u032` Art. 7 as rejected on 2026-09-30 ("avoid denying equal protection" / "give equal protection" on two predicates) | set of the two | admitted with finding `SeparatedByActOnly` naming both act phrases | separated "only by predicate name", found by the audit |
| F16 | C `u0214.s01`, `u0214.s02` in the translation with its norm units and fenced `u0248` | `ve-document@2`, profiles including `norms@0`, `soft-norms@0` | admitted by the Lean route; `u0214.s02` MIXED with parts LABELLED and UNFORMALISED as discourse 2.5; norm verdicts equal those without the `discourse` block | `UnsupportedProfile`; four failures |
| F17 | C `u0078.s01` [48052, 48503), reference surface at [48274, 48278) | translated norm unit with a provenance mention | if S4's specification admits provenance mentions (open question 7): admitted; report line "resolved by the translator", counted under provenance mentions and not under checked resolutions; the unit's status is what it is without the mention; without the mention `UnrecordedSlot` as today; with a target of the wrong sort `IllTypedTarget` | `UnrecordedSlot` |
| F18 | synthetic, shaped on the hard constraints | two sets whose candidates stratify alone and cycle together | `ReadingsNotSuperposable: <sets>`; the enumerated fallback gives the verdict (4 choices) | — |
| F19 | synthetic twin of F1 | default candidate whose exception has an unsatisfiable necessary condition | set rejected: "distinguishing situation does not separate readings" | — |
| F20 | U translation `document_id 97f65591…4533`; rights fixtures; discourse fixtures α to ω | `readings@1`, `right-clauses@0` off | identities, statuses and verdicts byte-identical | — |
| F21 | U `u048` [4739, 4837) Art. 13(1), set `rs_u048` (four claim candidates and the candidate `liberty`: "move as well as reside within the borders of each state"), beside Art. 30 `u114` as a **fixed** bar unit, reading `rule` | `readings-elaborate`, `readings-model`, then the shadow test per choice | `sup D` has the bar node on the liberty's permission predicate `m`, generated by `correlate` unchanged; `Choice_D` holds `∀x̄. aimed_m(x̄) → χ_liberty`, labelled as quiescence of `rs_u048`'s candidate `liberty`; a base with `aimed_m` true somewhere and a claim candidate chosen is rejected as a model; under each claim choice every outcome on `m` equals that of the choice's own document, which has no bar node and no `aimed_m`; under `liberty`, the liberty is barred where `aimed_m` holds (`bar_blocks`). Without the quiescence premise the claim choices forbid `m` where `aimed_m` holds and `superpose_faithful` is false | bar unused; `rs_u048` checked alone |
| F22 | synthetic twin of F1 | two candidates with the same rule under two rule names (both strict; then both default) | no situation and probe separates them: `separates = false` throughout, set rejected as in F19. A probe on a rule name would have separated them | — |

## 6. Measured unlock and order

Blockers removed, from the ledgers of 2026-09-30T18:00Z. "Removed" means the unit's recorded primary blocker no
longer exists; a rerun and an audit decide what the unit becomes.

| Stage | UDHR (130 units, 10,916 bytes) | Constitution (1,127 units, 184,893 bytes) |
|---|---|---|
| S1 | 43 units, 4,175 bytes (38.2%): `force_variants_in_one_reading_set` removed; 4 companion sets (`u017`, `u052`, `u112`, `u114`: 65 + 182 + 121 + 225 = 593 bytes) move into the document | 14 sets, 1,833 bytes: separation checked in the document instead of a placeholder; the uniform-force coupling becomes writable; no status change |
| S2a (soft) | none: the UDHR is a rights document and stays on the enumerated fallback, which is over the 64-choice budget, so its premise and rights reports stay UNKNOWN | main document's premises and conflict status leave UNKNOWN; two companion documents become redundant |
| S2b (rights), only once the rights case of `superpose_faithful`, bar case included, is proved | premise and rights reports leave UNKNOWN; `u111` (337 bytes) acts on every candidate line; 4 units, 393 bytes `right_lines_in_reading_sets` removed; the Art. 30 bar usable | none beyond S2a |
| S3 | 2 units, 269 bytes (`u076`, `u108`) `act_phrase_grammar` removed; fidelity of 6 audited units, 783 bytes (`u035`, `u039`, `u041`, `u046`, `u054`, `u077`), plus `u033b`: no coverage gain, the claimed bytes stop overclaiming | none measured (the hard constraints' act-pointer workaround could use clauses) |
| S4 | none measured (Article 29's anchors are already LABELLED) | `u0214.s02` (one MIXED unit); 15 norm units admissible beside a manifest; upper bound 80 `other:discourse` units, of which the pilot review expects none promoted by references alone |
| S0 | enabler | enabler |

Order: S0, then S1, S2a, S2b (one lane, in sequence), with S3 and S4 as independent lanes once S0 is in (both
import S0's `Content` and slot only). If only one lane
runs: S0, S1, S2a, S2b, S3, S4. S1 before S2 because S1 alone changes unit statuses (READINGS needs elaborated
candidates and a distinguishing situation, rights 7.2) and S2's theorems are the larger proof risk. The UDHR rows
of S2 are a promise of S2b alone: nothing in them is unlocked by S2a.

## 7. Open questions

1. **Is `superpose_faithful` provable as stated for rights?** Rights' generated names are positional
   (`rights-fan-<k>`, `rights__lim__<k>`), so `sup D` and `choiceDoc D c` number them differently; the theorem goes
   through `nameMap`, and its proof needs a lemma that `correlate` commutes with deleting never-applying lines up
   to that map. For soft-only documents (the constitution) names derive from rule names and the map is the
   qualification alone. Decided in the design debate: the soft-only case is proved and shipped first (S2a); rights
   documents use the enumerated fallback until the rights case, bar case included, is proved (S2b). As stated in
   draft 1 the theorem was false with a fixed bar: `sup D` has a bar node on every permission predicate some
   candidate liberty makes right-derived, and a choice without that liberty has none. The owner-based quiescence
   of `aimed_m` (2.3) repairs it, and F21 is the fixture the statement review attacks first.
2. **Superposition can fail where every choice is fine** (F18). How often on real documents is unmeasured; the
   pilots' candidates guard on base predicates only, where it cannot happen.
3. **What the force question may claim.** In a document, the strict and default readings differ in three ways (the
   exception; giving way to a strict rule instead of conflicting; blocking other defaults). The plan proves only the
   isolated statement and asks the IDE to list all three. Is one sentence each enough for an untrained reader?
   This needs the W8 fidelity gate, not a theorem.
4. **Separation through a decision assignment** is weaker than separation in the author's vocabulary: the strict
   and default readings agree in every situation unless a decider says the exception applies. Decided in the
   design debate: decision-based separation is kept, since requiring a cited or sufficient exception condition
   would block the 43 units again and add no truth. Such a set carries the finding `SeparatedByDecisionOnly`, and
   the IDE says "suppose *the decider* decides the exception applies", never a sentence that states the decision
   as a fact of the situation (2.4, section 3).
5. **Size.** `sup D` for the UDHR holds 67 right candidates today and roughly 150 after S1; soft's unfolded
   carve-outs and the conflict targets grow with them, and 20 right sets already cost 85 s per load. S2's
   acceptance measures it; if `MAX_NODES` is hit the verdict is UNKNOWN and a per-component split (superpose only
   sets whose candidates share an act) is the next design.
6. **NONE beyond 64 choices** has no single-witness form. The plan reports "not ALL, with a countermodel reading".
   Is a weaker named verdict worth a W2 change?
7. **Provenance mentions** (2.8) record a translator's resolution without a uniqueness claim. They make translated
   norm units admissible beside a manifest, but they are attributed interpretation, not checked resolution. The
   alternative is to require every translated unit with a reference to carry a fence. Decided in the design
   debate: if admitted, a provenance mention is reported only as attributed, is counted separately, and never
   changes a status; whether it is admitted is decided in S4's specification after question 14's tally. S4's
   measured unlock is small either way.
8. **A reference as a reading axis inside a rule** (two antecedents for "it" in a guard): candidates would differ
   only in a resolved position. The model allows it (candidates are resolved contents), but discourse records one
   target per slot. Left to the S4 specification.
9. **The bar** is enumerated because `correlate` cannot be gated. If a third enumerated axis appears, the right fix
   is a `rights@1` whose generated nodes take a guard, with the faithfulness theorems restated. A fixed bar needs
   no enumeration and no change to `correlate`: its generated node is silenced through `aimed_m` (2.3, F21).
10. **Candidates of more than one content** ("a liberty protected by a claim" as one candidate when the lines belong
    to two rights) are excluded; a right block with several lines already covers the single-right case.
11. **The totality premise is existential** and removes the document from norms 7's fragment. Whether a universal
    surrogate (a declared function symbol is outside the logic) exists is open; the cost is stated in the report.
12. **Rust** has no norm elaboration; it evaluates Python-generated formulas of `sup D` marked untrusted. That is
    the discourse precedent, and it means three-way agreement for S1 to S3 is Lean authority plus two-way
    differentials, not three independent implementations.
13. **`norm-defaults@0` order.** `fill` must run after superposition (its synthetic rule is lowest priority on the
    whole predicate). `Fill_T` then joins `slotP`. Whoever merges second adds the instance; neither blocks the other.
14. **The 80 `other:discourse` units have no byte tally** in `metrics.json`, and no count of reference-bearing
    sentences among the 668 `norms`-blocked units exists. S4 should start with that tally; if it is small, S4 drops
    below every other queued feature.
15. **Profile names and count.** `readings@1` and `right-clauses@0` are proposals. Folding clauses into a
    `rights@1` would save a profile and cost a restated rights wire.
16. **The choice vocabulary needs one element.** `ve__here` must denote something, and a structure may have an
    empty carrier (`Structure.constant` is `String → Option Carrier`). Resolved in the design debate, in three
    parts. (a) `superpose_conflict_free` needs no hypothesis: a regulated predicate has arity 1 or 2, so
    `ConflictFree` quantifies over typed tuples of length at least 1 and is vacuous on an empty carrier, and every
    admissible structure of `sup D` interprets `ve__here`, so it has an element. (b) `superpose_all` must cover
    empty author structures to match W2's entailment, so it drops the hypothesis through the lifting lemma stated
    in S2: adjoining one element that lies in no author sort preserves `BaseAdmissibleR` and the denotation of
    every author formula (quantifiers range over `S.domain s`). The lemma is expected to hold and is not proved; it
    is an obligation of the statement review, not a reason to weaken the ALL claim. If it fails there, the
    hypothesis stays and reports say "every reading with at least one individual", never "every reading". (c)
    `base_up` keeps the hypothesis either way. The logic has no nullary predicate; adding one would remove the sort
    and the constant, and is a frozen-contract change this plan does not ask for.

## 8. Not claimed, and out of scope

No coverage number. No theorem that a reading set is exhaustive, that a coupling or narrowing is the right
interpretation, that a relation's table is correct, or that a translator's resolution is the author's. No
completeness of the conflict check outside norms 7. No composition with speech acts, reports, alternatives, risk,
quantities, definitions or data (2.9 only fixes where each would attach). No change to act phrases, to any
`rights@0`, `soft-norms@0`, `norms@0` or `ve-document@1` identity, or to a frozen Lean file. No English parsing
work beyond registering the wordings named in section 3 (W7) and the IDE questions (W8), each behind its own gate.

## 9. Process

Draft 1 went to the Astra + Fable design debate (`manage-agents/debates/design-compose/`), with questions 1, 4
and 7 as the named points of attack. It converged after round 3 on REVISE: draft 2 (this file), then BUILD through
statement review with no second design debate. The orchestrator checks draft 2 against section 10. Then: S0's
statements ([composition.md](composition.md)) are reviewed and built first (small, no behaviour change). That
review converged on FIX after round 3 (`manage-agents/debates/compose-spec/`): eight edits, applied in
composition.md draft 2, none to a Lean statement. Both seats recheck that diff once, and S0's Lean starts after
the recheck without a new debate. S1, S3 and S4 get item-1 specifications in parallel (`readings.md`,
`right-clauses.md`, an amendment section of `discourse.md`), each with its statement review before Lean. S1's specification starts from the probe key and
the shared base (section 10, edits 4 and 5). S2's specification follows S1's merge, and its statement review
attacks `superpose_faithful` with F21 before the rights case. Every stage ends with both pilots rerun and audited,
and section 6's table replaced by measured results.

## 10. The converged edits and where each was applied

Source: `manage-agents/debates/design-compose/{astra,fable}.md`, CONVERGED after round 3 (`result.txt`). The joint
position is Fable's round 3 list, accepted by the Astra seat's round 3; items are numbered as in Fable's round 1
(edits 1 to 7), followed by the two reporting wordings and the Astra seat's four corrections. Nothing else changed
between draft 1 and draft 2.

| # | Converged edit | Change in this draft |
|---|---|---|
| 1 | `superpose_faithful` is false with a fixed bar. Quiescence for every generated predicate some choice's document lacks, `g → ⋁ χ(owners)`, `aimed_m` included when its permission has only candidate owners; the fixed bar's implementation kept intact; fixture F21 | 2.3 (quiescence rewritten, the per-choice paragraph), 2.6 (the bar), S2 (`superpose_faithful` comment, S2b acceptance), section 5 (F21), section 7 (questions 1 and 9) |
| 2 | Rule 2 contradicts 2.3: quiescence names a later layer's vocabulary; rule 2 states the exception | 2.1 rule 2 |
| 3 | `dispatch`, in the Astra seat's form: today's route on every list that has one (the alternatives, risk, speech-acts and reports routes preserved); the `Except` branch only outside both today's lists and the validated chain | 2.1 rules 1 and 6, 2.8, 2.9, S0 (`Route`, `today`, `dispatch`, `dispatch_today`, `today_sound`, `dispatch_chain`, `dispatch_error`, acceptance), section 3 |
| 4 | Drop `Probe.selects (rule)`; probe key `(kind, predicate, tuple)`, today's key; renamed-twin fixture | 2.4, S1 (`Probe`, `selectable`, `Observes`, acceptance), section 5 (F22) |
| 5 | 2.4 and `Achieves` disagree: fixed units' decisions go into the shared base, so they are not enumerated | 2.4 (situation, `Achieves`, the bound), S1 (`sharedBase`, `sharedName`, `Achieves`, `separates`, `separates_sound`) |
| 6 | Section 6 overstates S2 for the UDHR: S2a (soft) first, S2b (rights) on the enumerated fallback until the rights `superpose_faithful`, bar case included, is proved | section 0, 2.6, S2 (two milestones, split acceptance), section 6 (two rows, the order), section 7 (question 1) |
| 7 | Formula-only sets: 2.1 and `sup_no_sets` stated different identity cases; 2.5 dropped W2's shared-model NONE: W2's ALL and NONE route kept verbatim. Declared names distinct across sets, checked across sets, as a precondition of `choice_wellFormed` (the Astra seat's wider form: every declared name, not only rule names) | 2.1 (the Readings row), 2.5 (the formula-only paragraph, the NONE row), section 3; 2.2 (distinct declarations across sets), S1 scope, S2 (`choice_wellFormed`) |
| Q4 | Keep decision-based separation; finding `SeparatedByDecisionOnly`; the IDE says "suppose *the decider* decides the exception applies" | 2.4 (the Force bullet, the finding), section 3 (the force question), S1 scope, section 7 (question 4) |
| Q7 | Provenance mentions: attributed, counted separately, never changing a status; decided in S4's specification after question 14's tally | 2.8, S4 scope, section 5 (F17), section 7 (question 7) |
| A1 | A fixed rule's `over` or `cites` reference to a name every candidate declares maps to every qualified copy | 2.2 (interface name), 2.3 (`sup D`) |
| A2 | The combined slot `Lim_D ++ Choice_D ++ gated Rel_D`, with labels and per-choice model correspondence; a candidate's totality premise enters as `χ → ρ`; one rule: `sup` gates everything a candidate owns or causes | 2.1 rule 4, 2.3 (the rule, `Rel_D, gated`, `combined slot`), 2.7, S2 (`gatedRel`, `slotP`), S3, section 5 (F13) |
| A3 | Empty carrier: `superpose_conflict_free` needs no hypothesis (argument recorded); `superpose_all` drops it through the lifting lemma, stated explicitly; fallback wording "every reading with at least one individual"; `base_up` keeps it | 2.5, S2 (`superpose_conflict_free`, `adjoinOne`, `adjoin_denote`, `adjoin_baseAdmissible`, `superpose_all`), section 7 (question 16) |
| A4 | `Content` in a shared predecessor module (`VE.Compose.Content`, S0), so S3 and S4 are independent of S1 and S2 | section 0, S0 (scope, `Content`), S1 (`open`), S4 (`positions`, `resolveContent`), section 6 (the order) |

Two precisions were needed to write the converged edits down and are flagged for the statement reviews, not
decided here. First, in edit 1 an owner may be a pair of candidates of different sets (a candidate limitation with
a candidate line in its scope; two candidate default rules whose collision generates an `outweighs` predicate), so
a disjunct of `⋁ χ(owners)` may be a conjunction of atoms (2.3). Second, in edit 5 the shared base names the fixed
units' generated predicates by source key, because rights' generated names are positional and two candidates'
documents may number them differently (`sharedName`, S1).

## Change log

| Date | Revision | Changes |
|---|---|---|
| 2026-10-01 | Draft 1 | First plan: the stack and its six rules; content-bearing candidates; superposition with choice premises; separating situations over a shared base with private decision assignments; per-reading rights; structured lines with clauses, relation and `elided`; discourse on the chain; five stages with Lean statements, twenty pilot fixtures, the measured unlock table and fifteen open questions. Design only. |
| 2026-10-01 | Draft 2 | The converged design debate applied, nothing else (section 10): owner-based quiescence including `aimed_m` under a fixed bar, with F21; rule 2's stated exception; `dispatch` preserving every route of today, with an error branch only outside today's lists and the validated chain; the probe key `(kind, predicate, tuple)` with the renamed-twin fixture F22; fixed units' decisions in the shared base; S2 split into S2a (soft) and S2b (rights, enumerated until proved), with the UDHR unlock qualified; W2's formula-only ALL and NONE route kept; names distinct across sets; fixed `over` and `cites` references mapped to every qualified copy; the combined slot `Lim_D ++ Choice_D ++ gated Rel_D`; the empty-carrier resolution with the lifting lemma and the fallback wording; `Content` in S0; the findings and wordings of questions 4 and 7. The statement specification of the stack contract and S0 is [composition.md](composition.md). Design only. |
| 2026-10-01 | Draft 2, statement-review amendment | The converged statement review of composition.md applied where it reaches this plan (`manage-agents/debates/compose-spec/`, FIX after round 3), nothing else. A gated relation premise's slot label is `rights:relation:<line>:total under <set>@<v>:<i>`, naming its reading in the slot itself, and `conditional_on` lists slot labels verbatim (2.3 `Rel_D, gated` and `combined slot`; 2.7 the relation bullet and the fragment line). Pointers only: section 3 (the force question is E14's narrow case; other pairs are worded by their probe; no "may not"), S0's acceptance (fixture D-all's Lean half), section 9 (the review's outcome and the remaining recheck). No statement, fixture F1 to F22 or stage changed. Design only. |
