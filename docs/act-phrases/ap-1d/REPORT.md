# ap-1d build report: `check_spec`, `check_no_clause`, `fixedOk_unique` and the ties of `check` and `decodeFixed`

**No DRI signature is reserved; nothing stops the item.** Trust S +9 (`Accepts`), trusted -23 net, signed by R16
(DELTA T1). The item is **cut by the size rule**: the ties of `group` and `lex` move to **ap-1e** (section 6); their
proofs are done on the local branch `wip/ap-1e`. `decodeRegulated_plain` waits on ap-1b, as the task says.

Plan and spec on `main`: [act-phrases-PLAN.md](../../spec/act-phrases-PLAN.md) section 4 "AP-1", 2.1, 2.5;
[act-phrases.md](../../spec/act-phrases.md) 1.1-1.3, 4.1-4.3, 14.3 (unchanged since `c5197da78`). Read first:
[ap-1c's REPORT](../ap-1c/REPORT.md) section 6 and `manage-agents/FOLLOW-UPS.md` "## ap-1a".

## 1. Statement gate

The gate is ap-1a's and ap-1c's: the spec's statement review converged, draft 2 applied its edits (14.3, SR1-SR16),
and none of them touches 4.3's AP-1 statements. `docs/act-phrases/ap-1d/statements.py` compares `Accepts` (whole),
`check_spec`, `check_no_clause` and `fixedOk_unique` in `LexicalProofs.lean` with spec 4.3 after whitespace
normalisation: **all four EQUAL** (exit 0; with `.toLower` dropped from `check_no_clause` it prints DIFFERS). No
definition ap-1a pinned changed: `Lexical.lean`, `LexicalBase.lean`, `Norms/Wire.lean` and `LexicalExamples.lean`
are untouched (`git diff 768a935fc --stat`).

## 2. Task rows delivered and not delivered

| Task deliverable | Status | Where |
|---|---|---|
| `check_no_clause` | **done**, statement as in 4.3 (21 lines: via `check_iff`, `not_listed`, `word_out`, `out_eq_self`, `endsWith_comma`) | `LexicalProofs.lean` 734 |
| `check_spec` against `Accepts` | **done**: `check_iff` proves the iff without `fixedOk` (`check` refuses whatever `lex` refuses); `check_spec` is it | 671-733 |
| `fixedOk_unique` | **done**: `forIn_ok` reads `decodeFixed`'s two loops, `decodeFixed_ok` their checks, `clash_of_overlap` turns an overlap into a `clash` | 783-878 |
| Ties: `check` by `check_spec` | **done**, recorded in `tools/trust-classes.json` (`trust_map.py --check` validates it) | — |
| Ties: `decodeFixed` by `fixedOk_unique` | **done**, same | — |
| Ties: `group`, `lex` by `fixedOk_unique` | **ap-1e** (size rule). `fixedOk_unique`'s statement names neither, so `trust_map.py` refuses that tie; it needs `group_spec` and `lex_spec` (proved on `wip/ap-1e`) | — |
| `decodeRegulated_plain` | **ap-1e or later**: ap-1b has not merged (`feature/ap-1b` is not in `main`) | — |
| Proofs add no trusted lines; a trusted helper is recorded under R16 | **done**: the proofs are P; `Accepts` (spec 4.3's own definition) is S +9, signed by R16 | DELTA T1 |
| A seeded bug per proved theorem, in the definition it covers | **done**: 7 mutants, all killed in the named proofs (section 4) | [mutants.json](mutants.json) |

No AP-1 plan row other than 4.3's statements is touched; the row, the contract and the Python and Rust parts are
ap-1b's.

## 3. Deviations (recorded here, not in the plan)

1. **`Accepts` and the theorems live in `LexicalProofs.lean`**, not `Lexical.lean` (as ap-1c's REPORT, deviation 2,
   said): they need its lemmas. Names and statements are unchanged.
2. **`check_spec`'s hypothesis `h : fixedOk fx = true` is unused**: `check` throws whatever `lex` throws, and
   `Accepts` asks `lex` to succeed, so the iff holds for every `fx` (`check_iff`). The statement keeps `h` as the
   spec writes it (`set_option linter.unusedVariables false in`, as `VE/Cardinality/Theorems.lean` does).
3. **`Accepts` is decided** (`decOkAnd`, `decWord`, `decAccepts`, class P), so `#guard` fixtures can evaluate it.
4. **trust_mutants and a Prop.** `tools/trust_mutants.py` counts a kill only when a check reads every other definition
   unchanged; a check of a Prop goes through its `Decidable` instance, which Lean rebuilds from the mutated body, so
   each refutation reads as UNKNOWN (drift). The 64 mutants of `Accepts` are allowed with reasons (section 5).

## 4. Seeded bugs

`docs/act-phrases/ap-1d/seed_bugs.py` plants each mutant, builds `VE.Acts.LexicalProofs` and restores the file from
git. A mutant is killed only when an error lies inside one of the theorems it names (the theorem or a lemma of its
proof), never in the mutated definition itself (ap-1c review F5). Run on the
final Lean (`5ca7bdaeb`, results in `9f71b6467`): **7 mutants, 7 killed** ([mutants.json](mutants.json)).

| Id | Definition (file) | Why the theorem is false | Fails at |
|---|---|---|---|
| check-start | `check` (Lexical.lean) | `vote {0} now` accepted, not by `Accepts` | `LexicalProofs.lean:703` (`check_iff`) |
| check-size | `check` | an act of exactly 400 bytes refused | `:703` (`check_iff`) |
| clauseWords-slot | `clauseWords` | `{0} play the slot`: `check` exempts `slot`, now a clause word | `:749` (`check_no_clause`) |
| decodeFixed-twice | `decodeFixed` | `['a b', 'c d', 'c d']`: two `c d` at one place | `:826` (`decodeFixed_ok`) |
| decodeFixed-self | `decodeFixed` | `free to be free` at 0 and 3 | `:826` (`decodeFixed_ok`) |
| clash-start | `clash` | `seek asylum` and `seek asylum now` both at 0 | `:845` (`clash_of_overlap`) |
| Accepts-words | `Accepts` (LexicalProofs.lean) | `{0} vote`: `check` accepts, `Accepts` asks 3 words | `:703` (`check_iff`) |

Languages: Lean only (6 mutants in `Lexical.lean`, 1 in the changed `LexicalProofs.lean`). No Python, Rust or
product file under `ve/`, `tools/*.py`, `conformance/` or `rust/` changed.

## 5. Trust, size and tests

- **Trust** (`trust_map.py --check`, exit 0, against `768a935fc`): K +0, S +9, D +0, G +0, tied +32, trusted -23.
  R16 allowance S 9 in `docs/trust-baseline.json`; FOLLOW-UPS row "## ap-1d". `trust_mutants.py` (Mac runner):
  exit 0, 64 ALLOWED with [trust-mutants-allow.json](trust-mutants-allow.json) ([trust-mutants.json](trust-mutants.json)).
  Without the allow file ([trust-mutants-raw.json](trust-mutants-raw.json)): 0 KILLED, 3 SURVIVOR, 61 UNKNOWN.
  Of the UNKNOWN, 54 fail a `#guard` at `LexicalProofs.lean:770-778` (reported as drift through `decAccepts`) and 7
  make `Accepts` fail to elaborate or to be decided. The 3 survivors are equivalent (`b = false` to `b ≤ false` on
  Bool, twice; `2 ≤` to `1 ≤ ws.length`, since a normal act starting `{0} ` has two words).
- **Size** (`git diff --numstat 768a935fc`, hand-written): Lean 213 (`LexicalProofs.lean` +212/-1), evidence 174
  (`seed_bugs.py` 96, `statements.py` 44, allow file 18, `mutants.json` 9, `trust-baseline.json` 7; the 3-line
  FOLLOW-UPS row is outside the repo), side tables 24 (`trust-classes.json` 23, `assurance-manifest.json` 1),
  this report 137 and DELTA 14: **562**. Generated, not counted: the Lean inventories and the two
  `trust_mutants` JSONs. With the `group`/`lex` ties (`wip/ap-1e`) the Lean was 345 lines and the fixtures they need
  would have passed the cap, hence the cut.
- **Tests:** the selected tests (`mac-pytest.sh --select`, base `768a935fc`) on `9f71b6467` (the final Lean;
  only documents changed after it): exit 0, 77 units, 0 failed (run on the VM, Mac unreachable; 6,212 s), including
  `tests/test_assurance_manifest.py`, `tests/test_trust_budget.py`, `tests/test_trust_mutants.py` and
  `tests/test_acts_lexical_mutants.py`. Also: `lean/audit.py` PASS (603 files), `check_lean_imports.py` kept,
  `gate_collection.py --check --prebuilt` (0 added, 0 removed, 0 refused, 0 stale, 0 malformed), and
  `regen_generated.py --check` for lean-statements, lean-audit-manifests, frozen-inventory, trust-tables,
  assurance-manifest, assurance-doc and checker-pins. No test of `main-known-red.txt` was hit. The full gate is the
  chain's.
- **Shared files:** `tools/trust-classes.json` and `ve/assurance-manifest.json` are side tables that ap-1b, jt-2,
  me-2, me-9b, sc-1ad and me-1 also edit. ap-1b moves the `VE/Acts/Lexical.lean` entry, so whichever merges second
  re-applies this item's two ties there (`check`, `decodeFixed`).
- **Pilot bytes expected to move:** none (estimate). Proofs and fixtures only; no evaluated definition changed.
- **Commits** (`git log main..HEAD --no-merges` before this report): `66254a77d` theorems and ties; `81f26df2d`
  allowance; `14343d398` seeded bugs; `5ca7bdaeb` the cut, `Accepts` decided with fixtures, allowance S +9;
  `1eff72ba7`, `34c029c3e` trust_mutants evidence; `9f71b6467` seeded bugs rerun; `98395232b` statement script and
  DELTA.

## 6. Next items

- **ap-1e, the ties of `group` and `lex`** (Lean only). Branch `wip/ap-1e` (commit `14343d398`) has, proved:
  `expand` and `Grouped` (S: a token list written out, and 1.1's grouping: no ungrouped token starts an
  occurrence), `group_spec` (`group` with fuel at least the length groups a list with no `fixed` token),
  `rawLex_plain`, `mapM_mem` and `lex_spec` (`lex`'s tokens group `rawLex`'s), with their seeded bugs. Still to
  do: `#guard` fixtures of `expand` and `Grouped` for `trust_mutants`, the ties in `trust-classes.json`, and
  optionally `grouped_unique` (with `fixedOk_unique`, every occurrence is one `fixed` token).
- `decodeRegulated_plain` once ap-1b has merged (it is in `Norms/Wire.lean`).
- Then ap-3 (after ap-1bb), then ap-4 (after ap-3 and ar-10b), as the task says.
- Tool gap (in FOLLOW-UPS "## ap-1d"): `trust_mutants.py` cannot count a refutation of a Prop through the
  `Decidable` instance derived from it (also met by me-2's `Check.UnknownCause`).

## 7. Self-review against BUILDER-CHECKLIST

1. N.A.: no relayed answer, mode, schema or response field changes (DELTA: no user-visible row).
2. PASS: section 2 lists every task row, with its place or the item it moves to (size rule; `decodeRegulated_plain`
   by the task's own condition). No Python copy of a Lean decision, no report test; shared files in section 5.
3. PASS: 7 seeded bugs, 7 killed inside the named proofs (`mutants.json`, `seed_bugs.py`), at least one per proved
   theorem and one in the changed Lean file; `trust_mutants.py` exit 0 (`trust-mutants.json`, allow file with
   reasons, raw run `trust-mutants-raw.json`).
4. N.A.: no answer of any language changes (`Lexical.lean`, `Wire.lean`, `ve/`, `rust/` untouched).
5. N.A.: Python reads no new field.
6. PASS: `main` is still `768a935fc` (the merge base); inventories regenerated with `regen_generated.py`; the full
   gate is the chain's on the final HEAD.
7. PASS: DELTA T1 cites R16 with its evidence; no signature reserved.
8. PASS: no output can change: no evaluated definition changed (`git diff 768a935fc --stat -- lean` touches only
   `LexicalProofs.lean`, which no runner imports, and generated inventories).
9. PASS: `select_tests.py` selected 77 units for this diff, including `tests/test_trust_budget.py` (reads the ties
   and the allowance) and `tests/test_assurance_manifest.py` (reads the new `other_json` entry); every Lean seeded
   bug fails the selection's `lake build`.
10. PASS: each mutant above breaks the proof of the theorem it names; the theorems are about `check`'s returned
    value and `decodeFixed`'s list; statements equal 4.3 (`statements.py`, section 1); no hypothesis added.
11. N.A.: no budget, limit or deadline changes.
12. N.A.: no evaluated code changes; proofs are erased, and the fixtures run at build time only.
13. PASS: no test removed or renamed; `gate_collection.py --check --prebuilt`: 0 added, 0 removed, 0 refused, 0
    stale, 0 malformed.
