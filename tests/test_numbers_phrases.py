"""The existing English reader consumes the Lean-generated comparison rows."""
import json
from pathlib import Path

from ve import ast
from ve.english import _COMPARISONS


def test_comparison_rows_match_generated_table():
    path = Path(__file__).resolve().parents[1] / "ve/numbers_phrases.json"
    rows = json.loads(path.read_text())
    operators = {"eq": ast.Eq, "lt": ast.Lt, "le": ast.Le}
    assert _COMPARISONS == tuple(
        (row["text"], operators[row["rel"]], row["swap"]) for row in rows
    )
    assert len(rows) == 4
    assert len({row["text"] for row in rows}) == 4
    assert rows == [
        {"rel": "lt", "swap": False, "text": "{0} is less than {1}"},
        {"rel": "le", "swap": False, "text": "{0} is at most {1}"},
        {"rel": "lt", "swap": True, "text": "{0} is more than {1}"},
        {"rel": "le", "swap": True, "text": "{0} is at least {1}"},
    ]
