from .models import (MCQ, Check as C, CodingExercise, DebugExercise, Example as E,
                     Lesson, Option as O, PredictOutput, Topic)

# A deliberately messy dataset used throughout this topic.
MESSY = '''import io
import pandas as pd
csv_text = """order_id,customer,city,price,quantity,order_date
1,Ana, leeds ,12.50,2,2024-01-05
2,Ben,York,8.00,,2024-01-06
3,Cy,LEEDS,,1,2024-01-06
4,Di,Hull,"1,200.00",1,2024-01-07
5,Ben,York,8.00,,2024-01-06
6,Eve,york,5.25,4,2024-01-09
"""
df = pd.read_csv(io.StringIO(csv_text))
'''

L1 = Lesson(
    id="t08.l1",
    title="pandas DataFrames: loading and inspecting data",
    body=f"""
**pandas** is *the* Python library for tabular data. Its two core objects:

* **Series** — one column: values plus an index (row labels).
* **DataFrame** — a table of Series sharing the same index.

```python
import pandas as pd
df = pd.DataFrame({{"name": ["Ana", "Ben"], "age": [31, 25]}})
df = pd.read_csv("sales.csv")          # the usual way to load data
```

### First things to do with any dataset
| Code | Tells you |
|---|---|
| `df.head()` / `df.tail()` | first / last 5 rows |
| `df.shape` | `(rows, columns)` — a tuple! |
| `df.columns` | column names |
| `df.dtypes` | the type of each column |
| `df.info()` | types + non-null counts |
| `df.describe()` | summary statistics |

### Selecting
```python
df["price"]                    # one column → Series
df[["customer", "price"]]      # several columns → DataFrame (note [[ ]])
df.loc[0, "price"]             # by label
df.iloc[0, 3]                  # by position
df[df["price"] > 10]           # filter rows with a boolean condition
df[(df["city"] == "York") & (df["quantity"] > 1)]   # & = and, | = or, brackets required
```

### The messy dataset used in this topic
```python
{MESSY}```
It has inconsistent capitalisation, stray spaces, missing values, a duplicate
row and a price stored as text with a comma. Real data looks like this!
""",
    examples=(
        E("Inspect the messy data", MESSY + "print(df)\nprint(df.shape)\nprint(df.dtypes)"),
        E("Selecting and filtering", MESSY + "print(df['customer'].tolist())\nprint(df[['customer', 'quantity']].head(3))\nprint(df[df['quantity'] > 1])"),
        E("info() and missing counts", MESSY + "df.info()\nprint(df.isna().sum())"),
    ),
    key_points=("A DataFrame is a table; each column is a Series.", "Start with head, shape, dtypes, info.",
                "Filter with boolean masks; combine with `&` / `|` and brackets."),
)

L2 = Lesson(
    id="t08.l2",
    title="Missing values and duplicates",
    body="""
Missing values appear as `NaN` (Not a Number) or `None`.

```python
df.isna().sum()                 # missing count per column
df.dropna()                     # drop rows with ANY missing value
df.dropna(subset=["price"])     # only consider some columns
df["quantity"].fillna(1)        # replace missing values
df["price"].fillna(df["price"].median())
```

### ⚠️ Most pandas methods return a *new* object
`df.dropna()` on its own does **nothing** to `df`. Assign the result:
```python
df = df.dropna(subset=["price"])
df["quantity"] = df["quantity"].fillna(1)
```

### How should you handle missing data?
There's no single right answer — it's a judgement call you should document:
* **Drop** rows if few are affected and they're missing at random.
* **Fill** with a sensible default (0 sales, 1 item) when the meaning is clear.
* **Impute** with the median/mean for numeric columns (median is robust to outliers).
* **Keep and flag**: add a column `price_missing = df["price"].isna()`.

### Duplicates
```python
df.duplicated().sum()                       # count fully duplicated rows
df = df.drop_duplicates()
df = df.drop_duplicates(subset=["customer", "order_date"])
```
""",
    examples=(
        E("Counting missing values", MESSY + "print(df.isna().sum())\nprint('rows with any missing:', df.isna().any(axis=1).sum())"),
        E("dropna returns a new DataFrame", MESSY + "df.dropna()\nprint(len(df), 'rows — unchanged!')\nclean = df.dropna()\nprint(len(clean), 'rows after dropna')"),
        E("Filling", MESSY + "df['quantity'] = df['quantity'].fillna(1)\nprint(df['quantity'].tolist())"),
        E("Duplicates", MESSY + "print(df.duplicated(subset=['customer', 'order_date']).sum())\ndf = df.drop_duplicates(subset=['customer', 'order_date'])\nprint(df['order_id'].tolist())"),
    ),
    key_points=("`isna().sum()` counts missing values.", "Assign results: `df = df.dropna()`.",
                "Choose drop / fill / impute deliberately and document why."),
)

L3 = Lesson(
    id="t08.l3",
    title="Cleaning text, fixing types and creating columns",
    body="""
### String cleaning with `.str`
Text columns have a `.str` accessor with vectorised string methods:
```python
df["city"] = df["city"].str.strip().str.title()   # ' leeds ' → 'Leeds'
df["customer"].str.upper()
df["product"].str.contains("lap")
```

### Fixing types
```python
df["price"] = (df["price"].astype(str)
                 .str.replace(",", "", regex=False)
                 .astype(float))
df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")  # bad → NaN
df["order_date"] = pd.to_datetime(df["order_date"])
df["month"] = df["order_date"].dt.month
```
`errors="coerce"` turns unconvertible values into `NaN` instead of crashing —
then you can count them.

### New columns (vectorised maths — no loops needed)
```python
df["revenue"] = df["price"] * df["quantity"]
df["big_order"] = df["revenue"] > 50
df["size"] = df["quantity"].map({1: "single"}).fillna("multi")
```
Operations on whole columns are applied element-by-element, and are much
faster than Python loops.

### Renaming and sorting
```python
df = df.rename(columns={"qty": "quantity"})
df = df.sort_values("revenue", ascending=False)
```
""",
    examples=(
        E("Standardising text", MESSY + "print(df['city'].tolist())\ndf['city'] = df['city'].str.strip().str.title()\nprint(df['city'].tolist())\nprint(df['city'].value_counts())"),
        E("Fixing the price column", MESSY + "print(df['price'].tolist())\ndf['price'] = df['price'].astype(str).str.replace(',', '', regex=False)\ndf['price'] = pd.to_numeric(df['price'], errors='coerce')\nprint(df['price'].tolist())"),
        E("Dates and derived columns", MESSY + "df['order_date'] = pd.to_datetime(df['order_date'])\ndf['weekday'] = df['order_date'].dt.day_name()\ndf['quantity'] = df['quantity'].fillna(1)\nprint(df[['order_date', 'weekday', 'quantity']])"),
        E("A full cleaning pipeline", MESSY + "def clean(df):\n    df = df.drop_duplicates(subset=['customer', 'order_date']).copy()\n    df['city'] = df['city'].str.strip().str.title()\n    df['price'] = pd.to_numeric(df['price'].astype(str).str.replace(',', '', regex=False), errors='coerce')\n    df['quantity'] = df['quantity'].fillna(1).astype(int)\n    df = df.dropna(subset=['price'])\n    df['revenue'] = df['price'] * df['quantity']\n    return df\n\ntidy = clean(df)\nprint(tidy[['customer', 'city', 'price', 'quantity', 'revenue']])\nprint('Total revenue:', tidy['revenue'].sum())"),
    ),
    key_points=("Use `.str` methods to clean text columns.",
                "`pd.to_numeric(..., errors='coerce')` and `pd.to_datetime` fix types.",
                "Column arithmetic is vectorised — no loops needed."),
)

ITEMS = (
    MCQ("t08.mcq.shape", "What type is `df.shape`?",
        (O("A tuple `(rows, columns)`", True, "It's a tuple, so you can unpack it: `rows, cols = df.shape`."),
         O("A list", False, "It's an immutable tuple, not a list."),
         O("An int (the number of rows)", False, "That's `len(df)`."),
         O("A method you must call: `df.shape()`", False, "`shape` is an attribute — no brackets. "
           "`df.shape()` raises `TypeError: 'tuple' object is not callable`.")),
        "`df.shape` is a `(rows, columns)` tuple.", tags=("pandas", "tuples")),
    MCQ("t08.mcq.dropna_assign", "After running `df.dropna()` on its own line, what happened to `df`?",
        (O("Nothing — the cleaned result was thrown away", True, "`dropna` returns a new DataFrame; "
           "you must assign it: `df = df.dropna()`."),
         O("Rows with missing values were removed from `df`", False, "pandas methods don't modify in "
           "place by default — just like `str.upper()`."),
         O("Missing values were replaced by 0", False, "That's `fillna(0)`."),
         O("An error occurred", False, "It runs fine; the result is just discarded.")),
        "Assign the results of pandas methods.", tags=("pandas", "missing-data")),
    MCQ("t08.mcq.median", "A salary column has a few huge outliers and some missing values. Which fill value is usually most sensible?",
        (O("The median", True, "The median isn't pulled up by extreme values, so it represents a "
           "typical salary."),
         O("The mean", False, "Outliers drag the mean upwards, so you'd impute unrealistically high values."),
         O("The maximum", False, "That would inflate the data badly."),
         O("Always 0", False, "A salary of 0 is not a plausible typical value and would distort statistics.")),
        "Median is robust to outliers.", tags=("missing-data", "statistics")),
    MCQ("t08.mcq.and_filter", "Which correctly filters rows where city is York **and** quantity > 1?",
        (O("`df[(df['city'] == 'York') & (df['quantity'] > 1)]`", True, ""),
         O("`df[df['city'] == 'York' and df['quantity'] > 1]`", False, "Python's `and` doesn't work "
           "element-wise on columns: pandas raises 'The truth value of a Series is ambiguous'. Use `&`."),
         O("`df[df['city'] == 'York' & df['quantity'] > 1]`", False, "`&` binds tighter than `==` and "
           "`>`, so without brackets the expression is evaluated in the wrong order."),
         O("`df.where(city='York', quantity>1)`", False, "That's not pandas syntax.")),
        "Combine masks with `&`, `|`, `~` and wrap each condition in brackets.", tags=("pandas", "logic")),
    MCQ("t08.mcq.coerce", "What does `pd.to_numeric(s, errors='coerce')` do with the value `'n/a'`?",
        (O("Turns it into NaN", True, "Unconvertible values become missing values you can count and handle."),
         O("Raises a ValueError", False, "That's the default `errors='raise'`."),
         O("Leaves it as the string 'n/a'", False, "That was `errors='ignore'`, now deprecated."),
         O("Turns it into 0", False, "pandas never invents a 0; it marks the value as missing.")),
        "`errors='coerce'` converts bad values to NaN.", tags=("pandas", "types")),
    PredictOutput("t08.pred.shape", "What does this print?",
                  "import pandas as pd\ndf = pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})\nprint(df.shape)\nprint(len(df.columns))",
                  "(3, 2)\n2",
                  "3 rows and 2 columns; `shape` is `(rows, columns)`.",
                  tags=("pandas",),
                  common_wrong=(("(2, 3)", "The order is (rows, columns): 3 rows, 2 columns."),)),
    PredictOutput("t08.pred.isna", "What does this print?",
                  "import pandas as pd\ns = pd.Series([4, None, 7, None])\nprint(s.isna().sum())\nprint(s.fillna(0).sum())\nprint(s.mean())",
                  "2\n11.0\n5.5",
                  "Two values are missing. `fillna(0)` gives 4+0+7+0 = 11.0. `mean()` *skips* NaN by default: (4+7)/2.",
                  tags=("pandas", "missing-data"),
                  common_wrong=(("2\n11.0\n2.75", "pandas' `mean()` ignores missing values by default; it "
                                 "doesn't treat them as 0."),)),
    PredictOutput("t08.pred.str", "What does this print?",
                  "import pandas as pd\ns = pd.Series([' york', 'YORK ', 'Leeds'])\nprint(s.str.strip().str.title().nunique())",
                  "2",
                  "After stripping spaces and title-casing, the values are York, York, Leeds — 2 unique.",
                  tags=("pandas", "strings")),
    PredictOutput("t08.pred.filter", "What does this print?",
                  "import pandas as pd\ndf = pd.DataFrame({'x': [5, 12, 8, 20]})\nprint(len(df[df['x'] > 7]))\nprint(df[df['x'] > 7]['x'].sum())",
                  "3\n40",
                  "12, 8 and 20 are greater than 7; they sum to 40.",
                  tags=("pandas",)),
    DebugExercise("t08.dbg.not_assigned", "After cleaning, `df` should have **no** missing prices and the "
                  "city names should be title-case. Nothing seems to change. Fix it.",
                  MESSY + "df.dropna(subset=['price'])\ndf['city'].str.strip().str.title()",
                  MESSY + "df = df.dropna(subset=['price'])\ndf['city'] = df['city'].str.strip().str.title()",
                  (C("No missing prices", expr="int(df['price'].isna().sum())", expected=0),
                   C("5 rows left", expr="len(df)", expected=5),
                   C("Cities cleaned", expr="sorted(df['city'].unique())", expected=["Hull", "Leeds", "York"])),
                  "Both lines computed new results and threw them away. Assign them back.",
                  hints=("Do pandas methods change the DataFrame in place?",), tags=("pandas", "missing-data")),
    DebugExercise("t08.dbg.price_type", "`total` should be the sum of the price column (`1233.75`) but this "
                  "crashes. Fix the conversion so the price `\"1,200.00\"` is handled.",
                  MESSY + "df = df.dropna(subset=['price'])\ndf['price'] = df['price'].astype(float)\ntotal = df['price'].sum()",
                  MESSY + "df = df.dropna(subset=['price'])\ndf['price'] = df['price'].astype(str).str.replace(',', '', regex=False).astype(float)\ntotal = df['price'].sum()",
                  (C("total == 1233.75", expr="float(total)", expected=1233.75),),
                  "The thousands separator in `1,200.00` stops `float()` working. Remove commas first.",
                  hints=("Read the ValueError: which text couldn't be converted?",), tags=("pandas", "types")),
    CodingExercise("t08.code.clean", "Write `clean(df)` that returns a cleaned **copy** of the messy data: "
                   "remove duplicates on `customer` + `order_date`, title-case/strip `city`, convert `price` "
                   "to float (removing commas), fill missing `quantity` with 1, drop rows with missing price, "
                   "and add `revenue = price * quantity`.",
                   MESSY + "\ndef clean(df):\n    ...\n\ntidy = clean(df)\n",
                   MESSY + "\ndef clean(df):\n    df = df.drop_duplicates(subset=['customer', 'order_date']).copy()\n    df['city'] = df['city'].str.strip().str.title()\n    df['price'] = df['price'].astype(str).str.replace(',', '', regex=False).astype(float)\n    df['quantity'] = df['quantity'].fillna(1)\n    df = df.dropna(subset=['price'])\n    df['revenue'] = df['price'] * df['quantity']\n    return df\n\ntidy = clean(df)\n",
                   (C("4 rows remain", expr="len(tidy)", expected=4),
                    C("Cities cleaned", expr="sorted(tidy['city'].unique())", expected=["Hull", "Leeds", "York"]),
                    C("Total revenue", expr="float(tidy['revenue'].sum())", expected=1254.0),
                    C("No missing values in key columns", expr="int(tidy[['price', 'quantity', 'revenue']].isna().sum().sum())", expected=0),
                    C("Original df untouched", expr="len(df)", expected=6)),
                   "Wrapping cleaning steps in a function makes them repeatable for next month's data.",
                   hints=("Start with `df = df.drop_duplicates(...).copy()`.",
                          "price → `.astype(str).str.replace(',', '', regex=False).astype(float)`"),
                   tags=("pandas", "missing-data", "functions")),
    CodingExercise("t08.code.filter", "Using the built-in `scores` DataFrame, create `passed` containing only "
                   "rows where `score >= 50` **and** `attendance >= 0.8`, sorted by score descending.",
                   "import pandas as pd\nscores = pd.DataFrame({\n    'student': ['Ana', 'Ben', 'Cy', 'Di', 'Eve'],\n    'score': [72, 48, 91, 55, 63],\n    'attendance': [0.95, 0.9, 0.7, 0.85, 0.8],\n})\n",
                   "import pandas as pd\nscores = pd.DataFrame({\n    'student': ['Ana', 'Ben', 'Cy', 'Di', 'Eve'],\n    'score': [72, 48, 91, 55, 63],\n    'attendance': [0.95, 0.9, 0.7, 0.85, 0.8],\n})\npassed = scores[(scores['score'] >= 50) & (scores['attendance'] >= 0.8)].sort_values('score', ascending=False)",
                   (C("Right students in order", expr="passed['student'].tolist()", expected=["Ana", "Eve", "Di"]),),
                   "Boolean masks combined with `&`, then `sort_values`.",
                   hints=("Wrap each condition in brackets.",), tags=("pandas", "logic")),
)

TOPIC = Topic(
    id="t08", number=8, title="Data Preparation", icon="🧹",
    summary="pandas DataFrames: loading, inspecting, filtering, missing values, duplicates, types, new columns.",
    lessons=(L1, L2, L3), items=ITEMS, prerequisites=("t06",),
)
