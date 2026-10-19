# Run 20261019T0600Z: Claude constitution pilot at `ve-green-qt-b1`

Read `SUMMARY.md` first, then `AUDIT-REPAIR.md` and `FEATURE-REVIEW.md`. `prev/` holds the previous run's (20261018T1800Z) ledger, metrics, check, coverage, translation, probe results, rendering, scope tally and goals, which this run starts from and compares with. `base/` holds the inputs of earlier runs' repair scripts (kept because the scripts import each other). `AUDIT-20261018T1800Z-received.md` is the audit of the previous run (47 of 48 faithful; it rejected `u0042.presupposition`); the earlier `AUDIT-*-received.md` files are kept. The pinned source is `../source/` (`SOURCE.md` has the SHA-256 and fetch date; copied from `manage-agents/pilots/claude-constitution/source/`); it is never edited.

This run gives no unit a status or meaning from the language (the six merged batches add nothing a document can say). It repairs what the audit rejected, offers the two PS-0p items the 18:00Z run had to revert (the premise check now allows them), and carries the other plan sections.

| File | What it is |
|---|---|
| `translation.ve.md`, `units.json` | the main document and the ledger (1,133 units, every byte of the 184,893-byte source in exactly one). `translation.ve.md` is `readings/nd-all.ve.md` (cmp-identical), built by `nd.py all` from `translation-without-content.ve.md`, which `repair_20261019T0600Z.py` and `apply_plans.py ps0p --only=u0286.presupposition,u0032.presupposition` changed |
| `repair_20261019T0600Z.py` | the audit repair of QT-0p: the sort `principal_type` gets the noun "principal type of Claude", the predicate `claude_principal_type` is removed, u0042.presupposition and u0043.s02.p2 get formulas without it; refuses a second run |
| `apply_plans.py` | as in the last run; `ps0p` now offers u0286 and u0032 by default (u0245 is already in the start document) |
| `ledger_0600.py`, `finish_20261019T0600Z.py` | the ledger changes of this run (repairs, u0286, u0032, the audit's small faults); the finish builds `units.json`, `scope-tally.json` (carried), `presupposition-goals.json`, renderings, `check.json`, `coverage.json`, `metrics.json`. `ledger_1800.py` is last run's module (triggers, goals), reused |
| `checkpoint.py` | the checks after a document change (wordings unchanged except the two intended changes, fenced units parse to the same formulas, `ve document check`, the two conclusion queries); output `evidence/checkpoint-repair.json`, `evidence/checkpoint-final.json` |
| `seeded_bugs_0600.py`, `evidence/seeded-bugs.json`, `evidence/seeded/` | the seeded faults of this run's claims and the failing check of each (no product code changed) |
| `evidence/` | `ps0p/premise-variants-0600Z.json` (u0286, u0032 alone and together: premise check `model`), `ps0p/prev-1800Z/` (last run's UNKNOWN measurements, historical), `after-repair-nd-all*.{ve.md,json}` (the repair step alone), `pre-qt0p-translation-without-content.ve.md` (the 06:00Z document, the input of `probe_s1.py`), `prev-1800Z/checkpoint-qt0p.json`, `jt0p/`, `at0p/`, `m4-act-workaround.json`, `qt0p-constitution-u0042-u0043.ve.md` (the plan's content, with the predicate wording this run replaced), `companion-attribution.json` (the 18:00Z attribution), `soft-chain-probe.json` |
| `metrics.json` | bytes accounted, unit counts by status (new units and aggregated to the 299 old boundaries), claimed and audit-verified bytes, `changed_units` (7), `plan_repairs`, `audit_repairs` (5), open terms, `open_term_class`, `judgment_term_units/bytes`, reading sets, missing-feature tally, check verdicts, probes, `quantities_qt0p`, `presupposition_ps0p`, `scope_tally`, `act_workaround_m4`, `vocabulary_change_check`, `seeded_bugs`, `language_changes_since_previous_tag` |
| `scope-tally.json`, `presupposition-goals.json` | SC-M0 (carried) and PS-0p step 6 |
| `rendered.md`, `rendered-raw.md`, `check.json`, `coverage.json` | the rendering (`rendered.md` adds the source words and VE's verdicts under each hard constraint), the raw `ve document render`, `check` and `coverage` |
| `probes/` | the carried probes (`unspecified-probe.json` has the four AT-0p points per rule), `qt/` (the fourth-type queries, rewritten for the sort), `nd/` (`hard/`: 21 conclusion queries), `companion/`, `ask/` |
| the other scripts | earlier runs' scripts, kept because they import each other |

Reproduce (repository root; `lake build` in `lean/` and `python3 tools/rust_build.py` done):

    export PATH=~/.elan/bin:$PATH VE_NATIVE_PREBUILT=1
    R=usecases/claude-constitution-pilot/run-20261019T0600Z
    cp $R/prev/translation-without-content.ve.md $R/translation-without-content.ve.md     # the start (already so in a fresh copy)
    uv run python $R/nd.py all                                                           # cmp-identical to prev/translation.ve.md (before any change), about 3 min
    uv run python $R/repair_20261019T0600Z.py; uv run python $R/nd.py all; uv run python $R/checkpoint.py repair $PWD/<nd-all copy>   # the repair step alone
    uv run python $R/apply_plans.py ps0p --only=u0286.presupposition,u0032.presupposition; uv run python $R/nd.py all; cp $R/readings/nd-all.ve.md $R/translation.ve.md; uv run python $R/checkpoint.py final
    # probes: s1 and rights read an earlier run's soft companions (copy run-20261008T1800Z/readings/{all-default,s1}.ve.md in, run, remove)
    for p in unspecified risk discourse rights senses senses_doc s1 companions frame; do uv run python $R/probe_$p.py; done
    # ve document readings $R/translation.ve.md --conclusion $R/probes/qt/{fourth,no-fourth}.conclusion.json
    uv run python $R/probe_hard_conclusions.py           # 21 queries, 3 in parallel, about 26 min at this load
    uv run python $R/probe_soft_chain.py                 # about 8 min
    uv run python $R/seeded_bugs_0600.py cheap           # plus the scratch closure fault recorded in evidence/seeded-bugs.json
    uv run python $R/finish_20261019T0600Z.py            # ledger, scope tally, goals, renderings, check, coverage, metrics.json (about 10 min)
