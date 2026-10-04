"""Wall-clock guard for external tools, never a test acceptance criterion.

A test that bounds how much work a backend does measures CPU time instead:
elapsed time grows with machine load (a nightly suite at load 20 on 16 vCPUs
failed a 60-second elapsed bound that the same batch met alone), while the CPU
seconds a process spends are, to first order, the same on a busy or an idle
machine.
"""
import resource
import subprocess

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
    return completed, cpu.seconds
