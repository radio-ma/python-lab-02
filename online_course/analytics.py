from typing import Dict, List, Optional
from .student import Student
from .course import Course
from .performance import AcademicPerformance


def get_student_statistics(
    student: Student,
    performances: Dict[int, AcademicPerformance],
    courses: Dict[int, Course]
) -> dict:
    """
    Расчёт комплексной академической и финансовой статистики для студента.
    """
    if not isinstance(student, Student):
        raise TypeError("Ожидается объект Student")

    student_perfs = [
        p for p in performances.values()
        if p.student_id == student.student_id
    ]

    enrolled_count = len(student_perfs)
    if enrolled_count == 0:
        return {
            "student_id": student.student_id,
            "full_name": student.full_name,
            "email": student.email,
            "enrolled_courses_count": 0,
            "average_final_score": 0.0,
            "excellent_count": 0,
            "good_count": 0,
            "satisfactory_count": 0,
            "failed_count": 0,
            "average_discount": 0.0,
            "total_initial_cost": 0.0,
            "total_discounted_cost": 0.0,
            "total_savings": 0.0
        }

    final_scores = [p.calculate_final_score() for p in student_perfs]
    avg_score = round(sum(final_scores) / enrolled_count, 2)

    statuses = [p.get_status() for p in student_perfs]
    discounts = [p.calculate_discount() for p in student_perfs]
    avg_discount = round(sum(discounts) / enrolled_count, 2)

    total_initial = 0.0
    total_discounted = 0.0

    for p in student_perfs:
        course = courses.get(p.course_id)
        if course is not None:
            total_initial += course.base_price
            discount = p.calculate_discount()
            total_discounted += course.calculate_final_price(discount)

    total_savings = round(total_initial - total_discounted, 2)

    return {
        "student_id": student.student_id,
        "full_name": student.full_name,
        "email": student.email,
        "enrolled_courses_count": enrolled_count,
        "average_final_score": avg_score,
        "excellent_count": statuses.count("Отлично"),
        "good_count": statuses.count("Хорошо"),
        "satisfactory_count": statuses.count("Удовлетворительно"),
        "failed_count": statuses.count("Неудовлетворительно"),
        "average_discount": avg_discount,
        "total_initial_cost": round(total_initial, 2),
        "total_discounted_cost": round(total_discounted, 2),
        "total_savings": total_savings
    }


def rank_students(
    students: List[Student],
    performances: Dict[int, AcademicPerformance]
) -> List[Student]:
    """Сортировка студентов по среднему итоговому баллу успеваемости (по убыванию)."""
    def _student_avg_score(st: Student) -> float:
        st_perfs = [p for p in performances.values() if p.student_id == st.student_id]
        if not st_perfs:
            return 0.0
        return sum(p.calculate_final_score() for p in st_perfs) / len(st_perfs)

    return sorted(students, key=_student_avg_score, reverse=True)


def rank_courses(
    courses: List[Course],
    performances: Dict[int, AcademicPerformance]
) -> List[Course]:
    """Сортировка курсов по количеству записанных студентов (по популярности)."""
    def _course_enrollments(c: Course) -> int:
        return sum(1 for p in performances.values() if p.course_id == c.course_id)

    return sorted(courses, key=_course_enrollments, reverse=True)


def most_successful_student(
    students: List[Student],
    performances: Dict[int, AcademicPerformance]
) -> Optional[Student]:
    """Поиск студента с наивысшим средним баллом среди имеющих оценки."""
    active_students = [
        st for st in students
        if any(p.student_id == st.student_id for p in performances.values())
    ]
    if not active_students:
        return None

    def _avg_score(st: Student) -> float:
        st_perfs = [p for p in performances.values() if p.student_id == st.student_id]
        return sum(p.calculate_final_score() for p in st_perfs) / len(st_perfs)

    return max(active_students, key=_avg_score)


def most_popular_course(
    courses: List[Course],
    performances: Dict[int, AcademicPerformance]
) -> Optional[Course]:
    """Поиск курса с наибольшим числом обучающихся студентов."""
    if not courses:
        return None

    def _enrollments(c: Course) -> int:
        return sum(1 for p in performances.values() if p.course_id == c.course_id)

    return max(courses, key=_enrollments)
