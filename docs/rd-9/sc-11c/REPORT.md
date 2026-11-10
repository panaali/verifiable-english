# sc-11c report: the soft runners on the superposed route (rd-9 14.3, 14.11, 14.13)

**No DRI signature is reserved.** Status: built; HEAD in `git log -1`; open: the soft row is **sc-11cb** (SIGNED, DRI
reviews/dri-decisions-20261110-sc-11c.md item 1), which comes before sc-11b (now blocked by sc-11, sc-11w, sc-11c,
sc-11cb). The runners are reached only from `SoftSupRunExamples.lean`; `runSDKind` and `runS2ND` are unchanged, so no
answer changes: no DELTA row, pilot bytes 0 (14.13). No 14.8 statement is added or changed.

## Plan rows and directives

| Task row | Delivered |
| --- | --- |
| (1) the three runners | `SoftSupRun.lean`: `sdCaseOf` admits (`admitSDOf`) and routes once and stores `SDCase` (`sup N.D`, `supU N`, `fill (supU N)`, the slot, `softXL`, `supX`, `Fill_T`, the targets, both backgrounds, `elaborate`, the checked choices, `sharedEnvSD N`, the model vocabulary, the canonical environment); `sdConflictCore` (certificates; `sdWitness`), `sdCertificateCore`, `sdModelRun`, `runSDSup` read only the case |
| (1) `readings_wire_sd_*_sound` applies | each check an answer reports is the approved definition on the case's values: `SDCase.free_eq` (`conflictFreeCheckX`), `premises_eq` (`premisesX`), `bind_eq` (`bindCertX`), `model_eq` (`modelCheckX`), `local_eq`, `slotX_eq`, `taken_eq`; `free_sound` and `premises_check` apply them to the case's `SupReplaySD`. Not built: a theorem from each runner's returned JSON to the theorem's hypotheses (the decoders return no proofs, as RD-6b's runners) |
| (1) D14 | bound by `SDCase.bind` (= `bindCertX` over `premisesX (supU N) (slotUnder N.D A ++ supX N) (sup N.D).2` and the request's own premises) and checked on `SDCase.premises` (= `premisesX … ((sup N.D).2 ++ Γ)`) |
| (2) verdict scopes | `sdScope`: one conflict check per scope shared by its pieces (`sdFree`); `usedLabels` per accepted piece over the slot, `supX` and `Fill_T`; `labelImage` once per scope, only when a piece was accepted; soft premises shown by choice labels (`shownWith_eq`: `sdShown`) |
| (2) the soft row | **sc-11cb** (SIGNED, item 1 above); `SDCase` and `sdCaseOf` stay public for it |
| (3) W-13 | SoftSupRunExamples.lean:154: `NSDbig 8` (256 choices) admitted and routed once; CONFLICT in one check, naming the all-strict choice; :161 `NSDbig 10` refused with `runSDKind`'s text |
| (3) W-14 | :114, :115: `NSD4a` with conflict, certificate and model evidence under `rs1:1`, then conflict and a refused witness under `[]`: 1 admission, 1 route check, 2 conflict checks, 2 replays, 1 label image |
| (3) refusals | conflict :134, :135, :154; certificate :174, :175; model :187; another kind :190; texts compared whole |

Not built here (named for sc-11b): `sdScope` leaves `SupScope`'s English fields (`mentions`, `coherence`,
`witnessSummary`, `missing`, each note's `gaps` and classification) at their defaults; RD-7's helpers read S2a's `sup D`.
W-1a: Python's trace for `NSD4a`'s conflict under `rs1:1` uses the exception premise too (:115), so the shown labels
are `[sufficient:0, coherence]`, not W-1a's `[coherence]`; the 14.6 differential (sc-11b) compares the routes.

Certificates: `NSD4a` under `rs1:1` (targets, and W-1a's query), `NSDq` under `[]`: traces Python's
`prove_entailment(env, premises, φ, _background=False)` found once on the premises Lean regenerates (a scratch
`#eval` wrote `bgb ++ slotX A ++ Fill_T`, or `SDCase.premises A1 []`, with the formulas' predicates); Lean checks them on
every build. `NSDbig 8`'s `x_required` targets are not certified (that choice conflicts), so W-13's answer is a witness.

## Measurements

- **Size** (`git diff --numstat a3454b6ba`, generated files out): SoftSupRun.lean 363, SoftSupRunExamples.lean
  ~190, VE.lean 2, mutants.json 17, this report ~75; side tables tools/trust-classes.json 115, ve/assurance-manifest.json
  31. ~650 without the side tables is SIGNED (reviews/dri-decisions-20261110-sc-11c-size.md); the side tables: asked
  (inbox/dri 20261110T181658Z).
- **Trust** (`tools/trust_map.py --check` against a3454b6ba598): K +0, S +0, tied +36, trusted +84, all
  SoftSupRun.lean (`sdScope`, `sdProofs` G[V]; `sdShared`, `sdAssumed`, `sdModel`, `SDCase.labels` D[V]); runners C,
  counters G[R], fixtures T. Allowance "SIGNED by standing ruling R16 (DRI-RULINGS.md), sc-11c, 2026-10-18"; FOLLOW-UPS.md
  row "## sc-11c". Trust mutants: UNFILLED.
- **Build**: `lake build` PASS; `lean/audit.py` PASS (827 files, only the standard axioms); SoftSupRunExamples.lean
  builds in 46 s (`lake build VE.Readings.SoftSupRunExamples`, after folding `NSDbig 8` into one case).
- **Statements**: UNFILLED. **Selected tests**: UNFILLED.

## Seeded bugs (`docs/rd-9/sc-11c/mutants.json`, all Lean, each KILLED)

M1 a scope re-admits per piece (:114); M2 `labelImage` for a scope with no accepted piece (:114); M3 the binding
under `[]` (:168); M3b the check without `supX` (:168); M4 one check per choice on `NSDbig 8` (:154); M5 `Fill_T`
replayed twice (:121); M6 `shownWith` shows the superposed label (`shownWith_eq` fails) and M6b the scope does (:115);
M7 `valid` without `localFree` (:154); M8 a superposed label in `first_failing` (:183); M9 a conflict check per piece
(:114); M10 another kind answered as a model (:190).

## Spec re-read

- 14.3 order (docs/spec/rd-9-soft-chain.md:2039): slot, atoms, `supX`, `Fill_T`: `SDCase.slotX`, `free`, `premises`.
- 14.3 certificates (:2042-2044): `conflictFreeCheckX` per target (`free_eq`); `bindCertX` and diagnostic 11 on a
  binding that leaves a premise out or adds one (`bind_eq`; :174, :175).
- 14.3 models (:2044-2045): `modelCheckX` with `filling`, an `unsaid__` table refused (:187), `localFree` (`valid`, :154).
- 14.3 queries (:2046): typed over `sharedEnvSD N` (`sdShared` on `SDCase.envQ`).
- 14.11 (:2455-2460): one search (`checked`, `choices_isEmpty`); texts at most 64 from admission; values once per case;
  `labelImage` once per scope; `usedLabels` per accepted piece; members decoded once (one conflict decode per scope).
- 14.9 W-13 (:2422), W-14 (:2423); 14.13 (:2496): reached only from examples.

## Self-review against BUILDER-CHECKLIST

UNFILLED
