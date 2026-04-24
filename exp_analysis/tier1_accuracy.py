"""Tier 1 - Headline accuracy tables and plots.

Inputs: exp_results/LLM_experiments_scored.csv
Outputs (under reports/):
  plots/tier1/t1_01_leaderboard_by_model.png
  plots/tier1/t1_02_accuracy_by_question_type.png
  plots/tier1/t1_03_accuracy_by_state.png
  plots/tier1/t1_04_accuracy_by_program.png
  plots/tier1/t1_05_heatmap_model_x_qtype.png
  plots/tier1/t1_06_heatmap_model_x_state.png
  plots/tier1/t1_07_heatmap_model_x_program.png
  tables/tier1/*.csv + *.md (one per figure)
  summaries/tier1.md
"""
from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from .common import (
    MODEL_ORDER,
    PROGRAM_ORDER,
    QTYPE_ORDER,
    STATE_ORDER,
    accuracy_with_ci,
    apply_style,
    load_scored,
    save_fig,
    save_summary,
    save_table,
    short_model,
)


def _acc_table(scored: pd.DataFrame, group_col: str, order: list[str]) -> pd.DataFrame:
    rows = []
    for key in order:
        grp = scored[scored[group_col] == key]
        # Treat no_answer / unknown_type / no_ground_truth as not-correct.
        correct = (grp["status"] == "correct").sum()
        n = len(grp)
        rows.append({group_col: key, **accuracy_with_ci(correct, n)})
    return pd.DataFrame(rows)


def _barplot(df: pd.DataFrame, x_col: str, label_map=None, title="", xlabel="", ylabel="Accuracy"):
    fig, ax = plt.subplots(figsize=(max(6, 1.3 * len(df) + 2), 5))
    xs = np.arange(len(df))
    labels = [label_map(k) if label_map else k for k in df[x_col]]

    heights = df["accuracy"].values
    err_low = heights - df["ci_low"].values
    err_high = df["ci_high"].values - heights

    bars = ax.bar(xs, heights, yerr=[err_low, err_high], capsize=4,
                  color=sns.color_palette("deep")[:len(df)], edgecolor="black", linewidth=0.5)

    for i, bar in enumerate(bars):
        h = bar.get_height()
        ci_top = df["ci_high"].iloc[i]
        k = int(df["correct"].iloc[i])
        n = int(df["n"].iloc[i])
        label_y = max(h, ci_top) + 0.03
        ax.text(bar.get_x() + bar.get_width() / 2, label_y,
                f"{k}/{n}\n{h:.0%}", ha="center", va="bottom", fontsize=9)

    ax.set_xticks(xs)
    ax.set_xticklabels(labels, rotation=20, ha="right")
    ax.set_ylim(0, 1.22)
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
    ax.set_title(title)
    ax.axhline(0, color="black", lw=0.5)
    ax.set_yticks(np.linspace(0, 1, 6))
    ax.set_yticklabels([f"{int(y*100)}%" for y in np.linspace(0, 1, 6)])
    return fig


def _heatmap(df: pd.DataFrame, index: str, columns: str, row_order, col_order,
             title: str, row_label_map=None):
    acc = (df[df["status"] == "correct"]
           .groupby([index, columns]).size()
           .unstack(fill_value=0)
           .reindex(index=row_order, columns=col_order, fill_value=0))
    total = (df.groupby([index, columns]).size()
             .unstack(fill_value=0)
             .reindex(index=row_order, columns=col_order, fill_value=0))
    rate = (acc / total.replace(0, np.nan)).fillna(0.0)

    annot = np.empty_like(acc.values, dtype=object)
    for i in range(acc.shape[0]):
        for j in range(acc.shape[1]):
            k = int(acc.values[i, j])
            n = int(total.values[i, j])
            pct = rate.values[i, j]
            annot[i, j] = f"{k}/{n}\n{pct:.0%}"

    fig, ax = plt.subplots(figsize=(max(6, 1.1 * len(col_order) + 3),
                                    max(3, 0.9 * len(row_order) + 1.5)))
    sns.heatmap(rate, vmin=0, vmax=1, cmap="RdYlGn", annot=annot, fmt="",
                cbar_kws={"label": "accuracy"}, ax=ax, linewidths=0.5, linecolor="white")
    if row_label_map:
        ax.set_yticklabels([row_label_map(t.get_text()) for t in ax.get_yticklabels()],
                           rotation=0)
    else:
        ax.set_yticklabels(ax.get_yticklabels(), rotation=0)
    ax.set_title(title)
    ax.set_xlabel(columns)
    ax.set_ylabel(index)
    return fig, rate, acc, total


def run() -> list[str]:
    apply_style()
    scored = load_scored()
    bullets: list[str] = []

    # --- 1. Leaderboard by model ---
    lb_rows = []
    for m in MODEL_ORDER:
        grp = scored[scored["model"] == m]
        correct = (grp["status"] == "correct").sum()
        no_ans = (grp["status"] == "no_answer").sum()
        n = len(grp)
        stats = accuracy_with_ci(correct, n)
        stats.update({
            "model": m,
            "no_answer": int(no_ans),
            "coverage": 1.0 - no_ans / n if n else 0.0,
        })
        lb_rows.append(stats)
    leaderboard = pd.DataFrame(lb_rows)[[
        "model", "correct", "n", "accuracy", "ci_low", "ci_high", "no_answer", "coverage",
    ]]
    save_table(leaderboard, "t1_01_leaderboard_by_model", tier=1)
    fig = _barplot(leaderboard.rename(columns={"model": "group"}), "group",
                   label_map=short_model,
                   title="Overall accuracy by model (Wilson 95% CI)",
                   xlabel="Model")
    save_fig(fig, "t1_01_leaderboard_by_model", tier=1)
    for _, r in leaderboard.iterrows():
        bullets.append(
            f"{short_model(r['model'])}: {int(r['correct'])}/{int(r['n'])} "
            f"({r['accuracy']:.0%}, 95% CI {r['ci_low']:.0%}-{r['ci_high']:.0%})"
        )

    # --- 2. Accuracy by question type ---
    by_qtype = _acc_table(scored, "question_type", QTYPE_ORDER)
    save_table(by_qtype, "t1_02_accuracy_by_question_type", tier=1)
    fig = _barplot(by_qtype.rename(columns={"question_type": "group"}), "group",
                   title="Accuracy by question type (all models pooled)",
                   xlabel="Question type")
    save_fig(fig, "t1_02_accuracy_by_question_type", tier=1)
    best = by_qtype.loc[by_qtype["accuracy"].idxmax()]
    worst = by_qtype.loc[by_qtype["accuracy"].idxmin()]
    bullets.append(
        f"Easiest question type: {best['question_type']} "
        f"({int(best['correct'])}/{int(best['n'])}); "
        f"hardest: {worst['question_type']} "
        f"({int(worst['correct'])}/{int(worst['n'])})."
    )

    # --- 3. Accuracy by state ---
    by_state = _acc_table(scored, "state", STATE_ORDER)
    save_table(by_state, "t1_03_accuracy_by_state", tier=1)
    fig = _barplot(by_state.rename(columns={"state": "group"}), "group",
                   title="Accuracy by state (all models pooled)",
                   xlabel="State")
    save_fig(fig, "t1_03_accuracy_by_state", tier=1)

    # --- 4. Accuracy by program ---
    by_prog = _acc_table(scored, "program", PROGRAM_ORDER)
    save_table(by_prog, "t1_04_accuracy_by_program", tier=1)
    fig = _barplot(by_prog.rename(columns={"program": "group"}), "group",
                   title="Accuracy by program (all models pooled)",
                   xlabel="Program")
    save_fig(fig, "t1_04_accuracy_by_program", tier=1)

    # --- 5. Heatmap model x question_type ---
    fig, rate_mq, acc_mq, tot_mq = _heatmap(
        scored, index="model", columns="question_type",
        row_order=MODEL_ORDER, col_order=QTYPE_ORDER,
        title="Accuracy: model x question type",
        row_label_map=short_model,
    )
    save_fig(fig, "t1_05_heatmap_model_x_qtype", tier=1)
    save_table(rate_mq.reset_index().rename(columns={"model": "model"}),
               "t1_05_heatmap_model_x_qtype_rates", tier=1)
    save_table(acc_mq.reset_index(), "t1_05_heatmap_model_x_qtype_correct", tier=1)

    # --- 6. Heatmap model x state ---
    fig, _, _, _ = _heatmap(
        scored, index="model", columns="state",
        row_order=MODEL_ORDER, col_order=STATE_ORDER,
        title="Accuracy: model x state",
        row_label_map=short_model,
    )
    save_fig(fig, "t1_06_heatmap_model_x_state", tier=1)

    # --- 7. Heatmap model x program ---
    fig, _, _, _ = _heatmap(
        scored, index="model", columns="program",
        row_order=MODEL_ORDER, col_order=PROGRAM_ORDER,
        title="Accuracy: model x program",
        row_label_map=short_model,
    )
    save_fig(fig, "t1_07_heatmap_model_x_program", tier=1)

    # extra bullet: gap between best and worst model
    best_m = leaderboard.loc[leaderboard["accuracy"].idxmax()]
    worst_m = leaderboard.loc[leaderboard["accuracy"].idxmin()]
    bullets.append(
        f"Best-worst model gap: {short_model(best_m['model'])} "
        f"{best_m['accuracy']:.0%} vs {short_model(worst_m['model'])} "
        f"{worst_m['accuracy']:.0%} "
        f"({best_m['accuracy'] - worst_m['accuracy']:+.0%})."
    )

    save_summary(tier=1, lines=bullets)
    return bullets


if __name__ == "__main__":
    lines = run()
    print("Tier 1 summary:")
    for line in lines:
        print(" -", line)
