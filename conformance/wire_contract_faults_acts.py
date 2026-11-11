"""The fault catalogue of `acts@0` (ap-1bf), at and around each limit of `VE.Acts.Lexical`.

Every fault is applied to the base source, the unit's example `base.json`, and expects its member of 1.1 at
`/environment`. The limits are Lean's, found from its environment decoder (`limits`), never written here: one byte or
one phrase over each limit is a fault, and the sources at each limit (`at_limits`, which `limit.json` is, and
`at_count`) are accepted. Around the limits: a count over its limit with a phrase over its own, an act over its
limit that is not an act phrase, and an act over its limit after a refused fixed phrase, each the one Lean names.

The frames and adverbs of the `acts` block (ap-1bfb, D-31): a frame count over 31a's limit, found from Lean's decoder
as the others are, is 1.1e, alone and with a refused head; each other condition, 31b to 31s, has a fault of its own,
1.1f, as has a frame that does not decode. Their texts are Lean's.

The rule phases (ap-1bfb): `norms@0`'s phases from `profiles` to `semantic`, included as `norms`, each with faults on
the base source's rules; the rule count's limit is `limits.json`'s.
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
            "maxPhrases": _largest(lambda n: lambda root: _fixed(root).extend(phrases(n - 1)), 2),
            "maxFrames": _largest(lambda n: lambda root: _block(root).update(frames=frames(n)), 2)}


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


def frame(head, markers=(), split=(), modifiers=()):
    return {"head": head, "markers": list(markers), "split": list(split), "modifiers": list(modifiers)}


def frames(count):
    """`count` frames of one head word each, no head shared, so none begins another."""
    return [frame("v" + chr(97 + i // 26) + chr(97 + i % 26)) for i in range(count)]


def base():
    value = json.loads((EXAMPLES / "base.json").read_text())
    return value["environment"], value["norms"]


def _fixed(root):
    return root["environment"]["vocabulary"]["acts"]["fixed"]


def _block(root):
    return root["environment"]["vocabulary"]["acts"]


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


def at_frames():
    """`base()` with `maxFrames` frames and an adverb."""
    raw, norms = base()
    _block({"environment": raw}).update(frames=frames(limits()["maxFrames"]), adverbs=["promptly"])
    return raw, norms


def _vocabulary(frames_=None, adverbs=None):
    """An edit that declares the `acts` block's frames and adverbs."""
    def apply(root):
        if frames_ is not None:
            _block(root)["frames"] = frames_
        if adverbs is not None:
            _block(root)["adverbs"] = adverbs
    return apply


# One fault per condition of D-31 after 31a, in its order: (row, frames, adverbs).
D31 = [
    ("31b", [frame("")], None),
    ("31c", [frame("Give")], None),
    ("31d", [frame("give to")], None),
    ("31e", [frame("give"), frame("give")], None),
    ("31f", [frame("give"), frame("give up")], None),
    ("31g", [frame("give", ["to", "to"])], None),
    ("31h", [frame("give", modifiers=["for", "for"])], None),
    ("31i", [frame("give", ["to"], split=["for"])], None),
    ("31j", [frame("give", modifiers=[""])], None),
    ("31k", [frame("give", ["to"], modifiers=["to"])], None),
    ("31l", [frame("give", ["in  front"])], None),
    ("31m", [frame("give", ["To"])], None),
    ("31n", [frame("give", ["and"])], None),
    ("31o", [frame("give", ["in", "in front"])], None),
    ("31p", None, ["promptly", "promptly"]),
    ("31q", None, ["Promptly"]),
    ("31r", [frame("give", ["to"])], ["give"]),
    ("31s", [frame("give", ["up"]), frame("up")], None),
]


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
    def frames_over(root):
        _block(root)["frames"] = frames(n["maxFrames"] + 1)
    def frames_over_with_bad_head(root):
        frames_over(root)
        _block(root)["frames"][0]["head"] = "Give"
    return [("frames-over", "1.1e", frames_over),
            ("frames-over-with-bad-head", "1.1e", frames_over_with_bad_head),
            *((f"frames-{row}", "1.1f", _vocabulary(fs, adverbs)) for row, fs, adverbs in D31),
            ("frame-fields", "1.1f", _vocabulary([{"head": "give", "markers": []}])),
            ("frames-not-an-array", "1.1f", _vocabulary(7)),
            ("phrases-over", "1.1a", count_over),
            ("phrases-over-with-long-phrase", "1.1a", count_and_bytes_over),
            ("phrase-bytes-over", "1.1b", lambda root: _fixed(root).append(phrase(n["maxPhraseBytes"] + 1))),
            ("act-bytes-over", "1.1c", act_over),
            ("act-bytes-over-not-an-act", "1.1d",
             lambda root: _act(root).update(act="enjoy " + "b" * n["maxActBytes"])),
            ("act-bytes-over-after-phrase", "1.1d", act_over_after_phrase),
            ("joined-act", "1.1d", lambda root: _act(root).update(act="{0} seek and enjoy asylum"))]


def _rule(name, predicate="protected", guard=("unary", "c", ("var", 0)), over=()):
    return {"norm": {"name": name, "predicate": predicate, "sign": True, "guard": json.loads(json.dumps(guard)),
                     "unless": [], "over": list(over)}}


def _norm(i, **fields):
    return lambda root: root["norms"][i]["norm"].update(fields)


def _rule_faults():
    """(name, check, path, apply, args) of each fault of the included rule phases; `args` is `None` where the
    check is inherited (its text is each language's legacy text)."""
    rules = json.loads((ROOT / "ve/wire_contract/limits.json").read_text())["MAX_RULES"]
    return [
        ("rules-limit", "norms/2.2", "/norms",
         lambda root: root["norms"].extend(_rule(f"r{i}") for i in range(1, rules + 1)), {}),
        ("unit-field", "norms/3.1", "/norms/0", lambda root: root["norms"][0].update(extra=1), {}),
        ("guard-shape", "norms/3.8b", "/norms/0/norm/guard", _norm(0, guard=5), None),
        ("name-repeat", "norms/4.2", "/norms/1/norm/name", lambda root: root["norms"].append(_rule("r0")),
         {"value": "r0"}),
        ("predicate-unregulated", "norms/4.4", "/norms/0/norm/predicate", _norm(0, predicate="c"), {"value": "c"}),
        ("guard-arity", "norms/4.7a", "/norms/0", _norm(0, guard=["binary", "c", ["var", 0], ["var", 0]]), None),
        ("guard-predicate", "norms/4.7b", "/norms/0", _norm(0, guard=["unary", "d", ["var", 0]]), None),
        ("guard-on-a-plain-act", "norms/4.7b", "/norms/1",
         lambda root: root["norms"].extend([_rule("r1", "paid", ("unary", "paid", ("const", "k")))]), None),
        ("over-unknown", "norms/5.1", "/norms/0/norm/over/0", _norm(0, over=["zz"]), {"value": "zz"}),
        ("precedence-cycle", "norms/6.1", "/norms",
         lambda root: root.update(norms=[_rule("r0", over=["r1"]), _rule("r1", over=["r0"])]), {"detail": "r0, r1"}),
    ]


def catalogue():
    environment = [Fault(name, check, "/environment", apply, frozenset({name}), base=lambda: deepcopy(base()))
                   for name, check, apply in _faults()]
    return environment + [Fault(name, check, path, apply, frozenset({name}), base=lambda: deepcopy(base()), args=args)
                          for name, check, path, apply, args in _rule_faults()]
