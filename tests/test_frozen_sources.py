"""AR-2, the narrow freeze (architecture decision D2): `lean/VE/Route/frozen.py` hashes only the files with K
declarations and the `ve.core@0.1` decoders, `ve/question/LOCK.json` hashes no module, and
`tools/trust_changes.py` lists the changed D[V] and G[V] files instead. The pre-commit hook's half of the rules
is in tests/test_precommit_hook.py."""
from __future__ import annotations

from collections import defaultdict
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
LEAN = ROOT / "lean"
sys.path.insert(0, str(ROOT / "tools"))
import lake_outputs  # noqa: E402
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


# What the frozen identities are made of, read from the compiled library (the compiler is the oracle, not a reading
# of Lean source). The arguments: the module to import; the function naming each frozen envelope's identity version
# (`Legacy.version`: `ve.core@0` and the `ve.core@0.1` closure and order envelopes); the module that decodes every
# request, and the namespace of the JSON reader it decodes them with. Printed as JSON: the versions (the string
# literals of the version function); each definition that writes an identity domain `ve-environment-<v>\n` or
# `ve-meaning-<v>\n` as a literal argument, with its module and the function it is passed to; and the modules of
# VE each such function, and each reader function the request module calls, reaches through definitions.
IDENTITIES = r"""
import Lean
open Lean

def moduleOf (env : Environment) (n : Name) : Option Name :=
  (env.getModuleIdxFor? n).map fun i => env.header.moduleNames[i.toNat]!

def reach (env : Environment) (roots : Array Name) : Array String := Id.run do
  let mut seen : NameSet := {}
  let mut todo := roots
  let mut out : Array String := #[]
  while h : todo.size > 0 do
    let n := todo[todo.size - 1]
    todo := todo.pop
    if seen.contains n then continue
    seen := seen.insert n
    let some m := moduleOf env n | continue
    unless (`VE).isPrefixOf m do continue
    unless out.contains m.toString do out := out.push m.toString
    if let some (.defnInfo d) := env.find? n then todo := todo ++ d.value.getUsedConstants
  return out

def main (args : List String) : IO UInt32 := do
  let [root, version, requests, reader] := args | return 2
  initSearchPath (← findSysroot)
  let env ← importModules #[{ module := root.toName }] {}
  let some (.defnInfo v) := env.find? version.toName | throw (IO.userError s!"{version}: no such definition")
  let versions ← IO.mkRef (#[] : Array String)
  v.value.forEach fun | .lit (.strVal s) => versions.modify (·.push s) | _ => pure ()
  let domains := (← versions.get).toList.flatMap fun v => [s!"ve-environment-{v}\n", s!"ve-meaning-{v}\n"]
  let writers ← IO.mkRef (#[] : Array Json)
  let readers ← IO.mkRef (#[] : Array Name)
  for (n, info) in env.constants.map₁.toList do
    let some m := moduleOf env n | continue
    let .defnInfo d := info | continue
    if m == requests.toName then
      for c in d.value.getUsedConstants do
        if reader.toName.isPrefixOf c then readers.modify fun rs => if rs.contains c then rs else rs.push c
    unless (`VE).isPrefixOf m do continue
    d.value.forEach fun e => do
      if let .app f (.lit (.strVal s)) := e then
        if let .const c _ := f.getAppFn then
          if domains.contains s then writers.modify (·.push (toJson [m.toString, s, c.toString]))
  let digests := ((← writers.get).filterMap fun w => (w.getArrVal? 2 >>= Json.getStr?).toOption).toList.eraseDups
  IO.println (Json.mkObj [("versions", toJson (← versions.get)), ("writers", toJson (← writers.get)),
    ("reach", Json.mkObj (digests.map fun c => (c, toJson (reach env #[c.toName])))),
    ("readers", toJson ((← readers.get).map (·.toString))),
    ("reader_reach", toJson (reach env (← readers.get)))]).compress
  return 0
"""


@pytest.fixture(scope="module")
def identities(tmp_path_factory) -> dict:
    script = tmp_path_factory.mktemp("identities") / "identities.lean"
    script.write_text(IDENTITIES)
    done = subprocess.run([lake_outputs.lean_executable(None, "lake"), "env", "lean", "--run", str(script),
                           "VE.Service.Protocol", "VE.Service.Standalone.Legacy.version", "VE.Service.Protocol",
                           "VE.JsonInput"], cwd=LEAN, capture_output=True, text=True, timeout=HANG_TIMEOUT)
    assert done.returncode == 0, done.stdout + done.stderr
    return json.loads(done.stdout)


def path_of(module: str) -> str:
    return module.replace(".", "/") + ".lean"


def frozen_identity_files(facts: dict, decoders=frozen.DECODERS) -> tuple[dict[str, set[str]], list[str]]:
    """Each Lean file that defines part of a frozen identity, with what it defines, and the identity domains no file
    of `decoders` writes. `facts` is what the compiled library says (`IDENTITIES`): every frozen envelope's
    identity version has two domains; a decoder writes each one, and every module of VE the function it is passed to
    (the digest) reaches defines part of it; and every module the service's request reader reaches defines the
    values the digests hash. A file outside `decoders` that writes a domain uses the identity, it does not make
    the domain defined."""
    defines: dict[str, set[str]] = defaultdict(set)
    missing = []
    for domain in (f"ve-{kind}-{v}\n" for v in facts["versions"] for kind in ("environment", "meaning")):
        written = [(module, digest) for module, text, digest in facts["writers"]
                   if text == domain and path_of(module) in decoders]
        if not written:
            missing.append(domain)
        for module, digest in written:
            defines[path_of(module)].add(f"the domain {domain!r}")
            for reached in facts["reach"][digest]:
                defines[path_of(reached)].add(f"{digest}, which digests {domain!r}")
    for reached in facts["reader_reach"]:
        defines[path_of(reached)].add(f"the request reader ({', '.join(sorted(facts['readers']))})")
    return dict(defines), missing


def test_every_frozen_identity_has_a_decoder_and_every_decoder_defines_one(identities):
    """AR-2 review F4: `DECODERS` is complete. Each frozen envelope's identity domains are written in a decoder,
    and every module the digests and the request reader reach is one; each listed decoder defines part of them."""
    assert len(identities["versions"]) >= 3 and identities["readers"], identities
    defines, missing = frozen_identity_files(identities)
    assert missing == []
    assert set(defines) == set(frozen.DECODERS), defines
    # A frozen envelope Lean adds (a new `Legacy.version` arm) without a decoder fails, and so does a decoder no
    # longer listed, or one listed that defines no identity.
    added = {**identities, "versions": [*identities["versions"], "v0.3"]}
    assert frozen_identity_files(added)[1] == ["ve-environment-v0.3\n", "ve-meaning-v0.3\n"]
    for name in frozen.DECODERS:
        rest = [d for d in frozen.DECODERS if d != name]
        defines, missing = frozen_identity_files(identities, rest)
        assert missing or set(defines) != set(rest), name
    assert "VE/Gone.lean" not in frozen_identity_files(identities, (*frozen.DECODERS, "VE/Gone.lean"))[0]


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


def fixture_repo(root: Path, decoder: str = DECODER) -> str:
    (root / "lean/VE").mkdir(parents=True)
    (root / "tools").mkdir()
    (root / "lean/VE/Demo.lean").write_text(decoder)
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
    assert changes(tmp_path, base, capsys) == {"changed": {}, "deleted": [], "by_class": {"D[V]": [], "G[V]": []},
                                               "widened": []}
    # The body changes, the statement (`decodeThing : String → Nat`) does not.
    (tmp_path / "lean/VE/Demo.lean").write_text(DECODER.replace("s.length", "s.length + 1"))
    declarations(tmp_path, {"VE.Demo": "3:0-4:14 def VE.Demo.decodeThing", "VE.Glue": "3:0-3:20 def VE.Glue.glue"})
    out = changes(tmp_path, base, capsys)
    assert out["by_class"] == {"D[V]": ["VE/Demo.lean"], "G[V]": []}
    assert out["changed"] == {"VE/Demo.lean": {"K": 0, "S": 0, "D[V]": 3, "G[V]": 0, "trusted_width": 37,
                                               "base_width": 37}}
    assert out["widened"] == []
    (tmp_path / "lean/VE/Glue.lean").unlink()
    declarations(tmp_path, {"VE.Demo": "3:0-4:14 def VE.Demo.decodeThing"})
    table = json.loads((tmp_path / "tools/trust-classes.json").read_text())
    del table["modules"]["VE/Glue.lean"]
    (tmp_path / "tools/trust-classes.json").write_text(json.dumps(table))
    deleted_report = changes(tmp_path, base, capsys)
    assert deleted_report["deleted"] == ["VE/Glue.lean"]
    assert deleted_report["by_class"] == {"D[V]": ["VE/Demo.lean"], "G[V]": ["VE/Glue.lean"]}


def test_trusted_code_collapsed_onto_a_wider_line_is_reported(tmp_path, capsys):
    """AR-2 review F3: a trusted case added and an unrelated one collapsed onto one long line keep the line count
    (+0), so the report also names the file whose trusted lines grew wider than any line it had at the base."""
    base = fixture_repo(tmp_path)
    # Three lines become one, and a new branch of the same width class is added in their place: still 3 lines.
    wide = DECODER.replace("  s.length\n", "  if s.isEmpty then 0 else if s.length > 9 then s.length + s.length "
                                          "* 2 - 1 else s.length + 1 + (s.toList.filter Char.isDigit).length\n")
    assert wide.count("\n") == DECODER.count("\n")
    (tmp_path / "lean/VE/Demo.lean").write_text(wide)
    width = len(wide.split("\n")[3])
    declarations(tmp_path, {"VE.Demo": f"3:0-4:{width} def VE.Demo.decodeThing",
                            "VE.Glue": "3:0-3:20 def VE.Glue.glue"})
    out = changes(tmp_path, base, capsys)
    assert out["changed"]["VE/Demo.lean"] == {"K": 0, "S": 0, "D[V]": 3, "G[V]": 0, "trusted_width": width,
                                              "base_width": 37}
    assert out["widened"] == ["VE/Demo.lean"]
    assert trust_changes.main(["--since", base, "--root", str(tmp_path)]) == 0
    assert (f"widened: 1 changed files hold a trusted line wider than any trusted line they had at base\n"
            f"  VE/Demo.lean: trusted line of {width} characters, base at most 37\n") in capsys.readouterr().out
    # The same width in an untrusted (tied or test) declaration, or a new file, is not listed.
    table = json.loads((tmp_path / "tools/trust-classes.json").read_text())
    table["modules"]["VE/Demo.lean"] = {"T": ["VE.Demo.decodeThing"]}
    (tmp_path / "tools/trust-classes.json").write_text(json.dumps(table))
    assert changes(tmp_path, base, capsys)["widened"] == []


def test_a_long_comment_at_base_hides_no_collapsed_trusted_code(tmp_path, capsys):
    """AR-2 review F8: the base's width is its widest trusted line, not its widest line. A file whose base already
    holds a comment wider than the collapsed trusted line is still listed as widened."""
    comment = "-- " + "A comment wider than any trusted line of the file, and wider than the collapsed line. " * 3
    commented = DECODER.replace("namespace VE.Demo\n\n", f"namespace VE.Demo\n{comment}\n")
    base = fixture_repo(tmp_path, commented)
    collapsed = commented.replace("  s.length\n", "  if s.isEmpty then 0 else s.length + (s.toList.filter "
                                                  "Char.isDigit).length * 2\n")
    (tmp_path / "lean/VE/Demo.lean").write_text(collapsed)
    width = len(collapsed.split("\n")[3])
    assert 37 < width < len(comment)
    declarations(tmp_path, {"VE.Demo": f"3:0-4:{width} def VE.Demo.decodeThing",
                            "VE.Glue": "3:0-3:20 def VE.Glue.glue"})
    out = changes(tmp_path, base, capsys)
    assert out["changed"]["VE/Demo.lean"] == {"K": 0, "S": 0, "D[V]": 3, "G[V]": 0, "trusted_width": width,
                                              "base_width": 37}
    assert out["widened"] == ["VE/Demo.lean"]
    assert trust_changes.main(["--since", base, "--root", str(tmp_path)]) == 0
    assert f"  VE/Demo.lean: trusted line of {width} characters, base at most 37\n" in capsys.readouterr().out
    # The base is classified by the base's own table: trusted code that was a test (T) at the base has no width.
    table = (tmp_path / "tools/trust-classes.json").read_text()
    (tmp_path / "tools/trust-classes.json").write_text(table.replace('"D[V]"', '"T"'))
    (tmp_path / "lean/VE/Demo.lean").write_text(commented)
    declarations(tmp_path, {"VE.Demo": "3:0-4:10 def VE.Demo.decodeThing", "VE.Glue": "3:0-3:20 def VE.Glue.glue"})
    git(tmp_path, "commit", "-q", "-am", "the decoder is a test at the base")
    tested = git(tmp_path, "rev-parse", "HEAD")
    (tmp_path / "tools/trust-classes.json").write_text(table)
    (tmp_path / "lean/VE/Demo.lean").write_text(collapsed)
    declarations(tmp_path, {"VE.Demo": f"3:0-4:{width} def VE.Demo.decodeThing",
                            "VE.Glue": "3:0-3:20 def VE.Glue.glue"})
    out = changes(tmp_path, tested, capsys)
    assert (out["changed"]["VE/Demo.lean"]["base_width"], out["widened"]) == (0, ["VE/Demo.lean"])


def test_a_base_whose_classification_fails_gives_no_report(tmp_path, capsys):
    """The base's widths come from the base's validated classification, never from an unvalidated one."""
    base = fixture_repo(tmp_path)
    (tmp_path / "lean/declarations.txt").write_text("-- header\n")
    git(tmp_path, "commit", "-q", "-am", "a stale declaration list")
    stale = git(tmp_path, "rev-parse", "HEAD")
    (tmp_path / "lean/VE/Demo.lean").write_text(DECODER.replace("s.length", "s.length + 1"))
    declarations(tmp_path, {"VE.Demo": "3:0-4:14 def VE.Demo.decodeThing", "VE.Glue": "3:0-3:20 def VE.Glue.glue"})
    assert trust_changes.main(["--since", stale, "--root", str(tmp_path)]) == 1
    assert f"FAIL: the trust classification of {stale} fails:\n" in capsys.readouterr().err
    assert changes(tmp_path, base, capsys)["widened"] == []


def test_the_report_fails_closed(tmp_path, capsys):
    base = fixture_repo(tmp_path)
    # An edit the declaration list was not compiled from: no report from an unvalidated classification.
    (tmp_path / "lean/VE/Glue.lean").write_text(GLUE.replace("1", "2"))
    assert trust_changes.main(["--since", base, "--root", str(tmp_path)]) == 1
    assert "FAIL: the changed files are not reported" in capsys.readouterr().err
    assert trust_changes.main(["--since", "no-such-commit", "--root", str(tmp_path)]) == 1
    assert "FAIL: git ls-tree no-such-commit" in capsys.readouterr().err
