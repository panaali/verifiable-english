"""ME-0 labels: Michelson and Morley 1887 (`physics-michelson-morley/source.txt`, units h001-h173).

Each unit: (plan kind, status[, feature or W6a formula]). Status "L" LABELLED, "U" UNFORMALISED with one
missing feature, "C" CHECKED with a W6a statement (support: testimony). ("mixed", parts) splits a unit at anchors.
The table rows are transcribed from the pinned bytes by `_row` (no number is typed by hand); the graph certifies,
from the stated rows, that each printed Mean is the tenths-rounding of its three sessions, that the unlabelled row
repeats columns 8-16 of "Mean in w. l.", and that each Final mean is the mean of marks k and k + 8.
"""
from __future__ import annotations

import re
from pathlib import Path

TARGET = "physics-michelson-morley"
SOURCES = [("source.txt", "h")]
SRC = (Path(__file__).resolve().parents[3] / "docs/research/evidence/math-evidence" / TARGET / "source.txt"
       ).read_text(encoding="utf-8")

UNITS = {
    "meter": {"scale": "100", "display": {"kind": "decimal", "label": "meters"}},
    "centimeter": {"scale": "100", "display": {"kind": "decimal", "label": "centimeters"}},
    "minute": {"scale": "1", "display": {"kind": "decimal", "label": "minutes"}},
    "division": {"scale": "100", "display": {"kind": "decimal", "label": "divisions"}},
    "wave_length": {"scale": "1000", "display": {"kind": "decimal", "label": "wave-lengths"}},
}

CONSTANTS: dict[str, tuple[str, str, str]] = {
    "float_outside_diameter": ("meter", "outside diameter of the annular wooden float", "the float's outside diameter"),
    "float_inside_diameter": ("meter", "inside diameter of the annular wooden float", "the float's inside diameter"),
    "float_thickness": ("meter", "thickness of the annular wooden float", "the float's thickness"),
    "trough_thickness": ("centimeter", "thickness of the cast-iron trough", "the trough's thickness"),
    "mirror_diameter": ("centimeter", "diameter of each speculum-metal mirror", "the mirror diameter"),
    "glass_thickness": ("centimeter", "thickness of the plane-parallel glasses b and e", "the glass thickness"),
    "glass_surface_width": ("centimeter", "first side of the glass surfaces", "the glass surface width"),
    "glass_surface_height": ("centimeter", "second side of the glass surfaces", "the glass surface height"),
    "rotation_period": ("minute", "time of one turn of the apparatus", "the time of one turn"),
    "fringe_width_min": ("division", "smallest fringe width observed", "the smallest fringe width"),
    "fringe_width_max": ("division", "largest fringe width observed", "the largest fringe width"),
}

SESSIONS = {"noon": ("Noon Observations.", ("July 8", "July 9", "July 11")),
            "pm": ("P. M. Observations.", ("July 8", "July 9", "July 12"))}
MARKS = ["16 (start)"] + [str(k) for k in range(1, 16)] + ["16 (end)"]


def _row(session: str, label: str) -> list[str]:
    lines = SRC.splitlines()
    start = lines.index(SESSIONS[session][0])
    for line in lines[start + 1:]:
        cells = [c.strip() for c in line.split("|")]
        if cells[0] == label and all(re.fullmatch(r"\d*\.\d+", c) for c in cells[1:] if c):
            return [("0" + c if c.startswith(".") else c) for c in cells[1:] if c]
    raise KeyError((session, label))


def _c(tag, name):
    return ["const", tag, name]


def _d(tag, value):
    return ["decimal", tag, value]


def both(*fs):
    out = fs[-1]
    for f in reversed(fs[:-1]):
        out = ["and", f, out]
    return out


def _facts(prefix: str, tag: str, values: list[str], what: str, session: str) -> list:
    out = []
    for k, v in enumerate(values):
        name = f"{prefix}_c{k:02d}"
        CONSTANTS[name] = (tag, f"{what}, {session} observations, mark {MARKS[k]}", f"the {what} at mark {MARKS[k]}"
                           f" ({session})")
        out.append(["eq", _c(tag, name), _d(tag, v)])
    return out


ROWS = {}
for s in SESSIONS:
    for day in SESSIONS[s][1]:
        key = f"r_{s}_{day.replace(' ', '').lower()}"
        ROWS[key] = both(*_facts(key, "division", _row(s, day), f"mean reading of {day} (screw-head divisions)", s))
    ROWS[f"mean_{s}"] = both(*_facts(f"mean_{s}", "division", _row(s, "Mean"), "printed Mean", s))
    ROWS[f"mwl_{s}"] = both(*_facts(f"mwl_{s}", "wave_length", _row(s, "Mean in w. l."),
                                    "printed Mean in wave-lengths", s))
    ROWS[f"half_{s}"] = both(*_facts(f"half_{s}", "wave_length", _row(s, ""), "printed second-half value", s))
    ROWS[f"final_{s}"] = both(*_facts(f"final_{s}", "wave_length", _row(s, "Final mean"), "printed Final mean", s))

L, U, C = "L", "U", "C"
LABELS = {
    "h001": ("meta", L),
    **{f"h{i:03d}": ("exposition", L) for i in range(2, 7)},
    "h007": ("equation", U, "calc"),
    "h008": ("exposition", L),
    "h009": ("empirical claim", U, "attribution"),
    "h010": ("exposition", L),
    "h011": ("empirical claim", U, "attribution"),
    "h012": ("citation", L),
    "h013": ("exposition", L),
    "h014": ("citation", L),
    "h015": ("meta", L),
    "h016": ("hedge", U, "attitudes"),
    "h017": ("hedge", U, "attitudes"),
    "h018": ("exposition", L),
    "h019": ("empirical claim", U, "events"),
    "h020": ("exposition", L),
    "h021": ("hedge", U, "attitudes"),
    "h022": ("citation", L),
    "h023": ("citation", L),
    "h024": ("exposition", U, "events"),
    "h025": ("citation", L),
    "h026": ("exposition", L),
    "h027": ("citation", L),
    "h028": ("exposition", L),
    "h029": ("exposition", L),
    "h030": ("citation", L),
    "h031": ("exposition", L),
    "h032": ("comparison", U, "calc"),
    "h033": ("meta", L),
    "h034": ("exposition", L),
    "h035": ("caption", L),
    "h036": ("exposition", L),
    "h037": ("exposition", L),
    "h038": ("exposition", L),
    "h039": ("equation", U, "calc-algebra"),
    "h040": ("comparison", U, "approximation"),
    "h041": ("exposition", L),
    "h042": ("definition", U, "calc"),
    "h043": ("definition", U, "calc"),
    "h044": ("equation", U, "calc-algebra"),
    "h045": ("equation", U, "calc-algebra"),
    "h046": ("equation", U, "approximation"),
    "h047": ("equation", U, "calc-algebra"),
    "h048": ("equation", U, "calc-algebra"),
    "h049": ("equation", U, "calc"),
    "h050": ("equation", U, "calc"),
    "h051": ("exposition", L),
    "h052": ("exposition", L),
    "h053": ("comparison", U, "approximation"),
    "h054": ("comparison", U, "approximation"),
    "h055": ("caption", L),
    "h056": ("quantity", U, "approximation"),
    "h057": ("mixed", [(None, "exposition", L),
                       ("1.5 meter outside", "quantity", C, both(
                           ["eq", _c("meter", "float_outside_diameter"), _d("meter", "1.5")],
                           ["eq", _c("meter", "float_inside_diameter"), _d("meter", "0.7")],
                           ["eq", _c("meter", "float_thickness"), _d("meter", "0.25")]))]),
    "h058": ("mixed", [(None, "exposition", L),
                       ("1.6 centimeter thick", "quantity", C,
                        ["eq", _c("centimeter", "trough_thickness"), _d("centimeter", "1.6")]),
                       ("and of such dimensions", "quantity", U, "approximation")]),
    **{f"h{i:03d}": ("exposition", L) for i in range(59, 63)},
    "h063": ("caption", L),
    "h064": ("exposition", L),
    "h065": ("exposition", L),
    "h066": ("exposition", L),
    "h067": ("mixed", [(None, "exposition", L),
                       ("five centimeters in diameter", "quantity", C,
                        ["eq", _c("centimeter", "mirror_diameter"), _d("centimeter", "5")]),
                       ("and the glasses", "exposition", L)]),
    "h068": ("quantity", C, both(["eq", _c("centimeter", "glass_thickness"), _d("centimeter", "1.25")],
                                 ["eq", _c("centimeter", "glass_surface_width"), _d("centimeter", "5.0")],
                                 ["eq", _c("centimeter", "glass_surface_height"), _d("centimeter", "7.5")])),
    "h069": ("exposition", L),
    "h070": ("exposition", L),
    "h071": ("exposition", L),
    "h072": ("caption", L),
    **{f"h{i:03d}": ("exposition", L) for i in range(73, 77)},
    "h077": ("caption", L),
    "h078": ("exposition", L),
    "h079": ("quantity", U, "approximation"),
    "h080": ("exposition", L),
    "h081": ("quantity", U, "quantities"),
    "h082": ("mixed", [(None, "exposition", L),
                       ("(one turn in six minutes)", "quantity", C,
                        ["eq", _c("minute", "rotation_period"), _d("minute", "6")]),
                       (" and after a few minutes", "exposition", L)]),
    "h083": ("exposition", L),
    "h084": ("quantity", U, "quantities"),
    "h085": ("empirical claim", U, "events"),
    "h086": ("table", U, "calc-data"),
    "h087": ("definition", U, "calc-dimension"),
    "h088": ("mixed", [(None, "quantity", C, both(
                           ["eq", _c("division", "fringe_width_min"), _d("division", "40")],
                           ["eq", _c("division", "fringe_width_max"), _d("division", "60")])),
                       ("the mean value being near 50", "quantity", U, "approximation"),
                       ("so that one division", "definition", U, "calc-dimension")]),
    "h089": ("exposition", L),
    "h090": ("caption", L),
    "h091": ("table", L),
    "h092": ("table", C, ROWS["r_noon_july8"]),
    "h093": ("table", C, ROWS["r_noon_july9"]),
    "h094": ("table", C, ROWS["r_noon_july11"]),
    "h095": ("table", C, ROWS["mean_noon"]),
    "h096": ("table", C, ROWS["mwl_noon"]),
    "h097": ("table", C, ROWS["half_noon"]),
    "h098": ("table", C, ROWS["final_noon"]),
    "h099": ("caption", L),
    "h100": ("table", C, ROWS["r_pm_july8"]),
    "h101": ("table", C, ROWS["r_pm_july9"]),
    "h102": ("table", C, ROWS["r_pm_july12"]),
    "h103": ("table", C, ROWS["mean_pm"]),
    "h104": ("table", C, ROWS["mwl_pm"]),
    "h105": ("table", C, ROWS["half_pm"]),
    "h106": ("table", C, ROWS["final_pm"]),
    "h107": ("caption", L),
    "h108": ("caption", L),
    "h109": ("caption", L),
    "h110": ("hedge", U, "attitudes"),
    "h111": ("caption", L),
    "h112": ("empirical claim", U, "approximation"),
    "h113": ("equation", U, "calc"),
    "h114": ("equation", U, "calc"),
    "h115": ("comparison", U, "calc"),
    "h116": ("comparison", U, "calc-derive"),
    "h117": ("exposition", L),
    "h118": ("hedge", U, "attitudes"),
    "h119": ("exposition", L),
    "h120": ("hedge", U, "attitudes"),
    "h121": ("empirical claim", U, "attribution"),
    "h122": ("empirical claim", U, "attribution"),
    "h123": ("empirical claim", U, "attribution"),
    "h124": ("meta", L),
    "h125": ("hedge", U, "attitudes"),
    "h126": ("hedge", U, "attitudes"),
    "h127": ("exposition", L),
    "h128": ("exposition", L),
    "h129": ("empirical claim", U, "events"),
    "h130": ("definition", U, "calc"),
    "h131": ("exposition", L),
    "h132": ("definition", U, "calc"),
    "h133": ("definition", U, "calc"),
    "h134": ("equation", U, "approximation"),
    "h135": ("equation", U, "approximation"),
    "h136": ("exposition", L),
    "h137": ("definition", U, "calc"),
    "h138": ("equation", U, "calc-algebra"),
    "h139": ("equation", U, "approximation"),
    "h140": ("equation", U, "approximation"),
    "h141": ("equation", U, "approximation"),
    "h142": ("equation", U, "approximation"),
    "h143": ("equation", U, "calc"),
    "h144": ("equation", U, "calc"),
    "h145": ("hedge", U, "attitudes"),
    "h146": ("quantity", U, "approximation"),
    "h147": ("quantity", U, "approximation"),
    "h148": ("caption", L),
    "h149": ("quantity", U, "approximation"),
    "h150": ("exposition", L),
    "h151": ("exposition", L),
    "h152": ("hedge", U, "attitudes"),
    "h153": ("hedge", U, "attitudes"),
    **{f"h{i:03d}": ("exposition", L) for i in range(154, 165)},
    "h165": ("meta", L),
    "h166": ("exposition", L),
    "h167": ("hedge", U, "attitudes"),
    "h168": ("meta", L),
    "h169": ("exposition", L),
    "h170": ("hedge", U, "attitudes"),
    "h171": ("meta", L),
    "h172": ("exposition", L),
    "h173": ("exposition", L),
}

TABLE_UNITS = {"noon": ("h092", "h093", "h094", "h095", "h096", "h097", "h098"),
               "pm": ("h100", "h101", "h102", "h103", "h104", "h105", "h106")}


def _consequences(s: str):
    day = [f"r_{s}_{d.replace(' ', '').lower()}" for d in SESSIONS[s][1]]
    rounded, halves, finals = [], [], []
    for k in range(17):
        total = ["add", "division", _c("division", f"{day[0]}_c{k:02d}"),
                 ["add", "division", _c("division", f"{day[1]}_c{k:02d}"), _c("division", f"{day[2]}_c{k:02d}")]]
        three = ["scale", "division", "3", _c("division", f"mean_{s}_c{k:02d}")]
        rounded += [["le", ["add", "division", three, _d("division", "-0.15")], total],
                    ["lt", total, ["add", "division", three, _d("division", "0.15")]]]
    for k in range(9):
        halves.append(["eq", _c("wave_length", f"half_{s}_c{k:02d}"), _c("wave_length", f"mwl_{s}_c{k + 8:02d}")])
        finals.append(["eq", ["scale", "wave_length", "2", _c("wave_length", f"final_{s}_c{k:02d}")],
                       ["add", "wave_length", _c("wave_length", f"mwl_{s}_c{k:02d}"),
                        _c("wave_length", f"half_{s}_c{k:02d}")]])
    return both(*rounded), both(*halves), both(*finals)


def graph(content, prefix, env, prove, q):
    nodes, names = [], []
    for s, units in TABLE_UNITS.items():
        for uid in units:
            nodes.append({"name": f"{s}_{uid}", "quantity": content[uid], "unit": uid})
        r1, r2, r3, mean, mwl, half, final = (f"{s}_{u}" for u in units)
        rounded, halves, finals = _consequences(s)
        for name, formula, premises in ((f"{s}_means_are_rounded_means", rounded, [r1, r2, r3, mean]),
                                        (f"{s}_second_half_repeats_marks_8_to_16", halves, [mwl, half]),
                                        (f"{s}_final_means_average_opposite_marks", finals, [mwl, half, final])):
            by = {n["name"]: n["quantity"] for n in nodes}
            cert = prove(env, [by[p] for p in premises], q(formula))
            if cert is None:
                raise SystemExit(f"no certificate for {name}")
            nodes.append({"name": name, "quantity": q(formula), "premises": premises, "certificate": cert})
            names.append(name)
    by = {n["name"]: n["quantity"] for n in nodes}
    root = q(both(*[by[n]["formula"] for n in names]))
    cert = prove(env, [by[n] for n in names], root)
    nodes.append({"name": "table_arithmetic", "quantity": root, "premises": names, "certificate": cert})
    return {"root": "table_arithmetic", "nodes": nodes}


def _control(specs):
    """Negative control: the printed noon Mean at mark 1 (41.6) becomes 41.9; the graph's certificate for the
    true row is kept, so only Lean's replay can catch it."""
    kind, status, formula = specs["h095"]
    specs["h095"] = (kind, status, _replace(formula, "mean_noon_c01", "41.9"))
    return specs


def _replace(formula, name, value):
    if isinstance(formula, list):
        if formula[:1] == ["eq"] and formula[1] == ["const", "division", name]:
            return ["eq", formula[1], ["decimal", "division", value]]
        return [_replace(x, name, value) for x in formula]
    return formula


CONTROL = ("source.txt", _control)
