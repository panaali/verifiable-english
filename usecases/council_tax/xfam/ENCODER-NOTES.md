# Encoder notes (cases_xfam.py)

`python3 -I check.py out/cases_xfam.py out/inputs_xfam.jsonl` -> `OK: 34 cases, 7 unsupported, 10 probes, 3 bridge rows`

## Counts
- Cases (CASES): 34. These are K001-K010 (Q1, one value each) and K011-K034 (Q2/Q3, single days).
- Unsupported: 7 keys, each holding a Q3 over a run of several days: K011-7, K012-5, K013-5, K018-5, K020-5,
  K034-5, K035-1. K035's only question is a run, so K035 has no CASES record.
- Probes: 10 (K036-K045), 17 qids in PROBE_QIDS.
- Bridge rows (out/inputs_xfam.jsonl): 3. They are K020 dee d1 and d2 (date of birth 2007-06-02) and K021 eli d1 (2007-05-15).

## Conventions used
- C1 closed world: only stated true facts are listed. The boilerplate "not detained ... does not live in a hospital,
  care home or hostel", and the facts stated as not holding, are left out.
- C2: the persons of a case are the people named as residents on the days asked. A Q3 over a run of days gets no day items.
- C3: values, dates, amounts set, days in the year and certificate dates are copied as stated. A is given as `amt`
  when it is set for the listed band (K011, K020) and as `amtd` when it is set for band D (all other cases, including
  K019 and K026, which are listed in D). Money is written with 2 decimals, e.g. "39999.00". age18 comes only from the bridge.
- C4: the stated judgments severe_imp, appears_perm and smr_inst are entered as stated.
- Institution facts (inst_*, patient, receiving_care, smr_inst) are recorded per person per day for the institution
  the facts name. A building's name ("Meadow Hospital", "Meadow Care Home", "Meadow Hostel", "Meadow Independent
  Hospital") is not treated as a status.

## Judgements
- K013: on 2 May, "a warrant giving effect to a decision of a UK court" is carried as basis_sentence + uk_court.
- K014: on 2 July, basis_order + service_offence are kept for the award detention Ben is released from.
- K015: "physically held at a detention facility" is read as in_custody on each day.
- K017: basis_sentence + uk_court of the prison detention are kept on the day each person is discharged or released.
- K019: the certificate "throughout that period" is read as covering 20 to 22 May 2025 (certfrom/certto).
- K020: Dee (visiting, not a resident on 1 June) is a person of the case because Dee is a resident on 2 June. Bridge rows are written for both days.
- K023: "a health service hospital as defined by s. 275" is carried as inst_hs_hospital only.
