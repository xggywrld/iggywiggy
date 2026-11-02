from .models import (MCQ, Check as C, CodingExercise, DebugExercise, Example as E,
                     Lesson, Option as O, PredictOutput, Topic)

L1 = Lesson(
    id="t03.l1",
    title="Making decisions: if / elif / else",
    body="""
An `if` statement runs a block of code only when a condition is true.

```python
temperature = 31
if temperature > 30:
    print("Hot")        # indented = inside the if
elif temperature > 15:
    print("Mild")
else:
    print("Cold")
print("Done")           # not indented = always runs
```

* The line ends with a **colon** `:`.
* The block underneath is **indented** (4 spaces). Indentation *is* the
  structure in Python — there are no curly brackets.
* Python checks conditions **top to bottom** and runs **only the first** true
  branch. Order your `elif`s from most specific to least specific.

### Truthiness
Any value can be used as a condition. These are *falsy*: `False`, `0`, `0.0`,
`""` (empty string), `[]`, `{}`, `None`. Everything else is *truthy*.

```python
names = []
if names:
    print("We have names")
else:
    print("The list is empty")
```
""",
    examples=(
        E("Grade bands", 'score = 72\nif score >= 70:\n    grade = "A"\nelif score >= 60:\n    grade = "B"\nelif score >= 50:\n    grade = "C"\nelse:\n    grade = "Fail"\nprint(grade)',
          "Try changing `score`. What happens if you put the `>= 50` test first?"),
        E("Only the first true branch runs", 'x = 100\nif x > 10:\n    print("bigger than 10")\nelif x > 50:\n    print("bigger than 50")  # never reached for x = 100!'),
        E("Truthiness", 'for value in [0, 5, "", "hi", [], [1], None]:\n    if value:\n        print(repr(value), "is truthy")\n    else:\n        print(repr(value), "is falsy")'),
    ),
    key_points=("Conditions end with `:` and the block is indented.",
                "Only the first matching branch of an if/elif chain runs.",
                "Empty containers, 0 and None are falsy."),
)

L2 = Lesson(
    id="t03.l2",
    title="for loops and range() in depth",
    body="""
A `for` loop repeats a block **once for each item** in a sequence:

```python
for city in ["Paris", "Lima", "Oslo"]:
    print(city)
```
Each time round, the *loop variable* `city` is set to the next item.

### range()
`range()` generates integers, which is how you repeat something *n* times:

| Call | Numbers produced |
|---|---|
| `range(5)` | 0, 1, 2, 3, 4  (**stops before 5**) |
| `range(2, 6)` | 2, 3, 4, 5 |
| `range(0, 10, 3)` | 0, 3, 6, 9 |
| `range(5, 0, -1)` | 5, 4, 3, 2, 1 |

### The accumulator pattern
The single most important loop pattern in data work: start a total *before*
the loop, update it *inside* the loop, use it *after* the loop.

```python
sales = [120, 80, 200]
total = 0                 # 1. initialise BEFORE the loop
for s in sales:
    total += s            # 2. update INSIDE
print(total)              # 3. use AFTER (not indented!)
```

### Looping with positions: enumerate()
```python
for i, city in enumerate(["Paris", "Lima"]):
    print(i, city)        # 0 Paris / 1 Lima
```
Prefer `for item in items` over `for i in range(len(items))` unless you need
the index — and then prefer `enumerate`.

### Looping over two lists together: zip()
```python
for name, mark in zip(["Ana", "Ben"], [81, 67]):
    print(name, mark)
```

### Nested loops
A loop inside a loop: the inner loop runs completely for **each** pass of the
outer loop.
""",
    examples=(
        E("range variants", "print(list(range(5)))\nprint(list(range(2, 6)))\nprint(list(range(0, 10, 3)))\nprint(list(range(5, 0, -1)))"),
        E("Accumulator", "sales = [120, 80, 200, 45]\ntotal = 0\nfor s in sales:\n    total += s\nprint('Total:', total)\nprint('Average:', total / len(sales))"),
        E("Counting and filtering", "temps = [12, 25, 31, 18, 33, 29]\nhot_days = 0\nhot = []\nfor t in temps:\n    if t > 28:\n        hot_days += 1\n        hot.append(t)\nprint(hot_days, hot)"),
        E("enumerate and zip", 'names = ["Ana", "Ben", "Cy"]\nmarks = [81, 67, 90]\nfor i, name in enumerate(names, start=1):\n    print(i, name)\nfor name, mark in zip(names, marks):\n    print(f"{name}: {mark}")'),
        E("Nested loops", "for row in range(1, 4):\n    line = ''\n    for col in range(1, 4):\n        line += f'{row * col:4}'\n    print(line)"),
        E("Finding the maximum by hand", "values = [4, 17, 9, 23, 5]\nbest = values[0]\nfor v in values[1:]:\n    if v > best:\n        best = v\nprint(best)"),
    ),
    key_points=("`range(n)` gives 0 … n-1.", "Accumulator: initialise before, update inside, use after.",
                "Use `enumerate()` for index + item, `zip()` for parallel lists."),
)

L3 = Lesson(
    id="t03.l3",
    title="while loops, break and continue",
    body="""
A `while` loop repeats **as long as** its condition is true. Use it when you
don't know in advance how many repetitions you need.

```python
balance = 1000
years = 0
while balance < 2000:
    balance *= 1.07
    years += 1
print(years)   # 11 years to double at 7%
```

> ⚠️ Something inside the loop **must** eventually make the condition false,
> otherwise you get an **infinite loop**. (The sandbox stops runaway code after
> a few seconds.)

### break and continue
* `break` — leave the loop immediately.
* `continue` — skip the rest of *this* pass and go to the next one.

```python
for n in [3, -1, 4, 0, 5]:
    if n < 0:
        continue        # skip negatives
    if n == 0:
        break           # stop completely at 0
    print(n)            # prints 3 then 4
```

### for vs while
| Use `for` when... | Use `while` when... |
|---|---|
| you loop over a collection or a known count | you loop until something happens |
| e.g. every row of a dataset | e.g. until the user types `quit`, until a value converges |
""",
    examples=(
        E("Doubling money", "balance = 1000\nyears = 0\nwhile balance < 2000:\n    balance *= 1.07\n    years += 1\nprint(years, round(balance, 2))"),
        E("break and continue", "for n in [3, -1, 4, 0, 5]:\n    if n < 0:\n        continue\n    if n == 0:\n        break\n    print(n)"),
        E("Input until 'quit'", 'total = 0\nwhile True:\n    text = input()\n    if text == "quit":\n        break\n    total += int(text)\nprint("Sum:", total)',
          "Edit the Input box to try other numbers.", stdin="5\n10\n7\nquit\n"),
        E("An infinite loop (stopped safely)", "count = 0\nwhile count < 5:\n    print(count)\n    # forgot: count += 1",
          "Run it: the sandbox stops it. Then add `count += 1` inside the loop."),
    ),
    key_points=("`while` repeats while a condition is true — make sure it becomes false.",
                "`break` exits the loop; `continue` jumps to the next pass."),
)

ITEMS = (
    MCQ("t03.mcq.range", "Which numbers does `range(1, 10, 3)` produce?",
        (O("1, 4, 7", True, "Start at 1, step 3, stop *before* 10: 1, 4, 7."),
         O("1, 4, 7, 10", False, "The stop value is never included, so 10 is excluded."),
         O("1, 3, 6, 9", False, "The step is added to the start (1), not counted from 0."),
         O("0, 3, 6, 9", False, "The first argument (1) is the start, so it doesn't begin at 0.")),
        "`range(start, stop, step)` includes start and excludes stop.", tags=("loops", "range")),
    MCQ("t03.mcq.elif_order", "With `x = 95`, what does this print?",
        (O("`big`", True, "Python checks `x > 50` first; it's true, so that branch runs and the "
           "rest are skipped."),
         O("`huge`", False, "`x > 90` is never checked — an earlier branch already matched. "
           "Put the most specific test first."),
         O("`big` and `huge`", False, "An if/elif chain runs at most *one* branch."),
         O("Nothing", False, "95 > 50 is true, so the first branch runs.")),
        "Only the first true branch in an if/elif chain runs.",
        code='x = 95\nif x > 50:\n    print("big")\nelif x > 90:\n    print("huge")',
        tags=("conditionals",)),
    MCQ("t03.mcq.accumulator_place", "Where should `total = 0` go when summing a list with a loop?",
        (O("Before the loop", True, "It must be set once, before the first pass."),
         O("Inside the loop", False, "Then it would be reset to 0 on every pass and you'd only keep "
           "the last value."),
         O("After the loop", False, "The loop body would use `total` before it exists (NameError), "
           "and the sum would then be wiped out."),
         O("It doesn't matter", False, "Placement completely changes the result.")),
        "Accumulator pattern: initialise before, update inside, use after.", tags=("loops",)),
    MCQ("t03.mcq.break_continue", "What's the difference between `break` and `continue`?",
        (O("`break` exits the loop; `continue` skips to the next pass", True, ""),
         O("`continue` exits the loop; `break` skips to the next pass", False, "It's the other way "
           "round: `break` breaks out entirely."),
         O("They are the same", False, "`continue` keeps looping; `break` stops."),
         O("`break` ends the whole program", False, "`break` only exits the innermost loop; code "
           "after the loop still runs.")),
        "`break` = leave the loop now. `continue` = skip the rest of this pass.", tags=("loops",)),
    MCQ("t03.mcq.truthy", "Which value is **truthy**?",
        (O('`"0"`', True, "It's a non-empty string (it contains the character 0), so it's truthy."),
         O("`0`", False, "The number zero is falsy."),
         O("`[]`", False, "Empty lists are falsy."),
         O("`None`", False, "`None` is always falsy.")),
        "Empty things, zero and None are falsy; everything else is truthy.", tags=("conditionals",)),
    PredictOutput("t03.pred.loop_sum", "What does this code print?",
                  "total = 0\nfor i in range(4):\n    total += i\nprint(total)",
                  "6",
                  "`range(4)` gives 0, 1, 2, 3 and 0 + 1 + 2 + 3 = 6.",
                  tags=("loops", "range"),
                  common_wrong=(("10", "That's 1+2+3+4. `range(4)` starts at 0 and stops *before* 4."),)),
    PredictOutput("t03.pred.print_in_loop", "What does this code print? (Watch the indentation.)",
                  "total = 0\nfor n in [2, 4, 6]:\n    total += n\n    print(total)",
                  "2\n6\n12",
                  "The `print` is indented, so it runs inside the loop — once per pass — showing the "
                  "running total.",
                  tags=("loops", "indentation"),
                  common_wrong=(("12", "That's what you'd get if `print` were *not* indented. Here "
                                 "it's inside the loop, so it runs 3 times."),)),
    PredictOutput("t03.pred.while", "What does this code print?",
                  "n = 1\nwhile n < 20:\n    n *= 3\nprint(n)",
                  "27",
                  "n goes 1 → 3 → 9 → 27. The check `27 < 20` is false, so the loop stops with n = 27.",
                  tags=("loops", "while")),
    PredictOutput("t03.pred.break", "What does this code print?",
                  "for word in ['data', 'science', 'stop', 'ai']:\n    if word == 'stop':\n        break\n    print(word.upper())",
                  "DATA\nSCIENCE",
                  "`break` leaves the loop when 'stop' is reached, so 'ai' is never processed.",
                  tags=("loops",)),
    PredictOutput("t03.pred.nested", "What does this code print?",
                  "for i in range(2):\n    for j in range(3):\n        print(i, j)",
                  "0 0\n0 1\n0 2\n1 0\n1 1\n1 2",
                  "The inner loop runs completely (j = 0, 1, 2) for each value of i.",
                  tags=("loops", "nested")),
    DebugExercise("t03.dbg.reset_total", "This should print the sum `60`, but prints `30`. Fix it.",
                  "values = [10, 20, 30]\nfor v in values:\n    total = 0\n    total += v\nprint(total)",
                  "values = [10, 20, 30]\ntotal = 0\nfor v in values:\n    total += v\nprint(total)",
                  (C("Prints 60", stdout_equals="60"), C("total is 60", expr="total", expected=60)),
                  "`total = 0` was inside the loop, so it was reset on each pass. Move it before the loop.",
                  hints=("How many times does `total = 0` run?",), tags=("loops", "debugging")),
    DebugExercise("t03.dbg.infinite", "This should print 5, 4, 3, 2, 1 (one per line) but never stops. Fix it.",
                  "n = 5\nwhile n > 0:\n    print(n)",
                  "n = 5\nwhile n > 0:\n    print(n)\n    n -= 1",
                  (C("Prints 5 down to 1", stdout_equals="5\n4\n3\n2\n1"),),
                  "Nothing changed `n`, so `n > 0` was true forever. Decrease `n` inside the loop.",
                  hints=("What must change for the condition to become False?",), tags=("loops", "while")),
    DebugExercise("t03.dbg.off_by_one", "This should print every item in the list, but crashes. Fix it.",
                  "items = ['a', 'b', 'c']\nfor i in range(len(items) + 1):\n    print(items[i])",
                  "items = ['a', 'b', 'c']\nfor item in items:\n    print(item)",
                  (C("Prints a, b, c", stdout_equals="a\nb\nc"),),
                  "Positions go 0..len-1, so `range(len(items) + 1)` goes one too far (IndexError). "
                  "Simplest fix: loop over the items directly.",
                  hints=("What is the last valid index of a 3-item list?",), tags=("loops", "indexing")),
    CodingExercise("t03.code.count_passes", "Count how many marks are **50 or above** and store it in "
                   "`passes`. Also build a list `failed` of the marks below 50 (in original order).",
                   "marks = [72, 45, 50, 38, 91, 66, 49]\n",
                   "marks = [72, 45, 50, 38, 91, 66, 49]\npasses = 0\nfailed = []\nfor m in marks:\n    if m >= 50:\n        passes += 1\n    else:\n        failed.append(m)",
                   (C("passes == 4", expr="passes", expected=4),
                    C("failed == [45, 38, 49]", expr="failed", expected=[45, 38, 49])),
                   "One loop can maintain several accumulators at the same time.",
                   hints=("Start `passes = 0` and `failed = []` before the loop.",), tags=("loops", "conditionals")),
    CodingExercise("t03.code.fizzbuzz", "Print the numbers 1 to 15, but print `Fizz` for multiples of 3, "
                   "`Buzz` for multiples of 5 and `FizzBuzz` for multiples of both.",
                   "for n in range(1, 16):\n    ...\n",
                   "for n in range(1, 16):\n    if n % 15 == 0:\n        print('FizzBuzz')\n    elif n % 3 == 0:\n        print('Fizz')\n    elif n % 5 == 0:\n        print('Buzz')\n    else:\n        print(n)",
                   (C("Correct FizzBuzz output", stdout_equals="1\n2\nFizz\n4\nBuzz\nFizz\n7\n8\nFizz\nBuzz\n11\nFizz\n13\n14\nFizzBuzz"),),
                   "Check the most specific case (divisible by 15) first, otherwise 15 would print `Fizz`.",
                   hints=("`n % 3 == 0` tests divisibility.", "Which test must come first?"),
                   tags=("loops", "conditionals")),
)

TOPIC = Topic(
    id="t03", number=3, title="Control Flow", icon="🔀",
    summary="if/elif/else, truthiness, for loops, range, accumulators, while, break and continue.",
    lessons=(L1, L2, L3), items=ITEMS, prerequisites=("t02",),
)
