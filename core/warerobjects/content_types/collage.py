import math
import os
import time
import PIL.Image
import typing
import dotenv
import pathlib
import random

import core.warerobjects.content_types.base_type as base_type
import core.warerobjects.politics.size_policy as size_policy
import core.warerobjects.content_types.meta.effects as effects
import core.warerobjects.content_types.image as content_image

class Collage(content_image.Image):
    """
    Класс описывающий изображение как медиа-объект.

    Атрибуты экземпляра:
        _images: набор изображений типа content_image.Image
        _image: объект изображения PIL
        _file_path: путь к файлу изображения (если загружено из файла)
    """

    def __init__(self, image_path: str=None, image: PIL.Image.Image=None, list_of_images: list[content_image.Image] = None):
        """
        Инициализирует объект коллажа

        Параметры:
            image_path (str): путь к файлу изображения
            image (PIL.Image.Image): объект изображения PIL
            list_of_images (list): набор изображений
        """
        super().__init__(image_path=image_path, image=image)
        self._images = [] if list_of_images == None else list_of_images

    def create_collage(self, size_policy: size_policy.SizePolicy, effects_data: list[dict]=None) -> content_image.Image:
        """
        Создает коллаж из списка изображений.

        Аргументы:
            size_policy (SizePolicy): политика размера и соотношения сторон
            effects_data (list): список параметров эффектов (название эффекта и параметры)

        Возвращает:
            Image: объект изображения коллажа
        """
        if not self._images:
            return None

        # Получаем соотношение сторон из size_policy
        aspect_ratio = size_policy.size.aspect_ratio
        
        # Определяем оптимальное расположение изображений
        rows, cols = self._calculate_grid_layout(len(self._images), aspect_ratio)

        size_scaler = size_policy.size.scaler

        canvas_size = (size_scaler*size_policy.size.value[0], size_scaler*size_policy.size.value[1])

        cell_size = (math.ceil(canvas_size[0] / cols), math.ceil(canvas_size[1] / rows))
        
        # Подготавливаем изображения
        prepared_images = self._prepare_images_for_collage(cell_size)

        # Создаем холст для коллажа
        collage_canvas = PIL.Image.new('RGB', canvas_size, 'white')
        
        # Размещаем изображения на холсте
        final_collage = self._arrange_images_on_canvas(collage_canvas, prepared_images, rows, cols, k=1.2)
        final_collage = content_image.Image(image=final_collage)

        if effects_data != None:
            for data in effects_data:
                effect = data.get("effect")
                kwargs = data.get("kwargs")
                if effect != None:
                    if kwargs != None:
                        final_collage = final_collage.apply_effect(effect_name=effect, **kwargs)
                    else:
                        final_collage = final_collage.apply_effect(effect_name=effect)

        self.image = final_collage.image
        
        return final_collage

    def _calculate_grid_layout(self, image_count: int, aspect_ratio: float) -> tuple[int, int]:
        """
        Вычисляет оптимальное количество строк и столбцов для сетки.
        
        Аргументы:
            image_count (int): количество изображений
            aspect_ratio (float): желаемое соотношение сторон коллажа
            
        Возвращает:
            tuple: (rows, cols) - количество строк и столбцов
        """
        if image_count <= 0:
            return 0, 0
            
        # Начинаем с квадратного расположения
        cols = math.floor(math.sqrt(image_count))
        rows = image_count // cols
        
        # Корректируем с учетом соотношения сторон
        current_ratio = cols / rows
        
        if abs(current_ratio - aspect_ratio) > 0.5:
            cols, rows = rows, cols
        
        return rows, cols

    def _prepare_images_for_collage(self, cell_size: tuple[int, int]) -> list[PIL.Image.Image]:
        """
        Подготавливает изображения для коллажа (изменяет размер).
        
        Аргументы:
            cell_size (tuple): размеры ячейки в пикселях
            
        Возвращает:
            list: список подготовленных изображений PIL
        """
        if not self._images:
            return []
            
        prepared_images = []
        for img in self._images:
            if img.image:
                # Изменяем размер изображения с сохранением пропорций
                resized_img = self._resize_image_to_fit(img.image, cell_size)
                prepared_images.append(resized_img)
        
        return prepared_images

    def _resize_image_to_fit(self, image: PIL.Image.Image, cell_size: tuple[int, int]) -> PIL.Image.Image:
        """
        Изменяет размер изображения с сохранением пропорций и обрезкой по центру.
        
        Аргументы:
            image (PIL.Image.Image): исходное изображение
            cell_size (tuple): размеры ячейки в пикселях
            
        Возвращает:
            PIL.Image.Image: изображение с измененным размером
        """
        # Вычисляем соотношения
        img_ratio = image.width / image.height
        cell_ratio = cell_size[0] / cell_size[1]
        
        if img_ratio > cell_ratio:
            # Изображение шире целевого - обрезаем по бокам
            new_height = cell_size[1]
            new_width = math.ceil(new_height * img_ratio)
            resized = image.resize((new_width, new_height), PIL.Image.Resampling.LANCZOS)
            
            # Обрезаем по центру
            left = (new_width - cell_size[0]) // 2
            top = new_height
            right = left + cell_size[0]
            bottom = 0
            return resized.crop((left, bottom, right, top))
        else:
            # Изображение выше целевого - обрезаем сверху и снизу
            new_width = cell_size[0]
            new_height = math.ceil(new_width / img_ratio)
            resized = image.resize((new_width, new_height), PIL.Image.Resampling.LANCZOS)
            
            # Обрезаем по центру
            left = 0
            bottom = (new_height - cell_size[1]) // 2
            right = new_width
            top = bottom + cell_size[1]
            return resized.crop((left, bottom, right, top))

    def _arrange_images_on_canvas(self, canvas: PIL.Image.Image,
                                 prepared_images: list[PIL.Image.Image],
                                 rows: int, cols: int, k: float=1.1, shuffle: bool=True) -> PIL.Image.Image:
        """
        Размещает изображения на холсте.
        
        Аргументы:
            canvas (PIL.Image.Image): холст для коллажа
            prepared_images (list): список подготовленных изображений
            rows (int): количество строк
            cols (int): количество столбцов
            k (float): коэффициент масштабирования отдельной фотографии
            shuffle (bool): нужно ли перемешивать фотографии
            
        Возвращает:
            PIL.Image.Image: готовый коллаж
        """
        if not canvas or not prepared_images:
            return canvas
            
        result = canvas.copy()
        cell_width = prepared_images[0].width
        cell_height = prepared_images[0].height

        if shuffle:
            random.shuffle(prepared_images)

        prepared_images = prepared_images[:rows * cols]
        indexes = list(range(0, len(prepared_images)))
        random.shuffle(indexes)
        
        # Размещаем изображения на холсте
        for i in indexes:
            img = prepared_images[i]

            row = i // cols
            col = i % cols
            
            x = col * cell_width
            y = row * cell_height

            if random.randint(0, 1) == 1:
                img = content_image.Image(image=img).scale(k).image

                x -= (img.width - cell_width) // 2
                y -= (img.height - cell_height) // 2
            
            result.paste(img, (x, y))
        
        return result

    def add_image(self, image: content_image.Image) -> None:
        """
        Добавляет изображение в коллаж.
        
        Аргументы:
            image (Image): объект изображения для добавления
        """
        self._images.append(image)

    def clear_images(self) -> None:
        """
        Очищает список изображений коллажа.
        """
        self._images.clear()

    @property
    def images_count(self) -> int:
        """
        Возвращает количество изображений в коллаже.
        
        Возвращает:
            int: количество изображений
        """
        return len(self._images)

    def __str__(self):
        if self._images:
            return f"Collage(images_count={self.images_count})"
        return "Collage(empty)"

    def __repr__(self):
        return self.__str__()

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        return {
            "count": self.images_count,
            "images": [
                image.to_dict() for image in self._images
            ],
        }
    
if __name__ == "__main__":
    print("Пример использования класса Collage")

    dotenv.load_dotenv("dev.env")
    MEDIA_ROOT = os.getenv("MEDIA_ROOT")
    ASSETS_ROOT = os.getenv("ASSETS_ROOT")

    collage = Collage()

    for i in range(10):
        collage.add_image(content_image.Image(image_path=os.path.join(ASSETS_ROOT, "test/collage", f"{i+1}.jpg")))

    print(collage)
    print(collage.to_dict())

    for size in size_policy.SizePolicy.Size:
        test_size_policy = size_policy.SizePolicy(size)

        collage_image = collage.create_collage(size_policy=test_size_policy)
        collage_image.save(os.path.join(MEDIA_ROOT, "collage/sizes", f"collage_{size.name}.jpg"))

    test_size_policy = size_policy.SizePolicy(size_policy.SizePolicy.Size.SQUARE)

    for effect_name in effects.EffectNames:
        print(effect_name)
        old_time = time.time()
        collage_image = collage.create_collage(
            size_policy=test_size_policy, 
            effects_data=[{"effect": effect_name, "kwargs": {"shape": test_size_policy.size.value}}]
        )
        print(time.time() - old_time)
        collage_image.save(os.path.join(MEDIA_ROOT, "collage/effects", f"collage_{effect_name.name}.jpg"))

    