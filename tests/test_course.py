import pytest
from online_course.course import Course, StandardCourse, IntensiveCourse


def test_abstract_course_cannot_be_instantiated():
    with pytest.raises(TypeError):
        Course(1, "Тестовый курс", 10000.0, 40)


def test_standard_course_creation():
    course = StandardCourse(1, "Python Базовый", 15000.0, 36, has_certificate=True, max_discount_percent=30.0)
    assert course.course_id == 1
    assert course.title == "Python Базовый"
    assert course.base_price == 15000.0
    assert course.hours == 36
    assert course.has_certificate is True
    assert course.max_discount_percent == 30.0


def test_standard_course_discount_calculation():
    course = StandardCourse(1, "Python Базовый", 20000.0, 40)
    # 20% скидка: 20000 * 0.8 = 16000.0
    final_price = course.calculate_final_price(20.0)
    assert final_price == 16000.0


def test_standard_course_max_discount_cap():
    course = StandardCourse(1, "Python Базовый", 20000.0, 40, max_discount_percent=30.0)
    # Запрошена скидка 50%, но лимит 30%: 20000 * 0.7 = 14000.0
    final_price = course.calculate_final_price(50.0)
    assert final_price == 14000.0


def test_intensive_course_creation():
    course = IntensiveCourse(2, "Data Science Прорыв", 45000.0, 80, mentor_name="Иванов А.А.", projects_count=3)
    assert course.course_id == 2
    assert course.title == "Data Science Прорыв"
    assert course.base_price == 45000.0
    assert course.mentor_name == "Иванов А.А."
    assert course.projects_count == 3
    assert course.max_discount_percent == 20.0


def test_intensive_course_discount_calculation():
    course = IntensiveCourse(2, "Data Science", 50000.0, 60, mentor_name="Петров В.В.", max_discount_percent=20.0)
    # 15% скидка: 50000 * 0.85 = 42500.0
    assert course.calculate_final_price(15.0) == 42500.0
    # 30% скидка ограничена 20%: 50000 * 0.8 = 40000.0
    assert course.calculate_final_price(30.0) == 40000.0


def test_invalid_course_attributes():
    with pytest.raises(ValueError):
        StandardCourse(-1, "Курс", 1000.0, 10)

    with pytest.raises(ValueError):
        StandardCourse(1, "   ", 1000.0, 10)

    with pytest.raises(ValueError):
        StandardCourse(1, "Курс", -500.0, 10)

    with pytest.raises(ValueError):
        StandardCourse(1, "Курс", 1000.0, 0)

    with pytest.raises(TypeError):
        StandardCourse(1, "Курс", 1000.0, 10, has_certificate="да")

    with pytest.raises(ValueError):
        IntensiveCourse(1, "Курс", 1000.0, 10, mentor_name="")

    with pytest.raises(ValueError):
        IntensiveCourse(1, "Курс", 1000.0, 10, mentor_name="Ментор", projects_count=-1)


def test_course_dunder_methods():
    c1 = StandardCourse(1, "Веб-разработка", 25000.0, 50)
    c2 = StandardCourse(1, "Веб-разработка", 25000.0, 50)
    c3 = StandardCourse(2, "Мобильная разработка", 30000.0, 60)

    assert str(c1).startswith("Стандартный курс 'Веб-разработка'")
    assert "StandardCourse(" in repr(c1)
    assert c1 == c2
    assert c1 != c3
