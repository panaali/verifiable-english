"""Made-up smoke cases (NOT from questions-enc.jsonl; written with the translation, before that file was opened). They
only check that the translation, encoder and runner fit together; they are never graded. Expected answers in EXPECT."""
from __future__ import annotations

COC_LPV = ["basis_coc", "cert_lpv", "cert_co2", "has_lp"]


def case(cid, vehicles, questions):
    return {"id": cid, "vehicles": vehicles,
            "questions": [{"qid": f"{cid}-{i}", "item": it, "vehicle": v, "form": f}
                          for i, (f, it, v) in enumerate(questions, 1)], "judgement": []}


def veh(vid, facts, dreg, co2=None, lp=None, np=None, accessories=(), licences=()):
    ints = {"dreg": dreg}
    if co2 is not None:
        ints["co2"] = co2
    if lp is not None:
        ints["lp"] = lp
    if np is not None:
        ints["np"] = np
    return {"id": vid, "facts": facts, "ints": ints, "accessories": list(accessories), "licences": list(licences)}


CASES = [
    # petrol, 130 g/km (Table 1 row 7 upper bound), list 39,000 + accessory 1,000.01 -> over 40,000; licence 2 years on
    case("S001", [veh("v1", COC_LPV, "2023-05-10", co2="130", lp="39000.00",
                      accessories=[{"id": "v1a1", "facts": ["a_nonstd", "a_attached", "a_has_lp"],
                                    "ints": {"alp": "1000.01"}}],
                      licences=[{"id": "v1l1", "date": "2025-05-10"}])],
         [("rate1", "v1", "v1"), ("rate2", "v1l1", "v1"), ("ge2", "v1l1", "v1")]),
    # zero-emission, no figure on the certificate (1C), registered 2024 before 1 April 2025 -> (c) fails
    case("S002", [veh("v1", ["basis_ukac", "cert_lpv", "zero_rate", "has_lp"], "2024-07-01", lp="60000.00",
                      licences=[{"id": "v1l1", "date": "2026-07-01"}])],
         [("rate1", "v1", "v1"), ("rate2", "v1l1", "v1"), ("ge2", "v1l1", "v1")]),
    # diesel, Euro 6d-TEMP -> higher rate diesel, 0 g/km?? no: 256 g/km -> Table 2 row 12
    case("S003", [veh("v1", COC_LPV + ["diesel", "ind6dtemp"], "2019-01-15", co2="256", lp="30000.00")],
         [("rate1", "v1", "v1")]),
    # diesel Euro 6d -> Table 1, 0 g/km -> row 1; registered before 2017 -> Part does not apply (second vehicle)
    case("S004", [veh("v1", COC_LPV + ["diesel", "ind6d"], "2021-03-03", co2="0", lp="20000.00"),
                  veh("v2", COC_LPV, "2016-12-31", co2="100", lp="20000.00")],
         [("rate1", "v1", "v1"), ("rate1", "v2", "v2")]),
    # no list price, notional 50,000.01, zero-emission figure 0 stated, registered 2025-06-01; licence on sixth anniversary
    case("S005", [veh("v1", ["basis_coc", "cert_lpv", "cert_co2"], "2025-06-01", co2="0", np="50000.01",
                      licences=[{"id": "v1l1", "date": "2031-06-01"}, {"id": "v1l2", "date": "2031-05-31"}])],
         [("rate2", "v1l1", "v1"), ("ge2", "v1l1", "v1"), ("rate2", "v1l2", "v1"), ("ge2", "v1l2", "v1")]),
]
EXPECT = {"S001-1": "455.00", "S001-2": "640.00", "S001-3": "yes", "S002-1": "10.00", "S002-2": "200.00",
          "S002-3": "no", "S003-1": "5690.00", "S004-1": "10.00", "S004-2": "NOT_APPLY", "S005-1": "200.00",
          "S005-2": "no", "S005-3": "640.00", "S005-4": "yes"}
UNSUPPORTED = {}
PROBES = {}
PROBE_QIDS = {}
SMOKE_INPUTS = [("S001", "v1l1", "2023-05-10", "2025-05-10"), ("S002", "v1l1", "2024-07-01", "2026-07-01"),
                ("S005", "v1l1", "2025-06-01", "2031-06-01"), ("S005", "v1l2", "2025-06-01", "2031-05-31")]
