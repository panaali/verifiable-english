# Coverage review: Chat lines 2292–2793

Architecture line numbers below refer to the **pre-edit baseline**, SHA256 `74d12bccca86206274a660d257aab5af5bea4d7d687e8624d8bd55a78339e1da`. I reviewed every line in the owned Chat range and searched the entire architecture document before identifying gaps. Claims about tools, legal doctrine, and constitutions below are attributed to the Chat discussion; they are not independently verified.

## Source-backed omissions or partial coverage

1. **RustCompCert's source-parser trust boundary is missing.** Chat 2670 says the Rust source parser is unverified and that the verified chain starts after parsing into Rustlight; it suggests a small verified parser, direct Rustlight AST generation, or separate parser verification. Architecture 639–668, 2489–2534, 2600–2645, and 4903–4925 describe the compiler route and research-stage limits but do not name this boundary. Add near architecture 4903–4925: “The Chat discussion reports that RustCompCert's source parser is unverified; its verified chain begins with the Rustlight representation. A future end-to-end claim must account for parsing, for example by validating or verifying a restricted source parser or generating the accepted Rustlight AST directly.” Treat this as a reported limitation pending toolchain re-evaluation.

2. **Rustlight's reported feature boundary is only generalized.** Chat 2641–2650 specifically lists structs/enums, `Box`/RAII, references/lifetimes, safe and unsafe modules, verified borrow checking, and compilation to assembly; it also lists absent concurrency, polymorphism, traits, and closures. Architecture 2639–2645 calls the subset restricted, and 2649–2672 lists proposed core constructs, but does not distinguish demonstrated Rustlight support from VE's design preferences or state the excluded features. Add a concise, qualified snapshot near architecture 2639–2645, with a warning to recheck the project's current supported subset before choosing core constructs. This is especially relevant to the architecture's asserted common subset at 2645.

3. **The legal example could state how unresolved standards and interpretive methods are represented.** Chat 2707 retains “unreasonable searches and seizures” as an explicitly open standard at the text layer; Chat 2709 names text, original meaning, precedent, historical practice, structure, and pragmatic reasoning as different interpretive methods. Architecture 1023–1082 and 5028–5062 preserve text, doctrine, provenance, and unresolved disputes, but do not give a concrete open-standard example or record the interpretive method behind a doctrine. Add near architecture 1064–1082: “A phrase such as ‘unreasonable searches and seizures’ may remain an open standard in the text layer. Attach an interpretive-method tag or rationale to each proposed doctrinal reading so competing methods can be compared without silently treating one as the text itself.” This is a modeling proposal from the Chat, not a claim that any particular method controls a case.

4. **The precedent-change query should be explicit.** Chat 2719–2726 asks exactly what changes if a precedent is overruled. Architecture 1045–1073 and 5028–5062 cover versioned doctrine, but do not spell out impact analysis over claims depending on that precedent. Add near architecture 1060–1073: “Given a narrowed or overruled precedent, report which derived rules and applications lose support, while preserving the previous doctrine snapshot.”

## Compact coverage inventory

| Major Chat topic (exact lines) | Architecture baseline lines | Assessment |
| --- | --- | --- |
| Scientific paper as semantic object; layers and hidden-assumption detection, 2294–2337 | 935–970, 3142–3215, 4199–4230 | Covered |
| Authors writing directly versus retrospective paper audit, 2339–2365 | 972–1019, 1510–1526, 4999–5024 | Covered |
| Logical, mathematical, empirical verification boundary, 2367–2430 | 3142–3215, 1008–1019 | Covered |
| Preferred Rust core to Aeneas to Lean; Kani as supplement, 2434–2470 | 578–630, 2284–2366, 4806–4832 | Covered |
| Native Rust performance and offline verification, 2474–2510 | 2284–2314, 2538–2558, 2600–2622, 4806–4832 | Covered in substance |
| Rust versus C, Frama-C and CompCert tradeoff, 2514–2540 | 2386–2562, 4929–4957 | Covered |
| Agent-written code does not remove semantics/memory proof work; hax/Aeneas and small core, 2543–2625 | 2318–2332, 2552–2558, 2600–2690, 4806–4899 | Covered |
| RustCompCert motivation and Rustlight boundaries, 2629–2678 | 639–668, 2489–2534, 2600–2685, 4836–4925 | Partial: findings 1–2 |
| Constitutional text, doctrine, provenance and disagreement, 2682–2728 | 1023–1082, 4215–4244, 5028–5062 | Partial: findings 3–4 |
| Claude/AI constitution, rule types, spirit and semantic modules, 2730–2762 | 819–852, 1086–1126, 3687–3739, 5066–5096 | Covered |
| Doctrine versioning while text persists, 2766–2790 | 1045–1062, 3803–3805, 5028–5062 | Covered |

## Optional editorial suggestions

- Chat 2490–2508 explains that Aeneas and Kani verification run offline and need not add runtime cost to the shipped native Rust. Architecture 2284–2314 and 4806–4832 imply this but could say it directly near architecture 2284–2314. Preserve the distinction between source-level proof and optimized executable behavior.
- Chat 2754–2756 explicitly links math, process, and normative dialects to classical/dependent, temporal/event, and deontic/defeasible semantics with Lean handling metatheory. Architecture 819–852 and 3970–4035 cover the components; a cross-reference near architecture 1086–1126 would make the design rationale easier to follow.

## Integration outcome

This report retains the original baseline citations. The parent verified and dispositioned every finding and optional suggestion in the [consolidated review](README.md), which gives exact updated architecture line numbers and the final outcome.
