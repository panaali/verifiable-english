# Run 20261013T0600Z: Claude constitution pilot at `ve-green-eff-20261011-1`

Read `SUMMARY.md` first, then `AUDIT-REPAIR.md` and `FEATURE-REVIEW.md`. `prev/` holds the previous run's (20261012T1800Z) ledger, metrics, check, coverage, translation and probe results, which this run starts from and compares with (they are that run's record, not this run's; its translation inputs are `base/`). `AUDIT-20261012T1800Z-received.md` is the audit this run repairs (the three before are kept). The pinned source is `../source/` (`SOURCE.md` has the SHA-256 and fetch date); it is never edited.

| File | What it is |
|---|---|
| `translation.ve.md`, `units.json` | the main document and ledger (1,132 units, every byte of the 184,893-byte source in exactly one). Three "should" reading sets with Lean-checked content (8 choices, no coupling); u0125.s04.p2 is a CHECKED one-reading unit; each of the seven hard constraints has one strict rule whose guard is `knowingly_<category>` or `thought_likely_<category>` |
| `translation-without-content.ve.md`, `readings/all-strict.ve.md` | the translation with the three sets as pending candidates (input of `nd.py`), and the strict companion (source of the strict content) |
| `readings/nd-all-result.json`, `nd-all-check.json`, `coverage-nd-all.json` | `nd.py all`: the translation rebuilt (it is `translation.ve.md`), its check, separating situations and coverage |
| `metrics.json` | bytes accounted, unit counts by status (new units and aggregated to the 299 old boundaries), claimed and audit-verified bytes, `changed_units`, open terms, reading sets, missing-feature tally, check verdicts, probes, `lean_decided_share`, `question_probe`, `language_changes_since_previous_tag` |
| `rendered.md`, `rendered-raw.md`, `check.json`, `coverage.json` | the rendering (`rendered.md` adds the source words and VE's verdicts under each hard constraint), the raw `ve document render`, `check` and `coverage` |
| `probes/` | the six carried probes (byte-identical to `prev/probes/`), `unspecified-probe.json` (re-run: six points per hard constraint), `hard-conclusions-probe.json` and `nd/hard/` (new: 21 conclusion queries), `nd/` (denial and claim-human conclusions), `companion/`, `ask/` |
| `repair_20261013T0600Z.py`, `finish_20261013T0600Z.py`, `probe_hard_conclusions.py`, `probe_unspecified.py` | this run's scripts; the other scripts are earlier runs' kept because they import each other (`finish_0600.py`, `finish_20261012T0600Z.py`, `finish_20261012T1800Z.py`, `spec_nd.py`, `build.py`, `spec.py`, `nd.py`) |

Reproduce (repository root; `lake build` in `lean/` and `python3 tools/rust_build.py` done):

    export PATH=~/.elan/bin:$PATH VE_NATIVE_PREBUILT=1
    R=usecases/claude-constitution-pilot/run-20261013T0600Z
    uv run python $R/repair_20261013T0600Z.py            # base/ -> translation-without-content.ve.md, readings/all-strict.ve.md
    uv run python $R/nd.py all                           # about 1.5 min
    cp $R/readings/nd-all.ve.md $R/translation.ve.md
    uv run python -m ve document coverage $R/translation.ve.md > $R/readings/coverage-nd-all.json
    # probes: s1 and rights read earlier runs' soft companions (copy run-20261008T1800Z/readings/{all-default,s1}.ve.md in, run, remove);
    # discourse reads base/translation.ve.md, the form it has always started from
    for p in unspecified s1 risk discourse rights senses senses_doc; do uv run python $R/probe_$p.py; done
    uv run python $R/probe_companions.py                 # about 2 min
    N=$R/probes/nd   # ve document readings $R/translation.ve.md --conclusion $N/conclusion-no-denial.json  (and conclusion-no-claim-human.json)
    # companion queries: ve document readings $R/probes/companion/translation-companions-without_source_word.ve.md --conclusion ... --sentence u0125.s04.p2 | u0123.s03
    # ve ask $R/translation.ve.md "<question>" --reading --json   (probes/ask/)
    uv run python $R/probe_hard_conclusions.py           # 21 queries, 4 in parallel; about 20 min (u0165.s01 runs out of budget)
    uv run python $R/finish_20261013T0600Z.py            # about 4 min
