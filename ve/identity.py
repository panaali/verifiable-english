"""Domain-separated artifact bindings; identities never certify truth."""
import hashlib

from .ast import Document, document_to_data, formula_to_data
from .errors import SyntaxError
from .wire import digest


def source_id(source: str | bytes, env=None) -> str:
    try:
        raw = source.encode("utf-8") if isinstance(source, str) else source
        if type(raw) is not bytes:
            raise SyntaxError("Source must be str or bytes")
        return hashlib.sha256(f"ve-source-{env.identity_version if env is not None else 'v0'}\n".encode("ascii") + raw).hexdigest()
    except UnicodeError as exc:
        raise SyntaxError("Source is not valid Unicode") from exc


def meaning_id(env, document_or_formula) -> str:
    ast = (document_to_data(env, document_or_formula) if type(document_or_formula) is Document
           else formula_to_data(env, document_or_formula))
    return digest(f"ve-meaning-{env.identity_version}\n", {"environment_id": env.environment_id, "ast": ast})
