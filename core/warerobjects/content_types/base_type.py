"""
Здесь описан базовый класс всех классов-медиа. Объекты класса
передаются в качестве контента для сборки сообщения.
"""

import abc
import os
import pathlib

import core.warerobjects.warerobject as warer
import core.warerobjects.politics.content_policy as content_policy


class BaseMediaType(warer.WarerObject):
    """
    Базовый класс Медиа-объекта. Предоставляет интерфейс
    полиморфной трансформации в зависимости от политики.

    Родители:
        abc.ABC
        warer.WarerObject
    """

    def __init__(self):
        """
        Инициализирует self.
        """
        super().__init__()

    def make_dir(self, file_path: str) -> None:
        """
        Создаёт директорию если нужно.
        """
        if file_path:
            dirs = file_path.split("\\")
            file_dir = file_path
            if "." in dirs[-1]:
                file_dir = r"\\".join(dirs[:-1])
            pathlib.Path(file_dir).mkdir(parents=True, exist_ok=True)

    # @abc.abstractmethod
    # def apply_policy(self, policy: content_policy.ContentPolicy) -> 'BaseMediaType':
    #     """
    #     Возвращает объект с тем же содержимым, но соответствующем политике.
    #     Например: объект фото может вернуть кадрированный экземпляр;
    #     объект текста может вернуть форматированный (жирный) текст.

    #     Параметры:
    #         policy: это класс политики контента, наиболее полно описывает
    #         как должно выглядеть сообщение (фото выше текста, форматы текста и т.д.)
    #     """
    #     pass



if __name__ == "__main__":
    help(BaseMediaType)
