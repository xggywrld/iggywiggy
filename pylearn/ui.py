"""Reusable Streamlit widgets: code runner, exercise cards and feedback."""

from __future__ import annotations

import html
from typing import Optional

import streamlit as st

from .content.models import MCQ, CodingExercise, DebugExercise, Item, PredictOutput, Topic
from .explain import explain_run_error
from .grading import Feedback, grade_code, grade_mcq, grade_predict
from .progress import ProgressStore
from .sandbox import RunResult, run_code

KIND_LABEL = {"mcq": "🔘 Multiple choice", "predict": "🔮 Predict the output",
              "debug": "🐞 Fix the bug", "code": "⌨️ Write the code"}

CSS = """
<style>
  .block-container {padding-top: 2rem; max-width: 1150px;}
  textarea {font-family: "JetBrains Mono", "Fira Code", Menlo, Consolas, monospace !important;
            font-size: 0.9rem !important;}
  .pl-card {border: 1px solid rgba(128,128,128,.25); border-radius: 12px;
            padding: 0.9rem 1.1rem; margin-bottom: .6rem;
            background: rgba(127,127,127,.04);}
  .pl-hero {padding: 1.2rem 1.4rem; border-radius: 14px; margin-bottom: 1rem;
            background: linear-gradient(120deg, rgba(55,118,171,.18), rgba(255,212,59,.16));}
  .pl-hero h1 {margin: 0 0 .3rem 0; font-size: 1.9rem;}
  .pl-tag {display: inline-block; padding: 1px 8px; margin: 0 4px 4px 0; border-radius: 999px;
           font-size: .75rem; background: rgba(55,118,171,.15);}
  .pl-level {font-weight: 600;}
</style>
"""


def inject_css() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


def tags_html(tags) -> str:
    return "".join(f'<span class="pl-tag">{html.escape(t)}</span>' for t in tags)


def _height(code: str, minimum: int = 120, maximum: int = 520) -> int:
    return max(minimum, min(maximum, 26 * (code.count("\n") + 2)))


# ------------------------------------------------------------ running code --
def show_run(run: RunResult, *, show_checks: bool = False) -> None:
    """Render stdout, charts and a friendly error explanation."""
    if run.blocked:
        st.warning("⛔ " + run.blocked)
        return
    if run.stdout:
        st.markdown("**Output**")
        st.code(run.stdout + ("\n… (output truncated)" if run.truncated else ""), language="text")
    elif run.ok and not run.figures:
        st.caption("(The code ran but printed nothing.)")
    for png in run.figures:
        st.image(png)
    if run.error:
        exp = explain_run_error(run.error)
        line = f" (line {run.error['line']})" if run.error.get("line") else ""
        with st.container(border=True):
            st.markdown(f"**💥 {run.error['type']}{line}: {exp.title}**")
            st.markdown(exp.what_happened)
            st.markdown(f"**How to fix it:** {exp.how_to_fix}")
            if run.error.get("traceback"):
                with st.expander("Show Python's original error message"):
                    st.code(run.error["traceback"], language="text")
    if show_checks and run.checks:
        for c in run.checks:
            st.markdown(("✔️ " if c.passed else "✖️ ") + c.description)


def code_runner(key: str, code: str, *, stdin: str = "", show_stdin: Optional[bool] = None,
                setup: str = "", prelude: str = "", run_label: str = "▶ Run") -> None:
    """An editable code box with a Run button."""
    edited = st.text_area("Code", value=code, key=f"{key}-code", height=_height(code),
                          label_visibility="collapsed")
    if show_stdin is None:
        show_stdin = bool(stdin) or "input(" in code
    user_in = stdin
    if show_stdin:
        user_in = st.text_area("Input (one line per `input()` call)", value=stdin,
                               key=f"{key}-stdin", height=80)
    if st.button(run_label, key=f"{key}-run"):
        with st.spinner("Running in the sandbox…"):
            st.session_state[f"{key}-result"] = run_code(edited, stdin=user_in, setup=setup,
                                                         prelude=prelude)
    res = st.session_state.get(f"{key}-result")
    if res is not None:
        show_run(res)


def show_feedback(fb: Feedback) -> None:
    if fb.correct:
        box = st.success
    else:  # partially-passing code is encouraging news, not a failure
        box = st.warning if fb.headline.startswith("🟠") else st.error
    box(fb.headline)
    for d in fb.details:
        st.markdown(("- " if not d.startswith("  ") else "   - ") + d.strip())
    if fb.run is not None and (fb.run.stdout or fb.run.figures):
        with st.expander("What your code printed / drew", expanded=not fb.correct):
            if fb.run.stdout:
                st.code(fb.run.stdout, language="text")
            for png in fb.run.figures:
                st.image(png)
    if fb.explanation:
        st.info("💡 " + fb.explanation)


# --------------------------------------------------------- exercise cards --
def render_item(item: Item, topic: Topic, store: ProgressStore, learner: int, *,
                ctx: str = "practice", number: Optional[int] = None) -> None:
    """Render one interactive exercise and record attempts."""
    key = f"{ctx}-{item.id}"
    fb_key = f"{key}-fb"
    title = KIND_LABEL[item.kind] + (f" · Q{number}" if number else "")
    with st.container(border=True):
        st.markdown(f"**{title}** {tags_html(item.tags)}", unsafe_allow_html=True)
        st.markdown(item.prompt)

        def record(fb: Feedback, hints: int = 0) -> None:
            store.record_attempt(learner, item.id, topic.id, item.kind, fb.correct,
                                 source=ctx, hints_used=hints)
            st.session_state[fb_key] = fb

        if isinstance(item, MCQ):
            if item.code:
                st.code(item.code, language="python")
            labels = [o.text for o in item.options]
            choice = st.radio("Choose one", options=list(range(len(labels))),
                              format_func=lambda i: labels[i], index=None,
                              key=f"{key}-choice", label_visibility="collapsed")
            if st.button("Check answer", key=f"{key}-check"):
                if choice is None:
                    st.warning("Pick an option first.")
                else:
                    record(grade_mcq(item, choice))

        elif isinstance(item, PredictOutput):
            st.code(item.code, language="python")
            answer = st.text_area("Your predicted output (exactly as printed)", key=f"{key}-answer",
                                  height=max(80, 26 * (item.expected_output.count("\n") + 2)))
            c1, c2 = st.columns(2)
            if c1.button("Check prediction", key=f"{key}-check"):
                if not answer.strip():
                    st.warning("Type what you think the program prints first.")
                else:
                    record(grade_predict(item, answer))
            if fb_key in st.session_state and c2.button("▶ Run it and see", key=f"{key}-reveal"):
                st.session_state[f"{key}-ran"] = run_code(item.code)
            if f"{key}-ran" in st.session_state:
                show_run(st.session_state[f"{key}-ran"])

        elif isinstance(item, (DebugExercise, CodingExercise)):
            initial = item.buggy_code if isinstance(item, DebugExercise) else item.starter
            code = st.text_area("Your code", value=initial, key=f"{key}-code",
                                height=_height(initial, 160), label_visibility="collapsed")
            if item.stdin:
                st.caption("Input given to `input()`: " + " / ".join(item.stdin.split()))
            hint_key = f"{key}-hints"
            hints_shown = st.session_state.get(hint_key, 0)
            c1, c2, c3, c4 = st.columns(4)
            if c1.button("▶ Run", key=f"{key}-run"):
                st.session_state[f"{key}-ran"] = run_code(code, stdin=item.stdin)
                st.session_state.pop(fb_key, None)
            if c2.button("✅ Check", key=f"{key}-check"):
                with st.spinner("Testing your code…"):
                    record(grade_code(item, code), hints=hints_shown)
                st.session_state.pop(f"{key}-ran", None)
            if c3.button("💡 Hint", key=f"{key}-hint", disabled=hints_shown >= len(item.hints)):
                st.session_state[hint_key] = hints_shown = hints_shown + 1
            show_solution = c4.toggle("Solution", key=f"{key}-sol",
                                      help="Available after your first check.",
                                      disabled=fb_key not in st.session_state)
            for h in item.hints[:hints_shown]:
                st.markdown(f"💡 *{h}*")
            if f"{key}-ran" in st.session_state:
                show_run(st.session_state[f"{key}-ran"])
            if show_solution:
                st.markdown("**A reference solution** (yours can differ and still be right):")
                st.code(item.solution, language="python")

        fb = st.session_state.get(fb_key)
        if fb is not None:
            show_feedback(fb)
