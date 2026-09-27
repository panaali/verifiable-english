"""Keep wall-clock limits out of semantic test outcomes under CPU contention."""

import pytest

from ve import argument, bundle
from ve.surface import unambiguity


@pytest.fixture(autouse=True)
def generous_hang_guards(monkeypatch):
    # Deadline tests install their own deterministic clock and budget.
    # All production defaults and semantic work limits remain unchanged.
    monkeypatch.setattr(unambiguity, "EARLEY_SECONDS", 1800)
    monkeypatch.setattr(argument, "LEAN_REPLAY_TIMEOUT", 1800)
    monkeypatch.setattr(bundle, "LEAN_REPLAY_TIMEOUT", 1800)
    monkeypatch.setenv("VE_CONFORMANCE_HANG_TIMEOUT", "1800")
