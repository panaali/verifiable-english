"""The relay of Lean's `document` mode: the case sent, the answer read, and the document built from the answer
once it is bound to the document sent (moved from `ve/document.py`, AR-16a)."""
from __future__ import annotations

import json
from pathlib import Path

from ..ast import decimal_value
from ..backends.lean_service import CheckerUnavailable
from ..environment import Environment, listed_profiles
from ..errors import ResourceLimit, VEError
from ..identity import source_id
from ..openterms import validate_open_terms
from ..readings import active_reading_sets, rights_meaning_id
from ..wire import digest
from .source import (STATUSES, _RIGHTS_KINDS, _document_id, _english_fences, _environment, _parts, _split,
                     base_environment, chain_environment)
from .containers import (_content_environment, _defaults_environment, _free_norms, _reading_plan, _readings_routes,
                         _rights_block, _rights_units, _s1_attached, _soft_contents)


# Lean's refusal of a lexicon proposal for another environment than the one it reads the fences in
# (`VE.EnglishGrammar.Run.decodeLexicon`; `tests/test_scope_document.py` reads it from there).
PROPOSAL_ELSEWHERE = "InvalidInput: the lexicon names another environment"


def _document_case(raw: bytes, admit: bool, directory: Path | None = None, prepared: dict | None = None):
    """The `document` mode's case for a text, or None when Python's own path decides it: the text is not UTF-8, which
    the mode cannot be sent, or pending content-bearing readings under norm defaults still need the original Python
    coverage path. A text with English fences carries the lexicon proposal; a senses document's pack files are read
    beside it (`directory`) and sent as texts, with the proposal its senses route reads (batch 16f). A soft document
    built for the proposal is kept in `prepared` for the document built from the answer (`_lean_document`)."""
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return None
    try:
        meta, _, fences = _split(raw)
    except (KeyError, TypeError, VEError):
        meta = fences = None  # Let Lean decide malformed front matter and preserve its diagnostic.
    try:
        profiles = listed_profiles(meta.get("environment"))
        sets = meta.get("reading_sets", [])
        if {"readings@1", "norm-defaults@0"} <= set(profiles) and type(sets) is list:
            contents = [r.get("content") for s in sets if type(s) is dict
                        for r in s.get("readings", []) if type(r) is dict]
            if any(c is None for c in contents) and any(c is not None for c in contents):
                return None
    except (AttributeError, KeyError, TypeError, VEError):
        pass  # Let Lean decide malformed front matter and preserve its diagnostic.
    case = {"id": "document", "document": text, "admit": admit}
    if meta is not None and "senses" in meta and directory is not None:
        from ..senses_document import pack_texts
        texts = pack_texts(meta["senses"], directory)
        if texts is not None:
            case["packs"] = texts
    try:
        if "packs" in case or b"```ve " in raw and any(u.get("surface") == "english" and u.get("id") in fences
                                                       for u, _ in _parts(meta["units"])):
            from ..english import EnglishVocabulary
            from ..english_grammar import export
            # The proposal names the environment the chain reads the fences in (`chain_environment`).
            environment = chain_environment(meta["environment"])
            profiles = listed_profiles(environment)
            if "soft-norms@0" in profiles and "rights@0" not in profiles:
                # Batch 16f: a soft-norms document's fences are read in the soft route's `E″`, which the
                # proposal names (Lean `Service.Document.softLayer`).
                from ..softnorms import SoftNormDocument
                soft_document = SoftNormDocument(_environment(environment), _soft_contents(meta["units"]))
                if prepared is not None:
                    prepared["soft_document"] = soft_document
                words = soft_document.extended_env
            else:
                # A senses document's route reads the same proposal (`read_fences`, batch 16f).
                words = Environment(environment)
            case["lexicon"] = export(EnglishVocabulary(words))
    except (AttributeError, KeyError, TypeError, VEError, CheckerUnavailable):
        pass  # Lean checks the document before a fence needs the proposal.
    return case


def _lean_answer(raw: bytes, admit: bool, directory: Path | None = None, prepared: dict | None = None):
    """Lean's `document` row for a `ve-document@1` text, or None when Python's own path decides it: the mode
    answered `CheckerUnavailable` or `ResourceLimit` (it cannot decide, and says so), or the case cannot be sent
    (`_document_case`). A `ResourceLimit` for a document under a wrapper profile (`_lean_only`) is raised: no other
    path can decide it, and the limit is UNKNOWN, never Python's refusal of the profile. Any other rejection is Lean's diagnostic, raised verbatim; a failure of the service itself is
    raised, never answered by Python."""
    case = _document_case(raw, admit, directory, prepared)
    if case is None:
        return None
    from ..backends.relay import answer
    row, error = answer("document", case)
    if isinstance(error, ResourceLimit) and _lean_only(raw):
        # Python's own path cannot read a wrapper profile (`chain_environment`), so Lean's UNKNOWN is the answer.
        raise error
    if isinstance(error, (CheckerUnavailable, ResourceLimit)):
        return None
    if error is not None and getattr(error, "path", None) and not _names_a_model_member(raw, error.path):
        # Batch 16f: a located diagnostic (a distinguishing model's, `Service.Document.locatedModel`) names a member
        # of a model the document supplies, or it is not bound to the document sent.
        raise CheckerUnavailable("CheckerUnavailable: the Lean document answer's path names no member of a "
                                 "distinguishing model of the document sent")
    if error is not None and "lexicon" in case and str(error) == PROPOSAL_ELSEWHERE:
        # The proposal is the relay's, built before Lean answers: Lean's chain read the fences in another environment
        # than it names, which is a fault of the case sent, never the document's diagnostic. Under `scope@0` the soft
        # route's `E″` is that of the governed rules (`Service.Document.softLayer` over `withUnits`), which the relay
        # cannot read before Lean answers; it builds the proposal from the rules as written.
        raise CheckerUnavailable("CheckerUnavailable: Lean's chain reads the English fences in another environment "
                                 "than the lexicon proposal the case carries names")
    if error is not None and getattr(error, "span", None) is not None and not _spans_a_strict_fence(raw, error.span):
        # Batch 16f: a strict fence's located diagnostic (`Service.Document.locatedFence`) is a span in the text of a
        # strict fence the document has, with its line and column.
        raise CheckerUnavailable("CheckerUnavailable: the Lean document answer's span is in no strict fence of the "
                                 "document sent")
    if error is not None:
        raise error
    return row


def _lean_only(raw: bytes) -> bool:
    """Whether the document lists a wrapper profile only Lean's `document` mode reads (`chain_environment` lowers it):
    Python's own path refuses it at the environment, so it never answers in Lean's place."""
    try:
        environment = _split(raw)[0].get("environment")
        return chain_environment(environment) is not environment
    except (AttributeError, KeyError, TypeError, ValueError, VEError):
        return False


def _spans_a_strict_fence(raw: bytes, span) -> bool:
    """Whether `span` lies in the text of a strict-surface unit's fence, with that text's line and column (the
    binding `x-source-span` gives a `parse` answer's span over its request source)."""
    try:
        meta, _, fences = _split(raw)
        units = [u for u, _ in _parts(meta["units"])]
    except (VEError, KeyError, TypeError, ValueError):
        return False
    start, end, line, column = (getattr(span, key, None) for key in ("start", "end", "line", "column"))
    if not all(type(value) is int for value in (start, end, line, column)):
        return False
    for unit in units:
        uid = unit.get("id") if type(unit) is dict else None
        if (type(uid) is not str or unit.get("surface") != "strict" or unit.get("content") != {"fence": uid}
                or uid not in fences):
            continue
        text = fences[uid]
        if (0 <= start <= end <= len(text) and line == text.count("\n", 0, start) + 1
                and column == start - text.rfind("\n", 0, start)):
            return True
    return False


def _names_a_model_member(raw: bytes, path) -> bool:
    """Whether the JSON pointer `path` names a member of a distinguishing model the document supplies (a reading
    set's `models`): every token an object key or an in-range decimal list index (RFC 6901)."""
    try:
        meta, _, _ = _split(raw)
    except (VEError, KeyError, TypeError, ValueError):
        return False
    if type(path) is not str or not path.startswith("/"):
        return False
    tokens = [t.replace("~1", "/").replace("~0", "~") for t in path.split("/")[1:]]
    sets = meta.get("reading_sets")
    for reading_set in sets if type(sets) is list else ():
        models = reading_set.get("models") if type(reading_set) is dict else None
        for model in models.values() if type(models) is dict else ():
            node = model
            for token in tokens:
                if type(node) is dict and token in node:
                    node = node[token]
                elif (type(node) is list and token.isascii() and token.isdigit()
                      and (token == "0" or not token.startswith("0")) and decimal_value(token) < len(node)):
                    node = node[decimal_value(token)]
                else:
                    break
            else:
                return True
    return False


def _lean_document(raw: bytes, path: Path, row: dict, *, admitted: bool, prepared: dict | None = None):
    """The document Lean's `document` mode accepted, built from its answer (docs/LEAN-FIRST-PLAN.md rule 2: Lean
    validates, Python constructs). The row is bound to the request first: its source is the text's body and its
    units are the front matter's, in order, with content exactly where the front matter has some. A row that
    is not, or a document that cannot be built from it, is `CheckerUnavailable`, never a verdict."""
    from ..norms import NormDocument

    def unavailable(what):
        return CheckerUnavailable(f"CheckerUnavailable: the Lean document answer {what}")
    try:
        meta = json.loads(raw[4:raw.find(b"\n---\n", 4)].decode("utf-8"))
        _, body, fences = _split(raw)
        declared = [(u, parent) for u, parent in _parts(meta["units"])]
    except Exception as exc:  # noqa: BLE001 - Lean accepted this front matter
        raise unavailable("is for a front matter Python cannot read") from exc
    try:
        # The identities Lean answered are those of the environment its chain reads (`chain_environment`).
        env = _environment(chain_environment(meta["environment"]))
        senses = None
        if "senses" in meta:
            # Batch 16f: the senses route's reading of the English fences, which Lean's `document` mode composed
            # (`Service.Document.sensesLayer`). The answer is bound to it: each fence's content is the formula
            # this reading holds, and is absent exactly where it holds none (a preamble line or an open unit).
            from ..senses_document import read_senses
            senses = read_senses(env, meta["senses"], _english_fences(meta["units"], fences), path.parent,
                                 meta.get("reading_sets", []))
    except Exception as exc:  # noqa: BLE001 - a document Lean accepted that Python cannot build is a bug
        raise unavailable(f"could not be built: {type(exc).__name__}: {exc}"[:300]) from exc
    try:
        _bind_document_answer(body, meta, declared, row, senses)
        source, units = row["source"].encode("utf-8"), row["units"]
    except Exception as exc:  # noqa: BLE001 - an accepted but malformed service row is unavailable
        raise unavailable("is not bound to the document sent") from exc
    try:
        if row["source_id"] != source_id(source, env) or row["document_id"] != _document_id(meta, source, fences):
            raise unavailable("is not bound to the document sent")
        governed = _governed_units(meta)
        if governed:
            # scope@0: the identities are the document's as written; every container below, and every later read of
            # the front matter, reads the units Lean's chain read (`Service.Document.withUnits`), each governed rule
            # as the bound answer composed it, never as written.
            meta = _with_governed_units(meta, governed, units)
        rights_document = soft_document = None
        # A senses document's units are read in the senses route's projected environment.
        formula_env = env if senses is None else senses.environment
        soft = "soft-norms@0" in env.profiles and "rights@0" not in env.profiles
        if soft:
            # Batch 16f: the soft document Lean's `document` mode composed from the soft route
            # (`Service.Document.softLayer`); its units' contents and statuses are the answer's.
            from ..softnorms import SoftNormDocument
            # The soft document prepared for the proposal holds the rules as written, which govern may change.
            soft_document = ((prepared or {}).get("soft_document") if not governed else None) or \
                SoftNormDocument(env, _soft_contents(meta["units"]))
            formula_env = soft_document.extended_env
        if "rights@0" in env.profiles:
            # Batch 16e: the containers of the rights source Lean's `document` mode decoded with the rights route
            # (`Service.Document.rightsDoc`); Lean's unit statuses and contents are the answer's, not theirs.
            from ..rights import RightsDocument
            rights_document = RightsDocument(env, _rights_units(meta["units"]),
                                             open_predicates=validate_open_terms(env, meta.get("open_terms", [])))
            soft_document = rights_document.soft_document
            formula_env = soft_document.extended_env
        for unit in units:
            # A rights document's content is bound to its content environment, with the nullable decider slots
            # `_content` keeps (`rights_meaning_id`, Lean's `nullableMeaningId`).
            if "content" in unit and unit["meaning_id"] != (
                    rights_meaning_id(_content_environment(env, formula_env, unit["kind"]), unit["content"])
                    if soft_document is not None else
                    digest(f"ve-meaning-{formula_env.identity_version}\n",
                           {"environment_id": formula_env.environment_id, "ast": unit["content"]})):
                raise unavailable("is not bound to the document sent")
        # A rights block the binding found equal to the authored one is built as the authored object itself: the
        # rights containers hold the source's lines by identity (`ve.surface.rights._line`), as on Python's path.
        compiled = [{"id": u["id"], "span": u["span"], "kind": u["kind"], "meaning": u["meaning"],
                     "support": u["support"], "source": source[u["span"][0]:u["span"][1]].decode("utf-8"),
                     "content": (authored["content"] if _rights_block(u.get("content")) else u.get("content")),
                     "meaning_id": u.get("meaning_id"), "status": u["status"],
                     **({"parent_id": u["parent_id"]} if "parent_id" in u else {})}
                    for u, (authored, _) in zip(units, declared, strict=True)]
        active = active_reading_sets(meta.get("reading_sets", []))
        selected = _free_norms(compiled, active, _s1_attached(base_environment(meta), meta))
        if "norm-defaults@0" in env.profiles:
            from ..norm_defaults import UnspecifiedDocument
            norm_defaults = UnspecifiedDocument(_defaults_environment(env), selected)
            norms = None
        elif soft_document is not None:
            norm_defaults = norms = None
        else:
            # Batch 16f: the free norm document of a plain `norms@0` document, whose rules Lean's norms route
            # checked (`Service.Document.checkNorms`), built as Python's own path builds it.
            norm_defaults = None
            norms = (NormDocument(env, selected)
                     if selected or any(d.regulated is not None for d in env.predicates.values()) else None)
        reading_sets = meta.get("reading_sets", [])
        companions, s1_content = _readings_routes(env, reading_sets)
        composed = composed_set_units(meta)
        if composed and (companions or s1_content):
            # The readings routes read every reading's content, and a composed set's is Lean's, not the authored one.
            raise composed_unavailable(composed[0])
        readings_s1 = readings_s2 = readings_components = None
        if companions:
            from ..readings_components import load as load_components
            readings_components = load_components(env.to_dict(), compiled, reading_sets,
                                                  couplings=meta.get("couplings", []),
                                                  narrowings=meta.get("narrowings", []))
        elif s1_content:
            from ..readings_route import validate as validate_s1, elaborate as elaborate_s2
            readings_s1 = validate_s1(env.to_dict(), compiled, reading_sets)
            readings_s2 = elaborate_s2(env.to_dict(), compiled, reading_sets,
                                       couplings=meta.get("couplings", []),
                                       narrowings=meta.get("narrowings", []))
        reading_plan = _reading_plan(active, meta.get("couplings", []))
    except CheckerUnavailable:
        raise
    except Exception as exc:  # noqa: BLE001 - a document Lean accepted that Python cannot build is a bug
        raise unavailable(f"could not be built: {type(exc).__name__}: {exc}"[:300]) from exc
    return {"meta": meta, "environment": env, "source": source, "source_id": row["source_id"],
            "document_id": row["document_id"], "directory": path.parent, "units": compiled, "norms": norms,
            "soft_document": soft_document, "norm_defaults": norm_defaults, "senses": senses, "reports": None,
            "rights_document": rights_document, "readings_s1": readings_s1, "readings_s2": readings_s2,
            "readings_components": readings_components, "reading_plan": reading_plan,
            "lean": {"coverage": row["coverage"], "admitted": admitted}}


# The list lines of a composed block's coverage (`Alternatives.Wire.coverage`), each counted in the residual.
_BLOCK_LINES = ("alternatives_declared", "assumed_harm_free", "counterfactual_leaves", "dilemmas", "narrowings",
                "proximate_judgments", "unmapped_obligations")


def _bind_document_answer(body, meta, declared, row, senses=None):
    """Check the request-shaped fields and arithmetic of a successful Lean document row.

    The response schema checks types. This binding additionally checks values the schema
    cannot know: the authored unit fields, byte partition and every count derived from
    them. Checked content, statuses and identities remain Lean's decisions. A senses
    document's English fences are bound to the senses route's reading Python holds
    (`senses`, `ve.senses_document.SensesReading`); without it no senses row is bound.
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
    rights = "rights@0" in listed_profiles(meta.get("environment"))
    soft = "soft-norms@0" in listed_profiles(meta.get("environment"))
    # A senses document's English fence has the formula the senses route read (batch 16f), and no content where the
    # route read none: a preamble line or an open unit. Every fence the route read is one of the three.
    if "senses" in meta:
        require(senses is not None)
        formulas = senses.formulas
        read = set(formulas) | set(senses.unresolved) | senses.lines
    else:
        formulas, read = {}, set()
    governed = _governed_units(meta)
    kinds, statuses, reasons = {}, {}, {}
    for unit, (authored, parent) in zip(units, declared, strict=True):
        require(type(unit) is dict and type(authored) is dict)
        has_content = (authored.get("id") in formulas if authored.get("id") in read
                       else authored.get("content") is not None)
        if has_content and authored.get("id") in read:
            require("content" in unit and same(unit["content"], formulas[authored["id"]]))
        require(set(unit) == {"id", "span", "kind", "meaning", "support", "status"} |
                ({"content", "meaning_id"} if has_content else set()) |
                ({"parent_id"} if parent is not None else set()))
        for field in ("id", "span", "kind", "meaning", "support"):
            require(field in unit and field in authored and same(unit[field], authored[field]))
        require(("parent_id" in unit) == (parent is not None))
        if parent is not None:
            require(unit["parent_id"] == parent)
        require(("content" in unit) == has_content)
        require(("content" in unit) == ("meaning_id" in unit))
        if has_content and type(authored["content"]) is dict and "ast" in authored["content"]:
            require(same(unit["content"], authored["content"]["ast"]))
        if has_content and type(authored["content"]) is dict and {"norm", "part"} & set(authored["content"]):
            require(_rule_bound(unit["content"], authored["content"], authored.get("id") in governed,
                                rights or soft, same))
        if has_content and type(authored["content"]) is dict and set(authored["content"]) & set(_RIGHTS_KINDS):
            require(rights and same(unit["content"], authored["content"]))
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


def _governed_units(meta) -> set:
    """The units whose rule Lean's `document` mode may answer composed under `scope@0` (`VE.Scope.govern` patches the
    content of `affected` units only, all of them rule units): every unit the request's `scope` block names, as a
    governor's `unit` or in its recorded `units` (which Lean admits only equal to the reach it regenerates), and every
    `part` unit. Read from the request, never recomputed: which of them a governor changes, and how, is Lean's."""
    if "scope@0" not in listed_profiles(meta.get("environment")):
        return set()
    named = _named_units(meta)
    units = meta.get("units")
    return {u.get("id") for u, _ in _parts(units if type(units) is list else [])
            if type(u) is dict and (u.get("id") in named or
                                    type(u.get("content")) is dict and "part" in u["content"])}


def _named_units(meta) -> set:
    """Every unit the request's `scope` block names, as a governor's `unit` or in its recorded `units`."""
    block = meta.get("scope")
    governors = block.get("governors") if type(block) is dict else None
    named = set()
    for governor in governors if type(governors) is list else ():
        if type(governor) is dict:
            named.add(governor.get("unit"))
            named.update(u for u in (governor.get("units") if type(governor.get("units")) is list else ())
                         if type(u) is str)
    return named


def composed_set_units(meta) -> list:
    """The units, in front-matter order, whose reading set Lean's `document` mode composes per choice under `scope@0`
    (scope 11.1, `VE.Scope.governedSetUnits`): read from the request, never recomputed. A set on a unit a governor
    names is admitted only when GOVERN composes it per choice (any other is `ScopeReadings: <unit>`), so in a document
    Lean admitted these are exactly the sets on named units. Their readings as written are not their meaning: Lean's
    answer does not carry the composed readings yet (scope 11.7 item 7, sc-5rc), so whatever reads a reading of one
    is `composed_unavailable`, never the authored content."""
    if "scope@0" not in listed_profiles(meta.get("environment")):
        return []
    named = _named_units(meta)
    sets = meta.get("reading_sets")
    on = {s.get("unit") for s in (sets if type(sets) is list else ()) if type(s) is dict}
    units = meta.get("units")
    return [u["id"] for u, _ in _parts(units if type(units) is list else [])
            if type(u) is dict and u.get("id") in named and u.get("id") in on]


def composed_unavailable(unit: str) -> CheckerUnavailable:
    """The one refusal of whatever would read the readings of a set `composed_set_units` names."""
    return CheckerUnavailable(f"CheckerUnavailable: {unit}'s reading set is composed per choice by scope@0, and its "
                              "composed readings are not relayed yet")


def _with_governed_units(meta: dict, governed: set, rows: list) -> dict:
    """The front matter with each governed unit's content the bound answer's (MIXED parts included), as Lean's
    chain reads it under `scope@0` (`Service.Document.withUnits`)."""
    answered = {row["id"]: row["content"] for row in rows if row["id"] in governed and "content" in row}

    def unit(u):
        if u.get("status") == "MIXED":
            return {**u, "parts": [unit(p) for p in u["parts"]]}
        return {**u, "content": answered[u["id"]]} if u.get("id") in answered else u
    return {**meta, "units": [unit(u) for u in meta["units"]]}


def _rule_bound(answer, authored, governed: bool, soft: bool, same) -> bool:
    """A `norm` or `part` unit's content in Lean's answer bound to the authored content. A unit scope does not govern
    keeps its rule: exactly as written, or a soft one as `_soft_bound` binds it. A governed unit's rule is Lean's
    composition (`VE.Scope.newContent`): the authored members with `part` read as `norm`, every other member (`cites`)
    as written, and the rule an object; a soft one in the form its container holds (`_soft_bound` of the rule with
    itself), as for every soft rule Lean answers."""
    if not governed:
        return "part" not in authored and (_soft_bound(answer, authored, same) if soft else same(answer, authored))
    members = {"norm" if key == "part" else key for key in authored}
    return (type(answer) is dict and set(answer) == members and len(members) == len(authored) and
            type(answer.get("norm")) is dict and
            all(same(answer[key], authored[key]) for key in authored if key not in ("norm", "part")) and
            (not soft or _soft_bound(answer, answer, same)))


def _soft_bound(answer, authored, same) -> bool:
    """A rights or soft-norms document's soft norm unit in Lean's answer (`Service.Document.softCanonical`) bound to
    the authored content: the same members (`norm`, and `cites` as written), and the rule exactly as the soft rule
    container holds the authored one (`SoftRule.to_dict` of `_hydrate_rule`, the form Python's own path keeps): every
    member as written, a soft member omitted only where the container omits it. Lean's canonical form of a rule it
    accepted is that form; any other answer is not bound."""
    if type(answer) is not dict or type(authored) is not dict or set(answer) != set(authored):
        return False
    if "cites" in authored and not same(answer["cites"], authored["cites"]):
        return False
    from ..softnorms import _hydrate_rule
    try:
        written = _hydrate_rule({"norm": authored["norm"]}).to_dict()["norm"]
    except (VEError, KeyError, TypeError, ValueError, AttributeError, IndexError):
        return False  # an authored rule the container cannot hold binds no answer
    return same(answer.get("norm"), written)
