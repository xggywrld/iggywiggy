from .models import (MCQ, Check as C, CodingExercise, DebugExercise, Example as E,
                     Lesson, Option as O, PredictOutput, Topic)

L1 = Lesson(
    id="t01.l1",
    title="What is a program? Your first lines of Python",
    body="""
A **program** is a list of instructions that a computer follows *exactly*, one
after another, from the top of the file to the bottom. Python is popular in
Data Science and AI because its instructions read almost like English and it
has excellent libraries (pandas, matplotlib, scikit-learn, PyTorch...).

### `print()` — showing results
`print()` displays a value on the screen. Text (a **string**) goes inside
quotes; numbers do not.

```python
print("Hello, data world!")
print(42)
print("The answer is", 42)   # several values → separated by a space
```

### Comments
Anything after `#` is a **comment**: Python ignores it. Comments explain *why*
code exists, for the humans reading it.

### Order matters
Python runs line 1, then line 2, then line 3. If line 2 has an error, line 3
never runs. This top-to-bottom rule explains a huge number of beginner bugs.

> 💡 **How to use this app:** every code box below is editable. Change the code
> and press **Run** — experimenting is the fastest way to learn.
""",
    examples=(
        E("Hello world", 'print("Hello, data world!")\nprint(42)\nprint("The answer is", 42)',
          "Each `print()` produces one line. Commas inside `print()` add a space."),
        E("Comments are ignored", '# This line is a comment\nprint("Visible")  # so is this part\n# print("Not shown")',
          "The last line doesn't run because the whole line is a comment."),
        E("Top to bottom", 'print("Step 1")\nprint("Step 2")\nprint("Step 3")',
          "Try swapping lines and run again."),
    ),
    key_points=(
        "Python runs statements from top to bottom.",
        "`print()` shows values; strings need quotes, numbers don't.",
        "`#` starts a comment, which Python ignores.",
    ),
)

L2 = Lesson(
    id="t01.l2",
    title="Variables and basic data types",
    body="""
A **variable** is a name that refers to a value. You create one with `=`
(the *assignment* operator — read it as "gets", not "equals"):

```python
city = "Leeds"        # str  (text)
population = 812000   # int  (whole number)
growth = 1.4          # float (decimal number)
is_capital = False    # bool (True / False)
```

`type(x)` tells you what kind of value `x` holds. Types matter: `"5"` (text)
and `5` (number) behave differently: `"5" + "5"` is `"55"` but `5 + 5` is `10`.

### Reassignment
A variable can be pointed at a new value. The old value is forgotten:

```python
score = 10
score = score + 5   # take the current value, add 5, store it back
print(score)        # 15
```

### Naming rules
* letters, digits and `_` only, and must not start with a digit
* case-sensitive: `Total` ≠ `total`
* use descriptive `snake_case` names: `average_price`, not `ap`
* don't reuse built-in names like `print`, `sum`, `list`, `type`
""",
    examples=(
        E("Four basic types", 'city = "Leeds"\npopulation = 812000\ngrowth = 1.4\nis_capital = False\n'
          'print(type(city))\nprint(type(population))\nprint(type(growth))\nprint(type(is_capital))'),
        E("Text vs numbers", 'print("5" + "5")\nprint(5 + 5)\nprint("5" * 3)',
          "`+` joins strings but adds numbers. `*` repeats a string."),
        E("Updating a variable", "score = 10\nscore = score + 5\nprint(score)\nscore = 0\nprint(score)"),
    ),
    key_points=(
        "`=` stores a value in a variable; it is not a mathematical equation.",
        "The four basic types are `int`, `float`, `str` and `bool`.",
        "Names are case-sensitive and must not start with a digit.",
    ),
)

L3 = Lesson(
    id="t01.l3",
    title="Input, type conversion and f-strings",
    body="""
`input()` pauses the program and reads one line typed by the user.
**It always returns a string**, even if the user types digits. To do maths,
convert it:

```python
age = int(input("Age? "))        # "21" → 21
height = float(input("Height? ")) # "1.75" → 1.75
```

| Function | Converts to | Example |
|---|---|---|
| `int()` | whole number | `int("42")` → `42`, `int(3.9)` → `3` (truncates) |
| `float()` | decimal | `float("2.5")` → `2.5` |
| `str()` | text | `str(7)` → `"7"` |
| `bool()` | True/False | `bool(0)` → `False`, `bool("hi")` → `True` |

### f-strings: the best way to build text
Put `f` before the quotes and variables inside `{ }`:

```python
name, score = "Ada", 92.456
print(f"{name} scored {score:.1f}%")   # Ada scored 92.5%
```
`:.1f` means "one digit after the decimal point" — very handy for reporting
results in data science.

> In the sandbox, programs that call `input()` read from the **Input** box.
""",
    examples=(
        E("Reading input", 'name = input("What is your name? ")\nprint(f"Hello, {name}!")',
          "The prompt text is not echoed in the sandbox; your input comes from the Input box.",
          stdin="Ada\n"),
        E("input() returns text", 'age = input()\nprint(type(age))\nage = int(age)\nprint(age + 1)',
          stdin="20\n"),
        E("Formatting numbers", 'price = 3.14159\nprint(f"Price: £{price:.2f}")\nratio = 0.8734\nprint(f"Accuracy: {ratio:.1%}")'),
    ),
    key_points=(
        "`input()` always returns a `str`.",
        "Convert with `int()`, `float()`, `str()` before calculating.",
        "f-strings: `f\"{value:.2f}\"` formats to 2 decimal places.",
    ),
)

ITEMS = (
    MCQ("t01.mcq.type_of_input", "What type of value does `input()` return when the user types `25`?",
        (O("`str`", True, "`input()` always returns text. You must call `int()` to get a number."),
         O("`int`", False, "Although the user typed digits, `input()` never converts them — it "
           "doesn't know whether you want a number, a postcode or a phone number."),
         O("`float`", False, "No conversion happens automatically; you'd need `float(input())`."),
         O("It depends on what the user types", False, "Python can't guess: the result is "
           "*always* a string, whatever is typed.")),
        "`input()` always gives you a string. Convert it with `int()` or `float()` to do maths.",
        tags=("input", "types")),
    MCQ("t01.mcq.assignment", "After running this code, what is the value of `x`?",
        (O("`8`", True, "`x` starts at 5, then `x = x + 3` computes 5 + 3 and stores 8 back in `x`."),
         O("`5`", False, "The second line *reassigns* `x`, so the old value 5 is replaced."),
         O("`3`", False, "`x + 3` uses the current value of `x` (5) — it doesn't just store 3."),
         O("An error, because x can't equal x + 3", False, "`=` is not a maths equation; it means "
           "'compute the right side, then store it in the name on the left'.")),
        "Assignment evaluates the right-hand side first, then stores the result.",
        code="x = 5\nx = x + 3", tags=("variables",)),
    MCQ("t01.mcq.valid_name", "Which of these is a **valid** variable name?",
        (O("`total_sales_2024`", True, "Letters, digits and underscores, not starting with a digit."),
         O("`2024_sales`", False, "Variable names cannot start with a digit."),
         O("`total-sales`", False, "`-` is the minus operator; Python reads this as `total - sales`."),
         O("`class`", False, "`class` is a reserved keyword in Python and can't be used as a name.")),
        "Names may contain letters, digits and `_`, must not start with a digit and can't be keywords.",
        tags=("variables", "syntax")),
    MCQ("t01.mcq.str_plus", "What does `print(\"3\" + \"4\")` display?",
        (O("`34`", True, "Both values are strings, so `+` joins (concatenates) them."),
         O("`7`", False, "`+` only adds numerically when both values are numbers. These are strings "
           "because they're in quotes."),
         O("`\"34\"`", False, "`print()` shows strings without their quotes."),
         O("An error", False, "Joining two strings is allowed; only mixing a string and a number "
           "with `+` causes an error.")),
        "Quotes make a string. `+` on strings concatenates them.",
        tags=("types", "strings")),
    PredictOutput("t01.pred.print_sep", "What does this code print?",
                  'name = "Sam"\nage = 30\nprint(name, "is", age)\nprint(name + "!")',
                  "Sam is 30\nSam!",
                  "Commas in `print()` separate values with a single space. `+` joins strings with "
                  "no space at all.",
                  tags=("print", "strings"),
                  common_wrong=(("Sam,is,30\nSam!", "The commas separate the *arguments* of "
                                 "`print()`; they aren't printed. Python puts a space between values."),)),
    PredictOutput("t01.pred.reassign", "What does this code print?",
                  "a = 2\nb = a\na = 10\nprint(a, b)",
                  "10 2",
                  "`b = a` copies the *current value* 2 into `b`. Changing `a` later doesn't affect `b` "
                  "(numbers are immutable).",
                  tags=("variables",),
                  common_wrong=(("10 10", "`b = a` doesn't link `b` to `a` forever — it gives `b` the "
                                 "value `a` had at that moment (2)."),)),
    PredictOutput("t01.pred.fstring", "What does this code print?",
                  'price = 2.5\nqty = 4\nprint(f"Total: {price * qty:.2f}")',
                  "Total: 10.00",
                  "Expressions can go inside f-string braces. `:.2f` formats to two decimal places.",
                  tags=("fstrings",)),
    DebugExercise("t01.dbg.missing_quotes", "This program should print `Hello, Ada`. Fix the bug.",
                  'name = Ada\nprint("Hello, " + name)',
                  'name = "Ada"\nprint("Hello, " + name)',
                  (C("Prints Hello, Ada", stdout_equals="Hello, Ada"),),
                  "Without quotes, `Ada` is treated as a *variable name* that doesn't exist, which "
                  "causes a `NameError`. Text values need quotes.",
                  hints=("Run it and read the error. Which name is 'not defined'?",
                         "Text must be wrapped in quotes."),
                  tags=("strings", "nameerror")),
    DebugExercise("t01.dbg.input_int", "The user types two numbers. The program should print their sum "
                  "(for input 3 and 4 it should print `7`), but it prints `34`. Fix it.",
                  "a = input()\nb = input()\nprint(a + b)",
                  "a = int(input())\nb = int(input())\nprint(a + b)",
                  (C("Prints 7 for inputs 3 and 4", stdout_equals="7"),),
                  "`input()` returns strings, and `'3' + '4'` is `'34'`. Converting with `int()` "
                  "turns them into numbers so `+` adds them.",
                  hints=("What type does `input()` return?",),
                  tags=("input", "types"), stdin="3\n4\n"),
    CodingExercise("t01.code.greeting", "Create a variable `name` holding the text `Grace` and a variable "
                   "`year` holding the number `1906`. Then print exactly: `Grace was born in 1906`",
                   "# create name and year, then print the sentence\n",
                   'name = "Grace"\nyear = 1906\nprint(f"{name} was born in {year}")',
                   (C("`name` is the string 'Grace'", expr="name", expected="Grace"),
                    C("`year` is the integer 1906", expr="year", expected=1906),
                    C("`year` is an int, not a str", expr="type(year).__name__", expected="int"),
                    C("Prints the sentence", stdout_equals="Grace was born in 1906")),
                   "An f-string is the neatest way to combine text and numbers.",
                   hints=("Strings need quotes; numbers don't.", 'Try `print(f"{name} was born in {year}")`.'),
                   tags=("variables", "fstrings")),
    CodingExercise("t01.code.bmi", "Read a weight in kg and a height in metres (two lines of input, as "
                   "decimals). Compute `bmi = weight / height ** 2` and print it with one decimal place, "
                   "like `BMI: 22.9`.",
                   "weight = input()\nheight = input()\n# convert, calculate and print\n",
                   'weight = float(input())\nheight = float(input())\nbmi = weight / height ** 2\nprint(f"BMI: {bmi:.1f}")',
                   (C("Prints BMI for 70 kg, 1.75 m", stdout_equals="BMI: 22.9"),
                    C("`bmi` variable is correct", expr="round(bmi, 2)", expected=22.86)),
                   "`float(input())` converts the text to a decimal; `:.1f` formats one decimal place.",
                   hints=("Use `float()` because heights have decimals.", "`**` is the power operator."),
                   tags=("input", "fstrings", "operators"), stdin="70\n1.75\n"),
)

TOPIC = Topic(
    id="t01", number=1, title="Introduction & Programming Basics", icon="🚀",
    summary="How programs run, print(), variables, basic types, input and f-strings.",
    lessons=(L1, L2, L3), items=ITEMS,
)
