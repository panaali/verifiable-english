"""The OOM mutation record must show the seeded fault, not a stale checker binary."""
import json
from pathlib import Path


def test_python_mutants_reach_their_named_tests():
    evidence = Path(__file__).resolve().parents[1] / "docs/oom-rootcause/evidence/mutants.json"
    records = json.loads(evidence.read_text())
    python_records = [record for record in records if record["file"].startswith("ve/backends/")]
    assert len(python_records) == 5
    for record in python_records:
        excerpt = record["failure_excerpt"]
        assert "Rust executable hash mismatch" not in excerpt
        assert "FAILED " + record["test"] in excerpt
