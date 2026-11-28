# The tour's manifest of record

<!-- Written by tour/make_manifest.py; do not edit by hand. tests/test_tour.py fails when it drifts. -->

Which commit each part of the tour and of the demo video comes from. Every stop's script, and the small
program it runs, come from the checkout it is run in. The stops marked after-release run that program
with VE's code from the pinned after-release commit; the others use the checkout's own VE. What each stop
printed is recorded in tour/expected/. The demo video shows lines of those recorded outputs, each taken
at a commit named below.

- **Commit of record (main):** `0d184debe98820e25d005bb26cfd0336b2240e43`.
  The tour's timings were measured at it; each stop's recorded output below is compared with the one
  recorded at it.
- **After-release commit (pinned in tour/AFTER_RELEASE_COMMIT):** `a5dde317c4a53994128242b757af17eeaf870901`.
- **Timings** (tour/README.md, "How long it takes"): measured at main `0d184debe9`, after-release `a5dde317c4`.

## Stops

| stop | runs from | recorded output (sha256, first 12) | same output at the commit of record |
|---|---|---|---|
| 01-yes | this checkout | `f9440c4bea70` | same |
| 02-not-necessarily | this checkout | `fc399acb7b01` | same |
| 03-every-or-some | this checkout | `2fc3d3d88c78` | same |
| 04-date | this checkout, with VE from after-release `a5dde317c4` | `db7cf04c72f0` | same |
| 05-sum | this checkout, with VE from after-release `a5dde317c4` | `bdc03557aa6d` | same |
| 06-checker | this checkout | `45432a1e9c9f` | DIFFERS: recorded again after the commit of record |
| 07-company-policy | this checkout, with VE from after-release `a5dde317c4` | `b67d8a2a1857` | same |
| 08-outside-the-text | this checkout | `079312bb7705` | same |
| 09-planted-mistake | this checkout, with VE from after-release `a5dde317c4` | `61f45edbb9b3` | DIFFERS: recorded again after the commit of record |
| 10-not-yet | this checkout, with VE from after-release `a5dde317c4` | `b7b1829ab429` | same |
| 11-longer-example | this checkout | `9a802399645c` | same |
| 12-write-your-own | this checkout | `a2a226f5d376` | not recorded at that commit |

## Video scenes

From tour/video-sources.tsv (the lines of the stops' outputs that the video shows; its default commit `364dcfb813`), copied on 2026-11-28 from the demo video build's sources.tsv (cut 2; sha256 181dd81a0b3110c24583b1e0b5cbd9eaeec0dcccd1ae0d85264f07ad71f506c1; 94 lines listed there; the lines that quote records outside this repository are left out).
"Same at the commit of record" and "same today" compare each shown line with the same line of the
recorded output at the commit of record and in this checkout. "After-release pin then" is the pin in
force at the scene's commit, for the stops that use it.

| scene | output it shows | taken at commit | after-release pin then | lines shown | same at the commit of record | same today |
|---|---|---|---|---|---|---|
| d1 | tour/expected/01-yes.txt | `364dcfb813` | - | 1, 2, 3, 4, 5 | yes | yes |
| d2 | tour/expected/02-not-necessarily.txt | `364dcfb813` | - | 1, 2, 3, 4 | yes | yes |
| d3 | tour/expected/03-every-or-some.txt | `364dcfb813` | - | 1, 2, 3, 4, 5 | yes | yes |
| d4 | tour/expected/04-date.txt | `364dcfb813` | `a5dde317c4` | 1, 2, 5, 6, 7, 8, 9 | yes | yes |
| d5 | tour/expected/05-sum.txt | `364dcfb813` | `a5dde317c4` | 1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 17, 18 | yes | yes |
| d6 | tour/expected/06-checker.txt | `364dcfb813` | - | 1, 2, 3, 4, 5, 13, 14, 15, 16, 17, 18, 173, 174, 175, 176, 228 | yes | NO: line 1, 173, 174, 175, 176, 228 differs (re-cut the scene) |
| d7 | tour/expected/07-company-policy.txt | `364dcfb813` | `a5dde317c4` | 1, 2, 3, 4, 5 | yes | yes |
| d8 | tour/expected/08-outside-the-text.txt | `364dcfb813` | - | 1, 2, 3 | yes | yes |
| d9 | tour/expected/09-planted-mistake.txt | `d992212501` | `a5dde317c4` | 1, 2, 3, 6, 7, 8, 9, 19, 20, 21, 22, 23 | NO: line 6 differs | yes |
| d10 | tour/expected/12-write-your-own.txt | `951556d46c` | - | 22, 23, 24, 25, 27, 34, 39, 40, 41 | no: not recorded at that commit | NO: line 22, 23, 24, 25, 27, 34, 39, 40, 41 differs (re-cut the scene) |

Stops the video does not show: 10-not-yet, 11-longer-example.
