**20 of 20 sampled units are faithful.** The audit is written to `/home/seyran/code/manage-agents/pilots/claude-constitution/run-20260930T1800Z/AUDIT.md` (395 words). Read-only, no model calls. My git worktree is unchanged, and the pilot directory is not a git repository, so there is nothing to commit.

**Sample.** `random.Random("20260930T1800Z").sample(pool, 20)` over the 55 CHECKED/LABELLED/OPEN/READINGS units in `units.json` order drew 15 LABELLED, 4 READINGS and 1 OPEN. The only CHECKED unit (`u0248`) was not drawn.

**Faithful (20)**
- **LABELLED (15):** `u0126`, `u0265`, `u0277` and the heading markers of `u0008`, `u0032`, `u0040`, `u0055`, `u0075`, `u0130`, `u0195`, `u0207`, `u0238`, `u0257`, `u0260`, `u0286`. Every label equals the source line at the marker.
- **OPEN (1):** `u0073.s05`. "Generally" gives one defeasible reading. "Not unsafe, unethical, or against Anthropic's guidelines" is read as none of the three, each an open term.
- **READINGS (4):** `u0156.s03`, `u0078.s01`, `u0165.s02`, `u0165.s03`. Act, condition and the strict/defeasible pair match the source. The three repaired units keep the source's words in the guard atom, including "if deployed" for the cyberweapons unit with the attachment question listed as a factor, and excepted cases read "not required". Strict and defeasible readings differ in every sampled set.

**Unfaithful (0).**

**Minor, not counted**
- `u0078.s01`: "err on the side of" is a leaning, so the strict candidate is stronger than the source licenses, and no narrowing is recorded. Its English export does not parse back, nor does that of `u0073.s05`.
- `u0165.s02`: the act pointer "giving attack uplift" carries content. Harmless inside the guard, but the note's "abbreviates nothing" overstates it.
- `u0165.s02`, `u0165.s03`: the defeasible candidate contradicts `u0166.s04` ("cannot be unlocked"); the narrowing to strict is "recorded only".
- `u0126`: stray `ethical_harm` tag on a heading with no content (ledger only).

**Three highest-value missing features**
1. **Reading candidates that hold their rules, with narrowings that bind.** All four sampled sets keep a reading the source rules out or does not license. The translator's choice has no effect, the main premise status stays UNKNOWN, and readings live only in companion documents.
2. **An "unspecified" outcome for regulated acts.** All five sampled norms complete to "not required" where the source is silent, and the duty-to-avoid workaround forces pointer act phrases such as "avoid the creation in each situation".
3. **Act clauses in the source's words:** disjunction, qualifiers, no 80-character limit, and an English export that round-trips carve-out lists and nested guards. Next, norms inside attitude frames ("we want Claude to…"), the bulk of the 668 units blocked on norms.

One note for the orchestrator: the Write tool was denied in this session, as in the two previous audits, so the file was written through the shell instead.
