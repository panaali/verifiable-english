# ap-1bfb build report: `acts@0`'s rule phases, frames and adverbs, and ap-1bf's review findings F1 and F2

**Status: built, all of A, B and C; no DRI signature is reserved; nothing stops the item.** F1: both engines now say
`UnsupportedProfile: acts@0 requires norms@0` (Lean's profile row, relayed by Python). F2: `acts@0` is in both `UNITS`
and its recorded corpus is compared record by record. B: `acts@0.json` (revision 2) includes `norms@0`'s rule phases
over an `acts@0`-reading typing environment. C: D-31 is 1.1e/1.1f. DELTA: R1, R16 (V +36), R12. Next item: none.

Scope: this item's task (ap-1bfb, folding ap-1bf-f1); ap-1bf's [REPORT.md](../ap-1bf/REPORT.md) section 5 and deviation
4; ap-1bf-review-ov.final.md F1 and F2. Statement gate: no spec statement changes (`git diff --stat 8eda0371fd --
docs/spec/act-phrases.md docs/spec/wire-contract.md lean/statements.txt` is empty).

## 1. Rows delivered

| Task part | Status | Where; test |
|---|---|---|
| (A1) failing first: an `acts@0` source without `norms@0` gives one check, outcome and text in both engines | done; committed failing at `a85a490621` ([a1-before.txt](a1-before.txt)) | `tests/test_acts_contract.py::test_a_source_without_norms_gives_one_record_in_both_engines` |
| (A1) Lean's hook gets the branch for its own case; Lean owns the text, Python relays it | done: `decoded` runs `acts@0`'s profile row (`VE.Compose.gateOf baseRows`) before the decoder, as the environment mode does (`Service.Standalone.validatedLayerEnvironment`); the text is `Compose.needText`'s, and Python's engine has it from `Environment`, a relay of that mode. No Python text was added. | `lean/VE/WireContract/Hooks/Acts.lean` `decoded`; `#guard` on `decoded` without `norms@0` |
| (A1) the review's 45-case sweep rerun | done: [sweep.py](sweep.py) (kinds 6, domain 6, profile lists 9, multibyte 4, normalised spaces 5, regulated 64/65, `defined` 3, flags 3, admission 5, envelope 2). On the pre-A1 hook [sweep-before-a1.json](sweep-before-a1.json): 4 differ (`profiles-without-norms`, `admission-without-norms`, and the two below); on the final code [sweep-after.json](sweep-after.json): 2 differ | `uv run python docs/act-phrases/ap-1bfb/sweep.py <out>` |
| (A1) the two differences `norms@0` shares, listed, not fixed | `defined-without-definitions` (Lean `defined declarations require the definitions@0 profile`, Python's legacy text differs) and `language` (Lean `UnsupportedProfile: Unsupported language`, Python's differs): both texts only; check id and outcome agree | [sweep-after.json](sweep-after.json) rows `differs` |
| (A2) `acts@0` in `tests/contract_input_recorder.py`'s and `tests/test_wire_contract_s5_lean.py`'s `UNITS` | done: the recorder routes an `acts@0` source to its unit (both its paths read `UNITS`); the s5 row has the base, the norms route's kind, `Acts`, `legacy_norms`, and fixtures A1 to A6 | `tests/test_wire_contract_s5_lean.py::test_fixtures_records_and_legacy_agreement[acts@0]`, `::test_lean_route_rejects_where_the_engine_faults[acts@0]`, `::test_both_adapters_share_one_domain[acts@0]` |
| (A2) the recorded corpus compares both engines record by record | done: the recorder runs over `-k acts` of both files and every recorded source goes through Python's and Lean's engine | `tests/test_acts_contract.py::test_the_recorded_corpus_gives_one_record_in_both_engines` |
| (A2) the comparison would have caught F1 | shown: on the pre-A1 hook it fails naming the F1 source ([seed-1-norms-branch.txt](seed-1-norms-branch.txt), last lines) | same test |
| (B) a `typingEnvironment` that decodes with `acts := true`, beside `Hooks.Norms`' (unchanged) | done, with `ruleTyping` over it; the other included hooks are `Hooks.Norms`' own | `Hooks/Acts.lean` `typingEnvironment`, `ruleTyping`, `classifier`, `hooks`; the rule-phase `#guard`s |
| (B) `acts@0.json` includes `norms@0`'s rule phases | done: one phase `rules`, include `norms` of `profiles`, `rule-shape`, `rules`, `references`, `semantic` (norms@0's order); `uses` gains `norms@0`; revision 2 | `ve/wire_contract/acts@0.json`; `#guard` that the scope equals `Tables.Norms`' phases |
| (B) faults on `base.json` per included phase, generated through regen, both engines record by record | done: `rules-limit` (2.2), `unit-field` (3.1), `guard-shape` (3.8b), `name-repeat` (4.2), `predicate-unregulated` (4.4), `guard-arity` (4.7a), `guard-predicate` and `guard-on-a-plain-act` (4.7b), `over-unknown` (5.1), `precedence-cycle` (6.1) | `tests/test_acts_contract.py::test_every_fault_gives_its_member_in_python_with_leans_text`, `::test_every_fault_gives_its_record_in_lean_and_the_sources_at_each_limit_are_clean` |
| (C) D-31 refusals as named members of 1.1, text read from Lean | done: 1.1e (31a, `ACTS_RESOURCE_LIMIT`) and 1.1f (31b to 31s and a frame that does not decode, new code `ACTS_INVALID_FRAMES`); 1.1d kept (no id changed). Lean names the member when `Acts.Wire.decodeVocab` on the `acts` block gives exactly the decoder's text; Python when Lean's decoder gives that text on the block's frames and adverbs alone and accepts the same environment without them | `Hooks/Acts.lean` `member`, `blockOf`; `conformance/acts_contract.py` `vocabulary_refusal`; `tests/test_acts_contract.py::test_a_refusal_before_the_frames_is_not_theirs` |
| (C) faults at and around 31a's limit and one per text class | done: `frames-over`, `frames-over-with-bad-head` (1.1e), the source at the limit accepted (`at_frames`), one fault per condition 31b to 31s (18 distinct Lean texts), `frame-fields`, `frames-not-an-array` (1.1f). The limit is found from Lean's decoder (`limits()["maxFrames"]`), never written | `::test_every_fault_gives_its_record_in_lean_and_the_sources_at_each_limit_are_clean` (asserts 18 distinct texts); `::test_the_limits_are_leans_and_never_copied` |

## 2. Deviations and choices

1. **`profiles` is included too.** The task names rule-shape to semantic, "as norm-defaults@0.json shows the pattern";
   that file includes `profiles`, and it holds 2.2, the rule count, which is charged before any rule is walked. 2.1
   (`norms@0` required) cannot fire after 1.1, which refuses a source without `norms@0` first. The included phases
   keep `norms@0`'s order (norm-defaults puts `rule-shape` first), since the legacy validator here is the norms
   route's.
2. **The profile row runs on every list naming `acts@0`**, not only when `norms@0` is missing: that is the order of the
   environment mode Python's engine relays, so the two agree by construction (the sweep's profile-list cases and the
   `#guard` on an unsorted list with an unknown field).
3. **An inherited member of an included phase keeps each language's text** (wire-contract.md 2.7; the s5 tests compare
   it the same way): Lean's 3.8b says `array expected` where Python's legacy says `AST nodes must be nonempty tagged
   JSON arrays`. The corpus comparison therefore compares all fields of every record but `text` and `args` of those
   members (`comparable` in `tests/test_acts_contract.py`); 1.1's members carry Lean's text in both and are compared
   in full. This is `norms@0`'s own behaviour, not changed here.
4. **`ruleTyping` repeats `Hooks.Norms.ruleTyping`'s 10-line walk** over the acts-reading environment, since
   Hooks/Norms.lean stays byte for byte; it calls `Hooks.Norms.typeRule` and `typingMember`, so the typing itself has
   one owner. See Notes.
5. **The recorder's `_record_norm_cases` and `_norm_unit` now read `UNITS`** instead of literal unit tuples, so that
   dropping `acts@0` from `UNITS` stops its recording (seeded bug `py-recorder-units`); for `norms@0` and
   `norm-defaults@0` the sets are the same as before.
6. **The s5 adapter cases' quoted unit** reads `(norms * 2)[1]`, which is `norms[1]` for both norm bases (unchanged
   bytes) and `norms[0]` for the one-rule `acts@0` base.

## 3. Seeded bugs

[mutants.json](mutants.json), written by [seed_bugs.py](seed_bugs.py): **17, all killed** (Lean 9, Python 7, Rust 1
in the generated `contract_tables.rs`, the one Rust file changed). Each was planted, run and restored with
`git checkout`. The four the task names are the first, second (twice) and fourth below.

| Id | File (definition) | Bug | Killed by |
|---|---|---|---|
| `lean-norms-branch-removed` | `Hooks/Acts.lean` (`decoded`) | the profile row removed | `#guard` on `decoded` without `norms@0`; with the service rebuilt: the A1 test, the corpus test and the s5 row ([seed-1-norms-branch.txt](seed-1-norms-branch.txt)) |
| `lean-typing-without-acts` | `Hooks/Acts.lean` (`typingEnvironment`) | decoded without `acts := true` | the rule-phase `#guard`s (`norms/4.7b`) ([seed-3-typing-environment.txt](seed-3-typing-environment.txt)) |
| `lean-typing-error-ignored` | `Hooks/Acts.lean` (`ruleTyping`) | the refused rule's member dropped | `norms/4.7b` `#guard`s |
| `lean-typing-first-rule-only` | `Hooks/Acts.lean` (`ruleTyping`) | each item typed as rule 0 | `#guard` on rule 1's `norms/4.7b` |
| `lean-block-level` | `Hooks/Acts.lean` (`blockOf`) | the block read a level too high | the 1.1e/1.1f `#guard`s |
| `lean-frames-members-swapped` | `Hooks/Acts.lean` (`member`) | 1.1e and 1.1f swapped | the 1.1e/1.1f `#guard`s |
| `lean-classifier-norms-typing` | `Hooks/Acts.lean` (`classifier`) | 4.7 left to `Hooks.Norms`' typing environment | `norms/4.7b` `#guard`s |
| `lean-hooks-no-predicates` | `Hooks/Acts.lean` (`hooks`) | included hooks hold everywhere | `norms/4.4` `#guard` |
| `lean-registered-own-only` | `Hooks/Acts.lean` (`registered`) | included hook names unregistered | `#guard Tables.Acts.table.hookNames.all registered.contains` |
| `py-recorder-units` | `tests/contract_input_recorder.py` (`UNITS`) | `acts@0` dropped | `test_the_recorded_corpus_gives_one_record_in_both_engines` |
| `py-s5-units` | `tests/test_wire_contract_s5_lean.py` (`UNITS`) | `acts@0` dropped | same (the s5 file then records no source, so the set of recording files differs) |
| `py-d31-text-copied` | `conformance/acts_contract.py` (`acts_environment`) | 31p's text copied with `declared` made `listed` | `test_every_fault_gives_its_member_in_python_with_leans_text` |
| `py-oracle-unguarded` | `conformance/acts_contract.py` (`vocabulary_refusal`) | an earlier refusal read as the frames' | `test_a_refusal_before_the_frames_is_not_theirs` |
| `py-frames-class` | `conformance/acts_contract.py` (`acts_environment`) | the frame limit named 1.1f | `test_every_fault_gives_its_member_in_python_with_leans_text` |
| `py-registry-no-hooks` | `conformance/acts_contract.py` (`REGISTRY`) | `norms@0`'s hooks unregistered | same |
| `py-frame-limit-oracle` | `conformance/wire_contract_faults_acts.py` (`limits`) | the frame limit one too low | same |
| `rust-table-code` | `rust/ve-kernel/src/contract_tables.rs` (`ACTS`) | 1.1f's code | `tests/test_wire_contract_rust.py::test_rust_table_rows_equal_the_contract_rows` |

## 4. Trust, size, evidence and tests

- Trust: `uv run python tools/trust_map.py --check` against `8eda0371fd`: K +0, S +0, untied V +36, all in
  `lean/VE/WireContract/Hooks/Acts.lean` (the generated table is one line, as before); allowance recorded with
  `trust_map.py --allow` (`docs/trust-baseline.json`), DELTA row 2 (R16); FOLLOW-UPS.md row "## ap-1bfb". The new
  fixtures and the 14 derived `BEq` instances (test-only, for the structural `#guard`) are classed T.
- Trust mutants (13a; `mac-pytest.sh --trustmut -- --max-mutants 1000 --test lean/VE/WireContract/Hooks/Acts.lean
  --test lean/VE/WireContract/Diagnose.lean --allow docs/act-phrases/ap-1bfb/trust-allow.json`): the first run
  ([trust-mutants-first.json](trust-mutants-first.json), no allow file) had 329 SURVIVOR, 320 of them in the generated
  table's inlined `norms@0` phases; the `#guard`s added for them (the scope equal to `Tables.Norms`' phases, a joined
  act typed, `data@0`, the node total at the budget, an unsorted list with an unknown field) leave
  [trust-mutants.json](trust-mutants.json): **457 KILLED, 0 SURVIVOR, 0 UNKNOWN, 15 ALLOWED, 4 INVALID**, exit 0 (full
  run at `5e740e8dee`, then two `--rescore` runs for the 3 UNKNOWN and the allow edit). The allowed: 7 `inherited` flag
  flips of the own phase (no Lean engine function reads the flag), 2 equivalent `data@0` reads, 3 that do not
  elaborate, and 3 whose build aborts (Lean exit 134 under the node-budget `#guard`), each with its reason in
  [trust-allow.json](trust-allow.json).
- SIZE: 367 product (`Hooks/Acts.lean` 160, `acts_contract.py` 47, `wire_contract_faults_acts.py` 112, `acts@0.json`
  48), 193 tests (`test_acts_contract.py` 127, `test_wire_contract_s5_lean.py` 46, `contract_input_recorder.py` 20),
  other hand-written lines: about 520 (`sweep.py` 182, `seed_bugs.py` 116, `trust-allow.json` 44,
  `trust-classes.json` 32, the three seed and before texts 30, this report and DELTA.md); `git diff --numstat
  8eda0371fd`, generated files and saved JSON evidence left out.
- Lean: `lake build` (1406 jobs) and `python3 lean/audit.py` PASS (854 files, 9560 theorems) on the final Lean;
  `uv run python tools/regen_generated.py --write` once (40 entries; the Rust release binary pinned first with
  `--only checker-pins`, since `route-cases` runs it), `--check` 40 entries; `tools/gate_collection.py --check
  --prebuilt`: 7 added, 0 removed, 0 refused, stale or malformed.
- Tests while iterating: `tests/test_acts_contract.py` 10 passed; `tests/test_wire_contract_s5_lean.py -k acts`
  3 passed. Selected run: see section 7.
- Pilot bytes: 0 expected (shadow; no route reads the contract; nothing claimed before a pilot audit).
- Overlap: only the shared side table `tools/trust-classes.json` (branches ci-3, cmp-s3-cfr-1b, cmp-s3a-cfr-3,
  en-e3a-cutback, et-5b, norm-defaults-cfr-1b, ps-2ab-rule-firstob, me-1 also edit it; per-module entries).
- Spec re-read: the include form and `uses` against docs/spec/wire-contract.md:117 and :135, resolution and scopes
  against :258-260, inherited texts against :302-306; WC10's revision rule against :523; the `acts` block (`fixed`,
  `frames`, `adverbs`, `decodeVocab`) against docs/spec/act-phrases.md:367-388; D-31's order and texts against
  :1527-1553 (31a is the only ResourceLimit, so 1.1e is 31a alone); the profile row against act-phrases.md:571 (4.4).

## 5. Notes for the DRI

- `Hooks.Norms.ruleTyping` could take the environment as an argument (its owner's change); then `Hooks.Acts.ruleTyping`
  would be one line. Not done here: Hooks/Norms.lean stays byte for byte.
- `LIMIT_TEXTS` (ap-1bf review F3) is unchanged; the new members read no text in Python (Lean's decoder is the oracle).
- The rule phases' `ruleTyping` walks rules `0..i` for item `i` and decodes the environment per item, as
  `Hooks.Norms.ruleTyping` does: bounded by 2.2's rule count (charged first, in the included `profiles` phase) and the
  10,000-node total (the node-budget `#guard`, and the catalogue's `rules-limit`).
- ap-1bf review F4 (the "adapterof" typo, ap-1bf-f4) is not this item's.

## 6. Self-review against BUILDER-CHECKLIST

1. N.A.: no relayed answer is added or changed; no product path reads the `acts@0` diagnose row (DELTA preface).
2. PASS: section 1 lists every task line with its test; one-owner grep: no Python copy of a Lean text or limit
   (`test_the_limits_are_leans_and_never_copied`; seeded `py-d31-text-copied`); no permanent report test beyond R1's
   delta test (`test_the_saved_wording_delta_keeps_the_base_path_and_quoted_names`, which R1 asks for); overlap
   checked (section 4).
3. PASS: [mutants.json](mutants.json) 17 killed; [trust-mutants.json](trust-mutants.json) exit 0; the corpus
   comparator fails on a changed text (seed 1).
4. PASS: `test_the_recorded_corpus_gives_one_record_in_both_engines`, the catalogue tests in both engines, the sweep
   (before 4, after 2 differences).
5. N.A.: no Lean answer field is read by product Python.
6. PASS: the record for each fault is checked in full (`expected_record`); the sweep is saved on both sides.
7. PASS: DELTA rows cite R1, R16, R12 with their tests; no signature reserved.
8. PASS: DELTA.md lists the one changed record (R1) and the shadow diagnostics as evidence; route cases unchanged
   (`git diff --stat 8eda0371fd -- lean/VE/Route/examples tests/data` empty).
9. PASS: `uv run python tools/select_tests.py --base $(git merge-base HEAD main)` selects `tests/test_acts_contract.py`,
   `tests/test_wire_contract_s5_lean.py`, `tests/test_wire_gate_corpus.py`, `tests/test_wire_contract_rust.py`.
10. N.A.: no theorem added or changed.
11. PASS: limits charged first: 2.2 before the rule phases (`rules-limit`), 31a before the other D-31 conditions
    (`frames-over-with-bad-head`), the node total at its budget (`#guard` with `faultOf`); no sleep or deadline in
    the tests (the nested run uses `HANG_TIMEOUT`).
12. PASS (shadow): the classifier re-reads the frames once after a refusal; Python's oracle makes two Lean calls only
    after a non-limit refusal; no route runs it.
13. PASS: no test removed or renamed; `tools/gate_collection.py --check --prebuilt` 0 refused, stale, malformed.
14. PASS: opposite directions: at-limit sources clean and one over refused (`at_frames`, `frames-over`); a refusal
    before the frames stays 1.1d (`test_a_refusal_before_the_frames_is_not_theirs`); a clean rule (`#guard checkOf
    ... == none`) beside each refused one; spec re-read in section 4.
15. PASS: no overclaim (each count above names its file or command); no deliverable cut; every new check has a mutant
    (section 3); limits charged before work (item 11).

## 7. Selected tests

To be filled from the final selected run.
