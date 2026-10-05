import VE.WireContract.Diagnose

/-- The `ve_diagnose` executable (docs/spec/wire-contract.md 4.2). -/
-- Its assurance bindings select "soft-norms@0", "norms@0" or "norm-defaults@0".
def main (args : List String) : IO UInt32 := VE.WireContract.Diagnose.main args
