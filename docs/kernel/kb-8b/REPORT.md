# kb-8b build report: quantity's keyed kinds, the round-4 texts, `kernel_closure --why`

**Part 1 stopped before the promotion: `quantity` stays a candidate (FOLLOW-UP kb-8c below). No DRI signature needed.**
Status: built; tested HEAD 504e00da63 (this report is one docs-only commit after it) on main 9a3fd7a9f9.
Changed: CALLS.md measured (no key sends `count` or a conversion kind); round-4 DESIGN.md and spec section 8 in the repo plus three spec fixes; `tools/kernel_closure.py --why`; docs/kernel/kb-4/MEASURE.md.
Open: the promotion. Measured +1,121 (9,552 to 10,673, under the signed +1,300), but `kernel_closure` reports `quantity_admission_wire_sound` as leaving answer fields open, and fixing that is a Lean statement change this item may not make.
Kernel total: 9,552 before and after (registry, baseline, ALLOWANCES and frozen-keys unchanged). DELTA: none.

SIZE: 117 product (tools/kernel_closure.py 58, tools/kernel_closure.lean 59), 28 tests, 79 other hand-written lines (CALLS.md 71, spec fixes 8), not counting this report. Copied verbatim: DESIGN.md 134 lines, spec section 8 44 lines. Written by scripts from measurements: MEASURE.md 303 lines, calls.json, seeded-bugs.json. The code map was regenerated (7 files).

FOLLOW-UP: kb-8c Restate `VE.Time.Wire.quantity_admission_wire_sound` with its answer fields written by key (or as two closed answers, with and without `model`), so that `quantity` can be promoted. Part 1(b) of kb-8b could not be finished without it.

## Deliverables

| Task line | Commit | Evidence |
|---|---|---|
| 1(a) measure the kinds and fields per key; CALLS.md | f50e6514fd | docs/kernel/kb-8b/CALLS.md, calls.json (AGENT) |
| 1(b) promote if every keyed kind is covered | not made | promotion-attempt.txt: the tool's problem line; FOLLOW-UP kb-8c (AGENT, stopped) |
| 1(c) report any key that reads a keyed value from a nonverdict or uncovered kind | f50e6514fd | none: no key sent `count`, `day`, `civil`, `lower` or `render` (CALLS.md) |
| 2 DESIGN.md byte for byte | 1fb63f23e3 | `cmp` of source and copy: no output, exit 0 |
| 2 section 8 appended verbatim | 1fb63f23e3 | python check: the spec ends with exactly the text between the two marker lines (`True`) |
| 2 (i) (ii) (iii) the three stale places | 1fb63f23e3 | diff of docs/spec/kernel-boundary.md, lines 38, 369, 409, 413 |
| 2 the tests that read the spec | 1fb63f23e3 | `VE_NATIVE_PREBUILT=1 uv run pytest -q tests/test_kernel_closure.py tests/test_architecture_docs.py`: 68 passed. No test pinned text I changed |
| 3 `--why NAME` | 5375948b24 | tests/test_kernel_closure.py::test_why_names_the_part_and_one_shortest_chain_checked_by_hand |
| 3 MEASURE.md | 5375948b24 | docs/kernel/kb-4/MEASURE.md (its script is at its end) |
| 3 one test for `--why` on a definition checked by hand | 5375948b24 | the test above (`VE.Norms.Wire.decodeNormsEnvironment`) |

Acceptance: kernel check against the baseline. `regen_generated.py --write` reran `kernel_closure.py --out` with the new tool and the baseline came out byte-identical (git showed no change; 7af417909c). The selected run includes tests/test_kernel_closure.py: pass. `python3 tools/trust_map.py --check`: "K +0, S +0, D +0, G +0, tied +0, unclassified +0, trusted +0 ... PASS". Selected tests: pass (below). No Lean source under `lean/` changed (`git diff main...HEAD --stat -- lean/` is empty). The five keys' results.json files were unchanged by part 1's runs (`sha256sum -c` against the hashes taken before: all OK). AGENT for all.

## Part 1: CALLS.md's table

The recorder (`/tmp/kb8b/site/sitecustomize.py`, throwaway, not committed) wraps `LeanService._run_chunk`. Every chunk goes through that one function: both `run_bound`s call it, and so do all four relay helpers. The full method is in CALLS.md.

| Key | Kind (case `kind`) | Calls | Fields read (by) | Theorem that states the answer |
|---|---|---:|---|---|
| eligibility | admission (no `kind` field) | 6,781 (6,780 ok, 1 rejection: probe `P1`) | `id`; `status`, `value` (run.py:468-471); `error` (run.py:521, the rejection row of probe P1 only) | `VE.Time.Wire.quantity_admission_wire_sound` |
| eligibility | certificate | 2,353 | `id`; `status`, `valid` (run.py:464, 489) | `VE.Time.Wire.quantity_certificate_wire_sound` |
| eligibility | document | 269 | `id`; `status`, `assurance` (run.py:465) | `VE.Time.Wire.quantity_document_wire_sound` |
| Anthropic RSP | certificate | 26 | `status` (relay); `valid` (ve/units.py:422) | `VE.Time.Wire.quantity_certificate_wire_sound` |
| OpenAI Preparedness | certificate | 30 | `status` (relay); `valid` (ve/units.py:422) | `VE.Time.Wire.quantity_certificate_wire_sound` |
| DeepMind FSF | certificate | 3 | `status` (relay); `valid` (ve/units.py:422) | `VE.Time.Wire.quantity_certificate_wire_sound` |
| DeepMind FSF | countermodel | 1 | `status` (relay); `refutes` (ve/units.py:431) | `VE.Time.Wire.quantity_countermodel_wire_sound` |
| agent policy | (none) | 0 | | |

The harness results matched their READMEs: RSP 110 / 126, Preparedness 236 / 239, FSF 260/262, eligibility 32/32 mutants killed with `open` [], and agent policy exit 0. All five exited 0 (/tmp/kb8b/<key>.out and .rc).

## Kernel total before and after

- Before: 9,552 (docs/kernel/closure-baseline.json `kernel_lines`; ALLOWANCES.md "signed total: 9,552 lines").
- After: 9,552. The promotion was not made.
- With the promotion, as measured: 10,673. Keyed lines stay 16,198, and the kernel part of them would be 10,673. Source: docs/kernel/kb-8b/promotion-attempt.txt.

## Part 2: what changed beyond the verbatim texts

- Line 38 and the KB-3 row: `lean/VE/Service/Document.lean:1166-1180` and `Document.lean:1166-1180` both became "`Service/Document.lean` `environmentOf` (lines 1174-1208 on main 9a3fd7a9f9)". I checked that `def environmentOf` starts at line 1174 on main.
- Line 369 (experimental tier): "a line `Expires: YYYY-MM-DD` in its first docstring, a date not yet passed" is replaced by what `tools/check_lean_imports.py` (`first_docstring`, `expiry_problems`) enforces:
  - the module needs a header docstring, a `/--` or `/-!` doc comment that is its first command;
  - only blank lines, `--` and `/- -/` comments and `import` lines may come before it, in the plain layout `header` reads;
  - the docstring holds exactly one line that is `Expires: YYYY-MM-DD` and nothing else;
  - the date must be valid and no earlier than the day of the check;
  - any other first command, an unclosed doc comment or a header outside that layout fails the module.
  Spec re-read: against tools/check_lean_imports.py:109-146 and the cases in tests/test_lean_experimental_boundary.py:95-165.
- The step-table rows KB-2a and KB-3 now end with "See section 8." KB-2a's last cell had no full stop, so one was added before it.
- No test pinned any of this text. tests/test_kernel_closure.py and tests/test_architecture_docs.py passed unchanged (68 passed).

## Part 3: MEASURE.md's group totals

| Group | Of the 25 listed | Their lines | All kernel modules of the group | Their lines |
|---|---:|---:|---:|---:|
| acts decoding | 5 | 747 | 15 | 1,185 |
| profile gate and dispatch | 2 | 455 | 2 | 455 |
| wire codecs | 6 | 1,372 | 8 | 1,576 |
| logic and semantics | 9 | 2,042 | 68 | 4,507 |
| soft norms | 3 | 997 | 12 | 1,402 |
| other | 0 | 0 | 14 | 427 |
| total | 25 | 5,613 | 119 | 9,552 |

The 119 modules' lines add up to the baseline's `kernel_lines`, 9,552. The script asserts that each per-path, per-part module figure from `--why` equals the baseline's.

`--why` (tools/kernel_closure.py `why`, `why_rows`, `why_text`; tools/kernel_closure.lean `firstReached`, `whyChains`):
- For a module or a definition, it prints each kernel path part (spec or wrap) that counts it and the lines counted there.
- It also prints one shortest chain of references, root first. The Lean half walks the same closure breadth-first, with the same reading rules (`readDeps`; a root theorem gives its type only; theorems contribute nothing; the opaque names are not followed).
- It does this only when a request names `why`, so the measure is unchanged: the regenerated baseline is byte-identical.
- I tried `--why` on several names, and for one definition checked every link of both its chains against the Lean source. On the spec side, I also checked that no norms theorem's statement names the definition directly (lean/statements.txt), so that chain is the shortest. The test pins exactly those chains.

## Seeded bugs (docs/kernel/kb-8b/seeded-bugs.json; each planted, shown failing, restored by `git checkout`)

All five were run against tests/test_kernel_closure.py::test_why_names_the_part_and_one_shortest_chain_checked_by_hand. Each failed on an assertion, not at a build step.

| Id | File | Mutation | Result |
|---|---|---|---|
| S1 | tools/kernel_closure.lean | a statement's constants lose their root theorem as parent | 1 failed: chain starts at `decodeSource` |
| S2 | tools/kernel_closure.lean | the walk is depth-first (last in, first out) | 1 failed: a longer chain ending in `….match_3` |
| S3 | tools/kernel_closure.py | spec and wrap swapped in a row | 1 failed: the norms spec row carries the wrap chain |
| S4 | tools/kernel_closure.py | an uncounted name prints nothing | 1 failed: last line is not "counted by no kernel path" |
| S5 | tools/kernel_closure.py | `--why` ignored, the plain measure runs | 1 failed: the output is the measure's table |

No Rust was changed. The Lean seeds are in the tool's Lean half; no Lean under `lean/` changed.

## Tests and checks run

- Final selected run on the committed tree (git status clean), HEAD 504e00da63: `MAC_PYTEST_NO_DEFER=1 zsh mac-pytest.sh --select -- --base 9a3fd7a9f9 --run`. Exit 0. It ran on GitHub Actions in 2 shards: SHARD 1/2 had 17 units, 17 passed; SHARD 2/2 had 13 units, 13 passed; tree 302c1b52ac (log /tmp/kb8b/sel.wbg).
- While iterating: tests/test_kernel_closure.py 37 passed; the `--why` test alone 1 passed; with tests/test_architecture_docs.py 68 passed.
- `uv run python tools/gate_collection.py --check --prebuilt`: "34852 collected ... 1 added, 0 removed by a trailer, 0 refused, 0 stale and 0 malformed trailers", exit 0.
- `uv run python tools/regen_generated.py --write --skip route-cases`: "wrote 40 entries". `route-cases` was skipped because it needs the Rust release binary and none of its inputs changed (the plain `--write` stopped there with "missing Rust executable"). Only the code map moved; it lagged main's merges.
- Light lane: NOT (936 changed lines outside generated files). So the trust-mutant sweep ran: `zsh mac-pytest.sh --trustmut -- --max-mutants 1000 --json docs/kernel/kb-8b/trust-mutants.json` gave "0 definitions, 0 mutants ... 0 SURVIVOR", exit 0.
- `lake build` (default targets) before the measurements: "Build completed successfully (1438 jobs)". `python3 lean/audit.py` was not run, because no Lean under `lean/` changed.
- Not run by me: the full release gate (the chain runs it).

## DELTA

None. No answer, diagnostic, verdict or schema changed. `--why` is a new option of a measuring tool that prints and writes nothing. No DELTA.md.

## Notes for the DRI

- Duplicate section number. The amendment was appended verbatim, as asked, and its heading is "## 8. Amendments of 2026-11-13". The spec already has "## 8. The frozen keys on this measure" and "## 9. Risks and open points", so it now has two sections numbered 8. The "See section 8." on rows KB-2a and KB-3 means the new one. I did not renumber, because the task said "do not reword".
- `--why` roots. The task says "from a registry subject or a listed theorem statement". A subject is opaque to both parts: the spec leaves it unread and the wrap is cut at it, so no chain can start there. Spec chains therefore start at a listed theorem and wrap chains at the path's entry.
- Groups. The "logic and semantics" and "other" groups follow the namespace rule written in MEASURE.md. Seven `*Wire` modules outside the task's wire-codec list fall by that rule (listed there). `VE.Order.ProfileGate` is counted by no kernel path.
- Preparedness ran as `--check`, which includes its mutants, because that is the task's wording; kb-8 and the frozen-keys record used `--check --base-only`. So 30 calls here against 20 in the 2026-11-11 record.
- Eligibility's one rejection row (probe P1, `DateRange(1960-06-27)`, as the probe expects) is read for its `error` text, and that text goes into results.json `probes`, not into the keyed answers. No theorem states a rejection, and a refusal carries no verdict.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A. No relayed route or schema changed; `--why` reads only the tool's own Lean half output.
2. Deliverables: PASS. See the Deliverables table. Part 1(b) did not land, which is recorded as FOLLOW-UP kb-8c, a real seam: it needs a Lean statement change. `git diff main...HEAD` has no new permanent report test and no copy of a Lean decision in Python.
3. Tests can fail: PASS. Seeded bugs S1-S5 each fail the `--why` test. Trust mutants: 0 to run (trusted +0).
4. Python/Lean/Rust agree: N.A. No checker path changed. The baseline regenerated byte-identical (7af417909c shows no baseline change).
5. R8 binding: N.A. No relayed field added.
6. Gate evidence: PASS. Selected run on the committed tree 504e00da63; the full gate is the chain's.
7. Unsigned items: PASS. No DELTA row and no trust growth (`trust_map.py --check` +0).
8. User-visible changes: PASS. None; the five keys' results.json are byte-identical (`sha256sum -c`).
9. Test selection: PASS. `select_tests.py` picked 30 of 614 units, including tests/test_kernel_closure.py, the test S1-S5 break.
10. Lean statements: N.A. No theorem added or changed.
11. Budgets and limits: N.A. No public operation added; `--why` reuses the measure's `--timeout`.
12. CPU and memory: N.A. No checker path changed. `--why` runs only when asked (about 22 s per call).
13. Test-removed trailers: PASS. No test removed or renamed; `gate_collection.py --check --prebuilt`: 0 refused, 0 stale, 0 malformed.
14. Both directions and cited evidence: PASS. The `--why` test checks a counted name (rows and chains) and an uncounted one ("counted by no kernel path"). Every figure above names its command or file. Spec re-read: the Expires sentence against tools/check_lean_imports.py:109-146; the `environmentOf` line against lean/VE/Service/Document.lean:1174; section 8 against the source between its markers (byte check).
15. Overclaim, silent cut, failing checks, limits charged first: PASS / PASS / PASS / N.A.
   - "Unchanged" is said only of the baseline (regen, no diff), the results.json files (sha256) and the kernel total (no registry change).
   - The cut of 1(b) is stated in the summary and as FOLLOW-UP kb-8c.
   - Every new check has a seeded bug.
   - No new limit.

Sibling lesson kb-10b F1 (case identities lost in recorded rows): checked. CALLS.md and calls.json keep each rejection row's case id (`P1`) and each read's frame. The eligibility case ids are by profile and step, and the harnesses' fixed ids (`certificate`, `countermodel`) are reported as they are sent.
