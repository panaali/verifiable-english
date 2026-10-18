# ap-2 build report: the act grammar, part 1 (vocabulary, terminals, the D2 listing; Lean only)

**No DRI signature is reserved; nothing stops the item.** Trust growth is +145 lines (K +0), signed by standing
ruling R16 ([DELTA.md](DELTA.md) row 1). The item is **cut**. R16 allows at most 150 trusted lines per item, and the
task caps an item at about 600 lines. The stub's rule table and meaning alone are about 500 trusted lines (measured
below), so this item delivers the first coherent part. The rest is named **ap-2b** (section 6).

Plan: `research/act-phrases-p1` at `bb5b2f90d`, [act-phrases-PLAN.md](../../spec/act-phrases-PLAN.md) section 4
"AP-2", 2.2, 3, 5, 11 item 4. Spec: [act-phrases.md](../../spec/act-phrases.md) 1.4, 1.6, 5.1, 5.4, 5.6, 10 (D-31),
11.2 and 11.2a. Both files were copied verbatim from the pinned commit; main lacked them. DRI-DECISIONS-PHASE2
"Act-phrases": AP1 (keep the order) and AP4 (D9 option (i), the refusal in `meaning`).

## 1. Statement gate

The statement review of the specification converged on **FIX**
(`debates/act-phrases-spec/{astra,fable}.md`). Draft 2 applied it, and `act-phrases-p3ver1.final.md` verified the
application: **PASS**, with three small gaps left for the bounded re-check. The phase-2 check (`act-phrases-ph2-check`)
was **FIX** on one byte count, fixed in `bb5b2f90d`. D9 is decided (AP4). The plan's SR16 also asks for a bounded
re-check of the stub before any build; no record of one exists. This item re-ran the stub: it elaborates on main at
`802b8ff9b` with every `#guard` passing (section 2). The theorems delivered here are generic in the rule table, so they
do not depend on the parts of draft 2 the re-check would confirm (`framesOk` aside, built here from 1.4's text with
its own fixtures). The acting DRI launched the item with D9 decided, and I treated that launch as the DRI's go.

## 2. First step: N and the step budget after D9 (plan 11, item 4)

`docs/act-phrases/ap-2/measure_n.py` (committed in `597b0d8e4`, before it ran) reads the spec's stub and the registered
corpus from the pinned commit, checks the stub's sha256 (`6e33f85c…`, as AP-0), elaborates them with `lake env lean` on
this worktree, and writes [evidence/n-measurement.json](evidence/n-measurement.json). D9 (i) puts its refusal in
`meaning`, so the rule table, the raw counts and the steps are draft 2's as written.

- **Corpus:** the 22 registered phrases with their registered vocabularies, plus the eight M1 act phrases AP-0 left out
  (u039, u041, u082, u085, u086, u091, u106, u108). I wrote no phrase or fixed phrase, but the M1 frames are mine
  (below). For u039, u041, u085 and u106 the phrases and fixed phrases are the spec's fixtures A1, A16, A2 and A3.
  For u082, u086, u091 and u108 the phrase is the pilot declaration of the entitlement (AP-0's re-try documents), with
  no fixed phrase. No pilot declares frames, so each M1 row's frame comes from one rule I fixed before the run
  (`rule_frames`): the head is the words up to the first word of a closed preposition list, and every listed
  preposition after it is a marker. The rule has two variants: as modifier markers (the most room for the edge rules)
  and as argument markers.
- **Result:** 38 rows. **R = 2** (G5, G8, G9, G10, G12) ≤ 64, so **N = 256 stands**. **S = 19,184** (M082, the 265-byte
  u082 phrase), and 10 S = 191,840 ≤ 2,100,000, so **the step budget 2,100,000 stands**. Both verdicts PASS by AP-0's
  rule. **Both values stay provisional.** The plan (11, deferred item 5) drops "provisional" only after a
  re-measurement with vocabularies written by someone other than the person measuring. Here R rests on AP-0's 22
  registered rows alone (every M1 row has raw 0), and S on M082m, whose frame my rule wrote. `rawCap` and
  `stepBudget` in `Read.lean` say so, and deferred item 5 stays open (review F2;
  `tests/test_ap2_limits_provisional.py`).
- **Finding:** under the rule-generated frames, none of the eight M1 phrases has a derivation (raw 0 in both
  variants). u039 and u085 get no frame at all: a preposition or a fixed phrase follows `{0}` or `{0} to`, so the rule
  finds no head. The other six get a frame, and the evidence records it per row, but no derivation; this item does not
  diagnose why. So the M1 phrases bound S, not R. This agrees with the plan: u039, u041, u085 and u106 are AP-1's
  lexical acts, which never enter the grammar, and u082, u086 and u108 are outside this design (research note 2.1).

## 3. Plan rows delivered and not delivered

| Plan row (section 4 "AP-2", 3, 5) | Status | Where |
|---|---|---|
| Goal: `grammar`, `meaning`, `read`, `readings` on the generic engine, with the two limits of D2 and the explicit limit outcome | **part**: the limits (`rawCap`, `stepBudget`, `maxReadings`), `Listing`, `listing`, `readingsIn`, `readIn` and the limit outcome, generic in the grammar and the meaning; `grammar` and `meaning` are ap-2b | `Read.lean` |
| Goal: `analyse` | ap-2b (it needs the act trees `Act.one`) | — |
| Goal: frames in the `acts` block | **done** for the Lean side: `Frame`, `Vocab`, `checkVocab` (D-31's 19 texts, in order) and `framesOk = (checkVocab V).isOk` (spec 1.4, draft 2's canonical markers); the wire decoder is AP-3's | `Syntax.lean` |
| Goal: the render round trip | ap-2b (`Linearize.lean`) | — |
| New files `Syntax`, `Grammar`, `Meaning`, `Read`, `Linearize`, `GrammarExamples` | `Syntax`, `Read`, `GrammarExamples` **done**; `Grammar`, `Meaning`, `Linearize` ap-2b | `lean/VE/Acts/` |
| Shared files: none | **held**: the only hand-written shared file is `tools/layer_policy.py`, which the plan lists for every batch with new modules (`VE.Acts.` joins layer 3; section 7) | — |
| Generated: roots, `Audit.lean`, axioms, statements, pins, gate collection | **done** with `regen_generated.py --write` and `--resolve`. Pins are unchanged (no checker changed). The review fixes add 470 tests (`tests/test_acts_vocab_mutants.py` 467, `tests/test_ap2_limits_provisional.py` 3): `gate_collection.py --check --prebuilt` reports 470 added, 0 removed | — |
| Statement `grammar_wf` | ap-2b | — |
| Statements `read_unique`, `readings_exact`, `readings_nodup` (and spec 5.6's `read_none`, `read_many`, `readings_limit`, `listing_ok`) | **proved generically**: `readIn_unique`, `readingsIn_exact`, `readingsIn_nodup`, `readIn_none`, `readIn_many`, `readingsIn_limit` for any grammar `G` with `G.wf` and any meaning; `listing_ok` exactly as spec 5.6 writes it, plus `listing_limit`. Spec 5.6's statements follow in ap-2b by instantiating `G := grammar V`, `μ := meaning V` and using `grammar_wf` | `Read.lean` |
| Statement `read_normal` | ap-2b | — |
| Tests: both boundaries of each limit (N−1 and N raw; 63, 64, 65 readings) | **done** twice: LG1-LG8 on synthetic trees (spec 11.2), and on a real parse of a small grammar with phrases of 63, 64, 65, 255 and 256 derivations | `GrammarExamples.lean` 26-72 |
| Tests: duplicate derivations that would hide another meaning; raw-cap saturation; an exhausted step budget | **done**: LG6 and the toy's 256 derivations of one meaning are `limit`; 16 derivations meaning `"a"` and one meaning `"b"` read as `many`; a step budget of 0 and N = 0 are `limit` | 31, 68-71 |
| Tests: the review's counterexamples (FR1 to FR7) | FR1, FR2, FR6, FR7 **done** (`framesOk`); FR3-FR5 are about `normalOk` (ap-2b) | 96-186, 287-313 |
| Tests: the round trips N1 to N5 | ap-2b | — |
| Phase-1 corpus: the 13 `ap0` rows as `#guard`s on raw and meaning counts | **part**: their vocabularies pass `framesOk` (FR7); their raw and meaning counts need the rule table (ap-2b) | 313 |
| N and the step budget fixed from the re-measurement after D9 | **part**: re-measured after D9; both values stand by AP-0's rule and stay provisional (deferred item 5 is open; section 2) | `Read.lean` 16-19 |
| Every fixture of section 5 as a `#guard` on its derivation count and act tree | ap-2b (G5-L0 need the rule table and the meaning) | — |
| Seeded bug (Lean): premodifier on a middle item, A8 reports 3 readings | ap-2b (it is a rule of the table); this item's own seeded bugs are in section 4 | — |
| Moves: nothing (enabler) | nothing | — |

## 4. Seeded bugs

`docs/act-phrases/ap-2/seed_bugs.py` plants each bug, runs its check, and restores the file from git. The results are
in [mutants.json](mutants.json) (`file` and `test` keys). Every bug fails its check, and the restored build passes. A
bug in `Read.lean` is caught first by the proofs. The harness then plants it a second time with the proofs section
cut out (`fixtures_only`), and `GrammarExamples.lean` must fail on its own.

| # | Language, file | Bug | Fails |
|---|---|---|---|
| 1 | Lean, `lean/VE/Acts/Read.lean` | `listing`: `N < ts.length` (a saturated parse is listed) | proofs of `listing_ok`/`listing_limit`; fixtures alone: LG2 |
| 2 | Lean, `Read.lean` | `listing`: `L ≤ ms.length` (exactly 64 readings refused) | proofs; fixtures alone: LG4 |
| 3 | Lean, `Read.lean` | `firsts` keeps duplicates | `mem_firsts`/`nodup_firsts`; fixtures alone: LG7 |
| 4 | Lean, `Read.lean` | `readIn` reads two meanings as the first | `readIn_many`; fixtures alone: the hidden-meaning guard |
| 5 | Lean, `Read.lean` | `DerivedIn` without the meaning conjunct | `readingsIn_exact` and the theorems after it do not prove |
| 6 | Lean, `Read.lean` | `rawCap := 255` | the N−1 guard (255 derivations, one reading) |
| 7 | Lean, `lean/VE/Acts/Syntax.lean` | 31l accepts markers that are not canonical | FR2 and the `' in'` guard |
| 8 | Lean, `Syntax.lean` | 31i dropped (`split ⊆ markers`) | FR6 |
| 9 | Lean, `Syntax.lean` | `Term.accepts .slot` accepts the subject slot `{0}` | the terminals guard |
| 10 | Python, `tools/layer_policy.py` | `VE.Acts.` dropped from layer 3 | `tools/check_lean_imports.py`: "new outward Lean import: VE.Acts.Read -> VE.Grammar.Reading" |

No Rust code changed.

The review (F1) found seven more mutants of `checkVocab` and the limits that kept every `#guard` passing. The fix
treats the class: `tests/test_acts_vocab_mutants.py` plants 54 mutants, each elaborated with `Read.lean`'s proofs cut
out, and each must fail at a `#guard`. They are the review's seven, the same kinds elsewhere (each half of `wordOk`,
31q and 31r, the reserved-word lists swapped, 31s on any head word, each limit one off), and, generated from
`checkVocab`'s own blocks, every D-31 row dropped and every two adjacent rows swapped. A further test checks that the
blocks are D-31's 19 rows in the spec's order. On the fixtures before the fix, 28 of the 54 survived. The fixtures
that kill them are in `GrammarExamples.lean` 83-186: one vocabulary per D-31 row in a table, every pair of rows
joined either way round raising the earlier row's text (D-31's order), and the cases listed in section 9.

The recheck (F7) found six more that kept every `#guard` passing: 31c and 31r read only a head's first word, 31o over
argument markers only or over modifier markers only, 31i letting `split` name a modifier marker, and 31g ignoring
`""`. Their class is a condition over a list that reads only part of it, or the wrong one of a frame's marker lists.
The test now generates it from `Syntax.lean`'s source: every list that `wordsOf`, `firstDup` and `checkVocab` range
over (each receiver of a list method, each `for` and `firstDup` argument) cut to its first element, and every marker
list of a frame (`f.markers`, `f.split`, `f.mods`, both, `ms f`, the markers without `""`) replaced by each of the
others: 126 mutants, plus the review's six as it wrote them. On the fixtures before the fix, 31 of the 126 survived.
Seven of them change no answer of `checkVocab` (a head's first word is absent exactly when the head is; `""` has no
words; 31j has refused `""` as a modifier marker before 31k); they are listed with the reason in `EQUIVALENT`, and a
test checks that each still passes, so a wrong entry fails. The 24 others are killed by the guards of
`GrammarExamples.lean` 189-230: each condition with its fault in a later head word, marker, marker word, frame or
adverb (`seek Asylum`, `take part` beside `take part in`, markers `in, on, in`, adverbs `gladly, rest`), and on the
list 1.4 names (`""` twice refused, `""` split accepted, a modifier marker not split, `in front` with modifier `in`).
In all, 186 mutants: 179 fail at a `#guard` and nowhere else, and 7 are equivalent.

The second recheck (F10) found two more of the same class in places the generator did not look: `ms f`'s modifier
markers cut to the first (an operand of `++`), and the marker words cut to each marker's first word (the list that
`flatMap wordsOf` builds inside its argument). The generator no longer finds lists by their position alone. It
types the names of `Syntax.lean` from their declarations (`_list_names`: every structure field declared `List`,
every definition whose result is a `List`, every let of `checkVocab` annotated `List` or bound to a list, and a test
pins that table), and cuts every occurrence of a list-valued name wherever it stands, each operand of `++`, each
list binding's value, each list a `flatMap`'s function builds, and each list function passed without its argument
(`wordsOf` becomes `fun x => (wordsOf x).take 1`); a test checks that every occurrence of a list-valued name is cut.
The marker-list swaps now include the operands of `(f.markers ++ f.mods)`, and the scope includes the word lists
of 1.2 that the check reads (`joinWords`, `clauseWords`). This adds 31 generated mutants and the review's two as it
wrote them. On the fixtures before the fix, 8 of the 33 survived: the review's two, their generated twins, and 4
that change no answer (cutting `wordsOf m` before `== []`, and `ms f` with a marker list repeated or filtered twice),
listed in `EQUIVALENT` with the reason. The guards of `GrammarExamples.lean` 232-250 kill the others: each
condition that reads `ms f` (31l, 31m, 31n, 31o, 31r, 31s) with its fault in a later modifier marker after `at`,
and 31r and 31s with their fault in a marker's later word (adverb `front`, head `front desk`, beside marker
`in front`). In all, 219 mutants: 208 fail at a `#guard` and nowhere else, and 11 are equivalent.

The third recheck (F11) found four more at the other end of a list: 31f with its first frame skipped (`(fs.drop
1).find?`) or its last (`for f in fs.dropLast`), 31s with its first frame skipped, and 31s reading a head's first
word only when the head has two (`f.head.dropLast.head?`). The generator cut a list only to its first element, so a
guard with its fault in a later element killed every mutant it made. It now cuts each list in each of four ways
(`CUTS`: the first element alone, the last element alone, without the first, without the last), wherever it cut one
before, and a test checks that each way makes one mutant per list. The review's four are added as it wrote them, and
a test checks that each is, up to parentheses, the source of one of the generated mutants. This adds 244 mutants (240
generated). On the fixtures before the fix, 33 of them survived: the review's four, 25 generated ones (the review's
four twins, without the first or the last, and 21 with the last element alone), and 4 that change no answer (a head's
or marker's last word absent exactly when it is empty, 31f's and 31o's shorter prefix), listed in `EQUIVALENT` with
the reason. The guards of `GrammarExamples.lean` 252-285 kill the others: each condition with its fault in the first
element and not in the last (a first head word, marker, marker word, frame or adverb: `Seek asylum`, `take part`
before `take`, a split `by` before `to`, `""` and `in` as modifier markers, markers `in  front`, `In front` and `or
else` before `at`, adverbs `rest, gladly`), and 31s on a one-word head (`on` after `sit ["on"]`). In all, 463
mutants: 448 fail at a `#guard` and nowhere else, and 15 are equivalent.

## 5. Trust, size and tests

- **Trust:** `trust_map.py --check` PASS: K +0, S +69, untied V +76, trusted +145, tied +15. Per file: Syntax.lean
  +109 (S 45, D[V] 53, G[V] 11) and Read.lean +36 (S 24, G[V] 12). `GrammarExamples.lean`'s definitions are T. The
  allowance is signed by standing ruling R16, and the FOLLOW-UPS "## ap-2" row asks for the ties pass.
- **Size:** hand-written lines: Lean 636 (Syntax 128, Read 193, GrammarExamples 315), `tools/layer_policy.py` 1, the
  two evidence scripts 341 (`measure_n.py` 236, `seed_bugs.py` 105) and the review fixes' two tests 546
  (`test_acts_vocab_mutants.py` 489, `test_ap2_limits_provisional.py` 57), plus this report and DELTA. The plan and
  spec copies are 3,393 lines, verbatim and mandated. The evidence JSON is written by the scripts. Product code
  (Syntax and Read, 321) is within the ~600 cap; with fixtures, scripts and tests the total is about 1,520 (review
  F6, a follow-up).
- **Tests:** the selected tests (`mac-pytest.sh --select`, merge base `802b8ff9b`, on `3dbb2184`) ran 66 units, exit
  0, 0 failed. After the sync with main (`01f74cf4a`) they ran again on `04435990` (the code is final; only this
  report changes after it): 66 units, exit 0, 0 failed. No test in `main-known-red.txt` was hit. After the review
  fixes, on `21e9715a`: 74 units (lints, `lake build`, `lean/audit.py` and 73 test files). 73 passed. One failed:
  `test_ap2_limits_provisional.py`, because section 9 quoted the retracted phrase. With section 9 reworded, that
  file's 3 tests pass. No test in `main-known-red.txt` was hit. After the recheck fix (F7), on `7e457d65`: 74 units,
  exit 0, 0 failed (`test_acts_vocab_mutants.py` 383 s of them, on the Mac runner with 6 jobs); `lake build` and
  `lean/audit.py` pass. No test in `main-known-red.txt` was hit. After the second recheck fix (F10), on
  `8c0e99b6`: 74 units, exit 0, 0 failed (`test_acts_vocab_mutants.py` 1,415 s of them, on the VM with 6 jobs, where
  `mac-pytest.sh` yielded to a candidate gate); `lake build` and `lean/audit.py` pass; `trust_map.py --check` passes
  unchanged (trusted +145, K +0). No test in `main-known-red.txt` was hit. After the third recheck fix (F11), on
  `db140213`: 74 units, exit 0, 0 failed (`test_acts_vocab_mutants.py` 1,108 s of them, on the Mac runner with 6
  jobs); `lake build` and `lean/audit.py` pass; `trust_map.py --check` passes unchanged (trusted +145, K +0). No test
  in `main-known-red.txt` was hit. The full gate is the chain's.
- **Overlap:** `tools/layer_policy.py` is also edited by `lean-first/b18`, in a different hunk (lines 116 and 141;
  mine is 135). `git merge-tree HEAD lean-first/b18` merges it cleanly; that branch's other conflicts with this one
  are generated inventories (R12). No other in-flight branch touches `lean/VE/Acts/` or the plan and spec files.

## 6. Next item: ap-2b (and why it will need splitting or a DRI signature)

What remains of AP-2, sized from the stub (draft 1, lines 228-928):

- **ap-2b, the rule table:** `Grammar.lean` (`RuleS`, `schema`, `build`, `grammar`; about 180 trusted lines in the stub)
  and `grammar_wf`. The stub's `computeRanks` is a fixpoint with no proof, so a provable form is structured
  nonterminals with a rank per constructor. Fixtures: raw counts of G5-L0 and of the 13 `ap0` rows (11.2b); the
  plan's seeded bug (a premodifier rule on a middle item makes A8 give 3 derivations).
- **ap-2c, the meaning:** the act trees of 1.5 (`Join` … `Act`, 26 lines), `meaning` with D9 (i)'s refusal (a joined
  filler whose marker is written once, with a first or last part of two or more words, has no meaning; about 250
  lines in the stub), and `readings V := readingsIn (grammar V) (meaning V)`, `read`, `analyse`. Spec 5.6's
  `read_unique`, `readings_exact`, `readings_nodup`, `read_none`, `read_many` and `readings_limit` follow from this
  item's generic theorems and `grammar_wf`. Fixtures: G5-L0's readings and act trees, the 11.2b meaning counts under
  D9 (i), and A8's 3-reading seeded bug.
- **ap-2d, rendering:** `Linearize.lean` (`Atom.normal`, `Atom.canon`, `normalOk`), `read_normal`, FR3-FR5, N1-N5.
  `read_normal` needs an unambiguity argument over the whole rule table, and it is the hardest proof of AP-2.

The rule table and the meaning are each above R16's 150 trusted lines as the stub writes them. Each will need either
a further cut or a DRI signature for its growth. The DRI may prefer to sign AP-2's growth once, as one budget.

## 7. Deviations from the plan and the spec (recorded here, not in the copied plan)

1. `readingsIn`, `readIn` and `DerivedIn` take the grammar and the meaning as arguments, and are generic in the
   meaning's value type. `ReadOutcome` is generic too (`ReadOutcome Act` in ap-2c). Spec 5.4's
   `readings V N b ts := listing N maxReadings (parse (grammar V) N b ts) …` is exactly
   `readingsIn (grammar V) (meaning V) N b ts`, so no statement changes. Spec 5.6's statements are proved in ap-2c,
   as corollaries with the spec's names and the spec's text.
2. `Lexical.Tok`, `Lexical.joinWords` and `Lexical.clauseWords` (AP-1's names, spec 4.2) are defined here, in
   `Syntax.lean`, because the terminals need them first. ap-1a must import them, not define them again (one owner).
3. `framesOk` admits *for* as a head word, as the stub does. Spec 1.4's "not a join word" means the grammar join words
   *and*, *or*, *nor* (1.2); *for* is an ordinary word in the grammar.

## 8. Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: **N.A.**, no Lean answer is relayed (no route, mode or Python reader).
2. Every deliverable built, no rule broken: **PASS**. Section 3 lists every plan row with its place or the cut
   (ap-2b). Grep of the diff: no Python copy of a Lean decision, no authority switch; the one evidence test,
   `test_ap2_limits_provisional.py`, reads saved evidence. The overlap
   is in section 5.
3. Tests and gates can fail: **PASS**. 10 seeded bugs in [mutants.json](mutants.json), each failing a proof, `#guard` or
   check (none at a hash or build-only step); `seed_bugs.py`. After reviews F1, F7, F10 and F11, 448 mutants of `checkVocab`
   and the limits each fail a `#guard`, and 15 generated ones are equivalent, each with its reason (`tests/test_acts_vocab_mutants.py`, section 4).
4. Python, Lean and Rust agree: **N.A.** for the differential: the new modules are Lean only, and Python and Rust
   read nothing of them. Valid inputs still pass: FR7 `#guard` (`GrammarExamples.lean` 313) over every vocabulary
   of spec 11.2 and 11.2b.
5. R8 binding: **N.A.**, no relayed answer.
6. Gate evidence matches the final HEAD: **PASS** for what a builder runs. Synced with main (`01f74cf4a`); the
   commit list is saved in [evidence/commits.txt](evidence/commits.txt) from `main..HEAD --no-merges`; the full gate
   is the chain's, on the final HEAD.
7. No unsigned item: **PASS**. The DELTA's one row cites R16, and `trust_map.py --check` passes with the allowance.
8. Every user-visible change in DELTA: **PASS**. There is no public output change (DELTA's first paragraph); the trust
   growth is row 1.
9. Test selection finds the tests: **PASS**. `select_tests` chose 66 units, not the whole suite. A change to
   `tools/layer_policy.py` selects `tools/check_lean_imports.py`, which is the check seeded bug 10 fails
   (`select_tests.py` `LEAN_LAYER_INPUTS`).
10. Lean statements say what is claimed: **PASS**. Seeded bugs 1-5 break the proofs of `listing_ok`, `listing_limit`,
    `nodup_firsts`, `readIn_many` and `readingsIn_exact`. `listing_ok` is spec 5.6's text, unchanged. No hypothesis
    is added to an approved statement: the approved AP-2 statements are ap-2c's (section 7.1).
11. Budgets fail closed: **PASS**. A step budget of 0 and N = 0 are `limit` (`GrammarExamples.lean` 69-70); a
    saturated parse and 65 readings are `limit` (27, 66, 68); `readingsIn_limit` states the limit outcome exactly.
12. No CPU or memory regression: **N.A.**, no route or pilot path runs this code. The measurement's largest parse is
    19,184 steps (section 2).
13. `Test-removed` trailers: **PASS**. No test was removed or renamed: `gate_collection.py --check --prebuilt` reports
    470 added (the review fixes' tests), 0 removed, 0 refused, 0 stale, 0 malformed.

Build checklist (`prompts/build-checklist.txt`): 13 (seeded mutants) and 18 (fixture numbers computed by `#guard`; a
boundary fixture for each direction of `listing_ok`'s iff: LG1/LG2, LG4/LG5) apply and hold. 6 holds (UNKNOWN as
`limit`, budget 0). 14 holds: `measure_n.py` writes only its evidence file, and `seed_bugs.py` restores every file
from git. 16 holds: roots and audit are regenerated, and FR7 covers every registered vocabulary. The rest are
**N.A.**: no wire contract, relay, text normaliser, state machine or use case is added. 20 holds for the one
evidence test (`test_ap2_limits_provisional.py` reads the saved measurement).

## 9. Review fixes (`ap-2-review.final.md`)

| Finding | Fix | Regression test |
|---|---|---|
| F1 (B): seven `checkVocab` and limit mutants survive | the class: a D-31 table with one vocabulary per row and every pair in D-31's order; 128 and 129 distinct frames; `se3k` as head, marker and adverb, `-in` as marker, `Freely` as adverb, inner `-` and `'` accepted; an adverb equal to a head word and to a marker word; every reserved word of 1.2 as head, marker, modifier and adverb word (*to* and *for* accepted as markers); `take`/`taken`, `in`/`into` and `carry on` (string prefixes and later words are not word prefixes or first words); `rawCap`, `stepBudget` and `maxReadings` pinned | `tests/test_acts_vocab_mutants.py` (54 mutants, generated rows dropped and swapped included; the review's probe passes) |
| F2 (B): the limits called final without the plan's condition | `rawCap` and `stepBudget` say "provisional (plan 11, deferred item 5)"; section 2, its plan row and `measure_n.py`'s docstring say the M1 frames are the measurer's and the values stay provisional; deferred item 5 stays open | `tests/test_ap2_limits_provisional.py` |
| F3 (C): AP-1's names in `Syntax.lean`, layer of `Lexical` | follow-up (ap-1a moves them; section 7.2) | — |
| F4 (C): `maxReadings` copies `VE.Readings.maxChoices` | follow-up (pinned at 64 by a `#guard` meanwhile) | — |
| F5 (C): SR16's bounded re-check and DRI go not recorded | follow-up for the DRI (section 1) | — |
| F6 (C): size over ~600 | follow-up (section 5) | — |

Recheck (`ap-2-looprecheck1.final.md`): F1 and F2 confirmed fixed.

| Finding | Fix | Regression test |
|---|---|---|
| F7 (B): six `checkVocab` mutants survive (31c, 31r on a head's first word; 31o over one marker list; 31i splitting a modifier marker; 31g without `""`) | the class, generated from `Syntax.lean`: every list of 1.4's check cut to its first element, every marker list swapped for each other one (126 mutants, 7 equivalent with their reasons), the review's six as written; one guard per survivor in `GrammarExamples.lean` 189-230 (section 4) | `tests/test_acts_vocab_mutants.py` (186 mutants; the review's probe passes) |
| F8 (C): 31c's `{h}` not pinned | fixed with F7: `seek Asylum` raises 31c's text with the head `seek Asylum` | `GrammarExamples.lean` 193 |
| F9 (C): 31l's second half unreachable | the comment of `GrammarExamples.lean` 138-140 no longer counts 31l among the conditions whose halves are pinned, and says why its second half never decides; the code is unchanged (spec 1.4 states both halves) | — |

Second recheck (`ap-2-looprecheck2.final.md`): F7, F8 and F9 confirmed fixed.

| Finding | Fix | Regression test |
|---|---|---|
| F10 (B): two `checkVocab` mutants survive (`ms f` with its first modifier marker only, an operand of `++`; the marker words with each marker's first word only, a list built inside `flatMap`'s argument); DELTA called every condition pinned with its fault in a later element | the class: the generator types `Syntax.lean`'s names from their declarations and cuts every list-valued name where it stands, each `++` operand, each list binding's value, each list a `flatMap` builds and each list function passed bare; marker lists swapped inside `++` too (33 more mutants, 4 more equivalent with their reasons); guards in `GrammarExamples.lean` 232-250 (section 4); DELTA row 1 now states the coverage the generator checks | `tests/test_acts_vocab_mutants.py` (219 mutants, the review's two by name; `test_the_list_valued_names_are_read_from_the_declarations`, `test_the_generated_mutants_cover_every_list_of_the_check`); PROBE F10 fails before the fix and passes after |

Third recheck (`ap-2-c181429-looprecheck1.final.md`): F10 confirmed fixed; DELTA row 1's R16 conditions hold.

| Finding | Fix | Regression test |
|---|---|---|
| F11 (B): four `checkVocab` mutants survive at the other end of a list (31f skipping the first or the last frame, 31s skipping the first frame, 31s on a one-word head); the generator cut a list only to its first element | the class: every list the generator cuts is cut in each of four ways (`CUTS`: first or last element alone, without the first, without the last; 244 more mutants, 4 more equivalent with their reasons); the review's four as written, each checked to be a generated mutant; guards in `GrammarExamples.lean` 252-285, each condition with its fault in the first element and not the last, and 31s on a one-word head (section 4); DELTA row 1 states the four cuts | `tests/test_acts_vocab_mutants.py` (463 mutants; `test_every_seeded_mutant_fails_a_fixture[31f-g-not-first]`, `[31f-f-not-last]`, `[31s-f-not-first]`, `[31s-one-word-head]`, `test_the_generated_mutants_cover_every_list_of_the_check`); PROBE F11 fails before the fix (all four survive) and passes after |
