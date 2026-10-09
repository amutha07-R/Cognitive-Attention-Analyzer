"""
tests/test_modules.py
---------------------
Automated tests for the core src modules.
Covers: trial generation, answer checking, RT calculation, analysis, and storage.

Run from the project root:
    python -m pytest tests/ -v
"""

import sys
import os
import io
import tempfile
import shutil

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pandas as pd
import pytest

from src.stroop_test import (
    generate_trial,
    generate_trial_sequence,
    check_answer,
    compute_reaction_time_ms,
    build_stimulus_html,
    COLOURS,
    COLOUR_HEX,
)
from src.analysis import (
    compute_summary,
    generate_interpretation,
    compare_sessions,
)


# ─────────────────────────────────────────────
# stroop_test.py tests
# ─────────────────────────────────────────────

class TestGenerateTrial:
    def test_congruent_word_matches_ink(self):
        for _ in range(20):
            t = generate_trial("congruent")
            assert t["word"] == t["ink_colour"], "Congruent trial must have matching word and ink"

    def test_congruent_correct_answer_is_ink(self):
        for _ in range(20):
            t = generate_trial("congruent")
            assert t["correct_answer"] == t["ink_colour"]

    def test_congruent_condition_label(self):
        t = generate_trial("congruent")
        assert t["condition"] == "congruent"

    def test_incongruent_word_differs_from_ink(self):
        for _ in range(50):
            t = generate_trial("incongruent")
            assert t["word"] != t["ink_colour"], "Incongruent trial must NOT match word and ink"

    def test_incongruent_correct_answer_is_ink(self):
        for _ in range(20):
            t = generate_trial("incongruent")
            assert t["correct_answer"] == t["ink_colour"]

    def test_incongruent_condition_label(self):
        t = generate_trial("incongruent")
        assert t["condition"] == "incongruent"

    def test_colours_valid(self):
        for _ in range(20):
            t = generate_trial("congruent")
            assert t["word"] in COLOURS
            assert t["ink_colour"] in COLOURS


class TestGenerateTrialSequence:
    def test_total_length_even(self):
        seq = generate_trial_sequence(20)
        assert len(seq) == 20

    def test_total_length_odd(self):
        seq = generate_trial_sequence(11)
        assert len(seq) == 11

    def test_balanced_even(self):
        seq = generate_trial_sequence(20)
        cong   = sum(1 for t in seq if t["condition"] == "congruent")
        incong = sum(1 for t in seq if t["condition"] == "incongruent")
        assert cong == 10
        assert incong == 10

    def test_balanced_odd(self):
        seq = generate_trial_sequence(11)
        cong   = sum(1 for t in seq if t["condition"] == "congruent")
        incong = sum(1 for t in seq if t["condition"] == "incongruent")
        assert cong + incong == 11
        assert incong == cong + 1  # extra goes to incongruent

    def test_minimum_trials(self):
        seq = generate_trial_sequence(2)
        assert len(seq) == 2


class TestCheckAnswer:
    def _make_trial(self, condition="congruent", word="Red", ink="Red"):
        return {
            "word": word,
            "ink_colour": ink,
            "condition": condition,
            "correct_answer": ink,
        }

    def test_correct_answer(self):
        trial = self._make_trial(ink="Green")
        result = check_answer(trial, "Green")
        assert result["is_correct"] is True

    def test_incorrect_answer(self):
        trial = self._make_trial(word="Green", ink="Red", condition="incongruent")
        result = check_answer(trial, "Green")  # read word, not ink
        assert result["is_correct"] is False

    def test_result_has_required_keys(self):
        trial = self._make_trial()
        result = check_answer(trial, "Red")
        for key in ["word", "ink_colour", "condition", "correct_answer", "participant_answer", "is_correct"]:
            assert key in result

    def test_case_insensitive(self):
        trial = self._make_trial(ink="Blue")
        result = check_answer(trial, "blue")
        assert result["is_correct"] is True


class TestReactionTime:
    def test_normal_rt(self):
        rt = compute_reaction_time_ms(1000.0, 1650.5)
        assert abs(rt - 650.5) < 0.01

    def test_zero_rt(self):
        rt = compute_reaction_time_ms(500.0, 500.0)
        assert rt == 0.0

    def test_negative_rt_clamped(self):
        # Should return 0 if end < start (clock error)
        rt = compute_reaction_time_ms(1000.0, 500.0)
        assert rt == 0.0


class TestBuildStimulusHTML:
    def test_contains_word_uppercase(self):
        trial = {"word": "blue", "ink_colour": "Red"}
        html = build_stimulus_html(trial)
        assert "BLUE" in html

    def test_contains_ink_hex(self):
        trial = {"word": "Green", "ink_colour": "Red"}
        html = build_stimulus_html(trial)
        assert COLOUR_HEX["Red"] in html

    def test_returns_string(self):
        trial = {"word": "Yellow", "ink_colour": "Blue"}
        html = build_stimulus_html(trial)
        assert isinstance(html, str)


# ─────────────────────────────────────────────
# analysis.py tests
# ─────────────────────────────────────────────

def _make_trials_df(rows):
    """Helper to build a trial DataFrame from a list of tuples (condition, is_correct, rt_ms)."""
    data = [
        {"condition": c, "is_correct": ok, "reaction_time_ms": rt}
        for c, ok, rt in rows
    ]
    return pd.DataFrame(data)


class TestComputeSummary:
    def test_empty_df(self):
        result = compute_summary(pd.DataFrame())
        assert result["total_trials"] == 0

    def test_basic_counts(self):
        df = _make_trials_df([
            ("congruent",   True,  400),
            ("congruent",   True,  350),
            ("incongruent", True,  600),
            ("incongruent", False, 800),
        ])
        s = compute_summary(df)
        assert s["total_trials"] == 4
        assert s["correct"] == 3
        assert s["incorrect"] == 1

    def test_accuracy(self):
        df = _make_trials_df([
            ("congruent",   True,  400),
            ("incongruent", False, 600),
        ])
        s = compute_summary(df)
        assert s["accuracy_pct"] == 50.0
        assert s["error_rate_pct"] == 50.0

    def test_congruent_rt(self):
        df = _make_trials_df([
            ("congruent", True, 400),
            ("congruent", True, 600),
        ])
        s = compute_summary(df)
        assert s["congruent_rt_ms"] == 500.0

    def test_incongruent_rt(self):
        df = _make_trials_df([
            ("incongruent", True, 700),
            ("incongruent", True, 900),
        ])
        s = compute_summary(df)
        assert s["incongruent_rt_ms"] == 800.0

    def test_rt_difference(self):
        df = _make_trials_df([
            ("congruent",   True, 400),
            ("incongruent", True, 700),
        ])
        s = compute_summary(df)
        assert s["rt_difference_ms"] == 300.0

    def test_missing_condition_returns_none(self):
        df = _make_trials_df([
            ("congruent", True, 400),
            ("congruent", True, 500),
        ])
        s = compute_summary(df)
        # No incongruent rows
        assert s["incongruent_rt_ms"] is None
        assert s["rt_difference_ms"] is None

    def test_congruent_accuracy(self):
        df = _make_trials_df([
            ("congruent", True,  400),
            ("congruent", False, 500),
        ])
        s = compute_summary(df)
        assert s["congruent_acc_pct"] == 50.0


class TestGenerateInterpretation:
    def _summary(self, **kwargs):
        base = {
            "total_trials": 20,
            "correct": 16,
            "accuracy_pct": 80.0,
            "error_rate_pct": 20.0,
            "mean_rt_ms": 500.0,
            "congruent_rt_ms": 400.0,
            "incongruent_rt_ms": 650.0,
            "rt_difference_ms": 250.0,
            "congruent_acc_pct": 90.0,
            "incongruent_acc_pct": 70.0,
            "congruent_trials": 10,
            "incongruent_trials": 10,
            "mean_rt_correct_ms": 480.0,
        }
        base.update(kwargs)
        return base

    def test_returns_string(self):
        result = generate_interpretation(self._summary())
        assert isinstance(result, str)

    def test_positive_rt_diff_mentions_interference(self):
        result = generate_interpretation(self._summary(rt_difference_ms=250.0))
        assert "interference" in result.lower() or "stroop" in result.lower()

    def test_contains_disclaimer(self):
        result = generate_interpretation(self._summary())
        assert "not a clinical" in result.lower() or "clinical" in result.lower()

    def test_no_diagnosis_claim(self):
        result = generate_interpretation(self._summary())
        lower = result.lower()
        assert "adhd" not in lower
        assert "disorder" not in lower or "attention" not in lower

    def test_empty_returns_message(self):
        result = generate_interpretation({"total_trials": 0})
        assert "no trial" in result.lower()


class TestCompareSessions:
    def test_returns_dataframe(self):
        summaries = [
            {"participant_id": "A", "session_id": "S1", "timestamp": "2024-01-01", "accuracy_pct": 80},
            {"participant_id": "B", "session_id": "S2", "timestamp": "2024-01-02", "accuracy_pct": 75},
        ]
        df = compare_sessions(summaries)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2

    def test_empty_input(self):
        df = compare_sessions([])
        assert df.empty


# ─────────────────────────────────────────────
# storage.py tests
# ─────────────────────────────────────────────

class TestStorage:
    """
    Storage tests use a temporary directory to avoid touching real data files.
    The storage module's DATA_DIR and CSV paths are monkey-patched.
    """

    def setup_method(self):
        """Create a temporary directory before each test."""
        self.tmp_dir = tempfile.mkdtemp()
        import src.storage as storage
        self._orig_data_dir      = storage.DATA_DIR
        self._orig_trials_csv    = storage.TRIALS_CSV
        self._orig_summaries_csv = storage.SUMMARIES_CSV
        storage.DATA_DIR      = self.tmp_dir
        storage.TRIALS_CSV    = os.path.join(self.tmp_dir, "trials.csv")
        storage.SUMMARIES_CSV = os.path.join(self.tmp_dir, "summaries.csv")

    def teardown_method(self):
        """Remove temporary directory and restore paths."""
        import src.storage as storage
        storage.DATA_DIR      = self._orig_data_dir
        storage.TRIALS_CSV    = self._orig_trials_csv
        storage.SUMMARIES_CSV = self._orig_summaries_csv
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def _sample_trials(self, n=3):
        return [
            {
                "trial_number": i + 1,
                "word": "Red",
                "ink_colour": "Blue",
                "condition": "incongruent",
                "correct_answer": "Blue",
                "participant_answer": "Blue",
                "is_correct": True,
                "reaction_time_ms": 500.0 + i * 50,
            }
            for i in range(n)
        ]

    def _sample_summary(self):
        return {
            "total_trials": 3,
            "correct": 3,
            "incorrect": 0,
            "accuracy_pct": 100.0,
            "error_rate_pct": 0.0,
            "mean_rt_ms": 550.0,
            "mean_rt_correct_ms": 550.0,
            "congruent_trials": 0,
            "congruent_rt_ms": None,
            "congruent_acc_pct": None,
            "incongruent_trials": 3,
            "incongruent_rt_ms": 550.0,
            "incongruent_acc_pct": 100.0,
            "rt_difference_ms": None,
        }

    def test_save_and_load_trials(self):
        from src.storage import save_trials, load_session_trials
        save_trials("S1", "TestUser", "2024-01-01 10:00:00", self._sample_trials(3))
        df = load_session_trials("S1")
        assert len(df) == 3
        assert all(df["session_id"] == "S1")

    def test_append_does_not_overwrite(self):
        from src.storage import save_trials, load_all_trials
        save_trials("S1", "User1", "2024-01-01 10:00:00", self._sample_trials(2))
        save_trials("S2", "User2", "2024-01-01 11:00:00", self._sample_trials(3))
        df = load_all_trials()
        assert len(df) == 5

    def test_load_missing_trials_returns_empty(self):
        from src.storage import load_session_trials
        df = load_session_trials("NONEXISTENT")
        assert df.empty

    def test_save_and_load_summaries(self):
        from src.storage import save_summary, load_all_summaries
        save_summary("S1", "TestUser", "2024-01-01 10:00:00", self._sample_summary())
        df = load_all_summaries()
        assert len(df) == 1
        assert df.iloc[0]["session_id"] == "S1"

    def test_load_missing_summaries_returns_empty(self):
        from src.storage import load_all_summaries
        df = load_all_summaries()
        assert df.empty

    def test_generate_session_id_unique(self):
        from src.storage import generate_session_id
        ids = {generate_session_id() for _ in range(100)}
        assert len(ids) == 100  # all unique


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
