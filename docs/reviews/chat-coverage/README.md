# Chat coverage review and applied changes

Reviewed on September 20, 2026. Six subagents read every line of their assigned chat ranges and compared their topics against the full architecture memo. The integrating reviewer checked the reported gaps against the cited source and target passages, then applied **15 substantive additions/clarifications**, **6 optional improvements**, and **3 integration cleanups**. Seven other optional suggestions were already covered or were not worth duplicating; each disposition is recorded below. No reported substantive gap remains unapplied.

This was a **source-coverage audit**, not fresh external research. Historical project, availability, licensing, model-capability, and legal-source claims remain attributed to the conversation. The architecture remains a proposal, not evidence that implementation or verification milestones have already been achieved.

## Files and line-number convention

- **Chat** means [Chat-Formalize English In Lean.md](<../../sources/Chat-Formalize English In Lean.md>), 3,286 lines, unchanged by this review.
- **Architecture** means [verifiable_english_brainstorming_and_architecture_complete.md](../../sources/verifiable_english_brainstorming_and_architecture_complete.md), originally 5,219 lines; now 5,280 lines.
- **Baseline** line numbers refer to the exact pre-edit file used by every reviewer. The reviewer reports deliberately retain those original citations.
- **Updated** line numbers refer to the final architecture file. For omissions, baseline references identify the insertion point or partial coverage, not nonexistent text. Ranges are inclusive and 1-based.
- [architecture-changes.patch](architecture-changes.patch) preserves the complete edit and allows the baseline to be reconstructed from the updated file without storing a second full memo.

SHA-256 identities:

```text
Chat:                 72468df76d9eaf14fb7b293785f7613fd28e3069aece1c7839e1f8307efb4954
Architecture baseline: 74d12bccca86206274a660d257aab5af5bea4d7d687e8624d8bd55a78339e1da
Architecture updated:  90b9df7920f4d22d0931739e75610f6b5b29815f4f649a05cab5d46a3fa2ede1
```

## Review ownership

| Reviewer report | Owned chat lines | Scope |
|---|---|---|
| [Reviewer 01](reviewer-01.md) | 1–645 | Motivation, autoformalization, language comparison, reversible subsets |
| [Reviewer 02](reviewer-02.md) | 646–1319 | Lojban, ACE boundaries, implementation and metatheory |
| [Reviewer 03](reviewer-03.md) | 1320–1835 | Proof tools, existing languages and early project paths |
| [Reviewer 04](reviewer-04.md) | 1836–2291 | CE/NOAH, revised foundation, Lean/Rust verification and math |
| [Reviewer 05](reviewer-05.md) | 2292–2793 | Science, compiler verification, law, AI constitutions and versioning |
| [Reviewer 06](reviewer-06.md) | 2794–3286 | Naming, common Rust subset, final synthesis and expansion requests |

These ranges partition the complete chat with no gaps or overlapping ownership. Each report includes a coverage inventory with exact chat and baseline architecture lines. Reviewer 06 found no substantive omission, but proposed three improvements.

## Substantive findings: verified and applied

IDs correspond to the numbered findings in each reviewer report. Multiple edit ranges within one row implement one finding.

| Finding | Chat lines | Architecture baseline lines | Architecture updated lines | Verified disposition |
|---|---|---|---|---|
| R01-1 | 148–156 | 2873 | 2905–2907 | Applied: Formal English/Lean equivalence-oracle circularity. |
| R01-2 | 119–192 | 2961 | 2995–2999 | Applied: Candidate-space scale and limits of proof filtering and semantic ranking. The wording avoids the chat’s suggestion that proof attempts settle consistency or meaning. |
| R02-1 | 693–727; 1017–1021 | 4550; 4642 | 4594–4596; 4688–4690 | Applied: ACE lexical vagueness and underspecified background axioms, including the chat’s correction to its Lojban comparison. |
| R02-2 | 1206–1214 | 3779 | 3817–3819 | Applied: Unique accessible antecedent as a separate reference-resolution proof obligation. |
| R02-3 | 1117–1119 | 2272 | 2302 | Applied: ACE-in-GF tree round trips do not supply the missing ACE→DRS semantics. |
| R02-4 | 1218–1230 | 3799–3801 | 3839–3845 | Applied: Naturalness and all-English completeness are not established by the formal guarantees. |
| R02-5 | 1141–1156 | 524 | 539–541 | Applied: The ACE compatibility theorem needs a versioned formal ACE model, beyond regression agreement. |
| R03-1 | 1524–1538 | 241 | 254–256 | Applied: PENG’s bidirectional grammar as a parser/printer precedent. |
| R03-2 | 1656–1711; 1733–1789; 1838–1920 | 1299 | 1325–1327 | Applied: Decision chronology: ACE-informed technical milestone, then conditional CE collaboration. Parent verified the explicit later change at chat 1844–1846 and 1914–1920 rather than inferring a reversal from the memo alone. |
| R04-1 | 1990–2003 | 4727 | 4775–4777 | Applied: CGEL/CGELBank, Stanza, and markdownlint as historical component leads, not audited dependencies. |
| R04-2 | 1932–1948 | 4749 | 4799–4801 | Applied: Exact CE repository, MIT-0 claim, and source-layout leads with historical, unconfirmed status. |
| R05-1 | 2670 | 668; 4923 | 685; 4975–4977 | Applied: RustCompCert’s unverified source parser and proposed remedies. Distinguish that parser from VE’s parser; AST generation still needs correspondence to the proved core. |
| R05-2 | 2641–2650 | 2643 | 2673–2675 | Applied: Reported Rustlight supported/excluded features, distinguished from VE preferences and Aeneas support. |
| R05-3 | 2707–2709; 2762 | 1045–1047; 1073–1075 | 1064–1068; 1096–1101 | Applied: Open constitutional standard and interpretive-method provenance as modeling choices. |
| R05-4 | 2719–2726 | 1062 | 1083–1085 | Applied: Precedent-change dependency query, preserving prior snapshots and possible alternative support. |

## Optional suggestions: dispositions

`E` numbers follow the order of optional suggestions in the individual reports. An “already covered” outcome records useful verification, rather than an unhandled omission.

| Suggestion | Chat lines | Architecture baseline lines | Architecture updated lines | Disposition |
|---|---|---|---|---|
| R01-E1 | 520–642 | 205–237; 3628–3683 | 218–250; 3666–3721 | Already covered; retain the existing ACE/Lean expressive-boundary explanation rather than add another quantified/List.map example. |
| R02-E1 | 759–776 | 4615–4642 | 4661–4690 | Not added: the quantifier lesson is present; a canonical Lojban utterance would need separate language verification. |
| R02-E2 | 674–689 | 185–201; 4615–4642 | 198–214; 4661–4690 | Not added: another attachment-ambiguity example would duplicate existing examples and the syntax/meaning distinction. |
| R02-E3 | 1007–1009; 1310–1312 | 4554–4577 | 4600–4623 | Not added: retain the approximately 3,500 cases tied to ACE 6.6; the later approximately 3,700 figure is not tied to a corpus version in the chat. |
| R03-E1 | 1430–1452 | 2170 | 2200 | Applied: distinguish TLC finite-model exploration from TLAPS theorem proofs. |
| R03-E2 | 1604–1608 | 1738–1763; 3791–3799 | 1768–1793; 3831–3839 | Already covered: pragmatics and indirect requests have examples; the window/ability example adds no new design requirement. |
| R03-E3 | 1723–1729 | 3602–3624; 4962–4990 | 3640–3662; 5016–5044 | Not added: volatile model benchmark percentages remain outside this synthesis. The capability rationale remains, with point-of-claim dating under R06-E3. |
| R04-E1 | 93–156; 2092–2098; 2138–2154 | 723 | 740–742 | Applied: even an accepted well-formed AST can misstate human intent. |
| R05-E1 | 2490–2508 | 544–556; 2284–2314 | 561–573; 2314–2344 | Already explicit: baseline line 556 says formal verification is primarily offline and need not impose significant runtime overhead. No duplicate paragraph added. |
| R05-E2 | 2754–2756 | 1116 | 1142 | Applied: connect normative semantics to the module architecture and Lean metatheory. |
| R06-E1 | 2937–2972 | 49 | 51–62 | Applied: near-front use-case navigation table. |
| R06-E2 | 2984–2989; 2991–3062 | 1437; 2645; 2674 | 1465–1467; 2677; 2706 | Applied: restore “probably sufficient” uncertainty for the Rust intersection and add an early prototype with pinned tool versions. The prototype is an integration improvement, not a claim it already ran. |
| R06-E3 | 1727–1729; 2246; 3190–3192 | 4964–4966 | 5018–5020 | Applied: date and attribute the formal-math examples as discussion-time research leads, not newly verified evidence. |

## Integrating-review cleanups

These are explicitly identified as integration improvements rather than additional omissions claimed by subagents.

| Change | Chat lines | Architecture baseline lines | Architecture updated lines | Disposition |
|---|---|---|---|---|
| P-1 | 1–3286 | 5 | 5–7 | Applied: Add a source-basis note and a link to this audit; distinguish coverage from external fact verification. |
| P-2 | 3220–3230 | 140 | 153 | Applied: Align §4 with Appendix T: declared normalization, logical equivalence, and paraphrase must not be conflated. |
| P-3 | 2826–2854; 3272–3286 | 5197; 5203–5217 | 5251–5264; 5270–5278 | Applied: Update the coverage checklist, replace an unqualified completeness claim with the audit record, distinguish full chat from prompt archive, and correct the existing prompt-archive filename. |

## Verification

- Parent verified every substantive finding against the supplied chat and the original architecture passages. Additions preserve later decisions and distinguish historical claims from design proposals.
- Two original reviewers rechecked the applied edits. The non-Rust/nonlegal review found no source-fidelity or consistency issue; the Rust/legal review confirmed the parser trust boundary, conditional subset feasibility, and preservation of alternative legal support.
- Mechanical checks verified complete range ownership, unchanged chat content, exact edited-span line numbers, balanced Markdown fences, and local links. The saved patch was reversed in a temporary copy and recovered the baseline SHA-256 exactly.
- No implementation tests were run: only Markdown and review artifacts changed.

Review reports remain the original reviewer assessments; this file records the parent's verified disposition and the final line numbers. Future architecture edits will change those numbers, so use the recorded SHA-256 identities and patch when referring back to this audit.
