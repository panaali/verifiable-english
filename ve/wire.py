"""Strict JSON and RFC 8785 serialization for VE's restricted JSON subset.

There are no floating-point numbers in this subset. Object keys sort by UTF-16
code units, not Python's Unicode-code-point order. Surrogates are rejected.
"""
import hashlib
import json

from .errors import DuplicateDeclaration, ResourceLimit, SyntaxError, VEError
from .limits import MAX_INDEX, MAX_PACKAGE_BYTES


def _string(value: str) -> None:
    if any(0xD800 <= ord(c) <= 0xDFFF for c in value):
        raise VEError("JSON strings must not contain lone UTF-16 surrogates")


def validate_json(value, depth: int = 0) -> None:
    if depth > 256:
        raise ResourceLimit("JSON nesting exceeds 256 levels")
    if type(value) is str:
        _string(value)
    elif type(value) is bool:
        pass
    elif type(value) is int:
        if not 0 <= value <= MAX_INDEX:
            raise VEError("JSON integers must be in [0, 2^53-1]")
    elif type(value) is list:
        for item in value:
            validate_json(item, depth + 1)
    elif type(value) is dict:
        for key, item in value.items():
            if type(key) is not str:
                raise VEError("JSON object keys must be strings")
            _string(key)
            validate_json(item, depth + 1)
    else:
        raise VEError("Unsupported JSON value; null and floating-point numbers are not in v0")


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateDeclaration(f"Duplicate JSON object key: {key!r}")
        result[key] = value
    return result


def _integer(text):
    if len(text) > 16:
        raise ResourceLimit("JSON integer exceeds supported bound")
    value = int(text)
    if not 0 <= value <= MAX_INDEX:
        raise VEError("JSON integers must be in [0, 2^53-1]")
    return value


def _invalid_number(text):
    raise VEError(f"Unsupported JSON number: {text}")


def loads_json(data: str | bytes):
    if not isinstance(data, (str, bytes)):
        raise SyntaxError("JSON input must be str or bytes")
    try:
        raw = data.encode("utf-8") if isinstance(data, str) else data
        if len(raw) > MAX_PACKAGE_BYTES:
            raise ResourceLimit("JSON package exceeds 16 MiB")
        text = raw.decode("utf-8")
        value = json.loads(text, object_pairs_hook=_pairs, parse_int=_integer,
                           parse_float=_invalid_number, parse_constant=_invalid_number)
        validate_json(value)
        return value
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise SyntaxError(f"Invalid UTF-8 JSON: {exc}") from exc
    except RecursionError as exc:
        raise ResourceLimit("JSON nesting exceeds runtime limit") from exc


def canonical_json(value) -> bytes:
    validate_json(value)

    def encode(v):
        if type(v) is dict:
            return "{" + ",".join(encode(k) + ":" + encode(v[k])
                                  for k in sorted(v, key=lambda k: k.encode("utf-16be"))) + "}"
        if type(v) is list:
            return "[" + ",".join(map(encode, v)) + "]"
        return json.dumps(v, ensure_ascii=False, separators=(",", ":"), allow_nan=False)

    result = encode(value).encode("utf-8")
    if len(result) > MAX_PACKAGE_BYTES:
        raise ResourceLimit("Canonical JSON package exceeds 16 MiB")
    return result


def digest(domain: str, payload) -> str:
    return hashlib.sha256(domain.encode("ascii") + canonical_json(payload)).hexdigest()


def require_fields(value, fields, *, path="", error=VEError):
    if type(value) is not dict:
        raise error("Expected a JSON object", path=path)
    expected = set(fields)
    if set(value) != expected:
        missing, extra = expected - set(value), set(value) - expected
        raise error(f"Incorrect fields (missing={sorted(missing)}, unknown={sorted(extra)})", path=path)
