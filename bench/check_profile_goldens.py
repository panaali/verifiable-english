"""Compare pilot document and editor wire output with pre-optimization goldens.

No proposer or model service is used. Paths and input hashes pin the pilot files
that were available for the baseline comparison.
"""
import hashlib
import json
from pathlib import Path

from profile_english import service_env
from ve.assist.ambiguity_patterns import checked_wording, review
from ve.ast import Const, Unary
from ve.document import check_document

HERE = Path(__file__).resolve().parent


def encoded(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':')).encode()


def editor_output():
    env = service_env()
    return {
        'scope': review(env, 'Every engineer checks a server.',
                        {'every_sort': 'engineer', 'some_sort': 'server',
                         'relation': 'checks_pair'}, pattern_id='scope.every_some@1'),
        'reference': review(env, 'It is safe.',
                            {'predicate': 'safe', 'antecedents': ['api', 'carol']},
                            pattern_id='discourse.reference@1'),
        'validation': checked_wording(env, 'Api is safe.', Unary('safe', Const('api'))),
    }


def main():
    golden = json.loads((HERE / 'PROFILE-GOLDEN.json').read_text())
    for name, expected in golden['documents'].items():
        path = Path(name)
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected['input_sha256'], name
        try:
            report = check_document(path)
        except Exception as exc:
            assert (type(exc).__name__, str(exc)) == (expected.get('error'), expected.get('message')), name
        else:
            assert hashlib.sha256(encoded(report)).hexdigest() == expected['output_sha256'], name
        print('MATCH', name)
    actual = hashlib.sha256(encoded(editor_output()) + b'\n').hexdigest()
    assert actual == golden['editor_sha256']
    print('MATCH editor catalogue and wording')


if __name__ == '__main__':
    main()
