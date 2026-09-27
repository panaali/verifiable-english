import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("w2_dashboard", ROOT / "tools/coverage_dashboard.py")
dashboard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dashboard)


def test_baseline_is_tied_to_existing_audits():
    table = dashboard.baseline()
    assert "| news-article | 1 | 11 | 3 | 11 | 26 |" in table
    assert "17/19" in table
    assert "Art. I §7 has no audited pilot yet" in table


def test_pilot_partition_must_be_complete(tmp_path):
    for name in dashboard.AUDITS:
        target = tmp_path / "usecases" / name
        target.mkdir(parents=True)
        (target / "coverage.md").write_text((ROOT / "usecases" / name / "coverage.md").read_text())
    debate = tmp_path / "usecases/birthright-citizenship-debate"
    debate.mkdir()
    (debate / "coverage.md").write_text((ROOT / "usecases/birthright-citizenship-debate/coverage.md").read_text())
    pilot = tmp_path / "usecases/pilot"
    pilot.mkdir()
    (pilot / "coverage.json").write_text(json.dumps({"source_bytes": 5, "accounted_bytes": 4,
                                                       "residual_total": 0}))
    with pytest.raises(ValueError, match="partition coverage"):
        dashboard.baseline(tmp_path)
    (pilot / "coverage.json").write_text(json.dumps({"source_bytes": 5, "accounted_bytes": 5,
                                                       "residual_total": 2}))
    assert "| pilot | 5 | 5 | 2 |" in dashboard.baseline(tmp_path)
