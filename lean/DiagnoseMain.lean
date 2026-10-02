import VE.WireContract.Diagnose

/-- The `ve_diagnose` executable (docs/spec/wire-contract.md 4.2). -/
def main (args : List String) : IO UInt32 := VE.WireContract.Diagnose.main args
