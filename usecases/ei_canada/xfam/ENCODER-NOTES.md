# ENCODER NOTES — cases_xfam.py

Built by `out/build.py` (a parser for this writer's fact sentences; it stops on any sentence it cannot read) from
`questions-enc.jsonl` only. `python3 -I check.py out/cases_xfam.py` → `OK: 47 cases, 0 unsupported, 10 probes`.

## Counts
- Cases (scope "in"): 47 (E001–E047), 141 questions (47 qualify, 47 maxweeks, 47 rate).
- Probes (scope "out"): 10 (E048–E057), 21 qids, each with a one-line note on what it needs.
- Unsupported: 0.

## Conventions
- insured = True for every claimant. No case states it; this follows the encode.py convention (every claimant is an
  insured person). s23 = false (fixed by encode.py).
- interruption: as stated ("has had" → True; "has not had" → False, E047 only).
- rate, hours, bpstart: copied as stated ("The benefit period would begin on …" → ISO date).
- weeks: one stated amount per week 1..N, where N is the stated "The qualifying period has N weeks"; $0.00 weeks are
  transcribed as stated. runs: each stated "weeks a to b" or single listed week, with the week numbers as stated.
- seps: each stated lay-off/separation amount, in the order stated; [] where the facts say no such amounts were paid or payable.
- myie / myie_year: copied where stated (E005–E047); None where not stated (E001–E004, benefit periods in 1997–2000).
- b5_stated: True where the facts state that the s. 14(1.1) maximum caps weekly insurable earnings (E003, E005).
- halfup: False everywhere (every Q3 says "no rounding rule applies").
- "All money is in Canadian dollars." and "There are no other such amounts." have no field of their own (the second
  confirms the seps list is complete).
- Nothing was computed: no totals, averages, divisors, rates or numbers of weeks.

## Judgements (one line each)
- E001: weeks stated as comma lists: each listed week or 'a to b' range is one run of its own
- E007: $800.00 paid by reason of lay-off (week 30): one s. 14(3)(b) item; its week and paid/payable are not encoded
- E008: $840.00 payable by reason of separation from employment (week 30): one s. 14(3)(b) item; its week and paid/payable are not encoded
- E009: $440.00 paid by reason of lay-off (week 1): one s. 14(3)(b) item; its week and paid/payable are not encoded
- E009: $220.00 paid by reason of separation from employment (week 30): one s. 14(3)(b) item; its week and paid/payable are not encoded
- E010: $84.00 paid by reason of lay-off (week 30): one s. 14(3)(b) item; its week and paid/payable are not encoded
- E010: 'the weekly earnings came from insurable employment that has not ended': no field; not encoded (the interruption is encoded as stated)
- E010: weeks stated as comma lists: each listed week or 'a to b' range is one run of its own
- E011: weeks stated as comma lists: each listed week or 'a to b' range is one run of its own
- E012: $38.00 paid by reason of lay-off (week 1): one s. 14(3)(b) item; its week and paid/payable are not encoded
- E012: $57.00 payable by reason of separation from employment (week 2): one s. 14(3)(b) item; its week and paid/payable are not encoded
- E012: $19.00 paid by reason of separation from employment (week 3): one s. 14(3)(b) item; its week and paid/payable are not encoded
- E014: weeks stated as comma lists: each listed week or 'a to b' range is one run of its own
- E015: weeks stated as comma lists: each listed week or 'a to b' range is one run of its own
- E016: weeks stated as comma lists: each listed week or 'a to b' range is one run of its own
- E019: weeks stated as comma lists: each listed week or 'a to b' range is one run of its own
- E020: weeks stated as comma lists: each listed week or 'a to b' range is one run of its own
- E021: weeks stated as comma lists: each listed week or 'a to b' range is one run of its own
- E024: weeks stated as comma lists: each listed week or 'a to b' range is one run of its own
- E025: weeks stated as comma lists: each listed week or 'a to b' range is one run of its own
- E026: weeks stated as comma lists: each listed week or 'a to b' range is one run of its own
- E029: weeks stated as comma lists: each listed week or 'a to b' range is one run of its own
- E030: weeks stated as comma lists: each listed week or 'a to b' range is one run of its own
- E031: weeks stated as comma lists: each listed week or 'a to b' range is one run of its own
- E034: weeks stated as comma lists: each listed week or 'a to b' range is one run of its own
- E035: weeks stated as comma lists: each listed week or 'a to b' range is one run of its own
- E036: weeks stated as comma lists: each listed week or 'a to b' range is one run of its own
- E039: weeks stated as comma lists: each listed week or 'a to b' range is one run of its own
- E040: weeks stated as comma lists: each listed week or 'a to b' range is one run of its own
- E041: weeks stated as comma lists: each listed week or 'a to b' range is one run of its own
