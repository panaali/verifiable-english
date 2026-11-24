# ENCODER-NOTES: PAWHP (SSI 2024/351), cross-family set

`python3 -I check.py out/cases_xfam.py` -> `OK: 40 cases, 10 probes`

- Cases encoded: 40 (P001-P040, every in-scope id). None of the in-scope cases became a probe.
- Probes: 10 (P041-P050, every out-of-scope id). Each has a one-line reason in `PROBES`.

## Conventions used
- C1 domain closure: each case names everyone in the applicant's household and marriage. P036 includes Wallace, who has moved out, but gives him no pair facts.
- C2 start dates: "since 1 January 2000" is written as 2000-01-01. No start date before 1970 was needed.
- C3: facts stated for "both", "all", "neither" or "none" are stated for each person named. This covers residence, immigration, care, custody, benefits, awards and payments, and the same-household and mutual-home facts in P031 and P032.
- C4: in P028-P032 the couples and marriage members living together get same_household and share_mutual_home.
- C5 (each_day): set from the stated benefit dates for an applicant or member whose partner or fellow member is entitled throughout the week (P028, P029, P030, P031, P032). Elsewhere it follows the person's own benefits.
- C6: residence, mutual home, care home or independent hospital, free in-patient treatment and custody are taken as facts.
- Closed facts: the facts' closing sentences ("except for ... expressly stated here, none ...") are encoded as false. The only fact left unknown is P040.rb_by_later_decision.
- Dates are transcribed as stated: the application received date, the residence start or last day, the care start, and the opt-in day. Where the bridge gives two pensionable-age dates, sex is set only as the facts state it.

## Judgements (one line each)
- P019: fipt_52w_before is true because the stated stay from 2025-09-21 covers the 52 weeks before the week (the bridge's window starts 2025-09-22).
- P020: fipt_52w_before is true because the stated stay from 2025-09-22 covers the 52 weeks before the week (the bridge's window starts 2025-09-22).
- P023: the care home stay runs from 2026-06-29 with no last day; the absence from 10 to 20 Aug 2026 is a temporary absence and is disregarded.
- P034: Robert's holiday from 20 to 28 Sep 2026 is a temporary absence, so the mutual home is shared on the week's last day.
- P036: share_mutual_home is read on the week's last day (27 Sep 2026). Wallace had moved out that day, so he shares with neither of the others.
- P037: opt_in_before_payment is false because the opt-in (31 Mar 2027) came after this week's payment fell to be made (1 Dec 2026).
- P038: opt_in_before_payment is false because the opt-in (31 Mar 2027) came after this week's payment fell to be made (1 Dec 2026).
- P038: the 2 Apr 2027 award makes Colin entitled to state pension credit on 22 Sep 2026, which is a day in the week but not throughout it.
- P039: opt_in_before_payment is true because the opt-in (24 Sep 2026) came before this week's payment fell to be made (1 Dec 2026).
- P040: opt_out_before_payment is false because the opt-out (1 Feb 2027) came after this week's payment was made (1 Dec 2026).
- P040: rb_by_later_decision is left unknown because these facts leave out the usual "no later benefit decision" sentence.

## Superseded (row statute-xfam-wrong-pawhp-1, 2026-11-24)
The P019 and P020 judgements above (fipt_52w_before stated true) are replaced: the records now state only the stay
dates (../fipt-enc/stays-xfam.jsonl, a fresh encoder seat) and the checker derives both reg. 9(a) facts
(translation.fipt_rules; SI 2005/3360 reg. 2(5): the period begins the day after entry).
