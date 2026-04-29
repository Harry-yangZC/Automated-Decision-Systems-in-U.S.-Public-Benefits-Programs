### The core idea: a composable template system.

Think of each request as assembled from a set of JSON-defined components, with an LLM performing the final composition into natural prose. Define the modular templates as structured data (JSON templates), then use an LLM to compose them into coherent, state-compliant prose.

The workflow has 5 phases:

### Phase 1: Template definition by conducting research

### Research

Look up online sources to better understand what we need for drafting requests for {states, programs}.

## Key external resources to leverage

- **[NFOIC State Sample FOI Request Letters](https://www.nfoic.org/state-sample-foia-request-letters/)** — boilerplate templates for all 50 states
- **[Benefits Tech Advocacy Hub Key Questions Guide](https://www.btah.org/resources/key-questions-guide.html)** — the most directly relevant resource; defines exactly what questions to ask about ADS in benefits programs
- **[BTAH Public Records Request Guide](https://btah.org/resources/public-records-request-guide.html)** — step-by-step guidance for filing records requests specifically about benefits technology
- **[FOIA Basics Annotated Tech Request](https://www.foiabasics.org/annotated-tech-foia-request)** — annotated sample request for algorithmic systems
- **[MuckRock](https://www.muckrock.com/)** — searchable database of past requests; keyword searches for "algorithm", "AI", "benefits", "automated" yield precedent language

The BTAH resources in particular are almost perfectly aligned with this project — they've already done the intellectual work of defining what to ask about benefits tech, and our project can operationalize that at a national scale.


### Reusable request components

Having an anatomy of a request to make a reusable request: construct a generic request skeleton for {states, programs}.

At minimum, our request generator could fill these slots (we can keep edit this):

- **legal opening**
  - “This is a request under the [state law name/citation].”
- **recipient block**
  - records officer / custodian / RAO
- **program scope**
  - `{program}`, `{state}`, `{agency}`, relevant subunit
- **time scope**
  - e.g. “January 1, 2022 to present”
- **record modules**
  - inventory, vendor, audits, policies, workflow
- **format request**
  - electronic copies preferred
- **clarification / segregation language**
  - if a category is too broad, please advise how to narrow
  - if portions are exempt, produce the rest
- **fee language**
  - request fee waiver or advance notice above threshold
- **referral language**
  - if another office maintains the records, please forward or identify it
- **appeal preservation**
  - written response requested

### Normalizer above info into a generic Request Playbook schema

```json
{
  "state": "",
  "program": "",
  "program_aliases": [],
  "administering_agency": "",
  "sub_agency": "",
  "records_officer_title": "",
  "records_officer_name": null,
  "contact": {
    "email": null,
    "phone": null,
    "address": null,
    "portal_url": null
  },
  "public_records_law": {
    "name": "",
    "citation": "",
    "response_deadline": "",
    "appeal_path": "",
    "fee_notes": ""
  },
  "submission_methods": [],
  "requester_fields_required": [],
  "known_system_names": [],
  "known_vendors": [],
  "keywords": [],
  "evidence": [
    {
      "source_type": "official_webpage",
      "url": "",
      "quote": "",
      "retrieved_at": ""
    }
  ],
  "confidence": "",
  "needs_manual_review": false
}
```

Later in Phase 3, we can consider store one row per `{state, program, agency}` with fields like (We could also create a CSV for this if more reasonable):

### Phase 2: Define New Question Set
Based on our schema above, manually design a new question set and experiment pipeline based on we already have. 

Possible questions to add:
```
- What is the name of the public records / open records law in {state}?
- What is the statutory citation for the public records law in {state}?
- Does {state} allow fee waivers for academic or public interest requests on {program}? What are the requirements?
- Who is the Records Access Officer / FOIA officer for the agency that administers {program} in {state}?
- What is the local name for {program} in {state}? (e.g., CalFresh for SNAP in California)
...
```

### Phase 3: Data Collection using LLMs - Starts Using LLM APIs
Design a prompt in @questions_prompt.txt, use LLMs to collect answers for the questions above, extract and feed the answers into our Request Playbook schema in Phase 1 that stores the legal boilerplate for each {state, program}. This schema should be able to give us everything needed for every components (Phase 1) of a request letter.


## For Phase 2 and 3, we may have two different implementations
**Opt1**: Design a benchmark set first, and then running LLMs, and then do cross-model validation. Like what we've done before. 

**Opt2**: If scaling up, manually collect benchmark questions first, then validate them, and then move to the next phase, which may be time-consuming and tedious. 
Here is another solution to balance price and scale:
Choose the most advanced LLM model, run it 10 times on each question, and take the answer only when the agreement rate is greater than or equal to 0.6 (6/10). If the agreement rate for this question is below 0.6, mark it for human review. 

### Phase 4: LLM-assisted drafting
Now we should have a reuseable, comprehensive playbook for different {state, program}. 

### LLM-assisted drafting
The LLM's job in this step is **not** to invent content — all the factual information comes from the validated playbook data. The LLM is composing a coherent letter from pre-defined components, similar to a mail-merge but with the ability to adjust tone, handle edge cases (e.g., states that require specific form language), and produce natural-sounding prose.

**A `generate_request.py` script** would:
1. Load the playbook data + state legal requirements
2. For a given (state, program, agency) combination, assemble the relevant components
3. Feed them to an LLM with our prompt (@drafting_prompt.text) like: 

```text
"You are a legal writing assistant. 

## Instruction:
1. Compose a formal public records request letter using ONLY the information provided below. Do not add, infer, or fabricate any facts.

2. Validation:
Before any draft is accepted, validate:

* Does it name the right law?
* Does it target the right office?
* Does it ask for **records**, not answers?
* Does it specify a time range?
* Does it request existing materials only?
* Does it request format / delivery clearly?
* Does it include requester details required in that state?
* Does it avoid asking the agency to create a new analysis?
"
```

4. Output the draft to `generated_requests/{state}_{program}_{agency}.txt`


### Phase 5: Validation

**Layer 1 — MuckRock precedent validation** (new, per proposal A2.2):
Compare generated requests against successful precedents from MuckRock. This could be:
- An LLM-as-judge approach: give the LLM a successful MuckRock request + your generated request, ask it to identify structural mismatches (missing legal citation, missing fee waiver, scope too broad, etc.)
- Or simpler: a checklist of required elements (statute cited? fee waiver included? specific records described? deadline noted?) verified programmatically

**Layer 2 — Human review gate**:
All requests are reviewed by a human before submission. This is non-negotiable per the proposal.