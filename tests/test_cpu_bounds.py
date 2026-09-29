"""The CPU-time bound that replaces elapsed-time bounds on backend batches.

tests/test_w6a_limit_generator.py[2] failed its 60-second elapsed bound in a
nightly suite at load 20 on 16 vCPUs and met it alone: waiting for a CPU was
charged as work. `run_cpu_bounded` charges only the CPU a child spends, and
the kernel stops a child that spends past its limit.
"""
import signal
import sys

from subprocesses import ChildCPU, run_cpu_bounded


def test_time_a_child_spends_waiting_is_not_charged():
    completed, cpu = run_cpu_bounded([sys.executable, "-c", "import time; time.sleep(3)"], "", 2)
    assert completed.returncode == 0, completed.stderr
    assert cpu < 2, cpu


def test_a_child_that_spins_past_its_limit_is_stopped():
    completed, cpu = run_cpu_bounded([sys.executable, "-c", "while True: pass"], "", 1)
    assert completed.returncode in (-signal.SIGXCPU, -signal.SIGKILL), completed.returncode
    # The kernel checks the limit at scheduler ticks, and rusage rounds.
    assert 0.5 < cpu < 3, cpu


def test_child_cpu_counts_only_children_that_end_inside_the_block():
    with ChildCPU() as outside:
        pass
    assert outside.seconds == 0
    completed, cpu = run_cpu_bounded([sys.executable, "-c", "sum(range(3_000_000))"], "", 10)
    assert completed.returncode == 0 and 0 < cpu < 10, (completed.returncode, cpu)
