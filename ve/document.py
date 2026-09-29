"""ve-document@1: byte-partitioned source, reviewed metadata and P0 admission.

Front matter is JSON between two ``---`` lines. The source is every body byte
outside ``ve`` fences; unit spans are offsets into that exact byte sequence.
``ve <unit-id>`` fences supply an optional English or strict formula for a
unit. The JSON front matter may instead bind a formula AST or a W1 norm.
"""
from __future__ import annotations

import json
import hashlib
import re
from pathlib import Path

from .assurance import semantic_entry
from .admission import _check_kind, admit_document, token
from .ast import Document, formula_from_data, formula_to_data
from .environment import Environment
from .errors import VEError
from .identity import meaning_id, source_id
from .openterms import validate_open_terms
from .readings import (active_reading_sets, check_readings, plan_choices,
                       validate_couplings, validate_narrowings, validate_reading_sets)
from .wire import digest
from .vacuity import premise_status

MAX_DOCUMENT_BYTES = 4_000_000
SUPPORTS = {"assumption", "certificate", "observation", "calculation", "statistical",
            "testimony", "adapter", "none"}
STATUSES = {"CHECKED", "OPEN", "LABELLED", "UNFORMALISED"}


def _body(body: bytes):
    source = bytearray()
    fences = {}
    lines = body.splitlines(keepends=True)
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith(b"```ve "):
            try:
                uid = line[6:].strip().decode("ascii")
            except UnicodeDecodeError as exc:
                raise VEError("invalid VE fence name") from exc
            if not token(uid) or uid in fences:
                raise VEError("invalid or duplicate VE fence")
            i += 1
            content = bytearray()
            while i < len(lines) and lines[i].strip() != b"```":
                content.extend(lines[i])
                i += 1
            if i == len(lines):
                raise VEError("unclosed VE fence")
            try:
                fences[uid] = content.decode("utf-8")
            except UnicodeDecodeError as exc:
                raise VEError("VE fence is not UTF-8") from exc
        else:
            source.extend(line)
        i += 1
    return bytes(source), fences


def _split(raw: bytes):
    if len(raw) > MAX_DOCUMENT_BYTES:
        raise VEError("document byte budget exceeded")
    if not raw.startswith(b"---\n"):
        raise VEError("ve-document@1 needs JSON front matter")
    boundary = raw.find(b"\n---\n", 4)
    if boundary < 0:
        raise VEError("unclosed JSON front matter")
    try:
        meta = json.loads(raw[4:boundary].decode("utf-8"))
    except (ValueError, UnicodeError) as exc:
        raise VEError("invalid JSON front matter") from exc
    if type(meta) is not dict or meta.get("format") != "ve-document@1":
        raise VEError("unsupported document format")
    allowed = {"format", "environment", "units", "open_terms", "reading_sets",
               "narrowings", "couplings", "weights", "graph", "lemmas",
               "contexts", "assessments", "bridges", "scoped"}
    if set(meta) - allowed:
        raise VEError("unknown document metadata")
    if "couplings" in meta and "rights@0" not in meta.get("environment", {}).get("profiles", []):
        raise VEError("UnsupportedProfile: rights@0 is required for couplings")
    return meta, *_body(raw[boundary + 5:])


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
    from .units import elaborate_quantity, quantity_meaning_id
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
        from .surface.time import parse_w6_sentence
        payload = parse_w6_sentence(env, fences[unit["id"]].strip(), unit["surface"])
    else:
        raise VEError("unit content must bind one formula or norm")
    canonical, _ = elaborate_quantity(env, payload)
    return canonical, quantity_meaning_id(env, canonical)


def _content(env, unit, fences, *, formula_env=None, rights=False):
    formula_env = env if formula_env is None else formula_env
    content = unit.get("content")
    if content is None:
        return None
    if (rights and type(content) is dict and set(content) == {"norm", "cites"} and
            unit.get("kind") == "norm"):
        # 3.2: a norm unit outside rights may carry `narrows:<line>` citations,
        # which the rights document validates; the meaning binds them too.
        canonical, _ = _content(env, {**unit, "content": {"norm": content["norm"]}}, fences,
                                formula_env=formula_env)
        from .readings import rights_meaning_id
        canonical = {**canonical, "cites": content["cites"]}
        return canonical, rights_meaning_id(env, canonical)
    if type(content) is not dict or len(content) != 1:
        raise VEError("unit content must bind one formula or norm")
    if env.unit_schema is not None and "norm" not in content:
        return _quantity_content(env, unit, content, fences)
    if "quantity" in content:
        raise VEError("UnsupportedProfile: quantity content requires ve-units@1")
    if "reports@0" in env.profiles and set(content) & {"report", "assessment", "negated"}:
        return content, None  # The reports decoder binds its identity after all declarations.
    if "norm" in content:
        if "soft-norms@0" in env.profiles:
            from .softnorms import decode_rule, soft_digest
            canonical = decode_rule(env, content).to_dict()
            mid = soft_digest(f"ve-meaning-{env.identity_version}\n",
                              {"environment_id": env.environment_id, "ast": canonical})
            return canonical, mid
        from .norms import NormDocument
        if "norms@0" not in env.profiles:
            raise VEError("UnsupportedProfile: norms@0 is required")
        rule = NormDocument._decode(content)
        return rule.to_dict(), None
    if next(iter(content)) in {"right", "right_lines", "limitation", "bar"}:
        if "rights@0" not in env.profiles:
            raise VEError("UnsupportedProfile: rights@0 is required")
        from .readings import rights_meaning_id
        return content, rights_meaning_id(env, content)
    if "ast" in content:
        formula = formula_from_data(formula_env, content["ast"])
        return formula_to_data(formula_env, formula), meaning_id(formula_env, formula)
    if "fence" not in content or content["fence"] != unit["id"]:
        raise VEError("unit fence must match its id")
    if unit["id"] not in fences:
        raise VEError("missing VE fence")
    text = fences[unit["id"]]
    if unit.get("surface") == "english":
        from .english import parse_english
        document = parse_english(formula_env, text)
    elif unit.get("surface") == "strict":
        from .parser import parse
        document = parse(formula_env, text)
    else:
        raise VEError("fenced content needs english or strict surface")
    if len(document.formulas) != 1:
        raise VEError("each VE fence must contain exactly one sentence")
    formula = document.formulas[0]
    return formula_to_data(formula_env, formula), meaning_id(formula_env, formula)


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


def _parts(units):
    """Flatten an explicitly partitioned mixed source unit for W2 admission.

    The parent is retained as provenance in each part. Its bytes are counted
    exactly once, by its children; no parent content can silently claim them.
    """
    for unit in units:
        if type(unit) is not dict:
            raise VEError("invalid unit schema")
        if unit.get("status") != "MIXED":
            if "parts" in unit:
                raise VEError("parts require MIXED status")
            yield unit, None
            continue
        if set(unit) != {"id", "span", "status", "parts"} or not token(unit["id"]):
            raise VEError("invalid MIXED unit schema")
        span, parts = unit["span"], unit["parts"]
        if (type(span) is not list or len(span) != 2 or
                any(type(x) is not int for x in span) or
                type(parts) is not list or len(parts) < 2):
            raise VEError("MIXED unit needs partitioned parts")
        cursor = span[0]
        for part in parts:
            if (type(part) is not dict or part.get("status") not in STATUSES or
                    type(part.get("span")) is not list or len(part["span"]) != 2 or
                    part["span"][0] != cursor):
                raise VEError("MIXED parts must partition their parent span")
            cursor = part["span"][1]
            yield part, unit["id"]
        if cursor != span[1]:
            raise VEError("MIXED parts must partition their parent span")


def _soft_contents(units):
    return [u.get("content") for u in units
            if type(u) is dict and u.get("kind") == "norm"
            and type(u.get("content")) is dict and "norm" in u["content"]]


def load_document(path: str | Path):
    raw = Path(path).read_bytes()
    meta, source, fences = _split(raw)
    if not source:
        raise VEError("document source is empty")
    if type(meta.get("environment")) is not dict:
        raise VEError("document needs an embedded environment")
    rights_enabled = "rights@0" in meta["environment"].get("profiles", [])
    soft_enabled = "soft-norms@0" in meta["environment"].get("profiles", [])
    if soft_enabled and not rights_enabled:
        from .softnorms import SoftEnvironment, check_soft_source
        if type(meta.get("units")) is list:
            # The environment and the norm units are one soft source (8).
            check_soft_source(meta["environment"], _soft_contents(meta["units"]))
    if rights_enabled:
        from .rights import RightsEnvironment
        env = RightsEnvironment(meta["environment"])
    elif soft_enabled:
        from .softnorms import SoftEnvironment
        env = SoftEnvironment(meta["environment"])
    else:
        env = Environment(meta["environment"])
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
        from .rights import RightsDocument
        # Citations name source units (3.2): the rights source carries every unit id.
        ids = [u.get("id") for u, _ in _parts(units) if type(u) is dict and type(u.get("id")) is str]
        rights_document = RightsDocument(env, [{"source_units": ids}] + [
            u["content"] for u, _ in _parts(units)
            if type(u.get("content")) is dict and
            u.get("kind") in ("right", "right_lines", "limitation", "bar", "norm")])
        soft_document = rights_document.soft_document
        formula_env = soft_document.extended_env
        open_names = (set(open_names) | formula_env.decision_names |
                      set(rights_document.limitation_names.values()) |
                      set(rights_document.condition_names.values()) |
                      set(rights_document.bar_names.values()))
    elif soft_enabled:
        from .softnorms import SoftNormDocument
        soft_document = SoftNormDocument(env, _soft_contents(units))
        formula_env = soft_document.extended_env
        open_names = set(open_names) | soft_document.extended_env.decision_names
    compiled = []
    unit_ids = set()
    cursor = 0
    parents = [u["id"] for u in units if type(u) is dict and u.get("status") == "MIXED"]
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
        kind = (unit["kind"] if rights_enabled and unit["kind"] in
                ("right", "right_lines", "limitation", "bar") else
                _check_kind(unit["kind"], reports="reports@0" in env.profiles))
        status = _meaning(unit["meaning"], open_names, reports="reports@0" in env.profiles)
        if type(unit["support"]) is not str or unit["support"] not in SUPPORTS:
            raise VEError("invalid support")
        content_env = (env if rights_enabled and kind in ("right", "right_lines", "limitation", "bar")
                       else formula_env)
        content, mid = (_content(content_env, unit, fences, formula_env=formula_env,
                                 rights=rights_enabled)
                        if unit.get("content") is not None else (None, None))
        is_norm = type(content) is dict and "norm" in content
        if is_norm:
            from .norms import norm_meaning_id, NormDocument
            from .admission import _quoted
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
        if explicit_status is not None and explicit_status not in STATUSES:
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
        from .reports import ReportsDocument
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
    from .norms import NormDocument
    if set(fences) != {u["id"] for u, _ in _parts(units) if type(u.get("content")) is dict
                       and u["content"].get("fence") == u["id"]}:
        raise VEError("unbound VE fence")
    reading_sets = meta.get("reading_sets", [])
    validate_reading_sets(env if rights_enabled else formula_env, reading_sets, unit_ids)
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
        from .search import _used_predicates

        # Correlation keeps the incident order and appends outside rules after
        # them. Inspect the resulting guards and carve-outs, not source lines.
        correlated = {id(instance): rule for instance, rule in
                      zip(rights.instances, rights.soft_document.rules)}

        def open_rule(rule):
            return (rule.mode == "default" or bool(rule.alterable) or
                    bool(_used_predicates(rule.core.guard) & open_names) or
                    any(_used_predicates(f) & open_names for f in rule.core.unless))

        for unit in compiled:
            if unit["status"] != "CHECKED" or unit["kind"] not in (
                    "right", "right_lines", "limitation", "bar", "norm"):
                continue
            content = unit["content"]
            if type(content) is not dict:
                continue
            kind = unit["kind"]
            if kind in ("limitation", "bar"):
                unit["status"] = "OPEN"
            elif kind == "norm":
                from .softnorms import decode_rule
                if open_rule(decode_rule(rights.environment, {"norm": content["norm"]})):
                    unit["status"] = "OPEN"
            else:
                body = content[kind]
                name = body["name"] if kind == "right" else body["right"]
                active_lines = [i for i in rights.instances if i["right"] == name and
                                any(i["source_line"] is line for line in body["lines"])]
                if any(open_rule(correlated[id(i)]) or
                       any(rights._in_scope(limit, i) for limit in rights.limitations) or
                       (rights.bar is not None and i["kind"] in ("liberty", "powerLiberty"))
                       for i in active_lines):
                    unit["status"] = "OPEN"
    for unit in compiled:
        if unit.pop("explicit_status") not in (None, unit["status"]):
            raise VEError("unit status contradicts content, meaning, or active reading set")
    reading_units = {r["unit"] for r in active}
    norm_units = [u for u in compiled if u["kind"] == "norm"
                  and type(u["content"]) is dict and "norm" in u["content"]]
    quoted_norms.extend(u["content"] for u in norm_units if u["id"] in reading_units)
    if quoted_norms:
        if not soft_enabled:
            from .norm_admission import _check_quoted
            for content in quoted_norms:
                _check_quoted(env, content)
        # Soft quoted norms were checked as single units by decode_rule above;
        # they are not members of the active soft document or its layer premises.
    selected_norms = [u["content"] for u in norm_units if u["id"] not in reading_units]
    norms = (NormDocument(env, selected_norms)
             if not soft_enabled and (selected_norms or any(d.regulated is not None for d in env.predicates.values()))
             else None)
    if "lemmas" in meta and type(meta["lemmas"]) is not list:
        raise VEError("lemmas must be a list")
    for u in compiled:
        if (u["kind"] == "asserted" and u["content"] is None
                and not any(r["unit"] == u["id"] for r in reading_sets)):
            raise VEError("asserted unit needs content or a reading set")
    narrowings = meta.get("narrowings", [])
    validate_narrowings(narrowings, reading_sets, unit_ids)
    weights = meta.get("weights", [])
    if type(weights) is not list or any(type(w) is not dict or set(w) != {"set", "by", "values"} for w in weights):
        raise VEError("invalid removable reading weights")
    sid = source_id(source, env)
    # Bind checked metadata and all authored content, but keep removable weights
    # and JSON layout outside the evidence identity.
    identity_payload = {
        "metadata": {key: value for key, value in meta.items() if key != "weights"},
        "source": source.decode("utf-8"), "fences": fences}
    document_id = hashlib.sha256(
        b"ve-document@1\n" + json.dumps(identity_payload, sort_keys=True,
                                          ensure_ascii=False, separators=(",", ":"),
                                          allow_nan=False).encode("utf-8")).hexdigest()
    return {"meta": meta, "environment": env, "source": source, "source_id": sid,
            "document_id": document_id,
            "units": compiled, "norms": norms, "soft_document": soft_document,
            "reports": reports, "rights_document": rights_document,
            "reading_plan": plan_choices(active if couplings else
                                         [r for r in active if r["status"] == "open"],
                                         couplings=couplings)}


def _fixed_and_active(doc):
    sets = active_reading_sets(doc["meta"].get("reading_sets", []))
    return _fixed_premises(doc, sets), sets


def _fixed_premises(doc, sets):
    """Select fixed claims against the reading choices used by this check."""
    units_with_sets = {r["unit"] for r in sets}
    fixed = [u["content"] for u in doc["units"] if u["kind"] == "asserted"
             and u["content"] is not None and u["id"] not in units_with_sets]
    if doc["norms"] is not None and not _unresolved_norm_reading(sets):
        fixed.extend(formula_to_data(doc["environment"], formula)
                     for _, formula in doc["norms"].premises())
    return fixed


def _unresolved_norm_reading(sets):
    return any(c["kind"] == "norm" or c["content"] is None and c["kind"] != "asserted"
               for r in sets for c in r["readings"])


def _assertion_disjunctions(env, sets):
    from .ast import Or
    result = []
    for reading_set in sets:
        if any(r["kind"] != "asserted" or r["content"] is None for r in reading_set["readings"]):
            continue
        formulas = [formula_from_data(env, r["content"]) for r in reading_set["readings"]]
        formula = formulas[-1]
        for previous in reversed(formulas[:-1]):
            formula = Or(previous, formula)
        result.append(formula)
    return result


_RIGHTS_KINDS = ("right", "right_lines", "limitation", "bar")


def _rights_source_units(doc):
    return [{"source_units": [u["id"] for u in doc["units"]]}] + [
        u["content"] for u in doc["units"]
        if u["kind"] in (*_RIGHTS_KINDS, "norm") and type(u["content"]) is dict]


def _rights_report(doc):
    """The Lean-replayed rights report, or None while a rights reading set still
    needs per-choice elaboration (its findings are then not yet known)."""
    rights = doc.get("rights_document")
    if rights is None:
        return None
    if any(c["kind"] in _RIGHTS_KINDS
           for reading_set in active_reading_sets(doc["meta"].get("reading_sets", []))
           for c in reading_set["readings"]):
        return None
    from .rights_route import report_rights
    return report_rights(doc["environment"], _rights_source_units(doc), rights)


def coverage(doc, scoped=None, rights_report=None):
    """`scoped`: the reports layer's checked scoped verdicts (`check_document`);
    without them a scoped check is reported as not replayed. `rights_report`: the
    replayed rights report when the caller already has it."""
    units = doc["units"]
    source = doc["source"]
    kinds = {}
    statuses = {}
    reasons = {}
    for u in units:
        kind = u["kind"] if type(u["kind"]) is str else u["kind"][0]
        kinds[kind] = kinds.get(kind, 0) + u["span"][1] - u["span"][0]
        statuses[u["status"]] = statuses.get(u["status"], 0) + u["span"][1] - u["span"][0]
        if type(u["meaning"]) is dict and "unformalised" in u["meaning"]:
            reason = u["meaning"]["unformalised"]
            reasons[reason] = reasons.get(reason, 0) + 1
        if doc.get("reports") is not None:
            # 6: a nested unformalised kind is a part of the unit left unformalised
            # (the root one needs an unformalised meaning, counted above).
            from .reports import unformalised_kinds
            for node in unformalised_kinds(u["kind"]):
                if node["path"]:
                    reasons[node["reason"]] = reasons.get(node["reason"], 0) + 1
    meta = doc["meta"]
    graph = meta.get("graph")
    nodes = graph.get("nodes") if type(graph) is dict else None
    labels = [n["label"] for n in nodes if type(n) is dict and type(n.get("label")) is str] \
        if type(nodes) is list else []
    residual = {"open_terms": len(meta.get("open_terms", [])) +
                (len(doc["reports"].open_terms) if doc.get("reports") is not None else 0),
                "assumptions": sum(u["support"] == "assumption" for u in units),
                "bridge_leaves": sum(label.startswith("bridge:accepts(") for label in labels),
                "unresolved_reading_sets": sum(r["status"] == "open" for r in meta.get("reading_sets", []))}
    lines = {}
    if doc.get("reports") is not None:
        # 6: a nested bridge (`bridge:accepts_at`) assumes its payload as a root one
        # does, and every report or assessment premise is an identified assumption
        # whatever its support, so each line counts into the total.
        residual["bridges_nested"] = sum(label.startswith("bridge:accepts_at(") for label in labels)
        lines = doc["reports"].residual_lines(scoped)
        residual.update({line: sum(detail.values()) if type(detail) is dict else len(detail)
                         for line, detail in lines.items()})
    alternatives = None
    soft = doc.get("soft_document")
    environment = doc.get("environment") or (soft.env if soft is not None else None)
    if environment is not None and environment.alternatives is not None:
        from .wire import loads_json
        block = loads_json(environment.alternatives)
        declared, cells, proximate = [], [], []
        for unit in units:
            if unit["kind"] != "asserted":
                continue
            content = unit["content"]
            # Compiled formula content is the AST itself; norm content is a dict.
            ast = content
            if type(ast) is not list:
                continue
            negative = len(ast) == 2 and ast[0] == "not"
            atom = ast[1] if negative else ast
            if type(atom) is not list or len(atom) != 4 or atom[0] != "binary":
                continue
            if any(type(term) is not list or len(term) != 2 or term[0] != "const"
                   for term in atom[2:]):
                continue
            first, second = atom[2][1], atom[3][1]
            leaf = {"unit": unit["id"], "support": unit["support"]}
            if atom[1] == block["available"] and not negative:
                declared.append({"action": first, "chooser": second, **leaf})
            elif atom[1] == block["leads_to"]:
                cells.append({"action": first, "harm": second, "leads_to": not negative,
                              "decider": block.get("decided_by", "unstated"), **leaf})
            elif atom[1] == block.get("proximate") and not negative:
                proximate.append({"action": first, "harm": second,
                                  "decider": block.get("decided_by", "unstated"), **leaf})
        mapped = {item["obligation"] for item in block.get("fulfilments", [])}
        performed = block.get("performed", {}).get("obligation")
        unmapped = [name for name, predicate in environment.predicates.items()
                    if predicate.regulated is not None and predicate.regulated.role == "obligation"
                    and name != performed and name not in mapped]
        completion = ({"decider": block["outcomes"]["complete_by"],
                       "premise": "alternatives:table_complete"}
                      if type(block["outcomes"]) is dict else None)
        # Enumerate the named cells for which the general completion premise
        # supplies a negative answer, excluding every explicitly stated cell.
        actions = {name for name, const in environment.constants.items()
                   if const.sort == block["action"]}
        actions.update(item["action"] for item in declared)
        harms = {name for name, const in environment.constants.items()
                 if const.sort == block["harm"]}
        harms.update(item["harm"] for item in cells)
        stated = {(item["action"], item["harm"]) for item in cells}
        assumed = ([{"action": action, "harm": harm, **completion}
                    for action in sorted(actions) for harm in sorted(harms)
                    if (action, harm) not in stated] if completion else [])
        alternatives = {"alternatives_declared": declared, "counterfactual_leaves": cells,
                        "assumed_harm_free": assumed, "table_complete": completion,
                        "proximate_judgments": proximate, "unmapped_obligations": unmapped,
                        "dilemmas": [], "narrowings": meta.get("narrowings", [])}
        residual.update({"alternatives_declared": len(declared), "counterfactual_leaves": len(cells),
                         "assumed_harm_free": len(assumed),
                         "table_complete": int(completion is not None),
                         "proximate_judgments": len(proximate),
                         "unmapped_obligations": len(unmapped), "dilemmas": 0,
                         "narrowings": len(alternatives["narrowings"])})
    soft = doc.get("soft_document")
    if soft is not None:
        decisions = soft.extended_env.decision_names
        open_pairs = [
            f"soft:coherence:{left.core.name},{right.core.name}"
            for left, right in soft.collisions
            if (left.rank is None or right.rank is None or
                (left.rank not in soft.env.ranks_above[right.rank] and
                 right.rank not in soft.env.ranks_above[left.rank]))]
        residual["default_exceptions"] = sum(r.mode == "default" for r in soft.rules)
        residual["instruction_switches"] = sum(len(r.alterable) for r in soft.rules)
        residual["holistic_overrides"] = sum(name.startswith("soft__outweighs__") for name in decisions)
        residual["weighing_points"] = len(open_pairs)
        by_decider = {}
        for rule in soft.rules:
            if rule.mode == "default":
                who = (rule.exception or {}).get("decided_by") or soft.env.soft.get("exception_decider") or "unstated"
                by_decider[who] = by_decider.get(who, 0) + 1
    rights = doc.get("rights_document")
    if rights is not None:
        residual["limitation_terms"] = len(rights.limitation_names) + len(rights.condition_names)
        residual["limitation_deciders_unstated"] = sum(
            limit["decided_by"] == "unstated" for limit in rights.limitations)
        residual["bar_terms"] = len(rights.bar_names)
        residual["power_shadows"] = sum(i["kind"] in ("powerLiberty", "immunity")
                                         for i in rights.instances)
        for axis in ("bearer", "polarity", "incident", "force"):
            residual[f"{axis}_readings"] = sum(
                len({candidate.get("labels", {}).get(axis) for candidate in reading_set["readings"]}) > 1
                for reading_set in active_reading_sets(meta.get("reading_sets", [])))
        residual["couplings"] = len({item["axis"] for item in meta.get("couplings", [])})
        residual["narrowings"] = len(meta.get("narrowings", []))
        # 7.2: the audit findings are residual lines and count into the total;
        # while a rights reading set is pending they are not known, and say so.
        if rights_report is None:
            rights_report = _rights_report(doc)
        if rights_report is None:
            residual["rights_findings_pending"] = 1
        else:
            residual["unlicensed_limitations"] = len(rights_report["unlicensed_limitations"])
            residual["distinction_hits"] = sum(len(row["hits"]) for row in rights_report["distinction"])
    soft_open = ("default_exceptions", "instruction_switches", "holistic_overrides", "weighing_points",
                 "limitation_terms", "bar_terms")
    return {"source_bytes": len(source), "accounted_bytes": sum(kinds.values()),
            "coverage_percent": 100, "bytes_by_kind": kinds, "bytes_by_status": statuses,
            "unformalised_reasons": reasons,
            "residual": residual, "residual_total": sum(residual.values()),
            **({"residual_lines": lines} if lines else {}),
            **({"alternatives": alternatives} if alternatives is not None else {}),
            **({"soft_status": "OPEN" if any(residual.get(key) for key in soft_open) else "CHECKED",
                "default_exceptions_by_decider": by_decider,
                "soft_residual_labels": [*sorted(soft.extended_env.decision_names), *open_pairs],
                "soft_background_labels": [label for label, _ in soft.exception_premises]}
               if soft is not None else {}),
            **({"rights_residual_labels": [
                *[f"limitation {name} on {act}: {generated}; decider " +
                  next(limit["decided_by"] for limit in rights.limitations if limit["name"] == name)
                  for (name, act), generated in rights.limitation_names.items()],
                *[f"condition {condition} of limitation {name} on {act}: {generated}; decider " +
                  (next(item["decided_by"] for limit in rights.limitations if limit["name"] == name
                        for item in limit["conditions"] if item["name"] == condition) or
                   next(limit["decided_by"] for limit in rights.limitations if limit["name"] == name))
                  for (name, act, condition), generated in rights.condition_names.items()],
                *[f"coupling:{item['id']} ({item['axis']}, " +
                  ", ".join(ref["set"] for ref in item["sets"]) + ")"
                  for item in meta.get("couplings", [])]]}
               if rights is not None else {}),
            **({"rights_report": {
                "unlicensed_limitations": rights_report["unlicensed_limitations"],
                "distinction_hits": rights_report["distinction_hits"],
                "limitation_premises_used": rights_report["limitation_premises_used"]}}
               if rights is not None and rights_report is not None else {})}


def _check_narrowing_choices(meta, labels):
    from .admission import parse_label
    for n in meta.get("narrowings", []):
        if f"narrowing:{n['id']}" not in labels:
            continue
        rs = next(r for r in meta["reading_sets"]
                  if (r["id"], r["version"]) == (n["set"], n["version"]))
        for label in labels:
            parsed = parse_label(label) if label is not None else None
            if (parsed is not None and parsed.kind == "readings"
                    and parsed.args[:2] == (n["set"], n["version"])
                    and parsed.args[2] is not None
                    and rs["readings"][parsed.args[2]]["id"] not in n["keeps"]):
                raise VEError("reading choice conflicts with narrowing")


def quantity_admission_input(doc, active):
    """The P0-shaped admission input of a quantity document, as sent to Lean
    `ve_quantity` (case kind `document`). A unit with an active reading set
    contributes only through readings labels."""
    active_units = {r["unit"] for r in active}
    return {"units": [{"id": u["id"], "span": u["span"], "kind": u["kind"],
                       **({"content": u["content"]}
                          if u["content"] is not None and u["id"] not in active_units else {})}
                      for u in doc["units"]],
            "graph": doc["meta"]["graph"],
            **({"lemmas": doc["meta"]["lemmas"]} if "lemmas" in doc["meta"] else {}),
            "open_terms": [o["name"] for o in doc["meta"].get("open_terms", [])],
            "reading_sets": [{"id": r["id"], "version": r["version"],
                              "readings": [c["content"] for c in r["readings"]]}
                             for r in active],
            "narrowings": [n["id"] for n in doc["meta"].get("narrowings", [])]}


def _check_quantity_document(doc, active):
    """`ve document check` on the quantity route: Lean-mirrored admission of the
    claim graph over annotated statements, then premise status of the
    regenerated cores in the erased target."""
    from .units import core_formula, erased_environment
    env = doc["environment"]
    target = erased_environment(env)
    result = {"format": "ve-document@1", "source_id": doc["source_id"],
              "document_id": doc["document_id"],
              "coverage": coverage(doc), "reading_plan": doc["reading_plan"]}
    if any(c["kind"] != "asserted" or c["content"] is None for r in active for c in r["readings"]):
        raise VEError("non-assertion reading admission needs an elaborator")
    active_units = {r["unit"] for r in active}
    payloads = [u["content"] for u in doc["units"] if u["kind"] == "asserted"
                and u["content"] is not None and u["id"] not in active_units]
    if "graph" in doc["meta"]:
        result["admission"] = admit_document(env, quantity_admission_input(doc, active))
        labels = [a.get("label") for a in result["admission"]["report"]["assumptions"]]
        _check_narrowing_choices(doc["meta"], labels)
        payloads.extend(a["quantity"] for a in result["admission"]["report"]["assumptions"])
        result["admission"]["core_report_id"] = result["admission"]["report_id"]
        result["admission"]["report_id"] = digest(
            f"ve-report-{env.identity_version}\n",
            {"environment_id": env.environment_id, "document": doc["document_id"],
             "report": result["admission"]["report"]})
    premises = [core_formula(env, p)[1] for p in payloads]
    from .ast import Or
    for reading_set in active:
        cores = [core_formula(env, c["content"])[1] for c in reading_set["readings"]]
        formula = cores[-1]
        for previous in reversed(cores[:-1]):
            formula = Or(previous, formula)
        premises.append(formula)
    result["premises"] = premise_status(target, premises)
    if "admission" in result:
        status = result["premises"]["status"]
        result["admission"]["vacuous"] = (True if status == "INCONSISTENT" else
                                           False if status == "model" else None)
    return result


@semantic_entry("document.check")
def check_document(path):
    from .search import model_search_scope
    with model_search_scope():
        return _check_document(path)


def _check_document(path):
    doc = load_document(path)
    soft = doc["soft_document"]
    if doc["reports"] is not None:
        from .reports_route import checked_elaboration, run_case
        meta = doc["meta"]
        route_doc = {"units": [_wire_unit(u) for u in doc["units"]],
                     "contexts": meta.get("contexts", []), "assessments": meta.get("assessments", []),
                     "bridges": meta.get("bridges", []), "scoped": meta.get("scoped", []),
                     "open_terms": [o["name"] for o in meta.get("open_terms", [])],
                     **({"graph": meta["graph"]} if "graph" in meta else {})}
        environment = meta["environment"]
        reports = doc["reports"]
        checked = checked_elaboration(reports, environment, route_doc)
        # 6: the scoped checks' replayed verdicts, and every unit's and the
        # document's status as the meet of all nested results, in Python and Lean.
        replayed = run_case("reports-status", environment, route_doc)
        statuses = reports.statuses(reports.scoped_verdicts(replayed["scoped"]))
        if any(replayed.get(key) != statuses[key] for key in ("units", "document_status")):
            raise VEError("ReportsConformance: Python and Lean differ at statuses")
        result = {"format": "ve-document@1", "status": "UNVERIFIED",
                  "source_id": doc["source_id"], "document_id": doc["document_id"],
                  "coverage": coverage(doc, statuses["scoped"]), "reports": checked,
                  "statuses": statuses}
        # 7.1 row 4: P0's premise-set line over Background(E_reports) ++ Γ, where Γ
        # is the report premises, the author's asserted units and the graph's
        # admitted leaves, as in the plain W2 path.
        extended = doc["reports"].extended_environment
        premises = [formula_from_data(extended, p["ast"]) for p in checked["premises"]]
        premises += [formula_from_data(extended, ast) for ast in _fixed_premises(doc, [])]
        if "graph" in route_doc:
            result["admission"] = run_case("admission", environment, route_doc)
            premises += [formula_from_data(extended, a["ast"])
                         for a in result["admission"]["report"]["assumptions"]]
        result["premises"] = premise_status(extended, premises)
        status = result["premises"]["status"]
        if "admission" in result:
            result["admission"]["vacuous"] = (True if status == "INCONSISTENT" else
                                               False if status == "model" else None)
            # A status needs an admitted graph over a premise set with a model: an
            # inconsistent (or undecided) set makes every certificate vacuous.
            if status == "model":
                result["status"] = statuses["document_status"]
        return result
    env = soft.extended_env if soft is not None else doc["environment"]
    if env.unit_schema is not None:
        return _check_quantity_document(doc, active_reading_sets(doc["meta"].get("reading_sets", [])))
    fixed, active = _fixed_and_active(doc)
    assertions = [formula_from_data(env, ast) for ast in fixed]
    rights_report = _rights_report(doc)
    result = {"format": "ve-document@1", "source_id": doc["source_id"],
              "document_id": doc["document_id"],
              "coverage": coverage(doc, rights_report=rights_report),
              "reading_plan": doc["reading_plan"]}
    if soft is not None:
        from .soft_route import elaborate_soft_document
        elaborate_soft_document(soft)
        result["soft"] = {"environment_id": doc["environment"].environment_id,
                          "soft_document_hash": soft.document_hash,
                          "decision_predicates": sorted(soft.extended_env.decision_names),
                          "background_labels": [label for label, _ in soft.extended_env.soft_premises]}
        assertions.extend(formula for _, formula in soft.elaborated.premises())
        assertions.extend(formula for _, formula in soft.extended_env.soft_premises)
    rights = doc["rights_document"]
    if rights is not None:
        result["rights"] = {
            "environment_id": doc["environment"].environment_id,
            "limitation_predicates": [{"name": generated, "limitation": limit, "act": act}
                                      for (limit, act), generated in rights.limitation_names.items()],
            "condition_predicates": [{"name": generated, "limitation": limit, "act": act,
                                      "condition": condition}
                                     for (limit, act, condition), generated in rights.condition_names.items()],
            "limitation_background_labels": [label for label, _ in rights.limitation_premises]}
        assertions.extend(formula for _, formula in rights.limitation_premises)
        if rights_report is None:
            result["rights"]["report_status"] = "UNKNOWN: per-choice rights elaboration pending"
        else:
            result["rights"]["report"] = rights_report
    if "graph" in doc["meta"]:
        if (_unresolved_norm_reading(active) and
                any(type(node) is dict and type(node.get("label")) is str
                    and node["label"].startswith("layer:norms:")
                    for node in doc["meta"]["graph"].get("nodes", []))):
            raise VEError("non-assertion norm reading admission needs an elaborator")
        from .admission import parse_label
        active_keys = {(r["id"], r["version"]): r for r in active}
        for node in doc["meta"]["graph"].get("nodes", []):
            label = parse_label(node.get("label")) if type(node) is dict else None
            if label is not None and label.kind == "readings":
                reading_set = active_keys.get(label.args[:2])
                if reading_set is None:
                    raise VEError("graph cites a stale or unknown reading set version")
                if any(c["kind"] != "asserted" or c["content"] is None
                       for c in reading_set["readings"]):
                    raise VEError("non-assertion reading admission needs an elaborator")
        # A unit with an active reading set contributes premises only through
        # readings labels, including when its old content has the same formula.
        active_units = {r["unit"] for r in active}
        admission = {"units": [{"id": u["id"], "span": u["span"], "kind": u["kind"],
                                **({"content": u["content"]}
                                   if u["content"] is not None and u["id"] not in active_units else {})}
                               for u in doc["units"]],
                     "graph": doc["meta"]["graph"],
                     "lemmas": doc["meta"].get("lemmas", []),
                     "open_terms": [o["name"] for o in doc["meta"].get("open_terms", [])],
                     "reading_sets": [{"id": r["id"], "version": r["version"],
                                       "readings": [c["content"] for c in r["readings"]],
                                       **({"labels": [c.get("labels", {}) for c in r["readings"]]}
                                          if rights is not None else {})}
                                      for r in active
                                      if all(c["kind"] == "asserted" and c["content"] is not None
                                             for c in r["readings"])],
                     "narrowings": [n["id"] for n in doc["meta"].get("narrowings", [])],
                     **({"couplings": doc["meta"]["couplings"]}
                        if rights is not None and doc["meta"].get("couplings") else {})}
        if rights is not None:
            from .rights_route import admit_rights_document
            result["admission"] = admit_rights_document(doc["environment"], admission, rights)
        elif soft is not None:
            from .soft_route import admit_soft_document
            result["admission"] = admit_soft_document(doc["environment"], admission,
                                                       soft_document=soft)
        else:
            result["admission"] = admit_document(env, admission)
        latest = {}
        for rs in doc["meta"].get("reading_sets", []):
            latest[rs["id"]] = max(latest.get(rs["id"], 0), rs["version"])
        labels = [a.get("label") for a in result["admission"]["report"]["assumptions"]]
        _check_narrowing_choices(doc["meta"], labels)
        result["stale_reading_labels"] = [label for a in result["admission"]["report"]["assumptions"]
                                          if (label := a.get("label")) is not None
                                          and (parsed := parse_label(label)) is not None
                                          and parsed.kind == "readings"
                                          and parsed.args[1] < latest.get(parsed.args[0], 0)]
        # Graph leaves add premises; they do not replace fixed document claims.
        assertions.extend(formula_from_data(env, a["ast"])
                          for a in result["admission"]["report"]["assumptions"])
        result["admission"]["core_report_id"] = result["admission"]["report_id"]
        result["admission"]["report_id"] = digest(
            f"ve-report-{env.identity_version}\n",
            {"environment_id": env.environment_id, "document": doc["document_id"],
             "report": result["admission"]["report"]})
    assertions.extend(_assertion_disjunctions(env, active))
    if env.alternatives is not None:
        result["premises"] = {"status": "UNKNOWN",
                              "reason": "alternatives premise satisfiability requires the alternatives route"}
    elif _unresolved_norm_reading(active):
        result["premises"] = {"status": "UNKNOWN", "reason": "non-assertion reading elaboration pending"}
    else:
        result["premises"] = premise_status(env, assertions)
        if (result["premises"]["status"] != "INCONSISTENT"
                and any(c["kind"] != "asserted" or c["content"] is None
                        for r in active for c in r["readings"])):
            result["premises"] = {"status": "UNKNOWN", "reason": "non-assertion reading elaboration pending"}
    if "admission" in result:
        status = result["premises"]["status"]
        result["admission"]["vacuous"] = (True if status == "INCONSISTENT" else
                                           False if status == "model" else None)
    return result


def render_document(path):
    doc = load_document(path)
    lines = []
    from .printer import render
    render_env = (doc["soft_document"].extended_env if doc["soft_document"] is not None
                  else doc["environment"])

    def wording(ast):
        if doc["environment"].unit_schema is not None:
            from .surface.time import render_quantity_sentence
            try:
                return render_quantity_sentence(doc["environment"], ast)
            except VEError:
                return "The checked quantity statement " + json.dumps(ast["formula"]) + "."
        formula = formula_from_data(render_env, ast)
        return render(Document((formula,)), render_env, "ve_english").strip()

    descriptions = {
        "asserted": "a direct assertion", "norm": "a rule", "definition": "a definition",
        "right": "a right", "right_lines": "right incidents", "limitation": "a limitation",
        "bar": "a bar",
        "question": "a question", "instruction": "an instruction", "example": "an example",
        "exposition": "background information", "analogy": "an analogy",
        "explanation": "an explanation", "meta": "a comment about the text",
    }
    def kind_description(kind):
        if type(kind) is str:
            return descriptions[kind]
        if kind[0] == "attributed":
            return (f"{kind_description(kind[3])} attributed to {kind[1]} "
                    f"as something {kind[1]} {kind[2]}")
        if kind[0] == "hedged":
            return f"{kind_description(kind[2])} qualified as {kind[1]}"
        if kind[0] == "causal":
            return (f"a causal statement connecting {kind_description(kind[2])} "
                    f"to {kind_description(kind[3])} with the relation {kind[1]}")
        return f"a passage without a formal reading yet, for this reason: {kind[1].replace('_', ' ')}"

    def kind_wording(kind, content):
        if content is None:
            return f"The passage is recorded as {kind_description(kind)}."
        if kind in ("right", "right_lines", "limitation", "bar"):
            from .surface.rights import render_unit
            return render_unit(doc["rights_document"], content)
        if type(content) is dict and "norm" in content:
            if doc["soft_document"] is not None:
                rule = content["norm"]
                if rule.get("mode") == "default":
                    decider = (rule["exception"].get("decided_by") or
                               doc["environment"].soft.get("exception_decider") or "unstated")
                    from .surface.softnorms import rule_paraphrase
                    role = doc["environment"].predicates[rule["predicate"]].regulated.role
                    decision_source = (f"an open decision by {decider}" if decider != "unstated"
                                       else "an open decision whose decider the source does not name")
                    description = (f"Rule {rule['name']} is a default rule on {rule['predicate']} with sign "
                                   f"{'positive' if rule['sign'] else 'negative'}. Its exception is {decision_source}; "
                                   "the rule applies only if that exception does not apply. "
                                   + rule_paraphrase(rule["name"], "default", role=role, sign=rule["sign"],
                                                     decider=decider, alterable=rule.get("alterable", ()),
                                                     rank=rule.get("rank")))
                else:
                    description = (f"Rule {rule['name']} is a strict rule on {rule['predicate']} with sign "
                                   f"{'positive' if rule['sign'] else 'negative'}.")
                    if rule.get("alterable"):
                        from .surface.softnorms import rule_paraphrase
                        description += " " + rule_paraphrase(rule["name"], "strict", alterable=rule["alterable"])
                return (description if kind == "norm" else
                        f"{description} The source presents this as {kind_description(kind)}.")
            from .norms import NormDocument
            from .norm_english import render_rule_sentence
            rule = NormDocument._decode(content)
            claim = render_rule_sentence(rule, doc["environment"])
            if rule.over:
                claim += " Exception to " + ", ".join(rule.over) + "."
            return claim if kind == "norm" else f"{claim} The source presents this as {kind_description(kind)}."
        claim = wording(content)
        if kind == "asserted":
            return claim
        return f"{claim} The source presents this as {kind_description(kind)}."

    active_by_unit = {r["unit"]: r for r in active_reading_sets(doc["meta"].get("reading_sets", []))}
    for u in doc["units"]:
        lines.append(u["source"].strip())
        prefix = ("Open rule reading: " if type(u["content"]) is dict and
                  "norm" in u["content"] and
                  (u["content"]["norm"].get("mode") == "default" or
                   bool(u["content"]["norm"].get("alterable"))) else
                  "Checked reading: " if u["content"] is not None and
                  u["status"] == "CHECKED" else
                  "Open reading: " if u["content"] is not None and
                  u["status"] == "OPEN" else "Recorded meaning: ")
        lines.append(prefix + kind_wording(u["kind"], u["content"]))
        reading_set = active_by_unit.get(u["id"])
        if reading_set is not None:
            lines.append("The author's chosen reading is:" if reading_set["status"] == "authored"
                         else "This sentence could mean:")
            for index, candidate in enumerate(reading_set["readings"]):
                lead = "One reading is" if index == 0 else "Another reading is"
                lines.append(f"{lead}: {kind_wording(candidate['kind'], candidate['content'])}")
    return "\n".join(lines) + "\n"


def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser(prog="ve document")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("check", "render", "coverage", "readings"):
        sub.add_parser(name).add_argument("path")
    sub.choices["readings"].add_argument("--conclusion", help="formula AST JSON file to classify")
    sub.choices["readings"].add_argument("--narrowing", help="apply a recorded narrowing by id")
    args = parser.parse_args(argv)
    if args.command == "render":
        print(render_document(args.path), end="")
        return 0
    if args.command == "check":
        data = check_document(args.path)
    else:
        doc = load_document(args.path)
        if args.command == "coverage":
            data = coverage(doc)
        elif args.conclusion:
            conclusion = json.loads(Path(args.conclusion).read_text())
            active = active_reading_sets(doc["meta"].get("reading_sets", []))
            sets = [{**r, "readings": [{**c, "original_index": i}
                                      for i, c in enumerate(r["readings"])]} for r in active]
            if args.narrowing:
                matching = [n for n in doc["meta"].get("narrowings", []) if n["id"] == args.narrowing]
                if len(matching) != 1:
                    raise VEError("unknown narrowing")
                narrowing = matching[0]
                if not any((r["id"], r["version"]) == (narrowing["set"], narrowing["version"])
                           for r in sets):
                    raise VEError("narrowing does not target an active reading set")
                sets = [{**r, "readings": [c for c in r["readings"] if c["id"] in narrowing["keeps"]]}
                        if (r["id"], r["version"]) == (narrowing["set"], narrowing["version"]) else r
                        for r in sets]
            data = check_readings(doc["environment"], sets, conclusion,
                                  fixed=_fixed_premises(doc, sets),
                                  couplings=doc["meta"].get("couplings", []))
            if args.narrowing:
                data["narrowing"] = f"narrowing:{args.narrowing}"
        else:
            if args.narrowing:
                raise VEError("--narrowing requires --conclusion")
            data = doc["reading_plan"]
    print(json.dumps(data, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
