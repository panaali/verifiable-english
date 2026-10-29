"""Measured level of the policy family (apol-req): verified bytes over source bytes.

`python usecases/agent-policy/level.py` reads the requirement register
(`requirements.json`), `answer-key.json`, `results.json` and
`policy.manifest.json`, and prints verified bytes, source bytes and the OPEN
bytes of each missing feature family. It is a relay: it compares answers VE
already wrote to `results.json` with the frozen answer key, and runs the named
tests of the cedar-attributes and gatekeeper-exemption rows. It decides
nothing VE decides.

It exits 1, and counts no bytes for the row concerned, when the register is
malformed or its frozen rows changed, a row's bytes are not the UTF-8 length
of its statement, a VERIFIED row links no case or test, a linked case does
not agree, a named test fails, a row's VE text is not the text VE checked
(policy.ve, log.ve and log-schema.ve as `results.json` records them, rule
names bound by the manifest), or an OPEN row names no feature family.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]

# The closed list of missing feature families, in the words of the basis.
FAMILIES = ("speech acts", "time", "numbers", "information flow",
            "Cedar permit/forbid via the W1 adapter", "the full Gatekeeper template",
            "the classifiers PLAN section 2 puts outside VE")
USECASES = ("agent-policy", "cedar-attributes", "gatekeeper-exemption")
ROW_KEYS = {"id", "usecase", "source", "statement", "bytes", "status", "ve_text", "decided_by", "family"}
APPENDED_KEYS = ROW_KEYS | {"date"}
HEADER_KEYS = {"frozen_utc", "rows_sha256", "basis_by", "basis"}
# Answer-key policy fields and the results.json policy_summary field each is compared with.
POLICY_FIELDS = {"conflict": "conflict", "satisfiable_pairs": "satisfiable_pairs",
                 "pair_queries": "pair_queries", "never_deciding": "never_deciding",
                 "dead_guards": "dead_guards", "covered_tools": "covered_tools",
                 "gap_tools": "gap_tools", "required_overlaps": "overlaps"}
# The one gap results.json lists that the key states separately, as `unnamed_tool: "gap or OPEN"`.
UNDECLARED_TOOL = "(an undeclared tool)"


class RegisterError(Exception):
    pass


def rows_sha256(rows) -> str:
    text = json.dumps(rows, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _strings(value, what):
    if type(value) is not list or any(type(item) is not str or not item for item in value):
        raise RegisterError(f"{what} is not a list of non-empty strings")
    if len(set(value)) != len(value):
        raise RegisterError(f"{what} repeats an entry")
    return value


def _row_shape(row, keys):
    """Raises RegisterError unless the row has exactly the typed fields of the register."""
    if type(row) is not dict or set(row) != keys:
        raise RegisterError(f"row fields are not {sorted(keys)}")
    for key in ("id", "source", "statement"):
        if type(row[key]) is not str or not row[key]:
            raise RegisterError(f"{key} is not a non-empty string")
    if row["usecase"] not in USECASES:
        raise RegisterError(f"use case {row['usecase']!r} is not one of {list(USECASES)}")
    if type(row["bytes"]) is not int or row["bytes"] != len(row["statement"].encode("utf-8")):
        raise RegisterError("bytes is not the UTF-8 length of the statement")
    text, decided = row["ve_text"], row["decided_by"]
    if type(text) is not dict or set(text) != {"files", "rules", "records"}:
        raise RegisterError("ve_text fields are not files, rules, records")
    if type(decided) is not dict or set(decided) != {"cases", "tests"}:
        raise RegisterError("decided_by fields are not cases, tests")
    for name in ("files", "rules", "records"):
        _strings(text[name], f"ve_text.{name}")
    for name in ("cases", "tests"):
        _strings(decided[name], f"decided_by.{name}")
    if row["status"] == "OPEN":
        if row["family"] not in FAMILIES:
            raise RegisterError("an OPEN row names no feature family of the basis")
    elif row["status"] == "VERIFIED":
        if row["family"] is not None:
            raise RegisterError("a VERIFIED row names a missing feature family")
        if not text["files"]:
            raise RegisterError("a VERIFIED row names no VE text")
        links = decided["cases"] if row["usecase"] == "agent-policy" else decided["tests"]
        if not links:
            raise RegisterError("a VERIFIED row links no answer-key case or named test")
        if row["usecase"] != "agent-policy" and (decided["cases"] or text["rules"] or text["records"]):
            raise RegisterError("only agent-policy rows link answer-key cases, rules or records")
    else:
        raise RegisterError(f"status {row['status']!r} is not VERIFIED or OPEN")


def rows_of(register):
    """The frozen rows, then the appended ones; raises RegisterError on a changed or malformed register."""
    if type(register) is not dict or set(register) != {"header", "rows", "appended"}:
        raise RegisterError("register fields are not header, rows, appended")
    header, rows, appended = register["header"], register["rows"], register["appended"]
    if type(header) is not dict or set(header) != HEADER_KEYS or any(type(v) is not str for v in header.values()):
        raise RegisterError(f"header fields are not the strings {sorted(HEADER_KEYS)}")
    if type(rows) is not list or not rows or type(appended) is not list:
        raise RegisterError("rows is not a non-empty list, or appended is not a list")
    if rows_sha256(rows) != header["rows_sha256"]:
        raise RegisterError("the frozen rows do not match the header's SHA-256 (rows are appended, never edited)")
    for row in appended:
        if type(row) is not dict or type(row.get("date")) is not str or not row["date"]:
            raise RegisterError("an appended row has no date")
    ids = [row.get("id") if type(row) is dict else None for row in rows + appended]
    if len(set(map(repr, ids))) != len(ids):
        raise RegisterError("a row id repeats")
    return [(row, ROW_KEYS) for row in rows] + [(row, APPENDED_KEYS) for row in appended]


def _sorted(value):
    if type(value) is not list:
        raise RegisterError("a compared answer is not a list")
    return sorted(value, key=lambda item: json.dumps(item, sort_keys=True))


def case_agrees(case: str, key: dict, results: dict) -> bool:
    """Whether results.json gives the answer the key states for one linked case.

    Raises RegisterError when the case is not in the key or not in results.json."""
    kind, _, name = case.partition(":")
    try:
        if kind in ("action", "report"):
            want, got = key["actions"][name], results["actions"][name]
            if kind == "report":
                return type(got["rule_25"]) is str and got["rule_25"] == want["rule_25"]
            got = got["permission"]
            return type(got["verdict"]) is str and got["verdict"] == want["verdict"] and all(
                _sorted(got[side]) == _sorted(want[side]) for side in ("positive", "negative", "open"))
        if kind == "policy" and name in POLICY_FIELDS:
            want, got = key["policy"][name], results["policy_summary"][POLICY_FIELDS[name]]
            if name == "required_overlaps":
                return all(pair in _sorted(got) for pair in _sorted(want))
            if name == "gap_tools":
                got = [tool for tool in _sorted(got) if tool != UNDECLARED_TOOL]
            if type(want) is list:
                return _sorted(got) == _sorted(want)
            return type(got) is type(want) and got == want
        if case == "obligation:covered":
            return _sorted(results["comparison"]["obligation"]["covered"]) == _sorted(key["obligation"]["covered"])
        if case == "default:sensitive":
            return _sorted(results["comparison"]["M4_default_sensitive"]) == _sorted(key["forced_default_sensitive"])
    except (KeyError, TypeError) as error:
        raise RegisterError(f"case {case} is not in the answer key and results.json ({error!r})") from None
    raise RegisterError(f"case {case} is not a case kind of the register")


def _checked_text(row, results, manifest):
    """Raises RegisterError unless the row's VE text is the text VE checked for results.json."""
    text, inputs = row["ve_text"], results.get("inputs")
    names = {block.get("name") for block in manifest.get("blocks", []) if type(block) is dict}
    for path in text["files"]:
        file = REPO / path
        if not file.is_file():
            raise RegisterError(f"VE text {path} does not exist")
        if path.startswith("usecases/agent-policy/"):
            if type(inputs) is not dict or inputs.get(file.name) != file_sha256(file):
                raise RegisterError(f"VE text {path} is not the text results.json was checked on")
        elif not path.startswith(f"usecases/{row['usecase']}/"):
            raise RegisterError(f"VE text {path} is outside usecases/{row['usecase']}")
    if text["rules"]:
        policy = "usecases/agent-policy/policy.ve"
        if policy not in text["files"] or manifest.get("text_digest") != file_sha256(REPO / policy):
            raise RegisterError("the rules are not bound by policy.manifest.json to the checked policy.ve")
        for rule in text["rules"]:
            if rule not in names:
                raise RegisterError(f"rule {rule!r} is not in policy.manifest.json")
    if text["records"]:
        if "usecases/agent-policy/log.ve" not in text["files"]:
            raise RegisterError("log records are named without log.ve")
        for record in text["records"]:
            if record not in results.get("actions", {}):
                raise RegisterError(f"log record {record!r} is not in results.json")


def run_pytest(nodeids):
    """The named tests that pass, each run on its own."""
    passed = set()
    for nodeid in nodeids:
        run = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", nodeid],
                             cwd=REPO, capture_output=True, text=True)
        if run.returncode == 0:
            passed.add(nodeid)
    return passed


def measure(register, key, results, manifest, run_tests=run_pytest):
    """{"verified", "source", "open": {family: bytes}, "rows": {id: status}, "failures": [...]}.

    A row that fails a check counts in no verified or OPEN total; when the
    register itself is malformed nothing is counted."""
    level = {"verified": 0, "source": 0, "open": {family: 0 for family in FAMILIES}, "rows": {}, "failures": []}
    try:
        rows = rows_of(register)
    except RegisterError as error:
        level["failures"].append(f"register: {error}")
        return level
    shaped = []
    for row, keys in rows:
        try:
            _row_shape(row, keys)
            shaped.append(row)
        except RegisterError as error:
            level["failures"].append(f"{row.get('id', '?') if type(row) is dict else '?'}: {error}")
    tests = sorted({test for row in shaped if row["status"] == "VERIFIED" for test in row["decided_by"]["tests"]})
    passed = run_tests(tests) if tests else set()
    for row in shaped:
        level["source"] += row["bytes"]
        try:
            if row["status"] == "VERIFIED":
                _checked_text(row, results, manifest)
                for case in row["decided_by"]["cases"]:
                    if not case_agrees(case, key, results):
                        raise RegisterError(f"linked case {case} does not agree in results.json")
                for test in row["decided_by"]["tests"]:
                    if test not in passed:
                        raise RegisterError(f"named test {test} does not pass")
                level["verified"] += row["bytes"]
            else:
                level["open"][row["family"]] += row["bytes"]
            level["rows"][row["id"]] = row["status"]
        except RegisterError as error:
            level["failures"].append(f"{row['id']}: {error}")
        except (AttributeError, KeyError, TypeError, RecursionError) as error:
            level["failures"].append(f"{row['id']}: malformed results, key or manifest ({error!r})")
    return level


def _read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--register", default=HERE / "requirements.json")
    parser.add_argument("--results", default=HERE / "results.json")
    parser.add_argument("--key", default=HERE / "answer-key.json")
    parser.add_argument("--manifest", default=HERE / "policy.manifest.json")
    parser.add_argument("--json", action="store_true", help="print the level as JSON")
    args = parser.parse_args(argv)
    level = measure(_read(args.register), _read(args.key), _read(args.results), _read(args.manifest))
    if args.json:
        print(json.dumps(level, indent=2, ensure_ascii=False))
    else:
        print(f"verified bytes: {level['verified']}")
        print(f"source bytes: {level['source']}")
        for family, size in sorted(level["open"].items(), key=lambda item: (-item[1], item[0])):
            print(f"OPEN bytes, {family}: {size}")
        for failure in level["failures"]:
            print(f"FAIL {failure}", file=sys.stderr)
    return 1 if level["failures"] else 0


if __name__ == "__main__":
    sys.exit(main())
