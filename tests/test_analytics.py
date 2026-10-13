import pytest
from online_course.course import StandardCourse, IntensiveCourse
from online_course.student import Student
from online_course.performance import AcademicPerformance
from online_course.analytics import (
    get_student_statistics,
    rank_students,
    rank_courses,
    most_successful_student,
    most_popular_course
)


def test_student_statistics_full():
    st = Student(1, "Суворов Иван", "suvorov@example.com")
    c1 = StandardCourse(1, "Python", 20000.0, 40)
    c2 = IntensiveCourse(2, "Data Science", 50000.0, 60, mentor_name="Куратор")

    # c1: Отлично + 100% att -> скидка 30% (StandardCourse max 30%) -> цена 14000.0
    p1 = AcademicPerformance(1, 1, 1, 95.0, 95.0, 100.0)
    # c2: Хорошо + 90% att -> скидка 15% -> цена 50000 * 0.85 = 42500.0
    p2 = AcademicPerformance(2, 1, 2, 80.0, 80.0, 90.0)

    perfs = {1: p1, 2: p2}
    courses = {1: c1, 2: c2}

    stats = get_student_statistics(st, perfs, courses)

    assert stats["student_id"] == 1
    assert stats["enrolled_courses_count"] == 2
    assert stats["excellent_count"] == 1
    assert stats["good_count"] == 1
    assert stats["total_initial_cost"] == 70000.0
    assert stats["total_discounted_cost"] == 56500.0
    assert stats["total_savings"] == 13500.0


def test_student_statistics_empty():
    st = Student(1, "Суворов Иван", "suvorov@example.com")
    stats = get_student_statistics(st, {}, {})

    assert stats["enrolled_courses_count"] == 0
    assert stats["average_final_score"] == 0.0
    assert stats["total_savings"] == 0.0


def test_rank_students():
    st1 = Student(1, "Алексеев", "a@test.com")
    st2 = Student(2, "Борисов", "b@test.com")
    st3 = Student(3, "Суворов", "s@test.com")

    # st1 avg: 60.0, st2 avg: 95.0, st3: 85.0
    p1 = AcademicPerformance(1, 1, 1, 60.0, 60.0, 60.0)
    p2 = AcademicPerformance(2, 2, 1, 95.0, 95.0, 95.0)
    p3 = AcademicPerformance(3, 3, 1, 85.0, 85.0, 85.0)

    perfs = {1: p1, 2: p2, 3: p3}
    ranked = rank_students([st1, st2, st3], perfs)

    assert ranked == [st2, st3, st1]


def test_rank_courses_and_most_popular():
    c1 = StandardCourse(1, "Python", 20000.0, 40)
    c2 = StandardCourse(2, "Java", 22000.0, 45)
    c3 = StandardCourse(3, "Go", 25000.0, 50)

    # c1: 2 students, c2: 1 student, c3: 0 students
    p1 = AcademicPerformance(1, 10, 1, 80.0, 80.0, 80.0)
    p2 = AcademicPerformance(2, 11, 1, 90.0, 90.0, 90.0)
    p3 = AcademicPerformance(3, 10, 2, 70.0, 70.0, 70.0)

    perfs = {1: p1, 2: p2, 3: p3}
    courses = [c3, c2, c1]

    ranked = rank_courses(courses, perfs)
    assert ranked[0] == c1
    assert ranked[1] == c2
    assert ranked[2] == c3

    assert most_popular_course(courses, perfs) == c1


def test_most_successful_student():
    st1 = Student(1, "Студент 1", "s1@test.com")
    st2 = Student(2, "Студент 2", "s2@test.com")
    st3 = Student(3, "Студент 3", "s3@test.com")  # нет оценок

    p1 = AcademicPerformance(1, 1, 1, 70.0, 70.0, 70.0)
    p2 = AcademicPerformance(2, 2, 1, 95.0, 95.0, 95.0)

    best = most_successful_student([st1, st2, st3], {1: p1, 2: p2})
    assert best == st2


def test_analytics_invalid_student_type():
    with pytest.raises(TypeError):
        get_student_statistics("не студент", {}, {})
