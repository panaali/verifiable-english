# ap-3b build report: rendering and paraphrases (part 2 of AP-3; Lean only)

**No DRI signature is reserved.** Trust growth is S +46, K +0, signed by standing ruling R16 ([DELTA.md](DELTA.md)
row 1). Nothing is cut to ap-3bb: every deliverable the item names is built. One spec gap is recorded for ap-3c's
bounded re-check (section 6).

Plan: [act-phrases-PLAN.md](../../spec/act-phrases-PLAN.md) section 4 "AP-3", 2.3, 2.6. Spec:
[act-phrases.md](../../spec/act-phrases.md) 5.5, 6.2, D-23, D-32, E9, P12n. Both files on main (`0e7a813e8`) equal
`research/act-phrases-p1` at `bb5b2f90d` (ap-3's report, unchanged since). DRI-DECISIONS-PHASE2: AP2 (this part
claims no unit), AP4 (D9 (i): no change here, `meaning` is ap-2c's). The work is a restore of `wip/ap-3b`
(`9c5bb9fe0`, an ancestor of main whose rendering ap-3's commit `28e144cca` cut) onto main's `VE.Acts.Tree`.

## 1. Statement gate

The spec's statement review converged on FIX, draft 2 applied it, and `act-phrases-p3ver1` verified it: PASS.
`distinctTexts_ok` and `paraphrases_nodup` equal draft 2's text (spec 6.2) after whitespace normalisation: the
source of `paraphrases_nodup` is now written with draft 2's untyped binders `{fx op f what Rs ps}` (wip had typed
binders; the elaborated statement and its `expr` hash in `lean/statements.txt` are the same). The 14 `table_*`
statements are unchanged: `lean/statements.txt` only gains `distinctTexts_ok`, `firstEqualPair_none` (a helper) and
`paraphrases_nodup`.

## 2. Plan rows delivered

| Row | Status | Where |
|---|---|---|
| Rendering (5.5): `Atom.normal`, `tokText`, `Atom.text`, `partAct` (with `joinWord`, `Part.toks`, `listToks`, `Filler.toks`, `tokStr`, `Atom.withTo`) | **done**; this item owns `Atom.normal` (ap-2d adds `Atom.canon`, `normalOk`, `read_normal` beside it) | `lean/VE/Acts/Linearize.lean` |
| Paraphrases (6.2): `listText`, `Act.text`, `Simple.text`, `Op.inf`, `modalText`, `sentence`, `paraphrase`, `numbered`, `distinctTexts`, `paraphrases`; `distinctTexts_ok`, `paraphrases_nodup` | **done**, proved, audited | `lean/VE/Acts/Table.lean` (after the table; it now imports `Linearize`) |
| D-23, D-32 | **done**: D-32's text is `distinctTexts`'; D-23's list is `numbered (paraphrases …)` (its prefix is written by `readingOf`, ap-3c) | `Table.lean` |
| E9's exact text | **done**: a `#guard` on spec 11.3's whole E9 string, D-23 prefix included | `TableExamples.lean` "Paraphrases" |
| P12n | **done**: a `#guard` on the four texts of spec 11.4, in derivation order (wip checked only the count) | `TableExamples.lean` "Paraphrases" |
| `meaningTexts` (D-15) | not named in this item; it goes with `checkAct` (D-15) in ap-3d | — |
| `elaborate` and the rest | ap-3c, ap-3d (ap-3's report, section 6) | — |

Not edited: `Grammar.lean`, `Syntax.lean`, `Tree.lean`, Table.lean's statements, `Norms/Wire.lean`, any route.

## 3. Seeded bugs and mutants (Lean only; no Python or Rust product code changed)

[`seed_bugs.py`](seed_bugs.py) plants each bug, cuts Table.lean's theorems (so a fixture must fail, not a proof),
builds `VE.Acts.TableExamples` and restores. It refuses to run when a new definition has no bug. Result,
[`mutants.json`](mutants.json): all 36 bugs KILLED by a failed `#guard` of `lean/VE/Acts/TableExamples.lean`; the
restored build exits 0. Per definition (file `lean/VE/Acts/Linearize.lean` for the first ten, `Table.lean` after):

| Definition | Bugs (all killed) |
|---|---|
| `partAct` | `part-act-always-to` (claim B1: *to* only when plain) |
| `joinWord`; `Part.toks`; `Filler.toks` | `join-word-nor-as-or`; `part-words-first-only`; `filler-one-dropped` |
| `listToks` | `list-two-comma`, `list-many-no-comma` |
| `Atom.normal` | `to-word-misspelt`, `be-word-dropped`, `prep-marker-dropped`, `object-after-markers` |
| `tokStr`; `tokText` | `slot-number-shifted`, `fixed-not-folded` (A19); `text-separator`, `comma-spaced` |
| `Atom.withTo`; `Atom.text` | `with-to-ignored`, `with-to-default-true`; `text-without-fixed` |
| `listText`; `Act.text`; `Simple.text` | `list-text-many-as-two`, `list-text-two-comma`; `act-text-nor-as-or`, `act-text-subject-kept`; `simple-whole-no-form` |
| `Op.inf`; `modalText`; `sentence` | `right-without-to`; `right-default-entitled` (the spec's default), `must-not-as-must`; `sentence-no-subject` |
| `paraphrase` (claim B2: E9, P12n) | `paraphrase-no-gloss`, `paraphrase-and-gloss-as-or`, `paraphrase-two-semicolon`, `paraphrase-many-last-dropped` |
| `numbered` | `numbered-from-zero` |
| `firstEqualPair`, `distinctTexts`, `paraphrases` (claim B3: D-32) | `equal-paraphrases-listed`, `equal-pair-second-off`; `equal-pair-from-zero`, `distinct-texts-reversed`; `paraphrases-unchecked` |

- **Constructor sweep** (same script): every `Op` in `Op.inf` and `modalText`, `Role` in `partAct`, `Tok` in
  Linearize, and join word in `joinWord` and `Act.text`, swapped for each sibling: 105 rows, 21 KILLED, 84 INVALID
  (Lean refuses a redundant or missing case or a type error), 0 survivors.
- **trust_mutants** (`mac-pytest.sh --trustmut -- --max-mutants 1000 --jobs 6`, ve-mac-1, on `9362e9f1`, the final
  Lean): 5 definitions with operators, 214 mutants: 173 KILLED, 0 SURVIVOR, 0 UNKNOWN, 16 INVALID, 25 ALLOWED, 0 NOT
  RUN ([`trust-mutants.json`](trust-mutants.json)). The allowances
  ([`trust-mutants-allow.json`](trust-mutants-allow.json), carried from wip) are 5 equivalent survivors (`take 1` and
  `reverse.take 1` of `Atom.normal`'s *to* and *be* lists, which hold at most one token, and `(acc.take 1).isEmpty`,
  which is `acc.isEmpty`) and 20 mutants that do not elaborate.
- **Data types** (`tests/test_acts_tree_mutants.py`, ap-3's sweep): `Table.lean` now imports `Linearize`, so the test
  assembles `Linearize.lean` with the product modules. The rendering matches `Join`, `Part`, `Filler`, `Modifier` and
  `Atom`'s fields, so a dropped or added constructor or a retyped index is now refused there (`is not a field of
  structure` joins `REFUSED`, with a unit case). A swap of two field names still elaborates in the rendering, so the
  test now requires those mutants to be KILLED by a fixture. All 14 tests pass.

## 4. Trust

`trust_map.py --check`: PASS. K +0, S +46 (Linearize.lean, the ten definitions above), V +0, trusted +46; the
paraphrase section is G[R] +63 (not trusted); the fixtures are T. Recorded with `--allow`, signed by R16 (DELTA row
1); FOLLOW-UPS "## ap-3b" asks for the ties pass (tie `Atom.normal` to the grammar through ap-2d's `read_normal`).

## 5. Size, tests and checks

- **Size** (`git diff --numstat` against the merge base, hand-written): Linearize.lean 63, Table.lean +92/-3,
  TableExamples.lean +96/-2, `lean/VE.lean` 1, `tests/test_acts_tree_mutants.py` +13/-8, `tools/trust-classes.json`
  +31/-1, `seed_bugs.py` 249, the allow file 13, DELTA 22 and this report 151. About 570 without the two documents and
  about 745 with them: over the ~600 guideline by the documents, with nothing left to cut (the product and its
  fixtures are about 250 lines; the evidence script is required).
- `lake build` (1,115 jobs) passes. `python3 lean/audit.py`: PASS (636 files, 7,143 theorems).
  `regen_generated.py --check --skip route-cases`: 32 entries current. `route-cases` was skipped in `--write` and
  `--check` because its writer needs the Rust binary, which this worktree has not built; no route changed, and the
  chain's gate checks it.
- `gate_collection.py --check --prebuilt`: 19,535 collected; 0 added, 0 removed, 0 refused, 0 stale, 0 malformed.
- **Selected tests:** `mac-pytest.sh --select -- --base 0e7a813e8 --run` on ve-mac-1, HEAD `dc1469909` (clean): 84
  of 466 units, among them `lake build` (which builds every guard the seeded bugs break) and
  `tests/test_acts_tree_mutants.py`. Exit 0, 0 failed. An earlier run (`ce4767c14`) failed only
  `tests/test_acts_tree_mutants.py` (section 3, fixed in `dc1469909`). No test in `main-known-red.txt` was hit.
- **Not run:** the full gate (the chain runs it on the final HEAD), AP-7, any pilot.
- **Pilot bytes expected to move:** 0 B (*estimate*): no route reads the rendering yet.
- **Overlap:** no in-flight branch (`lean-first/*`, `feature/*`, `infra/*`, `foundation/*`) edits `lean/VE/Acts/`.
  `feature/df-2`, `feature/jt-2`, `foundation/me-1` and `infra/arch-AR-1` edit the shared root `lean/VE.lean` or the
  generated `lean/VE/Audit.lean`, which merge as unions or are regenerated.

## 6. Deviations and the spec gap

- **The plain predicate's form (for ap-3c's bounded re-check).** `paraphrase` takes the form (*has the right* or
  *is entitled*) as `Option Lexical.Form`, as spec 6.2 writes it. `Regulated` does not carry it, and spec 6.3's
  `ActsDoc` does not either (the decoder reads it from the raw declaration, `Norms.Wire.plainWording`). As directed,
  no field is added: `modalText .right none` is the spec's default, *has the right* (guarded, and the seeded bug
  `right-default-entitled` fails). So an *is entitled* predicate's D-23 text would read *has the right* until
  `ActsDoc` carries the forms or the spec keeps the default. Also in FOLLOW-UPS "## ap-3b".
- **Paraphrases in `Table.lean`**, as on wip and as spec 6.2 groups them; `Table.lean`'s import changes from
  `VE.Acts.Tree` to `VE.Acts.Linearize` (which imports it). Its statements are untouched.
- **The fixtures' own `joinWord`** (ap-3 fix1, a total match on `Join`) is dropped: its guard now runs on the trusted
  `VE.Acts.joinWord`.

## 7. Next items

1. **ap-3c** (ready): `ActsDoc`, `SplitMap`, `readingOf` (writes D-23's prefix around `numbered (paraphrases …)`),
   `elaborateMap`, `elaborate` and its theorems; WG-2 and SC-4 wait for it. It takes the form gap above to the
   bounded re-check.
2. **ap-3d** after ap-2c and ap-3c (with `meaningTexts` and `checkAct`, D-15).

## 8. Self-review against BUILDER-CHECKLIST

1. N.A.: no relayed Lean answer; no mode, route or row is added.
2. PASS: section 2 lists every row the item names with its file; the diff has no Python or Rust product change, no
   report test and no authority switch; overlap in section 5.
3. PASS: [mutants.json](mutants.json) (36 bugs killed, at least one per new definition; sweep 0 survivors);
   [trust-mutants.json](trust-mutants.json) (0 survivor, 0 unknown, every allowance with its reason);
   `tests/test_acts_tree_mutants.py::test_every_mutant_of_a_data_type_is_killed_or_refused`.
4. N.A.: no Python or Rust path renders an act; no existing input changes behaviour.
5. N.A.: no Lean answer is read by Python.
6. PASS: no gate evidence claimed; the selected run is on `dc1469909`; commit list below from `main..HEAD
   --no-merges`, base from `git merge-base`.
7. PASS: DELTA row 1 cites R16 and meets it (per file, `trust_map.py --check`, every new trusted definition killed by
   a named guard, FOLLOW-UPS row); no reserved signature.
8. PASS: no user-visible change (DELTA says why); only the trust row.
9. PASS: `select_tests.py --base 0e7a813e8` selects 84 of 466 units, including `lake build`, which builds
   `VE.Acts.TableExamples`, the target `seed_bugs.py` shows failing.
10. PASS: `distinctTexts_ok`/`paraphrases_nodup` are about the returned value; with the theorems cut each seeded bug
    still breaks a guard (`mutants.json`); statements equal draft 2 (section 1).
11. N.A.: no budget, limit or deadline; the rendering is total.
12. N.A.: no route runs it; each function is one pass over its list.
13. PASS: no test removed or renamed; `gate_collection.py --check --prebuilt` 0 refused, 0 stale, 0 malformed.

## 9. Commits (`main..HEAD --no-merges`)

- this report and DELTA (the last commit)
- `dc1469909` ap-3b: the data-type mutant sweep reads Linearize as product code (Table imports it); a missing field refused there is a refusal; swapped field names of the tree types must still fail a fixture
- `ce4767c14` ap-3b evidence: trust_mutants on the final Lean (mac-pytest --trustmut, ve-mac-1): 173 killed, 0 survivor, 0 unknown, 16 invalid, 25 allowed (5 equivalent take-1 survivors, 20 that do not elaborate)
- `9362e9f12` ap-3b: trust_mutants allow file (Linearize's allowances from wip/ap-3b)
- `26f0b22e9` ap-3b evidence: seeded bugs (36, one or more in each new definition, all killed by TableExamples.lean with the theorems cut) and the constructor sweep (105 rows: 21 killed, 84 refused by Lean)
- `21c2b8621` ap-3b: R16 allowance S +46 (Linearize), K +0
- `b0abdfa6f` ap-3b: rendering (Linearize.lean: Atom.normal, tokText, Atom.text, partAct) and the paraphrases (paraphrase, paraphrases, distinctTexts, distinctTexts_ok, paraphrases_nodup), restored from wip/ap-3b onto main's act trees
