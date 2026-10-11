# B16d and question-answering merge

The B16d Lean document mode now accepts four question-answering fixture documents that the question branch's
document-wrapper test formerly expected it to refuse: `udhr-part07.ve.md` and the `a-unspecified`, `a-rules`, and
`a-conflict` agent-policy documents. Their source identities, units, statuses, and wrapper coverage agree with the
retained Python loader. `group.ve.md` still needs the Lean surface parser, and `a-deny.ve.md` still needs the Lean
norms route; the mode reports `CheckerUnavailable` for those two documents.

The raw Lean `document` mode covers the wrapper, while `ve/document.py` adds norm-defaults gap evidence and
content-bearing readings findings to the public coverage report after the Lean answer. The original Python code
remains in `ve/document.py` and keeps its existing import-layer and inventory classification. The differential
wrapper compares the coverage fields owned by the raw mode; the B16d document tests compare the complete public
report. A follow-up can move these two report additions into the Lean document mode and then extend its response
schema and differential projection together.

The bounded differential fuzzer compares every question fixture as a seed and skips mutations of this large
vocabulary corpus, preserving the question branch's CPU budget. The wrapper tests check the four newly decided
seed answers against Python.
