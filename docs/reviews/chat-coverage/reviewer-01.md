# Coverage review: Chat lines 1–645

Owned source range: `docs/sources/Chat-Formalize English In Lean.md` lines **1–645** inclusive. Architecture references below use the **pre-edit baseline** of `docs/sources/verifiable_english_brainstorming_and_architecture_complete.md`, SHA256 `74d12bccca86206274a660d257aab5af5bea4d7d687e8624d8bd55a78339e1da`. I read the owned range and searched the entire architecture document before identifying gaps. No external claims in the chat were independently checked.

## Source-backed partial coverage

1. **Why a semantic-fidelity checker would be circular.** Chat **148–156** says that a machine-checkable equivalence test between ordinary English and Lean would first require a precise semantic representation of the English, which is the very output autoformalization seeks. Architecture **2829–2873** explains that Lean cannot determine whether a proposition captures English, but omits this useful explanation of why a separate *fully formal* English/Lean equivalence oracle is unavailable. **Proposed insertion after architecture 2873:** “A formal checker for `ordinary English ≡ Lean proposition` would itself need a precise formal interpretation of the English. Producing that interpretation is the autoformalization problem, so formal proof checking alone cannot close the semantic gap.” This should be framed as the reasoning in the chat, not a theorem that excludes all constrained-language checks.

2. **Candidate search has a scale and scope problem in addition to validity.** Chat **119–146** and **158–192** distinguishes swapped quantifiers, omitted assumptions, changed inequalities, and many provable but semantically different candidates. Architecture **2829–2873** captures the provable-wrong-statement problem and **2935–2958** depicts candidate filtering, but the workflow could explicitly state that type checking and proof attempts cannot rank semantic fidelity and that the candidate space can be large. **Proposed addition at architecture 2950–2955:** “Type checking and optional proof attempts eliminate some candidates; neither establishes fidelity to the source. Small changes in quantifier scope, domain, assumptions, or strictness can produce different well-formed and even provable propositions. Compare such differences in canonical back-translations and ask the author where source context does not decide.” This preserves the chat’s proposed use of proof attempts without implying their success settles meaning.

## Optional editorial suggestion

- **Clarify the restricted ACE↔Lean round trip with a concrete contrast.** Chat **520–642** gives “Every dog chases a cat” as a first-order example that can map through an AST to Lean, then contrasts a higher-order `List.map` theorem beyond ordinary ACE. Architecture **205–237**, **485–529**, **1962–1986**, **3315–3338**, and **3628–3683** already contain the substance: ACE-like first-order fragments can map to Lean; unrestricted Lean requires a much richer mathematical dialect or explicit escape hatch. If a reader needs a tangible example, add a short sentence near architecture **3628–3655**: “The ACE-like fragment can round-trip simple quantified propositions; higher-order Lean statements such as identities over `List.map` require the mathematical dialect or an explicit lower-level representation.” This is clarity, not a missing decision.

## Compact coverage inventory

| Chat source lines | Major topic | Architecture baseline lines | Assessment |
|---|---|---|---|
| 9–81 | Lean can represent precise propositions; formalization differs from proof and intent recovery | 53–105, 485–529, 674–725, 2829–2873, 3628–3665 | Covered; concrete `Good John` and Goldbach examples are illustrative, not necessary to retain. |
| 93–192 | Why autoformalization is hard; candidate generation, proof checking, semantic comparison | 2829–2873, 2935–2984, 2988–3028 | Covered with the two partial details above. |
| 198–245 | Human-readable controlled language; ACE, ForTheL, Lojban and syntax/semantics distinction | 165–237, 2032–2073, 3289–3338, 4615–4642 | Covered. Comparative star ratings in the chat are informal judgments and should not be imported as facts. |
| 249–294 | English-like surface, unique parse, shared semantic representation, round trip | 108–164, 426–481, 3749–3777, 4051–4081 | Covered. |
| 297–364 | Presupposition, sarcasm and indirect requests; context/intent | 53–105, 674–725, 1738–1763, 4288–4314 | Covered. |
| 366–418 | Formal→English versus ordinary English→formal asymmetry; ambiguity boundary | 674–725, 2877–2933, 2988–3028 | Covered. |
| 420–491 | Design ingredients: unique parse, quantifiers, probability, time/belief, explicit vagueness, feedback loop | 727–891, 1696–1782, 3749–3789, 4288–4332 | Covered. |
| 497–518 | OWL and ACE's DRS/FOL/OWL path | 205–237, 1962–1996, 3315–3338 | Covered. |
| 520–642 | ACE→Lean, restricted Lean→ACE, AST-mediated reversible subset | 108–164, 485–529, 892–934, 3315–3338, 3628–3683 | Covered; optional concrete example above. |

## Integration outcome

This report retains the original baseline citations. The parent verified and dispositioned every finding and optional suggestion in the [consolidated review](README.md), which gives exact updated architecture line numbers and the final outcome.
