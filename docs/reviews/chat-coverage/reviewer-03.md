# Coverage review: Chat lines 1320–1835

Owned source range: `docs/sources/Chat-Formalize English In Lean.md` lines **1320–1835**, read in full. Architecture line references below refer to the **pre-edit baseline** `docs/sources/verifiable_english_brainstorming_and_architecture_complete.md`, SHA256 `74d12bccca86206274a660d257aab5af5bea4d7d687e8624d8bd55a78339e1da`. The chat's project and model claims are reported as claims made in September 2026, not independently verified facts.

## Source-backed partial coverage

1. **PENG's bidirectional grammar precedent is missing from its profile.** Chat lines **1524–1527** explicitly say PENG maps controlled English through DRS to logic *and* has a bidirectional grammar that generates English from formal representations. Architecture lines **239–262** cover PENG's Event Calculus extension, while lines **1980–1990** mention bidirectionality for ACE/OWL and lines **2241–2248** discuss GF abstract/concrete syntax. Proposed insertion after architecture line **241**: “The chat also identified PENG's bidirectional grammar: controlled English could be parsed through DRS into formal representations and generated back from a formal representation. This is an additional precedent for VE's parser/printer contract.” Keep the source's attributed status and cite the PENG paper already linked in the chat.

2. **The provisional ACE-first milestone and later CE-first collaboration decision need a chronology note.** Chat lines **1655–1668**, **1707–1711**, and **1733–1789** propose a new Lean core beginning with an ACE fragment, using CE ideas later; chat lines **1695–1705** separately rank CE first among potential collaborators. Architecture lines **28–39**, **1258–1299**, **1328–1414**, and **1870–1899** recommend contacting/forking CE first, then an ACE compatibility benchmark. The final memo may reasonably supersede the chat's provisional path, but currently it does not tell a reader why ACE-first became CE-collaboration-first. Proposed insertion near architecture lines **1276–1299**: “Earlier in the discussion, an independent Lean implementation of a useful ACE fragment was the proposed first technical milestone. The later synthesis retained that ACE compatibility milestone but moved CE source and collaboration due diligence ahead of it because CE was closer to the broader human–agent language goal. If CE access or architecture is unsuitable, the independent ACE-informed core remains the fallback.” This is a provenance/decision clarification, not a request to reverse the chosen roadmap.

## Optional editorial improvements

- Chat lines **1430–1451** identify TLC finite-state exploration and TLAPS theorem proving as distinct TLA+ tools. Architecture lines **2130–2172** and **4768–4802** cover TLA+ and model checking, but do not name those tools. A one-sentence addition after architecture line **2170** would make the distinction concrete: “TLC explores reachable states of finite models for counterexamples; TLAPS supports theorem proofs.” This is useful background, not a missing architecture decision.
- Chat lines **1604–1608** give the concrete pragmatics boundary “Can you open the window?” (ability question versus request). Architecture lines **56–67**, **2020–2022**, and **3791–3798** capture the general boundary. A concrete example near architecture line **3795** would help readers understand it, but no substantive concept is absent.
- Chat lines **1723–1729** contain time-sensitive model names, benchmark percentages, and one reported Lean formalization. Architecture lines **3522–3545** and **4962–4990** capture the capability argument and the Anthropic example. Avoid adding volatile benchmark numbers unless dated and checked independently; the architecture's omission of them is sensible.

## Compact coverage inventory

| Chat source lines | Major topic | Architecture baseline lines | Assessment |
| --- | --- | --- | --- |
| 1320–1346 | ACE++ feasibility, exact semantics, Lean AST, round trips, limits of full English | 11–26, 41–67, 1351–1390, 3750–3798 | Covered |
| 1350–1378 | Why ACE semantics were specified while APE implementation relied on tests; inferred historical reasons | 205–235, 3089–3138, 4554–4572 | Covered, with inference appropriately framed |
| 1382–1418 | Prolog versus Lean/Coq/Isabelle; proofs versus tests | 2176–2235, 3121–3138, 3750–3775 | Covered |
| 1422–1451 | TLA+ and Lean roles; TLC/TLAPS | 2130–2172, 4768–4802 | Main distinction covered; tool names optional |
| 1456–1502 | ACE temporal limitation and explicit timestamps versus native eventually | 2130–2170, 4501–4534 | Covered |
| 1506–1538 | Existing-system survey; PENG bidirectionality, Event Calculus, limits | 239–262, 2572–2587, 1997–2126 | Event Calculus covered; bidirectional grammar partial |
| 1540–1563 | FRETish temporal language and PVS semantic-equivalence precedent | 266–314, 2219–2235 | Covered |
| 1565–1573 | CLCE contexts/times and missing grammatical tense | 1997–2028 | Covered in substance |
| 1575–1610 | CE ambition, lexicon/entity grounding, small early implementation, constructive gap and pragmatics | 318–373, 4646–4743 | Covered; pragmatics example optional |
| 1612–1644 | Verbose Lean, Visored, combined opportunity | 2074–2128, 2572–2587, 1282–1299 | Covered |
| 1648–1711 | ACE-first Lean proposal, existing-project collaboration ranking, small temporal demonstration | 1166–1299, 1328–1414, 1463–1482, 1870–1899 | Content covered; decision chronology partial |
| 1715–1771 | Model-assisted revised implementation, ACE corpus, proofs checked by Lean kernel | 1138–1162, 1351–1414, 3522–3545, 4962–4990 | Covered; benchmark specifics appropriately omitted |
| 1773–1835 | Temporal/events/CE extensions; human semantic choices; Lean kernel as judge | 727–792, 1282–1299, 1463–1482, 3522–3545, 3750–3775, 4856–4857, 4962–4990 | Covered |

## Integration outcome

This report retains the original baseline citations. The parent verified and dispositioned every finding and optional suggestion in the [consolidated review](README.md), which gives exact updated architecture line numbers and the final outcome.
