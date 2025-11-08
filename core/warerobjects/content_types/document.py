import os
import typing
import dotenv
import pathlib
import mimetypes

import core.warerobjects.content_types.base_type as base_type
import core.warerobjects.politics.size_policy as size_policy
import core.warerobjects.content_types.meta.effects as effects

class Document(base_type.BaseMediaType):
    """
    Класс описывающий документ как медиа-объект.

    Атрибуты экземпляра:
        _file_path: путь к файлу документа
        _content: бинарное содержимое документа (опционально)
    """

    def __init__(self, file_path: str = None, content: bytes = None):
        """
        Инициализирует объект документа.

        Параметры:
            file_path (str): путь к файлу документа
            content (bytes): бинарное содержимое документа
        """
        super().__init__()

        self._file_path = file_path
        
        if file_path is not None and os.path.exists(self._file_path):
            with open(self._file_path, 'rb') as file:
                self._content = file.read()
        elif content is not None:
            self._content = content
        else:
            self._content = b''

    @property
    def mime_type(self) -> str:
        """
        Свойство получение MIME-типа документа на основе расширения.

        Возвращает:
            str: MIME-тип документа
        """
        mime_type = "text/plain"

        if self._file_path:
            mime_type, encoding = mimetypes.guess_type(self._file_path)

        return mime_type

    @property
    def file_path(self) -> str:
        """
        Свойство получения пути к файлу документа.

        Возвращает:
            str: путь к файлу документа
        """
        return self._file_path
    
    @file_path.setter
    def file_path(self, new_path: str) -> None:
        """
        Свойство установки пути к файлу документа.

        Возвращает:
            str: путь к файлу документа
        """
        self._file_path = new_path

    @property
    def file_name(self) -> str:
        """
        Свойство получения полного имени файла документа.

        Возвращает:
            str: имя файла документа
        """
        file_name = None

        if self._file_path:
            dirs = self._file_path.split("\\")
            if "." in dirs[-1]:
                file_name = dirs[-1]

        return file_name
    
    @property
    def file_title(self) -> str:
        """
        Свойство получения имени файла документа без расширения.

        Возвращает:
            str: имя файла документа без расширения
        """
        file_title = None

        if self._file_path:
            file_title = os.path.basename(self._file_path)

        return file_title
    
    @property
    def file_extension(self) -> str:
        """
        Свойство получения расширения файла документа.

        Возвращает:
            str: расширение файла документа
        """
        extension = None

        if self.file_name:
            extension = self.file_name.split(".")[-1]

        return extension

    @property
    def file_size(self) -> int:
        """
        Свойство получения размера файла документа.

        Возвращает:
            int: размер файла в байтах
        """
        if self._content:
            return len(self._content)
        elif self._file_path:
            return os.path.getsize(self._file_path) if os.path.exists(self._file_path) else 0
        return 0

    @property
    def file_size_human(self) -> str:
        """
        Свойство получения размера файла в человеко-читаемом формате.

        Возвращает:
            str: размер файла (например, "2.5 MB")
        """
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        size = float(self.file_size)
        
        while size >= 1024 and i < len(size_names) - 1:
            size /= 1024
            i += 1
        
        return f"{size:.2f} {size_names[i]}"

    @property
    def content(self) -> bytes:
        """
        Свойство получения бинарного содержимого документа.

        Возвращает:
            bytes: содержимое документа
        """
        if self._content is not None:
            return self._content
        elif self._file_path is not None and os.path.exists(self._file_path):
            with open(self._file_path, 'rb') as file:
                return file.read()
        else:
            return b''
        
    @content.setter
    def content(self, value: bytes) -> None:
        """
        Свойство установки бинарного содержимого документа.

        Возвращает:
            bytes: содержимое документа
        """
        self._content = value

    def save(self, file_path: str) -> None:
        """
        Сохраняет документ в файл.

        Аргументы:
            file_path (str): путь для сохранения
        """
        if self.content:
            self.make_dir(file_path)
            with open(file_path, 'wb') as file:
                file.write(self.content)

    def exists(self) -> bool:
        """
        Проверяет существование документа (не только по пути).

        Возвращает:
            bool: True если документ существует, иначе False
        """
        if self._file_path:
            return os.path.exists(self._file_path)
        return self._content is not None

    def __str__(self):
        return f"Document(name='{self.file_name}', size={self.file_size_human})"

    def __repr__(self):
        return self.__str__()

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        return {
            "file_name": self.file_name,
            "file_path": self._file_path,
            "file_size": self.file_size,
            "mime_type": self.mime_type,
            "exists": self.exists(),
        }


if __name__ == "__main__":
    print("Пример использования класса Document:")

    dotenv.load_dotenv("dev.env")
    MEDIA_ROOT = os.getenv("MEDIA_ROOT")
    ASSETS_ROOT = os.getenv("ASSETS_ROOT")

    try:
        # Создание документа из файла
        txt_from_file = Document(file_path=os.path.join(ASSETS_ROOT, "test/document", "sample.txt"))
        print(f"Словарное представление: {txt_from_file.to_dict()}")
        doc_from_file = Document(file_path=os.path.join(ASSETS_ROOT, "test/document", "sample.docx"))
        print(f"Словарное представление: {doc_from_file.to_dict()}")
        pdf_from_file = Document(file_path=os.path.join(ASSETS_ROOT, "test/document", "sample.pdf"))
        print(f"Словарное представление: {pdf_from_file.to_dict()}")
        

        doc_from_file.content = b"No world Hello"
        doc_from_file.file_path = os.path.join(ASSETS_ROOT, "test/document", "sample_no.txt")

        print(f"Новое Словарное представление: {doc_from_file.to_dict()}")

        # Сохранение копии
        doc_from_file.save(os.path.join(MEDIA_ROOT, "document", "copy_sample.txt"))

        
        # Создание документа из бинарных данных
        sample_content = b"This is sample text content for a document"
        doc_from_content = Document(content=sample_content)
        
        print()
        print(f"Документ из контента: {doc_from_content}")
        
        # Сохранение документа из контента
        doc_from_content.save(os.path.join(MEDIA_ROOT, "document", "from_content.txt"))
        
    except FileNotFoundError as e:
        print(f"Файл не найден: {e}")
    except Exception as e:
        print(f"Ошибка при работе с документом: {e}")