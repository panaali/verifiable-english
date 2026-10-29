# Answer-key freeze: openai-preparedness

| Field | Value |
|---|---|
| Frozen at | 2026-10-28T18:40:38Z (UTC), before any VE run on this case |
| Frozen by | dri-safetyfw (acting DRI), after the plan reviews converged |
| Key | [PLAN.md](PLAN.md) section 6, from the line starting `## 6. ` up to (not including) the line starting `## 7. `, joined with `\n` plus a final `\n`, UTF-8 |
| Section 6 SHA-256 | `6d1dd2a7729f789ea26212783fd49355ff3256110dc879c18e9f794b955ac522` (14710 bytes) |
| Items | 239 (PLAN section 5) |
| Reviews | gpt-6-astra xhigh and Opus xhigh, three rounds: FIX / FIX / ACCEPT each (`manage-agents/safetyfw-planreview{,-r2,-r3}-{astra,opus}.final.md`); dispositions in `manage-agents/reviews/safetyfw-plan-convergence-20261028.md` |

The freeze commit is the commit that adds this file. From here on no section-6 cell changes: a cell VE disagrees with
is a finding, recorded in PLAN section 12 (Deviations) with the source sentence. A test recomputes the hash above.
