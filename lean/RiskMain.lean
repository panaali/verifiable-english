import VE.Risk.Run

/-- The `ve_risk_route` executable (docs/spec/risk.md 7.3). -/
def main (args : List String) : IO UInt32 := VE.Risk.Run.main args
