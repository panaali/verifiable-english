# Revision 6 handoff

Source material is regenerated; Qwen rewriting and Gemini review await the
orchestrator's OpenRouter environment. No paid calls were made by Worker X.
The old Claude review was imported with its original hashes and its explicit
unblinded disclosure. A current-packet Claude review is still required.

Run from the repository root, with OPENROUTER_API_KEY supplied by the operator:

```sh
export UV_CACHE_DIR=/private/tmp/ve-uv-cache-codex
# After code changes, refresh the freeze and reuse the existing Qwen smoke ($0):
uv run python experiments/P5-shifting-definitions/run_p5.py freeze --scenario dual_judge
uv run python experiments/P5-shifting-definitions/run_p5.py preflight-openrouter --offline
uv run python experiments/P5-shifting-definitions/run_p5.py paraphrase --revision v6 --cap-usd .40
# Reject incomplete/failed rewriting before buying any review:
uv run python -m experiments.p5_revision check
uv run python experiments/P5-shifting-definitions/run_p5.py freeze --scenario dual_judge
uv run python -m experiments.p5_revision gemini-review --cap-usd 1
```

Both caps are cumulative in their own revision ledgers; they do not reset on
resume. Raw replies, failures and billing holds are retained. Do not regenerate
source material between paraphrase dispatch and review. The Gemini command
stops before paid work unless all 84 new paraphrases pass semantic and distance
checks. It retains raw reviews and never fills annotations using hidden labels.
If model annotations differ, the existing adjudication requirement applies.

Export the new hash-bound packets for Claude, import that review, then refresh
counts, final review/leakage gates, freeze and timestamp before dev. Old gate
receipts cannot authorize new packet bytes. See AMENDMENTS.md for the review
provenance conflict and the retained failed random-tail assignment.

Only after all preflight gates pass, under separate dev authorization:

```sh
UV_CACHE_DIR=/private/tmp/ve-uv-cache-codex uv run python experiments/P5-shifting-definitions/run_p5.py dev --cap-usd 40
```

## v6 provider routing fix

The retained rejection identifies a DeepInfra 504 followed by automatic fallback
to Novita, whose raw HTTP 400 reports `INVALID_REQUEST_BODY` and an unsupported
`completions` endpoint. The client already used `/api/v1/chat/completions` with
system and user messages. Automatic fallback was the failing route. Authoring
now pins DeepInfra and explicitly tries Novita only after HTTP 429, using the
same chat endpoint and messages. Qwen judge routing is unchanged.

On online v6 resume, a narrowly matched Novita endpoint panel halt receives an
append-only recovery record. Its full infrastructure billing hold remains;
completed responses and original request identities/messages remain intact.
Every cached response is revalidated for semantics and normalized edit distance
before acceptance; an invalid response follows the existing single correction
policy. No source regeneration or ledger deletion is needed.

Worker X's checkout at this fix contained 9 completed v6 calls, not the reported
14. A read-only audit found that none of those 9 passed the current semantic
acceptance check. They remain in the ledger as evidence. Offline regression
fixtures separately verify retention of 14 accepted calls and rejection of
cached copies or meaning changes. No paid calls were made for this fix.
