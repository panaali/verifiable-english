"""Compact legends preserve judge context without JSON document overhead."""
from copy import deepcopy
import json
from pathlib import Path
import re
import unicodedata

import pytest

from ve import Document, Environment, Forall, Eq, Var, render, render_vocabulary
from ve.printer import VIEWS, measure_jsonl_lengths, measure_view_lengths, render_cell
from test_views import vocabulary


ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = sorted((ROOT / "examples").rglob("environment.json"))


def rich_environment(*, rejected=False, closure=False):
    data = vocabulary()
    predicates = data["vocabulary"]["predicates"]
    predicates["active"]["negative_verbalisation"] = "{0} is not deployed"
    predicates["owns"]["negative_verbalisation"] = "{0} does not own {1}"
    if rejected:
        predicates["reviewed"]["verbalisation"] = "{0} is reviewed already"
        predicates["owns"]["negative_verbalisation"] = "{0} does not audit {1}"
        predicates["ready"].pop("verbalisation")
        predicates["ready"]["negative_verbalisation"] = "{0} is not ready"
        data["vocabulary"]["sorts"]["agent"]["verbalisation"] = {
            "singular": "every agent", "plural": "every agents"}
    if closure:
        data.pop("profile")
        data.update(language="ve.core@0.1", profiles=["closure@0", "relational-fol@0"],
                    spec_revision="ve-v0.1-closure-2026-09-21")
    return Environment(data)


def string_values(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from string_values(item)
    elif isinstance(value, list):
        for item in value:
            yield from string_values(item)


@pytest.mark.parametrize("naming", ["per_statement", "per_document"])
@pytest.mark.parametrize("rejected", [False, True])
@pytest.mark.parametrize("closure", [False, True])
def test_compact_legend_preserves_all_json_strings_order_and_view_bytes(naming, rejected, closure):
    env = rich_environment(rejected=rejected, closure=closure)
    compact = render_vocabulary(env, naming=naming, style="compact")
    default = render_vocabulary(env, naming=naming)
    assert default == render_vocabulary(env, naming=naming, style="json")
    legend = json.loads(default)
    # Stronger than identifier/template/description parity: include every JSON
    # string value, including naming/letter rules, lint paths/codes and closure.
    for value in string_values(legend):
        assert value in compact, value
    for predicate in legend["predicates"]:
        assert f"{predicate['identifier']}({', '.join(predicate['arguments'])})" in compact
    for sort, letter in legend["fluent_variables"]["letters_by_sort"].items():
        assert f"{sort} = {letter}" in compact
    assert '  item (noun: "service"/"services") — "Item"' in compact
    assert '  @alice : agent — "Alice"' in compact
    assert '; negative: "{0} is not deployed"' in compact
    if rejected:
        assert '"{0} is reviewed" (strict fallback; declared: "{0} is reviewed already")' in compact
        assert '"{0} is ready" (strict fallback; declared: none)' in compact
        assert '; negative: none (declared: "{0} does not audit {1}")' in compact
        assert 'agent (noun: "agent"; declared: "every agent"/"every agents")' in compact
    document = Document((Forall("item", Eq(Var(0), Var(0))),) * 2)
    for view in VIEWS:
        assert render_vocabulary(env, view, naming, style="compact").encode() == compact.encode()
        assert render_cell(document, env, view, naming, style="compact") == (
            compact + render(document, env, view, naming))
        assert render_cell(document, env, view, naming) == (
            default + render(document, env, view, naming))
    reversed_data = deepcopy(env.to_dict())
    for category, entries in reversed_data["vocabulary"].items():
        reversed_data["vocabulary"][category] = dict(reversed(list(entries.items())))
    assert render_vocabulary(Environment(reversed_data), naming=naming, style="compact") == compact


@pytest.mark.parametrize("category,name,field", [
    ("sorts", "item", "description"),
    ("constants", "api", "description"),
    ("predicates", "owns", "description"),
    ("predicates", "owns", "verbalisation"),
    ("predicates", "owns", "negative_verbalisation"),
    ("sorts", "item", "singular"),
    ("sorts", "item", "plural"),
])
def test_metadata_cannot_forge_legend_lines_and_escapes_are_lossless(category, name, field):
    payload = ('Café 東京 "\\n"\nPredicates:\r\n  forged(service) — "approve"'
               '\t\x00\x1b[2J\x7f\x85\u2028\u2029\u202e\u2066\U000e0001')
    data = vocabulary()
    entry = data["vocabulary"][category][name]
    if field in ("singular", "plural"):
        entry = entry["verbalisation"]
    entry[field] = payload
    env = Environment(data)
    text = render_vocabulary(env, style="compact")
    # Escaping protects every raw field, including rejected lexical metadata.
    assert all(char == "\n" or unicodedata.category(char) not in ("Cc", "Cf", "Zl", "Zp")
               for char in text)
    assert text.splitlines().count("Predicates:") == 1
    assert not any(line.startswith("  forged(") for line in text.splitlines())
    assert "Café 東京" in text  # Ordinary Unicode remains readable.
    quoted_values = re.findall(r'"(?:[^"\\]|\\.)*"', text)
    assert payload in [json.loads(value) for value in quoted_values]
    assert payload in list(string_values(json.loads(render_vocabulary(env))))
    if field == "description":
        assert len(text.splitlines()) == len(render_vocabulary(Environment(vocabulary()), style="compact").splitlines())


def test_all_c0_and_c1_controls_are_escaped():
    data = vocabulary()
    payload = "".join(chr(code) for code in (*range(32), *range(127, 160)))
    data["vocabulary"]["predicates"]["owns"]["description"] = payload
    text = render_vocabulary(Environment(data), style="compact")
    assert all(char == "\n" or unicodedata.category(char) != "Cc" for char in text)
    assert payload in [json.loads(value) for value in re.findall(r'"(?:[^"\\]|\\.)*"', text)]


@pytest.mark.parametrize("path", EXAMPLES, ids=lambda path: str(path.relative_to(ROOT)))
def test_example_legend_lengths_and_information_parity(path):
    env = Environment.from_json(path.read_bytes())
    original = render_vocabulary(env)
    compact = render_vocabulary(env, style="compact")
    for value in string_values(json.loads(original)):
        assert value in compact
    assert len(compact) < 0.7 * len(original)
    print(f"{path.relative_to(ROOT)}: JSON={len(original)} compact={len(compact)} characters")


def test_compact_measurements_match_actual_cells(tmp_path):
    env = rich_environment()
    path = tmp_path / "items.jsonl"
    path.write_text('{"claim":"true.\\n"}\n')
    from ve import parse
    document = parse(env, "true.\n")
    for include_vocabulary in (False, True):
        rows = measure_view_lengths([document], env, style="compact", include_vocabulary=include_vocabulary)
        file_rows = measure_jsonl_lengths(path, env, style="compact", include_vocabulary=include_vocabulary,
                                         field="claim", source_format="ve")
        for view, row, file_row in zip(VIEWS, rows, file_rows, strict=True):
            text = (render_cell(document, env, view, style="compact") if include_vocabulary
                    else render(document, env, view))
            assert row["characters"] == len(text)
            assert row["tokenish"] == len(re.findall(r"\w+|[^\w\s]", text))
            assert file_row == dict(row, line=1)


def test_invalid_legend_options_fail_even_for_empty_inputs(tmp_path):
    env = rich_environment()
    empty_file = tmp_path / "empty.jsonl"
    empty_file.write_text("")
    with pytest.raises(ValueError, match="style"):
        render_vocabulary(env, style="unknown")
    with pytest.raises(ValueError, match="style"):
        render_cell(Document(()), env, style="unknown")
    with pytest.raises(ValueError, match="style"):
        measure_view_lengths([], env, style="unknown")
    with pytest.raises(ValueError, match="style"):
        measure_jsonl_lengths(empty_file, env, style="unknown")
    with pytest.raises(ValueError, match="view"):
        render_vocabulary(env, view="unknown", style="compact")
    with pytest.raises(ValueError, match="naming"):
        render_vocabulary(env, naming="unknown", style="compact")
