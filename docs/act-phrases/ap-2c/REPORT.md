# ap-2c build report: the meaning, `readings`, `read` and `analyse` (Lean only)

**No DRI signature is reserved; nothing stops the item.** Trust growth is +135 lines (K +0), signed by standing
ruling R16 ([DELTA.md](DELTA.md) row 1). Every deliverable of the task is built, so nothing is cut to ap-2cb. The item
is over the ~600-line size guideline (section 5).

Plan and spec on main (`docs/spec/act-phrases-PLAN.md`, `docs/spec/act-phrases.md`): plan "AP-2" and 2.2; spec 1.5,
5.3, 5.4, 5.6, 11.2, 11.2b; D9 (i) (DRI-DECISIONS-PHASE2 AP4: the refusal is in the meaning). Read: ap-2's REPORT
section 6, ap-2b's REPORT, ap-3's REPORT (the act trees are `VE.Acts.Tree`'s, used and not redefined).

## 1. Statement gate

Draft 2's statement review converged on FIX, draft 2 applied it and `act-phrases-p3ver1` verified it: PASS (ap-2's
REPORT, section 1). `read_unique`, `read_none`, `read_many`, `readings_exact`, `readings_nodup`, `readings_limit` and
`analyse_one` in `lean/VE/Acts/Readings.lean` equal spec 5.6's text after whitespace normalisation (compared by
script on the final file). Each is a corollary of ap-2's generic theorem (`readIn_unique`, ... `readingsIn_limit`) and
ap-2b's `grammar_wf`. No merged theorem of ap-2, ap-2b, ap-3 or ap-3c changes; `lean/statements.txt` only gains lines.

## 2. Design

- **A rule's kind is read from the rule, not stored.** Spec 5.2's `Kind` column is a function of the rule. Its left
  side gives the kind, and so does the shape of its right side (an adverb, or a marker and a filler). For the five
  edges whose two rules are written alike, so does which of the two it is. `meaning V` looks the node's rule up in
  `closed (schema V)`, the list `grammar V` numbers. A rule equal to the one before it is an edge's second, read
  over all (`rs.extract (i - 1) i == #[r]`). So `Grammar.lean` and `RuleS` stay as ap-2b merged them, and no kind is
  written twice. A fixture pins that only the edges' rules are alike (`edgeOnly`, 183-185).
- **Pieces, bottom-up** (spec 5.3): words, parts, join words, function words, a head, lists, elements (`Elt` with
  `Att`: own or all), split constructs, items and acts. `singleAct` adds each element to the last atom or to all;
  `coordAct` adds each to its own item's atom or to all. An edge's near end is its own item's: the first item for
  `E1X`, the last for the trailing and shared-object edges, the last part after a split.
- **D9 (i)** is one test at `PL`, the list of a marker written once (`OL`, `Oh`'s `PLh`, `OSh`). A first or last part
  `.words` of two or more words has no meaning. `RL` (a repeated marker) is not refused.
- `readings V := readingsIn (grammar V) (meaning V)` and `read V := readIn …` (ap-2's deviation 1); `analyse` is spec
  5.4's text.

## 3. Plan rows delivered and not delivered

| Plan or task row | Status | Where (`MeaningExamples.lean` lines) |
|---|---|---|
| (1) `meaning` over `VE.Acts.Tree`'s acts with D9 (i)'s refusal | **done** | `Meaning.lean`; 112-124 |
| (2) `readings`, `read`, `analyse` | **done** | `Readings.lean`; 33-68 |
| (3) spec 5.6's six theorems (and `analyse_one`) from ap-2's generic theorems and `grammar_wf` | **done**, draft 2's statements | `Readings.lean` 30-66 |
| (4) G5-L0's readings and act trees (11.2) | **done**: G5 (and G5d's order), G5b, G6, G7, G8 (with the two non-derived trees absent), G9, G10, G11, G12, G14v, G38, G39, L6, L7, L8, L0; `read`'s `ok`/`many`/`none`/`limit` as 11.2 lists. ap-3's hand-written trees (`TableExamples`) are now each built by `meaning` | 33-68 |
| (4) 11.2b's meaning counts under D9 (i) | **done**: 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, the spec's "Under F13 (i)" column | 90 |
| (4) A8's 3-reading seeded bug | **done**: the plan's plant (a third premodifier rule) gives A8 three meanings, and the A8 guard fails | 45; mutants.json `premodifier-middle-item` |
| (4) one mutant per new trusted definition | **done**: section 4 | mutants.json, trust-mutants.json |
| Each new check on both sides, at and around its boundary | **done**: D9 (i) at the first, last and middle part, with a slot or a fixed phrase at an end, for `O`, `OS`, `OL`, and `RL` not refused; `atomOk`'s object, argument-marker, modifier-marker and adverb conditions, each accepted and refused, at both ends of each list; `actOk` with one and two atoms, the failing one first or last | 112-171 |
| Rendering, `read_normal`, `Atom.canon`, `normalOk` | ap-2d (task: "beside them") | — |

## 4. Seeded bugs and mutants

[seed_bugs.py](seed_bugs.py) plants each bug in a file this item adds (Readings.lean with its theorems cut), or, for
the plan's bug, in `Grammar.lean`. It builds `VE.Acts.MeaningExamples` and records the failing guard. It then
restores the file. All are Lean (no Python or Rust product code changed). 36 plants: 32 KILLED, 4 REFUSED (a data
type's constructor dropped; `Derived` refused by its theorems), none survives; restored build exit 0.

| Definition | Plants (id: killing lines of `MeaningExamples.lean`) |
|---|---|
| `globalRules` (Grammar.lean, the plan's) | `premodifier-middle-item`: 45 (A8: 3 meanings), 185 |
| `Att`, `Elt`, `Piece` | `Att-drop-all`, `Elt-drop-mod`, `Piece-drop-list`: REFUSED by Lean |
| `Atom.add` | `add-arg-first`: 82, 155; `add-mod-dropped`: 33, … |
| `addPiece` | `all-as-own`: 33, …; `split-first-member`: 37, … |
| `joinAct` | `nor-as-or`: 48, 80; `and-unshared`: 78, 85 |
| `baseAtom` | `be-as-to`: 33, … |
| `singleAct` | `single-unshared`: 78, 85; `single-to-first`: 51 |
| `coordAct` | `coord-own-fw`: 48 (G9's *be*); `coord-first-item`: 33, … |
| `listOf`, `itemOf` | `list-keeps-join`: 33, …; `item-no-fw`: 33, … |
| `applyRule` | `d9-no-last`: 115, 118, 120; `d9-no-first`: 90, 115, …; `d9-also-repeated`: 38, 66, 124, 148; `edge-second-near`: 33, …; `rnr-args-own`: 33, …; `split-not-split`: 37, … |
| `piecesOf` | `fixed-as-slot`, `second-never`, `kids-reversed`: 33, … |
| `atomOk` | `no-object-check`: 131, 142, 163; `no-marker-check`: 136, 163; `no-mod-check`: 133, 166; `no-adverb-check`: 138, 166 |
| `actOk`, `meaning` | `join-of-one`: 142; `meaning-no-actOk`: 90, 131, 133, 136 |
| `readings`, `read`, `analyse` | `readings-budget-0`, `read-budget-0`: 33, …; `analyse-never`: 66 |
| `Derived` (tied) | `Derived-true`: REFUSED by `read_unique` (Readings.lean 27) |

**Mechanical mutants** ([trust-mutants.json](trust-mutants.json), on the merged HEAD `292392ba4`, base `b8eac7455`,
run on ve-mac-1 with `--jobs 6`): 504 mutants, 352 KILLED, 66 INVALID, 86 ALLOWED, 0 SURVIVOR, 0 UNKNOWN; exit 0.
Each allowance in [trust-mutants-allow.json](trust-mutants-allow.json) has its reason. They are ill-typed cuts that
Lean refuses with a message the tool does not class as a refusal, and equivalents the grammar's structure gives (one
join word per list, never at an end; one head per item; one split construct per single item; *to* first and *be*
last among the function words; D9's lists of two or more parts). The first runs' survivors are fixed. Fixtures
(148-171) kill those that changed a meaning: the conclusion mark, a single item that begins with an adverb, three
arguments, the split object's reading, and `atomOk` and `actOk` at both ends of each list. Four equivalent paths went
from the code: the `OL` arm, the `S` arm, `itemOf`'s filter and the edge list.

## 5. Trust, size, tests and checks

- **Trust** (`python3 tools/trust_map.py --check`, final HEAD): K +0, S +110, untied V +25, trusted +135 (Meaning.lean
  +128, Readings.lean +7; `Derived` is G[V] tied to `derived_iff`). Recorded with `trust_map.py --allow`, signed by
  R16; check PASS. The FOLLOW-UPS.md row is under "## ap-2c".
- **Size** (`git diff --numstat $(git merge-base HEAD main)`, hand-written): Meaning.lean 146, Readings.lean 67,
  MeaningExamples.lean 187, VE.lean 3, seed_bugs.py 114, trust-mutants-allow.json 35, trust-classes.json 58: 610,
  plus this report and DELTA, about 780. That is over the ~600 guideline. The fixtures the mutants asked for (148-171)
  and the evidence script are the excess. No deliverable was added beyond the task's four.
- **Checks on the final code:** `lake build` (all, after the main merge) passes; `python3 lean/audit.py`: PASS, 7,258
  theorems; `uv run python tools/regen_generated.py --write --skip route-cases` (route-cases needs a Rust release
  binary the worktree lacks, and no route is touched); `tools/gate_collection.py --check --prebuilt`: 19,905
  collected, 0 added, 0 removed, 0 refused/stale/malformed.
- **Selected tests** (`mac-pytest.sh --select`, once on the final code): 88 units, all exit 0 (section 9).
- **Pilot bytes:** 0 itself (estimate). Nothing reads a joined act on a route yet; AP-4 (u092, +163 B est.) and ap-3d
  need `read`. Nothing is claimed before a pilot audit.

## 6. Next items

ap-3d (the relay, with ap-3c), then AP-4 (protocol queue after qt-a3c and SC-1c); ap-2d (`Atom.canon`, `normalOk`,
`read_normal`, FR3-FR5, N1-N5) beside them. Nothing of ap-2c is left for an ap-2cb.

## 7. Deviations from the plan and the spec (recorded here, not in the copied plan)

1. **No `Kind` field.** Spec 5.2 gives `RuleS` a `Kind`, and ap-2b's report said ap-2c would add it. The kind is read
   from the rule instead (section 2), so `RuleS` and the rule table are unchanged (one owner). ap-2b's review F2 (C)
   asked that "the real premodifier seeded bug" be planted once kinds exist. Without kinds, the plan's plant (a third
   alike `E1X` rule) reads as `all`, and A8 then has three derivations with meanings. The A8 guard (45) counts every
   derivation's meaning, so it fails with 3. `RuleS` is not re-touched, so no trust estimate counts it.
2. **`Derived V ts A := DerivedIn (grammar V) (meaning V) ts A`.** That unfolds to spec 5.6's text, and
   `derived_iff` states that text (`Iff.rfl`). It ties `Derived`, which no check can compute.
3. **`Att` is own or all.** Spec 5.2 says "first", "last" or "all" for an edge. Here the near end is the element's own
   item's (the first item, or the last item or part), which is the same atoms.
4. **The meaning's error texts** ("an atom does not fit its frame", "this derivation has no meaning") are never shown:
   `valueOf` drops them, and 5.3 fixes none.

## 8. Self-review against BUILDER-CHECKLIST

1. Typed Lean answers: N.A. (no relay, no route, no service mode).
2. Deliverables: PASS, section 3; no Python copy of a Lean decision, no report test, no shared file of an in-flight
   branch except generated and merge-driver files (`VE.lean`, `Audit.lean`, statements, trust-classes).
3. Tests can fail: PASS: 36 seeded bugs (section 4); trust_mutants exit 0 with the allow file committed.
4. Python, Lean and Rust agree: N.A. (Lean only); the existing fixtures (RuleExamples, TableExamples) still pass.
5. R8 binding: N.A. (no relay).
6. Gate evidence: PASS: main merged at `b8eac7455`, generated files refreshed; the commit list (section 10) is
   `main..HEAD --no-merges`; the chain runs the gate on the final HEAD.
7. Unsigned items: PASS: DELTA row 1 cites R16 with its evidence.
8. DELTA: PASS: no output changes (no route reaches the new modules), so the only row is the trust growth.
9. Test selection: PASS: section 9 (the selection of the changed Lean modules).
10. Statements: PASS: section 1 (spec text, compared by script); each is proved from the generic theorem, and
    `Derived-true` is refused by `read_unique`.
11. Budgets: PASS: `read` and `readings` with step budget 0 are `limit` (L0, 64); raw cap at N (L8) is `limit`.
12. CPU or memory: N.A. for routes (none touched); `meaning` builds the rule array once per vocabulary.
13. Test-removed trailers: N.A.: no test removed (`gate_collection.py --check --prebuilt`: 0 removed).

## 9. Selected tests

`zsh mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run` on `a1456e5d` (clean), ve-mac-1, once:
88 of 477 test units selected (among them `test_acts_vocab_mutants`, `test_acts_tree_mutants`,
`test_acts_lexical_mutants`, `test_trust_budget`, `test_trust_mutants`, `test_lean_dump_cache`), each exit 0; 0 failed.
No test of main-known-red.txt was selected or failed; nothing pre-existing to report.

## 10. Commits (`main..HEAD --no-merges`, before this report)

dff8c2fb6, 292392ba4, d2d4919a6, ea9cc3ba9, e7aac35f7, b1d389d77, 30247cbfc, d5e11f91e, 83fbcc46f, 734a4dd84,
d8b07c596, 274a90b18, 4b050430a, 69d7f20f2, b68664af9, 89ca1111a, 6a243d047.

## FIXMAP
- `lean/VE/Acts/Meaning.lean`: the meaning (spec 5.3, D9 (i)): pieces, the act-building steps, `atomOk`, `actOk`.
- `lean/VE/Acts/Readings.lean`: `readings`, `read`, `analyse`, `Derived` (5.4) and spec 5.6's theorems.
- `lean/VE/Acts/MeaningExamples.lean`: the fixtures (11.2, 11.2b, D9 (i), `atomOk`, list ends, edges).
- `lean/VE.lean`: three import lines. `tools/trust-classes.json`: the classes of the new declarations.
- `docs/trust-baseline.json`: the R16 allowance (written by `trust_map.py --allow`).
- `docs/act-phrases/ap-2c/`: REPORT, DELTA, seed_bugs.py (→ mutants.json), trust-mutants.json and its allow file.
- Key definitions: `Att` Meaning.lean:20, `Elt` :23, `Piece` :27, `Atom.add` :33, `addPiece` :38, `joinAct` :43,
  `baseAtom` :48, `singleAct` :52 (5.3 single item), `coordAct` :59 (5.3 coordination), `listOf` :65, `itemOf` :71,
  `applyRule` :77 (each rule's kind; D9 (i) at the `PL` arm), `piecesOf` :115 (the rule lookup, an edge's second
  rule), `atomOk` :128, `actOk` :136, `meaning` :140.
- `readings` Readings.lean:15, `read` :17, `analyse` :19, `Derived` :22, `derived_iff` :25, `read_unique` :30,
  `read_none` :36, `read_many` :40, `readings_exact` :45, `readings_nodup` :49, `readings_limit` :53, `analyse_one` :63.
- Regression: `cd lean && PATH=~/.elan/bin:$PATH lake build VE.Acts.MeaningExamples` (every guard; RuleExamples and
  TableExamples too).
- Seeded bugs: `python3 docs/act-phrases/ap-2c/seed_bugs.py [ids…]` (ids rerun and merged into mutants.json).
- Generated after a Lean change: `uv run python tools/regen_generated.py --write` (statements, declarations,
  predicates, axioms, Audit.lean); then `python3 lean/audit.py` and `python3 tools/trust_map.py --check`.
- trust_mutants: `zsh /home/seyran/code/manage-agents/mac-pytest.sh --trustmut -- --jobs 6 --max-mutants 1000
  --allow docs/act-phrases/ap-2c/trust-mutants-allow.json --json docs/act-phrases/ap-2c/trust-mutants.json`
  (add `--rescore docs/act-phrases/ap-2c/trust-mutants.json` after an allow-only or fixture-only edit).
## END FIXMAP
