# Run 20261015T0600Z: Claude constitution pilot at `ve-green-lf-14b`

Read `SUMMARY.md` first, then `AUDIT-REPAIR.md` and `FEATURE-REVIEW.md`. `prev/` holds the previous run's (20261014T1800Z) ledger, metrics, check, coverage, translation, probe results, `AUDIT-REPAIR.md` and `FEATURE-REVIEW.md`, which this run starts from and compares with. `base/` holds this run's translation inputs: the previous run's final `translation-without-content.ve.md`, `all-strict.ve.md` (wide) and `all-strict-narrow.ve.md`, its final `start-translation.ve.md`, and `translation.ve.md`, the form the discourse probe has always started from. `AUDIT-20261014T1800Z-received.md` is the audit this run repairs. The pinned source is `../source/` (`SOURCE.md` has the SHA-256 and fetch date); it is never edited.

| File | What it is |
|---|---|
| `translation.ve.md`, `units.json` | the main document and ledger (1,132 units, every byte of the 184,893-byte source in exactly one). Four reading sets with Lean-checked content (three “should” sets and the scope set of u0165.s03, whose candidates have their own attitude terms: 16 choices, no coupling); each hard constraint has one strict rule (u0165.s03: two candidates) with guard `( C(s) and knowingly_engages_N(c, s) ) or thinks_quite_likely_N(c, s)` |
| `translation-without-content.ve.md`, `readings/all-strict.ve.md`, `readings/all-strict-narrow.ve.md` | the translation with the four sets as pending candidates (input of `nd.py`), the strict companion (u0165.s03 wide) and the same with u0165.s03 narrow (used by the probes) |
| `readings/nd-all-result.json`, `nd-all-check.json`, `coverage-nd-all.json` | `nd.py all`: the translation rebuilt (it is `translation.ve.md`), its check, separating situations and coverage |
| `metrics.json` | bytes accounted, unit counts by status (new units and aggregated to the 299 old boundaries), claimed and audit-verified bytes, `changed_units`, `plan_repairs`, `audit_repairs`, open terms, reading sets, missing-feature tally, check verdicts, probes, `scope_tally`, `act_workaround_m4`, `vocabulary_change_check`, `ledger_only_open_terms`, `english_round_trip`, `language_changes_since_previous_tag` |
| `scope-tally.json` | SC-M0: every governor, its reach and effect, what it governs, bytes; totals by reach and effect |
| `evidence/m4-act-workaround.json` | AP-0 item 3: the act-phrases evidence the `act_workaround` tags are copied from |
| `rendered.md`, `rendered-raw.md`, `check.json`, `coverage.json` | the rendering (`rendered.md` adds the source words and VE's verdicts under each hard constraint), the raw `ve document render`, `check` and `coverage` |
| `probes/` | the six carried probes (byte-identical to `prev/probes/`), `unspecified-probe.json` (four points per hard constraint, scope points for u0165.s03 on both companions, binding points for u0123.s02.p1), `hard-conclusions-probe.json` and `nd/hard/` (21 conclusion queries), `nd/` (denial and claim-human conclusions), `companion/`, `ask/` |
| `repair_20261015T0600Z.py`, `s03_scope.py`, `finish_20261015T0600Z.py`, `probe_hard_conclusions.py`, `probe_unspecified.py` | this run's scripts (`s03_scope.py` owns the two guards and the four attitude terms of u0165.s03); the other scripts are earlier runs' kept because they import each other |

Reproduce (repository root; `lake build` in `lean/` and `python3 tools/rust_build.py` done):

    export PATH=~/.elan/bin:$PATH VE_NATIVE_PREBUILT=1
    R=usecases/claude-constitution-pilot/run-20261015T0600Z
    uv run python $R/repair_20261015T0600Z.py            # base/ -> translation-without-content.ve.md, readings/all-strict*.ve.md
    uv run python $R/nd.py all                           # about 2-3 min
    cp $R/readings/nd-all.ve.md $R/translation.ve.md
    uv run python -m ve document coverage $R/translation.ve.md > $R/readings/coverage-nd-all.json
    # probes: s1 and rights read earlier runs' soft companions (copy run-20261008T1800Z/readings/{all-default,s1}.ve.md in, run, remove)
    for p in unspecified s1 risk discourse rights senses senses_doc; do uv run python $R/probe_$p.py; done
    uv run python $R/probe_companions.py
    N=$R/probes/nd   # ve document readings $R/translation.ve.md --conclusion $N/conclusion-no-denial.json  (and conclusion-no-claim-human.json)
    # ve ask $R/translation.ve.md "<question>" --reading --json   (probes/ask/)
    uv run python $R/probe_hard_conclusions.py           # 21 queries, 3 in parallel
    uv run python $R/probe_hard_conclusions.py rerun     # one at a time, the queries the Rust checker's default 5 s limit made CheckerUnavailable; a second tier runs under
                                                         # `prlimit --as=6442450944` with VE_RUST_TIMEOUT=600 and records the cap and the peak resident set
    uv run python $R/finish_20261015T0600Z.py            # ledger (units.json), scope-tally.json, renderings, check, coverage, metrics.json
