"""
Pro Pakistan Editorial & Viral Content Engine — run_agent.py
Autonomous publishing pipeline covering all 7 official verticals:
1. Technology & Telecom (PTA, 5G, Packages, Devices, ISPs)
2. Business & Finance (PSX, FBR Taxes, IMF, Startups)
3. Automotive (CarBase) (Car/Bike Prices, Fuel, EVs)
4. Sports (ProSports) (Pakistan Cricket, PSL, Tournaments)
5. Education & Scholarships (HEC, Admissions, Grants)
6. Entertainment & Lifestyle (Lens) (Celebrities, Cinema, Dramas)
7. Public Utility Guides (Passports, CNIC, NADRA, Wallets)

Features:
- Dedicated, clean 16:9 editorial cover photography for blog posts (NO text overlays).
- Attention-hook social variations: Single Card, 6-Slide Carousel, or 20s Reel.
- Full long-form, indexable journalistic articles with H2 sections, metrics, and FAQs.
- Multi-platform publishing to Instagram, Facebook, and Threads.
"""

import os
import sys
import json
import re
import random
import logging
import argparse
import shutil
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load local environment
load_dotenv()

BASE_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(BASE_DIR))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("pro_pakistan")

from agents.viral_hook_framework import PRO_PAKISTAN_NICHE_MATRIX, ViralHookEngine
from agents.pro_pakistan_editorial_agent import generate_pro_pakistan_editorial_package
from video_engine.editorial_image_service import EditorialImageService
from video_engine.niche_carousel_compositor import NicheCarouselCompositor
from video_engine.niche_card_compositor import NicheCardCompositor
from video_engine.niche_catalog import NicheCatalog

# Social publishers
from publish_reels import publish_facebook_photo, publish_instagram_reel, publish_facebook_reel, publish_threads_post
try:
    from publish_carousels import publish_facebook_carousel_local, publish_instagram_carousel_local
except ImportError:
    publish_facebook_carousel_local = None
    publish_instagram_carousel_local = None

DEFAULT_PAGE_ID = "1300365879835045"
DEFAULT_IG_ID = "17841424057438345"

def run_pipeline(
    niche_key: str = None,
    format_type: str = "auto",
    topic: str = None,
    lang: str = "english",
    no_publish: bool = False
):
    """
    Executes an autonomous editorial and social publishing cycle.
    """
    # 1. Resolve Niche
    if not niche_key or niche_key == "all":
        niche_key = random.choice(list(PRO_PAKISTAN_NICHE_MATRIX.keys()))
    elif niche_key not in PRO_PAKISTAN_NICHE_MATRIX:
        # Fallback to fuzzy match or random
        matched = [k for k in PRO_PAKISTAN_NICHE_MATRIX if niche_key in k]
        niche_key = matched[0] if matched else random.choice(list(PRO_PAKISTAN_NICHE_MATRIX.keys()))

    niche_meta = PRO_PAKISTAN_NICHE_MATRIX[niche_key]
    logger.info(f"🎯 Executing Editorial Package: '{niche_meta['name']}' (Format: {format_type.upper()}, Lang: {lang.upper()})")

    # 2. Generate Editorial Article & Viral Social Payload via LLM / Fallback
    package = generate_pro_pakistan_editorial_package(
        niche_key=niche_key,
        specific_topic=topic,
        preferred_format=format_type,
        lang=lang
    )

    blog_article = package["blog_article"]
    social_asset = package.get("social_asset", {})
    captions = package.get("social_captions", {})
    chosen_format = package.get("social_format", "card")

    # Generate unique URL slug & post ID
    slug = re.sub(r'[^a-z0-9]+', '-', blog_article.get("title", "article").lower()).strip('-')[:35]
    post_id = f"{slug}-{random.randint(100, 999)}"

    # 3. Generate Dedicated 16:9 Clean Blog Cover Image (NO Text Overlays)
    assets_posts_dir = BASE_DIR / "assets" / "posts"
    assets_posts_dir.mkdir(parents=True, exist_ok=True)
    blog_cover_path = assets_posts_dir / f"{post_id}_cover.jpg"

    EditorialImageService.generate_editorial_cover(
        prompt=blog_article.get("editorial_image_prompt", f"Editorial photo of {niche_meta['name']} in Pakistan"),
        niche_key=niche_key,
        output_path=blog_cover_path,
        width=1280,
        height=720
    )
    rel_cover_path = f"assets/posts/{post_id}_cover.jpg"
    logger.info(f"📸 Dedicated Clean 16:9 Blog Cover Created: {rel_cover_path}")

    # 4. Generate Social Artifact Based on Format
    fonts_dir = BASE_DIR / "assets" / "fonts"
    storage_dir = BASE_DIR / "storage"
    created_social_media = []

    if chosen_format == "carousel":
        carousel_compositor = NicheCarouselCompositor(font_dir=fonts_dir)
        carousel_out_dir = storage_dir / "carousels" / post_id
        slide_paths = carousel_compositor.render_carousel_deck(package, carousel_out_dir)
        created_social_media = slide_paths
        logger.info(f"🎠 Generated {len(slide_paths)}-Slide Studio Carousel with Viral Hook Cover")

    elif chosen_format in ("card", "auto"):
        # Single editorial card for breaking news or high-impact stats
        card_compositor = NicheCardCompositor(font_dir=fonts_dir)
        card_content = {
            "headline": social_asset.get("viral_hook_headline") or blog_article["title"],
            "subdeck": social_asset.get("sub_hook") or blog_article["subdeck"],
            "badge": package["badge"],
            "category_tag": package["category"],
            "stat_number": blog_article.get("stat_number", ""),
            "stat_label": blog_article.get("stat_label", "KEY METRIC"),
            "bullet_points": blog_article.get("key_takeaways", []),
            "captions": captions
        }
        card_storage_dir = storage_dir / "cards"
        card_storage_dir.mkdir(parents=True, exist_ok=True)
        card_output = card_storage_dir / f"{post_id}_card.png"
        
        # Render single social card
        legacy_niche = NicheCatalog.resolve_niche("tech_news")
        legacy_niche["name"] = niche_meta["name"]
        legacy_niche["category_tag"] = niche_meta["category_tag"]
        legacy_niche["badge"] = niche_meta["badge"]
        
        rendered_card = card_compositor.render_card(legacy_niche, card_content, str(card_output))
        created_social_media = [rendered_card]
        logger.info(f"🖼️ Single Editorial Hook Card Generated: {rendered_card}")

    # 5. Append Captions & Audit Log
    with open(BASE_DIR / "latest_caption.txt", "w", encoding="utf-8") as f:
        f.write(captions.get("threads", captions.get("facebook", "")))

    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "niche": niche_key,
        "format": chosen_format,
        "post_id": post_id,
        "title": blog_article["title"],
        "cover_image": rel_cover_path,
        "social_media": created_social_media,
        "captions": captions
    }
    with open(BASE_DIR / "captions_log.jsonl", "a", encoding="utf-8") as lf:
        lf.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

    # 6. Update Static Blog Catalog (posts.json + sitemap.xml)
    update_blog_catalog(post_id, package, rel_cover_path, lang)

    # 7. Publish to Social Platforms (Facebook, Instagram, Threads)
    if not no_publish:
        target_page_id = (os.getenv("FB_PAGE_ID") or DEFAULT_PAGE_ID).strip()
        logger.info(f"[*] Publishing to target Facebook Page ID: {target_page_id}")

        try:
            if chosen_format == "carousel" and len(created_social_media) > 1:
                # Multi-slide Carousel Publication
                if publish_facebook_carousel_local:
                    publish_facebook_carousel_local(created_social_media, captions.get("facebook", ""))
                if publish_instagram_carousel_local:
                    publish_instagram_carousel_local(created_social_media, captions.get("instagram", ""))
                if publish_threads_post:
                    publish_threads_post(captions.get("threads", ""))

            elif chosen_format == "card" and created_social_media:
                # Single Image Post Publication
                card_path = created_social_media[0]
                publish_facebook_photo(card_path, captions.get("facebook", ""), page_id=target_page_id)
                if publish_threads_post:
                    publish_threads_post(captions.get("threads", ""))

        except Exception as e:
            logger.error(f"[-] Social publishing error: {e}")
    else:
        logger.info("ℹ️ --no-publish flag set. Media preserved locally.")

    return {
        "post_id": post_id,
        "format": chosen_format,
        "cover_image": rel_cover_path,
        "social_media": created_social_media
    }

def update_blog_catalog(post_id: str, package: dict, cover_img_path: str, lang: str):
    """
    Appends the structured, in-depth blog post to posts.json and updates sitemap.xml.
    """
    posts_file = BASE_DIR / "posts.json"
    sitemap_file = BASE_DIR / "sitemap.xml"
    blog_article = package["blog_article"]

    # Flatten sections into body paragraphs for backward compatibility
    body_paragraphs = []
    for sec in blog_article.get("sections", []):
        body_paragraphs.append(sec.get("content", ""))

    new_article = {
        "id": post_id,
        "category": package["category"],
        "badge": package["badge"],
        "title": blog_article["title"],
        "subdeck": blog_article["subdeck"],
        "image": cover_img_path, # Pristine 16:9 editorial cover image
        "stat_number": blog_article.get("stat_number", ""),
        "stat_label": blog_article.get("stat_label", "KEY METRIC"),
        "author": blog_article.get("author", "Hamid Raza"),
        "author_role": blog_article.get("author_role", "Chief Technology Editor"),
        "author_avatar": blog_article.get("author_avatar", "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=120&h=120&fit=crop"),
        "date": datetime.now().strftime("%d %b %Y"),
        "read_time": blog_article.get("read_time", "4 min read"),
        "featured": True,
        "body": body_paragraphs if body_paragraphs else [blog_article["subdeck"]],
        "sections": blog_article.get("sections", []),
        "takeaways": blog_article.get("key_takeaways", []),
        "faqs": blog_article.get("faqs", []),
        "social_format": package.get("social_format", "card"),
        "lang": "ur" if lang == "urdu" else "en"
    }

    try:
        posts = []
        if posts_file.exists():
            with open(posts_file, "r", encoding="utf-8") as f:
                posts = json.load(f)
        for p in posts:
            p["featured"] = False
        posts.insert(0, new_article)
        posts = posts[:50]
        with open(posts_file, "w", encoding="utf-8") as f:
            json.dump(posts, f, indent=2, ensure_ascii=False)
        logger.info(f"📰 Autonomous Blog Catalog Updated: {posts_file} (+1 in-depth article: '{new_article['title']}')")

        # Update sitemap.xml
        if sitemap_file.exists():
            today_str = datetime.now().strftime("%Y-%m-%d")
            with open(sitemap_file, "r", encoding="utf-8") as sf:
                sitemap_content = sf.read()
            
            new_url_entry = f"""  <url>
    <loc>https://pro-pakistan.github.io/#{post_id}</loc>
    <lastmod>{today_str}</lastmod>
    <changefreq>daily</changefreq>
    <priority>0.85</priority>
  </url>
</urlset>"""
            if f"#{post_id}</loc>" not in sitemap_content and "</urlset>" in sitemap_content:
                sitemap_content = sitemap_content.replace("</urlset>", new_url_entry)
                with open(sitemap_file, "w", encoding="utf-8") as sf:
                    sf.write(sitemap_content)
                logger.info(f"🗺️ Sitemap Updated with post #{post_id}")

        # Sync INITIAL_POSTS in index.html for zero latency hydration
        index_file = BASE_DIR / "index.html"
        if index_file.exists():
            with open(index_file, "r", encoding="utf-8") as inf:
                html_text = inf.read()
            pattern = r'window\.INITIAL_POSTS\s*=\s*\[.*?\];'
            replacement = f'window.INITIAL_POSTS = {json.dumps(posts[:15], ensure_ascii=False)};'
            html_text = re.sub(pattern, lambda _: replacement, html_text, flags=re.DOTALL)
            with open(index_file, "w", encoding="utf-8") as outf:
                outf.write(html_text)
            logger.info("⚡ Synced window.INITIAL_POSTS in index.html")

    except Exception as e:
        logger.warning(f"Could not update blog catalog: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pro Pakistan Editorial & Viral Content Engine")
    parser.add_argument(
        "--niche",
        choices=["all"] + list(PRO_PAKISTAN_NICHE_MATRIX.keys()),
        default="all",
        help="Pro Pakistan niche vertical to publish"
    )
    parser.add_argument(
        "--format",
        choices=["auto", "card", "carousel", "reel"],
        default="auto",
        help="Social media format (card, carousel, reel, or auto)"
    )
    parser.add_argument("--topic", type=str, default=None, help="Custom topic / angle")
    parser.add_argument("--lang", type=str, choices=["english", "urdu"], default="english", help="Language")
    parser.add_argument("--no-publish", action="store_true", help="Generate assets & blog without social posting")
    parser.add_argument("--once", action="store_true", help="Run single generation cycle")

    args = parser.parse_args()
    run_pipeline(
        niche_key=args.niche,
        format_type=args.format,
        topic=args.topic,
        lang=args.lang,
        no_publish=args.no_publish
    )
