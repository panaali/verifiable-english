# ci-3b: the `String.splitOn` lemma library, `preposed_eq` and `readStep_conservative` (commands-imperatives section 7)

Status: built. Both statements are proved, with no `sorry`:
- `preposed_eq`, with the DRI's `hb`;
- `readStep_conservative`, exactly as section 7 states it.

Nothing is cut. The builder asked whether `readStep_conservative` could move to ci-3bb on size; the DRI ruled no
(reviews/dri-decisions-20261109-ci-3b.md item 1: proof lines for gated statements are exempt from ~600). No route calls
`readStep`, so no verdict, wording or pilot byte changes. There is no DELTA row: the item adds theorems only. Trust
growth is `splitOnL` (+11, R16, item 2 of the same decision). Next item: ci-4, after ci-3.

## Plan rows delivered (spec 9a12df17a section 7; plan CI-3; task deliverables)

| Deliverable | Commit | Evidence |
|---|---|---|
| (1) SplitOnLemmas.lean: splitOn and intercalate lemmas for a multi-character separator, each with a `#guard` | 7116b078a, 469f86398 | `lake build VE.Commands.SplitOnLemmas`; `#guard`s at lines 294-301 |
| (2) `preposed_eq` (with `hb`) | 7116b078a | StepsProofs.lean `preposed_eq`; `hb` fixtures `padded` |
| (2) `readStep_conservative` | 469f86398 | StepsProofs.lean `readStep_conservative`; the conservative `#guard` |
| (2) answer "Does W1's act linter make `hs` unnecessary?" | this REPORT | below |
| (3) lean/VE.lean import, tools/layer_policy.py layer 4, generated inventories | 7116b078a, regen commit | `check_lean_imports.py`; `regen_generated.py --write` |

### SplitOnLemmas.lean

`splitOnL` is a `List Char` spec of `String.splitOn`. Its lemmas, over `List Char` and over `String`:
- `splitOn_data` (the bridge): `s.splitOn t = (splitOnL t.data s.data).map String.mk` for every `t ≠ ""`. It is proved
  by following `String.splitOnAux` byte by byte, including the restart after a partial match. The `#guard`s at lines
  300-301 check it on a partial and an overlapping match.
- `splitOn_none`: a separator that does not occur gives the whole string.
- `intercalate_splitOn`: `t.intercalate (s.splitOn t) = s`.
- `splitOn_free`: the pieces hold no occurrence of the separator.
- `splitOn_first`: the first-occurrence decomposition `s = a ++ t ++ b`, with `a` free of `t`.
- `splitOn_two`: there are at least two pieces exactly when the separator occurs.
- `prefix_first`: a prefix without the separator's first character stays inside the first piece.
- The `List Char` twins of each.

`VE.Acts.Lexical.splitOn_space` (one space) and `VE.Readings`' `splitOn_dunder` are special cases of these. They are
left in place because their files are outside this item.

### StepsProofs.lean

- `preposed_eq` uses three lemmas:
  - `shapes_preposed`: `<x>` is a piece of the split at `, `;
  - `hasThen_preposed`: `<x>.` holds no `, then `;
  - `trimmed_infix`.
- `readStep_conservative` is `readStep_core` plus `one_begins`:
  - `readStep_core`: `hs` rules out the `seq` shape;
  - `one_begins`: over a decoded environment, a wording that `readCommand` reads as `one` has a body that begins with
    neither `If ` nor `Then `.
- `one_begins` traces the act linter:
  - `body_prefix` and `splitLast_prefix`: the body keeps the `If `/`Then ` prefix through `splitLastIf` and the
    `Do not ` test.
  - `decoded_actIn`: the act passes `canonicalActIn` (`canonicalAct`, or `Acts.Lexical.check` under `acts@0`).
  - `actIn_shape`: the act is `" ".intercalate W` and begins `{0} `. No brace-free word is `if` or `then` in any case,
    by `actReserved` and by `check_no_clause`.
  - `act_rest` and `verb_head`: its second word follows `{0} ` and opens no slot (`actVerb`, through `surfaceWords`).
  - `decode_templates` and `templates_act`: `slotsApart` holds for the act (`checkTemplates`).
  - `filled_word`: `fillHoles` copies the verb unchanged, and `slotsApart` refuses a slot attached to a letter, so the
    filled text begins with `if `/`then ` only if the verb is `if`/`then`. The linter refuses that verb.
- Fixtures (lines 654-673):
  - the rewritten wording "Click Ask, if draft is approved.";
  - `hasThen`;
  - a conservative row over `E_web`;
  - `hb`'s counterexample, `padded`.

### Statement comparison

Both theorems equal section 7's text after whitespace normalisation, except for `hb`. The check is an inline
`python3` snippet: it cuts `theorem <name> ` up to the first blank line or `:=` in /tmp/ci3b-spec.md (`git show
9a12df17a:docs/spec/commands-imperatives.md`) and in StepsProofs.lean, and joins whitespace.
- Output for `preposed_eq`: `equal after removing hb: True | hb present: True`.
- Output for `readStep_conservative`: `True`.

The one addition, in `preposed_eq` after `h`: `(hb : (trimmed s).utf8ByteSize ≤ maxWordingBytes)`. SIGNED by the DRI
2026-11-09, reviews/dri-decisions-20261109-ci-3a-wording.md item 1. `readStep_conservative` does not need it.

`hb` is needed. The counterexample is mechanised in the fixtures (StepsProofs.lean, `padded`):
- "If draft is approved," ++ 390 spaces ++ "click Ask." has the shape `.preposed "draft is approved" (389 spaces ++ "click Ask")`.
- Its trimmed form is over `maxWordingBytes`, so `step` gives `.limit`.
- `web` of the rewritten wording gives `.one ⟨.require, "click_ask_required", [], approvedDraft⟩`, because
  `readCommand` trims the spaces away.

So `preposed_eq` without `hb` is false.

spec re-read:
- `preposed_eq` against /tmp/ci3b-spec.md:960-962 (spec 955-962): names `c x r h`, the `↔` order, `capitalise x ++ ", if " ++ c ++ "."`.
- `readStep_conservative` against /tmp/ci3b-spec.md:954-958: `j r hd h hs`, `.one r false`.
- the `hs` question against /tmp/ci3b-spec.md:1053-1059.

## Does W1's act linter make `hs` unnecessary?

No. `hs` stays, as the spec's computed answer says. What is proved:
- `readStep_core` uses `hs` once, to rule out the `seq` shape (the body has no `, then `).
- `one_begins` rules out the `If ` and `Then ` shapes from the act linter, without `hs`.
- The linter constrains only the act phrase, which is the body before the last `, if `. Nothing proved here bounds the
  condition after `, if `, so nothing excludes a `, then ` inside it.
- Dropping `hs` would need an english-lean lemma that no condition reading holds `, then `. The spec computed that
  english-lean has no such sentence, but did not prove it.

Also UNVERIFIED (traced by hand and by the self-reviewer, not mechanised): without `checkTemplates` the statement would
fail. The act `{0} then{1}` passes `canonicalAct`, and a definite " draft" in the free `sc` would read "Then draft." as
`one`. That is why the proof needs `slotsApart`.

## Seeded bugs and mutants (`mutants.json`)

Each was planted, shown failing, and restored. Lines are on the final HEAD.

1. **S1 (Lean, `preposed_eq` fixture):** `capitalise` lower-cases the first letter in `lean/VE/Commands/Steps.lean`.
   - `StepsProofs.lean:655` fails ("did not evaluate to `true`", on a copy without the `E_web` fixtures, which import
     StepsExamples).
   - `StepsExamples.lean:40` fails too.
2. **S2 (Lean, splitOn `#guard`):** the separator `", then "` is shortened to `", "` in the `#guard` at
   `lean/VE/Commands/SplitOnLemmas.lean:297`. Line 297 fails.
3. **S3 (Lean, the bridge):** `splitOnL` drops `sep.length - 1` characters at a cut
   (`lean/VE/Commands/SplitOnLemmas.lean:20`). The `#guard`s at 300 and 301 fail, and so do the proofs at 25 and 41.
4. **S4 (Python, `tools/layer_policy.py`):** the two modules are left out of layer 4.
   `python3 tools/check_lean_imports.py` exits 1 with "new outward Lean import: VE.Commands.StepsProofs ->
   VE.Commands.Steps". Restored, it exits 0.
5. **S5 (Lean, conservative):** in `lean/VE/Commands/Steps.lean:40`, `shapes` makes an `after` shape for a body that
   begins `C` instead of `Then `.
   - `readStep_core` fails at StepsProofs.lean:575 and `shapes_preposed` at :60 (`lake env lean` on a copy without
     fixtures).
   - StepsExamples.lean 43, 45, 50, 57, 58, 77, 163 and 185 fail.

## Trust, size, overlap

- Trust: `splitOnL` counts +11 trusted lines (unclassified). It is recorded under R16:
  reviews/dri-decisions-20261109-ci-3b.md item 2 and the FOLLOW-UPS.md row "## ci-3b" (class it P). The final
  `tools/trust_map.py --check` numbers are below.
- Size (`git diff --numstat $(git merge-base HEAD main)`, at 469f86398 plus this report):
  - SplitOnLemmas.lean 303 and StepsProofs.lean 672 (975 lines, of which 784 are proof lines). The count leaves out
    blank lines, comments, docstrings, `#guard`s, imports and opens. This is under the DRI's ~800 stop trigger.
  - Hand-written non-proof lines: lean/VE.lean 1, tools/layer_policy.py 3, this report and mutants.json.
  - SplitOnLemmas.lean was 287 lines after deliverable (1) (7116b078a).
- Overlap: lean/VE.lean (cmp-s3a-cfr-1, rights-cfr-4, sc-7, me-1) and tools/layer_policy.py (et-5, rights-cfr-4) are
  edited in flight elsewhere. Each change here is a one-line addition in its own place.
- Pilot bytes moved: 0 (proofs only).
