import argparse
import re

import pandas as pd

JOIN_KEYS = ["question_template", "program", "state"]

NUM_TO_WORD = {
    1: "one", 2: "two", 3: "three", 4: "four", 5: "five",
    6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten",
    11: "eleven", 12: "twelve", 13: "thirteen", 14: "fourteen",
    15: "fifteen", 20: "twenty", 30: "thirty",
}

DAY_TYPE_ALIASES = {
    "business": ["business", "working"],
    "calendar": ["calendar"],
}


# ---------------------------------------------------------------------------
# Question-type classification
# ---------------------------------------------------------------------------

def classify_question(template: str) -> str:
    t = template.lower()
    if "which agency administers" in t:
        return "agency"
    if "how much time" in t:
        return "response_time"
    if "administration address" in t:
        return "address"
    if "email address" in t:
        return "email"
    if "phone number" in t:
        return "phone"
    return "unknown"


# ---------------------------------------------------------------------------
# Per-type matchers
# ---------------------------------------------------------------------------

def match_agency(ground_truth: str, answer: str) -> bool:
    """Check if the agency abbreviation or full name from the ground truth appears in the answer."""
    answer_lower = answer.lower()
    abbrev_match = re.search(r"\(([A-Z]{2,})\)", ground_truth)
    if abbrev_match:
        abbrev = abbrev_match.group(1)
        if abbrev.lower() in answer_lower:
            return True
        full_name = re.sub(r"\s*\([A-Z]{2,}\)", "", ground_truth).strip()
        full_name = re.sub(r"^The\s+", "", full_name).strip()
        return full_name.lower() in answer_lower
    clean_gt = re.sub(r"^The\s+", "", ground_truth).strip()
    return clean_gt.lower() in answer_lower


def match_response_time(ground_truth: str, answer: str) -> bool:
    """Check if the primary deadline (number + day type) from ground truth appears in the answer."""
    primary = ground_truth.split(" with ")[0].strip()
    m = re.search(r"(\d+)\s+(business|calendar)\s+days?", primary, re.IGNORECASE)
    if not m:
        return False
    num = int(m.group(1))
    day_type = m.group(2).lower()

    num_variants = [str(num)]
    word = NUM_TO_WORD.get(num)
    if word:
        num_variants.append(word)

    type_variants = DAY_TYPE_ALIASES.get(day_type, [day_type])
    answer_lower = answer.lower()

    disqualifiers = re.compile(r"\b(?:additional|extend|extra|more|further)\b")
    for nv in num_variants:
        for tv in type_variants:
            pattern = rf"\b{re.escape(nv)}\b.{{0,30}}\b{re.escape(tv)}\s+days?\b"
            m_hit = re.search(pattern, answer_lower)
            if m_hit and not disqualifiers.search(m_hit.group(0)):
                return True
    return False


def match_address(ground_truth: str, answer: str) -> bool:
    """Check for zip code, PO Box number, or street number from ground truth in the answer."""
    zip_match = re.search(r"\b(\d{5})(?:-\d{4})?\b", ground_truth)
    if zip_match and zip_match.group(1) in answer:
        return True

    po_match = re.search(r"P\.?O\.?\s*Box\s+(\d+)", ground_truth, re.IGNORECASE)
    if po_match:
        po_num = po_match.group(1)
        if re.search(rf"P\.?O\.?\s*Box\s+{re.escape(po_num)}\b", answer, re.IGNORECASE):
            return True

    street_match = re.search(
        r"\b(\d+)\s+\w+\s+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Place|Pl)",
        ground_truth, re.IGNORECASE,
    )
    if street_match and re.search(rf"\b{re.escape(street_match.group(1))}\b", answer):
        return True

    return False


def match_email(ground_truth: str, answer: str) -> bool:
    """Case-insensitive exact email substring match."""
    return ground_truth.strip().lower() in answer.lower()


def _extract_phone_patterns(text: str) -> list[str]:
    """Extract phone-number-like digit sequences from text."""
    patterns = re.findall(r"[\d][\d\s\-\.\(\)]{6,}[\d]", text)
    return [re.sub(r"\D", "", p) for p in patterns]


def _normalize_phone(digits: str) -> str:
    if len(digits) >= 10:
        return digits[-10:]
    if len(digits) >= 7:
        return digits[-7:]
    return digits


def match_phone(ground_truth: str, answer: str) -> bool:
    """Compare normalized phone digits extracted from the answer to ground truth."""
    gt_digits = _normalize_phone(re.sub(r"\D", "", ground_truth))
    if not gt_digits:
        return False
    for phone in _extract_phone_patterns(answer):
        if _normalize_phone(phone) == gt_digits:
            return True
    return False


MATCHERS = {
    "agency": match_agency,
    "response_time": match_response_time,
    "address": match_address,
    "email": match_email,
    "phone": match_phone,
}


# ---------------------------------------------------------------------------
# Scoring pipeline
# ---------------------------------------------------------------------------

def load_benchmark(path: str) -> pd.DataFrame:
    """Load the wide-format benchmark and melt into long format."""
    df = pd.read_csv(path)
    df = df.rename(columns={"Questions": "question_template", "Programs": "program"})
    state_cols = [c for c in df.columns if c not in ("question_template", "program")]
    long = df.melt(
        id_vars=["question_template", "program"],
        value_vars=state_cols,
        var_name="state",
        value_name="ground_truth",
    )
    for key in JOIN_KEYS:
        long[key] = long[key].astype(str).str.strip()
    return long


def load_summary(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    for key in JOIN_KEYS:
        df[key] = df[key].astype(str).str.strip()
    return df


def score(summary: pd.DataFrame, benchmark: pd.DataFrame) -> pd.DataFrame:
    merged = summary.merge(benchmark, on=JOIN_KEYS, how="left")

    statuses = []
    question_types = []

    for _, row in merged.iterrows():
        qtype = classify_question(row["question_template"])
        question_types.append(qtype)

        answer = row.get("majority_answer")
        gt = row.get("ground_truth")

        if pd.isna(answer) or answer is None or str(answer).strip() == "":
            statuses.append("no_answer")
            continue
        if pd.isna(gt) or gt is None or str(gt).strip() == "":
            statuses.append("no_ground_truth")
            continue

        matcher = MATCHERS.get(qtype)
        if matcher is None:
            statuses.append("unknown_type")
            continue

        statuses.append("correct" if matcher(str(gt), str(answer)) else "incorrect")

    merged["question_type"] = question_types
    merged["status"] = statuses

    column_order = [
        "question_template", "program", "state", "model",
        "question_type", "ground_truth", "majority_answer",
        "status", "agreement_rate", "avg_confidence",
    ]
    return merged[[c for c in column_order if c in merged.columns]]


def print_stats(scored: pd.DataFrame) -> None:
    total = len(scored)
    print(f"\n{'=' * 60}")
    print(f"SCORING RESULTS  ({total} rows)")
    print(f"{'=' * 60}")

    print("\n--- Accuracy by model ---")
    for model, grp in scored.groupby("model"):
        n = len(grp)
        correct = (grp["status"] == "correct").sum()
        incorrect = (grp["status"] == "incorrect").sum()
        no_ans = (grp["status"] == "no_answer").sum()
        answered = n - no_ans
        acc = correct / answered if answered > 0 else 0
        cov = answered / n if n > 0 else 0
        print(f"  {model}")
        print(f"    correct={correct}  incorrect={incorrect}  no_answer={no_ans}  "
              f"accuracy={acc:.1%}  coverage={cov:.1%}")

    print("\n--- Accuracy by question type ---")
    for qtype, grp in scored.groupby("question_type"):
        answered = grp[grp["status"] != "no_answer"]
        correct = (answered["status"] == "correct").sum()
        n = len(answered)
        acc = correct / n if n > 0 else 0
        print(f"  {qtype:15s}  correct={correct}/{n}  accuracy={acc:.1%}")

    print()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Score LLM experiment summaries against the benchmark ground truth.",
    )
    parser.add_argument(
        "--summary",
        default="exp_results/LLM_experiments_summary.csv",
        help="Path to the summary CSV (default: exp_results/LLM_experiments_summary.csv)",
    )
    parser.add_argument(
        "--benchmark",
        default="data/benchmark.csv",
        help="Path to the benchmark CSV (default: data/benchmark.csv)",
    )
    parser.add_argument(
        "--output",
        default="exp_results/LLM_experiments_scored.csv",
        help="Path for the scored CSV (default: exp_results/LLM_experiments_scored.csv)",
    )
    args = parser.parse_args()

    summary = load_summary(args.summary)
    print(f"Loaded {len(summary)} summary rows from {args.summary}")

    benchmark = load_benchmark(args.benchmark)
    print(f"Loaded {len(benchmark)} benchmark rows from {args.benchmark}")

    scored = score(summary, benchmark)
    scored.to_csv(args.output, index=False)
    print(f"Wrote {len(scored)} scored rows to {args.output}")

    print_stats(scored)


if __name__ == "__main__":
    main()
