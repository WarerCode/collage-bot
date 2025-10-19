"""
Определяет класс ContentPolicy для работы с политикой на основе метаданных.

Класс использует подсказки (hints) из объекта MetaData и предоставляет
методы для строкового представления и преобразования в словарь.
"""

import enum

import core.warerobjects.politics.basepolicy as policy
import core.warerobjects.data.metadata as metadata


class Hints(enum.Enum):
    """

    """

    class CaptionFormats(enum.Enum):
        """

        """
        HTML = "html",
        MARKED_DOWN = "marked_down",
        NO_FORMAT = "no_format"

    HIDDEN_IMAGE = "hidden_image",
    NO_CAPTION = "no_caption",
    CAPTION_UPPER_IMAGE = "caption_upper_image",
    IMAGE_PATHS = "image_paths",
    CAPTION_FORMAT = "caption_format"

    def __str__(self):
        """

        """
        return self.value

# триггер - величина, имеющая два значения
TRIGGERS = {
    Hints.HIDDEN_IMAGE: "has_spoiler",
    Hints.NO_CAPTION: Hints.NO_CAPTION.value
}


class ContentPolicy(policy.Policy):
    """
    Класс ContentPolicy представляет политику обработки содержимого,
    основанную на метаданных медиа-данных.

    Родители:
        policy.Policy
        warer.WarerObject
        abc.ABC

    Атрибуты:
        data (dict): Словарь подсказок (hints) из метаданных,
                     определяющий параметры политики.
    """

    MediaData = metadata.MetaData

    def __init__(self, media_data: MediaData):
        """
        Инициализирует объект ContentPolicy с использованием
        метаданных медиа-данных.

        Args:
            media_data (MediaData): Объект метаданных, содержащий hints.
        """
        super().__init__()
        self.data = media_data.hints

    def __str__(self):
        """
        Возвращает удобочитаемое строковое представление политики,
        отображающее ключевые подсказки.
        """
        return f"ContentPolicy(data={self.data!r})"

    def __repr__(self):
        """
        Возвращает подробное строковое представление объекта,
        пригодное для отладки.
        """
        return f"(data={self.data!r})"

    def to_dict(self):
        """
        Преобразует политику в словарь для сериализации
        или передачи.
        """
        return dict(self.data)  # копия словаря hints

    def __getitem__(self, item):
        """

        """
        return self.data.get(item)


if __name__ == "__main__":
    help(ContentPolicy)

    data = MetaData()
    data.set_hint(Hints.HIDDEN_IMAGE, False)
    data.set_hint(Hints.CAPTION_UPPER_IMAGE, True)
    data.set_hint(Hints.IMAGE_PATHS, [
        "some_long_path.png","some_long_path_1.png"
    ])
    data.set_hint(Hints.CAPTION_FORMAT, Hints.CaptionFormats.HTML)
    policy = ContentPolicy(data)

    # ContentPolicy(
    #   "hidden_image": False,
    #   "caption_upper_image": True,
    #   "image_paths": [
    #       "some_long_path.png",
    #       "some_long_path_1.png"
    #       ]
    #   "caption_format": CaptionFormats.HTML
    # )

    print(policy)
