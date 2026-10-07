"""Render the measured section of `docs/spec/english-lean-e2-report.md` from the E2.5 evidence.

    python -m conformance.english_lean_e2_report            # print the section
    python -m conformance.english_lean_e2_report --write    # rewrite it in the report

Every number of the section is computed here from `conformance/english-lean/e2-evidence.json`
(`conformance/english_lean_e2_evidence.py`), and every difference that evidence records is matched to a row of
`docs/lean-first/e2/DELTA.md` by `DISPOSITIONS`; one that no row covers is counted as undispositioned and named.
`tests/test_english_e2_report.py` checks that the committed section is this rendering.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "conformance/english-lean/e2-evidence.json"
REPORT = ROOT / "docs/spec/english-lean-e2-report.md"
BEGIN = "<!-- BEGIN GENERATED: python -m conformance.english_lean_e2_report --write -->\n"
END = "<!-- END GENERATED -->"


def _row_of(difference: dict) -> str | None:
    """The DELTA.md row that disposes of one G3 or reverse-corpus difference, or None."""
    python, lean = difference.get("python", {}), difference.get("lean", {})
    pcode, lcode = python.get("code"), lean.get("lean_code") or lean.get("code")
    message = python.get("message", "") or ""
    classes = set(difference.get("classes", ()))
    if pcode == "ResourceLimit" and message.startswith("This statement exceeds the 64-level nesting limit") and \
            lean.get("status") in ("none", "rejected"):
        return "O1"  # S2's F3: Python counts depth while it reads
    if pcode == "ResourceLimit" and lean.get("status") == "none" and "verdict" in classes:
        return "O2"  # S3's or38 class
    if classes == {"diagnostic-code"} and pcode in ("SyntaxError", "UnknownSymbol", "TypeMismatch",
                                                     "UnsupportedProfile") and lean.get("status") == "rejected":
        return "W2"  # both refuse; Lean's code and class for the refusal
    return None


DISPOSITIONS = {
    "O1": "order: S2's F3, Python's depth limit before a later fault",
    "O2": "order: S3's or38 class, Python's ResourceLimit where Lean has no reading",
    "W2": "wording: both refuse the text; the class is Lean's (spec 4.2)",
}


def g3_section(g3: dict) -> list[str]:
    out = ["### G3 at the dispatched boundary", ""]
    out.append(f"Configurations: {len(g3['by_config'])}; texts compared: **{g3['texts']:,}**; agreeing: "
               f"**{g3['agree']:,}**; differing: **{g3['differ']:,}**; excluded (Python's wall-clock limit): "
               f"{g3['excluded']}. Streams: the sealed round-trip stream ({g3['per_config']:,} texts per "
               f"round-trip configuration, {g3['per_usecase']} per use-case environment), "
               f"{g3['documents_per_config']} documents of five sentences per configuration, and "
               f"{len(g3['fresh_seeds'])} fresh date seeds of {g3['fresh_per_seed']} texts each per round-trip "
               f"configuration (seeds {g3['fresh_seeds'][0]} to {g3['fresh_seeds'][-1]}).")
    kinds = Counter()
    for counts in g3["by_config"].values():
        for key, value in counts.items():
            kinds[key] += value
    out.append("")
    out.append("| Stream | Texts | Agree | Differ |")
    out.append("|---|---:|---:|---:|")
    for kind in ("sealed", "documents", "fresh"):
        out.append(f"| {kind} | {kinds[f'{kind}:texts']:,} | {kinds[f'{kind}:agree']:,} | {kinds[f'{kind}:differ']:,} |")
    out.append("")
    stalled = g3.get("generator_stalled") or {}
    if stalled:
        out.append("The formula generator of `conformance.english_surface` found no formula within its time limit on: "
                   + ", ".join(f"`{name}`" for name in sorted(stalled)) + " (no text of that environment was "
                   "compared).")
        out.append("")
    out.append(f"Round trip (Lean's formulas against the formula each text was rendered from, or Lean refusing a text "
               f"Python reads): **{len(g3['roundtrip_failures'])}** failures.")
    out.append("")
    return out


def coverage_section(coverage: dict) -> list[str]:
    rules = sum(len(c.get("fixed_unreached", ())) for c in coverage.values())
    families = Counter(f for c in coverage.values() for f in c.get("families_unreached", ()))
    unreached = Counter(r for c in coverage.values() for r in c.get("fixed_unreached", ()))
    everywhere = sorted(r for r, n in unreached.items() if n == len(coverage))
    out = ["### Coverage", "",
           f"Over {len(coverage)} configurations, {rules:,} (configuration, fixed rule) pairs were not reached by a "
           f"compared text; {len(everywhere)} fixed rules were reached in no configuration. Lexical families "
           f"unreached somewhere: {', '.join(f'`{f}` ({n})' for f, n in families.most_common()) or 'none'}.", ""]
    if everywhere:
        out.append("Fixed rules no compared text reached: " + ", ".join(f"`{r}`" for r in everywhere) + ".")
        out.append("")
    return out


def differences_section(g3: dict, reverse: dict) -> tuple[list[str], int]:
    rows = Counter()
    undispositioned = []
    for d in g3["differences"]:
        row = _row_of(d)
        if row is None:
            undispositioned.append(("g3", d))
        else:
            rows[row] += 1
    for d in reverse["lean_accepts_python_differs"]:
        undispositioned.append(("reverse", d))
    out = ["### Differences and their dispositions", "",
           "| DELTA row | Disposition | G3 records |", "|---|---|---:|"]
    for row, text in DISPOSITIONS.items():
        out.append(f"| {row} | {text} | {rows[row]} |")
    out.append(f"| — | **undispositioned** | **{len(undispositioned)}** |")
    out.append("")
    for where, d in undispositioned[:20]:
        out.append(f"- {where}, `{d.get('config')}`: {d.get('classes')} — Python "
                   f"`{d.get('python', {}).get('code')}`, Lean `{d.get('lean', {}).get('status') if isinstance(d.get('lean'), dict) else 'one'}`: "
                   f"`{(d.get('text') or '')[:120]}`")
    if undispositioned:
        out.append("")
    return out, len(undispositioned)


def reverse_section(reverse: dict) -> list[str]:
    c = reverse["counts"]
    read = c.get("sample:lean-one", 0)
    agree = sum(v for k, v in c.items() if k.endswith("lean-one-python-agree"))
    differ = sum(v for k, v in c.items() if k.endswith("lean-one-python-differ"))
    return ["### The reverse corpus", "",
            f"{c.get('sample:texts', 0):,} texts were sampled from the `english.grammar` exports "
            f"({reverse['samples_per_config']:,} draws per configuration); Lean read {read:,} of them, the rest failing "
            f"a context condition the context-free sample cannot see (an unbound reference, an ordinal, a marker). "
            f"Every text Lean reads, with its spacing and word-split mutants that Lean also reads, was read by Python: "
            f"**{agree:,}** agree, **{differ}** differ.", ""]


def mutation_section(m: dict) -> list[str]:
    c = m["counts"]
    return ["### The lexicon mutation replay", "",
            f"{c.get('mutants', 0):,} mutants of the corpus lexicons (`english_lean_lexicon.mutants`); V1 to V6 refused "
            f"**{c.get('refused', 0):,}**, accepted **{c.get('accepted', 0):,}**. Over the accepted mutants, "
            f"{m['texts_per_config']} corpus texts each: unchanged {c.get('texts:same', 0):,}, no longer read "
            f"{c.get('texts:lost-or-unread', 0):,}, **changed formula {c.get('texts:changed', 0)}**.", ""]


def parity_section(p: dict) -> list[str]:
    c = p["counts"]
    v15 = [f for f in p["findings"] if f.get("status") == "v1-v5"]
    v6 = [f for f in p["findings"] if f.get("status") == "v6"]
    out = ["### Port parity", "",
           f"Corpus environments compared symbol by symbol: {c.get('corpus:compared', 0)}, mismatched symbols "
           f"**{c.get('corpus:symbols-mismatched', 0)}**. Mutation set: {c.get('mutant:compared', 0):,} environments "
           f"compared, mismatched symbols **{c.get('mutant:symbols-mismatched', 0)}**; V6 refusing Python's own "
           f"lexicon (a port defect): **{len(v6)}**; V1 to V5 refusing Python's lexicon (DELTA row A1): "
           f"{len(v15)}; mutants `Environment` refuses: {c.get('mutant-refused-by-Environment', 0)}.", ""]
    return out


def overlay_section(o: dict) -> list[str]:
    c = o["counts"]
    sites = {k.split(":", 2)[2]: v for k, v in c.items() if ":site:" in k and k.startswith("mutant")}
    return ["### Overlay parity", "",
            f"Corpus overlays compared: {c.get('corpus:compared', 0)}, agreeing {c.get('corpus:agree', 0)}. Overlay "
            f"mutants compared: {c.get('mutant:compared', 0):,}, agreeing **{c.get('mutant:agree', 0):,}**, differing "
            f"**{c.get('mutant:differ', 0)}**; refused by `display_environment` before any Lean call (not compared): "
            f"{c.get('mutant:display_environment-refuses', 0) + c.get('corpus:display_environment-refuses', 0)}. "
            f"Sites of the mutants: " + ", ".join(f"{k} {v}" for k, v in sorted(sites.items())) + ".", ""]


def latency_section(lat: dict) -> list[str]:
    def ok(value, budget):
        return "met" if budget is not None and value <= budget else ("reported" if budget is None else "**missed**")
    inst = lat["grammar_instantiation_ms"]
    wide = lat["environment_256_predicates"]["bench"]
    rows = [("a corpus sentence, p95", f"{lat['corpus_sentence_ms']['p95']} ms", "20 ms",
             ok(lat["corpus_sentence_ms"]["p95"], 20)),
            ("a 150-token sentence", f"{lat['sentence_150_tokens']['ms']} ms ({lat['sentence_150_tokens']['tokens']} "
             f"tokens, {lat['sentence_150_tokens']['status']})", "50 ms", ok(lat["sentence_150_tokens"]["ms"], 50)),
            ("a 300-token sentence (work budget)", f"{lat['sentence_300_tokens']['ms']} ms "
             f"({lat['sentence_300_tokens']['tokens']} tokens, {lat['sentence_300_tokens']['status']})", "inside the "
             "work budget", "met" if lat["sentence_300_tokens"]["status"] == "one" else "**missed**"),
            ("the BlueDot document's English", f"{lat['bluedot_document']['ms']} ms "
             f"({lat['bluedot_document']['sentences']} sentences, {lat['bluedot_document']['requests']} requests)",
             "1 s", ok(lat["bluedot_document"]["ms"], 1000)),
            ("grammar instantiation, worst corpus lexicon", f"{inst['max'][0]} ms (`{inst['max'][1]}`)", "100 ms",
             ok(inst["max"][0], 100)),
            ("`policyOk`, 256 predicates (CPU)", f"{wide['policy_micros'] / 1000:.0f} ms", "inside 100 ms",
             ok(wide["policy_micros"] / 1000, 100)),
            ("the generated modules", f"{lat['generated_modules_s']['s']} s ({lat['generated_modules_s']['files']} "
             "files, `lake env lean`)", "60 s", ok(lat["generated_modules_s"]["s"], 60))]
    out = ["### Latency (GE2 item 9)", "", "| Measure | Measured | Budget | |", "|---|---|---|---|"]
    out += [f"| {a} | {b} | {c} | {d} |" for a, b, c, d in rows]
    out.append("")
    return out


def render(evidence: dict | None = None) -> str:
    evidence = evidence or json.loads(EVIDENCE.read_text())
    parts = evidence["parts"]
    commits = sorted({p["commit"][:10] for p in parts.values()})
    lines = [f"Measured at {', '.join(f'`{c}`' for c in commits)} from "
             "[e2-evidence.json](../../conformance/english-lean/e2-evidence.json).", ""]
    lines += g3_section(parts["g3"])
    lines += coverage_section(parts["g3"]["coverage"])
    lines += reverse_section(parts["reverse"])
    differences, undispositioned = differences_section(parts["g3"], parts["reverse"])
    lines += differences
    lines += mutation_section(parts["mutation"])
    lines += parity_section(parts["parity"])
    lines += overlay_section(parts["overlay"])
    lines += latency_section(parts["latency"])
    lines.append(f"**Undispositioned differences: {undispositioned}.**")
    lines.append("")
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    section = render()
    if not args.write:
        print(section)
        return 0
    text = REPORT.read_text()
    head, rest = text.split(BEGIN, 1)
    _, tail = rest.split(END, 1)
    REPORT.write_text(head + BEGIN + section + END + tail)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
