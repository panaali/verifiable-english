# sc-7-f11: no sentence end hides inside a word (sc-7 recheck FOLLOW-UP F11)

**Status: review fixes done (F1 ties-pass row, F2 non-empty run); awaiting the chain gate. Lean HEAD dd9e73266.** Inside a word, a character outside
`clause`'s allow-list may now be followed only by a `follower`, so "the x.<U+1D159>The …" (also U+FFFC, U+E000) is
refused. The DRI's decision 2026-11-10 adds: a Markdown character reference ("&", a non-empty run, ";") is refused too.
Trust: V +22, R16 (ties-pass row FOLLOW-UPS.md:2518). No DRI signature is reserved.

FOLLOW-UP: sc-7-f12 refuse inline HTML inside a scope slot word

Task: `manage-agents/prompts/task-sc-7-f11.txt`. Rulings: `reviews/dri-decisions-20261109-sc-7-ok.md` items 1-2;
`reviews/dri-decisions-20261109-adv1056.md` item 2; `reviews/dri-decisions-20261110-sc-7-f11.md` items 1-2 (asked
by this item, msg.sh 18:17Z).

## Rows delivered

| Row (task) | Delivered | Where (guards are in `lean/VE/Scope/AuthoringExamples.lean`) |
|---|---|---|
| (a) inside a word, a sentence end is followed only by an allow-listed character or a closer | yes, widened | `Authoring.lean`: `allowed` (the allow-list, moved out of `clause` unchanged), `follower`, and `clause`'s new conjunct. The follower set is the allow-list, the closers, ASCII graphic U+0021-U+007E, and U+2010-U+2027. The last two were added after self-review A1 so that "(a)", "—(b)—", "wait...," and "user’(s)" stay accepted. Each is drawn as a mark, never as a space |
| #guards for U+1D159, U+FFFC and U+E000 joined, as a condition, as a list name and in every slot | yes | :220. `slotsJoined` (:212) covers `slotsEnding`'s nine slots with no space after `e`. The character is placed alone, after a closer and before one |
| The class | yes | :225 joins each of F7's 13 sentence ends with U+1D159, U+FFFC, U+E000, U+200B, U+2060, U+3164, U+2800 or U+0301, in every slot. The test `test_clause_accepts_exactly_its_documented_allow_list` now also sweeps "x." c "y" over every Unicode scalar value c: the word is accepted exactly when c is a word character and a `follower` |
| Accepted examples that must stay accepted | yes | :228 ("." before an allowed character, ")", "”", "(", "—", in every slot). :229 (round trip with "3.5" and "e.g"). :230 and :232 (19 words and the self-review's five sentences). :236-:238 (`follower`'s edges) |
| Kept selected | yes | `test_clause_accepts_exactly_its_documented_allow_list` is extended: it keeps its three sweeps and adds "joined" and `follower`'s docstring. `test_word_char_refuses_exactly_its_documented_characters` is unchanged, and so is `wordChar`. The PROBE F8/F9/F10 and U+1D159/U+E000/U+FFFC guards are unchanged. `test_review_f8_f9_f10_...` adds the joined probes and checks that the new guards stay |
| DRI 2026-11-10 item 1: refuse a Markdown character reference in a slot word | yes | `charRef`: "&", then a non-empty run of ASCII letters, digits or "#", then ";", as the ruling states it (review F2: the first version asked for a run of two and let "&a;", "&#;" and "AT&T;" through). Guards :245 (the builder's two sentences), :247 (&nbsp; &#32; &#x20; &period; &#46; in every slot), :249 and :252 (refused), :254 and :255 (a run of one, in every slot), :257 and :258 ("AT&T" and "x&;" accepted). `test_char_ref_refuses_every_run_the_ruling_names` sweeps "x&" c ";" over every scalar value. Seeded bugs: three in `charRef`, one in `clause`, all KILLED |
| DRI 2026-11-10 item 2: inline HTML | moved by the ruling | FOLLOW-UP sc-7-f12 (the line above) |
| REPORT "D +140" corrected to "V +112" | yes | `docs/scope/sc-7/REPORT.md:60` |
| FOLLOW-UPS.md "213 KILLED" corrected to 229 | yes (done in the review round, F3) | `manage-agents/FOLLOW-UPS.md`, "## sc-7" row (line 2194) |

**V +112.** `uv run python tools/trust_map.py --files <out>` on main f3f40d51d gives `VE/Scope/Authoring.lean`
{S 37, D 140, D[V] 112, D[I] 28, trusted 149}. Trusted counts K + S + untied [V], and 37 + 112 = 149. The "D +140" in
sc-7's REPORT also counted the 28 D[I] lines.

**229 KILLED.** The counts in `docs/scope/sc-7/trust-mutants.json` (head b11beab23) are {KILLED 229, SURVIVOR 0,
UNKNOWN 0, INVALID 64, ALLOWED 27}. 213 was the earlier F8/F9 run on c494438df.

**Why (a), not (b).** (b) refuses an enumerated set (Cf ∪ Mn ∪ Me ∪ Default_Ignorable_Code_Point ∪ {U+2800}). In each
of the earlier rounds F7 to F10, a set like that missed a character. (a) needs no list of blank-looking characters.
After a character outside the allow-list there must be a `follower`, and `follower` is a short closed list of visible
characters.

## What changed direction (accepted before, refused now)

1. **A word holding a character outside the allow-list, followed by one that is no `follower`.** :241 lists "x.́y",
   "x​​y", "x”́y", "x.‏y", "x.‰y", "x.¡y" and "x.⁠y". This includes:
   - any run of two non-Latin letters inside a word ("xαβy", "Привет,", "日本語-text");
   - two combining marks in a row ("́́y", :252);
   - a word that starts with a sentence end and a blank character (".​y", :252).
2. **A word holding a Markdown character reference** (:247, :249, :254 and :255), "AT&T;" and "x&#;" among them.

Spec 2.2 (docs/spec/scope.md:360-375) leaves `<condition>` as free English, so it admits these words. They are refused
in the refuse direction of R16 and of the DRI's decision. Before this item, a non-Latin word in a slot was already
refused unless its last character was on the allow-list (sc-7, note (c)).

Every earlier guard passes unchanged (`lake build VE.Scope.AuthoringExamples`: "Build completed successfully"). All 10
tests of `tests/test_scope_authoring.py` pass (`uv run pytest -q tests/test_scope_authoring.py`: "10 passed in
125.86s"; log /tmp/sc7f11/pytest3.log).

## Seeded bugs (Lean; `docs/scope/sc-7-f11/mutants.json`, 16 KILLED)

For each bug: plant it in `lean/VE/Scope/Authoring.lean`, run `lake build VE.Scope.AuthoringExamples`, restore. The
last column is the guards that failed.

| Definition | Bug | Fails |
|---|---|---|
| `clause` | drop the new condition | :220, :225, :241, :252 (each probe guard) |
| `clause` | allow "!" inside a word | :225 (the "!" row of the class guard) |
| `clause` | allow "." inside a word | :220, :225, :241, :252 |
| `clause` | the follower may be any `wordChar` | :220, :225, :241, :252 |
| `clause` | drop the `charRef` conjunct | :245, :247, :249, :252, :254, :255 |
| `follower` | no closer | :268 |
| `follower` | no allow-listed character | :236, :238 |
| `follower` | no ASCII graphic range | :228, :230, :232, :236 |
| `follower` | ASCII range widened to U+0080 | :236 |
| `follower` | U+2010..U+2027 dropped | :228, :230, :232, :236 |
| `follower` | range widened to U+2030 | :236, :241 |
| `charRef` | a run of two needed (the first version; review F2) | :254, :255 |
| `charRef` | no "#" in the run | :245, :247, :249, :254, :255 |
| `charRef` | no ";" needed | :257, :258 |
| `allowed` | no ASCII punctuation | :229, :230, :232, :257, :272, :281 |
| `allowed` | U+01C3 allowed | :276, :278 |

Only Lean product code changed. The Python edits are all in `tests/test_scope_authoring.py`, and no Rust changed.

**Trust mutants.** The run was `mac-pytest.sh --trustmut -- --max-mutants 1000 --test
lean/VE/Scope/AuthoringExamples.lean --json docs/scope/sc-7-f11/trust-mutants.json --allow
docs/scope/sc-7-f11/trust-mutants-allow.json`, rerun after review F2 on ve-cloud-2 at dd9e73266 (the record's `head`), a
full run with no `--rescore`. Result: 4 definitions, 127 mutants, 89 KILLED, 0 SURVIVOR, 0 UNKNOWN, 25 INVALID, 13
ALLOWED, exit 0. The one new ALLOWED is `!(r.take 1).isEmpty`, equal to `!r.isEmpty` (its reason is in the allow
file). The run before the review fix (a89a4da7f, with `--rescore`) gave 93 KILLED, 12 ALLOWED, 130 mutants.

The first run (on 656670ba6) left 11 survivors and 4 UNKNOWN:
- Three were closed by :252: `charRef` checking only the first "&", or only the last, and `clause` skipping a word's
  first pair.
- Each of the rest is allowed with its reason: `follower` `≤ 0x7E`→`<` (U+007E is a closer), `closers.drop 1`
  (U+0022 is ASCII graphic), `clause`'s `dropLast` (zip truncates, or the end conjunct refuses), `clause`'s list-last
  (`getLast?`), `charRef`'s `.take 1` before `startsWith`, and the ill-typed `list-empty` mutants.

## Trust

Command: `uv run python tools/trust_map.py --check` at HEAD, against f3f40d51dc6d. Output: "K +0, S +0, D +22, G +0,
tied +0, unclassified +0, trusted +22 … VE/Scope/Authoring.lean: trusted +22 … PASS".

| Definition | Lines |
|---|---|
| `allowed` (new) | 4 |
| `follower` (new) | 6 |
| `charRef` (new) | 7 |
| `clause` | +5 |

The line counts include each definition's blank line. All four are classed D[V] in `tools/trust-classes.json`;
`slotsJoined` is T. The allowance is recorded with `--allow`: "SIGNED by standing ruling R16 (DRI-RULINGS.md),
sc-7-f11, 2026-11-10". The ties-pass row is FOLLOW-UPS.md:2518, "## sc-7-f11 ties pass" (added in the review round,
F1: the earlier text said it existed; it did not).

## Checks run once on the finished code

- `uv run python tools/regen_generated.py --write`: "wrote 38 entries".
- `(cd lean && lake build)`: "Build completed successfully (1363 jobs)".
- `python3 lean/audit.py`: "PASS: 830 source files; 9335 named theorem declarations audited".
- `regen_generated.py --check`: "checked 38 entries".
- The selected tests, run once on the committed tree 06c3eb181:
  - Command: `MAC_PYTEST_NO_DEFER=1 mac-pytest.sh --select -- --base f3f40d51d --run`. It ran on the VM: 468 of 581 units,
    9245 s, exit 1.
  - It recorded 417 units, then stopped early at `--maxfail 5` with 51 units not run.
  - The failure was `tests/test_scope_lean.py::test_every_trusted_scope_definition_is_used_by_a_theorem` and the four
    tests derived from it. That test lists the Authoring definitions no theorem states, and it did not name the three
    new ones. Commit 617edc979 adds them.
  - The rerun was `mac-pytest.sh -- tests/test_scope_lean.py` plus the 51 units that did not run: "1789 passed in
    1246.94s", exit 0.
  - The selection is wide (468 units) because `tools/trust-classes.json`, `lean/declarations.txt` and the regenerated
    codemap are read by many units.
  - No test of `main-known-red.txt` was involved.

## Size

`git diff --numstat $(git merge-base HEAD main)`, outside the generated files (`docs/codemap/`,
`lean/declarations.txt`), at the docs commit: about 500 changed lines. Of these, 132 are the trust_mutants tool's
record, and the rest are hand-written:

| Part | Lines |
|---|---|
| Lean `Authoring.lean` | 28 |
| Guards | 48 |
| Test | 51 |
| Side tables | 11 |
| Allow file | 34 |
| `mutants.json` | 22 |
| DELTA, REPORT and the sc-7 fix | the rest |

This is under the 600 cap. It is over LIGHT_LANE's 150, and `tools-local/light-lane.py` gave NOT (trusted core), so
the trust-mutant sweep ran.

## Spec re-read

- `clause` against docs/spec/scope.md:362 ("Each wording has one reading"): a slot that holds a hidden sentence end
  has two readings.
- The DELTA row against docs/spec/scope.md:369-375 (the `<condition>`, `<list name>` and section slots of 2.2's rows).
- `charRef` against reviews/dri-decisions-20261110-sc-7-f11.md item 1 ("&", then a non-empty run of ASCII
  alphanumerics or "#", then ";"): the same rule. The ruling's AT&T condition is "AT&T" (no ";"), which stays accepted;
  "AT&T;" holds the reference "&T;" and is refused (review F2 corrected the earlier run-of-two reading).

## Pilot bytes

None expected. No route reads `clause` yet; sc-7b wires the IDE. Nothing is claimed before a pilot audit.

## Next item

FOLLOW-UP: sc-7-f12 (inline HTML, filed by the DRI). sc-3b, sc-e1 and sc-e2 follow their own gates.

## Self-review against BUILDER-CHECKLIST

1. N.A.: no relayed answer and no route; `clause` is Lean-only.
2. PASS: each task row is in "Rows delivered"; no Python copy of a Lean decision (the test's `ALLOW`/`FOLLOWER_DOC`
   are the documented sets, checked against Lean); no report test; no overlap with in-flight branches.
3. PASS: 16 hand mutants KILLED (`mutants.json`); trust mutants exit 0 (`trust-mutants.json`).
4. PASS: valid inputs still pass (:228-:238, :254-:255, every earlier accepted guard).
5. N.A.: no Python reads a Lean answer here.
6. PASS: the chain gates the final HEAD; regen, lake build and audit ran on the final Lean.
7. PASS: the DELTA row cites R16; the trust growth is under R16; no reserved signature.
8. PASS: DELTA's row lists both refusals and what changed direction.
9. PASS: the selection includes `tests/test_scope_authoring.py` and `tests/test_scope_lean.py`, and it caught the missing
   `AUTHORING` names. It is wide because of the shared side tables, not an unlayered path.
10. N.A.: no theorem statement changes (`scope_parseRender` and `scope_renderParse` still build).
11. N.A.: no budget or deadline.
12. PASS: the follower check is one pass over a word's pairs; no Lean call per candidate.
13. N.A.: no test removed or renamed.
14. PASS: both directions are guarded; each claim cites its command; spec re-read above.
15. PASS: overclaims fixed ("so no character drawn as a space or as nothing follows a sentence end" is proved by :220,
    :225 and the "joined" sweep; Markdown inline HTML is named deferred, sc-7-f12); no cut deliverable; every new
    guard has a mutant; no limit applies.

SELF-REVIEW: 2 A, 5 B, 4 C; fixed 11
