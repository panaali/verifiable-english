# Encoder notes: cases_xfam.py (Reg (EU) 1177/2010, Arts 2, 3, 19, 20)

`python3 -I check.py out/cases_xfam.py` → `OK: 35 cases, 10 probes`.

## Counts
- 45 cases in questions-enc.jsonl: 35 encoded in scope (E001-E035, qids -1/-2/-3 = applies/right/pay), 10 probes (E036-E045, one qid each).
- No in-scope case had to become a probe. Every stated fact fit the vocabulary, except the E006 deductions (see the judgements below).

## Conventions used
- C1 (closed world): any fact not listed is false. Examples: other_ms is never stated; dep_spec is true only where the ticket's departure time is stated (single tickets, E020); in E016 and E033 it is false.
- C2: numbers are copied as stated. Distances were already given in metres. Durations were given as (hours, minutes). Prices and the threshold are copied as EUR strings, e.g. "80.00". The return price (rprice) is used only in E008. dyear is set only where a design year is stated (E010, E029).
- C3: weather (E015) and extraord (E021) are entered as stated judgments.
- C4: places named as ports carry works_* and regular_*, as the facts also state. The facts also state the vessel, the contract and the valid document (BASE). Alder Canal (E013) is encoded with LAKE (inland + water_used), as stated.
- Probe reasons: cancellation (E036-E038); reduced mobility (E039); luggage (E040); Art 19(2) season ticket (E041); Art 19(5) payment and vouchers (E042, E043); air and bus transport (E044, E045).

## Judgements (one line each)
- E003: c is Harbour Navigation (the contract party); the seller Landing Tickets is not c.
- E006: the proposed fee, telephone and stamp deductions are not encoded (the vocabulary has no term for them).
- E008: c is Harbour Navigation (the contract party); the booking retailer Harbour Bookings is not c.
- E010: in "replica of a historical passenger ship designed in 1964", 1964 is read as the design year.
- E015: c is Harbour Navigation (the contract party); the tour operator Holiday Assembly is not c.
- E016: the travel pass is not stated to be an open ticket, so open_t is false (C1).
- E029: in "replica of a historical passenger ship designed in 1964", 1964 is read as the design year.
