# fu-ar2-decoders: arch-AR-2 round 1 follow-ups F4 and F8

FAST LANE item (acting DRI speed-feed, 2026-10-17). It covers F4 and F8 only. F5 (wiring `trust_changes.py` into the gate) and
F6 (the question-lock note, the assurance manifest's decoder pins) are not in this item.

## What changed

- **F4: `DECODERS` completeness test.** `tests/test_frozen_sources.py::test_every_frozen_identity_has_a_decoder_and_every_decoder_defines_one`.
  The test does not use a hand list or read Lean source text. It runs a Lean script (`IDENTITIES`) with the pinned
  toolchain (`lake env lean --run`), and the script reads the compiled environment of `VE.Service.Protocol`:
  - the frozen envelopes' identity versions: the string literals of `VE.Service.Standalone.Legacy.version`
    (`v0`, `v0.1`, `v0.1-order`);
  - every VE definition that passes an identity domain (`ve-environment-<v>\n` or `ve-meaning-<v>\n`) as a literal
    argument, with its module and the function it is passed to;
  - the VE modules that the digest (`VE.CertificateWire.digest`) reaches through definition values, and the VE
    modules reached by the service's request reader (the `VE.JsonInput` functions that `VE.Service.Protocol`'s
    definitions call).

  The test then checks two things. Every domain must be written in a listed decoder. The set of files that write
  a domain, plus the modules the digest and the reader reach, must equal `frozen.DECODERS`. So the test fails when
  Lean adds a frozen envelope (a new `Legacy.version` arm) that has no decoder, when a decoder is dropped from the
  list, and when the list names a file that defines no identity. Today the derived set is exactly
  `VE/CertificateWire.lean`, `VE/Json.lean` and `VE/Order/Wire.lean`.
- **F8: widest trusted line against widest trusted line.** `tools/trust_changes.py` used to take a file's base width
  from its widest line of any kind. It now uses the widest *trusted* line at the base. The tool reads the base tree
  from git with `trust_map.extract_rev` and classifies it with `trust_map.walk`, using the base's own side table and
  statement list. It then measures the base with the same `trusted_widths` it applies at HEAD. A base whose
  classification fails gives no report (exit 1): the base is held to the same fail-closed rule as the tree.
  `trust_map.measure_rev` now uses the same `extract_rev`, so the code that reads a commit's tree exists only once.
  The output keeps its format: the JSON keys and the line layout are the same. The `widened:` line's wording now
  reads "wider than any trusted line they had at base", which matches the new comparison.
  - Test: `tests/test_frozen_sources.py::test_a_long_comment_at_base_hides_no_collapsed_trusted_code` covers a base
    with a 261-character comment, and HEAD with the trusted body collapsed onto a 79-character line. The file is
    reported as widened, with base 37. In the same test, a decoder that was a test (`T`) at the base has base
    width 0, because the base's own table classifies it. Also
    `test_a_base_whose_classification_fails_gives_no_report`.
  - On VE's real tree, `trust_changes.py --since 8cbb3049` (main~15; this branch changes no Lean file) now lists 9
    files as widened. The old comparison listed 8. It missed `VE/Readings/ComponentsWire.lean` (trusted line of
    146 characters, widest trusted line at base 125, hidden by a wider untrusted line). It also gave
    `VE/NormDefaults/Run.lean` a base of 141 where the widest trusted line was 109.

## Deltas

None user-visible. `tools/trust_changes.py` is a measurement aid (R10) that is not wired into the gate (F5). Its
numbers change as described above. No VE verdict, diagnostic, schema or relay changes. No DELTA.md row.

## Observation for the DRI (not changed here)

The oracle shows that `VE.Service.Graph.legacyCtx` (`lean/VE/Service/Graph.lean:144`) writes the frozen `ve-environment-v0\n`
domain as its own literal, outside the frozen decoders. `VE.Service.Standalone.legacyEnvironmentId`/`legacyMeaningId` build the
frozen domains from `Legacy.version`, which is not hash-frozen either. Both call the frozen `VE.CertificateWire.digest`. An
edit to either literal would change a frozen identity, and the narrow freeze would not catch it. The completeness test counts a
writer outside `DECODERS` as a use, not a definition. Freezing these files, or routing them through a decoder's function, is a
D2 decision.

## Seeded bugs

Recorded in `docs/fu-ar2-decoders/mutants.json`. Each was planted, its test failed, and it was reverted. All are Python (no Lean
or Rust product code changed):

| id | file | behaviour | failing test |
|---|---|---|---|
| S1 | `lean/VE/Route/frozen.py` | `VE/Order/Wire.lean` dropped from `DECODERS` | `test_every_frozen_identity_has_a_decoder_and_every_decoder_defines_one` |
| S2 | `lean/VE/Route/frozen.py` | `VE/Bridge.lean` (no identity) added to `DECODERS` | `test_every_frozen_identity_has_a_decoder_and_every_decoder_defines_one` |
| S3 | `tools/trust_changes.py` | F8 reverted: base width = widest line of any kind | `test_a_long_comment_at_base_hides_no_collapsed_trusted_code` |
| S4 | `tools/trust_changes.py` | base classified with HEAD's side table | `test_a_long_comment_at_base_hides_no_collapsed_trusted_code` |
| S5 | `tools/trust_changes.py` | base classification problems ignored | `test_a_base_whose_classification_fails_gives_no_report` |
| S6 | `tools/trust_map.py` | `extract_rev` hides a git failure | `tests/test_consolidation_tools.py::test_since_gates_a_change_on_its_own_growth` |

## Tests run

- `tests/test_frozen_sources.py`: 14 passed (11 before, plus 3 new).
- `tests/test_trust_ratchet.py tests/test_consolidation_tools.py tests/test_frozen_sources.py`: 405 passed.
- Selected tests on the Mac runner (`mac-pytest.sh --select`, HEAD a21d8203, 25/423 units): exit 0, 0 failed.
- Full release gate: not run (FAST LANE). The chain and the merge train run it.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A. No relayed answer, schema or decoder of a Lean answer changed.
2. Deliverables: PASS. F4 is `test_every_frozen_identity_has_a_decoder_and_every_decoder_defines_one`. F8 is
   `test_a_long_comment_at_base_hides_no_collapsed_trusted_code`, and the output format is kept. F5 and F6 are
   excluded by the task. No Python copy of a Lean decision (the identities come from the compiled library), and no
   report test.
3. Tests can fail: PASS. Seeded bugs S1–S6 above, each killed by the test named.
4. Py/Lean/Rust agree: N.A. No checker behaviour changed.
5. R8 binding: N.A. No relay.
6. Gate evidence: N.A. for this build (FAST LANE: no gate run here). The selected tests on HEAD a21d8203 passed.
7. Unsigned items: PASS. No DELTA row and no trust-budget growth (no Lean file changed).
8. DELTA: PASS. No user-visible change. The measurement-tool output change is described under "Deltas".
9. Test selection: PASS. `tools/select_tests.py --base $(git merge-base HEAD main)` selects 25/423 units, including
   `tests/test_frozen_sources.py` and `tests/test_consolidation_tools.py`, which kill S1–S6.
10. Lean statements: N.A. No theorem added or changed.
11. Budgets, limits, deadlines: PASS. The oracle's subprocess waits use `HANG_TIMEOUT` and have no literal timeout
    (`tests/test_hang_guards.py` is in the selection and passed).
12. CPU and memory: N.A. Product code is unchanged. `trust_changes.py` now classifies the base once:
    9.4 s on the real tree against main~15.
13. Removed or renamed tests: N.A. None removed or renamed. `fixture_repo` gained an optional argument.
