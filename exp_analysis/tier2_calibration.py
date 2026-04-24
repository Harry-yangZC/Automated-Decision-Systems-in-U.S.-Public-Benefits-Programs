"""Tier 2 - Calibration and self-consistency.

Outputs (under reports/):
  plots/tier2/t2_01_agreement_rate_dist.png
  plots/tier2/t2_02_confidence_calibration.png
  plots/tier2/t2_03_agreement_vs_accuracy.png
  plots/tier2/t2_04_answer_diversity_hist.png
  tables/tier2/*.csv + *.md
  summaries/tier2.md
"""
from __future__ import annotations

import re

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from .common import (
    MODEL_ORDER,
    accuracy_with_ci,
    apply_style,
    grade_runs,
    load_scored,
    load_summary,
    save_fig,
    save_summary,
    save_table,
    short_model,
)


CONF_ORDER = ["low", "medium", "high"]


def _normalize_answer(ans: str | float, qtype: str) -> str:
    """Normalize per-run answers so that near-identical responses collapse for
    the Tier 2.4 diversity plot."""
    if pd.isna(ans) or ans is None:
        return ""
    s = str(ans).strip()
    if not s:
        return ""
    if qtype == "phone":
        digits = re.sub(r"\D", "", s)
        return digits[-10:] if len(digits) >= 10 else digits
    if qtype == "email":
        m = re.search(r"[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}", s)
        return m.group(0).lower() if m else s.lower()
    if qtype == "address":
        zm = re.search(r"\b\d{5}\b", s)
        pm = re.search(r"P\.?O\.?\s*Box\s+(\d+)", s, re.IGNORECASE)
        if zm:
            return f"zip:{zm.group(0)}"
        if pm:
            return f"pobox:{pm.group(1)}"
        return s.lower().strip()
    if qtype == "agency":
        ab = re.findall(r"\b[A-Z]{2,5}\b", s)
        return ("|".join(sorted(set(ab)))) or s.lower()
    if qtype == "response_time":
        m = re.search(r"(\d+)\s+(business|calendar|working)\s+days?", s, re.IGNORECASE)
        if m:
            num = m.group(1)
            typ = m.group(2).lower()
            typ = "business" if typ == "working" else typ
            return f"{num}-{typ}"
        return s.lower().strip()
    return s.lower().strip()


def _fig_agreement_rate_dist(summary: pd.DataFrame, scored: pd.DataFrame) -> tuple[plt.Figure, pd.DataFrame]:
    df = summary.merge(
        scored[["question_template", "program", "state", "model", "status"]],
        on=["question_template", "program", "state", "model"],
        how="left",
    )
    df = df[df["model"].isin(MODEL_ORDER)].copy()
    df["model_short"] = df["model"].map(short_model)
    df["is_correct"] = df["status"] == "correct"

    fig, ax = plt.subplots(figsize=(9, 5))
    order_short = [short_model(m) for m in MODEL_ORDER]
    sns.violinplot(
        data=df, x="model_short", y="agreement_rate", order=order_short,
        inner=None, cut=0, linewidth=1, color="#d9d9d9", ax=ax,
    )
    sns.stripplot(
        data=df, x="model_short", y="agreement_rate", hue="is_correct",
        order=order_short, dodge=True, palette={True: "#2ca02c", False: "#d62728"},
        edgecolor="black", linewidth=0.3, ax=ax, size=7, alpha=0.85,
    )
    ax.set_ylim(-0.05, 1.1)
    ax.set_ylabel("Agreement rate (top answer share of 5 runs)")
    ax.set_xlabel("Model")
    ax.set_title("Cell-level agreement rate per model (dots coloured by scored status)")
    handles, labels = ax.get_legend_handles_labels()
    if handles:
        ax.legend(handles, ["incorrect", "correct"], title="status", loc="lower right")

    stats = (
        df.groupby("model")["agreement_rate"]
        .agg(mean="mean", median="median", std="std", n="count")
        .reindex(MODEL_ORDER)
        .reset_index()
    )
    stats["model_short"] = stats["model"].map(short_model)
    return fig, stats[["model", "model_short", "mean", "median", "std", "n"]]


def _fig_confidence_calibration(graded: pd.DataFrame) -> tuple[plt.Figure, pd.DataFrame]:
    df = graded.copy()
    df = df[df["run_correct"].notna()]
    df["confidence"] = df["confidence"].astype(str).str.lower().str.strip()
    df = df[df["confidence"].isin(CONF_ORDER)]

    rows = []
    for conf in CONF_ORDER:
        grp = df[df["confidence"] == conf]
        k = int(grp["run_correct"].sum())
        n = len(grp)
        rows.append({"confidence": conf, **accuracy_with_ci(k, n)})
    table = pd.DataFrame(rows)

    fig, ax = plt.subplots(figsize=(8, 5))
    xs = np.arange(len(table))
    colors = {"low": "#d62728", "medium": "#ff7f0e", "high": "#2ca02c"}
    ax.bar(
        xs, table["accuracy"],
        yerr=[table["accuracy"] - table["ci_low"], table["ci_high"] - table["accuracy"]],
        capsize=4, color=[colors[c] for c in table["confidence"]],
        edgecolor="black", linewidth=0.5,
    )
    for i, row in table.iterrows():
        top = max(row["accuracy"], row["ci_high"])
        ax.text(i, top + 0.03,
                f"{int(row['correct'])}/{int(row['n'])}\n{row['accuracy']:.0%}",
                ha="center", va="bottom", fontsize=10)

    ax.set_xticks(xs)
    ax.set_xticklabels([c.capitalize() for c in table["confidence"]])
    ax.set_ylim(0, 1.22)
    ax.set_yticks(np.linspace(0, 1, 6))
    ax.set_yticklabels([f"{int(y*100)}%" for y in np.linspace(0, 1, 6)])
    ax.set_ylabel("Per-run accuracy")
    ax.set_xlabel("Self-reported confidence")
    ax.set_title("Calibration: per-run accuracy by self-reported confidence (95% CI)")
    return fig, table


def _fig_agreement_vs_accuracy(summary: pd.DataFrame, scored: pd.DataFrame) -> tuple[plt.Figure, pd.DataFrame]:
    df = summary.merge(
        scored[["question_template", "program", "state", "model", "status"]],
        on=["question_template", "program", "state", "model"],
        how="left",
    )
    df = df[df["model"].isin(MODEL_ORDER)].copy()
    df["is_correct"] = df["status"] == "correct"

    bins = [0.19, 0.21, 0.41, 0.61, 0.81, 1.01]
    labels = ["0.20", "0.40", "0.60", "0.80", "1.00"]
    df["bin"] = pd.cut(df["agreement_rate"], bins=bins, labels=labels, include_lowest=True)

    rows = []
    for b in labels:
        grp = df[df["bin"] == b]
        k = int(grp["is_correct"].sum())
        n = len(grp)
        rows.append({"agreement_bin": b, **accuracy_with_ci(k, n)})
    pooled = pd.DataFrame(rows)

    per_model_rows = []
    for m in MODEL_ORDER:
        m_df = df[df["model"] == m]
        for b in labels:
            grp = m_df[m_df["bin"] == b]
            k = int(grp["is_correct"].sum())
            n = len(grp)
            per_model_rows.append({
                "model": m, "agreement_bin": b,
                "correct": k, "n": n,
                "accuracy": k / n if n else np.nan,
            })
    per_model = pd.DataFrame(per_model_rows)

    fig, ax = plt.subplots(figsize=(9, 5.2))
    xs = np.arange(len(labels))
    ax.bar(xs, pooled["accuracy"],
           yerr=[pooled["accuracy"] - pooled["ci_low"], pooled["ci_high"] - pooled["accuracy"]],
           capsize=4, color="#4c72b0", edgecolor="black", linewidth=0.5, alpha=0.6,
           label="All models pooled")
    for i, row in pooled.iterrows():
        top = max(row["accuracy"], row["ci_high"])
        ax.text(i, top + 0.03, f"{int(row['correct'])}/{int(row['n'])}",
                ha="center", va="bottom", fontsize=9)

    for m, color in zip(MODEL_ORDER, sns.color_palette("deep")):
        sub = per_model[per_model["model"] == m]
        ax.plot(xs, sub["accuracy"].values, marker="o", linewidth=2, color=color,
                label=short_model(m))

    ax.set_xticks(xs)
    ax.set_xticklabels(labels)
    ax.set_ylim(0, 1.22)
    ax.set_yticks(np.linspace(0, 1, 6))
    ax.set_yticklabels([f"{int(y*100)}%" for y in np.linspace(0, 1, 6)])
    ax.set_xlabel("Agreement rate bin (top answer share)")
    ax.set_ylabel("Cell-level accuracy")
    ax.set_title("Does more run-to-run agreement predict correctness?")
    ax.legend(loc="lower right", fontsize=9)
    return fig, pooled.merge(
        per_model.pivot(index="agreement_bin", columns="model", values="accuracy").reset_index(),
        on="agreement_bin", how="left",
    )


def _fig_answer_diversity(graded: pd.DataFrame) -> tuple[plt.Figure, pd.DataFrame, pd.DataFrame]:
    df = graded.copy()
    df["norm_answer"] = [
        _normalize_answer(a, q) for a, q in zip(df["answer_extracted"], df["question_type"])
    ]
    cell = (
        df.groupby(["question_template", "program", "state", "model", "question_type"])
        .agg(
            unique_answers=("norm_answer", lambda s: len(set(x for x in s if x))),
            total_runs=("norm_answer", "size"),
            example_answers=("answer_extracted", lambda s: " || ".join(
                [str(x) for x in list(dict.fromkeys(s.dropna()))[:3]]
            )),
        )
        .reset_index()
    )

    top_unstable = (
        cell.sort_values(["unique_answers", "model"], ascending=[False, True])
        .head(15)
        .reset_index(drop=True)
    )

    fig, ax = plt.subplots(figsize=(9, 5))
    bins_edges = np.arange(0.5, 6.5, 1)
    xs = np.arange(1, 6)
    width = 0.27

    for i, m in enumerate(MODEL_ORDER):
        counts, _ = np.histogram(
            cell[cell["model"] == m]["unique_answers"].clip(upper=5),
            bins=bins_edges,
        )
        ax.bar(xs + (i - 1) * width, counts, width=width,
               label=short_model(m), edgecolor="black", linewidth=0.3)

    ax.set_xticks(xs)
    ax.set_xticklabels(xs)
    ax.set_xlabel("Distinct normalized answers per cell (out of 5 runs)")
    ax.set_ylabel("Number of cells")
    ax.set_title("Answer diversity across 5 runs (1 = all runs agree)")
    ax.legend()
    return fig, top_unstable, cell


def run() -> list[str]:
    apply_style()
    graded = grade_runs()
    summary = load_summary()
    scored = load_scored()
    bullets: list[str] = []

    # --- 2.1 agreement rate distribution ---
    fig, agree_stats = _fig_agreement_rate_dist(summary, scored)
    save_fig(fig, "t2_01_agreement_rate_dist", tier=2)
    save_table(agree_stats, "t2_01_agreement_rate_stats", tier=2)
    for _, r in agree_stats.iterrows():
        bullets.append(
            f"Mean agreement ({r['model_short']}): {r['mean']:.2f} "
            f"(median {r['median']:.2f})"
        )

    # --- 2.2 confidence calibration ---
    fig, conf_tbl = _fig_confidence_calibration(graded)
    save_fig(fig, "t2_02_confidence_calibration", tier=2)
    save_table(conf_tbl, "t2_02_confidence_calibration", tier=2)
    high = conf_tbl[conf_tbl["confidence"] == "high"].iloc[0] if (conf_tbl["confidence"] == "high").any() else None
    if high is not None:
        bullets.append(
            f"Calibration: confidence=high covers {int(high['n'])} runs with only "
            f"{high['accuracy']:.0%} per-run accuracy (95% CI "
            f"{high['ci_low']:.0%}-{high['ci_high']:.0%})."
        )

    # --- 2.3 agreement vs accuracy ---
    fig, agree_acc = _fig_agreement_vs_accuracy(summary, scored)
    save_fig(fig, "t2_03_agreement_vs_accuracy", tier=2)
    save_table(agree_acc, "t2_03_agreement_vs_accuracy", tier=2)
    low_bin = agree_acc[agree_acc["agreement_bin"] == "0.20"].iloc[0]
    top_bin = agree_acc[agree_acc["agreement_bin"] == "1.00"].iloc[0]
    bullets.append(
        f"Cells where all 5 runs agree (bin 1.00): {int(top_bin['correct'])}/{int(top_bin['n'])} "
        f"correct ({top_bin['accuracy']:.0%}); cells with bin 0.20: "
        f"{int(low_bin['correct'])}/{int(low_bin['n'])} ({low_bin['accuracy']:.0%})."
    )

    # --- 2.4 answer diversity ---
    fig, top_unstable, cell_all = _fig_answer_diversity(graded)
    save_fig(fig, "t2_04_answer_diversity_hist", tier=2)
    save_table(top_unstable, "t2_04_top_unstable_cells", tier=2)
    save_table(
        cell_all[["question_template", "program", "state", "model", "question_type",
                  "unique_answers", "total_runs"]],
        "t2_04_answer_diversity_per_cell", tier=2,
    )
    bullets.append(
        f"Mean distinct answers per cell: "
        f"{cell_all['unique_answers'].mean():.2f} of 5; "
        f"{int((cell_all['unique_answers'] == 1).sum())}/{len(cell_all)} cells have "
        f"all 5 runs identical after normalization."
    )

    save_summary(tier=2, lines=bullets)
    return bullets


if __name__ == "__main__":
    lines = run()
    print("Tier 2 summary:")
    for line in lines:
        print(" -", line)
