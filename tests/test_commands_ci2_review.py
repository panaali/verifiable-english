"""Regression checks for the CI-2 review's route claims: each comment names only bindings that are delivered (the
relay's binding and the source wrapper's call landed in ci-2b)."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_command_schema_and_entry_comments_name_only_delivered_bindings() -> None:
    schema = (ROOT / "lean/ResponseShape/Schemas/Command.lean").read_text()
    entry = (ROOT / "lean/VE/Commands/Run.lean").read_text()
    assert "The relay binds the id" not in schema
    assert "The generated shape binds id, unit and wording to the request" in schema
    assert "the relay binds the act, the fills, their spans,\nthe query" in schema
    assert "deferred to ci-2b" not in schema + entry
    assert "the `english.command` mode and the source wrapper both call it" in entry
