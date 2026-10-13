import pytest
from online_course.performance import AcademicPerformance


def test_performance_creation():
    perf = AcademicPerformance(1, 10, 20, 95.0, 90.0, 100.0)
    assert perf.performance_id == 1
    assert perf.student_id == 10
    assert perf.course_id == 20
    assert perf.homework_score == 95.0
    assert perf.exam_score == 90.0
    assert perf.attendance_rate == 100.0


def test_final_score_calculation():
    # 0.4 * 90 + 0.4 * 80 + 0.2 * 100 = 36 + 32 + 20 = 88.0
    perf = AcademicPerformance(1, 1, 1, homework_score=90.0, exam_score=80.0, attendance_rate=100.0)
    assert perf.calculate_final_score() == 88.0


def test_status_determination():
    # >= 90: Отлично
    p_exc = AcademicPerformance(1, 1, 1, 95.0, 95.0, 95.0)
    assert p_exc.get_status() == "Отлично"

    # >= 75: Хорошо (0.4*80 + 0.4*80 + 0.2*70 = 32 + 32 + 14 = 78.0)
    p_good = AcademicPerformance(2, 1, 1, 80.0, 80.0, 70.0)
    assert p_good.get_status() == "Хорошо"

    # >= 60: Удовлетворительно (0.4*60 + 0.4*65 + 0.2*60 = 24 + 26 + 12 = 62.0)
    p_sat = AcademicPerformance(3, 1, 1, 60.0, 65.0, 60.0)
    assert p_sat.get_status() == "Удовлетворительно"

    # < 60: Неудовлетворительно
    p_fail = AcademicPerformance(4, 1, 1, 50.0, 40.0, 50.0)
    assert p_fail.get_status() == "Неудовлетворительно"


def test_discount_tiers_and_bonus():
    # Отлично + 100% посещаемость: 25% + 5% = 30%
    p1 = AcademicPerformance(1, 1, 1, 95.0, 95.0, 100.0)
    assert p1.calculate_discount() == 30.0

    # Отлично + 90% посещаемость: 25% + 0% = 25%
    p2 = AcademicPerformance(2, 1, 1, 95.0, 95.0, 90.0)
    assert p2.calculate_discount() == 25.0

    # Хорошо + 100% посещаемость: 15% + 5% = 20%
    p3 = AcademicPerformance(3, 1, 1, 80.0, 80.0, 100.0)
    assert p3.calculate_discount() == 20.0

    # Удовлетворительно + 80% посещаемость: 5% + 0% = 5%
    p4 = AcademicPerformance(4, 1, 1, 60.0, 65.0, 80.0)
    assert p4.calculate_discount() == 5.0

    # Неудовлетворительно: 0%
    p5 = AcademicPerformance(5, 1, 1, 40.0, 40.0, 50.0)
    assert p5.calculate_discount() == 0.0


def test_update_scores():
    perf = AcademicPerformance(1, 1, 1, 50.0, 50.0, 50.0)
    assert perf.get_status() == "Неудовлетворительно"

    perf.update_scores(90.0, 95.0, 100.0)
    assert perf.calculate_final_score() == 94.0
    assert perf.get_status() == "Отлично"
    assert perf.calculate_discount() == 30.0


def test_invalid_score_boundaries():
    with pytest.raises(ValueError):
        AcademicPerformance(0, 1, 1, 50.0, 50.0, 50.0)

    with pytest.raises(ValueError):
        AcademicPerformance(1, 1, 1, -10.0, 50.0, 50.0)

    with pytest.raises(ValueError):
        AcademicPerformance(1, 1, 1, 50.0, 120.0, 50.0)

    with pytest.raises(ValueError):
        AcademicPerformance(1, 1, 1, 50.0, 50.0, -5.0)


def test_performance_dunder_methods():
    p1 = AcademicPerformance(1, 1, 2, 90.0, 90.0, 100.0)
    p2 = AcademicPerformance(1, 1, 2, 90.0, 90.0, 100.0)
    p3 = AcademicPerformance(2, 1, 2, 80.0, 80.0, 90.0)

    assert "Успеваемость" in str(p1)
    assert "AcademicPerformance(" in repr(p1)
    assert p1 == p2
    assert p1 != p3
