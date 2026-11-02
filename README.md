# 🐍 PyLearn — Python for Data Science & AI

An interactive, self-paced Python course for complete beginners, built with
[Streamlit](https://streamlit.io). It takes you from your first `print()` to
SQL, pandas and matplotlib, with code you can run and edit in a sandbox,
feedback that explains *why* an answer is wrong, and spaced repetition.

| | |
|---|---|
| **Topics** | 10 (34 lessons, 116 runnable, editable examples) |
| **Exercises** | 132: 49 multiple choice, 37 predict-the-output, 23 debugging, 23 coding |
| **Quizzes** | one per topic (all MCQ and prediction questions, scored with explanations) |
| **Mini-projects** | 3 realistic projects (12 steps) using pandas, matplotlib and SQLite |
| **Tests** | 333 automated tests |

## Contents

1. [Features](#features)
2. [Installation](#installation)
3. [Running the app](#running-the-app)
4. [Running the tests](#running-the-tests)
5. [Course outline](#course-outline)
6. [Architecture](#architecture)
7. [Sandbox security model](#sandbox-security-model)
8. [How progress, mastery and spaced repetition work](#how-progress-mastery-and-spaced-repetition-work)
9. [Adding or editing content](#adding-or-editing-content)
10. [Limitations](#limitations)

---

## Features

* **Progressive lessons.** Each lesson has explanations, tables, key points and
  several **editable, runnable examples**. Programs that use `input()` read from
  an Input box.
* **Four exercise types:**
  * 🔘 **Multiple choice.** *Every* wrong option has its own explanation of why
    it's wrong.
  * 🔮 **Predict the output.** Your prediction is compared with real Python
    output. Feedback covers specific common mistakes (for example "you forgot
    the `None` printed by the outer `print`") as well as general ones: quotes,
    capital letters, line breaks, ordering, `/` giving a float, a missing `None`,
    and the first line that differs.
  * 🐞 **Fix the bug.** Syntax, runtime and logic bugs in realistic code.
  * ⌨️ **Write the code.** Your code is run against automatic checks.
* **Beginner-friendly error explanations.** About 40 rules turn Python
  tracebacks (including SQLite errors) into plain English: what happened, and
  how to fix it. The grader also spots common misconceptions. For example, a
  function that **prints instead of returning** gets this message: *"Your
  function printed `212.0` but returned `None`…"*. It also flags a value with
  the right digits but the wrong type (`'5'` vs `5`).
* **Hints and reference solutions.** Hints are revealed one at a time. The
  solution unlocks after your first attempt.
* **Topic quizzes** with a score and an explanation for each question.
* **Python sandbox page** with templates for pandas, SQLite, matplotlib, files
  and input. Charts are captured and displayed automatically.
* **Progress tracking.** Every attempt is stored in SQLite, with support for
  several learner profiles.
* **Mastery scores** per topic, with levels: Not started, Learning, Developing,
  Proficient, Mastered.
* **Spaced repetition (SM-2).** Items you answer are rescheduled, and the
  Review page shows what's due.
* **Concept drill.** Practise any concept tag (for example `return-vs-print`,
  `slicing`, `joins`), weakest items first.
* **Revision recommendations.** These combine due reviews, weak topics, weak
  concepts and the next topic whose prerequisites you've met.
* **Dashboard** with metrics, mastery bars, an activity chart, a study streak
  and recent answers.

## Installation

You need **Python 3.10 or newer** (tested with 3.13), on Linux, macOS or Windows.

```bash
git clone https://github.com/xggywrld/iggywiggy.git
cd iggywiggy
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt    # app only
pip install -r requirements-dev.txt  # app + pytest
```

## Running the app

```bash
streamlit run app.py
```

Streamlit opens <http://localhost:8501> in your browser. If it doesn't, open
that address yourself.

* Progress is saved to `~/.pylearn/progress.db`. Set `PYLEARN_DATA_DIR` to use a
  different folder:
  ```bash
  PYLEARN_DATA_DIR=./my-data streamlit run app.py
  ```
* The first time code uses matplotlib, building the font cache can take a few
  seconds. The cache is kept in the data folder, so later runs are fast.

**Suggested route:** 📚 Learn → read a lesson and run its examples → mark it
complete → 🏋️ Practice → 📝 Quiz. Come back daily for 🔁 Review, and follow the
🏠 Dashboard's recommendations. Try 🛠️ Projects after topic 8.

## Running the tests

```bash
python -m pytest
```

There are 333 tests. They take about 1.5 minutes, because many of them run real
code in the sandbox.

| File | What it checks |
|---|---|
| `tests/test_content.py` | **Every answer key is checked against the real interpreter.** Each predict-the-output answer must match Python's actual output. Each debug and coding exercise's reference solution must pass its checks, and the buggy or starter code must *fail* them. Each lesson example must run (or fail only where it deliberately demonstrates an error). Each project step's solution must pass. Also checks the structure: unique IDs, one correct option per MCQ, a "why" for every wrong option, every exercise kind present in every topic, and minimum coverage of the in-depth concepts. |
| `tests/test_sandbox.py` | Security and behaviour. Blocked file reads and writes outside the sandbox folder, directory listing, `os.system`/`posix_spawn` (including routes past the static check), sockets, ctypes, dunder escapes, `eval`/`exec`, re-opening stdout, spoofed result markers, timeouts, memory limits, output truncation, stdin, figure capture, and check comparison (tuples vs lists, numpy types, float tolerance, bool vs int). |
| `tests/test_grading.py` | MCQ feedback, output-diff hints, print-vs-return detection, wrong-type detection, and error explanations for about 16 common errors. |
| `tests/test_progress.py` | SM-2 maths, scheduling and due dates (with simulated time), recency-weighted item scores, mastery, recommendations, concept-tag accuracy, streaks, separate profiles and reset. |
| `tests/test_app.py` | End-to-end UI tests with Streamlit's `AppTest`. Every page and every topic renders. Answering an MCQ updates the dashboard. Coding exercises cover check, hint and the print-vs-return feedback. Also covers lesson examples, lesson completion, quiz submission, sandbox error explanations, project step checks and the review page. |

The tests use a temporary `PYLEARN_DATA_DIR`, so they never touch your real
progress.

## Course outline

| # | Topic | Highlights |
|---|---|---|
| 1 | Introduction & Programming Basics | How programs run, `print`, variables, the four basic types, `input()` always returns `str`, f-strings |
| 2 | Operators & Debugging | `/` vs `//` vs `%`, precedence, `==` vs `=`, the `or` trap, reading tracebacks, a debugging routine |
| 3 | Control Flow | `if`/`elif` ordering, truthiness, `for` and `range` in depth, the accumulator pattern, `enumerate`/`zip`, nested loops, `while`, `break`/`continue`, infinite loops |
| 4 | Functions | Parameters vs arguments, defaults and keywords, **return vs print in depth** (`None`, early return, returning tuples), scope, docstrings, composing functions, `lambda` |
| 5 | Data Types | Strings and indexing, **slicing in depth**, **lists** (mutation, `.sort()` returning `None`, aliasing, comprehensions), **tuples** (immutability, `(5,)`, unpacking), **dictionaries** (`.get`, counting and grouping patterns, lists of dicts as rows), sets |
| 6 | File Input & Output | `with open`, modes, line-by-line reading, `csv`, `json`, `try`/`except` |
| 7 | SQL (5 lessons) | SQLite from Python, `SELECT`/`WHERE`/`ORDER BY`/`LIMIT`, `LIKE`/`IN`/`NULL`, aggregates, `GROUP BY` and `HAVING` vs `WHERE`, `INNER` and `LEFT JOIN`, `COUNT(*)` vs `COUNT(col)`, **SQL injection and `?` placeholders**, `pd.read_sql_query` |
| 8 | Data Preparation | DataFrames, inspection, boolean filtering, missing values (drop, fill or impute), duplicates, `.str` cleaning, `to_numeric(errors="coerce")`, dates, derived columns, a cleaning pipeline function |
| 9 | Descriptive Analysis | Mean, median and mode, skew, std and variance, quartiles and the IQR outlier rule, `describe`, `value_counts`, `groupby`/`agg`, pivot tables, correlation vs causation |
| 10 | Data Visualisation | Figure and axes, anatomy of a good chart, choosing line, bar, histogram, scatter or box plot, honest axes, pandas `.plot`, subplots, saving |

**Mini-projects**

1. ☕ **Coffee shop sales.** Messy till export, then cleaning (whitespace, case,
   `£` prices, missing values, duplicates), then revenue analysis and weekend
   share, then a two-panel chart.
2. 🏫 **School results database.** A three-table SQLite database: `COUNT`,
   `JOIN` + `GROUP BY`, top performers with `HAVING COUNT(*) = 4`, and pass
   rates in pandas with a bar chart.
3. 🍦 **Weather and ice-cream sales.** Parse dates, interpolate missing sensor
   readings, compute rolling and monthly averages and correlations, then tell
   the story in a chart.

Each project's dataset is generated by deterministic code inside the sandbox,
so expected answers are identical on every machine.

## Architecture

```
app.py                       Streamlit entry point: sidebar, navigation, the 6 pages
pylearn/
├── ui.py                    Reusable widgets: code runner, exercise cards, feedback display
├── sandbox.py               Parent side: static AST policy, launches the child process, parses results
├── sandbox_runner.py        Child side (separate interpreter): rlimits, preload, audit-hook policy,
│                            executes code, evaluates checks, captures prints and charts
├── grading.py               Grades MCQ / predict / code answers and writes beginner-friendly feedback
├── explain.py               Rule table mapping exception type + message to an explanation
├── progress.py              SQLite store: attempts, SM-2 reviews, lessons, project steps;
│                            mastery, recommendations, tag accuracy, streaks
└── content/
    ├── models.py            Immutable dataclasses: Topic, Lesson, Example, MCQ, PredictOutput,
    │                        DebugExercise, CodingExercise, Check, Project, ProjectStep
    ├── t01_basics.py …      One module per topic (content as data)
    ├── t10_visualisation.py
    ├── projects.py          The 3 mini-projects and their dataset generators
    └── __init__.py          Registry: TOPICS, PROJECTS, get_item, all_tags …
tests/                       pytest suite (see above)
.streamlit/config.toml       Theme
```

**Data flow for a coding exercise:**

```
learner code ──► grading.grade_code ──► sandbox.run_code
                                           │ 1. static_check (AST)  ──► rejected? friendly message
                                           │ 2. spawn: python -E sandbox_runner.py   (empty temp dir,
                                           │    scrubbed env, wall-clock timeout)
                                           ▼
                                   sandbox_runner (child)
                                     rlimits → preload libs → install audit hook (irremovable)
                                     → run setup/prelude (hidden) → exec learner code (stdout captured)
                                     → evaluate each Check in the learner's namespace
                                     → save matplotlib figures as PNG
                                     → print nonce-prefixed JSON result
                                           │
grading.feedback_from_run ◄── RunResult ◄──┘
  explain errors / per-check ✔/✖ / print-vs-return & wrong-type detection
        │
        ▼
progress.record_attempt  → attempts table + SM-2 update → mastery & recommendations
ui.show_feedback         → rendered in Streamlit
```

Design choices:

* **Content is data.** Lessons and exercises are frozen dataclasses in plain
  Python modules. Nothing is hard-coded in the UI, and the test-suite can check
  every item automatically.
* **Learner code never runs in the Streamlit process.** Each run is a fresh
  interpreter, so learner code can't corrupt the app's state, and every run
  starts from a clean state.
* **Checks run inside the sandbox**, in the learner's namespace. Their results
  come back as JSON-safe values: tuples become lists, numpy scalars become
  Python numbers, and NaN becomes a string. Checks can test return values,
  types, printed output and charts (for example
  `ax.get_title()` or `len(ax.patches)`).
* **Only the standard library is used for logic** (sqlite3, ast, subprocess).
  The runtime dependencies are Streamlit, pandas, numpy and matplotlib.

## Sandbox security model

Learner code is **never executed unsandboxed**. Several independent layers
protect the machine:

1. **Static policy** (`sandbox.static_check`). The code is parsed with `ast`
   before anything runs. It is rejected if it imports dangerous modules
   (`subprocess`, `socket`, `ctypes`, `sys`, `importlib`, `shutil`,
   `multiprocessing`…), calls `eval`, `exec`, `compile`, `__import__`,
   `getattr` and similar, or accesses dunder attributes such as
   `__subclasses__`, `__globals__`, `__builtins__` and frame or traceback
   attributes.
2. **Process isolation.** The code runs in a **separate Python process**
   (`python -E`, ignoring `PYTHON*` environment variables). It starts with a
   **minimal environment** (no inherited secrets or tokens) and its working
   directory is a **fresh, empty temporary folder** that is deleted afterwards.
3. **Resource limits** (POSIX `setrlimit`): CPU seconds, about 1.5 GB of
   address space, 5 MB maximum file size, a limit on open files, and no core
   dumps. The parent also enforces a **wall-clock timeout** (10 s by default)
   and kills the process.
4. **Runtime policy** using a PEP 578 **audit hook**, which can't be removed
   once installed. It blocks process creation (`subprocess`, `os.system`,
   `os.exec*`, `posix_spawn`, `fork`), all sockets, ctypes, `os.chdir`,
   symlinks, `sqlite3` extension loading and importing blocked modules. File
   writes, deletes and renames are allowed only inside the temp folder. File
   reads are allowed only inside the temp folder and the Python installation.
   SQLite databases can be opened only in the temp folder, and the raw
   stdin/stdout/stderr descriptors can't be reopened. This layer catches tricks
   that get past the static check, such as `os.__dict__['system']`, and the
   tests verify this.
5. **Output limits.** Captured stdout is capped at 20,000 characters, and at
   most 4 figures are returned. Results are read only from a line prefixed by
   a random per-run nonce, so printing fake results has no effect.

## How progress, mastery and spaced repetition work

* **Attempts.** Every graded answer (in practice, quiz, review, drill or
  projects) is logged with its correctness and source.
* **Item score.** An exponentially weighted average of attempts with α = 0.5,
  so recent answers count most. Wrong then right gives 0.5, and one more right
  answer gives 0.75.
* **Topic mastery (0–100)** = 20% share of lessons marked complete + 80% mean
  item score. Unattempted items count as 0. Levels: *Learning* < 40 ≤
  *Developing* < 70 ≤ *Proficient* < 90 ≤ *Mastered*.
* **Spaced repetition (SM-2).** The answer quality is 5 for correct with no
  help, 3 for correct after a hint or straight after a mistake, and 1 for
  wrong. Intervals go 1 day, then 6 days, then interval × ease (ease starts at
  2.5, minimum 1.3). A wrong answer resets the interval to 1 day and counts as
  a lapse.
* **Recommendations**, in priority order: due reviews, weak topics (started
  but with mastery below 60 or accuracy below 60%), weak concept tags (at least
  2 attempts and below 60% accuracy), then the next topic whose prerequisites
  have mastery of at least 40. Once everything is at least 70, a project is
  suggested.

## Adding or editing content

Add items to the `ITEMS` tuple of a topic module (for example
`pylearn/content/t04_functions.py`):

```python
CodingExercise(
    "t04.code.my_new_one",                       # id: "<topic>.<kind>.<name>"
    "Write `half(n)` that returns n / 2.",       # prompt (Markdown)
    "def half(n):\n    ...\n",                   # starter code
    "def half(n):\n    return n / 2",            # reference solution
    (Check("half(3) == 1.5", expr="half(3)", expected=1.5),),
    "Explanation shown after answering.",
    hints=("Use return.",), tags=("functions", "return-vs-print"),
)
```

Then run `python -m pytest tests/test_content.py`. The tests fail if the
solution doesn't pass its checks, if the starter accidentally passes, or if a
predict-the-output answer key is wrong.

## Limitations

These are known limitations, stated plainly:

* **The sandbox is a strong local sandbox, not a security boundary for
  hostile, internet-facing use.** Audit hooks and AST checks are
  defence-in-depth inside CPython. A determined attacker who finds an
  interpreter bug or an unaudited native code path could escape them. They are
  appropriate for a personal or classroom app on your own machine. **To host
  PyLearn publicly for untrusted users**, also run the app (or just
  `sandbox_runner.py`) inside an OS-level jail: a container without network
  access and with a read-only filesystem, gVisor or Firecracker, or nsjail or
  bubblewrap. Also run it as an unprivileged user.
* **Resource limits are POSIX-only.** On Windows, `resource.setrlimit` isn't
  available. The wall-clock timeout and the audit-hook policy still apply, but
  the CPU, memory and file-size caps don't.
* The policy allows reading files inside the Python installation, which is
  needed to import libraries. Learner code can therefore read library source
  files, but nothing outside the installation or the temp folder.
* The safety rules are deliberately strict. A few harmless but unusual things,
  such as `getattr()`, dunder attributes, or `import sys`, are refused with an
  explanation. Nothing in the course needs them.
* **Automatic checks test behaviour on specific inputs.** Passing them doesn't
  prove a solution is correct in every case. A learner who wants to cheat can
  hard-code answers.
* **Predict-the-output grading** compares text after trimming trailing spaces
  and blank lines. Answers that are equivalent but formatted differently, such
  as extra spaces inside a line, are marked wrong, but the hints point out
  spacing differences.
* **Progress is local** to one machine and one SQLite file. There are no
  accounts, passwords or cloud sync, and anyone using the same computer can
  pick any profile.
* **One run takes about 0.1 s for plain Python and about 1 s when pandas or
  matplotlib are used**, because each run starts a fresh interpreter. Variables
  don't persist between runs (unlike a Jupyter notebook). Project steps instead
  silently re-run the previous steps' reference solutions.
* The code editor is a plain text area. It has no syntax highlighting or
  autocompletion while typing, which keeps the dependencies minimal.
* Some pandas output (such as `df.dtypes` and `info()` formatting) differs
  slightly between pandas versions. The answer keys are checked against the
  installed version by the test-suite, so run the tests after upgrading pandas.
