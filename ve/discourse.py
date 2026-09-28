"""Conservative Python adapter for the ve.discourse@1 document profile.

The frozen environment and document routes receive only the base profile list.
Reference expansion is admitted here only when the expanded English has one
parse and reproduces the recorded formula. Other reference forms can still be
recorded on labelled or unformalised units without claiming formula coverage.
"""
from __future__ import annotations

from itertools import product
import re

from .admission import token
from .ast import formula_to_data
from .errors import VEError
from .readings import active_reading_sets
from .wire import digest

PROFILE = "ve.discourse@1"
_FORM_KINDS = {
    "pronoun": {"entity", "unit"}, "demonstrative": {"entity", "unit"},
    "possessive": {"entity"}, "definite": {"entity"},
    "ordinal_pair": {"entity"}, "plural": {"entity"},
    "such": {"predicate"}, "definition_ref": {"predicate"},
    "document_name": {"document"}, "citation": {"claim"},
    "section_ref": {"anchor"}, "navigation": {"anchor", "unit"},
}
_LOCATION = {"section_ref", "navigation"}
_LIMITS = {"anchors": 1024, "mentions": 4096, "names": 1024,
           "documents": 64, "groups": 256, "constraints": 1024}


def base_environment(meta):
    """Check the outer declaration, then produce the exact frozen input pair."""
    data = meta["environment"]
    if type(data) is not dict or type(data.get("profiles")) is not list:
        raise VEError("invalid environment profiles")
    profiles = data["profiles"]
    if meta["format"] == "ve-document@1":
        if PROFILE in profiles:
            raise VEError("UnsupportedProfile: ve.discourse@1 requires ve-document@2")
        return data
    if profiles != sorted(set(profiles)) or PROFILE not in profiles or "relational-fol@0" not in profiles:
        raise VEError("UnsupportedProfile: ve.discourse@1 requires a sorted profile list with relational-fol@0")
    if "discourse" not in meta:
        raise VEError("InvalidInput: missing discourse block")
    return {**data, "profiles": [p for p in profiles if p != PROFILE]}


def _array(block, key):
    value = block.get(key, [])
    if type(value) is not list:
        raise VEError(f"InvalidInput: discourse.{key}")
    if len(value) > _LIMITS.get(key, 1_000_000):
        raise VEError(f"ResourceLimit: {key}")
    return value


def _span(value, end):
    return (type(value) is list and len(value) == 2 and
            all(type(x) is int for x in value) and 0 <= value[0] < value[1] <= end)


def _no_null(value):
    if value is None:
        raise VEError("InvalidInput: null in discourse block")
    if type(value) is dict:
        for item in value.values():
            _no_null(item)
    elif type(value) is list:
        for item in value:
            _no_null(item)


def _table(items, key, category):
    result = {}
    for item in items:
        if type(item) is not dict or not token(item.get(key)):
            raise VEError(f"InvalidInput: {category}")
        value = item[key]
        if value in result:
            raise VEError(f"DuplicateDeclaration: {category} {value}")
        result[value] = item
    return result


def _inside(outer, inner):
    return outer[0] <= inner[0] and inner[1] <= outer[1]


def _anchors(block, source):
    anchors = _table(_array(block, "anchors"), "id", "anchor")
    if not anchors:
        raise VEError("InvalidInput: discourse needs a document anchor")
    roots = []
    for aid, anchor in anchors.items():
        if anchor.get("kind") not in {"document", "section", "clause", "item", "article"}:
            raise VEError(f"InvalidInput: anchor {aid}")
        if not _span(anchor.get("span"), len(source)):
            raise VEError(f"InvalidInput: anchor span {aid}")
        parent = anchor.get("parent")
        if parent is None:
            roots.append(aid)
        elif parent not in anchors:
            raise VEError(f"DanglingAnchor: {parent}")
        elif not _inside(anchors[parent]["span"], anchor["span"]):
            raise VEError(f"InvalidInput: anchor span {aid}")
    if len(roots) != 1 or anchors[roots[0]]["kind"] != "document" or anchors[roots[0]]["span"] != [0, len(source)]:
        raise VEError("InvalidInput: anchors need one document root spanning the source")
    for anchor in anchors.values():
        visited = set()
        cursor = anchor
        while "parent" in cursor:
            if cursor["id"] in visited:
                raise VEError("DependencyCycle: anchors")
            visited.add(cursor["id"])
            cursor = anchors[cursor["parent"]]
    siblings = {}
    for anchor in anchors.values():
        parent = anchor.get("parent")
        key = (parent, anchor.get("label"))
        if key in siblings:
            raise VEError(f"DuplicateAnchor: {anchor.get('label')}")
        siblings[key] = anchor
    for anchor in anchors.values():
        peers = [a for a in anchors.values() if a.get("parent") == anchor.get("parent") and a is not anchor]
        if any(max(anchor["span"][0], p["span"][0]) < min(anchor["span"][1], p["span"][1]) for p in peers):
            raise VEError(f"InvalidInput: overlapping anchors {anchor['id']}")
    return anchors


def _joint(block, active):
    sets = {(s["id"], s["version"]): s for s in active if s["status"] == "open"}
    constraints = _array(block, "constraints")
    decoded = []
    for row in constraints:
        if type(row) is not dict or row.get("kind") not in {"requires", "excludes"}:
            raise VEError("InvalidInput: discourse constraint")
        pair = []
        for key in ("a", "b"):
            ref = row.get(key)
            if type(ref) is not list or len(ref) != 3 or type(ref[1]) is not int:
                raise VEError("InvalidInput: discourse constraint reading")
            rs = sets.get((ref[0], ref[1]))
            if rs is None:
                raise VEError(f"InvalidInput: inactive reading set {ref[0]}@{ref[1]}")
            ids = [r["id"] for r in rs["readings"]]
            if ref[2] not in ids:
                raise VEError(f"InvalidInput: reading {ref[2]} not in {ref[0]}@{ref[1]}")
            pair.append((ref[0], ref[1], ids.index(ref[2])))
        decoded.append((row["kind"], *pair))
    count = 1
    ordered = list(sets.values())
    for rs in ordered:
        count *= len(rs["readings"])
        if count > 64:
            return {"status": "UNKNOWN", "budget": 64, "constraints": len(decoded)}
    choices = []
    for indices in product(*(range(len(rs["readings"])) for rs in ordered)):
        choice = {(rs["id"], rs["version"]): index for rs, index in zip(ordered, indices)}
        if all((choice[a[:2]] != a[2] or choice[b[:2]] == b[2]) if kind == "requires"
               else (choice[a[:2]] != a[2] or choice[b[:2]] != b[2])
               for kind, a, b in decoded):
            choices.append({f"{rs['id']}@{rs['version']}": index for rs, index in zip(ordered, indices)})
    if not choices:
        raise VEError("InvalidCompatibility: " + ", ".join(sorted(s["id"] for s in ordered)))
    return {"status": "complete", "choices": choices, "count": len(choices),
            "constraints": len(decoded)}


def _expanded_formula(doc, unit, mention, name):
    """Parse one explicit replacement; failure is a typed-out competitor."""
    from .english import parse_english
    env = doc["environment"]
    start, end = unit["span"]
    a, b = mention["span"]
    raw = doc["source"][start:a] + name.encode("utf-8") + doc["source"][b:end]
    try:
        expanded = raw.decode("utf-8")
        parsed = parse_english(env, expanded)
        if len(parsed.formulas) != 1:
            return None
        return expanded, formula_to_data(env, parsed.formulas[0])
    except (VEError, UnicodeError):
        return None


def _check_simple_expansion(doc, unit, mention, names, anchors):
    form = mention["form"]
    if form not in {"pronoun", "demonstrative", "ordinal_pair"}:
        raise VEError(f"MentionNotSlot: {mention['id']}")
    target = mention["target"]
    if target["kind"] != "entity":
        raise VEError(f"MentionNotSlot: {mention['id']}")
    candidates = {}
    for registration in names:
        name = registration["constant"]
        if not _inside(anchors[registration["scope"]]["span"], mention["span"]):
            continue
        if form == "ordinal_pair" and name not in target["pair"]:
            continue
        if form in {"pronoun", "demonstrative"} and _competing_quantifier(doc, mention, name, anchors):
            continue
        expansion = _expanded_formula(doc, unit, mention, registration["display"])
        if expansion is not None:
            candidates[name] = expansion
    chosen = target.get("name")
    if chosen not in candidates:
        raise VEError(f"IllTypedTarget: {mention['id']}: {chosen}")
    if len(candidates) > 1:
        raise VEError(f"AmbiguousReference: {mention['id']}: {', '.join(sorted(candidates))}")
    if candidates[chosen][1] != unit["content"]:
        raise VEError(f"ManifestMismatch: bound.{unit['id']}")
    return candidates[chosen][0]


def _contains_var(formula, index=0):
    if formula == ["var", index]:
        return True
    if type(formula) is list:
        if len(formula) == 3 and formula[0] in {"exists", "forall"}:
            return _contains_var(formula[2], index + 1)
        return any(_contains_var(item, index) for item in formula[1:])
    return False


def _same_witness(content):
    """Conservative fused shape: two clauses under one existential binder."""
    return (type(content) is list and len(content) == 3 and content[0] == "exists"
            and type(content[2]) is list and len(content[2]) == 3
            and content[2][0] == "and"
            and _contains_var(content[2][1]) and _contains_var(content[2][2]))


def _quantifies(formula, sort):
    if type(formula) is not list:
        return False
    if len(formula) == 3 and formula[0] in {"exists", "forall"} and formula[1] == sort:
        return True
    return any(_quantifies(item, sort) for item in formula[1:])


def _competing_quantifier(doc, mention, constant, anchors):
    position = mention["span"]
    enclosing = min((a for a in anchors.values() if _inside(a["span"], position)),
                    key=lambda a: a["span"][1] - a["span"][0])
    sort = doc["environment"].constants[constant].sort
    return any(u["kind"] == "asserted" and u["content"] is not None
               and _inside(enclosing["span"], u["span"])
               and u["span"][1] <= position[0] and _quantifies(u["content"], sort)
               for u in doc["units"])


def validate_discourse(doc):
    block = doc["meta"]["discourse"]
    if type(block) is not dict:
        raise VEError("InvalidInput: discourse block")
    _no_null(block)
    if block and block.get("version") != PROFILE:
        raise VEError("InvalidInput: discourse version")
    if set(block) - {"version", "definitions_version", "document_sort", "anchors", "names",
                      "content_names", "mentions", "documents", "imports", "groups", "constraints"}:
        raise VEError("InvalidInput: discourse field")
    if block.get("definitions_version", doc["environment"].environment_id) != doc["environment"].environment_id:
        raise VEError(f"StaleTarget: definitions@{block['definitions_version']}")
    if not block:
        return {"references": [], "groups": [], "joint": _joint(block, [])}
    env, units = doc["environment"], {u["id"]: u for u in doc["units"]}
    anchors = _anchors(block, doc["source"])
    names = _array(block, "names")
    for name in names:
        if type(name) is not dict or name.get("constant") not in env.constants or name.get("scope") not in anchors:
            raise VEError("InvalidInput: discourse name")
        if type(name.get("display")) is not str or type(name.get("aliases", [])) is not list:
            raise VEError("InvalidInput: discourse name display")
    for i, name in enumerate(names):
        for other in names[i + 1:]:
            if set([name["display"], *name.get("aliases", [])]) & set([other["display"], *other.get("aliases", [])]):
                if max(anchors[name["scope"]]["span"][0], anchors[other["scope"]]["span"][0]) < min(anchors[name["scope"]]["span"][1], anchors[other["scope"]]["span"][1]):
                    raise VEError(f"DuplicateDeclaration: name {name['display']}")
    content_names = _array(block, "content_names")
    for item in content_names:
        if type(item) is not dict or item.get("scope") not in anchors or type(item.get("units")) is not list or any(u not in units for u in item["units"]):
            raise VEError("InvalidInput: content_name")
    document_sort = block.get("document_sort")
    documents = _table(_array(block, "documents"), "name", "document")
    if documents:
        if document_sort not in env.sorts or {n for n, c in env.constants.items() if c.sort == document_sort} != set(documents):
            raise VEError(f"InvalidInput: document sort {document_sort} has other constants")
    mentions = _table(_array(block, "mentions"), "id", "mention")
    by_unit = {}
    for mid, m in mentions.items():
        uid = m.get("unit")
        if uid not in units or not _span(m.get("span"), len(doc["source"])) or not _inside(units[uid]["span"], m["span"]):
            raise VEError(f"InvalidInput: mention {mid} span")
        form, target = m.get("form"), m.get("target")
        if form not in _FORM_KINDS or type(target) is not dict:
            raise VEError(f"InvalidInput: mention {mid}")
        kind = target.get("kind")
        if kind not in _FORM_KINDS[form]:
            raise VEError(f"TargetKindMismatch: {mid}: {form}, {kind}")
        if "reading" in m and m["reading"] not in {"assertive", "presuppositional", "distributive"}:
            raise VEError(f"InvalidInput: reading {m['reading']}")
        by_unit.setdefault(uid, []).append(m)
    for uid, rows in by_unit.items():
        rows.sort(key=lambda m: (m["span"][0], -m["span"][1]))
        for i, a in enumerate(rows):
            for b in rows[i + 1:]:
                if a["span"][1] <= b["span"][0]:
                    break
                if not _inside(a["span"], b["span"]):
                    raise VEError(f"InvalidInput: mentions {a['id']}, {b['id']} overlap")
    references = []
    presentations = {}
    for mid, m in mentions.items():
        target = m["target"]
        kind, form = target["kind"], m["form"]
        if kind == "entity":
            members = target.get("members")
            pair = target.get("pair")
            if form == "plural":
                if type(members) is not list or len(members) < 2 or len(set(members)) != len(members):
                    raise VEError("InvalidInput: plural members")
                selected = members
            elif form == "ordinal_pair":
                if type(pair) is not list or len(pair) != 2 or target.get("name") not in pair:
                    raise VEError("InvalidInput: ordinal pair")
                selected = pair
            else:
                selected = [target.get("name")]
            for name in selected:
                registration = next((n for n in names if n["constant"] == name and _inside(anchors[n["scope"]]["span"], m["span"])), None)
                if registration is None:
                    raise VEError(f"InaccessibleTarget: {mid}: {name}")
                if form in {"pronoun", "demonstrative"} and _competing_quantifier(doc, m, name, anchors):
                    raise VEError(f"InaccessibleTarget: {mid}: {name}")
        elif kind == "anchor":
            if target.get("name") not in anchors:
                raise VEError(f"DanglingAnchor: {target.get('name')}")
        elif kind == "predicate":
            if target.get("name") not in env.predicates:
                raise VEError(f"UnresolvedReference: {mid}")
        elif kind == "unit":
            if type(target.get("units")) is not list or any(u not in units for u in target["units"]):
                raise VEError(f"UnresolvedReference: {mid}")
            if "content_name" in target and not any(c["name"] == target["content_name"] and c["units"] == target["units"] for c in content_names):
                raise VEError(f"ManifestMismatch: mentions.{mid}.content_name")
        elif kind == "document" and target.get("name") not in documents:
            raise VEError(f"UnknownDocument: {target.get('name')}")
        references.append({"mention": mid, "unit": m["unit"], "form": form, "target": target,
                           "status": "navigation" if form in _LOCATION else "resolved"})
    for uid, rows in by_unit.items():
        unit = units[uid]
        if unit["content"] is None:
            continue
        producing = [m for m in rows if m["form"] not in _LOCATION]
        if not producing:
            continue
        if len(producing) != 1 or len(rows) != 1:
            raise VEError(f"ResourceLimit: resolution of {uid}")
        presentations[uid] = _check_simple_expansion(doc, unit, producing[0], names, anchors)
    groups = _array(block, "groups")
    active = active_reading_sets(doc["meta"].get("reading_sets", []))
    for group in groups:
        if type(group) is not dict or type(group.get("spans")) is not list or not group["spans"] or len(group["spans"]) > 16:
            raise VEError("InvalidInput: group")
        rs = next((s for s in active if (s["id"], s["version"]) == (group.get("set"), group.get("version"))), None)
        if rs is None or group.get("reading") not in [r["id"] for r in rs["readings"]] or rs["unit"] != group["spans"][0]:
            raise VEError("InvalidInput: group reading")
        reading = next(r for r in rs["readings"] if r["id"] == group["reading"])
        if group["reading"] == "same-witness" and not _same_witness(reading.get("content")):
            raise VEError(f"WitnessSplit: {rs['id']}@{rs['version']}:same-witness")
        for uid in group["spans"]:
            if uid not in units or units[uid]["content"] is not None or any(s["unit"] == uid and s is not rs for s in active):
                raise VEError(f"IndependentFragment: {uid}")
            units[uid]["status"] = units[rs["unit"]]["status"]
    joint = _joint(block, active)
    return {"references": references, "groups": groups, "joint": joint,
            "presentations": presentations}


def report_discourse(doc, result):
    info = doc["discourse"]
    result["references"] = info["references"]
    result["groups"] = info["groups"]
    result["reviewed_presentations"] = info.get("presentations", {})
    result["joint_choices"] = {k: v for k, v in info["joint"].items() if k != "choices"}
    inner_id = result.get("admission", {}).get("report_id") or digest(
        "ve-document-inner@1\n", {"document_id": doc["document_id"],
                                   "premises": result["premises"]})
    result["report_id"] = digest(
        "ve-discourse-report@1\n",
        {"profiles": doc["meta"]["environment"]["profiles"],
         "environment_id": doc["environment"].environment_id,
         "document_id": doc["document_id"],
         "report_id": inner_id,
         "references": result["references"], "validity": []})
