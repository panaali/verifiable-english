#!/usr/bin/env python3
"""Reproducible sampling and full-dataset mechanical checks for the E0 dataset survey.

Usage:
    python3 survey_sample.py sample      # writes survey_samples/_drawn/<dataset>.json (items to classify)
    python3 survey_sample.py mechanical  # prints full-dataset mechanical numbers as JSON

Only the ProofWriter reader needs a third-party package (pyarrow, to read the parquet slice).
The per-item a/b/c/d classes in survey_samples/<dataset>.jsonl were assigned by a model reader
and are NOT produced by this script; this script only fixes which items were drawn.
"""
import glob
import json
import os
import random
import re
import sys
from collections import Counter

SEED = 20260921
N = 30
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "survey_samples", "_drawn")


def draw(items):
    """items: list of dicts with 'id'. Sorted by id first so file-system order cannot matter."""
    items = sorted(items, key=lambda r: r["id"])
    rng = random.Random(SEED)
    return rng.sample(items, min(N, len(items)))


# ---------------------------------------------------------------- FOLIO
def folio_rows():
    rows = []
    for split in ("train", "validation"):
        with open(os.path.join(DATA, "folio", f"tasksource_folio_v2_{split}.jsonl")) as f:
            rows += [dict(json.loads(l), split=split) for l in f if l.strip()]
    return rows


def folio_items():
    """Unit = one unique (NL sentence, gold FOL) pair: every premise and every conclusion."""
    seen, items = set(), []
    for r in folio_rows():
        nl, fol = r["premises"].split("\n"), r["premises-FOL"].split("\n")
        pairs = []
        if len(nl) == len(fol):
            pairs += [(f"s{r['story_id']}:p{i}", a, b) for i, (a, b) in enumerate(zip(nl, fol))]
        pairs.append((f"e{r['example_id']}:c", r["conclusion"], r["conclusion-FOL"]))
        for id_, a, b in pairs:
            if (a, b) not in seen:
                seen.add((a, b))
                items.append({"id": id_, "nl": a, "fol": b})
    return items


ATOM = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)\(([^()]*)\)")


def folio_formula_flags(fol):
    """Mechanical flags for one FOL string. Innermost-first atom stripping detects nesting."""
    flags = set()
    s = fol
    if re.search(r"[<>+*/≤≥]", s):
        flags.add("arith_or_cmp_symbol")
    if "=" in s:
        flags.add("equality")
    if "⊕" in s:
        flags.add("xor")
    maxar = 0
    # innermost parenthesised name(args) groups; after replacing with a token, an enclosing
    # name(...) that contains the token has a nested term => function symbol or malformed.
    for _ in range(10):
        found = False

        def rep(m):
            nonlocal maxar, found
            found = True
            args = [a.strip() for a in m.group(2).split(",")] if m.group(2).strip() else []
            maxar = max(maxar, len(args))
            if any("§" in a for a in args):
                flags.add("nested_term")
            if len(args) == 0:
                flags.add("arity0")
            if len(args) > 2:
                flags.add("arity_gt2")
            if any(re.fullmatch(r"-?\d+(\.\d+)?", a) for a in args):
                flags.add("numeric_constant")
            return "§"

        s2 = ATOM.sub(rep, s)
        if not found:
            break
        s = s2
    return flags, maxar


def folio_mechanical():
    items = folio_items()
    c = Counter()
    ar = Counter()
    for it in items:
        fl, m = folio_formula_flags(it["fol"])
        ar[m] += 1
        for x in fl:
            c[x] += 1
        if not (fl & {"arity_gt2", "nested_term", "arith_or_cmp_symbol", "numeric_constant", "arity0"}):
            c["clean"] += 1
    # story level: all formulas of an example clean
    ex_clean = ex_total = 0
    for r in folio_rows():
        fs = r["premises-FOL"].split("\n") + [r["conclusion-FOL"]]
        ex_total += 1
        bad = False
        for f in fs:
            fl, _ = folio_formula_flags(f)
            if fl & {"arity_gt2", "nested_term", "arith_or_cmp_symbol", "numeric_constant", "arity0"}:
                bad = True
        ex_clean += not bad
    return {"unique_sentence_pairs": len(items), "flags": dict(c), "max_arity_hist": dict(sorted(ar.items())),
            "examples_total": ex_total, "examples_all_formulas_clean": ex_clean}


# ---------------------------------------------------------------- ProofWriter
def proofwriter_rows():
    import pyarrow.parquet as pq  # third-party
    return pq.read_table(os.path.join(DATA, "proofwriter", "validation.parquet")).to_pylist()


def proofwriter_items():
    rows = proofwriter_rows()
    items = []
    for i, r in enumerate(rows):
        items.append({"id": f"{r['id']}#row{i}", "config": r["config"], "theory": r["theory"],
                      "question": r["question"], "answer": r["answer"]})
    return items


def proofwriter_mechanical():
    rows = proofwriter_rows()
    theories = {}
    for r in rows:
        theories.setdefault(r["theory"], r)
    neg = re.compile(r"\b(not|does not|do not|is not|are not)\b")
    c = Counter()
    for t, r in theories.items():
        c["theories"] += 1
        c["family:" + r["id"].split("-")[0]] += 1
        c["world:" + ("OWA" if "-OWA-" in r["id"] else "CWA" if "-CWA-" in r["id"] else "other")] += 1
        if neg.search(t):
            c["theories_with_negation"] += 1
        if re.search(r"\d", t):
            c["theories_with_digit"] += 1
    return {"rows": len(rows), "answers": dict(Counter(r["answer"] for r in rows)),
            "configs": dict(Counter(r["config"] for r in rows)), **dict(c)}


# ---------------------------------------------------------------- Cedar
def split_cedar(text):
    """Split a .cedar file into policies: text from (annotations +) permit/forbid up to the ';' at depth 0."""
    text_nc = re.sub(r"//[^\n]*", "", text)
    out, depth, start, in_str = [], 0, None, False
    i = 0
    while i < len(text_nc):
        ch = text_nc[i]
        if in_str:
            if ch == "\\":
                i += 1
            elif ch == '"':
                in_str = False
        elif ch == '"':
            in_str = True
            if start is None:
                start = i
        elif ch in "({[":
            depth += 1
        elif ch in ")}]":
            depth -= 1
        elif ch == ";" and depth == 0:
            if start is not None:
                out.append(text_nc[start:i + 1].strip())
            start = None
        elif start is None and not ch.isspace():
            start = i
        i += 1
    return [p for p in out if re.search(r"\b(permit|forbid)\b", p)]


def cedar_items():
    files = sorted(glob.glob(os.path.join(DATA, "cedar-examples", "**", "*.cedar"), recursive=True) +
                   glob.glob(os.path.join(DATA, "cedar-integration-tests", "tests", "**", "*.cedar"), recursive=True) +
                   glob.glob(os.path.join(DATA, "cedar-integration-tests", "sample-data", "**", "*.cedar"), recursive=True))
    seen, items = set(), []
    for f in files:
        rel = os.path.relpath(f, DATA)
        for k, p in enumerate(split_cedar(open(f).read())):
            key = re.sub(r"\s+", " ", p)
            if key in seen:
                continue
            seen.add(key)
            items.append({"id": f"{rel}#{k}", "text": p})
    return items


CEDAR_OPAQUE = [("numeric_cmp", r"(<=|>=|<(?!=)|(?<![=!<>])>(?!=))"), ("arith", r"[^/]\s[+*-]\s"),
                ("like", r"\blike\b"), ("ext_fn", r"\b(ip|decimal|datetime|duration)\("),
                ("ext_method", r"\.(isInRange|lessThan|greaterThan|lessThanOrEqual|greaterThanOrEqual|isIpv4|isIpv6|isLoopback|isMulticast|offset|durationSince|toDate|toTime)\("),
                ("set_ops", r"\.(containsAll|containsAny|isEmpty)\("), ("contains", r"\.contains\("),
                ("tags", r"\.(hasTag|getTag)\("), ("has", r"\bhas\b"), ("in_hierarchy", r"\bin\b"),
                ("attr_chain", r"\b[a-z]\w*\.\w+\.\w+"), ("template_slot", r"\?(principal|resource)"),
                ("context", r"\bcontext\b")]


def cedar_mechanical():
    items = cedar_items()
    c = Counter()
    for it in items:
        t = re.sub(r'"(\\.|[^"\\])*"', '""', it["text"])
        hit = {n for n, rx in CEDAR_OPAQUE if re.search(rx, t)}
        for h in hit:
            c[h] += 1
        if not (hit & {"numeric_cmp", "arith", "like", "ext_fn", "ext_method", "set_ops", "tags"}):
            c["no_opaque_construct"] += 1
    return {"unique_policies": len(items), "construct_counts": dict(c)}


# ---------------------------------------------------------------- Gatekeeper (OPA/Rego)
def gatekeeper_items():
    files = sorted(glob.glob(os.path.join(DATA, "gatekeeper-library", "src", "**", "src.rego"), recursive=True))
    return [{"id": os.path.relpath(f, DATA), "text": open(f).read()} for f in files]


def gatekeeper_mechanical():
    items = gatekeeper_items()
    rx = {"string_builtin": r"\b(startswith|endswith|contains|sprintf|concat|split|trim\w*|replace|lower|upper|substring|indexof|regex\.\w+|re_match|glob\.match)\(",
          "count_or_numeric": r"\b(count|sum|max|min|to_number|units\.\w+|abs)\(|[<>]=?\s",
          "comprehension": r"[\[{]\s*\w+\s*\|"}
    c = Counter()
    for it in items:
        for n, r in rx.items():
            if re.search(r, it["text"]):
                c[n] += 1
        if not any(re.search(r, it["text"]) for n, r in rx.items() if n != "comprehension"):
            c["no_string_or_numeric_builtin"] += 1
    return {"templates": len(items), **dict(c)}


# ---------------------------------------------------------------- Alloy
def alloy_items():
    files = sorted(glob.glob(os.path.join(DATA, "alloy-models", "**", "*.als"), recursive=True))
    items = []
    for f in files:
        txt = open(f, errors="replace").read()
        txt = re.sub(r"/\*.*?\*/", "", txt, flags=re.S)
        txt = re.sub(r"(//|--)[^\n]*", "", txt)
        for m in re.finditer(r"^\s*(fact|assert|pred)\b([^{\n]*)\{", txt, flags=re.M):
            depth, j = 1, m.end()
            while j < len(txt) and depth:
                depth += {"{": 1, "}": -1}.get(txt[j], 0)
                j += 1
            body = txt[m.start():j].strip()
            items.append({"id": f"{os.path.relpath(f, DATA)}@{m.start()}", "kind": m.group(1), "text": body})
    return items


def alloy_mechanical():
    items = alloy_items()
    rx = {"int_or_card": r"#|\bInt\b|\bint\b|\bsum\b|\bplus\b|\bminus\b|\bmul\b|[<>]=?|=<",
          "closure": r"\^|\*[A-Za-z(~]",
          "temporal": r"\b(always|eventually|after|until|historically|once|before)\b|'",
          "ordering_util": r"\b(next|prev|first|last|nexts|prevs|lt|gt|lte|gte)\b",
          "seq": r"\bseq\b|\bidxOf\b|\binds\b|\belems\b"}
    c = Counter(it["kind"] for it in items)
    for it in items:
        body = re.sub(r"<=>|=>|->|<:|:>", " ", it["text"])  # arrows are not comparisons
        hit = [n for n, r in rx.items() if re.search(r, body)]
        for h in hit:
            c[h] += 1
        if not hit:
            c["none_of_the_above"] += 1
    return {"paragraphs": len(items), "als_files": len(glob.glob(os.path.join(DATA, "alloy-models", "**", "*.als"), recursive=True)), **dict(c)}


# ---------------------------------------------------------------- Clover (Dafny)
def clover_items():
    base = os.path.join(DATA, "clover", "dataset", "CloverBench", "textbook_algo")
    items = []
    for d in sorted(os.listdir(base)):
        fs = sorted(glob.glob(os.path.join(base, d, "*.dfy")))
        if fs:
            items.append({"id": f"CloverBench/textbook_algo/{d}", "text": open(fs[0]).read()})
    return items


def clover_mechanical():
    items = clover_items()
    c = Counter()
    for it in items:
        spec = "\n".join(l for l in it["text"].split("\n") if re.search(r"\b(requires|ensures|invariant)\b", l))
        spec = re.sub(r"<==>|==>|<==", " ", spec)  # implications are not comparisons
        if re.search(r"[<>]=?|[+\-*/%]|\|\w|\.Length|\[", spec):
            c["spec_uses_arith_index_or_length"] += 1
        else:
            c["spec_without_those"] += 1
    return {"programs": len(items), **dict(c)}


# ---------------------------------------------------------------- FRET
FRET_FILES = ["fsm_reqts_and_vars.json", "LM_reqts_and_vars.json", "LPC_full_reqts_and_vars.json", "LM_requirements.json"]


def fret_items():
    items = []
    for f in FRET_FILES:
        d = json.load(open(os.path.join(DATA, "fret", f)))
        for r in d["requirements"]:
            if (r.get("fulltext") or "").strip():
                items.append({"id": f"{f}:{r.get('project')}:{r['reqid']}:{r.get('_id', '')[:8]}", "text": r["fulltext"]})
    return items


def fret_mechanical():
    items = fret_items()
    c = Counter()
    for it in items:
        t = re.sub(r"<=>|=>|->", " ", it["text"])  # implications are not comparisons
        num = bool(re.search(r"[<>]=?|[+*/]|\d\.\d|\babs|\b\d+\b", t))
        temp = bool(re.search(r"\b(next timepoint|within|for \d|after|until|before|eventually|immediately|when|whenever|upon|while|in \w+ mode)\b", t, re.I))
        c["numeric_or_arith"] += num
        c["temporal_keyword_beyond_always"] += temp
        c["neither"] += (not num and not temp)
    return {"requirements": len(items), **dict(c)}


DATASETS = {
    "folio": (folio_items, folio_mechanical),
    "proofwriter": (proofwriter_items, proofwriter_mechanical),
    "cedar": (cedar_items, cedar_mechanical),
    "gatekeeper": (gatekeeper_items, gatekeeper_mechanical),
    "alloy": (alloy_items, alloy_mechanical),
    "clover": (clover_items, clover_mechanical),
    "fret": (fret_items, fret_mechanical),
}

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "sample"
    only = sys.argv[2:] or list(DATASETS)
    if mode == "sample":
        os.makedirs(OUT, exist_ok=True)
        for name in only:
            items = DATASETS[name][0]()
            s = draw(items)
            with open(os.path.join(OUT, f"{name}.json"), "w") as f:
                json.dump({"population": len(items), "seed": SEED, "sample": s}, f, indent=1, ensure_ascii=False)
            print(name, "population", len(items), "drawn", len(s))
    else:
        print(json.dumps({n: DATASETS[n][1]() for n in only}, indent=1, ensure_ascii=False))
