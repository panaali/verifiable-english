# BlueDot draft as a VE use case

This is an **AUTHORING** exercise on our own text, not an edit to a grant
application. [`source.md`](source.md) is unchanged (SHA-256
`a9fa225acce6a684af7519c9c6fa82a20fc3a7e685a04b7e1a4bac88a0d6ed22`).
[`document.ve.md`](document.ve.md) embeds its exact 7,619 UTF-8 source bytes
after JSON front matter. The unit spans partition those bytes, including
punctuation and blank lines. [`natural-view.md`](natural-view.md) shows every
unit with its source wording and the audited natural VE rendering when checked.

## Coverage

| Status | Bytes | Units | Treatment |
|---|---:|---:|---|
| CHECKED | 780 | 12 | Valid VE formulas with one recorded author reading each; all 12 are admitted as graph leaves. |
| LABELLED | 3,513 | 50 | Headings, edit instructions, prior wording, plans, predictions, hopes, evaluations, and commentary retain their force. |
| OPEN | 2,081 | 22 | Clauses depend on one of five declared terms whose decision rules remain open. |
| UNFORMALISED | 1,245 | 9 | The feature needed to express the clause faithfully is named below. |
| **Total** | **7,619** | **93** | **100% span accounting**. |

The 12 checked source clauses give 11 distinct examples because the foundation
leaf clause occurs in both the proposed harms paragraph and its paste copy.
Their content is checked for syntax, types, a single chosen reading, and
admission. The author choices are in `reading_sets`, signed `grant-author`;
their `why` field states the scope of the choice. The graph proves only `true`
from those 12 leaves so that every checked reading appears in the admitted
report. It does not prove the draft's empirical or policy claims. The separate
premise consistency search currently reports `UNKNOWN`.

The open terms are `matched_cost`, `real_artefact`, `affordable_proof`,
`misleading_formalisation`, and `catastrophic_risk`. Each has a named decision
role and an unresolved question in the document metadata. Repeated mentions
remain OPEN until those criteria are supplied; the writer's ability to choose
a reading does not manufacture a measurement rule.

## Missing features

| Missing feature | Units | Why it remains unformalised |
|---|---:|---|
| `causal_evidence` | 8 | Claims that proof blocks a construction, controls test harms, or the project helps oversight need a causal or empirical evidence structure beyond a bare FOL atom. |
| `vague_comparison` | 1 | “Close to the current length” needs a stated baseline and tolerance. |

These counts are for UNFORMALISED units only. Numeric ranges and cost
comparisons inside OPEN units remain unresolved through their named terms;
they are not counted again as missing features.

## Ten before and after examples

The right column is the output of `render_natural_sentence`, not a free
paraphrase. Nine examples use its audited **explicit-form fallback** because
the current writable natural grammar rejects the longer domain phrases. A
quoted predicate identifier is therefore a visible readability gap. Example
10 is a notation-free natural sentence. Every right-hand sentence parses back
to exactly its recorded VE formula.

| Unit | Source sentence | Audited natural VE for checked clause(s) |
|---|---|---|
| `u036` | A proof label could increase false confidence: foundation leaves remain accepted without proof, and formalisation may misstate the task. | Every foundation leaf is classified as "accepted_without_proof". |
| `u048` | Mandatory proof prevents arbitrary false sub-claims from being accepted as new assumptions; the guarantee is conditional on the declared foundations. | Guarantee is classified as "conditional_on_foundations". |
| `u049` | It does not establish their truth or faithful formalisation | Both of the following hold: (a) it is not the case that "proof_rule" is classified as "establishes_foundation_truth"; (b) it is not the case that "proof_rule" is classified as "establishes_faithful_formalisation". |
| `u055` | The existing stability caveat concerns estimated leaves, not proved sub-claims | Both of the following hold: (a) caveat is classified as "concerns_estimated_leaves"; (b) it is not the case that caveat is classified as "concerns_proved_subclaims". |
| `u057` + `u058` | Evidence requirements do not guarantee evidence quality, and no VEX result or completed extension is claimed. | It is not the case that requirements is classified as "guarantees_evidence_quality". Both of the following hold: (a) it is not the case that draft is classified as "claims_vex_result"; (b) it is not the case that draft is classified as "claims_completed_extension". |
| `u059` | The existing evidence-layer milestones remain its development schedule | Milestones is classified as "schedules_development". |
| `u061` | The revised form text does not report new experimental results or assert a cost advantage | Both of the following hold: (a) it is not the case that draft is classified as "reports_new_result"; (b) it is not the case that draft is classified as "asserts_cost_advantage". |
| `u062` | Formalisation and proof production are included in the matched-cost comparison | Both comparison is classified as "includes_formalisation" and comparison is classified as "includes_proof_production". |
| `u065` | No budget or other field is revised | No field is revised. |
| `u066` | Character counts include spaces and punctuation but exclude labels and trailing newlines. | All of the following hold: (a) both counts is classified as "includes_spaces" and counts is classified as "includes_punctuation"; (b) both of the following hold: (i) it is not the case that counts is classified as "includes_labels"; (ii) it is not the case that counts is classified as "includes_trailing_newlines". |

The table folds the renderer's line breaks into spaces and omits source list
numbers. Where a source sentence has other clauses, only the checked clauses
appear on the right; their neighbors retain their own status in the document.
The complete exact
output is in [`natural-view.md`](natural-view.md); the test rechecks it.

## What writing a real proposal in VE teaches

The easy part is recording bounded facts about the draft, such as which
fields were revised. Even these require an author decision: “It” in `u049`
was resolved to the mandatory proof rule, and “no budget or other field” in
`u065` was read as no field revised. The checker validates the chosen formulas
and their use; it cannot certify that those choices match the author's intent.

Most proposal language has a different force. A milestone is an intention;
“could increase false confidence” is a possibility; “should help” is a hope;
and a budget or length judgement needs criteria. Treating any of these as a
proved present fact would make the application look more certain than it is.
The OLD and PASTE copies also need separate spans even when their words repeat.

An actual VE proposal would need richer, reviewable objects for dates, ranges,
comparative costs, evidence quality, causal study designs, and cited support.
It would also need a larger writable natural grammar: 11 of the 12 checked
clauses fall back to quoted identifiers. The exercise demonstrates full source
accounting and explicit limits, not full formalisation or proof of the grant's
predictions.

## Recheck

```sh
UV_CACHE_DIR=/tmp/uv-cache uv run python -m usecases.bluedot-grant.build_document
UV_CACHE_DIR=/tmp/uv-cache uv run python -m ve document check usecases/bluedot-grant/document.ve.md
UV_CACHE_DIR=/tmp/uv-cache uv run python -m pytest tests/test_bluedot_grant.py
UV_CACHE_DIR=/tmp/uv-cache uv run python -m pytest
```

The build script uses only local source bytes and checker APIs. It does not
invoke a model or change `source.md`.
