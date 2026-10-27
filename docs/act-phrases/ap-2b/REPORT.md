# ap-2b build report: the act grammar's rule table and `grammar_wf` (Lean only)

**No DRI signature is reserved; nothing stops the item.** Trust growth is +140 lines (K +0), signed by standing
ruling R16 ([DELTA.md](DELTA.md) row 1). The whole rule table of spec 5.2 fits in R16's 150 lines, so no part is cut
to ap-2bb. The meaning (with the rules' kinds) is ap-2c. The item is over the ~600-line size guideline (section 5).

Plan and spec on main at `0e7a813e8` (equal to `research/act-phrases-p1` at `bb5b2f90d`):
[act-phrases-PLAN.md](../../spec/act-phrases-PLAN.md) section 4 "AP-2" and 2.2; [act-phrases.md](../../spec/act-phrases.md)
5.1-5.4, 5.6, 11.2, 11.2a, 11.2b. DRI-DECISIONS-PHASE2 "Act-phrases" AP1 (order kept) and AP4 (D9 (i): its refusal
is in the meaning, so the rule table and the raw counts are draft 2's as written). SYNTHESIS 2.6 and 4.2: no shared
file of this item is queued; the overlap check is in section 5.

## 1. Statement gate

The statement review converged on FIX, draft 2 applied it and `act-phrases-p3ver1` verified it: PASS (ap-2's REPORT,
section 1). `grammar_wf`'s text in `Grammar.lean` equals draft 2's (spec 5.6, line 880) character for character. The
other theorems this item adds are helpers (`framesOk_words`, `schema_ok`, `schema_ranked`, `build_wf`, ...), not spec
statements. `lean/statements.txt` only gains lines; no theorem of ap-2 or ap-3 changes its statement.

## 2. Design

- **Structured nonterminals with a rank per constructor**, as ap-2's report proposed in place of the stub's unproved
  `computeRanks` fixpoint. `NT` holds the global nonterminals, `F h x` holds frame `h`'s (`FNT`), and `Core` names the
  four cores. `NT.rank` gives each constructor a rank above that of every nonterminal that starts one of its rules.
- **`schema V`** is 5.2's table rule for rule. Its helpers `items`, `tail` and `many1` write the recurring patterns
  (prefixed items, list tails, one-or-more). **`closed`** adds `X → never` for each nonterminal of a right side that
  has no rule (5.2, last paragraph). **`build`** numbers the nonterminals in order of first appearance as a left side.
  **`grammar V := build (closed (schema V))`**.
- **`grammar_wf`** is `build_wf`, a generic lemma: any rule list numbers into a well-formed grammar when every rule
  is `ok` and the list is closed. It is applied to `closed_ok`, `closed_cl` and `schema_ok`. `schema_ok` uses
  `framesOk` only through `framesOk_words`, which reads two of `checkVocab`'s conditions off a success: every head
  has a word (31b), and so does every marker other than `""` (31l). Those are the two places where a rule could have
  an empty right side, so these are exactly FR1's failure and an empty head (fixtures, section 3).

## 3. Plan rows delivered and not delivered

| Plan or task row | Status | Where |
|---|---|---|
| (1) `RuleS`, `schema`, `build`, `grammar` in a provable form; `Syntax.lean`'s list fields unchanged | **done** (Syntax.lean, Tree.lean, Table.lean, Linearize.lean, Norms/Wire.lean and every route are untouched) | `lean/VE/Acts/Grammar.lean` |
| (2) `grammar_wf` | **done**, draft 2's statement | `Grammar.lean` |
| (3) Raw counts of G5-L0 (11.2) | **done**: G5 2, G5b 0, G6 1, G7 1, G8 2, G9 2, G10 2, G11 1, G12 2, G14v 1, G38 0, G39 0, L6 64, L7 128, L8 256, L0 `none` (budget 0); every spec number holds | `RuleExamples.lean` 36-63 |
| (3) Raw counts of the 13 `ap0` rows (11.2b) | **done**: 1, 1, 1, 0, 1, 1, 0, 0, 1, 1, 1, 1, 1, as 11.2b and ap-2's measurement record them | 77 |
| (3) The plan's seeded bug: a premodifier rule on a middle item makes A8 give 3 | **done**: a third `E1X` rule makes G8 (A8's phrase) 3, and the G8 guard fails (also G9 and the corpus) | [mutants.json](mutants.json) `premodifier-middle-item` |
| (3) One mutant per new trusted definition | **done**: section 4 | `mutants.json`, `trust-mutants.json` |
| Meaning, `readings`, `read`, `analyse`, spec 5.6's other theorems, G5d, the meaning counts of 11.2b | **ap-2c** | — |
| Rendering, `read_normal`, FR3-FR5, N1-N5 | **ap-2d** (with ap-3b's `Linearize.lean`) | — |

Fixtures beyond the spec rows (each check on both sides, at and around its boundary):
- **`grammar_wf` on both sides** (97-109). Every spec vocabulary and every `ap0` vocabulary passes `framesOk`, and its
  grammar is well formed. FR1 (marker `" "`) and an empty head are refused by `framesOk`, and their grammars are not
  well formed, so the hypothesis is needed. One-word markers and heads are the passing boundary. FR2's two spellings
  double a phrase's count, which is why `framesOk` refuses them.
- **Every rule** (112-174). `K` has three frames, one of each shape the table tells apart: an object with split and
  plain markers, no object, and a split object. Its 101 phrases are a greedy cover chosen from 139 written ones.
  Their derivations use every rule except six, and a guard pins exactly those six: *go*'s `REt` and `REP` rules, which
  5.2 writes for every frame but only an object frame's `RM` reads. Each phrase's count is pinned. Each count is 2 to
  the number of the phrase's edge choices.
- **Lists of two** (176-195). `K2` has two of each list, so each element stands at either end. Accepted and refused
  phrases on both sides: an adverb, *be*, a modifier marker's first word and a head's first word are refused as
  fillers, and so is a repeated marker's list without its first member. A guard pins the `X → never` rules.
- **Derivation order** (68). G5's two derivations take its two `REt` rules in order: the edge on the last item comes
  first, then the edge on all items. That is G5d's order, which ap-2c's text depends on.

## 4. Seeded bugs and mutants

[`seed_bugs.py`](seed_bugs.py) plants each bug in `lean/VE/Acts/Grammar.lean` with the proofs cut, builds
`VE.Acts.RuleExamples`, records the failing `#guard` lines, and restores the file from git (restored build: exit 0).
All bugs are in Lean (no Python or Rust product code changed). One per claimed behaviour and per new definition:

| Bug (definition) | Behaviour | Fails (RuleExamples.lean lines) |
|---|---|---|
| `premodifier-middle-item` (globalRules) | plan's bug: A8/G8 gets 3 derivations | 44 (G8), 45, 164 |
| `marker-without-words` (globalRules) | W2: `MK ""` has an empty right side (also breaks `grammar_wf`'s proof) | 97, 105, 174 |
| `no-never-rules` (closed) | 5.2's last paragraph | 97, 105, 195 |
| `adverb-as-filler` (fillExcl) | 1.4's filler words | 164, 182, 191 |
| `start-not-S` (build) | the start symbol | 36-77, 109, 164-182 |
| `rank-coord-0` (NT.rank) | W3 (also breaks the proofs) | 36, 44-77, 97, 105, 164, 174 |
| `grammar-unclosed` (grammar), `nt-none` (RSym.nt?) | the closed schema | 97, 105 (and 195) |
| `kw-as-fill` (kwSyms), `many1-once` (many1), `tail-no-comma-join` (tail), `items-shared-drop-last` (items), `frame-object-list-split` (frameRules), `schema-first-frame-only` (schema) | each definition's rules | spec rows, 164, 174 (each in mutants.json) |
| `Core-drop-rnr`, `FNT-drop-REt`, `NT-drop-E1S`, `RSym-drop-t`, `RuleS-drop-rhs` | data types: a constructor or field dropped | refused by Lean in `Grammar.lean` itself |

`tools/trust_mutants.py` ran on the Mac runner (`mac-pytest.sh --trustmut`, `--max-mutants 1400`, the full run on
`dceb7400f`, then rescored after check-only and allow-only edits). It reports 986 killed, 0 survivor, 0 unknown, 52
invalid, 96 allowed and 0 not run, over all ten selected definitions
([trust-mutants.json](trust-mutants.json)). The first full run had 58 survivors, in two classes:
- lists of one element in the corpus vocabulary, so a cut to the first or the last element changed nothing;
- `closed`'s never rules, which derive nothing, so only the rule list itself shows them.

The two-element-list and never-rule guards killed them, and the run after them left two survivors. Those flip `split`
on only one of a split marker's two list rules; the marker-once phrases of `K2` kill them. Each allowance has its
reason in [trust-mutants-allow.json](trust-mutants-allow.json). 80 are cuts that leave an ill-typed term, which Lean
refuses with a message the tool does not class as a refusal. 16 are equivalent, and I checked each one's raw status:
- `act := 1`: `parse` never reads `act`.
- `build` dropping the first rule: the first two rules are both S's.
- `fillExcl` cutting a word list to its first element: only `head?` is read.
- 11 cuts in `closed`: each adds or drops a never rule only for a nonterminal that has rules (the reason names
  every case).

## 5. Trust, size, tests and checks

- **Trust:** `trust_map.py --check` PASS. K +0, S +126, untied V +14, tied +12, trusted +140, all in
  `Grammar.lean` (per declaration in DELTA row 1). Recorded with `--allow`, signed by R16. The FOLLOW-UPS "## ap-2b"
  row asks for the ties pass (tie `build` by a numbering theorem).
- **Size** (hand-written lines, `git diff --numstat` against the merge base):
  - Lean: `Grammar.lean` 311 (about 166 definitions, 145 proofs) and `RuleExamples.lean` 197.
  - Side tables: `lean/VE.lean` +2, `tools/trust-classes.json` +57, the allow file 35.
  - Evidence: `seed_bugs.py` 75.
  - Documents: DELTA 22 and this report 205.
  - Total: about 900, over the ~600 guideline.
  - The deliverables are the item's three. The excess is the proofs and the fixtures that R16's mutants demanded
    (the covering corpus, and the lists of two). No row can be cut without losing `grammar_wf` or a killed mutant.
  - The JSON evidence and the trust baseline are written by tools.
- **Builds and checks:**
  - `lake build` passes.
  - `python3 lean/audit.py` PASS (637 files, 7,150 theorems).
  - `regen_generated.py --check`: 33 entries current.
  - `gate_collection.py --check --prebuilt`: 19,535 collected; 0 added, 0 removed, 0 refused, 0 stale and 0 malformed.
  - `RuleExamples.lean` elaborates in about 12 s: each phrase list shares one prepared grammar.
- **Selected tests:** `mac-pytest.sh --select -- --base 0e7a813e8 --run` ran on `4d63cfd38` (the final Lean) and
  selected 74 of 466 units. Two failed, `test_trust_budget.py` and `test_trust_ratchet.py`, because the allowance was
  not recorded yet. After `--allow` (`8f504ebfe`) both files pass (110 tests). After that, only evidence, documents
  and one fixture commit changed: `3c920c237` wraps `RuleExamples.lean`'s long lines and changes no fixture (`lake
  build` passes, and the seeded bugs and `trust_mutants` were re-run on it). No test in `main-known-red.txt` was hit.
- **Not run:** the full gate (the chain's, on the final HEAD); no pilot (no route reads the grammar).
- **Overlap:** before I started, no in-flight branch touched `lean/VE/Acts/`. `lean/VE.lean` (a union file) and
  `tools/trust-classes.json` (one entry per module) are also edited by df-2, me-1, jt-2, me-2c and q1-4, in other
  entries.
- **Pilot bytes expected to move:** 0 B (*estimate*). Nothing parses an act yet. AP-4's u092 (+163 B, *estimate*)
  waits for ap-2c and AP-4.

## 6. Next items

1. **ap-2c, the meaning:**
   - add `Kind` to `RuleS`, one kind per rule as 5.2 lists it, with the two rules of each edge told apart;
   - the pieces, `applyKind`, `singleAct`, `coordAct`, and `meaning` with D9 (i)'s refusal;
   - `atomOk`; `readings V := readingsIn (grammar V) (meaning V)`, `read`, `analyse`;
   - spec 5.6's `read_unique`, `readings_exact`, `readings_nodup`, `read_none`, `read_many` and `readings_limit`, as
     corollaries of ap-2's generic theorems and `grammar_wf`;
   - fixtures: G5d, the meanings of G5 to G14v (ap-3's hand-written trees, built by `meaning`), the meaning counts of
     11.2b under D9 (i), and A8's 3 readings.
2. **ap-2d:** `Atom.canon`, `normalOk`, `read_normal`, FR3-FR5, N1-N5 (after ap-3b's `Linearize.lean`).
3. Then ap-3c, ap-3d and AP-4.

## 7. Deviations from the plan and the spec (recorded here, not in the copied plan)

1. **The rules' kinds move to ap-2c.** Spec 5.2's `RuleS` carries a `Kind`. Only the meaning reads it, so no
   fixture of this item could fail when a kind is wrong. So `RuleS` is a left side and a right side here, and the two
   rules of each edge are written alike. ap-2c adds the field and the kinds, and tells the two edge rules apart by
   their order.
2. **Ranks per constructor.** Spec 5.2 says a nonterminal's rank is computed, "one more than the largest rank" of a
   first nonterminal. Here each constructor has a fixed rank that satisfies W3 for every vocabulary (the task's
   "structured nonterminals with a rank per constructor"). The set of derivations does not depend on ranks; their
   order might. G5's order is pinned and equals G5d's (`RuleExamples.lean` 68).
3. **5.2's names** `FSh:m*` and `FNh:m°` are one constructor, `LST m split`. `TM:B`, `TM:F` and `TM:R` are `T own` with
   `bare`, `own` and `rnr`.
4. **The fixture file** is `RuleExamples.lean`, not `GrammarExamples.lean`: `tests/test_acts_vocab_mutants.py`
   assembles `GrammarExamples.lean` with `Syntax.lean` and `Read.lean`, so that file cannot import the grammar.

## 8. Self-review against BUILDER-CHECKLIST

1. N.A.: no Lean answer is relayed (no route, mode or Python reader).
2. PASS: section 3 lists each row with its place or its next item. Grepping the diff finds:
   - no Python or Rust change and no new pytest test;
   - no report test and no authority switch;
   - the overlap check in section 5.
3. PASS:
   - [mutants.json](mutants.json): 19 seeded bugs, 14 killed by a `#guard` with the proofs cut, and 5 data-type
     mutants refused by Lean (`seed_bugs.py`).
   - [trust-mutants.json](trust-mutants.json): exit 0, with 986 killed and 0 survivor. Each allowance has its reason
     (section 4).
4. N.A.: no Python or Rust path reads the grammar, and no existing input changes behaviour. Valid inputs still pass:
   every vocabulary of 11.2 and 11.2b is `framesOk`, and its grammar is well formed (`RuleExamples.lean` 97).
5. N.A.: no relayed answer.
6. PASS for what a builder runs. The base is `git merge-base` (`0e7a813e8`), and the commit list below is from
   `main..HEAD --no-merges`. The full gate is the chain's.
7. PASS: DELTA's one row cites R16 and meets its conditions (per file, re-measured, every definition exercised, and
   the FOLLOW-UPS row). No row reserves a signature.
8. PASS: there is no user-visible change, and DELTA says why it has only the trust row.
9. PASS: `select_tests.py --base 0e7a813e8` selects 74 of 466 units, not all of them. The selection includes
   `lake build`, which builds `VE.Acts.RuleExamples`, so every seeded bug fails a selected unit (`seed_bugs.py` runs
   the same build).
10. PASS:
    - `grammar_wf` is about `grammar V`, the value the parser reads.
    - `rank-coord-0` and `marker-without-words` break its proof.
    - Its statement equals draft 2's, and no hypothesis is added.
11. N.A. for new budgets (none is added). The existing ones fail closed on the real grammar: L0 (step budget 0) is
    `none`, and L8 saturates at N (`RuleExamples.lean` 62-63).
12. N.A.: no route or pilot runs the grammar. The largest fixture parse is L8's.
13. PASS: no test removed or renamed. `gate_collection.py --check --prebuilt` reports 0 added, 0 removed, 0 refused,
    0 stale and 0 malformed.

Build checklist (`prompts/build-checklist.txt`):
- 13 and 13a apply and hold (section 4).
- 16: the roots and audit are regenerated (`regen_generated.py --check`).
- 17: the statement is compared with the approved text (section 1).
- 18: the numbers are computed by `#guard`, with both sides of `grammar_wf`'s implication.
- 22: the selected tests ran; the full gate is the chain's.
- 23: DELTA.
- The rest are N.A.: no wire contract, relay, text normaliser, state machine or use case is added.

## 9. Commits (`main..HEAD --no-merges`, before this report)

`222440001` rule table and `grammar_wf`; `4993b5b84` fixtures; `f8f06fab5` rank tied to `schema_ranked`, trust
classes, regenerated inventories; `8723bdd0e` lists of two and never rules; `dceb7400f` allow file; `b1a102f00`
marker-once fixtures; `51b7a0b28` declarations; `5d2b0d99d` seeded bugs, trust_mutants exit 0; `4d63cfd38` rescore;
`8f504ebfe` trust allowance (R16); `3c7a0303f` DELTA; `560d8875d` compact allow file; `5d536b4e1` rescore;
`3c920c237` fixture lines wrapped; `9b819b962` seeded bugs re-recorded; `6390217a6` trust_mutants re-run.
