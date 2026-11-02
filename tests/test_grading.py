from pylearn.content import get_item
from pylearn.explain import explain_error
from pylearn.grading import (feedback_from_run, grade_code, grade_mcq, grade_predict,
                             normalise_output, output_diff_hints)
from pylearn.sandbox import run_code
from pylearn.content.models import Check


def test_mcq_correct_and_wrong_explain_why():
    _, item = get_item("t04.mcq.return_vs_print")
    ok = grade_mcq(item, item.correct_index)
    assert ok.correct and ok.explanation
    wrong_idx = next(i for i, o in enumerate(item.options) if not o.correct)
    bad = grade_mcq(item, wrong_idx)
    assert not bad.correct
    assert any("Why" in d for d in bad.details)
    assert any("correct answer" in d for d in bad.details)
    assert not grade_mcq(item, None).correct


def test_normalise_output():
    assert normalise_output("\n a  \nb\t\n\n") == " a\nb"
    assert normalise_output("x\r\ny") == "x\ny"


def test_predict_specific_common_wrong_answer():
    _, item = get_item("t04.pred.none_printed")
    fb = grade_predict(item, "HEY")
    assert not fb.correct
    assert "outer `print`" in fb.details[0]
    assert grade_predict(item, "HEY\nNone\n").correct


def test_predict_generic_hints():
    assert any("quotes" in h for h in output_diff_hints("hello", "'hello'"))
    assert any("capital" in h for h in output_diff_hints("True", "true"))
    assert any("float" in h.lower() for h in output_diff_hints("4.0", "4"))
    assert any("None" in h for h in output_diff_hints("5\nNone", "5"))
    assert any("order" in h for h in output_diff_hints("a\nb", "b\na"))
    assert any("line breaks" in h for h in output_diff_hints("a\nb", "a b"))
    assert any("empty" in h for h in output_diff_hints("a", ""))


def test_code_feedback_print_instead_of_return():
    _, item = get_item("t04.code.celsius")
    fb = grade_code(item, "def to_fahrenheit(c):\n    print(c * 9 / 5 + 32)")
    assert not fb.correct
    text = "\n".join(fb.details)
    assert "printed" in text and "return" in text


def test_code_feedback_error_is_explained():
    _, item = get_item("t04.code.celsius")
    fb = grade_code(item, "def to_fahrenheit(c):\n    return c * 9 / 5 + 32 +")
    assert not fb.correct and "SyntaxError" in fb.details[0]
    assert any("How to fix" in d for d in fb.details)


def test_code_feedback_wrong_type_hint():
    run = run_code("x = '5'", checks=[Check("x is 5", expr="x", expected=5)])
    fb = feedback_from_run(run)
    assert any("wrong **type**" in d for d in fb.details)


def test_code_feedback_missing_name():
    run = run_code("y = 1", checks=[Check("x exists", expr="x", expected=1)])
    fb = feedback_from_run(run)
    assert any("NameError" in d for d in fb.details)


def test_code_feedback_blocked():
    _, item = get_item("t04.code.celsius")
    fb = grade_code(item, "import subprocess")
    assert not fb.correct and "sandbox" in fb.headline.lower()


def test_correct_solution_passes():
    _, item = get_item("t05.code.word_count")
    assert grade_code(item, item.solution).correct


def test_explanations_cover_common_errors():
    cases = {
        ("NameError", "name 'totl' is not defined"): "totl",
        ("TypeError", 'can only concatenate str (not "int") to str'): "str(",
        ("TypeError", "unsupported operand type(s) for +: 'NoneType' and 'int'"): "return",
        ("TypeError", "'NoneType' object is not subscriptable"): "return",
        ("TypeError", "'tuple' object does not support item assignment"): "immutable",
        ("IndexError", "list index out of range"): "0",
        ("KeyError", "'colour'"): "get",
        ("AttributeError", "'NoneType' object has no attribute 'append'"): "None",
        ("ValueError", "invalid literal for int() with base 10: 'abc'"): "int()",
        ("ZeroDivisionError", "division by zero"): "zero",
        ("SyntaxError", "expected ':'"): "colon",
        ("IndentationError", "expected an indented block"): "indent",
        ("OperationalError", "no such column: Leeds"): "quote",
        ("OperationalError", "no such table: custmers"): "custmers",
        ("TimeoutError", "too long"): "loop",
        ("EOFError", "EOF when reading a line"): "input",
    }
    for (etype, msg), needle in cases.items():
        e = explain_error(etype, msg)
        blob = (e.title + e.what_happened + e.how_to_fix).lower()
        assert needle.lower() in blob, (etype, msg)


def test_unknown_error_has_generic_explanation():
    e = explain_error("WeirdError", "something odd")
    assert "WeirdError" in e.what_happened and e.how_to_fix
