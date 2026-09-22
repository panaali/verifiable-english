# D pilot

The timestamped `PREREG-D-pilot.md` defines the study. It was committed as
`5ac7071` before the content-free Opus gate. The gate served `claude-opus-5-5`.
`HASHES` freezes the executable main protocol before the first item exposure.
Its OpenTimestamps receipt is a calendar commitment pending Bitcoin confirmation.

Run from the repository root, serially:

```sh
UV_CACHE_DIR=/private/tmp/ve-uv-cache-v4 uv run python experiments/V4-D-pilot/run.py run
UV_CACHE_DIR=/private/tmp/ve-uv-cache-v4 uv run python experiments/V4-D-pilot/run.py summarize
```

No other process should use the backend's fixed empty working directory during
the run. The runner locks the pilot, reuses successful ledger samples on resume,
and refuses permanently after `results/STOP.json`. Never remove that stop marker
to continue a stopped study. A new protocol is required for a new run.

The checker is harness-mediated: an attack submission acts as a tool request;
the next fresh Opus call receives the actual formal result and preceding
submissions. The CLI itself has no tools enabled. Four candidates are generated
for every dishonest attack item. Only the selected candidate reaches a judge.
Gold-based eligibility is separate from the trusted checker report; judgments
never see it. There is no judge-feedback search or model-based item selection.

`checker.py` uses Python VE entailment proof replay, not Lean certification.
An implication graph is conditional on the consultant's English-to-VE table.
Certification never establishes that table's faithfulness. The system report
lists every unbound leaf and tells the judge explicitly to assess the translation.

The pilot excludes the C `uncertain` family to preserve binary entailment versus
refutation semantics. It has four fresh items from each of the other six families,
with True/False and honest/dishonest fully crossed in each family. It does not
reuse the calibration smoke items or select direct-QA failures.

480 judge samples and 192 physical argument calls are planned, plus the gate:
673 total. Honest arm-5 consultant material is reused from arm 4. The report
distinguishes physical spend from reused exposure and includes all attack attempts.
Argument budgets differ between arms; this is not a matched-token causal estimate.
Haiku uses a requested thinking cap of 1024, Sonnet has no thinking-cap environment
variable. Both retain the preregistered finite total-response ceilings.

Offline validation before the main run:

```sh
UV_CACHE_DIR=/private/tmp/ve-uv-cache-v4 uv run pytest -q tests/test_v4_d_pilot.py tests/test_v4_d_gate.py tests/test_v4_infrastructure.py tests/test_v4_calibration.py
```

This covers balance, gold proof replay, blinded prompts, a certified mistranslation,
unsupported leaves, source replacement, query mismatch, deterministic best-of-four
selection, missing-data denominators, uncapped Sonnet configuration, and permanent
stopping after endpoint mismatch. No model calls are made by these tests.
