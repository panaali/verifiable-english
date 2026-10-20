# ap-1c build report: the string-lemma library and `check_extends` (act-phrases 4.3, part 1)

**No DRI signature is reserved; nothing stops the item.** Trust +0 (K, S, V unchanged). The item is **cut by the size
rule**: the library and `check_extends` (the first theorem of the task's order) are delivered; `check_no_clause`,
`check_spec`, `fixedOk_unique` and `decodeRegulated_plain` are the next item, **ap-1d** (section 6). Even this first
part is over the ~600-line cap (section 5): `check_extends` needs nearly the whole library.

Plan and spec on `main` at `c5197da78`: [act-phrases-PLAN.md](../../spec/act-phrases-PLAN.md) section 4 "AP-1", 2.1,
2.5; [act-phrases.md](../../spec/act-phrases.md) 1.1-1.3, 4.1-4.3, 14.3. Read first:
[ap-1a's REPORT](../ap-1a/REPORT.md) sections 1, 2 (the 4.3 row) and 6.

## 1. Statement gate

The gate is ap-1a's (its REPORT section 1): the specification's statement review converged on FIX, draft 2 applied
the edits (spec 14.3, SR1-SR16), and the verification passed. None of the 14.3 edits touches 4.3's AP-1 statements.
`check_extends` in `Compat.lean` equals spec 4.3's statement after whitespace normalisation (the spec writes the
full name `VE.Acts.Lexical.check_extends`; the file states it inside `namespace VE.Acts.Lexical`, as ap-1a did for
`wording_subject_first`). Checked by script: equal. No definition ap-1a pinned changed (`check`, `lex`, `decodeFixed`,
`Lexical.lean` and `Wire.lean` are untouched).

## 2. Task rows delivered and not delivered

| Task deliverable | Status | Where |
|---|---|---|
| `words` (`String.split` with `pyWhitespace`) as a split of the character list | **done**: `split_data` (`String.split p = (splitL p s.data).map String.mk`, any `p`, any characters), `words_data`, `mem_words`, `words_cover`; also `splitOn_space` (`String.splitOn " "` as `splitL (· == ' ')`), which `rawLex` uses | `LexicalProofs.lean` 19-160, 439-470 |
| `scanSlots` commuting with that split (a slot never spans a space) | **done**: `splitL_out`, `wordsL_out`, `word_out`; with `out`'s unfolding equations (`out_cons`, `out_slot`, `out_brace`, fuel independence), `out_induct`, `out_append` and the character lemmas `mem_of_mem_out`, `mem_out_of_mem`, `out_eq_self` | `LexicalProofs.lean` 162-438 |
| `String.map` over characters for `toLower` | **done**: `toLower_mem`, by `VE.Readings.map_data` (already on main, `Readings/Names.lean`) | `LexicalProofs.lean` |
| `words` of a normal string | **done**: `words_intercalate` (`words (" ".intercalate ws) = ws` when every word is non-empty and has no whitespace), `intercalate_data`, `mem_intercalate` | `LexicalProofs.lean` 489-530 |
| `check_extends` (Compat.lean) | **done**, statement as in 4.3 | `Compat.lean` 17-153 |
| `check_no_clause` | **ap-1d** (size rule; the library has every lemma it needs: `word_out`, `out_eq_self`, `not_listed`, `endsWith_comma`) | — |
| `check_spec` against `Accepts` | **ap-1d** (size rule) | — |
| `fixedOk_unique` | **ap-1d** (size rule) | — |
| `decodeRegulated_plain` | **ap-1d**: ap-1b (`feature/ap-1b`) has not merged, so by the task it is named here | — |
| New lemmas in a new file, not `LexicalExamples.lean` | **done**: `lean/VE/Acts/LexicalProofs.lean`, layer 2 (`tools/layer_policy.py`) | — |
| Proofs add no trusted lines | **done**: trusted +0; the helper definitions are `P` | `tools/trust-classes.json` |
| A seeded bug per proved theorem, in the definition it covers | **done**: 11 Lean mutants of `Lexical.lean`, all killed (section 4) | [mutants.json](mutants.json) |

Plan rows of AP-1 that this item touches: 2.5 ("every act `canonicalAct` accepts today, `acts@0` accepts with the
same canonical string (`check_extends`, stated in a module above both `Norms.Wire` and `Acts.Lexical`), with one
exception", *nor*) is now a theorem. The AP-1 "Statements" row ("all of `VE.Acts.Lexical` (with `check_extends` in
`Compat`)") is part: `check_extends`, `check_no_join`, `wording_subject_first`; the rest is ap-1d. The other AP-1 rows
(the row, the hunks, the contract, the tests, the Python and Rust seeded bugs) are ap-1b's, as ap-1a's REPORT says.

## 3. Deviations (recorded here, not in the copied plan)

1. **`check_extends`'s proof reads the act's characters, not only its words.** `canonicalAct` does not fold U+2019,
   `check` does; the proof shows a canonical act holds no U+2019 (any non-space, non-slot character lands in a word
   of the slot-replaced text, which `actWord` limits to ASCII letters, `'` and `-`). The same argument shows it holds
   no comma, so `dropComma` is the identity on its words and `rawLex` makes one token per word.
2. **Theorems of 4.3 live outside `Lexical.lean`.** The spec places `check_no_clause`, `check_spec` and
   `fixedOk_unique` in `Lexical.lean`; they need the lemma library, which imports `Lexical`. ap-1d should state them
   in `LexicalProofs.lean` (namespace `VE.Acts.Lexical`, names unchanged), as `check_extends` is in `Compat.lean`.
3. **`String.utf8ByteSize.go` is written out.** A `local notation` for it made four macro declarations the trust map
   counts as unclassified; the file opens `String (utf8ByteSize)` instead.

## 4. Seeded bugs

`docs/act-phrases/ap-1c/seed_bugs.py` plants each mutant, builds `VE.Acts.Compat`, records the first failing line,
and restores the file from git. A Lean mutant counts only when the build fails in `Compat.lean` or
`LexicalProofs.lean`, not in the mutated file. Each mutant makes `check_extends` false: `why` names an act today's
`canonicalAct` accepts, without *nor*, that the mutated `check` refuses or rewrites. Results in
[mutants.json](mutants.json) (`file` and `test` keys): **12 mutants, 12 killed** (run on `a70583e93`).

| Id | Definition (file) | Act it breaks | Fails at |
|---|---|---|---|
| check-start | `check` (Lexical.lean) | every act | `Compat.lean:153` |
| check-slots | `check` | `{0} vote` at arity 1 | `Compat.lean:153` |
| check-two-words | `check` | `{0} vote` | `Compat.lean:153` |
| maxActBytes (400 → 79) | `maxActBytes` | an act of 80 characters | `Compat.lean:151` |
| joinWords-extra (`the`) | `joinWords` | `{0} read the news` | `Compat.lean:128` |
| normal-spacing | `normal` | `{0} seek asylum` | `Compat.lean:56` |
| fold-letter (`z` folded) | `fold` | `{0} seize land` | `LexicalProofs.lean:536` (`fold_eq_self`) |
| dropComma-letter (`e`) | `dropComma` | `{0} note` (read as `not`) | `Compat.lean:63` |
| pieceToks-hyphen | `pieceToks` | `{0} re-enter` | `Compat.lean:90` |
| rawLex-length | `rawLex` | `{0} seek asylum in other countries` | `Compat.lean:100` |
| group-comma | `group` | `{0} seek asylum` with fixed phrase `seek asylum` | `LexicalProofs.lean:652` (`mem_group`) |
| layer-policy | `lean_layer` (tools/layer_policy.py, Python) | — | `check_lean_imports.py`: "new outward Lean import: VE.Acts.Compat -> VE.Acts.LexicalProofs" |

Languages: Lean (11) and the Python tooling `tools/layer_policy.py` (1). No product module under `ve/` and no Rust
changed. `check-start` fails by a heartbeat timeout at the proof's last step (the condition the mutant breaks), the
others by a failed tactic.

## 5. Trust, size and tests

- **Trust:** `trust_map.py --check` PASS on the final Lean change against `c5197da78`: K +0, S +0, D +0, G +0, tied
  +0, unclassified +0, trusted +0. No R16 allowance, so no FOLLOW-UPS row and no `trust_mutants.py` run (13a applies
  to trusted growth). `check_extends` ties nothing yet: it states `check` on `canonicalAct`'s acts only. The tie of
  `check` asked by FOLLOW-UPS "## ap-1a" belongs to `check_spec` (ap-1d).
- **Size** (`git diff --numstat c5197da78`, hand-written): Lean 806 (`LexicalProofs.lean` 667, `Compat.lean` +139),
  evidence 107 (`seed_bugs.py` 93, `mutants.json` 14), side tables 12 (`layer_policy.py` +2/-1, `trust-classes.json`
  +8, `assurance-manifest.json` +2/-1), this report and DELTA about 140: about 1,065 in all, against the ~600 cap.
  The library is the floor: of its 667 lines, `check_extends` uses all but the parts ap-1d needs (`not_listed`'s
  clause half). Cut: `check_no_clause`, `check_spec`, `fixedOk_unique`, `decodeRegulated_plain`.
- **Tests:** the selected tests (`mac-pytest.sh --select`, base `c5197da78`) on `a70583e93`: 137 units, 1 failed,
  `tests/test_assurance_manifest.py::test_every_json_handling_lean_file_is_classified` (`Compat.lean` now names
  `getStr?` in `check_extends`'s statement). Fixed in `37b9dea6a` (`other_json` entry); `tests/test_assurance_manifest.py`
  then passed 137/137. The rerun of the selection on the final HEAD is in section 8. `lake build` (via
  `regen_generated.py --write`), `lean/audit.py` (PASS, 598 files), `check_lean_imports.py` (kept),
  `regen_generated.py --check` for the assurance entries, and `gate_collection.py --check --prebuilt` (0 added, 0
  removed, 0 refused, stale or malformed) pass. No test in `main-known-red.txt` was hit. The full gate is the chain's.
- **Pilot bytes expected to move:** none (*estimate*). Proofs only; nothing reaches a document before ap-1b's row.
- **Commits** (`git log main..HEAD --no-merges`, taken before the commit that adds this report): `0d6d36e98` library
  and `check_extends`; `a70583e93` seeded bugs and inventories; `37b9dea6a` assurance manifest.
- **Tooling note:** `tools/trust_map.py --files PATH` *writes* its per-file JSON to `PATH`. Run with a source path,
  it overwrote the then-uncommitted `LexicalProofs.lean`, which was rebuilt from the session's edits and recompiled
  unchanged in content. Worth a guard in the tool (refuse an existing `.lean` path).

## 6. Next items

- **ap-1d, the rest of 4.3's proofs** (Lean only): in `LexicalProofs.lean`, `check_no_clause` (about 30 lines with
  this library: a word of the act with `{` or `,` is no clause word by `not_listed`; otherwise it is a word of the
  slot-replaced text by `word_out` and `out_eq_self`), `check_spec` against `Accepts` (unfolding `check`; no string
  lemma), and `fixedOk_unique` (from `decodeFixed`'s two loops: no duplicate and no `clash`, then two prefixes of one
  list are comparable). `decodeRegulated_plain` when ap-1b has merged (it is in `Norms/Wire.lean`). Then the ties of
  FOLLOW-UPS "## ap-1a": `check` by `check_spec`, `group`/`lex`/`decodeFixed` by `fixedOk_unique`.
- Then ap-3 (after ap-1b), then ap-4 (after ap-3 and ar-10b), as the task says.

## 7. Self-review against BUILDER-CHECKLIST

1. N.A.: no relayed answer, mode or response field changes; proofs only (DELTA: none).
2. PASS: section 2 lists every task row with its place or the item it moves to (size rule; `decodeRegulated_plain`
   by the task's own condition). No Python copy of a Lean decision, no report test, no file shared with an in-flight
   branch (checked against every `feature/*`, `lean-first/*`, `infra/*`, `foundation/*` branch: none touches
   `Compat.lean`, `LexicalProofs.lean`, `Lexical.lean` or `layer_policy.py`).
3. PASS: 12 seeded bugs, 12 killed (`mutants.json`, `seed_bugs.py`), each failing in a proof, not at a hash or in
   the mutated file. `trust_mutants.py`: N.A. (trusted +0).
4. N.A.: no answer of any language changes; `Lexical.lean`, `Wire.lean`, `ve/` and `rust/` are untouched.
5. N.A.: Python reads no new field.
6. PASS: `main` is still `c5197da78` (the merge base); inventories regenerated with `regen_generated.py`; the full
   gate is the chain's on the final HEAD.
7. PASS: DELTA has no row (no user-visible delta; trust +0); no signature reserved.
8. PASS: no output can change: no definition the decoders or services evaluate changed (`git diff c5197da78
   --stat` touches no evaluated Lean file); DELTA says none.
9. PASS: `select_tests.py` selected 137 units for this diff, including `tests/test_assurance_manifest.py`, which
   failed on `a70583e93` and caught the unclassified JSON use; the Lean build of `VE.Acts.Compat` is part of the
   selection's `lake build`, and every Lean seeded bug fails it.
10. PASS: each Lean mutant above breaks `check_extends`'s proof; the theorem is about `check`'s returned value;
    its statement is 4.3's, unchanged (section 1); no hypothesis added.
11. N.A.: no budget, limit or deadline changes (the proof uses `maxActBytes` as it is).
12. N.A.: no evaluated code changes; proofs are erased at run time.
13. PASS: no test removed or renamed; `gate_collection.py --check --prebuilt`: 0 added, 0 removed, 0 refused, 0
    stale, 0 malformed.

## 8. Final selection run

Filled in after the run on the final HEAD.
