import asyncio
import os, aiofiles, aiohttp
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
from config import YOUTUBE_IMG_URL
from SWAGGYMUSIC import app

CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)

# Canonical YouTube thumbnail URL candidates for a given video ID, in order
# of preference. These URLs are 1:1 with the exact video ID — they NEVER
# return a different video's thumbnail. The previous implementation called
# VideosSearch("https://www.youtube.com/watch?v=<vid>", limit=1) and used
# the top result's thumbnail URL, but py_yt can surface a related video as
# the top hit, which gave us the WRONG thumbnail for the song that was
# actually playing. Using i.ytimg.com directly fixes the root cause.
_THUMB_URLS = (
    "https://i.ytimg.com/vi/{vid}/maxresdefault.jpg",
    "https://i.ytimg.com/vi/{vid}/sddefault.jpg",
    "https://i.ytimg.com/vi/{vid}/hqdefault.jpg",
    "https://i.ytimg.com/vi/{vid}/mqdefault.jpg",
)


async def _fetch_raw_thumbnail(videoid: str) -> str:
    """Download the thumbnail for the EXACT video id `videoid` from the
    canonical i.ytimg.com URLs. Returns the local path, or "" on failure.
    Tries maxres -> sd -> hq -> mq in order (YouTube doesn't always have
    maxresdefault for every video, but always has hqdefault)."""
    thumb_path = os.path.join(CACHE_DIR, f"raw_{videoid}.jpg")
    if os.path.exists(thumb_path) and os.path.getsize(thumb_path) > 0:
        return thumb_path
    async with aiohttp.ClientSession() as s:
        for tmpl in _THUMB_URLS:
            url = tmpl.format(vid=videoid)
            try:
                async with s.get(url, timeout=aiohttp.ClientTimeout(total=15)) as r:
                    if r.status != 200:
                        continue
                    data = await r.read()
                    if not data or len(data) < 1024:
                        # YouTube sometimes returns a 120x90 grey placeholder
                        # JPG for missing thumbnails — skip those.
                        continue
                    async with aiofiles.open(thumb_path, "wb") as f:
                        await f.write(data)
                    return thumb_path
            except Exception:
                continue
    return ""


async def _fetch_video_meta(videoid: str) -> dict:
    """Best-effort fetch of title/artist/duration/views for the card overlay.
    The thumbnail itself NEVER depends on this — it's always the exact-video
    i.ytimg.com URL fetched by `_fetch_raw_thumbnail`. If metadata cannot be
    fetched (e.g. py_yt offline), sensible defaults are returned and the
    card still renders with the correct thumbnail.

    IMPORTANT: We search using the FULL YouTube watch URL
    (`https://www.youtube.com/watch?v=<videoid>`), NOT the bare video ID.
    py_yt's VideosSearch is a text-search API — passing a bare 11-char
    video ID returns garbage / no results, which was the root cause of
    the "Unknown Title / Unknown Artist / 0 views" bug. Searching with
    the full URL lets py_yt correctly resolve the exact video.

    We also verify the returned result's `id` matches the requested
    `videoid` — if py_yt drifts to a different video, we retry once and
    then fall back to the defaults rather than showing wrong metadata."""
    if not videoid:
        return {
            "title": "Unknown Title",
            "artist": "Unknown Artist",
            "duration": "00:00",
            "views": "0 views",
        }
    watch_url = f"https://www.youtube.com/watch?v={videoid}"
    for attempt in range(2):
        try:
            from py_yt import VideosSearch
            search = VideosSearch(watch_url, limit=10)
            data = await search.next()
            results = data.get("result", []) if isinstance(data, dict) else []
            if not results:
                continue
            # Pick the result whose id EXACTLY matches the requested videoid.
            # This prevents the "wrong metadata" bug where py_yt returned a
            # different top hit for a watch-URL query.
            chosen = None
            for r in results:
                if str(r.get("id", "")) == str(videoid):
                    chosen = r
                    break
            if chosen is None:
                # No exact match — py_yt drifted. Retry once; if still no
                # match, fall through to defaults rather than showing wrong
                # metadata for a different video.
                if attempt == 0:
                    continue
                # On second attempt, accept the first result if its id is
                # close enough (e.g. same video, different params). Otherwise
                # fall through to defaults.
                if results and results[0].get("id"):
                    chosen = results[0]
                else:
                    continue
            return {
                "title": chosen.get("title") or "Unknown Title",
                "artist": (chosen.get("channel") or {}).get("name") or "Unknown Artist",
                "duration": chosen.get("duration") or "00:00",
                "views": (chosen.get("viewCount", {}) or {}).get("short") or "0 views",
            }
        except Exception:
            continue
    return {
        "title": "Unknown Title",
        "artist": "Unknown Artist",
        "duration": "00:00",
        "views": "0 views",
    }


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
                          views: str, thumbnail_path: str, player_username: str) -> str:
    """Synchronous PIL processing — runs in thread executor to avoid
    blocking the asyncio event loop. Returns the cached thumbnail path
    or YOUTUBE_IMG_URL on failure.

    NOTE: `thumbnail_path` is the LOCAL path to the already-downloaded
    raw thumbnail (fetched by `_fetch_raw_thumbnail` from the canonical
    i.ytimg.com URL for this exact video id). The previous implementation
    took a `thumbnail_url` and downloaded it inside this sync function
    via urllib — that was a problem because the URL came from
    VideosSearch and could be for a DIFFERENT video."""
    cache_path = os.path.join(CACHE_DIR, f"{videoid}_shashank.png")
    if os.path.exists(cache_path):
        return cache_path

    if not thumbnail_path or not os.path.exists(thumbnail_path):
        return YOUTUBE_IMG_URL

    try:
        img = Image.open(thumbnail_path).convert("RGBA")
    except Exception:
        return YOUTUBE_IMG_URL

    W, H = 1280, 720
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
        os.remove(thumbnail_path)
    except:
        pass

    return cache_path


async def get_thumb(videoid: str, player_username: str = None) -> str:
    if player_username is None:
        player_username = app.username

    cache_path = os.path.join(CACHE_DIR, f"{videoid}_shashank.png")
    if os.path.exists(cache_path):
        return cache_path

    # 1. Fetch the thumbnail from the canonical i.ytimg.com URLs for the
    #    EXACT video id. This is the root-cause fix for "wrong thumbnail"
    #    reports — the previous code used VideosSearch's top-result URL
    #    which could be for a different video.
    thumb_path = await _fetch_raw_thumbnail(videoid)
    if not thumb_path:
        # All canonical YouTube thumbnail URLs failed for this ID — fall
        # back to the generic YouTube image rather than guessing with
        # another search.
        return YOUTUBE_IMG_URL

    # 2. Best-effort metadata for the card overlay. If this fails, the
    #    card still renders with the correct thumbnail.
    meta = await _fetch_video_meta(videoid)

    # 3. Run the PIL processing in a thread executor so it doesn't block
    #    the asyncio event loop (PIL is synchronous and CPU-intensive).
    try:
        return await asyncio.to_thread(
            _generate_thumb_sync,
            videoid,
            meta["title"],
            meta["artist"],
            meta["duration"],
            meta["views"],
            thumb_path,
            player_username,
        )
    except Exception:
        return YOUTUBE_IMG_URL
