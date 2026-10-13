import pytest
from online_course.student import Student


def test_student_creation():
    student = Student(1, "Суворов Иван", "suvorov@example.com")
    assert student.student_id == 1
    assert student.full_name == "Суворов Иван"
    assert student.email == "suvorov@example.com"


def test_student_email_update():
    student = Student(1, "Суворов Иван", "old@example.com")
    student.update_email("new_email@study.ru")
    assert student.email == "new_email@study.ru"


def test_student_invalid_attributes():
    with pytest.raises(ValueError):
        Student(0, "Суворов Иван", "ivan@example.com")

    with pytest.raises(ValueError):
        Student(1, "   ", "ivan@example.com")

    with pytest.raises(ValueError):
        Student(1, "Суворов Иван", "invalid_email_without_at")

    with pytest.raises(ValueError):
        Student(1, "Суворов Иван", "invalid@no_dot_domain")


def test_student_dunder_methods():
    st1 = Student(1, "Суворов Иван", "ivan@example.com")
    st2 = Student(1, "Суворов Иван", "ivan@example.com")
    st3 = Student(2, "Петров Петр", "petr@example.com")

    assert str(st1) == "Студент Суворов Иван (ID: 1, email: ivan@example.com)"
    assert repr(st1) == "Student(student_id=1, full_name='Суворов Иван', email='ivan@example.com')"
    assert st1 == st2
    assert st1 != st3
