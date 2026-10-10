"""Boundary checks for the selector's non-import dependencies and fallback."""
from __future__ import annotations

import unittest
from unittest.mock import patch
from contextlib import redirect_stderr, redirect_stdout
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
from tempfile import TemporaryDirectory
import sys
from types import ModuleType

import check_lean_imports
try:
    import grimp
except ModuleNotFoundError:
    grimp = ModuleType("grimp")
    grimp.build_graph = None
    sys.modules["grimp"] = grimp
import check_python_layers
import check_rust_deps
import layer_policy
import rust_output_diff
import select_tests
import source_graph


_CACHE = None
_SAVED_CACHE_HOME = None


def setUpModule():
    # The selector caches parsed sources; keep those writes in a private directory.
    global _CACHE, _SAVED_CACHE_HOME
    _CACHE = TemporaryDirectory()
    _SAVED_CACHE_HOME = os.environ.get("XDG_CACHE_HOME")
    os.environ["XDG_CACHE_HOME"] = _CACHE.name


def tearDownModule():
    if _SAVED_CACHE_HOME is None:
        os.environ.pop("XDG_CACHE_HOME", None)
    else:
        os.environ["XDG_CACHE_HOME"] = _SAVED_CACHE_HOME
    _CACHE.cleanup()


def select(paths, **kwargs):
    """The selector on the static graph alone, so these checks do not depend on a cached map."""
    return select_tests.select(paths, coverage=None, **kwargs)

# The inward crate graph of rust/Cargo.toml: each crate and the workspace crates it uses.
RUST_CRATES = {"ve-kernel": [], "ve-profile": ["ve-kernel"], "ve-core": ["ve-kernel", "ve-profile"],
               "ve": ["ve-core"]}


def rust_workspace(root: Path, crates: dict[str, list[str]] = RUST_CRATES) -> Path:
    """A workspace of empty crates (`ve` a binary) with path dependencies and the pinned toolchain."""
    root.mkdir(parents=True, exist_ok=True)
    shutil.copy(layer_policy.ROOT / "rust-toolchain.toml", root / "rust-toolchain.toml")
    (root / "Cargo.toml").write_text(f'[workspace]\nresolver = "3"\nmembers = {json.dumps(list(crates))}\n')
    for crate, uses in crates.items():
        (root / crate / "src").mkdir(parents=True)
        (root / crate / "src" / ("main.rs" if crate == "ve" else "lib.rs")).write_text("")
        (root / crate / "Cargo.toml").write_text(
            f'[package]\nname = "{crate}"\nversion = "0.0.0"\nedition = "2024"\n[dependencies]\n'
            + "".join(f'{use} = {{ path = "../{use}" }}\n' for use in uses))
    return root


def rust_check(root: Path) -> tuple[int, str]:
    """check_rust_deps.main on the workspace at `root`: its exit code and standard error."""
    error = io.StringIO()
    with patch.object(check_rust_deps, "WORKSPACE", root), redirect_stdout(io.StringIO()), redirect_stderr(error):
        code = check_rust_deps.main()
    return code, error.getvalue()


class LayerSelectionTests(unittest.TestCase):
    def test_app_change_keeps_smoke_tests_and_app_consumer(self):
        plan = select(["ve_experiments/t1c/materials.py"])
        self.assertLess(plan["selected_count"], plan["full_count"])
        self.assertIn("tests/test_t1c.py", plan["selected"])
        self.assertTrue(set(plan["smoke"]) <= set(plan["selected"]))
        usecase = select(["usecases/asimov-laws/rules.ve"])
        self.assertIn("tests/test_asimov_laws.py", usecase["selected"])

    def test_native_inputs_schedule_their_builds(self):
        lean = select(["lean/VE/Norms/Wire.lean"])
        rust = select(["rust/ve/src/main.rs"])
        self.assertIn(["lake", "build"], lean["commands"])
        self.assertTrue(any(command[:3] == [*select_tests.CARGO, "test"] for command in rust["commands"]))
        self.assertIn([*select_tests.CARGO, "build", "--locked", "--release", "--manifest-path",
                       "rust/Cargo.toml", "-p", "ve"], rust["commands"])
        self.assertIn([*select_tests.CARGO, "build", "--locked", "--manifest-path",
                       "rust/Cargo.toml", "-p", "ve"], rust["commands"])
        self.assertLess(rust["commands"].index([*select_tests.CARGO, "build", "--locked",
                                                  "--manifest-path", "rust/Cargo.toml",
                                                  "-p", "ve"]), len(rust["commands"]) - 1)
        self.assertIn("tests/test_rust_conformance.py", rust["selected"])
        self.assertIn("tests/test_nary_differential.py", rust["selected"])

    def test_missing_debug_cli_is_built_for_selected_differential_test(self):
        real_exists = Path.exists
        debug = select_tests.ROOT / "rust/target/debug/ve"
        with patch.object(Path, "exists", lambda path: False if path == debug
                          else real_exists(path)):
            plan = select(["ve/search.py"])
        self.assertIn("tests/test_nary_differential.py", plan["selected"])
        self.assertIn([*select_tests.CARGO, "build", "--locked", "--manifest-path",
                       "rust/Cargo.toml", "-p", "ve"], plan["commands"])

    def test_unknown_input_falls_back_to_full_native_and_python_suite(self):
        plan = select(["new-unmapped-format.xyz"])
        self.assertEqual(plan["selected_count"], plan["full_count"])
        self.assertTrue(plan["lean_build"] and plan["rust_build"])
        self.assertTrue(select(["tests/conftest.py"])["full"])

    def test_reviewed_outward_imports_select_inner_consumers(self):
        self.assertIn("tests/test_norms.py", select(["ve/search.py"])["selected"])
        self.assertIn("tests/test_norms.py", select(["ve/surface/registry.py"])["selected"])
        self.assertIn("tests/test_assist.py", select(["ve_experiments/assist_haiku.py"])["selected"])

    def test_transitive_source_imports_select_surface_consumers(self):
        for source in ("ve/admission.py", "ve/vacuity.py"):
            with self.subTest(source=source):
                self.assertIn("tests/test_english.py", select([source])["selected"])

    def test_imported_fixtures_and_helpers_select_consumers(self):
        cases = (
            ("lean/Main.lean", "tests/test_lean_certificates.py"),
            ("lean/Main.lean", "tests/test_order_gate.py"),
            ("lean/VE/Route/Run.lean", "tests/test_order_round2.py"),
            ("rust/ve/src/main.rs", "tests/test_order_round2.py"),
            ("tests/test_data_flags.py", "tests/test_data_surface.py"),
            ("ve/__main__.py", "tests/test_english.py"),
            ("docs/english-surface.md", "tests/test_english.py"),
            ("docs/fluent-examples.md", "tests/test_views_polish.py"),
        )
        for source, consumer in cases:
            with self.subTest(source=source, consumer=consumer):
                self.assertIn(consumer, select([source])["selected"])

    def test_renames_include_deleted_paths_in_all_git_diff_modes(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)

            def git(*args):
                return subprocess.run(["git", "-C", str(root), *args], check=True,
                                      capture_output=True, text=True).stdout.strip()

            git("init", "-q")
            (root / "docs").mkdir()
            (root / "docs/fluent-examples.md").write_text("original\n")
            git("add", ".")
            git("-c", "user.name=Test", "-c", "user.email=test@example.invalid",
                "commit", "-qm", "initial")
            base = git("rev-parse", "HEAD")
            git("mv", "docs/fluent-examples.md", "docs/fluent.md")
            expected = {"docs/fluent-examples.md", "docs/fluent.md"}
            with patch.object(select_tests, "ROOT", root):
                self.assertEqual(set(select_tests.changed_paths(None, None)), expected)
            git("-c", "user.name=Test", "-c", "user.email=test@example.invalid",
                "commit", "-qm", "rename")
            with patch.object(select_tests, "ROOT", root):
                self.assertEqual(set(select_tests.changed_paths(base, None)), expected)
                self.assertEqual(set(select_tests.changed_paths(None, "HEAD")), expected)
            self.assertIn("tests/test_views_polish.py", select(sorted(expected))["selected"])

    def test_both_lean_executables_are_tool_consumers(self):
        self.assertIn("tests/test_norms_three_way.py",
                      select(["lean/VE/Norms/Run.lean"])["selected"])
        real_exists = Path.exists
        with patch.object(Path, "exists", lambda path: False if path.name == "ve_service"
                          else real_exists(path)):
            self.assertTrue(select(["ve/search.py"])["lean_build"])

    def test_service_executables_are_tool_consumers(self):
        self.assertIn("tests/test_lean_service.py",
                      select(["lean/VE/Service/Protocol.lean"])["selected"])
        real_exists = Path.exists
        for binary in ("ve_service", "ve_english_run", "ve_response_decode"):
            with self.subTest(binary=binary), patch.object(
                Path, "exists", lambda path: False if path.name == binary else real_exists(path)
            ):
                self.assertTrue(select(["ve/backends/lean_service.py"])["lean_build"])

    def test_python_app_package_outward_import_is_detected(self):
        class Graph:
            modules = {"ve.errors", "ve_experiments", "ve_experiments.runner"}

            def find_modules_directly_imported_by(self, importer):
                return {"ve_experiments", "ve_experiments.runner"} if importer == "ve.errors" else set()

        with patch.object(check_python_layers.grimp, "build_graph", return_value=Graph()):
            self.assertIn("ve.errors -> ve_experiments.runner",
                          check_python_layers.violations())
            self.assertIn("ve.errors -> ve_experiments", check_python_layers.violations())

    def test_facade_imports_resolve_to_export_owner(self):
        class Graph:
            modules = {"ve", "ve.errors", "ve.argument"}

            def find_modules_directly_imported_by(self, importer):
                return {"ve"} if importer == "ve.errors" else set()

        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "ve").mkdir()
            (root / "ve/__init__.py").write_text("from .argument import check_argument\n")
            (root / "ve/argument.py").write_text("")
            for source in ("from . import check_argument\n",
                           "from ve import check_argument as check\n",
                           "import ve as facade\nfacade.check_argument\n"):
                (root / "ve/errors.py").write_text(source)
                with (patch.object(check_python_layers, "ROOT", root),
                      patch.object(check_python_layers.grimp, "build_graph", return_value=Graph())):
                    self.assertIn("ve.errors -> ve.argument", check_python_layers.violations())

    def test_plain_lean_headers_with_comments(self):
        source = "/- a comment -/\n-- import VE.Fake\n\nimport VE.Route.Run\n"
        self.assertEqual(check_lean_imports.imports(source), ["VE.Route.Run"])

    def test_lean_headers_outside_the_plain_layout_are_rejected(self):
        # Lean reads VE.Surface from each of these (tests/test_lean_import_reader.py
        # checks the plain ones against Lean's own header parser).
        for source in ("import\n  VE.Surface\n", "prelude import VE.Syntax import VE.Surface\n",
                       "module\n\npublic import VE.Surface\n", "import«VE».Surface\n",
                       "import /- c -/ VE.Surface\n", "import -- c\n  VE.Surface\n",
                       "/- outer /- inner -/ -/ import VE.Surface\n", "/-/-/import VE.Surface\n",
                       "import VE.Core.Bridge /-/-/import VE.Surface\n",
                       "import VE.Core.Bridge import«VE».Surface\n"):
            with self.assertRaises(check_lean_imports.HeaderError, msg=source):
                check_lean_imports.imports(source)
        for source in ('def s := "import VE.Surface"\n', "def x := Foo.import\nimportant VE.Surface\n",
                       '/- "unclosed -/\ndef s := "\\" import VE.Surface"\n',
                       "import VE.Core.Bridge\ndef «an import VE.Surface» := 1\n",
                       "import VE.Core.Bridge\ndef x := 1\nimport VE.Surface\n",
                       "/-! doc -/\nimport VE.Surface\n"):
            self.assertNotIn("VE.Surface", check_lean_imports.imports(source), source)

    def test_lean_header_outside_the_plain_layout_fails_the_checker(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "lean/VE/Core").mkdir(parents=True)
            (root / "lean/VE/Route").mkdir(parents=True)
            (root / "lean/lean-toolchain").write_text((layer_policy.ROOT / "lean/lean-toolchain").read_text())
            (root / "lean/VE/Core/Wire.lean").write_text("/-/-/import VE.Route.Run\n")
            (root / "lean/VE/Route/Run.lean").write_text("")
            ledger = root / "exceptions.json"
            ledger.write_text("{}")
            error = io.StringIO()
            with (patch.object(check_lean_imports, "ROOT", root),
                  patch.object(check_lean_imports, "LEDGER", ledger),
                  redirect_stderr(error)):
                self.assertEqual(check_lean_imports.main(), 1)
            self.assertIn("Lean header not in the plain layout: lean/VE/Core/Wire.lean: line 1: "
                          "`/-` inside a block comment", error.getvalue())
            (root / "lean/VE/Core/Wire.lean").write_text("import VE.Route.Run\n")
            error = io.StringIO()
            with (patch.object(check_lean_imports, "ROOT", root),
                  patch.object(check_lean_imports, "LEDGER", ledger),
                  redirect_stderr(error)):
                self.assertEqual(check_lean_imports.main(), 1)
            self.assertIn("new outward Lean import: VE.Core.Wire -> VE.Route.Run", error.getvalue())
            self.assertNotIn("plain layout", error.getvalue())

    def test_every_lean_and_python_module_is_classified(self):
        lean = [".".join(path.relative_to(layer_policy.ROOT / "lean").with_suffix("").parts)
                for path in (layer_policy.ROOT / "lean").rglob("*.lean")
                if ".lake" not in path.parts]
        python = [".".join(path.relative_to(layer_policy.ROOT).with_suffix("").parts)
                  .removesuffix(".__init__")
                  for path in (layer_policy.ROOT / "ve").rglob("*.py")]
        self.assertIn("Serve", lean)
        self.assertEqual([m for m in lean if layer_policy.lean_layer(m) is None], [])
        self.assertEqual([m for m in python if m != "ve" and layer_policy.python_layer(m) is None], [])

    def test_lean_entry_modules_are_tool_layer(self):
        roots = layer_policy.lean_executables().values()
        self.assertTrue({"Main", "ResponseDecode", "Serve"} <= set(roots))
        for module in (*roots, "RiskMain"):
            with self.subTest(module=module):
                self.assertEqual(layer_policy.lean_layer(module), 4)
        with patch.object(layer_policy, "lean_executables", return_value={"ve_new": "Launch"}):
            self.assertEqual(layer_policy.lean_layer("Launch"), 4)
        for module in ("Alien", "VE.RiskMain", "Launch"):
            self.assertNotEqual(layer_policy.lean_layer(module), 4, module)

    def test_new_entry_module_passes_the_lean_checker(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "lean/VE/Route").mkdir(parents=True)
            (root / "lean/VE/Route/Run.lean").write_text("")
            (root / "lean/RiskMain.lean").write_text("import VE.Route.Run\n")
            ledger = root / "exceptions.json"
            ledger.write_text("{}")
            error = io.StringIO()
            with (patch.object(check_lean_imports, "ROOT", root),
                  patch.object(check_lean_imports, "LEDGER", ledger),
                  redirect_stderr(error)):
                self.assertEqual(check_lean_imports.main(), 0, error.getvalue())

    def test_documented_python_layers_match_policy(self):
        from fnmatch import fnmatch
        import re
        rows = {}  # the layer map is the first table whose rows start with a layer number
        for line in (layer_policy.ROOT / "docs/ARCHITECTURE-LAYERS.md").read_text().splitlines():
            if re.match(r"\| [1-5] ", line):
                rows.setdefault(int(line[2]), line.split("|")[2])
        for layer, names in layer_policy.PYTHON.items():
            patterns = [p.removesuffix(".*") for p in re.findall(r"`([^`]+)`", rows[layer])
                        if p != "ve_experiments.*"]
            with self.subTest(layer=layer):
                self.assertEqual([n for n in names if not any(fnmatch(n, p) for p in patterns)], [])
                self.assertEqual([p for p in patterns if not any(fnmatch(n, p) for n in names)], [])

    def test_every_lean_executable_consumer_is_tool_layer(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "tests").mkdir()
            path = root / "tests/test_route.py"
            (root / "lean").mkdir()
            shutil.copy(layer_policy.ROOT / "lean/lakefile.toml", root / "lean/lakefile.toml")
            for name in layer_policy.lean_executables():
                source = f'BIN = ROOT / "lean" / ".lake" / "build" / "bin" / "{name}"\n'
                path.write_text(source)
                graph = source_graph.Graph(root, ["tests/test_route.py"],
                                           {"tests/test_route.py": source_graph.summarize(source, "tests.test_route")})
                graph.prepare_names()
                graph.build()
                with self.subTest(name=name):
                    self.assertIn(f"lean-exe:{name}", graph.closure("tests/test_route.py")[1])
        real_exists = Path.exists
        for binary in ("ve_conformance", "ve_service"):
            with self.subTest(binary=binary), patch.object(
                Path, "exists", lambda path: False if path.name == binary else real_exists(path)
            ):
                self.assertTrue(select(["ve/search.py"])["lean_build"])

    def test_non_default_lean_executables_are_built_by_name(self):
        # Since lean-first batch 1 no executable is outside defaultTargets (the one-shot routes,
        # `ve_risk_eval` among them, are service modes); simulate one, which a test names.
        executables = {**layer_policy.lean_executables(), "ve_risk_eval": "RiskEvalMain"}
        defaults = layer_policy.lean_default_targets()
        real_exists = Path.exists

        def clear_caches():
            for value in vars(select_tests).values():
                if hasattr(value, "cache_clear"):
                    value.cache_clear()
        clear_caches()
        with (patch.object(select_tests, "lean_executables", return_value=executables),
              patch.object(select_tests, "lean_default_targets", return_value=defaults),
              patch.object(Path, "exists",
                           lambda path: False if path.name == "ve_risk_eval" else real_exists(path))):
            plan = select(["ve/search.py"])
        clear_caches()
        self.assertIn("tests/test_risk_differential.py", plan["selected"])
        self.assertIn(["lake", "build"], plan["commands"])
        self.assertIn(["lake", "build", "ve_risk_eval"], plan["commands"])

    def test_unmapped_lean_importer_reports_error(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "lean").mkdir()
            (root / "lean" / "Alien.lean").write_text("import VE.Route.Run\n")
            ledger = root / "exceptions.json"
            ledger.write_text("{}")
            error = io.StringIO()
            with (patch.object(check_lean_imports, "ROOT", root),
                  patch.object(check_lean_imports, "LEDGER", ledger),
                  redirect_stderr(error)):
                self.assertEqual(check_lean_imports.main(), 1)
            self.assertIn("unmapped Lean module: Alien", error.getvalue())

    def test_unmapped_imported_lean_module_reports_error(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "lean/VE/Core").mkdir(parents=True)
            (root / "lean/VE/Core/Wire.lean").write_text("import Alien\n")
            (root / "lean/Alien.lean").write_text("")
            ledger = root / "exceptions.json"
            ledger.write_text("{}")
            error = io.StringIO()
            with (patch.object(check_lean_imports, "ROOT", root),
                  patch.object(check_lean_imports, "LEDGER", ledger),
                  redirect_stderr(error)):
                self.assertEqual(check_lean_imports.main(), 1)
            self.assertIn("unmapped Lean module: Alien", error.getvalue())

    def test_namespace_package_imports_resolve_to_the_package(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "ve/surface").mkdir(parents=True)
            (root / "ve/surface/registry.py").write_text("")  # no __init__.py
            for source in ("from ve import surface\n", "import ve\nve.surface\n"):
                self.assertIn("ve.surface", layer_policy.python_imports("ve.ast", source, {}, root=root))
            self.assertNotIn("ve.absent", layer_policy.python_imports(
                "ve.ast", "from ve import absent\n", {}, root=root))

    def test_experiment_import_forms_are_outer_layer(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "tests").mkdir()
            path = root / "tests/test_p1.py"
            (root / "lean").mkdir()
            (root / "lean/lakefile.toml").write_text("")
            (root / "experiments").mkdir()
            (root / "experiments/p1.py").write_text("")
            for source in ("from experiments import p1\n", "import experiments.p1\n"):
                path.write_text(source)
                files = ["experiments/p1.py", "tests/test_p1.py"]
                graph = source_graph.Graph(root, files, {
                    "experiments/p1.py": source_graph.summarize("", "experiments.p1"),
                    "tests/test_p1.py": source_graph.summarize(source, "tests.test_p1")})
                graph.prepare_names()
                graph.build()
                self.assertIn("experiments/p1.py", graph.closure("tests/test_p1.py")[0])

    def test_rust_crate_graph_kept(self):
        output = io.StringIO()
        with redirect_stdout(output):
            self.assertEqual(check_rust_deps.main(), 0)
        self.assertIn("Rust crate graph kept (4 crates; ve-core re-exports only)", output.getvalue())
        self.assertEqual(check_rust_deps.CRATE_LAYERS,
                         {"ve-kernel": 1, "ve-profile": 2, "ve-core": 3, "ve": 4})
        for path, layer in (("rust/ve-kernel/src/semantics.rs", 1), ("rust/ve-core/src/lib.rs", 1),
                            ("rust/ve-core/tests/conformance.rs", 1), ("rust/ve-profile/src/eval.rs", 2),
                            ("rust/ve/src/main.rs", 4),
                            ("rust/ve-profile/Cargo.toml", 1)):
            self.assertEqual(layer_policy.source_layer(path), layer, path)

    def test_inward_fixture_workspace_passes(self):
        with TemporaryDirectory() as directory:
            root = rust_workspace(Path(directory))
            self.assertEqual(rust_check(root), (0, ""))

    def test_outward_crate_dependencies_are_rejected(self):
        for crate, use in (("ve-kernel", "ve-profile"), ("ve-kernel", "ve-core"), ("ve-profile", "ve-core"),
                           ("ve-core", "ve")):
            with self.subTest(f"{crate} -> {use}"), TemporaryDirectory() as directory:
                root = rust_workspace(Path(directory))
                manifest = root / crate / "Cargo.toml"
                manifest.write_text(manifest.read_text() + f'{use} = {{ path = "../{use}" }}\n')
                self.assertEqual(rust_check(root), (1, f"outward crate dependency: {crate} -> {use}\n"))

    def test_renamed_and_inherited_rust_dependencies_are_read_as_cargo_resolves_them(self):
        # A target-specific build dependency under another name, and a dev dependency inherited
        # from the workspace under another name: cargo resolves both to the `ve` crate.
        for declaration, workspace in (
            ('[target."cfg(unix)".build-dependencies]\ncli = { package = "ve", path = "../ve" }\n', ""),
            ('[dev-dependencies]\ncli.workspace = true\n',
             '[workspace.dependencies]\ncli = { package = "ve", path = "ve" }\n'),
        ):
            with self.subTest(declaration), TemporaryDirectory() as directory:
                root = rust_workspace(Path(directory))
                (root / "Cargo.toml").write_text((root / "Cargo.toml").read_text() + workspace)
                manifest = root / "ve-core" / "Cargo.toml"
                manifest.write_text(manifest.read_text() + declaration)
                self.assertEqual(rust_check(root), (1, "outward crate dependency: ve-core -> ve\n"))

    def test_modules_in_the_facade_are_rejected(self):
        for module in ("extra.rs", "nested/inner.rs"):
            with self.subTest(module), TemporaryDirectory() as directory:
                root = rust_workspace(Path(directory))
                (root / "ve-core/src" / module).parent.mkdir(parents=True, exist_ok=True)
                (root / "ve-core/src" / module).write_text("")
                code, error = rust_check(root)
                self.assertEqual(code, 1)
                self.assertTrue(error.startswith(f"module in the ve-core facade: {module}; "), error)
        with TemporaryDirectory() as directory:  # cargo still reads a crate whose only targets are tests
            root = rust_workspace(Path(directory))
            (root / "ve-core/src/lib.rs").unlink()
            (root / "ve-core/tests").mkdir()
            (root / "ve-core/tests/t.rs").write_text("")
            self.assertEqual(rust_check(root), (1, "the ve-core facade has no library target\n"))

    def test_unmapped_crates_and_outside_path_dependencies_are_rejected(self):
        with TemporaryDirectory() as directory:
            root = rust_workspace(Path(directory), {**RUST_CRATES, "ve-extra": []})
            self.assertEqual(rust_check(root), (1, "unmapped crates: ['ve-extra']\n"))
        with TemporaryDirectory() as directory:
            root = rust_workspace(Path(directory) / "workspace")
            rust_workspace(Path(directory) / "outside", {"helper": []})  # a crate of another workspace
            manifest = root / "ve-profile" / "Cargo.toml"
            manifest.write_text(manifest.read_text() + 'helper = { path = "../../outside/helper" }\n')
            self.assertEqual(rust_check(root), (1, "path dependency outside the workspace: ve-profile -> helper\n"))

    def test_unreadable_rust_workspace_fails(self):
        with TemporaryDirectory() as directory:
            root = rust_workspace(Path(directory))
            (root / "ve-kernel" / "Cargo.toml").write_text("[package\n")
            code, error = rust_check(root)
            self.assertEqual(code, 1)
            self.assertTrue(error.startswith("cannot read the Rust workspace: cargo metadata failed: "), error)


class RustOutputDiffTests(unittest.TestCase):
    def compare(self, baseline_body: str, new_body: str, work=None) -> tuple[int, str]:
        with TemporaryDirectory() as directory:
            binaries = []
            for name, body in (("baseline", baseline_body), ("new", new_body)):
                path = Path(directory) / name
                path.write_text("#!/bin/sh\n" + body)
                path.chmod(0o755)
                binaries.append(path)
            output, error = io.StringIO(), io.StringIO()
            work = [rust_output_diff.Invocation("parse", "case", ())] if work is None else work
            with (patch.object(rust_output_diff, "TIMEOUT", 1),
                  patch.object(rust_output_diff, "invocations", lambda folder: work),
                  patch.object(rust_output_diff.rust_build, "pinned_digests",
                               lambda: [rust_output_diff.rust_build.digest(binaries[0])]),
                  redirect_stdout(output), redirect_stderr(error)):
                code = rust_output_diff.compare(*binaries)
            return code, output.getvalue() + error.getvalue()

    def test_any_timeout_invalidates_the_differential(self):
        for name, baseline, new in (
            ("different partial output", "echo old\nexec sleep 5\n", "echo new\nexec sleep 5\n"),
            ("same partial output", "echo same\nexec sleep 5\n", "echo same\nexec sleep 5\n"),
            ("only the new binary", "echo same\n", "echo same\nexec sleep 5\n"),
            ("only the baseline", "echo same\nexec sleep 5\n", "echo same\n"),
        ):
            with self.subTest(name):
                code, report = self.compare(baseline, new)
                self.assertEqual(code, 1, report)
                self.assertIn("INVALID differential", report)
                self.assertIn("parse case:", report)
                self.assertIn("timed out after 1 s", report)

    def test_timed_out_runs_keep_their_partial_output(self):
        code, report = self.compare("echo old\nexec sleep 5\n", "echo new\nexec sleep 5\n")
        self.assertIn("parse case: stdout differ", report)
        invocation = rust_output_diff.Invocation("parse", "case", ())
        with TemporaryDirectory() as directory:
            path = Path(directory) / "slow"
            path.write_text("#!/bin/sh\necho partial\necho warning >&2\nexec sleep 5\n")
            path.chmod(0o755)
            with patch.object(rust_output_diff, "TIMEOUT", 1):
                self.assertEqual(rust_output_diff.run(path, invocation), ("timeout", b"partial\n", b"warning\n"))

    def test_empty_invocation_list_is_invalid(self):
        code, report = self.compare("echo same\n", "echo same\n", work=[])
        self.assertEqual(code, 1, report)
        self.assertIn("INVALID differential: no invocations", report)

    def test_equal_completed_runs_pass(self):
        code, report = self.compare("echo same\n", "echo same\n")
        self.assertEqual(code, 0, report)
        self.assertIn("1 invocations, 0 differences, 0 timed out", report)


if __name__ == "__main__":
    unittest.main()
