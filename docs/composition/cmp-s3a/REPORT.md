# cmp-s3a: structured right lines, the data and the `plain` translation

No DRI signature is reserved; no DELTA row (no answer changes: nothing outside `lean/VE/RightClauses/` calls these
names). One spec statement is cut to the next item: `plain_wellFormed` (8.3) -> **cmp-s3ab** (below).

Spec: docs/spec/right-clauses.md draft 3, cherry-picked from 6b1896ce1, f158e69b7, b74520009 (commits 90a837a71,
05222c47d, 0ad17047c); `git diff b74520009 HEAD -- docs/spec/right-clauses.md` is empty. DRI decisions read:
reviews/dri-decisions-20261031-spec-right-clauses.md items 1-7 (3: `RelationOnCandidate` abstains; 5:
`ClauseLineShape` stays; 6: totality on the holder slot only).

## Deliverables

| Task row | Delivered | Evidence |
|---|---|---|
| (1) Tree.lean: `Role`, `Clause`, `Relation`, `CLine`, `ClauseDoc`, `lineName`, `lineSorts`, `baseEnv` (8.2) | yes, verbatim | c05c7e2cf; statement check below |
| (2) Plain.lean: `relAtom`, `plainGuard`, `plainSource`, `plain`, `plainContent`, `guardOf`, `holderGuardOf`, `checkClauses`, `WellFormedClauses`, `checkCandidates` (8.3, 7's texts) | yes | c05c7e2cf |
| (2) theorems `plain_identity`, `plainContent_identity`, `plainContent_declared`, `plain_shape`, `plain_limPremises`, `plain_guard` | yes, word for word, no `sorry`, no new axiom | `python3 lean/audit.py`: PASS, 726 files; lean/axioms.txt lines for `VE.RightClauses.*` use only propext, Classical.choice, Quot.sound |
| (2) theorem `plain_wellFormed` | **no: cut to cmp-s3ab** | see "Cut" |
| (3) Examples.lean, 9.1 fixtures | K1, K2, K4, K5, K6, K7, K8, K11, K12, K13 (`plain_limPremises` by `#guard`), K14, plus both sides of every check | `lake build VE.RightClauses.Examples` |
| (3) K9, K15 (`elided` missing) | not here: a `CLine` always has `elided`; the text is the wire decoder's (8.5, Wire.lean, cmp-s3) | - |
| (3) K3's premise, K10 | Relation.lean / the profile-off route (cmp-s3); K3's line is accepted by `checkClauses` here | Examples.lean "K3 accepted" |
| (4) seeded bugs | 4 named + 45 more, all killed | docs/composition/cmp-s3a/mutants.json |
| (5) statements.txt, `VE.lean`, `VE/Audit.lean` | imports in `VE.lean`; Audit.lean, statements.txt, axioms.txt, declarations.txt regenerated | `uv run python tools/regen_generated.py --write --skip route-cases` rc 0 |

No import of `VE.Readings`: Tree.lean imports `VE.Compose.Slot` and `VE.Compose.Content` only. Frozen
`Rights/*`, `SoftNorms/*`, `Norms/*`, `Route/*` and `Compose/*` are untouched (`git diff --stat main...HEAD -- lean/VE/Rights
lean/VE/SoftNorms lean/VE/Norms lean/VE/Route lean/VE/Compose` is empty).

`route-cases` was skipped in regen: its generator needs a Rust release binary this worktree does not have, and
none of its inputs changed.

## Cut: `plain_wellFormed` -> cmp-s3ab

`WellFormedRights (plain D)` reruns `checkRights`, `validateSoft (correlate (plain D))` (with W1's `validateW1` and
`VE.Norms.WellFormed` on the softened document), the identifier limit and `rightsSemanticCheck`. The statement needs
each to be shown invariant under conjoining base formulas to norm guards, except for a `ResourceLimit`. No such
lemma exists in the tree, and the proof would exceed this item's size cap by itself. Nothing in cmp-s3 depends on it:
8.4's theorems take `WellFormedRights (plain D) = true` as a hypothesis, and 4.1 step 6 runs the rights checks on
`plain D` anyway. The statement is unchanged; only its proof moves.

## Choices the spec leaves to the build

- An entry that does not name exactly one source line of its right, or that shares its rule with another entry,
  is refused with `InvalidInput: invalid clauses of rule <n>`. The wire decoder builds one entry per line, so a
  decoded document never shows this text. It is what `plain_guard` reads (`entryOk`).
  Correction (cmp-s3a-cfr-2): the sentence before is false and withdrawn. No right-clauses wire decoder exists
  (it is cmp-s3-cfr-1). Two lines with one rule name fail `entryOk`. They got this text where rights says
  `DuplicateDeclaration`; they now get rights' own text (`entryError`). See docs/composition/cmp-s3a-cfr-2/REPORT.md.
- `ClauseLineShape` also covers a non-power line without a norm, which the rights decoder never produces
  (`shapeOk`). `plain_guard` needs a norm on every line that carries clauses.
- `RelationShape` also refuses a relation predicate with a reserved prefix (`rights__`, `soft__`, `ve__`; spec 1.5).
- The holder slot of 1.3 is rights' own `holderSlot` on the line's instance. A `.right` candidate is checked
  against `{ D.doc with rs := [R] }`, so its own right gives the holder and `H_R` (`candSource`).

## Seeded bugs (each planted alone, `lake build VE.RightClauses.Examples`, restored)

| Bug (task row 4) | File | Fails |
|---|---|---|
| clause span may end past the unit (K5) | lean/VE/RightClauses/Plain.lean `checkSpans` | Examples.lean:101 K5 `#guard check (cline [trig (charged 0) 90 110] none [])` |
| elided range may overlap a clause (K6) | Plain.lean `checkSpans` | Examples.lean:113 K6 `#guard check (cline [trig (charged 0) 10 20] none [(15, 25)])` |
| clause variable sorts not checked (K7) | Plain.lean `checkBody` | Examples.lean:127 K7 `#guard check (cline [trig (charged 1) 10 20] none [])` |
| `plainGuard` drops the line's own guard | Plain.lean `plainGuard` | Plain.lean:137, the proof of `plainSource_nil` (and of `plain_guard`) |

All 49 hand mutants, at least one per new trusted definition, are KILLED. They are listed in mutants.json with
file, definition and the failing `#guard` or proof. Trust mutants: docs/composition/cmp-s3a/trust-mutants.json
(`mac-pytest.sh --trustmut -- --max-mutants 1000 --allow docs/composition/cmp-s3a/trust-mutants-allow.json`). The
first run had 71 survivors and 44 unknowns. Fixtures now kill the survivors: several rights, lines and entries; slots
(1, 0); a ternary line; spans with gaps; the prefixes; cites in either order. The allow file lists only the mutants
that do not elaborate and the equivalent ones (an `Option.toList` has at most one element; `isEmpty` ignores
`take 1`; a line with a relation has one instance and no fan-out). The final run (`--rescore` of the second full
run, head 75ce3d87d) exits 0: 281 KILLED, 0 SURVIVOR, 0 UNKNOWN, 68 INVALID, 55 ALLOWED (44 that do not elaborate,
11 equivalent survivors), 0 NOT RUN.

## Trust (R16)

`uv run python tools/trust_map.py --check`: K +0, S +139 (lean/VE/RightClauses/Plain.lean +103, Tree.lean +36),
D/G +0; PASS within the allowance recorded by `trust_map.py --allow --reason "cmp-s3a: ..." --signed "SIGNED by
standing ruling R16 (DRI-RULINGS.md), cmp-s3a, 2026-10-18"`. Every check that decides acceptance is classed S, not C
(sibling finding cmp-s4a F2). The R16 ties-pass row is in manage-agents FOLLOW-UPS.md under "## cmp-s3a".

## Size

`git diff --numstat $(git merge-base HEAD main)`, hand-written: Lean 717 (Tree 50, Plain 386 of which lines 1-120 are the
definitions, Examples 278, VE.lean 3); side table tools/trust-classes.json 67; REPORT.md 141, mutants.json 51 and
trust-mutants-allow.json 28 (trust-mutants.json, 406 lines, is the tool's output).
That is over the ~600 cap. The cut was made at the one statement whose proof would double the item. The rest is the
item's own mandated content (the 8.2/8.3 definitions, six of the seven theorems, the fixtures with both sides of each
check, and the evidence R16 asks for).

## Overlap with branches in flight

Only additive lines in shared registries: `lean/VE.lean` (ap-3dd, cmp-s4, df-5a, en-s6b, pc-1, me-1) and
`tools/trust-classes.json` (ap-1bg, ap-3dd, cmp-s4, df-5a, me-2d-f2, pc-1, sn-b6b, me-1). No branch touches
`lean/VE/RightClauses/` or docs/spec/right-clauses.md.

## Tests

`zsh mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run` on HEAD fc75c247 (clean): "exit=0;
failed/error ids=0"; 199 units recorded, "0 failed"; known Mac-only failures: none (log /tmp/cmp-s3a-select.log,
summary line `[mac-pytest 08:29:30Z]`). `lake build` (1233 jobs) and `python3 lean/audit.py` ("PASS: 726 source
files; 8031 named theorem declarations audited") passed on the Lean code. No test of main-known-red.txt was touched.

## Pilot bytes

None expected: no route reads these definitions before cmp-s3.

## Spec re-read

- Each 8.2 and 8.3 definition and theorem against docs/spec/right-clauses.md:317-448. A whitespace-normalised
  comparison of each declaration's text gives OK for all 19 delivered, and MISSING for `plain_wellFormed` (cut).
- Diagnostic texts and their order against 7 (:279-299) and 4.1 steps 3-4 (:203-206). The order is the line
  shape, clause typing, spans (clauses then elided, wire order), the relation, its cites, then
  `RelationOnCandidate` after every candidate's checks (Examples: typing before spans, spans before the relation,
  the relation before the cites, the candidate's span before the abstention).
- 1.1 (:38-60) spans: non-empty, inside the unit, pairwise disjoint. 1.3 (:78-94): total is the holder slot,
  `H_R` typed over `baseEnv`. 1.5 (:115-119): reserved prefixes.

## Next item

cmp-s3 (Relation.lean, Wire.lean, `right-clauses@0` in the registry, the `clauses-elaborate` differential, `ve/right_clauses.py`,
9.2-9.3, K3, K9, K10, K15, and lean/RIGHT-CLAUSES.md of 8.1, which this item's file list leaves out), after cmp-s2b; and cmp-s3ab (`plain_wellFormed`).

## Self-review against BUILDER-CHECKLIST

1. Typed and contained answers: N.A., no relayed answer (no route, wire or Python in this item).
2. Deliverables: PASS, the table above; one cut (`plain_wellFormed`) under the size rule, named as cmp-s3ab.
3. Tests can fail: PASS, mutants.json (49 KILLED) and trust-mutants.json with the allow file.
4. Python/Lean/Rust agree: N.A., Lean only; the differential is cmp-s3's.
5. R8 binding: N.A., no relay.
6. Gate evidence matches HEAD: PASS, the chain runs the gate on the final HEAD; no evidence reads live git.
7. No unsigned item: PASS, R16 allowance signed by the standing ruling; no DELTA row; no reserved signature.
8. DELTA: PASS (none): no executable reads the new definitions (`grep -rn RightClauses lean/VE --include=*.lean`
   finds only the three new files, VE.lean and Audit.lean).
9. Test selection: PASS, `tools/select_tests.py --base $(git merge-base HEAD main)` selects 207/527 units, including
   the Lean build and the audit.
10. Statements say what is claimed: PASS, the statement comparison above, plus mutants that break proofs
    (`plainGuard-drops-own-guard`, `WellFormedClauses-error-true`, `plain-rs-kept`).
11. Budgets fail closed: N.A., no evaluator, runner or budget; `plain` adds guard nodes counted by W1's existing
    10,000-node limit on `plain D` (spec 10).
12. CPU/memory: N.A., no route calls the new code.
13. Test-removed trailers: PASS, no test removed; `uv run python tools/gate_collection.py --check --prebuilt`: "0 added,
    0 removed by a trailer, 0 refused, 0 stale and 0 malformed trailers".
14. Both directions, cited evidence, spec re-read: PASS, every check has accepting and refusing `#guard`s at each
    boundary (Examples.lean); the spec re-read is above.
