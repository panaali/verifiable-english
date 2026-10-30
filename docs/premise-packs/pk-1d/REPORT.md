# pk-1d: spec 2.6 and its stub name `legacy_labels_nodup_of_actKeys` (build report)

Status: built; no DRI signature is reserved or needed, and there is no DELTA row (no answer changes).
Changed: spec 2.6, the stub, its file check and `mutants.json`, plus one new test file. Bytes 0, trust +0.
Open: the stub has not type-checked on `main` since pk-1 (section 3), so its mutants ran on the tree before pk-1.
Base `main` 79ce58936, branch `feature/pk-1d`. Next item: none in the premise-pack plan for spec 2.6.

## 1. Gates

- **Decision read first.** `reviews/dri-decisions-20261027-featureplan-gates.md` item 3 signs
  `legacy_labels_nodup_of_actKeys`, which adds `∀ k ∈ condKeys R, ':' ∉ k.2.1.toList`.
- **Statement gate: pass.** The built `hk` at `lean/VE/NormDefaults/PacksLabels.lean:344` is the decision's text,
  with the name `VE.Rights.condKeys` written in full. No other statement in the stub or the spec changes.
- **Synthesis round 2 edits:** this item implements none of the eight in `edits-premise-packs.md`, and none of them
  touches 2.6's labels.
- **Overlap:** none of the 267 in-flight branches changes `docs/spec/premise-packs*` (a `git diff --name-only
  main...<branch>` loop printed nothing).
- **Size:** 211 added and 24 deleted hand-written lines before this report (`git diff --numstat`, excluding the code map).

## 2. Delivered

| Deliverable | Where |
| --- | --- |
| (1) spec 2.6: the new name and hypothesis, with a note citing the decision and `cx` | `docs/spec/premise-packs.md:117`, `:128–131`; also the file table (`:286`) and the `sorry` list (`:346`) |
| (2) the stub's statement replaced, with `sorry` | `docs/spec/premise-packs/SpecStubs_pk1.lean:163–165` |
| (2) the file check follows the new name and now also requires `hk` | `SpecStubs_pk1.lean:617–621` |
| (2) M11 follows the new name; M18 and M19 fail on the old statement | `docs/spec/premise-packs/mutants.py`, `mutants.json` |
| (3) a test that the stub's statement equals the built one, with fixtures on both sides | `tests/test_premise_packs_stub.py` (35 tests) |
| (4) other references to the old name | section 4 |

The stub's line count is unchanged up to the file check, so the spec's 53 `stub:NNN` references and the saved `test`
lines stay right. The theorem is therefore laid out differently from the built one. Only whitespace differs.

## 3. The stub does not type-check on `main`

Finding, not caused by this item. On today's tree, `lake env lean ../docs/spec/premise-packs/SpecStubs_pk1.lean` gives
54 errors, the first being ``VE.NormDefaults.Packs.PackKind` has already been declared`: pk-1 built the names the stub
declares. So `mutants.py` stops at "the unmutated stub has 54 errors", and the stub's claim to import `main` unchanged
was stale.

- **What I did.** I ran the stub and all nineteen mutants on `49a926ee7` (the pk-1s merge, the tree the stub was
  written for), from a `git archive` copy with the new stub and `mutants.py` over it. The unmutated stub has 0 errors
  there and `mutants.py` printed `19 of 19 mutants fail`. The stub's header, the `mutants.py` docstring and spec 5 now
  say which tree to use.
- **What that shows.** The 17 earlier records are identical to the saved ones, except M11's new name and message.
- **On today's tree.** The stub's statement was elaborated in a scratch file (`/tmp/pk1d-scratch.lean`, not committed),
  closed by `legacy_labels_nodup_of_actKeys U R hs hw hk`, and `example : @stub_text = @legacy_labels_nodup_of_actKeys
  := rfl` passed (`lake env lean`, exit 0; axioms `propext`, `Classical.choice`, `Quot.sound`). The permanent check is
  the text comparison in the test.
- **One change to `mutants.py` beyond the brief.** M19's error prints as `error(lean.unknownIdentifier):`, which the
  error pattern missed, so the script stopped. The pattern now accepts that form.

## 4. Other references to `legacy_labels_nodup`

- **Updated:** every one in spec 2.6 and 5 and the stub. The old name stays only in spec 2.6's note, which
  `test_the_superseded_name_stays_only_in_the_spec_note` pins.
- **Listed, not changed (dated records of what was true then):** `docs/premise-packs/pk-1/REPORT.md`,
  `pk-1b/REPORT.md`, `pk-1c/REPORT.md`, `pk-1c/DELTA.md`, `pk-1c/mutants.json`, `pk-1s/REPORT.md`.
- **Listed, not changed (out of scope, no Lean outside the stub):** `lean/VE/NormDefaults/PacksLabels.lean:340` and
  `lean/VE/NormDefaults/PacksLegacyExamples.lean` name it as the superseded statement. `tests/` had no reference.
- **Left as it is:** spec 5 and the stub's `planFiles` still place the theorem in `PacksLegacy.lean`; it was built in
  `PacksLabels.lean`. That is the statement-time file split, and moving it would change the stub's checked plan.

## 5. Seeded bugs

All nine are in `docs/premise-packs/pk-1d/mutants.json`, and each was restored. S1 is the item's named seeded bug.
No product code changed, so these cover the stub (Lean) and the spec tooling.

| Id | File | Bug | Fails |
| --- | --- | --- | --- |
| S1 | stub | keeps the old text: `hk` dropped | `test_the_stub_states_the_built_theorem` |
| S2 | stub | keeps the old name | `test_the_stub_states_the_built_theorem` |
| S3 | stub | `hk` reversed (`∈`) | `test_the_stub_states_the_built_theorem` |
| S4 | spec | 2.6 loses `hk`'s text | `test_spec_2_6_states_the_hypothesis_and_cites_the_decision` |
| S5 | spec | the `sorry` list keeps the old name | `test_the_superseded_name_stays_only_in_the_spec_note` |
| S6 | `mutants.py` | M11 keeps its old text to mutate | `test_every_stub_mutant_still_applies_and_is_recorded` |
| M11 | stub | `hs` is `WellFormedSoft (correlate R)` | `SpecStubs_pk1.lean:603`, the file check, WellFormedRights message |
| M18 | stub | `hk` dropped under the new name | `SpecStubs_pk1.lean:603`, the file check, `hk` message |
| M19 | stub | the old name and the old statement | `SpecStubs_pk1.lean:547`, unknown constant |

## 6. Checks run

- `uv run pytest -q tests/test_premise_packs_stub.py`: 35 passed.
- `mac-pytest.sh --select -- --base 79ce58936 --run`: exit 0 on GitHub Actions, 4 shards, 127 of 127 units
  passed (`SHARD n/4: exit 0` lines: 40, 30, 29, 28 units; run `pk-1d-f0e2facc-t360963`, on b859b1be4). Pre-existing
  failures on main: none hit.
- `uv run python tools/trust_map.py --check`: `K +0, S +0, D +0, G +0, tied +0, unclassified +0, trusted +0`, PASS.
- `uv run python tools/regen_generated.py --write`: wrote 34 entries; only the code map changed (new test module).
- `tools/select_tests.py` with a seeded `hk` change in `PacksLabels.lean`: both the map and `--static` selections
  contain the new test. Restored.
- Not run: `tools/gate.py` (the chain runs it on the final HEAD), `lean/audit.py` and a separate full `lake build` (no
  file under `lean/` changed), trust mutants (no trusted Lean changed).

Pilot bytes expected to move: 0.

## Self-review against BUILDER-CHECKLIST

1. N.A.: no relayed answer, schema or relay changed.
2. PASS: section 2 maps each task row to its file; `tests/test_premise_packs_stub.py`.
3. N.A.: no diagnostic or text path changed.
4. N.A.: no Lean answer is read.
5. N.A.: no decoder or request path changed.
6. N.A.: no verdict or budget changed.
7. N.A.: no deadline changed.
8. N.A.: no DELTA row: no answer changes (`git diff --stat` shows no file under `lean/`, `ve/` or `rust/`).
9. PASS: `tools/select_tests.py` selected 127 of 502 units and, with `hk` seeded in `PacksLabels.lean`, contains `tests/test_premise_packs_stub.py`.
10. PASS: scratch `rfl` against the built theorem (section 3); M18 and M19; no `tools/check_*_statements.py` covers this spec.
11. N.A.: no budget, limit or deadline changed.
12. N.A.: no product code changed.
13. N.A.: no test removed or renamed (`git diff --numstat` shows the one new test file and no deleted one).
14. PASS: `test_a_layout_or_proof_change_is_accepted` and `test_a_changed_statement_is_refused` cover both sides of the comparison, `test_the_old_name_is_told_from_its_neighbours` both sides of the name check. Spec re-read: `hk` in spec 2.6 and the stub against `lean/VE/NormDefaults/PacksLabels.lean:344` and the decision's item 3; the note's wording against the sibling review's F1 (it says "the route's decoder", not `VE.Bridge.identifier`, and avoids F2's "kernel fixtures").
