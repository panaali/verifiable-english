"""`check_document`: the report of a loaded document, its coverage and its premises (moved from
`ve/document.py`, AR-16a)."""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from ..assurance import semantic_entry
from ..admission import admit_document
from ..ast import formula_from_data, formula_to_data
from ..backends.lean_service import CheckerUnavailable
from ..errors import ResourceLimit, VEError
from ..readings import active_reading_sets
from ..wire import digest
from ..vacuity import premise_status
from .source import _RIGHTS_KINDS, _environment
from .containers import _content_bearing, _free_norms, _in_rights_source, _rights_units, _s1_attached, _soft_contents, _wire_unit
from .load import _load


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


def _filled_soft_elaboration(doc, active):
    """Lean's one elaboration of the soft chain, shared by premise decoding and checking."""
    if (doc.get("soft_document") is None or doc.get("rights_document") is not None
            or "norm-defaults@0" not in doc["environment"].profiles):
        return None
    if "_filled_soft_elaboration" not in doc:
        from ..norm_defaults_route import run_case
        source = doc["environment"].to_dict()
        source["profiles"] = [p for p in source["profiles"] if p != "readings@1"]
        attached = _s1_attached(doc["environment"].to_dict(), doc["meta"])
        doc["_filled_soft_elaboration"] = run_case({
            "id": "norm-defaults-elaborate", "kind": "norm-defaults-elaborate",
            "environment": source,
            "norms": _free_norms(doc["units"], active, attached)})
    return doc["_filled_soft_elaboration"]


def _checking_environment(doc):
    """The vocabulary in which a document's fixed premises and readings are checked."""
    if doc.get("soft_document") is not None:
        return doc["soft_document"].extended_env
    if doc.get("norm_defaults") is not None:
        return doc["norm_defaults"].filled.env
    if doc.get("senses") is not None:
        return doc["senses"].environment
    return doc["environment"]


def _report_premise_context(doc):
    """The report's premise set over Lean's filled soft tree when that route applies.

    The readings query has its own frozen lower-route identity and continues to
    use `_fixed_premises` and `_checking_environment` directly.
    """
    fixed, active = _fixed_and_active(doc)
    filled = _filled_soft_elaboration(doc, active)
    if filled is None:
        return _checking_environment(doc), fixed, active
    from ..environment import Environment
    # Lean's base_environment lists generated declarations; add the authored
    # predicates so graph leaves and assertions can be decoded in one vocabulary.
    raw = deepcopy(filled["base_environment"])
    predicates = raw["vocabulary"]["predicates"]
    from ..softnorms import base_predicate_declaration
    for name, declaration in doc["environment"].to_dict()["vocabulary"]["predicates"].items():
        base_declaration = base_predicate_declaration(declaration)
        if name in predicates and predicates[name] != base_declaration:
            raise CheckerUnavailable("CheckerUnavailable: filled soft vocabulary collides with source")
        predicates[name] = base_declaration
    if not _unresolved_norm_reading(active):
        fixed.extend(item["ast"] for field in ("background", "premises", "fill", "soft")
                     for item in filled[field])
    return Environment(raw), fixed, active


def _unresolved_norm_reading(sets):
    return any(c["kind"] == "norm" or c["content"] is None and c["kind"] != "asserted"
               for r in sets for c in r["readings"])


def _assertion_disjunctions(env, sets):
    from ..ast import Or
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


def _rights_source_units(doc):
    return [{"source_units": [u["id"] for u in doc["units"]]}] + [
        u["content"] for u in doc["units"] if _in_rights_source(u)]


def _lower_route(doc):
    """The environment and soft document of the lower route: under `readings@1`, without the profile."""
    if "readings@1" not in doc["environment"].profiles:
        return doc["environment"], doc["soft_document"]
    data = doc["environment"].to_dict()
    data["profiles"] = [p for p in data["profiles"] if p != "readings@1"]
    return _environment(data), _lower_soft_document(doc)


def _lower_rights_document(doc, lower_env):
    from ..rights import RightsDocument
    return RightsDocument(lower_env, _rights_units(doc["meta"]["units"],
                                                   _s1_attached(doc["environment"].to_dict(), doc["meta"])))


def _lower_soft_document(doc):
    """The soft document the lower route checks: under `readings@1` the head strips the profile and hands every
    other case to the lower route (composition-s1.md 4.1), so its environment is the one without it."""
    soft = doc["soft_document"]
    if (("readings@1" not in doc["environment"].profiles and
         "norm-defaults@0" not in doc["environment"].profiles)
            or (soft is None and doc["rights_document"] is None)):
        # The norms chain has no soft document, with or without `readings@1` (DRI ruling 4: a norms document with
        # `norm-defaults@0` and `readings@1` reaches this with a claim graph).
        return soft
    data = doc["environment"].to_dict()
    data["profiles"] = [p for p in data["profiles"] if p != "readings@1"]
    if "norm-defaults@0" in data["profiles"]:
        # Under the soft completion the soft route reads the source's placeholder (each unspecified completion read
        # as deny); `fill`, `Soft_T` on the filled tree and every verdict are Lean's readings route's (rd-9 3.8).
        from ..norms import _norm_defaults_placeholder
        data = _norm_defaults_placeholder(data)
    lower = _environment(data)
    attached = _s1_attached(doc["environment"].to_dict(), doc["meta"])
    if doc["rights_document"] is not None:
        from ..rights import RightsDocument
        return RightsDocument(lower, _rights_units(doc["meta"]["units"], attached)).soft_document
    from ..softnorms import SoftNormDocument
    return SoftNormDocument(lower, _soft_contents(doc["meta"]["units"], attached))


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
    from ..rights_route import report_rights
    return report_rights(doc["environment"], _rights_source_units(doc), rights)


def coverage_defaults(doc):
    """norm-defaults 3.2 lines for a document (a translation over source prose):
    gap and default-reached evidence from a small-model search or a certificate,
    and grounding against the `completions` block. Computed once per document."""
    if "_norm_defaults_report" not in doc:
        from ..norm_defaults import report
        doc["_norm_defaults_report"] = report(
            doc["norm_defaults"], prove=True, search_domain_size=2, translation=True,
            completions=doc["meta"].get("completions", {}),
            unit_ids={u["id"] for u in doc["units"]})
    return doc["_norm_defaults_report"]


def coverage(doc, scoped=None, rights_report=None):
    """`scoped`: the reports layer's checked scoped verdicts (`check_document`);
    without them a scoped check is reported as not replayed. `rights_report`: the
    replayed rights report when the caller already has it. A document Lean's `document` mode accepted has
    Lean's tables and wrapper counts (batch 16b); the lines of its composed profiles are `_profile_lines`, as on
    Python's own path."""
    if "lean" in doc:
        answer = deepcopy(doc["lean"]["coverage"])
        answer.update(_profile_lines(doc, answer["residual"], rights_report))
        answer["residual_total"] = sum(answer["residual"].values())
        return answer
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
        from ..backends.relay import decide
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
    profile = _profile_lines(doc, residual, rights_report)
    return {"source_bytes": len(source), "accounted_bytes": sum(kinds.values()),
            "coverage_percent": 100, "bytes_by_kind": kinds, "bytes_by_status": statuses,
            "unformalised_reasons": reasons,
            "residual": residual, "residual_total": sum(residual.values()),
            **({"residual_lines": lines} if lines else {}),
            **({"alternatives": alternatives} if alternatives is not None else {}),
            **profile}


def _profile_lines(doc, residual, rights_report=None):
    """The coverage lines of a document's composed profiles, for both of `coverage`'s paths: the soft and rights
    residual counts, labels and report, a content-bearing reading set's lines and the norm-defaults gaps. Each
    count is added to `residual`; the returned members join the coverage object."""
    meta = doc["meta"]
    soft = doc.get("soft_document")
    if soft is not None:
        from ..soft_route import elaborate_soft_document
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
        from ..readings_route import report as readings_report
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
    return {**({"norm_defaults": {
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
    from ..admission import parse_label
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
    from ..units import core_formula, erased_environment
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
    from ..ast import Or
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
        from ..discourse import unavailable_report
        raise unavailable_report(exc) from exc


def _report(doc):
    joint = doc.get("discourse", {}).get("joint")
    joint_pending = joint is not None and joint["status"] == "UNKNOWN"
    soft = doc["soft_document"]
    if doc["reports"] is not None:
        from ..reports_route import run_case
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
    if _checking_environment(doc).unit_schema is not None:
        return _check_quantity_document(doc, active_reading_sets(doc["meta"].get("reading_sets", [])))
    env, fixed, active = _report_premise_context(doc)
    assertions = [formula_from_data(env, ast) for ast in fixed]
    rights_report = _rights_report(doc)
    result = {"format": doc["meta"]["format"], "source_id": doc["source_id"],
              "document_id": doc["document_id"],
              "coverage": coverage(doc, rights_report=rights_report),
              "reading_plan": doc["reading_plan"]}
    if soft is not None:
        from ..soft_route import elaborate_soft_document
        elaborate_soft_document(_lower_soft_document(doc))
        result["soft"] = {"environment_id": doc["environment"].environment_id,
                          "soft_document_hash": soft.document_hash,
                          "decision_predicates": sorted(soft.extended_env.decision_names),
                          "background_labels": [label for label, _ in soft.extended_env.soft_premises]}
        if "norm-defaults@0" not in doc["environment"].profiles:
            # Under the soft completion no Python layer or soft premise enters a premise set (rd-9 3.8).
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
        from ..admission import parse_label
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
        from ..admission import parse_label
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
            from ..rights_route import admit_rights_document
            lower_rights = (rights if lower_env is doc["environment"] else
                            _lower_rights_document(doc, lower_env))
            result["admission"] = admit_rights_document(lower_env, admission, lower_rights)
        elif soft is not None:
            # Lean's norm-defaults service owns fill and its soft-vs-W1 choice;
            # the ordinary soft route remains the fallback for other profiles.
            result["admission"] = admit_document(lower_env, admission)
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
        # when every reading of an open set is an assertion with content.
        # It covers only open sets; signed authored assertions stay fixed.
        assertions.extend(_assertion_disjunctions(
            env, [r for r in active if r["status"] == "authored"]))
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
        from ..readings_verdicts import context
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
        from ..readings_route import report as readings_report
        result["readings"] = readings_report(doc)
    if "discourse" in doc:
        from ..discourse import report_discourse
        report_discourse(doc, result)
    return result


def _graph_nodes(graph):
    """The nodes of a claim graph as the pre-admission checks read them: none for a graph or node list of the
    wrong JSON type, which W2 admission then rejects with its own diagnostic."""
    nodes = graph.get("nodes", []) if type(graph) is dict else []
    return nodes if type(nodes) is list else []
