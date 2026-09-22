"""Separate offline prose pass: only natural-language dossiers are accepted.

No VE imports, labels, formulas, witnesses or solver calls. This deterministic
editor is a draft for inspection, NOT the registered independent Qwen72 pass.
The paid runner can replace drafts with one durable Qwen call per slot later.
"""
from copy import deepcopy
from ve_experiments.paid import digest

ALLOWED = {'id','glossary','premises','records','nodes','root','argument'}


def offline_pass(dossiers):
    result = []
    for dossier in dossiers:
        if set(dossier) != ALLOWED:
            raise ValueError('paraphraser input must be the natural-language dossier allowlist')
        nodes = deepcopy(dossier['nodes'])
        for node in nodes:
            node['text'] = 'For ' + node['text'].replace(' is ', ': ', 1)
        result.append({'id':dossier['id'], 'nodes':nodes,
            'argument':'Taken together, the stated facts and cited rules are offered as grounds for the final claim.',
            'provenance':{'method':'separate deterministic offline draft editor v1',
                'input_sha256':digest(dossier), 'input_fields':sorted(ALLOWED),
                'independent_qwen_pass':False, 'paid_calls':0,
                'limitation':'Not independent semantic paraphrasing; must be replaced and reviewed before scoring.'}})
    return result


def main():
    import json, sys
    json.dump(offline_pass(json.load(sys.stdin)), sys.stdout)

if __name__ == '__main__':
    main()
