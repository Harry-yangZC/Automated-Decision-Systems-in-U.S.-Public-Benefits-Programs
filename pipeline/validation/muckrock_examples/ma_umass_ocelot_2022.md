---
url: https://www.muckrock.com/foi/massachusetts-1/ocelot-documents-134670/
agency: University of Massachusetts Amherst
state: MA
program: Higher Education (not a benefits program)
filed_by: Todd Feathers
request_date: 2022-10-04
status: Completed
relevance: primary-ai-vendor-docs
relevance_notes: |
  Different sector (higher education, not benefits), but the request architecture
  is closer to V2's MA SNAP gold letter than any MA benefits-agency precedent we
  have. Successfully extracted contracts, data-sharing agreements, statements of
  work, technical/training/validation docs, and policy materials for an AI vendor.
---

# Ocelot documents

## Request scope (verbatim from MuckRock page)

> All contracts, memorandums of understanding, data sharing/privacy
> agreements, statements of work, and successful RFP responses and bid
> submission documents regarding the university's contracts with Ocelot Inc.
> ...
> This should include, where available, documents describing the design,
> training, and validation of any Ocelot Inc. artificial intelligence
> systems used by the university.

## Characterization

A completed AI-vendor-documents request against UMass Amherst from
October 2022. The request architecture explicitly asks for:
- Contracts and MOUs (`procurement_contracts_rfps` analogue)
- Data-sharing / privacy agreements (`data_inputs_and_dictionaries` analogue)
- Statements of work (`procurement_contracts_rfps` analogue)
- Bid submission documents (`procurement_contracts_rfps` analogue)
- Design / training / validation documentation
  (`system_documentation` + `validation_accuracy_audits` analogues)

This precedent's record-class breakdown maps almost one-to-one onto V2's
eight production-grounded modules, which is why we treat it as a primary
AI-vendor-docs comparator despite being from a non-benefits agency.

## Why it's included in the V2 MuckRock pool

Primary AI-vendor-docs comparator. The most direct AI-specific MA records
request precedent in the V2 pool; the scope decomposition closely matches
V2's module set. Use in Phase 5b LLM-as-judge comparison for
structural-completeness scoring.
