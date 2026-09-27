"""Re-segment the pinned 0407Z ledger without changing its semantic claims."""
from __future__ import annotations

import copy
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUN = Path(__file__).resolve().parent
PRIOR = Path('/home/seyran/code/manage-agents/pilots/claude-constitution/run-20260927T0407Z')
SOURCE = (ROOT / 'source/claude-constitution.md').read_bytes()
OLD_LEDGER = json.loads((PRIOR / 'units.json').read_text())
OLD_TEXT = (PRIOR / 'translation.ve.md').read_text()
OLD_META = json.loads(OLD_TEXT.split('\n', 2)[1])
OLD_UNITS = OLD_META['units']
assert len(OLD_LEDGER) == len(OLD_UNITS) == 299
assert OLD_UNITS[-1]['span'][1] == len(SOURCE)

SENTENCE = re.compile(r'[.!?][”"\')\]]*\s+(?=[A-Z“"‘*])')
ABBREVIATIONS = ('e.g.', 'i.e.', 'Mr.', 'Mrs.', 'Dr.', 'Prof.', 'U.S.', 'U.K.', 'vs.')
BULLET = re.compile(r'(?m)^\s*(?:\* |[-+] |\d+\. |#{1,6} )')


def split_text(value: str) -> list[str]:
    # First isolate each markdown bullet or heading, keeping all separators.
    points = [0] + [m.start() for m in BULLET.finditer(value) if m.start() > 0] + [len(value)]
    pieces = []
    for a, b in zip(points, points[1:]):
        part = value[a:b]
        cuts = [0]
        for match in SENTENCE.finditer(part):
            prefix = part[:match.start() + 1]
            if any(prefix.endswith(abbreviation) for abbreviation in ABBREVIATIONS):
                continue
            # The whitespace belongs to the preceding sentence.
            cuts.append(match.end())
        cuts.append(len(part))
        for x, y in zip(cuts, cuts[1:]):
            chunk = part[x:y]
            if not chunk:
                continue
            if len(chunk.encode()) <= 600:
                pieces.append(chunk)
                continue
            # A long sentence can contain distinct semicolon clauses.
            subs = re.split(r'(?<=;)\s+', chunk)
            pieces.extend(s for s in subs if s)
    assert ''.join(pieces) == value
    return pieces


meta = copy.deepcopy(OLD_META)
meta['units'] = []
# The prior audit found no source warrant for a blanket Anthropic reviewer.
# Preserve the open terms and their empty tests, but name the missing authority.
for term in meta['open_terms']:
    term['decided_by'] = 'unresolved_decider'
ledger = []
cursor = 0
for old_record, old_unit in zip(OLD_LEDGER, OLD_UNITS):
    assert old_record['id'] == old_unit['id']
    a, b = old_unit['span']
    assert a == cursor
    value = SOURCE[a:b].decode()
    parts = split_text(value)
    if old_unit['id'] == 'u0248':
        assert len(parts) == 1
    for index, part in enumerate(parts, 1):
        size = len(part.encode())
        unit = copy.deepcopy(old_unit)
        unit['id'] = old_unit['id'] if len(parts) == 1 else f"{old_unit['id']}.s{index:02d}"
        unit['span'] = [cursor, cursor + size]
        record = copy.deepcopy(old_record)
        record['id'] = unit['id']
        record['span'] = unit['span']
        record['parent_unit'] = old_unit['id']
        record['source_excerpt'] = part.strip()[:180]
        if isinstance(unit['kind'], list) and unit['kind'][0] == 'attributed':
            # Paragraph attribution should not silently attach to every
            # sentence after a sentence-level split.
            if not re.match(r'^\s*We (?:believe|think)\b', part):
                unit['kind'] = unit['kind'][3]
        if old_unit['id'] == 'u0214':
            # The prior audit found that a whole-paragraph OPEN label dropped
            # the principal hierarchy and its three named principals.
            unit['kind'] = ['unformalised', 'counting' if index == 1 else 'other.discourse']
            unit['meaning'] = {'unformalised': unit['kind'][1]}
            record['status'] = 'UNFORMALISED'
            record['missing_feature'] = 'counting' if index == 1 else 'other:discourse'
            record['note'] = 'Prior OPEN label was incomplete; principal hierarchy content remains unchecked.'
            record.pop('other_blockers', None)
        meta['units'].append(unit)
        ledger.append(record)
        cursor += size
    assert cursor == b

assert cursor == len(SOURCE)
assert [u['span'] for u in meta['units']] == [u['span'] for u in ledger]
# The old source body is preserved exactly. The only VE English sentence is
# the previous checked clause, copied byte for byte from the prior run.
body = OLD_TEXT.split('\n---\n', 1)[1]
assert body.startswith(SOURCE.decode())
suffix = body[len(SOURCE.decode()):]
(RUN / 'translation.ve.md').write_text('---\n' + json.dumps(meta, ensure_ascii=False, separators=(',', ':')) + '\n---\n' + SOURCE.decode() + suffix)
(RUN / 'units.json').write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + '\n')
