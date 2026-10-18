# Lean-first batch 16f: the document mode's remaining groups

This batch continues the document-mode work of [16c](../b16c/DELTA.md), [16d](../b16d/DELTA.md) and
[16e](../b16e/DELTA.md). Its groups are the 16c residue ledger's soft norms, norm content, senses, fenced content,
distinguishing models, and the malformed-profile and environment-key groups. `report.py` renders the block below from
`evidence/` only (decision D4: saved evidence, checked at the batch gate and by the merge train; no live diff against
a moving HEAD).

<!-- BEGIN GENERATED B16F METRICS -->
- Saved scope: `85b20fcb..f343e11e --no-merges`, 23 commit(s).
- Batch 16f's groups (16c ledger, 118 cases): Lean decided 116/118 (47 accepted with the prior path's report, 69 rejected, 0 with an error differing from the prior path's); 2 retained invalid inputs.
- By group: distinguishing models 26 error; environment key 25 error; fenced content 9 error, 3 ok; malformed profile 8 error; norm content 18 ok; senses 1 error, 4 ok, 2 retained; soft norms 22 ok.
- Outside the batch's groups: 12 cases, 12 of them valid documents still on the retained path.
- Nine-corpus A/B: 100394 records per side; 100386 the same; 0 unlisted differences (8 unavailable listed in delta.json).
- Seeded faults caught: 22/22 (10 Lean, 12 Python), in lean/VE/Service/Document.lean, tools/lean_first_diff.py, tools/relay_mutation_gate.py, ve/document.py.
- Relay mutation gate (document route): 3661 mutants, 3659 refused, 2 allowed, 0 failures. Differential fuzz (CI sample): 0 new differences, passed True.
- CPU, head over base, on 4 pilots: check and render ratios 0.97 to 1.27; the Lean document request at most 0.253 s.
<!-- END GENERATED B16F METRICS -->

## What Lean's `document` mode now decides, and how

Every step calls an existing Lean route, in the order Python's retained loader (`_load_document`) calls the same
route; no new semantics and no Python decision were added. The review fixes (`lf-16f-review.final.md`) are F1 (a
soft-norms document's fault order), F2 (the senses group, and the recorders that wrote a pilot without its pack) and
F3 (the pilot render ratio: speedups, the rest for the DRI).

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
- **A document with `senses`** (the senses group; review F2). After the units, `sensesLayer` runs `read_senses` in
  `load_document`'s order: the profile gate, `_parts`' faults (the English fences are listed first), the shape of
  `senses`, `own`, then the senses route itself (`Senses.Run.readCase`, the `senses.read` case Python's relay sends:
  the environment, the lexicon proposal, the pack texts, the own senses, the work budget, the English fences in
  unit order with their ids, the reading-set units and the defaults). Every unit is read in the route's projected
  environment (`sensesContentOf`: a fence's formula, or none for a preamble line or an open unit). The pack files
  are Python's to read: the request carries their texts (`packs`, `senses_document.pack_texts`). All seven ledger
  documents are over a frozen `ve.core@0` envelope, which the mode reads only under `senses`, with the frozen
  decoder and identities (`frozenEnv`, `Env.version`, `Env.meaningId`, `Loader.sourceIdOf`). Every other reader of
  the split (the Ask mode) still refuses a senses document.
- **A strict fence's syntax error** (the fenced-content group). The first strict fence the `check` mode's parser
  refuses is read as Python reads it (the `parse` mode over the fence as written) and answered with that mode's text
  and span (`locatedFence`). A strict fence over a statement layer's environment (a soft document's `E″`) keeps the
  retained path, since Python's `parse` reads those itself (`_lean_parse_scope`).

What keeps the retained path (`CheckerUnavailable`), and why:

- **A senses refusal whose answer carries the route's diagnostic object** (2 of the 7 senses ledger cases, both
  genuinely invalid: an unresolved word, `{"unit", "code": "Unresolved"}`, and a sentence with no reading, the
  refused reading): this mode's error row holds no such object. So does a senses document whose request carries no
  pack texts (a pack file Python cannot read: the loader reports it in its own order), or one beside norms, a
  block, a claim graph or reading sets over a frozen envelope. The build's measurement wrote each senses pilot
  alone, without the `pack.json` beside it, and listed all seven as a missing file (review F2); every recorder now
  writes a pilot with the files it names (`lean_first_diff.write_pilot`).
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

A `ve.core@0` document without `senses` keeps the retained path, as before (no corpus case).

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

- a senses document's units are read in the senses route's projected environment, so their `meaning_id` is bound
  there; and each English fence's content is bound to the senses route's reading Python holds (`_lean_document`
  reads it before the binding, `_bind_document_answer`'s `senses`): a fence the route read to a formula has exactly
  that formula, a fence it read as a preamble line or an open unit has no content, and every other unit's content
  is required as before (looprecheck1 F7: a dropped fence content with its `meaning_id` was accepted);

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
each meaning id, and refuses shifted, absent and out-of-range paths and spans. `tests/test_b16f_senses_document.py`
puts every relay-gate mutant of two genuine senses answers, and every pair of a unit's members dropped together,
through `_lean_document`: each is refused or shows what the genuine answer shows. The relay mutation gate has soft,
norms, senses, model-error and fence-error document fixtures and reads a `document` answer as `ve document` does
(`SERVICE_READERS["document"]`: the transport, then `_lean_document` with the pack files beside the document), so the
document entries the binding already refused (B0, B7, B8 and the F5, F6, F10 and F11 paths) are gone from the
allow-list; only B9 remains, a located row without its location.

## Deltas and their rulings

| Row | Delta | Ruling |
|-----|-------|--------|
| 1 | Who decides: the 116 decided cases of the groups (111 at the build, and 5 senses documents since review F2), and every corpus document of these kinds, are now Lean's. The public outcome is unchanged: the measurement compares each with the prior path (0 differing), and the nine-corpus A/B lists no difference from it. | No user-visible delta: none needed |
| 2 | A/B: 8 records unavailable on both sides with identical outputs (7 companion probes, `ReadingsConstruction ... KeyError`, and one pilot both sides stop at the recorder's 600 s limit). | SIGNED by standing ruling R7 (DRI-RULINGS.md); `delta.json` `unavailable` |
| 3 | A/B wording: none. The build's 7 pairs (a missing sense pack under each recorder's own temporary directory) were the recorder writing each senses pilot alone (review F2); it now writes them with their pack, and the base's seven were re-recorded so (`ab-recorded.json`). | No delta: none needed; `delta.json` `wording` is empty |
| 4 | A located row's new `path` or `span` member in the document answer (the information Python's retained path already raised, now carried by Lean's row). | SIGNED by standing ruling R3 (DRI-RULINGS.md): added, nothing removed; the fields equal the owning mode's (`test_a_refused_distinguishing_model_is_lean_s_located_diagnostic`, `test_a_strict_fence_s_syntax_error_has_the_parse_mode_s_span`) and are bound to the request (`test_a_model_path_is_bound_...`, `test_a_fence_span_is_bound_...`) |
| 5 | Fault order, one sentence per rule, each Python's loader's: a `soft-norms@0` document's soft source is checked before its environment's language and keys; a `soft-norms@0` document's `_parts` fault (a later unit's `MIXED` structure) is reported at that unit, after every earlier unit's fault, and an invalid `MIXED` id as `invalid MIXED unit id` before the first unit (`partsPrefix`, review F1: the build reported both before the unit loop); a senses document's faults come after its units, in the order `_parts`' faults, the shape of `senses`, `own`, the senses route; where the mode composes no route, the environment mode's fault comes before every later check; a distinguishing model's fault is reported at its set's model step; a strict fence's at its unit. | SIGNED by standing ruling R2 (DRI-RULINGS.md): deterministic and documented here; `test_an_environment_fault_is_the_environment_mode_s`, `test_a_soft_or_rights_environment_keeps_its_route_s_order`, `test_a_later_unit_s_structural_fault_comes_after_an_earlier_unit_s_fault` (every earlier fault by every structural fault, five seeds), `test_every_senses_fault_has_the_retained_path_s_public_outcome` |
| 6 | Trust budget: untied V +273 over 85b20fcb, by file: `lean/VE/Service/Document.lean` +265, `lean/VE/Discourse/Loader.lean` +5, `lean/ResponseShape/Schemas/Document.lean` +3; K +0, S +0 (`tools/trust_map.py --check` on the final code commit). The build's +142 (Document.lean +139, its schema +3) is recorded in `docs/trust-baseline.json`. The review fixes add +131: the senses route's composition (review F2: `sensesLayer` G[V], `SensesLayer`, `sensesContentOf`, `frozenEnv` D[V], and the grown `check`, `environmentOf`, `formulaCheck`, `sourceUnit`, `unitsOf`, `split`, `documentCase`) and the F3 speedups (`typedFormula`, `Loader.cutsBytes` D[V]); the identity helpers (`Env.version`, `Env.meaningId`, `Loader.sourceIdOf`) are D[I] and F1's `partsPrefix`, `yieldedParts` G[R], none trusted. Each new trusted definition is exercised by a test that can fail (the seeded faults below); the ties pass is a FOLLOW-UPS.md row. | R16 signs the build's +142 (`docs/trust-baseline.json`). The +131: SIGNED by the DRI 2026-10-17 (dri-decisions-20261017b.md #1), recorded with `tools/trust_map.py --allow` in `docs/trust-baseline.json`; condition: the ties pass (FOLLOW-UPS.md, ties-lf-16f) cuts it back by 2026-10-24 |
| 7 | CPU: the head's check and render on four pilots, over the base, are 0.97 to 1.27 times (`evidence/cpu.json`, 7 repeats, load about 8). Lean's document request is at most 0.253 s: within 1 s Lean CPU and 2 s wall per document check. The review's F3 speedups took the two constitution pilots' render from 1.34 and 1.35 to 1.27 and 1.22 (+0.19 s and +0.09 s): a unit's UTF-8 span check no longer encodes the whole source for every unit, a formula is typed against the route vocabulary decoded once, and the soft document is built once. The rest is the request itself on a 1,100-unit document: about 0.12 s in the mode (the front matter's parse and passes, the document identity's canonical JSON and SHA-256), the rest the shared transport (the frozen JSON reader and the digests of a 360 KB case) and the client's schema check, which R8 requires; SHA-256 and canonical JSON are in the hash-frozen `VE/CertificateWire.lean`. | R4 covers the absolute budgets, which hold. The render ratio on the two constitution pilots (1.27 and 1.22): SIGNED by the DRI 2026-10-17 (dri-decisions-20261017b.md #1) |
| 8 | Who decides, the senses group (review F2): Lean decides 5 of the 7 senses ledger documents (4 accepted with the prior path's report, 1 rejected with its text); the other 2 keep the retained path with their genuine diagnostics. The public outcome is unchanged: the measurement compares each with the prior path (0 differing) and the A/B lists no difference. | No user-visible delta: none needed |
| 9 | Trust ties pass for row 6 (infra item ties-lf-16f, 2026-10-18). Re-measured on main `2d4b93206` against the batch's base `85b20fcba`: the +273 is 29 declarations that grew (+288) and 3 that shrank (-15): Document.lean +265, Loader.lean +5, Schemas/Document.lean +3. The build's +142 is 21 grown and the 3 shrunk; the review fixes' +131 is 13 grown (5 of them grew in both). No theorem of `lean/statements.txt` names any of them, so `tools/trust_map.py` can accept no tie, and none is added: the ties remove 0 of the +131 and 0 of the +273. Untied V stays 40,244; the per-file counts, the list of declarations with the theorem that would tie each, and the seeded ties are in "Trust ties pass" below. | R16 (DRI-RULINGS.md): this is the ties pass R16 asks for; it changes no line, class, allowance or signature (`tools/trust-classes.json` and `docs/trust-baseline.json` unchanged). `python3 tools/trust_map.py --check` PASS before and after; seeded ties S1–S4 below each make it exit 1, and S1 and S2b fail `tests/test_trust_ratchet.py::test_committed_budget_passes_its_check` |

## Follow-ups

- The norms route's texts for a plain norm object's faults, and their classes, are not the retained loader's
  (`NormDocument`); once Lean's texts are made Python's, or the DRI accepts Lean's, those faults can be decided and the
  Python checks deleted.
- The twelve outside cases above need a scheduled batch.
- A senses refusal carries the route's diagnostic object (`{"unit", "code"}` or the refused reading), which a typed
  error row of its own could carry; then the two retained senses documents are decided too. A `ve.core@0` document
  without `senses` keeps the retained path (no corpus case).
- R16's ties pass for the new trusted lines (FOLLOW-UPS.md): run as infra item ties-lf-16f (row 9, "Trust ties pass"
  below). It found no existing theorem to tie any of the lines; the theorems that would are listed there.
- 16e's rights path answers a rejected soft rule with Lean's class code where Python's relay raises the soft route's
  contract code (`decode_rule`); the same reason made this batch's soft path fail closed. No corpus case shows it.

## Trust ties pass (row 9; infra item ties-lf-16f, 2026-10-18)

Method. `tools/trust_map.py`'s classifying pass (`walk`) was run on main with the batch merged (`2d4b93206`), on the
batch's base (`85b20fcba`) and on the build's last commit before the review fixes (`29949afef`), and every trusted
declaration (untied D[V] or G[V]) of the three files the batch grew was compared one by one between the trees. For each
declaration that grew, every theorem of `lean/statements.txt` was searched for one whose `-- uses` line names it (the
tool's own test of a tie, `classify`): none does, for any of the 29. Every Lean file of the tree was also searched for a
theorem that names one of them. The only one is `ResponseShape.Encoders.Document.runCaseReported_fits`, an encoder
theorem: it is not in the dump (the dump reads `lean/VE/Audit.lean` only, seeded tie S3), and its statement (`Fits`)
fixes the answer's form, not its meaning. There is no `VE.Service.runMode_document` equation, and
`VE.Service.Document.decodeRowKind_json`, the file's one dumped theorem, names only `decodeRowKind`, `RowKind` and
`RowKind.json`, which the batch did not grow. So nothing is tied, and `tools/trust-classes.json` is unchanged.

`split` and `documentCase`, which row 6 lists, were edited in place: their lines did not change (20 and 11), so
they hold none of the +273.

### Per-file counts (untied V lines, `trust_map.py`; base = `85b20fcba`, before = `2d4b93206` (main with the batch merged), after = the same tree, since nothing is tied)

| File | V base | V before | The batch's V | V after | Ties | The batch's V after the ties |
| --- | --- | --- | --- | --- | --- | --- |
| `VE/Service/Document.lean` | 901 | 1,166 | +265 | 1,166 | 0 | +265 |
| `VE/Discourse/Loader.lean` | 625 | 630 | +5 | 630 | 0 | +5 |
| `ResponseShape/Schemas/Document.lean` | 177 | 180 | +3 | 180 | 0 | +3 |
| **All files** | **39,941** | **40,244** | **+273** | **40,244** | **0** | **+273** |

All files: +303 between the two trees = this batch's +273 and +30 from items merged between them
(`VE/EnglishGrammar/Policy.lean` +15, `VE/Norms/Family.lean` +12, `ResponseShape/Schemas/Rights.lean` +6,
`VE/Core/Layers.lean` +1, `VE/Rights/Scope.lean` -4). K stays 997. S is 10,138 at the base and 10,152 on main; the +14 is
`VE/Closure/Order.lean`, not this batch. Tied lines stay 263 and the trusted total 51,393. `trust_map.py --check` passes
before and after, against `109c7de1d` (the merge base) and the allowances introduced since. Of the +131 that the DRI
signed on condition of this pass (dri-decisions-20261017b.md #1), the ties remove 0, and 0 of the whole +273.

### Declarations no existing theorem ties

Lines are untied V lines: base -> now, and in brackets how many came from the build (B, `85b20fcba..29949afef`) and
how many from the review fixes (F, `29949afef..2d4b93206`). The last column is a proposal. None of these theorems is
written or checked in Lean here: the task allows ties to existing theorems only, and no trusted code was added to make
up for one. Each would need a tree anchor on its `-- uses` line (a K, S or untied [V] declaration other than the one
it ties).

| File | Declaration | Lines | Why no existing theorem ties it | A theorem that would |
| --- | --- | --- | --- | --- |
| `VE/Service/Document.lean` | `sensesLayer` (G[V]) | 0 -> 64 (F 64) | No theorem names it. The senses route's theorems (`VE.Senses.readDocument_ok` and the like) are about `Senses.readDocument`, not the request this function builds or the answer it reads back | A senses wire theorem: `sensesLayer E front raw fences lexicon packs = .ok N` implies `Senses.Run.readCase` answered the request built from the English fences in unit order (their ids, the pack texts, `own`, the work budget, the reading-set units, the defaults) with a reading of status `one` or `open`; `N.projected` is `extendedEnv` (or `frozenEnv`) of that reading's `environment`; and `N.formulas` pairs each fence id with the `formula` of the unit the reading maps the fence to |
| `VE/Service/Document.lean` | `softContentOf` | 0 -> 24 (B 24) | No theorem names it | `softContentOf L … kind content = .ok (.soft c, mid)` for `content = {"norm": v}` implies that `SoftNorms.Wire.decodeSoftNorm se (wireJson 257 content) = .ok N` for `L.rules = some se`, with `c = softCanonical N v` and `mid = nullableMeaningId L.extended.profiles L.extended.envId c`. Every other content's answer is `contentOf L.extended …`'s |
| `VE/Service/Document.lean` | `check` | 56 -> 72 (B 11, F 5) | No theorem names it. `ResponseShape.Encoders.Document.document_fits` names `documentCase` and fixes form only (outside the dump) | A runner-level wire theorem per group (as rd-9's list proposes for its runners): `check text … = .ok c` implies that each unit row is `sourceUnit`'s answer under the layer the environment selects (`softLayer`'s `E″` under `Env.soft`, `sensesLayer`'s projection under `senses`, `rightsDoc` under `rights@0`). It also implies that a claim graph passed `admitGraph`, so that the route's admission soundness (`VE.SoftNorms.Run.runAdmission_sound`, `VE.Norms.Run.runAdmission_sound`) applies to it |
| `VE/Service/Document.lean` | `softSource` (G[V]) | 0 -> 14 (B 14) | No theorem names it | `softSource env ns = .ok src` implies `SoftNorms.Wire.decodeSoftSource (wireJson 257 env) (the wire form of ns) = .ok src` and that the soft document hash of the same pair is defined. Its error branch only maps to `CheckerUnavailable` |
| `VE/Service/Document.lean` | `extendedEnv` | 0 -> 13 (B 13) | No theorem names it | `extendedEnv j = .ok E` implies `Standalone.validated j (typing := true) = .ok E.checked` with the first-order family, `Route.Run.decodeRouteVocabulary E.checked.envelope = .ok E.rv`, `Route.Gate.profilesOf j = .ok E.profiles`, and `Standalone.environmentIdOf E.profiles j = .ok E.envId`. These are the identities every soft or senses unit's `meaning_id` is bound to |
| `VE/Service/Document.lean` | `frozenEnv` | 0 -> 13 (F 13) | No theorem names it | `frozenEnv j = .ok E` implies `Standalone.decodeLegacy j = .ok l` with `l` a `.v0` envelope, `E.legacy = some l`, `E.profiles = l.profiles` and `Standalone.legacyEnvironmentId l j = .ok E.envId` |
| `VE/Service/Document.lean` | `sensesContentOf` | 0 -> 11 (F 11) | No theorem names it | An English fence the senses route read to `ast` answers `formulaOf N.projected ast`'s formula and id; one it read as a preamble line or an open unit answers none; any other content answers `contentOf N.projected …`'s |
| `VE/Service/Document.lean` | `environmentOf` | 31 -> 41 (B 7, F 3) | No theorem names it. `environmentOf` in `VE/WireContract/Hooks/Norms.lean` is another declaration | A gate theorem: `environmentOf env units senses = .ok E` implies either that `Standalone.isLegacy env`, `senses` and `E` is `frozenEnv env`'s, or that every listed profile is in `ownedProfiles` and `E` is `decodedEnvironment env (blockOf (listedProfiles env))`'s. Under `soft-norms@0` without `rights@0`, with `units` an array, it also implies `softSource env (softSourceNorms units)` succeeded |
| `VE/Service/Document.lean` | `contentOf` | 55 -> 65 (B 10) | No theorem names it. `contentOf` in `VE/Discourse/WellFormed.lean` is another declaration | The norm branch the batch added: for a `{"norm": …}` content under `norm-defaults@0`, or under `norms@0` without a block, an answer `(.norm node, mid)` has `Norms.Wire.decodeNorm content = .ok node` and `mid = Route.Wire.meaningId E.profiles E.envId (Alternatives.Wire.encodeNode node)` |
| `VE/Service/Document.lean` | `admitGraph` | 67 -> 77 (B 10) | No theorem names it | `admitGraph E … = .ok ()` with `E.block = .none` implies that the route the environment selects answered the document it built: under `Env.soft`, `SoftNorms.Run.runAdmission "admission" (wireJson 257 E.lower) (wireJson 257 document) = .ok a`; under `usesNorms` (without `norm-defaults@0`), `Norms.Run.runAdmission`'s. Each route's `runAdmission_sound` then gives the meaning |
| `VE/Service/Document.lean` | `softRules` (G[V]) | 0 -> 10 (B 10) | No theorem names it | `softRules x flat = .ok none` exactly when no unit of `flat` holds norm content, and `.ok (some se)` implies `se` is the `se` of `SoftNorms.Wire.decodeSoftSource` of `x` with every `soft__` predicate removed (`_rule_source`) and no norms |
| `VE/Service/Document.lean` | `softSourceNorms` | 0 -> 10 (B 10) | No theorem names it | Through `softSource`'s theorem above: the soft source the mode checks is `decodeSoftSource` of the environment and of exactly the contents of the top-level `norm` units that hold `norm`, in order (Python's `_soft_contents`) |
| `VE/Service/Document.lean` | `SoftLayer` | 0 -> 9 (B 9) | A structure: its fields appear only as types; a structure's own text cannot tie it | The `softLayer` theorem below, which names its fields |
| `VE/Service/Document.lean` | `softLayer` (G[V]) | 0 -> 9 (B 9) | No theorem names it | `softLayer E d raw = .ok L` implies a `src` with `softSource E.lower (softSourceNorms (Json.arr raw.toArray)) = .ok src` and `SoftNorms.Wire.primeJson src.D (wireJson 257 E.lower) = .ok p`, such that `extendedEnv p = .ok L.extended`, `L.openNames = d ++ SoftNorms.decisionNames src.D` and `softRules p (partsPrefix raw) = .ok L.rules` |
| `VE/Service/Document.lean` | `SensesLayer` | 0 -> 7 (F 7) | A structure, as above | The `sensesLayer` theorem above |
| `VE/Service/Document.lean` | `Env.regulates` | 0 -> 7 (B 7) | No theorem names it | With `usesNorms` below: an equation with the norms route's own dispatch test `Norms.Run.usesNormsPath` (Python's `_uses_norms`) on the admission request `admitGraph` sends under `norms@0` |
| `VE/Service/Document.lean` | `typedFormula` | 0 -> 7 (F 7) | No theorem names it | An equation with the `check` mode's decoder: for an `E` with `E.checked.envelope.family = .fol` and `Route.Run.decodeRouteVocabulary E.checked.envelope = .ok E.rv` (what `decodedEnvironment` and `extendedEnv` build), `(typedFormula E ast).isOk = (Standalone.decodeTyped E.checked ast true).isOk`. The docstring claims this (the F3 speedup decodes the vocabulary once), and it should hold, since `Route.Run.decodeRouteVocabulary` is defined as `Route.Typed.routeVocabulary`; no theorem states it |
| `VE/Service/Document.lean` | `Env` | 11 -> 17 (B 3, F 3) | A structure, as above (the fields `generated` and `legacy`) | The `extendedEnv`, `frozenEnv` and `sensesLayer` theorems above, which fix both fields |
| `VE/Service/Document.lean` | `formulaCheck` | 7 -> 13 (F 6) | No theorem names it | `formulaCheck E ast = .ok ()` implies `Standalone.legacyTyped E.json ast true` succeeds when `E.legacy` is some envelope, and `typedFormula E ast` succeeds otherwise |
| `VE/Service/Document.lean` | `unitsOf` | 27 -> 33 (B 1, F 5) | No theorem names it | A partition theorem: `unitsOf … source … raw = .ok us` implies that the spans of `us`, in order, start at 0, each start where the previous one ends, end at `source.utf8ByteSize`, and cut no UTF-8 character (`Loader.cutsBytes source.toUTF8 a b = false`). It also implies that each unit is `sourceUnit`'s answer for its JSON |
| `VE/Service/Document.lean` | `runCaseReported` (G[V]) | 2 -> 8 (B 6) | Only `ResponseShape.Encoders.Document.runCaseReported_fits` names it: outside the dump, and form only | A located-row theorem: when `documentCase j` fails and `locatedOf j message = some (text, at_)`, a row's `path` is the `path` of `Standalone.reportedModel`'s row for the one refused model, with that row's `error`, and a row's `span` is the span `Standalone.parseRejection` gives for the first refused strict fence (the owning modes' answers, row 4) |
| `VE/Service/Document.lean` | `sourceUnit` | 49 -> 53 (B 2, F 2) | No theorem names it | Part of the `unitsOf` theorem: a unit's `content` and `meaningId` are the answer of the content function its layer selects (`rightsContentOf`, `softContentOf`, `sensesContentOf` or `contentOf`), and a stated `meaning_id` equals it |
| `VE/Service/Document.lean` | `Env.soft`, `usesNorms` | 0 -> 3 each (B 3 each) | No theorem names them | `usesNorms`: the `usesNormsPath` equation above. `Env.soft` is a two-profile test (`soft-norms@0` without `rights@0`). Only the routing theorems above (`admitGraph`, `check`) give it meaning; an equation with its own definition would be vacuous |
| `VE/Service/Document.lean` | `readingSetHasStrayNull` (G[V]) | 14 -> 16 (B 2) | No theorem names it | Its only reader is `strayNull` (D[R]), so it can only refuse (a stray `null` keeps the retained path). That makes it a classification question for the DRI ([R]), not a tie |
| `VE/Discourse/Loader.lean` | `cutsBytes` | 0 -> 4 (F 4) | No theorem names it. `cutsCharacter` is defined from it, so an equation with it would move the trust to the less direct side | None the tool can take: its meaning is Lean core's `String.fromUTF8?`, and core is outside the tree. The `unitsOf` partition theorem above states what the mode relies on |
| `VE/Discourse/Loader.lean` | `documentMetadata` | 3 -> 4 (F 1, the `senses` key) | A key list; no theorem names it | None: it is a table whose value is the statement. The loader tests check its agreement with Python's `_split` |
| `ResponseShape/Schemas/Document.lean` | `row` (+2), `file` (+1) (G[V]) | 15 -> 17, 10 -> 11 (B 3) | Response shapes: no dumped theorem names them. The encoder theorems (`locatedRow_fits`, `runCaseReported_fits`) read the generated shape through `skel%`, not these declarations, and are outside the dump | As in rd-9's pass: a dumped theorem that the encoder's `skel%` shape is this declaration's render. Even then, it would fix only the answer's form |

`decodedEnvironment` (41 -> 34), `rightsDoc` (27 -> 23) and `ownedBeneath` (4 -> 0) shrank; they are untied at the base
and now. One tie outside this batch's lines is available: `VE.Service.Document.decodeRowKind_json` is a decoder round
trip (`decodeRowKind rights j = .ok k → k.json = j`) that the tool accepts for `decodeRowKind` (9 lines; seeded tie
S2a). That declaration predates the batch, so it is left to a later pass and not added here.

### Seeded ties (each restored after its run; the tree was clean afterwards)

| Seed | Temporary change | `python3 tools/trust_map.py --check` |
| --- | --- | --- |
| S1 | `sensesLayer` tied to an unrelated theorem, `VE.Service.Document.decodeRowKind_json` (`tools/trust-classes.json`) | exit 1: "VE.Service.Document.sensesLayer: the statement of VE.Service.Document.decodeRowKind_json does not mention VE.Service.Document.sensesLayer of VE.Service.Document". `tests/test_trust_ratchet.py::test_committed_budget_passes_its_check` fails (`assert 1 == 0`) |
| S2a (control) | `decodeRowKind` tied to `decodeRowKind_json`, the round trip that names it | exit 0: "tied +9 … VE/Service/Document.lean: trusted -9". The ratchet test passes. A tie the tool can verify is accepted, so S1's and S2b's failures come from the missing mention, not from the tool |
| S2b | S2a's tie with that theorem's `-- uses` line broken: `VE.Service.Document.decodeRowKind@VE.Service.Document` removed (`lean/statements.txt`) | exit 1: "VE.Service.Document.decodeRowKind: the statement of VE.Service.Document.decodeRowKind_json does not mention VE.Service.Document.decodeRowKind of VE.Service.Document". The ratchet test fails |
| S3 | `runCaseReported` tied to the encoder theorem `ResponseShape.Encoders.Document.runCaseReported_fits` | exit 1: "tying theorem ResponseShape.Encoders.Document.runCaseReported_fits is not in statements.txt" |
| S4 | An existing tie's `-- uses` line broken: `VE.Readings.softX@VE.Readings.SoftDefaults` removed from `VE.Readings.softPremisesIn_fill` | exit 1: "VE.Readings.softX: the statement of VE.Readings.softPremisesIn_fill does not mention VE.Readings.softX of VE.Readings.SoftDefaults" |

## Seeded faults

`seed_faults.py` planted each fault, ran the named test (which failed), and restored the source; for a Lean fault the
build was pinned for the run. `evidence/mutants.json` keeps each fault's file, test and failure excerpt:

- Lean (`lean/VE/Service/Document.lean`): a norm object outside the soft source accepted without the soft route's check;
  quoted norms not checked by the norms route; a soft document's formulas read in its own environment instead of
  `E″`; a refused model decided when its set has two; the environment mode's fault taken before a soft source's check;
  a strict fence's syntax error left to the retained path. Review fixes: a soft document's parts pre-scan raising its
  fault before the unit loop (F1); a frozen envelope's meaning id under the profiles' identity version, a senses
  refusal decided without its diagnostic, and pack texts of another count read (F2).
- Python (`ve/document.py`, `tools/lean_first_diff.py`): a model path not bound to a model member; a fence span's line
  not bound; a soft rule bound as a subset of the authored one; a soft document's meaning ids bound to the document's
  environment. Review fixes (F2): a senses document's pack texts not sent; a senses unit's meaning id bound to the
  document's environment; a fence's content optional outside a senses document; a pilot written without the files
  it names.

Two further Lean checks of the new encoder theorem: a located row with a renamed `span` key, and one with a `BOGUS`
status, each broke `ResponseShape.Encoders.Document` at `locatedRow_fits` (unsolved goals); both were restored.

## What was not run

The full release gate is the chain's, on the committed final HEAD. Latency was measured only on the four pilots in
`evidence/cpu.json`. The retained Python loader is not deleted: it still decides the listed residues and the fail-closed
classes above.

Acceptance classification: the routes, binding, measurement, A/B, fault injection and saved evidence are **AGENT**
work, done here. The DRI's signatures for row 6's trust growth over R16 and row 7's pilot render ratio, and its
scheduling of the outside cases, are **HUMAN** work, deferred to the DRI. There is no **EXTERNAL** item.
