# ap-2bb build report: `Atom.canon`, `normalOk` and the render fixtures (Lean only)

**Status: built. No DRI signature is reserved and nothing stops the item.** `read_normal` failed the statement gate as
written, with spec 5.5's `normalOk` (counterexamples C1-C4). The DRI kept its text, strengthened `normalOk`, and cut the
general proof to ap-2bc ([decision](/home/seyran/code/manage-agents/reviews/dri-decisions-20261030-ap-2bb.md), items 1-3,
SIGNED). Delivered: `Atom.canon`, `normalOk` with the DRI's two conditions, `longEnd` (D9 (i)'s one test), and fixtures
FR3-FR5, N1-N5, G6, C1-C4. Trust: S +29, K +0, under R16 ([DELTA.md](DELTA.md)). Open: ap-2bc (the proof).

Read first: plan 2.2 and section 4 "AP-2"; spec 5.5, 5.6 (and its note), 11.2 and 11.2a; ap-2c's REPORT (section 1's
row, section 6); ap-2b's REPORT section 6 item 2; ap-3b's REPORT (`Linearize.lean`); and the synthesis-2 edits for
act-phrases.

## 1. Statement gate: `read_normal`

`read_normal` (spec 5.6) was reviewed and accepted (SR1, draft 2). On main `432763b06`, with `normalOk` written
exactly as spec 5.5 gives it, it is **false**. Each atom below passes that `normalOk` and `framesOk`, and `read` at
`rawCap` and `stepBudget` does not give `ok (one a.canon)`. Evaluated in Lean
([QUESTION-read_normal.md](QUESTION-read_normal.md); fixtures in `RenderExamples.lean`, lines 108-116):

- **C1:** spec 11.2's own G7 atom, `by [secret vote, fixed 0]`. It renders as `{0} be held by secret vote or
  equivalent free voting procedures` and reads `none`. The cause is D9 (i), which was decided after draft 2 wrote
  `normalOk`.
- **C2:** a joined object `[trade unions, {1}]`. It reads `none` (D9 (i) at `Oh`'s `PLh`).
- **C3:** a joined filler of one part. It reads back as a `.one` filler.
- **C4:** a joined filler of no parts. It reads `none`.

I asked the DRI decider (`msg.sh dri`, 2026-10-30 17:16Z). The decision of 17:18Z:

1. Keep `read_normal`'s text. `normalOk` adds two conditions: (a) every joined filler has two or more parts; (b)
   D9 (i), no joined filler has a first or last part of two or more words.
2. Spec 11.2's G7 render fixture changes to: G7's atom is `normalOk` false.
3. The general proof goes to ap-2bc and never lands with `sorry`. Backlog row `ap-2-render-d9` (a design question:
   should the normal form repeat the marker?) is filed by the DRI.

`read_normal` is therefore not in this item, so no theorem statement changes (`lean/statements.txt` gains no line
from this item).

## 2. Design

- **`Atom.canon`** (`Linearize.lean:41`) puts the object first, then the other arguments in their order, and the
  adverbs before the prepositional modifiers. **One owner of the order:** `Atom.normal` (`:47`) now writes the
  arguments as `a.canon.args`. Its output is unchanged, because the object's marker `""` has no words. Every
  existing normal-form and paraphrase `#guard` passes (TableExamples, ElaborateExamples; `lake build`, 1168 jobs,
  exit 0).
- **`normalOk`** (`Meaning.lean:147`) is `atomOk` plus these conditions:
  - each part of an argument, a joined filler or a modifier (`Filler.parts`, `:140`) is a non-empty run of the
    frame's filler words, compared lower-cased against `fillExcl`, the exclusions the grammar's `fill` terminal
    reads; or a slot other than `{0}`; or a fixed phrase;
  - no argument marker occurs twice;
  - each joined filler has two or more parts, sits under no split marker (the object's `""` included), and fails
    `longEnd`.
- **`longEnd`** (`Meaning.lean:77`) is D9 (i)'s test. `applyRule` had written it inline; it now calls `longEnd`, and
  so does `normalOk`. So the refusal and the condition that avoids it have one owner.

## 3. Plan and task rows

| Row (task "Deliver", plan AP-2) | Status | Where |
|---|---|---|
| (1) `Atom.canon` in 5.5's order | **done** | `Linearize.lean:41`; guards 41-48 |
| (1) `normalOk V a`: `atomOk`, non-empty filler words, no `{0}`, no repeated marker, no joined filler under a split marker | **done**, plus the DRI's (a) and (b) | `Meaning.lean:147` (deviation 1); guards 56-98, 108-128 |
| (1) one owner, no second normal-form function | **done**: `Atom.normal` reads `canon`'s order; `longEnd` is shared | section 2 |
| (2) `read_normal` with its lemmas | **not delivered: ap-2bc** (DRI item 3) | section 1 |
| (3) FR3, FR4, FR5 (`normalOk` false) on both sides | **done** | guards 66-76 |
| (3) N1-N5 round trips | **done**: text and `ok (one canon)`, at `rawCap`/`stepBudget` | guards 27-33 |
| (3) G6's render pair (`{0} be subjected to torture`, ...) | **done** | guards 23-25 |
| (3) G7 (DRI item 2): `normalOk` false, reads `none`; with the marker repeated still `ok g7` | **done** | guards 109-111 |
| Each condition on both sides | **done**: each condition accepted and refused; every argument and modifier checked with the refused one first or last; two split markers; `longEnd` on one-part lists and at each end | guards 56-128 |
| A mutant per new trusted definition that breaks a named guard | **done** | section 4 |

FR1, FR2, FR6 and FR7 are `framesOk` rows that ap-2 delivered (GrammarExamples). This item's FR4 atom also has an
object (`asylum`), because `atomOk` requires one for `seek`.

## 4. Seeded bugs and mutants (Lean only; no Python or Rust product code changed)

[seed_bugs.py](seed_bugs.py) plants each bug, builds `VE.Acts.RenderExamples`, records the failing guards and
restores the file ([mutants.json](mutants.json): 18 plants, all KILLED, restored build exit 0). Command:
`python3 docs/act-phrases/ap-2bb/seed_bugs.py`.

| Definition (file) | Plant: killing guards |
|---|---|
| `Atom.canon` (Linearize.lean) | `canon-args-kept`, `canon-object-last`: TableExamples 202, 207; `canon-mods-kept`: RenderExamples 41, 44 |
| `Atom.normal` (Linearize.lean) | `normal-args-raw`: TableExamples 202, 207 |
| `Filler.parts` (Meaning.lean) | `parts-joined-empty`: RenderExamples 61, 70 |
| `normalOk` (Meaning.lean) | `nonempty-dropped`: 56; `filler-words-dropped`: 57, 61; `filler-words-case`: 57; `subject-slot-allowed`: 66, 70, 87, 89; `nodup-dropped`: 74, 76; `split-joined-allowed`: 80, 83, 95; `two-parts-dropped`: 114, 116, 124, 128; `two-parts-one`: 114, 124, 128; `d9-dropped`: 110, 113, 118, 128; `no-frame-accepted`: 98; `atomOk-dropped`: 98 |
| `longEnd` (Meaning.lean) | `longEnd-first-only`: MeaningExamples 115, 118, 120; `longEnd-one-word`: MeaningExamples 51, 90, 112, ... |

`trust_mutants` was run as checklist 13a says: `mac-pytest.sh --trustmut -- --jobs 6 --max-mutants 1000 --allow
docs/act-phrases/ap-2bb/trust-mutants-allow.json --json docs/act-phrases/ap-2bb/trust-mutants.json`. It ran in full
on HEAD `2de6a75d6`, which is the final Lean, and exited 0: 176 KILLED, 8 INVALID, 34 ALLOWED, 0 SURVIVOR, 0 UNKNOWN
([trust-mutants.json](trust-mutants.json)). The allows ([trust-mutants-allow.json](trust-mutants-allow.json)) cover
two kinds of mutant. Ill-typed cuts are refused by Lean with a message the tool doesn't class as a refusal. The others
are equivalent:
- `take 1` or `reverse.take 1` where `head?`/`getLast?` already reads that element;
- the same cuts on `ws` in `!ws.isEmpty`;
- `longEnd`'s drop-first and drop-last on a one-part list, where the other side of `||` reads that same part.

The first run had 15 survivors; each one that wasn't equivalent got a fixture (guards 87-96, 124-127).

## 5. Trust

`uv run python tools/trust_map.py --check` on the final code gives `K +0, S +29, D +0, G +0, unclassified +0, trusted
+29` against the merge base:
- Meaning.lean +22: `normalOk`, `Filler.parts` and `longEnd`.
- Linearize.lean +7: `Atom.canon`, and `Atom.normal`'s line now reads `canon`.

The growth is recorded with `trust_map.py --allow`, "SIGNED by standing ruling R16 (DRI-RULINGS.md), ap-2bb,
2026-10-18". FOLLOW-UPS.md "## ap-2bb" asks for the ties pass (tie `canon`, `normal` and `normalOk` to `read_normal`
once ap-2bc proves it). The new fixture definitions are class T (`tools/trust-classes.json`). DELTA has one row,
R16.

## 6. Deviations

1. **`normalOk` and `Filler.parts` are in `Meaning.lean`, beside `atomOk`, not in `Linearize.lean`.** In
   `Linearize.lean` they would need `import VE.Acts.Meaning`, and that made `tests/test_acts_tree_mutants.py` fail.
   The test assembles `Tree`, `Linearize` and `Table` into one file, and `Tree`'s types were then declared twice
   (5 failures in the selected run on `5c2fa52f5`). It would also have made the renderer depend on the grammar.
   `normalOk` reads nothing from the renderer. `Atom.canon` stays beside `Atom.normal`.
2. **`normalOk` adds (a) and (b)**: DRI decision item 1, SIGNED.
3. **Spec edits** (DRI item 2, the three places it allows, each citing the decision):
   - `docs/spec/act-phrases.md:828` (5.5's `normalOk` sentence);
   - `:1639` (11.2's G7 render sentence);
   - `:1667` (11.2a, row C1-C4).
4. **`read_normal` is not in this item**: DRI item 3; it goes to ap-2bc.
5. **Synthesis round-2 edits:** this item implements none of them. Edits 1, 2, 4 and 5 are about the gate, the wire
   contract, cost and joint choices. Edit 3 makes `Lexical.lean` shared with CI-5, and this item does not touch that
   file. DEC 16 (u0218.s18) is not reached.

## 7. Tests

- **Selected tests.** Command: `mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run`, on `5c2fa52f5`
  (GitHub Actions, 4 shards, 74 units).
  - Shards 1, 2 and 4 passed: 21/21, 18/18 and 17/17.
  - Shard 3: `tests/test_acts_tree_mutants.py` failed (deviation 1), and maxfail left 2 units unrun.
- **After the fix** (`703898f2b`):
  - `mac-pytest.sh -- tests/test_acts_tree_mutants.py`: 14 passed (ve-mac-1).
  - `mac-pytest.sh -- tests/test_consolidation_tools.py tests/test_lean_dump_cache.py`: 348 passed (VM).
- **Builds and generators:**
  - `lake build`: 1168 jobs, exit 0.
  - `python3 lean/audit.py`: PASS, 7540 theorems.
  - `regen_generated.py --write --skip route-cases`: rc 0. `route-cases` needs the Rust release binary, which this
    worktree lacks, and none of its inputs changed.
  - The Lean generators were rerun after each Lean edit.
- No test in main-known-red.txt was selected or failed. The full gate is the chain's.

## 8. Pilot bytes, next items

- **Pilot bytes:** 0, as the task says. Nothing is relayed or rendered on a route yet.
- **ap-2bc:** the general proof of `read_normal` (an unambiguity argument over the whole rule table).
- **ap-3d:** the acts-elaborate relay.
- **ap-4:** readings from derivations.

## 9. Spec re-read

- `Atom.canon` against `docs/spec/act-phrases.md:825-826`.
- `normalOk` against `:828-834` and DRI items 1(a) and 1(b).
- FR3-FR5 against `:1662-1664`.
- N1-N5 and G6 against `:1638-1651`.
- `read_normal`'s text against `:909-910`. It is unchanged and not in this item.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A., because nothing is relayed (no route, mode or schema reaches the new code).
2. Deliverables: PASS. Section 3 maps each task row to its guards; `read_normal` moved by DRI decision item 3.
   - Grep of the diff: no Python copy, no report test, no shared file with an in-flight branch (`lean/VE.lean` is a
     union-merged import list).
3. Tests can fail: PASS. mutants.json has 18 plants, all KILLED; trust-mutants.json exits 0 with 0 survivors.
4. Python, Lean and Rust agree: N.A. (Lean only). The existing normal-form guards still pass (TableExamples 170-207).
5. R8 binding: N.A. (no relay).
6. Gate evidence: PASS. The commit list is `main..HEAD --no-merges` (section 10); the chain runs the gate on the final
   HEAD.
7. Unsigned items: PASS. DELTA row 1 cites R16; the DRI decision signs items 1-3.
8. DELTA: PASS. No output changes (no route reaches `normalOk` or `canon`; `Atom.normal`'s texts are unchanged,
   TableExamples 202 and 207), so the only row is the trust growth.
9. Test selection: PASS. The selection on `5c2fa52f5` included `test_acts_tree_mutants`, which caught deviation 1.
10. Statements: PASS. No statement is added or changed (`read_normal` is not stated here). The
    `normalOk` strengthening is DRI-signed, with the counterexamples mechanised (guards 108-116).
11. Budgets: N.A. No budgeted operation is added; the guards use `read`'s production limits only.
12. CPU or memory: N.A. No route is touched; `normalOk` is a linear pass over one atom.
13. Test-removed trailers: N.A. No test was removed.
14. Both directions and evidence: PASS. Each condition has an accepted and a refused guard (section 3). Each claim
    above names its command. Spec re-read: section 9.

## 10. Commits (`main..HEAD --no-merges`, before this report)

66d7def98, 6b00b710b, 712292416, d6b175b2c, 9bc1d604a, 51d9681a8, 87edb4e3b, 5ef19660e, d5ee457cb, 03472e042,
5c2fa52f5, 703898f2b, 2de6a75d6, 80ed0e83f, 442feff25.

## FIXMAP
- `lean/VE/Acts/Linearize.lean`: `Atom.canon` :41; `Atom.normal` :47 reads `canon`'s argument order.
- `lean/VE/Acts/Meaning.lean`: `longEnd` :77 (D9 (i), read by `applyRule` and `normalOk`); `Filler.parts` :140;
  `normalOk` :147.
- `lean/VE/Acts/RenderExamples.lean`: the fixtures. `lean/VE.lean`: one import.
- `tools/trust-classes.json`: the classes. `docs/trust-baseline.json`: the R16 allowance.
- `docs/spec/act-phrases.md`: DRI-allowed edits at :828, :1639 and :1667.
- Regression: `cd lean && PATH=~/.elan/bin:$PATH lake build VE.Acts.RenderExamples`.
- Seeded bugs: `python3 docs/act-phrases/ap-2bb/seed_bugs.py [ids…]`.
- trust_mutants: the command in section 4; add `--rescore docs/act-phrases/ap-2bb/trust-mutants.json` after an
  allow-only or fixture-only edit.
## END FIXMAP
