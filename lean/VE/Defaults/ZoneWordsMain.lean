import VE.Defaults.ZoneWire

/-- `ve/defaults_words.json`: the words of DE10 to DE13 (`VE.Defaults.Wire.zoneWordsJson`). -/
def main : IO Unit := IO.println VE.Defaults.Wire.zoneWordsJson.compress
