"""Orchestrator for Tiers 1-4 analysis.

Usage:
  python exp_analysis/run_all_tiers.py --tier all
  python exp_analysis/run_all_tiers.py --tier 2
  python exp_analysis/run_all_tiers.py --tier all --review

The --review flag prints a manifest of every artifact each tier wrote
(path, size, CSV shape or PNG dims) so a reviewer can inspect them in
between tiers.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd
from PIL import Image

if __package__ in (None, ""):
    # Allow `python exp_analysis/run_all_tiers.py` as well as `python -m exp_analysis.run_all_tiers`.
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from exp_analysis import tier1_accuracy, tier2_calibration, tier3_errors, tier4_sources
    from exp_analysis.common import PLOTS_DIR, REPORTS_DIR, TABLES_DIR, REPORTS_DATA_DIR
else:
    from . import tier1_accuracy, tier2_calibration, tier3_errors, tier4_sources
    from .common import PLOTS_DIR, REPORTS_DIR, TABLES_DIR, REPORTS_DATA_DIR

TIER_MODULES = {
    1: tier1_accuracy,
    2: tier2_calibration,
    3: tier3_errors,
    4: tier4_sources,
}


def _manifest_for_tier(tier: int) -> list[str]:
    lines: list[str] = []
    plots = PLOTS_DIR / f"tier{tier}"
    tables = TABLES_DIR / f"tier{tier}"

    if plots.exists():
        for p in sorted(plots.glob("*.png")):
            try:
                with Image.open(p) as im:
                    w, h = im.size
                dim = f"{w}x{h}"
            except Exception:
                dim = "unreadable"
            size_kb = p.stat().st_size / 1024
            lines.append(f"  PNG  {p.relative_to(REPORTS_DIR)}  ({dim}, {size_kb:.0f} KB)")

    if tables.exists():
        for p in sorted(tables.glob("*.csv")):
            try:
                n_rows = len(pd.read_csv(p))
                n_cols = len(pd.read_csv(p, nrows=0).columns)
                shape = f"{n_rows}x{n_cols}"
            except Exception:
                shape = "unreadable"
            lines.append(f"  CSV  {p.relative_to(REPORTS_DIR)}  ({shape})")

    summary = REPORTS_DIR / "summaries" / f"tier{tier}.md"
    if summary.exists():
        lines.append(f"  MD   {summary.relative_to(REPORTS_DIR)}  "
                     f"({summary.stat().st_size} bytes)")
    return lines


def run_tier(tier: int, review: bool = False) -> list[str]:
    mod = TIER_MODULES[tier]
    print(f"\n=== Running Tier {tier}: {mod.__name__} ===")
    bullets = mod.run()
    print("Summary bullets:")
    for b in bullets:
        print(" -", b)
    if review:
        print("\nArtifact manifest:")
        for line in _manifest_for_tier(tier):
            print(line)
    return bullets


def write_reports_readme(all_bullets: dict[int, list[str]]) -> Path:
    path = REPORTS_DIR / "README.md"
    tier_titles = {
        1: "Tier 1 - Headline accuracy",
        2: "Tier 2 - Calibration & self-consistency",
        3: "Tier 3 - Error taxonomy & consolidation gap",
        4: "Tier 4 - Sources & grounding",
    }

    with path.open("w") as f:
        f.write("# Benefits Decoded: LLM benchmark analysis\n\n")
        f.write(
            "Tiered analysis of the 375 raw LLM runs (75 cells x 5 runs) behind "
            "`exp_results/LLM_experiments.csv`. Regenerate with `python exp_analysis/run_all_tiers.py --tier all`.\n\n"
        )

        for tier, title in tier_titles.items():
            f.write(f"## {title}\n\n")
            bullets = all_bullets.get(tier, [])
            for b in bullets:
                f.write(f"- {b}\n")
            f.write("\n")

            plots = sorted((PLOTS_DIR / f"tier{tier}").glob("*.png"))
            tables = sorted((TABLES_DIR / f"tier{tier}").glob("*.md"))
            if plots:
                f.write("### Plots\n\n")
                for p in plots:
                    rel = p.relative_to(REPORTS_DIR).as_posix()
                    f.write(f"![{p.stem}]({rel})\n\n")
            if tables:
                f.write("### Tables (Markdown renderings)\n\n")
                for t in tables:
                    rel = t.relative_to(REPORTS_DIR).as_posix()
                    f.write(f"- [{t.stem}]({rel})\n")
                f.write("\n")
    return path


def main():
    parser = argparse.ArgumentParser(description="Run Tier 1-4 analysis pipeline.")
    parser.add_argument(
        "--tier", choices=["1", "2", "3", "4", "all"], default="all",
        help="Which tier to run (default: all).",
    )
    parser.add_argument(
        "--review", action="store_true",
        help="Print a manifest of every produced artifact after each tier.",
    )
    parser.add_argument(
        "--no-readme", action="store_true",
        help="Skip assembling reports/README.md at the end of an 'all' run.",
    )
    args = parser.parse_args()

    REPORTS_DATA_DIR.mkdir(parents=True, exist_ok=True)

    if args.tier == "all":
        tiers = [1, 2, 3, 4]
    else:
        tiers = [int(args.tier)]

    all_bullets: dict[int, list[str]] = {}
    for t in tiers:
        all_bullets[t] = run_tier(t, review=args.review)

    if not args.no_readme:
        # Pick up any tier summaries not regenerated this run so a single-tier
        # rerun still produces a coherent reports/README.md.
        summaries_dir = REPORTS_DIR / "summaries"
        for t in [1, 2, 3, 4]:
            if t not in all_bullets:
                f = summaries_dir / f"tier{t}.md"
                if f.exists():
                    lines = [l.lstrip("- ").rstrip() for l in f.read_text().splitlines()
                             if l.startswith("- ")]
                    all_bullets[t] = lines
        path = write_reports_readme(all_bullets)
        print(f"\nWrote {path}")


if __name__ == "__main__":
    main()
