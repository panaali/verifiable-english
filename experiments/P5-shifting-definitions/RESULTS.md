# P5 results — revision 8

**No dev or scored inference has run.** Material readiness is separate from
empirical efficacy. The 2026-09-22 orchestrator amendment drops the independent
paraphrase requirement after unsuccessful v6/v7 attempts.

Judges read **generator-rendered topological prose from the same VE graphs**.
This makes the VE arm's formalisation easier than on independently authored
prose and is a limitation on the comparison and its generalization. VE must
still author its own formalisation; the VE repair call is charged when used.
The tail-placement localisation fix is retained.

| Material stage | Accepted slots | Completed calls | Completed charges | Infrastructure/interruption holds |
| --- | ---: | ---: | ---: | ---: |
| Failed v6 rewrite, retained | 0/84 | 168 | $0.1597614352 | $0.0041484288 |
| Constrained v7 rewrite, retained | 2/84 | 167 | $0.1770597638 | $0.0290390016 |

v7 had 165 violations: 97 unsupported inference syntax, 38 changed atomic
phrases, 26 insufficient rewrite/changed licensing, 4 unparsed premises. These
attempts remain evidence and costs; they are not the adopted prose.

The historical round-5 Claude Opus blind material report says READY, with
84/84 kind and localisation recovery. Its original partial submission failed
the old importer; acceptance is now explicitly at report level. Round 6
confirms fidelity and no kind leak but is unblinded and found the subsequently
fixed tail-location shortcut. All current claims match round 5 except the
relocated conditional tail; source and localisation gates verify the change.
The earlier 768/1,024-token review attempt halted at 1,068 billed output tokens,
leaving five complete accepted reviews and $0.144180 in accounted costs.
The dated thinking-budget amendment raises both the wire output cap and billed
halt threshold to 4,096. Historical calls and charges remain in the ledger.

### Final 4,096-token review outcome (2026-09-22)

| Category | Packets |
| --- | ---: |
| (a) Completed and ACCEPTED (`ready=true`, no issues) | 83 |
| (b) Completed and flagged a material defect | 1 |
| (c) Incomplete/unreviewed | 0 |

Five complete historical reviews were reused unchanged. The continuation made
79 new calls, all ending in `STOP`, with at most 1,665 billed output tokens.
There were no new infrastructure failures or pending reservations. This task
spent **$1.129784 of its $1.50 authorization**. Cumulative review accounting is
**$1.273964**: $1.254676 across 88 completed calls plus the retained $0.019288
infrastructure hold. Old ledger bytes, truncated responses and halts are intact.

**Defect group — unintended extra meaning shift**

Packet `ib9279ca87379a78c8da58ec68a9d4b42`:

> Contains multiple meaning shifts (one on 'free' at n20, and another on 'clear' between n05 and n03), which is an unintended extra flaw.

This is Gemini's reported defect, retained without retry or reinterpretation.
**Dev is BLOCKED and was not started.** The review gate is not cleared.

Material acceptance is distinct from agreement with the reference diagnosis.
Five ready/no-issues reviews called reference-benign packets shifts:
`i17fe028fca21d694ebe499666730b759`, `i2e2c86f4cdc3bc257bbd62ae18da8f55`,
`i55908f495028f09871bca06b09ab1c3c`, `i65def4f39ff74a9f99bff1cce8d7d954`, and
`i9af8492c5aae07aa22ae6deeb7185eb6`. These remain counted in (a), not relabelled
as explicit material-defect reports. The existing diagnosis-agreement gate is
retained; 78/84 meet both acceptance and diagnosis criteria. Full reviewer
texts and reference comparisons are in `checks/gemini-rendered-resume-audit.json`.
Exact category counts and defect groups are in `checks/gemini-rendered-status.json`.

The blocked execution snapshot is refreshed for these final artifacts. No new
ready-to-run external timestamp is requested while the review gate fails; the
previous timestamp remains historical evidence. Resolving the material defect
and diagnosis disagreements, then refreshing the freeze and its timestamp, is
required before dev can pass its existing gates.


Registered dev feasibility, scored localized detection and VE−X interval,
benign completion, harm criteria, other arms/judges, UNKNOWN/failure rates,
actual per-arm costs and sensitivity intervals remain **unfilled**. Apply
registered outcome rules only after all gates and separate scoring authorization.
