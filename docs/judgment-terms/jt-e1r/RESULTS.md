# JT-E1r fresh-item proxy readability result

**JT-3 wording gate FAIL.** This is proxy evidence from Sonnet 5.5, not human comprehension. A human reader audit remains a separate acceptance item. JT-E1's invalid numerical PASS is not carried forward.

| Arm | Fully correct | Rate | Critical misreadings |
|---|---:|---:|---:|
| Main renderer identifier fallback | 20 / 40 | 50% | 0 |
| Section 2.4 generated English | 20 / 40 | 50% | 0 |

Bar (a), **FAIL**: the English arm needed at least 36/40 and a margin of six rows; it had 20/40 and a margin of zero. Bar (b), **PASS**: no dependent answer was read as settled or checked in the 40 English responses. The two bars are quoted verbatim in [`PRE-REGISTRATION.md`](PRE-REGISTRATION.md). The scores are from `UV_CACHE_DIR=/tmp/jt-e1r-uv uv run python docs/judgment-terms/jt-e1r/runner.py --score` on the 80 saved raw records.

Fallback rows U17–U20 and C17–C20 had identical saved display bytes in both arms: 4/8 correct in each. Accepted-template rows were 16/32 correct in each. The fallback rows give no evidence of a wording advantage. `render.audit()` recomputes all saved display bytes from the frozen generator and real VE renderer; `tests/test_jt_e1r.py::test_frozen_frame_and_real_capture_bytes` runs that check. The control display is the stdout of the saved `ve render --view ve_english` command, not an answer-key line.

The same 20 row IDs were incorrect in both arms: U01, U04, U05, U08, U09, U12, U13, U16, U17, U20, C01, C04, C05, C08, C09, C12, C13, C16, C17, C20. Every one had a `turns` key and was classified `CONDITIONAL`; the ten settled and ten conditional rows were classified correctly. There were **zero critical misreadings** under the frozen definition, because none was called settled or checked. This pattern is a failure of the intended class discrimination, even though bar (b) passes. It is an inference from the saved classifications, not evidence about human readers.

All 80 calls reported `claude-sonnet-5-5` exclusively, successful CLI results and `fallback_credit: null`; the account picker selected `claude-danielsaeedi37` for all 80. The runner charged **1,191,512 CW** from the four reported usage fields, below the 3M cap; 80 is below the 100-call cap. The `--score` output and the raw-record summary command in [`REPORT.md`](REPORT.md) reproduce the counts. Full prompts, CLI wrappers, answers and usage are in [`raw/`](raw/). No model call failed or was retried.

The plan's one wording revision and rerun on a fresh frame is a follow-up; no revision was applied to this frozen experiment.
