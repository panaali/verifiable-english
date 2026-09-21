"""VE v0 experimental language, finite semantics and checked argument API."""
from .ast import (And, Binary, Bottom, Const, Document, Eq, Exists, Forall,
                  Formula, Implies, Not, Or, Term, Top, Unary, Var,
                  check_document, check_formula, doc_from_json,
                  document_from_data, document_to_data, formula_from_data,
                  formula_to_data)
from .environment import Environment
from .errors import VEError
from .identity import meaning_id, source_id
from .parser import canonicalize, is_canonical, parse, parse_with_metadata
from .printer import (lint_vocabulary, measure_view_lengths, natural_document,
                      natural_formula, print_document, print_formula, render,
                      render_vocabulary)
from .fol import document_from_named_fol, document_to_named_fol, render_fol
from .model import FiniteModel
from .evaluate import evaluate
from .search import check_countermodel, find_countermodel, find_distinguishing_model
from .check import check
from .entailment import (EntailmentResult, EntailmentCertificateCheck,
                         prove_entailment, check_entailment_certificate)
from .argument import (Claim, Deduction, Evidence, ArgumentGraph, ArgumentResult,
                       check_argument, deduction_identity, outstanding_obligations,
                       predicate_use_panel)

__version__ = "0.1.0"
from .equivalence import (Budgets, ComparisonResult, DirectionResult, ReferenceValidation,
                          EQUIVALENT, DIFFERENT, UNKNOWN, compare, is_weaker, is_stronger,
                          in_two_variable_fragment, validate_reference)
