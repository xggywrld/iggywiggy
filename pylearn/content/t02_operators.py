from .models import (MCQ, Check as C, CodingExercise, DebugExercise, Example as E,
                     Lesson, Option as O, PredictOutput, Topic)

L1 = Lesson(
    id="t02.l1",
    title="Arithmetic operators and precedence",
    body="""
| Operator | Meaning | Example | Result |
|---|---|---|---|
| `+` `-` `*` | add, subtract, multiply | `7 * 3` | `21` |
| `/` | true division (**always a float**) | `7 / 2` | `3.5` |
| `//` | floor division (rounds *down*) | `7 // 2` | `3` |
| `%` | modulo (remainder) | `7 % 2` | `1` |
| `**` | power | `2 ** 3` | `8` |

### Precedence (BODMAS / PEMDAS)
`**` first, then `*` `/` `//` `%`, then `+` `-`. Use brackets whenever in
doubt — they make intent clear:

```python
print(2 + 3 * 4)     # 14, not 20
print((2 + 3) * 4)   # 20
```

### Why `%` and `//` matter in data work
* `n % 2 == 0` tests whether a number is even.
* `minutes // 60` and `minutes % 60` split minutes into hours and minutes.
* `index % 7` cycles through days of the week.

### Augmented assignment
`total += 5` is shorthand for `total = total + 5` (also `-=`, `*=`, `/=`).
""",
    examples=(
        E("All the operators", "print(7 + 2, 7 - 2, 7 * 2)\nprint(7 / 2)\nprint(7 // 2)\nprint(7 % 2)\nprint(2 ** 10)"),
        E("Precedence", "print(2 + 3 * 4)\nprint((2 + 3) * 4)\nprint(-2 ** 2)\nprint((-2) ** 2)",
          "`-2 ** 2` is `-(2 ** 2)` because `**` binds tighter than the minus sign."),
        E("Splitting minutes", "minutes = 135\nhours = minutes // 60\nrest = minutes % 60\nprint(f\"{hours}h {rest}m\")"),
        E("Float surprises", "print(0.1 + 0.2)\nprint(round(0.1 + 0.2, 2))\nprint(0.1 + 0.2 == 0.3)",
          "Computers store decimals in binary, so tiny rounding errors appear. Round before comparing."),
    ),
    key_points=("`/` always returns a float; `//` rounds down; `%` gives the remainder.",
                "`**` is power. Brackets override precedence.",
                "Floats are approximate: compare with `round()` or `math.isclose()`."),
)

L2 = Lesson(
    id="t02.l2",
    title="Comparison and logical operators",
    body="""
Comparisons produce a **bool** (`True` or `False`):

| Operator | Meaning |
|---|---|
| `==` | equal to (two equals signs!) |
| `!=` | not equal |
| `<` `<=` `>` `>=` | ordering |
| `in` | membership: `"a" in "cat"` → `True` |

> ⚠️ `=` **assigns**, `==` **compares**. Mixing them up is the #1 operator bug.

### Logical operators
* `and` — `True` only if **both** sides are true
* `or` — `True` if **at least one** side is true
* `not` — flips `True`/`False`

```python
age, member = 17, True
print(age >= 18 and member)   # False
print(age >= 18 or member)    # True
```

Python allows chained comparisons: `0 <= score <= 100`.

A common trap: `if colour == "red" or "blue":` is **always** true, because
`"blue"` on its own is a non-empty string (truthy). Write
`colour == "red" or colour == "blue"` or `colour in ("red", "blue")`.
""",
    examples=(
        E("Comparisons", 'print(5 == 5.0)\nprint("abc" == "ABC")\nprint(3 != 4)\nprint("data" in "big data")'),
        E("and / or / not", "age = 17\nmember = True\nprint(age >= 18 and member)\nprint(age >= 18 or member)\nprint(not member)"),
        E("The 'or' trap", 'colour = "green"\nprint(colour == "red" or "blue")\nprint(colour == "red" or colour == "blue")\nprint(colour in ("red", "blue"))',
          "The first line prints `blue`, which counts as true — that's the bug."),
    ),
    key_points=("`==` compares, `=` assigns.", "`and` needs both true; `or` needs one.",
                "Each side of `or` must be a full comparison."),
)

L3 = Lesson(
    id="t02.l3",
    title="Debugging: reading errors like a detective",
    body="""
Bugs come in three flavours:

1. **Syntax errors** — the code breaks Python's grammar, so *nothing* runs
   (missing `:`, quote or bracket).
2. **Runtime errors (exceptions)** — the grammar is fine but something
   impossible happens while running (`1 / 0`, using an undefined name).
3. **Logic errors** — no error message at all, but the answer is wrong. These
   are the hardest; the computer did exactly what you *said*, not what you *meant*.

### Reading a traceback
Read it **bottom-up**. The last line names the error; the lines above show
*where* it happened.

```
Traceback (most recent call last):
  File "<your code>", line 3
    print(total / count)
ZeroDivisionError: division by zero
```

### A debugging routine that works
1. **Reproduce** the bug — run it and note the exact message.
2. **Locate** — go to the line number in the traceback.
3. **Inspect** — `print()` the variables on that line (and their `type()`).
4. **Hypothesise** — "I think `count` is 0 because the loop never ran".
5. **Fix one thing at a time** and re-run.
6. **Rubber-duck** — explain your code line by line out loud; you'll often
   spot the mistake mid-sentence.

When this app shows an error, it also explains it in plain English.
""",
    examples=(
        E("A runtime error", "prices = [3, 5, 8]\ncount = 0\ntotal = sum(prices)\nprint(total / count)",
          "Run it and read the explanation. Then fix it by using `len(prices)`."),
        E("Print debugging", "def average(values):\n    total = 0\n    for v in values:\n        total = v   # bug!\n        print('debug: v =', v, 'total =', total)\n    return total / len(values)\n\nprint(average([2, 4, 6]))",
          "The debug prints show `total` never accumulates. Change `total = v` to `total += v`."),
        E("Check your types", 'value = "12"\nprint(value, type(value))\nprint(int(value) * 2)\nprint(value * 2)'),
    ),
    key_points=("Read tracebacks from the bottom: error type, message, then line.",
                "Logic errors give no message — print intermediate values.",
                "Change one thing at a time and re-run."),
)

ITEMS = (
    MCQ("t02.mcq.floor_div", "What is `17 // 5`?",
        (O("`3`", True, "`//` divides and rounds down to a whole number: 17 / 5 = 3.4 → 3."),
         O("`3.4`", False, "That's `17 / 5`. `//` throws away the fractional part."),
         O("`2`", False, "`2` is the remainder, `17 % 5`."),
         O("`4`", False, "`//` rounds *down*, not to the nearest whole number.")),
        "`//` is floor division and `%` is the remainder: 17 = 3 × 5 + 2.", tags=("operators",)),
    MCQ("t02.mcq.precedence", "What does `print(10 - 2 * 3 ** 2)` show?",
        (O("`-8`", True, "`3 ** 2` = 9 first, then `2 * 9` = 18, then `10 - 18` = -8."),
         O("`72`", False, "That's `(10 - 2) * 3 ** 2`. Python doesn't work left to right: it does "
           "`**` first, then `*`, and the subtraction last."),
         O("`5184`", False, "That treats it as `((10 - 2) * 3) ** 2`. Powers are computed first, "
           "not last."),
         O("`-26`", False, "That computes `(2 * 3) ** 2` = 36. `**` binds tighter than `*`, "
           "so only the 3 is squared.")),
        "Precedence: `**`, then `* / // %`, then `+ -`.", tags=("operators",)),
    MCQ("t02.mcq.or_trap", "`colour = \"green\"`. What does `colour == \"red\" or \"blue\"` evaluate to?",
        (O('`"blue"` (which is truthy)', True, "`colour == 'red'` is False, so `or` returns its right "
           "side — the string `'blue'`, which counts as true in an `if`."),
         O("`False`", False, "It would be False only if written `colour == 'red' or colour == 'blue'`. "
           "As written, the right side is just the string `'blue'`."),
         O("`True`", False, "Close, but `or` returns one of its operands, not a bool; here the string "
           "`'blue'`."),
         O("An error", False, "This is valid Python — which is why the bug is sneaky.")),
        "Each side of `or` is evaluated separately. A non-empty string is truthy.",
        tags=("logic", "debugging")),
    MCQ("t02.mcq.error_kinds", "Your program runs without any error message but prints the wrong "
        "average. What kind of bug is this?",
        (O("A logic error", True, "The code is valid and runs, but computes the wrong thing."),
         O("A syntax error", False, "Syntax errors stop the program before *anything* runs."),
         O("A runtime error", False, "Runtime errors (exceptions) produce a traceback and stop the program."),
         O("A sandbox error", False, "The sandbox only blocks unsafe actions and always tells you so.")),
        "Logic errors are found by testing with known answers and printing intermediate values.",
        tags=("debugging",)),
    PredictOutput("t02.pred.division", "What does this code print?",
                  "print(8 / 2)\nprint(8 // 3)\nprint(8 % 3)\nprint(2 ** 3)",
                  "4.0\n2\n2\n8",
                  "`/` always returns a float (`4.0`), `//` floors (2), `%` gives the remainder (2).",
                  tags=("operators",),
                  common_wrong=(("4\n2\n2\n8", "`8 / 2` prints `4.0`, not `4`: true division always "
                                 "produces a float in Python 3."),)),
    PredictOutput("t02.pred.bools", "What does this code print?",
                  "x = 7\nprint(x > 5 and x < 10)\nprint(x % 2 == 0)\nprint(not x == 7)",
                  "True\nFalse\nFalse",
                  "7 is between 5 and 10 (True); 7 is odd (False); `not True` is False.",
                  tags=("logic",)),
    PredictOutput("t02.pred.augmented", "What does this code print?",
                  "n = 10\nn += 5\nn *= 2\nn -= 1\nprint(n)",
                  "29",
                  "10 → 15 → 30 → 29. Each augmented operator updates `n` in place.",
                  tags=("operators", "variables")),
    DebugExercise("t02.dbg.assign_compare", "This should print `Even` for 4. It has a syntax error — fix it.",
                  'n = 4\nif n % 2 = 0:\n    print("Even")',
                  'n = 4\nif n % 2 == 0:\n    print("Even")',
                  (C("Prints Even", stdout_equals="Even"),),
                  "`=` assigns a value; comparisons need `==`.",
                  hints=("Read the SyntaxError message carefully.",), tags=("logic", "syntax")),
    DebugExercise("t02.dbg.average_logic", "This should print the average of the three marks (`70.0`) but "
                  "prints `150.0`. Fix the logic error.",
                  "a, b, c = 60, 70, 80\naverage = a + b + c / 3\nprint(average)",
                  "a, b, c = 60, 70, 80\naverage = (a + b + c) / 3\nprint(average)",
                  (C("`average` is 70.0", expr="average", expected=70.0),
                   C("Prints 70.0", stdout_equals="70.0")),
                  "Division happens before addition, so only `c` was divided by 3. Brackets fix the order.",
                  hints=("Which operation does Python do first?",), tags=("operators", "debugging")),
    CodingExercise("t02.code.time_split", "Given `seconds = 3725`, compute `hours`, `minutes` and `secs` "
                   "(the leftover seconds) using `//` and `%`. For 3725 that's 1 h, 2 min, 5 s.",
                   "seconds = 3725\n# compute hours, minutes and secs\n",
                   "seconds = 3725\nhours = seconds // 3600\nminutes = (seconds % 3600) // 60\nsecs = seconds % 60",
                   (C("hours == 1", expr="hours", expected=1),
                    C("minutes == 2", expr="minutes", expected=2),
                    C("secs == 5", expr="secs", expected=5)),
                   "`//` counts how many whole units fit; `%` gives what is left over.",
                   hints=("There are 3600 seconds in an hour.", "Minutes come from the remainder after hours."),
                   tags=("operators",)),
    CodingExercise("t02.code.valid_score", "Write a boolean variable `is_valid` that is `True` when "
                   "`score` is between 0 and 100 inclusive **and** `submitted` is True.",
                   "score = 85\nsubmitted = True\nis_valid = ...\n",
                   "score = 85\nsubmitted = True\nis_valid = 0 <= score <= 100 and submitted",
                   (C("is_valid is True for 85/True", expr="is_valid", expected=True),
                    C("is_valid is a bool", expr="type(is_valid).__name__", expected="bool")),
                   "Chained comparison `0 <= score <= 100` reads naturally; `and` combines conditions.",
                   hints=("Combine two conditions with `and`.",), tags=("logic",)),
)

TOPIC = Topic(
    id="t02", number=2, title="Operators & Debugging", icon="🧮",
    summary="Arithmetic, comparison and logical operators; reading tracebacks; a debugging routine.",
    lessons=(L1, L2, L3), items=ITEMS, prerequisites=("t01",),
)
