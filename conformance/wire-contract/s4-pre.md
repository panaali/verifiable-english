# S4-pre: align the two legacy soft-source rejection codes

The Python soft table now agrees with the frozen Lean soft route on the two
classes left by S3-pre. This is a product decision about rejected inputs; the
wire contract still decides no verdict. The comparison uses the 8,576-case
gate corpus at revision 3, before the public switch.

## Classes examined

Python's profile registry has six names absent from the Lean soft route:
`alternatives@0`, `norm-defaults@0`, `reports@0`, `rights@0`, `risk@0`, and
`speech-acts@0`. The soft route rejects all six in both languages. Four already
had matching codes. S3-pre aligned `rights@0` while preserving the rights
route. `speech-acts@0` was the remaining profile class with a code difference:
Python reached its later envelope check and returned `SOFT_INVALID_INPUT`;
Lean rejected the profile at check 3.2 with `SOFT_UNSUPPORTED_PROFILE`. Python
now rejects `speech-acts@0` at the profile check with the latter code and text.

The only profile passed to Python's inherited W1 decoder but omitted from
Lean's `inheritedProfiles` was `norm-defaults@0`. Python omits it when validating
a submitted source on the standalone soft route. An `unspecified` default under
that profile therefore fails the inherited declaration check with
`SOFT_INVALID_INPUT` in both languages. The inherited texts remain
language-specific: Python says `UnsupportedProfile: unspecified
completion requires norm-defaults@0`; Lean says `InvalidInput: invalid
regulated role or default for x_required` on the recorded input.

The full suite exposed a separate consumer: `norm_defaults.UnspecifiedSoftDocument`
constructs placeholder completions through `SoftEnvironment`. That route still
passes `norm-defaults@0` to W1, as it did before S4-pre. The narrower list is
selected only by `load_soft_document` and raw soft admission. This preserves the
norm-defaults route's verdicts and identities while closing the soft route's
code difference.

## Corpus result

The Python legacy validator's verdict, code, and text were captured before
the edit and compared by corpus position after it (labels alone are not unique).
Exactly three of 8,576 rows changed, all still rejected:

| Case | Previous Python code and text | New Python code and text |
|---|---|---|
| `L:speech-acts@0:env` | `SOFT_INVALID_INPUT`; `Incorrect fields (missing=['speech_acts'], unknown=[])` | `SOFT_UNSUPPORTED_PROFILE`; `UnsupportedProfile: Unsupported profile speech-acts@0` |
| `L:speech-acts@0:base` | same | same as the row above |
| `L:norm-defaults@0:unspecified` | `SOFT_UNSUPPORTED_PROFILE`; `UnsupportedProfile: norm-defaults@0 documents are checked through fill (ve.norm_defaults)` | `SOFT_INVALID_INPUT`; `UnsupportedProfile: unspecified completion requires norm-defaults@0` |

Every other corpus row kept its verdict, code, and text. No Lean decoder or
route row was edited. The switch gate requires `legacy_code_differences` empty.
