# cmp-s4a: formula positions, slots and their resolution (discourse 14.2, 14.3)

- **Status:** done, no DRI signature needed. Lean code at `708693a28`; the selected tests pass on `2de762fc9` (164 of 164).
- **What changed:** `lean/VE/Discourse/Positions.lean` holds 14.2 and 14.3's resolution and intended meaning, with the eight theorems proved (no `sorry`, no new axiom). `lean/VE/Discourse/PositionsExamples.lean` holds the 14.8 fixtures that need no fence compiler.
- **Cut to `cmp-s4ab`:** 14.3 steps 1 and 3 to 7, the checks the composed path runs around the fence compiler, with fixtures S4-5, S4-6, S4-8, S4-11 (header option), S4-12, S4-13 and S4-19 and the task's four named seeded bugs. Reason: size, see "Size".
- **Trust:** S +109, K +0, V +0. SIGNED by standing ruling R16. The trust mutants exit 0.
- **DELTA:** none. No route, wire, Python or English change; nothing calls these names before cmp-s4.

## Deliverables (task cmp-s4a)

| Task row | Delivered | Evidence |
|---|---|---|
| (1) 14.2: `nodeContext`, `nodePositions`, `linePositions`, `positions`, `withPositions`, `formulaMentions`, `slotPrefix`, `slotName` | yes, verbatim | `Positions.lean`; the statement check below |
| (1) 14.3: `resolveContent`, resolution steps 1 to 4 with their named errors | yes | `resolveContent`, `slotCheck` (step 2), `resolveAll`/`rowOf` (step 3), `checkAll` (step 4); S4-4, S4-7, S4-9, S4-10, S4-26 and the coverage `#guard`s |
| (1) 14.3 steps 1 and 3 to 7 (around the fence compiler) | **cut to cmp-s4ab** | written and tested in `4f84306a8` (`reservedNames`, `headerSlot`, `headerOver`, `softFields`, `jsonContent`, `uniqueTarget`); removed in `f699e1258` |
| (1) `VE.Structure.withConstant`, `withRelation`, `IntendedAt`, `resolveFormula` | yes, verbatim | `Positions.lean` |
| (2) `resolve_identity`, `resolve_position_faithful`, `resolve_no_new_symbols`, `resolve_typed`, `resolve_keeps_shape`, `positions_withPositions`, `withPositions_self`, `resolveFormula_assertion` | yes, statements verbatim | `python3 lean/audit.py`: PASS ("709 source files; 7894 named theorem declarations audited"). Each depends on `propext`, `Quot.sound` and at most `Classical.choice` (`lean/axioms.txt`) |
| (3) fixtures S4-4, S4-7, S4-9, S4-10, S4-11 (`resolve_identity` half), S4-15, S4-24, S4-26 | yes | `PositionsExamples.lean`, `lake build VE.Discourse.PositionsExamples` |
| (3) fixtures S4-5, S4-6, S4-8, S4-11 (header option), S4-12, S4-13, S4-19 | **cut to cmp-s4ab** | they passed at `4f84306a8` |
| (4) seeded bugs: S4-5 guard conjunct, S4-6 `binder:0` in a header, S4-19 reserved prefix, S4-8 ambiguity | **cut to cmp-s4ab** with their code | |
| (4) one mutant per new trusted definition | yes, 34 of 34 killed | `docs/composition/cmp-s4a/mutants.json` |
| (5) `lean/statements.txt` gains the theorems | yes, regenerated | `tools/regen_generated.py --write` (`lean-statements`) |

The statement check compared every declaration and docstring of 14.2 and 14.3's Lean blocks (`docs/spec/discourse.md`
lines 2089-2128, 2192-2196, 2230-2237 and 2249-2298) with `Positions.lean`, whitespace-normalised. Result:
"38 spec declarations and docstrings; 0 not verbatim in Positions.lean". The only spelling difference is `_root_.`,
which Lean needs to name `VE.Structure.withConstant` from inside `namespace VE.Discourse`. The script was a one-off
and is not committed (no statements checker exists for discourse 14).

No lemma had to go into `lean/VE/Compose/`. Every helper lemma is in `Positions.lean`: the `Fills` laws, `place_denote`,
`renameP_denote`, `rewrite_denote`, `resolve_ok` and `resolved_at`.

## Readings of the spec (re-read: 14.2 at discourse.md:2072-2151, 14.3 at :2153-2311)

1. **Nested mentions (14.3 step 2 and resolution step 2).** Resolution step 2 requires a slot for every mention of
   `formulaMentions`. 14.3 step 2 says a nested mention "is no separate slot of the text". So a mention whose span lies
   properly inside another formula-producing mention of the unit needs no slot (`nested`). A mention outside every
   other mention's span still does. Both directions have a `#guard` ("A mention nested in a description's span").
2. **Resolution step 4's check** is `A'.check E ctx` plus `Row.typed` (each constant target declared, a binder inside
   the context, a restriction typed at `[σ]`). Rows are built only for slots that occur in the position, so a target's
   constant occurs in `A'`, and `A'.check` already implies each conjunct. Nothing more is refused. The conjunct
   gives `resolve_position_faithful` its premises.
3. **A description's sort `σ`** is the first sort of `E` at which the recorded restriction checks over `[σ]` (4.5: the
   restriction is a formula over `[σ]`). A definite with no restriction, no reading or no such sort is
   `IllTypedTarget: <mention>: <target>`.
4. **`IntendedAt`** is `False` at a position that does not exist and at one whose rows have no reading. The spec says
   nothing about either case, and `resolve_position_faithful` reads neither.
5. **Span order** is the order of span starts, by a stable sort. The slots of one position have disjoint spans, so their
   starts never tie.
6. **Plan edits.** syn2-composition `d06b6711e` and syn2-discourse `247722022` concern PC-7b's compositions on
   cmp-s4's `composed_admission`, AR-10 rows and discourse's names and carriers. This item implements none of them.

## Size

`git diff --numstat $(git merge-base HEAD main)`: `Positions.lean` 693 lines, `PositionsExamples.lean` 172,
`lean/VE.lean` 2, `tools/trust-classes.json` 71. That is 938 hand-written lines before this report, above the ~600 guide.
The JSON evidence files and the generated files are tool output. The proofs of the eight required theorems take
about 400 of `Positions.lean`'s lines: the write-back laws, the slot semantics and the resolution lemmas. They cannot
leave the item without leaving the statement gate's theorems unproved. I cut at the seam the spec draws in 14.3:
the steps around the fence compiler (1 and 3 to 7) go to cmp-s4ab. Step 2, the fence compiler itself, is not in this
item either, so they belong with it.

## Seeded bugs (Lean only; no Python or Rust product code changed)

Each was planted alone in `lean/VE/Discourse/Positions.lean`, built with `lake build VE.Discourse.PositionsExamples`,
and restored. All 34, one per new definition, are in `mutants.json` with the first failing check. These are the
ones a `#guard` catches, one per claimed behaviour:

| Behaviour | Mutant | Fails |
|---|---|---|
| `binder:<i>` is context variable `ctx.length - 1 - i` | `rowOf`: `.binder (ctx.length - 1 - i)` → `.binder i` | `PositionsExamples.lean:133` (binder over `owns`) |
| the slot written first is outermost | `slotsIn`: comparator reversed | `PositionsExamples.lean:146` (two descriptions) |
| a nested mention needs no slot | `nested`: `o.span.1 ≤ m.span.1` → `<` | `PositionsExamples.lean:151` |
| a mention without a slot is refused | `slotCheck`: first check dropped | `PositionsExamples.lean:84` (`MentionNotSlot: m1`) |
| only formula-producing mentions are resolved | `formulaMentions`: `producing` dropped | `PositionsExamples.lean:66` (S4-11) |
| a wrong position count is refused | `withPositions`: length test dropped | `PositionsExamples.lean:41` (S4-4) |
| contexts are reversed predicate sorts | `nodeContext`: `.reverse` dropped | `PositionsExamples.lean:104` |
| the reserved prefix is `ve__slot__` | `slotPrefix` changed | `PositionsExamples.lean:118` |

The other 21 mutants (in `place`, `renameP`, the write-back functions, `slotMeaning`, `IntendedAt` and the rest) each break
a named proof (`mutants.json`).

## Trust (R16)

`uv run python tools/trust_map.py --check`: "against a73c2f53b88e: K +0, S +109, D +0, G +0, tied +0, unclassified +0,
trusted +109 … PASS". The allowance was recorded at S +110 before `slotsIn` lost a line, with
`--signed "SIGNED by standing ruling R16 (DRI-RULINGS.md), cmp-s4a, 2026-10-18"` (`docs/trust-baseline.json`).

The S lines are 14.2 and 14.3's meaning: `positions`, `nodeContext`, `nodePositions`, `linePositions`,
`formulaMentions`, `slotPrefix`, `slotName`, `Row`, `rowOf`, `slotsIn`, `rowsAt`, `VE.Structure.withConstant`,
`VE.Structure.withRelation`, `slotMeaning` and `IntendedAt`. The checked executables (`resolveContent` and its steps,
`withPositions` and the write-back functions, `place`, `renameP`, `Row.apply`) are C, as `elaborateD` is in
Elaborate. `Fills` is P, and the fixture helpers are T (`tools/trust-classes.json`).

R16's conditions:
- 109 ≤ 150, and K +0.
- Every new trusted definition is exercised by a check that can fail. `zsh mac-pytest.sh --trustmut -- --max-mutants 1000
  --allow docs/composition/cmp-s4a/trust-mutants-allow.json --json docs/composition/cmp-s4a/trust-mutants.json`
  on `708693a28` gave exit 0: KILLED 159, SURVIVOR 0, UNKNOWN 0, INVALID 24, ALLOWED 72.
- Each allow entry has one reason line. The Prop-valued `slotMeaning` and `IntendedAt` and the structures built by
  `withConstant` and `withRelation` cite the proofs the mutant breaks (`rewrite_denote`, `resolve_position_faithful`,
  `placeT_denote`, `renameP_denote`). The other entries are equivalent mutants (`take 1` on an `Option.toList`, `<`
  for `≤` on disjoint spans), type errors the tool reads as UNKNOWN, and `Row`'s constructor drops (each constructor
  has a `#guard`).
- The FOLLOW-UPS row is under "## cmp-s4a" in `manage-agents/FOLLOW-UPS.md` (ties pass).

## Evaluation cost (feature feed, evaluators and runners)

This item adds no route, runner or mode. `resolveContent` is called by cmp-s4's route entry. It still evaluates each
value once:
- `positions E c` once per call;
- each position's symbols once, not once per mention;
- each position's rows once.

A 120-mention, 121-position rule resolves in a `#guard` ("A large well-formed content"). A distributive plural
copies its position once per member (4.4). Several plurals in one position multiply, so the composed route must
charge the resolved size against the admission's limits. That is cmp-s4's route entry; it is named in the
FOLLOW-UP below.

## Tests

- `lake build VE.Discourse.PositionsExamples` passes: every `#guard`.
- `cd lean && lake build` passes. `python3 lean/audit.py` passes (above).
- `uv run python tools/regen_generated.py --check --skip route-cases` is clean except trust-tables, which passed after
  `--allow`. route-cases needs the Rust release binary, and its inputs did not change.
- Selected tests: `zsh mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run` on the final tree
  `dc6900469e` (HEAD `2de762fc9`) gave exit 0, 164 units in 5 shards, all passed. An earlier run on `9b4b5b79d` also
  passed (164 units).
- No test in `main-known-red.txt` was hit.
- Not run: the full gate (the chain runs it on the final HEAD).

## Pilot bytes

0 (*estimate*). No route calls these names before cmp-s4.

## Next items

- cmp-s4 (14.4 to 14.7, after this item).
- cmp-s4ab: 14.3 steps 1 and 3 to 7, cut from this item. Recover them from `4f84306a8`; their fixtures and the four
  named seeded bugs come with them.
