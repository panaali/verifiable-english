# V4 A/B study

**B stopped on served-model drift at attempt 142.** `results/b/STOP.json` permanently blocks resumption. One follow-on response and one interrupted identity are preserved but excluded. The frozen runner confused an allowed quota event with a rate error; current `run_b.py` fixes that bug. Its original preregistered bytes are preserved as `run_b-preregistered.py` and in commit `6d8525e`. HASHES/OTS were not rewritten; `results/b/prereg-verification.json` validates every original hash against that pre-run commit. Current runner bytes intentionally differ, requiring a new preregistration for any future study. C live smoke was withheld.

The full B study uses the fresh `items-b.jsonl` corpus and timestamped `PREREG-B.md`, frozen in commit `6d8525e` before any main-study calls. The previous infrastructure/smoke record is retained below for provenance. Its authorization and no-bulk-run statements describe the earlier task and are superseded by the current lead authorization and full B protocol.

```sh
# run_b.py now refuses to resume this stopped study. Offline reporting:
UV_CACHE_DIR=/private/tmp/ve-uv-cache-v4 uv run python experiments/V4-fidelity/analyze_b.py
UV_CACHE_DIR=/private/tmp/ve-uv-cache-v4 uv run python experiments/V4-fidelity/report_b.py
```

The live command is capped at 180 started identities and resumes successes without resampling failures. Date/host/binary/model/content-count drift must stop the study. The original protocol and runner hashes remain frozen. Reports and complete raw evidence are in `results/b/`; the new ten-call fixed-context audit is `results/endpoint-controlled.jsonl`. Step C lives in `../V4-calibration/`; only the Haiku engineering smoke is part of this task.

## Historical infrastructure notes (before main-study authorization)

# V4 A/B infrastructure

Scope: isolated `claude -p` backend, 60-item formalisation audit, scoring and preregistration. No calibration, debate, bulk inference, API replication, or frontier-benefit result.

Run from this worktree, serially:

```sh
export UV_CACHE_DIR=/private/tmp/ve-uv-cache-v4
uv run pytest -q tests/test_v4_infrastructure.py
uv run python experiments/V4-fidelity/fidelity.py generate
# Authorized live runs are already recorded; inspect results before any new call.
uv run python experiments/V4-fidelity/fidelity.py smoke
```

`smoke` resumes successful identities from its ledger; it never retries errors or interrupted attempts. It is hard-capped at three started identities. `ClaudeCLI.samples(item_id, system, prompt, k=3)` supports future replicates but is not a bulk-run authorization. A separate judge may select `Controls(model=MODELS["haiku"])` or `MODELS["sonnet"]`; only Opus was tested live.

## Artifacts

- `generator.py`, `provergen_rules.json`, `PROVENANCE.md`: public-generator adaptation and declared differences.
- `items.jsonl`, `manifest.json`: frozen English, gold VE ASTs, raw skeletons, E0 results, witness models, seed/hash and audit IDs.
- `PROMPT.md`, `fidelity.py`: fixed prompt, exact/checked-equivalence fidelity, predicate/binding/operator diagnostics and VE claim-graph verification. Only public vocabulary and English are sent to the author. The scorer normalizes trailing whitespace to one final newline before strict VE parsing; the original submission remains in the ledger.
- `PREREG-B.md`: local preregistration, 60 items/k=3 design, failure-inclusive analysis, 12-item human audit; external registration and human/model audits remain pending.
- `INDEPENDENT-AUDIT-PROMPT.md`: blinded independent judge prompt, not yet run.
- `results/`: resumable ledgers with intent and terminal rows, full stream-json, canary text, token counts and per-item scores.
- `../../ve_experiments/claude_cli.py`: endpoint controls and JSONL ledger. Credentials are read only from OAuth env, the credential file, or the Claude keychain entry, and only the access token is copied into the child environment. Credentials are never saved to the ledger.

## Endpoint gate and token interpretation

Pinned CLI `2.1.280 (Claude Code)`; the ledger pins its executable SHA-256, exact model id, thinking cap 1024, effort low, and output budget (6000 audit; 14000 smoke). Updater and SDK retries are disabled; no fallback model is requested. Each sample uses a fresh configuration/home and newly created empty temporary cwd. The final cwd has a fixed pathname to avoid random-path token variation; concurrent use fails safely if the path is occupied. User/project/local settings, memory, hooks, custom agents/skills/plugins and MCP servers are disabled; tools inventory must be empty. CLI built-in agent names still appear in init but have no callable tools; they are explicitly allowlisted. `--bare` is not used because this installed CLI disables subscription OAuth in bare mode.

Fresh-message input token totals include uncached, cache-created and cache-read input. The assertion compares identical content/config pairs; if independently counted exact system+user content tokens are supplied via `content_tokens`, it also asserts equal residual overhead across different prompts. The CLI exposes no exact separate tokenizer for the supplied content, so absolute wrapper overhead is **unmeasured**, not zero. Report the observed totals and their drift rather than inventing an absolute overhead number. Equal counts do not prove equal context or absence of provider instructions. Thinking usage is logged from `output_tokens_details`; fixed MAX_THINKING_TOKENS is a requested control, not a claim of API-equivalent internal reasoning.

The first ten calls used random temporary cwd names. Input totals varied and eight were rejected by the invariant. Two further canaries using the fixed cwd had equal counts; they are diagnostics, not a full five-plus-five revalidation. All 12 served Opus 5.5, tools/MCP empty. Canary self-reports show an SDK identity prefix and injected environment/model/date/token-budget text. Therefore the endpoint has **not passed a no-extra-context gate** and must not be treated as an API-equivalent scientific endpoint. The three B smoke calls demonstrate engineering feasibility only.

Before any bulk study: resolve the extra-context contract, perform the complete fixed-cwd audit, obtain exact content token counts if claiming absolute overhead, externally timestamp the preregistration, complete the English/gold human audit, arrange an independent judge/API replication, and confirm bulk subscription authorization. Do not auto-spend new calls to resolve these issues.
