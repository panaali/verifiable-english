# cmp-s4a-nested: the resolver's nested-mention exemption covers only a definite's restriction

Summary: `nested` (lean/VE/Discourse/Positions.lean:201-202) now exempts a mention from `slotCheck` only when it is the
possessive that supplies the other argument of a definite's relational restriction (`inRestriction`, :192-199),
as discourse.md 14.3 step 2 and 1.4 say. A mention nested in any other span (a plural's, a demonstrative's, a
definite's without that possessive) is checked like an outermost one, so a missing slot is `MentionNotSlot`.
No DRI signature is needed. Bytes 0 (no CLI answer reaches the changed path today, see "DELTA"). Trust: trusted +0, K +0, S +0 (no allowance).

Base: main at the merge base `e9a6ec8d5`. Commits (`git log --oneline main..HEAD --no-merges` on this branch):
`bd7b2b4fd` (the fix), `16c7f0fcc` (regenerated inventories and code map), `df175a622` (explicit-span guards and
the end-boundary guard), `87af0964c` (mutant evidence), and the commits of this report and of the class table
(tools/trust-classes.json; an R16 allowance recorded on the way was withdrawn, see "Trust").

## Deliverables (task cmp-s4a-nested)

| Task line | Delivered by |
|---|---|
| (1) exempt a mention only when it lies inside a definite's restriction (the nested possessive the grammar builds there), resolved there first; elsewhere checked like an outermost one, a missing slot is `MentionNotSlot` | `inRestriction` and `nested`, lean/VE/Discourse/Positions.lean:192-202 (`bd7b2b4fd`). The definite test reads `o.form == .definite` from the mention's slot form, as Access.lean does; the restriction test reads the form `restrFormula` builds for `POSSESSIVE RELNOUN` (lean/VE/Discourse/Elaborate.lean:59-61: `.binary q (.var 0) (.const c)` with `c` the possessive's target), so a possessive whose target is not that argument is not exempt |
| (2a) a pronoun inside a plural's span that the old code accepts and the new code refuses with `MentionNotSlot` | lean/VE/Discourse/PositionsExamples.lean:170. With a slot (:171) it is checked and its target used (`alice` in both conjuncts); with a slot in an ill-typed position (:174) the plural's typing fault is reported |
| (2b) the nested possessive inside a definite's restriction still accepted (no regression) | PositionsExamples.lean:164-167 (both manifest orders, at either end of the definite's span, and inside a span that does not start at 0) |
| (2c) a mention nested in another non-definite formula-producing mention refused | PositionsExamples.lean:177 (a pronoun inside a demonstrative) and :179 (a possessive inside a demonstrative that carries a relational restriction) |
| the opposite directions of each condition of `inRestriction` | :182 (a pronoun, not a possessive, inside a definite); :184-188 (no restriction, a unary restriction, another target, a binder target, a restriction whose first term is no binder); :191-194 (after the span, past its end, before its start, on the same span) |
| (3) the composed route's abstention (Compose.lean, `ve.discourse@1` refusals) unchanged | Compose.lean is not edited (`git diff --stat main...HEAD` lists no file under lean/VE/Discourse/ but Positions.lean and PositionsExamples.lean). Guards: lean/VE/Discourse/ComposeExamples.lean:75-85 (`contentOk`: a chain content with a recorded mention is `MentionNotSlot`, a fence and a bound prose unit are `NotImplemented`) and the route check at :245-264 (`UnsupportedProfile: ve.discourse@1 with readings@1` and `... with speech-acts@0`); `lake build VE.Discourse.ComposeExamples` on this HEAD: `Build completed successfully (380 jobs)` |
| seeded bugs in docs/composition/cmp-s4a-nested/mutants.json and this REPORT | "Seeded bugs" below |

The old guard that accepted a possessive at span (0, 1) inside `m7` (a definite with the unary restriction
`api(x)`) is replaced by :185, which refuses it: a unary restriction has no nested possessive (Grammar.lean:26,
`"the" NOUN`), so the old acceptance was the defect this item fixes.

Spec re-read: "A nested mention (1.4) is no separate slot of the text: it is resolved inside its definite's
restriction first" against docs/spec/discourse.md 14.3 step 2 (:2166) and 1.4; the grammar's
`POSSESSIVE RELNOUN -- definite slot with a nested possessive slot, RELNOUN_of(x, ·)` against
lean/VE/Discourse/Grammar.lean:27-28; the restriction formula against Elaborate.lean:55-61 (`restrFormula`).

## DELTA

None. The only caller of `resolveContent` with recorded mentions outside the examples is the composed route, and
it abstains first: `contentOk` (lean/VE/Discourse/Compose.lean:98-107) refuses every chain content with a recorded
formula-producing mention (`MentionNotSlot`) and every prose unit with one (`NotImplemented: a bound prose unit on
the chain`) before any resolution (`resolve_identity`, Compose.lean:19-22). `grep -rln "Discourse.Positions"
lean/VE` lists only Audit.lean, Compose.lean, PositionsExamples.lean and VE.lean as importers. So no CLI verdict
changes and no DELTA.md is written. When cmp-s4 (or cmp-s4ab) routes mentions to `resolveContent`, a unit with a
nested non-restriction mention is refused rather than accepted; that item writes the R8 row with its case.

## Size

`git diff --numstat e9a6ec8d5` (hand-written): lean/VE/Discourse/Positions.lean +12 -4, PositionsExamples.lean
+45 -5, mutants.json +98, trust-mutants-allow.json +14, tools/trust-classes.json +9, this REPORT. Generated or
tool-written: docs/codemap/*, lean/declarations.txt, lean/checkers.lock, trust-mutants.json.

## Seeded bugs (each planted alone in lean/VE/Discourse/Positions.lean, `lake build VE.Discourse.PositionsExamples`, then restored)

Lean is the only language whose product code changed (no Python or Rust file is in the diff). Every row is in
docs/composition/cmp-s4a-nested/mutants.json with its file and test; line numbers are this HEAD's
(PositionsExamples.lean is unchanged since `df175a622`).

| Definition | Mutant | Failing #guard (PositionsExamples.lean) |
|---|---|---|
| `nested` | the old any-span exemption restored (the task's first seeded bug) | :170, the pronoun inside a plural's span (also :177, :179, :182, :184-188) |
| `nested` | exempt nothing (`&& false`; the task's second seeded bug) | :164, the possessive inside the definite's restriction (also :165-167) |
| `inRestriction` | the encloser may have any form | :179 |
| `inRestriction` | the nested mention may have any form | :182 |
| `inRestriction` | the same span counts as nested | :194 |
| `inRestriction` | the start of the span is not checked | :193 |
| `inRestriction` | the end of the span is not checked | :191, :192 |
| `inRestriction` | the possessive's target is ignored | :186, :187 |
| `inRestriction` | the restriction's first term is not read | :188 |

The trust mutants (`tools/trust_mutants.py` over every new or changed definition, run at `df175a622` while they
were still unclassified and so counted as trusted; saved in trust-mutants.json): 24 KILLED, 0 SURVIVOR, 0 UNKNOWN, 4 ALLOWED. The allowed ones are span literals
of the fixture `herIn` moved by ±1 (`trust-mutants-allow.json`): the moved span still lies inside the plural's
(0, 5), so the guards read the same mention; the span boundaries are tested at :191-194.

## Trust

The new declarations are classified in tools/trust-classes.json (+9 lines): `inRestriction` is C (checker code),
like `nested`, `slotCheck` and `resolveAll` beside it on main; the eight new fixtures of PositionsExamples.lean
(`ownsApi`, `dOwner`, `inner`, `plural2`, `notified`, `runOn`, `ownerNotified`, `herIn`) are T. Neither class
counts as trusted (K + S + untied [V] + unclassified). `uv run python tools/trust_map.py --check` on this HEAD:
`against e9a6ec8d5938: K +0, S +0, D +0, G +0, tied +0, unclassified +0, trusted +0`, `PASS`. So no R16
allowance is needed. The one recorded while the declarations were unclassified (V 20) was withdrawn:
docs/trust-baseline.json is the merge base's. The selected tests caught the unclassified lines
(`tests/test_consolidation_tools.py::test_committed_trust_table_covers_every_declaration`, `assert 20 == 0`);
after the classification it passes (`uv run pytest -q tests/test_consolidation_tools.py -k
test_committed_trust_table_covers_every_declaration`: `1 passed`). The FOLLOW-UPS.md row "## cmp-s4a-nested"
now says no R16 ties pass is needed.

## Checks on this HEAD

- `lake build` (full): `Build completed successfully (1311 jobs)`; `python3 lean/audit.py`: `PASS: 780 source
  files; 8635 named theorem declarations audited`.
- `lake build VE.Discourse.Positions VE.Discourse.PositionsExamples VE.Discourse.Compose` and
  `VE.Discourse.ComposeExamples`: both `Build completed successfully` (the condition #guards).
- `uv run python tools/regen_generated.py --check --only checker-pins`: passes after the full build;
  `python3 tools/rust_build.py --check`: the release binary is pinned in lean/checkers.lock.
- Selected tests: see "Tests".

## Tests

- `zsh /home/seyran/code/manage-agents/mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run` on the
  tree of the report commit (run cmp-s4a-nested-8787e18f-t124473, 6 shards, 445 units): shards 1 to 5 `81, 80, 81,
  81, 61 units, all passed`; shard 6 `61 units, 60 passed`, the one failure
  `tests/test_consolidation_tools.py::test_committed_trust_table_covers_every_declaration` (`assert 20 == 0`, the
  unclassified declarations; fixed by the class table, see "Trust").
- The failed id rerun on the fixed tree: see the line below.
- The condition #guards (PositionsExamples.lean and ComposeExamples.lean) build on this HEAD ("Checks on this HEAD").
- Pre-existing failures on main (main-known-red.txt): none in this selection.

## Pilot bytes

0 expected: no pilot document reaches `resolveContent` with recorded mentions while the composed route abstains on
them (DELTA above). Nothing is claimed before a pilot audit.

## Next item

cmp-s4 (Compose.lean and the route) relies on the corrected exemption.

## Self-review against BUILDER-CHECKLIST

1. Typed and contained: N.A., no response schema, relay or decoder changes (no file under ve/ or lean/ResponseShape/ in the diff).
2. Deliverables: PASS, table "Deliverables" (each row with its #guard line); no Python copy of the Lean decision, no report test, no overlap (only Positions.lean and PositionsExamples.lean are hand-edited Lean).
3. Tests can fail: PASS, mutants.json (9 seeded bugs, each KILLED by a named #guard) and trust-mutants.json (24 KILLED, 0 SURVIVOR).
4. Agreement, valid inputs pass: PASS, PositionsExamples.lean:164-167 and :171 (accepted inputs), ComposeExamples.lean:75-85, :245-264 (route unchanged); no Python or Rust path changed.
5. R8 binding: N.A., no field Python reads from a Lean answer changed.
6. Gate evidence: N.A. for the builder (the chain runs the gate on the final HEAD); commit list above from `main..HEAD --no-merges`.
7. No unsigned item: PASS, no trust growth (`trust_map.py --check`: trusted +0) and no DELTA row.
8. DELTA: PASS, none, with the reason (Compose.lean `contentOk` abstains before `resolveContent`; ComposeExamples.lean:75-85).
9. Test selection: PASS, the selected-tests run in "Tests" (Positions.lean's changes are checked by its own Lean #guards in the build).
10. Lean statements: PASS, no theorem statement changed (`lean/declarations.txt` regenerated in `16c7f0fcc`; `resolveAll_ok` builds and is audited, lean/audit.py PASS).
11. Budgets fail closed: N.A., no budget, limit or deadline touched.
12. CPU or memory: N.A., `inRestriction` is a constant-size test per pair, the same `ms.any` walk as before.
13. Test-removed trailer: N.A., no file under tests/ is in the diff; the replaced item is a Lean #guard, not a collected test.
14. Both directions, cited evidence, spec re-read: PASS, the opposite-direction guards :182-194, "Spec re-read" above.
15. No overclaim: PASS, "unchanged" (Compose) cites ComposeExamples.lean:75-85, :245-264; no deliverable cut; every new guard has a killing mutant (mutants.json); limits N.A.
