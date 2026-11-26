"""GitLab 'Global Travel and Expense Policy' s.4.1 Travel related expenses (statute corpus batch 4, NON-STATUTE (a) company
expense policy): the VE translation, one pass with today's language. CROSS-FAMILY questions (Codex writer), Opus translator.

Row statute-corpus-gitlab-expenses (dri-statute-corpus-gitlab-expenses-w-1124, Opus 5.5). Written from the pinned source
(manage-agents reviews/spare/statute-corpus/batch4/gitlab-expenses/source.txt, sha256 a39c3c6a...136d45da, CC BY-SA 4.0) and
its 82 units (units.jsonl, sha256 474a3e4b...51e7). The encoder's question file (questions only, no answers) was read BEFORE
this file was written (ISOLATION.md says so). Scope and the scope decisions D1-D16 are ISOLATION.md's, fixed before the
writer ran; the readings below are fixed here, before cases.py exists. Nothing here is a Lean kernel line, a
profile, a refuses pair or a lint change.

UNITS maps each unit n of units.jsonl to
  ("RULE", builder, note)        the unit is written: builder(ctx) gives its ground formulas for one sub-case;
  ("PART", builder, cause, note) written except the part named in the note;
  ("NOT", None, cause, note)     not written (the ledger row's cause, CAUSES.tsv v2).
A builder returns (formula, target) pairs: target is the atom key or constant the formula defines (None = a check).

ONE SUB-CASE = the items one question needs: the team member p, and per question the flight, its segments, the trips of the
quarter, the acceptance check, the rental, the stay, the meal day, the expense items. Items are linked to their parent in
ctx.parent (a segment to its flight or trip, a meal item to its day). Every value a rule needs is a stated fact of the case
(dates, clock times, durations in hours and minutes, amounts in USD, heights, class order, approvals, purposes) or a
value computed in Lean from them; there is NO bridge script: dates, clock times, the 24 hours, lead times and nights are
date steps in the language (shift_days, elapsed_days, date comparisons).

READINGS (fixed here; refuse when in doubt; D-numbers are ISOLATION.md's):
R1  Classes (units 4-7, 14, 66, 67): the case lists the classes offered lowest first; their positions are the ranks
    (standard economy / standard = the lowest). "the next class up from standard economy" = rank of standard + 1; "below
    business class" = rank < business's rank; "One class of upgrade" = at most one rank above standard; standard is always
    in policy. A class is in policy (clsok) when it is standard or a permission of unit 4, 5, 6 or 7 holds; out of policy
    when it is not standard and every permission fails; otherwise undetermined.
R2  Height (unit 4, D4): "over 6'5\"/2m" in centimetres: over 195.58 cm (6'5" = 77 in x 2.54) and over 200 cm -> tall;
    at most 195.58 cm -> not tall; between (195.58, 200] -> two outcomes, undetermined. A height stated in feet and inches:
    inches = 12 x feet + inches (Lean); over 77 in and 254 x inches > 20000 -> tall; at most 77 in -> not tall.
R3  Five hours (units 5, 6, D4): a segment's minutes = 60 x hours + minutes (Lean). Every segment over 300 minutes -> both
    "a duration greater than 5 hours" and "each segment must be 5+ hours" hold; some segment under 300 -> both fail (the
    each-segment test fails on both readings of 5); a segment of exactly 300 with none under -> two outcomes, undetermined.
    The permission also needs the selected class to be the next class up from standard and below business.
R4  Frequent traveller (unit 7, D4, D9): "3 or more trips per quarter internationally on flights of 8 hrs+ ... (minimum 6
    flight segments with 8+ hours per segment)" under the heading "Flights exceeding 8 hours". Counted over the trips the
    case lists for the quarter (all of them; the case says they are all): a trip counts surely when it is international and
    every segment is over 480 minutes, and possibly when it is international and some segment is at least 480; a segment
    counts surely when over 480 and possibly when at least 480. Frequent when the sure counts reach 3 trips and 6 segments;
    not frequent when the possible counts are under 3 trips or under 6 segments; otherwise undetermined (exactly 8 hours).
    Business class is permitted on a flight of the trip when frequent, the flight is international, its segments are all
    over 480 minutes and the trip's purpose is one of the three listed (meeting with customers, speaking engagement,
    representing GitLab at a conference); not permitted when not frequent, or no listed purpose, or a segment under 480,
    or the selected class is not business.
R5  Flags (units 3, 14, 33, 64; D5): "over 20% of the Dynamic Policy" = price > 1.2 x DP, i.e. 5 x price > 6 x DP (Lean;
    the literal "more than a fifth of it" would flag every price). "more expensive than the cheapest option + our buffer":
    price > cheapest + buffer. "booked less than 14 days in advance": the booking day after the departure day minus 14
    (the brief's convention). Out-of-policy class: R1. Booked outside Navan: flagged "Out of Policy" (units 3, 18). The
    flight is flagged when any criterion holds and not flagged when every one fails. The email to the manager (unit 15) is
    sent when one of unit 14's three criteria holds.
R6  Automatic acceptance (unit 16, D8): a moment = (day, minute of the day) in the case's one time zone (UTC in every case:
    no clock change). The acceptance moment = the booking/email moment + 24 hours = (the next day, the same minute). A
    flagged booking with no manual action from the email through the asked moment is accepted by it when the asked moment
    is at or after the acceptance moment, and not accepted when it is before. A manager approval at or before the asked
    moment -> accepted (an approved booking stands). A denial before the acceptance moment -> never accepted.
R7  Advance purchase (unit 2): the latest booking date that meets the ideal interval = departure minus 14 days (domestic)
    or 21 days (international); "ideally" is a recommendation (D10): only the date is answered, never a consequence.
R8  Norms (D10): a plain prohibition or permission of the text ("need to be booked through Navan", "may not personally
    benefit", "are responsible for canceling", "must be used ... whenever possible", "not allowed as a claim", "not
    reimbursable", "cannot claim both", "not permitted to expense both", "Do Not purchase", "Purchase ...") is written as
    the yes/no predicate the question asks (may / should / is reimbursable), nothing more. A conditional permission ("is
    permitted if", "If a milk shipment service is unavailable, you may expense") is read as the only grant: its condition
    failing -> not permitted.
R9  Rental insurance (units 22-25; D1(b), D2): units 22-24 (headings "A. Third Party Liability", "B. Physical Damage") govern
    rentals in the US or Canada (unit 22's "State minimum coverage", unit 23's "renting autos in the US or Canada", and the
    next heading "Countries other than the US and Canada:"); unit 24's Mexico sentences also govern a rental where travel to
    Mexico is required; unit 25 governs traveling outside the US and Canada. Where two govern and give two outcomes (a
    rental in Mexico: unit 24 "Do Not purchase the Collision Damage Waiver", unit 25 "Purchase the Collision Damage
    Waiver"), no answer (refused: two outcomes).
R10 Caps and limits (D6): "up to $X" (hotel 32, Airbnb 43, host gift 46, meals 47, internet 76) caps the reimbursed amount:
    the claim's amount when at most X, X when over it. "at $X limit" (fuel 21, ground transport 71, parking and tolls 72)
    and "$80 limit per person per meal" (54): the claim's amount when at most X; over it, the amount is not stated (unit 73
    makes manager approval necessary, never sufficient): refused; "is the full charge reimbursable without attached
    approval" -> no; "with attached approval" -> refused.
R11 Tips (units 50, 55): "acceptable up to 20%": the tip counted is the tip when at most a fifth of the food bill it is on
    (5 x tip <= bill), else a fifth of the bill (an amount with no whole-cent value has no model: refused); "included in
    the final price to stay within the Policy limits": the counted tip is part of the day's (47) or the meal's (54) total.
R12 Meals per day (unit 47): the day's total = its food items + its counted tips; reimbursed = the total, capped at $120.
R13 Stays (units 32, 39, 75; the brief's convention): nights = check-out minus check-in (elapsed days, Lean); "over 5 days"
    = more than 5 nights. Days covered (75): the days of the work-related part (first to last day, both included) plus two
    where the case states the distance judgment includes one day before and one day after; a day before the work-related
    part is covered only so.
R14 Mileage amounts (units 57-63, D7, D13): the claim = miles x the rate, a product of two stated quantities; the language
    has no product of two constants, so every mileage amount is refused (ledger). "the rate ... based on your legal
    entity's mileage rates" (62) and "please update the rate ... to match your local compliance laws" (63): an entered rate
    that differs from the entity's stated compliant rate is not the controlling rate.
R15 Trains (units 64-67, D4): standard class with a 14-day lead time (departure minus 14, as R7); the upgrade of unit 67
    ("more than 3 train trips (6 segments) per quarter, and they are over 5 hours in duration"): permitted when the trips
    with every journey over 300 minutes number more than 3 and the journeys over 300 minutes more than 6; not permitted
    when the trips with some journey over 300 minutes number at most 3 and the journeys over 300 minutes fewer than 6
    (every reading of the two numbers fails); otherwise undetermined. One class up = rank of standard + 1.
R16 Rental class (unit 17): "up to the intermediate car class": the class's rank at most intermediate's. The rank order of
    car classes is not in the text: the case's classes are ranked by the encoder (encoder judgement where it is used).
READINGS R17-R29 (added 2026-11-26; the earlier rule each replaces is kept as a planted error, M25-M45). Where a condition
they add is not stated, no answer (refused):
R17 Unit 74: every rule applies only where the case states the travel is not to an internal GitLab event (ievt false).
R18 Unit 4: appr is the manager's approval alone (att, its attachment, is a separate fact no rule needs).
R19 Units 4-7 (R1): every permission is a route of clsok; one with unstated facts (no segments, no trip list) is unknown.
R20 Unit 7 (R4): only segments of international trips count toward the 6.
R21 Unit 16 (R6): the acceptance by silence follows unit 15's email for a flight booked in Navan; no flight, no rule.
R22 Per-day limits (units 21, 39 with 47, 41 with 72, 76): items are grouped under their day (fday, rsday, pkday, nday)
    and the limit is tested on the day's total; an item with no day stated has no amount or permission.
R23 Units 32-36: the $300 cap needs notappl stated false and no AP block exception; a block room with the exception is
    reimbursed at its nightly amount up to the exception's; unit 35's exception = a Corporate Events block or a block
    priced better than Navan.
R24 Unit 67 (R15): standard class booked in Navan with the lead time may be booked; 'may not' needs another class.
R25 Unit 7 (R4): 'internationally' qualifies the trips that make a frequent traveller; whether the permission also needs
    the flight itself to be international, and whether a class below business is covered by 'business class is
    permitted', the text leaves open: granted only for an international flight in business class, refused only for a
    class above business (or not frequent, a segment under 8 hours, no listed purpose); otherwise no answer.
R26 Unit 32 (R10): 'reimbursable up to $300 ... with a 7 day booking lead time': the lead time is a condition of the
    reimbursed amount, as for rentals (unit 17); a stay booked later, or with the lead time unknown: no amount.
R27 Unit 67 (R15): 'they are over 5 hours in duration' read for the journeys OR for the trips (a trip's journeys
    together): permitted when the journey reading permits (it implies the trip reading); not permitted only when both
    readings fail.
R28 Units 7, 67: a trip listed with no stated segments or journeys is not counted (its counts are unknown).
R29 Unit 32 with 31: a stay booked outside Navan is reimbursed only with the Manager's and AP Admin's approval.
No number from a case's facts is ever a coefficient: every coefficient is a literal of the pinned text (20% = 6/5 and 1/5,
the limits $300, $150, $120, $80, $50, 5 and 8 hours, 14, 21 and 7 days, 6'5" = 77 in, 2 m = 200 cm, 3 trips, 6
segments, 1 day before and after) or a unit conversion (60 minutes, 12 inches, 2.54 cm).
"""
from __future__ import annotations

import hashlib
import json

USD, DAY, NDAYS, MIN, CNT, RANK, HCM, INCH = ("usd_cent", "day", "elapsed_day", "minute", "count", "class_rank",
                                              "length_cm", "length_in")

# base -> (unit, wording); a constant is f"{base}_{item}"; bases carry no "_"
BASES = {
    # person
    "cm": (HCM, "the team member's height in centimetres (stated)"),
    "ft": (INCH, "the feet of the team member's height (stated)"),
    "inch": (INCH, "the inches of the team member's height beyond the feet (stated)"),
    "hin": (INCH, "the team member's height in inches"),
    "tlo": (CNT, "the international trips of the quarter whose every segment is over 8 hours"),
    "thi": (CNT, "the international trips of the quarter with some segment of at least 8 hours"),
    "slo": (CNT, "the segments of the quarter's international trips over 8 hours"),
    "shi": (CNT, "the segments of the quarter's international trips of at least 8 hours"),
    "rlo": (CNT, "the train trips of the quarter whose every journey is over 5 hours"),
    "rhi": (CNT, "the train trips of the quarter with some journey over 5 hours"),
    "jlo": (CNT, "the train journeys of the quarter over 5 hours"),
    "rtb": (CNT, "the train trips of the quarter whose journeys together are over 5 hours"),
    "jtb": (CNT, "the train journeys of the quarter's trips whose journeys together are over 5 hours"),
    "tdur": (MIN, "the train trip's journeys' minutes together"),
    "tb": (CNT, "1 if the train trip's journeys together are over 5 hours, else 0"),
    "js": (CNT, "1 if the journey's trip's journeys together are over 5 hours, else 0"),
    # segment (flight segment or train journey)
    "hh": (MIN, "the segment's whole hours (stated)"),
    "mm": (MIN, "the segment's minutes beyond the hours (stated)"),
    "d": (MIN, "the segment's duration in minutes"),
    "lo8": (CNT, "1 if the segment is over 8 hours, else 0"),
    "hi8": (CNT, "1 if the segment is at least 8 hours, else 0"),
    "g5": (CNT, "1 if the journey is over 5 hours, else 0"),
    # trip
    "tl": (CNT, "1 if the trip counts surely, else 0"),
    "th": (CNT, "1 if the trip counts possibly, else 0"),
    # flight, train or rental booking
    "pr": (USD, "the price selected (stated)"),
    "dp": (USD, "the Dynamic Policy price of the search (stated)"),
    "ch": (USD, "the cheapest option's price (stated)"),
    "bu": (USD, "the buffer (stated)"),
    "bk": (DAY, "the booking day (stated)"),
    "dep": (DAY, "the departure, pick-up or check-in day (stated)"),
    "lth": (DAY, "the departure day minus 14 days"),
    "ltw": (DAY, "the departure day minus 21 days"),
    "lid": (DAY, "the latest booking day that meets the ideal advance-purchase interval"),
    "lsv": (DAY, "the pick-up or check-in day minus 7 days"),
    "rsel": (RANK, "the selected class's position, lowest first (stated)"),
    "rstd": (RANK, "the standard class's position (stated)"),
    "rbus": (RANK, "business class's position (stated)"),
    "rint": (RANK, "the intermediate car class's position (stated)"),
    # acceptance check
    "bd": (DAY, "the day the booking was made and the approval email sent (stated)"),
    "bm": (MIN, "the minute of the day of the booking and approval email (stated)"),
    "ad": (DAY, "the day of the automatic acceptance"),
    "am": (MIN, "the minute of the day of the automatic acceptance"),
    "td": (DAY, "the asked day (stated)"),
    "tm": (MIN, "the asked minute of the day (stated)"),
    "pd": (DAY, "the day of the manager's approval of the booking (stated)"),
    "pm": (MIN, "the minute of the day of the manager's approval (stated)"),
    "dd": (DAY, "the day of the denial (stated)"),
    "dm": (MIN, "the minute of the day of the denial (stated)"),
    # amounts
    "amt": (USD, "the amount spent or charged (stated)"),
    "rmb": (USD, "the amount reimbursed"),
    "chg": (USD, "the charge (stated)"),
    "bill": (USD, "the food bill the tip is on (stated)"),
    "tcap": (USD, "a fifth of the food bill (20%)"),
    "tok": (USD, "the tip counted (at most 20%)"),
    "tot": (USD, "the total counted"),
    "alt": (USD, "the Navan alternative's price for the same stay (stated)"),
    "exc": (USD, "the nightly amount of the AP team's exception (stated)"),
    "ent": (USD, "the entity's compliant mileage rate per mile (stated)"),
    "ent2": (USD, "the rate per mile entered in Navan (stated)"),
    # stays and days
    "ci": (DAY, "the check-in day (stated)"),
    "co": (DAY, "the check-out day (stated)"),
    "n": (NDAYS, "the nights of the stay"),
    "ws": (DAY, "the first day of the work-related part (stated)"),
    "we": (DAY, "the last day of the work-related part (stated)"),
    "nw": (NDAYS, "the days of the work-related part"),
    "gw": (NDAYS, "elapsed days from the first to the last day of the work-related part"),
    "cov": (NDAYS, "the days for which the company covers lodging and meals"),
    "dy": (DAY, "the day asked (stated)"),
    "mo": (CNT, "the card's validity in whole months (stated)"),
}
STATED_BASES = ("cm", "ft", "inch", "hh", "mm", "pr", "dp", "ch", "bu", "bk", "dep", "rsel", "rstd", "rbus", "rint", "bd",
                "bm", "td", "tm", "pd", "pm", "dd", "dm", "amt", "chg", "bill", "alt", "exc", "ent", "ent2", "ci", "co", "ws",
                "we", "dy", "mo")
STEP_BASES = tuple(b for b in BASES if b not in STATED_BASES)

FACTS = {
    "incm": "the team member's height is stated in centimetres",
    "us": "the team member is a US team member",
    "intl": "the flight or trip is international",
    "navan": "the booking is made in Navan",
    "appr": "the manager approved a one-class upgrade (whether or not the approval is attached)",
    "att": "the manager's one-class upgrade approval is attached",
    "rcus": "the trip's purpose is meeting with customers",
    "rspk": "the trip's purpose is a speaking engagement",
    "rcnf": "the trip's purpose is representing GitLab at a conference",
    "biz": "the flight is a business-related flight",
    "noact": "nobody approves or denies the booking from its approval email through the asked moment",
    "apv": "the manager approved the booking at the stated moment",
    "den": "the manager denied the booking at the stated moment",
    "cant": "the team member knows they will no longer be able to attend the trip",
    "unused": "the ticket is an unused ticket",
    "pers": "the use or stay is personal",
    "ptsup": "the charge is for an upgrade obtained with personal frequent flyer miles or points",
    "usedwp": "the stated judgment: the team member used unused tickets for business travel whenever possible",
    "conf": "the Navan confirmation is attached to the claim",
    "rcpt": "the car rental receipt is attached to the claim",
    "renting": "the team member is renting a car for the travel",
    "usca": "the car is rented in the US or Canada",
    "mex": "travel to Mexico is required with the rental",
    "outus": "the rental is used traveling outside the US and Canada",
    "fuel": "the expense is fuel or EV charging",
    "mile": "the claim includes mileage",
    "ev": "the expense is Electric Vehicle charging fees",
    "std": "the room is a standard room",
    "refund": "the room booking is refundable",
    "only": "the room is the only available option",
    "extra": "the team member incurred additional hotel charges",
    "mgr": "the manager approved the booking outside Navan",
    "apadm": "AP Admin approved the booking outside Navan",
    "block": "the room is in a conference hotel room block or a Corporate Events organized block",
    "corp": "the block is a Corporate Events block organized by the internal team",
    "excg": "the AP team granted an exception for the nightly amount stated",
    "perscard": "the cost is charged to a personal credit card",
    "navexp": "the cost is submitted for reimbursement via Navan Expense",
    "notappl": "the stated judgment: the $300 USD limit is really not applicable to that area",
    "airbnb": "the stay is booked on the Airbnb platform",
    "cheaper": "the stated judgment: the Airbnb is cheaper than a hotel stay for the trip",
    "manual": "a manual expense of type Lodging is submitted in Navan with the receipt or invoice attached",
    "rsv": "the item is room service taken as a meal",
    "mtag": "the meal is segregated from the hotel bill and tagged under Meals Company Provided",
    "park": "the item is parking",
    "ptag": "the parking is segregated and tagged under Transportation",
    "client": "the item pertains to travel to or from clients, GitLab events or conferences",
    "desc": "the description box gives the trip details",
    "report": "the item is submitted through an expense report",
    "movie": "the item is a movie or minibar purchase",
    "self": "the team member stays with friends or family instead of a hotel or Airbnb for the business trip",
    "approp": "the stated judgment: the host/hostess gift is appropriate",
    "tipd": "the tip is detailed in the description box",
    "prac": "the stated judgment: separating billing at the group meal is practicable",
    "senior": "the team member who pays is the most senior team member present",
    "cash": "the tip is paid in cash",
    "rt": "the ground transport is a round trip (false: a single trip)",
    "app73": "manager approval is attached to the claim",
    "inc": "the stated judgment: depending on the distance, the trip includes one day before and one day after",
    "intev": "the trip is to an internal GitLab conference or meeting",
    "ievt": "the travel this sub-case concerns is to attend an internal GitLab conference or meeting",
    "trav": "the expense is incurred while traveling on GitLab business",
    "nurse": "the team member is nursing while traveling on GitLab approved business",
    "svc": "a milk shipment service is available",
    "svcfee": "the item is a fee of a milk shipment service",
    "bag": "the item is the cost of checking a bag while flying to carry breast milk",
    "cool": "the item is a cooler or container to store breast milk while traveling",
    "ship": "the item is shipment costs or materials (dry ice, packaging, styrofoam coolers, labels)",
    "pbook": "the stay is booked with Navan's Personal trip option",
}
STATED_JUDGMENT = ("usedwp", "notappl", "cheaper", "approp", "prac", "inc")   # D11: the stated judgments
DERIVED = {
    "tall": "the team member is over 6'5\"/2m in height",
    "allgt5": "every segment of the flight is over 5 hours",
    "somelt5": "some segment of the flight is under 5 hours",
    "all8": "every segment of the flight is over 8 hours",
    "some8": "some segment of the flight is under 8 hours",
    "isnext": "the selected class is the next class up from standard",
    "isstd": "the selected class is the standard class",
    "belowbus": "the selected class is below business class",
    "isbus": "the selected class is business class",
    "freq": "the team member travels frequently (3 or more qualifying trips per quarter, 6 or more qualifying segments)",
    "noreason": "the trip's purpose is none of the three listed",
    "ph": "the height upgrade permits the selected class",
    "pdur": "the flight-duration rule permits the selected class",
    "pfreq": "the frequent-traveller rule permits business class",
    "clsok": "the selected class may be chosen (in policy)",
    "hdur": "the height or the flight-duration rule permits the selected class",
    "over20": "the price is over 20% of the Dynamic Policy",
    "overbuf": "the price is more expensive than the cheapest option + the buffer",
    "late": "the booking is made less than 14 days in advance",
    "flag": "the booking is flagged",
    "email": "an email is automatically sent to the manager for approval",
    "fm": "the booking is flagged and sent to the manager",
    "outok": "the booking may be made outside Navan",
    "reached": "the asked moment is at or after the automatic acceptance moment",
    "apvby": "the manager approved the booking at or before the asked moment",
    "denb": "the booking was denied before the automatic acceptance moment",
    "acc": "the booking has been accepted by the asked moment",
    "lvok": "the team member may leave the trip uncanceled",
    "persok": "the team member may use the ticket for a personal flight",
    "buyok": "the team member may buy the new ticket while leaving the unused ticket unused",
    "rclsok": "the car class is within the intermediate car class",
    "rlead": "the rental is booked with the 7 day booking lead time",
    "rreimb": "the rental is reimbursable",
    "rflag": "the booking flags as Out of Policy for review by the manager and the AP team",
    "bxl": "the team member should purchase the excess liability insurance at the rental agency",
    "bcl": "the team member should purchase the liability insurance offered at the rental counter",
    "bcdw": "the team member should purchase the Collision Damage Waiver offered",
    "bmxl": "the team member should purchase the liability insurance for Mexico offered at the rental counter",
    "bboth": "the team member should purchase both the counter liability insurance and the Collision Damage Waiver",
    "fchad": "GitLab provides Foreign Corporate Hired Auto Physical Damage Coverage to reimburse the damage",
    "bothok": "the team member may claim both the fuel or charging and the mileage",
    "rep": "the team member needs to submit an expense report for the stay",
    "dc": "dry cleaning is allowable on the stay",
    "houtok": "the hotel may be booked outside Navan with the approvals given",
    "h20": "the room's price is over 20% of the Dynamic Policy",
    "nrok": "the non-refundable room may be chosen",
    "stdok": "the room is reimbursable under the standard-room allowance",
    "hlead": "the stay is booked with the 7 day booking lead time",
    "better": "the room block has better pricing than Navan",
    "blkok": "the room block booking is reimbursable as described",
    "abok": "the Airbnb stay is reimbursable as described",
    "abperm": "booking through Airbnb is permitted",
    "iok": "the incidental item is reimbursable as described",
    "incok": "every incidental item asked about is reimbursable as described",
    "noclaim": "the item is not allowed as a claim",
    "claimok": "the item may be claimed",
    "grp": "the paying team member may pay and submit the group bill",
    "nrc": "the cash tip does not need a receipt",
    "nrcany": "the cash-tip exemption applies to one of the tips asked about",
    "ctl": "the entered rate is the controlling policy rate",
    "full": "the full charge is reimbursable",
    "t20": "the train price is over 20% of the Dynamic Policy",
    "tlead": "the train booking meets the 14 day booking lead time",
    "tfreq": "the frequent-train upgrade is permitted",
    "tup": "the train class may be booked and charged to the GitLab travel card",
    "rcok": "the rail discount card is reimbursable",
    "covd": "the company covers lodging and meals for the day",
    "mok": "the nursing expense item is reimbursable",
    "mall": "every nursing expense item asked about is reimbursable",
    "pbok": "the personal stay may be booked in Navan with a personal credit card at booking",
    "invok": "the personal stay may be added to the GitLab invoice",
}


# --- formula helpers (ve-quantity@1 wire shapes) --------------------------------------------------------------------

def c(n): return ["const", n]
def U(p, x): return ["unary", p, c(x)]
def Not(f): return ["not", f]
def Implies(a, b): return ["implies", a, b]
def usd(v): return ["decimal", USD, v]
def nd(v): return ["decimal", NDAYS, str(v)]
def mn(v): return ["decimal", MIN, str(v)]
def cnt(v): return ["decimal", CNT, str(v)]
def rk(v): return ["decimal", RANK, str(v)]
def Eq(a, b): return ["eq", a, b]
def Lt(a, b): return ["lt", a, b]
def Le(a, b): return ["le", a, b]
def scale(tag, kk, t): return ["scale", tag, str(kk), t]
def add(tag, a, b): return ["add", tag, a, b]
def no_later(a, b): return ["date_no_later", a, b]
def before(a, b): return ["date_before", a, b]
def shift(a, b, n): return ["shift_days", a, b, str(n)]       # a is n days after b
def elapsed(a, b, n): return ["elapsed_days", a, b, n]       # the elapsed days from a to b equal n
TRUE, FALSE = ["top"], ["bottom"]


def And(*fs):
    fs = [f for f in fs if f is not None]
    if not fs:
        return TRUE
    r = fs[-1]
    for f in reversed(fs[:-1]):
        r = ["and", f, r]
    return r


def Or(*fs):
    fs = [f for f in fs if f is not None]
    if not fs:
        return FALSE
    r = fs[-1]
    for f in reversed(fs[:-1]):
        r = ["or", f, r]
    return r


def Add(unit, terms):
    terms = list(terms)
    if not terms:
        return ["decimal", unit, "0"]
    r = terms[-1]
    for t in reversed(terms[:-1]):
        r = ["add", unit, t, r]
    return r


UNIT_OF = {b: u for b, (u, _) in BASES.items()}


def k(base, x):
    return ["const", UNIT_OF[base], f"{base}_{x}"]


def key(formula):
    return json.dumps(formula, sort_keys=True, separators=(",", ":"))


def A(p, x):
    return key(U(p, x))


def sameday(a, b):
    return And(no_later(a, b), no_later(b, a))


# --- the case context -------------------------------------------------------------------------------------------------

class Ctx:
    """items: [(id, kind)]; parent: {child id: parent id}. Kinds: person, flight, seg, trip, chk, ticket, car, fuelx,
    stay, inc, gift, mday, meal, tip, group, mileage, train, card, ground, pday, work, day, net, milk, mset, personal."""

    def __init__(self, items, parent=None):
        self.items = list(items)
        self.parent = dict(parent or {})
        self.person = "p"

    def of(self, kind):
        return [x for x, kd in self.items if kd == kind]

    def children(self, x, kind=None):
        kinds = dict(self.items)
        return [y for y, p in self.parent.items() if p == x and (kind is None or kinds[y] == kind)]


P = "p"


def pk(base):
    return k(base, P)


def pf(name):
    return U(name, P)


def both(pos, neg, atom, x):
    """atom(x) <- pos; not atom(x) <- neg (either may be None)."""
    out = []
    if pos is not None:
        out.append((Implies(pos, U(atom, x)), A(atom, x)))
    if neg is not None:
        out.append((Implies(neg, Not(U(atom, x))), A(atom, x)))
    return out


# --- the rules, unit by unit ------------------------------------------------------------------------------------------

def _seg_minutes(ctx):
    """R3: a segment's minutes = 60 x hours + minutes."""
    return [(Eq(k("d", s), add(MIN, scale(MIN, 60, k("hh", s)), k("mm", s))), f"d_{s}") for s in ctx.of("seg")]


def _u1(ctx):
    """Unit 1: business flights need to be booked through Navan (even if cheaper outside)."""
    out = []
    for f in ctx.of("flight"):
        out += both(None, U("biz", f), "outok", f)
    return out


def _u2(ctx):
    """Unit 2 (R7): the latest booking day of the ideal interval: departure - 14 (domestic) / - 21 (international)."""
    out = []
    for f in ctx.of("flight"):
        out.append((shift(k("dep", f), k("lth", f), 14), f"lth_{f}"))
        out.append((shift(k("dep", f), k("ltw", f), 21), f"ltw_{f}"))
        out.append((Implies(Not(U("intl", f)), Eq(k("lid", f), k("lth", f))), f"lid_{f}"))
        out.append((Implies(U("intl", f), Eq(k("lid", f), k("ltw", f))), f"lid_{f}"))
    return out


def _over20(atom, x, base="pr"):
    """R5: over 20% of the Dynamic Policy: 5 x price > 6 x DP."""
    pr5, dp6 = scale(USD, 5, k(base, x)), scale(USD, 6, k("dp", x))
    return both(Lt(dp6, pr5), Le(pr5, dp6), atom, x)


def _u3(ctx):
    out = []
    for f in ctx.of("flight"):
        out += _over20("over20", f)
    return out


def _classes(x):
    rs, rst, rb = k("rsel", x), k("rstd", x), k("rbus", x)
    nxt = add(RANK, rst, rk(1))
    out = both(Eq(rs, nxt), Or(Lt(rs, nxt), Lt(nxt, rs)), "isnext", x)
    out += both(Eq(rs, rst), Or(Lt(rs, rst), Lt(rst, rs)), "isstd", x)
    out += both(Lt(rs, rb), Le(rb, rs), "belowbus", x)
    out += both(Eq(rs, rb), Or(Lt(rs, rb), Lt(rb, rs)), "isbus", x)
    return out


def _u4(ctx):
    """Unit 4 (R2): one class of upgrade with manager approval for team members over 6'5"/2m."""
    out = []
    cmh = pk("cm")
    out.append((Eq(pk("hin"), add(INCH, scale(INCH, 12, pk("ft")), pk("inch"))), "hin_p"))
    out += both(And(pf("incm"), Lt(["decimal", HCM, "200"], cmh)), And(pf("incm"), Le(cmh, ["decimal", HCM, "195.58"])),
                "tall", P)
    out += both(And(Not(pf("incm")), Lt(["decimal", INCH, "20000"], scale(INCH, 254, pk("hin")))),
                And(Not(pf("incm")), Le(pk("hin"), ["decimal", INCH, "77"])), "tall", P)
    for f in ctx.of("flight"):
        out += _classes(f)
        one = Le(k("rsel", f), add(RANK, k("rstd", f), rk(1)))
        out += both(And(pf("tall"), U("appr", f), one),
                    Or(Not(pf("tall")), Not(U("appr", f)), Lt(add(RANK, k("rstd", f), rk(1)), k("rsel", f))), "ph", f)
    return out


def _segs5(f, segs):
    out = both(And(*[Lt(mn(300), k("d", s)) for s in segs]), Or(*[Lt(k("d", s), mn(300)) for s in segs]), "allgt5", f)
    out += both(Or(*[Lt(k("d", s), mn(300)) for s in segs]), And(*[Le(mn(300), k("d", s)) for s in segs]), "somelt5", f)
    return out


def _dur_unit(ctx, intl, planted=False):
    """Units 5 (domestic) and 6 (international), R3. R19: a flight with no stated segments: the permission
    is never granted (its duration is unknown) and fails only by its class conditions."""
    out = []
    for f in ctx.of("flight"):
        segs = ctx.children(f, "seg")
        g = U("intl", f) if intl else Not(U("intl", f))
        if not segs:
            if not planted:
                out += both(None, And(g, Or(Not(U("isnext", f)), Not(U("belowbus", f)))), "pdur", f)
            continue
        out += _segs5(f, segs)
        out += both(And(g, U("allgt5", f), U("isnext", f), U("belowbus", f)),
                    And(g, Or(U("somelt5", f), Not(U("isnext", f)), Not(U("belowbus", f)))), "pdur", f)
    return out


def _u5(ctx):
    return _dur_unit(ctx, False)


def _u6(ctx):
    return _dur_unit(ctx, True)


def _u7(ctx, planted_counts=False, planted_routes=False, planted_intl=False, planted_bus=False, planted_empty=False):
    """Unit 7 (R4): the frequent traveller's business class. R20: only the segments of INTERNATIONAL trips count
    toward the 6 segments ('3 or more trips per quarter internationally ... (minimum 6 flight segments ...)'); R19: a
    flight's permission is grounded even with no trip list or no segments: it is then never granted (frequency or
    duration unknown) and fails only by a condition the case states. planted_counts / planted_routes: planted errors
    M27, M26."""
    out = []
    trips = ctx.of("trip")
    allsegs = []
    for t in trips:
        segs = ctx.children(t, "seg")
        allsegs += segs
        it = U("intl", t)
        gi, gn = (None, None) if planted_counts else (it, Not(it))
        for s in segs:
            d = k("d", s)
            out.append((Implies(And(gi, Lt(mn(480), d)), Eq(k("lo8", s), cnt(1))), f"lo8_{s}"))
            out.append((Implies(Or(gn, Le(d, mn(480))), Eq(k("lo8", s), cnt(0))), f"lo8_{s}"))
            out.append((Implies(And(gi, Le(mn(480), d)), Eq(k("hi8", s), cnt(1))), f"hi8_{s}"))
            out.append((Implies(Or(gn, Lt(d, mn(480))), Eq(k("hi8", s), cnt(0))), f"hi8_{s}"))
        if not segs and not planted_empty:                     # R28 (planted M43): no segments, no count
            continue
        out.append((Implies(And(it, *[Lt(mn(480), k("d", s)) for s in segs]), Eq(k("tl", t), cnt(1))), f"tl_{t}"))
        out.append((Implies(Or(Not(it), *[Le(k("d", s), mn(480)) for s in segs]), Eq(k("tl", t), cnt(0))), f"tl_{t}"))
        out.append((Implies(And(it, Or(*[Le(mn(480), k("d", s)) for s in segs])), Eq(k("th", t), cnt(1))), f"th_{t}"))
        out.append((Implies(Or(Not(it), And(*[Lt(k("d", s), mn(480)) for s in segs])), Eq(k("th", t), cnt(0))),
                    f"th_{t}"))
    if trips:
        out.append((Eq(pk("tlo"), Add(CNT, [k("tl", t) for t in trips])), "tlo_p"))
        out.append((Eq(pk("thi"), Add(CNT, [k("th", t) for t in trips])), "thi_p"))
        out.append((Eq(pk("slo"), Add(CNT, [k("lo8", s) for s in allsegs])), "slo_p"))
        out.append((Eq(pk("shi"), Add(CNT, [k("hi8", s) for s in allsegs])), "shi_p"))
        out += both(And(Le(cnt(3), pk("tlo")), Le(cnt(6), pk("slo"))), Or(Lt(pk("thi"), cnt(3)), Lt(pk("shi"), cnt(6))),
                    "freq", P)
    for f in ctx.of("flight"):
        segs = ctx.children(f, "seg")
        if planted_routes and (not segs or not trips):
            continue
        if segs:
            out += both(And(*[Lt(mn(480), k("d", s)) for s in segs]), Or(*[Le(k("d", s), mn(480)) for s in segs]),
                        "all8", f)
            out += both(Or(*[Lt(k("d", s), mn(480)) for s in segs]), And(*[Le(mn(480), k("d", s)) for s in segs]),
                        "some8", f)
        out += both(And(Not(U("rcus", f)), Not(U("rspk", f)), Not(U("rcnf", f))),
                    Or(U("rcus", f), U("rspk", f), U("rcnf", f)), "noreason", f)
        # R25: refused only above business; the flight's own international status does not refuse (planted M39, M40)
        above = Not(U("isbus", f)) if planted_bus else Lt(k("rbus", f), k("rsel", f))
        out += both(And(pf("freq"), U("intl", f), U("all8", f), Not(U("noreason", f)), U("isbus", f)) if segs else None,
                    Or(Not(pf("freq")), Not(U("intl", f)) if planted_intl else None, U("some8", f) if segs else None,
                       U("noreason", f), above), "pfreq", f)
    return out


def _clsok(ctx, planted=False):
    """R1: in policy when standard or permitted; out of policy when not standard and every permission fails. R19:
    every permission of units 4-7 is always one of the routes; one whose facts are not stated (no segments, no trip
    list) is unknown, so 'out of policy' then needs it to fail on a stated condition (else no answer). planted: planted
    error M26 (a route not grounded is dropped)."""
    out = []
    for f in ctx.of("flight"):
        segs = bool(ctx.children(f, "seg"))
        trips = bool(ctx.of("trip"))
        if planted:
            perms = [U("ph", f)] + ([U("pdur", f)] if segs else []) + ([U("pfreq", f)] if trips else [])
        else:
            perms = [U("ph", f), U("pdur", f), U("pfreq", f)]
        out += both(Or(U("isstd", f), *perms), And(Not(U("isstd", f)), *[Not(p) for p in perms]), "clsok", f)
        if segs or not planted:
            out += both(Or(U("ph", f), U("pdur", f)), And(Not(U("ph", f)), Not(U("pdur", f))), "hdur", f)
    return out


def _u8(ctx):
    """Unit 8: frequent flyer participation never makes an out-of-policy option in policy (carried by structure: no rule
    grants a class for points)."""
    return []


def _u9(ctx):
    """Unit 9: points upgrades allowed, the respective charges are not reimbursed."""
    return [(Implies(U("ptsup", x), Eq(k("rmb", x), usd("0"))), f"rmb_{x}") for x in ctx.of("ticket")]


def _u10(ctx):
    return [r for x in ctx.of("ticket") for r in both(None, U("cant", x), "lvok", x)]


def _u12(ctx):
    """Unit 12 (stated judgment 'whenever possible')."""
    return [r for x in ctx.of("ticket") for r in both(None, And(U("unused", x), Not(U("usedwp", x))), "buyok", x)]


def _u13(ctx):
    return [r for x in ctx.of("ticket") for r in both(None, And(U("unused", x), U("pers", x)), "persok", x)]


def _u14(ctx):
    """Unit 14 (R5): the three automatic out-of-policy criteria; with unit 3's two, the flag."""
    out = []
    for f in ctx.of("flight"):
        pr, cb = k("pr", f), add(USD, k("ch", f), k("bu", f))
        out += both(Lt(cb, pr), Le(pr, cb), "overbuf", f)
        out += both(before(k("lth", f), k("bk", f)), no_later(k("bk", f), k("lth", f)), "late", f)
        crit = [U("over20", f), U("overbuf", f), Not(U("clsok", f)), U("late", f), Not(U("navan", f))]
        out += both(Or(*crit), And(*[Not(x) if x[0] != "not" else x[1] for x in crit]), "flag", f)
    return out


def _u15(ctx):
    out = []
    for f in ctx.of("flight"):
        crit = [U("overbuf", f), Not(U("clsok", f)), U("late", f)]
        out += both(Or(*crit), And(Not(U("overbuf", f)), U("clsok", f), Not(U("late", f))), "email", f)
        out += both(And(U("flag", f), U("email", f)), Or(Not(U("flag", f)), Not(U("email", f))), "fm", f)
    return out


def _u16(ctx, crit="email", need_flight=True):
    """Unit 16 (R6): the automatic acceptance 24 hours after the booking/email moment. R21: the acceptance follows
    unit 15's email, which is sent when a flight booked in Navan triggers one of unit 14's three criteria (not any
    flag: over 20% of the Dynamic Policy is 'flagged for further review', and a booking outside Navan 'will need to be
    reviewed by your manager and the AP team', unit 3); and only for a flight in the sub-case (with no flight the
    acceptance by silence has no booking to attach to, so no answer). crit="flag" / need_flight=False: planted errors
    M28, M29."""
    out = []
    flights = ctx.of("flight")
    for x in ctx.of("chk"):
        out.append((shift(k("ad", x), k("bd", x), 1), f"ad_{x}"))
        out.append((Eq(k("am", x), k("bm", x)), f"am_{x}"))
        ad, am, td, tm = k("ad", x), k("am", x), k("td", x), k("tm", x)
        out += both(Or(before(ad, td), And(sameday(ad, td), Le(am, tm))),
                    Or(before(td, ad), And(sameday(ad, td), Lt(tm, am))), "reached", x)
        pd, pm = k("pd", x), k("pm", x)
        out += both(And(U("apv", x), Or(before(pd, td), And(sameday(pd, td), Le(pm, tm)))), None, "apvby", x)
        dd, dm = k("dd", x), k("dm", x)
        out += both(And(U("den", x), Or(before(dd, ad), And(sameday(dd, ad), Lt(dm, am)))), None, "denb", x)
        if crit == "flag":
            fl = [U("flag", f) for f in flights]
        else:
            fl = [And(U("navan", f), U("email", f)) for f in flights]
        if flights or not need_flight:
            out += both(Or(And(*fl, U("noact", x), U("reached", x)), U("apvby", x)),
                        Or(And(*fl, U("noact", x), Not(U("reached", x))), U("denb", x)), "acc", x)

    return out


def _u17(ctx):
    """Unit 17 (R16): rentals reimbursable, through Navan, up to intermediate, 7 day lead time."""
    out = []
    for r in ctx.of("car"):
        out.append((shift(k("dep", r), k("lsv", r), 7), f"lsv_{r}"))
        out += both(Le(k("rsel", r), k("rint", r)), Lt(k("rint", r), k("rsel", r)), "rclsok", r)
        out += both(no_later(k("bk", r), k("lsv", r)), before(k("lsv", r), k("bk", r)), "rlead", r)
        out += both(And(U("navan", r), U("rclsok", r), U("rlead", r), U("conf", r), U("rcpt", r)),
                    Not(U("rclsok", r)), "rreimb", r)
    return out


def _u18(ctx):
    return [rr for r in ctx.of("car") for rr in both(Not(U("navan", r)), None, "rflag", r)]


def _u19(ctx):
    """Unit 19: the confirmation and receipt attached (a condition of unit 17's rule above)."""
    return []


def _u20(ctx):
    """Unit 20: gas but not mileage when renting a car."""
    return [rr for x in ctx.of("fuelx") for rr in both(None, And(U("renting", x), U("fuel", x), U("mile", x)), "bothok", x)]


def _cap_limit(x, lim, cap):
    """R10: amount when at most the limit; over it: the cap ('up to') or nothing ('limit')."""
    out = [(Implies(Le(k("amt", x), usd(lim)), Eq(k("rmb", x), k("amt", x))), f"rmb_{x}")]
    if cap:
        out.append((Implies(Lt(usd(lim), k("amt", x)), Eq(k("rmb", x), usd(lim))), f"rmb_{x}"))
    return out


def _u21(ctx, planted=False):
    """Unit 21: fuel at $300 limit per day (R10: a limit). R22: the limit is on the DAY's fuel: a fuel item
    is grouped under its day (item kind fday, the day's fuel purchases as its children); the day's total = the sum of its
    items; each item is reimbursed in full when the day's total is at most $300; over it the amount is not stated
    (refused). A fuel item with no day stated: no amount (the day's other purchases are unknown). planted: planted
    error M30 (per item)."""
    out = []
    if planted:
        for x in ctx.of("fuelx"):
            out += [(Implies(U("renting", x), f), t) for f, t in _cap_limit(x, "300.00", False)]
        return out
    for dd in ctx.of("fday"):
        xs = ctx.children(dd, "fuelx")
        if not xs:
            continue
        out.append((Eq(k("tot", dd), Add(USD, [k("amt", x) for x in xs])), f"tot_{dd}"))
        for x in xs:
            out.append((Implies(And(U("renting", x), Le(k("tot", dd), usd("300.00"))), Eq(k("rmb", x), k("amt", x))),
                        f"rmb_{x}"))
    return out


def _u22(ctx):
    return [rr for r in ctx.of("car") for rr in both(U("usca", r), None, "bxl", r)]


def _u23(ctx):
    return [rr for r in ctx.of("car") for rr in both(And(Not(pf("us")), U("usca", r)), None, "bcl", r)]


def _u24(ctx):
    out = []
    for r in ctx.of("car"):
        out += both(None, Or(U("usca", r), U("mex", r)), "bcdw", r)
        out += both(U("mex", r), None, "bmxl", r)
    return out


def _u25(ctx):
    out = []
    for r in ctx.of("car"):
        out += both(U("outus", r), None, "bcl", r)
        out += both(U("outus", r), None, "bcdw", r)
        out += both(And(U("bcl", r), U("bcdw", r)), Or(Not(U("bcl", r)), Not(U("bcdw", r))), "bboth", r)
    return out


def _u26(ctx):
    return [rr for r in ctx.of("car") for rr in both(None, TRUE, "fchad", r)]


def _u28(ctx):
    return [rr for h in ctx.of("stay") for rr in both(None, And(U("navan", h), Not(U("extra", h))), "rep", h)]


def _incidental(ctx, n, planted=False):
    """Units 29, 30, 39-41 (and 47's, 72's limits): room service as a meal, parking; each segregated and tagged,
    within the limit, submitted through an expense report. R22: the limits are per DAY. Room service 'as a meal'
    counts in the day's meals, up to $120 per day (unit 47): the item's meal day is its child of kind rsday, whose
    children are the day's other meals (meal) and tips (tip, counted as R11); the day's total = the item + those. Hotel
    parking counts in the day's parking and tolls, $150 limit per day (unit 72): its day is its child of kind
    pkday, whose children are the day's other parking and tolls (ground). Within the day's limit -> reimbursable as
    described; over it, or no day stated -> no answer. planted: planted errors M34, M35 (per item)."""
    out = []
    for x in ctx.of("inc"):
        if n == 39:
            if planted:
                out += both(And(U("rsv", x), U("mtag", x), U("report", x), Le(k("amt", x), usd("120.00"))), None, "iok", x)
            for dd in ([] if planted else ctx.children(x, "rsday")):
                food, tips = ctx.children(dd, "meal"), ctx.children(dd, "tip")
                out.append((Eq(k("tot", dd), Add(USD, [k("amt", x)] + [k("amt", y) for y in food] +
                                                [k("tok", y) for y in tips])), f"tot_{dd}"))
                out += both(And(U("rsv", x), U("mtag", x), U("report", x), Le(k("tot", dd), usd("120.00"))), None,
                            "iok", x)
        if n == 41:
            if planted:
                out += both(And(U("park", x), U("ptag", x), U("client", x), U("desc", x), U("report", x),
                                Le(k("amt", x), usd("150.00"))), None, "iok", x)
            for dd in ([] if planted else ctx.children(x, "pkday")):
                ys = ctx.children(dd, "ground")
                out.append((Eq(k("tot", dd), Add(USD, [k("amt", x)] + [k("amt", y) for y in ys])), f"tot_{dd}"))
                out += both(And(U("park", x), U("ptag", x), U("client", x), U("desc", x), U("report", x),
                                Le(k("tot", dd), usd("150.00"))), None, "iok", x)
    if n == 30:
        for h in ctx.of("stay"):
            xs = ctx.children(h, "inc")
            if xs:
                out += both(And(*[U("iok", x) for x in xs]), Or(*[Not(U("iok", x)) for x in xs]), "incok", h)
    return out


def _u31(ctx):
    out = []
    for h in ctx.of("stay"):
        out += both(And(Not(U("navan", h)), U("mgr", h), U("apadm", h)),
                    And(Not(U("navan", h)), Or(Not(U("mgr", h)), Not(U("apadm", h)))), "houtok", h)
    return out


def _u32(ctx, notappl_guard=True, block_exception=True, planted_lead=False, planted_outside=False):
    """Unit 32 (R10, R13): standard rooms up to $300 per night, 7 day lead time. R23: the $300 CAP (a nightly
    amount over $300 -> $300) applies only where the case states the $300 limit is applicable to the area (unit 33
    'in case the $300 USD limit is really not applicable to that area': notappl stated false) and the room is not a block
    room with the AP team's exception granted (unit 36 'please contact the AP team for an exception to be
    granted'). A block room with the exception granted is reimbursed at its nightly amount when at most the exception's
    amount (exc). Otherwise over $300 no amount is answered. A nightly amount at most $300 is reimbursed in full either
    way (the Dynamic Policy only gives more room). notappl_guard=False / block_exception=False: planted errors
    M31, M33."""
    out = []
    for h in ctx.of("stay"):
        out.append((shift(k("ci", h), k("lsv", h), 7), f"lsv_{h}"))
        out += both(no_later(k("bk", h), k("lsv", h)), before(k("lsv", h), k("bk", h)), "hlead", h)
        std, amt = U("std", h), k("amt", h)
        lead = None if planted_lead else U("hlead", h)          # R26 (planted M41: no lead-time condition)
        if not planted_outside:                                 # R29 (planted M45): outside Navan needs unit 31's approvals
            lead = And(lead, Or(U("navan", h), And(U("mgr", h), U("apadm", h))))
        out.append((Implies(And(std, lead, Le(amt, usd("300.00"))), Eq(k("rmb", h), amt)), f"rmb_{h}"))
        cap = [std, lead, Lt(usd("300.00"), amt)]
        if notappl_guard:
            cap.append(Not(U("notappl", h)))
        if block_exception:
            cap.append(Or(Not(U("block", h)), Not(U("excg", h))))
            out.append((Implies(And(std, lead, U("block", h), U("excg", h), Le(amt, k("exc", h))), Eq(k("rmb", h), amt)),
                        f"rmb_{h}"))
        out.append((Implies(And(*[c for c in cap if c is not None]), Eq(k("rmb", h), usd("300.00"))), f"rmb_{h}"))
        out += both(None, Not(U("std", h)), "stdok", h)
    return out


def _u33(ctx):
    out = []
    for h in ctx.of("stay"):
        out += _over20("h20", h, "amt")
    return out


def _u34(ctx, planted=False):
    """Unit 34 with 35's exception: refundable unless the only option. R23: the block exception is unit 35's
    own: 'the Corporate Events hotel room blocks organized by the internal team or if the conference hotel room block has
    better pricing than Navan', i.e. a block that is a Corporate Events block (corp) or priced better than Navan (better);
    not any block. planted: planted error M32 (any block)."""
    out = []
    for h in ctx.of("stay"):
        if planted:
            out += both(Or(U("only", h), U("block", h)), And(Not(U("only", h)), Not(U("block", h))), "nrok", h)
            continue
        exc = And(U("block", h), Or(U("corp", h), U("better", h)))
        noexc = Or(Not(U("block", h)), And(Not(U("corp", h)), Not(U("better", h))))
        out += both(Or(U("only", h), exc), And(Not(U("only", h)), noexc), "nrok", h)
    return out


def _u35(ctx):
    """Unit 35: the block exception (the block's pricing better than Navan's alternative)."""
    out = []
    for h in ctx.of("stay"):
        out += both(Lt(k("amt", h), k("alt", h)), Le(k("alt", h), k("amt", h)), "better", h)
    return out


def _u36(ctx):
    """Units 36-37 (and 31): a block over $300 needs the AP team's exception; charged to a personal card and submitted via
    Navan Expense; booked outside Navan with the manager's and AP Admin's approval."""
    out = []
    for h in ctx.of("stay"):
        within = Or(Le(k("amt", h), usd("300.00")), And(U("excg", h), Le(k("amt", h), k("exc", h))))
        out += both(And(U("block", h), Or(U("corp", h), U("better", h)), within, U("houtok", h), U("perscard", h),
                        U("navexp", h), U("hlead", h)), None, "blkok", h)
    return out


def _u39(ctx, planted=False):
    out = []
    for h in ctx.of("stay"):
        out.append((elapsed(k("ci", h), k("co", h), k("n", h)), f"n_{h}"))
        out += both(Lt(nd(5), k("n", h)), Le(k("n", h), nd(5)), "dc", h)
    return out + _incidental(ctx, 39, planted)


def _u41(ctx, planted=False):
    return _incidental(ctx, 41, planted)


def _u42(ctx):
    return [rr for x in ctx.of("inc") for rr in both(None, U("movie", x), "claimok", x)]


def _u43(ctx):
    """Units 43-45: Airbnb on the platform, the hotel's amount restriction, permitted if cheaper (R8), manual Lodging
    expense with the receipt."""
    out = []
    for h in ctx.of("stay"):
        out += both(And(U("airbnb", h), U("cheaper", h)), And(U("airbnb", h), Not(U("cheaper", h))), "abperm", h)
        out += both(And(U("airbnb", h), U("abperm", h), U("manual", h), Le(k("amt", h), usd("300.00"))), None, "abok", h)
    return out


def _u46(ctx):
    out = []
    for x in ctx.of("gift"):
        out += [(Implies(And(U("self", x), U("approp", x)), f), t) for f, t in _cap_limit(x, "50.00", True)]
    return out


def _tips(ctx):
    """R11: the counted tip: the tip when 5 x tip <= bill, else a fifth of the bill."""
    out = []
    for x in ctx.of("tip"):
        out.append((Eq(scale(USD, 5, k("tcap", x)), k("bill", x)), f"tcap_{x}"))
        out.append((Implies(And(U("tipd", x), Le(k("amt", x), k("tcap", x))), Eq(k("tok", x), k("amt", x))), f"tok_{x}"))
        out.append((Implies(And(U("tipd", x), Lt(k("tcap", x), k("amt", x))), Eq(k("tok", x), k("tcap", x))), f"tok_{x}"))
    return out


def _u47(ctx):
    """Unit 47 (R12): meals per day, the day's total (food + counted tips) capped at $120."""
    out = []
    for dd in ctx.of("mday"):
        food, tips = ctx.children(dd, "meal"), ctx.children(dd, "tip")
        out.append((Eq(k("tot", dd), Add(USD, [k("amt", x) for x in food] + [k("tok", x) for x in tips])), f"tot_{dd}"))
        out.append((Implies(And(U("trav", dd), Le(k("tot", dd), usd("120.00"))), Eq(k("rmb", dd), k("tot", dd))),
                    f"rmb_{dd}"))
        out.append((Implies(And(U("trav", dd), Lt(usd("120.00"), k("tot", dd))), Eq(k("rmb", dd), usd("120.00"))),
                    f"rmb_{dd}"))
    return out


def _group(ctx):
    """Units 48 / 53: the most senior team member present pays and submits when separating billing is not practicable."""
    out = []
    for x in ctx.of("group"):
        out += both(And(Not(U("prac", x)), U("senior", x)), U("prac", x), "grp", x)
    return out


def _cashtip(ctx):
    """Units 50 / 55: for US team members, cash tips under $50 need no receipt."""
    out = []
    for x in ctx.of("tip"):
        out += both(And(pf("us"), U("cash", x), Lt(k("amt", x), usd("50.00"))),
                    Or(Not(pf("us")), Not(U("cash", x)), Le(usd("50.00"), k("amt", x))), "nrc", x)
    for g in ctx.of("tipset"):
        xs = ctx.children(g, "tip")
        out += both(Or(*[U("nrc", x) for x in xs]), And(*[Not(U("nrc", x)) for x in xs]), "nrcany", g)
    return out


def _u50(ctx):
    return _tips(ctx) + _cashtip(ctx)


def _u54(ctx):
    """Unit 54 (R10, R11): $80 limit per person per meal (food + counted tip); over it the amount is not stated."""
    out = []
    for m in ctx.of("tmeal"):
        food, tips = ctx.children(m, "meal"), ctx.children(m, "tip")
        out.append((Eq(k("tot", m), Add(USD, [k("amt", x) for x in food] + [k("tok", x) for x in tips])), f"tot_{m}"))
        out.append((Implies(Le(k("tot", m), usd("80.00")), Eq(k("rmb", m), k("tot", m))), f"rmb_{m}"))
    return out


def _u61(ctx):
    return [rr for x in ctx.of("fuelx") for rr in both(None, And(U("ev", x), U("mile", x)), "bothok", x)]


def _u62(ctx):
    """Units 62-63 (R14): an entered rate differing from the entity's compliant rate is not the controlling rate."""
    out = []
    for x in ctx.of("mileage"):
        out += both(None, Or(Lt(k("ent2", x), k("ent", x)), Lt(k("ent", x), k("ent2", x))), "ctl", x)
    return out


def _u64(ctx):
    out = []
    for t in ctx.of("train"):
        out += _over20("t20", t)
    return out


def _u66(ctx):
    """Unit 66: standard cabin class with a 14 day booking lead time."""
    out = []
    for t in ctx.of("train"):
        out.append((shift(k("dep", t), k("lth", t), 14), f"lth_{t}"))
        out += both(no_later(k("bk", t), k("lth", t)), before(k("lth", t), k("bk", t)), "tlead", t)
    return out


def _u67(ctx, planted=False, planted_trip=False, planted_empty=False):
    """Unit 67 (R15): the frequent-train upgrade of one class. R24: the standard class is always the
    bookable class (unit 66 'Train rides must be standard cabin class with a 14 day booking lead time'; unit 65 'Trains
    booked through Navan will be paid by GitLab travel card'): standard, booked in Navan with the lead time -> may be
    booked; 'may not' needs a class other than standard. planted: planted error M36."""
    out = []
    trips = ctx.of("ttrip")
    allsegs = []
    for t in trips:
        segs = ctx.children(t, "seg")
        allsegs += segs
        for s in segs:
            out.append((Implies(Lt(mn(300), k("d", s)), Eq(k("g5", s), cnt(1))), f"g5_{s}"))
            out.append((Implies(Le(k("d", s), mn(300)), Eq(k("g5", s), cnt(0))), f"g5_{s}"))
        if not segs and not planted_empty:                     # R28 (planted M44): no journeys, no count
            continue
        out.append((Implies(And(*[Lt(mn(300), k("d", s)) for s in segs]), Eq(k("tl", t), cnt(1))), f"tl_{t}"))
        out.append((Implies(Or(*[Le(k("d", s), mn(300)) for s in segs]), Eq(k("tl", t), cnt(0))), f"tl_{t}"))
        out.append((Implies(Or(*[Lt(mn(300), k("d", s)) for s in segs]), Eq(k("th", t), cnt(1))), f"th_{t}"))
        out.append((Implies(And(*[Le(k("d", s), mn(300)) for s in segs]), Eq(k("th", t), cnt(0))), f"th_{t}"))
    if trips:
        out.append((Eq(pk("rlo"), Add(CNT, [k("tl", t) for t in trips])), "rlo_p"))
        out.append((Eq(pk("rhi"), Add(CNT, [k("th", t) for t in trips])), "rhi_p"))
        out.append((Eq(pk("jlo"), Add(CNT, [k("g5", s) for s in allsegs])), "jlo_p"))
        neg = [Le(pk("rhi"), cnt(3)), Lt(pk("jlo"), cnt(6))]
        if not planted_trip:                                   # R27 (planted M42: the journey reading alone)
            for t in trips:
                segs = ctx.children(t, "seg")
                if not segs and not planted_empty:
                    continue
                out.append((Eq(k("tdur", t), Add(MIN, [k("d", s) for s in segs])), f"tdur_{t}"))
                out.append((Implies(Lt(mn(300), k("tdur", t)), Eq(k("tb", t), cnt(1))), f"tb_{t}"))
                out.append((Implies(Le(k("tdur", t), mn(300)), Eq(k("tb", t), cnt(0))), f"tb_{t}"))
                for s in segs:
                    out.append((Implies(Lt(mn(300), k("tdur", t)), Eq(k("js", s), cnt(1))), f"js_{s}"))
                    out.append((Implies(Le(k("tdur", t), mn(300)), Eq(k("js", s), cnt(0))), f"js_{s}"))
            out.append((Eq(pk("rtb"), Add(CNT, [k("tb", t) for t in trips])), "rtb_p"))
            out.append((Eq(pk("jtb"), Add(CNT, [k("js", s) for s in allsegs])), "jtb_p"))
            neg += [Le(pk("rtb"), cnt(3)), Lt(pk("jtb"), cnt(6))]
        out += both(And(Lt(cnt(3), pk("rlo")), Lt(cnt(6), pk("jlo"))), And(*neg), "tfreq", P)
    for t in ctx.of("train"):
        out += _classes(t)
        if planted:
            if trips:
                out += both(And(pf("tfreq"), U("isnext", t), U("tlead", t), U("navan", t)),
                            Or(Not(pf("tfreq")), Lt(add(RANK, k("rstd", t), rk(1)), k("rsel", t))), "tup", t)
            continue
        out += both(And(U("isstd", t), U("tlead", t), U("navan", t)), None, "tup", t)
        if trips:
            out += both(And(pf("tfreq"), U("isnext", t), U("tlead", t), U("navan", t)),
                        And(Not(U("isstd", t)), Or(Not(pf("tfreq")), Lt(add(RANK, k("rstd", t), rk(1)), k("rsel", t)))),
                        "tup", t)
    return out


def _u68(ctx):
    return [rr for x in ctx.of("card") for rr in both(None, Or(Eq(k("mo", x), cnt(12)), Eq(k("mo", x), cnt(1))), "rcok", x)]


def _u69(ctx):
    """Unit 69: ground transport and parking to clients acceptable; not both fuel/EV charging and mileage."""
    return [rr for x in ctx.of("fuelx") for rr in both(None, And(Or(U("fuel", x), U("ev", x)), U("mile", x)), "bothok", x)]


def _u71(ctx):
    """Units 70-71, 73 (R10): taxis $300 per round trip, $150 single; over a limit without approval: not in full."""
    out = []
    for x in ctx.of("ground"):
        g = And(U("client", x), U("desc", x))
        out.append((Implies(And(g, U("rt", x), Le(k("amt", x), usd("300.00"))), Eq(k("rmb", x), k("amt", x))), f"rmb_{x}"))
        out.append((Implies(And(g, Not(U("rt", x)), Le(k("amt", x), usd("150.00"))), Eq(k("rmb", x), k("amt", x))),
                    f"rmb_{x}"))
        over = Or(And(U("rt", x), Lt(usd("300.00"), k("amt", x))), And(Not(U("rt", x)), Lt(usd("150.00"), k("amt", x))))
        out += both(None, And(over, Not(U("app73", x))), "full", x)
    return out


def _u72(ctx):
    """Units 72-73 (R10): parking and tolls $150 per day."""
    out = []
    for dd in ctx.of("pday"):
        xs = ctx.children(dd, "ground")
        out.append((Eq(k("tot", dd), Add(USD, [k("amt", x) for x in xs])), f"tot_{dd}"))
        out.append((Implies(And(U("client", dd), U("desc", dd), Le(k("tot", dd), usd("150.00"))),
                    Eq(k("rmb", dd), k("tot", dd))), f"rmb_{dd}"))
        out += both(None, And(Lt(usd("150.00"), k("tot", dd)), Not(U("app73", dd))), "full", dd)
    return out


def _u75(ctx):
    """Units 74-75 (R13): days covered: the work-related part, plus one day before and one after where stated."""
    out = []
    for w in ctx.of("work"):
        ok = Not(U("intev", w))
        out.append((elapsed(k("ws", w), k("we", w), k("gw", w)), f"gw_{w}"))
        out.append((Eq(k("nw", w), add(NDAYS, k("gw", w), nd(1))), f"nw_{w}"))
        out.append((Implies(And(ok, U("inc", w)), Eq(k("cov", w), add(NDAYS, k("nw", w), nd(2)))), f"cov_{w}"))
        out.append((Implies(And(ok, Not(U("inc", w))), Eq(k("cov", w), k("nw", w))), f"cov_{w}"))
        for y in ctx.children(w, "day"):
            dy, ws, we = k("dy", y), k("ws", w), k("we", w)
            out += both(And(ok, no_later(ws, dy), no_later(dy, we)),
                        And(ok, Not(U("inc", w)), Or(before(dy, ws), before(we, dy))), "covd", y)
    return out


def _u76(ctx, planted=False):
    """Unit 76 (R10): internet up to $50 per day. R22: the cap is on the DAY's internet: an internet charge
    is grouped under its day (item kind nday, the day's charges as its children); the day's total = their sum; the day
    is reimbursed its total when at most $50, $50 when over; each charge is reimbursed in full when the day's total is at
    most $50, and a day's only charge is reimbursed what the day is; otherwise no per-charge amount (how the $50 is shared
    is not stated). A charge with no day stated: no amount. planted: planted error M38 (per charge)."""
    out = []
    if planted:
        for x in ctx.of("net"):
            out += [(Implies(And(U("trav", x), U("desc", x)), f), t) for f, t in _cap_limit(x, "50.00", True)]
        return out
    for dd in ctx.of("nday"):
        xs = ctx.children(dd, "net")
        if not xs:
            continue
        g = And(*[And(U("trav", x), U("desc", x)) for x in xs])
        tot = k("tot", dd)
        out.append((Eq(tot, Add(USD, [k("amt", x) for x in xs])), f"tot_{dd}"))
        out.append((Implies(And(g, Le(tot, usd("50.00"))), Eq(k("rmb", dd), tot)), f"rmb_{dd}"))
        out.append((Implies(And(g, Lt(usd("50.00"), tot)), Eq(k("rmb", dd), usd("50.00"))), f"rmb_{dd}"))
        for x in xs:
            out.append((Implies(And(g, Le(tot, usd("50.00"))), Eq(k("rmb", x), k("amt", x))), f"rmb_{x}"))
        if len(xs) == 1:
            out.append((Implies(And(g, Lt(usd("50.00"), tot)), Eq(k("rmb", xs[0]), usd("50.00"))), f"rmb_{xs[0]}"))
    return out


def _u79(ctx):
    """Units 78-79 (R8): the nursing expenses; checking a bag only if no milk shipment service is available."""
    out = []
    for x in ctx.of("milk"):
        g = pf("nurse")
        out += both(And(g, Or(U("svcfee", x), U("cool", x), U("ship", x), And(U("bag", x), Not(U("svc", x))))),
                    And(U("bag", x), U("svc", x)), "mok", x)
    for g in ctx.of("mset"):
        xs = ctx.children(g, "milk")
        out += both(And(*[U("mok", x) for x in xs]), Or(*[Not(U("mok", x)) for x in xs]), "mall", g)
    return out


def _u81(ctx):
    out = []
    for x in ctx.of("personal"):
        out += both(And(U("pers", x), U("pbook", x), U("perscard", x)), And(U("pers", x), U("pbook", x), Not(U("perscard", x))),
                    "pbok", x)
    return out


def _u82(ctx):
    return [rr for x in ctx.of("personal") for rr in both(None, And(U("pers", x), U("pbook", x)), "invok", x)]


def _u74(ctx):
    """Unit 74 (R17): travel to an internal GitLab conference or meeting follows the event's own guidelines
    'rather than this general Travel Policy'. Written as a guard on EVERY ground rule of this translation (rules()):
    each rule holds only where the case states the travel is not to an internal event (not ievt(p)); stated to be one, or
    not stated: no rule applies, so no answer. This builder grounds nothing itself; its presence turns the guard on
    (planted error M37 drops it: then only unit 75 carries such a guard)."""
    return []


_u74.guard74 = True


def _merge(*builders):
    return lambda ctx: [f for b in builders for f in b(ctx)]


def _nothing(ctx):
    return []


UNITS = {
    1: ("PART", _u1, "other:norm", "unit 1: 'need to be booked through Navan' written (R8); the Compass screenshot request is "
        "a request to the team member with no outcome (other:norm)"),
    2: ("PART", _u2, "other:norm", "unit 2: the latest booking day of the ideal interval (R7) written; 'as early as "
        "possible' and 'ideally' are recommendations (stated judgment / no outcome)"),
    3: ("RULE", _u3, "unit 3: over 20% of the Dynamic Policy (R5); outside Navan flags (in unit 14's rule)"),
    4: ("RULE", _merge(_u4, _seg_minutes, _clsok), "unit 4: one class of upgrade with manager approval over 6'5\"/2m (R1, R2)"),
    5: ("RULE", _u5, "unit 5: domestic flights over 5 hours (R3)"),
    6: ("RULE", _u6, "unit 6: international flights over 5 hours (R3)"),
    7: ("RULE", _u7, "unit 7: frequent traveller's business class (R4)"),
    8: ("RULE", _u8, "unit 8: carried by structure (no class is granted for points)"),
    9: ("RULE", _u9, "unit 9: points upgrades: the charges are not reimbursed ($0)"),
    10: ("RULE", _u10, "unit 10: responsible for canceling (R8)"),
    11: ("NOT", None, "other:norm", "unit 11: 'typically result in flight credit' describes a system with no definite "
         "outcome (D10)"),
    12: ("PART", _u12, "other:judgment standard", "unit 12: 'whenever possible' a stated judgment; the Compass request is a "
         "request with no outcome"),
    13: ("RULE", _u13, "unit 13: no personal benefit from unused tickets"),
    14: ("RULE", _u14, "unit 14: the three automatic out-of-policy flags (R5)"),
    15: ("PART", _u15, "other:norm", "unit 15: the email to the manager written; 'Please provide sufficient reasoning' is a "
         "request with no outcome"),
    16: ("RULE", _u16, "unit 16: acceptance 24 hours after the email (R6; dates and minutes in Lean)"),
    17: ("RULE", _u17, "unit 17: rentals reimbursable through Navan, up to intermediate, 7 day lead time (R16)"),
    18: ("RULE", _u18, "unit 18: outside Navan flags Out of Policy for review"),
    19: ("RULE", _u19, "unit 19: the attachments (conditions of unit 17's rule)"),
    20: ("RULE", _u20, "unit 20: gas but not mileage when renting"),
    21: ("RULE", _u21, "unit 21: fuel $300 limit per day (R10)"),
    22: ("RULE", _u22, "unit 22: purchase the excess liability (US or Canada rentals, R9)"),
    23: ("RULE", _u23, "unit 23: non-US team members in the US or Canada: purchase the counter liability (R9)"),
    24: ("RULE", _u24, "unit 24: do not purchase the CDW; Mexico: purchase the Mexico liability (R9)"),
    25: ("RULE", _u25, "unit 25: outside the US and Canada: purchase liability and the CDW (R9)"),
    26: ("RULE", _u26, "unit 26: GitLab does not purchase Foreign Corporate Hired Auto Physical Damage Coverage"),
    27: ("NOT", None, "other:norm", "unit 27: how Navan pays hotels (a system description, D1(e)); no question needs it "
         "beyond unit 28"),
    28: ("RULE", _u28, "unit 28: no extra charges, no expense report"),
    29: ("NOT", None, "other:norm", "unit 29: a duty to provide a card at check-in (no outcome a question can turn on)"),
    30: ("RULE", lambda ctx: _incidental(ctx, 30), "unit 30: incidentals within policy go through an expense report"),
    31: ("RULE", _u31, "unit 31: outside Navan: approval by Manager and AP Admin"),
    32: ("RULE", _u32, "unit 32: standard rooms up to $300 per night, 7 day lead time (R10, R13)"),
    33: ("PART", _u33, "other:judgment standard", "unit 33: over 20% of the Dynamic Policy flags (R5); 'really not "
         "applicable to that area' is a stated judgment: where stated (or not stated), unit 32's $300 cap is not applied "
         "(R23, in unit 32's rule); the amount then allowed is not stated"),
    34: ("RULE", _u34, "unit 34: refundable unless the only option (35's block exception)"),
    35: ("RULE", _u35, "unit 35: the block exception (pricing better than Navan)"),
    36: ("PART", _u36, "other:norm", "units 36-37: over $300 needs the AP team's exception; 'generally within the bounds' "
         "describes (no outcome)"),
    37: ("RULE", _nothing, "unit 37: personal card and Navan Expense (conditions of unit 36's rule)"),
    38: ("NOT", None, "other:norm", "unit 38: 'Always bring a credit card' a duty with no outcome; 'generally expect' "
         "describes"),
    39: ("RULE", _u39, "unit 39: dry cleaning over 5 days (nights, R13); room service as a meal"),
    40: ("RULE", _nothing, "unit 40: meals segregated and tagged (a condition of unit 39's room-service rule)"),
    41: ("RULE", _u41, "unit 41: parking segregated and tagged under Transportation; the day's parking and tolls within "
         "unit 72's $150 per day (R22)"),
    42: ("RULE", _u42, "unit 42: movies, mini bars not allowed as a claim"),
    43: ("RULE", _u43, "unit 43: Airbnb platform, the hotel's amount restriction"),
    44: ("RULE", _nothing, "unit 44: permitted if cheaper (stated judgment; R8, in unit 43's rule)"),
    45: ("RULE", _nothing, "unit 45: manual Lodging expense (a condition in unit 43's rule)"),
    46: ("RULE", _u46, "unit 46: self-stay host gift up to $50 (R10)"),
    47: ("RULE", _u47, "unit 47: meals up to $120 per day (R12)"),
    48: ("RULE", _group, "unit 48: separate billing; the most senior pays when not practicable"),
    49: ("NOT", None, "cross-reference", "unit 49: 'Refer to our Travel Handbook Page' (not pinned); the purpose sentence "
         "has no outcome"),
    50: ("RULE", _u50, "unit 50: tips up to 20%, included in the limit, US cash tips under $50 without receipt (R11)"),
    51: ("NOT", None, "other:norm", "unit 51: 'Please also add a description' a request with no outcome"),
    52: ("NOT", None, "other:norm", "unit 52: the purpose sentence has no outcome"),
    53: ("RULE", _group, "unit 53: as unit 48 for team events"),
    54: ("RULE", _u54, "unit 54: $80 limit per person per meal (R10, R11)"),
    55: ("RULE", _u50, "unit 55: as unit 50 for team events"),
    56: ("NOT", None, "other:norm", "unit 56: 'Please also add a description' a request with no outcome"),
    57: ("NOT", None, "other:product", "unit 57: mileage driven and calculated by Navan: the amount is miles x rate, a "
         "product of two stated quantities the language cannot write (R14)"),
    58: ("NOT", None, "definition by reference", "unit 58: 'according to local law' (the rates are not pinned)"),
    59: ("NOT", None, "other:norm", "unit 59: 'Should Show Start and End point' a duty with no outcome"),
    60: ("NOT", None, "other:norm", "unit 60: 'Please include a reason' a request with no outcome"),
    61: ("RULE", _u61, "unit 61: not both mileage and EV charging"),
    62: ("RULE", _u62, "unit 62: the entity's rate controls (R14)"),
    63: ("PART", _nothing, "other:product", "unit 63: the $.50 default and the update (in unit 62's rule); the amount at "
         "any rate is a product (R14)"),
    64: ("RULE", _u64, "unit 64: train over 20% of the Dynamic Policy flags (R5)"),
    65: ("RULE", _nothing, "unit 65: Navan trains paid by the GitLab travel card (a condition in unit 67's rule)"),
    66: ("RULE", _merge(_u66, _seg_minutes), "unit 66: standard cabin, 14 day lead time"),
    67: ("RULE", _u67, "unit 67: the frequent-train upgrade (R15)"),
    68: ("RULE", _u68, "unit 68: yearly or monthly rail discount cards not reimbursable"),
    69: ("RULE", _u69, "unit 69: ground transport to clients acceptable; not both fuel/EV and mileage"),
    70: ("RULE", _nothing, "unit 70: the description (a condition in units 71-72's rules)"),
    71: ("RULE", _u71, "unit 71: taxis $300 round trip, $150 single (R10)"),
    72: ("RULE", _u72, "unit 72: parking and tolls $150 per day (R10)"),
    73: ("RULE", _nothing, "unit 73: manager approval needed over a limit (in units 71-72's rules; never sufficient, R10)"),
    74: ("RULE", _u74, "unit 74: internal events follow their own guidelines: the guard 'not ievt' on every rule (R17; "
         "unit 75 keeps its own 'not intev')"),
    75: ("RULE", _u75, "unit 75: the work-related days, plus one before and after where stated (R13)"),
    76: ("RULE", _u76, "unit 76: internet up to $50 per day (R10)"),
    77: ("RULE", _nothing, "unit 77: trip details in the description (a condition in unit 76's rule)"),
    78: ("RULE", _nothing, "unit 78: nursing travel costs (the guard of unit 79's rule)"),
    79: ("RULE", _u79, "unit 79: the expensable nursing items (R8)"),
    80: ("RULE", _nothing, "unit 80: Navan can book personal trips (in unit 81's rule)"),
    81: ("RULE", _u81, "unit 81: a personal credit card at booking"),
    82: ("RULE", _u82, "unit 82: personal trips not on the GitLab invoice"),
}


def units_table(mutant=None):
    t = dict(UNITS)
    if mutant is not None:
        t = MUTANTS[mutant][1](t)
    return t


def rules(ctx, mutant=None):
    """Ground rules for a sub-case: [{"id", "unit", "formula", "defines"}]; a formula grounded by two units is kept once.
    Unit 74's guard (R17): while unit 74's builder carries it, every formula f becomes not ievt(p) -> f."""
    out, seen = [], set()
    t = units_table(mutant)
    guard = getattr(t[74][1], "guard74", False)
    for n, e in sorted(t.items()):
        if e[1] is None:
            continue
        for i, (f, target) in enumerate(e[1](ctx)):
            if guard:
                f = Implies(Not(pf("ievt")), f)
            kk = key([f, target])
            if kk in seen:
                continue
            seen.add(kk)
            out.append({"id": f"u{n}.{i}", "unit": n, "formula": f, "defines": [] if target is None else [target]})
    return out


# --- structure helpers --------------------------------------------------------------------------------------------

def q(formula):
    return {"format": "ve-quantity@1", "formula": formula}


def is_iff(f):
    return (type(f) is list and f and f[0] == "and" and type(f[1]) is list and type(f[2]) is list
            and f[1][:1] == ["implies"] and f[2][:1] == ["implies"] and f[1][1] == f[2][2] and f[1][2] == f[2][1])


def atoms_in(f, atoms, constants):
    if type(f) is not list or not f:
        return
    if f[0] in ("unary", "binary"):
        atoms.add(key(f))
        return
    if f[0] == "const" and len(f) == 3:
        constants.add(f[2])
        return
    for part in f[1:]:
        atoms_in(part, atoms, constants)


def environment(ctx, used=None):
    consts = {}
    for x, kind in ctx.items:
        consts[x] = {"sort": "item", "description": f"The case's {kind} {x}.", "verbalisation": f"{kind} {x}"}
    for name in sorted(used or ()):
        base, x = name.split("_", 1)
        u, w = BASES[base]
        consts[name] = {"sort": "$int", "unit": u, "description": f"{w[0].upper() + w[1:]} ({x}).",
                        "verbalisation": f"{w} ({x})"}
    preds = {n: {"arguments": ["item"], "description": d[0].upper() + d[1:] + "."} for n, d in {**FACTS, **DERIVED}.items()}
    return {"language": "ve.core@0.2", "profiles": ["documents@1", "order@0", "relational-fol@0", "time@0"],
            "spec_revision": "ve-v0.2-expand2-2026-09-25",
            "vocabulary": {"sorts": {"item": {"description": "A team member, booking, segment, trip, stay, expense item or day."}},
                           "predicates": preds, "constants": consts},
            "unit_schema": "ve-units@1",
            "units": {DAY: {"scale": "1", "display": {"kind": "iso_date"}},
                      NDAYS: {"scale": "1", "display": {"kind": "decimal", "label": "days"}},
                      MIN: {"scale": "1", "display": {"kind": "decimal", "label": "minutes"}},
                      CNT: {"scale": "1", "display": {"kind": "decimal", "label": "count"}},
                      RANK: {"scale": "1", "display": {"kind": "decimal", "label": "class position"}},
                      HCM: {"scale": "100", "display": {"kind": "decimal", "label": "cm"}},
                      INCH: {"scale": "1", "display": {"kind": "decimal", "label": "in"}},
                      USD: {"scale": "100", "display": {"kind": "money", "currency": "USD", "input_symbol": "$"}}}}


# --- planted errors (run.py --mutants): each must change the answer of at least one question ----------------------

def _swap(n, fn):
    def apply(t):
        t = dict(t)
        e = t[n]
        t[n] = (e[0], fn(e[1]), *e[2:])
        return t
    return apply


def _json_sub(a, b):
    return lambda builder: (lambda ctx: [(json.loads(json.dumps(f).replace(a, b)), tg) for f, tg in builder(ctx)])


def _drop(builder):
    return _nothing


_TIP25 = _json_sub('["scale", "usd_cent", "5", ["const", "usd_cent", "tcap_', '["scale", "usd_cent", "4", ["const", "usd_cent", "tcap_')
_NRC = _json_sub('["lt", ["const", "usd_cent", "amt_', '["le", ["const", "usd_cent", "amt_')


def _GRP(b):
    return lambda ctx: [(Implies(U("senior", tg_item(tg)), U("grp", tg_item(tg))) if f[2][0] == "unary" else f, tg)
                        for f, tg in b(ctx)]


def _set(n, builder):
    """A mutant that replaces unit n's builder."""
    def apply(t):
        t = dict(t)
        e = t[n]
        t[n] = (e[0], builder, *e[2:])
        return t
    return apply


def _appr_att(f):
    """planted error M25: unit 4's ph rules with appr read as the approval given AND attached."""
    if type(f) is not list or not f:
        return f
    if f[0] == "unary" and f[1] == "appr":
        return And(f, ["unary", "att", f[2]])
    return [f[0]] + [_appr_att(x) for x in f[1:]]


MUTANTS = {
    "M1": ("THRESHOLD: 'over 20% of the Dynamic Policy' read as at least 20% (flight, hotel, train)",
           lambda t: _swap(64, _json_sub('"lt", ["scale", "usd_cent", "6"', '"le", ["scale", "usd_cent", "6"'))(
               _swap(33, _json_sub('"lt", ["scale", "usd_cent", "6"', '"le", ["scale", "usd_cent", "6"'))(
                   _swap(3, _json_sub('"lt", ["scale", "usd_cent", "6"', '"le", ["scale", "usd_cent", "6"'))(t)))),
    "M2": ("DATE: the ideal domestic advance purchase 14 days read as 13", _swap(2, lambda b: (lambda ctx: [
        (f if tg is None or not tg.startswith("lth_") else shift(f[1], f[2], 13), tg) for f, tg in b(ctx)]))),
    "M3": ("DATE: the 24 hours of the automatic acceptance read as 48", _swap(16, lambda b: (lambda ctx: [
        (f if tg is None or not tg.startswith("ad_") else shift(f[1], f[2], 2), tg) for f, tg in b(ctx)]))),
    "M4": ("HEIGHT: 'over 6'5\"/2m' read as over 6'5\" alone (the 2 m threshold dropped, centimetres)",
           _swap(4, _json_sub('"length_cm", "200"', '"length_cm", "195.58"'))),
    "M5": ("DURATION: 'greater than 5 hours' with each segment 5+ read as at least 5 hours (domestic and international)",
           lambda t: _swap(6, _json_sub('["lt", ["decimal", "minute", "300"]', '["le", ["decimal", "minute", "300"]'))(
               _swap(5, _json_sub('["lt", ["decimal", "minute", "300"]', '["le", ["decimal", "minute", "300"]'))(t))),
    "M6": ("COUNT: frequent traveller '3 or more trips ... minimum 6 flight segments' read as 2 trips and 5 segments",
           _swap(7, lambda b: _json_sub('["decimal", "count", "6"]', '["decimal", "count", "5"]')(
               _json_sub('["decimal", "count", "3"]', '["decimal", "count", "2"]')(b)))),
    "M7": ("CONDITION: unit 7's listed purposes dropped (any purpose)", _swap(7, lambda b: (lambda ctx: [
        (Implies(f[1], Not(U("noreason", tg_item(tg)))) if tg and '"noreason"' in tg and f[2][0] == "unary" else f, tg)
        for f, tg in b(ctx)]))),
    "M8": ("AMOUNT: tips 20% read as 25% (a fourth of the bill)", lambda t: _swap(55, _TIP25)(_swap(50, _TIP25)(t))),
    "M9": ("AMOUNT: meals $120 per day read as $100", _swap(47, _json_sub('"usd_cent", "120.00"', '"usd_cent", "100.00"'))),
    "M10": ("THRESHOLD: dry cleaning 'over 5 days' read as at least 5", _swap(39, _json_sub(
        '["lt", ["decimal", "elapsed_day", "5"]', '["le", ["decimal", "elapsed_day", "5"]'))),
    "M11": ("AMOUNT: hotel cap $300 dropped (over it nothing is stated)", _swap(32, lambda b: (lambda ctx: [
        (f, tg) for f, tg in b(ctx) if not (tg and tg.startswith("rmb_") and '"lt"' in json.dumps(f))]))),
    "M12": ("CONDITION: unit 25 (outside the US and Canada) dropped", _swap(25, _drop)),
    "M13": ("DATE: unit 75's one day before and one day after dropped", _swap(75, _json_sub('"elapsed_day", "2"]',
                                                                                         '"elapsed_day", "0"]'))),
    "M14": ("CONDITION: Airbnb 'if it is cheaper than a hotel stay' dropped", _swap(43, lambda b: (lambda ctx: [
        (json.loads(json.dumps(f).replace(json.dumps(Not(U("cheaper", tg_item(tg)))), json.dumps(FALSE))
                    .replace(json.dumps(U("cheaper", tg_item(tg))), json.dumps(TRUE))) if tg else f, tg)
        for f, tg in b(ctx)]))),
    "M15": ("CONDITION: the milk-shipment-service condition on checking a bag dropped", _swap(79, _json_sub(
        '"svc"', '"svcfee"'))),
    "M16": ("CONDITION: the group-bill exception without 'not practicable'", lambda t: _swap(53, _GRP)(_swap(48, _GRP)(t))),
    "M17": ("AMOUNT: ground transport round trip $300 read as $350", _swap(71, _json_sub('"usd_cent", "300.00"',
                                                                                      '"usd_cent", "350.00"'))),
    "M18": ("AMOUNT: parking and tolls $150 per day read as $200", _swap(72, _json_sub('"usd_cent", "150.00"',
                                                                                     '"usd_cent", "200.00"'))),
    "M19": ("AMOUNT: host gift cap $50 read as $60", _swap(46, _json_sub('"usd_cent", "50.00"', '"usd_cent", "60.00"'))),
    "M20": ("COUNT: frequent train 'more than 3 train trips (6 segments)' read as more than 1 trip (4 segments)",
            _swap(67, lambda b: _json_sub('["decimal", "count", "6"]', '["decimal", "count", "4"]')(
                _json_sub('["decimal", "count", "3"]', '["decimal", "count", "1"]')(b)))),
    "M21": ("CONDITION: outside Navan, AP Admin's approval dropped (manager alone)", _swap(31, _json_sub('"apadm"',
                                                                                                       '"mgr"'))),
    "M22": ("THRESHOLD: US cash tips 'under $50' read as at most $50", lambda t: _swap(55, _NRC)(_swap(50, _NRC)(t))),
    "M23": ("AMOUNT: internet $50 per day cap dropped (over it nothing is stated)", _swap(76, lambda b: (lambda ctx: [
        (f, tg) for f, tg in b(ctx) if not (tg and tg.startswith("rmb_") and '"lt"' in json.dumps(f))]))),
    "M24": ("DATE: rental 7 day lead time read as 6", _swap(17, lambda b: (lambda ctx: [
        (f if tg is None or not tg.startswith("lsv_") else shift(f[1], f[2], 6), tg) for f, tg in b(ctx)]))),
    # M25-M45: each is the rule a reading R17-R29 replaced; killed by tests/test_gitlab_expenses_fidfix.py.
    "M25": ("EARLIER RULE U4: the height upgrade also needs the approval attached",
            _swap(4, lambda b: (lambda ctx: [(_appr_att(f) if tg and '"ph"' in tg else f, tg) for f, tg in b(ctx)]))),
    "M26": ("EARLIER RULE U4: a permission with no stated segments or trip list is dropped (class out of policy)",
            lambda t: _set(4, _merge(_u4, _seg_minutes, lambda ctx: _clsok(ctx, planted=True)))(
                _set(7, lambda ctx: _u7(ctx, planted_routes=True))(_set(5, lambda ctx: _dur_unit(ctx, False, True))(
                    _set(6, lambda ctx: _dur_unit(ctx, True, True))(t))))),
    "M27": ("EARLIER RULE U7: domestic trips' 8-hour segments count toward the 6", _set(7, lambda ctx: _u7(ctx, True))),
    "M28": ("EARLIER RULE U16: automatic acceptance after any flag (over 20%, outside Navan)",
            _set(16, lambda ctx: _u16(ctx, crit="flag"))),
    "M29": ("EARLIER RULE U16: automatic acceptance with no flight in the sub-case",
            _set(16, lambda ctx: _u16(ctx, need_flight=False))),
    "M30": ("EARLIER RULE U21: the fuel $300 limit per item, not per day", _set(21, lambda ctx: _u21(ctx, True))),
    "M31": ("EARLIER RULE U33: the $300 hotel cap whatever the stated applicability",
            _set(32, lambda ctx: _u32(ctx, notappl_guard=False))),
    "M32": ("EARLIER RULE U34: any room block is an exception to the refundable rule", _set(34, lambda ctx: _u34(ctx, True))),
    "M33": ("EARLIER RULE U36: the $300 hotel cap despite the AP team's block exception",
            _set(32, lambda ctx: _u32(ctx, block_exception=False))),
    "M34": ("EARLIER RULE U39: room service tested alone against $120", _set(39, lambda ctx: _u39(ctx, True))),
    "M35": ("EARLIER RULE U41: hotel parking tested alone against $150", _set(41, lambda ctx: _u41(ctx, True))),
    "M36": ("EARLIER RULE U67: a non-frequent traveller may not book standard class", _set(67, lambda ctx: _u67(ctx, True))),
    "M37": ("EARLIER RULE U74: the general policy answers for internal-event travel", _set(74, _nothing)),
    "M38": ("EARLIER RULE U76: the internet $50 cap per charge, not per day", _set(76, lambda ctx: _u76(ctx, True))),
    "M39": ("EARLIER RULE U7: a domestic flight is never permitted business class", _set(7, lambda ctx: _u7(ctx, planted_intl=True))),
    "M40": ("EARLIER RULE U7: any class other than business is refused the frequent-traveller permission",
            _set(7, lambda ctx: _u7(ctx, planted_bus=True))),
    "M41": ("EARLIER RULE U32: the hotel amount without the 7 day lead time", _set(32, lambda ctx: _u32(ctx, planted_lead=True))),
    "M42": ("EARLIER RULE U67: 'over 5 hours' read for the journeys only", _set(67, lambda ctx: _u67(ctx, planted_trip=True))),
    "M43": ("EARLIER RULE U7: a trip with no stated segments counts surely", _set(7, lambda ctx: _u7(ctx, planted_empty=True))),
    "M44": ("EARLIER RULE U67: a train trip with no stated journeys counts surely",
            _set(67, lambda ctx: _u67(ctx, planted_empty=True))),
    "M45": ("EARLIER RULE U32: a stay booked outside Navan reimbursed without unit 31's approvals",
            _set(32, lambda ctx: _u32(ctx, planted_outside=True))),
}


def tg_item(tg):
    """The item of an atom target key."""
    return json.loads(tg)[2][1]


def translation_sha256():
    import pathlib
    return hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()
