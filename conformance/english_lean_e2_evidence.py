"""The E2.5 evidence of English in Lean (docs/spec/english-lean-E2-PLAN.md E2.5 and GE2; spec 2.10).

    python -m conformance.english_lean_e2_evidence [--part NAME ...] [--workers N] [--per-config N]

Every part runs at the head, with Lean deciding English admission. Python's reader (`ve.english._python_reading`,
the hand parser, the Lark audit and the typed check) is the comparator, run beside it, never deciding. Parts:

* ``g3``: the comparison at the dispatched boundary (spec 2.10; S3 2.11's correspondence: verdict, formulas,
  canonical text, marks, witness count) on the sealed streams of every corpus configuration (the round-trip
  stream of `conformance.english_surface`, its seed per configuration, and its documents of five sentences),
  on fourteen fresh date seeds of the same streams, and on the use-case environments; Lean's formulas are also
  compared with the formula each text was rendered from. Coverage: the fixed rules and lexical families of
  every profile's `english.grammar` export that no compared text reached.
* ``reverse``: texts sampled from each configuration's `english.grammar` export, with spacing and word-split
  mutants; every text Lean reads (`one`) must be read by Python with the same formulas.
* ``mutation``: the lexicon mutation replay: mutants of each configuration's lexicon (`english_lean_lexicon`'s
  one- and two-fault mutants); a mutant V1 to V6 accept must change no corpus formula.
* ``parity``: the port against Python's `EnglishVocabulary`, symbol by symbol, on every corpus environment and
  on the mutation set of spec 2.10 (each wording of 8.1, the nouns of lx27, the display forms of lx28, the
  generated names under `alternatives@0` and `risk@0`): Python's lexicon against the `policy` the
  `english.grammar` export names, or the V1 to V6 failure that refuses it.
* ``overlay``: the overlay check against Python's producer with its refusals on: every corpus overlay and
  overlay mutants over every corpus environment; raise against no raise, and the site (O1 to O3). A mutant
  `display_environment` refuses is recorded, not compared.
* ``latency``: the service budgets of GE2 item 9.

The result is `conformance/english-lean/e2-evidence.json`; `docs/spec/english-lean-e2-report.md` and
`docs/lean-first/e2/DELTA.md` cite it, and `tests/test_english_e2_report.py` derives their numbers from it.
"""
from __future__ import annotations

import argparse
from collections import Counter
import datetime
import hashlib
import json
import multiprocessing
import os
from pathlib import Path
import random
import re
import statistics
import subprocess
import sys
import time
import warnings

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "conformance/english-lean/e2-evidence.json"
FORMAT = "ve.english-lean-e2-evidence@1"
PARTS = ("g3", "reverse", "mutation", "parity", "overlay", "latency")
FRESH_SEEDS = 14

# Filled before the workers fork: (name, env, options, words) per configuration.
CONFIGS: list = []


def _setup() -> None:
    warnings.simplefilter("ignore")
    os.environ["VE_ENGLISH_COMPARATOR"] = "0"  # the harness runs the comparator itself, record by record


def configurations() -> list:
    """Every corpus environment of the lexicon report (the 17 round-trip configurations, then every use-case
    environment, with its overlay), with Python's producer as the admission path builds it."""
    from conformance.english_lean_lexicon import environments
    from ve.english import EnglishVocabulary
    out = []
    for name, env, options in environments():
        try:
            words = EnglishVocabulary(env, _defer_overlay_refusals=True, **options)
        except Exception as exc:  # display_environment refuses: recorded by the parity part
            out.append((name, env, options, exc))
            continue
        out.append((name, env, options, words))
    return out


# ------------------------------------------------------------------ the two readers

def python_outcome(item):
    """Python's public outcome for one text (spec 2.11 comparison form), computed in a worker."""
    from ve import english as EN
    from ve.backends import english_lean as L
    from ve.errors import AmbiguousDerivation, ResourceLimit
    index, text = item
    _, env, options, words = CONFIGS[index]
    try:
        reading = EN._python_reading(env, text, words, options)
    except Exception as exc:  # every outcome is classified, internal errors included
        cls = L.python_class(exc)
        out = {"verdict": L._verdict(cls), "code": cls, "message": str(exc)[:300]}
        if isinstance(exc, AmbiguousDerivation):
            out["witnesses"] = 2
        if isinstance(exc, ResourceLimit) and str(exc) == L.WALL_CLOCK:
            out["excluded"] = "wall-clock ResourceLimit"
        return out
    marked = set(reading.conclusions)
    if any(not [j for j in range(i) if j not in marked] for i in reading.conclusions):
        return {"verdict": "rejected", "code": "SyntaxError", "message": L.NO_PREMISE}
    return {"verdict": "accepted", "code": "accepted", **reading.comparison()}


def lean_outcomes(index: int, texts: list[str], lexicon: dict | None = None) -> list[dict]:
    """Lean's checked answer for each text, as the relay reads it (or `CheckerUnavailable`)."""
    from ve.backends import english_lean as L
    from ve.backends import relay
    from ve.english_grammar import lexicon_id
    _, env, options, words = CONFIGS[index]
    out = []
    for start in range(0, len(texts), 400):
        chunk = texts[start:start + 400]
        cases = []
        for k, text in enumerate(chunk):
            case = {**L.request(env, text, words, options), "id": f"t{start + k}"}
            if lexicon is not None:
                case["lexicon"] = lexicon
            cases.append(case)
        rows = relay.rows("english.read", cases)
        for text, case, row in zip(chunk, cases, rows, strict=True):
            if row.get("status") != "ok":
                out.append({"status": "unavailable", "error": str(row.get("error", row))[:300]})
                continue
            expected = L.identities(env, text, words, case["lexicon"])
            expected["lexicon_id"] = lexicon_id(case["lexicon"])
            problem = L.response_problem(row["result"], expected, env, text)
            if problem:
                out.append({"status": "unavailable", "error": problem})
                continue
            out.append({"status": row["result"]["status"], "reading": L.LeanReading(row["result"], env, text)})
    return out


def compare(left: dict, lean: dict) -> tuple[list[str], dict]:
    from ve.backends import dispatch
    if lean["status"] == "unavailable":
        right = {"verdict": "unavailable", "code": "CheckerUnavailable"}
    else:
        right = lean["reading"].comparison(left["code"])
    compared = {k: v for k, v in left.items() if k not in ("message", "excluded")}  # as shadow_record compares
    classes = [] if "excluded" in left else dispatch._classes(compared, right)
    return classes, right


def _summary(right: dict) -> dict:
    return {k: right[k] for k in ("verdict", "code", "formulas", "conclusions", "witnesses") if k in right}


# ------------------------------------------------------------------ g3

class Stalled(Exception):
    """The formula generator found no formula within its time limit."""


def _bounded(fn, seconds: float = 2.0):
    """`fn()`, or `Stalled` after `seconds` (the generator of `english_surface` can search without end on an
    environment it was not written for)."""
    import signal

    def stop(_signum, _frame):
        raise Stalled()
    previous = signal.signal(signal.SIGALRM, stop)
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        return fn()
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous)


STALLED: dict[str, int] = {}


def streams(index: int, per_config: int, documents: int, fresh: list[int],
            fresh_count: int = 0) -> list[tuple[str, str, list | None]]:
    """(stream, text, the formulas it was rendered from) for one configuration: the sealed stream (the audit's
    seed), its documents of five sentences, and each fresh seed's stream. A draw that stalls ends its stream
    (counted in `STALLED`)."""
    from conformance.english_surface import SEED, directed_formulas, random_formula as unbounded
    from ve import ast
    from ve.english import EnglishTraversal
    name, env, options, words = CONFIGS[index]
    out = []

    def random_formula(rng, env, depth):
        return _bounded(lambda: unbounded(rng, env, depth))

    def render(formula):
        return EnglishTraversal(env, words).render(formula) + "."

    def stream(label, rng, count, directed=()):
        seen, made, queue = set(), 0, list(directed)
        draws = 0
        while made < count and draws < count * 20:
            draws += 1
            try:
                formula = queue.pop(0) if queue else random_formula(rng, env, rng.randrange(2, 9))
                ast.check_formula(env, formula)
                text = render(formula)
            except Stalled:
                STALLED[name] = STALLED.get(name, 0) + 1
                return
            except Exception:
                continue
            if formula in seen:
                continue
            seen.add(formula)
            out.append((label, text, [ast._to_data(formula)]))
            made += 1

    try:
        directed = list(dict.fromkeys(_bounded(lambda: list(directed_formulas(env, words)), 20.0)))
    except Exception:
        directed = []
    stream("sealed", random.Random(SEED + index), per_config, directed)
    rng = random.Random(SEED + 100_000 + index)
    for _ in range(documents):
        formulas, tries = [], 0
        while len(formulas) < 5 and tries < 100:
            tries += 1
            try:
                formula = random_formula(rng, env, rng.randrange(6, 10))
                ast.check_formula(env, formula)
                formulas.append(formula)
            except Stalled:
                STALLED[name] = STALLED.get(name, 0) + 1
                tries = 100
            except Exception:
                continue
        if len(formulas) < 5:
            break
        try:
            text = "".join(render(f) + "\n" for f in formulas)
        except Exception:
            continue
        out.append(("documents", text, [ast._to_data(f) for f in formulas]))
    for seed in fresh:
        stream(f"fresh:{seed}", random.Random(seed * 1000 + index), fresh_count)
    return out


def round_trip(name: str) -> bool:
    """One of the 17 round-trip configurations of `english_surface` (the generated streams), not a use case."""
    return not name.startswith("usecases/")


def part_g3(pool, per_config: int, per_usecase: int, fresh_count: int, documents: int) -> dict:
    today = int(datetime.date.today().strftime("%Y%m%d"))
    fresh = [today * 100 + k for k in range(FRESH_SEEDS)]
    rows, differences, roundtrip, coverage_tags = Counter(), [], [], {}
    by_config = {}
    for index, (name, env, options, words) in enumerate(CONFIGS):
        if isinstance(words, Exception):
            continue
        items = streams(index, per_config if round_trip(name) else per_usecase, documents,
                        fresh if round_trip(name) else [], fresh_count)
        texts = [text for _, text, _ in items]
        python = pool.map(python_outcome, [(index, t) for t in texts], chunksize=32)
        lean = lean_outcomes(index, texts)
        counts = Counter()
        for (stream, text, formulas), left, right_raw in zip(items, python, lean, strict=True):
            classes, right = compare(left, right_raw)
            kind = stream.split(":")[0]
            counts[f"{kind}:texts"] += 1
            counts[f"{kind}:{'agree' if not classes else 'differ'}"] += 1
            if "excluded" in left:
                counts["excluded"] += 1
            if right_raw["status"] == "one":
                for tree in right_raw["reading"].response["derivation"]:
                    for node in tree:
                        coverage_tags.setdefault(name, set()).add(node[0])
                if right_raw["reading"].response["ast"] != formulas:
                    roundtrip.append({"config": name, "stream": stream, "text": text,
                                      "rendered": formulas, "lean": right_raw["reading"].response["ast"]})
            elif left["verdict"] == "accepted":
                roundtrip.append({"config": name, "stream": stream, "text": text, "rendered": formulas,
                                  "lean": right_raw["status"]})
            if classes:
                differences.append({"config": name, "stream": stream, "text": text, "classes": classes,
                                    "python": {k: left[k] for k in ("verdict", "code", "message", "formulas")
                                               if k in left},
                                    "lean": {"status": right_raw["status"], **_summary(right),
                                             **({"lean_code": right_raw["reading"].response.get("code")}
                                                if right_raw["status"] not in ("one", "unavailable") else {})}})
        by_config[name] = dict(sorted(counts.items()))
        rows.update(counts)
        print(f"g3 {name}: {by_config[name]}", file=sys.stderr, flush=True)
    coverage = coverage_report(coverage_tags)
    return {"fresh_seeds": fresh, "per_config": per_config, "per_usecase": per_usecase,
            "fresh_per_seed": fresh_count, "documents_per_config": documents,
            "generator_stalled": dict(sorted(STALLED.items())),
            "texts": sum(v for k, v in rows.items() if k.endswith(":texts")),
            "agree": sum(v for k, v in rows.items() if k.endswith(":agree")),
            "differ": sum(v for k, v in rows.items() if k.endswith(":differ")),
            "excluded": rows["excluded"], "by_config": by_config,
            "roundtrip_failures": roundtrip, "differences": differences, "coverage": coverage}


def grammar_export(index: int, lexicon: dict | None = None, overlay_case: dict | None = None) -> dict:
    from ve.backends import english_lean as L
    from ve.backends import relay
    _, env, options, words = CONFIGS[index]
    case = L.request(env, "x.", words, options)
    case = {k: v for k, v in case.items() if k not in ("source", "mode", "cap")}
    case["id"] = "english.grammar"
    if lexicon is not None:
        case["lexicon"] = lexicon
    if overlay_case is not None:
        case.update(overlay_case)
    [row] = relay.rows("english.grammar", [case])
    return row


def coverage_report(tags_by_config: dict) -> dict:
    """The fixed rules and lexical families of each configuration's grammar that no compared text reached."""
    out = {}
    for index, (name, env, options, words) in enumerate(CONFIGS):
        if isinstance(words, Exception) or name not in tags_by_config:
            continue
        row = grammar_export(index)
        if row.get("status") != "ok" or "rules" not in row["result"]:
            out[name] = {"error": str(row)[:300]}
            continue
        rules = row["result"]["rules"]
        fixed = {r["tag"] for r in rules if not r["act"].split(" ", 1)[0] in LEXICAL_ACTS}
        families = {r["tag"].split(".", 1)[0] for r in rules if r["act"].split(" ", 1)[0] in LEXICAL_ACTS}
        seen = tags_by_config[name]
        out[name] = {"fixed_rules": len(fixed), "fixed_unreached": sorted(fixed - seen),
                     "families": len(families),
                     "families_unreached": sorted(families - {t.split(".", 1)[0] for t in seen})}
    return out


# `lexActText`'s first words (Run.lean): the actions of lexical rules.
LEXICAL_ACTS = {"pred", "relSubject", "relObject", "noun", "label", "const", "adjective", "natSubject", "copulaRel",
                "owner", "relation", "attribute", "attributeProperty", "guard", "altHead", "termOther"}


# ------------------------------------------------------------------ reverse

def sample_text(export: dict, rng: random.Random, depth: int = 14) -> str | None:
    """A text the exported grammar derives: a random derivation from the start symbol, bounded in depth."""
    rules: dict[str, list[list]] = {}
    for rule in export["rules"]:
        rules.setdefault(rule["lhs"], []).append(rule["rhs"])
    names = export["nonterminals"]
    height = {n: None for n in names}
    changed = True
    while changed:  # the least derivation height of each nonterminal
        changed = False
        for lhs, alternatives in rules.items():
            for rhs in alternatives:
                hs = [0 if type(s) is not dict or "n" not in s else height.get(s["n"]) for s in rhs]
                if all(h is not None for h in hs):
                    h = 1 + max(hs, default=0)
                    if height.get(lhs) is None or h < height[lhs]:
                        height[lhs], changed = h, True
    start = names[0]
    if height.get(start) is None:
        return None
    tokens: list[tuple[str, bool, bool]] = []

    def expand(symbol, level):
        if len(tokens) > 120:
            raise RecursionError
        if type(symbol) is str:
            tokens.append((symbol, False, False))
        elif "n" in symbol:
            alternatives = [r for r in rules.get(symbol["n"], ()) if all(
                type(s) is not dict or "n" not in s or height.get(s["n"]) is not None for s in r)]
            if level >= depth:
                best = min(1 + max([height[s["n"]] for s in r if type(s) is dict and "n" in s], default=0)
                           for r in alternatives)
                alternatives = [r for r in alternatives if 1 + max(
                    [height[s["n"]] for s in r if type(s) is dict and "n" in s], default=0) == best]
            for s in rng.choice(alternatives):
                expand(s, level + 1)
        elif "c" in symbol:
            tokens.append((symbol["c"], False, False))
        elif "kwMid" in symbol:
            tokens.append((symbol["kwMid"], False, False))
        elif "w" in symbol:
            tokens.append((symbol["w"], False, False))
        elif "q" in symbol:
            tokens.append((json.dumps(symbol["q"]), False, False))
        elif "label" in symbol:
            tokens.append((f"{symbol['label']}{symbol['index']}", False, False))
        elif "num" in symbol:
            tokens.append((symbol["num"], False, False))
        elif "p" in symbol:
            tokens.append((symbol["p"], symbol.get("before", False), symbol.get("after", False)))
        elif symbol.get("cls") == "numeral":
            tokens.append((str(rng.randrange(0, 50)), False, False))
        elif symbol.get("cls") == "label":
            tokens.append((f"{symbol['letter']}{rng.randrange(1, 4)}", False, False))

    try:
        expand({"n": start}, 0)
    except (RecursionError, ValueError, IndexError, KeyError):
        return None
    text = ""
    for k, (word, glued_before, glued_after) in enumerate(tokens):
        punct = not re.match(r"[A-Za-z0-9\"]", word)
        if k and not (punct and not glued_before and word in ",;:)") and not (punct and glued_before) \
                and not (k and tokens[k - 1][2]):
            text += " "
        text += word
    if not text:
        return None
    return text[0].upper() + text[1:] + "."


def mutants_of(text: str, rng: random.Random) -> list[tuple[str, str]]:
    words = text[:-1].split(" ")
    out = [("double-space", text.replace(" ", "  ", 1)), ("space-before-period", text[:-1] + " .")]
    if len(words) > 1:
        k = rng.randrange(1, len(words))
        out.append(("glue", " ".join(words[:k - 1] + [words[k - 1] + words[k]] + words[k + 1:]) + "."))
    long = [k for k, w in enumerate(words) if len(w) > 4 and w.isalpha()]
    if long:
        k = rng.choice(long)
        cut = rng.randrange(2, len(words[k]) - 1)
        out.append(("word-split", " ".join(words[:k] + [words[k][:cut], words[k][cut:]] + words[k + 1:]) + "."))
    return out


def part_reverse(pool, samples: int) -> dict:
    """Rejection sampling: `samples` derivations of each configuration's exported grammar are read by Lean;
    those it reads (`one`) and their spacing and word-split mutants are read by Python as well, and every
    text Lean reads must be read by Python with the same formulas (GE2 item 2, the reverse corpus)."""
    counts, findings = Counter(), []
    for index, (name, env, options, words) in enumerate(CONFIGS):
        if isinstance(words, Exception):
            continue
        row = grammar_export(index)
        if row.get("status") != "ok" or "rules" not in row["result"]:
            counts["no-export"] += 1
            continue
        rng = random.Random(20261007 + index)
        sampled = [text for text in (sample_text(row["result"], rng) for _ in range(samples)) if text]
        counts["sample:texts"] += len(sampled)
        read = lean_outcomes(index, sampled)
        items = []
        for text, answer in zip(sampled, read, strict=True):
            counts[f"sample:lean-{answer['status']}"] += 1
            if answer["status"] == "one":
                items.append(("sample", text, answer))
                for kind, mutant in mutants_of(text, rng):
                    items.append((kind, mutant, None))
        pending = [k for k, item in enumerate(items) if item[2] is None]
        for k, answer in zip(pending, lean_outcomes(index, [items[k][1] for k in pending]), strict=True):
            kind, text, _ = items[k]
            counts[f"{kind}:texts"] += 1
            counts[f"{kind}:lean-{answer['status']}"] += 1
            items[k] = (kind, text, answer)
        accepted = [(kind, text, answer) for kind, text, answer in items if answer["status"] == "one"]
        python = pool.map(python_outcome, [(index, text) for _, text, _ in accepted], chunksize=16)
        for (kind, text, answer), left in zip(accepted, python, strict=True):
            classes, right = compare(left, answer)
            counts[f"{kind}:lean-one-python-{'agree' if not classes else 'differ'}"] += 1
            if classes:
                findings.append({"config": name, "kind": kind, "text": text, "classes": classes,
                                 "python": {k: left[k] for k in ("code", "message", "formulas") if k in left},
                                 "lean": answer["reading"].response["ast"]})
        print(f"reverse {name}: {len(sampled)} sampled, {len(accepted)} read by Lean", file=sys.stderr, flush=True)
    return {"samples_per_config": samples, "counts": dict(sorted(counts.items())),
            "lean_accepts_python_differs": findings}


# ------------------------------------------------------------------ mutation replay

def part_mutation(texts_per_config: int) -> dict:
    from conformance.english_lean_lexicon import lexical_view, mutants
    from ve.english_grammar import export
    counts, changed = Counter(), []
    for index, (name, env, options, words) in enumerate(CONFIGS):
        if isinstance(words, Exception):
            continue
        texts = [t for _, t, _ in streams(index, texts_per_config, 0, [])]
        base = lean_outcomes(index, texts)
        lexicon = export(words)
        try:
            view = lexical_view(words)
        except Exception:
            counts["no-view"] += 1
            continue
        for label, mutant in mutants(view, lexicon):
            counts["mutants"] += 1
            probe = lean_outcomes(index, texts[:1], mutant)  # V1 to V6 refuse a mutant before any text
            if probe and probe[0]["status"] == "invalidGrammar":
                counts["refused"] += 1
                continue
            answers = probe + lean_outcomes(index, texts[1:], mutant)
            if all(a["status"] == "invalidGrammar" for a in answers):
                counts["refused"] += 1
                continue
            if any(a["status"] == "unavailable" for a in answers):
                counts["unavailable"] += 1
                continue
            counts["accepted"] += 1
            for text, before, after in zip(texts, base, answers, strict=True):
                if after["status"] != "one":
                    counts["texts:lost-or-unread"] += 1
                    continue
                if before["status"] == "one" and \
                        before["reading"].response["ast"] == after["reading"].response["ast"]:
                    counts["texts:same"] += 1
                    continue
                counts["texts:changed"] += 1
                changed.append({"config": name, "mutant": label, "text": text,
                                "before": before["reading"].response["ast"] if before["status"] == "one"
                                else before["status"], "after": after["reading"].response["ast"]})
        print(f"mutation {name}: {dict(counts)}", file=sys.stderr, flush=True)
    return {"texts_per_config": texts_per_config, "counts": dict(sorted(counts.items())), "changed": changed}


# ------------------------------------------------------------------ port parity

# The wordings of spec 8.1, by arity (lx15 to lx22), and the nouns and display forms of lx27 and lx28.
WORDINGS = {1: ["{0} never fails", "{0} is legacy", "{0} is archived", "{0} is undeployed", "{0} is recorded",
                "{0} is logged", "{0} is same", "{0} is v1.2 compliant", "{0} is compliant", "{0} is checked daily",
                "{0} is checked", "{0} runs", "{0} is service ready", "{0} is holds", "{0} is fully avoidable",
                "{0} is reviewed"],
            2: ["{0} is managed by {1}", "{0} manages {1}", "{0} reports to {1}", "{0} belongs to {1}",
                "{0} manage {1}", "{0} supervises abcdefghij abcdefghij abcdefghij abcdefghij abcdefghij "
                "abcdefghij {1}", "{0} denies the equal protection of the laws to {1}", "{0} relates X1 {1}",
                "{0} relates {1}", "{0} voted for {1}", "{0} was appointed by {1}", "{0} undermines {1}",
                "{0} likes {1}", "{0} risks {1}", "{0} might lead to {1}"]}
NOUNS = ["every item", "deployed service", "item", "severity", "level"]
DISPLAYS = ["hence", "the api", "api", "the legacy"]


def _symbols(env) -> tuple[list, list, list]:
    preds = [(p, len(d.arguments)) for p, d in env.predicates.items()]
    return preds, list(env.sorts), list(env.constants)


def environment_mutants(name: str, env) -> list[tuple[str, dict]]:
    """Spec 2.10's mutation set over one environment: each predicate's wording replaced in turn by each 8.1
    wording of its arity (at most three predicates per arity), each sort's noun and each constant's display form
    replaced by lx27's and lx28's, and under `alternatives@0` and `risk@0` wordings and nouns made of the
    generated names."""
    raw = env.to_dict()
    out = []
    preds, sorts, consts = _symbols(env)
    by_arity: dict[int, list] = {}
    for p, k in preds:
        by_arity.setdefault(k, []).append(p)
    generated = []
    if "alternatives@0" in env.profiles:
        generated += ["avoidable", "unavoidable", "allows", "prevents"]
    risk = (raw.get("risk") or {}).get("severity") or {}
    generated += list(risk.get("classes", ()))
    for k, names in by_arity.items():
        for p in names[:3]:
            for wording in WORDINGS.get(k, ()) + [f"{{0}} is fully {g}" for g in generated if k == 1]:
                data = json.loads(json.dumps(raw))
                data["vocabulary"]["predicates"][p]["verbalisation"] = wording
                data["vocabulary"]["predicates"][p].pop("negative_verbalisation", None)
                out.append((f"{name}: {p} := {wording}", data))
    for s in sorts[:3]:
        for noun in NOUNS + ([risk["sort"]] if risk.get("sort") else []):
            data = json.loads(json.dumps(raw))
            data["vocabulary"]["sorts"][s]["verbalisation"] = {"singular": noun, "plural": noun + "s"}
            out.append((f"{name}: sort {s} := {noun}", data))
    return out


def parity_of(env, options) -> dict:
    """Python's selection against the port's (the `policy` of the `english.grammar` export), symbol by symbol."""
    from ve.backends import english_lean as L
    from ve.backends import relay
    from ve.english import EnglishVocabulary
    from ve.english_grammar import export
    try:
        words = EnglishVocabulary(env, _defer_overlay_refusals=True, **options)
    except Exception as exc:
        return {"status": "producer-refuses", "error": f"{type(exc).__name__}: {exc}"[:200]}
    case = {k: v for k, v in L.request(env, "x.", words, options).items() if k not in ("source", "mode", "cap")}
    case["id"] = "english.grammar"
    [row] = relay.rows("english.grammar", [case])
    if row.get("status") != "ok":
        return {"status": "boundary", "error": str(row.get("error"))[:200]}
    result = row["result"]
    if result.get("status") == "invalidGrammar":
        failure = result.get("failure", [])
        return {"status": "v6" if failure[:1] == ["V6"] else "v1-v5", "failure": failure}
    lexicon = export(words)
    policy = result["policy"]
    mismatches = []
    for field, lean_field in (("wordings", "wordings"), ("negatives", "negatives"), ("nouns", "nouns"),
                              ("spellings", "spellings")):
        python = {k: v for k, v in lexicon[field]}
        lean = {k: v for k, v in policy[lean_field]}
        for key in sorted(set(python) | set(lean)):
            if python.get(key) != lean.get(key):
                mismatches.append([field, key, python.get(key), lean.get(key)])
    return {"status": "compared", "mismatches": mismatches}


def _parity_config(index: int) -> tuple[Counter, list]:
    from ve import Environment
    _setup()
    name, env, options, words = CONFIGS[index]
    counts, findings = Counter(), []
    rows = [(name, env, options)]
    for label, data in environment_mutants(name, env):
        try:
            rows.append((label, Environment(data), options if "vocabulary" not in options else {}))
        except Exception:
            counts["mutant-refused-by-Environment"] += 1
    for label, mutant_env, mutant_options in rows:
        result = parity_of(mutant_env, mutant_options)
        kind = "corpus" if label == name else "mutant"
        counts[f"{kind}:{result['status']}"] += 1
        if result["status"] == "compared":
            counts[f"{kind}:symbols-mismatched"] += len(result["mismatches"])
            if result["mismatches"]:
                findings.append({"environment": label, **result})
        elif result["status"] in ("v6", "v1-v5", "boundary"):
            findings.append({"environment": label, **result})
    return counts, findings


def _merged(pool, worker, part: str) -> dict:
    """Run `worker` on every configuration in the pool, merging its counts and findings in configuration order."""
    counts, findings = Counter(), []
    for index, (more, found) in enumerate(pool.imap(worker, range(len(CONFIGS)))):
        counts.update(more)
        findings += found
        print(f"{part} {CONFIGS[index][0]}: {dict(counts)}", file=sys.stderr, flush=True)
    return {"counts": dict(sorted(counts.items())), "findings": findings}


def part_parity(pool) -> dict:
    return _merged(pool, _parity_config, "parity")


# ------------------------------------------------------------------ overlay parity

SITES = (("Duplicate English wording", "O1"), ("reuses a risk@0 wording", "O2"), ("template linter", "O3"))


def overlay_mutants(name: str, env, options) -> list[tuple[str, dict]]:
    """Spec 2.10's overlay mutants: one entry replaced or added: a predicate entry with an 8.1 wording, with
    such a wording and a negative that is not its negation, with a risk template under `risk@0`, or with another
    predicate's wording; a sort entry with lx27's nouns; a constant entry from lx28."""
    base = options.get("vocabulary") or {"format": "ve.english-vocabulary@1", "environment_id": env.environment_id,
                                         "sorts": {}, "predicates": {}, "constants": {}}
    preds, sorts, consts = _symbols(env)
    out = []

    def with_entry(field, key, value):
        overlay = json.loads(json.dumps(base))
        overlay.setdefault(field, {})[key] = value
        return overlay
    for p, k in preds[:4]:
        for wording in WORDINGS.get(k, ())[:8]:
            out.append((f"{name}: {p} -> {wording}", with_entry("predicates", p, {"verbalisation": wording,
                                                                                  "suggested": False})))
        if k in (1, 2):
            first = WORDINGS[k][0]
            out.append((f"{name}: {p} -> {first} + bad negative", with_entry(
                "predicates", p, {"verbalisation": first, "negative_verbalisation": "{0} is never checked",
                                  "suggested": False})))
        others = [q for q, kq in preds if kq == k and q != p and env.predicates[q].verbalisation]
        if others:
            out.append((f"{name}: {p} -> {others[0]}'s wording", with_entry(
                "predicates", p, {"verbalisation": env.predicates[others[0]].verbalisation, "suggested": False})))
    for s in sorts[:2]:
        for noun in NOUNS[:3]:
            out.append((f"{name}: sort {s} -> {noun}", with_entry(
                "sorts", s, {"verbalisation": {"singular": noun, "plural": noun + "s"}, "suggested": False})))
    for c in consts[:2]:
        for display in DISPLAYS[:3]:
            out.append((f"{name}: constant {c} -> {display}", with_entry("constants", c, {"verbalisation": display})))
    return out


def _overlay_config(index: int) -> tuple[Counter, list]:
    from ve.backends import english_lean as L
    from ve.backends import relay
    from ve.english import EnglishVocabulary
    from ve.errors import VEError
    _setup()
    name, env, options, words = CONFIGS[index]
    counts, findings = Counter(), []
    rows = ([(name, options["vocabulary"])] if "vocabulary" in options else []) + \
        overlay_mutants(name, env, options)
    for label, overlay in rows:
        kind = "corpus" if label == name else "mutant"
        try:
            EnglishVocabulary(env, vocabulary=overlay)
            python = None
        except VEError as exc:
            python = next((site for text, site in SITES if text in str(exc)), "display_environment")
        if python == "display_environment":
            counts[f"{kind}:display_environment-refuses"] += 1  # refused before any Lean call (ov11)
            continue
        try:
            deferred = EnglishVocabulary(env, vocabulary=overlay, _defer_overlay_refusals=True)
        except VEError:
            counts[f"{kind}:display_environment-refuses"] += 1
            continue
        case = {k: v for k, v in L.request(env, "x.", deferred, {"vocabulary": overlay}).items()
                if k not in ("source", "mode", "cap")}
        case["id"] = "english.grammar"
        [row] = relay.rows("english.grammar", [case])
        result = row.get("result", {})
        lean = result.get("failure", [None])[0] if result.get("code") == "InvalidOverlay" else None
        counts[f"{kind}:compared"] += 1
        if python == lean:
            counts[f"{kind}:agree"] += 1
            counts[f"{kind}:site:{python}"] += 1
        else:
            counts[f"{kind}:differ"] += 1
            findings.append({"overlay": label, "python": python, "lean": lean,
                             "lean_result": {k: result[k] for k in ("status", "code", "failure", "fault")
                                             if k in result} if row.get("status") == "ok"
                             else str(row.get("error"))[:200]})
    return counts, findings


def part_overlay(pool) -> dict:
    return _merged(pool, _overlay_config, "overlay")


# ------------------------------------------------------------------ latency

def _timed(fn, repeat: int = 1) -> float:
    best = []
    for _ in range(repeat):
        start = time.perf_counter()
        fn()
        best.append(time.perf_counter() - start)
    return min(best)


def _case_json(env, words, options) -> dict:
    from ve.backends import english_lean as L
    case = {k: v for k, v in L.request(env, "x.", words, options).items() if k not in ("source", "mode", "cap")}
    return {**case, "id": "english.grammar"}


def bench_policy(case: dict, repetitions: int = 5) -> dict:
    """The compiled bench's least CPU times of V6, V1 to V5 and grammar preparation for one case."""
    import tempfile
    bench = ROOT / "lean/.lake/build/bin/ve_english_lean_bench"
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as handle:
        json.dump(case, handle)
    done = subprocess.run([str(bench), "--policy", handle.name, str(repetitions)], capture_output=True, text=True,
                          timeout=600)
    os.unlink(handle.name)
    if done.returncode != 0:
        return {"error": done.stderr.strip()[-300:]}
    return json.loads(done.stdout)


def bluedot_english() -> dict:
    """S2 spec 2.15's owed budget: the BlueDot document's English through `english.read`, warm. Its formula units
    are rendered with Python's renderer (the first candidate Lean reads back) and read as one text, one request;
    `check_document` of the document reads no English (its units are strict), so it is not this measure."""
    from ve import ast
    from ve.backends import english_lean as L
    from ve.backends import relay
    from ve.document import load_document
    from ve.english import EnglishTraversal, EnglishVocabulary
    path = ROOT / "usecases/bluedot-grant/document.ve.md"
    doc = load_document(path)
    env = doc["environment"]
    words = EnglishVocabulary(env)
    sentences = []
    for unit in doc["units"]:
        if not isinstance(unit.get("content"), list):
            continue
        try:
            formula = ast.formula_from_data(env, unit["content"])
        except Exception:
            continue
        for settings in ({}, {"avoid_negative_universal": True},
                         {"avoid_negative_universal": True, "word_markers": True}):
            sentence = EnglishTraversal(env, words, **settings).render(formula) + "."
            [row] = relay.rows("english.read", [{**L.request(env, sentence, words, {}), "id": "b"}])
            if row.get("result", {}).get("status") == "one":
                sentences.append(sentence)
                break
    # The reader's text limit is 10,000 characters (`textTooLong`): the document is read in the fewest texts
    # under it, each one request.
    texts, current = [], []
    for sentence in sentences:
        if current and len("\n".join(current + [sentence])) > 9500:
            texts.append("\n".join(current))
            current = []
        current.append(sentence)
    if current:
        texts.append("\n".join(current))
    cases = [{**L.request(env, text, words, {}), "id": f"bluedot{k}"} for k, text in enumerate(texts)]
    statuses = []

    def read_all():
        statuses[:] = [relay.rows("english.read", [case])[0].get("result", {}).get("status") for case in cases]
    ms = 1000 * min(_timed(read_all) for _ in range(5))
    return {"path": str(path.relative_to(ROOT)), "sentences": len(sentences),
            "tokens": sum(len(re.findall(r"\S+", text)) for text in texts), "requests": len(texts),
            "ms": round(ms, 1), "budget": 1000, "statuses": sorted(set(statuses))}


def part_latency() -> dict:
    """GE2 item 9 on the service (wall clock of one request through the relay, least of five where repeated)
    and, for V6 at 256 predicates, the compiled bench's CPU time."""
    from ve import Environment
    from ve.backends import english_lean as L
    from ve.backends import relay
    from ve.english import EnglishVocabulary
    out = {}
    index = next(i for i, c in enumerate(CONFIGS) if c[0] == "ordinary")
    name, env, options, words = CONFIGS[index]
    texts = [t for _, t, _ in streams(index, 300, 0, [])]
    one_call = []
    for text in texts:
        case = {**L.request(env, text, words, options), "id": "lat"}
        one_call.append(min(_timed(lambda: relay.rows("english.read", [case])) for _ in range(1)))
    one_call.sort()
    out["corpus_sentence_ms"] = {"n": len(one_call), "p50": round(1000 * one_call[len(one_call) // 2], 2),
                                 "p95": round(1000 * one_call[int(0.95 * len(one_call)) - 1], 2), "budget": 20}
    for tokens, budget in ((150, 50), (300, None)):
        levels = tokens // 6
        sentence = "It is not the case that " + "it is not the case that " * (levels - 1) + "legacy is deployed."
        count = len(re.findall(r"\S+", sentence))
        case = {**L.request(env, sentence, words, options), "id": "long"}
        rows = []
        ms = 1000 * min(_timed(lambda: rows.append(relay.rows("english.read", [case])[0])) for _ in range(5))
        out[f"sentence_{tokens}_tokens"] = {"tokens": count, "ms": round(ms, 2), "budget": budget,
                                            "status": rows[-1].get("result", {}).get("status", rows[-1].get("status"))}
    out["bluedot_document"] = bluedot_english()
    instantiation = []
    for i, (cname, cenv, coptions, cwords) in enumerate(CONFIGS):
        if isinstance(cwords, Exception):
            continue
        case = {**L.request(cenv, "x.", cwords, coptions), "id": "inst"}
        ms = 1000 * min(_timed(lambda: relay.rows("english.read", [case])) for _ in range(5))
        instantiation.append((round(ms, 2), cname))
    instantiation.sort()
    out["grammar_instantiation_ms"] = {"n": len(instantiation), "budget": 100, "max": instantiation[-1],
                                       "median": instantiation[len(instantiation) // 2][0],
                                       "over_budget": [x for x in instantiation if x[0] > 100]}
    raw = {"language": "ve.core@0", "profile": "relational-fol@0", "spec_revision": "ve-v0-draft-2026-09-20",
           "vocabulary": {"sorts": {"thing": {"description": "thing"}},
                          "predicates": {f"p{k}": {"arguments": ["thing"], "description": "p",
                                                   "verbalisation": f"{{0}} is quality{k}"} for k in range(256)},
                          "constants": {"anchor": {"sort": "thing", "description": "anchor"}}}}
    wide = Environment(raw)
    wide_words = EnglishVocabulary(wide)
    case = {**L.request(wide, "Anchor is quality7.", wide_words, {}), "id": "wide"}
    rows = []
    ms = 1000 * min(_timed(lambda: rows.append(relay.rows("english.read", [case])[0])) for _ in range(3))
    out["environment_256_predicates"] = {"request_ms": round(ms, 1),
                                         "status": rows[-1].get("result", {}).get("status"),
                                         "bench": bench_policy(_case_json(wide, wide_words, {})),
                                         "budget": "policyOk inside the instantiation budget (100 ms)"}
    generated = sorted((ROOT / "lean/VE/EnglishGrammar/Fixed").glob("*.lean"))
    lake = [os.path.expanduser("~/.elan/bin/lake"), "env", "lean"]
    start = time.perf_counter()
    for path in generated:
        subprocess.run([*lake, str(path.relative_to(ROOT / "lean"))], cwd=ROOT / "lean", check=True,
                       capture_output=True)
    out["generated_modules_s"] = {"files": len(generated), "s": round(time.perf_counter() - start, 1), "budget": 60}
    return out


# ------------------------------------------------------------------ main

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--part", nargs="+", choices=PARTS, default=list(PARTS))
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--per-config", type=int, default=5000, help="sealed texts per round-trip configuration")
    parser.add_argument("--per-usecase", type=int, default=500, help="texts per use-case environment")
    parser.add_argument("--fresh-per-seed", type=int, default=200, help="texts per fresh seed per configuration")
    parser.add_argument("--documents", type=int, default=50)
    parser.add_argument("--reverse-samples", type=int, default=300)
    parser.add_argument("--mutation-texts", type=int, default=40)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args(argv)
    _setup()
    CONFIGS.extend(configurations())
    previous = json.loads(args.output.read_text()) if args.output.exists() else {}
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    report = {"format": FORMAT, "parts": previous.get("parts", {})}
    report["environments"] = [c[0] for c in CONFIGS]
    with multiprocessing.get_context("fork").Pool(args.workers) as pool:
        for part in args.part:
            started = time.time()
            if part == "g3":
                result = part_g3(pool, args.per_config, args.per_usecase, args.fresh_per_seed, args.documents)
            elif part == "reverse":
                result = part_reverse(pool, args.reverse_samples)
            elif part == "mutation":
                result = part_mutation(args.mutation_texts)
            elif part == "parity":
                result = part_parity(pool)
            elif part == "overlay":
                result = part_overlay(pool)
            else:
                result = part_latency()
            result["commit"] = commit
            result["seconds"] = round(time.time() - started, 1)
            report["parts"][part] = result
            args.output.write_text(json.dumps(report, indent=1, sort_keys=True, ensure_ascii=False) + "\n")
    print(json.dumps({part: {k: v for k, v in r.items() if not isinstance(v, (list, dict))}
                      for part, r in report["parts"].items()}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
