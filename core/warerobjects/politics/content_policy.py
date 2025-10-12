"""
Определяет класс ContentPolicy для работы с политикой на основе метаданных.

Класс использует подсказки (hints) из объекта MetaData и предоставляет
методы для строкового представления и преобразования в словарь.
"""
import enum
import core.warerobjects.politics.basepolicy as policy
import core.warerobjects.data.metadata as metadata


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

    class MediaHints(enum.Enum):
        # Общие подсказки
        TEXT_POSITION = "text_position"
        
        # Подсказки для изображений
        IMAGE_HIDE = "image_hide"
        IMAGE_COMPRESS = "image_compress"
        IMAGE_SIZE = "image_size"
        
        # Подсказки для текста
        TEXT_FORMAT = "text_format"
        TEXT_MAX_LENGTH = "text_max_length"
        TEXT_LINK = "text_link"
        
        # Подсказки для GIF
        
        # Подсказки для документов


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


if __name__ == "__main__":
    help(ContentPolicy)
