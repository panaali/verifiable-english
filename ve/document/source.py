"""A `ve-document` text read: its JSON front matter, its source bytes and `ve` fences, its units' parts,
identities and environment (moved from `ve/document.py`, AR-16a)."""
from __future__ import annotations

import json
import hashlib

from ..admission import token
from ..environment import Environment, listed_profiles
from ..errors import ResourceLimit, UnsupportedProfile, VEError
from ..identity import source_id
from ..wire import LONE_SURROGATE


MAX_DOCUMENT_BYTES = 4_000_000
SUPPORTS = {"assumption", "certificate", "observation", "calculation", "statistical",
            "testimony", "adapter", "none"}
STATUSES = {"CHECKED", "OPEN", "LABELLED", "UNFORMALISED"}
# The rights source kinds under `rights@0` (Lean `Service.Document.RightsKind`): a unit kind and its block's key.
_RIGHTS_KINDS = ("right", "right_lines", "limitation", "bar")


def _body(body: bytes):
    source = bytearray()
    fences = {}
    lines = body.splitlines(keepends=True)
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith(b"```ve "):
            try:
                uid = line[6:].strip().decode("ascii")
            except UnicodeDecodeError as exc:
                raise VEError("invalid VE fence name") from exc
            if not token(uid) or uid in fences:
                raise VEError("invalid or duplicate VE fence")
            i += 1
            content = bytearray()
            while i < len(lines) and lines[i].strip() != b"```":
                content.extend(lines[i])
                i += 1
            if i == len(lines):
                raise VEError("unclosed VE fence")
            try:
                fences[uid] = content.decode("utf-8")
            except UnicodeDecodeError as exc:
                raise VEError("VE fence is not UTF-8") from exc
        else:
            source.extend(line)
        i += 1
    return bytes(source), fences


def front_matter(raw: bytes):
    """The decoded JSON front matter of a document text and its body bytes, before any check of
    the metadata or the body: all that names a text's format."""
    if len(raw) > MAX_DOCUMENT_BYTES:
        raise VEError("document byte budget exceeded")
    if not raw.startswith(b"---\n"):
        raise VEError("ve-document@1 needs JSON front matter")
    boundary = raw.find(b"\n---\n", 4)
    if boundary < 0:
        raise VEError("unclosed JSON front matter")
    try:
        meta = json.loads(raw[4:boundary].decode("utf-8"))
    except (ValueError, UnicodeError) as exc:
        raise VEError("invalid JSON front matter") from exc
    except RecursionError:
        raise ResourceLimit("ResourceLimit: JSON front matter nesting exceeds the parser's depth") from None
    return meta, raw[boundary + 5:]


def _split(raw: bytes):
    meta, body = front_matter(raw)
    if type(meta) is not dict or meta.get("format") not in ("ve-document@1", "ve-document@2"):
        raise VEError("unsupported document format")
    allowed = {"format", "environment", "units", "open_terms", "reading_sets",
               "narrowings", "couplings", "weights", "graph", "lemmas",
               "contexts", "assessments", "bridges", "scoped", "completions", "senses"}
    if meta["format"] == "ve-document@2":
        allowed.add("discourse")
    if set(meta) - allowed:
        raise VEError("unknown document metadata")
    if "couplings" in meta and not {"rights@0", "readings@1"}.intersection(
            listed_profiles(meta.get("environment"))):
        raise UnsupportedProfile("UnsupportedProfile: rights@0 is required for couplings")
    if "completions" in meta and "norm-defaults@0" not in listed_profiles(meta.get("environment")):
        raise UnsupportedProfile("UnsupportedProfile: norm-defaults@0 is required for completions")
    return meta, *_body(body)


def _parts(units):
    """Flatten an explicitly partitioned mixed source unit for W2 admission.

    The parent is retained as provenance in each part. Its bytes are counted
    exactly once, by its children; no parent content can silently claim them.
    """
    for unit in units:
        if type(unit) is not dict:
            raise VEError("invalid unit schema")
        if unit.get("status") != "MIXED":
            if "parts" in unit:
                raise VEError("parts require MIXED status")
            yield unit, None
            continue
        if set(unit) != {"id", "span", "status", "parts"} or not token(unit["id"]):
            raise VEError("invalid MIXED unit schema")
        span, parts = unit["span"], unit["parts"]
        if (type(span) is not list or len(span) != 2 or
                any(type(x) is not int for x in span) or
                type(parts) is not list or len(parts) < 2):
            raise VEError("MIXED unit needs partitioned parts")
        cursor = span[0]
        for part in parts:
            if (type(part) is not dict or type(part.get("status")) is not str or part["status"] not in STATUSES or
                    type(part.get("span")) is not list or len(part["span"]) != 2 or
                    part["span"][0] != cursor):
                raise VEError("MIXED parts must partition their parent span")
            cursor = part["span"][1]
            yield part, unit["id"]
        if cursor != span[1]:
            raise VEError("MIXED parts must partition their parent span")


def _english_fences(units, fences):
    """The English fences a senses document's units name (RD-8), in unit order (`_parts`, whose structural faults it
    raises): unit id and fence text. Only a string id names a fence; any other id is refused by the unit checks.
    Lean's document mode lists the same (`Service.Document.sensesLayer`)."""
    return [(u["id"], fences[u["id"]]) for u, _ in _parts(units)
            if type(u) is dict and u.get("surface") == "english" and type(u.get("content")) is dict
            and type(u.get("id")) is str and u["content"].get("fence") == u["id"] and u["id"] in fences]


def _document_id(meta, source, fences):
    """Bind checked metadata and all authored content, but keep removable weights and JSON
    layout outside the evidence identity."""
    identity_payload = {
        "metadata": {key: value for key, value in meta.items() if key != "weights"},
        "source": source.decode("utf-8"), "fences": fences}
    return hashlib.sha256(
        (meta["format"] + "\n").encode("ascii") + json.dumps(identity_payload, sort_keys=True,
                                          ensure_ascii=False, separators=(",", ":"),
                                          allow_nan=False).encode("utf-8")).hexdigest()


def _environment(data):
    """The environment of a document's (profile-stripped) environment data."""
    profiles = listed_profiles(data)
    if "rights@0" in profiles:
        from ..rights import RightsEnvironment
        return RightsEnvironment(data)
    if "soft-norms@0" in profiles:
        from ..softnorms import SoftEnvironment
        return SoftEnvironment(data)
    return Environment(data)


def stored_identities(raw: bytes):
    """The front matter, `source_id` and `document_id` of a stored document text: the decode and
    identity of an imported or embedded document (discourse.md 4.1(10)), not its admission."""
    meta, source, fences = _split(raw)
    if not source:
        raise VEError("document source is empty")
    if type(meta.get("environment")) is not dict:
        raise VEError("document needs an embedded environment")
    env = _environment(base_environment(meta))
    return meta, source_id(source, env), _document_id(meta, source, fences)


def base_environment(meta):
    """The environment data the frozen environment and document routes receive: a `@1`
    document's own (its profile gate of discourse.md 1.1 only), a `@2` document's without
    `ve.discourse@1` (docs/spec/discourse.md 3.4; Lean has admitted the `@2` document first)."""
    from ..discourse import PROFILE
    data = meta["environment"]
    if meta["format"] == "ve-document@1":
        if type(data) is dict and type(data.get("profiles")) is list and PROFILE in data["profiles"]:
            raise UnsupportedProfile("UnsupportedProfile: ve.discourse@1 requires ve-document@2")
        return data
    if (type(data) is not dict or type(data.get("profiles")) is not list
            or any(type(p) is not str for p in data["profiles"])):
        raise VEError("invalid environment profiles")
    profiles = data["profiles"]
    if profiles != sorted(set(profiles)) or PROFILE not in profiles or "relational-fol@0" not in profiles:
        raise UnsupportedProfile("UnsupportedProfile: ve.discourse@1 requires a sorted profile list with relational-fol@0")
    if "discourse" not in meta:
        raise VEError("InvalidInput: missing discourse block")
    return {**data, "profiles": [p for p in profiles if p != PROFILE]}


def _no_lone_surrogate(meta) -> None:
    """A lone surrogate escape reads as a string no UTF-8 text holds (the document identity encodes the metadata):
    the JSON boundary's diagnostic, which the Lean `document` mode gives at the same point (`split`). A
    `ve-document@2` document's front matter is the discourse route's, which refuses it as invalid JSON."""
    try:
        json.dumps(meta, ensure_ascii=False).encode("utf-8")
    except UnicodeEncodeError as exc:
        raise VEError(LONE_SURROGATE) from exc
