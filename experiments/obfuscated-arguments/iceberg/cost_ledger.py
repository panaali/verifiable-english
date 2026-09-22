#!/usr/bin/env python3
"""Aggregate this worker's Codex token_count events; never copies conversation text.
Usage: python3 .../cost_ledger.py /path/to/this-session-rollout.jsonl
Phase boundaries are observations from this run, not a generic benchmark.
"""
import datetime as dt
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
source = Path(sys.argv[1])
events = []
model = None
for line in source.open():
    event = json.loads(line)
    if event.get('type') == 'turn_context':
        model = event['payload'].get('model')
    if event.get('type') == 'event_msg' and event['payload'].get('type') == 'token_count':
        info = event['payload'].get('info')
        if info:
            events.append({'timestamp':event['timestamp'], 'total':info['total_token_usage']})
assert events
stamp = lambda s: dt.datetime.fromisoformat(s.replace('Z','+00:00'))
cutoff = events[-1]['timestamp']
bounds = [
    ('model_review','2026-09-22T22:55:57+00:00','2026-09-22T22:58:34+00:00'),
    ('formalisation','2026-09-22T22:58:34+00:00','2026-09-22T23:00:58.100682+00:00'),
    ('proof_repair','2026-09-22T23:00:58.100682+00:00','2026-09-22T23:05:42.366527+00:00'),
    ('checking','2026-09-22T23:05:42.366527+00:00',cutoff),
]
keys = ['input_tokens','cached_input_tokens','output_tokens','reasoning_output_tokens','total_tokens']
previous = dict.fromkeys(keys,0)
rows = []
for name, start, end in bounds:
    eligible = [e for e in events if stamp(e['timestamp']) <= stamp(end)]
    cumulative = eligible[-1]['total'] if eligible else previous
    usage = {k:cumulative.get(k,0)-previous.get(k,0) for k in keys}
    previous = cumulative
    rows.append(dict(phase=name,start=start,end=end,
                     wall_seconds=round((stamp(end)-stamp(start)).total_seconds(),6),**usage))
attempts = [json.loads(line) for line in (HERE/'attempts.jsonl').read_text().splitlines()]
checks = json.loads((HERE/'verification.json').read_text())['records']
qual = json.loads((HERE/'qualitative-verification.json').read_text())
record = dict(model=model,cutoff=cutoff,phases=rows,total_usage=events[-1]['total'],
              token_count_snapshots=events,
              failed_development_invocations=sum(a['exit_code']!=0 for a in attempts),
              development_invocations=len(attempts),
              development_lean_seconds=sum(a['seconds'] for a in attempts),
              serial_build_and_final_audit_seconds=sum(c['seconds'] for c in checks),
              final_fresh_lean_seconds=checks[-1]['seconds'],
              qualitative_check_seconds=qual['seconds'],
              scope='Session telemetry through cutoff; final ledger write, commit, and final reply after cutoff excluded. '
                    'Input is summed per request and includes cached/repeated context; reasoning is a subset of output. '
                    'Phase assignments use request-event timestamps and contiguous coarse work windows, not CPU attribution.')
(HERE/'cost.json').write_text(json.dumps(record,indent=2)+'\n')
lines=['# Measured cost ledger','',f'Model: `{model}`. Date: 2026-09-22. One implementing agent; no delegated or independent review.',
       '',f'Cutoff: **{cutoff}**. Start: 22:55:57 UTC (first clock observation).',
       'Costs after the cutoff (final ledger write/commit/reply) are excluded, not estimated.',
       '', '| Phase | Wall seconds | Input tokens | Cached input subset | Output tokens | Reasoning subset |',
       '|---|---:|---:|---:|---:|---:|']
for r in rows:
    lines.append(f"| {r['phase']} | {r['wall_seconds']:.3f} | {r['input_tokens']:,} | {r['cached_input_tokens']:,} | {r['output_tokens']:,} | {r['reasoning_output_tokens']:,} |")
t=record['total_usage'];wall=sum(r['wall_seconds'] for r in rows)
lines += [f"| **Total** | **{wall:.3f}** | **{t['input_tokens']:,}** | **{t['cached_input_tokens']:,}** | **{t['output_tokens']:,}** | **{t['reasoning_output_tokens']:,}** |",'',
          'These are actual cumulative Codex `token_count` deltas, not a word-count estimate. Input tokens',
          'include the initial instructions, tools and repeated context for each request; cached input is',
          'a subset of input, and reasoning is a subset of output. Do not add either subset again.',
          'This is usage accounting, not distinct transcript length or a dollar bill. Subscription quota',
          'only; no paid model API, GPU, dollar estimate or hidden parallel worker cost is included.', '',
          'The phase windows are coarse, contiguous wall-clock measurements. Model review includes source',
          'retrieval and idealisation decisions. Formalisation includes writing SPEC and the first proof.',
          'Repair includes compiler diagnosis, checklist writing, and non-vacuity witness authoring/repair.',
          'Checking includes serial build, VE skeleton/certificate preparation, documentation and ledger',
          'work through the cutoff. Token events are charged to the window of their timestamp; requests',
          'can straddle a boundary. This is not CPU time or an independently observed human-work estimate.', '',
          '## Attempts and compute','',
          f"- **{record['failed_development_invocations']} failed invocations out of {len(attempts)}** standalone Lean development runs; multiple cascading diagnostics count as one invocation.",
          '- Attempt 1: grouped structure-field syntax and unassisted order cancellation.',
          '- Attempt 2: nonlinear order/cancellation needed explicit rational lemmas.',
          '- Attempt 3: missing `Rat.mul_sub` name and rational `decide` reduction.',
          '- Attempt 4: the main proof and all original 11 result audits passed.',
          '- Attempt 5: newly added witness tactics failed when `dsimp` made no progress.',
          '- Attempt 6: the complete source and all 13 audits passed.',
          f"- Development Lean subprocess wall time: **{record['development_lean_seconds']:.3f} s** (all attempts).",
          f"- Clean-worktree serial whole-project build plus final audit: **{record['serial_build_and_final_audit_seconds']:.3f} s** across {len(checks)} commands; no initial local `.lake` directory.",
          f"- Final fresh standalone proof/audit invocation: **{record['final_fresh_lean_seconds']:.3f} s**, already included above.",
          f"- VE relational search and Python/Lean replay: **{record['qualitative_check_seconds']:.3f} s** (excludes Python startup and rendering).",
          '- All compute durations are subsets of phase wall time; do not add them to that total.',
          '- No failed whole-project builds or VE certificate replays. The unavailable in-app browser was a source-retrieval fallback, not a failed proof.', '',
          'Reproduction evidence: `attempts.jsonl`, `verification.json`, and',
          '`qualitative-verification.json`. `cost.json` retains only token-counter snapshots,',
          'not conversation content. `cost_ledger.py` regenerates the accounting from this',
          'worker\'s local rollout; the original private transcript is not part of the commit.', '',
          'One pilot on a fixed idealisation is not an affordability benchmark across physics,',
          'and does not compare against a measured debate run. Physical validation and a proved',
          'Lean-to-VE translation remain additional costs.']
(HERE/'COST.md').write_text('\n'.join(lines)+'\n')
print(json.dumps({k:record[k] for k in ['model','cutoff','phases','total_usage','failed_development_invocations','serial_build_and_final_audit_seconds','final_fresh_lean_seconds']},indent=2))
