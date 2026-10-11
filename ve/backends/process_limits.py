"""Memory backstops for the checker processes VE starts.

On 2026-10-10 and 2026-10-11 one Rust `ve jsonl` search grew to 91 GB and then 99 GB. The kernel's
OOM kill took every job sharing its scope. The Rust binary now holds a memory budget of its own
(`rust/ve/src/memory.rs`), and each child also runs under an address-space limit (RLIMIT_AS), so a
runaway fails its own allocation instead of exhausting the machine. Its caller reads that as a
refusal (ResourceLimit from Rust's budget, CheckerUnavailable from a Lean runner that stopped),
never as an answer.
"""
from __future__ import annotations

import os
import resource
import subprocess

from ..errors import CheckerUnavailable


def configured_bytes(variable: str, default: int) -> int:
    """The number of bytes the environment variable `variable` sets, else `default`. A value that
    is not a positive decimal integer is refused, never replaced by the default."""
    text = os.environ.get(variable)
    if text is None:
        return default
    if not (text.isascii() and text.isdigit() and int(text) > 0):
        raise CheckerUnavailable(f"CheckerUnavailable: {variable} must be a positive number of bytes, "
                                 f"not {text!r}")
    return int(text)


def limit_address_space(pid: int, limit: int) -> None:
    """Cap the address space of the running child `pid` at `limit` bytes. This is set right after
    the start: a runaway grows over seconds, and preexec_fn is unsafe in a threaded client."""
    try:
        resource.prlimit(pid, resource.RLIMIT_AS, (limit, limit))
    except ProcessLookupError:
        pass  # it has already ended: nothing left to cap


def run_limited(argv, *, input: bytes, timeout: float, address_space: int) -> subprocess.CompletedProcess:
    """`subprocess.run(argv, input=input, capture_output=True, timeout=timeout)`, with the child
    under an `address_space` byte limit. A child that times out is killed, as `run` kills it."""
    with subprocess.Popen(argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE) as process:
        try:
            limit_address_space(process.pid, address_space)
            stdout, stderr = process.communicate(input, timeout=timeout)
        except BaseException:
            process.kill()
            raise
    return subprocess.CompletedProcess(argv, process.returncode, stdout, stderr)
