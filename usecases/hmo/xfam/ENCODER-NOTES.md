# ENCODER-NOTES: HMO England, cross-family set (out/cases_xfam.py)

Counts: 26 in-scope records (H001-H026), 8 probes (H027-H034). `python3 -I check.py out/cases_xfam.py` prints OK.

## Conventions used

- C1: people = occupants of the premises in the order named; occupants of other flats of the block (Fred, Grace in H014/H015; David in H022) are not named. Places: `premises`, plus unit1.. for the units of a whole building, flat2/flat3 for the other flats of a block where the premises is Flat 1.
- C2: relations only as stated (boilerplate 'otherwise unrelated'); 'X is their child' = parent_of from each parent. No kinship chain needed C2's unknown.
- C3: whole houses = one unit (premises within); converted/side-by-side buildings and bedsit offices = one place per set/room; Flat 1 as premises = one unit.
- C4: s.255 declaration only in H005, H024; s.257 only in H021 (whole block).
- C5: 'all occupants share the toilet, bathroom and kitchen' = each shares toilet, washing, cooking.
- C6: rent, accommodation charges and ground rent counted as rent_payable for the payer's occupation; a domestic worker's work is not counted.
- C7: numbers compared in H007, H008, H011, H013, H019, H021, H022 (listed below).
- C8: nothing left unknown; every case states each occupant's main residence status.

## Vocabulary limits noted

- H021: within-flat sharing of each flat's own facilities cannot be stated by `shares` (one facility of a kind in the premises); encoded as no sharing, since none is shared between flats.
- H022: the whole block's s.257 status (stated: applies) has no place of its own; s257(premises) false because Flat 1 is stated not to be a s.257 block.
- H018/H019: co-operative membership (Eva not a member) has no predicate; the rules (coop_rule_a..d) are encoded.

## Judgements (one per line)

- H001: 'residence for undertaking a full-time course of higher education' = ft_student
- H001: main_res false: stated that none occupies as only or main residence
- H002: abuse_refuge_use: each occupant left home because of violence, abuse or threats from a (former) spouse, civil partner or cohabitant and the house's entire accommodation use is their temporary accommodation
- H002: main_res false: stated that none occupies as only or main residence
- H003: 'employer provides the accommodation partly in consideration of employment' = consid_employment and employer_provided
- H003: 'accommodation charges' = other consideration: rent_payable (C6)
- H003: Dora: harvesting employment for an employer, seasonal and recurring, cannot exceed 8 months = seasonal_emp, le_8_months
- H003: main_res false: stated that none occupies as only or main residence
- H004: 'Dana is Ben's stepchild' = step_parent_of(Ben, Dana); no relation of Dana to Alice stated
- H005: listed_work: every duty stated for Clara is work usually done by a reg. 3(3) worker (nanny, nurse, carer, governess, servant, chauffeur, gardener, secretary, personal assistant)
- H005: 'Alan supplies Clara's accommodation as part of her remuneration' = supplied_by(Clara, Alan) (consideration for the work)
- H005: rent_payable only Alan: his rent to the freeholder read as for his occupation; no rent stated for Beth
- H006: listed_work: every duty stated for Clara is work usually done by a reg. 3(3) worker
- H006: 'Alan supplies Clara's accommodation as part of her remuneration' = supplied_by(Clara, Alan)
- H006: rent_payable only Clara: no rent stated for Alan (freeholder) or Beth; Daniel, Edith pay nothing
- H007: C7: one service user (Ben) is not more than three: le3_users(Alice)
- H008: C7: four service users is more than three: le3_users(Alice) false
- H009: (none beyond C1-C8)
- H010: (none beyond C1-C8)
- H011: C7: lease term 22 years is more than 21: long_lease(Anna)
- H011: 'Clara is their child' = parent_of(Anna, Clara), parent_of(Ben, Clara)
- H012: (none beyond C1-C8)
- H013: unit1-3 = the wings of Anna, Ben, Clara; unit4 = Flat 1 (David), unit5 = Flat 2 (Eva)
- H013: a wing / flat of the building forms part of it: part_of_building
- H013: Flat 2 lies below Flat 1: above_below for both; wings: no part above or below: false
- H013: C7: lease of exactly 21 years is not more than 21: long_lease(Anna) false
- H013: premises: amenities available to occupants (in their units), not exclusive at building level
- H014: premises = Flat 1 as one unit (C3); flat2 = Flat 2, the other flat of the block
- H014: Fred (Flat 2 only) does not occupy the premises: not named (C1)
- H014: block built as two separate sets: Flat 1 is purpose-built
- H014: Flat 1 wholly above Flat 2: above_below for both; each flat part_of_building
- H015: premises = Flat 1 as one unit (C3); flat2, flat3 = Flats 2 and 3 of the block
- H015: Fred (Flat 2) and Grace (Flat 3) do not occupy the premises: not named (C1)
- H015: block built as three separate sets: Flat 1 is purpose-built
- H015: flats stacked wholly above one another: above_below for each; each part_of_building
- H016: bedsitting rooms = unit1..unit5 (one per occupant, in the order named), created_since; separate set / above or below not stated: false
- H016: units: the shared toilet, bathroom and kitchen are available to (not exclusive to) each room's occupant
- H016: each of the seven named bodies manages and controls the building: all seven mgr_ predicates true
- H017: (none beyond C1-C8)
- H018: the society's stated binding rules = coop_rule_a..d; who is a member (Eva not) has no predicate: not encoded
- H019: the society's stated binding rules = coop_rule_a..d; membership has no predicate: not encoded
- H019: C7: assured tenancy for one year is not more than 21 years: long_lease(Anna) false
- H020: (none beyond C1-C8)
- H021: unit1 = Flat 1 (Anna, Ben), unit2 = Flat 2 (Clara, David, Eva)
- H021: C7: leases of 99 years are more than 21: long_lease(Anna), long_lease(Clara)
- H021: ground rent under their leases = rent payable for Anna's and Clara's occupation (C6); none stated for the others
- H021: 'Eva is their child' = parent_of(Clara, Eva), parent_of(David, Eva)
- H021: shares false for all: the premises has one set of facilities per flat and none is shared between flats; `shares` (one such facility in the premises) cannot state within-flat sharing
- H021: premises: amenities available to occupants (in their flats), not exclusive at building level
- H022: premises = Flat 1 as one unit (C3); flat2 = Flat 2, the other flat of the block
- H022: David (Flat 2 only) does not occupy the premises: not named (C1)
- H022: created by conversion of a warehouse: created_since, not purpose_built
- H022: s257(premises) false: Flat 1 itself is stated not to be a s.257 block; the whole block's s.257 status has no place of its own here
- H022: C7: lease of 99 years is more than 21: long_lease(Anna)
- H023: sets = unit1..unit5 in the order named; a set of the building forms part of it: part_of_building
- H023: no part of the building above or below any set: above_below false
- H023: premises: amenities available to occupants (in their units), not exclusive at building level
- H024: bedsitting rooms = unit1..unit5 (one per occupant, in the order named), created_since; separate set / above or below not stated: false
- H024: 'own toilet and shower' = toilet and washing; cooking facilities nowhere in the building
- H025: bedsitting rooms = unit1..unit5 (one per occupant, in the order named), created_since; separate set / above or below not stated: false
- H025: units: the shared toilet, bathroom and kitchen are available to (not exclusive to) each room's occupant
- H025: use of the same rooms and kitchen as a public cafe: only_use false
- H026: bedsitting rooms = unit1..unit5 (one per occupant, in the order named), created_since; separate set / above or below not stated: false
- H026: units: the shared toilet, bathroom and kitchen are available to (not exclusive to) each room's occupant
- H026: main_res false: stated that none occupies as only or main residence (leisure visit)
- H026: gratuitous licences, no consideration: rent_payable false

## Probes

- H027: turns on Sch. 14 para 3A specifications not supplied and not in the encoded text
- H028: turns on Sch. 14 para 3 / s.254(6) regulations not supplied
- H029: asks whether a licence is required (Part 2 licensing), outside the encoded provisions
- H030: asks whether an HMO declaration should be made; s.255 criteria not supplied
- H031: s.257 status of the whole block not stated
- H032: building in Wales; the encoded test set is England's
- H033: asks about HMO status for Part 1, outside the encoded question
- H034: asks the encoder to decide unstated immigration and accommodation statuses
