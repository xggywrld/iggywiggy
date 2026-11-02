"""Turn Python error messages into beginner-friendly explanations.

Each rule is ``(error type, regex on the message, explanation template)``.
The first matching rule wins; templates can use named regex groups.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Explanation:
    title: str
    what_happened: str
    how_to_fix: str


_RULES: list[tuple[str, str, str, str, str]] = [
    # (type, regex, title, what happened, how to fix)
    ("NameError", r"name '(?P<name>\w+)' is not defined",
     "Python doesn't know the name `{name}`",
     "You used `{name}`, but Python has never seen a variable or function with that "
     "name. Python reads your code from top to bottom, so a name must be created "
     "(e.g. `{name} = ...` or `def {name}(...)`) *before* it is used.",
     "Check the spelling and capitalisation (`Total` and `total` are different names). "
     "If `{name}` is meant to be text, put it in quotes: `'{name}'`. "
     "If it is created inside a function, it only exists inside that function — "
     "`return` it instead."),
    ("TypeError", r'can only concatenate str \(not "(?P<t>\w+)"\) to str',
     "You tried to join text and a {t} with `+`",
     "`+` between two strings glues them together, but Python refuses to glue a "
     "string to a `{t}` because it can't guess what you mean.",
     "Convert the value to text first, e.g. `'Age: ' + str(age)`, or use an f-string: "
     "`f'Age: {{age}}'`."),
    ("TypeError", r"unsupported operand type\(s\) for (?P<op>\S+): '(?P<a>\w+)' and '(?P<b>\w+)'",
     "`{op}` doesn't work between a {a} and a {b}",
     "Python doesn't know how to apply `{op}` to a `{a}` and a `{b}`. "
     "A common cause is a value that is still text (from `input()` or a file) when "
     "you expected a number, or a function that returned `None`.",
     "Convert values with `int(...)`, `float(...)` or `str(...)` so both sides have "
     "compatible types. If one side is `NoneType`, the function you called probably "
     "uses `print` instead of `return`."),
    ("TypeError", r"'NoneType' object is not (?P<what>subscriptable|iterable|callable)",
     "You used `None` as if it were a real value",
     "Something gave you `None` (Python's 'nothing') and you then tried to index, loop "
     "over or call it. Very often this is a function that *prints* its result instead "
     "of *returning* it — such a function returns `None`. Also, list methods like "
     "`.sort()` and `.append()` change the list in place and return `None`.",
     "Make sure your function ends with `return value`. Don't write "
     "`my_list = my_list.sort()`; just write `my_list.sort()`."),
    ("TypeError", r"'(?P<t>\w+)' object is not subscriptable",
     "A {t} can't be indexed with `[ ]`",
     "Square brackets `x[0]` only work on sequences and mappings (strings, lists, "
     "tuples, dicts...). A `{t}` is a single value, so it has no positions.",
     "Check what type the variable really holds with `print(type(x))`. If you need the "
     "digits of a number, convert it first: `str(n)[0]`."),
    ("TypeError", r"'(?P<t>\w+)' object is not iterable",
     "You can't loop over a {t}",
     "`for` loops (and functions like `sum`, `list`, `sorted`) need a collection of "
     "items. A `{t}` is a single value.",
     "To repeat something n times write `for i in range(n):`, not `for i in n:`."),
    ("TypeError", r"'(?P<t>\w+)' object does not support item assignment",
     "A {t} cannot be changed in place",
     "`{t}` values are *immutable*: once created, their items can't be replaced. "
     "Tuples and strings are immutable; lists and dicts are mutable.",
     "Build a new value instead, e.g. `s = s[:0] + 'J' + s[1:]`, or convert to a list, "
     "change it and convert back: `lst = list(t); lst[0] = 9; t = tuple(lst)`."),
    ("TypeError", r"'(?P<t>\w+)' object is not callable",
     "You used `( )` on a {t}, which isn't a function",
     "Parentheses after a name mean 'call this function'. Here the name holds a "
     "`{t}`. Often you accidentally overwrote a built-in, e.g. `sum = 10` and later "
     "`sum([1, 2])`, or you wrote `x(2)` meaning `x * 2`.",
     "Rename your variable so it doesn't hide the function, and use `*` for "
     "multiplication."),
    ("TypeError", r"(?P<f>\w+)\(\) missing (?P<n>\d+) required positional argument",
     "`{f}()` was called with too few arguments",
     "The function `{f}` was defined with more parameters than you passed when you "
     "called it ({n} missing).",
     "Compare the `def {f}(...)` line with your call and pass a value for every "
     "parameter (or give the parameter a default value)."),
    ("TypeError", r"(?P<f>\w+)\(\) takes (?P<n>\d+) positional arguments? but (?P<m>\d+) (were|was) given",
     "`{f}()` was called with too many arguments",
     "`{f}` accepts {n} argument(s) but received {m}. If `{f}` is a method, remember "
     "that Python passes `self` automatically.",
     "Remove the extra arguments, or add parameters to the function definition."),
    ("TypeError", r"list indices must be integers or slices, not (?P<t>\w+)",
     "List positions must be whole numbers",
     "You used a `{t}` inside `[ ]` on a list. Lists are indexed by position "
     "(0, 1, 2, ...), not by name or decimal number.",
     "If you need to look things up by name, use a dictionary. If the index came from "
     "`input()` or `/`, convert it with `int(...)` or use `//`."),
    ("TypeError", r"unhashable type: '(?P<t>\w+)'",
     "A {t} can't be a dictionary key or set item",
     "Dictionary keys and set items must be immutable ('hashable'). A `{t}` can change, "
     "so Python refuses to use it as a key.",
     "Use a tuple instead of a list as the key, e.g. `d[(x, y)] = ...`."),
    ("IndexError", r"(?P<t>\w+) index out of range",
     "You asked for a position that doesn't exist",
     "Python counts positions from **0**, so a {t} with 3 items has positions 0, 1 "
     "and 2 — position 3 doesn't exist. Loops that go one step too far (`range(len(x) + 1)`) "
     "are a classic cause.",
     "Print `len(...)` to see how many items there are. The last item is always "
     "`x[-1]` or `x[len(x) - 1]`."),
    ("KeyError", r"(?P<k>.+)",
     "The key {k} isn't in the dictionary",
     "You looked up {k}, but the dictionary has no entry with that key. Keys are "
     "exact: `'Name'`, `'name'` and `'name '` are three different keys.",
     "Print the dictionary's keys with `print(d.keys())`. Use `d.get(key, default)` "
     "when a key may be missing, or check first with `if key in d:`."),
    ("AttributeError", r"'NoneType' object has no attribute '(?P<a>\w+)'",
     "You called `.{a}` on `None`",
     "The value before the dot is `None`. This usually means a function returned "
     "nothing (it used `print` instead of `return`), or you stored the result of an "
     "in-place method like `.sort()`, which returns `None`.",
     "Find where the variable was assigned and make sure it gets a real value."),
    ("AttributeError", r"'(?P<t>\w+)' object has no attribute '(?P<a>\w+)'",
     "A {t} doesn't have `.{a}`",
     "Each type has its own methods. `{t}` values don't have a method or attribute "
     "called `{a}`. For example, lists have `.append()` but strings and tuples don't.",
     "Check the spelling, and check the type with `type(x)`. `dir(x)` lists what a "
     "value supports."),
    ("ValueError", r"invalid literal for int\(\) with base 10: (?P<v>.+)",
     "{v} can't be turned into a whole number",
     "`int()` only understands text that looks like a whole number, such as `'42'`. "
     "Text like {v} (letters, decimals, spaces or an empty string) can't be converted.",
     "Use `float()` for decimals, call `.strip()` to remove spaces, and validate input "
     "with `.isdigit()` or `try` / `except ValueError`."),
    ("ValueError", r"could not convert string to float: (?P<v>.+)",
     "{v} isn't a number",
     "`float()` couldn't read {v} as a number. Watch out for commas (`'1,200'`), "
     "currency symbols or empty strings in data files.",
     "Clean the text first, e.g. `float(s.replace(',', '').replace('£', ''))`."),
    ("ValueError", r"too many values to unpack|not enough values to unpack",
     "The number of variables doesn't match the number of values",
     "When you write `a, b = something`, Python needs *exactly* as many values as "
     "variables on the left.",
     "Count the items on each side. In loops over a dict use `for k, v in d.items():`."),
    ("ZeroDivisionError", r".*",
     "You divided by zero",
     "Dividing by zero has no answer, so Python stops. In data work this often happens "
     "when computing an average of an empty list (`total / len(items)` where "
     "`len(items)` is 0).",
     "Check the divisor first: `if count > 0: average = total / count`."),
    ("IndentationError", r".*",
     "The indentation (spaces at the start of a line) is wrong",
     "Python uses indentation to know which lines belong to an `if`, loop or function. "
     "A block must be indented after a line ending in `:`, and lines in the same block "
     "must line up exactly.",
     "Indent block contents by 4 spaces and keep them aligned. Don't mix tabs and spaces."),
    ("TabError", r".*",
     "Tabs and spaces are mixed",
     "Some lines are indented with tabs and others with spaces, so Python can't tell "
     "how they line up.",
     "Re-indent the block using only spaces (4 per level)."),
    ("SyntaxError", r"expected ':'",
     "A colon `:` is missing",
     "Lines that start a block — `if`, `elif`, `else`, `for`, `while`, `def`, `class`, "
     "`try` — must end with a colon.",
     "Add `:` at the end of the line Python points to."),
    ("SyntaxError", r"unterminated string literal|EOL while scanning",
     "A string is missing its closing quote",
     "Python saw an opening quote but never found the matching closing quote on "
     "that line.",
     "Make sure every string starts and ends with the same kind of quote."),
    ("SyntaxError", r"'\(' was never closed|'\[' was never closed|'\{' was never closed|unexpected EOF",
     "A bracket was opened but never closed",
     "Every `(`, `[` and `{` needs a matching closing bracket. Python reached the end "
     "of the code while still waiting for one.",
     "Count the brackets on the line Python points to (and the line before it)."),
    ("SyntaxError", r"invalid syntax\. Maybe you meant '==' or ':=' instead of '='\?|cannot assign to",
     "`=` was used where a comparison was expected",
     "A single `=` *stores* a value in a variable. To *compare* two values use `==`.",
     "Write `if x == 5:` instead of `if x = 5:`."),
    ("SyntaxError", r"'return' outside function",
     "`return` can only be used inside a function",
     "`return` sends a value back from a function to the code that called it. Outside "
     "a function there is nothing to return to.",
     "Indent the `return` so it is inside the `def`, or use `print()` at the top level."),
    ("SyntaxError", r".*",
     "Python couldn't understand the grammar of a line",
     "A syntax error means the code breaks Python's grammar rules, so *nothing* ran. "
     "Common causes: a missing colon, quote or bracket, or a misspelled keyword.",
     "Look at the line indicated (and the line just before it, since the real mistake "
     "is often there)."),
    ("FileNotFoundError", r".*'(?P<f>[^']+)'",
     "The file `{f}` doesn't exist",
     "Python looked for `{f}` in the current folder and couldn't find it. File names "
     "are exact, including the extension (`.csv`, `.txt`).",
     "Check the spelling. If you are reading a file you just wrote, make sure the "
     "writing code ran first."),
    ("ModuleNotFoundError", r"No module named '(?P<m>[\w.]+)'",
     "The module `{m}` isn't available",
     "Python couldn't find a library called `{m}`. It may be misspelled or not installed.",
     "Check the spelling (`pandas`, `matplotlib.pyplot`, `sqlite3`)."),
    ("EOFError", r".*",
     "`input()` ran out of input",
     "Your program called `input()` more times than there are lines in the Input box, "
     "so there was nothing left to read.",
     "Add one line to the Input box for every `input()` call your program makes."),
    ("RecursionError", r".*",
     "A function called itself too many times",
     "A recursive function needs a *base case* that stops the recursion. Without one "
     "it calls itself forever until Python gives up.",
     "Add an `if` that returns without calling the function again, and make sure "
     "each call moves closer to that case."),
    ("TimeoutError", r".*",
     "Your code ran for too long",
     "The most common cause is an infinite loop: a `while` loop whose condition never "
     "becomes `False`, often because the loop variable is never updated.",
     "Make sure something inside the loop changes the condition (e.g. `count += 1`), "
     "or use a `for` loop with `range()`."),
    ("MemoryError", r".*",
     "Your code used too much memory",
     "You created something enormous, such as a list with billions of items, or a "
     "loop that keeps appending forever.",
     "Work with smaller data or check that your loop ends."),
    ("OperationalError", r"no such table: (?P<t>\w+)",
     "SQL: the table `{t}` doesn't exist",
     "Your query refers to a table called `{t}`, but the database has no such table. "
     "It may be misspelled or not created yet.",
     "Run `CREATE TABLE` first, or list existing tables with "
     "`SELECT name FROM sqlite_master WHERE type='table'`."),
    ("OperationalError", r"no such column: (?P<c>[\w.]+)",
     "SQL: the column `{c}` doesn't exist",
     "The query uses a column name that isn't in the table. In SQL, text values must "
     "be in single quotes — `WHERE city = London` makes SQL look for a *column* "
     "called London.",
     "Check column names, and quote text values: `WHERE city = 'London'`."),
    ("OperationalError", r'near "(?P<w>[^"]+)": syntax error',
     "SQL grammar error near `{w}`",
     "SQLite couldn't parse the query around `{w}`. Typical causes: a missing comma "
     "between columns, a keyword in the wrong order (the order is SELECT, FROM, WHERE, "
     "GROUP BY, HAVING, ORDER BY, LIMIT) or a missing quote.",
     "Read the query clause by clause and compare it with that order."),
    ("IntegrityError", r".*",
     "SQL: the data broke a table rule",
     "A constraint such as `PRIMARY KEY`, `UNIQUE` or `NOT NULL` was violated — for "
     "example inserting two rows with the same id.",
     "Use a different key, or check the data before inserting."),
    ("ProgrammingError", r"Incorrect number of bindings",
     "SQL: the number of `?` placeholders doesn't match the values",
     "Each `?` in the query is filled from the tuple of parameters. The counts differ.",
     "Pass exactly one value per `?`. A single value still needs a tuple: `(name,)`."),
    ("PermissionError", r"Sandbox",
     "The sandbox blocked this action",
     "To keep your computer safe, code in this app can only read and write files in "
     "its own temporary folder and cannot run programs or use the internet.",
     "Work with files in the current folder (e.g. `open('data.txt', 'w')`)."),
    ("ImportError", r"Sandbox",
     "This module is disabled in the sandbox",
     "Some modules (networking, running programs, low-level system access) are turned "
     "off in the learning sandbox for safety.",
     "Everything needed for the course — pandas, matplotlib, sqlite3, csv, json, math, "
     "statistics, random — is available."),
]


def explain_error(error_type: str, message: str) -> Explanation:
    """Return a friendly explanation for an exception type and message."""
    for etype, pattern, title, what, fix in _RULES:
        if etype != error_type:
            continue
        m = re.search(pattern, message or "")
        if not m:
            continue
        groups = {k: (v or "").strip() for k, v in m.groupdict().items()}
        try:
            return Explanation(title.format(**groups), what.format(**groups),
                               fix.format(**groups))
        except (KeyError, IndexError):
            return Explanation(title, what, fix)
    return Explanation(
        f"{error_type}",
        f"Python raised a `{error_type}`: {message}",
        "Read the last line of the traceback: it names the error and the line where "
        "it happened. Print the variables used on that line to see their real values.",
    )


def explain_run_error(error: Optional[dict]) -> Optional[Explanation]:
    if not error:
        return None
    return explain_error(error.get("type", ""), error.get("message", ""))
