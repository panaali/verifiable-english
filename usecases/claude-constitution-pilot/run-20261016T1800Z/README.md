# Run 20261016T1800Z: Claude constitution pilot at `ve-green-trust-ties-rd9`

Read `SUMMARY.md` first, then `AUDIT-REPAIR.md` and `FEATURE-REVIEW.md`. `prev/` holds the previous run's (20261016T0600Z) ledger, metrics, check, coverage, translation, probe results, rendering, `AUDIT-REPAIR.md`, `FEATURE-REVIEW.md` and `SUMMARY.md`, which this run starts from and compares with. `base/` holds the inputs of earlier runs' repair scripts (kept because the scripts import each other). `AUDIT-20261016T0600Z-received.md` is the audit of the previous run (20/20 sampled and 8/8 changed units faithful, small faults listed); the earlier `AUDIT-*-received.md` files are kept. The pinned source is `../source/` (`SOURCE.md` has the SHA-256 and fetch date; copied from `manage-agents/pilots/claude-constitution/source/`); it is never edited.

This run gives no unit a new status or meaning. It re-measures the carried translation at the new tag, repairs the small faults the audit recorded in ledger texts (seven changed units, `AUDIT-REPAIR.md`), re-asserts the plan additions' shapes, regenerates the tag-only ledger annotations, and probes the soft chain (rd-9) as a native form of the three "should" sets (`FEATURE-REVIEW.md`).

| File | What it is |
|---|---|
| `translation.ve.md`, `units.json` | the main document (byte-identical to `prev/translation.ve.md`) and ledger (1,132 units, every byte of the 184,893-byte source in exactly one). Four reading sets with Lean-checked content (three “should” sets and the scope set of u0165.s03, whose candidates have their own attitude terms: 16 choices, no coupling); each hard constraint has one strict rule (u0165.s03: two candidates) with guard `( C(s) and knowingly_engages_N(c, s) ) or thinks_quite_likely_N(c, s)` |
| `translation-without-content.ve.md`, `readings/all-strict.ve.md`, `readings/all-strict-narrow.ve.md` | the translation with the four sets as pending candidates (input of `nd.py`), the strict companion and the same with u0165.s03 narrow (used by the probes) |
| `readings/nd-all-result.json`, `nd-all-check.json`, `coverage-nd-all.json` | `nd.py all`: the translation rebuilt (`readings/nd-all.ve.md`, cmp-identical to `translation.ve.md`), its check, separating situations and coverage |
| `readings/soft-chain.ve.md`, `evidence/soft-chain-probe.json`, `probe_soft_chain.py` | the soft-chain probe: the three “should” sets as default rules with an unstated exception (a measurement document, not the translation); its load, coverage, render, conclusion queries, and the failure of `ve document check` |
| `metrics.json` | bytes accounted, unit counts by status (new units and aggregated to the 299 old boundaries), claimed and audit-verified bytes, `changed_units` (7), `plan_repairs`, `audit_repairs`, open terms, reading sets, missing-feature tally, check verdicts, probes, `scope_tally`, `act_workaround_m4`, `vocabulary_change_check`, `ledger_only_open_terms`, `english_round_trip`, `language_changes_since_previous_tag`, `soft_chain_probe`, `separation_line_gap_sentences`, `profile_combination_probe_changes`, `question_probe` |
| `scope-tally.json` | SC-M0: every governor, its reach and effect, what it governs, bytes; totals by reach and effect |
| `evidence/m4-act-workaround.json` | AP-0 item 3: the act-phrases evidence the `act_workaround` tags are copied from |
| `rendered.md`, `rendered-raw.md`, `check.json`, `coverage.json` | the rendering (`rendered.md` adds the source words and VE's verdicts under each hard constraint), the raw `ve document render`, `check` and `coverage` |
| `probes/` | the six carried probes (five byte-identical to `prev/probes/`; `s1-probe.json` differs in point (c)), `unspecified-probe.json` (byte-identical), `hard-conclusions-probe.json` and `nd/hard/` (21 conclusion queries), `nd/` (denial and claim-human conclusions), `companion/`, `ask/` |
| `repair_20261016T1800Z.py`, `finish_20261016T1800Z.py`, `probe_soft_chain.py`, `nd.py` | this run's scripts (`repair_20261016T1800Z.py` only asserts and writes nothing; the ledger repairs are in `finish_20261016T1800Z.py` `repair_ledger`); the other scripts are earlier runs' kept because they import each other |

Reproduce (repository root; `lake build` in `lean/` and `python3 tools/rust_build.py` done):

    export PATH=~/.elan/bin:$PATH VE_NATIVE_PREBUILT=1
    R=usecases/claude-constitution-pilot/run-20261016T1800Z
    uv run python $R/repair_20261016T1800Z.py            # asserts the carried documents (AT-0p shape, no stale terms, noun “thing”, corrected admission texts)
    uv run python $R/nd.py all                           # about 2 min
    cmp $R/readings/nd-all.ve.md $R/translation.ve.md    # identical
    uv run python -m ve document coverage $R/translation.ve.md > $R/readings/coverage-nd-all.json
    # probes: s1 and rights read earlier runs' soft companions (copy run-20261008T1800Z/readings/{all-default,s1}.ve.md in, run, remove)
    for p in unspecified s1 risk discourse rights senses senses_doc; do uv run python $R/probe_$p.py; done
    uv run python $R/probe_companions.py
    N=$R/probes/nd   # ve document readings $R/translation.ve.md --conclusion $N/conclusion-no-denial.json  (and conclusion-no-claim-human.json)
    # ve ask $R/translation.ve.md "<question>" --reading --json   (probes/ask/q*.json; without --reading: q*.answer.json)
    uv run python $R/probe_hard_conclusions.py           # 21 queries, 3 in parallel, about 24 min (all answered on the first run at the default Rust limit)
    uv run python $R/probe_soft_chain.py                 # about 3 min
    uv run python $R/finish_20261016T1800Z.py            # ledger (units.json), scope-tally.json, renderings, check, coverage, metrics.json
