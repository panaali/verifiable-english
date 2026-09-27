"""Stage 0 inventory policy must survive regeneration on another checkout."""
import json

from tools import semantic_inventory as inventory


def test_external_scan_excludes_cloned_core_and_uses_portable_labels():
    sources = inventory.read_sources()
    labels = [inventory.source_label(path) for path in sources]
    assert all(not label.startswith("/home/") for label in labels)
    snapshot = json.loads(inventory.EXTERNAL_SNAPSHOT.read_text())
    external = [item["path"] for item in snapshot["files"]]
    assert external and all(label.startswith("external:") for label in external)
    assert not any("/ve/" in label or "/tests/" in label for label in external)
    assert not any(label.startswith("/home/") for label, *_ in snapshot["edges"])


def test_semantic_combinations_have_explicit_ownership():
    report = inventory.generate()
    for module, symbol, owner in (("readings", "validate_reading_sets", "Lean `readings`"),
                                  ("readings", "check_readings", "Lean `readings`"),
                                  ("equivalence", "validate_reference", "Trusted narrowed"),
                                  ("document", "check_document", "Trusted narrowed")):
        row = next(line for line in report.splitlines()
                   if line.startswith(f"| `ve/{module}.py` | `{symbol}` |"))
        assert "| S |" not in row
        assert owner in row
    assert "`unresolved_obligations`; Lean `graph`" in report
