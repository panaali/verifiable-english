# Batch 16g build report: STOPPED at the precondition

DRI attention (first line, BUILDER-CHECKLIST 7): batch 16g did not start. Its precondition, a retained-path ledger
that after 16d–16f holds only genuinely invalid inputs, does not hold. Twelve valid documents in the 16c ledger, and
two live `usecases/` documents, are still decided by Python's retained loader. Deleting `ve/document.py`'s wrapper
code now would break them. The rows need a scheduled batch, or a DRI ruling that removes them from 16g's
precondition. No product code changed, and there is no DELTA row to sign.

## What was checked

On `109c7de1d` (main at the start, with lf-16f merged), after `lake build` (959 jobs) and `tools/rust_build.py`
(binary already pinned):

- `docs/lean-first/b16f/measure.py`, rerun unchanged over the 16c ledger's 130 rows that 16d and 16e did not take.
  Its `share.json` is byte-identical to 16f's saved one (`evidence/share.json`, `evidence/cases.json.gz`):
  0 problems in the batch groups, and `outside_valid_retained: 12`.
- `live_probe.py` over the live documents in the same classes (`evidence/live-probe.txt`).

## What is left on the retained path

| Class | Ledger cases | Lean's answer | Retained loader |
|-------|--------------|---------------|-----------------|
| `order@0` documents | 2: `seed/usecases/news-article/news-w6a.ve.md` and its `cc-20260929T0600Z` pilot copy | `CheckerUnavailable: document checks under order@0 need its Lean profile route` | accepts |
| soft norms with `readings@1` | 4 constitution pilots (`readings/s1.ve.md` of runs 20261003T0600Z, 20261004T0600Z, 20261004T1800Z, 20261008T0600Z) | `CheckerUnavailable: soft-norms with norm-defaults, readings, alternatives or risk needs its composed Lean route` | accepts |
| reading sets with a `null` reading content | 6 UDHR `translation.ve.md` pilots (runs 20260930T0600Z to 20261003T0600Z; five `rights@0`, one `readings@1`) | `CheckerUnavailable: front matter outside the document mode's JSON reader: null in reading_sets` | accepts |

The two live documents:

- `usecases/news-article/news-w6a.ve.md` (`order@0`): the same `CheckerUnavailable`; the retained loader accepts it.
- `usecases/udhr-pilot/run-20261010T1400Z/translation.ve.md` (`readings@1` with `norm-defaults@0`, newer than the
  16c ledger): Lean is never asked. `_document_case` (`ve/document.py:430-434`) returns None for readings whose
  contents are partly null under norm defaults, so Python decides the document on its own path. That gate is itself
  part of the Python wrapper code the batch was meant to delete.

What does qualify under the precondition (not blocking):

- Senses, 2 cases (`b_no_choice_made`, `f_two_words_one_default`): genuine invalid inputs. Lean refuses both, but the
  diagnostic comes from the retained loader (`CheckerUnavailable: a senses refusal carries the senses route's
  diagnostic, which this mode's row cannot hold`).
- Rights (16e), 53 cases: `ResourceLimit` on both paths with the same text (carve-out limits). These are UNKNOWN,
  not valid inputs that get dropped.

## Scope note for the batch that unblocks this

The senses refusals above, and every Lean path that answers `... keeps its loader's diagnostic`
(`lean/VE/Service/Document.lean:579, 614, 645, 703, 1082, 1141, 1517, 1644`), take their diagnostic text from the
Python loader. So even when the ledger holds only invalid inputs, deleting the loader down to file I/O and display
changes those diagnostics, unless Lean's rows can carry them first or a DELTA row (R2) records the change.

## Seeded bugs and tests

None. No product code changed, so there is no behaviour to seed and nothing to select. The committed files are this
report, its probe and its saved evidence. Selected tests (`mac-pytest.sh --select`, Mac runner, this tree with the
report uncommitted) ran 431 units with 0 failures. The chain's gate on this HEAD covers these documents only.

## Self-review against BUILDER-CHECKLIST

1. Every Lean answer typed and contained: N.A.: no relay changed.
2. Every deliverable built, no rule broken: N.A.: stopped at the precondition, as the task directs; the residue is listed above.
3. Tests and gates can fail: N.A.: no code changed. The measurement fails on a problem row (`measure.py` exits 1).
4. Python, Lean and Rust agree, valid inputs pass: N.A.: no change. The 12+2 valid retained documents are the stop reason.
5. R8 binding: N.A.
6. Gate evidence matches the final HEAD: PASS: measured on `109c7de1d`, the merge base. The commit adds only `docs/lean-first/b16g/`.
7. No unsigned item: PASS: no DELTA rows. The stop needs the DRI to schedule the residue, as named in the first line.
8. Every user-visible change in DELTA: N.A.: none.
9. Test selection: N.A.: no code changed.
10. Lean statements: N.A.
11. Budgets fail closed: N.A.
12. No CPU or memory regression: N.A.
13. Test-removed trailers: N.A.: no test removed.
