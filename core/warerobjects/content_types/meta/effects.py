import enum
import os
import numpy as np
import dotenv
import PIL
import PIL.Image
import PIL.ImageFilter
import PIL.ImageEnhance
import core.warerobjects.warerobject as warer


dotenv.load_dotenv("dev.env")
MEDIA_ROOT = os.getenv("MEDIA_ROOT")
ASSETS_ROOT = os.getenv("ASSETS_ROOT")
FRAMES_ROOT = os.path.join(ASSETS_ROOT, "frames")

class EffectNames(enum.Enum):
    """
    Список названий эффектов
    """
    GRAY = "grayscale"
    BLUR = "blur"
    NOISE = "noise"
    VIGNETTE = "vignette"

    VINTAGE_CORE = "vintage_core"
    INDIE_CORE = "indie_core"
    OLD_MONEY_CORE = "old_money_core"
    FAIRY_CORE = "fairy_core"
    GOLDEN_HOUR_CORE = "golden_hour_core"

    LEAFES_FRAME = "leafes_frame"
    PLAIN_FRAME = "plain_frame"
    GOTH_FRAME = "goth_frame"

# Список базовых эффектов
BASE_EFFECTS = [
    EffectNames.GRAY.value,
    EffectNames.BLUR.value,
    EffectNames.NOISE.value,
    EffectNames.VIGNETTE.value,
]

# Список расширенных эффектов
EXTENDED_EFFECTS = BASE_EFFECTS + [
    EffectNames.VINTAGE_CORE.value,
    EffectNames.INDIE_CORE.value,
    EffectNames.OLD_MONEY_CORE.value,
    EffectNames.FAIRY_CORE.value,
    EffectNames.GOLDEN_HOUR_CORE.value,

    EffectNames.LEAFES_FRAME.value,
    EffectNames.PLAIN_FRAME.value,
    EffectNames.GOTH_FRAME.value,
]

class Frames(warer.WarerObject):
    """
    Класс для работы с рамками.

    Поля класса:
        sub_dirs: словарь поддиректорий, где хранятся соответствующие рамки
    
    Поля экземпляра:
        Отсутствуют
    """
    sub_dirs = {
        EffectNames.LEAFES_FRAME.value: "leafes",
        EffectNames.PLAIN_FRAME.value: None,
        EffectNames.GOTH_FRAME.value: "goth"
    }

    def __init__(self):
        """
        Инициализация объекта.
        """
        super().__init__()

    @classmethod
    def get_file_name(cls, size: tuple, separator: str="_"):
        """
        Получение имени файла рамки с расширением

        Аргументы:
            size: кортеж формы рамки, например (16, 9)
            separator: разделитель по которому склеивается кортеж
        Возвращает:
            Строку - название файла с расширением
        """
        return separator.join(list(map(str, size))) + ".png"
    
    def __str__(self):
        """
        Преобразует объект в строку.
        Полезно для отладки или логирования.
        """
        pass

    def __repr__(self):
        """
        Возвращает строковое представление объекта в стиле Python.
        """
        pass

    def to_dict(self):
        """
        Возвращает представление объекта в виде словаря (например, для сериализации в JSON).

        Возвращает:
            dict: словарь, представляющий объект.
        """
        pass

class Effects(warer.WarerObject):
    """
    Класс для работы с эффектами.

    Поля класса:
        Отсутствуют
    
    Поля экземпляра:
        Отсутствуют
    """

    def __init__(self):
        """
        Инициализация объекта.
        """
        super().__init__()

    # Base Effects
    @staticmethod
    def adjust_brightness(image: PIL.Image.Image, factor: float = 1.0) -> PIL.Image.Image:
        """
        Регулировка яркости изображения

        Аргументы:
            image: исходное изображение
            factor: коэффициент 
                - (factor > 1 - ярче)
                - (factor < 1 - темнее)
                - (factor = 1 - исходное)
        Возвращает:
            Изображение после применения эффекта
        """
        enhancer = PIL.ImageEnhance.Brightness(image)
        return enhancer.enhance(factor)

    @staticmethod
    def adjust_contrast(image: PIL.Image.Image, factor: float = 1.0) -> PIL.Image.Image:
        """
        Регулировка контраста изображения

        Аргументы:
            image: исходное изображение
            factor: коэффициент 
                - (factor > 1 - контрастнее)
                - (factor < 1 - бледнее)
                - (factor = 1 - исходное)
        Возвращает:
            Изображение после применения эффекта
        """
        enhancer = PIL.ImageEnhance.Contrast(image)
        return enhancer.enhance(factor)

    @staticmethod
    def adjust_saturation(image: PIL.Image.Image, factor: float = 1.0) -> PIL.Image.Image:
        """
        Регулировка насыщенности изображения

        Аргументы:
            image: исходное изображение
            factor: коэффициент 
                - (factor > 1 - насыщеннее)
                - (factor < 1 - более серое)
                - (factor = 1 - исходное)
        Возвращает:
            Изображение после применения эффекта
        """
        enhancer = PIL.ImageEnhance.Color(image)
        return enhancer.enhance(factor)

    @staticmethod
    def adjust_sharpness(image: PIL.Image.Image, factor: float = 1.0) -> PIL.Image.Image:
        """
        Регулировка резкости изображения

        Аргументы:
            image: исходное изображение
            factor: коэффициент 
                - (factor > 1 - резче)
                - (factor < 1 - мыльнее)
                - (factor = 1 - исходное)
        Возвращает:
            Изображение после применения эффекта
        """
        enhancer = PIL.ImageEnhance.Sharpness(image)
        return enhancer.enhance(factor)

    @staticmethod
    def apply_color_filter(image: PIL.Image.Image, rgb_color: tuple, opacity: float = 0.1) -> PIL.Image.Image:
        """
        Накладывает цветной фильтр на изображение

        Аргументы:
            image: исходное изображение
            rgb_color: кортеж цвета в формате RGB
            opacity: непрозрачность от 0 до 1
        Возвращает:
            Изображение после применения эффекта
        """
        color_filter = PIL.Image.new('RGB', image.size, rgb_color)
        return PIL.Image.blend(image, color_filter, opacity)

    @staticmethod
    def apply_temperature(image: PIL.Image.Image, warmth: float = 0.1, opacity: float=0.1) -> PIL.Image.Image:
        """
        Регулировка температуры изображения

        Аргументы:
            image: исходное изображение
            opacity: непрозрачность от 0 до 1
            warmth: коэффициент 
                - (warmth > 0 - теплее)
                - (warmth < 0 - холоднее)
                - (warmth = 0 - исходное)
        Возвращает:
            Изображение после применения эффекта
        """
        if warmth > 0:
            # Теплые тона (оранжевый/желтый)
            warmth = min(warmth, 1)
            warm_filter = (np.array([255, 200, 0]) * warmth).astype(int)
        else:
            # Холодные тона (синий)
            warmth = abs(warmth)
            warmth = min(warmth, 1)
            warm_filter = (np.array([0, 150, 255]) * warmth).astype(int)
        return Effects.apply_color_filter(image, tuple(warm_filter), opacity)

    # Main Effects
    @staticmethod
    def apply_grayscale(image: PIL.Image.Image, **kwargs) -> PIL.Image.Image:
        """
        Применяет черно-белый фильтр на изображение

        Аргументы:
            image: исходное изображение
        Возвращает:
            Изображение после применения эффекта
        """
        return image.convert('L').convert('RGB')
    
    @staticmethod
    def apply_blur(image: PIL.Image.Image, radius: int = 1.5, **kwargs) -> PIL.Image.Image:
        """
        Применяет размытие на изображение

        Аргументы:
            image: исходное изображение
            radius: радиус размытия 
                - (radius > 0 - мыльнее)
                - (radius = 0 - исходное)
        Возвращает:
            Изображение после применения эффекта
        """
        return image.filter(PIL.ImageFilter.GaussianBlur(radius))
    
    @staticmethod
    def apply_noise(image: PIL.Image.Image, intensity: float = 0.05, **kwargs) -> PIL.Image.Image:
        """
        Применяет шум на изображение

        Аргументы:
            image: исходное изображение
            intensity: интенсивность 
                - (intensity > 0 - шумнее)
                - (intensity = 0 - исходное)
        Возвращает:
            Изображение после применения эффекта
        """
        img_array = np.array(image)
        noise = np.random.normal(0, intensity * 255, img_array.shape)
        noisy_array = np.clip(img_array + noise, 0, 255).astype(np.uint8)
        return PIL.Image.fromarray(noisy_array)
    
    @staticmethod
    def apply_vignette(image: PIL.Image.Image, intensity: float = 0.7, **kwargs) -> PIL.Image.Image:
        """
        Применяет виньетирование (затемнение краев) на изображение

        Аргументы:
            image: исходное изображение
            intensity: интенсивность 
                - (intensity > 0 - темнее)
                - (intensity = 0 - исходное)
        Возвращает:
            Изображение после применения эффекта
        """
        # Конвертируем изображение в массив numpy
        img_array = np.array(image)
        
        # Создаем координатные сетки
        height, width = img_array.shape[:2]
        x = np.linspace(-1, 1, width)
        y = np.linspace(-1, 1, height)
        X, Y = np.meshgrid(x, y)
        
        # Вычисляем расстояния от центра
        dist = np.sqrt(X**2 + Y**2)
        
        # Создаем маску виньетирования
        mask = 1 - dist * intensity
        mask = np.clip(mask, 0, 1)
        
        # Применяем маску к каждому каналу
        if len(img_array.shape) == 3:  # RGB изображение
            mask = mask[:, :, np.newaxis]  # Добавляем dimension для broadcasting
            result_array = (img_array * mask).astype(np.uint8)
        else:  # Grayscale изображение
            result_array = (img_array * mask).astype(np.uint8)
        
        return PIL.Image.fromarray(result_array)
    
    # Core Effects

    @staticmethod
    def apply_vintage_core(image: PIL.Image.Image, **kwargs) -> PIL.Image.Image:
        """
        Винтажный эффект (Vintage Core)

        Аргументы:
            image: исходное изображение
        Возвращает:
            Изображение после применения эффекта
        """
        # Сепия и снижение насыщенности
        result = Effects.apply_color_filter(image, (150, 120, 80), 0.3)
        result = Effects.adjust_saturation(result, 0.8)
        result = Effects.adjust_contrast(result, 1.1)
        result = Effects.apply_noise(result, 0.02)
        return Effects.apply_vignette(result, 0.3)

    @staticmethod
    def apply_indie_core(image: PIL.Image.Image, **kwargs) -> PIL.Image.Image:
        """
        Яркие насыщенные цвета (Indie Core)

        Аргументы:
            image: исходное изображение
        Возвращает:
            Изображение после применения эффекта
        """
        # Максимальная насыщенность и яркость
        result = Effects.adjust_saturation(image, 1.8)  # Очень насыщенные цвета
        result = Effects.adjust_brightness(result, 1.2)  # Ярче
        result = Effects.adjust_contrast(result, 1.3)   # Высокий контраст
        result = Effects.adjust_sharpness(result, 2)          # Четкие края
        return result

    @staticmethod
    def apply_old_money_core(image: PIL.Image.Image, **kwargs) -> PIL.Image.Image:
        """
        Богатые глубокие тона (Old Money Core)

        Аргументы:
            image: исходное изображение
        Возвращает:
            Изображение после применения эффекта
        """
        result = image
        result = Effects.apply_temperature(result, 1, 0.1)
        result = Effects.adjust_saturation(result, 0.93)
        result = Effects.adjust_contrast(result, 0.8)
        result = Effects.adjust_brightness(result, 0.9)
        return result

    @staticmethod
    def apply_fairy_core(image: PIL.Image.Image, **kwargs) -> PIL.Image.Image:
        """
        Мягкие пастельные тона с легким свечением (Fairy Core)

        Аргументы:
            image: исходное изображение
        Возвращает:
            Изображение после применения эффекта
        """
        result = Effects.adjust_saturation(image, 0.6)   # Приглушенные цвета
        result = Effects.adjust_brightness(result, 1.4)  # Очень светлый
        result = Effects.apply_color_filter(result, (255, 220, 255), 0.1)  # Розовый оттенок
        result = Effects.apply_blur(result, 1)  # Легкое размытие для свечения
        return result

    @staticmethod
    def apply_golden_hour_core(image: PIL.Image.Image, **kwargs) -> PIL.Image.Image:
        """
        Теплые тона закатного солнца (Golden Hour Core)

        Аргументы:
            image: исходное изображение
        Возвращает:
            Изображение после применения эффекта
        """
        result = Effects.apply_temperature(image, 0.7)  # Теплые тона
        result = Effects.adjust_brightness(result, 1.1)
        result = Effects.adjust_contrast(result, 1.2)
        return result
    
    # Frames Effects

    @staticmethod
    def apply_leafes_frame(image: PIL.Image.Image, shape: tuple, **kwargs) -> PIL.Image.Image:
        """
        Добавляет рамку с листьями

        Аргументы:
            image: исходное изображение
            shape: кортеж формы рамки, например (16, 9)
        Возвращает:
            Изображение после применения эффекта
        """
        try:
            sub_dir = Frames.sub_dirs[EffectNames.LEAFES_FRAME.value]
            if sub_dir != None:
                file_name = Frames.get_file_name(shape)
            else:
                raise Exception("File not supported for this effect")
            # Загружаем рамку с прозрачностью
            frame = PIL.Image.open(os.path.join(FRAMES_ROOT, sub_dir, file_name)).convert("RGBA")
            
            # Изменяем размер рамки под размер изображения
            frame = frame.resize(image.size, PIL.Image.Resampling.LANCZOS)
            
            # Конвертируем основное изображение в RGBA
            image_rgba = image.convert("RGBA")
            
            # Накладываем рамку поверх изображения
            result = PIL.Image.alpha_composite(image_rgba, frame)
            
            return result.convert("RGB")
            
        except Exception as e:
            # Fallback: простая зеленая рамка если файл не найден
            print(e)
            border_size = 30
            frame_color = (34, 139, 34)
            return PIL.ImageOps.expand(image, border=border_size, fill=frame_color)
    
    @staticmethod
    def apply_plain_frame(image: PIL.Image.Image, border_size: int=20, color=(255, 255, 255), **kwargs) -> PIL.Image.Image:
        """
        Простая рамка

        Аргументы:
            image: исходное изображение
            border_size: толщина рамки в пикселях
            color: кортеж цвета рамки в формате RGB
        Возвращает:
            Изображение после применения эффекта
        """
        return PIL.ImageOps.expand(image, border=border_size, fill=color)
    
    @staticmethod
    def apply_goth_frame(image: PIL.Image.Image, shape: tuple, **kwargs) -> PIL.Image.Image:
        """
        Готическая черная рамка

        Аргументы:
            image: исходное изображение
            shape: кортеж формы рамки, например (16, 9)
        Возвращает:
            Изображение после применения эффекта
        """
        try:
            image = Effects.apply_vignette(image)

            sub_dir = Frames.sub_dirs[EffectNames.GOTH_FRAME.value]
            if sub_dir != None:
                file_name = Frames.get_file_name(shape)
            else:
                raise Exception("File not supported for this effect")
            # Загружаем рамку с прозрачностью
            frame = PIL.Image.open(os.path.join(FRAMES_ROOT, sub_dir, file_name)).convert("RGBA")
            
            # Изменяем размер рамки под размер изображения
            frame = frame.resize(image.size, PIL.Image.Resampling.LANCZOS)
            
            # Конвертируем основное изображение в RGBA
            image_rgba = image.convert("RGBA")

            # Накладываем рамку поверх изображения
            result = PIL.Image.alpha_composite(image_rgba, frame)
            
            return result.convert("RGB")
            
        except Exception as e:
            # Fallback: простая готическая рамка если файл не найден
            print(e)
            border_size = 40
            framed = PIL.ImageOps.expand(image, border=border_size, fill='black')
            
            # Добавляем внутреннюю тонкую рамку
            inner_border = 5
            framed = PIL.ImageOps.expand(framed, border=inner_border, fill='darkred')
            framed = PIL.ImageOps.expand(framed, border=inner_border, fill='black')
            
            return framed
    
    def __str__(self):
        """
        Преобразует объект в строку.
        Полезно для отладки или логирования.
        """
        pass

    def __repr__(self):
        """
        Возвращает строковое представление объекта в стиле Python.
        """
        pass

    def to_dict(self):
        """
        Возвращает представление объекта в виде словаря (например, для сериализации в JSON).

        Возвращает:
            dict: словарь, представляющий объект.
        """
        pass

EFFECT_METHODS = {
    EffectNames.GRAY.value: Effects.apply_grayscale,
    EffectNames.BLUR.value: Effects.apply_blur,
    EffectNames.NOISE.value: Effects.apply_noise,
    EffectNames.VIGNETTE.value: Effects.apply_vignette,
    
    EffectNames.VINTAGE_CORE.value: Effects.apply_vintage_core,
    EffectNames.INDIE_CORE.value: Effects.apply_indie_core,
    EffectNames.OLD_MONEY_CORE.value: Effects.apply_old_money_core,
    EffectNames.FAIRY_CORE.value: Effects.apply_fairy_core,
    EffectNames.GOLDEN_HOUR_CORE.value: Effects.apply_golden_hour_core,
    
    EffectNames.LEAFES_FRAME.value: Effects.apply_leafes_frame,
    EffectNames.PLAIN_FRAME.value: Effects.apply_plain_frame,
    EffectNames.GOTH_FRAME.value: Effects.apply_goth_frame,
}

if __name__ == "__main__":
    # Пример использования еффектов можно увидеть в core.warerobjects.content_types.image
    pass
