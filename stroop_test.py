"""
stroop_test.py
--------------
Core Stroop test logic.
Handles trial generation, state management, and answer checking.

The Stroop Effect (1935):
    Reading words is an automatic process for literate adults.
    Identifying ink colour requires controlled attention.
    When word meaning and ink colour conflict (incongruent), the brain
    experiences cognitive interference, typically causing slower responses
    and more errors.
"""

import random
import time
from typing import List, Dict, Any


# ─────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────

COLOURS: List[str] = ["Red", "Green", "Blue", "Yellow"]

# Hex codes used when rendering coloured text in Streamlit HTML
COLOUR_HEX: Dict[str, str] = {
    "Red":    "#E74C3C",
    "Green":  "#27AE60",
    "Blue":   "#2980B9",
    "Yellow": "#F1C40F",
}

# Display text for each colour (same as the colour name here)
COLOUR_WORDS: List[str] = ["Red", "Green", "Blue", "Yellow"]


# ─────────────────────────────────────────────
# Trial generation
# ─────────────────────────────────────────────

def generate_trial(condition: str) -> Dict[str, Any]:
    """
    Create a single Stroop trial.

    Parameters
    ----------
    condition : str
        'congruent'   – ink colour matches word meaning
        'incongruent' – ink colour differs from word meaning

    Returns
    -------
    dict with keys: word, ink_colour, condition, correct_answer
    """
    if condition == "congruent":
        colour = random.choice(COLOURS)
        return {
            "word":           colour,
            "ink_colour":     colour,
            "condition":      "congruent",
            "correct_answer": colour,
        }
    else:
        word = random.choice(COLOURS)
        # Pick an ink colour that is definitely NOT the word
        remaining = [c for c in COLOURS if c != word]
        ink = random.choice(remaining)
        return {
            "word":           word,
            "ink_colour":     ink,
            "condition":      "incongruent",
            "correct_answer": ink,
        }


def generate_trial_sequence(total_trials: int = 20) -> List[Dict[str, Any]]:
    """
    Create a balanced, randomised list of trials.

    Half the trials are congruent, half incongruent.
    If total_trials is odd, one extra incongruent trial is added.

    Parameters
    ----------
    total_trials : int
        Total number of trials in the sequence.

    Returns
    -------
    List of trial dicts (shuffled).
    """
    half = total_trials // 2
    remainder = total_trials % 2  # 0 or 1

    trials = []
    for _ in range(half):
        trials.append(generate_trial("congruent"))
    for _ in range(half + remainder):
        trials.append(generate_trial("incongruent"))

    random.shuffle(trials)
    return trials


# ─────────────────────────────────────────────
# Answer checking
# ─────────────────────────────────────────────

def check_answer(trial: Dict[str, Any], participant_answer: str) -> Dict[str, Any]:
    """
    Evaluate a participant's response to a trial.

    Parameters
    ----------
    trial             : dict – the current trial dict
    participant_answer: str  – colour name chosen by the participant

    Returns
    -------
    dict with result metadata ready for storage.
    """
    is_correct = participant_answer.strip().lower() == trial["correct_answer"].strip().lower()

    return {
        "word":               trial["word"],
        "ink_colour":         trial["ink_colour"],
        "condition":          trial["condition"],
        "correct_answer":     trial["correct_answer"],
        "participant_answer": participant_answer,
        "is_correct":         is_correct,
    }


# ─────────────────────────────────────────────
# Timer helpers
# ─────────────────────────────────────────────

def get_current_time_ms() -> float:
    """Return current Unix time in milliseconds."""
    return time.time() * 1000.0


def compute_reaction_time_ms(start_ms: float, end_ms: float) -> float:
    """
    Compute reaction time in milliseconds.

    Parameters
    ----------
    start_ms : float – timestamp when the trial was displayed (ms)
    end_ms   : float – timestamp when the participant clicked (ms)

    Returns
    -------
    Reaction time in milliseconds (non-negative).
    """
    rt = end_ms - start_ms
    return max(0.0, rt)


# ─────────────────────────────────────────────
# HTML stimulus builder
# ─────────────────────────────────────────────

def build_stimulus_html(trial: Dict[str, Any], font_size: int = 72) -> str:
    """
    Return an HTML string that renders the Stroop word in its ink colour.

    Parameters
    ----------
    trial     : dict – trial dict with 'word' and 'ink_colour'
    font_size : int  – font size in pixels

    Returns
    -------
    HTML string for use with st.markdown(…, unsafe_allow_html=True)
    """
    hex_colour = COLOUR_HEX.get(trial["ink_colour"], "#FFFFFF")
    word = trial["word"].upper()

    html = (
        f'<div style="'
        f'text-align:center;'
        f'font-size:{font_size}px;'
        f'font-weight:900;'
        f'color:{hex_colour};'
        f'letter-spacing:6px;'
        f'text-shadow: 0 2px 12px rgba(0,0,0,0.4);'
        f'padding: 30px 0;'
        f'">{word}</div>'
    )
    return html
