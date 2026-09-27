# Soft norms and weighing in VE: plan (`soft-norms@0`)

> Status: planning draft 1 (2026-09-27), for statement review before any code or Lean (PLAN-EXPAND2 rule 10).
> Inputs: the constitution pilot W1 review (`run-20260927T0407Z/W1-REVIEW.md`, `metrics.json`: 154 of 258 unformalised
> units blocked on `norms`, 13 on `defaults`); the pinned constitution
> (`manage-agents/pilots/claude-constitution/source/claude-constitution.md`, cited by line as `:n`);
> [VISION.md](../../VISION.md); [norms.md](norms.md) (W1); [document.md](document.md) (W2).
> Nothing here changes a frozen contract, a `norms@0` hash or the checker.

## 0. Problem and stance

W1 expresses `must`, `must not`, `may`, `need not`, guards, carve-outs, same-predicate precedence and one completion
default per predicate; it rejects `should`, `generally`, "is more important than" and holistic weighing (norms.md 2,
2.6). The constitution is written almost entirely in the rejected register: "Claude should generally prioritize these
properties in the order in which they are listed ... the notion of prioritization is holistic rather than strict"
(:37); "Claude should generally comply with the system prompt's instructions if doing so is not unsafe, unethical, or
against Anthropic's guidelines" (:166); "Claude has a weak duty to proactively share information but a stronger duty
to not actively deceive people. The duty to proactively share information can be outweighed by other considerations,
such as ..." (:293); "Regardless of operator instructions, Claude should by default: ... Some of these defaults can be
altered by the user but not the operator" (:183-192). Only the hard constraints (:433-445) are strict, and the text
says so: they "act more like boundaries or filters on the space of acceptable actions" rather than being weighed.

Stance (VISION.md, "elaborate by default"): a soft norm is **a strict rule plus a named open exception**. "Should X"
means "X is required unless this rule's exception applies here", and whether it applies is an open term with a decider
(W2 schema). Weighing is never a consequence relation inside the checker (the research-track item of PLAN-EXPAND2 §7);
it is a set of named open procedures whose *structure* the checker certifies: which rules can collide, which
collisions the stated priorities resolve, which are left to a decider, and that hard constraints are never weighed.
Everything elaborates into `norms@0` over an extended vocabulary, so W1's proofs, conflict machinery and the Cedar and
Gatekeeper gates are inherited unchanged. "All things considered" is exactly what the checker does not compute: it
computes the conditional outcome given the deciders' findings and lists what those findings must satisfy.

## 1. Semantics sketch

A soft-norm document is a W1 tree `T` (norms.md 1) whose rules additionally carry:

```text
mode(N)      ∈ {strict, default}          strict = W1 rule as today; default = defeasible
rank(N)      ∈ Ranks ∪ {none}             a declared name: "safety", "honesty", "helpfulness", ...
alterable(N) ⊆ Parties                    who may turn the rule off by instruction ("operator", "user")
exception(N) = open term excepted_N(x̄)   mandatory for default rules; decider mandatory (rule or document level)
Ranks        = finite names + declared `outranks` (must be acyclic; incomparable = tie, ":347 in no particular order")
               + one flag: outranking is `strict` or `holistic` (:37)
```

**Elaboration `soften(T) = T′` over `E′ = E` + fresh base predicates** (each with its rule's argument sorts):

1. Default rule `N`: carve-outs `U_N ∪ {excepted_N(x̄)}`. Sufficient and necessary conditions the source states become
   the term's `sufficient`/`necessary` entries (:293: "hazardous to third parties", "operator does not want it shared",
   "not helpful enough to include").
2. Alterable rule `N`, party `π`: carve-out `off_N_π(x̄)`, a base fact recording an instruction (`off_N_user ∧
   ¬restricted_N_operator` for "users may turn off absent operator restriction", :416). Unlisted parties get no
   predicate, so their instructions provably cannot change the outcome.
3. Hard over soft: every strict rule on `p` takes precedence over every default rule on `p` (derived edges). A default
   rule may not be an exception of a strict rule (`SoftOverHard`): hard constraints "cannot be unlocked by any operator
   or user" (:443).
4. Rank resolution: for default rules `M, N` on `p` of opposite sign with `rank(M) outranks rank(N)`: derived edge
   `M over N`; under `holistic`, `M` gets the carve-out `selects′_N(x̄) ∧ outweighs_N_M(x̄)` (open term), so the higher
   rank decides unless the decider finds the lower one outweighs it in that situation, and `M` still decides wherever
   `N` is silent. Derived edges follow the acyclic rank order, so the precedence DAG stays a DAG; an author edge
   against the rank order is `RankAgainstPrecedence`.

`T′` is a well-formed `norms@0` tree; `applies`, `yields`, `selects`, completion, `elab_p` and every theorem of
norms.md 4 to 6 apply verbatim. A **direct semantics** `ValueSoft` is stated independently for the statement review:
in-force strict rules decide (two disagreeing = CONFLICT); otherwise in-force default rules (guard holds, no
carve-out, not excepted, not switched off, not dominated by an in-force higher-ranked opponent unless outweighed)
decide if they agree; none = the completion default; disagreement = a **weighing point**. Theorem `soften_faithful`:
`Norms.Value (soften T) p S v̄ = ValueSoft T p S v̄` on every structure over `E′`.

**Statuses.** W1's single verdict on `T′` would report CONFLICT for every pair of opposite default rules that can
co-apply (the base structure with both exceptions false is a witness). That is the intended reading, so the profile
answers three questions instead, with unchanged checker functions:

| Question | Method | Result |
|---|---|---|
| Do strict rules collide? | W1 conflict formulas on `T′` restricted to strict–strict pairs (and the obligation/permission pair formula over strict outcomes) | CONFLICT (witness situation) / CONFLICT-FREE (certificate) / UNKNOWN |
| Which default rules can collide? | per syntactic pair `(M, N)` on `p`, opposite sign, not rank-resolved: satisfiability of `selects′_M ∧ selects′_N` over base structures | DISJOINT (certificate) / WEIGHING POINT (witness + obligation `excepted_M ∨ excepted_N` there) / UNKNOWN |
| Are the priorities consistent? | `dependencyOrder` over rank names; author versus derived edges | acyclic / `DependencyCycle: <ranks>`; ties listed |

Weighing points are residual items (VISION.md 2), each with its resolution: `open` (a decider must except one of the
two), `rank: honesty over helpfulness (holistic)` (resolved by structure, `outweighs` term in the residual) or `strict`
(no residual). Obligations are reported, never added to Background: the checker does not invent decision criteria
(document.md); it states what the deciders' findings must satisfy for the rules to be jointly followable.

**Limit.** Collisions are same-predicate. "Help with the request" versus "refuse the request" are different acts;
their practical incompatibility is stage-3 material (actions, fulfilment). The four-property ordering therefore has
two encodings: ranks on rules over a shared act, or norms.md 9.2's reified `follow(situation, property)` over
`outranks(property, property)`, which no longer needs a reading set (section 4).

## 2. English wordings (one reading each; rejected as today when `soft-norms@0` is off)

| Wording | The one reading (the IDE's paraphrase) | Formal effect |
|---|---|---|
| `Rule n. Every <noun> should <act>[, if C][, unless U].` | In every situation of the kind, the act is required unless rule n's exception applies there; <decider> decides whether it applies. | default, obligation `+`; carve-out `excepted_n` |
| `... should not <act>` | ... the act is not permitted unless rule n's exception applies there. | default, permission `−` |
| `... generally may <act>` / `... generally need not <act>` | ... permitted / not required unless rule n's exception applies there. | default `+` permission / `−` obligation |
| `The exception to rule n is decided by <decider>.` | Names who decides whether rule n is excepted in a situation. | open-term decider |
| `Exceptions to rules in this document are decided by <decider>, unless a rule says otherwise.` | Document-level decider. | default decider |
| `Rule n is excepted when C.` / `... only when C.` | C is sufficient / necessary for rule n's exception. | `sufficient` / `necessary` |
| `Rule n serves <rank>.` | Rule n counts as a <rank> consideration where it collides with a rule of another rank. | `rank(n)` |
| `<Rank a> outranks <rank b>.` | Where a rule serving a and one serving b disagree, the a rule decides (subject to the flag below). | rank-order edge |
| `<Rank a> and <rank b> are not ranked.` | Neither outranks the other; a disagreement between them is a weighing point. | declared tie (checked) |
| `Outranking in this document is holistic; <decider> decides when a lower-ranked rule outweighs a higher-ranked one in a situation.` / `... is strict.` | Holistic: the higher rank decides unless the decider finds otherwise for that situation. Strict: it always decides. | flag; `outweighs_N_M` terms |
| `Rule n (operators may turn off).` / `(users may turn off)` / `(users may turn off, unless an operator restricts it)` / `(default; users may turn off)` | The rule holds unless the named party has turned it off for the situation; nobody else's instruction changes it. | carve-out `off_n_π`; authority certificate |

Input synonyms rendered canonically: `generally must` → `should`; `generally must not` → `should not`; `normally`,
`typically`, `as a rule` → `generally`. `By default,` remains the W1 completion legend, never a rule marker; the IDE
rewrites a sentence-initial "By default, Claude should ..." to a `should` rule or an alterable rule, showing both
paraphrases with a situation. `must` stays strict: writing `must` where the source says "should" is a translator's
narrowing and is recorded as one (VISION.md 3). The reader's checklist (norms.md 2.5) adds, per default rule, a
situation where it is excepted (naming the decider) and, if ranked, one where a higher rank overrides it.

Examples from the source (act phrases declared as in norms.md 2.4; subject sort `assistant`):

```text
:37   Safety outranks ethics. Ethics outranks guidelines. Guidelines outranks helpfulness.
      Outranking in this document is holistic; Anthropic's reviewers decide when a lower-ranked rule outweighs a
      higher-ranked one in a situation.                          (checked: acyclic; residual: outweighs terms)
:166  Rule 4. Every assistant should comply with each instruction of the operator, if it is not the case that
      complying with that instruction is unsafe, and it is not the case that complying with that instruction is
      unethical, and it is not the case that complying with that instruction is against Anthropic's guidelines.
      Rule 4 serves helpfulness.                 (open: unsafe, unethical, against-guidelines, excepted_4)
:293  Rule 12. Every assistant should share each piece of information that is helpful to the user.
      Rule 12 serves helpfulness. Rule 12 is excepted when that information is hazardous to a third party.
      Rule 12 is excepted when the operator does not want that information shared.
      Rule 13. Every assistant should not deceive each user. Rule 13 serves honesty. Honesty outranks helpfulness.
                                          ("weak duty" = stated sufficient exceptions plus the lower rank)
:185  Rule 20 (users may turn off). Every assistant must tell each user what that assistant cannot help with.
                                          (certified: no operator instruction changes rule 20)
:441  Rule 31. Every assistant must not generate child sexual abuse material.
                                          (strict; hard over soft; paraphrase: "no instruction by any party changes this")
```

## 3. What the checker certifies and what stays open

**Certified** (certificate or theorem, bound to `environment_id` and the soft document hash):

1. The strict core is conflict-free, or a witness situation is shown.
2. No situation exists in which a default rule decides against an in-force strict rule (`hard_over_soft`, a theorem
   about `soften`, not a search).
3. The complete list of default-rule pairs that can collide: each DISJOINT, a WEIGHING POINT with a situation in
   document terms, or UNKNOWN with the budget named; and whether the declared ranks resolve it.
4. The rank order is acyclic; declared ties are ties; no author precedence contradicts the ranks.
5. Override authority: exactly the named parties can switch a rule off; strict rules have no switch.
6. Everything W1 certifies already: faithful elaboration, well-formedness, DAGs, identity binding.

**Open, never certified:** the exception decisions (`excepted_N`); the holistic overrides (`outweighs_N_M`); weighing
procedures with their `factors` (:332-343 becomes the schema of `harm_outweighs_benefit(action, context)`: decider,
factors probability, counterfactual impact, severity, breadth, proximate cause, consent, responsibility,
vulnerability); open-textured predicates in guards ("serious uplift", "unsafe"); heuristics (:198-221; :240 "None of
the heuristics offered here are meant to be decisive": kind `explanation`, optionally pinned as `precedents`); the
"spirit of the document" clause (:47, `meta`); cross-act practical conflicts (stage 3); whether any rule is followed.

## 4. How coverage counts these units

Statuses stay CHECKED / LABELLED / OPEN / READINGS / UNFORMALISED; no new status.

- **A default rule is OPEN**, meaning `{"open": ["excepted_n", ...]}`: the logic is exact and applying the exception
  is a recorded decision, as for any open term (VISION.md 2). It is part of the checked spine; its exception enters the
  residual. A strict rule over declared vocabulary is CHECKED; one whose act carries an open predicate is OPEN, as today.
- **Residual gains lines** `default_exceptions` (distinct terms, also grouped by decider), `weighing_points` (with
  resolution), `holistic_overrides`, beside open terms, assumptions, bridge leaves and unresolved reading sets. A
  constitution will show on the order of a hundred default exceptions; that is the honest headline.
- **Ranking sentences are CHECKED** (a finite declared order, acyclicity proved); the holistic flag is OPEN. The :37
  unit stops being norms.md 9.2's two-reading set: the source itself says "holistic rather than strict", so it has one
  OPEN reading with the same certificate.
- **Open-term declaration prose** (:332-343; ":293 can be outweighed by ... such as") is a `definition` unit with
  `meaning: open`, as u0214 today: OPEN, bytes accounted to the term's schema.
- **Translation mode:** source "should" is a READINGS unit `{strict, default}` unless a cited source unit narrows it
  (":443 These represent absolute restrictions" narrows the :433 list to strict). "Generally X", "by default X (party
  may alter)" and "X outranks Y, holistically" each have one reading. `hedged(generally, norm)` stays accepted and
  LABELLED; the assistant offers the default-rule rewrite.
- **Split the units.** The W1 review's blocker was granularity: u0165 is seven bullets in 874 bytes and its "Claude
  should never:" header is u0164. Each bullet becomes a unit (the partition allows any byte boundaries); the header is
  LABELLED `meta`, noted as supplying the force to u0165a–g. Coverage is by bytes, so header bytes count LABELLED and
  bullet bytes CHECKED or OPEN, and nothing is discarded. Whole-unit fidelity stays the rule; capability evidence
  outside a faithful whole-unit translation stays outside counted coverage.

## 5. Work items

| # | Item | Owner, effort | Notes |
|---|---|---|---|
| 1 | `docs/spec/soft-norms.md`: `ValueSoft`, `soften`, statuses, wordings, diagnostics (`SoftOverHard`, `RankAgainstPrecedence`, `MissingExceptionDecider`, `UnknownRank`), acceptance tests; Astra + Fable statement review | spec, 2 days | review `ValueSoft` and the weighing-point obligation |
| 2 | Profile `soft-norms@0` requiring `norms@0`; fields `mode`, `rank`, `alterable`, `exception` on W2 `norm` content; rank declarations and the flag in the environment (identity-bound like `regulated`); no W5 dependency (ranks are declarations, `off_*` plain base predicates) | Python `ve/softnorms.py`, `ve/document.py`, `ve/profiles.py`, 4 days | all `norms@0` fixtures and hashes unchanged |
| 3 | Surface registrations (`should`, `generally`, `serves`, `outranks`, `are not ranked`, `is excepted when`, `is decided by`, header options), synonyms, profile-gated rejection; W7 harness fixtures; `tests/test_english_unambiguity.py` | `ve/surface/softnorms.py`, `ve/norm_english.py` | `Rule ` and `By default, ` reused, disambiguated on following tokens |
| 4 | Lean `lean/VE/SoftNorms/{Tree,Soften,Semantics,Status}.lean`: `SoftTree`, `soften`, `ValueSoft`; theorems `soften_wellFormed`, `soften_faithful`, `hard_over_soft`, `rank_acyclic` (via `VE.Route.dependencyOrder`), `weighing_points_complete` (every opposite-sign selection witness on `T′` is strict–strict or in an enumerated pair), `authority_sound`; wire path per norms.md 11.4: new executable `ve_soft_norms_route` regenerating `T′` from raw JSON and delegating strict-core and DISJOINT replay to unchanged W1 replay; `lean/SOFT-NORMS.md`; audit allowlist unchanged | Lean, 4 to 6 days | frozen `Norms/*`, `Route/*` untouched |
| 5 | Coverage: residual lines and grouping in `tools/coverage_dashboard.py` and `ve document coverage` | Python, 1 day | metrics schema addition only |
| 6 | W8: `add_default_rule`, `add_rank`, `set_exception`; paraphrases and extra example situations; translation rule for source "should"; fidelity gate before offering | `ve/assist/*` | exception and decider always named |
| 7 | Pilot re-run on the pinned constitution: re-split `norms` units; translate :37, :166, :181-192, :281-293, :325-343, :407-423, :433-445; report status and residual deltas against `run-20260927T0407Z`; blind fidelity audit of sampled paraphrases | pilot, 2 days | only measured numbers are claimed |

Sequencing: 1 → (2, 3, 4 in parallel) → 5 → 6 → 7. Item 4 does not wait on the W3/W5 composition gaps
([INTEGRATION-GAPS.md](../INTEGRATION-GAPS.md)): no soft construct needs a defined predicate or a data flag; a guard
that needs one inherits the existing `UnsupportedProfile` answer.

## 6. Risks

1. **OPEN read as "checked and true".** Mitigation: the residual is the headline; every default-rule paraphrase names
   its exception and decider; metrics separate `default_exceptions`.
2. **Residual size.** One exception per default rule makes the constitution's residual large. It is honest, but it must
   be shown grouped by decider and rank or the dashboard reads as failure.
3. **"Should" drift in translation.** Sources use "should" for strict rules too (:433). Collapsing to `should` weakens
   the source; to `must`, strengthens it. The reading-set rule of section 4 is mandatory and audited in item 7.
4. **False comfort.** "No weighing points" does not mean the rules are jointly followable in practice; cross-act
   incompatibility is invisible until stage 3. Status text must say "among rules on the same act".
5. **Naive reuse of the W1 verdict** on `T′` reports CONFLICT for every soft collision; section 1's three-question
   status is the contract, with a regression. Likewise the derived carve-out `selects′_N ∧ outweighs_N_M` is what keeps
   `M` deciding where `N` is silent (exceptions do not inherit guards, norms.md 2.3); `soften_faithful` and the
   norms.md 10.1 diamond and grandchild fixtures repeated on soft trees guard this.
6. **Zero-training English.** `should`/`must` are near-synonyms to many writers; `serves`/`outranks` are new keywords.
   Mitigation: the IDE never accepts a default rule without showing the excepted situation; W8 fidelity gate first.
7. **Reviewer objection: an always-available exception makes a rule vacuous.** It changes no strict rule, and a
   default rule's content is exactly "required unless excepted"; the certified obligations on the deciders are the
   non-vacuous part. The statement review settles this before Lean starts.

## Summary

Soft norms enter VE as strict rules with a named open exception, elaborated by `soften` into the existing `norms@0`
tree over an extended vocabulary, so W1's proofs and checks are inherited. `should`, `generally may`, rank sentences
(`X outranks Y`, holistic or strict), alterable-default headers and exception declarations each have one reading. The
checker certifies the strict core's conflict-freedom, that hard rules are never overridden by soft ones, the complete
list of default-rule collisions (each disjoint, rank-resolved or an open weighing point), acyclic priorities and
override authority. Exceptions, holistic overrides and weighing procedures with their factors stay open terms with
deciders. Default rules count as OPEN; the residual gains default-exception and weighing-point lines; translation keeps
`should` as a reading set unless the source narrows it; units split at bullet boundaries. Work: spec review, Python
profile and surface, Lean `SoftNorms` with `soften_faithful`, coverage lines, W8 tools, pilot re-run.
