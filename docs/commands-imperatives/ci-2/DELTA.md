# ci-2 delta: the `english.command` mode, no Python caller

Base `c3d9ea9380cb` (`git merge-base HEAD main` at this review fix). **Existing CLI and document verdicts and text: unchanged.** The service gains the mode
`english.command` (`VE.Commands.Run.caseReported`), so the handshake's mode list in
`ve/backends/lean_service_schema/envelope.json` names one more mode, and its schema `english.command.json` is new
(both generated, R12). No CLI command, document check, speech-acts path or conformance runner calls the mode: the
Python relay `read_command`, the source wrapper's fences and the deletions of Python's command branch,
`PROOF_TASK_ACT` and `legend`'s scope sentences are ci-2b's (REPORT.md, "Not delivered"). So no speech-acts test or
conformance case changes, and the A/B over the pinned command corpus has no record to compare yet: it is ci-2b's,
with the authority move (reviews/dri-decisions-20261028-commands-imperatives.md item 2(a)), R3's added fields and
the relay-binding rows (D9). The rows below record trusted-base growth and the forced source-identity raise.

The F1 refactor changes the source hash of `lean/VE/EnglishGrammar/Run.lean`. The grammar rules, verdicts and
diagnostic text are unchanged.

| # | Change | Evidence | Ruling |
|---|---|---|---|
| 1 | Trusted base: K +0, S +0, untied V +147: the original +141 plus `lean/VE/EnglishGrammar/Run.lean` +5 (`translationOf`, the shared formatter of an existing outcome) and `lean/VE/Commands/Read.lean` +1 (the outcome passed to it). The original files remain `lean/VE/Commands/Run.lean` +133, `lean/VE/Commands/Texts.lean` +2, `lean/ResponseShape/Skeletons.lean` +3, `lean/VE/Service/Protocol.lean` +1, `lean/VE/Service/Registry.lean` +1 and `lean/ResponseShape/Schemas.lean` +1. `tools/trust_map.py --check` passes with the +141 and +6 allowances in `docs/trust-baseline.json`. No Python decision path is deleted here. | The CI-2 `trust-mutants.json` and `mutants.json` exercise the original definitions. The review's injected-outcome `#guard` in `Read.lean` fails under the second-translation seed. `trust-mutants-review.json` exposed seven list truncation survivors; `trust-mutants-review-rescore.json` records ten killed after the complete-field guard in `RunExamples.lean` (three carried kills, seven rerun). The ties pass remains the FOLLOW-UPS.md row under "## ci-2". | SIGNED by standing ruling R16 (DRI-RULINGS.md) |
| 2 | `actions_version` 38 to 39 because base spec 2.12 requires a new source identity when `lean/VE/EnglishGrammar/Run.lean` changes. | `tools/english_grammar_gen.py --check` passes through `tools/regen_generated.py --check`; the 12 changed hashes in `lean/VE/Senses/RunExamples.lean` were recomputed from Lean's answers and `lake build` passes. All 18 ask fixtures were regenerated and replay against Lean. The 170 S3 comparator records were regenerated through `conformance.english_lean_s3_compare`; their report test passes. | SIGNED by the DRI 2026-11-02 (reviews/dri-decisions-20261102-jt-3p.md item 3) |
