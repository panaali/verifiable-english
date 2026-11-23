"""The encoder's cases, from questions-enc.jsonl ONLY (sha256 checked at import). SAME-FAMILY.

Encoder: dri-statute-corpus-hos-driving-1123 (Opus 5.5). Each in-scope case is parsed mechanically from its facts:
the log (each entry's two clock times, its stated duration and its named ACTIVITY), the carrier's every-day fact and
designated start of the 24-hour period, and each question's moment and kind. The only reading the encoder adds is
ACTIVITY below: which facts of translation.FACTS a named activity makes true (encoder judgement, listed in RESULT.md);
every other fact of a piece is stated false (closed world, encode.py C1). Out-of-scope probes: every answer UNSUPPORTED.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ENC_SHA256 = "8a99acb9d630bed4e903c3f355a4feed69320d3eccc2575212b32c4eb2a1be68"
_RAW = (HERE / "questions-enc.jsonl").read_bytes()
if hashlib.sha256(_RAW).hexdigest() != ENC_SHA256:
    raise SystemExit("questions-enc.jsonl differs from the sealed encoder file")
RAW_CASES = [json.loads(line) for line in _RAW.decode("utf-8").splitlines() if line.strip()]

CMV_DRIVE = ["at_controls", "in_on_cmv"]
ACTIVITY = {  # named activity -> the facts it makes true (encoder judgement; everything else false)
    "driving the truck": CMV_DRIVE,
    "driving the Ridgeline Freight truck": CMV_DRIVE,
    "driving a Harbor Line Carriers property-carrying truck": CMV_DRIVE,   # read as a CMV in operation
    "at home": [],
    "a meal at a restaurant": [],                                            # read as relieved from work
    "resting in a motel room": [],
    "inspecting the truck": ["inspecting"],
    "inspecting and checking the oil of the truck parked in the carrier's yard next to his house": ["inspecting"],
    "putting fuel in the truck": ["inspecting"],                             # servicing
    "washing the truck and topping up its fluids in the carrier's yard": ["inspecting"],   # servicing / conditioning
    "staying with the broken-down truck at the roadside and helping the mechanic repair it": ["disabled"],
    "unloading the truck at a customer's warehouse": ["loading"],
    "loading the truck at a shipper's dock": ["loading"],
    "waiting at a shipper's dock while the truck is being loaded": ["loading"],          # attending a CMV being loaded
    "giving and receiving receipts for the freight at a customer's dock": ["loading"],
    "filling in paperwork at the terminal": ["carrier_work"],
    "sorting furniture in Lakeside Movers' warehouse": ["carrier_work"],     # Lakeside Movers: a motor carrier (stated)
    "sorting parcels in Harbor Line Carriers' warehouse": ["carrier_work"],  # Harbor Line: a motor carrier (stated)
    "working a paid shift as a cashier at a grocery store": ["paid_other"],  # stated: not a motor carrier, pays
    "working a paid shift at a hardware store": ["paid_other"],
    "waiting at the terminal to be dispatched": ["wait_dispatch"],          # stated: not relieved
    "giving a urine sample": ["testing"],                                    # stated: directed, part 382 random test
    "driving her own car from home to the drug-testing collection site": ["testing"],   # travel to the site; no CMV
    "driving her own car from the collection site back home": ["testing"],
    "driving his own car from home to the drug-testing collection site": ["testing"],
    "driving his own car from the collection site to the terminal": ["testing"],
    "sitting in the drivers' lounge at the terminal waiting for a ride home": ["relieved"],  # H014: stated relieved
    "resting in the cab of the parked truck": ["in_on_cmv", "rest_parked"],
    "resting in the sleeper berth of the parked truck": ["in_on_cmv", "rest_parked", "rest_sleeper"],
    "resting in the sleeper berth while her co-driver Omar drives the truck": ["in_on_cmv", "rest_sleeper"],
    "resting in the sleeper berth while his co-driver Ines drives the truck": ["in_on_cmv", "rest_sleeper"],
    "resting in the sleeper berth while her co-driver Ruth drives the truck": ["in_on_cmv", "rest_sleeper"],
    "riding in the passenger seat of the truck while Omar drives it on the highway": ["in_on_cmv", "ride_passenger"],
    "riding in the passenger seat of the truck while Ines drives it on the highway": ["in_on_cmv", "ride_passenger"],
    "riding in the passenger seat of the truck while Ruth drives it on the highway": ["in_on_cmv", "ride_passenger"],
    "riding in the passenger seat of another Ridgeline Freight truck, driven by a colleague on the highway back to the "
    "terminal": ["in_on_cmv", "ride_passenger"],
}
JUDGEMENT = {  # activity readings beyond copying a word of the text (RESULT.md "Encoder judgement")
    "a meal at a restaurant": "relieved from work (off duty), no limb applies",
    "resting in a motel room": "off duty, no limb applies",
    "putting fuel in the truck": "servicing a CMV (limb (2))",
    "washing the truck and topping up its fluids in the carrier's yard": "servicing / conditioning a CMV (limb (2))",
    "inspecting and checking the oil of the truck parked in the carrier's yard next to his house": "inspecting / "
    "servicing a CMV (limb (2))",
    "waiting at a shipper's dock while the truck is being loaded": "attending a CMV being loaded (limb (5))",
    "driving a Harbor Line Carriers property-carrying truck": "a CMV in operation (driving time)",
    "driving her own car from home to the drug-testing collection site": "travel to the collection site (limb (7)); "
    "an own car is not a CMV (not driving time)",
    "driving her own car from the collection site back home": "travel from the collection site (limb (7))",
    "driving his own car from home to the drug-testing collection site": "travel to the collection site (limb (7))",
    "driving his own car from the collection site to the terminal": "travel from the collection site (limb (7))",
    "sitting in the drivers' lounge at the terminal waiting for a ride home": "not waiting to be dispatched; relieved "
    "(stated in H014's facts); off duty",
}

DAYS = "Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday"
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
          "November", "December"]
STAMP = rf"(?:{DAYS}) (\d{{1,2}}) ({'|'.join(MONTHS)}) (\d{{4}}), (\d{{2}}:\d{{2}})"
ENTRY = re.compile(rf"^(?:{DAYS}) (\d{{1,2}}) ({'|'.join(MONTHS)}) (\d{{4}}), (\d{{2}}:\d{{2}}) to "
                   rf"(?:(?:{DAYS}) (\d{{1,2}}) ({'|'.join(MONTHS)}) (\d{{4}}), )?(\d{{2}}:\d{{2}}) "
                   r"\((?:(\d+) days? )?(\d+) hours? (\d+) minutes?\): (.+)$")


def iso(d, mon, y, hm):
    return f"{int(y):04d}-{MONTHS.index(mon) + 1:02d}-{int(d):02d}T{hm}"


def parse_log(facts):
    i = facts.index("Log of ")
    body = facts[facts.index(": ", i) + 2:].strip()
    if body.endswith("."):
        body = body[:-1]
    out = []
    for raw in body.split("; "):
        mt = ENTRY.match(raw.strip())
        if not mt:
            raise ValueError(f"unparsed log entry: {raw!r}")
        d1, mo1, y1, h1, d2, mo2, y2, h2, dd, hh, mm, act = mt.groups()
        start = iso(d1, mo1, y1, h1)
        end = iso(d2, mo2, y2, h2) if d2 else iso(d1, mo1, y1, h2)
        if act not in ACTIVITY:
            raise ValueError(f"no reading for activity {act!r}")
        out.append({"start": start, "end": end, "stated": (int(dd or 0), int(hh), int(mm)), "activity": act})
    return out


def carrier(facts):
    every = "operates commercial motor vehicles every day of the week" in facts.split("Log of")[0]
    not_every = "on Mondays to Saturdays only" in facts
    if every == not_every:
        raise ValueError("carrier every-day fact not found")
    mt = re.search(r"designates (\d{2}:\d{2}) as the time at which its 24-hour period starts", facts)
    return every, mt.group(1)


def moment(text):
    mt = re.search(STAMP, text)
    if not mt:
        raise ValueError(f"no moment in {text!r}")
    return iso(*mt.groups())


def form(q):
    if q["kind"] == "Q1":
        return "q1", None
    if q["kind"] == "Q2":
        if "a limit of 395.3(a)" not in q["text"]:
            raise ValueError(q["qid"])
        return "q2", None
    if "60 hours in a period of 7 consecutive days" in q["text"]:
        return "q3", 7
    if "70 hours in a period of 8 consecutive days" in q["text"]:
        return "q3", 8
    raise ValueError(q["qid"])


def build():
    cases, probes = [], {}
    for c in RAW_CASES:
        if c["scope"] != "in":
            probes[c["id"]] = [q["qid"] for q in c["questions"]]
            continue
        every, designated = carrier(c["facts"])
        qs = []
        for q in c["questions"]:
            f, n = form(q)
            qs.append({"qid": q["qid"], "form": f, "n": n, "moment": moment(q["text"])})
        cases.append({"id": c["id"], "every_day": every, "designated": designated, "log": parse_log(c["facts"]),
                      "questions": qs})
    return cases, probes


CASES, PROBES = build()
