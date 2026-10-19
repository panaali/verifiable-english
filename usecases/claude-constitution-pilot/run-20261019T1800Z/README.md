# Run 20261019T1800Z: Claude constitution pilot at `ve-green-et-3b`

Read `SUMMARY.md` first, then `AUDIT-REPAIR.md` and `FEATURE-REVIEW.md`. `prev/` holds the previous run's (20261019T0600Z) ledger, metrics, check, coverage, translation, probe results, rendering, scope tally and goals, which this run starts from and compares with. `base/` holds the inputs of earlier runs' repair scripts (kept because the scripts import each other). `AUDIT-20261019T0600Z-received.md` is the audit of the previous run (30 of 31 faithful; it rejected `u0032.presupposition`); the earlier `AUDIT-*-received.md` files are kept. The pinned source is `../source/` (`SOURCE.md` has the SHA-256 and fetch date; copied from `manage-agents/pilots/claude-constitution/source/`); it is never edited.

This run upgrades one unit from the language (ps-6r merged: four relational-noun wordings), repairs what the audit rejected (u0032 back to UNFORMALISED) and carries the plans merged for the 18:00Z run of 20261018 (JT-0p, QT-0p, PS-0p, AT-0p, SC-M0, AP-0 item 3) unchanged. No plan repairs; no product code (Lean, Python, Rust) was changed.

| File | What it is |
|---|---|
| `translation.ve.md`, `units.json` | the main document and the ledger (1,133 units, every byte of the 184,893-byte source in exactly one). `translation.ve.md` is `readings/nd-all.ve.md` (cmp-identical), built by `nd.py all` from `translation-without-content.ve.md`, which `repair_20261019T1800Z.py --only=u0013` changed |
| `repair_20261019T1800Z.py` | the document changes: u0032 back to UNFORMALISED (predicate, open term and fence removed), and the ps-6r units (`--only=` picks which; the default does all four, which the premise check refuses); `--rename=` and `--unique-u0002` are measurement options for the variants |
| `ps6r_wordings.py`, `ps6r_variants.sh` | the lint/parse probe of the four wordings (`evidence/ps6r/wording-lint.json`) and the scratch-build driver of the 21 premise-check variants (`evidence/ps6r/premise-variants.json`; all-four build: `evidence/ps6r/all-four-*`) |
| `ledger_1800z.py`, `finish_20261019T1800Z.py` | the ledger changes of this run; the finish builds `units.json`, `scope-tally.json` (carried), `presupposition-goals.json`, renderings, `check.json`, `coverage.json`, `metrics.json`. `ledger_1800.py`, `ledger_0600.py` are earlier runs' modules, reused |
| `checkpoint.py` | the checks after a document change (wordings unchanged except the intended removal, the ```` ```ve ```` fences of the start document parse to the same formulas, `ve document check`, the two conclusion queries); output `evidence/checkpoint-final.json` |
| `seeded_bugs_1800.py`, `evidence/seeded-bugs.json` | the seeded faults of this run's claims and the failing check of each (no product code changed) |
| `evidence/` | `ps6r/`, `checkpoint-final.json`, `seeded-bugs.json`, `soft-chain-probe.json`, plus the carried `ps0p/`, `jt0p/`, `at0p/`, `m4-act-workaround.json`, `qt0p-*`, `companion-attribution.json` |
| `metrics.json` | bytes accounted, unit counts by status (new units and aggregated to the 299 old boundaries), claimed and audit-verified bytes, `changed_units` (6), `plan_repairs` (carried AT-0p only), `audit_repairs`, `feature_upgrades`, open terms, `open_term_class`, `judgment_term_units/bytes`, reading sets, missing-feature tally, check verdicts, probes, `quantities_qt0p`, `presupposition_ps0p`, `scope_tally`, `act_workaround_m4`, `vocabulary_change_check`, `seeded_bugs`, `language_changes_since_previous_tag` |
| `scope-tally.json`, `presupposition-goals.json` | SC-M0 (carried) and PS-0p step 6 |
| `rendered.md`, `rendered-raw.md`, `check.json`, `coverage.json` | the rendering (`rendered.md` adds the source words and VE's verdicts under each hard constraint), the raw `ve document render`, `check` and `coverage` |
| `probes/` | the carried probes (`unspecified-probe.json` has the four AT-0p points per rule), `qt/` (the fourth-type queries), `nd/` (`hard/`: 21 conclusion queries), `companion/`, `ask/` |
| the other scripts | earlier runs' scripts, kept because they import each other |

Reproduce (repository root; `lake build` in `lean/` and `python3 tools/rust_build.py` done):

    export PATH=~/.elan/bin:$PATH VE_NATIVE_PREBUILT=1
    R=usecases/claude-constitution-pilot/run-20261019T1800Z
    cp $R/prev/translation-without-content.ve.md $R/translation-without-content.ve.md     # the start
    uv run python $R/nd.py all                                                           # cmp-identical to prev/translation.ve.md (before any change), about 5 min
    uv run python $R/repair_20261019T1800Z.py --only=u0013; uv run python $R/nd.py all; cp $R/readings/nd-all.ve.md $R/translation.ve.md; uv run python $R/checkpoint.py final
    # probes: s1 and rights read an earlier run's soft companions (copy run-20261008T1800Z/readings/{all-default,s1}.ve.md in, run, remove)
    for p in unspecified risk discourse rights senses senses_doc s1 companions frame; do uv run python $R/probe_$p.py; done
    # ve ask --reading --json / --json on the five questions in probes/ask; ve document readings $R/translation.ve.md --conclusion <probes/nd/*.json, probes/qt/*.json>
    uv run python $R/probe_hard_conclusions.py           # 21 queries, 3 in parallel, about 36 min at this load
    uv run python $R/probe_soft_chain.py                 # about 6 min
    uv run python $R/finish_20261019T1800Z.py            # ledger, scope tally, goals, renderings, check, coverage, metrics.json (about 6 min)
    uv run python $R/seeded_bugs_1800.py                 # then finish again, so metrics.json carries the seeded faults
