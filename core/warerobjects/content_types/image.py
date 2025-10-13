import os
import PIL.Image
import typing
import dotenv
import pathlib

import core.warerobjects.content_types.base_type as base_type
import core.warerobjects.politics.size_policy as size_policy
import core.warerobjects.content_types.meta.effects as effects

dotenv.load_dotenv("dev.env")
MEDIA_ROOT = os.getenv("MEDIA_ROOT")
ASSETS_ROOT = os.getenv("ASSETS_ROOT")

class Image(base_type.BaseMediaType):
    """
    Класс описывающий изображение как медиа-объект.

    Атрибуты экземпляра:
        _image: объект изображения PIL
        _file_path: путь к файлу изображения (если загружено из файла)
    """

    def __init__(self, image_path: str=None, image: PIL.Image.Image=None):
        """
        Инициализирует объект изображения

        Параметры:
            image_path (str): путь к файлу изображения
            image (PIL.Image.Image): объект изображения PIL
        """
        super().__init__()
        if image_path != None and image == None:
            self._image = PIL.Image.open(image_path)
        else:
            self._image = image
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
    def size(self) -> typing.Tuple[int, int]:
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

    def resize(self, size: typing.Tuple[int, int], resample: int = PIL.Image.Resampling.LANCZOS) -> 'Image':
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
        return Image(image=resized_image)

    def crop(self, box: typing.Tuple[int, int, int, int]) -> 'Image':
        """
        Обрезает изображение по заданной области.

        Аргументы:
            box (tuple): область обрезки (left, lower, right, upper)

        Возвращает:
            Image: новый объект изображения
        """
        if not self._image:
            return self
        
        cropped_image = self._image.crop(box)
        return Image(image=cropped_image)

    def rotate(self, angle: float, expand: bool = True) -> 'Image':
        """
        Поворачивает изображение на заданный угол против часовой стрелки.

        Аргументы:
            angle (float): угол поворота в градусах
            expand (bool): увеличивать ли холст для полного отображения

        Возвращает:
            Image: новый объект изображения
        """
        if not self._image:
            return self
        
        rotated_image = self._image.rotate(angle, expand=expand)
        return Image(image=rotated_image)

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
        return Image(image=converted_image)

    def get_pixel_data(self) -> typing.Optional[typing.Any]:
        """
        Получает данные пикселей изображения.

        Возвращает:
            typing.Any: данные пикселей или None если изображение не загружено
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
            dirs = file_path.split("\\")
            file_dir = file_path
            if "." in dirs[-1]:
                file_dir = r"\\".join(dirs[:-1])
            pathlib.Path(file_dir).mkdir(parents=True, exist_ok=True)
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

    def apply_effect(self,
                     effect_name: str,
                     **kwargs: dict) -> 'Image':
        """
        Применяет эффект по имени из перечислителя effects.EffectNames

        Аргументы:
            effect_name: название эффекта
            **kwargs: дополнительные параметры для передачи в функцию конкретного эффекта
        Возвращает:
            Изображение после применения эффекта
        """

        if effect_name not in effects.EFFECT_METHODS:
            raise ValueError(f"Unknown effect: {effect_name}")
        
        new_image = effects.EFFECT_METHODS[effect_name](self._image, **kwargs)
        
        return Image(image=new_image)

    def __str__(self):
        if self._image:
            return f"Image({self.width}x{self.height}, {self.format}, {self.mode})"
        return "Image(empty)"

    def __repr__(self):
        return self.__str__()

    def to_dict(self) -> typing.Dict[str, typing.Any]:
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
        my_image = Image(image_path=os.path.join(ASSETS_ROOT, "test", "effects_test.jpg"))
        image_1_1 = Image(image_path=os.path.join(ASSETS_ROOT, "test", "1_1.jpg"))
        image_1_2 = Image(image_path=os.path.join(ASSETS_ROOT, "test", "1_2.jpg"))
        
        print(f"Размер изображения: {my_image.size}")
        print(f"Формат: {my_image.format}")
        print(f"Цветовой режим: {my_image.mode}")
        
        # Изменение размера
        resized = my_image.resize((300, 200))
        print(f"Новый размер: {resized.size}")
        resized.save(os.path.join(MEDIA_ROOT, "test", "resized.jpg"))

        # Поворот изображения
        rotated = my_image.rotate(90)
        rotated.save(os.path.join(MEDIA_ROOT, "test", "rotated.jpg"))
        
        # Обрезка изображения
        crop_frame = (0, my_image.height // 2 - 100, my_image.width, my_image.height // 2 + 100)
        croped = my_image.crop(crop_frame)
        croped.save(os.path.join(MEDIA_ROOT, "test", "croped.jpg"))

        # Применение одного эффекта
        for eff in effects.EffectNames:
            try:
                new_image = my_image.apply_effect(eff.value)
                new_image.save(os.path.join(MEDIA_ROOT, "effects", f"{eff.value}.jpg"))
            except Exception as e:
                print(e)
                continue

        # Тест эффектов-рамок
        one_image = image_1_1.apply_effect(effects.EffectNames.LEAFES_FRAME.value, **{"shape": size_policy.SizePolicy.Size.SQUARE.value})
        one_image.save(os.path.join(MEDIA_ROOT, "effects", f"{effects.EffectNames.LEAFES_FRAME.value}.jpg"))

        one_image = image_1_2.apply_effect(effects.EffectNames.GOTH_FRAME.value, **{"shape": size_policy.SizePolicy.Size.VERTICAL.value})
        one_image.save(os.path.join(MEDIA_ROOT, "effects", f"{effects.EffectNames.GOTH_FRAME.value}.jpg"))

        one_image = my_image.apply_effect(effects.EffectNames.PLAIN_FRAME.value, **{"border_size": 20, "color": (100, 100, 255)})
        one_image.save(os.path.join(MEDIA_ROOT, "effects", f"{effects.EffectNames.PLAIN_FRAME.value}.jpg"))
        
    except FileNotFoundError as e:
        print(e)
    except Exception as e:
        print(f"Ошибка при работе с изображением: {e}")