"""kb-10b-switch seeded bugs: plant each bug, run the one test that should catch it, restore the file from its saved text.
Writes /tmp/kb10bs/seeded.json (copied to docs/kernel/kb-10b-switch/seeded-bugs.json)."""
import json, os, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT / "tools"))
import nested_pytest  # noqa: E402  (the repository's one pytest command builder)
BUGS = [
 ("a", "ve/softnorms.py", 'for query, row in zip(queries, answer["results"]):', 'for query, row in zip(queries[1:], answer["results"]):',
  "tests/test_kb10b_switch.py::test_selected_rules_and_outcomes_are_leans_answers_at_each_tuple"),
 ("b", "ve/softnorms.py", 'return self._selected_row(source, predicate, model, values)["outcome"]', 'return bool(self._selected_row(source, predicate, model, values)["selected"])',
  "tests/test_kb10b_switch.py::test_the_outcome_is_not_the_truth_of_the_selection"),
 ("h", "ve/softnorms.py", 'if limit and isinstance(error, ResourceLimit):', 'if limit and getattr(error, "code", None) == "ResourceLimit":',
  "tests/test_kb10b_switch.py::test_over_the_query_limit_the_pair_is_asked_per_predicate"),
 ("i", "ve/softnorms.py", 'pair = pairs.setdefault(key, {', 'pair = pairs.setdefault("", {',
  "tests/test_kb10b_switch.py::test_another_model_or_another_document_is_another_call"),
 ("j", "ve/softnorms.py", '            predicates += [p for p in self.order if p not in predicates]\n', '',
  "tests/test_kb10b_switch.py::test_one_call_per_document_and_model_sends_every_query_of_the_pair"),
 ("k", "usecases/anthropic-rsp/run.py", 'outcome_at(predicate, model(doc, case), tuple(values))', 'outcome_at(predicate, model(doc, case), tuple(values)[::-1])',
  "tests/test_kb10b_switch.py::test_the_harnesses_completed_is_outcome_at"),
]
out = []
for name, path, a, b, test in BUGS:
    s = open(path).read(); assert s.count(a) == 1, name
    open(path, "w").write(s.replace(a, b))  # restored below from `s`, the file as it was
    try:
        r = subprocess.run(nested_pytest.command(["-q", test], python=["uv", "run", "python"]), cwd=ROOT,
                           env=nested_pytest.environment(os.environ), capture_output=True, text=True)
    finally:
        open(path, "w").write(s)
    last = r.stdout.strip().splitlines()[-1]
    caught = nested_pytest.failed_test_run(r)  # a failing test, not a collection or usage error
    print(name, path, "->", "FAILS" if caught else "NOT CAUGHT", "|", last)
    out.append({"bug": name, "file": path, "from": a, "to": b, "test": test, "result": last, "caught": caught})
json.dump(out, open("/tmp/kb10bs/seeded.json", "w"), indent=1)
