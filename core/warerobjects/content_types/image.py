import os
import PIL.Image
from typing import Tuple, Dict, Any, Optional
import core.warerobjects.content_types.base_type as base_type
import dotenv

dotenv.load_dotenv("dev.env")
ASSETS_ROOT = os.getenv("ASSETS_ROOT")

class Image(base_type.BaseMediaType):
    """
    Класс описывающий изображение как медиа-объект.

    Атрибуты экземпляра:
        _image: объект изображения PIL
        _file_path: путь к файлу изображения (если загружено из файла)
    """

    def __init__(self):
        """
        Инициализирует пустой объект изображения
        """
        super().__init__()
        self._image = None
        self._file_path = None

    def __init__(self, image_path: str):
        """
        Инициализирует объект изображения из файла

        Параметры:
            image_path (str): путь к файлу изображения
        """
        super().__init__()
        self._image = PIL.Image.open(image_path)
        self._file_path = image_path

    @property
    def width(self) -> int:
        """
        Свойство получение ширины изображения.

        Возвращает:
            int: ширина изображения в пикселях
        """
        return self._image.width if self._image else 0

    @property
    def height(self) -> int:
        """
        Свойство получение высоты изображения.

        Возвращает:
            int: высота изображения в пикселях
        """
        return self._image.height if self._image else 0

    @property
    def size(self) -> Tuple[int, int]:
        """
        Свойство получение размера изображения.

        Возвращает:
            tuple: кортеж (ширина, высота)
        """
        return self._image.size if self._image else (0, 0)

    @property
    def format(self) -> str:
        """
        Свойство получение формата изображения.

        Возвращает:
            str: формат изображения (JPEG, PNG, etc.)
        """
        return self._image.format if self._image else None

    @property
    def mode(self) -> str:
        """
        Свойство получение цветового режима изображения.

        Возвращает:
            str: цветовой режим (RGB, RGBA, L, etc.)
        """
        return self._image.mode if self._image else None

    def resize(self, size: Tuple[int, int], resample: int = PIL.Image.Resampling.LANCZOS) -> 'Image':
        """
        Изменяет размер изображения.

        Аргументы:
            size (tuple): новый размер (ширина, высота)
            resample (int): метод ресемплинга

        Возвращает:
            Image: новый объект изображения
        """
        if not self._image:
            return self
        
        resized_image = self._image.resize(size, resample)
        return Image(resized_image)

    def crop(self, box: Tuple[int, int, int, int]) -> 'Image':
        """
        Обрезает изображение по заданной области.

        Аргументы:
            box (tuple): область обрезки (left, upper, right, lower)

        Возвращает:
            Image: новый объект изображения
        """
        if not self._image:
            return self
        
        cropped_image = self._image.crop(box)
        return Image(cropped_image)

    def rotate(self, angle: float, expand: bool = True) -> 'Image':
        """
        Поворачивает изображение на заданный угол.

        Аргументы:
            angle (float): угол поворота в градусах
            expand (bool): увеличивать ли холст для полного отображения

        Возвращает:
            Image: новый объект изображения
        """
        if not self._image:
            return self
        
        rotated_image = self._image.rotate(angle, expand=expand)
        return Image(rotated_image)

    def convert_mode(self, mode: str) -> 'Image':
        """
        Конвертирует изображение в другой цветовой режим.

        Аргументы:
            mode (str): целевой цветовой режим

        Возвращает:
            Image: новый объект изображения
        """
        if not self._image:
            return self
        
        converted_image = self._image.convert(mode)
        return Image(converted_image)

    def get_pixel_data(self) -> Optional[Any]:
        """
        Получает данные пикселей изображения.

        Возвращает:
            Any: данные пикселей или None если изображение не загружено
        """
        return self._image.load() if self._image else None

    def save(self, file_path: str, format: str = None, **kwargs):
        """
        Сохраняет изображение в файл.

        Аргументы:
            file_path (str): путь для сохранения
            format (str): формат сохранения
            **kwargs: дополнительные параметры сохранения
        """
        if self._image:
            self._image.save(file_path, format=format, **kwargs)

    @property
    def image(self) -> PIL.Image.Image:
        """
        Свойство-getter для объекта изображения.

        Возвращает:
            PIL.Image.Image: объект изображения PIL
        """
        return self._image

    @image.setter
    def image(self, value: PIL.Image.Image):
        """
        Свойство-setter для объекта изображения.

        Аргументы:
            value (PIL.Image.Image): новый объект изображения

        Примечание: при перезаписывании изображения путь к нему удаляется!
        """
        self._image = value
        self._file_path = None

    @property
    def file_path(self) -> str:
        """
        Свойство-getter для пути к файлу.

        Возвращает:
            str: путь к файлу изображения
        """
        return self._file_path

    @file_path.setter
    def file_path(self, value: str):
        """
        Свойство-setter для пути к файлу.

        Аргументы:
            value (str): новый путь к файлу
        """
        self._file_path = value

    def __str__(self):
        if self._image:
            return f"Image({self.width}x{self.height}, {self.format}, {self.mode})"
        return "Image(empty)"

    def __repr__(self):
        return self.__str__()

    def to_dict(self) -> Dict[str, Any]:
        """
        Возвращает представление объекта в виде словаря.

        Возвращает:
            dict: словарь с информацией об изображении
        """
        return {
            "width": self.width,
            "height": self.height,
            "size": self.size,
            "format": self.format,
            "mode": self.mode,
            "file_path": self._file_path
        }

if __name__ == "__main__":
    print("Пример использования класса Image:")

    # Создание изображения из файла
    try:
        my_image = Image(os.path.join(ASSETS_ROOT, "test", "1_1.jpg"))
        
        print(f"Размер изображения: {my_image.size}")
        print(f"Формат: {my_image.format}")
        print(f"Цветовой режим: {my_image.mode}")
        
        # Изменение размера
        resized = my_image.resize((300, 200))
        print(f"Новый размер: {resized.size}")
        
    except FileNotFoundError:
        print("Файл example.jpg не найден")
    except Exception as e:
        print(f"Ошибка при работе с изображением: {e}")