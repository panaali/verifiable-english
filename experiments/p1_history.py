"""Reconstruct frozen P1 requests without relabelling a current checker build.

The retained record is historical evidence. Before it can be reused, the caller
must replay the obligation with the current checker and match every field other
than the implementation fingerprint. Paid-request cache matching is unchanged.
"""
from copy import deepcopy
from functools import lru_cache
import json
from pathlib import Path

from ve_experiments.paid import PreflightError, packed


@lru_cache(maxsize=1)
def retained_findings():
    root = Path(__file__).resolve().parent / 'P1-deference'
    ledger = root / 'runs/study/costs.jsonl'
    if not ledger.exists():
        return {}
    prefix, suffix = (root / 'prompts/finding.txt').read_text().split('{record}')
    records = {}
    with ledger.open() as stream:
        for line in stream:
            row = json.loads(line)
            metadata = row.get('metadata', {})
            if (row.get('event') != 'reserve' or metadata.get('arm') != 'A'
                    or metadata.get('role') != 'initial'):
                continue
            for message in row['messages']:
                text = message.get('content', '')
                if message.get('role') != 'system' or not text.startswith(prefix) or not text.endswith(suffix):
                    continue
                record = json.loads(text[len(prefix):len(text) - len(suffix) if suffix else None])
                item_id = metadata['item_id']
                if record['item_id'] != item_id or any(
                        record.get(k) != v for k, v in metadata['checker'].items()):
                    raise PreflightError('retained finding identity differs from its request')
                if item_id in records and records[item_id] != record:
                    raise PreflightError('conflicting retained findings for one P1 item')
                records[item_id] = record
    return records


def replayed_historical_finding(current):
    historical = retained_findings().get(current['item_id'])
    if historical is None:
        return current
    # Preserve the original record only after comparing the complete current
    # replay, including version, graph, queries, artifacts, and witness results.
    semantic = lambda record: {k: v for k, v in record.items() if k != 'checker_build'}
    if packed(semantic(current)) != packed(semantic(historical)):
        raise PreflightError('current replay differs from retained P1 finding')
    return deepcopy(historical)
