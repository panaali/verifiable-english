import VE.Norms.Run

/-- The `ve_norms_route` executable (docs/spec/norms.md 11.4). -/
def main (args : List String) : IO UInt32 := VE.Norms.Run.main args
