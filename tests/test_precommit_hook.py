"""tools/hooks/pre-commit: each check rejects a planted example and passes clean commits.

Every test stages content into a private index (GIT_INDEX_FILE) and object
directory (GIT_OBJECT_DIRECTORY, with the repository's objects as alternates),
so neither the worktree, its real index nor the shared object store changes.
Secret examples are assembled at run time so this file never contains one.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import time

import pytest

ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "tools/hooks/pre-commit"
INVENTORY = "lean/VE/Route/frozen-sources.sha256"


class Staging:
    def __init__(self, tmp: Path) -> None:
        objects = subprocess.run(["git", "rev-parse", "--path-format=absolute", "--git-path", "objects"],
                                 cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
        (tmp / "objects").mkdir()
        self.env = {**os.environ, "GIT_INDEX_FILE": str(tmp / "index"),
                    "GIT_OBJECT_DIRECTORY": str(tmp / "objects"),
                    "GIT_ALTERNATE_OBJECT_DIRECTORIES": objects}
        self.env.pop("VE_SKIP_HOOKS", None)
        self.tmp = tmp
        self.git("read-tree", "HEAD")

    def git(self, *args: str, data: bytes | None = None) -> bytes:
        return subprocess.run(["git", *args], cwd=ROOT, env=self.env, input=data,
                              capture_output=True, check=True).stdout

    def head(self, path: str) -> bytes:
        return self.git("cat-file", "blob", f"HEAD:{path}")

    def stage(self, path: str, content: bytes | str | None) -> None:
        if content is None:
            self.git("update-index", "--force-remove", "--", path)
            return
        data = content.encode() if isinstance(content, str) else content
        blob = self.git("hash-object", "-w", "--stdin", data=data).decode().strip()
        self.git("update-index", "--add", "--cacheinfo", f"100644,{blob},{path}")

    def stage_many(self, files: dict[str, bytes]) -> None:
        """Stage many files with two git processes."""
        folder = self.tmp / "many"
        paths = []
        for number, data in enumerate(files.values()):
            paths.append(folder / str(number))
            paths[-1].parent.mkdir(exist_ok=True)
            paths[-1].write_bytes(data)
        blobs = self.git("hash-object", "-w", "--stdin-paths",
                         data="".join(f"{p}\n" for p in paths).encode()).decode().split()
        self.git("update-index", "--add", "--index-info",
                 data="".join(f"100644 {blob}\t{path}\n" for blob, path in zip(blobs, files)).encode())

    def rehash(self, *paths: str) -> None:
        """Update the frozen inventory in the index, as the repository's rules require."""
        lines = self.git("cat-file", "blob", f":{INVENTORY}").decode().splitlines()
        recorded = dict(reversed(line.split(maxsplit=1)) for line in lines)
        for path in paths:
            recorded[path.removeprefix("lean/")] = hashlib.sha256(
                self.git("cat-file", "blob", f":{path}")).hexdigest()
        self.stage(INVENTORY, "".join(f"{digest}  {name}\n" for name, digest in sorted(recorded.items())))

    def run(self, *args: str, **env: str) -> subprocess.CompletedProcess:
        return subprocess.run([str(HOOK), *args], cwd=ROOT, env={**self.env, **env},
                              capture_output=True, text=True, check=False)

    def run_in(self, worktree: Path, *args: str) -> subprocess.CompletedProcess:
        """Run a copy of the hook from another working tree over the same repository and index."""
        hooks = worktree / "tools/hooks"
        hooks.mkdir(parents=True, exist_ok=True)
        for name in ("pre-commit", "precommit.py"):
            shutil.copy2(HOOK.parent / name, hooks / name)
        git_dir = self.git("rev-parse", "--absolute-git-dir").decode().strip()
        return subprocess.run([str(hooks / "pre-commit"), *args], cwd=worktree,
                              env={**self.env, "GIT_DIR": git_dir, "GIT_WORK_TREE": str(worktree)},
                              capture_output=True, text=True, check=False)


@pytest.fixture
def staging(tmp_path: Path) -> Staging:
    return Staging(tmp_path)


def rejects(staging: Staging, *messages: str) -> str:
    result = staging.run()
    assert result.returncode == 1, result.stderr
    for message in messages:
        assert message in result.stderr, result.stderr
    return result.stderr


def passes(staging: Staging) -> None:
    result = staging.run()
    assert result.returncode == 0, result.stderr


def test_clean_commit_passes(staging):
    staging.stage("ve/errors.py", staging.head("ve/errors.py") + b"\n# A harmless comment.\n")
    staging.stage("docs/precommit-probe.md", "# Probe\n\nA token of thanks; the password is in the vault.\n")
    staging.stage("ve/ast.py", staging.head("ve/ast.py") + b"\nimport ve.surface.registry\n")  # ledgered edge
    staging.stage("lean/VE/Syntax.lean", staging.head("lean/VE/Syntax.lean") + b"\n-- A comment.\n")
    staging.rehash("lean/VE/Syntax.lean")
    staging.stage("tools/hooks/unused.txt", None)  # removing an absent path is a no-op
    passes(staging)


def test_nothing_staged_passes(staging):
    passes(staging)


def test_wire_contract_checks_staged_generated_table(staging):
    path = "docs/spec/soft-norms-wire-table.md"
    staging.stage(path, staging.head(path) + b"\nChanged after generation.\n")
    rejects(staging, "wire contract check failed", "WC11")


def test_wire_contract_accepts_staged_equivalent_json(staging):
    path = "ve/wire_contract/limits.json"
    staging.stage(path, staging.head(path) + b"\n")
    passes(staging)


SECRETS = {
    "AWS access key id": lambda: "AKIA" + "Q7" * 8,
    "GitHub token": lambda: "ghp_" + "a1B2" * 9,
    "Anthropic API key": lambda: "sk-" + "ant-api03-" + "x9" * 20,
    "OpenAI API key": lambda: "sk-" + "proj-" + "Zq8" * 12,
    "Slack token": lambda: "xox" + "b-1234567890-abcdefghij",
    "private key block": lambda: "-----BEGIN " + "OPENSSH PRIVATE KEY-----",
    "credential assignment": lambda: 'api_key = "' + "k3yV4lue" * 4 + '"',
}


@pytest.mark.parametrize("kind", SECRETS)
def test_secret_in_added_line_is_rejected_without_echoing_it(staging, kind):
    secret = SECRETS[kind]()
    staging.stage("ve_experiments/planted.py", f'"""Doc."""\n\nVALUE = {secret!r}\n')
    stderr = rejects(staging, "secrets check failed", f"ve_experiments/planted.py:3: possible {kind}")
    assert secret not in stderr and secret[4:] not in stderr


def test_secret_allowlist_pragma_and_webapp_private_path(staging):
    secret = SECRETS["AWS access key id"]()
    staging.stage("docs/probe.md", f"Example: {secret}  <!-- pragma: allowlist secret -->\n")
    passes(staging)
    staging.stage("ve_experiments/.webapp-private/session.json", "{}\n")
    rejects(staging, "ve_experiments/.webapp-private/session.json: files under .webapp-private/")
    staging.stage("ve_experiments/.webapp-private/session.json", None)
    staging.stage("deploy/.env", "MODE=dev\n")
    rejects(staging, "deploy/.env: private key or environment file")


@pytest.mark.parametrize("setting", ["staged -diff", "configured binary", "NUL bytes"])
def test_secret_scan_reads_raw_staged_blobs(staging, tmp_path, setting):
    # Attributes, diff drivers and binary detection change what `git diff` shows,
    # not what the commit stores; the scan must see the stored bytes.
    secret = SECRETS["GitHub token"]()
    env = {}
    content = f"TOKEN = {secret!r}\n".encode()
    if setting == "staged -diff":
        staging.stage(".gitattributes", "*.py -diff\n")
    elif setting == "configured binary":
        (tmp_path / "attributes").write_text("* binary\n")
        env = {"GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "core.attributesFile",
               "GIT_CONFIG_VALUE_0": str(tmp_path / "attributes")}
    else:
        content = b"\0\x01binary header\0\n" + content
    staging.stage("ve_experiments/planted.py", content)
    result = staging.run(**env)
    assert result.returncode == 1, result.stderr
    line = 2 if setting == "NUL bytes" else 1
    assert f"ve_experiments/planted.py:{line}: possible GitHub token" in result.stderr, result.stderr


def test_secret_added_to_an_existing_file_is_located(staging):
    head = staging.head("ve/errors.py")
    secret = SECRETS["AWS access key id"]()
    staging.stage("ve/errors.py", head + f"# {secret}\n".encode())
    number = head.count(b"\n") + 1
    rejects(staging, f"ve/errors.py:{number}: possible AWS access key id")
    staging.stage("ve/errors.py", head + f"# {secret}  # pragma: allowlist secret\n".encode())
    passes(staging)


def test_verdicts_do_not_depend_on_the_working_tree(staging, tmp_path):
    # A working tree with none of the repository's files and an attributes file
    # that hides every diff must give exactly the verdicts of the real one.
    elsewhere = tmp_path / "worktree"
    elsewhere.mkdir()
    (elsewhere / ".gitattributes").write_text("* -diff\n")
    staging.stage("ve/ast.py", staging.head("ve/ast.py") + b"\nimport ve.surface.registry\n")
    staging.stage("lean/VE/Syntax.lean", staging.head("lean/VE/Syntax.lean") + b"\n-- A comment.\n")
    staging.rehash("lean/VE/Syntax.lean")
    clean = staging.run_in(elsewhere)
    assert clean.returncode == 0, clean.stderr
    staging.stage("docs/probe.md", SECRETS["GitHub token"]() + "\n")
    staging.stage("ve/ast.py", staging.head("ve/ast.py") + b"\nfrom ve import surface\n")
    staging.stage("lean/VE/Core/Planted.lean", "-- c\nimport VE.Surface\n")
    staging.rehash("lean/VE/Core/Planted.lean")
    here, there = staging.run(), staging.run_in(elsewhere)
    assert here.returncode == there.returncode == 1
    assert here.stderr == there.stderr
    for message in ("docs/probe.md:1: possible GitHub token",
                    "ve/ast.py: new outward import ve.ast -> ve.surface (layer 1 -> 3)",
                    "new outward Lean import VE.Core.Planted -> VE.Surface (layer 1 -> 3)"):
        assert message in here.stderr, here.stderr


def test_python_imports_resolve_against_the_staged_tree(staging):
    # Without its __init__.py, ve/surface is still importable as a namespace package.
    staging.stage("ve/surface/__init__.py", None)
    staging.stage("ve/ast.py", staging.head("ve/ast.py") + b"\nfrom ve import surface\n")
    rejects(staging, "ve/ast.py: new outward import ve.ast -> ve.surface (layer 1 -> 3)")


def test_staged_policy_code_is_the_policy(staging):
    policy = staging.head("tools/layer_policy.py")
    assert b'"ast environment errors' in policy
    staging.stage("tools/layer_policy.py", policy.replace(b'"ast environment errors',
                                                          b'"ast planted_module environment errors'))
    staging.stage("ve/planted_module.py", "import ve.errors\n")
    passes(staging)  # mapped by the staged policy, which the working tree lacks
    staging.stage("ve/planted_module.py", "from ve import parser\n")
    stderr = rejects(staging, "new outward import ve.planted_module -> ve.parser (layer 1 -> 3)")
    assert "unmapped" not in stderr
    audit = staging.head("lean/audit.py")
    assert b"|native_decide|" in audit
    staging.stage("lean/audit.py", audit.replace(b"|native_decide|", b"|native_decide|plantedword|"))
    staging.stage("lean/VE/Core/Planted.lean", "-- plantedword\n")
    staging.rehash("lean/VE/Core/Planted.lean")
    rejects(staging, "lean/VE/Core/Planted.lean:1: forbidden Lean token 'plantedword'")
    staging.stage("tools/layer_policy.py", None)
    rejects(staging, "internal error: RuntimeError: policy file tools/layer_policy.py is missing from the index")


def test_staged_lean_entry_modules_are_tool_layer(staging):
    # layers-entry-directive: a new route entry module needs no hand-listed layer.
    staging.stage("lean/RiskMain.lean", "import VE.Route.Run\n")
    passes(staging)
    staging.stage("lean/Launch.lean", "import VE.Route.Run\n")
    rejects(staging, "unmapped Lean module Launch")
    lakefile = staging.head("lean/lakefile.toml")
    staging.stage("lean/lakefile.toml", lakefile + b'\n[[lean_exe]]\nname = "ve_launch"\nroot = "Launch"\n')
    passes(staging)
    staging.stage("lean/lakefile.toml", None)
    rejects(staging, "internal error: RuntimeError: policy file lean/lakefile.toml is missing from the index")


def test_new_outward_python_import_is_rejected(staging):
    staging.stage("ve/ast.py", staging.head("ve/ast.py") + b"\nfrom ve import parser\n")
    rejects(staging, "layer imports check failed",
            "ve/ast.py: new outward import ve.ast -> ve.parser (layer 1 -> 3)")
    staging.stage("ve/ast.py", staging.head("ve/ast.py"))
    staging.stage("ve/planted_module.py", "import ve.ast\n")
    rejects(staging, "unmapped Python module ve.planted_module")


def test_new_outward_lean_import_is_rejected(staging):
    path = "lean/VE/Core/Planted.lean"
    staging.stage(path, "import VE.Core.Bridge\nimport VE.Surface\n\nnamespace VE\nend VE\n")
    staging.rehash(path)
    rejects(staging, f"{path}: new outward Lean import VE.Core.Planted -> VE.Surface (layer 1 -> 3)")
    staging.stage(path, "import VE.Core.Missing\n")
    staging.rehash(path)
    rejects(staging, f"{path}: missing local Lean import VE.Core.Missing")
    staging.stage(path, "import VE.Core.Bridge\n-- import VE.Surface\n")
    staging.rehash(path)
    passes(staging)


@pytest.mark.parametrize("header, line, reason", [
    # precommit-loop.final.md B: Lean reads VE.Surface after the comment `/-/-/`.
    ("/-/-/import VE.Surface\n", 1, "`/-` inside a block comment"),
    ("import VE.Core.Bridge /-/-/import VE.Surface\n", 1, "not a plain `import A.B.C` line"),
    ("-- c\n/-/-/\nimport VE.Surface\n", 2, "`/-` inside a block comment"),
    ("/- a -/ import VE.Surface\n", 1, "text after the closing `-/` of a block comment"),
    ("/- outer /- inner -/ -/\nimport VE.Surface\n", 1, "`/-` inside a block comment"),
    ("import VE.Core.Bridge\nimport\n  VE.Surface\n\nnamespace VE\nend VE\n", 2, "not a plain `import A.B.C` line"),
    ("prelude import VE.Core.Bridge import VE.Surface\n", 1, "not a plain `import A.B.C` line"),
    ("module\n\npublic import VE.Surface\n", 1, "not a plain `import A.B.C` line"),
    ("import«VE».Surface\n", 1, "not a plain `import A.B.C` line"),
    ("import /- c -/ VE.Surface\n", 1, "not a plain `import A.B.C` line"),
    ("import VE.Core.Bridge import «VE».Surface\n", 1, "not a plain `import A.B.C` line"),
    ("import VE.Core.Bridge/- c -/import VE.Surface\n", 1, "not a plain `import A.B.C` line"),
    ("\timport VE.Surface\n", 1, "character '\\t' at the start of a header line"),
], ids=["stacked", "stacked-after-import", "stacked-own-line", "after-comment", "nested", "next-line",
        "prelude-one-line", "public", "quoted-no-space", "comment-inside", "successive-quoted",
        "successive-after-comment", "tab"])
def test_lean_header_outside_the_plain_layout_is_rejected(staging, header, line, reason):
    path = "lean/VE/Core/Planted.lean"
    staging.stage(path, header)
    staging.rehash(path)
    rejects(staging, f"{path}: Lean header line {line}: {reason}; write the header in the plain layout")


def test_plain_lean_header_is_confirmed_by_the_pinned_lean(staging):
    path = "lean/VE/Core/Planted.lean"
    staging.stage(path, "/- A planted module. -/\n-- imports:\nimport VE.Core.Bridge\n\nimport VE.Surface\n")
    staging.rehash(path)
    result = staging.run("--timings")
    assert result.returncode == 1
    assert f"{path}: new outward Lean import VE.Core.Planted -> VE.Surface (layer 1 -> 3)" in result.stderr
    assert f"{path}: Lean header" not in result.stderr
    assert "lean --deps confirmed or refuted 1 of 1 staged Lean headers" in result.stderr, result.stderr


def test_lean_deps_disagreement_is_rejected(staging):
    # A staged reader that misreads a plain import: the pinned Lean refutes it.
    reader = staging.head("tools/check_lean_imports.py")
    assert b"found.append(match[1])" in reader
    staging.stage("tools/check_lean_imports.py",
                  reader.replace(b"found.append(match[1])", b'found.append(match[1].replace("Surface", "Syntax"))'))
    path = "lean/VE/Core/Planted.lean"
    staging.stage(path, "import VE.Surface\n")
    staging.rehash(path)
    stderr = rejects(staging, f"{path}: Lean header: the pinned Lean reads imports ['VE.Surface'], "
                              f"not ['VE.Syntax']; write the header in the plain layout")
    assert "VE.Core.Planted -> VE.Syntax" not in stderr


def test_lean_headers_without_the_pinned_toolchain(staging, tmp_path):
    # Without elan or lean on PATH the plain-layout grammar alone decides.
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    for tool in ("python3", "git", "dirname"):
        (bin_dir / tool).symlink_to(shutil.which(tool))
    path = "lean/VE/Core/Planted.lean"
    staging.stage(path, "import VE.Core.Bridge\n")
    staging.rehash(path)
    result = staging.run("--timings", PATH=str(bin_dir))
    assert result.returncode == 0, result.stderr
    assert "lean --deps: pinned toolchain unavailable; plain-layout grammar only" in result.stderr
    staging.stage(path, "/-/-/import VE.Surface\n")
    staging.rehash(path)
    result = staging.run(PATH=str(bin_dir))
    assert result.returncode == 1
    assert f"{path}: Lean header line 1: `/-` inside a block comment" in result.stderr, result.stderr


@pytest.mark.parametrize("source", [
    "import VE.Core.Bridge\n\ndef «an import VE.Surface» := 1\n",
    "def «an import VE.Surface» := 1\n",
    "import VE.Core.Bridge\n\nnamespace «import VE.Surface»\nend «import VE.Surface»\n",
    "import VE.Core.Bridge\n\n/-- `import VE.Surface` -/\ndef x := 1\n",
], ids=["quoted-name", "quoted-name-no-header", "quoted-namespace", "doc-comment"])
def test_import_text_after_the_header_is_not_an_import(staging, source):
    path = "lean/VE/Core/Planted.lean"
    staging.stage(path, source)
    staging.rehash(path)
    passes(staging)


def test_outward_rust_dependency_is_rejected(staging):
    manifest = staging.head("rust/ve-core/Cargo.toml") + b've = { path = "../ve" }\n'
    staging.stage("rust/ve-core/Cargo.toml", manifest)
    rejects(staging, "rust: outward crate dependency: ve-core -> ve")


@pytest.mark.parametrize("line, token", [
    ("theorem planted : 1 = 1 := by sorry", "sorry"),
    ("theorem planted : 1 = 1 := by admit", "admit"),
    ("axiom planted : False", "axiom"),
    ("-- a comment still may not say sorry", "sorry"),  # lean/audit.py scans comments too
], ids=["sorry", "admit", "axiom", "comment"])
def test_lean_forbidden_tokens_are_rejected(staging, line, token):
    path = "lean/VE/Core/Planted.lean"
    staging.stage(path, f"namespace VE\n\n{line}\n\nend VE\n")
    staging.rehash(path)
    rejects(staging, "Lean forbidden tokens check failed", f"{path}:3: forbidden Lean token '{token}'")


def test_lean_tokens_outside_lean_ignore_comments_only(staging):
    path = "experiments/obfuscated-arguments/Feasibility.lean"
    original = staging.head(path)
    staging.stage(path, original + b"\n-- no sorry here, only prose\n")
    passes(staging)
    staging.stage(path, original + b"\naxiom planted : False\n")
    rejects(staging, f"{path}:", "forbidden Lean token 'axiom'")


def test_frozen_file_change_requires_an_inventory_update(staging):
    path = "lean/VE/Syntax.lean"
    staging.stage(path, staging.head(path) + b"\n-- Unreviewed edit.\n")
    rejects(staging, "frozen files check failed",
            f"{path}: frozen file changed without an inventory update")
    staging.rehash(path)
    passes(staging)
    staging.stage(path, None)
    rejects(staging, f"{path}: frozen file deleted but still listed")


def test_frozen_guard_rejects_unlisted_modules_bad_inventory_and_main(staging):
    staging.stage("lean/VE/Core/Planted.lean", "namespace VE\nend VE\n")
    rejects(staging, "lean/VE/Core/Planted.lean: unlisted trusted module")
    staging.stage("lean/VE/Core/Planted.lean", None)
    first, rest = staging.head(INVENTORY).split(b"\n", 1)
    staging.stage(INVENTORY, b"0" * 64 + first[64:] + b"\n" + rest)  # a wrong rehash
    rejects(staging, f"lean/{first[66:].decode()}: frozen file changed without an inventory update")
    staging.stage(INVENTORY, staging.head(INVENTORY))
    staging.stage("lean/Main.lean", staging.head("lean/Main.lean") + b"\n-- edit\n")
    rejects(staging, "lean/Main.lean: existing subcommands changed")


def test_emergency_bypass_warns(staging):
    staging.stage("docs/probe.md", SECRETS["GitHub token"]() + "\n")
    result = staging.run(VE_SKIP_HOOKS="1")
    assert result.returncode == 0
    assert "warning: VE_SKIP_HOOKS=1: pre-commit checks SKIPPED" in result.stderr
    assert "the gate does NOT re-check secrets or layer imports" in result.stderr


def test_large_staged_change_stays_under_ten_seconds(staging):
    files = {}
    tracked = staging.git("ls-files", "-z", "--", "ve", "lean/VE").decode().split("\0")
    python = [p for p in tracked if p.endswith(".py")]
    lean = [p for p in tracked if p.endswith(".lean")]
    for path in python:
        files[path] = staging.head(path) + b"\n# Timing probe.\n"
    for path in lean:
        files[path] = staging.head(path) + b"\n-- Timing probe.\n"
    line = b"The applicant qualifies when every listed condition holds on the reference date.\n"
    for number in range(1500):
        files[f"experiments/timing-probe/case_{number:04}.md"] = line * 120
    staging.stage_many(files)
    staging.rehash(*lean)
    started = time.perf_counter()
    result = staging.run("--timings")
    elapsed = time.perf_counter() - started
    assert result.returncode == 0, result.stderr
    assert elapsed < 10, result.stderr
    print(f"\n{len(files) + 1} staged paths, {sum(map(len, files.values())) / 1e6:.1f} MB: "
          f"{elapsed:.2f} s\n{result.stderr}")
