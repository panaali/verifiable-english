# ci-2 delta: the `english.command` mode, no Python caller

Base `94580b39b` (`git merge-base HEAD main`). **Public output: none.** The service gains the mode
`english.command` (`VE.Commands.Run.caseReported`), so the handshake's mode list in
`ve/backends/lean_service_schema/envelope.json` names one more mode, and its schema `english.command.json` is new
(both generated, R12). No CLI command, document check, speech-acts path or conformance runner calls the mode: the
Python relay `read_command`, the source wrapper's fences and the deletions of Python's command branch,
`PROOF_TASK_ACT` and `legend`'s scope sentences are ci-2b's (REPORT.md, "Not delivered"). So no speech-acts test or
conformance case changes, and the A/B over the pinned command corpus has no record to compare yet: it is ci-2b's,
with the authority move (reviews/dri-decisions-20261028-commands-imperatives.md item 2(a)), R3's added fields and
the relay-binding rows (D9). The one row is the trusted-base growth.

| # | Change | Evidence | Ruling |
|---|---|---|---|
| 1 | Trusted base: K +0, S +0, untied V +141: `lean/VE/Commands/Run.lean` +133, `lean/VE/Commands/Texts.lean` +2 (`proofAct`), `lean/ResponseShape/Skeletons.lean` +3, `lean/VE/Service/Protocol.lean` +1, `lean/VE/Service/Registry.lean` +1, `lean/ResponseShape/Schemas.lean` +1 (`uv run python tools/trust_map.py --check`: PASS with the allowance in `docs/trust-baseline.json`). `ofPart`, `Run.message`, `Texts.queryMismatch` and `Schemas/Command.lean` are G[R], `Run.holeStart` G[I], `RunExamples.lean` T. No part is R6's: no Python decision path is deleted here | Every new trusted definition is exercised: `docs/commands-imperatives/ci-2/trust-mutants.json` with its allow file, and `mutants.json`; the ties pass is the FOLLOW-UPS.md row under "## ci-2" | SIGNED by standing ruling R16 (DRI-RULINGS.md) |
