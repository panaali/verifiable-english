# sc-7-f11: no sentence end hides inside a word (sc-7 recheck FOLLOW-UP F11)

**Summary.** Built option (a), the allow-list form adv1056 asks for in this class. Inside a word, a character outside
`clause`'s allow-list (a sentence end, a mark, a blank-looking character) may be followed only by an allow-listed
character or a closer (`lean/VE/Scope/Authoring.lean`, `Pinned.allowed` and `Pinned.clause`). So "the
x.<U+1D159>The rules below are called the y." is refused, also with U+FFFC, with U+E000 or with any other following
character. No theorem statement changes, and this only narrows what `clause` accepts. Trust: K +0, S +0, V +8, all
signed by R16. No DRI signature is reserved.

Task: `manage-agents/prompts/task-sc-7-f11.txt`. Rulings: `reviews/dri-decisions-20261109-sc-7-ok.md` items 1-2 and
`reviews/dri-decisions-20261109-adv1056.md` item 2.

## Rows delivered

| Row | Delivered | Where |
|---|---|---|
| (a) the follower rule inside a word | yes | `Authoring.lean` `allowed` (the allow-list, moved out of `clause` unchanged) and `clause`'s new conjunct and docstring |
| Guards for U+1D159, U+FFFC, U+E000 joined: as a condition, as a list name, and in every slot | yes | `AuthoringExamples.lean:220` (`slotsJoined`: the nine slots of `slotsEnding`, with no space after `e`), alone, after a closer and before one |
| The class | yes | `:225`: each of F7's 13 sentence ends, joined by U+1D159, U+FFFC, U+E000, U+200B, U+2060, U+3164, U+2800 or U+0301, in every slot. `test_clause_accepts_exactly_its_documented_allow_list` adds "x." c "y" for every Unicode scalar value c: it is accepted exactly when c is an allow-listed character or a closer |
| Accepted examples that must stay accepted | yes | `:228` (a "." before an allowed character, before ")" and before "”", in every slot), `:229` (a round trip with "3.5" and "e.g"), `:230` ("x.y", "x.)y", "x.”’y", "Claude’s", "(x)", "“x”", "x—y", "x​y", "cafés") |
| Kept selected | yes | `test_clause_accepts_exactly_its_documented_allow_list` and `test_word_char_refuses_exactly_its_documented_characters` are unchanged in what they claim. `wordChar` is unchanged, so its documented set is too. The PROBE F8/F9/F10 guards and the U+1D159/U+E000/U+FFFC guards are unchanged. `test_review_f8_f9_f10_...` also checks the two joined probe forms and that the new guards stay |
| REPORT "D +140" corrected to "V +112" | yes | `docs/scope/sc-7/REPORT.md:60` |
| FOLLOW-UPS.md "213 KILLED" corrected to 229 | yes | `manage-agents/FOLLOW-UPS.md` "## sc-7" row (line 2194) |

**The "V +112" figure.** Measured with `uv run python tools/trust_map.py --files <out>` on main f3f40d51d. For
`VE/Scope/Authoring.lean` it gives S 37, D 140, D[V] 112, D[I] 28 and trusted 149. Trusted counts K + S + untied [V],
and 37 + 112 = 149. "D +140" also counted the 28 D[I] lines, which are not trusted.

**The "229 KILLED" figure.** It is the record `docs/scope/sc-7/trust-mutants.json` (head b11beab23): its counts are
KILLED 229, SURVIVOR 0, UNKNOWN 0, INVALID 64, ALLOWED 27. sc-7's REPORT says the same. 213 was the earlier F8/F9 run on
c494438df.

**Why (a) and not (b).** Option (b) would refuse, inside a word, an enumerated set: Cf ∪ Mn ∪ Me ∪
Default_Ignorable_Code_Point ∪ {U+2800} plus the probes. Every earlier round of this class (F7 to F10) found a
character that such a set had missed. Option (a) names no blank-looking set at all. Whatever the character after a
sentence end is, it has to be on the allow-list (letters, digits, eleven ASCII punctuation characters) or be a closer,
so the hidden-space characters are refused because they are not on the allow-list.

## What changed direction (accepted, now refused)

The new rule refuses one pattern inside a word: two characters next to each other where neither is on the allow-list
and the second is not a closer. Examples (`AuthoringExamples.lean:232`):

- "x.́y"
- "x..y"
- "x——y"
- "x​​y"
- "xαβy" (any non-Latin run of two or more characters inside a word)
- "x”́y"

The spec (docs/spec/scope.md) admits nothing of this pattern. A non-Latin word in a slot was already refused unless
its last character was on the allow-list. No other guard or test changed direction: every earlier `#guard` and all 10
tests of `tests/test_scope_authoring.py` pass unchanged in what they claim.

## Seeded bugs (Lean; `docs/scope/sc-7-f11/mutants.json`, 8 KILLED)

For each bug: plant it in `lean/VE/Scope/Authoring.lean`, run `lake build VE.Scope.AuthoringExamples`, then restore the
file. "Fails" lists the guards that failed.

| Bug | Definition | Fails |
|---|---|---|
| Drop the new condition (`true`) | `clause` | :220, :225, :232 (each probe guard) |
| Allow "!" inside a word (`a == '!'`) | `clause` | :225 (the "!" row of the class guard) |
| Allow "." inside a word | `clause` | :220, :225, :232 |
| No closer after a sentence end inside a word | `clause` | :228, :230, :242, :246 |
| No allow-listed character after one | `clause` | :89, :131, :132, :154, :228-:230, … |
| The follower may be any `wordChar` | `clause` | :220, :225, :232 |
| `allowed` without its ASCII punctuation | `allowed` | :229, :246, :255 |
| `allowed` admits U+01C3 | `allowed` | :250, :252 |

No Python, Rust or other product code changed: the Python edits are in `tests/test_scope_authoring.py` only. So Lean is
the only language that needs seeded bugs.

## Trust

`uv run python tools/trust_map.py --check` on the final HEAD, against f3f40d51dc6d: K +0, S +0, untied V +8, trusted +8,
all in `VE/Scope/Authoring.lean`. `Pinned.allowed` is new, at 4 lines with its blank line, classed D[V] in
`tools/trust-classes.json`. `Pinned.clause` grows by 4 lines. This was recorded with `--allow`, "SIGNED by standing
ruling R16 (DRI-RULINGS.md), sc-7-f11, 2026-11-10". The FOLLOW-UPS.md ties-pass row is under "## sc-7-f11". The test
helper `slotsJoined` is T.

## Size

About 150 hand-written lines, these docs included (`git diff --numstat` against the merge base).

## Pilot bytes

None expected. No route reads `clause` yet (sc-7b wires the IDE). Nothing is claimed before a pilot audit.

## Next item

None. sc-3b, sc-e1 and sc-e2 follow their own gates.
