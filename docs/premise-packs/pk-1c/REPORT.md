# pk-1c: `legacy_labels_nodup_of_actKeys` (build report)

No DRI signature is reserved. The one changed approved statement (DELTA S1) is SIGNED by the DRI on 2026-10-27
(`reviews/dri-decisions-20261027-featureplan-gates.md` item 3).

Branch `feature/pk-1c`, base `main` 2d84b832c. Spec: `docs/spec/premise-packs.md` 2.6. The approved
`legacy_labels_nodup` (`docs/spec/premise-packs/SpecStubs_pk1.lean:163`) is false (pk-1 F1′, `cx` in
`lean/VE/NormDefaults/PacksLegacyExamples.lean`). The DRI's decision replaces it with
`legacy_labels_nodup_of_actKeys`, the same statement plus `(hk : ∀ k ∈ VE.Rights.condKeys R, ':' ∉ k.2.1.toList)`.

## 1. What was built

| Deliverable | Delivered | Where |
| --- | --- | --- |
| (1) the repaired theorem, proved, with the DRI's text exactly | yes. The proof is pk-1's candidate (e415f9c32), ported onto `main` without changes. The keys of `condKeys` are distinct (`checkRights` refuses repeated limitation and condition names, and `limActs` is deduplicated). A label is read from the right: condition names are identifiers, the kind word has no `:`, and by `hk` the act key has none, so the rest is the limitation name. Soft labels begin with `s`, rights labels with `r` | `lean/VE/NormDefaults/PacksLabels.lean:342` |
| (2a) F1′'s guards stay, including the refusal `InvalidInput: premise label … is used twice` | yes, unchanged | `PacksLegacyExamples.lean:121–129` |
| (2b) a lemma that `VE.Bridge.identifier` refuses a name containing `:` | `bridge_identifier_sep`. `legacy_labels_nodup_of_identifiers` discharges `hk` from it: when every act key passes the route's identifier check, the labels are distinct | `PacksLabels.lean:280`, `:392` |
| (2c) kernel fixtures on both sides of the new checks | `hk` fails on `cx`, and holds on the six well-formed sources (whose act keys are route identifiers and whose labels are distinct). One source has non-empty `condKeys`. `VE.Bridge.identifier` accepts `p`, `q`, `p9`, `p_q`, `publish_about_permitted` and a 64-byte name. It refuses `:` at the start, middle and end, `x:p`, `p;` (`;` is the character just after `:`), the empty name, `P`, `9p` and a 65-byte name | `PacksLegacyExamples.lean:131–141` |
| (3) seeded bugs | section 2 | `docs/premise-packs/pk-1c/mutants.json` |

`legacy_labels_nodup` is neither stated nor built in `lean/`. No other statement changes. The spec stub and
spec 2.6 still show the old text: they are approved, saved spec documents with their own mutant evidence (M11), so
they are not edited here (see pk-1d).

## 2. Seeded bugs (each planted in the real file, built, restored)

| Id | File | Bug | Fails |
| --- | --- | --- | --- |
| M1 | `lean/VE/NormDefaults/PacksLabels.lean` | `hk` dropped from `legacy_labels_nodup_of_actKeys` (the approved statement, false on `cx`) | `lake build VE.NormDefaults.PacksLabels`: `378:42 Unknown identifier hk` |
| M1b | same | `hk` on the condition names (`k.2.2`), which `cx` satisfies | same build: `379:82` timeout in the injectivity step; `396:77` type mismatch |
| M2 | `lean/VE/Bridge.lean` | `VE.Bridge.identifier` accepts `:` (it maps `:` to `_` before the grammar) | `bridge_identifier_sep` (`PacksLabels.lean:286`, rewrite fails). With that proof replaced by `sorry` for the run, the fixtures alone fail: `#guard` at `PacksLegacyExamples.lean:140` and `:141` |

The item adds no trusted definition (theorems and `#guard`s only), so there is no per-definition mutant. Python
and Rust product code are unchanged.

## 3. Trust, size, checks

- `tools/trust_map.py --check` on the final HEAD: K +0, S +0, D +0, G +0, unclassified +0, trusted +0. No allowance
  and no FOLLOW-UPS row are needed. An inline fixture replaced a 3-line helper definition in the examples file that
  had counted as unclassified.
- Size outside generated files: 236 lines added (`PacksLabels.lean` +195/−1, `PacksLegacyExamples.lean` +18/−2,
  DELTA 13, mutants 10, plus this report).
- `lake build` (1135 jobs) and `python3 lean/audit.py` pass: 7286 theorems, standard axioms only.
  `regen_generated --write` then `--check` pass (33 entries). `check_lean_imports` passes (the new import is
  `VE.Readings.Lines` in `PacksLabels.lean`). `check_*_statements.py` (4 scripts) pass. `gate_collection --check
  --prebuilt`: 0 added, 0 refused, 0 stale.
- Selected tests (`mac-pytest.sh --select`, 72 units including `tests/test_packs_guard_mutants.py`): exit 0,
  0 failures (ve-mac-1, HEAD 63b3060e).
- Pre-existing failures on main: none were hit.
- Pilot bytes expected to move: 0. No evaluated definition changes.

## 4. Next item

- **pk-1d**: make spec 2.6 and `SpecStubs_pk1.lean` name `legacy_labels_nodup_of_actKeys` in place of the
  superseded `legacy_labels_nodup`. The stub's file check (M11) and its `mutants.json` should follow the new name.
  This is a documentation sync after the DRI's amendment.

## Self-review against BUILDER-CHECKLIST

1. N.A.: no relayed answer, schema or relay changed.
2. PASS: section 1 maps every deliverable to a file and line. No Python copy of a Lean decision, no report test, and no in-flight branch touches these files (checked with `git diff --name-only main...<branch>` over every `feature/`, `lean-first/`, `infra/` and `foundation/` branch).
3. PASS: seeded bugs M1, M1b and M2 (`mutants.json`). Each fails a proof or a `#guard`, not a hash step.
4. N.A.: no Python, Lean or Rust behaviour changed. No evaluated definition differs, so there is nothing to A/B.
5. N.A.: no field is read from a Lean answer.
6. PASS: regen, audit and trust were run on the final Lean. The gate runs on the committed HEAD in the chain.
7. PASS: DELTA S1's Ruling cell is `SIGNED by the DRI 2026-10-27 (reviews/dri-decisions-20261027-featureplan-gates.md item 3)` and names the condition tests. Trust +0.
8. PASS: the DELTA states that no output changes (theorems and `#guard`s only), with the reason.
9. PASS: `tools/select_tests.py` picked 72 units, not everything, including `tests/test_packs_guard_mutants.py`, which reads `PacksLegacyExamples.lean`.
10. PASS: M1 and M1b break the proof. `check_rd9_sc1_statements.py` and the other statement checks pass. The added hypothesis has the DRI ruling and the counterexample `cx`.
11. N.A.: no budget, limit or deadline is touched.
12. N.A.: no runtime code changed. The `#guard`s add about 0.1 s to the build of `PacksLegacyExamples`.
13. PASS: no test was removed or renamed (`gate_collection --check --prebuilt`: 0 refused, 0 stale, 0 malformed).

## FIXMAP
- `lean/VE/NormDefaults/PacksLabels.lean`: the label-distinctness proofs of spec 2.6 (soft: `softLabelledU_labels_nodup`; rights: this item).
  - `pk_cond_ident` :245 (condition names are identifiers, from `checkRights`)
  - `pk_identifier_sep` (`VE.Rights.identifier` has no `:`)
  - `bridge_identifier_sep` :280 (`VE.Bridge.identifier` has no `:`)
  - `pk_rights_inj` :298 (reading a rights label from the right)
  - `pk_keyPremise` :311
  - `legacy_labels_nodup_of_actKeys` :342 (the DRI's statement)
  - `legacy_labels_nodup_of_identifiers` :392 (the route discharge)
- `lean/VE/NormDefaults/PacksLegacyExamples.lean`: F1′ (`cx`) :111–129, the `hk` fixtures :131–136 and the `VE.Bridge.identifier` fixtures :137–141.
- `docs/premise-packs/pk-1c/{DELTA.md,mutants.json,REPORT.md}`: the evidence.
- Regression: `cd lean && PATH=~/.elan/bin:$PATH lake build VE.NormDefaults.PacksLegacyExamples`; `uv run pytest -q tests/test_packs_guard_mutants.py`; `python3 lean/audit.py`.
- Generated files: `lean/declarations.txt`, `lean/statements.txt`, `lean/axioms.txt` and `lean/VE/Audit.lean`, through `uv run python tools/regen_generated.py --write`.
- No trust_mutants run: there is no trusted growth.
## END FIXMAP
