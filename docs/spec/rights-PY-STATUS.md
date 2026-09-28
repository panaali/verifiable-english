# Rights Python implementation status

This branch implements a Python subset of [rights.md](rights.md) without changing the W1 or soft-norms contracts. The generated soft tree is replayed by the existing Lean soft route; there is no Lean rights route on this branch.

| Plan item | Implemented | Remaining |
|---|---|---|
| 2, profile | Identity-bound `rights@0` environment block; incident shapes, fan-out, power split, limitations, bar; generated `E″`, soft `T″`, and `Lim_D`; rights background model validation; document check of the correlated soft tree | Rights-specific graph admission and certificates; full citation and limitation-scope audit; generated predicates in authored guards |
| 3, English | Strict and default claim, liberty, and immunity incident sentences reuse the P0-audited soft rule parser; read-only wordings for right, limitation and bar units | Full W7 inverse grammar for right headers, `includes`, limitations, bar, coupling, fan-out and passive rewrite; complete surface registrations |
| 5, coverage | Axis, limitation, bar, power-shadow, narrowing and coupling counts; compatible coupled-choice enumeration and `conditional_on` for checked assertion choices | Verified separating situations for right-block candidates; per-certificate limitation premises used; full licensing and non-discrimination findings |

The document check rejects a rights graph rather than admitting it without the rights route. Multi-candidate right readings with unverified separating models are rejected. These boundaries keep an unsupported certificate from appearing checked.

Reproduce the implemented conformance checks with `uv run --offline python conformance/rights.py` after `lake build` in `lean/`.
