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

from select_tests import select

# Each case is a compilable ve-core-shaped crate (`cargo check` accepts it): extra lib.rs
# items, then the ast.rs (kernel), eval.rs (profile) and surface.rs bodies, and the outward
# edges the module check must report.
SURFACE_RS = "pub fn parse<T: Default>() -> T { T::default() }\npub struct Node;\n"
RUST_MODULE_CASES = {
    "turbofish": ("", "pub fn f() -> u8 { crate::surface::parse::<u8>() }\n", "", SURFACE_RS,
                  {"ast -> surface"}),
    "turbofish in a use-free call chain": (
        "", "pub fn f() -> Vec<u8> { crate::surface::parse::<Vec<u8>>() }\n", "", SURFACE_RS,
        {"ast -> surface"}),
    "crate-prefixed root re-export": ("pub use crate::surface::parse;\n",
                                      "pub fn f() -> u8 { crate::parse() }\n", "", SURFACE_RS,
                                      {"ast -> surface"}),
    "self-prefixed aliased root re-export": ("pub use self::surface::parse as read;\n",
                                             "use crate::read;\npub fn f() -> u8 { read() }\n", "",
                                             SURFACE_RS, {"ast -> surface"}),
    "private root import": ("use surface::parse;\n", "pub fn f() -> u8 { crate::parse() }\n", "",
                            SURFACE_RS, {"ast -> surface"}),
    "module alias": ("pub(crate) use surface as syntax;\n", "pub fn f() -> u8 { crate::syntax::parse() }\n",
                     "", SURFACE_RS, {"ast -> surface"}),
    "root glob": ("pub use surface::*;\n", "pub fn f() -> u8 { crate::parse() }\n", "", SURFACE_RS,
                  {"ast -> surface"}),
    "chained module re-export": ("", "pub fn f() -> u8 { crate::eval::parse::<u8>() }\n",
                                 "pub use crate::surface::parse;\n", SURFACE_RS,
                                 {"ast -> eval", "ast -> surface", "eval -> surface"}),
    "module glob re-export": ("", "use crate::eval::parse;\npub fn f() -> u8 { parse() }\n",
                              "pub use crate::surface::*;\n", SURFACE_RS,
                              {"ast -> eval", "ast -> surface", "eval -> surface"}),
    "re-export inside an inline root module": (
        "pub mod api { pub use crate::surface::parse; }\n", "pub fn f() -> u8 { crate::api::parse() }\n",
        "", SURFACE_RS, {"ast -> surface"}),
    "raw identifier": ("", "pub fn f() -> u8 { crate::r#surface::parse() }\n", "", SURFACE_RS,
                       {"ast -> surface"}),
    "super from a nested module": (
        "", "mod inner {\n    pub fn f() -> u8 { super::super::surface::parse() }\n}\n", "", SURFACE_RS,
        {"ast -> surface"}),
    "root glob import": ("", "use crate::*;\npub fn f() -> u8 { surface::parse() }\n", "", SURFACE_RS,
                         {"ast -> eval", "ast -> surface"}),
    "nested super stays in the file": (
        "pub use surface::parse;\n",
        "pub fn g() -> u8 { 1 }\n#[cfg(test)]\nmod tests {\n    use super::*;\n"
        "    #[test]\n    fn t() { assert_eq!(g(), 1); }\n}\n",
        "pub fn h() -> u8 { 2 }\nmod tests {\n    use super::*;\n    pub fn k() -> u8 { h() }\n}\n",
        SURFACE_RS, set()),
    # Names bound by `use` items are path heads too, and identifiers are Unicode, compared after NFC.
    "crate alias": ("", "use crate as root;\npub fn f() -> u8 { root::surface::parse() }\n", "", SURFACE_RS,
                    {"ast -> surface"}),
    "super self alias": ("", "use super::{self as root};\npub fn f() -> u8 { root::surface::parse() }\n", "",
                         SURFACE_RS, {"ast -> surface"}),
    "crate self alias": ("", "use crate::{self as root};\npub fn f() -> u8 { root::surface::parse() }\n", "",
                         SURFACE_RS, {"ast -> surface"}),
    "Unicode re-export": ("pub use surface::parse as 読む;\n", "pub fn f() -> u8 { crate::読む() }\n", "",
                          SURFACE_RS, {"ast -> surface"}),
    "NFD identifier names the NFC re-export": (
        "pub use surface::parse as café;\n", "pub fn f() -> u8 { crate::café() }\n", "", SURFACE_RS,
        {"ast -> surface"}),
    "chained local aliases": (
        "", "use crate as root;\nuse root::surface as syntax;\npub fn f() -> u8 { syntax::parse() }\n", "",
        SURFACE_RS, {"ast -> surface"}),
    "re-export through a private alias": (
        "", "pub fn f() -> u8 { crate::eval::parse::<u8>() }\n", "use crate as root;\npub use root::surface::parse;\n",
        SURFACE_RS, {"ast -> eval", "ast -> surface", "eval -> surface"}),
    "nested block comment ends where rustc ends it": (
        "", '/* /* */ " */\npub fn f() -> u8 { crate::surface::parse() } // "\n', "", SURFACE_RS,
        {"ast -> surface"}),
    # Re-exports at any inline-module depth, and globs of the crate root.
    "nested inline root re-export": (
        "pub mod api { pub mod nested { pub use super::super::surface::parse; } }\n",
        "pub fn f() -> u8 { crate::api::nested::parse() }\n", "", SURFACE_RS, {"ast -> surface"}),
    "root glob inside an inline root module": (
        "pub mod api { pub use crate::*; }\n", "pub fn f() -> u8 { crate::api::surface::parse() }\n", "",
        SURFACE_RS, {"ast -> surface"}),
    "nested inline re-export in a profile module": (
        "", "pub fn f() -> u8 { crate::eval::api::nested::parse::<u8>() }\n",
        "pub mod api { pub mod nested { pub use super::super::super::surface::parse; } }\n", SURFACE_RS,
        {"ast -> eval", "ast -> surface", "eval -> surface"}),
    "root glob re-exported by a profile module": (
        "", "pub fn f() -> u8 { crate::eval::surface::parse::<u8>() }\n", "pub use crate::*;\n", SURFACE_RS,
        {"ast -> eval", "ast -> surface", "eval -> surface"}),
    "range to a surface item": (
        "", "pub fn f() -> core::ops::RangeTo<u8> { ..crate::surface::parse() }\n", "", SURFACE_RS,
        {"ast -> surface"}),
    # A proc-macro attribute may expand a string into a path; a builtin attribute's text names nothing.
    "serde path argument": (
        "", '#[derive(serde::Serialize)]\npub struct S {\n    #[serde(serialize_with = "crate::surface::write")]\n'
        "    f: u8,\n}\n", "",
        SURFACE_RS + "pub fn write<S: serde::Serializer>(v: &u8, s: S) -> Result<S::Ok, S::Error> {\n"
        "    s.serialize_u8(*v)\n}\n", {"ast -> surface"}),
    "builtin attribute text": ("", '#[deprecated(note = "crate::surface::parse")]\npub fn g() {}\n', "",
                               SURFACE_RS, set()),
    # The root's own items are kernel, including what its macros expand to.
    "root item calls the surface": ("pub fn helper() -> u8 { surface::parse() }\n",
                                    "pub fn f() -> u8 { crate::helper() }\n", "", SURFACE_RS, {"lib -> surface"}),
    "root macro names the surface": (
        "macro_rules! parsed { () => { $crate::surface::parse::<u8>() }; }\npub fn g() -> u8 { parsed!() }\n",
        "", "", SURFACE_RS, {"lib -> surface"}),
}
RUST_UNSUPPORTED_CASES = (
    ('#[path = "surface.rs"]\nmod other;\n', SURFACE_RS, "#[path"),
    ('#[cfg_attr(all(), path = "surface.rs")]\nmod other;\n', SURFACE_RS, "#[path"),
    ("", SURFACE_RS + "#[macro_export]\nmacro_rules! parsed { () => { 0u8 }; }\n", "#[macro_export"),
    ("#[macro_use]\nmod macros {}\n", SURFACE_RS, "#[macro_use"),
    ('include!("surface.rs");\n', "", "include!"),
    ('use std::include as source;\nsource!("surface.rs");\n', "", "include!"),
    ("extern crate self as fixture;\n", SURFACE_RS, "extern crate self"),
    ("macro_rules! call { ($m:ident) => { $crate::$m::parse::<u8>() }; }\npub fn g() -> u8 { call!(surface) }\n",
     SURFACE_RS, "::$"),
)


def rust_module_fixture(root: Path, lib: str, ast: str, eval_: str, surface: str, name: str = "fixture") -> Path:
    source = root / "src"
    source.mkdir(parents=True)
    serde = '[dependencies]\nserde = { version = "1", features = ["derive"] }\n' if "serde" in ast + surface else ""
    (root / "Cargo.toml").write_text(f'[package]\nname = "{name}"\nversion = "0.0.0"\nedition = "2024"\n'
                                     '[lib]\npath = "src/lib.rs"\n' + serde)
    (source / "lib.rs").write_text("#![allow(dead_code, unused_imports)]\nmod ast;\nmod eval;\n"
                                   "mod surface;\n" + lib)
    for module, text in (("ast", ast), ("eval", eval_), ("surface", surface)):
        (source / f"{module}.rs").write_text(text)
    return source


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
        self.assertIn("AlternativesMain", lean)
        self.assertEqual([m for m in lean if layer_policy.lean_layer(m) is None], [])
        self.assertEqual([m for m in python if m != "ve" and layer_policy.python_layer(m) is None], [])

    def test_lean_entry_modules_are_tool_layer(self):
        roots = layer_policy.lean_executables().values()
        self.assertTrue({"Main", "AlternativesMain", "ReportsMain", "Serve"} <= set(roots))
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
            for name in layer_policy.lean_executables():
                path.write_text(f'BIN = ROOT / "lean" / ".lake" / "build" / "bin" / "{name}"\n')
                select_tests.test_layer.cache_clear()
                with self.subTest(name=name), patch.object(select_tests, "ROOT", root):
                    self.assertEqual(select_tests.test_layer(path), 4)
            select_tests.test_layer.cache_clear()
        real_exists = Path.exists
        for binary in ("ve_quantity", "ve_discourse_route", "ve_reports_route"):
            with self.subTest(binary=binary), patch.object(
                Path, "exists", lambda path: False if path.name == binary else real_exists(path)
            ):
                self.assertTrue(select(["ve/search.py"])["lean_build"])

    def test_non_default_lean_executables_are_built_by_name(self):
        self.assertIn("ve_risk_eval", layer_policy.lean_executables())
        # Simulate a route outside defaultTargets; the current lakefile builds it
        # by default, but the selector must still support explicitly named builds.
        defaults = layer_policy.lean_default_targets() - {"ve_risk_eval"}
        real_exists = Path.exists
        with (patch.object(select_tests, "lean_default_targets", return_value=defaults),
              patch.object(Path, "exists",
                           lambda path: False if path.name == "ve_risk_eval" else real_exists(path))):
            plan = select(["ve/search.py"])
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
                    self.assertEqual(check_rust_deps.main(["--crates-only"]), 1)
                self.assertIn("outward crate dependency: ve-core -> ve", error.getvalue())

    def test_rust_module_ledger_matches_the_tree(self):
        source = check_rust_deps.WORKSPACE / "ve-core/src"
        edges, errors = check_rust_deps.module_edges("ve-core", source, check_rust_deps.MODULE_GROUPS["ve-core"])
        self.assertEqual(errors, [])
        self.assertEqual(edges, set(json.loads(check_rust_deps.MODULE_LEDGER.read_text())))
        self.assertEqual(edges, {"ve-core: environment -> route", "ve-core: model -> eval",
                                 "ve-core: wire -> surface"})
        output = io.StringIO()
        with redirect_stdout(output):
            self.assertEqual(check_rust_deps.main(), 0)
        self.assertIn("module graph kept (3 reviewed legacy edges)", output.getvalue())

    def test_outward_rust_module_imports_are_rejected(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "Cargo.toml").write_text('[workspace]\nmembers = ["ve-core", "ve"]\n')
            for crate in ("ve", "ve-core"):
                (root / crate / "src/nested").mkdir(parents=True)
                (root / crate / "Cargo.toml").write_text(f'[package]\nname = "{crate}"\n')
            source = root / "ve-core/src"
            (source / "lib.rs").write_text("mod ast;\nmod eval;\nmod surface;\nmod wire;\nmod model;\n"
                                           "pub use eval::{evaluate as run, Evaluation};\n"
                                           "pub use surface::parse;\n")
            (source / "eval.rs").write_text("use crate::{Error, ast::Formula};\n")
            (source / "surface.rs").write_text("use crate::eval::Evaluation;\n")
            (source / "ast.rs").write_text('// crate::surface::parse\nconst S: &str = "crate::surface";\n'
                                           "use crate::{Error, MAX_DEPTH};\n")
            (source / "wire.rs").write_text("use crate::{\n    Error,\n    run as evaluate,\n};\n"
                                            "fn f() { crate::surface::formula_record(1); }\n")
            (source / "model.rs").write_text("use super::parse;\nmod tests {\n    use super::*;\n}\n")
            (source / "extra.rs").write_text("")
            (source / "nested/inner.rs").write_text("")
            ledger = root / "exceptions.json"
            ledger.write_text(json.dumps({"ve-core: ast -> surface": "planted stale key"}))
            error = io.StringIO()
            with (patch.object(check_rust_deps, "WORKSPACE", root),
                  patch.object(check_rust_deps, "MODULE_LEDGER", ledger), redirect_stderr(error)):
                self.assertEqual(check_rust_deps.main(), 1)
            self.assertEqual(sorted(error.getvalue().splitlines()), [
                "new outward Rust module import: ve-core: model -> surface",
                "new outward Rust module import: ve-core: wire -> eval",
                "new outward Rust module import: ve-core: wire -> surface",
                "stale Rust module exception: ve-core: ast -> surface",
                "unmapped Rust module: ve-core: extra",
                "unmapped Rust module: ve-core: nested/inner.rs",
            ])
            error = io.StringIO()
            with (patch.object(check_rust_deps, "WORKSPACE", root),
                  patch.object(check_rust_deps, "MODULE_LEDGER", ledger), redirect_stderr(error)):
                self.assertEqual(check_rust_deps.main(["--crates-only"]), 0, error.getvalue())

    def test_rust_module_paths_resolve_generics_and_reexports(self):
        groups = check_rust_deps.MODULE_GROUPS["ve-core"]
        for name, (lib, ast, eval_, surface, expected) in RUST_MODULE_CASES.items():
            with self.subTest(name), TemporaryDirectory() as directory:
                source = rust_module_fixture(Path(directory), lib, ast, eval_, surface)
                edges, errors = check_rust_deps.module_edges("ve-core", source, groups)
                self.assertEqual(errors, [])
                self.assertEqual(edges, {f"ve-core: {edge}" for edge in expected})

    def test_unsupported_rust_module_constructs_fail_closed(self):
        groups = check_rust_deps.MODULE_GROUPS["ve-core"]
        for lib, surface, construct in RUST_UNSUPPORTED_CASES:
            with self.subTest(lib), TemporaryDirectory() as directory:
                source = rust_module_fixture(Path(directory), lib, "", "", surface)
                _, errors = check_rust_deps.module_edges("ve-core", source, groups)
                self.assertEqual(len(errors), 1, errors)
                self.assertTrue(errors[0].startswith("unsupported Rust construct: ve-core: "), errors)
                self.assertIn(repr(construct), errors[0])
        with TemporaryDirectory() as directory:  # rustc rejects a no-break space between tokens
            source = rust_module_fixture(Path(directory), "pub fn g()\u00a0{}\n", "", "", SURFACE_RS)
            _, errors = check_rust_deps.module_edges("ve-core", source, groups)
            self.assertEqual(errors, ["unsupported Rust construct: ve-core: lib: '\\xa0'"])

    def test_rust_tokens_follow_rustc(self):
        text = ('/* a /* b */ crate::x */ r##"crate::y"#"## b\'"\' \'\\u{22}\' \'a r#crate1::café '
                "cafe\u0301 c\"z\" x.0 1u8")
        self.assertEqual([(token.kind, token.text) for token in check_rust_deps.tokens(text)],
                         [("string", 'crate::y"#'), ("ident", "crate1"), ("::", "::"), ("ident", "café"),
                          ("ident", "café"), ("string", "z"), ("ident", "x"), ("punct", ".")])
        self.assertTrue(check_rust_deps.tokens("r#crate1")[0].raw)

    @unittest.skipUnless(shutil.which("cargo"), "cargo is not installed")
    def test_rust_module_fixtures_compile(self):
        """Every module-check fixture is real Rust: `cargo check` accepts all of them."""
        fixtures = [(lib, ast, eval_, surface) for lib, ast, eval_, surface, _ in RUST_MODULE_CASES.values()]
        fixtures += [(lib, "", "", surface) for lib, surface, _ in RUST_UNSUPPORTED_CASES]
        with TemporaryDirectory() as directory:
            root = Path(directory)
            members = [f"f{index}" for index in range(len(fixtures))]
            (root / "Cargo.toml").write_text(f"[workspace]\nresolver = \"3\"\nmembers = {json.dumps(members)}\n")
            for member, (lib, ast, eval_, surface) in zip(members, fixtures):
                rust_module_fixture(root / member, lib, ast, eval_, surface, name=f"fixture-{member}")
            result = subprocess.run(["cargo", "check", "--offline", "--quiet", "--workspace"], cwd=root,
                                    capture_output=True, text=True, env={**os.environ, "CARGO_TARGET_DIR":
                                                                         str(root / "target")})
            self.assertEqual(result.returncode, 0, result.stderr)


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
