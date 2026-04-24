"""Tier 4 - Sources and grounding.

Outputs (under reports/):
  plots/tier4/t4_01_source_domain_distribution.png
  plots/tier4/t4_02_gov_ratio_vs_correctness.png
  plots/tier4/t4_03_source_count_vs_correctness.png
  plots/tier4/t4_04_citation_state_consistency.png
  tables/tier4/*.csv + *.md
  summaries/tier4.md
"""
from __future__ import annotations

from collections import Counter

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from .common import (
    MODEL_ORDER,
    accuracy_with_ci,
    apply_style,
    extract_domain,
    is_gov,
    load_raw,
    load_scored,
    load_summary,
    save_fig,
    save_summary,
    save_table,
    short_model,
    split_sources,
    state_domain_match,
)


# ---------------------------------------------------------------------------
# 4.1 Source domain distribution per model
# ---------------------------------------------------------------------------

def _fig_domain_distribution(raw: pd.DataFrame) -> tuple[plt.Figure, pd.DataFrame]:
    rows = []
    for _, r in raw.iterrows():
        dom = extract_domain(r.get("source"))
        if dom:
            rows.append({"model": r["model"], "domain": dom})
    dd = pd.DataFrame(rows)

    top_global = [d for d, _ in Counter(dd["domain"]).most_common(15)]

    counts = (
        dd[dd["domain"].isin(top_global)]
        .groupby(["model", "domain"]).size()
        .unstack(fill_value=0)
        .reindex(index=MODEL_ORDER, columns=top_global, fill_value=0)
    )

    fig, ax = plt.subplots(figsize=(12, 5.5))
    width = 0.27
    xs = np.arange(len(top_global))
    for i, m in enumerate(MODEL_ORDER):
        ax.bar(xs + (i - 1) * width, counts.loc[m].values, width=width,
               label=short_model(m), edgecolor="black", linewidth=0.3)
    ax.set_xticks(xs)
    ax.set_xticklabels(top_global, rotation=40, ha="right", fontsize=9)
    ax.set_ylabel("Run-level citations")
    ax.set_title("Top 15 cited domains per model (across all 5 runs per cell)")
    ax.legend(fontsize=9)
    return fig, counts.reset_index()


# ---------------------------------------------------------------------------
# 4.2 .gov ratio per cell vs correctness
# ---------------------------------------------------------------------------

def _cell_gov_stats(raw: pd.DataFrame) -> pd.DataFrame:
    rows = []
    grp_keys = ["question_template", "program", "state", "model"]
    for keys, grp in raw.groupby(grp_keys):
        urls = [u for u in grp["source"].dropna().tolist() if isinstance(u, str)]
        n = len(urls)
        if n == 0:
            rows.append(dict(zip(grp_keys, keys), n_runs_with_url=0, gov_ratio=np.nan,
                             unique_domains=0))
            continue
        gov_count = sum(1 for u in urls if is_gov(u))
        unique = len({extract_domain(u) for u in urls if extract_domain(u)})
        rows.append(dict(zip(grp_keys, keys), n_runs_with_url=n, gov_ratio=gov_count / n,
                         unique_domains=unique))
    return pd.DataFrame(rows)


def _fig_gov_vs_correctness(raw: pd.DataFrame, scored: pd.DataFrame):
    cell = _cell_gov_stats(raw)
    cell = cell.merge(
        scored[["question_template", "program", "state", "model", "status"]],
        on=["question_template", "program", "state", "model"], how="left",
    )
    cell["is_correct"] = cell["status"] == "correct"

    rows = []
    for m in MODEL_ORDER:
        for status in [True, False]:
            sub = cell[(cell["model"] == m) & (cell["is_correct"] == status)]
            n = len(sub)
            mean_gov = sub["gov_ratio"].mean()
            # Wilson CI on mean .gov ratio doesn't strictly apply (not Bernoulli),
            # so report mean +/- std error as CI-style bars.
            se = sub["gov_ratio"].std(ddof=1) / np.sqrt(n) if n > 1 else 0.0
            rows.append({
                "model": m, "is_correct": status, "n_cells": n,
                "mean_gov_ratio": mean_gov,
                "ci_low": max(0.0, (mean_gov or 0) - 1.96 * se),
                "ci_high": min(1.0, (mean_gov or 0) + 1.96 * se),
            })
    tbl = pd.DataFrame(rows)

    fig, ax = plt.subplots(figsize=(9, 5))
    xs = np.arange(len(MODEL_ORDER))
    width = 0.36
    for i, status in enumerate([True, False]):
        sub = tbl[tbl["is_correct"] == status].set_index("model").reindex(MODEL_ORDER)
        means = sub["mean_gov_ratio"].values
        errs_low = means - sub["ci_low"].values
        errs_high = sub["ci_high"].values - means
        ax.bar(xs + (i - 0.5) * width, means, width=width,
               yerr=[errs_low, errs_high], capsize=4,
               color="#2ca02c" if status else "#d62728",
               edgecolor="black", linewidth=0.3,
               label="correct" if status else "incorrect")
        for j, v in enumerate(means):
            n = int(sub["n_cells"].iloc[j])
            if not np.isnan(v):
                ax.text(xs[j] + (i - 0.5) * width, v + 0.03,
                        f"{v:.0%}\n(n={n})", ha="center", va="bottom", fontsize=9)

    ax.set_xticks(xs)
    ax.set_xticklabels([short_model(m) for m in MODEL_ORDER])
    ax.set_ylim(0, 1.2)
    ax.set_yticks(np.linspace(0, 1, 6))
    ax.set_yticklabels([f"{int(y*100)}%" for y in np.linspace(0, 1, 6)])
    ax.set_ylabel("Mean fraction of cited URLs with .gov TLD")
    ax.set_title("Does citing .gov sources correlate with cell correctness?")
    ax.legend()
    return fig, tbl, cell


# ---------------------------------------------------------------------------
# 4.3 Source count vs correctness
# ---------------------------------------------------------------------------

def _fig_source_count(summary: pd.DataFrame, scored: pd.DataFrame):
    df = summary.merge(
        scored[["question_template", "program", "state", "model", "status"]],
        on=["question_template", "program", "state", "model"], how="left",
    )
    df["n_unique_sources"] = df["sources"].apply(lambda s: len(split_sources(s)))
    df["is_correct"] = df["status"] == "correct"

    fig, ax = plt.subplots(figsize=(9, 5))
    sns.boxplot(
        data=df, x="model", y="n_unique_sources", hue="is_correct",
        order=MODEL_ORDER, ax=ax,
        palette={True: "#2ca02c", False: "#d62728"},
    )
    sns.stripplot(
        data=df, x="model", y="n_unique_sources", hue="is_correct",
        order=MODEL_ORDER, dodge=True, ax=ax, size=4, alpha=0.7,
        palette={True: "#154d14", False: "#6d0d0d"},
    )
    ax.set_xticks(range(len(MODEL_ORDER)))
    ax.set_xticklabels([short_model(m) for m in MODEL_ORDER])
    ax.set_ylabel("Unique cited URLs per cell")
    ax.set_xlabel("Model")
    ax.set_title("Source breadth vs correctness")
    # seaborn adds duplicate legend entries (one from box, one from strip).
    handles, labels = ax.get_legend_handles_labels()
    seen: dict[str, object] = {}
    for h, l in zip(handles, labels):
        if l not in seen:
            seen[l] = h
    ax.legend(seen.values(), ["incorrect", "correct"], title="status", loc="upper right")
    summary_tbl = (
        df.groupby(["model", "is_correct"])["n_unique_sources"]
        .agg(["mean", "median", "min", "max", "count"])
        .reset_index()
    )
    return fig, summary_tbl


# ---------------------------------------------------------------------------
# 4.4 Citation-state consistency
# ---------------------------------------------------------------------------

def _fig_state_consistency(raw: pd.DataFrame, scored: pd.DataFrame):
    rows = []
    grp_keys = ["question_template", "program", "state", "model"]
    for keys, grp in raw.groupby(grp_keys):
        urls = [u for u in grp["source"].dropna().tolist() if isinstance(u, str)]
        state = keys[2]
        if not urls:
            rows.append(dict(zip(grp_keys, keys), any_state_match=False,
                             frac_state_match=np.nan, n_urls=0))
            continue
        state_hits = sum(1 for u in urls if state_domain_match(state, u))
        rows.append(dict(zip(grp_keys, keys), any_state_match=state_hits > 0,
                         frac_state_match=state_hits / len(urls), n_urls=len(urls)))
    cell = pd.DataFrame(rows)
    cell = cell.merge(
        scored[["question_template", "program", "state", "model", "status"]],
        on=grp_keys, how="left",
    )
    cell["is_correct"] = cell["status"] == "correct"

    tbl_rows = []
    for m in MODEL_ORDER:
        for status in [True, False]:
            sub = cell[(cell["model"] == m) & (cell["is_correct"] == status)]
            k = int(sub["any_state_match"].sum())
            n = len(sub)
            tbl_rows.append({
                "model": m, "is_correct": status,
                **accuracy_with_ci(k, n),
            })
    tbl = pd.DataFrame(tbl_rows)

    fig, ax = plt.subplots(figsize=(9, 5))
    xs = np.arange(len(MODEL_ORDER))
    width = 0.36
    for i, status in enumerate([True, False]):
        sub = tbl[tbl["is_correct"] == status].set_index("model").reindex(MODEL_ORDER)
        means = sub["accuracy"].values
        errs_low = means - sub["ci_low"].values
        errs_high = sub["ci_high"].values - means
        ax.bar(xs + (i - 0.5) * width, means, width=width,
               yerr=[errs_low, errs_high], capsize=4,
               color="#2ca02c" if status else "#d62728",
               edgecolor="black", linewidth=0.3,
               label="correct" if status else "incorrect")
        for j, v in enumerate(means):
            n = int(sub["n"].iloc[j])
            k = int(sub["correct"].iloc[j])
            ax.text(xs[j] + (i - 0.5) * width, v + 0.03,
                    f"{k}/{n}\n{v:.0%}", ha="center", va="bottom", fontsize=9)

    ax.set_xticks(xs)
    ax.set_xticklabels([short_model(m) for m in MODEL_ORDER])
    ax.set_ylim(0, 1.22)
    ax.set_yticks(np.linspace(0, 1, 6))
    ax.set_yticklabels([f"{int(y*100)}%" for y in np.linspace(0, 1, 6)])
    ax.set_ylabel("Share of cells with >=1 state-specific citation")
    ax.set_title("Citation-state consistency per model, split by correctness")
    ax.legend()
    return fig, tbl, cell


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def run() -> list[str]:
    apply_style()
    raw = load_raw()
    summary = load_summary()
    scored = load_scored()
    bullets: list[str] = []

    # --- 4.1 domain distribution
    fig, counts = _fig_domain_distribution(raw)
    save_fig(fig, "t4_01_source_domain_distribution", tier=4)
    save_table(counts, "t4_01_source_domain_distribution", tier=4)
    bullets.append(
        f"Top domain across all models: "
        f"{counts.set_index('model').sum(axis=0).idxmax()}."
    )

    # --- 4.2 .gov ratio
    fig, gov_tbl, gov_cell = _fig_gov_vs_correctness(raw, scored)
    save_fig(fig, "t4_02_gov_ratio_vs_correctness", tier=4)
    save_table(gov_tbl, "t4_02_gov_ratio_vs_correctness", tier=4)
    save_table(gov_cell, "t4_02_gov_ratio_per_cell", tier=4)
    for m in MODEL_ORDER:
        sub = gov_tbl[gov_tbl["model"] == m]
        c = sub[sub["is_correct"]].iloc[0]
        w = sub[~sub["is_correct"]].iloc[0]
        bullets.append(
            f"{short_model(m)} .gov ratio: correct {c['mean_gov_ratio']:.0%} "
            f"(n={int(c['n_cells'])}) vs incorrect {w['mean_gov_ratio']:.0%} "
            f"(n={int(w['n_cells'])})."
        )

    # --- 4.3 source count
    fig, count_tbl = _fig_source_count(summary, scored)
    save_fig(fig, "t4_03_source_count_vs_correctness", tier=4)
    save_table(count_tbl, "t4_03_source_count_vs_correctness", tier=4)
    bullets.append(
        "See t4_03 for per-model breakdown of unique URL counts per cell "
        "split by correctness."
    )

    # --- 4.4 state consistency
    fig, state_tbl, state_cell = _fig_state_consistency(raw, scored)
    save_fig(fig, "t4_04_citation_state_consistency", tier=4)
    save_table(state_tbl, "t4_04_citation_state_consistency", tier=4)
    save_table(state_cell, "t4_04_citation_state_per_cell", tier=4)
    for m in MODEL_ORDER:
        sub = state_tbl[state_tbl["model"] == m]
        c = sub[sub["is_correct"]].iloc[0]
        w = sub[~sub["is_correct"]].iloc[0]
        bullets.append(
            f"{short_model(m)} state-specific citations: correct "
            f"{int(c['correct'])}/{int(c['n'])} ({c['accuracy']:.0%}), "
            f"incorrect {int(w['correct'])}/{int(w['n'])} ({w['accuracy']:.0%})."
        )

    save_summary(tier=4, lines=bullets)
    return bullets


if __name__ == "__main__":
    lines = run()
    print("Tier 4 summary:")
    for line in lines:
        print(" -", line)
