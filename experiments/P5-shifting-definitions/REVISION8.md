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
