"""Export E5 to an upload-only gpu/ directory with a separate local label sidecar."""
import argparse
from pathlib import Path
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from experiments.colab_common import ROOT, cells_arg, export_bundle, read_budget, trial_rows
from experiments.trial_analysis import read_jsonl
from experiments.E5.materials import render_cell


def export(*, split, difficulty, instruction, cells, out):
    prereg = ROOT / "experiments/E5/PREREG.md"
    budget = read_budget(prereg, split)
    source = prereg.parent / f"{split}.jsonl.gz"
    rows, labels = [], []
    for item in read_jsonl(source):
        if item["payload"]["_audit"]["difficulty"] != difficulty:
            continue
        visible = {k: v for k, v in item["payload"].items() if not k.startswith("_")}
        for cell in cells_arg(cells, "abcde"):
            prompt = render_cell(visible, cell, instruction)
            row, label = trial_rows(item, cell, instruction, prompt, budget, "E5")
            rows.append(row); labels.append(label)
    return export_bundle(out, rows, labels, prereg=prereg,
        sources=[source, prereg.parent / "split.json", prereg.parent / "materials.py"],
        split=split, experiment="E5", selection=f"{difficulty}-{instruction}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--split", choices=("dev", "scored"), required=True)
    parser.add_argument("--difficulty", choices=("easy", "medium", "hard"), default="medium")
    parser.add_argument("--instruction", choices=("neutral", "audit"), required=True)
    parser.add_argument("--cells", default="a,b,c,d,e")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    try:
        export(**vars(args))
    except (ValueError, FileExistsError) as exc:
        parser.exit(2, f"Export refused: {exc}\n")


if __name__ == "__main__":
    main()
