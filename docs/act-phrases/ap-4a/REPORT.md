# ap-4a report: the edge rule's kinds, `modifier_edges`, `phraseReadings` and `phraseReadings_exact`

- **Status:** built, Lean only; no DRI signature reserved; DELTA's one row (trust S +31, K +0) is signed by R16.
- **HEAD:** branch tip of `feature/ap-4a`; base `0c4ea31d2` (main with ap-2bb, merged in at cb9c9dd1d).
- **Changed:** rule kinds and `modifier_edges` (Grammar.lean), the meaning reads them, `phraseReadings` and `_exact`.
- **Open:** nothing reaches a route (by design, plan G17); next ap-4b, then AP-7 on `phraseReadings`, then ap-4.
- **Evidence:** 15 seeded bugs killed; trust mutants 0 survivors; selected tests exit 0; full gate is the chain's.

## Scope and what reaches users

The plan (`docs/spec/act-phrases-PLAN.md` at `80f056f9e`) line 706: "AP-7, run on `phraseReadings`. The table
equations and the edge rule stay provisional until it passes." So nothing in ap-4a reaches a route, a relay or an
answer: no file under `lean/VE/Service/`, `ve/` or `rust/` changes, and no service mode calls `phraseReadings` or
reads a rule's kind. If AP-7 misses its pre-registered bar, D3 or D4 is revised before ap-4 merges, as the plan
orders. ap-4a implements no synthesis round 2 edit: round 2 (`f2b1d4634`, `80f056f9e`) changed AP-0 to AP-8's time
estimates and AP-3's u0123 text only, and section 3's statements are draft 3's.

Statement gate: the plan's statement review accepted AP-4's statements (spec 7; plan change log item 11, "No Lean
statement changed"). The two theorems and `phraseReadings` equal spec 7's text after whitespace normalisation (probe:
a Python script that cuts each from `lean/VE/Acts/{Grammar,Readings}.lean` and from spec section 7 and compares the
normalised text: `theorem modifier_edges EQUAL`, `def phraseReadings (V EQUAL`, `theorem phraseReadings_exact EQUAL`).

## Plan rows delivered

| Task deliverable | Where | Evidence |
|---|---|---|
| (1) the edge rule (2.4) in the grammar with `modifier_edges`, keeping every AP-2 derivation on phrases with no edge modifier | `Kind`, `Attach`, `RuleS.kind`, `attachOf`, `edgeLhs`, `modifier_edges` in `lean/VE/Acts/Grammar.lean` (83ca3931f); `applyRule` reads the kind (`lean/VE/Acts/Meaning.lean`) | `modifier_edges` proved; every `RuleExamples` raw count and `MeaningExamples` meaning guard passes unchanged (G6, G7, G14v and the 13 `ap0` rows have no edge modifier); ReadingsExamples 57-64 (G6, G7, G14v through the table) |
| (2) `phraseReadings` with its `Listing` result and its limits | `lean/VE/Acts/Readings.lean` | ReadingsExamples 68-75 |
| (3) `phraseReadings_exact` | `lean/VE/Acts/Readings.lean` | proved; by value on P11 both ways, ReadingsExamples 51-52 |
| (4) A5, A8, A9, A10, A11 give exactly 2 readings; A12 gives 2; 64 listed, 65 refused; N−1 and N raw derivations (G5); raw-cap saturation refused | `lean/VE/Acts/ReadingsExamples.lean` | 32-48 (by value, and the count list at 46); 68 (N = 3 lists, N = 2 refused); 73-74 (64 listed: L5 under *must not*, L6 under *has the right to*; L6 under *must not*, 128 lists, refused); 75 (L8 saturates `rawCap` = 256, refused); 70 (no steps); 65 lists: `phraseReadings_length` (below) |
| (5) computed once per request, its size charged against the stated limit | `phraseReadings` matches on `readings V N b ts` once; `table_length` (each meaning gives at most 2 lists, so at most 128 before `firsts`); `phraseReadings_length` (`ok` has at most 64); `phraseReadings_nodup` | the growing chain L5 to L8 under both modals (73-75) ends within the limit and the budget: `lake build` of the module completes |
| Seeded bug: drop the "all" reading of a pre-modifier; a named #guard fails | `e1x-all-dropped` | RuleExamples 44 (G8's raw count) first; with those guards off, ReadingsExamples 35 (A8), 37, 46, 83 ([mutants.json](mutants.json)) |

Boundary at 65 lists: no phrase of this grammar lists exactly 65. A phrase's meanings are the products of its binary
edge choices (5.2), and the table gives every meaning of one phrase the same count (1 or 2), so listings come in
powers of two. 65 is pinned by `phraseReadings_length` instead: an `ok` listing has at most `maxReadings` = 64 lists,
and the plant `phrase-limit-65` (`maxReadings + 1 <`) breaks that proof. 64 is listed (73-74) and 128 refused (73,
spec P65); the generic listing's 63, 64 and 65 are GrammarExamples LG3 to LG5.

Not delivered (other items, by the split): `Source`, `sourceCheck`, `sourceCheck_exact`, `atomSituation` (ap-4b);
the `act-readings` mode, relay, admission hook and Python fuzz (ap-4); S1 to S8 and AR1 to AR5 (theirs).

## Deviations from the spec text (no statement changes)

1. **`RuleS` gains a `kind` field, and the meaning reads it.** Spec 5.2 gives `RuleS` a `Kind`; AP-2 had none, and
   `applyRule` told an edge's `all` rule by its position (equal to the rule before it). The table now writes
   `.edge .first`/`.last`/`.all` on the five edges' rules and `.shape` on the others; `applyRule` reads
   `attachOf r.kind == some .all`. The rules' sides and order are unchanged, so every derivation and meaning is
   unchanged (all RuleExamples and MeaningExamples guards pass; the two guards that compared alike rules now compare
   the sides and the kinds, MeaningExamples 179-186).
2. **`edgeLhs` takes an `NT`, not a `String`**: the table's nonterminals are structured since ap-2b. The theorem's
   text is unchanged.
3. **`all` may stand at `E1X`.** Spec 7's docstring says "`last` and `all` only in trailing positions", but spec 5.2
   writes `E1X → ADV (first) | ADV (all)`. `edgeLhs .all` accepts `E1X` and the four trailing edges; the docstring
   says so. With the docstring's reading `modifier_edges` is false of 5.2's own table (plant
   `edgeLhs-all-trailing-only` breaks the proof).
4. Three small theorems beyond spec 7: `phraseReadings_nodup`, `phraseReadings_length`, `table_length` (deliverable 5
   and 1.6's "equal meanings once").

## Overlap with branches in flight

At the start, `feature/ap-2bb` was the only in-flight branch touching a file of this item
(`lean/VE/Acts/Meaning.lean`; checked with `git diff --name-only main...<branch>` over `lean-first/*`, `feature/*`,
`infra/*`, `foundation/*`). ap-2bb merged into main during the build; the merge cb9c9dd1d resolved the one conflict
(ap-2bb's `longEnd` and this branch's `applyRule` sit side by side; both kept), and `lake build` (1181 jobs, exit 0)
and `python3 lean/audit.py` (PASS: 684 source files, 7635 named theorem declarations) pass on the merged tree. The
`applyRule-own` plant was rerun there (KILLED, same guards).

## Seeded bugs (Lean; no Python or Rust product code changed)

`python3 docs/act-phrases/ap-4a/seed_bugs.py` plants each, builds `VE.Acts.ReadingsExamples`, restores; results in
[mutants.json](mutants.json) (15 plants, 15 KILLED, `restored_build_returncode` 0).

| Plant | File | Definition | Killed by |
|---|---|---|---|
| e1x-all-dropped (the plan's) | Grammar.lean | globalRules | RuleExamples 44, 45, 164 |
| e1x-all-dropped-isolated | Grammar.lean | globalRules | ReadingsExamples 35 (A8), 37, 46, 83 |
| e1x-all-as-first | Grammar.lean | globalRules | MeaningExamples 44, 45, 48, 184, 186 |
| trailing-all-as-last | Grammar.lean | frameRules | MeaningExamples 33, 35, 51, 55, 63, 64, 133, 184, 186 |
| trailing-all-dropped | Grammar.lean | frameRules | RuleExamples 36, 47, 51, 62, 68, 164, 174, 182 |
| middle-edge (AP-2's) | Grammar.lean | globalRules | `modifier_edges` (Grammar.lean 349) |
| attachOf-shape-all | Grammar.lean | attachOf | `modifier_edges` (346, 349) |
| edgeLhs-first-anywhere | Grammar.lean | edgeLhs | ReadingsExamples 88, 90 |
| edgeLhs-all-trailing-only | Grammar.lean | edgeLhs | `modifier_edges` (349) |
| applyRule-own | Meaning.lean | applyRule | MeaningExamples 33, 35, 44, 45, 48, 51, 55, 63, 64, 133 |
| phrase-limit-65 | Readings.lean | phraseReadings | `phraseReadings_length` (Readings.lean 118) |
| phrase-limit-64 | Readings.lean | phraseReadings | ReadingsExamples 73, 74 |
| phrase-no-dedup | Readings.lean | phraseReadings | `phraseReadings_nodup` (103) |
| phrase-limit-passed | Readings.lean | phraseReadings | Readings.lean 84, 99, 114 (the three proofs) |
| phrase-table-ignored | Readings.lean | phraseReadings | `phraseReadings_exact` (91, 92) |

The mechanical trust mutants (below) found `closed`'s never rules unchecked by any guard (its line changed only to
add `.shape`). The guard `closed rsC` (ReadingsExamples 98) was added. Hand cuts of `closed`, each built with
`closed_ok`, `closed_cl` and `grammar_wf` stubbed by `sorry` so that the guards run (a scratch script, not kept; the
mechanical run is the record): the leading `rs` cut to `dropLast` or `drop 1` (killed by RuleExamples 49, 97, 105, 164,
174 and others), the `rs.any` cut to `dropLast` (RuleExamples 212), and the scan cut ten ways (`rs.flatMap` from a
shorter list, the scanned list's `dropLast` and `drop 1`, `firsts`'s `dropLast`, `rs.any` from `drop 1`, each right
side's first or last symbol, each right side's first or last nonterminal): all killed by the `closed rsC` guard;
`firsts`'s `drop 1` is ill-typed. A control build with no cut passes.

## Trust

`uv run python tools/trust_map.py --check` on the final code: K +0, S +31, D +0, G +9 (tied +9), unclassified +0,
trusted +31 against `0c4ea31d2` (and the same against `327bf922a` before the merge); all in
`lean/VE/Acts/Grammar.lean`. Recorded with `trust_map.py --allow`
("SIGNED by standing ruling R16 (DRI-RULINGS.md), ap-4a, 2026-10-18"); FOLLOW-UPS.md "## ap-4a" asks for the ties
pass. `phraseReadings` is G[V] tied to `phraseReadings_exact`.

`tools/trust_mutants.py` (checklist 13a, through `mac-pytest.sh --trustmut`; cloud pool), final evidence
[trust-mutants.json](trust-mutants.json) at head `b118f331c`, base `0c4ea31d2`: 432 mutants of the 9 trusted
definitions whose lines this item changes (`globalRules`, `frameRules`, `many1`, `tail`, `items`, `closed`,
`edgeLhs`, `applyRule`, `piecesOf`): KILLED 378, SURVIVOR 0, UNKNOWN 0, INVALID 16, ALLOWED 38, exit 0. Every
ALLOWED verdict's `raw_status` is UNKNOWN; [trust-mutants-allow.json](trust-mutants-allow.json) gives each a one-line
reason: 34 are ill-typed cuts (an unknown constructor such as `Attach.any`, anonymous-constructor notation with no
expected type), and 4 (`closed`: M160, M180, M364, M376) fail the `closed rsC` guard but the tool's probe could not
re-read that check for them. History: the first run (`d1b651763`) left 17 survivors: 6 in `edgeLhs` (no guard read
it then; ReadingsExamples 88-92 added) and 11 in `closed`, whose never rules nothing checked (the `closed rsC` guard
added, then reordered once more for M190, which an allow entry had hidden in the second run). The tool's operators
find no site in `Attach` and `Kind` (one-line inductives: its `ctor-drop` reads constructors at line starts) or in
`attachOf` (a two-arm match with no Boolean arm), so they have no mechanical mutants; `attachOf-shape-all` in the
seeded-bug table plants one in `attachOf`, ReadingsExamples 92 checks it both ways, and every guard of the readings
reads the kinds.

## Tests

- While iterating: `lake build` of each edited module and its fixtures only.
- `cd lean && lake build`: 1171 jobs before the merge, 1181 after, exit 0; `python3 lean/audit.py`: PASS both times.
- `uv run python tools/regen_generated.py --write --skip route-cases`, then `--check --skip route-cases`: "checked 33
  entries". `route-cases` is skipped because it needs the Rust release binary (`rust/target/release/ve`, absent in
  this worktree) and this item changes no route.
- Selected tests, once, on the finished code before the merge (`153bbe624` plus the untracked report draft):
  `mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run`: 84 of 504 units, ran on ve-mac-1, exit 0,
  0 failed or errored ids (log summary line: "1133s; exit=0; failed/error ids=0"). After it, the merge of main and the
  reorder of `rsC` (one guard's rule list) changed the tree; the full gate the chain runs on the final HEAD covers both.
- `uv run python tools/gate_collection.py --check --prebuilt`: 30712 collected, 0 added, 0 removed, 0 refused, 0 stale,
  0 malformed (no test removed, so no `Test-removed` trailer).
- Pre-existing failures on main (`main-known-red.txt`): the two `test_lean_service.py` sub-tick deadline ids and
  `test_readings_defaults_rd8_report.py::test_review_fix_commit_chain_and_final_gate_target`; none was selected or
  touched here.
- Not run: the full release gate (the chain runs it on the final HEAD), Python or Rust differential tests (no Python
  or Rust change).

## Pilot bytes

0 by itself (an estimate; nothing is claimed before a pilot audit). u092's 163 B (M1) needs ap-4's route; u076's
125 B also waits for the readings elaboration (spec F11).

## Next item

ap-4b (`Source`, `sourceCheck`, `atomSituation`, Lean only), then AP-7 on `phraseReadings`, then ap-4.

## Commits

`git log --oneline main..HEAD --no-merges` at the time of writing: 7 commits and one merge of main (cb9c9dd1d): 83ca3931f (the
kinds, `modifier_edges`, `phraseReadings`, fixtures), 434f84a03 (registration and generated lists), d1b651763 (trust
classes, R16 allowance), e1e55742d (`phraseReadings_nodup`, both-way guards, seeded bugs), 153bbe624 (`closed rsC`,
first evidence, allow file, DELTA), 93a2eef3a (`rsC` reordered for M190), b118f331c (final evidence, allow reasons);
this report is committed after them.

## Self-review against BUILDER-CHECKLIST

1. Every Lean answer is fully typed and contained: N.A., no route, relay or answer reads anything this item adds
   (DELTA "Public output: none").
2. Every required deliverable is built: PASS, "Plan rows delivered" (each row with its file, commit and guard); rule
   breaks grepped in `git diff main...HEAD`: no Python or Rust file, no Python copy of a Lean decision, no report test;
   the one overlapping file (Meaning.lean, ap-2bb) is reported and merged.
3. Tests and gates can fail: PASS, [mutants.json](mutants.json) (15 plants, 15 KILLED, one per claimed behaviour and
   per new trusted definition) and [trust-mutants.json](trust-mutants.json) (0 SURVIVOR, 0 UNKNOWN, exit 0).
4. Python, Lean and Rust agree; valid inputs still pass: PASS for the second half (every RuleExamples and
   MeaningExamples guard passes, `lake build` 1181 jobs); N.A. for the first (Lean only, nothing to compare).
5. R8 binding: N.A., no relay (ap-4 binds `act-readings`).
6. Gate evidence matches the final HEAD: PASS for the sync (merge of main at cb9c9dd1d, merge base `0c4ea31d2`) and
   the saved evidence (trust mutants at b118f331c); the full gate is the chain's, on the final HEAD.
7. No unsigned item: PASS, DELTA row 1 cites R16 with `trust_map.py --check` and the mutants; no signature reserved.
8. Every user-visible change in DELTA: PASS, no public output changes (no route reads the new definitions), so the only
   row is the trust growth.
9. Test selection finds the tests: PASS, `select_tests` picked 84 of 504 units, and its setup runs `lake build`, which
   every seeded Lean bug fails (sel.log lines 5, 11).
10. Lean statements say what is claimed: PASS, the statement probe (`modifier_edges`, `phraseReadings`,
    `phraseReadings_exact` EQUAL to spec 7); plants that break each new theorem (`middle-edge`, `phrase-limit-65`,
    `phrase-no-dedup`, `phrase-table-ignored`); `phraseReadings_exact` is about `phraseReadings`'s own result.
11. Budgets and limits fail closed: PASS, ReadingsExamples 70 (step budget 0 is `limit`), 68 (N = 2 on G5's 2 raw
    derivations is `limit`), 75 (raw cap saturated), 73 (128 lists is `limit`); `limit` is a refusal, never `ok []`
    (plant `phrase-limit-passed`).
12. No CPU or memory regression: PASS, no route or pilot reaches the new code; `phraseReadings` parses once and handles
    at most 128 lists (`table_length`, `phraseReadings_length`); the L5 to L8 chain (73-75) ends within the limits.
13. Removed tests have a trailer: PASS, `gate_collection.py --check --prebuilt`: 0 added, 0 removed, 0 stale.
14. Both directions, cited evidence, spec re-read: PASS. Both directions: `edgeLhs` accepted and refused (88-90),
    `attachOf` (92), P11 listed and not listed (51-52), N = 3 listed and N = 2 refused (68), 64 listed and 128 refused
    (73-74), `closed rsC` adds and omits never rules (98). Spec re-read: `modifier_edges` against
    docs/spec/act-phrases.md:1316, `phraseReadings` against :1318-1323, `phraseReadings_exact` against :1325-1327,
    the limits against :202-225 (1.6), the fixtures against :1744-1757 (11.4) and plan AP-4 (lines 936-993 of the plan
    at `80f056f9e`).
