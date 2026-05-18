# Benefits Decoded

A reproducible, LLM-assisted national public records campaign to document **Automated Decision Systems (ADS)** in U.S. public benefits programs.

Brown University Data Science Institute, Spring 2026.

## Motivation

Around 92 million low-income people in the U.S. are exposed to AI-related decision-making in public benefits programs (SNAP, Medicaid, TANF, WIC, LIHEAP, CHIP) through eligibility, enrollment, or prior-authorization processes. Despite the stakes, there is no comprehensive, public, nationwide dataset documenting which ADS are used, who built them, how they shape decisions, or what audits govern their use.

This project aims to fill that gap by building the first auditable national dataset of ADS in public benefits programs, using a human-in-the-loop, LLM-assisted public records workflow.

## Project Pipeline

The project follows a four-stage pipeline:

### Stage 1 — Discovery (Aim 1): Validated Request Playbook

Build a structured, reproducible dataset identifying administering agencies, public-records submission procedures, and statutory requirements across all 50 states. LLM-assisted extraction from official sources is validated via cross-model benchmarking: the same prompts are run across multiple frontier LLMs, and entries require agreement with a hand-verified benchmark test set.

### Stage 2 — Drafting (Aim 2): Modular Request Library & Campaign

Generate state-compliant ADS transparency request templates from modular components (ADS inventory, vendor/contracts, audits, policies, decision workflows). Validate request language against successful precedents in MuckRock. Execute a pilot campaign (5 states x 2 agencies) before nationwide expansion.

### Stage 3 — Processing (Aim 3): Ingestion & Extraction

Process agency response documents (contracts, manuals, audits) using a secure, human-in-the-loop LLM extraction pipeline. Each extracted ADS claim is linked to its source document with page/section references, reviewer-verification flags, and ambiguity markers.

### Stage 4 — Dataset Construction

Assemble a versioned national dataset with provenance, uncertainty flags, and reviewer-verification status, supporting transparency research, governance evaluation, and tool-building.

## Current Progress

Stage 1 is in progress. We have completed an initial 5-state LLM-extraction benchmark, built a four-tier analysis pipeline over those results, and used the findings to design a next-stage workflow (`[pipeline/workflow_design_V2.md](pipeline/workflow_design_V2.md)`) that narrows Stage 1 to an end-to-end **Massachusetts x SNAP** vertical pilot before scaling.

### What has been completed

- **Benchmark test set** with 5 question templates, 4 programs, and 5 pilot states (MA, RI, CA, NY, TX), each with hand-verified ground-truth answers.
- **Experiment runner** (`run_experiment.py`) that queries models via OpenRouter, collects structured JSON responses (answer, source, confidence), supports multiple runs per combination, and resumes from partial results.
- **Summary pipeline** (`summarize_experiments.py`) that aggregates across runs to compute majority answers, agreement rates, and average confidence per (question, program, state, model).
- **Accuracy scoring** (`score_experiments.py`) that joins summary rows to `[data/benchmark.csv](data/benchmark.csv)` and scores each majority answer with question-type-aware matchers (agency abbreviation; primary response-time deadline with an extension-clause guard; address via zip, then PO Box, then street number; case-insensitive exact email; phone patterns normalized to 10 digits). Writes `[exp_results/LLM_experiments_scored.csv](exp_results/LLM_experiments_scored.csv)` and prints aggregate statistics.
- **Repository layout** — inputs under `data/`, experiment outputs under `exp_results/`, and project docs under `docs/`. The proposal PDF is expected at `docs/Benefits_Decoded_Project_Proposal.pdf` locally but is **not** committed (see [.gitignore](.gitignore)); clones receive code, benchmark, and results CSVs without that file.
- **Initial experiment results** (375 raw rows, 75 summary rows, 75 scored rows) from three models: Google Gemma 4 26B A4B IT (paid), OpenAI GPT-OSS-120B (free), and Anthropic Claude Opus 4.7 (paid).
- **Four-tier analysis pipeline** (`[exp_analysis/](exp_analysis/)`) over the 375 raw runs: headline accuracy, calibration and self-consistency, error taxonomy and consolidation gap, and source grounding. Regenerates plots, tables (CSV + Markdown), and per-tier summaries under `[reports/](reports/)`, stitched together by `[reports/README.md](reports/README.md)`.
- **Workflow design docs** for the next stage of Stage 1: `[pipeline/workflow_design_V1.md](pipeline/workflow_design_V1.md)` introduces the composable-template idea (an LLM composing prose from validated structured slots, not inventing facts); `[pipeline/workflow_design_V2.md](pipeline/workflow_design_V2.md)` supersedes V1 with a vertical-pilot architecture for **MA x SNAP** -- gold-letter spec-by-example, three-artifact playbook decomposition (`state_law` / `agency_program` / `request_modules`), typed short-answer extraction, tiered certification, programmatic-then-semantic validation, and explicit promotion gates from MA x SNAP to multi-program and multi-state.
- **Repository hygiene update:** the workflow design directory has been renamed from the misspelled `pipline/` path to the canonical `[pipeline/](pipeline/)` path. The V1 prompt and empty playbook placeholders have been removed now that V2 Phase 1 is complete.
- **V2 Phase 1 (Research & Schema) — completed:** the MA × SNAP gold-letter trio (`[MA_SNAP.md](pipeline/gold_letters/MA_SNAP.md)`, `[MA_SNAP.annotated.md](pipeline/gold_letters/MA_SNAP.annotated.md)`, `[MA_SNAP.source_note.md](pipeline/gold_letters/MA_SNAP.source_note.md)`); the DTA production package mined into `[pipeline/precedents/MA_DTA_ADS_2026/](pipeline/precedents/MA_DTA_ADS_2026/)` (request scope, document inventory, structured benefits-tech facts, request-module seeds, plus raw OCR text for the scanned attachments); two GPT deep-research passes consolidated at `[pipeline/research/MA_SNAP_research.md](pipeline/research/MA_SNAP_research.md)`; three generic schemas under `[pipeline/schemas/](pipeline/schemas/)` (state_law, agency_program, request_modules); eight production-grounded request modules under `[pipeline/request_modules/](pipeline/request_modules/)`; the MA state-law row and MA × SNAP agency-program row under `[pipeline/playbook/](pipeline/playbook/)`, every field carrying `evidence[]` rows with verbatim quotes; and five MA MuckRock precedents under `[pipeline/validation/muckrock_examples/](pipeline/validation/muckrock_examples/)` for Phase 5b. The Phase 1 closure check at `[pipeline/validation/closure_check.py](pipeline/validation/closure_check.py)` (V2 §5.5) is green: 21 of 21 playbook slots resolve, 8 of 8 modules present.
- **V2 design refinement — single-model Phase 3:** Phase 3 of the V2 pipeline was reduced from the originally-proposed three-model (`Claude Opus 4.7`, `Gemma`, `GPT-OSS`) self-consistency to a single web-tool-enabled model (`Claude Opus 4.7`). The change is motivated by the preliminary Tier 1 result — Opus 76% vs Gemma 44% vs GPT-OSS 36% — which shows cross-model agreement is dominated by the strongest model. Multi-model cross-checking is deferred to future work; see `[pipeline/workflow_design_V2.md](pipeline/workflow_design_V2.md)` §7.3 and §14.
- **V2 Phase 2 (Question set & benchmark) — completed:** the question-spec schema at `[pipeline/schemas/question_spec.schema.yaml](pipeline/schemas/question_spec.schema.yaml)`; 47 hand-authored question entries at `[pipeline/questions/question_spec.yaml](pipeline/questions/question_spec.yaml)` covering every web-extractable field in the populated playbook (22 state-law facts, 17 agency-program operational facts, and 8 production-document vendor facts flagged `extraction_mode: manual_production_doc`); the derivation script `[pipeline/questions/derive_benchmark.py](pipeline/questions/derive_benchmark.py)` that resolves each `field_path` against the joined playbook and emits the V2 §6.2 long-format benchmark `[pipeline/benchmarks/MA_SNAP_benchmark.csv](pipeline/benchmarks/MA_SNAP_benchmark.csv)` (47 rows, 15 columns, one row per question, ground-truth values copied directly from the playbook); and the Phase 2 closure check at `[pipeline/questions/validate_question_spec.py](pipeline/questions/validate_question_spec.py)` running three audits (schema conformance, forward closure with 28 documented exclusions, reverse closure). All three audits are green: 47 of 47 entries conform to the schema, 47 of 47 `field_path` values resolve to non-null leaves, and every uncovered playbook leaf is either composed into a sibling question or documented in `EXCLUDED_PATHS`.

### Preliminary observations

- **Coverage is now 100%** across all three models — every (question, state) cell has a majority answer, a substantial improvement over the prior run where Meta Llama 3.3 70B failed systematically to return extractable answers.
- **Accuracy ranking** (25 scored cells per model): Claude Opus 4.7 **76% (19/25)**, Gemma 4 26B A4B IT **44% (11/25)**, GPT-OSS-120B **36% (9/25)**.
- **Question-type pattern:** every model nails *agency identification* (15/15 = 100%) and most *response_time* questions (12/15 = 80%); *address* (5/15 = 33%), *phone* (5/15 = 33%), and *email* (2/15 = 13%) fields are materially harder across the board.
- **Phone numbers are an Opus-only success:** Opus answers 5/5 correctly, while Gemma and GPT-OSS each answer 0/5 — the free/cheap models tend to surface general public-assistance hotlines or hallucinate plausible-looking digits instead of the LIHEAP-specific number in the benchmark.
- **Cross-run agreement:** Opus's mean agreement rate (0.49) is roughly double Gemma's and GPT-OSS's (0.23 each), suggesting Opus produces materially more consistent phrasings of the same answer across the 5 runs.
- **Scoring snapshot (current pilot run):** Agency names match essentially universally; public-records response-time answers are mostly correct with occasional confusion between the primary deadline and the extension clause; mailing addresses, WIC public-records emails, and LIHEAP phone numbers remain the hardest fields, reflecting both model grounding limits and strict exact-match scoring for those fields.
- **Self-reported confidence is poorly calibrated:** `confidence=high` covers 330 of the 375 runs but only **54%** of those runs are correct (95% CI 48-59%). Confidence cannot be used as a standalone trust signal -- this is one of the motivations for V2's tiered certification gate. See Tier 2 (`reports/plots/tier2/t2_02_confidence_calibration.png`).
- **Cross-model error overlap:** **6 of 25** cells are wrong across all three models and **9 of 25** are correct across all three; the remaining 10 cells reveal model-specific knowledge gaps that cross-model agreement is well-suited to catch. See Tier 3 (`reports/plots/tier3/t3_01_models_wrong_histogram.png`).
- **pass@5 vs maj@5 oracle gap is small** (Opus +0%, Gemma +4%, GPT-OSS +12%): majority voting over 5 runs recovers most of what an oracle best-of-5 could, so adding more runs has diminishing returns relative to switching models or improving prompts. See Tier 3 (`reports/plots/tier3/t3_03_pass_at_k_vs_maj.png`).
- **Source grounding is necessary but not sufficient:** `.gov` citation rates are similar across correct and incorrect cells (e.g. Gemma cites `.gov` on 99% of *incorrect* cells), and state-domain pattern matches are near-universal regardless of correctness. A URL filter alone won't gate quality -- V2 layers in verbatim-quote retrieval grounding on top of source-domain checks. See Tier 4 (`reports/plots/tier4/t4_02_gov_ratio_vs_correctness.png`).
- **Scorer-strictness audit:** 9 of 36 incorrect cells still contain a ground-truth fragment (zip code, email domain, agency abbreviation, deadline number), suggesting some "incorrect" verdicts are matcher artifacts rather than model errors. V2's typed short-answer extraction is designed to collapse this ambiguity by constraining outputs at generation time rather than parsing free prose at scoring time.

### Next steps (per `[pipeline/workflow_design_V2.md](pipeline/workflow_design_V2.md)`)

The immediate plan is the **MA x SNAP vertical pilot** (V2 Phases 1-5), running the full Stage 1 -> Stage 2 path on a single (state, program) cell before adding a second state or program. Phases 1 and 2 are complete; Phase 3 is the next active phase.

1. **Phase 1 - Research & schema (completed).** Hand-write the MA SNAP gold letter and annotate every word as `slot | module | boilerplate`. Decompose the playbook into three artifacts (`state_law`, `agency_program`, `request_modules`) and manually populate the MA and MA x SNAP rows with per-field evidence URLs, verbatim quotes, and `retrieved_at` timestamps.
2. **Phase 2 - Question set (completed).** Hand-author `question_spec.yaml` covering every web-extractable playbook field plus the production-document vendor facts (47 entries), and auto-derive `MA_SNAP_benchmark.csv` from the spec plus playbook so the benchmark and the ground truth never drift apart. Validate with a three-audit Phase 2 closure check (schema conformance, forward closure with documented exclusions, reverse closure).
3. **Phase 3 - Typed short-answer extraction (next active phase).** Replace today's free-form research prompt with a per-format prompt that constrains the LLM to a single typed value (e.g. 10-digit phone, statute citation <= 60 chars), uses a single web-tool-enabled model (Claude Opus 4.7) for retrieval grounding, and runs the tiered certification gate (auto-certify / soft-certify / manual queue) combining single-model self-consistency and source-domain matching. Multi-model cross-checking is deferred to future work; the prior three-model benchmark showed cross-model agreement is dominated by the single strongest model.
4. **Phase 4 - Drafting.** Join the populated playbook with selected request modules and few-shot MuckRock precedents; have the drafting LLM compose the letter plus a structured `<validation>` block listing every slot location.
5. **Phase 5 - Validation.** Run Layer 1a (programmatic checklist) first, then Layer 1b (LLM-as-judge against MuckRock precedents) only on drafts that pass 1a, then Layer 2 (human review against the gold letter, with character-edit-distance acceptance criteria).
6. **Phase 6 - Promotion gates.** Promote from MA x SNAP to MA x {6 programs} to 5 states x 2 programs to nationwide scale on quantitative criteria (auto-certification rate, draft acceptance rate, real-submission response rate). Each gate adds exactly one axis of variation so failures are diagnosable.

### Longer-term (proposal aims)

- Experiments with additional frontier thinking models (latest OpenAI GPT and Google Gemini) once V2's typed-extraction prompt is in place.
- Scaling from 5 pilot states to all 50, and from SNAP to the full six-program set (SNAP, Medicaid, TANF, WIC, LIHEAP, CHIP).
- Stages 2-4 of the pipeline: nationwide drafting campaign, agency-response document ingestion and extraction, and versioned national dataset construction.

## Repository Structure

```
├── README.md
├── requirements.txt
├── .env                              # OPENROUTER_API_KEY (not committed)
├── exp_results/
│   ├── run_experiment.py             # LLM experiment runner (OpenRouter)
│   ├── summarize_experiments.py      # Aggregates raw runs into summary rows
│   ├── score_experiments.py          # Scores summary answers against benchmark
│   ├── LLM_experiments.csv           # Raw experiment results
│   ├── LLM_experiments_summary.csv   # Aggregated summary results
│   └── LLM_experiments_scored.csv    # Accuracy scores vs benchmark
├── exp_analysis/
│   ├── common.py                     # Shared loaders / grading / plot helpers
│   ├── tier1_accuracy.py             # Tier 1: headline accuracy tables & plots
│   ├── tier2_calibration.py          # Tier 2: calibration & self-consistency
│   ├── tier3_errors.py               # Tier 3: error taxonomy & pass@k gap
│   ├── tier4_sources.py              # Tier 4: sources & grounding
│   └── run_all_tiers.py              # Orchestrator (--tier {1,2,3,4,all})
├── data/
│   ├── benchmark.csv                 # Hand-verified ground-truth answers
│   └── questions_reference.csv       # Question template reference (Google Sheets)
├── reports/
│   ├── plots/tier{1..4}/             # Saved PNGs per tier
│   ├── tables/tier{1..4}/            # CSV + Markdown tables per tier
│   ├── data/                         # Derived intermediates (e.g. raw_graded.csv)
│   └── README.md                     # Stitched narrative + thumbnail index
├── pipeline/                         # V2 vertical pilot: design, artifacts, validation
│   ├── workflow_design_V1.md         # Initial composable-template concept (superseded; kept as history)
│   ├── workflow_design_V2.md         # Canonical V2 design: MA x SNAP vertical pilot
│   ├── gold_letters/
│   │   ├── gold_letter.pdf           # PI-provided successful DTA production package; gitignored
│   │   ├── outbound_PRR.txt          # PI-provided outbound PRR scope (verbatim)
│   │   ├── MA_SNAP.md                # V2 reference letter for MA SNAP (Phase 1a)
│   │   ├── MA_SNAP.annotated.md      # Per-word slot|module|boilerplate annotation (Phase 1a)
│   │   └── MA_SNAP.source_note.md    # Provenance, corrections log, slot-confirmation table
│   ├── precedents/
│   │   └── MA_DTA_ADS_2026/          # Phase 1b mining of the DTA production package
│   │       ├── request_excerpt.md
│   │       ├── production_inventory.yaml
│   │       ├── extracted_facts.yaml  # Structured benefits-tech facts (CLEAR, IDRA, etc.)
│   │       ├── request_module_seeds.yaml
│   │       └── raw_ocr/              # macOS Vision OCR of pp. 3-12 (scanned attachments)
│   ├── research/
│   │   └── MA_SNAP_research.md       # Consolidated Phase 1c deep-research deliverable
│   ├── step_1c_results/              # Raw 1c outputs (preserved as research artifacts)
│   │   ├── deep-research-report_1.md
│   │   └── deep-research-report_2.md
│   ├── schemas/                      # V2 §5.4 / §6.1 — generic schemas across all 50 states
│   │   ├── state_law.schema.json
│   │   ├── agency_program.schema.json
│   │   ├── request_modules.schema.yaml
│   │   └── question_spec.schema.yaml # Phase 2 — contract for question_spec.yaml entries
│   ├── playbook/                     # Per-row populated facts (only MA x SNAP in V2)
│   │   ├── state_law/MA.json
│   │   └── agency_program/MA_SNAP.json
│   ├── request_modules/              # Eight production-grounded modules (V2 §5.4)
│   │   ├── procurement_contracts_rfps.yaml
│   │   ├── system_documentation.yaml
│   │   ├── staff_use_policies_training.yaml
│   │   ├── validation_accuracy_audits.yaml
│   │   ├── implementation_deliverables.yaml
│   │   ├── data_inputs_and_dictionaries.yaml
│   │   ├── risk_alerts_thresholds_dashboards.yaml
│   │   └── vendor_support_change_requests.yaml
│   ├── questions/                    # Phase 2 question set + tooling (V2 §6.1)
│   │   ├── question_spec.yaml        # 47 hand-authored question entries
│   │   ├── derive_benchmark.py       # Emits MA_SNAP_benchmark.csv from spec + playbook
│   │   └── validate_question_spec.py # Phase 2 closure check (3 audits)
│   ├── benchmarks/                   # Phase 2 derived benchmark (V2 §6.2)
│   │   └── MA_SNAP_benchmark.csv     # 47 rows, 15 columns; long-format, regenerable
│   ├── prompts/                      # Reserved for Phase 3a/4a prompt files
│   ├── generated_requests/           # Reserved for Phase 4b drafted letters
│   └── validation/
│       ├── closure_check.py          # Phase 1 closure check (V2 §5.5)
│       └── muckrock_examples/        # Five MA precedents for Phase 5b LLM-as-judge
└── docs/
    ├── scoring_strategies.md
    ├── REPOSITORY_GUIDE.md           # Non-technical orientation + RA onboarding
    └── Benefits_Decoded_Project_Proposal.pdf   # local only; gitignored
```

## Setup

```bash
pip install -r requirements.txt
```

Create a `.env` file in the project root with your [OpenRouter](https://openrouter.ai/) API key:

```
OPENROUTER_API_KEY=sk-or-...
```

**Note:** Two of the default models are **paid** on OpenRouter: `[anthropic/claude-opus-4.7](https://openrouter.ai/anthropic/claude-opus-4.7)` ($5 / $25 per 1M input/output tokens) and `[google/gemma-4-26b-a4b-it](https://openrouter.ai/google/gemma-4-26b-a4b-it)` ($0.13 / $0.40 per 1M). At the default `--runs 5`, a full sweep costs roughly **$0.60–$1.00** for Opus and well under **$0.05** for Gemma; `openai/gpt-oss-120b:free` is free. Ensure your OpenRouter account has credit before running, or override `--models` to exclude paid entries.

## Usage

All pipeline commands below are intended to be executed from the repository root (so that the default `data/...` and `exp_results/...` paths resolve correctly).

### Run experiments

```bash
python exp_results/run_experiment.py
```

Key options:


| Flag          | Default                                                  | Description                                 |
| ------------- | -------------------------------------------------------- | ------------------------------------------- |
| `--models`    | `gemma-4-26b-a4b-it, gpt-oss-120b:free, claude-opus-4.7` | Comma-separated OpenRouter model IDs        |
| `--benchmark` | `data/benchmark.csv`                                     | Path to benchmark CSV                       |
| `--output`    | `exp_results/LLM_experiments.csv`                        | Output path for raw results                 |
| `--runs`      | `5`                                                      | Number of runs per (question, state, model) |
| `--delay`     | `3.0`                                                    | Seconds between API calls                   |


The runner is **resume-safe**: re-running the same command skips already-completed entries and retries any previous errors.

### Summarize results

```bash
python exp_results/summarize_experiments.py
```


| Flag       | Default                                   | Description                |
| ---------- | ----------------------------------------- | -------------------------- |
| `--input`  | `exp_results/LLM_experiments.csv`         | Path to raw experiment CSV |
| `--output` | `exp_results/LLM_experiments_summary.csv` | Output path for summary    |


Produces one row per (question, program, state, model) with majority answer, agreement rate, unique sources, and average confidence score.

### Score against benchmark

```bash
python exp_results/score_experiments.py
```


| Flag          | Default                                   | Description                |
| ------------- | ----------------------------------------- | -------------------------- |
| `--summary`   | `exp_results/LLM_experiments_summary.csv` | Path to summary CSV        |
| `--benchmark` | `data/benchmark.csv`                      | Path to benchmark CSV      |
| `--output`    | `exp_results/LLM_experiments_scored.csv`  | Output path for scored CSV |


Compares each model's majority answer to the hand-verified ground truth using question-type-aware matching (agency abbreviation check, response-time deadline extraction, address zip/PO-box matching, exact email match, normalized phone-digit comparison). Outputs a scored CSV and prints aggregate accuracy statistics.

### Generate Tier 1-4 analysis artifacts

```bash
python exp_analysis/run_all_tiers.py --tier all
```

Reads `exp_results/LLM_experiments{,_summary,_scored}.csv` and writes tables (CSV + Markdown), plots (PNG), and a per-tier `summary.md` under `reports/`. Individual tiers can be rerun with `--tier 1|2|3|4`. The four tiers cover:

1. **Headline accuracy** — leaderboards and heatmaps across model x question-type x state x program.
2. **Calibration & self-consistency** — agreement distributions, confidence calibration, answer diversity.
3. **Error taxonomy & consolidation gap** — cross-model hard cases, matcher-strictness audit, pass@k vs maj@k.
4. **Sources & grounding** — domain distribution, .gov-ratio vs correctness, citation-state consistency.

## Team

- **PI:** Tomo Lazovich — Assistant Professor of the Practice (AI Governance and Policy), Brown University Data Science Institute
- **RA:** Zhaocheng (Harry) Yang — Graduate Student (Master's, 26'), Brown University Data Science Institute
