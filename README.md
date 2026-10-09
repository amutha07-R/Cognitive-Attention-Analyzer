# 🧠 Cognitive Attention and Reaction Time Analyzer

> A Stroop Colour-Word Test application for studying selective attention,
> cognitive interference, and human reaction time.
> 
> **B.Tech Artificial Intelligence and Data Science — Mini Project**  
> _Cognitive Science as the primary subject_

---

## Abstract

This project implements an interactive, web-based Stroop Colour-Word Test using Python
and Streamlit. Participants view colour words (e.g., "GREEN") printed in ink colours that
may match (congruent) or differ (incongruent). They identify the ink colour using
four response buttons. The application records each response and reaction time,
calculates descriptive statistics, generates charts, and saves results to CSV files.
No machine learning is required for the core functionality.

---

## Problem Statement

Human attention is a limited cognitive resource. Understanding how well a person can
resist automatic word-reading in favour of deliberate colour-identification gives insight
into selective attention and cognitive control. Measuring reaction time differences
between congruent and incongruent conditions provides a quantitative index of
cognitive interference (the Stroop effect).

---

## Motivation

- The Stroop effect is one of the most replicated findings in cognitive psychology.
- Measuring it requires no lab equipment — just a screen and a timer.
- Analysing the results with Python demonstrates practical AI & DS skills:
  data collection, statistical analysis, and data visualisation.
- The project bridges Cognitive Science and Data Science in a meaningful way.

---

## Objectives

1. Build an interactive Stroop Colour-Word Test in a browser.
2. Collect accurate reaction time and accuracy data per trial.
3. Compute and display descriptive statistics for congruent and incongruent conditions.
4. Visualise results with professional Matplotlib charts.
5. Persist data to CSV and allow download.
6. Explain Cognitive Science concepts clearly for an academic audience.

---

## Scope

- Single-user, self-administered, web-based Stroop test.
- 10–40 configurable trials per session.
- Balanced congruent/incongruent split.
- Local CSV storage; no database or internet required.
- Not a clinical, diagnostic, or therapeutic tool.

---

## Cognitive Science Concepts Used

| Concept | Description |
|---|---|
| Selective Attention | Focusing on ink colour while suppressing automatic word reading |
| Cognitive Interference | Conflict between word meaning and ink colour slowing response |
| Reaction Time | Time from stimulus display to participant click (in ms) |
| Stroop Effect | Slower/less accurate responses on incongruent vs congruent trials |
| Congruent Stimulus | Word meaning matches ink colour — easier, faster |
| Incongruent Stimulus | Word meaning differs from ink colour — harder, slower |
| Descriptive Statistics | Mean, accuracy, error rate used to summarise performance |

---

## Technologies Used

| Technology | Version | Purpose |
|---|---|---|
| Python | ≥ 3.9 | Core application logic |
| Streamlit | ≥ 1.32 | Interactive web interface |
| Pandas | ≥ 2.0 | Data manipulation and analysis |
| Matplotlib | ≥ 3.7 | Chart generation |
| NumPy | ≥ 1.24 | Numerical computations |
| CSV (stdlib) | — | Local data persistence |

---

## System Requirements

- **OS:** Windows 10/11, macOS 12+, or Ubuntu 20.04+
- **Python:** 3.9 or higher
- **RAM:** 512 MB minimum (2 GB recommended)
- **Browser:** Chrome, Edge, Firefox (modern version)
- **Internet:** Only for loading Google Fonts (optional; works offline with default fonts)

---

## Project Folder Structure

```
Cognitive_Attention_Analyzer/
├── app.py                  # Main Streamlit application (entry point)
├── requirements.txt        # Python dependencies
├── README.md               # This file
├── .gitignore              # Git ignore rules
├── data/
│   ├── .gitkeep            # Keeps the folder in git
│   ├── trials.csv          # Created automatically: individual trial records
│   └── summaries.csv       # Created automatically: session-level summaries
├── src/
│   ├── __init__.py         # Python package marker
│   ├── stroop_test.py      # Trial generation, stimulus building, answer checking
│   ├── analysis.py         # Statistical analysis and text interpretation
│   ├── storage.py          # CSV read/write, session management
│   └── visualization.py   # All Matplotlib chart functions
└── docs/
    ├── project_report.md   # Full college mini-project report
    └── test_cases.md       # Manual test cases
```

---

## Installation — Windows PowerShell

### Step 1 — Navigate to the project folder

```powershell
cd D:\Cognitive_Attention_Analyzer
```

### Step 2 — Create a virtual environment

```powershell
python -m venv venv
```

### Step 3 — Activate the virtual environment

```powershell
.\venv\Scripts\Activate.ps1
```

> **If you get an execution policy error:**
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```
> Then try activating again.

### Step 4 — Install dependencies

```powershell
pip install -r requirements.txt
```

### Step 5 — Run the application

```powershell
streamlit run app.py
```

### Step 6 — Open in browser

Streamlit will print a local URL. Open it in your browser:

```
http://localhost:8501
```

---

## Application Features

- **Home Page** — Project introduction, cognitive science concepts, experiment overview.
- **Participant Setup** — Enter a nickname/ID, choose number of trials, read instructions.
- **Stroop Test** — Interactive trial presentation with 4 colour response buttons, timer, progress bar.
- **My Results** — Summary metrics, 3 Matplotlib charts, automated interpretation, data download.
- **All Sessions** — Browse all saved sessions, inspect individual sessions, compare multiple sessions.

---

## Algorithm / Workflow

```
1. Participant enters ID and selects trial count.
2. App generates a balanced, shuffled sequence of congruent and incongruent trials.
3. For each trial:
   a. Display word in ink colour on screen.
   b. Record start timestamp.
   c. Wait for participant to click one of four colour buttons.
   d. Record end timestamp.
   e. Compute RT = end_ms − start_ms.
   f. Check if answer == ink colour.
   g. Store result dict.
4. After all trials:
   a. Build DataFrame from results.
   b. Compute summary statistics.
   c. Generate interpretation.
   d. Save trials and summary to CSV.
   e. Render results page with charts and metrics.
```

---

## How the Stroop Test Works

Each trial presents a colour word (RED, GREEN, BLUE, YELLOW) in an ink colour.
The task is to click the button matching the **ink colour**, not the word.

- **Congruent:** `GREEN` displayed in green ink → click Green → typically fast.
- **Incongruent:** `GREEN` displayed in red ink → click Red → typically slower.

The difference in average reaction time between incongruent and congruent conditions
is called the **Stroop interference effect**.

---

## Data Collection and Analysis

### Trial data (data/trials.csv)
| Column | Description |
|---|---|
| session_id | Unique 8-character session identifier |
| participant_id | Participant nickname |
| timestamp | Session start time |
| trial_number | 1-indexed trial position |
| word | The displayed word |
| ink_colour | The ink colour |
| condition | congruent / incongruent |
| correct_answer | The ink colour (correct response) |
| participant_answer | What the participant clicked |
| is_correct | True / False |
| reaction_time_ms | Response time in milliseconds |

### Summary data (data/summaries.csv)
One row per completed session. Includes accuracy, error rate, mean RT for each condition,
and RT difference.

---

## Expected Output

After completing a 20-trial session, the Results page shows:
- Overall accuracy, error rate, and mean reaction time.
- Separate statistics for congruent and incongruent trials.
- Bar charts for RT and accuracy comparison.
- Trial-by-trial RT scatter chart.
- A short, automatically generated interpretation of task performance.
- Download buttons for trial and summary CSV files.

---

## Limitations

1. **Single session:** Results from one session have high random variability.
2. **Screen latency:** Click timing includes display and input device delays (~10–50 ms).
3. **Practice effects:** Performance typically improves across trials within a session.
4. **Self-administered:** No control for external distractions.
5. **No baseline:** No neutral condition or control group.
6. **Individual differences:** Age, expertise, language, and fatigue affect results.
7. **NOT diagnostic:** Does not measure intelligence or any clinical condition.

---

## Future Enhancements

- Add neutral trials (non-colour words in colour ink).
- Support multiple languages.
- Add a pre-test practice block.
- Use WebRTC audio stimuli to remove reading latency.
- Add inter-trial intervals (fixation cross).
- Export to PDF report.
- Group comparison with statistical tests (e.g., paired t-test).

---

## Common Errors and Fixes

| Error | Fix |
|---|---|
| `ModuleNotFoundError: No module named 'streamlit'` | Activate venv and run `pip install -r requirements.txt` |
| `ExecutionPolicy` error when activating venv | Run `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` |
| Port 8501 already in use | Run `streamlit run app.py --server.port 8502` |
| App shows blank page | Hard-refresh browser with Ctrl+Shift+R |
| CSV not created | Ensure you have write permissions to the `data/` folder |

---

## References

- Stroop, J. R. (1935). Studies of interference in serial verbal reactions.
  *Journal of Experimental Psychology*, 18(6), 643–662.
- MacLeod, C. M. (1991). Half a century of research on the Stroop effect:
  An integrative review. *Psychological Bulletin*, 109(2), 163–203.
- Posner, M. I., & Petersen, S. E. (1990). The attention system of the human brain.
  *Annual Review of Neuroscience*, 13(1), 25–42.
- Streamlit Documentation: https://docs.streamlit.io
- Pandas Documentation: https://pandas.pydata.org/docs/

---

*This project is for academic and educational purposes only.
It is not a clinical, diagnostic, or therapeutic tool.*
