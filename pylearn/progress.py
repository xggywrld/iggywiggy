"""Progress tracking, mastery scores, spaced repetition and recommendations.

Everything is stored in a small SQLite database (``progress.db``) in the data
directory (``$PYLEARN_DATA_DIR`` or ``~/.pylearn``). Multiple learner profiles
are supported on one machine.

Spaced repetition uses the SM-2 algorithm (as used by Anki/SuperMemo):
each answered item gets an *ease factor* and an *interval* (days until it is
due again). Correct answers stretch the interval; mistakes reset it to 1 day.

Mastery of a topic (0-100) =
    20% lessons completed + 80% average item score,
where an item's score is an exponentially-weighted average of its attempts
(recent attempts count more), and unattempted items score 0.
"""

from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable, Optional

SCHEMA = """
CREATE TABLE IF NOT EXISTS learners (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS attempts (
    id INTEGER PRIMARY KEY,
    learner_id INTEGER NOT NULL REFERENCES learners(id),
    item_id TEXT NOT NULL,
    topic_id TEXT NOT NULL,
    kind TEXT NOT NULL,
    correct INTEGER NOT NULL,
    source TEXT NOT NULL DEFAULT 'practice',
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_attempts_learner ON attempts(learner_id, item_id);
CREATE TABLE IF NOT EXISTS reviews (
    learner_id INTEGER NOT NULL REFERENCES learners(id),
    item_id TEXT NOT NULL,
    topic_id TEXT NOT NULL,
    ease REAL NOT NULL DEFAULT 2.5,
    interval_days REAL NOT NULL DEFAULT 0,
    repetitions INTEGER NOT NULL DEFAULT 0,
    due_at TEXT NOT NULL,
    last_reviewed TEXT NOT NULL,
    lapses INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (learner_id, item_id)
);
CREATE TABLE IF NOT EXISTS lessons_done (
    learner_id INTEGER NOT NULL REFERENCES learners(id),
    lesson_id TEXT NOT NULL,
    topic_id TEXT NOT NULL,
    created_at TEXT NOT NULL,
    PRIMARY KEY (learner_id, lesson_id)
);
CREATE TABLE IF NOT EXISTS projects_done (
    learner_id INTEGER NOT NULL REFERENCES learners(id),
    project_id TEXT NOT NULL,
    step INTEGER NOT NULL,
    created_at TEXT NOT NULL,
    PRIMARY KEY (learner_id, project_id, step)
);
"""

EWMA_ALPHA = 0.5  # weight of the newest attempt in an item's score
MAX_INTERVAL_DAYS = 365.0  # never schedule a review more than a year ahead
LESSON_WEIGHT = 0.2


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat(timespec="seconds")


def _parse(ts: str) -> datetime:
    return datetime.fromisoformat(ts)


def default_db_path() -> Path:
    base = Path(os.environ.get("PYLEARN_DATA_DIR", Path.home() / ".pylearn"))
    base.mkdir(parents=True, exist_ok=True)
    return base / "progress.db"


# --------------------------------------------------------------- SM-2 -------
@dataclass
class ReviewState:
    ease: float = 2.5
    interval_days: float = 0.0
    repetitions: int = 0
    lapses: int = 0


def sm2(state: ReviewState, quality: int) -> ReviewState:
    """Apply one SM-2 review. ``quality`` is 0 (blackout) .. 5 (perfect)."""
    if not 0 <= quality <= 5:
        raise ValueError("quality must be between 0 and 5")
    ease = state.ease + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    ease = max(1.3, ease)
    if quality < 3:
        return ReviewState(ease=ease, interval_days=1.0, repetitions=0,
                           lapses=state.lapses + 1)
    reps = state.repetitions + 1
    if reps == 1:
        interval = 1.0
    elif reps == 2:
        interval = 6.0
    else:
        interval = round(min(state.interval_days, MAX_INTERVAL_DAYS) * ease, 1)
    interval = min(interval, MAX_INTERVAL_DAYS)
    return ReviewState(ease=ease, interval_days=interval, repetitions=reps,
                       lapses=state.lapses)


def quality_from(correct: bool, hints_used: int = 0, attempts_before: int = 0) -> int:
    """Map an answer to an SM-2 quality score."""
    if not correct:
        return 1
    if hints_used or attempts_before:
        return 3
    return 5


def mastery_level(score: float) -> str:
    if score <= 0:
        return "Not started"
    if score < 40:
        return "Learning"
    if score < 70:
        return "Developing"
    if score < 90:
        return "Proficient"
    return "Mastered"


# -------------------------------------------------------------- store -------
@dataclass
class TopicMastery:
    topic_id: str
    score: float  # 0..100
    level: str
    items_attempted: int
    items_total: int
    lessons_done: int
    lessons_total: int
    accuracy: Optional[float]  # share of all attempts that were correct


@dataclass
class Recommendation:
    kind: str  # "review", "weak-topic", "next-topic", "weak-tag", "project"
    title: str
    reason: str
    topic_id: Optional[str] = None


class ProgressStore:
    def __init__(self, path: str | Path | None = None):
        self.path = str(path or default_db_path())
        with self._conn() as c:
            c.executescript(SCHEMA)

    @contextmanager
    def _conn(self):
        conn = sqlite3.connect(self.path, timeout=10)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    # --- learners ---------------------------------------------------------
    def learner_id(self, name: str) -> int:
        name = (name or "").strip() or "Learner"
        with self._conn() as c:
            c.execute("INSERT OR IGNORE INTO learners(name, created_at) VALUES (?, ?)",
                      (name, _iso(_now())))
            return c.execute("SELECT id FROM learners WHERE name = ?", (name,)).fetchone()[0]

    def learners(self) -> list[str]:
        with self._conn() as c:
            return [r[0] for r in c.execute("SELECT name FROM learners ORDER BY name")]

    def reset(self, learner: int) -> None:
        with self._conn() as c:
            for table in ("attempts", "reviews", "lessons_done", "projects_done"):
                c.execute(f"DELETE FROM {table} WHERE learner_id = ?", (learner,))

    # --- recording --------------------------------------------------------
    def record_attempt(self, learner: int, item_id: str, topic_id: str, kind: str,
                       correct: bool, *, source: str = "practice", hints_used: int = 0,
                       when: Optional[datetime] = None) -> ReviewState:
        when = when or _now()
        with self._conn() as c:
            c.execute(
                "INSERT INTO attempts(learner_id,item_id,topic_id,kind,correct,source,created_at)"
                " VALUES (?,?,?,?,?,?,?)",
                (learner, item_id, topic_id, kind, int(bool(correct)), source, _iso(when)))
            row = c.execute("SELECT * FROM reviews WHERE learner_id=? AND item_id=?",
                            (learner, item_id)).fetchone()
            # min() also repairs oversized intervals saved by older versions.
            state = ReviewState() if row is None else ReviewState(
                row["ease"], min(row["interval_days"], MAX_INTERVAL_DAYS),
                row["repetitions"], row["lapses"])
            # Answering correctly again *before* the item is due (e.g. resubmitting a
            # quiz) isn't a spaced-repetition review, so it must not stretch the
            # schedule. A wrong answer, however, always resets it.
            if row is not None and correct and _iso(when) < row["due_at"] \
                    and row["interval_days"] <= MAX_INTERVAL_DAYS:
                return state
            # Retrying immediately after a mistake shouldn't count as a perfect recall.
            recent_fail = False
            if row is not None and correct:
                last = c.execute(
                    "SELECT correct FROM attempts WHERE learner_id=? AND item_id=? "
                    "ORDER BY id DESC LIMIT 1 OFFSET 1", (learner, item_id)).fetchone()
                recent_fail = last is not None and not last[0]
            q = quality_from(correct, hints_used, 1 if recent_fail else 0)
            if row is None and not correct:
                q = 1
            new = sm2(state, q)
            due = when + timedelta(days=new.interval_days)
            c.execute(
                "INSERT INTO reviews(learner_id,item_id,topic_id,ease,interval_days,"
                "repetitions,due_at,last_reviewed,lapses) VALUES (?,?,?,?,?,?,?,?,?) "
                "ON CONFLICT(learner_id,item_id) DO UPDATE SET ease=excluded.ease, "
                "interval_days=excluded.interval_days, repetitions=excluded.repetitions, "
                "due_at=excluded.due_at, last_reviewed=excluded.last_reviewed, "
                "lapses=excluded.lapses",
                (learner, item_id, topic_id, new.ease, new.interval_days, new.repetitions,
                 _iso(due), _iso(when), new.lapses))
        return new

    def mark_lesson(self, learner: int, lesson_id: str, topic_id: str) -> None:
        with self._conn() as c:
            c.execute("INSERT OR IGNORE INTO lessons_done VALUES (?,?,?,?)",
                      (learner, lesson_id, topic_id, _iso(_now())))

    def lessons_done(self, learner: int) -> set[str]:
        with self._conn() as c:
            return {r[0] for r in c.execute(
                "SELECT lesson_id FROM lessons_done WHERE learner_id=?", (learner,))}

    def mark_project_step(self, learner: int, project_id: str, step: int) -> None:
        with self._conn() as c:
            c.execute("INSERT OR IGNORE INTO projects_done VALUES (?,?,?,?)",
                      (learner, project_id, step, _iso(_now())))

    def project_steps_done(self, learner: int, project_id: str) -> set[int]:
        with self._conn() as c:
            return {r[0] for r in c.execute(
                "SELECT step FROM projects_done WHERE learner_id=? AND project_id=?",
                (learner, project_id))}

    # --- queries ----------------------------------------------------------
    def item_scores(self, learner: int) -> dict[str, float]:
        """EWMA score (0..1) of every attempted item."""
        scores: dict[str, float] = {}
        with self._conn() as c:
            rows = c.execute("SELECT item_id, correct FROM attempts WHERE learner_id=? "
                             "ORDER BY id", (learner,))
            for item_id, correct in rows:
                prev = scores.get(item_id)
                scores[item_id] = float(correct) if prev is None else (
                    EWMA_ALPHA * correct + (1 - EWMA_ALPHA) * prev)
        return scores

    def attempt_stats(self, learner: int) -> dict:
        with self._conn() as c:
            total, right = c.execute(
                "SELECT COUNT(*), COALESCE(SUM(correct),0) FROM attempts WHERE learner_id=?",
                (learner,)).fetchone()
            days = [r[0] for r in c.execute(
                "SELECT DISTINCT substr(created_at,1,10) FROM attempts WHERE learner_id=? "
                "ORDER BY 1 DESC", (learner,))]
        streak = 0
        day = _now().date()
        dayset = set(days)
        if day.isoformat() not in dayset:
            day -= timedelta(days=1)
        while day.isoformat() in dayset:
            streak += 1
            day -= timedelta(days=1)
        return {"attempts": total, "correct": right, "streak_days": streak,
                "accuracy": (right / total) if total else None}

    def history(self, learner: int, limit: int = 200) -> list[dict]:
        with self._conn() as c:
            return [dict(r) for r in c.execute(
                "SELECT item_id, topic_id, kind, correct, source, created_at FROM attempts "
                "WHERE learner_id=? ORDER BY id DESC LIMIT ?", (learner, limit))]

    def due_items(self, learner: int, now: Optional[datetime] = None) -> list[dict]:
        now = now or _now()
        with self._conn() as c:
            rows = c.execute("SELECT * FROM reviews WHERE learner_id=? AND due_at <= ? "
                             "ORDER BY due_at", (learner, _iso(now))).fetchall()
        return [dict(r) for r in rows]

    def upcoming_reviews(self, learner: int) -> list[dict]:
        with self._conn() as c:
            return [dict(r) for r in c.execute(
                "SELECT item_id, topic_id, due_at, interval_days, ease, lapses FROM reviews "
                "WHERE learner_id=? ORDER BY due_at", (learner,))]

    def topic_mastery(self, learner: int, topic_id: str, item_ids: Iterable[str],
                      lesson_ids: Iterable[str]) -> TopicMastery:
        item_ids, lesson_ids = list(item_ids), list(lesson_ids)
        scores = self.item_scores(learner)
        done = self.lessons_done(learner)
        attempted = [i for i in item_ids if i in scores]
        item_part = (sum(scores.get(i, 0.0) for i in item_ids) / len(item_ids)) if item_ids else 0
        lesson_part = (sum(1 for l in lesson_ids if l in done) / len(lesson_ids)) if lesson_ids else 0
        score = round(100 * (LESSON_WEIGHT * lesson_part + (1 - LESSON_WEIGHT) * item_part), 1)
        with self._conn() as c:
            total, right = c.execute(
                "SELECT COUNT(*), COALESCE(SUM(correct),0) FROM attempts "
                "WHERE learner_id=? AND topic_id=?", (learner, topic_id)).fetchone()
        return TopicMastery(topic_id, score, mastery_level(score), len(attempted),
                            len(item_ids), sum(1 for l in lesson_ids if l in done),
                            len(lesson_ids), (right / total) if total else None)


def tag_accuracy(store: ProgressStore, learner: int, item_tags: dict[str, tuple[str, ...]]
                 ) -> dict[str, tuple[float, int]]:
    """Per-concept-tag (accuracy, number of attempts) from the attempt log."""
    totals: dict[str, list[int]] = {}
    with store._conn() as c:
        for item_id, correct in c.execute(
                "SELECT item_id, correct FROM attempts WHERE learner_id=?", (learner,)):
            for tag in item_tags.get(item_id, ()):
                t = totals.setdefault(tag, [0, 0])
                t[0] += correct
                t[1] += 1
    return {tag: (r / n, n) for tag, (r, n) in totals.items()}


def recommend(store: ProgressStore, learner: int, topics, max_items: int = 5
              ) -> list[Recommendation]:
    """Build a prioritised list of what to study next.

    ``topics`` is the ordered list of :class:`~pylearn.content.models.Topic`.
    """
    recs: list[Recommendation] = []
    due = store.due_items(learner)
    if due:
        by_topic: dict[str, int] = {}
        for d in due:
            by_topic[d["topic_id"]] = by_topic.get(d["topic_id"], 0) + 1
        recs.append(Recommendation(
            "review", f"Review {len(due)} item(s) that are due",
            "Spaced repetition: these questions are scheduled for today, just before "
            "you'd be likely to forget them. Topics: "
            + ", ".join(f"{t} ({n})" for t, n in by_topic.items()) + "."))

    masteries = {t.id: store.topic_mastery(learner, t.id, [i.id for i in t.items],
                                           [l.id for l in t.lessons]) for t in topics}

    # Weak topics: started, but low score or low accuracy.
    weak = sorted((m for m in masteries.values()
                   if m.items_attempted and (m.score < 60 or (m.accuracy or 0) < 0.6)),
                  key=lambda m: m.score)
    titles = {t.id: t.title for t in topics}
    for m in weak[:2]:
        acc = f"{m.accuracy:.0%}" if m.accuracy is not None else "n/a"
        recs.append(Recommendation(
            "weak-topic", f"Strengthen “{titles[m.topic_id]}”",
            f"Mastery {m.score:.0f}/100, accuracy {acc}. Re-read the lesson notes and "
            "retry the exercises you got wrong.", m.topic_id))

    # Weak concepts across topics.
    item_tags = {i.id: i.tags for t in topics for i in t.items}
    tags = tag_accuracy(store, learner, item_tags)
    weak_tags = sorted(((acc, n, tag) for tag, (acc, n) in tags.items() if n >= 2 and acc < 0.6))
    if weak_tags:
        recs.append(Recommendation(
            "weak-tag", "Concepts to revise: " + ", ".join(f"`{t}`" for _, _, t in weak_tags[:4]),
            "You've answered questions on these concepts several times with under 60% "
            "accuracy. Use the Review page's concept filter to practise them."))

    # Next topic: first topic whose prerequisites are at least Developing.
    for t in topics:
        m = masteries[t.id]
        if m.score >= 70:
            continue
        prereq_ok = all(masteries[p].score >= 40 for p in t.prerequisites if p in masteries)
        if prereq_ok:
            verb = "Continue" if m.score > 0 else "Start"
            recs.append(Recommendation(
                "next-topic", f"{verb} topic {t.number}: {t.title}",
                f"Current mastery {m.score:.0f}/100. Its prerequisites are in place, so "
                "it's the best next step on the learning path.", t.id))
            break
    if all(m.score >= 70 for m in masteries.values()):
        recs.append(Recommendation(
            "project", "Try a Data Science mini-project",
            "You're proficient across the course — apply it to a realistic dataset."))
    return recs[:max_items]
