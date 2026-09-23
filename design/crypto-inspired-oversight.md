# Cryptography-inspired ideas for VE oversight (2026-09-22)

Status: IDEAS, not a plan. Anything built from here needs the usual plan review (Astra xhigh + Opus xhigh) first.

## Why cryptography is the right lens

Cryptography rests on an asymmetry: checking a proof is cheap even when producing it, or redoing the work, is
expensive. Our results say the same about VE. Frontier judges gained nothing on small tasks because they can redo the
work (E1, P1 Gemini, V4, D pilot); a benefit is only possible where redoing is too costly (T1 at 5,000 grants) or where
the claim is universal (P3: VE certified 6/12 "for all principals" properties that plain review cannot). Design for the
asymmetry.

## 1. Certificates for "no" answers (NP vs coNP)  [highest priority]

"u can access x" has a short witness (the path). "u cannot access x" is universal and has none by default; it is the
claim T1's saboteur makes. Require a separating certificate: a set S of principals/groups/roles/resources with u in S,
S closed under every grant/membership/inheritance edge (no edge leaves S), and x not in S. Checking is one linear pass
over the edges; acceptance proves non-reachability. This is an inductive invariant (as for loop invariants).
Experiment: T1/T1b with "cannot access" claims that must carry S; compare checker + weak monitor vs Opus reading the
raw policy. Generalises to P3-style universal properties (invariants for "no principal can ...").

## 2. Authenticated verdicts (MACs/signatures)

P1: a capable judge follows the content of checker-shaped text regardless of provenance, so a judge cannot be relied
on to spot forgeries. The gate verifies a signature on every checker verdict; unsigned "checker says" text never
reaches the judge. Authenticity is a system property, never a judgment.

## 3. Commitments against shifting definitions

A definition that shifts across sub-claims (P5, safety-case D5.5) is a commitment failure. `meaning_id` is already a
hash commitment: arguers commit to vocabulary and claim ids before cross-examination; any later change is flagged
mechanically. Test as an added P5 arm.

## 4. Security games and Kerckhoffs's principle

Define oversight soundness as a game: an adversarial agent wins if an unsafe action or false claim is approved; report
the adversary's advantage, not average accuracy. Assume the adversary knows the whole system (the D-pilot
mistranslation attack already gives it the checker); evaluate against the best attack, not random planted flaws.

## 5. Probabilistic checking and soundness amplification

Translation fidelity is checked by sampled tests (P3: 66% of seeded mistranslations caught). State it as a soundness
error at a given sample size and amplify: more and independent random challenges, boundary-targeted inputs, multiple
test generators. Longer term: PCP-style spot-checking of very large certificates.

## 6. Minimal trusted base and transparency

Reference-monitor rules (complete mediation, tamper-proof, small enough to verify): only the verified checker and the
signature check are trusted. Log every approved action with its proof in an append-only hash chain (certificate
transparency style) for later audit.

## Related design direction: proof-carrying actions

Agents propose the exact tool call plus a VE proof that it complies with policy; the system executes only the call
named in a checked certificate (binding intent to action), with facts filled by trusted lookups ("says" provenance:
proof-carrying authorization, Appel & Felten 1999; Grey), tool contracts as reviewed VE pre/effect specs, trajectory-
level policies (information flow as closure/reachability), and delegation via attenuated Datalog-style tokens
(Biscuit, macaroons). Flagship evaluation: ControlArena-style control settings vs frontier LLM monitors.

## Assessment: what is most promising (2026-09-22)

**Most promising: separating certificates for universal claims, inside proof-carrying actions.**

Why:
1. It targets the only place our data leaves room. Wherever a frontier model can redo the work, VE added nothing (E1,
   P1 Gemini, V4, D pilot, P3 single requests). Where redoing is expensive or the claim is universal there are signs of
   life: at 1,500 grants Opus wrongly approved 6.7% of false "no access" claims (T1 gate); P3 certified 6/12 "for all
   principals" properties plain review cannot. Reading 5,000-50,000 grants should degrade; a linear certificate check
   does not.
2. The asymmetry is real, not constructed: "cannot access" otherwise requires exhaustive search by the verifier; with a
   certificate the verifier checks one closed set in one pass, independent of judge strength.
3. Ground truth is computable (access either exists or not), so no LLM grades outcomes.
4. It connects directly to AI control ("this action cannot reach secrets", "this change grants no new access") and
   extends to proof-carrying actions and information-flow policies.

Main risk (hostile reviewer): "a 20-line graph-reachability script does this; why VE?" Partly true: much of the
benefit belongs to the certificate protocol, not to VE's English. Defensible claims: (a) the protocol result itself
(untrusted agent supplies the certificate, trusted checker verifies), reported honestly even where a plain script
could play VE's role; (b) VE's role is generality: one proved-sound, human-readable language and checker for
reachability, role inheritance, universal policy properties, exceptions (once added) and multi-step trajectory rules,
instead of a bespoke script per policy type. Include a plain-script baseline and state where VE adds nothing.

Ranking of the rest: signed verdicts are a design rule to adopt (no research result left after P1); meaning_id
commitments are a reasonable P5 arm against a strong cross-examination baseline (expect a modest effect at best);
security games, amplification and transparency logs are methodology and deployment, not the headline.

Proposed next experiment, T1c (plan review required first): "cannot access" claims at 5,000 and 20,000 grants; the
saboteur must attach a separating set. Arms: Opus reading the raw policy; Haiku reading the raw policy; Haiku plus the
checker's verdict on the certificate; a plain graph-script baseline. Primary metric: false approval of sabotaged claims
against honest completion. Preregistered and timestamped; judge calls on the danielsaeedi37 account.
