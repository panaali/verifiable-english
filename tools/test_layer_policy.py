"""Boundary checks for the selector's non-import dependencies and fallback."""
from __future__ import annotations

import unittest
from unittest.mock import patch
from contextlib import redirect_stderr
import io
from pathlib import Path
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
import select_tests

from select_tests import select


class LayerSelectionTests(unittest.TestCase):
    def test_app_change_keeps_cross_cutting_tests_and_app_consumer(self):
        plan = select(["ve_experiments/t1c/materials.py"])
        self.assertEqual(plan["minimum_layer"], 5)
        self.assertLess(plan["selected_count"], plan["full_count"])
        self.assertIn("tests/test_t1c.py", plan["selected"])
        self.assertIn("tests/test_assist_recovery_replay.py", plan["selected"])
        self.assertIn("tests/test_assist_deadline.py", plan["selected"])
        self.assertTrue(set(plan["always"]) <= set(plan["selected"]))
        usecase = select(["usecases/asimov-laws/rules.ve"])
        self.assertIn("tests/test_asimov_laws.py", usecase["selected"])

    def test_native_inputs_schedule_their_builds(self):
        lean = select(["lean/VE/Norms/Wire.lean"])
        rust = select(["rust/ve/src/main.rs"])
        self.assertIn(["lake", "build"], lean["commands"])
        self.assertTrue(any(command[:2] == ["cargo", "test"] for command in rust["commands"]))
        self.assertIn(["cargo", "build", "--locked", "--release", "--manifest-path",
                       "rust/Cargo.toml", "-p", "ve"], rust["commands"])
        self.assertIn(["cargo", "build", "--locked", "--manifest-path",
                       "rust/Cargo.toml", "-p", "ve"], rust["commands"])
        self.assertLess(rust["commands"].index(["cargo", "build", "--locked",
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
        self.assertIn(["cargo", "build", "--locked", "--manifest-path",
                       "rust/Cargo.toml", "-p", "ve"], plan["commands"])

    def test_unknown_input_falls_back_to_full_native_and_python_suite(self):
        plan = select(["new-unmapped-format.xyz"])
        self.assertEqual(plan["selected_count"], plan["full_count"])
        self.assertTrue(plan["lean_build"] and plan["rust_build"])
        shared = select(["conformance/README.md"])
        self.assertEqual(shared["minimum_layer"], 1)

    def test_reviewed_outward_imports_select_inner_consumers(self):
        self.assertIn("tests/test_norms.py", select(["ve/search.py"])["selected"])
        self.assertIn("tests/test_norms.py", select(["ve/surface/registry.py"])["selected"])
        self.assertEqual(select(["ve/surface/registry.py"])["minimum_layer"], 1)
        self.assertEqual(select(["ve_experiments/assist_haiku.py"])["minimum_layer"], 4)
        self.assertEqual(select(["ve/surface/__init__.py"])["minimum_layer"], 1)

    def test_transitive_source_imports_select_surface_consumers(self):
        for source in ("ve/admission.py", "ve/vacuity.py"):
            with self.subTest(source=source):
                plan = select([source])
                self.assertLessEqual(plan["minimum_layer"], 3)
                self.assertIn("tests/test_english.py", plan["selected"])

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
        with patch.object(Path, "exists", lambda path: False if path.name == "ve_norms_route"
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

    def test_comment_prefixed_and_nested_lean_imports(self):
        source = "/- outer /- inner -/ -/ import VE.Route.Run\n-- import VE.Fake\n"
        self.assertEqual(check_lean_imports.imports(source), ["VE.Route.Run"])
        self.assertEqual(check_lean_imports.imports("import «VE».Route.Run\n"),
                         ["VE.Route.Run"])

    def test_lean_import_forms_the_header_parser_accepts(self):
        # Each form was checked against `lake env lean` on the pinned toolchain
        # (`public import` needs -Dexperimental.module=true).
        for source in ("import\n  VE.Surface\n", "import\r\n  VE.Surface\r\n",
                       "prelude import VE.Syntax import VE.Surface\n",
                       "module\n\npublic import VE.Surface\n", "import«VE».Surface\n",
                       "import /- c -/ VE.Surface\n", "import -- c\n  VE.Surface\n"):
            self.assertIn("VE.Surface", check_lean_imports.imports(source), source)
        for source in ('def s := "import VE.Surface"\n', "def x := Foo.import\nimportant VE.Surface\n",
                       '/- "unclosed -/\ndef s := "\\" import VE.Surface"\n'):
            self.assertNotIn("VE.Surface", check_lean_imports.imports(source), source)

    def test_quoted_lean_local_import_is_checked(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "lean/VE/Core").mkdir(parents=True)
            (root / "lean/VE/Route").mkdir(parents=True)
            (root / "lean/VE/Core/Wire.lean").write_text("import «VE».Route.Run\n")
            (root / "lean/VE/Route/Run.lean").write_text("")
            ledger = root / "exceptions.json"
            ledger.write_text("{}")
            error = io.StringIO()
            with (patch.object(check_lean_imports, "ROOT", root),
                  patch.object(check_lean_imports, "LEDGER", ledger),
                  redirect_stderr(error)):
                self.assertEqual(check_lean_imports.main(), 1)
            self.assertIn("new outward Lean import: VE.Core.Wire -> VE.Route.Run", error.getvalue())

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
            for source in ("from experiments import p1\n", "import experiments.p1\n"):
                path.write_text(source)
                select_tests.test_layer.cache_clear()
                with patch.object(select_tests, "ROOT", root):
                    self.assertEqual(select_tests.test_layer(path), 5)
            select_tests.test_layer.cache_clear()

    def test_renamed_rust_dependency_in_target_and_workspace_sections(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            for crate in ("ve", "ve-core"):
                (root / crate).mkdir()
                (root / crate / "Cargo.toml").write_text(f'[package]\nname = "{crate}"\n')
            (root / "Cargo.toml").write_text(
                '[workspace]\nmembers = ["ve-core", "ve"]\n'
                '[workspace.dependencies]\ncli = { package = "ve", path = "ve" }\n')
            core = root / "ve-core" / "Cargo.toml"
            for declaration in (
                '[target."cfg(unix)".build-dependencies]\n'
                'cli = { package = "ve", path = "../ve" }\n',
                '[dev-dependencies]\ncli.workspace = true\n',
            ):
                core.write_text('[package]\nname = "ve-core"\n' + declaration)
                error = io.StringIO()
                with patch.object(check_rust_deps, "WORKSPACE", root), redirect_stderr(error):
                    self.assertEqual(check_rust_deps.main(), 1)
                self.assertIn("outward crate dependency: ve-core -> ve", error.getvalue())


if __name__ == "__main__":
    unittest.main()
