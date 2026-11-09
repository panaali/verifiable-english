# pk-1-conditions: `Pack.conditions` (REPORT)

Summary: MERGED (review MERGE 2026-10-31; merge 33114d122; branch tip 11c045741). `Pack.conditions` added; every
pack built today exports `[]`, with fixtures and seeded bugs M1-M4. Trust V +2 under R16; pilot bytes 0. Open items:
none here; review F1 is pk-1-conditions-b, F2-F4 are corrected in pk-1-conditions-b (row pk-1-conditions-c, DRI
2026-11-05 cfr2 item 2). No DRI signature is reserved.

No DRI signature is reserved, and there is no DELTA row (no answer changes).

This item implements **edit 1 of synthesis round 2 for premise-packs**: the `Pack.conditions` field only. The edit
was applied on design/syn2-premise-packs (f38ab93aa + 74ac72f59, docs/spec/premise-packs.md:42). Edit 2 (G1b,
PacksVocab.lean, `acceptanceXV`) is not this item and stays in backlog row sa-pack-conditions.

Gate: DRI decision reviews/dri-decisions-20261031-pc-9-prereqs.md item 2 (SIGNED). It applies the approved
order: plan :1495, spec profile-composition.md 1.9, with the field landing in PK-1's own batch before PC-9.

Commits (`git log --oneline main..HEAD --no-merges`, base 8c28fe286):
- 4bb19d2fd: adds Pack.conditions; every pack built today exports `[]`.
- 567c6de4e: the packs guard mutants follow the 7-field constructor; re-pins Layered.lean.

## Deliverables

| # | Row (task / DRI item 2) | Tag | Delivered by |
|---|---|---|---|
| 1 | `conditions : List (VE.SoftNorms.DecisionKey × VE.Formula)` as the last field of `Packs.Pack`, with the spec 1.9 doc comment; `import VE.SoftNorms.Tree` | AGENT | 4bb19d2fd, `lean/VE/NormDefaults/Packs.lean:36-37`, import :3. No cycle: Packs.lean already imported Tree transitively, and Tree's closure does not contain Packs (import-closure probe, see "Checks") |
| 2 | Every `Pack` built on main exports `[]` | AGENT | 4bb19d2fd. `softPack`, `rightsPack` (Layered.lean:58, 62); `eventsPack` (Events/Wire.lean:182, structure-instance notation: `, conditions := []`); Events/WireExamples.lean:285; Defaults/RouteExamples.lean:48; NormDefaults/PacksExamples.lean (soft, rights, weighing, att, ev); PacksLegacyExamples.lean:31. Two sites the task's grep did not list, found by `lake build`: Defaults/WireExamples.lean:76 (an inline pack) and ResponseShape/Encoders/NormDefaults.lean:82 (`⟨·, …⟩`). Each line only gains the field. Senses/Fixtures.lean's `Pack` (a different structure) and the spec stub docs/spec/premise-packs/SpecStubs_pk1.lean are untouched |
| 3 | Condition fixture (DRI item 2) in PacksExamples.lean | AGENT | `softPack_conditions`, `rightsPack_conditions` (:138-139, `rfl` for every `U D` / `R`); `assemble_conditions` (:142, assembly permutes its input, so it adds no condition); `decodeLayered_conditions` (:147, every pack a decoded layered source carries, on both the soft and the rights route, has empty `conditions`); `#guard` on the rights example documents α, γ, γ7, ρ, ε (:156) and `#guard` on the decoded soft documents dα…dσ (:160, each assembles exactly `["soft"]` with empty conditions). `X` and every answer are unchanged: no reader of `Pack.conditions` exists (`git grep -n '\.conditions' -- lean/VE/NormDefaults` lists the fixture and, otherwise, only `RightsDoc` limitation conditions in PacksLabels.lean and PacksLegacyExamples.lean:26), and the existing Packs, PacksLegacy and Layered `#guard`s and theorems build unchanged (`lake build`, "Checks") |
| 4 | Seeded bug: `softPack` exports one dummy condition, so the fixture fails; then restored | AGENT | M1 below |
| 5 | lean/statements.txt regenerated; lean/axioms.txt unchanged | AGENT | statements.txt: +21 lines, the four fixture theorems only (`regen_generated.py --write`). **Deviation:** axioms.txt gains 4 rows, the same four theorems, each on the standard allowlist (`[propext, Classical.choice, Quot.sound]` or fewer). No axiom is added (`python3 lean/audit.py`: PASS). The task expected no new theorem rows. I kept the fixtures as theorems because `decodeLayered_conditions` is the only check that covers every decoded source, not just the example documents |

No reader of `conditions` was added (PC-9 adds the first one).

## Seeded bugs and mutants (docs/premise-packs/pk-1-conditions/mutants.json)

Only Lean product code changed. No Python or Rust code: `git diff --name-only main...HEAD -- ve rust` lists only `ve/assurance-manifest.json`, a generated pin (sha only). Every
mutant was planted, built with `lake build VE.NormDefaults.PacksExamples`, and restored.

- **M1** (lean/VE/NormDefaults/Layered.lean, `softPack` exports `[(.excepted "x", .top)]`) fails
  `softPack_conditions` (PacksExamples.lean:138), the rights `#guard` (:157) and the decoded-soft `#guard` (:161).
- **M2** (Layered.lean, `rightsPack` exports a dummy condition) fails `rightsPack_conditions` (:139) and the rights
  `#guard` (:157).
- **M3** (Layered.lean, `decodeRightsU` assembles `{ rightsPack src.D with conditions := [...] }`) fails
  `decodeLayered_conditions` (:154, unsolved goals). `rightsPack_conditions` does not catch this one.
- **M4** (lean/VE/NormDefaults/Packs.lean, the new field typed `Option (...)`, the R16 mutant of the one new
  trusted declaration) breaks the build at Layered.lean:58 and :62. This is a type-level mutant: the field carries
  no behaviour beyond what each constructor stores, and M1-M3 mutate that.

## Trust (R16)

Command: `uv run python tools/trust_map.py --check` against 2f1318f4ddfd. Result: `K +0, S +0, D +2, G +87,
trusted +4` (`VE/NormDefaults/Packs.lean: trusted +2`, `Serve.lean: trusted +2`). Serve.lean +2 is main's
(scale-stage-timers, merged after 2f1318f4d), not this item's. This item's growth is V +2: the field and its doc
comment. It is recorded in docs/trust-baseline.json, "SIGNED by standing ruling R16 (DRI-RULINGS.md),
pk-1-conditions, 2026-10-18". After that, `--check` prints `PASS: K, S and untied [V] within 2f1318f4ddfd and the
allowances introduced since`. A FOLLOW-UPS.md row "## pk-1-conditions (2026-10-31)" asks for the ties pass.

Trust mutants (`mac-pytest.sh --trustmut -- --max-mutants 1000 --json
docs/premise-packs/pk-1-conditions/trust-mutants.json`, exit 0) found `0 definitions, 0 mutants`. A structure field
gives the operators nothing to mutate, so M4 is the hand mutant for it.

## Checks (commands run)

- `lake build` (full default targets): `Build completed successfully (1192 jobs)`.
- `python3 lean/audit.py`: `PASS: 692 source files; 7813 named theorem declarations audited …`.
- `uv run python tools/regen_generated.py --write`: wrote 34 entries. This needed the Rust release binary, built
  with `python3 tools/rust_build.py`. The one hash this item added to lean/checkers.lock (4bb19d2fd, :252) is a
  `ve_service` pin (the rebuilt Lean service); the `rust_jsonl` list is unchanged (correction, pk-1-conditions-b,
  review F2). The codemap files it rewrote were
  stale on main. After the manifest re-pin I ran `--only assurance-manifest` and `--only assurance-doc`, and
  `--check --only assurance-manifest` passes.
- Import-closure probe (a python script over `import` lines): `Tree->Packs? False`, `Packs already ->Tree? True`.
- Selected tests (`mac-pytest.sh --select -- --base 8c28fe286 --run`, on 4bb19d2fd): 3 failures, all caused by
  this item and all fixed in 567c6de4e:
  - `tests/test_packs_guard_mutants.py::test_each_mutant_fails_a_guard[softPack-30]` and `[rightsPack-31]`: their
    mutant `find` strings used the 6-field constructor. They now find the 7-field one; each mutant still empties
    the labelled premises.
  - `tests/test_assurance_manifest.py::test_decoder_files_are_pinned_whole`: Layered.lean's whole-file pin took
    the new sha. The file has 463 lines, the range 1-463 is unchanged, and only the two constructor lines differ.

  I then reran only those ids: `3 passed` (`mac-pytest.sh -- <ids>`).
- No test in main-known-red.txt was involved.

## Spec re-read

- The field name, type, position (last) and doc comment were checked against
  profile-composition.md:1121 at 3dfadd302: `conditions : List (VE.SoftNorms.DecisionKey × VE.Formula)`, "each
  stated sufficient condition and its decision".
- "`softPack` and `rightsPack` export `[]`" was checked against profile-composition.md:1124 at 3dfadd302 and DRI
  item 2.
- "PK-1 builds the field in its own batch; profile-composition does not touch `Packs.lean`" was checked against
  premise-packs.md:42 at 74ac72f59.

## Size, pilot bytes, next item

- Size: about 52 hand-written changed lines outside generated files, plus mutants.json (97) and this report
  (`git diff --numstat 8c28fe286`).
- Pilot bytes: estimated 0. The field has no reader, so no answer moves. Nothing is claimed before a pilot audit.
- Next: pc-9 (PC-9's `dfltUniformOf`, after pc-3 and pc-6a); sa-pack-conditions (G1b) before the first pack with
  non-empty decls.

## Self-review against BUILDER-CHECKLIST

1. PASS: no relayed answer, schema or response field changes (`git diff --name-only main...HEAD -- ve/backends`, empty; the one ResponseShape line only gains the field in a fixture pack). `uv run python tools/relay_mutation_gate.py`: `45 routes, 146997 mutants, 0 failures`.
2. PASS: each deliverable row is in the table above, with its commit and fixture. In-flight overlap check: no
   branch in `lean-first/* feature/* infra/* foundation/*` touches a changed file (`git diff --name-only
   main...<b>` loop, no hits). No Python copy of a Lean decision, and no permanent report test.
3. PASS: M1-M4 each fail a named theorem or `#guard` (mutants.json). Trust mutants exit 0
   (trust-mutants.json, 0 definitions).
4. N.A.: no answer changes (no reader of the field). Existing corpora: the selected tests pass after the fix (`3 passed`).
5. N.A.: Python reads no new field from a Lean answer.
6. PASS: I ran no gate myself (task rule). The chain gates the final HEAD. The commit list comes from
   `main..HEAD --no-merges`.
7. PASS: trust V +2 is recorded under R16 in docs/trust-baseline.json, with the FOLLOW-UPS row. No DELTA row.
8. PASS: no user-visible change, so there is no DELTA.md. `X` and every answer are unchanged
   (`decodeLayered_conditions`, and the existing `#guard`s build).
9. PASS: the selection included the two tests the change broke (test_packs_guard_mutants,
   test_assurance_manifest), so it finds them.
10. PASS: each new theorem breaks under a mutant (M1 `softPack_conditions`, M2 `rightsPack_conditions`, M3
    `decodeLayered_conditions`). The theorems are about the values the decoders return (`L.packs` of
    `decodeLayered`).
11. N.A.: no budget, limit or deadline is touched.
12. N.A.: one empty list per pack, and no evaluator added.
13. N.A.: no test removed or renamed.
14. PASS: opposite direction: the fixtures accept `[]`, and M1-M3 (a non-empty condition) are refused. Every claim
    above cites its command. The spec re-read is listed above.
