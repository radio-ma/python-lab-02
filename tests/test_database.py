import sqlite3
import pytest

from online_course.database import (
    initialize_database,
    create_standard_course,
    create_intensive_course,
    create_student,
    save_performance,
    load_courses,
    load_students,
    load_performances
)
from online_course.course import StandardCourse, IntensiveCourse


def test_create_and_load_courses(tmp_path):
    db_file = tmp_path / "test_courses.db"

    c1 = create_standard_course("Python Start", 15000.0, 30, has_certificate=True, db_path=db_file)
    c2 = create_intensive_course("ML Pro", 60000.0, 90, mentor_name="Куратор", projects_count=2, db_path=db_file)

    assert c1.course_id == 1
    assert c2.course_id == 2

    courses = load_courses(db_file)
    assert len(courses) == 2
    assert isinstance(courses[1], StandardCourse)
    assert isinstance(courses[2], IntensiveCourse)
    assert courses[1].title == "Python Start"
    assert courses[2].mentor_name == "Куратор"


def test_create_and_load_students(tmp_path):
    db_file = tmp_path / "test_courses.db"

    st1 = create_student("Суворов Иван", "ivan@study.ru", db_path=db_file)
    st2 = create_student("Смирнов Максим", "maksim@study.ru", db_path=db_file)

    assert st1.student_id == 1
    assert st2.student_id == 2

    students = load_students(db_file)
    assert len(students) == 2
    assert students[1].full_name == "Суворов Иван"
    assert students[2].email == "maksim@study.ru"


def test_save_and_load_performance(tmp_path):
    db_file = tmp_path / "test_courses.db"

    c = create_standard_course("Python Start", 20000.0, 30, db_path=db_file)
    st = create_student("Суворов Иван", "ivan@study.ru", db_path=db_file)

    # ДЗ=95, Экзамен=95, Посещаемость=100 -> Итог=96.0, Скидка=30%, Цена=14000.0
    perf = save_performance(st.student_id, c.course_id, 95.0, 95.0, 100.0, db_path=db_file)
    assert perf.performance_id == 1

    perfs = load_performances(db_file)
    assert len(perfs) == 1
    assert perfs[1].student_id == st.student_id
    assert perfs[1].course_id == c.course_id
    assert perfs[1].homework_score == 95.0
    assert perfs[1].calculate_final_score() == 96.0

    with sqlite3.connect(db_file) as conn:
        row = conn.execute("SELECT final_price, discount_percent FROM performances WHERE id = 1").fetchone()
        assert row[0] == 14000.0
        assert row[1] == 30.0


def test_update_existing_performance(tmp_path):
    db_file = tmp_path / "test_courses.db"

    c = create_standard_course("Python Start", 20000.0, 30, db_path=db_file)
    st = create_student("Суворов Иван", "ivan@study.ru", db_path=db_file)

    save_performance(st.student_id, c.course_id, 50.0, 50.0, 50.0, db_path=db_file)
    save_performance(st.student_id, c.course_id, 90.0, 90.0, 100.0, db_path=db_file)

    perfs = load_performances(db_file)
    assert len(perfs) == 1
    assert perfs[1].homework_score == 90.0
    assert perfs[1].calculate_final_score() == 92.0


def test_foreign_key_constraints(tmp_path):
    db_file = tmp_path / "test_courses.db"
    initialize_database(db_file)

    # Попытка добавить успеваемость несуществующего студента / курса
    with pytest.raises(ValueError):
        save_performance(999, 999, 90.0, 90.0, 100.0, db_path=db_file)
