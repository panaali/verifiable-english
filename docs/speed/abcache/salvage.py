"""Finish a cached `record` whose child recording completed: run `record --cache` with the child's finished output
standing in for the child, so the segments are checked and stored as the run would have stored them (REPORT.md
section 2: the first cold run recorded every corpus, then stopped while splitting the child's output at U+2028).

    uv run python docs/speed/abcache/salvage.py CHILD_OUTPUT ROOT OUT CACHE
"""
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import sys
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools import lean_first_diff as diff  # noqa: E402


def main() -> int:
    finished, root, out, cache = sys.argv[1:5]

    def child(root, part, corpora, authorities, workers, scratch=None):
        assert (list(corpora), list(authorities)) == (list(diff.CORPORA), list(diff.AUTHORITIES))
        shutil.copyfile(finished, part)
        return 0
    args = argparse.Namespace(root=root, out=out, corpus=list(diff.CORPORA), authority=list(diff.AUTHORITIES),
                              workers=1, cache=cache)
    with patch.object(diff, "run_child", child):
        return diff.record(args)


if __name__ == "__main__":
    raise SystemExit(main())
