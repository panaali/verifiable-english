# ci-1b report: the rest of CI-1's statements

**Status:** built and proved. Deliverables (1) and (2), with `hw`'s fixtures, are done; (3)'s W16 and 50-segment pin moved to ci-1c (SIGNED, `reviews/dri-decisions-20261108-ci-1b-size.md` item 1). No signature reserved.
**Head:** the commit of this file on feature/ci-1b, based on main e9a6ec8d5.
**What changed:** `lean/VE/Commands/Read.lean` adds proofs only (0 new definitions). `lean/VE/Commands/Examples.lean` adds `hw`'s fixtures. `tools/trust-classes.json` classes the two new fixtures `T`. Inventories are regenerated (R12). Nothing in `ve/`, `rust/` or `tests/` changed.
**Open:** none in this item. ci-1c (W16, the 50 segments) is filed by the DRI. ci-2b discharges `hw` at the relay (below).
**Signature:** none. Trust: K +0, S +0, V +0. No DELTA row, so there is no DELTA.md.

## Deliverables

| Task item | Delivered | Evidence |
|---|---|---|
| (1) decoder half | `declared_of_decode` (`Read.lean:1293`): from `hw : JsonWF j` and `hd`, `declared se = true`. It goes through `strip_vocabulary`, `norms_facts` and `vocabulary_facts`. `readCommand_typed` (`Read.lean:1317`) is ci-1's REPORT statement exactly, and its proof is `readCommand_typed_of_facts … (declared_of_decode hw hd)`. | `cd lean && lake build`: 1311 jobs, success. The facts `#guard` on `E_web` stays (`Examples.lean:241`). |
| (2) six statements | `candidate_guard` :610, `candidate_fills` :624, `guard_limit` :656, `guard_unread` :669, `guard_ambiguous` :704, `refused_classed` :823, plus `guardOf_classed` :785 (RunSplit's second hypothesis) | `python3 lean/audit.py`: "PASS: 780 source files; 8671 named theorem declarations audited …; only the declared standard axiom allowlist". `#print axioms` of `readCommand_typed`, `refused_classed`, `guard_ambiguous`: propext, Classical.choice, Quot.sound. No `sorry`. |
| (3) fixtures | The raw-tree fixture `rawShare`/`rawEnv` (`Examples.lean:304-331`): it fails `jsonWF?`, it is not `declared`, and it reads `one` with `scopeOk` true and `commandOk` false. Every fixture environment passes `jsonWF?` (`:299`). W16 and the 50 segments are ci-1c's. | `lake build VE.Commands.Examples`: success |

DRI ci-1 item 1 conditions. (i) The raw tree fails `jsonWF?`: `Examples.lean:322`. (ii) Every fixture environment passes it: `:299`, covering the ten environments E_web, the four `webWith` variants, `envWith 1`/`2`, `goSorts`, `goCase` and `extraEnv`. (iii) `readCommand_typed` has hypotheses `hw hd h hE hS hR hk` and no others.

Spec re-read. Each statement was compared with spec section 3 at 9a12df17a (lines 362-449), whitespace normalised, by a script: `candidate_guard`, `candidate_fills`, `guard_ambiguous`, `guard_limit`, `guard_unread` and `refused_classed` are equal. `readCommand_typed` is equal once `(hw : VE.Scope.JsonWF j)` is removed, and that is the only difference.

## How the proofs differ from df2dee88b

1. `guardOf_classed` is re-proved. Main's `unreadOf` formats the outcome it already has (ed1aca6ce), so there is no second read at `workBudget`. The spec's `parse_mono` argument (section 3, after the block) is no longer needed. `unreadOf_classed` (`Read.lean:753`) only excludes the one-reading row, and `mapM_length` rules that row out.
2. The decoder half is new work. `Read.lean` now imports `VE.Scope.Theorems` (layer 2, under Read's layer 4). `tools/check_lean_imports.py` reports: "Lean layer graph kept".
3. The decoder section sits after `end Statements`, and the fixtures sit after `extraEnv`'s guards. That keeps both away from feature/ci-5's hunks, which insert just before `end Statements` and append at the end of `Examples.lean` (`git diff main...feature/ci-5 -- lean/VE/Commands/`).

## Where CI-2 discharges `hw`

`decodeRequest` (`lean/VE/Commands/Run.lean:104`, on main) runs `jsonWF?` on the whole request before `decodeSpeechEnvironmentFull` on its `environment` member (`:110`). It refuses a failing tree with `InvalidInput`. ci-2b discharges `hw` with `jsonWF?_sound` and then `wf_get` (`Read.lean`) for the member. CI-2's statements on main still cite `readCommand_typed_of_facts` (`Run.lean:268-279`, `RunSplit.lean:25-29`), not `readCommand_typed`. That move is ci-2b's.

`refused_classed` and `guardOf_classed`, as written here, are exactly the hypotheses of `RunSplit.readInstruction_refused_classed_of_ci1b`. Probe (scratch, not committed): `example := @RunSplit.readInstruction_refused_classed_of_ci1b refused_classed guardOf_classed` type-checks under `lake env lean`. Nothing was added in Python.

## Seeded bugs (`mutants.json`)

Method: each mutant runs in a scratch overlay of `lean/VE/Commands/Read.lean` with the statements cut. The overlay is compiled with `lean --root` against the built tree, then `Examples.lean` is compiled against it. The control (no mutation) has no error.

| Mutant (file) | Fails | With proofs kept, breaks |
|---|---|---|
| `declared` drops the sorts conjunct (`lean/VE/Commands/Read.lean`) | `Examples.lean:323`, the raw-tree fixture | `declared_of_decode`, `readCommand_typed_of_facts` |
| `guardList` keeps the first ambiguous guard (`lean/VE/Commands/Read.lean`) | `Examples.lean:167`, `:170`, W17's two-guard rows | `guard_ambiguous`, `outcome_checked` |
| `refusalOf` classes `limit` as unread (`lean/VE/Commands/Read.lean`) | `Examples.lean:175`, W18 | `guard_limit`, `refused_classed` |
| `rawShare` built well formed (`lean/VE/Commands/Examples.lean`) | `Examples.lean:322`, `:323` | n/a |
| `rawEnv` added to the fixture list (`lean/VE/Commands/Examples.lean`) | `Examples.lean:299` | n/a |

Only Lean product code changed, so all seeded bugs are Lean. There is no new trusted definition, so no per-definition mutant is owed.

## Trust, size, bytes

- `uv run python tools/trust_map.py --check`: "K +0, S +0, D +0, G +0, tied +0, unclassified +0, trusted +0 … PASS". There is no R16 allowance, no trust-mutants run and no FOLLOW-UPS row, since checklist 13a applies only to trusted growth.
- Size: `git diff --numstat $(git merge-base HEAD main)` with generated files excluded gives Read.lean 660 (proofs), Examples.lean 38, mutants.json 58, trust-classes.json 2, plus this REPORT. That is under the DRI's ~900 cap (`reviews/dri-decisions-20261108-ci-1b-size.md` item 1).
- Pilot bytes: 0, as estimated. The web fixture's +273 B is CI-2's to reach, and the 59-segment sum is ci-1c's to pin.

## Tests

- `mac-pytest.sh --select -- --base e9a6ec8d5 --run` at 85de43189 (only this file changed after it): exit 0. Run ci-1b-85de4318-t123901, 444 units in 6 shards, every shard passed. None of the 3 rows in main-known-red.txt is in this area.
- Selection took 429 of 547 units. It widened because of the regenerated inventories (`lean/statements.txt`, `lean/declarations.txt`, `lean/VE/Audit.lean`) and `tools/trust-classes.json`, which many tests read. That cause is known and expected.
- `uv run python tools/regen_generated.py --write --skip route-cases --skip checker-pins`: exit 0. The two skipped entries need the Rust release binary, which this worktree lacks. Rust is unchanged, so their outputs are not stale. They stay for the chain's gate.
- `tools/gate_collection.py --check --prebuilt`: "0 added, 0 removed …, 0 refused, 0 stale and 0 malformed". `tools/repo_map.py --check`: PASS.
- Not run: the full gate (the chain's job) and trust_mutants (no trusted growth).

## Self-review against BUILDER-CHECKLIST

1. Lean answer typed and contained: N.A., no relayed answer or mode changes (`git diff --name-only … -- ve rust tests`: empty).
2. Deliverables: PASS, the table above. The cut is SIGNED before it was made (`dri-decisions-20261108-ci-1b-size.md`).
3. Tests can fail: PASS, `mutants.json` (5 mutants, control clean).
4. Py/Lean/Rust agree: N.A., Lean proofs and fixtures only.
5. R8 binding: N.A., no relay. `hw`'s relay is ci-2b's, named above.
6. Gate evidence: PASS for what a builder runs (selected run ci-1b-85de4318-t123901, `gate_collection`). The full gate is the chain's.
7. Nothing unsigned: PASS. There is no DELTA row and the size cut is SIGNED.
8. User-visible change: N.A., none (`git diff --name-only … -- ve rust`: empty).
9. Selection: PASS, `tools/select_tests.py --base`: 429 of 547 units, widened by the inventories, a known cause. The raw-tree mutant's `#guard` is in `Examples.lean`, which the Lean build in every shard compiles.
10. Statements say what is claimed: PASS. The spec comparison script is above. Each definition mutant breaks its proofs (`mutants.json` `proofs_break`). `readCommand_typed` is about `readCommand`'s value.
11. Limits fail closed: PASS. `guard_limit` is proved, and W18 at budget 0 is `limit` (`Examples.lean:175`, killed by the `refusalOf` mutant).
12. No CPU regression: N.A., no definition changed (proofs and `#guard`s only).
13. Test-removed trailers: N.A., no test removed (`gate_collection`: 0 stale, 0 malformed).
14. Both directions, cited evidence, spec re-read: PASS. `jsonWF?` holds for ten environments (`:299`) and fails for the raw tree (`:322`). `declared` is true for `E_web` (`:241`) and false for `rawEnv` (`:323`). The spec re-read is above.
15. Four classes: overclaim PASS (each "every"/"no" above names its guard or command). No silent cut PASS (DRI asked first). Every new check can fail PASS (the two fixture mutants kill `:299` and `:322`/`:323`). Limits charged before work N.A. (no evaluator or definition added).

Next item: ci-2b (blocked by ci-2 and ci-1b), then ci-1c.
