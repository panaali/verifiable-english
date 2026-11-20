"""The counter code that decides what an FSF, RSP or PF reader is shown, copied byte for byte (defs-carried-gate-stage1-1119).

Every piece below a "# --- copied:" line is the text of one top-level statement of the manage-agents counter
(tools-local/uc-audit.py.reads-1119, and ARG_LIMIT from tools-local/omission-seq-read.py), unchanged. The VE repository
never imports across repositories, so the pieces are copied, and tests/test_definitions_carried.py hashes each one
against tests/data/defs_carried/counter_pin.json, which records the source files' sha256 and each piece's line range and
sha256. Editing a copied piece fails that test; to re-pin, copy the new text and its hashes together.

The three functions above the copied pieces are this module's own: the counter reads a VE commit with git, and
tools/defs_carried.py reads a tree (a checkout or a commit) through an object it registers here under a key that stands
in for the commit (bind_tree). They change no copied text.
"""
import json
import re

_TREES = {}   # key -> object with read(path) -> str | None and names(dir) -> [file names]
_OCAR = {}    # the counter's own cache of omit_carrier_texts, keyed (case, commit)


def bind_tree(key, tree):
    """Register tree under key; the copied functions then read `usecases/<case>/...` at "commit" key from it."""
    _TREES[key] = tree
    for k in [k for k in _OCAR if k[1] == key]:
        del _OCAR[k]


def _ve_show(commit, path):
    """The counter's git show (uc-audit.py.reads-1119:3270), read from the bound tree instead."""
    return _TREES[commit].read(path)


def semantic_files_git(commit, case):
    """The counter's semantic_files_git (uc-audit.py.reads-1119:1142), from the bound tree: {file name: bytes} of the case's
    environment.d<n>.json and *vocabulary.py files, the two kinds omit_carrier_texts reads from it."""
    t = _TREES[commit]
    out = {}
    for n in t.names(f'usecases/{case}'):
        if n.endswith('vocabulary.py') or re.fullmatch(r'environment\.d\d+\.json', n):
            s = t.read(f'usecases/{case}/{n}')
            if s is not None:
                out[n] = s.encode('utf-8')
    return out


def omit_code_parts(case, show):
    """The D2D3 unit's code parts, narrowed: every OMIT_CODE file whole, then each OMIT_CODE_SECTION section (from the
    column-0 header line to the next column-0 '# --- ' line; the whole file when the header is absent). The counter also
    appends each part's definition closure (omit_code_closure, not copied): this narrower unit can only miss a carrier,
    never add one, so a definition found only in the closure is reported not carried (a stated limit of stage 1)."""
    out = [(n, show(n)) for n in OMIT_CODE.get(case, ())]
    for n, header in OMIT_CODE_SECTION.get(case, ()):
        t = show(n)
        if t is None:
            out.append((n, None))
            continue
        lines = t.splitlines(keepends=True)
        start = next((i for i, l in enumerate(lines) if l.startswith(header)), None)
        if start is None:
            out.append((n, t))
            continue
        end = next((j for j in range(start + 1, len(lines)) if lines[j].startswith('# --- ')), len(lines))
        out.append((f'{n} section {header!r}', ''.join(lines[start:end])))
    return out


ARG_LIMIT = 131000   # bytes; Linux MAX_ARG_STRLEN is 131072 (largest measured prompt 2026-11-15: 105,768 bytes, RSP G3)


# --- copied: uc-audit.py.reads-1119 lines 1730-1730
OMIT_CODE = {'anthropic-rsp': ('stage0.py',), 'openai-preparedness': ('stage0.py',), 'safety-framework': ('severity_and_dates.py',)}

# --- copied: uc-audit.py.reads-1119 lines 1737-1737
OMIT_CODE_SECTION = {'openai-preparedness': (('run.py', '# --- S, T, D: D2 and D3'),)}

# --- copied: uc-audit.py.reads-1119 lines 3034-3043
def omit_norm(s):
    """Quote normalisation for the verbatim check: NFKC (ligatures), curly quotes and dashes, line-break hyphenation, case and
    whitespace."""
    import unicodedata
    s = unicodedata.normalize('NFKC', s)
    for a, b in (('’', "'"), ('‘', "'"), ('“', '"'), ('”', '"'), ('—', '-'), ('–', '-'),
                 ('‑', '-'), ('‐', '-'), ('…', '...'), ('‚', ',')):
        s = s.replace(a, b)
    s = re.sub(r'\s+', ' ', s.lower()).strip()
    return re.sub(r'(?<=[a-z])- (?=[a-z])', '', s)


# --- copied: uc-audit.py.reads-1119 lines 1159-1167
def rule_blocks(text):
    """{block id: (block text incl. header, body text)} of a rules.d1.ve ('## <id> | ...' headers)."""
    lines = text.splitlines()
    heads = [(i, mm.group(1)) for i, l in enumerate(lines) for mm in [re.match(r'^## (\S+) \|', l)] if mm]
    out = {}
    for j, (i, uid) in enumerate(heads):
        e = heads[j + 1][0] if j + 1 < len(heads) else len(lines)
        out[uid] = ('\n'.join(lines[i:e]).rstrip(), '\n'.join(lines[i + 1:e]))
    return out


# --- copied: uc-audit.py.reads-1119 lines 1202-1222
def seq_unit_legends(case, unit, rules, facts, show):
    """R16 C5: the vocabulary legends of the predicates the unit's block USES, exactly the predicates the counter's carrier
    definition counts (docstring omission-3 'a vocabulary legend of a predicate that block uses'; omit_exposure carrier() and
    omit_carrier_texts: used_predicates over the block body, header line excluded; FACTS = every fact block). The text shown
    is each predicate's description in environment.d1.json at the commit (the legend the VE states; for a computed legend,
    e.g. RSP plans_in_place, the vocabulary.py lines hold only a call). Constants and unused predicates are not shown (a
    constant's legend is a label the counter never counts). CASES and D2D3 have no legend part."""
    try:
        env = json.loads(show('environment.d1.json') or '{}')
    except ValueError:
        env = {}
    preds = ((env.get('vocabulary') or {}).get('predicates') or {}) if isinstance(env, dict) else {}
    if unit == 'FACTS':
        bodies = [body for _, body in rule_blocks(facts or '').values()]
    else:
        hit = rule_blocks(rules or '').get(unit) or rule_blocks(facts or '').get(unit)
        bodies = [hit[1]] if hit else []
    keys = list(dict.fromkeys(k for body in bodies for k in used_predicates(body, env)))
    lines = [f'- {k}: ' + (' '.join(str((preds.get(k) or {}).get('description') or '').split()) or '(no description)') for k in keys]
    return ('VOCABULARY LEGENDS (environment.d1.json) of the predicates this unit uses:\n' +
            ('\n'.join(lines) if lines else '(none)'))


# --- copied: uc-audit.py.reads-1119 lines 1241-1256
def used_predicates(rule_text, env):
    """Predicates a rule's text uses (verbalisation / act templates, 'classified as "<name>"'): the matching of
    uc-audit-blind.py legend_lines()."""
    used = []
    for key, p in ((env.get('vocabulary') or {}).get('predicates') or {}).items():
        hit = re.search(r'classified as "' + re.escape(key) + '"', rule_text)
        for tp in (p.get('verbalisation'), (p.get('regulated') or {}).get('act')):
            if hit or not tp:
                continue
            tp = re.sub(r'^\{0\}\s*', '', tp)
            pat = re.sub(r'\\\{\d\\\}', '.+?', re.escape(tp))
            if re.search(r'(?<![A-Za-z])' + pat + r'(?![A-Za-z])', rule_text):
                hit = True
        if hit:
            used.append(key)
    return used


# --- copied: uc-audit.py.reads-1119 lines 1259-1271
def legend_raw(key, vlines):
    """The vocabulary-file lines of a predicate's entry (no line numbers: an edit elsewhere does not move it)."""
    start = next((i for i, l in enumerate(vlines) if re.match(r'\s*"' + re.escape(key) + r'"\s*:', l)), None)
    if start is None:
        return []
    out, depth, j = [vlines[start]], vlines[start].count('(') - vlines[start].count(')'), start + 1
    while j < len(vlines) and (depth > 0 or vlines[j].lstrip().startswith('"') and not re.match(r'\s*"[a-z0-9_]+"\s*:', vlines[j])):
        out.append(vlines[j])
        depth += vlines[j].count('(') - vlines[j].count(')')
        j += 1
        if len(out) > 40:
            break
    return out


# --- copied: uc-audit.py.reads-1119 lines 3289-3298
def _omit_strip_comments(lines, body=False):
    """#3 (a): drop comment lines and trailing comments (a comment is documentation, not a carrier); in a rule body any
    trailing '#', '--' or '//' comment and every quoted literal (challenge 2 #3); in legend lines a trailing '#' comment."""
    out = []
    for l in lines:
        if l.lstrip().startswith(('#', '--', '//')):
            continue
        l = re.sub(r'\s*(#|--|//).*$', '', re.sub(r'"[^"]*"', ' ', l)) if body else re.sub(r'\s#.*$', '', l)
        out.append(l)
    return out


# --- copied: uc-audit.py.reads-1119 lines 3721-3741
def _omit_legend_segments(raw_lines):
    """The quoted strings of one vocabulary entry, implicit concatenation joined, the entry key dropped: [(meaning text with
    citations cut out, raw text)]. Citations: a parenthesis holding a digit or 'section' / 'appendix' / 'table', a leading
    '<n>:' and '<n> at {k}'; a whole string that starts with a section citation and copies a quoted source sentence is a
    provenance string (none ruling finding 3 and its reads prompt: documentation, never a carrier) (legend-carrier ruling s1)."""
    txt = '\n'.join(raw_lines)
    out = []
    for mm in re.finditer(r'"(?:[^"\\]|\\.)*"(?:\s*"(?:[^"\\]|\\.)*")*', txt):
        val = ''.join(re.findall(r'"((?:[^"\\]|\\.)*)"', mm.group(0)))
        if not out and mm.start() == txt.find('"'):   # the entry key
            out.append(None)
            continue
        if re.match(r'\s*(?:[A-Z]?\d+(?:\.\d+)*[a-z]?\s*(?::|at\s+\{\d\})|\(?section\b)', val, re.I) and \
                re.search(r'\\"[^"\\]*(?:\s+\S+){2,}[^"\\]*\\"', val):
            out.append(('', omit_norm(val)))   # a provenance string: a section citation plus a copied source sentence
            continue
        cut = re.sub(r'\([^()]*(?:\d|section|appendix|table)[^()]*\)', ' ', val, flags=re.I)
        cut = re.sub(r'^\s*[A-Z]?\d+(?:\.\d+)*[a-z]?\s*:', ' ', cut)
        cut = re.sub(r'\b[A-Z]?\d+(?:\.\d+)*[a-z]?\s+at\s+\{\d\}', ' ', cut)
        out.append((omit_norm(cut), omit_norm(val)))
    return [x for x in out if x]


# --- copied: uc-audit.py.reads-1119 lines 3744-3791
def omit_carrier_texts(case, commit):
    """omission-3: the carrier texts of a case at a VE commit: {unit: {'rule': text, 'legend': {key: [(meaning, raw)]},
    'header': text}} for every rule / fact block, 'FACTS' (all fact blocks), 'D2D3' {'code': text} and 'CASES' {'premise': text}.
    Rule and fact lines: comments stripped (a comment is documentation); code: comment lines, trailing comments and docstrings
    stripped. All normalised (omit_norm)."""
    if (case, commit) in _OCAR:
        return _OCAR[(case, commit)]
    import ast
    files = semantic_files_git(commit, case)
    try:
        env = json.loads(files.get('environment.d1.json') or b'{}')
    except ValueError:
        env = {}
    vf = sorted(n for n in files if n.endswith('vocabulary.py'))
    vlines = files[vf[0]].decode('utf-8', 'replace').splitlines() if vf else []
    out = {}
    def unit(blocks):
        for uid, (txt, body) in blocks.items():
            out[uid] = {'rule': omit_norm(' '.join(_omit_strip_comments(body.splitlines()))),
                        'legend': {k: _omit_legend_segments(legend_raw(k, vlines)) for k in used_predicates(body, env)},
                        'header': omit_norm(txt.splitlines()[0])}
    fb = rule_blocks(_ve_show(commit, f'usecases/{case}/facts.d1.ve') or '')
    unit(rule_blocks(_ve_show(commit, f'usecases/{case}/rules.d1.ve') or ''))
    unit(fb)
    out['FACTS'] = {'rule': ' | '.join(out[k]['rule'] for k in fb), 'header': ' | '.join(out[k]['header'] for k in fb),
                    'legend': {lk: lv for k in fb for lk, lv in out[k]['legend'].items()}}
    code = []
    for _fn, t in omit_code_parts(case, lambda n: _ve_show(commit, f'usecases/{case}/{n}')):   # row oseq-pf-d2d3-unit
        if t is None:
            continue
        lines = t.splitlines()
        try:
            for nd in ast.walk(ast.parse(t)):
                if isinstance(nd, ast.Expr) and isinstance(getattr(nd, 'value', None), ast.Constant) and isinstance(nd.value.value, str):
                    for i in range(nd.lineno - 1, nd.end_lineno):
                        lines[i] = ''
        except (SyntaxError, ValueError):
            pass
        code += [re.sub(r'\s+#.*$', '', l) for l in lines if not l.lstrip().startswith('#')]
    out['D2D3'] = {'code': omit_norm('\n'.join(code))}
    cj = _ve_show(commit, f'usecases/{case}/cases.json') or ''
    try:
        cases = '\n'.join(json.dumps(x, ensure_ascii=False) for x in json.loads(cj).get('cases', []))
    except (ValueError, AttributeError):
        cases = ''
    out['CASES'] = {'premise': omit_norm(cj + '\n' + cases)}
    _OCAR[(case, commit)] = out
    return out


