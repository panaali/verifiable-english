"""VE v0 experimental language core. No general entailment certification yet."""
from .ast import (And, Binary, Bottom, Const, Document, Eq, Exists, Forall,
                  Formula, Implies, Not, Or, Term, Top, Unary, Var,
                  check_document, check_formula, doc_from_json,
                  document_from_data, document_to_data, formula_from_data,
                  formula_to_data)
from .environment import Environment
from .errors import VEError
from .identity import meaning_id, source_id

__version__ = "0.1.0"
