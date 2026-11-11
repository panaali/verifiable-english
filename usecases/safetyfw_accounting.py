"""Source accounting: each block of a translated case says what it leaves out of its quoted source, and why.

Stdlib only; shared by the safety-framework-style cases (anthropic-rsp, openai-preparedness). For each block of
`rules.d1.ve` and then `facts.d1.ve` (a header line `## <id> | <when> | [RS0|independent |] <source>` and one line
of VE English, the format of each case's `read_blocks`), the tool takes the double-quoted text of the header's source
field (outermost quotes; a quote inside a quote stays in it, `scan_quotes`), widens each quote over its elisions to the span of the pinned source text (`--source`), and lists the content
words of that span that are neither in the block's VE text nor in the legend of a predicate or constant the block
uses: the UNACCOUNTED words. The sidecar `accounting.d1.txt` has one line per block, `<id> | omits: nothing` or
`<id> | omits: "<source words>" <reason> ; ...`; `--check` passes only when every unaccounted word is in some entry
of its block's line, every entry says only what the span says, and every reason's argument resolves. A `loss` entry
is the translator's statement that the rule does not carry those words: it is a finding, not a failure.

The method is the architect's experiment (fable-team/architect/experiments/source-accounting/account.py); the stop
list and the stemmer are copied from it unchanged and pinned by hash in tests/test_safetyfw_accounting.py, because a
change to either changes every case's result.

usage: safetyfw_accounting.py <case dir or name> [--source FILE] [--check] [--report FILE] [--score VERDICTS.md]
"""
from __future__ import annotations

import argparse
import bisect
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

STOP = frozenset("""a an the and or nor of to in on at by for from with without within as is are was were be been being it its
this that these those we our us will shall would should must may might can could if then than so such any all each every both
either neither not no only also which who whom whose what when where while whether into onto over under above below about
against between through during before after per via have has had do does did their they them he she his her you your i there
here other others more most less least own same e g i.e eg ie etc see section row column table bullet step item following
above-mentioned one two three first second third""".split())
SUFFIXES = ("ations", "ation", "ments", "ment", "ities", "ity", "ings", "ing", "ies", "ied", "ed", "es", "ly", "s")
STEM_MIN = 4

# translation-fidelity-checklist.md (manage-agents/prompts, DRI 2026-10-29): the failure classes a `loss` names.
LOSS_CLASSES = {1: "dropped conjunct or clause", 2: "quantifier scope", 3: "exclusive only and closed lists",
                4: "one predicate reused across bullets or regimes", 5: "modal strength",
                6: "obligation turned into method", 7: "invented guards and exclusions",
                8: "case facts fixing open terms", 9: "readings that manufacture conflicts", 10: "key cells",
                11: "elided quotes"}
REASONS = ("restates", "exposition", "rule", "open", "reading", "loss")
ELISION = re.compile(r"\.\.\.|\u2026")
WINDOW = 2500
MIN_QUOTE = 12
DECIDER = re.compile(r"\bdecided by\b|\bdecides\b")
SIDECAR = "accounting.d1.txt"
BLOCK_FILES = ("rules.d1.ve", "facts.d1.ve")


def table_digest(table) -> str:
    """The SHA-256 a test pins for the stop list (sorted) and the stemmer (suffixes in order, then the minimum)."""
    return hashlib.sha256("\n".join(table).encode()).hexdigest()


def stem(word: str) -> str:
    for suffix in SUFFIXES:
        if word.endswith(suffix) and len(word) - len(suffix) >= STEM_MIN:
            return word[: -len(suffix)]
    return word


def words(text: str) -> set[str]:
    """Content words: lower case, letters and digits, hyphenated parts apart, stop words out, suffixes stemmed."""
    out = set()
    for token in re.findall(r"[A-Za-z][A-Za-z\-']*|\d+", text.lower().replace("_", " ")):
        for part in token.split("-"):
            part = part.strip("'")
            if part.isdigit():
                out.add(part)
            elif len(part) > 2 and part not in STOP:
                out.add(stem(part))
    return out


def norm(text: str) -> str:
    """Curly quotes, dashes, the ellipsis sign and the PDF ligatures made plain; whitespace collapsed."""
    for a, b in (("“", '"'), ("”", '"'), ("’", "'"), ("‘", "'"), ("—", "-"),
                 ("–", "-"), ("…", "..."), ("ﬀ", "ff"), ("ﬁ", "fi"), ("ﬂ", "fl"),
                 ("ﬃ", "ffi"), ("ﬄ", "ffl")):
        text = text.replace(a, b)
    return re.sub(r"\s+", " ", text)


class AccountingError(Exception):
    """The case's files cannot be read in the block format (a malformed header, an odd line count)."""


# ---------------------------------------------------------------------------------------------------------------
# Reading a case


def read_blocks(path: Path):
    """The two-line blocks of one file, as dicts: id, when (set ids), source field, VE text."""
    lines = path.read_text(encoding="utf-8").splitlines()
    if len(lines) % 2:
        raise AccountingError(f"{path.name}: a header line without its block")
    out = []
    for header, text in zip(lines[::2], lines[1::2]):
        fields = header[3:].split(" | ") if header.startswith("## ") else []
        # The RSP's reader has a narrowing field (RS0 or independent) third; Preparedness's has none.
        fixed = 3 if len(fields) >= 4 and fields[2] in ("RS0", "independent") else 2
        if len(fields) <= fixed or not re.fullmatch(r"[a-z0-9-]+", fields[0]) or text.startswith("## "):
            raise AccountingError(f"{path.name}: malformed header {header!r}")
        when = fields[1].strip()
        sets = () if when == "always" else tuple(part.split("=")[0].strip() for part in when.split("&"))
        out.append({"id": fields[0], "file": path.name, "sets": sets, "source": " | ".join(fields[fixed:]),
                    "text": text})
    return out


PLACEHOLDER = re.compile(r"\{\d+\}")


def legends(environment: dict):
    """Each predicate's legend (description, verbalisation, regulated act) and how a block's text uses it.

    The act is matched with "{0} " removed and every other placeholder standing for a non-empty phrase of the
    text ("have the plans of the company about {1} in place" occurs in "... about each threshold in place")."""
    vocabulary = environment["vocabulary"]
    out = {}
    for name, entry in vocabulary.get("predicates", {}).items():
        act = str((entry.get("regulated") or {}).get("act", ""))
        verbalisation = str(entry.get("verbalisation", ""))
        bare = act.replace("{0} ", "").strip()
        out[name] = {"kind": "predicate", "description": str(entry.get("description", "")),
                     "legend": words(PLACEHOLDER.sub(" ", " ".join((str(entry.get("description", "")),
                                                                   verbalisation, act)))),
                     "act": re.compile(".+?".join(map(re.escape, PLACEHOLDER.split(bare)))) if bare else None,
                     "verb": re.sub(r"\s+", " ", PLACEHOLDER.sub("", verbalisation)).strip()}
    for name, entry in (vocabulary.get("constants") or {}).items():
        out[name] = {"kind": "constant", "description": str(entry.get("description", "")),
                     "legend": words(str(entry.get("description", ""))), "act": None, "verb": ""}
    return out


def used_names(text: str, legend: dict):
    quoted = set(re.findall(r'"([a-z0-9_]+)"', text))
    return sorted(name for name, entry in legend.items()
                  if name in quoted or (entry["kind"] == "predicate" and (
                      (entry["act"] is not None and entry["act"].search(text))
                      or (len(entry["verb"]) > 8 and entry["verb"] in text))))


def plan_tables(plan: Path):
    """The reading-set ids of PLAN 3.1's table and the item numbers of PLAN section 12."""
    if not plan.exists():
        return set(), set()
    sets, limits, section = set(), set(), None
    for line in plan.read_text(encoding="utf-8").splitlines():
        if line.startswith("#"):
            section = "3.1" if line.startswith("### 3.1 ") else "12" if line.startswith("## 12. ") else (
                section if section == "12" and line.startswith("### ") else None)
            continue
        if section == "3.1":
            match = re.match(r"\| ([A-Z][A-Za-z0-9]*) \|", line)
            if match and match[1] != "Id":
                sets.add(match[1])
        elif section == "12":
            match = re.match(r"(\d+)\. ", line)
            if match:
                limits.add(int(match[1]))
    return sets, limits


# ---------------------------------------------------------------------------------------------------------------
# Spans


# Layout the pinned extracted texts interleave with the prose (their extractors keep pypdf's page furniture in
# place): a footnote marker of one or two digits, or a page footer. A match may skip these between two words of a
# quote; the skipped tokens are cut out of the span. Patterns are over the lower-case token string.
FURNITURE = (r"\d{1,2}", r"responsible scaling policy anthropic \d{1,2}")
_GAP = "(?:(?:%s) )?" % "|".join(FURNITURE)


class Source:
    """A pinned source text, normalised, with its tokens (lower-case runs of letters and digits) for matching."""

    def __init__(self, text: str):
        self.text = norm(text)
        self.spans = [m.span() for m in re.finditer(r"[a-z0-9]+", self.text.lower())]
        self.joined, self.offsets, at = [], [], 0
        for start, end in self.spans:
            self.offsets.append(at)
            self.joined.append(self.text[start:end].lower())
            at += end - start + 1
        self.joined = " ".join(self.joined) + " "

    def pattern(self, fragment: str):
        tokens = re.findall(r"[a-z0-9]+", norm(fragment).lower())
        # A word of the quote may stand in the source split by a line-end hyphen ("con- trols").
        return re.compile("".join("(" + "(?: )?".join(map(re.escape, t)) + ") " + (_GAP if i < len(tokens) - 1 else "")
                                  for i, t in enumerate(tokens))) if tokens else None

    def token(self, joined_at: int) -> int:
        return bisect.bisect_right(self.offsets, joined_at) - 1

    def anchor(self, quote: str):
        """The source span from the quote's first fragment to its last, or None when they are not found in order.

        Fragments are the pieces between elisions; each next fragment must start within WINDOW characters after the
        end of the previous one. Every occurrence of the first fragment is tried. Footnote markers and page footers
        skipped inside a fragment are cut out of the span."""
        patterns = [self.pattern(f) for f in ELISION.split(norm(quote))]
        patterns = [p for p in patterns if p is not None]
        if not patterns:
            return None
        at = 0
        while True:
            first = patterns[0].search(self.joined, at)
            if first is None:
                return None
            matches = [first]
            for pattern in patterns[1:]:
                end = self.spans[self.token(matches[-1].end(len(matches[-1].groups())) - 1)][1]
                match = pattern.search(self.joined, matches[-1].end())
                if match is None or self.spans[self.token(match.start())][0] - end > WINDOW:
                    break
                matches.append(match)
            else:
                return self._span(matches)
            at = self.offsets[self.token(first.start()) + 1] if self.token(first.start()) + 1 < len(
                self.offsets) else len(self.joined)

    def _span(self, matches):
        first, last = self.token(matches[0].start()), self.token(matches[-1].end(len(matches[-1].groups())) - 1)
        words_of = [range(self.token(m.start(g)), self.token(m.end(g) - 1) + 1)
                    for m in matches for g in range(1, len(m.groups()) + 1)]
        quoted = {i for word in words_of for i in word}
        joined = {i for word in words_of for i in word[:-1]}  # a hyphen-split word of the quote, rejoined
        cut = {i for m in matches for i in range(self.token(m.start()), self.token(m.end() - 1) + 1)} - quoted
        kept = [i for i in range(first, last + 1) if i not in cut]
        out = self.text[self.spans[kept[0]][0]:self.spans[kept[0]][1]]
        for i, j in zip(kept, kept[1:]):
            gap = "" if i in joined else " " if j > i + 1 else self.text[self.spans[i][1]:self.spans[j][0]]
            out += gap + self.text[self.spans[j][0]:self.spans[j][1]]
        return out


# The double quote marks of a source field: the curly ones open or close by direction, the straight one does
# whichever its position needs (it closes a straight quote that is open innermost, else it opens one). Single marks
# are never paired: the sources use ’ and ' as apostrophes too.
OPENS, CLOSES, STRAIGHT = "“", "”", '"'


def scan_quotes(source_field: str):
    """(the outermost quotes of a source field, normalised and at least MIN_QUOTE long; a problem or None).

    Quotes nest: “… the ability to “filibuster”” is one quote with the inner one inside it, never a quote cut at the
    inner mark. A mark without its partner (a closing mark with nothing open, a curly closing mark while a straight
    quote is open innermost, a quote still open at the end) is a problem, not text silently left out."""
    out, stack, start = [], [], 0
    for at, mark in ((m.start(), m[0]) for m in re.finditer("[%s%s%s]" % (OPENS, CLOSES, STRAIGHT), source_field)):
        if mark == CLOSES or (mark == STRAIGHT and stack and stack[-1] == STRAIGHT):
            if not stack or stack[-1] != (OPENS if mark == CLOSES else STRAIGHT):
                return out, f"unpaired closing quote mark at character {at}"
            stack.pop()
            if not stack:
                quote = norm(source_field[start:at])
                if len(quote) >= MIN_QUOTE:
                    out.append(quote)
        else:
            if not stack:
                start = at + 1
            stack.append(mark)
    if stack:
        return out, f"unclosed quote mark at character {start - 1}"
    return out, None


def quotes(source_field: str):
    """The outermost quotes of a source field (see scan_quotes)."""
    return scan_quotes(source_field)[0]


# ---------------------------------------------------------------------------------------------------------------
# The sidecar

ENTRY = re.compile(r'"([^"]+)" (restates|exposition|rule [a-z0-9-]+|open [a-z0-9_]+|reading [A-Za-z0-9]+|'
                   r'loss (?:limit \d+|\d+))(?: ; |$)')


def read_sidecar(path: Path):
    """[(line number, block id, entries or None, problem or None)]; entries are dicts words, reason, arg."""
    out = []
    if not path.exists():
        return out
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        match = re.fullmatch(r"([a-z0-9-]+) \| omits: (.+)", line)
        if match is None:
            out.append((number, None, None, f"line {number}: not '<block id> | omits: ...': {line[:80]!r}"))
            continue
        body = match[2]
        if body == "nothing":
            out.append((number, match[1], [], None))
            continue
        entries, at = [], 0
        while at < len(body):
            entry = ENTRY.match(body, at)
            if entry is None:
                break
            reason, _, arg = entry[2].partition(" ")
            entries.append({"words": entry[1], "reason": reason, "arg": arg})
            at = entry.end()
        if at != len(body) or not entries:
            out.append((number, match[1], None, f"line {number}: unreadable entry at {body[at:at + 60]!r}"))
        else:
            out.append((number, match[1], entries, None))
    return out


# ---------------------------------------------------------------------------------------------------------------
# The accounting


def case_dir(name: str) -> Path:
    path = Path(name)
    return path if path.is_dir() else HERE / name


def account(case: Path, source_text: str | None = None, sidecar: Path | None = None):
    """The full accounting of a case: a dict with blocks, totals and problems (the --report JSON)."""
    blocks = [b for name in BLOCK_FILES if (case / name).exists() for b in read_blocks(case / name)]
    legend = legends(json.loads((case / "environment.d1.json").read_text(encoding="utf-8")))
    reading_sets, limits = plan_tables(case / "PLAN.md")
    source = Source(source_text) if source_text is not None else None
    problems = []
    by_id = {}
    for block in blocks:
        if block["id"] in by_id:
            problems.append(f"{block['id']}: two blocks have this id")
        by_id[block["id"]] = block
        used = used_names(block["text"], legend)
        block["used"] = used
        block["accounted"] = words(block["text"]).union(*(legend[name]["legend"] for name in used))
        spans, block["unanchored"], block["elided"] = [], [], []
        block["quotes"], unpaired = scan_quotes(block["source"])
        if unpaired:
            problems.append(f"{block['id']}: UNPAIRED quote marks in the source field: {unpaired}")
        for quote in block["quotes"]:
            if source is None:
                if ELISION.search(quote):
                    block["elided"].append(quote)
                spans.append(quote)
                continue
            span = source.anchor(quote)
            if span is None:
                block["unanchored"].append(quote)
                problems.append(f"{block['id']}: UNANCHORED quote {quote[:70]!r}")
                spans.append(quote)
            else:
                spans.append(span)
        block["span"] = " ".join(spans)
        block["span_words"] = words(block["span"])
        block["unaccounted"] = sorted(block["span_words"] - block["accounted"])

    lines = read_sidecar(sidecar if sidecar is not None else case / SIDECAR)
    if not lines:
        problems.append(f"{SIDECAR}: missing or empty")
    order = [b["id"] for b in blocks]
    seen = {}
    named = {block_id for _, block_id, _, _ in lines if block_id}
    for number, block_id, entries, problem in lines:
        if problem:
            problems.append(problem)
            continue
        if block_id not in by_id:
            problems.append(f"line {number}: {block_id}: no such block")
        elif block_id in seen:
            problems.append(f"line {number}: {block_id}: a second line for this block")
        else:
            seen[block_id] = entries
    for block_id in order:
        if block_id not in named:
            problems.append(f"{block_id}: no sidecar line")
    listed = [block_id for _, block_id, entries, problem in lines if problem is None and block_id in by_id]
    if not problems and listed != order:
        problems.append(f"{SIDECAR}: lines are not in the order of rules.d1.ve then facts.d1.ve")

    for block in blocks:
        entries = seen.get(block["id"]) or []
        block["entries"] = entries
        block["problems"] = [f"UNANCHORED quote {q[:70]!r}" for q in block["unanchored"]]
        covered = set().union(*(words(e["words"]) for e in entries)) if entries else set()
        for word in block["unaccounted"]:
            if word not in covered:
                block["problems"].append(f"unaccounted word {word!r} is in no entry")
        for entry in entries:
            entry_words = words(entry["words"])
            if not entry_words:
                block["problems"].append(f"entry {entry['words']!r} has no content word")
            outside = sorted(entry_words - block["span_words"])
            if outside and not block["elided"]:
                block["problems"].append(f"entry {entry['words']!r}: {outside} not in the source span")
            block["problems"].extend(resolve(entry, block, by_id, legend, reading_sets, limits))
        problems.extend(f"{block['id']}: {p}" for p in block["problems"])

    losses = {}
    for block in blocks:
        for entry in block["entries"]:
            if entry["reason"] == "loss":
                key = entry["arg"]
                losses[key] = losses.get(key, 0) + 1
    reasons = {}
    for block in blocks:
        for entry in block["entries"]:
            reasons[entry["reason"]] = reasons.get(entry["reason"], 0) + 1
    totals = {"blocks": len(blocks),
              "blocks_with_loss": sum(1 for b in blocks if any(e["reason"] == "loss" for e in b["entries"])),
              "losses_by_class": dict(sorted(losses.items(), key=lambda kv: _class_key(kv[0]))),
              "entries_by_reason": dict(sorted(reasons.items())),
              "unaccounted_words": sum(len(b["unaccounted"]) for b in blocks),
              "blocks_with_unaccounted_words": sum(1 for b in blocks if b["unaccounted"]),
              "quotes": sum(len(b["quotes"]) for b in blocks),
              "unanchored_quotes": sum(len(b["unanchored"]) for b in blocks),
              "elided_quotes_without_source": sum(len(b["elided"]) for b in blocks)}
    return {"case": case.name, "source_sha256": None if source_text is None else
            hashlib.sha256(source_text.encode("utf-8")).hexdigest(),
            "blocks": [{"id": b["id"], "file": b["file"], "span_length": len(b["span"]), "used": b["used"],
                        "unaccounted": b["unaccounted"], "entries": b["entries"], "problems": b["problems"],
                        **({"elided_needs_source": b["elided"]} if b["elided"] else {})} for b in blocks],
            "totals": totals, "problems": problems}


def _class_key(key: str):
    return (1, int(key.split()[1])) if key.startswith("limit ") else (0, int(key))


def resolve(entry, block, by_id, legend, reading_sets, limits):
    """The problems of one entry's reason argument (empty when it resolves)."""
    reason, arg = entry["reason"], entry["arg"]
    if reason == "rule":
        target = by_id.get(arg)
        if target is None:
            return [f"rule {arg}: no such block"]
        if arg == block["id"]:
            return [f"rule {arg}: a block cannot carry its own omission"]
        missing = sorted(words(entry["words"]) - target["accounted"])
        return [f"rule {arg}: {missing} are not among its accounted words"] if missing else []
    if reason == "open":
        entry_legend = legend.get(arg)
        if entry_legend is None or entry_legend["kind"] != "predicate":
            return [f"open {arg}: no such predicate"]
        if not DECIDER.search(entry_legend["description"]):
            return [f"open {arg}: its description names no decider ('decided by' or 'decides')"]
        return []
    if reason == "reading":
        if arg not in block["sets"] and arg not in reading_sets:
            return [f"reading {arg}: neither the block's when field nor PLAN 3.1 names this set"]
        return []
    if reason == "loss":
        if arg.startswith("limit "):
            n = int(arg.split()[1])
            return [] if n in limits else [f"loss limit {n}: PLAN section 12 has no item {n}"]
        return [] if int(arg) in LOSS_CLASSES else [f"loss {arg}: no such fidelity class"]
    return []


def score(result: dict, verdicts: Path):
    """The hit rate: of the re-audit's UNFAITHFUL units, those with a `loss` entry; of the FAITHFUL, those with one."""
    truth = dict(re.findall(r"^(\S+) (FAITHFUL|UNFAITHFUL)\s*$", verdicts.read_text(encoding="utf-8"), flags=re.M))
    has_loss = {b["id"]: any(e["reason"] == "loss" for e in b["entries"]) for b in result["blocks"]}
    unfaithful = sorted(u for u, v in truth.items() if v == "UNFAITHFUL" and u in has_loss)
    faithful = sorted(u for u, v in truth.items() if v == "FAITHFUL" and u in has_loss)
    return {"verdicts": str(verdicts), "unfaithful": len(unfaithful),
            "unfaithful_with_loss": sum(1 for u in unfaithful if has_loss[u]),
            "unfaithful_without_loss": [u for u in unfaithful if not has_loss[u]],
            "faithful": len(faithful), "faithful_with_loss": [u for u in faithful if has_loss[u]],
            "units_not_blocks": sorted(u for u in truth if u not in has_loss)}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("case")
    parser.add_argument("--source", type=Path)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--report", type=Path)
    parser.add_argument("--score", type=Path)
    parser.add_argument("--sidecar", type=Path, help="a sidecar other than <case>/accounting.d1.txt")
    args = parser.parse_args(argv)
    case = case_dir(args.case)
    source_text = args.source.read_text(encoding="utf-8", errors="replace") if args.source else None
    try:
        result = account(case, source_text, args.sidecar)
    except AccountingError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if args.score:
        result["score"] = score(result, args.score)
        s = result["score"]
        print(f"score: {s['unfaithful_with_loss']} of {s['unfaithful']} UNFAITHFUL units have a loss entry; "
              f"without one: {', '.join(s['unfaithful_without_loss']) or 'none'}")
        print(f"score: {len(s['faithful_with_loss'])} of {s['faithful']} FAITHFUL units have a loss entry: "
              f"{', '.join(s['faithful_with_loss']) or 'none'}")
    totals = result["totals"]
    print(f"{result['case']}: {totals['blocks']} blocks, {totals['unaccounted_words']} unaccounted words in "
          f"{totals['blocks_with_unaccounted_words']} blocks, {totals['blocks_with_loss']} blocks with a loss "
          f"{totals['losses_by_class']}, {totals['unanchored_quotes']} of {totals['quotes']} quotes unanchored"
          + ("" if source_text is not None else
             f", {totals['elided_quotes_without_source']} elided quotes need the source"))
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.check:
        for problem in result["problems"]:
            print(f"problem: {problem}")
        return 1 if result["problems"] else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
