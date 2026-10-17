"""Wall-clock guard for external tools, never a test acceptance criterion.

A test that bounds how much work a backend does measures CPU time instead:
elapsed time grows with machine load (a nightly suite at load 20 on 16 vCPUs
failed a 60-second elapsed bound that the same batch met alone), while the CPU
seconds a process spends are, to first order, the same on a busy or an idle
machine.
"""
import json
import os
import queue
import resource
import signal
import subprocess
import threading
import time
from types import SimpleNamespace

HANG_TIMEOUT = 1800
# The whole wall time a child that reports its progress may take (`run_while_progressing`): load
# stretches a run that keeps progressing, so its cap is far above HANG_TIMEOUT.
PROGRESS_WALL_CAP = 4 * HANG_TIMEOUT


def _children_cpu():
    usage = resource.getrusage(resource.RUSAGE_CHILDREN)
    return usage.ru_utime + usage.ru_stime


class ChildCPU:
    """CPU seconds (user + system) of the child processes that end inside the block."""

    def __enter__(self):
        self.seconds = None
        self._start = _children_cpu()
        return self

    def __exit__(self, *_):
        self.seconds = _children_cpu() - self._start
        return False


def run_cpu_bounded(command, stdin, cpu_seconds, env=None):
    """Run `command` on `stdin` under a kernel CPU-time limit of `cpu_seconds`.

    The limit (RLIMIT_CPU) stops a runaway child while it runs, whatever the
    load; HANG_TIMEOUT only catches a child that blocks without computing.
    `env`, when given, is the child's whole environment.
    Returns the completed process and the CPU seconds it spent; a child the
    limit stopped ends by SIGXCPU or SIGKILL, which the caller reports."""
    def limit():
        resource.setrlimit(resource.RLIMIT_CPU, (int(cpu_seconds), int(cpu_seconds) + 1))
    with ChildCPU() as cpu:
        completed = subprocess.run(command, input=stdin, text=True, capture_output=True,
                                   timeout=HANG_TIMEOUT, preexec_fn=limit, env=env)
    log = os.environ.get("VE_BENCH_CPU_LOG")
    if log:  # tools/bench/test_perf.py benchmarks what each bounded child spends
        with open(log, "a") as stream:
            stream.write(json.dumps({"test": os.environ.get("PYTEST_CURRENT_TEST", "").rsplit(" ", 1)[0],
                                     "command": os.path.basename(command[0]), "cpu": cpu.seconds}) + "\n")
    return completed, cpu.seconds


class Stalled(subprocess.TimeoutExpired):
    """A child `run_while_progressing` stopped: its progress stopped, or it ran past its wall cap."""

    def __init__(self, cmd, timeout, why, output=None, stderr=None):
        super().__init__(cmd, timeout, output, stderr)
        self.why = why

    def __str__(self):
        return f"Command {self.cmd!r} {self.why}"


class Progress:
    """When a watched child must next have progressed: `stall` seconds after it last did (reported a
    value above every earlier one), and never later than `cap` seconds after it started."""

    def __init__(self, start, stall, cap):
        self.start, self.stall, self.cap = start, stall, cap
        self.last = start
        self.mark = None

    def seen(self, value, now):
        if value is not None and (self.mark is None or value > self.mark):
            self.mark, self.last = value, now

    def deadline(self):
        return min(self.last + self.stall, self.start + self.cap)

    def why(self):
        """What the child did not do by `deadline`."""
        if self.start + self.cap <= self.last + self.stall:
            return f"ran past its wall cap of {self.cap:g} s"
        return f"made no progress for {self.stall:g} s"


def run_while_progressing(command, progress, *, cwd=None, env=None, stall=HANG_TIMEOUT,
                          cap=PROGRESS_WALL_CAP, clock=time.monotonic):
    """Run `command` to its end, as `subprocess.run(..., capture_output=True, text=True)` does, while it
    makes progress.

    `progress(line)` reads each line of the child's standard error as it comes: None for a line that
    reports none, else the child's progress so far, a value that grows while the child works. The child
    and every process of its session are killed and `Stalled` is raised when it reports no progress for
    `stall` seconds (`Progress`), or when it is still running `cap` seconds after it started. Machine load
    slows a working child without stopping its progress; a hang stops it. An exception `progress` raises
    (a work bound passed, say) kills them too and is raised. `clock` is the watch's clock: a test injects
    one that has already passed the deadline, so no wait is waited out."""
    proc = subprocess.Popen(command, cwd=cwd, env=env, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, text=True, start_new_session=True)
    lines, out, err = queue.Queue(), [], []

    def read_output():
        out.append(proc.stdout.read())

    def read_errors():
        for line in proc.stderr:
            lines.put(line)
        lines.put(None)
    readers = [threading.Thread(target=read_output, daemon=True), threading.Thread(target=read_errors, daemon=True)]
    for reader in readers:
        reader.start()
    watch = Progress(clock(), stall, cap)
    stalled, ended = None, False
    try:
        while True:
            now = clock()
            if now >= watch.start + cap:  # however fast it still reports
                stalled = watch.why()
                break
            try:
                line = lines.get(timeout=max(watch.deadline() - now, 0))
            except queue.Empty:
                stalled = watch.why()
                break
            if line is None:
                break
            err.append(line)
            watch.seen(progress(line), clock())
        if stalled is None:  # its standard error is closed: the child is ending
            try:
                proc.wait(timeout=max(watch.deadline() - clock(), 0))
            except subprocess.TimeoutExpired:
                stalled = watch.why()
        ended = stalled is None
    finally:
        if not ended:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:  # the session has no process left
                pass
        proc.wait()
        for reader in readers:
            reader.join(HANG_TIMEOUT)
    while not lines.empty():
        line = lines.get_nowait()
        if line is not None:
            err.append(line)
    if stalled is not None:
        raise Stalled(command, cap if "cap" in stalled else stall, stalled, "".join(out), "".join(err))
    return subprocess.CompletedProcess(command, proc.returncode, "".join(out), "".join(err))


def expired_waits(monkeypatch, module, *, expire=lambda argv: True):
    """An injected clock for the deadlines `module` sets on its children: each wall-clock wait
    it starts through its `subprocess` (`run` or `Popen.communicate`) on a
    child `expire(argv)` selects has already expired when it starts. The real child starts;
    unless it has answered at once, the call raises `TimeoutExpired` for the deadline asked
    for, exactly as after waiting that deadline out. A deadline test against a never-answering
    fake therefore waits for no deadline, whatever the load.

    Returns the list of the waits the code asked for, in order (the configured values)."""
    waits = []

    def expired(argv, timeout, call):
        if timeout is None or not expire(argv):
            return call(timeout)
        waits.append(timeout)
        try:
            return call(0)
        except subprocess.TimeoutExpired as exc:
            exc.timeout = timeout
            raise

    class Popen(subprocess.Popen):
        def communicate(self, input=None, timeout=None):
            return expired(self.args, timeout, lambda wait: super(Popen, self).communicate(input, wait))

    def run(argv, *, timeout=None, **options):
        return expired(argv, timeout, lambda wait: subprocess.run(argv, timeout=wait, **options))

    proxy = SimpleNamespace(**{name: getattr(subprocess, name) for name in dir(subprocess)
                               if not name.startswith("__")})
    proxy.Popen, proxy.run = Popen, run
    monkeypatch.setattr(module, "subprocess", proxy)
    return waits


BUSY_PHASES = {"write": "_write_all", "response": "_read_line"}


def busy_cpu(monkeypatch, module, phases=("response",)):
    """A CPU clock for the deadlines `module` sets on its service (`module._cpu_seconds`): while the
    client is in one of `phases` of a request (`write`, sending it; `response`, waiting for the answer
    after the whole request was sent), each reading of a process is one clock tick (the resolution
    /proc reports) past the last one and never below the real CPU time; in the request's other phase
    it stands still at the last reading; outside a request it is the real CPU time, never below an
    earlier reading. A process seen through it is working in `phases` only, so a CPU deadline below
    one tick is passed at the client's first check in the first of them, whatever the machine's speed:
    on the real clock a fast machine can answer within one tick, which reads as no CPU at all, and a
    slow one can pass the deadline while the request is still being written.

    The default is the response wait: there the service has the whole request, so a deadline found
    passed there is one the service's work passed, not one the client found while still writing.

    Returns the clock's record: `readings` by process id, and `fired`, the phase of each request whose
    deadline was found passed (in order)."""
    assert phases and set(phases) <= set(BUSY_PHASES), phases
    real, tick = module._cpu_seconds, 1 / os.sysconf("SC_CLK_TCK")
    clock = SimpleNamespace(readings={}, fired=[], phase=None)

    def reading(pid):
        seconds = real(pid)
        if seconds is None:
            return None
        seen = clock.readings.setdefault(pid, [])
        if not seen or clock.phase is None:
            seen.append(max([seconds, *seen[-1:]]))
        else:
            seen.append(max(seconds, seen[-1] + tick) if clock.phase in phases else seen[-1])
        return seen[-1]

    def within(phase, method):
        def call(self, *arguments):
            saved, clock.phase = clock.phase, phase
            try:
                return method(self, *arguments)
            except module.CheckerUnavailable:
                clock.fired.append(phase)
                raise
            finally:
                clock.phase = saved
        return call
    monkeypatch.setattr(module, "_cpu_seconds", reading)
    for phase, name in BUSY_PHASES.items():
        monkeypatch.setattr(module.LeanService, name, within(phase, getattr(module.LeanService, name)))
    return clock
