"""C5 and C6, the two small runs behind q1-3b's reports, saved so that each of their claims has a key to cite. C5: why
sentences of the `ordinary` stream have no fronting that reads. C6: which profile list `english.read` refuses, and how
the `soft-chain` part reads without the refused profile (a changed environment, so never one of C4's answers).

    uv run python docs/question-answering/q1-3b/samples.py
"""
from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import subprocess
import sys
import warnings

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from conformance import english_lean_e2_evidence as E  # noqa: E402
from conformance import question_reverse as R  # noqa: E402
from ve.english import EnglishVocabulary  # noqa: E402
from ve.environment import Environment  # noqa: E402

OUTPUT = Path(__file__).with_name("evidence") / "samples.json"
SOFT, DEFAULTS = "soft-norms@0", "norm-defaults@0"


def c5() -> dict:
    """`run_config_b` on texts 1,000 to 1,149 of the `ordinary` sealed stream: outcomes and the unreached first words."""
    R.TARGETS.extend(E.CONFIGS)
    _, texts, *_ = R.stream_of((0, 5000))
    name, env, options, words = R.TARGETS[0]
    run = R.run_config_b(name, env, words, options, texts[1000:1150], asks_f1=False, every=False)
    groups = {}
    for q in run["questions"]:
        if q["kind"] == "f2" and q["read"]:
            groups.setdefault(q["sentence"], []).append(q)
    unreached = [s for s, qs in groups.items() if not any(q["same"] for q in qs)]
    return {"stream": name, "sentences": len(groups), "reached": len(groups) - len(unreached),
            "unreached": len(unreached), "first_words": dict(Counter(s.split()[0] for s in unreached).most_common()),
            "outcomes": dict(Counter(q["outcome"]["status"] for qs in groups.values() for q in qs))}


def read(data: dict, profiles: list[str], texts: list[str]) -> dict:
    """Lean's outcomes for `texts` in `data` with `profiles`: a count per outcome, or the environment's refusal."""
    try:
        env = Environment({**data, "profiles": profiles})
        words = EnglishVocabulary(env, _defer_overlay_refusals=True)
    except Exception as exc:  # noqa: BLE001 - a refused environment is this sample's answer
        return {"profiles": profiles, "refused": str(exc)[:200]}
    reads = R.read_sentences(env, words, {}, texts)
    return {"profiles": profiles, "outcomes": dict(Counter(r["status"] for r in reads)),
            "errors": sorted({r["error"] for r in reads if "error" in r}),
            "read": [t for t, r in zip(texts, reads, strict=True) if r["status"] == "one"]}


def c6() -> dict:
    """`Claude is not human.` under each list of the two profiles, then all of `soft-chain` without `soft-norms@0`."""
    docs = {name.rsplit("/", 1)[-1]: text for name, _, text in R.norm_documents()}
    soft_only, _ = R.norm_units(docs["s1.ve.md"])
    defaults_only, _ = R.norm_units(docs["nd-s01p1.ve.md"])
    chain, units = R.norm_units(docs["soft-chain.ve.md"])
    asked = sorted({text for *_, text, reads in units if reads})
    plain = ["Claude is not human."]
    return {"soft_only": read(soft_only, soft_only["profiles"], plain),
            "defaults_only": read(defaults_only, defaults_only["profiles"], plain),
            "pair": read(chain, chain["profiles"], plain),
            "pair_on_defaults_part": read(defaults_only, sorted(defaults_only["profiles"] + [SOFT]), plain),
            "pair_on_soft_part": read(soft_only, sorted(soft_only["profiles"] + [DEFAULTS]), plain),
            "soft_chain_without_defaults": read(chain, [p for p in chain["profiles"] if p != DEFAULTS], plain),
            "soft_chain_without_soft": {
                "sentences": len(asked), "fences": sum(content == "fence" for _, content, *_ in units),
                **read(chain, [p for p in chain["profiles"] if p != SOFT], asked)}}


def main() -> int:
    E._setup()
    warnings.simplefilter("ignore")
    E.CONFIGS.extend(E.configurations())
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    OUTPUT.write_text(json.dumps({"commit": commit, "c5": c5(), "c6": c6()}, indent=1, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
