"""The `purposes@0` wire table in shadow (sa-wire-purposes0): `VE.Purposes.Wire`'s decoder still decides; the
contract names spec 7.1's row (and 7.2's row 2) of a refused block, with spec 7's text, in both engines, and no
document-mode answer depends on it."""

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re

import pytest

from conformance.purposes_contract import REGISTRY, bound, lean_record, legacy_validation, purposes_block
from conformance.wire_contract_engine import CLEAN, Fault, load, run
from conformance.wire_contract_faults import catalogue, expected_record, rendered
from conformance.wire_contract_faults_purposes import EXAMPLES, limit, link, refused
from tests import lean_routes
from ve.backends.lean_service import LeanService
from ve.backends.relay import answer
from ve.errors import CheckerUnavailable, VEError

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = load("purposes@0")
UNIT_FILES = ("ve/wire_contract/purposes@0.json", "conformance/purposes_contract.py",
              "conformance/wire_contract_faults_purposes.py", "lean/VE/WireContract/Hooks/Purposes.lean")
SPEC = ROOT / "docs/spec/purpose-explanation.md"
# Main's document-mode answers, recorded with the merge base's `ve_service` (`record`).
MAIN = ROOT / "docs/wire-contract/sa-wire-purposes0/shadow-main.json"
DOCUMENT = ROOT / "usecases/bluedot-grant/causal.ve.md"
# The other document-mode fixtures under 8 KB (the larger ones are part documents of whole-document runs).
FIXTURES = tuple(ROOT / p for p in ("tests/data/rd9-docroute.ve.md", "usecases/question-answering/group.ve.md",
                                    "tests/data/premise-scale/qt0p-companion.ve.md"))
pytestmark = pytest.mark.skipif(not lean_routes.SERVICE.exists(), reason="ve_service is not built")


def accepted():
    return [json.loads((EXAMPLES / f"{name}.json").read_text())["purposes"] for name in ("base", "limit")]


def members():
    return [m for phase in CONTRACT["phases"] for check in phase["checks"] for m in check["emits"]]


def spec_texts(section, end):
    text = SPEC.read_text()
    rows = text[text.index(section):text.index(end)].splitlines()
    return [row.rsplit("| `", 1)[1].split("`")[0] for row in rows if row.startswith("| ") and "| `" in row]


def test_the_limit_is_leans_and_never_copied():
    numerals = re.compile(rf"(?<![0-9])({limit()}|{limit() + 1})(?![0-9])")
    for relative in UNIT_FILES:
        assert not numerals.search((ROOT / relative).read_text()), relative
    assert accepted()[1] == {"links": [link(i) for i in range(limit())]}
    over = refused()["links-over"]
    assert over["purposes"] == {"links": [link(i) for i in range(limit() + 1)]} and over["args"] == {"limit": str(limit())}


def test_the_contract_registers_spec_7s_texts_verbatim_and_in_fault_order():
    """7.1's rows 2-9 are members 1.1b-1.1i and 7.2's row 2 is 2.1b, in order, each text with its placeholders."""
    def shape(text):
        return re.sub(r"\{[a-z]+\}|<[a-z]+>", "{}", text.replace("link n ", "link {} ").replace(f"exceed {limit()}", "exceed {}"))
    decode = spec_texts("### 7.1 Decoding", "### 7.2")
    check = spec_texts("### 7.2 Checking", "### 7.3")
    assert [m["id"] for m in members()] == ["1.1b", "1.1c", "1.1d", "1.1e", "1.1f", "1.1g", "1.1h", "1.1i", "2.1b"]
    assert [shape(m["text"]) for m in members()] == [shape(t) for t in decode[1:] + check[1:2]]


def test_the_examples_are_accepted_and_clean_in_both_engines():
    for block in accepted():
        legacy_validation(deepcopy(block))
        assert run(CONTRACT, {"purposes": block}, registry=REGISTRY) is CLEAN
    rows = lean_routes.diagnose("purposes@0", [{"id": "c", "purposes": b} for b in accepted()])
    assert [row["outcome"] for row in rows] == ["clean", "clean"]


def test_every_refused_example_round_trips_through_the_contract_in_both_engines():
    """Lean's record has the example's row, arguments and spec 7 text; Python renders the same record from the table;
    the legacy validator raises that text exactly for a decoding row."""
    faults = catalogue("purposes@0")
    assert {f.name for f in faults} == set(refused()) and len({f.check for f in faults}) == len(members())
    rows = lean_routes.diagnose("purposes@0", [{"id": f.name, "purposes": refused()[f.name]["purposes"]} for f in faults])
    for fault, row in zip(faults, rows):
        example, record = refused()[fault.name], row["diagnostic"]
        assert {k: record[k] for k in expected_record(CONTRACT, fault)} == expected_record(CONTRACT, fault), fault.name
        assert record["text"] == example["text"] == rendered(next(m["text"] for m in members() if m["id"] == fault.check),
                                                               example["args"]), fault.name
        python = run(CONTRACT, {"purposes": deepcopy(example["purposes"])}, registry=REGISTRY)
        assert isinstance(python, Fault) and {k: python.record[k] for k in record} == record, fault.name
        if record["phase"] == "decode":
            with pytest.raises(VEError, match=re.escape(example["text"])):
                legacy_validation(example["purposes"])
        else:
            legacy_validation(example["purposes"])


def test_the_relay_refuses_a_retyped_or_rebound_record():
    genuine = lean_routes.diagnose("purposes@0", [{"id": "c", "purposes": refused()["polarity"]["purposes"]}])[0]
    assert bound(deepcopy(genuine))["check"] == "1.1g"
    assert bound({"id": "c", "status": "ok", "outcome": "clean"}) is None
    def mutated(path, value):
        row = deepcopy(genuine)
        *head, last = path
        target = row
        for key in head:
            target = target[key]
        if value is KeyError:
            del target[last]
        else:
            target[last] = value
        return row
    d = ("diagnostic",)
    for path, value in [(("status",), "error"), (("outcome",), "maybe"), (("outcome",), "clean"), (d + ("check",), "absent"),
                        (d + ("check",), "1.1"), (d + ("check",), "2.1b"), (d + ("check",), "1.1f"), (d + ("check",), KeyError),
                        (d + ("phase",), "check"), (d + ("path",), "/purposes/links"), (d + ("args",), {}),
                        (d + ("args",), {"link": "l1", "polarity": "doubted", "id": "l1"}), (d + ("args",), None),
                        (d + ("args", "link"), 7), (d + ("args", "polarity"), KeyError), (d, None), (d, KeyError),
                        (d + ("code",), "NOPE"), (d + ("code",), "PURPOSES_INVALID_BLOCK"), (d + ("class",), None),
                        (d + ("class",), "ResourceLimit"), (d + ("text",), 7), (d + ("text",), "InvalidPurposes: x"),
                        (d + ("text",), KeyError), (d + ("revision",), 2), (d + ("revision",), True),
                        (d + ("revision",), "1"), (d + ("contract",), "acts@0"), (d + ("extra",), 1)]:
        with pytest.raises(CheckerUnavailable):
            bound(mutated(path, value))


def test_the_adapters_read_the_case_block():
    rows = lean_routes.diagnose("purposes@0", [{"id": "a"}, {"id": "b", "purposes": accepted()[0], "other": 1}])
    assert [row.get("diagnostic", {}).get("check") for row in rows] == ["1.1b", None]
    assert purposes_block({"id": "a"}) == {"purposes": None}
    assert purposes_block({"id": "b", "purposes": 3}) == {"purposes": 3}


def name(path):
    return path.name.removesuffix(".ve.md")


def documents():
    """`DOCUMENT` as written, then with `purposes@0` listed and each example's block in its front matter, then the block
    without the profile, then the profile without a block; each of `FIXTURES` as written and with the base block listed."""
    def with_(path, block, listed=True):
        _, front, body = path.read_text().split("---\n", 2)
        f = json.loads(front)
        f["environment"]["profiles"] = sorted(f["environment"]["profiles"] + ["purposes@0"] * listed)
        if block is not KeyError:
            f["purposes"] = block
        return "---\n" + json.dumps(f, indent=2) + "\n---\n" + body
    blocks = {"base": accepted()[0], "limit": accepted()[1], **{n: v["purposes"] for n, v in refused().items()}}
    return {"plain": DOCUMENT.read_text(), **{f"listed-{n}": with_(DOCUMENT, b) for n, b in blocks.items()},
            "unlisted-base": with_(DOCUMENT, blocks["base"], listed=False),
            "listed-without-block": with_(DOCUMENT, KeyError),
            **{f"plain-{name(p)}": p.read_text() for p in FIXTURES},
            **{f"listed-base-{name(p)}": with_(p, blocks["base"]) for p in FIXTURES}}


def answers(executable=None):
    """Each document's answer through the production relay (`executable`'s service when given): the SHA-256 of its
    bytes (sorted keys, compact, without the case id), its status, error and identities."""
    cases = [{"id": name, "document": text, "admit": False} for name, text in documents().items()]
    if executable is None:
        rows = [answer("document", case)[0] for case in cases]
    else:
        with LeanService(executable) as service:
            rows = service.run("document", cases)
    def digest(row):
        return hashlib.sha256(json.dumps({**row, "id": None}, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return {row["id"]: {"sha256": digest(row), "status": row["status"],
                        **{k: row[k] for k in ("error", "document_id", "source_id") if k in row}} for row in rows}


def record(executable):
    """Write `MAIN` from the merge base's `ve_service` (run once, by hand, before the contract existed)."""
    rows = sorted(answers(executable).items())
    MAIN.write_text("{\n" + ",\n".join(f"{json.dumps(k)}: {json.dumps(v, sort_keys=True)}" for k, v in rows) + "\n}\n")


def test_the_contract_is_off_the_verdict_and_identity_paths():
    """Every document answer, its canonical bytes and identities included, is main's, whether the contract finds the
    block clean or names a row: the contract decides nothing and `purposes@0` is not admitted."""
    got, main = answers(), json.loads(MAIN.read_text())
    assert got == main
    for plain in ("plain", "plain-qt0p-companion"):  # the others need a composed route, and are refused alike
        assert main[plain]["status"] == "ok" and main[plain]["document_id"] and main[plain]["source_id"], plain
    listed = {main[name]["sha256"] for name in main if name.startswith("listed-") and name != "listed-without-block"}
    assert len(listed) == 1 and len(main) == len(refused()) + 5 + 2 * len(FIXTURES)
