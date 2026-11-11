"""Compare the RD-1, RD-2a, RD-4a, RD-4b and RD-6a declarations with the approved text of docs/spec/readings-defaults.md 6.2,
6.3, 6.6 and 6.7.

Every declaration of the spec's 6.2 block is compared, not only the theorems (review B2): the structure, every
definition with its body (`AchievesU`, `fillDoc`, `fillNamesFree`, `normsShaped`, `WellFormedND`, ...), and every
theorem from `theorem <name>` to the proof's `:=`. The list is read from the spec block itself, so a declaration
added to the spec is compared without editing this file. Whitespace and comments are ignored; a declaration runs
to the next Lean command keyword at column 0 in code (`spans`), so a blank line or a comment of any kind inside it, a
doc comment at column 0 too, does not end it (review sc-2d-f1 F2, F3). A term or tactic line at column 0 that starts
the way a command does still ends it early, and the text after that line is not compared (`COMMANDS`; review
sc-2d-f1 F4). These cases are: a line that starts with `#` (an array literal `#[..]`), a line that starts with `@[`,
and a line that starts with a command keyword used as a term or tactic prefix: `open X in`, `set_option o v in` (Lean's
term and tactic forms ending in ` in`) and the term `unsafe e`. These are all the term and tactic parsers of Lean
v4.24.0's built-in syntax that start with a keyword in `COMMANDS`; a syntax a project declares could add more.
The Lean compiler checks elaboration, and lean/audit.py checks proof dependencies. A declaration that differs from the
approved text must be listed in PENDING with the reason, and is reported as pending the statement re-review; an
unlisted difference, a missing or repeated declaration, or a PENDING entry that no longer differs fails.

RD-2a's block (6.3) states some wire functions without a body (`ndText`, `admitND`, the replays: specified by their
docstrings and sections 3 to 5 of the spec); such a definition is compared up to its Lean body's `:=`. Its
declarations are found in the three files 6.1 places them in.

RD-4a is checked the same way against the `section Companions` of 6.6 (the wire part 6.1 places in
`Companions.lean`; the rest of 6.6 is RD-4b's).

RD-6a is checked the same way against 6.7 in `SupExtra.lean`. 6.7 also states RD-6b's declarations (LATER_6A); each
is compared once it is in the file and listed as not built before.

A declaration that a DRI ruling amended (AMENDED_6A) passes as exact, and is reported as amended, only when all of
these hold: the Lean text is the approved text with the ruled edit and nothing else; the refutations file states the
approved statement, binder for binder, as a proposition (`def <P> : Prop := ∀ <binders>, <conclusion>`, built from
the spec text here, so the refuted proposition cannot drift from the approved one); a theorem there concludes `¬ <P>`;
and lean/VE/Audit.lean audits that theorem. Lean checks that the proposition gives the built theorem (an `example`
in the refutations file applies it to the built binders).
"""

from dataclasses import dataclass
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "docs/spec/readings-defaults.md"
SOURCE = ROOT / "lean/VE/Readings/Unspecified.lean"
# The approved 6.2 block's declarations by kind; a change in the spec's count is a change to review.
EXPECTED = {"theorem": 10, "def": 20, "structure": 1}
# Declarations changed in the build, each awaiting the targeted statement re-review (PLAN-EXPAND2 rule 10). Empty:
# `attached_fillDoc`'s added `singlyAttached` hypothesis was approved by the DRI on 2026-10-07 and is in 6.2.
PENDING: dict[str, str] = {}
# RD-2a: spec 6.3, placed by 6.1 in the NormDefaults files (the UDoc lemmas) and `UnspecifiedWire.lean`.
SECTION_RD2A = ("### 6.3 RD-2a", "### 6.4")
SOURCES_RD2A = [ROOT / "lean/VE/NormDefaults/Wire.lean", ROOT / "lean/VE/NormDefaults/Report.lean",
                ROOT / "lean/VE/Readings/UnspecifiedWire.lean"]
EXPECTED_RD2A = {"theorem": 5, "def": 8, "structure": 3}
PENDING_RD2A: dict[str, str] = {}
# RD-3: spec 6.4 (the fold) and 6.5 (conditions and the English plan), placed by 6.1 in `Verdicts.lean`; the English
# plan and the wire are in `VerdictsWire.lean`, beside the kind that computes them.
SECTIONS_RD3 = (("### 6.4 RD-3", "### 6.5"), ("### 6.5 RD-3", "### 6.6"))
SOURCES_RD3 = [ROOT / "lean/VE/Readings/Verdicts.lean", ROOT / "lean/VE/Readings/VerdictsWire.lean"]
EXPECTED_RD3 = {"theorem": 11, "def": 18, "structure": 1}
PENDING_RD3: dict[str, str] = {}
# RD-4a: spec 6.6's `section Companions`, placed by 6.1 in `Companions.lean`.
SECTION_RD4A = ("### 6.6 RD-4a and RD-4b", "### 6.7")
SOURCE_RD4A = ROOT / "lean/VE/Readings/Companions.lean"
EXPECTED_RD4A = {"theorem": 4, "def": 6, "structure": 0}
PENDING_RD4A: dict[str, str] = {}
# RD-4b: the product statements after `end Companions` in the same approved block.
SOURCE_RD4B = ROOT / "lean/VE/Readings/Components.lean"
EXPECTED_RD4B = {"theorem": 6, "def": 8, "structure": 2}
PENDING_RD4B: dict[str, str] = {}
SOURCE_6A = ROOT / "lean/VE/Readings/SupExtra.lean"
# 6.7's declarations by kind, RD-6b's included.
EXPECTED_6A = {"theorem": 7, "def": 3, "structure": 0}
PENDING_6A: dict[str, str] = {}
# The one edit each RD-6a pending declaration makes to the approved text: (approved fragment, Lean fragment). Any other
# difference fails, so a pending declaration cannot drift further unnoticed.
EDITS_6A: dict[str, tuple[str, str]] = {}


@dataclass(frozen=True)
class Amendment:
    """A DRI ruling that accepts one edit to an approved declaration on condition that the approved form is refuted
    in Lean: the ruling, the edit (approved fragment, Lean fragment), and the proposition stating the approved form
    and the theorem refuting it, both in the refutations file."""
    ruling: str
    edit: tuple[str, str]
    proposition: str
    refutation: str


AMENDED_6A: dict[str, Amendment] = {
    "superpose_all_extra": Amendment(
        "DRI ruling 2026-10-07",
        ("(hq : Transfers.{u} D Q Q') (hcf :",
         "(hq : Transfers.{u} D Q Q') (hQw : VE.Compose.SlotWellFormed (correlate (sup D).1) Q) (hcf :"),
        "SuperposeAllExtraApproved", "superpose_all_extra_refuted"),
}
REFUTATIONS_6A = ROOT / "lean/VE/Readings/SupExtraExamples.lean"
REFUTATIONS_NAMESPACE_6A = "VE.Readings.SupExtraExamples"
sys.path.insert(0, str(ROOT / "tools"))
from lean_statements import inventory_path  # noqa: E402
AUDIT = inventory_path("lean/VE/Audit.lean")
# 6.7's RD-6b declarations, built by RD-6b in the same file.
LATER_6A = set()
RD6B_NAMES = {"fill_transfers", "nd_superpose_conflict_free", "nd_superpose_all"}
KINDS = ("theorem", "def", "structure")
# The Lean commands that end a declaration when one starts a line at column 0 in code (not in a comment or string):
# Lean ends a declaration's term only at the next command, so a blank line or a comment inside the term never ends
# it (review sc-2d-f1 F2). A comment of every kind, a doc comment `/-- -/` or `/-! -/` too, is not a command here:
# it is dropped, and it never ends a declaration, even at column 0 (review sc-2d-f1 F3: Lean reads a `/--` before
# a constructor `| c` or a structure field at column 0 as that constructor's or field's doc, inside the
# declaration). Lean itself ends a term at a `/--` (a declaration must follow) or a `/-!` (a module doc), so in
# built Lean the next line is a command; reading on past them makes the text longer, never shorter. A `|`
# constructor line or a structure field line at column 0 is not a command either. A column-0 line that is none of
# these is read as part of the declaration: an unknown command makes the text longer, so it differs from the
# approved one. A column-0 line in code that starts the way a command does is read as a command even when Lean reads
# it as part of the term or tactic block, so it ends the declaration early and the text after it is not compared
# (review sc-2d-f1 F4; C notes of the DRI rulings on F3 and F4: valid Lean that hides text this way is built on
# purpose). Every such case: a term line that starts with `#` (an array literal `#[..]`; `#check` is a command), a
# line that starts with `@[` (`@[simp]` is a command), and a command keyword used as a term or tactic prefix:
# `open X in ..` and `set_option o v in ..` (term and tactic forms) and the term `unsafe ..`. These are all of Lean
# v4.24.0's built-in term and tactic parsers that start with a keyword listed here; a syntax a project declares could
# add more. `binder_predicate` to `unif_hint` are the other declaration commands Lean's parser lists as able to
# follow a doc comment, so a doc comment no longer separating them changes nothing.
COMMANDS = ("theorem", "lemma", "def", "structure", "class", "inductive", "coinductive", "abbrev", "instance",
            "example", "axiom", "opaque", "mutual", "end", "namespace", "section", "open", "export", "universe",
            "variable", "private", "protected", "noncomputable", "partial", "unsafe", "nonrec", "attribute",
            "set_option", "local", "scoped", "macro", "macro_rules", "syntax", "elab", "elab_rules", "notation",
            "infix", "infixl", "infixr", "prefix", "postfix", "initialize", "builtin_initialize",
            "declare_syntax_cat", "import", "prelude", "omit", "include", "add_decl_doc", "run_cmd",
            r"deriving\s+instance", "binder_predicate", "simproc", "simproc_decl", "dsimproc", "dsimproc_decl",
            "builtin_simproc", "builtin_simproc_decl", "builtin_dsimproc", "builtin_dsimproc_decl",
            "grind_propagator", "builtin_grind_propagator", "declare_simp_like_tactic", "recommended_spelling",
            "register_error_explanation", "register_tactic_tag", "tactic_extension", "unif_hint")
COMMAND = re.compile(rf"@\[|#|(?:{'|'.join(COMMANDS)})(?![\w'!?.])")
NAME_CHAR = re.compile(r"[\w'!?.]")
CHAR = re.compile(r"'(?:\\(?:u\{[0-9a-fA-F]+\}|x[0-9a-fA-F]{2}|.)|[^\\'\n])'")
RAW = re.compile(r'r(#*)"')


def lex(text: str) -> tuple[str, list[int]]:
    """`text` as Lean's scanner sees it: (`code`, `commands`). `code` is `text` with every comment, a doc comment
    too, blanked to spaces (newlines and offsets kept); `commands` are the offsets of the lines that start a command
    at column 0 in code, outside every comment and string literal."""
    code, commands, i, n = list(text), [], 0, len(text)

    def blank(a: int, b: int) -> None:
        code[a:b] = [c if c == "\n" else " " for c in text[a:b]]

    while i < n:
        if (i == 0 or text[i - 1] == "\n") and COMMAND.match(text, i):
            commands.append(i)
        prior = text[i - 1] if i else " "
        if text.startswith("--", i):
            end = text.find("\n", i)
            end = n if end < 0 else end
            blank(i, end)
            i = end
        elif text.startswith("/-", i):
            depth, j = 1, i + 2
            while j < n and depth:
                if text.startswith("/-", j):
                    depth, j = depth + 1, j + 2
                elif text.startswith("-/", j):
                    depth, j = depth - 1, j + 2
                else:
                    j += 1
            blank(i, j)
            i = j
        elif text[i] == '"':
            j = i + 1
            while j < n and text[j] != '"':
                j += 2 if text[j] == "\\" else 1
            i = j + 1
        elif (raw := RAW.match(text, i)) and not NAME_CHAR.match(prior):
            end = text.find('"' + raw[1], raw.end())
            i = n if end < 0 else end + 1 + len(raw[1])
        elif (char := CHAR.match(text, i)) and not NAME_CHAR.match(prior):
            i = char.end()
        else:
            i += 1
    return "".join(code), commands


def spans(text: str, kinds: tuple[str, ...] = KINDS) -> list[tuple[str, str, int, int]]:
    """Every declaration of a kind in `kinds` that starts a line at column 0 in code: (kind, name, start, end), from
    its keyword to the next command (or the end of `text`), its trailing blank lines and comments left out. A
    declaration in a comment is not one; a blank line or a comment inside one does not end it."""
    code, commands = lex(text)
    start = re.compile(rf"({'|'.join(kinds)}) ([\w'!?.]+)")
    out = []
    for at, after in zip(commands, commands[1:] + [len(text)]):
        if head := start.match(code, at):
            out.append((head[1], head[2], at, at + len(code[at:after].rstrip())))
    return out


def span(text: str, kind: str, name: str) -> tuple[int, int]:
    """The offsets of the first declaration `kind name` of `text` (KeyError when there is none)."""
    for k, n, start, end in spans(text, (kind,)):
        if (k, n) == (kind, name):
            return start, end
    raise KeyError(f"{kind} {name}")


def normal(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


OPEN, CLOSE = "([{⟨⦃", ")]}⟩⦄"


def proof_cut(text: str) -> int:
    """Where a theorem's statement in `text` ends: its first `:=` outside every bracket, the one that starts the proof
    (len(text) when there is none). A `:=` inside the statement (`{ L with scope := s }`) is part of it (review sc-6
    F1); every statement gate cuts here."""
    depth = 0
    for i, char in enumerate(text):
        depth += (char in OPEN) - (char in CLOSE)
        if depth == 0 and text.startswith(":=", i):
            return i
    return len(text)


def declarations(text: str, statements_only: bool, kinds: tuple[str, ...] = KINDS) -> dict[tuple[str, str], list[str]]:
    """Every declaration of a kind in `kinds` at column 0 of `text` (`spans`): (kind, name) → its normalized texts,
    comments left out. A theorem is cut at its proof's `:=` when `statements_only`."""
    code, _ = lex(text)
    out: dict[tuple[str, str], list[str]] = {}
    for kind, name, start, end in spans(text, kinds):
        body = code[start:end]
        if statements_only and kind == "theorem":
            body = body[:proof_cut(body)]
        out.setdefault((kind, name), []).append(normal(body))
    return out


def block(start: str, stop: str) -> dict[tuple[str, str], list[str]]:
    section = SPEC.read_text().split(start, 1)[1].split(stop, 1)[0]
    return declarations(section.split("```lean", 1)[1].split("```", 1)[0], statements_only=True)


def approved() -> dict[tuple[str, str], list[str]]:
    return block("### 6.2 RD-1", "### 6.3")


def approved_rd2a() -> dict[tuple[str, str], list[str]]:
    return block(*SECTION_RD2A)


def approved_rd4a() -> dict[tuple[str, str], list[str]]:
    """The declarations between `section Companions` and `end Companions` of 6.6's block."""
    section = SPEC.read_text().split(SECTION_RD4A[0], 1)[1].split(SECTION_RD4A[1], 1)[0]
    code = section.split("```lean", 1)[1].split("```", 1)[0]
    return declarations(code.split("section Companions", 1)[1].split("end Companions", 1)[0], statements_only=True)


def approved_rd4b() -> dict[tuple[str, str], list[str]]:
    section = SPEC.read_text().split(SECTION_RD4A[0], 1)[1].split(SECTION_RD4A[1], 1)[0]
    code = section.split("```lean", 1)[1].split("```", 1)[0]
    return declarations(code.split("end Companions", 1)[1], statements_only=True)


def lean_of(sources) -> dict[tuple[str, str], list[str]]:
    """The Lean declarations of one source file or of several, merged (a name found twice is reported)."""
    out: dict[tuple[str, str], list[str]] = {}
    for source in [sources] if isinstance(sources, Path) else sources:
        for key, texts in declarations(Path(source).read_text(), statements_only=True).items():
            out.setdefault(key, []).extend(texts)
    return out


def approved_rd3() -> dict[tuple[str, str], list[str]]:
    """6.4 and 6.5 together: one batch, one comparison (a name stated in both would be reported twice)."""
    out: dict[tuple[str, str], list[str]] = {}
    for section in SECTIONS_RD3:
        for key, texts in block(*section).items():
            out.setdefault(key, []).extend(texts)
    return out


def approved_6a() -> dict[tuple[str, str], list[str]]:
    return block("### 6.7 RD-6a", "## 7.")


def signature(statement: str) -> tuple[str, str]:
    """A normalized `theorem <name> <binders> : <conclusion>` as (binders, conclusion): the binders are the bracketed
    groups after the name, read by bracket depth, so a `:` inside a binder does not end them."""
    rest = statement.split(" ", 2)[2]
    opens, closes = "({[⦃", ")}]⦄"
    i = 0
    while i < len(rest) and rest[i] in opens:
        depth = 0
        for j in range(i, len(rest)):
            depth += (rest[j] in opens) - (rest[j] in closes)
            if depth == 0:
                break
        else:
            raise ValueError(f"unbalanced binder in: {statement}")
        i = j + 1
        while i < len(rest) and rest[i] == " ":
            i += 1
    if not rest[i:].startswith(": "):
        raise ValueError(f"no conclusion after the binders of: {statement}")
    return rest[:i].strip(), rest[i + 2:].strip()


def refuted(name: str, approved_text: str, amendment: Amendment, refutations: Path, namespace: str,
            audit: Path) -> list[str]:
    """The errors of an amended declaration's refutation: the approved statement as a proposition, a theorem
    concluding its negation, and that theorem's audit entry."""
    decls = declarations(refutations.read_text(), statements_only=True)
    binders, conclusion = signature(approved_text)
    proposition = normal(f"def {amendment.proposition} : Prop := ∀ {binders}, {conclusion}")
    errors = []
    found = decls.get(("def", amendment.proposition), [])
    if found != [proposition]:
        errors.append(f"{name}: {amendment.proposition} is not the approved statement as one proposition\n"
                      f"  approved: {proposition}\n  Lean:     {found}")
    theorem = decls.get(("theorem", amendment.refutation), [])
    if len(theorem) != 1 or not re.search(rf" : ¬ ?{re.escape(amendment.proposition)}(\.\{{\w+\}})?$", theorem[0]):
        errors.append(f"{name}: no one theorem {amendment.refutation} concluding ¬ {amendment.proposition}")
    entry = f"#print axioms {namespace}.{amendment.refutation}"
    if entry not in audit.read_text().splitlines():
        errors.append(f"{name}: {amendment.refutation} is not audited in {audit.name}")
    return errors


def compare(batch: str, spec: dict, source, expected: dict, pending_ok: dict[str, str],
            later: set[str], edits: dict[str, tuple[str, str]] | None = None,
            amended: dict[str, Amendment] | None = None, refutations: Path | None = None,
            namespace: str = "") -> tuple[list[str], int]:
    """Print the batch's report; return its errors and its number of exact declarations. `source` is one Lean file
    or a list of them."""
    lean = lean_of(source)
    amended = amended or {}
    errors, pending, waiting, amends = [], [], [], []
    counts = {kind: sum(1 for k, _ in spec if k == kind) for kind in KINDS}
    if counts != expected:
        errors.append(f"expected {expected} approved {batch} declarations, found {counts}")
    names = {name for _, name in spec}
    for name in sorted((set(pending_ok) | later | set(amended)) - names):
        errors.append(f"{name}: listed as pending, amended or later but not an approved declaration")
    for name in sorted(set(pending_ok) & set(amended)):
        errors.append(f"{name}: listed as both pending and amended")
    for (kind, name), texts in sorted(spec.items()):
        if len(texts) != 1:
            errors.append(f"{name}: the spec block states it {len(texts)} times")
            continue
        found = lean.get((kind, name), [])
        if not found and name in later:
            waiting.append(name)
            continue
        if len(found) != 1:
            errors.append(f"{name}: expected one Lean {kind}, found {len(found)}")
            continue
        if kind == "def" and ":=" not in texts[0]:  # stated without a body: the signature is compared
            found = [found[0].split(" :=", 1)[0]]
        if name in amended:
            edited = texts[0].replace(amended[name].edit[0], amended[name].edit[1], 1)
            if edited == texts[0] or found[0] != edited:
                errors.append(f"{name}: is not the approved text with the edit of {amended[name].ruling}\n"
                              f"  approved: {texts[0]}\n  Lean:     {found[0]}")
                continue
            failures = refuted(name, texts[0], amended[name], refutations, namespace, AUDIT)
            errors += failures
            if not failures:
                amends.append(f"{name}: amended by {amended[name].ruling}, refuted original mechanised "
                              f"({amended[name].refutation})")
        elif found[0] == texts[0]:
            if name in pending_ok:
                errors.append(f"{name}: listed as pending but matches the approved text")
        elif name in pending_ok and name in (edits or {}) and \
                found[0] != texts[0].replace(edits[name][0], edits[name][1], 1):
            errors.append(f"{name}: differs from the approved text by more than its pending edit\n"
                          f"  approved: {texts[0]}\n  Lean:     {found[0]}")
        elif name in pending_ok:
            pending.append(f"{name}: PENDING re-review: {pending_ok[name]}\n  approved: {texts[0]}\n  Lean:     {found[0]}")
        else:
            errors.append(f"{name}: {kind} differs\n  approved: {texts[0]}\n  Lean:     {found[0]}")
    theorems = sum(1 for k, name in spec if k == "theorem" and name not in waiting)
    print(f"checked {len(spec) - len(waiting)} approved {batch} declarations ({theorems} theorems)")
    for line in amends + pending:
        print(line)
    if waiting:
        print(f"not built yet (a later batch): {', '.join(sorted(waiting))}")
    exact = len(spec) - len(pending) - len(waiting)
    if not errors:
        print(f"{batch} PASS: {exact} exact after whitespace normalization ({len(amends)} amended by a DRI ruling, "
              f"its original refuted in Lean); {len(pending)} pending the statement re-review")
    return errors, exact


def main() -> int:
    errors, _ = compare("RD-1", approved(), SOURCE, EXPECTED, PENDING, set())
    errors_6a, _ = compare("RD-6a", approved_6a(), SOURCE_6A, EXPECTED_6A, PENDING_6A, LATER_6A, EDITS_6A,
                           AMENDED_6A, REFUTATIONS_6A, REFUTATIONS_NAMESPACE_6A)
    errors += errors_6a
    if errors:
        print("\n".join(errors))
        return 1
    return 0


def main_rd6b() -> int:
    spec = {key: value for key, value in approved_6a().items() if key[1] in RD6B_NAMES}
    errors, _ = compare("RD-6b", spec, SOURCE_6A, {"theorem": 3, "def": 0, "structure": 0}, {}, set())
    if errors:
        print("\n".join(errors))
        return 1
    return 0


def main_rd2a() -> int:
    errors, _ = compare("RD-2a", approved_rd2a(), SOURCES_RD2A, EXPECTED_RD2A, PENDING_RD2A, set())
    if errors:
        print("\n".join(errors))
        return 1
    return 0


def main_rd3() -> int:
    errors, _ = compare("RD-3", approved_rd3(), SOURCES_RD3, EXPECTED_RD3, PENDING_RD3, set())
    if errors:
        print("\n".join(errors))
        return 1
    return 0


def main_rd4a() -> int:
    errors, _ = compare("RD-4a", approved_rd4a(), SOURCE_RD4A, EXPECTED_RD4A, PENDING_RD4A, set())
    if errors:
        print("\n".join(errors))
        return 1
    return 0


def main_rd4b() -> int:
    errors, _ = compare("RD-4b", approved_rd4b(), SOURCE_RD4B, EXPECTED_RD4B, PENDING_RD4B, set())
    if errors:
        print("\n".join(errors))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(max(main(), main_rd2a(), main_rd3(), main_rd4a(), main_rd4b(), main_rd6b()))
