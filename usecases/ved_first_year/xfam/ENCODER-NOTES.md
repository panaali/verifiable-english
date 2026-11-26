# Encoder notes: cases_xfam.py (ved-first-year, questions-enc.jsonl)

`python3 -I check.py out/cases_xfam.py` -> `OK: 35 cases, 100 questions encoded, 0 unsupported, 8 probes, 15 licences bridged`

## Counts
- Cases: 43 (35 in scope, encoded; 8 out of scope, V036-V043, left as probes)
- Vehicles: 73
- Questions: 100 encoded (Q1/Q2/Q3), 0 unsupported
- Probes: 8
- Licences bridged (Q2/Q3 licence dates): 15

## Conventions
- encode.py C1-C5 as they are written. Each V_FACTS / A_FACTS entry is true only where a case sentence states it; all other facts are false.
- Each case was read sentence by sentence. Every sentence maps to one fixed fact, or to none (licence durations, the no-rounding note, "not diesel", "not a taxi", Euro 6c). Any sentence the mapping did not recognise would have stopped the encoding; none did.
- Mappings:
  - "on the basis of an EU certificate of conformity / a UK approval certificate" -> basis_coc / basis_ukac
  - "identifies it as ... light passenger vehicle" -> cert_lpv
  - "specifies a CO2 emissions figure" -> cert_co2
  - "Its rate of CO2 emissions is zero" -> zero_rate
  - "constructed to be propelled by diesel" -> diesel
  - Euro 6d -> ind6d; Euro 6d-TEMP -> ind6dtemp (C3); Euro 6c -> neither
  - "has a list price of" -> has_lp + lp; "no list price; notional price" -> np
  - "was a taxi capable of zero emissions" -> taxi
  - A non-standard accessory attached at first registration under the Act -> a_nonstd + a_attached (+ a_has_lp when it has a list price); the stated price is copied
- Dates, CO2 figures and prices are copied as stated. No rate, band, total, duration or answer was computed.
- Q owners and Q2/Q3 licence dates come from each question's own text.

## Judgements
- V001: Ben: the certificate specifies a CO2 figure, but the facts state none (only a zero rate of emissions). co2 is left unstated, not typed as 0.
- V003: Ben: first registered under the law of Germany on 1 April 2025, before UK registration on 1 May 2025. dreg = the German date (V_UNITS dreg; 1GA(1)(a)). The basis is the certificate stated for that registration.
- V003: Ben: a UK approval certificate indicating Euro 6d is not an EU certificate of conformity, so ind6d / ind6dtemp are false (V_FACTS wording; 1GC(5)).
- V005: Alice: first registered under the law of France on 1 April 2025, before UK registration on 1 May 2025. dreg = the French date. The basis is the certificate stated for that registration.
- V010: Cara: the certificate specifies a CO2 figure, but the facts state none (only a zero rate of emissions). co2 is left unstated, not typed as 0.
- V011: Cara: the certificate specifies a CO2 figure, but the facts state none (only a zero rate of emissions). co2 is left unstated, not typed as 0.
