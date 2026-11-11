# ap-3cb-adapt build report: `splitMap_exact` and `elaborate_parts` on main's split functions (Lean proofs only)

**No DRI signature is reserved.** Trust growth: none (K +0, S +0, untied V +0). There is no DELTA row: the item adds
proofs and examples only, and changes no definition, text or answer. The ap-3c ties pass does not apply (section 4).
Review fix (section 11): F1's blanket refusal claims are narrowed to the fixtures the seeds record, and so is the
seeds claim of note F2. A test now checks them against the saved evidence. No Lean, Python product or Rust change.

Task: feature item ap-3cb-adapt (act-phrases, PORTFOLIO-PINS #8; DRI interim 2026-11-10 item 2). Spec
[act-phrases.md](../../spec/act-phrases.md) 6.6 (lines 1242-1262) and 11.3 (E1, E4: lines 1761-1764). Plan
[act-phrases-PLAN.md](../../spec/act-phrases-PLAN.md) section 4 AP-3. Source of the proofs: `wip/ap-3cb` (6217fa5c1e),
read as `/home/seyran/code/manage-agents/prompts/task-ap-3cb-adapt.wip-ap-3cb.patch`. Main at the start: 476b99b92.

## 1. Deliverables

| Deliverable | Status | Where (commit) |
|---|---|---|
| (1) `lean/VE/Acts/ElaborateProofs.lean`: the ported lemmas, `splitMap_exact` and `elaborate_parts`, proved, no `sorry`, no new `axiom`; listed in `lean/VE/Audit.lean` and the statement inventory by the regen tools | **done** | `bd7cc77c3`, `948bc68cc`; inventories `bed6d3bf3` (R12) |
| (2) E1 and E4 checked through the theorems | **done**: three `example`s (and the helpers `e1_map`, `e4_map`) beside E4's `#guard`s in `ElaborateExamples.lean` | `bd7cc77c3` |
| (3) Statement EQUAL check against spec 6.6, saved | **done**: `check_statements.py`, output `check_statements.out` | `bd7cc77c3` |
| (4) The ap-3c ties pass, if it now applies, recorded by `trust_map.py --check` before and after | **does not apply** (section 4); before and after counts recorded; the trial is saved in `ties-trial.txt` | `5be24c768` |

Statement gate (`python3 docs/act-phrases/ap-3cb-adapt/check_statements.py`, saved in
[check_statements.out](check_statements.out)):

```
EQUAL splitMap_exact
EQUAL elaborate_parts
```

The script is ap-3c's, with one change. Both statements contain `name := q`, so a Lean statement ends at its proof's
`:= by` instead of the first ` :=`. With ap-3c's ending, `elaborate_parts` read as DIFF because its text was cut
inside the statement.

## 2. The port

- Main's `elaborateMap_ok` concludes `U' = splitDoc D (splitAtoms D) (splitMap D (splitAtoms D))` and
  `M = splitMap D (splitAtoms D)`. Each lemma therefore takes the split as `sa` (`mem_partsOf`, `mem_preds`,
  `mem_rules`), and the theorems use it as `splitAtoms D`.
- `namesOk_ok` is now stated over any map `M`, because main's `namesOk D M` takes the map as an argument.
- `elaborate_parts`'s unspecified-name half reads `partNamesIn`, which `splitDoc` now uses for `unspec`.
- **One owner.** `inj_of_nodup_map`, `mem_splitReg` and `mem_splitNode` were already proved in `Faithful.lean`
  (ap-3dd), in the same namespace and form. The new file imports `VE.Acts.Faithful` and uses those lemmas rather than
  keeping copies. A first regen failed on the duplicate name (`environment already contains
  'VE.Acts.inj_of_nodup_map.match_1_1'`); `948bc68cc` fixed it.
- The statements are unchanged (section 1). The proofs need no hypothesis on the source. Step 3 (`namesOk`) gives
  fresh, distinct part names and part rule names. Step 7's backstop gives that no split rule keeps its name
  (clause 4).
- `python3 lean/audit.py`: `PASS: 847 source files; 9487 named theorem declarations audited`. The new theorems
  depend on `[propext, Classical.choice, Quot.sound]` or fewer (`/tmp` audit log, lines for `VE.Acts.splitMap_exact`,
  `VE.Acts.elaborate_parts`, `e1_map`, `e4_map`, `namesOk_ok`, `mem_partsOf`, `mem_preds`, `mem_rules`).
- `lake build` of the whole library ran inside `regen_generated.py --write` ("wrote 39 entries").
  `lake build VE.Acts.ElaborateExamples VE.Acts.ElaborateProofs VE.Acts.FaithfulExamples VE.Acts.DecodeExamples`:
  `Build completed successfully (144 jobs)`, with no warning in the two files.

## 3. E1 and E4 through the theorems (spec 11.3, lines 1761-1764)

In `lean/VE/Acts/ElaborateExamples.lean`, after E4's `#guard`s:

- **E1, `splitMap_exact` both directions.** For any `elaborateMap e1 = .ok (U', M)`:
  - the generated regulated names are exactly `p027__1` and `p027__2`, and the generated rule names exactly
    `r027-a1` and `r027-a2` (both directions of clauses 1 and 2);
  - `p027` and `r027` are not in the result (clauses 3 and 4).

  The map itself comes from `e1_map` (`elaborateMap_ok`; the kernel evaluates E1's split). Every other fact goes
  through the theorem.
- **E1, `elaborate_parts`.** Part 1 is `rg "p027__1" .permission (some (partAct fx6 .permission torture))` and part 2
  is the same with `cruel`, never the other way round. The part keeps `p027`'s sorts, role and completion.
- **E4, `elaborate_parts`.** `r027-a1` is `nd "r027-a1" "p027__1" false` and `r027b-a2` is
  `nd "r027b-a2" "p027__2" true ["r027-a2"]`. So each part rule keeps its sign and guard, and `r027b-a2`'s `over` is
  `[r027-a2]`.
- **Limit of the checks.** The kernel does not evaluate E4's split: `readingOf` compares two rules' readings, which
  reduces `wordsOf` (`String.splitOn`). It does not evaluate `partAct`'s text either.
  - The E4 example therefore takes `ha : splitAtoms e4 "p027" = some [torture, cruel]` as a hypothesis, and a new
    `#guard` pins it on both E1 and E4.
  - Another new `#guard` pins the two texts: `{0} be subjected to torture` and
    `{0} be subjected to cruel, inhuman or degrading treatment or punishment`.
  - The examples are conditional on `elaborateMap` accepting E1 and E4, which the existing `#guard`s show.

## 4. Trust and the ap-3c ties pass

- `python3 tools/trust_map.py --check` on HEAD: `against 476b99b92f5a: K +0, S +0, D +0, G +0, tied +0,
  unclassified +0, trusted +0` and `PASS`.
- Per-file counts (`trust_map.py --files`), before on a checkout of main 476b99b92 and after on HEAD:

  | File | before | after |
  |---|---|---|
  | `lean/VE/Acts/Elaborate.lean` | S 69, G[V] 93 untied, D[R] 5, P 202; trusted 162 | the same |
  | `lean/VE/Acts/ElaborateProofs.lean` | (absent) | P 196, o 16; trusted 0 |
  | `lean/VE/Acts/ElaborateExamples.lean` | T 245; trusted 0 | T 302, P 25; trusted 0 |
  | whole tree, trusted | 63309 | 63309 |

- **The ties pass does not apply.** FOLLOW-UPS "## ap-3c" asks to tie splitMap, splitReg, splitNode, splitEnv,
  partsOf and namesOk to these two theorems, ruleReading to `elaborate_one_reading`, and splitDoc to
  `elaborate_unspec`.
  - `trust_map.py` accepts a tie only when the theorem's compiled statement (its `-- uses` line) names the tied
    declaration. Neither 6.6 statement names any of these definitions: both speak of `elaborateMap`'s result.
  - A scratch `tools/trust-classes.json` with the six ties fails `--check` (exit 1) with twelve lines of the form
    `the statement of VE.Acts.splitMap_exact does not mention VE.Acts.splitMap`. They are saved in
    [ties-trial.txt](ties-trial.txt), and the table was restored afterwards.
  - `elaborate_one_reading`'s statement does not name `ruleReading`, and `elaborate_unspec`'s does not name
    `splitDoc`, so those two ties fail for the same reason.
  - The statements may not change in this item. A tie through `elaborateMap_ok`, whose statement does name
    `splitMap`, would be vacuous: it says only that `elaborateMap` calls `splitMap`. I took the conservative option
    and added no tie. The untied G[V] lines stay trusted.
- **trust_mutants.** The light lane printed NOT: `ElaborateProofs.lean`, `VE.lean` and `Audit.lean` are not in the
  side table, which lists no theorem files. `trust_mutants.py --plan`: `"definitions": 0, "mutants": 0`. The sweep
  through `mac-pytest.sh --trustmut` (on the VM): `0 definitions, 0 mutants ... 0 KILLED, 0 SURVIVOR`, saved in
  [trust-mutants.json](trust-mutants.json). R16 needs no mutant, since there is no new trusted definition.

## 5. Seeded bugs

`uv run python docs/act-phrases/ap-3cb-adapt/seed_bugs.py` writes [mutants.json](mutants.json); the unmutated pair
passes (`restored: SURVIVOR`) and accepts E1 and E4 (`restored_accepted`).
- Each bug is planted in a `/tmp` copy of `Elaborate.lean`, joined with Faithful.lean's three lemmas and the proofs
  (both sliced, not copied), and checked with `lake env lean`.
- Each bug carries `#guard`s, each evaluating one conjunct on E1 or E4 (fixtures sliced from
  `ElaborateExamples.lean`). The committed definitions are never touched.

The column "E1, E4 under the bug" is each row's `accepted` in mutants.json: one acceptance guard per fixture
(`#guard (elaborateMap e1).isOk`, `#guard (elaborateMap e4).isOk`), so the evidence names the fixture a bug refuses.
`tests/test_ap3cb_adapt_report.py` checks the column against mutants.json.

| Bug | File, definition | Fails | E1, E4 under the bug | Note |
|---|---|---|---|---|
| `parts-from-index-0`: `zipIdx 0` (the first part is index 0) | `lean/VE/Acts/Elaborate.lean`, `partsOf` | proof `mem_partsOf`, proof `splitMap_exact`; guard `M.preds.all (1 ≤ ·.2.2)` on E1 | accepted, accepted | the `1 ≤ i` conjunct is false on E1 |
| `split-node-over-unmapped`: `over := N.over` | same file, `splitNode` | proof `mem_splitNode` (the rule half of `elaborate_parts`); E4 acceptance guard | accepted, refused | see below |
| `part-keeps-source-name`: map entry `(r.name, r.name, i)` | same file, `splitMap` | proof `mem_preds` (`q = partPred p i`); E1 and E4 acceptance guards | refused, refused | see below |
| `part-declaration-keeps-source-name`: part declared as `r.name` | same file, `splitReg` | proof `mem_splitReg` (`splitMap_exact` clause 1, `elaborate_parts` `find?`); E1 and E4 acceptance guards | refused, refused | see below |
| `atoms-reversed`: `some atoms.reverse` | same file, `atomsOf` | the new `#guard splitAtoms e1 "p027" == some [torture, cruel] && …` | accepted, accepted | both theorems still prove; the pin catches the order |
| `statement-index-from-2`: `1 ≤ i` changed to `2 ≤ i` in clause 3 | `lean/VE/Acts/ElaborateProofs.lean`, `splitMap_exact` | proof `splitMap_exact`; `check_statements.py` would print DIFF | accepted, accepted | the statement proved is the spec's |

The task predicted different failing conjuncts for two of these bugs, and the actual failures differ:
- **Unmapped `over`.** The task predicted the rule half's own conjunct. What actually happens depends on the rule.
  - E4 is refused: `r027b`'s `over = [r027]` stays unmapped, so it names a rule the split removed. Probe: E4 with
    `r027b` over a rule on another predicate is refused on main with `UnknownRule: rule rk-a1`, and under the bug
    with `PrecedenceAcrossPredicates`. On E4 the rule-half conjunct holds only because the result is refused.
  - E1 is accepted: its one rule `r027` has `over = []`, and an empty `over` is the same mapped or not. On E1 the
    conjunct holds, and E1's result is the same as without the bug.
  - So the proof of the rule half (`mem_splitNode`) and E4's acceptance catch the bug. The E1 fixture cannot.
- **A part keeping its source's name.** The task predicted the Nodup conjuncts. What actually happens: step 3 or
  `validate` refuses E1 and E4 (both `refused` above). The proofs fail at `q = partPred p i` (`mem_preds`) and at
  `mem_splitReg`, not at a Nodup conjunct.

## 6. Tests

- The tests of the code touched: the Lean builds and the seed run above, and `check_statements.py`.
- `tests/test_ap3cb_adapt_report.py` (review fix, section 11) checks the seed table and the refusal and seed claims
  against mutants.json.
- `uv run python tools/gate_collection.py --check --prebuilt`: `33698 collected ... 0 added, 0 removed by a trailer,
  0 refused, 0 stale and 0 malformed trailers`.
- `tools/select_tests.py --base $(git merge-base HEAD main)`: `477/588 test units` (not every unit).
- Final selected run on the committed tree: section 9.

## 7. Spec re-read

- `splitMap_exact` against docs/spec/act-phrases.md:1242-1251: EQUAL after whitespace normalisation (script).
- `elaborate_parts` against docs/spec/act-phrases.md:1252-1262: EQUAL (script). Its docstring is the spec's
  (lines 1252-1254), word for word.
- E1 and E4 checks against docs/spec/act-phrases.md:1761-1764.
  - `splitMap_exact` "in both directions on E1": every generated name is in the map with its source and index, and
    p027 and r027 are neither generated nor in the map.
  - `elaborate_parts` on E1: part 1 is torture and part 2 the `cruel` rendering. On E4: sign and guard are kept, and
    `r027b-a2`'s `over` is `[r027-a2]`. All are in the examples of section 3.

## 8. Size, pilot, next item

SIZE: 213 product, 173 tests, 209 other hand-written lines (excluding this REPORT).
- Product is `ElaborateProofs.lean` 212 and `VE.lean` 1. Tests are the examples and guards in
  `ElaborateExamples.lean` (83) and `tests/test_ap3cb_adapt_report.py` (90, review fix).
- Other is `check_statements.py` 37, `seed_bugs.py` 157 and `ties-trial.txt` 13, plus the 2-line saved output.
- `mutants.json` and `trust-mutants.json` are written by scripts. The generated files (`Audit.lean`,
  `statements.txt`, `declarations.txt`, `predicates.txt`, `axioms.txt`, the code map) are R12.

Pilot bytes: none expected (proofs and examples; no answer changes). Next item: none.

## 9. Final selected run

`MAC_PYTEST_NO_DEFER=1 zsh /home/seyran/code/manage-agents/mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run`
on the committed tree at `6893abc90` (clean; tree `fd47c099a4`), log `/tmp/ap3cb/select.log`:

```
recorded 477 units for tree fd47c099a4; 5 others left to the static graph until they run; 0 failed
[mac-pytest 07:35:28Z] summary: ran LOCALLY (VM) because: ve-mac-1 unreachable (...); exit=0; 9877s
```

It includes `lake build`, `lean/audit.py` and the chunked units, all with exit 0. Only this docs file was committed
after the run. No test of main-known-red.txt was involved (0 failed).

## Notes for the DRI

- The ap-3c ties pass (FOLLOW-UPS "## ap-3c", first row) cannot be met with 6.6's statements, which name only
  `elaborateMap`'s result (section 4). Tying the G[V] lines would need theorems whose statements name `splitMap`,
  `splitNode` and the rest. For example, `splitMap_exact` restated over `splitMap D (splitAtoms D)` and
  `splitDoc …`: that is a statement change, so outside this item. Until then the 93 untied G[V] lines of
  `Elaborate.lean` stay trusted, as ap-3c recorded them.
- Two of the task's predicted failures differ from the actual ones (section 5). The fixtures say which documents each
  bug refuses (mutants.json `accepted`). The unmapped `over` refuses E4 and leaves E1 accepted and unchanged, since
  E1's one rule has `over = []`. A part keeping its source's name refuses both E1 and E4. On a refused fixture the
  conjunct guards hold only vacuously. So only the proofs and the acceptance guards catch these bugs (E4's for the
  `over` bug, E1's and E4's for the other two).
- `Elaborate.lean`'s module docstring (line 11) still says "`splitMap_exact` and `elaborate_parts` come with ap-3cb".
  They are now in `ElaborateProofs.lean`. This item may not edit `Elaborate.lean` (norm-defaults-cfr-1b is in flight
  there), so the wording waits for the next edit of that file.
- `regen_generated.py --write` also refreshed main's stale code map (ClausesElaborate, rights): R12.
- The kernel evaluates `splitAtoms` on E1 but not on E4 (`String.splitOn` under a comparison of two rules'
  readings). So the E4 example is conditional on its split, which a `#guard` pins.

## Self-review against BUILDER-CHECKLIST

1. N.A.: no relayed answer, route or schema changes (proofs and examples only).
2. PASS: each deliverable of the task is in section 1 with its commit. Grep of the diff: no Python, no report test,
   and no file of an in-flight branch (`git diff --name-only main...<branch>` over feature/, lean-first/, infra/ and
   foundation/ found no overlap). Duplicate lemmas replaced by Faithful.lean's (`948bc68cc`).
3. PASS: six seeded bugs, each failing a named proof or guard (`seed_bugs.py`, `mutants.json`). The restored pair
   passes. No trusted growth, so no R16 sweep is needed; the sweep is empty (`trust-mutants.json`).
4. N.A.: no Python or Rust change; no checker output changes.
5. N.A.: no field read from a Lean answer.
6. PASS: main 476b99b92 is the merge base and has not moved during the build. The full gate runs on the final HEAD
   by the chain; the commit list is in section 10.
7. PASS: no DELTA row and no trust growth (`trust_map.py --check`: trusted +0); nothing reserved.
8. N.A.: no user-visible change (no definition, text or answer edited; `git diff --stat` shows only Lean proofs and
   examples, generated inventories and docs).
9. PASS: `select_tests.py` selects 477/588 units, not all. The seeded statement change breaks
   `ElaborateProofs.lean`, which `lake build` (selected) builds.
10. PASS: `statement-index-from-2` breaks `splitMap_exact`'s proof. `check_statements.py` prints EQUAL for both.
    The theorems are about `elaborateMap`'s returned pair (`h : elaborateMap D = .ok (U', M)`). No hypothesis was
    added.
11. N.A.: no budget, limit or deadline touched.
12. N.A.: no runtime code changed. The new `#guard`s evaluate E1 and E4 once each.
13. PASS: no test removed. `gate_collection.py --check --prebuilt`: 0 refused, 0 stale, 0 malformed.
14. PASS. Opposite direction: `splitMap_exact` is checked on E1 in both directions (generated names in; p027, r027
    out). Of the two new guards, the split pin has a seed that fails it (`atoms-reversed`) and passes unmutated
    (`restored: SURVIVOR`). The `partAct` text pin has no seed. `partAct` is in `Linearize.lean`, which the seeds'
    scratch file imports built, so a seed there would need its dependents rebuilt. The pin is a literal `==` on two
    strings, so it fails on any other text.
    Each claim in this report names its command. Spec re-read in section 7.
15. PASS. No overclaim: "no trust growth" is from `trust_map.py --check`; "statements unchanged" is from
    `check_statements.py`; the ties pass is written as not applying, with `ties-trial.txt`. No silent cut: every
    deliverable is built or shown not to apply. Every new check but the `partAct` text pin has a seed that fails it
    (`mutants.json`, item 14). Limits: N.A. (no evaluator or runner added).

## 10. Commits (`git log --oneline main..HEAD --no-merges`, saved at writing)

- `f77b15247` ap-3cb-adapt: seed atoms-reversed (the examples' split pin catches what the theorems allow)
- `5be24c768` ap-3cb-adapt: the ap-3c ties pass does not apply (trust_map refuses each tie: neither statement names the definitions); evidence
- `bed6d3bf3` ap-3cb-adapt: regenerate the Lean inventories and the code map (R12)
- `948bc68cc` ap-3cb-adapt: reuse Faithful.lean's inj_of_nodup_map, mem_splitReg, mem_splitNode (one owner); seeds splice them in
- `395033388` ap-3cb-adapt: seeded bugs in /tmp copies (index 0, unmapped over, a part keeping its source's name, a stronger statement); mutants.json
- `bd7cc77c3` ap-3cb-adapt: splitMap_exact and elaborate_parts ported to main's split functions; E1 and E4 through them; statement check

## 11. Review fix (ap-3cb-adapt-review.final.md)

- **F1 (A, record-only overclaim).** Sections 5 and "Notes for the DRI", and `seed_bugs.py`'s docstring, said every
  split result or document is refused under the unmapped-`over` bug. E1 stays accepted under that bug: its one rule
  has `over = []`.
  - Class: a refusal claim wider than the fixtures checked. The cause was one acceptance guard, an `&&` over E1 and
    E4, which could not say which fixture a bug refuses.
  - Fix: `seed_bugs.py` now has one acceptance guard per fixture (`ACCEPT`) on every row, and records `accepted` per
    fixture in mutants.json (rerun on the rebuilt tree; restored: SURVIVOR, both accepted).
  - Section 5's table carries the record (column "E1, E4 under the bug"). The text says which fixture each bug
    refuses: the unmapped `over` refuses E4 only; a part keeping its source's name refuses E1 and E4.
  - Regression tests in `tests/test_ap3cb_adapt_report.py`:
    - `test_no_blanket_claim_about_refusals_or_seeds` holds PROBE F1's pattern and the class's other forms.
    - `test_each_seed_records_which_fixture_it_refuses` checks the per-fixture guards and evidence.
    - `test_the_unmapped_over_bug_leaves_e1_accepted` is F1's example.
    - `test_the_report_table_reads_the_saved_acceptance` checks the table against mutants.json.
  - All four fail on the pre-fix REPORT, seed script and mutants.json. A planted wrong table cell fails the table
    test.
  - PROBE F1 failed before the fix (exit 1) and passes after it (exit 0).
- **Note F2 (C, not filed; same class).** Item 14 said each new guard has a seed. Only the split pin has one
  (`atoms-reversed`). It now says the `partAct` text pin has none, and why. Item 15's "Every new check can fail" is
  narrowed the same way.
- No DELTA row: the fix changes report text, a seed script, its evidence and a test. No definition, text or answer
  changes, so no standing ruling is needed. No test of main-known-red.txt is involved.

