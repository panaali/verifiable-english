# Encoder notes: out/cases_xfam.py

`python3 -I check.py out/cases_xfam.py` -> `OK: 35 cases, 0 unsupported, 8 probes` (43 ids).

## Counts
- Cases (scope "in", encoded): 35 (M001-M035)
- Unsupported: 0
- Probes (scope "out"): 8 (M036-M043)

## Conventions used
- encode.py C1-C6 and the template's standing readings: no order / agreement -> morder, agree absent; no 10A
  regulations, no 10C(2)(b) description, not a variation, not of a 5(a) description -> those facts absent.
- Items: sam (parent), the children by first name, every other person the facts name (persons), one item per stated
  benefit (`chb`, `pension`, `allowance`, `benefit`).
- Qualifying children from "the children with respect to whom this maintenance calculation is made" (qcalc, childof)
  with their stated person with care (pwc).
- Income copied as written (e.g. "6.99", "3000.01"); stated reduced rate -> redrate, stated 4(2) flat rate -> flatamt.
- Nights copied for every child the facts give a number for, including the stated 0s.
- "paid ... in respect of this week" -> paid; "due ... not yet paid" -> due; child benefit received -> cbpaid for each
  named child and the benefit item chb (prescribed for neither 4(1)(b) nor (c)) paid to the recipient.
- Benefits prescribed for 4(1)(b) / 4(1)(c) -> b41b / b41c on the benefit item. A partner who is "also a non-resident
  parent" -> alsonrp; "a maintenance calculation with respect to Lee is in force" -> calcinforce.
- Pairs between persons are written with Sam first (C6).

## Judgements
- M022: Sam's child benefit is entered as one benefit item, chb, paid to Sam (standing reading).
- M023: Sam's child benefit is entered as one benefit item, chb, paid to Sam (standing reading).
- M024: Lee's child benefit is entered as one benefit item, chb, paid to Lee (standing reading).
- M024: "Married, live together" is entered as married + samehh, not livetog, because no 10C(5)(b) judgment is stated.
- M026: The allowance is due but not yet paid for the week, so it is entered as due (not paid).
- M027: "Married, live together" is entered as married + samehh, not livetog, because no 10C(5)(b) judgment is stated.
- M028: "Civil partners, live together" is entered as civil + samehh, not livetog, because no 10C(5)(b) judgment is stated.
- M030: The polygamous husband and wives are entered as polyg + oppsex + samehh, not also as married.
- M030: Lee's benefit is due but not yet paid for the week, so it is entered as due (not paid).
- M031: Cora habitually resides in England, so she is entered as habuk.
- M031: Bea "has care of" Cora, who is not a qualifying child; this is not entered as pwc.
- M032: Ben habitually resides in Wales, so he is entered as habuk.
- M032: The one stated reduced rate (7.00, which explicitly includes the arrangement children) is entered as both
  redrate and redrateh.
- M032: Bea "has care of" Ben, who is not a qualifying child; this is not entered as pwc.
- M033: Ben habitually resides in Scotland, so he is entered as habuk. Cora lives in France, so she is not habuk.
- M033: Ben living with Bea and Cora living with Dana are not entered as pwc, since neither is a qualifying child.

## Probes
- M036: Northern Ireland law. M037: the pre-2003 scheme. M038: the 2003-2012 scheme.
- M039: an undecided variation. M040 / M041: income would have to be worked out from a pay slip or tax return.
- M042: it is not stated which paragraph the allowance is prescribed for. M043: the substituted 10A percentage is not
  supplied.
