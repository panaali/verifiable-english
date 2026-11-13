"""Pin source-checked header quotations without distributing the pinned source text.

Run from the repository root with
``python usecases/openai-preparedness/source/quote_evidence.py`` after changing
the translations. The source path and hash are owned by build_document.py.
"""

import hashlib
import json
import re
import sys
from pathlib import Path

PF = Path(__file__).resolve().parents[1]
if __name__ == "__main__":
    sys.path.insert(0, str(PF))
import build_document as B
import pf_translation as T

EVIDENCE = (PF.parents[1] / "docs/usecases/openai-preparedness/openai-preparedness-fidelity-fix"
            / "quote-hashes.json")


def plain(text):
    """Ignore page numbers inside sentences, line-break hyphens, whitespace and quote styles."""
    text = re.sub(r" \d{1,2} (?=[a-z])", " ", text.replace("\n", " "))
    return re.sub(r"[\s\-‐]+", "", text.replace("’", "'").replace("“", '"').replace("”", '"'))


def quotes(block):
    return re.findall(r"“((?:[^“”]|“[^“”]*”)*)”", block.source)


def quote_faults(blocks, source_text):
    """(block id, quote) for missing, cut or non-source quotations."""
    source, faults = plain(source_text), []
    for block in blocks:
        found = quotes(block)
        faults += [(block.id, None)] if not found else [
            (block.id, q) for q in found if "…" in q or plain(q) not in source]
    return faults


def fingerprint(blocks):
    return {block.id: [hashlib.sha256(plain(q).encode()).hexdigest() for q in quotes(block)] for block in blocks}


def blocks():
    return T.rule_blocks() + T.fact_blocks()


def main():
    source = B.DEFAULT_SOURCE.read_bytes()
    B.check_source(source)
    rows = blocks()
    faults = quote_faults(rows, source.decode())
    if faults:
        raise ValueError(f"header quotations differ from source: {faults}")
    EVIDENCE.write_text(json.dumps({"source_sha256": B.TEXT_SHA256, "quotes": fingerprint(rows)},
                                   indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
