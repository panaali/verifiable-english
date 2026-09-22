"""Dated P5 schedule amendment; retained envelopes are never refunded."""
from collections import defaultdict
from decimal import Decimal
import json
from hashlib import sha256

from ve_experiments.paid import cost, PreflightError


def plan():
    from experiments import p5 as p
    return json.loads((p.HERE/'checks/budget-scenarios.json').read_text())


def family_names(count):
    from experiments import p5 as p
    if count not in range(3, 25, 3):
        raise ValueError('scored families must be a positive multiple of three <=24')
    strata = defaultdict(set)
    for row in p.labels(False):
        if row['split'] == 'scored':
            strata[row['predicates']].add(row['family'])
    return sorted(f for names in strata.values() for f in sorted(names)[:count//3])


def selected_materials(split=None):
    from experiments import p5 as p
    selected = set(family_names(plan()['scenarios'][0]['scored_families']))
    return [i for i in p.materials(split) if i['split'] == 'dev' or i['group'] in selected]


def item_charges():
    from experiments import p5 as p
    shared, _ = p.revision_paraphrase_costs(p.HERE)
    charged = defaultdict(Decimal)
    # Freeze accounting at the pre-calibration amendment boundary. Subsequent
    # study spend consumes these reservations; it is not a new planning cost.
    prefix = (p.HERE/'runs/study/costs.jsonl').read_bytes()[:plan()['ledger_prefix_bytes']]
    if sha256(prefix).hexdigest() != plan()['ledger_prefix_sha256']:
        raise PreflightError('retained budget ledger prefix changed')
    rows = [json.loads(line) for line in prefix.splitlines()]
    requests = {r['identity']: r for r in rows if r['event'] == 'reserve'}
    for row in rows:
        if row['event'] not in ('complete', 'interrupted', 'infrastructure_failure', 'panel_halt'):
            continue
        meta = requests.get(row.get('identity'), {}).get('metadata', {})
        amount = Decimal(row.get('cost_usd', row.get('infrastructure_hold_usd', '0')))
        if meta.get('role') == 'paraphrase':
            shared[meta['item_id']] += amount
        elif meta.get('arm') in p.ARMS:
            charged[meta['item_id'], meta['arm']] += amount
    return shared, charged


def ceilings(scenario, scored_families=None):
    from experiments import p5 as p
    if scenario not in p.SCENARIOS:
        raise ValueError('unknown scenario')
    data = plan()
    count = data['scenarios'][0]['scored_families'] if scored_families is None else scored_families
    families = set(family_names(count))
    items = [i for i in p.materials() if i['split'] == 'dev' or i['group'] in families]
    arms = {a: sum((cost('pro', *p.stage_limits(a, s)) for s in p.stage_list(a)), Decimal(0)) for a in p.ARMS}
    extra = {a: cost('replication', *p.stage_limits(a, 'lone' if a == 'L' else 'judge', 'replication'))
             if scenario == 'dual_judge' else Decimal(0) for a in p.ARMS}
    shared, charged = item_charges()
    attributed = {a: max(arms[a]+extra[a]+max(shared[i['id']], cost('replication', *p.STAGES['paraphrase']))
                        +charged[i['id'], a]+Decimal('.0004') for i in items) for a in p.ARMS}
    online = sum(arms.values())+sum(extra.values())
    retained = Decimal(data['retained_commitment_usd'])
    calibration = Decimal(data['calibration_task_cap_usd'])
    total = retained+calibration+len(items)*online
    return {'scenario': scenario, 'scored_families': count, 'dev_families': 4,
            'scheduled_items': len(items), 'selected_scored_families': sorted(families),
            'retained_commitment_usd': str(retained), 'cpu_usd': '.1344',
            'cpu_accounting': 'already included in retained commitment; no duplicate charge',
            'gemini_calibration_ceiling_usd': str(calibration),
            'api_usd': str(len(items)*online), 'all_in_usd': str(total),
            'reserve_usd': str(p.CAP-total), 'within_cap': total <= p.CAP,
            'matched_ceiling_usd': str(p.MATCHED_CAP),
            'within_matched_ceiling': all(v <= p.MATCHED_CAP for v in attributed.values()),
            'combined_attributed_item_arm_usd': {a: str(v) for a, v in attributed.items()},
            'replication_judge_overhead_usd': str(len(items)*sum(extra.values())),
            'future_online_calls': len(items)*(sum(len(p.stage_list(a)) for a in p.ARMS)+(4 if scenario == 'dual_judge' else 0)),
            'primary': 'Gemini min(VE_shift,VE_smuggle) - min(X_shift,X_smuggle)',
            'replication_policy': 'same frozen Gemini transcript; Qwen final judgment and lone floor'}
