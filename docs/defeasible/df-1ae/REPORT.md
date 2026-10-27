# df-1ae: the route (build report)

No DRI signature is reserved. DELTA D1 (the four kinds answered) is signed by the DRI's DF4 decision, as the task directs;
T1 (trust) by standing ruling R16. Nothing of the task was cut; the size is above the guideline (section 4).

Branch `feature/df-1ae`, base main a547f2141 (the merge base). Plan and spec as on main.

**Statement gate.** DF-S passed (`manage-agents/defeasible-p3ver1.final.md`). `docs/defeasible/df-1ac/evidence/
compare_statements.py` on this HEAD: **42 OK, 0 not OK**. No statement of spec 7.2 changed (`viewOf`, `defaultsCase`,
`Collision` and the theorems are as approved). No text claims minimality (DF-2 is not proved).

## 1. Delivered

| Task deliverable (DF-1a; spec 7.2, 8.1; DRI DF4) | Where | Test |
| --- | --- | --- |
| (1) The four `defaults-*` kinds as one entry of the layered kind table's construction (`defaultsKinds.map`, as `legacyRows`, the `soft` pack), in a module after `Wire.lean` | `lean/VE/Defaults/Route.lean`: `defaultsRows`, `layeredRows := legacyRows ++ defaultsRows`, `layeredKindCase`, and `runLayered` (moved from `Layered.lean`, now over the whole table) | `RouteExamples.lean`; seeded bugs RT1–RT7 |
| (2) The routing in `NormDefaults/Run.lean`; `defaultsCase_other` still holds; no other kind's answer changes | `runOtherCase` sends `defaults-*` kinds of the row (`defaultsKinds.contains`) on a layered source to `runLayered`. `layeredKindCase_other`: every kind outside the row is dispatched by today's rows | 330 of 330 recorded route cases byte-identical against the base (`evidence/byte-identity.json`); `RouteExamples.lean` "other kinds"; RN1, RN2, RT4, RT6 |
| (3) Response shapes, encoder theorems, `runLayered_fits` keeps holding; generated schemas | `Schemas/NormDefaults.lean`: `defaults_elaborate`, `_coherence`, `_certificate`, `_model`, `_situation`, kind and row entries. `Encoders/NormDefaults.lean`: `dispatch_okP`, `collides_named`, `defaultsCase_fits`, `layeredKindCase_fits`, `runLayered_fits` (same statement). `norm-defaults.json` by `regen_generated.py --write` | `ResponseShape/DefaultsExamples.lean` (both sides); 11 genuine cases in `tests/data/route-cases.jsonl` (`test_route_row_schemas.py`); SH1–SH9 |
| (4) df-1ac review F3's wire points, each on both sides | `Wire.lean`: COLLISION shows the situation (`situationJson`); DF-ω's `[]`, `"coherence": null` and no member send no pair certificate (UNKNOWN), a non-empty list still gets diagnostic 5, a non-list is refused; a collision naming an undeclared rule is refused (`InvalidInput: a collision names an undeclared rule <r>`), a declared pair named in reverse stays UNKNOWN | `WireExamples.lean`; WR1–WR7 |
| df-1ad review C findings sent here | F3: DOES-NOT-FOLLOW shows the situation and its gaps (`modelFields`). F2: the four `forcedAt` allow reasons corrected (equivalent mutants). F5: df-1ac W3/W8 and df-1ad M4, R10, R19, R20 follow the changed code; both rerun on this tree, all fail (`evidence/df-1a{c,d}-mutants-rerun.out`). F4 was fixed in df-1ad; F6 is size | — |

## 2. Deviations (no approved statement changed)

1. **The row decodes through `viewOf`.** A `KindRow` receives the decoded `LayeredU`, but a `DefaultsView` needs
   `L.U.D = soften L.D`, which only `decodeLayered`'s equation gives, and `viewOf`'s approved text decodes the request
   itself. So a `defaults-*` case decodes its source twice: 4.0 against 3.3 ms per case for `norm-defaults-elaborate`
   on the same one-rule document (warm service, 20 cases). Every other kind decodes once, as before. Removing it needs
   a change to `viewOf` (DRI) or a soften equation in `LayeredU`: FOLLOW-UPS "## df-1ae".
2. **Spec 5 against 8.1 on DF-ω's `[]`.** Diagnostic 5 refused `[]`, while 8.1 gives DF-ω's `[]` UNKNOWN. The shapes
   follow 8.1: an empty, `null` or absent list sends no certificate; diagnostic 5 applies to a non-empty list.
3. **New refusal text** `InvalidInput: a collision names an undeclared rule <r>` (review F3), not in spec 5's table.
4. **The situation** (spec 7.2 "the situation"; plan 2.2 "the situation and its gaps") is `{"filling": {unsaid table:
   rows}}`, every unsaid table of the checked filled situation, as a reachable report line's witness shows it
   (`witnessRow`). The base situation is the request's own `model`, which the relay binds. With COLLISION the answer
   requires `collision` and `situation` (`collides_named`: a checked collision names a colliding pair).
5. **Not edited:** `NormDefaults/Admission.lean` (arch-20261026-2), `ve/` relay code (df-1b), `Service/Document.lean`.
   `ve/assurance-manifest.json` changes only pins: `runLayered`'s decoder pin moves to `Route.lean`, `Layered.lean` and
   `Wire.lean` are repinned, `RouteExamples.lean` is classified as fixtures. `tools/layer_policy.py` puts
   `VE.Defaults.RouteExamples` with the other runner-boundary fixtures (layer 4).
6. **Corpus.** No Python test sends these kinds before df-1b, so the eleven `defaults-*` cases in
   `tests/data/route-cases.jsonl` are the Lean fixtures' requests (each kind and verdict, and a refusal), answered by the
   real service. `test_route_row_schemas.py` requires a genuine answer per schema kind and fuzzes them.

## 3. Evidence

- `lake build`: every `#guard` passes. `python3 lean/audit.py`: PASS. `regen_generated.py --write`: 33 entries.
- `trust_map.py --check`: PASS with the R16 allowance (V +104, K +0, S +0).
- `compare_statements.py`: 42 OK. `gate_collection.py --check --prebuilt`: 19,392 collected, 0 added, 0 removed.
- Seeded bugs: `python3 docs/defeasible/df-1ae/evidence/run_mutants.py` (in place, the file's theorems removed):
  controls 0 failures, **25 of 25 fail** their guards (`evidence/mutants.out`).
- `trust_mutants.py` (Mac, `--allow trust-mutants-allow.json`): on the final Lean, 398 mutants of 16 definitions: **383 killed, 0 survivors, 0 unknown, 4 invalid, 11 allowed**,
  exit 0 (`trust-mutants.json`). Each allowance has its one-line reason in `trust-mutants-allow.json`: texts that do
  not elaborate (7), `defaultsRows := []` (the tool counts no kill through `runLayered`; it is seeded bug RT3), the
  `obj` keyword of the certificate shape (redundant: its condition's branches refuse non-objects), and two `row` entries
  no defaults answer reaches (the batch decoder's `case_error`, the admission row). The first full run's 33 survivors
  were fixed by fixtures (pack order, conditional members, tuple bounds, objects retyped, an error row, an off-path row).
- Selected tests: `mac-pytest.sh --select -- --base a547f2141 --run` (ran on the VM: no Mac slot), HEAD 3abbff52d:
  373 units including `lake build`; **1 failed**, `test_assurance_manifest.py::test_every_json_handling_lean_file_is_classified`
  (the new `ResponseShape/DefaultsExamples.lean` unclassified), fixed in 2f44e2fbf; the file then passes alone (137
  passed). An earlier selected run failed `test_route_row_schemas.py` (no genuine answer per new kind; then a COLLISION
  member whose drop was accepted): fixed in c448d9618, and the file passes (229 passed with the corpus readers). No
  test of `main-known-red.txt` failed.
- Not run by me: the full gate (the chain runs it).

## 4. Seeded bugs, trust, size

Seeded bugs (Lean only; no Python or Rust product file changed), `mutants.json`, saved run `evidence/mutants.out`:

| # | Definition: bug | Fails |
| --- | --- | --- |
| RT1 | `defaultsRows`: no pack needed | the soft pack guard |
| RT2, RT3 | `defaultsRows`: every kind answered as elaborate; `layeredRows` without the row (claim 1) | the row through the mode |
| RT4, RT6 | `layeredRows` without today's rows; `runLayered` over today's table (claim 2) | other kinds unchanged; the row |
| RT5, RT7 | `layeredKindCase`: no pack ids; `defaultsKinds` without `defaults-model` | the row |
| RN1, RN2 | `runOtherCase`: every `defaults-` kind routed (a kind outside the row changes its refusal); none routed (claim 2) | `defaults-other`'s refusal; the row |
| WR1–WR3 | `situationJson` without the filling; COLLISION and DOES-NOT-FOLLOW without the situation (claim 4) | a filled gap; DF-γ; DF-β (i) |
| WR4, WR5 | `pairCertsOf`: `[]` refused; `null` read as a list (claim 4) | DF-ω's `[]`, `null`, no member |
| WR6, WR7 | `collisionOf`: undeclared rule not refused; only the first rule checked (claim 4) | undeclared rule |
| SH1–SH9 | the shapes: rules unbound, situation without COLLISION, basis untyped, DOES-NOT-FOLLOW without situation, label untyped, filling rows untyped, kind misnamed, row mis-selected, situation's shape dropped (claim 3) | `ResponseShape/DefaultsExamples.lean` |

**Trust** (R16, DELTA T1): V +104, K +0, S +0, per file in DELTA T1; FOLLOW-UPS "## df-1ae" asks for the ties pass.

**Size** (`git diff --numstat a547f2141`, hand-written): about 660 lines before this report, about 790 with it:
product Lean 250 (`Route` 46, `Wire` 40, shapes 86, encoders 76), fixtures 270 (`RouteExamples` 72,
`DefaultsExamples` 87, `WireExamples` 27, route cases 11, mutants 44, runner 65), ledgers 120. I measured 370 after
the first half (route, shapes, encoders, wire points) and kept going: the rest is the fixtures and evidence that R16
and the corpus test require, not further features. Nothing coherent could be cut to a next item.

## 5. Pilot bytes and next items

Bytes 0 (estimate): no CLI path calls these kinds until df-1b's relay. **Next:** df-1b, the relay and the first pilot
number (df-03's baseline P-1 0 of 3, P-2 SOME ×3); DF-2 alongside; pk-1c can now add its row after `defaultsRows`.

Evidence commit list (`git log --oneline main..HEAD --no-merges`, before this report): 9d17e066b, 2f44e2fbf, 3abbff52d, c448d9618, 835d2a9c5, d8dab408e, 63d016427, fc6a97289, 93d0d42b9, 896ce9ec3, 420615928, f9ec29141, 5ad4ae060, b7b9ba740, 56f23d799, cc6d5738b, 5cd76c338, dd139945f.

## Self-review against BUILDER-CHECKLIST

1. **Lean answers typed and contained.** PASS: closed shapes typed to the leaves; `ResponseShape/DefaultsExamples.lean`
   refuses every variant of each answer (member added, object/leaf/array retyped, required member dropped, tuple
   length); `test_route_row_schemas.py` fuzzes the eleven recorded answers through the client schema and Lean.
2. **Every deliverable built.** PASS: section 1, deliverables (1)–(4) and the review C findings; no Python copy of a
   Lean decision; in-flight overlap only `lean/VE.lean`'s import list (union-merged).
3. **Tests can fail.** PASS: 25 seeded bugs (`evidence/mutants.out`), `trust_mutants.py` (`trust-mutants.json`).
4. **Python, Lean and Rust agree.** PASS: base and head side by side on all 330 recorded route cases
   (`evidence/byte-identity.json`); the head's answers pass the client schema in `LeanService` (`evidence/delta.json`).
5. **R8 binding.** N.A. for the relay (df-1b). The shapes bind what they can (`id`, the collision's `rules`
   `.equals "/collision/rules"`); a collision naming an undeclared rule is refused (WR6, WR7).
6. **Gate evidence matches the final HEAD.** PASS: base is the merge base; the chain gates the final HEAD.
7. **No unsigned item.** PASS: D1 SIGNED by the DRI (DF4 with SYNTHESIS O3, as the task directs), T1 R16.
8. **Every user-visible change in DELTA.** PASS: D1 (`evidence/delta.json`: base refused, head answers), T1; 330/330
   recorded cases unchanged.
9. **Test selection.** PASS: 373 units selected, including `lake build`, `test_route_row_schemas.py` and the
   manifest tests, which failed before their fixes on this branch.
10. **Statements say what is claimed.** PASS: `compare_statements.py` 42 OK; `defaultsCase_fits` is about
    `defaultsCase`'s returned row; SH1–SH9 and the encoder build break on wrong shapes.
11. **Budgets fail closed.** N.A.: no budget or deadline added; the kinds give UNKNOWN without checked evidence
    (df-1ad's guards, unchanged).
12. **No CPU or memory regression.** PASS for other kinds (one decode, as before); the new kinds decode twice
    (deviation 1, 0.7 ms per case measured); no pilot run (L70).
13. **Test-removed trailers.** PASS: no test removed (`gate_collection.py --check --prebuilt`: 19,392 collected; 0 added, 0 removed, 0 refused, 0 stale, 0 malformed).
