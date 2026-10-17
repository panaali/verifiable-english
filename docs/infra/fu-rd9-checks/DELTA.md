# fu-rd9-checks delta

Infra item fu-rd9-checks (acting DRI speed-feed, 2026-10-17). It handles the two relay checks rd-9's rechecks left
open (`manage-agents/rd-9-c141730-looprecheck1.final.md`, FOLLOW-UP):

1. binding-audit row 38: a rights-conflict status line reading "CONFLICT-FREE … 9 coherence premises" on an
   UNKNOWN verdict;
2. the `report_id` of soft-norms and rights admission answers.

Both forgeries were replayed against the relay on main 85b20fcba (the rights-licence-relay merge) and both were
accepted ([`evidence/forgery-replay.json`](evidence/forgery-replay.json)). So rights-licence-relay closed neither.

**What users see does not change.** No genuine Lean answer changes and no relay output changes. The change is in
what the relay refuses. A rights-conflict answer that is not Lean's is now `CheckerUnavailable` when its status
line does not fit its verdict, or when the line names a target the request does not have. Every genuine answer of
the binding inventory's 25 rights sources and 3 soft sources is still accepted
(`tests/test_relay_binding_inventory.py::test_every_bound_field_mutant_is_unavailable[*]` relays each one before
mutating it), and the recorded route cases fit the regenerated schema (`tests/test_route_row_schemas.py`).

| # | Delta | Ruling | Evidence |
| --- | --- | --- | --- |
| 1 | The Lean shape `rights.json#/$defs/packages` (the rights-conflict answer over certificate packages) now constrains each verdict. **UNKNOWN:** the status line matches `UNKNOWN: .*`, `detail` matches `(missing\|invalid) certificate for .*` (Run.lean `firstFailure`), and `conditional_on` is empty. **CONFLICT-FREE:** the status line matches `CONFLICT-FREE among rules on the same act, conditional on .*`. Before, both fields were any non-empty text. This is exactly what `Rights.Run.runRightsKind` writes (Run.lean lines 459–473). An answer that is not Lean's and breaks it, such as audit row 38, is refused by the schema check of the Lean service client. The schema is regenerated from the shape. | SIGNED by standing ruling R8 (DRI-RULINGS.md), (a): the field is now typed to the form Lean writes for each verdict. The verdict-to-line relation is Lean's, written in Lean's shape, so Python decides nothing new. | `tests/test_rd9_followup_bindings.py::test_a_status_line_of_the_wrong_verdict_does_not_fit_the_lean_shape[*]` (row 38 as the audit wrote it, the line renamed, a detail that is no certificate failure, UNKNOWN with a premise, CONFLICT-FREE with the UNKNOWN line); genuine answers: `tests/test_route_row_schemas.py`, the inventory fuzz |
| 2 | `ve/rights_route.py` `_bind_conflict` binds an UNKNOWN package answer. The target its `detail` names must be one of the answer's bound `targets`, and its status line must be the UNKNOWN line of that detail. This is the counterpart of the existing CONFLICT-FREE branch, which binds that line's counts to `conditional_on`. A forgery is refused with the text the neighbouring CONFLICT-FREE check uses: `CheckerUnavailable: Lean rights conflict is not bound to the request: unbound conflict status text`. The binding inventory now fuzzes `detail` and `status_text` (BOUND) instead of listing them as Lean's. | SIGNED by standing ruling R8 (DRI-RULINGS.md), (b): the target the line names is bound to the request's targets. The refusal text is the existing one (R1 is not needed: no text changes) | `tests/test_rd9_followup_bindings.py::test_an_unknown_line_naming_what_the_request_lacks_is_unavailable[*]` (line names `ghost`, detail names `ghost`, line and detail differ, budget shifted, no target); `tests/test_relay_binding_inventory.py::test_every_bound_field_mutant_is_unavailable[rights-conflict]` |
| 3 | `report_id` of soft-norms and rights admission: **no relay change**. It is an identity hash, a derived value. ADR 0001 (D1, signed) says "Python never recomputes it to check it", and "new relaying code adds no Python recomputation of a derived value". `bound_admission`'s recomputation on the core route is listed debt for AR-15, and the identity lint ratchets it. Lean already guarantees the value: `VE.SoftNorms.Run.runAdmission_sound` and `VE.Rights.Run.runAdmission_sound` prove that every admission answer's `report_id` is the digest of the canonical environment id, the document sent and the report (`BindingsMatchSourceAndRegeneration`, `RightsAdmissionAnswer`). The binding inventory now names that theorem for the field. A relay check was built in e9f2b755a and removed in dc97aa4fd for this reason. | Not a delta; covered by standing ruling R8 (DRI-RULINGS.md) and ADR 0001 D1: "Python accepts a tampered derived field" is not a finding when the schema types it (`hex64`) and a Lean theorem covers it. **For the DRI:** the task asked for a relay refusal. A run-time check of this field belongs to AR-15's Lean-side plan, not to a new Python preimage | `tests/test_rd9_followup_bindings.py::test_the_report_id_guarantee_is_a_stated_audited_theorem`, `::test_lean_admission_report_ids_are_the_identity_the_theorem_states[soft]`, `[rights]` |
| 4 | Trust budget: **V +6** (K +0, S +0), measured with `python3 tools/trust_map.py --check` on the final tree against its merge base with main, bc1936dd5: `ResponseShape/Schemas/Rights.lean` +6 (`packages`, G[V], like every rights shape). The check passes. | SIGNED by standing ruling R16 (DRI-RULINGS.md): at most 150 lines, none in K. The new constraints are exercised by tests that can fail (seeded bugs L1 and L2). The ties pass is asked for in `manage-agents/FOLLOW-UPS.md` ("R16 ties pass (fu-rd9-checks …)"). The allowance is recorded with `tools/trust_map.py --allow` (V 6 in `docs/trust-baseline.json`, signed "SIGNED by standing ruling R16 (DRI-RULINGS.md)") | `python3 tools/trust_map.py --check` exit 0; `tests/test_trust_ratchet.py` passes |
| 5 | Generated inventories, regenerated with `tools/regen_generated.py --write`: `ve/backends/lean_service_schema/rights.json` (row 1), `lean/declarations.txt` (the shape module's hash and line ranges), and `docs/test-architecture/binding-census.{json,md}`. The census gains 3 `pattern` leaves (`/detail` and twice `/status_text`; leaves:none 1262 → 1265) | R12 (DRI-RULINGS.md): generated inventories, never hand-edited | `uv run python tools/regen_generated.py --check` exit 0 |
| 6 | Trust ties pass for row 4 (R16's FOLLOW-UP, FOLLOW-UPS "## fu-rd9-checks"; infra item ties-fu-1017, 2026-10-17). `packages` is **not tied**, so row 4's V +6 stands: untied V of `ResponseShape/Schemas/Rights.lean` is 407 before and after. No theorem the trust map reads can name the shape, because the statement dump reads only `lean/VE/Audit.lean`, which holds no `ResponseShape` theorem. No Lean theorem relates `ResponseShape.check` at `packages` to the answers either. The runner half of the tie the FOLLOW-UP asks for is now proved: `ResponseShape.Encoders.Rights.runRightsKind_packages` (with `firstFailure_text`) states what `runRightsKind` writes per verdict. Before, only tests on genuine answers checked it. The remaining theorem is named below ("Trust ties pass") | The ties pass that standing ruling R16 (DRI-RULINGS.md) asks for. It changes no trusted line, allowance or signature | `python3 tools/trust_map.py --check` PASS before and after (`ResponseShape/Schemas/Rights.lean`: V 407 at b5248038e and after the ties, 401 at bc1936dd5); seeded bug L4 below |

Fault order: unchanged for every answer the base accepted or refused. The new UNKNOWN check runs after every
existing check of `_bind_conflict`, and the schema check runs before the binder, as before.

## Trust ties pass (row 6; infra item ties-fu-1017, 2026-10-17)

Method. `tools/trust_map.py` was run on main with the item merged (b5248038e) and against row 4's base (bc1936dd5).
Row 4's V +6 is six lines of one declaration, `ResponseShape.Schemas.Rights.packages` (G[V], 20 lines): the `ite` on the
verdict and its two branches. No theorem of `lean/statements.txt` names it.

What was proved (commit f4c6ab414, `lean/ResponseShape/Encoders/Rights.lean`, audited in `lean/ResponseShape/Audit.lean`):

* `firstFailure_text`: a certificate-package failure detail is `"missing certificate for " ++ t` or
  `"invalid certificate for " ++ t`.
* `runRightsKind_packages`: for a rights-conflict case without a witness, every answer `runRightsKind` returns is one of
  two rows. **UNKNOWN**: `status_text` is `"UNKNOWN: " ++ d ++ ", budget 10000"`, `detail` is `d` (a failure detail, as
  above), and `conditional_on` is `[]`. **CONFLICT-FREE**: `status_text` starts with `"CONFLICT-FREE among rules on the
  same act, conditional on "` and there is no `detail`. These are the per-verdict constraints row 1 wrote into `packages`.
  Before, only `tests/test_route_row_schemas.py` and the inventory fuzz checked them, on recorded answers. The skeleton
  theorem `runRightsKind_fits` checks fields only, since skeletons treat patterns and counts as `any`. Seeded bug L4
  below shows the difference: it fails this theorem and leaves `runRightsKind_fits` proved.

Why this does not tie `packages`, and is not entered in the side table: its statement does not mention `packages`. A
statement that did would have to live in a module that imports `ResponseShape.Schemas.Rights`. Such a module is a
`ResponseShape` module, and `tools/lean_statements.py` dumps only the theorems of `lean/VE/Audit.lean`, so the trust map
cannot see the theorem. A `VE` module importing the shapes would reverse the layering, in which no runner imports
`ResponseShape`. Listing it would be a vacuous tie: the tool would reject it, and a reviewer should too.

### Per-file counts (untied V lines, `trust_map.py`; base = bc1936dd5, before = b5248038e (main with the item merged), after = 670a9f329 (the ties commit))

| File | V base | V before | Row 4's V | V after | Ties | Row 4's V after the ties |
| --- | --- | --- | --- | --- | --- | --- |
| `ResponseShape/Schemas/Rights.lean` | 401 | 407 | +6 | 407 | 0 | +6 |

`trust_map.py --check` passes before and after. The main totals of the same pass (V 39,971 to 39,922, all in
`VE/Norms/Family.lean`) are in `docs/infra/fu-lf14c-f4/DELTA.md` row 5. Row 4's allowance (V 6) is not touched.

### Declarations no theorem ties

| File | Declaration (row 4's lines) | Why no theorem ties it | A theorem that would |
| --- | --- | --- | --- |
| `ResponseShape/Schemas/Rights.lean` | `packages` (+6 of 20) | A response shape. No dumped theorem names it: the dump reads `lean/VE/Audit.lean` only, and any theorem naming the shape is a `ResponseShape` theorem. No Lean theorem evaluates `ResponseShape.check` at it: the encoder theorems read `skel%`, and `Fits` keeps no pattern or count. `runRightsKind_packages` proves what Lean writes, but not what the shape accepts | Two statements over `ResponseShape.check [Rights.file, Common.file] depth packages ctx [] v`. (1) Acceptance: every row of the two forms `runRightsKind_packages` gives (with `targets` a string array, `conditional_on` labels `conditional_labels` accepts, a valid `id`) checks `.ok ()`. (2) Refusal, which fixes what the six lines mean: every `v` it accepts with `verdict` UNKNOWN has the UNKNOWN status prefix, a missing/invalid certificate `detail` and an empty `conditional_on`, and every `v` with CONFLICT-FREE has the CONFLICT-FREE prefix and no `detail`. (1) alone would hold of a weaker shape. Both need lemmas on `Re.matches` for `Re.prefixes` (no `String` prefix lemmas exist in the toolchain). They also need the dump to read `lean/ResponseShape/Audit.lean`, or the shapes to move into a module `VE/Audit.lean` may import. That is a change to `tools/lean_statements.py` and the trust map's anchor rules, outside a ties pass |

### Seeded bug (restored; `docs/infra/ties-fu-1017/mutants.json`)

| Seed | Temporary change | Failure |
| --- | --- | --- |
| L4 | `runRightsKind` writes the UNKNOWN line without its colon (`s!"UNKNOWN {…}, budget 10000"`, `lean/VE/Rights/Run.lean`) | `lake build ResponseShape.Encoders.Rights`: `runRightsKind_packages` fails (Encoders/Rights.lean:189); `runRightsKind_fits` still proves |
