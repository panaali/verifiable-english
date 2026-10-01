# BlueDot grant draft, authored in VE

This measures translation of our own grant draft after merging the 2026-09-30
feature work. The source is unchanged: [`source.md`](source.md) has SHA-256
`a9fa225acce6a684af7519c9c6fa82a20fc3a7e685a04b7e1a4bac88a0d6ed22`
and 7,619 UTF-8 bytes. [`document.ve.md`](document.ve.md) partitions every
source byte into the same 93 units as the 2026-09-27 baseline. The source is
copied byte for byte after its JSON front matter. [`natural-view.md`](natural-view.md)
lists each source span and its checked rendering.

## Before and after coverage

| Status | 2026-09-27 bytes | 2026-09-27 units | Now bytes | Now units |
|---|---:|---:|---:|---:|
| CHECKED | 780 (10.2%) | 12 | 6,709 (88.1%) | 67 |
| LABELLED | 3,513 (46.1%) | 50 | 853 (11.2%) | 25 |
| OPEN | 2,081 (27.3%) | 22 | 0 (0%) | 0 |
| UNFORMALISED | 1,245 (16.3%) | 9 | 57 (0.7%) | 1 |
| **Total** | **7,619** | **93** | **7,619** | **93** |

`ve document coverage` reports 100% byte accounting and no residual open
terms. Its remaining 23 assumption lines are author readings, not evidence that
the underlying empirical and causal claims are true. `ve document check` reports
premise consistency `UNKNOWN` under its bounded search. The prior document's
tautological graph was removed: the five definitions are checked as definitions,
and this version does not claim a proof of the whole proposal.

## Author choices for the five former open terms

[`author_choices.py`](author_choices.py) contains the signed `grant-author`
rule, a short reason, and an executable record classifier for each term. The
VE environment also defines each term as the conjunction of its required
evidence flags. No record of a real trial or event is supplied as true.

| Term | Operational decision rule |
|---|---|
| `matched_cost` | Same task and preregistered budget record; log authoring, formalisation, proof, compute, and review for both arms; totals differ by at most 5% of the larger total. |
| `real_artefact` | Record a provenance SHA-256 and creation and selection dates; the independent task predates selection, and evaluators did not seed a flaw. |
| `affordable_proof` | A complete certificate passes the checker and both full cost and elapsed time meet budgets registered before the claim. |
| `misleading_formalisation` | Pin source and formula hashes, identify an answer-changing counterexample, and obtain two distinct blind reproductions. |
| `catastrophic_risk` | Record a pathway and its evidence to human extinction or at least one million projected deaths. Possibility of that pathway needs a separate risk judgment. |

The thresholds are author choices for this exercise; the checker does not
infer that any real case satisfies them. Boundary tests show what each rule
accepts and rejects. These rules replace the previous unresolved metadata,
including occurrences in OLD wording, NEW wording, PASTE copies, and notes.

## What the merged features unlocked

The byte partition stays in one relational document. Some statement profiles
cannot be combined in a single VE environment, so
[`feature-readings.json`](feature-readings.json) holds source-linked readings
checked by their separate feature APIs. Its entries retain the source unit IDs
and source SHA-256. The main document's recursive `kind` records causal,
attributed, hedged and instructional force; source propositions in those units
are typed but do not become unqualified empirical premises.

| Merged feature | Newly checked source units | Treatment |
|---|---|---|
| Causation | `u026 u030 u031 u040 u041 u047 u052 u060 u064 u084 u091 u092` | Causal kind, including the update's stated motivation. It records the proposed relation, without proving a causal effect. |
| Attribution and reported speech | `u003 u007 u009 u012 u013 u014 u015 u017 u024 u032 u039 u042 u056 u060 u074 u076 u078 u090 u093` | OLD text is quoted, and future work is an applicant intention. `u003 u007 u060 u074` also pass the reports layer without promoting the inner claim to truth. |
| Speech acts and commands | `u018 u019 u020 u021 u067 u079 u080 u081 u082` | All nine edit instructions are active `require` commands on the separate speech act route. The OLD `u015` instruction stays quoted. |
| Risk possibility and severity | `u029 u035 u037 u086 u088` | The “could/may” harms round-trip as “might lead to.” The severity class is explicitly `unassessed`; no harm magnitude is invented. |
| Units and time | `u012 u017 u078` | A separate annotated date statement checks 2026-10-25 as the intended deadline, using the dated draft context for the year. It does not assert release occurred. |
| Soft norms | none | The only “should,” `u033`, predicts that open research material will help others. It names no obligated actor or regulated action, so it remains a labelled hope. `u039` and `u090` describe an intended VEX requirement, not an active norm. |
| Discourse and pronouns | none on the discourse route | The author resolves “It” in `u049` to the proof rule and “their” to the foundations in its typed reading. The merged discourse route rejects this compound source sentence as outside its supported fragment; the binding remains an author choice. |

The table describes features used in a unit, so `u060` appears in both causal
and attribution rows. The 67 CHECKED units also include bounded statements
about the draft, the named decision criteria, and copied source metadata.
The checked renderings are audited parser round trips; some use the explicit
form when the writable natural grammar has no faithful phrasing.

## Remaining limits

| Missing capability | Source units | Coverage treatment |
|---|---:|---|
| Baseline and tolerance for “close to the current length” | 1 (`u069`) | UNFORMALISED, 57 bytes. The source does not give a baseline or tolerance. |
| Discourse validation of the compound pronoun sentence | 1 (`u049`) | The author reading is CHECKED as a relational formula; its pronoun binding is not independently admitted by `ve.discourse@1`. |

Headings, OLD/NEW/PASTE labels, the predictive hope `u033`, and the subjective
credit judgment `u053` remain LABELLED. A CHECKED status validates a chosen
formal reading and its typing. It does not establish the draft's experimental
predictions, cited provenance, risk reduction, or causal mechanism.

## Recheck

```sh
UV_CACHE_DIR=/tmp/uv-cache uv run python -m usecases.bluedot-grant.build_document
UV_CACHE_DIR=/tmp/uv-cache uv run python -m usecases.bluedot-grant.feature_readings
UV_CACHE_DIR=/tmp/uv-cache uv run python -m ve document check usecases/bluedot-grant/document.ve.md
UV_CACHE_DIR=/tmp/uv-cache uv run python -m ve document coverage usecases/bluedot-grant/document.ve.md
PATH="$HOME/.elan/bin:$PATH" lake build  # in lean/
UV_CACHE_DIR=/tmp/uv-cache uv run python lean/audit.py
UV_CACHE_DIR=/tmp/uv-cache uv run python -m pytest
```

The two generators use only local source bytes and checker APIs. They make no
model calls and do not modify `source.md`.

Verification on this worktree: `lake build` completed 488 jobs;
`lean/audit.py` passed its 249-file, 2,437-declaration audit; the focused
BlueDot test passed 4 tests. The full suite passed **4,886 tests, 10 skipped**
with `VE_NATIVE_PREBUILT=1`, `VE_LEAN_PREBUILT=1`, and
`VE_RUST_SHA256=04470aa2a3a7c14367f4040d1da37e2b356ad0c07f82a0b9731f0b34049261f4`,
the SHA-256 of the Rust binary built from this checkout. The first full-suite
run without that override had 134 Rust authority failures: `main` pins
`7d74b350…` in `lean/checkers.lock`, which differs from this local build.
Those 134 tests passed with the local SHA override before the successful full
rerun. No Rust source or trust lock was changed for this use case.
