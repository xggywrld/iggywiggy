"""PyLearn — an interactive Python course for Data Science & AI beginners.

Run with:  streamlit run app.py
"""

from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd
import streamlit as st

from pylearn.content import PROJECTS, TOPICS, all_tags, get_item, get_topic, prelude_for
from pylearn.content.models import MCQ, PredictOutput
from pylearn.grading import feedback_from_run, grade_mcq, grade_predict
from pylearn.progress import ProgressStore, recommend
from pylearn.sandbox import run_code
from pylearn.ui import code_runner, inject_css, render_item, show_feedback, show_run, tags_html

st.set_page_config(page_title="PyLearn · Python for Data Science", page_icon="🐍",
                   layout="wide")
inject_css()

PAGES = ["🏠 Dashboard", "📚 Learn", "🧪 Sandbox", "🔁 Review", "🛠️ Projects", "ℹ️ About"]


@st.cache_resource
def get_store() -> ProgressStore:
    return ProgressStore()


store = get_store()


# --------------------------------------------------------------- sidebar --
def sidebar() -> tuple[str, int]:
    with st.sidebar:
        st.markdown("## 🐍 PyLearn")
        st.caption("Python for Data Science & AI")
        names = store.learners() or ["Learner"]
        current = st.session_state.get("learner_name", names[0])
        if current not in names:
            names.append(current)
        name = st.selectbox("Learner profile", names, index=names.index(current))
        with st.expander("➕ New profile"):
            new = st.text_input("Name", key="new_profile")
            if st.button("Create profile") and new.strip():
                store.learner_id(new.strip())
                st.session_state["learner_name"] = new.strip()
                st.rerun()
        st.session_state["learner_name"] = name
        learner = store.learner_id(name)
        if "nav_to" in st.session_state:  # navigation requested by a button
            st.session_state["page"] = st.session_state.pop("nav_to")
        page = st.radio("Go to", PAGES, key="page", label_visibility="collapsed")
        due = len(store.due_items(learner))
        stats = store.attempt_stats(learner)
        st.divider()
        st.metric("Reviews due", due)
        st.metric("Study streak", f"{stats['streak_days']} day(s)")
    return page, learner


def topic_mastery(learner: int, topic):
    return store.topic_mastery(learner, topic.id, [i.id for i in topic.items],
                               [l.id for l in topic.lessons])


# ------------------------------------------------------------- dashboard --
def page_dashboard(learner: int) -> None:
    name = st.session_state["learner_name"]
    st.markdown(
        f'<div class="pl-hero"><h1>Welcome back, {name} 👋</h1>'
        "Learn Python for Data Science one runnable example at a time. Every answer "
        "you give updates your mastery scores and your spaced-repetition schedule.</div>",
        unsafe_allow_html=True)
    stats = store.attempt_stats(learner)
    masteries = [topic_mastery(learner, t) for t in TOPICS]
    overall = sum(m.score for m in masteries) / len(masteries)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Overall mastery", f"{overall:.0f}/100")
    c2.metric("Questions answered", stats["attempts"])
    c3.metric("Accuracy", "–" if stats["accuracy"] is None else f"{stats['accuracy']:.0%}")
    c4.metric("Reviews due", len(store.due_items(learner)))

    left, right = st.columns([3, 2])
    with left:
        st.subheader("Your mastery by topic")
        for t, m in zip(TOPICS, masteries):
            st.progress(min(1.0, m.score / 100),
                        text=f"{t.icon} {t.number}. {t.title} — **{m.score:.0f}** · {m.level} "
                             f"({m.items_attempted}/{m.items_total} exercises, "
                             f"{m.lessons_done}/{m.lessons_total} lessons)")
        st.caption("Mastery = 20% lessons completed + 80% exercise performance (recent answers "
                   "weigh more). Levels: Learning < 40 ≤ Developing < 70 ≤ Proficient < 90 ≤ Mastered.")
    with right:
        st.subheader("Recommended next")
        recs = recommend(store, learner, TOPICS)
        if not recs:
            st.info("Start with topic 1 in **📚 Learn**.")
        for r in recs:
            with st.container(border=True):
                st.markdown(f"**{r.title}**")
                st.caption(r.reason)
                if r.topic_id and st.button("Open topic", key=f"rec-{r.kind}-{r.topic_id}"):
                    st.session_state["topic_select"] = r.topic_id
                    st.session_state["nav_to"] = "📚 Learn"
                    st.rerun()
                if r.kind == "review" and st.button("Start review", key="rec-review"):
                    st.session_state["nav_to"] = "🔁 Review"
                    st.rerun()

    hist = store.history(learner, 500)
    if hist:
        st.subheader("Activity")
        df = pd.DataFrame(hist)
        df["day"] = df["created_at"].str[:10]
        daily = df.groupby("day").agg(answered=("correct", "size"), correct=("correct", "sum"))
        st.bar_chart(daily)
        with st.expander("Recent answers"):
            recent = df.head(20).copy()
            recent["result"] = recent["correct"].map({1: "✅", 0: "❌"})
            st.dataframe(recent[["created_at", "topic_id", "item_id", "kind", "source", "result"]],
                         hide_index=True)


# ----------------------------------------------------------------- learn --
def page_learn(learner: int) -> None:
    ids = [t.id for t in TOPICS]
    if st.session_state.get("topic_select") not in ids:
        st.session_state["topic_select"] = ids[0]

    def label(tid):
        t = get_topic(tid)
        return f"{t.icon} {t.number}. {t.title}"

    topic_id = st.selectbox("Topic", ids, format_func=label, key="topic_select")
    topic = get_topic(topic_id)
    m = topic_mastery(learner, topic)
    st.markdown(f"### {topic.icon} Topic {topic.number}: {topic.title}")
    st.markdown(f"{topic.summary}  \nMastery: **{m.score:.0f}/100** · "
                f'<span class="pl-level">{m.level}</span>', unsafe_allow_html=True)
    if topic.prerequisites:
        pre = [get_topic(p) for p in topic.prerequisites]
        weak = [p for p in pre if topic_mastery(learner, p).score < 40]
        if weak:
            st.warning("Recommended first: " + ", ".join(f"{p.number}. {p.title}" for p in weak)
                       + " (mastery below 40). You can still continue.")

    tab_lessons, tab_practice, tab_quiz = st.tabs(["📖 Lessons", "🏋️ Practice", "📝 Quiz"])
    with tab_lessons:
        lessons_tab(topic, learner)
    with tab_practice:
        practice_tab(topic, learner)
    with tab_quiz:
        quiz_tab(topic, learner)


def lessons_tab(topic, learner: int) -> None:
    done = store.lessons_done(learner)
    names = [f"{'✅' if l.id in done else '⬜'} {i}. {l.title}" for i, l in enumerate(topic.lessons, 1)]
    idx = st.radio("Lesson", list(range(len(names))), format_func=lambda i: names[i],
                   horizontal=False, key=f"lesson-{topic.id}")
    lesson = topic.lessons[idx]
    st.markdown(f"## {lesson.title}")
    st.markdown(lesson.body)
    if lesson.examples:
        st.markdown("### ▶ Try it yourself")
    for j, ex in enumerate(lesson.examples):
        with st.container(border=True):
            st.markdown(f"**Example {j + 1}: {ex.title}**")
            if ex.explanation:
                st.caption(ex.explanation)
            code_runner(f"ex-{lesson.id}-{j}", ex.code, stdin=ex.stdin)
    if lesson.key_points:
        st.markdown("### 🔑 Key points")
        for kp in lesson.key_points:
            st.markdown(f"- {kp}")
    if lesson.id in done:
        st.success("Lesson completed — practise it in the 🏋️ Practice tab.")
    elif st.button("✅ Mark lesson as complete", key=f"done-{lesson.id}"):
        store.mark_lesson(learner, lesson.id, topic.id)
        st.rerun()


def practice_tab(topic, learner: int) -> None:
    scores = store.item_scores(learner)
    kinds = {"All": None, "Multiple choice": "mcq", "Predict the output": "predict",
             "Fix the bug": "debug", "Write the code": "code"}
    c1, c2 = st.columns([2, 1])
    choice = c1.radio("Show", list(kinds), horizontal=True, key=f"kind-{topic.id}")
    only_todo = c2.toggle("Only unsolved / weak", key=f"todo-{topic.id}")
    items = [i for i in topic.items if kinds[choice] in (None, i.kind)]
    if only_todo:
        items = [i for i in items if scores.get(i.id, 0) < 0.75]
    if not items:
        st.success("Nothing left here — great work! 🎉")
    for n, item in enumerate(items, 1):
        render_item(item, topic, store, learner, ctx="practice", number=n)


def quiz_tab(topic, learner: int) -> None:
    questions = [i for i in topic.items if isinstance(i, (MCQ, PredictOutput))]
    st.markdown(f"A {len(questions)}-question check of the whole topic. Answer everything, then "
                "submit to see your score and an explanation for each question.")
    rkey = f"quiz-result-{topic.id}"
    with st.form(f"quiz-{topic.id}"):
        answers = {}
        for n, q in enumerate(questions, 1):
            st.markdown(f"**Q{n}.** {q.prompt}")
            if q.code:
                st.code(q.code, language="python")
            if isinstance(q, MCQ):
                labels = [o.text for o in q.options]
                answers[q.id] = st.radio(f"Q{n}", list(range(len(labels))), index=None,
                                         format_func=lambda i, labels=labels: labels[i],
                                         key=f"quiz-{q.id}", label_visibility="collapsed")
            else:
                answers[q.id] = st.text_area(f"Q{n} output", key=f"quiz-{q.id}", height=90,
                                             label_visibility="collapsed",
                                             placeholder="Type the exact output")
            st.divider()
        submitted = st.form_submit_button("Submit quiz")
    if submitted:
        results = []
        for q in questions:
            a = answers[q.id]
            fb = grade_mcq(q, a) if isinstance(q, MCQ) else grade_predict(q, a or "")
            store.record_attempt(learner, q.id, topic.id, q.kind, fb.correct, source="quiz")
            results.append((q, fb))
        st.session_state[rkey] = results
    results = st.session_state.get(rkey)
    if results:
        score = sum(fb.correct for _, fb in results)
        pct = score / len(results)
        (st.success if pct >= 0.7 else st.warning)(
            f"You scored **{score}/{len(results)}** ({pct:.0%}). "
            + ("Excellent!" if pct >= 0.9 else "Good — review the ones you missed." if pct >= 0.7
               else "Re-read the lessons, then try the Practice tab before retaking the quiz."))
        for n, (q, fb) in enumerate(results, 1):
            with st.expander(f"{'✅' if fb.correct else '❌'} Q{n}: {q.prompt[:80]}",
                             expanded=not fb.correct):
                if isinstance(q, PredictOutput):
                    st.markdown("**Actual output:**")
                    st.code(q.expected_output, language="text")
                show_feedback(fb)


# --------------------------------------------------------------- sandbox --
SNIPPETS = {
    "Hello world": 'print("Hello, world!")',
    "Blank": "",
    "Read input": 'name = input()\nage = int(input())\nprint(f"{name} will be {age + 1} next year")',
    "pandas DataFrame": "import pandas as pd\ndf = pd.DataFrame({'city': ['Leeds', 'York', 'Hull'], 'pop': [812, 211, 267]})\nprint(df.describe())\nprint(df.sort_values('pop', ascending=False))",
    "SQLite": "import sqlite3\nconn = sqlite3.connect(':memory:')\nconn.execute('CREATE TABLE t (name TEXT, score INT)')\nconn.executemany('INSERT INTO t VALUES (?, ?)', [('a', 3), ('b', 9), ('c', 5)])\nprint(conn.execute('SELECT name, score FROM t ORDER BY score DESC').fetchall())",
    "matplotlib chart": "import matplotlib.pyplot as plt\nfig, ax = plt.subplots(figsize=(6, 3))\nax.plot([1, 2, 3, 4], [10, 14, 9, 17], marker='o')\nax.set_title('My first chart')\nax.set_xlabel('Week')\nax.set_ylabel('Sales')",
    "Files": "with open('data.txt', 'w') as f:\n    f.write('3\\n5\\n8\\n')\nwith open('data.txt') as f:\n    print(sum(int(line) for line in f))",
}


def page_sandbox(_learner: int) -> None:
    st.markdown("## 🧪 Python sandbox")
    st.markdown("Write and run any Python code. pandas, matplotlib, sqlite3, csv, json, math, "
                "statistics and random are available. Charts appear automatically.")
    snippet = st.selectbox("Start from a template", list(SNIPPETS), key="sbx-template")
    if st.session_state.get("sbx-last-template") != snippet:
        st.session_state["sbx-last-template"] = snippet
        st.session_state["sbx-code"] = SNIPPETS[snippet]
        st.session_state["sbx-stdin"] = "Ada\n36" if snippet == "Read input" else ""
        st.session_state.pop("sbx-result", None)
    code = st.text_area("Code", key="sbx-code", height=320)
    stdin = st.text_area("Input for `input()` (one value per line)", key="sbx-stdin", height=80)
    if st.button("▶ Run code", type="primary"):
        with st.spinner("Running in the sandbox…"):
            st.session_state["sbx-result"] = run_code(code, stdin=stdin)
    if "sbx-result" in st.session_state:
        show_run(st.session_state["sbx-result"])
    with st.expander("🔒 How the sandbox keeps you safe"):
        st.markdown(
            "- Your code runs in a **separate Python process**, never inside this app.\n"
            "- It gets an **empty temporary folder**, deleted after each run.\n"
            "- Limits: ~10 s wall-clock, CPU time, memory and file-size caps.\n"
            "- Blocked: running programs, network access, reading/writing files outside the "
            "temporary folder, and Python internals that could bypass these rules.\n"
            "- See the README for the full security model and its limitations.")


# ---------------------------------------------------------------- review --
def page_review(learner: int) -> None:
    st.markdown("## 🔁 Review")
    st.markdown("Questions come back on a **spaced-repetition** schedule (SM-2): answer correctly "
                "and the gap grows (1 day → 6 days → ~2 weeks …); make a mistake and it returns "
                "tomorrow. Reviewing just before you'd forget is the most efficient way to learn.")
    tab_due, tab_drill, tab_sched = st.tabs(["📅 Due today", "🎯 Concept drill", "🗓️ Schedule"])
    with tab_due:
        due = store.due_items(learner)
        session = st.session_state.get("review-session")
        c1, c2 = st.columns([1, 3])
        if c1.button(f"Start review ({len(due)} due)", disabled=not due and not session):
            st.session_state["review-session"] = session = [d["item_id"] for d in due][:15]
            for k in [k for k in st.session_state if str(k).startswith("review-t")]:
                del st.session_state[k]
        if not session:
            if due:
                st.info(f"{len(due)} item(s) due. Press **Start review**.")
            else:
                st.success("Nothing is due right now. Answer more questions in 📚 Learn, or "
                           "use the Concept drill.")
        else:
            c2.caption(f"Session of {len(session)} item(s). Items you answer are rescheduled.")
            for n, item_id in enumerate(session, 1):
                try:
                    topic, item = get_item(item_id)
                except KeyError:
                    continue
                st.caption(f"From topic {topic.number}: {topic.title}")
                render_item(item, topic, store, learner, ctx="review", number=n)
    with tab_drill:
        scores = store.item_scores(learner)
        tags = all_tags()
        tag = st.selectbox("Concept", tags, index=tags.index("return-vs-print")
                           if "return-vs-print" in tags else 0, key="drill-tag")
        items = [(t, i) for t in TOPICS for i in t.items if tag in i.tags]
        items.sort(key=lambda ti: scores.get(ti[1].id, 0.0))
        st.caption(f"{len(items)} exercise(s) tagged `{tag}`, weakest first.")
        for n, (t, i) in enumerate(items, 1):
            render_item(i, t, store, learner, ctx="drill", number=n)
    with tab_sched:
        rows = store.upcoming_reviews(learner)
        if not rows:
            st.info("No review history yet.")
        else:
            df = pd.DataFrame(rows)
            now = datetime.now(timezone.utc)
            df["due_in_days"] = df["due_at"].map(
                lambda s: round((datetime.fromisoformat(s) - now).total_seconds() / 86400, 1))
            st.dataframe(df[["item_id", "topic_id", "due_in_days", "interval_days", "ease",
                             "lapses"]], hide_index=True)


# -------------------------------------------------------------- projects --
def page_projects(learner: int) -> None:
    st.markdown("## 🛠️ Data Science mini-projects")
    st.markdown("Realistic, multi-step projects using **pandas**, **matplotlib** and **SQLite**. "
                "Each step runs with the results of the previous steps already loaded.")
    ids = [p.id for p in PROJECTS]
    pid = st.radio("Project", ids, format_func=lambda i: next(p.title for p in PROJECTS if p.id == i),
                   horizontal=True, key="project-select")
    project = next(p for p in PROJECTS if p.id == pid)
    done = store.project_steps_done(learner, project.id)
    st.progress(len(done) / len(project.steps), text=f"{len(done)}/{len(project.steps)} steps complete")
    st.markdown(project.story)
    st.markdown(tags_html(project.skills), unsafe_allow_html=True)
    with st.expander("Peek at the raw data"):
        peek = {"p1": "print(open('coffee_sales.csv').read()[:900])",
                "p2": "import sqlite3\nc = sqlite3.connect('school.db')\nfor t in ['students', 'subjects', 'results']:\n    print(t, c.execute(f'SELECT * FROM {t} LIMIT 5').fetchall())",
                "p3": "print(open('weather_sales.csv').read()[:700])"}[project.id]
        if st.button("Show first rows", key=f"peek-{project.id}"):
            show_run(run_code(peek, setup=project.setup_code))
    for idx, step in enumerate(project.steps):
        key = f"proj-{project.id}-{idx}"
        with st.container(border=True):
            st.markdown(f"### {'✅' if idx in done else '⬜'} {step.title}")
            st.markdown(step.instructions)
            code = st.text_area("Code", value=step.starter, key=f"{key}-code",
                                height=max(160, 26 * (step.starter.count(chr(10)) + 3)),
                                label_visibility="collapsed")
            c1, c2, c3, c4 = st.columns(4)
            if c1.button("▶ Run", key=f"{key}-run"):
                st.session_state[f"{key}-res"] = ("run", run_code(
                    code, setup=project.setup_code, prelude=prelude_for(project, idx), timeout=20))
            if c2.button("✅ Check", key=f"{key}-check"):
                with st.spinner("Checking…"):
                    run = run_code(code, setup=project.setup_code,
                                   prelude=prelude_for(project, idx), checks=step.checks, timeout=20)
                fb = feedback_from_run(run, "✅ Step complete!")
                if fb.correct:
                    store.mark_project_step(learner, project.id, idx)
                st.session_state[f"{key}-res"] = ("check", fb)
            hk = f"{key}-hints"
            if c3.button("💡 Hint", key=f"{key}-hint",
                         disabled=st.session_state.get(hk, 0) >= len(step.hints)):
                st.session_state[hk] = st.session_state.get(hk, 0) + 1
            show_sol = c4.toggle("Solution", key=f"{key}-sol")
            for h in step.hints[:st.session_state.get(hk, 0)]:
                st.markdown(f"💡 *{h}*")
            res = st.session_state.get(f"{key}-res")
            if res:
                if res[0] == "run":
                    show_run(res[1])
                else:
                    show_feedback(res[1])
                    if res[1].run is not None and res[1].run.error:
                        show_run(res[1].run)
            if show_sol:
                st.code(step.solution, language="python")


# ----------------------------------------------------------------- about --
def page_about(learner: int) -> None:
    st.markdown("## ℹ️ About PyLearn")
    st.markdown("""
**PyLearn** is a self-paced course in ten topics, from your first `print()` to
SQL, pandas and matplotlib. Each topic has progressive lessons with editable,
runnable examples, four kinds of exercises (multiple choice with an explanation
for *every* wrong option, output prediction, debugging, coding), and a quiz.

**How progress works**
* Every answer is stored locally in an SQLite database (`~/.pylearn/progress.db`,
  or `$PYLEARN_DATA_DIR`).
* **Mastery** per topic = 20% lessons completed + 80% exercise score, where each
  exercise's score is a weighted average of your attempts (recent ones count more).
* **Spaced repetition** uses SM-2: each item has an ease factor and interval.
* **Recommendations** combine due reviews, weak topics, weak concepts (tags) and
  the next topic whose prerequisites you've met.

**Limitations** (see README for details)
* The sandbox is a defence-in-depth *local* sandbox (separate process, audit-hook
  policy, resource limits). It is suitable for a personal/classroom app on a trusted
  machine; for a public multi-user deployment run it inside a container/VM as well.
* Resource limits (CPU/memory) are only enforced on Linux/macOS.
* Code checks test behaviour on specific inputs; passing them doesn't prove code is
  correct in every case, and a determined learner can game them.
* Progress is per machine (no accounts or cloud sync).
""")
    if st.button("🗑️ Reset my progress", type="secondary"):
        st.session_state["confirm-reset"] = True
    if st.session_state.get("confirm-reset"):
        st.warning("This permanently deletes all answers, lessons and reviews for this profile.")
        if st.button("Yes, delete my progress"):
            store.reset(learner)
            st.session_state["confirm-reset"] = False
            st.success("Progress reset.")


def main() -> None:
    page, learner = sidebar()
    {
        "🏠 Dashboard": page_dashboard,
        "📚 Learn": page_learn,
        "🧪 Sandbox": page_sandbox,
        "🔁 Review": page_review,
        "🛠️ Projects": page_projects,
        "ℹ️ About": page_about,
    }[page](learner)


main()
