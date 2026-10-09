"""
analysis.py
-----------
Statistical analysis functions for Stroop test results.

All functions work on a list of trial-result dicts (as produced by
storage.load_session_trials) or on a pandas DataFrame.

No machine-learning is used here. Analysis is descriptive statistics:
means, counts, accuracy rates, and condition comparisons.
"""

import pandas as pd
from typing import Dict, Any, List, Optional


def compute_summary(trials_df: pd.DataFrame) -> Dict[str, Any]:
    """Compute participant-level summary statistics from trial data."""
    if trials_df.empty:
        return _empty_summary()

    df = trials_df.copy()
    df["is_correct"] = df["is_correct"].astype(bool)
    df["reaction_time_ms"] = pd.to_numeric(
        df["reaction_time_ms"], errors="coerce"
    )

    total = len(df)
    correct = int(df["is_correct"].sum())
    incorrect = total - correct
    accuracy = round((correct / total) * 100, 2) if total else 0.0
    error_rate = round(100.0 - accuracy, 2)

    all_rt_mean = _safe_mean(df["reaction_time_ms"])
    correct_rt_mean = _safe_mean(
        df.loc[df["is_correct"], "reaction_time_ms"]
    )

    cong_df = df[df["condition"] == "congruent"]
    incong_df = df[df["condition"] == "incongruent"]

    cong_rt = _safe_mean(cong_df["reaction_time_ms"])
    incong_rt = _safe_mean(incong_df["reaction_time_ms"])
    cong_acc = _safe_accuracy(cong_df)
    incong_acc = _safe_accuracy(incong_df)

    rt_difference = None
    if cong_rt is not None and incong_rt is not None:
        rt_difference = round(incong_rt - cong_rt, 2)

    return {
        "total_trials": total,
        "correct": correct,
        "incorrect": incorrect,
        "accuracy_pct": accuracy,
        "error_rate_pct": error_rate,
        "mean_rt_ms": _fmt(all_rt_mean),
        "mean_rt_correct_ms": _fmt(correct_rt_mean),
        "congruent_rt_ms": _fmt(cong_rt),
        "incongruent_rt_ms": _fmt(incong_rt),
        "congruent_acc_pct": _fmt(cong_acc),
        "incongruent_acc_pct": _fmt(incong_acc),
        "rt_difference_ms": _fmt(rt_difference),
        "congruent_trials": len(cong_df),
        "incongruent_trials": len(incong_df),
    }


def _empty_summary() -> Dict[str, Any]:
    """Return zero/None values when no trials exist."""
    keys = [
        "total_trials", "correct", "incorrect", "accuracy_pct",
        "error_rate_pct", "mean_rt_ms", "mean_rt_correct_ms",
        "congruent_rt_ms", "incongruent_rt_ms", "congruent_acc_pct",
        "incongruent_acc_pct", "rt_difference_ms",
        "congruent_trials", "incongruent_trials",
    ]
    return {
        key: 0 if key in (
            "total_trials", "correct", "incorrect",
            "congruent_trials", "incongruent_trials"
        ) else None
        for key in keys
    }


def _safe_mean(series: pd.Series) -> Optional[float]:
    """Return rounded mean or None if no valid values exist."""
    valid = series.dropna()
    if valid.empty:
        return None
    return round(float(valid.mean()), 2)


def _safe_accuracy(df: pd.DataFrame) -> Optional[float]:
    """Return accuracy percentage, or None for an empty subset."""
    if df.empty:
        return None
    return round(float(df["is_correct"].mean()) * 100, 2)


def _fmt(value: Optional[float]) -> Optional[float]:
    """Return rounded float or None."""
    if value is None:
        return None
    return round(float(value), 2)


def generate_interpretation(summary: Dict[str, Any]) -> str:
    """Generate a cautious interpretation of task performance."""
    lines: List[str] = []
    total = summary.get("total_trials", 0)

    if not total:
        return "No trial data available for interpretation."

    acc = summary.get("accuracy_pct")
    cong_rt = summary.get("congruent_rt_ms")
    incong_rt = summary.get("incongruent_rt_ms")
    rt_diff = summary.get("rt_difference_ms")
    cong_acc = summary.get("congruent_acc_pct")
    incong_acc = summary.get("incongruent_acc_pct")

    if acc is not None:
        if acc >= 90:
            lines.append(
                f"Overall accuracy was {acc}%, showing strong performance "
                f"in identifying ink colours across {total} trials."
            )
        elif acc >= 70:
            lines.append(
                f"Overall accuracy was {acc}% across {total} trials, "
                "suggesting moderate performance on the colour-identification task."
            )
        else:
            lines.append(
                f"Overall accuracy was {acc}% across {total} trials. This may "
                "reflect distraction, unfamiliarity with the task, or interference."
            )

    if rt_diff is not None:
        if rt_diff > 0:
            lines.append(
                f"Incongruent trials took approximately {abs(rt_diff):.0f} ms "
                "longer than congruent trials on average. This is consistent "
                "with the Stroop interference effect, where conflicting word "
                "meaning and ink colour can slow colour identification."
            )
        elif rt_diff < 0:
            lines.append(
                f"Congruent trials took approximately {abs(rt_diff):.0f} ms "
                "longer than incongruent trials. This atypical pattern may "
                "reflect strategy, practice, or random variation in this session."
            )
        else:
            lines.append(
                "Reaction times were similar across both conditions in this session."
            )

    # Accuracy difference comment: report each condition's own accuracy value.
    if cong_acc is not None and incong_acc is not None:
        diff_acc = round(cong_acc - incong_acc, 1)
        if abs(diff_acc) >= 5:
            if diff_acc > 0:
                better, worse = "congruent", "incongruent"
                better_acc, worse_acc = cong_acc, incong_acc
            else:
                better, worse = "incongruent", "congruent"
                better_acc, worse_acc = incong_acc, cong_acc

            lines.append(
                f"Accuracy was higher on {better} trials ({better_acc}%) than "
                f"on {worse} trials ({worse_acc}%). This describes this session "
                "only; more trials are needed to determine whether the pattern "
                "is consistent."
            )
        else:
            lines.append(
                f"Accuracy was similar across both trial types (congruent: "
                f"{cong_acc}%, incongruent: {incong_acc}%)."
            )

    lines.append(
        "\n⚠️ **Important:** This analysis describes performance on this "
        "computer-based task only. It is not a clinical, psychological, or "
        "neurological assessment. Results can be affected by screen latency, "
        "practice, fatigue, and individual differences."
    )
    return "  \n".join(lines)


def compare_sessions(summaries: List[Dict[str, Any]]) -> pd.DataFrame:
    """Build a comparison DataFrame from multiple session summaries."""
    if not summaries:
        return pd.DataFrame()

    rows = []
    for summary in summaries:
        rows.append({
            "Participant ID": summary.get("participant_id", "—"),
            "Session": summary.get("session_id", "—"),
            "Timestamp": summary.get("timestamp", "—"),
            "Total Trials": summary.get("total_trials", 0),
            "Accuracy (%)": summary.get("accuracy_pct"),
            "Mean RT (ms)": summary.get("mean_rt_ms"),
            "Congruent RT (ms)": summary.get("congruent_rt_ms"),
            "Incongruent RT (ms)": summary.get("incongruent_rt_ms"),
            "RT Difference (ms)": summary.get("rt_difference_ms"),
            "Congruent Acc (%)": summary.get("congruent_acc_pct"),
            "Incongruent Acc (%)": summary.get("incongruent_acc_pct"),
        })

    return pd.DataFrame(rows)
