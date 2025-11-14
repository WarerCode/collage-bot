import math
import os
import time
import PIL.Image
import PIL.ImageSequence
import typing
import dotenv
import pathlib
import random

import core.warerobjects.content_types.base_type as base_type
import core.warerobjects.politics.size_policy as size_policy
import core.warerobjects.content_types.meta.effects as effects
import core.warerobjects.content_types.image as content_image

class Gif(content_image.Image):
    """
    Класс описывающий изображение как медиа-объект.

    Атрибуты экземпляра:
        _images: набор изображений типа content_image.Image
        _image: объект изображения PIL
        _file_path: путь к файлу изображения (если загружено из файла)
    """

    def __init__(self, gif_path: str=None, gif: PIL.Image.Image=None):
        """
        Инициализирует объект Gif.

        Параметры:
            gif_path (str): путь к файлу GIF.
            gif (PIL.Image.Image): объект PIL.Image для инициализации.
        """
        super().__init__(image_path=gif_path, image=gif)

    @property
    def frames_count(self) -> int:
        """
        Возвращает количество кадров в gif.
        
        Возвращает:
            int: количество кадров
        """
        return len(list(PIL.ImageSequence.Iterator(self._image)))
    
    def apply_effect(
            self,
            effect_name: effects.EffectNames,
            frame_indexes: list[int] = None,
            is_all_frames: bool = True,
            **kwargs: dict
        ) -> 'Gif':
        """
        КРАЙНЕ НЕ РЕКОМЕНДУЕТСЯ ИСПОЛЬЗОВАТЬ ДАННЫЙ МЕТОД
        Применяет эффект по имени из перечислителя effects.EffectNames

        Аргументы:
            effect_name: название эффекта
            frame_indexes: список индексов кадров для применения эффекта
            is_all_frames: применить ко всем кадрам
            **kwargs: дополнительные параметры для передачи в функцию конкретного эффекта
        Возвращает:
            Gif после применения эффекта
        """

        if effect_name.value not in effects.EFFECT_METHODS:
            raise ValueError(f"Unknown effect: {effect_name}")

        # Получаем все кадры
        frames = []
        durations = []
        
        for i, frame in enumerate(PIL.ImageSequence.Iterator(self._image)):
            # Конвертируем в RGB если нужно (GIF часто в P mode)
            if frame.mode != 'RGB':
                frame = frame.convert('RGB')
            
            frames.append(frame.copy())
            
            # Сохраняем длительность кадра
            duration = frame.info.get('duration', 100)  # default 100ms
            durations.append(duration)

        # Применяем эффекты к выбранным кадрам
        if is_all_frames:
            for i in range(len(frames)):
                frames[i] = effects.EFFECT_METHODS[effect_name.value](frames[i], **kwargs)
        else:
            if frame_indexes is None:
                frame_indexes = [0]  # default to first frame
            
            for i in frame_indexes:
                if 0 <= i < len(frames):
                    frames[i] = effects.EFFECT_METHODS[effect_name.value](frames[i], **kwargs)

        # Создаем новый GIF объект
        if frames:
            # Создаем временный BytesIO для сохранения
            from io import BytesIO
            temp_buffer = BytesIO()
            
            frames[0].save(
                temp_buffer,
                format='GIF',
                save_all=True,
                append_images=frames[1:],
                duration=durations,
                loop=0,
                optimize=False
            )
            
            # Загружаем обратно из буфера
            temp_buffer.seek(0)
            result_gif = PIL.Image.open(temp_buffer)
            
            return Gif(gif=result_gif)
        
        return self
    
    def save(self, file_path: str, format: str = "GIF", **kwargs):
        """
        Сохраняет GIF изображение со всеми кадрами.

        Аргументы:
            file_path (str): путь для сохранения
            format (str): формат сохранения
            **kwargs: дополнительные параметры сохранения
        """
        if not self._image:
            return

        # Создаем директорию если нужно
        self.make_dir(file_path)

        # Проверяем, является ли изображение многокадровым GIF
        frames = PIL.ImageSequence.Iterator(self._image)
        
        # Сохраняем как анимированный GIF
        processed_frames = []
        durations = []
        
        for i, frame in enumerate(frames):
            # Конвертируем в RGB если нужно
            if frame.mode != 'RGB':
                frame = frame.convert('RGB')
            processed_frames.append(frame)

            # Сохраняем длительность кадра
            duration = frame.info.get('duration', 100)  # default 100ms
            durations.append(duration)
        
        # Сохраняем с сохранением анимации
        processed_frames[0].save(
            file_path,
            format=format,
            save_all=True,
            append_images=processed_frames[1:],
            duration=durations,
            loop=0,  # бесконечный цикл
            optimize=True,
            **kwargs
        )

    @property
    def durations(self):
        """
        Получение списка длительностей каждого кадра в миллисекундах.
        """
        frames = list(PIL.ImageSequence.Iterator(self._image))

        durations = []
        
        for frame in frames:
            duration = frame.info.get('duration', 100)
            durations.append(duration)
        
        return durations
    
    @property
    def duration(self):
        """
        Получение общей длительности gif в миллисекундах.
        """        
        return sum(self.durations)

    def __str__(self):
        if self.frames_count:
            return f"Gif(frames_count={self.frames_count}, duration={self.duration})"
        return "Gif(empty)"

    def __repr__(self):
        return self.__str__()

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        return {
            "count": self.frames_count,
            "duration": self.duration,
            "frames": [
                content_image.Image(image=frame).to_dict() for frame in PIL.ImageSequence.Iterator(self._image)
            ],
        }
    
if __name__ == "__main__":
    print("Пример использования класса Gif")

    dotenv.load_dotenv("dev.env")
    MEDIA_ROOT = os.getenv("MEDIA_ROOT")
    ASSETS_ROOT = os.getenv("ASSETS_ROOT")

    gif = Gif(gif_path=os.path.join(ASSETS_ROOT, "test/gif", "1.gif"))

    print(gif)
    print(gif.to_dict())
    print(gif.frames_count)
    print(gif.duration)

    test_size_policy = size_policy.SizePolicy(size_policy.SizePolicy.Size.SQUARE)

    for effect_name in [effects.EffectNames.GRAY]:
        print(effect_name)
        old_time = time.time()
        new_gif = gif.apply_effect(
            effect_name = effect_name,
            kwargs = {"shape": test_size_policy.size.value} # Не рекомендуется указывать политику размера для гифки
        )
        print(time.time() - old_time)
        new_gif.save(os.path.join(MEDIA_ROOT, "gif/effects", f"gif_{effect_name.name}.gif"))

    