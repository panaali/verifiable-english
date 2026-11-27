"""usecases/pinned_sources.json, tools/fetch_pinned_sources.py, the test helper tests/pinned_source.py and the gate's
seeding of its fresh home (item actions-pinned-sources). No network: downloads are file:// fixtures."""
from __future__ import annotations

import ast
import hashlib
import json
import re
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


def _entry(data: bytes, url: str, *, text: bytes | None = None, extract=COPY, path="doc/doc.txt") -> dict:
    text = data if text is None else text
    return {"url": url, "pdf_sha256": hashlib.sha256(data).hexdigest(), "pdf_bytes": len(data),
            "extract": list(extract), "path": path, "text_sha256": hashlib.sha256(text).hexdigest(),
            "text_bytes": len(text)}


def _outcome(doc: str, **kwargs) -> tuple[str, str]:
    """("fail" | "skip" | "returned", message) of the helper: a skip never passes for a failure."""
    try:
        return "returned", str(pinned_source(doc, **kwargs))
    except pytest.fail.Exception as exc:
        return "fail", str(exc)
    except pytest.skip.Exception as exc:
        return "skip", str(exc)


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
        assert S.doc_source(case) == F.source_path(doc) == F.sources_root() / entry["path"], doc
        step = f"usecases/{doc}/source/extract_text.py"
        assert entry["extract"] == ["uv", "run", "--no-project", "--with", "pypdf==6.19.0", "python", "-I", step,
                                    "{pdf}", "{text}"], doc
        assert _constants(ROOT / step)["PDF_SHA256"] == entry["pdf_sha256"], doc
        assert entry["url"].startswith("https://") and entry["url"].endswith(".pdf"), doc


@pytest.mark.parametrize("change", [{"extra": 1}, {"pdf_bytes": "1"}, {"path": "/etc/x"}, {"path": "a/../../x"},
                                    {"path": "pins/doc.txt"}, {"path": "~/doc/x"}, {"path": "code/x/doc/doc.txt"},
                                    {"extract": ["cp", "{pdf}"]}])
def test_a_malformed_pin_is_refused(tmp_path, change):
    entry = {**_entry(b"x", "file:///x"), **change}
    with pytest.raises(ValueError):
        F.load(_pins(tmp_path, {"doc": entry}))


# --- the helper -------------------------------------------------------------------------------------------------------

def test_the_helper_fails_by_name_when_required_and_absent(tmp_path, monkeypatch):
    monkeypatch.setenv(F.REQUIRE, "1")
    for skip in (True, False):
        kind, said = _outcome("safety-framework", skip=skip, home=tmp_path)
        assert kind == "fail", (kind, said)
        assert re.fullmatch(r"the pinned source safety-framework is not stored at .*/fsf-3\.1\.txt "
                            r"\(VE_REQUIRE_PINNED_SOURCES=1; fetch it: .*\)", said), said


@pytest.mark.parametrize("required", ["1", None])
def test_the_helper_fails_by_name_when_the_hash_is_wrong(tmp_path, monkeypatch, required):
    """A stored text that is not its pin always fails, required or not (it never skips)."""
    if required:
        monkeypatch.setenv(F.REQUIRE, required)
    else:
        monkeypatch.delenv(F.REQUIRE, raising=False)
    entry = F.load()["anthropic-rsp"]
    stored = F.sources_root(tmp_path) / entry["path"]
    stored.parent.mkdir(parents=True)
    stored.write_bytes(b"x" * entry["text_bytes"])
    for skip in (True, False):
        kind, said = _outcome("anthropic-rsp", skip=skip, home=tmp_path)
        assert kind == "fail", (kind, said)
        assert re.match(r"the pinned source anthropic-rsp at .* has sha256 [0-9a-f]{64} \(59410 bytes\), not the pin "
                        r"c7de7fe2f1f4", said), said


@pytest.mark.parametrize("value", [None, "0", "", "yes"])
def test_the_helper_skips_when_not_required(tmp_path, monkeypatch, value):
    if value is None:
        monkeypatch.delenv(F.REQUIRE, raising=False)
    else:
        monkeypatch.setenv(F.REQUIRE, value)
    assert _outcome("openai-preparedness", home=tmp_path) == ("skip", SKIP_REASON)
    assert _outcome("openai-preparedness", skip=False, home=tmp_path) == ("returned", "None")
    assert SKIP_REASON == "the pinned source is not stored on this machine"  # tools/gate-optional.json's reason


def test_the_helper_returns_a_text_stored_at_its_pin(tmp_path, monkeypatch):
    monkeypatch.setenv(F.REQUIRE, "1")
    entry = _entry(b"pinned text\n", "file:///x")
    monkeypatch.setattr(F, "load", lambda pins=F.PINS: {"doc": entry})
    (tmp_path / "ve-sources/doc").mkdir(parents=True)
    (tmp_path / "ve-sources/doc/doc.txt").write_bytes(b"pinned text\n")
    assert pinned_source("doc", home=tmp_path) == tmp_path / "ve-sources/doc/doc.txt"


def test_gate_optional_still_allows_the_unset_skips():
    """Unset runs keep today's skip; the gate-optional rows name exactly the helper's reason."""
    rows = json.loads((ROOT / "tools/gate-optional.json").read_text())["optional_tests"]
    pinned = {r["nodeid"] for r in rows if r["reason"] == SKIP_REASON}
    assert "tests/test_safety_framework.py::test_every_will_quote_is_the_pinned_source_text" in pinned
    assert "tests/test_safety_framework.py::test_every_glossary_definition_is_the_pinned_source_text" in pinned


# --- the fetch step ---------------------------------------------------------------------------------------------------

def test_the_fetch_refuses_bytes_whose_sha256_is_not_the_pin(tmp_path, capsys):
    served = tmp_path / "served.pdf"
    served.write_bytes(b"the pinned bytez")  # the pinned size, another sha256
    entry = _entry(b"the pinned bytes", served.as_uri())
    home = tmp_path / "home"
    with pytest.raises(F.FetchError, match=r"served sha256 [0-9a-f]{64} \(16 bytes\), not the pin"):
        F.fetch("doc", entry, home)
    assert not (F.sources_root(home) / entry["path"]).exists()
    assert F.main(["--home", str(home)], pins=_pins(tmp_path, {"doc": entry})) == 1
    assert "FAILED doc: " in capsys.readouterr().out
    assert not home.exists()


def test_the_fetch_writes_the_text_when_both_pins_hold(tmp_path, capsys):
    served = tmp_path / "served.pdf"
    served.write_bytes(b"%PDF fixture\n")
    entry = _entry(b"%PDF fixture\n", served.as_uri())
    pins, home = _pins(tmp_path, {"doc": entry}), tmp_path / "home"
    assert F.main(["--home", str(home)], pins=pins) == 0
    assert (home / "ve-sources/doc/doc.txt").read_bytes() == b"%PDF fixture\n"
    assert F.main(["--home", str(home)], pins=pins) == 0  # already stored: checked, kept
    assert F.main(["--home", str(home), "--check"], pins=pins) == 0
    assert "already stored" in capsys.readouterr().out


def test_the_fetch_refuses_an_extraction_that_is_not_the_pinned_text(tmp_path):
    served = tmp_path / "served.pdf"
    served.write_bytes(b"%PDF fixture\n")
    entry = _entry(b"%PDF fixture\n", served.as_uri(), text=b"another extraction\n")
    with pytest.raises(F.FetchError, match="the extract step does not reproduce the pin"):
        F.fetch("doc", entry, tmp_path / "home")
    assert not (tmp_path / "home/ve-sources/doc/doc.txt").exists()


def test_the_fetch_never_overwrites_a_stored_text_that_is_not_its_pin(tmp_path, capsys):
    served = tmp_path / "served.pdf"
    served.write_bytes(b"%PDF fixture\n")
    entry = _entry(b"%PDF fixture\n", served.as_uri())
    stored = tmp_path / "home/ve-sources/doc/doc.txt"
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
    monkeypatch.delenv(F.SOURCES_ROOT, raising=False)
    entry = F.load()["safety-framework"]
    account, home = tmp_path / "account", tmp_path / "home"
    (account / "ve-sources" / entry["path"]).parent.mkdir(parents=True)
    (account / "ve-sources" / entry["path"]).write_bytes(b"stored\n")
    assert gate.seed_pinned_sources(home, account) == (
        "anthropic-rsp absent; openai-preparedness absent; safety-framework copied")
    target = home / "ve-sources" / entry["path"]
    assert target.read_bytes() == b"stored\n" and not target.is_symlink()
    assert F.REQUIRE in gate.STAGE_ENVIRONMENT["pytest"] and F.REQUIRE not in gate.ALLOWED_ENVIRONMENT
    monkeypatch.setenv(F.REQUIRE, "1")
    assert gate.pinned_requirement() == {F.REQUIRE: "1"}
    monkeypatch.setenv(F.REQUIRE, "true")
    assert gate.pinned_requirement() == {}
    monkeypatch.delenv(F.REQUIRE)
    assert gate.pinned_requirement() == {}


# --- the sources root (dri-relb-privacy-archives-1126, orchestrator 212741Z item D) -----------------------------------

def test_the_pins_hold_no_absolute_or_home_relative_path():
    """Each pinned path is relative to the sources root and starts with its document's name: no absolute path, no ~,
    no home-directory or checkout prefix (on main before this row each path began with a checkout under home)."""
    raw = (ROOT / "usecases/pinned_sources.json").read_text(encoding="utf-8")
    for doc, entry in json.loads(raw)["sources"].items():
        path = entry["path"]
        assert not Path(path).is_absolute() and not path.startswith("~") and ".." not in Path(path).parts, doc
        assert Path(path).parts[0] == doc, (doc, Path(path).parts[0][:2] + "***")
    assert "Path.home() / path" not in raw and "/home/" not in raw and "~/code" not in raw


def test_unset_root_is_ve_sources_under_home(tmp_path, monkeypatch):
    monkeypatch.delenv(F.SOURCES_ROOT, raising=False)
    monkeypatch.setenv("HOME", str(tmp_path))
    assert F.sources_root() == tmp_path / "ve-sources"
    entry = F.load()["safety-framework"]
    assert F.source_path("safety-framework") == tmp_path / "ve-sources" / entry["path"]
    assert S.doc_source(ROOT / "usecases/safety-framework") == tmp_path / "ve-sources" / entry["path"]
    monkeypatch.setenv(F.REQUIRE, "1")
    fake = _entry(b"pinned text\n", "file:///x")
    monkeypatch.setattr(F, "load", lambda pins=F.PINS: {"doc": fake})
    (tmp_path / "ve-sources/doc").mkdir(parents=True)
    (tmp_path / "ve-sources/doc/doc.txt").write_bytes(b"pinned text\n")
    assert pinned_source("doc") == tmp_path / "ve-sources/doc/doc.txt"


def test_a_set_root_is_where_every_reader_looks(tmp_path, monkeypatch):
    root = tmp_path / "elsewhere"
    monkeypatch.setenv(F.SOURCES_ROOT, str(root))
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    assert F.sources_root() == root
    for doc, entry in F.load().items():
        assert F.source_path(doc) == root / entry["path"] == S.doc_source(ROOT / "usecases" / doc), doc
    # a pins file of an older commit (a prefix before the document's name) names the same stored file
    assert F.stored_path("safety-framework", "x/y/safety-framework/source/fsf-3.1.txt") == \
        root / "safety-framework/source/fsf-3.1.txt"
    served = tmp_path / "served.pdf"
    served.write_bytes(b"%PDF fixture\n")
    fake = _entry(b"%PDF fixture\n", served.as_uri())
    assert F.main([], pins=_pins(tmp_path, {"doc": fake})) == 0
    assert (root / "doc/doc.txt").read_bytes() == b"%PDF fixture\n" and not (tmp_path / "home").exists()
    monkeypatch.setenv(F.REQUIRE, "1")
    monkeypatch.setattr(F, "load", lambda pins=F.PINS: {"doc": fake})
    assert pinned_source("doc") == root / "doc/doc.txt"


def test_the_gate_seeds_from_a_set_root(tmp_path, monkeypatch):
    root, home, account = tmp_path / "root", tmp_path / "home", tmp_path / "account"
    monkeypatch.setenv(F.SOURCES_ROOT, str(root))
    entry = F.load()["anthropic-rsp"]
    (root / entry["path"]).parent.mkdir(parents=True)
    (root / entry["path"]).write_bytes(b"stored\n")
    assert gate.seed_pinned_sources(home, account) == (
        "anthropic-rsp copied; openai-preparedness absent; safety-framework absent")
    assert (home / "ve-sources" / entry["path"]).read_bytes() == b"stored\n"
    assert F.SOURCES_ROOT not in gate.ALLOWED_ENVIRONMENT  # inside the gate the root is its fresh home's ve-sources
