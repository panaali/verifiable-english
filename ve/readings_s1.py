"""Python's construction of S1 readings documents (docs/spec/composition-s1.md 1.1 to 1.7), for the English of the
checked answer and for the untrusted search for separating situations (10).

Lean owns every decision about a `readings@1` document: `ve/readings_route.py` relays `ve_readings_route`'s
`readings-validate` row (the checks of 4.1, every candidate's document, keys and chain findings, every recorded
separation, the findings of 4.6), and nothing here checks or regenerates it (lean-first batch 3). What is left
builds, from the environment and the document, the contents, each candidate's chain document (`one D s i`) and its
generated keys, which the English of `readings_route.Wording` names, and which the search evaluates. A document
Lean refuses never reaches the English, and a construction that fails on a document Lean accepted is the route's
`CheckerUnavailable` (docs/LEAN-FIRST-PLAN.md rule 2). The search runs before Lean has seen the situations: it
only proposes, and Lean's answer on the recorded document is the only check (8.5).

Four pieces repeat Lean's logic and are retained, listed as unfinished in `docs/lean-first/b3/LEDGER.md`: the
attachment relation (`Document.attached`, Lean's `attached`), the generated keys (`Side.gen_keys`, `genKeys`),
the force twins and acts the English names (`force_twins`, `content_acts`: `forceTwins`, `contentActs`), and the
search's evaluation of a candidate's side (`Side.valid`, `Side.observe`: `sideValid`, `sideValue`), which is a
generator-internal duplicate under the plan's rule 3.
"""
from __future__ import annotations

import json
from itertools import product

from .errors import CheckerUnavailable, VEError
from .wire import digest

READINGS = "readings@1"
RIGHTS_KINDS = ("right", "right_lines", "limitation", "bar", "norm")
MAX_CELLS = 12
PROBE_KINDS = ("claim", "liberty", "immunity", "powerLiberty", "powerRecognition", "norm")


def wire(value):
    """The restricted Lean input has no null literal: pending content is sent by omission."""
    if type(value) is dict:
        return {key: wire(item) for key, item in value.items() if item is not None}
    if type(value) is list:
        return [wire(item) for item in value]
    return value


def _canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def _sorted_items(value):
    """A JSON object's entries in Lean's order (its objects are ordered by key)."""
    return sorted(value.items()) if type(value) is dict else []


# ---------------------------------------------------------------------------------------------------------------
# The environment (1.1)

def _placeholder_frame(data):
    """`unspecified` completions read as `deny` (Lean `Wire.placeholderFrame`); every other field unchanged."""
    predicates = (data.get("vocabulary") or {}).get("predicates")
    if type(predicates) is not dict:
        return data
    renamed = {name: ({**decl, "regulated": {**decl["regulated"], "default": "deny"}}
                      if type(decl) is dict and type(decl.get("regulated")) is dict
                      and decl["regulated"].get("default") == "unspecified" else decl)
               for name, decl in predicates.items()}
    return {**data, "vocabulary": {**data["vocabulary"], "predicates": renamed}}


class S1Environment:
    """The environment with `readings@1`, its chain, and the lower and frame environments. The environment is read
    as Lean receives it (`wire`), as the document is: an explicit null is an absent field at every depth, so
    `vocabulary.soft: null` or a predicate's `regulated: null` is decoded as Lean decodes it."""

    def __init__(self, data):
        from .document import _environment
        data = wire(data)
        self.data = data
        self.env = _environment(data)
        self.profiles = list(self.env.profiles)
        self.lower_profiles = [p for p in self.profiles if p != READINGS]
        self.lower_data = {**data, "profiles": self.lower_profiles}
        self.chain = ("rights" if "rights@0" in self.profiles else
                      "soft" if "soft-norms@0" in self.profiles else "norms")
        frame = [p for p in self.lower_profiles if p != "norm-defaults@0"]
        self.frame_data = {**data, "profiles": frame}
        if "norm-defaults@0" in self.lower_profiles:
            # DRI ruling 4 (2026-10-03): the frame reads each `unspecified` completion as the placeholder `deny`
            # (norm-defaults 2.3's E‴), as Lean's `placeholderFrame` does, so that the frame decodes without the
            # profile and content beside it reaches the abstention of 1.1 instead of a decoder text.
            self.frame_data = _placeholder_frame(self.frame_data)
        self.frame = _environment(self.frame_data)
        self.regulated = {name: decl for name, decl in self.frame.predicates.items() if decl.regulated is not None}

    def soft_frame(self):
        """The frame as a soft environment: on the norms chain, with the empty soft block (13.6)."""
        from .softnorms import SoftEnvironment
        if self.chain != "norms":
            return SoftEnvironment(self.frame_data) if self.chain == "soft" else None
        data = json.loads(json.dumps(self.frame_data))
        data["profiles"] = sorted({*data["profiles"], "soft-norms@0"})
        data["vocabulary"]["soft"] = {"parties": [], "ranks": [], "outranks": [], "ties": [],
                                      "outranking": {"mode": "strict"}}
        return SoftEnvironment(data)

    def author_environment(self):
        """The author's base vocabulary: the frame without regulated predicates (4.5 step 1)."""
        from .environment import Environment
        data = json.loads(json.dumps(self.frame_data))
        data["vocabulary"].pop("soft", None)
        data["vocabulary"].pop("rights", None)
        data["vocabulary"]["predicates"] = {
            name: {k: v for k, v in decl.items() if k != "instruction_of"}
            for name, decl in data["vocabulary"]["predicates"].items() if "regulated" not in decl}
        data["profiles"] = [p for p in data["profiles"] if p not in ("norms@0", "soft-norms@0", "rights@0", "readings@1")]
        return Environment(data)

    def situation_id(self, entry):
        return digest(f"ve-situation-{self.env.identity_version}\n",
                      {"environment_id": self.env.environment_id, "situation": entry})


# ---------------------------------------------------------------------------------------------------------------
# Contents, names and the document (1.2 to 1.4)

class Content:
    """A decoded content: `kind` is the content's W2 kind word, `body` its JSON, `cites` a norm's citations."""

    def __init__(self, kind, body, raw, cites=None):
        self.kind, self.body, self.raw, self.cites = kind, body, raw, cites or {}

    def lines(self):
        return self.body.get("lines", []) if self.kind in ("right", "right_lines") else []

    def rules(self):
        """The rule objects the content states: a norm's body, or every rule-bearing field of each of its lines."""
        from .rights import RULE_FIELDS
        if self.kind == "norm":
            return [self.body]
        return [line[k] for line in self.lines() for k in RULE_FIELDS if type(line.get(k)) is dict]

    def declared(self):
        if self.kind == "assertion":
            return []
        if self.kind == "norm":
            return [("rule", self.body["name"])]
        names = [("rule", n) for line in self.lines() for n in _line_rule_names(line)]
        if self.kind == "right":
            return [("right", self.body["name"]), *names]
        if self.kind == "right_lines":
            return names
        return [("limitation", self.body["name"])]

    def uses(self):
        if self.kind == "assertion":
            return []
        if self.kind == "norm":
            return [("rule", n) for n in self.body.get("over", [])] + _cite_uses(self.cites)
        if self.kind == "right":
            return [u for line in self.lines() for u in _line_uses(line)]
        if self.kind == "right_lines":
            return [("right", self.body["right"])] + [u for line in self.lines() for u in _line_uses(line)]
        scope = self.body.get("scope")
        return [("right", r) for r in scope] if type(scope) is list else []


def _line_rule_names(line):
    """The names of the rules a line states, from every rule-bearing field of the rights schema (`RULE_FIELDS`)."""
    from .rights import RULE_FIELDS
    return [line[k]["name"] for k in RULE_FIELDS if type(line.get(k)) is dict]


def _cite_uses(cites):
    uses = []
    for key, _ in _sorted_items(cites):
        if key.startswith("over:"):
            uses.append(("rule", key[5:]))
        elif key.startswith("narrows:"):
            uses.append(("rule", key[8:]))
    return uses


def _line_uses(line):
    from .rights import RULE_FIELDS
    uses = [("rule", n) for k in RULE_FIELDS if type(line.get(k)) is dict
            for n in line[k].get("over", [])]
    return uses + _cite_uses(line.get("cites", {}))


# Decoded values. Lean compares contents as it decodes them (`SourceLine`, `SoftNode`, a right's header), not as
# written: an absent `cites`, `fan_out`, `mode`, `alterable` or `hard` is its default, and formulas are trees.
# The force twins of 1.7 compare contents through these values.

_UNDECODED = (VEError, TypeError, KeyError, AttributeError, ValueError, RecursionError)
_LINE_FIELDS = {"kind", "norm", "liberty", "recognition", "fan_out", "holder_slot", "cites"}


def node_value(raw, fan_pred=None):
    """A norm object as `ruleFields` decodes it (a `SoftNode`); raises when it does not decode. A fan-out line's
    absent predicate is its first mapped predicate (`decodeLineNorm`). The exception decider decides only whether
    the object decodes, never its value, so a stand-in is passed."""
    from .softnorms import _hydrate_rule
    if type(raw) is dict and fan_pred is not None and "predicate" not in raw:
        raw = {**raw, "predicate": fan_pred}
    f = _hydrate_rule({"norm": wire(raw)})
    exception = None
    if f.mode == "default":
        from .ast import _Decoder
        decoder = _Decoder()
        exception = (f.exception.get("decided_by"),
                     tuple(decoder.decode(x) for x in f.exception["sufficient"]),
                     tuple(decoder.decode(x) for x in f.exception["necessary"]),
                     tuple(f.exception["factors"]))
    return (f.core, f.mode, f.rank, f.alterable, exception, f.hard)


def line_value(line):
    """A line as `decodeLine` decodes it (a `SourceLine`): kind, rules, fan-out, holder slot, citations. A line
    that does not decode keeps its JSON (Lean refuses its document)."""
    j = wire(line)
    try:
        if set(j) - _LINE_FIELDS or j["kind"] not in ("claim", "liberty", "immunity", "power"):
            raise ValueError("line")
        slot = j.get("holder_slot", 0)
        if type(slot) is not int or slot < 0 or any(
                type(us) is not list or not us or any(type(u) is not str for u in us)
                for us in j.get("cites", {}).values()):
            raise ValueError("line")
        fan = j.get("fan_out", {})
        fan_out = tuple(sorted(fan.items()))
        if any(type(p) is not str for _, p in fan_out):
            raise TypeError("fan_out")
        fan_pred = fan_out[0][1] if fan_out else None
        rules = tuple(node_value(j[k], fan_pred) if k in j else None for k in ("norm", "liberty", "recognition"))
        cites = tuple((k, tuple(v)) for k, v in sorted(j.get("cites", {}).items()))
        return (j["kind"], rules, fan_out, j.get("holder_slot"), cites)
    except _UNDECODED:
        return ("undecoded", _canonical(j))


def lean_defaults(unit):
    """A rights unit with the defaults Lean's rights decoder reads written out, for Python's rights decoder, which
    requires the fields. Lean receives `wire(unit)`, so an absent field and a null one are the same to it: a right's
    guard is `top` (`decodeRight`), an empty `fan_out` is no fan-out (`decodeLine`), a limitation's or condition's
    decider is null (`decodeLimitation`, `decodeCondition`), and a bar's absent decider, which `validDecider`
    accepts and nothing reads, is `unstated` (`decodeBar`). Anything else is left as written."""
    if type(unit) is not dict or len(unit) != 1:
        return unit
    [(kind, body)] = unit.items()
    if type(body) is not dict:
        return unit

    def line(x):
        if type(x) is dict and x.get("fan_out") == {}:
            return {k: v for k, v in x.items() if k != "fan_out"}
        return x

    if kind in ("right", "right_lines"):
        body = dict(body)
        if kind == "right" and body.get("guard") is None:
            body["guard"] = ["top"]
        if type(body.get("lines")) is list:
            body["lines"] = [line(x) for x in body["lines"]]
    elif kind == "limitation":
        body = {"decided_by": None, **body}
        if type(body.get("conditions")) is list:
            body["conditions"] = [{"decided_by": None, **c} if type(c) is dict else c for c in body["conditions"]]
    elif kind == "bar" and body.get("decided_by") is None:
        body = {**body, "decided_by": "unstated"}
    return {kind: body}


def _right_header(body):
    """A right's name, holder and guard as `decodeRight` decodes them: an absent guard is `top`."""
    from .ast import Top, _Decoder
    guard = wire(body).get("guard")
    return (body.get("name"), body.get("holder"), Top() if guard is None else _Decoder().decode(guard))


def decode_content(j):
    """`Content`, `("bar", body)` or None (pending), as `Wire.decodeContent` reads a unit content."""
    if type(j) is list:
        return Content("assertion", j, j)
    if type(j) is not dict:
        return None
    keys = sorted(j)
    if keys in (["norm"], ["cites", "norm"]):
        return Content("norm", j["norm"], j, j.get("cites", {}))
    if keys == ["right"]:
        return Content("right", j["right"], j)
    if keys == ["right_lines"]:
        return Content("right_lines", j["right_lines"], j)
    if keys == ["limitation"]:
        return Content("limitation", j["limitation"], j)
    if keys == ["bar"]:
        return ("bar", j["bar"])
    return None


def in_force(kind, content):
    """`Wire.inForce`: a unit's content is in force only under its kind (1.2)."""
    if content.kind == "assertion":
        return kind == "asserted"
    if content.kind == "norm":
        return kind == "norm"
    return type(kind) is str and kind in RIGHTS_KINDS


class Candidate:
    def __init__(self, cid, content, labels):
        self.id, self.content, self.labels = cid, content, labels


class ReadingSet:
    def __init__(self, raw, candidates):
        self.raw = raw
        self.id, self.unit, self.version = raw["id"], raw["unit"], raw["version"]
        self.candidates = candidates
        self.situations = raw.get("situations") or {}


class Document:
    """The items of 1.2 in source order: ("fixed", unit, Content), ("bar", unit, raw json), ("set", ReadingSet).
    The document is read as Lean receives it (`wire`): an explicit null is an absent field at every depth, so a
    right's line with `cites: null` or a norm with `mode: null` is built with its defaults, as Lean decodes it.
    Nothing is checked: a candidate whose content is no content of its kind is Lean's rejection, and is built here
    as written."""

    def __init__(self, senv, document):
        self.senv = senv
        document = wire(document)
        units = document["units"]
        sets = document.get("reading_sets") or []
        self.unit_ids = [u["id"] for u in units]
        active = [r for r in sets if all(o["unit"] != r["unit"] or o["version"] <= r["version"] for o in sets)]
        self.items = []
        for unit in units:
            uid, kind = unit["id"], unit.get("kind")
            reading_set = next((r for r in active if r["unit"] == uid), None)
            if reading_set is not None:
                if reading_set["status"] == "open":
                    self.items.append(("set", uid, ReadingSet(reading_set, [
                        self._candidate(r) for r in reading_set["readings"]])))
                    continue
                [signed] = reading_set["readings"]
                kind, content = signed["kind"], signed.get("content")
            else:
                content = unit.get("content")
            decoded = decode_content(content)
            if isinstance(decoded, Content) and in_force(kind, decoded):
                self.items.append(("fixed", uid, decoded))
            elif type(decoded) is tuple and type(kind) is str and kind in RIGHTS_KINDS:
                self.items.append(("bar", uid, content["bar"]))

    @staticmethod
    def _candidate(reading):
        decoded = decode_content(reading.get("content"))
        if isinstance(decoded, Content) and decoded.kind == "assertion" and reading["kind"] != "asserted":
            decoded = None
        return Candidate(reading["id"], decoded, reading.get("labels") or {})

    @property
    def sets(self):
        return [item[2] for item in self.items if item[0] == "set"]

    def fixed_units(self):
        return [(item[1], item[2]) for item in self.items if item[0] == "fixed"]

    def set_by_id(self, s):
        return next((R for R in self.sets if R.id == s), None)

    # -- names (1.3)

    @staticmethod
    def declared_by(R):
        return [n for a in R.candidates if a.content is not None for n in a.content.declared()]

    @classmethod
    def interface_of(cls, R):
        return [n for n in cls.declared_by(R)
                if all(a.content is not None and n in a.content.declared() for a in R.candidates)]

    def attached(self):
        """The sets each fixed unit is attached to: the least relation of 1.3."""
        fixed = self.fixed_units()
        result = {}
        for u, c in fixed:
            result.setdefault(u, set()).update(
                R.id for R in self.sets if any(n in self.declared_by(R) for n in c.uses()))
        changed = True
        while changed:
            changed = False
            for u, c in fixed:
                for u2, c2 in fixed:
                    if any(n in c2.declared() for n in c.uses()) and not result[u2] <= result[u]:
                        result[u] |= result[u2]
                        changed = True
        return result

    # -- a candidate's document (1.4)

    def build(self, keep, pick):
        """The contents of `build D keep pick`, in source order."""
        return [c for item in self.items for c in self._picked(item, keep, pick)]

    def _picked(self, item, keep, pick):
        if item[0] == "fixed":
            return [item[2]] if keep(item[1]) else []
        if item[0] == "bar":
            return [("bar", item[2])] if keep(item[1]) else []
        a = pick(item[2])
        return [a.content] if a is not None and a.content is not None else []

    def one(self, attached, s, i):
        return self.build(lambda u: all(t == s for t in attached.get(u, ())),
                          lambda R: R.candidates[i] if R.id == s and i < len(R.candidates) else None)


# ---------------------------------------------------------------------------------------------------------------
# One chain document (`one D s i`) with its elaboration, keys and evaluation

class Side:
    """A candidate's chain document assembled from contents in source order (`place`) and elaborated by Python's
    chain classes, unchecked: Lean checks it (`sideWF`). Its soft document is deferred (`SoftNormDocument`): Lean
    is asked for this side alone only when a reader needs a field Lean supplies."""

    def __init__(self, senv, contents, unit_ids):
        self.senv, self.contents, self.unit_ids = senv, contents, unit_ids
        self.assertions = [c.body for c in contents if isinstance(c, Content) and c.kind == "assertion"]
        self.rights = None
        self.soft = None

    def rights_units(self):
        """The units of the side's rights document (the rights chain)."""
        units = [{"source_units": list(self.unit_ids)}]
        for c in self.contents:
            if not isinstance(c, Content):
                units.append(lean_defaults({"bar": c[1]}))
            elif c.kind != "assertion":
                units.append(lean_defaults(c.raw))
        return units

    def _elaborate(self, deferred=True):
        chain = self.senv.chain
        if chain == "rights":
            from .rights import RightsDocument
            self.rights = RightsDocument(self.senv.frame, self.rights_units(), deferred=deferred)
            self.soft = self.rights.soft_document
        else:
            from .softnorms import SoftNormDocument
            self.soft = SoftNormDocument(self.senv.soft_frame(), [c.raw for c in self.contents if c.kind == "norm"],
                                         deferred=deferred)

    # -- S2's regeneration of a choice document's chain refusal (composition-s2.md 4.1 step 5, `route_refusal`)
    #
    # Lean-first batch 3 dropped these from S1, whose answer Lean alone now gives; S2's `elaborate` still compares
    # Python's refusal and certificate binding with Lean's, so they stay here until S2 relays Lean too.

    def line_order_text(self):
        # Lines compare as Lean decodes them (`SourceLine`, `line_value`), not as written.
        rights, order = [], []
        for c in self.contents:
            if not isinstance(c, Content):
                continue
            if c.kind == "right":
                rights.append([c.body["name"], [line_value(line) for line in c.lines()]])
                order.extend((c.body["name"], line_value(line)) for line in c.lines())
            elif c.kind == "right_lines":
                r = c.body["right"]
                for entry in rights:
                    if entry[0] == r:
                        entry[1].extend(line_value(line) for line in c.lines())
                order.extend((r, line_value(line)) for line in c.lines())
        seen = []
        for r, line in order:
            if not any(name == r and line in lines for name, lines in rights):
                return f"UnknownRight: {r}"
            if (r, line) in seen:
                return f"InvalidInput: line order lists a line of right {r} twice"
            seen.append((r, line))
        return None

    def has_rights(self):
        return any(not isinstance(c, Content) or c.kind in ("right", "right_lines", "limitation")
                   for c in self.contents)

    def chain_text(self):
        """`Wire.chainText`: the chain's well-formedness of the document, then its assertions' typing."""
        try:
            self._checked_elaborate()
        except VEError as exc:
            return exc.message if hasattr(exc, "message") else str(exc)
        return None

    def _checked_elaborate(self):
        chain = self.senv.chain
        if chain == "rights":
            text = self.line_order_text()
            if text is not None:
                raise VEError(text)
        else:
            if self.has_rights():
                raise VEError("UnsupportedProfile: rights content requires rights@0")
            norms = [c.raw for c in self.contents if c.kind == "norm"]
            if chain == "norms" and any(
                    c.body.get("mode", "strict") != "strict" or c.body.get("alterable") for c in self.contents
                    if c.kind == "norm"):
                raise VEError("InvalidInput: invalid norm fields")
            from .softnorms import check_soft_source
            check_soft_source(self.senv.soft_frame().to_dict(), norms)
        self._elaborate(deferred=False)
        from .ast import formula_from_data
        env = self.soft.extended_env
        try:
            for ast in self.assertions:
                # Decoding types the closed formula over the complete vocabulary (`a.check` in `sideWF`).
                formula_from_data(env, ast, _generated=True)
        except (VEError, SyntaxError):
            raise VEError("InvalidInput: ill-typed assertion") from None

    # -- the chain's document hash (Run.documentHash)

    def document_hash(self):
        # Lean hashes the units as it receives them: without null values.
        units = [wire(c.raw) if isinstance(c, Content) else {"bar": wire(c[1])} for c in self.contents
                 if not (isinstance(c, Content) and c.kind == "assertion")]
        from .document import _environment
        lower = _environment(self.senv.lower_data)
        payload = {"environment_id": lower.environment_id}
        if self.senv.chain == "rights":
            payload["document"] = [{"source_units": list(self.unit_ids)}] + [_canonical_unit(u) for u in units]
            return digest(f"ve-rights-{lower.identity_version}\n", payload)
        if self.senv.chain == "soft":
            payload["document"] = [_canonical_norm(u) for u in units]
            return digest(f"ve-soft-norms-{lower.identity_version}\n", payload)
        payload["document"] = units
        return digest(f"ve-norms-{lower.identity_version}\n", payload)

    # -- source keys (1.5, `genKeys`)

    def keyed_rules(self):
        """The rules of the elaboration in order, each with its source rule name and bearer (`keyedNodes`)."""
        rules = list(self.soft.rules)
        if self.rights is None:
            return [(rule, rule.core.name, None) for rule in rules]
        keyed = []
        for instance, rule in zip(self.rights.instances, rules):
            bearer = instance["bearer"]
            name = instance["source_line"]["norm"]["name"] if bearer is not None else rule.core.name
            keyed.append((rule, name, bearer))
        keyed.extend((rule, rule.core.name, None) for rule in rules[len(self.rights.instances):])
        return keyed

    def gen_keys(self):
        """`genKeys`: (key, generated name, sorts), in the order of the generated vocabulary."""
        if hasattr(self, "_keys"):
            return self._keys
        sd = self.soft
        env = sd.env
        keyed = self.keyed_rules()
        keys = []
        for rule, name, bearer in keyed:
            if rule.mode == "default":
                keys.append((("excepted", name, bearer), "soft__excepted__" + rule.core.name.replace("-", "_"),
                             list(env.predicates[rule.core.predicate].arguments)))
        for rule, name, bearer in keyed:
            for party in rule.alterable:
                keys.append((("off", name, bearer, party),
                             f"soft__off__{rule.core.name.replace('-', '_')}__{party}",
                             list(env.predicates[rule.core.predicate].arguments)))
        if env.soft["outranking"]["mode"] == "holistic":
            seen = []
            for left, right in sd.collisions:
                generated = sd.override_for_pair.get(frozenset((left.core.name, right.core.name)))
                if generated is None:
                    continue
                _, _, low, high, act = generated.split("__", 4)
                key = ("outweighs", act, low, high)
                if key not in seen:
                    seen.append(key)
                    keys.append((key, generated, list(env.predicates[left.core.predicate].arguments)))
        if self.rights is not None:
            rd = self.rights
            frame = self.senv.frame
            for (limit, act), generated in sorted(rd.limitation_names.items()):
                keys.append((("lim", limit, act), generated, list(frame.predicates[act].arguments)))
            for (limit, act, condition), generated in sorted(rd.condition_names.items()):
                keys.append((("cond", limit, act, condition), generated, list(frame.predicates[act].arguments)))
            for predicate, generated in sorted(rd.bar_names.items()):
                keys.append((("aimed", predicate), generated, list(frame.predicates[predicate].arguments)))
        self._keys = keys
        return keys

    # -- evaluation over a finite base with tables (`tablesModel`, `backgroundValidR`, `observe`)

    def model(self, base, tables):
        """The base model with every generated predicate read from its key's table (`tablesModel`)."""
        relations = {p: set(rows) for p, rows in base.relations.items()}
        for key, name, _ in self.gen_keys():
            relations[name] = set(next((t for k, t in tables if k == key), ()))
        return _Model(base.domains, base.constants, relations)

    def _formulas(self):
        if hasattr(self, "_prepared"):
            return self._prepared
        from .ast import formula_from_data
        from .background import _literal_premises
        tree = self.soft.elaborated
        env = tree.base_environment()
        premises = list(_literal_premises(env))
        premises += [f for _, f in self.soft.extended_env.soft_premises]
        if self.rights is not None:
            premises += [f for _, f in self.rights.limitation_premises]
        assertions = [tree._expand(formula_from_data(self.soft.extended_env, ast, _generated=True), None)
                      for ast in self.assertions]
        self._prepared = (env, premises, assertions)
        return self._prepared

    def valid(self, model):
        from .evaluate import _Evaluator
        env, premises, _ = self._formulas()
        evaluator = _Evaluator(env, model, 10_000_000, trace=False)
        return all(evaluator.formula(f, ())[0] for f in premises)

    def selectable(self, kind, predicate):
        """The rules of the kind on the predicate, as they sit in the elaboration; never by rule name."""
        rules = list(self.soft.rules)
        if kind == "norm":
            count = len(self.rights.instances) if self.rights is not None else 0
            outside = len(self.rights.outside) if self.rights is not None else len(rules)
            return [r for r in rules[count:count + outside] if r.core.predicate == predicate]
        if self.rights is None:
            return []
        return [rule for instance, rule in zip(self.rights.instances, rules)
                if instance["kind"] == kind and rule.core.predicate == predicate]

    def observe(self, model, probe):
        """`observe`: the probe's value in the expansion of the model, or None at a collision."""
        from .evaluate import _Evaluator
        env, _, assertions = self._formulas()
        tree = self.soft.elaborated
        evaluator = _Evaluator(env, model, 10_000_000, trace=False)
        if probe == "holds":
            return all(evaluator.formula(f, ())[0] for f in assertions)
        kind, predicate, row = probe
        sorts = list(self.senv.regulated[predicate].arguments)
        bindings = tuple(zip(reversed(sorts), reversed(row)))
        if kind == "outcome":
            from .ast import And
            positive, negative, _ = tree.selection(predicate)
            conflict = And(tree._expand(positive, predicate), tree._expand(negative, predicate))
            if evaluator.formula(conflict, bindings)[0]:
                return None
            return evaluator.formula(tree.outcome(predicate, base=True), bindings)[0]
        _, _, selected = tree.selection(predicate)
        return any(evaluator.formula(tree._expand(selected[rule.core.name], None), bindings)[0]
                   for rule in self.selectable(kind, predicate))

class _Model:
    def __init__(self, domains, constants, relations):
        self.domains, self.constants = domains, constants
        self.relations = {p: frozenset(map(tuple, rows)) for p, rows in relations.items()}


def _canonical_raw(raw):
    if type(raw) is not dict:
        return raw
    return {k: v for k, v in raw.items()
            if not ((k, v) == ("mode", "strict") or (k, v) == ("alterable", []) or (k, v) == ("hard", False))}


def _canonical_unit(u):
    if "norm" in u:
        return {**u, "norm": _canonical_raw(u["norm"])}
    from .rights import RULE_FIELDS
    for key in ("right", "right_lines"):
        if key in u:
            body = u[key]
            if type(body) is dict and type(body.get("lines")) is list:
                body = {**body, "lines": [{**line, **{k: _canonical_raw(line[k]) for k in RULE_FIELDS if k in line}}
                                          for line in body["lines"]]}
            return {**u, key: body}
    return u


def _canonical_norm(u):
    raw = u.get("norm")
    if type(raw) is not dict:
        return u

    def dropped(k, v):
        return ((k == "mode" and v == "strict") or (k == "rank" and v is None) or (k == "alterable" and v == [])
                or (k == "exception" and v is None) or (k == "hard" and v is False))
    return {"norm": {k: v for k, v in raw.items() if not dropped(k, v)}}


# ---------------------------------------------------------------------------------------------------------------
# Keys on the wire

# The constructors of `GenKey` on the wire (Wire.lean `keyJson`, `decodeKey`): per constructor, its fields in the
# order of the key's tuple; `bearer` (KEY_OPTIONAL) is omitted when absent. `key_json`, `decode_key` and the
# route's response schema (`readings_route`) all read this one table.
KEY_FIELDS = {
    "excepted": ("excepted", "bearer"),
    "off": ("off", "bearer", "party"),
    "outweighs": ("outweighs", "lower", "higher"),
    "lim": ("lim", "act"),
    "cond": ("cond", "act", "condition"),
    "aimed": ("aimed",),
}
KEY_OPTIONAL = frozenset({"bearer"})


def key_json(key):
    fields = dict(zip(KEY_FIELDS[key[0]], key[1:]))
    return {**{f: v for f, v in fields.items() if f not in KEY_OPTIONAL},
            **{f: v for f, v in fields.items() if f in KEY_OPTIONAL and v is not None}}


def decode_key(j):
    """A key as `decodeKey` reads it; a key that does not decode is a construction failure (Lean refuses its
    document) or, in a route's answer, an invalid answer."""
    if type(j) is not dict or any(type(v) is not str for v in j.values()):
        raise ValueError(f"undecodable key {j!r}")
    for kind, fields in KEY_FIELDS.items():
        required = {f for f in fields if f not in KEY_OPTIONAL}
        if required <= set(j) <= set(fields):
            return (kind, *(j.get(f) for f in fields))
    raise ValueError(f"undecodable key {j!r}")


def key_source(key):
    if key[0] in ("excepted", "off"):
        return ("rule", key[1])
    if key[0] in ("lim", "cond"):
        return ("limitation", key[1])
    return None


# ---------------------------------------------------------------------------------------------------------------
# The decoded document (1.1 to 1.5)

def content_bearing(R):
    """`Wire.contentBearing`: some candidate of the set has content other than an assertion (1.2)."""
    return any(a.content is not None and a.content.kind != "assertion" for a in R.candidates)


class Decoded:
    """The environment and the document, with the attachment of 1.3 and each candidate's side built on demand.
    Nothing is checked (Lean's `admitReadings` is the check)."""

    def __init__(self, environment, document):
        self.senv = S1Environment(environment)
        self.doc = Document(self.senv, document)
        self.attached = self.doc.attached()
        self.sides = {}
        self._rules_warm = self.senv.chain != "rights"

    def _warm_rules(self):
        """Every candidate side's line rules in one Lean request per source, not one per side
        (`RightsDocument.warm_rules`). A side that cannot be assembled is built, and raises, when it is read."""
        from .rights import RightsDocument
        documents = []
        for R in self.doc.sets:
            for k in range(len(R.candidates)):
                try:
                    documents.append(self._plain_side(R.id, k).rights_units())
                except CheckerUnavailable:
                    raise
                except Exception:  # noqa: BLE001
                    continue
        RightsDocument.warm_rules(self.senv.frame, documents)

    def _plain_side(self, s, i):
        return Side(self.senv, self.doc.one(self.attached, s, i), self.doc.unit_ids)

    def side(self, s, i):
        if (s, i) not in self.sides:
            if not self._rules_warm:
                self._rules_warm = True
                self._warm_rules()
            side = self._plain_side(s, i)
            side._elaborate()
            self.sides[(s, i)] = side
        return self.sides[(s, i)]

    def candidate(self, s, i):
        R = self.doc.set_by_id(s)
        return R.candidates[i] if R is not None and 0 <= i < len(R.candidates) else None

    def owned(self, s, i, key):
        a = self.candidate(s, i)
        source = key_source(key)
        return a is not None and a.content is not None and source is not None and source in a.content.declared()

    def owned_keys(self, s, i):
        return [k for k, _, _ in self.side(s, i).gen_keys() if self.owned(s, i, k)]

    content_bearing = staticmethod(content_bearing)

    def key_tuples(self, s, j, model, key):
        rows = []
        for k, _, sorts in self.side(s, j).gen_keys():
            if k == key:
                for row in product(*(model.domains.get(sort, ()) for sort in sorts)):
                    if row not in rows:
                        rows.append(row)
        return rows

    def cells(self, s, j, model):
        return sum(len(self.key_tuples(s, j, model, k)) for k in self.owned_keys(s, j))

    def assignments(self, s, j, model):
        keys = self.owned_keys(s, j)
        cells = [(k, row) for k in keys for row in self.key_tuples(s, j, model, k)]
        for bits in product((False, True), repeat=len(cells)):
            yield [(k, [row for (key, row), bit in zip(cells, bits) if key == k and bit]) for k in keys]

    # -- the search's evaluation of one side (`sideValid`, `sideValue`; rule 3, untrusted): the search builds
    # every table from the side's own keys over the base, so each is typed

    def side_valid(self, s, i, model, tables):
        side = self.side(s, i)
        return side.valid(side.model(model, tables))

    def side_value(self, s, i, model, tables, probe):
        side = self.side(s, i)
        return side.observe(side.model(model, tables), probe)


def _twin_nodes(strict, default):
    """`twinNodes` on decoded rules (`node_value`): strict and default, equal in every other field (mode,
    exception and hard apart)."""
    (s_core, s_mode, s_rank, s_alterable, _, _), (d_core, d_mode, d_rank, d_alterable, _, _) = strict, default
    return s_mode == "strict" and d_mode == "default" and (s_core, s_rank, s_alterable) == (d_core, d_rank, d_alterable)


def _twin_lines(line, other):
    """`twinLines` on decoded lines (`line_value`): equal but in their `norm`, which are twins; no fan-out."""
    if line[0] == "undecoded" or other[0] == "undecoded":
        return False
    kind, (norm, liberty, recognition), fan_out, slot, cites = line
    twin = other[1][0]
    return norm is not None and twin is not None and _twin_nodes(norm, twin) and not fan_out and \
        (kind, (twin, liberty, recognition), fan_out, slot, cites) == other


def _twin_line_lists(ls, others):
    """`twinLineLists`: the raw `norm` objects of the one twin position, strict first; lines compare decoded."""
    values, other_values = [line_value(x) for x in ls], [line_value(x) for x in others]
    k = 0
    while k < len(ls) and k < len(others) and values[k] == other_values[k]:
        k += 1
    if k == len(ls) or k == len(others) or not _twin_lines(values[k], other_values[k]):
        return None
    return (ls[k]["norm"], others[k]["norm"]) if values[k + 1:] == other_values[k + 1:] else None


def force_twins(c, other):
    """`forceTwins` (1.7): the raw strict and default rule of a pair of force twins, compared as Lean decodes
    them; None otherwise."""
    try:
        if c.kind == other.kind == "norm":
            return (c.body, other.body) if _twin_nodes(node_value(c.body), node_value(other.body)) else None
        if c.kind == other.kind == "right":
            if _right_header(c.body) != _right_header(other.body):
                return None
            return _twin_line_lists(c.lines(), other.lines())
        if c.kind == other.kind == "right_lines":
            return _twin_line_lists(c.lines(), other.lines()) if c.body["right"] == other.body["right"] else None
    except _UNDECODED:
        pass  # a content Lean does not decode: its document is refused before any finding
    return None


def content_acts(side, c):
    """`contentActs`: the act keys a content regulates, first occurrence kept."""
    sd = side.soft
    env = sd.env

    def line_preds(line):
        own = [line[k]["predicate"] for k in ("liberty", "recognition") if type(line.get(k)) is dict]
        if line.get("fan_out"):
            return [p for _, p in sorted(line["fan_out"].items())] + own
        norm = [line["norm"]["predicate"]] if type(line.get("norm")) is dict else []
        return norm + own

    if c.kind == "norm":
        preds = [c.body["predicate"]]
    elif c.kind in ("right", "right_lines"):
        preds = [p for line in c.lines() for p in line_preds(line)]
    else:
        preds = []
    acts = []
    for p in preds:
        act = _act_key(env, p)
        if act not in acts:
            acts.append(act)
    return acts


def _act_key(env, predicate):
    """`VE.SoftNorms.actKey`: an obligation's declared permission dual, else the predicate itself."""
    decl = env.predicates.get(predicate)
    reg = decl.regulated if decl is not None else None
    return reg.permission if reg is not None and reg.role == "obligation" and reg.permission else predicate


# ---------------------------------------------------------------------------------------------------------------
# The search for separating situations (10; not verified: Lean checks what it finds, 8.5)

MAX_SEARCH_BASES = 4096


def _bases(senv, max_size):
    """Candidate bases over the author's vocabulary, smallest first: every sort with the same number of
    elements, then every relation table, empty tables first."""
    author = senv.author_environment()
    sorts = sorted(author.model_sorts)
    constants = sorted(author.constants)
    predicates = sorted(p for p in author.predicates if p not in author.definition_entries)
    count = 0
    for size in range(1, max_size + 1):
        letters = [_element(s, 0, 1) for s in sorts]
        domains = {s: tuple(_element(s if letters.count(_element(s, 0, 1)) == 1 else s, k, size,
                                     whole=letters.count(_element(s, 0, 1)) > 1) for k in range(size))
                   for s in sorts}
        cells = [(p, row) for p in predicates
                 for row in product(*(domains[s] for s in author.predicates[p].arguments))]
        for chosen in _subsets_by_size(cells):
            relations = {p: [list(row) for q, row in chosen if q == p] for p in predicates}
            for consts in product(*(domains[author.constants[c].sort] for c in constants)):
                count += 1
                if count > MAX_SEARCH_BASES:
                    return
                yield {"domains": {s: list(v) for s, v in domains.items()},
                       "constants": dict(zip(constants, consts)), "relations": relations}


def _element(sort, k, size, whole=False):
    """An element name: the sort's first letter (`a` for an agent), or the sort's name when two sorts share it."""
    letter = sort if whole else ("".join(ch for ch in sort if ch.isalpha())[:1] or "e")
    return letter if size == 1 else f"{letter}{k + 1}"


def _subsets_by_size(cells):
    from itertools import combinations
    for n in range(len(cells) + 1):
        yield from combinations(cells, n)


def _probes(decoded, s, i, j, base):
    """Probes of 1.6 typed over the base, in the order of 2.3: `outcome`, `holds` between two assertions,
    `selects`, `holds` on a mixed pair."""
    regulated = decoded.senv.regulated
    outcomes = [("outcome", p, row) for p in sorted(regulated)
                for row in product(*(base.domains[a] for a in regulated[p].arguments))]
    selects = [(k, p, row) for p in sorted(regulated) for k in PROBE_KINDS
               for row in product(*(base.domains[a] for a in regulated[p].arguments))]
    assertions = all(decoded.candidate(s, x).content.kind == "assertion" for x in (i, j))
    return outcomes + (["holds"] if assertions else []) + selects + ([] if assertions else ["holds"])


def search(environment, document, set_id, *, max_size=2, hints=(), decoded=None):
    """For each ordered pair of candidates of the set, neither pending, a situation entry Python finds that
    separates them, or None. The witness is either reading of the pair; tables of shared keys stay empty.
    `hints` are bases tried first (a pilot's recorded situation, re-expressed)."""
    from .model import FiniteModel
    decoded = decoded or Decoded(environment, document)
    R = decoded.doc.set_by_id(set_id)
    found = {}
    author = decoded.senv.author_environment()
    bases = []
    for wire_base in [*hints, *_bases(decoded.senv, max_size)]:
        try:
            bases.append((wire_base, FiniteModel._decode(author, {**wire_base, "complete": True},
                                                         _defer_model_id=True)))
        except VEError:
            continue
    contents = [k for k, a in enumerate(R.candidates) if a.content is not None]
    for x in contents:
        for y in contents:
            if x == y or (x, y) in found:
                continue
            found[(x, y)] = found[(y, x)] = _search_pair(decoded, set_id, x, y, bases)
    return {(R.candidates[x].id, R.candidates[y].id): entry for (x, y), entry in found.items()}


def guard_base(decoded, s, i):
    """The base of a recorded force situation: one element of each sort, and every positive atom of the
    candidate's rule guards true at the tuple of its arguments (the pilots' "every guard atom of the rule true,
    every carve-out false")."""
    author = decoded.senv.author_environment()
    domains = {sort: [_element(sort, 0, 1, whole=[_element(o, 0, 1) for o in author.model_sorts].count(
        _element(sort, 0, 1)) > 1)] for sort in sorted(author.model_sorts)}
    relations = {p: [] for p in sorted(author.predicates) if p not in author.definition_entries}
    content = decoded.candidate(s, i).content
    for rule in content.rules():
        decl = decoded.senv.frame.predicates.get(rule.get("predicate") or "")
        if decl is None:
            continue
        sorts = list(decl.arguments)
        for atom in _positive_atoms(rule.get("guard", ["top"])):
            name, args = atom
            if name not in relations or any(type(a) is not list or a[0] != "var" or a[1] >= len(sorts)
                                            for a in args):
                continue
            row = [domains[sorts[len(sorts) - 1 - a[1]]][0] for a in args]
            if row not in relations[name]:
                relations[name].append(row)
    constants = {c: domains[author.constants[c].sort][0] for c in sorted(author.constants)
                 if author.constants[c].sort in domains}
    return {"domains": domains, "constants": constants, "relations": relations}


def _positive_atoms(formula):
    if type(formula) is not list or not formula:
        return []
    if formula[0] in ("unary", "binary"):
        return [(formula[1], formula[2:])]
    if formula[0] == "and":
        return _positive_atoms(formula[1]) + _positive_atoms(formula[2])
    return []


def _search_pair(decoded, s, x, y, bases):
    for wire_base, model in bases:
        for i, j in ((x, y), (y, x)):
            if decoded.cells(s, j, model) > MAX_CELLS or decoded.cells(s, i, model) > MAX_CELLS:
                continue
            for decisions in decoded.assignments(s, i, model):
                decisions = [(k, rows) for k, rows in decisions]
                if not decoded.side_valid(s, i, model, decisions):
                    continue
                for probe in _probes(decoded, s, i, j, model):
                    value = decoded.side_value(s, i, model, decisions, probe)
                    if value is None:
                        continue
                    if any(decoded.side_valid(s, j, model, G) and decoded.side_value(s, j, model, G, probe) == value
                           for G in decoded.assignments(s, j, model)):
                        continue
                    return _entry(decoded, s, i, wire_base, decisions, probe, value)
    return None


def _entry(decoded, s, i, wire_base, decisions, probe, value):
    if probe == "holds":
        probe_json = "holds"
    elif probe[0] == "outcome":
        probe_json = {"outcome": {"predicate": probe[1], "tuple": list(probe[2])}}
    else:
        probe_json = {"selects": {"kind": probe[0], "predicate": probe[1], "tuple": list(probe[2])}}
    order = {"excepted": 0, "off": 1, "outweighs": 2, "lim": 3, "cond": 4, "aimed": 5}
    tables = sorted(((k, rows) for k, rows in decisions if rows), key=lambda t: (order[t[0][0]], t[0][1:]))
    entry = {"base": wire_base, "fixed": [], "witness": decoded.candidate(s, i).id,
             "decisions": [{"key": key_json(k), "tuples": [list(r) for r in rows]} for k, rows in tables],
             "probe": probe_json, "value": value}
    return decoded.senv.situation_id(entry), entry


def record_situations(reading_set, found):
    """The set with the situations `search` found recorded (3): each reading names, for every other reading,
    the situation of their pair. A pair without one keeps no id, so the set is refused (4.5)."""
    situations = {}
    readings = []
    for reading in reading_set["readings"]:
        models = dict(reading["admission"]["distinguishing_models"])
        for other in reading_set["readings"]:
            hit = found.get((reading["id"], other["id"]))
            if hit is not None:
                sid, entry = hit
                situations[sid] = entry
                models[other["id"]] = sid
        readings.append({**reading, "admission": {**reading["admission"], "distinguishing_models": models}})
    return {**reading_set, "readings": readings, "situations": situations}
