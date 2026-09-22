# Revision 7 handoff — constrained rewrite

Worker X prepared this amendment offline, with **$0 new spend**. The orchestrator
subsequently began v7 Qwen generation and was interrupted after nine completed
calls and one unresolved reservation. Reconciliation charges that reservation
at its full **$0.0020742144** ceiling, making v7 accounted cost **$0.0112893440**
with **$0.3887106560** left in its $0.40 envelope. This is conservative accounting
of an earlier call, not new provider spend or an audited invoice amount. No
Gemini review, dev or scored call is performed in this recovery. v7 uses the
unchanged v6 source dossiers and construction layout.

The v6 run completed 168 attempts across 84 slots, accepting none. The retained
ledger records $0.1597614352 in completed-call charges (about $0.16), plus its
original infrastructure records/holds. Its SHA-256 is
`bec35903f6e7b5e003c974e91db13a30eda7c49602033830e9ae4a75c480e95a`.
It remains at `runs/revision-v6/paraphrase-costs.jsonl`; no failed bill is removed
or refunded by this amendment. Raw responses and both attempts per slot remain
there even after v7 replaces the current material output archive.

The v7 pass independently re-structures prose with atomic claims verbatim;
it is **not a free paraphrase**. Acceptance masks each exact `unitN is <predicate>`
phrase with `#`, then measures character Levenshtein distance divided by the
longer masked string's length. Threshold: **0.20** across the ordered packet.
Other text is not case-folded or whitespace-normalized; step-ID markers are
absent from both compared strings. Every atom occurrence and unit name must be
preserved at its source step. Ordered step contents and conditional alternatives
must agree, and the public-record licensing search must recover the identical
readings, kind and localization. ID/gloss sanitation and validation still apply.

The parser accepts premise/conclusion reordering, split/merged premise sentences,
active/passive discourse frames and conditional-alternative reframing or movement
within its step. It conservatively rejects unparsed substantive text. A new
predicate synonym cannot earn distance or replace an atomic phrase. The prompt
provides supported framing examples. Source graphs/labels never reach Qwen.

Run from the repository root, with the operator's existing OpenRouter key:

```sh
export UV_CACHE_DIR=/private/tmp/ve-uv-cache-codex
uv run python experiments/P5-shifting-definitions/run_p5.py preflight-openrouter --offline
uv run python experiments/P5-shifting-definitions/run_p5.py paraphrase --revision v7 --cap-usd .40
```

Repeat the same paraphrase command to resume. `rewrite-v7/` identities and
`runs/revision-v7/paraphrase-costs.jsonl` isolate the re-buy from v6. The **$0.40
cumulative cap** includes failures and the single correction allowed per slot;
it never resets on resume. The study ledger retains the old v6 envelope and
reserves the additional v7 envelope under the unchanged $40 ceiling. Completed
responses are revalidated from the ledger without another call; terminal slots
are checkpointed individually. After stopping an interrupted caller, run
`uv run python experiments/P5-shifting-definitions/run_p5.py reconcile`.
The dated interrupted-call amendment charges every outstanding reservation in
the study and revision ledgers at its full ceiling, without inventing a response
or counting a trial. It allows the identical request to be re-issued and charges
the retry separately; the cumulative caps never reset. Completed-response
validation halts still require their existing recovery. Do not regenerate
sources between invocations.

After generation, this check makes no provider calls:

```sh
uv run python -m experiments.p5_revision check
```

All 84 accepted rewrites still require the registered independent review,
current packet hashes, refreshed counts, leakage gates, freeze and timestamp
before scoring. Gemini review now uses a separate v7 namespace and ledger;
preparing this handoff does not dispatch it. RESULTS.md is an unfilled reporting
template, not a result or evidence that the rewrite/review gate has passed.

Offline validation: `uv run pytest -q tests/test_p5*.py` passed **143 tests**.
Pinned native-tokenizer counts of all 84 exact v7 initial requests ranged from
**1,904 to 2,621 input tokens**, below the unchanged 4,096 cap. These checks made
no provider calls. Synthetic acceptance fixtures cover all 84 source packets;
they are not paid rewrites or independent review evidence.
