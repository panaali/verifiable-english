"""L1a, L2, L3, L4 and D, the checks against the full source sentence (plan sections 3.2-3.6): a report, never a gate.

L1a (anchoring, the last L1 class): a linked block's quote outside every span linked to it, or a cue sentence of a
linked span that no block linked to it quotes; an unlinked block's quote that occurs more than once. L2 (legends of
the regulated predicates): L2b no quoted passage of MIN_QUOTE characters, L2q a passage that fails as an L1 n/u/c/e
quote would, L2a a passage in no span linked to a rule using the predicate. L3w: a logic word of the block's own words
(rule line less the VE template, acts, unquoted legend text) with no member of its class in the block's sentences.
L4 (cue-based coverage, per sentence): L4u an obligation-bearing sentence nothing covers, L4l one inside LABELLED
units, L4g (info) one covered by a legend quote only. D: a content word of the block's full sentences that neither the
block's text nor the unquoted legend of a name it uses accounts for and no sidecar entry covers, and every `loss`
entry. cues.json and logic_words.json are frozen data (plan 3.0), each pinned by sha256 in a test.
"""
from __future__ import annotations

import bisect
import hashlib
import json
import re
from dataclasses import dataclass, replace
from pathlib import Path

from tools.fidmech import segment as S
from tools.fidmech import textchecks as T

HERE = Path(__file__).resolve().parent
CUES, LOGIC_WORDS, RULED_OUT = HERE / "cues.json", HERE / "logic_words.json", "ruled_out.json"
CHECKS = ("L1", "L1a", "L2", "L3", "L4", "D")
CLASSES = {"L1": T.CLASSES, "L1a": ("L1a",), "L2": ("L2b", "L2q", "L2a"), "L3": ("L3w",), "L4": ("L4u", "L4l"),
           "D": ("D",)}
INFO_CLASSES = ("L4g",)
OBLIGATION_KINDS = ("norm", "hedged", "unformalised")
# The levers of the case files (plan 2b and Opus round 2 point 3), each rerun off beside the boundaries levers.
CASE_LEVERS = {"ruled_out": ("L4",), "unformalised": ("L4",), "sidecar": ("D",)}
RULED_OUT_KEYS = {"at", "sentence", "reason", "by"}


class DataError(S.BoundariesError):
    """A frozen data file (cues, logic words, ruled_out) or a case file that is malformed or does not fit."""


def _sha(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None


def _phrase(pattern: str) -> re.Pattern:
    """A word or phrase (a regex) on word boundaries, in any case, its spaces any whitespace."""
    return re.compile(r"(?<![\w-])(?:" + pattern.replace(" ", r"\s+") + r")(?![\w-])", re.I)


def _literal(text: str) -> re.Pattern:
    """A literal word or phrase on word boundaries, in any case, its spaces any whitespace."""
    return _phrase(" ".join(re.escape(t) for t in text.split()))


def _refusing(fn):
    """A loader whose malformed input (a node of the wrong type, a missing key, bad JSON) is a DataError by name."""
    import functools

    @functools.wraps(fn)
    def wrapped(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except S.BoundariesError:
            raise
        except (KeyError, TypeError, AttributeError, IndexError, ValueError, re.error) as e:
            raise DataError(f"{fn.__name__}: malformed input ({type(e).__name__}: {e})") from e
    return wrapped


def _strings_lists(value):
    if not isinstance(value, list) or not value:
        raise DataError("classes must be a non-empty list of lists")
    return value


def _strings(value, what) -> list[str]:
    if not isinstance(value, list) or not value or not all(isinstance(v, str) and v.strip() for v in value):
        raise DataError(f"{what} must be a non-empty list of strings")
    return value


# ---------------------------------------------------------------------------------------------------------------
# The frozen data files


@dataclass(frozen=True)
class Cues:
    modal: tuple
    first: re.Pattern
    adverb: re.Pattern
    not_verbs: frozenset
    past: str
    hedges: tuple
    min_words: int  # by a unit's kind alone, a sentence needs this many words (shorter: a heading or a label)

    def cue(self, text: str) -> str | None:
        """The cue that makes a sentence obligation-bearing, or None: a modal or commitment word; else "we" or the
        company followed by a present-tense verb, in a sentence with no hedge word."""
        for p in self.modal:
            m = p.search(text)
            if m:
                return m[0].lower()
        if any(h.search(text) for h in self.hedges):
            return None
        for m in self.first.finditer(text):
            verb = m[1]
            if (verb.islower() and verb not in self.not_verbs and not verb.endswith(self.past)
                    and not self.adverb.fullmatch(verb)):
                return re.sub(r"\s+", " ", m[0])
        return None


@_refusing
def load_cues(document: str, path: Path = CUES) -> Cues:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("schema") != "fidmech-cues/1":
        raise DataError(f"{path}: schema must be fidmech-cues/1")
    fp = data["first_person"]
    subjects = _strings(fp["subjects"], "subjects") + ([fp["companies"][document]] if document in fp["companies"]
                                                       else [])
    adverbs = "|".join(_strings(fp["adverbs"], "adverbs"))
    first = re.compile(r"(?<![\w-])(?:%s)\s+(?:(?:%s)\s+)?([A-Za-z]+)"
                       % ("|".join(re.escape(s) for s in subjects), adverbs), re.I)
    return Cues(tuple(_phrase(p) for p in _strings(data["modal"], "modal")), first,
                re.compile(adverbs, re.I), frozenset(_strings(fp["not_verbs"], "not_verbs")), fp["past_suffix"],
                tuple(_literal(h) for h in _strings(fp["hedges"], "hedges")),
                S._int(data["min_words_by_kind"], "min_words_by_kind"))


@dataclass(frozen=True)
class LogicWords:
    classes: tuple  # of tuples of (word, pattern)
    template: frozenset

    def members(self, text: str, cls) -> list[str]:
        return [w for w, p in cls if p.search(text)]


@_refusing
def load_logic_words(path: Path = LOGIC_WORDS) -> LogicWords:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("schema") != "fidmech-logic-words/1":
        raise DataError(f"{path}: schema must be fidmech-logic-words/1")
    classes = [_strings(c, "a logic-word class") for c in _strings_lists(data["classes"])]
    flat = [w for c in classes for w in c]
    if len(flat) != len(set(flat)) or set(flat) & set(data["out"]["quantifiers"] + data["out"]["no class"]):
        raise DataError(f"{path}: a word is in two classes, or in a class and out")
    return LogicWords(tuple(tuple((w, _literal(w)) for w in c) for c in classes),
                      frozenset(_strings(data["template"], "template")))


@_refusing
def load_ruled_out(path: Path, seg: S.Segmentation) -> tuple[dict, ...]:
    """ruled_out.json (plan 2c): a list, `[]` at first; each entry needs exactly at, sentence, reason and by, a
    reason and a `by`, and `at` must be the byte start of a sentence of the source whose first 60 characters (after
    norm()) are `sentence`. Anything else is refused: an entry outside the source never clears a hit."""
    if not Path(path).exists():
        return ()
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise DataError(f"{path}: ruled_out must be a list")
    starts = {s.start: s for st in seg.streams for s in st.sentences}
    seen = set()
    for entry in data:
        if not isinstance(entry, dict) or set(entry) != RULED_OUT_KEYS:
            raise DataError(f"{path}: an entry needs exactly {sorted(RULED_OUT_KEYS)}: {entry!r}")
        for key in ("reason", "by", "sentence"):
            if not isinstance(entry[key], str) or not entry[key].strip():
                raise DataError(f"{path}: an entry without a {key}: {entry!r}")
        at = entry["at"]
        if not isinstance(at, int) or isinstance(at, bool) or at not in starts:
            raise DataError(f"{path}: {at!r} is no sentence start in the source")
        if starts[at].text[:60] != entry["sentence"]:
            raise DataError(f"{path}: the sentence at {at} starts {starts[at].text[:60]!r}, not {entry['sentence']!r}")
        if at in seen:
            raise DataError(f"{path}: two entries at {at}")
        seen.add(at)
    return tuple(data)


# ---------------------------------------------------------------------------------------------------------------
# The case: spans, vocabulary, sidecar


@dataclass(frozen=True)
class Unit:
    id: str
    kind: str
    status: str
    reason: str
    rule: str | None
    start: int
    end: int
    open_terms: tuple = ()


@dataclass(frozen=True)
class CaseData:
    document: str
    units: tuple
    vocabulary: dict
    legend: dict  # accounting.legends: how a block's text uses each name
    sidecar: dict | None  # block id -> entries; None when the case has no sidecar
    ruled_out: tuple
    cues: Cues
    logic: LogicWords
    unformalised: bool = True  # the UNFORMALISED-coverage rule (a lever)

    def without(self, lever: str) -> "CaseData":
        if lever == "ruled_out":
            return replace(self, ruled_out=())
        if lever == "unformalised":
            return replace(self, unformalised=False)
        if lever == "sidecar":
            return replace(self, sidecar={} if self.sidecar is not None else None)
        raise ValueError(f"unknown lever {lever!r}")


@_refusing
def load_case(case: Path, seg: S.Segmentation, cues: Path = CUES, logic: Path = LOGIC_WORDS) -> CaseData:
    acc = S.accounting
    spans = json.loads((case / "spans.json").read_text(encoding="utf-8"))
    if spans["source_sha256"] != seg.source.sha256:
        raise DataError(f"{case.name}/spans.json is for source {spans['source_sha256'][:12]}, not {seg.source.sha256[:12]}")
    if not isinstance(spans["units"], list) or not spans["units"]:
        raise DataError(f"{case.name}/spans.json: units must be a non-empty list")
    units = []
    for u in spans["units"]:
        a, b = u["span"]
        if not (all(isinstance(u[k], str) for k in ("id", "kind", "status"))
                and all(isinstance(x, int) and not isinstance(x, bool) for x in (a, b)) and 0 <= a <= b
                and isinstance(u.get("rule"), (str, type(None))) and isinstance(u.get("reason", ""), str)
                and isinstance(u.get("open_terms", []), list)):
            raise DataError(f"{case.name}/spans.json: a malformed unit {u!r:.120}")
        units.append(Unit(u["id"], u["kind"], u["status"], u.get("reason") or "", u.get("rule"), a, b,
                          tuple(u.get("open_terms") or ())))
    units = tuple(units)
    env = json.loads((case / "environment.d1.json").read_text(encoding="utf-8"))
    if not isinstance(env["vocabulary"]["predicates"], dict):
        raise DataError(f"{case.name}/environment.d1.json: vocabulary.predicates must be an object")
    sidecar = None
    if (case / acc.SIDECAR).exists():
        sidecar = {}
        for number, block_id, entries, problem in acc.read_sidecar(case / acc.SIDECAR):
            if problem:
                raise DataError(f"{case.name}/{acc.SIDECAR}: {problem}")
            sidecar[block_id] = entries
    return CaseData(case.name, units, env["vocabulary"], acc.legends(env), sidecar,
                    load_ruled_out(case / "fidmech" / RULED_OUT, seg), load_cues(case.name, cues),
                    load_logic_words(logic))


def overlaps(stream: S.Stream, i0: int, i1: int, a: int, b: int) -> bool:
    """Whether a character of stream.canon[i0:i1] comes from a source byte in [a, b)."""
    k = bisect.bisect_left(stream.canon.starts, a, i0, i1)
    return k < i1 and stream.canon.starts[k] < b


def _sentence(seg: S.Segmentation, stream: str, i: int) -> tuple[S.Stream, S.Sentence]:
    st = next(s for s in seg.streams if s.name == stream)
    return st, st.sentences[i]


def _units_of(seg, data, stream, i):
    st, s = _sentence(seg, stream, i)
    return [u for u in data.units if overlaps(st, s.i0, s.i1, u.start, u.end)]


def _unquoted(text: str) -> str:
    """A legend's text with its quoted source passages left out (plan 3.4 and 3.6)."""
    found, _ = T.header_quotes(text)
    out, at = [], 0
    for q in found:
        out.append(text[at:max(q.at - 1, at)])
        at = q.at + len(q.text) + 1
    return " ".join(out + [text[at:]])


def own_legend(entry: dict) -> str:
    """The unquoted legend of a vocabulary entry: description less its quoted passages, verbalisation, act."""
    parts = [_unquoted(str(entry.get("description", ""))), str(entry.get("verbalisation", "")),
             str((entry.get("regulated") or {}).get("act", ""))]
    return S.accounting.PLACEHOLDER.sub(" ", " ".join(parts))


def _entry(data: CaseData, name: str) -> dict:
    v = data.vocabulary
    return v.get("predicates", {}).get(name) or (v.get("constants") or {}).get(name) or {}


# ---------------------------------------------------------------------------------------------------------------
# The checks


def _hit(cls, block, file, quote, detail, at=None):
    return T.Hit(cls, block, file, quote, detail, at)


def l1a(seg, blocks, analyses, data) -> list[T.Hit]:
    """L1a: anchoring (plan 3.2), only on quotes with no earlier L1 class."""
    linked = {}
    for u in data.units:
        if u.rule:
            linked.setdefault(u.rule, []).append(u)
    quoted = {}  # block id -> the (stream, sentence) its quotes' placements touch
    for b in blocks:
        quoted[b["id"]] = {(loc.place.stream, i) for loc in analyses[b["id"]][2] if loc.place
                           for i in loc.place.sentences}
    hits = []
    for b in blocks:
        for loc in analyses[b["id"]][2]:
            if loc.cls or not loc.place:
                continue
            p = loc.place
            st = next(s for s in seg.streams if s.name == p.stream)
            at = (p.stream, p.start, p.end)
            if b["id"] in linked:
                if not any(overlaps(st, p.i0, p.i1, u.start, u.end) for u in linked[b["id"]]):
                    hits.append(_hit("L1a", b["id"], b["file"], loc.quote.text,
                                     "the located sentence lies outside every span linked to the block", at))
            else:
                places = {(q.start, q.end) for q in T._placements(seg, [f.strip() for f in
                                                                        T.ELLIPSIS.split(loc.text) if f.strip()])}
                if len(places) > 1:
                    hits.append(_hit("L1a", b["id"], b["file"], loc.quote.text,
                                     f"an unlinked block's quote that occurs {len(places)} times in the source", at))
    by_id = {b["id"]: b for b in blocks}
    for rule, units in sorted(linked.items()):
        if rule not in by_id:
            continue
        for st in seg.streams:
            for s in st.sentences:
                if not any(overlaps(st, s.i0, s.i1, u.start, u.end) for u in units):
                    continue
                if (st.name, s.index) in quoted[rule] or not data.cues.cue(s.text):
                    continue
                hits.append(_hit("L1a", rule, by_id[rule]["file"], None,
                                 f"a cue sentence of a linked span ({data.cues.cue(s.text)!r}) that no block linked "
                                 f"to it quotes: {s.text[:80]!r}", (st.name, s.start, s.end)))
    return hits


def legends(seg, data) -> dict:
    """Per regulated predicate: its checked passages (MIN_QUOTE characters or more, not in a note) as Located."""
    out = {}
    for name, entry in data.vocabulary.get("predicates", {}).items():
        if "regulated" not in entry:
            continue
        found, _ = T.header_quotes(str(entry.get("description", "")))
        rows, _ = T.checkable(found)
        rows = [r for r in rows if len(S.norm(r[0].text).strip()) >= S.accounting.MIN_QUOTE]
        out[name] = [loc for loc, _ in T.classify(seg, rows)] if rows else []
    return out


def users(blocks, data) -> dict:
    """name -> the ids of the blocks whose text uses it (accounting.used_names)."""
    out = {}
    for b in blocks:
        for name in S.accounting.used_names(b["text"], data.legend):
            out.setdefault(name, []).append(b["id"])
    return out


def l2(seg, blocks, data, legend_locs, used) -> tuple[list[T.Hit], dict]:
    linked = {}
    for u in data.units:
        if u.rule:
            linked.setdefault(u.rule, []).append(u)
    file = "environment.d1.json"
    hits, unlinked = [], 0
    for name, locs in legend_locs.items():
        if not locs:
            notes = sum(q.note and len(S.norm(q.text).strip()) >= S.accounting.MIN_QUOTE
                        for q in T.header_quotes(str(data.vocabulary["predicates"][name].get("description", "")))[0])
            hits.append(_hit("L2b", name, file, None, f"no quoted passage of {S.accounting.MIN_QUOTE} characters"
                             + (f" outside brackets ({notes} inside, read as translator's notes)" if notes else "")))
            continue
        spans = [u for b in used.get(name, []) for u in linked.get(b, [])]
        for loc in locs:
            p = loc.place
            at = (p.stream, p.start, p.end) if p else None
            if loc.cls:
                hits.append(_hit("L2q", name, file, loc.quote.text, f"fails as an {loc.cls} quote would", at))
            elif not spans:
                unlinked += 1
            else:
                st = next(s for s in seg.streams if s.name == p.stream)
                if not any(overlaps(st, p.i0, p.i1, u.start, u.end) for u in spans):
                    hits.append(_hit("L2a", name, file, loc.quote.text,
                                     "the passage lies in no span linked to a rule that uses the predicate", at))
    base = [n for n, e in data.vocabulary.get("predicates", {}).items() if "regulated" not in e]
    bare = sum(1 for n in base if not [q for q in T.header_quotes(str(data.vocabulary["predicates"][n]
                                                                        .get("description", "")))[0]
                                        if not q.note and len(S.norm(q.text).strip()) >= S.accounting.MIN_QUOTE])
    open_terms = {t for u in data.units for t in u.open_terms}
    return hits, {"regulated": len(legend_locs), "passages_unlinked": unlinked,
                  "not_checked": {"base_predicates": len(base), "base_bare": bare, "open_terms": len(open_terms)}}


def own_words(block: dict, data: CaseData, used) -> list[tuple[str, str]]:
    """L3's own words of a rule block: (where, text) for the rule line less the VE template (quoted constants, the
    rule number and the template words of logic_words.json), each used predicate's act and each used name's
    unquoted legend."""
    line = re.sub(r'"[^"]*"', " ", block["text"])
    line = re.sub(r"^Rule \d+\.", " ", line)
    line = " ".join(w for w in re.split(r"(\s+)", line) if w.strip().lower().strip(",.;:") not in data.logic.template)
    out = [("rule line", line)]
    for name in used:
        entry = _entry(data, name)
        act = str((entry.get("regulated") or {}).get("act", ""))
        if act:
            out.append((f"act of {name}", S.accounting.PLACEHOLDER.sub(" ", act)))
        out.append((f"legend of {name}", own_legend(entry)))
    return out


@dataclass(frozen=True)
class BlockSource:
    """A rule block's source for L3 and D (plan 3.4, 3.6): the full sentences its located quotes touch, plus the
    text of every quote L1 located no sentence for (plan 3.4: "the header quote is used and the hit is marked"),
    quote by quote, so a block with some quotes located still keeps the text of the others."""
    text: str
    sentences: int
    unlocated: int
    quotes: int

    @property
    def fallback(self) -> str:
        """'all', 'part' or '' : how much of the source is header-quote text L1 located no sentence for."""
        return "" if not self.unlocated else "all" if not self.sentences else "part"

    def where(self) -> str:
        """L3's name for the source (every L3w detail ends with it)."""
        return {"": "full source sentences", "all": "header quote (L1 located no sentence)",
                "part": f"full source sentences and the header quote L1 located no sentence for "
                        f"({self.unlocated} of {self.quotes} quotes)"}[self.fallback]

    def mark(self) -> str:
        """D's mark on each unaccounted word of the block (empty when every quote is located)."""
        return {"": "", "all": " (from the header quote: L1 located no sentence)",
                "part": f" (from the full sentences and the header quote L1 located no sentence for: "
                        f"{self.unlocated} of {self.quotes} quotes)"}[self.fallback]


def block_sentences(seg, locs) -> BlockSource:
    """The full sentences the block's located quotes touch, plus the text of each quote that is not located."""
    touched = sorted({(loc.place.stream, i) for loc in locs if loc.place for i in loc.place.sentences})
    loose = [loc.text for loc in locs if not loc.place]
    text = " ".join([_sentence(seg, st, i)[1].text for st, i in touched] + loose)
    return BlockSource(text, len(touched), len(loose), len(locs))


def fallback_counts(sources) -> dict:
    """How many blocks read every quote, or some quotes, from the header quote because L1 located no sentence."""
    return {"from_header_quote": sum(s.fallback == "all" for s in sources),
            "partly_from_header_quote": sum(s.fallback == "part" for s in sources)}


def l3(seg, blocks, analyses, data) -> tuple[list[T.Hit], dict]:
    hits, skipped, sources = [], 0, []
    for b in blocks:
        if b["file"] != "rules.d1.ve":
            continue
        locs = analyses[b["id"]][2]
        if not locs:
            skipped += 1
            continue
        src = block_sentences(seg, locs)
        sources.append(src)
        own = own_words(b, data, S.accounting.used_names(b["text"], data.legend))
        for cls in data.logic.classes:
            if data.logic.members(src.text, cls):
                continue
            where = [(w, place) for place, text in own for w in data.logic.members(text, cls)]
            if where:
                words = sorted({w for w, _ in where})
                hits.append(_hit("L3w", b["id"], b["file"], "/".join(words),
                                 f"{', '.join(words)} in {', '.join(sorted({p for _, p in where}))}; no member of "
                                 f"{{{', '.join(w for w, _ in cls)}}} in the " + src.where()))
    return hits, {"rule_blocks_without_quote": skipped, **fallback_counts(sources)}


def l4(seg, blocks, analyses, data, legend_locs, used) -> tuple[list[T.Hit], dict]:
    quoted = {(loc.place.stream, i) for b in blocks for loc in analyses[b["id"]][2] if loc.place
              for i in loc.place.sentences}
    by_legend = {(loc.place.stream, i) for name, locs in legend_locs.items() if used.get(name)
                 for loc in locs if loc.place for i in loc.place.sentences}
    ruled = {e["at"] for e in data.ruled_out}
    hits, bearing, by_cue = [], 0, 0
    for st in seg.streams:
        for s in st.sentences:
            units = [u for u in data.units if overlaps(st, s.i0, s.i1, u.start, u.end)]
            cue = data.cues.cue(s.text)
            by_kind = [u.id for u in units if u.kind in OBLIGATION_KINDS
                       and len(re.findall(r"[A-Za-z]+", s.text)) >= data.cues.min_words]
            if not (by_kind or cue):
                continue
            bearing += 1
            by_cue += cue is not None
            key = (st.name, s.index)
            if key in quoted or s.start in ruled:
                continue
            if data.unformalised and any(u.status == "UNFORMALISED" and u.reason for u in units):
                continue
            why = f"cue {cue!r}" if cue else f"unit {by_kind[0]}"
            block = f"{st.name}@{s.start}"
            at = (st.name, s.start, s.end)
            if key in by_legend:
                hits.append(_hit("L4g", block, "", s.text[:60], f"covered by a legend quote only ({why})", at))
            elif units and all(u.status == "LABELLED" for u in units):
                hits.append(_hit("L4l", block, "", s.text[:60], f"uncovered, in LABELLED units "
                                 f"{', '.join(u.id + ' (' + u.kind + ')' for u in units)} ({why})", at))
            else:
                hits.append(_hit("L4u", block, "", s.text[:60], f"uncovered ({why})", at))
    return hits, {"sentences": sum(len(st.sentences) for st in seg.streams), "obligation_bearing": bearing,
                  "by_cue": by_cue, "ruled_out": len(data.ruled_out)}


def d(seg, blocks, analyses, data) -> tuple[list[T.Hit], dict]:
    """D --span sentence (plan 3.6, Opus round 2 point 3): per block (i) the unaccounted words of its full sentences,
    (ii) those outside its header quotes; a hit per unaccounted word no sidecar entry covers, and per loss entry."""
    acc = S.accounting
    hits, rows, sources = [], [], []
    for b in blocks:
        locs = analyses[b["id"]][2]
        if not locs:
            continue
        src = block_sentences(seg, locs)
        sources.append(src)
        used = acc.used_names(b["text"], data.legend)
        accounted = acc.words(b["text"]).union(*(acc.words(own_legend(_entry(data, n))) for n in used))
        unaccounted = sorted(acc.words(src.text) - accounted)
        outside = sorted(set(unaccounted) - acc.words(" ".join(loc.text for loc in locs)))
        entries = (data.sidecar or {}).get(b["id"]) or []
        covered = set().union(*(acc.words(e["words"]) for e in entries)) if entries else set()
        mark = src.mark()
        for w in unaccounted:
            if w not in covered:
                hits.append(_hit("D", b["id"], b["file"], w, "unaccounted, in no sidecar entry"
                                 + (", outside the header quote" if w in outside else "") + mark))
        for e in entries:
            if e["reason"] == "loss":
                hits.append(_hit("D", b["id"], b["file"], f"loss {e['arg']}: {e['words']}",
                                 "a loss entry: the translator says the rule does not carry these words"))
        rows.append({"block": b["id"], "unaccounted": len(unaccounted), "outside_quote": len(outside)})
    return hits, {"sidecar": data.sidecar is not None, "span": "sentence", **fallback_counts(sources),
                  "unaccounted": sum(r["unaccounted"] for r in rows),
                  "outside_quote": sum(r["outside_quote"] for r in rows), "per_block": rows}


def run(seg: S.Segmentation, blocks, data: CaseData | None, checks) -> tuple[list[T.Hit], dict]:
    """Every requested check on one segmentation: (hits of the requested classes and L4g, info per check)."""
    analyses = {b["id"]: T.analyse(seg, b) for b in blocks}
    hits, info = [], {}
    q = {"note": 0, "empty": 0, "checked": 0}
    for b in blocks:
        for k in q:
            q[k] += analyses[b["id"]][1][k]
    info["quotes"] = q
    if "L1" in checks:
        hits += [h for b in blocks for h in analyses[b["id"]][0]]
    if not set(checks) - {"L1"}:
        return hits, info
    if "L1a" in checks:
        hits += l1a(seg, blocks, analyses, data)
        linked = {u.rule for u in data.units if u.rule}
        info["L1a"] = {"linked_blocks": sum(b["id"] in linked for b in blocks),
                       "unlinked_blocks": sum(b["id"] not in linked for b in blocks)}
    legend_locs = legends(seg, data) if {"L2", "L4"} & set(checks) else {}
    used = users(blocks, data)
    if "L2" in checks:
        h, info["L2"] = l2(seg, blocks, data, legend_locs, used)
        hits += h
    if "L3" in checks:
        h, info["L3"] = l3(seg, blocks, analyses, data)
        hits += h
    if "L4" in checks:
        h, info["L4"] = l4(seg, blocks, analyses, data, legend_locs, used)
        hits += h
    if "D" in checks:
        h, info["D"] = d(seg, blocks, analyses, data)
        hits += h
    return hits, info


def counts(hits, checks) -> dict:
    classes = [c for check in CHECKS if check in checks for c in CLASSES[check]]
    out = {c: sum(h.cls == c for h in hits) for c in classes}
    if "L4" in checks:
        out["L4g"] = sum(h.cls == "L4g" for h in hits)
    return out


def report(case: Path, data: bytes, boundaries_path: Path, checks=("L1",), cues: Path = CUES,
           logic: Path = LOGIC_WORDS) -> dict:
    """The report of one case: hits per class, raw and with each lever off, and what each lever clears or adds."""
    checks = [c for c in CHECKS if c in checks]
    source = S.Source(data)
    b = S.load_boundaries(boundaries_path)
    blocks = T.read_blocks(case)
    seg = S.Segmentation(source, b)
    cdata = load_case(case, seg, cues, logic) if set(checks) - {"L1"} else None
    hits, info = run(seg, blocks, cdata, checks)
    keys = {h.key() for h in hits}

    def lever_row(off):
        off_keys = {h.key() for h in off}
        return {"counts": counts(off, checks), "cleared": sorted(map(list, off_keys - keys), key=str),
                "added": sorted(map(list, keys - off_keys), key=str)}

    levers = {}
    for lever in S.LEVERS:
        try:
            levers[lever] = lever_row(run(S.Segmentation(source, b.without(lever, source)), blocks, cdata, checks)[0])
        except S.BoundariesError as e:
            levers[lever] = {"error": str(e)}
    for lever, needs in CASE_LEVERS.items():
        if set(needs) & set(checks):
            levers[lever] = lever_row(run(seg, blocks, cdata.without(lever), checks)[0])
    gated = T.ALSO_GATED.get(case.name, {}) if "L1" in checks else {}
    out = {"document": case.name, "checks": checks, "source_sha256": source.sha256,
           "boundaries_sha256": hashlib.sha256(Path(boundaries_path).read_bytes()).hexdigest(),
           "blocks": len(blocks), "quotes": info.pop("quotes"), "counts": counts(hits, checks),
           "also_gated": {c: {"by": gated[c], "hits": sum(h.cls == c for h in hits)} for c in gated},
           "sentences": {"main": len(seg.streams[0].sentences),
                         "footnote": sum(len(s.sentences) for s in seg.streams[1:])},
           "footnote_pairs": {"generator": sum(f["by"] == "generator" for f in b.footnotes),
                              "hand": sum(f["by"] == "hand" for f in b.footnotes)},
           "unpaired_digit_runs": len(seg.unpaired_runs),
           "hits": [h.to_dict() for h in hits], "levers": levers}
    if cdata is not None:
        out["info"] = info
        out["data_sha256"] = {"cues.json": _sha(Path(cues)), "logic_words.json": _sha(Path(logic)),
                              RULED_OUT: _sha(case / "fidmech" / RULED_OUT),
                              S.accounting.SIDECAR: _sha(case / S.accounting.SIDECAR)}
    return out
