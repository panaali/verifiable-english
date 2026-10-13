"""ET-E2: retrieve candidate sentences by the pre-registered word list (phase-1 doc 1.3); no classification.

Corpora: the two pinned pilot sources (units by the run 20261012T1800Z ledgers' spans) and the four answer-key use
cases. Sentences split at '. ', '? ', '! ' and line breaks. Writes every candidate with its offsets, units and the
words that matched; the classification is a separate, hand-written file (`ete2_labels.json`).

Usage: python3 ete2_candidates.py <pilots-dir> <repo-root> <out.json>
"""
import json
import re
import sys
from pathlib import Path

RUN = "run-20261012T1800Z"
WORDS = re.compile(r"\b(within|after|before|until|till|prior to|following|since|during|deadline|expire\w*|elapse\w*|"
                   r"no later than|no earlier than|upon|once|promptly|immediately|annual\w*|periodic\w*|age|aged|"
                   r"old)\b", re.I)
NUMBER = (r"(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|fifteen|twenty|thirty|forty|"
          r"fifty|sixty|ninety|hundred)")
DURATION = re.compile(NUMBER + r"[\s-]+(?:day|week|month|year|hour|minute)s?\b", re.I)
BY_TARGETS = {"day", "days", "date", "end", "time", "week", "month", "year", "deadline", "then", "monday", "tuesday",
              "wednesday", "thursday", "friday", "saturday", "sunday", "january", "february", "march", "april", "may",
              "june", "july", "august", "september", "october", "november", "december"}
SPLIT = re.compile(rb"(?<=[.?!])\s+|\n+")


def sentences(data):
    """(start, stop, text) for each sentence of a byte string, offsets in bytes."""
    pos = 0
    for m in SPLIT.finditer(data):
        if m.start() > pos:
            yield pos, m.start(), data[pos:m.start()].decode("utf-8", "replace")
        pos = m.end()
    if pos < len(data):
        yield pos, len(data), data[pos:].decode("utf-8", "replace")


def matches(text):
    found = [m.group(0).lower() for m in WORDS.finditer(text)]
    found += [m.group(0).lower() for m in DURATION.finditer(text)]
    tokens = re.findall(r"[A-Za-z]+", text)
    for i, t in enumerate(tokens):
        if t.lower() == "by" and any(x.lower() in BY_TARGETS for x in tokens[i + 1:i + 4]):
            found.append("by " + " ".join(tokens[i + 1:i + 4]).lower())
    return found


def ledger_units(path):
    data = json.loads(Path(path).read_text())
    return [(u["id"], *u["span"]) for u in (data["units"] if isinstance(data, dict) else data)]


def corpora(pilots, repo):
    pilots, repo = Path(pilots), Path(repo)
    yield ("pilot:udhr", "udhr.md", (pilots / "udhr/source/udhr.md").read_bytes(),
           ledger_units(pilots / "udhr" / RUN / "units.json"))
    yield ("pilot:constitution", "claude-constitution.md",
           (pilots / "claude-constitution/source/claude-constitution.md").read_bytes(),
           ledger_units(pilots / "claude-constitution" / RUN / "units.json"))
    uc = repo / "usecases"
    yield ("usecase:agent-policy", "policy.ve", (uc / "agent-policy/policy.ve").read_bytes(), None)
    yield ("usecase:asimov-extended", "source.md", (uc / "asimov-extended/source.md").read_bytes(), None)
    for p in sorted((uc / "eligibility/source").glob("*.txt")):
        yield ("usecase:eligibility", p.name, p.read_bytes(), None)
    # The safety framework's PDF is not committed: its sentences are those the translation quotes in its block
    # headers, and the README's own statements of what the translation could not say.
    for name in ("rules.d1.ve", "facts.d1.ve"):
        text = (uc / "safety-framework" / name).read_text()
        quoted = "\n".join(q for line in text.splitlines() if line.startswith("## ")
                           for q in re.findall(r"“([^”]+)”|\"([^\"]+)\"", line) for q in q if q)
        yield ("usecase:safety-framework", name + " (quoted)", quoted.encode(), None)
    yield ("usecase:safety-framework", "README.md", (uc / "safety-framework/README.md").read_bytes(), None)


def main(pilots, repo, out):
    rows = []
    for corpus, name, data, units in corpora(pilots, repo):
        for a, b, text in sentences(data):
            found = matches(text)
            if not found:
                continue
            ids = [u for u, s, e in units if s < b and a < e] if units else []
            rows.append({"n": len(rows), "corpus": corpus, "file": name, "span": [a, b], "units": ids,
                         "words": sorted(set(found)), "text": text.strip()})
    Path(out).write_text(json.dumps(rows, indent=1, ensure_ascii=False) + "\n")
    by = {}
    for r in rows:
        by[r["corpus"]] = by.get(r["corpus"], 0) + 1
    print(len(rows), by)


if __name__ == "__main__":
    main(*sys.argv[1:])
