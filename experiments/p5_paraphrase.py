"""Separate offline prose pass: only natural-language dossiers are accepted.

No VE imports, labels, formulas, witnesses or solver calls. This deterministic
editor is a draft for inspection, NOT the registered independent Qwen72 pass.
The paid runner can replace drafts with one durable Qwen call per slot later.
"""
import re
from ve_experiments.paid import digest

ALLOWED = {'id','glossary','premises','records','nodes','root','argument'}


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
            head, sep, tail = node['text'].partition('. ')
            match = re.fullmatch(r'(?:Given|From|Using) (.*), (unit\d+ is .+?)\.?', head)
            if not match:
                raise ValueError('unparsed source inference')
            text = f"Taking {match[1]} as premises, we conclude that {match[2].rstrip('.')}."
            if sep:
                text += ' ' + tail
            paragraphs.append(f"[{node['id']}] {text}")
        result.append({'id':dossier['id'], 'argument':'\n\n'.join(paragraphs),
            'provenance':{'method':'separate offline topological prose rendering pass v4',
                'input_sha256':digest(dossier), 'input_fields':sorted(ALLOWED),
                'independent_qwen_pass':False, 'paid_calls':0,
                'limitation':'Not independent semantic paraphrasing; must be replaced and reviewed before scoring.'}})
    return result


def main():
    import json, sys
    json.dump(offline_pass(json.load(sys.stdin)), sys.stdout)

if __name__ == '__main__':
    main()
