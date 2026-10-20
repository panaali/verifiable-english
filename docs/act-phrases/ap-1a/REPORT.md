# ap-1a build report: lexical acts, part 1 (`VE.Acts.LexicalBase`, `VE.Acts.Lexical`, `VE.Acts.Compat`)

**No DRI signature is reserved; nothing stops the item.** Trust growth is +150 lines (K +0), signed by standing ruling
R16 ([DELTA.md](DELTA.md) row 1); it is exactly at R16's cap. The item is **cut** by the size rule: the proofs of spec
4.3 that need a string-lemma library (`check_extends`, `check_no_clause`, `check_spec`, `fixedOk_unique`) are the next
item, **ap-1c**, and the contract source moves to ap-1b (section 6).

Plan: `research/act-phrases-p1` at `bb5b2f90d`, [act-phrases-PLAN.md](../../spec/act-phrases-PLAN.md) section 4 "AP-1",
2.1, 2.5, 2.8 and 3. Spec: [act-phrases.md](../../spec/act-phrases.md) 1.1-1.3, 2.1, 3, 4.1-4.3, 10 and 11.1. Both
files are on `main` already, byte-identical to the pinned commit (checked with `git show bb5b2f90d:<path> | diff`).
SYNTHESIS 4.2 puts AP-1 first in the `Norms/Wire.lean` queue; `lean-first/b14b` and lf-18 are merged.

## 1. Statement gate

The specification's statement review converged on **FIX** (`debates/act-phrases-spec/{astra,fable}.md`); draft 2
applied it and `act-phrases-p3ver1.final.md` verified the application: **PASS**, with three gaps for the bounded
re-check, none in AP-1's definitions (the stub's hash, a docstring in 6.4, D-28's prefix). `act-phrases-ph2-check`'s FIX
(one byte count) is fixed in `bb5b2f90d`. D9 is decided (DRI-DECISIONS-PHASE2 AP4). As for ap-2, no record of the
bounded re-check exists. Its AP-1 part (13, item 14 (e)) is the inventory of 4.1 and fixture E16 (AP-3's). This item
re-ran every AP-1 fixture it delivers in Lean, with the stub's bodies. All but one match spec 11.1: A25 (below). The
acting DRI launched the item, and I took that launch as the go.

## 2. Plan rows delivered and not delivered

| Plan row or task deliverable | Status | Where |
|---|---|---|
| `LexicalBase.lean`: `actReserved`, `words` and their helpers moved from `Norms.Wire`, one owner, `Norms.Wire` importing them | **done**: `Wire.lean`'s lines 25-71 moved verbatim, in namespace `VE.Norms.Wire` (every name unchanged), deleted from `Wire.lean` | `lean/VE/Acts/LexicalBase.lean` |
| `Lexical.lean`: 4.2's definitions | **done**: `joinWords`, `clauseWords`, `Tok`, the three limits, `fold`, `normal`, `dropComma`, `slotOf?`, `pieceToks`, `rawLex`, `phraseToks`, `clash`, `decodeFixed`, `fixedOk`, `group`, `lex`, `check`, `Form`, `Form.text`, `Form.ofText?`, `wording` | `lean/VE/Acts/Lexical.lean` |
| 4.3's theorems | **part**: `check_no_join` (Lexical), `wording_subject_first` (Compat), `decodeRegulated_without_acts` and `canonicalActIn_without_acts` (Wire) proved; `check_no_clause`, `check_spec`, `fixedOk_unique`, `check_extends` and `decodeRegulated_plain` are ap-1c (section 6) | — |
| `LexicalExamples.lean`: `#guard` fixtures A1-A6, A13, A15-A19, A21-A30, A32, A33 | **done**, every one with its bytes, tokens or exact diagnostic, plus the boundaries of each limit and diagnostic (D-1 to D-14, D-19) | `lean/VE/Acts/LexicalExamples.lean` |
| `Compat.lean` (`check_extends`) | **part**: the module exists, above both `Norms.Wire` and `Acts.Lexical`, with `wording_subject_first`; `check_extends` is ap-1c | `lean/VE/Acts/Compat.lean` |
| `ve/wire_contract/acts@0.json` (contract source) | **moved to ap-1b**: a contract needs a registry module, two examples that pass its legacy validator, a fault catalogue and Lean hooks (about 300-600 lines); its examples declare `acts@0`, which the envelope refuses until the row lands | — |
| `tests/test_acts_lexical.py` | **done** for what this item can reach: today's decoder through the service (a plain act or form refused, long, joined, comma and curly acts refused by today's check, *nor* kept) and `acts@0` refused until its row; the plan's Lean-verdict tests on `acts@0` documents are ap-1b | `tests/test_acts_lexical.py` |
| `Norms/Wire.lean`: `decodeRegulatedIn` plus `decodeRegulated_without_acts` | **done**: one body, `decodeRegulatedWith (acts) (actCheck)`; `decodeRegulated := decodeRegulatedWith false canonicalAct`, `decodeRegulatedIn ps fx := decodeRegulatedWith (ps.contains "acts@0") (canonicalActIn ps fx)` | `Wire.lean` 38-98 |
| the `canonicalEnvironmentJson` check | **part**: `canonicalActIn` and `canonicalActIn_without_acts` are here; the call sites (`canonicalEnvironmentJson`, and `decodeNormsEnvironment` with the envelope's profiles and the block's `fixed`) are ap-1b. They need the `acts` block admitted, which needs the row, and `FlaggedSpec.normsEnvironment_flag_not_defined` steps through `decodeNormsEnvironment`'s binds one by one | — |
| A31: without `acts@0`, byte-identical decodes over the route cases | **done** as saved evidence: 330 of 330 recorded cases (13 modes) answer identically at the merge base and here; and as theorems (`decodeRegulated_without_acts`, `canonicalActIn_without_acts`) | [evidence/byte-identity.json](evidence/byte-identity.json), `byte_identity.py` |
| Shared hunks `Tree.lean`, `NormDefaults/Check.lean`, `FillCheck.lean`, `Plain.lean`, `Encode.lean`, `Standalone.lean`, `Policy.lean`, `Compose/Dispatch.lean`, `ve/environment.py`, `ve/printer.py`, `rust/ve-kernel/src/environment.rs` | **not in this item** (the task: ap-1b, after ar-10a) | — |
| `tools/layer_policy.py` | **done**: `VE.Acts.LexicalBase`, `Lexical`, `Compat` and `LexicalExamples` are layer 2, because `Norms.Wire` (layer 2) imports `Lexical` | `tools/layer_policy.py` 133-134 |
| Generated files | **done** with `regen_generated.py --write`: roots, `Audit.lean`, axioms, statements, predicates, declarations, pins. The hand-reviewed side tables: trust classes, the trust allowance and the assurance pins (`Wire.lean`'s range re-reviewed; `Lexical.lean` pinned; `LexicalExamples.lean` under `other_json`). `docs/CONSOLIDATION-PLAN.md` row 8b re-measured (3,616: the 27 lines that leave `Norms/Wire.lean`) | — |
| Seeded bugs: Lean, a comma outside a fixed phrase fails A33 | **done**: `check-comma-passes` breaks `check_no_join`, and without the proofs the A33 guard fails | [mutants.json](mutants.json) |
| Seeded bugs: Python (drop `form` when loading), Rust (drop the `acts@0` refusal) | ap-1b, with the loader and the Rust refusal; no Python or Rust product code changed here | — |
| Moves (M2, M3, M4) | nothing: they need the row, the Policy wording and the pilot re-declaration | — |

## 3. Deviations from the plan and the spec (recorded here, not in the copied plan)

1. **`Tok`, `joinWords` and `clauseWords` are defined in `Lexical.lean`, not in `Syntax.lean`.** ap-2 put them in
   `Syntax.lean` and asked ap-1a to import them. But `Norms.Wire` must import `Lexical` (4.1), and `Syntax` imports
   `VE.Grammar.Basic`, a layer above `Norms.Wire`, so `Lexical` cannot import `Syntax`. The three definitions moved,
   byte for byte, to their owner in spec 4.2, and `Syntax` imports `Lexical`. `tests/test_acts_vocab_mutants.py`
   assembles them in front of `Syntax.lean` as before, so it collects the same 643 tests, and they pass.
2. **`fold` maps the character list** (`String.mk (s.toList.map …)`), not `String.map`. It is the same function
   (`#guard` on `’`, `‘` and plain text); the list form is the one the ap-1c proofs can unfold.
3. **No copy of the decoder.** The stub's `decodeRegulatedActs` copied `decodeRegulated`'s 35 lines. Here one body,
   `decodeRegulatedWith`, takes the `acts` flag and the act check. Under `acts@0` it gives the stub's answers (A30's
   guards). Without it, it is today's (the theorem and the 330 cases).
4. **`wording_subject_first` is in `Compat.lean`**, in namespace `VE.Acts.Lexical`. Its proof uses
   `VE.Readings.startsWith_append_ascii`, which `Lexical` (below `Norms.Wire`) cannot import.
5. **A25 uses the stub's phrases** (`equal pay rates`, `pay rates for women`). The spec's `equal pay for` ends with a
   join word, so D-13 fires before the overlap check. A guard records that behaviour.
6. **The limits' texts interpolate the limits** (`over {maxActBytes} bytes`), so the text and the limit have one
   owner; the texts are 10's.
7. `LexicalBase.lean` holds no JSON code, so the assurance manifest cannot pin it (its test requires a JSON use). Its
   seven declarations keep their D[V] class in the trust table, under their new file.

## 4. Seeded bugs

`docs/act-phrases/ap-1a/seed_bugs.py` plants each bug, builds `VE.Acts.LexicalExamples` (or runs the bug's own
check), records the first failing line, and restores the file from git. A bug that a proof of `Lexical.lean` catches
is planted again with the proofs cut out, and then a fixture must catch it too (`fixtures_only`). The results are in
[mutants.json](mutants.json) (`file` and `test` keys): **43 bugs, all killed.** Every new trusted definition has at
least one. `Tok` and `Form` are inductives, and a guard reads each of their constructors.

| Definition | Bugs (id: what fails) |
|---|---|
| `joinWords` | without *nor*: A24; without *for*: A2 |
| `clauseWords` | all of `actReserved`: A1 |
| `maxActBytes`, `maxPhraseBytes`, `maxPhrases` | 401: A22; 299 and 127: the guard that pins the three limits (and the 300-byte phrase and the 128 phrases behind it) |
| `fold`, `normal`, `dropComma` | U+2018: A19; no fold: A19; comma kept: A6 |
| `slotOf?` | length ≥ 2: `{}`; any digits: `{1a}` |
| `pieceToks`, `rawLex` | comma token dropped: A29; inner comma accepted: `a,b`; final comma accepted: A29 |
| `phraseToks` | ≥ 300 bytes: the 300-byte phrase; clause word case-sensitive: `Is`; one word: `court`; last edge unchecked: `equal pay for` |
| `clash` | self-overlap: `a b a b`; suffix half: A25; containment half: `a b c d` / `b c` |
| `decodeFixed`, `fixedOk` | ≥ 128: 128 phrases; duplicate only at index 0: the later duplicate; `fixedOk := true`: its guard |
| `group`, `lex` | one token consumed: A1; no grouping: A1 |
| `check` | `{0} ` start dropped: `{0}seek asylum`; `<` 400: A21; clause test without `dropComma`: `then,`; join word accepted: `check_no_join`, alone A5; comma accepted (the plan's bug): `check_no_join`, alone **A33**; join test case-sensitive: `check_no_join`, alone `FOR` |
| `Form.text`, `Form.ofText?`, `wording` | swapped: A2's wording; `is entitled to`: A30; `drop 3`: A1's wording; `{1} `: the proof of `wording_subject_first` |
| `canonicalActIn` | `acts@1`: `canonicalActIn_without_acts` |
| `decodeRegulatedIn`, `decodeRegulatedWith` | flag `false`: A30; plain fields without `acts`: today's refusal; both-or-neither half: A30; form unchecked: `may`; act read without `acts`: `plainReg []` |
| `lean_layer` (Python tooling) | the layer-2 line dropped: `tools/check_lean_imports.py` ("new outward Lean import: VE.Norms.Wire -> VE.Acts.Lexical") |

Languages: Lean (42 bugs) and the Python tooling `tools/layer_policy.py` (1). No Python product module under `ve/` and
no Rust changed.

## 5. Trust, size and tests

- **Trust:** `trust_map.py --check` PASS against the merge base `585794c92`: K +0, S +19, untied V +131, trusted +150
  (per file in DELTA row 1). Two allowances signed by standing ruling R16, and the FOLLOW-UPS "## ap-1a" ties row. The
  item is at the cap, so a review fix that adds trusted lines must offset them.
- **Size:** hand-written lines added: Lean product 293 (Lexical 184, LexicalBase 54, of them 47 moved verbatim,
  Compat 16, Wire +38/-53, Syntax +1/-14), fixtures 261, tests 101 (`test_acts_lexical.py` 88,
  `test_acts_vocab_mutants.py` +13/-2), evidence scripts 200, side tables about 125 (trust classes 75, the
  allowance 14, assurance pins 35, layer policy 2), this report and DELTA. Product code is within the ~600 cap. With
  fixtures, scripts and tables the total is about 1,000. The cut took out the proofs (section 6, estimated 300-400
  lines) and the contract (300-600).
- **Tests:** the selected tests (`mac-pytest.sh --select`, merge base `585794c92`, on `2b6e3c41`, after the sync with
  main) ran 370 units: exit 0, 0 failed. Before the sync, on `dbe8676a`, they ran 452 units: exit 0, 0 failed.
  After that run, `f0dc63b4` only rewrote the two trust tables in main's order (content unchanged); on it,
  `trust_map.py --check`, `regen_generated.py --check` and the trust, assurance and regeneration tests (335) pass.
  `tests/test_acts_vocab_mutants.py` (643 tests) passed on its own as well. `lake build`, `lean/audit.py`,
  `tools/check_lean_imports.py`, `regen_generated.py --check` and `gate_collection.py --check --prebuilt` (10 added,
  0 removed) pass. No test in `main-known-red.txt` was hit. The full gate is the chain's.
- **Saved evidence:** [evidence/commits.txt](evidence/commits.txt) is `git log main..HEAD --no-merges` taken just before
  the commit that adds it and this report, so it leaves out only that commit;
  [evidence/byte-identity.json](evidence/byte-identity.json) is `byte_identity.py`'s run against the merge base
  `585794c92`.
- **Pilot bytes expected to move:** none (*estimate*). Nothing here is reachable from a document until ap-1b's row.
  AP-1's M2 (u020, u059), M3 (28 UDHR entitlement lines) and M4 (Group C, 664 B) move only after the row, the Policy
  wording and the pilot's re-declaration.

## 6. Next items

- **ap-1c, the proofs of 4.3** (Lean only; before ap-1b's row admits `acts@0`): `check_extends` in `Compat.lean`,
  `check_no_clause`, `check_spec` against the independent `Accepts`, `fixedOk_unique` and `decodeRegulated_plain`. All
  but the last need one lemma library that the core library lacks: `words` (`String.split` with `pyWhitespace`) as a
  split of the character list; `scanSlots` commuting with that split (a slot never spans a space); `String.map` over
  characters for `toLower`; and `words` of a normal string. Estimate: 300-400 lines. These theorems would also tie
  `check`, `lex` and `decodeFixed`, which is the ties pass R16 asks for.
- **ap-1b** (after ar-10a): the `acts@0` row and `gate_acts`; `decodeNormsEnvironment` and `canonicalEnvironmentJson`
  calling `decodeRegulatedIn`/`canonicalActIn` with the envelope's profiles and the `acts` block's `fixed` (with
  `FlaggedSpec`'s proof); the `Tree`, `NormDefaults/Check`, `FillCheck`, `Plain`, `Encode`, `Standalone` and `Policy`
  hunks; `ve/environment.py`, `ve/printer.py`, the Rust refusal; `ve/wire_contract/acts@0.json` with its registry,
  examples and catalogue; the plan's Lean-verdict, wording and long-wording tests, and its Python and Rust seeded bugs.
  It is larger than one merge-sized item and will need splitting.
- Then ap-3.

## 7. Self-review against BUILDER-CHECKLIST

1. N.A.: no new relayed answer, mode or response field. The norms rows are unchanged:
   `evidence/byte-identity.json` (330/330), `tests/test_acts_lexical.py`.
2. PASS: section 2 lists every plan row and deliverable, with its place or the item it moved to (size rule). No Python
   copy of a Lean decision: no `ve/` change. No permanent report test. No in-flight overlap: only the generated
   `lean/VE.lean` is shared, with `feature/jt-1b`, `feature/me-5` and `foundation/me-1` (R12).
3. PASS: 43 seeded bugs, all killed (`mutants.json`, `seed_bugs.py`). `byte_identity.py` exits 1 on an empty corpus or
   on any differing answer.
4. PASS: base against head on the recorded corpus, `byte_identity.py` (330/330 identical);
   `tests/test_acts_lexical.py` (10 tests). Rust is unchanged (`tools/rust_build.py --check`: pinned).
5. N.A.: Python reads no new field from a Lean answer.
6. PASS: synced with main (`d4669ca3f`), inventories regenerated, the selected tests rerun on the synced code
   (`2b6e3c41`, 370 units, 0 failed). The full gate is the chain's, on the final HEAD.
7. PASS: DELTA row 1 cites R16 with its evidence; the FOLLOW-UPS "## ap-1a" row is written; no signature is reserved.
8. PASS: base and head outputs compared on every recorded route case (`evidence/byte-identity.json`): no record
   changes; `acts@0` stays refused (`test_the_acts_profile_is_refused_until_its_row_lands`).
9. PASS: `tools/select_tests.py` selects `tests/test_acts_lexical.py` and `tests/test_acts_vocab_mutants.py` (and
   `lake build`, which elaborates the fixtures) for this diff; a seeded Lean bug fails the selected `lake build`
   (`mutants.json`).
10. PASS: a seeded bug breaks each proof: `check-join-accepted` and `check-comma-passes` break `check_no_join`,
    `wording-subject` breaks `wording_subject_first` and `canonicalActIn-profile` breaks `canonicalActIn_without_acts`.
    The theorems are about the returned values (`check`'s result, `wording`'s string). No statement was changed or
    given a hypothesis.
11. PASS: the new limits refuse with `ResourceLimit` at the limit plus one and accept at the limit (A21/A22,
    128/129 phrases, 300/301-byte phrases: `LexicalExamples.lean` 100-103, 240-251).
12. N.A.: no new work on an existing path. Without `acts@0` the decoder evaluates two Boolean tests that
    short-circuit on `false`; the base and head services answered the 330 cases in about 3 s together.
13. PASS: `gate_collection.py --check --prebuilt`: 10 added, 0 removed, 0 refused, stale or malformed.

## 8. Review fixes (ap-1a-review.final.md)

**F1 (B): four behaviours of the new decoder were pinned by no fixture.** The class is a behaviour of the act check
or the regulated decoder that no `#guard` reads; the review's four were per-role behaviours of `decodeRegulatedWith`
and `check`'s slot comparison, read only on fixtures that passed `[]` as the fixed phrases.

- **Fixtures** (`LexicalExamples.lean`): slots repeated (`{0} meet {0}`), missing (`{0} meet {2}`) and out of order
  (`{0} meet {2} {1}`) refused, and in order accepted (lines 108-113). A role matrix (166-226): permission,
  obligation and plain, each with each field it may and may not carry (act, form, permission dual), under `acts@0`
  and without it, decoded with the fixed phrases `fx1` and A1's act, which only `Lexical.check` with `fx1` accepts.
  Each accepted declaration is compared as the whole record (default, role, act, dual), and the same act without the
  phrases is refused. A missing role or default, a declaration that is not an object, and an unknown role or default
  are pinned too: they were the sweep's other survivors.
- **Regression test** `tests/test_acts_lexical_mutants.py`. It plants the review's four, the fifth that only a proof
  caught (the fixed phrases not passed on), three more slot comparisons, and mutants generated from the source of
  `check`, `canonicalActIn`, `decodeRegulatedWith` and `decodeRegulatedIn`. The generated kinds are: every condition
  made never to fire and each of its conjuncts dropped, every comparison negated or moved off its boundary, every role
  replaced by each other role, each default arm negated, every read of `acts` fixed, `acts@0` negated, `fx` emptied,
  and each role's act sent to today's `canonicalAct`. Identical mutants are made once. Each mutant is elaborated with
  the fixtures and the proofs replaced by `sorry`, and it must fail only at `#guard`s. 78 do. 3 are equivalent, each
  with its reason, and are tested to still pass: `ws.length ≥ 2` after a normalised `{0} ` start, and the two reads of
  `acts` that the fields check makes unreachable without `acts@0`. A coverage test checks that every line of those
  definitions that decides something is changed by a generated mutant, and that each review mutant changes the line a
  generated one changes. The review's probe now exits 0 (3 of 3 killed); before the fix it exited 1.
- **Trust:** unchanged at +150 (`trust_map.py --check` PASS). The fixture helpers are classified `T` in
  `tools/trust-classes.json`, like the file's other fixtures. No product code changed: Lean `Lexical.lean` and
  `Wire.lean`, Python `ve/` and Rust are as reviewed. The line numbers in `mutants.json` are those of
  `LexicalExamples.lean` at `2b6e3c41`, when it was recorded.

F2 to F5 are C findings and are left to the items the review names (ap-1b and ap-1c, the spec erratum for A25).
