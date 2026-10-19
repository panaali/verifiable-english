/-! The v0 runtime envelope, once (docs/LEAN-FIRST-PLAN.md, batch 18). These bounds are not
logical axioms. Every non-frozen Lean check reads them from here, and the service states them in
its handshake (`VE.Service.handshake`, member `limits`), from which the response schema
(`envelope.json`) pins them and Python reads them (`ve/limits.py`): Python keeps no copy.
`tests/test_lean_limits.py` fails on a limit's literal in a non-frozen check (lf-18 review F2).

The limits are reducible, so an approved theorem statement that names a limit's value (a node
total at most 10000, a decoder at depth 64) is unchanged and its proof still holds for the check
that reads the limit; a changed limit no longer fits those statements, so the build fails.

The hash-frozen decoders (`VE.Json`, `VE.Bridge`, `VE.Order.Wire`, `VE.CertificateWire`;
architecture decision D2) and the English lexer, hashed by the grammar lock
(`tools/english_grammar_gen.py`), keep the literals they were frozen with; `VE.LimitTies` checks
that they are these values. -/
namespace VE.Limits

/-- Longest source text, in UTF-8 bytes. -/
abbrev maxSourceBytes : Nat := 65536
/-- Longest JSON package (`VE.JsonInput.parse`'s frozen cap). -/
abbrev maxPackageBytes : Nat := 16777216
/-- Deepest formula or term nesting. -/
abbrev maxDepth : Nat := 64
/-- Most AST nodes in one formula document. -/
abbrev maxNodes : Nat := 10000
/-- Most sorts of an environment. -/
abbrev maxSorts : Nat := 32
/-- Most predicates of an environment. -/
abbrev maxPredicates : Nat := 256
/-- Most entities of one sort's domain. -/
abbrev maxEntities : Nat := 1000
/-- Most relation tuples of a model, in all. -/
abbrev maxTuples : Nat := 100000
/-- Longest identifier, in ASCII bytes. -/
abbrev maxIdentifierBytes : Nat := 64
/-- The largest evaluation budget a request may ask for. -/
abbrev maxEvaluations : Nat := 1000000
/-- The largest de Bruijn index (the largest integer every JSON reader holds exactly). -/
abbrev maxIndex : Nat := 2 ^ 53 - 1
/-- Deepest JSON nesting (`VE.JsonInput.parse`'s frozen default). -/
abbrev maxJsonDepth : Nat := 256
/-- Longest accepted service request line, as the one-shot runners' input cap. -/
abbrev maxLineBytes : Nat := 16777216
/-- Most cases in one service request. -/
abbrev maxCases : Nat := 4096
/-- Longest decimal numeral of the order and time wires. -/
abbrev maxNumeralChars : Nat := 40

/-- The limits the service states in its handshake, by their wire names: the response schema
requires exactly these values, and Python reads them from there. -/
def stated : List (String × Nat) :=
  [("max_source_bytes", maxSourceBytes), ("max_package_bytes", maxPackageBytes), ("max_depth", maxDepth),
    ("max_nodes", maxNodes), ("max_sorts", maxSorts), ("max_predicates", maxPredicates),
    ("max_entities", maxEntities), ("max_tuples", maxTuples), ("max_identifier_bytes", maxIdentifierBytes),
    ("max_evaluations", maxEvaluations), ("max_index", maxIndex), ("json_depth", maxJsonDepth),
    ("max_line_bytes", maxLineBytes), ("max_cases", maxCases)]

end VE.Limits
