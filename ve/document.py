"""ve-document@1: byte-partitioned source, reviewed metadata and P0 admission.

Front matter is JSON between two ``---`` lines. The source is every body byte
outside ``ve`` fences; unit spans are offsets into that exact byte sequence.
``ve <unit-id>`` fences supply an optional English or strict formula for a
unit. The JSON front matter may instead bind a formula AST or a W1 norm.
"""
from __future__ import annotations

import json
import hashlib
from pathlib import Path

from .admission import _check_kind, admit_document, token
from .ast import Document, formula_from_data, formula_to_data
from .environment import Environment
from .errors import VEError
from .identity import meaning_id, source_id
from .openterms import validate_open_terms
from .readings import (active_reading_sets, check_readings, plan_choices,
                       validate_narrowings, validate_reading_sets)
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
    if type(meta) is not dict or meta.get("format") not in ("ve-document@1", "ve-document@2"):
        raise VEError("unsupported document format")
    allowed = {"format", "environment", "units", "open_terms", "reading_sets",
               "narrowings", "weights", "graph", "lemmas"}
    if meta["format"] == "ve-document@2":
        allowed.add("discourse")
    if set(meta) - allowed:
        raise VEError("unknown document metadata")
    return meta, *_body(raw[boundary + 5:])


def _meaning(value, open_names):
    if value == "specified":
        return "specified"
    if type(value) is not dict or len(value) != 1:
        raise VEError("invalid meaning status")
    status, detail = next(iter(value.items()))
    if status == "contextual" and type(detail) is str and detail:
        return status
    if status == "open" and type(detail) is list and detail and all(type(x) is str for x in detail) and set(detail) <= open_names:
        return status
    if status == "unformalised" and token(detail):
        return status
    raise VEError("invalid meaning status")


def _content(env, unit, fences):
    content = unit.get("content")
    if content is None:
        return None
    if type(content) is not dict or len(content) != 1:
        raise VEError("unit content must bind one formula or norm")
    if "norm" in content:
        from .norms import NormDocument
        if "norms@0" not in env.profiles:
            raise VEError("UnsupportedProfile: norms@0 is required")
        rule = NormDocument._decode(content)
        return rule.to_dict(), None
    if "ast" in content:
        formula = formula_from_data(env, content["ast"])
        return formula_to_data(env, formula), meaning_id(env, formula)
    if "fence" not in content or content["fence"] != unit["id"]:
        raise VEError("unit fence must match its id")
    if unit["id"] not in fences:
        raise VEError("missing VE fence")
    text = fences[unit["id"]]
    if unit.get("surface") == "english":
        from .english import parse_english
        document = parse_english(env, text)
    elif unit.get("surface") == "strict":
        from .parser import parse
        document = parse(env, text)
    else:
        raise VEError("fenced content needs english or strict surface")
    if len(document.formulas) != 1:
        raise VEError("each VE fence must contain exactly one sentence")
    formula = document.formulas[0]
    return formula_to_data(env, formula), meaning_id(env, formula)


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


def load_document(path: str | Path):
    raw = Path(path).read_bytes()
    meta, source, fences = _split(raw)
    if not source:
        raise VEError("document source is empty")
    if type(meta.get("environment")) is not dict:
        raise VEError("document needs an embedded environment")
    from .discourse import base_environment, validate_discourse
    environment_data = base_environment(meta)
    env = Environment(environment_data)
    open_names = validate_open_terms(env, meta.get("open_terms", []))
    units = meta.get("units")
    if type(units) is not list or not units:
        raise VEError("document needs units")
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
        kind = _check_kind(unit["kind"])
        status = _meaning(unit["meaning"], open_names)
        if type(unit["support"]) is not str or unit["support"] not in SUPPORTS:
            raise VEError("invalid support")
        content, mid = _content(env, unit, fences) if unit.get("content") is not None else (None, None)
        is_norm = type(content) is dict and "norm" in content
        if is_norm:
            from .norms import norm_meaning_id, NormDocument
            from .admission import _quoted
            if _quoted(kind):
                quoted_norms.append(content)
            elif kind != "norm":
                raise VEError("norm content requires a norm or quoted kind")
            mid = norm_meaning_id(env, NormDocument._decode(content))
        if status == "unformalised" and content is not None:
            raise VEError("unformalised unit cannot assert content")
        if type(unit["kind"]) is list and unit["kind"][0] == "unformalised" and status != "unformalised":
            raise VEError("unformalised kind needs unformalised meaning")
        if "meaning_id" in unit and unit["meaning_id"] != mid:
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
    from .norms import NormDocument
    if set(fences) != {u["id"] for u, _ in _parts(units) if type(u.get("content")) is dict
                       and u["content"].get("fence") == u["id"]}:
        raise VEError("unbound VE fence")
    reading_sets = meta.get("reading_sets", [])
    validate_reading_sets(env, reading_sets, unit_ids)
    active = active_reading_sets(reading_sets)
    units_by_id = {u["id"]: u for u in compiled}
    for reading_set in active:
        unit = units_by_id[reading_set["unit"]]
        unit["status"] = ("CHECKED" if reading_set["status"] == "authored"
                          and all(c["kind"] == "asserted" and c["content"] is not None
                                  for c in reading_set["readings"]) else "OPEN")
    for unit in compiled:
        if unit.pop("explicit_status") not in (None, unit["status"]):
            raise VEError("unit status contradicts content, meaning, or active reading set")
    reading_units = {r["unit"] for r in active}
    norm_units = [u for u in compiled if u["kind"] == "norm"
                  and type(u["content"]) is dict and "norm" in u["content"]]
    quoted_norms.extend(u["content"] for u in norm_units if u["id"] in reading_units)
    if quoted_norms:
        from .norm_admission import _check_quoted
        for content in quoted_norms:
            _check_quoted(env, content)
    selected_norms = [u["content"] for u in norm_units if u["id"] not in reading_units]
    norms = (NormDocument(env, selected_norms)
             if selected_norms or any(d.regulated is not None for d in env.predicates.values()) else None)
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
        (meta["format"] + "\n").encode("ascii") + json.dumps(identity_payload, sort_keys=True,
                                          ensure_ascii=False, separators=(",", ":"),
                                          allow_nan=False).encode("utf-8")).hexdigest()
    doc = {"meta": meta, "environment": env, "source": source, "source_id": sid,
            "document_id": document_id,
            "units": compiled, "norms": norms,
            "reading_plan": plan_choices([r for r in active if r["status"] == "open"])}
    if meta["format"] == "ve-document@2":
        doc["discourse"] = validate_discourse(doc)
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


def coverage(doc):
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
    meta = doc["meta"]
    bridge_count = sum(n.get("label", "").startswith("bridge:accepts(")
                       for n in meta.get("graph", {}).get("nodes", []))
    residual = {"open_terms": len(meta.get("open_terms", [])),
                "assumptions": sum(u["support"] == "assumption" for u in units),
                "bridge_leaves": bridge_count,
                "unresolved_reading_sets": sum(r["status"] == "open" for r in meta.get("reading_sets", []))}
    return {"source_bytes": len(source), "accounted_bytes": sum(kinds.values()),
            "coverage_percent": 100, "bytes_by_kind": kinds, "bytes_by_status": statuses,
            "unformalised_reasons": reasons,
            "residual": residual, "residual_total": sum(residual.values())}


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


def check_document(path):
    doc = load_document(path)
    if (doc.get("discourse", {}).get("joint", {}).get("constraints", 0)
            or doc.get("discourse", {}).get("joint", {}).get("status") == "UNKNOWN") and "graph" in doc["meta"]:
        raise VEError("ResourceLimit: discourse citation and report extension pending")
    env = doc["environment"]
    fixed, active = _fixed_and_active(doc)
    assertions = [formula_from_data(env, ast) for ast in fixed]
    result = {"format": doc["meta"]["format"], "source_id": doc["source_id"],
              "document_id": doc["document_id"],
              "coverage": coverage(doc), "reading_plan": doc["reading_plan"]}
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
                                       "readings": [c["content"] for c in r["readings"]]}
                                      for r in active
                                      if all(c["kind"] == "asserted" and c["content"] is not None
                                             for c in r["readings"])],
                     "narrowings": [n["id"] for n in doc["meta"].get("narrowings", [])]}
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
    if _unresolved_norm_reading(active):
        result["premises"] = {"status": "UNKNOWN", "reason": "non-assertion reading elaboration pending"}
    elif (doc.get("discourse", {}).get("joint", {}).get("constraints", 0)
          or doc.get("discourse", {}).get("joint", {}).get("status") == "UNKNOWN"):
        result["premises"] = {"status": "UNKNOWN", "reason": "correlated reading premises require a joint choice"}
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
    if "discourse" in doc:
        from .discourse import report_discourse
        report_discourse(doc, result)
    return result


def render_document(path):
    doc = load_document(path)
    lines = []
    from .printer import render

    def wording(ast):
        formula = formula_from_data(doc["environment"], ast)
        return render(Document((formula,)), doc["environment"], "ve_english").strip()

    descriptions = {
        "asserted": "a direct assertion", "norm": "a rule", "definition": "a definition",
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
        if type(content) is dict and "norm" in content:
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
        prefix = "Checked reading: " if u["content"] is not None else "Recorded meaning: "
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
                                  joint_choices=doc.get("discourse", {}).get("joint"))
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
