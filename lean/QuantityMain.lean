import VE.Time.Document

/-! `ve_quantity`: the W6a quantity route (`VE.Time.Wire`, `VE.Time.Document`). It
is a separate executable so the frozen `ve_conformance` subcommands stay
byte-identical. -/
def main (args : List String) : IO UInt32 := VE.Time.Document.main args
