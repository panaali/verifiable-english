"""Enforce one dossier per context and disjoint sibling exposure per reviewer."""
from pathlib import Path
from ve_experiments.paid import PreflightError


def single_context(items):
    if len(items) != 1:
        raise PreflightError('exactly one dossier per context; no few-shot or sibling pools')
    return items[0]


def blind_packet(payload):
    return {**{k: payload[k] for k in ('id', 'glossary', 'premises', 'records', 'argument', 'root')},
            'step_ids': [n['id'] for n in payload['nodes']]}


def export_isolated(destination, rows, families):
    """Export separate family-disjoint assignments, each packet in its own file.

    The index contains paths only, never packet content. A reviewer/context may
    consume ONE assignment; distinct assignments require distinct reviewers.
    """
    from experiments.p5_materials import write_json
    destination = Path(destination)
    seen, batches = {}, []
    for row in rows:
        item_id = row.get('item_id', row['packet']['id'])
        family = families[item_id]
        assigned = seen.setdefault(family, {})
        if item_id not in assigned:
            assigned[item_id] = len(assigned)
        b = assigned[item_id]
        while len(batches) <= b:
            batches.append([])
        path = destination.parent / (destination.stem + '-packets') / f'assignment-{b+1}' / f'{len(batches[b]):03d}.json'
        write_json(path, [row])
        batches[b].append(str(path.relative_to(destination.parent)))
    manifest = {'policy': 'One assignment per reviewer; one file per fresh context. Never combine assignments or use sibling few-shot examples.',
                'assignments': batches, 'packets': len(rows)}
    write_json(destination, manifest)
    return {'packets': len(rows), 'assignments': len(batches), 'output': str(destination)}


def validate_exposure(rows, prior, items, identity='reviewer_id'):
    seen = {}
    for row in [*prior, *rows]:
        item_id = row.get('item_id')
        person = row.get(identity) or (row.get('adjudicator') if identity == 'reviewer_id' else None)
        if item_id not in items or not person:
            continue
        key = (person, items[item_id]['group'])
        if seen.setdefault(key, item_id) != item_id:
            raise PreflightError('reviewer/rater cannot see multiple siblings, including earlier submissions')
