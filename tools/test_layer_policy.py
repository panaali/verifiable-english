"""Boundary checks for the selector's non-import dependencies and fallback."""
from __future__ import annotations

import unittest
from unittest.mock import patch
from contextlib import redirect_stderr
import io
from pathlib import Path
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
        self.assertTrue(any(command[:2] == ["cargo", "build"] for command in rust["commands"]))
        self.assertIn("tests/test_rust_conformance.py", rust["selected"])

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

    def test_both_lean_executables_are_tool_consumers(self):
        self.assertIn("tests/test_norms_three_way.py",
                      select(["lean/VE/Norms/Run.lean"])["selected"])

    def test_python_app_package_outward_import_is_detected(self):
        class Graph:
            modules = {"ve.errors", "ve_experiments", "ve_experiments.runner"}

            def find_modules_directly_imported_by(self, importer):
                return {"ve_experiments", "ve_experiments.runner"} if importer == "ve.errors" else set()

        with patch.object(check_python_layers.grimp, "build_graph", return_value=Graph()):
            self.assertIn("ve.errors -> ve_experiments.runner",
                          check_python_layers.violations())
            self.assertIn("ve.errors -> ve_experiments", check_python_layers.violations())

    def test_comment_prefixed_and_nested_lean_imports(self):
        source = "/- outer /- inner -/ -/ import VE.Route.Run\n-- import VE.Fake\n"
        self.assertEqual(check_lean_imports.imports(source), ["VE.Route.Run"])

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
