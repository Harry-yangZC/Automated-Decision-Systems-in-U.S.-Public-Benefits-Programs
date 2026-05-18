# MA_SNAP.annotated.md — schema spec for the MA SNAP gold letter

> **Purpose (per V2 §5.1).** Every span of `MA_SNAP.md` is classified as one
> of `slot | module | boilerplate`. Slot resolution is the closure check
> that gates Phase 1 — every `slot:<...>` here must resolve to a populated,
> non-null path in the joined playbook (V2 §5.5). Module references must
> resolve to a file under `pipeline/request_modules/`.

## Conventions

- `[[slot:path.to.field|TEXT]]` — text that pulls from the playbook. `path.to.field` is the JSON path inside the joined `(state_law, agency_program)` dict.
- `[[module:module_id|TEXT]]` — text that is the rendered body of a request module. `module_id` matches `pipeline/request_modules/<module_id>.yaml`.
- Anything not wrapped in `[[ ]]` is **boilerplate** — fixed wording applied to every letter in the V2 pilot.
- Module bodies can themselves contain slots; for readability we inline the rendered text and note nested slots in the index below.
- The `_letter_meta.*` namespace is reserved for per-letter parameters (date, time scope, requester). These are *not* state-law or agency-program facts; they live with the snapshot json described in V2 §8.2.

---

## Annotated letter

[[slot:_letter_meta.requester.name|Tomo Lazovich]]
[[slot:_letter_meta.requester.title|Assistant Professor of the Practice (AI Governance and Policy)]]
[[slot:_letter_meta.requester.organization|Brown University, Data Science Institute]]
[[slot:_letter_meta.requester.address_line1|164 Angell Street, Box 1827]]
[[slot:_letter_meta.requester.city|Providence]], [[slot:_letter_meta.requester.state|RI]] [[slot:_letter_meta.requester.zip|02912]]
[[slot:_letter_meta.requester.email|tomo_lazovich@brown.edu]]

[[slot:_letter_meta.letter_date|May 14, 2026]]

[[slot:agency_program.administering_agency.name|Massachusetts Department of Transitional Assistance]]
Attn: [[slot:agency_program.records_officer.name|Lauren Picone]], [[slot:agency_program.records_officer.title|Records Access Officer]]
[[slot:agency_program.contact.address_line1|One Ashburton Place]]
[[slot:agency_program.contact.city|Boston]], [[slot:agency_program.contact.state|MA]] [[slot:agency_program.contact.zip|02108]]

Re: Public Records Request under [[slot:state_law.public_records_law.citation|M.G.L. c. 66, § 10]] — Automated Decision Systems Used to Administer the [[slot:agency_program.program_aliases[0]|Supplemental Nutrition Assistance Program]]

Dear Ms. [[slot:agency_program.records_officer.name|Picone]],

Pursuant to the [[slot:state_law.public_records_law.name|Massachusetts Public Records Law]], [[slot:state_law.public_records_law.citation|M.G.L. c. 66, § 10]], and the definition of "public record" at [[slot:state_law.public_records_law.record_definition_citation|M.G.L. c. 4, § 7, cl. 26]], I respectfully request access to records held by the [[slot:agency_program.administering_agency.name|Massachusetts Department of Transitional Assistance]] ("[[slot:agency_program.administering_agency.abbreviation|DTA]]") concerning automated decision systems used by [[slot:agency_program.administering_agency.abbreviation|DTA]] to administer the [[slot:agency_program.program_aliases[0]|Supplemental Nutrition Assistance Program]] ("[[slot:agency_program.program|SNAP]]").

For the purposes of this request, "automated decision systems" includes algorithms, data-matching programs, artificial intelligence, machine learning, predictive analytics, identity-verification platforms, and risk-scoring tools used by [[slot:agency_program.administering_agency.abbreviation|DTA]] — in the Program Integrity division or any other [[slot:agency_program.administering_agency.abbreviation|DTA]] division — to assist in determining eligibility, detecting fraud, or flagging [[slot:agency_program.program|SNAP]] cases for review.

The time scope of this request is [[slot:_letter_meta.time_scope_start|January 1, 2018]] through the date of your response. I request only existing records; this request does not ask [[slot:agency_program.administering_agency.abbreviation|DTA]] to create new analyses, summaries, or compilations.

Specifically, I request the following eight categories of records:

1. **Procurement records.** [[module:procurement_contracts_rfps|Procurement contracts, order forms, statements of work, requests for proposals (RFPs), responses to RFPs, amendments, renewals, pricing schedules, subscription terms, and procurement correspondence for third-party software used for fraud detection, identity verification, or eligibility determination in [[slot:agency_program.program|SNAP]].]]

2. **System and product documentation.** [[module:system_documentation|Internally developed or vendor-provided technical documentation, system architecture descriptions, product attachments, configuration materials, online user manuals, and any embedded help or FAQ content describing the operation of these systems.]]

3. **Staff-use policies, manuals, and training materials.** [[module:staff_use_policies_training|User manuals, policy memos, training decks, recorded training sessions, screen-specific user guides, and Online Guide content describing how [[slot:agency_program.administering_agency.abbreviation|DTA]] staff use these systems to determine eligibility, deny, reduce, or terminate [[slot:agency_program.program|SNAP]] benefits, or refer cases for further review.]]

4. **Validation studies, accuracy audits, and bias or fairness reviews.** [[module:validation_accuracy_audits|Validation studies, accuracy audits, quality-assurance reviews, bias or fairness reviews, performance reports, false-positive analyses, and aggregate post-deployment metrics for these systems.]]

5. **Implementation deliverables.** [[module:implementation_deliverables|Data-file specifications documents (DFSDs), master design documents (MDDs), project requirements and onboarding (PROP) materials, kick-off and stakeholder lists, go-live materials, and implementation schedules associated with deploying these systems for [[slot:agency_program.program|SNAP]].]]

6. **Data inputs and dictionaries.** [[module:data_inputs_and_dictionaries|Data dictionaries, reference-code descriptions, source-data field lists, relational-model diagrams, lists of source data systems and tables shared with vendors, VPN and other transfer-protocol requirements, and data retention and post-termination destruction policies governing data shared with these systems.]]

7. **Risk alerts, thresholds, and dashboards.** [[module:risk_alerts_thresholds_dashboards|Configured risk alerts and their detection logic — including shared-address, shared-IP, shared-email, deceased-recipient, and similar anomaly checks — together with dashboard metric specifications, thresholds, scoring categories, and aggregate dashboards displaying [[slot:agency_program.program|SNAP]] applicant or recipient risk distributions.]]

8. **Vendor support, customer-success, and change requests.** [[module:vendor_support_change_requests|Help-desk severity-level terms, support tickets and escalations, customer-success engagement records, quarterly account-review materials, feature requests, new-data-source requests, and change orders associated with these systems.]]

**Format of production.** I request records in electronic format, delivered as text-searchable PDFs by email to [[slot:_letter_meta.requester.email|tomo_lazovich@brown.edu]] or via a secure shared link. If your office prefers, I am also happy to submit through DTA's public records request portal at [[slot:agency_program.portal.url|https://www.mass.gov/forms/submit-a-department-of-transitional-assistance-dta-public-records-request-prr]], or to correspond via [[slot:agency_program.contact.email|DTA.RAO@state.ma.us]]. Rolling production is welcome if the volume warrants.

**Segregation of exempt material.** [[slot:state_law.public_records_law.segregation_clause|Per [[slot:state_law.public_records_law.citation|M.G.L. c. 66, § 10]], exempt portions of a record may be withheld, but the non-exempt portions of the same record must still be produced.]] Please redact only what the statute requires and produce the balance.

**Fee waiver.** Pursuant to [[slot:state_law.public_records_law.fee_waiver.statutory_citation|M.G.L. c. 66, § 10(d)(v)]], I respectfully request a waiver or reduction of any applicable fees. The records sought concern operations of a public agency that significantly affect benefits decisions for low-income residents of the Commonwealth; the records will be used solely by [[slot:_letter_meta.requester.organization|Brown University's Data Science Institute]] for non-commercial public-interest research; and disclosure is not primarily in my personal commercial interest. If the estimated cost exceeds any fee-waiver threshold, please provide an itemized fee estimate before commencing the work so I may either authorize the work or narrow the request.

**Response deadline.** I look forward to your response within [[slot:state_law.public_records_law.response_deadline|10 business days]] of receipt of this request, consistent with [[slot:state_law.public_records_law.response_deadline_citation|M.G.L. c. 66, § 10(a)]]. If you cannot produce records within that period, please provide the written response that the statute requires, identifying which records require additional time and the reasons for the delay.

If any portion of this request is unclear, please contact me directly before denying it in whole or in part; I am happy to refine the scope, prioritize categories, or supply additional context. If you deny this request in whole or in part, please cite the specific statutory exemption relied on for each withheld record. I reserve my right to appeal to the [[slot:state_law.public_records_law.appeal_path.venue|Supervisor of Public Records in the Office of the Secretary of the Commonwealth]] pursuant to [[slot:state_law.public_records_law.appeal_path.citation|M.G.L. c. 66, § 10A]], or to seek judicial review in [[slot:state_law.public_records_law.appeal_path.judicial_venue|Suffolk Superior Court]].

Thank you for your time and assistance.

Sincerely,

[[slot:_letter_meta.requester.name|Tomo Lazovich]]
[[slot:_letter_meta.requester.title|Assistant Professor of the Practice (AI Governance and Policy)]]
[[slot:_letter_meta.requester.organization|Brown University, Data Science Institute]]

---

## Slot index — closure target for Phase 1e

**`state_law.*` slots (must resolve in `pipeline/playbook/state_law/MA.json`):**

- `state_law.public_records_law.name`
- `state_law.public_records_law.citation`
- `state_law.public_records_law.response_deadline`
- `state_law.public_records_law.response_deadline_citation`
- `state_law.public_records_law.record_definition_citation`
- `state_law.public_records_law.segregation_clause`
- `state_law.public_records_law.fee_waiver.statutory_citation`
- `state_law.public_records_law.appeal_path.venue`
- `state_law.public_records_law.appeal_path.citation`
- `state_law.public_records_law.appeal_path.deadline_days`
- `state_law.public_records_law.appeal_path.judicial_venue`

**`agency_program.*` slots (must resolve in `pipeline/playbook/agency_program/MA_SNAP.json`):**

- `agency_program.administering_agency.name`
- `agency_program.administering_agency.abbreviation`
- `agency_program.records_officer.name`
- `agency_program.records_officer.title`
- `agency_program.contact.address_line1`
- `agency_program.contact.city`
- `agency_program.contact.state`
- `agency_program.contact.zip`
- `agency_program.contact.email`
- `agency_program.portal.url`
- `agency_program.program`
- `agency_program.program_aliases[0]`

**`_letter_meta.*` slots (per-letter parameters; live in the Phase 4 snapshot json, not the playbook):**

- `_letter_meta.requester.name`
- `_letter_meta.requester.title`
- `_letter_meta.requester.organization`
- `_letter_meta.requester.address_line1`
- `_letter_meta.requester.city`
- `_letter_meta.requester.state`
- `_letter_meta.requester.zip`
- `_letter_meta.requester.email`
- `_letter_meta.letter_date`
- `_letter_meta.time_scope_start`

## Module index — closure target for `pipeline/request_modules/`

- `procurement_contracts_rfps`
- `system_documentation`
- `staff_use_policies_training`
- `validation_accuracy_audits`
- `implementation_deliverables`
- `data_inputs_and_dictionaries`
- `risk_alerts_thresholds_dashboards`
- `vendor_support_change_requests`

## Schema gaps surfaced by this annotation

Per V2 §5.1 the annotation is a *binary decision per word*; anything that
fits none of `slot | module | boilerplate` is a schema gap. The annotation
above did not surface any unclassifiable word, but it did add seven fields
not in the inline schemas of V2 §5.4 that are folded into the Phase 1d
schema files. Three were surfaced by the 1a annotation itself, and four
were surfaced by the 1c deep research and folded into the schema for
parity with what the research returned.

**From the 1a annotation:**

1. **`state_law.public_records_law.response_deadline_citation`** — the
   statute subsection that contains the deadline (here `M.G.L. c. 66, § 10(a)`).
2. **`state_law.public_records_law.record_definition_citation`** — the
   statute citation for the "public record" definition (here
   `M.G.L. c. 4, § 7, cl. 26`), distinct from the paraphrase string.
3. **`state_law.public_records_law.appeal_path.judicial_venue`** — the
   judicial-review venue distinct from the administrative appeal venue.

**From 1c deep research:**

4. **`state_law.public_records_law.extension`** — restructured from the V2
   §5.4 single `extension_clause: string` to a structured object
   `{ agency_initial_days, agency_initial_citation, supervisor_extension_days, supervisor_extension_citation }`
   to capture MA's two-stage extension (15-bd agency-initial under
   § 10(b)(vi); +20-bd Supervisor-granted under § 10).
5. **`state_law.public_records_law.appeal_path.deadline_days`** — 90
   (calendar). The V2 §5.4 schema already reserved this field.
6. **`state_law.public_records_law.oral_requests_allowed`** — boolean.
   MA explicitly allows oral PRRs but requires written form for appeal.
7. **`state_law.public_records_law.branch_carveouts`** — array of strings.
   MA exempts the legislature, courts, and federal agencies from the
   Public Records Law.

These are all additive; the only structural reshape is the extension
object replacing the extension string. None conflict with V2's design
rationale.
