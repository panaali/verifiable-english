"""Build out/cases_xfam.py from questions-enc.jsonl: a transcription of this writer's fact sentences into the record
format of make_cases.py's parse(). Every sentence must be read (or listed as carrying no field) or the build stops.
usage (in /work): python3 -I out/build.py > out/cases_xfam.py"""
import datetime as dt
import json
import os
import pprint
import re

W = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MONTHS = {m: i for i, m in enumerate(["January", "February", "March", "April", "May", "June", "July", "August",
                                      "September", "October", "November", "December"], 1)}
MONEY = r"\$([\d,]+\.\d\d)"
EARN = ("The insurable earnings received in each of those weeks, excluding all amounts paid or payable by reason of "
        "lay-off or separation from employment, are: (.*)\\.")
NOSEP = ("No insurable earnings were paid or payable during the qualifying period by reason of lay-off or separation "
         "from employment\\.")
SEP = ("Separately, the following insurable earnings were paid or payable during the qualifying period by reason of "
       "lay-off or separation from employment: (.*)\\.")
B5 = "For this test, the maximum weekly insurable earnings in s\\. 14\\(1\\.1\\) caps the claimant's weekly insurable earnings\\."


PROBE_NEEDS = {  # out-of-scope case -> what it needs (one line)
    "E048": "needs special benefits (pregnancy, parental incl. the 33% rate, sickness, caregiving) and their combination with "
            "regular benefits, outside s. 7, s. 12(1)-(2) and s. 14(1)-(4)",
    "E049": "needs the seasonal-claimant additional weeks of s. 12(2.3) and Schedule VI regions",
    "E050": "needs the Employment Insurance (Fishing) Regulations",
    "E051": "needs the temporary rules for a benefit period beginning in September 2020 (not in the translated text)",
    "E052": "needs the violation rule of s. 7.1",
    "E053": "needs the s. 7(6) joint determination with the United States",
    "E054": "needs the law for a benefit period beginning before 1997 (s. 14(1.1)(a) begins with 1997)",
    "E055": "needs the self-employed provisions (Part VII.1)",
    "E056": "needs the regional rate and the hours of insurable employment, which are not stated",
    "E057": "needs the qualifying period and its weekly insurable earnings, which are not stated",
}


def money(s):
    return s.replace(",", "")


def parse(c):
    sents = re.split(r"(?<=\.) (?=[A-Z])", c["facts"])
    used = [False] * len(sents)
    out = {"id": c["id"], "seps": [], "myie": None, "myie_year": None, "halfup": False, "insured": True,
           "interruption": None, "b5_stated": False, "judgement": []}
    noncontig = []

    def take(rx, fn):
        hit = 0
        for i, s in enumerate(sents):
            m = re.fullmatch(rx, s)
            if m:
                fn(m)
                used[i] = True
                hit += 1
        return hit
    assert take(r"(\w+) is the claimant\.", lambda m: out.update(name=m.group(1))) == 1, c["id"]
    assert take(r"The applicable regional rate of unemployment is (\d+\.\d)%\.", lambda m: out.update(rate=m.group(1))) == 1
    assert take(r"\w+ has ([\d,]+) hours of insurable employment in the qualifying period\.",
                lambda m: out.update(hours=int(m.group(1).replace(",", "")))) == 1
    assert take(r"\w+ has (not )?had an interruption of earnings from employment\.",
                lambda m: out.update(interruption=m.group(1) is None)) == 1
    assert take(r"The benefit period would begin on (\d+) (\w+) (\d{4})\.",
                lambda m: out.update(bpstart=dt.date(int(m.group(3)), MONTHS[m.group(2)], int(m.group(1))).isoformat())) == 1
    nweeks = []
    assert take(r"The qualifying period has (\d+) weeks\.", lambda m: nweeks.append(int(m.group(1)))) == 1
    n = nweeks[0]

    def weeks(m):
        wk = [None] * n
        out["runs"] = []
        for seg in m.group(1).split("; "):
            a = re.fullmatch(r"weeks? ([\d, to]+): " + MONEY + "( each)?", seg)
            if not a:
                raise ValueError(f"{c['id']}: week segment {seg!r}")
            v = money(a.group(2))
            parts = a.group(1).split(", ")
            if len(parts) > 1:
                noncontig.append(f"weeks {a.group(1)}: ${v} each")
            for p in parts:
                r = re.fullmatch(r"(\d+)(?: to (\d+))?", p)
                lo = int(r.group(1))
                hi = int(r.group(2) or lo)
                out["runs"].append([lo, hi])
                for i in range(lo, hi + 1):
                    assert wk[i - 1] is None, (c["id"], i)
                    wk[i - 1] = v
        assert all(x is not None for x in wk), (c["id"], "weeks not all given")
        out["weeks"] = wk
    assert take(EARN, weeks) == 1, c["id"]

    def seps(m):
        for seg in m.group(1).split("; "):
            s = re.fullmatch(r"week (\d+): " + MONEY + r" (paid|payable) by reason of (lay-off|separation from employment)",
                             seg)
            if not s:
                raise ValueError(f"{c['id']}: separation segment {seg!r}")
            out["seps"].append(money(s.group(2)))
            out["judgement"].append(f"${money(s.group(2))} {s.group(3)} by reason of {s.group(4)} (week {s.group(1)}): one "
                                    f"s. 14(3)(b) item; its week and paid/payable are not encoded")
    n_none = take(NOSEP, lambda m: None)
    n_some = take(SEP, seps)
    assert n_none + n_some == 1, c["id"]
    assert take(r"There are no other such amounts\.", lambda m: None) == n_some, c["id"]
    assert take(r"The maximum yearly insurable earnings for (\d{4}) are " + MONEY + r"\.",
                lambda m: out.update(myie=money(m.group(2)), myie_year=m.group(1))) <= 1
    take(B5, lambda m: out.update(b5_stated=True))
    take(r"All money is in Canadian dollars\.", lambda m: None)
    if take(r"The weekly earnings listed above came from insurable employment that has not ended\.", lambda m: None):
        out["judgement"].append("'the weekly earnings came from insurable employment that has not ended': no field; "
                                "not encoded (the interruption is encoded as stated)")
    rest = [s for s, u in zip(sents, used) if not u]
    if rest:
        raise ValueError(f"{c['id']}: unread fact sentences {rest}")
    if out["myie"] is not None:
        assert out["myie_year"] == out["bpstart"][:4], (c["id"], "MYIE year differs from the benefit period's year")
    if noncontig:
        out["judgement"].append("weeks stated as comma lists: each listed week or 'a to b' range is one run of its own")
    qs = []
    for q in c["questions"]:
        form = {"Q1": "qualify", "Q2": "maxweeks", "Q3": "rate"}[q["kind"]]
        if q["kind"] == "Q3":
            if "rounding half a cent up" in q["text"]:
                out["halfup"] = True
            else:
                assert "no rounding rule applies" in q["text"], q["qid"]
        qs.append({"qid": q["qid"], "form": form})
    out["questions"] = qs
    return out


def main():
    enc = [json.loads(line) for line in open(os.path.join(W, "questions-enc.jsonl"), encoding="utf-8") if line.strip()]
    cases, probes, probe_qids = [], {}, {}
    for c in enc:
        if c["scope"] == "in":
            cases.append(parse(c))
        else:
            probes[c["id"]] = PROBE_NEEDS[c["id"]]
            probe_qids[c["id"]] = [q["qid"] for q in c["questions"]]
    print('"""The encoder\'s cases, built by out/build.py from questions-enc.jsonl only (facts as stated; see '
          'ENCODER-NOTES.md)."""')
    print("CASES = " + pprint.pformat(cases, width=120, sort_dicts=False))
    print("PROBES = " + pprint.pformat(probes, width=120, sort_dicts=False))
    print("PROBE_QIDS = " + pprint.pformat(probe_qids, width=120, sort_dicts=False))
    print("UNSUPPORTED = {}")


if __name__ == "__main__":
    main()
