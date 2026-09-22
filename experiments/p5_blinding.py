"""Scan the tracked P5 artifact surface, including compressed JSON, for labels."""
import gzip
from pathlib import Path
import re
import subprocess

from experiments.p5_materials import HERE

# Exact paths, also named individually in REVIEW-CHECKLIST.md. These are
# construction/scoring history, never model context or reviewer attachments.
BARRED = (
    'labels.jsonl.gz',
    'materials/dossiers.jsonl.gz',
    'materials/scored.jsonl.gz',
    'materials/dev.jsonl.gz',
    'materials/paraphrases.jsonl.gz',
    'materials/graphs.jsonl.gz',
    'materials/anchored-labels.jsonl.gz',
    'materials/construction-ledger.jsonl.gz',
    'materials/review-ledger.jsonl.gz',
    'materials/rejected-v1.jsonl.gz',
    'materials/rejected-v2-initial.jsonl.gz',
    'checks/lean-replay-ledger.jsonl.gz',
    'checks/rejected-v2-generator.jsonl.gz',
    'checks/rejected-review-v1.json',
    'checks/round5-review-submission.json',
    'checks/round5-review-verification.txt',
)
LABEL_PATTERN = re.compile(
    r'"(?:kind|variant)"\s*:\s*"(?:shift|smuggle|benign)"'
    r'|"(?:slot_id|acceptable_locations|affected_uses|sense_use_mapping)"\s*:'
    r'|p5-(?:dev|scored)-\d+-(?:shift|smuggle|benign)'
)


def audit(base=HERE):
    root = base.parents[1]
    relative = base.relative_to(root)
    paths = subprocess.check_output(
        ['git', 'ls-files', '--cached', '--others', '--exclude-standard', '--', str(relative)],
        cwd=root, text=True).splitlines()
    failures = []; checked = 0
    for name in sorted(set(paths)):
        path = root/name
        if str(path.relative_to(base)) in BARRED:
            continue
        raw = path.read_bytes()
        # Timestamp receipts are binary; still scan any embedded text for labels.
        text = (gzip.decompress(raw) if path.suffix == '.gz' else raw).decode(errors='replace')
        checked += 1
        if LABEL_PATTERN.search(text):
            failures.append(name)
    checklist = (base/'REVIEW-CHECKLIST.md').read_text()
    missing = [name for name in BARRED if f'`{name}`' not in checklist]
    return {'passed':not failures and not missing, 'files_checked':checked,
            'label_bearing_files':failures, 'undocumented_barred_files':missing,
            'generation_calls':0}
