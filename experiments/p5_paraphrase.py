"""Separate offline prose pass: only natural-language dossiers are accepted.

No VE imports, labels, formulas, witnesses or solver calls. This deterministic
editor is a draft for inspection, NOT the registered independent Qwen72 pass.
The paid runner replaces drafts with validated, ledger-backed Qwen responses.
"""
import json
import re
from ve_experiments.json_response import strip_json_fence
from ve_experiments.paid import digest

ALLOWED = {'id','glossary','premises','records','nodes','root','argument'}


def _unique_object(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError(f'duplicate JSON key: {key}')
        obj[key] = value
    return obj


SANITISER = 'exact-parenthetical-glossary-sense-v1'


def glossary_senses(dossier):
    senses = set()
    for entry in dossier['glossary']:
        sense = re.sub(r'\s*\(R\d+\)\s*$', '', entry['sense'], flags=re.I)
        sense = sense.partition(':')[2] if ':' in sense else sense
        if sense.strip():
            senses.add(' '.join(sense.casefold().split()))
    return sorted(senses)


def sanitise_prose(prose, senses):
    """Remove only entire, unnested parentheticals equal to a glossary sense.

    Case and whitespace are ignored for matching. No labels, synonyms or
    substring deletions; surrounding whitespace and punctuation are tidied.
    """
    pattern = re.compile(r'(?<!\()\([^()]*\)(?!\))')
    def replace(match):
        prefix = prose[:match.start()]
        if prefix.count('(') != prefix.count(')'):
            return match[0]  # Do not edit a gloss nested inside other parentheses.
        phrase = ' '.join(match[0][1:-1].casefold().split())
        return ' ' if phrase in senses else match[0]
    cleaned = pattern.sub(replace, prose)
    if cleaned != prose:
        cleaned = re.sub(r'\s+([,.;:!?])', r'\1', ' '.join(cleaned.split()))
    return cleaned


def validate_reply(text, dossier):
    """Return sanitised, ordered texts or a violation; inspect prose, not keys."""
    try:
        row = json.loads(strip_json_fence(text), object_pairs_hook=_unique_object)
    except (TypeError, ValueError):
        return None, 'parse_failure: expected one JSON object (optionally fenced), without duplicate keys'
    ids = [n['id'] for n in dossier['nodes']]
    if (not isinstance(row, dict) or set(row) != {'texts'}
            or not isinstance(row['texts'], dict) or set(row['texts']) != set(ids)
            or any(not isinstance(t, str) or not t.strip() for t in row['texts'].values())):
        return None, 'schema_failure: texts must contain every existing node ID exactly once with nonempty string values and no additional fields'
    # Glossary entries are "term: sense phrase (Rnn)". The Rnn suffix is a
    # glossary label, not part of the phrase that must stay out of parentheses.
    senses = glossary_senses(dossier)
    row['texts'] = {key: sanitise_prose(prose, senses) for key, prose in row['texts'].items()}
    if any(not prose.strip() for prose in row['texts'].values()):
        return None, 'schema_failure: sanitised texts must remain nonempty'
    public_ids = {n['id'] for field in ('nodes', 'premises', 'records') for n in dossier[field]}
    id_pattern = re.compile(r'(?<!\w)(?:[nr]\d+|' + '|'.join(map(re.escape, sorted(public_ids))) + r')(?!\w)', re.I)
    for node_id in ids:
        prose = row['texts'][node_id]
        match = id_pattern.search(prose)
        if match:
            return None, f'node/rule ID in prose at {node_id}: {match.group()}'
        for parenthetical in re.findall(r'\(([^()]*)\)', prose):
            normalized = ' '.join(parenthetical.casefold().split())
            for sense in senses:
                if re.search(r'(?<!\w)' + re.escape(sense) + r'(?!\w)', normalized):
                    return None, f'parenthetical glossary sense at {node_id}: {sense}'
    return {node_id: row['texts'][node_id] for node_id in ids}, None


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
