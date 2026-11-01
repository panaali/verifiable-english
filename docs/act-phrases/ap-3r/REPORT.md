# ap-3r report: D3's revised cell

No DRI signature is reserved. The DELTA rows cite the DRI rulings the task names (2026-10-31 item 1; 2026-11-01
ap-3r-spec item 2) and R16; one question asked during the build (S3b) was answered by
`reviews/dri-decisions-20261101-ap-3r.md` item 1 (SIGNED).

Branch `feature/ap-3r` from main `3148e87c4` (ap-4b and ap-7 merged). Docs: design/ap-3r-spec's `8eec3fbc9`,
`ebaed1276`, `528b215be` cherry-picked in order (`git diff 528b215be HEAD -- docs/spec/` after the picks: empty), then
the o5-o7 ruling's edits (commit `a31c81383`). The syn2 edits (`debates/plan-synthesis-2/edits-act-phrases.md`, items
1-5 and DEC 16) concern `gate_acts`, ap-1bf, CI-5, cost and joint choices; none touches the D3 cell, so this item
implements none of them and nothing here differs from them.

## Delivered (task order)

| Deliverable | Where | Evidence |
|---|---|---|
| (1) the revised cell and its changed table theorem | `lean/VE/Acts/Table.lean`: `freeTable` `.all false true` / `.all false false`; `table_free_all_own`, `table_free_all_own_split` | `python3 tools/lean_statements.py --check`: "added: 1 VE.Acts.table_free_all_own_split; removed: 0; changed: 1 VE.Acts.table_free_all_own"; the theorem and `freeTable` lines `diff` equal to spec 6.2 (act-phrases.md:946-948, 1014-1017) |
| (1) TableExamples `#guard`s | T6 (both ops, both trees: 2 readings), T6s (split marker, own or shared *to*: 1); T9 (*must not* with *and*) unchanged | `lake build VE.Acts.TableExamples` |
| (2) norms route refuses the cell with D-23 | `Elaborate.lean` unchanged (byte-identical): `ruleReading` reads `table`; E17 and D-23 guards in `ElaborateExamples.lean` | E17 pins the spec's exact text (act-phrases.md:1750); *must not* on G12 unchanged |
| (3) guard moves of ap-3r-spec item 2 | ElaborateExamples: the one/two-atom splits and E16, D-26/D-27 order guards onto split-marker trees, old inputs expect D-23; ReadingsExamples: A5/A8/A12 4 readings, G5 N=3 lists 4, P64 on *must* (L6 under *right* now `limit`), the 64-choice fixture on L5, the :167 projection guard moved onto rs_u055 | `lake build VE.Acts.ElaborateExamples VE.Acts.ReadingsExamples` |
| (4) condition guards | S1 and S8 refused with the full F11/D-29 text (`together105`); S2, S3 refused; S4, S6 pass; S3b refused "a choice is not a reading" with its S4 on the same environment passing; S8b (S4 and S6 reordered) passes; u051's one-act "seek and enjoy" reading present; "to form and to join" two readings per place under *may* and *right*; a split marker's *and* under *may*/*right* one reading; E17 refused | ReadingsExamples.lean:37-58, 183-186, 213-239; ElaborateExamples.lean:141 |
| (5) seeded bugs | `docs/act-phrases/ap-3r/seed_bugs.py` -> `mutants.json` | 16 of 16 KILLED, restored build exit 0 (below) |
| DELTA | `DELTA.md` rows 1-4 | `L52_WIDE=1 review-ready.py --delta-dri-needed`: "no DELTA row reserved for the DRI" |
| o5-o7 docs | PLAN D3/D4 rows, 2.3, 2.4, D7 row, change item 15; spec 6.2, S3b, S8b | commit `a31c81383` and the S3b wording of `dri-decisions-20261101-ap-3r.md` |

Deviations: (a) S3b is built as the 2026-11-01 ap-3r decision item 1 words it (the o5-o7 wording cannot exist while
u055a is shared); the spec row is that decision's text. (b) The fixtures that tested later elaboration steps on an
own-*to* tree keep their input with the revised (D-23) answer where the verdict is the point, and move onto a
split-marker tree where a later step is the point (as the spec did for E16 and P64). (c) The `wide` choice-limit
fixture moves from L6 to L5, since L6 under *has the right to* now hits the reading limit first.

## Seeded bugs (all Lean; no Python or Rust product code changed)

`python3 docs/act-phrases/ap-3r/seed_bugs.py` (26 min; log lines in `mutants.json`, each with its failing lines):

| id | file | definition | first failing checks |
|---|---|---|---|
| own-to-restored | Table.lean | freeTable | Table.lean:67 (`table_free_all_own`), TableExamples:91 (T6), ReadingsExamples:37, 39 (u051 one act), 55 (A12), ElaborateExamples:141 (E17) |
| together-dropped | Table.lean | freeTable | Table.lean:68, TableExamples:91, ReadingsExamples:37, 39, 55, ElaborateExamples:141 |
| together-wrong-whole | Table.lean | freeTable | Table.lean:68, TableExamples:91, ReadingsExamples:37, 39, 45, 55 |
| split-marker-together | Table.lean | freeTable | Table.lean:71 (`table_free_all_own_split`), TableExamples:94 (T6s), 117, ElaborateExamples:120, 122 |
| right-only-dropped | Table.lean | table | Table.lean:69, Readings.lean:106-107, TableExamples:91, ElaborateExamples:141 |
| e1x-all-dropped | Grammar.lean | globalRules | ReadingsExamples:213 (S4), 217 (S6), 232 (S3b's S4), 239 |
| norms-split-again | Elaborate.lean | ruleReading | Elaborate.lean:265 (`ruleReading_ok`), ElaborateExamples:125, 127, 130, 141 (E17) |
| eachOrTogether-order, together105-text, e055x-denied-act, u055x-no-extra, other-listed | ReadingsExamples.lean | the new fixture definitions | ReadingsExamples:37/45/55; 183/184/186; 232; 233 (S3b); 239 |
| seekP-object, enjoyP-head, e17-sign, sick-filler | ElaborateExamples.lean | the new fixture definitions | ElaborateExamples:141 (E17); 191 |

## Trust

`uv run python tools/trust_map.py --check` on the final code: K +0, S +1 (`lean/VE/Acts/Table.lean`, `freeTable`),
unclassified +0, trusted +1: "PASS: K, S and untied [V] within 3148e87c47dc and the allowances introduced since".
The first measurement counted the new fixture definitions as unclassified (+22); they are class T in
`tools/trust-classes.json`, as every other definition of those two files is. Allowance S 1 recorded with `--allow`
(SIGNED by standing ruling R16); FOLLOW-UPS.md "## ap-3r" row added. The removed exception did not shrink the count.
Trust mutants (`mac-pytest.sh --trustmut -- --max-mutants 1000 --allow docs/act-phrases/ap-3r/trust-mutants-allow.json
--json docs/act-phrases/ap-3r/trust-mutants.json`, cloud pool): "34 KILLED, 0 SURVIVOR, 0 UNKNOWN, 0 INVALID, 6
ALLOWED", exit 0. The 6 allowed are `freeTable` pattern mutants (a flag or `all` -> `any` in a pattern) that leave a
case uncovered, which Lean refuses (`Missing cases`). The first run (before the T classification) had 14 survivors and
12 UNKNOWN, all on fixture definitions or those pattern mutants.

## Pilot bytes

0 expected. u051, u076 and u105 stay refused until the readings elaboration (F11; D7's new clause); their credit is
AP-4's and later. Nothing is claimed before a pilot audit.

## Tests run

- `lake build` (1214 jobs) and `python3 lean/audit.py`: "PASS: 710 source files; 7915 named theorem declarations".
- `uv run python tools/regen_generated.py --write --skip route-cases` (route-cases needs the Rust release binary;
  none of its inputs changed) and `--check --skip route-cases`: only `trust-tables` failed before the allowance.
- Selected tests, `mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run` (ran on the VM: "ve-mac-1
  unreachable"): "recorded 85 units …; 0 failed", exit 0, 5877 s. Its snapshot predates the T classification; the
  trust tests that read it were rerun after: `uv run pytest -q tests/test_trust_budget.py tests/test_trust_ratchet.py`:
  "112 passed".
- Known red on main (`main-known-red.txt`): none of its three tests is in this selection.

## Spec re-read

- `freeTable`, `table_free_all_own`, `table_free_all_own_split` against act-phrases.md:945-948 and 1014-1017 (`diff`).
- E17's diagnostic against act-phrases.md:1750; E16's act against :1749.
- T6/T6s against :1722-1723; P5/P8/P12/P64 against :1764-1772; S1-S8, S3b, S8b against :1782-1791.
- The DELTA Ruling cells against the task file's quoted wording; D3/D4/D7 rows against the o5-o7 ruling items 1 and 3.

## Next item

ap-4 (the act-readings mode, relay and admission hook; prerequisites gain ap-3r), then ap-5 and ap-6.

## Self-review against BUILDER-CHECKLIST

1. N.A.: no route, relay or response schema changes (no file under `ve/`, `lean/VE/Service/`, `rust/`).
2. PASS: the deliverables table above, each with its commit/guard; no Python copy of a Lean decision; no report test; overlap check against every in-flight `feature/*`, `infra/*`, `lean-first/*`, `foundation/*` branch found none.
3. PASS: `mutants.json` (16 of 16 killed by named guards or theorems); `trust-mutants.json` (34 killed, 6 allowed, exit 0).
4. N.A.: no Python or Rust path changes; the Lean answer is the only one.
5. N.A.: no relayed field added or changed.
6. PASS: no gate run by me (the chain runs it on the final HEAD); the base is `git merge-base HEAD main`.
7. PASS: DELTA rows 1-3 cite the DRI decisions, row 4 R16; `review-ready.py --delta-dri-needed` exit 0.
8. PASS: DELTA rows 1-3; ElaborateExamples E17 and the D-23 guards, ReadingsExamples S1/S8.
9. PASS: selected tests run with `mac-pytest.sh --select` (see "Tests run"); the seeded bugs fail guards in the built modules.
10. PASS: `lean_statements.py --check` (1 changed, 1 added, 0 removed); the plants `own-to-restored` and `split-marker-together` break the two theorems.
11. N.A.: no budget or limit changes; the 64-choice and reading-limit guards still hold (ReadingsExamples:84-92, 260-275).
12. N.A.: one table line became two; no new enumeration.
13. N.A.: no test removed or renamed.
14. PASS: each changed guard has its other side (E17 refused / split-marker split accepted; S3b refused / its S4 passes; S8b passes / S8 refused; T6 two / T6s one); spec re-read above.
