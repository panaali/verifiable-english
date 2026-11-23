"""The encoder's cases, from questions-enc.jsonl ONLY (sha256 checked at import). SAME-FAMILY.

Encoder: dri-statute-corpus-fwa-australia-1123 (Opus 5.5), after the translation was committed (6ff075b74d, 19:06Z).
Each case: "facts" (unary facts true of the employee e; every other one false, encode.py C1), "ints" (the stated service
at the time the notice is given / the end of that day / the termination, the casual period, the notice and termination
days and clock times, the weekly base and full rates), "questions" (qid -> form: notice = Q1, entitled = Q2, red = Q3 the
redundancy pay, piln = Q3 the least payment in lieu of notice), "judgement" (anything the encoder decided beyond copying a
stated fact: listed as "encoder judgement"). The age comes from bridge/inputs.jsonl -> bridges.jsonl (dates of birth and
notice days copied from the facts). PROBES: out-of-scope cases (every answer UNSUPPORTED).
"""
from __future__ import annotations

import hashlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
ENC_SHA256 = "6d133c29693c51b07b282f091227753cac744a7734253955c016015db7f26065"
if hashlib.sha256((HERE / "questions-enc.jsonl").read_bytes()).hexdigest() != ENC_SHA256:
    raise SystemExit("questions-enc.jsonl differs from the sealed encoder file")

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
    case("N001", STD + HOURS, same(1, 0), "2026-08-03", "2026-08-03", SAME_DAY, ("1150.40", "1290.75"),
         forms=Q12 + ("red", "piln")),
    case("N002", ["written_notice", "emp_init"], ((1, 1), (1, 1), (1, 45)), "2026-08-10", "2026-09-23", forms=Q12),
    case("N003", STD, ((0, 364), (0, 364), (1, 20)), "2026-08-17", "2026-09-07", forms=Q12),
    case("N004", STD + ["presc_div"], ((4, 100), (4, 100), (4, 128)), "2026-08-24", "2026-09-21", forms=Q12),
    case("N005", STD + HOURS, same(2, 0), "2026-08-31", "2026-08-31", SAME_DAY, ("1402.10", "1555.35"),
         forms=Q12 + ("red", "piln")),
    case("N006", STD + HOURS, same(1, 364), "2026-09-01", "2026-09-01", SAME_DAY, ("1288.88", "1400.00"),
         forms=Q12 + ("red",)),
    case("N007", STD + HOURS, same(3, 0), "2026-09-02", "2026-09-02", SAME_DAY, ("1333.33", "1500.00"),
         forms=Q12 + ("red",)),
    case("N008", STD + HOURS, same(2, 364), "2026-09-03", "2026-09-03", SAME_DAY, ("1199.99", "1250.10"),
         forms=Q12 + ("red",)),
    case("N009", STD + ["presc_subb"], ((3, 1), (3, 1), (3, 43)), "2026-09-07", "2026-10-19", forms=Q12),
    case("N010", STD + HOURS, same(4, 0), "2026-09-08", "2026-09-08", SAME_DAY, ("1500.25", "1650.00"),
         forms=Q12 + ("red",)),
    case("N011", STD + HOURS, same(3, 364), "2026-09-09", "2026-09-09", SAME_DAY, ("1100.50", "1180.00"),
         forms=Q12 + ("red",)),
    case("N012", STD + HOURS, same(5, 0), "2026-09-10", "2026-09-10", SAME_DAY, ("1250.75", "1375.20"),
         forms=Q12 + ("red", "piln")),
    case("N013", STD + HOURS, same(4, 364), "2026-09-14", "2026-09-14", SAME_DAY, ("1601.01", "1700.00"),
         forms=Q12 + ("red",)),
    case("N014", STD + ["ea_scheme", "ea_incorp", "ea_covered"], ((5, 1), (5, 1), (5, 31)), "2026-09-15",
         "2026-10-15", forms=Q12,
         judgement=["N014: 'No modern award's industry-specific redundancy scheme applies to Noah directly' read as "
                    "isrs_award false (s. 123(4)(b)); the scheme reaches him through the enterprise agreement, "
                    "s. 123(4)(c)"]),
    case("N015", STD + HOURS, same(6, 0), "2026-09-16", "2026-09-16", SAME_DAY, ("1420.60", "1530.00"),
         forms=Q12 + ("red",)),
    case("N016", STD + HOURS + ["daily_hire", "bci", "bci_conn"], same(5, 364), "2026-09-17", "2026-09-17", SAME_DAY,
         ("1310.45", "1310.45"), forms=Q12 + ("red",)),
    case("N017", STD + HOURS, same(7, 0), "2026-09-21", "2026-09-21", SAME_DAY, ("1275.30", "1390.00"),
         forms=Q12 + ("red",)),
    case("N018", STD + HOURS + ["daily_hire", "meat_slaughter", "meat_conn"], same(6, 364), "2026-09-22",
         "2026-09-22", SAME_DAY, ("1188.12", "1240.00"), forms=Q12 + ("red",),
         judgement=["N018: working 'in the meat industry in connection with the slaughter of livestock' also read as "
                    "working in connection with the meat industry (meat_conn; used only by s. 123(3)(d), weekly hire)"]),
    case("N019", STD + HOURS, same(8, 0), "2026-09-23", "2026-09-23", SAME_DAY, ("1444.44", "1600.00"),
         forms=Q12 + ("red",)),
    case("N020", STD + HOURS + ["presc_suba"], same(7, 364), "2026-09-24", "2026-09-24", SAME_DAY,
         ("1350.05", "1422.00"), forms=Q12 + ("red",)),
    case("N021", STD + HOURS, same(9, 0), "2026-09-28", "2026-09-28", SAME_DAY, ("1215.15", "1300.00"),
         forms=Q12 + ("red",)),
    case("N022", STD + HOURS + ["ea_scheme"], same(8, 364), "2026-09-29", "2026-09-29", SAME_DAY,
         ("1500.01", "1620.00"), forms=Q12 + ("red",)),
    case("N023", STD + HOURS, same(10, 0), "2026-09-30", "2026-09-30", SAME_DAY, ("1380.90", "1490.40"),
         forms=Q12 + ("red", "piln")),
    case("N024", STD + HOURS, same(9, 364), "2026-10-01", "2026-10-01", SAME_DAY, ("1260.20", "1333.00"),
         forms=Q12 + ("red",)),
    case("N025", ["written_notice", "insolv"], ((15, 170), (15, 170), (15, 200)), "2026-10-05", "2026-11-04",
         rates=("1222.22", "1300.00"), forms=Q12 + ("red",),
         judgement=["N025: the liquidator's termination 'for the employer' is not stated to be because the employer "
                    "no longer requires the job done (emp_init, not_required false); s. 119(1)(b) is the stated "
                    "ground"]),
    case("N026", STD + HOURS, ((1, 200), (1, 200), (1, 228)), "2026-10-06", "2026-11-03",
         rates=("1177.77", "1250.00"), casual=(3, 100), forms=Q12 + ("red",)),
    case("N027", STD + ["training", "tr_limited"], ((1, 100), (1, 100), (1, 114)), "2026-10-07", "2026-10-21",
         forms=Q12),
    case("N028", ["written_notice", "emp_init", "misconduct"], same(6, 0), "2026-10-08", "2026-10-08", SAME_DAY,
         forms=Q12),
    case("N029", STD + ["spec_period"], ((2, 100), (2, 100), (2, 128)), "2026-10-12", "2026-11-09", forms=Q12),
    case("N030", STD + HOURS + ["spec_period", "avoid"], ((4, 200), (4, 200), (4, 230)), "2026-10-13", "2026-11-12",
         rates=("1345.67", "1400.00"), forms=Q12 + ("red",)),
    case("N031", STD + ["casual"], same(0, 0), "2026-10-14", "2026-10-28", casual=(3, 40), forms=Q12,
         judgement=["N031: 'no period of continuous service with the employer apart from the period of employment as "
                    "a casual employee' encoded as 0 years 0 days of service other than casual periods at all three "
                    "times"]),
    case("N032", STD + ["weekly_hire", "meat_conn", "seasonal", "turnover"], ((2, 50), (2, 50), (2, 57)),
         "2026-10-15", "2026-10-22", forms=Q12),
    case("N033", STD + ["apprentice"], ((3, 10), (3, 10), (3, 38)), "2026-10-19", "2026-11-16", forms=Q12),
    case("N034", STD + ["isrs_award"], ((7, 100), (7, 100), (7, 128)), "2026-10-20", "2026-11-17", forms=Q12),
    case("N035", STD + HOURS + ["sbe_ntc", "sbe_trm"], same(8, 0), "2026-10-21", "2026-10-21", SAME_DAY,
         ("1400.00", "1480.80"), forms=Q12 + ("piln",)),
]
# The age bridge's input (copied from the facts: date of birth, the day the notice is given).
DOB = {"N001": "1996-05-14", "N002": "1993-02-09", "N003": "1990-11-02", "N004": "1985-06-21", "N005": "1976-03-30",
       "N006": "1974-01-18", "N007": "1988-07-07", "N008": "1985-04-04", "N009": "1981-09-07", "N010": "1979-12-01",
       "N011": "1996-10-10", "N012": "1997-03-03", "N013": "1982-02-02", "N014": "1966-05-05", "N015": "1991-08-19",
       "N016": "1980-11-11", "N017": "1986-06-06", "N018": "1983-03-13", "N019": "1981-09-22", "N020": "1990-01-25",
       "N021": "1979-04-30", "N022": "1987-12-12", "N023": "1971-07-01", "N024": "1987-05-20", "N025": "1968-10-03",
       "N026": "1978-02-14", "N027": "2003-06-15", "N028": "1989-08-08", "N029": "1984-04-12", "N030": "1980-01-09",
       "N031": "1995-12-24", "N032": "1992-03-03", "N033": "2006-07-20", "N034": "1975-09-09", "N035": "1983-10-31"}

UNSUPPORTED = {}  # no in-scope question is outside what the translation carries (decided per question, none found)
PROBES = {
    "N036": "s. 120 reduction by the Fair Work Commission (out of scope)",
    "N037": "s. 121(4) small business employer in liquidation (out of scope)",
    "N038": "notice an employee must give under a modern award (s. 118, out of scope)",
    "N039": "whether the employer is a small business employer (s. 23, out of scope; not stated)",
    "N040": "employee of a State public sector body, not a national system employer (out of scope)",
    "N041": "an undecided s. 120 application (out of scope)",
    "N042": "s. 121(4) small business employer who became bankrupt (out of scope)",
    "N043": "notice an employee must give when resigning (out of scope)",
}
PROBE_QIDS = {"N036": ["N036-1"], "N037": ["N037-1"], "N038": ["N038-1"], "N039": ["N039-1"],
              "N040": ["N040-1", "N040-2"], "N041": ["N041-1"], "N042": ["N042-1"], "N043": ["N043-1"]}
