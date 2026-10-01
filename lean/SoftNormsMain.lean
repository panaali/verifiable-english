import VE.SoftNorms.Run

/-- The `ve_soft_norms_route` executable (docs/spec/soft-norms.md 9.4). -/
def main (args : List String) : IO UInt32 := VE.SoftNorms.Run.main args
