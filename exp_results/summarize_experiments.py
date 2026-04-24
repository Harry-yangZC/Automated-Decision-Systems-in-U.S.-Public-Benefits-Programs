import argparse

import pandas as pd

REQUIRED_COLUMNS = [
    "question_template", "program", "state", "model",
    "run_number", "answer_extracted", "source", "confidence",
]

GROUP_KEYS = ["question_template", "program", "state", "model"]

CONFIDENCE_MAP = {"high": 3, "medium": 2, "low": 1}


def load_and_validate(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Input CSV is missing required columns: {missing}")
    return df


def summarize_group(group: pd.DataFrame) -> dict:
    answers = group["answer_extracted"].dropna()

    if answers.empty:
        majority_answer = None
        agreement_rate = 0.0
    else:
        majority_answer = answers.mode().iloc[0]
        matching = (answers == majority_answer).sum()
        agreement_rate = round(matching / len(answers), 2)

    unique_sources = group["source"].dropna().unique()
    if len(unique_sources) > 0:
        sources = " | ".join(sorted(str(s) for s in unique_sources))
    else:
        sources = None

    conf_scores = group["confidence"].map(CONFIDENCE_MAP).dropna()
    if not conf_scores.empty:
        avg_confidence = round(conf_scores.mean(), 2)
    else:
        avg_confidence = None

    return {
        "majority_answer": majority_answer,
        "agreement_rate": agreement_rate,
        "sources": sources,
        "avg_confidence": avg_confidence,
    }


def build_summary(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for keys, group in df.groupby(GROUP_KEYS, sort=False):
        row = dict(zip(GROUP_KEYS, keys))
        row.update(summarize_group(group))
        rows.append(row)

    column_order = [
        "question_template", "program", "state", "model",
        "majority_answer", "agreement_rate", "sources", "avg_confidence",
    ]
    return pd.DataFrame(rows, columns=column_order)


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Summarize LLM experiment runs into one row "
            "per (question, program, state, model)."
        ),
    )
    parser.add_argument(
        "--input",
        default="exp_results/LLM_experiments.csv",
        help="Path to the raw experiment CSV (default: exp_results/LLM_experiments.csv)",
    )
    parser.add_argument(
        "--output",
        default="exp_results/LLM_experiments_summary.csv",
        help="Path for the summary CSV (default: exp_results/LLM_experiments_summary.csv)",
    )
    args = parser.parse_args()

    df = load_and_validate(args.input)
    print(f"Loaded {len(df)} rows from {args.input}")

    summary = build_summary(df)
    summary.to_csv(args.output, index=False)
    print(f"Wrote {len(summary)} summary rows to {args.output}")


if __name__ == "__main__":
    main()
