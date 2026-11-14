"""The one helper every pinned-source test calls: the pinned publisher text of a use case, checked against its pin.

The text is read at build_document.DEFAULT_SOURCE (Path.home() / its path in usecases/pinned_sources.json; under
tools/gate.py the gate's own home, which the gate seeds from the account's). A text that is stored but is not its
pin fails with the reason. An absent text skips with SKIP_REASON (allowed by tools/gate-optional.json) unless
VE_REQUIRE_PINNED_SOURCES=1, which the Actions gate and nightly set after tools/fetch_pinned_sources.py: then it
fails with the reason.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from tools import fetch_pinned_sources as F

SKIP_REASON = F.SKIP_REASON


def pinned_source(doc: str, *, skip: bool = True, home: Path | None = None) -> Path | None:
    """The path of `doc`'s pinned text when it is stored at its pin. Absent and not required: skip the test, or
    return None with skip=False (the test then checks what needs no source). Absent and required, or stored with
    another hash or size: fail with the named reason."""
    entry = F.load()[doc]
    path = (Path.home() if home is None else home) / entry["path"]
    reason = F.problem(doc, entry, path)
    if reason is None:
        return path
    if path.is_file() or F.required():
        pytest.fail(f"{reason} ({F.REQUIRE}={'1' if F.required() else 'unset'}; "
                    "fetch it: uv run python tools/fetch_pinned_sources.py)")
    if skip:
        pytest.skip(SKIP_REASON)
    return None
