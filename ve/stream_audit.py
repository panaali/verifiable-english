"""Canonical audit helpers for model-backend streams: ONE credential sanitizer and ONE usage count.

Standard library only (no other ``ve`` imports), shared by the claude CLI endpoint
(``ve_experiments.claude_cli``), the ``ve assist`` session and its verifier, so the rules
that write a record are exactly the rules that check it.

Credentials
-----------
The subscription access token lives only in the child process environment and is never put
in a prompt, so a model cannot legitimately echo it. Defence in depth: every string that is
persisted or returned passes through :func:`sanitize`, which

1. replaces every literal occurrence of a *needle* (the token, its leading prefix, and the
   known credential prefix ``sk-ant-``), case-insensitively;
2. sanitizes JSON embedded in the string (a whole-string JSON value, or the ``{...}`` span a
   candidate parser would read) as a structure, and re-serialises it only if that changed
   something, so a reply stays usable with the echoed value redacted;
3. then decodes the result to a FIXPOINT under every supported encoding -- backslash escapes
   (``\\uXXXX``, ``\\xXX``, octal ``\\157``, ``\\/`` ...: JSON strings inside JSON, at any
   depth), percent-encoding, HTML entities, Unicode NFKC, base64 / base64url (also wrapped across
   lines) and hex chunks of plausible length, composed in any order -- and if ANY decoded view
   still contains a needle (or the fixpoint cannot be reached within bounds), the whole string
   is replaced by ``[REDACTED]``.

Step 3 is the gate that closes the class: the output of :func:`sanitize` never exposes a
needle under any composition of the supported decodings, and :func:`sanitize` is idempotent.

Usage
-----
:func:`stream_usage` is the field-wise MAX over EVERY usage-bearing record of a stream
(every ``result`` record and every ``assistant`` message), whatever the stream's shape, so a
later record (a second result reporting zeros, a result without usage) can never erase what
an earlier one reported. The endpoint counts with it and the verifier recomputes it from the
stored stream records.
"""
from __future__ import annotations

import base64
import binascii
import html
import json
import re
import unicodedata
from urllib.parse import unquote

REDACTED = "[REDACTED]"
KNOWN_PREFIXES = ("sk-ant-",)
MAX_VIEWS = 512

_ESCAPE = re.compile(r"\\(u[0-9a-fA-F]{4}|U[0-9a-fA-F]{8}|x[0-9a-fA-F]{2}|[0-7]{1,3}|[\\/\"'bfnrt])")
_SIMPLE = {"\\": "\\", "/": "/", '"': '"', "'": "'", "b": "\b", "f": "\f", "n": "\n", "r": "\r", "t": "\t"}
_B64_CHUNK = re.compile(r"[A-Za-z0-9+/_\-]{12,}={0,2}")
# Base64 wrapped across lines (MIME / PEM style): runs of the alphabet joined by line breaks.
_B64_WRAPPED = re.compile(r"[A-Za-z0-9+/_\-]{2,}(?:[ \t]*\r?\n[ \t]*[A-Za-z0-9+/_\-]{2,})+={0,2}")
_HEX_CHUNK = re.compile(r"(?:[0-9a-fA-F]{2}){8,}")
_JSON_SPAN = re.compile(r"\{.*\}", re.S)


def needles_for(token=None):
    """The strings that must never appear: the token, its leading prefix, and the known prefixes."""
    needles = set(KNOWN_PREFIXES)
    if isinstance(token, str) and token:
        needles.add(token)
        if len(token) >= 16:
            needles.add(token[:max(10, min(16, len(token) // 2))])
    return frozenset(n for n in needles if n)


# ------------------------------------------------------------------ decoders (str -> str or None)

def _unescape(text):
    if "\\" not in text:
        return None
    def one(match):
        body = match.group(1)
        if body[0] in "uUx":
            try:
                return chr(int(body[1:], 16))
            except (ValueError, OverflowError):
                return match.group(0)
        if body[0] in "01234567":  # C / Python / shell octal escape, e.g. \157 == "o"
            return chr(int(body, 8))
        return _SIMPLE[body]
    return _ESCAPE.sub(one, text)


def _percent(text):
    return unquote(text.replace("+", " ")) if "%" in text else None


def _entities(text):
    return html.unescape(text) if "&" in text else None


def _nfkc(text):
    return unicodedata.normalize("NFKC", text)


def _bytes_text(data):
    return data.decode("utf-8", errors="ignore") + "\n" + data.decode("latin-1")


def _base64(text):
    out = []
    chunks = _B64_CHUNK.findall(text)
    chunks += [c for c in (re.sub(r"\s+", "", w) for w in _B64_WRAPPED.findall(text)) if len(c) >= 12]
    for chunk in chunks:
        body = chunk.rstrip("=").replace("-", "+").replace("_", "/")
        for offset in range(4):
            part = body[offset:]
            if len(part) % 4 == 1:
                part = part[:-1]
            part += "=" * (-len(part) % 4)
            if len(part) < 8:
                continue
            try:
                out.append(_bytes_text(base64.b64decode(part, validate=True)))
            except (binascii.Error, ValueError):
                continue
    return "\n".join(out) if out else None


def _hex(text):
    out = []
    for chunk in _HEX_CHUNK.findall(text):
        for offset in (0, 1):
            part = chunk[offset:]
            part = part[:len(part) - len(part) % 2]
            try:
                out.append(_bytes_text(bytes.fromhex(part)))
            except ValueError:
                continue
    return "\n".join(out) if out else None


DECODERS = (_unescape, _percent, _entities, _nfkc, _base64, _hex)


def decoded_views(text, limit=MAX_VIEWS):
    """Every view of ``text`` under compositions of the decoders, to a fixpoint. Returns
    ``(views, complete)``; ``complete`` is False when the bound was hit first."""
    seen, pending = {text}, [text]
    while pending:
        view = pending.pop()
        for decode in DECODERS:
            try:
                decoded = decode(view)
            except Exception:  # a decoder must never let a string through by crashing
                decoded = None
            if decoded is None or decoded in seen:
                continue
            if len(seen) >= limit:
                return seen, False
            seen.add(decoded)
            pending.append(decoded)
    return seen, True


def exposes(text, needles):
    """Does ``text`` contain a needle under any decoding (or fail to reach a fixpoint within bounds)?"""
    if not needles or not isinstance(text, str):
        return False
    folded = [n.casefold() for n in needles]
    views, complete = decoded_views(text)
    if not complete:
        return True
    return any(n in view.casefold() for view in views for n in folded)


def contains_secret(value, needles):
    """Recursive :func:`exposes` over dicts (keys too), lists and strings."""
    if isinstance(value, str):
        return exposes(value, needles)
    if isinstance(value, dict):
        return any(contains_secret(k, needles) or contains_secret(v, needles) for k, v in value.items())
    if isinstance(value, (list, tuple)):
        return any(contains_secret(v, needles) for v in value)
    return False


# ------------------------------------------------------------------ the sanitizer

def _replace_literal(text, needles):
    for needle in sorted(needles, key=len, reverse=True):
        text = re.sub(re.escape(needle), REDACTED, text, flags=re.I)
    return text


def _embedded_json(text, needles):
    """Sanitize JSON inside ``text`` structurally (whole value, else the ``{...}`` span)."""
    candidates = [(0, len(text))]
    match = _JSON_SPAN.search(text)
    if match and (match.start(), match.end()) != (0, len(text)):
        candidates.append(match.span())
    for start, end in candidates:
        chunk = text[start:end]
        if not chunk.strip()[:1] in ("{", "[", '"'):
            continue
        try:
            value = json.loads(chunk)
        except ValueError:
            continue
        if isinstance(value, (int, float, bool)) or value is None:
            continue
        clean = sanitize(value, needles)
        if clean != value:
            return text[:start] + json.dumps(clean, ensure_ascii=False) + text[end:]
    return text


def sanitize_text(text, needles):
    if not needles or not isinstance(text, str):
        return text
    out = _replace_literal(text, needles)
    out = _embedded_json(out, needles)
    return REDACTED if exposes(out, needles) else out


def sanitize(value, needles):
    """Recursively sanitize every string (dict keys included) of ``value``. Idempotent."""
    if isinstance(value, str):
        return sanitize_text(value, needles)
    if isinstance(value, dict):
        return {sanitize(k, needles): sanitize(v, needles) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [sanitize(v, needles) for v in value]
    return value


# ------------------------------------------------------------------ usage

USAGE_KEYS = ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens", "output_tokens")
INPUT_KEYS = USAGE_KEYS[:3]


def _record_usage(record):
    if type(record) is not dict:
        return None
    if record.get("type") == "result":
        usage = record.get("usage")
    elif record.get("type") == "assistant":
        message = record.get("message")
        usage = message.get("usage") if type(message) is dict else None
    else:
        return None
    return usage if type(usage) is dict else None


def stream_usage(records):
    """Field-wise MAX over every usage-bearing record (each result record and each assistant message).

    Only nonnegative ints count. A reported cache field without ``input_tokens`` implies 0 for it."""
    found = {}
    for record in records:
        usage = _record_usage(record)
        if usage is None:
            continue
        for key in USAGE_KEYS:
            value = usage.get(key)
            if type(value) is int and value >= 0:
                found[key] = max(found.get(key, 0), value)
    if found and "input_tokens" not in found and any(k in found for k in INPUT_KEYS[1:]):
        found["input_tokens"] = 0
    return {k: found[k] for k in USAGE_KEYS if k in found}


def usage_totals(usage):
    """``(input, output)`` counted from a :func:`stream_usage` dict; None where nothing was reported."""
    usage = usage if type(usage) is dict else {}
    has_input = any(k in usage for k in INPUT_KEYS)
    return (sum(usage.get(k, 0) for k in INPUT_KEYS) if has_input else None, usage.get("output_tokens"))


def records_from_raw(raw):
    """The JSON-decodable lines of a raw stream (undecodable lines are skipped)."""
    records = []
    for line in str(raw).splitlines():
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except ValueError:
            continue
    return records
