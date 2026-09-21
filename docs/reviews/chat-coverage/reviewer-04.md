# Coverage review: Chat lines 1836–2291

Architecture line references below use the **pre-edit baseline**, SHA256 `74d12bccca86206274a660d257aab5af5bea4d7d687e8624d8bd55a78339e1da`. I read the entire owned Chat range and searched the entire architecture file before identifying gaps. The historical web and tool claims below are reported as claims made in the conversation, not independently verified current facts.

## Source-backed omissions or partial coverage

1. **CE component dependencies are incomplete.** Chat **1990–2003** explicitly identifies CGEL/CGELBank as grammatical structure, Stanza as a best-effort POS parser, and Markdown/markdownlint as document structure/checking. Architecture **4713–4743** already captures WordNet, entity identifiers, JSON-LD and Markdown/GFM, but does not mention CGEL/CGELBank, Stanza or markdownlint anywhere. The distinction matters for evaluating what can be reused if NOAH source is unavailable. **Proposed action:** Add after architecture **4723–4724**, marked as discussion-time candidates: “The CE description also points to CGEL/CGELBank for grammatical structure, Stanza for best-effort POS analysis, and Markdown/markdownlint for document structure/checking. These components could be assessed separately if NOAH cannot be obtained; their present integration and suitability need inspection.” Do not infer that they are hard dependencies of a source tree we have not inspected.

2. **The exact CE repository and license lead are missing from due diligence.** Chat **1932–1948** says the official site linked to `MichaelCurrie/canonical-english`, then returning 404, and described its code as MIT-0 with `canon/`, `src/`, and `docs/` directories. Architecture **4747–4764** records the inaccessible repository and calls for license confirmation, but omits the locator and what the site claimed about the license and layout. **Proposed action:** At architecture **4749–4759**, add a historical, explicitly unconfirmed note: “At the time of the discussion, the site linked to `MichaelCurrie/canonical-english` (including `FORMAT.md`); that URL returned 404. The site described the code as MIT-0 and mentioned `canon/`, `src/`, and `docs/`; confirm all of this against the obtainable repository before planning a fork.” This is an actionable lead, not a current availability or licensing assertion.

## Optional editorial suggestion

- Chat **2138–2154** loosely says a verified checker rejects parser “nonsense.” Architecture **678–723** correctly separates accepted-language soundness from recovery of human intent, and **447–483** describes the checker. Consider adding at architecture **708–723**: “A well-formed but unintended AST can pass the checker; user confirmation or equivalent provenance is needed to establish intended interpretation.” This reinforces an already covered distinction and is not a missing design decision.

## Compact coverage inventory

| Chat lines | Topic | Architecture baseline lines | Assessment |
| --- | --- | --- | --- |
| **1836–1920** | CE versus a new Lean-first project; CE maturity and constructivity; hybrid with Lean; collaborate first, CE-compatible successor; ACE as reference | **318–369**, **426–483**, **1166–1301**, **1870–1901**, **4646–4673** | Covered. |
| **1924–1950** | Repository search, 404, maintainer/contact rationale | **1328–1347**, **3339–3364**, **4747–4764** | Covered except exact historical locator/license/layout lead above. |
| **1954–2027** | Agent communication; NOAH parser/linter roles; DRS; reusable external components; JSON-LD and Lean branch | **318–425**, **3504–3517**, **4675–4743** | Covered except three component candidates above. |
| **2031–2105** | Lean semantics versus Rust implementation; checker architecture; parser proof requires extra work | **467–529**, **530–633**, **4806–4834** | Covered. |
| **2109–2224** | Soundness versus human intent; small checker; Aeneas, Kani and supported Rust subset; accepted-message guarantee | **560–633**, **674–723**, **2284–2314**, **2336–2368**, **3749–3799**, **4806–4902** | Covered; optional precision above. |
| **2228–2291** | VE as math front end to Lean; precedent systems and recent AI math examples; expressive goal and escape hatch; timing rationale | **892–934**, **2032–2103**, **3522–3624**, **3628–3685**, **4962–4992** | Covered. |

No substantive contradiction found in this range. The architecture's Rust core verified via Aeneas is a refinement of the Chat's earlier possible “small trusted Lean component” at **2067–2105** and its later combined recommendation at **2195–2224**; see architecture **560–633** and **4806–4834**.

## Integration outcome

This report retains the original baseline citations. The parent verified and dispositioned every finding and optional suggestion in the [consolidated review](README.md), which gives exact updated architecture line numbers and the final outcome.
