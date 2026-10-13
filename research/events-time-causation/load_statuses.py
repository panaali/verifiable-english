"""Load a document (no check) and print each unit's status and the coverage bytes by status.

Usage: python3 load_statuses.py <document.ve.md> [<unit id> ...]
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from ve.document import load_document  # noqa: E402

if __name__ == "__main__":
    doc = load_document(Path(sys.argv[1]))
    wanted = sys.argv[2:]
    rows = {u["id"]: u["status"] for u in doc["units"]}
    print(json.dumps({k: v for k, v in rows.items() if not wanted or k in wanted}))
