"""Boundary checks for the selector's non-import dependencies and fallback."""
from __future__ import annotations

import unittest

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


if __name__ == "__main__":
    unittest.main()
