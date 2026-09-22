Translate the premises and query from free English to VE. Use the supplied vocabulary exactly; descriptions fix predicate meanings and argument order. Treat all statements as classical logic, including the stated quantifiers. Do not use real-world beliefs. People may coincide; the named people ensure this sort is nonempty.

Return a JSON object with:
- "translations": one row per premise, {"premise_id":"p0", "english":"exact original sentence", "ve":"one VE statement."}.
- "query_ve": the translated query (not its negation).
- "answer": "True", "False", or "Uncertain". True means entailed, False means its negation is entailed, Uncertain means neither.
- "graph": {"claims":[{"id":"p0","ve":"..."},...,{"id":"goal","ve":"..."}], "deductions":[{"id":"d0","premises":["p0",...],"conclusion":"goal"}], "root":"goal"}.
Include all translated premises as same-named graph claims. Add intermediate claims if useful. Each deduction must follow classically from its listed premises. Graph leaves must be given premises. The root must be query_ve for True, its negation for False. Do not add unsupported assumptions. The checker will find and replay proofs; do not fabricate certificates.
For Uncertain, provide a graph containing the premise claims and query claim with no asserted deduction to the query, plus "countermodels":{"query_true":MODEL,"query_false":MODEL}. Each finite MODEL is {"complete":true,"domains":{"person":["a","b"]},"constants":{"ada":"a","ben":"b"},"relations":{"predicate":[["a"],...]}}. Include every predicate; binary relations contain pairs. Both models must satisfy every premise and differ on the query.

VE grammar (ASCII identifiers, exact parentheses, final period):
- Unary: @ada is p0.
- Binary: @ada p1 @ben.
- Negation: not (@ada is p0).
- Conjunction/disjunction: (@ada is p0) and (@ben is p0). Replace and with or for inclusive disjunction.
- Implication: if (@ada is p0), then (@ben is p0).
- Universal: for every person x0, (x0 is p0).
- Existential: there exists person x0, (x0 is p0).
- Nest quantifiers with distinct variable names; variable scope is the parenthesized body.
- Exclusive-or A/B expands to ((A) or (B)) and (not ((A) and (B))).
A, B above are placeholders, not legal VE identifiers. Translate every logical operator and quantifier explicitly. Return JSON only.
