"""Page-aware segmentation of a pinned source into sentences, on raw byte offsets (plan sections 2b and 3.1).

A pinned source holds one page per line. Its page furniture (running footers, repeated table headers) is matched by
patterns anchored to a page start or end; footnote pairs (marker, body) are proposed by `propose` and frozen in the
document's fidmech/boundaries.json, never inferred at check time. Two streams are built: the main text (pages joined,
furniture and footnote bodies cut out, frozen markers removed) and one stream per footnote body. Every normalised
character keeps the byte range of the source character it comes from, so a located quote is a byte span, as the
spans.json offsets are. Everything here is deterministic and pure.
"""
from __future__ import annotations

import bisect
import hashlib
import importlib.util
import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, replace
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def _accounting():
    """usecases/safetyfw_accounting.py, the owner of the character folding table and the block reader."""
    if "safetyfw_accounting" not in sys.modules:
        spec = importlib.util.spec_from_file_location("safetyfw_accounting", REPO / "usecases/safetyfw_accounting.py")
        module = importlib.util.module_from_spec(spec)
        sys.modules["safetyfw_accounting"] = module
        spec.loader.exec_module(module)
    return sys.modules["safetyfw_accounting"]


accounting = _accounting()

SCHEMA = "fidmech-boundaries/1"
# Generic rules, frozen on RSP before any FSF or PF run (plan 3.0). A document's own abbreviations are a lever.
GENERIC_ABBREV = ("e.g.", "i.e.", "cf.", "vs.")
BULLETS = "●○▪•"
LEVERS = ("extra", "suppress", "abbrev", "furniture", "footnotes", "hand-footnotes")
# Marks accounting.norm leaves alone; a single quote is folded to the double one (apostrophes alike on both sides).
EXTRA_FOLD = {"‐": "-", "‑": "-", "‒": "-", "−": "-"}
OPEN_MARKS, CLOSE_MARKS, NO_SPACE_BEFORE = "“‘([", "”’)]", ".,;:!?"
DIGIT_RUN = re.compile(r"(?<!\S)(\d{1,2})(?!\S)")
BODY_SHAPE = re.compile(r"\s+[“\"‘']?[A-Z]")
LABEL = re.compile(r"(?:[%s]|\d+(?:\.\d+)*\.|\((?:\d+|[a-z])\)) " % BULLETS)
NUMBER_ITEM = re.compile(r"\d+(?:\.\d+)*\. [A-Z]")
LEAD_IN = re.compile(r":(?= (?:[%s]|\((?:\d+|[a-z])\) |\d+(?:\.\d+)*\. [A-Z]))" % BULLETS)
RUN_IN = re.compile(r":(?= [A-Z])")


class BoundariesError(ValueError):
    """A boundaries.json that is malformed, stale or does not fit its source."""


# ---------------------------------------------------------------------------------------------------------------
# norm(): the one normaliser, used on source streams and quotes alike


def fold(ch: str) -> str:
    out = EXTRA_FOLD.get(ch) or accounting.norm(ch)
    return out.replace("'", '"')


@dataclass(frozen=True)
class Text:
    """A normalised text; starts[i], ends[i] are the byte range of the source character text[i] comes from."""
    text: str
    starts: tuple[int, ...]
    ends: tuple[int, ...]

    def index_of_byte(self, at: int) -> int | None:
        i = bisect.bisect_left(self.starts, at)
        return i if i < len(self.text) and self.starts[i] == at else None


def normalise(items) -> Text:
    """Fold quote styles, dashes and ligatures; collapse whitespace; drop a space after an opening mark and before a
    closing mark or punctuation. items: (character, byte start, byte end) in order."""
    out, starts, ends = [], [], []
    pending, after_open = None, True
    for ch, b0, b1 in items:
        s = fold(ch)
        if s.isspace() or s == "":
            pending = pending or (b0, b1)
            continue
        if pending and out and not after_open and ch not in CLOSE_MARKS and s[0] not in NO_SPACE_BEFORE:
            out.append(" ")
            starts.append(pending[0])
            ends.append(pending[1])
        pending = None
        for c in s:
            out.append(c)
            starts.append(b0)
            ends.append(b1)
        after_open = ch in OPEN_MARKS
    return Text("".join(out), tuple(starts), tuple(ends))


def norm(text: str) -> str:
    """norm() of a quote: the same folding, with no byte map."""
    return normalise((c, 0, 0) for c in text).text


def masked(text: str) -> str:
    """Every digit run masked to one placeholder (L1n's alignment, plan 3.2)."""
    return re.sub(r"\d+", "#", text)


# ---------------------------------------------------------------------------------------------------------------
# The source and its boundaries file


class Source:
    def __init__(self, data: bytes):
        self.data = data
        self.text = data.decode("utf-8")
        self.sha256 = hashlib.sha256(data).hexdigest()
        self.byte = [0]
        for ch in self.text:
            self.byte.append(self.byte[-1] + len(ch.encode("utf-8")))
        self.pages, at = [], 0
        for line in self.text.split("\n"):
            self.pages.append((at, at + len(line)))
            at += len(line) + 1
        self.page_starts = [a for a, _ in self.pages]

    def char(self, at: int) -> int:
        """The character index at byte offset `at`; a BoundariesError unless `at` starts a character."""
        i = bisect.bisect_left(self.byte, at) if isinstance(at, int) and not isinstance(at, bool) else -1
        if not 0 <= i < len(self.text) or self.byte[i] != at:
            raise BoundariesError(f"offset {at!r} is not a character start inside the source")
        return i

    def page_of(self, ci: int) -> int:
        return bisect.bisect_right(self.page_starts, ci) - 1


@dataclass(frozen=True)
class Boundaries:
    source_sha256: str
    abbrev: tuple = ()
    furniture: tuple = ()
    footnotes: tuple = ()
    unpaired: tuple = ()
    extra: tuple = ()
    suppress: tuple = ()

    def without(self, lever: str) -> "Boundaries":
        if lever == "hand-footnotes":
            return replace(self, footnotes=tuple(f for f in self.footnotes if f["by"] != "hand"))
        if lever not in LEVERS:
            raise ValueError(f"unknown lever {lever!r}")
        return replace(self, **{lever: ()})


_ENTRY_KEYS = {"abbrev": {"text", "reason"}, "furniture": {"pattern", "where", "reason"},
               "footnotes": {"n", "marker_at", "body", "by", "reason"}, "unpaired": {"at", "n", "reason"},
               "extra": {"at", "reason"}, "suppress": {"at", "reason"}}


def parse_boundaries(data) -> Boundaries:
    """The file's shape: every entry a dict with exactly its keys and a non-empty reason."""
    if not isinstance(data, dict) or set(data) != {"schema", "source_sha256", *_ENTRY_KEYS}:
        raise BoundariesError(f"boundaries: keys must be schema, source_sha256, {', '.join(sorted(_ENTRY_KEYS))}")
    if data["schema"] != SCHEMA or not isinstance(data["source_sha256"], str):
        raise BoundariesError(f"boundaries: schema must be {SCHEMA} and source_sha256 a string")
    for key, keys in _ENTRY_KEYS.items():
        if not isinstance(data[key], list):
            raise BoundariesError(f"boundaries: {key} must be a list")
        for entry in data[key]:
            if not isinstance(entry, dict) or set(entry) != keys:
                raise BoundariesError(f"boundaries: a {key} entry needs exactly {sorted(keys)}: {entry!r}")
            if not isinstance(entry["reason"], str) or not entry["reason"].strip():
                raise BoundariesError(f"boundaries: a {key} entry without a reason: {entry!r}")
    return Boundaries(data["source_sha256"], *(tuple(data[k]) for k in _ENTRY_KEYS))


def load_boundaries(path: Path) -> Boundaries:
    return parse_boundaries(json.loads(Path(path).read_text(encoding="utf-8")))


def _int(value, what):
    if not isinstance(value, int) or isinstance(value, bool):
        raise BoundariesError(f"{what} must be an integer: {value!r}")
    return value


def furniture_matches(source: Source, furniture) -> list[tuple[int, int, int, int]]:
    """(entry index, page, char start, char end) of every furniture match; an unanchored pattern, a match away from
    its stated page position, an empty match or a pattern that matches no page is a BoundariesError."""
    out = []
    for k, entry in enumerate(furniture):
        pattern, where = entry["pattern"], entry["where"]
        anchored = {"page-start": pattern.startswith("^"),
                    "page-end": pattern.endswith("$") and not pattern.endswith("\\$")}
        if where not in anchored or not anchored[where]:
            raise BoundariesError(f"furniture pattern {pattern!r} is not anchored to its {where!r}")
        try:
            rx = re.compile(pattern)
        except re.error as e:
            raise BoundariesError(f"furniture pattern {pattern!r}: {e}") from None
        hits = 0
        for p, (a, b) in enumerate(source.pages):
            m = rx.search(source.text[a:b])
            if m is None:
                continue
            if m.end() == m.start() or (m.start() != 0 if where == "page-start" else m.end() != b - a):
                raise BoundariesError(f"furniture pattern {pattern!r} matches away from the {where} of page {p + 1}")
            out.append((k, p, a + m.start(), a + m.end()))
            hits += 1
        if not hits:
            raise BoundariesError(f"furniture pattern {pattern!r} matches no page")
    return out


def _standalone(source: Source, ci: int, n: int) -> bool:
    digits = str(n)
    t = source.text
    return (t.startswith(digits, ci) and (ci == 0 or t[ci - 1].isspace())
            and (ci + len(digits) == len(t) or t[ci + len(digits)].isspace()))


def validate(source: Source, b: Boundaries) -> list[tuple[int, int, int, int]]:
    """Check b against source; returns the furniture matches. Footnotes (plan 2b): the marker's digits equal n, the
    body starts with n, each marker has one body and each body one marker, the body lies after its marker on the same
    or the next page, on one page, clear of furniture and of other bodies."""
    if b.source_sha256 != source.sha256:
        raise BoundariesError(f"boundaries are for source {b.source_sha256[:12]}, not {source.sha256[:12]}")
    for entry in b.abbrev:
        if not isinstance(entry["text"], str) or not re.fullmatch(r"\S+\.", entry["text"]):
            raise BoundariesError(f"abbreviation {entry['text']!r} must be one token ending in '.'")
    furn = furniture_matches(source, b.furniture)
    cut = [(s, e) for _, _, s, e in furn]
    markers, bodies = set(), []
    for f in b.footnotes:
        n = _int(f["n"], "footnote n")
        if f["by"] not in ("generator", "hand"):
            raise BoundariesError(f"footnote {n}: by must be generator or hand")
        body = f["body"]
        if not isinstance(body, list) or len(body) != 2:
            raise BoundariesError(f"footnote {n}: body must be [start, end]")
        m, s = source.char(_int(f["marker_at"], "marker_at")), source.char(_int(body[0], "body start"))
        e = source.char(_int(body[1], "body end")) if body[1] != len(source.data) else len(source.text)
        if not _standalone(source, m, n):
            raise BoundariesError(f"footnote {n}: the marker at {f['marker_at']} is not the digit run {n}")
        if not _standalone(source, s, n) or not BODY_SHAPE.match(source.text, s + len(str(n))):
            raise BoundariesError(f"footnote {n}: the body at {body[0]} does not start with {n} and a capital")
        ps, pm = source.page_of(s), source.page_of(m)
        if not (m < s < e) or source.page_of(e - 1) != ps or ps - pm not in (0, 1):
            raise BoundariesError(f"footnote {n}: the body must follow its marker on the same or the next page")
        if m in markers or any(s < e2 and s2 < e for s2, e2 in bodies + cut):
            raise BoundariesError(f"footnote {n}: a marker with two bodies, or a body overlapping another or furniture")
        markers.add(m)
        bodies.append((s, e))
    for entry in b.unpaired:
        if not _standalone(source, source.char(_int(entry["at"], "unpaired at")), _int(entry["n"], "unpaired n")):
            raise BoundariesError(f"unpaired entry at {entry['at']} is not the digit run {entry['n']}")
    for key in ("extra", "suppress"):
        for entry in getattr(b, key):
            source.char(_int(entry["at"], f"{key} at"))
    return furn


# ---------------------------------------------------------------------------------------------------------------
# The footnote-pair generator (plan 3.1): proposals only; its output is frozen in boundaries.json


def _blanked_pages(source: Source, furn):
    chars = list(source.text)
    for _, _, s, e in furn:
        chars[s:e] = " " * (e - s)
    return "".join(chars)


def propose(source: Source, furniture) -> tuple[list[dict], list[dict]]:
    """(pairs, unresolved). A body is a run "<n> <Capitalised text>"; it pairs with a marker when n occurs exactly
    twice on the body's page and the page before it, the other run first. A marker has the shape of a body, so the
    first run is never a body candidate. Other body-shaped runs are listed unresolved, for a hand decision."""
    furn = furniture_matches(source, furniture)
    text = _blanked_pages(source, furn)
    occ = defaultdict(list)
    for p, (a, b) in enumerate(source.pages):
        for m in DIGIT_RUN.finditer(text, a, b):
            occ[int(m[1])].append((m.start(), p, BODY_SHAPE.match(text, m.end()) is not None))
    pairs, used = [], set()
    for n, runs in sorted(occ.items()):
        for pos, p, shaped in runs:
            window = [r[0] for r in runs if r[1] in (p - 1, p)]
            if shaped and len(window) == 2 and window[1] == pos:
                pairs.append((n, window[0], pos))
                used.update((window[0], pos))
    starts_by_page = defaultdict(list)
    for _, _, s in pairs:
        starts_by_page[source.page_of(s)].append(s)
    out = []
    for n, m, s in sorted(pairs, key=lambda x: x[2]):
        out.append({"n": n, "marker_at": source.byte[m], "body": body_span(source, furn, s, starts_by_page),
                    "by": "generator", "reason": f"generator: {n} occurs twice on pages "
                    f"{source.page_of(m) + 1}-{source.page_of(s) + 1}, the second run body-shaped"})
    unresolved = [{"at": source.byte[pos], "n": n, "page": p + 1,
                   "context": source.text[max(pos - 30, source.pages[p][0]):pos + 40]}
                  for n, runs in sorted(occ.items()) for pos, p, shaped in runs if shaped and pos not in used]
    return out, sorted(unresolved, key=lambda u: u["at"])


def body_span(source: Source, furn, s: int, starts_by_page) -> list[int]:
    """[start, end] in bytes of the body at char s: to the next body or furniture on its page, or the page end."""
    p = source.page_of(s)
    ends = [source.pages[p][1]] + [x for x in starts_by_page[p] if x > s] + [fs for _, _, fs, _ in furn if fs > s]
    e = min(ends)
    while e > s and source.text[e - 1].isspace():
        e -= 1
    return [source.byte[s], source.byte[e]]


# ---------------------------------------------------------------------------------------------------------------
# Streams and sentences


@dataclass(frozen=True)
class Sentence:
    stream: str
    index: int
    i0: int  # normalised index of the start, of the text after a list label, and of the end (exclusive)
    ib: int
    i1: int
    start: int  # bytes
    end: int
    item: str | None  # the list glyph ("●", "(n)", "n.") the sentence starts with
    lead_in: int | None  # the index of its lead-in sentence in the same stream
    is_lead_in: bool
    text: str


@dataclass(frozen=True)
class Stream:
    name: str
    canon: Text  # frozen markers removed: sentences are cut on this text
    marked: Text  # frozen markers kept: a quote may be located here too
    sentences: tuple[Sentence, ...]

    def sentence_at(self, i: int) -> int:
        return bisect.bisect_right([s.i0 for s in self.sentences], i) - 1


def _abbrev_before(t: str, at: int, abbrev) -> bool:
    token = t[t.rfind(" ", 0, at) + 1:at + 1].lstrip('"([').lower()
    return token in abbrev


def cuts(t: str, abbrev) -> set[int]:
    """Sentence starts (plan 3.1): after . ? ! (and closing marks) and a space, before an upper-case letter, an
    opening mark, a bullet glyph or a numbered item ("2. Redaction"), unless after an abbreviation; at every bullet
    glyph; after a ':' lead-in directly before a bullet, a numbered item or an inline item number such as "(1)",
    which elsewhere splits nothing; after a run-in label's ':' before an upper-case letter ("Internal review: We")."""
    out = set()
    for m in re.finditer(r"[.?!][\"')\]]*", t):
        k = m.end() + 1
        if k >= len(t) or t[m.end()] != " ":
            continue
        if t[k].isupper() or t[k] in "\"([" + BULLETS or NUMBER_ITEM.match(t, k):
            if not (t[m.start()] == "." and _abbrev_before(t, m.start(), abbrev)):
                out.add(k)
    out.update(m.start() for m in re.finditer(f"[{BULLETS}]", t) if m.start())
    out.update(m.end() + 1 for m in LEAD_IN.finditer(t))
    out.update(m.end() + 1 for m in RUN_IN.finditer(t))
    return out


def _item(t: str, i: int) -> str | None:
    m = LABEL.match(t, i)
    if not m:
        return None
    label = m[0][:-1]
    return label if label in BULLETS else "(n)" if label.startswith("(") else "n."


def sentences(name: str, canon: Text, starts: set[int]) -> tuple[Sentence, ...]:
    t = canon.text
    bounds = sorted({0, *starts} - {len(t)}) + [len(t)]
    spans = []
    for a, z in zip(bounds, bounds[1:]):
        while z > a and t[z - 1] == " ":
            z -= 1
        if z > a:
            spans.append((a, z))
    out, stack = [], []
    for k, (a, z) in enumerate(spans):
        item = _item(t, a)
        nxt = _item(t, spans[k + 1][0]) if k + 1 < len(spans) else None
        lead = None
        if item:
            while stack and stack[-1][1] != item:
                stack.pop()
            lead = stack[-1][0] if stack else None
        elif nxt is None:
            stack = []
        is_lead = t[z - 1] == ":" and nxt is not None
        if is_lead:
            stack.append((k, nxt))
        label = LABEL.match(t, a)
        out.append(Sentence(name, k, a, label.end() if label else a, z, canon.starts[a], canon.ends[z - 1],
                            item, lead, is_lead, t[a:z]))
    return tuple(out)


def _mask(size, ranges) -> bytearray:
    gone = bytearray(size)
    for s, e in ranges:
        gone[s:e] = b"\x01" * (e - s)
    return gone


class Segmentation:
    """A source cut into a main stream and one stream per frozen footnote body (plan 3.1)."""

    def __init__(self, source: Source, b: Boundaries):
        self.source, self.boundaries = source, b
        furn = validate(source, b)
        cut = [(s, e) for _, _, s, e in furn]
        self.bodies = []
        markers = []
        for f in b.footnotes:
            s, e = source.char(f["body"][0]), (source.char(f["body"][1]) if f["body"][1] != len(source.data)
                                                else len(source.text))
            self.bodies.append((f["n"], s, e))
            m = source.char(f["marker_at"])
            markers.append((m, m + len(str(f["n"]))))
        self.abbrev = frozenset(GENERIC_ABBREV) | {a["text"].lower() for a in b.abbrev}
        removed = cut + [(s, e) for _, s, e in self.bodies]
        canon = self._main(removed + markers)
        marked = self._main(removed)
        starts = cuts(canon.text, self.abbrev)
        for entry in b.extra:
            i = canon.index_of_byte(entry["at"])
            if i is None:
                raise BoundariesError(f"extra boundary at {entry['at']} is not a character of the main stream")
            starts.add(i)
        for entry in b.suppress:
            i = canon.index_of_byte(entry["at"])
            if i is None or i not in starts:
                raise BoundariesError(f"suppress at {entry['at']} matches no sentence start")
            starts.discard(i)
        self.streams = [Stream("main", canon, marked, sentences("main", canon, starts))]
        for n, s, e in self.bodies:
            body = self._chars([(s + len(str(n)), e)])
            text = normalise(body)
            self.streams.append(Stream(f"fn{n}@{source.byte[s]}", text, text,
                                       sentences(f"fn{n}", text, cuts(text.text, self.abbrev))))
        self.markers = markers
        gone = _mask(len(source.text), removed + markers)
        kept = "".join(" " if gone[i] else c for i, c in enumerate(source.text))
        self.unpaired_runs = [source.byte[m.start()] for m in DIGIT_RUN.finditer(kept)]

    def _chars(self, ranges):
        t, by = self.source.text, self.source.byte
        return [(t[i], by[i], by[i + 1]) for a, z in ranges for i in range(a, z)]

    def _main(self, removed) -> Text:
        gone = _mask(len(self.source.text), removed)
        pages = []
        for a, z in self.source.pages:
            kept = [i for i in range(a, z) if not gone[i]]
            while kept and self.source.text[kept[-1]].isspace():
                kept.pop()
            pages.append(kept)
        items, t, by = [], self.source.text, self.source.byte
        for p, kept in enumerate(pages):
            if p and items:
                first = next((t[i] for i in kept if not t[i].isspace()), "")
                if items[-1][0] == "-" and len(items) > 1 and items[-2][0].isalpha() and first.islower():
                    items.pop()  # a word hyphenated across the page join
                else:
                    items.append((" ", by[self.source.pages[p][0]], by[self.source.pages[p][0]]))
            items.extend((t[i], by[i], by[i + 1]) for i in kept)
        return normalise(items)


def doc_source(case: Path) -> Path:
    """The pinned source path of a case, read (not run) from its build_document.DEFAULT_SOURCE assignment:
    `Path.home() / "<relative path>"`. Any other form is refused."""
    import ast
    tree = ast.parse((case / "build_document.py").read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and [getattr(t, "id", None) for t in node.targets] == ["DEFAULT_SOURCE"]:
            v = node.value
            if (isinstance(v, ast.BinOp) and isinstance(v.op, ast.Div) and isinstance(v.right, ast.Constant)
                    and isinstance(v.right.value, str) and ast.unparse(v.left) == "Path.home()"):
                return Path.home() / v.right.value
    raise BoundariesError(f"{case}/build_document.py: no DEFAULT_SOURCE = Path.home() / '...' assignment")
