"""The progress watch that tells a hung child from a slow one (`subprocesses.run_while_progressing`).

The x86 nightly of 2026-10-15 stopped `tests/test_difffuzz.py::test_ci_run` at its fixed HANG_TIMEOUT
wall wait while the CI run was still working through its third surface: under that load it needed more
than 1,800 s for what it does in about 3 minutes alone. The watch stops a child only when its progress
stops for HANG_TIMEOUT or it runs past a cap far above it. The rules are tested on the clock's values
(`Progress`); the real children's deadlines are passed by an injected clock, so nothing waits them out.
"""
import os
import select
import sys
import time

import pytest

from subprocesses import HANG_TIMEOUT, PROGRESS_WALL_CAP, Progress, Stalled, run_while_progressing

STALL, CAP = HANG_TIMEOUT, PROGRESS_WALL_CAP


def count(line):
    """The progress a fake child reports: `progress <n>` lines."""
    return int(line.split()[1]) if line.startswith("progress ") else None


def test_a_child_that_keeps_progressing_is_never_due_before_its_cap():
    watch = Progress(0.0, STALL, CAP)
    now = 0.0
    for value in range(1, 30):
        now += 0.9 * STALL
        if now >= CAP:
            break
        assert now < watch.deadline(), (value, now)
        watch.seen(value, now)
    assert now > 2 * STALL, "the run outlasted the stall window several times over"
    assert watch.deadline() == CAP and watch.why() == f"ran past its wall cap of {CAP:g} s"


@pytest.mark.parametrize("later", [[None, None], [5, 5], [4, 3]], ids=["no report", "same", "falling"])
def test_only_a_value_above_every_earlier_one_is_progress(later):
    watch = Progress(0.0, STALL, CAP)
    assert watch.deadline() == STALL, "a child that never reports is due a stall window after its start"
    watch.seen(5, 10.0)
    for offset, value in enumerate(later, start=1):
        watch.seen(value, 10.0 + offset * 100)
    assert watch.deadline() == 10.0 + STALL
    assert watch.why() == f"made no progress for {STALL:g} s"


def test_a_working_child_returns_its_output_and_exit_status():
    script = ("import sys\n"
              "for n in range(1, 4):\n"
              "    print(f'progress {n}', file=sys.stderr, flush=True)\n"
              "print('note', file=sys.stderr)\n"
              "print('the answer')\n"
              "raise SystemExit(3)\n")
    completed = run_while_progressing([sys.executable, "-c", script], count)
    assert (completed.returncode, completed.stdout) == (3, "the answer\n")
    assert completed.stderr == "progress 1\nprogress 2\nprogress 3\nnote\n"


def _expired_after_first_progress():
    """A clock and a progress reader: the clock is the real one up to the reading that records the child's
    first `progress` line; every later reading is one stall window after that, so the watch finds the stall
    at its next look, and nothing waits it out."""
    state = {"seen": False, "at": None}

    def clock():
        if not state["seen"]:
            return time.monotonic()
        if state["at"] is None:
            state["at"] = time.monotonic()
            return state["at"]
        return state["at"] + STALL

    def progress(line):
        value = count(line)
        state["seen"] = state["seen"] or value is not None
        return value
    return clock, progress


HUNG = {
    # Reports progress, then waits for nothing, as a run blocked on a pipe or a lock does.
    "stops working": "print('progress 1', file=sys.stderr, flush=True)\nsignal.pause()\n",
    # Repeats its last report without doing more: a heartbeat is no progress.
    "repeats itself": ("print('progress 1', file=sys.stderr, flush=True)\n"
                       "while True:\n    print('progress 1', file=sys.stderr, flush=True); signal.pause()\n"),
    # Closes its standard error and keeps running.
    "closes stderr": "print('progress 1', file=sys.stderr, flush=True)\nos.close(2)\nsignal.pause()\n",
}


@pytest.mark.parametrize("behaviour", sorted(HUNG))
def test_a_child_whose_progress_stops_is_stopped_with_its_session(tmp_path, behaviour):
    """The child starts a grandchild that holds a FIFO open, reports progress, then hangs. The watch raises
    `Stalled` and kills the whole session: the FIFO's last writer is gone, so its reader sees the end."""
    fifo = tmp_path / "held"
    os.mkfifo(fifo)
    reader = os.open(fifo, os.O_RDONLY | os.O_NONBLOCK)
    holder = f"import signal; held = open({str(fifo)!r}, 'w'); print('ready', flush=True); signal.pause()"
    script = ("import os, signal, subprocess, sys\n"
              f"holder = subprocess.Popen([sys.executable, '-c', {holder!r}], stdout=subprocess.PIPE, text=True)\n"
              "assert holder.stdout.readline() == 'ready\\n'\n" + HUNG[behaviour])
    clock, progress = _expired_after_first_progress()
    try:
        with pytest.raises(Stalled) as stalled:
            run_while_progressing([sys.executable, "-c", script], progress, clock=clock)
        assert str(stalled.value).endswith(f"made no progress for {STALL:g} s"), str(stalled.value)
        assert stalled.value.timeout == STALL and stalled.value.stderr.startswith("progress 1\n")
        ready, _, _ = select.select([reader], [], [], HANG_TIMEOUT)
        assert ready and os.read(reader, 1) == b"", "the grandchild outlived the stalled child"
    finally:
        os.close(reader)


def test_a_child_past_its_cap_is_stopped_while_it_still_progresses():
    script = ("import itertools, sys\n"
              "for n in itertools.count(1):\n"
              "    print(f'progress {n}', file=sys.stderr, flush=True)\n")
    # Each progress line takes half a stall window on the clock: always in time, until the cap.
    lines = []

    def progress(line):
        lines.append(line)
        return count(line)
    with pytest.raises(Stalled) as stalled:
        run_while_progressing([sys.executable, "-c", script], progress, clock=lambda: len(lines) * STALL / 2)
    assert str(stalled.value).endswith(f"ran past its wall cap of {CAP:g} s") and stalled.value.timeout == CAP
    assert len(lines) == 2 * CAP // STALL


def test_a_progress_reader_that_refuses_a_line_stops_the_child():
    script = ("import itertools, sys\n"
              "for n in itertools.count(1):\n"
              "    print(f'progress {n}', file=sys.stderr, flush=True)\n")

    def bounded(line):
        value = count(line)
        assert value is None or value < 3, "past its work bound"
        return value
    with pytest.raises(AssertionError, match="past its work bound"):
        run_while_progressing([sys.executable, "-c", script], bounded)
