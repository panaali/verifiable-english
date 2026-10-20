# Run 20261020T1800Z: Claude constitution pilot at `ve-green-sc-1ac`

Read `SUMMARY.md` first, then `AUDIT-REPAIR.md` and `FEATURE-REVIEW.md`. `prev/` holds the previous run's (20261020T0600Z) ledger, metrics, check, coverage, translation, probe results, rendering, scope tally and goals, which this run starts from and compares with. `base/` holds the inputs of earlier runs' repair scripts (kept because the scripts import each other). `AUDIT-20261019T1800Z-received.md` is the latest audit received (31 of 31 faithful); the run before this one is not audited yet. The pinned source is `../source/` (`SOURCE.md` has the SHA-256 and fetch date; copied from `manage-agents/pilots/claude-constitution/source/`); it is never edited.

This run upgrades nothing from the language (none of the ten merged batches lets a document say something new), repairs nothing (no audit fault on a covered unit), changes no unit, and carries the plans of the 18:00Z run of 20261018 (JT-0p, QT-0p, PS-0p, AT-0p, SC-M0, AP-0 item 3), which are in this run's prompt again, unchanged. No plan repairs; no product code (Lean, Python, Rust) was changed. `translation.ve.md` is byte-identical to the previous run's and `units.json` has no entry that differs from it.

| File | What it is |
|---|---|
| `translation.ve.md`, `units.json` | the main document and the ledger (1,133 units, every byte of the 184,893-byte source in exactly one). `translation.ve.md` is `readings/nd-all.ve.md` (cmp-identical), built by `nd.py all` from `translation-without-content.ve.md` (cmp-identical to `prev/translation-without-content.ve.md`) |
| `finish_20261020T1800Z.py` | the finish: builds `units.json`, `scope-tally.json` (carried), `presupposition-goals.json`, renderings, `check.json`, `coverage.json`, `metrics.json`, `evidence/new-profile-probe.json` (`scope@0`, `defaults@0`, `calc@0`, `acts@0`, `judgments@0`). Generated from `finish_20261020T0600Z.py` by text edits; earlier runs' `finish_*`, `ledger_*`, `repair_*` modules are reused |
| `rerun_queries.py` | re-runs the five `ve ask` questions and the four `ve document readings --conclusion` queries (denial, claim-to-be-human, fourth type, no fourth type) into `probes/` |
| `checkpoint.py` | the checks after a document change (wordings unchanged, the ```` ```ve ```` fences parse to the same formulas, `ve document check`, the two conclusion queries); output `evidence/checkpoint-final.json` |
| `seeded_bugs_20261020T1800Z.py`, `evidence/seeded-bugs.json` | the seeded faults of this run's claims and the failing check of each (no product code changed, so none in Lean, Python or Rust) |
| `owner_probe.py`, `evidence/owner-probe.json` | the probe of the three corrected unclaimed headings and the lower-case constant (re-run; byte-identical) |
| `evidence/` | `new-profile-probe.json`, `checkpoint-final.json`, `seeded-bugs.json`, `soft-chain-probe.json`, plus the carried `ps6r/`, `ps0p/`, `jt0p/`, `at0p/`, `m4-act-workaround.json`, `qt0p-*`, `companion-attribution.json` |
| `metrics.json` | bytes accounted, unit counts by status (new units and aggregated to the 299 old boundaries), claimed and audit-verified bytes, `changed_units` (none), `changed_units_previous_run_not_yet_audited` (3), `plan_repairs` (none), `feature_upgrades` (0), open terms, `open_term_class`, `judgment_term_units/bytes`, reading sets, missing-feature tally, check verdicts, probes, `quantities_qt0p`, `presupposition_ps0p` (incl. `prompt_tension`), `scope_tally`, `act_workaround_m4`, `vocabulary_change_check`, `seeded_bugs`, `language_changes_since_previous_tag` |
| `scope-tally.json`, `presupposition-goals.json` | SC-M0 (carried) and PS-0p step 6 |
| `rendered.md`, `rendered-raw.md`, `check.json`, `coverage.json` | the rendering (`rendered.md` adds the source words and VE's verdicts under each hard constraint), the raw `ve document render`, `check` and `coverage`; identical to the previous run's |
| `probes/`, `probe-*.out` | the carried probes (`unspecified-probe.json` has the four AT-0p points per rule), `qt/` (the fourth-type queries), `nd/` (`hard/`: 21 conclusion queries), `companion/`, `ask/` |
| the other scripts | earlier runs' scripts, kept because they import each other |

Reproduce (repository root; `lake build` in `lean/` and `python3 tools/rust_build.py` done; the Lean and Rust build products were copied from the `ve-integration` checkout at the identical commit):

    export PATH=~/.elan/bin:$PATH VE_NATIVE_PREBUILT=1
    R=usecases/claude-constitution-pilot/run-20261020T1800Z
    uv run python $R/nd.py all                           # cmp-identical to prev/translation.ve.md, about 4 min
    cp $R/readings/nd-all.ve.md $R/translation.ve.md; uv run python $R/checkpoint.py final
    uv run python $R/owner_probe.py
    # probes: s1 and rights read an earlier run's soft companions (copy run-20261008T1800Z/readings/{all-default,s1}.ve.md in, run, remove)
    for p in unspecified risk discourse rights senses senses_doc s1 companions frame; do uv run python $R/probe_$p.py; done
    uv run python $R/rerun_queries.py                    # five ve ask questions, four conclusion queries, about 6 min
    uv run python $R/probe_hard_conclusions.py           # 21 queries, 3 in parallel, about 36 min at this load
    uv run python $R/probe_soft_chain.py                 # about 11 min
    uv run python $R/seeded_bugs_20261020T1800Z.py
    uv run python $R/finish_20261020T1800Z.py            # ledger, scope tally, goals, renderings, check, coverage, metrics.json (about 8 min)
