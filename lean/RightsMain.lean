import VE.Rights.Run

/-- The `ve_rights_route` executable (docs/spec/rights.md 9.4). -/
def main (args : List String) : IO UInt32 := VE.Rights.Run.main args
