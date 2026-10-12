# Batch 13b A/B delta: core operations default to Lean

Base `main` at `abc30811`; head: this branch. `tools/lean_first_diff.py compare` read the base and head
recordings of every corpus (probe, conformance, pilots, readings, discourse, rights, quantity, norm defaults,
documents) under every authority they have, with [`DELTA.json`](DELTA.json) as the list; the result is
[`evidence/corpus-ab.json`](evidence/corpus-ab.json) and its counts are in [REPORT.md](REPORT.md) (generated from
that file). There are **no verdict and no availability changes**, and no unlisted difference.

## Wording (one block, 18 text pairs in `DELTA.json`)

* **Parse diagnostics under the default authority (48 records, 16 pairs).** Batch 13a moved the parser's
  diagnostics into Lean, with Lean's `Class:` prefix (`SyntaxError: expected ')'`, `ResourceLimit: source exceeds
  65536 bytes`, ...). The default authority now reaches them too; under `VE_AUTHORITY=lean` they were already
  the answer, so the `lean` column is unchanged. These are the same 13a pairs.
* **A probe budget boundary (1 record).** `Expected a JSON object` becomes Lean's wire text `offset 875: expected
  restricted JSON value`.
* **Document corpus (19 records).** The same parse texts reached through `check_document`/`render_document`.
* **Pilot corpus (7 records).** The recorder's own scratch path differs per side inside a missing-file message
  (`/tmp/b13b-ab/base.pilots/pack.json` against `.../head.pilots/...`); the answers are otherwise identical.
* **Outside the recorded corpora, found while switching** (tests updated, each named here): Lean's bundle
  reading-binding text `Reading label is not bound to its registered reading formula or citation is unresolved`
  replaces Python's three (`Unresolved citation hypothesis`, `Reading label has no unique registered reading set`,
  `Reading label depends on a superseded reading set version`); a forged v0 certificate version is
  `certificate does not replay` rather than `certificate is stale or bound to different inputs` (same verdict).
  Porting Python's more specific bundle texts into Lean (DRI answer 3) is a follow-up, not done here.

DRI answer 3 (2026-10-04) makes Lean's texts canonical; the exact pairs await the DRI's block signature (HUMAN).

## Order (4 records, each needs a DRI signature)

`document/default` mutants 634 and 940 (`document_check` and `document_render`): a formula naming a constant or
predicate `null`. Base: Python typing said `UnknownSymbol: Unknown constant None` (`... predicate None`). Head:
the Lean relay refuses the value at the wire, `InvalidInput: Unsupported JSON value; null and floating-point
numbers are not in v0`. Same rejection, another code. Outside the corpora the norms@0 wire-contract unit's Z8 case
`0:profile-missing` (a norm unit without `norms@0`) changes from `SyntaxError: AST nodes must be nonempty tagged
JSON arrays` to Lean's route decoder text `array expected` (`InvalidInput`); `tests/test_norms_contract.py` pins it.
**DRI signature: not yet given** (HUMAN, owner: DRI).

## Retained fallbacks (no Python decision deleted for these inputs)

The four stage-2c branches named by plan row 13b stay until 14a–d:

1. `definitions@0` surface sugar (`parser._parse_lean`): a source read through a sugar production, or rejected
   inside one, keeps the retained reader's answer (batch 14a).
2. Non-first-order norm guards on the closure, core and order families (`norms._lean_route`) (batch 14b).
3. n-ary core definitions (`definitions._compile_lean`, `validation.family_in_scope`) (batch 14c).
4. Coupled reading sets and discourse joint choices (`readings.check_readings`): Python's enumeration and
   verdict over Lean-checked per-choice evidence (batch 14d).

Scope gaps the switch found that the plan's list did not name, each kept on the retained path and listed for the
DRI (HUMAN):

5. Parse over statement-layer and W6 environments (`parser._lean_parse_scope`), graph and readings outside
   `validation.family_in_scope`, norms over statement-layer environments (`norms._lean_route`), and bundles
   outside Lean's bundle modes (`bundle._lean_bundle_mode`, including a container with no decodable ve.core@0.2
   environment). These were already the scope of the `lean` authority's adapters.
6. Certificate replay, premise status and compare over `norm-defaults@0` and `readings@1` environments
   (`entailment.lean_check_scope`): no Lean mode replays or checks a countermodel there while binding the whole
   environment. Follow-up: a certificate and countermodel mode over the readings/norm-defaults frame.
7. The envelope routing refusal `admission requires a ve.core@0.2 environment` for a frozen v0/v0.1 envelope
   (`admission._admit_lean`): Lean's route answers it with a raw decoder text.
8. The prover's internal replay (`_background=False`, generated premises) and `ast._Checker` for generated
   formulas: generator-internal, never reported (rule 3, lead decision 2026-10-08, question 10 closed as option A).

## Lean changes

`VE.Service.Standalone.typingReduced` also sets `readings@1`, `norm-defaults@0` (placeholder `deny`) and `risk@0`
(`riskReduced`) aside, as `modelEnvironment` already did, so typing has no Python fallback for those profiles; the
soft-norms branch now filters the current profile list. No theorem statement changed (`tools/lean_statements.py`:
0 added, 0 removed, 0 changed). `tools/trust_map.py --check` reports **trusted +8** lines in
`VE/Service/Standalone.lean` (untied [V]). As batch 16b did, `tools/trust_map.py --write --reason` records the
growth in `docs/trust-baseline.json`'s history with that reason, which says the allowance awaits the DRI's
signature; no `signed` entry is written (HUMAN, owner: DRI).

The looprecheck1 fix adds `VE.Core.Layers.folEntry` (at most two arguments), now the one filter of every
regenerated Background (`folPredicates`, the norms view, the n-ary definition checks). No theorem statement
changed.

**Certificate counts are Lean's (fix3, architecture decision D1, DRI-RULINGS R8/R11).** The schema's and the
response shapes' prediction of a certificate's `background` count (`x-background-count`,
`ResponseShape.backgroundCount`, `service_schema._fol_entry`) is deleted: each fix of the prediction broke
another case (looprecheck2: a plain norms certificate over a 3-argument norm pair, which Lean counts, was refused
as CheckerUnavailable). The client now binds the count only by a closed relation to the request,
`x-background-bound` (`ResponseShape.backgroundBound`): an integer at most four per predicate declaration, one
per pair of constants and one per `soft_premises` element (`test_background_bound_is_a_relation_to_the_request`
enumerates request shapes against Lean's decoder). `ResponseDecode`'s invariants no longer predict counts from
the request either (`folCount`, `flagsCount`, `definitionsCount`, `literalsCount`, `regulatedCount`,
`pairsCount`, `runs` are deleted): a certificate's `background` must equal the length of the Background the
same mode's runner regenerates for its environment (plus a plain norms certificate's soft premises), a norms
certificate's `background` and `layers` the regenerated `norms-elaborate` Background and layer premises, and a
`background` or `norms-elaborate` row's Background list the regenerated one
(`test_certificate_background_is_lean_checked_not_client_predicted`,
`test_genuine_soft_premise_certificate_count_is_lean_checked`, and the mig1c `*-background-*` content cases).
The plain norms certificate path (`usesNormsPath`), unchecked before, is now held to the same invariant.
Regressions: `test_norm_pair_certificate_check_is_valid[1-4]` and
`test_genuine_norm_pair_certificates_are_valid_at_every_arity` (the service corpus gains norm pairs of 1-4
arguments, `norm_pair_cases`, a soft-premise certificate and a norms certificate with a literal pair); the
3-argument `defined` case of looprecheck1 stays Valid (`test_genuine_certificates_over_nary_families_are_accepted`).
Trust: `tools/trust_map.py --write` lowers the [V] budget from 34980 to 34965, below the 34966 before the two
count-binding allowances (+7, +7) that awaited the DRI's signature, so neither is needed any more.

**Follow-ups (not fixed here):**
* Lean's profile premise for a norm pair with three or more arguments is a vacuous `∀∀∀(⊥→⊥)`
  (`VE.Norms.Basic.atom` returns `⊥` outside the FOL projection, `Norms.Plain.pairPremises` keeps the pair). It is
  counted and harmless, but it states nothing; already the case before this batch.
* A proof that needs a 3-argument definition is NotFound on both sides (Python's prover and Lean's FOL
  projection drop it): a completeness gap, not a wrong answer.

## Behaviour notes for reviewers

* `dispatch.owned` runs a Lean-owned operation under every selection and pins its constituents to Lean, so
  premise status and compare read Lean-checked replays and model checks only, as `VE_AUTHORITY=lean` did.
* Background requests send the model projection (`lean_runner.background_environment`, with W6 annotations erased),
  so Lean regenerates Background for alternatives, risk, norm-defaults, readings and W6 environments, which the
  route projection refused; Lean's premises are decoded structurally, not retyped.
* Trusted Background slots (soft, rights and the norm-defaults fill premises) reach Lean's replay in the norms
  route's `soft_premises` slot over layered environments, and as the leading case premises otherwise (the same
  ordered list); the fill slot was in the deleted Python generator only.
* `admission.bound_admission` binds every admission row to its request: kinds, the graph's root and `report_id`
  as the identity of the returned report (`wire.digest`, rule 5). This closed a hole the new relay fuzz found:
  a report with an assumption dropped or duplicated passed the row schema.
* The differential fuzzer's reviewed baseline shrinks from 254 to 250: four `requests` disagreements between
  Python's and Lean's answers are gone because the Python column is Lean's answer (`three_way.KIND_OPERATIONS`).

## DRI rulings

- [x] §8.1, per-batch corpus evidence and the 3-day operational soak after 13b: the A/B is
  `test_report_numbers_are_regenerated_from_saved_evidence`; the soak is EXTERNAL (owner: DRI), not started here.
- [x] §8.3, Lean's text is canonical: `test_an_empty_or_extra_row_is_refused` and the wording block above.
- [x] §8.7, frozen Python oracle: `tests/test_norm_defaults.py` still runs the frozen norm-defaults oracle.
- [x] §8.10 (rule 3, option A): the retained prover replay is item 8 above.
