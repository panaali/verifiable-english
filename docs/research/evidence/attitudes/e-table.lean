-- removed before freezing (G4): []
-- Lean Table.reviewed: True
def frozenTable : VE.Attitudes.Table :=
  { candidates := VE.Attitudes.e1Words,
    lowerBound := [("almost certain", "E1.cert.almost-certain"), ("very likely", "E1.cert.very-likely"), ("quite likely", "E1.cert.quite-likely"), ("likely", "E1.cert.likely"), ("more likely than not", "E1.cert.more-likely-than-not")],
    above := [("almost certain", "very likely", "E1.pair.almost-certain.very-likely"), ("almost certain", "quite likely", "E1.pair.almost-certain.quite-likely"), ("almost certain", "likely", "E1.pair.almost-certain.likely"), ("almost certain", "more likely than not", "E1.pair.almost-certain.more-likely-than-not"), ("very likely", "quite likely", "E1.pair.very-likely.quite-likely"), ("very likely", "likely", "E1.pair.very-likely.likely"), ("very likely", "more likely than not", "E1.pair.very-likely.more-likely-than-not"), ("quite likely", "likely", "E1.pair.quite-likely.likely"), ("quite likely", "more likely than not", "E1.pair.quite-likely.more-likely-than-not"), ("likely", "more likely than not", "E1.pair.likely.more-likely-than-not")],
    factive := some "E2.factive",
    knowsBelieves := some "E2.knows-believes",
    knowsThinks := [("almost certain", "E2.knows-thinks.almost-certain"), ("very likely", "E2.knows-thinks.very-likely"), ("quite likely", "E2.knows-thinks.quite-likely"), ("likely", "E2.knows-thinks.likely"), ("more likely than not", "E2.knows-thinks.more-likely-than-not")] }
