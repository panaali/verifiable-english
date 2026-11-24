# ENCODER-NOTES: cases_xfam.py (RTOA 1988 s.35, England and Wales)

`python3 -I check.py out/cases_xfam.py` -> `OK: 35 cases, 7 probes`

## Counts
- 42 ids: 35 in-scope records in CASES (Z001-Z035), 7 probes in PROBES (Z036-Z042, all scope "out").
- No in-scope case was moved to PROBES; UNSUPPORTED stays empty.

## Conventions used
- C1 closed world: a fact not stated true is false. "unknown" is used only for `rests` in Z031 and Z034 (see judgements).
- C2 items: v1 is the conviction; o1 (o2 in Z027) are the offences; p1..p4 are the previous disqualifications, in the order
  stated (each gets "prior"); c1 is the circumstance put to the court or asked about in Q4.
- C3 constants are typed only as stated: conv_v1, lo_v1, pts_v1, imp_p*, the period (based / basem / basey; totd + extd
  where the stated period includes an extension), and occ_c1. The months and days between dates are left to the frozen bridge.
- C4 stated judgments go in as stated facts: satisfied (Z031, Z034), nserious (Z003), exceptional (Z002, Z031, Z033, Z034;
  false in Z032).
- C5 every record is a conviction in England and Wales.
- Template period helpers: "N days, no extension" -> Dd(N) (in_days, based N, extd 0); "N months" -> M(N); "N year" -> Y(N).
  I added three local helpers: Dt (a stated total that includes an extension -> totd, extd, ext + ext_<section>, with the
  record marked tot_stated), NOFIX (no fixed period: prior only), and unk/tot (to set unknown / tot_stated on a record).
- The section under which an earlier disqualification was imposed (s.34, s.35) has no fact in the vocabulary unless (5)
  names it, so it is not encoded. Only s.26, s.147, s.164, s.223A and s.436A are encoded, as u_* facts.

## Judgements (one line each)
- Z011: a "fixed period of 60 days" that "included" a 5-day s.35A extension is read as a total of 60 (tot_stated; the build derives the base).
- Z012: the same reading, with a 5-day s.35C extension.
- Z013: the same reading, with a 5-day s.248D CP(S)A 1995 extension.
- Z014: the same reading, with a 5-day s.147A PCC(S)A 2000 extension.
- Z015: the same reading, with a 5-day s.166 Sentencing Code extension.
- Z016: the same reading, with a 4-day s.35A extension.
- Z027: the other offence of the same occasion, asked about in Q4, is made circumstance c1 with no (4) fact (not hardship, not alleged to make the offence not serious, not taken earlier).
- Z029: "an offence involving obligatory disqualification" is read as not discretionary; obligatory endorsement is not stated, so it is false under C1.
- Z030: the same reading as Z029 (with a s.34 order stated).
- Z031: "thinks fit not to order" is read as not declining (declines false); the facts do not say whether the satisfaction rests on c1 (rests unknown).
- Z034: "thinks fit to order ... 3 months" is read as not declining (declines false); the facts do not say whether the satisfaction rests on c1 (rests unknown).
