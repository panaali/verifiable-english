# Round-5 handoff

Worker generation spend: **$0**. Scenario: `dual_judge`; study cap: **$40**.
The independent verifier reports soundness/localization 84/84, zero invalid
packets and leakage at the permutation null. This is materials evidence.

The supplied `completed-review.json` is preserved byte-for-byte in
`checks/round5-review-submission.json`. The requested import was attempted and
rejected for sibling exposure. It contains 30 partial annotations, no packet
hashes, and no sense mappings, root meanings or source evidence. Its original
model metadata differs from the operator's specified attribution, which is
recorded separately as **Claude Opus 4.x subagent, cross-family, blind** in
`checks/round5-review-import.json`. No reviewer identities or annotations were
invented. Two independent complete reviews per final packet, including a
human/project lead, remain required; adjudication is not yet eligible.

The four bulk material archives and the preserved external review files are
explicitly barred. P5 tests cover the archive list, compressed label detection
and binary timestamp receipts. `MATERIALS-HASHES.txt` hashes the material
manifest, preregistration, amendments and original submission; its `.ots` is
also bound into the freeze. The separate `freeze-manifest.sha256.ots` binds
the execution freeze under the existing preflight policy. Calendar receipts
are pending Bitcoin confirmation.

## Orchestrator commands and caps

These commands are for the orchestrator only. Caps are cumulative study-ledger
limits, rounded upward to cents, derived from `execution-inventory.json` and
the frozen stage token/rate schedule. They are not fresh per-command budgets.

```sh
cd /Users/seyran/code/ve-codex
export UV_CACHE_DIR=/private/tmp/ve-uv-cache-codex
export UV_TOOL_DIR=/private/tmp/ve-uv-tools-codex
```

1. Independent Qwen pass (`qwen/qwen-2.5-72b-instruct`): 84 calls, 4096 input /
   1024 output tokens per call, block ceiling **$0.1669742592**. The runner
   requires a Qwen smoke receipt before paraphrasing, so bootstrap it first:

```sh
uv run python experiments/P5-shifting-definitions/run_p5.py preflight-openrouter --cap-usd 0.01
uv run python experiments/P5-shifting-definitions/run_p5.py paraphrase --cap-usd 0.17
```

The smoke ceiling is $0.0004807424; combined ceiling is $0.1674550016.
The OpenRouter-only smoke returns exit 2 while the overall provider gate still
awaits Gemini; inspect `models.replication.passed` before proceeding.

**Before proceeding:** obtain complete independent reviews of all final Qwen
packets and resolve any disagreements; rerun free token counts; regenerate
MATERIALS-MANIFEST.json and MATERIALS-HASHES.txt, archive prior timestamp
receipts, stamp the new bundle, refreeze, and stamp the new freeze hash.
Run preflight on those final bytes. The current timestamps/reviews cannot
approve rewritten packets. No gate bypass is authorized.

2. Refresh the OpenRouter receipt for that final freeze (the unchanged smoke
   request reuses its durable result):

```sh
uv run python experiments/P5-shifting-definitions/run_p5.py preflight-openrouter --cap-usd 0.17
```

3. Gemini + Qwen infrastructure probe, with the requested **$1 cap**:

```sh
uv run python experiments/P5-shifting-definitions/run_p5.py probe --cap-usd 1
```

The two unique smoke calls cost at most $0.0130247424 together; cumulative
paraphrase + smokes ceiling is $0.1799990016.

4. Dev, after every prerequisite gate passes:

```sh
uv run python experiments/P5-shifting-definitions/run_p5.py dev --cap-usd 5.24
```

Dev block ceiling: $4.919556144. Including materials, smokes and the reserved
$0.1344 CPU envelope, cumulative ceiling: $5.2339551456. Dev always requires
source-fidelity review; contract compliance alone does not open scoring.

5. Scored, after the dev source-fidelity/compliance gate is accepted against
   this exact freeze:

```sh
uv run python experiments/P5-shifting-definitions/run_p5.py scored --cap-usd 34.76
```

Scored block ceiling: $29.517336864. All-in cumulative ceiling:
**$34.7512920096**, leaving **$5.2487079904** under $40. Unknown billing,
infrastructure holds or changed materials require explicit reconciliation;
these ceilings do not silently fund retries or replacement samples.
