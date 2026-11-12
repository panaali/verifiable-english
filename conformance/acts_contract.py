"""Python hook and adapter of the `acts@0` wire table, in shadow (ap-1bf; act-phrases-PLAN.md 2.8, edit 2 of
plan synthesis round 2): it reports and refuses nothing.

`acts_environment` names the member of 1.1 from the text Lean's environment decoder wrote when it refused the
environment, as `ve.norms_contract.rule_typing` names 4.7's from the class: the limits and their texts are
`VE.Acts.Lexical`'s, and none is computed here. A refusal of the `acts` block's frames and adverbs (D-31; ap-1bfb)
is named the same way, with Lean as the oracle: its decoder refuses the frames and adverbs on their own with the same
text (`vocabulary_refusal`), and D-31's texts are never written here. The included phases of `norms@0` (ap-1bfb) run `norms@0`'s own hooks
and classifiers: each reads the environment through `Environment`, which Lean's environment mode decodes reading
`acts@0`. Diagnostic only: the legacy validator alone accepts or rejects.
"""

from ve.environment import Environment
from ve.errors import VEError
from ve.norms_contract import CLASSIFIERS, HOOKS, NORM_KINDS, decoded_environment, in_domain as norms_domain, source
from ve.wire_contract.registry import Registry

# The head and tail of `VE.Acts.Lexical`'s refusal at each of its three limits, by member; any other refusal
# of the decoder is 1.1d.
LIMIT_TEXTS = (("1.1a", "ResourceLimit: more than ", " fixed phrases"),
               ("1.1b", "ResourceLimit: fixed phrase '", " bytes"),
               ("1.1c", "ResourceLimit: act phrase for ", " bytes"))


def in_domain(environment, norms):
    """`acts@0` listed in `/environment/profiles`, and the source without it in `norms@0`'s domain (so neither
    `norm-defaults@0` nor a statement layer is listed), as `Hooks.Acts.inDomain` decides it."""
    listed = environment.get("profiles") if type(environment) is dict else None
    if type(listed) is not list or "acts@0" not in listed:
        return False
    return norms_domain({**environment, "profiles": [p for p in listed if p != "acts@0"]}, norms, defaults=False)


def acts_source(case):
    """The adapter: the norms route's case kinds and `admission`, in this unit's domain."""
    return source(case, kinds=NORM_KINDS.__contains__, defaults=False, inside=in_domain)


def _refusal(environment, decode=Environment):
    """The text Lean's environment decoder refuses `environment` with, `None` when it accepts it."""
    try:
        decode(environment)
    except VEError as exc:
        return str(exc)
    return None


def vocabulary_refusal(environment, text):
    """Whether `text` is the refusal of the `acts` block's frames and adverbs, as `Hooks.Acts.framesRefusal` decides
    it: the environment with the `acts` block alone in its vocabulary (`Hooks.Acts.alone`) is refused with `text`,
    and the same without the block's `frames` and `adverbs` is accepted, so no check before them refuses the
    environment. The block is kept whole otherwise: a refusal of its `fixed` comes before the frames (ap-1bfb
    review F1)."""
    vocabulary = environment.get("vocabulary") if type(environment) is dict else None
    block = vocabulary.get("acts") if type(vocabulary) is dict else None
    if type(block) is not dict:
        return False
    def alone(frames):
        acts = block if frames else {k: v for k, v in block.items() if k not in ("frames", "adverbs")}
        return {**environment, "vocabulary": {"sorts": {}, "predicates": {}, "constants": {}, "acts": acts}}
    return _refusal(alone(True)) == text and _refusal(alone(False)) is None


def acts_environment(root, items):
    """1.1: the environment decoder, reading `acts@0`, accepts the environment; a refusal at one of Lean's
    limits, or of the frames and adverbs (1.1e at their limit, 1.1f otherwise), names its member."""
    text = _refusal(root, decoded_environment)
    if text is None:
        return None
    if vocabulary_refusal(root["environment"], text):
        return ("1.1e" if text.startswith("ResourceLimit:") else "1.1f"), {"message": text}
    member = next((m for m, head, tail in LIMIT_TEXTS if text.startswith(head) and text.endswith(tail)), "1.1d")
    return member, {"message": text}


REGISTRY = Registry().register(hooks=HOOKS, classifiers={**CLASSIFIERS, "acts_environment": acts_environment},
                               adapters={"acts_source": acts_source})
