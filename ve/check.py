"""Acceptance records bind exact input bytes, AST, vocabulary and inventory.

This is experimental runtime checking, not a proof certificate or intent sign-off.
"""
from .ast import Document, check_document, document_from_data, document_to_data
from .errors import VEError
from .evaluate import evaluate
from .identity import meaning_id, source_id
from .parser import parse
from .printer import print_document


def check(env, source, model=None, *, candidate_ast=None, max_evaluations=1_000_000, trace=True, surface="strict"):
    paraphrase = None
    if surface == "english":
        from .english import parse_english_with_metadata
        parsed = parse_english_with_metadata(env, source)
        document, paraphrase = parsed.document, parsed.paraphrase()
    elif surface == "strict":
        document = parse(env, source)
    else:
        raise ValueError("surface must be strict or english")
    if candidate_ast is not None:
        candidate = (check_document(env, candidate_ast) if type(candidate_ast) is Document
                     else document_from_data(env, candidate_ast))
        if candidate != document:
            raise VEError("Submitted candidate AST does not match the exact parsed source")
    canonical = print_document(env, document)
    raw = source.encode("utf-8") if type(source) is str else source
    result = {"assurance": "experimental", "language": "accepted", "environment_id": env.environment_id,
              "source_id": source_id(source, env), "meaning_id": meaning_id(env, document),
              "ast": document_to_data(env, document), "canonical_text": canonical,
              "canonical": canonical.encode("ascii") == raw,
              "intent": "unconfirmed", "proof": "not_checked", "evaluation": "not_evaluated"}
    if paraphrase is not None:
        result["surface"] = "english"
        result["paraphrase"] = paraphrase
    if model is not None:
        evaluation = evaluate(env, document, model, max_evaluations=max_evaluations, trace=trace)
        result["model_id"] = model.model_id
        result["evaluation"] = evaluation.to_dict()
    return result
