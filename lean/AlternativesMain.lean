import VE.Alternatives.Run

/-- The `ve_alternatives_route` executable (docs/spec/alternatives.md 7.3). -/
def main (args : List String) : IO UInt32 := VE.Alternatives.Run.main args
