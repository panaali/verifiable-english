# sc-11 report: the superposed soft route's Lean side (rd-9 14.13, first build item)

**No DRI signature is reserved.** Every 14.8 statement is built and proved; the soft runners moved to **sc-11c** under
the DRI's pre-approved cut (reviews/dri-decisions-20261109-sc-11-2.md item 1). The dispatch is unchanged: no answer
changes, no DELTA row, pilot bytes 0 (14.13). Spec section 14 came in by cherry-picking 33bc5f48f and ea5b0e420.

## Plan rows and directives

| Row | Delivered |
| --- | --- |
| SC-11 (plan :1266), Lean side | `SoftSupLabels.lean` (14.8 block 1: 3 definitions, 8 theorems), `SoftSupWire.lean` (block 2: 5 definitions, `SupReplaySD`, 9 theorems), `SoftSupWireExamples.lean` (14.9 W-2 to W-6′, W-3's base column, W-5, W-5′, W-13's route values). Python side: sc-11b |
| D3 | The enumerated row and its cause are untouched (nothing dispatches on `routeSD`) |
| D11, D12 | Nothing on the rights chain or own vocabularies; no wording |
| D13 | Soft-only code in new `Soft*` files; no general definition with `X` moved; `SoftSup.lean`, `SoftSupExamples.lean` unchanged |
| D14 | The certificate theorem reads `supCertificateCheckSD` (sc-10b), whose premises are `premisesX`; binding is sc-11c's runner |
| Runners (`readings-conflict`, `-certificate`, `-model`, the soft row, verdict scopes), read-once tests, W-13's conflict in one proof | **sc-11c**, filed (`backlog.sh add sc-11c`, sc-11b blocked by sc-11, sc-11w, sc-11c) |
| `tools/layer_policy.py` rows | None needed: the `VE.` default puts all three modules at layer 2 (`tools/check_lean_imports.py`: "Lean layer graph kept") |

**Size** (`git diff --numstat` against 33fe04615, generated files excluded): exempt 1,537 lines (the spec copy and its
two signed edits; statement-gate proofs; ruling-condition fixtures), the rest about 410 (definitions, docs, tests,
tools, trust classes, this report). RD-6b's analogues of the runners are 636 lines (55 replay, 91 runner, 490
verdict wire), so with them the rest passes ~600, and the pre-approved cut applies.

**Statements.** `tools/check_rd9_sc1_statements.py`: "SC-11 labels PASS: 11 exact", "SC-11 wire PASS: 15 exact",
nothing not built; `tests/test_rd9_statements.py`: 43 passed (both after the regen). `lean/audit.py`: PASS; each new
theorem uses only `propext`, `Classical.choice`, `Quot.sound` (`lean/axioms.txt`). `supLabel_pull`/`supLabel_other` are
`exc_pullF`'s and `coh_pullF`'s per-premise halves: SoftSup.lean keeps those pieces inside its proofs and is read-only
here, so `sel_pullF` (F1-F4), `excPrem_pullF` and `excPrem_dead` restate them per premise, and `label_unique` locates
a premise by its label (a choice's document need not pass the soft check, so its names are read through their
images). The wire theorems apply sc-10b's three theorems and restate none.

## Measurements and rulings

- **OPEN-SC11-7** (DRI 2026-11-09 sc-11 item 1, SIGNED, commit b1b2e801f): `maxSdCheckWork` = 32,768, measured
  (`docs/rd-9/sc-11/w13-cpu.md`, compiled Lean on the VM, AMD EPYC 7B12, load 78 to 108: ~29 µs per unit on W-13's shape,
  NSDbig 8 0.71 s, NSDbig 10 3.67 s). Past 64 choices a document is decided in one proof when `sdCheckWork` is within
  32,768 (256 W-13-shaped choices); `maxChoiceChecks` 1024 stays a second bound and can bind first (`NSDcount`: the cut
  list stops at 1025 choices, 9 units each, work 9,225, enumerated by the count). Correction sent to the DRI: the two
  wide-guard rows' cost is `sdSuperposable`'s, not the per-choice texts' (w13-cpu.md); it bears on sc-11w and
  sc-admit-cpu, not on the constant.
- **14.2** (sc-11-2 item 2, SIGNED, commit ef6699583): the work limit applies at any choice count; `NSDheavy` (64
  choices, `sdSuperposable` true, work 34,752) is enumerated (SoftSupWireExamples.lean:174).
- **W-6′'s `WellFormedU (supU N)` row is not isolated**: `⟨D4, ["bogus"]⟩` fails it and every choice's text too. The
  checks `WellFormedU` adds to `superposable` on the superposed document are the rule count with the unspecified names
  and the node count with the fill guards; a superposed document over them whose every choice is under them needs about
  10,000 guard nodes, whose checks take minutes in a `#guard` (w13-cpu.md). The other conjunct rows are isolated
  (M8: `sdChecked` true, `superposable` false; NSDlate: only the per-choice texts fail; NSDbig 11: only the count).
- **Read once (14.11)**: `sdChecked` and `sdCheckWork` each build `checkedChoices`, and `sdSuperposable` and
  `sdCheckWork` each build `sup N.D`, as 14.8's approved bodies are written; sc-11c's runners read them once per case,
  and sc-11w's stricter measure may take the computed list. W-6 decodes a small environment (`envWith 0`): the route
  reads `re` only through `sdChoiceText`'s author checks.

## Seeded bugs and mutants (`docs/rd-9/sc-11/mutants.json`)

Lean: M1 `labelImage` (W-2, W-5 fail), M2 `routeSD` without `sdChecked` (W-6′ fails), M3 a no-image label shown as `""`
(W-3 fails), M4 `sdCheckWork` not charged (W-13's work case and the 64-choice work fixture fail), M4b the work charge
read after the texts (the statement compare fails), M5 `nodeExcLabels` (W-2′ fails). Python: P1 in the statement
checker (`test_rd9_statements_match_the_approved_text_with_nothing_unbuilt` fails). Not run: 14.9's W-7 and W-9 bugs
(sc-11b's wire fixtures). Trust mutants (`docs/rd-9/sc-11/trust-mutants.json`, cloud pool): the first run on `sdShown`
left 18 survivors (list truncations); five `sdShown` fixtures were added, and the rescored run gives 45 killed,
0 survivors, 1 unknown (M008, a mutant that does not type-check).

## Trust

`tools/trust_map.py --check` against 33fe04615: K +0, S +0, trusted +5 (`sdShown`, untied G[V]; `labelImage` tied to
`labelImage_fst`, `_snd_mem`, `_functional`, `supLabel_pull`, `supLabel_other`; `nodeExcLabels` to `excLabels_nodes`;
the route pieces C, `maxSdCheckWork` G[R]). Allowance recorded: "SIGNED by standing ruling R16 (DRI-RULINGS.md), sc-11,
2026-10-18"; FOLLOW-UPS.md row "## sc-11". DELTA: none (no answer changes).

## Tests

TESTS: pending the final selected run.

## Spec re-read

Each 14.8 declaration against the code (the compare above); 14.9 W-2 to W-6′, W-13 (as signed) against each `#guard`;
14.11's "charged before use" against `sdChecked`'s order (M4, M4b); 14.2 as amended; 14.13's sc-11 bullet.

## Self-review against BUILDER-CHECKLIST

1. N.A.: no relayed answer (no runner, no Python).
2. PASS: plan rows above; runners cut by DRI ruling sc-11-2 item 1; no Python copy of a Lean decision.
3. PASS: M1-M5, M4b, P1 each fail a named check; trust mutants 0 survivors.
4. N.A.: no Python or Rust product code.
5. N.A.: no relay binding.
6. PASS: the chain runs the gate on the final HEAD; evidence above names its commands.
7. PASS: trust growth signed under R16; no DELTA row.
8. PASS: no user-visible change (dispatch unchanged).
9. PASS: `tools/select_tests.py --base 33fe04615` selects `tests/test_rd9_statements.py`.
10. PASS: statement compare PASS; mutants M1, M4b; `lean/audit.py` PASS.
11. PASS: over a limit the route is enumerated, never superposed (W-13, `NSDheavy`, `NSDcount`).
12. PASS: no live path changed; W-13's CPU measured (w13-cpu.md).
13. PASS: `tools/gate_collection.py --check --prebuilt`: 0 refused, 0 stale, 0 malformed.
14. PASS: each iff has a fixture per direction (W-5, W-5′, W-6/W-6′); claims cite commands.
15. PASS: overclaim (W-6′ row stated as not isolated); cut by ruling; every new check has a mutant; limits read before work (M4, M4b).

SELF-REVIEW: 2 A, 8 B, 6 C; fixed 15 (B1 documented, not isolated)
