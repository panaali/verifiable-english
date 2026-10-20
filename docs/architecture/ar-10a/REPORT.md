# ar-10a report: the profile-gate table (AR-10, SYNTHESIS 2.2)

No DRI signature is reserved. Two findings on the approved statements (F1, F2) are reported, not acted on beyond the
one forced type choice in F1.

Plan: docs/ARCHITECTURE-REVIEW-2026-10.md 4.4 AR-10 at 6ae55ebb8, as SYNTHESIS.md 2.2 widens it; 4.1 and 4.2;
arch-dri-decisions.md D8. Statement gate: SYNTHESIS 2.2 is the converged three-round review (Astra and Fable) and
the task names it as the statements to build; I found no separate review record of AR-10's table (SYNTHESIS 4.1 step
2 asks for one), so this item rests on the task's instruction.

## Plan rows

| Row | Delivered | Where | Checked by |
|---|---|---|---|
| `ProfileRow` (four fields, as written) | yes | `lean/VE/Compose/Dispatch.lean` | every guard below |
| `profileTable`, the only place a profile is registered | yes: `baseRows ++ wrapperRows`, 24 rows for 19 profiles; Python's list comes from it | same | `gate_legacy`; `#guard` legacy profiles = table profiles |
| `gateOf` with a fixed fault order | yes: order error, unregistered profile, then each row in table order (requirements, then refusals) | same | `gateOf_iff`, `gate_legacy`, Examples guards |
| `gateOf_iff`, exactly as written | yes | same | `#print axioms` in Audit.lean |
| `gate_legacy` | yes, with the right side `dispatch ps` (F1) | same | Examples guards on 65,536 + 4,096 lists |
| Runners call the table; today's checks deleted | runners switched: Standalone (3 sites, `gateOf baseRows` or the whole table with `readings@1`, proved by `baseGate_today`), Readings Run and Wire. The legacy definitions stay as the specification (F2) | `Service/Standalone.lean`, `Readings/{Run,Wire}.lean` | selected tests |
| Python reads a generated data file; no hand-written rows; mirror deleted | yes: `ve/profile_table.json` from `VE/Compose/ProfilesMain.lean` (`tools/profile_table.py`, regen entry `profile-table`); `REGISTRY`, `ProfileRecord`, `checker_family`, `route_gate`, `require_checker`, `GATED` deleted (R6: Environment construction is Lean-validated, so `search.py`'s call decided nothing new) | `ve/profiles.py`, `ve/search.py` | `tests/test_profile_table.py` |
| Route/mode registry | not here: ar-10b, as the task says | | |

## Findings on the approved statements

- **F1.** `gate_legacy`'s right side `todayGate ps` has type `Except String Unit`; `gateOf` answers `Except String
  Route`, so the statement as written does not elaborate. Built as `gateOf profileTable ps = dispatch ps`: `dispatch`
  is today's gate with its route, the stack included (verdict, text, fault order and route). `legacyProfiles` is
  `registered ++ wrapperProfiles`. `todayGate` itself is pinned by `baseGate_today` (`gateOf baseRows ps = today ps`).
- **F2.** "Today's profile checks are then deleted" conflicts with `gate_legacy`, whose right side must exist. No
  runner calls `todayGate`, `today` or `dispatch` now; they stay as the legacy specification, with their approved
  theorems unchanged (statements.txt has additions only).
- **F3 (elaboration, no statement change).** Today's order interleaves profiles (risk@0's checks sit at 4.2 checks
  4-5 and 15; the base requirement at check 9), and its requirement texts differ. Within the four fields: a profile
  may have several rows; a row that requires its own profile is mandatory (`Missing profile p`); a checker row's
  requirement reads `Unsupported profile p without q`; the route is the first of a fixed list of heads with a listed
  row (`heads`). The one order the table cannot keep is an unregistered profile's: DELTA row 1 (R2).

## Seeded bugs and mutants

[`mutants.json`](mutants.json): 20 of 20 killed, each run twice (as is, and with the section's proofs stubbed so
only `#guard`s, `example`s and tests can catch it). Lean (one per new definition, 16) in
`lean/VE/Compose/Dispatch.lean`, e.g. `needText` "requires" to "needs" fails the 65,536-list guard (Examples.lean:232)
and `todayGate_base`; `gateOf` with the unregistered check removed fails Examples.lean:234 and `gateOf_iff`;
`outsideProfiles` without reports@0 fails the 4,096-list wrapper guard (:255) and `gate_legacy`. Printer (2) in
`lean/VE/Compose/ProfilesMain.lean` fail `test_the_committed_table_is_the_lean_generators_output`. Python (2):
`ve/profiles.py` `BY_NAME` fails `test_python_reads_the_rows_and_the_environment_profiles`;
`tools/profile_table.py` `--check` fails `test_generator_writes_lean_output_and_check_refuses_any_other_file`.

## Trust, size and evidence

- Trust (`tools/trust_map.py --check`, against main 585794c92): K +0, S +18 (Dispatch +19: ProfileRow 7,
  TableAdmits 5, routeOf 5, legacyProfiles 2; Standalone -1), untied V +49 (Dispatch +43: refusing 3, speechOthers 5,
  outsideProfiles 3, wrapperRows 8, environmentWrapper 4, environmentProfiles 3, heads 6, needText 5, rowChecks 6;
  ProfilesMain +7: rowJson 4, main 3; Standalone -1);
  `baseRows`, `profileTable` and `gateOf` are tied (`baseGate_today`, `gate_legacy`, `gateOf_iff`). Allowance signed
  by R16; FOLLOW-UPS "## ar-10a" asks for the ties pass.
- Size: 628 hand-written lines added before this report (174 deleted), about 690 with it, of which 265 are the
  `gate_legacy` proof; no smaller part carries the switch, so nothing is split off.
- Tests: the selected plan on the Mac runner (c67af76d9, 452 units) failed only three inventory tests, fixed in
  bc44abcfd (197 pass); after syncing main, 970 pass in the nine affected files. `regen_generated.py --check` and
  `gate_collection.py --check --prebuilt` pass (4 added, 0 removed). Not run: `tools/lean_first_diff.py` (the batch
  gate's A/B; its pilots corpus is whole documents, L70); `gate_legacy` and the guards cover the gate itself.
- Pilot bytes: none expected; no verdict moves.
- Overlap: `tools/regen_generated.py` is also edited by two stale branches (foundation/me-1, infra/arch-AR-1).
- Next: ar-10b (route registry), then the profile rows (ap-1b, jt-2, et-4 ...); ties-ar-10a; composition.md 4.2 and
  9.3 still name `ve/profiles.py` `checker_family` (for the docs sweep).

## Self-review against BUILDER-CHECKLIST

1. N.A.: no new or changed relayed Lean answer; the generated file's types are checked by `test_python_reads_the_rows_and_the_environment_profiles`.
2. PASS: plan rows table above.
3. PASS: `mutants.json`, 20 of 20 with proofs stubbed.
4. PASS: `gate_legacy`, `baseGate_today`; Examples guards on 65,536 and 4,096 lists; the A/B not run (above).
5. N.A.: no relayed field added; Python reads only Lean's generated file.
6. PASS: synced with main (6f3687a24); the chain runs the gate on the final HEAD.
7. PASS: DELTA rows cite R2 and R16.
8. PASS: DELTA row 1 with its guards (Examples.lean 234-238).
9. PASS: the selected run included `tests/test_profile_table.py`, `tests/test_compose_dispatch.py` and the inventory tests it caught.
10. PASS: proofs break under the unstubbed mutants (`mutants.json` "proofs"); statements.txt additions only.
11. N.A.: no budget, limit or deadline code.
12. N.A.: the gate runs once per environment over at most 19 profiles; no enumeration on a production path.
13. PASS: `gate_collection.py --check --prebuilt`: 0 removed, 0 malformed.
