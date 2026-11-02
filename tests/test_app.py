"""End-to-end UI tests using Streamlit's AppTest harness."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parents[1] / "app.py")


@pytest.fixture
def at(tmp_path, monkeypatch):
    monkeypatch.setenv("PYLEARN_DATA_DIR", str(tmp_path))
    import streamlit as st
    st.cache_resource.clear()
    app = AppTest.from_file(APP, default_timeout=120)
    app.run()
    assert not app.exception
    return app


def goto(at, page):
    at.sidebar.radio(key="page").set_value(page).run()
    assert not at.exception, [e.message for e in at.exception]


def button(at, label):
    return next(b for b in at.button if b.label == label)


@pytest.mark.parametrize("page", ["🏠 Dashboard", "📚 Learn", "🧪 Sandbox", "🔁 Review",
                                  "🛠️ Projects", "ℹ️ About"])
def test_every_page_renders(at, page):
    goto(at, page)


def test_every_topic_renders(at):
    goto(at, "📚 Learn")
    for tid in [f"t{n:02d}" for n in range(1, 11)]:
        at.selectbox(key="topic_select").set_value(tid).run()
        assert not at.exception, tid


def test_mcq_answer_updates_progress(at):
    goto(at, "📚 Learn")
    at.radio(key="practice-t01.mcq.type_of_input-choice").set_value(1).run()
    at.button(key="practice-t01.mcq.type_of_input-check").click().run()
    assert any("Not quite" in e.value for e in at.error)
    assert any("Why" in m.value for m in at.markdown)
    at.radio(key="practice-t01.mcq.type_of_input-choice").set_value(0).run()
    at.button(key="practice-t01.mcq.type_of_input-check").click().run()
    assert any("Correct" in s.value for s in at.success)
    goto(at, "🏠 Dashboard")
    assert at.metric[1].value == "2"  # questions answered


def test_coding_exercise_check_and_hint(at):
    goto(at, "📚 Learn")
    at.selectbox(key="topic_select").set_value("t04").run()
    key = "practice-t04.code.celsius"
    at.text_area(key=f"{key}-code").input("def to_fahrenheit(c):\n    print(c * 9 / 5 + 32)").run()
    at.button(key=f"{key}-check").click().run()
    assert not at.exception
    assert any("returned" in m.value and "None" in m.value for m in at.markdown)
    at.button(key=f"{key}-hint").click().run()
    assert any("return" in m.value for m in at.markdown if m.value.startswith("💡"))
    at.text_area(key=f"{key}-code").input("def to_fahrenheit(c):\n    return c * 9 / 5 + 32").run()
    at.button(key=f"{key}-check").click().run()
    assert any("All checks passed" in s.value for s in at.success)


def test_lesson_example_runs_and_lesson_completes(at):
    goto(at, "📚 Learn")
    at.button(key="ex-t01.l1-0-run").click().run()
    assert any("Hello, data world!" in c.value for c in at.code)
    at.button(key="done-t01.l1").click().run()
    assert any("Lesson completed" in s.value for s in at.success)


def test_quiz_submission(at):
    goto(at, "📚 Learn")
    at.button(key="FormSubmitter:quiz-t01-Submit quiz").click().run()
    assert not at.exception
    assert any("You scored" in w.value for w in list(at.warning) + list(at.success))


def test_sandbox_runs_code_and_explains_errors(at):
    goto(at, "🧪 Sandbox")
    at.text_area(key="sbx-code").input("nums = [1, 2]\nprint(nums[5])").run()
    button(at, "▶ Run code").click().run()
    assert any("position that doesn't exist" in m.value for m in at.markdown)


def test_project_step_check(at):
    goto(at, "🛠️ Projects")
    from pylearn.content import PROJECTS
    sol = PROJECTS[0].steps[0].solution
    at.text_area(key="proj-p1-0-code").input(sol).run()
    at.button(key="proj-p1-0-check").click().run()
    assert any("Step complete" in s.value for s in at.success)


def test_review_flow(at):
    goto(at, "📚 Learn")
    at.radio(key="practice-t01.mcq.type_of_input-choice").set_value(1).run()
    at.button(key="practice-t01.mcq.type_of_input-check").click().run()
    goto(at, "🔁 Review")
    # Concept drill always has items.
    assert any("exercise(s) tagged" in c.value for c in at.caption)
