"""
Класс для хранения дополнительных данных других объектов WarerCode.

Предполагает использование в качестве (приватного) поля класса.
Предоставляет возможности по указанию спецификации дополнительных данных.
"""

import enum

import core.warerobjects.warerobject as warer


class MetaData(warer.WarerObject):
    """
    Класс для хранения дополнительной информации об объектах.

    Предполагается использовать, как поле класса.

    Родители:
        warer.WarerObject
        abc.ABC

    Аттрибуты:
        type (Metadata.Type): хранит спецификацию объекта.
    """

    class Type(enum.Enum):
        """
        Вложенный класс-перечислитель для MetaData.

        Содержит строковые константы для задания объекту спецификации.

        Например, можно указать, что значения ключей не важны (KEY_ONLY),
        или что все значения - числа или строки и т.д.

        Может быть полезно при чтении данных.
        """

        STR_ONLY = "string_only"
        INT_ONLY = "integer_only"
        KEY_ONLY = "keys_only"
        NO_SPECIFIC = "general"

    def __init__(self,
                 flag: Type = Type.NO_SPECIFIC):
        """
        Инициализирует self.
        """
        super().__init__()
        self.type = flag

    def __repr__(self):
        """
        Возвращает отладочное представление данных.
        """
        return f"MetaData(hints={self.hints}, type={self.type})"

    def __str__(self):
        """
        Возвращает читаемое строковое представление данных.
        """
        return f"(hints={self.hints}, type={self.type})"

    def to_dict(self):
        """
        Возвращает представление данных в виде json.
        """
        return {
            "hints": self.hints,
            "type": self.type.value
        }

    def reset_state(self):
        """
        Сбрасывает состояние объекта до состояния по умолчанию.
        Вызывает родительский метод сброса и дополняет его.
        """
        warer.WarerObject.reset_hints(self)
        self.reset_specific()

    def from_dict(self, obj: dict):
        """
        Инициализирует данные из json.

        Аргументы:
            obj (dict): словарь для копирования.
        """
        self.reset_hints()
        for key, value in obj.items():
            self.set_hint(key, value)

    def set_hints(self, obj: dict):
        """
        Объединяет поля из obj с полями self.hints.

        При совпадении ключей - переписывает.
        Похож на self.from_dict.

        Аргументы:
            obj (dict): словарь для копирования.
        """
        for key, value in obj.items():
            self.set_hint(key, value)

    def reset_hints_in(self,
                       keys,
                       *,
                       set_none: bool = False):
        """
        Удаляет или очищает значения ключей из keys.

        При очистке ключи устанавливаются в None, при удалении — удаляются из hints.
        Несуществующие ключи игнорируются.

        Аргументы:
            keys: ключи для удаления (очищения).
            set_none (bool): если True, то не удаляет, а устанавливает в None.
        """
        for key in keys:
            if set_none:
                self.hints[key] = None
            else:
                self.hints.pop(key, None)

    def reset_specific(self):
        """
        Обобщает содержимое объекта до "общего", не специального.
        Эквивалентно вызову self.set_specific с параметром по умолчанию.
        """
        self.type = self.Type.NO_SPECIFIC

    def set_specific(self, flag: Type=Type.NO_SPECIFIC):
        """
        Добавляет объекту спецификацию.
        Полезно при передаче объекта, чтобы уточнить содержимое.

        Аргументы:
            flag (MetaData.Type): специальный спецификатор, см MetaData.Type
        """
        self.type = flag



if __name__ == "__main__":
    print("Объект хранения дополнительных данных:")
    help(MetaData)

    print("Пример использования класса:")
    data = MetaData()
    data.set_hint("номер", 1)
    data.set_hint("имя", "Данила")
    print(data)

    print("Добавим поля:")
    data.set_hint("посещение", 23)
    data.set_hint("возраст", 20)
    data.set_specific(MetaData.Type.INT_ONLY)
    print(data)
    print()

    print("Результат метода __repr__: ", data.__repr__())
    print()

    print("Сбросим состояние:")
    data.reset_state()
    print(data)
    print()

    print("Пример работы метода reset_hints_in:")
    data.set_hints({"посещения":1, "имя":"Данила", "возраст":20})
    print("data: ", data)
    print("-"*15)

    print("очистим, а потом удалим два поля: (имя, посещения)")
    data.reset_hints_in(["имя", "посещения"], set_none=True)
    print("очищенные поля: ", data)
    data.reset_hints_in(["имя", "посещения"])
    print("удаленные поля: ", data)
