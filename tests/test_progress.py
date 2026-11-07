from datetime import datetime, timedelta, timezone

import pytest

from pylearn.content import TOPICS
from pylearn.progress import (ProgressStore, ReviewState, mastery_level, quality_from,
                              recommend, sm2, tag_accuracy)


@pytest.fixture
def store(tmp_path):
    return ProgressStore(tmp_path / "p.db")


def test_sm2_intervals_grow_and_reset():
    s = ReviewState()
    s = sm2(s, 5); assert s.interval_days == 1 and s.repetitions == 1
    s = sm2(s, 5); assert s.interval_days == 6
    s = sm2(s, 5); assert s.interval_days == pytest.approx(6 * s.ease, abs=0.1)
    assert s.ease > 2.5
    failed = sm2(s, 1)
    assert failed.interval_days == 1 and failed.repetitions == 0 and failed.lapses == 1
    assert failed.ease < s.ease


def test_sm2_ease_floor_and_validation():
    s = ReviewState()
    for _ in range(20):
        s = sm2(s, 0)
    assert s.ease == 1.3
    with pytest.raises(ValueError):
        sm2(s, 6)


def test_quality_mapping():
    assert quality_from(True) == 5
    assert quality_from(True, hints_used=1) == 3
    assert quality_from(False) == 1


def test_mastery_levels():
    assert mastery_level(0) == "Not started"
    assert mastery_level(30) == "Learning"
    assert mastery_level(65) == "Developing"
    assert mastery_level(85) == "Proficient"
    assert mastery_level(95) == "Mastered"


def test_learners_are_separate(store):
    a, b = store.learner_id("A"), store.learner_id("B")
    assert a != b and store.learner_id("A") == a
    store.record_attempt(a, "t01.x", "t01", "mcq", True)
    assert store.item_scores(b) == {}
    assert set(store.learners()) == {"A", "B"}


def test_item_score_is_recency_weighted(store):
    l = store.learner_id("x")
    store.record_attempt(l, "i", "t01", "mcq", False)
    store.record_attempt(l, "i", "t01", "mcq", True)
    assert store.item_scores(l)["i"] == 0.5
    store.record_attempt(l, "i", "t01", "mcq", True)
    assert store.item_scores(l)["i"] == 0.75


def test_review_scheduling_and_due(store):
    l = store.learner_id("x")
    t0 = datetime(2026, 1, 1, tzinfo=timezone.utc)
    store.record_attempt(l, "good", "t01", "mcq", True, when=t0)
    store.record_attempt(l, "bad", "t01", "mcq", False, when=t0)
    assert store.due_items(l, now=t0) == []
    due = {d["item_id"] for d in store.due_items(l, now=t0 + timedelta(days=1, minutes=1))}
    assert due == {"good", "bad"}
    # Second correct answer pushes 'good' 6 days out.
    store.record_attempt(l, "good", "t01", "mcq", True, when=t0 + timedelta(days=1))
    due = {d["item_id"] for d in store.due_items(l, now=t0 + timedelta(days=3))}
    assert due == {"bad"}


def test_retry_after_mistake_is_not_perfect_recall(store):
    l = store.learner_id("x")
    store.record_attempt(l, "i", "t01", "code", False)
    state = store.record_attempt(l, "i", "t01", "code", True)
    assert state.interval_days == 1  # quality 3, not a big jump


def test_topic_mastery(store):
    l = store.learner_id("x")
    topic = TOPICS[0]
    items = [i.id for i in topic.items]
    lessons = [x.id for x in topic.lessons]
    m = store.topic_mastery(l, topic.id, items, lessons)
    assert m.score == 0 and m.level == "Not started"
    for lid in lessons:
        store.mark_lesson(l, lid, topic.id)
    for iid in items:
        store.record_attempt(l, iid, topic.id, "mcq", True)
    m = store.topic_mastery(l, topic.id, items, lessons)
    assert m.score == 100 and m.level == "Mastered" and m.accuracy == 1.0
    store.record_attempt(l, items[0], topic.id, "mcq", False)
    m2 = store.topic_mastery(l, topic.id, items, lessons)
    assert m2.score < 100


def test_recommendations(store):
    l = store.learner_id("x")
    recs = recommend(store, l, TOPICS)
    assert recs[0].kind == "next-topic" and recs[0].topic_id == "t01"
    t = TOPICS[0]
    for item in t.items[:4]:
        store.record_attempt(l, item.id, t.id, item.kind, False,
                             when=datetime.now(timezone.utc) - timedelta(days=2))
    recs = recommend(store, l, TOPICS)
    kinds = [r.kind for r in recs]
    assert "review" in kinds and "weak-topic" in kinds
    assert any(r.kind == "weak-tag" for r in recs)


def test_tag_accuracy(store):
    l = store.learner_id("x")
    store.record_attempt(l, "a", "t", "mcq", True)
    store.record_attempt(l, "b", "t", "mcq", False)
    acc = tag_accuracy(store, l, {"a": ("loops",), "b": ("loops", "dicts")})
    assert acc["loops"] == (0.5, 2) and acc["dicts"] == (0.0, 1)


def test_streak_and_reset(store):
    l = store.learner_id("x")
    now = datetime.now(timezone.utc)
    for d in range(3):
        store.record_attempt(l, f"i{d}", "t01", "mcq", True, when=now - timedelta(days=d))
    assert store.attempt_stats(l)["streak_days"] == 3
    store.mark_project_step(l, "p1", 0)
    assert store.project_steps_done(l, "p1") == {0}
    store.reset(l)
    assert store.attempt_stats(l)["attempts"] == 0
    assert store.project_steps_done(l, "p1") == set()


def test_repeated_correct_answers_never_overflow(store):
    """Regression: resubmitting a quiz many times crashed with OverflowError."""
    l = store.learner_id("x")
    for _ in range(300):
        state = store.record_attempt(l, "q", "t01", "mcq", True, source="quiz")
    assert state.interval_days <= 365


def test_early_correct_review_does_not_stretch_schedule(store):
    l = store.learner_id("x")
    t0 = datetime(2026, 1, 1, tzinfo=timezone.utc)
    first = store.record_attempt(l, "q", "t01", "mcq", True, when=t0)
    again = store.record_attempt(l, "q", "t01", "mcq", True, when=t0 + timedelta(minutes=5))
    assert again.interval_days == first.interval_days == 1
    # Once it is actually due, a correct answer advances it (1 -> 6 days).
    due = store.record_attempt(l, "q", "t01", "mcq", True, when=t0 + timedelta(days=1, hours=1))
    assert due.interval_days == 6


def test_early_wrong_answer_still_resets(store):
    l = store.learner_id("x")
    t0 = datetime(2026, 1, 1, tzinfo=timezone.utc)
    store.record_attempt(l, "q", "t01", "mcq", True, when=t0)
    store.record_attempt(l, "q", "t01", "mcq", True, when=t0 + timedelta(days=2))
    wrong = store.record_attempt(l, "q", "t01", "mcq", False, when=t0 + timedelta(days=3))
    assert wrong.interval_days == 1 and wrong.lapses == 1


def test_corrupt_huge_interval_in_old_database_is_repaired(store):
    l = store.learner_id("x")
    store.record_attempt(l, "q", "t01", "mcq", True)
    with store._conn() as c:
        c.execute("UPDATE reviews SET interval_days = 1e9, due_at = '2026-01-01T00:00:00+00:00'")
    state = store.record_attempt(l, "q", "t01", "mcq", True)
    assert state.interval_days <= 365
