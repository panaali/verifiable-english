"""ap-4bb statement gate: ap-4b's declarations plus `sourceCheck_complete` equal spec 7's text, whitespace normalised.

    python3 docs/act-phrases/ap-4bb/check_statements.py

Runs ap-4b's checker (docs/act-phrases/ap-4b/check_statements.py) with `sourceCheck_complete` read from
lean/VE/Acts/SourcesProofs.lean. Exit 1 on any difference or a declaration missing on either side.
"""
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location("ap4b", Path(__file__).resolve().parents[1] / "ap-4b/check_statements.py")
ap4b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ap4b)
ap4b.DECLS.append(("theorem", "sourceCheck_complete", False, "lean/VE/Acts/SourcesProofs.lean"))

if __name__ == "__main__":
    ap4b.main()
