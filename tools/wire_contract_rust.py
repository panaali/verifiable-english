"""Render format-1 contracts as data-only Rust table modules (docs/spec/wire-contract-s4-2.md 4)."""

from conformance.wire_contract_engine import pieces as split_template
from tools.wire_contract_lean import parse_pattern, parse_ranges


def q(value):
    """A Rust string literal: `\\`, `"` and the control characters escaped, every other character as itself."""
    return '"' + "".join(f"\\u{{{ord(c):x}}}" if ord(c) < 0x20 or ord(c) == 0x7F else
                         "\\" + c if c in '\\"' else c for c in value) + '"'


def seq(values):
    return "&[" + ", ".join(values) + "]"


def opt(value):
    return "None" if value is None else f"Some({value})"


def ordered(keys):
    """Keys in Unicode code point order (base spec 2.1): Python orders `str` by code point."""
    return sorted(keys)


def value(v):
    if type(v) is bool:
        return f"Value::Bool({'true' if v else 'false'})"
    if type(v) is int:
        return f"Value::Int({v})"
    return f"Value::Str({q(v)})"


def pattern(source):
    level, steps = parse_pattern(source)
    base = "Base::Root" if level is None else f"Base::Item({level})"
    return f"Pattern {{ base: {base}, steps: {seq('Step::Star' if s == '*' else f'Step::Tok({q(s)})' for s in steps)} }}"


def atom(a):
    return "Atom::" + a.capitalize()


def type_form(t):
    if type(t) is str:
        return f"TypeForm::Atom({atom(t)})"
    if "array_of" in t:
        return f"TypeForm::ArrayOf({atom(t['array_of'])})"
    return f"TypeForm::Tuple({seq(map(atom, t['tuple']))})"


def typ(t):
    return seq(map(type_form, t if type(t) is list else [t]))


def guard(literals):
    rendered = []
    for literal in literals:
        op, arg = next(iter(literal.items()))
        if op in ("present", "absent"):
            rendered.append(f"Lit::{op.capitalize()}({pattern(arg)})")
        elif op in ("equals", "differs"):
            rendered.append(f"Lit::{op.capitalize()}({pattern(arg[0])}, {value(arg[1])})")
        else:
            tag = "IsType" if op == "is" else "NotType"
            rendered.append(f"Lit::{tag}({pattern(arg[0])}, {typ(arg[1])})")
    return seq(rendered)


def ranges(spec):
    found = parse_ranges(spec)
    return "None" if found is None else f"Some({seq(f'({a}, {b})' for a, b in found)})"


def name_class(cls):
    return ("NameClass { first: " + ranges(cls.get("first")) + ", rest: " + ranges(cls.get("rest")) +
            ", min_bytes: " + opt(cls.get("min_bytes")) + ", max_bytes: " + opt(cls.get("max_bytes")) +
            ", forbid_prefix: " + seq(map(q, cls.get("forbid_prefix", []))) +
            ", forbid_infix: " + seq(map(q, cls.get("forbid_infix", []))) +
            ", one_of: " + opt(seq(map(q, cls["enum"])) if "enum" in cls else None) + " }")


def pieces(template):
    """The template split as the Python engine splits it: `{{` and `}}` are literal braces."""
    return seq(f"Piece::Lit({q(p[1])})" if p[0] == "lit" else f"Piece::Arg({q(p[1])}, Renderer::{p[2].capitalize()})"
               for p in split_template(template))


def keys(names):
    return seq(map(q, ordered(names)))


def kind(entry, codes, limits, names):
    k = entry["kind"]
    if k == "type": return f"Kind::HasType({typ(entry['type'])})"
    if k == "exact_keys": return f"Kind::ExactKeys({keys(entry['keys'])})"
    if k == "keys": return f"Kind::Keys({keys(entry['required'])}, {keys(entry['optional'])})"
    if k == "const": return f"Kind::Const({value(entry['value'])})"
    if k == "enum": return f"Kind::OneOf({seq(map(value, entry['values']))})"
    if k in ("max_items", "max_bytes", "max_count"):
        bound = entry["limit"] if type(entry["limit"]) is int else limits[entry["limit"]]
        if k == "max_count": return f"Kind::MaxCount({pattern(entry['of'])}, {bound})"
        return f"Kind::{'MaxItems' if k == 'max_items' else 'MaxBytes'}({bound})"
    if k == "name": return f"Kind::Name({name_class(names[entry['class']])}, {'true' if entry.get('on') == 'key' else 'false'})"
    if k == "sorted_unique": return "Kind::SortedUnique"
    if k == "unique_so_far": return "Kind::UniqueSoFar"
    if k == "declared_in": return f"Kind::DeclaredIn({pattern(entry['set'])})"
    if k in ("requires", "excludes"):
        tag = k.capitalize() + ("Member" if "member" in entry else "Item")
        return f"Kind::{tag}({q(entry['member']) if 'member' in entry else value(entry['item'])})"
    if k == "hook": return f"Kind::Hook({q(entry['hook'])})"
    if k == "classifier":
        members = ("Member { id: " + q(m["id"]) + ", code: " + q(m["code"]) + ", cls: " +
                   q(codes[m["code"]]["class"]) + ", text: " + pieces(m["text"]) +
                   ", inherited: " + str(bool(m.get("inherited"))).lower() + " }" for m in entry["emits"])
        return f"Kind::Classifier({q(entry['classifier'])}, {seq(members)})"
    raise ValueError(k)


def entries(rows, owner, known, limits, names, inside=False, depth=1):
    """One entry per line, indented by its depth, so that a diff of a table names its rows."""
    result = []
    for entry in rows:
        if "each" in entry:
            result.append(f"Entry::Each({q(entry['id'])}, {pattern(entry['each'])}, {guard(entry.get('when', []))}, " +
                          entries(entry["checks"], owner, known, limits, names, True, depth + 1) + ")")
        elif entry["kind"] == "include":
            target = known[entry["contract"]]
            included = [e for p in target["phases"] if p["name"] in entry["phases"] for e in p["checks"]]
            recode = (f"Some(({q(entry['as'])}, {q(owner['codes'][entry['as']]['class'])}))"
                      if "as" in entry else "None")
            result.append(f"Entry::Scope({q(entry['id'])}, {pattern(entry.get('at', '@' if inside else ''))}, " +
                          f"{opt(q(entry['view']) if 'view' in entry else None)}, {recode}, " +
                          entries(included, target, known, limits, names, False, depth + 1) + ")")
        else:
            code = entry.get("code", owner["residual"])
            args = entry.get("args", {})
            result.append("Entry::Check(Check { id: " + q(entry["id"]) +
                          ", loc: " + pattern(entry.get("at", "@" if inside else "")) +
                          ", guard: " + guard(entry.get("when", [])) +
                          ", kind: " + kind(entry, owner["codes"], limits, names) +
                          ", code: " + q(code) + ", cls: " + q(owner["codes"][code]["class"]) +
                          ", text: " + pieces(entry.get("text", "")) +
                          ", args: " + seq(f"({q(n)}, {pattern(args[n])})" for n in ordered(args)) +
                          ", inherited: " + str(bool(entry.get("inherited"))).lower() + " })")
    indent = "\n" + "    " * depth
    return "&[" + ",".join(indent + row for row in result) + "]"


def table(contract, known, limits, names):
    phases = ("Phase { name: " + q(phase["name"]) + ", entries: " +
              entries(phase["checks"], contract, known, limits, names) + " }" for phase in contract["phases"])
    residual = contract["residual"]
    return ("Table { contract: " + q(contract["contract"]) + f", revision: {contract['revision']}, residual: (" +
            q(residual) + ", " + q(contract["codes"][residual]["class"]) + "), phases: " + seq(phases) + " }")


def static_name(unit):
    return unit.split("@", 1)[0].upper().replace("-", "_")


def module(source, use, sources, contracts, known, limits, names):
    """A table module (4): the header naming every source with its hash, one `use`, `SOURCES`, one static
    per contract and `TABLES`. `sources` are (file, revision, sha256) rows; `contracts` the units to emit."""
    units = sorted(contracts)
    rows = sorted(sources)
    return ("// GENERATED by tools/wire_contract.py from " + source + ":\n" +
            "".join(f"// {file} revision {revision} sha256 {digest}\n" for file, revision, digest in rows) +
            "// Do not edit.\n" + f"use {use}::contract::*;\n\n" +
            "pub static SOURCES: &[Source] = " +
            seq(f"Source {{ file: {q(file)}, revision: {revision}, sha256: {q(digest)} }}"
                for file, revision, digest in rows) + ";\n\n" +
            "".join(f"pub static {static_name(unit)}: Table = {table(contracts[unit], known, limits, names)};\n\n"
                    for unit in units) +
            "pub static TABLES: &[&Table] = " + seq(f"&{static_name(unit)}" for unit in units) + ";\n")
