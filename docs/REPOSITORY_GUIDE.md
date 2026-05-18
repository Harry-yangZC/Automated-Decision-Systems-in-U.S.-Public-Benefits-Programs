# Repository Guide

A non-technical orientation to the Benefits Decoded codebase, intended for the collaborators and future researchers who want to know where something lives without reading code and onboarding handoff.

For the technical pipeline (installation, run commands, file formats), see
the project [README](../README.md). For design rationale see
`[pipeline/workflow_design_V2.md](../pipeline/workflow_design_V2.md)`.

---

## 30-second tour

Benefits Decoded is a Brown Data Science Institute project that uses LLMs
plus human review to build a national, public, auditable dataset of
**Automated Decision Systems (ADS)** used in U.S. public benefits programs
(SNAP, Medicaid, TANF, WIC, LIHEAP, CHIP).

The project's pipeline turns *official state government webpages and
successful public-records productions* into *validated structured data*,
and that data into *state-compliant public records request letters*.

Right now the project is running a vertical pilot — **Massachusetts × SNAP**
only — end to end before scaling. Phase 1 (research and schema) and Phase 2
(question set and benchmark) are complete; the rest of the pipeline
(extraction, drafting, validation, promotion gates) is next.

---

## Folder-by-folder walkthrough

This section names every top-level directory and the most important
subdirectories, in plain language.

### Top of the repo


| Path                                      | Purpose                                                                                                                                                                   | Who reads      | Who writes      |
| ----------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------- | --------------- |
| `[README.md](../README.md)`               | High-level technical README: project description, what has been completed, current preliminary observations, next steps, repository structure, setup, and usage commands. | Everyone       | RA + PI         |
| `[requirements.txt](../requirements.txt)` | Python package dependencies. Used by `pip install -r requirements.txt`.                                                                                                   | Tech reviewers | RA              |
| `.env`                                    | API keys (OpenRouter). **Not committed.** Each new RA creates this file locally.                                                                                          | RA             | RA (local only) |
| `[.gitignore](../.gitignore)`             | Lists files that should not be checked into version control (the proposal PDF, the local production package, `.DS_Store`, etc.).                                          | Tech reviewers | RA              |


### `pipeline/` — the V2 vertical pilot

This is where almost all of the active work lives. The structure mirrors
the six-phase workflow design.


| Path                                                                                                | Purpose                                                                                                                                                                                                                                                        |
| --------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `[pipeline/workflow_design_V1.md](../pipeline/workflow_design_V1.md)`                               | The first sketch of the pipeline. Superseded by V2 but kept as design history; do not edit.                                                                                                                                                                    |
| `[pipeline/workflow_design_V2.md](../pipeline/workflow_design_V2.md)`                               | The **canonical** design document. Six phases (research, questions, extraction, drafting, validation, promotion gates) plus open risks and promotion criteria. Read this first if you are new.                                                                 |
| `[pipeline/gold_letters/](../pipeline/gold_letters/)`                                               | The reference public records request letter for MA × SNAP, plus its annotation and provenance notes. The "gold letter" is the operational quality target — the letter we would actually want to send.                                                          |
| `[pipeline/gold_letters/gold_letter.pdf](../pipeline/gold_letters/gold_letter.pdf)`                 | PI-provided **successful** DTA production package (response letter + Thomson Reuters / West Publishing contracts). The empirical evidence that a request with this scope produces real benefits-tech records. **Local only; gitignored.**                      |
| `[pipeline/gold_letters/outbound_PRR.txt](../pipeline/gold_letters/outbound_PRR.txt)`               | The PI's outbound public records request scope text, verbatim. The gold letter's substantive scope is verified against this file.                                                                                                                              |
| `[pipeline/gold_letters/MA_SNAP.md](../pipeline/gold_letters/MA_SNAP.md)`                           | The V2 reference letter — the actual draft text we would submit.                                                                                                                                                                                               |
| `[pipeline/gold_letters/MA_SNAP.annotated.md](../pipeline/gold_letters/MA_SNAP.annotated.md)`       | Same letter, every word tagged as one of `slot` (pulled from the playbook), `module` (a reusable content block), or `boilerplate` (fixed across all letters). This is the spec the schema implements.                                                          |
| `[pipeline/gold_letters/MA_SNAP.source_note.md](../pipeline/gold_letters/MA_SNAP.source_note.md)`   | Provenance, corrections log, and slot-confirmation table. Always read this before making changes to the letter.                                                                                                                                                |
| `[pipeline/precedents/MA_DTA_ADS_2026/](../pipeline/precedents/MA_DTA_ADS_2026/)`                   | Phase 1b mining of the DTA production package: outbound request excerpt, document inventory, structured benefits-tech facts (vendors, products, pricing, deliverables), seeds for the request modules, and raw OCR of the scanned attachments.                 |
| `[pipeline/research/MA_SNAP_research.md](../pipeline/research/MA_SNAP_research.md)`                 | Consolidated Phase 1c deep-research deliverable. Reconciles two independent deep-research passes into a single chosen value per field with verbatim quotes and source URLs. This is the canonical research output.                                             |
| `[pipeline/step_1c_results/](../pipeline/step_1c_results/)`                                         | Raw deep-research outputs from the two 1c passes, preserved as research artifacts.                                                                                                                                                                             |
| `[pipeline/schemas/](../pipeline/schemas/)`                                                         | Three generic schemas covering state law, agency-program facts, and reusable request modules. Designed for all 50 states × 6 programs; only MA × SNAP is populated in V2.                                                                                      |
| `[pipeline/playbook/state_law/MA.json](../pipeline/playbook/state_law/MA.json)`                     | Massachusetts public-records-law facts (citation, deadlines, fee waiver, appeal pathway, oral-request rules, branch carveouts). Every field has an evidence row with a verbatim quote.                                                                         |
| `[pipeline/playbook/agency_program/MA_SNAP.json](../pipeline/playbook/agency_program/MA_SNAP.json)` | MA × SNAP operational facts (administering agency, RAO, contact, portal, known systems, vendors, structured benefits-tech facts). Mixed evidence: web sources for publicly-known facts; production-document evidence for facts only in the production package. |
| `[pipeline/request_modules/](../pipeline/request_modules/)`                                         | Eight reusable content blocks that form the body of the gold letter: procurement contracts, system documentation, staff-use materials, validation/accuracy audits, implementation deliverables, data dictionaries, risk alerts/dashboards, vendor support.     |
| `[pipeline/questions/question_spec.yaml](../pipeline/questions/question_spec.yaml)`                 | The Phase 2 question set: 47 hand-authored entries, one per web-extractable playbook field plus the production-doc vendor facts. Each entry carries `field_path`, `question_template`, `answer_format`, source pattern, certification threshold, and good/bad examples. Conforms to `pipeline/schemas/question_spec.schema.yaml`. |
| `[pipeline/questions/derive_benchmark.py](../pipeline/questions/derive_benchmark.py)`               | Reads `question_spec.yaml` and the two playbooks, resolves each `field_path`, and writes `pipeline/benchmarks/MA_SNAP_benchmark.csv` with one row per question. Re-run this whenever the spec or the playbook changes; never edit the benchmark CSV by hand.   |
| `[pipeline/questions/validate_question_spec.py](../pipeline/questions/validate_question_spec.py)`   | Phase 2 closure-check script. Runs three audits: schema conformance, forward closure (every web-extractable playbook leaf is covered or documented as excluded), reverse closure (every spec entry resolves to a non-null leaf). A green run is the gate from Phase 2 into Phase 3. |
| `[pipeline/benchmarks/MA_SNAP_benchmark.csv](../pipeline/benchmarks/MA_SNAP_benchmark.csv)`         | The Phase 2 ground-truth benchmark, one row per question. 15-column long format including verbatim evidence quote, source URL or production document, retrieval/receipt date, and answer-format metadata. Auto-derived by `derive_benchmark.py`.               |
| `[pipeline/prompts/](../pipeline/prompts/)`                                                         | Reserved for Phase 3a (typed short-answer extraction prompt) and Phase 4a (drafting prompt).                                                                                                                                                                   |
| `[pipeline/generated_requests/](../pipeline/generated_requests/)`                                   | Reserved for Phase 4b output: the drafted letter and its reproducibility snapshot.                                                                                                                                                                             |
| `[pipeline/validation/closure_check.py](../pipeline/validation/closure_check.py)`                   | Phase 1 closure-check script. Confirms every slot in the annotated gold letter resolves to a populated playbook value and every module reference has a YAML file.                                                                                              |
| `[pipeline/validation/muckrock_examples/](../pipeline/validation/muckrock_examples/)`               | Five MA MuckRock precedents for Phase 5b LLM-as-judge comparison. Three are direct ADS comparators (two DUA, one UMass Ocelot); two are tone-only comparators (older DTA SNAP requests).                                                                       |


### `data/` — input data for the prior 5-state benchmark


| Path                                                              | Purpose                                                                                                          |
| ----------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| `[data/benchmark.csv](../data/benchmark.csv)`                     | Hand-verified ground-truth answers for the 5-state × 4-program × 5-question benchmark that informed V2's design. |
| `[data/questions_reference.csv](../data/questions_reference.csv)` | Reference list of the question templates that drove the benchmark.                                               |


### `exp_results/` — the prior benchmark experiment

The 5-state × 3-model benchmark whose results are reported in the
README's "Preliminary observations" section. Useful as historical context;
not currently being re-run.


| Path                                                                                    | Purpose                                                                              |
| --------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| `[exp_results/run_experiment.py](../exp_results/run_experiment.py)`                     | Calls the LLMs via OpenRouter; supports multiple runs per question and model.        |
| `[exp_results/summarize_experiments.py](../exp_results/summarize_experiments.py)`       | Aggregates raw runs into majority answers and per-cell agreement rates.              |
| `[exp_results/score_experiments.py](../exp_results/score_experiments.py)`               | Compares majority answers to the benchmark ground truth with question-type matchers. |
| `[exp_results/LLM_experiments.csv](../exp_results/LLM_experiments.csv)`                 | Raw run results (375 rows).                                                          |
| `[exp_results/LLM_experiments_summary.csv](../exp_results/LLM_experiments_summary.csv)` | Aggregated summary rows.                                                             |
| `[exp_results/LLM_experiments_scored.csv](../exp_results/LLM_experiments_scored.csv)`   | Scored cells.                                                                        |


### `exp_analysis/` — four-tier analysis pipeline

Reads the prior benchmark CSVs and generates plots, tables, and per-tier
summary markdown under `reports/`. Each tier covers one type of analysis
(accuracy, calibration, error taxonomy, source grounding).

### `reports/` — generated analysis output

Stitched narrative and figures from the four-tier analysis. Open
`[reports/README.md](../reports/README.md)` for an index.

### `docs/` — project documentation


| Path                                                  | Purpose                                                    |
| ----------------------------------------------------- | ---------------------------------------------------------- |
| `[docs/REPOSITORY_GUIDE.md](REPOSITORY_GUIDE.md)`     | This file.                                                 |
| `[docs/scoring_strategies.md](scoring_strategies.md)` | Design notes on question-type-aware accuracy scoring.      |
| `docs/Benefits_Decoded_Project_Proposal.pdf`          | The original project proposal. **Local only; gitignored.** |


---

## Glossary


| Term                           | Plain definition                                                                                                                                                                                                             |
| ------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **ADS**                        | Automated Decision System. Any algorithm, data-matching program, AI, ML, or predictive analytic that helps a government agency decide who gets benefits, who is investigated for fraud, or whose case is flagged for review. |
| **PRR**                        | Public Records Request. A formal request to a government agency for copies of records, under state public-records law. The federal equivalent is FOIA.                                                                       |
| **RAO**                        | Records Access Officer. The person designated by an agency to handle PRRs. In Massachusetts, every agency must have one.                                                                                                     |
| **SNAP**                       | Supplemental Nutrition Assistance Program. Formerly "food stamps." A federal nutrition program administered by each state's benefits agency.                                                                                 |
| **DTA**                        | Massachusetts Department of Transitional Assistance. The state agency that administers SNAP, TAFDC, and EAEDC.                                                                                                               |
| **TAFDC, EAEDC**               | The other two main MA benefits programs DTA administers (Transitional Aid to Families with Dependent Children; Emergency Aid to Elders, Disabled, and Children).                                                             |
| **BEACON, EPPIC, DTA Connect** | The three MA DTA benefit-administration systems publicly named in audits. BEACON is primary eligibility/case management; EPPIC distributes EBT; DTA Connect is the client-facing case portal.                                |
| **CLEAR, IDRA**                | Thomson Reuters / West Publishing products that DTA contracts with for identity verification and risk analytics. Surfaced in the production package we received.                                                             |
| **MuckRock**                   | A nonprofit transparency website where individuals file and track public records requests; many are publicly viewable, including agency responses. We use it as a source of precedent letters.                               |
| **NFOIC**                      | National Freedom of Information Coalition. Maintains per-state guides to public-records laws.                                                                                                                                |
| **slot**                       | A field in the gold letter whose value is pulled from the playbook (e.g., the statute citation). Slots come from `state_law.`* or `agency_program.*` paths.                                                                  |
| **module**                     | A reusable content block in the gold letter (e.g., the "procurement contracts" paragraph). Modules are jurisdiction-independent prose with placeholders that get filled at draft time.                                       |
| **boilerplate**                | Fixed wording in the gold letter that does not change across states or programs (e.g., the closing courtesy line).                                                                                                           |
| **gold letter**                | The reference letter we would actually want to send. Phase 5 Layer 2 measures LLM-drafted letters by character-edit distance to this letter.                                                                                 |
| **closure check**              | The script that confirms every slot in the annotated gold letter has a corresponding populated value in the playbook. Per V2 §5.5, a green closure check is the gate from Phase 1 into Phase 2.                              |
| **playbook**                   | The combined `(state_law, agency_program)` JSON data that the gold letter draws facts from. One row per state and one row per (state, program). Only MA and MA × SNAP are populated in V2.                                   |
| **production package**         | A successful agency response to a public records request, including the cover letter and the produced documents. Used as ground-truth evidence that a particular request scope produces useful records.                      |
| **Layer 1a / 1b / Layer 2**    | The three stages of Phase 5 validation. Layer 1a is a deterministic checklist (no LLM cost). Layer 1b is an LLM-as-judge comparison against successful precedents. Layer 2 is human review.                                  |
| **certification tier**         | The label assigned to each cell of the Phase 3 extraction output: auto-certify, soft-certify, or manual-queue.                                                                                                               |


---

## Where do I put a new ___?


| If you have …                                        | Put it here                                                                                                                                                                                                                        |
| ---------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| A new gold letter for another (state, program) cell  | `pipeline/gold_letters/<STATE>_<PROGRAM>.md` + matching `.annotated.md` + `.source_note.md`. Reuse the MA × SNAP file structure as the template.                                                                                   |
| A new successful production package from an agency   | `pipeline/precedents/<STATE>_<AGENCY>_<TOPIC>_<YEAR>/` with the four files we used for MA DTA (request_excerpt, production_inventory, extracted_facts, request_module_seeds). OCR pages with no text layer.                        |
| A new state's public-records-law data                | `pipeline/playbook/state_law/<STATE>.json`. Conform to `pipeline/schemas/state_law.schema.json`. Every field needs an evidence row.                                                                                                |
| A new (state, program) row                           | `pipeline/playbook/agency_program/<STATE>_<PROGRAM>.json`. Conform to `pipeline/schemas/agency_program.schema.json`.                                                                                                               |
| A new MuckRock or other precedent letter             | `pipeline/validation/muckrock_examples/<state>_<agency>_<topic>_<year>.md` with the YAML frontmatter we used (url, agency, state, program, filed_by, request_date, status, relevance, relevance_notes).                            |
| A new request-module body block                      | `pipeline/request_modules/<id>.yaml`. Update `pipeline/gold_letters/MA_SNAP.annotated.md` to reference it as `[[module:                                                                                                            |
| A new schema field                                   | The relevant schema file in `pipeline/schemas/`. Then update every populated playbook row to either include the new field or have an evidence row explaining a negative finding. Then re-run the closure check.                    |
| A new question_spec entry for an existing playbook field | Add a YAML block to `pipeline/questions/question_spec.yaml`, conforming to `pipeline/schemas/question_spec.schema.yaml`. Then re-run `python pipeline/questions/validate_question_spec.py` to confirm closure, and `python pipeline/questions/derive_benchmark.py` to regenerate the benchmark.                                  |
| A new derivation rule or audit                       | `pipeline/questions/derive_benchmark.py` (composition rules for fields whose ground-truth string is composed from multiple playbook leaves) or `pipeline/questions/validate_question_spec.py` (closure audits). Keep `EXCLUDED_PATHS` documented with a reason string for every excluded path.                                    |
| A new research source (e.g., a state legal handbook) | If it informs Layer A of the research deliverable, cite it in `pipeline/research/MA_SNAP_research.md` (or the equivalent file for that state). If it informs the gold letter, also add to the source-note's cross-references list. |
| A new run of the experiment pipeline (CSV outputs)   | `exp_results/`. Use the existing CSV filenames so the analysis pipeline picks them up.                                                                                                                                             |
| A new analysis script or plot                        | `exp_analysis/`. Update `reports/README.md` to reference any new plots.                                                                                                                                                            |


---

## Onboarding checklist

A new researcher member can quickly onboard by doing these in order.

1. **Read this guide end to end** (you are doing that now). Spend ~15
  minutes.
1. **Read `[pipeline/workflow_design_V2.md](../pipeline/workflow_design_V2.md)*`*
  end to end. This is the canonical pipeline design. Spend ~60 minutes.
1. **Install dependencies.** From the repo root:
  ```bash
   pip install -r requirements.txt
  ```
   Add OCR tools if you may need to mine new production packages with
   scanned attachments:
   Create `.env` at the repo root with your OpenRouter API key.
1. **Run the Phase 1 closure check** to confirm your local checkout is
  consistent with what is committed:
   ```bash
   python pipeline/validation/closure_check.py
   ```
   Expected output ends with `PASS  Phase 1 closure check is GREEN.`
1. **Run the Phase 2 closure check** to confirm the question set and the
  populated playbook still agree:
   ```bash
   python pipeline/questions/validate_question_spec.py
   ```
   Expected output ends with `PASS  Phase 2 closure check is GREEN.` If you
   subsequently edit `question_spec.yaml` or either playbook JSON, also
   regenerate the benchmark with `python pipeline/questions/derive_benchmark.py`.
6. **Skim the consolidated research file**
  `[pipeline/research/MA_SNAP_research.md](../pipeline/research/MA_SNAP_research.md)`
   and the two raw deep-research passes under
   `[pipeline/step_1c_results/](../pipeline/step_1c_results/)`. This is what
   the MA × SNAP playbook is built from.
1. **Open
  `[pipeline/gold_letters/MA_SNAP.annotated.md](../pipeline/gold_letters/MA_SNAP.annotated.md)`**
   side by side with the playbook JSON files. Trace at least three slots
   through the annotation to the playbook to the evidence URL. By the time
   that traversal feels routine, you have a working grasp of the V2 design.

After that, the natural next thing to work on is Phase 3 — the typed
short-answer extraction prompt and tiered certification gate (see V2 §7).

---

## When to update this guide

This guide is intended to track the **current** repository layout. Update
it when:

- A new top-level directory is added under `pipeline/` or the repo root.
- A new project-level documentation file is added under `docs/`.
- A previously reserved directory (e.g. `pipeline/questions/`) is populated
for the first time; update the table row to describe what it now contains.
- A core term changes meaning (rare).

This guide is **not** the place to record day-to-day implementation
progress — that lives in the README's "What has been completed" section.