"""2026-09-22 harness-defect replacement: dev X/VE only, costs retained."""
import json
from experiments.p5_materials import read
from ve_experiments.paid import PreflightError

REVISION = 'study-v10'
RERUN_ARMS = ('X', 'VE')
RETAINED_ARMS = ('L', 'S')

# Generic syntax documentation, never a dossier-specific environment or solution.
ENVIRONMENT_EXAMPLE = {
    'language': 've.core@0', 'profile': 'relational-fol@0',
    'spec_revision': 've-v0-draft-2026-09-20',
    'vocabulary': {
        'sorts': {'thing': {'description': 'An example entity.'}},
        'predicates': {'marked': {'arguments': ['thing'], 'description': 'Example property.'}},
        'constants': {'sample': {'sort': 'thing', 'description': 'Example constant.'}}}}
WIRE_GUIDE = ('VE wire-format guide (syntax only; author your own vocabulary and claims): '
    'environment must be a JSON object, not a string. Example: '
    + json.dumps(ENVIRONMENT_EXAMPLE, separators=(',', ':'))
    + '. Strict claim syntax examples: "@sample is marked.\\n", '
    '"for every thing x, (if (x is marked), then (x is marked)).\\n" '
    'Use declared ASCII identifiers and a final period followed by a newline, not parenthetical English senses. '
    'Each alignment entry must cite nonempty exact record IDs, including premise entries. '
    'These examples supply no facts, bridges, or source interpretations.')


def superseded_identity(identity):
    parts = (identity or '').split('/')
    return (len(parts) == 7 and parts[:2] == ['study-v9', 'dev']
            and parts[3] in RERUN_ARMS)


def run_path(split, name):
    from experiments import p5 as p
    return p.HERE/'runs/dev-v10'/name if split == 'dev' else p.run_path(split, name)


def trials(split):
    from experiments import p5 as p
    if split != 'dev':
        return read(p.run_path(split, 'trials.jsonl'))
    retained = [r for r in read(p.run_path('dev', 'trials.jsonl')) if r['condition'] in RETAINED_ARMS]
    fresh = read(run_path('dev', 'trials.jsonl'))
    if any(r['condition'] not in RERUN_ARMS for r in fresh):
        raise PreflightError('v10 dev may contain only replacement X/VE judgments')
    return retained + fresh


def verify_retained():
    from experiments import p5 as p
    manifest = json.loads((p.HERE/'checks/dev-rerun-amendment.json').read_text())
    for path, expected in manifest['retained_hashes'].items():
        if p.sha(p.HERE/path) != expected:
            raise PreflightError('superseded/retained dev evidence changed: '+path)
    raw = (p.HERE/'runs/study/costs.jsonl').read_bytes()
    from hashlib import sha256
    if sha256(raw[:manifest['ledger_prefix_bytes']]).hexdigest() != manifest['ledger_prefix_sha256']:
        raise PreflightError('retained study costs changed')
    rows = [r for r in trials('dev') if r['condition'] in RETAINED_ARMS]
    expected = {(i['id'], a, j) for i in p.materials('dev') for a in RETAINED_ARMS
                for j in p.SCENARIOS['dual_judge']}
    if len(rows) != 48 or {(r['item_id'], r['condition'], r['judge']) for r in rows} != expected:
        raise PreflightError('retained L/S dev must have exactly 48 final judgments')
    return manifest
