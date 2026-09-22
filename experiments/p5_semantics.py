"""Fail-closed prose licensing, using only text, glossary and source records.

Search zero-relaxation readings first, then all one-bridge readings. This is a
material check, not a judge: hidden labels and formal graphs are never inputs.
Unsupported prose is rejected for review, never silently rewritten.
"""
import itertools
import json
import re
from collections import Counter
from experiments.p5_paraphrase import inference_parts, validate_reply
from ve_experiments.paid import digest

ATOM = re.compile(r'(unit\d+) is ([a-z-]+)(?: \(([a-z -]+)\))?')
CLAIM = re.compile(r'(?<!\w)unit\d+ is [a-z]+(?:-[a-z]+)*(?![\w-])')
REF = re.compile(r'the immediately preceding ([a-z-]+) result(?: holds)?', re.I)
MIN_DISTANCE = .20


def mask_claims(text):
    """Replace each verbatim atomic phrase with one fixed character.

    Preserve case, whitespace, punctuation and multiplicity elsewhere. Identity
    and content preservation are checked separately, before accepting distance.
    """
    return CLAIM.sub('#', text)


def edit_distance(a, b):
    """Normalized character Levenshtein (Myers bit-vector, no optional library)."""
    if not a or not b:
        return float(bool(a or b))
    masks = {}
    for i, char in enumerate(a):
        masks[char] = masks.get(char, 0) | (1 << i)
    positive, negative, score = ~0, 0, len(a)
    last = 1 << (len(a) - 1)
    for char in b:
        equal = masks.get(char, 0)
        xv = equal | negative
        xh = (((equal & positive) + positive) ^ positive) | equal
        ph, mh = negative | ~(xh | positive), positive & xh
        score += bool(ph & last) - bool(mh & last)
        ph = (ph << 1) | 1
        positive, negative = (mh << 1) | ~(xv | ph), ph & xv
    return score / max(len(a), len(b))


def parts(text):
    text = re.sub(r'^\[n\d+\] ', '', text).strip()
    # Conditional alternatives can move within the step or change discourse
    # framing, but must remain conditional and preserve the paired alternatives.
    sentences = re.findall(r'[^.]+(?:\.|$)', text)
    tails = [s for s in sentences if 'would' in s.split()]
    if len(tails) > 1:
        raise ValueError('multiple conditional alternative sentences')
    tail = tails[0].strip() if tails else ''
    head = ' '.join(s.strip() for s in sentences if s not in tails)
    # Conclusion-first and premise-first structures, including split sentences.
    atom = r'unit\d+ is [a-z-]+'
    # Match the whole inference before the legacy parser: its broad conclusion
    # capture mistakes discourse framing after a comma for predicate wording.
    m = re.fullmatch(r'(?:From (?:the fact|the facts) that |Given that |Since |Because )(.+?), '
                     r'(?:it follows that |we infer that |we conclude that )?(' + atom + r')\.', head)
    if m:
        return m[1], m[2], tail
    m = re.fullmatch(r'(?:It follows that |We infer that |We conclude that |The conclusion is that )?('
                     + atom + r')[,;]? (?:because|on the grounds that|is inferred from the fact that|'
                     r'follows from the fact that) (.+)\.', head)
    if m:
        return m[2], m[1], tail
    m = re.fullmatch(r'(?:We conclude that |The conclusion is that )?(' + atom +
                     r')[,;]? (?:because|on the grounds that) (.+)\.', head, re.I)
    if m:
        return m[2], m[1], tail
    m = re.fullmatch(r'(.+?)[.;,] (?:Thus|Therefore|So|Hence|We conclude that|It follows that)[,:]? (?:that )?(' + atom + r')\.', head, re.I)
    if m:
        return m[1], m[2], tail
    try:
        ant, con, old_tail, _ = inference_parts(head)
        if old_tail:
            raise ValueError('unparsed extra assertion')
        return ant, con, tail
    except ValueError:
        pass
    raise ValueError('unsupported inference syntax; preserve literal atom clauses and explicit inference direction')


def alternatives(text):
    if not text:
        return ()
    patterns = (
        r'The checks that (.+) would (?:yield|imply|establish) that (.+), respectively\.',
        r'If (.+), then (.+) would follow, respectively\.',
        r'Given the checks that (.+), (.+) would follow, respectively\.',
        r'(.+) would follow from the checks that (.+), respectively\.',
    )
    for index, pattern in enumerate(patterns):
        match = re.fullmatch(pattern, text)
        if not match:
            continue
        ant, con = match.groups()[::-1] if index == 3 else match.groups()
        sides = []
        for side in (ant, con):
            atoms = CLAIM.findall(side)
            residue = CLAIM.sub('', side)
            if not atoms or set(re.findall(r'\w+', residue)) - {'and'}:
                raise ValueError('unparsed conditional alternatives')
            sides.append(atoms)
        if len(sides[0]) != len(sides[1]):
            raise ValueError('conditional alternative pairing changed')
        return tuple(sorted(zip(*sides)))
    raise ValueError('unsupported conditional alternatives')


def step(text):
    ant, con, tail = parts(text)
    if '(' in text or ')' in text:
        raise ValueError('sense gloss in argument')
    conclusion = ATOM.fullmatch(con)
    if not conclusion:
        raise ValueError('unsupported conclusion')
    slots = [('literal', m[0], m[1]) for m in ATOM.findall(ant)]
    slots += [('reference', term.lower()) for term in REF.findall(ant)]
    residue = REF.sub('', ATOM.sub('', ant)).lower()
    # Only non-substantive framing may remain outside atom clauses. In
    # particular, negation/modality/extra assertions cannot evade extraction.
    allowed = {'and','because','since','given','that','we','have','take','as',
               'our','starting','points','premises','these','facts','together',
               'with','the','result','holds','from','using','on','basis','of',
               'this','reasoning','rests','following','information','is','are',
               'established','provides','grounds','for','inference','here',
               'first','also','now','both','a','pair','namely','fact',
               'consider','considered','taken','stated','given','have','been'}
    if set(re.findall(r'[a-z0-9-]+', residue)) - allowed:
        raise ValueError('unparsed substantive premise wording')
    if not slots:
        raise ValueError('missing premises')
    return {'slots': slots, 'conclusion': conclusion.groups()[:2], 'tail': alternatives(tail)}


def parse(packet):
    paragraphs = packet['argument'].split('\n\n')
    if len(paragraphs) != len(packet['nodes']):
        raise ValueError('step count changed')
    return [dict(step(t), id=n['id']) for n, t in zip(packet['nodes'], paragraphs)]


def licensing(packet):
    senses = {}
    for g in packet['glossary']:
        sense = g['sense'].split(': ', 1)[1].split(' (R', 1)[0]
        senses.setdefault(g['term'], set()).add(sense)
    def atoms(text):
        result = []
        for unit, term, sense in ATOM.findall(text):
            if not sense:
                if len(senses[term]) != 1:
                    raise ValueError('ambiguous source atom')
                sense = next(iter(senses[term]))
            if sense not in senses[term]:
                raise ValueError('unknown sense')
            result.append((unit, term, sense))
        return result
    rules = []
    for record in packet['records']:
        for ant, con in re.findall(r'If (.*?), then (.*?)\.', record['text']):
            rules.append((atoms(ant), atoms(con)[0]))
    facts = set()
    for premise in packet['premises']:
        facts.update(atoms(premise['text'].split('. The checks that')[0]))
    nodes = parse(packet)
    def search(budget):
        readings = set()
        def visit(index, assigned, issues):
            if index == len(nodes):
                readings.add((tuple(issues), tuple(assigned)))
                return
            node = nodes[index]
            for required, output in rules:
                if output[:2] != node['conclusion'] or len(required) != len(node['slots']):
                    continue
                for order in set(itertools.permutations(required)):
                    choices = []
                    for slot, want in zip(node['slots'], order):
                        if slot[0] == 'reference':
                            actual = [assigned[-1]] if assigned and assigned[-1][1] == slot[1] else []
                            producer = nodes[index-1]['id'] if index else None
                        else:
                            actual = [a for a in facts | set(assigned) if a[:2] == slot[1:]]
                            producer = None
                        options = []
                        for got in actual:
                            if got == want:
                                options.append(None)
                            elif got[:2] == want[:2] and got[2] != want[2]:
                                options.append(('shift', producer, node['id']))
                            elif got[1:] == want[1:] and got[0] != want[0]:
                                options.append(('smuggle', producer, node['id']))
                        choices.append(set(options))
                    for chosen in itertools.product(*choices):
                        new = issues + [c for c in chosen if c is not None]
                        if len(new) <= budget:
                            visit(index+1, assigned+[output], new)
        visit(0, [], [])
        return readings
    readings = search(0)
    if not readings:
        readings = search(1)
    if not readings:
        raise ValueError('no zero- or one-relaxation licensing reading')
    diagnoses = sorted({('benign', ()) if not issues else
                        (issues[0][0], tuple(x for x in issues[0][1:] if x))
                        for issues, _ in readings})
    return {'diagnoses': diagnoses, 'readings_sha256': digest(sorted(readings)),
            'readings': len(readings)}


def acceptance_check(dossier, texts):
    checked, violation = validate_reply(json.dumps({'texts': texts}), dossier)
    if violation or checked != texts:
        return {'passed': False, 'error': violation or 'unsanitised glossary sense in prose'}
    source = {**dossier, 'argument': '\n\n'.join(n['text'] for n in dossier['nodes'])}
    rewritten = {**dossier, 'argument': '\n\n'.join(texts[n['id']] for n in dossier['nodes'])}
    distance = edit_distance(mask_claims(source['argument']), mask_claims(rewritten['argument']))
    result = {'passed': False, 'normalized_levenshtein': distance, 'minimum': MIN_DISTANCE,
              'distance_basis': 'atomic-phrases-masked-with-#; character-distance/max-length',
              'method': 'constrained-atomic-verbatim-public-record-licensing-v7'}
    try:
        if set(texts) != {n['id'] for n in dossier['nodes']}:
            raise ValueError('step IDs changed')
        for node in dossier['nodes']:
            if (Counter(CLAIM.findall(node['text'])) != Counter(CLAIM.findall(texts[node['id']]))
                    or Counter(re.findall(r'\bunit\d+\b', node['text'])) !=
                    Counter(re.findall(r'\bunit\d+\b', texts[node['id']]))):
                raise ValueError('atomic claim phrases or unit names changed; preserve them verbatim')
        before, after = parse(source), parse(rewritten)
        for a, b in zip(before, after):
            if (a['conclusion'] != b['conclusion'] or Counter(a['slots']) != Counter(b['slots'])
                    or a['tail'] != b['tail']):
                raise ValueError('step content, immediate reference, or conditional alternatives changed')
        original, candidate = licensing(source), licensing(rewritten)
        result.update(source=original, paraphrase=candidate,
                      passed=original == candidate and distance >= MIN_DISTANCE)
    except (ValueError, KeyError) as exc:
        result['error'] = str(exc)
    return result
