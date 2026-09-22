# P2 flaw-taxonomy rubric (written before labelling)

Unit: one human-annotated flaw (the first error step, the judge's main complaint, or the
annotated fallacy span). One primary code per item; optional secondary code; `?` marks low
confidence.

Decision order (take the first that applies):

1. **S: wrong statement / misformalisation.** The flaw is in *what* is being argued, not in how.
   The author misreads the problem or a given premise (swaps "older"/"newer", drops a
   constraint, uses the wrong quantity), sets up the wrong equation from the text, proves a
   weaker or different claim than asked, answers the wrong question, or attacks a straw man.
   A verified checker would verify the wrong thing, so it cannot catch S.
2. **P: false or unjustified premise.** A claim is asserted *as a fact, recalled theorem,
   assumption or authority*, not as a consequence of earlier lines, and it is false or
   unsupported. Examples: a misremembered formula or theorem, "assume WLOG" when it is not WLOG,
   an unproven lemma stated as known, a factual error, a false dilemma (false disjunctive
   premise), an appeal to authority standing in for evidence. In VE this is a leaf, and the
   checker can flag it only as *ungrounded*, not as false.
3. **O: other**, with a sub-code:
   - `O-arith`: numeric or symbolic computation slip (wrong product, sign error, bad expansion).
     This is invalid inference in the narrow sense, but it can be caught by a CAS or `norm_num`,
     not by a natural-language deduction layer. Listed separately because the task asks for it.
   - `O-case`: missing case or non-exhaustive case split.
   - `O-equiv`: **equivocation.** One term is used in two senses across premises and
     conclusion. It is flagged separately because VE's identity-bound predicates target it.
   - `O-circ`: circular reasoning or begging the question (the argument is valid but assumes its
     conclusion).
   - `O-ambig`: vague or rhetorical, with no determinate propositional content (loaded language,
     emotional appeal with no inference to judge).
   - `O-incomplete`: the argument stops or hand-waves the key step ("it can be shown", an
     unfinished computation). No wrong step is written; a step is missing.
4. **D: invalid step.** Every stated premise is true or given, and the model or author presents
   the step as following from them, but it does not follow. This covers non sequiturs,
   overgeneralisation from special cases, converse or inverse errors, and wrongly concluding
   that a derived arrangement or value is forced when other options remain. Informal fallacies
   of relevance (ad hominem, ad populum, false causality, hasty generalisation, appeal to
   emotion *with* a conclusion) are D: the conclusion does not follow from what is stated.

Tie-breaks:
- S versus D in puzzles: if the step contradicts a *given* constraint because it was read
  wrongly, code S. If it was read correctly but mis-combined, code D.
- P versus D in proofs: if the text says "hence", "so", or "therefore" about a claim that does
  not follow, code D. If it says "it is known", "clearly" (for an external fact), "assume", or
  cites a theorem, code P.
- D versus O-arith: code O-arith when the error is local arithmetic or algebra that a calculator
  or CAS would catch. Code D when the invalid move is logical (a quantifier, a direction of
  implication, the conditions for applying a lemma).
- Fallacy corpora: start from the corpus label's default mapping (below), then override it from
  the text when the text clearly shows a different flaw. Mark `?` whenever the text does not
  clearly show the labelled fallacy at all (label noise).

Default mapping for the LOGIC/LogicClimate labels:

| label | default |
|---|---|
| faulty generalization, false causality, ad hominem, ad populum, fallacy of relevance, appeal to emotion, fallacy of logic | D |
| fallacy of credibility, false dilemma | P |
| fallacy of extension (straw man) | S |
| equivocation | O-equiv |
| circular reasoning | O-circ |
| intentional (deliberately misleading) | read text: usually S or P |

VE catchability tiers, reported separately:
- **strict**: D + O-equiv. The checker rejects the step, or the identity binding exposes it.
- **broad**: strict + O-circ + O-case + O-arith. These are mechanically detectable given a
  conclusion-in-premises check, exhaustiveness obligations, and a CAS.
- **never**: P and S. The checker is sound relative to leaves and to the formal statement, and
  these flaws live in exactly those places.

Caveat: in informal argument almost every D can be "repaired" into a valid argument with a false
premise (enthymeme). Formalising in VE forces that hidden premise to be stated, so a D flaw
becomes a visible P leaf. That still helps (the flaw becomes locatable), but it is not a
mechanical rejection.

## Amendment (added after labelling the first 17 BBM items, before any tallies)

- **S split.** `S-goal` covers the wrong question, a weaker claim, or a straw man. `S-premise`
  covers misreading or misencoding a *given* premise: a direction flip, a wrong slot index, a
  dropped quantity, or a coordinate choice that silently adds a constraint. The split matters
  because S-premise *is* catchable when the premises are formalised independently of the prover
  (for example by a separate formaliser or a cross-check), and is not catchable when the prover
  writes its own premises.
- **`D*`.** The step is annotated as a flaw, but it is entailed by the full premise set; it only
  uses premises it does not cite. BBM guidelines count "large logical jumps" as negative. VE
  would accept such a step once the premise is cited, so D* is reported separately and is *not*
  counted as D.
- **`N`.** Under this rubric the annotated step has no flaw: it is valid, or it is only
  redundant, which BBM also marks negative. Excluded from the denominator.
- **`U`.** The annotation says the result is wrong (for example "construction incorrect" or
  "wrong answer") but does not locate the flaw. Excluded from the denominator.
- **MathArena category hints.** Judge categories (logic, assumption, idea, algebra) are shown
  in brackets in the notes and were used as evidence, not as the label.
