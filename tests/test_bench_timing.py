"""The cold editor call must not determine warm latency p95."""
from bench import timing


def test_measure_excludes_cold_call_and_samples_each_warm_call(monkeypatch):
    calls = []
    ticks = iter(range(10))
    monkeypatch.setattr(timing.time, 'perf_counter', lambda: next(ticks))
    monkeypatch.setattr(timing.os, 'getloadavg', lambda: (1, 2, 3))

    def operation():
        calls.append(len(calls))

    values, loads = timing.measure(operation, repeats=5)
    assert calls == list(range(6))
    assert values == [1000] * 5
    assert loads == [[1, 2, 3]] * 5


def test_p95_uses_all_twenty_editor_samples():
    values = list(range(19)) + [100]
    assert timing.stats(values) == {'p50_ms': 9.5, 'p95_ms': 22.1, 'max_ms': 100}
