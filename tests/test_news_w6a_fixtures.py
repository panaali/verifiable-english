"""Pinned news numeric inputs remain source-scoped and admission-only."""
from hashlib import sha256
import json
from pathlib import Path

from ve.environment import Environment
from ve.units import elaborate_quantity, render_coordinate

ROOT = Path(__file__).resolve().parents[1] / "usecases" / "news-article"


def test_news_quantity_fixtures():
    fixture = json.loads((ROOT / "w6a-quantity-fixtures.json").read_text())
    assert sha256((ROOT / "source.md").read_bytes()).hexdigest() == fixture["source_sha256"]
    env = Environment(fixture["environment"])
    coordinates = {}
    for case in fixture["cases"]:
        canonical, core = elaborate_quantity(env, {"format": "ve-quantity@1", "formula": case["formula"]})
        assert canonical["formula"] and core
        coordinates[case["id"]] = core
    assert coordinates["N07-lower"] == ["eq", ["const", "new_target_lower"], ["num", "375"]]
    assert coordinates["N07-upper"] == ["eq", ["const", "new_target_upper"], ["num", "400"]]
    assert coordinates["N21-september"][-1] == ["num", "370"]
    assert coordinates["N21-june"][-1] == ["num", "360"]
    assert coordinates["N22-year"][-1] == ["num", "2029"]
    assert [coordinates[x][-1] for x in ("N23-growth-old", "N23-growth-new",
                                            "N23-unemployment-old", "N23-unemployment-new")] == [
                                                ["num", "220"], ["num", "230"],
                                                ["num", "430"], ["num", "410"]]
    assert render_coordinate("bp", 375, env) == "3.75%"
    assert render_coordinate("calendar_year", 2029, env) == "calendar year 2029"
    assert {r["id"]: r["status"] for r in fixture["residuals"]} == {
        "N07b": "NO", "N08": "REIFIED", "N22b": "NO", "N23-slightly": "OPEN"}
