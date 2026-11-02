"""Check the q1-3b claims of the batch's two reports against its saved evidence, so that a claim written on an old
premise cannot outlive a rerun. Each summary, headline or conclusion sentence must cite its key (`C4 `f2.share``) or be
listed in `NO_CLAIM`; each bullet and table row elsewhere in the q1-3b section must cite one or sit under a heading that
does; every key must exist, every number must be a value of a cited key or of `derived`, every `TRUTHS` row must hold,
and no `STALE` wording stays.
A batch's review probe, not a permanent test (DRI decision D4): `tests/test_question_reverse.py` tests it on fixtures.

    uv run python docs/question-answering/q1-3b/claims.py [--list]
"""
from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[3]
BATCH = Path(__file__).parent
SPEC = "docs/spec/question-answering-q1-report.md"
REPORT = "docs/question-answering/q1-3b/REPORT.md"

# Wording of a premise a rerun or a probe refuted; the phrase "norm unit" hid two meanings (F10).
STALE = ("norm unit", "0 reached", "no prose unit reads", "prose never is", "for profile `soft-norms@0`",
         "has profile `soft-norms@0`", "profile `soft-norms@0` is refused", "every non-timing", "5,429 `unformalised`",
         "the long random earley", "each other sentence `moved`", "none of the 143 units of kind `norm` reads",
         "is not a question's source", "the pilot blobs' sha-256")
# (report, first words, last words or None for the end) of a part where each sentence must cite its own key. Anchors
# that are gone fail the check.
STRICT = ((SPEC, "q1-3b (C4, below) adds", "\n\n## Commands"), (SPEC, "- **For the plan:**", "\n\n### Latency"),
          (REPORT, "- **Result:**", "\n\nThe numbers are in"), (REPORT, "**On the gap row", "\n\n## How each"),
          (REPORT, "## Next", None))
UNITS = ((SPEC, "### Coverage", "- **For the plan:**"), (SPEC, "### Latency", None),
         (REPORT, "| (1) F2", "| (5) the report"))
# First words of a checked sentence that claims nothing a key could show, and why.
NO_CLAIM = {
    "q1-3b (C4, below) adds": "what the item adds; the sentences after it carry the numbers",
    "A better tie rule": "advice to the plan",
    "This count is the evidence": "advice to the plan",
    "Hand-written size is": "`git diff --numstat`, not the corpus run",
    "A re-scope fits this": "advice to the plan",
    "This run does not measure": "says what was not run",
    "The decision is the": "says who decides",
    "## Next - Q2.1": "plan order",
    "- q1-3c: the review": "plan order",
    "- A tie rule for": "plan order",
    "- More seeded bugs": "plan order",
    "A change there would": "says why they wait",
}
# A headline claim that a number alone cannot show (a small number can match another key, a zero may have no number):
# (report, the words as written, what must hold of the evidence). F10's sentence was a claim of this kind.


def reached_rows(e: dict) -> list:
    return [row for d in e["C4"]["norm"]["documents"].values() for row in d["reach"] if row[2] == "reached"]


def only_soft_chain(e: dict) -> bool:
    coverage = e["C4"]["coverage"]
    left = [k for k in ("unsealed_streams", "unsealed_random_earley", "unsealed_documents", "mixed_unmatched",
                        "documents_not_their_sentences", "mixed_paragraphs_not_their_sentences", "short_streams",
                        "skipped", "unavailable_reads") if coverage[k]]
    return coverage["whole_streams"] is False and left == ["unavailable_reads"] and \
        all("soft-chain" in k for k in coverage["unavailable_reads"])


def pair_is_refused(e: dict) -> bool:
    c6 = e["C6"]
    return c6["pair"]["outcomes"] == {"unavailable": 1} and c6["soft_only"]["outcomes"] == {"one": 1} and \
        c6["defaults_only"]["outcomes"] == {"one": 1}


def fences_only(e: dict) -> bool:
    count = sum(row[3] for row in reached_rows(e))
    return all(row[1] == "fence" for row in reached_rows(e)) and count == e["C4"]["norm"]["reached"] == 5


def only_fences_without_soft(e: dict) -> bool:
    soft = e["C6"]["soft_chain_without_soft"]
    return len(soft["read"]) == soft["fences"] == 3 and soft["outcomes"]["one"] == 3


def no_kind_norm_reads(e: dict) -> bool:
    return all(row[0] == "asserted" for row in reached_rows(e))


# A unit's `english.read` outcome as a claim counts it. `unavailable` (no answer) and `not asked` (not one sentence) are
# UNKNOWN: a unit with either does not read and does not fail to read, so "none of the N reads" cannot count it (F13).
OUTCOME = (("reached", "reached"), ("english.read:none:", "none"), ("english.read:rejected:", "rejected"),
           ("english.read:unavailable", "unavailable"), ("not one sentence", "not asked"))
UNKNOWN = frozenset({"unavailable", "not asked"})


def outcome(why: str) -> str:
    """The outcome a reach row's `why` names; a `why` no row of `OUTCOME` knows fails the check."""
    found = [name for prefix, name in OUTCOME if why == prefix or (prefix.endswith(":") and why.startswith(prefix))]
    if len(found) != 1:
        raise ValueError(f"reach row of unknown outcome: {why!r}")
    return found[0]


def kind_outcomes(e: dict, kind: str) -> Counter:
    """Each outcome's count over every unit of `kind` in C4, reached or not."""
    out = Counter()
    for d in e["C4"]["norm"]["documents"].values():
        for row in d["reach"]:
            if row[0] == kind:
                out[outcome(row[2])] += row[3]
    return out


def none_reads(counts: Counter | dict, population: int) -> bool:
    """Whether "none of the `population` reads" holds of `counts`: each of them has an answer, and none reads."""
    return sum(counts.values()) == population and all(k in ("none", "rejected") for k, v in counts.items() if v)


def answered(counts: Counter) -> Counter:
    return Counter({k: v for k, v in counts.items() if k not in UNKNOWN})


def norm_units_answered(e: dict) -> bool:
    found = kind_outcomes(e, "norm")
    return sum(found.values()) == 143 and none_reads(answered(found), 100)


def norm_units_unknown(e: dict) -> bool:
    soft = [row for name, d in e["C4"]["norm"]["documents"].items() if "soft-chain" in name for row in d["reach"]
            if row[0] == "norm" and outcome(row[2]) == "unavailable"]
    found = kind_outcomes(e, "norm")
    return found["not asked"] == 30 and found["unavailable"] == sum(row[3] for row in soft) == 13


def fences_are_asserted(e: dict) -> bool:
    """Every fenced unit, reached or not, is of kind `asserted`, and there are 8."""
    rows = [row for d in e["C4"]["norm"]["documents"].values() for row in d["reach"] if row[1] == "fence"]
    return all(row[0] == "asserted" for row in rows) and sum(row[3] for row in rows) == 8


def soft_chain_others_answered(e: dict) -> bool:
    soft = e["C6"]["soft_chain_without_soft"]
    others = Counter(soft["outcomes"]) - Counter(one=soft["fences"])
    return not soft["errors"] and none_reads(others, soft["sentences"] - soft["fences"])


def corpus_streams_give_none(e: dict) -> bool:
    c4 = e["C4"]
    return not any(k.split(":")[0] == "none" for k in c4["f2"]["outcomes"]) and \
        all(m["code"] == "QuestionTooLong" for m in c4["f1"]["misses"])


def blob_ids_recorded(e: dict) -> bool:
    """14 parts' values are 40-hex git blob ids and `udhr-part07`'s is a 64-hex SHA-256: recorded, not compared."""
    ids = {name: d["sha256"] for name, d in e["C4"]["norm"]["documents"].items()}
    hexes = all(re.fullmatch(r"[0-9a-f]+", v) for v in ids.values())
    blobs = [n for n, v in ids.items() if len(v) == 40 and n.startswith("norm-documents:pilot/")]
    own = [n for n, v in ids.items() if len(v) == 64 and n.endswith("/udhr-part07.ve.md")]
    return hexes and len(blobs) == 14 and len(own) == 1 and len(ids) == 15


TRUTHS = (
    (SPEC, "No fronting that Lean answers reads another formula or is `many`",
     lambda e: not e["C4"]["f2"]["other_formula"] and not e["C4"]["f2"]["many_causes"]),
    (SPEC, "5 of 5,859 units are reached, all `ve` fences of kind `asserted`", lambda e: fences_only(e) and no_kind_norm_reads(e)),
    (SPEC, "of the 143 units of kind `norm`, `english.read` answers 100 and reads none", norm_units_answered),
    (SPEC, "30 are not one sentence and 13 are in `soft-chain`", norm_units_unknown),
    (SPEC, "`english.read` answers 100 of the 143 and reads none", norm_units_answered),
    (SPEC, "13 in `soft-chain` have no answer and 30 are not one sentence", norm_units_unknown),
    (SPEC, "is false for one reason", only_soft_chain),
    (SPEC, "`english.question` refuse that pair", pair_is_refused),
    (SPEC, "reads its 3 fences and none of its other 1,002 sentences",
     lambda e: only_fences_without_soft(e) and soft_chain_others_answered(e)),
    (SPEC, "**Over-generation:** no answered fronting reads with a formula other than its sentence's, so the 4.9 measure "
     "finds no acceptance to list", lambda e: not e["C4"]["f2"]["other_formula"]),
    (SPEC, "The corpus streams give none", corpus_streams_give_none),
    (SPEC, "111 of 148 sentences have no fronting that reads", lambda e: (e["C5"]["unreached"], e["C5"]["sentences"]) ==
     (111, 148) and e["C5"]["outcomes"].get("one") == e["C5"]["reached"] and
     set(e["C5"]["outcomes"]) <= {"budget", "moved", "one", "none", "rejected"}),
    (SPEC, "not compared: each part's git blob id, or `udhr-part07`'s SHA-256, recorded", blob_ids_recorded),
    (REPORT, "Lean answers all but one", lambda e: e["C4"]["f2"]["outcomes"]["unavailable"] == 1),
    (REPORT, "reads none with another formula, and none is `many`",
     lambda e: not e["C4"]["f2"]["other_formula"] and not e["C4"]["f2"]["many_causes"]),
    (REPORT, "5 of 5,859 units are reached, all `ve` fences", fences_only),
    (REPORT, "no prose Lean answers for reads", fences_only),
    (REPORT, "a pair `english.read` and `english.question` refuse though each alone reads", pair_is_refused),
    (REPORT, "only 8 of the 5,859 units have a fence, none is of kind `norm`", fences_are_asserted),
    (REPORT, "none that Lean answers for reads", fences_only),
    (REPORT, "reads its 3 fences and none of its other 1,002 sentences",
     lambda e: only_fences_without_soft(e) and soft_chain_others_answered(e)),
    (REPORT, "the other 70 norms have none", lambda e: sum(
        row[3] for d in e["C4"]["norm"]["documents"].values() for row in d["reach"] if row[:2] == ["norm", "-"]) == 70),
)
# A universal claim ("none", "never", "no ... reads") claims of every unit, so a number cannot show it: each one in the
# checked text must sit inside the words of a `TRUTHS` row, or of a row here that says why it claims nothing (F13).
UNIVERSAL = re.compile(r"\b(?:none|never|nothing)\b|\bno\b[^,;.()]*?\b(?:reads?|reached|reaches|accept\w*)\b", re.I)
NOT_UNIVERSAL = {
    "C4 does not save which sentences no fronting reaches": "says what C4 does not hold",
    "the sentences no question form reaches and why": "names the task's row",
    "for which the document holds no VE sentence": "a document's text is source English (the sentence before)",
}
# The table's `Compared with` column: each cell as written, and what must hold of the evidence. A digest or a count the
# run compares has its comparison's key; a value it only records says `not compared` (F14).
COMPARED = {
    "`corpus_sha256`, 17 of 17": lambda e: not e["C4"]["coverage"]["unsealed_streams"],
    "not compared: drawn by the seal's generator (not sealed)": lambda e: True,
    "not compared: read from the files": lambda e: True,
    "`random_earley_corpus_sha256`, 17 of 17": lambda e: not e["C4"]["coverage"]["unsealed_random_earley"],
    "`document_corpus_sha256`, 17 of 17": lambda e: not e["C4"]["coverage"]["unsealed_documents"],
    "the report's `corpus_sha256`, 18 of 18; the seal's 6,757":
        lambda e: not e["C4"]["coverage"]["mixed_unmatched"] and
        e["C4"]["coverage"]["mixed_texts"] == e["C4"]["coverage"]["seal_sizes"]["english-mixed"],
    "the seal's 1,220": lambda e: e["C4"]["coverage"]["natural_statements"] ==
        e["C4"]["coverage"]["seal_sizes"]["natural-view"],
    "not compared: each part's git blob id, or `udhr-part07`'s SHA-256, recorded (C4 `norm.documents.*.sha256`)":
        blob_ids_recorded,
}
# Numbers in the checked text that name a plan section, or a fact of the host that the evidence does not hold.
OUTSIDE = {"3.6", "4.9", "10.2", "2.5", "32"}
NUMBER = re.compile(r"(?<![\w.,-])\d[\d,]*(?:\.\d+)?%?(?![\w-])")
CITED = re.compile(r"\bC([1456])((?:,? (?:and )?`[^`]+`)+)")


def values(node, path: list[str]) -> list | None:
    """The values at a dotted key's `path`, `*` meaning every child; None when the key does not exist."""
    if not path:
        return [node]
    head, rest = path[0].strip('"'), path[1:]
    if head == "*" and isinstance(node, dict | list):
        found = [values(child, rest) for child in (node.values() if isinstance(node, dict) else node)]
        return [v for f in found if f is not None for v in f] if any(f is not None for f in found) else None
    return values(node[head], rest) if isinstance(node, dict) and head in node else None


def split_key(key: str) -> list[str]:
    return re.findall(r'"[^"]+"|[^.]+', key)


def numbers(node) -> set[float]:
    """Every number under `node`, with the length of each list (a list's count is what a report cites)."""
    if isinstance(node, bool):
        return set()
    if isinstance(node, int | float):
        return {node}
    if isinstance(node, dict):
        return set().union(*map(numbers, node.values())) if node else {0}
    if isinstance(node, list):
        return {len(node)}.union(*map(numbers, node))
    return set()


def matches(token: str, known: set[float]) -> bool:
    """Whether a number as the report writes it (1,442, 0.256, 91%, 1,451.3) is one of the `known` values, rounded."""
    text = token.replace(",", "").rstrip("%")
    if token.endswith("%"):
        return any(round(v * 100) == float(text) for v in known)
    places = len(text.partition(".")[2])
    return any(round(v, places) == float(text) for v in known)


def problems(unit: str, evidence: dict[str, dict], inherited: tuple = (), extra: frozenset = frozenset()) -> list[str]:
    """What is wrong with one checked sentence, bullet or row: no citation, a key that is not there, or a number that
    no cited key (or `inherited`, its heading's citation) holds."""
    cited = [(label, key) for label, keys in CITED.findall(unit) for key in re.findall(r"`([^`]+)`", keys)]
    if not cited and not inherited:
        return ["cites no key"]
    found, out = set(extra), []
    for label, key in (*cited, *inherited):
        got = values(evidence[f"C{label}"], split_key(key))
        if got is None:
            out.append(f"C{label} has no key {key}")
        else:
            found |= numbers(got)
    plain = re.sub(r"\[[^]]*\]\([^)]*\)|`[^`]*`", " ", unit)
    return out + [f"{token} is not a value of its keys" for token in NUMBER.findall(plain)
                  if token.rstrip(",") not in OUTSIDE and not matches(token.rstrip(","), found)]


def derived(c4: dict, c6: dict) -> frozenset:
    """Numbers the reports add up from C4 or C6's keys: totals, and each unit kind's count out of `reach`."""
    by_why, closest, questions, kinds = c4["norm"]["by_why"], c4["closest"], c4["norm"]["questions"], Counter()
    for document in c4["norm"]["documents"].values():
        for kind, content, _, count in document["reach"]:
            kinds[kind] += count
            kinds[(kind, content)] += count
    names = [k for k in kinds if isinstance(k, str)]
    unformalised = sum(kinds[k] for k in names if "unformalised" in k)
    attributed = [k for k in names if k.startswith('["attributed"')]
    attributed_unformalised = sum(kinds[k] for k in attributed if "unformalised" in k)
    soft = c6["soft_chain_without_soft"]
    misses = Counter(m["config"].split(":")[0] for m in c4["f1"]["misses"])
    fences = {text for document in c4["norm"]["documents"].values() for key, texts in document["examples"].items()
              if key.endswith("/reached") for text in texts}
    norms = kind_outcomes({"C4": c4}, "norm")
    return frozenset({
        sum(by_why.values()), sum(v for k, v in by_why.items() if ":rejected:" in k),
        questions["f1_unavailable"] + questions["f2_unavailable"], questions["f1_same"] + questions["f2_same"],
        closest["one_candidate"] + closest["measured"], closest["by_form"]["f2"] - closest["measured"],
        unformalised, attributed_unformalised, sum(kinds[k] for k in attributed) - attributed_unformalised,
        kinds["meta"], kinds["norm"], kinds["asserted"], kinds[("asserted", "ast")], kinds[("asserted", "fence")],
        kinds[("norm", "norm")], kinds[("norm", "-")], kinds[("norm", "norm")] + kinds[("asserted", "ast")],
        kinds[("asserted", "fence")] - c4["norm"]["reached"], soft["sentences"] - soft["fences"],
        c4["streams"]["random-earley"]["configs"] * 50, 250,
        c4["coverage"]["mixed_texts"] - c4["streams"]["english-mixed"]["one_formula"], *misses.values(),
        c4["f2"]["sentences"] - c4["f2"]["limited"], len(fences), 50,
        *norms.values(), sum(answered(norms).values()), sum(norms.values()) - sum(answered(norms).values())})


def sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.])\s+(?=[A-Z`*(-])", re.sub(r"\s+", " ", text)) if s.strip()]


def cut(text: str, start: str, end: str | None) -> str | None:
    """The part of `text` from `start` up to `end`, or None when an anchor is gone."""
    begin = text.find(start)
    stop = text.find(end, begin + len(start)) if end else len(text)
    return None if begin < 0 or stop < 0 else text[begin:stop]


def blocks(text: str) -> list[tuple[str, tuple]]:
    """(bullet, paragraph or table row, the citation of the `###` heading above it), in order."""
    out, heading, lines = [], (), text.split("\n")
    for line in lines:
        if line.startswith("### "):
            heading = tuple((label, k) for label, keys in CITED.findall(line) for k in re.findall(r"`([^`]+)`", keys))
        elif line.startswith(("- ", "  - ", "| ")) or not out or not line.strip():
            if line.strip() and not line.startswith("|---") and "| Measure |" not in line and "| Stream |" not in line:
                out.append((re.sub(r"^\| \(\d\) ", "| ", line), heading))
        else:
            out[-1] = (f"{out[-1][0]} {line.strip()}", heading)
    return out


def uncovered(unit: str, covers: list[str]) -> list[str]:
    """Each universal claim in `unit`, outside code, that no words of `covers` contain."""
    spans = [(m.start(), m.end()) for words in covers for m in re.finditer(re.escape(words), unit)]
    spans += [(m.start(), m.end()) for m in re.finditer(r"`[^`]*`", unit)]
    return [m.group(0) for m in UNIVERSAL.finditer(unit)
            if not any(start <= m.start() and m.end() <= end for start, end in spans)]


def compared_cells(text: str) -> list[str] | None:
    """The `Compared with` column of the table that has one, or None when there is no such table."""
    lines = text.split("\n")
    head = next((k for k, line in enumerate(lines) if line.startswith("|") and "| Compared with |" in line), None)
    if head is None:
        return None
    column = [c.strip() for c in lines[head].split("|")].index("Compared with")
    rows = [line for line in lines[head + 1:] if line.startswith("|") or not line.strip()]
    rows = rows[:next((k for k, line in enumerate(rows) if not line.strip()), len(rows))]
    return [line.split("|")[column].strip() for line in rows if not line.startswith("|---")]


def check(texts: dict[str, str], evidence: dict[str, dict], extra: frozenset, no_claim: dict = NO_CLAIM,
          report=None, truths: tuple = TRUTHS, compared: dict | None = COMPARED,
          not_universal: dict = NOT_UNIVERSAL) -> list[str]:
    """Every problem of both reports; `report` receives each checked unit and whether it claims anything. `compared`
    None leaves out the `Compared with` column (a fixture with no table)."""
    out = [f"{path}: stale wording: {w!r}" for path, text in texts.items() for w in STALE
           if w in re.sub(r"\s+", " ", text).lower()]
    flat = {path: re.sub(r"\s+", " ", text) for path, text in texts.items()}
    out.extend(f"{path}: words gone: {words!r}" for path, words, _ in truths if words not in flat[path])
    out.extend(f"{path}: not so: {words!r}" for path, words, holds in truths
               if words in flat[path] and not holds(evidence))
    if compared is not None:
        cells = compared_cells(texts[SPEC])
        if cells is None:
            out.append(f"{SPEC}: anchor gone: 'Compared with'")
        else:
            out.extend(f"{SPEC}: compared with what no COMPARED row backs: {c!r}" for c in cells if c not in compared)
            out.extend(f"{SPEC}: not so: compared with {c!r}" for c in cells if c in compared
                       and not compared[c](evidence))
            out.extend(f"COMPARED row unused: {c!r}" for c in compared if c not in cells)
    covers = {path: [w for p, w, _ in truths if p == path] + list(not_universal) for path in texts}
    universal_used = set()

    def universal(path: str, unit: str) -> None:
        universal_used.update(w for w in not_universal if w in unit)
        out.extend(f"{path}: {unit[:70]!r}: universal claim with no TRUTHS row: {u!r}"
                   for u in uncovered(unit, covers[path]))
    used = set()
    for path, start, end in STRICT:
        part = cut(texts[path], start, end)
        if part is None:
            out.append(f"{path}: anchor gone: {start!r}")
            continue
        for sentence in sentences(part):
            reason = next((k for k in no_claim if sentence.startswith(k)), None)
            used.add(reason)
            if report:
                report(path, sentence, reason)
            universal(path, sentence)
            if reason is None:
                out.extend(f"{path}: {sentence[:70]!r}: {p}" for p in problems(sentence, evidence, (), extra))
    for path, start, end in UNITS:
        part = cut(texts[path], start, end)
        if part is None:
            out.append(f"{path}: anchor gone: {start!r}")
            continue
        for unit, heading in blocks(part):
            if unit.startswith("### "):
                continue
            if report:
                report(path, unit, None)
            universal(path, unit)
            out.extend(f"{path}: {unit[:70]!r}: {p}" for p in problems(unit, evidence, heading, extra))
    return out + [f"NO_CLAIM row unused: {k!r}" for k in no_claim if k not in used] + \
        [f"NOT_UNIVERSAL row unused: {k!r}" for k in not_universal if k not in universal_used]


def main(argv: list[str]) -> int:
    c4 = json.loads((BATCH / "evidence/question-reverse-b.json").read_text())
    samples = json.loads((BATCH / "evidence/samples.json").read_text())
    c1 = json.loads((BATCH.parent / "q1-3/evidence/question-reverse.json").read_text())
    evidence = {"C1": c1, "C4": c4, "C5": samples["c5"], "C6": samples["c6"]}
    texts = {path: (ROOT / path).read_text() for path in (SPEC, REPORT)}
    checked = []
    found = check(texts, evidence, derived(c4, samples["c6"]), report=lambda *row: checked.append(row))
    if not c4["commit"].startswith("5c56edcec"):
        found.append(f"C4 ran at {c4['commit']}, not the commit the reports name")
    if "--list" in argv:
        for path, unit, reason in checked:
            print(f"{Path(path).name}: {unit[:110]}" + (f" [no claim: {NO_CLAIM[reason]}]" if reason else ""))
    print("\n".join(found) or f"{len(checked)} claims checked, 0 problems")
    return 1 if found else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
