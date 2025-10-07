"""
Здесь представлена реализация класса, хранящего всю информацию
о медиа данных, необходимых для ответа сборки сообщения.
"""

import core.warerobjects.warerobject as warer
import core.warerobjects.content_types.base_type as basemedia


class Media(warer.WarerObject):
    """
    Класс, хранящий всю информацию о медиа данных, необходимых
    для ответа. Предоставляет интерфейс контейнера.
    """

    def __init__(self, content: list[basemedia.BaseMediaType]):
        """
        Инициализирует self.
        """
        super().__init__()
        self.content = content

    def __str__(self):
        """
        Представляет объект в удобном виде.
        """
        return f"Media(content={self.content})"

    def __repr__(self):
        """
        Представляет объект в удобном для отладки виде.
        """
        return f"(content={self.content})"

    def to_dict(self):
        """
        Представляет объект в виде словаря.
        """
        return {
            "content": [item for item in self.content],
            "hints": self.hints
        }

#TODO: доработать интерфейс класса Медиа. @DanilaEfimov


if __name__ == "__main__":
    pass
