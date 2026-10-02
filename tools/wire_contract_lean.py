"""Render format-1 contracts as data-only Lean table modules."""

import json
import re


def q(value):
    return json.dumps(value, ensure_ascii=False)


def seq(values):
    return "[" + ", ".join(values) + "]"


def opt(value):
    return "none" if value is None else f"(some {value})"


def value(v):
    if type(v) is bool:
        return ".bool true" if v else ".bool false"
    if type(v) is int:
        return f".int {v}"
    return f".str {q(v)}"


def pattern(source):
    if source.startswith("@"):
        head, _, tail = source.partition("/")
        base = f".item {int(head[1:] or 0)}"
        steps = tail.split("/") if tail else []
    else:
        base = ".root"
        steps = source[1:].split("/") if source else []
    def step(s):
        return ".star" if s == "*" else f".tok {q(s.replace('~1', '/').replace('~0', '~'))}"
    return f"⟨{base}, {seq(map(step, steps))}⟩"


def atom(a):
    return f".{a}"


def type_form(t):
    if type(t) is str:
        return f".atom {atom(t)}"
    if "array_of" in t:
        return f".arrayOf {atom(t['array_of'])}"
    return f".tuple {seq(map(atom, t['tuple']))}"


def typ(t):
    return seq(map(type_form, t if type(t) is list else [t]))


def guard(literals):
    rendered = []
    for literal in literals:
        op, arg = next(iter(literal.items()))
        if op in ("present", "absent"):
            rendered.append(f".{op} {pattern(arg)}")
        elif op in ("equals", "differs"):
            rendered.append(f".{op} {pattern(arg[0])} ({value(arg[1])})")
        else:
            tag = "isType" if op == "is" else "notType"
            rendered.append(f".{tag} {pattern(arg[0])} {typ(arg[1])}")
    return seq(rendered)


def ranges(spec):
    if spec is None:
        return "none"
    out = []
    index = 0
    while index < len(spec):
        if index + 2 < len(spec) and spec[index + 1] == "-":
            out.append(f"({ord(spec[index])}, {ord(spec[index + 2])})")
            index += 3
        else:
            out.append(f"({ord(spec[index])}, {ord(spec[index])})")
            index += 1
    return f"some {seq(out)}"


def name_class(cls):
    return "⟨" + ", ".join((
        ranges(cls.get("first")), ranges(cls.get("rest")),
        opt(str(cls["min_bytes"]) if "min_bytes" in cls else None),
        opt(str(cls["max_bytes"]) if "max_bytes" in cls else None),
        seq(map(q, cls.get("forbid_prefix", []))),
        seq(map(q, cls.get("forbid_infix", []))),
        opt(seq(map(q, cls["enum"])) if "enum" in cls else None),
    )) + "⟩"


PLACEHOLDER = re.compile(r"\{([A-Za-z_][A-Za-z_0-9]*)(?::([A-Za-z]+))?\}")


def pieces(template):
    out = []
    start = 0
    for match in PLACEHOLDER.finditer(template):
        if match.start() > start:
            out.append(f".lit {q(template[start:match.start()])}")
        out.append(f".arg {q(match[1])} .{match[2] or 'raw'}")
        start = match.end()
    if start < len(template):
        out.append(f".lit {q(template[start:])}")
    return seq(out)


def kind(entry, limits, names):
    k = entry["kind"]
    if k == "type": return f".hasType {typ(entry['type'])}"
    if k == "exact_keys": return f".exactKeys {seq(map(q, entry['keys']))}"
    if k == "keys": return f".keys {seq(map(q, entry['required']))} {seq(map(q, entry['optional']))}"
    if k == "const": return f".const ({value(entry['value'])})"
    if k == "enum": return f".oneOf {seq(f'({value(v)})' for v in entry['values'])}"
    if k in ("max_items", "max_bytes", "max_count"):
        bound = entry["limit"] if type(entry["limit"]) is int else limits[entry["limit"]]
        if k == "max_count": return f".maxCount {pattern(entry['of'])} {bound}"
        return f".{('maxItems' if k == 'max_items' else 'maxBytes')} {bound}"
    if k == "name": return f".name {name_class(names[entry['class']])} {'true' if entry.get('on') == 'key' else 'false'}"
    if k == "sorted_unique": return ".sortedUnique"
    if k == "unique_so_far": return ".uniqueSoFar"
    if k == "declared_in": return f".declaredIn {pattern(entry['set'])}"
    if k in ("requires", "excludes"):
        tag = k + ("Member" if "member" in entry else "Item")
        arg = q(entry["member"]) if "member" in entry else f"({value(entry['item'])})"
        return f".{tag} {arg}"
    if k == "hook": return f".hook {q(entry['hook'])}"
    if k == "classifier":
        members = []
        for m in entry["emits"]:
            members.append("{ id := " + q(m["id"]) + ", code := " + q(m["code"]) +
                           ", cls := " + q(entry["_codes"][m["code"]]["class"]) +
                           ", text := " + pieces(m["text"]) +
                           ", inherited := " + str(bool(m.get("inherited"))).lower() + " }")
        return f".classifier {q(entry['classifier'])} {seq(members)}"
    raise ValueError(k)


def entries(rows, owner, known, limits, names, inside=False):
    result = []
    for entry in rows:
        if "each" in entry:
            result.append(f".each {q(entry['id'])} {pattern(entry['each'])} {guard(entry.get('when', []))} " +
                          entries(entry["checks"], owner, known, limits, names, True))
        elif entry["kind"] == "include":
            target = known[entry["contract"]]
            included = [e for p in target["phases"] if p["name"] in entry["phases"] for e in p["checks"]]
            recode = (f"(some ({q(entry['as'])}, {q(owner['codes'][entry['as']]['class'])}))"
                      if "as" in entry else "none")
            result.append(f".scope {q(entry['id'])} {pattern(entry.get('at', '@' if inside else ''))} " +
                          f"{opt(q(entry['view']) if 'view' in entry else None)} {recode} " +
                          entries(included, target, known, limits, names))
        else:
            e = {**entry, "_codes": owner["codes"]}
            result.append(".check { id := " + q(e["id"]) +
                          ", loc := " + pattern(e.get("at", "@" if inside else "")) +
                          ", guard := " + guard(e.get("when", [])) +
                          ", kind := " + kind(e, limits, names) +
                          ", code := " + q(e.get("code", owner["residual"])) +
                          ", cls := " + q(owner["codes"][e.get("code", owner["residual"])]["class"]) +
                          ", text := " + pieces(e.get("text", "")) +
                          ", args := " + seq(f"({q(n)}, {pattern(p)})" for n, p in e.get("args", {}).items()) +
                          ", inherited := " + str(bool(e.get("inherited"))).lower() + " }")
    return seq(result)


def table(contract, known, limits, names):
    phases = []
    for phase in contract["phases"]:
        phases.append("{ name := " + q(phase["name"]) + ", entries := " +
                      entries(phase["checks"], contract, known, limits, names) + " }")
    residual = contract["residual"]
    return ("{ contract := " + q(contract["contract"]) +
            f", revision := {contract['revision']}, residual := ({q(residual)}, " +
            q(contract["codes"][residual]["class"]) + "), phases := " + seq(phases) + " }")


def module(namespace, definitions, source, revision, digest, limit_digest, name_digest):
    return (f"/- GENERATED by tools/wire_contract.py from {source}, revision {revision},\n"
            f"   sha256 {digest}; limits {limit_digest}; names {name_digest}. Do not edit. -/\n"
            "import VE.WireContract.Table\n\n" +
            f"namespace VE.WireContract.Tables.{namespace}\n" + definitions +
            f"end VE.WireContract.Tables.{namespace}\n")
