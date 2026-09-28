"""Domain-separated artifact bindings; identities never certify truth."""
import hashlib
from functools import lru_cache

from .ast import Document, document_to_data, formula_to_data
from .errors import SyntaxError
from .wire import canonical_json, digest


@lru_cache(maxsize=8192)
def _meaning_digest(version: str, environment_id: str, ast_bytes: bytes) -> str:
    # The cache key is canonical immutable wire content, never a mutable AST
    # container or an Environment object's identity.
    from .wire import loads_json
    return digest(f"ve-meaning-{version}\n",
                  {"environment_id": environment_id, "ast": loads_json(ast_bytes)})


def source_id(source: str | bytes, env=None) -> str:
    try:
        raw = source.encode("utf-8") if isinstance(source, str) else source
        if type(raw) is not bytes:
            raise SyntaxError("Source must be str or bytes")
        return hashlib.sha256(f"ve-source-{env.identity_version if env is not None else 'v0'}\n".encode("ascii") + raw).hexdigest()
    except UnicodeError as exc:
        raise SyntaxError("Source is not valid Unicode") from exc


def meaning_id(env, document_or_formula, *, _generated=False) -> str:
    ast = (document_to_data(env, document_or_formula) if type(document_or_formula) is Document
           else formula_to_data(env, document_or_formula, _generated=_generated))
    return _meaning_digest(env.identity_version, env.environment_id, canonical_json(ast))
