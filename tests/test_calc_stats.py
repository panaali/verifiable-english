"""ME-7: exact statistics (math-evidence spec 7; fixtures V-6, V-6r and S-5 of 13.2 and 13.3).

Lean decides every answer here: one Lean file evaluates each fixture with `VE.Calc.Stats` and prints it, and the tests
compare the printed lines with the spec's hand-computed numbers. The sign-flip p and the binomial tail are also checked
against an exhaustive enumeration written here, so a wrong count in Lean and in the hand number at once is caught.
"""
import itertools
import json
import math
import shutil
import subprocess
from fractions import Fraction

import pytest

from subprocesses import HANG_TIMEOUT
from tests.lean_build import LEAN, lean_build

HEADER = """import VE.Calc.StatsExamples
open VE.Calc VE.Calc.StatsExamples VE.Numbers

def q (x : Option Rat) : String := match x with
  | some r => if r.den = 1 then toString r.num else s!"{r.num}/{r.den}"
  | none => "undefined"
def line (key value : String) : IO Unit := IO.println (key ++ "\\t" ++ value)
def rats (xs : List Int) (d : Nat) : List Rat := xs.map fun (k : Int) => Rat.ofInt k / d
"""

V6 = [-100, -133, 94, -192, 21, 86, -57, 0, 61, -50, -246, -29]
# Twelve synthetic differences in thousandths, not symmetric, with two equal magnitudes (a tie at the boundary).
SYNTH = [130, -40, 75, 220, -15, 90, 60, -110, 5, 40, 185, -60]


def sign_flip(d):
    """The exact two-sided sign-flip p by enumerating all 2ⁿ sign vectors (the observed vector counted)."""
    obs = abs(sum(d))
    hits = sum(1 for s in itertools.product((1, -1), repeat=len(d)) if abs(sum(k * x for k, x in zip(s, d))) >= obs)
    return Fraction(hits, 2 ** len(d))


def binomial_tail(n, k, p):
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k, n + 1))


def show(x):
    if x is None:
        return "undefined"
    x = Fraction(x)
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"


FIXTURES = [
    # V-6: the sample variance and the three printed roots; V-6r: the population variance's root is 0.103, not 0.108.
    ("v6-sum", "q (some v6.sum)", "-109/200"),
    ("v6-variance", "q (sampleVariance? v6)", "1527611/132000000"),
    ("v6-sd", "toString (rootsAt sv)", "[108]"),
    ("v6-se", "toString (rootsAt (sv / 12))", "[31]"),
    ("v6-half-width", "toString (rootsAt (2593 ^ 2 / 1000 ^ 2 * sv / 12))", "[81]"),
    ("v6r-variance", "q (populationVariance? v6)", "1527611/144000000"),
    ("v6r-sd", "toString (rootsAt pv)", "[103]"),
    ("v6r-claim", "toString (decide (SqrtRoundsTo .tiesUp ⟨108, 3⟩ pv))", "false"),
    # S-5 (J5): undefined below each statistic's shortest list, defined at it; a negative value has no root.
    ("s5-empty", "toString ([Stat.mean, .variance, .populationVariance, .signFlip].map fun s => q (s.run []))",
     "[undefined, undefined, undefined, undefined]"),
    ("s5-one", "toString ([Stat.mean, .variance, .populationVariance, .signFlip].map fun s => q (s.run [3]))",
     "[3, undefined, 0, 1]"),
    ("s5-root", "toString (decide (SqrtRoundsTo .tiesUp ⟨1, 1⟩ (-1 / 100)))", "false"),
    ("s5-kappa", "q (kappa? [[0, 0], [0, 0]])", "undefined"),
    ("s5-unguarded", "toString [q (some (binomialTail 10 8 2)), q (some (binomialTail 1 1 2)), q (some (signFlipP []))]",
     "[7424, 2, 1]"),
    ("binomial-ends", "toString [q (some (binomialTail 10 8 0)), q (some (binomialTail 10 8 1))]", "[0, 1]"),
    # A binomial tail and a kappa of a 2 × 2 table (po = 7/10, pe = 1/2).
    ("binomial-half", "q (some (binomialTail 10 8 (1 / 2)))", "7/128"),
    ("kappa", "q (kappa? [[20, 5], [10, 15]])", "2/5"),
    # The sign-flip p over twelve differences: nine +1, three −1; by hand 2 · (1 + 12 + 66 + 220) = 598 of 4096.
    ("sign-flip-hand", "q (some (signFlipP d12))", "299/2048"),
    # The limit: 16 values within `maxWork`; one unit short of their work is UNKNOWN. The charge counts value bits.
    ("sign-flip-16", "toString ((signFlipC Work.maxWork d16).map fun (p, w) => (q (some p), w))",
     "(some (1/32768, 179311968))"),
    ("sign-flip-short", "toString ((signFlipC 179311967 d16).isNone)", "true"),
    ("sign-flip-empty", "toString [(signFlipC 120 []).isSome, (signFlipC 119 []).isNone, (signFlipC 0 d16).isNone]",
     "[true, true, true]"),
    # Large values the length-only charge admitted (1,114,128 and 53,260 units): refused, UNKNOWN, by their bits.
    ("sign-flip-big16", "toString (signFlipWork big16, (signFlipC Work.maxWork big16).isNone)", "(9612065232, true)"),
    ("sign-flip-big12", "toString (signFlipWork big12, (signFlipC Work.maxWork big12).isNone)", "(11241469680, true)"),
    # ME-4's aggregates over T-1 (scores 3 and 5 for 32B).
    ("agg-variance", "toString ((Agg.run TableExamples.T1 (.isText \"judge\" \"32B\") (.variance \"score\")).map toString)",
     "(some 2)"),
    ("agg-population-variance",
     "toString ((Agg.run TableExamples.T1 (.isText \"judge\" \"32B\") (.populationVariance \"score\")).map toString)",
     "(some 1)"),
]

# Checked against enumeration here: the expected value is computed by `sign_flip` and `binomial_tail`.
ENUMERATED = [
    ("sign-flip-synthetic", f"q (some (signFlipP (rats {json.dumps(SYNTH)} 1000)))",
     show(sign_flip([Fraction(x, 1000) for x in SYNTH]))),
    ("sign-flip-v6", "q (some (signFlipP v6))", show(sign_flip(V6))),
    ("binomial-third", "q (some (binomialTail 12 9 (1 / 3)))", show(binomial_tail(12, 9, Fraction(1, 3)))),
]


# The charge is never below the work: 12.2's units counted here by running the sign flip (one per value plus its bits).
COPRIME = [Fraction(2 ** 999, 2 ** 1999 + 2 * i + 1) for i in range(6)]
PRIMES = [Fraction(1, 3), Fraction(-2, 5), Fraction(7, 11), Fraction(-13, 17), Fraction(19, 23), Fraction(29, 31),
          Fraction(-37, 41), Fraction(43, 47)]
WORK_CASES = {
    "d12": ("d12", [1] * 9 + [-1] * 3),
    "v6": ("v6", [Fraction(x, 1000) for x in V6]),
    "synthetic": (f"rats {json.dumps(SYNTH)} 1000", [Fraction(x, 1000) for x in SYNTH]),
    "coprime": ("(List.range 6).map fun i => ((2 ^ 999 : Nat) : Rat) / ((2 ^ 1999 + 2 * i + 1 : Nat) : Rat)", COPRIME),
    "primes": ("[1/3, -2/5, 7/11, -13/17, 19/23, 29/31, -37/41, 43/47]", PRIMES),
}
WORKS = [(f"work-{name}", f"toString (signFlipWork ({expression}))", None)
         for name, (expression, _) in WORK_CASES.items()]


def qbits(x):
    x = Fraction(x)
    return max(1, abs(x.numerator).bit_length()) + max(1, x.denominator.bit_length())


def counted_work(d):
    """`signFlipP d` run here, each value it computes charged one visit plus its bits."""
    d = [Fraction(x) for x in d]
    n = len(d)

    def units(values):
        return sum(1 + qbits(v) for v in values)

    def vector(signs):
        products = [k * x for k, x in zip(signs, d)]
        mean = sum(products) / n if n else Fraction(0)
        return units([Fraction(k) for k in signs] + products + [sum(products[i:]) for i in range(n + 1)]
                     + [Fraction(n), mean, abs(mean)]) + 2

    return (units(d) + vector([1] * n) + sum(vector(s) for s in itertools.product((1, -1), repeat=n))
            + qbits(sign_flip(d)) + 1)


@pytest.fixture(scope="module")
def lean(tmp_path_factory):
    lake = shutil.which("lake")
    if lake is None:
        pytest.skip("lake is not available")
    lean_build("VE")
    path = tmp_path_factory.mktemp("stats") / "Stats.lean"
    path.write_text(HEADER + "".join(f"#eval line {json.dumps(key)} ({expression})\n"
                                     for key, expression, _ in FIXTURES + ENUMERATED + WORKS))
    done = subprocess.run([lake, "env", "lean", str(path)], cwd=LEAN, capture_output=True, text=True,
                          timeout=HANG_TIMEOUT)
    assert done.returncode == 0, done.stdout + done.stderr
    return dict(row.split("\t", 1) for row in done.stdout.splitlines())


@pytest.mark.parametrize("key, expected", [pytest.param(key, expected, id=key)
                                           for key, _, expected in FIXTURES + ENUMERATED])
def test_fixture(lean, key, expected):
    assert lean[key] == expected


def test_every_fixture_printed_once(lean):
    assert sorted(lean) == sorted(key for key, _, _ in FIXTURES + ENUMERATED + WORKS)


@pytest.mark.parametrize("name", list(WORK_CASES))
def test_sign_flip_charge_covers_work(lean, name):
    """Conservative: Lean's charge is at least the units the run takes, and within 16 times of them."""
    work = counted_work(WORK_CASES[name][1])
    assert work <= int(lean[f"work-{name}"]) <= 16 * work


def test_hand_numbers_agree_with_enumeration():
    """The spec's hand numbers this file states are the enumeration's too (a guard on the fixtures themselves)."""
    assert sign_flip([1] * 9 + [-1] * 3) == Fraction(598, 4096) == Fraction(2 * sum(math.comb(12, i) for i in range(4)),
                                                                          4096)
    assert binomial_tail(10, 8, Fraction(1, 2)) == Fraction(7, 128)
    assert binomial_tail(10, 8, 2) == 7424 and binomial_tail(1, 1, 2) == 2
    assert sum(V6) == -545 and sum(x * x for x in V6) == 152053
    assert sign_flip([Fraction(x, 1000) for x in SYNTH]) not in (0, 1)
