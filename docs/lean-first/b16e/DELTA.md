# Lean-first batch 16e: rights@0 and readings@1 documents

This batch continues the document-mode work of [16c](../b16c/DELTA.md) and [16d](../b16d/DELTA.md). Its group is
the 1,250 rights cases of 16c's saved residue ledger: 1,000 rights documents and 250 under the `readings@1` head.
`report.py` renders the block below from `evidence/` only (decision D4: saved evidence, checked at the batch gate
and by the merge train; no live diff against a moving HEAD).

<!-- BEGIN GENERATED B16E METRICS -->
- Saved scope: `8cec935a..6f739fb0 --no-merges`, 11 commit(s).
- rights (16c ledger, 1250 cases): Lean decided 1197/1250 (955 accepted with the prior path's report, 242 rejected, 0 with an error differing from the prior path's); 53 retained invalid inputs (53 ResourceLimit).
- Nine-corpus A/B: 100348 records per side; 100337 the same; 0 unlisted differences (4 unavailable, 7 wording listed in delta.json).
- Seeded faults caught: 15/15, in docs/lean-first/b16e/measure.py, lean/VE/Service/Document.lean, ve/document.py, ve/rights.py, ve/softnorms.py.
<!-- END GENERATED B16E METRICS -->

## Document route and ownership

Python's `load_document` reads a `rights@0` document through `RightsDocument`, which relays the document's rights
source to the rights route before any unit is checked, then reads every formula and norm unit in the route's
extended environment `E″′`. `VE.Service.Document` now calls the same Lean routes in the same order, with no new
rights or soft semantics:

- `rightsDoc` decodes the rights source (every string unit id, then the content of each rights or `norm` unit, as
  `_rights_units` builds it) with the rights route's own decoder, `Rights.Wire.decodeRightsSource`, over the
  environment without the `readings@1` head. The names an `open` meaning may cite are the declared open terms, the
  rights-generated predicates (`genEntries`) and the soft decision predicates. Each rights source unit's status is
  the route's (`Rights.Run.unitOpen`, the `unit_open` of `rights-elaborate`).
- `rightsContentOf` is `_content` over it: a soft norm passes the soft route's single-rule check
  (`SoftNorms.Wire.decodeSoftNorm` under `_rule_source`, the `soft-rules` case) and is answered in its canonical form
  (`softCanonical`: the W1 core re-encoded, each soft field away from its default, an absent decider omitted); a
  rights block is answered as written. Each `meaning_id` is bound to the unit's content environment: the document's
  for a rights kind, `E″′` for any other (`nullableMeaningId`, which keeps the soft route's nullable decider slots).
- The unit kind is typed (`RowKind`: W2's kind, or `RightsKind`, the one table of rights source kinds).
- `soft-norms@0` is owned only beneath `rights@0` (`ownedBeneath`; a soft-norms document on its own is batch 16f's),
  and a `readings@1` document no longer needs `norm-defaults@0` to be decided.

What the mode leaves to the retained path, answering `CheckerUnavailable`: a rights document with reading sets,
couplings or a claim graph (`RightsDoc.unowned`: per-choice rights elaboration and the rights admission), a rights
environment the rights route rejects (its loader's diagnostic stands), formula or fenced content in a rights document
(typed in `E″′`, which the mode does not build), and rights with `norm-defaults@0`, alternatives or risk. A
`ResourceLimit` answer is the retained path's by `_lean_answer`'s contract; the 53 retained ledger cases are the
corpus's seeded carve-out limit faults, which both paths reject with the same `ResourceLimit` text.

Python builds the document from the accepted answer: the rights containers (`RightsDocument`) from the authored
source, as before, with the authored rights blocks themselves as the units' content (the binding found Lean's copy
equal to them; the renderer holds the source's lines by identity). The coverage lines of every composed profile (soft,
rights, content-bearing readings, norm defaults) come from one helper for both paths (`_profile_lines`).

## Response schema and binding

`document.json` types the new fields: the unit kind as W2's kind or a rights source kind, a rights block
(`rights_block`, with `rights_line`, `rights_condition`, `soft_norm`, `soft_exception`, `cites`) and a soft norm
(`soft_content`), both `copied` from the request. An optional member may be `null`, which the routes read as absent;
a required member never is, since the decoders refuse it absent. `ResponseShape.Encoders.Document.rowKind_fits` and
`unit_fits` prove every rendered row fits. `_bind_document_answer` binds each new field to the request: a rights
block must equal the authored block; a soft norm (`_soft_bound`) must have the authored members, name, predicate,
sign, `over`, soft fields and citations as written (its formulas are Lean's re-encoding); `_lean_document` binds
each `meaning_id` to its content and content environment. `tests/test_b16e_rights_document.py` retypes every leaf of
every unit of a genuine answer (schema or binding refuses each), forges typed values (binding refuses), and
re-binds meaning ids. The relay mutation gate has a rights document fixture; its transport accepts four valid-shape
mutants of copied content, which the binding refuses (allow entry B7, with its test).

## Measurements

`measure.py` takes the cases and source hashes from 16c's committed ledger and decides each case on both paths
(16e review F2): an accepted case's public report must equal the prior path's, a rejected one must be rejected
there too (a differing error is saved as `prior_error`; there are none), and a retained one must be a genuinely
invalid input (any error but `CheckerUnavailable`; a `ResourceLimit` only with Lean's own text).

The A/B recorded all nine corpora at the merge base `8cec935a` (a detached worktree with its own Lean build) and at
`9122d41f` (this branch; after it only `document.json`'s `soft_norm.mode` was re-expressed as one enum with `null`, which accepts the same values, so that `tests/test_enum_domains.py` keeps the field's domain). Rows a loaded machine's wall-clock guards decided
(load average 30 to 110) were re-recorded on both sides with one worker and the same `VE_RUST_TIMEOUT` (a guard, not
a work limit), and spliced in by key (`splice_recording.py`): two UDHR whole-translation pilots (both sides stop at
the recorder's 600 s) and four document-corpus rows that hit the Rust checker's 5 s guard on one side.
`make_ab.py` refuses any difference but the two listed kinds; `evidence/ab.json` holds both recordings' hashes.

Two further sweeps compared the paths beyond the corpora: every `check_document`/`render_document` call of eleven
document test files under a two-path harness (109 Lean-decided calls, among them plain `readings@1` documents and
companion readings in parts, all the same), and 1- and 2-fault mutants of rights documents on 18 seeds (17,642
Lean-decided mutants over the sweep's runs, nested lines, conditions and exceptions included; the last run of every
seed had no difference). The sweep found three crashes of the retained path on inputs the rights route reads and one
schema gap (a `null` citation, which the routes read as absent, refused as a malformed answer); each is fixed
(below). `tests/test_b16e_rights_document.py` keeps the sweep on three seeds.

## Deltas

| Delta | Ruling |
| --- | --- |
| Four pilots are `CheckerUnavailable` on both sides with identical outputs (two companion probes; two UDHR whole translations that stop at the recorder's 600 s). | SIGNED by standing ruling R7 (DRI-RULINGS.md) |
| Seven pilot outcomes name each recorder's temporary directory for the same missing sense pack. | Not a product delta (the recorder's paths) |
| A rights document unit whose `id` is a list or object: the retained path crashed with `TypeError` (`_in_rights_source` tested it against the attached ids); both paths now give the unit check's `duplicate or invalid unit id`, or the rights route's citation fault when the unit was cited. No accepted output changes. | NEEDS A DRI SIGNATURE (a raw crash replaced by a diagnostic; not covered by R1 to R15) |
| An outside soft norm with `"alterable": null`: the retained path answered `CheckerUnavailable` (its container failed on `tuple(None)`); both paths now read the null as absent, as the soft route does, and accept. `test_a_null_alterable_party_list_is_read_as_absent_on_both_paths`. | SIGNED by the DRI 2026-10-14 (reviews/lf-16e-dri-note-1130.md) |
| A right without a `guard`: the retained path answered `CheckerUnavailable` (its container read `body["guard"]`); both paths now read it as `top`, as the rights route does, and accept. `test_a_right_without_a_holder_guard_is_built_on_both_paths`. | SIGNED by the DRI 2026-10-14 (reviews/lf-16e-dri-note-1130.md) |
| Trust budget: V +269 trusted lines (`VE/Service/Document.lean` +185, `ResponseShape/Schemas/Document.lean` +84), measured against merge base `8cec935a` on the final tree by `tools/trust_map.py --since` (which reports the allowance as unsigned in its pre-ruling baseline); no K or S growth. F6's 25 new normalizer lines are D[R] and add no trusted V. | SIGNED by the DRI 2026-10-14 (reviews/lf-16e-dri-note-1130.md), conditional on these final per-file counts |
| F4: accepted rights documents with arbitrary JSON in a condition's ignored `purposes` metadata now receive the Lean document answer instead of `CheckerUnavailable`; the copied content remains request bound. `test_f4_copied_ignored_condition_metadata_accepts_every_json_type` covers every JSON type. | SIGNED by the DRI 2026-10-14 (reviews/lf-16e-dri-note-1130.md) |
| F5: `render_document` now renders accepted null citations and omitted or null condition and bar deciders, where it previously crashed. `test_f5_optional_rights_metadata_renders_after_acceptance` checks the rendered output on both document paths. | SIGNED by the DRI 2026-10-14 (reviews/lf-16e-dri-note-1130.md) |
| F6: a null member forbidden by the closed copied-rights schema now reaches the Lean rights decoder and is refused. The retained Python route validates the authored block with that same generated schema before its restricted wire removes optional nulls. `test_f6_closed_rights_content_rejects_forbidden_null_members` covers six nested objects and misleading field names. | Correctness fix; the DRI required rejection in reviews/lf-16e-dri-note-1130.md |

FOLLOW-UP (consolidation): remove the retained Python loader's rights and soft source parts after Lean owns reading sets, couplings, claim graphs and standalone `soft-norms@0` documents. This is the condition attached to the signed V +269 allowance.

No diagnostic text, fault order or accepted output of any corpus changed: the 242 rejected ledger cases give the
prior path's code and text, and the A/B has no `order`, `verdict`, `availability` or `wording` difference in a
product output.

## Seeded faults

`seed_faults.py` planted each fault, ran the named test of `tests/test_b16e_rights_document.py`, and restored the
source, the lock and the build (`evidence/mutants.json`, 15 of 15 caught). Lean (`VE/Service/Document.lean`): the
rights route's statuses ignored; norm meaning ids bound to the rights environment instead of `E″′`; a rights block
accepted under a `norm` unit; a rights document's claim graph decided; nulls in rights content refused;
`soft-norms@0` owned without `rights@0`. Python: a rights block and a soft norm left unbound to the request; meaning
ids bound to one environment for every kind; the composed profile lines dropped on the Lean path; the measurement
counting a rejected valid case, or accepting a report that differs from the prior path (`measure.py`); and each of
the three retained-path crashes restored (`ve/document.py`, `ve/softnorms.py`, `ve/rights.py`).

## Not run, and acceptance

The release gate (`tools/gate.py`) and the full suite were not run in this fix round, by its instructions: the merge
train's branch verify and the nightly full suite run after it. The saved gate records of the earlier round,
`evidence/gate-9801fe70.json` and `gate-full-9801fe70.json`, are of `9801fe70`, before this batch's code: they are
kept as history and are not this HEAD's gate. Latency was not measured reliably: at load average ~90 the median
`check_document` of 40 rights documents was 0.37 s on the Lean path and 0.30 s on the retained path, with tails above
10 s on both; no R4 claim is made. No differential fuzz across the Python, Lean and Rust parsers was run for this
route change (Rust has no document mode).

Acceptance: the route, schema, binding, measurement, A/B, sweeps and seeded faults are **AGENT** work, done. The
final-HEAD gate is **AGENT** work for the merge train. The DRI signatures above are **HUMAN** work, pending. There is
no **EXTERNAL** item.
