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
uv run --offline python -m experiments.p5_rendered gemini-review --cap-usd 1
```

The review cap is cumulative and the command reuses completed replies. Review
issues, malformed replies, billing uncertainty and cap exhaustion cannot become
approvals. Refresh free counts (`inventory --count-tokens`), review, material
hashes, freeze and OpenTimestamps receipt, then rerun `preflight --offline` and
`probe --offline`. No dev/scored dispatch is part of this authorization.

Current outcome: Claude report accepted; Gemini has 5/84 accepted current
reviews and halted after exceeding the 1,024 billed-token cap. Accounted
review spending is $0.144180. The following dev command remains blocked
by the review gate. It is not executed in this revision.

After every pre-dev gate passes, under separate paid dev authorization:

```sh
UV_CACHE_DIR=/private/tmp/ve-uv-cache-codex uv run --offline python experiments/P5-shifting-definitions/run_p5.py dev --cap-usd 40
```

`uv --offline` prevents package downloads; the dev command itself calls paid
providers. A positive cap does not bypass any review or offline evidence gate.
