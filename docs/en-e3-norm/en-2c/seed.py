"""en-e3bb's seeded bugs (docs/spec/en-e3-norm.md section 9, Python (EN-2)): each planted alone in a copy of its file,
its test run, the file restored. `uv run python docs/en-e3-norm/en-2c/seed.py` writes mutants.json beside it."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
import nested_pytest  # noqa: E402
ANSWER, SHADOW = "tests/test_english_statement_answer.py", "tests/test_english_statement_shadow.py"
MUTANTS = [
    ("an answer with one rule row more than the request's numbering allows is accepted (the header binding gone)",
     "ve/norm_english.py", '''    if header is None or header[1] != str(row["number"]):''', '''    if False:''',
     [f"{ANSWER}::test_an_extra_rule_row_over_a_precedence_line_is_unavailable"]),
    ("the span binding's overlap check dropped", "ve/norm_english.py",
     '''        if any(a[1] > b[0] for a, b in zip(spans, spans[1:])):''', '''        if False:''',
     [f"{ANSWER}::test_p2_a_rule_span_out_of_the_source_is_unavailable", f"{ANSWER}::test_every_named_mutant_is_unavailable"]),
    ("the shadow calls Lean with VE_SHADOW_LOG unset (the default log of english_lean.py)", "ve/norm_english.py",
     '''    log = statement_shadow_log() if type(source) is str else None''',
     '''    log = Path(os.environ.get("VE_SHADOW_LOG", "ve-shadow.jsonl")) if os.environ.get("VE_STATEMENT_COMPARATOR") == "1" else None''',
     [f"{SHADOW}::test_the_shadow_needs_both_flags"]),
    ("the binding accepts a span that ends inside a multi-byte character", "ve/norm_english.py",
     '''_on_boundary(raw, start) and _on_boundary(raw, stop)''', '''_on_boundary(raw, start)''',
     [f"{ANSWER}::test_p2_a_rule_span_out_of_the_source_is_unavailable", f"{ANSWER}::test_every_named_mutant_is_unavailable"]),
    ("the node's over not tied to its row's exception_to and precedence rows", "ve/norm_english.py",
     '''norm["over"] != over:''',
     '''not set(norm["over"]) <= {f"rule-{m}" for m in range(1, k + 1)}:''',
     [f"{ANSWER}::test_every_retyped_dropped_or_duplicated_member_is_unavailable"]),
    ("the rule rows' spans not all bound before their nodes are read (limits charged after work)",
     "ve/norm_english.py", '''        spans = [r["span"] for r in rules]''', '''        spans = [r["span"] for r in rules][:1]''',
     [f"{ANSWER}::test_the_spans_bound_the_rule_rows_before_any_node_is_read"]),
    ("a rule node's formulas may name an undeclared constant or an unbound variable", "ve/norm_english.py",
     '''constants <= env.constants.keys() and bound):''', '''True):''',
     [f"{ANSWER}::test_every_named_mutant_is_unavailable",
      f"{ANSWER}::test_every_retyped_dropped_or_duplicated_member_is_unavailable"]),
    ("the gate reads english.statement without its reader", "tools/relay_mutation_gate.py",
     '''SERVICE_READERS["english.statement"] = _statement_reader''', '''pass''',
     ["tests/test_relay_mutation_gate.py::test_english_statement_is_read_as_the_w1_shadow_reads_it"]),
]


def main() -> int:
    out = []
    for behaviour, path, old, new, tests in MUTANTS:
        target = ROOT / path
        text = target.read_text()
        assert text.count(old) == 1, (path, old)
        target.write_text(text.replace(old, new))
        try:
            run = subprocess.run(nested_pytest.command(["-q", *tests]), cwd=ROOT, capture_output=True, text=True,
                                 env=nested_pytest.environment(os.environ))
        finally:
            target.write_text(text)
        failed = sorted({line[len("FAILED "):].split(" - ")[0] for line in run.stdout.splitlines()
                         if line.startswith("FAILED ")})
        out.append({"behaviour": behaviour, "file": path, "test": tests, "failed": failed,
                    "caught": run.returncode == 1 and bool(failed)})
        print(out[-1]["caught"], behaviour, failed)
    (Path(__file__).parent / "mutants.json").write_text(json.dumps(out, indent=1) + "\n")
    return 0 if all(m["caught"] for m in out) else 1


if __name__ == "__main__":
    raise SystemExit(main())
