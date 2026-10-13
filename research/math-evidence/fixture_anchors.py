"""ME-0, P4: re-anchor the plan's fixtures (section 4) to byte spans of the pinned sources and repository files.

For each fixture: the file, the needles (words or numbers the fixture quotes or uses), their byte spans (searched with
runs of whitespace treated as one space), the outcome in the pre-registered categories (ANCHORED, RE-WORDED, CHANGED,
ABSENT, NOT A QUOTE) and the reason. The outcome is a reading of the spans, written here before the bar is computed;
the script fails if a needle claimed present is missing. Also writes exact-arithmetic pre-checks of fixture numbers
(Python `fractions`, for ME-S's `#eval`; these are not VE verdicts).

    python3 -I research/math-evidence/fixture_anchors.py
"""
from __future__ import annotations

import hashlib
import json
import re
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EV = ROOT / "docs/research/evidence/math-evidence"
PILOTS = Path("/home/seyran/code/manage-agents/pilots")
H = EV / "physics-michelson-morley/source.txt"
M = EV / "math-ramanujan-bertrand/source.txt"
V = EV / "ve-paper-e1/source-04-e1.md"
A = EV / "ve-paper-e1/source-appendix-per-template.md"

FIXTURES = [
    ("H-1", H, ["Then ${T=\\frac{D}{V-v}}$, ${T_{/}=\\frac{D}{V+v}}$.",
                "The whole time of going and coming is ${T+T_{/}=2D \\frac{V}{V^2-v^2}}$"],
     "RE-WORDED", "Same equations as TeX; the source writes T-sub-slash for T1 and 2D V/(V^2 - v^2)."),
    ("H-2", H, ["the distance traveled in this time is ${2D \\frac{V^2}{V^2-v^2}=2D \\left(1+\\frac{v^2}{V^2}\\right)}$",
                "neglecting terms of the fourth order"],
     "RE-WORDED", "Same equation; the source's line break is inside the sentence."),
    ("H-3", H, ["or to the same degree of accuracy, ${2D \\left( 1+\\frac{v^2}{2V^2}\\right)}$",
                "The difference is therefore ${D\\frac{v^2}{V^2}}$."],
     "RE-WORDED", "Same equation. The Wikisource TeX of the preceding square root is unbalanced "
                  "(`\\sqrt{(1+\\frac{v^2}{V^2}}`), a transcription defect outside the case."),
    ("H-4", H, ["hence the displacement of the interference fringes should be ${2D \\frac{v^2}{V^2}}$",
                "Considering only the velocity of the earth in its orbit, this would be ${2D \\times 10^{-8}}$."],
     "CHANGED", "The case takes 'v/V = 10^-4 stated'; the source states no v/V. It gives v^2/V^2 = 10^-8 only "
                "through '2D x 10^-8' (twice: h049, h113). The case's premise must be v^2/V^2 = 10^-8, read from "
                "those spans, or an external premise with its own support."),
    ("H-5", H, ["2×10^7 wave-lengths of yellow light; hence the displacement to be expected was 0•4 fringe"],
     "CHANGED", "The case computes 2 x (2x10^7) x (10^-4)^2 = 0.4, so it uses H-4's premise v/V = 10^-4, which the "
                "source never states (see H-4). The result 0.4 is the source's ('0•4', the decimal point a bullet), "
                "but the source reaches it through v^2/V^2 = 10^-8 ('2D x 10^-8', h113): 2 x 2x10^7 x 10^-8 = 0.4. "
                "The source also has the 1881 version (h050): D = 2x10^6 gives 0.04, a further fixture."),
    ("H-6", H, ["The actual displacement was certainly less than the twentieth part of this",
                "But since the displacement is proportional to the square of the velocity",
                "and certainly less than one-fourth"],
     "ANCHORED", "Premises and claim are in h115-h116 in these words."),
    ("H-6p", H, ["and probably less than the fortieth part",
                 "is probably less than one sixth the earth's orbital velocity"],
     "ANCHORED", "In these words."),
    ("H-6n", H, [], "NOT A QUOTE", "A negative control the plan constructs."),
    ("H-7", H, ["T=time light occupies to pass from a to c.", "D=distance ab or ac, fig. 1."],
     "RE-WORDED", "D (a length) and T (a time) are defined by the source; D/(V - v), D/lambda and D + T are the "
                  "case's expressions."),
    ("H-8", H, ["The distance D was about eleven meters, or 2×10^7 wave-lengths of yellow light"],
     "ANCHORED", "In these words ('2×10^7' renders the superscript). The wavelength is an external premise, as the "
                 "case says."),
    ("H-9", H, ["The following tables give the means of the six readings",
                "Mean | 43.1 | 41.6", "Mean in w. l. | .862", "Final mean | .784"],
     "CHANGED", "The table is not 'readings at 16 azimuths per session': each cell is already the mean of six "
                "readings (the readings themselves are not printed), there are 17 columns (mark 16 at the start and "
                "end of a turn), three sessions per table, and three derived rows (Mean, Mean in w. l., Final mean) "
                "plus a repeated half row. Today's W6a certifies the Mean and Final mean rows (section 3 of the "
                "results); only 'Mean in w. l.' needs a unit change."),
    ("H-10", H, ["July 8 | 44.7", "July 11 | 27.3", "July 12 | 66.8", "November 1887"],
     "RE-WORDED", "The dates are row labels without a year; 1887 comes from the publication line. The case's "
                  "'1887' is inferred, not printed beside the dates."),
    ("M-1", M, ["Thus Bertrand’s Postulate is proved for all values of x, not less than 162: and, \n"
                "by actual verification, we find that it is true for smaller values."],
     "RE-WORDED", "The case is the whole-number reading of the source's real x (M-3r)."),
    ("M-2", M, [], "NOT A QUOTE", "The plan marks it 'not Ramanujan's wording'."),
    ("M-3", M, ["truth of which was conjectured by Bertrand: namely that there is at least \none prime"],
     "RE-WORDED", "The statement's formula is OCR-garbled in both scans ('®<ps;2®, if ®>1'; 'æ< p«2z, if z 21'): "
                  "x < p <= 2x if x >= 1, read from the scan, not from the OCR bytes."),
    ("M-3r", M, ["where [®] denotes as usual the greatest integer in ®."],
     "RE-WORDED", "The source's x is real (it takes the integer part of x)."),
    ("M-4", M, ["> 1, 2, 3, 4,5,..., if * » 2, 11, 17, 29, 41"],
     "RE-WORDED", "Formula (18): pi(x) - pi(x/2) >= 1, 2, 3, 4, 5 for x >= 2, 11, 17, 29, 41. The symbols are "
                  "OCR-garbled, so the case's words are not in the pinned bytes; its numbers are (intact). The case "
                  "uses the second pair (2 at 11); the other four pairs are further fixtures."),
    ("M-4x", M, [], "NOT A QUOTE", "A constructed budget fixture."),
    ("M-5", M, [], "NOT A QUOTE", "A constructed negative control."),
    ("V-1", V, ["Its scored baseline, 176/594 = .296, is outside the gate band", "30--60% gate"],
     "ANCHORED", "Exact words; the source breaks the line after '.296,'."),
    ("V-1n", V, [], "NOT A QUOTE", "Constructed (0.297)."),
    ("V-2", V, ["false approval is 52/243 (.214) versus 31/243 (.128), an 8.6-point pooled increase"],
     "ANCHORED", "Exact words across a line break."),
    ("V-3", ROOT / "paper/sections/05-e4.md",
     ["For 7B, prose rejects 56/60 valid inferences; checked feedback increases HA from 4/60 to 52/60"],
     "ANCHORED", "Exact words (outside ME-0's pinned E1 slice; anchored in the repository file)."),
    ("V-4", V, ["The 32B symbolic/no-explanation baseline was 34/110 false approvals, only one candidate inside "
                "the primary 30--60% gate"], "ANCHORED", "Exact words."),
    ("V-5", ROOT / "paper/generated/posthoc-weakening-rates.md",
     ["| 151/243 | 0.621 |", "| 155/243 | 0.638 |", "| 136/243 | 0.560 |", "| 90/243 | 0.370 |",
      "| 43/243 | 0.177 |", "| 37/243 | 0.152 |"], "ANCHORED", "The six example rows of the 20."),
    ("V-6", A, ["t01: -0.100, t02: -0.133, t05: +0.094, t06: -0.192, t07: +0.021, t08: +0.086, t09: -0.057, "
                "t10: +0.000, t11: +0.061, t12: -0.050, t15: -0.246, t16: -0.029 | 0.108 | 0.031 | 0.081 |"],
     "ANCHORED", "Row '14B AWQ | P1 attacker'."),
    ("V-6r", A, [], "NOT A QUOTE", "The population reading the case constructs."),
    ("V-7", ROOT / "paper/generated/posthoc-weakening-contrasts.md",
     ["| 0.812500 |", "| 0.085938 |", "| 0.687500 |", "| 0.679688 |", "| 0.359375 |", "| 0.125000 |",
      "| 0.875000 |"], "ANCHORED", "Seven of the eight rows; the eighth is V-8."),
    ("V-8", ROOT / "paper/generated/posthoc-weakening-contrasts.md", ["| 14B | F - S | attacker | -0.180 | "
                                                                      "[-0.312, -0.055] | 0.007812 |"],
     "ANCHORED", "Row '14B F - S attacker'."),
    ("V-9", V, [], "NOT A QUOTE", "Constructed software-convention fixture."),
    ("V-10", V, [], "NOT A QUOTE", "Constructed software-convention fixture."),
    ("V-11", V, [], "NOT A QUOTE", "Constructed limit fixture."),
    ("V-12", V, [".296,"], "RE-WORDED", "Constructed over the real span '.296' of V-1."),
    ("D-1", ROOT / "ROADMAP.md", ["Math mini paper: **17/19** current verified outcomes (15 tableau certificates "
                                  "plus T9 and T9e by closure induction)"], "ANCHORED", "Exact words."),
    ("D-2", PILOTS / "udhr/run-20261012T1800Z/SUMMARY.md", ["claimed covered bytes 4,792 (43.90%",
                                                             "all 10,916 bytes accounted"],
     "ANCHORED", "Exact words in the pinned pilot summary."),
    ("D-3", PILOTS / "claude-constitution/run-20261012T1800Z/SUMMARY.md",
     ["Claimed coverage is unchanged at 2,951 bytes (1.60%)"], "ANCHORED",
     "Exact words; coverage.json gives CHECKED 73, LABELLED 349, OPEN 2,529 of 184,893 (checked below)."),
]


# P4's pre-registered scope: H-1 to H-10, M-1 to M-5, V-1 to V-8, D-1 to D-3, each with its lettered variants
# (H-6p, H-6n, M-3r, M-4x, V-1n, V-6r). V-9 to V-12 lie outside it; they are reported, not counted toward the bar.
SCOPE = {"H": 10, "M": 5, "V": 8, "D": 3}


def in_scope(fid: str) -> bool:
    family, number = fid.split("-")
    return int(re.match(r"\d+", number).group()) <= SCOPE[family]


def find(data: bytes, needle: str) -> list[int] | None:
    words = [re.escape(w) for w in needle.split()]
    m = re.search(r"\s+".join(words).encode(), data)
    return [m.start(), m.end()] if m else None


def rounds(x: F, places: int, rule: str = "up") -> F:
    scaled = x * 10 ** places
    lo = scaled.numerator // scaled.denominator
    frac = scaled - lo
    if frac > F(1, 2) or (frac == F(1, 2) and (rule == "up" or lo % 2 == 1)):
        lo += 1
    return F(lo, 10 ** places)


def prechecks() -> dict:
    out = {}
    out["V-1 176/594 at 3 places (ties up)"] = str(rounds(F(176, 594), 3))
    out["V-2 52/243, 31/243 at 3; 100*21/243 at 1"] = [str(rounds(F(52, 243), 3)), str(rounds(F(31, 243), 3)),
                                                      str(rounds(F(2100, 243), 1))]
    diffs = [F(x, 1000) for x in (-100, -133, 94, -192, 21, 86, -57, 0, 61, -50, -246, -29)]
    n, mean = len(diffs), sum(diffs) / len(diffs)
    ss = sum((x - mean) ** 2 for x in diffs)
    out["V-6 sum (thousandths), sample variance"] = [str(sum(diffs) * 1000), str(ss / (n - 1))]
    out["V-6 sqrt(sample var) in [0.1075, 0.1085)"] = F(10750, 100000) ** 2 <= ss / (n - 1) < F(10850, 100000) ** 2
    out["V-6r sqrt(population var) in [0.1025, 0.1035)"] = F(1025, 10000) ** 2 <= ss / n < F(1035, 10000) ** 2
    p12 = {".460938": 1888, ".875488": 3586, ".000977": 4, ".001953": 8, ".218750": 896, ".993164": 4068}
    out["main-text p values as k/4096 at 6 places, ties up / half even (new fixture candidate)"] = {
        printed: [str(rounds(F(k, 4096), 6)), str(rounds(F(k, 4096), 6, "even")), F(k, 4096) * 10 ** 7 % 10 == 5]
        for printed, k in p12.items()}
    out["H-5 2 x 2e7 x 1e-8; h050 2 x 2e6 x 1e-8"] = [str(2 * 2 * 10 ** 7 * F(1, 10 ** 8)),
                                                     str(2 * 2 * 10 ** 6 * F(1, 10 ** 8))]
    out["H-6 1/20 <= 1/16; H-6p 1/40 <= 1/36; H-6n 1/20 <= 1/25"] = [F(1, 20) <= F(1, 16), F(1, 40) <= F(1, 36),
                                                                       F(1, 20) <= F(1, 25)]

    def primes_upto(n):
        return [p for p in range(2, n + 1) if all(p % d for d in range(2, int(p ** 0.5) + 1))]

    def pi(x: F) -> int:
        return len(primes_upto(x.numerator // x.denominator))

    def first_x(k):  # smallest whole x with pi(x) - pi(x/2) >= k for every real y >= x (checked to 2000)
        for x in range(1, 2000):
            if all(pi(F(y)) - pi(F(y, 2)) >= k for y in range(x, 2000)) and \
               all(pi(F(2 * y + 1, 2)) - pi(F(2 * y + 1, 4)) >= k for y in range(x, 2000)):
                return x
    out["M-4 smallest x (whole, and half-integers, to 2000) with pi(x)-pi(x/2) >= 1..5"] = [first_x(k)
                                                                                            for k in range(1, 6)]
    out["D-3 73+349+2529, 100*2951/184893 at 2 places"] = [73 + 349 + 2529, str(rounds(F(295100, 184893), 2))]
    t = {"256": (F(48, 10), F(6, 10)), "384": (F(92, 10), F(11, 10)), "2500 (h)": (F(18), F(21, 10))}
    out["AlphaFold '8x faster': ensembled/plain time (new fixture candidate)"] = {
        k: [str(a / b), str(rounds(a / b, 0))] for k, (a, b) in t.items()}
    out["AlphaFold 'around 350,000' vs 355,993 rounded at the written place (10^4)"] = str(
        rounds(F(355993, 10 ** 4), 0) * 10 ** 4)
    return out


def main() -> None:
    rows, bar_fail = [], []
    for fid, path, needles, outcome, why in FIXTURES:
        data = path.read_bytes()
        spans = {n: find(data, n) for n in needles}
        missing = [n for n, s in spans.items() if s is None]
        if missing and outcome not in ("ABSENT",):
            raise SystemExit(f"{fid}: needle not found: {missing}")
        rows.append({"fixture": fid, "file": str(path.relative_to(ROOT) if path.is_relative_to(ROOT) else path),
                     "file_sha256": hashlib.sha256(data).hexdigest(), "spans": spans, "outcome": outcome,
                     "reason": why, "in_preregistered_scope": in_scope(fid)})
        if outcome in ("CHANGED", "ABSENT") and in_scope(fid):
            bar_fail.append(fid)
    cov = json.loads((PILOTS / "claude-constitution/run-20261012T1800Z/coverage.json").read_text())
    cov = cov.get("coverage", cov)
    outcomes = ("ANCHORED", "RE-WORDED", "CHANGED", "ABSENT", "NOT A QUOTE")
    result = {"fixtures": rows, "changed_or_absent": bar_fail, "pass": not bar_fail,
              "counts": {o: sum(r["outcome"] == o for r in rows if r["in_preregistered_scope"]) for o in outcomes},
              "counts_outside_scope": {o: sum(r["outcome"] == o for r in rows if not r["in_preregistered_scope"])
                                       for o in outcomes},
              "constitution_coverage_by_status": cov.get("bytes_by_status"),
              "prechecks_not_ve_verdicts": prechecks()}
    (EV / "fixture-anchors.json").write_text(json.dumps(result, indent=1, ensure_ascii=False, default=str) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "fixtures"}, indent=1, ensure_ascii=False,
                     default=str))


if __name__ == "__main__":
    main()
