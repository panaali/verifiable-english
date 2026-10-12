"""arch-AR-4 review F2: AR-4 moves the per-file trust tables out of the tree and into the gate record
(`tools/trust_map.py --files`), but no gate wrote them. Every gate, full or a rerun, now records them, checked
by their writer's schema (`trust_map.files_problems`); missing or malformed counts fail the gate."""
from __future__ import annotations

import pytest

from test_gate_integrity import trust_counts
from test_gate_rerun import fake  # noqa: F401  (the fixture)
from tools import gate


def test_every_gate_records_the_per_file_trust_counts(fake):
    """A full gate and a rerun both record what `tools/trust_map.py --files` measured."""
    code, record = fake.run()
    assert code == 1 and record["trust"] == trust_counts() and gate.TRUST_STAGE in fake.stages()
    fake.failing = set()
    code, record = fake.run("--rerun-failed")
    assert (code, record["status"], record["trust"]) == (0, "rerun-passed", trust_counts())
    code, record = fake.run()
    assert (code, record["status"], record["trust"]) == (0, "passed", trust_counts())


def _counts(change):
    counts = trust_counts()
    change(counts)
    return counts


@pytest.mark.parametrize("counts", [
    False, {}, [], 0, {**trust_counts(), "files": {}}, {**trust_counts(), "extra": 1},
    _counts(lambda c: c["files"]["VE/Demo.lean"].update(C=True)),
    _counts(lambda c: c["files"]["VE/Demo.lean"].update(C=-1)),
    _counts(lambda c: c["files"]["VE/Demo.lean"].pop("trusted")),
    _counts(lambda c: c["files"]["VE/Demo.lean"].update(trusted=4)),
    _counts(lambda c: c["budget"].update(V=1)),
    _counts(lambda c: c["files"].update({"VE/Demo.py": dict(c["files"]["VE/Demo.lean"])})),
], ids=["not written", "empty", "list", "zero", "no files", "extra key", "bool count", "negative count",
        "missing count", "totals disagree", "budget disagrees", "not a lean file"])
def test_a_gate_without_valid_trust_counts_fails(fake, counts):
    fake.failing, fake.trust = set(), counts
    code, record = fake.run()
    assert (code, record["status"]) == (1, "failed") and "trust" not in record
    assert any(failure["reason"].startswith(gate.TRUST_STAGE) for failure in record["failures"])
