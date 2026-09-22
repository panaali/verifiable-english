"""Run from repository root; all generation commands default to $0 (blocked)."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from experiments.p5 import main
if __name__=='__main__':
    raise SystemExit(main())
