# Audit repair

The 28 September audit rejected `u0165.s07` because the generic document renderer called its 48-byte OPEN norm a “Checked reading.” The ledger and admitted document already marked the unit OPEN and named `child_sexual_abuse_material` with `decided_by: unresolved_decider`. Its source span is `[102149,102197)`.

In this run, `rendered.md` labels that exact reading **Open reading (child_sexual_abuse_material classification; decider unresolved)**. The norm content, source bytes, and OPEN status are unchanged. This is a presentation repair in the delivered rendering; `ve document render` still emits the generic “Checked reading” prefix, so regenerating that file requires applying this one label correction again.

The audit accepted the unit's substantive reading and the 22-byte `u0248` CHECKED assertion. After the label repair, these are the 70 audit-reviewed substantive covered bytes. The remaining 349 claimed covered bytes are metadata labels and are not counted as audit-verified substantive coverage.
