"""Regression checks for the CI-2 review's deferred-route claims."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_command_schema_and_entry_comments_name_only_delivered_bindings() -> None:
    schema = (ROOT / "lean/ResponseShape/Schemas/Command.lean").read_text()
    entry = (ROOT / "lean/VE/Commands/Run.lean").read_text()
    assert "The relay binds the id" not in schema
    assert "The generated shape binds id, unit and wording to the request" in schema
    assert "Relay binding of fills, spans, act and query is" in schema
    assert "the source wrapper both call it" not in entry
    assert "Source-wrapper integration is deferred to ci-2b" in entry
