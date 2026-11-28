# Stand-in newcomers: the three kept transcripts

The tour page (tour/README.md) was tried by three **stand-in** newcomers before it was published. They are not
people: each is a fresh AI session (Claude Sonnet 5.5, an Anthropic model) that knew nothing of the project. Real
first-time readers have not tried this page yet; whether two people read it first is the project lead's decision.

- run1.md, run2.md, run3.md: what each stand-in did, call by call, and its report, scrubbed (below).
- SCORES.md: their answers to the five questions graded against the fixed key (tour/NEWCOMER-QUESTIONS.md), and how
  that key changed over time.
- render.py: the script that wrote run1.md to run3.md from the sessions' records.

## How they were run (27 November 2026, 20:09 to 20:11 UTC)

- **The page they read**: tour/README.md as committed in b3786c3e70 (27 November 2026, 19:37 UTC), git blob
  dedcb76b77, sha256 c1350a65a9fc2a4f01e28ef5fd7d1a180469fc3fc4def308fec059839fdad01a (each run.md prints the sha256 of
  the page its stand-in read; all three match). b3786c3e70 is not on main (it was rebased away and may not exist in
  your clone); its page is ac985dbee0's tour/README.md without the 3-line "Clashing duty rules" item. The page has
  changed since (20 lines added, 12 removed when these runs were published); the stops' outputs (tour/expected/) are the same as the ones the stand-ins saw.
- **Their copy of the project**: a clean clone of that commit, with CLAUDE.md, AGENTS.md and tour/NEWCOMER-QUESTIONS.md
  removed so the session had no other guidance and never saw the key. The pinned after-release checkout
  (.tour-after-release/, a5dde317c4) was added.
- **The install was done for them.** A finished Lean and Rust build was copied into each clone, and sh tour/install.sh
  was run once before the session started. The stand-ins' install therefore took 7 to 8 seconds: these runs say
  nothing about how long a real first install takes.
- **The session**: `claude -p --model claude-sonnet-5-5 --effort high`, tools Read, Grep, Glob and Bash only,
  automatic memory off, no added tool servers, no slash commands; the prompt below on its input. Each finished in under two minutes.
- **The pass rule**, set before the runs: at least 2 of the 3 answer all five questions right, and none hits an error.
  Result: 3 of 3 answered all five right; none reported an error (SCORES.md).
  Graded by two Claude Opus 5.5 sessions, the same maker as the stand-ins; no person has graded them. The key was
  rewritten after rounds 1 and 2 had been read (SCORES.md).

### A fault in how runs 2 and 3 were set up

The three sessions ran at the same time on one machine. Runs 2 and 3 both saved the outputs of stops 6 to 12 to the
same scratch files (/tmp/out-<stop>.txt), so each may have read a file the other had just rewritten. The two copies
hold the same text (the same commit and programs), except once: run 3's first look at stop 12's file came while run 2
was rewriting it, and it saw 90 zero bytes in place of two lines (run3.md, call 5). Run 3 looked again (calls 6 and
7), found the full 44 lines, and its report calls it "a display problem in my tooling". Run 1 used its own file
names.

### Earlier rounds, not kept here

Rounds 1 to 3 (26 November) tried earlier versions of the page. Round 4 (27 November, 19:40 UTC) is void: the copied
build was incomplete, the install started a full Lean build, and all three sessions stopped at the prompt's 15-minute
limit. The three runs here are round 5.

## What was removed from the records

render.py keeps every tool call, its output and the final report verbatim, except:

- the stand-in's own folder is shown as `<newcomer>`, any other home folder as `<home>`, e-mail addresses as
  `<e-mail>`, an account name as `<account>`, a uuid as `<uuid>`, and a project folder's name as Claude Code
  stores it (its path with dashes for the slashes) as `<project>` (none shows in runs 1 to 3);
- a run of zero bytes is shown as "[n zero bytes]" (one output holds 90, see above);
- the page the stand-in read is not repeated (it is the page named above; its sha256 is printed);
- session and message ids, account and usage-limit details, cost and token counts are dropped. The sessions' hidden
  reasoning is not in the records (they keep none of its text).

## The prompt (the same for all three)

```
You are a newcomer who has never heard of this project. Your working directory holds a fresh copy of a software
project, in the folder ./verifiable-english (the "git clone" step of its page is already done for you).

Your task: learn what the project does by following ONE page, verifiable-english/tour/README.md, from top to bottom,
as a careful first-time reader would.
- Read only that page. Do not open any other file of the project to learn about it (no other README, no docs, no
  source code, no tour scripts, nothing under tour/expected). You may look at files that the page's commands print.
- Run the commands the page gives, exactly as written, from inside ./verifiable-english: first the install command
  (sh tour/install.sh), then each stop's command, in order. The project has not published the install's download yet, so
  your environment already sets VE_TOUR_PREBUILT to a copy of it, as the page's note describes; the install should
  finish in a few minutes. Use only these commands (plus cd and echo if you need them).
  If the install runs for more than 15 minutes, stop it and report that.
- After each stop, compare what you saw with the page's "What you should see".

Then reply with your report, in plain English, under 700 words, in three parts:
A. Where you stumbled: every place where the page was unclear, where you had to guess, where you were confused by
   a word, or where the output differed from the page. Quote the words that caused it and say which stop.
B. Errors: every command that failed or printed an error you did not expect from the page (quote the line), or "none".
C. Your answers to these five questions, in your own words, from what you read and saw:
   1. When VE answers "Yes" to a question about a text, what does it give you besides the answer, and what checks
      the reasoning?
   2. What is the difference between VE answering "Not necessarily" and answering "No"? What does VE show to back up
      a "Not necessarily"?
   3. What does VE do when a question uses words the text does not define, or when a sentence of the text can be
      read in more than one way?
   4. In the stop with the planted mistake, why does Lean not catch the mistake, and what does catch it?
   5. Name two things VE cannot do yet.
```

The prompt says VE_TOUR_PREBUILT is set; in these runs the install had already been run instead (above), so that note
did not apply (run 3 says so).
