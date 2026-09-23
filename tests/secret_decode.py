"""Test-only, INDEPENDENT brute-force decoder (deliberately not ve.stream_audit's): does a secret
appear in a value under any composition of JSON parsing, unicode escapes, percent-encoding, HTML
entities, NFKC, base64/base64url and hex?"""
import base64
import binascii
import codecs
import html
import json
import re
import unicodedata
import warnings
from urllib.parse import unquote_plus

_RUN = re.compile(r"[A-Za-z0-9+/=_\-]{8,}")
_HEX = re.compile(r"[0-9a-fA-F]{16,}")


def _strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for k, v in value.items():
            yield from _strings(k)
            yield from _strings(v)
    elif isinstance(value, (list, tuple)):
        for v in value:
            yield from _strings(v)


def _decodings(text):
    out = []
    for attempt in (text, '"' + text + '"'):
        try:
            out.extend(_strings(json.loads(attempt)))
        except (ValueError, RecursionError):
            pass
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            out.append(codecs.decode(text.encode("latin-1", "backslashreplace"), "unicode_escape"))
    except (UnicodeDecodeError, ValueError):
        pass
    out += [unquote_plus(text), html.unescape(text), unicodedata.normalize("NFKC", text)]
    for run in _RUN.findall(text):
        run = run.replace("=", "")
        for start in range(4):
            part = run[start:]
            for alt in (part, part.replace("-", "+").replace("_", "/")):
                padded = alt + "=" * (-len(alt) % 4)
                for decode in (base64.b64decode, base64.urlsafe_b64decode):
                    try:
                        out.append(decode(padded).decode("utf-8", "ignore"))
                    except (binascii.Error, ValueError):
                        pass
    for run in _HEX.findall(text):
        for start in (0, 1):
            part = run[start:]
            try:
                out.append(bytes.fromhex(part[:len(part) // 2 * 2]).decode("utf-8", "ignore"))
            except ValueError:
                pass
    return out


def exposes_secret(value, secret, limit=4000):
    target = secret.casefold()
    for text in _strings(value if not isinstance(value, (bytes, bytearray)) else value.decode("utf-8", "ignore")):
        seen, pending = {text}, [text]
        while pending and len(seen) < limit:
            view = pending.pop()
            if target in view.casefold():
                return True
            for decoded in _decodings(view):
                if decoded not in seen:
                    seen.add(decoded)
                    pending.append(decoded)
    return False
