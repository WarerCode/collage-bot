"""

"""

import core.warerobjects.warerobject as warer


class UserInfo(warer.WarerObject):
    """

    """

    def __init__(self,
                 user_id,
                 username: str,
                 age: int | None=None):
        """
        Инициализирует self.
        """
        super().__init__()
        self.user_id = user_id
        self.username = username
        self.age = age

    def __repr__(self):
        """
        Возвращает отладочное представление данных.
        """
        return (f"MetaData(hints={self.hints}, "
                f"user_id={self.user_id}, "
                f"username={self.username}, "
                f"age={self.age})")

    def __str__(self):
        """
        Возвращает читаемое строковое представление данных.
        """
        return (f"(hints={self.hints}, "
                f"user_id={self.user_id}, "
                f"username={self.username}, "
                f"age={self.age})")

    def to_dict(self):
        """
        Возвращает представление данных в виде json.
        """
        return {
            "hints": self.hints,
            "user_id": self.user_id,
            "username": self.username,
            "age": self.age
        }


if __name__ == "__main__":
    pass
