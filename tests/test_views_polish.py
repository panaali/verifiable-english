"""Review regressions: lexical limits, shared scopes, cells, and measurements."""
import json
from pathlib import Path
import random
import re

import pytest

from ve import (And, Binary, Const, Document, Environment, Eq, Exists, Forall,
                Implies, Not, Top, Unary, Var, lint_vocabulary, render,
                render_vocabulary, formula_to_data, document_to_data)
from ve.fluent import contraction_stats
from ve.printer import (VIEWS, measure_jsonl_lengths, measure_view_lengths,
                        render_cell)
from explicit_inverse import parse_explicit
from fluent_inverse import parse_fluent
from test_fluent import negative_vocabulary
from test_views import ENV, _random_formula, vocabulary


@pytest.mark.parametrize("word", "nothing nobody everything everybody just solely only many several another but plus all most few always never may might must can".split())
def test_quantity_exclusivity_and_modal_words_cannot_enter_templates(word):
    data = vocabulary()
    data["vocabulary"]["predicates"]["owns"]["verbalisation"] = "{0} owns " + word + " {1}"
    env = Environment(data)
    assert any(i.code == "LOGICAL_WORD" for i in lint_vocabulary(env))
    assert render(Binary("owns", Const("alice"), Const("api")), env, "ve_fluent") == "@alice owns @api"


@pytest.mark.parametrize("noun", ["service", "services", "person", "people", "item", "agent", "fleet service", "fleet services"])
def test_templates_must_not_mention_any_declared_sort_noun(noun):
    data = vocabulary()
    data["vocabulary"]["sorts"]["fleet"] = {
        "description": "Fleet", "verbalisation": {"singular": "fleet service", "plural": "fleet services"}}
    data["vocabulary"]["predicates"]["owns"]["verbalisation"] = "{0} owns " + noun + " {1}"
    env = Environment(data)
    assert any(i.code == "SORT_NOUN" and "/owns/" in i.path for i in lint_vocabulary(env))


@pytest.mark.parametrize("phrase,accepted", [
    ("{0} owns " + "b" * 67 + " {1}", True),  # exactly 80 characters
    ("{0} owns " + "b" * 68 + " {1}", False),
    ("{0} owns red red red red red {1}", True),  # exactly 8 words incl. placeholders
    ("{0} owns red red red red red red {1}", False),
])
def test_template_length_boundaries(phrase, accepted):
    data = vocabulary()
    data["vocabulary"]["predicates"]["owns"]["verbalisation"] = phrase
    env = Environment(data)
    assert any(i.code == "TEMPLATE_LENGTH" for i in lint_vocabulary(env)) != accepted
    legend = json.loads(render_vocabulary(env))
    entry = next(p for p in legend["predicates"] if p["identifier"] == "owns")
    assert (entry["rendered_template"] == phrase) == accepted


def test_negative_template_length_cap_also_applies():
    data = vocabulary()
    entry = data["vocabulary"]["predicates"]["owns"]
    entry["verbalisation"] = "{0} owns " + "b" * 64 + " {1}"
    entry["negative_verbalisation"] = "{0} does not own " + "b" * 64 + " {1}"
    env = Environment(data)
    assert any(i.code == "TEMPLATE_LENGTH" and i.path.endswith("negative_verbalisation")
               for i in lint_vocabulary(env))
    assert render(Not(Binary("owns", Const("alice"), Const("api"))), env, "ve_fluent").startswith("it is false that ")


@pytest.mark.parametrize("alias", ["precedes", "disowns"])
def test_lexical_semantic_limit_is_visible_in_required_cell(alias):
    data = vocabulary()
    entry = data["vocabulary"]["predicates"]["owns"]
    entry["verbalisation"] = "{0} " + alias + " {1}"
    env = Environment(data)
    assert not lint_vocabulary(env)  # A lexical check cannot establish equivalence.
    cell = render_cell(Binary("owns", Const("alice"), Const("api")), env, "ve_fluent")
    assert '"identifier": "owns"' in cell and alias in cell


@pytest.mark.parametrize("naming", ["per_statement", "per_document"])
def test_all_views_use_one_naming_scope_and_cells_always_include_legend(naming):
    formula = Forall("item", Exists("item", Eq(Var(0), Var(1))))
    document = Document((formula, formula))
    legends = {render_vocabulary(ENV, view, naming) for view in VIEWS}
    assert len(legends) == 1
    legend = legends.pop()
    assert json.loads(legend)["naming"] == naming
    for view in VIEWS:
        text = render(document, ENV, view, naming)
        lines = text.splitlines()
        assert (lines[0] == lines[1]) == (naming == "per_statement")
        if naming == "per_document":
            assert ("S3" if view == "ve_fluent" else "x2") in lines[1]
        for line in lines:
            assert (parse_fluent(ENV, line[:-1]) if view == "ve_fluent" else
                    parse_explicit(ENV, line[:-1], view)) == formula
        assert render_cell(document, ENV, view, naming) == legend + text
        assert render_cell(formula, ENV, view, naming) == legend + render(formula, ENV, view, naming)
        assert render(document, ENV, view) == render(document, ENV, view, "per_statement")
        with pytest.raises(ValueError, match="naming"):
            render(document, ENV, view, "unknown")


def test_a_i_o_and_all_identifier_categories_are_reserved_case_insensitively():
    data = vocabulary()
    data["vocabulary"]["sorts"] = {name: {"description": name}
                                    for name in ("apple", "island", "object", "e", "u")}
    data["vocabulary"]["predicates"] = {"p": {"description": "P", "arguments": ["apple"]}}
    data["vocabulary"]["constants"] = {"s": {"description": "S", "sort": "island"},
                                         "b2": {"description": "B2", "sort": "object"}}
    env = Environment(data)
    letters = json.loads(render_vocabulary(env))["fluent_variables"]["letters_by_sort"]
    assert letters == {"apple": "L", "e": "C", "island": "N", "object": "J", "u": "D"}
    assert all(not set(code).intersection("AIO") for code in letters.values())
    for sort in env.sorts:
        formula = Forall(sort, Eq(Var(0), Var(0)))
        assert parse_fluent(env, render(formula, env, "ve_fluent")) == formula


@pytest.mark.parametrize("finite,base", [
    ("admires", "admire"), ("watches", "watch"), ("washes", "wash"),
    ("passes", "pass"), ("fixes", "fix"), ("buzzes", "buzz"), ("carries", "carry"),
    ("studies", "study"), ("plays", "play"), ("uses", "use"), ("houses", "house"),
    ("has", "have"), ("goes", "go"), ("ties", "tie"), ("lies", "lie"),
    ("dies", "die"), ("quizzes", "quiz"), ("focuses", "focus"), ("echoes", "echo"),
    ("vies", "vie"), ("aches", "ache"), ("caches", "cache"), ("niches", "niche"),
    ("axes", "axe"), ("shoes", "shoe"), ("toes", "toe"), ("tiptoes", "tiptoe"),
])
def test_mechanical_negatives_roundtrip_in_atoms_and_relative_guards(finite, base):
    data = vocabulary()
    data["vocabulary"]["predicates"] = {"relation": {
        "arguments": ["item", "item"], "description": "Relation",
        "verbalisation": f"{{0}} {finite} {{1}}",
        "negative_verbalisation": f"{{0}} does not {base} {{1}}"}}
    env = Environment(data)
    assert not lint_vocabulary(env)
    formula = Forall("item", Implies(Not(Binary("relation", Var(0), Const("api"))), Top()))
    text = render(formula, env, "ve_fluent")
    assert f"that does not {base} @api" in text
    assert parse_fluent(env, text) == formula


@pytest.mark.parametrize("finite,base", [("foos", "fooey"), ("outdoes", "outdo")])
def test_unsupported_inflection_keeps_explicit_negation(finite, base):
    data = vocabulary()
    data["vocabulary"]["predicates"]["owns"].update(
        verbalisation=f"{{0}} {finite} {{1}}", negative_verbalisation=f"{{0}} does not {base} {{1}}")
    env = Environment(data)
    assert any(i.code == "NEGATIVE_NOT_NEGATION" for i in lint_vocabulary(env))
    text = render(Not(Binary("owns", Const("alice"), Const("api"))), env, "ve_fluent")
    assert text == f"it is false that @alice {finite} @api"
    assert parse_fluent(env, text) == Not(Binary("owns", Const("alice"), Const("api")))


def test_contraction_counts_match_emitted_guard_and_negative_forms():
    env = Environment(negative_vocabulary())
    p, q = Unary("active", Var(0)), Not(Unary("reviewed", Var(0)))
    object_guard = Binary("links", Const("api"), Var(0))
    forms = [p, And(p, q), And(p, And(p, q)), object_guard, And(p, object_guard)]
    formulas = [Forall("item", Implies(g, q)) for g in forms]
    formulas += [Not(Not(Unary("reviewed", Const("api")))),
                 Not(Eq(Const("api"), Const("api"))), Not(Top())]
    counts = contraction_stats([Document(tuple(formulas))], env)
    assert counts["guards"] == counts["universal_groups"] == 5
    assert counts["relative_guards"] == 2
    assert counts["structural_guards"] == 3
    assert counts["structural_both_guards"] == 2
    assert counts["negations"] == 11
    assert counts["whitelisted_negations"] == 8
    assert counts["equality_negations"] == 1
    assert counts["fallback_negations"] == 2
    assert counts["relative_guards_share"] == 2 / 5
    text = render(Document(tuple(formulas)), env, "ve_fluent")
    assert text.count("such that (both ") == counts["structural_both_guards"]
    assert text.count("it is false that ") == counts["fallback_negations"]
    assert contraction_stats([], env)["whitelisted_negations_share"] == 0.0


def test_seeded_random_negation_and_contraction_sample():
    rng = random.Random(20260921)
    items = [_random_formula(rng, rng.randrange(1, 7)) for _ in range(2000)]
    env = Environment(negative_vocabulary())
    counts = contraction_stats(items, env)
    texts = [render(item, env, "ve_fluent") for item in items]
    assert counts["fallback_negations"] == sum(t.count("it is false that ") for t in texts)
    assert counts["negations"] == sum(counts[k] for k in (
        "whitelisted_negations", "fallback_negations", "equality_negations"))
    assert counts["structural_both_guards"] == sum(t.count("such that (both ") for t in texts)
    print(json.dumps({"seed": 20260921, "draws": 2000, "stats": counts}, sort_keys=True))


@pytest.mark.parametrize("source_format", ["ast", "ve"])
@pytest.mark.parametrize("naming", ["per_statement", "per_document"])
def test_jsonl_lengths_measure_real_record_text(tmp_path, source_format, naming):
    formula = Forall("item", Eq(Var(0), Var(0)))
    items = [formula, Document((formula, formula))]
    path = tmp_path / "items.jsonl"
    records = []
    for index, item in enumerate(items):
        value = (render(Document((item,)) if index == 0 else item, ENV)
                 if source_format == "ve" else
                 formula_to_data(ENV, item) if index == 0 else document_to_data(ENV, item))
        records.append({"id": f"item-{index}", "payload": value, "environment_id": ENV.environment_id,
                        "score": 0.5, "label": None})
    path.write_text("\n".join(json.dumps(record) for record in records) + "\n")
    rows = measure_jsonl_lengths(path, ENV, field="payload", source_format=source_format, naming=naming)
    assert len(rows) == 10
    for row in rows:
        index = row["item_index"]
        item = Document((items[0],)) if source_format == "ve" and index == 0 else items[index]
        text = render_cell(item, ENV, row["view"], naming)
        assert row["characters"] == len(text)
        assert row["tokenish"] == len(re.findall(r"\w+|[^\w\s]", text))
        assert row["line"] == index + 1 and row["item_id"] == f"item-{index}"


@pytest.mark.parametrize("record", ['{}', '{"ast": ["unknown"]}', '',
                                     '{"ast": ["top"], "environment_id": "wrong"}',
                                     '{"ast": ["top"], "ast": ["bottom"]}',
                                     '{"ast": ["top"], "score": NaN}'])
def test_jsonl_does_not_silently_drop_invalid_items(tmp_path, record):
    path = tmp_path / "items.jsonl"
    path.write_text('{"ast": ["top"]}\n' + record + '\n')
    with pytest.raises(ValueError):
        measure_jsonl_lengths(path, ENV)


def test_committed_item_file_lengths_and_example_documentation():
    import runpy
    root = Path(__file__).resolve().parents[1]
    env = Environment.from_json((root / "examples/fluent/environment.json").read_bytes())
    rows = measure_jsonl_lengths(root / "tests/data/fluent-items.jsonl", env,
                                 field="claim", source_format="ve")
    assert len(rows) == 30
    assert {row["item_id"] for row in rows} == {f"fluent-{i}" for i in range(1, 7)}
    assert all(row["includes_vocabulary"] for row in rows)
    # The legacy example generator lives outside the authorized edit scope.
    # Its outputs are current; correct only its old naming-policy sentence.
    text = runpy.run_path(str(root / "examples/fluent_views.py"))["report"]()
    text = text.replace("are unique across statements.",
                        "restart in each statement under the default naming policy.")
    assert (root / "docs/fluent-examples.md").read_text() == text
