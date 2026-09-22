#!/usr/bin/env python3
"""Build the proposal-only OEWN lexicon using Python's standard library.

Run: python tools/build_lexicon.py [--source /path/to/english-wordnet-2025.zip]
The optional local archive must pass the same checksum as a download.
No frequency cutoff. Only ASCII alphabetic single words (the proposal token
alphabet) are retained; no spaces, underscores, hyphens, or glosses.
OEWN 2025 (without Namenet) supplies the common-word release.

Exception lists do NOT label tense. Preserve all verb exceptions separately;
tag third-person forms by spelling and participles conservatively: -ed/-en
and the explicit irregular spellings below, only when present in verb.exc.
Regular -s/-ed rules are generated fallbacks, not attributed to OEWN. Do not
generate a regular participle when there is an unclassified past exception.
This is incomplete morphology for diagnostics, never a grammar rule.
"""
import argparse
from collections import defaultdict
import hashlib
import io
import json
from pathlib import Path
import re
from urllib.request import urlopen
import zipfile

VERSION = '2025'
SOURCE_URL = 'https://en-word.net/static/english-wordnet-2025.zip'
SOURCE_SHA256 = '38b16326159f51853626b7d24a44c453fa88ab33f06fce5ec8fc5996d1c2be93'
LICENSE_ROOT = 'https://raw.githubusercontent.com/globalwordnet/english-wordnet/2025-edition/'
LICENSES = {
    'LICENSE.md': '672cc8b5663e8dc74c4b07a9dcf477193853575b119908fd3dc0aeeb60a9dbbb',
    'WNDB_License.txt': 'df30ec18fbabcdaf031b79ea026d3e6b959010cffe6dd7be9ac137822175b904',
}
WORD = re.compile(r'[a-z]+')
# Spelling labels only: every mapped form must still occur in OEWN verb.exc.
IRREGULAR_PARTICIPLES = frozenset('''been bent besought bet bid bled blest born
bound bred brought built burnt bought caught clad clung crept dealt done dreamt
drunk dug dwelt fed felt fled flung fought found gone got ground grown had heard held
hidden hit hung hurt kept knelt laid lain leant learnt led left lent let lit lost
made meant met mown paid pled put read rent rid ridden risen run said sat sawn
seen sent set sewn shaven shed shod shone shot shown shrunk shut slain slept slid
slung slit smelt sold sought sown sped spent spilt spun split spoilt spread sprung
stolen stood stridden strung stuck stung stunk struck striven sung sunk swept
swollen swung taught thought thrust told torn trodden understood upset wept wet
won worn wound wrung'''.split())
# Same-form participles have no exception-list row; these are explicit rules.
UNCHANGED_PARTICIPLES = frozenset('bet bid burst cast cost cut fit hit hurt let put quit read rid run set shed shut slit split spread thrust upset wet'.split())


def verified(data, checksum):
    actual = hashlib.sha256(data).hexdigest()
    if actual != checksum:
        raise ValueError(f'SHA-256 mismatch: expected {checksum}, got {actual}')
    return data


def download(url, checksum):
    with urlopen(url, timeout=60) as response:
        return verified(response.read(), checksum)


def verb_forms(lemma, exceptions):
    third = ('is' if lemma == 'be' else 'has' if lemma == 'have' else
             lemma[:-1] + 'ies' if re.search(r'[^aeiou]y$', lemma) else
             lemma + 'es' if lemma.endswith(('s', 'x', 'z', 'ch', 'sh', 'o')) else lemma + 's')
    # OEWN includes variants such as quizzes/quiz and chevies/chivvies/chivy.
    # 'was' is the only -s past form in this pinned exception list.
    thirds = sorted({w for w in exceptions if w.endswith('s') and w != 'was'} or {third})
    past = {w for w in exceptions if not w.endswith('ing') and w not in thirds
            and w not in {'am', 'are', 'is'}}
    participles = {w for w in past if w.endswith(('ed', 'en')) or w in IRREGULAR_PARTICIPLES}
    if lemma in UNCHANGED_PARTICIPLES:
        participles.add(lemma)
    if not past and not participles:
        participles.add(lemma + 'd' if lemma.endswith('e') else
                        lemma[:-1] + 'ied' if re.search(r'[^aeiou]y$', lemma) else
                        lemma + 'ked' if lemma.endswith('c') else lemma + 'ed')
    return {'third_person': thirds, 'past_participle': sorted(participles),
            'exceptions': sorted(exceptions)}


def build(data):
    verified(data, SOURCE_SHA256)
    senses = defaultdict(set)
    exceptions = defaultdict(set)
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        for line in archive.read('oewn2025/index.sense').decode('utf-8').splitlines():
            key = line.split()[0]
            lemma, suffix = key.split('%')
            cls = {'1': 'noun', '2': 'verb', '3': 'adjective', '5': 'adjective'}.get(suffix[0])
            if WORD.fullmatch(lemma) and cls:
                senses[lemma, cls].add(suffix)
        for line in archive.read('oewn2025/verb.exc').decode('utf-8').splitlines():
            form, *lemmas = line.split()
            if WORD.fullmatch(form):
                for lemma in lemmas:
                    exceptions[lemma].add(form)
    rows = [[lemma, cls, sorted(keys), verb_forms(lemma, exceptions[lemma]) if cls == 'verb' else {}]
            for (lemma, cls), keys in sorted(senses.items())]
    return {'format': 've.oewn-lexicon@1', 'version': 'oewn-' + VERSION,
            'source': {'url': SOURCE_URL, 'sha256': SOURCE_SHA256},
            'columns': ['lemma', 'class', 'sense_key_suffixes', 'inflections'],
            'sense_key_encoding': 'lemma + "%" + suffix (lossless)', 'entries': rows}


def encode(lexicon):
    # One compact row per line keeps the artifact diffable and below 5 MB.
    header = {k: v for k, v in lexicon.items() if k != 'entries'}
    compact = lambda value: json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(',', ':'))
    output = (compact(header)[:-1] + ',"entries":[\n' +
              ',\n'.join(compact(row) for row in lexicon['entries']) + '\n]}\n').encode('utf-8')
    if len(output) >= 5_000_000:
        raise ValueError('Lexicon must remain below 5 MB')
    return output


def attribution(notices):
    notices = {name: '\n'.join(line.rstrip() for line in text.splitlines()) + '\n'
               for name, text in notices.items()}
    return f'''# Open English WordNet proposal lexicon

Derived from Open English WordNet {VERSION}, by the Open English WordNet team,
incorporating Princeton University WordNet. OEWN is licensed under
[Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/).
The underlying Princeton data retains the WordNet notice below.

Source: {SOURCE_URL}
SHA-256: `{SOURCE_SHA256}`
Release: https://github.com/globalwordnet/english-wordnet/releases/tag/2025-edition

Regenerate with `python tools/build_lexicon.py` (Python 3.12+, standard library).
`--source PATH` reuses a checksum-verified archive; license downloads are also
checksum-pinned in the script. No frequency list or cutoff is used.

Changes: keep ASCII alphabetic single-word noun/adjective/verb lemmas only;
merge adjective satellite entries; discard glosses, relations and all other
classes. Rows, sense keys and forms are sorted. Each row contains lemma, class,
losslessly factored sense-key suffixes (prepend `lemma%`), and inflections.
All compatible senses are retained; none is selected as the intended meaning.
Inflections include source verb exceptions plus explicitly generated spelling
rules. OEWN exceptions do not label tense: participle tagging is conservative
and incomplete (see `verb_forms` in the generator); untagged forms remain in
`exceptions`. No countability, transitivity or phrase boundaries are inferred.

The following pinned upstream notices retain their wording; trailing whitespace
is removed for Markdown distribution.

## OEWN license and CC-BY 4.0 terms

{notices['LICENSE.md']}

## OEWN and Princeton WordNet distribution notice

```text
{notices['WNDB_License.txt']}```
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path)
    parser.add_argument('--output', type=Path, default=Path(__file__).resolve().parents[1] / 've/lexicon')
    args = parser.parse_args()
    # Finish and verify every download before writing any artifact. Failure is fatal.
    data = args.source.read_bytes() if args.source else download(SOURCE_URL, SOURCE_SHA256)
    output = encode(build(data))
    notices = {name: download(LICENSE_ROOT + name, checksum).decode('utf-8')
               for name, checksum in LICENSES.items()}
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / f'oewn-{VERSION}.json').write_bytes(output)
    (args.output / 'ATTRIBUTION.md').write_text(attribution(notices), encoding='utf-8')
    print(f'oewn-{VERSION}: {len(output):,} bytes; source SHA-256 {SOURCE_SHA256}')


if __name__ == '__main__':
    main()
