"""Gate 2 inventory lint: no retained code imports a class-A body.

SEMANTICS-MIGRATION-PLAN.md section 1.4: a class-A symbol's verdict moves
behind an adapter with the same signature, and its Python body is deleted in
stage 5. Retained code (everything that is not itself a class-A body) may call
the adapter entry points, never a body directly, or the body would keep
producing verdicts outside the selected authority.

`BODIES` names, per module, the retained Python implementations behind the
stage-2 adapters and the class-A bodies of `tools/semantic_inventory.py` whose
public entry point is not yet an adapter. The lint walks every function and
method in `ve/` (module level included), resolves the `from … import` bindings
it uses, including function-local imports, and reports each use of another
module's body from code that is not itself a body. `EXCEPTIONS` records the
reviewed uses that stay, each with its reason; any other use fails the lint.

Run ``python3 tools/inventory_lint.py`` (exit 1 on a violation).
"""
from __future__ import annotations

import ast
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]

# The class-A bodies: retained Python verdicts behind an adapter (their public
# entry point dispatches), then class-A entry points that have no adapter yet
# and are therefore bodies themselves.
BODIES: dict[str, set[str]] = {
    "ve.ast": {"_Checker"},
    "ve.environment": {"Environment._decode"},
    "ve.model": {"FiniteModel._decode"},
    # `_validate_model` (inventory A) now only checks the container and calls the
    # FiniteModel.from_dict adapter.
    "ve.evaluate": {"_evaluate_validated"},
    "ve.search": {"_check_countermodel_values"},
    "ve.entailment": {"_Replayer", "_check_certificate_python"},
    "ve.order": {"decode_trace", "_Replayer", "replay_trace"},
    "ve.background": {"_validate_background_python",
                      "_valid_flags", "_valid_definitions", "_valid_literals", "_valid_profile",
                      "_valid_soft", "_valid_rights", "_valid_fill"},
    "ve.definitions": {"_compile_python"},
    "ve.norms": {"NormDocument._elaborate_python", "NormDocument._premises_python", "check_witness",
                 "_check_conflict_python", "_norm_certificate_python"},
    "ve.norm_defaults_route": {"admit_norm_defaults_document"},
    "ve.bundle": {"_check_bundle_python"},
    "ve.parser": {"_parse_python", "_parse_python_marked"},
    "ve.vacuity": {"_premise_status"},
    "ve.equivalence": {"_compare"},
    "ve.argument": {"_check_argument_python", "_check_edge", "_lean_deductions"},
    "ve.readings": {"_check_readings_python"},
}

# Reviewed uses of a body by retained code: (consumer module, consumer
# function, provider module, body) -> reason.
GENERATOR = ("untrusted generator (inventory class U): it only proposes a witness or proof, "
             "which the selected authority checks before anything is reported")
SURFACE = ("surface decoder (inventory class S) typing open formulas, which no adapter types; "
           "every operation the decoded object reaches re-decodes and checks it on the selected authority")
DIAGNOSTIC = ("wire contract hook (docs/spec/wire-contract-s5.md 2.5), diagnostic only: it runs after the "
              "legacy validator has rejected, retypes as the validator did to name the first failing check, and "
              "decides no verdict")
EXCEPTIONS: dict[tuple[str, str, str, str], str] = {
    ("ve.closure", "derive_induction", "ve.ast", "_Checker"): GENERATOR,
    ("ve.norms", "_find_conflict", "ve.ast", "_Checker"): GENERATOR,
    ("ve.entailment", "_validate_inputs", "ve.ast", "_Checker"):
        "structural re-typing of generated premises (regenerated Background, whose generator is the "
        "checker's), as ast._typed does; case premises and conclusions go through check_document",
    ("ve.norms", "NormDocument.__init__", "ve.ast", "_Checker"):
        SURFACE + " (the Lean norms route decodes and validates the norm objects: Norms.Wire.decodeSource)",
    ("ve.norm_english", "_parse_guard", "ve.ast", "_Checker"): SURFACE,
    ("ve.speech_english", "_body", "ve.ast", "_Checker"):
        SURFACE + " (English E3 remains the parser owner; the speech-source route checks its structured result)",
    ("ve.norms_contract", "typing_failure", "ve.ast", "_Checker"): DIAGNOSTIC,
    ("ve.norm_defaults_contract", "filled_ast_fits", "ve.ast", "_Checker"): DIAGNOSTIC,
    ("ve.admission", "_admit_lean", "ve.norm_defaults_route", "admit_norm_defaults_document"):
        "envelope routing to the Lean norm-defaults route (lean-first batch 10b), which decides; no Python "
        "verdict (lean-first batch 13b deleted the Python admission that called it before)",
}


def module_name(path: Path) -> str:
    return ".".join(path.relative_to(ROOT).with_suffix("").parts)


def resolve(current: str, node: ast.ImportFrom) -> str:
    if not node.level:
        return node.module or ""
    package = current.split(".")[:-1]
    base = package[:len(package) - node.level + 1]
    return ".".join(base + ([node.module] if node.module else []))


def owners(tree: ast.Module):
    """(qualified name, node) for the module body and every function or method."""
    yield "<module>", tree
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            yield node.name, node
        elif isinstance(node, ast.ClassDef):
            for child in node.body:
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    yield f"{node.name}.{child.name}", child


def is_body(module: str, qualified: str) -> bool:
    bodies = BODIES.get(module, set())
    return qualified in bodies or qualified.split(".")[0] in bodies


def uses(current: str, tree: ast.Module):
    """(consumer function, provider module, provider symbol, line) for every use of
    an imported ve symbol; module-level imports are charged to each function
    that reads the name."""
    module_bindings = {}
    for node in tree.body:
        if isinstance(node, ast.ImportFrom):
            provider = resolve(current, node)
            for alias in node.names:
                module_bindings[alias.asname or alias.name] = (provider, alias.name, node.lineno)
    for qualified, owner in owners(tree):
        bindings = dict(module_bindings) if qualified != "<module>" else {}
        nodes = list(ast.walk(owner)) if qualified != "<module>" else [
            n for top in owner.body if not isinstance(top, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
            for n in ast.walk(top)]
        for node in nodes:
            if isinstance(node, ast.ImportFrom):
                provider = resolve(current, node)
                for alias in node.names:
                    bindings[alias.asname or alias.name] = (provider, alias.name, node.lineno)
        for node in nodes:
            name = None
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                name = node.id
            if name in bindings:
                provider, symbol, line = bindings[name]
                yield qualified, provider, symbol, getattr(node, "lineno", line)
            if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
                # `module.symbol` through `from . import module` or `import ve.x as m`.
                base = bindings.get(node.value.id)
                if base is not None and base[1] != "*":
                    provider = f"{base[0]}.{base[1]}" if base[0] else base[1]
                    yield qualified, provider, node.attr, node.lineno


def violations():
    found, excepted = [], []
    for path in sorted((ROOT / "ve").rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        current = module_name(path)
        tree = ast.parse(path.read_text(), filename=str(path))
        seen = set()
        for consumer, provider, symbol, line in uses(current, tree):
            head = symbol.split(".")[0]
            bodies = BODIES.get(provider, set())
            if not (symbol in bodies or head in bodies):
                continue
            if provider == current or is_body(current, consumer):
                continue  # the adapter wiring its own body, or one body using another
            key = (current, consumer, provider, symbol)
            if key in seen:
                continue
            seen.add(key)
            row = {"consumer": f"{current}:{consumer}", "provider": f"{provider}:{symbol}",
                   "line": f"{path.relative_to(ROOT)}:{line}"}
            if key in EXCEPTIONS:
                excepted.append({**row, "reason": EXCEPTIONS[key]})
            else:
                found.append(row)
    return found, excepted


def main() -> int:
    found, excepted = violations()
    for row in excepted:
        print(f"recorded  {row['line']}: {row['consumer']} uses {row['provider']} ({row['reason']})")
    for row in found:
        print(f"VIOLATION {row['line']}: {row['consumer']} uses {row['provider']}")
    print(f"{'FAIL' if found else 'PASS'}: {len(found)} violations, {len(excepted)} recorded exceptions")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
