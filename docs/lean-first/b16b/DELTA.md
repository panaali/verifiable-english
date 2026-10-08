# Lean-first batch 16b: the document switch

<!-- The sections below are completed by the batch report; the retained table is read by
tests/test_document_lean_switch.py. -->

## Retained: what Python's own path still decides

`load_document` and `check_document` ask Lean's `document` mode first. Python's own loader (`_load_document`) runs
only when the mode answers `CheckerUnavailable` or `ResourceLimit`, or the text cannot be sent. Each row is one
reason the mode gives (its text in `lean/VE/Service/Document.lean`), with the batch whose Lean route must be
composed in the mode before Python's path for it can be deleted.

| Mode answer (`CheckerUnavailable: …` unless stated) | Documents | Owner of the missing Lean step |
|---|---|---|
| front matter outside the restricted JSON reader | `null`, negative, fractional or large numbers, duplicate keys, `NaN` in the front matter | wire primitive (rule 5): DRI decision whether such front matter is refused (an `availability` change) |
| a document with senses is read by the Lean senses route | `senses` metadata (RD-8) | senses route composed in the mode (16c) |
| a document over a ve.core@0 or ve.core@0.1 environment needs its legacy route | legacy envelopes | batch 12b |
| document checks under {profile} need its Lean profile route | `soft-norms@0`, `rights@0`, `reports@0`, `norm-defaults@0`, `readings@1`, `speech-acts@0`, `order@0`, closure and core profiles, quantities | the profile's route (batches 6, 7, 8, 10, 3/14, 11, 12b, 9) composed in the mode (16c) |
| the environment block {key} needs its Lean route's decoder | blocks other than `alternatives` and `risk` (`unit_schema`, `soft`, …) | batch 9 / 12b, composed in the mode (16c) |
| document checks on the {family} family need its Lean route | closure, n-ary and order families | batch 12b |
| regulated predicates need the Lean norms route | regulated predicates under `norms@0` without a block | batch 13b (norms route) |
| norm content needs the Lean norms route | norm units | batch 13b (norms route) |
| fenced English or strict content needs the Lean surface parser | `ve` fences | batch 13a/13b and English E2 |
| claim graph: UnsupportedProfile: … | graphs the admission route defers (definitions, citations) | batches 13b and 14a |
| a distinguishing model the Lean model decoder refuses | reading sets with such models | batch 12b |
| `ResourceLimit` (JSON depth over 256) | front matter nested deeper than the restricted reader's limit | batch 18 (one limits table) |
| (not sent) | a text that is not UTF-8 | 16c: the mode reads text only |
| a ve-document@2 document is admitted by the discourse route | never sent: `@2` documents go to the discourse route first | batch 4 (already Lean's) |
