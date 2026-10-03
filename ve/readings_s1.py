"""Python's regeneration of the S1 readings route (docs/spec/composition-s1.md 4.1 to 4.6, 8.4).

`answer` computes, from the environment and the document alone, what Lean's `readings-validate` answers: the
first diagnostic of 4.1 in its order, or per content-bearing set the candidates (each candidate's chain document
hash, its owned and shared source keys with their generated names, its chain findings), every pair with the
facts of its recorded situation, and the findings of 4.6. `ve/readings_route.py` compares the two answers byte
for byte (4.1 rule 3). Python is not the authority: Lean's answer decides admission, and Python's search for
situations (`search`) is checked by Lean before anything is recorded (8.5).

Python reuses its own chain classes (`RightsDocument`, `SoftNormDocument`), whose generated formulas the soft and
rights routes already compare with Lean's, and evaluates their premises, outcomes, selections and assertions on
each situation as Lean's `separates` does. One field is not computed independently: the per-candidate chain
findings of the rights chain (`limitationScope`, `noDistinction`) have no Python implementation; they are the
rights route's own answer (`rights-scope`) on the candidate's document, as in Python's rights report today.
Couplings, narrowings and W2's structural validation of the sets are Python's alone; Lean does not decode them
(S1 limitation, DRI ruling 3), and nothing here says Lean checked them.
"""
from __future__ import annotations

import json
from itertools import product

from .errors import VEError
from .wire import digest

READINGS = "readings@1"
RIGHTS_KINDS = ("right", "right_lines", "limitation", "bar", "norm")
MAX_CELLS = 12
PROBE_KINDS = ("claim", "liberty", "immunity", "powerLiberty", "powerRecognition", "norm")
SITUATION_FIELDS = ["base", "decisions", "fixed", "probe", "value", "witness"]


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

class S1Environment:
    """The environment with `readings@1`, its chain, and the lower and frame environments. The environment is read
    as Lean receives it (`wire`), as the document is: an explicit null is an absent field at every depth, so
    `vocabulary.soft: null` or a predicate's `regulated: null` is decoded as Lean decodes it."""

    def __init__(self, data):
        from .document import _environment
        data = wire(data)
        self.data = data
        profiles = data.get("profiles") if type(data) is dict else None
        if type(profiles) is not list or any(type(p) is not str for p in profiles):
            # Lean's `profilesOf`: an absent profiles field (or a null one, which `wire` omits) is refused first.
            raise VEError("UnsupportedProfile: profiles must be a sorted unique array")
        self.profiles = list(profiles)
        if READINGS not in self.profiles:
            raise VEError("UnsupportedProfile: readings@1 is required")
        self.lower_profiles = [p for p in self.profiles if p != READINGS]
        self.lower_data = {**data, "profiles": self.lower_profiles}
        self.chain = ("rights" if "rights@0" in self.profiles else
                      "soft" if "soft-norms@0" in self.profiles else "norms")
        frame = [p for p in self.lower_profiles if p != "norm-defaults@0"]
        self.frame_data = {**data, "profiles": frame}
        self.env = _environment(data)
        self.lower = _environment(self.lower_data)
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
        data["profiles"] = [p for p in data["profiles"] if p not in ("norms@0", "soft-norms@0", "rights@0")]
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

    def needs(self):
        return None if self.kind == "assertion" else "norms@0" if self.kind == "norm" else "rights@0"


def _line_rule_names(line):
    return [line[k]["name"] for k in ("norm", "liberty", "recognition") if type(line.get(k)) is dict]


def _cite_uses(cites):
    uses = []
    for key, _ in _sorted_items(cites):
        if key.startswith("over:"):
            uses.append(("rule", key[5:]))
        elif key.startswith("narrows:"):
            uses.append(("rule", key[8:]))
    return uses


def _line_uses(line):
    uses = [("rule", n) for k in ("norm", "liberty", "recognition") if type(line.get(k)) is dict
            for n in line[k].get("over", [])]
    return uses + _cite_uses(line.get("cites", {}))


# Decoded values. Lean compares contents as it decodes them (`SourceLine`, `SoftNode`, a right's header), not as
# written: an absent `cites`, `fan_out`, `mode`, `alterable` or `hard` is its default, and formulas are trees.
# Every comparison of contents goes through these values (the line order of 4.4, force twins of 1.7).

_UNDECODED = (VEError, TypeError, KeyError, AttributeError, ValueError, RecursionError)
_LINE_FIELDS = {"kind", "norm", "liberty", "recognition", "fan_out", "holder_slot", "cites"}


def node_value(raw, fan_pred=None):
    """A norm object as `ruleFields` decodes it (a `SoftNode`); raises when it does not decode. A fan-out line's
    absent predicate is its first mapped predicate (`decodeLineNorm`). The exception decider decides only whether
    the object decodes, never its value, so a stand-in is passed."""
    from .softnorms import _rule_fields
    if type(raw) is dict and fan_pred is not None and "predicate" not in raw:
        raw = {**raw, "predicate": fan_pred}
    f = _rule_fields({"norm": wire(raw)}, "unstated")
    exception = None
    if f.mode == "default":
        exception = (f.exception.get("decided_by"), f.conditions["sufficient"], f.conditions["necessary"],
                     tuple(f.exception["factors"]))
    return (f.core, f.mode, f.rank, f.alterable, exception, f.hard)


def line_value(line):
    """A line as `decodeLine` decodes it (a `SourceLine`): kind, rules, fan-out, holder slot, citations. A line
    Lean does not decode keeps its JSON: Lean refuses its document before comparing any line."""
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
    from .ast import Top
    from .softnorms import _fol
    guard = wire(body).get("guard")
    return (body.get("name"), body.get("holder"), Top() if guard is None else _fol(guard))


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
    right's line with `cites: null` or a norm with `mode: null` is decoded with its defaults, as Lean decodes it."""

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
            if unit.get("content") is not None and kind is None:
                raise VEError("InvalidInput: unit kind is required")
            reading_set = next((r for r in active if r["unit"] == uid), None)
            if reading_set is not None:
                if reading_set["status"] == "open":
                    self.items.append(("set", uid, ReadingSet(reading_set, [
                        self._candidate(reading_set["id"], r) for r in reading_set["readings"]])))
                    continue
                if len(reading_set["readings"]) != 1:
                    raise VEError("authored reading needs one signed choice")
                kind = reading_set["readings"][0]["kind"]
                content = reading_set["readings"][0].get("content")
            else:
                content = unit.get("content")
            decoded = decode_content(content)
            if isinstance(decoded, Content) and in_force(kind, decoded):
                self.items.append(("fixed", uid, decoded))
            elif type(decoded) is tuple and type(kind) is str and kind in RIGHTS_KINDS:
                self.items.append(("bar", uid, content["bar"]))

    def _candidate(self, set_id, reading):
        decoded = decode_content(reading.get("content"))
        labels = reading.get("labels") or {}
        kind = reading["kind"]
        if decoded is None:
            return Candidate(reading["id"], None, labels)
        if type(decoded) is tuple:
            raise VEError("UnsupportedProfile: readings@1 bar candidate content is not implemented")
        if decoded.kind == "assertion":
            return Candidate(reading["id"], decoded if kind == "asserted" else None, labels)
        if kind != decoded.kind:
            shown = kind if type(kind) is str else "composite"
            raise VEError(f"InvalidInput: reading {set_id}:{reading['id']} has kind {shown} "
                          f"and content of kind {decoded.kind}")
        if self.senv.chain == "norms" and decoded.kind == "norm":
            # On the norms chain a norm is W1's: a soft field is the W1 decoder's error.
            from .norms import NormDocument
            NormDocument._decode({"norm": decoded.body})
        return Candidate(reading["id"], decoded, labels)

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

    def free(self, attached):
        return self.build(lambda u: not attached.get(u), lambda R: None)

    def one(self, attached, s, i):
        return self.build(lambda u: all(t == s for t in attached.get(u, ())),
                          lambda R: R.candidates[i] if R.id == s and i < len(R.candidates) else None)


# ---------------------------------------------------------------------------------------------------------------
# One chain document (`one D s i`, `free D`) with its elaboration, keys and evaluation

class Side:
    """A chain document assembled from contents in source order (`place`), checked and elaborated."""

    def __init__(self, senv, contents, unit_ids):
        self.senv, self.contents, self.unit_ids = senv, contents, unit_ids
        self.assertions = [c.body for c in contents if isinstance(c, Content) and c.kind == "assertion"]
        self.rights = None
        self.soft = None

    # -- the line order (DRI ruling 1, 4.4)

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
            self._elaborate()
        except VEError as exc:
            return exc.message if hasattr(exc, "message") else str(exc)
        return None

    def _elaborate(self):
        chain = self.senv.chain
        if chain == "rights":
            text = self.line_order_text()
            if text is not None:
                raise VEError(text)
            from .rights import RightsDocument
            units = [{"source_units": list(self.unit_ids)}]
            for c in self.contents:
                if not isinstance(c, Content):
                    units.append(lean_defaults({"bar": c[1]}))
                elif c.kind != "assertion":
                    units.append(lean_defaults(c.raw))
            self.rights = RightsDocument(self.senv.frame, units)
            self.soft = self.rights.soft_document
        else:
            if self.has_rights():
                raise VEError("UnsupportedProfile: rights content requires rights@0")
            norms = [c.raw for c in self.contents if c.kind == "norm"]
            if chain == "norms" and any(
                    c.body.get("mode", "strict") != "strict" or c.body.get("alterable") for c in self.contents
                    if c.kind == "norm"):
                raise VEError("InvalidInput: invalid norm fields")
            from .softnorms import SoftNormDocument, check_soft_source
            env = self.senv.soft_frame()
            check_soft_source(env.to_dict(), norms)
            self.soft = SoftNormDocument(env, norms)
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
                pair = sd._rank_pair(left, right)
                if pair is None:
                    continue
                generated = sd._outweighs_name(*pair, sd._act(left), env.predicates[left.core.predicate].arguments)
                act = generated[len(f"soft__outweighs__{pair[0]}__{pair[1]}__"):]
                key = ("outweighs", act, pair[0], pair[1])
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

    def key_sorts(self, key):
        return next((sorts for k, _, sorts in self.gen_keys() if k == key), None)

    def generates(self, key):
        return any(k == key for k, _, _ in self.gen_keys())

    # -- evaluation over a finite base with tables (`tablesModel`, `backgroundValidR`, `observe`)

    def model(self, base, tables):
        """The base model with every generated predicate read from its key's table (`tablesModel`)."""
        relations = {p: set(rows) for p, rows in base.relations.items()}
        for key, name, _ in self.gen_keys():
            relations[name] = set(next((t for k, t in tables if k == key), ()))
        return _Model(base.domains, base.constants, relations)

    def tables_typed(self, base, tables):
        for key, rows in tables:
            if not self.generates(key):
                return False
            for row in rows:
                for k, name, sorts in self.gen_keys():
                    if k == key and not _typed(base, sorts, row):
                        return False
        return True

    def probe_typed(self, base, probe):
        if probe == "holds":
            return True
        kind, predicate, row = probe
        regulated = self.senv.regulated
        if kind not in ("outcome", *PROBE_KINDS) or predicate not in regulated:
            return False
        return _typed(base, list(regulated[predicate].arguments), row)

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

    def evaluation_case(self, base, tables, probe):
        """The side of Rust's untrusted `readings-evaluate` case: the base environment with a constant per
        entity, the model, and the closed premises, probe formulas and assertions (10)."""
        from .ast import And, Const, Not, _to_data
        from .norms import _instantiate
        env, premises, assertions = self._formulas()
        model = self.model(base, tables)
        data = env.to_dict()
        data["vocabulary"].pop("soft", None)
        names = {}
        for sort, values in sorted(model.domains.items()):
            for value in values:
                names[(sort, value)] = f"s1_{len(names)}"
                data["vocabulary"]["constants"][names[(sort, value)]] = {
                    "sort": sort, "description": f"the entity {value} of the situation"}
        outcomes, selections = [], []
        if probe != "holds":
            kind, predicate, row = probe
            sorts = list(self.senv.regulated[predicate].arguments)
            terms = tuple(Const(names[(s, v)]) for s, v in zip(sorts, row))
            tree = self.soft.elaborated
            if kind == "outcome":
                positive, negative, _ = tree.selection(predicate)
                conflict = And(tree._expand(positive, predicate), tree._expand(negative, predicate))
                outcomes = [_instantiate(Not(conflict), terms),
                            _instantiate(tree.outcome(predicate, base=True), terms)]
            else:
                _, _, selected = tree.selection(predicate)
                selections = [_instantiate(tree._expand(selected[rule.core.name], None), terms)
                              for rule in self.selectable(kind, predicate)]
        wire_model = {"complete": True, "domains": {s: sorted(v) for s, v in model.domains.items()},
                      "constants": {**dict(model.constants), **{n: v for (s, v), n in names.items()}},
                      "relations": {p: sorted(map(list, rows)) for p, rows in model.relations.items()}}
        return {"environment": data, "model": wire_model,
                "premises": [_to_data(f) for f in premises], "outcomes": [_to_data(f) for f in outcomes],
                "selections": [_to_data(f) for f in selections],
                "assertions": [_to_data(f) for f in assertions]}


class _Model:
    def __init__(self, domains, constants, relations):
        self.domains, self.constants = domains, constants
        self.relations = {p: frozenset(map(tuple, rows)) for p, rows in relations.items()}


def _typed(base, sorts, row):
    return len(sorts) == len(row) and all(v in base.domains.get(s, ()) for s, v in zip(sorts, row))


def _canonical_raw(raw):
    if type(raw) is not dict:
        return raw
    return {k: v for k, v in raw.items()
            if not ((k, v) == ("mode", "strict") or (k, v) == ("alterable", []) or (k, v) == ("hard", False))}


def _canonical_unit(u):
    if "norm" in u:
        return {**u, "norm": _canonical_raw(u["norm"])}
    for key in ("right", "right_lines"):
        if key in u:
            body = u[key]
            if type(body) is dict and type(body.get("lines")) is list:
                body = {**body, "lines": [{**line, **{k: _canonical_raw(line[k]) for k in
                                                      ("norm", "liberty", "recognition") if k in line}}
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

def key_json(key):
    kind = key[0]
    if kind == "excepted":
        return {"excepted": key[1], **({"bearer": key[2]} if key[2] is not None else {})}
    if kind == "off":
        return {"off": key[1], "party": key[3], **({"bearer": key[2]} if key[2] is not None else {})}
    if kind == "outweighs":
        return {"outweighs": key[1], "lower": key[2], "higher": key[3]}
    if kind == "lim":
        return {"lim": key[1], "act": key[2]}
    if kind == "cond":
        return {"cond": key[1], "act": key[2], "condition": key[3]}
    return {"aimed": key[1]}


def key_text(key):
    kind = key[0]
    if kind == "excepted":
        return f"excepted {key[1]}" + (f" bearer {key[2]}" if key[2] is not None else "")
    if kind == "off":
        return f"off {key[1]}" + (f" bearer {key[2]}" if key[2] is not None else "") + f" {key[3]}"
    return " ".join([kind, *key[1:]])


def decode_key(j, bad):
    if type(j) is not dict:
        raise VEError(bad)
    keys = sorted(j)
    if any(type(v) is not str for v in j.values()):
        raise VEError(bad)
    if keys in (["excepted"], ["bearer", "excepted"]):
        return ("excepted", j["excepted"], j.get("bearer"))
    if keys in (["off", "party"], ["bearer", "off", "party"]):
        return ("off", j["off"], j.get("bearer"), j["party"])
    if keys == ["higher", "lower", "outweighs"]:
        return ("outweighs", j["outweighs"], j["lower"], j["higher"])
    if keys == ["act", "lim"]:
        return ("lim", j["lim"], j["act"])
    if keys == ["act", "cond", "condition"]:
        return ("cond", j["cond"], j["act"], j["condition"])
    if keys == ["aimed"]:
        return ("aimed", j["aimed"])
    raise VEError(bad)


def key_source(key):
    if key[0] in ("excepted", "off"):
        return ("rule", key[1])
    if key[0] in ("lim", "cond"):
        return ("limitation", key[1])
    return None


# ---------------------------------------------------------------------------------------------------------------
# Admission (4.1 to 4.4)

class Admission:
    """The decoded document after the checks of 4.1 up to each candidate's well-formedness."""

    def __init__(self, environment, document):
        self.senv = S1Environment(environment)
        self.doc = Document(self.senv, document)
        self.attached = self.doc.attached()
        self.sides = {}
        text = self._admission_text()
        if text is not None:
            raise VEError(text)

    def side(self, s, i):
        if (s, i) not in self.sides:
            side = Side(self.senv, self.doc.one(self.attached, s, i), self.doc.unit_ids)
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

    @staticmethod
    def content_bearing(R):
        return any(a.content is not None and a.content.kind != "assertion" for a in R.candidates)

    def _admission_text(self):
        senv, doc = self.senv, self.doc
        for text in (self._abstention(), self._reserved(), self._duplicate(), self._interface(),
                     self._attachment()):
            if text is not None:
                return text
        text = Side(senv, doc.free(self.attached), doc.unit_ids).chain_text()
        if text is not None:
            return text
        for R in doc.sets:
            for i, a in enumerate(R.candidates):
                if a.content is None:
                    continue
                side = Side(senv, doc.one(self.attached, R.id, i), doc.unit_ids)
                text = side.chain_text()
                if text is not None:
                    return text + f" under {R.id}@{R.version}:{i}"
                self.sides[(R.id, i)] = side
        return None

    def _abstention(self):
        lower = self.senv.lower_profiles
        if "norm-defaults@0" in lower and any(self.content_bearing(R) for R in self.doc.sets):
            return "UnsupportedProfile: readings@1 content with norm-defaults@0 is not implemented"
        for R in self.doc.sets:
            for a in R.candidates:
                need = a.content.needs() if a.content is not None else None
                if need is not None and need not in lower:
                    return f"UnsupportedProfile: reading {R.id}:{a.id} of kind {a.content.kind} requires {need}"
        return None

    def _reserved(self):
        vocabulary = self.senv.data["vocabulary"]
        symbols = (sorted(vocabulary.get("sorts", {})) + sorted(vocabulary.get("predicates", {})) +
                   sorted(vocabulary.get("constants", {})))
        for name in symbols:
            if name.startswith("ve__"):
                return f"InvalidInput: name {name} begins with ve__"
        for item in self.doc.items:
            contents = ([item[2]] if item[0] == "fixed" else
                        [a.content for a in item[2].candidates if a.content is not None] if item[0] == "set" else [])
            for c in contents:
                for _, name in c.declared():
                    if name.startswith("rd-"):
                        return f"InvalidInput: name {name} begins with rd-"
        return None

    def _item_names(self, item):
        if item[0] == "fixed":
            return [n for _, n in item[2].declared()]
        if item[0] == "bar":
            return [item[2].get("name")]
        return []

    def _duplicate(self):
        doc = self.doc
        fixed_names = [n for item in doc.items for n in self._item_names(item)]
        sets = doc.sets
        for k, R in enumerate(sets):
            for _, name in doc.declared_by(R):
                if name in fixed_names:
                    return f"DuplicateDeclaration: {name} in reading sets {R.id} and the document"
                for other in sets[k + 1:]:
                    if other.id != R.id and any(m == name for _, m in doc.declared_by(other)):
                        return f"DuplicateDeclaration: {name} in reading sets {R.id} and {other.id}"
        earlier = []
        for item in doc.items:
            for name in self._item_names(item):
                if name in earlier:
                    return self._fixed_duplicate_text(name)
            earlier.extend(self._item_names(item))
        return None

    def _fixed_duplicate_text(self, name):
        declared = [n for item in self.doc.items if item[0] == "fixed" for n in item[2].declared()]
        declared += [("bar", item[2].get("name")) for item in self.doc.items if item[0] == "bar"]
        if self.senv.chain == "rights":
            if ("right", name) in declared:
                return f"DuplicateDeclaration: right {name}"
            if ("limitation", name) in declared:
                return f"DuplicateDeclaration: limitation {name}"
            if ("bar", name) in declared:
                return "DuplicateDeclaration: bar"
        return f"DuplicateDeclaration: rule {name}"

    def _interface(self):
        doc = self.doc
        for R in doc.sets:
            declared, interface = doc.declared_by(R), doc.interface_of(R)
            for u, c in doc.fixed_units():
                for n in c.uses():
                    if n in declared and n not in interface:
                        return f"ReadingInterface: {R.id}: {n[1]}"
        return None

    def _attachment(self):
        ids = [R.id for R in self.doc.sets]
        for u, _ in self.doc.fixed_units():
            hit = [s for s in ids if s in self.attached.get(u, ())]
            if len(hit) >= 2:
                return f"UnsupportedProfile: readings@1 fixed unit {u} depends on reading sets {hit[0]} and {hit[1]}"
        return None

    # -- situations (4.5)

    def decode_situation(self, s, i, j, sid, entry):
        """`decodeSituation`, `stepOne` and the base's validity: the situation, or 4.5 step 1's diagnostic."""
        bad = f"InvalidInput: invalid situation {sid}"
        if type(entry) is not dict or sorted(entry) != SITUATION_FIELDS:
            raise VEError(bad)
        if self.senv.situation_id(entry) != sid:
            raise VEError("distinguishing model id does not match model")
        if type(entry["witness"]) is not str:
            raise VEError(bad)
        base = entry["base"]
        if type(base) is not dict:
            raise VEError(bad)
        base = base if "complete" in base else {**base, "complete": True}
        base = {**base, "complete": True}
        from .model import FiniteModel
        try:
            model = FiniteModel._decode(self.senv.author_environment(), base, _defer_model_id=True)
        except VEError:
            raise VEError(bad) from None
        for sort, values in sorted(model.domains.items()):
            for value in values:
                if value.startswith("rd-"):
                    raise VEError(f"InvalidInput: name {value} begins with rd-")
                if "__" in value:
                    raise VEError(bad)
        Xi, Xj = self.side(s, i), self.side(s, j)

        def tables(raw):
            if raw is None:
                return []
            if type(raw) is not list:
                raise VEError(bad)
            out = []
            for item in raw:
                if type(item) is not dict or sorted(item) != ["key", "tuples"]:
                    raise VEError(bad)
                key = decode_key(item["key"], bad)
                sorts = Xi.key_sorts(key) or Xj.key_sorts(key)
                if sorts is None or type(item["tuples"]) is not list:
                    raise VEError(bad)
                rows = []
                for row in item["tuples"]:
                    if type(row) is not list or len(row) != len(sorts) or any(type(v) is not str for v in row):
                        raise VEError(bad)
                    rows.append(tuple(row))
                out.append((key, rows))
            return out

        fixed, decisions = tables(entry["fixed"]), tables(entry["decisions"])
        probe = self._probe(entry["probe"], bad)
        if type(entry["value"]) is not bool:
            raise VEError(bad)
        witness = entry["witness"]
        for key, _ in decisions:
            if not self.owned(s, i, key):
                raise VEError(f"InvalidInput: situation {sid} decides {key_text(key)}, which reading {witness} "
                              "does not own")
        for key, _ in fixed:
            if self.owned(s, i, key) or self.owned(s, j, key):
                raise VEError(f"InvalidInput: situation {sid} decides {key_text(key)}, which reading {witness} "
                              "does not own")
        situation = (model, fixed, decisions, probe, entry["value"])
        if not self.situation_wf(s, i, j, situation):
            raise VEError(bad)
        return situation

    def _probe(self, raw, bad):
        if raw == "holds":
            return "holds"
        if type(raw) is not dict or ("outcome" in raw) == ("selects" in raw):
            raise VEError(bad)
        body = raw.get("outcome") if "outcome" in raw else raw.get("selects")
        if type(body) is not dict or type(body.get("predicate")) is not str:
            raise VEError(bad)
        kind = "outcome" if "outcome" in raw else body.get("kind")
        if type(kind) is not str:
            raise VEError(bad)
        predicate = body["predicate"]
        decl = self.senv.regulated.get(predicate)
        sorts = list(decl.arguments) if decl is not None else []
        row = body.get("tuple")
        if type(row) is not list or len(row) != len(sorts) or any(type(v) is not str for v in row):
            raise VEError(bad)
        return (kind, predicate, tuple(row))

    def tables_for(self, s, i, tables):
        side = self.side(s, i)
        return [(k, rows) for k, rows in tables if side.generates(k)]

    def situation_wf(self, s, i, j, situation):
        model, fixed, decisions, probe, _ = situation
        keys = [k for k, _ in fixed + decisions]
        Xi, Xj = self.side(s, i), self.side(s, j)
        return (len(set(keys)) == len(keys)
                and all(not self.owned(s, i, k) and not self.owned(s, j, k) and (Xi.generates(k) or Xj.generates(k))
                        for k, _ in fixed)
                and all(self.owned(s, i, k) and Xi.generates(k) for k, _ in decisions)
                and Xi.tables_typed(model, self.tables_for(s, i, fixed + decisions))
                and Xj.tables_typed(model, self.tables_for(s, j, fixed))
                and Xi.probe_typed(model, probe))

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

    def side_valid(self, s, i, model, tables):
        side = self.side(s, i)
        return side.tables_typed(model, tables) and side.valid(side.model(model, tables))

    def side_value(self, s, i, model, tables, probe):
        side = self.side(s, i)
        return side.observe(side.model(model, tables), probe)

    def pair_facts(self, s, sid, other_name, *, rust=None):
        """`pairFacts`: the replay of one recorded situation, as `readings-separate` answers it."""
        R = self.doc.set_by_id(s)
        if R is None:
            raise VEError(f"InvalidInput: unknown reading set {s}")
        entry = R.situations.get(sid) if type(R.situations) is dict else None
        if entry is None:
            raise VEError("distinguishing model id does not match model")
        bad = f"InvalidInput: invalid situation {sid}"
        witness = entry.get("witness") if type(entry) is dict else None
        if type(witness) is not str:
            raise VEError(bad)
        ids = [a.id for a in R.candidates]
        if witness not in ids or other_name not in ids:
            raise VEError(bad)
        i, j = ids.index(witness), ids.index(other_name)
        if i == j:
            raise VEError(bad)
        situation = self.decode_situation(s, i, j, sid, entry)
        model, fixed, decisions, probe, value = situation
        Ti = self.tables_for(s, i, fixed + decisions)
        if self.cells(s, j, model) > MAX_CELLS:
            raise VEError("ResourceLimit: decision assignments")
        Tj = self.tables_for(s, j, fixed)
        witness_valid = self.side_valid(s, i, model, Ti)
        witness_value = self.side_value(s, i, model, Ti, probe)
        other_admissible = False
        reached = False
        for G in self.assignments(s, j, model):
            if self.side_valid(s, j, model, Tj + G):
                other_admissible = True
                if self.side_value(s, j, model, Tj + G, probe) == value:
                    reached = True
                    break
        separated = witness_valid and witness_value == value and not reached
        facts = {"situation": sid, "witness": witness, "separated": separated,
                 "witness_admissible": witness_valid, "witness_value": witness_value,
                 "other_admissible": other_admissible}
        if not self.owned_keys(s, j):
            facts["other_value"] = self.side_value(s, j, model, Tj, probe)
        if rust is not None:
            rust(self, s, i, j, situation, Ti, Tj, facts)
        return facts

    # -- findings (4.6, 1.7)

    def decision_only(self, s, i, j):
        ci, cj = self.candidate(s, i).content, self.candidate(s, j).content
        if ci is None or cj is None:
            return None
        twins = force_twins(ci, cj)
        if twins is None:
            return None
        _, default = twins
        side = self.side(s, j)
        sd = side.soft
        if (default.get("exception") or {}).get("sufficient"):
            return None
        rules = list(sd.rules)
        if not any(r.core.name == default["name"] and r.core.predicate == default["predicate"] for r in rules):
            return None
        act = _act_key(sd.env, default["predicate"])
        if any(_act_key(sd.env, r.core.predicate) == act and r.core.name != default["name"] for r in rules):
            return None
        return ("excepted", default["name"], None)

    def act_only(self, s, i, j):
        ci, cj = self.candidate(s, i).content, self.candidate(s, j).content
        if ci is None or cj is None:
            return None
        a, b = content_acts(self.side(s, i), ci), content_acts(self.side(s, j), cj)
        if len(a) == 1 and len(b) == 1 and a[0] != b[0]:
            return (a[0], b[0])
        return None

    def set_findings(self, R):
        n = len(R.candidates)
        findings = []
        for i in range(n):
            for j in range(i + 1, n):
                if self.decision_only(R.id, i, j) is not None:
                    findings.append(decision_only_text(R.id, i, j))
                elif self.decision_only(R.id, j, i) is not None:
                    findings.append(decision_only_text(R.id, j, i))
                if self.act_only(R.id, i, j) is not None:
                    findings.append(f"SeparatedByActOnly: {R.id}: {i}, {j}")
        return findings


def decision_only_text(s, i, j):
    """DRI ruling 2: the finding's theorem is unproved, so its text says it is not certified."""
    return f"SeparatedByDecisionOnly: {s}: {i}, {j} (not certified)"


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
# The answer of `readings-validate` (8.4)

def answer(environment, document, *, chain_findings=None, rust=None):
    """Python's `readings-validate` answer, as Lean's `validateResult` builds it, or the first diagnostic of 4.1
    raised as `VEError`. `chain_findings(units, label)` supplies the rights chain's findings of one candidate's
    document (none on the other chains); `rust` checks each pair's evaluations against Rust's (10)."""
    admission = Admission(environment, document)
    sets = [R for R in admission.doc.sets if Admission.content_bearing(R)]
    if not sets:
        return {"content_bearing": False}
    rows = []
    for R in sets:
        candidates = []
        for i, a in enumerate(R.candidates):
            if a.content is None:
                candidates.append({"id": a.id, "index": i, "pending": True})
                continue
            side = admission.side(R.id, i)
            keys = []
            for key, name, _ in side.gen_keys():
                if key not in [k for k, _ in keys]:
                    keys.append((key, name))
            label = f" under {R.id}@{R.version}:{i}"
            findings = ([text + label for text in chain_findings(side, label)]
                        if chain_findings is not None and admission.senv.chain == "rights" else [])
            candidates.append({
                "id": a.id, "index": i, "pending": False, "document_hash": side.document_hash(),
                "owned": [{"key": key_json(k), "name": n} for k, n in keys if admission.owned(R.id, i, k)],
                "shared": [{"key": key_json(k), "name": n} for k, n in keys if not admission.owned(R.id, i, k)],
                "findings": findings})
        pairs = []
        for x in R.candidates:
            for y in R.candidates:
                if x is y or x.content is None or y.content is None:
                    continue
                reading = next(r for r in R.raw["readings"] if r["id"] == x.id)
                models = reading["admission"]["distinguishing_models"]
                sid = models.get(y.id)
                if sid is None:
                    raise VEError("each other reading needs a distinguishing model id")
                entry = R.situations.get(sid)
                if entry is None:
                    raise VEError("distinguishing model id does not match model")
                witness = entry.get("witness") if type(entry) is dict else None
                if witness not in (x.id, y.id):
                    raise VEError(f"InvalidInput: invalid situation {sid}")
                other = y.id if witness == x.id else x.id
                facts = admission.pair_facts(R.id, sid, other, rust=rust)
                if not facts["witness_admissible"]:
                    raise VEError("distinguishing model violates a generated premise")
                if not facts["separated"]:
                    raise VEError("distinguishing model does not separate readings")
                pairs.append({"reading": x.id, "other": y.id, "pair": facts})
        rows.append({"set": R.id, "version": R.version, "candidates": candidates, "pairs": pairs,
                     "findings": admission.set_findings(R)})
    return {"content_bearing": True, "sets": rows}


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


def _probes(admission, s, i, j, base):
    """Probes of 1.6 typed over the base, in the order of 2.3: `outcome`, `holds` between two assertions,
    `selects`, `holds` on a mixed pair."""
    regulated = admission.senv.regulated
    outcomes = [("outcome", p, row) for p in sorted(regulated)
                for row in product(*(base.domains[a] for a in regulated[p].arguments))]
    selects = [(k, p, row) for p in sorted(regulated) for k in PROBE_KINDS
               for row in product(*(base.domains[a] for a in regulated[p].arguments))]
    assertions = all(admission.candidate(s, x).content.kind == "assertion" for x in (i, j))
    return outcomes + (["holds"] if assertions else []) + selects + ([] if assertions else ["holds"])


def search(environment, document, set_id, *, max_size=2, hints=(), admission=None):
    """For each ordered pair of candidates of the set, neither pending, a situation entry Python finds that
    separates them, or None. The witness is either reading of the pair; tables of shared keys stay empty.
    `hints` are bases tried first (a pilot's recorded situation, re-expressed)."""
    from .model import FiniteModel
    admission = admission or Admission(environment, document)
    R = admission.doc.set_by_id(set_id)
    found = {}
    author = admission.senv.author_environment()
    bases = []
    for wire_base in [*hints, *_bases(admission.senv, max_size)]:
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
            found[(x, y)] = found[(y, x)] = _search_pair(admission, set_id, x, y, bases)
    return {(R.candidates[x].id, R.candidates[y].id): entry for (x, y), entry in found.items()}


def guard_base(admission, s, i):
    """The base of a recorded force situation: one element of each sort, and every positive atom of the
    candidate's rule guards true at the tuple of its arguments (the pilots' "every guard atom of the rule true,
    every carve-out false")."""
    author = admission.senv.author_environment()
    domains = {sort: [_element(sort, 0, 1, whole=[_element(o, 0, 1) for o in author.model_sorts].count(
        _element(sort, 0, 1)) > 1)] for sort in sorted(author.model_sorts)}
    relations = {p: [] for p in sorted(author.predicates) if p not in author.definition_entries}
    content = admission.candidate(s, i).content
    rules = ([content.body] if content.kind == "norm" else
             [line[k] for line in content.lines() for k in ("norm", "liberty", "recognition")
              if type(line.get(k)) is dict])
    for rule in rules:
        decl = admission.senv.frame.predicates.get(rule.get("predicate") or "")
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


def _search_pair(admission, s, x, y, bases):
    for wire_base, model in bases:
        for i, j in ((x, y), (y, x)):
            if admission.cells(s, j, model) > MAX_CELLS or admission.cells(s, i, model) > MAX_CELLS:
                continue
            for decisions in admission.assignments(s, i, model):
                decisions = [(k, rows) for k, rows in decisions]
                if not admission.side_valid(s, i, model, decisions):
                    continue
                for probe in _probes(admission, s, i, j, model):
                    value = admission.side_value(s, i, model, decisions, probe)
                    if value is None:
                        continue
                    if any(admission.side_valid(s, j, model, G) and admission.side_value(s, j, model, G, probe) == value
                           for G in admission.assignments(s, j, model)):
                        continue
                    return _entry(admission, s, i, wire_base, decisions, probe, value)
    return None


def _entry(admission, s, i, wire_base, decisions, probe, value):
    if probe == "holds":
        probe_json = "holds"
    elif probe[0] == "outcome":
        probe_json = {"outcome": {"predicate": probe[1], "tuple": list(probe[2])}}
    else:
        probe_json = {"selects": {"kind": probe[0], "predicate": probe[1], "tuple": list(probe[2])}}
    order = {"excepted": 0, "off": 1, "outweighs": 2, "lim": 3, "cond": 4, "aimed": 5}
    tables = sorted(((k, rows) for k, rows in decisions if rows), key=lambda t: (order[t[0][0]], t[0][1:]))
    entry = {"base": wire_base, "fixed": [], "witness": admission.candidate(s, i).id,
             "decisions": [{"key": key_json(k), "tuples": [list(r) for r in rows]} for k, rows in tables],
             "probe": probe_json, "value": value}
    return admission.senv.situation_id(entry), entry


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
