"""
app.py
------
Main Streamlit application for the Cognitive Attention and Reaction Time Analyzer.

Run from the project root:
    streamlit run app.py

Pages:
    🏠 Home         – Introduction and navigation
    👤 Participant  – Enter participant ID and read instructions
    🧠 Stroop Test  – Interactive Stroop colour-word test
    📊 My Results   – Results and visualizations for the current session
    📁 All Results  – Browse and compare all saved sessions
"""

import sys
import os

# Make the src package importable from the project root
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
import pandas as pd

from src.stroop_test import (
    generate_trial_sequence,
    check_answer,
    build_stimulus_html,
    get_current_time_ms,
    compute_reaction_time_ms,
    COLOURS,
    COLOUR_HEX,
)
from src.analysis import compute_summary, generate_interpretation, compare_sessions
from src.storage import (
    generate_session_id,
    save_trials,
    save_summary,
    load_all_summaries,
    load_session_trials,
    get_session_list,
    trials_to_csv_string,
    summary_to_csv_string,
    get_current_timestamp,
)
from src.visualization import (
    plot_rt_comparison,
    plot_accuracy_comparison,
    plot_trial_by_trial_rt,
    plot_session_comparison,
)


# ─────────────────────────────────────────────────────────────────────────────
# Streamlit global configuration
# ─────────────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Cognitive Attention Analyzer",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ─────────────────────────────────────────────────────────────────────────────
# Custom CSS – dark premium academic design
# ─────────────────────────────────────────────────────────────────────────────

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;900&display=swap');

:root {
    --bg-primary:   #0F0F23;
    --bg-secondary: #1A1A2E;
    --bg-card:      #16213E;
    --bg-card2:     #1a2744;
    --accent-blue:  #4A90E2;
    --accent-green: #27AE60;
    --accent-red:   #E74C3C;
    --accent-yellow:#F1C40F;
    --accent-purple:#9B59B6;
    --text-primary: #E8ECF4;
    --text-secondary:#A8B2C8;
    --border:       #2C3E6B;
    --border-glow:  rgba(74,144,226,0.3);
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* ── Page background ── */
.stApp {
    background: linear-gradient(135deg, #0F0F23 0%, #1A1A2E 50%, #0D1B3E 100%);
    color: var(--text-primary);
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1A1A2E 0%, #16213E 100%);
    border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] .stRadio label {
    color: var(--text-primary) !important;
    font-size: 0.95rem;
}

/* ── Hero banner ── */
.hero-banner {
    background: linear-gradient(135deg, #1A1A2E 0%, #16213E 40%, #0D1B3E 100%);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 3rem 2.5rem 2.5rem;
    text-align: center;
    margin-bottom: 2rem;
    box-shadow: 0 8px 40px rgba(74,144,226,0.12);
    position: relative;
    overflow: hidden;
}
.hero-banner::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle at 30% 30%, rgba(74,144,226,0.07) 0%, transparent 60%);
    pointer-events: none;
}
.hero-title {
    font-size: 2.6rem;
    font-weight: 900;
    background: linear-gradient(135deg, #4A90E2, #A29BFE, #74B9FF);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.5rem;
    line-height: 1.2;
}
.hero-subtitle {
    font-size: 1.1rem;
    color: var(--text-secondary);
    margin-bottom: 1.5rem;
    font-weight: 400;
}
.hero-badge {
    display: inline-block;
    background: rgba(74,144,226,0.12);
    border: 1px solid rgba(74,144,226,0.3);
    border-radius: 20px;
    padding: 0.3rem 1rem;
    font-size: 0.82rem;
    color: #74B9FF;
    margin: 0.2rem;
}

/* ── Cards ── */
.card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1.2rem;
    box-shadow: 0 4px 20px rgba(0,0,0,0.25);
    transition: border-color 0.25s;
}
.card:hover {
    border-color: var(--border-glow);
}
.card-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--accent-blue);
    margin-bottom: 0.6rem;
}

/* ── Section headers ── */
.section-header {
    font-size: 1.4rem;
    font-weight: 700;
    color: var(--text-primary);
    border-bottom: 2px solid var(--border);
    padding-bottom: 0.5rem;
    margin: 1.5rem 0 1rem;
}

/* ── Concept chips ── */
.concept-chip {
    display: inline-block;
    background: rgba(155,89,182,0.15);
    border: 1px solid rgba(155,89,182,0.35);
    border-radius: 6px;
    padding: 0.3rem 0.8rem;
    margin: 0.2rem;
    font-size: 0.85rem;
    color: #C39BD3;
}

/* ── Stroop stimulus area ── */
.stroop-box {
    background: var(--bg-card);
    border: 2px solid var(--border);
    border-radius: 16px;
    padding: 2rem 1rem;
    text-align: center;
    margin: 1rem 0;
    box-shadow: 0 0 30px rgba(74,144,226,0.08);
    min-height: 170px;
    display: flex;
    align-items: center;
    justify-content: center;
}

/* ── Progress bar ── */
.progress-track {
    background: var(--bg-card);
    border-radius: 8px;
    height: 10px;
    overflow: hidden;
    border: 1px solid var(--border);
    margin: 0.5rem 0;
}
.progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #4A90E2, #A29BFE);
    border-radius: 8px;
    transition: width 0.4s ease;
}

/* ── Stroop response buttons ── */
.stButton > button {
    border-radius: 10px !important;
    font-weight: 700 !important;
    font-size: 1.05rem !important;
    letter-spacing: 1px !important;
    padding: 0.65rem 1.2rem !important;
    transition: all 0.2s ease !important;
    border: 2px solid transparent !important;
}
.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0,0,0,0.4) !important;
}

/* ── Info / warning boxes ── */
.info-box {
    background: rgba(74,144,226,0.08);
    border-left: 4px solid var(--accent-blue);
    border-radius: 0 8px 8px 0;
    padding: 1rem 1.2rem;
    margin: 0.8rem 0;
    color: var(--text-primary);
    font-size: 0.95rem;
}
.warning-box {
    background: rgba(241,196,15,0.08);
    border-left: 4px solid var(--accent-yellow);
    border-radius: 0 8px 8px 0;
    padding: 1rem 1.2rem;
    margin: 0.8rem 0;
    color: var(--text-primary);
    font-size: 0.95rem;
}
.success-box {
    background: rgba(39,174,96,0.1);
    border-left: 4px solid var(--accent-green);
    border-radius: 0 8px 8px 0;
    padding: 1rem 1.2rem;
    margin: 0.8rem 0;
    color: var(--text-primary);
    font-size: 0.95rem;
}

/* ── Metric cards ── */
[data-testid="stMetric"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    padding: 0.8rem 1rem !important;
}
[data-testid="stMetricValue"] {
    font-size: 1.6rem !important;
    font-weight: 700 !important;
    color: var(--accent-blue) !important;
}
[data-testid="stMetricLabel"] {
    color: var(--text-secondary) !important;
    font-size: 0.82rem !important;
}

/* ── DataFrames ── */
[data-testid="stDataFrame"] {
    border-radius: 10px !important;
    overflow: hidden !important;
}

/* ── Dividers ── */
hr {
    border-color: var(--border) !important;
}

/* ── Footer ── */
.footer {
    text-align: center;
    color: var(--text-secondary);
    font-size: 0.8rem;
    padding: 2rem 0 1rem;
    border-top: 1px solid var(--border);
    margin-top: 3rem;
}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Session-state initialisation
# ─────────────────────────────────────────────────────────────────────────────

def _init_state():
    defaults = {
        "page":             "home",
        "participant_id":   "",
        "session_id":       None,
        "session_ts":       None,
        "trials":           [],          # list of trial dicts
        "trial_index":      0,
        "trial_results":    [],          # list of result dicts
        "trial_start_ms":   None,
        "test_complete":    False,
        "results_saved":    False,
        "summary":          None,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

_init_state()


# ─────────────────────────────────────────────────────────────────────────────
# Sidebar navigation
# ─────────────────────────────────────────────────────────────────────────────

def render_sidebar():
    with st.sidebar:
        st.markdown(
            "<h2 style='color:#4A90E2;font-size:1.3rem;margin-bottom:0;'>🧠 Cognitive Analyzer</h2>"
            "<p style='color:#A8B2C8;font-size:0.78rem;margin-top:0.2rem;'>Stroop Test · Reaction Time</p>",
            unsafe_allow_html=True,
        )
        st.divider()

        pages = {
            "home":        "🏠  Home",
            "participant": "👤  Participant Setup",
            "test":        "🧪  Stroop Test",
            "results":     "📊  My Results",
            "all_results": "📁  All Sessions",
        }

        for key, label in pages.items():
            is_active = st.session_state["page"] == key
            if st.button(
                label,
                key=f"nav_{key}",
                use_container_width=True,
                type="primary" if is_active else "secondary",
            ):
                st.session_state["page"] = key
                st.rerun()

        st.divider()

        if st.session_state.get("participant_id"):
            st.markdown(
                f"<div style='color:#A8B2C8;font-size:0.82rem;'>"
                f"👤 <b style='color:#E8ECF4;'>{st.session_state['participant_id']}</b><br/>"
                f"🔖 Session: <b style='color:#74B9FF;'>{st.session_state.get('session_id','—')}</b>"
                f"</div>",
                unsafe_allow_html=True,
            )
            st.divider()

        st.markdown(
            "<div style='color:#5D6D7E;font-size:0.75rem;'>"
            "B.Tech AI & DS Mini Project<br/>Cognitive Science · Stroop (1935)"
            "</div>",
            unsafe_allow_html=True,
        )


# ─────────────────────────────────────────────────────────────────────────────
# Page: Home
# ─────────────────────────────────────────────────────────────────────────────

def page_home():
    st.markdown("""
    <div class="hero-banner">
        <div class="hero-title">🧠 Cognitive Attention &amp;<br/>Reaction Time Analyzer</div>
        <div class="hero-subtitle">
            An interactive Stroop Colour-Word Test to study selective attention<br/>
            and cognitive interference in human response
        </div>
        <div>
            <span class="hero-badge">🎓 B.Tech AI &amp; DS Mini Project</span>
            <span class="hero-badge">🧪 Stroop Effect (1935)</span>
            <span class="hero-badge">📊 Cognitive Science</span>
            <span class="hero-badge">⚡ Reaction Time Analysis</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Concept cards ──────────────────────────────────────────────────────
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="card">
            <div class="card-title">🔍 Cognitive Attention</div>
            <p style="color:#A8B2C8;font-size:0.9rem;">
                Cognitive attention is the mental process of selectively focusing on
                specific information while ignoring other stimuli.  When you read this
                sentence, you attend to it and filter out background noise.
                <br/><br/>
                <b>Selective attention</b> lets us choose what to process.  The Stroop
                test challenges selective attention by creating a conflict between two
                pieces of information: the word you read and the colour you see.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="card">
            <div class="card-title">⏱ Reaction Time</div>
            <p style="color:#A8B2C8;font-size:0.9rem;">
                Reaction time (RT) is the duration between the appearance of a stimulus
                and the start of a person's response.  It is measured in milliseconds
                (ms) and reflects how quickly the brain processes information and sends
                a motor signal.
                <br/><br/>
                Faster RT generally indicates more efficient information processing for
                that particular task under those specific conditions.  RT is influenced
                by attention, fatigue, practice, and task difficulty.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="card">
            <div class="card-title">🌈 The Stroop Effect</div>
            <p style="color:#A8B2C8;font-size:0.9rem;">
                Described by John Ridley Stroop in 1935, the Stroop effect is the
                observation that people are slower and less accurate when naming the
                <i>ink colour</i> of a colour-word whose meaning conflicts with that colour.
                <br/><br/>
                Example: the word <b style="color:#E74C3C;">BLUE</b> printed in red ink —
                the word triggers the automatic response "blue" while the task requires
                you to say "red", causing <b>cognitive interference</b>.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # ── How the experiment works ────────────────────────────────────────────
    st.markdown('<div class="section-header">⚙️ How the Experiment Works</div>', unsafe_allow_html=True)

    col_a, col_b = st.columns([3, 2])
    with col_a:
        st.markdown("""
        <div class="card">
            <ol style="color:#A8B2C8;font-size:0.93rem;line-height:1.9;">
                <li>You enter a participant ID (nickname only – no personal data collected).</li>
                <li>You read the test instructions carefully.</li>
                <li>The test presents <b style="color:#E8ECF4;">20 trials</b> (configurable) one at a time.
                    Each trial shows a colour word (e.g., "GREEN") printed in an ink colour
                    that may or may not match the word.</li>
                <li>Your task is to <b style="color:#4A90E2;">identify the INK COLOUR</b> — not read the word —
                    by clicking one of four colour buttons: Red, Green, Blue, or Yellow.</li>
                <li>Your answer and the time you took to respond are recorded automatically.</li>
                <li>After all trials, the app calculates your accuracy and reaction times
                    and displays a full analysis with charts.</li>
                <li>Results are saved to a CSV file automatically.</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)

    with col_b:
        st.markdown("""
        <div class="card">
            <div class="card-title">📐 Trial Types</div>
            <div style="margin-bottom:0.8rem;">
                <span style="color:#27AE60;font-weight:700;">● Congruent</span>
                <p style="color:#A8B2C8;font-size:0.88rem;margin:0.2rem 0 0.8rem 1rem;">
                    Word meaning = ink colour<br/>
                    e.g., <b style="color:#27AE60;">GREEN</b> in green ink<br/>
                    Usually faster and more accurate
                </p>
            </div>
            <div>
                <span style="color:#E74C3C;font-weight:700;">● Incongruent</span>
                <p style="color:#A8B2C8;font-size:0.88rem;margin:0.2rem 0 0 1rem;">
                    Word meaning ≠ ink colour<br/>
                    e.g., <span style="color:#E74C3C;font-weight:700;">GREEN</span> in red ink<br/>
                    Usually slower – Stroop interference!
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="card">
            <div class="card-title">⚠️ Important Notice</div>
            <p style="color:#A8B2C8;font-size:0.88rem;">
                This is an <b>academic experiment</b> for educational purposes only.
                It <b>does not</b> diagnose any psychological condition, measure
                intelligence, or assess attention disorders.
                Results describe task performance on this specific test only.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # ── Cognitive Science concepts ────────────────────────────────────────
    st.markdown('<div class="section-header">🔬 Cognitive Science Concepts</div>', unsafe_allow_html=True)

    concepts = [
        ("🧠 Cognitive Science", "The interdisciplinary study of the mind and its processes, including perception, attention, memory, language, and problem-solving."),
        ("👁 Selective Attention", "The ability to focus on one stimulus or task while ignoring others.  Reading word names competes with colour identification in the Stroop task."),
        ("⚡ Cognitive Interference", "When two competing cognitive processes (word reading and colour naming) conflict, slowing down response and increasing errors."),
        ("📏 Reaction Time (RT)", "Time from stimulus onset to participant response, measured in milliseconds.  A key index of cognitive processing speed."),
        ("🔵 Congruent Stimulus", "Word meaning matches ink colour.  No conflict; typically easier and faster."),
        ("🔴 Incongruent Stimulus", "Word meaning mismatches ink colour.  Conflict creates interference; typically harder."),
        ("📊 Descriptive Statistics", "Mean, accuracy, and error rate used here are descriptive – they describe this sample only and are not generalisable without controlled replication."),
        ("⚖️ Limitations", "Single session, unknown individual differences, screen/mouse latency, practice effects within session, no control for fatigue or distractions."),
    ]

    cols = st.columns(2)
    for i, (title, desc) in enumerate(concepts):
        with cols[i % 2]:
            st.markdown(f"""
            <div class="card">
                <div class="card-title">{title}</div>
                <p style="color:#A8B2C8;font-size:0.88rem;">{desc}</p>
            </div>
            """, unsafe_allow_html=True)

    st.divider()

    # ── CTA buttons ───────────────────────────────────────────────────────
    st.markdown('<div style="text-align:center;margin:1.5rem 0;">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        if st.button("🚀 Start Test", type="primary", use_container_width=True, key="home_start"):
            st.session_state["page"] = "participant"
            st.rerun()
    with c2:
        if st.button("📊 View All Results", type="secondary", use_container_width=True, key="home_results"):
            st.session_state["page"] = "all_results"
            st.rerun()
    with c3:
        if st.button("📖 Instructions", type="secondary", use_container_width=True, key="home_instructions"):
            st.session_state["page"] = "participant"
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(
        "<div class='footer'>Cognitive Attention &amp; Reaction Time Analyzer · "
        "B.Tech AI &amp; DS Mini Project · Stroop (1935)</div>",
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Page: Participant Setup
# ─────────────────────────────────────────────────────────────────────────────

def page_participant():
    st.markdown(
        "<h1 style='color:#4A90E2;font-size:2rem;'>👤 Participant Setup</h1>",
        unsafe_allow_html=True,
    )

    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.markdown("""
        <div class="card">
            <div class="card-title">📋 Test Instructions</div>
            <ol style="color:#A8B2C8;font-size:0.93rem;line-height:2.0;">
                <li>Ensure you are in a <b>quiet environment</b> with minimal distractions.</li>
                <li>The test will present <b>colour words</b> printed in different ink colours.</li>
                <li><b style="color:#F1C40F;">Your task:</b> Identify the <b>INK COLOUR</b> of the word — 
                    <u>not the meaning of the word itself</u>.</li>
                <li>Click one of the four colour buttons: 
                    <b style="color:#E74C3C;">Red</b>, 
                    <b style="color:#27AE60;">Green</b>, 
                    <b style="color:#4A90E2;">Blue</b>, 
                    <b style="color:#F1C40F;">Yellow</b>.</li>
                <li>Respond as <b>quickly and accurately</b> as possible.</li>
                <li>Your response time is recorded from the moment the word appears.</li>
                <li>There are <b>no trick questions</b> — simply name the ink colour you see.</li>
                <li>Once you click a button for a trial, you <b>cannot change your answer</b>.</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="info-box">
            🔒 <b>Privacy Notice:</b> Only a nickname or ID is collected.
            No real name, contact information, or personal data is required.
            Data is stored locally on this device only.
        </div>
        """, unsafe_allow_html=True)

    with col_right:
        st.markdown("""
        <div class="card">
            <div class="card-title">🔖 Enter Your Details</div>
        """, unsafe_allow_html=True)

        participant_input = st.text_input(
            "Participant Nickname / ID",
            value=st.session_state.get("participant_id", ""),
            placeholder="e.g., Student01 or Alex",
            max_chars=30,
            key="participant_input_field",
        )

        num_trials = st.slider(
            "Number of Trials",
            min_value=10,
            max_value=40,
            value=20,
            step=2,
            help="More trials give more reliable results but take longer.",
        )

        st.markdown("</div>", unsafe_allow_html=True)

        # Example stimulus preview
        st.markdown("""
        <div class="card">
            <div class="card-title">👁 Sample Trial Preview</div>
            <p style="color:#A8B2C8;font-size:0.85rem;">
                In this example, the word is "GREEN" but the ink colour is RED.<br/>
                You should click <b style="color:#E74C3C;">Red</b> — ignore the word!
            </p>
            <div style="text-align:center;font-size:3.5rem;font-weight:900;
                        color:#E74C3C;letter-spacing:4px;padding:10px 0;">
                GREEN
            </div>
            <p style="text-align:center;color:#A8B2C8;font-size:0.8rem;">
                ↑ Correct answer: <b style="color:#E74C3C;">Red</b> (the ink colour)
            </p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("▶ Start Stroop Test", type="primary", use_container_width=True, key="begin_test_btn"):
            pid = participant_input.strip()
            if not pid:
                st.error("⚠️ Please enter a participant nickname or ID before starting.")
            elif len(pid) < 2:
                st.error("⚠️ Participant ID must be at least 2 characters.")
            else:
                # Initialise session
                st.session_state["participant_id"] = pid
                st.session_state["session_id"]     = generate_session_id()
                st.session_state["session_ts"]     = get_current_timestamp()
                st.session_state["trials"]          = generate_trial_sequence(num_trials)
                st.session_state["trial_index"]     = 0
                st.session_state["trial_results"]   = []
                st.session_state["trial_start_ms"]  = None
                st.session_state["test_complete"]   = False
                st.session_state["results_saved"]   = False
                st.session_state["summary"]         = None
                st.session_state["page"]            = "test"
                st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# Page: Stroop Test
# ─────────────────────────────────────────────────────────────────────────────

def page_stroop_test():
    # Guard: must have a session
    if not st.session_state.get("session_id"):
        st.warning("⚠️ No active test session.  Please set up a participant first.")
        if st.button("← Go to Participant Setup", key="test_no_session_btn"):
            st.session_state["page"] = "participant"
            st.rerun()
        return

    trials     = st.session_state["trials"]
    idx        = st.session_state["trial_index"]
    total      = len(trials)
    is_done    = st.session_state["test_complete"]

    # ── Completed screen ───────────────────────────────────────────────────
    if is_done or idx >= total:
        st.session_state["test_complete"] = True
        _save_results_if_needed()

        st.markdown("""
        <div class="hero-banner" style="padding:2.5rem;">
            <div style="font-size:4rem;margin-bottom:0.5rem;">🎉</div>
            <div class="hero-title" style="font-size:2rem;">Test Complete!</div>
            <p style="color:#A8B2C8;">
                All trials finished.  Your results have been saved automatically.
            </p>
        </div>
        """, unsafe_allow_html=True)

        summary = st.session_state.get("summary", {})
        if summary:
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Total Trials",  summary.get("total_trials", 0))
            m2.metric("Correct",       summary.get("correct", 0))
            m3.metric("Accuracy",      f"{summary.get('accuracy_pct', 0)}%")
            m4.metric("Avg RT",        f"{summary.get('mean_rt_ms', '—')} ms")

        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("📊 View Detailed Results", type="primary", use_container_width=True, key="done_view_results"):
                st.session_state["page"] = "results"
                st.rerun()
        with col_b:
            if st.button("🔄 Start New Test", type="secondary", use_container_width=True, key="done_new_test"):
                _reset_test()
                st.session_state["page"] = "participant"
                st.rerun()
        return

    # ── Active trial ───────────────────────────────────────────────────────
    current_trial = trials[idx]

    # Set timer when trial starts
    if st.session_state["trial_start_ms"] is None:
        st.session_state["trial_start_ms"] = get_current_time_ms()

    # Header
    st.markdown(
        "<h1 style='color:#4A90E2;font-size:1.8rem;margin-bottom:0.5rem;'>🧪 Stroop Test</h1>",
        unsafe_allow_html=True,
    )

    # Progress bar
    pct = idx / total
    st.markdown(
        f"<div style='color:#A8B2C8;font-size:0.9rem;margin-bottom:4px;'>"
        f"Trial <b style='color:#E8ECF4;'>{idx + 1}</b> of <b style='color:#E8ECF4;'>{total}</b>"
        f"&nbsp;&nbsp;|&nbsp;&nbsp;"
        f"Participant: <b style='color:#74B9FF;'>{st.session_state['participant_id']}</b>"
        f"&nbsp;&nbsp;|&nbsp;&nbsp;"
        f"Session: <b style='color:#74B9FF;'>{st.session_state['session_id']}</b>"
        f"</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<div class='progress-track'>"
        f"<div class='progress-fill' style='width:{pct*100:.1f}%;'></div>"
        f"</div>",
        unsafe_allow_html=True,
    )
    st.markdown(f"<p style='color:#5D6D7E;font-size:0.78rem;'>Progress: {pct*100:.0f}%</p>",
                unsafe_allow_html=True)

    st.divider()

    # Instruction reminder
    st.markdown("""
    <div class="warning-box">
        👆 <b>Click the button that matches the INK COLOUR</b> of the word below.
        Do <u>not</u> read the word — identify its colour!
    </div>
    """, unsafe_allow_html=True)

    # Stimulus
    st.markdown(build_stimulus_html(current_trial, font_size=80), unsafe_allow_html=True)

    st.divider()

    # Condition badge (shown after trial for educational value)
    # We reveal it only in the results; during test we keep it hidden to avoid bias

    # Response buttons – 2×2 grid
    button_colours = {
        "Red":    ("#E74C3C", "#FDECEA"),
        "Green":  ("#27AE60", "#E8F8F0"),
        "Blue":   ("#2980B9", "#EAF3FB"),
        "Yellow": ("#D4AC0D", "#FEF9E7"),
    }

    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)

    answer_cols = [col1, col2, col3, col4]
    colours_order = ["Red", "Green", "Blue", "Yellow"]

    answer_given = None
    for col, colour in zip(answer_cols, colours_order):
        hex_c, _ = button_colours[colour]
        with col:
            if st.button(
                colour,
                key=f"answer_{colour}_{idx}",
                use_container_width=True,
            ):
                answer_given = colour

    # Process answer
    if answer_given is not None:
        end_ms = get_current_time_ms()
        start_ms = st.session_state["trial_start_ms"] or end_ms
        rt_ms = compute_reaction_time_ms(start_ms, end_ms)

        result = check_answer(current_trial, answer_given)
        result["reaction_time_ms"] = rt_ms
        result["trial_number"]     = idx + 1

        st.session_state["trial_results"].append(result)
        st.session_state["trial_index"]    = idx + 1
        st.session_state["trial_start_ms"] = None  # reset for next trial

        st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# Page: My Results
# ─────────────────────────────────────────────────────────────────────────────

def page_my_results():
    summary = st.session_state.get("summary")
    session_id = st.session_state.get("session_id")
    pid = st.session_state.get("participant_id", "—")
    ts  = st.session_state.get("session_ts", "—")

    if not session_id or not st.session_state.get("test_complete"):
        st.markdown("""
        <div class="warning-box">
            ⚠️ No completed test session found in this browser session.
            Please complete the Stroop Test first, or browse
            <b>All Sessions</b> to view previously saved results.
        </div>
        """, unsafe_allow_html=True)
        if st.button("← Start Test", type="primary", key="results_no_session_btn"):
            st.session_state["page"] = "participant"
            st.rerun()
        return

    # Make sure summary is computed
    if not summary:
        _save_results_if_needed()
        summary = st.session_state.get("summary", {})

    trials_df = load_session_trials(session_id)

    st.markdown(
        "<h1 style='color:#4A90E2;font-size:2rem;'>📊 My Test Results</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<p style='color:#A8B2C8;'>Participant: <b style='color:#E8ECF4;'>{pid}</b> &nbsp;|&nbsp; "
        f"Session ID: <b style='color:#74B9FF;'>{session_id}</b> &nbsp;|&nbsp; "
        f"Completed: <b style='color:#E8ECF4;'>{ts}</b></p>",
        unsafe_allow_html=True,
    )

    st.divider()

    # ── Key metrics ────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">📈 Performance Summary</div>', unsafe_allow_html=True)

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Total Trials",  summary.get("total_trials", 0))
    m2.metric("✅ Correct",    summary.get("correct", 0))
    m3.metric("❌ Incorrect",  summary.get("incorrect", 0))
    m4.metric("Accuracy",      f"{summary.get('accuracy_pct', '—')}%")
    m5.metric("Error Rate",    f"{summary.get('error_rate_pct', '—')}%")

    st.markdown("<br/>", unsafe_allow_html=True)

    m6, m7, m8, m9 = st.columns(4)
    m6.metric("Overall Avg RT",         f"{summary.get('mean_rt_ms', '—')} ms")
    m7.metric("Congruent Avg RT",        f"{summary.get('congruent_rt_ms', '—')} ms")
    m8.metric("Incongruent Avg RT",      f"{summary.get('incongruent_rt_ms', '—')} ms")

    rt_diff = summary.get("rt_difference_ms")
    rt_diff_display = f"+{rt_diff} ms" if rt_diff and rt_diff > 0 else (f"{rt_diff} ms" if rt_diff is not None else "—")
    m9.metric("RT Difference (Inc−Con)", rt_diff_display,
              delta_color="inverse" if rt_diff and rt_diff > 0 else "normal")

    st.markdown("<br/>", unsafe_allow_html=True)

    m10, m11, m12 = st.columns(3)
    m10.metric("Congruent Accuracy",   f"{summary.get('congruent_acc_pct', '—')}%")
    m11.metric("Incongruent Accuracy", f"{summary.get('incongruent_acc_pct', '—')}%")
    m12.metric("Congruent Trials",     summary.get("congruent_trials", 0))

    st.divider()

    # ── Charts ─────────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">📉 Visualization Dashboard</div>', unsafe_allow_html=True)

    ch1, ch2 = st.columns(2)
    with ch1:
        st.subheader("Reaction Time Comparison")
        fig_rt = plot_rt_comparison(summary)
        st.pyplot(fig_rt, use_container_width=True)

    with ch2:
        st.subheader("Accuracy Comparison")
        fig_acc = plot_accuracy_comparison(summary)
        st.pyplot(fig_acc, use_container_width=True)

    st.markdown("<br/>", unsafe_allow_html=True)
    st.subheader("Trial-by-Trial Reaction Time")
    fig_trial = plot_trial_by_trial_rt(trials_df)
    st.pyplot(fig_trial, use_container_width=True)

    st.divider()

    # ── Interpretation ─────────────────────────────────────────────────────
    st.markdown('<div class="section-header">🔍 Automated Interpretation</div>', unsafe_allow_html=True)
    interpretation = generate_interpretation(summary)
    st.markdown(f"""
    <div class="card">
        <p style="color:#C8D6E5;font-size:0.95rem;line-height:1.8;">
            {interpretation.replace(chr(10), '<br/>')}
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # ── Trial-level data table ─────────────────────────────────────────────
    st.markdown('<div class="section-header">📋 Trial-Level Data</div>', unsafe_allow_html=True)

    if not trials_df.empty:
        display_cols = [c for c in [
            "trial_number", "word", "ink_colour", "condition",
            "correct_answer", "participant_answer", "is_correct", "reaction_time_ms",
        ] if c in trials_df.columns]
        st.dataframe(
            trials_df[display_cols].rename(columns={"reaction_time_ms": "RT (ms)"}),
            use_container_width=True,
            height=300,
        )
    else:
        st.info("Trial data not available.")

    st.divider()

    # ── Download buttons ────────────────────────────────────────────────────
    st.markdown('<div class="section-header">💾 Download Your Data</div>', unsafe_allow_html=True)
    dl1, dl2 = st.columns(2)

    with dl1:
        if not trials_df.empty:
            csv_trials = trials_to_csv_string(trials_df)
            st.download_button(
                label="⬇️ Download Trial Data (CSV)",
                data=csv_trials,
                file_name=f"stroop_trials_{session_id}.csv",
                mime="text/csv",
                key="dl_trials",
                use_container_width=True,
            )

    with dl2:
        csv_summary = summary_to_csv_string(summary, session_id, pid, ts)
        st.download_button(
            label="⬇️ Download Summary (CSV)",
            data=csv_summary,
            file_name=f"stroop_summary_{session_id}.csv",
            mime="text/csv",
            key="dl_summary",
            use_container_width=True,
        )


# ─────────────────────────────────────────────────────────────────────────────
# Page: All Results / Session Browser
# ─────────────────────────────────────────────────────────────────────────────

def page_all_results():
    st.markdown(
        "<h1 style='color:#4A90E2;font-size:2rem;'>📁 All Saved Sessions</h1>",
        unsafe_allow_html=True,
    )

    summaries_df = load_all_summaries()

    if summaries_df.empty:
        st.markdown("""
        <div class="info-box">
            ℹ️ No saved sessions found yet.  Complete the Stroop test to generate results.
        </div>
        """, unsafe_allow_html=True)
        if st.button("🚀 Start Test", type="primary", key="all_results_start_btn"):
            st.session_state["page"] = "participant"
            st.rerun()
        return

    # Convert numeric columns
    numeric_cols = [
        "accuracy_pct", "mean_rt_ms", "congruent_rt_ms",
        "incongruent_rt_ms", "rt_difference_ms",
        "congruent_acc_pct", "incongruent_acc_pct",
        "total_trials", "correct", "incorrect",
    ]
    for col in numeric_cols:
        if col in summaries_df.columns:
            summaries_df[col] = pd.to_numeric(summaries_df[col], errors="coerce")

    # ── Summary table ──────────────────────────────────────────────────────
    st.markdown('<div class="section-header">📊 Session Overview</div>', unsafe_allow_html=True)

    display_df = summaries_df[[c for c in [
        "session_id", "participant_id", "timestamp",
        "total_trials", "accuracy_pct", "mean_rt_ms",
        "congruent_rt_ms", "incongruent_rt_ms", "rt_difference_ms",
    ] if c in summaries_df.columns]].copy()

    display_df.columns = [c.replace("_", " ").title() for c in display_df.columns]
    st.dataframe(display_df, use_container_width=True, height=280)

    st.divider()

    # ── Session detail viewer ─────────────────────────────────────────────
    st.markdown('<div class="section-header">🔎 View Session Details</div>', unsafe_allow_html=True)

    session_options = []
    if "session_id" in summaries_df.columns and "participant_id" in summaries_df.columns:
        for _, row in summaries_df.iterrows():
            label = f"{row.get('participant_id','?')} | {row.get('session_id','?')} | {row.get('timestamp','')}"
            session_options.append((label, row.get("session_id")))

    if session_options:
        selected_label = st.selectbox(
            "Select a session to inspect:",
            options=[s[0] for s in session_options],
            key="session_select",
        )
        selected_sid = next((s[1] for s in session_options if s[0] == selected_label), None)

        if selected_sid:
            sel_summary_row = summaries_df[summaries_df["session_id"] == selected_sid].iloc[0].to_dict()
            sel_trials_df   = load_session_trials(selected_sid)

            col_a, col_b, col_c, col_d = st.columns(4)
            col_a.metric("Accuracy",     f"{sel_summary_row.get('accuracy_pct','—')}%")
            col_b.metric("Mean RT",      f"{sel_summary_row.get('mean_rt_ms','—')} ms")
            col_c.metric("Cong RT",      f"{sel_summary_row.get('congruent_rt_ms','—')} ms")
            col_d.metric("Incong RT",    f"{sel_summary_row.get('incongruent_rt_ms','—')} ms")

            if not sel_trials_df.empty:
                st.markdown("<br/>", unsafe_allow_html=True)
                fig_trial = plot_trial_by_trial_rt(sel_trials_df)
                st.pyplot(fig_trial, use_container_width=True)

                csv_dl = trials_to_csv_string(sel_trials_df)
                st.download_button(
                    label=f"⬇️ Download Trials for {selected_sid}",
                    data=csv_dl,
                    file_name=f"stroop_trials_{selected_sid}.csv",
                    mime="text/csv",
                    key=f"dl_session_{selected_sid}",
                )

    st.divider()

    # ── Multi-session comparison ───────────────────────────────────────────
    if len(summaries_df) >= 2:
        st.markdown('<div class="section-header">📐 Session Comparison Charts</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="info-box">
            ℹ️ These charts compare descriptive metrics across recorded sessions.
            They do <b>not</b> imply cognitive or clinical differences between participants.
        </div>
        """, unsafe_allow_html=True)

        summaries_list = summaries_df.to_dict(orient="records")
        # Rename for compare_sessions
        for s in summaries_list:
            if "participant_id" not in s:
                s["participant_id"] = s.get("Participant Id", "?")
            if "session_id" not in s:
                s["session_id"] = s.get("Session Id", "?")

        comp_df = compare_sessions(summaries_list)

        if not comp_df.empty:
            cc1, cc2 = st.columns(2)
            with cc1:
                st.subheader("Accuracy Comparison")
                fig_comp_acc = plot_session_comparison(comp_df, "Accuracy (%)", "Accuracy (%)")
                st.pyplot(fig_comp_acc, use_container_width=True)
            with cc2:
                st.subheader("Mean RT Comparison")
                fig_comp_rt = plot_session_comparison(comp_df, "Mean RT (ms)", "Mean RT (ms)")
                st.pyplot(fig_comp_rt, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# Utility helpers
# ─────────────────────────────────────────────────────────────────────────────

def _save_results_if_needed():
    """Compute summary and save to CSV exactly once per session."""
    if st.session_state.get("results_saved"):
        return

    trial_results = st.session_state.get("trial_results", [])
    session_id    = st.session_state.get("session_id")
    pid           = st.session_state.get("participant_id", "unknown")
    ts            = st.session_state.get("session_ts") or get_current_timestamp()

    if not trial_results or not session_id:
        return

    trials_df = pd.DataFrame(trial_results)
    summary   = compute_summary(trials_df)

    st.session_state["summary"] = summary

    try:
        save_trials(session_id, pid, ts, trial_results)
        save_summary(session_id, pid, ts, summary)
        st.session_state["results_saved"] = True
    except Exception as e:
        st.error(f"⚠️ Could not save results: {e}")


def _reset_test():
    """Clear test-related session state."""
    for key in ["trials", "trial_index", "trial_results", "trial_start_ms",
                "test_complete", "results_saved", "summary", "session_id", "session_ts"]:
        st.session_state[key] = None if key not in ("trials", "trial_results") else []
    st.session_state["trial_index"] = 0
    st.session_state["test_complete"] = False
    st.session_state["results_saved"] = False


# ─────────────────────────────────────────────────────────────────────────────
# Router
# ─────────────────────────────────────────────────────────────────────────────

def main():
    render_sidebar()

    page = st.session_state.get("page", "home")

    if page == "home":
        page_home()
    elif page == "participant":
        page_participant()
    elif page == "test":
        page_stroop_test()
    elif page == "results":
        page_my_results()
    elif page == "all_results":
        page_all_results()
    else:
        page_home()


if __name__ == "__main__":
    main()
