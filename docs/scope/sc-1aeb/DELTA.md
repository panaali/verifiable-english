# User-visible deltas (sc-1aeb)

| Item | Change | Ruling |
|---|---|---|
| Approved statement of spec 5.1 | `govern_provenance` is built with spec 5.1's text (`docs/spec/scope.md:1075`) plus one hypothesis, `(hw : JsonWF D.doc)`, written as sc-1ae wrote it for the other four and using sc-1ae's `JsonWF` (`lean/VE/Scope/Govern.lean`); every other token is exact (`docs/scope/sc-1aeb/statement-diff.txt`). | SIGNED by the DRI 2026-10-27 (reviews/dri-decisions-20261027-featureplan-gates.md item 2). Condition tests: F-raw's four `#guard`s stay unchanged in `lean/VE/Scope/Examples.lean` (lines 738 (items 1 and 2), 743 (item 3) and 748 (item 4)) as the reason for the hypothesis; the parser lemma is sc-1af, so SC-1b's statements may not take `JsonWF` as a hypothesis until it is proved. |

No other delta:

- **No answer or refusal changes.** No definition that computes an answer is edited: the diff adds theorems to
  `Theorems.lean`, two fixture functions and `#guard`s to `Examples.lean`, docs and generated inventories.
- **No trust growth.** `uv run python tools/trust_map.py --check`: "K +0, S +0, D +0, G +0, tied +0, unclassified +0,
  trusted +0"; the two fixture functions are class T in `tools/trust-classes.json`.
