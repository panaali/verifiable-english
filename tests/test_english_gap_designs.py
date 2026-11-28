"""English-gap test cases: must/may wording (A), numbers (B), time phrases (C) and passives (D), from 40 real source
sentences (row english-gap-tests-build; designs 1-40 of the english-gap design review of 2026-11-28, each read by two
independent seats; the four disputed designs C3, C8, D6 and D10 are used only in the stricter form the DRI chose,
decide wake 1124Z item 2).

Each case is a plain text for `ve read` (ve/plain_read.py): the source's own sentence(s), quoted exactly (the quote
is the rule), then the case's facts in plain English, then one question. Its expected outcome is the design's answer:
"Yes" or "No", or REFUSE (the design says the words do not settle it: VE must not answer Yes or No). The case ID
starts with its design ID (A1 to D10), and the source each quote is copied from is named in `source`.

Main's plain reader reads only a few sentence shapes (tour stop 12), so it refuses every one of these texts whole.
A REFUSE case therefore passes on main: that pass is a guard (a later reader that reads these sentences must still
not commit to an answer here), not evidence that main sees the ambiguity. Every Yes/No case not in ANSWERED is a
strict xfail with the reason "english-gap <id>: ..." (allowed by its row in tools/gate-optional.json): it turns into
an XPASS failure,
and must lose its mark, as soon as the reader answers it right. Those xfail IDs are the build queue.
"""
from __future__ import annotations

from dataclasses import dataclass

import pytest

from ve.plain_read import read

YES, NO, REFUSE = "Yes", "No", "refuse"
# A REFUSE case passes when VE gives neither Yes nor No: the text is refused, or the answer is left open.
NOT_COMMITTED = {"refused", "not determined", "no answer"}


@dataclass(frozen=True)
class Case:
    ident: str      # "<design id>-<n>"
    source: str     # the corpus file and lines the quote is copied from
    rule: str       # the quoted source sentence(s), exactly
    facts: str      # the case's facts, plain English
    question: str   # one yes/no question
    expect: str     # YES, NO or REFUSE
    why: str        # the design's reason, one line

    @property
    def design(self) -> str:
        return self.ident.split("-")[0]

    @property
    def text(self) -> str:
        return f"{self.rule}\n{self.facts}\n{self.question}\n"


# ---- the quoted rules (each exactly as in its source; "[...]" never appears inside a quoted line) ----

HOS_LEAD = ("(a) Except as otherwise provided in § 395.1, no motor carrier shall permit or require any driver used by "
            "it to drive a property-carrying commercial motor vehicle, nor shall any such driver drive a "
            "property-carrying commercial motor vehicle, regardless of the number of motor carriers using the "
            "driver's services, unless the driver complies with the following requirements:")
A1 = HOS_LEAD + "\n(1) Start of work shift. A driver may not drive without first taking 10 consecutive hours off duty;"
A2 = (HOS_LEAD + "\n(1) Start of work shift. A driver may not drive without first taking 10 consecutive hours off duty;"
      "\n(2) 14-hour period. A driver may not drive after a period of 14 consecutive hours after coming on-duty "
      "following 10 consecutive hours off-duty."
      "\n(3) Driving time and interruptions of driving periods—(i) Driving time. A driver may drive a total of 11 "
      "hours during the period specified in paragraph (a)(2) of this section.")
A3 = ("Beta Previews may not be supported and may be changed at any time without notice. In addition, Beta Previews "
      "are not subject to the same security measures and auditing to which the Service has been and is subject. By "
      "using a Beta Preview, you use it at your own risk.")
A4 = ("(4) If the trader gives the consumer the option of filling in and submitting such a form or other statement on "
      "the trader's website—\n(a)the consumer need not use it, but\n(b)if the consumer does, the trader must "
      "communicate to the consumer an acknowledgement of receipt of the cancellation on a durable medium without "
      "delay.")
A4_32_3 = ("(3) To inform the trader under paragraph (2) the consumer may either—\n(a)use a form following the "
           "model cancellation form in part B of Schedule 3, or\n(b)make any other clear "
           "statement setting out the decision to cancel the contract.")
A5 = ("(1)An employer to whom an application under section 80F is made—\n(b)shall only refuse the application because "
      "he considers that one or more of the following grounds applies—")
A6 = ("(1)A landlord must not require a relevant person to make a prohibited payment to the landlord in connection "
      "with a tenancy of housing in England.")
A7 = ("(b) Operations not requiring a medical certificate. A person is not required to hold a medical certificate—\n"
      "(1) When exercising the privileges of a student pilot certificate while seeking—\n"
      "(i) A sport pilot certificate with glider or balloon privileges; or")
A8 = ("(9) If (in the case of a sales contract) the value of the goods is diminished by any amount as a result of "
      "handling of the goods by the consumer beyond what is necessary to establish the nature, characteristics and "
      "functioning of the goods, the trader may recover that amount from the consumer, up to the contract price.")
A9 = ("5. The compensation shall be paid within 1 month after the submission of the request for compensation. The "
      "compensation may be paid in vouchers and/or other services, provided that the conditions are flexible, "
      "particularly regarding the period of validity and the destination. The compensation shall be paid in money at "
      "the request of the passenger.")
A10 = ("(1)Where—\n(a)a person is convicted of an offence to which this subsection applies, and\n(b)the penalty points "
       "to be taken into account on that occasion number twelve or more,\nthe court must order him to be disqualified "
       "for not less than the minimum period unless the court is satisfied, having regard to all the circumstances, "
       "that there are grounds for mitigating the normal consequences of the conviction and thinks fit to order him "
       "to be disqualified for a shorter period or not to order him to be disqualified.")

B1 = ("(2) Has been employed for at least 1,250 hours of service during the 12-month period immediately preceding the "
      "commencement of the leave (see § 825.801 for special hours of service requirements for airline flight crew "
      "employees), and")
B2 = ("(1) Subject to the exceptions provided in paragraph (b)(2) of this section, employment periods prior to a break "
      "in service of seven years or more need not be counted in determining whether the employee has been employed "
      "by the employer for at least 12 months.\n(2) Employment periods preceding a break in service of more than "
      "seven years must be counted in determining whether the employee has been employed by the employer for at "
      "least 12 months where:")
B3 = ("(b)the penalty points to be taken into account on that occasion number twelve or more,\n(2)The minimum period "
      "referred to in subsection (1) above is—\n(a)six months if no previous disqualification imposed on the "
      "offender is to be taken into account, and\n(b)one year if one, and two years if more than one, such "
      "disqualification is to be taken into account;")
B4 = ("1. Without losing the right to transport, passengers may request compensation from the carrier if they are "
      "facing a delay in arrival at the final destination as set out in the transport contract. The minimum level of "
      "compensation shall be 25 % of the ticket price for a delay of at least:\n(a) 1 hour in the case of a scheduled "
      "journey of up to 4 hours;\n(b) 2 hours in the case of a scheduled journey of more than 4 hours, but not "
      "exceeding 8 hours;\n(c) 3 hours in the case of a scheduled journey of more than 8 hours, but not exceeding 24 "
      "hours; or\n(d) 6 hours in the case of a scheduled journey of more than 24 hours.\nIf the delay exceeds double "
      "the time set out in points (a) to (d), the compensation shall be 50 % of the ticket price.")
B5 = ("6. The compensation of the ticket price shall not be reduced by financial transaction costs such as fees, "
      "telephone costs or stamps. Carriers may introduce a minimum threshold under which payments for compensation "
      "will not be paid. This threshold shall not exceed EUR 6.")
B6 = ("(3)But if the amount of the tenancy deposit exceeds—\n(a)the amount of five weeks' rent, where the annual rent "
      "in respect of the tenancy immediately after its grant, renewal or continuance is less than £50,000, or\n(b)the "
      "amount of six weeks' rent, where the annual rent in respect of the tenancy immediately after its grant, "
      "renewal or continuance is £50,000 or more,\nthe amount of the excess is a prohibited payment.\n(c)“one week's "
      "rent” means the amount of the annual rent payable in respect of the tenancy immediately after its grant, "
      "renewal or continuance divided by 52.")
B7 = ("6(1)A payment is a permitted payment if it is a payment—E+W\n(a)to a landlord in consideration of the "
      "variation, "
      "assignment or novation of a tenancy at the tenant's request, or\n(b)to a letting agent in consideration of "
      "arranging the variation, assignment or novation of a tenancy at the tenant's request.\n(2)But if the amount "
      "of the payment exceeds the greater of—\n(a)£50, or\n(b)the reasonable costs of the person to whom the payment "
      "is to be made in respect of the variation, assignment or novation of the tenancy,\nthe amount of the excess "
      "is a prohibited payment.")
B8 = ("(1)A person's qualifying earnings in a pay reference period of 12 months are the part (if any) of the gross "
      "earnings payable to that person in that period that is—\n(a)more than £6,240, and\n(b)not more than £50,270.")
B9 = ("(1)Apprenticeship levy is charged if—\n(a)a person has a pay bill for a tax year, and\n(b)the relevant "
      "percentage of that pay bill exceeds the amount of the person's levy allowance (if any) for that tax year.\n"
      "(2)The amount charged for the tax year is equal to—\n[FORMULA, an image in the official text "
      "(ukpga_20160024_en_sld_012.gif, pinned in raw/), transcribed by the selector: N - A]\nwhere—\n"
      "N is the relevant percentage of the pay bill for the tax year, and\nA is the amount of the levy allowance "
      "(if any) to which the person is entitled for the tax year.\n(4)Except so far as section 103 provides otherwise, "
      "a person who has a pay bill for a tax year is entitled to a levy allowance for the tax year.\n"
      "(5)The amount of the levy allowance is £15,000 "
      "(except where section 101 or 102 provides otherwise).\n(6)For the purposes of this section the “relevant "
      "percentage” is 0.5%.")
B10 = ("GitHub Apps authenticating with an installation access token use the installation's minimum rate limit of "
       "5,000 "
       "requests per hour. If the installation is on a GitHub Enterprise Cloud organization, the installation has a "
       "rate limit of 15,000 requests per hour.\nFor installations that are not on a GitHub Enterprise Cloud "
       "organization, the rate limit for the installation will scale with the number of users and repositories. "
       "Installations that have more than 20 repositories receive another 50 requests per hour for each repository. "
       "Installations that are on an organization that have more than 20 users receive another 50 requests per hour "
       "for each user. The rate limit cannot increase beyond 12,500 requests per hour.")

C1 = ("(b) Implementation specification: Timeliness of notification. Except as provided in § 164.412, a covered entity "
      "shall provide the notification required by paragraph (a) of this section without unreasonable delay and in no "
      "case later than 60 calendar days after discovery of a breach.")
C2 = ("(c) Implementation specifications: Breaches involving less than 500 individuals. For breaches of unsecured "
      "protected health information involving less than 500 individuals, a covered entity shall maintain a log or "
      "other documentation of such breaches and, not later than 60 days after the end of each calendar year, provide "
      "the notification required by paragraph (a) of this section for breaches discovered during the preceding "
      "calendar year, in the manner specified on the HHS web site.")
C3 = ("(4) The consumer must send off the goods under paragraph (2)(a), or hand them over under paragraph (2)(b), "
      "without undue delay and in any event not later than 14 days after the day on which the consumer informs the "
      "trader as required by regulation 32(2).")
C4 = ("2(1)In this Schedule “the deadline for agreement” means the fifteenth day of the period beginning with the day "
      "on which the landlord or letting agent receives the holding deposit.E+W\n(2)But the landlord or the letting "
      "agent may agree with the tenant in writing that a different day is to be the deadline for agreement for the "
      "purposes of this Schedule.")
C5 = ("(2)In this paragraph “relevant default” means—\n(a)the loss of a key to, or other security device giving access "
      "to, the housing to which the tenancy relates, or\n(b)a failure to make a payment of rent in full before the "
      "end of the period of 14 days beginning with the date (“the due date”) on which the payment is required to be "
      "made in accordance with the tenancy agreement.")
C6 = ("(4)An employee may not—\n(a)make more than two applications under this section to the same employer during any "
      "period of 12 months;\n(b)make an application under this section to an employer if another such application to "
      "the same employer is proceeding.")
C7 = ("(1C)An agreement to extend the decision period in a particular case may be made—\n(a)before it ends, or\n"
      "(b)with retrospective effect, before the end of a period of three months beginning with the day after that on "
      "which the decision period that is being extended came to an end.")
C8 = ("An applicant for a knowledge test who fails that test may not reapply for the test for 14 calendar days after "
      "failing the test.")
C9 = ("and a previous disqualification imposed on an offender is , subject to subsection (2A), to be taken into "
      "account "
      "if it was for a fixed period of 56 days or more and was imposed within the three years immediately preceding "
      "the commission of the latest offence in respect of which penalty points are taken into account under section "
      "29 of this Act.")
C10 = ("(b) No motor carrier shall permit or require a driver of a property-carrying commercial motor vehicle to "
       "drive, "
       "nor shall any driver drive a property-carrying commercial motor vehicle, regardless of the number of motor "
       "carriers using the driver's services, for any period after—\n(1) Having been on duty 60 hours in any period "
       "of 7 consecutive days if the employing motor carrier does not operate commercial motor vehicles every day of "
       "the week; or\n(2) Having been on duty 70 hours in any period of 8 consecutive days if the employing motor "
       "carrier operates commercial motor vehicles every day of the week.\n(c)(1) Any period of 7 consecutive days "
       "may end with the beginning of an off-duty period of 34 or more consecutive hours.")

D1 = ("(3) Is employed at a worksite where 50 or more employees are employed by the employer within 75 miles of that "
      "worksite. See § 825.105(b) regarding employees who work outside the U.S.")
D2 = ("(e) Whether 50 employees are employed within 75 miles to ascertain an employee's eligibility for FMLA benefits "
      "is determined when the employee gives notice of the need for leave. Whether the leave is to be taken at one "
      "time or on an intermittent or reduced leave schedule basis, once an employee is determined eligible in "
      "response to that notice of the need for leave, the employee's eligibility is not affected by any subsequent "
      "change in the number of employees employed at or within 75 miles of the employee's worksite, for that "
      "specific notice of the need for leave.")
D3 = ("(2) Breaches treated as discovered. For purposes of paragraph (a)(1) of this section, a breach shall be treated "
      "as discovered by a business associate as of the first day on which such breach is known to the business "
      "associate or, by exercising reasonable diligence, would have been known to the business associate. A business "
      "associate shall be deemed to have knowledge of a breach if the breach is known, or by exercising reasonable "
      "diligence would have been known, to any person, other than the person committing the breach, who is an "
      "employee, officer, or other agent of the business associate (determined in accordance with the Federal common "
      "law of agency).")
D4 = ("(5) Where the consumer informs the trader under paragraph (2) by sending a communication, the consumer is to be "
      "treated as having cancelled the contract in the cancellation period if the communication is sent before the "
      "end of the period.")
D5 = ("(1D)An application under section 80F is to be treated as having been withdrawn by the employee if—\n(a)the "
      "employee without good reason has failed to attend both the first meeting arranged by the employer to discuss "
      "the application and the next meeting arranged for that purpose, or\n(b)where the employer allows the employee "
      "to appeal a decision to reject an application or to make a further appeal, the employee without good reason "
      "has failed to attend both the first meeting arranged by the employer to discuss the appeal and the next "
      "meeting arranged for that purpose,\nand the employer has notified the employee that the employer has decided "
      "to treat that conduct of the employee as a withdrawal of the application.")
D6 = ("This Agreement may only be modified by a written amendment signed by an authorized representative of GitHub, or "
      "by the posting by GitHub of a revised version in accordance with Section R. Changes to These Terms. These Terms "
      "of Service, together with the GitHub Privacy Statement, represent the complete and exclusive statement of the "
      "agreement between you and us. This Agreement supersedes any proposal or prior agreement oral or written, and "
      "any other communications between you and GitHub relating to the subject matter of these terms including any "
      "confidentiality or nondisclosure agreements.")
D7 = ("(9)In this Act “relevant person” means—\n(a)a tenant, or\n(b)subject to subsection (10), a person acting on "
      "behalf of, or who has guaranteed the payment of rent by, a tenant.\n(10)The reference in subsection (9)(b) to a "
      "person does not include—\n(a)a local housing authority within the meaning of the Housing Act 1985 (see section "
      "1 of that Act),\n(b)the Greater London Authority, or\n(c)a person acting on behalf of an authority within "
      "paragraph (a) or the Greater London Authority.")
D8 = ("(1)This section applies to a jobholder—\n(a)who is aged at least 22,\n(b)who has not reached pensionable age, "
      "and\n(c)to whom earnings of more than £10,000 are payable by the employer in the relevant pay reference period "
      "(see section 15).")
D8_1_2 = ("(2)Where a jobholder has more than one employer, or a succession of employers, this Chapter applies "
          "separately in "
          "relation to each employment.")
D9 = ("3E+WSubject as follows, the person who received the holding deposit must repay it if—\n(a)the landlord and the "
      "tenant enter into a tenancy agreement relating to the housing,\n(b)the landlord decides before the deadline for "
      "agreement not to enter into a tenancy agreement relating to the housing, or\n(c)the landlord and the tenant "
      "fail to enter into a tenancy agreement relating to the housing before the deadline for agreement.\n4E+WIf "
      "paragraph 3 applies, the deposit must be repaid within the period of 7 days beginning with—\n(a)where "
      "paragraph 3(a) applies, the date of the tenancy agreement,\n(b)where paragraph 3(b) applies, the date on which "
      "the landlord decides not to enter into the tenancy agreement, or\n(c)where paragraph 3(c) applies, the "
      "deadline for agreement.")
D10 = ("1GE(1)Sub-paragraph (2) applies for the purpose of determining the rate at which vehicle excise duty is to be "
       "paid on any other vehicle licence for a vehicle to which this Part applies if—\n(a)the price of the vehicle "
       "exceeds the applicable amount,\n(b)the vehicle was first registered, under this Act or under the law of a "
       "country or territory outside the United Kingdom, less than six years before the date on which the licence "
       "has effect, and\n(c)either—\n(i)the vehicle was so registered on or after 1 April 2025, or\n(ii)it was so "
       "registered before that date and its applicable CO2 emissions figure exceeds 0g/km.")

HOS = "stock/hos-driving/source.txt"
CANCEL = "batch5/uk-consumer-cancellation/source.txt"
FLEX = "batch5/uk-flexible-working/source.txt"
FEES = "tenant-fees/source.txt"
SEA = "stock/eu-sea-passengers/source.txt"
TOT = "stock/totting-up/source.txt"
FMLA = "stock/fmla-eligibility/source.txt"
HIPAA = "batch4/hipaa-breach-notice/source.txt"
PENS = "batch4/pensions-auto-enrolment/source.txt"

CASES = [
    # ---- Gap A: must / may / shall wording ----
    Case("A1-1", f"{HOS} L3-L4", A1,
         "The driver was off duty from 20:00 to 02:00. The driver was on duty from 02:00 to 03:00. The driver was off "
         "duty from 03:00 to 07:00. The driver wants to start driving at 07:00.",
         "Does paragraph (1) permit the driver to start driving at 07:00?", NO,
         "6 h + 4 h off is not 10 consecutive hours"),
    Case("A1-2", f"{HOS} L3-L4", A1,
         "The driver was off duty from 20:00 to 06:00. The driver starts driving at 06:00.",
         "Does paragraph (1) permit the driver to start driving at 06:00?", YES, "10 consecutive hours exactly"),
    Case("A1-3", f"{HOS} L3-L4", A1,
         "The driver was off duty from 20:00 to 02:00. The driver was on duty from 02:00 to 03:00. The driver was off "
         "duty from 03:00 to 07:00. The driver says that an exception in § 395.1 lets the driver drive at 07:00.",
         "Is the driver allowed to drive at 07:00?", REFUSE,
         "edge case: § 395.1 is outside the text: not decided by these words"),
    Case("A2-1", f"{HOS} L3-L6", A2,
         "The driver came on duty at 06:00 after 10 consecutive hours off duty. By 19:00 the driver has driven a "
         "total of 11 hours.",
         "Is the driver permitted to drive from 19:30 to 20:00?", NO, "the 11-hour total is reached"),
    Case("A2-2", f"{HOS} L3-L6", A2,
         "The driver came on duty at 06:00 after 10 consecutive hours off duty. By 20:30 the driver has driven a "
         "total of 9 hours.",
         "Is the driver permitted to drive at 20:30?", NO, "outside the 14-hour period of (a)(2), though under 11 h"),
    Case("A2-3", f"{HOS} L3-L6", A2, "The driver came on duty at 06:00 after 10 consecutive hours off duty.",
         "Must the motor carrier let the driver drive 11 hours?", NO, "'may drive' is a ceiling, not an entitlement"),
    Case("A3-1", "batch5/github-tos-accounts/source.txt L156", A3, "A user uses a Beta Preview.",
         "Is GitHub prohibited from supporting the Beta Preview?", NO, "epistemic 'may not', not a prohibition"),
    Case("A3-2", "batch5/github-tos-accounts/source.txt L156", A3, "A user uses a Beta Preview.",
         "Does GitHub promise support for the Beta Preview?", NO, "'may not be supported' promises nothing"),
    Case("A3-3", "batch5/github-tos-accounts/source.txt L156", A3,
         "GitHub changed a Beta Preview without notice.",
         "Did GitHub breach these words by changing the Beta Preview without notice?", NO,
         "'may be changed at any time without notice' reserves that liberty"),
    Case("A4-1", f"{CANCEL} L42-L47", A4_32_3 + "\n" + A4,
         "The trader gives the consumer the option of submitting a cancellation form on the trader's website. The "
         "consumer cancels by e-mail with a clear statement setting out the decision to cancel the contract.",
         "Must the trader communicate an acknowledgement of receipt of the cancellation under paragraph (4)(b)?", NO,
         "(4)(b) applies only if the consumer uses the website form"),
    Case("A4-2", f"{CANCEL} L42-L47", A4_32_3 + "\n" + A4,
         "The trader gives the consumer the option of submitting a cancellation form on the trader's website. The "
         "consumer cancels by e-mail with a clear statement setting out the decision to cancel the contract.",
         "Is the consumer's cancellation by e-mail a valid way to cancel?", YES,
         "'need not use it'; a clear statement is a route of reg 32(3)(b)"),
    Case("A4-3", f"{CANCEL} L45-L47", A4,
         "The trader gives the consumer the option of submitting a cancellation form on the trader's website. The "
         "consumer submits the cancellation form on the trader's website.",
         "Must the trader communicate an acknowledgement of receipt of the cancellation on a durable medium without "
         "delay?", YES, "the consumer used the website form"),
    Case("A5-1", f"{FLEX} L50, L54", A5,
         "The employer considers that the burden of additional costs ground applies. The employer grants the "
         "application.", "Is the employer in breach of paragraph (1)(b)?", NO,
         "'shall only refuse because' restricts refusal; it does not require it"),
    Case("A5-2", f"{FLEX} L50, L54", A5,
         "The employer refuses the application because it dislikes home working. The employer does not consider that "
         "any listed ground applies.", "Is the employer in breach of paragraph (1)(b)?", YES,
         "refusal on a reason that is no listed ground"),
    Case("A6-1", f"{FEES} L4", A6,
         "The landlord makes a £150 admin fee a condition of granting a tenancy of housing in England. The admin fee "
         "is a prohibited payment. The tenant's guarantor is a relevant person. The guarantor pays the admin fee to "
         "the landlord.", "Is the landlord in breach of subsection (1)?", YES,
         "requiring a relevant person (a guarantor) to pay a prohibited payment"),
    Case("A6-2", f"{FEES} L4", A6,
         "The landlord makes a £150 admin fee a condition of granting a tenancy of housing in Wales. The admin fee is "
         "a prohibited payment.", "Does subsection (1) apply to this tenancy?", NO, "England only"),
    Case("A7-1", "dl/cfr61/full.txt L16-L18", A7,
         "A student pilot is seeking a sport pilot certificate with glider privileges. The student pilot flies a "
         "glider solo, exercising the privileges of the student pilot certificate, without a medical certificate.",
         "Is the student pilot required by paragraph (b) to hold a medical certificate?", NO,
         "the duty is removed for this case"),
    Case("A7-2", "dl/cfr61/full.txt L16-L18", A7,
         "A student pilot is seeking a sport pilot certificate with glider privileges. The student pilot holds a "
         "valid medical certificate.", "Does the student pilot breach paragraph (b) by holding a medical "
         "certificate?", NO, "'is not required to hold' does not forbid holding"),
    Case("A7-3", "dl/cfr61/full.txt L16-L18", A7,
         "A student pilot is seeking a private pilot certificate for aeroplanes. The student pilot flies solo "
         "without a medical certificate.",
         "Is the student pilot exempt from holding a medical certificate?", REFUSE,
         "this paragraph does not cover it; the answer depends on other paragraphs"),
    Case("A8-1", f"{CANCEL} L70", A8,
         "The contract is a sales contract. The contract price is £100. The value of the goods is diminished by £30 "
         "as a result of handling of the goods by the consumer beyond what is necessary to establish their nature, "
         "characteristics and functioning.", "May the trader recover £30 from the consumer?", YES,
         "a permission, within the cap"),
    Case("A8-2", f"{CANCEL} L70", A8,
         "The contract is a sales contract. The contract price is £100. The value of the goods is diminished by £30 "
         "as a result of handling of the goods by the consumer beyond what is necessary to establish their nature, "
         "characteristics and functioning.", "Must the trader recover £30 from the consumer?", NO,
         "'may recover' is a permission, not a duty"),
    Case("A8-3", f"{CANCEL} L70", A8,
         "The contract is a sales contract. The contract price is £100. The value of the goods is diminished by £120 "
         "as a result of handling of the goods by the consumer beyond what is necessary to establish their nature, "
         "characteristics and functioning.", "May the trader recover more than £100 from the consumer?", NO,
         "capped at the contract price"),
    Case("A8-4", f"{CANCEL} L70", A8,
         "The contract is a sales contract. The contract price is £100. The value of the goods is diminished only as "
         "a result of handling that was necessary to establish how the goods function.",
         "May the trader recover any amount from the consumer under paragraph (9)?", NO,
         "necessary handling gives nothing"),
    Case("A9-1", f"{SEA} L51", A9,
         "The passenger requests the compensation in money. The carrier offers vouchers with flexible conditions.",
         "Must the carrier pay the compensation in money?", YES, "the passenger's request for money overrides"),
    Case("A9-2", f"{SEA} L51", A9,
         "The passenger makes no request about the form of the compensation. The carrier pays the compensation in "
         "vouchers valid for 2 weeks for one route only.", "Is the carrier allowed to pay the compensation in these "
         "vouchers?", NO, "the conditions are not flexible"),
    Case("A9-3", f"{SEA} L51", A9,
         "The request for compensation was submitted on 3 March. The compensation was paid on 10 April.",
         "Was the compensation paid in time?", NO, "1 month after 3 March is 3 April"),
    Case("A10-1", f"{TOT} L5-L8", A10,
         "A person is convicted of an offence to which this subsection applies. The penalty points to be taken into "
         "account number 12. The court finds no grounds for mitigating the normal consequences of the conviction.",
         "Must the court order the person to be disqualified for not less than the minimum period?", YES,
         "both conditions hold, no mitigation"),
    Case("A10-2", f"{TOT} L5-L8", A10,
         "A person is convicted of an offence to which this subsection applies. The penalty points to be taken into "
         "account number 11.", "Does subsection (1) require the court to disqualify the person?", NO,
         "11 points does not trigger (1)"),
    Case("A10-3", f"{TOT} L5-L8", A10,
         "A person is convicted of an offence to which this subsection applies. The penalty points to be taken into "
         "account number 12. The court is satisfied that there are grounds for mitigating the normal consequences of "
         "the conviction. The court orders the person to be disqualified for the full minimum period.",
         "Is the court's order lawful under these words?", YES,
         "finding mitigating grounds does not oblige a shorter period"),

    # ---- Gap B: numbers ----
    Case("B1-1", f"{FMLA} L5", B1,
         "The employee has 1,250 hours of service during the 12-month period immediately preceding the commencement "
         "of the leave.", "Is the condition in paragraph (2) met?", YES, "'at least' includes 1,250"),
    Case("B1-2", f"{FMLA} L5", B1,
         "The employee has 1,249 hours of service during the 12-month period immediately preceding the commencement "
         "of the leave.", "Is the condition in paragraph (2) met?", NO, "1,249 is under 1,250"),
    Case("B1-3", f"{FMLA} L5", B1,
         "The employee has 1,400 hours of service in total. 300 of those hours were worked 13 to 14 months before the "
         "commencement of the leave.", "Is the condition in paragraph (2) met?", NO,
         "only 1,100 hours fall in the 12-month window"),
    Case("B2-1", f"{FMLA} L8-L9", B2,
         "The employee had a break in service of 8 years. The employee has a written rehire agreement, which is one "
         "of the conditions listed in paragraph (2).",
         "Must the employment period before the break be counted?", YES, "more than seven years, a listed condition"),
    Case("B2-2", f"{FMLA} L8-L9", B2,
         "The employee had a break in service of 6 years. The employee has no written rehire agreement.",
         "Does the employment period before the break count toward the 12 months?", YES, "no exclusion applies"),
    Case("B2-3", f"{FMLA} L8-L9", B2,
         "The employee had a break in service of exactly 7 years. The employee has a written rehire agreement, which "
         "is one of the conditions listed in paragraph (2).",
         "Must the employment period before the break be counted under paragraph (2)?", NO,
         "boundary: exactly 7 years is 'seven years or more' but not 'more than seven years' (literal answer)"),
    Case("B3-1", f"{TOT} L7, L12-L14", B3,
         "The penalty points to be taken into account number 12. No previous disqualification is to be taken into "
         "account.", "Is the minimum period six months?", YES, "none counted gives 6 months"),
    Case("B3-2", f"{TOT} L7, L12-L14", B3,
         "The penalty points to be taken into account number 14. One previous disqualification is to be taken into "
         "account.", "Is the minimum period one year?", YES, "one counted gives 1 year"),
    Case("B3-3", f"{TOT} L7, L12-L14", B3,
         "The penalty points to be taken into account number 12. Three previous disqualifications are to be taken "
         "into account.", "Is the minimum period two years?", YES, "more than one gives 2 years, not 3"),
    Case("B3-4", f"{TOT} L7, L12-L14", B3, "The penalty points to be taken into account number 11.",
         "Is the condition in subsection (1)(b) met?", NO, "11 is under twelve"),
    Case("B4-1", f"{SEA} L42-L47", B4, "The scheduled journey is 4 hours. The delay in arrival is 1 hour.",
         "Is the minimum compensation 25 % of the ticket price?", YES, "a 4-hour journey is band (a)"),
    Case("B4-2", f"{SEA} L42-L47", B4, "The scheduled journey is 4 hours. The delay in arrival is exactly 2 hours.",
         "Is the compensation 50 % of the ticket price?", NO, "exactly double does not 'exceed double'"),
    Case("B4-3", f"{SEA} L42-L47", B4,
         "The scheduled journey is 4 hours. The delay in arrival is 2 hours and 1 minute.",
         "Is the compensation 50 % of the ticket price?", YES, "over double the 1-hour threshold"),
    Case("B4-4", f"{SEA} L42-L47", B4,
         "The scheduled journey is 5 hours. The delay in arrival is 1 hour and 30 minutes.",
         "Is the passenger owed compensation under paragraph 1?", NO, "band (b) needs 2 hours"),
    Case("B4-5", f"{SEA} L42-L47", B4, "The scheduled journey is 24 hours. The delay in arrival is 3 hours.",
         "Is the minimum compensation 25 % of the ticket price?", YES, "a 24-hour journey is band (c)"),
    Case("B5-1", f"{SEA} L52", B5,
         "The carrier has a minimum threshold of EUR 6. The compensation due is EUR 5.50.",
         "Will the compensation be paid?", NO, "under the threshold"),
    Case("B5-2", f"{SEA} L52", B5,
         "The carrier has a minimum threshold of EUR 6. The compensation due is EUR 6.00.",
         "Will the compensation be paid?", YES, "equal to the threshold is not 'under' it"),
    Case("B5-3", f"{SEA} L52", B5, "The carrier introduces a minimum threshold of EUR 8.",
         "Is the carrier allowed to introduce this threshold?", NO, "the threshold shall not exceed EUR 6"),
    Case("B5-4", f"{SEA} L52", B5,
         "The compensation due is EUR 20. The carrier pays EUR 18.50 after deducting a EUR 1.50 bank fee.",
         "Is the carrier allowed to deduct the bank fee?", NO, "no deduction for transaction costs"),
    Case("B6-1", f"{FEES} L114-L117, L121", B6,
         "The annual rent immediately after the grant of the tenancy is £26,000. The tenancy deposit is £3,000.",
         "Is the prohibited payment exactly £500?", YES, "week £500, five-week cap £2,500, excess £500"),
    Case("B6-2", f"{FEES} L114-L117, L121", B6,
         "The annual rent immediately after the grant of the tenancy is £26,000. The tenancy deposit is £3,000.",
         "Is the whole deposit a prohibited payment?", NO, "trap: only the excess is prohibited"),
    Case("B6-3", f"{FEES} L114-L117, L121", B6,
         "The annual rent immediately after the grant of the tenancy is £50,000. The tenancy deposit is £5,500.",
         "Is any part of the deposit a prohibited payment?", NO, "£50,000 is the six-week band: cap £5,769.23"),
    Case("B6-4", f"{FEES} L114-L117, L121", B6,
         "The annual rent immediately after the grant of the tenancy is £49,999. The tenancy deposit is £5,500.",
         "Is the prohibited payment £692.40, to the nearest penny?", YES,
         "five-week cap £4,807.60 (a 1p rounding tolerance is allowed by the design)"),
    Case("B7-1", f"{FEES} L164-L170", B7,
         "The landlord charges £60 for a variation of the tenancy at the tenant's request. The landlord's reasonable "
         "costs are £30.", "Is the prohibited payment exactly £10?", YES, "the cap is the greater figure, £50"),
    Case("B7-2", f"{FEES} L164-L170", B7,
         "The landlord charges £80 for a variation of the tenancy at the tenant's request. The landlord's reasonable "
         "costs are £80.", "Is any part of the payment a prohibited payment?", NO, "£80 does not exceed £80"),
    Case("B7-3", f"{FEES} L164-L170", B7,
         "The landlord charges £100 for a variation of the tenancy at the tenant's request. The landlord's "
         "reasonable costs are £80.", "Is the prohibited payment exactly £20?", YES, "100 - 80"),
    Case("B7-5", f"{FEES} L164-L170", B7,
         "The landlord charges £100 for a variation of the tenancy at the tenant's request. The landlord's "
         "reasonable costs are £80.", "Is the prohibited payment exactly £50?", NO,
         "trap: £50 is not a fixed cap; the cap is the greater figure, £80"),
    Case("B7-4", f"{FEES} L164-L170", B7,
         "The landlord charges £40 for a variation of the tenancy at the landlord's request.",
         "Does paragraph 6(1) make the payment a permitted payment?", NO, "not at the tenant's request"),
    Case("B8-1", f"{PENS} L61-L63", B8, "The gross earnings in a 12-month pay reference period are £30,000.",
         "Are the qualifying earnings £23,760?", YES, "30,000 - 6,240"),
    Case("B8-2", f"{PENS} L61-L63", B8, "The gross earnings in a 12-month pay reference period are £60,000.",
         "Are the qualifying earnings £44,030?", YES, "50,270 - 6,240"),
    Case("B8-3", f"{PENS} L61-L63", B8, "The gross earnings in a 12-month pay reference period are £5,000.",
         "Are there any qualifying earnings?", NO, "under the band"),
    Case("B8-4", f"{PENS} L61-L63", B8, "The gross earnings in a 12-month pay reference period are £6,240.",
         "Are there any qualifying earnings?", NO, "'more than £6,240' excludes 6,240"),
    Case("B9-1", "stock/app-levy/source.txt L5-L12, L14-L16", B9,
         "The person's pay bill for the tax year is £4,000,000. Sections 101, 102 and 103 do not apply.",
         "Is the amount of apprenticeship levy charged £5,000?", YES, "20,000 - 15,000"),
    Case("B9-2", "stock/app-levy/source.txt L5-L12, L14-L16", B9,
         "The person's pay bill for the tax year is £3,000,000. Sections 101, 102 and 103 do not apply.",
         "Is apprenticeship levy charged?", NO, "15,000 does not exceed the allowance"),
    Case("B9-3", "stock/app-levy/source.txt L5-L12, L14-L16", B9,
         "The person's pay bill for the tax year is £2,000,000. Sections 101, 102 and 103 do not apply.",
         "Is apprenticeship levy charged?", NO, "10,000 is under the allowance"),
    Case("B10-1", "batch5/github-rest-rate-limits/source.txt L20-L21", B10,
         "The installation has 10 repositories and 5 users. It is not on a GitHub Enterprise Cloud organization.",
         "Is the installation's rate limit 5,000 requests per hour?", YES, "no increase applies"),
    Case("B10-2", "batch5/github-rest-rate-limits/source.txt L20-L21", B10,
         "The installation has 200 repositories and no users beyond 20. It is not on a GitHub Enterprise Cloud "
         "organization.", "Is the installation's rate limit 12,500 requests per hour?", YES,
         "15,000 or 14,000 before the cap: 12,500 under either reading"),
    Case("B10-3", "batch5/github-rest-rate-limits/source.txt L20-L21", B10,
         "The installation has 25 repositories and 10 users. It is not on a GitHub Enterprise Cloud organization.",
         "Is the installation's rate limit 6,250 requests per hour?", REFUSE,
         "'for each repository' allows 6,250 (every repository) or 5,250 (beyond 20): no single figure"),

    # ---- Gap C: time phrases ----
    Case("C1-1", f"{HIPAA} L40", C1,
         "The covered entity discovered the breach on 1 March. It provided the notification on 30 April. Section "
         "164.412 does not apply.", "Was the notification within the 60-calendar-day outer limit?", YES,
         "30 April is day 60"),
    Case("C1-2", f"{HIPAA} L40", C1,
         "The covered entity discovered the breach on 1 March. It provided the notification on 1 May. Section "
         "164.412 does not apply.", "Was the notification provided in time?", NO, "1 May is day 61"),
    Case("C1-3", f"{HIPAA} L40", C1,
         "The covered entity discovered the breach on 1 March. It had all the facts on 3 March. It waited without "
         "giving a reason and provided the notification on day 45 after discovery. Section 164.412 does not apply.",
         "Did the covered entity comply with paragraph (b)?", REFUSE,
         "within 60 days, but whether the delay was unreasonable needs facts the sentence does not fix"),
    Case("C2-1", f"{HIPAA} L47", C2,
         "A breach of unsecured protected health information involving 120 individuals was discovered on 10 June "
         "2026.", "Must the covered entity notify the Secretary not later than 1 March 2027?", YES,
         "60 days after 31 December 2026 is 1 March 2027"),
    Case("C2-2", f"{HIPAA} L47", C2,
         "A breach of unsecured protected health information involving 120 individuals was discovered on 5 May 2027.",
         "Must the covered entity notify the Secretary not later than 29 February 2028?", YES,
         "2028 is a leap year: 60 days after 31 December 2027 is 29 February 2028"),
    Case("C2-3", f"{HIPAA} L47", C2,
         "A breach of unsecured protected health information involving 500 individuals was discovered on 10 June "
         "2026.", "Does paragraph (c) apply to this breach?", NO, "500 is not 'less than 500'"),
    # C3 (strict form): "without undue delay" is a separate limit from the 14-day outer limit.
    Case("C3-1", f"{CANCEL} L90", C3,
         "The consumer informed the trader of the cancellation on 3 June as required by regulation 32(2). The "
         "consumer sent off the goods on 17 June. The trader received the goods on 20 June.",
         "Did the consumer send off the goods in time?", REFUSE,
         "strict form: day 14 meets the outer limit, but no facts decide 'without undue delay'"),
    Case("C3-2", f"{CANCEL} L90", C3,
         "The consumer informed the trader of the cancellation on 3 June as required by regulation 32(2). The "
         "consumer sent off the goods on 17 June. The trader received the goods on 20 June.",
         "Did the consumer send off the goods not later than 14 days after the day on which the consumer informed "
         "the trader?", YES, "the 14 days are 4-17 June; sending off counts, not arrival (outer limit only)"),
    Case("C3-3", f"{CANCEL} L90", C3,
         "The consumer informed the trader of the cancellation on 3 June as required by regulation 32(2). The "
         "consumer sent off the goods on 18 June.", "Did the consumer send off the goods in time?", NO,
         "18 June is past the 14-day outer limit"),
    Case("C4-1", f"{FEES} L222-L223", C4,
         "The landlord receives the holding deposit on 1 March. There is no agreement in writing about a different "
         "day.", "Is the deadline for agreement 15 March?", YES, "the day of receipt is day 1"),
    Case("C4-2", f"{FEES} L222-L223", C4,
         "The landlord receives the holding deposit on 20 February 2027. There is no agreement in writing about a "
         "different day.", "Is the deadline for agreement 6 March 2027?", YES, "20-28 February is 9 days"),
    Case("C4-3", f"{FEES} L222-L223", C4,
         "The landlord receives the holding deposit on 1 March. The landlord and the tenant agree orally that the "
         "deadline for agreement is 31 March.", "Is the deadline for agreement 31 March?", NO,
         "an oral agreement is not 'in writing'"),
    Case("C5-1", f"{FEES} L138-L140", C5, "The rent was due on 1 May. The tenant paid the rent in full on 14 May.",
         "Is there a relevant default?", NO, "the period is 1-14 May"),
    Case("C5-2", f"{FEES} L138-L140", C5, "The rent was due on 1 May. The tenant paid the rent in full on 15 May.",
         "Is there a relevant default?", YES, "15 May is after the end of the period"),
    Case("C5-3", f"{FEES} L138-L140", C5,
         "The rent was due on 1 May. The tenant paid half of the rent on 10 May and the rest on 16 May.",
         "Is there a relevant default?", YES, "not paid in full by the end of 14 May"),
    Case("C6-1", f"{FLEX} L17-L19", C6,
         "The employee made applications under this section to the same employer on 1 February 2026 and 1 December "
         "2026. Both were decided. The employee makes a third application to the same employer on 15 January 2027.",
         "Is the third application allowed by paragraph (a)?", NO, "1 February 2026 - 31 January 2027 holds three"),
    Case("C6-2", f"{FLEX} L17-L19", C6,
         "The employee made applications under this section to the same employer on 1 February 2026 and 1 December "
         "2026. Both were decided. The employee makes a third application to the same employer on 2 February 2027.",
         "Is the third application allowed by paragraph (a)?", YES, "no 12-month period holds all three"),
    Case("C6-3", f"{FLEX} L17-L19", C6,
         "The employee made applications under this section to one employer on 1 February 2026 and 1 December 2026. "
         "Both were decided. The employee makes a third application to a different employer on 15 January 2027.",
         "Is the third application allowed by paragraph (a)?", YES, "another employer is counted separately"),
    Case("C7-1", f"{FLEX} L86-L88", C7,
         "The decision period came to an end on 10 March. The employer and the employee make an agreement to extend "
         "it, with retrospective effect, on 10 June.", "Was the agreement made in time?", YES,
         "three months beginning 11 March end at the end of 10 June"),
    Case("C7-2", f"{FLEX} L86-L88", C7,
         "The decision period came to an end on 10 March. The employer and the employee make an agreement to extend "
         "it, with retrospective effect, on 11 June.", "Was the agreement made in time?", NO, "11 June is too late"),
    Case("C7-3", f"{FLEX} L86-L88", C7,
         "The decision period ends on 10 March. The employer and the employee make an agreement to extend it on 5 "
         "March.", "Was the agreement made in time?", YES, "before it ends: (a)"),
    Case("C8-1", "dl/cfr107/full.txt L77", C8,
         "An applicant failed the knowledge test on 1 March. The applicant reapplies for the test on 10 March.",
         "Is the applicant allowed to reapply on 10 March?", NO, "inside the bar under either count"),
    Case("C8-2", "dl/cfr107/full.txt L77", C8,
         "An applicant failed the knowledge test on 1 March. The applicant reapplies for the test on 16 March.",
         "Is the applicant allowed to reapply on 16 March?", YES, "after the bar under either count"),
    # C8 (strict form): whether the failure day counts is ambiguous, so 15 March commits to no single count.
    Case("C8-3", "dl/cfr107/full.txt L77", C8,
         "An applicant failed the knowledge test on 1 March. The applicant reapplies for the test on 15 March.",
         "Is the applicant allowed to reapply on 15 March?", REFUSE,
         "strict form: 2-15 March (not allowed) or 1-14 March (allowed) are both allowed by the words"),
    Case("C9-1", f"{TOT} L15", C9,
         "A previous disqualification for a fixed period of 3 months was imposed on the offender on 1 June 2023. The "
         "latest offence was committed on 1 May 2026. The offender was convicted on 1 August 2026. Subsection (2A) "
         "does not apply.", "Is the previous disqualification to be taken into account?", YES,
         "within the three years before the offence (not the conviction); the design's minimum of 1 year is B3-2"),
    Case("C9-2", f"{TOT} L15", C9,
         "A previous disqualification for a fixed period of 28 days was imposed on the offender on 1 June 2025. The "
         "latest offence was committed on 1 May 2026. Subsection (2A) does not apply.",
         "Is the previous disqualification to be taken into account?", NO, "28 days is under 56 days"),
    Case("C9-3", f"{TOT} L15", C9,
         "A previous disqualification for a fixed period of 56 days was imposed on the offender on 1 April 2023. The "
         "latest offence was committed on 15 April 2026. The offender was convicted on 1 June 2026. Subsection (2A) "
         "does not apply.", "Is the previous disqualification to be taken into account?", NO,
         "1 April 2023 is before 15 April 2023"),
    Case("C10-1", f"{HOS} L8-L11", C10,
         "The employing motor carrier operates commercial motor vehicles Monday to Friday only. The driver was on duty "
         "12 hours on each day from Monday to Friday. On Saturday morning the driver has been off duty for 10 hours "
         "since Friday.", "May the driver drive on Saturday morning?", NO, "60 hours in 7 consecutive days"),
    Case("C10-2", f"{HOS} L8-L11", C10,
         "The employing motor carrier operates commercial motor vehicles Monday to Friday only. The driver was on duty "
         "12 hours on each day from Monday to Friday. The driver was then off duty for 34 consecutive hours, from "
         "Friday 18:00 to Sunday 04:00.", "May the driver drive at Sunday 04:00?", YES,
         "34 consecutive hours off end the period"),
    Case("C10-3", f"{HOS} L8-L11", C10,
         "The employing motor carrier operates commercial motor vehicles every day of the week. The driver has been "
         "on duty 64 hours in the last 8 consecutive days.", "Does paragraph (2) bar the driver from driving?", NO,
         "64 is under 70"),

    # ---- Gap D: passives ----
    Case("D1-1", f"{FMLA} L6", D1,
         "The employee's worksite has 30 employees of the employer. Another site of the same employer, 60 miles away, "
         "has 25 employees of the employer.", "Is the condition in paragraph (3) met?", YES, "55 within 75 miles"),
    Case("D1-2", f"{FMLA} L6", D1,
         "The employee's worksite has 40 employees of the employer and 20 contractor staff employed by an agency. The "
         "employer has no other site.", "Is the condition in paragraph (3) met?", NO,
         "staff of other employers do not count: 40"),
    Case("D1-3", f"{FMLA} L6", D1,
         "The employee's worksite has 30 employees of the employer. Another site of the same employer, 80 miles away, "
         "has 25 employees of the employer.", "Is the condition in paragraph (3) met?", NO, "the far site is excluded"),
    Case("D2-1", f"{FMLA} L18", D2,
         "The employee gave notice of the need for leave on 1 April. 55 employees were employed within 75 miles then. "
         "The leave starts on 1 May, when 40 employees are employed within 75 miles.",
         "Is the 50-employees condition met for that notice?", YES, "counted when notice is given"),
    Case("D2-2", f"{FMLA} L18", D2,
         "The employee gave notice of the need for leave on 1 April. 45 employees were employed within 75 miles then. "
         "The leave starts on 1 May, when 55 employees are employed within 75 miles.",
         "Is the 50-employees condition met for that notice?", NO, "not at the time of notice"),
    Case("D2-3", f"{FMLA} L18", D2,
         "The employee gave a notice on 1 April, when 45 employees were employed within 75 miles. On 1 June the count "
         "reached 55. The employee gives a new notice of the need for leave on 2 June, when 55 employees are employed "
         "within 75 miles.",
         "Is the 50-employees condition met for the new notice?", YES, "counted afresh at the new notice"),
    Case("D3-1", f"{HIPAA} L52", D3,
         "An employee of the business associate committed the breach and knew of it on 1 January. No one else knew of "
         "it. By exercising reasonable diligence it would have been known on 10 January. The security team found it "
         "on 20 January.", "Is the breach treated as discovered on 10 January?", YES,
         "the wrongdoer's knowledge is excluded"),
    Case("D3-2", f"{HIPAA} L52", D3,
         "An employee of the business associate committed the breach and knew of it on 1 January. An uninvolved "
         "employee of the business associate saw it on 5 January and told no one. By exercising reasonable diligence "
         "it would have been known on 10 January. The security team found it on 20 "
         "January.", "Is the breach treated as discovered on 5 January?", YES,
         "an uninvolved employee's knowledge is imputed"),
    Case("D4-1", f"{CANCEL} L48", D4,
         "The cancellation period ends at the end of 14 May. The consumer informs the trader by a letter posted on 14 "
         "May. The letter arrives on 16 May.", "Is the consumer treated as having cancelled in the cancellation "
         "period?", YES, "sent, not received, counts"),
    Case("D4-2", f"{CANCEL} L48", D4,
         "The cancellation period ends at the end of 14 May. The consumer informs the trader by a letter posted on 15 "
         "May.", "Is the consumer treated as having cancelled in the cancellation period?", NO, "sent too late"),
    Case("D5-1", f"{FLEX} L89-L92", D5,
         "The employee failed to attend the first meeting arranged by the employer to discuss the application. The "
         "employee attended the next meeting.", "Is the application treated as withdrawn?", NO,
         "one missed meeting is not enough"),
    Case("D5-2", f"{FLEX} L89-L92", D5,
         "The employee without good reason failed to attend both the first meeting arranged by the employer to "
         "discuss the application and the next meeting. The employer has not notified the employee of anything.",
         "Is the application treated as withdrawn?", NO, "no notice, no deemed withdrawal"),
    Case("D5-3", f"{FLEX} L89-L92", D5,
         "The employee without good reason failed to attend both the first meeting arranged by the employer to "
         "discuss the application and the next meeting. The employer notified the employee that it has decided to "
         "treat that conduct as a withdrawal of the application.", "Is the application treated as withdrawn?", YES,
         "both meetings missed without good reason, and the notice"),
    Case("D5-4", f"{FLEX} L89-L92", D5,
         "The employee without good reason failed to attend the first meeting arranged by the employer to discuss the "
         "application. The employee had a good reason for failing to attend the next meeting. The employer notified "
         "the employee that it has decided to treat that conduct as a withdrawal of the application.",
         "Is the application treated as withdrawn?", NO, "'without good reason' for both is not made out"),
    Case("D6-1", "batch5/github-tos-accounts/source.txt L236", D6,
         "The user e-mails an amended clause to GitHub and signs it. GitHub does not sign it.",
         "Has the Agreement been modified?", NO, "only GitHub's side can modify"),
    # D6 (strict form): an unsigned chat message: plainly "not modified", no hedge.
    Case("D6-2", "batch5/github-tos-accounts/source.txt L236", D6,
         "GitHub support sends the user an unsigned chat message waiving a clause.",
         "Has the Agreement been modified?", NO, "strict form: unsigned, so not a signed written amendment"),
    Case("D6-3", "batch5/github-tos-accounts/source.txt L236", D6,
         "GitHub posts a revised version of the Agreement in accordance with Section R.",
         "Has the Agreement been modified?", YES, "the second route"),
    Case("D7-1", f"{FEES} L26-L32", D7, "The tenant's parent guarantees the payment of rent by the tenant.",
         "Is the tenant's parent a relevant person?", YES, "a guarantor of the tenant's rent"),
    Case("D7-2", f"{FEES} L26-L32", D7,
         "A local housing authority within the meaning of the Housing Act 1985 guarantees the payment of rent by the "
         "tenant.", "Is the local housing authority a relevant person?", NO, "excluded by (10)(a)"),
    Case("D7-3", f"{FEES} L26-L32", D7,
         "A friend of the tenant pays the tenant's moving costs. The friend does not guarantee the payment of rent "
         "and does not act on behalf of the tenant.", "Is the friend a relevant person?", NO, "not covered by (9)(b)"),
    Case("D8-1", f"{PENS} L9, L17-L20", D8_1_2 + "\n" + D8,
         "The jobholder is aged 30 and has not reached pensionable age. Employer A pays the jobholder £6,000 and "
         "employer B pays the jobholder £6,000, each in a 12-month pay reference period.",
         "Does this section apply to the jobholder's employment with employer A?", NO,
         "tested per employer, not added up"),
    Case("D8-1b", f"{PENS} L9, L17-L20", D8_1_2 + "\n" + D8,
         "The jobholder is aged 30 and has not reached pensionable age. Employer A pays the jobholder £6,000 and "
         "employer B pays the jobholder £6,000, each in a 12-month pay reference period.",
         "Does this section apply to the jobholder's employment with employer B?", NO,
         "tested per employer, not added up (neither employment)"),
    Case("D8-2", f"{PENS} L17-L20", D8,
         "The jobholder is aged 30 and has not reached pensionable age. The employer pays the jobholder exactly "
         "£10,000 in the relevant pay reference period.", "Does this section apply to the jobholder?", NO,
         "£10,000 is not 'more than £10,000'"),
    Case("D8-3", f"{PENS} L17-L20", D8,
         "The jobholder is aged 21. The employer pays the jobholder £20,000 in the relevant pay reference period.",
         "Does this section apply to the jobholder?", NO, "under 22"),
    Case("D9-1", f"{FEES} L227-L236", D9,
         "A letting agent received the holding deposit. The landlord decides on 3 March, before the deadline for "
         "agreement, not to enter into a tenancy agreement. None of paragraphs 5 to 12 applies.",
         "Must the letting agent repay the deposit by 9 March?", YES,
         "the recipient repays; 7 days beginning with 3 March"),
    Case("D9-2", f"{FEES} L227-L236", D9,
         "A letting agent received the holding deposit. The landlord decides on 3 March, before the deadline for "
         "agreement, not to enter into a tenancy agreement. None of paragraphs 5 to 12 applies.",
         "Is the landlord the person who must repay the deposit?", NO, "trap: the person who received it repays"),
    Case("D9-3", f"{FEES} L227-L236", D9,
         "The landlord received the holding deposit. The landlord and the tenant enter into a tenancy agreement dated "
         "10 April. None of paragraphs 5 to 12 applies.", "Must the landlord repay the deposit by 16 April?", YES,
         "7 days beginning with 10 April"),
    # D10 (strict form): no £40,000 figure; the price fact is stated as "exceeds the applicable amount".
    Case("D10-1", "stock/ved-first-year/source.txt L85-L90", D10,
         "The vehicle is a petrol car to which this Part applies. The price of the vehicle exceeds the applicable "
         "amount. It was first registered in France on 1 March 2021 and registered in the United Kingdom in 2024. Its "
         "applicable CO2 emissions figure exceeds 0g/km. The licence is not its first vehicle licence and has effect "
         "on 1 December 2026.", "Does sub-paragraph (2) apply to this licence?", YES,
         "first registration anywhere: 5 years 9 months is less than six years"),
    Case("D10-2", "stock/ved-first-year/source.txt L85-L90", D10,
         "The vehicle is a petrol car to which this Part applies. The price of the vehicle exceeds the applicable "
         "amount. It was first registered in France on 1 March 2021 and registered in the United Kingdom in 2024. Its "
         "applicable CO2 emissions figure exceeds 0g/km. The licence is not its first vehicle licence and has effect "
         "on 2 March 2027.", "Does sub-paragraph (2) apply to this licence?", NO, "not less than six years"),
    Case("D10-3", "stock/ved-first-year/source.txt L85-L90", D10,
         "The vehicle is a zero-emission car to which this Part applies. The price of the vehicle exceeds the "
         "applicable amount. It was first registered on 1 January 2025. Its applicable CO2 emissions figure is "
         "0g/km. The licence is not its first vehicle licence and has effect on 1 December 2026.",
         "Does sub-paragraph (2) apply to this licence?", NO, "(c) fails: before 1 April 2025 and 0g/km"),
    Case("D10-4", "stock/ved-first-year/source.txt L85-L90", D10,
         "The vehicle is a petrol car to which this Part applies. The price of the vehicle is £45,000. It was first "
         "registered in France on 1 March 2021. Its applicable CO2 emissions figure exceeds 0g/km. The licence is not "
         "its first vehicle licence and has effect on 1 December 2026.",
         "Does sub-paragraph (2) apply to this licence?", REFUSE,
         "strict form: the quoted lines do not state the applicable amount, so a price in pounds settles nothing"),
]

DESIGNS = [f"{gap}{n}" for gap in "ABCD" for n in range(1, 11)]
STRICT = {"C3", "C8", "D6", "D10"}  # resolved toward refusing, decide wake 1124Z item 2


# The Yes/No cases the reader answers as designed. Empty on main (a2aa95f3e1): main's reader refuses every one of these
# texts whole. The row that builds the reader adds each case it answers here; that case then loses its strict xfail
# (its XPASS would fail first), and every REFUSE case of the same design must from then on be read and left open.
ANSWERED: set[str] = set()
XFAIL = {case.ident for case in CASES if case.expect != REFUSE} - ANSWERED
OPEN_LEADS = {"notSettled", "notNecessarily", "unknown"}


def outcome(case: Case, tmp_path) -> tuple[str, str | None, list[str]]:
    """("refused", None, refusal lines) when VE does not read the text; else (the answer, its lead, Lean's lines)."""
    result = read(tmp_path / f"{case.ident}.txt", case.text, scratch=tmp_path)
    if result["status"] != "read":
        return "refused", None, result["text"]
    assert len(result["answers"]) == 1, (case.ident, result["answers"])
    got = result["answers"][0]
    return got["answer"], got["lead"], got["text"]


def check(case: Case, tmp_path) -> None:
    got, lead, lines = outcome(case, tmp_path)
    if case.expect == REFUSE:
        # A REFUSE failure is a real failure (never an xfail): its message does not carry the xfail rows' reason.
        message = f"english-gap-guard {case.ident}: {case.why} (expected no Yes or No, got {got})"
        if any(c.design == case.design and c.ident in ANSWERED for c in CASES):
            # The reader reads this design's sentences: the refusal must be the answer left open, not a text refused.
            assert got != "refused" and lead in OPEN_LEADS, message
        else:
            assert got in NOT_COMMITTED, message
        return
    # The message starts with the xfail reason, so a gate that reads a failure's text sees "english-gap <id>".
    message = f"english-gap {case.design}: {case.why} (case {case.ident}: expected {case.expect}, got {got})"
    assert got == case.expect, message
    if case.ident == "D6-2":
        # Strict form: a plain "not modified", with no hedge.
        assert not any("unless" in line.lower() for line in lines), message


def _param(case: Case):
    marks = ([pytest.mark.xfail(strict=True, raises=AssertionError,
                               reason=f"english-gap {case.design}: {case.why}")]
             if case.ident in XFAIL else [])
    return pytest.param(case, id=case.ident, marks=marks)


@pytest.mark.parametrize("case", [_param(case) for case in CASES])
def test_english_gap_design(case, tmp_path):
    """One test case of an english-gap design (the case ID starts with the design ID, A1 to D10)."""
    check(case, tmp_path)


def test_every_design_has_cases_and_the_strict_forms_are_kept():
    """All 40 designs have a case; the four disputed ones keep the DRI's stricter form (C3 day-14 posting and C8 15
    March refuse; D6's unsigned chat message is a plain No; D10 states no pound figure for the applicable amount and
    refuses for a price in pounds)."""
    assert sorted({case.design for case in CASES}, key=DESIGNS.index) == DESIGNS
    assert len({case.ident for case in CASES}) == len(CASES)
    by_id = {case.ident: case for case in CASES}
    assert by_id["C3-1"].expect == REFUSE and "17 June" in by_id["C3-1"].facts
    assert by_id["C3-3"].expect == NO
    assert by_id["C8-3"].expect == REFUSE and "15 March" in by_id["C8-3"].facts
    assert by_id["D6-2"].expect == NO and "unsigned" in by_id["D6-2"].facts
    assert not any("40,000" in case.text for case in CASES if case.design == "D10")
    assert by_id["D10-4"].expect == REFUSE
    assert all(case.expect in (YES, NO, REFUSE) and case.question.endswith("?") for case in CASES)


def test_each_quoted_rule_keeps_its_source_words():
    """Each quote is copied whole: no case cuts a quoted line (an ellipsis appears in none of them)."""
    for case in CASES:
        assert "[...]" not in case.rule and "…" not in case.rule, case.ident
