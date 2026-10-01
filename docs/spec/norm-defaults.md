# The `unspecified` completion (`norm-defaults@0`): specification

> Status: statement specification, draft 2 (2026-10-01): draft 1 with the statement changes the Lean build and the
> integration review found (section 12). Draft 1 (2026-09-29) was written from [norm-defaults-PLAN.md](norm-defaults-PLAN.md)
> draft 2, which applies the converged statement review of plan draft 1
> (`manage-agents/debates/norm-defaults-spec/{astra,fable}.md`: FIX, CONVERGED after round 2); section 11 maps each
> finding to its change. Sections 1 to 10 are the plan's sections 1 to 10; draft 1 copied section 7's statements and
> section 9's fixtures from the plan exactly, and draft 2's departures from them are listed in section 12. This is the statement under review: a statement pass on this draft's
> changes (section 7's changed statements and fixtures u1, u5, u6, u12, u13 and u16) decides whether the Lean and
> Python work starts (PLAN-EXPAND2 rule 10), and a new draft alone opens nothing. Theorem statements and fixtures are
> implementation obligations, not claims of completed proofs or tests. The evidence (plan section 0) and the work
> items (plan section 11) stay in the plan. Inputs: [norms.md](norms.md) (W1, cited `norms n`),
> [soft-norms.md](soft-norms.md) (`soft n`), [rights.md](rights.md) (`rights n`), [alternatives.md](alternatives.md)
> (`alt n`), [document.md](document.md) (W2), `risk.md` and `risk-PLAN.md` on branch `design/risk` (`risk n`,
> `risk-PLAN n`), [VISION.md](../../VISION.md), `lean/VE/{Norms,SoftNorms,Rights,Alternatives}` and the pilot records
> cited in the plan's section 0. Nothing here changes a frozen contract, an existing profile's hash, a
> W1/soft/rights/alternatives theorem statement or a checker function.

## 0. Scope, one paragraph

norms 3.1 makes a regulated predicate's `default` mandatory and allows only `deny | allow`, and norms 4.3 completes
every case that no rule decides with that value, so a translator must pick one even where the source is silent, and
the checker reports the pick as the text's content (the plan's section 0 records the cases: an invented permission in
constitution u0165.s07, the collapse of u0156.s03's defeasible reading into the strict one, agent-policy's four
environments, UDHR's conditions moved into sorts, risk's `default_decided`). Under the profile `norm-defaults@0`, a
third completion, `unspecified`, says "the text is silent here". Where no rule decides an unspecified predicate, the
predicate is unconstrained except by the profile premise "whatever must be done may be done", and the checker reports
the point as **UNDECIDED** instead of a value. The direct semantics drops W1's third clause (2.2). The route
elaborates by `fill`, one fresh base predicate and one synthetic lowest-priority rule per unspecified predicate, run
last on every route, into an ordinary W1 tree, so W1's definitions, checker and theorems are reused unchanged (2.3).
The profile premise constrains fillings only at gaps (`Fill_T`, 2.4).

In this specification: the decisions (1), the semantics (2), checks and reports (3), the English (4), translation and
authoring policy (5), migration and conservativity (6), the Lean definitions and exact statements (7), agreement,
diagnostics and limits (8), the fixtures (9), the open questions (10), the statement review's findings and
changes (11), and the statement changes found by the Lean build and the integration review (12).

## 1. Decisions

| # | Decision | Where |
|---|---|---|
| D1 | New value `"default": "unspecified"` under a new profile `norm-defaults@0`; the field stays mandatory | 2.1 |
| D2 | Meaning: where no rule decides, the predicate is unconstrained, except where "whatever must be done may be done" forces it | 2.2, 2.4 |
| D3 | Elaboration by `fill`: one fresh base predicate `unsaid__p` and one synthetic lowest-priority rule per unspecified `p`; the result is an ordinary W1 tree, so W1 is reused unchanged; `fill` runs last on every route | 2.3 |
| D4 | Pair premises restricted to gaps (`Fill_T`) enter base admissibility, as soft's `Soft_T` does | 2.4 |
| D5 | Per-point status: SETTLED yes/no, UNDECIDED (two checked fillings) or UNKNOWN; undecidedness propagates upward through guards | 2.5 |
| D6 | CONFLICT-FREE means conflict-free under every admissible filling; a contradiction that needs a particular filling is a CONFLICT with a *latent* witness | 3.1 |
| D7 | Legend: "When nothing else in the text decides, the text does not say whether a <noun> may <act>." | 4 |
| D8 | Translation policy: `unspecified` unless a cited span states the completion; an uncited deny/allow that a situation reaches is the finding `UngroundedDefault` | 3.2, 5 |
| D9 | Conservativity: no existing identity, certificate or report moves; opting in is per environment | 6 |

## 2. Semantics

### 2.1 Declaration and wire

```json
"permitted": {"arguments": ["action"], "description": "the agent may perform the action",
              "regulated": {"role": "permission", "default": "unspecified", "act": "{0} be performed"}}
```

`unspecified` is accepted only when the environment enables `norm-defaults@0` (which requires `norms@0`); otherwise
`UnsupportedProfile: unspecified completion requires norm-defaults@0`. Any other value is `InvalidInput`, as today.
The field stays mandatory: an absent `default` is `InvalidInput` as today (norms 3.1: "no silent completion").
`unspecified` is a statement, not an absence, and an implicit value would give one meaning two spellings and so two
identities. The value is allowed on every role (permission, obligation, plain), on either member of a declared dual
pair and on both. Under the profile, author predicate names beginning `unsaid__` and author rule names beginning
`unsaid--` are `InvalidInput`: they are reserved for `fill`, as soft 1.3 reserves `soft__`.

### 2.2 Direct semantics: dropping the third clause

With completion `c_p ∈ {deny, allow, unspecified}` and W1's `P_p`, `N_p` (norms 4.2):

```text
Value3_p(S, v̄) := conflict   if P_p and N_p hold at v̄                              (W1's none)
                | yes        if P_p and not N_p
                | no         if N_p and not P_p
                | yes | no   if neither, and c_p = allow | deny                       (W1, unchanged)
                | unsaid     if neither, and c_p = unspecified
Intended3_p(S) := for every typed v̄: yes → p(v̄); no → ¬p(v̄); unsaid → no constraint; conflict → false
```

For deny and allow this is W1's `IntendedAt`. For an unspecified predicate it is the first two clauses of W1's
`elab_p`, `∀x̄. (P_p(x̄) → p(x̄)) ∧ (N_p(x̄) → ¬p(x̄))`: the whole change is **dropping the third clause**
`(¬P ∧ ¬N) → (p ↔ d)`. An **expansion** of a base situation `B` is a structure over `E` with base restriction `B`
that satisfies Background (flags, W3 definitions, literals, the profile pairs `∀x̄. r(x̄) → m(x̄)`) and `Intended3_p`
for every regulated `p`, over the lower tables as in W1. A conflict-free W1 document has exactly one expansion per
base situation. With gaps it has one per admissible way of filling the silences. For a CONFLICT-FREE document (3.1),
"the text says `p(ā)`" means that every expansion agrees (`settled_all_expansions`, 7). A CONFLICT document may have
no expansion for some fillings, so the statuses of 2.5 are defined over admissible fillings, not over expansions.
Only the profile premise constrains a gap (2.4).

### 2.3 Elaboration: `fill`

W1 is not edited. As `soften` does, the route elaborates into a W1 tree over an extended vocabulary:

```text
for every regulated p with c_p = unspecified:
  unsaid_p   a fresh base predicate `unsaid__<p>`, p's argument sorts, no flags, no rules: "the text does not say
             whether p(x̄)". It has no decider and is never asserted; it is the filling of the gap
  F_p        a synthetic rule named `unsaid--<p'>` (p' is p with `_` replaced by `-`): sign +, guard unsaid_p(x̄),
             no carve-outs, no `over`
  every root rule on p (a rule with empty `over`) gains `over: [F_p]`, so F_p is the parent of every root on p
  p's W1 completion is the placeholder deny
fill(E, T) := (E‴, T‴) with E‴ = E + {unsaid_p}, T‴ as above; nothing else changes
```

Why this is exactly 2.2. `F_p` is the parent of every root on `p`, so it selects iff `unsaid_p` holds and no root
subtree yields. A subtree yields iff one of its rules applies, iff one of its rules selects (the lowest applying rule
selects). So `P‴_p = P_p ∨ (unsaid_p ∧ ¬P_p ∧ ¬N_p)` and `N‴_p = N_p`. With the deny placeholder, W1's `elab_p` on
`T‴` says: `p` is true where `P`, false where `N`, `p ↔ unsaid_p` where neither, and has no model where both hold,
since `P‴ ∧ N‴ = P ∧ N`. Forgetting the unsaid tables, the expansions of `T‴` are those of 2.2 (`fill_expansions`,
7). The unsaid tables play exactly the part of soft's decision predicates: a base assignment the checker never
decides. No author rule gains a child, so every author rule's `applies`, `yields` and `selects` is unchanged
(`fill_selects_author`).

**Order.** `fill` runs last on every route: `fill(T)` for norms, `fill(soften(T))` for soft,
`fill(soften(correlate(D)))` for rights, `fill(inlineTree(A))` for alternatives and risk. The order matters. Inside
`soften`, a strict `F_p` would block every default rule on `p` wherever no strict rule decides (soft 4.2 step 2), and
its selection would depend on default selection, which is circular. After `soften`, `F_p` only reads finished
selections. **Size**: one node and one precedence level per unspecified predicate; no guard is copied or inlined
(limits, 8).

### 2.4 Pair premises at gaps: `Fill_T`

The profile premise `∀x̄. r(x̄) → m(x̄)` (norms 3.1) is in Background. With free unsaid tables, W1's pair target
`O_r‴° ∧ ¬O_m‴°` would report spurious conflicts at fillings that contradict it: `unsaid_r` true where `m` is decided
false, or `unsaid_m` false where `r` is decided true. The text's own "must implies may" excludes those fillings, so
they are not conflicts in the text. Hence:

```text
gap_p(x̄) := ¬P_p°(x̄) ∧ ¬N_p°(x̄)   if c_p = unspecified, else ⊥
            (author rules only; ° is W1's outcome substitution computed on T‴, so lower gaps appear as unsaid atoms)
Fill_T   := for every declared pair (r, m) with r or m unspecified:
            ∀x̄. ¬(O_r‴°(x̄) ∧ ¬O_m‴°(x̄) ∧ (gap_r(x̄) ∨ gap_m(x̄)))              label unsaid:pair:<r>,<m>
BaseAdmissible‴(B) := W1 BaseAdmissible(fill T)(B) ∧ B ⊨ Fill_T
```

A filling is admissible when it respects "whatever must be done may be done" at the gaps:

- `m` unspecified, `r` required by a rule, no rule on `m` deciding: every admissible filling has `unsaid_m` true
  there, so the act is SETTLED permitted "because it is required".
- `r` unspecified and `m` decided false: `r` is SETTLED false, "not required, because not permitted".
- Both are gaps: the admissible fillings of `(r, m)` are (no, no), (no, yes) and (yes, yes); both are UNDECIDED.
- Both sides decided (by rules or by allow/deny completions): the pair conflict is still CONFLICT, and W1
  10.1(a, b) are unchanged.

Three properties are required (7). `canonical_fill_sat`: the filling "true for permission members of pairs, false
elsewhere" satisfies `Fill_T` in every base situation, so `Fill_T` never excludes a situation the author's
vocabulary can describe. `fill_extends`: `Fill_T` constrains only the unsaid tables of pair members.
`conflictFreeU_consistent`: a CONFLICT-FREE document has an expansion in every base situation. This also removes
soft 6.6's forced choice: a default obligation beside an unspecified permission is CONFLICT-FREE, and the act is
permitted wherever it is required.

### 2.5 Status of a point; inherited undecidedness

```text
SETTLED yes   every admissible filling (B ⊨ Fill_T) gives O‴_p°(ā) true                         "the text says so"
SETTLED no    every admissible filling gives false
UNDECIDED     two admissible fillings give different values                                    "the text does not say"
UNKNOWN       neither shown within budget (budget named); never promoted to either of the others
```

Every admissible filling counts, including one at which a conflict target is true. A status that skipped conflicting
fillings would report the value of the remaining ones as the text's content: in u6 the only conflict-free filling
has `y_permitted(a)` false, so the checker would say the agent may not Y, and where no filling is conflict-free both
SETTLED values would hold vacuously. In a CONFLICT-FREE document every admissible filling is conflict-free, so there
the statuses are unaffected, and a SETTLED point has its value in every expansion (`settled_all_expansions`).

UNDECIDED is not confined to unspecified predicates. Take `Rule 1. Every agent must report each action, if that
agent may perform that action.`, with `report_required` deny-by-default and `permitted` unspecified with no rule.
Then `report_required` is UNDECIDED wherever `permitted` is: "The text does not say whether the agent must report
a36: rule 1 decides only if the agent may perform a36, and the text does not say whether it may." This is
propagation, not invention. Its static footprint (every regulated predicate whose guard cone mentions an unspecified
one) is reported per predicate as `inherits_from`.

Evidence (the search is untrusted, and every piece of evidence is checked):

- **`table3`** computes outcomes on the finite base situation in DAG order, with every unsaid atom unknown, Kleene
  connectives and finite quantifiers. Each symbol is placed once: all its rows, and every close they make, are
  computed from the table before it and only then entered, so no row reads a close made at another row. Where
  a pair closes it applies the profile rule, only where the side it sets is a gap (its `gap` formula of 2.4
  Kleene-true there): `m` := yes where `r` is yes and `m` is a gap; `r` := no where `m` is no and `r` is a gap. The
  side it sets is the member being placed, or the earlier member if that is still unknown; a symbol placed between
  the two members has already read the earlier one as unknown and keeps its entry (enumeration settles it). Python
  and Lean compute this same table (`tabK`). A decided pair clash (`r` yes, `m` decided no) is never closed: it is a
  CONFLICT (3.1). A definite entry is SETTLED (`table3_sound`). Kleene is incomplete (`u ∨ ¬u` is unknown), so an
  unknown entry is not yet UNDECIDED.
- **Exhaustive check.** For an unknown entry, enumerate the assignments of the unsaid atoms in `ā`'s cone, up to
  `MAX_UNSAID_ATOMS` (proposed 12, so at most 4,096 assignments). The cone is the set of unsaid atoms on which the
  Kleene value at `ā` depends, closed under the ground `Fill_T` instances that mention one of them (`coneAtoms`); the
  other unsaid atoms stay unknown. An assignment under which some `Fill_T` formula is Kleene-false is skipped;
  agreement of the rest is SETTLED (`settled_of_enumeration`). Any atom list is sound: an admissible filling agrees
  with the assignment of its own values on the list, no `Fill_T` formula is false under it, and a definite Kleene
  value is the filling's value. The closure makes the check exact: a touching instance is decided by the cone, an
  instance outside it is true under the canonical filling off the cone, so every assignment that is kept extends to
  an admissible filling. Enumerating only the cone with the other atoms fixed to one filling would not be sound; the
  other atoms are unknown, not fixed. The budget counts the cone's atoms, in Python and in Lean.
- **UNDECIDED** needs two finite fillings, each validated (`Fill_T` true on the situation), with opposite values at
  `ā` (`undecided_witness_sound`). The search starts from the canonical filling and flips atoms in the cone.
- Otherwise the status is UNKNOWN, naming `MAX_UNSAID_ATOMS` or `MAX_EVALUATIONS`.

## 3. Effects on checks and reports

### 3.1 Conflict checking

W1's check runs unchanged on `fill(T)` over `Background_base(E‴) ++ Fill_T`, with the same targets (`conflict` per
predicate, `pairConflict` per pair).

- **CONFLICT-FREE** := `∀B. BaseAdmissible‴(B) → ConflictFree(fill T)(B)`. Every situation, however its silences
  are admissibly answered, has exactly one filled expansion (W1's `conflictFree_expands_document` on `T‴`). With
  `canonical_fill_sat`, it has at least one expansion in source terms: the text is consistent in every situation.
- **CONFLICT witness**: a finite base situation *with a filling* (valid for `E‴_base` and `Fill_T`) at which a target
  is true. The untrusted classifier uses `table3`. It is a `settled conflict` when the target is true under every
  filling (for example two author rules of opposite sign), or a `latent conflict under <p>(ā) = yes | no` when the
  target is Kleene-unknown, in which case the filling is shown.
- **Where new conflicts come from.** For an unspecified `p` the local target equals W1's (`fill_local_conflict`).
  New conflicts arise only as latent ones, where a guard mentions an undecided lower predicate, never from the
  completion itself. Pair conflicts at gaps are excluded by `Fill_T`; decided pair conflicts are unchanged.
- **Unchanged:** UNKNOWN, overlap and vacuity. **Fragment** (norms 7.1): unsaid predicates are relational base
  predicates without flags, so W1's gate stands, plus "every `Fill_T` formula is quantifier-free after
  substitution"; `conflict_smallModel`'s proof obligation extends to `fill` (`fillPremises_universal`).

**Honest cost.** A document that is CONFLICT-FREE with `y_permitted` deny may be CONFLICT with it unspecified, for
example `must X if may Y` beside `must not X` (fixture u6). This is deliberate: under deny, the consistency rested
on an invented "Y is forbidden". Latent conflicts are CONFLICT, with a witness kind that names the filling (Q1,
closed by the statement review). Beside the CONFLICT, `y_permitted(a)` is UNDECIDED (2.5), never "the text says the
agent may not Y".

### 3.2 Gaps, grounded defaults, coverage and queries

| Line (per regulated predicate) | Evidence | Meaning |
|---|---|---|
| `completion: unspecified \| deny \| allow` | environment | as declared |
| `gaps: none` | certificate for `∀x̄. P_p°(x̄) ∨ N_p°(x̄)` over `Background_base(E‴) ++ Fill_T` | rules decide every situation, however lower gaps are filled; the completion is never used |
| `gaps: reachable` | a checked situation and filling where neither holds, rendered, e.g. "the text does not say whether an entity other than Claude may generate child sexual abuse material" | the silence the author or translator must see |
| `default reached` (deny/allow) | the same formula and evidence | where the completion, not a rule, decides; replaces risk's interim `default_decided` |
| `grounded: <unit ids>` or `UngroundedDefault: <p>` | the document's `completions` block (5) | translation documents only; the finding appears only when `default reached` has a witness |
| `inherits_from: [q, …]` | static cone | may be UNDECIDED because `q` is |

- **Residual and unit status** (document.md coverage). A new residual line, `gaps`, lists the unspecified predicates
  with reachable gaps and counts `UngroundedDefault` findings. A gap is not an open term: it has no decider and
  nobody is asked to decide it. It does not change unit status: a norm unit on an unspecified predicate says exactly
  what the source says and stays CHECKED.
- **Grounding.** A reached, uncited deny or allow in a translation is added content, so it is a finding (a report
  line, never a rejection). This implements ARCH-ROADMAP line 14 ("default must cite text or be OPEN"), with
  `unspecified` as the uncited option.
- **Queries.** `ve document readings --conclusion` and P0 entailment reports keep their mechanics. A conclusion about
  an undecided point is not entailed, and its countermodel includes a filling. Rendering names every filled gap
  ("Here the text does not say whether Sol may generate …; this situation answers 'yes'"), so "the text is silent"
  is distinguishable from "false in a situation the facts allow".
- **`reports@0` quoted norm content.** The completion enters `environment_id` only; no layer, no other change.

### 3.3 Soft norms, rights, followability and risk

**Soft** (`soften` unchanged, `fill` after it):

- **The collapse is fixed.** A default `should not X` on an unspecified permission, where its exception applies
  (`excepted_N` true): no rule selects, so X is UNDECIDED, not "not permitted". u0156.s03's strict and default
  readings are now told apart by a checked situation, strict SETTLED no against default UNDECIDED (`excepted_lifts`).
  That is the "model that really tells the readings apart" the 1800Z audit asked for (AUDIT.md:23), for norm
  readings.
- soft 6.6 (pair conflicts against a completion) is confined to deny and allow.
- `ValueSoft3` is `value3` over `DecidesSoftD` (`fill_soft_value`, by `soften_faithful`).
- A strict decision still blocks default rules; a gap is not a decision and never blocks (`F_p` is not in `T`).
- **Coherence.** `Coh_T`'s `selects′°` contain unsaid atoms wherever guards mention unspecified predicates.
  Recommendation: classify pairs with unsaid atoms universally quantified. DISJOINT certificates are over
  `Background_base(E′‴) ++ Exc_T ++ Fill_T`, and WEIGHING POINT witnesses carry their filling (Q3).
- The report (soft 7.2) gains `gaps`.

**Rights** (`correlate` and `soften` unchanged, `fill` last):

- The third variant of fixture (γ) (Limitation 29 on Art. 9) is the faithful one. With `arrest_permitted`
  unspecified, a limited arrest (the line silenced by `limpack`) is UNDECIDED: Art. 29(2) allows limiting the right
  but grants no permission. The allow variant ("permitted by the default") and the deny variant both add content.
- `rightsOf` and `dutiesOf` project selection (rights 4.4) and are unchanged (`fill_selects_author`); "the
  projections say nothing a completion says" now covers gaps. "By default a state may arrest" becomes "the text
  does not say whether a state may arrest".
- Narrowing mechanisms, licensing, `limitationScope` and the bar are unchanged. `F_p` is not right-derived and is
  excluded from `narrowings`, as `bar_m` is special-cased.
- `ValueRight3` follows from `correlate_faithful` and `fill_soft_value`.

**Followability** (`alternatives@0`): `clear(r, a)` requires `O_m°(a)` (alt 4.6). On `fill(inlineTree A)`, with
`Fill_T` added to `Background_baseAlt`, FOLLOWABLE requires a clear alternative under **every** admissible filling;
an alternative whose permission is UNDECIDED is clear in some fillings only. FOLLOWABLE is a certificate over
`Background_baseAlt(E‴) ++ Fill_T ++ Γ_base` (`followableU_sound`). DILEMMA is a witness situation plus a filling.
The untrusted diagnosis gains a branch before NONE-PERMITTED: `UNSETTLED(a, …)`, when no alternative is permitted in
the witness filling but some available alternative's permission is UNDECIDED ("no alternative is known to be
permitted: the text does not say whether R may push"). In scenarios (alt 4.7) each alternative is clear, not clear,
or "undecided: the text does not say whether it may be performed". A chooser is never said to "have a clear action"
because of an undecided alternative. A weaker verdict "followable if the silences are answered favourably" is Q4 (not
recommended).

**Risk** already reserves UNDECIDED (risk-PLAN.md:651) and "UNDECIDED and not clear" (risk-PLAN.md:1086-1089).
risk's `status` column gains UNDECIDED from 2.5, and `default_decided` survives for deny and allow as the
`default reached` evidence of 3.2. risk's route applies `fill` last; chance and severity are untouched. In agent-ops
with `permitted` unspecified: in k9 (empty rule set) all three alternatives are UNDECIDED and none is clear; in k10,
"running the job with the memory limit" and "asking the user" move from `default_decided` to UNDECIDED. Sequencing
is Q9.

**Integration gap (2026-10-01).** The merged alternatives and risk Lean routes still consume completed deny/allow
norms and do not replay `Fill_T` or classify an unspecified permission. Their combination with `norm-defaults@0`
is rejected at profile validation with `UnsupportedProfile`; neither route may report a two-valued decision for a
silent permission. The W1 norm-defaults route, soft and rights semantics, and the existing alternatives/risk routes
remain available separately. Implementing `fill(inlineTree A)` and risk's three-valued decision report, followed by
the cross-route fixtures u10/u11, is required before these profile pairs can be enabled.

**Grounded completions stay.** Cedar's `permitted(request)` stays deny: Cedar's documented semantics is deny unless
a policy permits, a citation the adapter records. Gatekeeper's `admitted` stays allow for the same reason.
Candidates for `unspecified`, which this specification does not change: norms 9.1's "By default, a state may make a
law", and soft 2.4's `comply_permitted`, no longer forced by 6.6.

## 4. English

### 4.1 Legend sentences

| Role | deny | allow | unspecified (new) |
|---|---|---|---|
| permission | `By default, a <noun> must not <act>.` | `By default, a <noun> may <act>.` | `When nothing else in the text decides, the text does not say whether a <noun> may <act>.` |
| obligation | `By default, a <noun> need not <act>.` | `By default, a <noun> must <act>.` | `When nothing else in the text decides, the text does not say whether a <noun> must <act>.` |
| plain | `By default, it is not the case that <verbalisation>.` | `By default, <verbalisation>.` | `When nothing else in the text decides, the text does not say whether <verbalisation>.` |

Example (u0165.s07): "When nothing else in the text decides, the text does not say whether an entity may generate
child sexual abuse material." **One reading:** when no rule, no `By default` sentence and no pair sentence settles the
answer, alone or together, neither answer follows. It never means "may", and never "must not". The sentence is true
for every role, including a member of a declared pair: for a predicate outside a pair it says what "when no rule
decides" would; in u5(a) and u5(b), where no rule on the act decides but the pair sentence (with, in (a), the other
member's `By default` sentence) settles it, the sentence does not claim silence, and finding the answer is a reasoning
item that 4.3 scores. A wording that says only "when no rule decides" would be false there. **Registration:** one
surface record, `norm-unspecified`, with keyword `When nothing else in the text decides, ` under `norm-defaults@0`,
rendered by `ve/norm_english.py:default_sentence` beside today's `By default, ` sentence, for every role. No
registered keyword begins with `When` today (a grep of `ve/surface` on 2026-09-29), and the registry's
duplicate-keyword refusal re-checks it; u13 adds a keyword-collision check for `When nothing`. It joins the mixed
English harness and `tests/test_english_unambiguity.py`.
**Pair sentence:** in the legend of every declared pair with an unspecified member, `Whenever a <noun> must <act>, it
may <act>.` This is the profile premise. W1 never renders it, because a completion always decided both sides; now it
visibly settles gaps. It is render-only: the dual declaration is its source (Q10).

### 4.2 Paraphrases

- **Carve-out** (norms 2.5): "When this condition holds, this rule is silent; other rules may decide; if none does,
  the text does not say whether entry is permitted." norms 2.6 row 2 gains a third reading: with the completion
  unspecified, deprivation with due process is "the text does not say", closer to the literal "unless" than either
  W1 default. The IDE shows it when the author chooses the completion.
- **Soft default** (soft 2.3): "… is not permitted unless rule 12's exception applies there; where it applies and no
  other rule decides, the text does not say whether it is permitted."
- **Status:** "The text says an instance of Claude must not generate … (rule hc-csam)." / "The text does not say
  whether Sol may generate …: no rule decides this situation." / inherited, as in 2.5 / pair: "The assistant may
  share it: rule 12 requires sharing it, and whatever must be done may be done."
- **Latent conflict:** "Rules 1 and 2 contradict each other if the agent may Y, and the text does not say whether it
  may. To settle it, add a rule about Y, or make one rule an exception to the other."
- **`F_p` is never shown as a rule.** Its selection renders as "the text does not say"; a filling renders as "this
  situation answers 'yes'".

### 4.3 Reader testing (zero-training)

The main risks are "not forbidden, therefore allowed" (the u0165.s07 failure moved into the reader's head) and
reading "does not say" as a third deontic value ("optional", "indifferent"). The protocol belongs to W8's
per-construct held-out fidelity gate (VISION.md, roadmap row 2).

**Materials:** the natural view only (rules and legend; no tutorial, no logic). Each item gives a situation and asks
"According to the text, may (must) … ?", with the answers Yes, No and The text does not say. **Items:** u0165.s07
(Claude; another entity); u0156.s03, excepted and not, under both readings; agent-policy a27, a36, a37 and a38 plus
two covered actions each way; a pair item ("it must report it; may it?"); an inherited item; a carve-out item. Each
is crossed with the deny, allow and unspecified legends, between subjects per item. **Measures:** agreement with the
checker's status; *silence misread* (Yes or No where the checker says UNDECIDED); *invented silence* ("does not say"
where the checker SETTLES by a rule, a default or the pair premise). **Wordings:** A (the short legend of 4.1) and
B (A plus ": this text neither permits nor forbids it"), chosen by measurement; B risks being read as a third
deontic status. **Translators** (W2's second-rater protocol): two raters decide from source and unit whether the
source states the completion, and agreement is reported; a disagreement becomes `unspecified` or a recorded note
(Q8). Thresholds and sample sizes are W8's (Q6).

## 5. Translation and authoring policy

Recommendation: `unspecified` becomes the translation default **as policy, not as a parser default** (2.1).

- **Translation** (a `ve-document@1` over source prose). Translator guidance and tooling emit `unspecified` unless a
  source span states the completion ("everything not expressly permitted is forbidden", or Cedar's documented deny).
  A deny or allow is grounded in a document-level block `{"completions": {"<p>": {"cites": ["<unit id>", …],
  "reason": "…"}}}`, validated like narrowing `reason_spans` (the ids exist and their spans are in the source); the
  block is part of the document identity, not of `environment_id`. A deny or allow with a `default reached` witness
  and no citation is `UngroundedDefault: <p>`. One without a witness is not flagged. Switching it to `unspecified` is
  proved meaning-preserving (`unreached_switch`) by a `gaps: none` certificate for `p` on the switched document
  `U.switch p`; `default reached: none` on the document itself does not prove it (6.3).
- **Authoring.** The IDE asks, showing the three legend sentences with a situation no rule covers, with no option
  preselected; it never fills in the value.
- **Pilots.** The translator rule "NO INVENTED PERMISSIONS" (`manage-agents/ve-run-log.md:874`) generalises to "no
  invented completions", and pilot audits count `UngroundedDefault`.

Evidence: each record in the plan's section 0 shows a workaround needed only for want of a third value, namely the
constitution's 15 `deny` predicates over `claude_instance`, UDHR's conditions in sort descriptions and agent-policy's
four environments. Detecting a translation document mechanically is Q7.

## 6. Migration and conservativity

1. **Bytes.** No existing environment contains `unspecified` or enables `norm-defaults@0`, so for them every decoder
   behaves as today (`decode_conservative`): the same canonical bytes, `environment_id`, `meaning_id`s,
   certificates, conformance reports and frozen-source hashes. `fill` without unspecified predicates is the identity
   (`fill_conservative`: `fill U = U.D` and `Fill_T = []`), so each route's regenerated premises and targets are
   byte-identical on such documents. The whole existing suite is the regression (fixture Z).
2. **Opt-in** is explicit and per environment. Enabling the profile or changing a completion changes
   `environment_id`, as any declaration change does (norms 10.7), and with it every `meaning_id` and bound
   certificate. Stale certificates are rejected (norms 10.8).
3. **Migration audit.** `ve norms completions --audit <doc>` is Python, untrusted and report-only. For every deny or
   allow predicate it gives the `default reached` evidence. For a reached one it lists the conclusions and statuses
   that would change if switched (a re-run under `unspecified`). For an unreached one it gives the `gaps` line of
   `p` on the switched document `U.switch p`: a `gaps: none` certificate there is the certificate that switching
   preserves meaning (`unreached_switch`, whose hypothesis it is through `normDefaults_wire_gaps_sound`), and a
   reachable gap there is shown with its witness. UDHR SUMMARY.md:8's "completion is never used (checked under both
   completions)" becomes one such certificate. It never rewrites anything automatically.

   `default reached: none` on `U` is not that certificate. Counterexample: `x_required` unspecified with no rules,
   paired with `x_permitted` (deny, rule "may X if may P"), and `p_permitted` deny with the rule "may P if X need not
   be done". Under `U`, `O_x_permitted = O_p_permitted = ¬unsaid_x_required`, so `Fill_T` at the gap of `x_required`
   forces `unsaid_x_required` no; then `p_permitted` is yes everywhere and never reached, and `U` has the certificate.
   After switching `p_permitted`, the filling `x_required` yes, `p_permitted` yes (its gap filled yes),
   `x_permitted` yes is admissible: an expansion that `U` rejects, and `x_required` moves from SETTLED no to
   UNDECIDED. The switched document's `gaps` line for `p_permitted` is `reachable` (fixture a1).
4. **Pilots and use cases migrate by re-running, never by editing frozen keys.** Constitution: u0165.s07 goes back
   to an `entity` sort with an unspecified completion, and u0156.s03 and u0165.s03 become unspecified. Agent-policy:
   one unspecified environment is added beside the four shipped ones, which remain as regressions; the answer key
   stays frozen. UDHR: u052 and u112 move their conditions back into guards. Risk: agent-ops variants.
5. **Lean.** No existing statement changes and all new definitions go in new modules. Each route's `Wire` and `Run`
   file gains a profile branch and is repinned in the assurance manifest. `Main.lean` is untouched.

## 7. Lean: definitions and the exact statements

**Files.** `lean/VE/NormDefaults/{Tree,Fill,Semantics,Premises,Status,Wire,Run}.lean`, and `lean/NORMDEFAULTS.md`
listing each theorem in plain words. **Naming.** Names use no primes and none of the audit's banned words (`partial`,
`admit`, even in comments). These are statement schemata in the style of norms 6: helper names are defined here, and
the existing names (`Doc`, `Regulated`, `DecidesD`, `tupleVal`, `forget`, `IntendedAt`, `BaseAdmissible`,
`ConflictFree`, `DocumentExpansion`, `outcomeBase`, `pairConflict`, `pairs`, `before`, `envAt`, `size`,
`restrictAll`, `backgroundValid`, `canon`, `DecidesSoftD`, `DecidesR`, `inlineTree`, `regulatedNames`, `ruleName`,
`height`, `fuel`) are those in `lean/VE` today (`regulatedNames`, `ruleName` and `height` in `Norms/Tree.lean`).

```lean
namespace VE.NormDefaults
open VE.Norms VE.Route
universe u

inductive Completion | deny | allow | unspecified
  deriving DecidableEq, Repr

/-- A W1 document plus its `unspecified` predicates; each is declared in `D.T.regulated` with the placeholder
    `allowByDefault = false`. Soft, rights and alternatives instantiate `D` with `soften`, `soften ∘ correlate`,
    `inlineTree`. -/
structure UDoc where
  D : Doc
  unspec : List String

def completionOf (U : UDoc) (r : Regulated) : Completion :=
  if r.name ∈ U.unspec then .unspecified else if r.allowByDefault then .allow else .deny
def unsaidName (p : String) : String := "unsaid__" ++ p
def fillName (p : String) : String := "unsaid--" ++ p.map (fun c => if c = '_' then '-' else c)
def fillNode (r : Regulated) : Node :=
  { name := fillName r.name, pred := r.name, sign := true, guard := atom (unsaidName r.name) r.sorts,
    carveOuts := [], over := [] }

/-- `U.switch p`: `p`'s completion becomes `unspecified` (placeholder `false`, `p` appended to `unspec`). -/
def UDoc.switch (U : UDoc) (p : String) : UDoc :=
  { D := { U.D with T := { U.D.T with regulated := U.D.T.regulated.map fun r =>
             if r.name = p then { r with allowByDefault := false } else r } },
    unspec := U.unspec ++ [p] }

/-- `WellFormed U.D`; `unspec` duplicate-free, ⊆ regulated names, placeholder `false`; reserved prefixes unused; and
    the author-side limits of 8, which `fill_wellFormed` proves sufficient for `WellFormed (fill U)`:
    (i)   `ruleName (fillName p) = true` for every `p ∈ unspec` (its characters, and `p` at most 56 bytes);
    (ii)  `unspec.map fillName` duplicate-free;
    (iii) `U.D.T.nodes.length + unspec.length ≤ 256`;
    (iv)  `height U.D.T (fuel U.D.T) N ≤ 15` for every `N ∈ U.D.T.nodes` with `N.pred ∈ unspec`;
    (v)   the `VE.Bridge.formulaNodes` of every author guard and carve-out plus those of every `F_p` guard total at
          most 10,000. -/
def WellFormedU (U : UDoc) : Bool
/-- `E‴` (unsaid predicates as base predicates) and `T‴` (fill nodes; every root on p gains `over := [fillName p]`). -/
def fill (U : UDoc) : Doc
def unsaidNames (U : UDoc) : List String := U.unspec.map unsaidName
def pairMembers (U : UDoc) : List String   -- the members of declared pairs with an unspecified member
def sortsOf (D : Doc) (p : String) : List String   -- p's declared argument sorts

/-- `gap_p` (2.4): author rules only, substituted on `fill U`; `.bottom` unless `p ∈ U.unspec`. -/
def gapF (U : UDoc) (p : String) : VE.Formula :=
  if p ∈ U.unspec then
    .and (.not (subst (fill U).T (before (fill U) p) (pos U.D.T p)))
         (.not (subst (fill U).T (before (fill U) p) (neg U.D.T p)))
  else .bottom
/-- `default reached` (3.2) for any regulated `p`, deny/allow included: `gapF`'s `.and` body without its `unspec`
    test (`gapF` is `.bottom` off `unspec`, so it cannot serve a deny/allow `p`). -/
def reachedF (U : UDoc) (p : String) : VE.Formula :=
  .and (.not (subst (fill U).T (before (fill U) p) (pos U.D.T p)))
       (.not (subst (fill U).T (before (fill U) p) (neg U.D.T p)))
def fillPremises (U : UDoc) : List VE.Formula :=
  ((pairs U.D.T).filter (fun pr => pr.req ∈ U.unspec ∨ pr.perm ∈ U.unspec)).map fun pr =>
    bindAll pr.sorts (.not (.and (pairConflict (fill U) pr) (.or (gapF U pr.req) (gapF U pr.perm))))

def BaseAdmissibleU (U : UDoc) (B : VE.Structure.{u}) : Prop :=
  BaseAdmissible (fill U) B ∧ Sat B (fillPremises U)
def ConflictFreeU (U : UDoc) : Prop :=
  ∀ B : VE.Structure.{u}, BaseAdmissibleU U B → ConflictFree (fill U) B

inductive Outcome3 | yes | no | unsaid | conflict
noncomputable def value3 (P N : Prop) (c : Completion) : Outcome3 := by
  classical
  exact if P ∧ N then .conflict else if P then .yes else if N then .no else
    match c with | .allow => .yes | .deny => .no | .unspecified => .unsaid
noncomputable def Value3 (U : UDoc) (r : Regulated) (S : VE.Structure.{u}) (vs : List S.Carrier) : Outcome3 :=
  value3 (DecidesD U.D.T S (tupleVal vs) r.name true) (DecidesD U.D.T S (tupleVal vs) r.name false)
    (completionOf U r)
def IntendedAt3 (U : UDoc) (r : Regulated) (S : VE.Structure.{u}) : Prop :=
  ∀ vs, VE.TupleTyped S r.sorts vs →
    match Value3 U r (forget [r.name] S) vs with
    | .yes => S.relation r.name vs | .no => ¬ S.relation r.name vs | .unsaid => True | .conflict => False
/-- Expansions in source terms (2.2): no unsaid predicates. -/
def Expansion3 (U : UDoc) (B S : VE.Structure.{u}) : Prop :=
  restrictAll U.D.T S = B ∧ S.Admissible (envAt U.D (size U.D)) ∧ Sat S (background U.D) ∧
    ∀ r ∈ U.D.T.regulated, IntendedAt3 U r S

/-- Unsaid tables over `B`'s carrier, `B` extended by them, and the canonical expansion with them forgotten;
    all three keep `B.Carrier` definitionally (`canon` and `forget` only replace relations). -/
def FillTables (U : UDoc) (B : VE.Structure.{u}) : Type u := String → List B.Carrier → Prop
def withFill (U : UDoc) (B : VE.Structure.{u}) (F : FillTables U B) : VE.Structure.{u}
def canonicalFill (U : UDoc) (B : VE.Structure.{u}) : FillTables U B -- true on permission pair members, else false
/-- `canon` read on typed tuples: a layer symbol's relation holds only at tuples of its declared sorts (12, item 1). -/
def canonTyped (D : Doc) (B : VE.Structure.{u}) : VE.Structure.{u} :=
  { B with relation := fun n vs => (canon D B).relation n vs ∧
      (n ∈ layerNames D.T → ∃ ss, D.E.predicates n = some ss ∧ VE.TupleTyped B ss vs) }
def expandFill (U : UDoc) (B : VE.Structure.{u}) (F : FillTables U B) : VE.Structure.{u} :=
  forget (unsaidNames U) (canonTyped (fill U) (withFill U B F))

/-- Statuses (2.5) count every admissible filling, conflicting ones included. -/
def SettledAs (U : UDoc) (B : VE.Structure.{u}) (r : Regulated) (vs : List B.Carrier) (b : Bool) : Prop :=
  ∀ F : FillTables U B, BaseAdmissibleU U (withFill U B F) →
    ((outcomeBase (fill U) r.name).denote (withFill U B F) (tupleVal vs) ↔ b = true)
def UndecidedAt (U : UDoc) (B : VE.Structure.{u}) (r : Regulated) (vs : List B.Carrier) : Prop :=
  ∃ F₁ F₂ : FillTables U B,
    BaseAdmissibleU U (withFill U B F₁) ∧ BaseAdmissibleU U (withFill U B F₂) ∧
    (outcomeBase (fill U) r.name).denote (withFill U B F₁) (tupleVal vs) ∧
    ¬ (outcomeBase (fill U) r.name).denote (withFill U B F₂) (tupleVal vs)
```

All `h` below are `WellFormedU U = true`; all `hr` are `r ∈ U.D.T.regulated`.

```lean
/-- The author-side limits of `WellFormedU` suffice: `fill` never produces a tree that W1's `validate` rejects (8). -/
theorem fill_wellFormed (U) (h) : WellFormed (fill U) = true
theorem fill_conservative (U) (h0 : U.unspec = []) : fill U = U.D ∧ fillPremises U = []

/-- No author rule's selection changes: `fill` adds parents only. -/
theorem fill_selects_author (U) (h) (N : Node) (hN : N ∈ U.D.T.nodes) (S : VE.Structure.{u}) (ρ : VE.Valuation S) :
    (selects (fill U).T (fuel (fill U).T) N).denote S ρ ↔ (selects U.D.T (fuel U.D.T) N).denote S ρ

/-- The synthetic rule selects exactly where the author rules are silent and the gap is filled "yes". -/
theorem fill_decides (U) (h) (p : String) (hp : p ∈ U.unspec) (S : VE.Structure.{u}) (ρ : VE.Valuation S) :
    (DecidesD (fill U).T S ρ p true ↔ DecidesD U.D.T S ρ p true ∨
        ((atom (unsaidName p) (sortsOf U.D p)).denote S ρ ∧
          ¬ DecidesD U.D.T S ρ p true ∧ ¬ DecidesD U.D.T S ρ p false)) ∧
    (DecidesD (fill U).T S ρ p false ↔ DecidesD U.D.T S ρ p false)

theorem fill_local_conflict (U) (h) (r) (hr) (S : VE.Structure.{u}) (ρ : VE.Valuation S) :
    ((pos (fill U).T r.name).denote S ρ ∧ (neg (fill U).T r.name).denote S ρ) ↔
      ((pos U.D.T r.name).denote S ρ ∧ (neg U.D.T r.name).denote S ρ)

/-- Faithfulness of the W1 layer on `T‴` to the direct semantics of 2.2 plus agreement with the filling. -/
theorem fill_intended (U) (h) (r) (hr) (S : VE.Structure.{u}) :
    IntendedAt (fill U).T r S ↔
      IntendedAt3 U r S ∧
      (r.name ∈ U.unspec → ∀ vs, VE.TupleTyped S r.sorts vs →
        Value3 U r (forget [r.name] S) vs = .unsaid →
          (S.relation r.name vs ↔ S.relation (unsaidName r.name) vs))

/-- Adequacy: the source expansions are exactly the filled W1 expansions with the unsaid tables forgotten. -/
theorem fill_expansions (U) (h) (B : VE.Structure.{u}) (hB : BaseAdmissible U.D B) (S : VE.Structure.{u}) :
    Expansion3 U B S ↔
      restrictAll U.D.T S = B ∧
      ∃ S' : VE.Structure.{u}, forget (unsaidNames U) S' = S ∧
        BaseAdmissibleU U (restrictAll (fill U).T S') ∧
        DocumentExpansion (fill U) (restrictAll (fill U).T S') S'

theorem canonical_fill_sat (U) (h) (B : VE.Structure.{u}) (hB : BaseAdmissible U.D B) :
    BaseAdmissibleU U (withFill U B (canonicalFill U B))
theorem fill_extends (U) (h) (B : VE.Structure.{u}) (hB : BaseAdmissible U.D B) (F : FillTables U B) :
    ∃ F' : FillTables U B, (∀ p, p ∉ (pairMembers U).map unsaidName → F' p = F p) ∧
      BaseAdmissibleU U (withFill U B F')

/-- W1's pointwise iff, instantiated: conflict-free under every admissible filling = unique filled expansion. -/
theorem conflictFreeU_iff (U) (h) :
    ConflictFreeU.{u} U ↔ ∀ B : VE.Structure.{u}, BaseAdmissibleU U B → Unique (DocumentExpansion (fill U) B)
/-- Consistency in every base situation (the text never contradicts itself, however it is filled). -/
theorem conflictFreeU_consistent (U) (h) (hc : ConflictFreeU.{u} U) (B : VE.Structure.{u})
    (hB : BaseAdmissible U.D B) : ∃ S, Expansion3 U B S

theorem settled_expansions (U) (h) (B) (hB : BaseAdmissible U.D B) (r) (hr) (vs : List B.Carrier)
    (typed : VE.TupleTyped B r.sorts vs) (b : Bool)
    (hs : SettledAs U B r vs b) (F : FillTables U B) (hF : BaseAdmissibleU U (withFill U B F))
    (hcf : ConflictFree (fill U) (withFill U B F)) :
    Expansion3 U B (expandFill U B F) ∧ ((expandFill U B F).relation r.name vs ↔ b = true)
/-- The headline reading of 2.2: in a CONFLICT-FREE document a SETTLED point has its value in every expansion.
    `B` is `restrictAll U.D.T S`, whose carrier is `S.Carrier` definitionally, so `vs` types in both; `typed` is
    needed because an admissible `S` holds no ill-typed tuple while an outcome formula may be true at one. -/
theorem settled_all_expansions (U) (h) (hc : ConflictFreeU.{u} U) (r) (hr) (S : VE.Structure.{u})
    (hS : Expansion3 U (restrictAll U.D.T S) S) (vs : List S.Carrier) (typed : VE.TupleTyped S r.sorts vs)
    (b : Bool) (hs : SettledAs U (restrictAll U.D.T S) r vs b) :
    S.relation r.name vs ↔ b = true
theorem undecided_expansions (U) (h) (hc : ConflictFreeU.{u} U) (B) (hB : BaseAdmissible U.D B) (r) (hr)
    (vs : List B.Carrier) (typed : VE.TupleTyped B r.sorts vs) (hu : UndecidedAt U B r vs) :
    ∃ F₁ F₂ : FillTables U B, Expansion3 U B (expandFill U B F₁) ∧ Expansion3 U B (expandFill U B F₂) ∧
      (expandFill U B F₁).relation r.name vs ∧ ¬ (expandFill U B F₂).relation r.name vs

/-- Switching a deny/allow completion to `unspecified` changes no expansion when no admissible filling of the
    switched document reaches it (5, 6.3): the hypothesis is `gaps: none` for `p` on `U.switch p`. -/
theorem unreached_switch (U) (h) (p : String) (hp : p ∈ regulatedNames U.D.T) (hnp : p ∉ U.unspec)
    (h' : WellFormedU (U.switch p) = true)
    (hnr : ∀ B : VE.Structure.{u}, BaseAdmissibleU (U.switch p) B → ∀ vs, VE.TupleTyped B (sortsOf U.D p) vs →
      ¬ (reachedF (U.switch p) p).denote B (tupleVal vs)) :
    ∀ B S : VE.Structure.{u}, BaseAdmissible U.D B → (Expansion3 U B S ↔ Expansion3 (U.switch p) B S)
  -- U.switch and reachedF are defined above; the form with hnr over U's fillings is false (6.3, 12 item 2)
```

Finite evidence. `FiniteFill U α` is a finite table per unsaid predicate, and `M.withFill F` is the finite model
extended by it. `fillValid U M F` evaluates `fillPremises U` on `M.withFill F`.

```lean
theorem table3_sound {α : Type u} [DecidableEq α] (U) (h) (M : VE.FiniteModel α) (valid : M.Valid (envAt U.D 0))
    (hb : backgroundValid U.D M = true) (F : FiniteFill U α) (hF : fillValid U M F = true) (r) (hr) (vs : List α)
    (typed : VE.TupleTyped M.asStructure r.sorts vs) (b : Bool) (ht : table3 U M r.name vs = some b) :
    (outcomeBase (fill U) r.name).eval (M.withFill F) (tupleVal vs) = b
theorem settled_of_table3 {α : Type u} [DecidableEq α] (U) (h) (M) (valid) (hb) (r) (hr) (vs) (typed) (b)
    (ht : table3 U M r.name vs = some b) : SettledAs U M.asStructure r vs b
theorem settled_of_enumeration {α : Type u} [DecidableEq α] (U) (h) (M) (valid) (hb) (r) (hr) (vs) (typed) (b)
    (he : enumerateSettled U M r.name vs = some b) : SettledAs U M.asStructure r vs b
  -- enumerateSettled: every assignment of the closed cone's unsaid atoms (coneAtoms, ≤ MAX_UNSAID_ATOMS; the
  -- other unsaid atoms unknown) under which no Fill_T formula is Kleene-false gives b, and at least one is left
theorem undecided_witness_sound {α : Type u} [DecidableEq α] (U) (h) (M : VE.FiniteModel α)
    (valid : M.Valid (envAt U.D 0)) (hb : backgroundValid U.D M = true) (F₁ F₂ : FiniteFill U α)
    (h₁ : fillValid U M F₁ = true) (h₂ : fillValid U M F₂ = true)
    (r) (hr) (vs : List α) (typed : VE.TupleTyped M.asStructure r.sorts vs)
    (v₁ : (outcomeBase (fill U) r.name).eval (M.withFill F₁) (tupleVal vs) = true)
    (v₂ : (outcomeBase (fill U) r.name).eval (M.withFill F₂) (tupleVal vs) = false) :
    UndecidedAt U M.asStructure r vs
/-- A filled finite witness (settled or latent) refutes ConflictFreeU; the pair companion is analogous. -/
theorem conflictU_witness_sound {α : Type u} [DecidableEq α] (U) (h) (r) (hr) (M : VE.FiniteModel α)
    (valid : M.Valid (envAt (fill U) 0)) (hb : backgroundValid (fill U) M = true)
    (hF : (fillPremises U).all (fun φ => φ.eval M []) = true) (vs : List α)
    (typed : VE.TupleTyped M.asStructure r.sorts vs) (hw : (conflict (fill U) r).eval M (tupleVal vs) = true) :
    ¬ ConflictFreeU.{u} U
theorem fillPremises_universal (U) (h) (hf : InFragment (fill U) = true) :
    ∀ φ ∈ fillPremises U, UniversalQF φ   -- preserved under substructures: conflict_smallModel extends
```

Route corollaries: statements only, each by rewriting with the named existing theorem.

```lean
theorem fill_soft_value (D : SoftDoc) (unspec : List String) (h : WellFormedU ⟨soften D, unspec⟩ = true)
    (r) (hr : r ∈ D.T.regulated) (S : VE.Structure.{u}) (vs : List S.Carrier) :
    Value3 ⟨soften D, unspec⟩ r S vs =
      value3 (DecidesSoftD D S (tupleVal vs) r.name true) (DecidesSoftD D S (tupleVal vs) r.name false)
        (completionOf ⟨soften D, unspec⟩ r)                                  -- by decidesD_soften
/-- The collapse of section 0 removed: an excepted sole default rule leaves an unspecified act unsaid. -/
theorem excepted_lifts (D : SoftDoc) (unspec) (h) (r) (hr : r.name ∈ unspec) (N : SoftNode)
    (hN : rulesOn D r.name = [N]) (hd : N.mode = .default) (S : VE.Structure.{u}) (vs : List S.Carrier)
    (hx : (exceptedF D N).denote S (tupleVal vs)) :
    Value3 ⟨soften D, unspec⟩ r S vs = .unsaid
  -- companion excepted_collapses_under_deny: same hypotheses with r ∉ unspec, r.allowByDefault = false give .no
theorem fill_rights_value (D : RightsDoc) (unspec) (h : WellFormedRights D = true) (r)
    (hr : r ∈ (correlate D).T.regulated) (S : VE.Structure.{u}) (vs : List S.Carrier) :
    Value3 ⟨soften (correlate D), unspec⟩ r S vs =
      value3 (DecidesR D S (tupleVal vs) r.name true) (DecidesR D S (tupleVal vs) r.name false)
        (completionOf ⟨soften (correlate D), unspec⟩ r)                     -- by correlate_faithful
theorem followableU_sound (A : AltDoc) (unspec) (h) (hc : ConflictFreeU.{u} ⟨inlineTree A, unspec⟩)
    (c : VE.Tableau.Certificate)
    (ok : VE.Tableau.checkCertificate (envAt (fill ⟨inlineTree A, unspec⟩) 0)
      (backgroundBaseAltU A unspec ++ A.Γ) (allFollowableU A unspec) c = true) :
    ∀ B : VE.Structure.{u}, BaseAdmissibleAltU A unspec B → Sat B A.Γ → (allFollowableU A unspec).denote B []
  -- …U: alt 4.6's formulas regenerated on the filled tree, with fillPremises in the background
```

**Wire.** `decode_conservative`: on raw JSON with no `unspecified` value and no `norm-defaults@0`, the new decoder
returns exactly the existing route decoder's result with `unspec = []`, and identical canonical environment bytes.
`normDefaults_wire_acceptance` and `normDefaults_wire_conflict_sound` follow norms 11.4's chain (decoder soundness,
exact regeneration, binding equality, leaf admission, checker soundness, document iff) on `fill U`, with
`fillPremises U` in the regenerated base background. They are instantiated for each route that enables the profile.

**Proof plan.** `fill_decides` and `fill_local_conflict` follow from "a subtree yields iff one of its rules selects"
(`yields_iff_some_selects`, a new W1-level lemma on `YieldsD`/`SelectsD`, by induction on fuel with the deepest
applying rule); `fill_selects_author` holds because every author node keeps its `children` and fuel only grows.
`fill_intended` is W1's `catalaValue` case split with `fill_decides`. `fill_expansions`: forward, take `S' := S`
with `unsaid_p := S.relation p`, where `Fill_T` holds by W1's `subst_sound` and the profile premise in `S`;
backward, forget the unsaid tables and apply `fill_intended`. `settled_all_expansions` is `fill_expansions`
forward: the filling read off `S` is admissible, `hc` makes it conflict-free, and `hs` gives its value.
`fill_wellFormed` walks W1's `check` and `semanticCheck` on `T‴`: each `F_p` adds one rule, one rule name, one guard
and one precedence level above the roots on `p`, and `WellFormedU` (i)–(v) bound exactly these. A `check` condition
the proof finds uncovered is added to `WellFormedU` and to 8's table with its own diagnostic, never replaced by a bare
`WellFormed (fill U)` hypothesis. `canonical_fill_sat` is pointwise: at a gap of `r`,
`O_r‴ = P_r` is false; at a gap of `m`, `O_m‴` is true. The conflict theorems are W1's, instantiated on `fill U`
with `BaseAdmissibleU`, as soft 6.4 instantiates them with `BaseAdmissible′`. `table3_sound` is by induction over
the DAG (Kleene monotonicity, the pair rule justified by `Fill_T` at gaps only). Every proof is audited with the
unchanged axiom allowlist.

## 8. Agreement, diagnostics and limits

**Python** (`ve/norm_defaults.py`) builds `fill`, `Fill_T`, `table3`, the filling search, the gap and
default-reached targets, the report and the migration audit. **Lean** regenerates and checks each of them and
certifies all the evidence. **Rust** never elaborates (norms 11.6): it receives the filled premise list untrusted, and
its models carry the `unsaid__` tables as ordinary base tables; the only Rust change is fixtures.

**Differentials** (`conformance/norm_defaults_differential.py`, run by `tests/test_norm_defaults_three_way.py`).
1,000 generated trees × completion assignments over {deny, allow, unspecified}, including a pair and guards that
mention lower regulated predicates in a drawn order (so other symbols land between the pair's members), at the rule's
own row, under ∃ and ∀, or at a constant (so one row of a symbol reads another row of a lower one), give
byte-identical `T‴` and `Fill_T` (and every other regenerated output) in Python and Lean. On 1,000 generated finite
situations (at least the 300 asked for; some have more unsaid atoms than `MAX_UNSAID_ATOMS`) every `table3` entry is
identical and every status is the one Lean's replay reports (an UNKNOWN past the budget is Lean's enumeration
declining too); Lean validates every UNDECIDED and latent witness. Rust's
evaluator agrees on every premise list in its fixture file (`conformance/norm_defaults_rust.json`). norms 10.8's
mutations, plus flipping a completion and dropping a `Fill_T` premise, are rejected by the bound hashes.

**Diagnostics** (shared text): `UnsupportedProfile: unspecified completion requires norm-defaults@0`;
`InvalidInput: reserved name <n>` (the `unsaid__` and `unsaid--` prefixes); `InvalidModel("norms", "<unsaid__p> is a
filling; supply it only with norm-defaults@0")`; `ResourceLimit: unsaid atoms`; `ResourceLimit: fill premise`;
`ResourceLimit: unspecified name length`; and the author-side limits below.
Report findings, never errors: `UngroundedDefault: <p>`; `LatentConflict: <rules> under <p>(<situation>)` (the
witness kind of a CONFLICT); `UNSETTLED(<alternatives>)` (a DILEMMA diagnosis).

**Limits.** W1's rule count, rule names, AST budget and precedence depth are checked in Lean `WellFormed` (`check`,
`Tree.lean:331`, `:335`, `:346`, `:357`), so they bind `T‴`, and under the profile the author limits shrink (Q2,
closed by the statement review). For each unspecified predicate `fill` adds one rule, one rule name `unsaid--<p'>`,
one guard and one precedence level above the roots on `p`, and one base predicate `unsaid__<p>`; it adds no regulated
predicate and no carve-out, so the 64-regulated-predicate and 8-carve-out caps are unaffected. The decoder checks the
author document against `WellFormedU`'s limits (7) after its W1 checks and before `fill` is built ("accepted means
elaborable", soft 5.3), in this order, each under its own diagnostic:

| Limit on the author document under the profile | Diagnostic |
|---|---|
| declared predicates + unspecified predicates ≤ 256: `E‴` crosses the Bridge in bound packages and supplied `unsaid__` tables (`Bridge.lean:89`) | `ResourceLimit: vocabulary size` |
| author rules + unspecified predicates ≤ 256 (`WellFormedU` (iii)) | `ResourceLimit: rules` |
| each unspecified predicate name at most 56 bytes, so `unsaid--<p'>` (`ruleName`) and `unsaid__<p>` (`Bridge.identifier`) stay within 64 (`WellFormedU` (i)) | `ResourceLimit: unspecified name length` |
| AST nodes of the author guards and carve-outs plus one `F_p` guard per unspecified predicate ≤ 10,000 (`WellFormedU` (v)) | `ResourceLimit: AST exceeds 10,000 nodes` |
| precedence height ≤ 15 for every author rule on an unspecified predicate (`WellFormedU` (iv)) | `ResourceLimit: precedence depth` |

The character condition in `WellFormedU` (i) and the distinctness condition (ii) hold for every name decoded from the
wire (`Surface.identifier`, `[a-z][a-z0-9_]*`, which `fillName` maps injectively into `ruleName`), so they have no wire
diagnostic; they exclude Lean-built documents only. `fill_wellFormed` proves the limits sufficient, so no diagnostic
ever names an `unsaid--` rule. `Fill_T` formulas count against `MAX_NODES`. `MAX_UNSAID_ATOMS` bounds enumeration and
`MAX_EVALUATIONS` bounds the witness search. Every overflow is `ResourceLimit` or an UNKNOWN naming the budget, never
a status.

## 9. Fixtures (hand-written expectations; Python and Lean; Rust where it evaluates)

- **u1: u0165.s07, audited shape.** Sort `entity`; constants `claude` and `sol`; `csam_generation_permitted(entity)`
  unspecified; rule `no-csam-generation`, sign −, guard `var 0 = claude`. Expected: CONFLICT-FREE (certificate);
  `claude` SETTLED no (rule); `sol` UNDECIDED (fillings `{}` and `{sol}`); `gaps: reachable`, rendered "an entity
  other than Claude"; the legend exactly as in 4.1's example. Variant allow: `sol` SETTLED yes "(by default)", plus
  `default reached` and `UngroundedDefault` (the audited failure, now a finding). Variant deny: `sol` SETTLED no,
  plus `UngroundedDefault`. In both variants the `environment_id` is the one computed by the unchanged decoder.
- **u2: u0156.s03.** `system_prompt_deception_permitted(claude_instance, user)` unspecified; reading set
  `force-u0156-s03` {strict, default}, default with `decided_by: unstated`. Where
  `soft__excepted__no_system_prompt_deception` is true, strict is SETTLED no and default UNDECIDED (a checked
  distinguishing situation); where it is false, both are SETTLED no. The conclusion that the instance is not
  permitted to deceive the user is proved under the strict choice and has a filled countermodel under the default
  choice (document.md SOME). Variant deny: both SETTLED no everywhere; the collapse is kept as a regression, with
  `default reached` at the excepted situation.
- **u3: u0165.s03.** `cyberweapon_creation_permitted(claude_instance)` unspecified; strict reading `hard: true`;
  default reading; the translator's narrowing to strict recorded. As u2 for both readings; dependent conclusions carry
  `readings:force-u0165-s03:strict`; `hard_never_weighed` is unaffected.
- **u4: agent-policy.** A new `environment.unspecified.json`, both predicates unspecified; the expected sets are
  copied from the frozen answer key and README and checked, not regenerated. `permitted` is UNDECIDED exactly on
  `forced_default_sensitive` = {a27, a36, a37, a38}; every other action's status equals its completed outcome in all
  four shipped environments; a10 is still CONFLICT (rules 3 and 14). a13's reporting breach stays settled (rules 25
  and 26 decide it); the 13 approved, unreported actions of README.md:151-152 (a01, a02, a04, a07, a15, a17, a19,
  a21, a23, a25, a29, a35, a42) become UNDECIDED breaches. Harness verdicts are unchanged (they never read the
  default), and the four shipped environments reproduce their current outputs byte for byte.
- **u5: pairs.** (a) `x_required` unspecified, `x_permitted` deny with no rules: `x_required` SETTLED no,
  CONFLICT-FREE (contrast W1 10.1(b)). (b) `x_permitted` unspecified plus `Every act must be done.`: `x_permitted`
  SETTLED yes. (c) Both unspecified, no rules: both UNDECIDED; the filling (yes, no) fails `Fill_T`. (d) W1 10.1(a)
  with deny: CONFLICT, unchanged.
- **u6: latent conflict.** `Every agent must X, if that agent may Y.` (on `x_required`) and `Every agent must not X.`
  (on `x_permitted`), with `y_permitted` unspecified: CONFLICT, witness kind `latent under y_permitted(a) = yes`, and
  the English of 4.2; `y_permitted(a)` UNDECIDED (not SETTLED no: the conflicting filling counts, 2.5). With
  `y_permitted` deny: CONFLICT-FREE, byte-identical to today.
- **u7: inherited.** `report_required` deny with 2.5's rule 1, `permitted` unspecified with no rules:
  `report_required` UNDECIDED at every action, with `inherits_from: [permitted]`; `table3` is unknown and a pair of
  witness fillings is given.
- **u8: soft (γ)** with `x_permitted` unspecified: CONFLICT-FREE (soft's deny variant is CONFLICT). X is SETTLED
  permitted where rule 12 selects and UNDECIDED where rule 12 is excepted. Every other soft fixture is byte-identical.
- **u9: rights (γ), third variant.** The limited arrest is UNDECIDED; `rightsOf`, `dutiesOf` and the
  `UnlicensedLimitation` findings are identical to the allow and deny variants.
- **u10: followability.** Chooser R; pull forbidden by a rule, push with no rule; `permitted` unspecified. DILEMMA,
  diagnosis `UNSETTLED(push)`, scenario text "no clear action is established: the text does not say whether R may
  push". Adding `Every action may be performed, if that action is push.` makes it FOLLOWABLE.
- **u11: risk agent-ops** with `permitted` unspecified. k9: three UNDECIDED alternatives, none clear. k10:
  `default_decided` empty, and its two alternatives UNDECIDED.
- **u12: Kleene incompleteness.** A guard `if that agent may Y, or it is not the case that that agent may Y`, with
  `y_permitted` unspecified: `table3` unknown, SETTLED by enumeration. With `MAX_UNSAID_ATOMS = 0`: UNKNOWN naming the
  budget, never UNDECIDED.
- **u13: English.** The three legend sentences render and parse with one derivation each; the legends of u5(a) and
  u5(b) render, and each `When nothing else in the text decides` sentence in them parses with one derivation; the pair
  sentence renders; the keyword-collision check for `When nothing`; carve-out, soft and status paraphrases exactly as
  in 4.2; norms 2.6 row 2's third reading; `F_p` in no rendering.
- **u14: identity and mutation.** Flipping a completion changes `environment_id`, and the stale certificate is
  rejected. `unsaid__x` as an author predicate is rejected under the profile and accepted without it. A supplied
  `unsaid__` table without the profile is `InvalidModel`. Dropping a `Fill_T` premise from a bound package is
  rejected.
- **u15: unreached switch.** A UDHR-style unconditional prohibition over its scope has `gaps: none` (a certificate);
  switching deny to unspecified leaves every status and conclusion identical.
- **u16: limits.** With `p` unspecified: an author rule on `p` at precedence height 16 gives `ResourceLimit:
  precedence depth`; `257 − |unspec|` author rules (256 with one unspecified predicate, which W1 alone accepts) give
  `ResourceLimit: rules`; a 57-byte `p` gives `ResourceLimit: unspecified name length`. At height 15,
  `256 − |unspec|` rules and a 56-byte `p` the document is accepted and `fill U` passes `WellFormed`. No diagnostic
  mentions `unsaid--`; `ResourceLimit` is never a status.
- **Z: conservativity.** The full existing suite, conformance reports and frozen hashes are unchanged.
- **Review regressions** (12; `conformance/norm_defaults_three_way.py`). **b1:** `x_permitted` unspecified with no
  rules, `a_permitted` deny with "may A if may X", `x_required` deny with "must X if c", `c(a)` true: `table3` gives
  `x_permitted(a)` yes and leaves `a_permitted(a)` unknown in Python and Lean, and enumeration settles it yes in both.
  **b1-rows:** `x_permitted` unspecified with no rules, `x_required` deny with "must X if c" and "must X if someone
  may X" (b1-rows-exists) or "must X if K may be done" (b1-rows-const, `K` naming a), acts a and b, `c` on one act:
  `table3` gives both members yes at that act and leaves the other act unknown in Python and Lean, whichever act `c`
  holds on; enumeration settles it yes in both (in b1-rows-const with `c(b)` it is UNDECIDED in both). **b2:** u12 over 13 acts (13 unsaid atoms, one in each point's cone): SETTLED yes by enumeration in both. **a1:**
  6.3's counterexample: `p_permitted` has `default reached: none` under deny and `gaps: reachable` when switched; the
  audit gives no certificate for it, and lists `x_required` moving from SETTLED no to UNDECIDED.

## 10. Open questions

1. **Latent conflicts:** closed by the statement review: CONFLICT, keeping W1's three statuses, with the witness kind
   naming the filling.
2. **Limits on `T‴`:** closed by the statement review: W1's limits are in Lean `WellFormed`, so the author limits
   shrink under the profile, each with its own diagnostic (8).
3. **Soft coherence over gaps:** built as recommended (statement review): pairs are classified with unsaid atoms
   universal (3.3), so no weighing point is silently discharged by a gap answered "no".
4. **Followability:** built as recommended (statement review): "every filling", as risk's "UNDECIDED and not clear";
   no "FOLLOWABLE IF …" verdict.
5. **Evidence completeness:** Kleene plus bounded enumeration may leave many points UNKNOWN over large domains (pilot
   measurement needed); a two-copy "fill independence" certificate is a possible upgrade at double the vocabulary.
6. **Reader tests:** thresholds, sample size, wording A or B (W8). Untested: whether "the text" reads naturally in an
   authored policy.
7. **Translation documents:** how is one detected mechanically? Is the grounding block in front matter (recommended)
   or the environment? Are authored environments exempt from `UngroundedDefault` (recommended)?
8. **Readings over completions:** {deny, unspecified} as readings would need per-reading environments, which are
   UNKNOWN today (document.md, definition readings). Until then, `unspecified` plus a note?
9. **Sequencing with risk:** does risk/integrate or this profile's repin land first, and who owns risk's decoder branch?
10. **Names:** `unspecified` (recommended; `open` collides with W2's `{"open": …}`). Should 4.1's pair sentence parse?
11. **Definitions above norms:** `violation` and `breach` inherit UNDECIDED; a count format ("1 settled, 13
    undecided" breaches) is not designed.
12. **Coverage:** should gaps affect the coverage percentage or `bytes_by_status`? Recommended: no; a separate residual
    line, with units staying CHECKED.

## 11. Statement review of plan draft 1: findings and changes

`manage-agents/debates/norm-defaults-spec/{astra,fable}.md`, 2026-09-29: FIX, CONVERGED after round 2 (Opus stood in
for Astra in both rounds, as `astra.md` records). Plan draft 1 had no spec file; both sides asked for it to be written
from the edited plan. Every change below is in plan draft 2 (its section 12 holds the same table) and in this
specification. Citations are round.item; a bare round number cites that round's agreed list or refinement.

| # | Finding (raised by) | Change |
|---|---|---|
| 1 | `fill_expansions` is false: its right side never mentions `B`, so an expansion of another base situation satisfies it (Fable 1.1, Astra 1.2) | the right side begins `restrictAll U.D.T S = B ∧` (7) |
| 2 | The statuses count only conflict-free fillings. In u6 that reports "the agent may not Y", the invented prohibition of the plan's section 0, and with no conflict-free filling both SETTLED values hold vacuously (Fable 1.2, Astra 1.3) | `ConflictFree` conjuncts dropped from `SettledAs` and `UndecidedAt`; `conflictFreeEval` dropped (its definition, `enumerateSettled`, `c₁ c₂` of `undecided_witness_sound`); `undecided_expansions` gains `hc : ConflictFreeU U`; new headline `settled_all_expansions`; 2.2 reads "every expansion agrees" for CONFLICT-FREE documents only; 2.5's table, note and UNDECIDED validation; 3.1; u6 gains `y_permitted(a)` UNDECIDED |
| 3 | `table3`'s pair rule closes a decided pair clash, so `table3_sound` fails there (Fable 1.2, Astra 1.6) | the rule fires only where the side it sets is a gap; a decided clash is a CONFLICT (2.5, proof plan) |
| 4 | `fill_wellFormed` is false at W1's limits, which Lean `WellFormed` checks (Tree.lean:331, :335, :346, :357), so Q2 is answered: author limits shrink (Fable 1.3 and 2.1, Astra 1.4 and 2) | `WellFormedU` (i) `ruleName (fillName p)` (Astra 2: `\|p\| ≤ 56` alone misses the characters), (iii) rules, (iv) height ≤ 15, (v) AST budget with `F_p` guards; `fill_wellFormed` proved from them; the decoder's named diagnostics and the vocabulary cap for `E‴` at the Bridge (8); Q2 closed; u16 |
| 5 | The legend "When no rule decides, the text does not say whether …" is false for pair members: in u5(a, b) no rule decides, yet the text settles the point (Fable 1.4, Astra 1.5; wording Fable 2.2) | keyword `When nothing else in the text decides, ` for every role, with its one reading (4.1, D7); keyword-collision check for `When nothing`; u13 renders and parses u5(a, b) |
| 6 | `U.switch`, `regulatedNames` and `reachedF` are used but not defined; `reachedF` cannot reuse `gapF`, which is ⊥ off `unspec` (Astra 1.6 and 2, Fable 2) | `UDoc.switch` and `reachedF` defined (7); `regulatedNames` cited from `Norms/Tree.lean:120` |
| 7 | u12 names `permitted_y`; u1's deny variant has no "today's `environment_id`" (Fable 1.5) | `y_permitted`; "computed by the unchanged decoder" |
| 8 | Q1, Q3 and Q4 accepted as recommended; "everything else is built as planned" (Fable 1, Astra 1 and 2) | Q1 closed (3.1); Q3 and Q4 built as recommended (10) |
| 9 | Found while writing (i)–(v), under the converged rule "a `check` limit the proof finds uncovered is added to the list": two unspecified names differing only in `_` and `-` give one `unsaid--` name in a Lean-built document, which `check` rejects as a duplicate rule | `WellFormedU` (ii), `unspec.map fillName` duplicate-free; wire names never trigger it (8) |
| 10 | Found while writing row 2's headline in Lean: as sketched (`vs` over `B`, conclusion over any `S`), `S.relation r.name vs` does not type, and without typedness it is false (an outcome formula may be true at an ill-typed tuple, which no admissible `S` holds) | `settled_all_expansions` takes `B := restrictAll U.D.T S` (the same carrier, definitionally) and `typed : VE.TupleTyped S r.sorts vs`; its content is unchanged |

**Where the two round-2 texts crossed.** On the limits, each side conceded to the other's round-1 form: Fable proposed
the bare conjunct `WellFormed (fill U) = true` in `WellFormedU` plus named checks in the decoder, and Astra proposed
the named conditions in `WellFormedU` with `fill_wellFormed` proved from them. This specification takes the second,
since it meets both sides' stated requirements: a missed limit cannot pass unnoticed (the proof fails, and the limit
joins the list), each limit has its own author-facing diagnostic, and it is what makes u16's "no diagnostic mentions
`unsaid--`" a consequence rather than a hope. On the legend, Astra accepted Fable's round-1 wording ("When neither a
rule nor the sentence above decides", with the pair sentence first) while Fable replaced it in round 2, because "the
sentence above" depends on rendering order and "a rule above" can attach wrongly. This specification takes Fable's
round-2 keyword, which does not refer to position, so the rendering order is unchanged.

**What the statement pass checks.** Only the changes above: section 7's changed definitions and statements
(`UDoc.switch`, `WellFormedU`, `reachedF`, `SettledAs`, `UndecidedAt`, `fill_wellFormed`, `fill_expansions`,
`settled_all_expansions`, `undecided_expansions`, `undecided_witness_sound` and the `enumerateSettled` comment), 2.5's
`table3` pair rule, 4.1's legend and its one reading, 8's limits and diagnostics, and fixtures u1, u5, u6, u12, u13
and u16. If it is clean, the build starts; everything else in sections 2 to 9 is built as specified.

## 12. Statement changes found by the Lean build and the integration review

The Lean build (`lean/NORMDEFAULTS.md`, "Findings") showed four section-7 statements false as written; the DRI accepted
each change, and the integration review (2026-10-01, `manage-agents/norm-defaults-review-astra.final.md`,
`manage-agents/reviews/norm-defaults-review-fable.md`) found that this specification and the Python audit still
stated or implemented the false forms, and that Python and Lean computed `table3` and enumeration differently. Section
7 now shows the statements as proved.

| # | Finding | Change |
|---|---|---|
| 1 | `expandFill` with `canon` need not be admissible: `canon` holds on ill-typed tuples wherever a substituted outcome is true there; with typed tuples only, `settled_expansions` and `undecided_expansions` still fail at an ill-typed `vs` | `canonTyped`; `expandFill` uses it; both theorems take `typed : VE.TupleTyped B r.sorts vs`, as `settled_all_expansions` does (11, item 10) |
| 2 | `unreached_switch` with `hnr` over `U`'s fillings is false (6.3's counterexample) | `hnr` over the admissible fillings of `U.switch p`, reading `reachedF (U.switch p) p`; 5 and 6.3 say the certificate is `gaps: none` on the switched document, and the migration audit proves it there (`audit_completions`: `switched_gaps`, `certificate`, `switched_witness`) |
| 3 | `fill_rights_value` needs `WellFormedRights D` (what `correlate_faithful` needs); `WellFormedU` does not imply it, and the conclusion never needs `WellFormedU` | `h : WellFormedRights D = true` in place of `WellFormedU` |
| 4 | `table3` (review B1): Python closed the earlier member of a pair on demand, before the symbols placed in between read it; Lean's `closeRule` closes it only when the later member is placed | Python follows Lean step for step (2.5); every fixture point and every differential point compares the two tables |
| 5 | Enumeration (review B2): Lean enumerated every unsaid atom of the situation, Python the closed cone, so a wide situation with a small cone was SETTLED in Python and UNKNOWN in Lean | Lean enumerates the closed cone (`coneAtoms`), as 2.5 always said; `settled_of_enumeration`'s statement is unchanged and holds for any atom list (2.5 gives the argument) |
| 6 | Spec 8's differentials were not built (review) | built, as 8 now describes |
| 7 | `table3` (loop recheck of B1): Python entered a symbol row by row, so a close of the earlier pair member made at one row was read by a later row of the same symbol through ∃ or a constant ("must X if c" and "must X if someone may X", acts a and b, `c(a)`): SETTLED in Python, unknown in Lean, and Python's table depended on row order. The differential's guards were all at the rule's own row, so it could not see this | every row of a symbol, and every close it makes, reads the table before the symbol (2.5), as `tabK` does; fixtures b1-rows-exists and b1-rows-const (Python, three-way, Rust corpus, `Examples.lean` `uRows`); 8's differentials draw ∃, ∀ and constant guards |
