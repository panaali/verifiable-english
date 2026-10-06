import VE.EnglishGrammar.Run

/-- The `ve_english_route` executable (docs/spec/english-lean-s2.md 2.10). -/
def main (args : List String) : IO UInt32 := VE.EnglishGrammar.Run.main args
