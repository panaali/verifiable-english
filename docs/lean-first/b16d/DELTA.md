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
- Seeded faults caught: 11/11. Clean gate: passed, 13662 passed, 92 skipped, 0 failed.
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

The review fix round (below) adds five more, each caught by its test in
`tests/test_b16d_norm_roles.py`: the role table refusing quoted norms (Lean),
and Lean's or Python's free document keeping a unit under an active reading
set or an attached unit. `seed_faults.py` now saves every planted fault with
a `caught` flag instead of stopping at the first survivor, and `report.py`
counts the caught ones, so the line above is no longer true by construction.

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

## Review fix round 1 (lf-16d-review.final.md B1, B2)

**The class.** Which norm units make the norm-defaults document was read in
three places that disagreed: Lean's document mode refused quoted norm units
with its own kind check (B1), and both Lean's completion check and Python's
coverage document took every norm unit, including a unit under an active
reading set and a unit attached to an open content-bearing set (B2). The old
path left those out (`selected_norms`) and checked quoted and held units as
single rules (`_check_quoted`).

**The fix.** A unit's norm role comes from one table,
`Norms.Admission.normRole`, which W1's own admission split (`splitUnit`) and
the document mode both read. `Service.Document.freeNorms` selects the free
document's rules: role in force, under no active set, and attached to no open
set. Attachment is `Readings.attached` on the readings route's own decoding of
the same document. Quoted and held units go through
`NormDefaults.Admission.checkQuoted`. Python's two load paths share one helper
each for the selection (`_free_norms`), the lowered environment
(`_defaults_environment`) and the reading plan (`_reading_plan`). That last
helper also fixes the C note on coupled plans over authored sets.
`tests/test_b16d_norm_roles.py` runs every kind constructor (atomic, and
attributed, hedged and causal over `norm` and `asserted` to depth 2) on norm
content, plus norm content under an open set (the reviewer's 15-gap case, and
a dangling precedence edge), an attached unit built on F-ND1 with recorded
situations, and invalid quoted or held rules. For each case Lean's document
mode must answer, and the report or diagnostic must equal the retained path's.

**Deltas.**
- Fault order, SIGNED by standing ruling R2 (DRI-RULINGS.md). The
  norm-defaults step now runs after the reading sets and the unit status
  check, in the old path's order. Within the step, the single-rule checks
  come first, then the free document, then `completions`. One corpus case
  changes: `document/mutant/15` now gives the old path's
  `distinguishing model id does not match model` instead of a TypeMismatch.
  The A/B therefore lists two fewer differences (`same` 99926, `order` 170).
- Trust budget: V +27 trusted lines (`Service/Document.lean` +20,
  `Norms/Admission.lean` +7). R6 does not cover this, because Python keeps its
  own selection to build the coverage document. The rebaseline in
  `docs/trust-baseline.json` history states this. It **needs a DRI
  signature**.
- `lean/checkers.lock`: the two `ve_service` pins this branch added were for
  the superseded 106e91e7 and 2bdbd8b5 sources (not a gate build path). Both
  are replaced by the one build of this round.

**Evidence and what was not run.** `measure.py` was rerun on the fixed code.
`cases.json.gz` and `share.json` came out byte-identical. The nine-corpus head
is the saved 16d head recording with `norm_defaults` and `document`
re-recorded on the fixed code. The machine's load average was about 48, so two
re-recordings each hit the Rust checker's 5 s wall limit on one bluedot-grant
row, a different row each time. Where the two runs differ, the non-timeout row
is used (both runs are of the same commit). `pilots` was not re-recorded: no
pilot has a quoted, held or attached norm unit. `scope.json` and `gate.json`
are still the 2bdbd8b5 capture. This round ran only the selected tests, its
new tests, `lake build` and `lean/audit.py`. The full gate on the final HEAD
belongs to the merge train.

**Not fixed here (review C notes, follow-up):** the generic reason over
error-to-error A/B changes (DRI review deferred); `"Expected a JSON object"`
copied into Lean; Python merging the gap and readings lines and re-adding
`residual_total`, which keeps a Python selection beside Lean's
(`_free_norms`, cross-checked by the differential and the seeded faults
above). Moving the norm-defaults coverage into Lean would delete it.
