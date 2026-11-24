"""Fair Work Act 2009 ss. 117, 119, 121(1), 123: TEMPLATE for the cross-family encoder: the build's record format,
helpers and conventions; records removed.

Each case (built with case()): "facts" (unary facts true of the employee e; every other one false, encode.py C1), "ints"
(the stated service at the time the notice is given / the end of that day / the termination, the casual period, the notice
and termination days and clock times in minutes after midnight, the weekly base and full rates), "questions" (qid -> form:
notice = Q1, entitled = Q2, red = Q3 the redundancy pay, piln = Q3 the least payment in lieu of notice), "judgement"
(anything the encoder decided beyond copying a stated fact: listed as "encoder judgement").
The age comes from the bridge (bridge/age.py) on DOB[id] (the stated date of birth, copied) and the notice day (dn_e);
never typed here. PROBES: out-of-scope cases, id -> reason; PROBE_QIDS: id -> its qids (every answer UNSUPPORTED).
UNSUPPORTED: in-scope cases the vocabulary cannot state, id -> (reason, [qids]).
"""
from __future__ import annotations

# The facts most cases state: written notice; the employer terminates on its own initiative because it no longer
# requires the job done by anyone; stated judgment: not due to the ordinary and customary turnover of labour (so
# "turnover" is false by C1); not a small business employer; no other exclusion.
STD = ["written_notice", "emp_init", "not_required"]
HOURS = ["same_hours"]  # "works the same 38 ordinary hours every week and no other hours, and would have kept ..."
SAME_DAY = (540, 1020)  # "At 9:00 am on D ... terminates at 5:00 pm on D"


def svc(ntc, end, trm):
    out = {}
    for t, (y, d) in (("ntc", ntc), ("end", end), ("trm", trm)):
        out[f"ncy_{t}_e"], out[f"ncd_{t}_e"] = y, d
    return out


def case(cid, facts, service, notice, term, clock=None, rates=None, casual=(0, 0), forms=(), judgement=()):
    ints = svc(*service)
    ints.update({"cay_e": casual[0], "cad_e": casual[1], "dn_e": notice, "dt_e": term})
    if clock:
        ints["cn_e"], ints["ct_e"] = clock
    if rates:
        ints["base_e"], ints["full_e"] = rates
    return {"id": cid, "facts": list(facts), "ints": ints,
            "questions": [{"qid": f"{cid}-{i}", "item": "e", "form": f} for i, f in enumerate(forms, 1)],
            "judgement": list(judgement)}


def same(y, d):
    return ((y, d), (y, d), (y, d))


Q12 = ("notice", "entitled")
CASES = [
    case("N001", STD + HOURS, same(0, 364), "2026-11-24", "2026-11-24", (1020, 1020), ("1010.00", "1260.00"),
         forms=Q12 + ("piln",)),
    case("N002", STD + HOURS, same(1, 0), "2026-11-24", "2026-11-24", (1020, 1020), ("1020.00", "1270.00"),
         casual=(1, 0), forms=Q12 + ("red",),
         judgement=["casual period stated as 'a single period of 1 calendar year' entered as 1 year 0 days"]),
    case("N003", STD + HOURS, same(1, 364), "2026-11-24", "2026-11-24", (1020, 1020), ("1030.00", "1280.00"),
         forms=Q12 + ("red",)),
    case("N004", STD + HOURS, same(2, 0), "2026-11-24", "2026-11-24", (1020, 1020), ("1040.00", "1290.00"),
         forms=Q12 + ("red",)),
    case("N005", STD + HOURS, same(2, 364), "2026-11-24", "2026-11-24", (1020, 1020), ("1050.00", "1300.00"),
         forms=Q12 + ("red",)),
    case("N006", STD + HOURS, same(3, 0), "2026-11-24", "2026-11-24", (1020, 1020), ("1060.00", "1310.00"),
         forms=Q12 + ("red",)),
    case("N007", STD + HOURS, same(3, 364), "2026-11-24", "2026-11-24", (1020, 1020), ("1070.00", "1320.00"),
         forms=Q12 + ("red",)),
    case("N008", STD + HOURS, ((3, 1), (3, 1), (4, 0)), "2025-11-25", "2026-11-24", (1020, 1020),
         ("1080.00", "1330.00"), forms=Q12 + ("red",)),
    case("N009", STD + HOURS, same(4, 364), "2026-11-24", "2026-11-24", (1020, 1020), ("1090.00", "1340.00"),
         forms=Q12 + ("red",)),
    case("N010", STD + HOURS, same(5, 0), "2026-11-24", "2026-11-24", (1020, 1020), ("1100.00", "1350.00"),
         forms=Q12 + ("red",)),
    case("N011", STD + HOURS, same(5, 364), "2026-11-24", "2026-11-24", (1020, 1020), ("1110.00", "1360.00"),
         forms=Q12 + ("red",)),
    case("N012", STD + HOURS, ((5, 1), (5, 1), (6, 0)), "2025-11-25", "2026-11-24", (1020, 1020),
         ("1120.00", "1370.00"), forms=Q12 + ("red",)),
    case("N013", STD + HOURS, same(6, 364), "2026-11-24", "2026-11-24", (1020, 1020), ("1130.00", "1380.00"),
         forms=Q12 + ("red",)),
    case("N014", STD + HOURS, same(7, 0), "2026-11-24", "2026-11-24", (1020, 1020), ("1140.00", "1390.00"),
         forms=Q12 + ("piln", "red")),
    case("N015", STD + HOURS, same(7, 364), "2026-11-24", "2026-11-24", (1020, 1020), ("1150.00", "1400.00"),
         forms=Q12 + ("red",)),
    case("N016", STD + HOURS, same(8, 0), "2026-11-24", "2026-11-24", (1020, 1020), ("1160.00", "1410.00"),
         forms=Q12 + ("red",)),
    case("N017", STD + HOURS, same(8, 364), "2026-11-24", "2026-11-24", (1020, 1020), ("1170.00", "1420.00"),
         forms=Q12 + ("red",)),
    case("N018", STD + HOURS, same(9, 0), "2026-11-24", "2026-11-24", (1020, 1020), ("1180.00", "1430.00"),
         forms=Q12 + ("red",)),
    case("N019", STD + HOURS, same(9, 364), "2026-11-24", "2026-11-24", (1020, 1020), ("1190.00", "1440.00"),
         forms=Q12 + ("red",)),
    case("N020", ["written_notice", "emp_init", "insolv"] + HOURS, same(10, 0), "2026-11-24", "2026-11-24",
         (1020, 1020), ("1200.00", "1450.00"), forms=Q12 + ("red",),
         judgement=["'initiates the termination solely because of its bankruptcy' read as emp_init and insolv"]),
    case("N021", STD + HOURS, ((0, 364), (0, 364), (1, 0)), "2026-11-23", "2026-11-24", (1020, 1020),
         ("1210.00", "1460.00"), forms=Q12 + ("red",)),
    case("N022", ["written_notice", "emp_init", "misconduct"] + HOURS, same(4, 0), "2026-11-24", "2026-11-24",
         (1020, 1020), ("1220.00", "1470.00"), forms=Q12 + ("red",)),
    case("N023", STD + HOURS + ["spec_period"], same(4, 0), "2026-11-24", "2026-11-24", (1020, 1020),
         ("1230.00", "1480.00"), forms=Q12 + ("red",)),
    case("N024", STD + HOURS + ["spec_period", "avoid"], same(1, 1), "2026-11-24", "2026-11-24", (1020, 1020),
         ("1240.00", "1490.00"), forms=Q12 + ("red",)),
    case("N025", STD + HOURS + ["casual"], same(0, 0), "2026-11-24", "2026-11-24", (1020, 1020),
         ("1250.00", "1500.00"), casual=(2, 0), forms=Q12 + ("red",),
         judgement=["casual period stated as 'a single period of 2 calendar years' entered as 2 years 0 days"]),
    case("N026", STD + HOURS + ["training", "spec_period", "tr_limited", "avoid"], same(2, 0), "2026-11-24",
         "2026-11-24", (1020, 1020), ("1260.00", "1510.00"), forms=Q12 + ("red",),
         judgement=["'his employment lasts for that arrangement only' read as tr_limited"]),
    case("N027", STD + HOURS + ["daily_hire", "bci", "bci_conn"], same(4, 0), "2026-11-24", "2026-11-24",
         (1020, 1020), ("1270.00", "1520.00"), forms=Q12 + ("red",),
         judgement=["'repairing buildings' read as bci_conn (with bci, both stated)"]),
    case("N028", STD + HOURS + ["daily_hire", "meat_slaughter", "meat_conn"], same(10, 1), "2026-11-24",
         "2026-11-24", (1020, 1020), ("1280.00", "1530.00"), forms=Q12 + ("red",),
         judgement=["'working in the meat industry' also read as meat_conn (not a weekly hire employee)"]),
    case("N029", STD + HOURS + ["turnover", "weekly_hire", "meat_conn", "seasonal"], same(5, 1), "2026-11-24",
         "2026-11-24", (1020, 1020), ("1290.00", "1540.00"), forms=Q12 + ("red",)),
    case("N030", STD + HOURS + ["apprentice", "training"], same(3, 0), "2026-11-24", "2026-11-24", (1020, 1020),
         ("1300.00", "1550.00"), forms=Q12 + ("piln",)),
    case("N031", STD + HOURS + ["isrs_award"], same(5, 0), "2026-11-24", "2026-11-24", (1020, 1020),
         ("1310.00", "1560.00"), forms=Q12 + ("red",)),
    case("N032", STD + HOURS + ["ea_scheme", "ea_incorp", "ea_covered"], same(6, 0), "2026-11-24", "2026-11-24",
         (1020, 1020), ("1320.00", "1570.00"), forms=Q12 + ("red",)),
    case("N033", STD + HOURS + ["sbe_ntc"], ((5, 364), (5, 364), (6, 0)), "2026-11-23", "2026-11-24", (1020, 1020),
         ("1330.00", "1580.00"), forms=Q12 + ("red",)),
    case("N034", STD + HOURS + ["presc_div"], same(4, 0), "2026-11-24", "2026-11-24", (1020, 1020),
         ("1340.00", "1590.00"), forms=Q12 + ("red",)),
    case("N035", STD + HOURS + ["presc_suba", "presc_subb"], same(4, 0), "2026-11-24", "2026-11-24", (1020, 1020),
         ("1350.00", "1600.00"), forms=Q12 + ("red",)),
]
# The age bridge's input (copied from the facts): id -> date of birth (YYYY-MM-DD); the notice day is the case's dn_e.
DOB = {
    "N001": "1990-11-24", "N002": "1981-11-24", "N003": "1980-11-24", "N004": "1981-11-23", "N005": "1990-11-24",
    "N006": "1981-11-23", "N007": "1990-11-24", "N008": "1990-11-24", "N009": "1990-11-24", "N010": "1981-11-24",
    "N011": "1990-11-24", "N012": "1990-11-24", "N013": "1990-11-24", "N014": "1981-11-23", "N015": "1990-11-24",
    "N016": "1990-11-24", "N017": "1990-11-24", "N018": "1990-11-24", "N019": "1990-11-24", "N020": "1990-11-24",
    "N021": "1981-11-23", "N022": "1990-11-24", "N023": "1990-11-24", "N024": "1990-11-24", "N025": "1990-11-24",
    "N026": "1990-11-24", "N027": "1990-11-24", "N028": "1990-11-24", "N029": "1990-11-24", "N030": "1990-11-24",
    "N031": "1990-11-24", "N032": "1990-11-24", "N033": "1990-11-24", "N034": "1990-11-24", "N035": "1990-11-24",
}

UNSUPPORTED = {}
PROBES = {
    "N036": "s. 120 reduction of redundancy pay by the Fair Work Commission (other acceptable employment): not in ss. 117, 119, 121(1), 123",
    "N037": "s. 121(4)-(7) small business employer in liquidation: not in the translated s. 121(1)",
    "N038": "notice given by the employee under a modern award term (not supplied): outside s. 117",
    "N039": "small business employer status to be decided from the employee count (s. 23, not pinned; not a stated fact)",
    "N040": "State industrial law, not a national system employer: outside the Act's provisions",
}
PROBE_QIDS = {"N036": ["N036-1"], "N037": ["N037-1"], "N038": ["N038-1"], "N039": ["N039-1"], "N040": ["N040-1"]}
