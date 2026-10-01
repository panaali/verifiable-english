# Feature composition: plan (one stack for references, readings and norms)

> Status: planning draft 1 (2026-10-01), design only: no code, Lean or frozen contract changes. Baseline `main` at
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

Stages, in order of measured unlock (section 6): S0 the base-premise slot and the dispatcher (enabler); S1
content-bearing norm candidates with Lean-checked separating situations; S2 superposed verdicts and per-reading
rights elaboration; S3 structured right lines; S4 discourse on the chain. S3 and S4 are independent of S1 and S2.

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
| Line shape (scope, trigger and object clauses; bearer–holder relation) | `right-clauses@0` | right lines with `clauses`, `relation` | `rights@0` lines with larger guards; relation premises `Rel_D` | no clause, no relation: the line unchanged |
| Readings (which candidate each unit takes; couplings, constraints, narrowings) | `readings@1` | fixed units, reading sets with content | one reading-free document `sup D`; choice premises `Choice_D` | no content-bearing norm or right set: `sup D = D` |
| Holders, incidents, limitations, the bar | `rights@0` | rights document | soft document; `Lim_D` | rights 9.2 `correlate_identity_top` |
| Force, exceptions, switches, ranks | `soft-norms@0` | soft document | W1 tree; `Soft_T` | soft-norms 5.1 (all rules hard: `T′ = T`) |
| Silence (unmerged) | `norm-defaults@0` | W1 tree with `unspecified` | W1 tree; `Fill_T` | no unspecified predicate |
| Applicability, completion, conflict | `norms@0` | W1 tree | layer premises `elab_p` | no regulated predicate |
| Truth, proof, countermodels | frozen route | premises, conclusion | certificate or finite model | — |

Rules of the stack (the contract a layer signs to be placed in it):

1. **One position.** A profile has one rank in the order above. A wrapper validates and strips its own profile,
   then calls `dispatch` on the remaining profiles (S0), never a specific route. Today's routes are `dispatch`'s
   values on today's profile sets.
2. **Source in, same kind out.** A layer's output is a document its successor already accepts. No layer reads a
   later layer's generated vocabulary; later layers never see an earlier layer's constructs.
3. **Regenerated, never trusted.** Every derived object (resolved contents, `sup D`, `Choice_D`, `E″`, `T′`, layers)
   is recomputed from the decoded document at every trusted site and bound to the document hash; none is on the wire
   as authority.
4. **Premises only through slots.** A layer may add closed formulas over the base vocabulary to base admissibility
   (as `Soft_T` and `Lim_D` do). They are labelled, listed in `conditional_on` when used, and enter through one
   generic lemma (S0), so a new layer restates no route theorem.
5. **Identity when unused**, as a Lean theorem, so every existing document keeps its bytes, identities and verdicts.
6. **Abstention is named.** A combination outside the stack is `UnsupportedProfile: <a> with <b>`, never a silent
   drop of a block (INTEGRATION-GAPS's rule).

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

Admission conditions on a set, checked per candidate in the context of the fixed units, so linear in candidates:

- **Closure.** A candidate names (in `over`, `cites`, `scope`, `right_lines.right`) only fixed names or names it
  declares. A fixed unit may name something a set declares only if every candidate of that set declares it
  (`ReadingInterface: <set>: <name>` otherwise). So `Right 18 includes: …` is admissible exactly when every
  candidate of `rs_u066` declares right 18.
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
sup D               F unchanged, then for every candidate a_{s,i} (k its position in the canonical order: sets in
                    source order, candidates by index):
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
  quiescence          ∀x̄. g(x̄) → χ_{s,i} for every generated predicate g owned by one candidate: its rules'
                      soft__excepted__…, soft__off__…, a candidate limitation's rights__lim__…, rights__cond__…
                                                                                         readings:<set>@<v>:<i>:quiet
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
exception premises hold, and an unchosen limitation's predicates are empty, so its packed carve-out is false. What
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
situation        base: a finite model over the author's base vocabulary (E_base, flags, literals)
                 decisions: tables for the generated predicates of the witnessing candidate only
probe            the outcome of a regulated predicate at a tuple | whether a named rule or line selects at a tuple
                 | (formula candidates) the candidate's own truth
Achieves(a, B, q, v)   some decision assignment over B makes "fixed units + a" admissible with probe q = v
Separated(a, b)        ∃ B, q, v. Achieves(a, B, q, v) ∧ ¬ Achieves(b, B, q, v), or the same with a and b exchanged
```

The checker is given `(base, decisions, probe)` for one side, evaluates it, then enumerates every decision
assignment of the other side on the same finite base (at most 2¹² assignments, `ResourceLimit: decision
assignments` beyond, never a verdict) and requires that none reaches the same probe value. Lean's `separates` is
the authority (`separates_sound`, S1); Python searches for the situation and Rust replays the evaluation untrusted.

- **Force.** For `u0156.s03` the base situation has one instance of Claude and one user; under the defeasible
  candidate the exception applies there, so avoiding the deception is not required; the strict candidate has no
  decision to make and requires it. One shared situation, checked. If a default candidate's exception can never
  apply (a necessary condition that is unsatisfiable), nothing separates it from the strict candidate and the set
  is rejected: the two wordings then say the same thing.
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

| Question | Evidence on `sup D` | Report |
|---|---|---|
| Does φ follow under every reading? (ALL) | one certificate from `background ++ Choice_D ++ layers ++ Γ`; its used leaves name the sets it needed | `readings:<set>@<v>:all` for a set some used leaf mentions with no atom of it assumed; `readings:<set>@<v>:<i>` when an atom was assumed; nothing for a set no used leaf mentions ("does not depend on how sentence 7 is read") |
| Under a named reading? | the same with that choice's atoms as premises | the choice listed |
| SOME | a certificate under one named choice and a checked countermodel whose atoms encode another | both choices listed |
| NONE | a countermodel per compatible choice, enumerated up to 64 | beyond 64: `UNKNOWN (not ALL: countermodel under <choice>)` |
| Can the rules contradict each other? | W1's conflict targets on `sup D` over `Background_base ++ Choice_D`: one certificate per target covers every reading; a witness's atoms name the reading it is a conflict of | CONFLICT-FREE under every reading, conditional on the listed coherence, limitation and choice premises / CONFLICT under <choice> at <situation> / UNKNOWN |
| Are the premises consistent? | one model (a reading and a situation); then one model per candidate with its atom true | consistent under <choice>; `DeadReading: <set>:<i>` with a certificate of `¬χ_{s,i}` for a candidate no compatible choice can use |

Soft's classification of colliding default pairs runs on `sup D` with `Choice_D` among its premises. A pair of
rules from two candidates of one set has contradictory atoms in its two guards, so it is DISJOINT by a certificate
that needs no premise, and is never listed as a weighing point.

### 2.6 Rights per reading

Nothing is added to `rights@0`; it receives `sup D`.

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
  be an open term with a decider.
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
(`fragment: no (rights:relation:<line>:total)`); certificates and witnesses still decide, completeness does not.

### 2.8 References on the chain

Discourse 5 already states the contract (an elaborated norm unit enters W1 as ordinary content; soft's coherence
premises are retained; anything touching the `soft` block is `UnsupportedTarget`). What is missing is the route and
three definitions.

- **Dispatch.** After validating and stripping `ve.discourse@1`, the wrapper calls `dispatch` (S0) on the base pair
  instead of the frozen admission: the chain's admission when `norms@0` is enabled, the frozen one otherwise. The
  environment is decoded by the chain's decoder, which knows `regulated`, `soft` and `rights`.
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
  elaboration. No uniqueness claim is made about the prose, and the report says "resolved by the translator". The
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
one instance of the slot lemma, not a new route.

## 3. VE's properties under composition

- **One reading per sentence.** Every candidate is a VE content with one derivation; superposition never lets one
  sentence be read two ways inside one argument, because `Choice_D` makes each choice global per unit (W2's rule).
  Resolution closes references before anything is a candidate. Provenance mentions (2.8) claim nothing about prose.
- **Zero-training English.** No new norm word. The force question the IDE asks is English with one situation:
  "This sentence says *shall*. (1) *Every state must secure social security for each person.* (2) *Every state
  should secure social security for each person, unless an exception applies.* They differ here: Ruritania lacks
  the resources and the exception applies. Under (1) Ruritania still must. Under (2) it is not required to."
  Verdicts read "Under every reading of the 14 open sentences, no two rules contradict" and "Read sentence 12 as
  *must* and sentence 15 as *should*: rules 12 and 15 contradict when …". Clauses are ordinary "if … and …"
  sentences; the relation is "where that state is the country of that person"; totality is "Every person has at
  least one country." W7 registers each wording and each passes the all-derivations gate before it is offered.
- **Small verified core.** No new operator, checker rule or judgment kind. New Lean is three elaborations
  (`sup`, `plain`, position-wise `resolve`), one executable check (`separates`) and their faithfulness theorems;
  every route theorem is the generic slot lemma instantiated.
- **Python, Lean and Rust agree.** Lean is the authority for all new semantics (SEMANTICS-MIGRATION section 6;
  discourse 3.4's "Python's admission is Lean's" is extended to the composed route). Python checks shape, searches
  for situations and certificates, renders English. Rust evaluates the regenerated formulas of `sup D` marked
  untrusted. Diagnostics follow one order: stack order, then each layer's own table.
- **Conservativity.** Profiles off: every construct here is rejected as today. Profiles on with nothing used: the
  identity theorems (`sup_no_sets`, `plain_identity`, `resolve_identity`, `dispatch_base`) give byte-identical
  elaboration. No frozen file, canonical byte, identity or theorem statement changes; `rights@0`'s right sets keep
  today's validation when `readings@1` is off. The only verdict that moves is UNKNOWN ("elaboration pending"), in
  documents that opt in.

## 4. Stages

Each stage is one branch, mergeable alone, with its own item-1 specification (statements and fixtures reviewed by
Astra and Fable before Lean starts), Lean, Python, conformance and a pilot rerun as acceptance.

### S0. The slot lemma and the dispatcher (enabler; no behaviour change)

Scope: `lean/VE/Compose/{Slot,Dispatch}.lean`, `lean/COMPOSE.md`. No executable changes its answers.

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

/-- The chain head for a profile list; on today's lists it is today's route. -/
def dispatch (profiles : List String) : Route
theorem dispatch_base (ps) (h : "norms@0" ∉ ps) : dispatch ps = .frozen
theorem dispatch_chain (ps) (h : "norms@0" ∈ ps) :
  dispatch ps = if "rights@0" ∈ ps then .rights else if "soft-norms@0" ∈ ps then .soft else .norms
end VE.Compose
```

Acceptance: the Lean audit passes with the unchanged allowlist; `rights_route_acceptance` and
`rights_route_countermodel` are re-derived as instances (their statements untouched); no conformance output moves.

### S1. Content-bearing candidates and separating situations (`readings@1`, part A)

Scope: the wire of 2.2, admission of a set (closure, each candidate elaborates, separation), `labels` and
`couplings` on every kind, the finding `SeparatedByActOnly`. Document verdicts over such sets stay UNKNOWN
("superposition pending") until S2, as rights sets are today. Files `lean/VE/Readings/{Doc,Separate,Wire,Run}.lean`,
target `ve_readings_route` (root `ReadingsMain.lean`), `lean/READINGS.md`; Python `ve/readings.py` gains the
situation search and delegates the verdict to Lean.

```lean
namespace VE.Readings
open VE.Norms (Regulated Sat tupleVal)
open VE.SoftNorms (ValueSoft SelectsSoftD)
open VE.Rights (RightsDoc correlate limPremises WellFormedRights)
open VE.Compose (BaseAdmissibleP)

inductive Content
  | assertion (φ : VE.Formula) | norm (N : VE.SoftNorms.SoftNode) | right (R : VE.Rights.Right)
  | rightLines (right : String) (ls : List VE.Rights.SourceLine) | limitation (L : VE.Rights.Limitation)
structure Candidate where id : String; content : Content; labels : List (String × String)
structure ReadingSet where id : String; unit : String; version : Nat; candidates : List Candidate
structure Doc where
  base : RightsDoc                 -- the environment with its blocks and the fixed norm, right, limitation, bar units
  asserted : List VE.Formula       -- the fixed assertion units
  sets : List ReadingSet           -- active versions, source order
  couplings : List Coupling; constraints : List Constraint; narrowings : List Narrowing

/-- Fixed units plus candidate i of set s, and the assertions in force (the candidate's own, if it is a formula). -/
def one (D : Doc) (s : String) (i : Nat) : RightsDoc × List VE.Formula
def authorBase (D : Doc) : List String                         -- base predicate names of E: no generated name
inductive Probe (α : Type) | outcome (p : String) (vs : List α) | selects (rule : String) (vs : List α) | holds

/-- Probe q has value v in S for the document X with assertions A. -/
def Observes (X : RightsDoc) (A : List VE.Formula) (S : VE.Structure) : Probe S.Carrier → Bool → Prop
  | .outcome p vs, v => ∃ r ∈ (correlate X).T.regulated, r.name = p ∧ ValueSoft (correlate X) r S vs = some v
  | .selects n vs, v => ∃ N ∈ (correlate X).T.nodes, N.name = n ∧
      (SelectsSoftD (correlate X) S (tupleVal vs) (VE.SoftNorms.fuel (correlate X)) N ↔ v = true)
  | .holds, v        => ((∀ a ∈ A, a.denote S []) ↔ v = true)

/-- Some decision assignment over the shared base B makes the candidate's document admissible with q = v. -/
def Achieves (D : Doc) (s : String) (i : Nat) (B : VE.Structure) (q : Probe B.Carrier) (v : Bool) : Prop :=
  ∃ R : String → List B.Carrier → Prop, (∀ p ∈ authorBase D, ∀ vs, R p vs ↔ B.relation p vs) ∧
    BaseAdmissibleP (correlate (one D s i).1) (limPremises (one D s i).1) { B with relation := R } ∧
    Observes (one D s i).1 (one D s i).2 { B with relation := R } q v
def Separated (D : Doc) (s : String) (i j : Nat) : Prop :=
  ∃ (B : VE.Structure) (q : Probe B.Carrier) (v : Bool),
    (Achieves D s i B q v ∧ ¬ Achieves D s j B q v) ∨ (Achieves D s j B q v ∧ ¬ Achieves D s i B q v)

/-- The executable check: evaluate the witnessing side on base + decisions, then every decision assignment of the
    other side on the same finite base (bounded; false when the bound is exceeded). -/
def separates {α} [DecidableEq α] (D : Doc) (s : String) (i j : Nat) (M : VE.FiniteModel α)
    (decisions : List (String × List (List α))) (q : Probe α) : Bool
theorem separates_sound {α} [DecidableEq α] (D : Doc) (hD : WellFormedDoc D = true) (s) (i j) (M) (decisions) (q)
    (valid : M.Valid (authorEnv D)) (h : separates D s i j M decisions q = true) : Separated D s i j

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

Acceptance: fixtures F1 to F6, F15, F19, F20; differential `readings-validate` Python search versus Lean check on
1,000 generated sets (strict/default twins, mixed kinds, renamed twins that must **not** separate); the
constitution's 14 sets and the UDHR's 4 norm-candidate sets validate in-document with their stored situations.

### S2. Superposed verdicts and per-reading rights (`readings@1`, part B)

Scope: `sup`, `Choice_D`, the verdict table of 2.5, 2.6 including the enumerated bar axis and the fallback, W2
`readings:` labels on certificates, `DeadReading`. Files `lean/VE/Readings/{Superpose,Choice,Route,Admission}.lean`.

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
def slotP (D : Doc) : List VE.Formula := limPremises (sup D).1 ++ choicePremises D
def Encodes (D : Doc) (c : Choice) (S : VE.Structure) : Prop :=
  ∀ R ∈ D.sets, ∀ i, i < R.candidates.length → ((atom D R.id i).denote S [] ↔ (R.id, i) ∈ c)
def nameMap (D : Doc) (c : Choice) : String → String       -- a generated name of choiceDoc D c ↦ its name in sup D
def pull (ν : String → String) (S : VE.Structure) : VE.Structure := { S with relation := fun p vs => S.relation (ν p) vs }

theorem sup_wellFormed (D : Doc) (h : WellFormedDoc D = true) (hs : superposable D = true) :
  WellFormedRights (sup D).1 = true
theorem choice_wellFormed (D) (h : WellFormedDoc D = true) (hs : superposable D = true) (c) (hc : Compatible D c) :
  WellFormedRights (choiceDoc D c).1 = true
theorem sup_no_sets (D : Doc) (h : D.sets = []) : sup D = (D.base, D.asserted) ∧ choicePremises D = []

/-- Every admissible base of sup D is one compatible choice. -/
theorem encodes_unique (D) (h) (hs) (B : VE.Structure) (hB : BaseAdmissibleP (correlate (sup D).1) (slotP D) B) :
  ∃ c, Compatible D c ∧ Encodes D c B ∧ ∀ c', Encodes D c' B → c' = c

/-- 2.3: where exactly c's atoms hold, the superposed document decides every act as c's document does. -/
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

/-- Conflict-free under every reading, in one check. -/
theorem superpose_conflict_free (D) (h) (hs) :
  VE.Compose.ConflictFreeP (correlate (sup D).1) (slotP D) ↔
    ∀ c, Compatible D c → VE.Rights.RightsConflictFree (choiceDoc D c).1

/-- ALL: a certificate on sup D proves φ in every reading's document. Γ and φ are over the author's vocabulary. -/
theorem superpose_all (D) (h) (hs) (hcf : VE.Compose.ConflictFreeP (correlate (sup D).1) (slotP D))
    (Γ : List VE.Formula) (φ : VE.Formula) (hΓ : ∀ a ∈ Γ, AuthorFormula D a) (hφ : AuthorFormula D φ)
    (cert : VE.Tableau.Certificate) (accepted : supCertificateCheck D Γ φ cert = true)
    (c : Choice) (hc : Compatible D c) (B : VE.Structure) (hne : Nonempty B.Carrier)
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

Acceptance: fixtures F3, F6 to F10, F18; `readings-elaborate` differential on 1,000 generated documents with faulty
sources rejected by both; on every generated document with at most 64 choices, the superposed verdict equals the
enumerated one (ALL, conflict status, premise status), which is the executable shadow of the theorems; pilot
reruns: both main documents leave `premises: UNKNOWN`; U `limitation_terms > 0`; load time reported against the
85 s the 20 right sets cost today.

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
stated for a binary claim. The route is the slot lemma at `P := limPremises (plain D) ++ relPremises D`.

Acceptance: fixtures F11 to F14; rights' seventeen fixture shapes unchanged with the profile on and no clause
(`plain_identity`); every unit of the UDHR rerun reports `elided_bytes`; the audit's seven units are re-audited.

### S4. Discourse on the chain (`ve.discourse@1`, amendment; `ve-document@2`)

Scope: 2.8. Files `lean/VE/Discourse/{Positions,Compose}.lean`; the discourse loader's three abstentions become
implementations; `ve/profiles.py` and the Lean gate admit `ve.discourse@1` beside the chain.

```lean
namespace VE.Discourse
/-- The formula positions of a content with their contexts, in canonical order (2.8). -/
def positions : VE.Readings.Content → List (List String × VE.Formula)
def resolveContent (E) (K : Manifest) (unit : String) (c : VE.Readings.Content) : Except String VE.Readings.Content

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
| F13 | U `u054` [5239, 5284) Art. 15(1) | set {assertion "each person has some nationality", assertion "some state grants each person one", claim with relation `responsible_for` and `total`} | mixed-kind set admitted; under the claim, `relation_some_bearer` gives a bearer per person; the claim candidate is separated from "every state must grant" by a two-state situation | strengthened, then assertions only |
| F14 | U `u077` [6861, 6938) Art. 21(2) "in his country" | claim with relation `country_of`; second candidate without it | separated by a situation with a state that is not the person's country | "strengthened": relation dropped |
| F15 | U `u032` Art. 7 as rejected on 2026-09-30 ("avoid denying equal protection" / "give equal protection" on two predicates) | set of the two | admitted with finding `SeparatedByActOnly` naming both act phrases | separated "only by predicate name", found by the audit |
| F16 | C `u0214.s01`, `u0214.s02` in the translation with its norm units and fenced `u0248` | `ve-document@2`, profiles including `norms@0`, `soft-norms@0` | admitted by the Lean route; `u0214.s02` MIXED with parts LABELLED and UNFORMALISED as discourse 2.5; norm verdicts equal those without the `discourse` block | `UnsupportedProfile`; four failures |
| F17 | C `u0078.s01` [48052, 48503), reference surface at [48274, 48278) | translated norm unit with a provenance mention | admitted; report line "resolved by the translator"; without the mention `UnrecordedSlot` as today; with a target of the wrong sort `IllTypedTarget` | `UnrecordedSlot` |
| F18 | synthetic, shaped on the hard constraints | two sets whose candidates stratify alone and cycle together | `ReadingsNotSuperposable: <sets>`; the enumerated fallback gives the verdict (4 choices) | — |
| F19 | synthetic twin of F1 | default candidate whose exception has an unsatisfiable necessary condition | set rejected: "distinguishing situation does not separate readings" | — |
| F20 | U translation `document_id 97f65591…4533`; rights fixtures; discourse fixtures α to ω | `readings@1`, `right-clauses@0` off | identities, statuses and verdicts byte-identical | — |

## 6. Measured unlock and order

Blockers removed, from the ledgers of 2026-09-30T18:00Z. "Removed" means the unit's recorded primary blocker no
longer exists; a rerun and an audit decide what the unit becomes.

| Stage | UDHR (130 units, 10,916 bytes) | Constitution (1,127 units, 184,893 bytes) |
|---|---|---|
| S1 | 43 units, 4,175 bytes (38.2%): `force_variants_in_one_reading_set` removed; 4 companion sets (`u017`, `u052`, `u112`, `u114`: 65 + 182 + 121 + 225 = 593 bytes) move into the document | 14 sets, 1,833 bytes: separation checked in the document instead of a placeholder; the uniform-force coupling becomes writable; no status change |
| S2 | premise and rights reports leave UNKNOWN; `u111` (337 bytes) acts on every candidate line; 4 units, 393 bytes `right_lines_in_reading_sets` removed; the Art. 30 bar usable | main document's premises and conflict status leave UNKNOWN; two companion documents become redundant |
| S3 | 2 units, 269 bytes (`u076`, `u108`) `act_phrase_grammar` removed; fidelity of 6 audited units, 783 bytes (`u035`, `u039`, `u041`, `u046`, `u054`, `u077`), plus `u033b`: no coverage gain, the claimed bytes stop overclaiming | none measured (the hard constraints' act-pointer workaround could use clauses) |
| S4 | none measured (Article 29's anchors are already LABELLED) | `u0214.s02` (one MIXED unit); 15 norm units admissible beside a manifest; upper bound 80 `other:discourse` units, of which the pilot review expects none promoted by references alone |
| S0 | enabler | enabler |

Order: S0, then S1, S2 (one lane, in sequence), with S3 and S4 as independent lanes once S0 is in. If only one lane
runs: S0, S1, S2, S3, S4. S1 before S2 because S1 alone changes unit statuses (READINGS needs elaborated candidates
and a distinguishing situation, rights 7.2) and S2's theorems are the larger proof risk.

## 7. Open questions

1. **Is `superpose_faithful` provable as stated for rights?** Rights' generated names are positional
   (`rights-fan-<k>`, `rights__lim__<k>`), so `sup D` and `choiceDoc D c` number them differently; the theorem goes
   through `nameMap`, and its proof needs a lemma that `correlate` commutes with deleting never-applying lines up
   to that map. For soft-only documents (the constitution) names derive from rule names and the map is the
   qualification alone. Proposal: prove the soft-only case first and ship S2 for it; rights documents use the
   enumerated fallback until the rights case is proved. The statement review should attack this theorem first.
2. **Superposition can fail where every choice is fine** (F18). How often on real documents is unmeasured; the
   pilots' candidates guard on base predicates only, where it cannot happen.
3. **What the force question may claim.** In a document, the strict and default readings differ in three ways (the
   exception; giving way to a strict rule instead of conflicting; blocking other defaults). The plan proves only the
   isolated statement and asks the IDE to list all three. Is one sentence each enough for an untrained reader?
   This needs the W8 fidelity gate, not a theorem.
4. **Separation through a decision assignment** is weaker than separation in the author's vocabulary: the strict
   and default readings agree in every situation unless a decider says the exception applies. The definition is
   honest about it ("if the exception applies here"); reviewers may prefer to require a cited or sufficient
   exception condition before a force set counts as READINGS.
5. **Size.** `sup D` for the UDHR holds 67 right candidates today and roughly 150 after S1; soft's unfolded
   carve-outs and the conflict targets grow with them, and 20 right sets already cost 85 s per load. S2's
   acceptance measures it; if `MAX_NODES` is hit the verdict is UNKNOWN and a per-component split (superpose only
   sets whose candidates share an act) is the next design.
6. **NONE beyond 64 choices** has no single-witness form. The plan reports "not ALL, with a countermodel reading".
   Is a weaker named verdict worth a W2 change?
7. **Provenance mentions** (2.8) record a translator's resolution without a uniqueness claim. They make translated
   norm units admissible beside a manifest, but they are attributed interpretation, not checked resolution. The
   alternative is to require every translated unit with a reference to carry a fence. The discourse reviewers
   decide; S4's measured unlock is small either way.
8. **A reference as a reading axis inside a rule** (two antecedents for "it" in a guard): candidates would differ
   only in a resolved position. The model allows it (candidates are resolved contents), but discourse records one
   target per slot. Left to the S4 specification.
9. **The bar** is enumerated because `correlate` cannot be gated. If a third enumerated axis appears, the right fix
   is a `rights@1` whose generated nodes take a guard, with the faithfulness theorems restated.
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
16. **The choice vocabulary needs one element.** `ve__here` must denote something, so `base_up` and `superpose_all`
    assume a non-empty carrier. `superpose_conflict_free` is stated without the hypothesis on the expectation that
    a structure with no element has no conflict point; the statement review must confirm that against W1's
    `ConflictFree` or add the hypothesis. The logic has no nullary predicate; adding one would remove the sort and
    the constant, and is a frozen-contract change this plan does not ask for.

## 8. Not claimed, and out of scope

No coverage number. No theorem that a reading set is exhaustive, that a coupling or narrowing is the right
interpretation, that a relation's table is correct, or that a translator's resolution is the author's. No
completeness of the conflict check outside norms 7. No composition with speech acts, reports, alternatives, risk,
quantities, definitions or data (2.9 only fixes where each would attach). No change to act phrases, to any
`rights@0`, `soft-norms@0`, `norms@0` or `ve-document@1` identity, or to a frozen Lean file. No English parsing
work beyond registering the wordings named in section 3 (W7) and the IDE questions (W8), each behind its own gate.

## 9. Process

This plan goes to the Astra + Fable design debate (`manage-agents/debates/design-compose/`), with questions 1, 4
and 7 as the named points of attack. On convergence: S0's statements are reviewed and built first (small, no
behaviour change); S1, S3 and S4 get item-1 specifications in parallel (`readings.md`, `right-clauses.md`, an
amendment section of `discourse.md`), each with its statement review before Lean; S2's specification follows S1's
merge. Every stage ends with both pilots rerun and audited, and section 6's table replaced by measured results.

## Change log

| Date | Revision | Changes |
|---|---|---|
| 2026-10-01 | Draft 1 | First plan: the stack and its six rules; content-bearing candidates; superposition with choice premises; separating situations over a shared base with private decision assignments; per-reading rights; structured lines with clauses, relation and `elided`; discourse on the chain; five stages with Lean statements, twenty pilot fixtures, the measured unlock table and fifteen open questions. Design only. |
