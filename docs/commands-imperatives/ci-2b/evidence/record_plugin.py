"""A pytest plugin (`-p record_plugin`, this directory on `PYTHONPATH`) that appends every command wording a test
reads, through Lean's `read_command` or the frozen pre-switch parser, to `$CI2B_AB_OUT` as one JSON line:
the environment, the wording, the query records (Lean's side) or the selected query id (the frozen side)."""
import json
import os

from tests.frozen_speech import speech_english as frozen
from ve import speech_english
from ve.backends import english_lean

OUT = os.environ["CI2B_AB_OUT"]
QUESTION = ("Which ", "Does it follow from these premises that ", "Is ", "Must ", "Can ")


def _write(row):
    with open(OUT, "a") as handle:
        handle.write(json.dumps(row, sort_keys=True) + "\n")


def pytest_configure(config):
    real_read, real_frozen = english_lean.read_command, frozen.parse_speech

    def read_command(env, wording, words, options, *, unit, queries):
        _write({"side": "lean", "environment": env.to_dict(), "wording": wording, "queries": queries})
        return real_read(env, wording, words, options, unit=unit, queries=queries)

    def parse_speech(env, source, scope, *, query=None, **kwargs):
        if type(source) is str and not source.strip().startswith(QUESTION):
            _write({"side": "frozen", "environment": env.to_dict(), "wording": source, "query": query})
        return real_frozen(env, source, scope, query=query, **kwargs)
    english_lean.read_command = speech_english.read_command = read_command
    frozen.parse_speech = parse_speech
