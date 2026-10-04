"""Python relay for the ve.discourse@1 document profile.

A `ve-document@2` document's admission is the Lean route's (`ve_discourse_route`,
docs/spec/discourse.md 3.4, 8): it reads the same bytes and decides everything the
profile adds, from the block's wire shape and the stored documents to slot coverage,
reference resolution, groups, the joint set and the composition gate. Python relays
(docs/LEAN-FIRST-PLAN.md, rule 2, batch 4): a rejection is Lean's diagnostic, verbatim
(`rejection`), and an admission's references, unit statuses, report id, validity
verdicts, joint choices and joint disjunction are Lean's answer (`validate_discourse`).
Python reads the sibling files a document's imports name (`import_files`) and displays
the answer: a unit's reviewed wording replaces each resolved pronoun, demonstrative or
ordinal pair with the display its target is registered under. Without an answer from
Lean the result is `CheckerUnavailable`, never a Python-only verdict.
"""
from __future__ import annotations

import collections
import errno
import json
import os
from pathlib import Path

from .backends.lean_service import CheckerUnavailable
from .errors import ResourceLimit, UnsupportedProfile, VEError
from .readings import active_reading_sets

PROFILE = "ve.discourse@1"
_MAX_NESTING = 4  # Lean's `depthOf D ≤ 4`: how deep `import_files` reads the stored chain
_JOINT_BUDGET = 64  # Lean's `compatibleChoices` limit, shown beside an UNKNOWN joint set
_PRESENTED = {"pronoun", "demonstrative", "ordinal_pair"}
_LAYOUT = " \t\n\r"  # the layout around a unit's sentences, not part of them (4.1(4))


# Reading what Lean reads -----------------------------------------------------

def _is_text(value):
    """Whether a string decoded from JSON is UTF-8 text: Python's JSON reader lets an unpaired
    surrogate escape (`"\\udcff"`) through as a lone surrogate, which Lean's restricted reader
    rejects and which no UTF-8 JSON can carry."""
    try:
        value.encode("utf-8")
    except UnicodeEncodeError:
        return False
    return True


def _import_names(meta):
    """The sibling file names a front matter's import pins give (`bytes`), for any front matter.
    A name that is no UTF-8 text is none: Lean never reads the front matter that holds it."""
    block = meta.get("discourse")
    imports = block.get("imports") if type(block) is dict else None
    if type(imports) is not dict:
        return []
    return [pin["bytes"] for pin in imports.values()
            if type(pin) is dict and type(pin.get("bytes")) is str and _is_text(pin["bytes"])]


def _sibling(directory, name):
    """The bytes of a named sibling file, or None when there is no such file (as for a name no
    file can have: one too long for the file system)."""
    path = directory / name
    try:
        return path.read_bytes() if path.is_file() else None
    except OSError as exc:
        if exc.errno == errno.ENAMETOOLONG:
            return None
        raise CheckerUnavailable(f"CheckerUnavailable: import file {name} cannot be read ({exc})") from None


def _embedded(meta, source):
    """The bytes of the embedded units a front matter names, for any front matter, as Lean's
    `embeddedBytes` reads them: the first unit with the named id, its span's two naturals as a
    clamped byte range."""
    block = meta.get("discourse")
    declarations = block.get("documents") if type(block) is dict else None
    units = meta.get("units")
    if type(declarations) is not list or type(units) is not list:
        return []
    children = []
    for declaration in declarations:
        refers = declaration.get("refers") if type(declaration) is dict else None
        name = refers.get("embedded") if type(refers) is dict else None
        unit = next((u for u in units if type(u) is dict and u.get("id") == name), None) if type(name) is str else None
        span = unit.get("span") if unit is not None else None
        if type(span) is list and len(span) == 2 and all(type(x) is int and x >= 0 for x in span):
            children.append(source[span[0]:span[1]])
    return children


# The Lean authority (docs/spec/discourse.md 3.4, 8) ----------------------------

_ROUTE = Path(__file__).resolve().parents[1] / "lean/.lake/build/bin/ve_discourse_route"
_ROUTE_TIMEOUT = 300
_CASE_ID = "python-admission"
_STATUSES = {"CHECKED", "OPEN", "LABELLED", "UNFORMALISED"}


def route_executable():
    """The `ve_discourse_route` executable: `VE_DISCOURSE_ROUTE`, else the lake build."""
    return Path(os.environ.get("VE_DISCOURSE_ROUTE") or _ROUTE)


def is_discourse_text(raw):
    """Whether a document text is a `ve-document@2` document, whose admission is Lean's: its
    front matter's `format`, read before and apart from every other Python check, so a body or
    metadata Python reads differently still reaches Lean. A text whose front matter does not
    decode is not: Lean's restricted JSON reads a subset of Python's, so Lean rejects it too."""
    from .document import front_matter
    try:
        meta = front_matter(raw)[0]
    except VEError:
        return False
    return type(meta) is dict and meta.get("format") == "ve-document@2"


def import_files(raw, directory):
    """The sibling files the stored chain of a document text names, by the name its import pins
    give (`bytes`), as the texts the Lean route receives as the case's `files`, and the names of
    those that are no UTF-8 text: the imports of the document, of each stored document and of
    each embedded unit, to the nesting budget. Any front matter is read, however malformed (its
    rejection is Lean's), and breadth first, so a file is read at its least depth. A file that is
    no UTF-8 text cannot reach Lean (its `files` are JSON strings) and names no further file; a
    named file Python cannot read is `CheckerUnavailable`."""
    from .document import _split
    files, binary, done, queue = {}, [], set(), collections.deque([(raw, 0)])
    while queue:
        text, depth = queue.popleft()
        if depth > _MAX_NESTING or text in done:
            continue
        done.add(text)
        try:
            meta, source, _ = _split(text)
        except VEError:
            continue
        for name in _import_names(meta):
            if name in files or name in binary:
                continue
            data = _sibling(directory, name)
            if data is None:
                continue
            try:
                files[name] = data.decode("utf-8")
            except UnicodeError:
                binary.append(name)
                continue
            queue.append((data, depth + 1))
        queue.extend((child, depth + 1) for child in _embedded(meta, source))
    return files, binary


def _triple(value):
    return (type(value) is list and len(value) == 3 and type(value[0]) is str
            and all(type(x) is int and x >= 0 for x in value[1:]))


def _joint_answer(row):
    """Whether an admission row's joint set is well formed: a completed set (`joint` the number
    of its choices, each a `[set, version, index]` vector over the same sets) carries its choices
    and disjunction, and a set over its budget (`joint` a `ResourceLimit` text, `admitted:
    UNKNOWN`) carries neither."""
    joint = row.get("joint")
    if type(joint) is str:
        return (joint.startswith("ResourceLimit") and row.get("admitted") == "UNKNOWN"
                and "joint_choices" not in row and "joint_formula" not in row)
    choices = row.get("joint_choices")
    return (type(joint) is int and row.get("admitted") is True and type(choices) is list
            and len(choices) == joint > 0 and type(row.get("joint_formula")) is list
            and all(type(c) is list and all(_triple(x) for x in c) for c in choices)
            and len({tuple(tuple(x[:2]) for x in c) for c in choices}) == 1)


def lean_admission(raw, directory):
    """Lean's admission of a `ve-document@2` text (`ve_discourse_route`, kind `admission`), with the
    sibling files its imports name: `{"status": "ok", ...}` or `{"status": "error", "error"}`.
    Anything else (no executable, a crash, a timeout, output that is not one answer to this case)
    is `CheckerUnavailable`, never a verdict; there is no fallback to Python. What no UTF-8 JSON
    can carry never admits: a text that is no UTF-8 text is `InvalidInput` (Lean reads a document
    as a string), and a named file that is none is left out of the case, so Lean still diagnoses
    the document, but Lean's admission, which read that file as absent, is `InvalidInput`."""
    executable = route_executable()
    if not executable.is_file():
        raise CheckerUnavailable(f"CheckerUnavailable: the Lean discourse route {executable} is not built")
    try:
        text = raw.decode("utf-8")
    except UnicodeError:
        raise VEError("InvalidInput: the document is not UTF-8 text") from None  # relay-lint: file I/O
    files, binary = import_files(raw, directory)
    case = {"id": _CASE_ID, "kind": "admission", "document": text, "files": files}
    from .backends.lean import run_discourse_case
    returncode, stdout, stderr = run_discourse_case(executable, case, timeout=_ROUTE_TIMEOUT)
    try:
        rows = json.loads(stdout)
    except ValueError:
        rows = None
    row = rows[0] if type(rows) is list and len(rows) == 1 and type(rows[0]) is dict else {}
    status = row.get("status")
    well_formed = (row.get("id") == _CASE_ID and returncode == (1 if status == "error" else 0) and (
        type(row.get("error")) is str if status == "error" else
        status == "ok" and row.get("admitted") in (True, "UNKNOWN") and type(row.get("report_id")) is str
        and type(row.get("references")) is list and type(row.get("statuses")) is dict
        and all(type(v) is str and v in _STATUSES for v in row["statuses"].values())
        and type(row.get("validity")) is dict and type(row.get("bound")) is dict and _joint_answer(row)))
    if not well_formed:
        detail = stderr.decode("utf-8", "replace").strip()[-300:]
        raise CheckerUnavailable("CheckerUnavailable: the Lean discourse route returned no answer to the case"
                                 + (f" ({detail})" if detail else ""))
    if status == "ok" and binary:
        raise VEError(f"InvalidInput: import file {binary[0]} is not UTF-8 text")  # relay-lint: file I/O
    return row


def _error_of(message):
    """A Lean diagnostic as a Python error with its code, from the message's `Class:` prefix: the
    route's rows carry no `code` yet (the service sets one, batch 1). Lean's `NotImplemented` is an
    abstention, not a verdict: `UnsupportedProfile`, with Lean's text."""
    code = message.split(":", 1)[0]
    cls = {"ResourceLimit": ResourceLimit, "UnsupportedProfile": UnsupportedProfile,
           "NotImplemented": UnsupportedProfile}.get(code, VEError)
    error = cls(message)
    if cls is VEError and code.isidentifier() and code[:1].isupper():
        error.code = code
    return error


def rejection(lean):
    """The error of a document Lean does not admit: Lean's diagnostic, whatever Python read."""
    return _error_of(lean["error"])


def unavailable_report(error):
    """Python cannot load or report a document Lean admitted: no verdict, never a rejection."""
    return CheckerUnavailable(f"CheckerUnavailable: Lean admits the document but Python cannot report it ({error})")


def _joint(lean, block, active):
    """The joint set as Lean answered it: the compatible choices of the active open sets (each a
    mapping `set@version` to a reading index), or UNKNOWN over the budget."""
    constraints = block.get("constraints", []) if type(block) is dict else []
    count = len(constraints) if type(constraints) is list else 0
    if lean["admitted"] == "UNKNOWN":
        return {"status": "UNKNOWN", "budget": _JOINT_BUDGET, "constraints": count}
    open_sets = [(rs["id"], rs["version"]) for rs in active if rs["status"] == "open"]
    choices = lean["joint_choices"]
    if any([tuple(x[:2]) for x in choice] != open_sets for choice in choices):
        raise CheckerUnavailable("CheckerUnavailable: the Lean discourse route chose over other reading sets")
    return {"status": "complete", "choices": [{f"{s}@{v}": i for s, v, i in choice} for choice in choices],
            "count": len(choices), "constraints": count}


def _presentations(doc, block, lean):
    """Each unit's reviewed wording: a unit with meaning whose recorded formula-producing mentions
    are all resolved pronouns, demonstratives or ordinal pairs naming an entity, with each mention's
    bytes replaced by the display its target is registered under. Lean resolved the targets; the
    wording is shown only when the English parser reads it (each constant by the parser's own
    spelling, so a display it does not read back never decides) as exactly the formula Lean bound
    to the unit: nothing is displayed without passing the parser."""
    from .ast import formula_to_data
    from .english import EnglishVocabulary, parse_english
    env = doc["environment"]
    names = block.get("names", []) if type(block) is dict else []
    displays = {n["constant"]: n["display"] for n in names}
    spellings = EnglishVocabulary(env).constants
    spans = {m["id"]: m["span"] for m in block.get("mentions", [])} if type(block) is dict else {}
    active = {rs["unit"] for rs in active_reading_sets(doc["meta"].get("reading_sets", []))}
    by_unit = collections.defaultdict(list)
    for ref in lean["references"]:
        if ref["status"] != "navigation":
            by_unit[ref["unit"]].append((spans[ref["mention"]], ref, ref["target"]))
    out = {}
    for unit in doc["units"]:
        rows = sorted(by_unit.get(unit["id"], []), key=lambda r: r[0][0])
        bound = lean["bound"].get(unit["id"])
        if (not rows or bound is None or (unit["content"] is None and unit["id"] not in active)
                or any(ref["status"] != "resolved" or ref["form"] not in _PRESENTED
                       or target.get("kind") != "entity" or target.get("name") not in displays
                       or target["name"] not in spellings for _, ref, target in rows)):
            continue
        cursor, shown, read = unit["span"][0], b"", b""
        for (start, end), _, target in rows:
            gap = doc["source"][cursor:start]
            shown += gap + displays[target["name"]].encode("utf-8")
            read += gap + spellings[target["name"]].encode("utf-8")
            cursor = end
        rest = doc["source"][cursor:unit["span"][1]]
        try:
            parsed = parse_english(env, (read + rest).decode("utf-8").strip(_LAYOUT))
        except (VEError, UnicodeError):
            continue
        if len(parsed.formulas) == 1 and formula_to_data(env, parsed.formulas[0]) == bound:
            out[unit["id"]] = (shown + rest).decode("utf-8")
    return out


def validate_discourse(doc, lean):
    """The discourse admission of a loaded `@2` document: Lean's verdict and answer (`lean`, the
    route's answer on the same bytes), never Python's. The references, every unit's status, the
    report id, the validity verdicts, the joint choices and the joint disjunction are Lean's
    (`load_document` has raised Lean's rejection of a document Lean does not admit)."""
    block = doc["meta"]["discourse"]
    if set(lean["statuses"]) != {u["id"] for u in doc["units"]}:
        raise CheckerUnavailable("CheckerUnavailable: the Lean discourse route reported other units")
    for unit in doc["units"]:
        unit["status"] = lean["statuses"][unit["id"]]
    groups = block.get("groups", []) if type(block) is dict else []
    return {"references": lean["references"], "groups": groups,
            "joint": _joint(lean, block, active_reading_sets(doc["meta"].get("reading_sets", []))),
            "joint_formula": lean.get("joint_formula"),
            "presentations": _presentations(doc, block, lean),
            "report_id": lean["report_id"], "validity": lean["validity"]}


def report_discourse(doc, result):
    info = doc["discourse"]
    result["references"] = info["references"]
    result["groups"] = info["groups"]
    result["reviewed_presentations"] = info["presentations"]
    result["joint_choices"] = {k: v for k, v in info["joint"].items() if k != "choices"}
    # the report identity is Lean's (it binds Lean's references and validity verdicts)
    result["report_id"] = info["report_id"]
    if info["validity"]:
        result["validity"] = info["validity"]
