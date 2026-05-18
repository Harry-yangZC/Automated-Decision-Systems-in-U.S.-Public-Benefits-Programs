# Outbound request scope — MA DTA ADS public records request (Jan 27, 2026)

> **Provenance.** This file reconstructs the outbound request scope from the
> verbatim quotation embedded in DTA's response letter
> (`gold_letter.pdf`, p. 1, dated Feb 13, 2026). The exact outbound PRR text
> (including header, greeting, fee-waiver paragraph, format-of-production
> paragraph, etc.) is **not** in the PI-provided production package; only the
> *substantive scope* survives as DTA's quotation. Anything outside the
> quotation is unrecoverable from this package.

**Submitted by:** Tomo Lazovich, Brown University (`tomo_lazovich@brown.edu`)

**Received by DTA:** January 27, 2026

**DTA reference:** "PRR – Tomo Lazovich – Fraud Detection and Eligibility Determination Software"

**Quoted scope (verbatim from DTA response letter, p. 1):**

> Records regarding any automated decision systems, algorithms, data-matching
> programs, artificial intelligence, machine learning, or predictive analytics
> used by the DTA (in the Program Integrity or any other division) to assist
> in determining eligibility, detecting fraud, or flagging cases for review in
> the SNAP, TAFDC, and EAEDC programs.
>
> 1. Procurement contracts and RFPs for third-party software used for fraud
>    detection, identity verification, or eligibility determination.
> 2. Documentation of any internally developed software used for fraud
>    detection, identity verification, or eligibility determination.
> 3. User manuals, policy memos, or training materials describing how DTA
>    staff utilize these tools to deny, reduce, or terminate benefits.
> 4. Reports of any validation studies or accuracy audits conducted on these
>    systems.

**Program scope.** Original request named SNAP, TAFDC, and EAEDC. V2 narrows
implementation to **SNAP only** for the MA × SNAP vertical pilot (see
`pipeline/workflow_design_V2.md` §4 and §5.2). The TAFDC/EAEDC framing is
preserved in this excerpt as evidence that the broader phrasing succeeded.

**Division scope.** The outbound named the Program Integrity division and "any
other division." This catches both fraud-side ADS (Program Integrity, Recipient
Investigations, etc.) and eligibility-side ADS.

**Use-case scope.** Three eligibility-touching use cases: (a) determining
eligibility, (b) detecting fraud, (c) flagging cases for review.

**Record-class scope.** Four numbered categories in the outbound. V2 §5.4
expands these into eight production-grounded modules
(`procurement_contracts_rfps`, `system_documentation`,
`staff_use_policies_training`, `validation_accuracy_audits`,
`implementation_deliverables`, `data_inputs_and_dictionaries`,
`risk_alerts_thresholds_dashboards`, `vendor_support_change_requests`) based on
what DTA actually produced; the gold letter at
`pipeline/gold_letters/MA_SNAP.md` uses the expanded eight-module set.
