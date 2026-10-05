# English in Lean, S2: integration (record)

Status: record of branch `english-lean-s2/integrate`, 2026-10-05. It merges `english-lean-s2/py` (S2.0, S2.5:
`manage-agents/codex-english-lean-s2-py.final.md`, `c7d69739`) and `english-lean-s2/lean` (S2.1 to S2.3:
[english-lean-s2-lean.md](english-lean-s2-lean.md), `ee11a6fe`) on `ve-integration` `629709ec`, builds S2.4, and
closes the open items of both reports that concern admission: the real Lean call, admission end to end, and
three-way conformance on the spec fixtures. S2.6 (the G2 harness) is not in it.

## 1. The merge

The one conflict of substance was the fixed table. The Lean branch had written `Fixed/RelationalFol.lean` as
88 `FixedRow` literals (typed `FixedAct` per row, record L3) by an uncommitted script; the Python branch's
generator wrote 98 untyped `Rule` literals with the action as a row index. Resolved per the spec:

- **One generated file.** `tools/english_grammar_gen.py` now writes the Lean branch's format: `relationalFolRows
  : Array FixedRow` with each row's `FixedAct` and its data, plus `ntNames`, `ranks`, `relationalFolActs` (the
  4.4 act texts) and `relationalFolSha256`. `Catalogue.lean` keeps `ntTy`, the index constants, `FixedAct` and
  `FixedRow`; `Rules.lean` checks the index constants and `ntTy` against the generated names (`#guard`). The
  contract "fixed rule `k` has `act := k`" holds through `fixedRules`. A table row may not name an action of
  2.12's proposed rules (`orAdjectives`, `impliesAnd`), which `FixedAct` lacks.
- **98 rows, not 88** (spec section 17). Python's grammar has the eight ordinals `first` to `eighth`, and D15
  makes the table mirror it; the Lean branch's 88 rows are exactly the generated rows without the ten ordinal
  rows of `declaration` and `term`, in the same order. Recomputed: 127 rules for `F`/`LF`, `|G|` = 504, steps
  7,736 / 13,837 / 2,659 (`ReadExamples.lean`); no verdict, formula, statement or code changed.
- **The lock.** The S2 reader modules (`Catalogue`, `Rules`, `Actions`, `Encode`, `Read`) and the service
  (`Run`) are trusted files of `ve/english_grammar/LOCK.json`; `Extends` and `ReadExamples` are listed as
  untrusted with reasons. `actions_version` is 3 (5 after the review fixes of section 6).

## 2. S2.4: `ve_english_route`

`lean/EnglishMain.lean` and `VE.EnglishGrammar.Run` (layer 4), a one-shot runner as the adapter's transport
expects (`{"id", "status": "ok", "result"}` rows; a case it cannot read is an `error` row).

| Mode | Request | Answer |
|---|---|---|
| `english.read` | environment, overlay (optional), lexicon (`ve.english-lexicon@1`, naming the environment), source, mode, cap | base 4.3 with the six identities of base 2.12 computed from the case; `derivation`/`witnesses` as rule tags in pre-order with token spans (spec 4.3); codes and texts of base 4.2 and spec 3.2 |
| `english.grammar` | environment, overlay (optional), lexicon | spec 4.4: identities (all but `source_sha256`), nonterminal names, ranks, every rule with index, tag, sides (`kwMid` included) and act text |

Choices: `read` gets the empty `Overlay`, the overlay being applied by `Env.decode` (record L11); authoring reads at
cap 2 only; `environment_id` is the typing service's (`Standalone.environmentCase`); `canonical` is not in Lean's
answer, the adapter renders Lean's formulas with Python's printer (one owner, as the Lean report recommended); the
status codes of `none`, `many`, `budget`, `invalidGrammar` are `NoDerivation`, `Ambiguous`, `Budget`,
`InvalidGrammar`, and the adapter checks them; in translation mode a set that is not complete with fewer than two
readings is `budget`, never `none` or `one`. The grammar is computed per case (no cache: one-shot).

## 3. Admission and conformance

| Item | Evidence |
|---|---|
| the adapter reads the real reader | `ve/backends/english_lean.py`: no `canonical` from Lean, status-code check, the tree form of 4.3 checked node by node; `tests/test_english_lean_adapter.py` (fake answers, 70+ mutants) |
| admission end to end | `tests/test_english_lean_route.py`: `parse_english_with_metadata` under `english.admission=shadow` (every record `classes == []`, Lean answered); `english.admission=lean` and `=rust-experimental` are refused (`test_admission_refuses_to_make_the_reader_the_authority`; review A2, DRI ruling 6) |
| fixtures, Python and two Lean readers | the 89 literal fixtures of `ReadExamples.lean` under `F`, `FC`, `F3`, `FD`, `F51`, `F52`, `F53`, `Fapi`: Python's dispatched unit and `english.read` agree under 2.11 on all 89 (46 accepted, 43 rejected); the W7 reader gives Python's formulas on the 14 it reads (`test_three_way_conformance_on_the_spec_fixtures`). The third reader is W7's Lean reader, not Rust: there is no Rust English reader. The comparison reads Python's selected lexicon, which equals the fixture lexicon for `F`, `FC`, `F3`, `FD`, `Fapi` (`test_python_selects_the_fixture_lexicon`) but not for `F51` to `F53`: there the `#guard` outcomes of e51 to e53 (`illTyped`, `relativeForm`) are Lean-only evidence |
| spacing | every spacing change at every token boundary of every fixture (whitespace before the first item and after the last; at each boundary removed, widened, or added) gives one outcome under 2.11 (`test_spacing_mutants_of_every_fixture_get_one_outcome`); the texts of F1 are `BadSpacing` in Lean, `badSpacing` in the reference lexer, `SyntaxError` in Python (`test_spacing_rejections_agree`) |
| identities | i1, i2, i3, i4 (a stated `lexicon_id` is an unknown field; an answer for another lexicon fails closed), i6, and every sampled fixture answer equals the adapter's identities |
| render, then read | Python's renderings of seeded formulas over the six base-profile vocabularies read back as exactly their formulas (240 in the test; a one-off run of 5,000 over ten vocabularies, four use cases included, had no difference) |
| text variants | no-break space, double space, tab, CR LF, curly quotes, Kelvin sign, dotted capital I, a control character and a space before the period agree on every fixture of `F` |
| malformed requests | every node of a genuine request replaced by 7, true, [], {} or a 300-deep array gives an `ok` or `error` row; a `null` is a framing error (exit 2, no rows), which the adapter reads as `CheckerUnavailable` |
| export | the 4.4 export of `F` holds the source's rows with their act texts and the lexical rows with theirs |

## 4. Findings

- **F1 (closed; DRI ruling 1, reviews A1 and B2).** Lean's lexer (base 2.2: whitespace was ignored) read texts
  Python refuses with `SyntaxError`: a space or tab before the terminator (`Legacy is deployed .`), a word glued
  after it (`Legacy is deployed.It is reviewed.`), whitespace before the first sentence, and a quoted name glued
  to a word (`relation"owner_of"to`). The class: every spacing Python's patterns fix and the token stream did
  not carry. The lexer now checks one spacing table (`Lexer.lean` `spacing`, mirrored as `SPACING` in
  `conformance/english_lean_lexer.py`) when each item starts: no whitespace before the first item or before a
  terminator, whitespace after a terminator unless the text ends, whitespace between two tokens of the word
  kinds; punctuation stays with the `glued` flags and the rules. A breach is the new `Reject.badSpacing`
  (`BadSpacing`, Python class `SyntaxError`). V3 now lexes a wording with each hole as a word of its own
  (`wordingTokens`, the substitution the lexical rules read; review C2), since holes as spaces would breach
  the table, and so a wording such as `{0}s are {1}` fails V3 instead of passing it and giving no rule.
- **F3 (open; DRI).** A validation-order difference, both sides rejecting: at 64 negations Python's hand parser
  applies the nesting limit (`ResourceLimit`) while it reads, before a word or spacing it would refuse later;
  Lean lexes the whole text and reads the words before it counts the depth (`NoDerivation` or `BadSpacing`).
  Listed in `order_difference` of `tests/test_english_lean_route.py`; no other difference is allowed there.
- **F2 (spec text, applied).** The 88 rows of spec 2.5: section 17.

## 5. Not done

| Item | Owner |
|---|---|
| S2.6: the G2 harness (sealed corpus, reverse corpus, mutation replay, the 57,765-text three-way, the BlueDot and `lake build` budgets) | Python implementer |
| g1: the nearest-wording suggestion quotes whole tokens | adapter, with the authority flip |
| `LeanService` transport and t4 (service mode against the one-shot executable): `english.read` is one-shot only | Lean implementer |
| the grammar-instantiation diagnostic of base 4.4 (the first failing rule by tag and condition): `invalidGrammar` carries the fault and, for `lexicon`, the first failure only | Lean implementer |
| a binding of `english.read` in the assurance manifest: `english.admission` keeps `authority: python`, so the mode stays planned | with the authority flip |
| DRI rulings: Q2 (the four codes), Q5 (`kwMid`), Q6 (V3), record L5 and L14, F3, and `Run.lean` as a trusted file of the lock | DRI |

## 6. Review fixes

Reviews `manage-agents/english-lean-s2-review-astra.final.md` and `manage-agents/reviews/english-lean-s2-review-fable.md`.

| Finding | Fix | Regression tests |
|---|---|---|
| A1 (Astra), B2 (Fable): spacing widens acceptance | F1 above: the spacing table, `badSpacing`, V3 through `wordingTokens`; `actions_version` 5 | `test_spacing_mutants_of_every_fixture_get_one_outcome`, `test_spacing_rejections_agree`, `test_text_variants_…[space before the period]`, lexer fixtures x18 to x22 (`Examples.lean`, `lexer.json`), the `glue` and `lead-space` lexicon mutants (`LexiconFixtures.lean`) |
| A2 (Astra): `english.admission=lean` replaced Python's admission | `dispatch.SHADOW_ONLY` and `dispatch.shadowed`: a shadow-only operation returns Python's result under every selection, records under `shadow`, and refuses `lean` and `rust-experimental` with `CheckerUnavailable`; `execute` refuses it, so no sibling caller can route it | `test_no_named_override_makes_the_english_reader_the_authority`, `test_a_lying_reader_never_changes_the_admitted_document` (shadow and pins), `test_execute_refuses_a_shadow_only_operation`, `test_admission_refuses_to_make_the_reader_the_authority`; the adapter's fail-closed tests now call Lean's leg directly |
| B1 (Fable): `Actions.lean` `actionsVersion := "1"` | the definition names `Fixed.actionsVersion`, the one generated constant; `actions_version` 4 | `test_actions_version_has_one_literal_and_it_is_generated` |
| C1, C2, C4 (Fable) | C1: the fixtures row of section 3; C2: with F1; C4: the comment went with A2 | as above |
