"""
Здесь описан базовый класс всех классов-медиа. Объекты класса
передаются в качестве контента для сборки сообщения.
"""

import abc

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
