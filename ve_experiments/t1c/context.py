"""Context safety: byte upper bound, then authenticated native token count if needed."""
import json
import urllib.request
from .transport import oauth_token, MODELS

LIMITS = {'opus': 1000000, 'haiku': 200000, 'sonnet': 1000000}
WRAPPER_RESERVE = 4096


def compact_ve(submission):
    # Lossless transport: retain every mapping, including duplicate IDs and malformed rows.
    groups = {}
    other = []
    for row in submission.get('rows', []):
        if isinstance(row, dict) and set(row) == {'source', 'clause'} and isinstance(row['source'], str) and ':' in row['source']:
            file, line = row['source'].rsplit(':', 1)
            groups.setdefault(file, []).append([line, row['clause']])
        else:
            other.append(row)
    return {'encoding': 'Each file maps to ordered [line, VE clause] pairs. Source ID is file:line. Duplicates are retained.',
            'files': groups, 'other_rows': other, 'certificate': submission.get('certificate', {})}


def check(model, system, prompt, output, account):
    size = len(system.encode()) + len(prompt.encode())
    limit = LIMITS[model]
    receipt = {'model': MODELS[model], 'context_limit': limit, 'utf8_bytes': size,
               'output_reserve': output, 'wrapper_reserve': WRAPPER_RESERVE}
    if size + output + WRAPPER_RESERVE <= limit:
        return receipt | {'method': 'conservative_utf8_byte_upper_bound', 'fits': True}
    body = json.dumps({'model': MODELS[model], 'system': system,
                       'messages': [{'role': 'user', 'content': prompt}]}).encode()
    request = urllib.request.Request('https://api.anthropic.com/v1/messages/count_tokens', data=body,
        headers={'Authorization': 'Bearer ' + oauth_token(account), 'anthropic-version': '2023-06-01',
                 'anthropic-beta': 'oauth-2025-04-20', 'Content-Type': 'application/json'})
    with urllib.request.urlopen(request, timeout=60) as response:
        counted = json.load(response)
    tokens = counted.get('input_tokens')
    if type(tokens) is not int or tokens < 0:
        raise RuntimeError('Native context token count missing')
    return receipt | {'method': 'native_count_tokens', 'input_tokens': tokens,
                      'fits': tokens + output + WRAPPER_RESERVE <= limit}
