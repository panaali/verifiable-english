# ps-2a: the readings block and PS-E1's candidate table (spec 4.7, Wire.lean) (build report)

No DRI signature is reserved in this item. There are no DELTA rows (DELTA.md): the item adds only Lean that no route
reads. Trusted growth is +102 (K +0, S +59, V +43), covered by standing ruling R16 (see "Trust").
Status: built to the cut the DRI signed: deliverables (1) and (2) (reviews/dri-decisions-20261109-ps-2a.md item 1).
`admit`, A1-A28, the 19 `admit_*` statements and Run.lean go to ps-2ab (see "Cut").
Open: the chain runs the full gate on the final HEAD. Next item: ps-2ab.

Feature item ps-2a (PS-2a's second part, after ps-2aa; plan `docs/spec/presupposition-PLAN.md:847-863`, 4.6
`:498-520`; spec `docs/spec/presupposition.md` 4.7). Branch `feature/ps-2a`, merge base 098dbe688 (main's tip at
launch). Command outputs: `evidence/tests.txt`.

## Preconditions

- **Statement gate.** PASSED, as the task states. ps-2aa's probe form, rerun over Wire.lean (`evidence/tests.txt`):
  39 declarations, each compared with the stub's 4.7 declaration of the same name and with spec 4.7's lean blocks
  (`presupposition.md:841-1069`), comments stripped and whitespace normalised. 38 are equal. `candidateTable` differs
  from both, and deliverable (2) requires that: the stub and the spec hold the empty placeholder until PS-E1 fills it
  (spec `:1218`, section 6).
- **ps-2aa merged.** Wire.lean on main has every type `admit` needs except the cut readings block. This item
  restores that block, so ps-2ab finds `RReading` to `PDoc` in place.
- **Synthesis round 2.** Item 1 (no mode; the report is a layer field): kept. The item adds no mode, schema or relay.
  Item 5 (the RF row) and DEC 10 (a heading presupposition is the heading unit's `.layer` assumption) belong to
  `admit` and the A24 fixture, so they move to ps-2ab. This item implements none of them.
- **Layers.** `tools/check_lean_imports.py`: "Lean layer graph kept (790 modules, 18 reviewed legacy edges)". Wire.lean
  now also imports `VE.Presupposition.Rules` (for `conditionNode`), as ps-2aa's full version did. I made no
  `layer_policy` edit.
- **In-flight overlap.** No branch in flight touches `lean/VE/Presupposition/`. Shared files: `tools/trust-classes.json`
  (added entries only), `docs/trust-baseline.json` (one allowance) and generated inventories.

## Plan rows delivered

| Row (task "Deliver") | Commit | Evidence |
|---|---|---|
| (1) `RContent`, `RReading`, `UContent`, `DocUnit`, `PDoc`, `env`, `unitOf`, `unitContent`, `unitAsserted`, `unitReadings`, `nodeCertificate`, `premisesBefore`, `claimReading`, `ruleReading`, `emitted`, `aliasesOf`, `expectedReadings` (ps-2aa's 9cdd78473 text, copied) | 2412b516f | Wire.lean:106-168, :187-220 |
| (1) the 7.1 `expected` row; S12 and S26 reading shapes; S25; S27's alias half (seeded bug 2); S17; the rule-act readings (9cdd78473's guards, copied, renamed where ps-2aa's later fixtures took the name) | 2412b516f, this branch | Examples.lean:614-712 |
| (2) `candidateTable` = `docs/research/presupposition-E1/candidate-table.json` cell by cell; `tableOk` holds; one guard per row and one for an unknown row | 2412b516f | Wire.lean:82-88; Examples.lean:497, :511-518 |
| (3) `admit` + A1-A28 | cut to ps-2ab | "Cut" |
| (4) Run.lean | cut to ps-2ab | "Cut" |
| (5) the 19 `admit_*` statements | cut to ps-2ab | "Cut" |

Guards in Examples.lean: 213 → 251 (`grep -c '^#guard'`). ps-2aa's guard `!carrierAllowed candidateTable chk12 .assumed`
was a fact about the empty table. It now reads `carrierAllowed … .assumed && !carrierAllowed … .conditioned` (:532).

## Cut (reviews/dri-decisions-20261109-ps-2a.md item 1, SIGNED by the DRI)

I measured at the (2) boundary with `tools/trust_map.py --check`: trusted +102 (S +59, D[V] +25, G[V] +18, K +0). The
readings block alone is 97 of these. ps-2aa's "~47" was a partial measure; its REPORT's own numbers give 217 - 120 = 97.
That leaves 48 of R16's 150 lines. Untied, `admit` (spec 4.7's five steps) cannot fit in 48. The task's pre-approved
seam cuts only (5) and then (4), so I asked the DRI (msg.sh, 2026-11-09T10:18Z). The DRI ruled that ps-2a ends at (1)+(2).
**ps-2ab** takes (3) `admit` with A1-A28, (5) the 19 statements, which tie `admit` so its lines leave the trusted
count, and (4) Run.lean last. ps-2ab has its own seam: Run.lean to ps-2ac. The M2 seeded bug and the "admit drops one
emitted candidate" bug move with `admit`. Item 2 of the same decision confirms `admit := admitWith candidateTable
<fixed inputs>`, which is spec 4.7 step 5's text (`:1105-1108`), for ps-2ab.

## Deviations

- **`candidateTable` is copied by hand from PS-E1's JSON, not generated.** Spec section 6 (`:1333`) says a generator
  writes it. The four guards at Examples.lean:514-518 fix every cell: definite, plural, generic and an unknown row. A
  change to the JSON is not caught automatically. The generator is listed in FOLLOW-UPS.md "## ps-2a".
- **Guards renamed on copy.** ps-2aa's later fixtures took `repR` and `chkR` (a rule-name argument). The copied
  rule-act guards use `repRR` and `chkR "…" "r1"`. The copy of `unitModes rep26 …` is dropped, because ps-2aa's
  `rep26` (with `chk12`) already guards `unitModes` (:552).

## Seeded bugs (Lean only; this item changes no Python or Rust product code)

`mutants.json` lists 36 hand mutants, at least one per new trusted definition (the five types included), with `file`,
`find`, `replace` and `test`. I applied each alone, built `VE.Presupposition.Examples` and restored the file. All 36
fail (`evidence/tests.txt`). The first run left 3 survivors: a lookup by name or unit that the fixtures never put
second. Two fixtures kill them: a foreign-unit conditioned obligation (Examples.lean:643-645) and a foreign rule
first in the tree (:680-685). The claimed behaviours:

| Id | Behaviour | Mutant | Fails |
|---|---|---|---|
| M-aliasesOf-shallow | R-D1, S27 (task seeded bug 2): in place aliases conditioned only at a shallow frame | drops `decide c.frame.shallow` | Examples.lean:636, :646, :649, :651 |
| M-emitted-inPlace | R-D1, R-4: in place is never a reading of its own | keeps in place in `emitted` | :622, :624, :626, :627 |
| L-premisesBefore-strict | S17: premises strictly before the unit | every unit | :705 |
| L-candidateTable-generic | PS-E1's open cell | generic's consequent loses unconditional | :516 |

## Trust

`tools/trust_map.py --check` against 098dbe6886d6: Wire.lean trusted +102 (S +59, D[V] +25, G[V] +18), K +0;
Examples.lean is T (its new fixtures are classed T) and unclassified +0. Classes: S for `RContent`, `RReading`,
`premisesBefore`, `claimReading`, `ruleReading`, `emitted`, `aliasesOf`, `expectedReadings` (and `candidateTable`,
already S); D[V] for the document's shapes `UContent`, `DocUnit`, `PDoc`; G[V] for the accessors `env`, `unitOf`,
`unitContent`, `unitAsserted`, `unitReadings`, `nodeCertificate`. The allowance in `docs/trust-baseline.json` is
"SIGNED by standing ruling R16 (DRI-RULINGS.md), ps-2a, 2026-10-18". The "## ps-2a" ties-pass row is in FOLLOW-UPS.md.

## Size, bytes, evaluators

- **Size.** `git diff --numstat 098dbe688`, without generated files: see "Final checks".
- **Pilot bytes.** 0: no route reads Wire.lean yet.
- **Evaluators.** None added. `expectedReadings` maps over one cell (at most 5 candidates). `premisesBefore` walks the
  unit list once. Neither is a runner or a mode. Limits on `admit` are ps-2ab's (step 1).

## Spec re-read

- 4.7 definitions against `presupposition.md:941-1069`, by the probe (38/39 equal; `candidateTable` as above).
- 7.1 S12 `:1369` (two readings; conditioned's aliases `[inPlace]`; no in-place reading: :622-627), S25 `:1370`
  (:635-636), S26 `:1371` (in place T, asserted F, assumed premise `q` F: :639-642), S27 `:1372` (no in-place reading,
  no alias: :649-652). `expected` (7.1, one-candidate cell gives one reading; heading none: :656-663).
- Section 6 `:1324-1335` against `candidate-table.json` (candidate order as listed; `tableOk` holds: :497).

## Final checks

PENDING (filled after the self-review and the once-only checks).

## Self-review against BUILDER-CHECKLIST

PENDING.

FOLLOW-UP: ps-2ab admit, A1-A28, the 19 admit_* statements and Run.lean (PS-2a part 3)
