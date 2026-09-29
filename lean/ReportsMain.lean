import VE.Attribution.Run

/-- The `ve_reports_route` executable (docs/spec/attribution.md 9.4). -/
def main (args : List String) : IO UInt32 := VE.Reports.Run.main args
