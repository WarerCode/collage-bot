"""
Модуль сожержит определение класса политики размеров.

Класс рекомендуется использовать для передачи в качестве параметра
или в качестве поля класса.
"""

import enum

import core.warerobjects.politics.basepolicy as policy


class SizePolicy(policy.Policy):
    """
    Класс политики размеров прямоугольников.

    Родители:
        policy.Policy
        warer.WarerObject
        abc.ABC

    Атрибуты:
        _size (Size): обертка над кортежем (int, int) с интерфейсом масштабирования.
    """

    class Size(enum.Enum):
        """
        Класс-перечислитель, обертка над кортежем (int, int)
        """

        SQUARE = (1,1)
        HORIZONTAL = (1,2)
        VERTICAL = (2,1)
        HOR_PHONE = (9,16)
        VER_PHONE = (16,9)

        @property
        def width(self):
            """
            Возвращает нормализованую ширину.
            """
            return self.value[0] / max(self.value)

        @property
        def height(self):
            """
            Возвращает нормализованную высоту.
            """
            return self.value[1] / max(self.value)

        @property
        def aspect_ratio(self):
            """
            Возвращает отношение ширины к высоте.
            """
            return self.value[0] / self.value[1]

        @property
        def normalized(self):
            """
            Возвращает нормализованный размер.
            """
            return self.width, self.height

    def __init__(self, mode: Size):
        """
        Инициализирует self.
        """
        super().__init__()
        self._size = mode

    def __str__(self):
        """
        Преобразует объект в строку.
        Полезно для отладки или логирования.
        """
        return (f"SizePolicy(hints={self.hints}, "
                f"size={self._size.value})")

    def __repr__(self):
        """
        Возвращает строковое представление объекта в стиле Python.
        """
        return (f"(hints={self.hints}, "
                f"_size={self._size.value})")

    def to_dict(self):
        """
        Возвращает представление объекта в виде словаря (например, для сериализации в JSON).

        Возвращает:
            dict: словарь, представляющий объект.
        """
        return {
            "hints": self.hints,
            "size": self._size.value
        }

    def scale(self, base_size: int):
        """
        Масштабирует стороны пропорционально базовому размеру.

        Параметры:
            base_size (int): единица размера
        """
        normalized = self._size.normalized
        return (int(normalized[0] * base_size),
                int(normalized[1] * base_size))



if __name__ == "__main__":
    print("")
    help(SizePolicy)

    square = SizePolicy(SizePolicy.Size.SQUARE)
    print(f"Объект политики квадратного холста: {square}")
    base = 720
    print(f"Получим размер с масштабом {base}: {square.scale(base)}")
    base = 360
    print(f"Получим размер с масштабом {base}: {square.scale(base)}")
    print()

    print("Методы представления объекта:")
    print(f"__str__: {square.__str__()}")
    print(f"__repr__: {square.__repr__()}")
    print(f"to_dict: {square.to_dict()}")
