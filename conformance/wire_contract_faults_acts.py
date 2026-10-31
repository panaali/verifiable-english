"""The fault catalogue of `acts@0` (ap-1bf), at and around each limit of `VE.Acts.Lexical`.

Every fault is applied to the base source, the unit's example `base.json`, and expects its member of 1.1 at
`/environment`. The limits are Lean's, found from its environment decoder (`limits`), never written here: one byte or
one phrase over each limit is a fault, and the sources at each limit (`at_limits`, which `limit.json` is, and
`at_count`) are accepted. Around the limits: a count over its limit with a phrase over its own, an act over its
limit that is not an act phrase, and an act over its limit after a refused fixed phrase, each the one Lean names.
"""

from copy import deepcopy
from functools import cache
import json
from pathlib import Path

from conformance.wire_contract_faults import Fault
from ve.environment import Environment
from ve.errors import VEError

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "ve/wire_contract/examples/acts@0"
UNIT = "acts@0"
UNREACHED = {}


def _accepts(edit):
    """Whether Lean's environment decoder accepts `base()`'s environment after `edit`; a refusal other than a
    `ResourceLimit` is a broken family and raises."""
    raw, norms = base()
    edit({"environment": raw, "norms": norms})
    try:
        Environment(raw)
    except VEError as exc:
        if exc.code != "ResourceLimit":
            raise
        return False
    return True


def _largest(edit, size):
    """The largest `n` at least `size` whose `edit(n)` Lean accepts (it accepts `size`): doubling, then halving."""
    low, high = size, 2 * size
    while _accepts(edit(high)):
        low, high = high, 2 * high
    while high - low > 1:
        middle = (low + high) // 2
        low, high = (middle, high) if _accepts(edit(middle)) else (low, middle)
    return low


@cache
def limits():
    """The three limits of `VE.Acts.Lexical`, with Lean's decoder as the oracle (no value is written here): for
    each, the largest size of a family of sources that it accepts."""
    return {"maxActBytes": _largest(lambda n: lambda root: _act(root).update(act=act(n)), 16),
            "maxPhraseBytes": _largest(lambda n: lambda root: _fixed(root).append(phrase(n)), 16),
            "maxPhrases": _largest(lambda n: lambda root: _fixed(root).extend(phrases(n - 1)), 2)}


def phrase(size):
    """A fixed phrase of two words, `size` bytes long."""
    return "zeta " + "a" * (size - 5)


def act(size):
    """An act phrase of one slot and two words, `size` bytes long."""
    return "{0} enjoy " + "b" * (size - 10)


def phrases(count):
    """`count` fixed phrases of two words each, no word shared, so none overlaps another."""
    tag = lambda i: chr(97 + i // 26) + chr(97 + i % 26)
    return [f"p{tag(i)} q{tag(i)}" for i in range(count)]


def base():
    value = json.loads((EXAMPLES / "base.json").read_text())
    return value["environment"], value["norms"]


def _fixed(root):
    return root["environment"]["vocabulary"]["acts"]["fixed"]


def _act(root, predicate="paid"):
    return root["environment"]["vocabulary"]["predicates"][predicate]["regulated"]


def at_limits():
    """`base()` with a fixed phrase of `maxPhraseBytes` bytes and `protected`'s act of `maxActBytes`."""
    raw, norms = base()
    root = {"environment": raw, "norms": norms}
    _fixed(root).append(phrase(limits()["maxPhraseBytes"]))
    _act(root, "protected")["act"] = act(limits()["maxActBytes"])
    return raw, norms


def at_count():
    """`base()` with `maxPhrases` fixed phrases."""
    raw, norms = base()
    root = {"environment": raw, "norms": norms}
    _fixed(root).extend(phrases(limits()["maxPhrases"] - len(_fixed(root))))
    return raw, norms


def _faults():
    """(name, check, apply) of each fault."""
    n = limits()
    def count_over(root):
        _fixed(root).extend(phrases(n["maxPhrases"] + 1 - len(_fixed(root))))
    def count_and_bytes_over(root):
        count_over(root)
        _fixed(root).append(phrase(n["maxPhraseBytes"] + 1))
    def act_over(root):
        _act(root)["act"] = act(n["maxActBytes"] + 1)
    def act_over_after_phrase(root):
        act_over(root)
        _fixed(root).append("seek and")
    return [("phrases-over", "1.1a", count_over),
            ("phrases-over-with-long-phrase", "1.1a", count_and_bytes_over),
            ("phrase-bytes-over", "1.1b", lambda root: _fixed(root).append(phrase(n["maxPhraseBytes"] + 1))),
            ("act-bytes-over", "1.1c", act_over),
            ("act-bytes-over-not-an-act", "1.1d",
             lambda root: _act(root).update(act="enjoy " + "b" * n["maxActBytes"])),
            ("act-bytes-over-after-phrase", "1.1d", act_over_after_phrase),
            ("joined-act", "1.1d", lambda root: _act(root).update(act="{0} seek and enjoy asylum"))]


def catalogue():
    return [Fault(name, check, "/environment", apply, frozenset({name}), base=lambda: deepcopy(base()))
            for name, check, apply in _faults()]
