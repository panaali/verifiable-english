# Run 20261015T1800Z: Claude constitution pilot at `ve-green-fix-abbrev`

Read `SUMMARY.md` first, then `AUDIT-REPAIR.md` and `FEATURE-REVIEW.md`. `prev/` holds the previous run's (20261015T0600Z) ledger, metrics, check, coverage, translation, probe results, `AUDIT-REPAIR.md` and `FEATURE-REVIEW.md`, which this run starts from and compares with. `base/` holds the inputs of earlier runs' repair scripts (kept because the scripts import each other; this run's documents are the previous run's, byte for byte). `AUDIT-20261015T0600Z-received.md` is the audit of the previous run (20/20 sampled and 9/9 changed units faithful). The pinned source is `../source/` (`SOURCE.md` has the SHA-256 and fetch date); it is never edited.

This run changes no unit. It re-measures the carried translation at the new tag, asserts the plan additions' shapes and regenerates the tag-only ledger annotations.

| File | What it is |
|---|---|
| `translation.ve.md`, `units.json` | the main document and ledger (1,132 units, every byte of the 184,893-byte source in exactly one); byte-identical to `prev/translation.ve.md`. Four reading sets with Lean-checked content (three “should” sets and the scope set of u0165.s03, whose candidates have their own attitude terms: 16 choices, no coupling); each hard constraint has one strict rule (u0165.s03: two candidates) with guard `( C(s) and knowingly_engages_N(c, s) ) or thinks_quite_likely_N(c, s)` |
| `translation-without-content.ve.md`, `readings/all-strict.ve.md`, `readings/all-strict-narrow.ve.md` | the translation with the four sets as pending candidates (input of `nd.py`), the strict companion (u0165.s03 wide) and the same with u0165.s03 narrow (used by the probes) |
| `readings/nd-all-result.json`, `nd-all-check.json`, `coverage-nd-all.json` | `nd.py all`: the translation rebuilt (`readings/nd-all.ve.md`, cmp-identical to `translation.ve.md`), its check, separating situations and coverage |
| `metrics.json` | bytes accounted, unit counts by status (new units and aggregated to the 299 old boundaries), claimed and audit-verified bytes, `changed_units` (empty), `plan_repairs`, open terms, reading sets, missing-feature tally, check verdicts, probes, `scope_tally`, `act_workaround_m4`, `vocabulary_change_check`, `ledger_only_open_terms`, `english_round_trip`, `language_changes_since_previous_tag`, `question_probe` |
| `scope-tally.json` | SC-M0: every governor, its reach and effect, what it governs, bytes; totals by reach and effect |
| `evidence/m4-act-workaround.json` | AP-0 item 3: the act-phrases evidence the `act_workaround` tags are copied from (cmp-identical to the file on `research/act-phrases-p1`) |
| `rendered.md`, `rendered-raw.md`, `check.json`, `coverage.json` | the rendering (`rendered.md` adds the source words and VE's verdicts under each hard constraint), the raw `ve document render`, `check` and `coverage` |
| `probes/` | the six carried probes (byte-identical to `prev/probes/`), `unspecified-probe.json` (four points per hard constraint, scope points for u0165.s03 on both companions, binding points for u0123.s02.p1; byte-identical to the previous run's), `hard-conclusions-probe.json` and `nd/hard/` (21 conclusion queries), `nd/` (denial and claim-human conclusions), `companion/`, `ask/` (`q*.json` with `--reading`, `q*.answer.json` without it: new at this tag) |
| `repair_20261015T1800Z.py`, `finish_20261015T1800Z.py` | this run's scripts (`repair_20261015T1800Z.py` only asserts and writes nothing); the other scripts are earlier runs' kept because they import each other |

Reproduce (repository root; `lake build` in `lean/` and `python3 tools/rust_build.py` done):

    export PATH=~/.elan/bin:$PATH VE_NATIVE_PREBUILT=1
    R=usecases/claude-constitution-pilot/run-20261015T1800Z
    uv run python $R/repair_20261015T1800Z.py            # asserts the carried documents (AT-0p shape, no stale terms, noun “thing”)
    uv run python $R/nd.py all                           # about 2 min
    cp $R/readings/nd-all.ve.md $R/translation.ve.md     # byte-identical to prev/translation.ve.md
    uv run python -m ve document coverage $R/translation.ve.md > $R/readings/coverage-nd-all.json
    # probes: s1 and rights read earlier runs' soft companions (copy run-20261008T1800Z/readings/{all-default,s1}.ve.md in, run, remove)
    for p in unspecified s1 risk discourse rights senses senses_doc; do uv run python $R/probe_$p.py; done
    uv run python $R/probe_companions.py
    N=$R/probes/nd   # ve document readings $R/translation.ve.md --conclusion $N/conclusion-no-denial.json  (and conclusion-no-claim-human.json)
    # ve ask $R/translation.ve.md "<question>" --reading --json   (probes/ask/q*.json; without --reading: q*.answer.json)
    uv run python $R/probe_hard_conclusions.py           # 21 queries, 3 in parallel
    uv run python $R/probe_hard_conclusions.py rerun     # one at a time, the queries the Rust checker's default 5 s limit made CheckerUnavailable; a second tier runs under
                                                         # `prlimit --as=6442450944` with VE_RUST_TIMEOUT=600 and records the cap and the peak resident set
    uv run python $R/finish_20261015T1800Z.py            # ledger (units.json), scope-tally.json, renderings, check, coverage, metrics.json
