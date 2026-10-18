"""Whether a command names the git program: the one definition, for the run and for the source.

`tests/read_recorder.py` decides with it, at run time, whether a process a test run started may read history;
`tools/history_tests.py` decides with it, in the source, whether code starts git. Standard library only: the
recorder loads it into every pytest process before any test module.
"""
from __future__ import annotations

import os
import re

# What ends a word in a command line or a shell command: `cd x && git log`, `$(git rev-parse HEAD)`, a Python
# program's `['git', 'log']`.
_WORD_BREAKS = re.compile(r"[\s;&|()<>`$\"'=\[\],{}]+")


def words(text: str) -> list[str]:
    """The words of a command line or a shell command, split where a shell or a Python list would split them."""
    return [word for word in _WORD_BREAKS.split(text) if word]


def names_git(text) -> bool:
    """Whether a command line, one argument or a shell command names the git program: a word whose basename is
    `git` (`git`, `/usr/bin/git`, `cd x && git log`, `$(git rev-parse HEAD)`). An argument that only mentions
    git counts too, which is the safe side."""
    if isinstance(text, os.PathLike):
        text = os.fspath(text)
    if isinstance(text, bytes):
        text = os.fsdecode(text)
    return isinstance(text, str) and any(os.path.basename(word) == "git" for word in words(text))


def program_is_git(text: str) -> bool:
    """Whether a command's program, its first word, is git (`git`, `/usr/bin/git`, `git log`)."""
    first = text.split(maxsplit=1)
    return bool(first) and os.path.basename(first[0]) == "git"
