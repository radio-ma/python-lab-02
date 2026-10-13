from datetime import datetime
from pathlib import Path
from typing import Dict

from docx import Document
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill

from .course import Course, StandardCourse, IntensiveCourse
from .student import Student
from .performance import AcademicPerformance
from .analytics import get_student_statistics, rank_students


def export_report(
    students: Dict[int, Student],
    courses: Dict[int, Course],
    performances: Dict[int, AcademicPerformance],
    output_dir=None
) -> Path:
    """Экспорт аналитического отчёта в формат Microsoft Word (.docx)."""
    if output_dir is None:
        reports_dir = Path(__file__).resolve().parent.parent / "reports"
    else:
        reports_dir = Path(output_dir)

    reports_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    file_path = reports_dir / f"course_report_{timestamp}.docx"

    doc = Document()
    doc.add_heading("Образовательная платформа: Онлайн-курсы", 0)
    doc.add_paragraph(f"Отчёт сформирован: {datetime.now():%d.%m.%Y %H:%M}")

    # 1. Общая статистика
    doc.add_heading("1. Общая статистика платформы", level=1)
    doc.add_paragraph(f"Количество курсов в каталоге: {len(courses)}")
    doc.add_paragraph(f"Количество зарегистрированных студентов: {len(students)}")
    doc.add_paragraph(f"Всего записей об успеваемости: {len(performances)}")

    # 2. Каталог курсов
    doc.add_heading("2. Каталог доступных курсов", level=1)
    if courses:
        table_c = doc.add_table(rows=1, cols=6)
        table_c.style = "Table Grid"
        headers_c = ["ID", "Тип", "Название", "Базовая цена", "Часы", "Макс. скидка"]
        for cell, text in zip(table_c.rows[0].cells, headers_c):
            cell.text = text

        for course in courses.values():
            row = table_c.add_row().cells
            row[0].text = str(course.course_id)
            row[1].text = "Стандартный" if isinstance(course, StandardCourse) else "Интенсив"
            row[2].text = course.title
            row[3].text = f"{course.base_price:.2f} руб."
            row[4].text = str(course.hours)
            row[5].text = f"{course.max_discount_percent:.1f}%"
    else:
        doc.add_paragraph("Курсы пока не добавлены.")

    # 3. Ведомость успеваемости
    doc.add_heading("3. Академическая ведомость и расчёт скидок", level=1)
    if performances:
        table_p = doc.add_table(rows=1, cols=8)
        table_p.style = "Table Grid"
        headers_p = [
            "Студент", "Курс", "ДЗ", "Экзамен", "Посещ.", "Итог", "Скидка", "Итоговая цена"
        ]
        for cell, text in zip(table_p.rows[0].cells, headers_p):
            cell.text = text

        for perf in performances.values():
            st = students.get(perf.student_id)
            c = courses.get(perf.course_id)
            st_name = st.full_name if st else f"ID {perf.student_id}"
            c_title = c.title if c else f"ID {perf.course_id}"
            discount = perf.calculate_discount()
            final_price = c.calculate_final_price(discount) if c else 0.0

            row = table_p.add_row().cells
            row[0].text = st_name
            row[1].text = c_title
            row[2].text = f"{perf.homework_score:.1f}"
            row[3].text = f"{perf.exam_score:.1f}"
            row[4].text = f"{perf.attendance_rate:.1f}%"
            row[5].text = f"{perf.calculate_final_score():.1f} ({perf.get_status()})"
            row[6].text = f"{discount:.1f}%"
            row[7].text = f"{final_price:.2f} руб."
    else:
        doc.add_paragraph("Записи об успеваемости отсутствуют.")

    # 4. Персональная статистика студентов
    doc.add_heading("4. Персональная статистика студентов", level=1)
    if not students:
        doc.add_paragraph("Студенты не зарегистрированы.")
    else:
        for st in rank_students(list(students.values()), performances):
            stats = get_student_statistics(st, performances, courses)
            doc.add_heading(f"{st.full_name} (ID: {st.student_id})", level=2)
            doc.add_paragraph(f"Email: {st.email}")
            doc.add_paragraph(f"Изучаемых курсов: {stats['enrolled_courses_count']}")
            doc.add_paragraph(f"Средний итоговый балл: {stats['average_final_score']}")
            doc.add_paragraph(f"Средняя скидка за успеваемость: {stats['average_discount']}%")
            doc.add_paragraph(f"Стоимость курсов без скидок: {stats['total_initial_cost']:.2f} руб.")
            doc.add_paragraph(f"Итоговая стоимость со скидками: {stats['total_discounted_cost']:.2f} руб.")
            doc.add_paragraph(f"Сэкономлено студентом: {stats['total_savings']:.2f} руб.")

    doc.save(file_path)
    return file_path


def export_excel(
    students: Dict[int, Student],
    courses: Dict[int, Course],
    performances: Dict[int, AcademicPerformance],
    output_dir=None
) -> Path:
    """Экспорт аналитического отчёта в формат Microsoft Excel (.xlsx)."""
    if output_dir is None:
        reports_dir = Path(__file__).resolve().parent.parent / "reports"
    else:
        reports_dir = Path(output_dir)

    reports_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    file_path = reports_dir / f"course_report_{timestamp}.xlsx"

    wb = Workbook()

    # Лист 1: Сводка
    ws_summary = wb.active
    ws_summary.title = "Сводка"
    ws_summary.append(["Показатель", "Значение"])
    ws_summary.append(["Дата формирования отчёта", datetime.now().strftime("%d.%m.%Y %H:%M")])
    ws_summary.append(["Количество курсов", len(courses)])
    ws_summary.append(["Количество студентов", len(students)])
    ws_summary.append(["Количество оценочных ведомостей", len(performances)])

    total_init = 0.0
    total_disc = 0.0
    for perf in performances.values():
        c = courses.get(perf.course_id)
        if c:
            total_init += c.base_price
            disc = perf.calculate_discount()
            total_disc += c.calculate_final_price(disc)

    ws_summary.append(["Общая начальная стоимость (руб.)", round(total_init, 2)])
    ws_summary.append(["Общая стоимость со скидками (руб.)", round(total_disc, 2)])
    ws_summary.append(["Суммарная скидка студентам (руб.)", round(total_init - total_disc, 2)])

    # Лист 2: Курсы
    ws_courses = wb.create_sheet("Курсы")
    ws_courses.append([
        "ID", "Тип курса", "Название", "Базовая цена (руб.)", "Часы", "Особенности", "Макс. скидка (%)"
    ])
    for c in courses.values():
        c_type = "Стандартный" if isinstance(c, StandardCourse) else "Интенсив"
        features = "Сертификат" if getattr(c, "has_certificate", False) else f"Ментор: {getattr(c, 'mentor_name', 'Нет')}"
        ws_courses.append([
            c.course_id, c_type, c.title, c.base_price, c.hours, features, c.max_discount_percent
        ])

    # Лист 3: Успеваемость
    ws_perf = wb.create_sheet("Успеваемость")
    ws_perf.append([
        "ID записи", "ID студента", "Студент", "ID курса", "Курс",
        "Балл ДЗ", "Балл экзамена", "Посещаемость (%)",
        "Итоговый балл", "Статус", "Скидка (%)", "Итоговая цена (руб.)"
    ])
    for p in performances.values():
        st = students.get(p.student_id)
        c = courses.get(p.course_id)
        st_name = st.full_name if st else "Неизвестен"
        c_title = c.title if c else "Неизвестен"
        discount = p.calculate_discount()
        final_price = c.calculate_final_price(discount) if c else 0.0

        ws_perf.append([
            p.performance_id, p.student_id, st_name, p.course_id, c_title,
            p.homework_score, p.exam_score, p.attendance_rate,
            p.calculate_final_score(), p.get_status(), discount, final_price
        ])

    # Лист 4: Рейтинг студентов
    ws_rank = wb.create_sheet("Рейтинг студентов")
    ws_rank.append([
        "Место", "ID студента", "ФИО студента", "Email", "Курсов",
        "Средний балл", "Средняя скидка (%)", "Экономия (руб.)"
    ])
    for idx, st in enumerate(rank_students(list(students.values()), performances), start=1):
        st_stats = get_student_statistics(st, performances, courses)
        ws_rank.append([
            idx, st.student_id, st.full_name, st.email,
            st_stats["enrolled_courses_count"],
            st_stats["average_final_score"],
            st_stats["average_discount"],
            st_stats["total_savings"]
        ])

    # Стилизация таблиц
    header_fill = PatternFill(fill_type="solid", fgColor="28405A")
    header_font = Font(name="Arial", size=11, bold=True, color="FFFFFF")

    for sheet in wb.worksheets:
        sheet.freeze_panes = "A2"
        sheet.auto_filter.ref = sheet.dimensions

        for cell in sheet[1]:
            cell.font = header_font
            cell.fill = header_fill

        for col in sheet.columns:
            max_len = max(
                len(str(cell.value)) if cell.value is not None else 0
                for cell in col
            )
            col_letter = col[0].column_letter
            sheet.column_dimensions[col_letter].width = min(max(max_len + 3, 12), 45)

    wb.save(file_path)
    return file_path
