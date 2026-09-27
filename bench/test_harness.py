import json

from bench.run import corpus, input_bytes, percentile, report, wire
from bench.worker import run


def test_python_fixtures_are_accepted():
    for name, (case, implementations) in corpus().items():
        assert 'python' in implementations, name
        answer = run(wire(case, 'python'))
        assert answer.get('status') != 'error', (name, answer)
        if name.startswith('certificate/'):
            assert answer['valid']


def test_wire_batches_preserve_identical_cases():
    case, _ = corpus()['finite-model/evaluation']
    python = [json.loads(line) for line in input_bytes(case, 'python', 4).splitlines()]
    rust = [json.loads(line) for line in input_bytes(case, 'rust', 4).splitlines()]
    lean = json.loads(input_bytes(case, 'lean', 4))
    assert len(python) == len(rust) == len(lean) == 4
    assert all(row['ast'] == case['ast'] for row in python + rust + lean)
    assert all(row['model'] == case['model'] for row in python + rust + lean)
    assert len({json.dumps(row, sort_keys=True) for row in lean}) == 1


def test_percentile_and_report():
    assert percentile([1, 2, 3, 4, 5], .95) == 4.8
    sample = {'median_ms': 1, 'p95_ms': 2}
    data = {'quick': True, 'measurements': [{'workload': 'x', 'cases': 4,
            'implementation': 'python', 'startup': sample, 'call': sample,
            'throughput': {'median_per_s': 20, 'p95_per_s': 21}}]}
    assert '| x | 4 | — | python |' in report(data)
