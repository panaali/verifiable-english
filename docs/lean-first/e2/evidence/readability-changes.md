# E2.5 readability replay

Frozen evaluation `ac91e1e4`; base `9aaf918d`; reviewed merge `9cc8418d`. The saved writing files hold every one of the 36 recorded attempts and their scorer verdict and displayed message. The saved reading files hold all 30 item keys and VE verdict sentences, including replay errors. No model was called.

Writing: 6 changed messages, 0 changed scorer verdicts. On Python authority with Lean in shadow, all 36 writing verdicts and messages match the base. Reading: 5 changed item outcomes; 5 became unavailable on the current checkout. The risk calls use the current route signature, and the speech replay has the frozen evaluation import path available.

## Changed writing messages at the reviewed merge

| Item | Base verdict | Base message | Merge verdict | Merge message |
|---|---|---|---|---|
| W08 s1 attempt 1 | parse_failure | Expected ', then ' here. Use the English paraphrase as a writing example. | parse_failure | Sentence 1 has no reading with the current vocabulary. Unknown English phrase 'person was born in the United States'. Nearest declared wordings: 'was born in the United States'; 'was naturalized in the United States'; 'is a citizen of the United States'. |
| W08 s2 attempt 1 | parse_failure | Expected ', then ' here. Use the English paraphrase as a writing example. | parse_failure | Sentence 1 has no reading with the current vocabulary. Unknown English phrase 'person was born in the United States'. Nearest declared wordings: 'was born in the United States'; 'was naturalized in the United States'; 'is a citizen of the United States'. |
| W12 s1 attempt 1 | parse_failure | Unknown English phrase 't'. Nearest declared wordings: 'owns {1}'; 'person'; 'service'. | parse_failure | Sentence 1 has no reading with the current vocabulary. A sentence that begins with "no" cannot use "that" or "who" after the noun. Write "it is not the case that there is ... such that ..." instead. |
| W12 s2 attempt 1 | parse_failure | Unknown English phrase 't'. Nearest declared wordings: 'owns {1}'; 'person'; 'service'. | parse_failure | Sentence 1 has no reading with the current vocabulary. A sentence that begins with "no" cannot use "that" or "who" after the noun. Write "it is not the case that there is ... such that ..." instead. |
| W12 s2 attempt 2 | parse_failure | Expected '.' here. Use the English paraphrase as a writing example. | parse_failure | Sentence 1 has no reading with the current vocabulary. Unknown English phrase 'No service'. Nearest declared wordings: 'service'; 'person'; 'is reviewed'. |
| W14 s1 attempt 1 | parse_failure | Expected '.' here. Use the English paraphrase as a writing example. | parse_failure | Sentence 1 has no reading with the current vocabulary. |

These six changed texts fail the specified preservation test: W08 loses the paraphrase suggestion; W12 loses the base named phrase or paraphrase suggestion; W14 loses the paraphrase suggestion. The replacement for W12 attempt 1 adds a useful rewrite but does not retain the base named phrase.

## Changed reading items after the authority revert

| Item | Base verdict | Base message | Current verdict | Current message |
|---|---|---|---|---|
| R23 | FOLLOWS |  | unavailable | cannot import name 'SpeechDocument' from 've.speech_acts' |
| R24 | GAP |  | unavailable | cannot import name 'SpeechDocument' from 've.speech_acts' |
| R25 | REQUIRED |  | unavailable | cannot import name 'SpeechDocument' from 've.speech_acts' |
| R29 | FORBIDDEN | The text says Texas must not deprive Ann of life (rule 1). | unavailable | fields do not match: expected [sort, description], got [description, sort, verbalisation] |
| R30 | DNS | The text does not say whether Texas must protect Ann against deprivation of life: no rule decides this situation. | unavailable | fields do not match: expected [sort, description], got [description, sort, verbalisation] |

R23–R25 became unavailable because the frozen scorer imports `SpeechDocument` from `ve.speech_acts`, which the current checkout no longer exports. R29 and R30 became unavailable because the current checker rejects constant `verbalisation` fields in the frozen evaluation environment. These five items are not counted as preserved.
