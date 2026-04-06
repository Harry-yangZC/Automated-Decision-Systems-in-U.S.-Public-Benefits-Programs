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
- **Initial experiment results** (~975 raw rows, 77 summary rows) from three free-tier models: Qwen 3.6 Plus, OpenAI GPT-OSS-120B, and Meta Llama 3.3 70B Instruct.

### Preliminary observations

- Qwen 3.6 Plus returned substantive answers across all questions and states with generally high confidence.
- GPT-OSS-120B produced partial coverage (complete for some questions, missing for others).
- Meta Llama 3.3 70B failed systematically (no answers extracted).
- Cross-run agreement rates are low (0.2–0.6), largely due to verbosity variation rather than factual disagreement — models identify the same entities but phrase answers differently each time.

### What remains

- Accuracy scoring of LLM outputs against the benchmark ground-truth.
- Experiments with frontier thinking models (latest OpenAI GPT, Google Gemini, Anthropic Claude) as specified in the proposal's cross-LLM validation protocol.
- Scaling from 5 pilot states to all 50.
- Stages 2–4 of the pipeline.

## Repository Structure

```
├── README.md
├── requirements.txt
├── .env                                          # OPENROUTER_API_KEY (not committed)
├── run_experiment.py                             # LLM experiment runner (OpenRouter)
├── summarize_experiments.py                      # Aggregates raw runs into summary rows
├── Benefits Decoded Project - Benchmark.csv      # Hand-verified ground-truth answers
├── Benefits Decoded Project - LLM Experiment.csv # Question template reference (Google Sheets)
├── LLM_experiments.csv                           # Raw experiment results
└── LLM_experiments_summary.csv                   # Aggregated summary results
```

## Setup

```bash
pip install -r requirements.txt
```

Create a `.env` file in the project root with your [OpenRouter](https://openrouter.ai/) API key:

```
OPENROUTER_API_KEY=sk-or-...
```

## Usage

### Run experiments

```bash
python run_experiment.py
```

Key options:

| Flag | Default | Description |
|------|---------|-------------|
| `--models` | 3 free-tier models | Comma-separated OpenRouter model IDs |
| `--benchmark` | `Benefits Decoded Project - Benchmark.csv` | Path to benchmark CSV |
| `--output` | `LLM_experiments.csv` | Output path for raw results |
| `--runs` | `5` | Number of runs per (question, state, model) |
| `--delay` | `3.0` | Seconds between API calls |

The runner is **resume-safe**: re-running the same command skips already-completed entries and retries any previous errors.

### Summarize results

```bash
python summarize_experiments.py
```

| Flag | Default | Description |
|------|---------|-------------|
| `--input` | `LLM_experiments.csv` | Path to raw experiment CSV |
| `--output` | `LLM_experiments_summary.csv` | Output path for summary |

Produces one row per (question, program, state, model) with majority answer, agreement rate, unique sources, and average confidence score.

## Team

- **PI:** Tomo Lazovich — Assistant Professor of the Practice (AI Governance and Policy), Brown University Data Science Institute
- **RA:** Zhaocheng (Harry) Yang — Graduate Student (Master's), Brown University Data Science Institute
