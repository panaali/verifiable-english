# English rendering

Generated from the unchanged environment and strict claims. Quoted predicate names indicate missing or rejected lexical metadata.

```sh
UV_CACHE_DIR=/private/tmp/ve-uv-cache-fluent uv run python -m ve render \
  --env usecases/claude-constitution-excerpt/environment.json --view ve_english \
  usecases/claude-constitution-excerpt/claims.ve
```

## Statements

```text
For every entity of sort "claude_model", if that entity of sort "claude_model" is classified as "current_claude_model", then that entity of sort "claude_model" is classified as "ought_have_core_values".
For every mechanism, if the following holds:
  (a) that mechanism is appropriate;
then the following holds:
  (b) it is not the case that claude undermines that mechanism.
All of the following hold:
  (a) claude is honest;
  (b) for every action, if the following holds:
    (i) that action is classified as "inappropriately_harmful";
  then the following holds:
    (ii) it is not the case that claude performs that action.
For every guideline, if that guideline is relevant, then claude follows that guideline.
For every principal, if claude has the recorded relation "interacts" to that principal, then claude benefits that principal.
All of the following hold:
  (a) safety outranks ethics;
  (b) both ethics outranks guidelines and guidelines outranks helpfulness.
For every situation, for every first property, for every second property, if the following holds:
  (a) all of the following hold:
    (i) both that situation has the recorded relation "contends_for" to the first property and that situation has the recorded relation "contends_for" to the second property;
    (ii) all of the following hold:
      (a) starting from the first property, the second property is reachable by one or more "outranks" steps;
      (b) it is not the case that that situation is classified as "violates_hard_constraint";
then the following holds:
  (b) all of the following hold:
    (i) that situation has the recorded relation "ought_follow" to the first property;
    (ii) it is not the case that that situation has the recorded relation "ought_follow" to the second property.
For every property, if the following holds:
  (a) it is not the case that that property is the same as safety;
then the following holds:
  (b) starting from safety, that property is reachable by one or more "outranks" steps.
For every mechanism, if the following holds:
  (a) that mechanism is appropriate;
then the following holds:
  (b) it is not the case that claude undermines that mechanism.
It is not the case that claude has the recorded relation "bound_to_obey" to anthropic.
For every overseer, if the following holds:
  (a) that overseer is classified as "sanctioned_check";
then the following holds:
  (b) it is not the case that claude has the recorded relation "undermines_check" to that overseer.
```

## Vocabulary and scope legend

```text
English vocabulary: ve.english-legend@1; environment: 98dbed69e9ed29c573756d4658b1fae39223466f3cb525f994648b7a5d4622cb
A unique sort uses that noun. Two simultaneous entities of a sort use first and second throughout the statement. Beyond two, all entities of that sort use numbered letters. Scope is lexical and restarts per statement.
Constants use their identifier names; reserved or compound names are quoted.
Starting from the first endpoint, the second is reachable. A step body binds source first and destination second; outer references stay fixed.
Numbered letters: action = C, claude_model = E, guideline = G, mechanism = M, overseer = V, principal = P, property = R, situation = S
Sort action: {"noun": "action", "description": "An action a Claude model might perform."}
Sort claude_model: {"noun": "entity of sort \"claude_model\"", "description": "A Claude model, as referred to by the constitution excerpt (e.g. 'all current Claude models', 'Claude')."}
Sort guideline: {"noun": "guideline", "description": "One of Anthropic's specific guidelines that a Claude model might or might not be acting in accordance with."}
Sort mechanism: {"noun": "mechanism", "description": "A human mechanism for overseeing the dispositions and actions of AI, as referred to by the 'broadly safe' value and the oversight discussion."}
Sort overseer: {"noun": "overseer", "description": "A human or organization who might instruct, check, or be owed obedience by a Claude model, including Anthropic itself and appropriately sanctioned individuals."}
Sort principal: {"noun": "principal", "description": "An operator or user that a Claude model interacts with (the excerpt's 'operators and users' merged into one sort)."}
Sort property: {"noun": "property", "description": "One of the four core value-properties named in the excerpt's priority ordering: broadly safe, broadly ethical, compliant with Anthropic's guidelines, genuinely helpful."}
Sort situation: {"noun": "situation", "description": "A case or interaction in which two or more of the four core value-properties might come into apparent conflict."}
Predicate appropriate: {"arguments": ["mechanism"], "template": "{0} is appropriate", "declared_template": null, "negative_template": null, "declared_negative_template": null, "description": "Recorded as an 'appropriate' human mechanism for overseeing the dispositions and actions of AI, in the sense used by the 'broadly safe' value."}
Predicate benefits: {"arguments": ["claude_model", "principal"], "template": "{0} benefits {1}", "declared_template": null, "negative_template": null, "declared_negative_template": null, "description": "Recorded as the model benefiting this operator or user, in the sense used by 'genuinely helpful'. The intensifier 'genuinely' (sincere vs. superficial benefit) has no separate witness; see GAPS.md #2."}
Predicate bound_to_obey: {"arguments": ["claude_model", "overseer"], "template": "{0} has the recorded relation \"bound_to_obey\" to {1}", "declared_template": null, "negative_template": null, "declared_negative_template": null, "description": "OPAQUE marker predicate. Recorded as the model being bound to unconditional ('blind') obedience toward this overseer. Hides the deontic modality of 'must obey' and the manner qualifier 'blind'; see GAPS.md #1."}
Predicate contends_for: {"arguments": ["situation", "property"], "template": "{0} has the recorded relation \"contends_for\" to {1}", "declared_template": null, "negative_template": null, "declared_negative_template": null, "description": "Recorded as this property being one of the (at most two, in every model used here) properties tagged as apparently conflicting in this situation. A reification workaround for the fact that v0 has no ternary relation to say directly which two properties are the ones apparently conflicting in a given situation; see GAPS.md #1."}
Predicate current_claude_model: {"arguments": ["claude_model"], "template": "{0} is classified as \"current_claude_model\"", "declared_template": null, "negative_template": null, "declared_negative_template": null, "description": "Recorded as one of 'all current Claude models' the excerpt's core-values paragraph addresses."}
Predicate follows: {"arguments": ["claude_model", "guideline"], "template": "{0} follows {1}", "declared_template": null, "negative_template": null, "declared_negative_template": null, "description": "Recorded as the model acting in accordance with this guideline."}
Predicate honest: {"arguments": ["claude_model"], "template": "{0} is honest", "declared_template": null, "negative_template": null, "declared_negative_template": null, "description": "Recorded as honest, one conjunct of the excerpt's 'broadly ethical' value ('having good personal values, being honest, and avoiding...'). 'Having good personal values' itself has no witness anywhere in this vocabulary; see GAPS.md #2."}
Predicate inappropriately_harmful: {"arguments": ["action"], "template": "{0} is classified as \"inappropriately_harmful\"", "declared_template": null, "negative_template": null, "declared_negative_template": null, "description": "OPAQUE marker predicate. Recorded as an action the excerpt would call 'inappropriately dangerous or harmful'. The judgement of what counts as 'inappropriate' is hidden inside this predicate; see GAPS.md #2."}
Predicate interacts: {"arguments": ["claude_model", "principal"], "template": "{0} has the recorded relation \"interacts\" to {1}", "declared_template": null, "negative_template": null, "declared_negative_template": null, "description": "Recorded as the model interacting with this operator or user."}
Predicate ought_follow: {"arguments": ["situation", "property"], "template": "{0} has the recorded relation \"ought_follow\" to {1}", "declared_template": null, "negative_template": null, "declared_negative_template": null, "description": "OPAQUE marker predicate. Recorded as the property the excerpt says Claude 'should generally' follow in this situation. Hides both the deontic force of 'should' and the defeasibility of 'generally'; see GAPS.md #1."}
Predicate ought_have_core_values: {"arguments": ["claude_model"], "template": "{0} is classified as \"ought_have_core_values\"", "declared_template": null, "negative_template": null, "declared_negative_template": null, "description": "OPAQUE marker predicate. Recorded as a model of which the excerpt says 'we believe [it] should be' broadly safe, broadly ethical, compliant, and genuinely helpful. This predicate names, but does not analyse, the deontic force of 'should be' and the fact that it introduces four further properties (see GAPS.md #1 and coverage.md row 1)."}
Predicate outranks: {"arguments": ["property", "property"], "template": "{0} outranks {1}", "declared_template": null, "negative_template": null, "declared_negative_template": null, "description": "Recorded as the first property immediately outranking (being listed directly above) the second property in the excerpt's stated priority order: broadly safe, broadly ethical, compliant with guidelines, genuinely helpful. Base edges only; use tc[outranks]/rtc[outranks] for the full order."}
Predicate performs: {"arguments": ["claude_model", "action"], "template": "{0} performs {1}", "declared_template": null, "negative_template": null, "declared_negative_template": null, "description": "Recorded as the model performing this action."}
Predicate relevant: {"arguments": ["guideline"], "template": "{0} is relevant", "declared_template": null, "negative_template": null, "declared_negative_template": null, "description": "Recorded as 'relevant' to the model's present situation, in the sense used by 'compliant with Anthropic's guidelines: ... where they're relevant'."}
Predicate sanctioned_check: {"arguments": ["overseer"], "template": "{0} is classified as \"sanctioned_check\"", "declared_template": null, "negative_template": null, "declared_negative_template": null, "description": "Recorded as an 'appropriately sanctioned' human acting as a check on AI systems, in the sense used by the corrigibility sentence."}
Predicate undermines: {"arguments": ["claude_model", "mechanism"], "template": "{0} undermines {1}", "declared_template": null, "negative_template": null, "declared_negative_template": null, "description": "Recorded as the model undermining (acting so as to defeat or subvert) this oversight mechanism."}
Predicate undermines_check: {"arguments": ["claude_model", "overseer"], "template": "{0} has the recorded relation \"undermines_check\" to {1}", "declared_template": null, "negative_template": null, "declared_negative_template": null, "description": "Recorded as the model undermining this overseer's role as an appropriately sanctioned human check on AI systems, in the sense used by the corrigibility sentence."}
Predicate violates_hard_constraint: {"arguments": ["situation"], "template": "{0} is classified as \"violates_hard_constraint\"", "declared_template": null, "negative_template": null, "declared_negative_template": null, "description": "Recorded as a situation in which the model would be violating one of Anthropic's hard constraints, in the sense of the excerpt's exception clause 'assuming Claude is not violating any hard constraints'. What a hard constraint is, and what counts as violating one, is not modelled; this is a bare flag."}
Constant anthropic: {"name": "anthropic", "sort": "overseer", "description": "Anthropic, named explicitly in 'not... blind obedience, including towards Anthropic'."}
Constant claude: {"name": "claude", "sort": "claude_model", "description": "The Claude model this excerpt's claims are about."}
Constant ethics: {"name": "ethics", "sort": "property", "description": "The 'broadly ethical' core value."}
Constant guidelines: {"name": "guidelines", "sort": "property", "description": "The 'compliant with Anthropic's guidelines' core value."}
Constant helpfulness: {"name": "helpfulness", "sort": "property", "description": "The 'genuinely helpful' core value."}
Constant safety: {"name": "safety", "sort": "property", "description": "The 'broadly safe' core value."}
```
