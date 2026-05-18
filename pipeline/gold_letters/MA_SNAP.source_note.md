# MA_SNAP.md — provenance and source notes

## Source-of-truth status

**Scope: verified against outbound. Boilerplate: V2-authored.**

The substantive request scope in [pipeline/gold_letters/MA_SNAP.md](MA_SNAP.md)
is verified to match the outbound public records request at
[pipeline/gold_letters/outbound_PRR.txt](outbound_PRR.txt), which the PI
provided after the initial gold-letter reconstruction was written. The
outbound scope and the four numbered record categories in our gold letter
are aligned with the PI's actual filing. The verbatim quotation embedded in
DTA's response letter (`gold_letter.pdf`, p. 1, dated Feb 13, 2026) matches
the PI's outbound text.

The **surrounding boilerplate** (header, recipient block, greeting,
definitions-of-ADS paragraph, format-of-production paragraph, segregation
clause, fee-waiver paragraph, response-deadline paragraph, sign-off, etc.)
is V2-authored, drawing on the BTAH/FOIA Basics/NFOIC templates listed
under "Cross-references" below. The PI's outbound did not include those
paragraphs; V2 adds them to give the schema spec the full slot coverage
required by §5.1 of `pipeline/workflow_design_V2.md`.

The eight numbered record categories in our gold letter are a deliberate
expansion of the PI's original four. The expansion adds four
production-grounded modules (implementation deliverables, data inputs and
dictionaries, risk alerts and dashboards, vendor support and change
requests) on the basis that DTA's actual production revealed record classes
the original four-category framing did not call out by name. See V2 §5.4.

Pages 3–12 of [pipeline/gold_letters/gold_letter.pdf](gold_letter.pdf) are
the production attachments (Thomson Reuters Order Form Q-08237974 on pp. 3–6;
West Publishing Statement of Work for ID Risk Analytics on pp. 7–12). Those
pages have no embedded text layer and were extracted via macOS Vision OCR;
cleaned text lives in [pipeline/precedents/MA_DTA_ADS_2026/raw_ocr/](../precedents/MA_DTA_ADS_2026/raw_ocr/).

## Program scope narrowing

The PI's outbound named SNAP, TAFDC, and EAEDC. For the V2 vertical pilot
this gold letter narrows to **SNAP only** (per V2 §4). The narrower phrasing
is a deliberate V2 design choice and is *not* a recommendation against
asking for TAFDC/EAEDC in the original outbound — those programs would be
modeled as separate `(state, program)` cells in later promotion gates.

## Slot value status after Phase 1c

The deep research run (Phase 1c) completed two passes. Both pass outputs
are preserved at [pipeline/step_1c_results/](../step_1c_results/) as raw
artifacts; the consolidated reconciled view is at
[pipeline/research/MA_SNAP_research.md](../research/MA_SNAP_research.md).
The table below records the status of each slot used in `MA_SNAP.md`.

| Slot                                                          | Value                                                                                                                  | Status                                                              |
| ------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------- |
| `state_law.public_records_law.name`                           | Massachusetts Public Records Law                                                                                       | Confirmed by 1c (mass.gov, sec.state.ma.us, malegislature.gov)      |
| `state_law.public_records_law.citation`                       | M.G.L. c. 66, § 10                                                                                                     | Confirmed by 1c                                                     |
| `state_law.public_records_law.response_deadline`              | 10 business days                                                                                                       | Confirmed by 1c                                                     |
| `state_law.public_records_law.response_deadline_citation`     | M.G.L. c. 66, § 10(a)                                                                                                  | Corrected from § 10(b) — see "Corrections applied" below            |
| `state_law.public_records_law.record_definition_citation`     | M.G.L. c. 4, § 7, cl. 26                                                                                               | Confirmed by 1c                                                     |
| `state_law.public_records_law.segregation_clause`             | "exempt portions of a record may be withheld, but the non-exempt portions of the same record must still be produced." | Confirmed by 1c                                                     |
| `state_law.public_records_law.fee_waiver.statutory_citation`  | M.G.L. c. 66, § 10(d)(v)                                                                                               | Refined from § 10(d) — see "Corrections applied" below              |
| `state_law.public_records_law.appeal_path.venue`              | Supervisor of Public Records in the Office of the Secretary of the Commonwealth                                        | Confirmed by 1c                                                     |
| `state_law.public_records_law.appeal_path.citation`           | M.G.L. c. 66, § 10A                                                                                                    | Confirmed by 1c                                                     |
| `state_law.public_records_law.appeal_path.judicial_venue`     | Suffolk Superior Court                                                                                                 | Confirmed; refined to "Superior Court under § 10A(c)" in playbook    |
| `state_law.public_records_law.appeal_path.deadline_days`      | 90 (calendar)                                                                                                          | New from 1c                                                         |
| `agency_program.administering_agency.name`                    | Massachusetts Department of Transitional Assistance                                                                    | Confirmed by 1c and `gold_letter.pdf` p. 1                          |
| `agency_program.administering_agency.abbreviation`            | DTA                                                                                                                    | Confirmed by 1c and `gold_letter.pdf` p. 1                          |
| `agency_program.records_officer.name`                         | Lauren Picone                                                                                                          | New from 1c (mass.gov/dta-public-records) — added to recipient block |
| `agency_program.records_officer.title`                        | Records Access Officer                                                                                                 | PRR role title per MA law                                           |
| `agency_program.records_officer.org_title`                    | Deputy General Counsel                                                                                                 | New field; carries her mass.gov-listed org title                    |
| `agency_program.contact.address_line1`                        | One Ashburton Place                                                                                                    | Confirmed                                                           |
| `agency_program.contact.city`                                 | Boston                                                                                                                 | Confirmed                                                           |
| `agency_program.contact.state`                                | MA                                                                                                                     | Confirmed                                                           |
| `agency_program.contact.zip`                                  | 02108                                                                                                                  | Confirmed                                                           |
| `agency_program.contact.phone`                                | 6173485247 (RAO general line)                                                                                          | New from 1c                                                         |
| `agency_program.contact.email`                                | DTA.RAO@state.ma.us                                                                                                    | New from 1c — added to Format-of-production paragraph               |
| `agency_program.portal.url`                                   | https://www.mass.gov/forms/submit-a-department-of-transitional-assistance-dta-public-records-request-prr               | New from 1c — added to Format-of-production paragraph               |
| `agency_program.program`                                      | SNAP                                                                                                                   | Confirmed                                                           |
| `agency_program.program_aliases`                              | [Supplemental Nutrition Assistance Program, SNAP, food stamps, food assistance]                                        | Confirmed by 1c                                                     |

## Corrections applied (post-1c)

The following corrections were made to `MA_SNAP.md` after 1c completed:

1. **Response-deadline citation.** Changed `M.G.L. c. 66, § 10(b)` to
   `M.G.L. c. 66, § 10(a)`. The 10-business-day duty is in subsection (a)
   of § 10 per the malegislature.gov statute text quoted in
   [pipeline/research/MA_SNAP_research.md](../research/MA_SNAP_research.md);
   (b) describes the procedural response and contains the 15-business-day
   initial extension at (b)(vi).
2. **Fee-waiver citation refined.** Changed `M.G.L. c. 66, § 10(d)` to
   `M.G.L. c. 66, § 10(d)(v)` for precision; the waiver clause is at (d)(v).
3. **Recipient block named.** Changed `Attn: Records Access Officer` to
   `Attn: Lauren Picone, Records Access Officer` and updated the greeting
   to `Dear Ms. Picone,`. This satisfies V2 §9.1's Layer 1a check that
   requires the RAO name and title to appear when both are non-null.
4. **Format-of-production paragraph expanded.** Added DTA's public records
   intake email and portal URL as alternate submission channels.

## Why this letter is dated May 14, 2026

The date in the letter is the V2 pilot drafting date, not the date of any
actual submission. When the campaign moves into Phase 6 promotion gates,
each submitted letter will be re-dated and snapshotted (see V2 §8.2 on the
snapshot json).

## Cross-references consulted (per V2 §5.1)

- [pipeline/gold_letters/gold_letter.pdf](gold_letter.pdf) (PI-provided
  successful DTA production package). Primary empirical precedent for
  request scope.
- [pipeline/gold_letters/outbound_PRR.txt](outbound_PRR.txt) (PI's outbound
  scope text). Verbatim source of the four numbered record categories and
  the substantive request scope.
- BTAH Public Records Request Guide model letter (Arkansas DHS example).
  Baseline format with named individuals and keyword strategy.
- FOIA Basics annotated tech FOIA request. Source of the definitions block,
  format-of-production block, fee-waiver block, and expedited-processing
  block patterns.
- NFOIC's MA-specific FOI sample letter. Source of the M.G.L. c. 66, § 10
  framing.
- Five MuckRock precedents in
  [pipeline/validation/muckrock_examples/](../validation/muckrock_examples/),
  collected by 1c Layer D.

## Closure check

Run by [pipeline/validation/closure_check.py](../validation/closure_check.py)
against the populated playbook at
[pipeline/playbook/](../playbook/). Per V2 §5.5, every `slot:<...>`
annotation in [MA_SNAP.annotated.md](MA_SNAP.annotated.md) must resolve to
a populated non-null path in the joined playbook. The closure check is the
gate to Phase 2.
