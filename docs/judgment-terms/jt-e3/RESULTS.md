# JT-E3 results

**PASS**: 60 blind ratings per model; 53 agreements and 7 disagreements.
Claude Sonnet 5.5 (`claude-saeedi-danial`) and Codex GPT-6 Astra made one
independent rater call each. `claude.raw.txt` and `codex.raw.txt` retain the
unaltered CLI answers; the validated classifications are `claude.json` and
`codex.json`. `RESULTS.json` is the machine-readable computation.

## Agreement

Rows are Claude; columns are Codex. Classes are in the preregistered order.

| Claude \ Codex | attitude | classification | exception | judgment | proportion | Total |
|---|---:|---:|---:|---:|---:|---:|
| attitude | 2 | 0 | 0 | 0 | 0 | 2 |
| classification | 0 | 20 | 0 | 1 | 0 | 21 |
| exception | 0 | 0 | 3 | 0 | 0 | 3 |
| judgment | 0 | 6 | 0 | 27 | 0 | 33 |
| proportion | 0 | 0 | 0 | 0 | 1 | 1 |
| **Total** | **2** | **26** | **3** | **28** | **1** | **60** |

`Po = (2 + 20 + 3 + 27 + 1) / 60 = 53/60`.
`Pe = (2×2 + 21×26 + 3×3 + 33×28 + 1×1) / 60² = 371/900`.
`κ = (Po − Pe)/(1 − Pe) = 424/529 = 0.801512…`.
The preregistered bar is **Cohen's κ at least 0.7**; this result passes.
`analyze.py` uses exact fractions, and `test_hand_computed_kappa` checks
`[[3,1],[1,3]] → κ = 1/2`.

The seven differing terms are `community_of_full_development`,
`democratic_society`, `discrimination`, `equal_protection_of_the_law`,
`full_equality`, `persecution` (UDHR), and
`instruction_abandon_identity_in_persona` (constitution). Claude called the
first `classification` and the other six `judgment`; Codex made the opposite
call for each. The original frame class is `classification` for the first and
`judgment` for the other six. The original class was hidden from both raters.

## Count sensitivity

These are the original JT-0p instrument counts recomputed from the pinned
ledgers. “Without disagreement” removes the seven sampled terms above from
each unit's judgment-term set; a unit with another judgment term remains.
“Without borderline” also removes the frame's flagged judgment terms.
The cuts are independent. `UDHR JT-0p` is the copy with the two renamed terms;
the baseline UDHR is the earlier live pilot.

| Pilot | Disagreeing terms | Borderline terms | Units | Bytes |
|---|---|---|---:|---:|
| UDHR | with | with | 18 | 1,945 |
| UDHR | with | without | 11 | 1,333 |
| UDHR | without | with | 14 | 1,627 |
| UDHR | without | without | 11 | 1,333 |
| UDHR JT-0p | with | with | 20 | 2,143 |
| UDHR JT-0p | with | without | 13 | 1,531 |
| UDHR JT-0p | without | with | 16 | 1,825 |
| UDHR JT-0p | without | without | 13 | 1,531 |
| Constitution | with | with | 507 | 88,989 |
| Constitution | with | without | 503 | 88,025 |
| Constitution | without | with | 507 | 88,989 |
| Constitution | without | without | 503 | 88,025 |

This is sensitivity to **observed** disagreement in the 60-term sample.
The 29 unsampled terms keep their original frame classes; this experiment
cannot identify disagreement on them. Constitution's disagreeing term occurs
alongside other judgment terms in its annotated units, so excluding it does
not change the unit or byte totals. These are retrospective instrument counts,
not a new checker result or newly claimed pilot coverage.
