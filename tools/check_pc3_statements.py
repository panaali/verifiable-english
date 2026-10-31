"""Compare PC-3's Lean declarations with the approved Lean blocks of docs/spec/profile-composition.md 1.2 to 1.5
(build checklist 17).

Every declaration of those blocks is compared with the one Lean declaration of that kind and name in the files PC-3
writes: a theorem up to its proof's `:=`, anything else in full, after whitespace normalization and with line
comments dropped on both sides. A declaration a later batch builds (`LATER`) must not exist yet, so the list can only
shrink. `RouteFacts` is staged: PC-3 builds its two entries, and the acts, discourse and generic entries are PC-6b's,
PC-7b's and PC-4b's, so until they land its last clause is `| _ => False` in place of theirs (`STAGED`).
"""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "docs/spec/profile-composition.md"
SOURCES = [ROOT / "lean/VE/Compose" / name for name in ("Dispatch.lean", "Stack.lean", "Contract.lean")]
KINDS = ("theorem", "def", "structure", "inductive")
START = re.compile(rf"^({'|'.join(KINDS)}) ([\w'!?.]+)", re.M)
STOP = re.compile(r"^(?:\s*$|(?:theorem|def|structure|inductive|end|namespace|open|universe|/--|/-!|#|```))", re.M)
LATER = {"ActsFaithful", "ActsPreserves", "StackRuns", "ReadingsFaithful", "readingsFaithful", "RewriterFacts",
         "VE.Discourse.caseManifest", "VE.Discourse.effectContent", "VE.Discourse.withEffectContent",
         "ResolvedEffect", "PairFacts", "stack_evidence", "stackRuns_all", "LayerFacts", "layer_evidence",
         "layer_admitted"}
STAGED = {"RouteFacts": ('| ["acts@0", "scope@0"] =>', "| _ => False")}


def declarations(code: str) -> dict[tuple[str, str], list[str]]:
    code = re.sub(r"(?<![/-])--[^\n]*", "", code)
    out: dict[tuple[str, str], list[str]] = {}
    for start in START.finditer(code):
        stop = STOP.search(code, code.find("\n", start.end()) + 1)
        body = code[start.start():stop.start() if stop else len(code)]
        if start[1] == "theorem":
            body = body.split(":=", 1)[0]
        out.setdefault((start[1], start[2]), []).append(re.sub(r"\s+", " ", body).strip())
    return out


def approved() -> dict[tuple[str, str], list[str]]:
    section = SPEC.read_text().split("### 1.2 ", 1)[1].split("### 1.6 ", 1)[0]
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
