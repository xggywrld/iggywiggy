from .models import (MCQ, Check as C, CodingExercise, DebugExercise, Example as E,
                     Lesson, Option as O, PredictOutput, Topic)

L1 = Lesson(
    id="t04.l1",
    title="Defining and calling functions",
    body="""
A **function** is a named, reusable block of code. You *define* it once and
*call* it as often as you like.

```python
def greet(name):            # 'name' is a PARAMETER
    print(f"Hello, {name}!")

greet("Ada")                # "Ada" is an ARGUMENT
greet("Linus")
```

* `def` starts the definition; the line ends with `:`; the body is indented.
* Defining a function does **not** run it. The body runs only when called.
* **Parameters** are the names in the definition; **arguments** are the values
  you pass in the call. Arguments are matched to parameters in order.

### Why functions?
* **Don't repeat yourself** — write the logic once.
* **Name an idea** — `clean_prices(df)` is easier to read than 15 lines.
* **Test in isolation** — data pipelines are built from small, tested functions.

### Default and keyword arguments
```python
def describe(value, unit="kg", decimals=1):
    return f"{value:.{decimals}f} {unit}"

describe(3.14159)                 # '3.1 kg'
describe(3.14159, "m")            # '3.1 m'
describe(3.14159, decimals=3)     # '3.142 kg'  (keyword argument)
```
""",
    examples=(
        E("Define, then call", 'def greet(name):\n    print(f"Hello, {name}!")\n\nprint("Before calling")\ngreet("Ada")\ngreet("Linus")'),
        E("Defaults and keywords", 'def describe(value, unit="kg", decimals=1):\n    return f"{value:.{decimals}f} {unit}"\n\nprint(describe(3.14159))\nprint(describe(3.14159, "m"))\nprint(describe(3.14159, decimals=3))'),
        E("Missing an argument", "def area(width, height):\n    return width * height\n\nprint(area(3))",
          "Read the error explanation, then pass a second argument."),
    ),
    key_points=("`def name(params):` defines; `name(args)` calls.", "Defining ≠ running.",
                "Defaults make parameters optional; keywords make calls readable."),
)

L2 = Lesson(
    id="t04.l2",
    title="return vs print — the most important distinction",
    body="""
This is the concept beginners most often get wrong, so take your time.

| | `print(x)` | `return x` |
|---|---|---|
| What it does | **shows** `x` on the screen | **sends `x` back** to the code that called the function |
| Who sees it | a human | the program |
| Can you use the result later? | ❌ no — it's gone | ✅ yes — store it, add to it, pass it on |
| Ends the function? | no | **yes, immediately** |

### See the difference
```python
def add_print(a, b):
    print(a + b)

def add_return(a, b):
    return a + b

x = add_print(2, 3)    # shows 5 ... but x is None!
y = add_return(2, 3)   # shows nothing ... y is 5
print(x, y)            # None 5
```

`add_print` *displays* 5, but gives nothing back, so `x` is `None`.
Try `add_print(2, 3) + 1` — it crashes with
`TypeError: unsupported operand type(s) for +: 'NoneType' and 'int'`.

### `None`: the value of "nothing"
A function **without** a `return` statement (or with a bare `return`) gives
back `None`. If you ever see an unexpected `None` printed, or a `'NoneType'`
error, ask: *"did that function print instead of return?"*

### return ends the function
```python
def sign(n):
    if n > 0:
        return "positive"
    if n < 0:
        return "negative"
    return "zero"
```
As soon as a `return` runs, the function stops — no `else` needed.

### Returning several values
Return a tuple, and unpack it:
```python
def min_max(values):
    return min(values), max(values)

low, high = min_max([4, 9, 1])
```

### Rule of thumb
**Functions should `return` results. Only the top-level code should
`print` them.** That makes functions reusable: a function that returns an
average can be used in a report, a chart, a test or another calculation; one
that prints it can only be looked at.
""",
    examples=(
        E("print vs return side by side", "def add_print(a, b):\n    print(a + b)\n\ndef add_return(a, b):\n    return a + b\n\nx = add_print(2, 3)\ny = add_return(2, 3)\nprint('x =', x)\nprint('y =', y)"),
        E("Using a returned value", "def add_return(a, b):\n    return a + b\n\ntotal = add_return(2, 3) + add_return(10, 20)\nprint(total)\nprint(add_return(add_return(1, 2), 3))",
          "Returned values can be combined, stored and passed to other functions."),
        E("The None crash", "def add_print(a, b):\n    print(a + b)\n\nresult = add_print(2, 3) + 1",
          "This crashes — read the explanation to see why."),
        E("return stops the function", "def first_negative(values):\n    for v in values:\n        if v < 0:\n            return v\n        print('checked', v)\n    return None\n\nprint(first_negative([3, 8, -2, 7, -9]))"),
        E("Returning several values", "def min_max(values):\n    return min(values), max(values)\n\nresult = min_max([4, 9, 1])\nprint(result, type(result))\nlow, high = min_max([4, 9, 1])\nprint(low, high)"),
    ),
    key_points=("`print` shows a value to a human; `return` hands it back to the program.",
                "No `return` → the function returns `None`.",
                "`return` exits the function immediately.",
                "Functions should return; the caller decides whether to print."),
)

L3 = Lesson(
    id="t04.l3",
    title="Scope, docstrings and composing functions",
    body="""
### Local scope
Variables created **inside** a function are *local*: they exist only while
the function runs and are invisible outside it.

```python
def calc():
    result = 42
calc()
print(result)   # NameError: name 'result' is not defined
```
To get a value out, **return** it. (Reading a global variable inside a function
works, but relying on globals makes code fragile — pass values as parameters.)

### Docstrings
A string on the first line of a function documents it; `help(func)` shows it.
```python
def mean(values):
    \"\"\"Return the arithmetic mean of a non-empty list of numbers.\"\"\"
    return sum(values) / len(values)
```

### Composing small functions
Data pipelines are chains of small functions, each doing one job:
```python
def clean(values):    return [v for v in values if v is not None]
def mean(values):     return sum(values) / len(values)
def report(values):   return f"mean = {mean(clean(values)):.2f}"
```

### Lambda (anonymous) functions
A tiny one-expression function, often used as a `key` for sorting:
```python
people = [("Ana", 31), ("Ben", 25)]
sorted(people, key=lambda p: p[1])   # sort by age
```
""",
    examples=(
        E("Local variables vanish", "def calc():\n    result = 42\n    return result\n\nanswer = calc()\nprint(answer)\nprint(result)",
          "`answer` works because the value was returned; `result` doesn't exist outside."),
        E("Docstrings and help()", 'def mean(values):\n    """Return the arithmetic mean of a non-empty list of numbers."""\n    return sum(values) / len(values)\n\nprint(mean([2, 4, 9]))\nprint(mean.__doc__)'),
        E("A tiny pipeline", "def clean(values):\n    return [v for v in values if v is not None]\n\ndef mean(values):\n    return sum(values) / len(values)\n\ndef report(values):\n    return f'mean = {mean(clean(values)):.2f}'\n\nprint(report([3, None, 4, 8, None]))"),
        E("Sorting with lambda", 'people = [("Ana", 31), ("Ben", 25), ("Cy", 40)]\nprint(sorted(people, key=lambda p: p[1]))\nprint(max(people, key=lambda p: p[1]))'),
    ),
    key_points=("Variables inside a function are local to it.", "Return values to share them.",
                "Build programs from small, single-purpose functions."),
)

ITEMS = (
    MCQ("t04.mcq.return_vs_print", "What is stored in `result`?",
        (O("`None`", True, "`double` prints 10 but has no `return`, so it gives back `None`."),
         O("`10`", False, "10 is *displayed* by `print`, but displaying isn't returning. The caller "
           "receives nothing."),
         O("`'10'`", False, "`print` doesn't convert and return text either; it returns `None`."),
         O("An error occurs", False, "Calling the function is fine; an error would only happen if "
           "you then tried to do maths with `result`.")),
        "Without `return`, a function returns `None` — even if it printed something.",
        code="def double(n):\n    print(n * 2)\n\nresult = double(5)", tags=("return-vs-print", "functions")),
    MCQ("t04.mcq.def_runs", "What does this program print?",
        (O("Only `end`", True, "Defining `hello` doesn't run it, and it's never called."),
         O("`hi` then `end`", False, "The body of a function only runs when the function is *called* "
           "with `hello()`."),
         O("Nothing", False, "The `print('end')` at the top level always runs."),
         O("An error", False, "Defining a function that is never called is perfectly valid.")),
        "A `def` creates the function; calling it runs the body.",
        code='def hello():\n    print("hi")\n\nprint("end")', tags=("functions",)),
    MCQ("t04.mcq.return_exits", "What does `check(5)` return?",
        (O("`'small'`", True, "5 < 10, so the first `return` runs and the function ends immediately."),
         O("`'big'`", False, "The second `return` is never reached because the first one already "
           "ended the function."),
         O("`['small', 'big']`", False, "A function returns one value per call; `return` stops it."),
         O("`None`", False, "A `return` with a value does run here.")),
        "`return` immediately exits the function.",
        code="def check(n):\n    if n < 10:\n        return 'small'\n    return 'big'", tags=("return-vs-print",)),
    MCQ("t04.mcq.scope", "What happens when this runs?",
        (O("`NameError`", True, "`total` is local to `f` and doesn't exist outside it."),
         O("It prints `3`", False, "The value is never returned, and local variables disappear when "
           "the function finishes."),
         O("It prints `None`", False, "That would happen with `print(f())`. Here we print `total`, "
           "which isn't defined at the top level."),
         O("It prints nothing", False, "The `print` runs and fails.")),
        "Local variables are only visible inside their function. Return values you need.",
        code="def f():\n    total = 1 + 2\n\nf()\nprint(total)", tags=("scope", "functions")),
    MCQ("t04.mcq.args_params", "In `def area(w, h):` ... `area(3, 4)`, which are the *parameters*?",
        (O("`w` and `h`", True, "Parameters are the names in the definition."),
         O("`3` and `4`", False, "Those are the *arguments* — the values passed in the call."),
         O("`area`", False, "That's the function's name."),
         O("All four", False, "Parameters (definition) and arguments (call) are different things.")),
        "Parameters receive the arguments' values when the function is called.", tags=("functions",)),
    PredictOutput("t04.pred.none_printed", "What does this code print?",
                  "def shout(word):\n    print(word.upper())\n\nprint(shout('hey'))",
                  "HEY\nNone",
                  "Inside the function `print` shows `HEY`. The function returns `None`, which the outer "
                  "`print` then shows.",
                  tags=("return-vs-print",),
                  common_wrong=(("HEY", "Don't forget the outer `print`: it prints the function's return "
                                 "value, which is `None` because there's no `return`."),
                                ("None", "The inner `print(word.upper())` runs first and shows `HEY`."),)),
    PredictOutput("t04.pred.return_used", "What does this code print?",
                  "def square(n):\n    return n * n\n\nx = square(3) + square(4)\nprint(x)",
                  "25",
                  "Each call returns a number (9 and 16), and returned values can be added: 25.",
                  tags=("return-vs-print",)),
    PredictOutput("t04.pred.defaults", "What does this code print?",
                  "def power(base, exp=2):\n    return base ** exp\n\nprint(power(3))\nprint(power(2, 5))\nprint(power(exp=3, base=2))",
                  "9\n32\n8",
                  "`exp` defaults to 2 when omitted. Keyword arguments can be given in any order.",
                  tags=("functions", "defaults")),
    PredictOutput("t04.pred.multi_return", "What does this code print?",
                  "def stats(values):\n    return min(values), max(values)\n\nresult = stats([5, 2, 8])\nprint(result)\nlo, hi = result\nprint(hi - lo)",
                  "(2, 8)\n6",
                  "Returning two values actually returns one tuple, which can be unpacked.",
                  tags=("functions", "tuples")),
    DebugExercise("t04.dbg.print_not_return", "`average` should *return* the mean so that the last line "
                  "prints `Rounded: 3.0`. Currently it crashes. Fix the function.",
                  "def average(values):\n    print(sum(values) / len(values))\n\nresult = average([2, 3, 4])\nprint('Rounded:', round(result, 1))",
                  "def average(values):\n    return sum(values) / len(values)\n\nresult = average([2, 3, 4])\nprint('Rounded:', round(result, 1))",
                  (C("average([2, 3, 4]) returns 3.0", expr="average([2, 3, 4])", expected=3.0),
                   C("average([1, 2]) returns 1.5", expr="average([1, 2])", expected=1.5),
                   C("Prints Rounded: 3.0", stdout_contains="Rounded: 3.0")),
                  "`print` only displays the value; `round(None, 1)` then fails. `return` hands the "
                  "value back so the caller can use it.",
                  hints=("What does `average` give back to `result`?",), tags=("return-vs-print",)),
    DebugExercise("t04.dbg.early_return", "`count_evens` should count the even numbers in a list "
                  "(for `[2, 4, 5, 6]` → 3) but returns 1. Fix it.",
                  "def count_evens(values):\n    count = 0\n    for v in values:\n        if v % 2 == 0:\n            count += 1\n        return count",
                  "def count_evens(values):\n    count = 0\n    for v in values:\n        if v % 2 == 0:\n            count += 1\n    return count",
                  (C("count_evens([2, 4, 5, 6]) == 3", expr="count_evens([2, 4, 5, 6])", expected=3),
                   C("count_evens([]) == 0", expr="count_evens([])", expected=0),
                   C("count_evens([1, 3]) == 0", expr="count_evens([1, 3])", expected=0)),
                  "The `return` was indented inside the loop, so the function ended after the first "
                  "item. Dedent it so it runs after the loop finishes.",
                  hints=("How many times does the loop run before `return`?",),
                  tags=("return-vs-print", "loops", "indentation")),
    CodingExercise("t04.code.celsius", "Write a function `to_fahrenheit(c)` that **returns** the "
                   "temperature in °F (`c * 9 / 5 + 32`). Do not print inside the function.",
                   "def to_fahrenheit(c):\n    ...\n",
                   "def to_fahrenheit(c):\n    return c * 9 / 5 + 32",
                   (C("to_fahrenheit(0) == 32", expr="to_fahrenheit(0)", expected=32.0),
                    C("to_fahrenheit(100) == 212", expr="to_fahrenheit(100)", expected=212.0),
                    C("to_fahrenheit(-40) == -40", expr="to_fahrenheit(-40)", expected=-40.0)),
                   "Returning the value lets the caller convert whole lists: "
                   "`[to_fahrenheit(t) for t in temps]`.",
                   hints=("Use `return`, not `print`.",), tags=("functions", "return-vs-print")),
    CodingExercise("t04.code.grade", "Write `grade(score)` that returns `'A'` for 70+, `'B'` for 60–69, "
                   "`'C'` for 50–59 and `'F'` otherwise.",
                   "def grade(score):\n    ...\n",
                   "def grade(score):\n    if score >= 70:\n        return 'A'\n    if score >= 60:\n        return 'B'\n    if score >= 50:\n        return 'C'\n    return 'F'",
                   (C("grade(85) == 'A'", expr="grade(85)", expected="A"),
                    C("grade(70) == 'A' (boundary)", expr="grade(70)", expected="A"),
                    C("grade(65) == 'B'", expr="grade(65)", expected="B"),
                    C("grade(50) == 'C' (boundary)", expr="grade(50)", expected="C"),
                    C("grade(12) == 'F'", expr="grade(12)", expected="F")),
                   "Because `return` exits immediately, each later `if` only runs when earlier ones failed.",
                   hints=("Test the highest band first.", "Remember the boundaries: 70 is an A."),
                   tags=("functions", "conditionals")),
    CodingExercise("t04.code.summary", "Write `summarise(values)` that returns a **tuple** "
                   "`(count, mean, max)` for a list of numbers. Return `(0, None, None)` for an empty list.",
                   "def summarise(values):\n    ...\n",
                   "def summarise(values):\n    if not values:\n        return (0, None, None)\n    return (len(values), sum(values) / len(values), max(values))",
                   (C("summarise([2, 4, 9])", expr="summarise([2, 4, 9])", expected=[3, 5.0, 9]),
                    C("Returns a tuple", expr="type(summarise([1])).__name__", expected="tuple"),
                    C("Empty list handled", expr="summarise([])", expected=[0, None, None])),
                   "Guard clauses (`if not values: return ...`) handle edge cases before the main logic.",
                   hints=("An empty list is falsy.",), tags=("functions", "tuples")),
)

TOPIC = Topic(
    id="t04", number=4, title="Functions", icon="🧩",
    summary="Defining functions, parameters, return vs print, None, scope and composition.",
    lessons=(L1, L2, L3), items=ITEMS, prerequisites=("t03",),
)
