# Run 20261018T1800Z: Claude constitution pilot at `ve-green-eff-20261018-1`

Read `SUMMARY.md` first, then `AUDIT-REPAIR.md` and `FEATURE-REVIEW.md`. `prev/` holds the previous run's (20261018T0600Z) ledger, metrics, check, coverage, translation, probe results, rendering, scope tally and audit, which this run starts from and compares with. `base/` holds the inputs of earlier runs' repair scripts (kept because the scripts import each other). `AUDIT-20261018T0600Z-received.md` is the audit of the previous run (25 of 25 verdicts faithful); the earlier `AUDIT-*-received.md` files are kept. The pinned source is `../source/` (`SOURCE.md` has the SHA-256 and fetch date; copied from `manage-agents/pilots/claude-constitution/source/`); it is never edited.

This run gives no unit a status or meaning from the language (the thirteen merged batches add nothing a document can say). It applies the plans merged for this run, in the order JT-0p (ledger only), QT-0p, PS-0p, each followed by `nd.py all` and `checkpoint.py` so that a failure belongs to one plan.

| File | What it is |
|---|---|
| `translation.ve.md`, `units.json` | the main document and the ledger (1,133 units, every byte of the 184,893-byte source in exactly one). `translation.ve.md` is `readings/nd-all.ve.md` (cmp-identical), built by `nd.py all` from `translation-without-content.ve.md`, which `apply_plans.py` changed (QT-0p, then PS-0p's u0245) |
| `apply_plans.py` | the document changes of QT-0p (`qt0p`) and PS-0p (`ps0p`, default: u0245 only; `PS_NOTE` says why u0286 and u0032 are not in the default), idempotent, starting from `prev/translation-without-content.ve.md` |
| `ledger_1800.py` | the ledger changes: QT-0p units, PS-0p notes and `presupposition_triggers`, `presupposition-goals.json`; `finish_20261018T1800Z.py` calls it and adds JT-0p (classes, `judgment_terms`), the scope tags, the M4 tags and `metrics.json` |
| `checkpoint.py` | the checks after a document change: existing predicate wordings unchanged, fenced units parse to the same formulas, `ve document check`, the two conclusion queries; output `evidence/checkpoint-qt0p.json`, `evidence/checkpoint-final.json` |
| `ps0p_wordings.py`, `diag_premises.py` | which wordings the English lint admits (`evidence/ps0p/wording-lint.json`); the searches the premise check makes (`evidence/ps0p/premise-diag-*.txt`, `premise-variants.json`: the PS-0p items added one at a time) |
| `seeded_bugs.py`, `evidence/seeded-bugs.json`, `evidence/seeded/` | the seeded faults of this run's claims and the failing check of each |
| `evidence/` | `ps0p/` (phase-1 census, headings, goals, plan text copied from `research/presupposition-p1`), `jt0p/instrument-constitution.json` (phase 1's classes), `qt0p-constitution-u0042-u0043.ve.md` (the plan's content), `m4-act-workaround.json`, `companion-attribution.json`, `soft-chain-probe.json`, `finish-timing.json` |
| `metrics.json` | bytes accounted, unit counts by status (new units and aggregated to the 299 old boundaries), claimed and audit-verified bytes, `changed_units` (25), `plan_repairs`, `audit_repairs`, open terms, `open_term_class`, `judgment_term_units/bytes`, reading sets, missing-feature tally, check verdicts, probes, `quantities_qt0p`, `presupposition_ps0p`, `scope_tally`, `act_workaround_m4`, `vocabulary_change_check`, `seeded_bugs`, `language_changes_since_previous_tag` |
| `scope-tally.json`, `presupposition-goals.json` | SC-M0 (governors, reach, effect, bytes) and PS-0p step 6 |
| `rendered.md`, `rendered-raw.md`, `check.json`, `coverage.json` | the rendering (`rendered.md` adds the source words and VE's verdicts under each hard constraint), the raw `ve document render`, `check` and `coverage` |
| `probes/` | the carried probes (`unspecified-probe.json` has the four AT-0p points per rule), `qt/` (the fourth-type queries), `nd/` (`hard/`: 21 conclusion queries), `companion/`, `ask/` |
| the other scripts | earlier runs' scripts, kept because they import each other (`nd.py`, `spec_nd.py`, `frame_u0156.py`, `s03_scope.py`, `finish_*.py`, `repair_*.py`, `probe_*.py`); `probe_s1.py` reads `prev/translation-without-content.ve.md` because its soft companion `readings/s1.ve.md` (run 20261008T1800Z) knows the old vocabulary only |

Reproduce (repository root; `lake build` in `lean/` and `python3 tools/rust_build.py` done):

    export PATH=~/.elan/bin:$PATH VE_NATIVE_PREBUILT=1
    R=usecases/claude-constitution-pilot/run-20261018T1800Z
    uv run python $R/apply_plans.py qt0p; uv run python $R/nd.py all; uv run python $R/checkpoint.py qt0p      # about 9 min
    uv run python $R/apply_plans.py ps0p; uv run python $R/nd.py all; cp $R/readings/nd-all.ve.md $R/translation.ve.md; uv run python $R/checkpoint.py final
    # probes: s1 and rights read an earlier run's soft companions (copy run-20261008T1800Z/readings/{all-default,s1}.ve.md in, run, remove)
    for p in unspecified risk discourse rights senses senses_doc s1 companions frame; do uv run python $R/probe_$p.py; done
    N=$R/probes/nd   # ve document readings $R/translation.ve.md --conclusion $N/conclusion-no-denial.json  (and conclusion-no-claim-human.json); probes/qt/*.conclusion.json likewise
    # ve ask $R/translation.ve.md "<question>" --reading --json   (probes/ask/q*.json; without --reading: q*.answer.json); the companion queries use --sentence u0125.s04.p2 / u0123.s03
    uv run python $R/probe_hard_conclusions.py           # 21 queries, 3 in parallel, about 35 min at this load (all answered on the first run at the default Rust limit)
    uv run python $R/probe_soft_chain.py                 # about 7 min
    uv run python $R/seeded_bugs.py
    uv run python $R/finish_20261018T1800Z.py            # ledger (units.json), scope-tally.json, presupposition-goals.json, renderings, check, coverage, metrics.json (about 5 min)
