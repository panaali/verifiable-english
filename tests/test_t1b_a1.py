from ve_experiments.t1b.amendment_run import canonical_ids
from ve_experiments.claude_cli import MODELS


def test_exact_haiku_equivalence_only():
    assert canonical_ids('haiku')=={'claude-haiku-4-5-20251001','claude-haiku-4-5'}
    assert 'claude-haiku-4-6' not in canonical_ids('haiku')
    assert canonical_ids('opus')=={MODELS['opus']}
    assert canonical_ids('sonnet')=={MODELS['sonnet']}
