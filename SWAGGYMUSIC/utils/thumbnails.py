import os
import re
import random
import time
import aiofiles
import aiohttp
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageEnhance
from py_yt import VideosSearch
from config import YOUTUBE_IMG_URL

FONT_TITLE = "ShiviMusic/assets/f (1).ttf"
FONT_AXIOM = "ShiviMusic/assets/f (1).ttf"
FONT_META  = "ShiviMusic/assets/cfont (1).ttf"
FONT_TIME  = "ShiviMusic/assets/cfont (1).ttf"

CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)

COLOR_PALETTE = [
    (0, 230, 118), (124, 77, 255), (255, 23, 68), (255, 109, 0),
    (0, 176, 255), (255, 193, 7), (233, 30, 99), (0, 200, 150),
    (156, 39, 176), (255, 87, 34), (33, 150, 243), (76, 175, 80),
    (255, 152, 0), (121, 85, 72), (96, 125, 139), (244, 67, 54),
    (232, 30, 99), (103, 58, 183), (63, 81, 181), (3, 169, 244),
    (0, 188, 212), (0, 150, 136), (139, 195, 74), (205, 220, 57),
    (255, 235, 59), (255, 64, 129), (224, 64, 251), (92, 107, 192),
    (68, 138, 255), (0, 229, 255), (29, 233, 182), (118, 255, 3),
    (176, 255, 0), (238, 255, 65), (255, 234, 0), (255, 214, 0),
    (255, 145, 0), (255, 82, 82), (255, 128, 171), (255, 179, 207),
    (234, 199, 255), (209, 196, 233), (197, 202, 233), (197, 214, 255),
    (178, 235, 242), (178, 223, 219), (200, 230, 201), (220, 237, 200),
    (240, 244, 195), (255, 249, 196), (255, 236, 179), (255, 224, 178),
    (255, 204, 188), (255, 205, 210), (252, 228, 236), (243, 229, 245),
    (237, 231, 246), (232, 234, 246), (227, 242, 253), (224, 247, 250),
    (224, 242, 241), (232, 245, 233), (241, 248, 233), (249, 251, 231),
    (255, 252, 225), (255, 248, 225), (255, 243, 224), (251, 233, 231),
    (255, 235, 238), (255, 99, 71), (255, 140, 0), (255, 215, 0),
    (50, 205, 50), (64, 224, 208), (72, 61, 139), (95, 158, 160),
    (100, 149, 237), (102, 205, 170), (106, 90, 205), (112, 128, 144),
    (119, 136, 153), (123, 104, 238), (127, 255, 0), (127, 255, 212),
    (128, 0, 0), (128, 0, 128), (128, 128, 0), (135, 206, 235),
    (135, 206, 250), (138, 43, 226), (139, 69, 19), (143, 188, 143),
    (144, 238, 144), (147, 112, 219), (148, 0, 211), (152, 251, 152),
    (153, 50, 204), (154, 205, 50), (160, 82, 45), (165, 42, 42),
    (169, 169, 169), (173, 216, 230), (175, 238, 238), (176, 196, 222),
    (176, 224, 230), (178, 34, 34), (184, 134, 11), (186, 85, 211),
    (188, 143, 143), (189, 183, 107), (192, 192, 192), (199, 21, 133),
    (205, 92, 92), (205, 133, 63), (208, 32, 144), (210, 105, 30),
    (210, 180, 140), (216, 191, 216), (218, 112, 214), (218, 165, 32),
    (219, 112, 147), (220, 20, 60), (220, 220, 220), (221, 160, 221),
    (222, 184, 135), (224, 255, 255), (230, 230, 250), (233, 150, 122),
    (238, 130, 238), (238, 221, 130), (238, 232, 170), (240, 128, 128),
    (240, 230, 140), (240, 248, 255), (240, 255, 240), (240, 255, 255),
    (244, 164, 96), (245, 222, 179), (245, 245, 220), (245, 245, 245),
    (245, 255, 250), (246, 255, 237), (248, 248, 255), (249, 255, 240),
    (250, 128, 114), (250, 235, 215), (250, 240, 230), (253, 245, 230),
    (255, 0, 0), (255, 0, 255), (255, 20, 147), (255, 218, 185),
    (255, 222, 173), (255, 228, 185), (255, 228, 196), (255, 228, 225),
    (255, 239, 213), (255, 240, 245), (255, 245, 238), (255, 250, 205),
    (255, 250, 240), (255, 250, 250), (255, 255, 0), (255, 255, 224),
    (255, 255, 240), (255, 255, 250), (255, 255, 245),
    (0, 0, 0), (25, 25, 112), (30, 144, 255), (46, 139, 87),
    (47, 79, 79), (60, 179, 113), (65, 105, 225), (70, 130, 180),
    (72, 209, 204), (75, 0, 130), (85, 107, 47), (100, 0, 0),
    (105, 105, 105), (111, 0, 255), (118, 0, 255), (120, 0, 255),
    (125, 0, 255), (130, 0, 255), (135, 0, 255), (140, 0, 255),
    (145, 0, 255), (150, 0, 255), (155, 0, 255), (160, 0, 255),
    (165, 0, 255), (170, 0, 255), (175, 0, 255), (180, 0, 255),
    (185, 0, 255), (190, 0, 255), (195, 0, 255), (200, 0, 255),
    (205, 0, 255), (210, 0, 255), (215, 0, 255), (220, 0, 255),
    (225, 0, 255), (230, 0, 255), (235, 0, 255), (240, 0, 255),
    (245, 0, 255), (250, 0, 255), (255, 0, 250), (255, 0, 245),
    (255, 0, 240), (255, 0, 235), (255, 0, 230), (255, 0, 225),
    (255, 0, 220), (255, 0, 215), (255, 0, 210), (255, 0, 205),
    (255, 0, 200), (255, 0, 195), (255, 0, 190), (255, 0, 185),
    (255, 0, 180), (255, 0, 175), (255, 0, 170), (255, 0, 165),
    (255, 0, 160), (255, 0, 155), (255, 0, 150), (255, 0, 145),
    (255, 0, 140), (255, 0, 135), (255, 0, 130), (255, 0, 125),
    (255, 0, 120), (255, 0, 115), (255, 0, 110), (255, 0, 105),
    (255, 0, 100), (255, 0, 95), (255, 0, 90), (255, 0, 85),
    (255, 0, 80), (255, 0, 75), (255, 0, 70), (255, 0, 65),
    (255, 0, 60), (255, 0, 55), (255, 0, 50), (255, 0, 45),
    (255, 0, 40), (255, 0, 35), (255, 0, 30), (255, 0, 25),
    (255, 0, 20), (255, 0, 15), (255, 0, 10), (255, 0, 5),
    (255, 5, 0), (255, 10, 0), (255, 15, 0), (255, 20, 0),
    (255, 25, 0), (255, 30, 0), (255, 35, 0), (255, 40, 0),
    (255, 45, 0), (255, 50, 0), (255, 55, 0), (255, 60, 0),
    (255, 65, 0), (255, 70, 0), (255, 75, 0), (255, 80, 0),
    (255, 85, 0), (255, 90, 0), (255, 95, 0), (255, 100, 0),
    (255, 105, 0), (255, 110, 0), (255, 115, 0), (255, 120, 0),
    (255, 125, 0), (255, 130, 0), (255, 135, 0), (255, 140, 0),
    (255, 145, 0), (255, 150, 0), (255, 155, 0), (255, 160, 0),
    (255, 165, 0), (255, 170, 0), (255, 175, 0), (255, 180, 0),
    (255, 185, 0), (255, 190, 0), (255, 195, 0), (255, 200, 0),
    (255, 205, 0), (255, 210, 0), (215, 255, 0), (220, 255, 0),
    (225, 255, 0), (230, 255, 0), (235, 255, 0), (240, 255, 0),
    (245, 255, 0), (255, 250, 0), (250, 255, 0), (245, 255, 0),
    (240, 255, 0), (235, 255, 0), (230, 255, 0), (225, 255, 0),
    (220, 255, 0), (215, 255, 0), (210, 255, 0), (205, 255, 0),
    (200, 255, 0), (195, 255, 0), (190, 255, 0), (185, 255, 0),
    (180, 255, 0), (175, 255, 0), (170, 255, 0), (165, 255, 0),
    (160, 255, 0), (155, 255, 0), (150, 255, 0), (145, 255, 0),
    (140, 255, 0), (135, 255, 0), (130, 255, 0), (125, 255, 0),
    (120, 255, 0), (115, 255, 0), (110, 255, 0), (105, 255, 0),
    (100, 255, 0), (95, 255, 0), (90, 255, 0), (85, 255, 0),
    (80, 255, 0), (75, 255, 0), (70, 255, 0), (65, 255, 0),
    (60, 255, 0), (55, 255, 0), (50, 255, 0), (45, 255, 0),
    (40, 255, 0), (35, 255, 0), (30, 255, 0), (25, 255, 0),
    (20, 255, 0), (15, 255, 0), (10, 255, 0), (5, 255, 0),
    (0, 255, 5), (0, 255, 10), (0, 255, 15), (0, 255, 20),
    (0, 255, 25), (0, 255, 30), (0, 255, 35), (0, 255, 40),
    (0, 255, 45), (0, 255, 50), (0, 255, 55), (0, 255, 60),
    (0, 255, 65), (0, 255, 70), (0, 255, 75), (0, 255, 80),
    (0, 255, 85), (0, 255, 90), (0, 255, 95), (0, 255, 100),
    (0, 255, 105), (0, 255, 110), (0, 255, 115), (0, 255, 120),
    (0, 255, 125), (0, 255, 130), (0, 255, 135), (0, 255, 140),
    (0, 255, 145), (0, 255, 150), (0, 255, 155), (0, 255, 160),
    (0, 255, 165), (0, 255, 170), (0, 255, 175), (0, 255, 180),
    (0, 255, 185), (0, 255, 190), (0, 255, 195), (0, 255, 200),
    (0, 255, 205), (0, 255, 210), (0, 255, 215), (0, 255, 220),
    (0, 255, 225), (0, 255, 230), (0, 255, 235), (0, 255, 240),
    (0, 255, 245), (0, 255, 250), (0, 250, 255), (0, 245, 255),
    (0, 240, 255), (0, 235, 255), (0, 230, 255), (0, 225, 255),
    (0, 220, 255), (0, 215, 255), (0, 210, 255), (0, 205, 255),
    (0, 200, 255), (0, 195, 255), (0, 190, 255), (0, 185, 255),
    (0, 180, 255), (0, 175, 255), (0, 170, 255), (0, 165, 255),
    (0, 160, 255), (0, 155, 255), (0, 150, 255), (0, 145, 255),
    (0, 140, 255), (0, 135, 255), (0, 130, 255), (0, 125, 255),
    (0, 120, 255), (0, 115, 255), (0, 110, 255), (0, 105, 255),
    (0, 100, 255), (0, 95, 255), (0, 90, 255), (0, 85, 255),
    (0, 80, 255), (0, 75, 255), (0, 70, 255), (0, 65, 255),
    (0, 60, 255), (0, 55, 255), (0, 50, 255), (0, 45, 255),
    (0, 40, 255), (0, 35, 255), (0, 30, 255), (0, 25, 255),
    (0, 20, 255), (0, 15, 255), (0, 10, 255), (0, 5, 255),
    (5, 0, 255), (10, 0, 255), (15, 0, 255), (20, 0, 255),
    (25, 0, 255), (30, 0, 255), (35, 0, 255), (40, 0, 255),
    (45, 0, 255), (50, 0, 255), (55, 0, 255), (60, 0, 255),
    (65, 0, 255), (70, 0, 255), (75, 0, 255), (80, 0, 255),
    (85, 0, 255), (90, 0, 255), (95, 0, 255), (100, 0, 255),
    (105, 0, 255), (110, 0, 255), (115, 0, 255), (120, 0, 255),
    (125, 0, 255), (130, 0, 255), (135, 0, 255), (140, 0, 255),
    (145, 0, 255), (150, 0, 255), (155, 0, 255), (160, 0, 255),
    (165, 0, 255), (170, 0, 255), (175, 0, 255), (180, 0, 255),
    (185, 0, 255), (190, 0, 255), (195, 0, 255), (200, 0, 255),
    (205, 0, 255), (210, 0, 255), (215, 0, 255), (220, 0, 255),
    (225, 0, 255), (230, 0, 255), (235, 0, 255), (240, 0, 255),
    (245, 0, 255), (250, 0, 255),
]

THUMB_SIZE = 420
THUMB_X = 60
THUMB_Y = (720 - THUMB_SIZE) // 2
THUMB_RADIUS = 50

TITLE_X = THUMB_X + THUMB_SIZE + 50
TITLE_Y = THUMB_Y + 20
META_Y = TITLE_Y + 75
VIEWS_Y = META_Y + 55
PLAYER_Y = VIEWS_Y + 55
DEV_Y = PLAYER_Y + 55
REQUESTED_Y = DEV_Y + 55

BAR_X = TITLE_X
BAR_Y = REQUESTED_Y + 85
BAR_WIDTH = 630
BAR_HEIGHT = 8

TIME_Y = BAR_Y + 35

MAX_TITLE_WIDTH = 630


def trim_text(text, font, max_width):
    try:
        if hasattr(font, 'getlength'):
            if font.getlength(text) <= max_width:
                return text
            for i in range(len(text) - 1, 0, -1):
                if font.getlength(text[:i] + "…") <= max_width:
                    return text[:i] + "…"
            return "…"
        else:
            return text[:60]
    except:
        return text[:60]


DIRECT_THUMB_FALLBACK = "https://i.ytimg.com/vi/{videoid}/hqdefault.jpg"


async def _fetch_meta_via_search(videoid: str):
    """Try to get title/thumb/duration/views/channel via py_yt search.
    Verifies the returned result's own id actually matches videoid,
    since VideosSearch is a text-search API, not an exact lookup —
    it can occasionally return an unrelated video."""
    for _attempt in range(2):
        try:
            results = VideosSearch(f"https://www.youtube.com/watch?v={videoid}", limit=1)
            results_data = await results.next()
            data = results_data.get("result", [{}])[0]

            fetched_id = data.get("id") or data.get("videoId")
            if fetched_id and fetched_id != videoid:
                # search drifted to a different video — don't trust it, retry once
                continue

            title = re.sub(r"\W+", " ", data.get("title", "Song")).title()
            thumbnail_url = data.get("thumbnails", [{}])[0].get("url", "").split("?")[0]
            duration = data.get("duration")
            views = data.get("viewCount", {}).get("short", "Unknown")
            channel = data.get("channel", {}).get("name", "YouTube")
            if thumbnail_url:
                return title, thumbnail_url, duration, views, channel
        except Exception:
            pass
    return None


async def get_thumb(videoid: str, progress_percent: int = 0, use_cache: bool = True, user_name: str = "Badnam") -> str:
    print(f"📥 get_thumb called with videoid: {videoid}, progress: {progress_percent}%")

    use_cache = False

    timestamp = int(time.time()) if not use_cache else 0
    cache_path = os.path.join(CACHE_DIR, f"{videoid}_p{progress_percent}_t{timestamp}.png")

    if use_cache and os.path.exists(cache_path):
        return cache_path

    thumb_path = os.path.join(CACHE_DIR, f"thumb_{videoid}_{timestamp}.png")
    accent = random.choice(COLOR_PALETTE)

    meta = await _fetch_meta_via_search(videoid)
    if meta:
        title, thumbnail_url, duration, views, channel = meta
    else:
        # Search failed / drifted — fall back to YouTube's own CDN thumbnail
        # keyed directly by videoid. This is ALWAYS the correct thumbnail
        # for this exact video, unlike the generic static YOUTUBE_IMG_URL
        # used previously, which had nothing to do with the playing song.
        title, thumbnail_url, duration, views, channel = (
            "Song", DIRECT_THUMB_FALLBACK.format(videoid=videoid), None, "Unknown", "YouTube"
        )

    is_live = not duration or str(duration).strip().lower() in {"", "live"}
    duration_text = "LIVE" if is_live else (duration or "0:00")

    downloaded = False
    for url in (thumbnail_url, DIRECT_THUMB_FALLBACK.format(videoid=videoid)):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as resp:
                    if resp.status == 200:
                        async with aiofiles.open(thumb_path, "wb") as f:
                            await f.write(await resp.read())
                        downloaded = True
                        break
        except Exception:
            continue

    if not downloaded:
        # Both the search-derived URL and the direct videoid-keyed CDN URL
        # failed (network/YouTube outage) — only now use the generic image,
        # as a last resort so the bot doesn't crash.
        return YOUTUBE_IMG_URL

    try:
        base = Image.open(thumb_path).convert("RGBA")
        base = base.resize((1280, 720), Image.LANCZOS)
        base = ImageEnhance.Brightness(base).enhance(1.1)
        bg = base.filter(ImageFilter.GaussianBlur(50))
        dark = Image.new("RGBA", bg.size, (0, 0, 0, 100))
        bg = Image.alpha_composite(bg, dark)

        border_layer = Image.new("RGBA", (1280, 720), (0, 0, 0, 0))
        bd = ImageDraw.Draw(border_layer)
        
        bd.rectangle((0, 0, 1279, 719), outline=accent, width=6)
        
        inner_glow_params = [
            (2, 250), (4, 235), (6, 218), (8, 195), (10, 172),
            (12, 150), (14, 130), (16, 112), (18, 95), (20, 80),
            (22, 65), (24, 52), (26, 40), (28, 30), (30, 22), (32, 15)
        ]
        
        for inset, alpha in inner_glow_params:
            bd.rectangle(
                (inset, inset, 1279 - inset, 719 - inset),
                outline=(*accent, alpha),
                width=2
            )
            
        bg = Image.alpha_composite(bg, border_layer)

        thumb_img = Image.open(thumb_path).convert("RGBA")
        thumb_img = thumb_img.resize((THUMB_SIZE, THUMB_SIZE), Image.LANCZOS)
        thumb_img = ImageEnhance.Brightness(thumb_img).enhance(1.1)

        thumb_mask = Image.new("L", (THUMB_SIZE, THUMB_SIZE), 0)
        ImageDraw.Draw(thumb_mask).rounded_rectangle(
            (0, 0, THUMB_SIZE, THUMB_SIZE), radius=THUMB_RADIUS, fill=255
        )

        shadow = Image.new("RGBA", (1280, 720), (0, 0, 0, 0))
        sd = ImageDraw.Draw(shadow)
        sd.rounded_rectangle(
            (THUMB_X - 8, THUMB_Y - 8,
             THUMB_X + THUMB_SIZE + 8, THUMB_Y + THUMB_SIZE + 8),
            radius=THUMB_RADIUS + 10, fill=(*accent, 140)
        )
        shadow = shadow.filter(ImageFilter.GaussianBlur(25))
        bg = Image.alpha_composite(bg, shadow)

        thumb_glow = Image.new("RGBA", (1280, 720), (0, 0, 0, 0))
        tg = ImageDraw.Draw(thumb_glow)
        
        for spread, alpha in [(32, 15), (30, 22), (28, 30), (26, 40), (24, 52), (22, 65), (20, 80), (18, 95), 
                              (16, 112), (14, 130), (12, 150), (10, 172), (8, 195), (6, 218), (4, 235), (2, 250)]:
            tg.rounded_rectangle(
                (THUMB_X - spread, THUMB_Y - spread,
                 THUMB_X + THUMB_SIZE + spread, THUMB_Y + THUMB_SIZE + spread),
                radius=THUMB_RADIUS + spread,
                outline=(*accent, alpha),
                width=3
            )
        
        for inner, alpha in [(3, 120), (6, 80)]:
            tg.rounded_rectangle(
                (THUMB_X + inner, THUMB_Y + inner,
                 THUMB_X + THUMB_SIZE - inner, THUMB_Y + THUMB_SIZE - inner),
                radius=THUMB_RADIUS - inner,
                outline=(*accent, alpha),
                width=2
            )
        
        bg = Image.alpha_composite(bg, thumb_glow)
        bg.paste(thumb_img, (THUMB_X, THUMB_Y), thumb_mask)

        draw = ImageDraw.Draw(bg)

        try:
            title_font = ImageFont.truetype(FONT_TITLE, 52)
            axiom_font = ImageFont.truetype(FONT_AXIOM, 30)
            meta_font = ImageFont.truetype(FONT_META, 32)
            time_font = ImageFont.truetype(FONT_TIME, 28)
        except:
            title_font = ImageFont.load_default()
            axiom_font = title_font
            meta_font = title_font
            time_font = title_font

        trimmed = trim_text(title, title_font, MAX_TITLE_WIDTH)
        draw.text((TITLE_X + 1, TITLE_Y + 1), trimmed, fill=(0, 0, 0, 100), font=title_font)
        draw.text((TITLE_X, TITLE_Y), trimmed, fill="white", font=title_font)

        draw.text((TITLE_X, META_Y), f"Channel | {channel}",
                  fill=(190, 190, 190), font=axiom_font)

        draw.text((TITLE_X, VIEWS_Y), f"Views | {views}",
                  fill=(190, 190, 190), font=axiom_font)

        draw.text((TITLE_X, PLAYER_Y), f"Player | @Kirtiprobot",
                  fill=(190, 190, 190), font=axiom_font)

        draw.text((TITLE_X, DEV_Y), "",
                  fill=(190, 190, 190), font=axiom_font)

        try:
            from unidecode import unidecode
            clean_name = re.sub(r'<[^>]+>', '', str(user_name))
            clean_name = unidecode(clean_name).strip()
        except:
            clean_name = re.sub(r'<[^>]+>', '', str(user_name)).strip()
        
        if not clean_name:
            clean_name = "BADNAM"
        
        prefix_text = "Requested By | "
        draw.text((TITLE_X, DEV_Y), prefix_text, 
                  fill=(190, 190, 190), font=axiom_font)
        
        prefix_width = axiom_font.getlength(prefix_text)
        draw.text((TITLE_X + prefix_width, DEV_Y), clean_name, 
                  fill=accent, font=axiom_font)

        bar_end = BAR_X + BAR_WIDTH
        draw.rounded_rectangle(
            [(BAR_X, BAR_Y), (bar_end, BAR_Y + BAR_HEIGHT)],
            radius=10, fill=(60, 60, 60)
        )

        progress = int(BAR_WIDTH * (progress_percent / 100))
        draw.rounded_rectangle(
            [(BAR_X, BAR_Y), (BAR_X + progress, BAR_Y + BAR_HEIGHT)],
            radius=10, fill=accent
        )

        cx, cy = BAR_X + progress, BAR_Y + BAR_HEIGHT // 2
        
        for glow_size, alpha in [(12, 30), (8, 60), (4, 100)]:
            draw.ellipse([(cx - glow_size, cy - glow_size), 
                         (cx + glow_size, cy + glow_size)],
                        fill=(*accent, alpha))
        
        draw.ellipse([(cx - 3, cy - 3), (cx + 3, cy + 3)], fill="white")

        try:
            if duration and ":" in str(duration):
                parts = str(duration).split(":")
                if len(parts) == 2:
                    total_seconds = int(parts[0]) * 60 + int(parts[1])
                elif len(parts) == 3:
                    total_seconds = int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
                else:
                    total_seconds = 0
                
                current_seconds = int((progress_percent / 100) * total_seconds)
                current_minutes = current_seconds // 60
                current_secs = current_seconds % 60
                current_time = f"{current_minutes}:{current_secs:02d}"
            else:
                current_time = "0:00"
        except:
            current_time = "0:00"

        draw.text((BAR_X, TIME_Y), current_time, fill=(200, 200, 200), font=time_font)  
        total = duration_text if not is_live else "LIVE"
        draw.text((bar_end - 50, TIME_Y), total, fill=(200, 200, 200), font=time_font)  

        bg = bg.convert("RGB")
        bg.save(cache_path, "PNG", quality=100)
        print(f"✓ Thumbnail saved with color RGB{accent} | Progress: {progress_percent}%")

    except Exception as e:
        import traceback
        print(f"Error: {e}")
        traceback.print_exc()
        return YOUTUBE_IMG_URL
    finally:
        try:
            if os.path.exists(thumb_path):
                os.remove(thumb_path)
        except:
            pass

    return cache_path
