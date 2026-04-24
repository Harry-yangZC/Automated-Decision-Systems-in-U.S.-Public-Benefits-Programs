"""Shared helpers used by the tier1-tier4 analysis scripts.

All paths are resolved relative to the repository root so scripts can be
invoked either as `python exp_analysis/tierN_*.py` from the repo root or as a
module.
"""
from __future__ import annotations

import sys
from pathlib import Path
from urllib.parse import urlparse

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from exp_results.score_experiments import MATCHERS, classify_question, load_benchmark  # noqa: E402

RESULTS_DIR = REPO_ROOT / "exp_results"
DATA_DIR = REPO_ROOT / "data"
REPORTS_DIR = REPO_ROOT / "reports"
PLOTS_DIR = REPORTS_DIR / "plots"
TABLES_DIR = REPORTS_DIR / "tables"
REPORTS_DATA_DIR = REPORTS_DIR / "data"

MODEL_ORDER = [
    "anthropic/claude-opus-4.7",
    "google/gemma-4-26b-a4b-it",
    "openai/gpt-oss-120b:free",
]

MODEL_SHORT = {
    "anthropic/claude-opus-4.7": "Claude Opus 4.7",
    "google/gemma-4-26b-a4b-it": "Gemma 4 26B",
    "openai/gpt-oss-120b:free": "GPT-OSS 120B",
}

QTYPE_ORDER = ["agency", "response_time", "address", "email", "phone"]
STATE_ORDER = ["MA", "RI", "CA", "NY", "TX"]
PROGRAM_ORDER = ["SNAP", "Medicaid", "WIC", "LIHEAP"]

STATE_DOMAIN_TOKENS = {
    "MA": ["mass.gov", "ma.gov", "massachusetts.gov", "massresources"],
    "RI": ["ri.gov", "rhodeisland.gov"],
    "CA": ["ca.gov", "california.gov"],
    "NY": ["ny.gov", "newyork.gov", "nyc.gov"],
    "TX": ["tx.gov", "texas.gov", "tex.gov"],
}


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------

def load_raw() -> pd.DataFrame:
    df = pd.read_csv(RESULTS_DIR / "LLM_experiments.csv")
    for col in ["question_template", "program", "state", "model"]:
        df[col] = df[col].astype(str).str.strip()
    return df


def load_summary() -> pd.DataFrame:
    df = pd.read_csv(RESULTS_DIR / "LLM_experiments_summary.csv")
    for col in ["question_template", "program", "state", "model"]:
        df[col] = df[col].astype(str).str.strip()
    return df


def load_scored() -> pd.DataFrame:
    df = pd.read_csv(RESULTS_DIR / "LLM_experiments_scored.csv")
    for col in ["question_template", "program", "state", "model"]:
        df[col] = df[col].astype(str).str.strip()
    return df


def load_benchmark_long() -> pd.DataFrame:
    return load_benchmark(str(DATA_DIR / "benchmark.csv"))


# ---------------------------------------------------------------------------
# Stats helpers
# ---------------------------------------------------------------------------

def wilson_ci(k: int, n: int, alpha: float = 0.05) -> tuple[float, float]:
    """Wilson score interval via the Clopper-Pearson-equivalent beta formulation
    is a touch wider but simpler to compute; stick with the canonical Wilson
    formula here for interpretability.
    """
    if n == 0:
        return 0.0, 0.0
    from math import sqrt
    z = 1.959963984540054  # 97.5% standard normal quantile (alpha=0.05)
    phat = k / n
    denom = 1 + z * z / n
    center = (phat + z * z / (2 * n)) / denom
    half = (z * sqrt((phat * (1 - phat) + z * z / (4 * n)) / n)) / denom
    return max(0.0, center - half), min(1.0, center + half)


def accuracy_with_ci(k: int, n: int) -> dict:
    lo, hi = wilson_ci(k, n)
    return {
        "correct": int(k),
        "n": int(n),
        "accuracy": k / n if n else 0.0,
        "ci_low": lo,
        "ci_high": hi,
    }


# ---------------------------------------------------------------------------
# Per-run grading (Tier 2 + Tier 3 use this)
# ---------------------------------------------------------------------------

def grade_runs(force: bool = False) -> pd.DataFrame:
    """Apply the scorer matchers to every individual run row.

    Returns a dataframe keyed on (question_template, program, state, model,
    run_number) with columns `question_type`, `ground_truth`, `run_correct`
    (bool or None when the run had no answer or no ground truth).
    Cached to reports/data/raw_graded.csv.
    """
    cache = REPORTS_DATA_DIR / "raw_graded.csv"
    if cache.exists() and not force:
        df = pd.read_csv(cache)
        return df

    raw = load_raw()
    bench = load_benchmark_long()

    merged = raw.merge(
        bench,
        on=["question_template", "program", "state"],
        how="left",
    )

    qtypes = []
    run_correct = []
    for _, row in merged.iterrows():
        qtype = classify_question(row["question_template"])
        qtypes.append(qtype)

        ans = row.get("answer_extracted")
        gt = row.get("ground_truth")

        if pd.isna(ans) or ans is None or str(ans).strip() == "":
            run_correct.append(None)
            continue
        if pd.isna(gt) or gt is None or str(gt).strip() == "":
            run_correct.append(None)
            continue

        matcher = MATCHERS.get(qtype)
        if matcher is None:
            run_correct.append(None)
            continue

        try:
            run_correct.append(bool(matcher(str(gt), str(ans))))
        except Exception:
            run_correct.append(None)

    merged["question_type"] = qtypes
    merged["run_correct"] = run_correct

    keep = [
        "question_template", "program", "state", "model", "run_number",
        "question_type", "ground_truth", "answer_extracted",
        "source", "confidence", "run_correct",
    ]
    out = merged[[c for c in keep if c in merged.columns]].copy()

    REPORTS_DATA_DIR.mkdir(parents=True, exist_ok=True)
    out.to_csv(cache, index=False)
    return out


# ---------------------------------------------------------------------------
# Source / URL helpers (Tier 4)
# ---------------------------------------------------------------------------

def split_sources(cell: str | float) -> list[str]:
    if pd.isna(cell) or not isinstance(cell, str):
        return []
    parts: list[str] = []
    for sep in ["|", ";", ","]:
        if sep in cell:
            parts = [p.strip() for p in cell.split(sep)]
            break
    if not parts:
        parts = [cell.strip()]
    return [p for p in parts if p]


def extract_domain(url: str) -> str | None:
    if not isinstance(url, str) or not url.strip():
        return None
    u = url.strip()
    if "://" not in u:
        u = "http://" + u
    try:
        host = urlparse(u).hostname
    except ValueError:
        return None
    if not host:
        return None
    host = host.lower()
    if host.startswith("www."):
        host = host[4:]
    return host


def is_gov(url: str) -> bool:
    dom = extract_domain(url) or ""
    return dom.endswith(".gov") or ".gov/" in (url or "").lower()


def state_domain_match(state: str, url: str) -> bool:
    tokens = STATE_DOMAIN_TOKENS.get(state, [])
    url_lower = (url or "").lower()
    return any(tok in url_lower for tok in tokens)


# ---------------------------------------------------------------------------
# Saving
# ---------------------------------------------------------------------------

def _tier_paths(tier: int) -> tuple[Path, Path]:
    plots = PLOTS_DIR / f"tier{tier}"
    tables = TABLES_DIR / f"tier{tier}"
    plots.mkdir(parents=True, exist_ok=True)
    tables.mkdir(parents=True, exist_ok=True)
    return plots, tables


def save_table(df: pd.DataFrame, name: str, tier: int) -> Path:
    _, tables = _tier_paths(tier)
    csv_path = tables / f"{name}.csv"
    md_path = tables / f"{name}.md"
    df.to_csv(csv_path, index=False)
    # Render floats with 3 decimals in the markdown version for readability.
    with md_path.open("w") as f:
        f.write(df.to_markdown(index=False, floatfmt=".3f"))
        f.write("\n")
    return csv_path


def save_fig(fig: plt.Figure, name: str, tier: int) -> Path:
    plots, _ = _tier_paths(tier)
    path = plots / f"{name}.png"
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path


def save_summary(tier: int, lines: list[str]) -> Path:
    _, tables = _tier_paths(tier)
    path = tables.parent.parent / f"summaries" / f"tier{tier}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        f.write(f"# Tier {tier} summary\n\n")
        for line in lines:
            f.write(f"- {line}\n")
    return path


# ---------------------------------------------------------------------------
# Style defaults
# ---------------------------------------------------------------------------

def apply_style() -> None:
    sns.set_theme(style="whitegrid", context="talk", palette="deep")
    plt.rcParams["figure.figsize"] = (8, 5)
    plt.rcParams["axes.titlesize"] = 14
    plt.rcParams["axes.labelsize"] = 12
    plt.rcParams["xtick.labelsize"] = 10
    plt.rcParams["ytick.labelsize"] = 10
    plt.rcParams["legend.fontsize"] = 10
    plt.rcParams["savefig.bbox"] = "tight"


def short_model(m: str) -> str:
    return MODEL_SHORT.get(m, m)
