# Encoder notes: cases_xfam.py (FA 2016 ss. 99-101, apprenticeship levy)

## Counts
- Cases in questions-enc.jsonl: 39 (the brief says 43; the file holds 39, L001-L039, and check.py checks against the file).
- In scope: 35 cases, 35 records (each names one tax year, 2026-27, so no `@year` split).
- Probes: 4 (L036 charity; L037 s. 103 applies; L038 s. 100(4) continental-shelf certificate; L039 a one-month period, not a tax year).
- Unsupported: 0.
- `check.py`: `OK: 35 records, 4 probes, 0 unsupported`. I also checked that each question's form (Q1/Q2/Q3) and person match the file's kind and the name in its text.

## Conventions used
- C1 closed world. A fact is listed only when the facts state it. "Neither incurs nor would incur" gives `sec` only. Charity is always absent.
- C3: `co` for a company within s. 1121(1) CTA 2010, `llp` for L025's Alma, `ind` for an individual employer.
- C4: one earnings item per earner (`j<earner>`) with the stated amount. A stated liability, including one of GBP 0, is `liab`. Below the lower earnings limit is `butfor`. Neither is `none`. L014 and L015 have no earnings items.
- C5: a stated company that is connected with no other company is in no group. L025-L035 have one group `g` (all the named employers).
- C6: determinations (`det`), alterations (`alt`), returns (`ret`, which gives `ret9` + `aware`), notices (`notified8`/`notified13`), action not taken (`not_taken8`/`not_taken13`), `noreturns`, and paid/due amounts are all as stated. `dues_stated:g` is set wherever the members' amounts due and payable are stated. Every person's paid/due is encoded as stated (GBP 0.00 unless stated otherwise).
- C7: no case states the half-up convention or a s. 101(12) rounding, so no `halfup` or `rnd_*`.
- No amount, total, share or answer was computed. All amounts are copied as stated, in pence.

## Judgements (one line each)
- L025, L026, L027, L028, L029, L030, L031, L032, L033, L034, L035: connected at 00:00 on 6 April 2026 read as at the beginning of the tax year (conn).
- L028: the members' 1 February 2027 agreement to assign 8,000 / 7,000 "instead" read as an alteration (altmade).
- L030, L031, L032, L033: HMRC knowing the returns from 2 March 2027 read as aware at the assessment time (aware).
- L031: action taken on 10 March 2027 read as within the 2-16 March 2027 period (not_taken8 absent).
- L032, L033, L034, L035: no action up to the 5 April 2027 assessment read as not taken within the 2-16 March 2027 period.
- L033: HMRC's stated s. 101(7) roundings (2,142.86 up, 12,857.14 down) not encoded: the rnd_* facts state s. 101(12) shares only.
- L034, L035: paid / due are the stated figures at 2 March 2027 for the tax year (no later payment).
- L035: HMRC knowing the return on 2 March 2027 read as aware at the assessment time (aware).
- L035: Alma's return is silent on Bea, Cora and their allowance, and the determination was not communicated: read as insufficient (s. 101(13)(b)).
