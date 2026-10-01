import VE.Discourse.Run

/-- The `ve_discourse_route` executable (docs/spec/discourse.md 9.7). -/
def main (args : List String) : IO UInt32 := VE.Discourse.Run.main args
