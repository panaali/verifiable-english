# ap-1b build report: the `acts@0` row, its decoders and Lean's entitlement wordings

**No DRI signature is reserved; nothing stops the item.** DELTA rows: R16 (trust, untied V +67, K +0), the DRI's
SYNTHESIS 2.2/4.2 (the row and what it admits, as et-7's merged DELTA cites them), R1 (refusal texts), R2 (fault
order). The item is over the ~600-line guide (section 5); the rest of AP-1 is the next item, **ap-1bb** (section 6).

Plan: `research/act-phrases-p1` at `bb5b2f90d`, [act-phrases-PLAN.md](../../spec/act-phrases-PLAN.md) section 4
"AP-1" (what [ap-1a's REPORT](../ap-1a/REPORT.md) section 6 left) and 2.8; spec [act-phrases.md](../../spec/act-phrases.md)
2.1, 3.1-3.3, 4.1, 4.4, 10, 11.1. Both files are on `main`, byte-identical to the pinned commit.

## 1. Statement gate and order

As for ap-1a (its REPORT section 1): the statement review converged (FIX applied, verified PASS); the acting DRI
launched this item after ap-1a and ar-10a, which are merged. ap-1a's review F5 asked that ap-1c (the proofs of spec
4.3) land before `acts@0` is admitted; ap-1c is not queued, and the DRI's order for this item is "after ap-1a and
ar-10a". The acceptance it adds is computed by Lean (`Lexical.check`, `decodeFixed`, the row, with fixtures); the
missing theorems characterise it and are not presented as checked anywhere.

**Overlap** (hand-written files of branches in flight): `feature/jt-2` edits `lean/VE/Compose/Dispatch.lean` (its
`judgments@0` row, `todayGate_base`'s `simp` set), `lean/VE/Compose/Examples.lean`'s profile-count guard,
`lean/VE/Service/Standalone.lean` and `ve/profiles.py`. SYNTHESIS 4.2 puts table rows in landing order; this row sits
after `norms@0`, away from jt-2's hunk; the count guard and the `simp` set will conflict and whichever lands second
takes both rows.

## 2. Plan rows delivered and not delivered

| Plan row (AP-1, as ap-1a left it) | Status | Where |
|---|---|---|
| `Dispatch.lean`: `acts@0`'s row of AR-10's table with its composition theorem | **done**: `⟨"acts@0", ["norms@0"], actsRefuses, "layer"⟩` after `norms@0`; `gate_acts` as spec 4.4 states it; `gate_legacy` and `todayGate_base` re-proved | `Dispatch.lean` 757-783, 1104-1157; `Compose/Examples.lean` 240-261 |
| `Norms/Wire.lean`: `decodeNormsEnvironment` with the envelope's profiles and the block's `fixed`; `canonicalEnvironmentJson` by `canonicalActIn` | **done**: an `acts` flag lets a route read `acts@0` (`decodeSource` and `decodeEnvironmentU` set it; every other caller keeps refusing the profile); `actsView` is what the frozen envelope and vocabulary decoders read; `FlaggedSpec`'s proof follows (the approved statement unchanged, a new `normsEnvironment_flag_not_defined_in`) | `Wire.lean` 107-189 |
| `Tree.lean`, `NormDefaults/Check.lean`, `FillCheck.lean`: drop the plain-act refusal | **done**: `check_eq := rfl` holds; `regBody_ok` and `fill_regOK` compile unchanged; the frozen inventory regenerated | — |
| `Plain.lean`, `Encode.lean`, `Standalone.lean` (spec F1) | **done**: `decodeRegulatedAllIn`; `Plain.run`, `Replay.baseEnvironmentJson`, `regulatedView`/`typingView` and `modalForm` read the profile; the environment mode gates an `acts@0` list by the table first and leaves its declarations to the norms decoder | — |
| `Policy.lean`: the selected wording of a plain act is `Lexical.wording` | **done, without a Policy hunk** (deviation 1): `modalForm` returns it beside the modal forms and `Env.decode` puts it in the forms' wordings, which `policyPredicateIn` selects for a non-modal predicate | `ActsExamples.lean` (wordings guards) |
| `ve/environment.py`: the block and a plain `act`/`form` as data | **done** (no check); `ve/norms.py`'s base projection drops `acts@0` and its block with `norms@0`; `ve/profiles.py` keeps `acts@0` for model cases | `tests/test_acts_profile.py` |
| `ve/printer.py`: render a plain act with Lean's wording | **ap-1bb**: no service mode returns wordings to Python; Python may not compute one | — |
| `rust/ve-kernel/src/environment.rs`: refuse `acts@0` | **no change needed**: `ALLOWED` lacks the profile, so Rust answers `UnsupportedProfile: Unsupported profile acts@0`; pinned by `test_rust_refuses_an_acts_environment`. No Rust code changed, so no Rust seeded bug | — |
| `ve/wire_contract/acts@0.json` | **ap-1bb** (size) | — |
| Tests: Lean verdicts relayed (A1-A3 check, A5/A6 refused with Lean's text) | **done** | `tests/test_acts_profile.py`, `tests/test_acts_lexical.py` |
| A31: byte-identical without `acts@0` | **done**: 330 of 330 | [evidence/byte-identity.json](evidence/byte-identity.json) |
| A plain act renders its Lean wording; long wordings (A1 109 B, A21 414 B) | **Lean: done** (`#guard`s); Python display: ap-1bb | `ActsExamples.lean` |
| ap-1a review F2: pin three fault orders under R2 | **done** | `LexicalExamples.lean` 248-254, DELTA row 4 |

## 3. Deviations (recorded here, not in the copied plan)

1. **No `Policy.lean` hunk.** Marking a plain act's predicate modal would exempt it from lexicon V4 (spec 2.1 keeps
   V4) and drop it from the situation's author predicates; a forms wording does neither, and Policy already prefers it
   for a non-modal predicate. The `EnglishGrammar/*` queue's first edit is `Encode.lean` (`actions_version` 32).
2. **The row's slot is `layer`**, as `data@0`'s and `definitions@0`'s (spec 4.4 wrote `decoder`, "like data@0 and
   definitions@0"); no route head reads it. Its refusal texts omit `UnsupportedProfile: ` (the gate adds it). It also
   refuses `speech-acts@0`: the table's speech row does not list `acts@0`, and `gate_acts` needs the refusal.
3. **Readings and model questions are refused, not read.** The row admits the readings route, whose decoder does not
   read `acts@0` yet: it answers `Unsupported profile acts@0` (guarded). Rust and Lean's model path answer
   `UnsupportedProfile` on model questions; the model oracle gains the `acts@0` environment with those answers
   (`oracle_acts.py`; recorded at the head, as the profile has no base).
4. An act with U+2019 loaded through Python is `CheckerUnavailable` (Lean folds it into the identity, Python stores it
   as written); pinned by a test, fixed in ap-1bb.

## 4. Seeded bugs

`seed_bugs.py` plants each, runs its check (a module build or a pytest node) and restores the file;
[mutants.json](mutants.json) holds `file`, `test` and the first failure: **34 bugs, all killed** (Lean 30, Python 4).
`ActsExamples.lean` line numbers are those of the file when each ran.

| Definition | Bugs (what fails) |
|---|---|
| `actsFixed` | fields unchecked, phrases unchecked: block guards |
| `actsProfiles` | any list read, `acts` flag ignored: the frozen-decoder refusals |
| `actsView` | block kept, profile kept: the A1-A3 decode |
| `actsFamilyRefusal`, `actsRefuses`, the row | text, `speech-acts@0` dropped, `requires` emptied: Compose guards (the last two fail `gate_acts` first) |
| `decodeNormsEnvironment`, `canonicalEnvironmentJson`, `decodeSource`, `decodeEnvironmentU` | phrases not passed, profiles, `canonicalAct`, flags off: their guards |
| `decodeRegulatedAllIn`, `Plain.run`, `baseEnvironmentJson`, `typingView` | today's decoder, family unchecked, view dropped: plain-route, replay and typing-view guards |
| `Tree.check` (+ `regBody`) | plain-act refusal restored: `check_eq`; with `regBody` too, `regBody_ok` |
| `validatedComposedEnvironment`, `folView` | gate off, `checkRegulated` run: environment-mode and family guards |
| `modalForm`, `Env.decode` | no wording, modal, no phrases: the wordings guard |
| orders (F2) | shape/bytes, count/phrases, both-or-neither/form swapped: `LexicalExamples` 250, 251, 253 |
| Python | `form` dropped (the plan's bug), block dropped, base keeps `acts@0`, model row not kept: `test_acts_profile`, `test_model_environment` |

## 5. Trust, size, evidence and tests

- **Trust:** `trust_map.py --check` PASS: K +0, S +0, untied V +67 (per file in DELTA row 1); the allowance is signed
  by R16, and FOLLOW-UPS has "## ap-1b". New declarations are classified (`ActsExamples` helpers `T`).
- **Size** (hand-written, against the merge base): Lean product about 220 lines (Dispatch 64, Wire 55, Encode 34,
  Plain 19, FlaggedSpec 17, Standalone 9, FamilyNorms 7, Replay 6, Tree/NormDefaults 6), Python product 22, fixtures
  173 (`ActsExamples` 142, Compose 24, Lexical 7), tests 146, evidence scripts about 295 (`seed_bugs.py` 160,
  `delta.py` 95, `oracle_acts.py` 40), side tables 43, this report and DELTA. About 900 before the docs, over the
  ~600 guide: the product part is 240; the rest is the fixtures and evidence the rulings ask for. ap-1bb is cut to
  stay small.
- **Evidence:** [evidence/byte-identity.json](evidence/byte-identity.json) (330/330 identical);
  [evidence/delta.json](evidence/delta.json) (14 records; `delta.py` exits 1 head against head);
  [evidence/commits.txt](evidence/commits.txt) (`git log main..HEAD --no-merges` before the commit that adds it).
- **Tests:** `lake build` (1,046 jobs), `lean/audit.py`, `check_lean_imports.py`, `regen_generated.py --check`,
  the four `check_*_statements.py`, `gate_collection.py --check --prebuilt` (14 added, 1 removed by its trailer) pass;
  `tests/test_acts_profile.py` 10/10. Selected tests: see section 8. No `main-known-red.txt` test is involved. The full
  gate is the chain's.
- **Pilot bytes expected to move:** none until a pilot re-declares (*estimate*): this makes M2 (u020, u059, 364 B),
  M3 (28 UDHR entitlement lines) and M4 (Group C, 664 B) expressible; nothing is claimed before a pilot audit.

## 6. Next item: ap-1bb

The plain-act display in `ve/printer.py` through a Lean wording relay (a mode or field that returns Lean's selected
wordings, typed and bound); Python's identity from Lean's canonical environment (deviation 4); the readings route's
decoder and Lean's model path reading `acts@0` (deviation 3); `Words/Situation.lean`'s regulated decode;
`ve/wire_contract/acts@0.json` with its registry, examples and catalogue. Then ap-1c (proofs) and AP-3.

## 7. Self-review against BUILDER-CHECKLIST

1. PASS: no new response field or mode; existing relays carry `acts@0` documents and their fuzz tests run in the
   selection (`tests/test_relay_mutation_gate.py`, `tests/test_norms*.py`); the environment's new data is identity-bound
   (`test_an_acts_environment_loads_with_its_block_and_forms_as_data`, `py-drop-form`).
2. PASS: section 2 lists every row with its place or ap-1bb; no Python copy of a Lean decision (Python stores data,
   `ve/norms.py` only drops a block); no permanent report test; overlap reported (section 1).
3. PASS: 34 seeded bugs killed (`mutants.json`); `delta.py` fails head against head and on empty input.
4. PASS: base against head on 330 route cases (`byte-identity.json`) and on the `acts@0` inputs (`delta.json`).
5. PASS: Python reads no new field from a Lean answer; Lean's refusals are relayed (`test_a_joined_act_is_refused_with_leans_text`).
6. PASS: synced with main `2296317a9` (clean merge), inventories regenerated, the selected tests rerun on the synced
   tree (section 8); evidence from `main..HEAD --no-merges`; the gate is the chain's.
7. PASS: DELTA rows cite R16, the DRI's SYNTHESIS (as et-7), R1 and R2; FOLLOW-UPS row written; nothing reserved.
8. PASS: `delta.json` (every `acts@0` input, every mode it reaches) and `byte-identity.json` (none changes otherwise).
9. PASS: `select_tests.py` selects `tests/test_acts_profile.py`, `tests/test_acts_lexical.py`, the model and profile
   table tests, and `lake build` for this diff; a seeded Lean bug fails the selected `lake build`.
10. PASS: `gate_acts` broken by `row-requires` and `actsRefuses-speech`; no approved statement changed
    (`check_*_statements.py`; `statements.txt` gains two theorems).
11. PASS: limits unchanged (ap-1a's boundaries); the act and phrase limits' order is now pinned (F2 guards).
12. N.A.: no new work on an existing path beyond one `profilesOf` read per decode; 330/330 cases identical.
13. PASS: `gate_collection.py --check --prebuilt`: 1 removed by its trailer, 0 refused, 0 stale, 0 malformed.

## 8. Selected tests and the sync

- **Sync:** `main` moved to `2296317a9` (et-3c, speed-trustmut, df-1ab, ar-10b); the merge was clean, then
  `regen_generated.py --write`, `lake build` (1,052 jobs), `lean/audit.py`, `trust_map.py --check` (PASS against
  `2296317a9`) and `gate_collection.py --check --prebuilt` (14 added, 1 removed by its trailer, 0 refused).
- **`actions_version` 32** (`Encode.lean` holds trusted English code): the recorded `tests/fixtures/ask/*.json`
  (`tools/ask_fixtures.py --write`) and `docs/english-lean/s3-fixture-comparison.json`
  (`conformance.english_lean_s3_compare`) are re-recorded; only the version field changes (as ps-6r did for 31).
- **Selected run** (`mac-pytest.sh --select`, merge base `2296317a9`, on `0e233f67`'s parent; it ran on the VM, the
  Mac yielding to a candidate gate): 459 units, 457 passed, 2 failed, both fixed in `0e233f67` and passing on rerun:
  `tests/test_compose_dispatch.py` (58 passed; its 2^16-list enumeration of the composition spec's legacy registry
  now names `acts@0` as a later row, covered by `gate_acts` and the Compose guards) and
  `tests/test_english_lean_s3_compare.py` (6 passed; the version re-record). An earlier run on the pre-sync tree
  failed in `test_lean_conformance` and `test_consolidation_tools` only because my seeded-bug runs edited sources
  during it; those pass on the final tree (rerun directly, 14 passed).
