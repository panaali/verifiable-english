# AR-22: closure certificates replay through Core; the closure tableau copy is deleted (consolidation step 3b)

**No DELTA row waits for a DRI signature.** DELTA has R7 rows only (records unavailable on both sides with identical
outputs). **For the DRI (a question, not a DELTA row; merging does not wait on it):** plan row 3b's "one of the three
trace decoders" saving is **not done**. AR-21 proved the decoder equality false (`decodeTrace_ne_embed`), and no gate
replacing closure's decoder is approved, so closure keeps its own decoder (deliverable 3, below). Trusted lines did
**not** fall: K, S and untied V are +0. The reduction is 1,951 untrusted C and P lines.
`batch_evidence.py --check` stops only at the missing `[gate]` and `[scope]`. They are saved after the chain's gate
(see "After the gate").

Plan: architecture review 2026-10 (`design/arch-review` 6ae55ebb8), section 4.5, row AR-22 ("3b"), batch gate 4.1,
coordination 4.2. `docs/CONSOLIDATION-PLAN.md` step 3, row 3b (line 335). Gate met: AR-21 merged
(`lean/VE/Closure/CoreEquiv.lean`, `docs/arch/AR-21/REPORT.md`). AR-23 (3c, `Closure.Formula.denote` through Core) is
not part of this batch.

## Measured outcome

All numbers are against the merge base `a6d0d389a` (main, merged into this branch at `ac15efb61`). Each comes from
the tool output named here. Main moved three times during the build (`e433588f5`, `53fdabfde`, `a6d0d389a`). Each
time it was merged and the generated files were regenerated. The evidence was measured again after the last merge.

- **Lean.** `git diff --stat a6d0d389a HEAD -- lean/VE` (hand-written files only):
  - 10 files deleted, 1,548 lines (`wc -l` at the base).
  - `Closure/Tableau.lean` is new, with 111 lines.
  - `Closure/CoreEquiv.lean` went from 676 to 119 lines.
  - `CertificateWire.lean`, `Route/Checker.lean` and `Route/Steps.lean` each changed one import line.
- **Trust (D3).** `uv run python tools/trust_map.py --check` reports "against a6d0d389a07b: K +0, S +0, D +0, G +0, tied +0,
  unclassified +0, trusted +0 ... PASS". No allowance was added.

  | Class | Before | After | Change |
  |---|---|---|---|
  | K | 994 | 994 | 0 |
  | S | 14,135 | 14,135 | 0 |
  | untied V | 45,602 | 45,602 | 0 |
  | trusted (K + S + untied V) | 60,731 | 60,731 | 0 |
  | C | 13,170 | 12,789 | −381 |
  | P | 108,677 | 107,107 | −1,570 |
  | T | 37,091 | 36,970 | −121 (`VE/Audit.lean`) |
  | o | 19,708 | 19,656 | −52 |
  | all lines | 248,093 | 245,969 | −2,124 |

  The plan estimated "K 0; removes about 1,550 untrusted lines (C and P) and one of the three trace decoders (D, about
  30 est.)". Measured: K 0, C and P −1,951, D 0. The C and P cut is larger than the plan's because AR-21's 557 lines of
  embedding lemmas also went. **Trusted lines did not fall.** Plan 4.1 item 3 asks Phase C for a reduction. This
  row's reduction is untrusted lines only, because the deleted copy was class C and P. The decoder (D) saving is not
  delivered (deliverable 3). Per file: `evidence/trust.json`, `changed_files`.
- **Statements.** `uv run python tools/lean_statements.py --diff` on the base's and head's `statements.txt`: 8,154 →
  8,033 entries. 0 added, 121 removed, 24 changed. For each of the 24 changed entries, the statement text and the `expr`
  hash are byte-identical, and so is the set of used constant names. Only the `@Module` tag of a moved constant on the
  `-- uses` line differs: `Trace`, `Certificate`, `checkCertificate`, `extraRule`, `embedTrace`, `embedTraces` and
  `embedCert` now live in `VE.Closure.Tableau`. The comparison is per field, in `evidence/statements.json`
  (`changed_all_text_identical`, `changed_all_expr_identical` and `changed_all_uses_names_identical` are all `true`).
  Each of the 121 removed theorems is about a deleted copy, and each has a cover that is in the head's
  `statements.txt` (`removed_all_covered: true`). DELTA lists them one per row. `predicates.txt` loses the 10 deleted
  modules and the 7 predicates they declared, and gains `module VE.Closure.Tableau`.
- **Behaviour (4.1 item 2).** `tools/lean_first_diff.py` over all nine corpora. The base was recorded at `a6d0d389a` from
  its own worktree (`/home/seyran/code/ve-ar22-base`), and the head at `01d1e6030` from this checkout, both at the
  same time. They were compared by `python -m tools.evidence ab ... --delta evidence/ab-delta.json`: "ab PASS".
  - **Result:** 100,522 records the same, 31 unavailable on both sides with identical outputs (R7), 0 unlisted. After
    the reruns below, the two recordings are byte-identical (SHA-256 `a9cf0b43…` for both, `evidence/ab.json`).
  - **The reruns.** In the raw recordings (base `4dd5d23f…`, head `b17f8368…`), 8 pilot `document_check` records
    differed. Each was a time-out on one side only, under load 90 to 110: Lean's 600 s limit, or the Rust checker's
    internal time-out at about 19 s. These came from both sides: 7 were the base's and 1 the head's. Each of the 8
    was run again on both sides with the recorder's own `pilot_check`, via `uv run python docs/arch/AR-20/pilot_rerun.py`
    (AR-20's script, unchanged). Every rerun answered, base and head gave the same answer, and every answer recorded on
    either side equals its rerun (`evidence/pilot-rerun.json`).
  - **Earlier run.** Before the last merge of main, the same A/B against `53fdabfde` (head `73b73ad0d`) gave 100,524
    the same, 29 R7 pairs and 0 unlisted, with byte-identical raw recordings (`41540eaf…`).
- **Lean output differential (OUT, row 3b).** Every `lean_exe` was built in both checkouts. The baseline was saved
  from the base worktree with `tools/lean_output_diff.py --save-baseline`, and the head was compared with `--all`:
  "441 invocations, 441 run on both builds ...; 1 differences, 0 timed out". The one difference is the stderr of the
  `ve_service` corpus session. That session reaches two pre-existing `PANIC at Lean.Json.setObjVal!` lines, and those
  lines are the same on both builds. Only the backtrace frames after them differ: they carry the executable path and
  ASLR addresses, and two runs of the baseline binary differ in the same way. The exit code and stdout are the same,
  and so is stderr once the frame lines are removed (`evidence/out.json`). This is not an output change.
- **Build and audit.** `regen_generated.py --write` after the last merge ran `lake build` and `lean/audit.py`:
  "PASS: 777 source files; 8619 named theorem declarations audited ...; only the declared standard axiom allowlist".
  No axiom or `sorry` was added: `axioms.txt` only loses the removed theorems' lines.

## The deliverables

| Plan row 3b and the task | Commit | Evidence |
|---|---|---|
| 1. `runClosure` and `CertificateWire.runClosureCase` call Core's `replay` behind an atom-free gate, keeping closure's version gate (`@0`, `@1`, second flag `version == @1`); `checkCertificate_eq_core_replay` is the defining equation | `1eccc87b0` | `Closure.Tableau.checkCertificate` (`lean/VE/Closure/Tableau.lean:65-72`) is closure's version gate, the well-formedness checks, then `Core.Tableau.replay E true (c.checker_version == "…@1") 125` of the embedded certificate. Both runners call it unchanged (`CertificateWire.lean` and `Route/Wire.lean`), so they now run Core's replay. `checkCertificate_eq_core_replay` is `rfl`, with its AR-21 statement byte-identical. Tests: `test_closure_core_replay.py` (3 tests, both runners); mutants M1 to M7 |
| 2. Delete `VE/TableauExtended*` (6 files, 1,075 lines) and `Closure/{PathRules,Induction,Substitution,Congruence}` (473 lines); confirm with `lake build`; a file with another user stays | `1eccc87b0` | All 10 deleted, 1,548 lines. No file stayed: no other module imported them once `Closure/Tableau.lean` held the types (the import edits are named below). `lake build` passes ("Build completed successfully"; after the last merge, inside `regen_generated.py --write`). A grep of `lean ve tools tests conformance rust` for the 10 module names finds none outside the generated inventories |
| 3. Keep closure's trace decoder | n/a | Kept: `VE.CertificateWire.decodeClosureTrace` is unchanged. **The plan's "one of the three trace decoders" saving is not done.** AR-21's `decodeTrace_ne_embed` shows that Core's decoder reads an n-ary `atom` invariant, which closure's refuses with `invalid indexed formula`. No gate replacing closure's decoder is approved, and no hypothesis was added. Question for the DRI below |
| 4. `Steps.closure` may go; keep or move the closure `Trace` and `Certificate` types | `1eccc87b0` | The types moved to `lean/VE/Closure/Tableau.lean` with the embedding (`embedTrace`, `embedTraces`, `embedCert`). **`Steps.closure` stays.** The approved statement `VE.Service.FamilyBundle.closure_bundle_sound` names it (its `-- uses` line in `statements.txt`), so removing it would change an approved statement. It is a one-line `abbrev` of `CertificateWire.closureSteps`, which is frozen. `steps_embed` (kept) proves it equals `Steps.core` on the embedding |
| Must not change: verdict, error text of a rejected certificate, step count, wire field, fault order | all | A/B: 0 unlisted, recordings byte-identical. OUT: no output change. `test_closure_core_replay.py` pins the refusal texts on both runners. `steps_embed` is kept, with an unchanged statement |
| `VE.Closure.Formula`, `Closure.Entails`, `Closure.Tableau.checkCertificate`, `Closure.embed` stay | all | All present. `checkCertificate_sound` and `checkCertificate_sound_v0` keep their statements, byte for byte |
| Audited theorem names keep byte-identical statements unless about a deleted copy; each removed theorem listed with its cover in DELTA | `adcec8100`, regenerations | `evidence/statements.json`; DELTA's cover table (121 rows: 61 Core twins, 60 covered by the defining equation) |
| Frozen files: edit only where 3b requires; name each edit | `1eccc87b0`, `262f2d231` | Below, "Frozen edits" |
| Generated files only through `regen_generated.py --write`; rebuild and repin | `adcec8100`, `adc23b806`, `73b73ad0d`, `01d1e6030` | `regen_generated.py --check`: "checked 36 entries". `python3 tools/rust_build.py --check`: "pinned in lean/checkers.lock". `tools/trust-classes.json` has no writer. Its 10 file entries were removed with their files. `Closure/Tableau.lean`'s constants are class C, including `embedTrace`, `embedTraces` and `embedCert`, which moved there from `CoreEquiv.lean`'s P because the checker now runs them. `CoreEquiv.lean` keeps P for `embedEdge` |
| `tools/consolidation-ledger.json`, `tools/layer_policy.py`, `tools/lean-layer-exceptions.json`: remove rows only because their file went | `1eccc87b0` | Ledger: the `VE/TableauExtended*` and 4 closure rows. Layer policy: the 6 `VE.TableauExtended*` module names were replaced by `VE.Closure.Tableau`. Layer exceptions: the 4 edges from `TableauExtended*` into the deleted closure files. `uv run python tools/check_lean_imports.py`: "Lean layer graph kept (777 modules, 18 reviewed legacy edges)" |
| Trust (D3): K, S, untied V at or below base, no new allowance; measured before and after with the plan's estimate | `01d1e6030` | Above (`evidence/trust.json`) |
| Behaviour A/B over all nine corpora; row 3b tests: closure three-way, `rust/fuzz_closure.py`, `test_closure*.py`, OUT; `@0`, `@1`, an atom formula the gate refuses, an unknown version | evidence commits | Above. Row 3b tests on the final Lean (`evidence/row3b-tests.json`): `test_closure.py`, `test_closure_certificates.py`, `test_closure_core_replay.py`, `test_closure_induction.py`, `test_closure_witnesses.py`, and the closure-carrying three-way suites `test_data_three_way.py` and `test_p0_three_way.py` gave "95 passed, 3 skipped". The 3 skips are the pre-existing "outside Rust scope" cells. `rust/fuzz_closure.py` gave 3,000 cases, 3,000 agreements. `test_closure_core_replay.py` covers `@0`, `@1`, `@2`, Core's version string, an n-ary `atom` invariant and conclusion, a stale binding and an unknown rule |
| Seeded bugs (a) drop the atom-free gate, (b) `true` for `version == @1`, (c) change a refusal text | `171a04dd3` (spec), `3b7a0acaf` (run) | 7/7 killed (below) |
| Evidence in `docs/arch/AR-22/` with `evidence.toml`, each file under 1 MB; `batch_evidence.py --check` | evidence commits | `ls -l docs/arch/AR-22/evidence`: the largest file is `statements.json`, about 30 KB. The check is under "Tests" |

### Frozen edits (`lean/VE/Route/frozen-sources.sha256`)

Handled as AR-20 handled its `CertificateWire.lean` edit. Each edit is the smallest one row 3b requires: the module
the file imported was deleted. The frozen list was regenerated, not edited by hand (`regen_generated.py --write`,
`adcec8100`). `CertificateWire.lean`'s pin in `ve/assurance-manifest.json` was updated with the line count unchanged,
and its two ranges were reviewed. They did not move, because only line 3 changed (`262f2d231`). `tests/test_assurance_manifest.py`:
"139 passed".

- `lean/VE/CertificateWire.lean:3`: `import VE.TableauExtendedChecker` → `import VE.Closure.Tableau`. No other line changed.
- `lean/VE/Route/Checker.lean:3`: `import VE.TableauExtendedChecker` → `import VE.Closure.Tableau`. No other line changed.
- `lean/VE/Closure/{Consequence,Paths,Syntax}.lean`: not edited.

### The atom-free gate

Closure's certificate types have no n-ary `atom`. `Trace.induct` carries a closure `Formula`, which `embedClosure`
maps into Core without one. Closure's decoder is the gate in front of Core: it refuses an `atom` invariant or formula
with its own text, `invalid indexed formula`, before Core's replay sees anything. Seeded bugs M1 (decoder side) and
M2 (embedding side) show that each half is tested.

## Seeded bugs

`docs/arch/AR-22/mutants.json`, run by `uv run python tools/mutants.py docs/arch/AR-22/mutants.json --evidence
docs/arch/AR-22/evidence/mutants.json`: "mutants: 7/7 killed". Before each mutant, the unmutated baseline of its
command passed (`baseline_exit` 0). For the test mutants, each command rebuilds `ve_conformance` and `ve_service`,
repins them in a scratch copy of `checkers.lock`, and runs the named tests. Only Lean product code changed in this
batch (Python product: none; Rust: none). Every mutant is in a Lean file this batch changed.

| Id | File | Seeded bug (task item) | Failing test or build line |
|---|---|---|---|
| M1 | `lean/VE/CertificateWire.lean` | (a) decoder half of the atom-free gate: an undecodable invariant becomes `top` instead of being refused | `test_closure_core_replay.py::test_certificate_runner_keeps_closures_version_gate_and_refusal_texts`, `::test_route_runner_keeps_closures_version_gate_and_refusal_texts` |
| M2 | `lean/VE/Closure/Tableau.lean` | (a) embedding half: `embedTrace` hands Core an n-ary `atom` in place of the invariant | `::test_certificate_runner_keeps_closures_version_gate_and_refusal_texts`, `test_closure_induction.py::test_induction_python_lean_differential` |
| M3 | `lean/VE/Closure/Tableau.lean` | (b) `true` in place of `version == @1` | `::test_certificate_runner_keeps_closures_version_gate_and_refusal_texts`, `test_closure_induction.py::test_induction_python_lean_differential` |
| M4 | `lean/VE/Closure/Tableau.lean` | (b), the same edit, against the defining equation | `lake build VE.Closure.CoreEquiv`: `CoreEquiv.lean:58:0: maximum recursion depth has been reached` (the `rfl` of `checkCertificate_eq_core_replay`), then `:73:8: (kernel) unknown constant 'VE.Closure.CoreEquiv.checkCertificate_eq_core_replay'` (`checkCertificate_v0`) |
| M5 | `lean/VE/CertificateWire.lean` | (c) refusal text: `unknown tableau rule` → `unknown closure tableau rule` | `::test_certificate_runner_keeps_closures_version_gate_and_refusal_texts`, `::test_route_runner_keeps_closures_version_gate_and_refusal_texts` |
| M6 | `lean/VE/CertificateWire.lean` | (c) refusal text: `certificate is stale or bound to different inputs` → `certificate is stale` | `::test_certificate_runner_keeps_closures_version_gate_and_refusal_texts` |
| M7 | `lean/VE/Closure/Tableau.lean` | the version gate accepts `@2` instead of `@0` (`@0` certificates keep their verdicts) | `::test_certificates_without_induction_keep_their_verdict_at_both_versions`, `::test_route_runner_keeps_closures_version_gate_and_refusal_texts`, `test_closure_induction.py::test_previous_closure_version_replays_all_original_rules` |

After the run, `git status` showed the sources restored. `lake build` passed ("Build completed successfully (1296
jobs)"), and `regen_generated.py --check --only checker-pins` gave "checked 1 entries".

## Tests

- **Selected tests**, once, on the finished code after the last merge: `zsh .../mac-pytest.sh --select -- --base
  a6d0d389a --run`. It ran 6 shards on the Claude cloud runner (run `arch-20261105-1-01d1e603-t152037`), exit 0:
  84 + 85 + 85 + 86 + 87 + 64 = 491 units, all passed. `tools/select_tests.py` selects 476 of 552 test units. The
  selection is wide because `CertificateWire.lean` is imported widely. It is not every unit, and it includes every
  closure test file and `test_assurance_manifest.py`. No test in `main-known-red.txt` was selected.
- `tests/test_assurance_manifest.py` after the manifest order fix (`5c4fe4156`): "139 passed".
- `uv run python tools/gate_collection.py --check --prebuilt`: "32854 collected, 32851 at a6d0d389a…; 3 added, 0
  removed by a trailer, 0 refused, 0 stale and 0 malformed trailers". The 3 added are `test_closure_core_replay.py`'s
  tests. No test was removed or renamed, so no `Test-removed` trailer is needed.
- `uv run python tools/repo_map.py --check`: "PASS: 42 modes, each with its schema file". `uv run python
  tools/assurance_manifest.py --check`: exit 0.
- `batch_evidence.py --check docs/arch/AR-22`: stops at `[scope]`/`[gate]`, which are saved after the gate (as AR-21).
  Its other functions were run on the saved files: `mutant_problems` and `mutant_source_problems` at HEAD, and
  `tools.evidence.ab.problems` with the recorded head `01d1e6030` and base `a6d0d389a`. Each returned `[]`. The
  check itself, at `7a67d0a32`, reports "evidence/scope.json: no such evidence file" (it reads the scope first).
- Not run by me: the full gate (`tools/gate.py`). The chain runs it on the final HEAD.

## Coordination

At the start, `git diff --name-only main...<branch>` was run for every `lean-first/*`, `feature/*`, `infra/*` and
`foundation/*` branch not yet in main, against this batch's files.

- **Generated files (R12):** the overlaps were `statements.txt`, `declarations.txt`, `axioms.txt`, `predicates.txt`,
  `Audit.lean`, `checkers.lock`, the frozen list, the code map and the generated manifest parts.
- **Hand-written shared tables:**
  - `tools/trust-classes.json`: ap-3dc, ci-5, jt-3b, qt-a4b, sn-b6c, me-1, arch-20261105-2 and others. This branch
    only deletes the 10 deleted files' entries and adds `Closure/Tableau.lean`'s entry, with main's key order kept.
  - `tools/layer_policy.py`: df-5 and et-4b each edit a different line (another module list).
  - `tools/consolidation-ledger.json`: foundation/me-1 edits another row.
  - `ve/assurance-manifest.json`: ap-3dc, ci-5, et-4b, qt-a4b and me-1. This branch changes only the
    `CertificateWire.lean` pin. A merge driver had sorted the file; `5c4fe4156` restores main's order.
- No in-flight branch edits `lean/VE/TableauExtended*`, `lean/VE/Closure/`, `lean/VE/Route/{Checker,Steps}.lean` or
  `lean/VE/CertificateWire.lean`.

## For the DRI: closure's trace decoder (question only)

Replacing closure's `decodeClosureTrace` with Core's decoder plus an atom-free check would leave one closure-shaped
decoder fewer (D, the plan estimates about 30 lines). It would not change verdicts if the check refuses with
closure's exact text, `invalid indexed formula`, at the same point in the fault order. That needs its own statement:
the composition equals closure's decoder on every input, including the fault order. Without that statement it is a
change to the refusal path, which this batch must not make. I think the saving is too small to be worth a new trusted
statement now. AR-23's semantics change (`Closure.Formula.denote` through Core) does not need it. Asked, not done.

## What AR-23 may now do

- Closure's tableau soundness no longer has a closure-specific proof. `Closure.Tableau.checkCertificate_sound` applies
  `Core.Tableau.replay_sound` and `VE.Core.entails_closure`. When AR-23 redefines `Closure.Formula.denote` as
  `(embedClosure a).denote`, it does not need to restate the 61 deleted closure soundness lemmas, which were the main
  users of closure's own denotation.
- Statements whose `-- uses` line names `VE.Closure.Formula.denote` went from 29 at the base to 14 at the head
  (`awk` over `statements.txt` at each commit). AR-23 must keep these 14, including `conservativity` and
  `closure_route_acceptance`, as row 3c asks.
- `Closure/{Paths,Finite}` are untouched here. Nothing that was deleted imported them, so 3c's aliases need no
  change in this batch's files.

## After the gate

The scope, the A/B and the gate must name the commit the chain gates (`<G>`). After that gate, make one report commit
that changes only `docs/arch/AR-22/`:

    cp gate-result.json docs/arch/AR-22/evidence/gate.json
    uv run python -m tools.evidence scope --base main --head <G> --out docs/arch/AR-22/evidence/scope.json
    uv run python -m tools.evidence ab ~/.cache/ve-ar22b/base2.jsonl ~/.cache/ve-ar22b/head2.jsonl \
        --base-commit a6d0d389a07b606e27881aacad9b01be8e8844ca --head-commit <G> \
        --out docs/arch/AR-22/evidence/ab.json --delta docs/arch/AR-22/evidence/ab-delta.json \
        --corpus probe conformance readings pilots discourse rights quantity norm_defaults document
    uv run python tools/batch_evidence.py --check docs/arch/AR-22 --report-commit HEAD

The head recording was made at `01d1e6030`. From there to `<G>`, `lean/` and `rust/` are unchanged. The only change
under `ve/` is `5c4fe4156`, which restores main's entry order in `ve/assurance-manifest.json` with the same content.
The base recording was made with that order, and `ve/assurance.py` reads `lean_decoders` only to render the doc table.
If main moves again before the merge, the A/B must be recorded again against the new merge base.

## Spec re-read

- `checkCertificate` against `docs/CONSOLIDATION-PLAN.md:335`: it keeps "closure's own version gate (`@0` and `@1`,
  second flag `version == @1`)". `Closure/Tableau.lean:67-71` accepts exactly those two strings and passes
  `c.checker_version == "ve-tableau-closure-checker@1"` as the second flag. The first flag is `true`, as in AR-21's
  `checkCertificate_eq_core_replay` statement, which is unchanged.
- "`runClosure` and `CertificateWire.runClosureCase` call the Core `replay`": both call
  `Closure.Tableau.checkCertificate`, which is now defined as Core's `replay` (`rfl`).
- "behind an atom-free gate": closure's decoder (`CertificateWire.lean`, `decodeClosureTrace` and `decodeFormula`)
  and closure's types. Tested by the `atom-invariant` and `atom-conclusion` cases on both runners. Mutants M1 and M2.
- "Error text for rejected certificates must not change" (row 3b, risk column): the A/B is byte-identical, and the
  test pins `unknown tableau rule`, `certificate is stale or bound to different inputs` and `invalid indexed formula`.
  Mutants M5 and M6.
- The deletion set against plan row AR-22 (`ARCHITECTURE-REVIEW-2026-10.md:1127`): "`VE/TableauExtended*` (6 files,
  1,075 lines) and four closure files (473 lines)". Measured with `wc -l` at the base: 1,075 and 473.
- DELTA's R7 rows against DRI-RULINGS R7: "unavailable on both sides with identical outputs". Each row's records are
  byte-identical on both sides: the scratch script that wrote `evidence/ab-delta.json` asserts it per record, and
  `tools.evidence ab` refuses an R7 pair that is not identical.

## Self-review against BUILDER-CHECKLIST

1. Every Lean answer typed and contained: N.A. No relay, schema, route field or binding changed (A/B 0 unlisted,
   `evidence/ab.json`; OUT no output change, `evidence/out.json`).
2. Every deliverable built, no rule broken: PASS. "The deliverables" maps each line to a commit and its evidence.
   Deliverable 3's decoder saving is not done, with the reason (`decodeTrace_ne_embed`) and a question for the DRI.
   `Steps.closure` is kept because an approved statement uses it. No Python copy of a Lean decision, no report test
   and no per-batch mutant script were added. The pilot rerun reuses AR-20's script. Coordination found no source
   overlap.
3. Tests can fail: PASS. 7/7 seeded mutants were killed, each by a named test or the build of
   `checkCertificate_eq_core_replay` (`evidence/mutants.json`). Trust mutants (13a): N.A., no trusted growth (+0).
4. Python, Lean and Rust agree; valid inputs pass: PASS. The corpus A/B has 0 unlisted. `rust/fuzz_closure.py`: 3,000
   of 3,000 agree. `test_p0_three_way.py` and `test_data_three_way.py` pass (`evidence/row3b-tests.json`).
5. R8 binding: N.A. No field read from a Lean answer changed.
6. Gate evidence matches the final HEAD: PASS for the parts this batch can do. Main was merged three times. The scope
   base is `git merge-base HEAD main` (`a6d0d389a`), and the A/B, trust, statements, OUT and row 3b tests were
   measured again against it. "After the gate" re-saves the scope, the A/B and the gate for `<G>`.
7. No unsigned item: PASS. DELTA's Ruling cells are R7 only, and the trust budget is +0. The decoder question is not
   a DELTA row.
8. Every user-visible change in DELTA: PASS. The A/B diff is empty apart from R7 pairs, all in
   `evidence/ab-delta.json`. OUT shows no output change.
9. Test selection finds the affected tests: PASS. `select_tests.py` selects 476 of 552 units, including the files
   whose tests kill M1 to M7 (`test_closure_core_replay.py`, `test_closure_induction.py`).
10. Lean statements say what is claimed: PASS. M4 breaks the build of `checkCertificate_eq_core_replay`. No statement
    changed (`evidence/statements.json`), and no hypothesis was added.
11. Budgets fail closed: N.A. No budget, limit or deadline changed. The replay fuel stays 125, which is the same in
    the defining equation.
12. No CPU or memory regression: PASS. The closure path now runs Core's replay, which takes the same steps
    (`steps_embed`). On the A/B, every record that timed out on one side answered the same on both sides when run
    again. The whole-UDHR pair timed out on both sides (pre-existing, L75). No step-count test was needed: no eager
    pattern was introduced.
13. Removed tests have trailers: PASS. `gate_collection.py --check --prebuilt`: 0 removed, 0 refused, 0 stale, 0
    malformed.
14. Both directions, cited evidence, spec re-read: PASS. Every gate is tested on both sides on both runners: `@0` and
    `@1` accepted, `@2` and Core's version refused, a closure invariant accepted and an `atom` refused, a fresh binding
    accepted and a stale one refused. The claims above cite their commands, and the spec re-read is listed.
15. The four classes: PASS. (a) No overclaim: "unchanged" and "none" claims cite the A/B, OUT and
    `statements.json`, and the decoder saving is written as not done. (b) No silent cut: deliverable 3 is the task's
    own instruction, and `Steps.closure` was optional ("may go"). (c) Every new check can fail: M1 to M7. (d) Limits
    are charged before work: N.A., no limit changed.
