"""Generate the Stage 0, AST based dependency and deletion inventory.

Run ``python3 tools/semantic_inventory.py --write``. The external repositories are
read when present; their absence is reported rather than silently ignored.
"""
from __future__ import annotations

import argparse
import ast
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXTERNAL = (Path.home() / "code/ve-webapp", Path.home() / "code/ve-bench")
SCOPES = (ROOT / "ve", ROOT / "tests", ROOT / "conformance", ROOT / "ve_experiments", *EXTERNAL)
TARGETS = {
    "ast", "environment", "model", "evaluate", "search", "entailment", "closure",
    "order", "background", "definitions", "norms", "norm_admission", "admission",
    "bundle", "profiles", "parser", "printer", "argument",
}
INTERFACES = {
    "ast": "Lean typecheck / formula decode", "environment": "Lean environment / route gate",
    "model": "Lean model decode", "evaluate": "Lean evaluate; Rust budgeted evaluation",
    "search": "Lean countermodel check; Rust search", "entailment": "Lean certificate replay",
    "closure": "Lean closure certificate", "order": "Lean order certificate",
    "background": "Lean background / dependency-order", "definitions": "Lean background definitions",
    "norms": "Lean norms route", "norm_admission": "Lean norms admission",
    "admission": "Lean admission / label", "bundle": "Lean bundle",
    "profiles": "Lean route gate", "parser": "Lean parse / normalize",
    "printer": "Lean canonical field", "argument": "Lean graph report and edge checks",
}

# Explicit policy for public or semantically important symbols. Search code and
# its shared rule machinery remain U until its Rust replacement passes Gate 2.
AUTHORITY = {
    "ast": {"_Checker", "check_formula", "check_document"},
    "environment": {"Environment.__init__", "Environment.from_dict", "Environment.from_json"},
    "model": {"FiniteModel.from_dict", "FiniteModel.from_json"},
    "evaluate": {"_evaluate_validated", "evaluate", "_validate_model"},
    "search": {"check_countermodel", "_check_countermodel_values", "find_countermodel", "find_distinguishing_model"},
    "entailment": {"_Replayer", "check_entailment_certificate"},
    "order": {"decode_trace", "_Replayer", "replay_trace"},
    "background": {"background", "checked_premises", "validate_background", "dependency_order", "dependency_order_nodes"},
    "definitions": {"compile_definitions", "expand"},
    "norms": {"NormDocument.elaborate", "NormDocument.premises", "NormDocument.conflict_targets", "check_witness", "check_norm_entailment_certificate", "check_conflict"},
    "norm_admission": {"admit_norm_document"},
    "admission": {"_check_graph", "admit_document"},
    "bundle": {"check_bundle"},
    "profiles": {"checker_family"},
    "parser": {"parse_with_metadata", "parse", "canonicalize", "is_canonical"},
    "argument": {"_check_edge", "_lean_deductions", "check_argument"},
}
UNTRUSTED = {
    "ast": {"_Decoder", "formula_from_data", "document_from_data", "doc_from_json", "_to_data", "formula_to_data", "document_to_data"},
    "evaluate": {"Explanation", "EvaluationResult", "_Evaluator", "_Exhausted"},
    "search": {"_used_predicates", "_models", "_order_models", "_nonvacuous", "_SearchSpaceLimit"},
    "entailment": {"_Signed", "_Branch", "_InvalidTrace", "_term_token", "_derive", "_apply", "_closed", "_Searcher", "prove_entailment", "_prove_order"},
    "closure": {"InductionInvariant", "derive_extra", "extra_candidates", "derive_induction", "induction_candidates"},
    "order": {"Signed", "Branch", "_Search", "search", "closed", "next_branches", "neq_split", "farkas_closes", "constraint", "linearize", "_fourier_motzkin", "_cut_wire"},
    "background": {"Premise", "HOOKS"},
    "definitions": {"Definition", "_atom", "premise"},
    "norms": {"Norm", "_atom", "prove_norm_entailment"},
    "admission": {"token", "_check_kind", "parse_label", "validate_label", "_decode_reading_set"},
    "parser": {"SourceMetadata", "ParseResult", "_Parser"},
    "printer": {"_Traversal", "print_formula", "print_document"},
    "argument": {"_validate_graph"},
}
SURFACE = {
    "ast": {"Document", "Var", "Const", "Num", "Add", "Scale", "Top", "Bottom", "Unary", "Binary", "Atom", "Eq", "Not", "And", "Or", "Implies", "Forall", "Exists", "Named", "Body", "Reach", "Lt", "Le", "integer_value", "decimal_from_wire", "decimal_to_wire"},
    "environment": {"Environment", "valid_identifier", "validate_identifier", "SortVerbalisation", "SortDecl", "PredicateDecl", "RegulatedDecl", "ConstantDecl"},
    "model": {"FiniteModel", "_normalized", "_cell"},
    "argument": {"Claim", "Evidence", "Deduction", "ArgumentGraph", "ArgumentResult", "deduction_identity", "outstanding_obligations", "predicate_use_panel"},
    "norms": {"NormDocument.__init__", "NormDocument._decode", "NormDocument.meaning_id", "NormDocument.base_environment"},
    "printer": {"render", "render_cell", "render_vocabulary", "NaturalView", "natural_document", "natural_formula", "lint_vocabulary", "VocabularyLint", "measure_view_lengths", "measure_jsonl_lengths"},
    "profiles": {"ProfileRecord", "require_checker"},
}


def module_name(path: Path) -> str | None:
    try:
        rel = path.relative_to(ROOT)
    except ValueError:
        return None
    if rel.parts[0] != "ve":
        return None
    return ".".join(rel.with_suffix("").parts)


def definitions(tree: ast.Module):
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            yield node.name, node
            if isinstance(node, ast.ClassDef):
                for child in node.body:
                    if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        yield f"{node.name}.{child.name}", child


def read_sources():
    sources = {}
    missing = []
    for scope in SCOPES:
        if not scope.exists():
            missing.append(str(scope))
            continue
        for path in sorted(scope.rglob("*.py")):
            if any(part in {".venv", ".git", "build", "dist", "__pycache__"} for part in path.parts):
                continue
            sources[path] = ast.parse(path.read_text(), filename=str(path))
    return sources, missing


def imports(path: Path, tree: ast.Module):
    """Return (target module, imported symbol, line) for resolved ve imports."""
    current = module_name(path)
    edges = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.level:
                if current is None:
                    continue
                package = current.split(".")[:-1]
                base = package[:len(package) - node.level + 1]
                mod = ".".join(base + ([node.module] if node.module else []))
            else:
                mod = node.module or ""
            for alias in node.names:
                if mod.startswith("ve."):
                    edges.append((mod, alias.name, node.lineno))
                elif mod == "ve" and alias.name in TARGETS:
                    edges.append((f"ve.{alias.name}", "*module*", node.lineno))
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith("ve."):
                    edges.append((alias.name, "*module*", node.lineno))
    return edges


def classify(module: str, symbol: str, referenced: bool):
    head = symbol.split(".")[0]
    if symbol in AUTHORITY.get(module, ()) or head in AUTHORITY.get(module, ()):
        return "A"
    if (module, symbol) == ("norms", "NormDocument"):
        return "S"
    if symbol in SURFACE.get(module, ()) or head in SURFACE.get(module, ()):
        return "S"
    if symbol in UNTRUSTED.get(module, ()) or head in UNTRUSTED.get(module, ()):
        return "U"
    if module in {"closure", "order", "entailment", "search"}:
        return "U"  # shared search / replay rule code: inspect before deletion
    if module in {"parser", "printer", "argument"}:
        return "S"  # parser/surface and graph diagnostics survive
    if referenced:
        return "U"  # unknown retained consumer: conservative
    return "D"


def generate():
    sources, missing = read_sources()
    refs = defaultdict(list)
    local_uses = defaultdict(set)
    graph = []
    for path, tree in sources.items():
        current = module_name(path)
        if current and current.split(".")[1] in TARGETS:
            for node in ast.walk(tree):
                if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                    local_uses[current].add(node.id)
                elif isinstance(node, ast.Attribute) and isinstance(node.ctx, ast.Load):
                    local_uses[current].add(node.attr)
        for mod, symbol, line in imports(path, tree):
            if mod.split(".")[1] in TARGETS:
                label = str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)
                graph.append((label, mod, symbol, line))
                refs[(mod, symbol)].append(f"{label}:{line}")
    lines = ["# Stage 0 semantic inventory", "", "Generated by `python3 tools/semantic_inventory.py --write` from Python ASTs.",
             "Classes: **A** authority adapter; **U** untrusted search/surface helper; **S** surface/container/display; **D** no retained consumer identified.",
             "A classifies a verdict-producing body, including its helper methods; it does not classify the exported name for deletion. Method and private-helper classifications require review before stage 5.",
             "", "## Coverage", "", f"Parsed {len(sources)} Python files; found {len(graph)} import edges into section 1.1 modules."]
    if missing:
        lines += ["Missing optional external trees: " + ", ".join(missing) + "."]
    lines += ["", "## Symbols", "", "Every A row uses the signature-preserving `ve/backends/dispatch.py` adapter from plan §3 stage 2a; the interface column names its backend target.",
              "", "| Module | Symbol | Line | Class | Stage 2 adapter → interface for A | Direct import consumers |", "|---|---|---:|:---:|---|---|"]
    for module in sorted(TARGETS):
        path = ROOT / "ve" / f"{module}.py"
        for symbol, node in definitions(sources[path]):
            direct = refs.get((f"ve.{module}", symbol.split(".")[0]), [])
            cls = classify(module, symbol, bool(direct) or symbol.split(".")[-1] in local_uses[f"ve.{module}"])
            consumer = ", ".join(f"`{r}`" for r in direct[:6])
            if len(direct) > 6:
                consumer += f" (+{len(direct)-6})"
            iface = f"`ve/backends/dispatch.py` → {INTERFACES[module]}" if cls == "A" else "—"
            lines.append(f"| `ve/{module}.py` | `{symbol}` | {node.lineno} | {cls} | {iface} | {consumer or '—'} |")
    lines += ["", "## Other `ve/` functions", "",
              "Section 1.2 combination functions are C; single-verdict relabelling is L; other retained surface, authoring, diagnostic and transport functions are S. This covers functions outside the section 1.1 deletion list.",
              "", "| Module | Function | Line | Class |", "|---|---|---:|:---:|"]
    for path in sorted((ROOT / "ve").rglob("*.py")):
        module = module_name(path)
        if module is None or module.split(".")[1] in TARGETS:
            continue
        for symbol, node in definitions(sources[path]):
            cls = ("C" if (module, symbol) in {("ve.readings", "check_readings"),
                                               ("ve.equivalence", "compare"),
                                               ("ve.document", "check_document")}
                   else "L" if module in {"ve.check", "ve.vacuity", "ve.identity", "ve.wire"}
                   else "S")
            lines.append(f"| `{path.relative_to(ROOT)}` | `{symbol}` | {node.lineno} | {cls} |")
    lines += ["", "## Combination roles inside section 1.1 modules", "",
              "These roles are additional to A/U/S/D: the class-A adapter must ask Lean for the combined verdict, while diagnostic-only code stays a trusted display rule.",
              "", "| Function | Role | Reason |", "|---|:---:|---|",
              "| `argument.check_argument` | C | Root reachability, ordered leaves, status and composition combine edge checks; Lean `graph` owns consequence. |",
              "| `argument._check_edge` | L | Displays each checked certificate or countermodel with diagnostic attempts. |",
              "| `admission.admit_document` | C | Document graph admission combines labelled leaves, citations and certificates; Lean `admission` owns verdict. |",
              "| `bundle.check_bundle` | C | Transitive citation and certificate replay combine into one bundle verdict; Lean `bundle` owns verdict. |",
              "| `norms.check_conflict` | C | Combines generated targets and checked witnesses/certificates; Lean `norms-conflict` owns verdict. |"]
    lines += ["", "## Plan revision findings", "",
              "- `FiniteModel.from_dict` builds defined-predicate tables by calling `_Evaluator.formula` with open bodies and explicit bindings. `norms.py` also calls `_Evaluator` for selected rules, conflict witnesses and overlap checks. The stage 2 adapter contract must provide an open-formula/bindings evaluation path before `_Evaluator` can become D; closed-document `evaluate` alone cannot replace these consumers.",
              "- `norm_strict.py` imports `_Parser` directly. Keep this untrusted parser for norm-unit surface reading even after Lean owns public parse acceptance; only its verdict authority moves.",
              "- Searchers in `entailment.py`, `closure.py` and `order.py` share rule helpers with replay. Keep them U until the generator path has a replacement, then reclassify individually.",
              "- The AST graph records explicit imports, including `from` aliases and relative imports. It cannot prove that a dynamically imported or reflected name is unused; D is a candidate for Stage 5 review, not a deletion instruction by itself."]
    lines += ["", "## AST import graph", "", "One row per import statement binding. `*module*` and `*` need a later use-site review; AST imports cannot detect reflection or dynamic imports.",
              "", "| Consumer | Provider | Imported symbol | Line |", "|---|---|---|---:|"]
    lines += [f"| `{p}` | `{m}` | `{s}` | {n} |" for p, m, s, n in sorted(graph)]
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    output = generate()
    target = ROOT / "docs/spec/semantics-inventory.md"
    if args.write:
        target.write_text(output)
    else:
        assert target.read_text() == output, f"stale {target}; run --write"


if __name__ == "__main__":
    main()
