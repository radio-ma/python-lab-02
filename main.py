import sqlite3
from typing import Dict

from online_course.course import Course, StandardCourse, IntensiveCourse
from online_course.student import Student
from online_course.performance import AcademicPerformance
from online_course.analytics import (
    get_student_statistics,
    rank_students,
    rank_courses,
    most_successful_student,
    most_popular_course
)
from online_course.report import export_report, export_excel
from online_course.database import (
    create_standard_course,
    create_intensive_course,
    create_student,
    save_performance,
    load_courses,
    load_students,
    load_performances
)


def read_positive_int(message: str) -> int:
    while True:
        try:
            value = int(input(message))
            if value <= 0:
                print("Введите положительное число.")
                continue
            return value
        except ValueError:
            print("Ошибка: необходимо ввести целое число")


def read_float(message: str, min_val: float = 0.0, max_val: float = float("inf")) -> float:
    while True:
        try:
            value = float(input(message))
            if not (min_val <= value <= max_val):
                print(f"Ошибка: число должно быть в диапазоне от {min_val} до {max_val}.")
                continue
            return value
        except ValueError:
            print("Ошибка: необходимо ввести число")


def add_standard_course_action(courses: Dict[int, Course]):
    print("\n--- Новый стандартный курс ---")
    title = input("Название: ").strip()
    price = read_float("Базовая цена (руб.): ", min_val=0.0)
    hours = read_positive_int("Количество академических часов: ")
    cert_input = input("Выдавать сертификат? (да/нет, по умолчанию да): ").strip().lower()
    has_cert = False if cert_input in ("нет", "n", "no", "0") else True

    course = create_standard_course(title, price, hours, has_certificate=has_cert)
    courses[course.course_id] = course
    print(f"Курс успешно добавлен (ID: {course.course_id})")


def add_intensive_course_action(courses: Dict[int, Course]):
    print("\n--- Новый интенсивный курс ---")
    title = input("Название: ").strip()
    price = read_float("Базовая цена (руб.): ", min_val=0.0)
    hours = read_positive_int("Количество академических часов: ")
    mentor = input("Имя ментора: ").strip()
    projects = int(read_float("Количество проектов: ", min_val=0.0))

    course = create_intensive_course(title, price, hours, mentor_name=mentor, projects_count=projects)
    courses[course.course_id] = course
    print(f"Интенсивный курс успешно добавлен (ID: {course.course_id})")


def add_student_action(students: Dict[int, Student]):
    print("\n--- Регистрация студента ---")
    name = input("Имя: ").strip()
    email = input("Email: ").strip()

    student = create_student(name, email)
    students[student.student_id] = student
    print(f"Студент зарегистрирован (ID: {student.student_id})")


def record_performance_action(
    students: Dict[int, Student],
    courses: Dict[int, Course],
    performances: Dict[int, AcademicPerformance]
):
    if not students or not courses:
        print("Сначала добавьте курсы и зарегистрируйте студентов")
        return

    print("\n--- Успеваемость студента ---")
    print("Студенты:")
    for st in students.values():
        print(f"{st.student_id}: {st.full_name}")

    st_id = read_positive_int("ID студента: ")
    student = students.get(st_id)
    if student is None:
        print("Студент не найден")
        return

    print("\nКурсы:")
    for c in courses.values():
        print(f"{c.course_id}: {c.title} ({c.base_price:.2f} руб.)")

    c_id = read_positive_int("ID курса: ")
    course = courses.get(c_id)
    if course is None:
        print("Курс не найден")
        return

    hw = read_float("Балл за домашние задания (0..100): ", 0.0, 100.0)
    exam = read_float("Балл за экзамен (0..100): ", 0.0, 100.0)
    att = read_float("Процент посещаемости (0..100): ", 0.0, 100.0)

    perf = save_performance(st_id, c_id, hw, exam, att)
    performances[perf.performance_id] = perf

    final_score = perf.calculate_final_score()
    status = perf.get_status()
    discount = perf.calculate_discount()
    final_price = course.calculate_final_price(discount)

    print("\nУспеваемость успешно зафиксирована:")
    print(f"Итоговый балл: {final_score:.2f} ({status})")
    print(f"Скидка на курс: {discount:.1f}%")
    print(f"Финальная стоимость: {final_price:.2f} руб. (базовая: {course.base_price:.2f} руб.)")


def show_catalog_and_ranking(courses: Dict[int, Course], performances: Dict[int, AcademicPerformance]):
    if not courses:
        print("Каталог пока пуст")
        return

    print("\n--- Рейтинг курсов по популярности ---")
    ranked = rank_courses(list(courses.values()), performances)
    for c in ranked:
        enrolled = sum(1 for p in performances.values() if p.course_id == c.course_id)
        print(f"ID: {c.course_id} | {c.title} | Учащихся: {enrolled} | Базовая цена: {c.base_price:.2f} руб.")


def show_student_statistics_action(
    students: Dict[int, Student],
    courses: Dict[int, Course],
    performances: Dict[int, AcademicPerformance]
):
    if not students:
        print("Студенты пока не зарегистрированы")
        return

    print("\n--- Статистика студента ---")
    for st in students.values():
        print(f"{st.student_id}: {st.full_name}")

    st_id = read_positive_int("ID студента: ")
    student = students.get(st_id)
    if student is None:
        print("Студент не найден")
        return

    stats = get_student_statistics(student, performances, courses)
    print(f"\nСтатистика для {stats['full_name']} (ID: {stats['student_id']}):")
    print(f"Email: {stats['email']}")
    print(f"Изучаемых курсов: {stats['enrolled_courses_count']}")
    print(f"Средний итоговый балл: {stats['average_final_score']}")
    print(f"Оценок 'Отлично': {stats['excellent_count']}")
    print(f"Оценок 'Хорошо': {stats['good_count']}")
    print(f"Оценок 'Удовлетворительно': {stats['satisfactory_count']}")
    print(f"Неудовлетворительно: {stats['failed_count']}")
    print(f"Средняя скидка: {stats['average_discount']}%")
    print(f"Стоимость курсов без скидок: {stats['total_initial_cost']:.2f} руб.")
    print(f"Итоговая стоимость со скидками: {stats['total_discounted_cost']:.2f} руб.")
    print(f"Суммарная экономия студента: {stats['total_savings']:.2f} руб.")


def show_top_performers(
    students: Dict[int, Student],
    courses: Dict[int, Course],
    performances: Dict[int, AcademicPerformance]
):
    if not students and not courses:
        print("Данные пока отсутствуют")
        return

    top_st = most_successful_student(list(students.values()), performances)
    pop_course = most_popular_course(list(courses.values()), performances)

    print("\n--- Самые успешные курсы и студенты ---")
    if top_st:
        stats = get_student_statistics(top_st, performances, courses)
        print(f"Лучший студент: {top_st.full_name} (средний балл: {stats['average_final_score']})")
    else:
        print("Лучший студент: пока нет данных об оценках")

    if pop_course:
        enrolled = sum(1 for p in performances.values() if p.course_id == pop_course.course_id)
        print(f"Самый популярный курс: {pop_course.title} (записано студентов: {enrolled})")
    else:
        print("Курсов пока нет")


def main():
    courses = load_courses()
    students = load_students()
    performances = load_performances()

    while True:
        print("\n========== ОНЛАЙН-КУРСЫ ==========")
        print("1. Добавить стандартный курс")
        print("2. Добавить интенсивный курс")
        print("3. Зарегистрировать студента")
        print("4. Внести успеваемость студента")
        print("5. Посмотреть каталог и рейтинг")
        print("6. Статистика студента")
        print("7. Самые популярные курсы и студенты")
        print("8. Сохранить отчёт в Word")
        print("9. Сохранить отчёт в Excel")
        print("0. Выход")

        choice = input("\nВыберите действие: ").strip()

        try:
            if choice == "1":
                add_standard_course_action(courses)
            elif choice == "2":
                add_intensive_course_action(courses)
            elif choice == "3":
                add_student_action(students)
            elif choice == "4":
                record_performance_action(students, courses, performances)
            elif choice == "5":
                show_catalog_and_ranking(courses, performances)
            elif choice == "6":
                show_student_statistics_action(students, courses, performances)
            elif choice == "7":
                show_top_performers(students, courses, performances)
            elif choice == "8":
                file_path = export_report(students, courses, performances)
                print(f"Отчёт успешно сохранён: {file_path}")
            elif choice == "9":
                file_path = export_excel(students, courses, performances)
                print(f"Excel-отчет успешно сохранен: {file_path}")
            elif choice == "0":
                print("Завершение работы")
                break
            else:
                print("Неизвестная команда")

        except (ValueError, TypeError, OSError, sqlite3.Error) as error:
            print(f"Ошибка: {error}")


if __name__ == "__main__":
    main()
