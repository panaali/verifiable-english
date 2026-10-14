"""DF-0 item 2: bare generics, by the screen stated in docs/research/defeasible-phase1.md 1.2 (committed first).

    uv run python research/defeasible/screen_bare_generics.py

Word classes come from OEWN 2025 (`ve/lexicon/oewn-2025.json`), read as data.
"""
from __future__ import annotations

import json
import re

from common import (CONSTITUTION, CONSTITUTION_RUN, MARKER_RE, ROOT, UDHR, UDHR_RUN, sha256, unit_bytes,
                    unit_text, units, write_json)
from screen_markers import CLASSES, INSTRUCTIONS

LEXICON = ROOT / "ve/lexicon/oewn-2025.json"

MODALS = {"must", "should", "shall", "may", "might", "can", "could", "will", "would", "ought", "cannot", "can't",
          "won't", "shouldn't", "mustn't"}
DEONTIC = {"need", "needs", "require", "requires", "required", "permit", "permits", "permitted", "allow", "allows",
           "allowed", "forbid", "forbids", "forbidden", "prohibit", "prohibits", "prohibited", "oblige", "obliges",
           "obliged", "obligated"}
CLOSED = {
    # determiners and quantifiers
    "a", "an", "the", "this", "that", "these", "those", "my", "our", "your", "his", "her", "its", "their", "some",
    "any", "each", "every", "all", "no", "many", "most", "few", "several", "both", "either", "neither", "much",
    "such", "another", "other", "more", "less", "fewer", "enough", "own", "same", "certain", "various",
    # pronouns
    "i", "we", "you", "he", "she", "it", "they", "me", "us", "him", "them", "one", "ones", "someone", "anyone",
    "everyone", "nobody", "something", "anything", "everything", "nothing", "itself", "themselves", "ourselves",
    "yourself", "himself", "herself", "oneself",
    # prepositions
    "in", "on", "at", "by", "for", "with", "without", "from", "to", "of", "about", "into", "onto", "over", "under",
    "after", "before", "during", "through", "between", "among", "against", "within", "across", "towards", "toward",
    "upon", "beyond", "despite", "via", "per", "like", "unlike", "around", "behind", "below", "above", "near",
    # conjunctions and subordinators
    "and", "or", "but", "nor", "so", "yet", "if", "when", "whenever", "while", "whilst", "although", "though",
    "because", "since", "as", "unless", "until", "once", "whether", "than", "then", "also", "however", "thus",
    "therefore", "instead", "rather", "even", "only", "just", "still", "indeed", "perhaps",
    # wh-words, negation, numerals, deictics
    "what", "which", "who", "whom", "whose", "where", "why", "how", "not", "never", "there", "here", "now",
    "first", "second", "third", "two", "three", "four", "five", "ten", "hundred",
    # auxiliaries and copulas (never a subject word)
    "is", "are", "was", "were", "be", "been", "being", "am", "has", "have", "had", "do", "does", "did",
}
ADVERBS = {"often", "also", "always", "never", "sometimes", "rarely", "still", "only", "even", "already", "just"}
IRREGULAR_PLURALS = {"people", "children", "men", "women", "data", "media", "criteria"}
WORD = re.compile(r"[A-Za-z][A-Za-z'’-]*")
LIST_MARKER = re.compile(r"^(?:[-*+]\s+|\d+\.\s+|\([A-Za-z0-9]+\)\s+|[A-Za-z]\)\s+)")
CLAUSE_END = re.compile(r"[,;:.?!()—–\"“”\n]| - ")


def lexicon():
    data = json.loads(LEXICON.read_text())
    nouns, adjectives, verbs, third = set(), set(), set(), set()
    for lemma, cls, _suffixes, forms in data["entries"]:
        if cls == "noun":
            nouns.add(lemma)
        elif cls == "adjective":
            adjectives.add(lemma)
        elif cls == "verb":
            verbs.add(lemma)
            third.update(forms.get("third_person", ()))
    return nouns, adjectives, verbs, third


NOUNS, ADJECTIVES, VERBS, THIRD = lexicon()


def plural(word):
    if word in IRREGULAR_PLURALS:
        return True
    if word.endswith("ies") and word[:-3] + "y" in NOUNS:
        return True
    if word.endswith("es") and word[:-2] in NOUNS:
        return True
    return word.endswith("s") and word[:-1] in NOUNS


def normalise(text):
    text = text.lstrip()
    while True:
        before = text
        text = text.lstrip().lstrip(">").lstrip()
        text = LIST_MARKER.sub("", text)
        text = text.lstrip("*_").lstrip()
        if text == before:
            return text.replace("*", "").replace("_", "")


def first_clause(text):
    match = CLAUSE_END.search(text)
    return text[:match.start()] if match else text


def proper_names(source):
    words = WORD.findall(source)
    lower = {w for w in words if w == w.lower()}
    return {w.lower() for w in words if w != w.lower() and w.lower() not in lower}


def np_word(word, proper):
    return (word not in CLOSED and word not in proper
            and (word in NOUNS or word in ADJECTIVES or plural(word)))


def verb_agrees(head, verb):
    if plural(head) and (verb in VERBS or verb in {"are", "have", "do", "don't", "don’t"}):
        return "plural"
    if head in NOUNS and (verb in THIRD or verb in {"is", "has", "does", "doesn't", "doesn’t"}):
        return "singular"
    return None


def screen(clause, proper):
    words = [w.lower() for w in WORD.findall(clause)]
    if not words or words[0] in CLOSED or words[0] in proper:
        return None
    for k in range(1, 5):
        if k >= len(words) or not np_word(words[k - 1], proper):
            return None
        for at in (k, k + 1):
            if at >= len(words) or (at == k + 1 and not (words[k].endswith("ly") or words[k] in ADVERBS)):
                continue
            form = verb_agrees(words[k - 1], words[at])
            if form:
                return {"subject": " ".join(words[:k]), "verb": words[at], "head": form}
    return None


def run(source_path, run_path):
    source = source_path.read_bytes()
    proper = proper_names(source.decode("utf-8"))
    counts = {"units": 0, "headings": 0, "marker": 0, "modal_or_deontic": 0, "no_match": 0, "match": 0}
    rows = []
    for unit in units(run_path):
        counts["units"] += 1
        text = normalise(unit_text(source, unit))
        if text.startswith("#"):
            counts["headings"] += 1
            continue
        if MARKER_RE.search(unit_text(source, unit)):
            counts["marker"] += 1
            continue
        clause = first_clause(text)
        if {w.lower() for w in WORD.findall(clause)} & (MODALS | DEONTIC):
            counts["modal_or_deontic"] += 1
            continue
        hit = screen(clause, proper)
        if hit is None:
            counts["no_match"] += 1
            continue
        counts["match"] += 1
        rows.append({"id": unit["id"], "bytes": unit_bytes(unit), "first_clause": clause.strip(), **hit})
    return {"inputs": {"units": sha256(run_path / "units.json"), "source": sha256(source_path),
                       "lexicon": sha256(LEXICON)},
            "counts": counts, "bytes": sum(r["bytes"] for r in rows), "rows": rows}


def main():
    constitution = run(CONSTITUTION / "source/claude-constitution.md", CONSTITUTION_RUN)
    udhr = run(UDHR / "source/udhr.md", UDHR_RUN)
    write_json("bare-generics.json", {"screen": "docs/research/defeasible-phase1.md 1.2",
                                      "constitution": constitution, "udhr_supplementary": udhr})
    # Item 2's units go to the deferred second reader as their own list, scored separately (no key: a count).
    source = (CONSTITUTION / "source/claude-constitution.md").read_bytes()
    by_id = {u["id"]: u for u in units(CONSTITUTION_RUN)}
    write_json("second-reader-packet-bare.json", {
        "instructions": INSTRUCTIONS, "classes": CLASSES,
        "units": [{"id": r["id"], "bytes": r["bytes"], "text": unit_text(source, by_id[r["id"]])}
                  for r in constitution["rows"]]})
    for name, result in (("constitution", constitution), ("udhr", udhr)):
        print(name, result["counts"], result["bytes"], "B")


if __name__ == "__main__":
    main()
