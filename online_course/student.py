class Student:
    """
    Класс студента образовательной платформы.
    Хранит информацию об учащемся, его контактных данных и идентификаторе.
    """

    def __init__(self, student_id: int, full_name: str, email: str):
        self.student_id = student_id
        self.full_name = full_name
        self.email = email

    @property
    def student_id(self) -> int:
        return self._student_id

    @student_id.setter
    def student_id(self, value: int):
        if not isinstance(value, int) or value <= 0:
            raise ValueError("ID студента должен быть положительным целым числом")
        self._student_id = value

    @property
    def full_name(self) -> str:
        return self._full_name

    @full_name.setter
    def full_name(self, value: str):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Имя студента не может быть пустым")
        self._full_name = value.strip()

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, value: str):
        if not isinstance(value, str) or "@" not in value or "." not in value:
            raise ValueError("Email должен содержать корректный адрес электронной почты (содержать '@' и '.')")
        self._email = value.strip()

    def update_email(self, new_email: str):
        """Обновление контактного email студента."""
        self.email = new_email

    def __str__(self) -> str:
        return f"Студент {self.full_name} (ID: {self.student_id}, email: {self.email})"

    def __repr__(self) -> str:
        return (
            f"Student("
            f"student_id={self.student_id}, "
            f"full_name={self.full_name!r}, "
            f"email={self.email!r})"
        )

    def __eq__(self, other) -> bool:
        if not isinstance(other, Student):
            return False
        return self.student_id == other.student_id
