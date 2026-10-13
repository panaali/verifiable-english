"""Which of the plan's role and link wordings (plan 2.7, D2, D10) does today's English lexicon accept as written?

Each wording is declared as the verbalisation of a fresh binary predicate in a minimal norms environment; the
lexicon lint (`ve.english.lint_english_vocabulary`) lists the codes it refuses with. No product code changes.

Usage: python3 wording_probe.py <out.json>
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from ve.document import _environment  # noqa: E402
from ve.english import lint_english_vocabulary  # noqa: E402

WORDINGS = [
    ("event", "day", "{0} happens on {1}"),
    ("event", "day", "{0} is committed on {1}"),
    ("event", "day", "{0} was committed on {1}"),
    ("event", "day", "{0} occurs on {1}"),
    ("state", "day", "{0} begins on {1}"),
    ("state", "day", "{0} ends on {1}"),
    ("state", "day", "{0} is dissolved on {1}"),
    ("day", "day", "{0} is before {1}"),
    ("day", "day", "{0} precedes {1}"),
    ("event", "event", "{0} contributed to {1}"),
    ("event", "event", "{0} was necessary for {1}"),
    ("event", "day", "{0} constitutes a penal offence on {1}"),
]


def main(out):
    rows = []
    for i, (a, b, text) in enumerate(WORDINGS):
        sorts = {s: {"description": s, "verbalisation": {"singular": s, "plural": s + "s"}} for s in {a, b}}
        name = f"probe_{i}"
        env = _environment({"language": "ve.core@0.2", "profiles": ["documents@1", "norms@0", "relational-fol@0"],
                            "spec_revision": "ve-v0.2-expand2-2026-09-25",
                            "vocabulary": {"constants": {}, "sorts": sorts, "predicates": {
                                name: {"arguments": [a, b], "description": text, "verbalisation": text}}}})
        codes = sorted({x.code for x in lint_english_vocabulary(env) if name in x.path})
        rows.append({"wording": text, "accepted": not codes, "codes": codes})
        print(("ACCEPTED " if not codes else "REFUSED  ") + text, codes)
    Path(out).write_text(json.dumps(rows, indent=1) + "\n")


if __name__ == "__main__":
    main(*sys.argv[1:])
