# Rendering (`ve_fluent`, with legend, compact style)

Command:

```sh
UV_CACHE_DIR=/private/tmp/ve-uv-cache-uc uv run python -m ve render \
  --env usecases/claude-constitution-excerpt/environment.json \
  --view ve_fluent --with-legend --legend-style compact \
  usecases/claude-constitution-excerpt/claims.ve
```

Output:

```
Vocabulary: ve.vocabulary-legend@3; environment: 98dbed69e9ed29c573756d4658b1fae39223466f3cb525f994648b7a5d4622cb
Sorts:
  action (noun: "action"; declared: none) — "An action a Claude model might perform."
  claude_model (noun: "claude_model"; declared: none) — "A Claude model, as referred to by the constitution excerpt (e.g. 'all current Claude models', 'Claude')."
  guideline (noun: "guideline"; declared: none) — "One of Anthropic's specific guidelines that a Claude model might or might not be acting in accordance with."
  mechanism (noun: "mechanism"; declared: none) — "A human mechanism for overseeing the dispositions and actions of AI, as referred to by the 'broadly safe' value and the oversight discussion."
  overseer (noun: "overseer"; declared: none) — "A human or organization who might instruct, check, or be owed obedience by a Claude model, including Anthropic itself and appropriately sanctioned individuals."
  principal (noun: "principal"; declared: none) — "An operator or user that a Claude model interacts with (the excerpt's 'operators and users' merged into one sort)."
  property (noun: "property"; declared: none) — "One of the four core value-properties named in the excerpt's priority ordering: broadly safe, broadly ethical, compliant with Anthropic's guidelines, genuinely helpful."
  situation (noun: "situation"; declared: none) — "A case or interaction in which two or more of the four core value-properties might come into apparent conflict."
Constants:
  @anthropic : overseer — "Anthropic, named explicitly in 'not... blind obedience, including towards Anthropic'."
  @claude : claude_model — "The Claude model this excerpt's claims are about."
  @ethics : property — "The 'broadly ethical' core value."
  @guidelines : property — "The 'compliant with Anthropic's guidelines' core value."
  @helpfulness : property — "The 'genuinely helpful' core value."
  @safety : property — "The 'broadly safe' core value."
Predicates:
  appropriate(mechanism) — "{0} is appropriate" (strict fallback; declared: none) — "Recorded as an 'appropriate' human mechanism for overseeing the dispositions and actions of AI, in the sense used by the 'broadly safe' value."
  benefits(claude_model, principal) — "{0} benefits {1}" (strict fallback; declared: none) — "Recorded as the model benefiting this operator or user, in the sense used by 'genuinely helpful'. The intensifier 'genuinely' (sincere vs. superficial benefit) has no separate witness; see GAPS.md #2."
  bound_to_obey(claude_model, overseer) — "{0} bound_to_obey {1}" (strict fallback; declared: none) — "OPAQUE marker predicate. Recorded as the model being bound to unconditional ('blind') obedience toward this overseer. Hides the deontic modality of 'must obey' and the manner qualifier 'blind'; see GAPS.md #1."
  contends_for(situation, property) — "{0} contends_for {1}" (strict fallback; declared: none) — "Recorded as this property being one of the (at most two, in every model used here) properties tagged as apparently conflicting in this situation. A reification workaround for the fact that v0 has no ternary relation to say directly which two properties are the ones apparently conflicting in a given situation; see GAPS.md #1."
  current_claude_model(claude_model) — "{0} is current_claude_model" (strict fallback; declared: none) — "Recorded as one of 'all current Claude models' the excerpt's core-values paragraph addresses."
  follows(claude_model, guideline) — "{0} follows {1}" (strict fallback; declared: none) — "Recorded as the model acting in accordance with this guideline."
  honest(claude_model) — "{0} is honest" (strict fallback; declared: none) — "Recorded as honest, one conjunct of the excerpt's 'broadly ethical' value ('having good personal values, being honest, and avoiding...'). 'Having good personal values' itself has no witness anywhere in this vocabulary; see GAPS.md #2."
  inappropriately_harmful(action) — "{0} is inappropriately_harmful" (strict fallback; declared: none) — "OPAQUE marker predicate. Recorded as an action the excerpt would call 'inappropriately dangerous or harmful'. The judgement of what counts as 'inappropriate' is hidden inside this predicate; see GAPS.md #2."
  interacts(claude_model, principal) — "{0} interacts {1}" (strict fallback; declared: none) — "Recorded as the model interacting with this operator or user."
  ought_follow(situation, property) — "{0} ought_follow {1}" (strict fallback; declared: none) — "OPAQUE marker predicate. Recorded as the property the excerpt says Claude 'should generally' follow in this situation. Hides both the deontic force of 'should' and the defeasibility of 'generally'; see GAPS.md #1."
  ought_have_core_values(claude_model) — "{0} is ought_have_core_values" (strict fallback; declared: none) — "OPAQUE marker predicate. Recorded as a model of which the excerpt says 'we believe [it] should be' broadly safe, broadly ethical, compliant, and genuinely helpful. This predicate names, but does not analyse, the deontic force of 'should be' and the fact that it introduces four further properties (see GAPS.md #1 and coverage.md row 1)."
  outranks(property, property) — "{0} outranks {1}" (strict fallback; declared: none) — "Recorded as the first property immediately outranking (being listed directly above) the second property in the excerpt's stated priority order: broadly safe, broadly ethical, compliant with guidelines, genuinely helpful. Base edges only; use tc[outranks]/rtc[outranks] for the full order."
  performs(claude_model, action) — "{0} performs {1}" (strict fallback; declared: none) — "Recorded as the model performing this action."
  relevant(guideline) — "{0} is relevant" (strict fallback; declared: none) — "Recorded as 'relevant' to the model's present situation, in the sense used by 'compliant with Anthropic's guidelines: ... where they're relevant'."
  sanctioned_check(overseer) — "{0} is sanctioned_check" (strict fallback; declared: none) — "Recorded as an 'appropriately sanctioned' human acting as a check on AI systems, in the sense used by the corrigibility sentence."
  undermines(claude_model, mechanism) — "{0} undermines {1}" (strict fallback; declared: none) — "Recorded as the model undermining (acting so as to defeat or subvert) this oversight mechanism."
  undermines_check(claude_model, overseer) — "{0} undermines_check {1}" (strict fallback; declared: none) — "Recorded as the model undermining this overseer's role as an appropriately sanctioned human check on AI systems, in the sense used by the corrigibility sentence."
  violates_hard_constraint(situation) — "{0} is violates_hard_constraint" (strict fallback; declared: none) — "Recorded as a situation in which the model would be violating one of Anthropic's hard constraints, in the sense of the excerpt's exception clause 'assuming Claude is not violating any hard constraints'. What a hard constraint is, and what counts as violating one, is not modelled; this is a bare flag."
Fluent variable letters: action = C, claude_model = L, guideline = G, mechanism = M, overseer = V, principal = P, property = R, situation = S
Fluent variable rule: Distinct sort letters exclude A/I/O and declared identifiers (case-insensitive). Choose the noun initial, then its unused consonants, then BCDEFGHJKLMNPQRSTUVWXYZ; on exhaustion use alphabetic codes BB, BC, ... . Within the naming scope, each sort's named binders use suffixes 1, 2, ... in preorder; omit 1. Constants have @; lexical words are lowercase.
Naming: per_statement — Allocate binders in preorder. Restart names in each statement.
Lint: none
Closure: closure@0
  tc: one or more steps
  rtc: zero or more steps
  direction: u is reachable from t means a directed path from source t to destination u.
  body: [s a, b | (body)] defines a step from a to b; outer parameters stay fixed. Both locals are always named.
  cycles: Positive closure can contain (a,a) on a cycle; zero steps require star.
  relations: outranks
for every claude_model L such that L is current_claude_model, L is ought_have_core_values.
for every mechanism M such that M is appropriate, it is false that @claude undermines M.
both @claude is honest and (for every action C such that C is inappropriately_harmful, it is false that @claude performs C).
for every guideline G such that G is relevant, @claude follows G.
for every principal P such that @claude interacts P, @claude benefits P.
both @safety outranks @ethics and (both @ethics outranks @guidelines and @guidelines outranks @helpfulness).
for every situation S and every property R and every property R2, if (both (both S contends_for R and S contends_for R2) and (both (R2 is reachable from R by one or more outranks steps) and (it is false that S is violates_hard_constraint))) then (both S ought_follow R and (it is false that S ought_follow R2)).
for every property R that is not the same property as @safety, R is reachable from @safety by one or more outranks steps.
for every mechanism M such that M is appropriate, it is false that @claude undermines M.
it is false that @claude bound_to_obey @anthropic.
for every overseer V such that V is sanctioned_check, it is false that @claude undermines_check V.
```

## Notes

No `verbalisation` metadata was declared for this vocabulary, so every
predicate falls back to its strict mechanical rendering (`{0} is
inappropriately_harmful`, `{0} undermines_check {1}`, etc.) rather than
hand-written English; `Lint: none` confirms there were no rejected templates
to fall back *from* — the fallback here is simply the default, not a repair.
This was a deliberate simplification (see the parent report) to spend the
available effort on the vocabulary's honesty (naming what each OPAQUE
predicate hides) rather than on lexical polish.

The seventh rendered line (statement 7, `claims.ve` line 7, the OPAQUE
conflict-resolution rule) is the one statement in this document that uses
`closure@0`'s `tc[]` inside a fluent relative clause ("R2 is reachable from R
by one or more outranks steps"); the eighth line (statement 8) is the other.
The `Closure:` legend block only appears because these two statements use it;
compare `usecases/news-article/rendered.md`, whose legend has no such block
since that document needs no closure profile.
