#!/usr/bin/env python3
"""Lean output differential (bundle OUT of docs/CONSOLIDATION-PLAN.md, step 0).

The Lean twin of layers2's Rust bundle D. Before a Lean edit, copy every `lean_exe` of
`lean/lakefile.toml` aside, from a build of the committed sources:

    python3 tools/lean_output_diff.py --save-baseline

After it, rebuild and compare the two builds byte for byte (exit code, stdout and stderr) over
the same invocations:

    python3 tools/lean_output_diff.py --build [--recorded DIR] [--contract-inputs FILE]

The invocations are:

* every case-reading mode (`ve_conformance` with no mode, `check-certificate`, `order` and
  `route`; the `ve_service` modes that replaced `ve_quantity`, every `ve_*_route` and `ve_risk_eval`
  in lean-first batch 1, and its mode `diagnose` for every registered unit, each as a `ve_service`
  session) over every `conformance/*.json` corpus that is a list of cases and every
  `lean/VE/*/examples/*.json` case file. A mode is given every corpus, matching or not: a corpus of
  another route's cases exercises its rejection path, which must not change either;
* for the executables that read no case list, the inputs their tests generate: a `ve_service`
  session over `tests/lean_service_corpus.py` (every mode and result kind, and the request
  errors), its English payloads for `ve_english_run`, the baseline service's responses to that
  session for both `ve_response_decode` checks, one shard of `tests/test_risk_differential.py`
  for the service's `risk-eval` mode, the sources of `conformance/english-lean/lexer.json` for
  `ve_english_lean_bench --lex` (its default mode prints CPU times, which no byte comparison
  holds; it is measurement only), and for `ve_english_route` the spec fixtures of
  `tests/test_english_lean_route.py` as `english.read` cases and each of its environments as an
  `english.grammar` case; for `ve_senses_route`, a successful s7 request and a malformed pack;
* with `--contract-inputs`, the `soft-norms@0` inputs that `tests/contract_input_recorder.py`
  wrote (`VE_CONTRACT_INPUTS`), as `soft-elaborate` cases for the service modes `soft-norms` and
  `diagnose` (unit `soft-norms@0`);
* with `--recorded`, every Lean executable invocation the test suite made, as recorded by
  `tests/lean_input_recorder.py` (`VE_LEAN_INPUTS`): arguments, input files and standard input,
  `ve_service` sessions included.

`--save-baseline` refuses a build that is not of the committed Lean sources (uncommitted changes
under `lean/`, or `lake build --no-build` reports work to do) and a `ve_service` that is not
pinned in `lean/checkers.lock`. An executable whose new build is byte-identical to its baseline
is not run (identical programs, identical output); `--all` runs it anyway. A clean comparison is
evidence of equal output over these inputs only; a run that times out, an empty invocation
list, or a compared executable (rebuilt, or any under `--all`) with no invocation makes the
differential invalid (exit 1). The full recorded corpus of a suite run is large
(about 10,000 invocations, tens of minutes at `--jobs 8`).
"""
from __future__ import annotations

import argparse
import base64
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
from typing import NamedTuple

ROOT = Path(__file__).resolve().parents[1]
LEAN = ROOT / "lean"
BIN = LEAN / ".lake/build/bin"
BASELINE = LEAN / ".lake/ve-output-baseline"
LOCK = LEAN / "checkers.lock"
TIMEOUT = 300

# Executables that read a case list from a path or `-`, with their mode arguments. `ve_diagnose`
# units are read from `VE/WireContract/Diagnose.lean`.
CASE_MODES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("ve_conformance", ()), ("ve_conformance", ("check-certificate",)), ("ve_conformance", ("order",)),
    ("ve_conformance", ("route",)),
)
# The `ve_service` modes that replaced the one-shot route executables (lean-first batch 1), given the
# same corpora as `ve_service` sessions (`route_session`).
ROUTE_MODES = ("quantity", "norms", "discourse", "speech-acts", "soft-norms", "rights", "reports", "alternatives",
               "risk", "norm-defaults", "readings-route")
# Executables that read no case list; `harness_invocations` gives their inputs.
HARNESS_EXECUTABLES = frozenset({"ve_service", "ve_english_run", "ve_response_decode", "ve_english_lean_bench",
                                 "ve_english_route", "ve_senses_route"})


class Invocation(NamedTuple):
    exe: str
    label: str
    args: tuple[str, ...]
    stdin: bytes | None = None


def executables(root: Path = ROOT) -> list[str]:
    lakefile = tomllib.loads((root / "lean/lakefile.toml").read_text())
    return sorted(exe["name"] for exe in lakefile.get("lean_exe", []))


def diagnose_units(root: Path = ROOT) -> list[str]:
    text = (root / "lean/VE/WireContract/Diagnose.lean").read_text()
    return re.findall(r'\("([\w.-]+@\d+)", ⟨', text)


def case_corpora(root: Path = ROOT) -> list[Path]:
    """`conformance/*.json` files whose top level is a list, and the Lean example case files."""
    found = []
    for path in [*sorted((root / "conformance").glob("*.json")), *sorted((root / "lean/VE").glob("*/examples/*.json"))]:
        try:
            if isinstance(json.loads(path.read_text()), list):
                found.append(path)
        except ValueError:
            continue
    return found


def write(path: Path, data: str | bytes) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data.encode() if isinstance(data, str) else data)
    return str(path)


def route_session(mode: str, cases: list, unit: str | None = None) -> bytes:
    """A `ve_service` session sending `cases` to `mode` in requests of at most 256 cases (`unit`, for
    `diagnose`, named in each case)."""
    from ve.backends.lean_service import LeanService
    if unit is not None:
        cases = [{**case, "unit": unit} if isinstance(case, dict) else case for case in cases]
    lines = []
    for start in range(0, max(len(cases), 1), 256):
        text = json.dumps(cases[start:start + 256], ensure_ascii=False, separators=(",", ":"))
        count = len(cases[start:start + 256])
        lines.append(LeanService._request_line(f"out-{start}", mode, text,
                                               {"cases": max(count, 1), "bytes": len(text.encode())}))
    return b"".join(lines)


def static_invocations(root: Path = ROOT) -> list[Invocation]:
    sessions = [*((mode, None) for mode in ROUTE_MODES), *(("diagnose", unit) for unit in diagnose_units(root))]
    found = []
    for corpus in case_corpora(root):
        name = corpus.relative_to(root).as_posix()
        for exe, mode in CASE_MODES:
            found.append(Invocation(exe, f"{' '.join(mode)} {name}".strip(), (*mode, str(corpus))))
        cases = json.loads(corpus.read_text())
        for mode, unit in sessions:
            found.append(Invocation("ve_service", f"{mode} {unit or ''} {name}".replace("  ", " "), (),
                                    route_session(mode, cases, unit)))
    return found


def service_session() -> tuple[bytes, list[tuple[str, dict]]]:
    """A `ve_service` session over `tests/lean_service_corpus.py` (every mode and result kind, in
    16-case requests, then the request errors), with the request each response is bound to."""
    from tests.lean_service_corpus import ERROR_REQUESTS, corpus
    from ve.backends.lean_service import LeanService, request_context
    lines, requests = [], []

    def request(mode: str, text: str, count: int, budget: dict) -> None:
        nonce = f"out-{len(requests)}"
        lines.append(LeanService._request_line(nonce, mode, text, budget))
        requests.append((mode, request_context(nonce, mode, text, count)))

    for mode, cases in corpus().items():
        for start in range(0, len(cases), 16):
            text = json.dumps(cases[start:start + 16], ensure_ascii=False, separators=(",", ":"))
            count = len(cases[start:start + 16])
            request(mode, text, count, {"cases": max(count, 1), "bytes": len(text.encode())})
    for mode, text, count, budget in ERROR_REQUESTS:
        request(mode, text, count, budget or {"cases": max(count, 1), "bytes": len(text.encode())})
    return b"".join(lines), requests


def harness_invocations(baseline: Path) -> list[Invocation]:
    """Inputs of the executables that read no case list (`ve_service`, its `risk-eval` mode included,
    `ve_english_run`, `ve_response_decode`, `ve_english_lean_bench`, `ve_english_route`,
    `ve_senses_route`), from the generators and
    fixtures their tests use. The responses that `ve_response_decode` checks are the baseline
    service's answers to the session."""
    for folder in (ROOT, ROOT / "tests"):  # the test modules import their helpers as pytest does
        if str(folder) not in sys.path:
            sys.path.insert(0, str(folder))
    from tests.lean_service_corpus import english_cases
    from tests.test_risk_differential import lean_cases, shard
    session, requests = service_session()
    found = [Invocation("ve_service", "corpus session", (), session)]
    found += [Invocation("ve_english_run", f"english payload {index}", (),
                         json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode())
              for index, payload in enumerate(english_cases())]
    boxes, conditions, _ = shard(0)
    found.append(Invocation("ve_service", "risk-eval conditions shard 0", (),
                            route_session("risk-eval", lean_cases(boxes[:12], conditions[:12]))))
    lexer = json.loads((ROOT / "conformance/english-lean/lexer.json").read_text())["cases"]
    sources = [case["source"] if "source" in case else
               case["source_repeat"]["text"] * case["source_repeat"]["times"] + case["source_repeat"]["tail"]
               for case in lexer]
    found.append(Invocation("ve_english_lean_bench", "lex the lexer fixture's sources", ("--lex", "/dev/stdin"),
                            json.dumps(sources, ensure_ascii=False).encode()))
    import test_english_lean_route as english_route
    reads = [{**english_route.request(name, text), "id": f"f{index}"}
             for index, (name, text) in enumerate(english_route.FIXTURES)]
    found.append(Invocation("ve_english_route", "english.read of the spec fixtures", ("english.read", "-"),
                            json.dumps(reads, ensure_ascii=False).encode()))
    grammars = [{**english_route.grammar_request(name), "id": name} for name in english_route.ENVIRONMENTS]
    found.append(Invocation("ve_english_route", "english.grammar of every environment", ("english.grammar", "-"),
                            json.dumps(grammars, ensure_ascii=False).encode()))
    from test_senses_route import PACK, joke_env
    from ve.english import EnglishVocabulary
    from ve.english_grammar import export
    env = joke_env()
    senses_case = {"id": "senses-s7", "environment": env.to_dict(),
                   "lexicon": export(EnglishVocabulary(env)), "packs": [PACK.decode("utf-8")],
                   "own": [], "source": "Alice tells the riddle.", "budget": 2_100_000}
    malformed = {**senses_case, "id": "senses-invalid-pack", "packs": ["null"]}
    found.append(Invocation("ve_senses_route", "senses s7 and malformed pack", ("-",),
                            json.dumps([senses_case, malformed], ensure_ascii=False).encode()))
    code, out, err = run(baseline / "ve_service", found[0])
    responses = [json.loads(line) for line in out.decode().splitlines()[1:]]
    if code != 0 or len(responses) != len(requests):
        raise SystemExit(f"the baseline ve_service answered {len(responses)} of {len(requests)} requests "
                         f"(exit {code}): {err[-500:]!r}")
    for check in ("decode", "invariants"):
        text = "".join(json.dumps({"check": check, "mode": mode, "request": request, "responses": [response]},
                                  ensure_ascii=False) + "\n" for (mode, request), response in zip(requests, responses))
        found.append(Invocation("ve_response_decode", f"{check} of the corpus session", (), text.encode()))
    return found


def contract_invocations(path: Path) -> list[Invocation]:
    rows = json.loads(path.read_text())
    cases = [{"id": f"recorded-{index}", "kind": "soft-elaborate", "environment": environment, "norms": norms}
             for index, (_label, environment, norms) in enumerate(rows)]
    return [Invocation("ve_service", f"soft-norms contract inputs {path.name}", (), route_session("soft-norms", cases)),
            Invocation("ve_service", f"diagnose soft-norms@0 contract inputs {path.name}", (),
                       route_session("diagnose", cases, "soft-norms@0"))]


def recorded_invocations(folder: Path, scratch: Path) -> list[Invocation]:
    """The invocations of `tests/lean_input_recorder.py`, deduplicated, input files restored."""
    found, seen = [], set()
    for path in sorted(folder.glob("*.jsonl")):
        for line in path.read_text().splitlines():
            record = json.loads(line)
            key = hashlib.sha256(json.dumps([record["exe"], record["args"], record["files"], record["stdin"]],
                                            sort_keys=True).encode()).hexdigest()
            if key in seen:
                continue
            seen.add(key)
            args = []
            for arg in record["args"]:
                index = re.fullmatch(r"@file:(\d+)", arg)
                if index:
                    content = base64.b64decode(record["files"][int(index[1])]["data"])
                    name = record["files"][int(index[1])]["name"]
                    args.append(write(scratch / "recorded" / key[:16] / index[1] / name, content))
                else:
                    args.append(arg)
            stdin = base64.b64decode(record["stdin"]) if record["stdin"] is not None else None
            found.append(Invocation(record["exe"], f"recorded {record.get('test', '?')} [{key[:12]}]",
                                    tuple(args), stdin))
    return found


def run(binary: Path, invocation: Invocation) -> tuple[int | str, bytes, bytes]:
    """Exit code, stdout and stderr; a timed-out run keeps its partial output under the code "timeout"."""
    try:
        done = subprocess.run([str(binary), *invocation.args], input=invocation.stdin if invocation.stdin is not None
                              else b"", capture_output=True, cwd=ROOT, timeout=TIMEOUT, check=False)
    except subprocess.TimeoutExpired as expired:
        return "timeout", expired.stdout or b"", expired.stderr or b""
    return done.returncode, done.stdout, done.stderr


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, text=True, capture_output=True, check=True).stdout


def save_baseline(target: Path) -> int:
    dirty = [line for line in git("status", "--porcelain", "--untracked-files=all", "--", "lean").splitlines()
             if "/.lake/" not in line
             and re.search(r"\.lean$|lakefile\.toml$|lean-toolchain$|lake-manifest\.json$", line)]
    if dirty:
        print("uncommitted changes under lean/; the baseline must be a build of committed sources:\n  "
              + "\n  ".join(dirty[:10]), file=sys.stderr)
        return 2
    names = executables()
    built = subprocess.run(["lake", "build", "--no-build", *names], cwd=LEAN, capture_output=True, text=True,
                           check=False)
    if built.returncode:
        print("lake build --no-build reports work to do; run lake build on the committed sources first:\n"
              + built.stdout[-1500:] + built.stderr[-1500:], file=sys.stderr)
        return 2
    pinned = set(json.loads(LOCK.read_text()).get("ve_service", []))
    if digest(BIN / "ve_service") not in pinned:
        print(f"ve_service ({digest(BIN / 've_service')}) is not pinned in {LOCK.relative_to(ROOT)}", file=sys.stderr)
        return 2
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True)
    manifest = {"commit": git("rev-parse", "HEAD").strip(), "executables": {}}
    for name in names:
        shutil.copy2(BIN / name, target / name)
        manifest["executables"][name] = digest(target / name)
    (target / "manifest.json").write_text(json.dumps(manifest, indent=1) + "\n")
    print(f"baseline of {manifest['commit'][:12]}: {len(names)} executables copied to {target}")
    return 0


def weight(invocation: Invocation) -> int:
    """Input bytes, to start the longest runs first."""
    size = len(invocation.stdin or b"")
    for arg in invocation.args:
        path = Path(arg)
        if path.is_absolute() and path.is_file():
            size += path.stat().st_size
    return size


def compare(baseline: Path, new: Path, extra: list[Invocation], scratch: Path, *, jobs: int = 8,
            everything: bool = False) -> int:
    manifest_path = baseline / "manifest.json"
    if not manifest_path.is_file():
        print(f"no baseline at {baseline}; run --save-baseline before the Lean edit", file=sys.stderr)
        return 2
    manifest = json.loads(manifest_path.read_text())
    for name, value in manifest["executables"].items():
        if digest(baseline / name) != value:
            print(f"baseline {name} does not match its manifest digest", file=sys.stderr)
            return 2
    missing = [name for name in executables() if name not in manifest["executables"] or not (new / name).is_file()]
    if missing:
        print(f"executables missing from the baseline or the new build: {', '.join(missing)}", file=sys.stderr)
        return 2
    changed = sorted(name for name in manifest["executables"] if digest(new / name) != manifest["executables"][name])
    # A byte-identical executable gives identical output on every input; its runs are skipped
    # unless --all asks for them.
    targets = sorted(manifest["executables"]) if everything else changed
    work = [*static_invocations(), *extra]
    if set(targets) & HARNESS_EXECUTABLES:
        work += harness_invocations(baseline)
    unknown = sorted({i.exe for i in work} - set(manifest["executables"]))
    if unknown:
        print(f"invocations of executables that are not in the baseline: {', '.join(unknown)}", file=sys.stderr)
        return 2
    run_work = sorted((i for i in work if i.exe in targets), key=weight, reverse=True)
    # Every executable that is compared needs inputs: an executable with none would pass unseen.
    uncovered = sorted(set(targets) - {i.exe for i in run_work})

    def both(invocation: Invocation) -> tuple[Invocation, tuple, tuple]:
        return invocation, run(baseline / invocation.exe, invocation), run(new / invocation.exe, invocation)

    with ThreadPoolExecutor(max_workers=max(1, jobs)) as pool:
        results = list(pool.map(both, run_work))
    differences, timeouts = [], []
    for invocation, old, fresh in results:
        parts = [part for part, a, b in zip(("exit code", "stdout", "stderr"), old, fresh) if a != b]
        if parts:
            differences.append(f"{invocation.exe} {invocation.label}: {', '.join(parts)} differ")
        sides = [side for side, result in (("baseline", old), ("new", fresh)) if result[0] == "timeout"]
        if sides:
            timeouts.append(f"{invocation.exe} {invocation.label}: {' and '.join(sides)} timed out after {TIMEOUT} s")
    print(f"baseline {manifest['commit'][:12]}; executables rebuilt with a different digest: "
          f"{', '.join(changed) if changed else 'none'}")
    print(", ".join(f"{name} {count}" for name, count in sorted(Counter(i.exe for i in work).items())))
    for line in (timeouts + differences)[:50]:
        print(line, file=sys.stderr)
    skipped = len(work) - len(run_work)
    print(f"{len(work)} invocations, {len(run_work)} run on both builds, {skipped} skipped as their executable "
          f"is byte-identical to the baseline; {len(differences)} differences, {len(timeouts)} timed out")
    invalid = []
    if timeouts:
        invalid.append(f"{len(timeouts)} invocations timed out, so their output was not compared in full")
    if not work:
        invalid.append("no invocations")
    if uncovered:
        invalid.append(f"no invocation of the rebuilt executables {', '.join(uncovered)}, so their output was "
                       "not compared")
    for reason in invalid:
        print(f"INVALID differential: {reason}", file=sys.stderr)
    return 1 if differences or invalid else 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--save-baseline", action="store_true", help="copy the current build to --baseline and stop")
    parser.add_argument("--baseline", type=Path, default=BASELINE)
    parser.add_argument("--build", action="store_true", help="run lake build before comparing")
    parser.add_argument("--jobs", type=int, default=min(8, os.cpu_count() or 1), help="parallel invocations")
    parser.add_argument("--all", action="store_true",
                        help="also run executables that are byte-identical to the baseline")
    parser.add_argument("--new", type=Path, default=BIN, help="the folder of the executables to compare")
    parser.add_argument("--recorded", type=Path, help="a VE_LEAN_INPUTS folder of tests/lean_input_recorder.py")
    parser.add_argument("--contract-inputs", type=Path, help="a VE_CONTRACT_INPUTS file of "
                                                             "tests/contract_input_recorder.py")
    args = parser.parse_args(argv)
    if args.save_baseline:
        return save_baseline(args.baseline)
    if args.build:
        built = subprocess.run(["lake", "build"], cwd=LEAN, check=False, stdout=subprocess.DEVNULL)
        if built.returncode:
            return built.returncode
    with tempfile.TemporaryDirectory(prefix="ve-lean-output-diff-") as folder:
        extra: list[Invocation] = []
        if args.contract_inputs:
            extra += contract_invocations(args.contract_inputs)
        if args.recorded:
            recorded = recorded_invocations(args.recorded, Path(folder))
            if not recorded:
                print(f"no recorded invocations in {args.recorded}", file=sys.stderr)
                return 1
            extra += recorded
        return compare(args.baseline, args.new, extra, Path(folder), jobs=args.jobs, everything=args.all)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
