"""Realistic Data Science mini-projects.

Each project has trusted ``setup_code`` that writes its dataset (CSV files or
an SQLite database) into the sandbox's private folder. Data is generated with
a tiny deterministic pseudo-random generator so the expected answers are the
same on every machine and Python version.

When a learner runs step *n*, the sandbox first (silently) runs the setup code
and the reference solutions of steps 1..n-1, so each step builds on the last.
"""

from .models import Check as C, Project, ProjectStep as S

_LCG = '''
def _lcg(seed):
    while True:
        seed = (seed * 1103515245 + 12345) % 2147483648
        yield seed // 65536
'''

# ----------------------------------------------------------------- coffee --
COFFEE_SETUP = _LCG + '''
import csv
_r = _lcg(2024)
_products = [("Espresso", 2.20), ("Latte", 3.10), ("Cappuccino", 3.00), ("Mocha", 3.40)]
_rows = []
for _day in range(1, 29):
    _date = f"2024-02-{_day:02d}"
    _weekend = _day % 7 in (3, 4)          # 3 Feb 2024 was a Saturday
    for _name, _price in _products:
        _qty = 8 + next(_r) % 18 + (12 if _weekend else 0)
        if _name == "Latte":
            _qty += 6
        _rows.append([_date, _name, f"£{_price:.2f}", str(_qty)])
for _i, _row in enumerate(_rows):
    if _i % 9 == 4:
        _row[1] = "  " + _row[1].lower() + " "
    if _i % 13 == 7:
        _row[3] = ""
_rows.append(list(_rows[5]))
_rows.append(list(_rows[40]))
with open("coffee_sales.csv", "w", newline="") as _f:
    _w = csv.writer(_f)
    _w.writerow(["date", "product", "price", "quantity"])
    _w.writerows(_rows)
'''

COFFEE = Project(
    id="p1",
    title="☕ Coffee shop sales analysis",
    story="""
You've been hired by a small café chain. The manager exported February's
till data to **`coffee_sales.csv`** and wants to know: *Which drinks earn the
most? What was the best day? Do weekends matter?*

The export is messy — just like real data: product names have inconsistent
spacing and capitals, prices are stored as text like `£3.10`, some quantities
are missing, and the till duplicated a couple of rows.

**Columns:** `date`, `product`, `price`, `quantity`
""",
    skills=("pandas", "data cleaning", "groupby", "matplotlib"),
    topics=("t06", "t08", "t09", "t10"),
    setup_code=COFFEE_SETUP,
    steps=(
        S("1. Load and inspect",
          "Load `coffee_sales.csv` into a DataFrame called `df`. Then store the number of rows in "
          "`n_rows` and the number of missing quantities in `n_missing_qty`. Print `df.head()` to look "
          "at the data.",
          "import pandas as pd\n\ndf = ...\nn_rows = ...\nn_missing_qty = ...\nprint(df.head())\n",
          "import pandas as pd\n\ndf = pd.read_csv('coffee_sales.csv')\nn_rows = len(df)\nn_missing_qty = int(df['quantity'].isna().sum())\nprint(df.head())\n",
          (C("df has the right number of rows", expr="n_rows", expected=114),
           C("n_missing_qty is correct", expr="int(n_missing_qty)", expected=9),
           C("df is a DataFrame", expr="type(df).__name__", expected="DataFrame")),
          hints=("`pd.read_csv('coffee_sales.csv')`", "`df['quantity'].isna().sum()`")),
        S("2. Clean the data",
          "Create `clean` from `df`:\n\n1. drop exact duplicate rows\n2. tidy `product` "
          "(strip spaces, Title Case)\n3. convert `price` to a float (remove the `£`)\n"
          "4. drop rows with a missing `quantity` (we can't guess sales)\n5. add "
          "`revenue = price * quantity`.",
          "clean = df.drop_duplicates().copy()\n# continue cleaning...\n",
          "clean = df.drop_duplicates().copy()\nclean['product'] = clean['product'].str.strip().str.title()\nclean['price'] = clean['price'].str.replace('£', '', regex=False).astype(float)\nclean = clean.dropna(subset=['quantity'])\nclean['revenue'] = clean['price'] * clean['quantity']\n",
          (C("Duplicates and missing quantities removed", expr="len(clean)", expected=103),
           C("Four tidy product names", expr="sorted(clean['product'].unique())", expected=["Cappuccino", "Espresso", "Latte", "Mocha"]),
           C("price is numeric", expr="float(clean['price'].max())", expected=3.4),
           C("Total revenue", expr="round(float(clean['revenue'].sum()), 2)", expected=6276.2),
           C("Original df untouched", expr="len(df)", expected=114)),
          hints=("`.str.strip().str.title()`", "`.str.replace('£', '', regex=False).astype(float)`",
                 "`dropna(subset=['quantity'])`")),
        S("3. Analyse",
          "Compute:\n\n* `revenue_by_product` — total revenue per product, **sorted highest first**\n"
          "* `best_product` — the name of the top product\n* `daily` — total revenue per `date`\n"
          "* `best_day` — the date with the highest revenue\n* `weekend_share` — the fraction of "
          "revenue earned on Saturdays and Sundays (convert `date` with `pd.to_datetime`; "
          "`.dt.dayofweek` is 5 or 6 at the weekend). Round to 3 decimals.",
          "revenue_by_product = ...\nbest_product = ...\ndaily = ...\nbest_day = ...\nweekend_share = ...\n",
          "revenue_by_product = clean.groupby('product')['revenue'].sum().sort_values(ascending=False)\nbest_product = revenue_by_product.index[0]\ndaily = clean.groupby('date')['revenue'].sum()\nbest_day = daily.idxmax()\nis_weekend = pd.to_datetime(clean['date']).dt.dayofweek >= 5\nweekend_share = round(clean.loc[is_weekend, 'revenue'].sum() / clean['revenue'].sum(), 3)\n",
          (C("best_product", expr="best_product", expected="Latte"),
           C("revenue_by_product is sorted descending", expr="revenue_by_product.is_monotonic_decreasing", expected=True),
           C("daily has one value per day", expr="len(daily)", expected=28),
           C("best_day", expr="str(best_day)[:10]", expected="2024-02-18"),
           C("weekend_share", expr="float(weekend_share)", expected=0.417, tolerance=0.001)),
          hints=("`groupby('product')['revenue'].sum().sort_values(ascending=False)`",
                 "`.idxmax()` gives the label of the largest value."),
          ),
        S("4. Visualise",
          "Make a figure with two side-by-side axes in `axes`: a **bar chart** of `revenue_by_product` "
          "(left) and a **line chart** of `daily` revenue (right). Give each a title and label the "
          "y-axes `Revenue (£)`. What does the line chart tell you about weekends?",
          "import matplotlib.pyplot as plt\nfig, axes = plt.subplots(1, 2, figsize=(11, 4))\n",
          "import matplotlib.pyplot as plt\nfig, axes = plt.subplots(1, 2, figsize=(11, 4))\naxes[0].bar(revenue_by_product.index, revenue_by_product.values)\naxes[0].set_title('Revenue by product')\naxes[0].set_ylabel('Revenue (£)')\naxes[1].plot(pd.to_datetime(daily.index), daily.values, marker='o')\naxes[1].set_title('Daily revenue, February 2024')\naxes[1].set_ylabel('Revenue (£)')\naxes[1].tick_params(axis='x', rotation=45)\nfig.tight_layout()\n",
          (C("A figure was drawn", figure=True),
           C("Left: 4 bars", expr="len(axes[0].patches)", expected=4),
           C("Right: a line", expr="len(axes[1].lines) >= 1", expected=True),
           C("Both have titles", expr="bool(axes[0].get_title()) and bool(axes[1].get_title())", expected=True),
           C("y-axis labelled", expr="axes[0].get_ylabel()", expected="Revenue (£)")),
          hints=("`axes[0].bar(revenue_by_product.index, revenue_by_product.values)`",)),
    ),
)

# ----------------------------------------------------------------- school --
SCHOOL_SETUP = _LCG + '''
import sqlite3
_r = _lcg(7)
_first = ["Ava", "Ben", "Chloe", "Dev", "Ella", "Finn", "Grace", "Hugo", "Isla", "Jack",
          "Kira", "Leo", "Maya", "Noah", "Orla", "Priya", "Quinn", "Ravi", "Sofia", "Theo",
          "Uma", "Vik", "Willa", "Xander", "Yara", "Zane", "Amir", "Bea", "Cal", "Dina"]
_subjects = ["Maths", "English", "Science", "Computing"]
_offset = {"Maths": -4, "English": 3, "Science": 0, "Computing": 6}
_conn = sqlite3.connect("school.db")
_conn.executescript("""
DROP TABLE IF EXISTS results; DROP TABLE IF EXISTS students; DROP TABLE IF EXISTS subjects;
CREATE TABLE students (id INTEGER PRIMARY KEY, name TEXT NOT NULL, year_group INTEGER);
CREATE TABLE subjects (id INTEGER PRIMARY KEY, name TEXT NOT NULL);
CREATE TABLE results (student_id INTEGER REFERENCES students(id),
                      subject_id INTEGER REFERENCES subjects(id), score INTEGER);
""")
for _i, _n in enumerate(_first, start=1):
    _conn.execute("INSERT INTO students VALUES (?, ?, ?)", (_i, _n, 10 + _i % 3))
for _j, _s in enumerate(_subjects, start=1):
    _conn.execute("INSERT INTO subjects VALUES (?, ?)", (_j, _s))
for _i in range(1, 31):
    _ability = 35 + next(_r) % 45
    for _j, _s in enumerate(_subjects, start=1):
        if (_i * _j) % 17 == 0:
            continue                      # some students missed an exam
        _score = max(0, min(100, _ability + _offset[_s] + next(_r) % 21 - 10))
        _conn.execute("INSERT INTO results VALUES (?, ?, ?)", (_i, _j, _score))
_conn.commit()
_conn.close()
'''

SCHOOL = Project(
    id="p2",
    title="🏫 School results database (SQL + pandas)",
    story="""
A school keeps exam results in an SQLite database, **`school.db`**, with three
related tables:

| table | columns |
|---|---|
| `students` | `id`, `name`, `year_group` |
| `subjects` | `id`, `name` |
| `results` | `student_id` → students.id, `subject_id` → subjects.id, `score` |

The head teacher asks: *How many students do we have? Which subjects score
best? Who are the top performers? What's each subject's pass rate (≥ 50)?*
Some students missed exams, so not everyone has four results.
""",
    skills=("SQL", "JOIN", "GROUP BY", "HAVING", "pandas", "matplotlib"),
    topics=("t07", "t09", "t10"),
    setup_code=SCHOOL_SETUP,
    steps=(
        S("1. Connect and explore",
          "Connect to `school.db` as `conn`. Use SQL to store the number of students in `n_students` "
          "(an int) and a list of subject names in alphabetical order in `subjects`.",
          "import sqlite3\nconn = sqlite3.connect('school.db')\nn_students = ...\nsubjects = ...\n",
          "import sqlite3\nconn = sqlite3.connect('school.db')\nn_students = conn.execute('SELECT COUNT(*) FROM students').fetchone()[0]\nsubjects = [row[0] for row in conn.execute('SELECT name FROM subjects ORDER BY name')]\n",
          (C("n_students", expr="n_students", expected=30),
           C("subjects", expr="subjects", expected=["Computing", "English", "Maths", "Science"])),
          hints=("`fetchone()[0]` gets the single value from a COUNT.", "`[row[0] for row in ...]`")),
        S("2. Average score per subject",
          "Store in `avg_by_subject` a list of `(subject_name, average_score)` tuples, with the average "
          "rounded to 1 decimal place in SQL (`ROUND(AVG(score), 1)`), ordered from highest average to "
          "lowest. You'll need to JOIN `results` with `subjects`.",
          "sql = '''\nSELECT ...\n'''\navg_by_subject = conn.execute(sql).fetchall()\n",
          "sql = '''\nSELECT s.name, ROUND(AVG(r.score), 1) AS avg_score\nFROM results r\nJOIN subjects s ON r.subject_id = s.id\nGROUP BY s.name\nORDER BY avg_score DESC\n'''\navg_by_subject = conn.execute(sql).fetchall()\n",
          (C("avg_by_subject", expr="avg_by_subject", expected=[["Computing", 65.1], ["English", 63.9], ["Science", 59.4], ["Maths", 57.9]]),),
          hints=("`JOIN subjects s ON r.subject_id = s.id`", "`GROUP BY s.name ORDER BY avg_score DESC`")),
        S("3. Top performers",
          "Store in `top5` the five students with the highest average score — **only counting "
          "students who sat all four exams** (use `HAVING COUNT(*) = 4`). Each row should be "
          "`(name, average)` with the average rounded to 1 decimal. Break ties by name.",
          "sql = '''\nSELECT ...\n'''\ntop5 = conn.execute(sql).fetchall()\n",
          "sql = '''\nSELECT st.name, ROUND(AVG(r.score), 1) AS avg_score\nFROM results r\nJOIN students st ON r.student_id = st.id\nGROUP BY st.id\nHAVING COUNT(*) = 4\nORDER BY avg_score DESC, st.name\nLIMIT 5\n'''\ntop5 = conn.execute(sql).fetchall()\n",
          (C("top5 has 5 rows", expr="len(top5)", expected=5),
           C("Correct top 5", expr="top5", expected=[["Finn", 80.5], ["Bea", 77.5], ["Cal", 74.0], ["Ben", 72.5], ["Ava", 72.3]])),
          hints=("GROUP BY the student, then HAVING COUNT(*) = 4.", "ORDER BY avg DESC, name, then LIMIT 5.")),
        S("4. Pass rates with pandas and a chart",
          "Load every result with its subject name into a DataFrame `df` using `pd.read_sql_query`. "
          "Compute `pass_rate`: a Series of the fraction of scores ≥ 50 per subject, sorted descending "
          "and rounded to 2 decimals. Then draw a bar chart of it on `ax` with a title.",
          "import pandas as pd\nimport matplotlib.pyplot as plt\ndf = pd.read_sql_query('''\nSELECT ...\n''', conn)\npass_rate = ...\nfig, ax = plt.subplots()\n",
          "import pandas as pd\nimport matplotlib.pyplot as plt\ndf = pd.read_sql_query('''\nSELECT s.name AS subject, r.score\nFROM results r JOIN subjects s ON r.subject_id = s.id\n''', conn)\npass_rate = (df['score'] >= 50).groupby(df['subject']).mean().round(2).sort_values(ascending=False)\nfig, ax = plt.subplots()\nax.bar(pass_rate.index, pass_rate.values)\nax.set_title('Pass rate by subject')\nax.set_ylabel('Share of scores ≥ 50')\nax.set_ylim(0, 1)\n",
          (C("df has every result", expr="len(df)", expected=116),
           C("pass_rate values", expr="pass_rate.to_dict()", expected={"Computing": 0.9, "English": 0.86, "Science": 0.76, "Maths": 0.69}),
           C("A chart was drawn", figure=True),
           C("4 bars", expr="len(ax.patches)", expected=4),
           C("Chart has a title", expr="bool(ax.get_title())", expected=True)),
          hints=("`(df['score'] >= 50)` is a boolean Series; its mean is the pass rate.",
                 "`.groupby(df['subject']).mean()`")),
    ),
)

# ---------------------------------------------------------------- weather --
WEATHER_SETUP = _LCG + '''
import csv, math
_r = _lcg(99)
_rows = []
for _d in range(91):                       # 1 April .. 30 June 2024
    _month = 4 if _d < 30 else (5 if _d < 61 else 6)
    _day = _d + 1 if _d < 30 else (_d - 29 if _d < 61 else _d - 60)
    _temp = 9 + _d * 0.12 + 4 * math.sin(_d / 4.0) + (next(_r) % 40) / 10 - 2
    _rain = max(0.0, (next(_r) % 120) / 10 - 6)
    _sales = max(0, round(15 + 7.5 * _temp - 3 * _rain + next(_r) % 30 - 15))
    _t = f"{_temp:.1f}" if _d % 11 != 5 else ""   # a faulty sensor
    _rows.append([f"2024-{_month:02d}-{_day:02d}", _t, f"{_rain:.1f}", _sales])
with open("weather_sales.csv", "w", newline="") as _f:
    _w = csv.writer(_f)
    _w.writerow(["date", "temp_c", "rain_mm", "ice_creams"])
    _w.writerows(_rows)
'''

WEATHER = Project(
    id="p3",
    title="🍦 Weather and ice-cream sales",
    story="""
A seaside kiosk recorded daily temperature, rainfall and ice-cream sales from
April to June in **`weather_sales.csv`**. The temperature sensor sometimes
failed, leaving gaps. The owner wants to know how strongly weather drives
sales so they can plan stock.

**Columns:** `date`, `temp_c`, `rain_mm`, `ice_creams`
""",
    skills=("pandas", "dates", "interpolation", "rolling averages", "correlation", "matplotlib"),
    topics=("t08", "t09", "t10"),
    setup_code=WEATHER_SETUP,
    steps=(
        S("1. Load and repair the data",
          "Load the CSV into `df` with the `date` column parsed as dates (`parse_dates=['date']`). "
          "Store the number of missing temperatures in `n_missing`, then fill the gaps with "
          "`df['temp_c'].interpolate()` (a straight line between neighbouring days).",
          "import pandas as pd\ndf = ...\nn_missing = ...\n",
          "import pandas as pd\ndf = pd.read_csv('weather_sales.csv', parse_dates=['date'])\nn_missing = int(df['temp_c'].isna().sum())\ndf['temp_c'] = df['temp_c'].interpolate()\n",
          (C("91 days loaded", expr="len(df)", expected=91),
           C("n_missing", expr="n_missing", expected=8),
           C("No gaps after interpolation", expr="int(df['temp_c'].isna().sum())", expected=0),
           C("Dates parsed", expr="str(df['date'].dtype).startswith('datetime64')", expected=True)),
          hints=("`pd.read_csv(..., parse_dates=['date'])`",)),
        S("2. Trends: rolling and monthly averages",
          "Add a column `rolling_7`: the 7-day rolling mean of `temp_c`. Then create `monthly`: the "
          "mean temperature per month (use `df['date'].dt.month`), rounded to 1 decimal.",
          "df['rolling_7'] = ...\nmonthly = ...\n",
          "df['rolling_7'] = df['temp_c'].rolling(7).mean()\nmonthly = df.groupby(df['date'].dt.month)['temp_c'].mean().round(1)\n",
          (C("rolling_7 starts with 6 NaNs", expr="int(df['rolling_7'].isna().sum())", expected=6),
           C("monthly averages", expr="monthly.to_dict()", expected={"4": 10.8, "5": 14.8, "6": 18.0}),
           C("June warmer than April", expr="bool(monthly[6] > monthly[4])", expected=True)),
          hints=("`.rolling(7).mean()`", "`df.groupby(df['date'].dt.month)['temp_c'].mean()`")),
        S("3. How much does weather matter?",
          "Compute `r_temp` (correlation of `temp_c` with `ice_creams`) and `r_rain` (correlation of "
          "`rain_mm` with `ice_creams`), each rounded to 2 decimals. Then `warm_avg`: mean sales on "
          "days with `temp_c >= 15`, and `cool_avg` for days below 15, both rounded to 1 decimal.",
          "r_temp = ...\nr_rain = ...\nwarm_avg = ...\ncool_avg = ...\nprint(r_temp, r_rain, warm_avg, cool_avg)\n",
          "r_temp = round(df['temp_c'].corr(df['ice_creams']), 2)\nr_rain = round(df['rain_mm'].corr(df['ice_creams']), 2)\nwarm_avg = round(df.loc[df['temp_c'] >= 15, 'ice_creams'].mean(), 1)\ncool_avg = round(df.loc[df['temp_c'] < 15, 'ice_creams'].mean(), 1)\nprint(r_temp, r_rain, warm_avg, cool_avg)\n",
          (C("r_temp", expr="float(r_temp)", expected=0.95, tolerance=0.006),
           C("r_rain", expr="float(r_rain)", expected=-0.12, tolerance=0.006),
           C("warm_avg", expr="float(warm_avg)", expected=150.5, tolerance=0.06),
           C("cool_avg", expr="float(cool_avg)", expected=95.3, tolerance=0.06)),
          hints=("`df['a'].corr(df['b'])`", "`df.loc[condition, 'ice_creams'].mean()`")),
        S("4. Tell the story with a chart",
          "Create `fig, axes = plt.subplots(1, 2, ...)`. Left: a **scatter** of temperature (x) against "
          "ice-cream sales (y). Right: a **line** of `temp_c` over `date` plus a second line for "
          "`rolling_7`, with a legend. Title and label everything.",
          "import matplotlib.pyplot as plt\nfig, axes = plt.subplots(1, 2, figsize=(11, 4))\n",
          "import matplotlib.pyplot as plt\nfig, axes = plt.subplots(1, 2, figsize=(11, 4))\naxes[0].scatter(df['temp_c'], df['ice_creams'], s=14)\naxes[0].set_title(f'Warmer days sell more (r = {r_temp})')\naxes[0].set_xlabel('Temperature (°C)')\naxes[0].set_ylabel('Ice creams sold')\naxes[1].plot(df['date'], df['temp_c'], alpha=0.5, label='daily')\naxes[1].plot(df['date'], df['rolling_7'], label='7-day average')\naxes[1].set_title('Temperature, April–June')\naxes[1].set_ylabel('Temperature (°C)')\naxes[1].legend()\naxes[1].tick_params(axis='x', rotation=45)\nfig.tight_layout()\n",
          (C("A figure was drawn", figure=True),
           C("Left is a scatter", expr="len(axes[0].collections) >= 1", expected=True),
           C("Right has two lines", expr="len(axes[1].lines)", expected=2),
           C("Right has a legend", expr="axes[1].get_legend() is not None", expected=True),
           C("Scatter axes labelled", expr="bool(axes[0].get_xlabel()) and bool(axes[0].get_ylabel())", expected=True)),
          hints=("`axes[0].scatter(x, y)`", "Pass `label=` to each `plot` call, then `axes[1].legend()`.")),
    ),
)

PROJECTS = (COFFEE, SCHOOL, WEATHER)


def get_project(project_id: str) -> Project:
    for p in PROJECTS:
        if p.id == project_id:
            return p
    raise KeyError(project_id)


def prelude_for(project: Project, step_index: int) -> str:
    """Reference solutions of the steps before ``step_index`` (0-based)."""
    return "\n".join(s.solution for s in project.steps[:step_index])
