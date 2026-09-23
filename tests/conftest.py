"""Guard: no test may make a real model or auditor call (C3, Opus re-review 2026-09-23).

Every test except those marked ``live`` runs with:
* ``subprocess.run`` / ``Popen`` / ``check_output`` refusing to start ``claude``, ``codex``, ``gemini`` or
  ``security`` (the keychain read that precedes a real Claude call);
* ``socket.socket.connect`` / ``connect_ex`` refusing any non-loopback address (Vertex, OpenRouter,
  Anthropic, OpenAI, Google auth...); tests that inject a fake backend client never reach a socket.

A refused call raises ``RealModelCall`` AND is recorded; the test then FAILS at teardown even if the code
under test caught the exception (``run_audit`` logs any auditor error, for example). Tests that fake a
binary patch ``subprocess.run`` themselves (after this guard), so their fakes still run.
"""
from __future__ import annotations

import os
import socket
import subprocess

import pytest

BLOCKED_BINARIES = {"claude", "codex", "gemini", "security"}


class RealModelCall(RuntimeError):
    pass


def _argv0(args, kwargs):
    argv = args[0] if args else kwargs.get("args")
    if isinstance(argv, (list, tuple)) and argv:
        return os.path.basename(str(argv[0]))
    if isinstance(argv, str):
        return os.path.basename(argv.split()[0]) if argv.split() else ""
    return ""


def _loopback(address):
    if not isinstance(address, tuple):
        return True  # AF_UNIX path
    host = str(address[0])
    return host in ("localhost", "::1") or host.startswith("127.")


@pytest.fixture(autouse=True)
def no_real_model_calls(request, monkeypatch):
    if request.node.get_closest_marker("live"):
        yield
        return
    seen = []

    def refuse(what):
        seen.append(what)
        raise RealModelCall(f"test attempted a real model/auditor call: {what}")

    def wrap(original):
        def guarded(*args, **kwargs):
            name = _argv0(args, kwargs)
            if name in BLOCKED_BINARIES:
                refuse(f"subprocess {name}")
            return original(*args, **kwargs)
        return guarded

    for name in ("run", "check_output", "Popen"):
        monkeypatch.setattr(subprocess, name, wrap(getattr(subprocess, name)))

    connect, connect_ex = socket.socket.connect, socket.socket.connect_ex

    def guarded_connect(self, address):
        if not _loopback(address):
            refuse(f"network connect {address!r}")
        return connect(self, address)

    def guarded_connect_ex(self, address):
        if not _loopback(address):
            refuse(f"network connect {address!r}")
        return connect_ex(self, address)

    monkeypatch.setattr(socket.socket, "connect", guarded_connect)
    monkeypatch.setattr(socket.socket, "connect_ex", guarded_connect_ex)
    yield
    if seen:
        pytest.fail("real model/auditor call(s) attempted: " + "; ".join(seen), pytrace=False)
