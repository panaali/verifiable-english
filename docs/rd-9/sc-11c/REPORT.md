# sc-11c report: the soft runners on the superposed route (rd-9 14.3, 14.11, 14.13)

**No DRI signature is reserved.** The soft row (14.3 "The soft row") moved to **sc-11cb**, signed by the DRI
(reviews/dri-decisions-20261110-sc-11c.md item 1); sc-11cb comes before sc-11b, which now waits for sc-11, sc-11w,
sc-11c and sc-11cb. The runners are reached only from `SoftSupRunExamples.lean`; the dispatch (`runSDKind`,
`runS2ND`) is unchanged, so no answer changes: no DELTA row, pilot bytes 0 (14.13). No 14.8 statement is added or changed.

## Plan rows and directives

| Row (task "Deliver") | Delivered |
| --- | --- |
| (1) `readings-conflict`, `-certificate`, `-model` on a superposed soft document | `lean/VE/Readings/SoftSupRun.lean`: `sdCaseOf` admits (`admitSDOf`) and routes once; `SDCase` holds `sup N.D`, `supU N`, `fill (supU N)`, the slot, `softXL N (sup N.D).1`, `supX`, `Fill_T`, the targets, the checked choices, `sharedEnvSD N` and the model vocabulary, each computed once; `sdConflictCore` (certificates, `sdWitness`), `sdCertificateCore`, `sdModelRun`, `runSDSup` read only the case |
| (1) each answer satisfies its `readings_wire_sd_*_sound` | `SDCase.free_eq`, `premises_eq`, `model_eq`, `local_eq`, `slotX_eq`, `taken_eq` (each check is the approved definition on the case's values); `free_sound` and `premises_check` apply `readings_wire_sd_conflict_sound` and `supCertificateCheckSD` to the case's `SupReplaySD` |
| (1) the certificate runner binds to `premisesX` (D14) | `bindCertX` over `premisesX (supU N) (slotUnder N.D A ++ supX N) (sup N.D).2` and the case's own premises, checked on `SDCase.premises` (= `premisesX`, `premises_eq`) |
| (2) the verdict scopes | `sdScope`: each piece on the case's values; `usedLabels` per accepted piece over the slot, `supX` and `Fill_T` (one replay each); `labelImage` once per scope, only when a piece was accepted; soft premises shown by their choice labels (`shownWith_eq`: = `sdShown`) |
| (2) the soft row | **sc-11cb**, SIGNED by the DRI (reviews/dri-decisions-20261110-sc-11c.md item 1); `SDCase` and `sdCaseOf` stay public for it |
| (3) W-13's "a conflict answer in one proof" on `NSDbig 8` | SoftSupRunExamples.lean:131: 256 checked choices, one conflict check, CONFLICT naming the all-strict choice; :135 `NSDbig 10` refused with `runSDKind`'s text |
| (3) the read-once rule (W-14) on `NSD4a` | :106: conflict, certificate and model evidence under `rs1:1`, then a conflict piece under `[]`: 1 admission, 1 route check, 3 conflict checks, 2 replays, 1 label image; :107 the shown labels |
| (3) a refusing case per runner | conflict :122 (no candidate), :123 (witness tuple); certificate :146 (`supX` left out of the binding); model :153 (an `unsaid__` table, F-SD8): today's decoder texts, compared whole |
| 14.11 "charged before use" | the route reads the count, then the work limit, then (past 64 choices) the per-choice texts (`sdCaseOf`'s `if`, left to right); at most 64 choices the texts are admission's (`sdCheck_of_admitted`) |

Certificates in the fixtures: `NSD4a` under `rs1:1` and `NSDq` under `[]` are traces Python's prover found once
(`prove_entailment`, `_background=False`) on the premises Lean regenerates for the superposed document; Lean checks
them in every build. `NSDbig 8`'s `x_required` targets are not certified (the all-strict choice conflicts), so W-13's
answer is a witness: one model check over the superposed document.

**Size** (`git diff --numstat $(git merge-base HEAD main)`, generated files excluded): see "Measurements".

## Measurements

UNFILLED

## Seeded bugs (`docs/rd-9/sc-11c/mutants.json`)

All Lean (no Python or Rust product code changed): M1 a scope that re-admits per piece (:106), M2 `labelImage` for a
scope with no accepted piece (:106), M3 the certificate bound without the slot (:142, :106, :107), M4 the conflict
check run per choice on `NSDbig 8` (:131), M5 `Fill_T` replayed twice (:158), M6 `shownWith` showing the superposed
label (`shownWith_eq` fails), M6b the scope showing superposed labels (:107). Each KILLED.

## Spec re-read

UNFILLED

## Self-review against BUILDER-CHECKLIST

UNFILLED
