"""The classification of the English hand parser's rejection sites stays true (S0, spec 4.2)."""
import re
from pathlib import Path

from conformance import english_lean_rejections as R

ROOT = Path(__file__).resolve().parents[1]


def test_every_probe_witnesses_its_class():
    report = R.run()
    assert [p['id'] for p in report['probes'] if not p['consistent']] == []


def test_the_table_covers_every_error_message_of_the_hand_parser():
    source = (ROOT / 've/english.py').read_text()
    start = source.index('class EnglishParser')
    end = source.index('def _parse_english_document_uncached')
    body = source[start:end]
    messages = re.findall(r"self\.error\(f?['\"]([^'\"{]{12,})", body)
    prefixes = [s[0] for s in R.SITES]
    missing = [m for m in messages if not any(m.startswith(p[:12]) or p.startswith(m[:12]) for p in prefixes)]
    assert missing == []
