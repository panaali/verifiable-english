# Rights integration status

The Python profile and Lean rights route are merged on `rights/integrate`. Rights
correlation is checked against the soft Lean route, and the document report
replays the independent rights Lean route. The original soft-norms Lean sources
remain the merged `soft/build` versions.

| Area | Implemented | Remaining |
|---|---|---|
| Profile and W2 | Identity-bound rights block; incident shapes, fan-out, power, limitations, bar, generated vocabulary and premises; labelled couplings; checked finite separating situations for complete standalone right readings; authored guards may name generated limitation and condition predicates | Rights-path graph admission and certificate theorem; per-choice elaboration with other rights units and limitations; graph leaves for rights and coupling labels |
| English | Strict and default incident sentences reuse the soft grammar; readable right, limitation and bar unit wording | Inverse grammar for complete right headers, includes, limitations, bar, fan-out, coupling and passive rewrite |
| Reports | Lean-replayed scope licensing, distinction hits, bar rows and conflict status in document checks; coverage counts; right-route certificate replay reports `conditional_on` when supplied | Document-level certificate submission and per-certificate limitation usage; automatic conflict and scope certificate search; full example-situation narratives |
| Conformance | Ten fixture shapes compare Python correlation, Lean rights elaboration and Lean soft elaboration; Lean build-time fixture guards and end-to-end certificate replay | Ternary μ and ψ (Lean's current formula language is binary); exhaustive acceptance fixtures and per-choice W2 verdicts |

The rights route rejects W2 graph admission explicitly. Document checks do not
present such a graph as admitted. A right reading set is reported as pending
per-choice elaboration if its candidates would change the rights tree. These
boundaries keep unchecked certificates and readings out of a checked verdict.

Run `python conformance/rights_three_way.py` after `lake build` to regenerate
`conformance/rights-three-way-report.json`.
