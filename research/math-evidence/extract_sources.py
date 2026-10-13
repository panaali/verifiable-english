"""ME-0: derive each target's pinned plain text (`source.txt`) from the raw bytes `fetch_sources.py` pinned.

Deterministic; the rules are stated per target below and repeated in each `SOURCE.md`. The derived text is the
denominator of the ledger. Formulas stay as the source writes them (TeX for Wikisource, OCR for the 1927 scan):
ME-0 never transcribes a formula into words in a source file (plan, ME-0).

    python3 -I research/math-evidence/extract_sources.py [--check]
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "docs/research/evidence/math-evidence"


# --- Physics: Wikisource page wikitext -> text -------------------------------------------------------------

def _wiki_inline(text: str, notes: list[str]) -> str:
    def ref(match: re.Match) -> str:
        notes.append(match.group(1))
        return f" [note {len(notes)}: {_wiki_inline(match.group(1).strip(), [])}]"

    text = re.sub(r"<ref>(.*?)</ref>", ref, text, flags=re.S)
    text = re.sub(r"<math>\s*(?:\\scriptstyle\s*)?(.*?)</math>", lambda m: "$" + m.group(1).strip() + "$", text,
                  flags=re.S)
    text = re.sub(r"\[\[(?:Image|File):[^|\]]*?- ([^|\]]+?)\.png[^\]]*\]\]", r"[Image: \1]", text)
    text = re.sub(r"\[\[[^|\]]*\|([^\]]*)\]\]", r"\1", text)
    text = re.sub(r"\[\[([^\]]*)\]\]", r"\1", text)
    text = re.sub(r"\{\{Hyphenated word start\|[^|}]*\|([^}]*)\}\}", r"\1", text)
    text = re.sub(r"\{\{Hyphenated word end\|[^}]*\}\}", "", text)
    text = re.sub(r"\{\{(?:sc|c|lang\|[a-z]+)\|([^{}]*)\}\}", r"\1", text)
    text = re.sub(r"\{\{(?:c/s|c/e|rule|smallrefs)\}\}", "", text)
    text = re.sub(r"<sup>(.*?)</sup>", r"^\1", text)
    text = re.sub(r"<sub>(.*?)</sub>", r"\1", text)
    text = re.sub(r"<br\s*/?>", "", text)
    text = text.replace("'''", "").replace("''", "").replace("&nbsp;", " ")
    return text


def _wiki_table(block: str) -> str:
    rows, lines = [], block.strip().splitlines()
    for line in lines[1:]:
        if line.startswith("|-") or line.startswith("|}"):
            continue
        cells = [c.strip() for c in line.lstrip("|").split("||")]
        cells = [re.sub(r'^\s*colspan="\d+"\s*align="center"\s*\|', "", c).strip() for c in cells]
        cells = [_wiki_inline(c, []).strip() for c in cells]
        while cells and not cells[-1]:
            cells.pop()
        rows.append(" | ".join(cells))
    return "\n".join(rows)


def physics() -> bytes:
    raw = EVIDENCE / "physics-michelson-morley/raw"
    pages = []
    for n in range(1, 14):
        text = (raw / f"page-{n:02d}.wiki").read_text(encoding="utf-8")
        text = re.sub(r"<noinclude>.*?</noinclude>", "", text, flags=re.S)
        pages.append(text)
    body = "\n".join(p.strip("\n") for p in pages)
    table = re.search(r"\{\|.*?\n\|\}", body, flags=re.S)
    assert table
    body = body[:table.start()] + _wiki_table(table.group(0)) + body[table.end():]
    body = _wiki_inline(body, [])
    body = re.sub(r"^:", "", body, flags=re.M)
    body = re.sub(r"[ \t]+\n", "\n", body)
    body = re.sub(r"\n{3,}", "\n\n", body)
    head = ("On the Relative Motion of the Earth and the Luminiferous Ether\n"
            "Albert A. Michelson and Edward W. Morley\n"
            "American Journal of Science, 3rd series, vol. 34, no. 203, pp. 333-345, November 1887\n\n")
    return (head + body.strip() + "\n").encode("utf-8")


# --- Mathematics: the 1927 Collected Papers OCR (Kerala scan), the paper's exact byte slice.
# Of the two OCR texts fetched, the Kerala item keeps the paper's numerals 300, 324 and 162 intact; the Hardy item
# prints them as 800/900, 22324 and 22102. The choice was made after reading both slices. --------------------------------

RAM_START = b"A PROOF OF BERTRAND"
RAM_END = b"respectively. \n"


def ramanujan_slice() -> tuple[int, int, bytes]:
    raw = (EVIDENCE / "math-ramanujan-bertrand/raw/collected-papers-1927-kerala-item_djvu.txt").read_bytes()
    start = raw.index(RAM_START)
    end = raw.index(RAM_END, start) + len(RAM_END)
    return start, end, raw[start:end]


def mathematics() -> bytes:
    return ramanujan_slice()[2]


# --- Deep learning: the Europe PMC JATS of the CC BY 4.0 article -> text ------------------------------------

def _jats_inline(e: ET.Element) -> str:
    out = [e.text or ""]
    for c in e:
        if c.tag == "xref" and c.get("ref-type") == "bibr":
            out.append("[" + "".join(c.itertext()) + "]")
        elif c.tag in ("fig", "table-wrap", "supplementary-material"):
            pass
        else:
            out.append(_jats_inline(c))
        out.append(c.tail or "")
    return re.sub(r"\s+", " ", "".join(out))


def _jats_block(e: ET.Element, out: list[str], depth: int) -> None:
    for c in e:
        if c.tag == "title":
            out.append("#" * depth + " " + _jats_inline(c).strip())
        elif c.tag == "p":
            out.append(_jats_inline(c).strip())
            for f in c.iter("fig"):
                _jats_fig(f, out)
        elif c.tag == "fig":
            _jats_fig(c, out)
        elif c.tag in ("sec", "ack", "notes", "app"):
            _jats_block(c, out, depth + 1)
        elif c.tag == "supplementary-material":
            text = _jats_inline(c).strip()
            if text:
                out.append(text)
        elif c.tag == "ref-list":
            out.append("#" * depth + " References")
            for ref in c.findall("ref"):
                label = ref.findtext("label") or ""
                cite = ref.find("mixed-citation")
                if cite is None:
                    cite = ref.find(".//mixed-citation")
                out.append(f"{label}. " + _jats_inline(cite).strip())


def _jats_fig(f: ET.Element, out: list[str]) -> None:
    label = (f.findtext("label") or "").strip()
    cap = f.find("caption")
    parts = [_jats_inline(x).strip() for x in cap] if cap is not None else []
    out.append((label + " " + " ".join(parts)).strip())


def deep_learning() -> bytes:
    root = ET.parse(EVIDENCE / "dl-alphafold/raw/europepmc-fulltext.xml").getroot()
    meta = root.find("front/article-meta")
    title = _jats_inline(meta.find("title-group/article-title")).strip()
    out = [title,
           "John Jumper et al. (34 authors), Nature 596, 583-589 (2021), doi:10.1038/s41586-021-03819-2, "
           "licensed under CC BY 4.0",
           "# Abstract",
           _jats_inline(meta.find("abstract[@id='Abs1']")).strip()]
    _jats_block(root.find("body"), out, 1)
    _jats_block(root.find("back"), out, 1)
    text = "\n\n".join(x for x in out if x.strip())
    return (text + "\n").encode("utf-8")


# --- VE's own paper: in-repository bytes ---------------------------------------------------------------------

APPENDIX_HEAD = b"## Per-template differences of the co-primary contrasts (false approval)\n"
APPENDIX_NEXT = b"## E1b comprehension"


def ve_paper_e1() -> bytes:
    return (ROOT / "paper/sections/04-e1.md").read_bytes()


def ve_paper_appendix() -> bytes:
    raw = (ROOT / "paper/sections/10-appendices.md").read_bytes()
    start = raw.index(APPENDIX_HEAD)
    return raw[start:raw.index(APPENDIX_NEXT, start)]


SOURCES = {
    "physics-michelson-morley/source.txt": physics,
    "math-ramanujan-bertrand/source.txt": mathematics,
    "dl-alphafold/source.txt": deep_learning,
    "ve-paper-e1/source-04-e1.md": ve_paper_e1,
    "ve-paper-e1/source-appendix-per-template.md": ve_paper_appendix,
}


def main(check: bool) -> int:
    digests = {}
    for name, make in SOURCES.items():
        data = make()
        path = EVIDENCE / name
        if check:
            if path.read_bytes() != data:
                print(f"stale: {name}", file=sys.stderr)
                return 1
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        digests[name] = {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
    start, end, _ = ramanujan_slice()
    digests["math-ramanujan-bertrand/source.txt"]["slice_of_raw"] = [start, end]
    print(json.dumps(digests, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main("--check" in sys.argv))
