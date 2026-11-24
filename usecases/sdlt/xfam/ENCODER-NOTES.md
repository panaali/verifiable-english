# ENCODER NOTES: cases_xfam.py (FA 2003 s. 55 / Sch. 6ZA)

`python3 -I check.py out/cases_xfam.py` -> `OK: 35 cases, 10 probes, 0 unsupported`

## Counts
- Cases (scope "in"): 35 (S001-S035), 121 questions.
- Probes (scope "out"): 10 (S036-S045), each with qids -1..-3.
- Unsupported: 0.

## Conventions used
- The template's record format and helpers (Q, solo, HOUSE, FLAT, WITHGARDEN). I added a generic `rec` (the same record
  shape) and `both` (lists "linked" in both directions).
- Transaction names: t = the transaction the question is about (in S028 the question is about g, the garden-strip
  lease); u = a separate, unlinked second transaction in the same case (S007-S009); g = the linked transaction
  (S022-S028); p, q = a person's earlier acquisitions. Persons get short initials.
- Forms: Q1 -> taxnr, Q2 -> claim, Q3 -> taxr. In S025-S027, Q3 is asked after a later linked purchase, so it is taxw.
  Those three cases are encoded as the state after g: t and g are linked, with earlier(t, g).
- Closed world (C1): only stated facts are listed. Facts stated as not holding (no trust, no alternative finance
  arrangement, not suitable, not linked, and so on) are left out. "allres" is listed only where the case says the land
  is entirely residential. "individual" is listed only for natural persons.
- Links (C2): "earlier" is listed for each earlier acquisition against every later transaction in the case. Same-instant
  transactions are not "earlier". "gardenof" / "benefitof" are listed only where the facts say so.
- Ints (C3): `cons_<txn>` is the stated chargeable consideration, as a decimal string. `years_<txn>` is a stated whole
  number of years to run. Nothing is computed.
- Stated judgments (C4) are entered as stated: suitablesingle (S006, S009), equivalent (S029, S030), wouldbeaf (S033),
  intends (including S012's stated "main residence").
- HOUSE / FLAT include landtxn for the transaction asked about (template convention). In S029 the lease of a house uses
  the FLAT fact list, which holds lease facts only.

## Judgements (one line each)
- S001: p (2010 purchase of a lease of a Leeds flat) read as a land transaction within the Act (landtxn)
- S002: the shed standing in the garden read as part of the garden land (extraland, extragarden), not a further building (multidwelling false)
- S004: the separate shop building read as a second building (multidwelling) and land besides the house (extraland)
- S007: p (2015 purchase of a Plymouth freehold) read as a land transaction within the Act (landtxn)
- S008: p (2012 purchase of a lease of a Manchester flat) read as a land transaction within the Act (landtxn)
- S010: p (2014 purchase of a Reading freehold) read as a land transaction within the Act (landtxn)
- S011: Harbour Finance (a financial institution) read as not an individual
- S012: p (2011 Cardiff lease, before Welsh LTT) read as a land transaction within the Act (landtxn), situated in Wales (wales)
- S013: p (2013 Sheffield lease grant) read as a land transaction within the Act (landtxn)
- S014: Hearth Finance (a financial institution) read as not an individual
- S021: the garage standing in the garden read as part of the garden and grounds (extraland, extragarden), not a further building (multidwelling false)
- S023: g, a permanent right of way, read as neither a freehold nor a lease (a right over land: benefitof)
- S024: g, a permanent right of way, read as neither a freehold nor a lease (a right over land: benefitof)
- S028: p (2014 purchase of a Leeds freehold) read as a land transaction within the Act (landtxn)
- S029: the Toronto lease read as a lease (term of years) for the para. 6(2) rule (lease)
- S030: the Ottawa lease read as a lease (term of years) for the para. 6(2) rule (lease)
- S031: p (2011 Cardiff lease grant, before Welsh LTT) read as a land transaction within the Act (landtxn), situated in Wales (wales)
- S032: p, q (2015 Leeds, 2016 Nottingham purchases) read as land transactions within the Act (landtxn)
- S032: Cedar Finance and Willow Finance (financial institutions) read as not individuals
- S033: p (9 March 2000, before SDLT) read as not a land transaction within the Act and not a first transaction under ss. 71A/73 (landtxn, affirst false)
- S033: Larch Finance (a financial institution) read as not an individual
