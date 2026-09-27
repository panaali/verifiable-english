"""Persistent Python peer. One JSON request and one JSON response per line."""
import json
import sys


def run(request):
    from ve.environment import Environment
    from ve.ast import document_from_data
    from ve.entailment import check_entailment_certificate
    from ve.model import FiniteModel
    from ve.evaluate import evaluate
    from ve.search import find_countermodel
    from ve.norms import NormDocument, check_conflict
    from ve.bundle import check_bundle
    from ve.admission import admit_document
    from ve.english import parse_english, parse_english_with_metadata
    kind = request['bench_kind']
    if kind == 'bundle':
        result = check_bundle(request['bundle'])
        return {'status': result['status'], 'checked': len(result['lemmas'])}
    env = Environment(request['environment'])
    if kind == 'english':
        return {'parsed': parse_english(env, request['source']) is not None}
    if kind == 'english-admission':
        result = parse_english_with_metadata(env, request['source'])
        return {'admitted': result.document is not None}
    if kind == 'admission':
        return {'status': 'ok', 'admitted': admit_document(env, request['document'])['admitted']}
    if kind.startswith('norms-'):
        doc = NormDocument(env, request['norms'])
        if kind == 'norms-elaborate':
            return {'status': 'ok', 'layers': len(doc.premises())}
        return {'verdict': check_conflict(doc, certificates=request['packages']).status}
    if kind in ('evaluate', 'definitions'):
        model = FiniteModel.from_dict(env, request['model'])
        doc = document_from_data(env, request['ast'])
        return {'status': 'ok', 'values': [evaluate(env, f, model, trace=False).value for f in doc.formulas]}
    fs = document_from_data(env, request['premises'] + [request['conclusion']]).formulas
    if kind == 'search':
        r = find_countermodel(env, fs[:-1], fs[-1], max_domain_size=request['max_domain_size'],
                              max_models=request.get('max_models', 10000),
                              max_evaluations=request.get('max_evaluations', 1000000))
        return {'status': r.status}
    if kind == 'certificate':
        return {'valid': check_entailment_certificate(env, fs[:-1], fs[-1], request['certificate']).valid}
    raise ValueError(kind)


def main():
    for line in sys.stdin:
        try:
            request = json.loads(line)
            if request == {'ping': True}:
                answer = {'ready': True}
            else:
                answer = run(request)
        except Exception as exc:
            answer = {'status': 'error', 'error': str(exc)}
        print(json.dumps(answer, separators=(',', ':')), flush=True)


if __name__ == '__main__':
    main()
