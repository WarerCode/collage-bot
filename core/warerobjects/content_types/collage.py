import math
import os
import PIL.Image
import typing
import dotenv
import pathlib

import core.warerobjects.content_types.base_type as base_type
import core.warerobjects.politics.size_policy as size_policy
import core.warerobjects.content_types.meta.effects as effects
import core.warerobjects.content_types.image as content_image

class Collage(content_image.Image):
    """
    Класс описывающий изображение как медиа-объект.

    Атрибуты экземпляра:
        _image: объект изображения PIL
        _file_path: путь к файлу изображения (если загружено из файла)
    """

    def __init__(self, image_path: str=None, image: PIL.Image.Image=None, list_of_images: list[content_image.Image] = None):
        """
        Инициализирует объект изображения

        Параметры:
            image_path (str): путь к файлу изображения
            image (PIL.Image.Image): объект изображения PIL
        """
        super().__init__(image_path=image_path, image=image)
        self._images = [] if list_of_images == None else list_of_images

    def create_collage(self, size_policy: size_policy.SizePolicy, effects: list[effects.EffectNames]=None) -> content_image.Image:
        """
        Создает коллаж из списка изображений.

        Аргументы:
            effects (list): список эффектов (пока не используется)
            size_policy (SizePolicy): политика размера и соотношения сторон

        Возвращает:
            Image: объект изображения коллажа
        """
        if not self._images:
            return None

        # Получаем соотношение сторон из size_policy
        aspect_ratio = size_policy.size.aspect_ratio
        print(aspect_ratio)
        
        # Определяем оптимальное расположение изображений
        rows, cols = self._calculate_grid_layout(len(self._images), aspect_ratio)

        size_scaler = size_policy.size.scaler

        canvas_size = (size_scaler*size_policy.size.value[0], size_scaler*size_policy.size.value[1])

        cell_size = (canvas_size[0] // cols, canvas_size[1] // rows)
        
        # Подготавливаем изображения
        prepared_images = self._prepare_images_for_collage(cell_size)

        # Создаем холст для коллажа
        collage_canvas = PIL.Image.new('RGB', canvas_size, 'white')
        
        # Размещаем изображения на холсте
        final_collage = self._arrange_images_on_canvas(collage_canvas, prepared_images, rows, cols)
        
        return content_image.Image(image=final_collage)

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
        cols = math.ceil(math.sqrt(image_count))
        rows = math.ceil(image_count / cols)

        print(cols)
        print(rows)
        
        # Корректируем с учетом соотношения сторон
        current_ratio = cols / rows
        
        if current_ratio < aspect_ratio:
            # Нужно больше столбцов для более широкого формата
            if rows*cols > image_count:
                rows -= 1
            else:
                while cols / rows < aspect_ratio and cols * rows >= image_count:
                    cols += 1
                    rows = math.ceil(image_count / cols)
        else:
            # Нужно больше строк для более высокого формата
            if rows*cols > image_count:
                cols -= 1
            else:
                while cols / rows > aspect_ratio and cols * rows >= image_count:
                    rows += 1
                    cols = math.ceil(image_count / rows)

        print(cols)
        print(rows)
        
        return rows, cols

    def _prepare_images_for_collage(self, cell_size: tuple[int, int]) -> list[PIL.Image.Image]:
        """
        Подготавливает изображения для коллажа (изменяет размер).
        
        Аргументы:
            rows (int): количество строк в сетке
            cols (int): количество столбцов в сетке
            aspect_ratio (float): соотношение сторон коллажа
            
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
            target_width (int): целевая ширина
            target_height (int): целевая высота
            
        Возвращает:
            PIL.Image.Image: изображение с измененным размером
        """
        # Вычисляем соотношения
        img_ratio = image.width / image.height
        cell_ratio = cell_size[0] / cell_size[1]
        
        if img_ratio > cell_ratio:
            # Изображение шире целевого - обрезаем по бокам
            new_height = cell_size[1]
            new_width = int(new_height * img_ratio)
            resized = image.resize((new_width, new_height), PIL.Image.Resampling.LANCZOS)
            
            # Обрезаем по центру
            left = (new_width - cell_size[0]) // 2
            top = cell_size[1]
            right = left + cell_size[0]
            bottom = 0
            return resized.crop((left, bottom, right, top))
        else:
            # Изображение выше целевого - обрезаем сверху и снизу
            new_width = cell_size[0]
            new_height = int(new_width / img_ratio)
            resized = image.resize((new_width, new_height), PIL.Image.Resampling.LANCZOS)
            
            # Обрезаем по центру
            left = 0
            bottom = (new_height - cell_size[1]) // 2
            right = cell_size[0]
            top = bottom + cell_size[1]
            return resized.crop((left, bottom, right, top))

    def _arrange_images_on_canvas(self, canvas: PIL.Image.Image,
                                 prepared_images: list[PIL.Image.Image],
                                 rows: int, cols: int) -> PIL.Image.Image:
        """
        Размещает изображения на холсте.
        
        Аргументы:
            canvas (PIL.Image.Image): холст для коллажа
            prepared_images (list): список подготовленных изображений
            rows (int): количество строк
            cols (int): количество столбцов
            
        Возвращает:
            PIL.Image.Image: готовый коллаж
        """
        if not canvas or not prepared_images:
            return canvas
            
        result = canvas.copy()
        cell_width = prepared_images[0].width
        cell_height = prepared_images[0].height
        
        # Вычисляем отступы для центрирования
        total_used_width = cell_width * cols
        total_used_height = cell_height * rows
        offset_x = (canvas.width - total_used_width) // 2
        offset_y = (canvas.height - total_used_height) // 2
        
        # Размещаем изображения на холсте
        for i, img in enumerate(prepared_images):
            if i >= rows * cols:
                break  # Не размещаем больше, чем есть ячеек
                
            row = i // cols
            col = i % cols
            
            x = offset_x + col * cell_width
            y = offset_y + row * cell_height
            
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
    print("Пример использования класса Collage")

    dotenv.load_dotenv("dev.env")
    MEDIA_ROOT = os.getenv("MEDIA_ROOT")
    ASSETS_ROOT = os.getenv("ASSETS_ROOT")

    collage = Collage()

    for i in range(10):
        collage.add_image(content_image.Image(image_path=os.path.join(ASSETS_ROOT, "test/collage", f"{i+1}.jpg")))

    for size in size_policy.SizePolicy.Size:
        test_size_policy = size_policy.SizePolicy(size)

        collage_image = collage.create_collage(size_policy=test_size_policy)
        collage_image.save(os.path.join(MEDIA_ROOT, "collage", f"collage_{size}.jpg"))