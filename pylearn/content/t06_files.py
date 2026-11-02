from .models import (MCQ, Check as C, CodingExercise, DebugExercise, Example as E,
                     Lesson, Option as O, PredictOutput, Topic)

L1 = Lesson(
    id="t06.l1",
    title="Reading and writing text files",
    body="""
Data lives in files. Python's built-in `open()` gives you a *file object*.
Always use a **`with` block** — it closes the file automatically, even if an
error happens:

```python
with open("notes.txt", "w") as f:      # "w" = write (creates / OVERWRITES)
    f.write("first line\\n")
    f.write("second line\\n")

with open("notes.txt") as f:           # default mode "r" = read
    text = f.read()                    # the whole file as one string
```

| Mode | Meaning |
|---|---|
| `"r"` | read (default). Error if the file doesn't exist. |
| `"w"` | write. Creates the file or **erases** an existing one! |
| `"a"` | append to the end. |
| `"x"` | create; error if it already exists. |

### Reading line by line
```python
with open("notes.txt") as f:
    for line in f:              # memory-friendly for big files
        print(line.strip())     # strip() removes the trailing "\\n"
```
`f.readlines()` returns a list of lines (each still ending in `"\\n"`).

### Important details
* `write()` does **not** add a newline — include `"\\n"` yourself.
* `write()` needs a string: `f.write(str(42))`.
* Pass `encoding="utf-8"` when sharing files across computers.

> In this app's sandbox, every run gets its own fresh, empty folder, so files
> you create exist only during that run.
""",
    examples=(
        E("Write then read", 'with open("notes.txt", "w") as f:\n    f.write("first line\\n")\n    f.write("second line\\n")\n\nwith open("notes.txt") as f:\n    text = f.read()\nprint(repr(text))\nprint(text)'),
        E("Line by line", 'with open("temps.txt", "w") as f:\n    for t in [12.5, 14.0, 9.8]:\n        f.write(f"{t}\\n")\n\ntotal = 0\nwith open("temps.txt") as f:\n    for line in f:\n        total += float(line.strip())\nprint("Total:", total)'),
        E("Append mode", 'for i in range(3):\n    with open("log.txt", "a") as f:\n        f.write(f"run {i}\\n")\nwith open("log.txt") as f:\n    print(f.readlines())'),
    ),
    key_points=("Use `with open(...) as f:` so files close automatically.",
                "`'w'` overwrites, `'a'` appends, `'r'` reads.",
                "Lines end with `\\n`; use `.strip()` when reading."),
)

L2 = Lesson(
    id="t06.l2",
    title="CSV and JSON files",
    body="""
### CSV — comma-separated values
The most common format for tabular data. The `csv` module handles commas
inside quotes, so don't just use `line.split(",")`.

```python
import csv

with open("people.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["name", "age"])          # header
    writer.writerows([["Ana", 31], ["Ben", 25]])

with open("people.csv", newline="") as f:
    for row in csv.DictReader(f):             # each row → dict keyed by header
        print(row["name"], int(row["age"]))   # values are always strings!
```
> CSV values are read as **strings**. Convert numbers with `int()` / `float()`.

### JSON — nested data
JSON looks like Python dicts and lists, and is how web APIs exchange data.

```python
import json
config = {"model": "tree", "params": {"depth": 3}, "tags": ["v1"]}
with open("config.json", "w") as f:
    json.dump(config, f, indent=2)     # Python → file
with open("config.json") as f:
    loaded = json.load(f)              # file → Python
```
`json.dumps(obj)` / `json.loads(text)` do the same with strings.

In the Data Preparation topic you'll load CSVs with `pandas.read_csv`, which
converts types for you.
""",
    examples=(
        E("Writing and reading CSV", 'import csv\n\nwith open("people.csv", "w", newline="") as f:\n    writer = csv.writer(f)\n    writer.writerow(["name", "age", "city"])\n    writer.writerows([["Ana", 31, "Leeds"], ["Ben", 25, "York, UK"]])\n\nwith open("people.csv") as f:\n    print(f.read())\n\nwith open("people.csv", newline="") as f:\n    for row in csv.DictReader(f):\n        print(row["name"], int(row["age"]) + 1, row["city"])',
          "Notice `York, UK` is quoted in the file so its comma doesn't split the column."),
        E("JSON round trip", 'import json\nconfig = {"model": "tree", "params": {"depth": 3}, "tags": ["v1", "test"]}\nwith open("config.json", "w") as f:\n    json.dump(config, f, indent=2)\nwith open("config.json") as f:\n    print(f.read())\nwith open("config.json") as f:\n    loaded = json.load(f)\nprint(loaded["params"]["depth"], loaded == config)'),
    ),
    key_points=("Use the `csv` module for CSV files.", "CSV values are strings until converted.",
                "`json.dump`/`json.load` save and load nested data."),
)

L3 = Lesson(
    id="t06.l3",
    title="Handling errors: try / except",
    body="""
Files go missing, data is messy. Instead of crashing, handle expected errors:

```python
try:
    with open("missing.txt") as f:
        data = f.read()
except FileNotFoundError:
    print("File not found — using defaults")
    data = ""
```

* Put only the risky lines inside `try`.
* Catch **specific** exceptions (`FileNotFoundError`, `ValueError`). A bare
  `except:` hides real bugs, including typos.
* `else:` runs if no error occurred; `finally:` always runs.

### Cleaning messy numeric data
```python
raw = ["12", "7.5", "n/a", "", "30"]
values, bad = [], 0
for r in raw:
    try:
        values.append(float(r))
    except ValueError:
        bad += 1
```
This is the plain-Python version of what `pd.to_numeric(..., errors="coerce")`
does for you later.
""",
    examples=(
        E("Missing file", 'try:\n    with open("missing.txt") as f:\n        data = f.read()\nexcept FileNotFoundError as err:\n    print("Problem:", err)\n    data = ""\nprint("Continuing with", repr(data))'),
        E("Skipping bad values", 'raw = ["12", "7.5", "n/a", "", "30"]\nvalues, bad = [], 0\nfor r in raw:\n    try:\n        values.append(float(r))\n    except ValueError:\n        bad += 1\nprint(values, "bad:", bad)'),
        E("else and finally", 'for text in ["42", "forty-two"]:\n    try:\n        n = int(text)\n    except ValueError:\n        print(text, "-> not a number")\n    else:\n        print(text, "-> ok", n)\n    finally:\n        print("checked", text)'),
    ),
    key_points=("`try`/`except` handles expected errors.", "Catch specific exception types.",
                "Count and report bad records rather than silently dropping them."),
)

ITEMS = (
    MCQ("t06.mcq.mode_w", "What happens when you open an existing file with mode `\"w\"`?",
        (O("Its contents are erased and replaced", True, "`'w'` truncates the file. Use `'a'` to add to it."),
         O("New text is added to the end", False, "That's append mode, `'a'`."),
         O("An error is raised", False, "That's mode `'x'`, which refuses to overwrite."),
         O("It opens read-only", False, "Read mode is `'r'`.")),
        "`'w'` overwrites; `'a'` appends; `'x'` refuses to overwrite.", tags=("files",)),
    MCQ("t06.mcq.with", "Why use `with open(...) as f:`?",
        (O("The file is closed automatically, even if an error occurs", True, ""),
         O("It makes reading faster", False, "Speed isn't the point; safe cleanup is."),
         O("It's required to read a file", False, "You can call `open()` and `f.close()` manually — "
           "but it's easy to forget the close, especially when errors happen."),
         O("It converts the file to a list", False, "It just manages opening and closing.")),
        "Context managers guarantee cleanup.", tags=("files",)),
    MCQ("t06.mcq.csv_types", "Reading a CSV with `csv.DictReader`, what's the type of `row['age']`?",
        (O("`str`", True, "The csv module never converts types: everything is text."),
         O("`int`", False, "It *looks* like a number in the file, but csv returns strings; call `int()`."),
         O("It depends on the value", False, "csv doesn't inspect values; they're always strings."),
         O("`float`", False, "No automatic conversion happens.")),
        "Convert CSV fields yourself, or use pandas which infers types.", tags=("files", "csv", "types")),
    MCQ("t06.mcq.bare_except", "Why is `except:` (with no exception type) usually a bad idea?",
        (O("It hides unexpected bugs such as typos", True, "It catches *everything*, including "
           "NameErrors from misspelled variables, so real bugs go unnoticed."),
         O("It's a syntax error", False, "It's valid syntax, which is why it's tempting."),
         O("It catches nothing", False, "It catches every exception."),
         O("It makes the program slower", False, "Performance isn't the issue.")),
        "Catch only the errors you expect and know how to handle.", tags=("errors",)),
    PredictOutput("t06.pred.write_read", "What does this code print?",
                  "with open('a.txt', 'w') as f:\n    f.write('one')\n    f.write('two')\nwith open('a.txt') as f:\n    print(f.read())",
                  "onetwo",
                  "`write()` doesn't add newlines, so the two strings are stuck together.",
                  tags=("files",),
                  common_wrong=(("one\ntwo", "`write()` does not add a line break the way `print()` "
                                 "does. You must write `'\\n'` yourself."),)),
    PredictOutput("t06.pred.lines", "What does this code print?",
                  "with open('n.txt', 'w') as f:\n    f.write('3\\n4\\n5\\n')\nwith open('n.txt') as f:\n    lines = f.readlines()\nprint(len(lines))\nprint(sum(int(x) for x in lines))",
                  "3\n12",
                  "There are three lines; `int()` ignores the surrounding whitespace/newline.",
                  tags=("files",)),
    PredictOutput("t06.pred.try", "What does this code print?",
                  "for v in ['5', 'x', '7']:\n    try:\n        print(int(v) * 2)\n    except ValueError:\n        print('skip')",
                  "10\nskip\n14",
                  "The error for `'x'` is caught, so the loop continues with `'7'`.",
                  tags=("errors",)),
    DebugExercise("t06.dbg.newline", "This should write three names, one per line, so the file reads "
                  "`Ana\\nBen\\nCy\\n`. Fix it.",
                  "names = ['Ana', 'Ben', 'Cy']\nwith open('names.txt', 'w') as f:\n    for n in names:\n        f.write(n)\nwith open('names.txt') as f:\n    content = f.read()",
                  "names = ['Ana', 'Ben', 'Cy']\nwith open('names.txt', 'w') as f:\n    for n in names:\n        f.write(n + '\\n')\nwith open('names.txt') as f:\n    content = f.read()",
                  (C("File content is one name per line", expr="content", expected="Ana\nBen\nCy\n"),),
                  "`write()` writes exactly what you give it — add `'\\n'` to end each line.",
                  hints=("Does `write()` add line breaks?",), tags=("files",)),
    DebugExercise("t06.dbg.csv_sum", "This should total the `amount` column (`57.5`) but crashes. Fix it.",
                  "import csv\nwith open('t.csv', 'w', newline='') as f:\n    csv.writer(f).writerows([['item', 'amount'], ['tea', '2.5'], ['cake', '55']])\n\ntotal = 0\nwith open('t.csv', newline='') as f:\n    for row in csv.DictReader(f):\n        total += row['amount']",
                  "import csv\nwith open('t.csv', 'w', newline='') as f:\n    csv.writer(f).writerows([['item', 'amount'], ['tea', '2.5'], ['cake', '55']])\n\ntotal = 0\nwith open('t.csv', newline='') as f:\n    for row in csv.DictReader(f):\n        total += float(row['amount'])",
                  (C("total == 57.5", expr="total", expected=57.5),),
                  "CSV values are strings; `0 + '2.5'` is a TypeError. Convert with `float()`.",
                  hints=("What type is `row['amount']`?",), tags=("files", "csv", "types")),
    CodingExercise("t06.code.save_load", "Write `save_scores(path, scores)` that writes a dict like "
                   "`{'Ana': 81}` to a CSV with header `name,score`, and `load_scores(path)` that reads it back "
                   "into a dict with **int** scores.",
                   "import csv\n\ndef save_scores(path, scores):\n    ...\n\ndef load_scores(path):\n    ...\n",
                   "import csv\n\ndef save_scores(path, scores):\n    with open(path, 'w', newline='') as f:\n        w = csv.writer(f)\n        w.writerow(['name', 'score'])\n        for name, score in scores.items():\n            w.writerow([name, score])\n\ndef load_scores(path):\n    with open(path, newline='') as f:\n        return {r['name']: int(r['score']) for r in csv.DictReader(f)}",
                   (C("Round trip preserves data", expr="(save_scores('s.csv', {'Ana': 81, 'Ben': 67}), load_scores('s.csv'))[1]", expected={"Ana": 81, "Ben": 67}),
                    C("Header line is name,score", expr="(save_scores('h.csv', {'X': 1}), open('h.csv').readline().strip())[1]", expected="name,score")),
                   "Writing and re-reading data is how you check a save function works.",
                   hints=("Use `csv.writer` and `csv.DictReader`.", "Convert scores back with `int()`."),
                   tags=("files", "csv", "dicts")),
    CodingExercise("t06.code.safe_mean", "Write `safe_mean(texts)` that converts each string to a float, "
                   "skips values that can't be converted, and returns the mean of the valid ones "
                   "(or `None` if there are none).",
                   "def safe_mean(texts):\n    ...\n",
                   "def safe_mean(texts):\n    vals = []\n    for t in texts:\n        try:\n            vals.append(float(t))\n        except ValueError:\n            pass\n    return sum(vals) / len(vals) if vals else None",
                   (C("Skips bad values", expr="safe_mean(['4', 'x', '8'])", expected=6.0),
                    C("All bad → None", expr="safe_mean(['n/a', ''])", expected=None),
                    C("Decimals", expr="safe_mean(['1.5', '2.5'])", expected=2.0)),
                   "Catching `ValueError` lets you skip messy entries.",
                   hints=("Wrap `float(t)` in try/except ValueError.",), tags=("errors", "functions")),
)

TOPIC = Topic(
    id="t06", number=6, title="File Input & Output", icon="📁",
    summary="Reading/writing text, CSV and JSON files; with-blocks; try/except error handling.",
    lessons=(L1, L2, L3), items=ITEMS, prerequisites=("t05",),
)
