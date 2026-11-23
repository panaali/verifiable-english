"""Generate cases.py from questions-enc.jsonl ONLY (the encoder's file): a mechanical parse of the writer's fixed-form fact
sentences, with a completeness check per case (every sentence used, every week of the qualifying period given exactly
once). Anything the parse cannot read stops it. usage: python3 -I usecases/ei_canada/make_cases.py > usecases/ei_canada/cases.py
"""
import datetime as dt
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
MONTHS = {m: i for i, m in enumerate(["January", "February", "March", "April", "May", "June", "July", "August",
                                      "September", "October", "November", "December"], 1)}
MONEY = r"\$([\d,]+\.\d\d)"


def money(s):
    return s.replace(",", "")


def parse(c):
    facts = c["facts"]
    sents = re.split(r"(?<=\.) (?=[A-Z])", facts)
    used = [False] * len(sents)
    out = {"id": c["id"], "seps": [], "myie": None, "halfup": False, "insured": None, "interruption": None, "judgement": []}

    def take(rx, fn):
        hit = 0
        for i, s in enumerate(sents):
            m = re.fullmatch(rx, s)
            if m:
                fn(m)
                used[i] = True
                hit += 1
        return hit
    assert take(r"(\w+) is an insured person who has made an initial claim for regular benefits\.",
                lambda m: out.update(name=m.group(1), insured=True)) == 1
    assert take(r"If a benefit period is established for \w+, it would begin on (\d+) (\w+) (\d{4})\.",
                lambda m: out.update(bpstart=dt.date(int(m.group(3)), MONTHS[m.group(2)], int(m.group(1))).isoformat())) == 1
    assert take(r"The regional rate of unemployment that applies to \w+ is (\d+\.\d)%\.", lambda m: out.update(rate=m.group(1))) == 1
    assert take(r"\w+ had ([\d,]+) hours of insurable employment in the qualifying period\.",
                lambda m: out.update(hours=int(m.group(1).replace(",", "")))) == 1
    assert take(r"\w+ has (not )?had an interruption of earnings from employment\.",
                lambda m: out.update(interruption=m.group(1) is None)) == 1

    def weeks(m):
        n = int(m.group(1))
        wk = [None] * n
        for seg in m.group(2).split("; "):
            a = re.fullmatch(r"weeks (\d+) to (\d+): " + MONEY + " each", seg)
            b = re.fullmatch(r"week (\d+): " + MONEY, seg)
            if a:
                lo, hi, v = int(a.group(1)), int(a.group(2)), money(a.group(3))
            elif b:
                lo = hi = int(b.group(1))
                v = money(b.group(2))
            else:
                raise ValueError(f"{c['id']}: week segment {seg!r}")
            for i in range(lo, hi + 1):
                assert wk[i - 1] is None, (c["id"], i)
                wk[i - 1] = v
        assert all(x is not None for x in wk), (c["id"], "weeks not all given")
        out["weeks"] = wk
    assert take(r"\w+'s insurable earnings in each week of the (\d+)-week qualifying period, not including any amount paid or "
                r"payable by reason of lay-off or separation from employment: (.*)\.", weeks) == 1

    def seps(m):
        for seg in re.split(r", | and |; ", m.group(1)):
            s = re.fullmatch(MONEY + r" in week (\d+)", seg)
            if not s:
                raise ValueError(f"{c['id']}: separation segment {seg!r}")
            out["seps"].append(money(s.group(1)))
            out["judgement"].append(f"lay-off/separation amount ${money(s.group(1))} in week {s.group(2)}: an item of "
                                    f"s. 14(3)(b); its week is not used (s. 14(4) ranks the stated weekly earnings)")
    n_none = take(r"No insurable earnings were paid or payable to \w+ during the qualifying period by reason of lay-off or "
                  r"separation from employment\.", lambda m: None)
    n_some = take(r"Insurable earnings paid or payable to \w+ during the qualifying period by reason of lay-off or "
                  r"separation from employment: (.*)\.", seps)
    assert n_none + n_some == 1, c["id"]
    assert take(r"The maximum yearly insurable earnings for (\d{4}) are " + MONEY + r"\.",
                lambda m: out.update(myie=money(m.group(2)), myie_year=m.group(1))) <= 1
    take(r"For this test, the maximum weekly insurable earnings in s\. 14\(1\.1\) caps the claimant's weekly insurable "
         r"earnings\.", lambda m: out.update(b5_stated=True))
    rest = [s for s, u in zip(sents, used) if not u]
    if rest:
        raise ValueError(f"{c['id']}: unread fact sentences {rest}")
    if out["myie"] is not None:
        assert out["myie_year"] == out["bpstart"][:4], (c["id"], "MYIE year differs from the benefit period's year")
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
    enc = [json.loads(line) for line in open(HERE / "questions-enc.jsonl", encoding="utf-8") if line.strip()]
    cases, probes, probe_qids = [], {}, {}
    for c in enc:
        if c["scope"] == "in":
            cases.append(parse(c))
        else:
            probes[c["id"]] = "out of scope (writer's probe): " + c["facts"][:160]
            probe_qids[c["id"]] = [q["qid"] for q in c["questions"]]
    print('"""The encoder\'s cases, GENERATED by make_cases.py from questions-enc.jsonl only (do not edit by hand)."""')
    print("CASES = " + json.dumps(cases, indent=1, ensure_ascii=False).replace("true", "True").replace("false", "False")
          .replace("null", "None"))
    print("PROBES = " + json.dumps(probes, indent=1, ensure_ascii=False))
    print("PROBE_QIDS = " + json.dumps(probe_qids, indent=1))
    print("UNSUPPORTED = {}")
    print(f"# {len(cases)} in-scope cases, {sum(len(c['questions']) for c in cases)} questions; {len(probes)} probes",
          file=sys.stderr)


if __name__ == "__main__":
    main()
