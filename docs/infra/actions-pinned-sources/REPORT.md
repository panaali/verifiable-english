# actions-pinned-sources: the Actions gate and nightly fetch FSF, RSP and PF at sha256 pins and fail closed

- Status: built, ready for review. No DELTA rows, no DRI signature reserved, trust +0 (no Lean, no trusted line).
- What changed: `usecases/pinned_sources.json` (hashes, sizes and URLs only), `tools/fetch_pinned_sources.py`, one test helper
  `tests/pinned_source.py` that all 16 former `DEFAULT_SOURCE.exists()` branches and the 3+3 gate-optional skips call,
  `VE_REQUIRE_PINNED_SOURCES=1` (named failure when absent), `tools/gate.py` seeding its fresh home, and the `ve-job.yml` step.
- Found on the way (MEASURED): under `tools/gate.py` HOME is a fresh scratch home, so no gate on any machine found the stored
  sources. The ve-cloud-2 copy of 11-13 12:45Z changed nothing (Notes for the DRI, 1). This branch fixes that too.
- Open: the post-merge Actions run (decision item 2 condition) and the arm step install (section "arm workflow step").

SIZE: 199 product (tools 177, workflow 20, plus the 33-line pins file), 344 tests, 2 other hand-written files (this report and
`fetch-vm1.txt`). Counted with `git diff --numstat $(git merge-base HEAD main)..HEAD`, codemap excluded.

## Deliverables (task DO 1 to 5)

| # | Deliverable | Where | Test |
|---|---|---|---|
| 1 | Pins file: per document the publisher URL, PDF sha256 and size, extract command, text sha256 and size, home-relative path | `usecases/pinned_sources.json` | `tests/test_pinned_sources.py::test_the_pins_equal_each_build_document_and_extract_step`, `::test_a_malformed_pin_is_refused` |
| 1 | One owner: build_document.py keeps `TEXT_SHA256`/`TEXT_BYTES`/`DEFAULT_SOURCE`; the test checks the pins equal them, and `PDF_SHA256` of each `source/extract_text.py` | same test | as above (seeded bug S6) |
| 2 | Fetch step: download, check PDF sha256+size, run the committed extract step, check text sha256+size, write where `DEFAULT_SOURCE` looks (`Path.home() / path`) | `tools/fetch_pinned_sources.py` | `::test_the_fetch_refuses_bytes_whose_sha256_is_not_the_pin`, `::test_the_fetch_writes_the_text_when_both_pins_hold`, `::test_the_fetch_refuses_an_extraction_that_is_not_the_pinned_text`, `::test_the_fetch_never_overwrites_a_stored_text_that_is_not_its_pin`, `::test_the_check_names_each_absent_document` |
| 2 | FSF and RSP extract steps | already committed: `usecases/safety-framework/source/extract_text.py` (21b9f9987a), `usecases/anthropic-rsp/source/extract_text.py` (6625d35e1e), both pypdf==6.19.0 like PF's | VM1 reproduction below |
| 2 | VM1 reproduces each stored .txt byte for byte | `docs/infra/actions-pinned-sources/fetch-vm1.txt` | `cmp` lines there: 3 of 3 identical |
| 3 | `VE_REQUIRE_PINNED_SOURCES=1`: one helper; absent or wrong hash FAILS by name; unset keeps the skip | `tests/pinned_source.py` | `::test_the_helper_fails_by_name_when_required_and_absent`, `::test_the_helper_fails_by_name_when_the_hash_is_wrong[1]`, `[None]`, `::test_the_helper_skips_when_not_required[None,0,,yes]`, `::test_the_helper_returns_a_text_stored_at_its_pin` |
| 3 | The 16 `DEFAULT_SOURCE.exists()` branches (the task said 15: 5 FSF, 9 in test_safetyfw_usecases, 2 in test_pf_fidelity_fix) and the gate-optional skips use it | `tests/test_safety_framework.py`, `tests/test_safetyfw_usecases.py`, `tests/test_pf_fidelity_fix.py`, `tests/test_fidmech_segment.py` | `grep -rn "DEFAULT_SOURCE.exists" tests/` prints nothing |
| 3 | The gate passes the variable to pytest and copies stored sources into its fresh home | `tools/gate.py` (`seed_pinned_sources`, `pinned_requirement`, `STAGE_ENVIRONMENT["pytest"]`) | `::test_the_gate_copies_stored_sources_into_its_home_and_passes_the_requirement` |
| 4 | `ve-job.yml`: a gate job (the nightly's shards included) runs the fetch step and sets `VE_REQUIRE_PINNED_SOURCES=1` | `.github/workflows/ve-job.yml` steps `job commit` (output `gate`), `pinned sources`, `job` | `tests/test_ci_workflow.py::test_only_a_gate_job_fetches_and_requires_the_pinned_sources[7 cases]`, `::test_the_job_step_requires_the_pinned_sources_only_in_a_gate_job`, `::test_the_fetch_step_records_its_status_and_never_fails_the_run[0,1]` |
| 5 | Tests that fail on the old code | `tests/test_pinned_sources.py` imports `tests.pinned_source` and `tools.fetch_pinned_sources`, absent on main | the condition tests below |

Condition tests (stay selected; `tools/select_tests.py --base $(git merge-base HEAD main)` lists every file below):
`tests/test_pinned_sources.py::test_the_helper_fails_by_name_when_required_and_absent`,
`::test_the_helper_fails_by_name_when_the_hash_is_wrong`, `::test_the_fetch_refuses_bytes_whose_sha256_is_not_the_pin`,
`::test_the_pins_equal_each_build_document_and_extract_step`,
`tests/test_safety_framework.py::test_every_will_quote_is_the_pinned_source_text`.

## Design choices (conservative option taken, not asked)

- **Where the text goes.** The fetch step writes `Path.home() / path`, exactly where `build_document.DEFAULT_SOURCE` looks;
  no `DEFAULT_SOURCE` and no `tools/fidmech/segment.py:doc_source` changed. Under `tools/gate.py`, HOME is
  `<scratch>/home`, so the gate copies (never links) each stored text from the account home (password database, as for
  the toolchains) to the same path in its home. It copies the bytes as they are; the helper checks the hash.
- **Wrong hash always fails**, required or not; only an absent text may skip, and only when not required. Today a stored
  wrong text already failed later in the build; it now fails at once with the hash in the message.
- **The fetch never overwrites a stored text that differs from its pin** and never falls back to another copy; it names
  each failing document on a `FAILED <doc>: <reason>` line and exits 1. It downloads with a generic User-Agent
  (`ve-fetch-pinned-sources/1`); `Python-urllib`'s default got HTTP 403 from www-cdn.anthropic.com (probe, 11-14).
- **Which Actions jobs.** `ve-job.yml` runs every kind of job. A gate job is recognised by gate-job.sh's contract: job.json
  `argv[5]` is its `<workers>` count (1 to 4 digits); a cmd job has `<name>=<command>` there and is unchanged (no fetch,
  no variable), so trust-mutant and command jobs are not affected.
- **The step never fails the run.** Its output goes to `out/pinned-sources.txt` and `gha-setup.tsv` (`pinned_sources rc s`).
  A missing source then fails the pinned-source tests by name in the gate (fail closed), and the record still arrives.
- **Integrity.** PDF sha256 and size before extraction; text sha256 and size after. `uv run --with pypdf==6.19.0` resolves
  pypdf from PyPI by version, not by hash; the text pin is the check on its output.

How the gate-optional rows interact: the six rows ("the pinned source is not stored on this machine": three FSF tests and
three `test_fidmech_segment` cases) stay. They allow only a skip with that reason, and the helper skips with exactly
that reason only when the variable is unset (`test_gate_optional_still_allows_the_unset_skips`). With
`VE_REQUIRE_PINNED_SOURCES=1` the helper never skips, so the rows never apply and a missing source is a gate failure.
The gate matches reasons by substring (`tools/gate.py:311`), so the new skip location (`tests/pinned_source.py`) still
matches.

## Measured

- Publisher URLs (VM1, 11-14, `curl -sSL` then `sha256sum`): FSF 447,155 bytes `ad10d2d2…`, RSP 304,755 `6247b9e4…`, PF
  170,399 `fae6e4cc…`: all three equal the pins in each PLAN.md section 1. No document fails closed.
- `tools/fetch_pinned_sources.py` into an empty home: 3 ok, 11.6 s, `cmp` identical with the stored copies
  (`fetch-vm1.txt`). `--check` on the VM's home: 3 ok, exit 0.
- An Actions-like run (HOME = that fetched home, `VE_REQUIRE_PINNED_SOURCES=1`): the three FSF gate-optional tests and the three
  `test_the_frozen_boundaries_fit_the_pinned_source` cases passed (logs `/tmp/aps-t6.log` 4 passed, `/tmp/aps-t7.log` 2 passed).
- On the VM's own home with the variable set: the 13 edited tests across the four files passed (`/tmp/aps-t2.log`), and the
  7 PF tests of test_safetyfw_usecases passed (`/tmp/aps-t3.log`).
- Empty HOME: the will-quote test skips unset ("SKIPPED ... the pinned source is not stored on this machine") and fails
  with `VE_REQUIRE_PINNED_SOURCES=1` ("Failed: the pinned source safety-framework is not stored at .../fsf-3.1.txt").

Not run: the extraction on aarch64 (pypdf is pure Python; UNVERIFIED there, and the text pin fails closed if it differs);
any Actions run (post-merge, below); the full gate (the chain runs it).

## Seeded bugs (Python, plus the workflow YAML; no Lean or Rust changed)

Each was planted alone, the one test run, the file restored with `git checkout` (`/tmp/aps-seed.sh`):

| Id | File | Bug | Failing test |
|---|---|---|---|
| S1 | `tests/pinned_source.py` | required is ignored (`if path.is_file():`) | `test_pinned_sources.py::test_the_helper_fails_by_name_when_required_and_absent` |
| S10 | `tests/pinned_source.py` | a wrong hash fails only when required | `::test_the_helper_fails_by_name_when_the_hash_is_wrong[None]` |
| S11 | `tests/pinned_source.py` | `skip` inverted | `::test_the_helper_skips_when_not_required[None]` |
| S2 | `tools/fetch_pinned_sources.py` | the PDF check compares the size only | `::test_the_fetch_refuses_bytes_whose_sha256_is_not_the_pin` |
| S3 | `tools/fetch_pinned_sources.py` | the text check compares the size only | `::test_the_helper_fails_by_name_when_the_hash_is_wrong[1]` |
| S8 | `tools/fetch_pinned_sources.py` | the extracted text is not checked | `::test_the_fetch_refuses_an_extraction_that_is_not_the_pinned_text` |
| S9 | `tools/fetch_pinned_sources.py` | a differing stored text is deleted, then refetched | `::test_the_fetch_never_overwrites_a_stored_text_that_is_not_its_pin` |
| S4 | `tools/gate.py` | the variable is not passed to pytest | `::test_the_gate_copies_stored_sources_into_its_home_and_passes_the_requirement` |
| S5 | `tools/gate.py` | the source is symlinked, not copied | same test |
| S6 | `usecases/pinned_sources.json` | FSF `text_bytes` 54374 | `::test_the_pins_equal_each_build_document_and_extract_step` |
| S7 | `.github/workflows/ve-job.yml` | any `argv[5]` makes a gate job | `test_ci_workflow.py::test_only_a_gate_job_fetches_and_requires_the_pinned_sources[cmd job]` |

S1 and S2 first survived. A `pytest.skip` passed through `pytest.raises(pytest.fail.Exception)` as a skip, and the
hash fixture differed in size. Commit 3rd on the branch ("helper tests tell a skip from a failure") fixed both tests, and
both seeds then failed.

## arm workflow step (install read)

Not edited here (manage-agents `gha/ve-job-arm.yml`, row actions-pinned-sources-arm, installed by the DRI decider). Three
edits, the same as x86:

1. In step `job commit`, before `[ "$(git rev-parse HEAD~1)" = "$head" ]`, add the line below, then add
   `echo "gate=$gate" >> "$GITHUB_OUTPUT"` after its last `echo ... >> "$GITHUB_OUTPUT"` line:

```yaml
          gate=$(python3 -I -c 'import json, re; a = json.load(open("ci-job/job.json"))["argv"]; print("1" if isinstance(a, list) and len(a) > 5 and isinstance(a[5], str) and re.fullmatch("[0-9]{1,4}", a[5]) else "")')
```

2. A new step after `git` (it needs uv from `tools`) and before `job`:

```yaml
      - name: pinned sources
        if: steps.job.outputs.gate == '1'
        run: |
          set -uo pipefail
          t0=$(date +%s); P=$RUNNER_TEMP/out/pinned-sources.txt
          if [ -f tools/fetch_pinned_sources.py ]; then timeout 1800 python3 -I tools/fetch_pinned_sources.py > "$P" 2>&1; rc=$?
          else echo "no tools/fetch_pinned_sources.py at this head" > "$P"; rc=0; fi
          cat "$P"; printf 'pinned_sources\t%s\t%s\n' "$rc" "$(( $(date +%s) - t0 ))" >> "$RUNNER_TEMP/out/gha-setup.tsv"
```

3. In step `job`, add an `env:` and one line after `set -uo pipefail`:

```yaml
      - name: job
        env:
          GATE_JOB: ${{ steps.job.outputs.gate }}
        run: |
          set -uo pipefail
          [ "${GATE_JOB:-}" != 1 ] || export VE_REQUIRE_PINNED_SOURCES=1
```

The arm legs run the head's `tools/gate.py`, which passes the variable on and seeds its home once this merges. Before
the install, arm legs keep the allowed skip.

## After merge (decision item 2 condition; not doable on this branch)

One `gha-arm-shard.sh` x86 run of main after the merge must record the three FSF tests and the RSP/PF pinned-source tests
PASSED, not skipped. Then `zsh msg.sh dri <name> "actions-pinned-sources: <run id> pinned-source tests PASSED"`;
the decider restores NIGHTLY_X86_ACTIONS (decision item 3). Owner: whoever runs the post-merge check for this row (EXTERNAL
to this build).

## Notes for the DRI

1. MEASURED: the 11-13 12:45Z copy to ve-cloud-2 did not un-skip anything. `tools/gate.py:gate_environment` sets HOME to
   `<scratch>/home`, and `DEFAULT_SOURCE` is `Path.home() / ...`. `manage-agents/nightly-gate.x86.json` (6949e5de,
   written 11-13 19:37) records HOME `/tmp/ve-gate-benup4lp/home` and still has the 3 FSF "pinned source is not stored"
   skips, as `nightly-vm-gate.json` (a8b8c0fd) does. Gates on any machine have never run these tests. With this branch the
   gate copies stored texts into its home, so VM and ve-cloud-2 gates run them too, unset.
2. `uv run python tools/regen_generated.py --write` also wrote code map entries that main was missing
   (`tests/omission_rule.py`, `docs/kernel/kb-10b/repair_shadow_choices.py` → new `docs/codemap/docs__kernel.md`).
3. Pre-existing failures: none of the touched test files is in `main-known-red.txt` (grep, no match).

## Spec re-read

- "download, check the sha256, run the committed extract step, check the .txt sha256, and write it where DEFAULT_SOURCE
  looks" (task DO 2) against `tools/fetch_pinned_sources.py:fetch`: same order; sizes checked too.
- "When the variable is set and the source is absent or has the wrong hash, it FAILS with a named reason. Unset, it keeps
  today's skip" (DO 3) against `tests/pinned_source.py:pinned_source`: yes. Narrower on one point: a wrong hash fails
  unset too.
- "run the fetch step and set VE_REQUIRE_PINNED_SOURCES=1 for the nightly and gate modes" (DO 4): gate jobs by
  gate-job.sh's argv contract (`manage-agents/gha/gate-job.sh` usage line). The nightly runs as gate shards
  (`x86sh-nightly-*`, argv `[j, h, b, -, -, w, k/n, authority]`).
- "Only hashes, sizes and URLs" (DO 1): the pins file and `fetch-vm1.txt` hold no source text.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed: N.A. (no relayed answer).
2. Deliverables: PASS, table above. No copy of a Lean decision, no permanent report test.
3. Tests can fail: PASS, 11 seeded bugs above.
4. Py/Lean/Rust agree: N.A. (no checker path changed).
5. R8 binding: N.A.
6. Gate evidence on final HEAD: the chain runs the gate. The final selected run is on committed code (below).
7. Unsigned items: PASS, none (no DELTA rows, trust +0).
8. DELTA: N.A. No user-visible checker output changes. The gate runs, rather than skips, pinned-source tests where a
   stored text exists (Notes 1).
9. Selection: PASS, `select_tests.py --base` lists tests/test_pinned_sources.py, test_ci_workflow.py,
   test_safety_framework.py, test_safetyfw_usecases.py, test_pf_fidelity_fix.py, test_fidmech_segment.py,
   test_gate_integrity.py (203/619 units).
10. Lean statements: N.A.
11. Budgets: N.A. No new test wait (tools/ is outside test_hang_guards' scan; the tests use HANG_TIMEOUT).
12. CPU: N.A. (the fetch is 11.6 s once per gate job, outside the suite).
13. Test-removed trailer: N.A. No test removed or renamed.
14. Both directions: PASS. Accept and refuse for the helper (returns / fails / skips), fetch (writes / refuses PDF, text,
    overwrite), gate (copied / absent; variable passed / not), workflow (gate / cmd job).
15. Overclaim: "16 branches" counted with grep before the edit. "Gates on any machine have never run these tests" rests on
    the two nightly records cited plus `gate_environment`.

## Final selected run

- `MAC_PYTEST_NO_DEFER=1 zsh mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run` on committed 1e65477c51
  (log `/tmp/aps-select.log`; ran on the VM, MAC_LAST): 203 units recorded, 1 failed:
  `tests/test_difffuzz.py::test_every_fixture_is_read_or_excluded_with_a_reason` ("unread: usecases/pinned_sources.json").
- Fix d75f28b519: `tools/difffuzz_corpus.py` EXCLUDED lists the pins file as `no-input` (it has no environment or request).
  Rerun of the failed id only: `zsh mac-pytest.sh -- tests/test_difffuzz.py::test_every_fixture_is_read_or_excluded_with_a_reason`
  on ve-mac-1, HEAD d75f28b5 clean: 1 passed, exit 0. `regen_generated.py --check`: 41 entries fresh.
- Because a code commit followed the selected run, the chain gate cannot reuse it and runs in full on the final HEAD.
