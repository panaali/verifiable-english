"""The encoder's cases, from questions-enc.jsonl ONLY (sha256 checked at import). CROSS-FAMILY questions, Opus encoder.

Encoder: dri-statute-corpus-wmf-nonpublic-access-w-1124 (Opus 5.5), after the translation was committed (3ddf4c44ed).
Each case: items by kind (translation.Ctx), "facts" {item: [true facts]} (C1: all others false), "ints" {day constant: day},
"bridge" {item: bridge input row} (dates of birth, disclosure days with the named holidays), "questions" [(qid, item, form)],
"judgement" (anything the encoder decided beyond copying a stated fact: listed as "encoder judgement").
Forms: translation.DERIVED_UNARY names read as yes/no; "chglim", "dl", "lat" read a day (run.VALUE); NOFORM: the question asks
something no rule of translation.py decides (a duty of the Foundation to list publicly, what the Foundation "will" do, whether
the Confidentiality Agreement must outline a subject): answered OPEN (refused), never forced into a nearby predicate.
The cases' convention "acts at 12:00 UTC, grants and candidacies at 14:00 UTC" puts every act of the grant day on or before
it: days compare exactly (an act on the grant's day counts as done by the grant). W013's 13:00 request is the same day.
PROBES: out-of-scope cases (every answer UNSUPPORTED, from the scope field). UNSUPPORTED (in scope): none.
REVISION 11-25 (dri-b4-policy-translation-revise-1125, after the translation revision 4ed67126d1 was committed): W014-2..W014-7
(the six subjects the Confidentiality Agreement outlines, asked of the grant test a1) map to the new R6 forms agconf, agwhen,
aguse, agdisc, agsafe, agrep instead of NOFORM. No other question's form changed; no encoder judgement added.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ENC_SHA256 = "b627d555584c250d574586dd29f92ee2682663193b70cbc90f7d7024eaeac70d"
if hashlib.sha256((HERE / "questions-enc.jsonl").read_bytes()).hexdigest() != ENC_SHA256:
    raise SystemExit("questions-enc.jsonl differs from the sealed encoder file")

NOFORM = "noform"
REQ = ["cert", "sub", "subvalid", "link", "linkvalid", "cs"]


def case(cid, qs, judgement=(), bridge=None, facts=None, ints=None, **items):
    return {"id": cid, "facts": facts or {}, "ints": ints or {}, "bridge": bridge or {}, **items,
            "questions": [{"qid": q, "item": x, "form": f} for (q, x, f) in qs], "judgement": list(judgement)}


def grant(cid, dob, day, qs, facts=REQ, more=(), less=(), days=None, ert=False, app=True, extra=None, judgement=()):
    """One test item a1 tested on `day` (the grant and the candidacy are on the same day in every case here)."""
    f = [x for x in facts if x not in less] + list(more) + (["ert"] if ert else [])
    acts = {"certd": day, "subd": day, "linkd": day, "csd": day, **(days or {})}
    ints = {f"{b}_a1": v for b, v in acts.items()}
    ints["at_a1"] = day
    if app:
        ints["app_a1"] = day
    allf, items = {"a1": f}, {"tests": ["a1"]}
    for kk, v in (extra or {}).items():
        if kk == "facts":
            allf.update(v)
        elif kk == "ints":
            ints.update(v)
        else:
            items[kk] = v
    return case(cid, qs, judgement, {"a1": {"kind": "age", "dob": dob}}, allf, ints, **items)


def yn(cid, *pairs):
    """(n, item, form) -> question ids."""
    return [(f"{cid}-{n}", x, f) for (n, x, f) in pairs]


def disc_bridge(*pairs, hol=("2026-09-07",)):
    return {d: {"kind": "b10", "day": day, "holidays": list(hol)} for d, day in pairs}


J_INFR = "the complaint is taken as one about an infringement of this Policy (the question's own framing: 'as an infringement')"
CASES = [
    # W001-W005: age edges on 10 July 2026 (grant and candidacy the same day; one test item answers both, R2)
    grant("W001", "2008-07-10", "2026-07-10", yn("W001", (1, "a1", "ok"), (2, "a1", "ok"), (3, "a1", NOFORM))),
    grant("W002", "2008-07-11", "2026-07-10", yn("W002", (1, "a1", "ok"), (2, "a1", "ok"))),
    grant("W003", "2008-07-09", "2026-07-10", yn("W003", (1, "a1", "ok"), (2, "a1", "ok"))),
    grant("W004", "2010-07-10", "2026-07-10", yn("W004", (1, "a1", "ok"), (2, "a1", "ok")), ert=True),
    grant("W005", "2010-07-11", "2026-07-10", yn("W005", (1, "a1", "ok"), (2, "a1", "ok")), ert=True),
    # W006 a 17-year-old email response team member applying for CheckUser; coverage through the VRTS grant
    grant("W006", "2009-07-10", "2026-07-10", yn("W006", (1, "a1", "ok"), (2, "m", "covered")),
          extra={"facts": {"m": ["granted", "tool"]}}),
    # W007 Legal-reviewed exemption for age and domicile
    grant("W007", "2009-07-10", "2026-07-10", yn("W007", (1, "a1", "ok"), (2, "a1", "ok"), (3, "a1", NOFORM)),
          more=("exm_age", "exm_dom", "blocked")),
    grant("W008", "2009-07-10", "2026-07-10", yn("W008", (1, "a1", "ok"), (2, "a1", "ok"))),
    grant("W009", "1990-06-12", "2026-07-10", yn("W009", (1, "a1", "ok"), (2, "a1", "ok")), less=("cert",)),
    grant("W010", "1990-06-12", "2026-07-10", yn("W010", (1, "a1", "ok"), (2, "a1", "ok")), less=("sub", "subvalid")),
    grant("W011", "1990-06-12", "2026-07-10", yn("W011", (1, "a1", "ok"), (2, "a1", "ok")), less=("link", "linkvalid")),
    grant("W012", "1990-06-12", "2026-07-10", yn("W012", (1, "a1", "ok"), (2, "a1", "ok")), ert=True,
          less=("subvalid", "linkvalid")),
    grant("W013", "1990-06-12", "2026-07-10", yn("W013", (1, "a1", "ok"), (2, "a1", "ok")), more=("vrq",),
          days={"vrqd": "2026-07-10"}),
    # W014 read but never certified the Confidentiality Agreement; questions 2-7 ask what the Agreement must outline
    grant("W014", "1990-06-12", "2026-07-10", yn("W014", (1, "a1", "ok"), *[(n, "a1", f) for n, f in zip(range(2, 8), (  # rev 11-25 (R6)
        "agconf", "agwhen", "aguse", "agdisc", "agsafe", "agrep"))]),
          less=("cs",)),
    # W015 community training criterion unmet (R2: undetermined when the Policy's own requirements are met)
    grant("W015", "1990-06-12", "2026-07-10", yn("W015", (1, "a1", "ok"), (2, "a1", "ok")), more=("crit_unmet",)),
    # W016 change 3 Aug, informed 10 Aug; Suppression grant 11 Aug; coverage through the CheckUser grant
    grant("W016", "1990-06-12", "2026-08-11", yn("W016", (1, "e1", "chglim"), (2, "a1", "ok"), (3, "m", "covered")),
          extra={"facts": {"e1": ["inf"], "m": ["granted", "tool"]}, "ints": {"chgd_e1": "2026-08-03", "infd_e1": "2026-08-10"},
                 "changes": ["e1"]}),
    # W017 change 3 Aug, first informed 11 Aug; complaint; CheckUser data while not revoked
    case("W017", yn("W017", (1, "e1", "chglim"), (2, "k1", "ombuds"), (3, "dat1", "destroy")), [f"W017-2: {J_INFR}"],
         facts={"e1": ["inf"], "k1": ["infr"]},
         ints={"chgd_e1": "2026-08-03", "infd_e1": "2026-08-11", "xask_dat1": "2026-08-12"},
         changes=["e1"], comps=["k1"], tools=["t1"], datas=["dat1"], **{"from": [("dat1", "t1")]}),
    # W018-W020 existing CheckUser holders (granted 1 Feb 2026; effective 1 Mar 2026), Suppression applications
    grant("W018", "1990-06-12", "2026-05-30", yn("W018", (1, "m", "dl"), (2, "a1", "ok"), (3, "dat1", "destroy")),
          days={"subd": "2026-02-01", "linkd": "2026-02-01"},
          extra={"facts": {"m": ["granted", "tool"]}, "ints": {"eff_m": "2026-03-01", "gd_m": "2026-02-01",
                                                               "xask_dat1": "2026-05-30"},
                 "tools": ["t1"], "datas": ["dat1"], "from": [("dat1", "t1")]}),
    grant("W019", "1990-06-12", "2026-06-01", yn("W019", (1, "m", "dl"), (2, "m", NOFORM), (3, "a1", "ok")),
          days={"subd": "2026-02-01", "linkd": "2026-02-01", "csd": "2026-05-31"},
          extra={"facts": {"m": ["granted", "tool"]}, "ints": {"eff_m": "2026-03-01", "gd_m": "2026-02-01"}}),
    grant("W020", "1990-06-12", "2026-05-31", yn("W020", (1, "m", "dl"), (2, "a1", "ok"), (3, "dat1", "destroy")),
          days={"subd": "2026-02-01", "linkd": "2026-02-01"},
          extra={"facts": {"m": ["granted", "tool", "ext"]},
                 "ints": {"eff_m": "2026-03-01", "gd_m": "2026-02-01", "extd_m": "2026-05-31", "xask_dat1": "2026-05-31"},
                 "tools": ["t1"], "datas": ["dat1"], "from": [("dat1", "t1")]}),
    # W021 granted on 2 March 2026 (after the effective day 1 March) without the Agreement (certified 10 March)
    grant("W021", "1990-06-12", "2026-03-02", yn("W021", (1, "a1", "ok"), (2, "m", "dl"), (3, "m", "covered")),
          days={"csd": "2026-03-10"},
          extra={"facts": {"m": ["granted", "tool"]}, "ints": {"eff_m": "2026-03-01", "gd_m": "2026-03-02"}}),
    # W022 volunteer developer: coverage, application information, two uses
    case("W022", yn("W022", (1, "m", "covered"), (2, "i1", "priv"), (3, "u1", "mayuse"), (4, "u2", "mayuse")),
         facts={"m": ["granted", "dev"], "i1": ["subapp"], "u1": ["pol"]}, infos=["i1"], uses=["u1", "u2"]),
    # W023 Suppression revoked 1 Aug; data from it and from a VRTS account (not revoked), asked 2 Aug
    case("W023", yn("W023", (1, "m", "covered"), (2, "dat1", "destroy"), (3, "dat2", "destroy")),
         facts={"m": ["granted", "supp", "tool"], "t1": ["rev"]},
         ints={"revd_t1": "2026-08-01", "xask_dat1": "2026-08-02", "xask_dat2": "2026-08-02"},
         tools=["t1", "t2"], datas=["dat1", "dat2"], **{"from": [("dat1", "t1"), ("dat2", "t2")]}),
    # W024 CheckUser: cross-wiki (local policy not applicable), Dutch-only (local policy refuses), cross-wiki non-compliant
    case("W024", yn("W024", (1, "u1", "mayuse"), (2, "u2", "mayuse"), (3, "u3", "mayuse")),
         facts={"u1": ["pol", "cu", "cross", "locbad"], "u2": ["pol", "cu", "locbad"], "u3": ["cu", "cross"]},
         uses=["u1", "u2", "u3"]),
    case("W025", yn("W025", (1, "m", "covered"), (2, "u1", "mayuse"), (3, "u2", "mayuse")),
         facts={"m": ["granted", "supp"], "u1": ["pol"]}, uses=["u1", "u2"]),
    # W026 disclosures to other community members (i)
    case("W026", yn("W026", (1, "d1", "maydisc"), (2, "d2", "maydisc"), (3, "d3", "maydisc")),
         facts={"d1": ["r_dcm", "duty", "disc"], "d2": ["r_dcm", "duty", "disc"], "d3": ["duty", "disc"]},
         ints={"dday_d1": "2026-08-01", "dday_d2": "2026-08-02", "dday_d3": "2026-08-03"}, discs=["d1", "d2", "d3"]),
    # W027 (ii) IP blocks / ISP complaint, 21 Sep 2026, Labour Day 7 Sep
    case("W027", yn("W027", (1, "d1", "lat"), (2, "d1", "needappr"), (3, "d1", "maydisc"), (4, "d2", "maydisc")),
         ["W027: an Internet service provider and a carrier taken as 'service providers, carriers' of (ii) (the recipients' "
          "kinds as named)"],
         disc_bridge(("d1", "2026-09-21"), ("d2", "2026-09-21")),
         facts={"d1": ["r_vendor", "ipblk", "sent", "appr", "apprst", "disc"],
                "d2": ["r_vendor", "ipblk", "sent", "appr", "apprst", "disc"]},
         ints={"dday_d1": "2026-09-21", "sentd_d1": "2026-09-04", "apprd_d1": "2026-09-04",
               "dday_d2": "2026-09-21", "sentd_d2": "2026-09-08", "apprd_d2": "2026-09-08"}, discs=["d1", "d2"]),
    # W028 (iv) authorized parties with the user's express permission
    case("W028", yn("W028", (1, "d1", "lat"), (2, "d1", "needappr"), (3, "d1", "maydisc"), (4, "d2", "maydisc")), (),
         disc_bridge(("d1", "2026-09-21"), ("d2", "2026-09-21")),
         facts={"d1": ["r_auth", "uperm", "sent", "appr", "apprst", "disc"],
                "d2": ["r_auth", "uperm", "sent", "appr", "apprst", "disc"]},
         ints={"dday_d1": "2026-09-21", "sentd_d1": "2026-09-04", "apprd_d1": "2026-09-04",
               "dday_d2": "2026-09-21", "sentd_d2": "2026-09-08", "apprd_d2": "2026-09-08"}, discs=["d1", "d2"]),
    # W029 required by law (administrative body, governmental agency) + a Legal exception subject to the approval rules
    case("W029", yn("W029", (1, "d1", "lat"), (2, "d1", "needappr"), (3, "d1", "maydisc"), (4, "d2", "maydisc")), (),
         disc_bridge(("d1", "2026-09-21"), ("d2", "2026-09-21")),
         facts={"d1": ["lawreq", "legexc", "sent", "appr", "apprst", "disc"],
                "d2": ["lawreq", "legexc", "sent", "appr", "apprst", "disc"]},
         ints={"dday_d1": "2026-09-21", "sentd_d1": "2026-09-04", "apprd_d1": "2026-09-04",
               "dday_d2": "2026-09-21", "sentd_d2": "2026-09-08", "apprd_d2": "2026-09-08"}, discs=["d1", "d2"]),
    # W030 emergency request, serious threat, disclosed at once
    case("W030", yn("W030", (1, "d1", "nopre"), (2, "d1", "emailnow"), (3, "d1", "obliged"), (4, "d1", "lat")), (),
         disc_bridge(("d1", "2026-08-01"), hol=()),
         facts={"d1": ["r_le", "threat", "lereq", "emerg", "disc"]}, ints={"dday_d1": "2026-08-01"}, discs=["d1"]),
    # W031 a threat of bodily harm that is not serious (d1); a serious-threat emergency request declined (d2)
    case("W031", yn("W031", (1, "d1", "nopre"), (2, "d2", "emailnow"), (3, "d2", "tolegal")),
         facts={"d1": ["r_le", "lereq", "emerg", "disc"], "d2": ["r_le", "threat", "lereq", "emerg"]},
         ints={"dday_d1": "2026-08-02", "dday_d2": "2026-08-03"}, discs=["d1", "d2"]),
    # W032 (v) public disclosure with a block
    case("W032", yn("W032", (1, "d1", "maydisc"), (2, "d2", "maydisc"), (3, "d1", "needappr")),
         facts={"d1": ["r_pub", "blk", "disc"], "d2": ["r_pub", "disc"]},
         ints={"dday_d1": "2026-08-04", "dday_d2": "2026-08-05"}, discs=["d1", "d2"]),
    # W033 (vi) a group exception; a complaint about an action under it
    case("W033", yn("W033", (1, "d1", "maydisc"), (2, "k1", "ombuds"), (3, "k1", "commgov"), (4, "k1", "wmfref"),
                    (5, "k1", NOFORM)),
         facts={"d1": ["legexc", "disc"], "k1": ["excact", "ppsec"]}, ints={"dday_d1": "2026-08-10"},
         discs=["d1"], comps=["k1"]),
    # W034 a journalist's request and a lawyer's subpoena (not required by law)
    case("W034", yn("W034", (1, "d1", "maydisc"), (2, "d1", "tolegal"), (3, "d2", "maydisc"), (4, "d2", "tolegal")),
         facts={"d1": [], "d2": ["subp"]}, discs=["d1", "d2"]),
    # W035 complaints: the late email notice (infringement), the meeting-note promise (outside the Policy)
    case("W035", yn("W035", (1, "k1", "ombuds"), (2, "k1", NOFORM), (3, "k1", NOFORM), (4, "k2", "commgov"),
                    (5, "k2", NOFORM)), [f"W035-1: {J_INFR}"],
         facts={"k1": ["infr"], "k2": ["outside"]}, comps=["k1", "k2"]),
]

PROBES, PROBE_QIDS = {}, {}
for _line in (HERE / "questions-enc.jsonl").read_text(encoding="utf-8").splitlines():
    _c = json.loads(_line)
    if _c["scope"] == "out":
        PROBES[_c["id"]] = "out of scope (the encoder file's scope field): " + _c["facts"][-160:]
        PROBE_QIDS[_c["id"]] = [q["qid"] for q in _c["questions"]]
UNSUPPORTED = {}


def check_coverage():
    """Every in-scope question of the encoder file has exactly one entry here."""
    want = []
    for line in (HERE / "questions-enc.jsonl").read_text(encoding="utf-8").splitlines():
        c = json.loads(line)
        if c["scope"] == "in":
            want += [q["qid"] for q in c["questions"]]
    got = [q["qid"] for c in CASES for q in c["questions"]]
    assert sorted(want) == sorted(got) and len(got) == len(set(got)), (set(want) ^ set(got))
    return len(got)


def write_bridge_inputs():
    rows = []
    for c in CASES:
        for item, r in c["bridge"].items():
            rows.append(json.dumps({"case": c["id"], "item": item, **r}, sort_keys=True))
    (HERE / "bridge" / "inputs.jsonl").write_text("".join(x + "\n" for x in rows), encoding="utf-8")
    return len(rows)


if __name__ == "__main__":
    print("in-scope questions", check_coverage(), "bridge rows", write_bridge_inputs(), "probes", len(PROBES))
