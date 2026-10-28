"""Q1.4b's check of its saved A/B (plan Q1.4; DRI 2026-10-27 item 4, DRI 2026-10-28 items 1-5).

The corpus, its recording and its comparison are Q1.4's (`../../q1-4/evidence/speech_ab.py write` and `compare`):
base.json is `write` at the merge base, head.json is `write` at this item's head, and delta.json is `compare` of the
two; `augment` adds the cases of `extra_cases` to both. A `verdict` row must be in exactly one signed class.
2026-10-27 item 4: (a) `gloss`, a declared gloss the base read as its one predicate and Lean's lexicon refuses; (b)
`folded`, a name the base matched after folding its case and Lean refuses; (c) `quantified`, the six `Is every/some
service reviewed?` in Q1.4's environments, which the base refused as `UnknownAlternative` and Lean reads with a
quantifier. 2026-10-28: item 1 `negative`, a declared negative verbalisation; item 2 `bare_name` and `quoted_name`,
a name with a digit or underscore; item 3 `determiner`, a grammar determiner outside (c); items 4 and 5
`unverbalised`, a predicate declared without a verbalisation; item 5 `opening`, a question of `opening_cases` (one
sentence per grammar rule, so every way a sentence opens) that the base refused and Lean reads. A `class` or
`wording` row must keep R1's (a) and (b) or be R2's rule O1, as in Q1.4. A `lint` row fails, and so does a class
whose count is not the recorded one, so an empty delta or a head-against-head comparison fails too. `audit` and
`check` are the same check.
"""
from __future__ import annotations

import functools
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "q1-4" / "evidence"))

import speech_ab  # noqa: E402

NEGATIVE_SUBJECTS = ("atlas", "beacon")
SPECIAL_NAMES = ("atlas2", "atlas_two", "beacon2", "beacon_two")
GRAMMAR = Path(__file__).resolve().parents[4] / "ve/english_grammar/relational-fol@0.json"
UNVERBALISED = "checked"
EXTRA_ENVS = ("negative", "names", "unverbalised")


def determiners() -> tuple[str, ...]:
    """The words the grammar puts before a noun phrase: the first terminal of every rule whose next symbol is a
    declaration or a natural subject (`every`, `some`, `no`). Read from the grammar source, so a determiner the
    grammar gains is a corpus case before anyone lists it."""
    rules = json.loads(GRAMMAR.read_text())
    return tuple(sorted({r["rhs"][0] for r in rules if len(r["rhs"]) > 1 and type(r["rhs"][0]) is str
                         and r["rhs"][1] in ({"n": "declaration"}, {"n": "natural_subject"})}))


def reader_cases() -> list[tuple[str, str, str]]:
    """(env, wording, predicate word) over the reader's dimensions: subject (a name, or each grammar determiner over
    a sort) x predicate declaration (with a verbalisation in `speech`; without one in `unverbalised`, as declared
    and capitalised) x polarity."""
    forms = {"speech": ("reviewed",), "unverbalised": (UNVERBALISED, UNVERBALISED.capitalize())}
    subjects = {"speech": (), "unverbalised": ("atlas",)}
    return [(env, f"Is {subject} {polarity}{word}?", word)
            for env, words in forms.items() for word in words
            for subject in (*subjects[env], *(f"{det} service" for det in determiners()))
            for polarity in ("", "not ")]


def _lexicon(raw: dict, word: str) -> dict[str, list[str]]:
    """The words of the grammar's vocabulary categories (the nonterminals no grammar rule defines) for the
    environment `raw` and its one-place predicate `word` over `service`, as `ve/english.py` builds them; a category
    the environment cannot fill (`relation`, `object_relative`) is absent, so no sentence is built through it."""
    from ve.environment import Environment
    from ve.printer import _fluent_variable_letters

    noun = raw["vocabulary"]["sorts"]["service"]["verbalisation"]["singular"]
    constant = next(n for n, c in raw["vocabulary"]["constants"].items() if c["sort"] == "service")
    letter = _fluent_variable_letters({"service": noun}, Environment(raw))["service"]
    return {"noun": [noun], "constant": [constant], "label": [letter + "1"], "adjective": [word],
            "atom": [constant, "is", word], "relative": ["is", word], "copula_relative": ["is", word],
            "copula_adjective": [word], "natural_subject": [word, noun], "owner_clause": ["has", "an", "owner"]}


def _symbol(s) -> str | None:
    """A rule symbol's terminal text (a word, a case-folded word, a punctuation mark), or None for a nonterminal."""
    return s if type(s) is str else s.get("c", s.get("p"))


def _join(tokens: list) -> str:
    """Spell tokens as the grammar does: a punctuation symbol marked `before` follows its word without a space."""
    text = ""
    for t in tokens:
        text += t[0] if type(t) is tuple else (" " if text else "") + t
    return text


def opening_sentences(raw: dict, word: str) -> dict[str, list]:
    """One sentence per grammar rule, so every way a sentence can open (a marker, `it is not the case that`, `there
    is a`, `this is impossible`, a determiner, a term, a listing, ...) is a corpus case. Each rule is put in the
    shortest sentence that reaches its left-hand side, with every other nonterminal at its shortest expansion; read
    from the grammar source and the environment's words, so a rule the grammar gains is a case before anyone lists
    it. Returns tag -> tokens (a `before` punctuation mark is a 1-tuple). A rule no sentence reaches is absent."""
    rules = json.loads(GRAMMAR.read_text())
    tok = lambda s: (s["p"],) if type(s) is dict and s.get("before") else _symbol(s)
    shortest = dict(_lexicon(raw, word))
    changed = True
    while changed:  # the shortest expansion of each nonterminal, to a fixed point
        changed = False
        for r in rules:
            if all(_symbol(s) is not None or s["n"] in shortest for s in r["rhs"]):
                out = [t for s in r["rhs"] for t in ([tok(s)] if _symbol(s) is not None else shortest[s["n"]])]
                if r["lhs"] not in shortest or len(out) < len(shortest[r["lhs"]]):
                    shortest[r["lhs"]], changed = out, True
    hole = object()
    context = {"sentence": [hole]}  # the shortest sentence with a hole where the nonterminal goes
    changed = True
    while changed:
        changed = False
        for r in rules:
            if r["lhs"] not in context:
                continue
            for i, s in enumerate(r["rhs"]):
                if _symbol(s) is not None or any(_symbol(o) is None and o["n"] not in shortest
                                                 for j, o in enumerate(r["rhs"]) if j != i):
                    continue
                inner = [t for j, o in enumerate(r["rhs"]) for t in (
                    [hole] if j == i else [tok(o)] if _symbol(o) is not None else shortest[o["n"]])]
                at = context[r["lhs"]].index(hole)
                out = context[r["lhs"]][:at] + inner + context[r["lhs"]][at + 1:]
                if s["n"] not in context or len(out) < len(context[s["n"]]):
                    context[s["n"]], changed = out, True
    sentences = {}
    for r in rules:
        if r["lhs"] in context and all(_symbol(s) is not None or s["n"] in shortest for s in r["rhs"]):
            body = [t for s in r["rhs"] for t in ([tok(s)] if _symbol(s) is not None else shortest[s["n"]])]
            at = context[r["lhs"]].index(hole)
            sentences[r["tag"]] = context[r["lhs"]][:at] + body + context[r["lhs"]][at + 1:]
    return sentences


def opening_cases() -> list[tuple[str, str, str]]:
    """(env, wording, rule tag): each sentence of `opening_sentences` asked with the auxiliary taken out, once for
    each `is` it has (the inverse of the question reader putting the auxiliary back in one gap, spec 2.2), in
    `speech` (a predicate with a verbalisation) and `unverbalised` (one without)."""
    raws = extra_environments()
    cases = {}
    for env, word in (("speech", "reviewed"), ("unverbalised", UNVERBALISED)):
        for tag, tokens in opening_sentences(raws[env], word).items():
            for i, t in enumerate(tokens):
                if t == "is":
                    cases.setdefault((env, f"Is {_join(tokens[:i] + tokens[i + 1:])}?"), tag)
    return [(env, wording, tag) for (env, wording), tag in cases.items()]


def extra_environments() -> dict[str, dict]:
    """The environments of the added cases; `speech` is Q1.4's."""
    from test_speech_acts import environment

    negative = environment().to_dict()
    negative["vocabulary"]["predicates"]["reviewed"]["negative_verbalisation"] = "{0} is not reviewed"
    named = environment().to_dict()
    for name in SPECIAL_NAMES:
        named["vocabulary"]["constants"][name] = {"sort": "service", "description": name}
    unverbalised = environment().to_dict()
    unverbalised["vocabulary"]["predicates"][UNVERBALISED] = {"arguments": ["service"], "description": UNVERBALISED}
    return {"speech": environment().to_dict(), "negative": negative, "names": named, "unverbalised": unverbalised}


def extra_cases() -> list[tuple[str, str, dict]]:
    """Environment/wording pairs missed by the original Cartesian corpus.

    Keep these outside Q1.4's corpus: that earlier batch's saved evidence is
    frozen.  Both spellings of service names, both subjects of a declared
    negative verbalisation, `reader_cases` and `opening_cases` exercise whole classes, not one reproducer.
    """
    raws = extra_environments()
    return ([("negative", f"Is {name} not reviewed?", raws["negative"]) for name in NEGATIVE_SUBJECTS]
            + [("names", f"Is {spelling} reviewed?", raws["names"])
               for name in SPECIAL_NAMES
               for spelling in (name, f'"{name}"')]
            + [(env, wording, raws[env]) for env, wording, _ in reader_cases()]
            + [(env, wording, raws[env]) for env, wording, _ in opening_cases()])


def augment(source: str, out: str) -> None:
    """Append the new cases to a saved base/head corpus using this checkout's parser.

    VE_AB_ROOT selects the base parser when recording base answers; the corpus
    and this script always come from the current checkout.
    """
    from ve.environment import Environment

    rows = json.loads(Path(source).read_text())
    keys = {(row["env"], row["wording"]) for row in rows}
    for env_name, wording, raw in extra_cases():
        if (env_name, wording) in keys:  # in Q1.4's corpus, or recorded by an earlier augment
            continue
        keys.add((env_name, wording))
        rows.append({"env": env_name, "wording": wording,
                     "outcome": speech_ab.outcome(Environment(raw), wording)})
    Path(out).write_text(json.dumps(rows, indent=1, sort_keys=True) + "\n")

GLOSS_PREDICATES = {name for name, _ in speech_ab.GLOSSES} | {"cat"}


def _named(r: dict) -> tuple[str, str] | None:
    """The name as the wording writes it and the constant the base read, for a base polar reading of one constant."""
    body = r["base"].get("content", {}).get("body")
    if r["base"].get("kind") != "question" or type(body) is not list or body[0] != "unary":
        return None
    return r["wording"].split(" ")[1], body[2][1]


def gloss(r: dict) -> bool:
    named = _named(r)
    return (r["class"] == "verdict" and named is not None and named[0] == named[1]
            and r["base"]["content"]["body"][1] in GLOSS_PREDICATES and r["head"].get("code") == "SyntaxError")


def folded(r: dict) -> bool:
    named = _named(r)
    return (r["class"] == "verdict" and named is not None and named[0] != named[1]
            and named[0].casefold() == named[1] and named[0] != named[1].capitalize()
            and r["head"].get("code") == "SyntaxError")


def quantified(r: dict) -> bool:
    word = r["wording"].split(" ")[1]
    body = r["head"].get("content", {}).get("body")
    return (r["class"] == "verdict" and r["env"] not in EXTRA_ENVS and word in ("every", "some")
            and r["wording"] == f"Is {word} service reviewed?"
            and r["base"].get("message") == f"UnknownAlternative: wording, {word}" and type(body) is list
            and body[0] == {"every": "forall", "some": "exists"}[word])


def negative(r: dict) -> bool:
    name = r["wording"].split()[1]
    return (r["class"] == "verdict" and r["env"] == "negative" and name in NEGATIVE_SUBJECTS
            and r["wording"] == f"Is {name} not reviewed?" and r["base"].get("code") == "SyntaxError"
            and r["head"].get("content", {}).get("body") == ["not", ["unary", "reviewed", ["const", name]]])


def _spelled(r: dict, quoted: bool) -> bool:
    """Item 2: the bare spelling goes from polar to `SyntaxError`, the quoted one from `InvalidInput` to polar."""
    name = r["wording"].removeprefix("Is ").removesuffix(" reviewed?").strip('"')
    if r["class"] != "verdict" or r["env"] != "names" or name not in SPECIAL_NAMES or r["wording"] != (
            f'Is "{name}" reviewed?' if quoted else f"Is {name} reviewed?"):
        return False
    atom = ["unary", "reviewed", ["const", name]]
    read, refused = (r["head"], r["base"]) if quoted else (r["base"], r["head"])
    return read.get("content", {}).get("body") == atom and refused.get("code") == (
        "InvalidInput" if quoted else "SyntaxError")


# The formula a determiner's question has over its predicate's atom (spec 2.2-2.4 as Lean reads it); a determiner
# the grammar gains and this table lacks fails the audit with a KeyError until its reading is recorded here.
QUANTIFIED = {"every": lambda atom: ["forall", "service", atom], "some": lambda atom: ["exists", "service", atom],
              "no": lambda atom: ["not", ["exists", "service", atom]]}


def _reads(r: dict, predicate: str) -> bool:
    """The head is the reading of `Is <subject> <predicate>?`: the atom of the name, or the determiner's formula."""
    subject = r["wording"].split(" ")[1]
    body = r["head"].get("content", {}).get("body")
    if subject in determiners():
        return body == QUANTIFIED[subject](["unary", predicate, ["var", 0]])
    return body == ["unary", predicate, ["const", subject]]


def determiner(r: dict) -> bool:
    word = r["wording"].split(" ")[1]
    return (r["class"] == "verdict" and r["env"] == "speech" and word in set(determiners()) - {"every", "some"}
            and r["wording"] == f"Is {word} service reviewed?"
            and r["base"].get("message") == f"UnknownAlternative: wording, {word}" and _reads(r, "reviewed"))


def unverbalised(r: dict) -> bool:
    return (r["class"] == "verdict" and r["env"] == "unverbalised" and (r["env"], r["wording"]) in _keys(
        reader_cases) and r["base"].get("code") in (
        "SyntaxError", "InvalidInput") and r["wording"].removesuffix("?").split()[-1].casefold() == UNVERBALISED
            and _reads(r, UNVERBALISED))


@functools.cache
def _keys(cases) -> frozenset[tuple[str, str]]:
    """The (env, wording) pairs of `reader_cases` or `opening_cases`, computed once per run."""
    return frozenset((env, wording) for env, wording, *_ in cases())


def opening(r: dict) -> bool:
    """Item 5 (class (d)): an `opening_cases` question outside `reader_cases` that the base refused and the head
    reads as a polar question; that the reading is `ve ask`'s is the test's to show
    (`test_every_opening_verdict_row_is_read_as_ve_ask_reads_it`)."""
    body = r["head"].get("content", {}).get("body")
    return (r["class"] == "verdict" and (r["env"], r["wording"]) in _keys(opening_cases) - _keys(reader_cases)
            and "error" in r["base"] and r["head"].get("kind") == "question" and type(body) is list)


# Each class, its decision (manage-agents/reviews/) and its count in the recorded delta.
CLASSES = {"gloss": gloss, "folded": folded, "quantified": quantified, "negative": negative,
           "bare_name": lambda r: _spelled(r, False), "quoted_name": lambda r: _spelled(r, True),
           "determiner": determiner, "unverbalised": unverbalised, "opening": opening}
DECIDED = {"gloss": 10, "folded": 3, "quantified": 6,  # dri-decisions-20261027-featureplan-gates.md item 4
           "negative": len(NEGATIVE_SUBJECTS), "bare_name": len(SPECIAL_NAMES),  # dri-decisions-20261028-q1-4b.md
           "quoted_name": len(SPECIAL_NAMES), "determiner": 1, "unverbalised": 8,  # items 1, 2, 2, 3, 4 and 5
           "opening": 50}  # item 5


def check(delta_path: str) -> int:
    rows = json.loads(Path(delta_path).read_text())["rows"]
    counts = {name: sum(map(test, rows)) for name, test in CLASSES.items()}
    refusals = [r for r in rows if r["class"] in ("class", "wording")]
    bad = [r for r in rows if r["class"] == "lint"
           or r["class"] == "verdict" and sum(test(r) for test in CLASSES.values()) != 1
           or r in refusals and not speech_ab.order_o1(r) and not speech_ab.keeps(r)]
    for r in bad:
        print("fails:", r["class"], r["env"], repr(r["wording"]), r["base"].get("message"), "->",
              r["head"].get("message"))
    o1 = [r for r in refusals if speech_ab.order_o1(r)]
    print(json.dumps({"rows": len(rows), **counts, "O1": len(o1), "R1": len(refusals) - len(o1),
                      "failing": len(bad)}))
    return 1 if bad or counts != DECIDED else 0


if __name__ == "__main__":
    if sys.argv[1:2] == ["augment"] and len(sys.argv) == 4:
        augment(sys.argv[2], sys.argv[3])
    elif sys.argv[1:2] not in (["check"], ["audit"]) or len(sys.argv) != 3:
        raise SystemExit(__doc__)
    else:
        raise SystemExit(check(sys.argv[2]))
