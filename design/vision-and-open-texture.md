# Vision and open texture: VE as a commitment layer (2026-09-22)

Status: position note from discussions with the project lead; not a plan. Companions:
`design/crypto-inspired-oversight.md`, `design/frontier-failure-modes-and-ve.md`.

## The long-term vision

VE is the language of **committed communication**: laws, contracts, policies, scientific claims and methods, safety
procedures, and every instruction to or action by an AI agent. People think, talk, brainstorm and make art in ordinary
language; anything someone will be held to is written in VE, drafted by a translator (an IDE/LLM) and approved by its
author through an unambiguous paraphrase. Agents must state and prove what they intend to do before they act
(proof-carrying actions).

Thought experiment: an island whose constitution, laws and written communication use the extended VE of the vision
(degrees, tolerances, probability, time, obligations, exceptions, numbers, versioned definitions, a marked register for
analogies and suggestions). Conclusion after critique and counter-critique: no fundamental barrier; it likely gains
fewer legal contradictions, fewer disputes over meaning, more reproducible science, and agents whose actions are
checkable. What remains are engineering choices and social norms, listed below.

## Open texture: the residual that never disappears

Words that touch the world ("demeans", "harmful", "reasonable", "meaningful uplift") stay judgement calls (Hart's
"no vehicles in the park"). VE makes the logic around them exact but cannot decide whether they apply. Design response:
- **Decompose** open-textured predicates into narrower, evidence-backed leaves (as law splits crimes into elements);
  stop decomposing when inter-rater agreement on a leaf is high enough for the stakes.
- **Keep a named catch-all standard** ("... or otherwise demeans, as judged by the panel") so rubric-dodging content
  lands in an explicit, logged judgement slot instead of passing silently; patch the rubric from those cases.
- **Leave genuinely holistic terms whole** but isolated, counted and consistent (one predicate, one meaning everywhere);
  pin their known factors (e.g. foreseeability, cost of precaution) as named inputs.
- **Precisify lazily, like case law**: rulings become VE facts or definitions pinned by `meaning_id`.
- Each open predicate names who decides it (court, jury, AI panel), on what evidence, with what appeal.
Testable claim: decomposed verdicts flip less under pushback and agree more across judges than holistic ones (second
arm of the pushback study in `frontier-failure-modes-and-ve.md`).

## Norms and engineering the vision needs

- **Author responsibility:** the author owns an approved translation and corrects it, like a paper's numbers.
  Meaning pins plus dependency graphs let corrections and retractions propagate automatically.
- **Translator audits:** a widely used translator with a systematic bias (e.g. "may" -> "must") is not caught by
  individual responsibility; validate translators like calculators and statistics packages.
- **Two-party documents:** when one party's tool drafts the VE the other approves, adopt rules like reading ambiguity
  against the drafter.
- **Approval fatigue:** highlight the parts of a translation that most change meaning.
- **Conventions for vague terms:** shared defaults for "warm", "around", tolerances, like units.
- **Speech-act register:** claims vs analogies/suggestions/heuristics; analogies stated with explicit mappings.
- **Versioned concepts:** redefinitions are dated events; old documents keep their meaning.
- **Expressiveness vs checkability:** each extension must keep the checker small and proved; richer logics will make
  the checker answer UNKNOWN more often. The island's language is precise everywhere and mechanically checkable over
  most, not all, of what it can say.
- **Strategic ambiguity** (diplomacy, negotiation) is allowed in a marked register by choice.

## Implications for the project now

The same shape at every scale: checked structure plus an explicit, minimal, named residual. Near-term work that
serves the vision: the IDE loop (LLM drafts VE, author approves a paraphrase), policy-grade extensions (numbers,
attributes, sets, exceptions; borrow from Catala), a speech-act register, versioned definitions, and experiments that
measure whether shrinking and exposing judgement reduces errors and persuasion.
