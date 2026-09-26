"""nary@0 wire and type checks, including repeated argument positions."""
import pytest

from ve.ast import Atom, Const, Document, Not, formula_from_data, formula_to_data
from ve.environment import Environment
from ve.english import parse_english, render_english
from ve.errors import InvalidModel, SyntaxError, TypeMismatch, UnknownSymbol, VEError
from ve.evaluate import evaluate
from ve.model import FiniteModel
from ve.parser import parse
from ve.printer import print_document
from ve.printer import lint_vocabulary
from ve.profiles import LANGUAGE, SPEC_REVISION
from ve.search import check_countermodel


def environment(arity=3):
    return Environment({
        "language": LANGUAGE,
        "profiles": ["closure@0", "nary@0", "relational-fol@0"],
        "spec_revision": SPEC_REVISION,
        "vocabulary": {
            "sorts": {"s": {"description": "S"}, "t": {"description": "T"}},
            "predicates": {"p": {"arguments": ["s"] * (arity - 1) + ["t"],
                                 "description": "P"}},
            "constants": {"a": {"sort": "s", "description": "A"},
                          "b": {"sort": "t", "description": "B"}},
        },
    })


def test_atom_wire_repeated_arguments():
    env = environment()
    node = Atom("p", (Const("a"), Const("a"), Const("b")))
    wire = ["atom", "p", [["const", "a"], ["const", "a"], ["const", "b"]]]
    assert formula_to_data(env, node) == wire
    assert formula_from_data(env, wire) == node
    doc = Document((node,))
    assert print_document(env, doc) == "p(@a, @a, @b).\n"
    assert parse(env, print_document(env, doc)) == doc


@pytest.mark.parametrize("wire,error", [
    (["atom", "p", [["const", "a"]] * 2], SyntaxError),
    (["atom", "p", [["const", "a"]] * 7], SyntaxError),
    (["atom", "p", "not-an-array"], SyntaxError),
    (["atom", "p", [["const", "a"], ["const", "a"], ["const", "a"]]], TypeMismatch),
    (["atom", "p", [["const", "a"], ["const", "a"], ["const", "missing"]]], UnknownSymbol),
])
def test_hostile_wire(wire, error):
    with pytest.raises(error):
        formula_from_data(environment(), wire)


def test_environment_arity_cap_and_unknown_third_sort():
    assert len(environment(6).predicates["p"].arguments) == 6
    with pytest.raises(VEError):
        environment(7)
    data = environment().to_dict()
    data["vocabulary"]["predicates"]["p"]["arguments"][2] = "missing"
    with pytest.raises(UnknownSymbol):
        Environment(data)


def test_finite_model_and_countermodel_with_nary_relation():
    env = environment()
    model = FiniteModel.from_dict(env, {
        "complete": True,
        "domains": {"s": ["x"], "t": ["y"]},
        "constants": {"a": "x", "b": "y"},
        "relations": {"p": [["x", "x", "y"]]},
    })
    atom = Atom("p", (Const("a"), Const("a"), Const("b")))
    assert evaluate(env, atom, model).value is True
    assert check_countermodel(env, [atom], Not(atom), model).valid
    with pytest.raises(InvalidModel):
        FiniteModel.from_dict(env, {**model.to_dict(), "relations": {"p": [["x", "y", "x"]]}})


def test_english_template_round_trip_and_lint():
    raw = environment().to_dict()
    raw["vocabulary"]["predicates"]["p"]["verbalisation"] = "{0} reports {1} to {2}"
    env = Environment(raw)
    atom = Atom("p", (Const("a"), Const("a"), Const("b")))
    rendered = render_english(Document((atom,)), env)
    assert parse_english(env, rendered) == Document((atom,))
    assert not lint_vocabulary(env)
    raw["vocabulary"]["predicates"]["p"]["verbalisation"] = "{0} reports {2} to {1}"
    assert {i.code for i in lint_vocabulary(Environment(raw))} == {"TEMPLATE_SHAPE"}


def test_fret_user_sort_time_and_arity_six():
    raw = environment(6).to_dict()
    raw["vocabulary"]["sorts"]["time"] = {"description": "Time"}
    raw["vocabulary"]["predicates"]["p"]["arguments"][1] = "time"
    raw["vocabulary"]["constants"]["clock"] = {"sort": "time", "description": "Clock"}
    env = Environment(raw)
    atom = Atom("p", (Const("a"), Const("clock"), Const("a"),
                      Const("a"), Const("a"), Const("b")))
    assert parse(env, print_document(env, Document((atom,)))) == Document((atom,))
