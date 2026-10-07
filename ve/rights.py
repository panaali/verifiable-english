"""Rights environment and Python views of Lean's rights elaboration."""
from __future__ import annotations

from copy import deepcopy
import re

from .errors import DuplicateDeclaration, UnknownSymbol, UnsupportedProfile, VEError
from .environment import validate_authored_source
from .softnorms import SoftEnvironment, SoftNormDocument

_RULE = re.compile(r"[a-z][a-z0-9-]*\Z", re.ASCII)
# Every line kind with its rule-bearing fields, in the order the line states its rules: a power line states a
# liberty and a recognition rule, every other kind one norm. Whatever names or owns a line's rules reads this table
# (compose-s2 fix4 A2), so a new kind cannot be added without saying which fields carry its rules.
LINE_RULE_FIELDS = {"claim": ("norm",), "liberty": ("norm",), "immunity": ("norm",), "power": ("liberty", "recognition")}
RULE_FIELDS = tuple(dict.fromkeys(field for fields in LINE_RULE_FIELDS.values() for field in fields))
_KINDS = frozenset(LINE_RULE_FIELDS)


def _name(value):
    if type(value) is not str or len(value) > 64 or not _RULE.fullmatch(value):
        raise VEError(f"InvalidInput: invalid rights name {value!r}")
    if value.startswith("rights-"):
        raise VEError(f"InvalidInput: name {value} begins with rights-")
    return value


def _strings(value):
    return type(value) is list and all(type(item) is str for item in value)


def _decode_block(rights):
    """The types `decodeRightsBlock` reads before the soft environment is
    decoded: `holders`, `bearers` and `protected` arrays of strings, `alters` an
    object whose entries have their fields, a natural `holder_slot` and a string
    `status` and `recognition`."""
    if (not all(_strings(rights.get(key, [])) for key in ("holders", "bearers", "protected"))
            or type(rights.get("alters", {})) is not dict):
        raise VEError("InvalidInput: invalid rights block")
    for act, entry in rights.get("alters", {}).items():
        if (type(entry) is not dict or not {"holder_slot", "status"} <= set(entry)
                or set(entry) - {"holder_slot", "status", "recognition"}
                or type(entry["holder_slot"]) is not int or entry["holder_slot"] < 0
                or type(entry["status"]) is not str or type(entry.get("recognition", "")) is not str):
            raise VEError(f"InvalidInput: alters {act}")


def _duplicate(values, kind):
    seen = set()
    for value in values:
        if value in seen:
            raise DuplicateDeclaration(f"{kind} {value}")
        seen.add(value)


class RightsEnvironment(SoftEnvironment):
    """Validate and bind the rights block without changing older identities."""

    LAYERS = frozenset({"rights@0"})

    def __init__(self, data):
        validate_authored_source(data)
        profiles = data.get("profiles") if type(data) is dict else None
        if type(profiles) is not list or any(type(p) is not str for p in profiles):
            # VE.Rights.Wire.decodeRightsEnvironment reads the profiles first.
            raise UnsupportedProfile("profiles must be a sorted unique array")
        if "rights@0" not in profiles:
            raise UnsupportedProfile("rights@0 is required")
        if "soft-norms@0" not in profiles:
            raise UnsupportedProfile("rights@0 requires soft-norms@0")
        raw = deepcopy(data)
        vocabulary = raw.get("vocabulary", {})
        rights = vocabulary.pop("rights", None) if type(vocabulary) is dict else None
        # As Lean's `decodeRightsBlock` reads the block: `holders` and `bearers` are required, `protected` and
        # `alters` optional (an absent one is empty). The block is kept as written, so its identity is Lean's.
        if (type(rights) is not dict or not {"holders", "bearers"} <= set(rights)
                or not set(rights) <= {"holders", "bearers", "protected", "alters"}):
            raise VEError("InvalidInput: invalid rights block")
        for entry in (rights["alters"].values() if type(rights.get("alters")) is dict else ()):
            if type(entry) is dict and "recognition" in entry and entry["recognition"] is None:
                # 3.1's null recognition is the absent key: canonical JSON has no null,
                # and the Lean wire sends the field absent.
                del entry["recognition"]
        _decode_block(rights)
        predicates = vocabulary.get("predicates")
        for predicate in (predicates if type(predicates) is dict else ()):
            if predicate.startswith("rights__"):
                raise VEError(f"InvalidInput: author predicate {predicate} begins with rights__")
        object.__setattr__(self, "rights", rights)
        super().__init__(raw)
        # VE.Rights.Correlate.checkBlock's order: nonempty, declared, distinct.
        holders, bearers = tuple(rights["holders"]), tuple(rights["bearers"])
        if not holders or not bearers:
            raise VEError("InvalidInput: invalid rights block")
        for sort in (*holders, *bearers):
            if sort not in self.sorts:
                raise UnknownSymbol(f"UnknownSymbol: sort {sort}")
        _duplicate(holders, "holder")
        _duplicate(bearers, "bearer")
        object.__setattr__(self, "holders", holders)
        object.__setattr__(self, "bearers", bearers)
        protected = rights.get("protected", [])
        if len(set(protected)) != len(protected):
            raise VEError("InvalidInput: protected")
        for name in protected:
            decl = self.predicates.get(name)
            if (decl is None or decl.regulated is not None or decl.defined is not None
                    or not set(decl.arguments) & set(holders)):
                raise VEError(f"InvalidInput: protected {name}")
        for act, entry in rights.get("alters", {}).items():
            declaration = self.predicates.get(act)
            if (declaration is None or declaration.regulated is None
                    or declaration.regulated.role != "permission"):
                raise VEError(f"InvalidInput: alters {act}")
            slot = entry["holder_slot"]
            if slot >= len(declaration.arguments):
                raise VEError(f"InvalidInput: alters {act}")
            holder = declaration.arguments[slot]
            status = self.predicates.get(entry["status"])
            recognition = self.predicates.get(entry["recognition"]) if entry.get("recognition") else None
            if (holder not in holders or status is None or status.regulated is not None
                    or status.defined is not None or holder not in status.arguments
                    or ("recognition" in entry and
                        (recognition is None or recognition.regulated is None
                         or recognition.regulated.role != "obligation"
                         or recognition.arguments[0] not in bearers
                         or holder not in recognition.arguments))):
                raise VEError(f"InvalidInput: alters {act}")

    def to_dict(self):
        result = super().to_dict()
        result["vocabulary"]["rights"] = deepcopy(self.rights)
        return result


class RightsDocument:
    """Python containers constructed from the Lean rights elaboration.

    Lean checks the complete source first. The objects below serve existing
    rendering and proof-search callers; they do not decide rights acceptance.
    """

    def __init__(self, env: RightsEnvironment, units, *, open_predicates=()):
        from .rights_route import run_rights_case
        from .errors import CheckerUnavailable
        from .ast import formula_from_data, _Decoder

        row = run_rights_case(env, units, "rights-elaborate",
                              open_predicates=sorted(open_predicates))
        try:
            self.elaborated = row
            self.env = env
            self.units = units
            self.rights = {}
            self.limitations = tuple(u["limitation"] for u in units if "limitation" in u)
            bars = [u["bar"] for u in units if "bar" in u]
            self.bar = bars[0] if bars else None
            self.outside = tuple(u for u in units if "norm" in u)
            self.source_units = tuple(next((u["source_units"] for u in units if "source_units" in u), ()))
            self.limitation_names = {(g["limitation"], g["act"]): g["name"]
                                     for g in row["generated"] if g["kind"] == "lim"}
            self.condition_names = {(g["limitation"], g["act"], g["condition"]): g["name"]
                                    for g in row["generated"] if g["kind"] == "cond"}
            self.bar_names = {g["predicate"]: g["name"] for g in row["generated"]
                              if g["kind"] == "aimed"}

            # Source references preserve the authored line's identity for the
            # renderer. Lean's lines are in precisely this source order.
            refs = []
            for unit in units:
                kind = "right" if "right" in unit else "right_lines" if "right_lines" in unit else None
                if kind is None:
                    continue
                body = unit[kind]
                right = body["name"] if kind == "right" else body["right"]
                if kind == "right":
                    self.rights[right] = {**body, "guard_formula": _Decoder().decode(body["guard"])}
                for line in body["lines"]:
                    fields = LINE_RULE_FIELDS[line["kind"]]
                    for field in fields:
                        raw = line[field]
                        fan = line.get("fan_out") or {}
                        for bearer in (sorted(fan) if fan else (None,)):
                            refs.append((right, line, raw, bearer))
            if len(refs) != len(row["lines"]):
                raise ValueError("rights line count")
            if set(row["wordings"]) != {g["name"] for g in row["generated"]}:
                raise ValueError("rights wording keys")
            for line_row, (right, line, raw, bearer) in zip(row["lines"], refs):
                if (line_row["right"] != right or line_row["kind"] != line["kind"] or
                    line_row.get("bearer") != bearer or
                    line_row["rule"] != line_row["node"]["name"] or
                    line_row["predicate"] != line_row["node"]["predicate"] or
                    (bearer is None and line_row["rule"] != raw["name"])):
                    raise ValueError("rights line binding")

            raw_env = env.to_dict()
            raw_env["profiles"].remove("rights@0")
            raw_env["vocabulary"].pop("rights")
            generated = row["environment_prime"]["vocabulary"]["predicates"]
            raw_env["vocabulary"]["predicates"].update(
                {name: declaration for name, declaration in generated.items()
                 if name.startswith("rights__")})
            self.environment = SoftEnvironment(raw_env, generated=True)
            self.line_env = self.environment

            def rule_from_node(node, raw):
                # Soft metadata stays in the source. Lean provides every
                # correlated W1 core field and the hard/mode decisions.
                norm = {key: raw[key] for key in ("rank", "alterable", "exception") if key in raw}
                norm.update({"name": node["name"], "predicate": node["predicate"],
                             "sign": node["sign"], "guard": node["guard"],
                             "unless": node["unless"], "over": node["over"],
                             "mode": node["mode"], "hard": node["hard"]})
                return {"norm": norm}

            self.instances = tuple({"right": r["right"], "source_kind": r["kind"],
                                    "kind": r["instance"], "rule": None,
                                    "holder_slot": r["holder_slot"],
                                    "cites": line.get("cites", {}),
                                    "bearer": r.get("bearer"), "source_line": line}
                                   for r, (_, line, _, _) in zip(row["lines"], refs))
            rules = [rule_from_node(r["node"], ref[2])
                     for r, ref in zip(row["lines"], refs)]
            rules.extend({"norm": u["norm"]} for u in self.outside)
            rules.extend(rule_from_node(n, {}) for n in row["bars"])
            self.soft_document = SoftNormDocument(self.environment, rules)
            for instance, rule in zip(self.instances, self.soft_document.rules):
                instance["rule"] = rule
            self.limitation_premises = tuple((item["label"],
                formula_from_data(self.soft_document.extended_env, item["ast"], _generated=True))
                for item in row["limitations"])
            object.__setattr__(self.soft_document.extended_env, "rights_premises",
                               self.limitation_premises)
            self.wordings = row["wordings"]
            object.__setattr__(self.environment, "rights_wordings", self.wordings)
            object.__setattr__(self.soft_document.extended_env, "rights_wordings", self.wordings)
        except Exception as exc:
            raise CheckerUnavailable("CheckerUnavailable: Lean accepted a rights source that "
                                     "the Python container could not build") from exc

def correlate(environment, units):
    """Return the validated holder-side document and its soft elaboration."""
    env = environment if isinstance(environment, RightsEnvironment) else RightsEnvironment(environment)
    return RightsDocument(env, units)
