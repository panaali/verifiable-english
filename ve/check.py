"""Acceptance records bind exact input bytes, AST, vocabulary and inventory.

This is experimental runtime checking, not a proof certificate or intent sign-off.
"""
from .ast import Document, check_document, document_from_data, document_to_data
from .errors import VEError
from .evaluate import evaluate
from .identity import meaning_id, source_id
from .parser import parse
from .printer import print_document


def check(env, source, model=None, *, candidate_ast=None, max_evaluations=1_000_000):
    document = parse(env, source)
    if candidate_ast is not None:
        candidate = (check_document(env, candidate_ast) if type(candidate_ast) is Document
                     else document_from_data(env, candidate_ast))
        if candidate != document:
            raise VEError("Submitted candidate AST does not match the exact parsed source")
    canonical = print_document(env, document)
    raw = source.encode("ascii") if type(source) is str else source
    result = {"assurance": "experimental", "language": "accepted", "environment_id": env.environment_id,
              "source_id": source_id(source), "meaning_id": meaning_id(env, document),
              "ast": document_to_data(env, document), "canonical_text": canonical,
              "canonical": canonical.encode("ascii") == raw,
              "intent": "unconfirmed", "proof": "not_checked", "evaluation": "not_evaluated"}
    if model is not None:
        evaluation = evaluate(env, document, model, max_evaluations=max_evaluations)
        result["model_id"] = model.model_id
        result["evaluation"] = evaluation.to_dict()
    return result
