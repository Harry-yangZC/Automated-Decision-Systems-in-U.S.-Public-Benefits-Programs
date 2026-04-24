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

The project is in the **early experimental phase of Stage 1**, focused on LLM-assisted extraction benchmarking over a 5-state pilot.

### What has been completed

- **Benchmark test set** with 5 question templates, 4 programs, and 5 pilot states (MA, RI, CA, NY, TX), each with hand-verified ground-truth answers.
- **Experiment runner** (`run_experiment.py`) that queries models via OpenRouter, collects structured JSON responses (answer, source, confidence), supports multiple runs per combination, and resumes from partial results.
- **Summary pipeline** (`summarize_experiments.py`) that aggregates across runs to compute majority answers, agreement rates, and average confidence per (question, program, state, model).
- **Accuracy scoring** (`score_experiments.py`) that joins summary rows to [`data/benchmark.csv`](data/benchmark.csv) and scores each majority answer with question-type-aware matchers (agency abbreviation; primary response-time deadline with an extension-clause guard; address via zip, then PO Box, then street number; case-insensitive exact email; phone patterns normalized to 10 digits). Writes [`exp_results/LLM_experiments_scored.csv`](exp_results/LLM_experiments_scored.csv) and prints aggregate statistics.
- **Repository layout** — inputs under `data/`, experiment outputs under `exp_results/`, and project docs under `docs/`. The proposal PDF is expected at `docs/Benefits_Decoded_Project_Proposal.pdf` locally but is **not** committed (see [.gitignore](.gitignore)); clones receive code, benchmark, and results CSVs without that file.
- **Initial experiment results** (375 raw rows, 75 summary rows, 75 scored rows) from three models: Google Gemma 4 26B A4B IT (paid), OpenAI GPT-OSS-120B (free), and Anthropic Claude Opus 4.7 (paid).

### Preliminary observations

- **Coverage is now 100%** across all three models — every (question, state) cell has a majority answer, a substantial improvement over the prior run where Meta Llama 3.3 70B failed systematically to return extractable answers.
- **Accuracy ranking** (25 scored cells per model): Claude Opus 4.7 **76% (19/25)**, Gemma 4 26B A4B IT **44% (11/25)**, GPT-OSS-120B **36% (9/25)**.
- **Question-type pattern:** every model nails *agency identification* (15/15 = 100%) and most *response_time* questions (12/15 = 80%); *address* (5/15 = 33%), *phone* (5/15 = 33%), and *email* (2/15 = 13%) fields are materially harder across the board.
- **Phone numbers are an Opus-only success:** Opus answers 5/5 correctly, while Gemma and GPT-OSS each answer 0/5 — the free/cheap models tend to surface general public-assistance hotlines or hallucinate plausible-looking digits instead of the LIHEAP-specific number in the benchmark.
- **Cross-run agreement:** Opus's mean agreement rate (0.49) is roughly double Gemma's and GPT-OSS's (0.23 each), suggesting Opus produces materially more consistent phrasings of the same answer across the 5 runs.
- **Scoring snapshot (current pilot run):** Agency names match essentially universally; public-records response-time answers are mostly correct with occasional confusion between the primary deadline and the extension clause; mailing addresses, WIC public-records emails, and LIHEAP phone numbers remain the hardest fields, reflecting both model grounding limits and strict exact-match scoring for those fields.

### What remains

- Experiments with additional frontier thinking models (latest OpenAI GPT and Google Gemini) as specified in the proposal's cross-LLM validation protocol.
- Scaling from 5 pilot states to all 50.
- Stages 2–4 of the pipeline.

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
└── docs/
    ├── scoring_strategies.md
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

**Note:** Two of the default models are **paid** on OpenRouter: [`anthropic/claude-opus-4.7`](https://openrouter.ai/anthropic/claude-opus-4.7) ($5 / $25 per 1M input/output tokens) and [`google/gemma-4-26b-a4b-it`](https://openrouter.ai/google/gemma-4-26b-a4b-it) ($0.13 / $0.40 per 1M). At the default `--runs 5`, a full sweep costs roughly **$0.60–$1.00** for Opus and well under **$0.05** for Gemma; `openai/gpt-oss-120b:free` is free. Ensure your OpenRouter account has credit before running, or override `--models` to exclude paid entries.

## Usage

All pipeline commands below are intended to be executed from the repository root (so that the default `data/...` and `exp_results/...` paths resolve correctly).

### Run experiments

```bash
python exp_results/run_experiment.py
```

Key options:

| Flag | Default | Description |
|------|---------|-------------|
| `--models` | `gemma-4-26b-a4b-it, gpt-oss-120b:free, claude-opus-4.7` | Comma-separated OpenRouter model IDs |
| `--benchmark` | `data/benchmark.csv` | Path to benchmark CSV |
| `--output` | `exp_results/LLM_experiments.csv` | Output path for raw results |
| `--runs` | `5` | Number of runs per (question, state, model) |
| `--delay` | `3.0` | Seconds between API calls |

The runner is **resume-safe**: re-running the same command skips already-completed entries and retries any previous errors.

### Summarize results

```bash
python exp_results/summarize_experiments.py
```

| Flag | Default | Description |
|------|---------|-------------|
| `--input` | `exp_results/LLM_experiments.csv` | Path to raw experiment CSV |
| `--output` | `exp_results/LLM_experiments_summary.csv` | Output path for summary |

Produces one row per (question, program, state, model) with majority answer, agreement rate, unique sources, and average confidence score.

### Score against benchmark

```bash
python exp_results/score_experiments.py
```

| Flag | Default | Description |
|------|---------|-------------|
| `--summary` | `exp_results/LLM_experiments_summary.csv` | Path to summary CSV |
| `--benchmark` | `data/benchmark.csv` | Path to benchmark CSV |
| `--output` | `exp_results/LLM_experiments_scored.csv` | Output path for scored CSV |

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
- **RA:** Zhaocheng (Harry) Yang — Graduate Student (Master's), Brown University Data Science Institute
