import collections
import core.warerobjects.content_types.base_type as base_type

class Text(base_type.BaseMediaType):
    """
    Класс описывающий текст как медиа-объект.

    Атрибуты класса:
        Отсутствуют

    Атрибут экземпляра:
        _text: текстовое значение
    """

    def __init__(self):
        """
        Инициализирует объект текста

        Параметры:
            отсутствуют
        """
        super().__init__()
        self._text = ""

    def __init__(self, text: str):
        """
        Инициализирует объект текста

        Параметры:
            text (str): исходная строка.
        """
        super().__init__()
        self._text = text

    @property
    def length(self) -> int:
        """
        Свойство получение длины текста.

        Аргументы:
            отсутствуют

        Возвращает:
            int: длина текста
        """
        return len(self._text)
    
    def words_count(self, separator: str=" ") -> int:
        """
        Получение количества слов в тексте.

        Аргументы:
            separator (str): разделитель слов

        Возвращает:
            int: кол-во слов
        """
        return len(self._text.split(separator))
    
    def symbol_types_count(self) -> dict:
        """
        Получение набора кол-ва определённых символов в тексте.

        Аргументы:
            отсутствуют

        Возвращает:
            dict: словарь вида:
                - ключ: тип символа
                - значение: кол-во
        """
        result = collections.defaultdict(int)
        for char in self._text:
            if char.isdigit():
                result["digits"] += 1
            elif char.isspace():
                result["spaces"] += 1
            elif char.isalpha():
                result["alphas"] += 1
            else:
                result["punctuations"] += 1

        return dict(result)
    
    @property
    def text(self):
        """
        Свойство-getter для текста.

        Аргументы:
            отсутствуют

        Возвращает:
            str: _text
        """
        return self._text
    
    @text.setter
    def text(self, value: str):
        """
        Свойство-setter для текста.

        Аргументы:
            value (str): новое значения для текста

        Возвращает:
            None
        """
        self._text = value

    def __str__(self):
        return self._text

    def __repr__(self):
        return self._text

    def to_dict(self):
        return {"text": self._text}

if __name__ == "__main__":
    print("Пример использования:")

    my_text = Text("Какой-то мой текст, с различными 456 67 символами")

    print(f"Длина текста: {my_text.length}")
    print(f"Кол-во слов в тексте: {my_text.words_count()}")
    print(f"Кол-во символов определённого типа: {my_text.symbol_types_count()}")
    my_text.text = "Какой-то новый текст"
    print(f"Новый текст: {my_text.text}")