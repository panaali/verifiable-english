# sc-11c report: the soft runners on the superposed route (rd-9 14.3, 14.11, 14.13)

**No DRI signature is reserved.** Status: built. Open: the soft row is **sc-11cb** (SIGNED, reviews/dri-decisions-20261110-sc-11c.md
item 1), before sc-11b (blocked by sc-11, sc-11w, sc-11c, sc-11cb). The runners are reached only from `SoftSupRunExamples.lean`;
`runSDKind` and `runS2ND` are unchanged, so no answer changes: no DELTA row, pilot bytes 0 (14.13). No 14.8 statement changes.

## Plan rows and directives

| Task row | Delivered (SoftSupRun.lean; fixtures SoftSupRunExamples.lean:line) |
| --- | --- |
| (1) three runners | `sdCaseOf` admits (`admitSDOf`) and routes once and stores `SDCase`: `sup N.D`, `supU N`, `fill (supU N)`, slot, `softXL`, `supX`, `Fill_T`, targets, backgrounds, `elaborate`, checked choices, `sharedEnvSD N`, model vocabulary, canonical environment; `sdConflictCore` (`sdWitness`), `sdCertificateCore`, `sdModelRun`, `runSDSup` read only the case |
| (1) `readings_wire_sd_*_sound` applies | each reported check is the approved definition on the case's values: `SDCase.free_eq`, `premises_eq`, `bind_eq`, `model_eq`, `local_eq`, `slotX_eq`, `taken_eq`, `labels_eq`; `free_sound`, `premises_check` apply them to the case's `SupReplaySD`. Not built: a theorem from a runner's returned JSON to the hypotheses (the decoders return no proofs, as RD-6b's) |
| (1) D14 | bound by `SDCase.bind` (= `bindCertX` over `premisesX (supU N) (slotUnder N.D A ++ supX N) (sup N.D).2` and the request's premises), checked on `SDCase.premises` (= `premisesX … ((sup N.D).2 ++ Γ)`); :195 accepted, :201 and :202 refused |
| (2) verdict scopes | `sdScope`: one conflict check per scope (`sdFree`); `labelImage` once, at the first accepted piece (`SDCase.images`, `images_shown`); per accepted piece `usedOf` (its labels replay its proofs: `usedOf_replays`; a full replay is the piece's own check: `replay_query`, `replay_conflict`), shown by `relabel` (`relabel_shown`: `sdShown`) |
| (2) the soft row | **sc-11cb** (SIGNED, item 1 above); `SDCase`, `sdCaseOf` stay public for it |
| (3) W-13 | :180 `NSDbig 8` (256 choices) admitted and routed once; CONFLICT in one check (all-strict choice), also as a scope piece; :188 `NSDbig 10` refused with `runSDKind`'s text |
| (3) W-14 | :121, :124: four scopes of `NSD4a` with conflict, certificate, countermodel, unsat and model evidence: 1 admission, 1 route check, 3 conflict checks, 2 replays, 3 label images (none for the scope without an accepted piece) |
| (3) refusals | conflict :157, :158, :180; certificate :201, :202; model :214; another kind :217; texts compared whole |

Both directions: CONFLICT-FREE :150 / UNKNOWN :155; accepted :195 / not :199; model valid :206 / not (atom :208, soft premise
by its choice label :210, `localFree` :180); `Fill_T` in `reading_premises` :147 and in the shown labels :134; three encoded :138.

Not built (for sc-11b's verdict answer): `SupScope`'s English fields (`mentions`, `coherence`, `witnessSummary`, `missing`, each
note's `gaps` and classification) stay at their defaults; RD-7's helpers read S2a's `sup D`. W-1a: Python's trace for `NSD4a`'s
conflict under `rs1:1` also uses the exception premise, so its shown labels are `[sufficient:0, coherence]` (:124), not W-1a's
`[coherence]`; the 14.6 differential (sc-11b) compares the routes.

Certificates: `NSD4a` under `rs1:1` (targets; W-1a's query) and `NSDq` under `[]` are traces Python's
`prove_entailment(env, premises, φ, _background=False)` found once on premises Lean regenerated (a scratch `#eval` wrote
`bgb ++ slotX A ++ Fill_T` or `SDCase.premises A1 []` and their predicates); Lean checks them on every build.

## Measurements

- **Size** (`git diff --numstat a3454b6ba`, generated files and tool evidence out): SoftSupRun.lean 427, SoftSupRunExamples.lean
  220, VE.lean 2, mutants.json 17, this report ~70: ~736 (limit ~750, reviews/dri-decisions-20261110-sc-11c-size2.md); side
  tables trust-classes.json 160, assurance-manifest.json 31, trust-baseline.json 7 (SIGNED, same file).
- **Trust** (`tools/trust_map.py --check` against a3454b6ba598): PASS; K +0, S +0, tied +66, trusted +65, all SoftSupRun.lean
  (`sdScope` G[V]; `sdShared`, `sdAssumed`, `sdModel` D[V]); runners and route C, counters G[R], fixtures T. Allowance "SIGNED
  by standing ruling R16 (DRI-RULINGS.md), sc-11c, 2026-10-18" (V +84, recorded before the ties); FOLLOW-UPS.md "## sc-11c".
  Trust mutants (docs/rd-9/sc-11c/trust-mutants.json, `mac-pytest.sh --trustmut`, HEAD 414446583): 107 KILLED, 0 SURVIVOR,
  0 UNKNOWN (three earlier sweeps' survivors fixed by the ties and fixtures above).
- **Build**: `lake build` PASS; `python3 lean/audit.py` PASS (827 files, 9326 theorems, standard axioms only); the fixtures
  build in 46 s (`NSDbig 8` read once); `tools/check_lean_imports.py`: kept (the fixtures declare layer 4: they read `Readings.Run`).
- **Statements**: `tools/check_rd9_sc1_statements.py`: "SC-11 labels PASS: 11 exact", "SC-11 wire PASS: 15 exact", 0 pending; `tests/test_rd9_statements.py`: 43 passed. **Selected tests**: SELECTED.

## Seeded bugs (`docs/rd-9/sc-11c/mutants.json`, all Lean, each KILLED)

M1 a scope re-admits per piece (:121); M2 `labelImage` at a scope's first piece, accepted or not (:121); M3 the binding under
`[]` (:195); M3b the check without `supX` (:195); M4 one check per choice on `NSDbig 8` (:180); M5 `Fill_T` replayed twice
(:134); M6 `shownWith` and M6b `relabel` show the superposed label (:124); M7 `valid` without `localFree` (:180); M8 a
superposed label in `first_failing` (:210); M9 a conflict check per piece (:121); M10 another kind answered as a model (:217).

## Spec re-read

- 14.3 (docs/spec/rd-9-soft-chain.md:2039-2046): order slot, atoms, `supX`, `Fill_T` (`slotX`, `free`, `premises`);
  `conflictFreeCheckX` per target (`free_eq`); `bindCertX`, refused when the binding drops or adds a premise (:201, :202);
  `modelCheckX` with `filling`, an `unsaid__` table refused (:214), `localFree` (:180); queries over `sharedEnvSD N`.
- 14.11 (:2455-2460): one search (`checked`, `choices_isEmpty`); texts at most 64 from admission; values once per case;
  `labelImage` once per scope; `usedLabels` per accepted piece; members decoded once (one conflict decode per scope).
- 14.9 W-13 (:2422), W-14 (:2423); 14.13 (:2496): reached only from examples.

## Self-review against BUILDER-CHECKLIST

1. N.A.: no relayed answer (nothing dispatches here; sc-11b's relay rows). 2. PASS: rows above; the soft row moved by DRI
ruling. 3. PASS: twelve seeded bugs KILLED; trust mutants 107 KILLED. 4. N.A.: no Python or Rust product code. 5. N.A.: no
relay binding (sc-11b). 6. PASS: the chain gates the final HEAD. 7. PASS: R16 allowance and FOLLOW-UPS row; no DELTA; no
reserved signature. 8. PASS: no user-visible change (:188 compares with `runSDKind`). 9. PASS: SELECT9. 10. PASS: the ties'
theorems break under M5, M6, M6b; statements PASS (11 + 15 exact); audit PASS. 11. PASS: over a limit the route refuses before any choice's text
(:188); a refused piece is no verdict (:124). 12. PASS: `NSDbig 8` read once in the fixtures (46 s, was 96 s). 13. PASS: no
test removed. 14. PASS: both directions above; spec re-read above. 15. PASS: overclaims narrowed (not built: JSON-to-hypothesis
theorems, the English scope fields); no silent cut (DRI rulings); every new check has a seeded bug; limits before work.

SELF-REVIEW: 2 A, 10 B, 7 C; fixed SRFIX. Second review: SR2.
