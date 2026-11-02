from .models import (MCQ, Check as C, CodingExercise, DebugExercise, Example as E,
                     Lesson, Option as O, PredictOutput, Topic)

L1 = Lesson(
    id="t10.l1",
    title="matplotlib basics: figures, axes and line charts",
    body="""
**matplotlib** is Python's foundational plotting library (pandas and seaborn
are built on it). The recommended style creates a **figure** (the whole image)
and one or more **axes** (individual plots):

```python
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(6, 3))
ax.plot(months, sales, marker="o", label="2024")
ax.set_title("Monthly sales")       # every chart needs a title...
ax.set_xlabel("Month")              # ...and labelled axes (with units!)
ax.set_ylabel("Sales (£k)")
ax.legend()
plt.show()
```

### Anatomy of a good chart
1. A **title** that states what the chart shows (or even the conclusion).
2. **Axis labels with units**.
3. A **legend** when there's more than one series.
4. No clutter: remove what doesn't help the reader.

**Line charts** are for values that change over a continuous dimension,
usually **time**.

> In this app, charts you create are captured and displayed below your code
> automatically; `plt.show()` is optional.
""",
    examples=(
        E("A labelled line chart", "import matplotlib.pyplot as plt\nmonths = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']\nsales = [12, 15, 14, 19, 23, 21]\nlast_year = [10, 11, 13, 14, 17, 18]\nfig, ax = plt.subplots(figsize=(6, 3))\nax.plot(months, sales, marker='o', label='2024')\nax.plot(months, last_year, linestyle='--', label='2023')\nax.set_title('Monthly sales grew every quarter')\nax.set_xlabel('Month')\nax.set_ylabel('Sales (£k)')\nax.legend()\nplt.show()"),
        E("A bad chart (spot the problems)", "import matplotlib.pyplot as plt\nfig, ax = plt.subplots(figsize=(6, 3))\nax.plot([3, 1, 4, 1, 5, 9, 2, 6])\nax.plot([2, 7, 1, 8, 2, 8, 1, 8])",
          "No title, no labels, no legend: what is this showing? Fix it."),
    ),
    key_points=("`fig, ax = plt.subplots()` then call methods on `ax`.",
                "Always add a title and axis labels with units.", "Line charts suit time series."),
)

L2 = Lesson(
    id="t10.l2",
    title="Choosing the right chart: bar, histogram, scatter, box",
    body="""
| Question | Chart | matplotlib |
|---|---|---|
| How does a value change over time? | line | `ax.plot(x, y)` |
| How do categories compare? | bar | `ax.bar(categories, values)` / `ax.barh(...)` |
| What's the distribution of one numeric variable? | histogram | `ax.hist(values, bins=20)` |
| Are two numeric variables related? | scatter | `ax.scatter(x, y)` |
| How do distributions compare across groups? | box plot | `ax.boxplot([g1, g2])` |

### Honest charts
* **Bar charts must start at zero** — bar length encodes the value, so a
  truncated axis exaggerates differences.
* Sort bars by value unless the categories have a natural order.
* Avoid pie charts with many slices; a sorted bar chart is easier to read.
* Use colour to highlight, not decorate.

### Histograms and bins
The number of `bins` changes the story: too few hides shape, too many adds
noise. Try a few values.
""",
    examples=(
        E("Sorted bar chart", "import matplotlib.pyplot as plt\nlangs = {'Python': 68, 'SQL': 52, 'R': 21, 'Java': 30}\nitems = sorted(langs.items(), key=lambda kv: kv[1])\nnames = [k for k, v in items]\nvalues = [v for k, v in items]\nfig, ax = plt.subplots(figsize=(6, 3))\nax.barh(names, values, color='tab:blue')\nax.set_title('Languages used by data scientists (%)')\nax.set_xlabel('% of respondents')\nplt.show()"),
        E("Histogram", "import matplotlib.pyplot as plt\nimport random\nrandom.seed(1)\nheights = [random.gauss(170, 8) for _ in range(500)]\nfig, ax = plt.subplots(figsize=(6, 3))\nax.hist(heights, bins=25, edgecolor='white')\nax.set_title('Distribution of heights')\nax.set_xlabel('Height (cm)')\nax.set_ylabel('Number of people')\nplt.show()",
          "Change `bins` to 5 and then 100 and compare."),
        E("Scatter plot", "import matplotlib.pyplot as plt\nhours = [1, 2, 3, 4, 5, 6, 7, 8]\nscore = [52, 55, 61, 64, 70, 72, 79, 83]\nfig, ax = plt.subplots(figsize=(5, 3))\nax.scatter(hours, score)\nax.set_title('More study, higher scores')\nax.set_xlabel('Hours studied')\nax.set_ylabel('Exam score (%)')\nplt.show()"),
        E("Box plot", "import matplotlib.pyplot as plt\nteam_a = [52, 61, 58, 70, 66, 59, 63]\nteam_b = [45, 80, 50, 91, 39, 72, 60]\nfig, ax = plt.subplots(figsize=(5, 3))\nax.boxplot([team_a, team_b])\nax.set_xticks([1, 2], ['Team A', 'Team B'])\nax.set_title('Similar medians, very different spread')\nax.set_ylabel('Score')\nplt.show()"),
    ),
    key_points=("Line → time; bar → categories; histogram → distribution; scatter → relationship.",
                "Bar charts start at zero.", "Experiment with histogram bins."),
)

L3 = Lesson(
    id="t10.l3",
    title="Plotting with pandas and multi-panel figures",
    body="""
pandas objects have a `.plot()` method that wraps matplotlib:
```python
df.plot(x="month", y="sales", kind="line", ax=ax)
df["region"].value_counts().plot(kind="bar", ax=ax)
df.groupby("region")["revenue"].sum().sort_values().plot.barh(ax=ax)
df["price"].plot.hist(bins=20, ax=ax)
```
Passing `ax=ax` puts the plot on an axes you created, so you can still set
titles and labels.

### Several charts in one figure
```python
fig, axes = plt.subplots(1, 2, figsize=(10, 3))   # 1 row, 2 columns
axes[0].hist(values)
axes[1].scatter(x, y)
fig.suptitle("Overview")
fig.tight_layout()
```
`axes` is an array — index it like a list.

### Saving charts
`fig.savefig("chart.png", dpi=150, bbox_inches="tight")` writes a file you can
put in a report.
""",
    examples=(
        E("pandas .plot()", "import pandas as pd\nimport matplotlib.pyplot as plt\nsales = pd.DataFrame({'region': ['North', 'South', 'East', 'North', 'South', 'East'],\n                      'revenue': [30, 17.5, 36, 12, 37.5, 10]})\nfig, ax = plt.subplots(figsize=(5, 3))\nsales.groupby('region')['revenue'].sum().sort_values().plot.barh(ax=ax)\nax.set_title('Revenue by region')\nax.set_xlabel('Revenue (£)')\nplt.show()"),
        E("Two panels", "import matplotlib.pyplot as plt\nimport random\nrandom.seed(0)\nx = [random.uniform(0, 10) for _ in range(80)]\ny = [2 * v + random.gauss(0, 2) for v in x]\nfig, axes = plt.subplots(1, 2, figsize=(9, 3))\naxes[0].hist(x, bins=10)\naxes[0].set_title('Distribution of x')\naxes[1].scatter(x, y, s=12)\naxes[1].set_title('y against x')\nfig.suptitle('Exploratory overview')\nfig.tight_layout()\nplt.show()"),
    ),
    key_points=("`df.plot(kind=..., ax=ax)` plots straight from pandas.",
                "`plt.subplots(rows, cols)` makes multi-panel figures.", "`fig.savefig()` saves to a file."),
)

ITEMS = (
    MCQ("t10.mcq.chart_choice", "You want to show the distribution of 10,000 customers' ages. Which chart?",
        (O("Histogram", True, "Histograms show how a single numeric variable is distributed."),
         O("Line chart", False, "Line charts imply an ordered, continuous sequence like time."),
         O("Pie chart", False, "Ages aren't parts of a whole, and a pie with many slices is unreadable."),
         O("Scatter plot", False, "Scatter plots need two numeric variables.")),
        "Distribution of one variable → histogram (or box plot).", tags=("visualisation",)),
    MCQ("t10.mcq.bar_zero", "Why should a bar chart's value axis start at zero?",
        (O("Bar length encodes the value, so cutting the axis exaggerates differences", True, ""),
         O("matplotlib requires it", False, "matplotlib lets you set any limits — that's why you must "
           "choose carefully."),
         O("It makes the chart load faster", False, "It's about honesty, not speed."),
         O("Zero is always the mean", False, "Unrelated to the mean.")),
        "Truncated bar axes mislead readers.", tags=("visualisation",)),
    MCQ("t10.mcq.relationship", "Which chart best shows whether advertising spend relates to sales across 50 stores?",
        (O("Scatter plot", True, "Each store is a point (spend, sales); patterns reveal the relationship."),
         O("Bar chart", False, "50 bars of sales wouldn't show how sales relate to spend."),
         O("Histogram of sales", False, "That shows sales alone, not the relationship."),
         O("Pie chart", False, "Pies show composition, not relationships.")),
        "Two numeric variables → scatter plot.", tags=("visualisation",)),
    MCQ("t10.mcq.subplots", "`fig, axes = plt.subplots(2, 3)` — how do you draw on the bottom-right plot?",
        (O("`axes[1, 2].plot(...)`", True, "Row index 1 (second row), column index 2 (third column)."),
         O("`axes[2, 3].plot(...)`", False, "Indexes start at 0, so the maximum indexes are 1 and 2."),
         O("`axes[6].plot(...)`", False, "With several rows `axes` is a 2-D array; there's no index 6."),
         O("`fig.plot(...)`", False, "Figures don't have `.plot`; you draw on axes.")),
        "Axes arrays are indexed `[row, col]`, starting at 0.", tags=("visualisation", "indexing")),
    PredictOutput("t10.pred.bars", "What does this print?",
                  "import matplotlib.pyplot as plt\nfig, ax = plt.subplots()\nbars = ax.bar(['a', 'b', 'c'], [3, 5, 2])\nax.set_title('Counts')\nprint(len(bars))\nprint(ax.get_title())",
                  "3\nCounts",
                  "One bar per category; `get_title()` returns the title text.",
                  tags=("visualisation",)),
    PredictOutput("t10.pred.subplots_shape", "What does this print?",
                  "import matplotlib.pyplot as plt\nfig, axes = plt.subplots(2, 3)\nprint(axes.shape)\nprint(len(fig.axes))",
                  "(2, 3)\n6",
                  "`axes` is a 2×3 array — a shape tuple again — and the figure holds 6 axes.",
                  tags=("visualisation", "tuples")),
    DebugExercise("t10.dbg.labels", "This chart should have the title `Weekly visitors`, x label `Week` and "
                  "y label `Visitors`. It crashes. Fix it.",
                  "import matplotlib.pyplot as plt\nfig, ax = plt.subplots()\nax.plot([1, 2, 3, 4], [120, 135, 160, 150])\nax.title('Weekly visitors')\nax.xlabel('Week')\nax.ylabel('Visitors')",
                  "import matplotlib.pyplot as plt\nfig, ax = plt.subplots()\nax.plot([1, 2, 3, 4], [120, 135, 160, 150])\nax.set_title('Weekly visitors')\nax.set_xlabel('Week')\nax.set_ylabel('Visitors')",
                  (C("Title set", expr="ax.get_title()", expected="Weekly visitors"),
                   C("x label set", expr="ax.get_xlabel()", expected="Week"),
                   C("y label set", expr="ax.get_ylabel()", expected="Visitors")),
                  "`plt.title()` is the shortcut function, but axes objects use `set_title`, `set_xlabel`, `set_ylabel`.",
                  hints=("Axes methods start with `set_`.",), tags=("visualisation",)),
    DebugExercise("t10.dbg.hist_list", "This should draw a histogram of `ages` with 5 bins, but crashes. Fix it.",
                  "import matplotlib.pyplot as plt\nages = ['23', '35', '31', '44', '29', '52', '38']\nfig, ax = plt.subplots()\ncounts, edges, patches = ax.hist(ages + 5)",
                  "import matplotlib.pyplot as plt\nages = ['23', '35', '31', '44', '29', '52', '38']\nages = [int(a) for a in ages]\nfig, ax = plt.subplots()\ncounts, edges, patches = ax.hist(ages, bins=5)",
                  (C("5 bins", expr="len(patches)", expected=5),
                   C("All 7 ages counted", expr="int(sum(counts))", expected=7)),
                  "`ages + 5` tries to add a number to a list. The bin count goes in `bins=5`, and the "
                  "ages must be numbers, not strings.",
                  hints=("How do you tell `hist` the number of bins?", "Are the ages numbers?"),
                  tags=("visualisation", "types")),
    CodingExercise("t10.code.bar", "Create a bar chart of `revenue` by `region` on `ax` with the title "
                   "`Revenue by region` and y-label `Revenue (£)`. Bars should be sorted from highest to lowest.",
                   "import matplotlib.pyplot as plt\nrevenue = {'North': 67, 'South': 79, 'East': 46}\nfig, ax = plt.subplots()\n",
                   "import matplotlib.pyplot as plt\nrevenue = {'North': 67, 'South': 79, 'East': 46}\nfig, ax = plt.subplots()\nitems = sorted(revenue.items(), key=lambda kv: kv[1], reverse=True)\nax.bar([k for k, v in items], [v for k, v in items])\nax.set_title('Revenue by region')\nax.set_ylabel('Revenue (£)')",
                   (C("A chart was drawn", figure=True),
                    C("3 bars", expr="len(ax.patches)", expected=3),
                    C("Bars sorted high → low", expr="[round(p.get_height()) for p in ax.patches]", expected=[79, 67, 46]),
                    C("Title", expr="ax.get_title()", expected="Revenue by region"),
                    C("y label", expr="ax.get_ylabel()", expected="Revenue (£)")),
                   "Sorting bars makes ranking obvious at a glance.",
                   hints=("`sorted(revenue.items(), key=lambda kv: kv[1], reverse=True)`",),
                   tags=("visualisation", "dicts")),
    CodingExercise("t10.code.two_panel", "Make a figure with **two** side-by-side axes stored in `axes`: a "
                   "histogram of `temps` on the left (title `Distribution`) and a line chart of `temps` over "
                   "`days` on the right (title `Over time`).",
                   "import matplotlib.pyplot as plt\ndays = list(range(1, 11))\ntemps = [14, 16, 15, 18, 21, 19, 22, 24, 20, 23]\n",
                   "import matplotlib.pyplot as plt\ndays = list(range(1, 11))\ntemps = [14, 16, 15, 18, 21, 19, 22, 24, 20, 23]\nfig, axes = plt.subplots(1, 2, figsize=(9, 3))\naxes[0].hist(temps, bins=5)\naxes[0].set_title('Distribution')\naxes[1].plot(days, temps)\naxes[1].set_title('Over time')",
                   (C("Two axes", expr="len(axes)", expected=2),
                    C("Left title", expr="axes[0].get_title()", expected="Distribution"),
                    C("Right title", expr="axes[1].get_title()", expected="Over time"),
                    C("Left is a histogram", expr="len(axes[0].patches) > 0", expected=True),
                    C("Right has a line", expr="len(axes[1].lines)", expected=1)),
                   "Multi-panel figures let readers compare views of the same data.",
                   hints=("`fig, axes = plt.subplots(1, 2)`",), tags=("visualisation",)),
)

TOPIC = Topic(
    id="t10", number=10, title="Data Visualisation", icon="📈",
    summary="matplotlib figures and axes, choosing charts honestly, pandas plotting, multi-panel figures.",
    lessons=(L1, L2, L3), items=ITEMS, prerequisites=("t09",),
)
