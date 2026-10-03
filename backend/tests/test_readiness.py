from datetime import date, timedelta

from services.readiness import exam_readiness


def test_low_progress_near_exam_is_not_ready():
    today = date.today()
    exam = today + timedelta(days=5)
    topics = [
        {"progress_pct": 70, "revision_count": 1},
        {"progress_pct": 55, "revision_count": 1},
        {"progress_pct": 18, "revision_count": 0},
        {"progress_pct": 40, "revision_count": 0},
    ]
    score = exam_readiness(topics, exam.isoformat(), today)
    assert 20 <= score <= 55


def test_completing_topics_raises_readiness():
    today = date.today()
    exam = today + timedelta(days=5)
    before = exam_readiness(
        [
            {"progress_pct": 18, "revision_count": 0},
            {"progress_pct": 40, "revision_count": 0},
        ],
        exam.isoformat(),
        today,
    )
    after = exam_readiness(
        [
            {"progress_pct": 70, "revision_count": 2},
            {"progress_pct": 80, "revision_count": 2},
        ],
        exam.isoformat(),
        today,
    )
    assert after > before
