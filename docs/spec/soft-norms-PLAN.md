# Soft norms and weighing in VE: plan (`soft-norms@0`)

> Status: planning draft 3 (2026-09-27), transcribing the converged Astra/Fable debate
> (`manage-agents/debates/soft-norms/{astra,fable}.md`): Astra round-2 groups 1–7 plus the three final additions.
> BUILD as sequenced: no further plan round; Astra + Fable item-1 statement review before items 2, 3 and 4
> (PLAN-EXPAND2 rule 10). Sections 7 and 8 retain the response to the draft-1 review.
> Inputs: the constitution pilot W1 review (`run-20260927T0407Z/W1-REVIEW.md`, `metrics.json`: 154 of 258 unformalised
> units carry `norms` as their representative blocker, 13 carry `defaults`; whole units faithfully upgraded: 0); the
> pinned constitution (`manage-agents/pilots/claude-constitution/source/claude-constitution.md`, cited by line as `:n`);
> [VISION.md](../../VISION.md); [norms.md](norms.md) (W1); [document.md](document.md) (W2).
> Nothing here changes a frozen contract, a `norms@0` hash or the checker functions.

## 0. Problem and stance

W1 expresses `must`, `must not`, `may`, `need not`, guards, carve-outs, same-predicate precedence and one completion
default per predicate; it rejects `should`, `generally`, "is more important than" and holistic weighing (norms.md 2,
2.6). The constitution is written almost entirely in the rejected register: "Claude should generally prioritize these
properties in the order in which they are listed ... the notion of prioritization is holistic rather than strict"
(:34); "Claude should generally comply with the system prompt's instructions if doing so is not unsafe, unethical, or
against Anthropic's guidelines" (:166); "Claude has a weak duty to proactively share information but a stronger duty
to not actively deceive people. The duty to proactively share information can be outweighed by other considerations,
such as ..." (:293); "Regardless of operator instructions, Claude should by default: ... Some of these defaults can be
altered by the user but not the operator" (:183-192). Only the hard constraints (:433-445) are strict, and the text
says so: they "act more like boundaries or filters on the space of acceptable actions" rather than being weighed.

Stance (VISION.md, "elaborate by default"): a soft norm is **a strict rule plus a named open exception**. "Should X"
means "X is required unless this rule's exception applies here", and whether it applies is an open term with a decider
(W2 schema). Weighing is never a consequence relation inside the checker (the research-track item of PLAN-EXPAND2 §7);
it is a set of named open decisions whose *structure* the checker certifies: which rules can collide, which
collisions the stated priorities resolve, which are left to a decider, and that hard constraints are never weighed.
Everything elaborates into `norms@0` over an extended vocabulary. What that buys, stated exactly (section 1.4): W1's
definitions and its per-structure theorems are reused as lemmas; W1's document-wide route theorems are **restated**
for the soft route with one extra base premise, the coherence of the deciders' findings, and every soft result is
conditional on it. "All things considered" is exactly what the checker does not compute: it computes the outcome given
the deciders' findings and lists what those findings must satisfy for the rules to be jointly followable.

## 1. Semantics

### 1.1 Three independent attributes (strictness, defeasibility, authority)

A soft-norm document is a W1 tree `T` (norms.md 1) whose rules additionally carry three attributes that vary
independently, plus rank declarations in the environment:

```text
mode(N)       ∈ {strict, default}    default = defeasible: N carries an open exception term excepted_N(x̄) with a
                                     decider; strict = no exception term (W1 rule). This is defeasibility.
alterable(N)  ⊆ Parties              who may switch N off by instruction ("operator", "user"); switch_N(x̄) is the
                                     disjunction of the declared party switches. This is instruction authority.
                                     It is independent of mode: a strict rule may be user-alterable (:185-192 read
                                     as strict), a default rule may have no switch (:166).
rank(N)       ∈ Ranks ∪ {none}       a declared name ("safety", "ethics", "guidelines", "helpfulness"); affects only
                                     default rules (theorem hard_never_weighed, 1.3)
hard(N)       := mode = strict ∧ alterable = ∅   (derived, not declared): no exception, no switch; only a strict
                                     exception rule written in the document can override it (W1 precedence)
Ranks         finite names; `outranks` edges, closed transitively into a strict partial order (DependencyCycle on a
              cycle); incomparable ranks are ties (:347 "in no particular order"); a declared tie between comparable
              ranks is TieAgainstOrder; one document flag: outranking is `strict` or `holistic` (:34)
exception     excepted_N(x̄): mandatory for default rules; decider named at rule or document level in authoring
              (MissingExceptionDecider); in translation the decider may be `unstated` (counted, section 4)
```

Decision predicates are fresh base predicates of `E′ = E + decisions`: `excepted_N` and `off_N_π` have their rule's
argument sorts; `outweighs_{a,L,H}` is indexed by declared act `a` and ordered rank pair L below H used by a colliding
pair on that act, with the act's argument sorts (shared by its dual predicates, norms.md 3.1). Act identity, ordered
ranks and signature are identity-bound in `E′` and the soft document hash. Below, `outweighs_{a,N,M}` abbreviates
`outweighs_{a,rank(N),rank(M)}` for rules N, M; it is not a separate rule-pair predicate. These predicates are
nobody's instruction: an environment may attribute ordinary base predicates to a party (`"instruction_of":
"operator"`, rendered in the legend as `"<verbalisation> records an instruction of the operator."`); decision
predicates carry no attribution, because what a decider considers is outside the checker.

Colliding rules. Each rule has an *effect* on its act: `require` (+ on the obligation predicate `r`), `release`
(− on `r`), `permit` (+ on the permission predicate `m`), `forbid` (− on `m`). Two default rules **collide** when their
effects are incompatible: require/release, permit/forbid, or require/forbid across the declared dual pair `(r, m)` of
one act (norms.md 3.1). The collision relation is bipartite ({require, permit} against {release, forbid}). `CP(T)` is
the set of colliding default pairs. This replaces draft 1's same-predicate-only notion (review A2).

### 1.2 The direct semantics `ValueSoft`: a terminating decision procedure on `T`

`ValueSoft_p(S, v̄)` is defined on the soft tree `T` itself, for a structure `S` over the symbols strictly below `p`
in the dependency order of section 1.3 and a typed tuple `v̄`, evaluated under W1's `tupleVal`. It never refers to the
elaboration. Every step is a finite Boolean evaluation; step 3 recurses strictly upward in the finite rank order,
and W1's `yields`/`selects` recurses on the author precedence DAG, well-founded by norms.md 4.1(3).

```text
Step 0  In force.   live_N(x̄) := G_N(x̄) ∧ ¬⋁U_N(x̄) ∧ ¬switch_N(x̄) ∧ [mode default] ¬excepted_N(x̄)
        A rule is live by its own terms only: guard, author carve-outs, switches, its exception. No other rule occurs.

Step 1  Strict rules decide.  T_s := the strict rules of T with the author precedence among them (a strict rule may be
        an exception of a default rule; the reverse is rejected, SoftOverHard, so every descendant of a strict rule is
        strict and its `selects` is the same in T_s and in T′). With applies_N := live_N, W1 selects over T_s gives
        P^s_p := ⋁_{strict, +} selects_N, N^s_p := ⋁_{strict, −} selects_N.

Step 2  Hard over soft.  A default rule N on p is blocked at x̄ when a strict rule decides the same act either way:
        blocked_N(x̄) := P^s_p(x̄) ∨ N^s_p(x̄)
                        ∨ [N requires, dual m declared] N^s_m(x̄)      a strict rule forbids the act
                        ∨ [N forbids, dual r declared]  P^s_r(x̄)      a strict rule requires the act
        A strict rule that is itself overridden by a strict exception does not select and blocks nothing.

Step 3  Dominance by rank.  eligible_N(x̄) := live_N(x̄) ∧ ¬blocked_N(x̄)
        eff_N(x̄) := eligible_N(x̄) ∧ ¬dominated_N(x̄)
        For (M, N) ∈ CP(T) on act a with comparable ranks, M dominates N at x̄ iff
          rank(M) outranks rank(N):  flag strict:   eff_M(x̄)
                                      flag holistic: eff_M(x̄) ∧ ¬outweighs_{a,N,M}(x̄)
          rank(N) outranks rank(M):  flag strict:   never
                                      flag holistic: eligible_M(x̄) ∧ outweighs_{a,M,N}(x̄)
        dominated_N(x̄) := ⋁_M dom(M, N)(x̄). Higher opponents must be effective; lower overriding opponents need
        only be eligible. Effective-rule dependencies go strictly upward, so the recursion is well-founded.

Step 4  Default rules decide.  applies′_N := eff_N for default N; W1 yields′/selects′ over the author precedence
        DAG among all rules on p, explicitly including strict children of default parents in yields′;
        P^d_p, N^d_p as in W1 over default rules.
        P′_p := P^s_p ∨ P^d_p,  N′_p := N^s_p ∨ N^d_p
        ValueSoft_p(S, v̄) := some true  if P′ and not N′       | some false  if N′ and not P′
                            | some d_p   if neither             | none        if both
```

Where a strict rule decides (`P^s ∨ N^s`), step 2 makes every default rule on `p` inapplicable, so `none` at a point
with a strict rule is a strict–strict collision and `none` without one is a **weighing point**: two live, unblocked,
undominated default rules of opposite effect, neither excepted. `some d_p` applies when no rule selects on `p`.
At a fixed act and tuple, if any default is eligible, some default is effective, before author precedence. Proof:
suppose none were effective. Choose an eligible rule with no lower-ranked eligible rule, which exists because the
rank order is finite and acyclic. No higher effective rule can dominate it, and no lower eligible rule can override
it. It is therefore effective, a contradiction. All eligible defaults being dominated is unreachable; this does
not identify a predetermined winner or guarantee a selection on each predicate of the act.

Why draft 1 was circular and this is not (review A1). Draft 1 made the higher rule an exception node of the lower
one and then gave the higher rule a carve-out mentioning the lower rule's `selects`, so each rule's applicability
depended on the other's selection: with both live and `outweighs` true the equations were `H = ¬L`, `L = ¬H`, two
solutions. Here blocking depends only on strict selection, and dominance depends on higher effectiveness and lower
eligibility, never on default selection after author precedence. With just H and L eligible on act a and
`outweighs_{a,L,H}` true: H is dominated (`eligible_L ∧ outweighs_{a,L,H}`), L is not
(`eff_H ∧ ¬outweighs_{a,L,H}` is false); L alone applies. One winner, by evaluation, not by fixpoint.

### 1.3 Elaboration `soften(T) = T′` over `E′`

`T′` keeps every rule's predicate, sign, guard and author `over` edges and adds exactly one derived carve-out per rule
(packed into one formula so W1's carve-out limit of eight per rule leaves seven to the author; guard size is bounded
by `MAX_NODES` and overflow is `ResourceLimit`, never a verdict):

```text
derived_N := switch_N(x̄)                                                      strict N
derived_N := excepted_N(x̄) ∨ switch_N(x̄) ∨ blocked_N(x̄) ∨ dominated_N(x̄)       default N
carve-outs of N in T′ := U_N ++ [derived_N];  precedence of T′ := author precedence of T;  no derived edges
```

The well-founded step-3 recursion is expanded into these derived carve-outs, inlining higher `eff_M` formulas;
author precedence is applied afterward. Unfolded size is subject to `MAX_NODES`; overflow is `ResourceLimit`.
`T′` is a `norms@0` tree over `E′`. Its stratification (norms.md 4.1(4)) is computed on `T′`: `blocked_N` and
`dominated_N` mention the guard, carve-out and decision symbols of other rules, so a rule on `r` whose derived
carve-out mentions the strict rules on `m` needs those rules' guards to lie strictly below `r`, and symmetrically for
`m`. Guards over base predicates always satisfy this; a guard that mentions the dual predicate itself can create a
cycle, reported as `DependencyCycle` with the rewrite hint `DualGuardCycle` ("rule n's guard mentions whether S may X
and a rule on may-X must give way to rule n; restate the guard over the facts").

Theorems about `soften` (Lean `VE/SoftNorms/*`, item 4):

- `soften_wellFormed`: `WellFormedSoft E T → Norms.WellFormed E′ T′` (SoftOverHard, rank acyclicity, ties,
  deciders in authoring mode, dual ordering, W1 checks).
- `soften_faithful`: `Norms.Value T′ p S v̄ = ValueSoft T p S v̄` for every `p`, every structure `S` admissible for the
  layer below `p` and every typed `v̄`. Proof: `applies_{T′}(N) = live_N ∧ ¬derived_N = applies′_N` by unfolding; the
  precedence DAG is the same, so `yields`/`selects` coincide; the four-way case split is W1's.
- `hard_over_soft`: at any point where a strict rule selects on `p`, or a strict rule on the dual decides the act
  against a default rule's effect, that default rule does not select; hence `P^d ∧ N^s` and `N^d ∧ P^s` are
  unsatisfiable on the same predicate, and no `required ∧ ¬permitted` point has a default rule on one side and a
  strict rule on the other. This is about `soften`, not a search.
- `hard_never_weighed`: locally, with the interpretations of strict guards and author carve-outs, the layer below
  and all strict switches fixed, `P^s_p`, `N^s_p` and every strict rule's `selects` are independent of ranks, the flag
  and `outweighs` and default-exception decisions. Global independence from decision predicates requires a
  decision-free dependency cone,
  including strict exceptions (using the cone check of section 3, item 6). A hard rule's own lack of a switch does
  not imply this: a switchable strict exception can change its selection, and a strict guard can read a lower soft
  outcome.
- `rank_resolves`: for `(M, N) ∈ CP(T)` with comparable ranks, `selects′_M ∧ selects′_N` is unsatisfiable (strict
  flag: both effective would make the lower dominated by the higher; holistic: both effective would require the
  same act-indexed `outweighs` atom to be true to protect the lower and false to protect the higher).
- `rank_acyclic`: the closed `outranks` order is a strict partial order (via `VE.Route.dependencyOrder`).

### 1.4 Decision assignments, coherence and what "conflict-free" means (review A3)

```text
decision assignment  the tables of the decision predicates in a base structure B over E′
classification       for (M, N) ∈ CP(T):
                       RANK-RESOLVED   comparable ranks (theorem rank_resolves; no search)
                       DISJOINT        certificate  Background_base(E′) ⊢ ∀x̄. ¬(selects′_M°(x̄) ∧ selects′_N°(x̄))
                       WEIGHING POINT  checked witness (B, ā) with both selecting; shown as a situation
                       UNKNOWN         neither within budget; budget named
WP(T)                := the WEIGHING POINT and UNKNOWN pairs (undischarged conjuncts)
Coh_T                := ⋀_{(M,N) ∈ CP(T)} ∀x̄. ¬(selects′_M°(x̄) ∧ selects′_N°(x̄))
                        one universal base formula per pair, labelled soft:coherence:<M>,<N>, regenerated from the
                        decoded document at every site and bound to the soft document hash, never taken from the wire
coherent B           := B ⊨ Coh_T: all colliding default pairs have disjoint selections
Background_base′     := Background_base(E′) ++ Coh_T        (universal, so norms.md 7.1(3) is preserved when the
BaseAdmissible′ E T B := BaseAdmissible E′ B ∧ Sat B Coh_T    substituted selections are quantifier-free)
```

`Coh_T` is defined over all syntactic `CP(T)`, independently of classification budgets. RANK-RESOLVED conjuncts
are theorems and DISJOINT conjuncts follow from their certificates; classification marks these as discharged,
without changing the route's coherence condition or requiring classifications to be replayed to regenerate it.

Draft 1 claimed W1's guarantees would be inherited by replaying the strict core and the DISJOINT certificates. That
was wrong: at a weighing point with both exceptions false `T′` elaborates to contradictory requirements, `elab_p` is
false there, and W1's unique-expansion premise fails for that base structure; no report restores it. What holds, and
what the soft route certifies, is the following.

- `coherent_expands` (W1's pointwise `conflictFree_expands_document` applied to `T′`; reused, not restated): for
  every base `B` over `E′` with `BaseAdmissible E′ B`,
  `Unique(DocumentExpansion E′ T′ B) ↔ ConflictFree E′ T′ B`. A coherent assignment that
  also avoids the conflicts below has exactly one expansion; an incoherent one has none.
- `soft_conflict_decomposition`: `ConflictFree E′ T′ B ↔ NoStrictCollision(B) ∧ NoHardPairConflict(B) ∧ Sat B Coh_T`,
  where `NoStrictCollision` is `∀p x̄. ¬(P^s_p° ∧ N^s_p°)` and `NoHardPairConflict` says no declared pair `(r, m)` has
  `O_r° ∧ ¬O_m°` at a point unless both sides come from default rules (which is the case `Coh_T` covers). The `←`
  direction contains `hard_over_soft` and `weighing_points_complete`: every collision in a coherent `B` is
  strict–strict on one predicate or a pair conflict with a strict rule or a completion on at least one side; every
  default–default collision is at a pair in `CP(T)` (and cannot be a discharged pair in an admissible base).
- **What CONFLICT-FREE certifies**: `soft_conflict_free := ∀B. BaseAdmissible′ E T B → ConflictFree E′ T′ B`,
  checked by W1's unchanged conflict machinery (tableau, witness search, evaluator) on `T′` over `Background_base′`.
  In words: under any decision assignment that resolves the listed weighing points, every situation has exactly one
  outcome for every regulated act. The weighing-point witnesses are exactly the countermodels to the *unconditional*
  claim, and the report shows them as such.
- **Conditional guarantees.** The soft route's acceptance and countermodel theorems are W1's
  `norms_route_acceptance` and `norms_route_countermodel` restated with `BaseAdmissible′` (the frozen P0 `Layer` takes
  the first layer's `Admissible_in` as a parameter, so `Coh_T` enters through it; `BackgroundSound`/`Complete` for
  the soft route include `Coh_T`). A certified conclusion holds in every situation whose decision assignment is
  coherent and satisfies the report's other assumptions; a countermodel is a coherent base situation, rendered with
  its decision assignment in document terms ("rule 12 is excepted here; rule 4 is not; on complying with this
  operator instruction, helpfulness outweighs ethics", the act-indexed atom for rules 4 and 21).
  Every soft report states the route's full `Coh_T` condition separately from `conditional_on: soft:coherence:<pairs>`,
  which lists only the undischarged coherence premises actually used by the certificate. The used-leaf list records
  those dependencies (as bridge leaves are shown today).
- **Vacuity.** (i) The P0 vacuity report (3.8) runs over `Background_base′ ++ layer premises ++ Γ`, so a `Γ` that
  fixes decision facts incompatible with `Coh_T` makes dependent certificates `vacuous`, visibly. (ii) A CONFLICT-FREE
  report must also exhibit one coherent decision assignment as a checked finite model together with `Γ`, or say
  UNKNOWN; without it the conditional claim could be about no situation at all. (iii) A default rule alone proves
  nothing about its act unless the premises constrain `excepted_N`; that is the intended content of "should", and the
  report says so rather than hiding it (risk 6.7).
- **Completion outcomes.** Pair conflicts in which one side is a completion default are CONFLICT, as in W1 10.1(a,b):
  a default obligation that selects where the act's permission is deny-by-default and nothing permits it, or a
  default prohibition that selects where the act is required by default. `soften` does not carve defaults out on
  completions; doing so would make every default obligation vacuous under a deny default (section 7, item 1). The
  witness names the completion ("rule 12 requires sharing here; by default an assistant may not share; no rule
  permits it").
- **Override cycles.** Under the holistic flag, take four eligible defaults on act a, ranks A>B>C>D, A/C requiring
  and B/D releasing, with findings `outweighs_{a,B,A} ∧ outweighs_{a,C,B} ∧ outweighs_{a,D,C} ∧ ¬outweighs_{a,D,A}`
  (B>A, C>B, D>C, A>D). This is an alternating collision cycle, not four pairwise-colliding rules. D alone is
  effective. The report's `override_cycles` line gives a diagnostic warning with a witness, not an additional
  assumed obligation; `Coh_T` contains no ban on such cycles.

Draft 1's status table said CONFLICT for the naive W1 verdict on `T′` was "the intended reading"; it is not, and it
is not what the soft route reports. The soft route's contract is the conditional statement above with its residual.

### 1.5 The report

| Question | Method | Result |
|---|---|---|
| Which default rules can collide, and is each collision resolved? | for each `(M, N) ∈ CP(T)`: `rank_resolves`, else certificate, else witness | RANK-RESOLVED / DISJOINT / WEIGHING POINT (situation, condition `¬(selects′_M ∧ selects′_N)` there) / UNKNOWN; identifies discharged conjuncts of the budget-independent `Coh_T` and the remaining `WP(T)` |
| Can the rules contradict each other under a coherent decision assignment? | W1 conflict check on `T′` over `Background_base′`, unchanged functions | CONFLICT (witness classified: strict collision / pair conflict with a strict rule or completion) / CONFLICT-FREE conditional on `Coh_T` (certificate + one coherent model) / UNKNOWN |
| Are the priorities consistent? | closure of `outranks`, `dependencyOrder`; declared ties; author edges against rank | acyclic / `DependencyCycle: <ranks>`; `TieAgainstOrder`; undeclared ties listed; `RankAgainstPrecedence` (warning: legal, pointless) |
| Who can change each rule? | switches; attribution cone check (section 3, item 6) | per rule: parties with a switch; whether any predicate attributed to another party occurs in the rule's cone |

Weighing points and coherence premises are residual items (VISION.md 2), each with its resolution:
`open` (the two rules must not both select: exceptions, switches, guard or author carve-out conditions, strict
blocking, dominance by other rules or author precedence can prevent selection), `rank: ethics over helpfulness
(holistic)` (pairwise defeat resolved by structure, the act-indexed `outweighs` term in the residual), `strict`
(no residual). Reports show the actual selection-disjointness condition, not a requirement that one exception
must hold. The full route condition `Coh_T` is separate from the undischarged premises actually used, listed in
`conditional_on`; `override_cycles` entries are diagnostic warnings, not assumed obligations. The checker does
not invent decision criteria (document.md).

### 1.6 Limit

Collisions are same-act: one predicate, or the declared obligation/permission pair of one act. "Help with the
request" versus "refuse the request" are different acts; their practical incompatibility is stage-3 material
(actions, fulfilment). This limit bites on the constitution: its hard constraints regulate their own acts (generate
CSAM, provide serious uplift), while most soft rules regulate complying, sharing, deceiving; `hard_over_soft`
resolves something there only where a soft rule regulates the same declared act. The four-property ordering has two
encodings: ranks on rules over shared acts (this profile), or norms.md 9.2's reified `follow(situation, property)`
over `outranks(property, property)`; both stay in the :34-37 reading set (section 4).

## 2. English wordings (one reading each; rejected as today when `soft-norms@0` is off)

| Wording | The one reading (the IDE's paraphrase) | Formal effect |
|---|---|---|
| `Rule n. Every <noun> should <act>[, if C][, unless U].` | In every situation of the kind, the act is required unless rule n's exception applies there; <decider> decides whether it applies. | default, obligation `+`; `excepted_n` |
| `... should not <act>` | ... the act is not permitted unless rule n's exception applies there. | default, permission `−` |
| `... generally may <act>` / `... generally need not <act>` | ... permitted / not required unless rule n's exception applies there. | default `+` permission / `−` obligation |
| `The exception to rule n is decided by <decider>.` | Names who decides whether rule n is excepted in a situation. | open-term decider |
| `Exceptions to rules in this document are decided by <decider>, unless a rule says otherwise.` | Document-level decider. | default decider |
| `Rule n is excepted when C.` / `... only when C.` | C is sufficient / necessary for rule n's exception. | `sufficient` / `necessary` (premises in the `soft` background slot, listed under the term) |
| `The exception to rule n takes account of <consideration>[, <consideration>]*.` | These considerations bear on whether rule n is excepted; none is by itself decisive. | `factors` (no premise) |
| `Rule n serves <rank>.` | Rule n counts as a <rank> consideration where it collides with a rule of another rank. | `rank(n)` |
| `<Rank a> outranks <rank b>.` | Where the rules collide on one act, the lower rule gives way to an effective higher rule, subject to the holistic override if declared; this is pairwise defeat, not guaranteed final selection. | rank-order edge |
| `<Rank a> and <rank b> are not ranked.` | Neither outranks the other; a disagreement between them is a weighing point. | declared tie (checked) |
| `Outranking in this document is holistic; <decider> decides when a lower-ranked rule outweighs a higher-ranked one in a situation.` / `... is strict.` | Holistic: a lower rule gives way to an effective higher opponent unless the decider finds that it outweighs that opponent; a higher rule gives way to an eligible lower opponent found to outweigh it. Strict: a lower rule gives way to an effective higher opponent. Neither guarantees final selection. | flag; `outweighs_{act,L,H}` terms |
| `Rule n (operators may turn off).` / `(users may turn off)` | The rule holds unless the named party has turned it off for the situation; no other party has a switch. | `off_n_π`; authority report |
| `"<verbalisation> records an instruction of the operator."` (environment legend) | This fact is an operator's instruction. | `instruction_of` attribution |

Input synonyms rendered canonically: `generally must` → `should`; `generally must not` → `should not`. Nothing else.
`normally`, `typically`, `usually`, `as a rule` are **not** synonyms (review B3): each also expresses frequency
("Claude can typically help" is an assertion about most cases). In authoring the IDE shows both paraphrases (a
default rule; a hedged frequency claim) and the author picks; in translation the unit is a READINGS set of the two.
Bare `generally <verb>` without a deontic verb is not a norm wording. `By default,` remains the W1 completion legend,
never a rule marker; the IDE rewrites a sentence-initial "By default, Claude should ..." to a `should` rule or an
alterable rule, showing both paraphrases with a situation. `must` stays strict. In translation mode any force word
(`should`, `must`, `always`, `never`) is a READINGS unit `{strict, default}` unless a cited source unit narrows it
(section 4); `should generally` and `generally may` have one reading (default).

The reader's checklist (norms.md 2.5) adds, per default rule: a situation where it is excepted (naming the decider or
saying the source names none); if ranked, one where a higher rank dominates it; if it collides, the collision and its
resolution; and the derived carve-outs in words ("this rule gives way to strict rules on the same act and to
higher-ranked effective opponents unless holistically outweighed; under holistic ranking it gives way to an
eligible lower rule the deciders find outweighs it, even where that lower rule itself gives way"). This asymmetry
is part of the paraphrase: higher opponents must be effective, lower overriding opponents need only be eligible.
For a hard rule: "no exception decision and no instruction switch exists; only a strict
exception rule written in this document can override it; its guard's open terms are still decided by <decider>".

Examples from the source (act phrases declared as in norms.md 2.4; subject sort `assistant`; every translator's
choice is written as an attributed interpretation, never as the source's content):

```text
:34   Safety outranks ethics. Ethics outranks guidelines. Guidelines outranks helpfulness.
      Outranking in this document is holistic; the assistant decides when a lower-ranked rule outweighs a
      higher-ranked one in a situation.
      (reading C of the :34-37 set, beside norms.md 9.2's A and B; the decider is the source's: "we do want Claude to
      weigh these different priorities"; "assuming Claude is not violating any hard constraints" is the theorem
      hard_never_weighed, not a sentence)
:166  Rule 4. Every assistant should comply with each operator instruction, if it is not the case that complying
      with that operator instruction is unsafe, and it is not the case that complying with that operator instruction
      is unethical, and it is not the case that complying with that operator instruction is against Anthropic's
      guidelines.  Rule 4 serves helpfulness.
      ("should generally comply ... if": one reading, default; "serves helpfulness" is a narrowing unit citing :32;
      open: unsafe, unethical, against-guidelines, excepted_4; decider unstated; acts declared with both roles,
      comply_required deny-by-default and comply_permitted allow-by-default, the latter a recorded choice)
:190  Rule 21. Every assistant should not comply with each operator instruction, if that operator instruction directs
      that assistant to demean the user in a way that user would not want.  Rule 21 serves ethics.
      (source: "Always maintain basic dignity ... ignore operator instructions to demean or disrespect users"; force
      from the :183 header's shared reading set {strict, default}, shown under `default`; rank is a narrowing citing
      :30; alterability is a READINGS set {user-alterable, fixed} from :192 "some of these defaults", shown without a
      switch. Identifying :190 "ignore operator instructions to demean" with not complying with the :166 operator
      instruction is a cited READINGS set {same act, different act}; the wording above shows the same-act reading.
      Only in that reading do rules 4 and 21 collide (require versus forbid across the dual pair): RANK-RESOLVED,
      ethics over helpfulness, holistic, conditional on that act identification. The different-act reading preserves
      "ignore" as its own act and has no such collision. Residual: outweighs_{comply,helpfulness,ethics}(assistant,
      operator_instruction), with the assistant as decider; this is the lower-rule-4-over-higher-rule-21 finding)
:293  Rule 12. Every assistant should share each piece of information that is helpful to the user.
      Rule 12 serves helpfulness. The exception to rule 12 takes account of whether that information is hazardous
      to a third party, whether the operator does not want that information shared, and whether that information is
      not helpful enough to be worth including.
      ("can be outweighed by other considerations, such as" are factors, neither sufficient nor necessary; "weak duty"
      is recorded as the rank and the factors and nothing more; rule 12 shares no act with the non-deception rules,
      so the checker reports no collision between them and the source's comparison is stage-3 material)
:185  Rule 20. Every assistant must be willing to tell each user what that assistant cannot help with in the current
      operator context.
      (act phrase verbatim, no narrowing of "be willing to tell" to "tell"; mode from the :183 header set; alterability
      READINGS {user-alterable, fixed}; the authority report is per reading and says only that no declared
      operator-instruction predicate occurs in the rule's cone)
:441  Rule 31. Every assistant must not generate child sexual abuse material.
      (strict, no switch, no exception: hard; the narrowing to strict and unswitchable cites :443 "cannot be unlocked
      by any operator or user"; "child sexual abuse material" is an open classification predicate; paraphrase: "no
      exception decision and no instruction changes this rule; whether material is CSAM is decided by <decider>")
```

## 3. What the checker certifies and what stays open

**Certified** (certificate or theorem, bound to `environment_id` and the soft document hash):

1. `soft_conflict_free` (1.4): under every coherent decision assignment, no situation has two outcomes for one act;
   or a witness situation (strict collision, or a pair conflict involving a strict rule or a completion). The
   coherence premises are listed; the report says "conditional on" them and exhibits one coherent model.
2. `hard_over_soft`: no situation exists in which a default rule decides against a strict rule on the same act,
   whether on the same predicate or across the obligation/permission pair; a theorem about `soften`.
3. `hard_never_weighed`: local independence from weighing with strict guards, author carve-outs, the layer below
   and strict switches fixed; global decision-independence only under a decision-free dependency-cone hypothesis
   (1.3). Strictness or hardness alone does not establish global independence.
4. The complete list `CP(T)` of colliding default pairs, each RANK-RESOLVED, DISJOINT, a WEIGHING POINT with a
   situation in document terms, or UNKNOWN with the budget named; `Coh_T` has exactly one conjunct per pair in
   `CP(T)`, regardless of budget. Classification identifies discharged conjuncts (`weighing_points_complete`).
5. The rank order is acyclic; declared ties are ties; author precedence against the ranks is flagged.
6. **Authority, scoped** (review B1): for each rule, exactly the declared parties have a switch (there is no other
   `off` predicate to set). Separately, an attribution check: if no predicate attributed to party π occurs in the
   base cone of `p` in `T′` (guards, carve-outs, exception premises, definitions below `p`) and π has no switch on any
   rule on `p`, then `O_p°` is invariant under changes to π-attributed predicates (`authority_independent`, a
   non-mention lemma). The certificate is about *declared* attribution only. It says nothing about whether a decider
   of `excepted_N` or `outweighs` takes π's instructions into account, and nothing about base facts the environment
   did not attribute; the report states both limits next to the result.
7. `soften_wellFormed`, `soften_faithful`; W1's well-formedness, DAG and identity checks on `T′`.

**Open, never certified:** the exception decisions (`excepted_N`); the holistic overrides (`outweighs_{act,L,H}`); the
coherence of the deciders' findings (assumed, listed); weighing procedures with their factors (:332-343 becomes the
schema of `harm_outweighs_benefit(action, context)` with factors probability, counterfactual impact, severity,
breadth, proximate cause, consent, responsibility, vulnerability; decider per the source: the assistant, :325 "use
good judgment"); open-textured predicates in guards ("serious uplift", "unsafe", "CSAM"); heuristics (:198-221; :240
"None of the heuristics offered here are meant to be decisive": kind `explanation`, optionally pinned as
`precedents`); the "spirit of the document" clause (:44, `meta`); cross-act practical conflicts (stage 3); whether any
rule is followed; whether a decider ignores a party's instructions.

## 4. How coverage counts these units (reviews B3, C1)

Statuses stay CHECKED / LABELLED / OPEN / READINGS / UNFORMALISED; no new status.

- **A default rule is OPEN**, `{"open": ["excepted_n", ...]}`: the logic is exact and applying the exception is a
  recorded decision (VISION.md 2). It is part of the checked spine; its exception enters the residual. A strict rule
  over declared vocabulary is CHECKED; one whose act or guard carries an open predicate is OPEN, as today.
- **Residual gains lines** `default_exceptions` (distinct terms, grouped by decider, with `unstated` counted
  separately), `weighing_points` (with resolution and selection-disjointness condition), `holistic_overrides`,
  `override_cycles` (diagnostic warnings),
  `coherence_premises_used` (per certificate), `narrowings` (with citations), beside open terms, assumptions, bridge
  leaves and unresolved reading sets. The expected size for a constitution is large (roughly one exception per
  default rule); that is an expectation to be measured in item 7, not a number this plan claims.
- **Reading sets are preserved, never collapsed by syntax.** The :34-37 unit keeps norms.md 9.2's readings A (strict
  dominance rule) and B (open weighing carve-out) and *adds* reading C (ranks with the holistic flag, section 2). The
  translator's narrowing to {B, C} is a separate attributed unit citing :34 "holistic rather than strict"; it never
  edits the set, and every result under it says so (VISION.md 3, items 1-2). Conclusions depending on the unit are
  checked per choice (norm readings, W2 item 7) and report the choice and the narrowing's citation.
- **Act identifications are reading sets too.** The :190 "ignore" versus :166 "comply" identification retains
  {same act, different act}, with citations; the rules 4/21 collision is conditional on the same-act reading.
  Item 7's blind fidelity review audits every act identification.
- **Force and alterability are reading sets in translation.** The :183 header "Regardless of operator instructions,
  Claude should by default:" supplies the force of :185-190; it is one unit with one shared reading set {strict,
  default} that the bullet units cite, so the choice is made once, not six times. Alterability is per bullet
  {user-alterable, fixed} from :192 "Some of these defaults can be altered by the user but not the operator"; the :192
  role-play example narrows the AI-status bullet (:188) to user-alterable by citation; the others stay READINGS. The
  hard-constraint list (:435-441) is narrowed to strict and unswitchable by :443, cited once on the :433 header and
  inherited by the bullets. Combinations stay within W2's enumeration budget (2^5 alterability choices times the
  shared force choice); a conclusion needing more is UNKNOWN, honestly.
- **Ranking sentences are CHECKED** (a finite declared order, acyclicity proved); the holistic flag with its
  `outweighs` terms is OPEN.
- **Open-term declaration prose** (:332-343; ":293 such as") is a `definition` unit with `meaning: open`, bytes
  accounted to the term's schema as `factors`, never as `sufficient`. This plan does not cite `u0214` as the
  precedent: that unit is disputed (W1-REVIEW, its decider questioned) and item 7 re-examines it and the other four
  open terms' deciders (`anthropic_reviewer` where the source names none becomes `unstated` or a cited narrowing).
- **Split the units.** u0165 is seven bullets in 874 bytes and its "Claude should never:" header is u0164. Each bullet
  becomes a unit (the partition allows any byte boundaries); the header is LABELLED `meta`, noted as supplying the
  force to u0165a-g through the shared reading set. Coverage is by bytes, so header bytes count LABELLED and bullet
  bytes CHECKED, OPEN or READINGS, and nothing is discarded.
- **Whole-unit fidelity is the rule.** A unit changes status only when its entire span is rendered faithfully as a
  nest of kinds (a norm with open guards, an attributed explanation, a factor list). Capability evidence outside a
  faithful whole-unit translation stays outside counted coverage, as in the W1 review.
- **No gain is counted without three things** (review C1): (a) an end-to-end admission: the unit's norm content goes
  through `ve document check` and the soft route as a document unit, not through an isolated parser call (item 0);
  (b) a split-only baseline: the same re-split ledger run under `norms@0` alone, so the soft-norms delta is measured
  against it and not against `run-20260927T0407Z`; (c) a blind whole-span fidelity review of every upgraded unit
  (source span against the paraphrases of all its readings and kinds, auditing every act identification), with
  failures reverted before counting. The 154 `norms` labels are representative blockers and many of those units
  carry other blockers (causation 17,
  quantities 31, counting 8); the upgradeable count is unknown until measured and this plan predicts none.

## 5. Work items

| # | Item | Owner, effort | Notes |
|---|---|---|---|
| 0 | Document-level norm admission: `ve-document@1` units of kind `norm` carried through `ve document check` to the norms route and to the soft route; today the loader accepts formula content only (W1-REVIEW) | W1/W2 integration ([INTEGRATION-GAPS.md](../INTEGRATION-GAPS.md)), 2 days | prerequisite for any counted coverage; without it item 7 measures nothing |
| 1 | `docs/spec/soft-norms.md`: attributes (1.1), `ValueSoft` (1.2), `soften` (1.3), coherence and the conditional contract (1.4), report (1.5), wordings, diagnostics (`SoftOverHard`, `RankAgainstPrecedence`, `MissingExceptionDecider`, `UnknownRank`, `TieAgainstOrder`, `DualGuardCycle`, `HardConstraintAltered` for a rule narrowed hard by citation that carries a switch), acceptance fixtures below; Astra + Fable statement review | spec, 3 days | review questions listed after this table |
| 2 | Profile `soft-norms@0` requiring `norms@0`; fields `mode`, `rank`, `alterable`, `exception` on W2 `norm` content; ranks, flag and `instruction_of` in the environment (identity-bound like `regulated`); `outweighs` identities bind declared act, ordered rank pair and act argument sorts; `Background_base′` generator slot `soft` (coherence premises over all `CP(T)`, exception `necessary`/`sufficient` premises); no W5 dependency | Python `ve/softnorms.py`, `ve/document.py`, `ve/profiles.py`, `ve/background.py`, 5 days | all `norms@0` fixtures and hashes unchanged; W1's `check_conflict`, tableau and search reused on `T′` |
| 3 | Surface registrations (`should`, `generally`, `serves`, `outranks`, `are not ranked`, `is excepted when`, `takes account of`, `is decided by`, header options, legend attribution), the two synonyms, profile-gated rejection, the frequency-versus-norm paraphrases; W7 harness fixtures; `tests/test_english_unambiguity.py` | `ve/surface/softnorms.py`, `ve/norm_english.py`, 3 days | `Rule ` and `By default, ` reused, disambiguated on following tokens |
| 4 | Lean `lean/VE/SoftNorms/{Tree,Soften,Semantics,Coherence,Status,Wire,Admission,Run}.lean`: `SoftTree`, `ValueSoft`, `soften`; theorems `soften_wellFormed`, `soften_faithful`, `hard_over_soft`, `hard_never_weighed`, `rank_resolves`, `rank_acyclic`, `weighing_points_complete`, `soft_conflict_decomposition`, `coherent_expands` (W1 lemma instance), `soft_conflict_free`, `soft_route_acceptance`, `soft_route_countermodel`, `soft_wire_acceptance`, `soft_wire_conflict_sound` (W1's restated with `BaseAdmissible′`), `authority_independent`; executable `ve_soft_norms_route` regenerating `T′`, `Coh_T` and `Background_base′` from raw JSON, delegating checker calls to unchanged W1 functions; `lean/SOFT-NORMS.md`; audit allowlist unchanged | Lean, 7 to 10 days | frozen `Norms/*`, `Route/*` untouched; W1's per-structure lemmas reused, document-wide theorems restated |
| 5 | Coverage: residual lines and grouping in `tools/coverage_dashboard.py` and `ve document coverage`; `conditional_on` on every soft report; split-only baseline mode | Python, 2 days | metrics schema addition only |
| 6 | W8: `add_default_rule`, `add_rank`, `set_exception`, `set_factors`; paraphrases and extra example situations including the derived carve-outs and the collision resolution; translation rule for force words; fidelity gate before offering | `ve/assist/*` | exception and decider always shown; `unstated` shown as such |
| 7 | Pilot re-run on the pinned constitution: re-split `norms` units; split-only baseline under `norms@0`; translate :34-37, :166, :181-192, :281-293, :325-347, :405-423, :433-445 with reading sets and cited narrowings; re-examine the five open terms' deciders and `u0214`; blind whole-span fidelity review auditing every act identification; report status and residual deltas against the split-only baseline and against `run-20260927T0407Z` | pilot, 3 days | only measured numbers are claimed; every translator choice is an attributed unit |

Acceptance fixtures for item 1 (deterministic, hand-written expected results, Python and Lean where a case kind
exists), beside norms.md 10.1 repeated on soft trees:

- (α) A1 regression: two default rules of opposite effect on act X, ranks a over b, holistic; both eligible;
  `outweighs_{X,b,a}` true:
  the lower alone selects; false: the higher alone; `Norms.Value T′` equals `ValueSoft`; exactly one expansion.
- (β) A2 mixed: default `should X` (+r) and strict `must not X` (−m), both live: X neither required nor permitted,
  CONFLICT-FREE; strict `must X` and default `should not X`: required and permitted; same-predicate strict versus
  default likewise.
- (γ) completions: default `should X`, `m` deny-by-default, no rule on `m`: CONFLICT with the witness "rule not
  excepted"; `m` allow-by-default: CONFLICT-FREE. Default `should not X` with `r` allow-by-default: CONFLICT.
- (δ) soft–soft across the dual, unranked: WEIGHING POINT with obligation; ranked: RANK-RESOLVED; certificate for
  the conditional claim replays; dropping `Coh_T` from the background makes the same certificate fail to replay.
  Different classification budgets leave `Coh_T` unchanged; `conditional_on` names only undischarged premises used.
  The paraphrase permits resolution by a switch or another rule's defeat without either exception holding.
- (ε) alternating collision cycle: four eligible defaults on X, ranks A>B>C>D, A/C require, B/D release, holistic;
  findings B>A, C>B, D>C, A>D (`outweighs_{X,B,A}`, `outweighs_{X,C,B}`, `outweighs_{X,D,C}` true,
  `outweighs_{X,D,A}` false). D alone is effective; the `override_cycles` warning names the situation without
  adding an assumed obligation.
- (ζ) authority: a strict user-alterable rule; an operator-attributed predicate in its guard versus not; the
  report's per-party result flips only in the first case; the switch predicate for the operator does not exist.
- (η) W1's diamond (10.1 q) and grandchild (10.1 d) as default rules; a strict child of a default parent; a default
  child of a strict parent rejected `SoftOverHard`; a default rule with author `unless` and an exception: `live`
  false under either.
- (θ) `TieAgainstOrder`; `DependencyCycle` on ranks; `RankAgainstPrecedence` as a warning with unchanged semantics;
  `DualGuardCycle` when a guard mentions the dual predicate on both sides.
- (ι) vacuity: `Γ` fixing `excepted_M` and `excepted_N` false at a weighing point makes a dependent certificate
  `vacuous` when `Γ` also fixes guards, carve-outs, switches and other defeats so that both rules select; false
  exceptions alone do not suffice. The report's coherent-model exhibit fails and says so.
- (κ) chain: A requires X, B forbids X, C permits X, ranks A>B>C, strict flag, all live, no strict rules or author
  precedence, permission deny-by-default. A and C select; X is required and permitted, CONFLICT-FREE.
- (λ) blocked dominator: strict `need not X`, higher-ranked default `should X`, lower-ranked default `should not X`,
  all live, strict ranking, permission allow-by-default. The strict release blocks the obligation, which does not
  dominate the prohibition; the prohibition selects. X is neither required nor permitted, CONFLICT-FREE.
- (μ) hard parent H requires X with a strict user-alterable exception E releasing X. Switching E off changes
  whether H selects, despite H being hard. Local independence holds with strict switches fixed; the global
  decision-free-cone hypothesis fails.
- (ν) two declared acts with different argument sorts share the same ordered ranks L<H. Their distinct
  `outweighs_{act,L,H}` predicates use each act's sorts; elaboration, identity binding and rendered witnesses retain
  the act and rank pair without conflating the predicates.

Recorded answers for the statement review: step 3 uses higher effectiveness and lower eligibility, with the
asymmetry stated in English; at a fixed act and tuple an eligible default guarantees some effective default before
author precedence, so the all-dominated case is unreachable. The item-1 statement review by Astra + Fable checks
the spec against the converged corrections transcribed here. Remaining questions: is `Coh_T` in base admissibility,
with results marked conditional, an acceptable reading of "check under all admitted interpretations or identify the
chosen one"? Is the attribution check the right scope for "authority"?

Sequencing: draft-3 transcription without a further plan round → 0 and 1 in parallel → Astra + Fable item-1
statement review → (2, 3, 4 in parallel) → 5 → 6 → 7. Item 4 does not wait on the W3/W5 composition
gaps: no soft construct needs a defined predicate or a data flag; a guard that needs one inherits the existing
`UnsupportedProfile` answer.

## 6. Risks

1. **OPEN read as "checked and true".** Mitigation: the residual is the headline; every default-rule paraphrase names
   its exception and decider; metrics separate `default_exceptions`.
2. **Conditional read as unconditional.** A CONFLICT-FREE soft document is conflict-free *under coherent findings*.
   Mitigation: the status text says so; `conditional_on` is on every report; the weighing-point witnesses are shown as
   countermodels to the unconditional claim; the coherent model is exhibited.
3. **Residual size.** One exception per default rule makes the constitution's residual large. It is honest, but it must
   be shown grouped by decider and rank or the dashboard reads as failure.
4. **Force drift in translation.** Sources use "should" for strict rules too (:433). Collapsing to `should` weakens
   the source; to `must`, strengthens it. Reading sets with cited narrowings (section 4) are mandatory and audited in
   item 7.
5. **False comfort.** "No weighing points" does not mean the rules are jointly followable in practice; cross-act
   incompatibility is invisible until stage 3, and on the constitution most hard constraints and soft rules regulate
   different acts (1.6). Status text must say "among rules on the same act".
6. **Naive reuse of the W1 verdict** on `T′` without `Coh_T` reports CONFLICT for every soft collision; the conditional
   contract of 1.4 is the contract, with fixture (δ) as regression. Dominance must use higher effectiveness and
   lower eligibility: a defeated higher opponent or a strictly blocked rule must not defeat a lower default.
   `soften_faithful` and fixtures (α, η, κ, λ) guard this.
7. **Reviewer objection: an always-available exception makes a rule vacuous.** It changes no strict rule, and a
   default rule's content is exactly "required unless excepted"; without premises about `excepted_N` nothing about
   the act is provable, and the report says so. The certified obligations on the deciders (`Coh_T`) are the
   non-vacuous part. The statement review settles this before Lean starts.
8. **Zero-training English.** `should`/`must` are near-synonyms to many writers; `serves`/`outranks` are new keywords;
   `generally` versus `typically` is a distinction writers do not make. Mitigation: the IDE never accepts a default rule
   without showing the excepted situation and, for the frequency words, both paraphrases; W8 fidelity gate first.
9. **No measurable gain.** The 154 blockers are labels; item 7 may find few units whose only blockers are norms and
   defaults. The plan is then still worth its spec (soft norms are needed by every policy document), but the pilot
   headline must be reported as measured, including zero.

## 7. Disagreements

No A or B finding is rejected. Three remedies differ from what the review suggests or implies, with reasons:

1. **Completion outcomes (A2).** The review asks that mixed and soft obligation–permission conflicts "including
   completion outcomes" be included. They are included in the check (1.4), but a soft obligation is **not** made to
   give way to a deny completion: a default obligation that selects where the act is forbidden by default and no rule
   permits it is reported as CONFLICT, as W1 10.1(a) does for strict rules. Reason: carving defaults out on
   completions would make every default obligation vacuous under a deny default (it could never require anything the
   document does not separately permit), and the completion is the environment's legend, not a rule that can
   dominate. The author's fix is one sentence (`may X`, or an allow default), and the witness names it.
2. **Authority (B1).** The review asks the theorem to be scoped so that omitting a switch is not read as "operator
   instructions cannot affect the rule". Agreed and done (section 3, item 6). But no checker can certify that a
   decider's open judgment (`excepted_N`, `outweighs`) ignores a party's instructions; that is open-term adjudication,
   outside certification by the converged rule (VISION.md, item 8). The plan therefore does not promise a stronger
   authority theorem for default rules than the attribution check, and says so in the report rather than leaving the
   gap implicit.
3. **Scope of item 0 (C1).** The end-to-end admission test the review requires depends on the `ve-document@1` loader
   carrying `norm` units, which is a W1/W2 integration gap, not a soft-norms construct. The plan makes it item 0 and a
   hard prerequisite for any counted number, but records it under the integration owner rather than inside the soft
   profile, so that its absence blocks the pilot claim and not the semantics review.

Two points where the plan goes further than asked, noted so they are not mistaken for disagreements: `typically`,
`normally`, `usually` and `as a rule` are dropped as synonyms outright rather than disambiguated case by case (B3),
and in translation the act phrase "be willing to tell" is kept verbatim instead of being narrowed and attributed (B2).

## 8. Review response table (finding → change)

| Finding | Change in this draft | Where | Regression |
|---|---|---|---|
| A1 — holistic elaboration circular (`H = ¬L`, `L = ¬H`) | `ValueSoft` defined on `T` with well-founded upward recursion: higher effectiveness, lower eligibility; `soften` unfolds it into one derived carve-out per rule and no derived precedence edges; default selection after author precedence is not used by dominance; the two-winner example has one winner | 1.2, 1.3 | (α), (η), (κ), (λ) |
| A2 — hard-over-soft misses `should X` versus `must not X`; mixed and soft dual conflicts; completions | collision defined by effect across the dual pair (`CP(T)`); `blocked_N` includes the dual's strict decision; `hard_over_soft` covers same predicate and dual; soft–soft dual collisions are classified pairs in `Coh_T`; completion pair conflicts stay CONFLICT with the completion named; `DualGuardCycle` for the stratification case | 1.1, 1.2 step 2, 1.3, 1.4 "Completion outcomes", 7.1 | (β), (γ), (δ), (θ) |
| A3 — residuals do not restore model correspondence; specify admissible assignments, conditional guarantees, vacuity | decision assignments and `Coh_T` defined; `Background_base′`/`BaseAdmissible′`; `coherent_expands`, `soft_conflict_decomposition`, `soft_conflict_free` as the certified statement; route theorems restated, not inherited; `conditional_on` on reports; three vacuity measures incl. the exhibited coherent model; draft 1's "intended reading" retracted | 0, 1.4, 1.5, 3, 5 item 4 | (δ), (ι) |
| B1 — authority claims contradict the language; separate strictness, defeasibility, authority; scope the theorem | `mode`, `alterable`, `rank` independent; `hard` derived; strict alterable rules allowed (rule 20); "strict rules have no switch" withdrawn; switches plus attribution cone check with stated limits; `hard_never_weighed` local with strict inputs fixed, global only with a decision-free dependency cone | 1.1, 1.3, 3 items 3 and 6, 7.2 | (ζ), (μ) |
| B2 — fake precision: "such as" as sufficient conditions, "be willing to tell" as "must tell", "some" as a specific switch, unsourced decider | "such as" → `factors` with a new wording and no premise; act phrase verbatim; alterability a READINGS set with the :192 narrowing only where cited; deciders per source (the assistant at :34, :325) or `unstated`; every translator choice an attributed unit; examples rewritten with provenance; rule 12/13 collision claim withdrawn (different acts) | 2 (table, examples), 4 | item 7 blind review |
| B3 — one-reading syntax does not justify collapsing the :37 set; "typically" is frequency; keep cited narrowings | :34-37 set keeps A and B and adds C; narrowing to {B, C} is a cited attributed unit; per-choice checking reports choice and citation; `typically`/`normally`/`usually`/`as a rule` no longer synonyms, READINGS in translation and a two-paraphrase prompt in authoring | 2 (synonyms), 4 | `tests/test_english_unambiguity.py`; 10.4-style per-choice test |
| C1 — strengthen the coverage experiment (labels, zero whole-unit upgrades, disputed `u0214`) | item 0 end-to-end admission as prerequisite; split-only baseline; blind whole-span fidelity review before counting; `u0214` no longer cited as precedent and re-examined with the other deciders; no predicted number | 4, 5 items 0, 5, 7, 6.9 | item 7 protocol |

## Summary

Soft norms enter VE as strict rules with a named open exception, elaborated by `soften` into a `norms@0` tree over an
extended vocabulary by adding one derived carve-out per rule and no derived precedence, so the semantics is a
terminating procedure (`ValueSoft`) and the elaboration is faithful to it by unfolding. Strictness, defeasibility and
instruction authority are three independent attributes; hard rules are strict and unswitchable. Collisions are
defined by effect on one act across the obligation/permission pair, so `should X` gives way to `must not X`
(`hard_over_soft`), soft collisions are rank-resolved or listed as weighing points, and completion conflicts stay
CONFLICT. The checker certifies conflict-freedom conditional on the coherence of the deciders' findings, stated as an
explicit base premise `Coh_T` that every soft result names; W1's per-structure lemmas are reused and its document-wide
route theorems are restated with that premise. `should`, `generally may`, rank sentences, factor lists, alterable
headers and exception declarations each have one reading; frequency words are not synonyms. In translation, force,
alterability and the priority sentence are reading sets with cited, attributed narrowings that never collapse the
source's set. Coverage counts a unit only after end-to-end document admission, against a split-only baseline, and
after blind whole-span fidelity review; no number is predicted.

## Change log

| Date | Revision | Changes |
|---|---|---|
| 2026-09-27 | Draft 1 | Initial plan: soft norm as strict rule plus open exception; ranks; alterable defaults; three-question status; coverage counting. |
| 2026-09-27 | Draft 2 | Applied every A/B finding of Astra's REVISE review and C1: `ValueSoft` as a terminating procedure with liveness-based dominance and carve-out-only elaboration (A1); effect-based collisions across the dual pair, dual-aware hard-over-soft, completion conflicts kept (A2); decision assignments, `Coh_T`, conditional route contract, vacuity measures, retraction of "inherited unchanged" (A3); independent mode/alterable/rank with a scoped authority check (B1); factors not sufficiency, verbatim act phrases, sourced or `unstated` deciders, provenance on every example (B2); preserved reading sets with cited narrowings, frequency words removed as synonyms (B3); end-to-end admission prerequisite, split-only baseline, blind whole-span fidelity, `u0214` re-examined (C1). Corrected line citations (:34, :44, :192). Added sections 7 and 8. Plan only: no code, Lean or frozen contract changed. |
| 2026-09-27 | Draft 3 | Transcribed the converged debate in `manage-agents/debates/soft-norms/astra.md` (round-2 groups 1–7; round-3 existence correction) and `manage-agents/debates/soft-norms/fable.md` (final round-3 joint position): higher-effective/lower-eligible dominance and unfolded carve-outs; `Coh_T` over all `CP(T)`, discharged classifications and used-premise reporting; local weighing independence, conditional global independence and `BaseAdmissible` retained; selection-disjointness English, pairwise defeat and cycle warnings; act-and-rank-indexed decision signatures; same/different-act readings and audit; operator-restriction wording removed from `@0`, strict children included in `yields′`. Added the chain, blocked-dominator, hard-parent/switchable-exception and differently typed acts fixtures; corrected the alternating-cycle fixture. The three final additions are the eligible-implies-effective statement and corrected proof in place of the false corollary, the asymmetry sentence in English, and this transcription without a further plan round; item-1 statement review by both reviewers gates items 2–4. Coverage protocol remains an implementation gate, with no gain claimed. Plan only. |
