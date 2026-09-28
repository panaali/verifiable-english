import VE.Time.Wire

/-! `ve_quantity`: the W6a quantity route (`VE.Time.Wire`). It is a separate
executable so the frozen `ve_conformance` subcommands stay byte-identical. -/
def main (args : List String) : IO UInt32 := VE.Time.Wire.main args
