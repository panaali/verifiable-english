"""Every enumeration of the response schemas is kept by the encoder theorems (shapes-fix3, B4).

The skeleton a row is proved against kept a field's allowed values only for a field named `status`,
so Lean proved rows with `document_status`, `point_status`, a conflict `verdict` or `gaps` outside
their enums while `service_schema.check_row` rejected them. `ResponseShape.EnumSites` lists every
`enum` and `const` of the Lean schemas and every field whose value resolves to one; this test

* checks that list against the rendered schema files (`ve/backends/lean_service_schema/`, walked
  here independently, failing on any keyword it does not know), so no declaration is missed;
* has Lean prove, for every such field, that each declared value fits the field's extracted
  skeleton, and that `BOGUS` and every value another field of the same name declares (the opposite
  verdict, another status word) do not (`¬ Fits`, by `Fits.not_of_admits`);
* keeps the reviewer's row probes (document_status, point_status, the two conflict verdicts).
"""
from __future__ import annotations

import json
import shutil
import subprocess

import pytest

from subprocesses import HANG_TIMEOUT
from tests.lean_build import LEAN, ROOT, lean_build

SCHEMAS = ROOT / "ve/backends/lean_service_schema"

HEADER = """import ResponseShape.EnumSites
import ResponseShape.FitsTactic
import VE.Service.Protocol
open Lean ResponseShape ResponseShape.Skeletons ResponseShape.EnumSites
"""

# The declarations a runner copies from the request (`Shape.copied`): the client checks them, the
# encoder theorems do not. A new one must be added here on purpose.
COPIED = {("discourse.json", "/$defs/reference/properties/form/enum")}

KEYWORDS = {"$ref", "$comment", "type", "enum", "const", "pattern", "minLength", "maxLength", "minimum",
            "required", "properties", "additionalProperties", "prefixItems", "items", "minItems", "maxItems",
            "contains", "anyOf", "allOf", "not", "if", "then", "else", "x-tagged", "x-fuel", "x-echo",
            "x-equals", "x-length", "x-count", "x-references", "x-index", "x-digest", "x-zip", "x-case",
            "x-select", "x-count-where", "x-count-presence", "x-rows", "x-row"}


@pytest.fixture(scope="module")
def lake():
    path = shutil.which("lake")
    if path is None:
        pytest.skip("lake is not available")
    lean_build("ResponseShape")
    return path


def _lean(lake, tmp_path, body: str) -> subprocess.CompletedProcess:
    source = tmp_path / "EnumDomains.lean"
    source.write_text(HEADER + body)
    return subprocess.run([lake, "env", "lean", str(source)], cwd=LEAN, capture_output=True, text=True,
                          timeout=HANG_TIMEOUT)


@pytest.fixture(scope="module")
def listed(lake, tmp_path_factory):
    """(sites, probes) as `ResponseShape.EnumSites` lists them."""
    done = _lean(lake, tmp_path_factory.mktemp("sites"),
                 "#eval IO.println (toJson (sites Schemas.files, probes Schemas.files)).compress\n")
    assert done.returncode == 0, done.stdout + done.stderr
    sites, probes = json.loads(done.stdout)
    return sites, probes


def _escape(token: str) -> str:
    return token.replace("~", "~0").replace("/", "~1")


def _walk(node, pointer: str, role: str, out: list) -> None:
    """Every `enum` and `const` under one schema of the rendered dialect, with its role."""
    if not isinstance(node, dict):
        return
    condition = "condition" if role == "value" else role
    for key, value in node.items():
        here = f"{pointer}/{_escape(key)}"
        if key not in KEYWORDS:
            raise AssertionError(f"unknown schema keyword {key} at {pointer}")
        if key == "enum":
            out.append((here, role, value))
        elif key == "const":
            out.append((here, role, [value]))
        elif key == "properties":
            for name, sub in value.items():
                _walk(sub, f"{here}/{_escape(name)}", role, out)
        elif key in ("prefixItems", "anyOf", "allOf"):
            for i, sub in enumerate(value):
                _walk(sub, f"{here}/{i}", role, out)
        elif key in ("items", "additionalProperties", "then", "else", "x-rows"):
            _walk(value, here, role, out)
        elif key in ("not", "contains", "if", "x-case"):
            _walk(value, here, condition, out)
        elif key == "x-tagged":
            for tag, slots in value.items():
                for i, sub in enumerate(slots):
                    _walk(sub, f"{here}/{_escape(tag)}/{i}", "grammar" if role == "value" else role, out)
        elif key == "x-select":
            for i, entry in enumerate(value):
                _walk(entry["when"], f"{here}/{i}/when", condition, out)
                _walk(entry["then"], f"{here}/{i}/then", role, out)
        elif key == "x-zip":
            _walk(value["items"], f"{here}/items", role, out)
        elif key == "x-count-where":
            _walk(value["where"], f"{here}/where", condition, out)


def _rendered_sites() -> set:
    """(file, pointer, role, values) of every declaration in the rendered schema files."""
    found = set()
    for path in sorted(SCHEMAS.glob("*.json")):
        document = json.loads(path.read_text())
        out: list = []
        for key, value in document.items():
            if key in ("$id", "$comment"):
                continue
            if key != "$defs":
                _walk(value, f"/{_escape(key)}", "value", out)
                continue
            for name, entry in value.items():
                base = f"/$defs/{_escape(name)}"
                if not isinstance(entry, dict) or all(k in KEYWORDS for k in entry):
                    _walk(entry, base, "value", out)
                else:  # a group of named schemas
                    for member, sub in entry.items():
                        if member != "$comment":
                            _walk(sub, f"{base}/{_escape(member)}", "value", out)
        found |= {(path.name, pointer, role, json.dumps(values)) for pointer, role, values in out}
    return found


def test_every_declaration_is_listed(listed):
    """The Lean list is exactly the rendered files' declarations, roles included."""
    sites, _ = listed
    lean = {(s["file"], s["pointer"], "value" if s["role"] == "copied" else s["role"], json.dumps(s["values"]))
            for s in sites}
    assert lean == _rendered_sites()
    assert len(lean) > 300


def test_copied_declarations_are_the_known_ones(listed):
    sites, _ = listed
    assert {(s["file"], s["pointer"]) for s in sites if s["role"] == "copied"} == COPIED


def test_every_value_declaration_has_a_proved_field(listed):
    """Every declaration a row uses as a value (through any reference) is the domain of a probed field."""
    sites, probes = listed
    reached = {site for p in probes for site in p["sites"]}
    values = {f'{s["file"]}#{s["pointer"]}' for s in sites if "value" in s["uses"]}
    assert values - reached == set()
    assert len(values) > 200


def _lean_value(value) -> str | None:
    """The Lean term of a JSON value the probes use, or None."""
    if isinstance(value, bool):
        return f".bool {'true' if value else 'false'}"
    if value is None:
        return ".null"
    if isinstance(value, str):
        return ".str " + json.dumps(value, ensure_ascii=False)
    if isinstance(value, int):
        return f"(toJson ({value} : Int))"
    if isinstance(value, list) and all(isinstance(x, str) for x in value):
        return "(toJson [" + ", ".join(json.dumps(x, ensure_ascii=False) for x in value) + "] : Json)"
    return None


def _name(probe) -> str:
    """A field's name; an array's items and an object's other properties go by their property's."""
    if probe["name"] not in ("[]", "*"):
        return probe["name"]
    tokens = probe["pointer"].split("/")
    named = [tokens[i + 1] for i, t in enumerate(tokens[:-1]) if t == "properties"]
    return (named[-1] if named else probe["pointer"]) + probe["name"]


def _probe_examples(probes) -> tuple[str, int, int]:
    """The Lean examples of every probe: each value fits; BOGUS and the siblings' strings do not when
    every string of the field is declared (`strings`), the opposite Boolean when every value is (`exact`)."""
    by_name: dict[str, set] = {}
    for p in probes:
        by_name.setdefault(_name(p), set()).update(json.dumps(v) for v in p["values"] if isinstance(v, str))
    lines, positive, negative = [], 0, 0
    for i, p in enumerate(probes):
        lines.append(f"abbrev probe{i} : Skel := fieldSkel% {i}")
        own = {json.dumps(v) for v in p["values"]}
        for v in p["values"]:
            term = _lean_value(v)
            assert term is not None, (p, v)
            lines.append(f"example (req : Json) : Fits req probe{i} ({term}) := by fits")
            positive += 1
        rejected = set()
        if p["strings"]:
            rejected |= {json.dumps("BOGUS")} | (by_name[_name(p)] - own)
        if p["exact"]:
            rejected |= {json.dumps(not v) for v in p["values"] if isinstance(v, bool)} - own
        for v in sorted(rejected):
            term = _lean_value(json.loads(v))
            lines.append(f"example (req : Json) : ¬ Fits req probe{i} ({term}) := "
                         "Fits.not_of_admits (n := 64) (by decide)")
            negative += 1
    return "\n".join(lines) + "\n", positive, negative


def test_every_field_keeps_its_domain(lake, tmp_path, listed):
    """Each declared value is proved to fit its field; BOGUS and the siblings' values are proved not to."""
    _, probes = listed
    body, positive, negative = _probe_examples(probes)
    assert positive > 500 and negative > 500, (positive, negative)
    done = _lean(lake, tmp_path, body)
    assert done.returncode == 0 and "error" not in done.stdout, (done.stdout + done.stderr)[-4000:]


def test_a_bogus_value_is_not_proved(lake, tmp_path, listed):
    """The probes are not vacuous: `fits` leaves BOGUS unproved on a field it proves a value of."""
    _, probes = listed
    i = next(i for i, p in enumerate(probes) if p["name"] == "document_status")
    done = _lean(lake, tmp_path, f'example (req : Json) : Fits req (fieldSkel% {i}) (.str "BOGUS") := by fits\n')
    assert done.returncode != 0 and "unsolved goals" in done.stdout, done.stdout


def _row(lake, tmp_path, target: str, fields: str) -> bool:
    done = _lean(lake, tmp_path, f"""
example (req : Json) (id t : String) (ts : List String) :
    Fits req (skel% "{target}") (Json.mkObj {fields}) := by
  fits
""")
    return done.returncode == 0 and "error" not in done.stdout


def _probe(probes, file: str, pointer: str) -> int:
    return next(i for i, p in enumerate(probes) if p["file"] == file and p["pointer"] == pointer)


@pytest.mark.parametrize("verdict, proved", [("CONFLICT", True), ("UNKNOWN", True), ("CONFLICT-FREE", False),
                                             ("BOGUS", False)])
def test_witness_conflict_verdict(lake, tmp_path, verdict, proved):
    fields = (f'[("id", .str id), ("status", .str "ok"), ("verdict", .str "{verdict}"), ("target", .str t), '
              '("targets", toJson ts)]')
    assert _row(lake, tmp_path, "common.json#/$defs/witness_conflict", fields) is proved


@pytest.mark.parametrize("verdict, proved", [("CONFLICT-FREE", True), ("CONFLICT", False), ("BOGUS", False)])
def test_packages_conflict_verdict(lake, tmp_path, verdict, proved):
    fields = f'[("id", .str id), ("status", .str "ok"), ("verdict", .str "{verdict}"), ("targets", toJson ts)]'
    assert _row(lake, tmp_path, "common.json#/$defs/packages_conflict", fields) is proved


@pytest.mark.parametrize("status, proved", [("SETTLED yes", True), ("UNKNOWN", True), ("BOGUS", False)])
def test_point_status(lake, tmp_path, status, proved):
    fields = f'[("id", .str id), ("status", .str "ok"), ("point_status", .str "{status}"), ("predicate", .str t)]'
    assert _row(lake, tmp_path, "norm-defaults.json#/$defs/status", fields) is proved


@pytest.mark.parametrize("status, proved", [("CHECKED", True), ("UNFORMALISED", True), ("BOGUS", False),
                                            ("FOLLOWS", False)])
def test_document_status(lake, tmp_path, listed, status, proved):
    """reports-status' document answer: the status words of `status_word`, by reference."""
    _, probes = listed
    i = _probe(probes, "reports.json", "/$defs/status/properties/document_status")
    done = _lean(lake, tmp_path, f'example (req : Json) : Fits req (fieldSkel% {i}) (.str "{status}") := by fits\n')
    assert (done.returncode == 0 and "error" not in done.stdout) is proved, done.stdout
