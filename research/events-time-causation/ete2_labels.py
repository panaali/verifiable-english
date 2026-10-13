"""ET-E2: the hand classification of every candidate (phase-1 doc 1.3), and the tally against the bar.

Each candidate number of `candidates.json` gets exactly one label: O (offset over an event), D (fulfilment by a
deadline; sub-label D-event or D-duration) or N, with a reason category for N. The labels were written by reading
each candidate sentence; the tally refuses to run if any candidate is unlabelled or labelled twice.

Usage: python3 ete2_labels.py <candidates.json> <out-labels.json> <out-tally.json>
"""
import json
import sys
from pathlib import Path


def rng(a, b):
    return list(range(a, b + 1))


O = {30: "over the age of 18: an age (18 years from each user's birth)",
     103: "the age of 65 years", 104: "the age of 60", 111: "the age of 66",
     112: "the age shown in table 3 (66 years and n months)",
     **{n: "a table 3 cell of candidate 112 (66 years and n months)" for n in rng(115, 125)},
     126: "month-end convention for a 66-years-and-4-months offset", 127: "the same, 9 months",
     128: "the same, 10 months", 129: "the age of 67", 133: "the age of 68", 150: "the age of 16",
     157: "substituted text: to the age of 65 (men) and 60 (women)", 159: "substituted text: 65 and 60",
     170: "the age of 65 and the age of 60", 185: "in-patient treatment for not less than 52 weeks",
     186: "the same for both partners", 187: "the day after the day of entry (a one-day offset)",
     192: "a period of at least 12 weeks ending immediately before the qualifying week",
     **{n: "reached (or not) the age of 80" for n in rng(195, 203)},
     205: "more than 52 weeks ending immediately before the qualifying week",
     **{n: "reached (or not) the age of 80" for n in rng(212, 217)},
     219: "treatment for more than 52 weeks", 220: "residential care for the preceding 12 weeks",
     224: "zero degrees or below for 7 days in a row (another benefit, named in the guidance)"}

D = {80: ("D-event", "u0204.s03: raise concerns before undertaking a task (soft: 'should ideally')"),
     207: ("D-event", "no claim on or before 31 March following the qualifying week: a claim deadline as a "
                      "condition of entitlement (a norm's effect, not an obligation)"),
     221: ("D-event", "the same claim deadline, in the explanatory note"),
     240: ("D-event", "the deadline to make a claim is 31 March 2027"),
     246: ("D-event", "you need to contact them before 31 March 2027"),
     247: ("D-event", "F2: a critical capability assessment prior to the first external deployment"),
     250: ("D-duration", "F18: reviewed at least once a year (fulfilment within each period)"),
     255: ("D-event", "README's restatement of F2"),
     260: ("D-duration", "README's restatement of F18"),
     265: ("D-duration", "README's remark on when F18's first review falls")}

N = {
    "non-temporal": [0, 1, 3, 4, 9, 10, 11, 12, 13, 15, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
                     *rng(33, 46), 48, 50, 51, *rng(53, 69), 70, 71, 72, 73, 75, 79, 81, 83, 84, 86, 89, 90, 91, 93,
                     97, 98, 99, 101, 102, 136, 144, 145, 148, 152, 171, 173, 176, 183, 189, 190, 210, 223, 227, 229,
                     236, 237, 242, 251, 252, 257, 261, 268],
    "order-only (before, after, until, during, once an event; no distance and no deadline obligation)":
        [2, 6, 17, 32, 47, 52, 74, 76, 77, 78, 85, 87, 92, 94, 96, 135, 138, 139, 140, 188, 209, 238, 239, 244,
         245, 248, 256, 263],
    "no stated amount (an age or a period the text does not quantify)": [5, 31],
    "vague period ('the current period', 'during training')": [14, 16, 18, 49, 82, 88, 95],
    "vague recurrence ('periodic', no stated amount)": [7, 8, 249, 258, 259, 262, 266],
    "named dates or a named window only": [105, 108, 130, 146, 147, 153, 167, 172, 174, 175, 177, 178, 179, 180,
                                           181, 182, 184, 194, 206, 208, 222, 225, 226, 228, *rng(230, 235), 241,
                                           243],
    "table header": [106, 107, 109, 110, 113, 114, 131, 132],
    "defined term only (pensionable age; its offsets are counted where stated)":
        [134, 137, 141, 142, 143, 151, 154, 155, 156, 158, *rng(160, 166), 168, 169, 191, 193, 204, 211, 218],
    "a count of tax years (a quantity, not compared with an amount)": [149],
    "about the project, not the source": [100, 253, 254, 264, 267, 269],
}


def main(candidates, out_labels, out_tally):
    rows = json.loads(Path(candidates).read_text())
    labels = {}
    for n, note in O.items():
        labels.setdefault(n, []).append({"label": "O", "note": note})
    for n, (sub, note) in D.items():
        labels.setdefault(n, []).append({"label": "D", "sub": sub, "note": note})
    for reason, ns in N.items():
        for n in ns:
            labels.setdefault(n, []).append({"label": "N", "reason": reason})
    missing = [r["n"] for r in rows if r["n"] not in labels]
    twice = [n for n, v in labels.items() if len(v) != 1]
    extra = sorted(set(labels) - {r["n"] for r in rows})
    if missing or twice or extra:
        raise SystemExit(f"unlabelled {missing}, labelled twice {twice}, unknown {extra}")
    out = [{**r, **labels[r["n"]][0]} for r in rows]
    Path(out_labels).write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    hits = [r for r in out if r["label"] in ("O", "D")]
    pilot_units = sorted({u for r in hits if r["corpus"].startswith("pilot:") for u in r["units"]})
    use_cases = sorted({r["corpus"].split(":", 1)[1] for r in hits if r["corpus"].startswith("usecase:")})
    by = {}
    for r in out:
        key = f'{r["corpus"]} {r["label"]}' + (f' {r["sub"]}' if r.get("sub") else "")
        by[key] = by.get(key, 0) + 1
    tally = {"candidates": len(out), "by_corpus_and_label": dict(sorted(by.items())),
             "pilot_units_O_or_D": pilot_units, "pilot_unit_count": len(pilot_units),
             "use_cases_O_or_D": use_cases, "use_case_count": len(use_cases),
             "bar": "pilot units >= 5 or answer-key use cases >= 2",
             "bar_met": len(pilot_units) >= 5 or len(use_cases) >= 2}
    Path(out_tally).write_text(json.dumps(tally, indent=1) + "\n")
    print(json.dumps(tally, indent=1))


if __name__ == "__main__":
    main(*sys.argv[1:])
