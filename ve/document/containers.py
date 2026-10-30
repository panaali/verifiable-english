"""The unit roles and containers both load paths build from a document's units: the soft and rights
sources, the free norms, the reading routes and plan (moved from `ve/document.py`, AR-16a)."""
from __future__ import annotations

from ..environment import listed_profiles
from ..errors import VEError
from ..readings import plan_choices, s1_content_kind
from .source import _RIGHTS_KINDS, _environment, _parts, _parts_prefix


def _wire_unit(unit):
    """A compiled unit in the reports wire form that Python and Lean both decode.

    Report content is already a wire tree; a compiled formula is the bare AST
    and goes back into its ``{"ast": ...}`` wrapper (fence text included, since
    the Lean route decodes no surface text).
    """
    content = unit["content"]
    if content is not None and not (type(content) is dict and set(content) & {"report", "assessment", "negated"}):
        content = {"ast": content}
    return {"id": unit["id"], "span": unit["span"], "kind": unit["kind"], "meaning": unit["meaning"],
            "support": unit["support"], **({"content": content} if content is not None else {})}


def _soft_contents(units, exclude=frozenset()):
    """The soft source's norm objects: the content of each unit of kind `norm` with norm content, a `MIXED` unit's
    parts included, over the units `_parts` yields before its first fault (Lean `Service.Document.softSourceNorms`)."""
    return [u.get("content") for u in _parts_prefix(units)
            if type(u) is dict and u.get("kind") == "norm" and u.get("id") not in exclude
            and type(u.get("content")) is dict and "norm" in u["content"]]


def _readings_routes(env, reading_sets):
    """(companions, s1_content) of a document's reading sets under `readings@1`: whether some reading carries its
    own vocabulary, so Lean splits the document (readings-defaults RD-4b, 1.9), and whether some set is
    content-bearing (composition-s1.md 1.2), which a split document always is."""
    from ..readings_components import has_companions
    companions = "readings@1" in env.profiles and has_companions(reading_sets)
    s1_content = "readings@1" in env.profiles and type(reading_sets) is list and (companions or any(
        type(s) is dict and type(s.get("readings")) is list and any(
            type(r) is dict and s1_content_kind(r.get("content")) in
            {"norm", "right", "right_lines", "limitation"} for r in s["readings"])
        for s in reading_sets))
    return companions, s1_content


def _s1_attached(environment_data, meta):
    """Under `readings@1`, the fixed units attached to an open content-bearing set (composition-s1.md 1.3): they
    belong to that set's candidates' documents, and the lower route checks `free D` without them (4.1). A
    document S1 cannot decode is left whole here; the readings route reports its diagnostic."""
    if "readings@1" not in listed_profiles(environment_data):
        return frozenset()
    sets = meta.get("reading_sets", [])
    if type(sets) is not list or not any(
            type(s) is dict and type(s.get("readings")) is list and any(
                type(r) is dict and s1_content_kind(r.get("content")) in {"norm", "right", "right_lines", "limitation"}
                for r in s["readings"]) for s in sets):
        return frozenset()
    from ..readings_s1 import Document as S1Document
    try:
        units = [{"id": u["id"], "kind": u.get("kind"), "content": u.get("content")}
                 for u, _ in _parts(meta.get("units", []))]
        # Attachment reads names only (1.3), never the frame, which under norm-defaults@0 is Lean's.
        attached = S1Document(None, {"units": units, "reading_sets": sets}).attached()
    except (VEError, KeyError, TypeError, ValueError, AttributeError, IndexError):
        return frozenset()
    return frozenset(u for u, owners in attached.items() if owners)


def _free_norms(units, active, attached):
    """`selected_norms`, for both of `load_document`'s paths: the rules of the free norm document are the units of
    kind `norm` with norm content, under no active reading set and attached to no open set. A quoted unit, or one
    under an active set, is checked alone (`_check_quoted`); under `readings@1` an attached unit is checked in its
    set's candidates' documents (S1 1.3). Lean's document mode reads the same roles (`Service.Document.freeNorms`,
    over `Norms.Admission.normRole`)."""
    held = {r["unit"] for r in active}
    return [u["content"] for u in units if u["kind"] == "norm" and type(u["content"]) is dict
            and "norm" in u["content"] and u["id"] not in held and u["id"] not in attached]


def _defaults_environment(env):
    """The environment of the free norm-defaults document. Under `readings@1` it is the lower route's, read with
    the profile stripped as Lean's readings route hands every other kind down (`Readings.Run.runLower`): the W2
    route of a non-content-bearing set, and the norm-defaults document beside content-bearing sets."""
    if "readings@1" not in env.profiles:
        return env
    lowered = env.to_dict()
    lowered["profiles"] = [p for p in lowered["profiles"] if p != "readings@1"]
    return _environment(lowered)


def _reading_plan(active, couplings):
    """The reading plan for both paths: with couplings over every active set (a coupling may name an authored
    one), else over the open sets."""
    return plan_choices(active if couplings else [r for r in active if r["status"] == "open"],
                        couplings=couplings)


def _rights_block(content):
    """The rights block a checked content holds (`right`, `right_lines`,
    `limitation` or `bar`), else None."""
    if type(content) is dict and len(content) == 1 and next(iter(content)) in _RIGHTS_KINDS:
        return next(iter(content))
    return None


def _content_bearing(doc):
    """Whether the document has a content-bearing reading set (composition-s1.md 1.2); a document whose readings
    carry their own vocabulary has one (readings-defaults 1.9)."""
    if doc.get("readings_components") is not None:
        return True
    row = doc.get("readings_s1")
    return row is not None and row.get("content_bearing") is True


def _content_environment(env, formula_env, kind):
    """`content_env` of a unit of either path: under `rights@0` a rights block's own environment for a rights kind,
    else the environment its formulas and norms are read in (the rights route's `E″′`)."""
    return env if "rights@0" in env.profiles and type(kind) is str and kind in _RIGHTS_KINDS else formula_env


def _rights_units(units, exclude=frozenset()):
    """The rights source of a document's units: the unit ids, then every rights or norm content."""
    ids = [u.get("id") for u, _ in _parts(units) if type(u) is dict and type(u.get("id")) is str]
    return [{"source_units": ids}] + [u["content"] for u, _ in _parts(units) if _in_rights_source(u, exclude)]


def _in_rights_source(unit, exclude=frozenset()):
    """A unit of the rights source (Lean `Service.Document.rightsSourceUnit`): object content under a rights kind or
    `norm`, outside `exclude` (unit ids; an id that is not a string names no unit, and its unit's own check refuses
    it)."""
    uid = unit.get("id")
    return (type(unit.get("content")) is dict and not (type(uid) is str and uid in exclude) and
            unit.get("kind") in (*_RIGHTS_KINDS, "norm"))
