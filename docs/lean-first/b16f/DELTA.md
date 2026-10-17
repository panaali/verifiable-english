# Lean-first batch 16f: the document mode's remaining groups

This batch continues the document-mode work of [16c](../b16c/DELTA.md), [16d](../b16d/DELTA.md) and
[16e](../b16e/DELTA.md). Its groups are the 16c residue ledger's soft norms, norm content, senses, fenced content,
distinguishing models, and the malformed-profile and environment-key groups. `report.py` renders the block below from
`evidence/` only (decision D4: saved evidence, checked at the batch gate and by the merge train; no live diff against
a moving HEAD).

<!-- BEGIN GENERATED B16F METRICS -->
- Saved scope: `85b20fcb..38b93aaa --no-merges`, 12 commit(s).
- Batch 16f's groups (16c ledger, 118 cases): Lean decided 111/118 (43 accepted with the prior path's report, 68 rejected, 0 with an error differing from the prior path's); 7 retained invalid inputs.
- By group: distinguishing models 26 error; environment key 25 error; fenced content 9 error, 3 ok; malformed profile 8 error; norm content 18 ok; senses 7 retained; soft norms 22 ok.
- Outside the batch's groups: 12 cases, 12 of them valid documents still on the retained path.
- Nine-corpus A/B: 100394 records per side; 100379 the same; 0 unlisted differences (8 unavailable, 7 wording listed in delta.json).
- Seeded faults caught: 10/10 (6 Lean, 4 Python), in lean/VE/Service/Document.lean, ve/document.py.
- Relay mutation gate (document route): 3199 mutants, 3091 refused, 108 allowed, 0 failures. Differential fuzz (CI sample): 0 new differences, passed True.
- CPU, head over base, on 4 pilots: check and render ratios 1.0 to 1.35; the Lean document request at most 0.279 s.
<!-- END GENERATED B16F METRICS -->

## What Lean's `document` mode now decides, and how

Every step calls an existing Lean route, in the order Python's retained loader (`_load_document`) calls the same
route; no new semantics and no Python decision were added.

- **Plain `norms@0` norm content** (the norm-content group). `contentOf` decodes a norm object with the norms route's
  decoder (`Norms.Wire.decodeNorm`) and binds it to its `meaning_id`, as 16d does under `norm-defaults@0`.
  `checkNorms` runs `_check_quoted`'s check (`Norms.Admission.checkQuoted`) on each quoted norm and each norm under an
  active set, then `NormDocument(env, selected_norms)` (`Norms.Wire.decodeSource`, data flags admitted as
  `NormDocument` reads none). A claim graph with a norm construct is admitted on the norms route
  (`Norms.Run.runAdmission`, Python's `_uses_norms`). The gate "regulated predicates need the Lean norms route" is gone.
  Norm content beside an alternatives or risk block keeps the retained path.
- **A `soft-norms@0` document without `rights@0`** (the soft-norms group; 16e owned the profile only beneath
  `rights@0`). `softSource` is `check_soft_source`, before the environment: the soft route's decoding of the
  environment and the soft source's norm objects, and its document hash. `softLayer` builds `E″`, the soft route's `E′`
  (`SoftNorms.Wire.primeJson`), as an environment of the mode (`extendedEnv`), its decision predicates (which an
  `open` meaning may cite) and `_rule_source(E″)` (`softRules`, shared with the rights document). Every formula, fence
  and reading set is read in `E″` (an English fence as the soft route's generated frame, the English case's
  `generated`). Each norm object is checked alone (`SoftNorms.Wire.decodeSoftNorm`), answered in canonical form
  (`softCanonical`) and bound to `E″` (`nullableMeaningId`). The claim graph is admitted on the soft route
  (`SoftNorms.Run.runAdmission`). Soft norms with `norm-defaults@0`, `readings@1`, an alternatives or a risk block keep
  the retained path.
- **An environment the mode composes no route for** (the malformed-profile and environment-key groups). Where the mode
  answered `CheckerUnavailable` for an unowned profile, an unknown environment key, a units block or norm defaults with
  a block, it now asks the `environment` mode (`Standalone.reportedEnvironment`, Python's `Environment` through
  `validated_environment`) and answers that mode's fault when it rejects without a JSON `path` (`environmentFault`).
  Under `soft-norms@0` or `rights@0` Python's loader runs those routes first, so the mode does not consult it there.
- **A distinguishing model the route decoder refuses** (the distinguishing-models group). The first set in order
  with a refused model is re-read with the `model` mode (`Standalone.reportedModel`, Python's `validated_model`). A
  JSON object here has no authored order, so the model mode's diagnostic is the answer only when exactly one model of
  that set is refused or misnamed (`locatedModel`), with its JSON `path` into that model. A `null` inside a model
  reaches the model mode as written on both paths.
- **A strict fence's syntax error** (the fenced-content group). The first strict fence the `check` mode's parser
  refuses is read as Python reads it (the `parse` mode over the fence as written) and answered with that mode's text
  and span (`locatedFence`). A strict fence over a statement layer's environment (a soft document's `E″`) keeps the
  retained path, since Python's `parse` reads those itself (`_lean_parse_scope`).

What keeps the retained path (`CheckerUnavailable`), and why:

- **Senses (7 ledger cases).** Each document names a sense pack file that does not exist. Python reads the file
  (`Cannot read sense pack: [Errno 2] No such file or directory: '<directory>/pack.json'`); Lean's `document` mode
  receives no file. These are genuinely invalid inputs (a missing file), so they are listed with that cause.
- **A rejection whose answer this mode's error row cannot carry.** The soft relay adds the `diagnose` mode's
  diagnostic, or the soft route's contract code (`SOFT_*`), to a soft source's, a soft rule's or a soft claim graph's
  rejection.
- **A plain norm fault.** The norms route words a malformed norm object's faults, and classes some, otherwise than
  the retained loader's `NormDocument`: `invalid indexed formula` against `AST nodes must be nonempty tagged JSON
  arrays`, `fields do not match: ...` against `Incorrect fields (missing=[...], unknown=[...])`, a raw name against
  Python's `repr`, `UnknownSymbol` against `InvalidInput`. The differential fuzzer found the first three on the new
  `norms-content` seed. The mode answers `CheckerUnavailable` naming the route's text (follow-up below).
- **A `readings@1` document whose readings carry their own vocabulary**, without `norm-defaults@0`: Python relays it
  to the readings components route (`load_components`), which this mode does not compose.

Twelve ledger cases fall in no batch's groups (pilots under `order@0`, `readings@1` or `rights@0`). They are measured
and saved with `"outside": true`; all twelve are valid documents that stay on the retained path (`order@0`; soft
norms with `readings@1`; a rights document with reading sets and a `null` reading content). They need a batch the DRI
schedules.

## Response schema and binding

`document.json`'s rejection rows are now three typed variants (`ResponseShape.Schemas.Document`): `plain_error`
(id, text), `model_error` (id, text, a non-empty `path`) and `fence_error` (id, text, a `span` of four naturals).
`ResponseShape.Encoders.Document.locatedRow_fits` proves every located row fits; `runCaseReported_fits` covers the
new branch. A soft-norms unit uses 16e's typed `soft_content`.

The receiver binds each new field to the request (R8):

- a `path` must name a member of a distinguishing model the document supplies, every token an object key or an
  in-range decimal index (`_names_a_model_member`);
- a `span` must lie in the text of a strict fence of the document, with that text's line and column
  (`_spans_a_strict_fence`, the relation `x-source-span` binds for the `parse` mode);
- a soft norm unit must equal the rule as the soft rule container holds the authored one (`_soft_bound`): a dropped
  soft member, or a changed guard or carve-out, is refused. This also tightens 16e's rights binding, which allowed a
  subset of the members and skipped the formulas;
- every soft unit's `meaning_id` is bound to `E″` (`soft_document.extended_env`).

`tests/test_b16f_document.py` retypes every leaf of every unit of a genuine soft and norms answer (the schema or the
binding refuses each), refuses empty, extra, duplicated and missing unit rows, forges each soft member and rebinds
each meaning id, and refuses shifted, absent and out-of-range paths and spans. The relay mutation gate has soft,
norms, model-error and fence-error document fixtures; its by-design entries B8 and B9 name what the transport accepts
and the document binding refuses, each with its test.

## Deltas and their rulings

| Row | Delta | Ruling |
|-----|-------|--------|
| 1 | Who decides: the 111 decided cases of the groups, and every corpus document of these kinds, are now Lean's. The public outcome is unchanged: the measurement compares each with the prior path (0 differing), and the nine-corpus A/B lists no difference from it. | No user-visible delta: none needed |
| 2 | A/B: 8 records unavailable on both sides with identical outputs (7 companion probes, `ReadingsConstruction ... KeyError`, and one pilot both sides stop at the recorder's 600 s limit). | SIGNED by standing ruling R7 (DRI-RULINGS.md); `delta.json` `unavailable` |
| 3 | A/B: 7 wording pairs, the same missing sense pack named under each recorder's own temporary directory. A recording artefact, not a product delta. | none needed; `delta.json` `wording` |
| 4 | A located row's new `path` or `span` member in the document answer (the information Python's retained path already raised, now carried by Lean's row). | SIGNED by standing ruling R3 (DRI-RULINGS.md): added, nothing removed; the fields equal the owning mode's (`test_a_refused_distinguishing_model_is_lean_s_located_diagnostic`, `test_a_strict_fence_s_syntax_error_has_the_parse_mode_s_span`) and are bound to the request (`test_a_model_path_is_bound_...`, `test_a_fence_span_is_bound_...`) |
| 5 | Fault order, one sentence per rule, each Python's loader's: a `soft-norms@0` document's soft source is checked before its environment's language and keys; where the mode composes no route, the environment mode's fault comes before every later check; a distinguishing model's fault is reported at its set's model step; a strict fence's at its unit. | SIGNED by standing ruling R2 (DRI-RULINGS.md): deterministic and documented here; `test_an_environment_fault_is_the_environment_mode_s`, `test_a_soft_or_rights_environment_keeps_its_route_s_order` |
| 6 | Trust budget: untied V +142 over 85b20fcb, by file: `lean/VE/Service/Document.lean` +139, `lean/ResponseShape/Schemas/Document.lean` +3; K +0, S +0. New Lean-owned behaviour; each new trusted definition is exercised by a test that can fail (the seeded faults below); the ties pass is a FOLLOW-UPS.md row. Recorded in `docs/trust-baseline.json`. | SIGNED by standing ruling R16 (DRI-RULINGS.md), re-measured with `tools/trust_map.py` on the final code commit |
| 7 | CPU: the head's check and render on four pilots, over the base, are 1.0 to 1.35 times (`evidence/cpu.json`). Lean's document request is at most 0.279 s: within 1 s Lean CPU and 2 s wall per document check. The largest share of the added render time is the client's schema check of the 1,100-unit answer (0.20 s of 0.69 s, profiled), which R8 requires. | SIGNED by standing ruling R4 (DRI-RULINGS.md) for the absolute budgets. The render ratio on the two largest constitution pilots (1.34 and 1.35, +0.14 s and +0.24 s) is a pilot slowdown R4 excludes: DRI acknowledgement needed |

## Follow-ups

- The norms route's texts for a plain norm object's faults, and their classes, are not the retained loader's
  (`NormDocument`); once Lean's texts are made Python's, or the DRI accepts Lean's, those faults can be decided and the
  Python checks deleted.
- The twelve outside cases above, and senses documents whose pack exists (the senses route's composition), need a
  scheduled batch.
- R16's ties pass for the new trusted lines (FOLLOW-UPS.md).
- 16e's rights path answers a rejected soft rule with Lean's class code where Python's relay raises the soft route's
  contract code (`decode_rule`); the same reason made this batch's soft path fail closed. No corpus case shows it.

## Seeded faults

`seed_faults.py` planted each fault, ran the named test (which failed), and restored the source; for a Lean fault the
build was pinned for the run. `evidence/mutants.json` keeps each fault's file, test and failure excerpt:

- Lean (`lean/VE/Service/Document.lean`): a norm object outside the soft source accepted without the soft route's check;
  quoted norms not checked by the norms route; a soft document's formulas read in its own environment instead of
  `E″`; a refused model decided when its set has two; the environment mode's fault taken before a soft source's check;
  a strict fence's syntax error left to the retained path.
- Python (`ve/document.py`): a model path not bound to a model member; a fence span's line not bound; a soft rule bound
  as a subset of the authored one; a soft document's meaning ids bound to the document's environment.

Two further Lean checks of the new encoder theorem: a located row with a renamed `span` key, and one with a `BOGUS`
status, each broke `ResponseShape.Encoders.Document` at `locatedRow_fits` (unsolved goals); both were restored.

## What was not run

The full release gate is the chain's, on the committed final HEAD. Latency was measured only on the four pilots in
`evidence/cpu.json`. The retained Python loader is not deleted: it still decides the listed residues and the fail-closed
classes above.

Acceptance classification: the routes, binding, measurement, A/B, fault injection and saved evidence are **AGENT**
work, done here. The DRI's acknowledgement of row 7's pilot render ratio, and its scheduling of the outside cases, are
**HUMAN** work, deferred to the DRI. There is no **EXTERNAL** item.
