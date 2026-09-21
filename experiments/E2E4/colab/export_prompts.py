"""Export native E2 or E4 harness conditions; these experiments have no E5 style factor."""
import argparse
from pathlib import Path
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from experiments.colab_common import ROOT, cells_arg, export_bundle, read_budget, trial_rows
from experiments.E2E4.materials import E2_CELLS, E4_CELLS, load_frozen, render_cell


def export(*, experiment, split, cells, out):
    base = ROOT / "experiments/E2E4"
    prereg = base / experiment / "PREREG.md"
    budget = read_budget(prereg, split)
    selected = cells_arg(cells, E2_CELLS if experiment == "E2" else E4_CELLS)
    rows, labels = [], []
    for item in load_frozen(split, experiment):
        visible = {k: v for k, v in item["payload"].items() if not k.startswith("_")}
        for cell in selected:
            row, label = trial_rows(item, cell, "harness", render_cell(visible, cell), budget, experiment)
            rows.append(row); labels.append(label)
    sources = [base / f"{experiment.lower()}-{split}.jsonl.gz", base / "splits.json",
               base / "materials.py", base / f"{experiment.lower()}.py", base / "common.py", base / "fol.py"]
    if experiment == "E2":
        sources += sorted((base / "certificates").glob("*.jsonl.gz"))
    return export_bundle(out, rows, labels, prereg=prereg, sources=sources,
                         split=split, experiment=experiment, selection="native")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--experiment", choices=("E2", "E4"), required=True)
    parser.add_argument("--split", choices=("dev", "scored"), required=True)
    parser.add_argument("--cells", help="Comma-separated native cell names; default is all three")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    try:
        export(**vars(args))
    except (ValueError, FileExistsError) as exc:
        parser.exit(2, f"Export refused: {exc}\n")


if __name__ == "__main__":
    main()
