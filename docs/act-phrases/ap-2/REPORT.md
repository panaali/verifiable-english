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
| Generated: roots, `Audit.lean`, axioms, statements, pins, gate collection | **done** with `regen_generated.py --write` and `--resolve`. Pins are unchanged (no checker changed). The gate collection is unchanged (no pytest added): `gate_collection.py --check --prebuilt` reports 0 added, 0 removed | — |
| Statement `grammar_wf` | ap-2b | — |
| Statements `read_unique`, `readings_exact`, `readings_nodup` (and spec 5.6's `read_none`, `read_many`, `readings_limit`, `listing_ok`) | **proved generically**: `readIn_unique`, `readingsIn_exact`, `readingsIn_nodup`, `readIn_none`, `readIn_many`, `readingsIn_limit` for any grammar `G` with `G.wf` and any meaning; `listing_ok` exactly as spec 5.6 writes it, plus `listing_limit`. Spec 5.6's statements follow in ap-2b by instantiating `G := grammar V`, `μ := meaning V` and using `grammar_wf` | `Read.lean` |
| Statement `read_normal` | ap-2b | — |
| Tests: both boundaries of each limit (N−1 and N raw; 63, 64, 65 readings) | **done** twice: LG1-LG8 on synthetic trees (spec 11.2), and on a real parse of a small grammar with phrases of 63, 64, 65, 255 and 256 derivations | `GrammarExamples.lean` 26-71 |
| Tests: duplicate derivations that would hide another meaning; raw-cap saturation; an exhausted step budget | **done**: LG6 and the toy's 256 derivations of one meaning are `limit`; 16 derivations meaning `"a"` and one meaning `"b"` read as `many`; a step budget of 0 and N = 0 are `limit` | 31, 67-70 |
| Tests: the review's counterexamples (FR1 to FR7) | FR1, FR2, FR6, FR7 **done** (`framesOk`); FR3-FR5 are about `normalOk` (ap-2b) | 102-132, 160 |
| Tests: the round trips N1 to N5 | ap-2b | — |
| Phase-1 corpus: the 13 `ap0` rows as `#guard`s on raw and meaning counts | **part**: their vocabularies pass `framesOk` (FR7); their raw and meaning counts need the rule table (ap-2b) | 160 |
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

## 5. Trust, size and tests

- **Trust:** `trust_map.py --check` PASS: K +0, S +69, untied V +76, trusted +145, tied +15. Per file: Syntax.lean
  +109 (S 45, D[V] 53, G[V] 11) and Read.lean +36 (S 24, G[V] 12). `GrammarExamples.lean`'s definitions are T. The
  allowance is signed by standing ruling R16, and the FOLLOW-UPS "## ap-2" row asks for the ties pass.
- **Size:** hand-written lines: Lean 483 (Syntax 128, Read 193, GrammarExamples 162), `tools/layer_policy.py` 1, and
  the two evidence scripts 339 (`measure_n.py` 234, `seed_bugs.py` 105), plus this report and DELTA. The plan and
  spec copies are 3,393 lines, verbatim and mandated. The evidence JSON is written by the scripts. Product code is
  within the ~600 cap; with the evidence scripts the total is about 820.
- **Tests:** the selected tests (`mac-pytest.sh --select`, merge base `802b8ff9b`, on `3dbb2184`) ran 66 units, exit
  0, 0 failed. After the sync with main (`01f74cf4a`) they ran again on `04435990` (the code is final; only this
  report changes after it): 66 units, exit 0, 0 failed. No test in `main-known-red.txt` was hit. The full gate is the
  chain's.
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
   (ap-2b). Grep of the diff: no Python copy of a Lean decision, no new report test, no authority switch. The overlap
   is in section 5.
3. Tests and gates can fail: **PASS**. 10 seeded bugs in [mutants.json](mutants.json), each failing a proof, `#guard` or
   check (none at a hash or build-only step); `seed_bugs.py`.
4. Python, Lean and Rust agree: **N.A.** for the differential: the new modules are Lean only, and Python and Rust
   read nothing of them. Valid inputs still pass: FR7 `#guard` (`GrammarExamples.lean` 160) over every vocabulary
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
11. Budgets fail closed: **PASS**. A step budget of 0 and N = 0 are `limit` (`GrammarExamples.lean` 68-69); a
    saturated parse and 65 readings are `limit` (27, 65, 67); `readingsIn_limit` states the limit outcome exactly.
12. No CPU or memory regression: **N.A.**, no route or pilot path runs this code. The measurement's largest parse is
    19,184 steps (section 2).
13. `Test-removed` trailers: **PASS**. No test was removed or renamed: `gate_collection.py --check --prebuilt` reports
    0 added, 0 removed, 0 refused, 0 stale, 0 malformed.

Build checklist (`prompts/build-checklist.txt`): 13 (seeded mutants) and 18 (fixture numbers computed by `#guard`; a
boundary fixture for each direction of `listing_ok`'s iff: LG1/LG2, LG4/LG5) apply and hold. 6 holds (UNKNOWN as
`limit`, budget 0). 14 holds: `measure_n.py` writes only its evidence file, and `seed_bugs.py` restores every file
from git. 16 holds: roots and audit are regenerated, and FR7 covers every registered vocabulary. The rest are
**N.A.**: no wire contract, relay, text normaliser, state machine, use case or report test is added.
