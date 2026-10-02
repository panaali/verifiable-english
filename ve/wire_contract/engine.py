"""Ordered, diagnostic-only interpreter for wire contracts (format 1)."""

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
from typing import Callable

from ve.errors import CheckerUnavailable, VEError
from ve.wire import canonical_json, loads_json


ROOT = Path(__file__).resolve().parent
ABSENT = object()
_PATTERN = re.compile(r"^(?:@(?:[0-9]+)?(?=/|$))?(?:/[^/]*)*$")
_TOKEN = re.compile(r"(?:0|[1-9][0-9]*)\Z")
_PLACEHOLDER = re.compile(r"\{([a-zA-Z_][a-zA-Z_0-9]*)(?::(raw|json|index|count|list))?\}")


@dataclass(frozen=True)
class Fault:
    record: dict


@dataclass(frozen=True)
class Clean:
    pass


@dataclass(frozen=True)
class Deferred:
    id: str


CLEAN = Clean()


@dataclass
class Registry:
    hooks: dict[str, Callable]
    classifiers: dict[str, Callable]
    views: dict[str, Callable]
    adapters: dict[str, Callable]

    def __init__(self):
        self.hooks, self.classifiers, self.views, self.adapters = {}, {}, {}, {}

    def register(self, *, hooks=None, classifiers=None, views=None, adapters=None):
        for attr, entries in (("hooks", hooks), ("classifiers", classifiers),
                              ("views", views), ("adapters", adapters)):
            if entries:
                getattr(self, attr).update(entries)
        return self


def load(unit: str, *, directory: Path = ROOT) -> dict:
    """Load a locked contract. A bad package is an operational error."""
    filename = f"{unit}.json"
    contract = loads_json((directory / filename).read_bytes())
    lock = loads_json((directory / "contracts.lock").read_bytes())
    for used in (filename, *(f"{name}.json" for name in contract.get("uses", []))):
        value = contract if used == filename else loads_json((directory / used).read_bytes())
        actual = hashlib.sha256(canonical_json(value)).hexdigest()
        revision = value.get("revision", lock.get(used, {}).get("revision", 1))
        if lock.get(used) != {"revision": revision, "sha256": actual}:
            raise RuntimeError(f"wire contract lock mismatch: {used}")
    return contract


def _domain(value, depth=0):
    if depth > 256:
        return False
    if value is None or type(value) is bool:
        return True
    if type(value) is str:
        return not any(0xD800 <= ord(char) <= 0xDFFF for char in value)
    if type(value) is int:
        return 0 <= value <= 2**53 - 1
    if type(value) in (list, tuple):
        return all(_domain(v, depth + 1) for v in value)
    if type(value) is dict:
        return all(_domain(k, depth + 1) and type(k) is str and _domain(v, depth + 1)
                   for k, v in value.items())
    return False


def _equal(a, b):
    if type(a) is not type(b):
        if type(a) in (list, tuple) and type(b) in (list, tuple):
            return len(a) == len(b) and all(_equal(x, y) for x, y in zip(a, b))
        return False
    if type(a) is dict:
        return a.keys() == b.keys() and all(_equal(a[k], b[k]) for k in a)
    if type(a) in (list, tuple):
        return len(a) == len(b) and all(_equal(x, y) for x, y in zip(a, b))
    return a == b


def _unescape(token):
    return token.replace("~1", "/").replace("~0", "~")


def _pointer(tokens):
    return "".join("/" + t.replace("~", "~0").replace("/", "~1") for t in tokens)


def _parse(pattern, items):
    if not _PATTERN.fullmatch(pattern):
        raise ValueError(f"invalid pattern: {pattern}")
    head, *rest = pattern.split("/")
    if head.startswith("@"):
        level = int(head[1:] or 0)
        if level >= len(items):
            return None
        base = items[level]
    else:
        base = ()
        rest = pattern.split("/")[1:] if pattern else []
    return base, [_unescape(s) for s in rest]


def _step(value, token):
    if type(value) is dict:
        return value.get(token, ABSENT)
    if type(value) in (list, tuple) and _TOKEN.fullmatch(token):
        index = int(token)
        if index < len(value):
            return value[index]
    return ABSENT


def matches(root, items, pattern):
    parsed = _parse(pattern, items)
    if parsed is None:
        return []
    base, steps = parsed
    value = root
    for token in base:
        value = _step(value, token)
        if value is ABSENT:
            return []
    found = [(base, value)]
    for token in steps:
        next_found = []
        for path, value in found:
            if token == "*":
                if type(value) in (list, tuple):
                    next_found.extend((path + (str(i),), v) for i, v in enumerate(value))
                elif type(value) is dict:
                    next_found.extend((path + (k,), value[k]) for k in sorted(value))
            else:
                v = _step(value, token)
                if v is not ABSENT:
                    next_found.append((path + (token,), v))
        found = next_found
    return found


def resolve(root, items, location):
    result = matches(root, items, location)
    return result[0] if result else None


def concrete(items, location):
    parsed = _parse(location, items)
    if parsed is None:
        return ""
    base, steps = parsed
    return _pointer(base + tuple(steps))


def _atom(value, atom):
    return {"null": value is None, "boolean": type(value) is bool,
            "integer": type(value) is int, "string": type(value) is str,
            "array": type(value) in (list, tuple), "object": type(value) is dict}[atom]


def _type(value, form):
    if type(form) is list:
        return any(_type(value, f) for f in form)
    if type(form) is str:
        return _atom(value, form)
    if "array_of" in form:
        return type(value) in (list, tuple) and all(_atom(v, form["array_of"]) for v in value)
    parts = form["tuple"]
    return type(value) in (list, tuple) and len(value) == len(parts) and all(
        _atom(v, a) for v, a in zip(value, parts))


def _guard(root, items, literals):
    for literal in literals:
        op, arg = next(iter(literal.items()))
        loc = arg if op in ("present", "absent") else arg[0]
        match = resolve(root, items, loc)
        value = ABSENT if match is None else match[1]
        holds = {
            "present": lambda: value is not ABSENT,
            "absent": lambda: value is ABSENT,
            "equals": lambda: value is not ABSENT and _equal(value, arg[1]),
            "differs": lambda: value is ABSENT or not _equal(value, arg[1]),
            "is": lambda: value is not ABSENT and _type(value, arg[1]),
            "is_not": lambda: value is ABSENT or not _type(value, arg[1]),
        }[op]()
        if not holds:
            return False
    return True


def _character_set(spec):
    chars = set()
    i = 0
    while i < len(spec):
        if i + 2 < len(spec) and spec[i + 1] == "-":
            chars.update(chr(n) for n in range(ord(spec[i]), ord(spec[i + 2]) + 1))
            i += 3
        else:
            chars.add(spec[i])
            i += 1
    return chars


def _name(value, cls):
    if type(value) is not str:
        return False
    if "first" in cls and (not value or value[0] not in _character_set(cls["first"])):
        return False
    if "rest" in cls and any(c not in _character_set(cls["rest"]) for c in value[1:]):
        return False
    size = len(value.encode("utf-8"))
    return (size >= cls.get("min_bytes", 0) and size <= cls.get("max_bytes", 2**53 - 1)
            and not any(value.startswith(s) for s in cls.get("forbid_prefix", []))
            and not any(s in value for s in cls.get("forbid_infix", []))
            and ("enum" not in cls or value in cls["enum"]))


def _json_text(value):
    def string(v):
        result = ['"']
        for char in v:
            if char == '"':
                result.append('\\"')
            elif char == "\\":
                result.append("\\\\")
            elif ord(char) < 0x20:
                result.append(f"\\u{ord(char):04x}")
            else:
                result.append(char)
        return "".join(result) + '"'

    def encode(v):
        if type(v) is dict:
            return "{" + ",".join(encode(k) + ":" + encode(v[k]) for k in sorted(v)) + "}"
        if type(v) in (list, tuple):
            return "[" + ",".join(map(encode, v)) + "]"
        if type(v) is str:
            return string(v)
        return json.dumps(v, ensure_ascii=False, separators=(",", ":"))
    full = encode(value)
    if len(full.encode("utf-8")) <= 80:
        return full
    result = ""
    for c in full:
        if len((result + c).encode("utf-8")) > 80:
            break
        result += c
    return result + "..."


def _render(value, renderer):
    if value is ABSENT:
        return ""
    if renderer == "raw" and type(value) is str:
        return value
    if renderer in ("index", "count") and type(value) is int:
        return str(value)
    if renderer == "list" and type(value) in (list, tuple) and all(type(v) is str for v in value):
        return ", ".join(sorted(value))
    return _json_text(value)


def _template(template, values):
    escaped = template.replace("{{", "\x01").replace("}}", "\x02")
    args = {}
    def replace(match):
        name, renderer = match.groups()
        rendered = _render(values.get(name, ABSENT), renderer or "raw")
        args[name] = rendered
        return rendered
    return _PLACEHOLDER.sub(replace, escaped).replace("\x01", "{").replace("\x02", "}"), args


def _limit(value, limits):
    return limits[value] if type(value) is str else value


def _fails(entry, root, items, earlier, names, limits):
    kind = entry["kind"]
    loc = entry.get("at", "@" if items else "")
    found = resolve(root, items, loc)
    path, value = found if found is not None else (None, ABSENT)
    extras = {}
    if kind == "max_count":
        count = len(matches(root, items, entry["of"]))
        limit = _limit(entry["limit"], limits)
        return count > limit, {"count": count, "limit": limit}, concrete(items, loc), ABSENT
    if value is ABSENT:
        return False, extras, concrete(items, loc), value
    if kind == "type":
        fail = not _type(value, entry["type"])
    elif kind == "exact_keys":
        fail = type(value) is not dict or set(value) != set(entry["keys"])
    elif kind == "keys":
        fail = (type(value) is not dict or not set(entry["required"]) <= set(value)
                or not set(value) <= set(entry["required"] + entry["optional"]))
    elif kind == "const":
        fail = not _equal(value, entry["value"])
    elif kind == "enum":
        fail = not any(_equal(value, v) for v in entry["values"])
    elif kind in ("max_items", "max_bytes"):
        count = (len(value) if kind == "max_items" and type(value) in (list, tuple, dict)
                 else len(value.encode("utf-8")) if kind == "max_bytes" and type(value) is str else 0)
        limit = _limit(entry["limit"], limits)
        fail = count > limit
        extras = {"count": count, "limit": limit}
    elif kind == "name":
        candidate = path[-1] if entry.get("on") == "key" else value
        fail = not _name(candidate, names[entry["class"]])
    elif kind == "sorted_unique":
        fail = type(value) in (list, tuple) and all(type(v) is str for v in value) and any(
            a >= b for a, b in zip(value, value[1:]))
    elif kind == "unique_so_far":
        fail = any((prior := resolve(root, (p,) + items[1:], loc)) is not None
                   and _equal(value, prior[1]) for p in earlier)
    elif kind == "declared_in":
        fail = not any(_equal(value, v) for _, v in matches(root, items, entry["set"]))
    elif kind in ("requires", "excludes"):
        if "member" in entry:
            present = type(value) is dict and entry["member"] in value
            fail = type(value) is dict and (not present if kind == "requires" else present)
        else:
            present = type(value) in (list, tuple) and any(_equal(v, entry["item"]) for v in value)
            fail = type(value) in (list, tuple) and (not present if kind == "requires" else present)
    else:
        raise ValueError(f"unknown kind: {kind}")
    return fail, extras, _pointer(path), value


def run(contract, root, *, registry=None, contracts=None, limits=None, names=None):
    """Return the first fault, a deferred id, or clean; never decide acceptance."""
    if not _domain(root):
        return CLEAN
    registry = registry or Registry()
    contracts = contracts or {}
    limits = limits if limits is not None else loads_json((ROOT / "limits.json").read_bytes())
    names = names if names is not None else loads_json((ROOT / "names.json").read_bytes())
    if type(root) is not dict:
        root = {}
    root = {name: root.get(name) for name in contract["input"]}

    def walk(entries, phase, current, items=(), earlier=(), sites=(), ids=(), recode=None,
             viewed=False, declaring_codes=None):
        declaring_codes = declaring_codes or contract["codes"]
        for entry in entries:
            if not _guard(current, items, entry.get("when", [])):
                continue
            if "each" in entry:
                prior = []
                for path, _ in matches(current, items, entry["each"]):
                    result = walk(entry["checks"], phase, current, (path,) + items,
                                  tuple(prior), sites, ids, recode, viewed, declaring_codes)
                    if result is not CLEAN:
                        return result
                    prior.append(path)
                continue
            if entry.get("kind") == "include":
                site = resolve(current, items, entry.get("at", "@" if items else ""))
                if site is None:
                    continue
                site_path, value = site
                view_name = entry.get("view")
                if view_name:
                    view = registry.views.get(view_name)
                    if view is None:
                        return Deferred("/".join(ids + (entry["id"],)))
                    value = view(value)
                inner = contracts.get(entry["contract"])
                if inner is None:
                    inner = load(entry["contract"])
                for included_phase in inner["phases"]:
                    if included_phase["name"] in entry["phases"]:
                        result = walk(included_phase["checks"], phase, value, (), (),
                                      sites + (site_path,), ids + (entry["id"],),
                                      recode or entry.get("as"), viewed or bool(view_name),
                                      inner["codes"])
                        if result is not CLEAN:
                            return result
                continue
            kind = entry["kind"]
            member = entry
            loc = entry.get("at", "@" if items else "")
            path = concrete(items, loc)
            values = {"key": items[0][-1] if items and items[0] else "",
                      "index": 0, "value": ABSENT}
            if items:
                # An item index is its position in its group's ordered matches, not its array token.
                values["index"] = len(earlier)
            target = resolve(current, items, loc)
            if target is not None:
                values["value"] = target[1]
            if kind == "hook":
                fn = registry.hooks.get(entry["hook"])
                if fn is None:
                    return Deferred("/".join(ids + (entry["id"],)))
                answer = fn(current, items)
                fail = answer is not None and answer is not False
                extra = answer if type(answer) is dict else {}
            elif kind == "classifier":
                fn = registry.classifiers.get(entry["classifier"])
                if fn is None:
                    return Deferred("/".join(ids + (entry["id"],)))
                answer = fn(current, items)
                if not answer:
                    continue
                member_id, extra = answer
                member = next((m for m in entry["emits"] if m["id"] == member_id), None)
                if member is None:
                    continue
                fail = True
            else:
                fail, extra, path, value = _fails(entry, current, items, earlier, names, limits)
                values["value"] = value
            if not fail:
                continue
            for name, location in entry.get("args", {}).items():
                found = resolve(current, items, location)
                values[name] = found[1] if found else ABSENT
            values.update(extra)
            text, rendered = _template(member["text"], values)
            code = recode or member["code"]
            cls = (contract["codes"] if recode else declaring_codes)[code]["class"]
            if sites:
                if viewed:
                    rendered["inner_path"] = path
                    path = "".join(_pointer(s) for s in sites)
                else:
                    path = "".join(_pointer(s) for s in sites) + path
            record = {"contract": contract["contract"], "revision": contract["revision"],
                      "check": "/".join(ids + (member["id"],)), "phase": phase,
                      "code": code, "class": cls, "path": path, "text": text, "args": rendered}
            return Fault(record)
        return CLEAN

    for phase in contract["phases"]:
        outcome = walk(phase["checks"], phase["name"], root)
        if outcome is not CLEAN:
            return outcome
    return CLEAN


def overlay(contract, legacy_error: VEError | None, outcome, lean=None):
    """Choose a record for an existing rejection; shadow callers only inspect it."""
    if legacy_error is None:
        return None
    if isinstance(outcome, Deferred) and lean is not None:
        try:
            outcome = lean() if callable(lean) else lean
        except CheckerUnavailable:
            # Diagnosis is optional; the legacy validator has already rejected.
            pass
    if isinstance(outcome, Deferred):
        return {"contract": contract["contract"], "revision": contract["revision"],
                "deferred": outcome.id, "text": str(legacy_error)}
    if isinstance(outcome, Fault):
        return outcome.record
    code = contract["residual"]
    return {"contract": contract["contract"], "revision": contract["revision"],
            "check": "residual", "phase": "residual", "code": code,
            "class": contract["codes"][code]["class"], "path": "",
            "text": str(legacy_error), "args": {}}
