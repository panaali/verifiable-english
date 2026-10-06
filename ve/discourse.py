"""Python relay for the ve.discourse@1 document profile.

A `ve-document@2` document's admission is the Lean route's (service mode `discourse`,
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
import re

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

_CASE_ID = "python-admission"
_STATUSES = {"CHECKED", "OPEN", "LABELLED", "UNFORMALISED"}


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
    """Lean's admission of a `ve-document@2` text (service mode `discourse`, kind `admission`), with
    the sibling files its imports name: `{"status": "ok", ...}` or `{"status": "error", "error"}`.
    Anything else (no service, a crash, a deadline, a row that is not one answer to this case)
    is `CheckerUnavailable`, never a verdict; there is no fallback to Python. What no UTF-8 JSON
    can carry never admits: a text that is no UTF-8 text is `InvalidInput` (Lean reads a document
    as a string), and a named file that is none is left out of the case, so Lean still diagnoses
    the document, but Lean's admission, which read that file as absent, is `InvalidInput`."""
    try:
        text = raw.decode("utf-8")
    except UnicodeError:
        raise VEError("InvalidInput: the document is not UTF-8 text") from None  # relay-lint: file I/O
    files, binary = import_files(raw, directory)
    case = {"id": _CASE_ID, "kind": "admission", "document": text, "files": files}
    from .backends.relay import rows
    # The service binds the row to this case (`lean_service`), an error row included, and refuses every
    # malformed answer (`discourse.json#/row`).
    [row] = rows("discourse", [case])
    status = row.get("status") if type(row) is dict else None
    # A row naming the case by position is Lean's reader refusing the case Python wrote: no answer.
    well_formed = status is not None and row.get("id") == _CASE_ID and (
        "case_index" not in row and status == "error" and type(row.get("error")) is str or status == "ok" and (
        # `in (True, ...)` would let 1 through: True == 1 is no JSON equality.
        (row.get("admitted") is True or row.get("admitted") == "UNKNOWN") and type(row.get("report_id")) is str
        and type(row.get("references")) is list and type(row.get("statuses")) is dict
        and all(type(v) is str and v in _STATUSES for v in row["statuses"].values())
        and type(row.get("validity")) is dict and type(row.get("bound")) is dict and _joint_answer(row)))
    if not well_formed:
        raise CheckerUnavailable("CheckerUnavailable: the Lean discourse route returned no answer to the case")
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


# Binding Lean's answer to the document asked about ------------------------------
#
# `lean_admission` checks the answer's shape before Python loads the document; once loaded, every
# member the relay reads is bound to what the document records (an untrusted answer's schema): the units,
# the mentions, the validity claims and the active open reading sets. An answer that is not an
# answer to this document is `CheckerUnavailable`, never a verdict: Lean decides which choices are
# compatible and how each reference and claim comes out, Python only that the answer is about
# this document and well formed (no duplicate or out-of-range choice, the joint disjunction the
# one its choices denote).

_REFERENCE_STATUSES = {"resolved", "navigation", "pending"}  # Run.lean `referencesJson`
_VERDICT = re.compile(r"(checked|refuted|none|unconfirmed \(.+\))\Z", re.S)  # Admission.lean `verdictText`
_REPORT_ID = re.compile(r"[0-9a-f]{64}\Z")


def _foreign(member):
    return CheckerUnavailable(f"CheckerUnavailable: the Lean discourse route answered another document ({member})")


def _decoded(env, data, member):
    """A formula of the answer, decoded as Python decodes any formula; one that does not decode is
    no answer (an untrusted value never escapes as a Python error)."""
    from .ast import formula_from_data
    try:
        return formula_from_data(env, data)
    except (VEError, TypeError, ValueError, KeyError, IndexError, RecursionError):
        raise _foreign(member) from None


def _right_nested(tag, formulas):
    """`[tag, f1, [tag, f2, ... fn]]`, built from the right without recursion: a joint set has as
    many conjuncts as open sets and as many disjuncts as choices, more than Python's call depth."""
    out = formulas[-1]
    for formula in reversed(formulas[:-1]):
        out = [tag, formula, out]
    return out


def _conj(formulas):
    """Joint.lean `conj`, on the wire: the empty conjunction is top, one formula is itself, else
    right-nested."""
    return _right_nested("and", formulas) if formulas else ["top"]


def _disj(formulas):
    """Joint.lean `disj`, on the wire, over the nonempty list of a completed joint set."""
    return _right_nested("or", formulas)


def _keys(obj, expected, member):
    """A JSON object of the answer keyed by exactly the `expected` ids: membership, never order (Lean
    emits an object's keys in lexical order, not the document's)."""
    if set(obj) != set(expected):
        raise _foreign(member)


def _bind_references(block, references):
    """Run.lean `referencesJson`: one line per recorded mention, in manifest order, carrying the
    mention's id, unit, form and target as recorded, and one of the three statuses."""
    mentions = block.get("mentions", []) if type(block) is dict else []
    if len(references) != len(mentions):
        raise _foreign("references")
    for ref, mention in zip(references, mentions):
        if (type(ref) is not dict or set(ref) != {"mention", "unit", "form", "target", "status"}
                or [ref["mention"], ref["unit"], ref["form"], ref["target"]]
                != [mention["id"], mention["unit"], mention["form"], mention["target"]]
                or ref["status"] not in _REFERENCE_STATUSES):
            raise _foreign("references")


def _bind_joint(doc, lean, open_sets):
    """The joint set over the active open reading sets (Joint.lean `compatibleChoices` at Lean's
    budget): UNKNOWN exactly when their product is over the budget; else between one and product
    choices, each one reading index in range per open set, in that set order, listed in the
    enumeration's strictly increasing order (so none twice), and the joint disjunction the
    disjunction of the conjunctions of the chosen readings (`joint`)."""
    product = 1
    for rs in open_sets:
        product *= len(rs["readings"])
    if lean["admitted"] == "UNKNOWN":
        if product <= _JOINT_BUDGET:
            raise _foreign("joint")
        return
    choices = lean["joint_choices"]
    if product > _JOINT_BUDGET or not 1 <= len(choices) <= product:
        raise _foreign("joint")
    vectors = []
    for choice in choices:
        if (len(choice) != len(open_sets)
                or any([s, v] != [rs["id"], rs["version"]] or i >= len(rs["readings"])
                       for (s, v, i), rs in zip(choice, open_sets))):
            raise _foreign("joint choices")
        vectors.append([i for _, _, i in choice])
    if any(a >= b for a, b in zip(vectors, vectors[1:])):
        raise _foreign("joint choices")
    # compared on the wire: a joint disjunction of many choices is deeper than Python's AST budget
    from .ast import formula_to_data
    env = doc["environment"]
    readings = [[formula_to_data(env, _decoded(env, r["content"], "reading sets")) for r in rs["readings"]]
                for rs in open_sets]
    try:
        same = lean["joint_formula"] == _disj([_conj([readings[k][i] for k, i in enumerate(vector)])
                                               for vector in vectors])
    except RecursionError:  # deeper than the C stack compares: no answer Python can read
        same = False
    if not same:
        raise _foreign("joint formula")


def _bind_answer(doc, block, lean, open_sets):
    """Lean's answer, bound to the loaded document (see above)."""
    units = [u["id"] for u in doc["units"]]
    _keys(lean["statuses"], units, "statuses")
    if not _REPORT_ID.match(lean["report_id"]):
        raise _foreign("report id")
    _bind_references(block, lean["references"])
    # Admission.lean `admitCore`: every unit of a formula-producing (non-navigation) mention is
    # bound unless a presupposition of it is pending, and a pending unit never is
    pending = {ref["unit"] for ref in lean["references"] if ref["status"] == "pending"}
    producing = {ref["unit"] for ref in lean["references"] if ref["status"] != "navigation"}
    if not producing - pending <= set(lean["bound"]) <= set(units) - pending:
        raise _foreign("bound")
    for formula in lean["bound"].values():
        _decoded(doc["environment"], formula, "bound")
    claims = block.get("validity", []) if type(block) is dict else []
    _keys(lean["validity"], [claim["unit"] for claim in claims], "validity")
    if not all(type(v) is str and _VERDICT.match(v) for v in lean["validity"].values()):
        raise _foreign("validity")
    _bind_joint(doc, lean, open_sets)


def _joint(lean, block, open_sets):
    """The joint set as Lean answered it: the compatible choices of the active open sets (each a
    mapping `set@version` to a reading index), or UNKNOWN over the budget."""
    constraints = block.get("constraints", []) if type(block) is dict else []
    count = len(constraints) if type(constraints) is list else 0
    if lean["admitted"] == "UNKNOWN":
        return {"status": "UNKNOWN", "budget": _JOINT_BUDGET, "constraints": count}
    choices = lean["joint_choices"]
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
    open_sets = [rs for rs in active_reading_sets(doc["meta"].get("reading_sets", [])) if rs["status"] == "open"]
    _bind_answer(doc, block, lean, open_sets)
    for unit in doc["units"]:
        unit["status"] = lean["statuses"][unit["id"]]
    groups = block.get("groups", []) if type(block) is dict else []
    return {"references": lean["references"], "groups": groups,
            "joint": _joint(lean, block, open_sets),
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
