"""
storage.py
----------
Handles all CSV file reading and writing for the Stroop test application.

Two CSV files are maintained:
  1. data/trials.csv       – one row per individual trial
  2. data/summaries.csv    – one row per completed participant session

File handling is safe: files are created automatically when missing.
Existing data is never overwritten; new rows are appended.
"""

import os
import csv
import uuid
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List, Optional

# ─────────────────────────────────────────────
# File paths  (relative to project root)
# ─────────────────────────────────────────────
DATA_DIR      = "data"
TRIALS_CSV    = os.path.join(DATA_DIR, "trials.csv")
SUMMARIES_CSV = os.path.join(DATA_DIR, "summaries.csv")

# ─────────────────────────────────────────────
# Column definitions
# ─────────────────────────────────────────────
TRIAL_COLUMNS = [
    "session_id",
    "participant_id",
    "timestamp",
    "trial_number",
    "word",
    "ink_colour",
    "condition",
    "correct_answer",
    "participant_answer",
    "is_correct",
    "reaction_time_ms",
]

SUMMARY_COLUMNS = [
    "session_id",
    "participant_id",
    "timestamp",
    "total_trials",
    "correct",
    "incorrect",
    "accuracy_pct",
    "error_rate_pct",
    "mean_rt_ms",
    "mean_rt_correct_ms",
    "congruent_trials",
    "congruent_rt_ms",
    "congruent_acc_pct",
    "incongruent_trials",
    "incongruent_rt_ms",
    "incongruent_acc_pct",
    "rt_difference_ms",
]


# ─────────────────────────────────────────────
# Directory / file initialisation
# ─────────────────────────────────────────────

def _ensure_data_dir() -> None:
    """Create the data directory if it does not exist."""
    os.makedirs(DATA_DIR, exist_ok=True)


def _ensure_csv(filepath: str, columns: List[str]) -> None:
    """
    Create a CSV file with the given header if it does not already exist.
    Does NOT overwrite an existing file.
    """
    _ensure_data_dir()
    if not os.path.isfile(filepath):
        with open(filepath, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=columns)
            writer.writeheader()


# ─────────────────────────────────────────────
# Session ID
# ─────────────────────────────────────────────

def generate_session_id() -> str:
    """Return a short unique session identifier."""
    return str(uuid.uuid4())[:8].upper()


# ─────────────────────────────────────────────
# Save operations
# ─────────────────────────────────────────────

def save_trials(
    session_id: str,
    participant_id: str,
    timestamp: str,
    trial_results: List[Dict[str, Any]],
) -> None:
    """
    Append individual trial records to trials.csv.

    Parameters
    ----------
    session_id      : unique session identifier
    participant_id  : participant nickname / ID
    timestamp       : ISO-format session start time
    trial_results   : list of dicts from stroop_test.check_answer(),
                      each must also have 'reaction_time_ms' and 'trial_number'
    """
    _ensure_csv(TRIALS_CSV, TRIAL_COLUMNS)

    with open(TRIALS_CSV, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=TRIAL_COLUMNS, extrasaction="ignore")
        for trial in trial_results:
            row = {
                "session_id":          session_id,
                "participant_id":      participant_id,
                "timestamp":           timestamp,
                "trial_number":        trial.get("trial_number", ""),
                "word":                trial.get("word", ""),
                "ink_colour":          trial.get("ink_colour", ""),
                "condition":           trial.get("condition", ""),
                "correct_answer":      trial.get("correct_answer", ""),
                "participant_answer":  trial.get("participant_answer", ""),
                "is_correct":          trial.get("is_correct", False),
                "reaction_time_ms":    round(trial.get("reaction_time_ms", 0), 2),
            }
            writer.writerow(row)


def save_summary(
    session_id: str,
    participant_id: str,
    timestamp: str,
    summary: Dict[str, Any],
) -> None:
    """
    Append one session-level summary row to summaries.csv.

    Parameters
    ----------
    session_id     : unique session identifier
    participant_id : participant nickname / ID
    timestamp      : ISO-format session start time
    summary        : output of analysis.compute_summary()
    """
    _ensure_csv(SUMMARIES_CSV, SUMMARY_COLUMNS)

    row = {
        "session_id":          session_id,
        "participant_id":      participant_id,
        "timestamp":           timestamp,
        "total_trials":        summary.get("total_trials", 0),
        "correct":             summary.get("correct", 0),
        "incorrect":           summary.get("incorrect", 0),
        "accuracy_pct":        summary.get("accuracy_pct"),
        "error_rate_pct":      summary.get("error_rate_pct"),
        "mean_rt_ms":          summary.get("mean_rt_ms"),
        "mean_rt_correct_ms":  summary.get("mean_rt_correct_ms"),
        "congruent_trials":    summary.get("congruent_trials", 0),
        "congruent_rt_ms":     summary.get("congruent_rt_ms"),
        "congruent_acc_pct":   summary.get("congruent_acc_pct"),
        "incongruent_trials":  summary.get("incongruent_trials", 0),
        "incongruent_rt_ms":   summary.get("incongruent_rt_ms"),
        "incongruent_acc_pct": summary.get("incongruent_acc_pct"),
        "rt_difference_ms":    summary.get("rt_difference_ms"),
    }

    with open(SUMMARIES_CSV, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=SUMMARY_COLUMNS, extrasaction="ignore")
        writer.writerow(row)


# ─────────────────────────────────────────────
# Load operations
# ─────────────────────────────────────────────

def load_all_summaries() -> pd.DataFrame:
    """
    Load summaries.csv and return a DataFrame.
    Returns an empty DataFrame (with correct columns) if the file is missing.
    """
    _ensure_csv(SUMMARIES_CSV, SUMMARY_COLUMNS)
    try:
        df = pd.read_csv(SUMMARIES_CSV, dtype=str)
        if df.empty:
            return pd.DataFrame(columns=SUMMARY_COLUMNS)
        return df
    except pd.errors.EmptyDataError:
        return pd.DataFrame(columns=SUMMARY_COLUMNS)
    except Exception as e:
        print(f"[storage] Warning: could not load summaries – {e}")
        return pd.DataFrame(columns=SUMMARY_COLUMNS)


def load_session_trials(session_id: str) -> pd.DataFrame:
    """
    Load all trial rows for a given session_id from trials.csv.

    Parameters
    ----------
    session_id : str

    Returns
    -------
    pd.DataFrame (may be empty if no trials found).
    """
    _ensure_csv(TRIALS_CSV, TRIAL_COLUMNS)
    try:
        df = pd.read_csv(TRIALS_CSV, dtype=str)
        if df.empty:
            return pd.DataFrame(columns=TRIAL_COLUMNS)
        session_df = df[df["session_id"] == session_id].copy()
        # Convert numeric columns
        for col in ["reaction_time_ms", "trial_number"]:
            if col in session_df.columns:
                session_df[col] = pd.to_numeric(session_df[col], errors="coerce")
        if "is_correct" in session_df.columns:
            session_df["is_correct"] = session_df["is_correct"].map(
                {"True": True, "False": False, True: True, False: False}
            ).fillna(False).astype(bool)
        return session_df
    except pd.errors.EmptyDataError:
        return pd.DataFrame(columns=TRIAL_COLUMNS)
    except Exception as e:
        print(f"[storage] Warning: could not load trials for session {session_id} – {e}")
        return pd.DataFrame(columns=TRIAL_COLUMNS)


def load_all_trials() -> pd.DataFrame:
    """Load the entire trials.csv file."""
    _ensure_csv(TRIALS_CSV, TRIAL_COLUMNS)
    try:
        df = pd.read_csv(TRIALS_CSV, dtype=str)
        if df.empty:
            return pd.DataFrame(columns=TRIAL_COLUMNS)
        for col in ["reaction_time_ms", "trial_number"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        if "is_correct" in df.columns:
            df["is_correct"] = df["is_correct"].map(
                {"True": True, "False": False, True: True, False: False}
            ).fillna(False).astype(bool)
        return df
    except pd.errors.EmptyDataError:
        return pd.DataFrame(columns=TRIAL_COLUMNS)
    except Exception as e:
        print(f"[storage] Warning: could not load all trials – {e}")
        return pd.DataFrame(columns=TRIAL_COLUMNS)


# ─────────────────────────────────────────────
# Utility
# ─────────────────────────────────────────────

def get_current_timestamp() -> str:
    """Return the current date-time as a readable ISO-style string."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_session_list() -> List[Dict[str, str]]:
    """
    Return a list of session metadata dicts for use in selection UI.
    Each dict has: session_id, participant_id, timestamp.
    """
    df = load_all_summaries()
    if df.empty:
        return []
    required = {"session_id", "participant_id", "timestamp"}
    if not required.issubset(df.columns):
        return []
    records = df[["session_id", "participant_id", "timestamp"]].drop_duplicates(
        subset="session_id"
    )
    return records.to_dict(orient="records")


def trials_to_csv_string(trials_df: pd.DataFrame) -> str:
    """Convert a trials DataFrame to a CSV string for download."""
    return trials_df.to_csv(index=False)


def summary_to_csv_string(summary: Dict[str, Any], session_id: str, participant_id: str, timestamp: str) -> str:
    """Convert a summary dict to a one-row CSV string for download."""
    row = {
        "session_id": session_id,
        "participant_id": participant_id,
        "timestamp": timestamp,
        **summary,
    }
    df = pd.DataFrame([row])
    return df.to_csv(index=False)
