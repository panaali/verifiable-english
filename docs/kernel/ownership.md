# Per-answer Lean ownership of the five frozen keys

Generated from docs/kernel/ownership.json by `tools/ownership_trace.py verdict`; never edit by hand.
Test: manage-agents reviews/lean-ownership-baseline-20261112.md section 2. An item passes when (1) no decision function of tools/ownership-decision-functions.json ran while it was answered, (2) its value is a Lean answer of a kind whose theorem tools/kernel-paths.json lists on a kernel path (not `uncovered`, `nonverdict` or untied), and (3) the value equals the frozen key or PLAN.md section 12 records the difference. The counts are per answer; quote them, never a family tally.

Traced at 7bb830b01b, da0822ae80.

| key | items | passes | fails 1 | fails 2 | fails 3 |
|---|---:|---:|---:|---:|---:|
| anthropic-rsp | 126 | **100** | 8 | 15 | 3 |
| openai-preparedness | 239 | **228** | 8 | 3 | 0 |
| safety-framework | 262 | **241** | 6 | 12 | 3 |
| agent-policy | 42 | **0** | 42 | 0 | 0 |
| eligibility | 269 | **269** | 0 | 0 | 0 |

## anthropic-rsp

| family | items | 1 clean | 2 Lean kernel kind | 3 agrees or recorded | passes | first failing reason (most items) |
|---|---:|---:|---:|---:|---:|---|
| A | 40 | 40 | 40 | 40 | **40** |  |
| B | 12 | 12 | 12 | 12 | **12** |  |
| C | 8 | 0 | 8 | 8 | **0** | (1) ve/evaluate.py:_Evaluator.__init__ |
| D | 9 | 9 | 9 | 6 | **6** | (3) value "UNDECIDED" differs from the key "NONE", no PLAN.md section 12 entry |
| G | 8 | 8 | 5 | 5 | **5** | (2) no Lean case of the key's value sources was sent (the value is not a Lean answer) |
| K | 27 | 27 | 25 | 25 | **25** | (2) no Lean case of the key's value sources was sent (the value is not a Lean answer) |
| N | 5 | 5 | 3 | 3 | **3** | (2) no Lean case of the key's value sources was sent (the value is not a Lean answer) |
| S | 8 | 8 | 0 | 7 | **0** | (2) no kernel path lists a theorem for risk kind risk-decision (paths: risk (candidate)), sent by d2 |
| T | 9 | 9 | 9 | 9 | **9** |  |

Passing (100): A-T0/PROT1, A-T0/PROT2, A-T0/PROT3, A-T0/PROT4, A-T0/ARG1, A-T0/ARG2, A-T0/ARG3, A-T0/ARG4, A-T1/PROT1, A-T1/PROT2, A-T1/PROT3, A-T1/PROT4, A-T1/ARG1, A-T1/ARG2, A-T1/ARG3, A-T1/ARG4, A-T2/PROT1, A-T2/PROT2, A-T2/PROT3, A-T2/PROT4, A-T2/ARG1, A-T2/ARG2, A-T2/ARG3, A-T2/ARG4, A-T3/PROT1, A-T3/PROT2, A-T3/PROT3, A-T3/PROT4, A-T3/ARG1, A-T3/ARG2, A-T3/ARG3, A-T3/ARG4, A-T4/PROT1, A-T4/PROT2, A-T4/PROT3, A-T4/PROT4, A-T4/ARG1, A-T4/ARG2, A-T4/ARG3, A-T4/ARG4, B-PUB/INSCOPE, B-PUB/ASSESS, B-INT/INSCOPE, B-INT/ASSESS, B-INTD/INSCOPE, B-INTD/ASSESS, B-AUT/INSCOPE, B-AUT/ASSESS, B-VOL/INSCOPE, B-VOL/ASSESS, B-TRN/INSCOPE, B-TRN/ASSESS, K1, K2, K3, K4, K5, K6, K7, K8, K11, K12a, K12b, K13, K14, K15a, K15b, K16, K17, K18, K19a, K19b, K20, K21a, K21b, K22a, K22b, T1, T2a, T2b, T3, T4a, T4b, T5, T6, T7, G1, G2, G3, G7, G8, N1, N2, N3, D1, D2, D3a, D3b, D4, D5.

## openai-preparedness

| family | items | 1 clean | 2 Lean kernel kind | 3 agrees or recorded | passes | first failing reason (most items) |
|---|---:|---:|---:|---:|---:|---|
| A | 140 | 140 | 140 | 140 | **140** |  |
| B | 42 | 42 | 42 | 42 | **42** |  |
| C | 7 | 0 | 7 | 7 | **0** | (1) ve/evaluate.py:_Evaluator.__init__ |
| D | 4 | 4 | 4 | 4 | **4** |  |
| G | 10 | 10 | 10 | 10 | **10** |  |
| K | 22 | 22 | 22 | 22 | **22** |  |
| N | 4 | 3 | 3 | 4 | **3** | (1) ve/evaluate.py:_Evaluator.__init__ |
| S | 8 | 8 | 5 | 8 | **5** | (2) no kernel path lists a theorem for risk kind risk-decision (paths: risk (candidate)), sent by risk_probe |
| T | 2 | 2 | 2 | 2 | **2** |  |

Passing (228): A-L0-DEV/SEC, A-L0-DEV/MIS, A-L0-DEV/ALN, A-L0-DEV/SUF, A-L0-DEV/HALT, A-L0-INT/SEC, A-L0-INT/MIS, A-L0-INT/ALN, A-L0-INT/SUF, A-L0-INT/HALT, A-L0-LINT/SEC, A-L0-LINT/MIS, A-L0-LINT/ALN, A-L0-LINT/SUF, A-L0-LINT/HALT, A-L0-EXT/SEC, A-L0-EXT/MIS, A-L0-EXT/ALN, A-L0-EXT/SUF, A-L0-EXT/HALT, A-BIO-H-DEV/SEC, A-BIO-H-DEV/MIS, A-BIO-H-DEV/ALN, A-BIO-H-DEV/SUF, A-BIO-H-DEV/HALT, A-BIO-H-INT/SEC, A-BIO-H-INT/MIS, A-BIO-H-INT/ALN, A-BIO-H-INT/SUF, A-BIO-H-INT/HALT, A-BIO-H-LINT/SEC, A-BIO-H-LINT/MIS, A-BIO-H-LINT/ALN, A-BIO-H-LINT/SUF, A-BIO-H-LINT/HALT, A-BIO-H-EXT/SEC, A-BIO-H-EXT/MIS, A-BIO-H-EXT/ALN, A-BIO-H-EXT/SUF, A-BIO-H-EXT/HALT, A-BIO-C-DEV/SEC, A-BIO-C-DEV/MIS, A-BIO-C-DEV/ALN, A-BIO-C-DEV/SUF, A-BIO-C-DEV/HALT, A-BIO-C-INT/SEC, A-BIO-C-INT/MIS, A-BIO-C-INT/ALN, A-BIO-C-INT/SUF, A-BIO-C-INT/HALT, A-BIO-C-LINT/SEC, A-BIO-C-LINT/MIS, A-BIO-C-LINT/ALN, A-BIO-C-LINT/SUF, A-BIO-C-LINT/HALT, A-BIO-C-EXT/SEC, A-BIO-C-EXT/MIS, A-BIO-C-EXT/ALN, A-BIO-C-EXT/SUF, A-BIO-C-EXT/HALT, A-CYB-H-DEV/SEC, A-CYB-H-DEV/MIS, A-CYB-H-DEV/ALN, A-CYB-H-DEV/SUF, A-CYB-H-DEV/HALT, A-CYB-H-INT/SEC, A-CYB-H-INT/MIS, A-CYB-H-INT/ALN, A-CYB-H-INT/SUF, A-CYB-H-INT/HALT, A-CYB-H-LINT/SEC, A-CYB-H-LINT/MIS, A-CYB-H-LINT/ALN, A-CYB-H-LINT/SUF, A-CYB-H-LINT/HALT, A-CYB-H-EXT/SEC, A-CYB-H-EXT/MIS, A-CYB-H-EXT/ALN, A-CYB-H-EXT/SUF, A-CYB-H-EXT/HALT, A-CYB-C-DEV/SEC, A-CYB-C-DEV/MIS, A-CYB-C-DEV/ALN, A-CYB-C-DEV/SUF, A-CYB-C-DEV/HALT, A-CYB-C-INT/SEC, A-CYB-C-INT/MIS, A-CYB-C-INT/ALN, A-CYB-C-INT/SUF, A-CYB-C-INT/HALT, A-CYB-C-LINT/SEC, A-CYB-C-LINT/MIS, A-CYB-C-LINT/ALN, A-CYB-C-LINT/SUF, A-CYB-C-LINT/HALT, A-CYB-C-EXT/SEC, A-CYB-C-EXT/MIS, A-CYB-C-EXT/ALN, A-CYB-C-EXT/SUF, A-CYB-C-EXT/HALT, A-AIS-H-DEV/SEC, A-AIS-H-DEV/MIS, A-AIS-H-DEV/ALN, A-AIS-H-DEV/SUF, A-AIS-H-DEV/HALT, A-AIS-H-INT/SEC, A-AIS-H-INT/MIS, A-AIS-H-INT/ALN, A-AIS-H-INT/SUF, A-AIS-H-INT/HALT, A-AIS-H-LINT/SEC, A-AIS-H-LINT/MIS, A-AIS-H-LINT/ALN, A-AIS-H-LINT/SUF, A-AIS-H-LINT/HALT, A-AIS-H-EXT/SEC, A-AIS-H-EXT/MIS, A-AIS-H-EXT/ALN, A-AIS-H-EXT/SUF, A-AIS-H-EXT/HALT, A-AIS-C-DEV/SEC, A-AIS-C-DEV/MIS, A-AIS-C-DEV/ALN, A-AIS-C-DEV/SUF, A-AIS-C-DEV/HALT, A-AIS-C-INT/SEC, A-AIS-C-INT/MIS, A-AIS-C-INT/ALN, A-AIS-C-INT/SUF, A-AIS-C-INT/HALT, A-AIS-C-LINT/SEC, A-AIS-C-LINT/MIS, A-AIS-C-LINT/ALN, A-AIS-C-LINT/SUF, A-AIS-C-LINT/HALT, A-AIS-C-EXT/SEC, A-AIS-C-EXT/MIS, A-AIS-C-EXT/ALN, A-AIS-C-EXT/SUF, A-AIS-C-EXT/HALT, B-L0/CAPREP, B-L0/SAFEREP, B-L0/MREP, B-L0/DISC, B-L0/PUBRES, B-L0/CONTRIB, B-BIO-H/CAPREP, B-BIO-H/SAFEREP, B-BIO-H/MREP, B-BIO-H/DISC, B-BIO-H/PUBRES, B-BIO-H/CONTRIB, B-BIO-C/CAPREP, B-BIO-C/SAFEREP, B-BIO-C/MREP, B-BIO-C/DISC, B-BIO-C/PUBRES, B-BIO-C/CONTRIB, B-CYB-H/CAPREP, B-CYB-H/SAFEREP, B-CYB-H/MREP, B-CYB-H/DISC, B-CYB-H/PUBRES, B-CYB-H/CONTRIB, B-CYB-C/CAPREP, B-CYB-C/SAFEREP, B-CYB-C/MREP, B-CYB-C/DISC, B-CYB-C/PUBRES, B-CYB-C/CONTRIB, B-AIS-H/CAPREP, B-AIS-H/SAFEREP, B-AIS-H/MREP, B-AIS-H/DISC, B-AIS-H/PUBRES, B-AIS-H/CONTRIB, B-AIS-C/CAPREP, B-AIS-C/SAFEREP, B-AIS-C/MREP, B-AIS-C/DISC, B-AIS-C/PUBRES, B-AIS-C/CONTRIB, K1, K2, K3, K4, K5, K6a, K6b, K6c, K7, K8, K9, K10, K11, K12, K13, K14, K15, K16, K17, K18, K19, K20, T1, T2, G1, G2, G3, G4, G5, G6, G7, G8, G9, G10, N1, N2, N4, S1, S2, S3, S4, S5, D1, D2, D3, D4.

## safety-framework

| family | items | 1 clean | 2 Lean kernel kind | 3 agrees or recorded | passes | first failing reason (most items) |
|---|---:|---:|---:|---:|---:|---|
| A | 160 | 160 | 160 | 160 | **160** |  |
| B | 40 | 40 | 40 | 40 | **40** |  |
| C | 6 | 0 | 6 | 6 | **0** | (1) ve/norms.py:NormDocument._expand |
| D | 3 | 3 | 3 | 3 | **3** |  |
| G | 9 | 9 | 9 | 8 | **8** | (3) value "NONE" differs from the key "ALL", no PLAN.md section 12 entry |
| K | 18 | 18 | 18 | 16 | **16** | (3) value "ALL" differs from the key "NONE", no PLAN.md section 12 entry |
| N | 3 | 3 | 3 | 3 | **3** |  |
| R | 11 | 11 | 11 | 11 | **11** |  |
| S | 12 | 12 | 0 | 12 | **0** | (2) no kernel path lists a theorem for risk kind risk-decision (paths: risk (candidate)), sent by risk_run |

Passing (241): A-L0-DEV/DM, A-L0-DEV/SEC, A-L0-DEV/GOV, A-L0-DEV/CCA, A-L0-INT/DM, A-L0-INT/SEC, A-L0-INT/GOV, A-L0-INT/CCA, A-L0-HRI/DM, A-L0-HRI/SEC, A-L0-HRI/GOV, A-L0-HRI/CCA, A-L0-LRX/DM, A-L0-LRX/SEC, A-L0-LRX/GOV, A-L0-LRX/CCA, A-L0-EXT/DM, A-L0-EXT/SEC, A-L0-EXT/GOV, A-L0-EXT/CCA, A-L1-DEV/DM, A-L1-DEV/SEC, A-L1-DEV/GOV, A-L1-DEV/CCA, A-L1-INT/DM, A-L1-INT/SEC, A-L1-INT/GOV, A-L1-INT/CCA, A-L1-HRI/DM, A-L1-HRI/SEC, A-L1-HRI/GOV, A-L1-HRI/CCA, A-L1-LRX/DM, A-L1-LRX/SEC, A-L1-LRX/GOV, A-L1-LRX/CCA, A-L1-EXT/DM, A-L1-EXT/SEC, A-L1-EXT/GOV, A-L1-EXT/CCA, A-L2-DEV/DM, A-L2-DEV/SEC, A-L2-DEV/GOV, A-L2-DEV/CCA, A-L2-INT/DM, A-L2-INT/SEC, A-L2-INT/GOV, A-L2-INT/CCA, A-L2-HRI/DM, A-L2-HRI/SEC, A-L2-HRI/GOV, A-L2-HRI/CCA, A-L2-LRX/DM, A-L2-LRX/SEC, A-L2-LRX/GOV, A-L2-LRX/CCA, A-L2-EXT/DM, A-L2-EXT/SEC, A-L2-EXT/GOV, A-L2-EXT/CCA, A-L3-DEV/DM, A-L3-DEV/SEC, A-L3-DEV/GOV, A-L3-DEV/CCA, A-L3-INT/DM, A-L3-INT/SEC, A-L3-INT/GOV, A-L3-INT/CCA, A-L3-HRI/DM, A-L3-HRI/SEC, A-L3-HRI/GOV, A-L3-HRI/CCA, A-L3-LRX/DM, A-L3-LRX/SEC, A-L3-LRX/GOV, A-L3-LRX/CCA, A-L3-EXT/DM, A-L3-EXT/SEC, A-L3-EXT/GOV, A-L3-EXT/CCA, A-L4-DEV/DM, A-L4-DEV/SEC, A-L4-DEV/GOV, A-L4-DEV/CCA, A-L4-INT/DM, A-L4-INT/SEC, A-L4-INT/GOV, A-L4-INT/CCA, A-L4-HRI/DM, A-L4-HRI/SEC, A-L4-HRI/GOV, A-L4-HRI/CCA, A-L4-LRX/DM, A-L4-LRX/SEC, A-L4-LRX/GOV, A-L4-LRX/CCA, A-L4-EXT/DM, A-L4-EXT/SEC, A-L4-EXT/GOV, A-L4-EXT/CCA, A-L5-DEV/DM, A-L5-DEV/SEC, A-L5-DEV/GOV, A-L5-DEV/CCA, A-L5-INT/DM, A-L5-INT/SEC, A-L5-INT/GOV, A-L5-INT/CCA, A-L5-HRI/DM, A-L5-HRI/SEC, A-L5-HRI/GOV, A-L5-HRI/CCA, A-L5-LRX/DM, A-L5-LRX/SEC, A-L5-LRX/GOV, A-L5-LRX/CCA, A-L5-EXT/DM, A-L5-EXT/SEC, A-L5-EXT/GOV, A-L5-EXT/CCA, A-L6-DEV/DM, A-L6-DEV/SEC, A-L6-DEV/GOV, A-L6-DEV/CCA, A-L6-INT/DM, A-L6-INT/SEC, A-L6-INT/GOV, A-L6-INT/CCA, A-L6-HRI/DM, A-L6-HRI/SEC, A-L6-HRI/GOV, A-L6-HRI/CCA, A-L6-LRX/DM, A-L6-LRX/SEC, A-L6-LRX/GOV, A-L6-LRX/CCA, A-L6-EXT/DM, A-L6-EXT/SEC, A-L6-EXT/GOV, A-L6-EXT/CCA, A-L7-DEV/DM, A-L7-DEV/SEC, A-L7-DEV/GOV, A-L7-DEV/CCA, A-L7-INT/DM, A-L7-INT/SEC, A-L7-INT/GOV, A-L7-INT/CCA, A-L7-HRI/DM, A-L7-HRI/SEC, A-L7-HRI/GOV, A-L7-HRI/CCA, A-L7-LRX/DM, A-L7-LRX/SEC, A-L7-LRX/GOV, A-L7-LRX/CCA, A-L7-EXT/DM, A-L7-EXT/SEC, A-L7-EXT/GOV, A-L7-EXT/CCA, B-L0/RRA, B-L0/SC, B-L0/PRA, B-L0/RECSEC, B-L0/DISC, B-L1/RRA, B-L1/SC, B-L1/PRA, B-L1/RECSEC, B-L1/DISC, B-L2/RRA, B-L2/SC, B-L2/PRA, B-L2/RECSEC, B-L2/DISC, B-L3/RRA, B-L3/SC, B-L3/PRA, B-L3/RECSEC, B-L3/DISC, B-L4/RRA, B-L4/SC, B-L4/PRA, B-L4/RECSEC, B-L4/DISC, B-L5/RRA, B-L5/SC, B-L5/PRA, B-L5/RECSEC, B-L5/DISC, B-L6/RRA, B-L6/SC, B-L6/PRA, B-L6/RECSEC, B-L6/DISC, B-L7/RRA, B-L7/SC, B-L7/PRA, B-L7/RECSEC, B-L7/DISC, K1-L2/PROXIMITY, K1-L3/PROXIMITY, K1-L4/PROXIMITY, K1-L6/PROXIMITY, K1-L7/PROXIMITY, K3/FURTHER_CCA, K4/CHECKPOINT_MCCA, K5/SUBMISSION, K6/YEARLY_REVIEW, K7/ADD, K8/FREQUENT_REVIEW, K9-L2/DISC, K9-L3/DISC, K9-L4/DISC, K9-L6/DISC, K9-L7/DISC, R1/ACCEPTABLE, R2/ACCEPTABLE, R3/ACCEPTABLE, R4/ACCEPTABLE, R5/ACCEPTABLE, R6/ACCEPTABLE, R7/ACCEPTABLE, R8/ACCEPTABLE, R9a/ACCEPTABLE, R9b/PERMITS, R9c/FORBIDS, G1, G2, G4, G5, G6, G7, G8, G9, N1, N2, N3, D1, D2, D3.

## agent-policy

| family | items | 1 clean | 2 Lean kernel kind | 3 agrees or recorded | passes | first failing reason (most items) |
|---|---:|---:|---:|---:|---:|---|
| action | 42 | 0 | 42 | 42 | **0** | (1) ve/evaluate.py:_Evaluator.__init__ |

Passing (0): none.

## eligibility

| family | items | 1 clean | 2 Lean kernel kind | 3 agrees or recorded | passes | first failing reason (most items) |
|---|---:|---:|---:|---:|---:|---|
| Q1 | 80 | 80 | 80 | 80 | **80** |  |
| Q2 | 63 | 63 | 63 | 63 | **63** |  |
| Q3 | 63 | 63 | 63 | 63 | **63** |  |
| Q4 | 63 | 63 | 63 | 63 | **63** |  |

Passing (269): A01/Q1, A01/Q2, A01/Q3, A01/Q4, A02/Q1, A02/Q2, A02/Q3, A02/Q4, A03/Q1, A03/Q2, A03/Q3, A03/Q4, A04/Q1, A04/Q2, A04/Q3, A04/Q4, A05/Q1, A05/Q2, A05/Q3, A05/Q4, A06/Q1, A06/Q2, A06/Q3, A06/Q4, A07/Q1, A07/Q2, A07/Q3, A07/Q4, A08/Q1, A08/Q2, A08/Q3, A08/Q4, A09/Q1, A09/Q2, A09/Q3, A09/Q4, A10/Q1, A10/Q2, A10/Q3, A10/Q4, A11/Q1, A11/Q2, A11/Q3, A11/Q4, A12/Q1, A12/Q2, A12/Q3, A12/Q4, A13/Q1, A13/Q2, A13/Q3, A13/Q4, B01/Q1, B02/Q1, B02/Q2, B02/Q3, B02/Q4, B03/Q1, B03/Q2, B03/Q3, B03/Q4, B04/Q1, B05/Q1, B05/Q2, B05/Q3, B05/Q4, B06/Q1, B06/Q2, B06/Q3, B06/Q4, B07/Q1, B08/Q1, B09/Q1, B10/Q1, B10/Q2, B10/Q3, B10/Q4, B11/Q1, B12/Q1, B13/Q1, B13/Q2, B13/Q3, B13/Q4, B14/Q1, B14/Q2, B14/Q3, B14/Q4, B15/Q1, B15/Q2, B15/Q3, B15/Q4, B16/Q1, B16/Q2, B16/Q3, B16/Q4, B17/Q1, B17/Q2, B17/Q3, B17/Q4, B18/Q1, B19/Q1, B19/Q2, B19/Q3, B19/Q4, B20/Q1, B20/Q2, B20/Q3, B20/Q4, B21/Q1, B21/Q2, B21/Q3, B21/Q4, B22/Q1, B22/Q2, B22/Q3, B22/Q4, B23/Q1, B24/Q1, B24/Q2, B24/Q3, B24/Q4, B25/Q1, B25/Q2, B25/Q3, B25/Q4, B26/Q1, B26/Q2, B26/Q3, B26/Q4, B27/Q1, B27/Q2, B27/Q3, B27/Q4, B28/Q1, B29/Q1, B30/Q1, B30/Q2, B30/Q3, B30/Q4, B31/Q1, B31/Q2, B31/Q3, B31/Q4, B32/Q1, B32/Q2, B32/Q3, B32/Q4, B33/Q1, B33/Q2, B33/Q3, B33/Q4, B34/Q1, B34/Q2, B34/Q3, B34/Q4, C01/Q1, C01/Q2, C01/Q3, C01/Q4, C02/Q1, C03/Q1, C03/Q2, C03/Q3, C03/Q4, C04/Q1, C04/Q2, C04/Q3, C04/Q4, C05/Q1, C05/Q2, C05/Q3, C05/Q4, C06/Q1, C06/Q2, C06/Q3, C06/Q4, C07/Q1, C07/Q2, C07/Q3, C07/Q4, C08/Q1, C08/Q2, C08/Q3, C08/Q4, C09/Q1, C09/Q2, C09/Q3, C09/Q4, C10/Q1, C10/Q2, C10/Q3, C10/Q4, C11/Q1, C11/Q2, C11/Q3, C11/Q4, C12/Q1, C12/Q2, C12/Q3, C12/Q4, C13/Q1, C14/Q1, C14/Q2, C14/Q3, C14/Q4, C15/Q1, C15/Q2, C15/Q3, C15/Q4, C16/Q1, C17/Q1, C17/Q2, C17/Q3, C17/Q4, C18/Q1, C19/Q1, C19/Q2, C19/Q3, C19/Q4, C20/Q1, C21/Q1, C21/Q2, C21/Q3, C21/Q4, C22/Q1, C22/Q2, C22/Q3, C22/Q4, C23/Q1, C24/Q1, C24/Q2, C24/Q3, C24/Q4, C25/Q1, C25/Q2, C25/Q3, C25/Q4, C26/Q1, C26/Q2, C26/Q3, C26/Q4, C27/Q1, C27/Q2, C27/Q3, C27/Q4, D01/Q1, D01/Q2, D01/Q3, D01/Q4, D02/Q1, D02/Q2, D02/Q3, D02/Q4, D03/Q1, D03/Q2, D03/Q3, D03/Q4, D04/Q1, D04/Q2, D04/Q3, D04/Q4, D05/Q1, D05/Q2, D05/Q3, D05/Q4, D06/Q1, D06/Q2, D06/Q3, D06/Q4.
