"""
Editorial Image Service for Pro-Pakistan Blog Posts.
Produces clean, high-resolution 16:9 photojournalistic cover images for blog posts,
completely free of social media card overlays, badges, and typography.

Backends:
1. Pollinations FLUX (Free AI image generation with photorealistic prompt)
2. Curated High-Resolution Editorial Photography Catalog (Curated Unsplash CDN per niche)
"""

import os
import time
import urllib.parse
import logging
from pathlib import Path
from typing import Optional, Dict
import requests
from PIL import Image

logger = logging.getLogger(__name__)

# Curated high-resolution editorial photography fallbacks for each niche
NICHE_EDITORIAL_FALLBACKS: Dict[str, list] = {
    "technology_telecom": [
        "https://images.unsplash.com/photo-1519389950473-47ba0277781c?w=1280&h=720&fit=crop&q=85", # Tech office / devices
        "https://images.unsplash.com/photo-1544197150-b99a580bb7a8?w=1280&h=720&fit=crop&q=85", # Server / Fiber optics
        "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=1280&h=720&fit=crop&q=85", # Modern smartphone
        "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=1280&h=720&fit=crop&q=85"  # Digital coding / telecom
    ],
    "business_finance": [
        "https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?w=1280&h=720&fit=crop&q=85", # Stock trading / charts
        "https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?w=1280&h=720&fit=crop&q=85", # Finance calculator / paperwork
        "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=1280&h=720&fit=crop&q=85", # Modern banking tower
        "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=1280&h=720&fit=crop&q=85"  # Financial trading screen
    ],
    "automotive_carbase": [
        "https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=1280&h=720&fit=crop&q=85", # Modern luxury sports car
        "https://images.unsplash.com/photo-1558981403-c5f9899a28bc?w=1280&h=720&fit=crop&q=85", # Modern motorcycle
        "https://images.unsplash.com/photo-1563720223185-11003d516935?w=1280&h=720&fit=crop&q=85", # Electric vehicle charging
        "https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?w=1280&h=720&fit=crop&q=85"  # Highway automotive speed
    ],
    "sports_prosports": [
        "https://images.unsplash.com/photo-1540747913346-19e32dc3e97e?w=1280&h=720&fit=crop&q=85", # Stadium floodlights
        "https://images.unsplash.com/photo-1531415074968-036ba1b575da?w=1280&h=720&fit=crop&q=85", # Cricket pitch / sports gear
        "https://images.unsplash.com/photo-1508098682722-e99c43a406b2?w=1280&h=720&fit=crop&q=85", # Stadium crowd excitement
        "https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=1280&h=720&fit=crop&q=85"  # Athletic competition
    ],
    "education_scholarships": [
        "https://images.unsplash.com/photo-1523240795612-9a054b0db644?w=1280&h=720&fit=crop&q=85", # University students studying
        "https://images.unsplash.com/photo-1541339907198-e08756dedf3f?w=1280&h=720&fit=crop&q=85", # University graduation / campus
        "https://images.unsplash.com/photo-1498243691581-b145c3f54a5a?w=1280&h=720&fit=crop&q=85", # Historic university library
        "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=1280&h=720&fit=crop&q=85"  # Collaborative campus discussion
    ],
    "entertainment_lens": [
        "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=1280&h=720&fit=crop&q=85", # Cinema hall / theater seats
        "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=1280&h=720&fit=crop&q=85", # Concert stage lighting
        "https://images.unsplash.com/photo-1478720568477-152d9b164e26?w=1280&h=720&fit=crop&q=85", # Film camera / production
        "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=1280&h=720&fit=crop&q=85"  # Music studio / lifestyle
    ],
    "public_utility_guides": [
        "https://images.unsplash.com/photo-1450133064473-71024230f91b?w=1280&h=720&fit=crop&q=85", # Legal documents / passport check
        "https://images.unsplash.com/photo-1563986768609-322da13575f3?w=1280&h=720&fit=crop&q=85", # Mobile digital banking / security
        "https://images.unsplash.com/photo-1554224154-26032ffc0d07?w=1280&h=720&fit=crop&q=85", # Official government portal / stamps
        "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=1280&h=720&fit=crop&q=85"  # Step-by-step checklist desk
    ]
}

class EditorialImageService:
    """Generates and persists dedicated 16:9 editorial imagery for blog posts."""

    @staticmethod
    def generate_editorial_cover(
        prompt: str,
        niche_key: str,
        output_path: Path,
        width: int = 1280,
        height: int = 720,
        timeout: int = 25
    ) -> Path:
        """
        Attempts to generate a clean 16:9 editorial photograph using Pollinations FLUX.
        Falls back to high-resolution curated photography if generation is unavailable.
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Clean the prompt for photorealistic editorial journalism style
        enhanced_prompt = (
            f"photojournalism editorial photograph, {prompt}, "
            "shot on 35mm lens, natural cinematic lighting, highly detailed 8k, "
            "no text, no watermark, no overlays, no frames, widescreen 16:9"
        )
        
        # Step 1: Try Pollinations AI FLUX
        try:
            clean_encoded = urllib.parse.quote(enhanced_prompt.replace("\n", " ").strip())
            pollinations_url = (
                f"https://image.pollinations.ai/prompt/{clean_encoded}"
                f"?width={width}&height={height}&nologo=true&model=flux"
            )
            logger.info(f"🎨 Requesting 16:9 editorial blog cover via Pollinations...")
            res = requests.get(pollinations_url, headers={"User-Agent": "ProPakistaniEditorial/2.0"}, timeout=timeout)
            if res.status_code == 200 and len(res.content) > 5000:
                with open(output_path, "wb") as f:
                    f.write(res.content)
                logger.info(f"✅ Generated 16:9 editorial cover: {output_path} ({len(res.content)} bytes)")
                return output_path
            else:
                logger.warning(f"Pollinations returned status {res.status_code}. Using curated fallback.")
        except Exception as e:
            logger.warning(f"Pollinations generation timed out or failed ({e}). Using curated fallback.")

        # Step 2: Fallback to Curated High-Res Editorial Photography
        fallback_urls = NICHE_EDITORIAL_FALLBACKS.get(niche_key, NICHE_EDITORIAL_FALLBACKS["technology_telecom"])
        import random
        chosen_url = random.choice(fallback_urls)
        try:
            logger.info(f"📥 Downloading curated editorial fallback from Unsplash: {chosen_url}")
            res = requests.get(chosen_url, timeout=15)
            if res.status_code == 200:
                with open(output_path, "wb") as f:
                    f.write(res.content)
                logger.info(f"✅ Downloaded curated 16:9 fallback: {output_path}")
                return output_path
        except Exception as e:
            logger.error(f"Failed to download curated fallback: {e}")

        # Step 3: Absolute fallback - generate high-grade solid gradient placeholder
        img = Image.new("RGB", (width, height), (15, 23, 42))
        img.save(output_path, "JPEG", quality=90)
        return output_path
