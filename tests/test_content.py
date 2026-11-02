"""Validate every piece of course content against the real interpreter.

These tests guarantee that answer keys are correct: every predict-the-output
answer matches what Python really prints, every reference solution passes its
checks, and every buggy/starter program does *not* pass.
"""

import pytest

from pylearn.content import PROJECTS, TOPICS, all_items, get_item, prelude_for
from pylearn.content.models import (MCQ, CodingExercise, DebugExercise, Example,
                                    PredictOutput)
from pylearn.grading import normalise_output
from pylearn.sandbox import run_code

ITEMS = all_items()
EXAMPLES = [(t.id, l.id, i, e) for t in TOPICS for l in t.lessons
            for i, e in enumerate(l.examples)]


def _ids(kind):
    return [i for i in ITEMS if i.kind == kind]


def test_ten_topics_in_order():
    assert [t.number for t in TOPICS] == list(range(1, 11))
    titles = [t.title for t in TOPICS]
    assert titles == [
        "Introduction & Programming Basics", "Operators & Debugging", "Control Flow",
        "Functions", "Data Types", "File Input & Output", "SQL", "Data Preparation",
        "Descriptive Analysis", "Data Visualisation"]


def test_ids_unique_and_namespaced():
    ids = [i.id for i in ITEMS] + [l.id for t in TOPICS for l in t.lessons]
    assert len(ids) == len(set(ids))
    for t in TOPICS:
        for i in t.items:
            assert i.id.startswith(t.id + "."), i.id
            assert get_item(i.id)[0] is t


def test_every_topic_has_all_exercise_kinds():
    for t in TOPICS:
        kinds = {i.kind for i in t.items}
        assert {"mcq", "predict", "debug", "code"} <= kinds, t.id
        assert len(t.lessons) >= 3
        for p in t.prerequisites:
            assert p in {x.id for x in TOPICS}


def test_in_depth_topics_have_extra_coverage():
    tags = [tag for i in ITEMS for tag in i.tags]
    for tag, minimum in {"return-vs-print": 8, "slicing": 5, "loops": 10, "dicts": 6,
                         "tuples": 8, "sql": 15, "lists": 3, "functions": 8}.items():
        assert tags.count(tag) >= minimum, (tag, tags.count(tag))


@pytest.mark.parametrize("item", _ids("mcq"), ids=lambda i: i.id)
def test_mcq_well_formed(item: MCQ):
    assert sum(o.correct for o in item.options) == 1
    assert 3 <= len(item.options) <= 5
    for o in item.options:
        if not o.correct:
            assert o.why.strip(), f"{item.id}: wrong option {o.text!r} needs a 'why'"
    assert item.explanation


@pytest.mark.parametrize("item", _ids("predict"), ids=lambda i: i.id)
def test_predict_answer_matches_python(item: PredictOutput):
    result = run_code(item.code)
    assert not result.blocked, result.blocked
    assert result.error is None, result.error
    assert normalise_output(result.stdout) == normalise_output(item.expected_output)
    for wrong, _why in item.common_wrong:
        assert normalise_output(wrong) != normalise_output(item.expected_output)


@pytest.mark.parametrize("item", _ids("debug"), ids=lambda i: i.id)
def test_debug_solution_passes_and_bug_fails(item: DebugExercise):
    good = run_code(item.solution, checks=item.checks, stdin=item.stdin)
    assert good.all_checks_passed, (good.error, good.checks)
    bad = run_code(item.buggy_code, checks=item.checks, stdin=item.stdin, timeout=4)
    assert not bad.all_checks_passed
    assert item.hints


@pytest.mark.parametrize("item", _ids("code"), ids=lambda i: i.id)
def test_coding_solution_passes_and_starter_fails(item: CodingExercise):
    good = run_code(item.solution, checks=item.checks, stdin=item.stdin)
    assert good.all_checks_passed, (good.error, good.checks)
    starter = run_code(item.starter, checks=item.checks, stdin=item.stdin, timeout=4)
    assert not starter.all_checks_passed


@pytest.mark.parametrize("ex", EXAMPLES, ids=lambda e: f"{e[1]}-{e[2]}")
def test_lesson_examples_run(ex):
    _topic, _lesson, _idx, example = ex
    example: Example
    timeout = 3 if "infinite" in example.title.lower() else 15
    result = run_code(example.code, stdin=example.stdin, timeout=timeout)
    assert not result.blocked, result.blocked
    if result.error:
        # Some examples deliberately demonstrate an error; they say so.
        assert result.error["type"] != "SandboxError", result.error
        demo_words = ("error", "crash", "mistake", "infinite", "missing", "vanish",
                      "immutable", "bad chart")
        text = (example.title + " " + example.explanation).lower()
        assert any(w in text for w in demo_words), (example.title, result.error)


@pytest.mark.parametrize("project", PROJECTS, ids=lambda p: p.id)
def test_project_steps(project):
    assert len(project.steps) >= 3
    for idx, step in enumerate(project.steps):
        prelude = prelude_for(project, idx)
        good = run_code(step.solution, setup=project.setup_code, prelude=prelude,
                        checks=step.checks, timeout=30)
        assert good.setup_error is None, good.setup_error
        assert good.all_checks_passed, (project.id, idx, good.error, good.checks)
        starter = run_code(step.starter, setup=project.setup_code, prelude=prelude,
                           checks=step.checks, timeout=30)
        assert not starter.all_checks_passed, (project.id, idx)
