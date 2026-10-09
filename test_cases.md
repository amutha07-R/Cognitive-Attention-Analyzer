# Test Cases — Cognitive Attention and Reaction Time Analyzer

**Project:** Cognitive Attention and Reaction Time Analyzer Using Python  
**Module Under Test:** All src modules + app.py  
**Test Type:** Manual verification (functional, edge-case, error-handling)

---

## TC-01: Congruent Trial Generation

**Module:** `src/stroop_test.py` → `generate_trial("congruent")`  
**Description:** Verify that a congruent trial has matching word and ink colour.

| Step | Action | Expected Result |
|---|---|---|
| 1 | Call `generate_trial("congruent")` | Returns a dict |
| 2 | Check `trial["word"] == trial["ink_colour"]` | True |
| 3 | Check `trial["condition"]` | `"congruent"` |
| 4 | Check `trial["correct_answer"] == trial["ink_colour"]` | True |
| 5 | Check `trial["word"] in COLOURS` | True |

---

## TC-02: Incongruent Trial Generation

**Module:** `src/stroop_test.py` → `generate_trial("incongruent")`  
**Description:** Verify that word meaning and ink colour differ.

| Step | Action | Expected Result |
|---|---|---|
| 1 | Call `generate_trial("incongruent")` repeatedly (10 times) | Returns dicts |
| 2 | Check `trial["word"] != trial["ink_colour"]` for each | True in all cases |
| 3 | Check `trial["correct_answer"] == trial["ink_colour"]` | True |
| 4 | Check `trial["condition"]` | `"incongruent"` |

---

## TC-03: Balanced Trial Sequence

**Module:** `src/stroop_test.py` → `generate_trial_sequence(20)`  
**Description:** Verify balance between congruent and incongruent conditions.

| Step | Action | Expected Result |
|---|---|---|
| 1 | Call `generate_trial_sequence(20)` | Returns list of 20 dicts |
| 2 | Count congruent trials | 10 |
| 3 | Count incongruent trials | 10 |
| 4 | Verify list is shuffled (order not always sorted) | Passed on multiple runs |
| 5 | Call with `n=11` | Returns 11 trials (5 cong, 6 incong) |
| 6 | Call with `n=10` | Returns 10 trials (5 cong, 5 incong) |

---

## TC-04: Correct Answer — Congruent Trial

**Module:** `src/stroop_test.py` → `check_answer()`  
**Description:** Participant selects the ink colour correctly.

| Step | Action | Expected Result |
|---|---|---|
| 1 | Create trial: `word="Red", ink_colour="Red", condition="congruent"` | — |
| 2 | Call `check_answer(trial, "Red")` | Returns dict with `is_correct=True` |
| 3 | Check `result["participant_answer"]` | `"Red"` |
| 4 | Check `result["correct_answer"]` | `"Red"` |

---

## TC-05: Incorrect Answer — Incongruent Trial

**Module:** `src/stroop_test.py` → `check_answer()`  
**Description:** Participant reads the word instead of identifying the ink colour.

| Step | Action | Expected Result |
|---|---|---|
| 1 | Create trial: `word="Green", ink_colour="Red", condition="incongruent"` | — |
| 2 | Call `check_answer(trial, "Green")` (reading word, not ink) | Returns `is_correct=False` |
| 3 | Check `result["correct_answer"]` | `"Red"` |
| 4 | Check `result["participant_answer"]` | `"Green"` |

---

## TC-06: Reaction Time Recording

**Module:** `src/stroop_test.py` → `compute_reaction_time_ms()`  
**Description:** Verify RT calculation is correct.

| Step | Action | Expected Result |
|---|---|---|
| 1 | `start_ms = 1000.0`, `end_ms = 1650.5` | — |
| 2 | Call `compute_reaction_time_ms(1000.0, 1650.5)` | Returns `650.5` |
| 3 | Call with `start=end` (same time) | Returns `0.0` |
| 4 | Call with `end < start` (clock error) | Returns `0.0` (non-negative) |

---

## TC-07: Summary Statistics — Normal Data

**Module:** `src/analysis.py` → `compute_summary()`  
**Description:** Verify correct statistics for a known set of trials.

**Input DataFrame:**
```
condition      is_correct  reaction_time_ms
congruent      True        400
congruent      True        350
incongruent    True        600
incongruent    False       800
```

| Step | Metric | Expected Result |
|---|---|---|
| 1 | `total_trials` | 4 |
| 2 | `correct` | 3 |
| 3 | `incorrect` | 1 |
| 4 | `accuracy_pct` | 75.0 |
| 5 | `error_rate_pct` | 25.0 |
| 6 | `congruent_rt_ms` | 375.0 |
| 7 | `incongruent_rt_ms` | 700.0 |
| 8 | `rt_difference_ms` | 325.0 |
| 9 | `congruent_acc_pct` | 100.0 |
| 10 | `incongruent_acc_pct` | 50.0 |

---

## TC-08: Summary Statistics — Empty DataFrame

**Module:** `src/analysis.py` → `compute_summary()`  
**Description:** Application must not crash with empty data.

| Step | Action | Expected Result |
|---|---|---|
| 1 | Call `compute_summary(pd.DataFrame())` | Returns dict with 0 or None values |
| 2 | No exception raised | True |
| 3 | Check `result["total_trials"]` | 0 |

---

## TC-09: Summary Statistics — One Condition Only

**Module:** `src/analysis.py` → `compute_summary()`  
**Description:** Handle case where only congruent trials exist (no incongruent).

| Step | Action | Expected Result |
|---|---|---|
| 1 | Build DataFrame with only `condition="congruent"` rows | — |
| 2 | Call `compute_summary(df)` | Returns dict without crash |
| 3 | Check `incongruent_rt_ms` | `None` (not an error) |
| 4 | Check `rt_difference_ms` | `None` |

---

## TC-10: CSV Creation — New Files

**Module:** `src/storage.py` → `save_trials()`, `save_summary()`  
**Description:** CSV files are created automatically if missing.

| Step | Action | Expected Result |
|---|---|---|
| 1 | Delete `data/trials.csv` and `data/summaries.csv` if they exist | — |
| 2 | Call `save_trials(...)` with one trial | `data/trials.csv` is created with header + 1 row |
| 3 | Call `save_summary(...)` with one summary | `data/summaries.csv` is created with header + 1 row |
| 4 | Inspect header row of trials.csv | Contains all TRIAL_COLUMNS |

---

## TC-11: CSV Append — No Overwrite

**Module:** `src/storage.py` → `save_trials()`  
**Description:** Existing data is not lost when a new session is saved.

| Step | Action | Expected Result |
|---|---|---|
| 1 | Save first session (session_id = "AAAA") with 3 trials | `trials.csv` has 1 header + 3 rows |
| 2 | Save second session (session_id = "BBBB") with 3 trials | `trials.csv` has 1 header + 6 rows |
| 3 | Load all trials | Both sessions present in DataFrame |
| 4 | Filter by session_id "AAAA" | Returns exactly 3 rows |

---

## TC-12: Load Missing CSV

**Module:** `src/storage.py` → `load_all_summaries()`  
**Description:** Application handles missing CSV without crashing.

| Step | Action | Expected Result |
|---|---|---|
| 1 | Delete `data/summaries.csv` | — |
| 2 | Call `load_all_summaries()` | Returns empty DataFrame with correct columns |
| 3 | No exception raised | True |

---

## TC-13: Load Session Trials — Unknown Session ID

**Module:** `src/storage.py` → `load_session_trials()`  
**Description:** Returns empty DataFrame for a session that does not exist.

| Step | Action | Expected Result |
|---|---|---|
| 1 | Call `load_session_trials("ZZZZZZZZ")` | Returns empty DataFrame |
| 2 | No exception raised | True |
| 3 | Returned DataFrame has correct column names | True |

---

## TC-14: Dashboard Charts — Normal Data

**Module:** `src/visualization.py`  
**Description:** Charts render without error for valid summary and trial data.

| Step | Action | Expected Result |
|---|---|---|
| 1 | Create valid summary dict with both condition RTs | — |
| 2 | Call `plot_rt_comparison(summary)` | Returns a matplotlib Figure |
| 3 | Call `plot_accuracy_comparison(summary)` | Returns a matplotlib Figure |
| 4 | Build a 5-row trial DataFrame | — |
| 5 | Call `plot_trial_by_trial_rt(df)` | Returns a matplotlib Figure |

---

## TC-15: Dashboard Charts — Empty Data

**Module:** `src/visualization.py`  
**Description:** Charts handle empty/None data gracefully without crashing.

| Step | Action | Expected Result |
|---|---|---|
| 1 | Pass `{}` as summary to `plot_rt_comparison` | Returns Figure with "No data" message |
| 2 | Pass empty DataFrame to `plot_trial_by_trial_rt` | Returns Figure with "No data" message |
| 3 | No exception raised | True |

---

## TC-16: Participant ID Validation

**Module:** `app.py` → `page_participant()`  
**Description:** Invalid participant IDs are rejected before starting the test.

| Step | Input | Expected Result |
|---|---|---|
| 1 | Empty string "" | Error: "Please enter a participant ID" |
| 2 | Single character "A" | Error: "at least 2 characters" |
| 3 | Valid "Student01" | Proceeds to test page |
| 4 | Spaces only "   " | Treated as empty after strip; shows error |

---

## TC-17: Duplicate Click Prevention

**Module:** `app.py` → `page_stroop_test()`  
**Description:** Clicking a button twice for the same trial only records one response.

| Step | Action | Expected Result |
|---|---|---|
| 1 | On trial index 3, click "Red" | Result recorded; `trial_index` advances to 4; page reruns |
| 2 | After rerun, trial 4 is shown | Only one result recorded for trial 3 |
| 3 | Check `len(trial_results)` | Equal to current trial index |

*Implementation note: Streamlit's button key includes the trial index
(`answer_{colour}_{idx}`), so each trial gets unique button keys. A page rerun
after each click advances the index, making previous buttons non-functional.*

---

## TC-18: Test Completion Detection

**Module:** `app.py` → `page_stroop_test()`  
**Description:** Completion screen appears after final trial.

| Step | Action | Expected Result |
|---|---|---|
| 1 | Configure 10 trials, answer all 10 | Completion screen is shown |
| 2 | Check `st.session_state["test_complete"]` | True |
| 3 | Check `st.session_state["results_saved"]` | True |
| 4 | Navigate to "My Results" page | Displays summary for completed session |

---

## TC-19: Interpretation — Positive RT Difference

**Module:** `src/analysis.py` → `generate_interpretation()`  
**Description:** Correct text is produced when incongruent RT > congruent RT.

| Step | Action | Expected Result |
|---|---|---|
| 1 | Set `congruent_rt_ms=400`, `incongruent_rt_ms=650`, `rt_difference_ms=250` | — |
| 2 | Call `generate_interpretation(summary)` | Text mentions "250 ms longer" and "Stroop interference" |
| 3 | Text does NOT mention diagnosis or disorder | True |
| 4 | Text includes disclaimer about clinical assessment | True |

---

## TC-20: Multi-Session Comparison

**Module:** `src/analysis.py` → `compare_sessions()`;  
         `src/visualization.py` → `plot_session_comparison()`  
**Description:** Comparison works correctly for 2+ sessions.

| Step | Action | Expected Result |
|---|---|---|
| 1 | Create list of 3 summary dicts with different participant IDs | — |
| 2 | Call `compare_sessions(summaries_list)` | Returns DataFrame with 3 rows |
| 3 | Call `plot_session_comparison(df, "Accuracy (%)", "Accuracy (%)")` | Returns Figure |
| 4 | All 3 sessions appear as bars in the chart | True |

---

## TC-21: CSV Download

**Module:** `src/storage.py` → `trials_to_csv_string()`  
**Description:** CSV string is valid and complete.

| Step | Action | Expected Result |
|---|---|---|
| 1 | Load trials for a session into DataFrame | — |
| 2 | Call `trials_to_csv_string(df)` | Returns a string |
| 3 | Parse the string with `pd.read_csv(io.StringIO(s))` | Returns same DataFrame |
| 4 | Check column names match TRIAL_COLUMNS | True |

---

## TC-22: Build Stimulus HTML

**Module:** `src/stroop_test.py` → `build_stimulus_html()`  
**Description:** HTML output contains correct word and colour.

| Step | Action | Expected Result |
|---|---|---|
| 1 | Trial: `word="Blue", ink_colour="Red"` | — |
| 2 | Call `build_stimulus_html(trial)` | Returns HTML string |
| 3 | Check HTML contains `color:#E74C3C` (Red hex) | True |
| 4 | Check HTML contains the text "BLUE" in uppercase | True |

---

*All test cases above are designed for manual execution by the developer.
Results are verified by inspection of actual output, DataFrame contents, or visual
chart review.  Automated test scripts can be added using pytest for TC-01 through TC-09.*
