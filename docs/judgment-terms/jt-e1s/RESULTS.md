# JT-E1s result: the one revision of section 2.4, rerun on fresh items

**JT-3 wording gate FAIL: bar (a) fails (English 25/40, identifier 20/40, margin 5); bar (b) passes (0 critical).**

This is proxy evidence from Sonnet 5.5, not human comprehension. A human reader audit remains a separate acceptance item. It was the plan's one revision (section 6, JT-E1 "Then"), so there is no second revision. The plan's fallback applies: JT-3's declaration lines use today's identifier wording.

| Arm | Fully correct | Rate | Critical misreadings |
|---|---:|---:|---:|
| Main renderer identifier fallback | 20 / 40 | 50% | 0 |
| Section 2.4 English, revised (declaration plus answer row) | 25 / 40 | 62.5% | 0 |

**Bar (a): FAIL.** The English arm needed at least 36/40 and a margin of six rows. It had 25/40 and a margin of five. **Bar (b): PASS.** No dependent answer was read as settled or checked in the 40 English responses. The bars are quoted verbatim in [`PRE-REGISTRATION.md`](PRE-REGISTRATION.md). The scores come from `uv run python docs/judgment-terms/jt-e1s/runner.py --score` on the 80 saved raw records. `tests/test_jt_e1s.py::test_saved_records_reproduce_the_gate_line` checks that they still reproduce.

**By class, English arm against identifier arm:**

| Class | English | Identifier |
|---|---:|---:|
| settled | 10/10 | 10/10 |
| conditional | 9/10 | 10/10 |
| turns | 6/20 | 0/20 |

**Template and fallback rows.** On the 32 template rows, English scored 21/32 and identifier 16/32. The fallback rows U17–U20 and C17–C20 had identical display bytes in both arms. Each arm scored 4/8 on them, the same as JT-E1r. These rows give no evidence of a wording advantage.

**The misses.**

- **Identifier arm.** The 20 identifier misses are exactly the 20 `turns` rows. Each was read as CONDITIONAL with the right decider: JT-E1r's pattern again.
- **English arm, `turns` rows.** The answer row moved 6 of the 16 template `turns` rows to TURNS: U01, U09, U12, U13, U16 and C13. The other 10 stayed CONDITIONAL with the right decider: U04, U05, U08, C01, C04, C05, C08, C09, C12 and C16.
- **English arm, conditional row.** One conditional row, C07, regressed: the class was right but the decider was `NONE`. Its WHY line says the text does not show the judgment changing the result once the criterion is fixed.

**What the failure shows (an inference from the saved WHY lines, not evidence about human readers).**

- **The readers saw the answer row and still answered CONDITIONAL.** All 10 English template `turns` misses give a WHY that says the conclusion holds "only if" or "only given" the decider's judgment, or is "certified only given" it. Several also repeat that the two admissible completions differ.
- **They read a single judgment as a criterion.** They took the decider's judgment of one item to be the "judgment criterion" of the frozen prompt's CONDITIONAL definition. In this frame, 2.4's `Left to` wording does not separate TURNS from CONDITIONAL under that frozen prompt.
- **Where the overlap may lie.** The prompt and its class definitions were frozen word for word from JT-E1. So the result cannot tell how much of the overlap is in 2.4's wording and how much is in the prompt's definitions.

**Calls and charges.**

- **Calls.** All 80 calls reported `claude-sonnet-5-5` only, with successful CLI results and `fallback_credit: null`. No call failed or was retried.
- **Account.** The account picker selected `claude-panaali2` for all 80.
- **Charge.** The runner charged **1,185,742 CW** from the four reported usage fields, below the 3M cap. The 80 calls are below the 100-call cap.
- **Raw records.** The full prompts, CLI wrappers, answers and usage are in [`raw/`](raw/).
