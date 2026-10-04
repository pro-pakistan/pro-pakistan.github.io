"""
Studio-Grade Multi-Slide Carousel Compositor.
Renders high-converting 4:5 (1080x1350) carousel decks for Instagram & Facebook:
Slide 1: High-CTR Attention Hook Cover (Inspired by viralhooks.org & 1k+ like accounts)
Slides 2-4: Structured Value Delivery & Tactical Insights
Slide 5: Action Checklist / Key Metric Summary
Slide 6: Save & Share Engagement CTA
"""

import os
import math
import logging
from pathlib import Path
from typing import Dict, List, Any, Tuple
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np

logger = logging.getLogger(__name__)

CAROUSEL_SIZE = (1080, 1350)  # 4:5 Portrait format

class NicheCarouselCompositor:
    def __init__(self, font_dir: Path):
        self.font_dir = font_dir
        self.width, self.height = CAROUSEL_SIZE
        self.font_latin_bold = str(font_dir / "NotoSans-Bold.ttf")
        self.font_urdu_bold = str(font_dir / "NotoNastaliqUrdu-Bold.ttf")

    def _get_font(self, size: int, is_urdu: bool = False):
        font_path = self.font_urdu_bold if is_urdu else self.font_latin_bold
        try:
            return ImageFont.truetype(font_path, size)
        except Exception:
            return ImageFont.load_default()

    def _wrap_text(self, text: str, font, max_width: int, draw: ImageDraw.ImageDraw) -> List[str]:
        words = text.split()
        lines = []
        cur = []
        for w in words:
            test_line = " ".join(cur + [w])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            if bbox[2] - bbox[0] <= max_width:
                cur.append(w)
            else:
                if cur:
                    lines.append(" ".join(cur))
                cur = [w]
        if cur:
            lines.append(" ".join(cur))
        return lines

    def _create_gradient_canvas(self, color_primary=(15, 30, 60), color_secondary=(5, 10, 25)) -> Image.Image:
        base = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 255))
        arr = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        
        for y in range(self.height):
            ratio = y / float(self.height)
            r = int(color_primary[0] * (1 - ratio) + color_secondary[0] * ratio)
            g = int(color_primary[1] * (1 - ratio) + color_secondary[1] * ratio)
            b = int(color_primary[2] * (1 - ratio) + color_secondary[2] * ratio)
            arr[y, :, 0] = r
            arr[y, :, 1] = g
            arr[y, :, 2] = b
            
        gradient = Image.fromarray(arr, mode="RGB").convert("RGBA")
        
        # Subtle grid texture for editorial tech/finance aesthetic
        draw = ImageDraw.Draw(gradient)
        for x in range(0, self.width, 90):
            draw.line([(x, 0), (x, self.height)], fill=(255, 255, 255, 6), width=1)
        for y in range(0, self.height, 90):
            draw.line([(0, y), (self.width, y)], fill=(255, 255, 255, 6), width=1)
            
        return gradient

    def render_carousel_deck(self, package: Dict[str, Any], output_dir: Path) -> List[str]:
        """
        Renders a full 5-6 slide carousel set to the given directory.
        Returns the list of absolute file paths to the slides.
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        slides_data = package.get("social_asset", {}).get("carousel_slides", [])
        if not slides_data:
            return []

        total_slides = len(slides_data)
        brand_name = "PROPAKISTANI"
        category = package.get("category", "TECH & DIGITAL")
        badge_text = package.get("badge", "DAILY DOSSIER")
        
        slide_paths = []

        for idx, slide in enumerate(slides_data):
            slide_num = idx + 1
            is_first = (slide_num == 1)
            is_last = (slide_num == total_slides)

            canvas = self._create_gradient_canvas()
            draw = ImageDraw.Draw(canvas)

            # 1. Header Bar: Brand Logo & Slide Counter
            header_font = self._get_font(26)
            draw.text((80, 70), brand_name, font=header_font, fill=(59, 130, 246, 255))
            draw.text((290, 70), "•  " + category.upper(), font=header_font, fill=(180, 195, 215, 200))
            
            counter_text = f"{slide_num} / {total_slides}"
            c_bbox = draw.textbbox((0, 0), counter_text, font=header_font)
            draw.text((self.width - 80 - (c_bbox[2] - c_bbox[0]), 70), counter_text, font=header_font, fill=(180, 195, 215, 180))

            # 2. Category / Topic Pill Badge
            pill_font = self._get_font(24)
            badge_title = slide.get("badge", badge_text).upper()
            p_bbox = draw.textbbox((0, 0), badge_title, font=pill_font)
            pw = p_bbox[2] - p_bbox[0] + 36
            ph = 44
            px, py = 80, 150
            draw.rounded_rectangle([px, py, px + pw, py + ph], radius=22, fill=(29, 78, 216, 220), outline=(96, 165, 250, 180), width=1)
            draw.text((px + 18, py + 10), badge_title, font=pill_font, fill=(255, 255, 255, 255))

            # 3. Main Card Container (Glassmorphic look)
            card_rect = [80, 230, self.width - 80, 1160]
            draw.rounded_rectangle(card_rect, radius=28, fill=(15, 23, 42, 230), outline=(51, 65, 85, 200), width=2)

            # Slide Content Rendering
            title_text = slide.get("title", "")
            body_text = slide.get("body", "")

            if is_first:
                # ── SLIDE 1: HOOK COVER SLIDE ──
                # Large Viral Hook Typography
                title_font = self._get_font(56)
                lines = self._wrap_text(title_text, title_font, card_rect[2] - card_rect[0] - 80, draw)
                ty = 320
                for line in lines[:5]:
                    draw.text((120, ty), line, font=title_font, fill=(255, 255, 255, 255))
                    ty += 76

                # Decorative accent divider
                draw.line([(120, ty + 20), (320, ty + 20)], fill=(59, 130, 246, 255), width=4)

                # Subdeck / Swipe prompt
                sub_font = self._get_font(34)
                draw.text((120, ty + 60), body_text, font=sub_font, fill=(147, 197, 253, 255))

                # Swipe Arrow Prompt at bottom of card
                prompt_font = self._get_font(30)
                draw.rounded_rectangle([120, 1020, self.width - 120, 1100], radius=16, fill=(30, 41, 59, 200), outline=(71, 85, 105, 180))
                draw.text((160, 1042), "👉  SWIPE TO READ THE FULL REPORT", font=prompt_font, fill=(255, 255, 255, 230))

            elif is_last:
                # ── SLIDE 6: CTA / ENGAGEMENT SLIDE ──
                icon_font = self._get_font(72)
                draw.text((120, 320), "🔖", font=icon_font, fill=(255, 215, 0, 255))

                title_font = self._get_font(52)
                draw.text((120, 430), "Save This For Later", font=title_font, fill=(255, 255, 255, 255))
                
                body_font = self._get_font(32)
                b_lines = self._wrap_text(body_text, body_font, card_rect[2] - card_rect[0] - 80, draw)
                by = 530
                for bl in b_lines:
                    draw.text((120, by), bl, font=body_font, fill=(203, 213, 225, 255))
                    by += 48

                # Call to action pills
                cta_font = self._get_font(30)
                draw.rounded_rectangle([120, 780, self.width - 120, 860], radius=20, fill=(29, 78, 216, 255))
                draw.text((160, 804), "📲  Share this with a friend or colleague", font=cta_font, fill=(255, 255, 255, 255))

                draw.rounded_rectangle([120, 890, self.width - 120, 970], radius=20, fill=(30, 41, 59, 220), outline=(51, 65, 85, 255))
                draw.text((160, 914), "🔔  Follow @ProPakistani for daily updates", font=cta_font, fill=(147, 197, 253, 255))

            else:
                # ── SLIDES 2–5: VALUE DELIVERY SLIDES ──
                step_tag = f"INSIGHT #{slide_num - 1}"
                tag_font = self._get_font(26)
                draw.text((120, 310), step_tag, font=tag_font, fill=(59, 130, 246, 255))

                # Slide Headline
                title_font = self._get_font(44)
                t_lines = self._wrap_text(title_text, title_font, card_rect[2] - card_rect[0] - 80, draw)
                ty = 370
                for tl in t_lines[:3]:
                    draw.text((120, ty), tl, font=title_font, fill=(255, 255, 255, 255))
                    ty += 60

                draw.line([(120, ty + 20), (280, ty + 20)], fill=(71, 85, 105, 180), width=2)

                # Body Prose / Insight
                body_font = self._get_font(34)
                b_lines = self._wrap_text(body_text, body_font, card_rect[2] - card_rect[0] - 80, draw)
                by = ty + 60
                for bl in b_lines:
                    draw.text((120, by), bl, font=body_font, fill=(226, 232, 240, 255))
                    by += 54

            # 4. Bottom Footer Attribution
            footer_font = self._get_font(22)
            draw.text((80, 1240), "ProPakistani — Independent Digital Journalism", font=footer_font, fill=(100, 116, 139, 200))
            draw.text((self.width - 240, 1240), "propakistani.pk", font=footer_font, fill=(100, 116, 139, 200))

            slide_filename = f"slide_{slide_num:02d}.png"
            slide_path = output_dir / slide_filename
            canvas.save(slide_path, "PNG", optimize=True)
            slide_paths.append(str(slide_path))

        logger.info(f"✅ Generated {len(slide_paths)}-slide carousel in: {output_dir}")
        return slide_paths
