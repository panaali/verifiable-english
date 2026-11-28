# The tour's manifest of record

<!-- Written by tour/make_manifest.py; do not edit by hand. tests/test_tour.py fails when it drifts. -->

Which commit each part of the tour and of the demo video comes from. A stop runs the code of the checkout
it is run in (stops on main) or of the pinned after-release commit (the other stops); what it printed is
recorded in tour/expected/. The demo video shows lines of those recorded outputs, each taken at a commit
named below.

- **Commit of record (main):** `0d184debe98820e25d005bb26cfd0336b2240e43`.
  The tour's timings were measured at it; each stop's recorded output below is compared with the one
  recorded at it.
- **After-release commit (pinned in tour/AFTER_RELEASE_COMMIT):** `a5dde317c4a53994128242b757af17eeaf870901`.
- **Timings** (tour/README.md, "How long it takes"): measured at main `0d184debe9`, after-release `a5dde317c4`.

## Stops

| stop | runs from | recorded output (sha256, first 12) | same output at the commit of record |
|---|---|---|---|
| 01-yes | main (this checkout) | `f9440c4bea70` | same |
| 02-not-necessarily | main (this checkout) | `fc399acb7b01` | same |
| 03-every-or-some | main (this checkout) | `2fc3d3d88c78` | same |
| 04-date | after-release `a5dde317c4` | `db7cf04c72f0` | same |
| 05-sum | after-release `a5dde317c4` | `bdc03557aa6d` | same |
| 06-checker | main (this checkout) | `774e4015aed3` | same |
| 07-company-policy | after-release `a5dde317c4` | `b67d8a2a1857` | same |
| 08-outside-the-text | main (this checkout) | `079312bb7705` | same |
| 09-planted-mistake | after-release `a5dde317c4` | `61f45edbb9b3` | DIFFERS: recorded again after the commit of record |
| 10-not-yet | after-release `a5dde317c4` | `b7b1829ab429` | same |
| 11-longer-example | main (this checkout) | `9a802399645c` | same |
| 12-write-your-own | main (this checkout) | `9530610a7c64` | not recorded at that commit |

## Video scenes

From tour/video-sources.tsv (the video's own list of the lines it shows; its default commit `364dcfb813`).
"Same today" compares each shown line with the same line of this checkout's recorded output.

| scene | output it shows | taken at commit | lines shown | same today |
|---|---|---|---|---|
| d1 | tour/expected/01-yes.txt | `364dcfb813` | 1, 2, 3, 4, 5 | yes |
| d2 | tour/expected/02-not-necessarily.txt | `364dcfb813` | 1, 2, 3, 4 | yes |
| d3 | tour/expected/03-every-or-some.txt | `364dcfb813` | 1, 2, 3, 4, 5 | yes |
| d4 | tour/expected/04-date.txt | `364dcfb813` | 1, 2, 5, 6, 7, 8, 9 | yes |
| d5 | tour/expected/05-sum.txt | `364dcfb813` | 1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 17, 18 | yes |
| d6 | tour/expected/06-checker.txt | `364dcfb813` | 1, 2, 3, 4, 5, 13, 14, 15, 16, 17, 18, 173, 174, 175, 176, 228 | yes |
| d7 | tour/expected/07-company-policy.txt | `364dcfb813` | 1, 2, 3, 4, 5 | yes |
| d8 | tour/expected/08-outside-the-text.txt | `364dcfb813` | 1, 2, 3 | yes |
| d9 | tour/expected/09-planted-mistake.txt | `d992212501` | 1, 2, 3, 6, 7, 8, 9, 19, 20, 21, 22, 23 | yes |
| d10 | tour/expected/12-write-your-own.txt | `951556d46c` | 22, 23, 24, 25, 27, 34, 39, 40, 41 | yes |

Stops the video does not show: 10-not-yet, 11-longer-example.
