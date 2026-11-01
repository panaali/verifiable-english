# sn-b8 SOURCES: where each pack entry comes from

Every entry is taken from a declaration in the repository, cited by file and entry. Nothing is invented. Lean
judges each pack (`Dictionary.wf`, through `ve senses check`); where Lean refused a first draft, its text is noted.

Rules used for every entry:

- **word, wording, kinds, description**: the declaration's verbalisation, argument sorts and description, verbatim.
  The word is the one word of the wording that is not a hole or a function word (`resides_in` gives `resides`).
- **gloss**: no source declares a gloss. Each gloss is one to three words of the declaration's description,
  verbatim, other than the word itself: the meaning after the description's colon where it has one, otherwise the
  recording source the description names. Lean refused `recorded` and `nothing` (W2: reserved words); the
  glosses below replace them with other words of the same descriptions. For the verbs and the fluent and assist
  adjectives, the descriptions only restate the word, so their glosses name the recording source or the
  inventory. These glosses are weak, and the review reads them first.
- **sorts**: name and description from the environment's sort declaration. The noun is the sort name, as VE's
  English vocabulary reads a sort without a verbalisation. The plural follows VE's default plural
  (`ve/english_vocabulary.py:158`: `person` → `people`, otherwise noun + `s`; so `directorys`, as VE prints it
  today). The letter is the one S2's lexicon export gives for the same environment (`export(EnglishVocabulary(env))`).
- **negatives**: none is declared. Lean refused the declared `{0} does not reside in {1}` of `resides_in` (W5: "resides
  declares a negative wording although its negative is automatic"), so every negative is Lean's automatic one.

## policies@1 (`ve/senses/packs/policies@1.json`)

Source: `usecases/agent-policy/environment.lean.json`, `vocabulary.sorts` and `vocabulary.predicates` (the
entry named in the last column). `usecases/cedar-attributes/environment.json` has one predicate, `department`
(`person`, `$string`): its second kind is not a sort, so it cannot be a sense (W4), and it is not packed.

| Word | Wording | Kinds | Gloss (from the description) | Entry |
|---|---|---|---|---|
| reads | `{0} reads {1}` | action, file | file tools | `predicates.reads` |
| writes | `{0} writes {1}` | action, file | file tools | `predicates.writes` |
| deletes | `{0} deletes {1}` | action, file | file tools | `predicates.deletes` |
| contacts | `{0} contacts {1}` | action, host | network layer | `predicates.contacts` |
| messages | `{0} messages {1}` | action, person | mail chat tools | `predicates.messages` |
| discloses | `{0} discloses {1}` | action, secret | scanner | `predicates.discloses` |
| resides | `{0} resides in {1}` | file, directory | path resolver | `predicates.resides_in` |
| confidential | `{0} is confidential` | file | credential path list | `predicates.confidential` |
| tracked | `{0} is tracked` | file | version control | `predicates.tracked` |
| allowlisted | `{0} is allowlisted` | host | network allowlist | `predicates.allowlisted` |
| principal | `{0} is principal` | person | user | `predicates.principal` |
| confirmed | `{0} is confirmed` | action | dialog | `predicates.confirmed` |
| readonly | `{0} is readonly` | action | shell classifier | `predicates.readonly` |
| privileged | `{0} is privileged` | action | elevated privileges | `predicates.privileged` |
| affordable | `{0} is affordable` | action | spending limit | `predicates.affordable` |
| reported | `{0} is reported` | action | harness | `predicates.reported` |

Sorts: `action`, `directory`, `file`, `host`, `person`, `secret` from `vocabulary.sorts`. Not packed: `tool`
(`action`, `$string`: not a sort), `permitted` and `report_required` (no wording; the norms route generates them).
The plan's examples `access`, `allowed`, `denied` and `owns` are not declarations of either use case, so they are
not in the pack.

## software-services@1 (`ve/senses/packs/software-services@1.json`)

| Word | Wording | Kinds | Gloss | Entry |
|---|---|---|---|---|
| deployed | `{0} is deployed` | service | inventory | `examples/fluent/environment.json` `predicates.deployed` (description); gloss from `examples/assist/environment.json` `predicates.deployed` ("Recorded as deployed in this inventory.") |
| reviewed | `{0} is reviewed` | service | inventory | fluent `predicates.reviewed`; gloss from assist `predicates.reviewed` |
| owns | `{0} owns {1}` | person, service | ownership | fluent `predicates.owns` |
| safe | `{0} is safe` | service | inventory | `examples/assist/environment.json` `predicates.safe` (no verbalisation: the wording is the one VE gives it and the assist argument writes, "Every reviewed service is safe.") |

Sorts: `person` and `service` from `examples/fluent/environment.json` `vocabulary.sorts`. Not read: the
readability eval, which this build did not locate as a declaration source (its entries and table rows go to
sn-b8b). The plan's example `depends on` is in none of the sources read.

## Q3: words that would need two senses for two sorts

Counted over the two packs' sources: 0. No word of `policies@1` or `software-services@1` is declared with two
different kind lists, and the two packs share no word. Outside these sources, `tracked` is declared over `file`
(agent-policy) and over `level` (`usecases/safety-framework/environment.d1.json`), and `reached` over two different
first kinds (openai-preparedness, safety-framework). They belong to the risk sources, which go to sn-b8b with
`risk@1`.
