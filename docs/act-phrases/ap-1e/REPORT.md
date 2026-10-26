# ap-1e build report: the ties of `group` and `lex`, and `grouped_unique`

**No DRI signature is reserved; nothing stops the item.** Trust S +13 (`expand`, `Grouped`), trusted -2 net, signed by
R16 (DELTA T1). All four task deliverables are in; `decodeRegulated_plain` moves to **ap-1f** (ap-1b has not merged).

Plan and spec on `main` (unchanged since `597b0d8e4`): [act-phrases-PLAN.md](../../spec/act-phrases-PLAN.md) 4 "AP-1"
and 2.1; [act-phrases.md](../../spec/act-phrases.md) 1.1-1.3, 4.1-4.3, 14.3. Read first: [ap-1d's REPORT](../ap-1d/REPORT.md)
section 6 and `manage-agents/FOLLOW-UPS.md` "## ap-1a" and "## ap-1d".

## 1. Statement gate

The gate is ap-1a's, ap-1c's and ap-1d's: the statement review converged, draft 2 applied its edits (14.3, SR1-SR16),
and none touches 4.3. `docs/act-phrases/ap-1d/statements.py` on the final tree: `Accepts`, `check_spec`,
`check_no_clause` and `fixedOk_unique` **all EQUAL** (exit 0). No definition ap-1a pinned changed: `Lexical.lean`,
`LexicalBase.lean`, `Norms/Wire.lean` and `LexicalExamples.lean` are untouched (`git diff 343261104 --stat`).
`expand` and `Grouped` are this item's own definitions (spec 1.1, condition 6, written out); 4.3 states neither.

## 2. Task rows delivered

| Task deliverable | Status | Where (`LexicalProofs.lean`) |
|---|---|---|
| (1) `expand`, `Grouped` (S, R16), `group_spec`, `rawLex_plain`, `mapM_mem`, `lex_spec`, with ap-1d's seeded bugs | **done**: recovered from `14343d398` (`c1e4d76ab`); `Grouped` also asks each `fixed` token to name a declared, non-empty phrase (`group_range`), see deviation 1 | 878-1028 |
| (2) `#guard` fixtures of `expand` and `Grouped` that `trust_mutants` can kill | **done** for `expand` (12 KILLED); `Grouped`'s refutations read UNKNOWN (the ap-1d tool gap, section 4) | 1123-1131 |
| (3) ties of `group` and `lex` in `tools/trust-classes.json` | **done**: `group` by `group_spec`, `lex` by `lex_spec`; `trust_map.py --check` validates both | — |
| (4) `grouped_unique` if it fits | **done**: under `decodeFixed fx = .ok ps`, two groupings of one token list are equal | 1061 |
| `decodeRegulated_plain` | **ap-1f**: it is in `Norms/Wire.lean`, which ap-1b changes; ap-1b is not in `main` | — |

## 3. Deviations (recorded here, not in the plan)

1. **`Grouped` has a range clause** (`∀ t ∈ g, ∀ i, t = .fixed i → ps.getD i [] ≠ []`) that `wip/ap-1e` lacked.
   Without it no grouping is unique (`[]` and `[.fixed 5]` both write out to `[]`, and an empty phrase can be inserted
   anywhere), so `grouped_unique` would be false. `group` emits only such tokens (`group_range`), so `group_spec` holds
   unchanged in strength otherwise; the tie of `group` binds more than in the wip branch.
2. **`Grouped` is decided** (`decFixed`, `decPlain`, `decSuffixes`, `decGrouped`, class P) so fixtures evaluate it, as
   ap-1d did for `Accepts`.
3. **What the ties do not bind** (as ap-1d's F1): `lex_spec` says what `lex` returns when it succeeds, not that it
   succeeds whenever `decodeFixed` and `rawLex` do, and not its error texts (fixtures in `LexicalExamples.lean` pin
   those); `group_spec` needs fuel at least the length, which `lex` passes.

## 4. Seeded bugs and mutants

`docs/act-phrases/ap-1e/seed_bugs.py` plants each mutant, builds `VE.Acts.LexicalProofs` and restores the file from
git. A mutant is killed only when an error lies inside a target it names (a theorem or a lemma of its proof, or a
`#guard` line), never only in the mutated definition. Run on `29a7f43fd` (the final Lean): **10 mutants, 10 killed**
([mutants.json](mutants.json)). Language: Lean only (6 in `Lexical.lean`, 4 + the 46 below in the changed
`LexicalProofs.lean`); no Python or Rust product file changed (`seed_bugs.py` is evidence).

| Id | Definition (file) | Why the target is false | Fails at (`LexicalProofs.lean`) |
|---|---|---|---|
| group-rest | `group` (Lexical.lean) | phrase `b c` in `[a, b, c]`: after the ungrouped `a`, `b c` stays ungrouped | `:920` (`group_expand`) |
| group-empty | `group` | an empty phrase is grouped: a `fixed` token naming no phrase | `:919` (`group_expand`), `:959` (`group_range`) |
| lex-fuel | `lex` | `{0} seek asylum`: the fuel ends before the phrase | `:1028` (`lex_spec`) |
| rawLex-fixed | `pieceToks` | `{0} vote`: `rawLex` makes the slot a `fixed` token | `:1012` (`rawLex_plain`) |
| expand-fixed | `expand` (LexicalProofs.lean) | a grouped phrase written out loses its words | `:1123` (`#guard`) |
| expand-plain | `expand` | written out, only the phrases are kept | `:1123` (`#guard`) |
| Grouped-written | `Grouped` | `to seek asylum` grouped `[to, fixed 0]` with `to seek` declared | `:968` (`group_spec`), `:1131` (`#guard`) |
| Grouped-range | `Grouped` | phrase `[]` declared: `[]` and `[fixed 0]` both group `[]` | `:1038` (`grouped_fixed`), `:1129` (`#guard`) |
| Grouped-empty | `Grouped` | the empty phrase is a prefix of every list | `:968` (`group_spec`), `:1127` (`#guard`) |
| Grouped-plain | `Grouped` | a `fixed` token checked as if ungrouped | `:968` (`group_spec`), `:1128` (`#guard`) |

**trust_mutants** (Mac runner, `mac-pytest.sh --trustmut`, [trust-mutants.json](trust-mutants.json)): 46 mutants of the
2 new trusted definitions: 12 KILLED (all `expand`'s that elaborate), 4 INVALID, 9 ALLOWED
([trust-mutants-allow.json](trust-mutants-allow.json): 1 equivalent, `= false` to `≤ false` on Bool; 8 that do not
elaborate), **21 UNKNOWN, exit 1**. All 21 are `Grouped`'s and are rows of `mutants.json` with their cause: 14 are
refuted by a `#guard` at 1126-1131, read through `decGrouped`, which Lean rebuilds from the mutated body (the tool gap
of FOLLOW-UPS "## ap-1d", not this item's); 7 do not elaborate but share an operator with a drift mutant, so the
per-operator allow file cannot take them without hiding the drift ones. None is allowed as equivalent (ap-1d review F2).

## 5. Trust, size and tests

- **Trust** (`trust_map.py --check`, exit 0, against `343261104`): K +0, S +13, D +0, G +0, tied +15, trusted -2.
  R16 allowance S 13 in `docs/trust-baseline.json`; FOLLOW-UPS row "## ap-1e".
- **Size** (`git diff --numstat 343261104`, hand-written): Lean 255, evidence 169 (`seed_bugs.py` 123, `mutants.json`
  33, allow file 6, `trust-baseline.json` 7), side table 27 (`trust-classes.json`), this report 114 and DELTA 13: **578**.
  Generated, not counted: the Lean inventories and `trust-mutants.json`.
- **Tests:** selected tests (`mac-pytest.sh --select`, base `343261104`) on `fec8089ef`: **exit 0, 75 units, 0
  failed**, including `test_trust_budget.py`, `test_trust_mutants.py`, `test_acts_lexical_mutants.py`. Also: full
  `lake build` (1063 jobs), `lean/audit.py` PASS (608 files; the new theorems use only `propext`, `Classical.choice`,
  `Quot.sound`), `regen_generated.py --check` (33 entries), `gate_collection.py --check --prebuilt` (0 added, 0
  removed, 0 refused, 0 stale, 0 malformed). No test of `main-known-red.txt` was hit. The full gate is the chain's.
- **Shared files:** `tools/trust-classes.json` and `docs/trust-baseline.json` are also edited by ap-1b, df-1ad, jt-2,
  me-2, me-12a and me-1. ap-1b moves the `VE/Acts/Lexical.lean` entry, so whichever merges second re-applies the ties
  of `group` and `lex` there. `LexicalProofs.lean` is in no other branch.
- **Pilot bytes expected to move:** none (estimate). Proofs, specification and fixtures only.
- **Commits** (`git log main..HEAD --no-merges` before this report): `c1e4d76ab` recovered proofs; `e5ff1f590` range
  clause and fixtures; `72eda5c96` `grouped_unique`; `29a7f43fd` ties and allowance; `fa709c26a` seeded bugs;
  `fec8089ef` trust_mutants evidence; `8c2876079` DELTA.

## 6. Next items

- **ap-1f:** `decodeRegulated_plain` (`Norms/Wire.lean`) once ap-1b has merged.
- Then ap-3 (after ap-1bb), then ap-4, as the task says.

## 7. Self-review against BUILDER-CHECKLIST

1. N.A.: no relayed answer, mode, schema or response field changes (DELTA: trust row only).
2. PASS: section 2 lists every task row with its place, `decodeRegulated_plain` to ap-1f by the task's own condition;
   no Python copy of a Lean decision, no report test; shared files in section 5.
3. PASS: 10 seeded bugs killed in the named targets (`mutants.json`, `seed_bugs.py`), at least one per new trusted
   definition and per proved theorem; trust_mutants on the Mac (`trust-mutants.json`) with its 21 UNKNOWN listed (section 4).
4. N.A.: no answer of any language changes (`Lexical.lean`, `Wire.lean`, `ve/`, `rust/` untouched).
5. N.A.: Python reads no new field.
6. PASS: `main` is still `343261104` (the merge base); inventories regenerated with `regen_generated.py`; the full
   gate is the chain's on the final HEAD.
7. PASS: DELTA T1 cites R16 with its evidence; no signature reserved.
8. PASS: no output can change: `git diff 343261104 --stat -- lean` touches only `LexicalProofs.lean` (imported by no
   runner) and generated inventories.
9. PASS: `select_tests.py` selected 75 units, including `tests/test_trust_budget.py` (reads the ties) and
   `tests/test_acts_lexical_mutants.py`; every Lean seeded bug fails the selection's `lake build`.
10. PASS: each mutant in section 4 breaks the theorem or `#guard` it names; the theorems are about `group`'s and
    `lex`'s returned lists; `statements.py` EQUAL for 4.3; no hypothesis added to an approved statement.
11. N.A.: no budget, limit or deadline changes.
12. N.A.: no evaluated code changes; proofs are erased and the fixtures run at build time only.
13. PASS: no test removed or renamed; `gate_collection.py --check --prebuilt`: 0 refused, 0 stale, 0 malformed.
