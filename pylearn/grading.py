"""Answer checking and beginner-friendly feedback for every exercise type."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional

from .content.models import MCQ, CodingExercise, DebugExercise, PredictOutput
from .explain import explain_run_error
from .sandbox import RunResult, run_code


@dataclass
class Feedback:
    correct: bool
    headline: str
    details: list[str] = field(default_factory=list)  # markdown bullet points
    run: Optional[RunResult] = None
    explanation: str = ""  # the concept explanation shown after answering


# --------------------------------------------------------------------- MCQ --
def grade_mcq(item: MCQ, choice: Optional[int]) -> Feedback:
    if choice is None:
        return Feedback(False, "Please choose an answer first.")
    opt = item.options[choice]
    right = item.options[item.correct_index]
    if opt.correct:
        details = [opt.why] if opt.why else []
        return Feedback(True, "✅ Correct!", details, explanation=item.explanation)
    details = []
    if opt.why:
        details.append(f"**Why “{opt.text}” is wrong:** {opt.why}")
    details.append(f"**The correct answer is “{right.text}”.** {right.why}".strip())
    return Feedback(False, "❌ Not quite.", details, explanation=item.explanation)


# ------------------------------------------------------- predict-the-output --
def normalise_output(text: str) -> str:
    lines = [line.rstrip() for line in (text or "").replace("\r\n", "\n").split("\n")]
    while lines and not lines[0]:
        lines.pop(0)
    while lines and not lines[-1]:
        lines.pop()
    return "\n".join(lines)


def _strip_quotes(s: str) -> str:
    return re.sub(r"""['"]""", "", s)


def output_diff_hints(expected: str, answer: str) -> list[str]:
    """Generic heuristics explaining *why* a predicted output differs."""
    exp, ans = normalise_output(expected), normalise_output(answer)
    hints: list[str] = []
    if not ans:
        return ["You left the answer empty. Type exactly what the program prints, "
                "one line per `print()` call."]
    exp_lines, ans_lines = exp.split("\n"), ans.split("\n")
    if exp.lower() == ans.lower():
        hints.append("Your answer only differs in **capital letters**. Python output is "
                     "case-sensitive: `True` is not `true`, `'Hi'` is not `'hi'`.")
    elif _strip_quotes(exp) == _strip_quotes(ans):
        if ans.count("'") + ans.count('"') > exp.count("'") + exp.count('"'):
            hints.append("You added **quotes**. `print()` shows strings *without* quotes "
                         "(`print('hi')` → `hi`). Quotes only appear when a string is "
                         "shown *inside* a list, tuple or dict, e.g. `['hi']`.")
        else:
            hints.append("You left out **quotes**. When a list, tuple or dict is printed, "
                         "the strings inside it are shown with quotes: "
                         "`print(['a'])` → `['a']`.")
    elif " ".join(exp.split()) == " ".join(ans.split()):
        if len(exp_lines) != len(ans_lines):
            hints.append("The values are right but the **line breaks** differ. Each "
                         "`print()` normally ends with a new line; `print(a, b)` puts "
                         "both values on one line separated by a space; `end=''` "
                         "changes what goes at the end.")
        else:
            hints.append("Check the **spaces**. `print(a, b)` adds one space between "
                         "values, but `+` between strings adds none.")
    elif sorted(exp_lines) == sorted(ans_lines):
        hints.append("You have the right lines in the **wrong order**. Python runs "
                     "statements top to bottom, and a loop finishes one pass before "
                     "starting the next.")
    else:
        if len(ans_lines) != len(exp_lines):
            hints.append(f"The program prints **{len(exp_lines)} line(s)**, but your answer "
                         f"has {len(ans_lines)}. Count the `print()` calls that actually "
                         "run — a loop body runs once per item, and `range(n)` stops "
                         "*before* n.")
        if "None" in exp and "None" not in ans:
            hints.append("The real output contains **`None`**. A function with no "
                         "`return` statement gives back `None`, and printing that "
                         "result shows `None`.")
        if "None" in ans and "None" not in exp:
            hints.append("There is no `None` in the output — the function *does* return "
                         "a value here.")
        if re.search(r"\d+\.\d+", exp) and not re.search(r"\d+\.\d+", ans):
            hints.append("The output contains a **decimal (float)**. In Python 3, `/` "
                         "always gives a float (`6 / 2` → `3.0`); use `//` for whole-"
                         "number division.")
        if re.search(r"\d+\.\d+", ans) and not re.search(r"\d+\.\d+", exp):
            hints.append("The output has **no decimals**. `//` and `int()` give whole "
                         "numbers, and `len()` / `range()` always work with integers.")
        if ("Error" in exp) != ("Error" in ans):
            if "Error" in exp:
                hints.append("This code actually **raises an error** — look for an "
                             "operation that can't work.")
            else:
                hints.append("This code runs without an error.")
        for i, (e, a) in enumerate(zip(exp_lines, ans_lines), start=1):
            if e != a:
                hints.append(f"The first difference is on **line {i}**: Python prints "
                             f"`{e}` but you wrote `{a}`.")
                break
    return hints


def grade_predict(item: PredictOutput, answer: str) -> Feedback:
    exp = normalise_output(item.expected_output)
    ans = normalise_output(answer)
    if ans == exp:
        return Feedback(True, "✅ Correct — that's exactly what Python prints!",
                        explanation=item.explanation)
    details = []
    for wrong, why in item.common_wrong:
        if normalise_output(wrong) == ans:
            details.append(why)
            break
    details.extend(output_diff_hints(exp, ans))
    return Feedback(False, "❌ That's not what Python prints.", details,
                    explanation=item.explanation)


# ----------------------------------------------------------- code & debug --
def feedback_from_run(run: RunResult, success_msg: str = "✅ All checks passed!") -> Feedback:
    """Explain the outcome of running code against checks."""
    if run.blocked:
        return Feedback(False, "⛔ This code isn't allowed in the sandbox.", [run.blocked], run=run)
    details: list[str] = []
    if run.error:
        exp = explain_run_error(run.error)
        line = f" on line {run.error['line']}" if run.error.get("line") else ""
        details.append(f"**{run.error['type']}{line}: {exp.title}.** {exp.what_happened}")
        details.append(f"**How to fix it:** {exp.how_to_fix}")
        return Feedback(False, "💥 Your code stopped with an error.", details, run=run)
    if run.setup_error:
        details.append("The exercise's data could not be prepared: " + run.setup_error)
    if run.all_checks_passed:
        return Feedback(True, success_msg, run=run)
    for c in run.checks:
        if c.passed:
            details.append(f"✔️ {c.description}")
            continue
        if c.error:
            details.append(f"✖️ {c.description} — checking it caused an error: `{c.error}`")
            if "NameError" in c.error:
                details.append("  Make sure you created that variable/function with "
                               "exactly the name the task asks for.")
            continue
        msg = f"✖️ {c.description}"
        if c.expected is not None:
            msg += f" — expected `{c.expected}`, got `{c.actual}`"
        details.append(msg)
        if c.actual_is_none and c.expected not in (None, "None"):
            if c.printed.strip():
                details.append("  🔎 Your function **printed** "
                               f"`{c.printed.strip()[:80]}` but **returned** `None`. "
                               "`print()` only shows a value on the screen; the caller "
                               "receives nothing. Use `return` to send the value back.")
            else:
                details.append("  🔎 Your code produced `None`. Did you forget a "
                               "`return` statement, or store the result of an in-place "
                               "method like `.sort()`?")
        elif c.actual and c.expected and c.actual.strip("'\"") == c.expected.strip("'\"") \
                and c.actual != c.expected:
            details.append("  🔎 The value looks right but has the wrong **type** — e.g. "
                           "the text `'5'` instead of the number `5`. Convert it with "
                           "`int()`, `float()` or `str()`.")
    return Feedback(False, "🟠 Some checks didn't pass yet.", details, run=run)


def grade_code(item: CodingExercise | DebugExercise, code: str) -> Feedback:
    stdin = getattr(item, "stdin", "")
    run = run_code(code, checks=item.checks, stdin=stdin)
    fb = feedback_from_run(run)
    fb.explanation = item.explanation
    return fb
