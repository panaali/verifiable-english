# The `unspecified` completion in VE: plan (`norm-defaults@0`)

> Status: planning draft 1 (2026-09-29). Design only: nothing is implemented, and every theorem and fixture below
> is an implementation obligation, not a claim. This is the planner's input to the Astra + Fable convergence that
> ARCH-ROADMAP P1 "unspecified default" (DRI 2026-09-29) schedules for after rights merges. Rights merged to main
> at `a1bf3a60`. A statement review of the resulting spec gates the Lean and Python work (PLAN-EXPAND2 rule 10).
> Inputs: [norms.md](norms.md) (W1, cited `norms n`), [soft-norms.md](soft-norms.md) (`soft n`),
> [rights.md](rights.md) (`rights n`), [alternatives.md](alternatives.md) (`alt n`), [document.md](document.md) (W2),
> `risk.md` and `risk-PLAN.md` on branch `design/risk` (`risk n`, `risk-PLAN n`), [VISION.md](../../VISION.md),
> `lean/VE/{Norms,SoftNorms,Rights,Alternatives}` and the pilot records cited in section 0. Nothing here changes a
> frozen contract, an existing profile's hash, a W1/soft/rights/alternatives theorem statement or a checker function.

## 0. Problem and evidence

norms 3.1 makes a regulated predicate's `default` mandatory and allows only `deny | allow`. norms 4.3 then completes
every case that no rule decides with that value. When the source says nothing about those cases, the translator
must still pick one, and the checker reports the pick as the text's content. Four independent records show this.

| Record | What was forced | Consequence |
|---|---|---|
| Constitution u0165.s07, "Generate child sexual abuse material (CSAM)." under "Claude should never:" (run-20260929T0600Z) | `csam_generation_permitted(entity)`, `default: allow`; one rule `¬p` with guard `entity = claude` | `pilots/claude-constitution/run-20260929T0600Z/AUDIT.md:11`: "Under the implemented norm completion, permission therefore holds for every entity unequal to Claude. The source supplies no such permission". The repair (AUDIT-REPAIR.md:9-20) narrowed the sort to `claude_instance` and flipped the default to `deny`, moving the rule's scope into the sort |
| Constitution u0156.s03 ("Claude shouldn't actively deceive the user about the existence of a system prompt or its content.") and u0165.s03 (cyberweapons), run-20260929T1800Z | reading set {strict, default}; completion `deny` | `run-20260929T1800Z/AUDIT.md:16`: "an excepted case still comes out "not permitted". That makes the defeasible reading identical to the strict one". AUDIT.md:22: "first an invented permission, now an invented prohibition". The translator disclosed it beforehand (FEATURE-REVIEW.md:79-82, F1); `metrics.json:599-727` shows all 15 predicates set to `deny`, each over the `claude_instance` workaround sort |
| agent-policy (`usecases/agent-policy`) | `permitted(action)`, `report_required(action)`: "not stated by the policy; VE forces one" (PLAN.md:111-112) | four environments ship, one per default combination (PLAN.md:116-129). Actions a27, a36, a37 and a38 are NOT-COVERED, and "VE's completed outcome ... is whatever default the environment was given" (README.md:195-199; `answer-key.json:477` `forced_default_sensitive`). For reporting, 13 actions are breaches or not depending only on the default (README.md:149-152) |
| risk (`design/risk`) | agent-ops policy "By default, an action may be performed." | risk-PLAN.md:1086-1089: it "silently permits every alternative no rule addresses ... Once it lands, `unspecified` makes them UNDECIDED and not clear". The interim report line is `default_decided` (risk.md:849-851, 985) |

Two more records. The UDHR pilot moved conditions into sort descriptions because "a conditional prohibition cannot
leave everyone else unspecified" (`pilots/udhr/run-20260929T1800Z/SUMMARY.md:5`); units u052 and u112 were judged
unfaithful for exactly that (AUDIT.md:14-24). The specs force it too. norms 9.1 declares "By default, a state may make
a law" because "the amendment restricts, it does not license", so it says the amendment licenses what it merely does
not restrict. soft 2.4 (:166) records `comply_permitted` allow-by-default as "a recorded choice", needed only because
soft 6.6 makes a default obligation against a deny completion a CONFLICT.

The common cause: a completion is content. Stance: a third completion, `unspecified`, says "the text is silent
here", and the checker reports silence as **UNDECIDED** instead of a value. Nothing is silently allowed or forbidden;
the translator is never forced to invent a default.

## 1. Decisions

| # | Decision | Where |
|---|---|---|
| D1 | New value `"default": "unspecified"` under a new profile `norm-defaults@0`; the field stays mandatory | 2.1 |
| D2 | Meaning: where no rule decides, the predicate is unconstrained, except where "whatever must be done may be done" forces it | 2.2, 2.4 |
| D3 | Elaboration by `fill`: one fresh base predicate `unsaid__p` and one synthetic lowest-priority rule per unspecified `p`; the result is an ordinary W1 tree, so W1 is reused unchanged; `fill` runs last on every route | 2.3 |
| D4 | Pair premises restricted to gaps (`Fill_T`) enter base admissibility, as soft's `Soft_T` does | 2.4 |
| D5 | Per-point status: SETTLED yes/no, UNDECIDED (two checked fillings) or UNKNOWN; undecidedness propagates upward through guards | 2.5 |
| D6 | CONFLICT-FREE means conflict-free under every admissible filling; a contradiction that needs a particular filling is a CONFLICT with a *latent* witness | 3.1 |
| D7 | Legend: "When no rule decides, the text does not say whether a <noun> may <act>." | 4 |
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
base situation. With gaps it has one per admissible way of filling the silences, and "the text says `p(ā)`" means
that every expansion agrees. Only the profile premise constrains a gap (2.4).

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
(limits, 8.3).

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
SETTLED yes   every admissible filling (B ⊨ Fill_T, conflict-free at B) gives O‴_p°(ā) true    "the text says so"
SETTLED no    every admissible filling gives false
UNDECIDED     two admissible fillings give different values                                    "the text does not say"
UNKNOWN       neither shown within budget (budget named); never promoted to either of the others
```

UNDECIDED is not confined to unspecified predicates. Take `Rule 1. Every agent must report each action, if that
agent may perform that action.`, with `report_required` deny-by-default and `permitted` unspecified with no rule.
Then `report_required` is UNDECIDED wherever `permitted` is: "The text does not say whether the agent must report
a36: rule 1 decides only if the agent may perform a36, and the text does not say whether it may." This is
propagation, not invention. Its static footprint (every regulated predicate whose guard cone mentions an unspecified
one) is reported per predicate as `inherits_from`.

Evidence (the search is untrusted, and every piece of evidence is checked):

- **`table3`** computes outcomes on the finite base situation in DAG order, with every unsaid atom unknown, Kleene
  connectives and finite quantifiers; where a pair closes it applies the profile rule (`m` := yes where `r` is yes;
  `r` := no where `m` is no). A definite entry is SETTLED (`table3_sound`). Kleene is incomplete (`u ∨ ¬u` is
  unknown), so an unknown entry is not yet UNDECIDED.
- **Exhaustive check.** For an unknown entry, enumerate the admissible fillings of the unsaid atoms in `ā`'s cone,
  up to `MAX_UNSAID_ATOMS` (proposed 12, so at most 4,096 fillings); agreement is SETTLED
  (`settled_of_enumeration`).
- **UNDECIDED** needs two finite fillings, each validated (`Fill_T` true and every conflict target false on the
  situation), with opposite values at `ā` (`undecided_witness_sound`). The search starts from the canonical filling
  and flips atoms in the cone.
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
on an invented "Y is forbidden". Whether latent conflicts need their own status word is Q1.

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

**Grounded completions stay.** Cedar's `permitted(request)` stays deny: Cedar's documented semantics is deny unless
a policy permits, a citation the adapter records. Gatekeeper's `admitted` stays allow for the same reason.
Candidates for `unspecified`, which this plan does not change: norms 9.1's "By default, a state may make a law", and
soft 2.4's `comply_permitted`, no longer forced by 6.6.

## 4. English

### 4.1 Legend sentences

| Role | deny | allow | unspecified (new) |
|---|---|---|---|
| permission | `By default, a <noun> must not <act>.` | `By default, a <noun> may <act>.` | `When no rule decides, the text does not say whether a <noun> may <act>.` |
| obligation | `By default, a <noun> need not <act>.` | `By default, a <noun> must <act>.` | `When no rule decides, the text does not say whether a <noun> must <act>.` |
| plain | `By default, it is not the case that <verbalisation>.` | `By default, <verbalisation>.` | `When no rule decides, the text does not say whether <verbalisation>.` |

Example (u0165.s07): "When no rule decides, the text does not say whether an entity may generate child sexual abuse
material." **One reading:** "when no rule decides" means when no rule on this act selects, and "the text does not
say whether" means that neither answer follows. It never means "may", and never "must not". **Registration:** one
surface record, `norm-unspecified`, with keyword `When no rule decides, ` under `norm-defaults@0`, rendered by
`ve/norm_english.py:default_sentence` beside today's `By default, ` sentence. No
registered keyword begins with `When` today (a grep of `ve/surface` on 2026-09-29), and the registry's
duplicate-keyword refusal re-checks it. It joins the mixed English harness and `tests/test_english_unambiguity.py`.
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
  and no citation is `UngroundedDefault: <p>`. An unreached one is harmless and not flagged: switching it is proved
  meaning-preserving (`unreached_switch`).
- **Authoring.** The IDE asks, showing the three legend sentences with a situation no rule covers, with no option
  preselected; it never fills in the value.
- **Pilots.** The translator rule "NO INVENTED PERMISSIONS" (`manage-agents/ve-run-log.md:874`) generalises to "no
  invented completions", and pilot audits count `UngroundedDefault`.

Evidence: each record in section 0 shows a workaround needed only for want of a third value, namely the
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
   that would change if switched (a re-run under `unspecified`). For an unreached one it gives the certificate that
   switching preserves meaning; UDHR SUMMARY.md:8's "completion is never used (checked under both completions)"
   becomes one such certificate. It never rewrites anything automatically.
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
`restrictAll`, `backgroundValid`, `canon`, `DecidesSoftD`, `DecidesR`, `inlineTree`) are those in `lean/VE` today.

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

/-- `WellFormed U.D`; `unspec` duplicate-free, ⊆ regulated names, placeholder `false`; reserved prefixes unused. -/
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
def expandFill (U : UDoc) (B : VE.Structure.{u}) (F : FillTables U B) : VE.Structure.{u} :=
  forget (unsaidNames U) (canon (fill U) (withFill U B F))

def SettledAs (U : UDoc) (B : VE.Structure.{u}) (r : Regulated) (vs : List B.Carrier) (b : Bool) : Prop :=
  ∀ F : FillTables U B, BaseAdmissibleU U (withFill U B F) → ConflictFree (fill U) (withFill U B F) →
    ((outcomeBase (fill U) r.name).denote (withFill U B F) (tupleVal vs) ↔ b = true)
def UndecidedAt (U : UDoc) (B : VE.Structure.{u}) (r : Regulated) (vs : List B.Carrier) : Prop :=
  ∃ F₁ F₂ : FillTables U B,
    BaseAdmissibleU U (withFill U B F₁) ∧ ConflictFree (fill U) (withFill U B F₁) ∧
    BaseAdmissibleU U (withFill U B F₂) ∧ ConflictFree (fill U) (withFill U B F₂) ∧
    (outcomeBase (fill U) r.name).denote (withFill U B F₁) (tupleVal vs) ∧
    ¬ (outcomeBase (fill U) r.name).denote (withFill U B F₂) (tupleVal vs)
```

All `h` below are `WellFormedU U = true`; all `hr` are `r ∈ U.D.T.regulated`.

```lean
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

theorem settled_expansions (U) (h) (B) (hB : BaseAdmissible U.D B) (r) (hr) (vs : List B.Carrier) (b : Bool)
    (hs : SettledAs U B r vs b) (F : FillTables U B) (hF : BaseAdmissibleU U (withFill U B F))
    (hcf : ConflictFree (fill U) (withFill U B F)) :
    Expansion3 U B (expandFill U B F) ∧ ((expandFill U B F).relation r.name vs ↔ b = true)
theorem undecided_expansions (U) (h) (B) (hB : BaseAdmissible U.D B) (r) (hr) (vs : List B.Carrier)
    (hu : UndecidedAt U B r vs) :
    ∃ F₁ F₂ : FillTables U B, Expansion3 U B (expandFill U B F₁) ∧ Expansion3 U B (expandFill U B F₂) ∧
      (expandFill U B F₁).relation r.name vs ∧ ¬ (expandFill U B F₂).relation r.name vs

/-- Switching a never-reached deny/allow completion to `unspecified` changes no expansion (5, 6.3). -/
theorem unreached_switch (U) (h) (p : String) (hp : p ∈ regulatedNames U.D.T) (hnp : p ∉ U.unspec)
    (h' : WellFormedU (U.switch p) = true)
    (hnr : ∀ B : VE.Structure.{u}, BaseAdmissibleU U B → ∀ vs, VE.TupleTyped B (sortsOf U.D p) vs →
      ¬ (reachedF U p).denote B (tupleVal vs)) :
    ∀ B S : VE.Structure.{u}, BaseAdmissible U.D B → (Expansion3 U B S ↔ Expansion3 (U.switch p) B S)
  -- U.switch p: placeholder false and p added to unspec; reachedF U p: gapF's formula for a deny/allow p
```

Finite evidence. `FiniteFill U α` is a finite table per unsaid predicate, and `M.withFill F` is the finite model
extended by it. `fillValid U M F` evaluates `fillPremises U` on `M.withFill F`. `conflictFreeEval D M` evaluates every
conflict and pair target at every typed tuple.

```lean
theorem table3_sound {α : Type u} [DecidableEq α] (U) (h) (M : VE.FiniteModel α) (valid : M.Valid (envAt U.D 0))
    (hb : backgroundValid U.D M = true) (F : FiniteFill U α) (hF : fillValid U M F = true) (r) (hr) (vs : List α)
    (typed : VE.TupleTyped M.asStructure r.sorts vs) (b : Bool) (ht : table3 U M r.name vs = some b) :
    (outcomeBase (fill U) r.name).eval (M.withFill F) (tupleVal vs) = b
theorem settled_of_table3 {α : Type u} [DecidableEq α] (U) (h) (M) (valid) (hb) (r) (hr) (vs) (typed) (b)
    (ht : table3 U M r.name vs = some b) : SettledAs U M.asStructure r vs b
theorem settled_of_enumeration {α : Type u} [DecidableEq α] (U) (h) (M) (valid) (hb) (r) (hr) (vs) (typed) (b)
    (he : enumerateSettled U M r.name vs = some b) : SettledAs U M.asStructure r vs b
  -- enumerateSettled: every filling of the cone's unsaid atoms (≤ MAX_UNSAID_ATOMS) that passes fillValid and
  -- conflictFreeEval gives b, and at least one does
theorem undecided_witness_sound {α : Type u} [DecidableEq α] (U) (h) (M : VE.FiniteModel α)
    (valid : M.Valid (envAt U.D 0)) (hb : backgroundValid U.D M = true) (F₁ F₂ : FiniteFill U α)
    (h₁ : fillValid U M F₁ = true) (h₂ : fillValid U M F₂ = true)
    (c₁ : conflictFreeEval (fill U) (M.withFill F₁) = true) (c₂ : conflictFreeEval (fill U) (M.withFill F₂) = true)
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
theorem fill_rights_value (D : RightsDoc) (unspec) (h) (r) (hr) (S : VE.Structure.{u}) (vs : List S.Carrier) :
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
backward, forget the unsaid tables and apply `fill_intended`. `canonical_fill_sat` is pointwise: at a gap of `r`,
`O_r‴ = P_r` is false; at a gap of `m`, `O_m‴` is true. The conflict theorems are W1's, instantiated on `fill U`
with `BaseAdmissibleU`, as soft 6.4 instantiates them with `BaseAdmissible′`. `table3_sound` is by induction over
the DAG (Kleene monotonicity, the pair rule justified by `Fill_T`). Every proof is audited with the unchanged axiom
allowlist.

## 8. Agreement, diagnostics and limits

**Python** (`ve/norm_defaults.py`) builds `fill`, `Fill_T`, `table3`, the filling search, the gap and
default-reached targets, the report and the migration audit. **Lean** regenerates and checks each of them and
certifies all the evidence. **Rust** never elaborates (norms 11.6): it receives the filled premise list untrusted, and
its models carry the `unsaid__` tables as ordinary base tables; the only Rust change is fixtures.

**Differentials.** 1,000 generated trees × completion assignments over {deny, allow, unspecified}, including pairs
and guards that mention lower regulated predicates, give byte-identical `T‴` and `Fill_T` in Python and Lean. 300
generated finite situations give identical `table3` results and statuses. Lean validates every UNDECIDED and latent
witness, and Rust's evaluator agrees on every supplied premise list. norms 10.8's mutations, plus flipping a
completion and dropping a `Fill_T` premise, are rejected by the bound hashes.

**Diagnostics** (shared text): `UnsupportedProfile: unspecified completion requires norm-defaults@0`;
`InvalidInput: reserved name <n>` (the `unsaid__` and `unsaid--` prefixes); `InvalidModel("norms", "<unsaid__p> is a
filling; supply it only with norm-defaults@0")`; `ResourceLimit: unsaid atoms`; `ResourceLimit: fill premise`.
Report findings, never errors: `UngroundedDefault: <p>`; `LatentConflict: <rules> under <p>(<situation>)` (the
witness kind of a CONFLICT); `UNSETTLED(<alternatives>)` (a DILEMMA diagnosis).

**Limits.** `fill` adds at most 64 nodes and one precedence level. W1's limits (256 rules, depth 16, 8 carve-outs;
norms 11.5) apply to the author document; whether `T‴` may exceed them depends on whether they are checked in Lean
`WellFormed` or only by decoders (Q2). Sizes are computed before anything is built ("accepted means elaborable",
soft 5.3), and `Fill_T` formulas count against `MAX_NODES`. `MAX_UNSAID_ATOMS` bounds enumeration and
`MAX_EVALUATIONS` bounds the witness search. Every overflow is `ResourceLimit` or an UNKNOWN naming the budget, never
a status.

## 9. Fixtures (hand-written expectations; Python and Lean; Rust where it evaluates)

- **u1: u0165.s07, audited shape.** Sort `entity`; constants `claude` and `sol`; `csam_generation_permitted(entity)`
  unspecified; rule `no-csam-generation`, sign −, guard `var 0 = claude`. Expected: CONFLICT-FREE (certificate);
  `claude` SETTLED no (rule); `sol` UNDECIDED (fillings `{}` and `{sol}`); `gaps: reachable`, rendered "an entity
  other than Claude"; the legend exactly as in 4.1's example. Variant allow: `sol` SETTLED yes "(by default)", plus
  `default reached` and `UngroundedDefault` (the audited failure, now a finding). Variant deny: `sol` SETTLED no,
  plus `UngroundedDefault`. Both variants keep today's `environment_id`.
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
  the English of 4.2. With `y_permitted` deny: CONFLICT-FREE, byte-identical to today.
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
  `permitted_y` unspecified: `table3` unknown, SETTLED by enumeration. With `MAX_UNSAID_ATOMS = 0`: UNKNOWN naming the
  budget, never UNDECIDED.
- **u13: English.** The three legend sentences render and parse with one derivation each; the pair sentence renders;
  the keyword-collision check; carve-out, soft and status paraphrases exactly as in 4.2; norms 2.6 row 2's third
  reading; `F_p` in no rendering.
- **u14: identity and mutation.** Flipping a completion changes `environment_id`, and the stale certificate is
  rejected. `unsaid__x` as an author predicate is rejected under the profile and accepted without it. A supplied
  `unsaid__` table without the profile is `InvalidModel`. Dropping a `Fill_T` premise from a bound package is
  rejected.
- **u15: unreached switch.** A UDHR-style unconditional prohibition over its scope has `gaps: none` (a certificate);
  switching deny to unspecified leaves every status and conclusion identical.
- **u16: limits.** Author depth 16 on an unspecified predicate behaves as Q2 decides; `ResourceLimit` is never a
  status.
- **Z: conservativity.** The full existing suite, conformance reports and frozen hashes are unchanged.

## 10. Open questions

1. **Latent conflicts:** CONFLICT (recommended; keeps W1's three statuses, and the witness kind names the filling), or
   a separate status such as "CONFLICT-FREE where decided; latent conflict at …"?
2. **Limits on `T‴`:** are W1's rule-count and depth limits in Lean `WellFormed` (then author limits shrink by one
   level and 64 rules under the profile) or only in decoders (then synthetic nodes are exempt)? Needs a code check.
3. **Soft coherence over gaps:** may `Coh_T`, a premise, constrain unsaid tables? A weighing point disjoint only if a
   gap is answered "no" would then be silently discharged. Recommended: classify with unsaid atoms universal.
4. **Followability:** "every filling" (recommended, as risk's "UNDECIDED and not clear"), or also "FOLLOWABLE IF …"?
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

## 11. Work items, sequencing and review checklist

(1) Astra + Fable convergence on this plan, then the spec `norm-defaults.md` and its statement review before any code
(the ARCH-ROADMAP precondition, rights merged, holds). (2) Lean: the `NormDefaults` modules and theorems (7), the
profile branch in the norms, soft, rights and alternatives routes (risk after its merge), and assurance-manifest
repins. (3) Python: decoder, `fill`, `Fill_T`, `table3`, searches, report block, legend and paraphrases,
`completions` grounding validation, migration audit. (4) Rust: fixtures and `unsaid__` tables in models. (5) W8:
registration, the IDE question, the reader test (4.3). (6) Pilot re-runs under the profile: constitution (u0165.s07,
u0156.s03, u0165.s03), agent-policy, UDHR (u052, u112), risk agent-ops; audits check `UngroundedDefault = 0` and read
every `gaps: reachable` line.

Statement review asks: (a) is dropping the third clause (2.2) the meaning of "the text is silent"? (b) Is `T‴` exactly
2.2 (`fill_expansions`), and is running `fill` last sound (`fill_selects_author`)? (c) Is `Fill_T` the only constraint
on gaps (`canonical_fill_sat`, `fill_extends`)? (d) CONFLICT-FREE under every admissible filling, and latent
conflicts as CONFLICT (Q1)? (e) Is the status evidence sound (`table3_sound`, `settled_of_enumeration`,
`undecided_witness_sound`), with UNKNOWN never promoted? (f) `excepted_lifts`, rights (γ), followability (3.3)?
(g) Legend, paraphrases and reader protocol (4)? (h) Translation policy and `UngroundedDefault` (5)?
(i) Conservativity (`decode_conservative`, `fill_conservative`, `unreached_switch`, fixture Z)?
