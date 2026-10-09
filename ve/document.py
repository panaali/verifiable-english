"""ve-document@1: byte-partitioned source, reviewed metadata and P0 admission.

Front matter is JSON between two ``---`` lines. The source is every body byte
outside ``ve`` fences; unit spans are offsets into that exact byte sequence.
``ve <unit-id>`` fences supply an optional English or strict formula for a
unit. The JSON front matter may instead bind a formula AST or a W1 norm.

A ``ve-document@1`` document is checked by Lean's ``document`` mode (lean-first batch 16b): its checks, unit
statuses, identities and coverage are Lean's, and this module builds the document from that answer and displays
it. Python's own loader below (``_load_document``) runs only for a ``ve-document@2`` document after Lean's discourse
admission, and for a document the mode answers ``CheckerUnavailable`` or ``ResourceLimit`` for: the profiles,
contents and routes listed in docs/lean-first/b16b/DELTA.md, each retained until its batch composes it in the mode.
"""
from __future__ import annotations

from copy import deepcopy
import json
import hashlib
import re
from pathlib import Path

from .assurance import semantic_entry
from .admission import _check_kind, admit_document, token
from .ast import Document, decimal_value, formula_from_data, formula_to_data
from .backends.lean_service import CheckerUnavailable
from .environment import Environment, listed_profiles
from .errors import ResourceLimit, UnsupportedProfile, VEError
from .identity import meaning_id, source_id
from .openterms import validate_open_terms
from .readings import (active_reading_sets, check_readings, plan_choices, s1_content_kind,
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


def front_matter(raw: bytes):
    """The decoded JSON front matter of a document text and its body bytes, before any check of
    the metadata or the body: all that names a text's format."""
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
    except RecursionError:
        raise ResourceLimit("ResourceLimit: JSON front matter nesting exceeds the parser's depth") from None
    return meta, raw[boundary + 5:]


def _split(raw: bytes):
    meta, body = front_matter(raw)
    if type(meta) is not dict or meta.get("format") not in ("ve-document@1", "ve-document@2"):
        raise VEError("unsupported document format")
    allowed = {"format", "environment", "units", "open_terms", "reading_sets",
               "narrowings", "couplings", "weights", "graph", "lemmas",
               "contexts", "assessments", "bridges", "scoped", "completions", "senses"}
    if meta["format"] == "ve-document@2":
        allowed.add("discourse")
    if set(meta) - allowed:
        raise VEError("unknown document metadata")
    if "couplings" in meta and not {"rights@0", "readings@1"}.intersection(
            listed_profiles(meta.get("environment"))):
        raise UnsupportedProfile("UnsupportedProfile: rights@0 is required for couplings")
    if "completions" in meta and "norm-defaults@0" not in listed_profiles(meta.get("environment")):
        raise UnsupportedProfile("UnsupportedProfile: norm-defaults@0 is required for completions")
    return meta, *_body(body)


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
        from .readings import rights_meaning_id
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
            from .softnorms import batch_rule, decode_rule, soft_digest
            rule = (batch_rule(env, content, rule_result) if rule_result is not None
                    else decode_rule(env, content))
            canonical = rule.to_dict()
            mid = soft_digest(f"ve-meaning-{env.identity_version}\n",
                              {"environment_id": env.environment_id, "ast": canonical})
            return canonical, mid
        from .norms import NormDocument
        if "norms@0" not in env.profiles:
            raise UnsupportedProfile("UnsupportedProfile: norms@0 is required")
        rule = NormDocument._decode(content)
        return rule.to_dict(), None
    if next(iter(content)) in {"right", "right_lines", "limitation", "bar"}:
        if "rights@0" not in env.profiles:
            raise UnsupportedProfile("UnsupportedProfile: rights@0 is required")
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
    if senses is not None and unit.get("surface") == "english":
        # RD-8: Lean read the fence (`ve.senses_document`); a preamble line or an open unit has no formula.
        data = senses.formulas.get(unit["id"])
        if data is None:
            return None, None
        formula = formula_from_data(formula_env, data)
        return formula_to_data(formula_env, formula), meaning_id(formula_env, formula)
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
            if (type(part) is not dict or type(part.get("status")) is not str or part["status"] not in STATUSES or
                    type(part.get("span")) is not list or len(part["span"]) != 2 or
                    part["span"][0] != cursor):
                raise VEError("MIXED parts must partition their parent span")
            cursor = part["span"][1]
            yield part, unit["id"]
        if cursor != span[1]:
            raise VEError("MIXED parts must partition their parent span")


def _document_id(meta, source, fences):
    """Bind checked metadata and all authored content, but keep removable weights and JSON
    layout outside the evidence identity."""
    identity_payload = {
        "metadata": {key: value for key, value in meta.items() if key != "weights"},
        "source": source.decode("utf-8"), "fences": fences}
    return hashlib.sha256(
        (meta["format"] + "\n").encode("ascii") + json.dumps(identity_payload, sort_keys=True,
                                          ensure_ascii=False, separators=(",", ":"),
                                          allow_nan=False).encode("utf-8")).hexdigest()


def _soft_contents(units, exclude=frozenset()):
    return [u.get("content") for u in units
            if type(u) is dict and u.get("kind") == "norm" and u.get("id") not in exclude
            and type(u.get("content")) is dict and "norm" in u["content"]]


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
    from .readings_s1 import Document as S1Document
    try:
        units = [{"id": u["id"], "kind": u.get("kind"), "content": u.get("content")}
                 for u, _ in _parts(meta.get("units", []))]
        # Attachment reads names only (1.3), never the frame, which under norm-defaults@0 is Lean's.
        attached = S1Document(None, {"units": units, "reading_sets": sets}).attached()
    except (VEError, KeyError, TypeError, ValueError, AttributeError, IndexError):
        return frozenset()
    return frozenset(u for u, owners in attached.items() if owners)


def _environment(data):
    """The environment of a document's (profile-stripped) environment data."""
    profiles = listed_profiles(data)
    if "rights@0" in profiles:
        from .rights import RightsEnvironment
        return RightsEnvironment(data)
    if "soft-norms@0" in profiles:
        from .softnorms import SoftEnvironment
        return SoftEnvironment(data)
    return Environment(data)


def stored_identities(raw: bytes):
    """The front matter, `source_id` and `document_id` of a stored document text: the decode and
    identity of an imported or embedded document (discourse.md 4.1(10)), not its admission."""
    meta, source, fences = _split(raw)
    if not source:
        raise VEError("document source is empty")
    if type(meta.get("environment")) is not dict:
        raise VEError("document needs an embedded environment")
    env = _environment(base_environment(meta))
    return meta, source_id(source, env), _document_id(meta, source, fences)


def base_environment(meta):
    """The environment data the frozen environment and document routes receive: a `@1`
    document's own (its profile gate of discourse.md 1.1 only), a `@2` document's without
    `ve.discourse@1` (docs/spec/discourse.md 3.4; Lean has admitted the `@2` document first)."""
    from .discourse import PROFILE
    data = meta["environment"]
    if meta["format"] == "ve-document@1":
        if type(data) is dict and type(data.get("profiles")) is list and PROFILE in data["profiles"]:
            raise UnsupportedProfile("UnsupportedProfile: ve.discourse@1 requires ve-document@2")
        return data
    if (type(data) is not dict or type(data.get("profiles")) is not list
            or any(type(p) is not str for p in data["profiles"])):
        raise VEError("invalid environment profiles")
    profiles = data["profiles"]
    if profiles != sorted(set(profiles)) or PROFILE not in profiles or "relational-fol@0" not in profiles:
        raise UnsupportedProfile("UnsupportedProfile: ve.discourse@1 requires a sorted profile list with relational-fol@0")
    if "discourse" not in meta:
        raise VEError("InvalidInput: missing discourse block")
    return {**data, "profiles": [p for p in profiles if p != PROFILE]}


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
    from .discourse import is_discourse_text, lean_admission, rejection, unavailable_report
    if not is_discourse_text(raw):
        row = _lean_answer(raw, admit)
        if row is None:
            return _load_document(raw, path, None)
        return _lean_document(raw, path, row, admitted=admit)
    lean = lean_admission(raw, Path(path).parent)
    if lean["status"] == "error":
        raise rejection(lean)
    try:
        return _load_document(raw, path, lean)
    except CheckerUnavailable:
        raise
    except Exception as exc:
        raise unavailable_report(exc) from exc


def _lean_answer(raw: bytes, admit: bool):
    """Lean's `document` row for a `ve-document@1` text, or None when Python's own path decides it: the mode
    answered `CheckerUnavailable` or `ResourceLimit` (it cannot decide, and says so), or the text is not UTF-8,
    which the mode cannot be sent. Any other rejection is Lean's diagnostic, raised verbatim; a failure of the
    service itself is raised, never answered by Python."""
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return None
    from .backends.relay import answer
    row, error = answer("document", {"id": "document", "document": text, "admit": admit})
    if isinstance(error, (CheckerUnavailable, ResourceLimit)):
        return None
    if error is not None:
        raise error
    return row


def _lean_document(raw: bytes, path: Path, row: dict, *, admitted: bool):
    """The document Lean's `document` mode accepted, built from its answer (docs/LEAN-FIRST-PLAN.md rule 2: Lean
    validates, Python constructs). The row is bound to the request first: its source is the text's body and its
    units are the front matter's, in order, with content exactly where the front matter has some. A row that
    is not, or a document that cannot be built from it, is `CheckerUnavailable`, never a verdict."""
    from .norms import NormDocument

    def unavailable(what):
        return CheckerUnavailable(f"CheckerUnavailable: the Lean document answer {what}")
    try:
        meta = json.loads(raw[4:raw.find(b"\n---\n", 4)].decode("utf-8"))
        body = raw[raw.find(b"\n---\n", 4) + 5:]
        declared = [(u, parent) for u, parent in _parts(meta["units"])]
    except Exception as exc:  # noqa: BLE001 - Lean accepted this front matter
        raise unavailable("is for a front matter Python cannot read") from exc
    try:
        _bind_document_answer(body, meta, declared, row)
        source, units = row["source"].encode("utf-8"), row["units"]
    except Exception as exc:  # noqa: BLE001 - an accepted but malformed service row is unavailable
        raise unavailable("is not bound to the document sent") from exc
    try:
        env = Environment(meta["environment"])
        if row["source_id"] != source_id(source, env) or row["document_id"] != _document_id(meta, source, {}):
            raise unavailable("is not bound to the document sent")
        for unit in units:
            if "content" in unit and unit["meaning_id"] != digest(
                    f"ve-meaning-{env.identity_version}\n",
                    {"environment_id": env.environment_id, "ast": unit["content"]}):
                raise unavailable("is not bound to the document sent")
        compiled = [{"id": u["id"], "span": u["span"], "kind": u["kind"], "meaning": u["meaning"],
                     "support": u["support"], "source": source[u["span"][0]:u["span"][1]].decode("utf-8"),
                     "content": u.get("content"), "meaning_id": u.get("meaning_id"), "status": u["status"],
                     **({"parent_id": u["parent_id"]} if "parent_id" in u else {})} for u in units]
        active = active_reading_sets(meta.get("reading_sets", []))
        norms = (NormDocument(env, []) if any(d.regulated is not None for d in env.predicates.values())
                 else None)
        reading_plan = plan_choices([r for r in active if r["status"] == "open"], couplings=[])
    except CheckerUnavailable:
        raise
    except Exception as exc:  # noqa: BLE001 - a document Lean accepted that Python cannot build is a bug
        raise unavailable(f"could not be built: {type(exc).__name__}: {exc}"[:300]) from exc
    return {"meta": meta, "environment": env, "source": source, "source_id": row["source_id"],
            "document_id": row["document_id"], "directory": path.parent, "units": compiled, "norms": norms,
            "soft_document": None, "norm_defaults": None, "senses": None, "reports": None,
            "rights_document": None, "readings_s1": None, "readings_s2": None, "reading_plan": reading_plan,
            "lean": {"coverage": row["coverage"], "admitted": admitted}}


# The list lines of a composed block's coverage (`Alternatives.Wire.coverage`), each counted in the residual.
_BLOCK_LINES = ("alternatives_declared", "assumed_harm_free", "counterfactual_leaves", "dilemmas", "narrowings",
                "proximate_judgments", "unmapped_obligations")


def _bind_document_answer(body, meta, declared, row):
    """Check the request-shaped fields and arithmetic of a successful Lean document row.

    The response schema checks types. This binding additionally checks values the schema
    cannot know: the authored unit fields, byte partition and every count derived from
    them. Checked content, statuses and identities remain Lean's decisions.
    """
    def same(a, b):
        return (json.dumps(a, sort_keys=True, ensure_ascii=False, allow_nan=False) ==
                json.dumps(b, sort_keys=True, ensure_ascii=False, allow_nan=False))

    def require(condition):
        if not condition:
            raise ValueError("Lean document row disagrees with its request")

    require(type(row) is dict and type(row.get("source")) is str and
            set(row) == {"id", "status", "document_id", "source_id", "source", "units", "coverage"})
    source = row["source"].encode("utf-8")
    require(source == body)
    units = row.get("units")
    require(type(units) is list and len(units) == len(declared))
    kinds, statuses, reasons = {}, {}, {}
    for unit, (authored, parent) in zip(units, declared, strict=True):
        require(type(unit) is dict and type(authored) is dict)
        require(set(unit) == {"id", "span", "kind", "meaning", "support", "status"} |
                ({"content", "meaning_id"} if "content" in authored else set()) |
                ({"parent_id"} if parent is not None else set()))
        for field in ("id", "span", "kind", "meaning", "support"):
            require(field in unit and field in authored and same(unit[field], authored[field]))
        require(("parent_id" in unit) == (parent is not None))
        if parent is not None:
            require(unit["parent_id"] == parent)
        require(("content" in unit) == ("content" in authored))
        require(("content" in unit) == ("meaning_id" in unit))
        span = unit["span"]
        require(type(span) is list and len(span) == 2 and
                all(type(n) is int for n in span) and 0 <= span[0] < span[1] <= len(source))
        require(type(unit.get("status")) is str and unit["status"] in STATUSES)
        size = span[1] - span[0]
        kind = unit["kind"] if type(unit["kind"]) is str else unit["kind"][0]
        kinds[kind] = kinds.get(kind, 0) + size
        statuses[unit["status"]] = statuses.get(unit["status"], 0) + size
        meaning = unit["meaning"]
        if type(meaning) is dict and "unformalised" in meaning:
            reason = meaning["unformalised"]
            reasons[reason] = reasons.get(reason, 0) + 1

    # Every member of the coverage but a block's cells is a function of the request and the unit rows: it is
    # recomputed here and compared whole, so a missing, extra or changed key anywhere in it (a forged residual
    # line included) is unbound. Only the cells are Lean's, and they are bound to the units and the counts.
    coverage = row.get("coverage")
    require(type(coverage) is dict)
    graph = meta.get("graph")
    nodes = graph.get("nodes") if type(graph) is dict else None
    labels = [n["label"] for n in nodes if type(n) is dict and type(n.get("label")) is str] \
        if type(nodes) is list else []
    residual = {"open_terms": len(meta.get("open_terms", [])),
                "assumptions": sum(u["support"] == "assumption" for u in units),
                "bridge_leaves": sum(label.startswith("bridge:accepts(") for label in labels),
                "unresolved_reading_sets": sum(r["status"] == "open" for r in meta.get("reading_sets", []))}
    profiles = meta["environment"].get("profiles", [])
    expected = {}
    if "alternatives@0" in profiles or "risk@0" in profiles:
        cells = coverage.get("alternatives")
        require(type(cells) is dict and set(cells) == set(_BLOCK_LINES) | {"table_complete"})
        by_id = {u["id"]: u for u in units}
        for line in _BLOCK_LINES:
            require(type(cells[line]) is list)
        for line in ("alternatives_declared", "counterfactual_leaves", "proximate_judgments"):
            for cell in cells[line]:
                require(type(cell) is dict and cell.get("unit") in by_id and
                        cell.get("support") == by_id[cell["unit"]]["support"])
        require(same(cells["narrowings"], meta.get("narrowings", [])))
        residual.update({line: len(cells[line]) for line in _BLOCK_LINES})
        residual["table_complete"] = int(cells["table_complete"] is not None)
        expected["alternatives"] = cells
    expected.update({"source_bytes": len(source), "accounted_bytes": len(source), "coverage_percent": 100,
                     "bytes_by_kind": kinds, "bytes_by_status": statuses, "unformalised_reasons": reasons,
                     "residual": residual, "residual_total": sum(residual.values())})
    require(same(coverage, expected))


def _load_document(raw: bytes, path: str | Path, lean):
    """Python's own path: a `ve-document@2` document after Lean's discourse admission (`lean`), and a
    `ve-document@1` document Lean's `document` mode cannot decide yet (`_lean_answer`)."""
    meta, source, fences = _split(raw)
    if not source:
        raise VEError("document source is empty")
    if type(meta.get("environment")) is not dict:
        raise VEError("document needs an embedded environment")
    from .discourse import validate_discourse
    environment_data = base_environment(meta)
    profiles = listed_profiles(environment_data)
    rights_enabled = "rights@0" in profiles
    soft_enabled = "soft-norms@0" in profiles
    defaults_enabled = "norm-defaults@0" in profiles
    if defaults_enabled and soft_enabled:
        # The soft and rights document routes are checked by Lean, whose
        # norm-defaults route has no admission kind for them yet.
        raise UnsupportedProfile("UnsupportedProfile: norm-defaults@0 documents on the soft and rights "
                      "routes await the Lean route")
    attached = _s1_attached(environment_data, meta)
    if soft_enabled and not rights_enabled:
        from .softnorms import check_soft_source
        if type(meta.get("units")) is list:
            # The environment and the norm units are one soft source (8).
            check_soft_source(environment_data, _soft_contents(meta["units"], attached),
                              layers=frozenset({"readings@1"} if "readings@1" in profiles else ()))
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
        from .rights import RightsDocument
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
        from .softnorms import SoftNormDocument
        soft_document = SoftNormDocument(env, _soft_contents(units, attached))
        formula_env = soft_document.extended_env
        open_names = set(open_names) | soft_document.extended_env.decision_names
    senses = None
    if "senses" in meta:
        # RD-8: Lean reads the English fences; their units' environment is Lean's projected one.
        from .senses_document import read_senses
        if (meta["format"] != "ve-document@1" or env.unit_schema is not None
                or set(env.profiles) & {"soft-norms@0", "rights@0", "reports@0", "norm-defaults@0", "readings@1"}):
            raise UnsupportedProfile("UnsupportedProfile: senses are read in ve-document@1 documents without the soft-norms@0, "
                          "rights@0, reports@0, norm-defaults@0, readings@1 and quantity routes")
        # Only a string id names a fence; any other id is refused by the unit checks below.
        english = [(u["id"], fences[u["id"]]) for u, _ in _parts(units)
                   if type(u) is dict and u.get("surface") == "english" and type(u.get("content")) is dict
                   and type(u.get("id")) is str and u["content"].get("fence") == u["id"] and u["id"] in fences]
        senses = read_senses(env, meta["senses"], english, Path(path).parent, meta.get("reading_sets", []))
        formula_env = senses.environment
    rule_results = {}
    if soft_enabled:
        from .softnorms import check_rule_batch
        authored = []
        try:
            for raw, _ in _parts(units):
                content = raw.get("content")
                if type(content) is dict and "norm" in content:
                    authored.append((raw, {"norm": content["norm"]}))
        except VEError:
            # The ordinary unit loop below reports this structural fault in
            # source order, after any earlier per-rule Lean outcome.
            pass
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
        kind = (unit["kind"] if rights_enabled and unit["kind"] in
                ("right", "right_lines", "limitation", "bar") else
                _check_kind(unit["kind"], reports="reports@0" in env.profiles))
        status = _meaning(unit["meaning"], open_names, reports="reports@0" in env.profiles)
        if type(unit["support"]) is not str or unit["support"] not in SUPPORTS:
            raise VEError("invalid support")
        content_env = (env if rights_enabled and kind in ("right", "right_lines", "limitation", "bar")
                       else formula_env)
        content, mid = (_content(content_env, unit, fences, formula_env=formula_env,
                                 rights=rights_enabled, senses=senses, rule_result=rule_results.get(id(unit)))
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
    from .readings_components import has_companions
    # readings-defaults RD-4b: a reading with its own vocabulary is content-bearing (Lean splits the document).
    companions = "readings@1" in env.profiles and has_companions(reading_sets)
    s1_content = "readings@1" in env.profiles and type(reading_sets) is list and (companions or any(
        type(s) is dict and type(s.get("readings")) is list and any(
            type(r) is dict and s1_content_kind(r.get("content")) in
            {"norm", "right", "right_lines", "limitation"} for r in s["readings"])
        for s in reading_sets))
    validate_reading_sets(env if rights_enabled or s1_content else formula_env,
                          reading_sets, unit_ids, source=source,
                          unit_spans={u["id"]: u["span"] for u in compiled},
                          lean_replay=s1_content)
    readings_s1 = None
    readings_components = None
    if companions:
        # readings-defaults 1.9 and 4.5 (RD-4b): Lean splits the document and checks each case by itself; its
        # elaboration, validation and the product's conflict answer are relayed, bound to the request.
        from .readings_components import load as load_components
        readings_components = load_components(env.to_dict(), compiled, reading_sets,
                                              couplings=meta.get("couplings", []),
                                              narrowings=meta.get("narrowings", []))
    elif s1_content:
        from .readings_route import validate as validate_s1
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
        source_ids = [u["id"] for u, _ in _parts(units)
                      if type(u.get("content")) is dict and u.get("id") not in attached and
                      u.get("kind") in ("right", "right_lines", "limitation", "bar", "norm")]
        source_status = dict(zip(source_ids, statuses[1:], strict=True))
        for unit in compiled:
            if unit["status"] == "CHECKED" and source_status.get(unit["id"], False):
                unit["status"] = "OPEN"
    if meta["format"] == "ve-document@1":
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
    # Under readings@1, fixed units attached to an open set are checked in its candidates' documents (S1 1.3).
    selected_norms = [u["content"] for u in norm_units if u["id"] not in reading_units and u["id"] not in attached]
    norms = (NormDocument(env, selected_norms)
             if not soft_enabled and (selected_norms or any(d.regulated is not None for d in env.predicates.values()))
             else None)
    norm_defaults = None
    if defaults_enabled:
        # norm-defaults 2.3: the layers are those of `fill U`, over E‴ with Fill_T.
        from .norm_defaults import UnspecifiedDocument, validate_completions
        defaults_env = env
        if "readings@1" in env.profiles:
            # The free norms are the lower route's document, read with `readings@1` stripped as Lean's readings
            # route hands every other kind down (`Readings.Run.runLower`): the W2 route of a non-content-bearing
            # set, and the norm-defaults document beside content-bearing sets (the readings route admits those).
            lowered = env.to_dict()
            lowered["profiles"] = [p for p in lowered["profiles"] if p != "readings@1"]
            defaults_env = _environment(lowered)
        norm_defaults = UnspecifiedDocument(defaults_env, selected_norms)
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
        from .readings_route import elaborate as elaborate_s2
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
           "reading_plan": plan_choices(active if couplings else
                                        [r for r in active if r["status"] == "open"],
                                        couplings=couplings)}
    if meta["format"] == "ve-document@2":
        doc["discourse"] = validate_discourse(doc, lean)
        for unit in compiled:
            if unit.pop("explicit_status") not in (None, unit["status"]):
                raise VEError("unit status contradicts content, meaning, or active reading set")
    return doc


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
    defaults = doc.get("norm_defaults")
    if defaults is not None and not _unresolved_norm_reading(sets):
        # The filled layers and Fill_T, over E‴ (`_checking_environment`).
        fixed.extend(formula_to_data(defaults.filled.env, formula)
                     for _, formula in (*defaults.filled.premises(), *defaults.fill_premises))
    return fixed


def _checking_environment(doc):
    """The vocabulary in which a document's fixed premises and readings are checked."""
    if doc.get("soft_document") is not None:
        return doc["soft_document"].extended_env
    if doc.get("norm_defaults") is not None:
        return doc["norm_defaults"].filled.env
    if doc.get("senses") is not None:
        return doc["senses"].environment
    return doc["environment"]


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


def _rights_block(content):
    """The rights block a checked content holds (`right`, `right_lines`,
    `limitation` or `bar`), else None."""
    if type(content) is dict and len(content) == 1 and next(iter(content)) in _RIGHTS_KINDS:
        return next(iter(content))
    return None


def _rights_source_units(doc):
    return [{"source_units": [u["id"] for u in doc["units"]]}] + [
        u["content"] for u in doc["units"]
        if u["kind"] in (*_RIGHTS_KINDS, "norm") and type(u["content"]) is dict]


def _content_bearing(doc):
    """Whether the document has a content-bearing reading set (composition-s1.md 1.2); a document whose readings
    carry their own vocabulary has one (readings-defaults 1.9)."""
    if doc.get("readings_components") is not None:
        return True
    row = doc.get("readings_s1")
    return row is not None and row.get("content_bearing") is True


def _lower_route(doc):
    """The environment and soft document of the lower route: under `readings@1`, without the profile."""
    if "readings@1" not in doc["environment"].profiles:
        return doc["environment"], doc["soft_document"]
    data = doc["environment"].to_dict()
    data["profiles"] = [p for p in data["profiles"] if p != "readings@1"]
    return _environment(data), _lower_soft_document(doc)


def _lower_rights_document(doc, lower_env):
    from .rights import RightsDocument
    return RightsDocument(lower_env, _rights_units(doc["meta"]["units"],
                                                   _s1_attached(doc["environment"].to_dict(), doc["meta"])))


def _lower_soft_document(doc):
    """The soft document the lower route checks: under `readings@1` the head strips the profile and hands every
    other case to the lower route (composition-s1.md 4.1), so its environment is the one without it."""
    soft = doc["soft_document"]
    if "readings@1" not in doc["environment"].profiles or (soft is None and doc["rights_document"] is None):
        # The norms chain has no soft document, with or without `readings@1` (DRI ruling 4: a norms document with
        # `norm-defaults@0` and `readings@1` reaches this with a claim graph).
        return soft
    data = doc["environment"].to_dict()
    data["profiles"] = [p for p in data["profiles"] if p != "readings@1"]
    lower = _environment(data)
    attached = _s1_attached(doc["environment"].to_dict(), doc["meta"])
    if doc["rights_document"] is not None:
        from .rights import RightsDocument
        return RightsDocument(lower, _rights_units(doc["meta"]["units"], attached)).soft_document
    from .softnorms import SoftNormDocument
    return SoftNormDocument(lower, _soft_contents(doc["meta"]["units"], attached))


def _rights_units(units, exclude=frozenset()):
    """The rights source of a document's units: the unit ids, then every rights or norm content."""
    ids = [u.get("id") for u, _ in _parts(units) if type(u) is dict and type(u.get("id")) is str]
    return [{"source_units": ids}] + [
        u["content"] for u, _ in _parts(units)
        if type(u.get("content")) is dict and u.get("id") not in exclude and
        u.get("kind") in ("right", "right_lines", "limitation", "bar", "norm")]


def _rights_report(doc):
    """The Lean-replayed rights report, or None while a rights reading set still
    needs per-choice elaboration (its findings are then not yet known)."""
    rights = doc.get("rights_document")
    if rights is None:
        return None
    if _content_bearing(doc):
        # composition-s1.md 4.8: the rights report keeps "per-choice rights elaboration pending".
        return None
    if any(c["kind"] in _RIGHTS_KINDS
           for reading_set in active_reading_sets(doc["meta"].get("reading_sets", []))
           for c in reading_set["readings"]):
        return None
    from .rights_route import report_rights
    return report_rights(doc["environment"], _rights_source_units(doc), rights)


def coverage_defaults(doc):
    """norm-defaults 3.2 lines for a document (a translation over source prose):
    gap and default-reached evidence from a small-model search or a certificate,
    and grounding against the `completions` block. Computed once per document."""
    if "_norm_defaults_report" not in doc:
        from .norm_defaults import report
        doc["_norm_defaults_report"] = report(
            doc["norm_defaults"], prove=True, search_domain_size=2, translation=True,
            completions=doc["meta"].get("completions", {}),
            unit_ids={u["id"] for u in doc["units"]})
    return doc["_norm_defaults_report"]


def coverage(doc, scoped=None, rights_report=None):
    """`scoped`: the reports layer's checked scoped verdicts (`check_document`);
    without them a scoped check is reported as not replayed. `rights_report`: the
    replayed rights report when the caller already has it. A document Lean's `document` mode accepted has
    Lean's coverage (batch 16b)."""
    if "lean" in doc:
        return deepcopy(doc["lean"]["coverage"])
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
            # Lean supplies every nested status and its reason.
            nested = next(row["nested"] for row in doc["reports"].statuses()["units"]
                          if row["id"] == u["id"])
            for node in nested:
                if node["item"] != "unformalised":
                    continue
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
        lines = doc["reports"].residual_lines()
        residual.update({line: sum(detail.values()) if type(detail) is dict else len(detail)
                         for line, detail in lines.items()})
    alternatives = None
    soft = doc.get("soft_document")
    environment = doc.get("environment") or (soft.env if soft is not None else None)
    if environment is not None and environment.alternatives is not None:
        from .backends.relay import decide
        risk = environment.risk is not None
        # A unit without content (or meaning id) is sent without the field: the wire has no null.
        case = {"id": "coverage", "kind": "risk-elaborate" if risk else "alt-elaborate",
                "environment": environment.to_dict(),
                "coverage_units": [{key: value for key, value in u.items() if value is not None} for u in units],
                "narrowings": meta.get("narrowings", [])}
        if risk:
            case["document"] = {"norms": [], "units": []}
        else:
            case["norms"] = []
        row = decide("risk" if risk else "alternatives", [case])[0]
        alternatives = row["coverage"]["alternatives"]
        residual.update(row["coverage"]["residual"])
    soft = doc.get("soft_document")
    if soft is not None:
        from .soft_route import elaborate_soft_document
        soft_row = elaborate_soft_document(_lower_soft_document(doc) if "environment" in doc else soft)
        residual.update(soft_row["soft_residual"])
        by_decider = soft_row["default_exceptions_by_decider"]
        open_pairs = soft_row["conditional_on"]
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
    if _content_bearing(doc):
        # composition-s1.md 6: separations by probe form, findings, pending candidates, and the couplings line
        # on every chain.
        from .readings_route import report as readings_report
        readings = readings_report(doc)
        residual["separations"] = sum(readings["separations"].values())
        residual["readings_findings"] = sum(readings["findings"].values())
        residual["pending_candidates"] = readings["pending_candidates"]
        residual["couplings"] = readings["couplings"]
    defaults_lines = None
    if doc.get("norm_defaults") is not None:
        # norm-defaults 3.2: a gap is no open term and changes no unit status.
        defaults_lines = coverage_defaults(doc)
        gaps = defaults_lines["residual"]
        residual["gaps"] = len(gaps["gaps"])
        residual["ungrounded_defaults"] = gaps["ungrounded_defaults"]
    rights_open = ("limitation_terms", "bar_terms")
    return {"source_bytes": len(source), "accounted_bytes": sum(kinds.values()),
            "coverage_percent": 100, "bytes_by_kind": kinds, "bytes_by_status": statuses,
            "unformalised_reasons": reasons,
            "residual": residual, "residual_total": sum(residual.values()),
            **({"residual_lines": lines} if lines else {}),
            **({"alternatives": alternatives} if alternatives is not None else {}),
            **({"norm_defaults": {
                "gaps": gaps["gaps"],
                "findings": defaults_lines["findings"]}}
               if defaults_lines is not None else {}),
            **({"soft_status": "OPEN" if soft_row["soft_status"] == "OPEN" or
                any(residual.get(key) for key in rights_open) else "CHECKED",
                "default_exceptions_by_decider": by_decider,
                "soft_residual_labels": [*sorted(item["name"] for item in soft_row["decisions"]), *open_pairs],
                "soft_background_labels": [item["label"] for item in soft_row["background"]
                                           if item["generator"] == "soft" and
                                           item["label"].startswith("soft:exception:")]}
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
    return _check_document(path)


def _check_document(path):
    doc = _load(Path(path), admit=True)
    if "discourse" not in doc:
        return _report(doc)
    try:
        return _report(doc)
    except CheckerUnavailable:
        raise
    except Exception as exc:
        # Lean admitted the document (load_document): Python never rejects it on its own
        from .discourse import unavailable_report
        raise unavailable_report(exc) from exc


def _report(doc):
    joint = doc.get("discourse", {}).get("joint")
    joint_pending = joint is not None and joint["status"] == "UNKNOWN"
    soft = doc["soft_document"]
    if doc["reports"] is not None:
        from .reports_route import run_case
        meta = doc["meta"]
        route_doc = {"units": [_wire_unit(u) for u in doc["units"]],
                     "contexts": meta.get("contexts", []), "assessments": meta.get("assessments", []),
                     "bridges": meta.get("bridges", []), "scoped": meta.get("scoped", []),
                     "open_terms": [o["name"] for o in meta.get("open_terms", [])],
                     **({"graph": meta["graph"]} if "graph" in meta else {})}
        environment = meta["environment"]
        reports = doc["reports"]
        reports.replay()
        checked = reports.route_answer()
        statuses = reports.statuses()
        result = {"format": doc["meta"]["format"], "status": "UNVERIFIED",
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
    env = _checking_environment(doc)
    if env.unit_schema is not None:
        return _check_quantity_document(doc, active_reading_sets(doc["meta"].get("reading_sets", [])))
    fixed, active = _fixed_and_active(doc)
    assertions = [formula_from_data(env, ast) for ast in fixed]
    rights_report = _rights_report(doc)
    result = {"format": doc["meta"]["format"], "source_id": doc["source_id"],
              "document_id": doc["document_id"],
              "coverage": coverage(doc, rights_report=rights_report),
              "reading_plan": doc["reading_plan"]}
    if soft is not None:
        from .soft_route import elaborate_soft_document
        elaborate_soft_document(_lower_soft_document(doc))
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
    defaults = doc.get("norm_defaults")
    if defaults is not None:
        lines = coverage_defaults(doc)
        result["norm_defaults"] = {
            "environment_id": doc["environment"].environment_id,
            "filled_environment_id": defaults.filled.env.environment_id,
            "fill_hash": defaults.fill_hash,
            "unsaid_predicates": [f"unsaid__{p}" for p in defaults.unspec],
            "background_labels": [label for label, _ in defaults.fill_premises],
            "report": {line["predicate"]: line["lines"] for line in lines["report"]}}
    if "graph" in doc["meta"] and joint_pending:
        result["admission"] = {"status": "UNKNOWN",
                               "reason": "discourse citation and report extension pending"}
    # A document Lean's `document` mode admitted (`check_document`) had its claim graph's reading checks, W2
    # admission and narrowing choices decided there; Python asks the admission route for the report only.
    lean_admitted = doc.get("lean", {}).get("admitted", False)
    if "graph" in doc["meta"] and not joint_pending and not lean_admitted:
        nodes = _graph_nodes(doc["meta"]["graph"])
        if (_unresolved_norm_reading(active) and
                any(type(node) is dict and type(node.get("label")) is str
                    and node["label"].startswith("layer:norms:")
                    for node in nodes)):
            raise VEError("non-assertion norm reading admission needs an elaborator")
        from .admission import parse_label
        active_keys = {(r["id"], r["version"]): r for r in active}
        for node in nodes:
            label = parse_label(node.get("label")) if type(node) is dict else None
            if label is not None and label.kind == "readings":
                reading_set = active_keys.get(label.args[:2])
                if reading_set is None:
                    raise VEError("graph cites a stale or unknown reading set version")
                if any(c["kind"] != "asserted" or c["content"] is None
                       for c in reading_set["readings"]):
                    raise VEError("non-assertion reading admission needs an elaborator")
    if "graph" in doc["meta"] and not joint_pending:
        from .admission import parse_label
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
        # Under readings@1 the graph is the lower route's case (composition-s1.md 4.1): its environment is the
        # one without the profile, and the fixed units attached to an open set are not in it.
        lower_env, lower_soft = _lower_route(doc)
        if rights is not None:
            from .rights_route import admit_rights_document
            lower_rights = (rights if lower_env is doc["environment"] else
                            _lower_rights_document(doc, lower_env))
            result["admission"] = admit_rights_document(lower_env, admission, lower_rights)
        elif soft is not None:
            from .soft_route import admit_soft_document
            result["admission"] = admit_soft_document(lower_env, admission, soft_document=lower_soft)
        elif defaults is not None:
            # W1's admission on `fill U`, from the source environment (Lean
            # `VE.NormDefaults.Admission`); the report is over E‴ (`env`).
            result["admission"] = admit_document(lower_env, admission)
        elif lean_admitted:
            try:
                result["admission"] = admit_document(env, admission)
            except (CheckerUnavailable, ResourceLimit):
                raise
            except VEError as exc:
                raise CheckerUnavailable("CheckerUnavailable: the admission route rejects a claim graph Lean's "
                                         f"document mode admitted: {exc.message}") from exc
        else:
            result["admission"] = admit_document(env, admission)
        latest = {}
        for rs in doc["meta"].get("reading_sets", []):
            latest[rs["id"]] = max(latest.get(rs["id"], 0), rs["version"])
        labels = [a.get("label") for a in result["admission"]["report"]["assumptions"]]
        if not lean_admitted:
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
    if joint is not None and joint["constraints"]:
        # the joint disjunction is Lean's (`Joint(K)`, docs/spec/discourse.md 4.8); a premise only
        # when every reading of an open set is an assertion with content
        joint_formula = None
        if joint["status"] == "complete" and all(c["kind"] == "asserted" and c["content"] is not None
                                                 for r in active if r["status"] == "open"
                                                 for c in r["readings"]):
            joint_formula = formula_from_data(env, doc["discourse"]["joint_formula"])
            assertions.append(joint_formula)
    else:
        assertions.extend(_assertion_disjunctions(env, active))
    if env.alternatives is not None:
        result["premises"] = {"status": "UNKNOWN",
                              "reason": "alternatives premise satisfiability requires the alternatives route"}
    elif _content_bearing(doc):
        # composition-s2.md 1.1, 4.5 and 4.6: the premises across readings on the superposed or the enumerated
        # route, each verdict from evidence Lean checked; the pending row keeps today's UNKNOWN.
        from .readings_verdicts import context
        result["premises"] = context(doc).premises()
    elif _unresolved_norm_reading(active):
        result["premises"] = {"status": "UNKNOWN", "reason": "non-assertion reading elaboration pending"}
    elif joint_pending or (joint is not None and joint["constraints"] and joint_formula is None):
        result["premises"] = {"status": "UNKNOWN", "reason": "joint choice enumeration or elaboration pending"}
    else:
        result["premises"] = premise_status(env, assertions)
        if (result["premises"]["status"] != "INCONSISTENT"
                and any(c["kind"] != "asserted" or c["content"] is None
                        for r in active for c in r["readings"])):
            result["premises"] = {"status": "UNKNOWN", "reason": "non-assertion reading elaboration pending"}
    if "admission" in result and "report" in result["admission"]:
        status = result["premises"]["status"]
        result["admission"]["vacuous"] = (True if status == "INCONSISTENT" else
                                           False if status == "model" else None)
    if _content_bearing(doc):
        from .readings_route import report as readings_report
        result["readings"] = readings_report(doc)
    if "discourse" in doc:
        from .discourse import report_discourse
        report_discourse(doc, result)
    return result


def _graph_nodes(graph):
    """The nodes of a claim graph as the pre-admission checks read them: none for a graph or node list of the
    wrong JSON type, which W2 admission then rejects with its own diagnostic."""
    nodes = graph.get("nodes", []) if type(graph) is dict else []
    return nodes if type(nodes) is list else []


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
        try:
            return render(Document((formula,)), render_env, "ve_english").strip()
        except VEError:
            # Decision predicates are generated by the soft-norms document layer;
            # the English request carries only the submitted vocabulary. Display
            # their checked strict form until the statement layer has a Lean
            # rendering for these generated symbols.
            from .search import _used_predicates
            if not any(name.startswith("soft__") for name in _used_predicates(formula)):
                raise
            from .parser import parse
            strict = render(Document((formula,)), render_env, "ve_strict")
            if parse(render_env, strict) != Document((formula,)):
                raise VEError("The generated decision has no checked display form")
            return strict.strip()

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

    def kind_wording(kind, content, rights=None, vocabulary=None):
        """`rights`: the correlated document `content` was checked in, when it is
        not the base one (a right-reading candidate is checked on its own)."""
        if content is None:
            return f"The passage is recorded as {kind_description(kind)}."
        block = _rights_block(content)
        if block is not None:
            # The content's own block decides the rendering; the kind only how
            # the source presents it.
            from .surface.rights import render_unit
            text = render_unit(doc["rights_document"] if rights is None else rights, content)
            return text if kind == block else f"{text} The source presents this as {kind_description(kind)}."
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
                    if rule.get("alterable") or rule.get("rank"):
                        from .surface.softnorms import rule_paraphrase
                        description += " " + rule_paraphrase(rule["name"], "strict",
                                                             alterable=rule.get("alterable", ()),
                                                             rank=rule.get("rank"))
                # The rule itself (guard and carve-outs), then every field the lines
                # above leave out: precedence, exception conditions, factors, citations.
                from .norm_english import render_rule_sentence
                from .softnorms import decode_rule
                from .surface.rights import citation_notes, rule_notes
                text_env = doc["soft_document"].env
                decoded = decode_rule(text_env, {"norm": rule})
                description = " ".join((description, render_rule_sentence(decoded, text_env),
                                        *rule_notes(decoded, text_env, switches=False),
                                        *citation_notes(content.get("cites"))))
                return (description if kind == "norm" else
                        f"{description} The source presents this as {kind_description(kind)}.")
            from .norms import NormDocument
            from .norm_english import render_rule_sentence
            rule = NormDocument._decode(content)
            claim = render_rule_sentence(rule, doc["environment"] if vocabulary is None else vocabulary)
            if rule.over:
                claim += " Exception to " + ", ".join(rule.over) + "."
            return claim if kind == "norm" else f"{claim} The source presents this as {kind_description(kind)}."
        claim = wording(content)
        if kind == "asserted":
            return claim
        return f"{claim} The source presents this as {kind_description(kind)}."

    def candidate_units(content):
        # A right candidate is checked alone over the document's source units
        # (validate_reading_sets), not in the base document: its line objects
        # and right name live only in that correlated document.
        if doc["rights_document"] is None or _rights_block(content) != "right":
            return None
        return [{"source_units": sorted(u["id"] for u in doc["units"])}, content]

    def candidate_rights(content):
        # Its wording reads the rules alone, so the soft document is deferred (`SoftNormDocument`).
        units = candidate_units(content)
        if units is None:
            return None
        from .rights import RightsDocument
        return RightsDocument(doc["environment"], units, deferred=True)

    active_by_unit = {r["unit"]: r for r in active_reading_sets(doc["meta"].get("reading_sets", []))}
    # Every right candidate's line rules in one Lean request per source, not one per candidate.
    shown = [candidate_units(candidate["content"]) for u in doc["units"]
             for candidate in active_by_unit.get(u["id"], {}).get("readings", ())]
    if any(units is not None for units in shown):
        from .rights import RightsDocument
        RightsDocument.warm_rules(doc["environment"], [units for units in shown if units is not None])
    s1_wording = None
    component_environments = {}
    if doc.get("readings_components") is not None:
        from .readings_components import PartsWording
        s1_wording = PartsWording(doc)
        for part in doc["readings_components"]["parts"]:
            from .environment import Environment
            for reading_set in part["document"].get("reading_sets") or []:
                component_environments[reading_set["id"]] = Environment(part["environment"])
    elif _content_bearing(doc):
        from .readings_route import Wording
        s1_wording = Wording(doc)
    for u in doc["units"]:
        lines.append(u["source"].strip())
        expanded = doc.get("discourse", {}).get("presentations", {}).get(u["id"])
        if expanded is not None:
            lines.append("Reviewed wording: " + expanded.strip())
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
                # A coupled axis's label says which reading a coupling chooses together (6.2).
                labels = candidate.get("labels") or {}
                if labels:
                    lead += " (" + ", ".join(f"{axis} {value}" for axis, value in sorted(labels.items())) + ")"
                lines.append(f"{lead}: " + kind_wording(candidate["kind"], candidate["content"],
                                                        candidate_rights(candidate["content"]),
                                                        component_environments.get(reading_set["id"])))
            if s1_wording is not None and reading_set["status"] == "open":
                # composition-s1.md 2.3: each checked pair's wording, then E16 under the set.
                lines.extend(s1_wording.set_lines(u["id"]))
    sets = {r["id"]: r for r in active_reading_sets(doc["meta"].get("reading_sets", []))}
    for coupling in doc["meta"].get("couplings", []):
        if "readings@1" in doc["environment"].profiles and "rights@0" not in doc["environment"].profiles:
            from .readings_english import coupling_sentence
            lines.append(coupling_sentence(coupling, sets, doc["units"]))
            continue
        units = [sets[ref["set"]]["unit"] for ref in coupling["sets"]]
        lines.append(f"Reading units {', '.join(units[:-1])} and {units[-1]} with the same "
                     f"{coupling['axis']}, because {', '.join(coupling['reason_spans'])} "
                     f"(coupling {coupling['id']} by {coupling['by']}).")
    return "\n".join(lines) + "\n"


def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser(prog="ve document")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("check", "render", "coverage", "readings"):
        sub.add_parser(name).add_argument("path")
    sub.choices["readings"].add_argument("--conclusion", help="formula AST JSON file to classify")
    sub.choices["readings"].add_argument("--narrowing", help="apply a recorded narrowing by id")
    sub.choices["readings"].add_argument("--under", action="append", metavar="SET:INDEX",
                                         help="a named reading of a content-bearing set (composition-s2.md 4.5)")
    sub.choices["readings"].add_argument("--sentence", metavar="UNIT",
                                         help="the sentence checked by itself the conclusion is about "
                                              "(readings-defaults 4.5)")
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
        elif args.under and not args.conclusion:
            raise VEError("--under requires --conclusion")
        elif args.sentence and not args.conclusion:
            raise VEError("--sentence requires --conclusion")
        elif args.conclusion:
            conclusion = json.loads(Path(args.conclusion).read_text())
            if _content_bearing(doc):
                # composition-s2.md 4.5 and 4.6: ALL, SOME or NONE across the readings of a content-bearing
                # document. Every narrowing in force is already a premise there (1.2); `--narrowing` is W2's.
                if args.narrowing:
                    raise VEError("--narrowing applies to W2's route; on the superposed and enumerated routes "
                                  "every narrowing in force is a premise")
                from .readings_verdicts import context
                from .readings_s2_wording import query_english
                assumed = None
                if args.under:
                    assumed = []
                    for item in args.under:
                        set_id, _, index = item.rpartition(":")
                        if not set_id or not index.isdigit():
                            raise VEError("--under takes SET:INDEX")
                        assumed.append((set_id, decimal_value(index)))
                if doc.get("readings_components") is not None:
                    # readings-defaults 4.5 (RD-4b): the query is typed in one sentence checked by itself, Lean's.
                    from .readings_components import query as components_query
                    data = components_query(doc, conclusion, assumed=assumed, sentence=args.sentence)
                    print(json.dumps(data, ensure_ascii=False, indent=2))
                    return 0
                if args.sentence:
                    raise VEError("--sentence names a sentence checked by itself; this document has none")
                data = context(doc).entailment(conclusion, assumed=assumed)
                data["english"] = query_english(doc, conclusion, data)
                print(json.dumps(data, ensure_ascii=False, indent=2))
                return 0
            if args.under:
                raise VEError("--under names readings of a content-bearing set (composition-s2.md 4.5)")
            if args.sentence:
                raise VEError("--sentence names a sentence checked by itself; this document has none")
            active = active_reading_sets(doc["meta"].get("reading_sets", []))
            sets = [{**r, "readings": [{**c, "original_index": i}
                                      for i, c in enumerate(r["readings"])]} for r in active]
            joint = doc.get("discourse", {}).get("joint")
            if args.narrowing:
                matching = [n for n in doc["meta"].get("narrowings", []) if n["id"] == args.narrowing]
                if len(matching) != 1:
                    raise VEError("unknown narrowing")
                narrowing = matching[0]
                if not any((r["id"], r["version"]) == (narrowing["set"], narrowing["version"])
                           for r in sets):
                    raise VEError("narrowing does not target an active reading set")
                if joint is not None and joint["status"] == "complete":
                    rs = next(r for r in sets if (r["id"], r["version"]) ==
                              (narrowing["set"], narrowing["version"]))
                    kept = {i for i, candidate in enumerate(rs["readings"])
                            if candidate["id"] in narrowing["keeps"]}
                    key = f"{rs['id']}@{rs['version']}"
                    joint = {**joint, "choices": [c for c in joint["choices"]
                                                   if c.get(key) in kept]}
                    if not joint["choices"]:
                        raise VEError(f"InvalidCompatibility: narrowing {narrowing['id']}")
                    joint["count"] = len(joint["choices"])
                elif joint is None:
                    sets = [{**r, "readings": [c for c in r["readings"] if c["id"] in narrowing["keeps"]]}
                            if (r["id"], r["version"]) == (narrowing["set"], narrowing["version"]) else r
                            for r in sets]
            data = check_readings(_checking_environment(doc), sets, conclusion,
                                  fixed=_fixed_premises(doc, sets),
                                  joint_choices=joint,
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
