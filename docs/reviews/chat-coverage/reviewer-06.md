# Coverage review 06

Owned source range: `Chat-Formalize English In Lean.md` lines 2794–3286 inclusive. Architecture line numbers below refer to the pre-edit baseline, SHA256 `74d12bccca86206274a660d257aab5af5bea4d7d687e8624d8bd55a78339e1da`.

## Source-backed omissions and contradictions

No substantive omission or contradiction found in this range after searching the entire architecture memo. The source is largely a sequence of requests to expand earlier drafts and ChatGPT's summaries of those expansions; the complete architecture memo already includes the resulting material, often in dedicated appendices.

## Coverage inventory

| Chat source lines | Topic | Architecture baseline lines |
| --- | --- | --- |
| 2794–2822 | Meaning of canonical; naming alternatives and conditional VE/CEV preference | 138–163; 1800–1866; 5100–5122 |
| 2826–2854 | Prompt archive and decision-memo purpose | 1–51; 5201–5217 |
| 2858–2919 | Related language/system survey, including OWL, CLCE, ForTheL, Verbose Lean, Visored, TLA+, proof assistants, GF, C, Frama-C, and CompCert | 1958–2280; 2386–2558 |
| 2927–2972 | Broad use cases and three kinds of scientific correctness | 892–1128; 1624–1696; 3142–3220; 5156–5179 |
| 2976–3080 | Aeneas/Rustlight common subset, trusted checker steps, dual proof paths, coding standard | 2600–2820; 4806–4927 |
| 3088–3170 | Autoformalization mismatch; directional asymmetry; generate, verify, clarify; ACE rationale; verification taxonomy; human/agent/kernel roles; historical notes | 2825–3520; 4470–4768 |
| 3178–3193 | AI feasibility and dated capability evidence; Claude constitution case; strong Lean front-end ambition | 3522–3741; 4962–4990; 5066–5098 |
| 3195–3233 | Guarantees, versioning, conformance, benchmarks, extensions, equivalence levels, security | 3745–4169 |
| 3237–3264 | Claimed comprehensive additions, including error taxonomy, provenance, interoperability, authoring, governance, artifacts, thesis | 4173–4468 |
| 3272–3286 | Claimed final audit, coverage checklist, and final download filename | 4470–5219 |

## Optional editorial improvements

1. **Gather use cases near the beginning.** Chat lines 2937–2972 explicitly propose a single use-case catalog. The architecture includes the substantive cases in §§14–17 (lines 892–1128), demos (1624–1696), and the checklist (5156–5179), but readers must collect them across the memo. Consider a compact navigation table after the executive summary, around architecture lines 49–52, pointing to each existing section. This is an organization improvement, not missing content.

2. **Qualify the common-subset feasibility claim.** Chat lines 2984–2989 say the Aeneas/Rustlight overlap is *probably* sufficient. Architecture lines 2641–2645 say it is "already large enough," while lines 2804–2810 prescribe the intersection as a coding standard. The source offers a design hypothesis, not a demonstrated intersection of tool-supported language features. Consider revising line 2645 to "appears likely to be large enough, subject to a representative parser/checker spike" and adding that spike to roadmap lines 1550–1558. This retains the recommendation while making its uncertainty clear.

3. **Date the formal-math examples at point of claim.** Chat lines 3190–3192 explicitly request dated, time-sensitive capability evidence. Architecture lines 3602–3624 explain this policy, but the concrete claims at 4962–4988 use "recent" without an as-of date. Add an as-of date at 4962–4964 or cross-reference the dated tooling profile. This is an attribution/maintenance improvement, not a coverage omission.

## Integration outcome

This report retains the original baseline citations. The parent verified and dispositioned every finding and optional suggestion in the [consolidated review](README.md), which gives exact updated architecture line numbers and the final outcome.
