# Batch 13a deletion ledger

Base: `7345e3ed`. The Lean service owns the decisions below. Python keeps input container construction and converts the service's bound answer into the existing public record.

| Deleted Python decision | Lean owner and caller |
|---|---|
| `entailment._trace_nodes`: one replay charge per trace node | `VE.CertificateWire.folSteps` and `.closureSteps`, with `VE.Route.Steps.core` and `.order` for their families; certificate routes return `steps`. `_check_certificate_lean` and `_norm_certificate_lean` consume that field. |
| `entailment._replay_prechecks`: wire fields and stale binding | `VE.CertificateWire.certificateFields`, family certificate decoders, and `VE.Route.Wire.bindingOk` (including core, order and norms routes). The Lean callers send the whole envelope. |
| `entailment._replay_prechecks`: replay budget and premature result | `VE.CertificateWire.limit` and `.stepLimit` own the budget; `VE.Route.Steps` re-exports them to the core and order runners. The Python callers send `max_steps` where the public operation takes it. |
| `entailment._lean_replay_record`: response validity, replay count, and below-budget uncertainty | Lean answers `valid` and `steps` or a bound `ResourceLimit`; the relay checks the producer-derived response shape. Python maps that answer to the existing `EntailmentCertificateCheck` display record. |
| `parser._parse_lean`: Python's rejection and wording arbitration through `validation.decided` | `VE.Service.Standalone.reportedParse` and `VE.Service.ParseDiagnostic.scan` answer rejections with Lean code, text and span. Python constructs an AST only after Lean accepts and treats disagreement as `CheckerUnavailable`. |
| Order parse lacked a canonical answer, leaving its text to the Python comparison | `VE.Order.Surface.print` supplies the order family's canonical text in the service parse row. |

`rg` finds no consumer of `_trace_nodes`, `_replay_prechecks`, or `_lean_replay_record`. The default Python authority's replay remains until the planned core-operation switch in 13b; the prover-internal replay has the separate batch-15 measurement gate. Definitions surface sugar is also assigned to 13b. No Rust decision site changed in 13a.
