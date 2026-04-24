"""Tier 3 - Error taxonomy and consolidation gap.

Outputs (under reports/):
  plots/tier3/t3_01_models_wrong_histogram.png
  plots/tier3/t3_02_matcher_false_negatives.png
  plots/tier3/t3_03_pass_at_k_vs_maj.png
  tables/tier3/*.csv + *.md
  summaries/tier3.md
"""
from __future__ import annotations

import re

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from .common import (
    MODEL_ORDER,
    QTYPE_ORDER,
    apply_style,
    grade_runs,
    load_scored,
    save_fig,
    save_summary,
    save_table,
    short_model,
)


# ---------------------------------------------------------------------------
# Lenient "does the incorrect answer at least contain a ground-truth fragment?"
# ---------------------------------------------------------------------------

def _contains_gt_fragment(qtype: str, gt: str, answer: str) -> tuple[bool, str]:
    """Return (is_contained, fragment_kind)."""
    if not isinstance(answer, str) or not isinstance(gt, str):
        return False, ""
    ans = answer.lower()

    if qtype == "phone":
        gt_digits = re.sub(r"\D", "", gt)
        ans_digits = re.sub(r"\D", "", answer)
        for n in (10, 7, 6, 5, 4):
            if len(gt_digits) >= n and gt_digits[-n:] and gt_digits[-n:] in ans_digits:
                return True, f"last-{n}-digits"
        return False, ""

    if qtype == "email":
        m = re.search(r"([\w.+-]+)@([\w.-]+)", gt)
        if m:
            local, dom = m.group(1).lower(), m.group(2).lower()
            if local in ans:
                return True, "email-local-part"
            if dom in ans:
                return True, "email-domain"
        return False, ""

    if qtype == "address":
        zm = re.search(r"\b(\d{5})\b", gt)
        if zm and zm.group(1) in answer:
            return True, "zip"
        pm = re.search(r"P\.?O\.?\s*Box\s+(\d+)", gt, re.IGNORECASE)
        if pm and pm.group(1) in answer:
            return True, "pobox-digits"
        sm = re.search(r"\b(\d{1,6})\s+\w+\s+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Place|Pl)",
                       gt, re.IGNORECASE)
        if sm and sm.group(1) in answer:
            return True, "street-number"
        return False, ""

    if qtype == "agency":
        ab = re.search(r"\(([A-Z]{2,})\)", gt)
        if ab and ab.group(1).lower() in ans:
            return True, "agency-abbrev"
        # Try a full-name token fallback (first capitalized 2-word span from gt).
        words = re.findall(r"\b[A-Z][a-z]+\b", gt)
        if len(words) >= 2 and " ".join(words[:2]).lower() in ans:
            return True, "agency-name-first2"
        return False, ""

    if qtype == "response_time":
        m = re.search(r"(\d+)\s+(business|calendar|working)\s+days?", gt, re.IGNORECASE)
        if m and m.group(1) in answer:
            return True, "deadline-number"
        return False, ""

    return False, ""


# ---------------------------------------------------------------------------
# 3.1 Hard cells (wrong across all models)
# ---------------------------------------------------------------------------

def _hard_cells(scored: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    pivot = scored.pivot_table(
        index=["question_template", "program", "state", "question_type", "ground_truth"],
        columns="model",
        values="status",
        aggfunc="first",
    ).reset_index()
    pivot["n_wrong"] = (pivot[MODEL_ORDER] == "incorrect").sum(axis=1)

    answer_pivot = scored.pivot_table(
        index=["question_template", "program", "state"],
        columns="model",
        values="majority_answer",
        aggfunc="first",
    ).reset_index()
    answer_pivot.columns = list(answer_pivot.columns[:3]) + [
        f"answer::{c}" for c in answer_pivot.columns[3:]
    ]

    merged = pivot.merge(answer_pivot, on=["question_template", "program", "state"], how="left")
    hard = merged[merged["n_wrong"] == len(MODEL_ORDER)].reset_index(drop=True)

    hist = (
        pivot["n_wrong"]
        .value_counts()
        .reindex(range(len(MODEL_ORDER) + 1), fill_value=0)
        .rename_axis("n_models_wrong")
        .reset_index(name="num_cells")
    )
    return hard, hist


def _fig_models_wrong_histogram(hist: pd.DataFrame) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(7, 4.5))
    xs = hist["n_models_wrong"].values
    colors = ["#2ca02c", "#a6d96a", "#fdae61", "#d7191c"]
    bars = ax.bar(xs, hist["num_cells"], color=[colors[i] for i in xs], edgecolor="black", linewidth=0.4)
    for b, v in zip(bars, hist["num_cells"]):
        if v > 0:
            ax.text(b.get_x() + b.get_width() / 2, v + 0.3, str(int(v)),
                    ha="center", va="bottom", fontsize=11)
    ax.set_xticks(xs)
    ax.set_xlabel("Number of models that got the cell wrong (out of 3)")
    ax.set_ylabel("Number of cells")
    ax.set_title("Cross-model error overlap (25 total cells)")
    ax.set_ylim(0, hist["num_cells"].max() * 1.2 + 2)
    return fig


# ---------------------------------------------------------------------------
# 3.2 Matcher false-negative candidates
# ---------------------------------------------------------------------------

def _matcher_false_negatives(scored: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    incorrect = scored[scored["status"] == "incorrect"].copy()
    flags, kinds = [], []
    for _, r in incorrect.iterrows():
        is_, kind = _contains_gt_fragment(r["question_type"], r.get("ground_truth"),
                                          r.get("majority_answer"))
        flags.append(is_)
        kinds.append(kind)
    incorrect["contains_gt_fragment"] = flags
    incorrect["fragment_kind"] = kinds

    stacked = (
        incorrect.groupby(["question_type", "contains_gt_fragment"]).size()
        .unstack(fill_value=0)
    )
    for col in [True, False]:
        if col not in stacked.columns:
            stacked[col] = 0
    stacked = stacked.reindex(QTYPE_ORDER, fill_value=0)
    stacked.columns = ["truly_wrong" if not c else "contains_gt_fragment" for c in stacked.columns]

    return incorrect, stacked


def _fig_matcher_false_negatives(stacked: pd.DataFrame) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(9, 5))
    xs = np.arange(len(stacked))
    bottom = np.zeros(len(stacked))
    for col, color in zip(["truly_wrong", "contains_gt_fragment"], ["#d62728", "#f2c14e"]):
        vals = stacked[col].values
        ax.bar(xs, vals, bottom=bottom, label=col.replace("_", " "),
               color=color, edgecolor="black", linewidth=0.4)
        for i, v in enumerate(vals):
            if v > 0:
                ax.text(i, bottom[i] + v / 2, int(v), ha="center", va="center",
                        fontsize=10, color="white")
        bottom = bottom + vals

    ax.set_xticks(xs)
    ax.set_xticklabels(stacked.index)
    ax.set_xlabel("Question type")
    ax.set_ylabel("Number of 'incorrect' cells")
    ax.set_title("Scorer-strictness audit: do 'incorrect' cells still contain a ground-truth fragment?")
    ax.legend()
    return fig


# ---------------------------------------------------------------------------
# 3.3 pass@k vs maj@k
# ---------------------------------------------------------------------------

def _pass_at_k_table(graded: pd.DataFrame, scored: pd.DataFrame) -> pd.DataFrame:
    """Compute per (model, question_type):
       - pass@1 = mean per-run correctness
       - maj@5  = rate of correct majority-answer cells (from scored)
       - pass@5 = rate of cells where ANY run was correct
    """
    graded = graded.copy()
    graded["is_correct"] = graded["run_correct"].fillna(False).astype(bool)

    cell_pass_any = (
        graded.groupby(["question_template", "program", "state", "model", "question_type"])
        ["is_correct"].max().reset_index().rename(columns={"is_correct": "pass_any"})
    )
    cell_correct_frac = (
        graded.groupby(["question_template", "program", "state", "model", "question_type"])
        ["is_correct"].mean().reset_index().rename(columns={"is_correct": "pass_at_1"})
    )

    scored_tmp = scored[["question_template", "program", "state", "model", "status"]].copy()
    scored_tmp["maj_correct"] = (scored_tmp["status"] == "correct").astype(int)

    base = cell_correct_frac.merge(cell_pass_any,
                                   on=["question_template", "program", "state", "model", "question_type"])
    base = base.merge(scored_tmp, on=["question_template", "program", "state", "model"], how="left")

    invariant_violations = base[~(base["pass_any"] >= base["maj_correct"])]
    assert len(invariant_violations) == 0, (
        f"Invariant pass@5 >= maj@5 violated for {len(invariant_violations)} cells"
    )
    invariant_violations2 = base[~(base["pass_any"] >= base["pass_at_1"] - 1e-9)]
    assert len(invariant_violations2) == 0, (
        "Invariant pass@5 >= pass@1 violated"
    )

    rows = []
    for m in MODEL_ORDER:
        m_df = base[base["model"] == m]
        for q in QTYPE_ORDER:
            q_df = m_df[m_df["question_type"] == q]
            n = len(q_df)
            rows.append({
                "model": m,
                "question_type": q,
                "n_cells": n,
                "pass@1": q_df["pass_at_1"].mean() if n else np.nan,
                "maj@5": q_df["maj_correct"].mean() if n else np.nan,
                "pass@5": q_df["pass_any"].mean() if n else np.nan,
            })
        rows.append({
            "model": m,
            "question_type": "ALL",
            "n_cells": len(m_df),
            "pass@1": m_df["pass_at_1"].mean(),
            "maj@5": m_df["maj_correct"].mean(),
            "pass@5": m_df["pass_any"].mean(),
        })
    return pd.DataFrame(rows)


def _fig_pass_at_k(tbl: pd.DataFrame) -> plt.Figure:
    # One subplot per model, grouped bars across question types.
    fig, axes = plt.subplots(1, len(MODEL_ORDER), figsize=(15, 5.8), sharey=True)
    metrics = ["pass@1", "maj@5", "pass@5"]
    metric_labels = [
        "pass@1: mean per-run accuracy (avg over 5 runs)",
        "maj@5: majority-vote accuracy (modal answer of 5 runs)",
        "pass@5: oracle best-of-5 (cell counted correct if ANY of 5 runs is correct)",
    ]
    colors = ["#c6c6c6", "#4c72b0", "#2ca02c"]

    for ax, m in zip(axes, MODEL_ORDER):
        sub = tbl[(tbl["model"] == m) & (tbl["question_type"].isin(QTYPE_ORDER))].set_index("question_type")
        sub = sub.reindex(QTYPE_ORDER)
        xs = np.arange(len(QTYPE_ORDER))
        width = 0.27
        for i, (metric, label, color) in enumerate(zip(metrics, metric_labels, colors)):
            vals = sub[metric].values
            ax.bar(xs + (i - 1) * width, vals, width=width, label=label,
                   color=color, edgecolor="black", linewidth=0.3)
        ax.set_xticks(xs)
        ax.set_xticklabels(QTYPE_ORDER, rotation=25, ha="right")
        ax.set_ylim(0, 1.1)
        ax.set_yticks(np.linspace(0, 1, 6))
        ax.set_yticklabels([f"{int(y*100)}%" for y in np.linspace(0, 1, 6)])
        ax.set_title(short_model(m))
        ax.grid(axis="y", linestyle=":", alpha=0.5)

    axes[0].set_ylabel("Accuracy")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(
        handles, labels,
        loc="lower center", ncol=3, fontsize=9, frameon=False,
        bbox_to_anchor=(0.5, -0.02),
    )
    fig.suptitle("pass@1 vs maj@5 vs pass@5 (oracle best-of-5) per model and question type",
                 fontsize=13)
    fig.subplots_adjust(bottom=0.22)
    return fig


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def run() -> list[str]:
    apply_style()
    scored = load_scored()
    graded = grade_runs()
    bullets: list[str] = []

    # --- 3.1 hard cells
    hard, hist = _hard_cells(scored)
    save_table(hard, "t3_01_hard_cells_all_models_wrong", tier=3)
    save_table(hist, "t3_01_models_wrong_histogram", tier=3)
    fig = _fig_models_wrong_histogram(hist)
    save_fig(fig, "t3_01_models_wrong_histogram", tier=3)
    bullets.append(
        f"{int(hist.loc[hist['n_models_wrong'] == 3, 'num_cells'].iloc[0])} of 25 cells "
        f"are incorrect across ALL 3 models; "
        f"{int(hist.loc[hist['n_models_wrong'] == 0, 'num_cells'].iloc[0])} are correct "
        f"across all 3."
    )

    # --- 3.2 matcher false negatives
    incorrect, stacked = _matcher_false_negatives(scored)
    save_table(incorrect, "t3_02_matcher_false_negative_details", tier=3)
    save_table(stacked.reset_index().rename(columns={"index": "question_type"}),
               "t3_02_matcher_false_negative_counts", tier=3)
    fig = _fig_matcher_false_negatives(stacked)
    save_fig(fig, "t3_02_matcher_false_negatives", tier=3)
    contains = int(stacked["contains_gt_fragment"].sum())
    total_incorrect = int(stacked.values.sum())
    bullets.append(
        f"Among {total_incorrect} incorrect cells, {contains} contain a ground-truth "
        f"fragment (e.g. ZIP, PO box number, email domain) - possible matcher strictness."
    )

    # --- 3.3 pass@k vs maj@k
    tbl = _pass_at_k_table(graded, scored)
    save_table(tbl, "t3_03_pass_at_k_vs_maj", tier=3)
    fig = _fig_pass_at_k(tbl)
    save_fig(fig, "t3_03_pass_at_k_vs_maj", tier=3)
    for m in MODEL_ORDER:
        row = tbl[(tbl["model"] == m) & (tbl["question_type"] == "ALL")].iloc[0]
        bullets.append(
            f"{short_model(m)}: pass@1={row['pass@1']:.0%}, maj@5={row['maj@5']:.0%}, "
            f"pass@5={row['pass@5']:.0%} -> oracle gap={row['pass@5'] - row['maj@5']:+.0%}"
        )

    save_summary(tier=3, lines=bullets)
    return bullets


if __name__ == "__main__":
    lines = run()
    print("Tier 3 summary:")
    for line in lines:
        print(" -", line)
