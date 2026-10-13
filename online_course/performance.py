class AcademicPerformance:
    """
    Класс академической успеваемости студента по конкретному курсу.
    Хранит баллы за домашние задания, экзамен и процент посещаемости.
    Рассчитывает итоговый балл, статус успеваемости и положенную скидку на курс.
    """

    def __init__(
        self,
        performance_id: int,
        student_id: int,
        course_id: int,
        homework_score: float = 0.0,
        exam_score: float = 0.0,
        attendance_rate: float = 0.0
    ):
        self.performance_id = performance_id
        self.student_id = student_id
        self.course_id = course_id
        self.homework_score = homework_score
        self.exam_score = exam_score
        self.attendance_rate = attendance_rate

    @property
    def performance_id(self) -> int:
        return self._performance_id

    @performance_id.setter
    def performance_id(self, value: int):
        if not isinstance(value, int) or value <= 0:
            raise ValueError("ID записи успеваемости должен быть положительным целым числом")
        self._performance_id = value

    @property
    def student_id(self) -> int:
        return self._student_id

    @student_id.setter
    def student_id(self, value: int):
        if not isinstance(value, int) or value <= 0:
            raise ValueError("ID студента должен быть положительным целым числом")
        self._student_id = value

    @property
    def course_id(self) -> int:
        return self._course_id

    @course_id.setter
    def course_id(self, value: int):
        if not isinstance(value, int) or value <= 0:
            raise ValueError("ID курса должен быть положительным целым числом")
        self._course_id = value

    @property
    def homework_score(self) -> float:
        return self._homework_score

    @homework_score.setter
    def homework_score(self, value: float):
        if not isinstance(value, (int, float)) or not (0.0 <= float(value) <= 100.0):
            raise ValueError("Балл за домашние задания должен быть в диапазоне от 0.0 до 100.0")
        self._homework_score = float(value)

    @property
    def exam_score(self) -> float:
        return self._exam_score

    @exam_score.setter
    def exam_score(self, value: float):
        if not isinstance(value, (int, float)) or not (0.0 <= float(value) <= 100.0):
            raise ValueError("Экзаменационный балл должен быть в диапазоне от 0.0 до 100.0")
        self._exam_score = float(value)

    @property
    def attendance_rate(self) -> float:
        return self._attendance_rate

    @attendance_rate.setter
    def attendance_rate(self, value: float):
        if not isinstance(value, (int, float)) or not (0.0 <= float(value) <= 100.0):
            raise ValueError("Процент посещаемости должен быть в диапазоне от 0.0 до 100.0")
        self._attendance_rate = float(value)

    def calculate_final_score(self) -> float:
        """
        Расчёт итогового средневзвешенного балла успеваемости:
        40% домашние задания + 40% экзамен + 20% посещаемость.
        """
        score = 0.4 * self.homework_score + 0.4 * self.exam_score + 0.2 * self.attendance_rate
        return round(score, 2)

    def get_status(self) -> str:
        """Определение академического статуса по итоговому баллу."""
        final_score = self.calculate_final_score()
        if final_score >= 90.0:
            return "Отлично"
        elif final_score >= 75.0:
            return "Хорошо"
        elif final_score >= 60.0:
            return "Удовлетворительно"
        else:
            return "Неудовлетворительно"

    def calculate_discount(self) -> float:
        """
        Расчёт скидки на курс в зависимости от успеваемости:
        - Итоговый балл >= 90 («Отлично»): 25%
        - Итоговый балл >= 75 («Хорошо»): 15%
        - Итоговый балл >= 60 («Удовлетворительно»): 5%
        - Итоговый балл < 60 («Неудовлетворительно»): 0%
        Бонус: 100% посещаемость даёт дополнительно +5% скидки.
        """
        status = self.get_status()
        base_discount = {
            "Отлично": 25.0,
            "Хорошо": 15.0,
            "Удовлетворительно": 5.0,
            "Неудовлетворительно": 0.0
        }[status]

        bonus = 5.0 if self.attendance_rate >= 100.0 else 0.0
        return round(base_discount + bonus, 2)

    def update_scores(self, homework_score: float, exam_score: float, attendance_rate: float):
        """Обновление баллов успеваемости."""
        self.homework_score = homework_score
        self.exam_score = exam_score
        self.attendance_rate = attendance_rate

    def __str__(self) -> str:
        final_score = self.calculate_final_score()
        status = self.get_status()
        discount = self.calculate_discount()
        return (
            f"Успеваемость (Студент ID: {self.student_id}, Курс ID: {self.course_id}): "
            f"Итог={final_score} ({status}), Скидка={discount}%"
        )

    def __repr__(self) -> str:
        return (
            f"AcademicPerformance("
            f"performance_id={self.performance_id}, "
            f"student_id={self.student_id}, "
            f"course_id={self.course_id}, "
            f"homework_score={self.homework_score}, "
            f"exam_score={self.exam_score}, "
            f"attendance_rate={self.attendance_rate})"
        )

    def __eq__(self, other) -> bool:
        if not isinstance(other, AcademicPerformance):
            return False
        return self.performance_id == other.performance_id
