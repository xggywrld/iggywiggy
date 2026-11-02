from .models import (MCQ, Check as C, CodingExercise, DebugExercise, Example as E,
                     Lesson, Option as O, PredictOutput, Topic)

# A small shop database reused by examples and exercises. It is shown in full
# so learners can see exactly what data their queries run against.
SHOP = '''import sqlite3
conn = sqlite3.connect(":memory:")
conn.executescript("""
CREATE TABLE customers (id INTEGER PRIMARY KEY, name TEXT, city TEXT);
CREATE TABLE orders (id INTEGER PRIMARY KEY, customer_id INTEGER, product TEXT,
                     amount REAL, order_date TEXT);
INSERT INTO customers VALUES (1, 'Ana', 'Leeds'), (2, 'Ben', 'York'),
                             (3, 'Cy', 'Leeds'), (4, 'Di', 'Hull');
INSERT INTO orders VALUES
  (1, 1, 'laptop', 900.0, '2024-01-05'), (2, 1, 'mouse', 25.0, '2024-01-20'),
  (3, 2, 'desk', 150.0, '2024-02-02'),   (4, 3, 'chair', 85.0, '2024-02-14'),
  (5, 3, 'laptop', 950.0, '2024-03-01'), (6, 2, 'mouse', 20.0, '2024-03-09');
""")
'''

L1 = Lesson(
    id="t07.l1",
    title="Databases, tables and your first queries",
    body=f"""
A **relational database** stores data in **tables**: rows (records) and
columns (fields), like a set of linked spreadsheets. **SQL** (Structured Query
Language) is the language for asking questions of that data. It's one of the
most requested skills in data jobs.

Python ships with **SQLite**, a complete database in a single file (or in
memory) — no server required:

```python
import sqlite3
conn = sqlite3.connect("shop.db")      # or ":memory:" for a temporary DB
conn.execute("CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT, price REAL)")
conn.execute("INSERT INTO products (name, price) VALUES ('pen', 1.2)")
conn.commit()                          # save changes (for file databases)
rows = conn.execute("SELECT * FROM products").fetchall()
print(rows)                            # [(1, 'pen', 1.2)]  ← a LIST of TUPLES
```

### Key vocabulary
* **Primary key** — a column that uniquely identifies each row (`id`).
* **Foreign key** — a column that refers to another table's primary key
  (`orders.customer_id` → `customers.id`).
* SQL keywords are case-insensitive, but writing them in CAPITALS is
  conventional. **Text values go in single quotes**: `'Leeds'`.

### The database used in this topic
```python
{SHOP}```
""",
    examples=(
        E("Create, insert, select", "import sqlite3\nconn = sqlite3.connect(':memory:')\nconn.execute('CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT, price REAL)')\nconn.execute(\"INSERT INTO products (name, price) VALUES ('pen', 1.2)\")\nconn.execute(\"INSERT INTO products (name, price) VALUES ('book', 8.5)\")\nconn.commit()\nrows = conn.execute('SELECT * FROM products').fetchall()\nprint(rows)\nfor pid, name, price in rows:\n    print(pid, name, price)",
          "Each row comes back as a tuple — unpack it in the loop."),
        E("Explore the shop database", SHOP + "print(conn.execute('SELECT * FROM customers').fetchall())\nprint(conn.execute('SELECT name FROM sqlite_master WHERE type=\"table\"').fetchall())"),
    ),
    key_points=("Tables have rows and columns; primary keys identify rows.",
                "`conn.execute(sql).fetchall()` returns a list of tuples.",
                "Text values in SQL use single quotes."),
)

L2 = Lesson(
    id="t07.l2",
    title="SELECT, WHERE, ORDER BY and LIMIT",
    body="""
```sql
SELECT columns          -- which columns (* = all)
FROM table              -- which table
WHERE condition         -- which rows (filter)
ORDER BY column DESC    -- sort (ASC is the default)
LIMIT n                 -- at most n rows
```
The clauses **must** appear in this order.

### Filtering with WHERE
| SQL | Meaning |
|---|---|
| `amount > 100` | comparison (`=`, `<>` or `!=`, `<`, `>=` ...) |
| `city = 'Leeds'` | equality uses a **single** `=` in SQL |
| `city IN ('Leeds', 'York')` | membership |
| `amount BETWEEN 20 AND 100` | inclusive range |
| `product LIKE 'lap%'` | pattern: `%` = any characters, `_` = one character |
| `city IS NULL` | missing values (never `= NULL`) |
| `AND`, `OR`, `NOT` | combine conditions |

### Computed columns and aliases
```sql
SELECT product, amount, amount * 1.2 AS amount_with_vat FROM orders
```
`DISTINCT` removes duplicate rows: `SELECT DISTINCT city FROM customers`.
""",
    examples=(
        E("WHERE and ORDER BY", SHOP + "sql = '''\nSELECT product, amount\nFROM orders\nWHERE amount > 50\nORDER BY amount DESC\n'''\nfor row in conn.execute(sql):\n    print(row)"),
        E("Patterns, IN and LIMIT", SHOP + "print(conn.execute(\"SELECT name FROM customers WHERE city IN ('Leeds', 'Hull')\").fetchall())\nprint(conn.execute(\"SELECT product FROM orders WHERE product LIKE 'm%'\").fetchall())\nprint(conn.execute('SELECT product, amount FROM orders ORDER BY amount DESC LIMIT 2').fetchall())"),
        E("Aliases and DISTINCT", SHOP + "print(conn.execute('SELECT DISTINCT city FROM customers ORDER BY city').fetchall())\nprint(conn.execute('SELECT product, amount * 1.2 AS with_vat FROM orders LIMIT 3').fetchall())"),
        E("A quoting mistake", SHOP + "print(conn.execute('SELECT * FROM customers WHERE city = Leeds').fetchall())",
          "Without quotes SQL thinks Leeds is a column. Run it, read the explanation and fix it."),
    ),
    key_points=("Clause order: SELECT, FROM, WHERE, ORDER BY, LIMIT.",
                "`=` compares in SQL; text in single quotes.", "Use `IS NULL` for missing values."),
)

L3 = Lesson(
    id="t07.l3",
    title="Aggregates, GROUP BY and HAVING",
    body="""
**Aggregate functions** summarise many rows into one value:
`COUNT(*)`, `SUM(col)`, `AVG(col)`, `MIN(col)`, `MAX(col)`.

```sql
SELECT COUNT(*), SUM(amount), AVG(amount) FROM orders
```

### GROUP BY — one result row per group
```sql
SELECT customer_id, COUNT(*) AS n_orders, SUM(amount) AS total
FROM orders
GROUP BY customer_id
ORDER BY total DESC
```
Think of it as: *split the rows into groups → aggregate each group → one
row per group.* This is exactly pandas' `df.groupby(...).agg(...)`.

**Rule:** every column in `SELECT` must either be in `GROUP BY` or be inside
an aggregate function.

### WHERE vs HAVING
* `WHERE` filters **rows before** grouping.
* `HAVING` filters **groups after** aggregating.

```sql
SELECT product, SUM(amount) AS revenue
FROM orders
WHERE order_date >= '2024-02-01'   -- rows
GROUP BY product
HAVING SUM(amount) > 100           -- groups
```
Full clause order: `SELECT … FROM … WHERE … GROUP BY … HAVING … ORDER BY … LIMIT`.
""",
    examples=(
        E("Whole-table aggregates", SHOP + "print(conn.execute('SELECT COUNT(*), SUM(amount), ROUND(AVG(amount), 2), MAX(amount) FROM orders').fetchone())"),
        E("GROUP BY", SHOP + "sql = '''\nSELECT customer_id, COUNT(*) AS n_orders, SUM(amount) AS total\nFROM orders\nGROUP BY customer_id\nORDER BY total DESC\n'''\nfor row in conn.execute(sql):\n    print(row)"),
        E("WHERE vs HAVING", SHOP + "sql = '''\nSELECT product, SUM(amount) AS revenue\nFROM orders\nWHERE order_date >= '2024-02-01'\nGROUP BY product\nHAVING SUM(amount) > 100\n'''\nprint(conn.execute(sql).fetchall())"),
        E("Grouping by month", SHOP + "sql = '''\nSELECT substr(order_date, 1, 7) AS month, ROUND(SUM(amount), 2)\nFROM orders GROUP BY month ORDER BY month\n'''\nprint(conn.execute(sql).fetchall())"),
    ),
    key_points=("Aggregates collapse rows: COUNT, SUM, AVG, MIN, MAX.",
                "GROUP BY makes one row per group.", "WHERE filters rows; HAVING filters groups."),
)

L4 = Lesson(
    id="t07.l4",
    title="JOINs: combining tables",
    body="""
Data is split across tables to avoid repetition. A **JOIN** puts it back
together by matching keys.

```sql
SELECT c.name, o.product, o.amount
FROM orders AS o
JOIN customers AS c ON o.customer_id = c.id
```
`o` and `c` are **table aliases** — shorthand that also makes it clear which
table each column comes from.

| Join | Keeps |
|---|---|
| `INNER JOIN` (or `JOIN`) | only rows with a match in **both** tables |
| `LEFT JOIN` | **all** rows from the left table; missing matches become `NULL` |

```sql
-- Customers with no orders still appear, with NULL totals:
SELECT c.name, COUNT(o.id) AS n_orders
FROM customers AS c
LEFT JOIN orders AS o ON o.customer_id = c.id
GROUP BY c.name
```
In our shop, Di has no orders: an INNER JOIN drops Di; a LEFT JOIN keeps Di
with `n_orders = 0`. Note `COUNT(o.id)` counts only non-NULL values, whereas
`COUNT(*)` would count Di's NULL row as 1.

> ⚠️ Forgetting the `ON` condition produces every combination of rows (a
> *cartesian product*) — a classic way to get wildly wrong totals.
""",
    examples=(
        E("INNER JOIN", SHOP + "sql = '''\nSELECT c.name, o.product, o.amount\nFROM orders AS o\nJOIN customers AS c ON o.customer_id = c.id\nORDER BY c.name\n'''\nfor row in conn.execute(sql):\n    print(row)"),
        E("LEFT JOIN keeps unmatched rows", SHOP + "sql = '''\nSELECT c.name, COUNT(o.id) AS n_orders, COALESCE(SUM(o.amount), 0) AS spent\nFROM customers AS c\nLEFT JOIN orders AS o ON o.customer_id = c.id\nGROUP BY c.name\nORDER BY spent DESC\n'''\nfor row in conn.execute(sql):\n    print(row)",
          "`COALESCE(x, 0)` replaces NULL with 0."),
        E("Revenue by city", SHOP + "sql = '''\nSELECT c.city, SUM(o.amount) AS revenue\nFROM orders o JOIN customers c ON o.customer_id = c.id\nGROUP BY c.city ORDER BY revenue DESC\n'''\nprint(conn.execute(sql).fetchall())"),
    ),
    key_points=("JOIN … ON matches rows by key.", "INNER keeps matches only; LEFT keeps all left rows.",
                "Always write the ON condition."),
)

L5 = Lesson(
    id="t07.l5",
    title="Safe queries with parameters, and SQL + pandas",
    body="""
### Never build SQL with f-strings from user input
```python
name = input()
conn.execute(f"SELECT * FROM customers WHERE name = '{name}'")   # ❌ DANGEROUS
```
If someone types `x' OR '1'='1`, the query returns *every* customer — this is
**SQL injection**, one of the most common security holes on the web.

Use **placeholders** (`?`) and pass values separately. The database treats them
strictly as data, never as SQL:
```python
conn.execute("SELECT * FROM customers WHERE name = ?", (name,))  # ✅
conn.executemany("INSERT INTO customers (name, city) VALUES (?, ?)",
                 [("Eve", "Bath"), ("Fin", "York")])
```
Note `(name,)` — a one-item **tuple** needs the trailing comma.

### SQL → pandas
`pandas.read_sql_query` runs a query and returns a DataFrame, ready for
analysis and plotting:
```python
import pandas as pd
df = pd.read_sql_query("SELECT * FROM orders", conn)
df.groupby("product")["amount"].sum()
```
A common workflow: use SQL to **select and join** the data you need from a big
database, then pandas to **clean, analyse and visualise** it.
""",
    examples=(
        E("Injection demo", SHOP + "evil = \"x' OR '1'='1\"\nunsafe = f\"SELECT name FROM customers WHERE name = '{evil}'\"\nprint('unsafe:', conn.execute(unsafe).fetchall())\nsafe = conn.execute('SELECT name FROM customers WHERE name = ?', (evil,)).fetchall()\nprint('safe:  ', safe)"),
        E("executemany", SHOP + "conn.executemany('INSERT INTO customers (name, city) VALUES (?, ?)', [('Eve', 'Bath'), ('Fin', 'York')])\nprint(conn.execute('SELECT COUNT(*) FROM customers').fetchone()[0])\nprint(conn.execute('SELECT name FROM customers WHERE city = ?', ('York',)).fetchall())"),
        E("SQL into pandas", SHOP + "import pandas as pd\ndf = pd.read_sql_query('SELECT c.city, o.product, o.amount FROM orders o JOIN customers c ON o.customer_id = c.id', conn)\nprint(df)\nprint(df.groupby('city')['amount'].sum())"),
    ),
    key_points=("Use `?` placeholders — never f-strings — for values.",
                "One value still needs a tuple: `(value,)`.",
                "`pd.read_sql_query(sql, conn)` returns a DataFrame."),
)

ITEMS = (
    MCQ("t07.mcq.clause_order", "Which query has its clauses in a valid order?",
        (O("`SELECT name FROM customers WHERE city = 'Leeds' ORDER BY name`", True, ""),
         O("`SELECT name WHERE city = 'Leeds' FROM customers`", False, "FROM must come before WHERE."),
         O("`FROM customers SELECT name`", False, "SQL starts with SELECT (in SQLite)."),
         O("`SELECT name FROM customers ORDER BY name WHERE city = 'Leeds'`", False, "WHERE must come "
           "before ORDER BY: filter first, then sort.")),
        "Order: SELECT, FROM, WHERE, GROUP BY, HAVING, ORDER BY, LIMIT.", tags=("sql",)),
    MCQ("t07.mcq.where_having", "You want product groups whose **total** revenue exceeds 500. Which clause filters on the total?",
        (O("`HAVING SUM(amount) > 500`", True, "HAVING filters groups after aggregation."),
         O("`WHERE SUM(amount) > 500`", False, "WHERE runs on individual rows *before* grouping, so "
           "aggregates aren't available yet — SQLite raises 'misuse of aggregate'."),
         O("`WHERE amount > 500`", False, "That keeps individual *orders* above 500, not groups whose "
           "total is above 500."),
         O("`ORDER BY SUM(amount) > 500`", False, "ORDER BY sorts; it doesn't remove rows.")),
        "WHERE → rows (before grouping). HAVING → groups (after).", tags=("sql", "groupby")),
    MCQ("t07.mcq.left_join", "Customers: Ana, Ben, Di. Only Ana and Ben have orders. Which join lists **all three** customers?",
        (O("`customers LEFT JOIN orders`", True, "A LEFT JOIN keeps every row of the left table (customers)."),
         O("`customers INNER JOIN orders`", False, "INNER JOIN drops Di because there is no matching order."),
         O("`orders LEFT JOIN customers`", False, "Now *orders* is the left table, so only customers with "
           "orders appear."),
         O("`customers JOIN orders` without ON", False, "Without ON you get every customer paired with "
           "every order — a cartesian product, not what you want.")),
        "LEFT JOIN keeps all rows from the table written first.", tags=("sql", "joins")),
    MCQ("t07.mcq.injection", "Which line is safe from SQL injection?",
        (O("`conn.execute('SELECT * FROM users WHERE name = ?', (name,))`", True, "The placeholder sends "
           "`name` as pure data."),
         O("`conn.execute(f\"SELECT * FROM users WHERE name = '{name}'\")`", False, "The user's text "
           "becomes part of the SQL itself; a quote in it can change the query."),
         O("`conn.execute(\"SELECT * FROM users WHERE name = '\" + name + \"'\")`", False, "String "
           "concatenation has exactly the same problem as an f-string."),
         O("`conn.execute('SELECT * FROM users WHERE name = ?', name)`", False, "Right idea, but the "
           "parameters must be a sequence: a string would be treated as a sequence of characters. Use `(name,)`.")),
        "Always use `?` placeholders with a tuple of values.", tags=("sql", "security", "tuples")),
    MCQ("t07.mcq.fetchall_type", "What does `conn.execute('SELECT name, city FROM customers').fetchall()` return?",
        (O("A list of tuples", True, "One tuple per row, with one item per selected column."),
         O("A list of dicts", False, "sqlite3 returns tuples by default (you can change `row_factory`)."),
         O("A DataFrame", False, "That's what `pd.read_sql_query` returns."),
         O("A single string", False, "Results are structured as rows.")),
        "Rows are tuples; unpack them with `for name, city in rows:`.", tags=("sql", "tuples")),
    MCQ("t07.mcq.count_null", "After `customers LEFT JOIN orders`, Di has one row with NULL order columns. "
        "What does `COUNT(o.id)` give for Di?",
        (O("`0`", True, "`COUNT(column)` ignores NULLs."),
         O("`1`", False, "That's `COUNT(*)`, which counts rows regardless of NULLs."),
         O("`NULL`", False, "COUNT always returns a number."),
         O("An error", False, "Counting a nullable column is valid.")),
        "COUNT(*) counts rows; COUNT(col) counts non-NULL values.", tags=("sql", "joins")),
    PredictOutput("t07.pred.where", "What does this print?",
                  SHOP + "rows = conn.execute(\"SELECT name FROM customers WHERE city = 'Leeds' ORDER BY name DESC\").fetchall()\nprint(rows)",
                  "[('Cy',), ('Ana',)]",
                  "Two customers live in Leeds; DESC sorts Z→A. Each row is a one-item tuple, hence `('Cy',)`.",
                  tags=("sql", "tuples"),
                  common_wrong=(("['Cy', 'Ana']", "Rows are always tuples, even with one column: `('Cy',)`."),
                                ("[('Ana',), ('Cy',)]", "`DESC` means descending order (Z to A)."),)),
    PredictOutput("t07.pred.group", "What does this print?",
                  SHOP + "for row in conn.execute('SELECT product, COUNT(*) FROM orders GROUP BY product ORDER BY product'):\n    print(row)",
                  "('chair', 1)\n('desk', 1)\n('laptop', 2)\n('mouse', 2)",
                  "GROUP BY creates one row per product; COUNT(*) counts the orders in each group.",
                  tags=("sql", "groupby")),
    PredictOutput("t07.pred.agg", "What does this print?",
                  SHOP + "print(conn.execute('SELECT MIN(amount), MAX(amount) FROM orders WHERE product = ?', ('mouse',)).fetchone())",
                  "(20.0, 25.0)",
                  "Two mouse orders (25.0 and 20.0). `fetchone()` returns a single tuple.",
                  tags=("sql",)),
    PredictOutput("t07.pred.join", "What does this print?",
                  SHOP + "sql = '''SELECT c.name, SUM(o.amount) FROM customers c\nLEFT JOIN orders o ON o.customer_id = c.id\nGROUP BY c.name ORDER BY c.name'''\nprint(conn.execute(sql).fetchall())",
                  "[('Ana', 925.0), ('Ben', 170.0), ('Cy', 1035.0), ('Di', None)]",
                  "LEFT JOIN keeps Di; the SUM of no values is NULL, which Python shows as `None`.",
                  tags=("sql", "joins")),
    DebugExercise("t07.dbg.quotes", "This should list the names of York customers (`[('Ben',)]`). Fix the query.",
                  SHOP + "result = conn.execute('SELECT name FROM customers WHERE city = York').fetchall()",
                  SHOP + "result = conn.execute(\"SELECT name FROM customers WHERE city = 'York'\").fetchall()",
                  (C("result == [('Ben',)]", expr="result", expected=[["Ben"]]),),
                  "Without quotes, SQL reads York as a column name. Text values need single quotes "
                  "(or better, a `?` placeholder).",
                  hints=("Read the 'no such column' explanation.",), tags=("sql",)),
    DebugExercise("t07.dbg.having", "This should list products with total revenue over 100, but errors. Fix it.",
                  SHOP + "sql = 'SELECT product, SUM(amount) FROM orders WHERE SUM(amount) > 100 GROUP BY product ORDER BY product'\nresult = conn.execute(sql).fetchall()",
                  SHOP + "sql = 'SELECT product, SUM(amount) FROM orders GROUP BY product HAVING SUM(amount) > 100 ORDER BY product'\nresult = conn.execute(sql).fetchall()",
                  (C("Correct groups", expr="result", expected=[["desk", 150.0], ["laptop", 1850.0]]),),
                  "Aggregates can't be used in WHERE because WHERE runs before grouping. Use HAVING "
                  "after GROUP BY.",
                  hints=("Which clause filters groups?",), tags=("sql", "groupby")),
    DebugExercise("t07.dbg.param_tuple", "This should insert Eve from Bath, but crashes. Fix it.",
                  SHOP + "city = 'Bath'\nconn.execute('INSERT INTO customers (name, city) VALUES (?, ?)', ('Eve'))\nconn.execute('UPDATE customers SET city = ? WHERE name = ?', (city, 'Eve'))\nresult = conn.execute(\"SELECT name, city FROM customers WHERE name = 'Eve'\").fetchall()",
                  SHOP + "city = 'Bath'\nconn.execute('INSERT INTO customers (name, city) VALUES (?, ?)', ('Eve', city))\nconn.execute('UPDATE customers SET city = ? WHERE name = ?', (city, 'Eve'))\nresult = conn.execute(\"SELECT name, city FROM customers WHERE name = 'Eve'\").fetchall()",
                  (C("Eve from Bath inserted", expr="result", expected=[["Eve", "Bath"]]),),
                  "There are two `?` placeholders, so two values are needed. Also `('Eve')` isn't even a "
                  "tuple — it's just a string in brackets.",
                  hints=("Count the `?` placeholders and the values.",), tags=("sql", "tuples")),
    CodingExercise("t07.code.select", "Using the shop database, store in `big_orders` the `product` and "
                   "`amount` of orders with amount **≥ 100**, sorted by amount descending (use `fetchall()`).",
                   SHOP + "big_orders = ...\n",
                   SHOP + "big_orders = conn.execute('SELECT product, amount FROM orders WHERE amount >= 100 ORDER BY amount DESC').fetchall()",
                   (C("Correct rows", expr="big_orders", expected=[["laptop", 950.0], ["laptop", 900.0], ["desk", 150.0]]),
                    C("Rows are tuples", expr="type(big_orders[0]).__name__", expected="tuple")),
                   "Filter with WHERE, sort with ORDER BY … DESC.",
                   hints=("`SELECT product, amount FROM orders WHERE ... ORDER BY ...`",), tags=("sql",)),
    CodingExercise("t07.code.groupby", "Store in `city_revenue` a list of `(city, total)` tuples: total order "
                   "amount per customer city, highest first. Hint: you need a JOIN and GROUP BY.",
                   SHOP + "city_revenue = ...\n",
                   SHOP + "city_revenue = conn.execute('''SELECT c.city, SUM(o.amount) AS total FROM orders o\nJOIN customers c ON o.customer_id = c.id GROUP BY c.city ORDER BY total DESC''').fetchall()",
                   (C("Correct totals", expr="city_revenue", expected=[["Leeds", 1960.0], ["York", 170.0]]),),
                   "JOIN brings in the city; GROUP BY city aggregates; ORDER BY total DESC ranks.",
                   hints=("`JOIN customers c ON o.customer_id = c.id`", "`GROUP BY c.city`"),
                   tags=("sql", "joins", "groupby")),
    CodingExercise("t07.code.function", "Write `orders_for(conn, name)` that **returns** the list of products "
                   "ordered by the customer with that name, alphabetically, using a `?` placeholder.",
                   SHOP + "\ndef orders_for(conn, name):\n    ...\n",
                   SHOP + "\ndef orders_for(conn, name):\n    sql = '''SELECT o.product FROM orders o JOIN customers c ON o.customer_id = c.id\n             WHERE c.name = ? ORDER BY o.product'''\n    return [row[0] for row in conn.execute(sql, (name,))]",
                   (C("orders_for(conn, 'Ana')", expr="orders_for(conn, 'Ana')", expected=["laptop", "mouse"]),
                    C("Unknown customer → []", expr="orders_for(conn, 'Zed')", expected=[]),
                    C("Injection attempt returns nothing", expr="orders_for(conn, \"x' OR '1'='1\")", expected=[])),
                   "Parameterised queries are both correct and safe. A list comprehension pulls the "
                   "first column out of each row tuple.",
                   hints=("`conn.execute(sql, (name,))`", "`[row[0] for row in ...]`"),
                   tags=("sql", "functions", "security")),
)

TOPIC = Topic(
    id="t07", number=7, title="SQL", icon="🗄️",
    summary="SQLite from Python: SELECT, WHERE, aggregates, GROUP BY/HAVING, JOINs, safe parameters, pandas.",
    lessons=(L1, L2, L3, L4, L5), items=ITEMS, prerequisites=("t05",),
)
