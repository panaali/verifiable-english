# Counts and proportions in Lean (`lean/VE/Cardinality/*`)

Specification: [docs/spec/quantities.md](../docs/spec/quantities.md) sections 3.2 to 3.9 (statement spec, draft 3)
and [docs/spec/quantities-PLAN.md](../docs/spec/quantities-PLAN.md) batch QT-A1. This file lists the files, the
theorems proved so far in plain words, the fixtures and every difference from the spec. `lean/audit.py` audits every
theorem: no unfinished proof, only `propext`, `Classical.choice` and `Quot.sound`. No existing Lean source changed;
`VE.lean` gained one import and `VE/Audit.lean` its generated entries.

QT-A1 is delivered in two parts. This item (qt-a1) holds the syntax, the meaning, admission, regions, erasure, the
finite countermodel check and the theorems that do not need erasure's soundness. **qt-a1b** holds the soundness
theorems (listed at the end).

## Files

| File | Contents |
|---|---|
| `Syntax.lean` | `Body`, `Rel`, `CountAtom`, `Cmp`, `Proportion`, `CFormula`, `CEnv`, `regionPrefix`, `CEnv.WellFormed`; admission: `BodyTyped`, `Admitted` (the specification), `bodyCheck`, `CFormula.admits` (the check); `bodyCheck_iff`, `admits_iff`, `admits_sound`, `admits_complete` |
| `Semantics.lean` | the meaning without erasure: `Body.holds`, `HasCount`, `Rel.holds`, `Cmp.holds`, `Counts`, `CountAtom.holds`, `Proportion.holds`, `CFormula.holds`, `Admissible`, `CEntails` |
| `Regions.lean` | counted sorts and recognised universal statements (`bodyOfQ?`, `universalsOf`, `countedSorts`, `countedUniversals`), `predsOn`, `regions`, `Body.inRegion`, `regionConst`, `regionTable`, `CEnv.elab`, `regionBody`; the problem limits P1 and P2 (`problemLimits`) |
| `Erase.lean` | `regionSum`, the erasure of counts and proportions (`CFormula.erase`), `nonnegPremises`, `bridgePremises`, `erasedProblem`; `withRegions` (region constants read as region sizes); the finite countermodel check: `Body.evalFin`, `countFin`, `withRegionsFinite`, `refutesC` |
| `Theorems.lean` | `hasCount_exists_unique`, `hasCount_unique`, `nonneg_hold`, `proportion_holds_iff`; W6a's four counting forms as count atoms (`atLeastAtom`, `atMostAtom`, `exactlyAtom`, `nOfMFormula`) and `Body.toFormula` |
| `Examples.lean` | the fixtures as `#guard` lines and `example` proofs (below) |

## Theorems in plain words

* **`admits_sound`, `admits_complete`** (3.4): the executable admission accepts a statement exactly when the
  independent specification `Admitted` holds: counts and proportions name a declared finite sort, every body atom is
  a declared unary predicate of that sort, a proportion's fraction is between 0 and 1 with a positive denominator,
  and W6a parts are W6a-admitted.
* **`hasCount_exists_unique`** (3.6): on an admissible structure, every body has exactly one count on a declared
  finite sort, so a count atom and its negation mean what they say.
* **`nonneg_hold`** (3.6): where region constants are region sizes, every premise `0 ≤ n` holds.
* **`proportion_holds_iff`** (3.6): a proportion holds exactly when its population is nonempty and its share
  compares with the fraction as written.

## Fixtures (`Examples.lean`)

`holdsFin` is the test oracle: it counts each body directly on a finite model, with no regions; `agrees` compares it
with every erased formula on `withRegionsFinite` and checks every region and bridge premise there.

FA1 (news S3: admission; regions `…__00` to `…__11`; two bridges; 10 erased premises; 91 nodes; the certificates for
"exactly 16" and "at least 16", found by Python's untrusted search and replayed by the frozen order checker, and
refused without the exclusion premise), FA1b (the countermodel (1, 1, 15, 1): `refutesC`, meaning and erasure agree,
premises true and conclusion false; with the exclusion premise it is no countermodel), FA1c ("at least 16" with "at
most 2" refuted by (1, 0, 17, 0)), FA2 (each count atom against `VE.Time.atLeast`, `atMost`, `exactly` and `nOfM` on
models of 6, 7 and 8 objects), FA3 ("exactly 16 of the 18" admitted), FA8 (hostile admission; the limits at 6 and 7
predicates and at 8 and 9 counted sorts; a universal statement with seven predicates and no count makes no region),
FA9a (a declared constant spelled like a region constant: erasure overwrites it, which is why `WellFormed` is a
hypothesis), FA9c and FA10 (an empty population: "at least 1 in 1,000" false as a proportion, true as a bare count
atom; the rows of 9.1), and `example` proofs of the meaning on a two-user structure (`Admissible`, `HasCount`,
`CountAtom.holds`, `Proportion.holds`, `CEntails`, `WellFormed`).

## Differences from the spec

* **The ratio constructors are QT-A2's.** `roundsTo`, `percentOf`, `percentRoundsTo`, the operand type `CTerm` and
  its typing (`CTermTyped`, `CTerm.Denotes`, `CTerm.tagOf`, `ratioTyped`), `admittedRules` and their erasure
  (`roundingQ`) are added by QT-A2 with its agreement theorem, exactly as spec 3.2 to 3.5 and 3.8 write them. Every
  other definition and statement here is the spec's, unchanged.
* **Problem limits** P1 and P2 of spec 4.2 are `problemLimits`, so the core can be tested against them; P3 (W6a's
  aggregate limit) needs W6a's admissions and comes with the wire (QT-A3).
* Added helper theorems, not in the spec: `bodyCheck_iff`, `admits_iff`, `hasCount_unique`, `exists_nodup_filter`,
  `nodup_length_eq`.

## qt-a1b: the soundness theorems

`withRegions_admissible`, `bridge_hold`, `erase_iff`, `cardinality_elab_sound`, `erasedProblem_admitted`,
`count_atLeast_agree`, `count_atMost_agree`, `count_exactly_agree`, `count_nOfM_agree` and `refutesC_sound`, as spec
3.6, 3.7 and 3.9 state them. Until they are proved, no route uses erasure or `refutesC`: an erased problem's W6a
certificate says only that the erased problem is entailed, not yet the counting problem.
