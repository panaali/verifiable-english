import VE.SpeechActs.Source.Admission.Run

/-- The `ve_speech_acts_route` executable (docs/spec/speech-acts.md 8.6), with the decoded-source wrapper's
`speech-source` kind (8.5). -/
def main (args : List String) : IO UInt32 := VE.SpeechActs.Source.main args
