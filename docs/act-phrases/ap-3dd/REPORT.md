# ap-3dd build report: `elaborate_faithful` (part of AP-3; Lean only)

**Status:** built. `elaborate_faithful` and its twin are proved with no `sorry`; the selected tests pass (219 units, 0 failed).
**One statement changed, signed by the DRI:** `elaborate_faithful` gains `h0`, because the spec's text is false for a source
that is not well formed (`dri-decisions-20261102-ap-3dd.md`). **No DRI signature is reserved.** Trust K +0, S +8 (R16).
Size 870 hand-written lines, over ~600, signed in `dri-decisions-20261102-ap-3dd-size.md`. Pilot bytes expected to move: 0 B.
Not run by me: the full gate (the chain runs it). Next: ap-3dc.

Plan: AP-3 at `80f056f9e`. Spec: `docs/spec/act-phrases.md` 6.4, 6.6, 11.3. Read first: ap-3d's and ap-3r's REPORTs.
**Synthesis round 2:** this item implements none of `edits-act-phrases.md` (items 1-5 and DEC 16 concern `gate_acts`,
ap-1bf, CI-5, cost, joint choices and u0218.s18).

## 1. Statement gate

The statement is false as written, for a reason other than the revised D3 cell. That cell is refused, so it is vacuous
(`#guard sides e17 (one []) == none`, FaithfulExamples.lean:214). The counterexample is `ce` (FaithfulExamples.lean:230):
E1 plus a rule `r0` on the literal name `p027__1`, which the source does not regulate. `namesOk` does not read
`Node.pred`, so `validate` on the result passes once `p027__1` is a part. `elaborate` accepts it and the result is
`WellFormedU`, yet on the one-person empty model `holdsCatala` is false and `IntendedActs` is true. No decoded source is
like this. I asked through `msg.sh`; the DRI signed option (a).

| Condition of the decision | Where |
|---|---|
| (i) `elaborate_faithful` with `(h0 : VE.Norms.WellFormed D.U.D = true)`, under the spec's name, no other hypothesis | `lean/VE/Acts/Faithful.lean:305` |
| (ii) twin, no hypothesis beyond `h` | `Faithful.lean:378` `Decode.decodeElaboratedU_faithful` |
| (iii) spec and plan signature, the twin and its one sentence | `docs/spec/act-phrases.md:1276-1282`; `act-phrases-PLAN.md` (section 4 below) |
| (a) `ce`'s three `#guard`s | FaithfulExamples.lean:232-234 |
| (b) both theorems in the generated lists | `git diff` of `lean/statements.txt` against the base: `+theorem VE.Acts.elaborate_faithful`, `+theorem VE.Acts.Decode.decodeElaboratedU_faithful`, no `-theorem` line |
| (c) E11's guards, and the sign-flip mutant | section 3 |
| (d) the other 6.6 theorems unchanged | the diff of 6.6 below; `Elaborate.lean` is untouched |

`git diff <base> -- docs/spec/act-phrases.md`, in full: the two lines of `elaborate_faithful` become these, and the twin's
five lines follow.

```lean
theorem elaborate_faithful (D : ActsDoc) {U' : VE.NormDefaults.UDoc} (h0 : VE.Norms.WellFormed D.U.D = true)
    (h : elaborate D = .ok U') (S : VE.Structure.{u}) : VE.Norms.holdsCatala U'.D.T S ↔ IntendedActs D S
```

`python3 docs/act-phrases/ap-3dd/check_statements.py`: 4 EQUAL (`readAs`, `IntendedActs`, both theorems).

## 2. Deliverables

| Row | Status | Where |
|---|---|---|
| (1) `IntendedActs`, `readAs`, `elaborate_faithful`, proved | **done** (statement as signed) | `Faithful.lean:18,22,305`; `python3 lean/audit.py`: "PASS: 723 source files; 8013 named theorem declarations" |
| (2) E11's check on both sides, small structures | **done** | FaithfulExamples.lean:153 on; `holdsB_iff` (:113) and `intendedActsB_iff` (:119) tie the guards to the two sides |
| (3) `elaborateMap` mutant, one part's sign flipped | **done** | `part-sign-flipped`, section 3 |
| (4) a mutant in each new trusted definition | **done** | `readAs` and `IntendedActs`, section 3 |
| FOLLOW-UPS row, trust allowance | **done** | "## ap-3dd"; `docs/trust-baseline.json` |
| E5j | not in this item's list | stays with ap-3db (needs the hook) |

**How the proof goes.** `intended_tracks` (`Faithful.lean:263`) carries a predicate of one tree to a predicate of the
other when a map tracks their rules. The proof uses it for a predicate with no parts (`id`) and for part i. The two
trees' fuels differ, so `decides_tracks` (:201) compares them at their sum, by `selects_stable` on both acyclic trees.
Guards agree because they name no split predicate (`refsOk`) and no part (typed in the source, whose environment does
not declare a part: `h0`, `namesOk`).

**The fixtures** cover, each on both sides: one person or one of two breaks one part; the first and the last of five
parts (E3); precedence (E4), a conflict with no value, a chain three deep (fuel 3 against 6); guards and carve-outs, with
a default of allow; a predicate with no parts beside a split one; one atom kept (E2); unspecified predicates (E5);
a decoded document (:221-222). The guards on `reads` (:131) read `readAs` itself, not its finite-model mirror.

## 3. Seeded bugs and mutants (Lean only; no Python or Rust product code changed)

`uv run python docs/act-phrases/ap-3dd/seed_bugs.py`: **10 of 10 KILLED**, restored build exit 0, in
[mutants.json](mutants.json). Each bug is built twice: alone, where the proof must fail; and with the theorem sections
cut and the older fixtures' guards off, where a `#guard` of FaithfulExamples.lean must fail and no other file may.

| id | file | definition | proof fails at | first guard (count) |
|---|---|---|---|---|
| part-sign-flipped | `lean/VE/Acts/Elaborate.lean` | `splitNode` (`elaborateMap`) | Faithful.lean:117 | FaithfulExamples:154 (15) |
| part-guard-dropped | same | `splitNode` | :117 | FaithfulExamples:179 (4) |
| part-carve-outs-dropped | same | `splitNode` | :117 | :195 (1) |
| part-precedence-dropped | same | `splitNode` | :117 | :167 (3) |
| part-default-flipped | same | `splitReg` | :107 | :191 (6) |
| read-as-reads-the-source | `lean/VE/Acts/Faithful.lean` | `readAs` | :278 | :133 (19) |
| read-as-reads-every-name | same | `readAs` | :329 | :135 (11) |
| intended-acts-first-part | same | `IntendedActs` | :368 | :154 (5) |
| intended-acts-last-predicate-only | same | `IntendedActs` | :368 | :204 (4) |
| intended-acts-without-reading | same | `IntendedActs` | :369 | :154 (17) |

The first failing proof for the `Elaborate.lean` bugs is a structural lemma (`mem_splitNode`, `mem_splitReg`), which
restates the definition. The semantic evidence for them is the guards. The `readAs` and `IntendedActs` bugs are planted
in `readM` and `intendedActsB` too, or the tie breaks first and no guard is reached.

**Trust mutants, read exactly:** 0 KILLED, 0 SURVIVOR, 0 UNKNOWN, 0 INVALID, **4 ALLOWED**, exit 0, on `69ffe8726`, in
[trust-mutants.json](trust-mutants.json) (`mac-pytest.sh --trustmut`, `--rescore` of
[trust-mutants-run1.json](trust-mutants-run1.json), cloud pool). So the tool itself counted no kill. The size decision's
"10 killed, 0 survivors, 4 allowed" joins two runs: the 10 are the seeded bugs above.

- `IntendedActs` (`body-true`, `body-false`): a Prop over every structure, which no check can evaluate. The tool's rule
  for this case is an allow reason citing the proofs broken: `elaborate_faithful`, `intendedActsB_iff`.
- `readAs` (`eq-le`, `eq-ne`): a check reaches its relation only through a `Decidable` instance, whose term changes with
  the mutant, so the tool answers UNKNOWN although the guards on `reads` do refute it. It also breaks
  `elaborate_faithful` and `readAs_asStructure`. The reasons are in
  [trust-mutants-allow.json](trust-mutants-allow.json).

## 4. Deviations

1. `elaborate_faithful` has `h0`: section 1.
2. The plan's theorem line was an older form, `(h …) (hw : WellFormedActs D = true) (S …)`, on main and at `80f056f9e`
   alike. I replaced it with the signed signature, as the decision's (iii) asks. The plan's `IntendedActs` draft above
   it is left as it was: "nothing else" changes, and the spec is the statement.
3. **Assurance manifest:** only `FaithfulExamples.lean` has an entry. `Faithful.lean` cannot: an entry for it fails
   `tests/test_assurance_manifest.py::test_every_json_handling_lean_file_is_classified`, which requires the classified
   set to equal the JSON-handling files, and it is not one.
4. `lean/VE.lean` is a hand-kept union file, not generated: two import lines added.
5. `Faithful.lean` does not import `VE.Norms.FlaggedSpec`'s `preds_declared`: `check_lean_imports.py` refuses that
   outward edge, so `denote_preds_congr` reads the typing itself.
6. Regen ran with `--skip route-cases`, which needs the Rust release binary; none of its inputs changed.
7. **Size:** 870 added and 5 removed hand-written lines at `3d94f2a5a` (`git diff --numstat` of the merge base, without
   generated inventories and evidence JSON), plus this report: `Faithful.lean` 386, `FaithfulExamples.lean` 237,
   `seed_bugs.py` 115, `check_statements.py` 38, `trust-classes.json` 38. I measured late; the rule says before the
   second half. Signed: `dri-decisions-20261102-ap-3dd-size.md`, no further growth.

## 5. Trust

`uv run python tools/trust_map.py --check`: "against fe6bf09b8aad: K +0, S +8, D +0, G +0, tied +0, unclassified +0,
trusted +8"; "PASS: K, S and untied [V] within fe6bf09b8aad and the allowances introduced since". `VE/Acts/Faithful.lean`
+8 (S: `readAs`, `IntendedActs`). SIGNED by standing ruling R16; [DELTA.md](DELTA.md) row 1 itemises it. The task expected
no DELTA row for a route answer, and there is none: this row exists because R16 asks a DELTA to itemise trust growth.

## 6. Pilot bytes

0 B expected (*estimate*): theorems and fixtures only. Nothing is claimed before a pilot audit.

## 7. Tests run

- `lake build` (1230 jobs): success. `python3 lean/audit.py`: PASS (quoted above).
- `python3 tools/lean_statements.py --check`: "PASS: 7439 statements". `python3 tools/check_lean_imports.py`: "Lean layer
  graph kept".
- `uv run pytest -q tests/test_assurance_manifest.py`: 139 passed.
- `uv run python tools/gate_collection.py --check --prebuilt`: "31562 collected … 0 added, 0 removed by a trailer, 0
  refused, 0 stale and 0 malformed".
- Selected tests on `3d94f2a5a`: `mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run`: "selected tests ran
  on the Claude cloud (6 shards …); exit=0; 3593s"; six shards of 41, 33, 39, 33, 40, 33 units, all passed (219). Log:
  `/tmp/ap3dd-sel.log`. Only this report changed afterwards. No test in `main-known-red.txt` failed.
- **Not run:** the full gate, the route-cases regen, AP-7, any pilot. **Not synced:** main is 93 commits ahead;
  `git diff --name-only HEAD...main` shows no file under `Acts/` and no act-phrases spec. The merge train syncs.

## 8. Spec re-read

- `readAs`, `IntendedActs`: act-phrases.md:1229-1235 (`check_statements.py`, EQUAL).
- `elaborate_faithful` and the twin: :1276-1282 against `dri-decisions-20261102-ap-3dd.md` item 1 (i)-(iii).
- E11's check: :1761-1763 (both sides false, both sides true); FaithfulExamples.lean:153-156.
- The revised D3 cell: E17 at spec 11.3 against FaithfulExamples.lean:214 (refused, so no claim).

## 9. Next item

ap-3dc (the relay), then ap-4. No work is cut from this item.

## Self-review against BUILDER-CHECKLIST

1. N.A.: no relayed Lean answer; nothing under `lean/VE/Service/` or `rust/` and no Python under `ve/` changes (only one entry in `ve/assurance-manifest.json`).
2. PASS: sections 1 and 2 map each row and condition to a line. The diff has no Python product change and no report test.
   Overlap: no in-flight `feature/`, `infra/`, `lean-first/` or `foundation/` branch edits the Acts files or act-phrases spec (scripted `git diff --name-only main...<branch>`, empty).
3. PASS: `mutants.json` (10 KILLED, each by a proof and a named `#guard`); `trust-mutants.json` exit 0 with 4 allowed, read exactly in section 3.
4. N.A.: no Python or Rust path, and `elaborate` is unchanged (`git diff` of `Elaborate.lean` is empty).
5. N.A.: Python reads no new field.
6. PASS: the base is `git merge-base HEAD main`; the commit list below is `main..HEAD --no-merges`; I ran no gate. The branch is not synced with main (section 7).
7. PASS: DELTA row 1 cites R16; `h0` and the size carry their DRI decisions.
8. PASS: no user-visible change; DELTA says why, and `Elaborate.lean`, `Decode.lean` and every route file are untouched.
9. PASS: `tools/select_tests.py --base …`: 207 of 527 units, including `lake build`, which builds FaithfulExamples.lean, the file every seeded bug fails.
10. PASS: `check_statements.py` 4 EQUAL; the seeded bugs break both theorems; the added hypothesis has its ruling and its mechanised counterexample (`ce`).
11. N.A.: no budget, limit or deadline.
12. N.A.: no route runs this code; the finite evaluator is fixture-only.
13. N.A.: no test removed; `gate_collection.py --check --prebuilt`: 0 refused, 0 stale, 0 malformed.
14. PASS: every guard family has both sides (section 2; `ce` differs where every other document agrees, FaithfulExamples.lean:235); each claim names its command; spec re-read in section 8.

## Commits (`main..HEAD --no-merges`)

- this report (the last commit)
- `3d94f2a5a` ap-3dd evidence: seeded bugs and trust_mutants on the final code (10 killed; 0 survivor, 0 unknown, 4 allowed)
- `69ffe8726` ap-3dd: regenerated inventories and code map; previous trust_mutants JSON kept for the rescore
- `2921d4d6d` ap-3dd: the child-tracking duplicates merged; DELTA (R16 row)
- `4ca9fcdea` ap-3dd: statement check (4 EQUAL); seeded bugs on the final code (10 killed)
- `96bcea4cb` ap-3dd evidence: trust_mutants on the final Lean (rescored): 0 survivor, 0 unknown, 4 allowed; the spec's twin in the section's namespac
- `efd0d63c2` ap-3dd: allow reasons for readAs; first trust_mutants JSON kept for the rescore
- `ea2109c02` ap-3dd: readAs checked directly (trust_mutants survivors M003, M004); allow file for IntendedActs, which no check can evaluate
- `9e6143c3c` ap-3dd: Faithful.lean without the outward import (typing read in denote_preds_congr); roots; regenerated inventories; R16 allowance S +8
- `34afcb0ec` ap-3dd: seeded bugs (10, each in a proof and in a named #guard of FaithfulExamples.lean)
- `b5c1e805b` ap-3dd: elaborate_faithful with h0 and its twin decodeElaboratedU_faithful, proved; E11's fixtures on both sides of the iff; spec and pl
- `236dfbe11` ap-3dd: readAs and IntendedActs; both sides of the iff computed on finite models; counterexample to elaborate_faithful for a source with
