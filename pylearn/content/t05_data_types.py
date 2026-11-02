from .models import (MCQ, Check as C, CodingExercise, DebugExercise, Example as E,
                     Lesson, Option as O, PredictOutput, Topic)

L1 = Lesson(
    id="t05.l1",
    title="Strings and indexing",
    body="""
A **string** is a sequence of characters. Each character has a position
(**index**), counting from **0**. Negative indices count from the end.

```
 text:   P   y   t   h   o   n
 index:  0   1   2   3   4   5
 neg:   -6  -5  -4  -3  -2  -1
```

```python
word = "Python"
word[0]     # 'P'
word[-1]    # 'n'  (last character)
len(word)   # 6
```

### Useful string methods
| Method | Result for `"  Data Science  "` |
|---|---|
| `.strip()` | `'Data Science'` |
| `.lower()` / `.upper()` | `'  data science  '` / `'  DATA SCIENCE  '` |
| `.replace("Data", "Big")` | `'  Big Science  '` |
| `.split()` | `['Data', 'Science']` |
| `.startswith("  D")` | `True` |

`"-".join(["a", "b", "c"])` → `'a-b-c'` (the reverse of `split`).

Strings are **immutable**: methods return a *new* string. `name.upper()` alone
does nothing useful — write `name = name.upper()`.
""",
    examples=(
        E("Indexing", 'word = "Python"\nprint(word[0], word[3], word[-1], word[-2])\nprint(len(word))'),
        E("Cleaning text", 'raw = "  Data Science  "\nprint(repr(raw.strip()))\nprint(raw.strip().lower())\nprint(raw.split())\nprint("-".join(["2024", "06", "30"]))'),
        E("Strings are immutable", 'name = "ada"\nname.upper()\nprint(name)\nname = name.upper()\nprint(name)'),
    ),
    key_points=("Indices start at 0; `-1` is the last item.", "String methods return new strings.",
                "`split()` turns text into a list; `join()` does the reverse."),
)

L2 = Lesson(
    id="t05.l2",
    title="Slicing in depth",
    body="""
A **slice** extracts part of a sequence (string, list or tuple):

```
sequence[start : stop : step]
```
* `start` is **included**, `stop` is **excluded** (just like `range`).
* Omit `start` → from the beginning. Omit `stop` → to the end.
* `step` skips items; a negative step goes backwards.

```
 letters:  a   b   c   d   e   f
 index:    0   1   2   3   4   5
```
| Slice | Result | Read it as |
|---|---|---|
| `letters[1:4]` | `['b','c','d']` | from 1 up to (not incl.) 4 |
| `letters[:3]` | `['a','b','c']` | the first 3 |
| `letters[3:]` | `['d','e','f']` | from index 3 to the end |
| `letters[-2:]` | `['e','f']` | the last 2 |
| `letters[:-1]` | `['a'..'e']` | everything except the last |
| `letters[::2]` | `['a','c','e']` | every 2nd |
| `letters[::-1]` | `['f'..'a']` | reversed |

### Think of the cuts *between* items
Index numbers mark the gaps between elements; `[1:4]` cuts at gap 1 and gap 4.
The length of `s[a:b]` is `b - a` (when in range).

### Slicing never raises IndexError
`letters[10]` crashes, but `letters[2:100]` just returns what exists. That's
handy, but it can also hide bugs.

### Slices make copies (for lists)
`copy = data[:]` is a new list; changing `copy` won't change `data`.

### In data science
`values[:5]` previews the first rows, `values[-7:]` takes the last week,
`train, test = data[:80], data[80:]` splits a dataset.
""",
    examples=(
        E("Slice table", "letters = ['a', 'b', 'c', 'd', 'e', 'f']\nprint(letters[1:4])\nprint(letters[:3])\nprint(letters[3:])\nprint(letters[-2:])\nprint(letters[:-1])\nprint(letters[::2])\nprint(letters[::-1])"),
        E("Slicing strings", 'date = "2024-06-30"\nyear = date[:4]\nmonth = date[5:7]\nday = date[-2:]\nprint(year, month, day)\nprint("racecar"[::-1])'),
        E("No IndexError with slices", "nums = [1, 2, 3]\nprint(nums[1:100])\nprint(nums[5:])\nprint(nums[5])",
          "The last line crashes: single indexes must exist, slices needn't."),
        E("Train/test split", "data = list(range(1, 11))\nsplit = int(len(data) * 0.8)\ntrain, test = data[:split], data[split:]\nprint('train', train)\nprint('test ', test)"),
    ),
    key_points=("`s[start:stop:step]` — stop is excluded.", "`[:n]` first n, `[-n:]` last n, `[::-1]` reversed.",
                "Slices don't raise IndexError and return copies."),
)

L3 = Lesson(
    id="t05.l3",
    title="Lists: ordered, mutable collections",
    body="""
A **list** holds an ordered collection of values in square brackets:

```python
prices = [3.5, 2.0, 7.25]
prices.append(4.0)      # add to the end
prices.insert(0, 1.0)   # insert at position 0
prices.remove(2.0)      # remove first matching value
last = prices.pop()     # remove and return the last item
prices[1] = 9.99        # replace an item — lists are MUTABLE
```

| Operation | Meaning |
|---|---|
| `len(lst)` | number of items |
| `x in lst` | membership test |
| `lst.sort()` | sort **in place** (returns `None`!) |
| `sorted(lst)` | returns a **new** sorted list |
| `sum(lst)`, `min(lst)`, `max(lst)` | aggregates |
| `lst.count(x)`, `lst.index(x)` | counting / searching |

### ⚠️ Trap 1: `.sort()` returns None
```python
nums = [3, 1, 2]
nums = nums.sort()   # BUG: nums is now None
```
Use `nums.sort()` on its own, or `nums = sorted(nums)`.

### ⚠️ Trap 2: aliasing
`b = a` does **not** copy a list; both names refer to the *same* list.
```python
a = [1, 2]
b = a
b.append(3)
print(a)      # [1, 2, 3]  — a changed too!
c = a.copy()  # or a[:] or list(a) → an independent copy
```

### List comprehensions
A compact way to build a list from another:
```python
squares = [n ** 2 for n in range(5)]            # [0, 1, 4, 9, 16]
evens   = [n for n in range(10) if n % 2 == 0]  # with a filter
```
""",
    examples=(
        E("Mutating a list", "prices = [3.5, 2.0, 7.25]\nprices.append(4.0)\nprices.insert(0, 1.0)\nprices.remove(2.0)\nlast = prices.pop()\nprices[1] = 9.99\nprint(prices, last)"),
        E("sort() vs sorted()", "nums = [3, 1, 2]\nnew = sorted(nums)\nprint(nums, new)\nresult = nums.sort()\nprint(nums, result)"),
        E("Aliasing", "a = [1, 2]\nb = a\nb.append(3)\nprint('a:', a)\nc = a.copy()\nc.append(4)\nprint('a:', a, 'c:', c)\nprint(a is b, a is c)"),
        E("Comprehensions", "squares = [n ** 2 for n in range(5)]\nevens = [n for n in range(10) if n % 2 == 0]\nnames = ['ana', 'ben']\nprint(squares, evens, [n.title() for n in names])"),
    ),
    key_points=("Lists are ordered and mutable.", "`.sort()` sorts in place and returns `None`.",
                "`b = a` shares one list; use `.copy()` for a real copy."),
)

L4 = Lesson(
    id="t05.l4",
    title="Tuples: fixed records and unpacking",
    body="""
A **tuple** is like a list, but **immutable** — it can't be changed after
creation. Use round brackets (or just commas):

```python
point = (51.5, -0.12)      # latitude, longitude
rgb = 255, 128, 0          # brackets are optional
single = (5,)              # a one-item tuple needs a trailing comma!
not_a_tuple = (5)          # this is just the int 5
```

Indexing and slicing work exactly as for lists, but `point[0] = 52` raises
`TypeError: 'tuple' object does not support item assignment`.

### When to use a tuple instead of a list
| Tuple | List |
|---|---|
| a fixed *record* with a known shape: `(name, age)`, `(x, y)` | a growing collection of similar things |
| can be a dictionary key | cannot be a dictionary key |
| signals "don't change this" | expected to change |

### Unpacking
```python
lat, lon = point                 # assign each item to a name
a, b = b, a                      # swap two variables
for name, score in [("Ana", 81), ("Ben", 67)]:
    print(name, score)           # unpack inside a loop
first, *rest = [1, 2, 3, 4]      # first = 1, rest = [2, 3, 4]
```
SQL query results arrive as lists of tuples — one tuple per row — so you'll use
this constantly in the SQL topic.
""",
    examples=(
        E("Creating tuples", "point = (51.5, -0.12)\nrgb = 255, 128, 0\nsingle = (5,)\nnot_a_tuple = (5)\nprint(type(point), type(rgb), type(single), type(not_a_tuple))"),
        E("Tuples are immutable", "point = (51.5, -0.12)\nprint(point[0])\npoint[0] = 52"),
        E("Unpacking", "lat, lon = (51.5, -0.12)\nprint(lat, lon)\na, b = 1, 2\na, b = b, a\nprint(a, b)\nfirst, *rest = [1, 2, 3, 4]\nprint(first, rest)\nfor name, score in [('Ana', 81), ('Ben', 67)]:\n    print(f'{name} scored {score}')"),
    ),
    key_points=("Tuples are immutable sequences.", "`(5,)` is a tuple; `(5)` is an int.",
                "Unpacking: `a, b = pair`; works in for loops too."),
)

L5 = Lesson(
    id="t05.l5",
    title="Dictionaries and sets",
    body="""
A **dictionary** maps **keys** to **values**. Instead of looking things up by
position, you look them up by key:

```python
stock = {"apples": 12, "pears": 0, "kiwis": 30}
stock["apples"]          # 12
stock["plums"] = 7       # add a new key
stock["apples"] += 3     # update a value
del stock["pears"]       # remove a key
"kiwis" in stock         # True — checks KEYS, not values
```

### Safe lookups
`stock["mango"]` raises `KeyError`. Use `stock.get("mango", 0)` to supply a
default when a key may be missing.

### Looping
```python
for key in stock:                   # keys
for value in stock.values():        # values
for key, value in stock.items():    # both — the most common form
```

### The counting pattern
```python
counts = {}
for word in ["a", "b", "a", "c", "a"]:
    counts[word] = counts.get(word, 0) + 1
# {'a': 3, 'b': 1, 'c': 1}
```

### Grouping pattern (dict of lists)
```python
by_city = {}
for name, city in [("Ana", "Leeds"), ("Ben", "York"), ("Cy", "Leeds")]:
    by_city.setdefault(city, []).append(name)
```

### Rules
* Keys must be unique and immutable (str, int, tuple). Values can be anything.
* Dicts keep insertion order (Python 3.7+).
* A *list of dicts* is a natural way to represent rows of data — and it's
  exactly what `pandas.DataFrame(...)` accepts.

### Sets
A **set** is an unordered collection of **unique** values — great for removing
duplicates and membership tests: `set([3, 1, 3])` → `{1, 3}`.
`a & b` (intersection), `a | b` (union), `a - b` (difference).
""",
    examples=(
        E("Dictionary basics", 'stock = {"apples": 12, "pears": 0, "kiwis": 30}\nstock["plums"] = 7\nstock["apples"] += 3\ndel stock["pears"]\nprint(stock)\nprint("kiwis" in stock, 30 in stock)\nprint(stock.get("mango", 0))'),
        E("Looping over items", 'stock = {"apples": 15, "kiwis": 30, "plums": 7}\nfor fruit, qty in stock.items():\n    print(f"{fruit:>8}: {qty}")\nprint(sum(stock.values()))'),
        E("Counting words", 'text = "the cat and the hat and the bat"\ncounts = {}\nfor word in text.split():\n    counts[word] = counts.get(word, 0) + 1\nprint(counts)\nprint(max(counts, key=counts.get))'),
        E("List of dicts = rows", 'rows = [\n    {"name": "Ana", "city": "Leeds", "spend": 120},\n    {"name": "Ben", "city": "York", "spend": 80},\n    {"name": "Cy", "city": "Leeds", "spend": 45},\n]\ntotals = {}\nfor r in rows:\n    totals[r["city"]] = totals.get(r["city"], 0) + r["spend"]\nprint(totals)'),
        E("Sets", "a = {1, 2, 3, 4}\nb = {3, 4, 5}\nprint(a & b, a | b, a - b)\nprint(sorted(set(['x', 'y', 'x', 'z', 'y'])))"),
    ),
    key_points=("Dicts map unique keys to values.", "Use `.get(key, default)` for missing keys.",
                "`for k, v in d.items()` loops over pairs.", "Sets store unique values."),
)

ITEMS = (
    MCQ("t05.mcq.slice_basic", "`nums = [10, 20, 30, 40, 50]`. What is `nums[1:3]`?",
        (O("`[20, 30]`", True, "Start index 1 (20) is included; stop index 3 (40) is excluded."),
         O("`[20, 30, 40]`", False, "The stop index is *excluded*, so 40 (index 3) isn't included."),
         O("`[10, 20, 30]`", False, "Indexing starts at 0, so index 1 is 20, not 10."),
         O("`[10, 20]`", False, "That's `nums[0:2]`.")),
        "Slices include the start and exclude the stop; length = stop - start.", tags=("slicing",)),
    MCQ("t05.mcq.slice_neg", "Which expression gives the **last three** items of a list `xs`?",
        (O("`xs[-3:]`", True, "Start 3 from the end and go to the end."),
         O("`xs[:-3]`", False, "That's everything *except* the last three."),
         O("`xs[-3]`", False, "That's a single item — the third from last — not a slice."),
         O("`xs[3:]`", False, "That skips the *first* three, which only equals the last three if "
           "the list has exactly six items.")),
        "`[-n:]` takes the last n; `[:-n]` drops the last n.", tags=("slicing",)),
    MCQ("t05.mcq.sort_none", "What is printed?",
        (O("`None`", True, "`.sort()` sorts the list in place and returns `None`, which is stored in `b`."),
         O("`[1, 2, 3]`", False, "That's `a` after sorting, but `b` holds `.sort()`'s return value, "
           "which is `None`. Use `sorted(a)` to get a new list."),
         O("`[3, 1, 2]`", False, "`b` is not a copy of `a`; it's the return value of `.sort()`."),
         O("An error", False, "No error occurs; the bug is silent, which makes it tricky.")),
        "In-place methods (`.sort()`, `.append()`, `.reverse()`) return `None`.",
        code="a = [3, 1, 2]\nb = a.sort()\nprint(b)", tags=("lists", "return-vs-print")),
    MCQ("t05.mcq.alias", "What does this print?",
        (O("`[1, 2, 3, 4]`", True, "`b = a` makes `b` another name for the same list, so the append "
           "is visible through `a`."),
         O("`[1, 2, 3]`", False, "That would be true if `b` were a copy (`b = a.copy()`). Assignment "
           "never copies a list."),
         O("`[4]`", False, "`b` refers to the whole existing list, not a new empty one."),
         O("An error", False, "Appending through either name is allowed.")),
        "Assignment binds a second name to the same object. Copy lists with `.copy()` or `[:]`.",
        code="a = [1, 2, 3]\nb = a\nb.append(4)\nprint(a)", tags=("lists", "aliasing")),
    MCQ("t05.mcq.tuple_choice", "Which is the best choice to store a GPS coordinate that should never change?",
        (O("A tuple `(lat, lon)`", True, "A fixed-size record that shouldn't change is exactly what "
           "tuples are for, and it can be a dict key."),
         O("A list `[lat, lon]`", False, "It works, but lists signal 'this will change' and can be "
           "modified accidentally; they also can't be dict keys."),
         O("A dict `{lat: lon}`", False, "This would use the latitude value as a key — not a "
           "meaningful structure."),
         O("A set `{lat, lon}`", False, "Sets are unordered (you'd lose which is lat and which is lon) "
           "and drop duplicates.")),
        "Tuples are immutable records; lists are mutable collections.", tags=("tuples",)),
    MCQ("t05.mcq.single_tuple", "What is `type((7))`?",
        (O("`int`", True, "Brackets alone are just grouping. A one-item tuple needs a comma: `(7,)`."),
         O("`tuple`", False, "It's the comma, not the brackets, that makes a tuple."),
         O("`list`", False, "Lists use square brackets."),
         O("`set`", False, "Sets use curly braces.")),
        "`(7,)` is a tuple; `(7)` is the integer 7.", tags=("tuples",)),
    MCQ("t05.mcq.dict_in", "`d = {'a': 1, 'b': 2}`. What is `2 in d`?",
        (O("`False`", True, "`in` checks the dictionary's **keys**. 2 is a value, not a key."),
         O("`True`", False, "2 is a *value*. Use `2 in d.values()` to search values."),
         O("`KeyError`", False, "`in` never raises KeyError; it just returns True/False."),
         O("`1`", False, "`in` returns a bool.")),
        "`key in d` tests keys. Use `d.values()` to test values.", tags=("dicts",)),
    MCQ("t05.mcq.dict_get", "Why use `counts.get(word, 0) + 1` instead of `counts[word] + 1`?",
        (O("It avoids a KeyError the first time a word appears", True, "`.get` returns the default "
           "(0) when the key doesn't exist yet."),
         O("It's faster", False, "Speed isn't the reason; correctness is."),
         O("It sorts the dictionary", False, "`.get` only reads one value."),
         O("`counts[word]` doesn't work on strings", False, "String keys work fine with `[]` — "
           "*if* the key exists.")),
        "`d.get(key, default)` returns default for missing keys.", tags=("dicts",)),
    PredictOutput("t05.pred.slices", "What does this code print?",
                  "s = 'DATASCIENCE'\nprint(s[:4])\nprint(s[4:])\nprint(s[-3:])\nprint(s[::3])",
                  "DATA\nSCIENCE\nNCE\nDAIC",
                  "`[:4]` first four, `[4:]` from index 4, `[-3:]` last three, `[::3]` every third "
                  "character starting at index 0 (indexes 0, 3, 6, 9: D, A, I, C).",
                  tags=("slicing", "strings")),
    PredictOutput("t05.pred.reverse_slice", "What does this code print?",
                  "nums = [1, 2, 3, 4, 5, 6]\nprint(nums[::-1])\nprint(nums[1::2])\nprint(nums[4:1:-1])",
                  "[6, 5, 4, 3, 2, 1]\n[2, 4, 6]\n[5, 4, 3]",
                  "A negative step walks backwards: `[4:1:-1]` starts at index 4 (5) and stops before index 1.",
                  tags=("slicing",)),
    PredictOutput("t05.pred.list_methods", "What does this code print?",
                  "xs = [5, 3]\nxs.append(9)\nxs.insert(1, 7)\nprint(xs)\nprint(xs.pop(), xs)",
                  "[5, 7, 3, 9]\n9 [5, 7, 3]",
                  "`insert(1, 7)` puts 7 at index 1. `pop()` removes and returns the last item.",
                  tags=("lists",)),
    PredictOutput("t05.pred.unpack", "What does this code print?",
                  "pairs = [('x', 1), ('y', 2)]\nfor letter, number in pairs:\n    print(letter * number)",
                  "x\nyy",
                  "Each tuple is unpacked into `letter` and `number`; `'y' * 2` repeats the string.",
                  tags=("tuples", "loops")),
    PredictOutput("t05.pred.dict_loop", "What does this code print?",
                  "ages = {'Ana': 31, 'Ben': 25}\nages['Cy'] = 40\nages['Ana'] += 1\nfor name, age in ages.items():\n    print(name, age)\nprint(len(ages))",
                  "Ana 32\nBen 25\nCy 40\n3",
                  "Dicts keep insertion order. Updating an existing key keeps its position.",
                  tags=("dicts",)),
    PredictOutput("t05.pred.strings", "What does this code print?",
                  "t = '  Hello World  '\nprint(t.strip().lower())\nprint(t.split())\nprint(len(t.strip()))",
                  "hello world\n['Hello', 'World']\n11",
                  "`strip` removes outer spaces; `split()` splits on whitespace; 'Hello World' has 11 characters.",
                  tags=("strings",)),
    DebugExercise("t05.dbg.sort_none", "`top_three` should return the three largest values, largest first. "
                  "It crashes. Fix it.",
                  "def top_three(values):\n    ordered = values.sort(reverse=True)\n    return ordered[:3]",
                  "def top_three(values):\n    ordered = sorted(values, reverse=True)\n    return ordered[:3]",
                  (C("top_three([4, 9, 1, 7, 3]) == [9, 7, 4]", expr="top_three([4, 9, 1, 7, 3])", expected=[9, 7, 4]),
                   C("Original list is not modified", expr="(lambda v: (top_three(v), v)[1])([2, 1, 3])", expected=[2, 1, 3])),
                  "`.sort()` returns `None`, so `ordered[:3]` fails. `sorted()` returns a new list and "
                  "doesn't modify the caller's data.",
                  hints=("What does `.sort()` return?",), tags=("lists", "slicing")),
    DebugExercise("t05.dbg.tuple_assign", "This should change the first score to 90 and print `[90, 75]`. Fix it.",
                  "scores = (80, 75)\nscores[0] = 90\nprint(scores)",
                  "scores = [80, 75]\nscores[0] = 90\nprint(scores)",
                  (C("Prints [90, 75]", stdout_equals="[90, 75]"),),
                  "Tuples are immutable. If the data must change, use a list.",
                  hints=("Read the TypeError: which type can't be changed?",), tags=("tuples",)),
    DebugExercise("t05.dbg.keyerror", "This counts colours, but crashes with a KeyError. Make `counts` "
                  "equal `{'red': 2, 'blue': 1}`.",
                  "counts = {}\nfor c in ['red', 'blue', 'red']:\n    counts[c] = counts[c] + 1",
                  "counts = {}\nfor c in ['red', 'blue', 'red']:\n    counts[c] = counts.get(c, 0) + 1",
                  (C("counts is correct", expr="counts", expected={"red": 2, "blue": 1}),),
                  "The first time a colour appears it isn't a key yet, so `counts[c]` fails. "
                  "`counts.get(c, 0)` starts missing keys at 0.",
                  hints=("What's in `counts` on the very first pass?",), tags=("dicts",)),
    CodingExercise("t05.code.slicing", "Given `readings` (14 daily values), create: `first_week` (first 7), "
                   "`last_three` (last 3), `every_other` (items at even indexes) and `reversed_readings`.",
                   "readings = [3, 5, 2, 8, 6, 9, 4, 7, 1, 5, 6, 8, 2, 4]\n",
                   "readings = [3, 5, 2, 8, 6, 9, 4, 7, 1, 5, 6, 8, 2, 4]\nfirst_week = readings[:7]\nlast_three = readings[-3:]\nevery_other = readings[::2]\nreversed_readings = readings[::-1]",
                   (C("first_week", expr="first_week", expected=[3, 5, 2, 8, 6, 9, 4]),
                    C("last_three", expr="last_three", expected=[8, 2, 4]),
                    C("every_other", expr="every_other", expected=[3, 2, 6, 4, 1, 6, 2]),
                    C("reversed_readings", expr="reversed_readings", expected=[4, 2, 8, 6, 5, 1, 7, 4, 9, 6, 8, 2, 5, 3]),
                    C("readings unchanged", expr="readings[0]", expected=3)),
                   "Slices are the idiomatic way to take windows of data.",
                   hints=("`[:n]`, `[-n:]`, `[::step]`",), tags=("slicing",)),
    CodingExercise("t05.code.word_count", "Write `word_counts(text)` that returns a dict mapping each "
                   "lower-cased word to how many times it appears.",
                   "def word_counts(text):\n    ...\n",
                   "def word_counts(text):\n    counts = {}\n    for w in text.lower().split():\n        counts[w] = counts.get(w, 0) + 1\n    return counts",
                   (C("Counts a simple sentence", expr="word_counts('the cat the hat')", expected={"the": 2, "cat": 1, "hat": 1}),
                    C("Case-insensitive", expr="word_counts('AI ai Ai')", expected={"ai": 3}),
                    C("Empty text → empty dict", expr="word_counts('')", expected={})),
                   "The counting pattern `d[k] = d.get(k, 0) + 1` is everywhere in data work.",
                   hints=("`.lower().split()` gives you clean words.",), tags=("dicts", "strings")),
    CodingExercise("t05.code.records", "`rows` is a list of `(name, dept, salary)` tuples. Build a dict "
                   "`by_dept` mapping each department to its **total** salary, and a variable "
                   "`highest_paid` holding the name of the highest earner.",
                   "rows = [('Ana', 'Data', 52000), ('Ben', 'Ops', 38000),\n        ('Cy', 'Data', 61000), ('Di', 'Ops', 41000)]\n",
                   "rows = [('Ana', 'Data', 52000), ('Ben', 'Ops', 38000),\n        ('Cy', 'Data', 61000), ('Di', 'Ops', 41000)]\nby_dept = {}\nfor name, dept, salary in rows:\n    by_dept[dept] = by_dept.get(dept, 0) + salary\nhighest_paid = max(rows, key=lambda r: r[2])[0]",
                   (C("by_dept totals", expr="by_dept", expected={"Data": 113000, "Ops": 79000}),
                    C("highest_paid == 'Cy'", expr="highest_paid", expected="Cy")),
                   "Unpack tuples in the loop header, and use `max(..., key=...)` to find the best record.",
                   hints=("`for name, dept, salary in rows:`", "`max(rows, key=lambda r: r[2])` returns the whole tuple."),
                   tags=("tuples", "dicts")),
)

TOPIC = Topic(
    id="t05", number=5, title="Data Types", icon="🗂️",
    summary="Strings, slicing, lists, tuples, dictionaries and sets — in depth.",
    lessons=(L1, L2, L3, L4, L5), items=ITEMS, prerequisites=("t04",),
)
