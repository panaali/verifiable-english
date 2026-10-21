# Run 20261021T1800Z: Claude constitution pilot at `ve-green-ap-1b`

Read `SUMMARY.md` first, then `AUDIT-REPAIR.md` and `FEATURE-REVIEW.md`. `prev/` holds the previous run's (20261021T0600Z) ledger, metrics, check, coverage, translation, probe results, rendering, scope tally and goals, which this run starts from and compares with. `base/` holds the inputs of earlier runs' repair scripts (kept because the scripts import each other). `AUDIT-20261021T0600Z-received.md` is the latest audit received (29 of 30 verdicts faithful; one unfaithful, repaired here); this run is not audited yet. The pinned source is `../source/` (`SOURCE.md` has the SHA-256 and fetch date; copied from `manage-agents/pilots/claude-constitution/source/`); it is never edited.

This run upgrades nothing from the language (only `acts@0` is new and no document can use it yet), repairs the one unit the latest audit marked unfaithful (u0156.s03), carries the plans of the 18:00Z run of 20261018 (JT-0p, QT-0p, PS-0p, AT-0p, SC-M0, AP-0 item 3) unchanged, and changes no product code (Lean, Python, Rust). `changed_units` in `metrics.json`: u0156.s03; `plan_repairs`: none.

| File | What it is |
|---|---|
| `translation.ve.md`, `units.json` | the main document and the ledger (1,133 units, every byte of the 184,893-byte source in exactly one). `translation.ve.md` is `readings/nd-all.ve.md` (cmp-identical), built by `nd.py all` from `translation-without-content.ve.md` |
| `repair_20261021T1800Z.py` | the document change of this run, applied to `translation-without-content.ve.md` and the strict companions in `readings/` (the second argument of `system_prompt_deception_permitted` is a situation; the in-frame companion is rebuilt); `frame_u0156.py` and `nd.py` own the frame term and the exception term |
| `finish_20261021T1800Z.py` | the finish: applies the ledger repair, builds `units.json`, `scope-tally.json` (carried), `presupposition-goals.json`, renderings, `check.json`, `coverage.json`, `metrics.json`, `evidence/new-profile-probe.json`. Generated from `finish_20261021T0600Z.py` by edits; earlier runs' `finish_*`, `ledger_*`, `repair_*` modules are reused |
| `checkpoint.py` | the checks after a document change (the three intended rewordings are listed in it; every other wording unchanged, every fence parses to the same formula, `ve document check`, the two conclusion queries); output `evidence/checkpoint-final.json` |
| `seeded_bugs_20261021T1800Z.py`, `evidence/seeded-bugs.json` | four seeded faults of this run's claims and the failing check of each (no product code changed, so none in Lean, Python or Rust) |
| `rerun_queries.py` | re-runs the five `ve ask` questions and the four `ve document readings --conclusion` queries into `probes/` |
| `metrics.json` | bytes accounted, unit counts by status (new units and aggregated to the 299 old boundaries), claimed and audit-verified bytes, `changed_units`, `plan_repairs` (none), `audit_repairs`, `feature_upgrades` (0), open terms, `open_term_class`, `judgment_term_units/bytes`, reading sets, missing-feature tally, check verdicts, probes, `quantities_qt0p`, `presupposition_ps0p`, `scope_tally`, `act_workaround_m4` (14 units, 2,219 B; 3 stale), `vocabulary_change_check`, `seeded_bugs`, `language_changes_since_previous_tag` |
| `scope-tally.json`, `presupposition-goals.json` | SC-M0 (carried) and PS-0p step 6 |
| `rendered.md`, `rendered-raw.md`, `check.json`, `coverage.json` | the rendering (`rendered.md` adds the source words and VE's verdicts under each hard constraint), the raw `ve document render`, `check` and `coverage` |
| `probes/`, `probe-*.out` | the probes (`unspecified-probe.json`, `frame-probe.json` with the situation binding points), `qt/`, `nd/` (`hard/`: 21 conclusion queries), `companion/`, `ask/` |
| the other scripts | earlier runs' scripts, kept because they import each other |

Reproduce (repository root; `lake build` in `lean/` and `python3 tools/rust_build.py` done; the Lean and Rust build products were copied from the `ve-integration` checkout at the identical commit):

    export PATH=~/.elan/bin:$PATH VE_NATIVE_PREBUILT=1
    R=usecases/claude-constitution-pilot/run-20261021T1800Z
    # start: copy prev/translation-without-content.ve.md and prev/readings/all-strict*.ve.md back, then
    uv run python $R/repair_20261021T1800Z.py            # refuses a second run
    uv run python $R/nd.py all                           # about 1 min
    cp $R/readings/nd-all.ve.md $R/translation.ve.md; uv run python $R/checkpoint.py final
    # probes: s1 and rights read an earlier run's soft companions (copy run-20261008T1800Z/readings/{all-default,s1}.ve.md in, run, remove)
    for p in unspecified risk discourse rights senses senses_doc s1 companions frame; do uv run python $R/probe_$p.py; done
    uv run python $R/rerun_queries.py                    # five ve ask questions, four conclusion queries
    uv run python $R/probe_hard_conclusions.py           # 21 queries, 3 in parallel, about 5 min
    uv run python $R/probe_soft_chain.py                 # about 1 min
    uv run python $R/owner_probe.py
    uv run python $R/finish_20261021T1800Z.py            # ledger, scope tally, goals, renderings, check, coverage, metrics.json (about 4 min; FINISH_CACHE=1 memoises the `ve` calls while developing)
    uv run python $R/seeded_bugs_20261021T1800Z.py       # after the finish (reads units.json); then rerun the finish once so metrics.json carries evidence/seeded-bugs.json
