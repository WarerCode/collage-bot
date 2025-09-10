"""
Модуль хранит объявление базового класса всех политик проекта WarerCode.
"""

import core.warerobjects.warerobject as warer


class Policy(warer.WarerObject):
    """
    Базовый класс всех политик проекта WarerCode.

    Система политик управляет ограничениями и правилами для объектов.

    Родители:
        warer.WarerObject
        abc.ABC
    """
    pass



if __name__ == "__main__":
    print("Базовый класс политик проекта WarerCode:")
    help(Policy)
