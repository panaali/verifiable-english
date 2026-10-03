import VE.Readings.Run

/-- The `ve_readings_route` executable (docs/spec/composition-s1.md 8.4). -/
def main (args : List String) : IO UInt32 := VE.Readings.Run.main args
