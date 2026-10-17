# Run 20261017T1800Z: Claude constitution pilot at `ve-green-fu-ar2-decoders`

Read `SUMMARY.md` first, then `AUDIT-REPAIR.md` and `FEATURE-REVIEW.md`. `prev/` holds the previous run's (20261017T0600Z) ledger, metrics, check, coverage, translation, probe results, rendering, `AUDIT-REPAIR.md`, `FEATURE-REVIEW.md` and `SUMMARY.md`, which this run starts from and compares with. `base/` holds the inputs of earlier runs' repair scripts (kept because the scripts import each other). `AUDIT-20261017T0600Z-received.md` is the audit of the previous run (24 of 25 verdicts faithful, u0156.s03 unfaithful: readings incomplete; two small faults); the earlier `AUDIT-*-received.md` files are kept. The pinned source is `../source/` (`SOURCE.md` has the SHA-256 and fetch date; copied from `manage-agents/pilots/claude-constitution/source/`); it is never edited.

This run gives no unit a new status or meaning from the language (the two merged batches change tests, tools and reports only). It repairs what the audit found: u0156.s03's reading set gets two candidates scoped to the situation of u0156.s01 (`frame_u0156.py`), u0165.s06 records its governor u0186.s01, and the notes of the three "should" units state the right count of choices. It re-asserts the plan additions' shapes and regenerates the tag-only ledger annotations.

| File | What it is |
|---|---|
| `translation.ve.md`, `units.json` | the main document (differs from `prev/translation.ve.md` in the reading set of u0156.s03, the frame term `asked_to_keep_system_prompt_confidential`, and the record of `illegitimate_absolute_control`) and ledger (1,132 units, every byte of the 184,893-byte source in exactly one). Four reading sets with Lean-checked content (the three “should” sets, u0156.s03's with four candidates, and the scope set of u0165.s03): 32 choices, no coupling; each hard constraint has one strict rule (u0165.s03: two candidates) with guard `( C(s) and knowingly_engages_N(c, s) ) or thinks_quite_likely_N(c, s)` |
| `frame_u0156.py` | the one owner of u0156.s03's four candidates: names, wording, admission sentences, the guard |
| `translation-without-content.ve.md`, `readings/all-strict.ve.md`, `readings/all-strict-narrow.ve.md`, `readings/all-strict-in-frame.ve.md` | the translation with the sets as pending candidates (input of `nd.py`), the strict companion, the same with u0165.s03 narrow, and with u0156.s03 as the strict-in-frame rule (English, silence sentence, `probe_frame.py`) |
| `readings/nd-all-result.json`, `nd-all-check.json`, `coverage-nd-all.json` | `nd.py all`: the translation rebuilt (`readings/nd-all.ve.md`, cmp-identical to `translation.ve.md`), its check, separating situations and coverage |
| `readings/soft-chain.ve.md`, `evidence/soft-chain-probe.json`, `probe_soft_chain.py` | the soft-chain probe: the “should” sets' default candidates (including default-in-frame) as default rules with an unstated exception (a measurement document, not the translation) |
| `metrics.json` | bytes accounted, unit counts by status (new units and aggregated to the 299 old boundaries), claimed and audit-verified bytes, `changed_units` (4), `plan_repairs`, `audit_repairs`, open terms, reading sets, missing-feature tally, check verdicts, probes, `frame_probe`, `scope_tally`, `act_workaround_m4`, `vocabulary_change_check`, `seeded_bugs`, `language_changes_since_previous_tag` |
| `scope-tally.json` | SC-M0: every governor, its reach and effect, what it governs, bytes; totals by reach and effect |
| `evidence/m4-act-workaround.json` | AP-0 item 3: the act-phrases evidence the `act_workaround` tags are copied from |
| `rendered.md`, `rendered-raw.md`, `check.json`, `coverage.json` | the rendering (`rendered.md` adds the source words and VE's verdicts under each hard constraint), the raw `ve document render`, `check` and `coverage` |
| `probes/` | the six carried probes (byte-identical to `prev/probes/`), `unspecified-probe.json` (byte-identical), `frame-probe.json` (new), `hard-conclusions-probe.json` and `nd/hard/` (21 conclusion queries), `nd/` (denial and claim-human conclusions), `companion/`, `ask/` |
| `repair_20261017T1800Z.py`, `finish_20261017T1800Z.py`, `probe_frame.py`, `probe_soft_chain.py`, `nd.py` | this run's scripts (`repair_20261017T1800Z.py` writes the two new pending candidates, the u0186.s01 record and the in-frame companion, and refuses a second run; `--check` asserts the finished translation; `nd.py` gives the four candidates their content, declares the frame term and the unit's meaning); the other scripts are earlier runs' kept because they import each other |

Reproduce (repository root; `lake build` in `lean/` and `python3 tools/rust_build.py` done):

    export PATH=~/.elan/bin:$PATH VE_NATIVE_PREBUILT=1
    R=usecases/claude-constitution-pilot/run-20261017T1800Z
    uv run python $R/repair_20261017T1800Z.py            # once, on the carried documents
    uv run python $R/nd.py all                           # about 4 min
    cp $R/readings/nd-all.ve.md $R/translation.ve.md
    uv run python $R/repair_20261017T1800Z.py --check
    uv run python -m ve document coverage $R/translation.ve.md > $R/readings/coverage-nd-all.json
    # probes: s1 and rights read an earlier run's soft companions (copy run-20261008T1800Z/readings/{all-default,s1}.ve.md in, run, remove)
    for p in unspecified s1 risk discourse rights senses senses_doc; do uv run python $R/probe_$p.py; done
    uv run python $R/probe_companions.py; uv run python $R/probe_frame.py
    N=$R/probes/nd   # ve document readings $R/translation.ve.md --conclusion $N/conclusion-no-denial.json  (and conclusion-no-claim-human.json)
    # ve ask $R/translation.ve.md "<question>" --reading --json   (probes/ask/q*.json; without --reading: q*.answer.json)
    uv run python $R/probe_hard_conclusions.py           # 21 queries, 3 in parallel, about 60 min at this load (all answered on the first run at the default Rust limit)
    uv run python $R/probe_soft_chain.py                 # about 5 min
    uv run python $R/finish_20261017T1800Z.py            # ledger (units.json), scope-tally.json, renderings, check, coverage, metrics.json
