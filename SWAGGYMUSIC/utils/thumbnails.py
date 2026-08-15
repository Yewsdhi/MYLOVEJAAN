import asyncio
import os, aiofiles, aiohttp
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
from py_yt import VideosSearch
from config import YOUTUBE_IMG_URL
from SWAGGYMUSIC import app

CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)

def trim_to_width(text: str, font: ImageFont.FreeTypeFont, max_width: int) -> str:
    ellipsis = "..."
    if font.getlength(text) <= max_width:
        return text
    for i in range(len(text), 0, -1):
        new = text[:i] + ellipsis
        if font.getlength(new) <= max_width:
            return new
    return ellipsis

def _generate_thumb_sync(videoid: str, title: str, artist: str, duration: str,
                          views: str, thumbnail_url: str, player_username: str) -> str:
    """Synchronous PIL processing — runs in thread executor to avoid
    blocking the asyncio event loop. Returns the cached thumbnail path
    or YOUTUBE_IMG_URL on failure."""
    cache_path = os.path.join(CACHE_DIR, f"{videoid}_shashank.png")
    if os.path.exists(cache_path):
        return cache_path

    thumb_path = os.path.join(CACHE_DIR, f"raw_{videoid}.jpg")
    try:
        import urllib.request
        urllib.request.urlretrieve(thumbnail_url, thumb_path)
    except Exception:
        return YOUTUBE_IMG_URL

    W, H = 1280, 720
    img = Image.open(thumb_path).convert("RGBA")
    bg = img.resize((W, H))
    bg = bg.filter(ImageFilter.GaussianBlur(radius=40))
    enhancer = ImageEnhance.Brightness(bg)
    bg = enhancer.enhance(0.4) # Darken background

    draw = ImageDraw.Draw(bg)

    try:
        font_bold = "SWAGGYMUSIC/assets/font2.ttf"
        font_med = "SWAGGYMUSIC/assets/font.ttf"
        title_font = ImageFont.truetype(font_bold, 60)
        artist_font = ImageFont.truetype(font_med, 40)
        time_font = ImageFont.truetype(font_med, 32)
    except:
        title_font = artist_font = time_font = ImageFont.load_default()

    frame_w, frame_h = 450, 450
    frame_x, frame_y = 100, (H - frame_h) // 2

    album = img.resize((frame_w, frame_h), Image.LANCZOS)

    mask = Image.new("L", (frame_w, frame_h), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, frame_w, frame_h), radius=40, fill=255)

    glow = Image.new("RGBA", (frame_w + 40, frame_h + 40), (0, 0, 0, 0))
    ImageDraw.Draw(glow).rounded_rectangle((20, 20, frame_w + 20, frame_h + 20), radius=40, fill=(0, 0, 0, 150))
    glow = glow.filter(ImageFilter.GaussianBlur(radius=15))
    bg.paste(glow, (frame_x - 20, frame_y - 20), glow)

    bg.paste(album, (frame_x, frame_y), mask)

    draw.rounded_rectangle(
        (frame_x, frame_y, frame_x + frame_w, frame_y + frame_h),
        radius=40,
        outline=(255, 255, 255, 80),
        width=6
    )

    text_x = 620
    glass_rect = [text_x - 40, frame_y, W - 60, frame_y + frame_h]
    overlay = Image.new('RGBA', (W, H), (0,0,0,0))
    d_overlay = ImageDraw.Draw(overlay)
    d_overlay.rounded_rectangle(glass_rect, radius=30, fill=(255, 255, 255, 25))
    bg.alpha_composite(overlay)

    clean_title = trim_to_width(title, title_font, 600)
    draw.text((text_x, frame_y + 40), clean_title, font=title_font, fill=(255, 255, 255, 255))

    clean_artist = trim_to_width(f"By {artist}", artist_font, 550)
    draw.text((text_x, frame_y + 120), clean_artist, font=artist_font, fill=(200, 200, 200, 230))

    draw.text((text_x, frame_y + 190), f"Views: {views}", font=time_font, fill=(180, 180, 180, 200))

    bar_width = 500
    bar_height = 8
    bar_x_pos = text_x
    bar_y_pos = frame_y + 320

    draw.rounded_rectangle((bar_x_pos, bar_y_pos, bar_x_pos + bar_width, bar_y_pos + bar_height), radius=4, fill=(255, 255, 255, 50))

    progress = 0.4
    draw.rounded_rectangle((bar_x_pos, bar_y_pos, bar_x_pos + (bar_width * progress), bar_y_pos + bar_height), radius=4, fill=(0, 200, 255, 255))

    circle_r = 10
    draw.ellipse((bar_x_pos + (bar_width * progress) - circle_r, bar_y_pos + (bar_height/2) - circle_r,
                  bar_x_pos + (bar_width * progress) + circle_r, bar_y_pos + (bar_height/2) + circle_r),
                  fill=(255, 255, 255, 255))

    draw.text((bar_x_pos, bar_y_pos + 25), "00:25", font=time_font, fill=(255, 255, 255, 200))
    draw.text((bar_x_pos + bar_width - 80, bar_y_pos + 25), str(duration), font=time_font, fill=(255, 255, 255, 200))

    bg = bg.convert("RGB")
    bg.save(cache_path, quality=95)

    try:
        os.remove(thumb_path)
    except:
        pass

    return cache_path


async def get_thumb(videoid: str, player_username: str = None) -> str:
    if player_username is None:
        player_username = app.username

    cache_path = os.path.join(CACHE_DIR, f"{videoid}_shashank.png")
    if os.path.exists(cache_path):
        return cache_path

    try:
        results = VideosSearch(f"https://www.youtube.com/watch?v={videoid}", limit=1)
        search_result = await results.next()
        data = search_result.get("result", [])[0]

        title = data.get("title") or "Unknown Title"
        artist = data.get("channel", {}).get("name") or "Unknown Artist"
        duration = data.get("duration") or "00:00"
        views = data.get("viewCount", {}).get("short") or "0 views"
        thumbnail = data.get("thumbnails", [{}])[0].get("url") or YOUTUBE_IMG_URL
    except Exception:
        title = "Unknown Title"
        artist = "Unknown Artist"
        duration = "05:00"
        views = "1M views"
        thumbnail = YOUTUBE_IMG_URL

    # Run the PIL processing in a thread executor so it doesn't block
    # the asyncio event loop (PIL is synchronous and CPU-intensive).
    try:
        return await asyncio.to_thread(
            _generate_thumb_sync,
            videoid, title, artist, duration, views, thumbnail, player_username
        )
    except Exception:
        return YOUTUBE_IMG_URL
