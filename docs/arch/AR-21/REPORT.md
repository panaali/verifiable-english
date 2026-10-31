# AR-21: closure's replay is Core's replay on the embedding (consolidation step 3a, theorem only)

**For the DRI (a question, not a DELTA row; merging does not wait on it): plan row 3a's trace-decoder equality is
false.** Core's decoder reads an n-ary `atom` invariant that closure's refuses; `decodeTrace_ne_embed` is the
kernel-checked counterexample. That part stopped there. No hypothesis was added to it. Replay, step counts and the
per-version checker corollaries are proved. Trust is K, S and untied V +0. DELTA has R7 rows only.
`batch_evidence.py --check` passes every section except `[gate]`, which is saved after the chain's gate (see "After the gate").

Plan: architecture review 2026-10 (`design/arch-review` 6ae55ebb8), section 4.5, row AR-21 ("3a, theorem only"),
gate 4.1, coordination 4.2; `docs/CONSOLIDATION-PLAN.md` step 3, row 3a (line 334), with row 3b (line 335) for
what the theorem must support. Gate met: AR-20 merged. Statements for review: `STATEMENTS.md` (commit `66e99e55`,
before the proof work).

## Measured outcome

All numbers are against the merge base `e73ded83` and come from the tool outputs named here.

- **Lean.** One new proof module, `lean/VE/Closure/CoreEquiv.lean`, 676 lines. `tools/trust_map.py --files` classes it
  P 644 and o 32 (`evidence/trust.json`, `changed_files`). It is imported from `lean/VE.lean`. No existing definition
  or statement changed: `git diff e73ded834 HEAD --stat -- lean/VE` lists only `VE/Audit.lean` (generated) and the
  new file.
- **Statements.** `uv run python tools/lean_statements.py --diff` gives `statements.txt` 7,063 → 7,135 entries: 72
  added, 0 removed, 0 changed. The head file with the added entries deleted equals the base byte for byte
  (`evidence/statements.json`, `kept_byte_identical: true`). All 72 are `VE.Closure.CoreEquiv.*`. `predicates.txt`
  gains only the line `module VE.Closure.CoreEquiv` (the module declares no predicate).
- **Trust (D3).** `uv run python tools/trust_map.py --check`: "against e73ded83483a: K +0, S +0, D +0, G +0, tied +0,
  unclassified +0, trusted +0 ... PASS". K 994 → 994, S 12,152 → 12,152, untied V 43,904 → 43,904, trusted 57,050 →
  57,050. No allowance was added. P 94,817 → 95,461 (`evidence/trust.json`). Plan 4.1 item 3 asks Phase C for a
  reduction; this row is "none (theorem only)", and the reduction is AR-22's.
- **Behaviour (4.1 item 2).** `tools/lean_first_diff.py` over all nine corpora (base `e73ded83` from its own worktree,
  head `703f4156` from this checkout), compared by `python -m tools.evidence ab ... --delta evidence/ab-delta.json`:
  "ab PASS". The result: 100,504 records the same, 18 unavailable on both sides with identical outputs (R7), 0 unlisted.
  The two recordings are byte-identical (SHA-256 `3803e4f2…` for both, `evidence/ab.json`). In the full recording,
  8 whole-UDHR pilot records answered on the base and hit the recorder's 600 s time-out on the head (load average
  about 60). `docs/arch/AR-20/pilot_rerun.py` re-ran each of them on both sides at once, with the recorder's 600 s limit.
  All 8 came out the same: 5 answered identically and 3 timed out on both sides. Matching cases took about the same
  time on each side: 578 s against 585 s, and 505 s against 505 s (`evidence/pilot-rerun.json`). Those 8 outcomes
  replace the full recording's for both sides.
  `lean/checkers.lock` is byte-identical to the base's, so every checker binary is unchanged.
- **Build and audit.** `lake build`: "Build completed successfully (1180 jobs)". `python3 lean/audit.py`: "PASS: 683
  source files; 7702 named theorem declarations audited ...; only the declared standard axiom allowlist". The new
  theorems use only `propext`, `Quot.sound` and `Classical.choice` (`lean/axioms.txt`). No `sorry` (grep of the module
  for the audit's forbidden words is empty).

## The theorems

Exact statements and their plain-English readings: `STATEMENTS.md`. In `VE.Closure.CoreEquiv`:

| Plan row 3a asks | Delivered | Result |
|---|---|---|
| closure's `replay E a b` equals Core's on the embedding (`embedClosure`, `embedCert`), for all `a b` | `replay_embed` (any branch and trace, both flags, every fuel); `replay_certificate_embed` (from the initial branch, on `embedCert c`) | proved |
| the same for `Steps.closure` vs `Steps.core` | `steps_embed`: `Steps.core (embedTrace t) = Steps.closure t` | proved: the counts do not differ (the plan's named risk did not happen) |
| the same for the trace decoders | the equality `Core.Wire.decodeTrace fuel j = (decodeClosureTrace fuel j).map embedTrace` | **false**: `decodeTrace_ne_embed`, kernel-checked by `decide`. On `{"rule": "closure-induct@1", "at": 0, "sort": "s", "invariant": ["atom", "p", [c, c, c]], "children": []}` at fuel 125, Core decodes and closure answers `invalid indexed formula` (also seen with `#eval`). Stopped there, for the DRI |
| not the `checkCertificate` equality; per accepted version, closure's checker = Core's `replay` with closure's flag choice, on the embedding | `checkCertificate_eq_core_replay` (all versions); `checkCertificate_v0` (`replay E true false`); `checkCertificate_v1` (`replay E true true`); `checkCertificate_other_version` (false) | proved |

How it is proved. The embedding (`embedToken`, `embedTrace`, `embedCert`, `embedSigned`, `embedBranch`, plus
`embedEdge`, `embedRule`, `embedAtom`, `embedLiteral` and `embedPair` for the intermediate types) maps constructor to
constructor. It is class P in `tools/trust-classes.json`. Each function `replay` calls has one lemma saying that Core's
copy, applied to embedded arguments, returns the embedding of closure's answer: `next_embed`, `step_embed`,
`induct_embed`, `extra_embed`, `closed_embed`, `reachClosed_embed`, `complementary_embed` and their helpers, down to
`subst_embed` and `matches_embed` on formulas. Most are proved by case analysis. `replay_embed` is an induction on
fuel. The Core-only n-ary `atom` constructor never occurs in an embedded formula, so the extra Core cases never fire.
Injectivity of the embedding (`embedClosure_inj`, `embedToken_inj`, `embedEdge_inj`) carries the equality tests in
`complementary`, `composeStep` and `dedup`.

## What AR-22 may now delete

From plan row 3b: `VE/TableauExtended*` (6 files) and `Closure/{PathRules,Induction,Substitution,Congruence}`.
`wc -l` gives 1,548 lines. A grep of `import VE.<module>` shows that, outside that set and `VE/Audit.lean`, only
`VE/Route/Steps.lean`, `VE/Route/Checker.lean`, `VE/CertificateWire.lean` and this batch's
`VE/Closure/CoreEquiv.lean` import any of it. The theorems support the deletion this way:

1. **The replay and the checker.** Closure's checker can be defined as its own version gate, then Core's `replay`
   with flags `true` and `(version == @1)`, applied to the embedding. `checkCertificate_eq_core_replay` is exactly
   that definition's equation, so `@0` certificates keep their verdicts (`checkCertificate_v0`).
2. **Step counts.** Equal (`steps_embed`), so `Steps.closure` can become `Steps.core ∘ embedTrace` without changing
   any step-limit refusal. Keeping `Steps.closure` as it is also stays correct.
3. **Not supported: the trace decoder.** Deleting `VE.CertificateWire.decodeClosureTrace` in favour of Core's
   `decodeTrace` would widen what closure accepts (n-ary atom invariants). It would also change the refusal text,
   `invalid indexed formula` against `Atom terms must be an array of three to six terms` or a decoded atom
   (`decodeTrace_ne_embed`). Plan 3b's "one of the three trace decoders" therefore needs the DRI: either AR-22 keeps
   closure's decoder, or the DRI approves an atom-free gate with identical refusal text, with its own statement. The
   true part, that whenever closure's decoder returns `ok t` Core's returns `ok (embedTrace t)`, is not stated here,
   because stating it would add a hypothesis to the plan's statement (DRI-RULINGS "never covered"). It is a candidate
   if the DRI wants it.
4. **Types.** The closure `Trace` and `Certificate` types live in `VE/TableauExtended.lean`, and `CertificateWire`,
   `Route/Steps` and this module use them. AR-22 moves or keeps them. The lemmas here about closure's `Branch`,
   `Signed` and `next` go with the replay they describe, and `checkCertificate_eq_core_replay` becomes the closure
   checker's defining equation.

## Plan rows and directives

| Line | Commit | Evidence |
|---|---|---|
| Statements in `docs/arch/AR-21/STATEMENTS.md` before the proof work | `66e99e55` | `STATEMENTS.md` |
| 1. Replay equality, both flags explicit | `56917a0f` | `replay_embed`, `replay_certificate_embed`; mutants M1, M2, M3, M6 |
| 2. Trace decoders; `Steps.closure` vs `Steps.core` | `56917a0f` | `steps_embed` (M4); decoders false: `decodeTrace_ne_embed` (M7) |
| 3. No `checkCertificate` equality; the per-version corollary | `56917a0f` | `checkCertificate_eq_core_replay`, `_v0`, `_v1`, `_other_version` (M5) |
| 4. Step counts: report where they differ | n/a | they do not differ (`steps_embed`) |
| New proof module imported from `lean/VE.lean`; no existing definition or statement changed; only P-class lines | `56917a0f`, `d2573757` | `evidence/statements.json`; `evidence/trust.json` (the file is P 644, o 32) |
| `lake build`, `lean/audit.py`, axiom audit; no new axiom, no `sorry` | all | outputs quoted above |
| New theorems in `statements.txt` through the generator; the diff only adds them | `d2573757` | `regen_generated.py --write` ("wrote 34 entries"), then `--check` ("checked 34 entries"); `lean_statements.py --check`: "PASS: 7135 statements ... unchanged" |
| Inventories, trust classes, audit manifests and checker pins only through `regen_generated.py --write` | `d2573757` | `tools/trust-classes.json` has no writer (`trust-tables [json]`, "write: -"). Its entry gives the 11 embedding defs P, as `VE/Order/Conservativity.lean`'s `embed` (and as AR-20 did for its entries). `python3 tools/rust_build.py --check` and `regen_generated.py --check --only checker-pins` pass; `checkers.lock` is unchanged |
| No user-visible change; no Python or Rust change | all | A/B 0 unlisted. The one `ve/` edit is a classification row in `ve/assurance-manifest.json`'s `other_json` (`1faafe1a`), which only `tests/test_assurance_manifest.py` reads (grep of `other_json` in `ve/` and `tools/` is empty) |
| Trust (D3): K, S, untied V each unchanged, no allowance | `d2573757` | `trust_map.py --check` PASS, +0 each |
| Seeded bugs (Lean): at least two in the closure copy, the new theorem no longer builds | `703f4156` | 7/7 killed (below) |
| Evidence in `docs/arch/AR-21/` with `evidence.toml`, each file under 1 MB, `batch_evidence.py --check` | `e447656c` and the after-gate commit | largest file `evidence/pilot-rerun.json`, 924,408 bytes |
| Coordination: files against every branch in flight | start | below |

Coordination. At the start, `git diff --name-only main...<branch>` for every `lean-first/*`, `feature/*`, `infra/*`
and `foundation/*` branch, against this batch's files (`lean/VE/Closure/*`, `lean/VE/Core/*`,
`lean/VE/TableauExtended*`, `lean/VE.lean`, `lean/statements.txt`, `docs/arch/AR-21/*`). The only overlaps were
`lean/VE.lean` (union merge driver: ap-2bb, ap-3d, ap-4a, cmp-s2b, pc-3, me-1) and the generated `statements.txt`
(R12). No branch touches `lean/VE/Closure`, `lean/VE/Core` or `lean/VE/TableauExtended*`. `ve/assurance-manifest.json`
was added later, after a failing selected test. It is a shared manifest whose new row is append-only.

## Seeded bugs

`docs/arch/AR-21/mutants.json`, run by `uv run python tools/mutants.py docs/arch/AR-21/mutants.json --evidence
docs/arch/AR-21/evidence/mutants.json`: "mutants: 7/7 killed". The command of each is `lake build
VE.Closure.CoreEquiv`. Each mutant keeps its own file's proofs building (closure's soundness proofs included). The
failing build line is in the new module every time:

| Id | File | Seeded bug | Failing build line |
|---|---|---|---|
| M1 | `lean/VE/TableauExtendedChecker.lean` | closure's reach-unfolding step also refuses index 7 | `CoreEquiv.lean:488:4: unsolved goals` (`next_embed`) |
| M2 | `lean/VE/TableauExtendedRules.lean` | `isReach` drops body reaches | `CoreEquiv.lean:361:14: Tactic rfl failed` (`isReach_embed`) |
| M3 | `lean/VE/TableauExtendedChecker.lean` | `replay` ignores its induction flag | `CoreEquiv.lean:572:16: Tactic rfl failed` (`replay_embed`) |
| M4 | `lean/VE/CertificateWire.lean` | `closureSteps` counts an induction node 2 | `CoreEquiv.lean:601:24: unsolved goals` (`steps_embed`) |
| M5 | `lean/VE/TableauExtendedChecker.lean` | the version gate accepts `@2` instead of `@0` | `CoreEquiv.lean:625:34` (`checkCertificate_eq_core_replay`), `:660:64` (`checkCertificate_other_version`) |
| M6 | `lean/VE/Closure/CoreEquiv.lean` | `embedTrace` drops an expansion's parameter | `CoreEquiv.lean:566:16: Tactic rfl failed` (`replay_embed`) |
| M7 | `lean/VE/Core/Bridge.lean` | Core's formula decoder no longer reads `atom` | `CoreEquiv.lean:674:2: Tactic decide proved that the proposition ...` is false (`decodeTrace_ne_embed`) |

Only Lean product code changed (Python and Rust: none), and M6 is in the one Lean file this batch added. After the
run, `git status` showed the sources restored, a full `lake build` passed (1180 jobs), and the checker pins still
matched.

## Tests

- Selected tests, once, on the finished code: `zsh .../mac-pytest.sh --select -- --base e73ded83 --run`. It ran
  81 units on 4 GitHub Actions shards. 80 passed and 1 failed:
  `tests/test_assurance_manifest.py::test_every_json_handling_lean_file_is_classified`. The new module builds JSON
  (its counterexample), and the manifest had not classified it. Fixed in `1faafe1a`. The file then passed:
  `uv run pytest -q tests/test_assurance_manifest.py`, "138 passed". No main-known-red test was selected.
- `uv run python tools/gate_collection.py --check --prebuilt`: "30735 collected, 30735 at e73ded83...; 0 added, 0
  removed by a trailer, 0 refused, 0 stale and 0 malformed trailers". No test was removed or renamed.
- `uv run python tools/check_lean_imports.py`: "Lean layer graph kept (683 modules, 22 reviewed legacy edges)". The
  new module is layer 2 (`tools/layer_policy.py`, the `VE.*` default), and every module it imports is layer 1 or 2.
- Not run by me: the full gate (`tools/gate.py`). The chain runs it on the final HEAD.

## After the gate

The scope, the A/B and the gate must name the commit the chain gates (`<G>`). After that gate, make one report
commit that changes only `docs/arch/AR-21/`:

    cp gate-result.json docs/arch/AR-21/evidence/gate.json
    uv run python -m tools.evidence scope --base main --head <G> --out docs/arch/AR-21/evidence/scope.json
    uv run python -m tools.evidence ab ~/.cache/ve-ar21-ab/base-rerun.jsonl ~/.cache/ve-ar21-ab/head-rerun.jsonl \
        --base-commit e73ded83483ad43164d596e1fe910e9bc60c2b2e --head-commit <G> \
        --out docs/arch/AR-21/evidence/ab.json --delta docs/arch/AR-21/evidence/ab-delta.json \
        --corpus probe conformance readings pilots discourse rights quantity norm_defaults document
    uv run python tools/batch_evidence.py --check docs/arch/AR-21 --report-commit HEAD

The head recording was made at `703f4156`. From there to `<G>`, `lean/` and `rust/` are unchanged, and `ve/` changes
only by the one `other_json` row of `ve/assurance-manifest.json`, which no operation reads. Every other commit after it
changes only `docs/arch/AR-21/`.

## Spec re-read

- `replay_embed` and `replay_certificate_embed` against `docs/CONSOLIDATION-PLAN.md:334`: "closure's `replay E a b`
  on a certificate equals Core's `replay E a b` on its embedding (`embedClosure`, `embedCert`), for all `a b`". Both
  flags are universally quantified, `embedClosure` is the existing one, and `embedCert` is new.
- `steps_embed` against the same line: "`Steps.closure` vs `Steps.core`". These are `VE.Route.Steps.closure` and
  `VE.Route.Steps.core` (`lean/VE/Route/Steps.lean:23,26`).
- `decodeTrace_ne_embed` against the same line, "the same for the trace decoders". These are the closure decoder
  (`lean/VE/CertificateWire.lean:182`) and Core's (`lean/VE/Core/Wire.lean:62`).
- The checker corollaries against `docs/CONSOLIDATION-PLAN.md:334`, `lean/VE/Core/TableauExtendedChecker.lean:223-225`
  and `lean/VE/TableauExtendedChecker.lean:223-226`: Core accepts only `ve-tableau-core-checker@1` and runs
  `replay E true true`; closure accepts `@0` and `@1` and runs `replay E true (version == @1)`. The corollaries
  restate closure's own gate and flag and do not claim equality with Core's checker.
- Row 3b (`docs/CONSOLIDATION-PLAN.md:335`): "keeping closure's own version gate (`@0` and `@1`, second flag
  `version == @1`) so `@0` certificates keep their verdicts". `checkCertificate_v0` is that statement, on the
  embedding.

## Self-review against BUILDER-CHECKLIST

1. Every Lean answer typed and contained: N.A. No relay, schema, route or binding changed (A/B 0 unlisted,
   `evidence/ab.json`).
2. Every deliverable built, no rule broken: PASS. "Plan rows and directives" maps each line to a commit and its
   evidence. The decoder part is false and stopped with a counterexample (`decodeTrace_ne_embed`). There is no Python
   copy of a Lean decision, no report test and no authority switch, and coordination found no overlap.
3. Tests can fail: PASS. 7/7 seeded mutants were killed, each failing in `VE.Closure.CoreEquiv` with its own file's
   proofs intact (`evidence/mutants.json`). Trust mutants (13a): N.A., because there is no trusted growth (trust +0).
4. Python, Lean and Rust agree; valid inputs pass: PASS. The corpus A/B over the nine corpora has 0 unlisted records,
   and the recordings are byte-identical (`evidence/ab.json`).
5. R8 binding: N.A. No field read from a Lean answer changed.
6. Gate evidence matches the final HEAD: PASS for the parts this batch can do. The scope base is
   `git merge-base HEAD main` (`e73ded83`), and the after-gate steps above re-save the scope, the A/B and the gate
   for `<G>`. Main has not moved since the start (`git log -1 main`: `e73ded83`).
7. No unsigned item: PASS. `DELTA.md` has R7 rows only, and the trust budget is +0. The decoder question is not a
   DELTA row; it is listed first.
8. Every user-visible change in DELTA: PASS. The A/B diff is empty apart from the R7 pairs, all listed in
   `evidence/ab-delta.json`.
9. Test selection finds the affected tests: PASS. `tools/select_tests.py` selected 81 of 505 units, not all. One
   selected test (`test_every_json_handling_lean_file_is_classified`) caught a real gap.
10. Lean statements say what is claimed: PASS. Mutants M1–M7 break the build of the theorem each guards. No hypothesis
    was added to a false statement; the false one has a mechanised counterexample. `lean_statements.py --check` PASS.
11. Budgets fail closed: N.A. No budget, limit or deadline changed.
12. No CPU or memory regression: PASS. The checker binaries are unchanged (`checkers.lock`). The whole-UDHR rerun
    took about the same time on each side: 578 s against 585 s, and 556 s against 524 s (`evidence/pilot-rerun.json`).
13. Removed tests have trailers: PASS. `gate_collection.py --check --prebuilt` reports 0 removed, 0 refused, 0 stale
    and 0 malformed.
14. Both directions, cited evidence, spec re-read: PASS. Each equality is checked both ways by a mutant on either
    side of it (closure side M1–M5, embedding M6). The counterexample's dependency on Core's atom case is shown by
    M7. Every claim above cites its command output, and the spec re-read is listed above.
