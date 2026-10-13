"""SC-M0: retrospective scope tally over the pinned pilot runs (research only; not product code).

Reads the pinned constitution and UDHR runs read only, regenerates the layout of every unit with a Python
transcription of the item-1 spec's `VE.Layout` (docs/spec/scope.md 1.2 and 4.1: `ofSource`, `listRun`,
`itemRun`), and writes:
  - scope-tally.json: units and bytes by reach kind and effect, the colon lead-ins, the restrictive connective
    units, `governed_by`, and the would-be `other:scope` tags;
  - checks.json: the reproduction checks pre-registered in docs/research/scope-phase1.md 1.4.

Usage: python3 -I research/scope/sc_m0_tally.py <manage-agents/pilots> <output dir>
"""

import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

CONSTITUTION = ("claude-constitution/run-20261012T1800Z/units.json", "claude-constitution/source/claude-constitution.md")
UDHR = ("udhr/run-20261012T1800Z/units.json", "udhr/source/udhr.md")

SP, NL = 32, 10
STATUSES = ["CHECKED", "LABELLED", "OPEN", "READINGS", "UNFORMALISED"]
ADMITTED_RULE = {"CHECKED", "OPEN", "READINGS"}
RESTRICTIVE = ["That said", "However", "At the same time", "This doesn't mean", "This doesn’t mean",
               "This doesn't imply", "This doesn’t imply", "This does not mean", "This does not imply",
               "Nevertheless", "Still"]


# --- VE.Layout, transcribed from docs/spec/scope.md 4.1 -------------------------------------------------------

def get(b, i):
    return b[i] if 0 <= i < len(b) else 0  # ByteArray.get! default


def line_start(b, s):
    k = s
    while k > 0 and get(b, k - 1) != NL:
        k -= 1
    return k


def spaces_only(b, i, j):
    return all(get(b, i + k) == SP for k in range(j - i))


def skip_spaces(b, i, e):
    for k in range(e - i):
        if get(b, i + k) != SP:
            return i + k
    return e


def is_digit(c):
    return 48 <= c <= 57


def marker_len(b, f, e):
    c = get(b, f)
    if f + 1 < e and c in (42, 45, 43) and get(b, f + 1) == SP:
        return 2
    n = next((k for k in range(e - f) if not is_digit(get(b, f + k))), e - f)
    if 0 < n and f + n + 1 < e and get(b, f + n) == 46 and get(b, f + n + 1) == SP:
        return n + 2
    return None


def is_blank(c):
    return c in (32, 9, 10, 13)


def last_non_blank(b, s, e):
    for k in reversed(range(e - s)):
        if not is_blank(get(b, s + k)):
            return get(b, s + k)
    return None


def bold_label(b, p, e):
    if not (p + 1 < e and get(b, p) == 42 and get(b, p + 1) == 42):
        return False
    for k in range(e - (p + 2)):
        c = get(b, p + 2 + k)
        if c == NL or (c == 42 and p + 3 + k < e and get(b, p + 3 + k) == 42):
            return c == 42 and 0 < k and (get(b, p + 1 + k) == 58 or (p + 4 + k < e and get(b, p + 4 + k) == 58))
    return False


def para_counts(b):
    arr, cnt, blank = [], 0, False
    for c in b:
        arr.append(cnt)
        if c == NL:
            cnt, blank = (cnt + 1 if blank else cnt), True
        elif c in (SP, 9, 13):
            pass
        else:
            blank = False
    arr.append(cnt)
    return arr


def of_source(b, units):
    pc = para_counts(b)
    out = []
    for uid, s, e in units:
        ls = line_start(b, s)
        f = skip_spaces(b, s, e)
        mid = not spaces_only(b, ls, s)
        m = None if mid else marker_len(b, f, e)
        item = ((f - ls) // 2 if (f - ls) % 2 == 0 else None) if m is not None else None
        label = bold_label(b, f + m, e) if (item is not None and m is not None) else False
        out.append({"id": uid, "span": (s, e), "item": item, "midLine": mid,
                    "lead": last_non_blank(b, s, e) == 58, "label": label,
                    "para": pc[s] if s < len(pc) else 0})
    return out


def continues(d, x):
    return (x["item"] is not None and d <= x["item"]) or x["midLine"]


def run_from(d, xs):
    out = []
    for x in xs:
        if not continues(d, x):
            break
        if x["item"] == d:
            out.append(x["id"])
    return out


def run_units(d, xs):
    """Every unit of the run (governed items, deeper items, mid-line continuations): for reporting only."""
    out = []
    for x in xs:
        if not continues(d, x):
            break
        out.append(x["id"])
    return out


def list_run(L, idx, lead):
    i = idx.get(lead)
    if i is None:
        return ("error", f"ScopeUnknownUnit: {lead}")
    if i + 1 >= len(L) or not L[i]["lead"]:
        return ("error", f"NotALeadIn: {lead}")
    d = L[i + 1]["item"]
    if d is None:
        return ("error", f"NotALeadIn: {lead}")
    return ("ok", run_from(d, L[i + 1:]))


def item_run(L, idx, item):
    i = idx.get(item)
    if i is None:
        return ("error", f"ScopeUnknownUnit: {item}")
    x = L[i]
    d = x["item"]
    if d is None or not x["label"]:
        return ("error", f"NotALabel: {item}")
    out = [x["id"]]
    for y in L[i + 1:]:
        if (y["item"] is not None and d < y["item"]) or y["midLine"]:
            out.append(y["id"])
        else:
            break
    return ("ok", out)


# --- helpers ------------------------------------------------------------------------------------------------

def sha256(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def nbytes(u):
    return u["span"][1] - u["span"][0]


def text_of(b, u):
    s, e = u["span"]
    return b[s:e].decode("utf-8", "replace")


def first_text(b, u):
    s, e = u["span"]
    return b[skip_spaces(b, s, e):e].decode("utf-8", "replace")


def primary(u):
    return u.get("missing_feature")


def co(u):
    return u.get("other_blockers") or []


def tot(us):
    return {"units": len(us), "bytes": sum(nbytes(u) for u in us)}


def by_status(us):
    out = {}
    for st in STATUSES:
        sel = [u for u in us if u["status"] == st]
        if sel:
            out[st] = tot(sel)
    return out


def by_tag(us):
    c = defaultdict(list)
    for u in us:
        c[str(primary(u))].append(u)
    return {k: tot(v) for k, v in sorted(c.items(), key=lambda kv: (-len(kv[1]), kv[0]))}


def summary(us):
    return {**tot(us), "by_status": by_status(us), "by_primary_tag": by_tag(us)}


def check(cid, what, expected, measured):
    return {"id": cid, "check": what, "expected": expected, "measured": measured,
            "result": "PASS" if expected == measured else "FAIL"}


# --- per-pilot tally ----------------------------------------------------------------------------------------

def load(root, rel):
    led = json.loads((root / rel[0]).read_text())
    units = led["units"] if isinstance(led, dict) else led
    src = (root / rel[1]).read_bytes()
    spans = [tuple(u["span"]) for u in units]
    assert spans == sorted(spans), "ledger not in span order"
    return units, src


def headings(b, L, U):
    """Markdown heading units (candidates for an `anchor` reach) and the units up to the next heading of the same
    or a higher level."""
    hs = []
    for i, x in enumerate(L):
        if x["midLine"]:
            continue
        t = first_text(b, U[i])
        if t.startswith("#"):
            level = len(t) - len(t.lstrip("#"))
            s = x["span"][0]
            line = b[s:b.find(b"\n", s) if b.find(b"\n", s) >= 0 else len(b)].decode("utf-8", "replace")
            hs.append((i, level, line.strip()))
    out = []
    for n, (i, level, line) in enumerate(hs):
        j = len(L)
        for (k, lv, _) in hs[n + 1:]:
            if lv <= level:
                j = k
                break
        title = line.lstrip("#").strip()
        cond = title.split(" ", 1)[0] in ("When", "If")
        out.append({"unit": L[i]["id"], "level": level, "line": line,
                    "effect": "condition (When/If clause; SC-3b)" if cond else "title",
                    "section": [L[k]["id"] for k in range(i + 1, j)]})
    return out


def tally(root, rel, name):
    U, b = load(root, rel)
    L = of_source(b, [(u["id"], u["span"][0], u["span"][1]) for u in U])
    idx = {x["id"]: i for i, x in enumerate(L)}
    byid = {u["id"]: u for u in U}

    def us(ids):
        return [byid[i] for i in ids]

    # list reaches: every colon lead-in
    leadins = []
    for i, x in enumerate(L):
        if not x["lead"]:
            continue
        u = U[i]
        r = list_run(L, idx, x["id"])
        row = {"unit": x["id"], "bytes": nbytes(u), "status": u["status"], "primary": primary(u),
               "co_blockers": co(u), "excerpt": first_text(b, u)[:100]}
        if r[0] == "ok":
            d = L[i + 1]["item"]
            items = us(r[1])
            row.update({"run": r[1], "run_units": run_units(d, L[i + 1:]),
                        "items_status": dict(Counter(v["status"] for v in items)),
                        "moves_now": u["status"] == "UNFORMALISED" and all(v["status"] in ADMITTED_RULE for v in items)})
        else:
            row.update({"refused": r[1]})
        leadins.append(row)

    # label reaches
    labels = []
    for i, x in enumerate(L):
        if x["label"]:
            r = item_run(L, idx, x["id"])
            labels.append({"unit": x["id"], "excerpt": first_text(b, U[i])[:100], "units": r[1] if r[0] == "ok" else r})

    hs = headings(b, L, U)

    restrictive = [u for u in U if any(first_text(b, u).startswith(c) for c in RESTRICTIVE)]
    tts = [u for u in U if first_text(b, u).split(" ", 1)[0] in ("This", "These", "Such")]
    far = [u for u in U if any(c in text_of(b, u).lower() for c in ("notwithstanding", "subject to"))]

    # governed_by: list runs (governed items) and label item units
    governed_by = defaultdict(list)
    for r in leadins:
        for v in r.get("run", []):
            governed_by[v].append(r["unit"])
    for r in labels:
        if isinstance(r["units"], list):
            for v in r["units"][1:]:
                governed_by[v].append(r["unit"])
    for h in hs:
        if h["effect"] != "title":
            for v in h["section"]:
                governed_by[v].append(h["unit"])

    ok_leads = [r["unit"] for r in leadins if "run" in r]
    gov_units = sorted(set(ok_leads) | {r["unit"] for r in labels} | {h["unit"] for h in hs}
                       | {u["id"] for u in restrictive}, key=idx.get)
    governed = sorted(governed_by, key=idx.get)
    tagged = sorted(set(gov_units) | set(governed), key=idx.get)

    reach = {
        "list": {"effect": "frame", "governors": summary(us(ok_leads)),
                 "governed": summary(us(sorted({v for r in leadins for v in r.get("run", [])}, key=idx.get)))},
        "list_refused": {"effect": "none (NotALeadIn)", "governors": summary(us([r["unit"] for r in leadins if "refused" in r]))},
        "label": {"effect": "title or condition (undetermined by layout)", "governors": summary(us([r["unit"] for r in labels])),
                  "governed": summary(us(sorted({v for r in labels if isinstance(r["units"], list) for v in r["units"][1:]}, key=idx.get)))},
        "anchor_candidate_title": {"effect": "title", "governors": summary(us([h["unit"] for h in hs if h["effect"] == "title"]))},
        "anchor_candidate_condition": {"effect": "condition (SC-3b)", "governors": summary(us([h["unit"] for h in hs if h["effect"] != "title"])),
                                       "governed": summary(us(sorted({v for h in hs if h["effect"] != "title" for v in h["section"]}, key=idx.get)))},
        "frontier_candidate": {"effect": "undetermined (SC-E1)", "governors": summary(restrictive)},
    }

    out = {
        "pilot": name,
        "inputs": {rel[0]: sha256(root / rel[0]), rel[1]: sha256(root / rel[1])},
        "units": len(U), "bytes": len(b),
        "status_totals": by_status(U),
        "reach": reach,
        "colon_leadins": {"summary": summary(us([r["unit"] for r in leadins])), "rows": leadins},
        "restrictive_connectives": {"summary": summary(restrictive),
                                    "rows": [{"unit": u["id"], "bytes": nbytes(u), "status": u["status"], "primary": primary(u),
                                              "co_blockers": co(u), "excerpt": first_text(b, u)[:100]} for u in restrictive]},
        "this_these_such": summary(tts),
        "far_precedence_cues": [{"unit": u["id"], "bytes": nbytes(u), "status": u["status"], "excerpt": first_text(b, u)[:120]} for u in far],
        "labels": labels,
        "headings": [{k: h[k] for k in ("unit", "level", "line", "effect")} | {"section_units": len(h["section"])} for h in hs],
        "governed_by": {k: governed_by[k] for k in governed},
        "would_be_other_scope": {
            "rule": "governor units: colon lead-ins with a list run, bold-label items, markdown headings, restrictive "
                    "connective units; governed units: list-run items, label item units, units under a When/If heading",
            "governor_units": summary(us(gov_units)),
            "governed_units": summary(us(governed)),
            "all": summary(us(tagged)),
            "unformalised_with_no_co_blocker": tot([byid[i] for i in tagged if byid[i]["status"] == "UNFORMALISED" and not co(byid[i])]),
        },
    }
    return out, U, b, L, idx, byid, leadins, labels, hs, restrictive, tts


def span_of(byid, ids):
    return sum(nbytes(byid[i]) for i in ids)


def block(U, prefix):
    return [u for u in U if u["id"] == prefix or u["id"].startswith(prefix + ".")]


def constitution_checks(t, U, b, L, idx, byid, leadins, labels, hs, restrictive, tts):
    C = []
    C.append(check("C1", "status totals", {"CHECKED": {"units": 2, "bytes": 73}, "LABELLED": {"units": 39, "bytes": 349},
                                           "OPEN": {"units": 14, "bytes": 2246}, "READINGS": {"units": 3, "bytes": 283},
                                           "UNFORMALISED": {"units": 1074, "bytes": 181942}}, t["status_totals"]))
    C.append(check("C2", "primary other:discourse", {"units": 81, "bytes": 8222},
                   tot([u for u in U if primary(u) == "other:discourse"])))
    C.append(check("C3", "other:* co-blockers; other:scope anywhere", [0, 0],
                   [sum(1 for u in U for c in co(u) if str(c).startswith("other:")),
                    sum(1 for u in U if primary(u) == "other:scope" or "other:scope" in co(u))]))
    leads = [byid[r["unit"]] for r in leadins]
    disc = [u for u in leads if primary(u) == "other:discourse"]
    rest = [u for u in leads if primary(u) != "other:discourse"]
    C.append(check("C4", "colon lead-ins (all; discourse-tagged; others)",
                   [{"units": 22, "bytes": 1352}, {"units": 9, "bytes": 506}, {"units": 13, "bytes": 846}],
                   [tot(leads), tot(disc), tot(rest)]))
    C.append(check("C4-tags", "primary tags of the 13 others (as the research names them)",
                   {"norms": 6, "quantities": 3, "defaults": 1, "counting": 1, "causation": 1, "attribution": 1},
                   dict(Counter(str(primary(u)) for u in rest))))
    C.append(check("C5", "restrictive connective units", {"units": 22, "bytes": 4196}, tot(restrictive)))
    C.append(check("C6", "This/These/Such units", {"units": 68, "bytes": 10981}, tot(tts)))
    C.append(check("C7", "bullet units", 141, sum(1 for x in L if x["item"] is not None)))
    pres = [u for u in U if u["id"].endswith(".presupposition")]
    C.append(check("C8", "split heading titles (all; discourse-tagged)", [{"units": 29, "bytes": 999}, {"units": 14, "bytes": 437}],
                   [tot(pres), tot([u for u in pres if primary(u) == "other:discourse"])]))

    def one(i):
        u = byid.get(i)
        return [nbytes(u), u["status"]] if u else None
    hc = [f"u0165.s0{k}" for k in range(1, 8)]
    C.append(check("C9", "named spans and statuses", {
        "u0164.s02": [22, "UNFORMALISED"], "u0164.s01": [68, "UNFORMALISED"], "u0173.s01": [263, "UNFORMALISED"],
        "u0165.s01-s07": [874, ["OPEN"]], "u0170.s01": 108, "u0046.s02": 41, "u0179.s03": 63, "u0047.s05": 95,
        "u0047.s06": 209, "u0062.s03": 16, "u0079": 64, "u0080.s01-s06": 1252, "u0072.s02": 84, "u0073.s01": 166,
        "u0073 block": 2475, "u0138.s02": 41, "u0139.s01": 50}, {
        "u0164.s02": one("u0164.s02"), "u0164.s01": one("u0164.s01"), "u0173.s01": one("u0173.s01"),
        "u0165.s01-s07": [span_of(byid, hc), sorted({byid[i]["status"] for i in hc})],
        "u0170.s01": one("u0170.s01")[0], "u0046.s02": one("u0046.s02")[0], "u0179.s03": one("u0179.s03")[0],
        "u0047.s05": one("u0047.s05")[0], "u0047.s06": one("u0047.s06")[0], "u0062.s03": one("u0062.s03")[0],
        "u0079": tot(block(U, "u0079"))["bytes"], "u0080.s01-s06": span_of(byid, [f"u0080.s0{k}" for k in range(1, 7)]),
        "u0072.s02": one("u0072.s02")[0], "u0073.s01": one("u0073.s01")[0], "u0073 block": tot(block(U, "u0073"))["bytes"],
        "u0138.s02": one("u0138.s02")[0], "u0139.s01": one("u0139.s01")[0]}))
    C.append(check("C10", "u0165.s07 end to u0173.s01 start", 4949, byid["u0173.s01"]["span"][0] - byid["u0165.s07"]["span"][1]))

    def lr(u):
        r = list_run(L, idx, u)
        return r[1] if r[0] == "ok" else r[1].split(":")[0]
    x = L[idx["u0164.s02"]]
    C.append(check("C11", "spec layout fixtures on the full pinned layout", {
        "F1": hc,
        "F1'''": {"u0166.s01 item": None, "in run": False},
        "L1": {"u0164.s02": {"midLine": True, "lead": True}, "u0165 items": [0] * 7},
        "F2": ["u0182.s01", "u0182.s02", "u0182.s04"],
        "F2'": ["u0073.s01", "u0073.s05", "u0073.s08"],
        "F2''": "NotALeadIn",
        "F10": ["u0073.s01", "u0073.s02", "u0073.s03", "u0073.s04"]}, {
        "F1": lr("u0164.s02"),
        "F1'''": {"u0166.s01 item": L[idx["u0166.s01"]]["item"], "in run": "u0166.s01" in run_units(0, L[idx["u0164.s02"] + 1:])},
        "L1": {"u0164.s02": {"midLine": x["midLine"], "lead": x["lead"]}, "u0165 items": [L[idx[i]]["item"] for i in hc]},
        "F2": lr("u0181.s02"),
        "F2'": lr("u0072.s02"),
        "F2''": lr("u0164.s01"),
        "F10": (lambda r: r[1] if r[0] == "ok" else r[1])(item_run(L, idx, "u0073.s01"))}))
    moves = [r for r in leadins if r.get("moves_now")]
    C.append(check("C12", "lead-ins that move now", [{"unit": "u0164.s02", "bytes": 22, "to": "OPEN"}],
                   [{"unit": r["unit"], "bytes": r["bytes"],
                     # weakest first; READINGS's place is an assumption (it only matters for mixed runs)
                     "to": min(r["items_status"], key=["OPEN", "READINGS", "CHECKED"].index)}
                    for r in moves]))
    return C


def udhr_checks(t, U, b, L, idx, byid, hs):
    C = []
    C.append(check("U1", "status totals", {"CHECKED": {"units": 18, "bytes": 1019}, "LABELLED": {"units": 34, "bytes": 535},
                                           "OPEN": {"units": 21, "bytes": 1870}, "READINGS": {"units": 11, "bytes": 1368},
                                           "UNFORMALISED": {"units": 46, "bytes": 6124}}, t["status_totals"]))
    C.append(check("U2", "primary other:discourse or naming scope", 0,
                   sum(1 for u in U if primary(u) == "other:discourse" or "scope" in str(primary(u)).lower())))

    def one(i):
        u = byid.get(i)
        return [nbytes(u), u["status"]] if u else None
    C.append(check("U3", "named spans", {"u111": [337, "READINGS"], "u112": [121, "OPEN"], "u114": [225, "READINGS"],
                                         "u052": [182, "READINGS"], "u019": [251, "UNFORMALISED"]},
                   {k: one(k) for k in ("u111", "u112", "u114", "u052", "u019")}))
    pre = [u for u in U if "preamble" in str(u.get("article", "")).lower()]
    C.append(check("U4", "preamble", {"units": 14, "bytes": 2004}, tot(pre)))
    h = next((h for h in hs if h["unit"] == "u109"), None)
    nxt = None
    if h:
        later = [g for g in hs if idx[g["unit"]] > idx["u109"]]
        stop = idx[later[0]["unit"]] if later else len(L)
        nxt = [L[k]["id"] for k in range(idx["u109"] + 1, stop)]
    C.append(check("U5", "F8 layout", {"u109": "## Article 29", "after": ["u110", "u111", "u112"]},
                   {"u109": h["line"] if h else None, "after": nxt}))
    return C


def main():
    root, outdir = Path(sys.argv[1]), Path(sys.argv[2])
    outdir.mkdir(parents=True, exist_ok=True)
    tc = tally(root, CONSTITUTION, "claude-constitution run-20261012T1800Z")
    tu = tally(root, UDHR, "udhr run-20261012T1800Z")
    checks = constitution_checks(*tc) + udhr_checks(tu[0], tu[1], tu[2], tu[3], tu[4], tu[5], tu[8])
    (outdir / "scope-tally.json").write_text(json.dumps({"constitution": tc[0], "udhr": tu[0]}, indent=1, ensure_ascii=False) + "\n")
    (outdir / "checks.json").write_text(json.dumps(checks, indent=1, ensure_ascii=False) + "\n")
    for c in checks:
        print(c["id"], c["result"], "" if c["result"] == "PASS" else json.dumps(c["measured"], ensure_ascii=False)[:600])


if __name__ == "__main__":
    main()
