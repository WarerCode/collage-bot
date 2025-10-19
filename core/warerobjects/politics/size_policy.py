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
        HORIZONTAL = (2,1)
        VERTICAL = (1,2)
        HOR_PHONE = (16,9)
        VER_PHONE = (9,16)

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
        def scaler(self):
            """
            Возвращает коэффициент умножения.
            """
            scalers = [1500, 750, 100]
            for scale in scalers:
                new_width = self.value[0]*scale
                new_right = self.value[1]*scale
                if max(new_width, new_right) < 2000:
                    return scale
            return scalers[-1]

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

    @property
    def size(self):
        """
        Свойство-getter размера изображения.

        Возвращает:
            Size: элемент перечислителя размера
        """
        return self._size
    
    @size.setter
    def size(self, value: Size):
        """
        Свойство-setter для объекта изображения.

        Аргументы:
            value (Size): новый элемент перечислителя размера
        """
        self._size = value

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
    print("Класс политики размеров прямоугольников:")
    help(SizePolicy)

    print("__str__:")
    for size_mode in SizePolicy.Size:
        size_policy = SizePolicy(size_mode)
        print(f"Политика размера для {size_mode.name}: {size_policy}")
    print()

    print("__repr__:")
    for size_mode in SizePolicy.Size:
        size_policy = SizePolicy(size_mode)
        print(f"Политика размера для {size_mode.name}: {size_policy.__repr__()}")
    print()

    print("to_dict:")
    for size_mode in SizePolicy.Size:
        size_policy = SizePolicy(size_mode)
        print(f"Политика размера для {size_mode.name}: {size_policy.to_dict()}")
    print()

    print("scale:")
    base_size = 720
    for size_mode in SizePolicy.Size:
        size_policy = SizePolicy(size_mode)
        scaled = size_policy.scale(base_size)
        print(f"Масштаб {base_size} для {size_mode.name}: {scaled}")
