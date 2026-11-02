from .models import (MCQ, Check as C, CodingExercise, DebugExercise, Example as E,
                     Lesson, Option as O, PredictOutput, Topic)

SALES = '''import pandas as pd
sales = pd.DataFrame({
    "region":  ["North", "South", "North", "East", "South", "East", "North", "South"],
    "product": ["A", "A", "B", "B", "A", "A", "A", "B"],
    "units":   [12, 7, 3, 9, 15, 4, 10, 6],
    "price":   [2.5, 2.5, 4.0, 4.0, 2.5, 2.5, 2.5, 4.0],
})
sales["revenue"] = sales["units"] * sales["price"]
'''

L1 = Lesson(
    id="t09.l1",
    title="Centre: mean, median and mode",
    body="""
**Descriptive statistics** summarise a dataset with a few numbers. The first
question is: *what's a typical value?*

| Measure | Definition | pandas | Sensitive to outliers? |
|---|---|---|---|
| **Mean** | sum ÷ count | `s.mean()` | **yes** |
| **Median** | middle value when sorted | `s.median()` | no |
| **Mode** | most frequent value | `s.mode()` | no |

```python
incomes = pd.Series([21, 23, 25, 26, 28, 30, 400])   # one billionaire-ish outlier
incomes.mean()     # 79.0  ← dragged up by 400
incomes.median()   # 26.0  ← a typical person
```
When mean ≫ median the data is **right-skewed** (a long tail of large values) —
common for incomes, house prices and website visits. Report the median for
skewed data.

The standard library also has these: `import statistics; statistics.median(xs)`.
""",
    examples=(
        E("Mean vs median", "import pandas as pd\nincomes = pd.Series([21, 23, 25, 26, 28, 30, 400])\nprint('mean  ', incomes.mean())\nprint('median', incomes.median())\nprint('without outlier:', incomes[incomes < 100].mean())"),
        E("Mode", "import pandas as pd\nshoe_sizes = pd.Series([7, 8, 8, 9, 8, 10, 7])\nprint(shoe_sizes.mode().tolist())\nprint(shoe_sizes.value_counts())"),
        E("statistics module (no pandas)", "import statistics\nxs = [3, 7, 7, 2, 9]\nprint(statistics.mean(xs), statistics.median(xs), statistics.mode(xs))"),
    ),
    key_points=("Mean is pulled by outliers; median isn't.", "Mean ≫ median signals right skew.",
                "Mode is the most frequent value — useful for categories."),
)

L2 = Lesson(
    id="t09.l2",
    title="Spread: range, variance, standard deviation, quartiles",
    body="""
Two datasets can share a mean but differ wildly in **spread**:

| Measure | pandas | Meaning |
|---|---|---|
| Range | `s.max() - s.min()` | total width (very outlier-sensitive) |
| Variance | `s.var()` | average squared distance from the mean |
| Standard deviation | `s.std()` | √variance, in the data's own units |
| Quartiles | `s.quantile([0.25, 0.5, 0.75])` | 25% / 50% / 75% points |
| IQR | `Q3 - Q1` | spread of the middle 50% (robust) |

> pandas' `.std()` uses the **sample** formula (divides by n − 1). NumPy's
> `np.std` divides by n unless you pass `ddof=1`. Both are "correct" — they
> answer slightly different questions — but know which you're using.

### Outliers with the IQR rule
A common rule flags values below `Q1 − 1.5 × IQR` or above `Q3 + 1.5 × IQR`.
This is exactly what box plots draw.

### describe() does it all at once
`df.describe()` prints count, mean, std, min, quartiles and max for every
numeric column — always run it on a new dataset.
""",
    examples=(
        E("Same mean, different spread", "import pandas as pd\na = pd.Series([49, 50, 51, 50, 50])\nb = pd.Series([10, 90, 30, 70, 50])\nprint(a.mean(), b.mean())\nprint(round(a.std(), 2), round(b.std(), 2))"),
        E("Quartiles and outliers", "import pandas as pd\ns = pd.Series([12, 14, 15, 15, 16, 18, 19, 21, 55])\nq1, q3 = s.quantile(0.25), s.quantile(0.75)\niqr = q3 - q1\nlow, high = q1 - 1.5 * iqr, q3 + 1.5 * iqr\nprint('Q1', q1, 'Q3', q3, 'IQR', iqr)\nprint('outliers:', s[(s < low) | (s > high)].tolist())"),
        E("describe()", SALES + "print(sales.describe().round(2))"),
    ),
    key_points=("Standard deviation measures typical distance from the mean.",
                "IQR is robust; the 1.5×IQR rule flags outliers.", "Run `describe()` on every new dataset."),
)

L3 = Lesson(
    id="t09.l3",
    title="Grouping, counting and correlation",
    body="""
### value_counts — frequencies of categories
```python
sales["region"].value_counts()                  # counts
sales["region"].value_counts(normalize=True)    # proportions
```

### groupby — statistics per group (split → apply → combine)
```python
sales.groupby("region")["revenue"].sum()
sales.groupby("region")["units"].agg(["count", "mean", "max"])
sales.groupby(["region", "product"])["revenue"].sum()
```
This is the pandas equivalent of SQL's `GROUP BY`.

### pivot tables — two-way summaries
```python
sales.pivot_table(index="region", columns="product", values="revenue",
                  aggfunc="sum", fill_value=0)
```

### Correlation — do two variables move together?
`df["x"].corr(df["y"])` gives Pearson's *r* between −1 and 1:
* close to **+1**: as x rises, y rises
* close to **−1**: as x rises, y falls
* close to **0**: no *linear* relationship

> ⚠️ **Correlation is not causation.** Ice-cream sales and drownings are
> correlated because both rise in summer. Always look for a hidden third factor.
""",
    examples=(
        E("value_counts", SALES + "print(sales['region'].value_counts())\nprint(sales['region'].value_counts(normalize=True).round(2))"),
        E("groupby", SALES + "print(sales.groupby('region')['revenue'].sum())\nprint(sales.groupby('region')['units'].agg(['count', 'mean', 'max']))"),
        E("Pivot table", SALES + "print(sales.pivot_table(index='region', columns='product', values='revenue', aggfunc='sum', fill_value=0))"),
        E("Correlation", "import pandas as pd\ndf = pd.DataFrame({\n    'hours_studied': [1, 2, 3, 4, 5, 6, 7, 8],\n    'score':         [52, 55, 61, 64, 70, 72, 79, 83],\n    'shoe_size':     [9, 7, 10, 8, 7, 9, 8, 10],\n})\nprint(round(df['hours_studied'].corr(df['score']), 3))\nprint(round(df['hours_studied'].corr(df['shoe_size']), 3))\nprint(df.corr().round(2))"),
    ),
    key_points=("`value_counts()` for categories; `groupby().agg()` for per-group stats.",
                "Correlation r ranges from −1 to 1.", "Correlation ≠ causation."),
)

ITEMS = (
    MCQ("t09.mcq.skew", "House prices in a town: mean £410k, median £260k. What does this suggest?",
        (O("A few very expensive houses skew the mean upwards", True, "Mean ≫ median indicates a long "
           "right tail; the median better describes a typical house."),
         O("Most houses cost about £410k", False, "The mean is inflated by a small number of very "
           "expensive properties; half the houses cost less than £260k."),
         O("The data must contain an error", False, "This pattern is completely normal for prices."),
         O("The distribution is symmetric", False, "In a symmetric distribution mean ≈ median.")),
        "Report the median for skewed data.", tags=("statistics",)),
    MCQ("t09.mcq.std", "Two classes both have a mean score of 65. Class A's std is 3, class B's is 18. Which is true?",
        (O("Class B's scores are much more spread out", True, "Standard deviation measures spread "
           "around the mean."),
         O("Class B did better", False, "Both means are equal; std says nothing about which is higher."),
         O("Class A has more students", False, "Std doesn't depend on the number of students."),
         O("Class A has outliers", False, "A *small* std means scores cluster tightly around 65.")),
        "Std describes spread, not level.", tags=("statistics",)),
    MCQ("t09.mcq.corr", "Cities with more fire engines report more fire damage (r = 0.8). What can you conclude?",
        (O("They're correlated, probably because bigger cities have both", True, "City size is a "
           "confounding variable driving both."),
         O("Fire engines cause fire damage", False, "Correlation alone never proves causation."),
         O("Remove fire engines to reduce damage", False, "That's acting on a causal claim the data "
           "doesn't support."),
         O("r = 0.8 means 80% of damage is caused by engines", False, "r is not a percentage of causation.")),
        "Correlation is not causation; look for confounders.", tags=("statistics", "correlation")),
    MCQ("t09.mcq.groupby", "Which gives total revenue per region?",
        (O("`sales.groupby('region')['revenue'].sum()`", True, ""),
         O("`sales['revenue'].sum()`", False, "That's the grand total, not per region."),
         O("`sales.groupby('revenue')['region'].sum()`", False, "The column roles are swapped: group by "
           "region, aggregate revenue."),
         O("`sales['region'].value_counts()`", False, "That counts rows per region; it ignores revenue.")),
        "`df.groupby(key)[value].agg_function()`.", tags=("pandas", "groupby")),
    PredictOutput("t09.pred.median", "What does this print?",
                  "import pandas as pd\ns = pd.Series([3, 1, 9, 5])\nprint(s.mean())\nprint(s.median())",
                  "4.5\n4.0",
                  "Mean = 18/4 = 4.5. Sorted: 1, 3, 5, 9 — with an even count the median is the average "
                  "of the middle two: (3+5)/2 = 4.0.",
                  tags=("statistics",),
                  common_wrong=(("4.5\n9.0", "The median uses the *sorted* values (1, 3, 5, 9), not the "
                                 "original order."),
                                ("4.5\n5.0", "With an even number of values the median is the mean of "
                                 "the two middle values: (3 + 5) / 2."),)),
    PredictOutput("t09.pred.value_counts", "What does this print?",
                  "import pandas as pd\ns = pd.Series(['a', 'b', 'a', 'c', 'a', 'b'])\ncounts = s.value_counts()\nprint(counts.index[0], counts.iloc[0])\nprint(len(counts))",
                  "a 3\n3",
                  "`value_counts()` sorts by frequency, so the most common value ('a', 3 times) is first. "
                  "There are 3 distinct values.",
                  tags=("pandas", "statistics")),
    PredictOutput("t09.pred.groupby", "What does this print?",
                  SALES + "totals = sales.groupby('region')['units'].sum()\nprint(totals['North'])\nprint(totals.idxmax())",
                  "25\nSouth",
                  "North: 12 + 3 + 10 = 25. South: 7 + 15 + 6 = 28 (the max). East: 9 + 4 = 13.",
                  tags=("pandas", "groupby")),
    DebugExercise("t09.dbg.mean_of_groups", "`avg_units` should be the average units per sale in the North "
                  "region (`8.333...`). This computes the wrong thing. Fix it.",
                  SALES + "north = sales[sales['region'] == 'North']\navg_units = sales['units'].mean()",
                  SALES + "north = sales[sales['region'] == 'North']\navg_units = north['units'].mean()",
                  (C("avg_units for North", expr="round(float(avg_units), 3)", expected=8.333),),
                  "The filter was stored in `north` but the mean was taken over the full `sales` table.",
                  hints=("Which DataFrame does the mean use?",), tags=("pandas", "debugging")),
    DebugExercise("t09.dbg.iqr", "`outliers` should list values outside the 1.5×IQR fences (`[95]`), but "
                  "it's empty. Fix the logic.",
                  "import pandas as pd\ns = pd.Series([20, 22, 23, 24, 25, 26, 27, 95])\nq1, q3 = s.quantile(0.25), s.quantile(0.75)\niqr = q3 - q1\noutliers = s[(s < q1 - 1.5 * iqr) & (s > q3 + 1.5 * iqr)].tolist()",
                  "import pandas as pd\ns = pd.Series([20, 22, 23, 24, 25, 26, 27, 95])\nq1, q3 = s.quantile(0.25), s.quantile(0.75)\niqr = q3 - q1\noutliers = s[(s < q1 - 1.5 * iqr) | (s > q3 + 1.5 * iqr)].tolist()",
                  (C("outliers == [95]", expr="outliers", expected=[95]),),
                  "No value can be both below the lower fence *and* above the upper fence. Use `|` (or).",
                  hints=("Can a number be too small and too big at the same time?",), tags=("statistics", "logic")),
    CodingExercise("t09.code.summary", "Using `sales`, create: `total_revenue` (sum of revenue), "
                   "`revenue_by_product` (a Series of total revenue per product) and `best_region` "
                   "(the region with the highest total revenue).",
                   SALES,
                   SALES + "total_revenue = sales['revenue'].sum()\nrevenue_by_product = sales.groupby('product')['revenue'].sum()\nbest_region = sales.groupby('region')['revenue'].sum().idxmax()",
                   (C("total_revenue", expr="float(total_revenue)", expected=192.0),
                    C("revenue_by_product", expr="revenue_by_product.to_dict()", expected={"A": 120.0, "B": 72.0}),
                    C("best_region", expr="best_region", expected="South")),
                   "`idxmax()` returns the *label* of the largest value.",
                   hints=("`groupby(...)[...].sum()`", "`.idxmax()` on the grouped Series."),
                   tags=("pandas", "groupby", "statistics")),
    CodingExercise("t09.code.zscore", "Write `zscores(values)` that returns a **list** of z-scores "
                   "`(x - mean) / std` using the sample std (`pandas .std()`), each rounded to 2 decimals.",
                   "import pandas as pd\n\ndef zscores(values):\n    ...\n",
                   "import pandas as pd\n\ndef zscores(values):\n    s = pd.Series(values, dtype=float)\n    return ((s - s.mean()) / s.std()).round(2).tolist()",
                   (C("zscores([2, 4, 6])", expr="zscores([2, 4, 6])", expected=[-1.0, 0.0, 1.0]),
                    C("zscores([10, 10, 13, 15])", expr="zscores([10, 10, 13, 15])", expected=[-0.82, -0.82, 0.41, 1.22]),
                    C("Returns a list", expr="type(zscores([1, 2])).__name__", expected="list")),
                   "A z-score says how many standard deviations a value is from the mean.",
                   hints=("Turn the list into a Series first.", "`.round(2).tolist()`"),
                   tags=("statistics", "functions")),
)

TOPIC = Topic(
    id="t09", number=9, title="Descriptive Analysis", icon="📊",
    summary="Mean/median/mode, spread, quartiles and outliers, groupby, pivot tables and correlation.",
    lessons=(L1, L2, L3), items=ITEMS, prerequisites=("t08",),
)
