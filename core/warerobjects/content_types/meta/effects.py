import enum
import numpy as np
import core.warerobjects.warerobject as warer
import abc
import PIL


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

class Effects(abc.ABC):
    """
    TODO:
    """
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
    
    @staticmethod
    def apply_vintage_core(image: PIL.Image.Image) -> PIL.Image.Image:
        """Винтажный эффект с сепией и шумом"""
        # Сепия
        sepia_filter = PIL.Image.new('RGB', image.size, (112, 66, 20))
        vintage = PIL.Image.blend(image, sepia_filter, 0.3)
        
        # Увеличение контраста
        enhancer = PIL.ImageEnhance.Contrast(vintage)
        vintage = enhancer.enhance(1.2)
        
        # Добавление шума
        vintage = PIL.ImageEffects.apply_noise(vintage, 0.03)
        
        # Легкое виньетирование
        vintage = PIL.ImageEffects.apply_vignette(vintage, 0.5)
        
        return vintage
    
    @staticmethod
    def apply_indie_core(image: PIL.Image.Image) -> PIL.Image.Image:
        """Инди-эффект с приглушенными цветами"""
        # Уменьшение насыщенности
        enhancer = PIL.ImageEnhance.Color(image)
        indie = enhancer.enhance(0.7)
        
        # Увеличение яркости
        enhancer = PIL.ImageEnhance.Brightness(indie)
        indie = enhancer.enhance(1.1)
        
        # Легкое размытие
        indie = PIL.ImageEffects.apply_blur(indie, 1)
        
        return indie
    
    @staticmethod
    def apply_old_money_core(image: PIL.Image.Image) -> PIL.Image.Image:
        """Эффект 'старых денег' с золотыми тонами"""
        # Золотистый оттенок
        gold_filter = PIL.Image.new('RGB', image.size, (255, 215, 0))
        money = PIL.Image.blend(image, gold_filter, 0.2)
        
        # Увеличение насыщенности
        enhancer = PIL.ImageEnhance.Color(money)
        money = enhancer.enhance(1.3)
        
        # Высокий контраст
        enhancer = PIL.ImageEnhance.Contrast(money)
        money = enhancer.enhance(1.4)
        
        return money
    
    @staticmethod
    def apply_fairy_core(image: PIL.Image.Image) -> PIL.Image.Image:
        """Сказочный эффект с пастельными тонами"""
        # Осветление
        enhancer = PIL.ImageEnhance.Brightness(image)
        fairy = enhancer.enhance(1.3)
        
        # Пастельные тона (уменьшение насыщенности)
        enhancer = PIL.ImageEnhance.Color(fairy)
        fairy = enhancer.enhance(0.6)
        
        # Легкое свечение (размытие + наложение)
        blurred = PIL.ImageEffects.apply_blur(fairy, 3)
        fairy = PIL.Image.blend(fairy, blurred, 0.2)
        
        return fairy
    
    @staticmethod
    def apply_golden_hour_core(image: PIL.Image.Image) -> PIL.Image.Image:
        """Эффект золотого часа с теплыми тонами"""
        # Теплый оранжевый фильтр
        golden_filter = PIL.Image.new('RGB', image.size, (255, 165, 0))
        golden = PIL.Image.blend(image, golden_filter, 0.25)
        
        # Увеличение яркости и контраста
        enhancer = PIL.ImageEnhance.Brightness(golden)
        golden = enhancer.enhance(1.2)
        
        enhancer = PIL.ImageEnhance.Contrast(golden)
        golden = enhancer.enhance(1.3)
        
        return golden
    
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
            cls.GRAY: cls.apply_grayscale,
            cls.BLUR: cls.apply_blur,
            cls.NOISE: cls.apply_noise,
            cls.VIGNETTE: cls.apply_vignette,
            
            cls.VINTAGE_CORE: cls.apply_vintage_core,
            cls.INDIE_CORE: cls.apply_indie_core,
            cls.OLD_MONEY_CORE: cls.apply_old_money_core,
            cls.FAIRY_CORE: cls.apply_fairy_core,
            cls.GOLDEN_HOUR_CORE: cls.apply_golden_hour_core,
            
            cls.LEAFES_FRAME: cls.apply_leafes_frame,
            cls.PLAIN_FRAME: cls.apply_plain_frame,
            cls.GOTH_FRAME: cls.apply_goth_frame,
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

    