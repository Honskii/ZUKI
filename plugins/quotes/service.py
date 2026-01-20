import io
import random
import textwrap
from datetime import datetime, date, timezone
from pathlib import Path
from zoneinfo import ZoneInfo
from typing import List

from PIL import Image, ImageDraw, ImageOps, ImageFont


class QuoteService:
    def __init__(
        self,
        *,
        src_path: Path,
        backgrounds: list[Path],
        quote_font_family: Path,
        metadata_font_family: Path,
        avatar: bytes = None,
        randomized: bool = True,
        quote_font_size: int = 24,
        metadata_font_size: int = 18,
        timezone: str = "Etc/UTC",
        strftime: str = "%d.%m.%Y"
    ):
        self.src_path = src_path
        self.randomized = randomized
        self.avatar = avatar
        self.quote_font_family = quote_font_family
        self.metadata_font_family = metadata_font_family
        self.quote_font_size = quote_font_size
        self.metadata_font_size = metadata_font_size
        self.current_bg_index = 0
        self.backgrounds = self.load_backgrounds(backgrounds)
        self.timezone = timezone
        self.strftime = strftime

        self.avatar_size = 200
        self.max_text_length = 225
        self.rate_limit = 2
        self.margin = 30
        self.text_area_width = 375
        self.font_size_text = 24
        self.font_size_metadata = 18

    def load_backgrounds(self, bg_path_list: List[Path]) -> list[Image.Image]:
        """Загружает все доступные фоны из заданной директории в оперативную память"""
        if not bg_path_list:
            raise ValueError("No background paths provided to load.")

        loaded_images = []
        for bg_path in bg_path_list:
            try:
                image = Image.open(bg_path).convert("RGBA")
                if image.size != (700, 400):
                    image = image.resize((700, 400))

                mask_image = Image.open(self.src_path / "img/mask.png").convert("RGBA")
                if mask_image.size != (700, 400):
                    mask_image = mask_image.resize((700, 400))

                image.alpha_composite(mask_image)

                loaded_images.append(image)
            except Exception as e:
                raise RuntimeError(f"Ошибка при загрузке или обработке фона {bg_path}: {e}")
        return loaded_images

    async def get_next_background(self) -> Image.Image:
        """Возвращает следующий фон из списка"""
        if not self.backgrounds:
            raise ValueError("No backgrounds available in QuoteService.")
        bg = None
        if self.randomized:
            bg = random.choice(self.backgrounds)
        else:
            bg = self.backgrounds[self.current_bg_index]
            self.current_bg_index = (self.current_bg_index + 1) % len(self.backgrounds)
        return bg.copy()

    def create_quote_image(
        self,
        bg_image: Image.Image,
        avatar_bytes: bytes,
        username: str,
        text: str,
        message_datetime: datetime
    ) -> io.BytesIO:
        """Генерирует изображение с цитатой"""
        draw = ImageDraw.Draw(bg_image)

        # 2. Шрифты
        try:
            font_text = ImageFont.truetype(self.src_path / "fonts" / self.quote_font_family, self.font_size_text)
            font_metadata = ImageFont.truetype(self.src_path / "fonts" / self.metadata_font_family, self.font_size_metadata)
        except IOError:
            # Если шрифт не найден, используем стандартный
            font_text = ImageFont.load_default()
            font_metadata = ImageFont.load_default()

        # 3. Подготовка аватарки
        avatar = self.prepare_avatar(avatar_bytes) if avatar_bytes else None

        # Координаты аватарки (вертикально по центру)
        avatar_y = (400 - self.avatar_size) // 2
        avatar_x = self.margin

        if avatar:
            bg_image.alpha_composite(avatar, (avatar_x, avatar_y))

        # 4. Отрисовка имени (под аватаркой)
        # Разбиение имени на несколько строк, но пока не используется
        wrapped_name = textwrap.fill(username, width=1500)

        # Расчёт высоту блока имени
        bbox_name = draw.multiline_textbbox((0, 0), wrapped_name, font=font_metadata)
        name_height = bbox_name[3] - bbox_name[1]

        name_y = avatar_y + self.avatar_size + self.margin / 3 # 10px отступ от аватарки
        draw.multiline_text((avatar_x, name_y), f"© {wrapped_name}", font=font_metadata, fill="white", align="center")


        now = message_datetime
        now = now.astimezone(ZoneInfo(self.timezone))
        date_text = f"@ {now.strftime(self.strftime)}"
        date_y = name_y + name_height + self.margin / 4
        draw.text((avatar_x, date_y), date_text, font=font_metadata, fill="white")

        # 5. Отрисовка текста сообщения справа от аватарки
        text_x = avatar_x + self.avatar_size + self.margin * 1.5
        max_width = self.text_area_width

        def wrap_text_by_width(text: str, font: ImageFont.FreeTypeFont, draw: ImageDraw.ImageDraw, max_w: int):
            paragraphs = text.splitlines()
            lines: list[str] = []

            for para in paragraphs:
                # Пустая строка
                if not para:
                    lines.append("")
                    continue

                words = para.split()
                current = ""
                for w in words:
                    candidate = (current + " " + w).strip()
                    bbox = draw.textbbox((0, 0), candidate, font=font)
                    candidate_w = bbox[2] - bbox[0]
                    if candidate_w <= max_w:
                        current = candidate
                    else:
                        if current:
                            lines.append(current)
                        # Если одно слово длиннее max_w — разбиваем его по символам
                        part = ""
                        for ch in w:
                            test_part = part + ch
                            bbox_p = draw.textbbox((0, 0), test_part, font=font)
                            if bbox_p[2] - bbox_p[0] <= max_w:
                                part = test_part
                            else:
                                if part:
                                    lines.append(part)
                                part = ch
                        current = part
                if current:
                    lines.append(current)
            return lines

        lines = wrap_text_by_width(text, font_text, draw, max_width)

        # Рассчитываем ширину самой длинной строки
        text_width = 0
        for line in lines:
            bb = draw.textbbox((0, 0), line, font=font_text)
            w = bb[2] - bb[0]
            if w > text_width:
                text_width = w

        # Центрируем текст в пределах контейнера по горизонтали
        text_x += (self.text_area_width - text_width) // 2

        # Проверяем высоту текста
        line_bbox = draw.textbbox((0, 0), "A", font=font_text)
        line_height = line_bbox[3] - line_bbox[1] + 7  # межстрочный интервал
        total_text_height = len(lines) * line_height

        # Максимальная высота для текста (чтобы не улетел за края)
        max_text_height = 360  # 400 - 20 отступа сверху и снизу

        if total_text_height > max_text_height:
            raise ValueError("Текст слишком большой для картинки")

        # Центрируем блок текста по вертикали относительно фона
        text_start_y = int((400 - total_text_height) / 2.2)

        current_y = text_start_y
        for line in lines:
            draw.text((text_x, current_y), line, font=font_text, fill="white")
            current_y += line_height

        # 6. Сохранение в буфер
        output = io.BytesIO()
        bg_image = bg_image.convert("RGB") # Телеграм лучше так принимает
        bg_image.save(output, format='JPEG', quality=95)
        output.seek(0)
        return output

    def prepare_avatar(self, image_bytes: bytes) -> Image.Image:
        """Подгатавливает аватарку, превращая в требуемый формат"""
        im = Image.open(io.BytesIO(image_bytes)).convert("RGBA")

        im = im.resize((self.avatar_size, self.avatar_size), Image.Resampling.LANCZOS)

        SCALE = 4
        big = self.avatar_size * SCALE

        mask_big = Image.new('L', (big, big), 0)
        draw = ImageDraw.Draw(mask_big)
        draw.ellipse((0, 0, big - 1, big - 1), fill=255)

        mask = mask_big.resize((self.avatar_size, self.avatar_size), Image.Resampling.LANCZOS)

        output = ImageOps.fit(im, (self.avatar_size, self.avatar_size), centering=(0.5, 0.5))
        output.putalpha(mask)
        return output