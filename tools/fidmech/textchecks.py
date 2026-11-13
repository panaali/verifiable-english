"""L1, the header-quote checks per rule and fact block (plan section 3.2; L1a is fid-mech-b2's): a report, never a gate.

Classes, one hit per quote, the first that applies: L1m (a header with no checkable quotation) > L1n (equal with
every digit run masked, unequal as written) > L1u (not source text under norm(), in the main or a footnote stream)
> L1c (not a whole run of sentences, or a list item without its lead-in among the block's quotes) > L1e (an
elision). A quotation inside a translator's note in brackets, such as ("promptly" is OT12), is no source quote: it is
counted in the info class `note`, outside the headline.
"""
from __future__ import annotations

import bisect
import hashlib
import re
from dataclasses import dataclass
from pathlib import Path

from tools.fidmech import segment as S

CLASSES = ("L1m", "L1n", "L1u", "L1c", "L1e")
INFO = ("note", "empty")
ELLIPSIS = re.compile(r"\[\.\.\.\]|\.\.\.")  # after norm(), which folds … to ... and drops the spaces inside [ ]
START_SLACK = re.compile(r'[ "(\[]*')
END_SLACK = re.compile(r'[ "\')\].,;:!?]*')
MAX_OCCURRENCES = 500
# Today's merge-train checks that already fail a hit of this class on this document (plan section 1, Opus round 2
# point 9). FSF's WILL_FEATURES test compares its own quote table, not header quotes, so no FSF class is listed.
ALSO_GATED = {"openai-preparedness": {
    "L1m": "quote_evidence.py:39 (a block with no quotation)",
    "L1u": "quote_evidence.py:40 via test_pf_fidelity_fix.py:179 (plain() substring)",
    "L1e": "quote_evidence.py:40 and test_pf_fidelity_fix.py:184 ('…')"}}


@dataclass(frozen=True)
class Quote:
    text: str
    at: int  # character offset in the header's source field
    note: bool  # inside a translator's note in brackets


def header_quotes(field: str) -> tuple[list[Quote], str | None]:
    """The outermost quotations of a header source field, with safetyfw_accounting.scan_quotes's pairing of the
    marks (curly by direction; a straight mark closes a straight quote open innermost, else opens one), each marked
    when it lies inside brackets outside any quotation. An unpaired mark is a problem, returned beside."""
    acc = S.accounting
    out, stack, start, depth = [], [], 0, 0
    for i, ch in enumerate(field):
        if ch == acc.CLOSES or (ch == acc.STRAIGHT and stack and stack[-1] == acc.STRAIGHT):
            if not stack or stack[-1] != (acc.OPENS if ch == acc.CLOSES else acc.STRAIGHT):
                return out, f"unpaired closing quote mark at character {i}"
            stack.pop()
            if not stack:
                out.append(Quote(field[start:i], start, depth > 0))
        elif ch in (acc.OPENS, acc.STRAIGHT):
            if not stack:
                start = i + 1
            stack.append(ch)
        elif not stack and ch in "([":
            depth += 1
        elif not stack and ch in ")]":
            depth = max(depth - 1, 0)
    return out, (f"unclosed quote mark at character {start - 1}" if stack else None)


def _occurrences(hay: str, needle: str):
    i, n = hay.find(needle), 0
    while i >= 0 and n < MAX_OCCURRENCES:
        yield i
        i, n = hay.find(needle, i + 1), n + 1


def _chains(hay: str, frags):
    """Every placement of the fragments in order: each occurrence of the first, the rest at their next occurrence."""
    for i in _occurrences(hay, frags[0]):
        spans, at = [(i, i + len(frags[0]))], i + len(frags[0])
        for f in frags[1:]:
            j = hay.find(f, at)
            if j < 0:
                break
            spans.append((j, j + len(f)))
            at = j + len(f)
        else:
            yield spans


@dataclass(frozen=True)
class Placement:
    stream: str
    sentences: tuple[int, ...]  # the sentence indices the fragments touch
    whole: bool  # starts at a sentence start and runs to a sentence end
    lead_in: int | None  # the lead-in the first sentence needs
    start: int  # bytes
    end: int


def _placements(seg: S.Segmentation, frags):
    for stream in seg.streams:
        canon = stream.canon
        for text in (canon, stream.marked) if stream.marked is not canon else (canon,):
            for spans in _chains(text.text, frags):
                if text is not canon:  # back to the canonical stream through the bytes
                    spans = [(bisect.bisect_left(canon.starts, text.starts[a]),
                              bisect.bisect_right(canon.ends, text.ends[z - 1])) for a, z in spans]
                    if any(a >= z for a, z in spans):
                        continue
                touched = sorted({k for a, z in spans
                                  for k in range(stream.sentence_at(a), stream.sentence_at(z - 1) + 1)})
                if touched != list(range(touched[0], touched[-1] + 1)):
                    continue  # the fragments skip a whole sentence: not one run of contiguous sentences
                first, last = stream.sentences[touched[0]], stream.sentences[touched[-1]]
                a, z = spans[0][0], spans[-1][1]
                whole = (any(START_SLACK.fullmatch(canon.text, x, a) for x in (first.i0, first.ib) if x <= a)
                         and END_SLACK.fullmatch(canon.text, z, max(z, last.i1)) is not None)
                yield Placement(stream.name, tuple(touched), whole, first.lead_in, canon.starts[a], canon.ends[z - 1])


def _masked_found(seg: S.Segmentation, frags) -> bool:
    mf = [S.masked(f) for f in frags]
    return any(next(_chains(S.masked(t.text), mf), None) is not None
               for stream in seg.streams for t in (stream.canon, stream.marked))


@dataclass(frozen=True)
class Hit:
    cls: str
    block: str
    file: str
    quote: str | None
    detail: str
    at: tuple[str, int, int] | None = None  # (stream, byte start, byte end) of the chosen placement

    def key(self):
        return (self.cls, self.block, self.quote)

    def to_dict(self):
        return {"class": self.cls, "block": self.block, "file": self.file, "quote": self.quote,
                "detail": self.detail, "at": list(self.at) if self.at else None}


def check_block(seg: S.Segmentation, block: dict) -> tuple[list[Hit], dict]:
    """L1 on one block: (hits, info counts)."""
    found, problem = header_quotes(block["source"])
    info = {"note": sum(q.note for q in found), "empty": 0, "checked": 0}
    rows = []
    for q in found:
        if q.note:
            continue
        n = S.norm(q.text).strip()
        frags = [f.strip() for f in ELLIPSIS.split(n)]
        frags = [f for f in frags if f]
        if not frags or re.fullmatch(r"[\W_]*", n):
            info["empty"] += 1
            continue
        rows.append((q, frags, ELLIPSIS.search(n) is not None))
    hit = lambda cls, q, detail, at=None: Hit(cls, block["id"], block["file"], q, detail, at)  # noqa: E731
    if not rows:
        why = problem or ("only quotations in translator's notes" if info["note"] else
                          "only empty quotations" if info["empty"] else "no quotation")
        return [hit("L1m", None, why)], info
    info["checked"] = len(rows)
    placed = [(q, frags, elided, list(_placements(seg, frags))) for q, frags, elided in rows]
    covered = set()
    for _, _, _, places in placed:
        best = next((p for p in places if p.whole), places[0] if places else None)
        if best:
            covered.update((best.stream, i) for i in best.sentences)
    hits = []
    for q, frags, elided, places in placed:
        if not places:
            masked = _masked_found(seg, frags)
            hits.append(hit("L1n" if masked else "L1u", q.text,
                            "equal only with the digit runs masked" if masked else "not source text under norm()"))
            continue
        ranked = sorted(places, key=lambda p: (not p.whole, p.lead_in is not None
                                               and (p.stream, p.lead_in) not in covered))
        p = ranked[0]
        at = (p.stream, p.start, p.end)
        if not p.whole:
            hits.append(hit("L1c", q.text, "not a whole sentence run", at))
        elif p.lead_in is not None and (p.stream, p.lead_in) not in covered:
            hits.append(hit("L1c", q.text, "a list item quoted without its lead-in", at))
        elif elided:
            hits.append(hit("L1e", q.text, "an elision", at))
    return hits, info


def read_blocks(case: Path) -> list[dict]:
    return [b for name in S.accounting.BLOCK_FILES if (case / name).exists()
            for b in S.accounting.read_blocks(case / name)]


def l1(seg: S.Segmentation, blocks) -> tuple[list[Hit], dict]:
    hits, info = [], {"note": 0, "empty": 0, "checked": 0}
    for block in blocks:
        h, i = check_block(seg, block)
        hits += h
        for k in info:
            info[k] += i[k]
    return hits, info


def counts(hits) -> dict:
    return {c: sum(h.cls == c for h in hits) for c in CLASSES}


def report(case: Path, data: bytes, boundaries_path: Path) -> dict:
    """The L1 report of one case: hits per class, raw and with each lever off, and what each lever clears."""
    source = S.Source(data)
    b = S.load_boundaries(boundaries_path)
    blocks = read_blocks(case)
    seg = S.Segmentation(source, b)
    hits, info = l1(seg, blocks)
    keys = {h.key() for h in hits}
    levers = {}
    for lever in S.LEVERS:
        off, _ = l1(S.Segmentation(source, b.without(lever)), blocks)
        off_keys = {h.key() for h in off}
        levers[lever] = {"counts": counts(off), "cleared": sorted(map(list, off_keys - keys), key=str),
                         "added": sorted(map(list, keys - off_keys), key=str)}
    gated = ALSO_GATED.get(case.name, {})
    return {"document": case.name, "checks": ["L1"], "source_sha256": source.sha256,
            "boundaries_sha256": hashlib.sha256(Path(boundaries_path).read_bytes()).hexdigest(),
            "blocks": len(blocks), "quotes": info, "counts": counts(hits),
            "also_gated": {c: {"by": gated[c], "hits": sum(h.cls == c for h in hits)} for c in gated},
            "sentences": {"main": len(seg.streams[0].sentences),
                          "footnote": sum(len(s.sentences) for s in seg.streams[1:])},
            "footnote_pairs": {"generator": sum(f["by"] == "generator" for f in b.footnotes),
                               "hand": sum(f["by"] == "hand" for f in b.footnotes)},
            "unpaired_digit_runs": len(seg.unpaired_runs),
            "hits": [h.to_dict() for h in hits], "levers": levers}
