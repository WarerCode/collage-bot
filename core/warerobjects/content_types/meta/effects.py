import enum
import numpy as np
import core.warerobjects.warerobject as warer
import abc
import PIL
import PIL.Image
import PIL.ImageFilter
import PIL.ImageEnhance



class EffectNames(enum.Enum):
    """
    TODO:
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

BASE_EFFECTS = [
    EffectNames.GRAY.value,
    EffectNames.BLUR.value,
    EffectNames.NOISE.value,
    EffectNames.VIGNETTE.value,
]

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

class Effects(warer.WarerObject):
    """
    TODO:
    """
    def __init__(self):
        """
        Инициализация объекта.
        """
        super().__init__()

    # Base Effects

    @staticmethod
    def adjust_brightness(image: PIL.Image.Image, factor: float = 1.0) -> PIL.Image.Image:
        """Регулировка яркости (factor > 1 - ярче, < 1 - темнее)"""
        enhancer = PIL.ImageEnhance.Brightness(image)
        return enhancer.enhance(factor)

    @staticmethod
    def adjust_contrast(image: PIL.Image.Image, factor: float = 1.0) -> PIL.Image.Image:
        """Регулировка контраста (factor > 1 - контрастнее)"""
        enhancer = PIL.ImageEnhance.Contrast(image)
        return enhancer.enhance(factor)

    @staticmethod
    def adjust_saturation(image: PIL.Image.Image, factor: float = 1.0) -> PIL.Image.Image:
        """Регулировка насыщенности (factor > 1 - насыщеннее)"""
        enhancer = PIL.ImageEnhance.Color(image)
        return enhancer.enhance(factor)

    @staticmethod
    def adjust_sharpness(image: PIL.Image.Image, factor: float = 1.0) -> PIL.Image.Image:
        """Регулировка резкости (factor > 1 - резче)"""
        enhancer = PIL.ImageEnhance.Sharpness(image)
        return enhancer.enhance(factor)

    @staticmethod
    def apply_color_filter(image: PIL.Image.Image, rgb_color: tuple, opacity: float = 0.1) -> PIL.Image.Image:
        """Накладывает цветной фильтр (opacity от 0 до 1)"""
        color_filter = PIL.Image.new('RGB', image.size, rgb_color)
        return PIL.Image.blend(image, color_filter, opacity)

    @staticmethod
    def apply_temperature(image: PIL.Image.Image, warmth: float = 0.1, opacity: float=0.1) -> PIL.Image.Image:
        """Регулировка цветовой температуры (warmth > 0 - теплее, < 0 - холоднее)"""
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
    def apply_grayscale(image: PIL.Image.Image) -> PIL.Image.Image:
        """Применяет черно-белый фильтр"""
        return image.convert('L').convert('RGB')
    
    @staticmethod
    def apply_blur(image: PIL.Image.Image, radius: int = 2) -> PIL.Image.Image:
        """Применяет размытие по Гауссу"""
        return image.filter(PIL.ImageFilter.GaussianBlur(radius))
    
    @staticmethod
    def apply_noise(image: PIL.Image.Image, intensity: float = 0.05) -> PIL.Image.Image:
        """Добавляет шум к изображению"""
        img_array = np.array(image)
        noise = np.random.normal(0, intensity * 255, img_array.shape)
        noisy_array = np.clip(img_array + noise, 0, 255).astype(np.uint8)
        return PIL.Image.fromarray(noisy_array)
    
    @staticmethod
    def apply_vignette(image: PIL.Image.Image, intensity: float = 0.8) -> PIL.Image.Image:
        """Применяет виньетирование (затемнение краев)"""
        width, height = image.size
        x_center, y_center = width // 2, height // 2
        max_dist = np.sqrt(x_center**2 + y_center**2)
        
        vignette = PIL.Image.new('L', (width, height))
        for x in range(width):
            for y in range(height):
                dist = np.sqrt((x - x_center)**2 + (y - y_center)**2)
                factor = 1 - (dist / max_dist) * intensity
                vignette.putpixel((x, y), int(255 * factor))
        
        return PIL.Image.composite(image, PIL.Image.new('RGB', image.size, 'black'), vignette)
    
    # Core Effects

    @staticmethod
    def apply_vintage_core(image: PIL.Image.Image) -> PIL.Image.Image:
        """Винтажный эффект с сепией"""
        # Сепия и снижение насыщенности
        result = Effects.apply_color_filter(image, (150, 120, 80), 0.3)
        result = Effects.adjust_saturation(result, 0.8)
        result = Effects.adjust_contrast(result, 1.1)
        result = Effects.apply_noise(result, 0.02)
        return Effects.apply_vignette(result, 0.2)

    @staticmethod
    def apply_indie_core(image: PIL.Image.Image) -> PIL.Image.Image:
        """Яркие насыщенные цвета как в детском саду"""
        # Максимальная насыщенность и яркость
        result = Effects.adjust_saturation(image, 1.8)  # Очень насыщенные цвета
        result = Effects.adjust_brightness(result, 1.2)  # Ярче
        result = Effects.adjust_contrast(result, 1.3)   # Высокий контраст
        result = Effects.adjust_sharpness(result, 2)          # Четкие края
        return result

    @staticmethod
    def apply_old_money_core(image: PIL.Image.Image) -> PIL.Image.Image:
        """Богатые глубокие тона с золотым отливом"""
        result = image
        result = Effects.apply_temperature(result, 1, 0.1)
        result = Effects.adjust_saturation(result, 0.93)
        result = Effects.adjust_contrast(result, 0.8)
        result = Effects.adjust_brightness(result, 0.9)
        return result

    @staticmethod
    def apply_fairy_core(image: PIL.Image.Image) -> PIL.Image.Image:
        """Мягкие пастельные тона с легким свечением"""
        result = Effects.adjust_saturation(image, 0.6)   # Приглушенные цвета
        result = Effects.adjust_brightness(result, 1.4)  # Очень светлый
        result = Effects.apply_color_filter(result, (255, 220, 255), 0.1)  # Розовый оттенок
        result = Effects.apply_blur(result, 1)  # Легкое размытие для свечения
        return result

    @staticmethod
    def apply_golden_hour_core(image: PIL.Image.Image) -> PIL.Image.Image:
        """Теплые тона закатного солнца"""
        result = Effects.apply_temperature(image, 0.7)  # Теплые тона
        result = Effects.adjust_brightness(result, 1.1)
        result = Effects.adjust_contrast(result, 1.2)
        return result
    
    # Frames Effects

    @staticmethod
    def apply_leafes_frame(image: PIL.Image.Image) -> PIL.Image.Image:
        """Добавляет рамку с листьями"""
        # Создаем простую зеленую рамку (заглушка)
        border_size = 30
        frame_color = (34, 139, 34)  # Лесной зеленый
        
        # Расширяем изображение с рамкой
        framed = PIL.ImageOps.expand(image, border=border_size, fill=frame_color)
        
        # Можно добавить текстуру листьев здесь
        # Для реального использования нужны PNG с прозрачностью
        
        return framed
    
    @staticmethod
    def apply_plain_frame(image: PIL.Image.Image) -> PIL.Image.Image:
        """Простая белая рамка"""
        border_size = 20
        return PIL.ImageOps.expand(image, border=border_size, fill='white')
    
    @staticmethod
    def apply_goth_frame(image: PIL.Image.Image) -> PIL.Image.Image:
        """Готическая черная рамка с узором"""
        border_size = 40
        framed = PIL.ImageOps.expand(image, border=border_size, fill='black')
        
        # Добавляем внутреннюю тонкую рамку
        inner_border = 5
        framed = PIL.ImageOps.expand(framed, border=inner_border, fill='darkred')
        framed = PIL.ImageOps.expand(framed, border=inner_border, fill='black')
        
        return framed
    
    @classmethod
    def apply_effect(cls, image: PIL.Image.Image, effect_name: str) -> PIL.Image.Image:
        """Применяет эффект по имени"""
        effect_methods = {
            EffectNames.GRAY.value: cls.apply_grayscale,
            EffectNames.BLUR.value: cls.apply_blur,
            EffectNames.NOISE.value: cls.apply_noise,
            EffectNames.VIGNETTE.value: cls.apply_vignette,
            
            EffectNames.VINTAGE_CORE.value: cls.apply_vintage_core,
            EffectNames.INDIE_CORE.value: cls.apply_indie_core,
            EffectNames.OLD_MONEY_CORE.value: cls.apply_old_money_core,
            EffectNames.FAIRY_CORE.value: cls.apply_fairy_core,
            EffectNames.GOLDEN_HOUR_CORE.value: cls.apply_golden_hour_core,
            
            EffectNames.LEAFES_FRAME.value: cls.apply_leafes_frame,
            EffectNames.PLAIN_FRAME.value: cls.apply_plain_frame,
            EffectNames.GOTH_FRAME.value: cls.apply_goth_frame,
        }
        
        if effect_name not in effect_methods:
            raise ValueError(f"Unknown effect: {effect_name}")
        
        return effect_methods[effect_name](image)
    
    @classmethod
    def apply_multiple_effects(cls, image: PIL.Image.Image, effect_names: list) -> PIL.Image.Image:
        """Применяет несколько эффектов последовательно"""
        result = image.copy()
        for effect_name in effect_names:
            result = cls.apply_effect(result, effect_name)
        return result
    
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

if __name__ == "__main__":
    # Пример использования
    effects = Effects()

    # Загрузка изображения
    image = PIL.Image.open("core/assets/effects_test.jpg")

    # Применение одного эффекта
    for eff in EffectNames:
        new_image = effects.apply_effect(image, eff.value)
        new_image.save(f"core/assets/effects_ready/{eff.value}.jpg")

    # eff = EffectNames.GOLDEN_HOUR_CORE
    # one_image = effects.apply_effect(image, eff.value)
    # one_image.save(f"core/assets/effects_ready_one/{eff.value}.jpg")