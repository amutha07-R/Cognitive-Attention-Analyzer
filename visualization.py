"""
visualization.py
----------------
All Matplotlib chart generation for the Stroop test dashboard.

Every chart function returns a matplotlib.figure.Figure object
that can be passed directly to st.pyplot().

Design choices:
- Dark background (#1A1A2E) to match the Streamlit dark theme.
- Consistent colour palette for congruent vs incongruent bars.
- Clear labels, units, and titles on every chart.
"""

import matplotlib
matplotlib.use("Agg")  # non-interactive backend for Streamlit

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List


# ─────────────────────────────────────────────
# Shared style constants
# ─────────────────────────────────────────────

BG_COLOUR     = "#1A1A2E"
PANEL_COLOUR  = "#16213E"
TEXT_COLOUR   = "#E0E0E0"
GRID_COLOUR   = "#2C2C54"

# Condition colours
CONG_COLOUR   = "#27AE60"   # green  – congruent
INCONG_COLOUR = "#E74C3C"   # red    – incongruent
NEUTRAL_COLOUR = "#3498DB"  # blue   – overall / neutral

FONT_FAMILY = "DejaVu Sans"

plt.rcParams.update({
    "figure.facecolor":  BG_COLOUR,
    "axes.facecolor":    PANEL_COLOUR,
    "axes.edgecolor":    GRID_COLOUR,
    "axes.labelcolor":   TEXT_COLOUR,
    "axes.titlecolor":   TEXT_COLOUR,
    "xtick.color":       TEXT_COLOUR,
    "ytick.color":       TEXT_COLOUR,
    "text.color":        TEXT_COLOUR,
    "grid.color":        GRID_COLOUR,
    "grid.linewidth":    0.6,
    "font.family":       FONT_FAMILY,
})


def _new_fig(figsize=(7, 4.5)):
    """Return a new (fig, ax) pair with the shared dark style applied."""
    fig, ax = plt.subplots(figsize=figsize, facecolor=BG_COLOUR)
    ax.set_facecolor(PANEL_COLOUR)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(GRID_COLOUR)
    ax.spines["bottom"].set_color(GRID_COLOUR)
    return fig, ax


def _add_value_labels(ax, bars, fmt="{:.0f}", offset=3, color=TEXT_COLOUR, fontsize=10):
    """Add numeric labels on top of each bar."""
    for bar in bars:
        height = bar.get_height()
        if not np.isnan(height):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                height + offset,
                fmt.format(height),
                ha="center", va="bottom",
                color=color, fontsize=fontsize, fontweight="bold",
            )


# ─────────────────────────────────────────────
# Chart 1 – Reaction Time Comparison
# ─────────────────────────────────────────────

def plot_rt_comparison(summary: Dict[str, Any]) -> plt.Figure:
    """
    Bar chart comparing average reaction times for congruent vs incongruent trials.

    Parameters
    ----------
    summary : dict – output of analysis.compute_summary()

    Returns
    -------
    matplotlib Figure
    """
    cong_rt   = summary.get("congruent_rt_ms")
    incong_rt = summary.get("incongruent_rt_ms")

    labels = []
    values = []
    colours = []

    if cong_rt is not None:
        labels.append("Congruent")
        values.append(cong_rt)
        colours.append(CONG_COLOUR)

    if incong_rt is not None:
        labels.append("Incongruent")
        values.append(incong_rt)
        colours.append(INCONG_COLOUR)

    fig, ax = _new_fig()

    if not values:
        ax.text(0.5, 0.5, "No data available", transform=ax.transAxes,
                ha="center", va="center", color=TEXT_COLOUR, fontsize=14)
        ax.set_title("Average Reaction Time by Trial Condition", fontsize=13, fontweight="bold", pad=12)
        return fig

    x = np.arange(len(labels))
    bars = ax.bar(x, values, color=colours, width=0.45, zorder=3, edgecolor="none")

    _add_value_labels(ax, bars, fmt="{:.0f} ms")

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=12)
    ax.set_ylabel("Average Reaction Time (ms)", fontsize=11)
    ax.set_title("Average Reaction Time by Trial Condition", fontsize=13, fontweight="bold", pad=12)
    ax.set_ylim(0, max(values) * 1.3 if values else 1000)

    legend_elements = [
        mpatches.Patch(color=CONG_COLOUR,   label="Congruent"),
        mpatches.Patch(color=INCONG_COLOUR, label="Incongruent"),
    ]
    ax.legend(handles=legend_elements, loc="upper right",
              facecolor=PANEL_COLOUR, edgecolor=GRID_COLOUR,
              labelcolor=TEXT_COLOUR, fontsize=10)

    fig.tight_layout()
    return fig


# ─────────────────────────────────────────────
# Chart 2 – Accuracy Comparison
# ─────────────────────────────────────────────

def plot_accuracy_comparison(summary: Dict[str, Any]) -> plt.Figure:
    """
    Bar chart comparing accuracy percentages for congruent vs incongruent trials.
    """
    cong_acc   = summary.get("congruent_acc_pct")
    incong_acc = summary.get("incongruent_acc_pct")

    labels = []
    values = []
    colours = []

    if cong_acc is not None:
        labels.append("Congruent")
        values.append(cong_acc)
        colours.append(CONG_COLOUR)

    if incong_acc is not None:
        labels.append("Incongruent")
        values.append(incong_acc)
        colours.append(INCONG_COLOUR)

    fig, ax = _new_fig()

    if not values:
        ax.text(0.5, 0.5, "No data available", transform=ax.transAxes,
                ha="center", va="center", color=TEXT_COLOUR, fontsize=14)
        ax.set_title("Accuracy (%) by Trial Condition", fontsize=13, fontweight="bold", pad=12)
        return fig

    x = np.arange(len(labels))
    bars = ax.bar(x, values, color=colours, width=0.45, zorder=3, edgecolor="none")
    _add_value_labels(ax, bars, fmt="{:.1f}%")

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=12)
    ax.set_ylabel("Accuracy (%)", fontsize=11)
    ax.set_ylim(0, 115)
    ax.axhline(100, color=GRID_COLOUR, linewidth=0.8, linestyle=":")
    ax.set_title("Accuracy (%) by Trial Condition", fontsize=13, fontweight="bold", pad=12)

    fig.tight_layout()
    return fig


# ─────────────────────────────────────────────
# Chart 3 – Trial-by-Trial Reaction Time
# ─────────────────────────────────────────────

def plot_trial_by_trial_rt(trials_df: pd.DataFrame) -> plt.Figure:
    """
    Line + scatter chart showing reaction time for every trial in sequence.
    Congruent trials are shown in green, incongruent in red.

    Parameters
    ----------
    trials_df : pd.DataFrame – session trials with trial_number, reaction_time_ms, condition
    """
    fig, ax = _new_fig(figsize=(9, 4))

    if trials_df.empty or "reaction_time_ms" not in trials_df.columns:
        ax.text(0.5, 0.5, "No trial data available", transform=ax.transAxes,
                ha="center", va="center", color=TEXT_COLOUR, fontsize=14)
        ax.set_title("Reaction Time per Trial", fontsize=13, fontweight="bold", pad=12)
        return fig

    df = trials_df.copy()
    df["reaction_time_ms"] = pd.to_numeric(df["reaction_time_ms"], errors="coerce")
    df["trial_number"]     = pd.to_numeric(df["trial_number"], errors="coerce")
    df = df.dropna(subset=["reaction_time_ms", "trial_number"]).sort_values("trial_number")

    if df.empty:
        ax.text(0.5, 0.5, "No valid reaction time data", transform=ax.transAxes,
                ha="center", va="center", color=TEXT_COLOUR, fontsize=14)
        ax.set_title("Reaction Time per Trial", fontsize=13, fontweight="bold", pad=12)
        return fig

    # Overall line
    ax.plot(df["trial_number"], df["reaction_time_ms"],
            color="#5D6D7E", linewidth=1.2, alpha=0.5, zorder=1)

    # Scatter coloured by condition
    for cond, colour, label in [
        ("congruent",   CONG_COLOUR,   "Congruent"),
        ("incongruent", INCONG_COLOUR, "Incongruent"),
    ]:
        subset = df[df["condition"] == cond]
        ax.scatter(
            subset["trial_number"], subset["reaction_time_ms"],
            c=colour, s=55, zorder=3, label=label, edgecolors="none",
        )

    # Mean lines
    overall_mean = df["reaction_time_ms"].mean()
    ax.axhline(overall_mean, color=NEUTRAL_COLOUR, linewidth=1.2,
               linestyle="--", alpha=0.7, label=f"Mean: {overall_mean:.0f} ms")

    ax.set_xlabel("Trial Number", fontsize=11)
    ax.set_ylabel("Reaction Time (ms)", fontsize=11)
    ax.set_title("Reaction Time per Trial", fontsize=13, fontweight="bold", pad=12)
    ax.legend(facecolor=PANEL_COLOUR, edgecolor=GRID_COLOUR,
              labelcolor=TEXT_COLOUR, fontsize=9, loc="upper right")

    ax.set_xticks(df["trial_number"].astype(int).unique())
    fig.tight_layout()
    return fig


# ─────────────────────────────────────────────
# Chart 4 – Multi-session comparison (optional)
# ─────────────────────────────────────────────

def plot_session_comparison(comparison_df: pd.DataFrame, metric: str, ylabel: str) -> plt.Figure:
    """
    Horizontal bar chart comparing a single metric across sessions.

    Parameters
    ----------
    comparison_df : pd.DataFrame – output of analysis.compare_sessions()
    metric        : column name to plot
    ylabel        : axis label string
    """
    fig, ax = _new_fig(figsize=(8, max(3.5, len(comparison_df) * 0.7)))

    if comparison_df.empty or metric not in comparison_df.columns:
        ax.text(0.5, 0.5, "No comparison data available", transform=ax.transAxes,
                ha="center", va="center", color=TEXT_COLOUR, fontsize=14)
        ax.set_title(f"Session Comparison – {ylabel}", fontsize=13, fontweight="bold", pad=12)
        return fig

    df = comparison_df.copy()
    df[metric] = pd.to_numeric(df[metric], errors="coerce")
    df = df.dropna(subset=[metric])

    labels = df.apply(
        lambda r: f"{r.get('Participant ID','?')} ({r.get('Session','?')})", axis=1
    )
    values = df[metric].values

    y_pos = np.arange(len(labels))
    colours = [NEUTRAL_COLOUR] * len(values)

    bars = ax.barh(y_pos, values, color=colours, edgecolor="none", height=0.5, zorder=3)

    for bar, val in zip(bars, values):
        ax.text(val + max(values) * 0.01, bar.get_y() + bar.get_height() / 2,
                f"{val:.1f}", va="center", color=TEXT_COLOUR, fontsize=9, fontweight="bold")

    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_xlabel(ylabel, fontsize=11)
    ax.set_title(f"Session Comparison – {ylabel}", fontsize=13, fontweight="bold", pad=12)
    ax.grid(axis="x", linestyle="--", alpha=0.4)

    fig.tight_layout()
    return fig
