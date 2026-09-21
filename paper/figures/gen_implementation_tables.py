#!/usr/bin/env python3
"""Build example displays and corpus/performance tables from repository artifacts."""
import json
import re
import sys
import textwrap
from statistics import median

from gen_e0_tables import ROOT, table, write

sys.path.insert(0, str(ROOT.parent))
from ve import Environment, parse, render, render_vocabulary
from ve.ast import document_to_data
from ve.printer import VIEWS, render_cell


def read(relative):
    return json.loads((ROOT.parent / relative).read_text())


def worked_example():
    env = Environment.from_json((ROOT / 'sources/worked-example.env.json').read_bytes())
    document = parse(env, (ROOT / 'sources/worked-example.ve').read_bytes())
    strings = {view: render(document, env, view) for view in VIEWS}
    legends = {render_vocabulary(env, view) for view in VIEWS}
    assert len(legends) == 1
    legend_text = legends.pop()
    legend = json.loads(legend_text)
    assert not legend['lint']
    assert parse(env, strings['ve_strict']) == document
    cells = {view: render_cell(document, env, view) for view in VIEWS}
    assert all(cells[v] == legend_text + strings[v] for v in VIEWS)
    write('worked-example.json', json.dumps({
        'environment': json.loads((ROOT / 'sources/worked-example.env.json').read_text()),
        'ast': document_to_data(env, document), 'views': strings,
        'legend': legend, 'cells': cells,
    }, indent=2, ensure_ascii=True))

    parts = []
    for view in VIEWS:
        parts.append(f'**`{view}`**\n')
        if view == 'fol_symbols':
            # Mechanical typesetting of the actual symbolic string; no paraphrase.
            tokens = re.findall(r'∀|∃|→|[A-Za-z]+|\d+|\s+|.', strings[view])
            mapped = {'∀': r'\forall ', '∃': r'\exists ', '→': r'\to '}
            math = ''.join(mapped.get(t, r'\mathrm{' + t + '}'
                                     if re.fullmatch('[A-Za-z]+', t) else t)
                           for t in tokens)
            math = re.sub(r'\\mathrm\{x\}(\d+)', r'x_{\1}', math)
            parts.append('$$\n' + math.strip() + '\n$$\n')
        else:
            wrapped = textwrap.fill(strings[view].strip(), width=80,
                                    break_long_words=False, break_on_hyphens=False)
            parts.append('```text\n' + wrapped + '\n```\n')
    parts.append('<!-- src: paper/sources/worked-example.env.json; '
                 'paper/sources/worked-example.ve; ve/printer.py; ve/fluent.py. '
                 'Exact strings and AST: paper/generated/worked-example.json. -->')
    write('worked-example.md', '\n'.join(parts))
    rows = []
    for s in legend['sorts']:
        rows.append([f"`{s['identifier']}`", 'Sort', s['description'], f"`{s['rendered_noun']}`"])
    for p in legend['predicates']:
        rows.append([f"`{p['identifier']}`", ', '.join(f'`{s}`' for s in p['arguments']),
                     p['description'], f"`{p['rendered_template']}`"])
    write('worked-legend.md', table(['Identifier', 'Ordered signature', 'Description', 'Wording'], rows)
          + '\nNo constants are declared. No lint diagnostic is reported. The stored legend '
          'also records the optional negative template for `owns`, absent negative wording '
          'for `deployed`, raw declarations, and the naming rules.\n\n'
          '<!-- src: paper/generated/worked-example.json, generated from '
          'paper/sources/worked-example.env.json. -->')


def conformance():
    rows = []
    scopes = {
        'evaluation': 'Python / Lean / Rust evaluation and canonical text',
        'countermodels': 'Python / Lean / Rust finite witnesses',
        'parser': 'Python / Rust diagnostics; Lean acceptance/rejection',
        'identity': 'Python / Rust hashes; Lean surface/evaluation only',
        'wire': 'Python / Rust restricted JSON',
        'validation': 'Python / Rust diagnostics; Lean rejection',
        'search': 'Python / Rust bounded search / witnesses',
        'closure': 'Python / Lean evaluation and canonical text; no Rust',
    }
    for name, scope in scopes.items():
        data = read(f'conformance/{name}.json')
        count = f'{len(data):,}'
        if name in ('evaluation', 'closure'):
            count += f" cases; {sum(len(c['ast']) for c in data):,} formulas"
        rows.append([f'`{name}.json`', count, scope])
    write('conformance-table.md', table(['Fixture', 'Size', 'Recorded comparison'], rows)
          + '\n<!-- src: conformance/{evaluation,countermodels,parser,identity,wire,validation,search,closure}.json; '
          'conformance/README.md for comparison scope. -->\n\n'
          + replay_table())


def replay_table():
    r = read('conformance/certificates-report.json')
    f = read('conformance/fuzz-summary.json')
    outcomes = {status: sum(v for k, v in r['search_outcomes'].items()
                           if k.endswith(':' + status))
                for status in ('Found', 'NotFound', 'ResourceLimit')}
    assert outcomes['Found'] == r['python_accepted'] == r['lean_accepted']
    rows = [
        ['Recorded Python/Rust fuzz agreements', f"{f['agreements']:,}/{f['cases']:,}"],
        ['Certificate searches (all attempts)', sum(outcomes.values())],
        ['Search Found / NotFound / ResourceLimit', ' / '.join(str(v) for v in outcomes.values())],
        ['Produced certificates accepted by Lean', f"{r['lean_accepted']}/{r['python_accepted']}"],
        ['Forged certificates rejected by Lean', f"{r['lean_rejected_forged']}/{r['forged']}"],
    ]
    return (table(['Development check', 'Recorded count'], rows) + '\n'
            '<!-- src: conformance/fuzz-summary.json; conformance/certificates-report.json. -->')


def rust():
    data = read('rust/benchmark-results.json')
    rows = []
    for r in data['results']:
        if r['id'] not in ('eval_n32', 'eval_n64'):
            continue
        p = 1000 * median(r['python_kernel_seconds_per_call'])
        s = 1000 * median(r['rust_kernel_seconds_per_call'])
        assert abs(p - r['python_kernel_median_ms']) < 1e-9
        assert abs(s - r['rust_kernel_median_ms']) < 1e-9
        assert abs(p / s - r['kernel_ratio']) < 1e-9
        rows.append([r['size'], f'{p:.3f}', f'{s:.3f}', f'{p/s:.2f}', f"{r['api_ratio']:.2f}"])
    assert len(rows) == 2
    write('rust-table.md', f"Medians of {data['repeats']} serial samples per workload; times in milliseconds.\n\n"
          + table(['Domain size', 'Python kernel', 'Rust kernel', 'Kernel ratio', 'API ratio'], rows)
          + '\n<!-- src: rust/benchmark-results.json; medians and kernel ratios recomputed from its raw samples. -->')


if __name__ == '__main__':
    worked_example()
    conformance()
    rust()
    print('Implementation tables: renderer outputs checked; fixture sizes and medians recomputed.')
