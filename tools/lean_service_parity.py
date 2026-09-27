"""Gate 1: `ve_service` results are byte-identical to the one-shot Lean executables.

Usage (repository root, after `cd lean && lake build`):

    PATH="$HOME/.elan/bin:$PATH" UV_CACHE_DIR=/tmp/ve-uv-cache uv run --frozen \
        python tools/lean_service_parity.py [--full] --out experiments/lean-service/parity

Every corpus is cut into the client's request chunks (at most 256 cases or 4 MiB).
Each chunk goes once to the one-shot executable as a JSON array and once to the
service as one request with the same cases text; the service's `results` array must
equal the one-shot stdout byte for byte. A chunk the one-shot runner rejects as a
whole (exit 2, message on stderr) must be a service line error with the same message.
The English runner takes one object per process; each one is one service case, and
its one-shot failure (exit 2) must be the service's error record with that message.

Corpora: the committed conformance fixtures that are runner case lists, the committed
replay queries, the fast generators used by the differential tests, adversarial
cases (depth, non-objects, forged fields) for every mode, and with `--full` the
prover-backed certificate and order generators.
"""
from __future__ import annotations

import argparse
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.lean_service_common import MODES, machine  # noqa: E402
from ve.backends.lean_service import LeanService  # noqa: E402

COMMAND = {mode: command for mode, command in MODES.values()}
FIXTURES = ROOT / "conformance"


def load(path):
    return json.loads((ROOT / path).read_text())


def adversarial(mode):
    """Inputs the runners reject case by case, plus a depth-limited case."""
    deep = {"id": "deep", "x": json.loads("[" * 300 + "]" * 300)}
    cases = [deep, {}, {"id": "no-environment"}, {"id": 7, "environment": {}},
             {"id": "unicode é中", "environment": {"language": "ve.core@9"}},
             {"id": "list-env", "environment": []}]
    if mode == "english":
        return [{"environment": {"sorts": [], "predicates": {}, "constants": {}},
                 "lexicon": {"sorts": {}, "predicates": {}, "constants": {}}, "cases": []},
                {"environment": {}}, {"lexicon": {}}]
    return cases


def evaluate_corpora():
    yield "evaluation.json", load("conformance/evaluation.json")
    yield "countermodels.json", load("conformance/countermodels.json")
    yield "parser.json", load("conformance/parser.json")
    yield "identity.json", load("conformance/identity.json")
    yield "validation.json", load("conformance/validation.json")
    closure = load("conformance/closure.json")
    variants = [{"id": f"{c['id']}-cm", "kind": "countermodel", "environment": c["environment"],
                 "model": c["model"], "premises": c["ast"][:1], "conclusion": c["ast"][1]}
                for c in closure if len(c["ast"]) > 1]
    yield "closure.json + countermodel variants", closure + variants
    p1 = [e["query"] for e in load("experiments/P1-deference/checks/lean-replay.json")["entries"]
          if e.get("kind") == "countermodel"]
    yield "P1 lean-replay countermodels", p1
    # Forged evaluation inputs: every case with one field removed or retyped.
    forged = []
    for case in load("conformance/evaluation.json")[:60]:
        for key in ("model", "ast", "environment"):
            forged.append({k: v for k, v in case.items() if k != key})
            forged.append({**case, key: "forged"})
    yield "forged evaluation fields", forged


def certificate_corpora(full):
    rows = load("conformance/v0-replay-baseline.json")["rows"]
    yield "v0-replay-baseline.json", [r["case"] for r in rows]
    p1 = [e["query"] for e in load("experiments/P1-deference/checks/lean-replay.json")["entries"]
          if e.get("kind") != "countermodel"]
    yield "P1 lean-replay certificates", p1
    queries = [json.loads(p.read_text()) for p in sorted((ROOT / "usecases/closure-induction").glob("*/query.json"))]
    queries.append(load("experiments/obfuscated-arguments/iceberg/qualitative-query.json"))
    yield "closure-induction and iceberg queries", queries
    if full:
        from conformance import certificates, closure_certificates, induction
        positive, _ = certificates.positive_cases()
        yield "certificates.py positive", positive
        yield "certificates.py forged", certificates.forged_cases()
        closure, _ = closure_certificates.positive_cases()
        yield "closure_certificates.py positive", closure
        yield "closure_certificates.py forged", closure_certificates.forged_cases(closure)
        yield "induction.py positive", induction.positive_cases()[0] if isinstance(
            induction.positive_cases(), tuple) else induction.positive_cases()
        yield "induction.py forged", induction.forged_cases()


def order_corpora(full):
    from conformance import order
    from ve import Environment, print_document
    from ve.ast import document_from_data
    cases = order.evaluation_cases(200)
    generated = [c for c, _ in cases] if cases and isinstance(cases[0], tuple) else cases
    yield "order.evaluation_cases(200)", generated
    surface = []
    for case in generated:
        env = Environment(case["environment"])
        source = print_document(env, document_from_data(env, case["ast"]))
        surface.append({"id": case["id"], "kind": "surface", "environment": case["environment"],
                        "source": source})
    yield "order surface variants", surface
    if full:
        positive, refuted, _, _ = order.positive_cases(1.0)
        yield "order.py positive", positive
        yield "order.py forged", order.forged_cases(positive)
        yield "order.py refuted", refuted


def route_corpora():
    route = load("lean/VE/Route/examples/route-cases.json")
    yield "route-cases.json", route
    sys.path.insert(0, str(ROOT / "tests"))
    from tests.test_definitions_differential import SETS, generate, probes
    definitions = []
    for index in range(SETS):
        env, model, _ = generate(index)
        try:
            ast = probes(env)
        except Exception:  # noqa: BLE001  (an invalid environment: Lean reports it)
            ast = []
        definitions.append({"id": f"bg{index}", "kind": "background", "environment": env})
        definitions.append({"id": f"ev{index}", "kind": "evaluate", "environment": env, "model": model,
                            "ast": ast})
    yield "definitions differential (1000 sets)", definitions
    from ve.profiles import LANGUAGE, SPEC_REVISION
    core = []
    for filename in ("evaluation.json", "closure.json"):
        for old in load(f"conformance/{filename}"):
            raw = {k: v for k, v in old["environment"].items() if k != "profile"}
            raw.update(language=LANGUAGE, spec_revision=SPEC_REVISION,
                       profiles=["closure@0", "nary@0", "relational-fol@0"])
            core.append({"id": old["id"], "kind": "evaluate", "environment": raw, "ast": old["ast"],
                         "model": old["model"]})
    yield "nary core replay of evaluation + closure", core
    spec = importlib.util.spec_from_file_location("dag_differential",
                                                  ROOT / "lean/VE/Route/examples/dag_differential.py")
    dag = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(dag)
    import random
    rng = random.Random(20260925)
    yield "dag_differential (200)", [{"id": f"g{i}", "kind": "dependency-order", "environment": dag.ENV,
                                      "nodes": dag.graph(rng)} for i in range(200)]
    usecase = ROOT / "usecases/math-mini-paper/t7-definitions-bundle.json"
    if usecase.exists():
        bundle = json.loads(usecase.read_text())
        yield "math-mini-paper definitions bundle", [{"id": "t7", "kind": "bundle",
                                                      "environment": bundle["environment"],
                                                      "lemmas": bundle["lemmas"]}]


def norms_corpora():
    sys.path.insert(0, str(ROOT / "tests"))
    from tests.test_norms_three_way import corpus, lean_case, pair_corpus
    docs = [*corpus(), *pair_corpus()]
    yield "norms 1100 regenerated documents", [lean_case(i, d) for i, d in enumerate(docs)]
    yield "route-cases.json through ve_norms_route", load("lean/VE/Route/examples/route-cases.json")


def english_payloads(per_vocabulary):
    import warnings
    from conformance import english_lean as E
    from ve import ast, render
    from ve.english import EnglishVocabulary, UnreviewedVocabularyWarning
    warnings.simplefilter("ignore", UnreviewedVocabularyWarning)
    payloads = []
    for offset, (name, env, options) in enumerate(E.configurations()):
        words = EnglishVocabulary(env, **options)
        try:
            lex = E.lexicon(env, words)
        except E.Untokenizable:
            continue
        letters = tuple(words.letters.values())
        cases = []
        for formula in E.corpus(env, words, name, per_vocabulary, offset):
            if not E.v0_only(formula):
                continue
            text = render(ast.Document((formula,)), env, "ve_english", **options)
            tokens = E.tokenize(E.lower_sentence_starts(text), letters)
            cases.append({"tokens": tokens, "formulas": [E.wire(formula)]})
        cases += [{"tokens": tokens, "formulas": [E.wire(ast.Top())]} for _, tokens, _ in E.fixtures(lex)]
        payloads.append({"environment": E.environment(env), "lexicon": lex, "cases": cases})
    return payloads


def chunks(service, cases):
    texts = [json.dumps(c, ensure_ascii=False, separators=(",", ":")) for c in cases]
    for chunk in service._chunks(texts):
        yield "[" + ",".join(chunk) + "]", len(chunk)


def results_text(raw: bytes) -> bytes:
    start = raw.index(b'"results":') + len(b'"results":')
    suffix = b',"status":"ok"}'
    assert raw.endswith(suffix), raw[-100:]
    return raw[start:-len(suffix)]


def compare_batch(service, mode, cases):
    stats = {"cases": len(cases), "requests": 0, "identical": 0, "mismatches": [], "exit_codes": {},
             "one_shot_s": 0.0, "service_s": 0.0}
    for text, n in chunks(service, cases):
        stats["requests"] += 1
        started = time.perf_counter()
        proc = subprocess.run([str(x) for x in COMMAND[mode]], input=text.encode(), capture_output=True,
                              timeout=600)
        stats["one_shot_s"] += time.perf_counter() - started
        stats["exit_codes"][proc.returncode] = stats["exit_codes"].get(proc.returncode, 0) + n
        started = time.perf_counter()
        raw, response = service.exchange(mode, text, n, timeout=600, budget={"cases": 4096, "bytes": 1 << 24})
        stats["service_s"] += time.perf_counter() - started
        if proc.returncode == 2:
            ok = response.get("status") == "error" and response.get("error") == proc.stderr.decode().strip()
        else:
            ok = response.get("status") == "ok" and results_text(raw) == proc.stdout.strip()
        if ok:
            stats["identical"] += n
        else:
            stats["mismatches"].append({"one_shot": proc.stdout[:300].decode(errors="replace"),
                                        "stderr": proc.stderr[:300].decode(errors="replace"),
                                        "service": raw[:300].decode(errors="replace")})
    return stats


def compare_english(service, payloads):
    """One-shot outputs must appear byte for byte in the service's results; a one-shot
    failure (exit 2, message on stderr) must be the service's error record."""
    stats = {"cases": len(payloads), "requests": 0, "identical": 0, "mismatches": [], "exit_codes": {},
             "one_shot_s": 0.0, "service_s": 0.0}
    expected = []
    for payload in payloads:
        started = time.perf_counter()
        proc = subprocess.run([str(x) for x in COMMAND["english"]],
                              input=json.dumps(payload, ensure_ascii=False).encode(),
                              capture_output=True, timeout=600)
        stats["one_shot_s"] += time.perf_counter() - started
        stats["exit_codes"][proc.returncode] = stats["exit_codes"].get(proc.returncode, 0) + 1
        expected.append((proc.returncode, proc.stdout.strip(), proc.stderr.decode().strip()))
    offset = 0
    for text, n in chunks(service, payloads):
        stats["requests"] += 1
        started = time.perf_counter()
        raw, response = service.exchange("english", text, n, timeout=600)
        stats["service_s"] += time.perf_counter() - started
        body = results_text(raw) if response.get("status") == "ok" else b""
        rows = response.get("results") or [None] * n
        for (code, stdout, stderr), row in zip(expected[offset:offset + n], rows):
            if code == 0:
                ok = stdout in body and json.loads(stdout) == row
            else:
                ok = row == {"status": "error", "error": stderr}
            if ok:
                stats["identical"] += 1
            else:
                stats["mismatches"].append({"one_shot": (stdout or stderr.encode())[:300].decode(errors="replace"),
                                            "service": json.dumps(row)[:300]})
        offset += n
    return stats


def compare_english_raw(service, payloads):
    """Exercise JSON accepted by the English runner but not the restricted decoder."""
    stats = {"cases": len(payloads), "requests": 0, "identical": 0, "mismatches": [], "exit_codes": {},
             "one_shot_s": 0.0, "service_s": 0.0}
    for payload in payloads:
        started = time.perf_counter()
        proc = subprocess.run([str(x) for x in COMMAND["english"]], input=payload.encode(),
                              capture_output=True, timeout=600)
        stats["one_shot_s"] += time.perf_counter() - started
        stats["exit_codes"][proc.returncode] = stats["exit_codes"].get(proc.returncode, 0) + 1
        started = time.perf_counter()
        raw, response = service.exchange("english", "[" + payload + "]", 1, timeout=600)
        stats["service_s"] += time.perf_counter() - started
        stats["requests"] += 1
        row = response.get("results", [None])[0]
        if proc.returncode == 0:
            ok = response["status"] == "ok" and proc.stdout.strip() in results_text(raw) and row == json.loads(proc.stdout)
        else:
            ok = row == {"status": "error", "error": proc.stderr.decode().strip()}
        if ok:
            stats["identical"] += 1
        else:
            stats["mismatches"].append({"input": payload[:300], "one_shot": proc.stdout[:300].decode(errors="replace"),
                                        "stderr": proc.stderr[:300].decode(errors="replace"),
                                        "service": raw[:300].decode(errors="replace")})
    return stats


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--full", action="store_true", help="include prover-backed generators")
    parser.add_argument("--english-per-vocabulary", type=int, default=200)
    args = parser.parse_args(argv)
    families = [("evaluate", evaluate_corpora()), ("check-certificate", certificate_corpora(args.full)),
                ("order", order_corpora(args.full)), ("route", route_corpora()), ("norms", norms_corpora())]
    report = {"machine": machine(), "full": args.full, "corpora": []}
    service = LeanService(timeout=600, max_requests=10**9, max_rss=None)
    service.start()
    for mode, corpora in families:
        rejected = [(f"batch rejected: null ({mode})", [{"id": "a"}, {"id": None}]),
                    (f"batch rejected: fraction ({mode})", [{"id": "b", "x": 1.5}])]
        for name, cases in list(corpora) + [(f"adversarial ({mode})", adversarial(mode))] + rejected:
            stats = compare_batch(service, mode, cases)
            report["corpora"].append({"mode": mode, "corpus": name, **stats})
            print(f"{mode:18} {name:45} {stats['identical']}/{stats['cases']} identical "
                  f"in {stats['requests']} requests; exits {stats['exit_codes']}", flush=True)
    for name, payloads in (("english_lean differential payloads", english_payloads(args.english_per_vocabulary)),
                           ("adversarial (english)", adversarial("english"))):
        stats = compare_english(service, payloads)
        report["corpora"].append({"mode": "english", "corpus": name, **stats})
        print(f"{'english':18} {name:45} {stats['identical']}/{stats['cases']} identical "
              f"in {stats['requests']} requests; exits {stats['exit_codes']}", flush=True)
    base = json.dumps(adversarial("english")[0], separators=(",", ":"))
    specimens = [base[:-1] + suffix for suffix in (
        ',"ignored":null}', ',"ignored":1.5}', ',"ignored":1e2}',
        ',"ignored":1,"ignored":2}')]
    stats = compare_english_raw(service, specimens)
    report["corpora"].append({"mode": "english", "corpus": "one-shot JSON acceptance", **stats})
    print(f"{'english':18} one-shot JSON acceptance{'':22} {stats['identical']}/{stats['cases']} identical", flush=True)
    report["service_stats"] = service.stats
    service.close()
    total = sum(c["cases"] for c in report["corpora"])
    same = sum(c["identical"] for c in report["corpora"])
    report["total"] = {"cases": total, "identical": same}
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "parity.json").write_text(json.dumps(report, indent=2) + "\n")
    lines = ["# Lean service parity (stage 1, gate 1)", "",
             f"Commit `{report['machine']['commit']}`; {'full' if args.full else 'fast'} corpora. "
             f"{same}/{total} cases byte-identical to the one-shot executables; "
             f"service restarts {report['service_stats']['restarts']}.", "",
             "| Mode | Corpus | Cases | Requests | Identical | One-shot exit codes (cases) |",
             "|---|---|---:|---:|---:|---|"]
    for c in report["corpora"]:
        lines.append(f"| {c['mode']} | {c['corpus']} | {c['cases']} | {c['requests']} | {c['identical']} | "
                     f"{', '.join(f'{k}: {v}' for k, v in sorted(c['exit_codes'].items()))} |")
    (args.out / "PARITY.md").write_text("\n".join(lines) + "\n")
    print(f"TOTAL {same}/{total} identical")
    return 0 if same == total else 1


if __name__ == "__main__":
    sys.exit(main())
