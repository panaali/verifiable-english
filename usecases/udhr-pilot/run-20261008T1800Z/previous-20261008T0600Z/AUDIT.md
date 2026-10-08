**Faithful: 15/20.**

Sampling: Python `random.Random("20261008T0600Z")`, successive `.sample` calls on pools in `units.json` order: CHECKED 1, LABELLED 8, OPEN 0, READINGS 11. READINGS units appear as OPEN in document coverage. This stratified result is not a corpus-wide rate.

VERDICTS:
```text
u012 FAITHFUL
u020 UNFAITHFUL
u022a UNFAITHFUL
u024 FAITHFUL
u032 FAITHFUL
u033b FAITHFUL
u046 UNFAITHFUL
u047 FAITHFUL
u049 FAITHFUL
u050 FAITHFUL
u055 FAITHFUL
u056 FAITHFUL
u063 UNFAITHFUL
u065 FAITHFUL
u072 FAITHFUL
u074 FAITHFUL
u095 FAITHFUL
u104 FAITHFUL
u105b UNFAITHFUL
u111 FAITHFUL
```

Unfaithful units:

- **u020:** Lists whether territory status counts as country status as an unsettled question. The source explicitly covers both countries and territories; coverage does not depend on equating them.
- **u022a:** `claim_positive` and `claim_combined` add an active life-protection requirement. The words grant a right to life without specifying that positive protective obligation.
- **u046:** `entitlement_any` and `claim_any` discard “arbitrary” from the antecedent of “such interference,” extending protection to non-arbitrary interference.
- **u063:** Positive and combined readings require enabling property ownership. A right to own property does not itself specify a positive enabling obligation.
- **u105b:** Positive and combined readings similarly require enabling arts enjoyment, adding provision beyond the stated right.

Removing an invented duty-bearer does not make these added obligations textually supported. A faithful alternative does not rescue the reading set.

Three highest-value missing features:

1. **Native rights with unspecified responsibility:** preserve entitlements without forcing additional protection, provision, or enablement commitments.
2. **Compositional action phrases and scoped references:** retain long qualifications, coordination, and antecedent modifiers without hiding them in sort descriptions.
3. **Integrated norm-reading evaluation:** support unspecified defaults, references between reading sets, and Article 29 limitation links within the main document.

Source spans and companion source bytes match. No files changed or model calls made. AUDIT.md was not written because its destination is outside the permitted writable roots.
## Full audit of the remaining covered units (one-off, 2026-10-08; these verdicts count as audit-verified like the sampled ones)
Faithful: 17/34.

VERDICTS:
```text
u018 FAITHFUL
u022b UNFAITHFUL
u022c UNFAITHFUL
u025 FAITHFUL
u027 UNFAITHFUL
u029 FAITHFUL
u033a FAITHFUL
u035 UNFAITHFUL
u037 FAITHFUL
u045a FAITHFUL
u045b FAITHFUL
u048 UNFAITHFUL
u051 FAITHFUL
u059 FAITHFUL
u064 FAITHFUL
u066 UNFAITHFUL
u070 UNFAITHFUL
u073 UNFAITHFUL
u077 FAITHFUL
u081 UNFAITHFUL
u084a UNFAITHFUL
u084b UNFAITHFUL
u084c FAITHFUL
u084d FAITHFUL
u087 UNFAITHFUL
u096 FAITHFUL
u098 UNFAITHFUL
u099a FAITHFUL
u099b FAITHFUL
u100a FAITHFUL
u100b UNFAITHFUL
u105a UNFAITHFUL
u105c UNFAITHFUL
u110 UNFAITHFUL
```

- u022b: Positive and combined readings add an active obligation to secure liberty beyond the stated right to liberty.
- u022c: The combined reading adds an obligation to enable exercise of the right to security of person, which the words do not specify.
- u027: Lists whether punishment is covered as unsettled, although the source explicitly includes treatment or punishment.
- u035: The tribunal claim requires every competent national tribunal to provide a remedy for every qualifying violation; the source grants a remedy through competent tribunals without this universal distribution.
- u048: Positive and combined readings require enabling movement and residence, adding provision beyond the stated freedom.
- u066: The combined reading requires enabling exercise of thought, conscience and religion, beyond the stated right to those freedoms.
- u070: The combined reading requires enabling exercise of opinion and expression, beyond the stated right to those freedoms.
- u073: The combined reading requires enabling peaceful assembly and association, beyond the stated right to those freedoms.
- u081: The resources reading imports a qualification from the separate entitlement to realization of rights and also drops “organization” from that qualification.
- u084a: Positive and combined readings require everyone to be provided with work, strengthening the right to work into a job-provision obligation.
- u084b: The combined reading adds an obligation to enable exercise of free employment choice, beyond the stated freedom of choice.
- u087: The positive reading requires enabling union formation and membership, adding assistance beyond the stated right.
- u098: Makes attendance obligatory only if education is already compulsory for someone, allowing no compulsory education at all; also invents the question of who makes it compulsory.
- u100b: Labels the meaning with an open question about rights and freedoms set forth in this Declaration, although the source refers generally to human rights and fundamental freedoms.
- u105a: Positive and combined readings require enabling cultural participation, adding assistance beyond the stated right to participate freely.
- u105c: Positive and combined readings require enabling participation in scientific advancement and its benefits, adding an obligation the words do not specify.
- u110: Lists whether a community permitting full development exists as unsettled, although the source takes that community’s existence for granted.

Writing `AUDIT-FULL.md` failed: the destination is on a read-only filesystem. No files changed or model calls made.
## Full audit of the remaining covered units (one-off, 2026-10-08; these verdicts count as audit-verified like the sampled ones)
Faithful: 17/34.

VERDICTS:
```text
u018 FAITHFUL
u022b UNFAITHFUL
u022c UNFAITHFUL
u025 FAITHFUL
u027 UNFAITHFUL
u029 FAITHFUL
u033a FAITHFUL
u035 UNFAITHFUL
u037 FAITHFUL
u045a FAITHFUL
u045b FAITHFUL
u048 UNFAITHFUL
u051 FAITHFUL
u059 FAITHFUL
u064 FAITHFUL
u066 UNFAITHFUL
u070 UNFAITHFUL
u073 UNFAITHFUL
u077 FAITHFUL
u081 UNFAITHFUL
u084a UNFAITHFUL
u084b UNFAITHFUL
u084c FAITHFUL
u084d FAITHFUL
u087 UNFAITHFUL
u096 FAITHFUL
u098 UNFAITHFUL
u099a FAITHFUL
u099b FAITHFUL
u100a FAITHFUL
u100b UNFAITHFUL
u105a UNFAITHFUL
u105c UNFAITHFUL
u110 UNFAITHFUL
```

- u022b: Positive and combined readings add an active obligation to secure liberty beyond the stated right to liberty.
- u022c: The combined reading adds an obligation to enable exercise of the right to security of person, which the words do not specify.
- u027: Lists whether punishment is covered as unsettled, although the source explicitly includes treatment or punishment.
- u035: The tribunal claim requires every competent national tribunal to provide a remedy for every qualifying violation; the source grants a remedy through competent tribunals without this universal distribution.
- u048: Positive and combined readings require enabling movement and residence, adding provision beyond the stated freedom.
- u066: The combined reading requires enabling exercise of thought, conscience and religion, beyond the stated right to those freedoms.
- u070: The combined reading requires enabling exercise of opinion and expression, beyond the stated right to those freedoms.
- u073: The combined reading requires enabling peaceful assembly and association, beyond the stated right to those freedoms.
- u081: The resources reading imports a qualification from the separate entitlement to realization of rights and also drops “organization” from that qualification.
- u084a: Positive and combined readings require everyone to be provided with work, strengthening the right to work into a job-provision obligation.
- u084b: The combined reading adds an obligation to enable exercise of free employment choice, beyond the stated freedom of choice.
- u087: The positive reading requires enabling union formation and membership, adding assistance beyond the stated right.
- u098: Makes attendance obligatory only if education is already compulsory for someone, allowing no compulsory education at all; also invents the question of who makes it compulsory.
- u100b: Labels the meaning with an open question about rights and freedoms set forth in this Declaration, although the source refers generally to human rights and fundamental freedoms.
- u105a: Positive and combined readings require enabling cultural participation, adding assistance beyond the stated right to participate freely.
- u105c: Positive and combined readings require enabling participation in scientific advancement and its benefits, adding an obligation the words do not specify.
- u110: Lists whether a community permitting full development exists as unsettled, although the source takes that community’s existence for granted.

Writing `AUDIT-FULL.md` failed: the destination is on a read-only filesystem. No files changed or model calls made.