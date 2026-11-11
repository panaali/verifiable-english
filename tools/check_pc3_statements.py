"""Compare PC-3's Lean declarations with the approved Lean blocks of docs/spec/profile-composition.md 1.2 to 1.6
(build checklist 17).

Every declaration of those blocks is compared with the one Lean declaration of that kind and name in the files PC-3
writes: a theorem up to its proof's `:=`, anything else in full, after whitespace normalization and with
comments dropped on both sides. A declaration a later batch builds (`LATER`) must not exist yet, so the list can only
shrink. `RouteFacts` is staged: PC-3 builds its two entries, and the acts, discourse and generic entries are PC-6b's,
PC-7b's and PC-4b's, so until they land its last clause is `| _ => False` in place of theirs (`STAGED`).
"""

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from check_readings_defaults_statements import declarations as scan  # noqa: E402

SPEC = ROOT / "docs/spec/profile-composition.md"
SOURCES = [ROOT / "lean/VE/Compose" / name for name in ("Dispatch.lean", "Stack.lean", "Contract.lean")]
KINDS = ("theorem", "def", "structure", "inductive")
LATER = {"ActsFaithful", "ActsPreserves", "StackRuns", "ReadingsFaithful", "readingsFaithful", "RewriterFacts",
         "VE.Discourse.caseManifest", "VE.Discourse.effectContent", "VE.Discourse.withEffectContent",
         "ResolvedEffect", "PairFacts", "stack_evidence", "stackRuns_all", "LayerFacts", "layer_evidence",
         "layer_admitted", "fullEnvX", "BaseAdmissibleXV", "DocumentExpansionXV", "EntailsXV", "acceptanceXV",
         "entailsXV_constraint", "countermodelXV"}
STAGED = {"RouteFacts": ('| ["acts@0", "scope@0"] =>', "| _ => False")}


def declarations(code: str) -> dict[tuple[str, str], list[str]]:
    """The shared scanner of the statement gates: a declaration runs to the next Lean command, so a blank line or a
    comment inside it never ends it (review sc-2d-f1 F2), and comments are left out on both sides."""
    return scan(code, statements_only=True, kinds=KINDS)


def approved() -> dict[tuple[str, str], list[str]]:
    section = SPEC.read_text().split("### 1.2 ", 1)[1].split("### 1.7 ", 1)[0]
    return declarations("\n".join(re.findall(r"```lean\n(.*?)```", section, re.S)))


def main(sources=SOURCES) -> int:
    lean: dict[tuple[str, str], list[str]] = {}
    for source in sources:
        for key, texts in declarations(Path(source).read_text()).items():
            lean.setdefault(key, []).extend(texts)
    errors, exact = [], 0
    for (kind, name), texts in sorted(approved().items()):
        found = lean.get((kind, name), [])
        if name in LATER:
            if found:
                errors.append(f"{name}: listed as a later batch's but built")
            continue
        text = texts[0]
        if name in STAGED:
            before, after = STAGED[name]
            text = text.split(before, 1)[0] + after
        if len(texts) != 1 or found != [text]:
            errors.append(f"{name}: {kind} differs\n  approved: {text}\n  Lean:     {found}")
        else:
            exact += 1
    print(f"PC-3: {exact} declarations equal the approved text ({', '.join(STAGED)} staged); "
          f"later batches: {len(LATER)}")
    print("\n".join(errors))
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
