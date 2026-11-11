"""The fault catalogue of `purposes@0` (sa-wire-purposes0): one fault per refused example.

Each file of `ve/wire_contract/examples/purposes@0/refused/` is a block with the member of 7.1 (or 7.2's row 2) it
breaks, the arguments the member's text quotes and that text, an instance of spec 7's text. A fault replaces the
case's block with the file's. The link limit is Lean's (`limit`), never written here.
"""

from copy import deepcopy
from functools import cache
import json
from pathlib import Path

from conformance.wire_contract_faults import Fault

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "ve/wire_contract/examples/purposes@0"
UNREACHED = {}


@cache
def refused():
    """Each refused example by name: `check`, `args`, `text` and the block `purposes`."""
    return {path.stem: json.loads(path.read_text()) for path in sorted((EXAMPLES / "refused").glob("*.json"))}


def link(i):
    """The `i`-th link of a block at and over the limit: a `because` link with empty sides."""
    return {"id": f"l{i}", "relation": "because", "polarity": "affirmed", "reason": [], "target": [], "marker": f"m{i}"}


@cache
def limit():
    """The link limit, as Lean's record of a block far over it quotes it."""
    from conformance.purposes_contract import lean_record
    return int(lean_record({"links": [link(i) for i in range(1 << 12)]})["args"]["limit"])


def catalogue():
    return [Fault(name, value["check"], "/purposes",
                  lambda root, block=value["purposes"]: root.update(purposes=deepcopy(block)),
                  frozenset({name}), args=value["args"]) for name, value in refused().items()]
