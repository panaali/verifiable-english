# Revision 8: reviewed generator-rendered prose

The 2026-09-22 orchestrator amendment drops independent paraphrasing and accepts
the historical round-5 Claude material report plus a fresh isolated Gemini
review of every current packet. Round 6 remains unblinded supporting evidence.
The old reports, failed v6/v7 attempts and all billing records remain intact.
Current prose equals round 5 except for the retained conditional-tail relocation.

```sh
export UV_CACHE_DIR=/private/tmp/ve-uv-cache-codex
uv run --offline python -m experiments.p5_rendered prepare
uv run --offline python experiments/P5-shifting-definitions/run_p5.py freeze --scenario dual_judge
uv run --offline python -m experiments.p5_rendered gemini-review --cap-usd 1.644180
```

The review cap is cumulative and the command reuses completed replies. Review
issues, malformed replies, billing uncertainty and cap exhaustion cannot become
approvals. Refresh free counts (`inventory --count-tokens`), review, material
hashes, freeze and OpenTimestamps receipt, then rerun `preflight --offline` and
`probe --offline`. No dev/scored dispatch is part of this authorization.

Historical outcome before the 4,096-token amendment: Claude report accepted; Gemini has 5/84 accepted current
reviews and halted after exceeding the 1,024 billed-token cap. Accounted
review spending is $0.144180. The following dev command remains blocked
by the review gate. It is not executed in this revision.

After every pre-dev gate passes, under separate paid dev authorization:

```sh
UV_CACHE_DIR=/private/tmp/ve-uv-cache-codex uv run --offline python experiments/P5-shifting-definitions/run_p5.py dev --cap-usd 40
```

`uv --offline` prevents package downloads; the dev command itself calls paid
providers. A positive cap does not bypass any review or offline evidence gate.


2026-09-22 thinking-budget continuation: material reviews now request and halt
at 4,096 total billed output tokens, including thinking. The cumulative review
cap is $1.644180: $0.144180 prior spending plus this task's $1.50 authorization.
Ledger reconstruction reuses every complete untruncated review, including
negative judgments. Only incomplete reviews are reissued. The machine-readable
submission and status reports distinguish acceptance, completed defect reports,
and incompleteness; exact defect text is grouped with packet IDs. The final outcome is recorded below. No dev call is part of this task.


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


### Mechanical adjudication (2026-09-22; supersedes the blocked snapshot above)

Worker X was explicitly authorized to adjudicate the one defect claim and five
diagnosis disagreements without paid calls. The exhaustive public-record search
from round-5 Claude's `p5v5.py`/`solve2.py` is reproduced in
`experiments/p5_licensing.py`, with a global relaxation budget, all successful
assignments retained, and safe immutable backtracking. The search uses public
records, declared premises and prose, not hidden graphs or reference labels.
Labels are consulted only after the search to check the recovered diagnosis.

The defect claim on `ib9279ca87379a78c8da58ec68a9d4b42` is **rejected**. There are
zero fully licensed assignments and two assignments with exactly one relaxation,
both at **n03**, the intended shift. At n05, r15 branch 3 establishes unit4 clear
(contamination absent); n03/r09 requires unit4 clear (optically transparent).
Thus the clear transition has no licensing reading. The alleged extra shift on
free at n20 is licensed: n16/r05 establishes unit0 free (space available), n06/r14
establishes unit0 free (fee waived), and r10 consumes these two senses explicitly.

All five documented reference-benign disputes have two complete zero-relaxation
assignments each; all five Gemini shift diagnoses are rejected. No family, seed,
packet, reference label or original Gemini judgment changes. The raw Gemini
status remains 83 accepted / 1 defect claim / 0 incomplete. The resolved review
gate has **84 accepted slots: 78 direct agreements and six adjudications**.

`checks/gemini-rendered-adjudication.json` binds each resolution to the current
packet and original review and includes every minimum-relaxation assignment.
The gate recomputes this evidence and still requires authentic billed reviews;
an edited review, stale witness, changed packet, or second flaw cannot pass.
The adjudication is frozen and barred from model-visible material. No dev or
scored call was executed; the dev command above requires paid authorization.
