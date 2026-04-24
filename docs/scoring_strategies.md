# Scoring Strategies

This document describes how we automatically evaluate LLM-generated answers against a set of known correct answers (the **benchmark**). Each question type uses a dedicated matching strategy tailored to the kind of information being verified.

## Pipeline Overview

Scoring is the final stage of a three-step pipeline:

1. **Run experiments** (`run_experiment.py`) -- Send each question to one or more LLMs multiple times and collect raw responses.
2. **Summarize** (`summarize_experiments.py`) -- Group the raw responses by question, program, state, and model. Select the **majority answer** (the most frequent response) for each group.
3. **Score** (`score_experiments.py`) -- Compare each majority answer against the benchmark ground truth using a question-type-specific matcher. Record the result as `correct` or `incorrect`.

## Question-Type Classification

Before scoring, each question is classified into one of five types based on keywords in its template:

| Keyword in question template | Assigned type |
|---|---|
| "which agency administers" | **agency** |
| "how much time" | **response_time** |
| "administration address" | **address** |
| "email address" | **email** |
| "phone number" | **phone** |

The assigned type determines which matching strategy is applied.

## Matching Strategies

### 1. Agency

**Goal:** Verify that the LLM identified the correct government agency.

**How it works:**

- If the benchmark answer contains an abbreviation in parentheses (e.g., "DTA"), the scorer first checks whether that abbreviation appears anywhere in the LLM's answer.
- If the abbreviation is not found, the scorer falls back to checking whether the **full agency name** (without the leading "The") appears in the answer.
- If the benchmark answer has no abbreviation, the scorer checks for the full name directly.
- All comparisons are case-insensitive.

**Example:**

- Ground truth: *The Massachusetts Department of Transitional Assistance (DTA)*
- Accepted answers:
  - "...administered by the Department of Transitional Assistance (DTA)." -- matches on abbreviation "DTA"
  - "...the Massachusetts Department of Transitional Assistance manages..." -- matches on full name

### 2. Response Time

**Goal:** Verify that the LLM stated the correct primary deadline for public records requests.

**How it works:**

- The scorer extracts the **primary deadline** from the benchmark -- the portion before any "with ..." extension clause. For instance, from "10 business days with 20 business days extension", only "10 business days" is used.
- It then searches the LLM's answer for that number paired with the correct day type ("business" or "calendar"), allowing up to 30 characters between the two.
- **Number flexibility:** Both the digit form ("10") and the spelled-out form ("ten") are accepted.
- **Day-type aliases:** "working days" is treated as equivalent to "business days."
- **Extension filtering:** If the matched phrase contains qualifier words such as "additional", "extend", "extra", "more", or "further", the match is rejected. This prevents the scorer from incorrectly matching an extension period (e.g., "an additional 10 business days") as the primary deadline. The filter operates on each matched snippet individually, and the scorer stops at the first clean match. This means an answer can mention extensions elsewhere and still be scored correct, as long as at least one occurrence of the deadline appears without a qualifier attached to it.

**Examples:**

- Ground truth: *10 business days with 20-30 business days extension*
- Accepted: "...agencies must respond within 10 business days..." -- matches "10" + "business days"
- Accepted: "...agencies have 10 business days to respond, with the option to extend by 20 more business days..." -- the first occurrence ("10 business days") is a clean match, so the scorer accepts it immediately without examining the extension clause
- Rejected: "...an additional ten working days..." -- disqualified by the word "additional" (only extension mentioned, no primary deadline)

### 3. Address

**Goal:** Verify that the LLM provided the correct mailing address.

**How it works:**

The scorer uses a three-tier check. Any single match is sufficient to mark the answer as correct:

1. **Zip code** -- Looks for the 5-digit zip code from the benchmark (e.g., "02780") in the answer. Extended zip+4 formats in the benchmark are matched by their first five digits.
2. **P.O. Box number** -- If the benchmark contains a P.O. Box, the scorer checks whether the same box number appears in the answer with a "P.O. Box" prefix (flexible punctuation: "PO Box", "P.O. Box", etc.).
3. **Street number** -- If the benchmark contains a street address, the scorer extracts the street number (e.g., "744" from "744 P Street") and checks whether it appears in the answer.

**Example:**

- Ground truth: *DTA Document Processing Center, P.O. Box 4406, Taunton, MA 02780-0420*
- Accepted: "...P.O. Box 4406, Taunton..." -- matches on P.O. Box number
- Also accepted: "...Taunton, MA 02780..." -- matches on zip code

### 4. Email

**Goal:** Verify that the LLM provided the correct email address.

**How it works:**

- The scorer performs a straightforward case-insensitive substring check: if the benchmark email address appears anywhere in the LLM's answer, the answer is correct.

**Example:**

- Ground truth: *DPH.RAO@state.ma.us*
- Accepted: "...contact DPH.RAO@state.ma.us for records requests..." -- exact email present in text

### 5. Phone

**Goal:** Verify that the LLM provided the correct phone number.

**How it works:**

- The scorer strips all non-digit characters (parentheses, dashes, spaces, dots) from both the benchmark number and any phone-number-like sequences found in the LLM's answer.
- It normalizes each to its last **10 digits** (or last 7 if fewer than 10 are available), removing country codes and leading digits that vary by formatting convention.
- If any phone-like sequence in the answer matches the normalized benchmark number, the answer is correct.

**Example:**

- Ground truth: *(800) 632-8175*
- Accepted: "...call 1-800-632-8175 for assistance..." -- both normalize to `8006328175`
- Also accepted: "...800.632.8175..." -- same digits after stripping punctuation

## Scoring Outcomes

Each scored row receives one of four statuses:

| Status | Meaning |
|---|---|
| `correct` | The matcher confirmed the answer contains the expected information. |
| `incorrect` | The matcher did not find the expected information in the answer. |
| `no_answer` | The LLM did not produce a majority answer for this question. |
| `no_ground_truth` | No benchmark value exists for this question/program/state combination. |
