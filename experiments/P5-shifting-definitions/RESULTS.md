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
Fresh Vertex Gemini 3.1 Pro review produced **5 valid current-packet reviews**,
all ready and all agreeing with the source kind/localisation. Nine completed
provider calls cost **$0.124892**; one infrastructure hold adds **$0.019288**,
for **$0.144180** accounted against the cumulative $1 cap. Initial 768-token
and continued 1,024-token requests encountered truncated JSON; the final call
reported **1,068 billed output tokens against its 1,024 ceiling**, causing a
durable provider validation halt. The raw answers, failed calls and recovery
record remain in `runs/revision-v8/gemini-review-costs.jsonl`.

**The review gate is BLOCKED: 79/84 slots lack an accepted current Gemini
review.** The historical Claude report is accepted under the amendment; the
Gemini policy is implemented, but a partial run is not represented as approval
of all material. No further generation or dev/scored inference is dispatched
through the validation halt. See `checks/gemini-rendered-status.json` and
`checks/review.json` for the exact current status.

Registered dev feasibility, scored localized detection and VE−X interval,
benign completion, harm criteria, other arms/judges, UNKNOWN/failure rates,
actual per-arm costs and sensitivity intervals remain **unfilled**. Apply
registered outcome rules only after all gates and separate scoring authorization.
