"""Per-item OPAQUE predicates: things the VE formalisation needs but VE cannot
express (numeric comparison, string globbing, datetime arithmetic). Each hook is
trusted adapter code outside VE and is counted against VE coverage in results.

A hook receives (world, request, factbase, constants) and returns
{predicate: set of tuples of VE local IDs}. Use ``factbase`` domains/constants
to look up the local IDs the fixed encoder already assigned.
"""
from __future__ import annotations

OPAQUE: dict = {}
OPAQUE_PREDICATES: dict[str, set] = {"cedar": set(), "k8s": set(), "iam": set(), "alloy": set()}


def _num_pred(attr: str, test):
    """Owners whose long-valued attribute ``attr`` satisfies ``test`` (Cedar: absent -> no row)."""
    def hook(fb):
        return {(owner,) for (owner, a), v in fb.raw.items()
                if a == attr and isinstance(v, int) and not isinstance(v, bool) and test(v)}
    return hook


# c08 (Cedar 4a): principal.jobLevel >= 5
OPAQUE["c08_cit_4a"] = lambda w, r, fb, c: {"joblevel_ge_5": _num_pred("joblevel", lambda v: v >= 5)(fb)}
# c12 (Cedar 5b): context.photo.filesize_mb <= 1 / <= 100
OPAQUE["c12_cit_5b"] = lambda w, r, fb, c: {"filesize_le_1": _num_pred("filesize_mb", lambda v: v <= 1)(fb),
                                            "filesize_le_100": _num_pred("filesize_mb", lambda v: v <= 100)(fb)}
OPAQUE_PREDICATES["cedar"] |= {"joblevel_ge_5", "filesize_le_1", "filesize_le_100"}


# ---- c19 (Cedar streaming_service): datetime/duration extension, outside VE --------------
import re as _re
from datetime import datetime as _dt, timezone as _tz, timedelta as _td


def _datetime_ms(s: str):
    m = _re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})(?:T(\d{2}):(\d{2}):(\d{2})(?:\.(\d{3}))?(Z|[+-]\d{4}))?", s)
    if not m:
        return None
    y, mo, d, h, mi, se, ms, tz = m.groups()
    t = _dt(int(y), int(mo), int(d), int(h or 0), int(mi or 0), int(se or 0), tzinfo=_tz.utc)
    if tz and tz != "Z":
        sign = 1 if tz[0] == "+" else -1
        t -= sign * _td(hours=int(tz[1:3]), minutes=int(tz[3:5]))
    return int(t.timestamp() * 1000) + int(ms or 0)


def _duration_ms(s: str):
    m = _re.fullmatch(r"(-?)((?:\d+(?:d|h|ms|m|s))+)", s)
    if not m:
        return None
    unit = {"d": 86400000, "h": 3600000, "m": 60000, "s": 1000, "ms": 1}
    total = sum(int(n) * unit[u] for n, u in _re.findall(r"(\d+)(ms|d|h|m|s)", m.group(2)))
    return -total if m.group(1) else total


def _ext(v, fn):
    if isinstance(v, dict) and "__extn" in v and v["__extn"].get("fn") == fn:
        return (_datetime_ms if fn == "datetime" else _duration_ms)(v["__extn"]["arg"])
    return None


def _streaming(world, request, fb, consts):
    ctx = request.get("context", {})
    now_rec = ctx.get("now") if isinstance(ctx.get("now"), dict) and "__extn" not in ctx.get("now", {}) else None
    now = _ext(now_rec.get("datetime"), "datetime") if now_rec else None
    off = _ext(now_rec.get("localTimeOffset"), "duration") if now_rec else None
    out = {k: set() for k in ("now_lt_release", "now_ge_release", "now_ge_release_minus_24h",
                              "oscar_window", "outside_waking_hours")}
    for e in world["entities"]:
        rel = _ext(e["attrs"].get("releaseDate"), "datetime")
        if now is None or rel is None:
            continue
        me = fb.E(e["uid"])
        out["now_lt_release" if now < rel else "now_ge_release"].add((me,))
        if now >= rel - 24 * 3600000:
            out["now_ge_release_minus_24h"].add((me,))
    c = consts["context"]
    if now is not None and _datetime_ms("2025-02-02T19:00:00-0500") <= now < _datetime_ms("2025-03-02T19:00:00-0500"):
        out["oscar_window"].add((c,))
    if now is not None and off is not None:
        t = (now + off) % 86400000
        if not (6 * 3600000 <= t <= 21 * 3600000):
            out["outside_waking_hours"].add((c,))
    return out


OPAQUE["c19_streaming"] = _streaming
OPAQUE_PREDICATES["cedar"] |= {"now_lt_release", "now_ge_release", "now_ge_release_minus_24h", "oscar_window", "outside_waking_hours"}
