"""Display-only English overlays and conservative, explicitly accepted suggestions."""
from copy import deepcopy
import re
from importlib.resources import files

from .environment import Environment
from .errors import VEError
from .wire import canonical_json, digest, require_fields, loads_json

# Finite lexical idioms. These are atomic vocabulary, never new logical operators.
# Argument positions remain literal and in order, including trailing complements.
IDIOMS = {
    1: {
        '{0} is unanimous',
        '{0} is born in the United States',
        '{0} is a US citizen',
        '{0} is subject to US jurisdiction',
        '{0} has a noncitizen parent domiciled in the United States',
        '{0} has an undocumented noncitizen parent',
        '{0} has a noncitizen parent temporarily in the United States',
        '{0} is a current Claude model',
        '{0} is expected to have the core values',
        '{0} is inappropriately harmful',
        '{0} is inappropriately dangerous or harmful',
        '{0} involves a hard constraint violation',
        '{0} is an appropriately sanctioned human check',
    },
    2: {
        '{0} may access {1}',
        '{0} undermines {1}',
        '{0} interacts with {1}',
        '{0} involves apparent conflict over {1}',
        '{0} calls for generally prioritizing {1}',
        '{0} undermines the oversight role of {1}',
        '{0} owes unconditional obedience to {1}',
        '{0} raised its policy rate on {1}',
        '{0} voted for {1}',
        '{0} raised its policy rate to {1}',
        '{0} promised {1}',
        '{0} submitted a rate projection for {1}',
        '{0} is the first policy shift under {1}',
        '{0} was appointed by {1}',
        '{0} took office in {1}',
        '{0} is projected for the end of {1}',
        '{0} issued {1}',
        '{0} attributes elevated inflation to {1}',
        '{0} is scheduled for {1}',
        '{0} is projected to occur in {1}',
        '{0} pledged {1}',
        '{0} is a citizen of {1}',
        '{0} is within the jurisdiction of {1}',
        '{0} abridges the privileges or immunities of {1}',
        '{0} deprives {1} of life, liberty, or property',
    },
}


def negative_template(template, arity):
    from .printer import _negative_template
    if template.startswith('{0} is '):
        return template.replace('{0} is ', '{0} is not ', 1)
    if template.startswith('{0} was '):
        return template.replace('{0} was ', '{0} was not ', 1)
    if template.startswith('{0} has '):
        return template.replace('{0} has ', '{0} does not have ', 1)
    past = {'raised': 'raise', 'voted': 'vote', 'promised': 'promise',
            'submitted': 'submit', 'took': 'take', 'issued': 'issue', 'pledged': 'pledge'}
    verb = template.split()[1]
    if template in IDIOMS[arity] and verb in past:
        return template.replace('{0} ' + verb + ' ', '{0} did not ' + past[verb] + ' ', 1)
    return _negative_template(template, 2) if arity == 2 or template in IDIOMS[1] else None


def overlay_provenance(vocabulary):
    """Only the repository's pinned record can attest to a reviewed digest."""
    if vocabulary is None:
        return {'overlay_digest': None, 'review_status': 'not_applicable'}
    overlay_digest = digest('ve-english-vocabulary-v1\n', vocabulary)
    # Missing/unreadable review records fail closed, without affecting checking.
    try:
        records = loads_json(files('ve').joinpath('reviewed-overlays.json').read_bytes())
        reviewed = any(r.get('overlay_digest') == overlay_digest and r.get('reviewer')
                       and r.get('date') for r in records)
    except (OSError, VEError, TypeError, AttributeError):
        reviewed = False
    return {'overlay_digest': overlay_digest,
            'review_status': 'reviewed' if reviewed else 'unreviewed'}


def display_environment(env, vocabulary, accept_suggested_vocabulary):
    """Validate the entire overlay; never return a replacement identity environment."""
    if vocabulary is None:
        return env, None, {'sorts': {}, 'predicates': {}}
    canonical_json(vocabulary)
    require_fields(vocabulary, {'format', 'environment_id', 'sorts', 'predicates'})
    if vocabulary['format'] != 've.english-vocabulary@1' or vocabulary['environment_id'] != env.environment_id:
        raise VEError('English vocabulary format or environment_id does not match')
    data = env.to_dict()
    for category in ('sorts', 'predicates'):
        entries = vocabulary[category]
        if type(entries) is not dict:
            raise VEError('English vocabulary entries must be objects')
        for name, entry in entries.items():
            if name not in data['vocabulary'][category]:
                raise VEError(f'Unknown English vocabulary symbol: {name}')
            fields = {'verbalisation', 'suggested'}
            if category == 'predicates' and type(entry) is dict and 'negative_verbalisation' in entry:
                fields.add('negative_verbalisation')
            require_fields(entry, fields)
            if type(entry['suggested']) is not bool:
                raise VEError('suggested must be a boolean')
            if entry['suggested'] and not accept_suggested_vocabulary:
                raise VEError('Suggested vocabulary requires --accept-suggested-vocabulary (API: accept_suggested_vocabulary=True)')
            target = data['vocabulary'][category][name]
            # An old negative must not silently attach to a changed positive template.
            if category == 'predicates': target.pop('negative_verbalisation', None)
            target.update({k: deepcopy(v) for k, v in entry.items() if k != 'suggested'})
    return Environment(data), digest('ve-english-vocabulary-v1\n', vocabulary), vocabulary


def suggest_vocabulary(env):
    """Return lint-clean candidates, never automatically applied to an environment.

    Identifiers supply only finite safe morphological patterns. Descriptions may
    supply an exact 'Recorded as <adjective>.' gloss. Arbitrary prose, abbreviations,
    modality, and argument direction are not inferred.
    """
    from .english import EnglishVocabulary, _RESERVED
    result = {'format': 've.english-vocabulary@1', 'environment_id': env.environment_id,
              'sorts': {}, 'predicates': {}}
    adjectives = {'active', 'appropriate', 'deployed', 'eligible', 'exempt', 'harmful',
                  'honest', 'ready', 'relevant', 'reviewed', 'safe', 'unanimous', 'valid'}
    modifiers = {'fully', 'newly', 'currently', 'publicly', 'inappropriately'}
    verbs = {'owns', 'audits', 'undermines', 'performs', 'follows', 'benefits', 'outranks', 'exceeds'}
    for name, decl in sorted(env.sorts.items()):
        if decl.verbalisation: continue
        noun = name.replace('_', ' ')
        if re.fullmatch('[a-z]+(?: [a-z]+)*', noun) and not set(noun.split()) & _RESERVED:
            plural = {'person': 'people', 'property': 'properties'}.get(noun, noun + 's')
            result['sorts'][name] = {'verbalisation': {'singular': noun, 'plural': plural}, 'suggested': True}
    for name, decl in sorted(env.predicates.items()):
        if decl.verbalisation: continue
        template = None
        phrase = name.removeprefix('is_').replace('_', ' ')
        parts = phrase.split()
        if len(decl.arguments) == 1:
            if phrase in adjectives or (len(parts) == 2 and parts[0] in modifiers and parts[1] in adjectives):
                template = '{0} is ' + phrase
            elif name in {'born_in_us', 'naturalized_in_us'} and re.search(r'United States|U\.S\.', decl.description):
                template = '{0} was ' + name.split('_')[0] + ' in the United States'
            else:
                gloss = re.fullmatch(r'Recorded as ([a-z]+)\.', decl.description)
                if gloss and gloss[1] in adjectives: template = '{0} is ' + gloss[1]
        elif name in verbs:
            template = '{0} ' + name + ' {1}'
        elif name.startswith('has_') and re.fullmatch('[a-z]+(?:_[a-z]+)*', name):
            template = '{0} has ' + name[4:].replace('_', ' ') + ' {1}'
        if template:
            result['predicates'][name] = {'verbalisation': template, 'suggested': True}
    # Joint linting matters: two individually harmless suggestions may collide.
    while True:
        display, _, _ = display_environment(env, result, True)
        words = EnglishVocabulary(display)
        rejected = []
        for category in ('sorts', 'predicates'):
            for name, entry in result[category].items():
                target = entry['verbalisation']
                selected = words.sorts[name] if category == 'sorts' else words.predicates[name]
                if selected != (target['singular'] if category == 'sorts' else target) or any(
                    i.path.startswith(f'/vocabulary/{category}/{name}/') for i in words.issues
                ): rejected.append((category, name))
        if not rejected: return result
        for category, name in rejected: del result[category][name]
