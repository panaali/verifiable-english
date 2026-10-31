# ap-1bf build report: the `acts@0` wire contract, in shadow

**Status: built; no DRI signature is reserved; nothing stops the item.** The `acts@0` contract (revision 1, `shadow`)
names, for an environment the norms route refuses, the limit of `VE.Acts.Lexical` it broke (1.1a phrases, 1.1b phrase
bytes, 1.1c act bytes) or the decoder's other refusal (1.1d); both engines agree at and around each limit. DELTA has
one row (R16, untied V +61, K +0, S +0). Implements edit 2 of plan synthesis round 2 (shadow first, not switched on).
Open: ap-1bfb (section 5). Size: 767 hand-written lines, over the ~600 line (section 4).

Scope: ap-1be's REPORT section 5 (the ap-1bf paragraph) and ap-1bc's section 5 part (3); plan
[act-phrases-PLAN.md](../../spec/act-phrases-PLAN.md) 2.8; spec [act-phrases.md](../../spec/act-phrases.md) 3.1 and 12
(the limits). The task's "section 6 (the wire)" is AP-3's statements on main; the wire is 3 and the limits are 12.

## 1. Rows delivered

| Task part | Status | Where |
|---|---|---|
| (1) `Hooks/Acts.lean`: an `acts@0`-aware environment hook beside `Hooks/Norms.lean`'s (theirs unchanged) | done: `decoded` runs `decodeNormsEnvironment (acts := true)` and `decodeSource`'s `definitions@0` check; `member` names the limit whose own Lexical function (`decodeFixed`, `phraseToks`, `check`) gives exactly the decoder's text | `lean/VE/WireContract/Hooks/Acts.lean`; 30 `#guard`s |
| (1) its row in `Diagnose.lean` | done, with a guard on the unit list and the row | `lean/VE/WireContract/Diagnose.lean` |
| (1) limits read from `VE.Acts.Lexical`, never copied; a test fails if a copy appears | done: Lean reads `maxActBytes`, `maxPhraseBytes`, `maxPhrases`; Python finds each as the largest size Lean's decoder accepts | `tests/test_acts_contract.py::test_the_limits_are_leans_and_never_copied` |
| (2) `UNITS` row, registry module in `conformance/`, two examples, `acts@0.json` marked shadow | done | `tools/wire_contract.py`, `conformance/acts_contract.py`, `ve/wire_contract/examples/acts@0/{base,limit}.json`, `ve/wire_contract/acts@0.json` |
| (3) `conformance/wire_contract_faults_acts.py` writing the catalogue, generated through `regen_generated.py --write` | done: the regen entry `acts-fault-catalogue`; 7 faults at and around each limit | `conformance/wire-contract/acts@0-catalogue.json` |
| (4) tests, manifest, trust classes | done: 6 tests, both engines; `wire.diagnose` dispatch lists `Hooks/Acts.lean`; 3 modules in `tools/trust-classes.json` | `tests/test_acts_contract.py` |

## 2. Deviations

1. **The second example accepts, at the limits.** WC10 (`tools/wire_contract.py` `_check_unit`) requires every example
   to be accepted and clean, so `limit.json` holds a phrase of `maxPhraseBytes` and an act of `maxActBytes`; the
   refusing side one byte over is the catalogue's (`phrase-bytes-over`, `act-bytes-over`).
2. **Python finds the limits from Lean.** Lean's service exports no `VE.Acts.Lexical` limit and checklist 11 forbids
   reading Lean source, so `limits()` takes the largest size Lean's environment decoder accepts (doubling, then
   halving), with Lean as the oracle.
3. **The Python classifier reads Lean's text.** `acts_environment` names the member from the head and tail of the
   refusal Lean wrote (`LIMIT_TEXTS`), since the environment row carries no structured member; the engines' agreement
   is tested record by record (`test_every_fault_gives_its_member_in_python_with_leans_text`, `..._in_lean_...`).
4. **Environment only.** The table has no `norms@0` include: `Hooks.Norms.ruleTyping` reads `typingEnvironment`, which
   decodes without `acts`, so an included 4.7 would hold on every `acts@0` source. A refusal of the rules is the
   residual `ACTS_INVALID_INPUT` until ap-1bfb. `ve/norms_contract.py` `source` takes an `inside` domain (3 lines).

## 3. Seeded bugs

[mutants.json](mutants.json): **8, all killed** (Lean 4, Python 4; no Rust product code changed, only the generated
`contract_tables.rs`). Each was planted, run and restored by a scratch driver; the file records the first failure.

| Id | File (definition) | Bug | Killed by |
|---|---|---|---|
| `lean-limit-member` | `Hooks/Acts.lean` (`member`) | 1.1c named 1.1d | `Hooks/Acts.lean:119` `#guard` |
| `lean-decoder-without-acts` | `Hooks/Acts.lean` (`decoded`) | no `acts := true` | `Hooks/Acts.lean:118` `#guard` |
| `lean-count-off-by-one` | `Hooks/Acts.lean` (`member`) | `>` read as `≥` | `Hooks/Acts.lean:126` `#guard` (added for it) |
| `lean-hooks-no-classifier` | `Hooks/Acts.lean` (`hooks`) | no classifier | `Hooks/Acts.lean:139` `#guard` |
| `py-limit-text` | `conformance/acts_contract.py` (`LIMIT_TEXTS`) | 1.1c's tail misread | `test_every_fault_gives_its_member_in_python_with_leans_text` |
| `py-domain-open` | `conformance/acts_contract.py` (`in_domain`) | domain open | `test_the_adapters_read_acts_sources_of_the_norms_route_only` |
| `py-limit-oracle` | `conformance/wire_contract_faults_acts.py` (`_largest`) | limit one too high | `test_the_sources_at_each_limit_are_accepted_and_clean_in_python` |
| `py-limit-copied` | `conformance/acts_contract.py` | `400` in a comment | `test_the_limits_are_leans_and_never_copied` |

## 4. Trust, size, evidence and tests

- Trust: `uv run python tools/trust_map.py --check` against `11de39bd8`: K +0, S +0, untied V +61 (`Hooks/Acts.lean`
  +57, `Diagnose.lean` +2, `Tables/Acts.lean` +2); allowance in `docs/trust-baseline.json`, DELTA row 1 (R16).
- Trust mutants (13a, Mac/cloud, `--test` the hook and Diagnose modules, `--allow` [trust-allow.json](trust-allow.json)):
  [trust-mutants.json](trust-mutants.json) at `7a4ef55e8`: 109 KILLED, 0 SURVIVOR, 0 UNKNOWN, 26 ALLOWED (17 that do
  not elaborate, 9 equivalent: `isEmpty` cuts, sorted profiles, the table's unread `inherited` flags), 7 INVALID.
- Size (`git diff --numstat 11de39bd8`, generated files, the locks and the measured JSON left out): 767 lines. At the
  midpoint it was 421; the rest is R16's mutant fixtures and this evidence. Nothing more was cut, since the remaining
  part (ap-1bfb) does not shrink the delivered one.
- Lean: `lake build` (1184 jobs) and `python3 lean/audit.py` PASS on the final Lean; `regen_generated.py --write` (35
  entries), `tools.wire_contract --check` exit 0.
- Tests: `tests/test_acts_contract.py` 6 passed; wire lint, generator, Rust, norm-defaults and soft-norms contract
  files 71 passed. The selected run is in the final commit's message.
- Pilot bytes: 0 (shadow; no route reads the contract). Overlap: only shared side tables (`tools/trust-classes.json`,
  `ve/assurance-manifest.json`, `tools/regen_generated.py`), as earlier items.
- Spec re-read: the three limits and their owners against act-phrases.md:1796-1799; the `acts` block and `fixed`
  against 3.1 (361-372); `acts@0` read only under the profile against the plan's 2.8 (363-375).

## 5. Next items

**ap-1bfb**: the rule phases of `acts@0`: include `norms@0`'s profiles to semantic phases, with a typing environment
that reads `acts@0` (a new `typingEnvironment` beside `Hooks.Norms`'), their faults on `base.json`, and `frames` (AP-2,
`framesOk`) once the decoder admits them. Then ap-1bg (`acts@0` on the readings routes) and ap-4.

## 6. Self-review against BUILDER-CHECKLIST

1. N.A.: no relayed answer is added; no product path reads the `acts@0` diagnose row (DELTA preface).
2. PASS: section 1, each row with its file and test; generated files only through regen (`acts-fault-catalogue`).
3. PASS: [mutants.json](mutants.json) 8 killed; [trust-mutants.json](trust-mutants.json) exit 0.
4. PASS: `test_every_fault_gives_its_record_in_lean_and_the_sources_at_each_limit_are_clean` compares Lean's record
   with the oracle and its text with Python's legacy text; deviation 3 names the one text match.
5. N.A.: no Python reader of a Lean answer is added.
6. N.A. for the builder: the chain runs the gate on the final HEAD.
7. PASS: DELTA row 1 cites R16 with its trust-mutant evidence and FOLLOW-UPS row.
8. PASS: DELTA preface (no route case changed; no product caller of the unit).
9. PASS: `tools/select_tests.py --base 11de39bd8` selects 445 of 509 units (the service changed), including
   `tests/test_acts_contract.py`.
10. N.A.: no theorem added or changed.
11. PASS: limits fail closed at the decoder; the classifier reads each phrase and act once after a refusal (guards at
    `maxPhrases` with an act over its limit).
12. N.A.: diagnostic only, no pilot path; the at-limit sources (128 phrases) end in the tests' service call.
13. N.A.: no test removed.
14. PASS: both sides of every limit (`#guard`s at and one over each; the catalogue's faults and `at_count`,
    `at_limits`); spec re-read in section 4.
