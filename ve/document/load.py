"""`load_document`: Lean's `document` answer when it decides, else Python's own loader, the retained path
(moved from `ve/document.py`, AR-16a)."""
from __future__ import annotations

import re
from pathlib import Path

from ..admission import _check_kind, token
from ..ast import formula_from_data, formula_to_data
from ..backends.lean_service import CheckerUnavailable
from ..environment import listed_profiles
from ..errors import UnsupportedProfile, VEError
from ..identity import meaning_id, source_id
from ..openterms import validate_open_terms
from ..readings import active_reading_sets, validate_couplings, validate_narrowings, validate_reading_sets
from .source import (STATUSES, SUPPORTS, _RIGHTS_KINDS, _document_id, _english_fences, _environment,
                     _no_lone_surrogate, _parts, _parts_prefix, _split, base_environment)
from .containers import (_content_environment, _defaults_environment, _free_norms, _in_rights_source, _reading_plan,
                         _readings_routes, _rights_units, _s1_attached, _soft_contents, _wire_unit)
from .lean import _lean_answer, _lean_document


def load_document(path: str | Path):
    """Load and check a document. A `ve-document@1` document is Lean's (`document` mode, batch 16b): Lean decides
    every check, the unit statuses, the identities and the coverage, and Python builds the document from that
    answer (`_lean_document`); only a document the mode answers `CheckerUnavailable` or `ResourceLimit` for (a
    profile, content or route it cannot decide yet, docs/lean-first/b16b/DELTA.md) takes Python's own path. A
    `ve-document@2` document's admission is Lean's (`ve_discourse_route` on the same bytes,
    docs/spec/discourse.md 3.4): a document Lean rejects raises Lean's diagnostic before any Python check runs,
    and a document Lean admits that Python cannot load is `CheckerUnavailable`, never a Python-only verdict."""
    return _load(Path(path), admit=False)


def _load(path: Path, *, admit: bool):
    """`load_document`; `admit`: also `_report`'s claim-graph checks, which `check_document` asks Lean for."""
    raw = path.read_bytes()
    from ..discourse import is_discourse_text, lean_admission, rejection, unavailable_report
    if not is_discourse_text(raw):
        prepared = {}
        row = _lean_answer(raw, admit, path.parent, prepared)
        if row is None:
            return _load_document(raw, path, None)
        return _lean_document(raw, path, row, admitted=admit, prepared=prepared)
    lean = lean_admission(raw, Path(path).parent)
    if lean["status"] == "error":
        raise rejection(lean)
    try:
        return _load_document(raw, path, lean)
    except CheckerUnavailable:
        raise
    except Exception as exc:
        raise unavailable_report(exc) from exc


def _meaning(value, open_names, *, reports=False):
    if value == "specified":
        return "specified"
    if type(value) is not dict or len(value) != 1:
        raise VEError("invalid meaning status")
    status, detail = next(iter(value.items()))
    if status == "contextual" and type(detail) is str and detail:
        return status
    # Each name is declared or, under reports@0, shaped as a generated one; the
    # reports layer then checks it against the names the document generates.
    if status == "open" and type(detail) is list and detail and all(
            type(x) is str and (x in open_names or reports and re.fullmatch(r"reports__(?:may|probably)__[1-9][0-9]*", x))
            for x in detail):
        return status
    if status == "unformalised" and token(detail):
        return status
    raise VEError("invalid meaning status")


def _quantity_content(env, unit, content, fences):
    """W6 content: every statement is an annotated quantity admitted before
    erasure. Legacy `ast` content is dimensionless source input; a fence goes
    through the whole-grammar all-derivations gate (`parse_w6_sentence`)."""
    from ..units import elaborate_quantity, quantity_meaning_id
    if "quantity" in content:
        payload = content["quantity"]
    elif "ast" in content:
        payload = {"format": "ve-quantity@1", "formula": content["ast"]}
    elif "fence" in content:
        if content["fence"] != unit["id"]:
            raise VEError("unit fence must match its id")
        if unit["id"] not in fences:
            raise VEError("missing VE fence")
        if unit.get("surface") not in ("english", "strict"):
            raise VEError("fenced content needs english or strict surface")
        from ..surface.time import parse_w6_sentence
        payload = parse_w6_sentence(env, fences[unit["id"]].strip(), unit["surface"])
    else:
        raise VEError("unit content must bind one formula or norm")
    canonical, _ = elaborate_quantity(env, payload)
    return canonical, quantity_meaning_id(env, canonical)


def _content(env, unit, fences, *, formula_env=None, rights=False, senses=None, rule_result=None):
    formula_env = env if formula_env is None else formula_env
    content = unit.get("content")
    if content is None:
        return None
    if (rights and type(content) is dict and set(content) == {"norm", "cites"} and
            unit.get("kind") == "norm"):
        # 3.2: a norm unit outside rights may carry `narrows:<line>` citations,
        # which the rights document validates; the meaning binds them too.
        canonical, _ = _content(env, {**unit, "content": {"norm": content["norm"]}}, fences,
                                formula_env=formula_env, senses=senses, rule_result=rule_result)
        from ..readings import rights_meaning_id
        canonical = {**canonical, "cites": content["cites"]}
        return canonical, rights_meaning_id(env, canonical)
    if type(content) is not dict or len(content) != 1:
        raise VEError("unit content must bind one formula or norm")
    if env.unit_schema is not None and "norm" not in content:
        return _quantity_content(env, unit, content, fences)
    if "quantity" in content:
        raise UnsupportedProfile("UnsupportedProfile: quantity content requires ve-units@1")
    if "reports@0" in env.profiles and set(content) & {"report", "assessment", "negated"}:
        return content, None  # The reports decoder binds its identity after all declarations.
    if "norm" in content:
        if "soft-norms@0" in env.profiles:
            from ..softnorms import batch_rule, decode_rule, soft_digest
            rule = (batch_rule(env, content, rule_result) if rule_result is not None
                    else decode_rule(env, content))
            canonical = rule.to_dict()
            mid = soft_digest(f"ve-meaning-{env.identity_version}\n",
                              {"environment_id": env.environment_id, "ast": canonical})
            return canonical, mid
        from ..norms import NormDocument
        if "norms@0" not in env.profiles:
            raise UnsupportedProfile("UnsupportedProfile: norms@0 is required")
        rule = NormDocument._decode(content)
        return rule.to_dict(), None
    if next(iter(content)) in _RIGHTS_KINDS:
        if "rights@0" not in env.profiles:
            raise UnsupportedProfile("UnsupportedProfile: rights@0 is required")
        from ..readings import rights_meaning_id
        return content, rights_meaning_id(env, content)
    if "ast" in content:
        formula = formula_from_data(formula_env, content["ast"])
        return formula_to_data(formula_env, formula), meaning_id(formula_env, formula)
    if "fence" not in content or content["fence"] != unit["id"]:
        raise VEError("unit fence must match its id")
    if unit["id"] not in fences:
        raise VEError("missing VE fence")
    text = fences[unit["id"]]
    if senses is not None and unit.get("surface") == "english":
        # RD-8: Lean read the fence (`ve.senses_document`); a preamble line or an open unit has no formula.
        data = senses.formulas.get(unit["id"])
        if data is None:
            return None, None
        formula = formula_from_data(formula_env, data)
        return formula_to_data(formula_env, formula), meaning_id(formula_env, formula)
    if unit.get("surface") == "english":
        from ..english import parse_english
        document = parse_english(formula_env, text)
    elif unit.get("surface") == "strict":
        from ..parser import parse
        document = parse(formula_env, text)
    else:
        raise VEError("fenced content needs english or strict surface")
    if len(document.formulas) != 1:
        raise VEError("each VE fence must contain exactly one sentence")
    formula = document.formulas[0]
    return formula_to_data(formula_env, formula), meaning_id(formula_env, formula)


def _load_document(raw: bytes, path: str | Path, lean):
    """Python's own path: a `ve-document@2` document after Lean's discourse admission (`lean`), and a
    `ve-document@1` document Lean's `document` mode cannot decide yet (`_lean_answer`)."""
    meta, source, fences = _split(raw)
    _no_lone_surrogate(meta)
    if not source:
        raise VEError("document source is empty")
    if type(meta.get("environment")) is not dict:
        raise VEError("document needs an embedded environment")
    from ..discourse import validate_discourse
    environment_data = base_environment(meta)
    profiles = listed_profiles(environment_data)
    if "judgments@0" in profiles:
        # Its statuses are Lean's (`Service.Document.check`, docs/spec/judgment-terms.md 8.1); this loader has none.
        raise CheckerUnavailable("CheckerUnavailable: judgments@0 documents are checked by Lean's document mode")
    rights_enabled = "rights@0" in profiles
    soft_enabled = "soft-norms@0" in profiles
    defaults_enabled = "norm-defaults@0" in profiles
    if defaults_enabled and rights_enabled:
        # The rights document route is checked by Lean, whose norm-defaults
        # route has no admission kind for it yet (rd-9-soft-chain 3.11 row 7).
        raise UnsupportedProfile("UnsupportedProfile: norm-defaults@0 documents on the rights route await the "
                                 "Lean route")
    attached = _s1_attached(environment_data, meta)
    if soft_enabled and not rights_enabled:
        from ..softnorms import check_soft_source
        if type(meta.get("units")) is list:
            # The environment and the norm units are one soft source (8).
            check_soft_source(environment_data, _soft_contents(meta["units"], attached),
                              layers=frozenset(p for p in ("readings@1", "norm-defaults@0") if p in profiles))
    env = _environment(environment_data)
    if "reports@0" not in env.profiles and set(meta) & {"contexts", "assessments", "bridges", "scoped"}:
        raise VEError("unknown document metadata")
    open_names = validate_open_terms(env, meta.get("open_terms", []))
    units = meta.get("units")
    if type(units) is not list or not units:
        raise VEError("document needs units")
    soft_document = None
    rights_document = None
    formula_env = env
    if rights_enabled:
        from ..rights import RightsDocument
        # Citations name source units (3.2): the rights source carries every unit id.
        ids = [u.get("id") for u, _ in _parts(units) if type(u) is dict and type(u.get("id")) is str]
        rights_document = RightsDocument(env, _rights_units(units, attached),
                                         open_predicates=open_names)
        soft_document = rights_document.soft_document
        formula_env = soft_document.extended_env
        open_names = (set(open_names) | formula_env.decision_names |
                      set(rights_document.limitation_names.values()) |
                      set(rights_document.condition_names.values()) |
                      set(rights_document.bar_names.values()))
    elif soft_enabled:
        from ..softnorms import SoftNormDocument
        soft_document = SoftNormDocument(env, _soft_contents(units, attached))
        formula_env = soft_document.extended_env
        open_names = set(open_names) | soft_document.extended_env.decision_names
    senses = None
    if "senses" in meta:
        # RD-8: Lean reads the English fences; their units' environment is Lean's projected one.
        from ..senses_document import read_senses
        if (meta["format"] != "ve-document@1" or env.unit_schema is not None
                or set(env.profiles) & {"soft-norms@0", "rights@0", "reports@0", "norm-defaults@0", "readings@1"}):
            raise UnsupportedProfile("UnsupportedProfile: senses are read in ve-document@1 documents without the soft-norms@0, "
                          "rights@0, reports@0, norm-defaults@0, readings@1 and quantity routes")
        senses = read_senses(env, meta["senses"], _english_fences(units, fences), Path(path).parent,
                             meta.get("reading_sets", []))
        formula_env = senses.environment
    rule_results = {}
    if soft_enabled:
        from ..softnorms import check_rule_batch
        # The ordinary unit loop below reports a structural fault in source
        # order, after any earlier per-rule Lean outcome.
        authored = [(raw, {"norm": raw["content"]["norm"]}) for raw in _parts_prefix(units)
                    if type(raw.get("content")) is dict and "norm" in raw["content"]]
        if authored:
            outcomes = check_rule_batch(formula_env, (content for _, content in authored))
            rule_results = {id(raw): outcome for (raw, _), outcome in zip(authored, outcomes, strict=True)}
    compiled = []
    unit_ids = set()
    cursor = 0
    parents = [u.get("id") for u in units if type(u) is dict and u.get("status") == "MIXED"]
    if not all(token(uid) for uid in parents):
        raise VEError("invalid MIXED unit id")
    if len(set(parents)) != len(parents):
        raise VEError("duplicate MIXED unit id")
    parent_ids = set(parents)
    quoted_norms = []
    for unit, parent_id in _parts(units):
        required = {"id", "span", "kind", "meaning", "support"}
        if (type(unit) is not dict or not required <= set(unit)
                or set(unit) - required - {"content", "surface", "meaning_id", "status"}):
            raise VEError("invalid unit schema")
        uid = unit["id"]
        if not token(uid) or uid in unit_ids or uid in parent_ids:
            raise VEError("duplicate or invalid unit id")
        unit_ids.add(uid)
        span = unit["span"]
        if (type(span) is not list or len(span) != 2 or any(type(x) is not int for x in span)
                or span[0] != cursor or span[1] <= cursor or span[1] > len(source)):
            raise VEError("unit spans must partition every source byte in order")
        try:
            source[span[0]:span[1]].decode("utf-8")
        except UnicodeDecodeError as exc:
            raise VEError("unit span cuts a UTF-8 character") from exc
        cursor = span[1]
        kind = (unit["kind"] if rights_enabled and unit["kind"] in _RIGHTS_KINDS else
                _check_kind(unit["kind"], reports="reports@0" in env.profiles))
        status = _meaning(unit["meaning"], open_names, reports="reports@0" in env.profiles)
        if type(unit["support"]) is not str or unit["support"] not in SUPPORTS:
            raise VEError("invalid support")
        content_env = _content_environment(env, formula_env, kind)
        content, mid = (_content(content_env, unit, fences, formula_env=formula_env,
                                 rights=rights_enabled, senses=senses, rule_result=rule_results.get(id(unit)))
                        if unit.get("content") is not None else (None, None))
        is_norm = type(content) is dict and "norm" in content
        if is_norm:
            from ..norms import norm_meaning_id, NormDocument
            from ..admission import _quoted
            if _quoted(kind):
                quoted_norms.append(content)
            elif kind != "norm":
                raise VEError("norm content requires a norm or quoted kind")
            if not soft_enabled:
                mid = norm_meaning_id(env, NormDocument._decode(content))
        if (type(kind) is list and kind[0] == "unformalised" and
                unit["meaning"] != {"unformalised": kind[1]}):
            raise VEError(f"InvalidInput: unformalised kind reason does not match meaning of {uid}")
        if status == "unformalised" and content is not None:
            raise VEError("unformalised unit cannot assert content")
        if "meaning_id" in unit and mid is not None and unit["meaning_id"] != mid:
            raise VEError("unit meaning id does not match content")
        explicit_status = unit.get("status")
        if explicit_status is not None and (type(explicit_status) is not str or explicit_status not in STATUSES):
            raise VEError("invalid unit status")
        inferred_status = ("CHECKED" if content is not None and status == "specified" else
                           "OPEN" if status == "open" else
                           "UNFORMALISED" if status == "unformalised" else "LABELLED")
        compiled.append({"id": uid, "span": span, "kind": unit["kind"], "meaning": unit["meaning"],
                         "support": unit["support"], "source": source[span[0]:span[1]].decode("utf-8"),
                         "content": content, "meaning_id": mid, "status": inferred_status,
                         "explicit_status": explicit_status,
                         **({"parent_id": parent_id} if parent_id is not None else {})})
    if cursor != len(source):
        raise VEError("unit spans do not partition all source bytes")
    reports = None
    if "reports@0" in env.profiles:
        from ..reports import ReportsDocument
        if meta.get("reading_sets") or meta.get("lemmas"):
            raise VEError("reports readings and lemma replay await the Lean route")
        reported = [u for u in compiled if type(u["content"]) is dict
                    and set(u["content"]) & {"report", "assessment", "negated"}]
        reports = ReportsDocument(env, meta.get("contexts", []), meta.get("assessments", []),
                                  [_wire_unit(u) for u in compiled], bridges=meta.get("bridges", []),
                                  scoped=meta.get("scoped", []), open_terms=sorted(open_names))
        for u in reported:
            u["meaning_id"] = reports.meaning_id(u["content"])
            original = next(raw for raw, _ in _parts(units) if raw["id"] == u["id"])
            if "meaning_id" in original and original["meaning_id"] != u["meaning_id"]:
                raise VEError("unit meaning id does not match content")
        # 6: every unit's status is the meet of its meaning's and every result
        # nested in its content and kind (an assessment node at any depth is OPEN,
        # an act outside the slice anywhere in its kind LABELLED, an unformalised
        # node anywhere in its kind UNFORMALISED).
        for u, wire in zip(compiled, reports.units):
            u["status"] = reports.unit_status(wire)
    from ..norms import NormDocument
    if set(fences) != {u["id"] for u, _ in _parts(units) if type(u.get("content")) is dict
                       and u["content"].get("fence") == u["id"]}:
        raise VEError("unbound VE fence")
    reading_sets = meta.get("reading_sets", [])
    companions, s1_content = _readings_routes(env, reading_sets)
    validate_reading_sets(env if rights_enabled or s1_content else formula_env,
                          reading_sets, unit_ids, source=source,
                          unit_spans={u["id"]: u["span"] for u in compiled},
                          lean_replay=s1_content)
    readings_s1 = None
    readings_components = None
    if companions:
        # readings-defaults 1.9 and 4.5 (RD-4b): Lean splits the document and checks each case by itself; its
        # elaboration, validation and the product's conflict answer are relayed, bound to the request.
        from ..readings_components import load as load_components
        readings_components = load_components(env.to_dict(), compiled, reading_sets,
                                              couplings=meta.get("couplings", []),
                                              narrowings=meta.get("narrowings", []))
    elif s1_content:
        from ..readings_route import validate as validate_s1
        readings_s1 = validate_s1(env.to_dict(), compiled, reading_sets)
    active = active_reading_sets(reading_sets)
    couplings = meta.get("couplings", [])
    validate_couplings(env, couplings, reading_sets, unit_ids)
    units_by_id = {u["id"]: u for u in compiled}
    for reading_set in active:
        unit = units_by_id[reading_set["unit"]]
        unit["status"] = ("CHECKED" if reading_set["status"] == "authored"
                          and all(c["kind"] == "asserted" and c["content"] is not None
                                  for c in reading_set["readings"]) else "OPEN")
    if rights_document is not None:
        rights = rights_document
        statuses = rights.elaborated["unit_open"]
        source_ids = [u["id"] for u, _ in _parts(units) if _in_rights_source(u, attached)]
        source_status = dict(zip(source_ids, statuses[1:], strict=True))
        for unit in compiled:
            if unit["status"] == "CHECKED" and source_status.get(unit["id"], False):
                unit["status"] = "OPEN"
    if meta["format"] == "ve-document@1":
        for unit in compiled:
            if unit.pop("explicit_status") not in (None, unit["status"]):
                raise VEError("unit status contradicts content, meaning, or active reading set")
    reading_units = {r["unit"] for r in active}
    quoted_norms.extend(u["content"] for u in compiled if u["kind"] == "norm" and u["id"] in reading_units
                        and type(u["content"]) is dict and "norm" in u["content"])
    if quoted_norms:
        if not soft_enabled:
            from ..norm_admission import _check_quoted
            for content in quoted_norms:
                _check_quoted(env, content)
        # Soft quoted norms were checked as single units by decode_rule above;
        # they are not members of the active soft document or its layer premises.
    selected_norms = _free_norms(compiled, active, attached)
    norms = (NormDocument(env, selected_norms)
             if not soft_enabled and (selected_norms or any(d.regulated is not None for d in env.predicates.values()))
             else None)
    norm_defaults = None
    if defaults_enabled and not soft_enabled:
        # norm-defaults 2.3: the layers are those of `fill U`, over E‴ with Fill_T. On the soft chain Lean's
        # layered route owns them (rd-9-soft-chain 3.8): no W1 container is built over soft units.
        from ..norm_defaults import UnspecifiedDocument, validate_completions
        norm_defaults = UnspecifiedDocument(_defaults_environment(env), selected_norms)
        validate_completions(norm_defaults, meta.get("completions", {}), unit_ids)
        norms = None
    if "lemmas" in meta and type(meta["lemmas"]) is not list:
        raise VEError("lemmas must be a list")
    for u in compiled:
        if (u["kind"] == "asserted" and u["content"] is None
                and not any(r["unit"] == u["id"] for r in reading_sets)):
            raise VEError("asserted unit needs content or a reading set")
    narrowings = meta.get("narrowings", [])
    validate_narrowings(narrowings, reading_sets, unit_ids)
    readings_s2 = None
    if s1_content and not companions:
        from ..readings_route import elaborate as elaborate_s2
        readings_s2 = elaborate_s2(env.to_dict(), compiled, reading_sets,
                                    couplings=couplings, narrowings=narrowings)
    weights = meta.get("weights", [])
    if type(weights) is not list or any(type(w) is not dict or set(w) != {"set", "by", "values"} for w in weights):
        raise VEError("invalid removable reading weights")
    sid = source_id(source, env)
    document_id = _document_id(meta, source, fences)
    doc = {"meta": meta, "environment": env, "source": source, "source_id": sid,
           "document_id": document_id, "directory": Path(path).parent,
           "units": compiled, "norms": norms, "soft_document": soft_document,
           "norm_defaults": norm_defaults, "senses": senses,
           "reports": reports, "rights_document": rights_document,
           "readings_s1": readings_s1,
           "readings_s2": readings_s2,
           "readings_components": readings_components,
           "reading_plan": _reading_plan(active, couplings)}
    if meta["format"] == "ve-document@2":
        doc["discourse"] = validate_discourse(doc, lean)
        for unit in compiled:
            if unit.pop("explicit_status") not in (None, unit["status"]):
                raise VEError("unit status contradicts content, meaning, or active reading set")
    return doc
