"""
Здесь описаны служебные перечислители для метаинформации о медиа файлах
и поддерживаемых типов медиа-контента.
"""

import enum

class MediaHints(enum.Enum):
    """
    Перечислитель для значений метаполей.
    """

    COUNT = "count"
    MEDIA_GROUP_ID = "media_group_id"
    FILE_ID = "file_id"

class MediaType(enum.Enum):
    """
    Перечислитель для поддерживаемых типов медиа-данных.
    """

    PHOTO = "photo"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"



if __name__ == "__main__":
    help(MediaHints)
    help(MediaType)
