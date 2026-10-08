"""Render the saved readability comparison; no checkout or live git queries."""
from __future__ import annotations
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
BASE='9aaf918d538a35e63d64a7c5abc86bbcfbb87472'
MERGE='9cc8418d'
FREEZE='ac91e1e4'

def read(name):
    return [json.loads(line) for line in (HERE/name).read_text().splitlines()]

def escaped(value):
    return (value or '').replace('|','\\|').replace('\n','<br>')

def render():
    wb, wh, ws = (read(f'readability-{name}.jsonl') for name in ('base','head','shadow'))
    rb, rh = (read(f'readability-reading-{name}.jsonl') for name in ('base','head'))
    assert len(wb)==len(wh)==len(ws)==36 and len(rb)==len(rh)==30
    changed=[]
    for a,b,c in zip(wb,wh,ws,strict=True):
        assert (a['task'],a['session'],a['attempt'],a['sentence']) == (b['task'],b['session'],b['attempt'],b['sentence']) == (c['task'],c['session'],c['attempt'],c['sentence'])
        if (a['outcome'],a['ve_message'])!=(b['outcome'],b['ve_message']): changed.append((a,b))
    reading_changes=[(a,b) for a,b in zip(rb,rh,strict=True) if (a['verdict'],a['message'])!=(b['verdict'],b['message'])]
    summary={'format':'ve-e2-readability-comparison@1','base_commit':BASE,'review_merge':MERGE,'frozen_eval_commit':FREEZE,
             'writing_attempts':len(wb),'writing_verdict_changes':sum(a['outcome']!=b['outcome'] for a,b in zip(wb,wh)),
             'writing_message_changes':len(changed),'shadow_writing_differences':sum((a['outcome'],a['ve_message'])!=(c['outcome'],c['ve_message']) for a,c in zip(wb,ws)),
             'reading_items':len(rb),'reading_differences':len(reading_changes),
             'reading_unavailable_both':[a['item'] for a,b in zip(rb,rh) if a['verdict']==b['verdict']=='unavailable'],
             'reading_newly_unavailable':[a['item'] for a,b in reading_changes if a['verdict']!='unavailable' and b['verdict']=='unavailable'],
             'message_preservation':'failed: six changed writing messages omit base names or suggestions; R23-R25 and R29-R30 become unavailable'}
    (HERE/'readability-comparison.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
    lines=['# E2.5 readability replay','',f'Frozen evaluation `{FREEZE}`; base `{BASE[:8]}`; reviewed merge `{MERGE}`. The saved writing files hold every one of the 36 recorded attempts and their scorer verdict and displayed message. The saved reading files hold all 30 item keys and VE verdict sentences, including replay errors. No model was called.','',f'Writing: {len(changed)} changed messages, 0 changed scorer verdicts. On Python authority with Lean in shadow, all {len(ws)} writing verdicts and messages match the base. Reading: {len(reading_changes)} changed item outcomes; {len(summary["reading_newly_unavailable"])} became unavailable on the current checkout. The risk calls use the current route signature, and the speech replay has the frozen evaluation import path available.','','## Changed writing messages at the reviewed merge','', '| Item | Base verdict | Base message | Merge verdict | Merge message |','|---|---|---|---|---|']
    for a,b in changed:
        lines.append(f"| {a['task']} {a['session']} attempt {a['attempt']} | {a['outcome']} | {escaped(a['ve_message'])} | {b['outcome']} | {escaped(b['ve_message'])} |")
    lines += ['','These six changed texts fail the specified preservation test: W08 loses the paraphrase suggestion; W12 loses the base named phrase or paraphrase suggestion; W14 loses the paraphrase suggestion. The replacement for W12 attempt 1 adds a useful rewrite but does not retain the base named phrase.','', '## Changed reading items after the authority revert','', '| Item | Base verdict | Base message | Current verdict | Current message |','|---|---|---|---|---|']
    for a,b in reading_changes:
        lines.append(f"| {a['item']} | {a['verdict']} | {escaped(a['message'])} | {b['verdict']} | {escaped(b['message'])} |")
    lines += ['','R23–R25 became unavailable because the frozen scorer imports `SpeechDocument` from `ve.speech_acts`, which the current checkout no longer exports. R29 and R30 became unavailable because the current checker rejects constant `verbalisation` fields in the frozen evaluation environment. These five items are not counted as preserved.','']
    (HERE/'readability-changes.md').write_text('\n'.join(lines))
    print(json.dumps(summary,indent=2))

if __name__=='__main__': render()
