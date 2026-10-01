import VE.SpeechActs.Run

/-- The `ve_speech_acts_route` executable (docs/spec/speech-acts.md 8.6). -/
def main (args : List String) : IO UInt32 := VE.SpeechActs.Run.main args
