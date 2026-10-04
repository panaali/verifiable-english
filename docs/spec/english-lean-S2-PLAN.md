# English in Lean, stage S2 (pointer plan)
Item 1 of THIS plan is stage S2 of docs/spec/english-lean-PLAN.md ("English instance": lexer, fixed-rule JSON and generator, lexRules, Lexicon.valid, actions, english.read, shadow wiring; base constructs, contractions, validated negatives, coordination, closure, natural clauses), building on S0 + S1a/S1b (branch english-lean/integrate; merging as ve-green-english-lean).
Apply that plan's S2 row exactly, with these DRI amendments (lead directive 2026-10-04, no duplicated logic; LEAN-FIRST-PLAN.md English track E1-E2):
- Lean owns the grammar and the one-reading decision. Python does NOT get a generated copy of the grammar; Python's English path calls Lean (service) once S5 lands. Keep the existing Python parser only as the comparator until then.
- The S4 14-day shadow is replaced by corpus evidence (the 85,000 English pairs, use cases, pilots) per LEAN-FIRST-PLAN E2.
- Include the readability-eval writing gaps as fixtures (ARCH-ROADMAP 'English grammar coverage'): "For every X, if A and B, then C"; "A or B, or both"; the negated-existential error message; prohibition written as an exception to a default.
- DRI rulings 1-6 in ~/code/manage-agents/english-lean-dri-note.md stay in force.
Honest open questions.
