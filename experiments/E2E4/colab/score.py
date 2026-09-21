"""Score E2/E4 Colab outputs with their native preregistered contrasts."""
from pathlib import Path
import sys
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from experiments.colab_scoring import main
if __name__ == "__main__":
    main(("E2", "E4"))
