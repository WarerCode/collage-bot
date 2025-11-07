"""
Здесь представлена реализация класса, хранящего всю информацию
о медиа данных, необходимых для ответа сборки сообщения.
"""

import core.warerobjects.warerobject as warer
import core.warerobjects.content_types.base_type as base_type
import core.warerobjects.content_types.text as text


class Media(warer.WarerObject):
    """
    Класс, хранящий всю информацию о медиа данных, необходимых
    для ответа. Предоставляет интерфейс контейнера.
    Поле self.content также может содержать и объекты типа text.Text.
    """

    def __init__(self, content: list[base_type.BaseMediaType]):
        """
        Инициализирует self.
        """
        super().__init__()
        self.content = content

    def merge_texts(self) -> text.Text:
        """
        Метод для сбора
        """
        merged = text.Text("")
        for item in self.content:
            if isinstance(item, text.Text):
                merged += item
        return merged

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
