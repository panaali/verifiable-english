# sc-admit-cpu: `admitSD` within R4 on the large soft-chain documents (REPORT)

- Status: built. Step 1 (measurement) and step 2 (the charge) are done; the DRI signed the step-2 build, the move and
  the DELTA row: manage-agents/reviews/dri-decisions-20261111-sc-admit-cpu.md, items 1-3.
- Changed: `admitSDOf` now reads `sdAdmitWork N ≤ maxSdAdmitWork` (131,072) before the at-most-64 per-choice texts.
  Over it, admission refuses with `ResourceLimit: the per-reading checks of <n> readings exceed 131072 units`.
  `sdSizeCharge` moved, unchanged, to SoftWire.lean.
- Open: documents with many fixed rules are still over R4. The cost is in `admitS2`, before the charge (Notes for
  the DRI, item 1). No signature is reserved.

## Step 1: measured on main (docs/rd-9/sc-admit-cpu/cpu.md)

The three named documents are within R4 on main (5f756e791d): `run_bench.sh`, output `output-main-step1.txt`, VM
AMD EPYC 7B12, load 15-20, user CPU of three runs, process start-up included.

| Document | `admitSD` | CPU |
| --- | --- | --- |
| NSDbig 6 | ok | 0.13, 0.12, 0.13 s |
| 767-node guard (`NSDbig 8 (wide 8)`) | ok (65 choices, so no per-choice text runs) | 0.09, 0.09, 0.09 s |
| 3,071-node guard (`NSDbig 6 (wide 10)`) | `ResourceLimit: generated norm layer …` (`admitS2`) | 0.06, 0.06, 0.07 s |

On main, no live path evaluates `superposable` or `supU` on a soft-chain document (cpu.md "Does a live path…", with
file:line for each entry). `readings-dead` builds `sup D` itself (`deadCheck`/`unsatCheck`, Superpose.lean:788-791):
0.06-0.10 s on these documents (`sup` mode).

sc-11w's own documents are over R4 through the live admission: NSDheavy took 1.96, 1.88 and 2.00 s, and heavyIn
1.30, 1.32 and 1.60 s (`output-main-wider.txt`). The cost is the 64 per-choice `sdChoiceText`s (cost split in
cpu.md). The builder asked the DRI (inbox 20261111T102054Z), and the DRI signed step 2 (item 1).

## Step 2: the charge (DRI 2026-11-11 sc-admit-cpu items 2-3)

- Move (item 2): `sdRuleCharge`, `sdContentCharge` and `sdSizeCharge` moved, text unchanged, from SoftSupWire.lean to
  SoftWire.lean. `maxSdSizeCharge` and `sdSuperposable` stay in SoftSupWire.lean.
- Proof change in SoftSupWire.lean (not only the deletion): `sdCheck_of_admitted`'s proof unfolded `admitSDOf` and
  followed its splits. It now reads the new lemma `admitSDOf_texts` (SoftWire.lean) in one line, and its statement is
  unchanged. Recorded here because item 2 says "the deletion only".
- New in SoftWire.lean:
  - `sdAdmitWork N := (choices N.D).length * sdSizeCharge N`;
  - `maxSdAdmitWork := 131072`;
  - `sdAdmitWorkText`;
  - `sdTextsWithin limit re N`: 4.1 step 5 with a limit parameter, the charge first;
  - `admitSDOf`, which reads `sdTextsWithin maxSdAdmitWork`;
  - theorem `admitSDOf_texts`.
- The limit: the provisional 524,288 and 262,144 admit 64-choice documents over 1 s, so the limit was lowered to
  131,072, as item 3 directs (cpu.md "The limit").
- Charged figures (`output-charged.txt`, commit 5cfea74ca9, load 27-41):
  - NSDheavy: refused in 0.23, 0.22, 0.22 s.
  - heavyIn: refused in 0.23, 0.20, 0.21 s.
  - At the limit (`atLimit`, 131,072 units): admitted in 0.57, 0.61, 0.61 s.
  - `overLimit` (133,120): refused in 0.21-0.23 s.
  - NSDbig 6: 0.15-0.18 s. `wideGuard767`: 0.08-0.09 s. `wideGuard3071`: 0.07-0.08 s.
- Spec: 4.1 step 5 gains the charge and its text. 14.11's `sdChoiceText` row names the charge, and a paragraph gives
  the figures and the open gap. Neither section is a checked statement block: `tests/test_rd9_statements.py` passes.

## Tests and checks run (final code unless noted)

- `lake build` (whole tree): 1405 jobs, ok. `python3 lean/audit.py`: PASS, 853 files, 9526 theorems.
- `lake build VE.Readings.SoftWireExamples`: the module's ten `#guard`s pass (lines 34-56).
- `uv run pytest -q tests/test_rd9_admit_charge.py`: 9 passed, through the rebuilt service.
- `uv run pytest -q tests/test_rd9_sc11_charge_wording.py tests/test_rd9_statements.py`: 34 and 43 passed. The
  wording test now reads `sdSizeCharge`'s docstring in SoftWire.lean (the moved text).
- `uv run python tools/trust_map.py --check`: exit 0.
- `uv run python tools/gate_collection.py --check --prebuilt`: one renamed parameter ID, recorded with a
  `Test-removed:` trailer.
- Selected tests: see "Final selected run" below.

## Seeded bugs (docs/rd-9/sc-admit-cpu/mutants.json; Lean only, no Python or Rust product code changed)

Each was applied to `lean/VE/Readings/SoftWire.lean`, then `lake build VE.Readings.SoftWireExamples` was run and the
file restored with `git checkout`.

| Id | Behaviour | Mutation | Fails |
| --- | --- | --- | --- |
| B1 | over the charge, refused before any text | `if sdAdmitWork N ≤ limit` → `if true` | SoftWireExamples.lean:35 (NSDheavy), :36, :40, :42 |
| B2 | the limit is 131,072 | `131072` → `131073` | :40 (at-limit), :34, :35, :36 |
| B3 | the charge is choices × `sdSizeCharge` | drop `(choices N.D).length *` | :35, :36, :40, :42 and 2 more |
| B4 | over 64 choices, no charge | over-64 branch reads the charge | :46 (`wideGuard767`) |
| B5 | the signed refusal text | `exceed {limit} units` → `exceed {limit}` | :35, :36, :40, :42 |

## Trust

- `uv run python tools/trust_map.py --check` against 5f756e791d4c: K +0, S +0, trusted (V) +6. All 6 lines are in
  SoftWire.lean: `sdTextsWithin`, class G[V].
- The moved definitions are class C (not trusted), so the move counts 0.
- The other new definitions: `sdAdmitWork` is C, `maxSdAdmitWork` and `sdAdmitWorkText` are G[R], and SoftWireExamples'
  definitions are T (tools/trust-classes.json).
- Recorded with `--allow`, signed "SIGNED by standing ruling R16 (DRI-RULINGS.md), sc-admit-cpu, 2026-10-18".
- FOLLOW-UPS.md row added under "## sc-admit-cpu".
- `trust_mutants`: run through mac-pytest.sh --trustmut. The first run was 11 KILLED, 2 SURVIVOR, 1 INVALID. The two
  survivors were `sdTextsWithin`'s `.take 1` and `.dropLast` on the choices. The fixture SoftWireExamples.lean:56
  (NSDbig 2 under 253 names: only the last choice fails) was added for them. The rescore at f0b8baac7b gave
  13 KILLED, 0 SURVIVOR, 1 INVALID (trust-mutants.json).

## DELTA (docs/rd-9/sc-admit-cpu/DELTA.md)

There is one row: documents of at most 64 choices over the charge go from admitted to `ResourceLimit`. Its Ruling
cell is "SIGNED by the DRI 2026-11-11 (reviews/dri-decisions-20261111-sc-admit-cpu.md item 3)". R5's tests are
listed in the row.

## Pilot bytes

0 expected: the pilots carry no soft-chain readings document over the charge. This is an estimate, not a claim.

## SIZE

- Product: 135 lines. SoftWire.lean +78/-3; SoftSupWire.lean +1/-52, of which 89 lines are the move; VE.lean +1.
- Tests: 126 lines. SoftWireExamples.lean 62, test_rd9_admit_charge.py 62, the wording test 2.
- Other hand-written: about 700 lines. Spec 26, trust tables 29, DELTA 26, cpu.md 160, mutants.json 32; bench,
  generator and script 252; this REPORT.
- Generated and output files are excluded.

## Spec re-read

- 4.1 step 5 (docs/spec/rd-9-soft-chain.md:340-344) against `sdTextsWithin`: the charge comes first, then each
  choice in canonical order; over 64, no text and no charge.
- 14.11's row and paragraph (:2459, :2492-2507) against item 3's wording of the refusal text and the figures.
- DELTA row 1 against item 3's exact Ruling cell.

## Notes for the DRI

1. **Many fixed rules: `admitSD` is over R4 below the charge, in `admitS2`** (cpu.md "Open"). Measured at
   ba8900650b, load 16-24 (`output-gap.txt`):
   - One reading set and 64 one-node fixed rules (2 choices, work 9,656): `admitS2` takes 6.50-9.19 s, and
     `admitSD` 9.19-10.34 s.
   - 128 rules: `admitS2` takes 54-56 s, then refuses with `ResourceLimit: generated norm layer …`.
   - 30 rules and 16 choices: `admitSD` takes 1.54-1.63 s, of which `admitS2` is 1.32-1.37 s (load 35-40).

   The cost grows with the number of fixed rules, both in S1's/S2a's admission (shared by every readings chain;
   measured here on the soft chain only) and in `choiceChainText`. `sdSizeCharge` does not track it: 32 one-node
   rules cost about 11 µs per unit, wide-guard rules about 1 µs. Lowering `maxSdAdmitWork` cannot help, because
   `admitS2` runs first, and 32,768 would refuse NSDbig 6.

   This is outside this item's files and deliverables (the charge is in `admitSDOf`). It is not filed as a FOLLOW-UP
   (standing override 3: no verdict is wrong). A row for a rule-count bound or a cheaper chain check in admission is
   the DRI's call. It matters for sc-11b's goal that no user-facing check passes R4.
2. sc-11wc (now blocked by this item): it should reuse `sdAdmitWork`/`maxSdAdmitWork` as item 2 says. With NSDheavy
   and heavyIn refused at admission, its route-side figures should be re-measured after this merge.
3. `readings-elaborate` on the soft chain reads `generatedPredicatesJson .enumerated D` over `choices D`. That is cut
   at 65 by `search`, so it is bounded. It was not measured here.

4. `sdTextsWithin` evaluates `choices N.D` up to three times: its length, `sdAdmitWork` and the texts. Main
   evaluated it twice. The enumeration is cut at 65 by `search`. Its cost is inside the measured figures: NSDbig 6
   took 0.15-0.18 s charged, at a higher load than main's 0.12-0.13 s.

## Next item

sc-11wc, then sc-11b (the live switch) once sc-11c and sc-11wc merge.

## Self-review against BUILDER-CHECKLIST

1. Typed and contained: PASS. No relay or schema changed. The refusal is an existing `error` row, pinned through the
   service by `tests/test_rd9_admit_charge.py`.
2. Every deliverable built: PASS. Step 1 is cpu.md. Step 2 is SoftWire.lean with fixtures NSDheavy and heavyIn
   within 1 s (output-charged.txt). The at-limit document took 0.57-0.61 s.
3. Tests can fail: PASS. Seeded bugs B1-B5 (mutants.json); trust-mutants.json has 0 survivors.
4. Python, Lean and Rust agree: N.A. No Python or Rust decision was changed, and Lean's text is relayed as is.
5. R8 binding: N.A. No field and no relay was added.
6. Gate evidence on the final HEAD: PASS. The final selected run is on committed code; the chain gate runs on
   the final HEAD.
7. No unsigned item: PASS. The DELTA row is SIGNED by item 3, and no signature is reserved.
8. Every user-visible change is in DELTA: PASS. DELTA row 1; the move and the proof change are not visible
   (`#guard`s unchanged).
9. Test selection: PASS. `tools/repo_map.py file lean/VE/Readings/SoftWire.lean` lists the readings tests, and
   the new test imports the readings route.
10. Statements say what is claimed: PASS. `admitSDOf_texts` states only the passing direction, and the refusal is
    pinned by `#guard`s :35-:42.
11. Budgets fail closed: PASS. Over the charge the answer is `ResourceLimit`, never an accept (B1, :35).
12. No CPU regression: PASS. The charge reads `sdSizeCharge` once per admission: NSDbig 6 took 0.15-0.18 s
    against 0.12-0.13 s on main, at load 27-41 against 15-20 (output-charged.txt, output-main-step1.txt).
13. Test-removed trailer: PASS. The renamed parameter ID of the wording test is in this commit's trailer
    (`gate_collection.py --check --prebuilt`).
14. Both directions: PASS. Refused: :35, :36, :42. Admitted: :38, :40, :44, :46, and the wire test's within-charge
    cases. Spec re-read is listed above.
15. No overclaim: PASS. The open many-rule gap is stated in cpu.md, the spec and Notes 1. No cut: PASS. The limits
    are charged before work: PASS (:35, B1). Every new check can fail: PASS (B1-B5, trust-mutants.json).
