# Lean-first batch 16d: norm-defaults documents

This batch continues the document-mode work in [16c](../b16c/DELTA.md). The
measurement selects the norm-defaults residues from 16c's saved ledger. The
scope, per-case decisions, nine-corpus comparison, fault injections, and gate
result are stored in `evidence/`; `tests/test_b16d_evidence.py` checks those
saved files without consulting a moving `HEAD` or a live diff. `report.py`
renders the following block from them.

<!-- BEGIN GENERATED B16D METRICS -->
- Saved scope: `c24aeab2..2bdbd8b5 --no-merges`, 4 commit(s): `2bdbd8b5`, `106e91e7`, `2c03afc1`, `6d01a3f4`.
- norm-defaults: Lean decided 1010/1010; 0 saved invalid-input residues.
- document-corpus: Lean decided 786/904; 118 saved invalid-input residues.
- pilots: Lean decided 339/339; 0 saved invalid-input residues.
- Nine-corpus A/B: 100301 records per side; 0 unlisted differences.
- Seeded faults caught: 6/6. Clean gate: passed, 13662 passed, 92 skipped, 0 failed.
<!-- END GENERATED B16D METRICS -->

## Document route and ownership

`VE.Service.Document` calls the existing Lean norm-defaults environment,
content, completion-validation, and graph-admission routes, then computes the
wrapper's coverage in its existing Lean function. It also calls the readings
validation and English or strict surface routes for the document's content.
`VE.Discourse.Loader` validates pending reading metadata, including optional
labels, before the document route accepts a pending set. The document service
returns the checked norm node and its meaning identity. The response schema
gives the norm node a closed, typed shape. No new norm or reading semantics
were added to Rust.

Python sends an English lexicon proposal when an English fence requires it,
checks the typed answer against the exact request, then constructs the public
document and its existing reading-plan display. The answer binding checks
source bytes, document and meaning identities, the full ordered unit list,
each authored id, span, kind, meaning, support, parent, content, and every
coverage count. An empty or extra unit row is refused. Python's retained
loader remains for routes outside this batch and for the saved invalid inputs
that Lean marks unavailable. Lean owns acceptance and checked content on the
new route; the receiver only checks binding and builds the public object from
the accepted answer.

## Measurements and review boundary

`measure.py` takes the exact cases and source hashes from 16c's committed
residue ledger. A retained case has its Lean unavailability cause and the
prior path's invalid-input error in `cases.json.gz`. The measurement aborts if
a previously valid case is retained. `make_ab.py` compares complete recordings
of all nine registered corpora and writes each difference into `delta.json`.
It rejects any changed accepted output. The listed document and norm-defaults
differences are between two errors on invalid input; the pilot wording entries
name the recorder's different temporary directories for the same missing
sense pack. The recordings' hashes are in `evidence/ab.json`.

`test_every_norm_field_is_typed_and_every_row_bound` retypes every nested
field of a genuine norm answer and rebinds any mutation that passes the
schema. It also checks empty and extra unit rows and bool/string/negative
coverage counts. `seed_faults.py` planted and removed these faults, each of
which made its named test fail (see `evidence/mutants.json`):

- accept forged norm content with a matching forged meaning identity;
- omit the English fence lexicon proposal;
- omit norm-defaults coverage;
- skip pending-reading model validation;
- erase authored reading couplings from the displayed plan;
- refuse pending-reading labels.

The saved gate includes the full Lean build and audit, Rust build and tests,
schema and wire checks, and the complete selected Python suite. The approved
readings/defaults statement comparison passed; no theorem statement changed.
The refreshed trust baseline records the added document wrapper and response
shape lines without any growth in Lean's `K` or `S` classes. Its history names
the deferred DRI review explicitly; it does not claim a DRI signature.
The initial fresh-worktree gate needed the ignored Lean build and offline
Cargo registry cache seeded before its checks could run. The passing capture
uses the committed source and a clean tracked worktree. The final HEAD gate is
run separately after this report is committed.

Acceptance classification: the route, binding, corpus comparison, fault
injection, saved evidence, and gate are **AGENT** work. Review of changed
invalid-input diagnostics is **HUMAN**, deferred to the DRI. There is no
**EXTERNAL** acceptance item in this batch. Other 16c residues and deletion
of the retained Python loader are outside this batch. Differential fuzz across
all parsers, latency measurement, and unrelated state-machine tests were not
run for this route change.
