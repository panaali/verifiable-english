"""Mechanical wording mutants (moved from manage-agents tools-local/wording-mutants.py, item 47: VE owns it now).

Origin: the RECALL GATE of the per-unit checklist pass (2026-11-12 dri-uc-audit-union-rule-2;
reviews/dri-decisions-20261112-audit-stability.md item 47, mutant kinds of item 46). plan() and apply() are the
bundle's, byte for byte in output (tests/test_fidmech_wording.py: frozen inputs, tests/data/fidmech/wording-golden.json);
ACTORS is unchanged. The bundle's uc-audit-blind.py loads this file from its pinned VE checkout after the install read.

No model, no network: text in, text out. A mutant changes ONE rule-block unit of a case's VE text so that the unit no
longer says what its source says, in one of these kinds (about two in three are wording, the rest structural):
  wording (in an act phrase or a legend; vocabulary file, environment.d1.json and every rule that uses the act together):
    actor       two actors swapped (or one actor replaced by another actor the case names)
    qualifier   a qualifier dropped ("promptly", "final", "at least", "all", "redacted", ...)
    quantity    a quantity or deadline changed (a number, "one week", "thirty days", "within" -> "after", ...)
    attachment  the objects of two prepositional phrases swapped (what attaches to what)
  structural (in the unit's own rule line in rules.d1.ve):
    modal       must <-> should (may -> must)
    guard       a conjunct of the guard dropped ("if both A and B" -> "if A")
    negation    the first condition of the guard negated
Selection is deterministic for a seed: units shuffled by the seed, wording kinds round robin (act and legend alternating),
one mutant per unit.
  python -m tools.fidmech.wording plan <tree> <case> <n> <seed>        print the plan (JSON), write nothing
Python use (uc-audit-blind.py): plan(files, units, n, seed) -> [mutant]; apply(files, [mutant]) -> {name: new text}.

Harness mode (plan 5.2; the fidmech mutant records are tools/fidmech/mutants.py's): harness_candidates() gives every
wording candidate of a unit, with the case's own actors (usecases/<doc>/fidmech/actors.json, load_actors) matched by
actor_pattern (a phrase's first letter in either case: "The SAG" at a sentence start is "the SAG"). ACTORS is
RSP-centred and case_actor_list only filters it, so it cannot find a PF or FSF actor. propose_actors() lists the
capitalised and role noun phrases of a case's acts and legends, the generated part of actors.json.
"""
import json
import random
import re
import sys
from pathlib import Path

ACTORS = ['the Responsible Scaling Officer', 'the external reviewers', 'external reviewers', 'the Board', 'the LTBT',
          'the CEO', 'the RSO', 'the company', 'regular-clearance employees', 'full-time employees', 'employees',
          'the public', 'the government', 'reviewers', 'Anthropic']
QUALIFIERS = ['promptly', 'final', 'unredacted', 'full', 'comprehensive', 'public', 'written', 'at least', 'all', 'each',
              'significantly', 'minimally-redacted', 'regular-clearance', 'full-time', 'past', 'current', 'external',
              'noteworthy', 'redacted', 'internal', 'new', 'publicly', 'only', 'any', 'material', 'reasonably', 'fully']
QUANT_WORDS = [('one week', 'two weeks'), ('thirty days', 'sixty days'), ('30 days', '60 days'), ('two hundred', 'twenty'),
               ('within', 'after'), ('before', 'after'), ('prior to', 'after'), ('annually', 'every two years'),
               ('quarterly', 'annually'), ('monthly', 'quarterly'), ('one', 'two'), ('two', 'three'), ('three', 'five'),
               ('four', 'six'), ('five', 'seven'), ('ten', 'twenty'), ('hundred', 'thousand')]
WORDING = ('actor', 'qualifier', 'quantity', 'attachment')
STRUCTURAL = ('modal', 'guard', 'negation')



def _wb(word):
    return re.compile(r'(?<![\w-])' + re.escape(word) + r'(?![\w-])')


def actor_pattern(phrase):
    """The harness's actor matcher: `phrase` at word bounds, its first letter in either case."""
    head = phrase[:1]
    first = '[' + re.escape(head.lower() + head.upper()) + ']' if head.isalpha() else re.escape(head)
    return re.compile(r'(?<![\w-])' + first + re.escape(phrase[1:]) + r'(?![\w-])')


def actor_cands(s, case_actors, actors=ACTORS, pattern=_wb):
    found = sorted({(mm.start(), mm.end(), a) for a in actors for mm in pattern(a).finditer(s)})
    keep, last = [], -1   # longest first at a position, no overlaps
    for st, en, a in sorted(found, key=lambda x: (x[0], -(x[1] - x[0]))):
        if st >= last:
            keep.append((st, en, a))
            last = en
    distinct = [x for k, x in enumerate(keep) if x[2] not in [y[2] for y in keep[:k]]]
    for k in range(len(distinct) - 1):   # two actors in different roles (not a plain list: "A, B and C" keeps its meaning)
        (a0, b0, x0), (a1, b1, x1) = distinct[k:k + 2]
        if not re.fullmatch(r'\s*(?:,|and|or|/|, and|, or|as well as)?\s*(?:all )?', s[b0:a1]):
            return [(s[a0:b1], s[a1:b1] + s[b0:a1] + s[a0:b0])]   # the matched texts: x1 and x0 for ACTORS
    if len(distinct) >= 2:
        return []
    if len(distinct) == 1:
        st, en, a = distinct[0]
        other = next((x for x in case_actors if x != a and x.lower() not in a.lower() and a.lower() not in x.lower()), None)
        if other:
            return [(s[st:en], other)]
    return []


def qualifier_cands(s):
    out = []
    for q in QUALIFIERS:
        mm = _wb(q).search(s)
        if mm:
            a, b = mm.start(), mm.end()
            old = s[a:b + 1] if b < len(s) and s[b] in ' ,' else s[a:b]
            art = re.search(r'(?<![\w-])(an?) $', s[:a])
            new = ''
            if art:   # keep the article right for the word that now follows it ("an external reviewer" -> "a reviewer")
                nxt = s[a + len(old):].lstrip()[:1].lower()
                old, new = art.group(1) + ' ' + old, ('an ' if nxt in 'aeiou' and nxt else 'a ')
            if old.strip() and len(s.replace(old, new, 1).split()) >= 3:
                out.append((old, new))
    return out


def quantity_cands(s):
    out = []
    for old, new in QUANT_WORDS:
        if _wb(old).search(s):
            out.append((old, new))
    for mm in re.finditer(r'(?<![\d.({])(?<!section )(?<!Section )(?<!Appendix )(?<!step )(\d+)(?![\d.)}])', s):   # not a section, a list mark, {0}
        out.append((mm.group(1), str(int(mm.group(1)) * 2 if int(mm.group(1)) else 1)))
    return out


STOP = {'to', 'for', 'with', 'from', 'by', 'of', 'on', 'at', 'in', 'as', 'and', 'or', 'within', 'before', 'after', 'that',
        'which', 'if', 'when', 'than', 'is', 'are', 'be', 'was', 'were', 'has', 'have'}


def _objects(s):
    """[(start, end)] of 'the <words>' objects right after a preposition, up to the next stop word or punctuation."""
    out = []
    for mm in re.finditer(r'\b(?:to|for|with|from|by|of|on|at) (the) ', s):
        a = mm.start(1)
        toks = list(re.finditer(r'[\w-]+', s[mm.end():]))
        end, k = None, 0
        for t in toks:
            gap = s[mm.end() + (toks[k - 1].end() if k else 0):mm.end() + t.start()]
            if k and (gap.strip() or t.group(0).lower() in STOP) or k >= 4:
                break
            if t.group(0).lower() in STOP:
                break
            end = mm.end() + t.end()
            k += 1
        if end:
            out.append((a, end))
    return out


def attachment_cands(s):
    ms = _objects(s)
    for i in range(len(ms)):
        for j in range(i + 1, len(ms)):
            o1, o2 = s[ms[i][0]:ms[i][1]], s[ms[j][0]:ms[j][1]]
            if o1 != o2 and not (o1 in ACTORS and o2 in ACTORS) and ms[i][1] <= ms[j][0]:
                return [(s[ms[i][0]:ms[j][1]], o2 + s[ms[i][1]:ms[j][0]] + o1)]
    return []


def structural_cands(kind, line):
    if kind == 'modal':
        for old, new in ((' must not ', ' should not '), (' must ', ' should '), (' should ', ' must '), (' may ', ' must ')):
            if old in line:
                return [(old, new)]
    if kind == 'guard':
        mm = re.search(r', if both (.+?) and (that situation .+?)\.\s*$', line)
        if mm:
            return [(mm.group(0).rstrip(), f', if {mm.group(1)}.')]
    if kind == 'negation':
        mm = re.search(r', if (?:both |all of the following hold: \(a\) )?that situation (is classified as|has crossed|is) ', line)
        if mm:
            verb = mm.group(1)
            neg = {'is classified as': 'is not classified as', 'has crossed': 'has not crossed', 'is': 'is not'}[verb]
            return [(mm.group(0), mm.group(0)[:-len(verb) - 1] + neg + ' ')]
    return []


def _ctx(files):
    try:
        env = json.loads(files.get('environment.d1.json') or '{}')
    except ValueError:
        env = {}
    vf = sorted(n for n in files if n.endswith('vocabulary.py'))
    return env, (vf[0] if vf else None)


def _blocks(rules):
    lines = rules.splitlines()
    heads = [(i, mm.group(1)) for i, l in enumerate(lines) for mm in [re.match(r'^## (\S+) \|', l)] if mm]
    out = {}
    for j, (i, uid) in enumerate(heads):
        e = heads[j + 1][0] if j + 1 < len(heads) else len(lines)
        out[uid] = (i, e)
    return out, lines


def _used(body, env):
    used = []
    for key, p in ((env.get('vocabulary') or {}).get('predicates') or {}).items():
        act = (p.get('regulated') or {}).get('act')
        hit = re.search(r'classified as "' + re.escape(key) + '"', body)
        for tp in (p.get('verbalisation'), act):
            if hit or not tp:
                continue
            pat = re.sub(r'\\\{\d\\\}', '.+?', re.escape(re.sub(r'^\{0\}\s*', '', tp)))
            if re.search(r'(?<![A-Za-z])' + pat + r'(?![A-Za-z])', body):
                hit = True
        if hit:
            used.append(key)
    return used


def _legend_span(vlines, key):
    start = next((i for i, l in enumerate(vlines) if re.match(r'\s*"' + re.escape(key) + r'"\s*:', l)), None)
    if start is None:
        return None
    depth, j = vlines[start].count('(') - vlines[start].count(')'), start + 1
    while j < len(vlines) and (depth > 0 or vlines[j].lstrip().startswith('"') and not re.match(r'\s*"[a-z0-9_]+"\s*:', vlines[j])):
        depth += vlines[j].count('(') - vlines[j].count(')')
        j += 1
    return start, j


def _strings(line):
    """The string literals of a source line (contents only)."""
    return [mm.group(1) for mm in re.finditer(r'"((?:[^"\\]|\\.)*)"', line)]


def candidates(files, unit, case_actors, actors=ACTORS, pattern=_wb, structural=True):
    """[(kind, where, pred or None, old, new)] for one rule-block unit. The defaults are plan()'s; the harness passes
    the case's actors, actor_pattern and structural=False (harness_candidates)."""
    env, vname = _ctx(files)
    preds = (env.get('vocabulary') or {}).get('predicates') or {}
    blocks, lines = _blocks(files.get('rules.d1.ve', ''))
    if unit not in blocks:
        return []
    i, e = blocks[unit]
    body = '\n'.join(lines[i + 1:e])
    out = []
    rule_lines = [l for l in lines[i + 1:e] if re.match(r'\s*Rule \d+\.', l)]
    for kind in STRUCTURAL if structural else ():
        for l in rule_lines[:1]:
            for old, new in structural_cands(kind, l):
                out.append((kind, 'rule', None, old, new))
    vlines = files[vname].splitlines() if vname else []
    for key in _used(body, env):
        p = preds.get(key) or {}
        act = (p.get('regulated') or {}).get('act')
        sp = _legend_span(vlines, key)
        if not sp:
            continue
        lit = [s for l in vlines[sp[0]:sp[1]] for s in _strings(l)]
        if act and act in lit:   # the act template is one literal: mutate it (and every rule that uses it)
            phrase = re.sub(r'^\{0\}\s*', '', act)
            for kind, fn in (('actor', lambda s: actor_cands(s, case_actors, actors, pattern)), ('qualifier', qualifier_cands),
                             ('quantity', quantity_cands), ('attachment', attachment_cands)):
                for old, new in fn(phrase):
                    if '{' not in old and '{' not in new and old != new:
                        out.append((kind, 'act', key, old, new))
        desc = p.get('description') or ''
        for s in lit:
            if s == act or s == key or not s.strip() or s not in desc.replace('\\"', '"'):
                continue
            for kind, fn in (('actor', lambda s: actor_cands(s, case_actors, actors, pattern)), ('qualifier', qualifier_cands),
                             ('quantity', quantity_cands), ('attachment', attachment_cands)):
                for old, new in fn(s):
                    if '{' not in old and old != new and '\\' not in old:
                        out.append((kind, 'legend', key, old, new))
    return out


def case_actor_list(files):
    text = '\n'.join(v for k, v in files.items() if k.endswith('vocabulary.py') or k == 'rules.d1.ve')
    return [a for a in ACTORS if _wb(a).search(text)]


def plan(files, units, n, seed):
    """About n mutants (round(2n/3) wording, the rest structural), one per unit, deterministic for the seed."""
    n = int(n)
    acts = case_actor_list(files)
    order = list(units)
    random.Random(int(seed) or 1).shuffle(order)
    cands = {u: candidates(files, u, acts) for u in order}
    want_w = round(n * 2 / 3)
    out, used_u, used_p = [], set(), set()

    def take(kinds, wheres):
        for u in order:
            if u in used_u:
                continue
            for c in cands[u]:
                if c[0] in kinds and c[1] in wheres and (c[2] is None or c[2] not in used_p):
                    used_u.add(u)
                    if c[2]:
                        used_p.add(c[2])
                    out.append({'unit': u, 'kind': c[0], 'class': 'wording' if c[0] in WORDING else 'structural',
                                'where': c[1], 'pred': c[2], 'old': c[3], 'new': c[4]})
                    return True
        return False
    k = 0
    tries = 0
    while sum(x['class'] == 'wording' for x in out) < want_w and tries < 4 * len(WORDING) * 2:
        kind = WORDING[k % len(WORDING)]
        where = ('act', 'legend')[(k // len(WORDING)) % 2]
        if not take((kind,), (where,)):
            take((kind,), ('act', 'legend'))
        k += 1
        tries += 1
    k = 0
    tries = 0
    while len(out) < n and tries < 3 * len(STRUCTURAL) * 2:
        take((STRUCTURAL[k % len(STRUCTURAL)],), ('rule',))
        k += 1
        tries += 1
    if len(out) < n:   # not enough structural candidates: fill with wording ones
        for kind in WORDING * 3:
            if len(out) >= n:
                break
            take((kind,), ('act', 'legend'))
    return out


def apply(files, mutants):
    """{file name: new text} for the files the mutants change (the input dict is not modified)."""
    env, vname = _ctx(files)
    new = {}
    get = lambda f: new.get(f, files.get(f, ''))
    blocks, _ = _blocks(files.get('rules.d1.ve', ''))
    for x in mutants:
        if x['where'] == 'rule':
            lines = get('rules.d1.ve').splitlines(keepends=True)
            i, e = blocks[x['unit']]
            for j in range(i + 1, e):
                if re.match(r'\s*Rule \d+\.', lines[j]) and x['old'] in lines[j]:
                    lines[j] = lines[j].replace(x['old'], x['new'], 1)
                    break
            new['rules.d1.ve'] = ''.join(lines)
            continue
        key = x['pred']
        p = env['vocabulary']['predicates'][key]
        vlines = get(vname).splitlines(keepends=True)
        sp = _legend_span([l.rstrip('\n') for l in vlines], key)
        if x['where'] == 'act':
            act = p['regulated']['act']
            nact = act.replace(x['old'], x['new'], 1)
            for j in range(*sp):
                if '"' + act + '"' in vlines[j]:
                    vlines[j] = vlines[j].replace('"' + act + '"', '"' + nact + '"', 1)
                    break
            tp = re.sub(r'^\{0\}\s*', '', act)
            pat = re.compile(r'(?<![A-Za-z])' + re.sub(r'\\\{\d\\\}', '.+?', re.escape(tp)) + r'(?![A-Za-z])')
            rl = get('rules.d1.ve').splitlines(keepends=True)
            for j, l in enumerate(rl):
                mm = pat.search(l)
                if mm and re.match(r'\s*Rule \d+\.', l) and x['old'] in mm.group(0):
                    rl[j] = l[:mm.start()] + mm.group(0).replace(x['old'], x['new'], 1) + l[mm.end():]
            new['rules.d1.ve'] = ''.join(rl)
            p['regulated']['act'] = nact
        else:
            for j in range(*sp):
                if x['old'] in vlines[j]:
                    vlines[j] = vlines[j].replace(x['old'], x['new'], 1)
                    break
            p['description'] = p['description'].replace(x['old'], x['new'], 1)
        new[vname] = ''.join(vlines)
        ind = 2 if '\n  "' in files.get('environment.d1.json', '') else None
        new['environment.d1.json'] = json.dumps(env, indent=ind, ensure_ascii=False) + ('\n' if files.get('environment.d1.json', '').endswith('\n') else '')
    return new


# ---- harness mode (fidmech, plan 5.2) ------------------------------------------------------------------------------

ROLE_HEADS = ('officer', 'board', 'reviewer', 'employee', 'staff', 'team', 'group', 'council', 'committee', 'company',
              'developer', 'government', 'public', 'auditor', 'expert', 'leadership', 'partner', 'user', 'tester',
              'researcher', 'customer', 'function', 'party', 'parties', 'regulator', 'authority', 'authorities',
              'organization', 'organisation', 'chair', 'directors', 'competitor', 'actor', 'stakeholder')
ROLE_STOP = STOP | {'a', 'an', 'the', 'any', 'its', 'our', 'their', 'his', 'her', 'have', 'has', 'not', 'no', 'so',
                    'such', 'other', 'each', 'every', 'all', 'one', 'is', 'decision', 'use', 'act', 'step'}


def actor_texts(files):
    """The act phrases and legends (descriptions) of a case's predicates, in environment.d1.json order."""
    env, _ = _ctx(files)
    out = []
    for p in ((env.get('vocabulary') or {}).get('predicates') or {}).values():
        out += [t for t in ((p.get('regulated') or {}).get('act'), p.get('description')) if t]
    return out


def propose_actors(files):
    """The generated part of actors.json, longest first; a builder reviews it. Capitalised phrases whose last word is an
    acronym (2-5 capitals), a role head or a CamelCase name, and every ACTORS phrase the texts hold; role noun phrases:
    a role head with at most one lower-case modifier right before it, and "the" when it comes first."""
    heads = r'(?:' + '|'.join(re.escape(h) for h in ROLE_HEADS) + r')s?'
    found = set()
    for t in actor_texts(files):
        for mm in re.finditer(r'(?<![\w-])(?:the )?[A-Z][\w-]*(?: (?:of |and |for )?[A-Z][\w-]*)*', t):
            last = mm.group(0).split()[-1]
            if (re.fullmatch(r'[A-Z]{2,5}|[A-Z][a-z]+[A-Z][A-Za-z]*', last) or re.fullmatch(heads, last.lower())) \
                    and not re.search(r'\d', mm.group(0)):
                found.add(mm.group(0))
        found.update(a for a in ACTORS if _wb(a).search(t))
        toks = list(re.finditer(r'[\w-]+', t))
        for k, tok in enumerate(toks):
            if not re.fullmatch(heads, tok.group(0)):
                continue
            j = k
            if k and t[toks[k - 1].end():tok.start()] == ' ' and toks[k - 1].group(0).islower() \
                    and toks[k - 1].group(0) not in ROLE_STOP:
                j = k - 1
            the = j and toks[j - 1].group(0) == 'the' and t[toks[j - 1].end():toks[j].start()] == ' '
            found.add(('the ' if the else '') + t[toks[j].start():tok.end()])
    return sorted(found, key=lambda a: (-len(a), a))


def load_actors(path):
    """The reviewed actor list of an actors.json: `actors` (the generated list less `removed`, plus `added`)."""
    data = json.loads(Path(path).read_text(encoding='utf-8'))
    removed, added = [r['phrase'] for r in data['removed']], [r['phrase'] for r in data['added']]
    expected = sorted((set(data['generated']) - set(removed)) | set(added), key=lambda a: (-len(a), a))
    if data['actors'] != expected or not set(removed) <= set(data['generated']):
        raise ValueError(f'{path}: actors is not generated - removed + added')
    return data['actors']


def harness_candidates(files, unit, actors):
    """Every wording candidate of one rule-block unit, the case's actors matched by actor_pattern. A replacing actor
    holds no "and" or "or": VE refuses an act phrase with a logic word, so such a mutant could only be stillborn."""
    replacing = [a for a in actors if not re.search(r'(?<![\w-])(?:and|or)(?![\w-])', a)]
    return candidates(files, unit, replacing, actors, actor_pattern, structural=False)


def read_case(tree, case):
    d = Path(tree) / 'usecases' / case
    return {f.name: f.read_text() for f in sorted(d.iterdir()) if f.is_file() and
            (f.name in ('rules.d1.ve', 'environment.d1.json') or f.name.endswith('vocabulary.py'))}


if __name__ == '__main__':
    a = sys.argv[1:]
    if len(a) == 5 and a[0] == 'plan':
        fs = read_case(a[1], a[2])
        units = list(_blocks(fs.get('rules.d1.ve', ''))[0])
        print(json.dumps(plan(fs, units, a[3], a[4]), indent=1, ensure_ascii=False))
    else:
        sys.exit(__doc__)
