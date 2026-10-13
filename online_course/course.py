from abc import ABC, abstractmethod


class Course(ABC):
    """
    Абстрактный базовый класс учебного онлайн-курса.
    Определяет общие атрибуты курса и интерфейс расчёта стоимости со скидкой.
    """

    def __init__(self, course_id: int, title: str, base_price: float, hours: int):
        self.course_id = course_id
        self.title = title
        self.base_price = base_price
        self.hours = hours

    @property
    def course_id(self) -> int:
        return self._course_id

    @course_id.setter
    def course_id(self, value: int):
        if not isinstance(value, int) or value <= 0:
            raise ValueError("ID курса должен быть положительным целым числом")
        self._course_id = value

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, value: str):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Название курса не может быть пустым")
        self._title = value.strip()

    @property
    def base_price(self) -> float:
        return self._base_price

    @base_price.setter
    def base_price(self, value: float):
        if not isinstance(value, (int, float)) or value < 0:
            raise ValueError("Базовая цена курса не может быть отрицательной")
        self._base_price = float(value)

    @property
    def hours(self) -> int:
        return self._hours

    @hours.setter
    def hours(self, value: int):
        if not isinstance(value, int) or value <= 0:
            raise ValueError("Количество академических часов должно быть положительным целым числом")
        self._hours = value

    @abstractmethod
    def calculate_final_price(self, discount_percent: float) -> float:
        """
        Абстрактный метод для вычисления финальной стоимости курса
        с учётом процента скидки за успеваемость.
        """
        pass

    def __str__(self) -> str:
        return f"Курс '{self.title}' (ID: {self.course_id}, {self.hours} ч., {self.base_price:.2f} руб.)"

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"course_id={self.course_id}, "
            f"title={self.title!r}, "
            f"base_price={self.base_price}, "
            f"hours={self.hours})"
        )

    def __eq__(self, other) -> bool:
        if not isinstance(other, Course):
            return False
        return self.course_id == other.course_id


class StandardCourse(Course):
    """
    Класс стандартного онлайн-курса с самостоятельным обучением.
    Максимально допустимая скидка по успеваемости: 30%.
    """

    def __init__(
        self,
        course_id: int,
        title: str,
        base_price: float,
        hours: int,
        has_certificate: bool = True,
        max_discount_percent: float = 30.0
    ):
        super().__init__(course_id, title, base_price, hours)
        self.has_certificate = has_certificate
        self.max_discount_percent = max_discount_percent

    @property
    def has_certificate(self) -> bool:
        return self._has_certificate

    @has_certificate.setter
    def has_certificate(self, value: bool):
        if not isinstance(value, bool):
            raise TypeError("Флаг наличия сертификата должен быть булевым значением")
        self._has_certificate = value

    @property
    def max_discount_percent(self) -> float:
        return self._max_discount_percent

    @max_discount_percent.setter
    def max_discount_percent(self, value: float):
        if not isinstance(value, (int, float)) or not (0.0 <= value <= 100.0):
            raise ValueError("Максимальная скидка должна быть в диапазоне от 0 до 100%")
        self._max_discount_percent = float(value)

    def calculate_final_price(self, discount_percent: float) -> float:
        if not isinstance(discount_percent, (int, float)) or discount_percent < 0:
            raise ValueError("Процент скидки не может быть отрицательным")
        effective_discount = min(float(discount_percent), self.max_discount_percent)
        final_price = self.base_price * (1.0 - effective_discount / 100.0)
        return round(final_price, 2)

    def __str__(self) -> str:
        cert_info = "с сертификатом" if self.has_certificate else "без сертификата"
        return f"Стандартный курс '{self.title}' ({cert_info}, {self.base_price:.2f} руб., макс. скидка: {self.max_discount_percent}%)"

    def __repr__(self) -> str:
        return (
            f"StandardCourse("
            f"course_id={self.course_id}, "
            f"title={self.title!r}, "
            f"base_price={self.base_price}, "
            f"hours={self.hours}, "
            f"has_certificate={self.has_certificate}, "
            f"max_discount_percent={self.max_discount_percent})"
        )


class IntensiveCourse(Course):
    """
    Класс интенсивного онлайн-курса с персональным ментором и практическими проектами.
    Максимально допустимая скидка по успеваемости: 20%.
    """

    def __init__(
        self,
        course_id: int,
        title: str,
        base_price: float,
        hours: int,
        mentor_name: str,
        projects_count: int = 1,
        max_discount_percent: float = 20.0
    ):
        super().__init__(course_id, title, base_price, hours)
        self.mentor_name = mentor_name
        self.projects_count = projects_count
        self.max_discount_percent = max_discount_percent

    @property
    def mentor_name(self) -> str:
        return self._mentor_name

    @mentor_name.setter
    def mentor_name(self, value: str):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Имя ментора не может быть пустым")
        self._mentor_name = value.strip()

    @property
    def projects_count(self) -> int:
        return self._projects_count

    @projects_count.setter
    def projects_count(self, value: int):
        if not isinstance(value, int) or value < 0:
            raise ValueError("Количество проектов не может быть отрицательным")
        self._projects_count = value

    @property
    def max_discount_percent(self) -> float:
        return self._max_discount_percent

    @max_discount_percent.setter
    def max_discount_percent(self, value: float):
        if not isinstance(value, (int, float)) or not (0.0 <= value <= 100.0):
            raise ValueError("Максимальная скидка должна быть в диапазоне от 0 до 100%")
        self._max_discount_percent = float(value)

    def calculate_final_price(self, discount_percent: float) -> float:
        if not isinstance(discount_percent, (int, float)) or discount_percent < 0:
            raise ValueError("Процент скидки не может быть отрицательным")
        effective_discount = min(float(discount_percent), self.max_discount_percent)
        final_price = self.base_price * (1.0 - effective_discount / 100.0)
        return round(final_price, 2)

    def __str__(self) -> str:
        return (
            f"Интенсивный курс '{self.title}' (ментор: {self.mentor_name}, "
            f"проектов: {self.projects_count}, {self.base_price:.2f} руб., макс. скидка: {self.max_discount_percent}%)"
        )

    def __repr__(self) -> str:
        return (
            f"IntensiveCourse("
            f"course_id={self.course_id}, "
            f"title={self.title!r}, "
            f"base_price={self.base_price}, "
            f"hours={self.hours}, "
            f"mentor_name={self.mentor_name!r}, "
            f"projects_count={self.projects_count}, "
            f"max_discount_percent={self.max_discount_percent})"
        )
