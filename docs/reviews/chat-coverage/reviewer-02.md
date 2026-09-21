# Coverage review 02

Owned source range: `Chat-Formalize English In Lean.md` lines 646–1319, read in full. Architecture line numbers below refer to the **pre-edit baseline**, SHA256 `74d12bccca86206274a660d257aab5af5bea4d7d687e8624d8bd55a78339e1da`. I compared against the entire 5,219-line architecture document. Historical and implementation claims below are claims made in the chat; this is a source-coverage review, not external verification.

## Source-backed omissions and partial coverage

1. **The semantics of ACE predicates also need background definitions.** Chat lines **693–727**, especially the explicit correction at **725–727**, acknowledge that “good doctor” is context dependent in *both* Lojban and ACE. Chat lines **1017–1021** further qualify that a unique ACE DRS does not settle background axioms for plurals and modality. Architecture lines **205–235**, **3289–3309**, **4538–4550**, and **4615–4642** give the contrast but can leave the impression that ACE's formal structure settles lexical and background meaning. Add after architecture **4634–4640**: “This contrast concerns a specified logical representation, not a complete definition of every content word or background axiom. ‘Good doctor’ still needs a chosen predicate meaning in either language; ACE DRSs may leave background treatment of plurals or modality open.” Preserve the chat's correction rather than its earlier overstrong example.

2. **Reference-resolution proof obligation is absent.** Chat lines **1206–1214** propose rejecting ambiguous pronouns or proving that each accepted pronoun resolves to exactly one accessible antecedent; this is a concrete guarantee beyond generic unique parsing. Architecture lines **61–68** mention ambiguous references, **3089–3104** describes APE anaphora resolution, and **3753–3779** lists guarantees, but none states the accepted-pronoun obligation. Add near architecture **3757–3759** or **3777–3779**: “For accepted anaphoric references, resolution selects exactly one accessible antecedent under the declared discourse rules; otherwise the checker requests clarification or rejects the sentence.” If this cannot be guaranteed for all accepted syntax, mark it as a versioned target theorem.

3. **ACE-in-GF's semantic boundary is only implicit.** Chat lines **1117–1119** distinguish GF's abstract/concrete grammars and tree round trips from the absent ACE→DRS semantic mapping. Architecture lines **2241–2276** cover the architecture and say GF lacks all desired semantics, but do not explicitly warn that the cited project does not supply ACE→DRS semantics. Add to architecture **2270–2272**: “In the chat's assessment, ACE-in-GF tested tree round trips but did not provide an ACE→DRS semantics; its round trip alone is not a proof of semantic preservation.” Treat this as a claim from the discussion, pending independent project verification.

4. **The boundary of what can be proved should be stated explicitly.** Chat lines **1218–1230** say naturalness and completeness for all English meaning lack a formal reference specification, while an English grammar can be checked and naturalness can be evaluated with speakers. Architecture lines **694–706** and **3791–3799** caution against recovering arbitrary intent and vagueness; **3751–3789** lists formal guarantees. Add near architecture **3791–3799**: “We cannot prove that every VE sentence sounds natural to English speakers, or that VE expresses every meaning of unrestricted English, without a formal specification of those targets. Assess naturalness empirically and measure coverage against a declared corpus and domain.” This avoids treating an open-ended aspiration as a theorem.

5. **Potentially misleading strength of ACE compatibility theorem.** Chat lines **1141–1156** condition a conservative-extension proof on formalizing ACE 6.7 semantics first. Architecture lines **517–522** and **1384–1390** state compatibility equations, while **1394–1414** describes empirical APE benchmarking, but the theorem prerequisite is not adjacent to either equation. Add a sentence after architecture **517–522**: “This theorem requires a versioned formal model of the relevant ACE semantics; APE regression agreement alone supports compatibility empirically but cannot prove equality for all ACE sentences.”

## Optional editorial suggestions

- The concrete Lojban utterance and `ro da` / `su'o de` quantifier gloss from chat **759–776** do not appear in architecture **4615–4642**. It could be included as a compact teaching example, but the formal contrast is already captured there. Verify the Lojban sentence with a qualified source before promoting it to a canonical example.
- The train attachment ambiguity from chat **674–689** could be included beside architecture **185–201** or **4636–4640** as a simple syntactic example; the existing quantifier comparison may suffice.
- Architecture **4564** preserves the approximately 3,500 ACE 6.6 cases from chat **1007–1009**, but not the later approximately 3,700 count in chat **1009**, **1310–1312**. Keeping the dated 6.6 figure is more precise unless a later corpus version is identified.

## Compact coverage inventory

| Chat source lines | Major topic | Architecture baseline lines | Assessment |
|---|---|---|---|
| 646–662, 737–747, 940–957 | Lojban syntax versus ACE formal interpretation | 185–201, 3289–3309, 4581–4606, 4634–4642 | Covered; lexical caveat partial |
| 674–715, 719–727 | English attachment ambiguity and corrected “good doctor” comparison | 185–201, 3289–3309, 4615–4642 | Principle covered; correction partial |
| 729–776, 802–820 | Doctor/patient quantification, ACE surface form, Lojban quantifiers | 4615–4642 | Formal comparison covered; exact Lojban wording omitted |
| 780–798, 932–957 | Lojban origins, six source languages, Lean translation limit | 3289–3309, 4581–4606 | Covered |
| 824–879, 1031–1095 | Sarah tense/aspect example, indirect ACE encoding, richer semantic domains | 90–104, 727–746, 765–825, 4474–4550 | Covered |
| 883–928 | ACE historical design and requirements examples | 3030–3085 | Covered |
| 961–1009 | ACE++ feasibility, APE license, pipeline, regression corpus | 205–235, 3089–3117, 4554–4577 | Covered, with corpus-version nuance |
| 1013–1027 | ACE implementation proof gap and semantic underspecification | 3121–3138, 4538–4550 | Proof gap covered; background axioms partial |
| 1099–1133 | Semantic AST, English rendering, Lean, GF precedent | 110–170, 2241–2276, 3366–3374 | Covered; ACE-in-GF semantic boundary partial |
| 1137–1204 | Conservative extension, unique interpretation, round trip, translation correctness | 467–524, 1375–1414, 3745–3775 | Covered; formal ACE prerequisite partial |
| 1206–1214 | Anaphora uniqueness proof obligation | 61–68, 3089–3104, 3753–3779 | Partial |
| 1218–1269 | Limits of naturalness/completeness proofs, pragmatics/context | 694–706, 1738–1755, 3791–3799, 4060–4079 | Examples covered; proof boundary partial |
| 1273–1290 | Graduated difficulty and open-ended research scope | 727–825, 1700–1765, 1890–1953 | Covered in substance |
| 1294–1316 | APE as compatibility oracle, Lean core, first milestone | 235, 1384–1414, 1883–1900, 4564–4572 | Covered |

## Integration outcome

This report retains the original baseline citations. The parent verified and dispositioned every finding and optional suggestion in the [consolidated review](README.md), which gives exact updated architecture line numbers and the final outcome.
