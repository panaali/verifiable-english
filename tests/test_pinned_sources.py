"""usecases/pinned_sources.json, tools/fetch_pinned_sources.py, the test helper tests/pinned_source.py and the gate's
seeding of its fresh home (item actions-pinned-sources). No network: downloads are file:// fixtures."""
from __future__ import annotations

import ast
import hashlib
import json
import sys
from pathlib import Path

import pytest

from tests.pinned_source import SKIP_REASON, pinned_source
from tools import fetch_pinned_sources as F
from tools import gate
from tools.fidmech import segment as S

ROOT = Path(__file__).resolve().parents[1]
COPY = [sys.executable, "-I", "-c", "import shutil, sys; shutil.copyfile(sys.argv[1], sys.argv[2])", "{pdf}", "{text}"]


def _constants(path: Path) -> dict:
    """The module-level constant assignments of `path`, read without running it."""
    found = {}
    for node in ast.parse(path.read_text(encoding="utf-8")).body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name) \
                and isinstance(node.value, ast.Constant):
            found[node.targets[0].id] = node.value.value
    return found


def _entry(data: bytes, url: str, *, text: bytes | None = None, extract=COPY, path="pins/doc.txt") -> dict:
    text = data if text is None else text
    return {"url": url, "pdf_sha256": hashlib.sha256(data).hexdigest(), "pdf_bytes": len(data),
            "extract": list(extract), "path": path, "text_sha256": hashlib.sha256(text).hexdigest(),
            "text_bytes": len(text)}


def _pins(tmp_path: Path, entries: dict) -> Path:
    pins = tmp_path / "pins.json"
    pins.write_text(json.dumps({"version": 1, "about": "test", "sources": entries}), encoding="utf-8")
    return pins


# --- the pins file is the one place of each pin ---------------------------------------------------------------------

def test_the_pins_equal_each_build_document_and_extract_step():
    """Each pin's text sha256, size and path are build_document.py's TEXT_SHA256, TEXT_BYTES and DEFAULT_SOURCE; its
    PDF sha256 is the extract step's PDF_SHA256; its extract command runs that committed step with pypdf 6.19.0."""
    sources = F.load()
    assert sorted(sources) == ["anthropic-rsp", "openai-preparedness", "safety-framework"]
    for doc, entry in sources.items():
        case = ROOT / "usecases" / doc
        built = _constants(case / "build_document.py")
        assert (built["TEXT_SHA256"], built["TEXT_BYTES"]) == (entry["text_sha256"], entry["text_bytes"]), doc
        assert S.doc_source(case) == Path.home() / entry["path"], doc
        step = f"usecases/{doc}/source/extract_text.py"
        assert entry["extract"] == ["uv", "run", "--no-project", "--with", "pypdf==6.19.0", "python", "-I", step,
                                    "{pdf}", "{text}"], doc
        assert _constants(ROOT / step)["PDF_SHA256"] == entry["pdf_sha256"], doc
        assert entry["url"].startswith("https://") and entry["url"].endswith(".pdf"), doc


@pytest.mark.parametrize("change", [{"extra": 1}, {"pdf_bytes": "1"}, {"path": "/etc/x"}, {"path": "a/../../x"},
                                    {"extract": ["cp", "{pdf}"]}])
def test_a_malformed_pin_is_refused(tmp_path, change):
    entry = {**_entry(b"x", "file:///x"), **change}
    with pytest.raises(ValueError):
        F.load(_pins(tmp_path, {"doc": entry}))


# --- the helper -------------------------------------------------------------------------------------------------------

def test_the_helper_fails_by_name_when_required_and_absent(tmp_path, monkeypatch):
    monkeypatch.setenv(F.REQUIRE, "1")
    for skip in (True, False):
        with pytest.raises(pytest.fail.Exception, match=r"the pinned source safety-framework is not stored at .*"
                           r"VE_REQUIRE_PINNED_SOURCES=1"):
            pinned_source("safety-framework", skip=skip, home=tmp_path)


@pytest.mark.parametrize("required", ["1", None])
def test_the_helper_fails_by_name_when_the_hash_is_wrong(tmp_path, monkeypatch, required):
    """A stored text that is not its pin always fails, required or not (it never skips)."""
    if required:
        monkeypatch.setenv(F.REQUIRE, required)
    else:
        monkeypatch.delenv(F.REQUIRE, raising=False)
    entry = F.load()["anthropic-rsp"]
    stored = tmp_path / entry["path"]
    stored.parent.mkdir(parents=True)
    stored.write_bytes(b"x" * entry["text_bytes"])
    with pytest.raises(pytest.fail.Exception, match=r"the pinned source anthropic-rsp at .* has sha256 [0-9a-f]{64} "
                       r"\(59410 bytes\), not the pin c7de7fe2f1f4"):
        pinned_source("anthropic-rsp", skip=False, home=tmp_path)


@pytest.mark.parametrize("value", [None, "0", "", "yes"])
def test_the_helper_skips_when_not_required(tmp_path, monkeypatch, value):
    if value is None:
        monkeypatch.delenv(F.REQUIRE, raising=False)
    else:
        monkeypatch.setenv(F.REQUIRE, value)
    with pytest.raises(pytest.skip.Exception, match=SKIP_REASON):
        pinned_source("openai-preparedness", home=tmp_path)
    assert pinned_source("openai-preparedness", skip=False, home=tmp_path) is None
    assert SKIP_REASON == "the pinned source is not stored on this machine"  # tools/gate-optional.json's reason


def test_the_helper_returns_a_text_stored_at_its_pin(tmp_path, monkeypatch):
    monkeypatch.setenv(F.REQUIRE, "1")
    entry = _entry(b"pinned text\n", "file:///x")
    monkeypatch.setattr(F, "load", lambda pins=F.PINS: {"doc": entry})
    (tmp_path / "pins").mkdir()
    (tmp_path / "pins/doc.txt").write_bytes(b"pinned text\n")
    assert pinned_source("doc", home=tmp_path) == tmp_path / "pins/doc.txt"


def test_gate_optional_still_allows_the_unset_skips():
    """Unset runs keep today's skip; the gate-optional rows name exactly the helper's reason."""
    rows = json.loads((ROOT / "tools/gate-optional.json").read_text())["optional_tests"]
    pinned = {r["nodeid"] for r in rows if r["reason"] == SKIP_REASON}
    assert "tests/test_safety_framework.py::test_every_will_quote_is_the_pinned_source_text" in pinned


# --- the fetch step ---------------------------------------------------------------------------------------------------

def test_the_fetch_refuses_bytes_whose_sha256_is_not_the_pin(tmp_path, capsys):
    served = tmp_path / "served.pdf"
    served.write_bytes(b"other bytes")
    entry = {**_entry(b"the pinned bytes", served.as_uri())}
    home = tmp_path / "home"
    with pytest.raises(F.FetchError, match=r"served sha256 [0-9a-f]{64} \(11 bytes\), not the pin"):
        F.fetch("doc", entry, home)
    assert not (home / entry["path"]).exists()
    assert F.main(["--home", str(home)], pins=_pins(tmp_path, {"doc": entry})) == 1
    assert "FAILED doc: " in capsys.readouterr().out
    assert not home.exists()


def test_the_fetch_writes_the_text_when_both_pins_hold(tmp_path, capsys):
    served = tmp_path / "served.pdf"
    served.write_bytes(b"%PDF fixture\n")
    entry = _entry(b"%PDF fixture\n", served.as_uri())
    pins, home = _pins(tmp_path, {"doc": entry}), tmp_path / "home"
    assert F.main(["--home", str(home)], pins=pins) == 0
    assert (home / "pins/doc.txt").read_bytes() == b"%PDF fixture\n"
    assert F.main(["--home", str(home)], pins=pins) == 0  # already stored: checked, kept
    assert F.main(["--home", str(home), "--check"], pins=pins) == 0
    assert "already stored" in capsys.readouterr().out


def test_the_fetch_refuses_an_extraction_that_is_not_the_pinned_text(tmp_path):
    served = tmp_path / "served.pdf"
    served.write_bytes(b"%PDF fixture\n")
    entry = _entry(b"%PDF fixture\n", served.as_uri(), text=b"another extraction\n")
    with pytest.raises(F.FetchError, match="the extract step does not reproduce the pin"):
        F.fetch("doc", entry, tmp_path / "home")
    assert not (tmp_path / "home/pins/doc.txt").exists()


def test_the_fetch_never_overwrites_a_stored_text_that_is_not_its_pin(tmp_path, capsys):
    served = tmp_path / "served.pdf"
    served.write_bytes(b"%PDF fixture\n")
    entry = _entry(b"%PDF fixture\n", served.as_uri())
    stored = tmp_path / "home/pins/doc.txt"
    stored.parent.mkdir(parents=True)
    stored.write_bytes(b"edited\n")
    assert F.main(["--home", str(tmp_path / "home")], pins=_pins(tmp_path, {"doc": entry})) == 1
    assert "it is not overwritten" in capsys.readouterr().out
    assert stored.read_bytes() == b"edited\n"


def test_the_check_names_each_absent_document(tmp_path, capsys):
    assert F.main(["--home", str(tmp_path), "--check"]) == 1
    out = capsys.readouterr().out
    assert [line.split(":")[0] for line in out.splitlines()] == [
        "FAILED anthropic-rsp", "FAILED openai-preparedness", "FAILED safety-framework"]


# --- the gate ---------------------------------------------------------------------------------------------------------

def test_the_gate_copies_stored_sources_into_its_home_and_passes_the_requirement(tmp_path, monkeypatch):
    entry = F.load()["safety-framework"]
    account, home = tmp_path / "account", tmp_path / "home"
    (account / entry["path"]).parent.mkdir(parents=True)
    (account / entry["path"]).write_bytes(b"stored\n")
    assert gate.seed_pinned_sources(home, account) == (
        "anthropic-rsp absent; openai-preparedness absent; safety-framework copied")
    assert (home / entry["path"]).read_bytes() == b"stored\n" and not (home / entry["path"]).is_symlink()
    assert F.REQUIRE in gate.STAGE_ENVIRONMENT["pytest"] and F.REQUIRE not in gate.ALLOWED_ENVIRONMENT
    monkeypatch.setenv(F.REQUIRE, "1")
    assert gate.pinned_requirement() == {F.REQUIRE: "1"}
    monkeypatch.setenv(F.REQUIRE, "true")
    assert gate.pinned_requirement() == {}
    monkeypatch.delenv(F.REQUIRE)
    assert gate.pinned_requirement() == {}
