"""Untrusted reports@0 document elaboration and identity binding.

This module prepares FOL input for the existing search/replay machinery. It
never treats that preparation, or a search result, as a semantic certificate.
"""
from __future__ import annotations

from collections import defaultdict
import hashlib
import json

from .admission import token
from .ast import formula_from_data, formula_to_data
from .environment import Environment
from .limits import MAX_PREDICATES
from .errors import DuplicateDeclaration, ResourceLimit, UnsupportedProfile, VEError
from .wire import canonical_json

ACTS = frozenset(("says", "believes", "wants", "intends"))
JUDGMENTS = frozenset(("may", "probably"))
# W2's support values (`ve/document.py` SUPPORTS; Lean `supports`).
SUPPORTS = frozenset(("assumption", "certificate", "observation", "calculation", "statistical",
                      "testimony", "adapter", "none"))


def _canonical(value):
    """RFC 8785 ordering for the reports subset, including optional JSON null."""
    if value is None:
        return b"null"
    if type(value) is dict:
        return ("{" + ",".join(_canonical(k).decode() + ":" + _canonical(value[k]).decode()
                               for k in sorted(value, key=lambda s: s.encode("utf-16be"))) + "}").encode()
    if type(value) is list:
        return ("[" + ",".join(_canonical(v).decode() for v in value) + "]").encode()
    return canonical_json(value)


def _id(domain, value):
    return hashlib.sha256(domain.encode("ascii") + _canonical(value)).hexdigest()


def _records(rows, label, limit):
    if type(rows) is not list:
        raise VEError(f"InvalidInput: {label} must be a list")
    if len(rows) > limit:
        raise ResourceLimit(f"ResourceLimit: {label}")
    result = {}
    for row in rows:
        if type(row) is not dict or not token(row.get("id")):
            raise VEError(f"InvalidInput: {label} record")
        if row["id"] in result:
            raise DuplicateDeclaration(f"DuplicateDeclaration: {label[:-1]} {row['id']}")
        result[row["id"]] = dict(row)
    return result


class ReportsDocument:
    def __init__(self, environment: Environment, contexts, assessments, units, *,
                 bridges=(), scoped=(), choices=(), open_terms=()):
        if "reports@0" not in environment.profiles or environment.reports is None:
            raise UnsupportedProfile("reports@0 needs a reports block")
        self.environment = environment
        self.contexts = _records(contexts, "contexts", 256)
        self.assessments = _records(assessments, "assessments", 256)
        self.units = units
        self.bridges = list(bridges)
        self.scoped = list(scoped)
        for label, rows in (("bridge", self.bridges), ("scoped", self.scoped)):
            ids = [row.get("id") if type(row) is dict else None for row in rows]
            duplicate = next((i for n, i in enumerate(ids) if i in ids[:n]), None)
            if duplicate is not None:
                raise DuplicateDeclaration(f"DuplicateDeclaration: {label} {duplicate}")
        self.choices = list(choices)
        self.declared_open_terms = list(open_terms)
        if len(self.bridges) > 1000 or len(self.scoped) > 256:
            raise ResourceLimit("ResourceLimit: bridges or scoped")
        if self.choices:
            raise UnsupportedProfile("reports reading choices await the Lean route")
        self._objects = {}
        for cid, row in self.contexts.items():
            if (set(row) not in ({"id", "tense", "description"},
                                 {"id", "tense", "reference_time", "description"})
                    or ("reference_time" in row and row["reference_time"] is not None
                        and not token(row["reference_time"]))
                    or type(row["description"]) is not str or not row["description"]):
                raise VEError(f"InvalidInput: context {cid}")
            if row["tense"] not in ("present", "past", "perfect"):
                raise VEError(f"ContextTense: {cid}")
            if len(row["description"].encode()) > 200:
                raise ResourceLimit("ResourceLimit: context description")
        evidence = environment.reports["evidence"]
        for aid, row in self.assessments.items():
            needed = {"id", "context", "decided_by", "necessary", "sufficient",
                      "factors", "precedents", "jurisdiction", "version"}
            if set(row) != needed or not token(row.get("decided_by")):
                raise VEError(f"InvalidInput: assessment {aid} needs decided_by")
            if (row["context"] not in environment.constants or
                    environment.constants[row["context"]].sort != evidence):
                raise VEError(f"UnknownSymbol: evidence context {row['context']}")
            if (not token(row["jurisdiction"]) or type(row["version"]) is not int
                    or row["version"] < 1 or any(type(row[f]) is not list for f in
                    ("necessary", "sufficient", "factors", "precedents"))):
                raise VEError(f"InvalidInput: assessment {aid}")
            for field in ("necessary", "sufficient"):
                row[field] = [formula_to_data(environment, formula_from_data(environment, formula))
                              for formula in row[field]]
            if any(type(x) is not str or not x for f in ("factors", "precedents") for x in row[f]):
                raise VEError(f"InvalidInput: assessment {aid}")
        if type(units) is not list:
            raise VEError("InvalidInput: units must be a list")
        self.report_keys = set()
        self.assessment_keys = set()
        canonical_units = []
        w2_units = []
        unit_ids = set()
        self.metadata = []
        cursor = 0
        for unit in units:
            if (type(unit) is not dict or not token(unit.get("id")) or unit["id"] in unit_ids):
                raise VEError("InvalidInput: report unit")
            unit_ids.add(unit["id"])
            span = unit.get("span")
            if (type(span) is not list or len(span) != 2 or any(type(x) is not int or x < 0 for x in span)
                    or span[0] > span[1] or span[0] < cursor):
                raise VEError("unit spans must be sorted and non-overlapping")
            cursor = span[1]
            is_report = (type(unit.get("content")) is dict and bool(set(unit["content"]) &
                                                                    {"report", "assessment", "negated"}))
            fields = {"id", "span", "kind", "content", "meaning", "support"}
            if (set(unit) != fields if is_report else not {"id", "span", "kind"} <= set(unit) <= fields):
                raise VEError(f"InvalidInput: unit {unit['id']} fields")
            self.metadata.append({"id": unit["id"], "span": span,
                                  **({"meaning": self._meaning(unit["meaning"])} if "meaning" in unit else {}),
                                  **({"support": unit["support"]} if "support" in unit else {})})
            if not is_report:
                w2_units.append({"id": unit["id"], "kind": json.dumps(unit.get("kind"),
                                  ensure_ascii=False, separators=(",", ":")),
                                 **self._w2_content(unit)})
                continue
            content_object = self._node(unit["content"], unit["id"], top=True)
            if "kind" in unit and not self._kind_matches(unit["kind"], unit["content"]):
                raise VEError(f"KindMismatch: {unit['id']}")
            canonical_units.append({"id": unit["id"], "content": content_object})
        self.names = {}
        for keys, offset in ((self.report_keys, 0), (self.assessment_keys, 1)):
            grouped = defaultdict(list)
            for key in sorted(keys):
                grouped[key[0]].append(key)
            for act, group in grouped.items():
                for index, key in enumerate(group, 1):
                    self.names[(offset, key)] = f"reports__{act}__{index}"
        self.open_terms = []
        for key in sorted(self.assessment_keys):
            record = self.assessments[key[1]]
            self.open_terms.append({"name": self.names[(1, key)],
                                    "arguments": [environment.reports["evidence"]],
                                    "record": record})
        raw = environment.to_dict()
        predicates = raw["vocabulary"]["predicates"]
        for (_, key), name in self.names.items():
            sort = key[1] if len(key) == 4 else evidence
            key_object = ({"act": key[0], "holder_sort": key[1], "context": key[2],
                           "complement_id": key[3]} if len(key) == 4 else
                          {"judgment": key[0], "assessment": key[1], "content_id": key[2]})
            predicates[name] = {"arguments": [sort],
                                "description": "generated by reports@0 for " +
                                json.dumps(key_object, ensure_ascii=False, sort_keys=True,
                                           separators=(",", ":"))}
        # 4.1 steps 5 and 6, in Lean's order (`scopedOk`, then `bridgeOk`), then
        # the units' W2 metadata (`metaOk`), before step 7.
        self.scoped_objects = [self._scoped_object(s) for s in self.scoped]
        self.bridge_objects = [self._bridge_object(b) for b in self.bridges]
        for row in self.metadata:
            self._check_metadata(row)
        if len(predicates) > MAX_PREDICATES:
            raise ResourceLimit("ResourceLimit: MAX_PREDICATES")
        self.extended_environment = Environment(raw, _generated_reports=True)
        self.premises = [self.elaborate(unit["content"]) for unit in units
                         if type(unit.get("content")) is dict and set(unit["content"]) &
                         {"report", "assessment", "negated"}]
        self.document_id = _id(f"ve-reports-{environment.identity_version}\n",
                               {"environment_id": environment.environment_id,
                                "document": {"units": canonical_units,
                                  "contexts": [self._context_object(c) for c in self.contexts.values()],
                                  "assessments": list(self.assessments.values()),
                                  "bridges": self.bridge_objects,
                                  "scoped": self.scoped_objects,
                                  "w2_units": w2_units, "metadata": self.metadata}})
        self.envelope = {"environment_id": environment.environment_id,
                         "document_id": self.document_id}

    @staticmethod
    def _meaning(value):
        """W2's meaning status (`ve/document.py`), decoded as Lean `decodeMeaning` does."""
        if value == "specified":
            return value
        if type(value) is dict and len(value) == 1:
            (status, detail), = value.items()
            if status == "open" and type(detail) is list and all(type(x) is str for x in detail):
                return {"open": list(detail)}
            if status in ("contextual", "unformalised") and type(detail) is str:
                return {status: detail}
        raise VEError("invalid meaning status")

    def _assessment_names(self, node):
        """The generated names of the assessment nodes of one tree (Lean `unitAssessNames`)."""
        tag, value = next(iter(node.items()))
        if tag == "negated":
            return self._assessment_names(value)
        if tag == "report":
            return self._assessment_names(value["content"])
        if tag == "assessment":
            cid = self._remember(self._node(value["content"], "names"))
            return ([self.names[(1, (value["judgment"], value["record"], cid))]]
                    + self._assessment_names(value["content"]))
        return []

    def _check_metadata(self, row):
        """3.3, W2 and 6 (Lean `metaOk`): W2's support values; an open meaning names
        declared or generated open terms; a report unit is `specified` exactly when
        its tree has no assessment node, and otherwise `open`, listing every
        generated assessment name of its tree."""
        uid, meaning = row["id"], row.get("meaning")
        if "support" in row and (type(row["support"]) is not str or row["support"] not in SUPPORTS):
            raise VEError(f"InvalidInput: support of {uid}")
        generated = {term["name"] for term in self.open_terms}
        valid = (meaning is None or meaning == "specified"
                 or "open" in meaning and bool(meaning["open"]) and all(
                     n in self.declared_open_terms or n in generated for n in meaning["open"])
                 or "contextual" in meaning and bool(meaning["contextual"])
                 or "unformalised" in meaning and token(meaning["unformalised"]))
        unit = next((u for u in self.units if u["id"] == uid and type(u.get("content")) is dict
                     and set(u["content"]) & {"report", "assessment", "negated"}), None)
        if valid and unit is not None:
            names = self._assessment_names(unit["content"])
            valid = (meaning == "specified" and not names
                     or type(meaning) is dict and "open" in meaning and set(names) <= set(meaning["open"]))
        if not valid:
            raise VEError(f"InvalidInput: meaning of {uid}")

    def _w2_content(self, unit):
        """An ordinary W2 unit's content as the Lean decoder reads it: absent, or
        exactly ``{"ast": φ}`` with φ closed over E, never on a quoted kind."""
        if "content" not in unit or unit["content"] is None:
            return {}
        content = unit["content"]
        if type(unit.get("kind")) is list and unit["kind"][0] in ("attributed", "hedged"):
            raise VEError(f"InvalidInput: invalid content for {unit['id']}")
        if type(content) is not dict or set(content) != {"ast"}:
            raise VEError(f"InvalidInput: invalid content for {unit['id']}")
        return {"content": formula_to_data(self.environment, formula_from_data(self.environment, content["ast"]))}

    @staticmethod
    def _context_object(row):
        return {key: value for key, value in row.items() if key != "reference_time" or value is not None}

    @staticmethod
    def _path_object(path):
        if type(path) is str:
            return {"unit": path, "depth": 0}
        if type(path) is dict and set(path) == {"unit", "path"} and type(path["path"]) is str:
            parts = path["path"].split(".")
            if parts and all(p == "1" for p in parts):
                return {"unit": path["unit"], "depth": len(parts)}
        raise VEError("InvalidInput: bridge path")

    def _bridge_object(self, row):
        """3.2 and 4.1 step 6 (Lean `decodeBridge`, `bridgeOk`): the target resolves
        (`BridgeTarget`) to a formula, report or assessment node in the author's
        scope (`BridgeKindMismatch` for a norm or definition node and for any node
        under a quoted package, such as a definition package's statement)."""
        if (type(row) is not dict or not {"id", "unit", "accepted_by", "reason"} <= set(row)
                or set(row) - {"id", "unit", "accepted_by", "reason", "path"}
                or any(type(row[f]) is not str for f in ("id", "unit", "accepted_by"))
                or type(row["reason"]) is not list or any(type(r) is not str for r in row["reason"])):
            raise VEError("InvalidInput: bridge")
        target = self._path_object({"unit": row["unit"], "path": row["path"]} if "path" in row else row["unit"])
        content, scope = self._resolve(target)
        if content is None:
            raise VEError(f"BridgeTarget: {target['unit']}")
        if next(iter(content)) in ("norm", "definition") or scope is not self.environment:
            raise VEError(f"BridgeKindMismatch: {target['unit']}, {target['depth']}")
        return {"id": row["id"], "target": target, "accepted_by": row["accepted_by"], "reason": row["reason"]}

    def _scoped_object(self, row):
        """3.2 and 4.1 step 5 (Lean `decodeScoped`, `scopedOk`): at most 64 payloads,
        each a formula node (`ScopedTarget`), all in one scope with a conclusion
        closed over it (`ScopedEnvironment`). A carried certificate may carry its
        envelope (3.4); an envelope without a certificate is malformed."""
        if (type(row) is not dict or not {"id", "payloads", "conclusion"} <= set(row)
                or set(row) - {"id", "payloads", "conclusion", "certificate", "envelope"} or type(row["id"]) is not str
                or type(row["payloads"]) is not list or type(row["conclusion"]) is not dict
                or set(row["conclusion"]) != {"ast"}):
            raise VEError("InvalidInput: scoped")
        if "envelope" in row and "certificate" not in row:
            raise VEError(f"InvalidInput: envelope without a certificate on scoped check {row['id']}")
        payloads = [self._path_object(p) for p in row["payloads"]]
        if len(payloads) > 64:
            raise ResourceLimit("ResourceLimit: scoped payloads")
        resolved = [self._resolve(p) for p in payloads]
        if any(c is None or next(iter(c)) != "ast" for c, _ in resolved):
            raise VEError(f"ScopedTarget: {row['id']}")
        if not payloads or any(s.environment_id != resolved[0][1].environment_id for _, s in resolved):
            raise VEError(f"ScopedEnvironment: {row['id']}")
        scope = resolved[0][1]
        try:
            conclusion = formula_to_data(scope, formula_from_data(scope, row["conclusion"]["ast"]))
        except VEError as exc:
            raise VEError(f"ScopedEnvironment: {row['id']}") from exc
        return {"id": row["id"], "payloads": payloads, "conclusion": conclusion}

    def _remember(self, obj):
        cid = _id(f"ve-content-{self.environment.identity_version}\n", obj)
        if cid in self._objects and self._objects[cid] != obj:
            raise VEError(f"HashCollision: {cid}")
        self._objects[cid] = obj
        return cid

    @staticmethod
    def _kind_matches(kind, node):
        tag, value = next(iter(node.items()))
        if tag == "negated":
            return ReportsDocument._kind_matches(kind, value)
        if tag == "ast":
            return kind == "asserted"
        if tag in ("norm", "definition"):
            return kind == tag
        if tag == "report":
            return (type(kind) is list and len(kind) == 4 and kind[:3] ==
                    ["attributed", value["holder"], value["act"]] and
                    ReportsDocument._kind_matches(kind[3], value["content"]))
        if tag == "assessment":
            return (type(kind) is list and len(kind) == 3 and kind[:2] ==
                    ["hedged", "could" if value["judgment"] == "may" else "likely"] and
                    ReportsDocument._kind_matches(kind[2], value["content"]))
        return False

    def _node(self, node, unit, *, top=False, depth=1):
        if depth > 16:
            raise ResourceLimit("ResourceLimit: content depth")
        if type(node) is not dict or len(node) != 1:
            raise VEError(f"InvalidInput: invalid content for {unit}")
        tag, value = next(iter(node.items()))
        if top and tag not in ("report", "assessment", "negated"):
            raise VEError(f"InvalidInput: invalid content for {unit}")
        if tag == "ast":
            formula = formula_from_data(self.environment, value)
            obj = {"environment_id": self.environment.environment_id,
                   "ast": formula_to_data(self.environment, formula)}
        elif tag == "norm":
            from .norms import NormDocument
            if type(value) is not dict or set(value) != {"environment", "norms"}:
                raise VEError(f"InvalidInput: quoted norm in {unit}")
            local = Environment(value["environment"])
            if "norms@0" not in local.profiles:
                raise UnsupportedProfile("quoted norm needs norms@0 locally")
            checked = NormDocument(local, value["norms"])
            obj = {"environment_id": local.environment_id,
                   "norms": [rule.to_dict() for rule in checked.rules]}
        elif tag == "definition":
            if type(value) is not dict or set(value) != {"environment", "content"}:
                raise VEError(f"InvalidInput: quoted definition in {unit}")
            local = Environment(value["environment"])
            if "definitions@0" not in local.profiles:
                raise UnsupportedProfile("quoted definition needs definitions@0 locally")
            statement = value["content"]
            if statement is not None:
                if type(statement) is not dict or set(statement) != {"ast"}:
                    raise VEError(f"InvalidInput: definition statement in {unit}")
                formula = formula_from_data(local, statement["ast"])
                statement = {"environment_id": local.environment_id,
                             "ast": formula_to_data(local, formula)}
                self._remember(statement)
            obj = {"environment_id": local.environment_id,
                   **({"content": statement} if statement is not None else {})}
        elif tag == "report":
            if type(value) is not dict or set(value) not in (
                    {"holder", "act", "context", "content"},
                    {"holder", "act", "context", "literal", "content"}):
                raise VEError(f"InvalidInput: report in {unit}")
            holder, act, context = value["holder"], value["act"], value["context"]
            if holder not in self.environment.constants:
                raise VEError(f"UnknownHolder: {holder}")
            sort = self.environment.constants[holder].sort
            if sort not in self.environment.reports["holders"]:
                raise VEError(f"HolderSort: {holder} is not of a holder sort")
            if act not in ACTS:
                raise VEError(f"UnsupportedAct: {act} (reports@0 admits says, believes, wants, intends)")
            if context not in self.contexts:
                raise VEError(f"UnknownContext: {context}")
            literal = value.get("literal")
            if literal is not None and (type(literal) is not str or not literal):
                raise VEError("InvalidInput: literal")
            if literal is not None and len(literal.encode()) > 4096:
                raise ResourceLimit("ResourceLimit: literal bytes")
            inner = self._node(value["content"], unit, depth=depth + 1)
            complement = {"content": inner, **({"literal": literal} if literal is not None else {})}
            complement_id = self._remember(complement)
            self.report_keys.add((act, sort, context, complement_id))
            obj = {"holder": holder, "act": act, "context": self._context_object(self.contexts[context]),
                   "complement": complement}
        elif tag == "assessment":
            if type(value) is not dict or set(value) != {"judgment", "record", "content"}:
                raise VEError(f"InvalidInput: assessment in {unit}")
            if value["judgment"] not in JUDGMENTS or value["record"] not in self.assessments:
                raise VEError(f"UnknownAssessment: {value.get('record')}")
            inner = self._node(value["content"], unit, depth=depth + 1)
            cid = self._remember(inner)
            self.assessment_keys.add((value["judgment"], value["record"], cid))
            obj = {"judgment": value["judgment"], "record": self.assessments[value["record"]],
                   "content": inner}
        elif tag == "negated":
            if type(value) is not dict or len(value) != 1 or next(iter(value)) not in ("report", "assessment"):
                raise VEError(f"InvalidInput: negated operand in {unit}")
            obj = {"negated": self._node(value, unit, depth=depth)}
        else:
            raise VEError(f"InvalidInput: invalid content for {unit}")
        if self.choices:
            obj = {**obj, "choices": self.choices}
        self._remember(obj)
        return obj

    def elaborate(self, node):
        tag, value = next(iter(node.items()))
        if tag == "negated":
            return ["not", self.elaborate(value)]
        if tag == "ast":
            return formula_to_data(self.extended_environment,
                                   formula_from_data(self.environment, value))
        if tag == "report":
            inner = self._node(value["content"], "elaboration")
            cid = self._remember({"content": inner,
                                  **({"literal": value["literal"]} if value.get("literal") is not None else {})})
            sort = self.environment.constants[value["holder"]].sort
            key = (value["act"], sort, value["context"], cid)
            return ["unary", self.names[(0, key)], ["const", value["holder"]]]
        if tag == "assessment":
            cid = self._remember(self._node(value["content"], "elaboration"))
            key = (value["judgment"], value["record"], cid)
            holder = self.assessments[value["record"]]["context"]
            return ["unary", self.names[(1, key)], ["const", holder]]
        raise VEError("quoted blocks need local validation before elaboration")

    def search_payload(self, conclusion=None):
        """Explicitly untrusted FOL problem for Rust witness search."""
        return {"family": "elaborated-document", "profile": "reports@0", "untrusted": True,
                "environment": self.extended_environment.to_dict(),
                "premises": self.premises, "envelope": self.envelope,
                "open_terms": self.open_terms,
                **({"conclusion": conclusion} if conclusion is not None else {})}

    def elaborated(self):
        """The independent Python projection compared with the Lean reports route."""
        keys = []
        for (offset, key), name in self.names.items():
            if offset == 0:
                source = {"act": key[0], "holder_sort": key[1], "context": key[2],
                          "complement_id": key[3]}
                arguments = [key[1]]
            else:
                source = {"judgment": key[0], "assessment": key[1], "content_id": key[2]}
                arguments = [self.environment.reports["evidence"]]
            keys.append({"name": name, "arguments": arguments, "key": source})
        report_units = [u for u in self.units if type(u.get("content")) is dict and
                        set(u["content"]) & {"report", "assessment", "negated"}]
        premises = [{"label": ("assessment:" if self._is_assessment(u["content"]) else "report:") + u["id"],
                     "ast": self.elaborate(u["content"])} for u in report_units]
        bridges = [{"id": row["id"], "unit": row["target"]["unit"], "depth": row["target"]["depth"],
                    "ast": self.elaborate(self._resolve(row["target"])[0])} for row in self.bridge_objects]
        return {"environment_reports_id": self.extended_environment.environment_id,
                "keys": keys, "premises": premises, "open_terms": self.open_terms,
                "bridge_formulas": bridges,
                "content_ids": [{"unit": u["id"], "content_id":
                                 _id(f"ve-content-{self.environment.identity_version}\n",
                                     self._node(u["content"], u["id"]))} for u in report_units],
                "envelope": self.envelope,
                "warnings": [f"unreviewed act {u['kind'][2]} in {u['id']}" for u in self.units
                             if u not in report_units and type(u.get("kind")) is list and
                             len(u["kind"]) == 4 and u["kind"][0] == "attributed" and
                             u["kind"][2] not in ACTS]}

    @staticmethod
    def _is_assessment(content):
        if "negated" in content:
            return ReportsDocument._is_assessment(content["negated"])
        return "assessment" in content

    def _resolve(self, target):
        """Lean `contentAt` and `scopeAt`: descend from the unit's root, once more per
        `1`, through negated nodes; a definition package's statement is over its
        pinned environment. Only report units are targets."""
        unit = next((u for u in self.units if u["id"] == target["unit"] and type(u.get("content")) is dict
                     and set(u["content"]) & {"report", "assessment", "negated"}), None)
        if unit is None:
            return None, None
        node, scope = unit["content"], self.environment
        for _ in range(target["depth"] + 1):
            if node is None:
                return None, None
            if "negated" in node:
                node = node["negated"]
            if "report" in node or "assessment" in node:
                node = next(iter(node.values()))["content"]
            elif "definition" in node:
                scope = Environment(node["definition"]["environment"])
                node = node["definition"].get("content")
            else:
                return None, None
        return node, scope

    def meaning_id(self, node):
        obj = self._node(node, "meaning")
        return _id(f"ve-meaning-{self.environment.identity_version}\n",
                   {"environment_id": self.environment.environment_id, "ast": obj})
