"""Wall-clock guard for external tools, never a test acceptance criterion.

A test that bounds how much work a backend does measures CPU time instead:
elapsed time grows with machine load (a nightly suite at load 20 on 16 vCPUs
failed a 60-second elapsed bound that the same batch met alone), while the CPU
seconds a process spends are, to first order, the same on a busy or an idle
machine.
"""
import json
import os
import resource
import subprocess
from types import SimpleNamespace

HANG_TIMEOUT = 1800


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
