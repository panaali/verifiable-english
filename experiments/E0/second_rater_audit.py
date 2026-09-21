#!/usr/bin/env python3
"""Freeze blind E0 ratings, verify witnesses, then compare and report.

The freeze and verify commands never open first-rater label files. Comparison
requires an intact freeze manifest. No statistical dependencies are needed.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
DATASETS = ('folio', 'proofwriter', 'cedar', 'gatekeeper', 'alloy', 'fret', 'clover')
DISPLAY = dict(zip(DATASETS, ('FOLIO', 'ProofWriter', 'Cedar', 'Gatekeeper', 'Alloy', 'FRET', 'Clover')))
LABELS = ('DIRECT', 'REIFIED', 'OPAQUE', 'NO')
FIRST_LABELS = dict(zip('abcd', LABELS))
FIT = frozenset(('DIRECT', 'REIFIED'))
PIN = '12538d8d418b3eeec59e58d74c3886786e5139da'
SECOND = ROOT / 'second_rater.jsonl'
SEAL = ROOT / 'second_rater_freeze.json'


def read_json(path):
    return json.loads(path.read_text())


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def write_json(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')


def write_jsonl(path, rows):
    path.write_text(''.join(json.dumps(row, ensure_ascii=False, sort_keys=True) + '\n' for row in rows))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sample_path(dataset):
    return ROOT / 'survey_samples' / '_drawn' / f'{dataset}.json'


def samples(dataset):
    return read_json(sample_path(dataset))['sample']


def wilson(k, n=30):
    if not 0 <= k <= n or n <= 0:
        raise ValueError('Expected 0 <= k <= n and n > 0')
    z = 1.959963984540054
    p, z2 = k / n, z * z
    den = 1 + z2 / n
    center = (p + z2 / (2 * n)) / den
    radius = z * math.sqrt(p * (1 - p) / n + z2 / (4 * n * n)) / den
    return {'k': k, 'n': n, 'rate': p,
            'ci_low': max(0.0, center - radius), 'ci_high': min(1.0, center + radius)}


def agreement(first, second, labels):
    if len(first) != len(second) or not first:
        raise ValueError('Agreement requires equally sized nonempty vectors')
    n = len(first)
    matrix = {a: {b: 0 for b in labels} for a in labels}
    for a, b in zip(first, second):
        matrix[a][b] += 1
    ca, cb = Counter(first), Counter(second)
    matching = sum(a == b for a, b in zip(first, second))
    po = matching / n
    pe = sum(ca[label] * cb[label] for label in labels) / (n * n)
    return {'n': n, 'matching': matching, 'observed': po, 'expected': pe,
            'kappa': None if pe == 1 else (po - pe) / (1 - pe),
            'kappa_note': 'undefined: expected agreement is 1' if pe == 1 else None,
            'confusion_matrix_first_rows_second_columns': matrix}


def validate_rows(rows):
    assert len(rows) == 210, f'Expected 210 items, got {len(rows)}'
    for dataset in DATASETS:
        subset = [r for r in rows if r['dataset'] == dataset]
        expected = {s['id'] for s in samples(dataset)}
        assert len(subset) == len(expected) == 30, dataset
        assert {r['id'] for r in subset} == expected, dataset
        assert len({r['id'] for r in subset}) == len(subset), dataset
    for row in rows:
        assert row['label'] in LABELS
        assert isinstance(row['construct_needed'], list)
        assert row['rationale'].strip()
        if row['label'] == 'REIFIED':
            assert row.get('reification'), row['id']
        if row['label'] in ('OPAQUE', 'NO'):
            assert row['construct_needed'], row['id']


def check_witnesses(rows, checker_dir, update=False):
    sys.path.insert(0, str(Path(checker_dir).resolve()))
    import ve
    assert Path(ve.__file__).resolve().parent == Path(checker_dir).resolve() / 've', ve.__file__
    checked = Counter()
    for row in rows:
        source = row.get('formalization')
        if not source:
            assert not row.get('environment'), row['id']
            if update:
                row['formalization'] = None
                row['environment'] = None
                row['parse_result'] = {'status': 'not_attempted', 'reason': 'No full v0 witness supplied.'}
            continue
        try:
            result = ve.check(ve.Environment(row['environment']), source)
        except Exception as exc:
            raise AssertionError(f"{row['dataset']} {row['id']}: witness fails checker: {exc}") from exc
        assert result['language'] == 'accepted'
        if update:
            row['parse_result'] = {**result, 'checker_revision': PIN}
        else:
            assert row['parse_result'] == {**result, 'checker_revision': PIN}, row['id']
        if row['label'] in FIT:
            checked[row['dataset']] += 1
    for dataset in DATASETS:
        fits = sum(r['dataset'] == dataset and r['label'] in FIT for r in rows)
        assert checked[dataset] >= min(10, fits), (dataset, checked[dataset], fits)
    return dict(checked)


def count_rows(rows):
    return {d: {label: sum(r['dataset'] == d and r['label'] == label for r in rows)
                for label in LABELS} for d in DATASETS}


def count_table(rows):
    lines = ['| Dataset | DIRECT | REIFIED | OPAQUE | NO | Fit witnesses checked |',
             '|---|---:|---:|---:|---:|---:|']
    for d, counts in count_rows(rows).items():
        tested = sum(r['dataset'] == d and r['label'] in FIT and bool(r.get('formalization')) for r in rows)
        lines.append('| ' + ' | '.join([DISPLAY[d], *(str(counts[l]) for l in LABELS), str(tested)]) + ' |')
    return '\n'.join(lines)


def freeze(checker_dir):
    assert not SEAL.exists(), 'Blind freeze already exists; do not rewrite independent labels after unblinding.'
    rows = []
    for dataset in DATASETS:
        parts = read_jsonl(ROOT / 'second_rater_work' / f'{dataset}.jsonl')
        by_id = {r['id']: r for r in parts}
        assert len(parts) == len(by_id) == 30, dataset
        for sample in samples(dataset):
            row = by_id[sample['id']]
            row['dataset'] = dataset
            row['source_sample_sha256'] = hashlib.sha256(
                json.dumps(sample, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
            rows.append(row)
    validate_rows(rows)
    checked = check_witnesses(rows, checker_dir, update=True)
    write_jsonl(SECOND, rows)
    checker_hashes = {str(p.relative_to(checker_dir)): sha(p)
                      for p in sorted(Path(checker_dir).glob('ve/*.py'))}
    write_json(SEAL, {
        'frozen_at_utc': datetime.now(timezone.utc).isoformat(),
        'phase': 'independent ratings and witnesses complete; first item labels not inspected',
        'checker_revision': PIN, 'checker_files_sha256': checker_hashes,
        'second_rater_sha256': sha(SECOND), 'n': len(rows), 'fit_witnesses_checked': checked,
        'samples_sha256': {d: sha(sample_path(d)) for d in DATASETS},
        'blinding_disclosure': (
            'Parent performed schema-only programmatic inspection of first-rater JSONL files '
            '(keys/counts, not class or reason values). A location search printed SURVEY.md '
            'aggregate counts and dataset commentary before rating. No item-specific first-rater '
            'label or rationale was displayed before freeze. Seven dataset agents received '
            'fresh contexts without those aggregates and were instructed to avoid SURVEY.md '
            'and all first-rater JSONL files. This is not a fully aggregate-blind parent audit.'),
    })
    (ROOT / 'SECOND_RATER.md').write_text(
        '# E0 independent second rater\n\nBlind labels frozen; comparison not yet opened.\n\n'
        + count_table(rows) + '\n')
    print(json.dumps({'n': len(rows), 'counts': count_rows(rows), 'checked': checked}, indent=2))


def verify_seal(checker_dir=None):
    seal = read_json(SEAL)
    assert sha(SECOND) == seal['second_rater_sha256'], 'Independent labels changed after freeze'
    for d in DATASETS:
        assert sha(sample_path(d)) == seal['samples_sha256'][d], d
    rows = read_jsonl(SECOND)
    validate_rows(rows)
    for row in rows:
        sample = next(s for s in samples(row['dataset']) if s['id'] == row['id'])
        assert row['source_sample_sha256'] == hashlib.sha256(
            json.dumps(sample, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    if checker_dir:
        hashes = {str(p.relative_to(checker_dir)): sha(p) for p in sorted(Path(checker_dir).glob('ve/*.py'))}
        assert hashes == seal['checker_files_sha256'], 'Checker source differs from pinned source'
        assert check_witnesses(rows, checker_dir) == seal['fit_witnesses_checked']
    return rows


def comparison():
    rows = verify_seal()
    results, disagreements = {}, []
    for dataset in DATASETS:
        # This is the sole first-rater input reader, used only AFTER verify_seal.
        first_rows = read_jsonl(ROOT / 'survey_samples' / f'{dataset}.jsonl')
        first = {r['id']: r for r in first_rows}
        second = [r for r in rows if r['dataset'] == dataset]
        assert len(first_rows) == len(first) == len(second) == 30
        assert set(first) == {r['id'] for r in second}
        a = [FIRST_LABELS[first[r['id']]['class']] for r in second]
        b = [r['label'] for r in second]
        results[dataset] = {
            'first_counts': dict(Counter(a)), 'second_counts': dict(Counter(b)),
            'four_way': agreement(a, b, LABELS),
            'collapsed': agreement(['FIT' if x in FIT else 'NO_FIT' for x in a],
                                   ['FIT' if x in FIT else 'NO_FIT' for x in b], ('FIT', 'NO_FIT')),
        }
        for row, old_label in zip(second, a):
            if old_label != row['label']:
                old = first[row['id']]
                disagreements.append({
                    'dataset': dataset, 'id': row['id'], 'first_label': old_label,
                    'first_original_class': old['class'], 'first_rationale': old['reason'],
                    'second_label': row['label'], 'second_rationale': row['rationale'],
                    'construct_needed': row['construct_needed'],
                })
    write_json(ROOT / 'second_rater_comparison.json', results)
    write_jsonl(ROOT / 'second_rater_disagreements.jsonl', disagreements)
    return rows, results, disagreements


def rates_table(rows):
    lines = ['| Dataset | Strict: DIRECT | Lenient: DIRECT + REIFIED | Opaque-dependent: OPAQUE only |',
             '|---|---|---|---|']
    rates = {}
    for d, counts in count_rows(rows).items():
        values = [counts['DIRECT'], counts['DIRECT'] + counts['REIFIED'], counts['OPAQUE']]
        intervals = [wilson(k) for k in values]
        rates[d] = dict(zip(('strict', 'lenient', 'opaque_dependent'), intervals))
        cells = [f"{v['k']}/30 = {100*v['rate']:.1f}% [{100*v['ci_low']:.1f}, {100*v['ci_high']:.1f}]"
                 for v in intervals]
        lines.append('| ' + ' | '.join([DISPLAY[d], *cells]) + ' |')
    return '\n'.join(lines), rates


def roadmap(rows, mapping):
    counts = defaultdict(Counter)
    members = defaultdict(list)
    for r in rows:
        if r['label'] not in ('NO', 'OPAQUE'):
            continue
        families = set()
        for tag in r['construct_needed']:
            assert tag in mapping, f'Unmapped construct: {tag}'
            families.update(mapping[tag])
        assert families, f"Excluded item has no genuine blocker mapped: {r['dataset']} {r['id']}"
        for family in families:
            counts[family][r['dataset']] += 1
            members[family].append({'dataset': r['dataset'], 'id': r['id'], 'label': r['label']})
    ranked = sorted(counts, key=lambda c: (-sum(counts[c].values()), c))
    lines = ['| Construct | ' + ' | '.join(DISPLAY[d] for d in DATASETS) + ' | Total items |',
             '|---|' + '---:|' * (len(DATASETS) + 1)]
    result = []
    for family in ranked:
        per_dataset = {d: counts[family][d] for d in DATASETS}
        total = sum(per_dataset.values())
        lines.append('| ' + ' | '.join([family, *(str(v) for v in per_dataset.values()), str(total)]) + ' |')
        result.append({'construct': family, 'per_dataset': per_dataset, 'total': total, 'items': members[family]})
    return '\n'.join(lines), result


def report():
    rows, results, disagreements = comparison()
    adjudications = read_jsonl(ROOT / 'second_rater_adjudications.jsonl')
    decisions = {(r['dataset'], r['id']): r for r in adjudications}
    assert len(adjudications) == len(decisions) == len(disagreements)
    assert set(decisions) == {(r['dataset'], r['id']) for r in disagreements}
    proposed = []
    for row in rows:
        decision = decisions.get((row['dataset'], row['id']))
        if decision:
            assert decision['label'] in LABELS and decision['reason'].strip()
        proposed.append({**row, 'label': decision['label'] if decision else row['label']})
    for row in disagreements:
        decision = decisions[row['dataset'], row['id']]
        row.update(proposed_adjudicated_label=decision['label'], adjudication_reason=decision['reason'])
    write_jsonl(ROOT / 'second_rater_disagreements.jsonl', disagreements)
    independent_rates, rate_data = rates_table(rows)
    proposed_rates, proposed_rate_data = rates_table(proposed)
    mapping = read_json(ROOT / 'second_rater_construct_map.json')
    roadmap_table, roadmap_data = roadmap(rows, mapping)
    proposed_roadmap_table, proposed_roadmap_data = roadmap(proposed, mapping)
    write_json(ROOT / 'second_rater_metrics.json', {
        'second_counts': count_rows(rows), 'proposed_adjudicated_counts': count_rows(proposed),
        'agreement': results, 'second_rates': rate_data, 'proposed_adjudicated_rates': proposed_rate_data,
        'roadmap_independent': roadmap_data, 'roadmap_proposed_adjudicated': proposed_roadmap_data,
        'denominator_per_dataset': 30, 'wilson_confidence': 0.95,
        'disagreements': len(disagreements),
    })
    lines = ['# E0 independent second-rater coverage audit', '',
             (ROOT / 'second_rater_work' / 'METHODS.md').read_text().strip(), '',
             '## Frozen independent labels', '', count_table(rows), '',
             '## Coverage estimates', '',
             'Each cell is k/30, percentage, and nominal 95% Wilson interval. '
             'Opaque-dependent fit is OPAQUE alone, disjoint from lenient fit; '
             'it does not establish that v0 implements the hidden check.', '', independent_rates, '',
             '## Agreement with the first rater', '',
             'Original a/b/c/d map to DIRECT/REIFIED/OPAQUE/NO. Collapsed FIT = '
             'DIRECT or REIFIED; NO_FIT = OPAQUE or NO. Raw labels are compared '
             'without silently repairing first-rater scope exceptions. Confusion matrices '
             '(first rater rows, second rater columns) are in `second_rater_comparison.json`.', '',
             '| Dataset | 4-way agreement | 4-way κ | Fit/no-fit agreement | Fit/no-fit κ |',
             '|---|---:|---:|---:|---:|']
    for d in DATASETS:
        a, b = results[d]['four_way'], results[d]['collapsed']
        fmt = lambda v: 'undefined (pₑ = 1)' if v is None else f'{v:.4f}'
        lines.append(f"| {DISPLAY[d]} | {a['matching']}/30 ({100*a['observed']:.1f}%) | {fmt(a['kappa'])} | "
                     f"{b['matching']}/30 ({100*b['observed']:.1f}%) | {fmt(b['kappa'])} |")
    lines += ['', 'Kappa is undefined when both marginal distributions put all items '
              'in the same category; perfect observed agreement is still reported.', '',
              '## Proposed adjudication', '',
              'These are Worker X proposals after seeing both rationales, not an independent '
              'third rating or accepted consensus. Frozen second-rater labels are unchanged. '
              'All matching labels are retained; each disagreement is addressed below.', '',
              proposed_rates, '', '## What v0 would need next', '',
              'Counts use frozen NO and OPAQUE items. An item counts once per construct family '
              'and can contribute to multiple families; column sums are not sample sizes. '
              'The tag-to-family mapping and item memberships are committed for inspection.', '',
              roadmap_table, '', 'After proposed adjudication:', '', proposed_roadmap_table, '',
              '## Every disagreement', '']
    for d in DATASETS:
        selected = [r for r in disagreements if r['dataset'] == d]
        lines += [f'### {DISPLAY[d]} ({len(selected)})', '']
        if not selected:
            lines += ['None.', '']
        for r in selected:
            lines += [f"**`{r['id']}`**", '',
                      f"- First: **{r['first_label']}** — {r['first_rationale']}",
                      f"- Second: **{r['second_label']}** — {r['second_rationale']}",
                      f"- Proposed: **{r['proposed_adjudicated_label']}** — {r['adjudication_reason']}", '']
    (ROOT / 'SECOND_RATER.md').write_text('\n'.join(lines))
    print(json.dumps({'n': len(rows), 'disagreements': len(disagreements), 'counts': count_rows(rows)}, indent=2))


def selftest():
    # Hand-checkable cases test chance correction, degenerate marginals and endpoints.
    a = agreement(['a', 'a', 'b', 'b'], ['a', 'b', 'b', 'b'], ('a', 'b'))
    assert a['observed'] == 0.75 and a['expected'] == 0.5 and a['kappa'] == 0.5
    assert agreement(['a'] * 30, ['a'] * 30, ('a', 'b'))['kappa'] is None
    assert agreement(['a', 'b'], ['b', 'a'], ('a', 'b'))['kappa'] == -1
    assert abs(wilson(0)['ci_high'] - 0.1135133931739688) < 1e-12
    assert abs(wilson(30)['ci_low'] - 0.8864866068260312) < 1e-12
    assert abs(wilson(15)['ci_low'] + wilson(15)['ci_high'] - 1) < 1e-12
    print('Statistical self-tests passed (kappa, degeneracy, Wilson endpoints and symmetry).')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('freeze', 'verify', 'compare', 'report', 'selftest'))
    parser.add_argument('--checker-dir', default='/private/tmp/ve-e0-integration')
    args = parser.parse_args()
    if args.command == 'freeze':
        freeze(args.checker_dir)
    elif args.command == 'verify':
        rows = verify_seal(args.checker_dir)
        print(f'Verified freeze, source hashes, sample IDs and all recorded witnesses: {len(rows)} items.')
    elif args.command == 'compare':
        rows, results, disagreements = comparison()
        print(json.dumps({'n': len(rows), 'agreement': results, 'disagreements': len(disagreements)}, indent=2))
    elif args.command == 'report':
        report()
    else:
        selftest()


if __name__ == '__main__':
    main()
