"""Run from the repository root; see README.md for gates and dollar ceilings."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from experiments.p1 import main

if __name__ == "__main__":
    raise SystemExit(main())
