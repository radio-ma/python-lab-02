import sqlite3
from pathlib import Path
from typing import Dict, Optional

from .course import Course, StandardCourse, IntensiveCourse
from .student import Student
from .performance import AcademicPerformance

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "course.db"


def initialize_database(db_path=None) -> Path:
    """
    Инициализация базы данных SQLite.
    Создает таблицы courses, students и performances, если они не существуют.
    """
    if db_path is None:
        db_path = DB_PATH

    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(db_path) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.executescript("""
            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_type TEXT NOT NULL,
                title TEXT NOT NULL,
                base_price REAL NOT NULL,
                hours INTEGER NOT NULL,
                has_certificate INTEGER DEFAULT 1,
                mentor_name TEXT,
                projects_count INTEGER DEFAULT 0,
                max_discount REAL NOT NULL
            );

            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE
            );

            CREATE TABLE IF NOT EXISTS performances (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                course_id INTEGER NOT NULL,
                homework_score REAL NOT NULL DEFAULT 0.0,
                exam_score REAL NOT NULL DEFAULT 0.0,
                attendance_rate REAL NOT NULL DEFAULT 0.0,
                final_score REAL NOT NULL DEFAULT 0.0,
                discount_percent REAL NOT NULL DEFAULT 0.0,
                final_price REAL NOT NULL DEFAULT 0.0,
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
                FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
                UNIQUE(student_id, course_id)
            );
        """)

    return db_path


def create_standard_course(
    title: str,
    base_price: float,
    hours: int,
    has_certificate: bool = True,
    max_discount_percent: float = 30.0,
    db_path=None
) -> StandardCourse:
    """Создание и сохранение в БД стандартного курса."""
    title = title.strip()
    if not title:
        raise ValueError("Название курса не может быть пустым")
    if base_price < 0:
        raise ValueError("Базовая цена не может быть отрицательной")
    if hours <= 0:
        raise ValueError("Количество часов должно быть положительным")

    db_path = initialize_database(db_path)

    with sqlite3.connect(db_path) as connection:
        cursor = connection.execute("""
            INSERT INTO courses (
                course_type, title, base_price, hours,
                has_certificate, mentor_name, projects_count, max_discount
            )
            VALUES (?, ?, ?, ?, ?, NULL, 0, ?)
        """, (
            "standard",
            title,
            float(base_price),
            int(hours),
            1 if has_certificate else 0,
            float(max_discount_percent)
        ))
        new_id = cursor.lastrowid

    return StandardCourse(
        new_id,
        title,
        base_price,
        hours,
        has_certificate=has_certificate,
        max_discount_percent=max_discount_percent
    )


def create_intensive_course(
    title: str,
    base_price: float,
    hours: int,
    mentor_name: str,
    projects_count: int = 1,
    max_discount_percent: float = 20.0,
    db_path=None
) -> IntensiveCourse:
    """Создание и сохранение в БД интенсивного курса."""
    title = title.strip()
    mentor_name = mentor_name.strip()
    if not title:
        raise ValueError("Название курса не может быть пустым")
    if not mentor_name:
        raise ValueError("Имя ментора не может быть пустым")
    if base_price < 0:
        raise ValueError("Базовая цена не может быть отрицательной")
    if hours <= 0:
        raise ValueError("Количество часов должно быть положительным")
    if projects_count < 0:
        raise ValueError("Количество проектов не может быть отрицательным")

    db_path = initialize_database(db_path)

    with sqlite3.connect(db_path) as connection:
        cursor = connection.execute("""
            INSERT INTO courses (
                course_type, title, base_price, hours,
                has_certificate, mentor_name, projects_count, max_discount
            )
            VALUES (?, ?, ?, ?, 1, ?, ?, ?)
        """, (
            "intensive",
            title,
            float(base_price),
            int(hours),
            mentor_name,
            int(projects_count),
            float(max_discount_percent)
        ))
        new_id = cursor.lastrowid

    return IntensiveCourse(
        new_id,
        title,
        base_price,
        hours,
        mentor_name=mentor_name,
        projects_count=projects_count,
        max_discount_percent=max_discount_percent
    )


def create_student(full_name: str, email: str, db_path=None) -> Student:
    """Создание и сохранение в БД нового студента."""
    full_name = full_name.strip()
    email = email.strip()
    if not full_name:
        raise ValueError("Имя студента не может быть пустым")
    if "@" not in email or "." not in email:
        raise ValueError("Некорректный адрес электронной почты")

    db_path = initialize_database(db_path)

    with sqlite3.connect(db_path) as connection:
        cursor = connection.execute("""
            INSERT INTO students (full_name, email)
            VALUES (?, ?)
        """, (full_name, email))
        new_id = cursor.lastrowid

    return Student(new_id, full_name, email)


def save_performance(
    student_id: int,
    course_id: int,
    homework_score: float,
    exam_score: float,
    attendance_rate: float,
    db_path=None
) -> AcademicPerformance:
    """
    Сохранение или обновление данных об успеваемости студента по курсу в SQLite.
    Проверяет существование студента и курса, вычисляет итоговый балл,
    скидку и финальную цену курса.
    """
    db_path = initialize_database(db_path)

    temp_perf = AcademicPerformance(
        1, student_id, course_id,
        homework_score, exam_score, attendance_rate
    )
    final_score = temp_perf.calculate_final_score()
    discount = temp_perf.calculate_discount()

    with sqlite3.connect(db_path) as connection:
        connection.execute("PRAGMA foreign_keys = ON")

        course_row = connection.execute(
            "SELECT course_type, base_price, max_discount FROM courses WHERE id = ?",
            (course_id,)
        ).fetchone()

        if course_row is None:
            raise ValueError(f"Курс с ID {course_id} не найден в базе данных")

        student_row = connection.execute(
            "SELECT id FROM students WHERE id = ?",
            (student_id,)
        ).fetchone()

        if student_row is None:
            raise ValueError(f"Студент с ID {student_id} не найден в базе данных")

        base_price = course_row[1]
        max_disc = course_row[2]
        effective_disc = min(discount, max_disc)
        final_price = round(base_price * (1.0 - effective_disc / 100.0), 2)

        cursor = connection.execute("""
            INSERT INTO performances (
                student_id, course_id, homework_score, exam_score,
                attendance_rate, final_score, discount_percent, final_price
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(student_id, course_id) DO UPDATE SET
                homework_score = excluded.homework_score,
                exam_score = excluded.exam_score,
                attendance_rate = excluded.attendance_rate,
                final_score = excluded.final_score,
                discount_percent = excluded.discount_percent,
                final_price = excluded.final_price
        """, (
            student_id,
            course_id,
            temp_perf.homework_score,
            temp_perf.exam_score,
            temp_perf.attendance_rate,
            final_score,
            discount,
            final_price
        ))

        perf_id = cursor.lastrowid
        if not perf_id:
            row = connection.execute(
                "SELECT id FROM performances WHERE student_id = ? AND course_id = ?",
                (student_id, course_id)
            ).fetchone()
            perf_id = row[0]

    return AcademicPerformance(
        perf_id,
        student_id,
        course_id,
        temp_perf.homework_score,
        temp_perf.exam_score,
        temp_perf.attendance_rate
    )


def load_courses(db_path=None) -> Dict[int, Course]:
    """Загрузка всех курсов из базы данных."""
    db_path = initialize_database(db_path)
    courses = {}

    with sqlite3.connect(db_path) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute("SELECT * FROM courses ORDER BY id").fetchall()

    for row in rows:
        if row["course_type"] == "standard":
            courses[row["id"]] = StandardCourse(
                row["id"],
                row["title"],
                row["base_price"],
                row["hours"],
                has_certificate=bool(row["has_certificate"]),
                max_discount_percent=row["max_discount"]
            )
        elif row["course_type"] == "intensive":
            courses[row["id"]] = IntensiveCourse(
                row["id"],
                row["title"],
                row["base_price"],
                row["hours"],
                mentor_name=row["mentor_name"] or "Куратор",
                projects_count=row["projects_count"] or 1,
                max_discount_percent=row["max_discount"]
            )
        else:
            raise ValueError(f"Неизвестный тип курса: {row['course_type']}")

    return courses


def load_students(db_path=None) -> Dict[int, Student]:
    """Загрузка всех студентов из базы данных."""
    db_path = initialize_database(db_path)
    students = {}

    with sqlite3.connect(db_path) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute("SELECT * FROM students ORDER BY id").fetchall()

    for row in rows:
        students[row["id"]] = Student(row["id"], row["full_name"], row["email"])

    return students


def load_performances(db_path=None) -> Dict[int, AcademicPerformance]:
    """Загрузка всех записей успеваемости из базы данных."""
    db_path = initialize_database(db_path)
    performances = {}

    with sqlite3.connect(db_path) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute("SELECT * FROM performances ORDER BY id").fetchall()

    for row in rows:
        performances[row["id"]] = AcademicPerformance(
            row["id"],
            row["student_id"],
            row["course_id"],
            row["homework_score"],
            row["exam_score"],
            row["attendance_rate"]
        )

    return performances
