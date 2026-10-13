"""AR-2, the narrow freeze (architecture decision D2): `lean/VE/Route/frozen.py` hashes only the files with K
declarations and the `ve.core@0.1` decoders, `ve/question/LOCK.json` hashes no module, and
`tools/trust_changes.py` lists the changed D[V] and G[V] files instead. The pre-commit hook's half of the rules
is in tests/test_precommit_hook.py."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
LEAN = ROOT / "lean"
sys.path.insert(0, str(ROOT / "tools"))
import trust_changes  # noqa: E402
from tests.subprocesses import HANG_TIMEOUT  # noqa: E402


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


frozen = load("ve_frozen_under_test", LEAN / "VE/Route/frozen.py")
TABLE = (LEAN / frozen.TABLE).read_text()
INVENTORY = (LEAN / frozen.INVENTORY).read_text()
MAIN = (LEAN / "Main.lean").read_text()


def tree(**edits: bytes | None):
    """The committed tree's reader with `edits` (path from `lean/`, `__` for `/`) over it; None deletes."""
    changed = {name.replace("__", "/") + ".lean": blob for name, blob in edits.items()}
    return lambda name: changed[name] if name in changed else frozen.read_tree(name)


def kernel_modules(table: str = TABLE) -> set[str]:
    return {module for module, classes in json.loads(table)["modules"].items() if classes.get("K")}


def test_the_list_is_the_k_files_and_the_core_decoders():
    names = frozen.frozen_names(TABLE)
    assert set(names) == kernel_modules() | set(frozen.DECODERS)
    assert sorted(frozen.recorded(INVENTORY)) == names
    assert frozen.problems(INVENTORY, TABLE, frozen.read_tree, MAIN) == []
    assert frozen.inventory_text() == INVENTORY
    # Far fewer than the 391 modules hashed before (plan 2.5): the kernel files and three decoders.
    assert len(names) < 40 < len(list((LEAN / "VE").rglob("*.lean")))


def test_each_decoder_defines_a_core_identity():
    """`DECODERS` names the files whose definitions are the ve.core@0.1 identities, not a hand-picked list of
    any decoders: each holds the identity code it is listed for."""
    texts = {name: (LEAN / name).read_text() for name in frozen.DECODERS}
    assert 'digest "ve-environment-v0.1\\n"' in texts["VE/CertificateWire.lean"]
    assert "def sha256 (input : ByteArray)" in texts["VE/CertificateWire.lean"]
    assert "def canonical : Nat → Json → Except String String" in texts["VE/CertificateWire.lean"]
    assert "def parse (text : String)" in texts["VE/Json.lean"]
    assert '"ve-environment-v0.1-order\\n"' in texts["VE/Order/Wire.lean"]


def test_an_unhashed_edit_of_a_k_file_fails():
    kernel = sorted(kernel_modules())[0]
    edited = (LEAN / kernel).read_bytes() + b"\n-- Unreviewed edit.\n"
    assert frozen.problems(INVENTORY, TABLE, tree(**{kernel.removesuffix(".lean").replace("/", "__"): edited}),
                           MAIN) == [f"{kernel}: frozen file changed without an inventory update"]
    decoder = frozen.DECODERS[0]
    edited = (LEAN / decoder).read_bytes() + b"\n-- Unreviewed edit.\n"
    reader = tree(**{decoder.removesuffix(".lean").replace("/", "__"): edited})
    assert frozen.problems(INVENTORY, TABLE, reader, MAIN) == [
        f"{decoder}: frozen file changed without an inventory update"]
    # After `--write` (the inventory of the edited tree) it passes.
    assert frozen.problems(frozen.render(frozen.frozen_names(TABLE), reader), TABLE, reader, MAIN) == []


def test_other_modules_and_new_modules_need_no_line():
    edited = (LEAN / "VE/Service/Document.lean").read_bytes() + b"\n-- An edit.\n"
    reader = tree(VE__Service__Document=edited, VE__Core__Planted=b"namespace VE\nend VE\n")
    assert "VE/Service/Document.lean" not in frozen.recorded(INVENTORY)
    assert frozen.problems(INVENTORY, TABLE, reader, MAIN) == []
    # A question module, too: and the question lock names none (an edit needs no LOCK.json update).
    assert not any(name.startswith("VE/Question/") for name in frozen.recorded(INVENTORY))


def test_a_new_k_module_must_be_listed_and_a_listed_file_must_be_frozen():
    table = json.loads(TABLE)
    table["modules"]["VE/Core/Planted.lean"] = {"K": ["VE.Planted"]}
    reader = tree(VE__Core__Planted=b"namespace VE\nend VE\n")
    assert frozen.problems(INVENTORY, json.dumps(table), reader, MAIN) == [
        "VE/Core/Planted.lean: frozen file (K declarations or a ve.core@0.1 decoder) is not listed"]
    written = frozen.render(frozen.frozen_names(json.dumps(table)), reader)
    assert frozen.problems(written, json.dumps(table), reader, MAIN) == []
    extra = INVENTORY + f"{hashlib.sha256((LEAN / 'VE/Surface.lean').read_bytes()).hexdigest()}  VE/Surface.lean\n"
    assert frozen.problems(extra, TABLE, frozen.read_tree, MAIN) == [
        "VE/Surface.lean: listed but neither holds a K declaration nor is a ve.core@0.1 decoder"]
    kernel = sorted(kernel_modules())[0]
    assert frozen.problems(INVENTORY, TABLE, tree(**{kernel.removesuffix(".lean").replace("/", "__"): None}),
                           MAIN) == [f"{kernel}: frozen file deleted but still listed"]


def test_main_lean_rule_is_unchanged():
    assert frozen.problems(INVENTORY, TABLE, frozen.read_tree, MAIN + "-- edit\n") == [
        "Main.lean: existing subcommands changed"]
    route = frozen.ROUTE_LINES[1]
    assert frozen.problems(INVENTORY, TABLE, frozen.read_tree, MAIN.replace(route, "")) == [
        f"Main.lean: expected exactly one {route.strip()!r}"]
    assert frozen.MAIN_BASE == "1bd244f8ff087d3f81e7302a0938ceab9d107e9efd609d97e41b23c0eb36c26d"


def test_a_hand_edited_inventory_is_refused():
    assert frozen.problems(INVENTORY.replace("# Generated", "# Hand"), TABLE, frozen.read_tree, MAIN) == [
        f"{frozen.INVENTORY}: not in the form `--write` writes"]


def test_an_edit_of_a_question_module_needs_no_lock_update(tmp_path):
    lock = json.loads((ROOT / "ve/question/LOCK.json").read_text())
    assert lock == {"format": "ve.question-lock@2", "question_version": lock["question_version"]}
    # A copy of the tool, its inputs and the Question modules, one of them edited: the lock still passes.
    for relative in ("tools/question_lock.py", "ve/question/codes.json", "ve/question/LOCK.json"):
        (tmp_path / relative).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / relative).write_bytes((ROOT / relative).read_bytes())
    (tmp_path / "lean/VE/Question").mkdir(parents=True)
    for path in (LEAN / "VE/Question").glob("*.lean"):
        (tmp_path / "lean/VE/Question" / path.name).write_bytes(path.read_bytes() + b"\n-- An edit.\n")
    done = subprocess.run([sys.executable, "tools/question_lock.py"], cwd=tmp_path, capture_output=True, text=True,
                          timeout=HANG_TIMEOUT)
    assert (done.returncode, done.stdout) == (0, "PASS: ve/question/LOCK.json records the service's question "
                                                 "version\n"), done.stderr


# The changed-files report: a fixture repository of one decoder and one glue module.

DECODER = "namespace VE.Demo\n\ndef decodeThing (s : String) : Nat :=\n  s.length\n\nend VE.Demo\n"
GLUE = "namespace VE.Glue\n\ndef glue : Nat := 1\n\nend VE.Glue\n"


def declarations(root: Path, ranges: dict[str, str]) -> None:
    rows = ["-- header\n"]
    for module, entry in ranges.items():
        path = root / "lean" / (module.replace(".", "/") + ".lean")
        if path.exists():
            rows.append(f"module {module} {hashlib.sha256(path.read_bytes()).hexdigest()}\n{entry}@{module}\n")
    (root / "lean/declarations.txt").write_text("".join(rows))
    modules = [m for m in ranges if (root / "lean" / (m.replace(".", "/") + ".lean")).exists()]
    (root / "lean/predicates.txt").write_text("-- header\n" + "".join(f"module {m}\n" for m in modules))


def git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), "-c", "user.name=t", "-c", "user.email=t@example.invalid",
                           "-c", "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null", *args],
                          capture_output=True, text=True, check=True).stdout.strip()


def fixture_repo(root: Path) -> str:
    (root / "lean/VE").mkdir(parents=True)
    (root / "tools").mkdir()
    (root / "lean/VE/Demo.lean").write_text(DECODER)
    (root / "lean/VE/Glue.lean").write_text(GLUE)
    (root / "lean/statements.txt").write_text("")
    (root / "tools/trust-classes.json").write_text(json.dumps({"modules": {
        "VE/Demo.lean": {"D[V]": ["VE.Demo.decodeThing"]}, "VE/Glue.lean": {"G[V]": ["VE.Glue.glue"]}}}))
    declarations(root, {"VE.Demo": "3:0-4:10 def VE.Demo.decodeThing", "VE.Glue": "3:0-3:20 def VE.Glue.glue"})
    git(root, "init", "-q")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "base")
    return git(root, "rev-parse", "HEAD")


def changes(root: Path, base: str, capsys) -> dict:
    assert trust_changes.main(["--since", base, "--root", str(root), "--json"]) == 0
    return json.loads(capsys.readouterr().out)


def test_a_body_only_edit_of_a_dv_file_is_reported(tmp_path, capsys):
    base = fixture_repo(tmp_path)
    assert changes(tmp_path, base, capsys) == {"changed": {}, "deleted": [], "by_class": {"D[V]": [], "G[V]": []}}
    # The body changes, the statement (`decodeThing : String → Nat`) does not.
    (tmp_path / "lean/VE/Demo.lean").write_text(DECODER.replace("s.length", "s.length + 1"))
    declarations(tmp_path, {"VE.Demo": "3:0-4:14 def VE.Demo.decodeThing", "VE.Glue": "3:0-3:20 def VE.Glue.glue"})
    out = changes(tmp_path, base, capsys)
    assert out["by_class"] == {"D[V]": ["VE/Demo.lean"], "G[V]": []}
    assert out["changed"] == {"VE/Demo.lean": {"K": 0, "S": 0, "D[V]": 3, "G[V]": 0}}
    (tmp_path / "lean/VE/Glue.lean").unlink()
    declarations(tmp_path, {"VE.Demo": "3:0-4:14 def VE.Demo.decodeThing"})
    table = json.loads((tmp_path / "tools/trust-classes.json").read_text())
    del table["modules"]["VE/Glue.lean"]
    (tmp_path / "tools/trust-classes.json").write_text(json.dumps(table))
    assert changes(tmp_path, base, capsys)["deleted"] == ["VE/Glue.lean"]


def test_the_report_fails_closed(tmp_path, capsys):
    base = fixture_repo(tmp_path)
    # An edit the declaration list was not compiled from: no report from an unvalidated classification.
    (tmp_path / "lean/VE/Glue.lean").write_text(GLUE.replace("1", "2"))
    assert trust_changes.main(["--since", base, "--root", str(tmp_path)]) == 1
    assert "FAIL: the changed files are not reported" in capsys.readouterr().err
    assert trust_changes.main(["--since", "no-such-commit", "--root", str(tmp_path)]) == 1
    assert "FAIL: git ls-tree no-such-commit" in capsys.readouterr().err
