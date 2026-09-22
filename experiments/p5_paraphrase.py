"""Separate offline prose pass: only natural-language dossiers are accepted.

No VE imports, labels, formulas, witnesses or solver calls. This deterministic
editor is a draft for inspection, NOT the registered independent Qwen72 pass.
The paid runner can replace drafts with one durable Qwen call per slot later.
"""
import re
from ve_experiments.paid import digest

ALLOWED = {'id','glossary','premises','records','nodes','root','argument'}


FRAMES = (
    'Because {premises}, {conclusion}.',
    'Since {premises}, it follows that {conclusion}.',
    'Given that {premises}, we infer that {conclusion}.',
    'It follows that {conclusion} because {premises}.',
)


def render_inference(premises, conclusion, frame):
    return FRAMES[frame].format(premises=premises, conclusion=conclusion)


def inference_parts(text):
    head, sep, tail = text.partition('. ')
    patterns = (
        r'Because (.*), (unit\d+ is .+?)\.?',
        r'Since (.*), it follows that (unit\d+ is .+?)\.?',
        r'Given that (.*), we infer that (unit\d+ is .+?)\.?',
        r'It follows that (unit\d+ is .+?) because (.*?)\.?',
    )
    for frame, pattern in enumerate(patterns):
        match = re.fullmatch(pattern, head)
        if match:
            premises, conclusion = match.groups()[::-1] if frame == 3 else match.groups()
            return premises, conclusion.rstrip('.'), tail if sep else '', frame
    raise ValueError('unparsed inference node')


def offline_pass(dossiers):
    if len(dossiers) != 1:
        raise ValueError('paraphrase contexts must contain exactly one packet')
    result = []
    for dossier in dossiers:
        if set(dossier) != ALLOWED:
            raise ValueError('paraphraser input must be the natural-language dossier allowlist')
        paragraphs = []
        seen = {n['id'] for n in dossier['premises']}
        for node in dossier['nodes']:
            if not set(node['parents']) <= seen:
                raise ValueError('prose must follow topological order')
            seen.add(node['id'])
            premises, conclusion, tail, frame = inference_parts(node['text'])
            text = render_inference(premises, conclusion, frame)
            if tail:
                text += ' ' + tail
            paragraphs.append(f"[{node['id']}] {text}")
        result.append({'id':dossier['id'], 'argument':'\n\n'.join(paragraphs),
            'provenance':{'method':'separate offline topological prose rendering pass v5',
                'input_sha256':digest(dossier), 'input_fields':sorted(ALLOWED),
                'independent_qwen_pass':False, 'paid_calls':0,
                'limitation':'Not independent semantic paraphrasing; must be replaced and reviewed before scoring.'}})
    return result


def main():
    import json, sys
    json.dump(offline_pass(json.load(sys.stdin)), sys.stdout)

if __name__ == '__main__':
    main()
