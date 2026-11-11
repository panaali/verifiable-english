# sc-11c report: the soft runners on the superposed route (rd-9 14.3, 14.11, 14.13)

**No DRI signature is reserved.** Status: built. Open: the soft row and the scope's English fields are **sc-11cb** (SIGNED:
reviews/dri-decisions-20261110-sc-11c.md item 1, -sc-11c-asks3.md item 1), before sc-11b; W-1a is OPEN for sc-11b (asks3 item 2).
The runners are reached only from `SoftSupRunExamples.lean`; `runSDKind` and `runS2ND` are unchanged, so no answer changes: no
DELTA row, pilot bytes 0 (14.13). No 14.8 statement changes.

## Plan rows and directives

| Task row | Delivered (SoftSupRun.lean; fixtures SoftSupRunExamples.lean:line) |
| --- | --- |
| (1) three runners | `sdCaseOf` admits (`admitSDOf`) and routes once, then stores `SDCase`: `sup N.D`, `supU N`, `fill (supU N)`, slot, `softXL`, `supX`, `Fill_T`, targets, backgrounds, `elaborate`, checked choices, `sharedEnvSD N`, model vocabulary, canonical environment; `runSDSup` (`SDKind`: conflict, certificate, model) reads only the case |
| (1) `readings_wire_sd_*_sound` applies | each reported check is the approved definition on the case's values (`SDCase.free_eq`, `premises_eq`, `bind_eq`, `model_eq`, `local_eq`, `slotX_eq`, `taken_eq`, `labels_eq`); `free_sound`, `premises_check` apply them to the case's `SupReplaySD`. Not built: a theorem from a runner's JSON to the hypotheses (`sdAssumed`, `sdShared`, `sdModel` return no proofs; RD-6b's replays keep `decodeShared`'s and `decodeSupModel`'s; `sdModel` decodes on the stored vocabulary so `supVocabulary` is not rebuilt per piece) |
| (1) D14 | bound by `SDCase.bind` (= `bindCertX` over `premisesX (supU N) (slotUnder N.D A ++ supX N) (sup N.D).2` and the request's premises), checked on `SDCase.premises`; :203 accepted, :209 and :210 refused |
| (2) verdict scopes | `sdScope`: one conflict check per scope (`sdFree`); `labelImage` once, at the first accepted piece (`SDCase.images`, `images_shown`); per accepted piece `usedOf` (`usedOf_replays`; a full replay is the piece's own check: `replay_query`, `replay_conflict`) shown by `relabel` (`relabel_shown`: `sdShown`). Left at their defaults for sc-11cb (asks3 item 1): `mentions`, `coherence`, `witnessSummary`, `missing`, each note's `gaps` and classification, the answers' `gaps` |
| (2) the soft row | **sc-11cb** (SIGNED); `SDCase`, `sdCaseOf` stay public for it |
| (3) W-13 | :188 `NSDbig 8` (256 choices) admitted and routed once: CONFLICT in one model check (all-strict choice), also as a scope piece. Its `x_required` targets have no certificate (that choice conflicts), so no CONFLICT-FREE case there; :196 `NSDbig 10` refused with `runSDKind`'s text |
| (3) W-14 | :124, :127: four scopes of `NSD4a` (conflict, certificate, countermodel, unsat, model evidence): 1 admission, 1 route check, 3 conflict checks, 2 replays, 3 label images (none for the scope with no accepted piece) |
| (3) refusals | conflict :161, :162, :164, :166, :188; certificate :209, :210, :231; model :225, :227; texts compared whole |

Both directions: CONFLICT-FREE :154 / UNKNOWN :159; accepted :203 / not :207; model valid :214 / not (atom :216, a soft
premise by its choice label with one counted image :219, `localFree` :188); `Fill_T` in `reading_premises` :151 and shown :138;
three encoded pieces :142. Not reached by a fixture: `unsatText` in `sdCaseOf` (RD-6b's shared text) and an accepted `unsat`.

W-1a (OPEN, asks3 item 2): the shown labels of `rs1:1`'s conflict are `[sufficient:0, coherence]` (:127) for the trace
Python's prover supplied, not W-1a's pinned `[coherence]`; sc-11b's differential must meet the pin.

Certificates: `NSD4a` under `rs1:1` (targets; W-1a's query) and `NSDq` under `[]` are traces Python's
`prove_entailment(env, premises, φ, _background=False)` found once on premises Lean regenerated (a scratch `#eval` wrote
`bgb ++ slotX A ++ Fill_T` or `SDCase.premises A1 []` and their predicates); Lean checks them on every build.

## Measurements

- **Size** (`git diff --numstat a3454b6ba`, generated files and tool evidence out): SoftSupRun.lean 433, SoftSupRunExamples.lean
  235, VE.lean 2, mutants.json 19, this report 80: 769 (limit ~800, -sc-11c-asks3.md item 3); with the side tables
  (trust-classes.json 161, assurance-manifest.json 31, trust-baseline.json 7): 968.
- **Trust** (`tools/trust_map.py --check` against a3454b6ba598): PASS; K +0, S +0, tied +66, trusted +65, all SoftSupRun.lean
  (`sdScope` G[V]; `sdShared`, `sdAssumed`, `sdModel` D[V]); runners, route and `SDKind` C, counters G[R], fixtures T. Allowance
  "SIGNED by standing ruling R16 (DRI-RULINGS.md), sc-11c, 2026-10-18" (V +84, recorded before the ties); FOLLOW-UPS.md "## sc-11c".
  Trust mutants (docs/rd-9/sc-11c/trust-mutants.json, `mac-pytest.sh --trustmut`, HEAD 727edc27b): 108 KILLED, 0 SURVIVOR,
  0 UNKNOWN (earlier sweeps' survivors fixed by the ties and fixtures above).
- **Per case, never per piece**: `sup N.D` is built by `sdCaseOf` and again inside `supVocabulary`; `fill U` by `sdCaseOf` and
  inside `fillPremises` (approved bodies, once per case). Admission's search (cut 65) is admission's; `sdCaseOf` runs the cut-1025
  search once, after `routeOf`, `superposable` and `WellFormedU`. `SDCase.bind` encodes and hashes `premisesX` per certificate piece.
- **Build**: `lake build` PASS; `python3 lean/audit.py` PASS (827 files, 9326 theorems, standard axioms only); fixtures build in
  ~46 s; `tools/check_lean_imports.py` kept (the fixtures declare layer 4: they read `Readings.Run`); `tools/assurance_manifest.py --check` 0.
- **Statements**: `tools/check_rd9_sc1_statements.py`: "SC-11 labels PASS: 11 exact", "SC-11 wire PASS: 15 exact", 0 pending;
  `tests/test_rd9_statements.py`: 43 passed. **Selected tests**: `MAC_PYTEST_NO_DEFER=1 mac-pytest.sh --select -- --base a3454b6ba --run` on dd6cf4f43
  (tree 9900a779d1, run on the VM): 112 units recorded, 0 failed, exit 0; no test of main-known-red.txt met.

## Seeded bugs (`docs/rd-9/sc-11c/mutants.json`, all Lean, each KILLED)

M1 a scope re-admits per piece (:124); M2 `labelImage` at a scope's first piece, accepted or not (:124); M3 the binding
under `[]` (:203); M3b the check without `supX` (:203); M4 one check per choice on `NSDbig 8` (:188); M5 `Fill_T` replayed
twice (:138); M6 `shownWith` and M6b `relabel` show the superposed label (:127); M7 `valid` without `localFree` (:188); M8 a
superposed label in `first_failing` (:219); M9 a conflict check per piece (:124); M10 an untaken choice not refused (:162);
M11 the filling ignored (:124, :127, :142); M12 a scope's failing model reads `labelImage` (:124). M5, M6, M6b also break
`replay_conflict`, `shownWith_eq`, `relabel_shown` (their guard runs stub that one proof).

## Spec re-read

- 14.3 (docs/spec/rd-9-soft-chain.md:2039-2046): order slot, atoms, `supX`, `Fill_T` (`slotX`, `free`, `premises`);
  `conflictFreeCheckX` per target (`free_eq`); `bindCertX`, refused when the binding drops or adds a premise (:209, :210);
  `modelCheckX` with `filling`, an `unsaid__` table refused (:227), `localFree` (:188); queries over `sharedEnvSD N` (:231).
- 14.11 (:2455-2460): texts at most 64 from admission; the case's values once per case; `labelImage` once per scope;
  `usedLabels` per accepted piece; members decoded once per piece, the conflict certificates once per scope.
- 14.9 W-13 (:2422), W-14 (:2423); 14.13 (:2496): reached only from examples.

## Self-review against BUILDER-CHECKLIST

1. N.A.: no relayed answer (nothing dispatches here; sc-11b's relay rows). 2. PASS: rows above; moves signed by the DRI. 3. PASS:
14 seeded bugs KILLED (mutants.json); trust mutants 108 KILLED, 0 survivors. 4. N.A.: no Python or Rust product code. 5. N.A.: no relay binding
(sc-11b). 6. PASS: the chain gates the final HEAD. 7. PASS: R16 allowance and FOLLOW-UPS row; no DELTA; no reserved signature.
8. PASS: no user-visible change (:196 compares with `runSDKind`). 9. PASS: `tools/select_tests.py --base a3454b6ba` selects 119 units, not all; among them tests/test_rd9_statements.py, test_assurance_manifest.py, test_trust_budget.py. 10. PASS: the ties' theorems break under M5,
M6, M6b; statements 11 + 15 exact; audit PASS. 11. PASS: over the work limit the route refuses (:196; the order is argued in
`sdCaseOf`, SoftSupWireExamples' W-13 rows pin the route values); a refused piece is no verdict (:127). 12. PASS: `NSDbig 8`
read once in the fixtures (46 s, was 96 s). 13. PASS: no test removed. 14. PASS: both directions above; spec re-read above.
15. PASS: overclaims narrowed (this section and "Per case"); no silent cut (three DRI rulings); every new check has a seeded bug;
limits before work (`sdCaseOf`: superposable, count, work, then texts).

SELF-REVIEW: 2 A, 10 B, 7 C; fixed 17 (B: answers' proofs narrowed, not built). Second review: 2 A, 7 B, 7 C; fixed 14 (C: an
accepted `unsat` and `unsatText` not reached; `bind`'s per-piece hashing named).
