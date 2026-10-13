"""ME-0 labels: Ramanujan 1919, "A proof of Bertrand's postulate" (`math-ramanujan-bertrand/source.txt`, m001-m049).

The pinned bytes are the 1927 Collected Papers OCR; formulas are garbled by the OCR and stay as printed. The
analytic steps (logarithms, the Chebyshev functions, Stirling's approximation, real x) are tagged `arith-import`:
no plan batch states them in VE, and the plan keeps them residual or imported (research 2.6, row 12).
"""
from __future__ import annotations

TARGET = "math-ramanujan-bertrand"
SOURCES = [("source.txt", "m")]
UNITS: dict = {}
CONSTANTS: dict = {}

L, U = "L", "U"
ANALYTIC = ("proof step", U, "arith-import")
FORMULA = ("equation", U, "arith-import")

LABELS = {
    "m001": ("meta", L),
    "m002": ("citation", L),
    "m003": ("meta", L),
    "m004": ("theorem", U, "arith-import"),
    "m005": ("citation", L),
    "m006": ("exposition", L),
    "m007": ("definition", U, "arith-import"),
    "m008": FORMULA,
    "m009": FORMULA,
    "m010": ("definition", U, "arith-import"),
    "m011": ANALYTIC,
    "m012": FORMULA,
    "m013": ANALYTIC,
    "m014": FORMULA,
    "m015": ANALYTIC,
    "m016": FORMULA,
    "m017": FORMULA,
    "m018": FORMULA,
    "m019": FORMULA,
    "m020": ANALYTIC,
    "m021": FORMULA,
    "m022": FORMULA,
    "m023": ANALYTIC,
    "m024": FORMULA,
    "m025": FORMULA,
    "m026": ("meta", L),
    "m027": ANALYTIC,
    "m028": FORMULA,
    "m029": ANALYTIC,
    "m030": FORMULA,
    "m031": FORMULA,
    "m032": ANALYTIC,
    "m033": ANALYTIC,
    "m034": FORMULA,
    "m035": ("proof step", U, "calc-derive"),
    "m036": FORMULA,
    "m037": ("theorem", U, "arith-import"),
    "m038": ("mixed", [(None, "theorem", U, "arith-import"),
                       ("by actual verification", "proof step", U, "arith")]),
    "m039": ("meta", L),
    "m040": ("definition", U, "arith"),
    "m041": ANALYTIC,
    "m042": ANALYTIC,
    "m043": FORMULA,
    "m044": ANALYTIC,
    "m045": ANALYTIC,
    "m046": FORMULA,
    "m047": ANALYTIC,
    "m048": ("theorem", U, "arith"),
    "m049": ("theorem", U, "arith"),
}
