import openpyxl
from online_course.course import StandardCourse, IntensiveCourse
from online_course.student import Student
from online_course.performance import AcademicPerformance
from online_course.report import export_excel


def test_export_excel(tmp_path):
    c1 = StandardCourse(1, "Python Базовый", 20000.0, 40)
    c2 = IntensiveCourse(2, "Data Science", 50000.0, 60, mentor_name="Куратор")
    st = Student(1, "Суворов Иван", "ivan@study.ru")
    p1 = AcademicPerformance(1, 1, 1, 95.0, 95.0, 100.0)
    p2 = AcademicPerformance(2, 1, 2, 80.0, 80.0, 90.0)

    courses = {1: c1, 2: c2}
    students = {1: st}
    perfs = {1: p1, 2: p2}

    report_path = export_excel(students, courses, perfs, output_dir=tmp_path)

    assert report_path.exists()
    assert report_path.suffix == ".xlsx"

    wb = openpyxl.load_workbook(report_path)
    sheet_names = wb.sheetnames
    assert "Сводка" in sheet_names
    assert "Курсы" in sheet_names
    assert "Успеваемость" in sheet_names
    assert "Рейтинг студентов" in sheet_names


def test_export_empty_excel(tmp_path):
    report_path = export_excel({}, {}, {}, output_dir=tmp_path)

    assert report_path.exists()
    assert report_path.suffix == ".xlsx"

    wb = openpyxl.load_workbook(report_path)
    assert len(wb.sheetnames) >= 1
