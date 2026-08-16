import asyncio
import os
import re
from typing import Union
import yt_dlp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from py_yt import VideosSearch
import aiohttp

from SWAGGYMUSIC.logging import LOGGER

# SHRUTI API endpoint and key. Updated to match the newer api01.shrutibots.site
# endpoint used by the reference Meera Music bot — the older api.shrutibots.site
# endpoint became unreliable (rate-limited / deprecated) and was the root cause
# of AutoPlay silently stopping after a handful of songs: every audio download
# started returning error responses, so all autoplay candidates failed and the
# bot fell through to "The Music Queue Has Ended".
API_URL = os.environ.get("SHRUTI_API_URL", "https://api01.shrutibots.site")

API_KEY = os.environ.get("SHRUTI_API_KEY", "ShrutiBotsAlSpfeG7JItQmuoxCqKd") ## Get This API KEY FROM TELEGRAM BOT USERNAME: @SHRUTIAPIBOT

DOWNLOAD_DIR = "downloads"

# Minimum size for a real audio/video file. Anything smaller is almost
# certainly an error page (SHRUTI's API sometimes returns a ~38KB Telegram
# web-preview HTML page with content-type: audio/mpeg when the backend is
# degraded). Without this guard, the HTML gets saved as .mp3 and PyTgCalls
# / ffmpeg then spends minutes trying to probe it as audio before failing.
_MIN_AUDIO_BYTES = 100_000  # ~100 KB — a real song is at least 1–3 MB
_MIN_VIDEO_BYTES = 200_000  # ~200 KB — a real video is at least a few MB


def _looks_like_audio(data: bytes) -> bool:
    """Heuristic check: real audio/video files start with known magic
    bytes (ID3 for MP3, ftyp for MP4/M4A, RIFF for WAV, OggS for Ogg,
    \x1A\x45\xDF for WebM/Matroska). HTML responses start with `<!DOCTYPE`
    or `<html`. If we see HTML or the size is too small, treat it as a
    failure so the caller can fall back rather than feeding garbage to
    ffmpeg."""
    if not data or len(data) < 2048:
        return False
    head = data[:16]
    # Common audio/video magic bytes
    if head.startswith(b"ID3"):  # MP3 with ID3v2 tag
        return True
    if head.startswith(b"\xff\xfb") or head.startswith(b"\xff\xf3") or head.startswith(b"\xff\xfa"):
        # MP3 frame sync
        return True
    if head[4:8] == b"ftyp":  # MP4/M4A/M4V
        return True
    if head.startswith(b"RIFF") and head[8:12] == b"WAVE":
        return True
    if head.startswith(b"OggS"):
        return True
    if head.startswith(b"\x1a\x45\xdf\xa3"):
        # WebM / Matroska
        return True
    if head.startswith(b"\x00\x00\x00") and len(data) > _MIN_AUDIO_BYTES:
        # Could be a ftyp box with a different offset, or a generic
        # binary container. If it's big enough and starts with a NUL byte,
        # it's almost certainly a real media file, not HTML.
        return True
    # HTML / JSON / XML — definitely not audio
    if head[:5].lower() in (b"<!doc", b"<html", b"<?xml"):
        return False
    if head[:1] == b"{":
        return False
    # If it's big enough and doesn't look like text, accept it
    if len(data) >= _MIN_AUDIO_BYTES and b"<" not in head[:8]:
        return True
    return False


def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60 ** i for i, x in enumerate(reversed(stringt.split(":"))))


def _ytdlp_audio_sync(video_id: str) -> str:
    """yt-dlp fallback for audio downloads when SHRUTI API fails.
    Extracts the best-audio stream and saves it as downloads/<video_id>.mp3.
    Returns the file path on success, None on failure."""
    if not video_id or len(video_id) < 3:
        return None
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    file_path = os.path.join(DOWNLOAD_DIR, f"{video_id}.mp3")
    if os.path.exists(file_path) and os.path.getsize(file_path) > _MIN_AUDIO_BYTES:
        return file_path
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "no_progress": True,
        "format": "bestaudio/best",
        "outtmpl": file_path,
        "noplaylist": True,
        "default_search": "auto",
    }
    # Use cookies if available (helps with age-restricted / regional content).
    cookiefile = _cookie_file_ytdlp()
    if cookiefile:
        ydl_opts["cookiefile"] = cookiefile
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([f"https://www.youtube.com/watch?v={video_id}"])
    except Exception as e:
        LOGGER(__name__).warning(
            f"[DOWNLOAD] yt-dlp audio fallback failed for {video_id}: "
            f"{type(e).__name__}: {e}"
        )
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass
        return None
    if os.path.exists(file_path) and os.path.getsize(file_path) > _MIN_AUDIO_BYTES:
        return file_path
    return None


def _ytdlp_video_sync(video_id: str) -> str:
    """yt-dlp fallback for video downloads when SHRUTI API fails."""
    if not video_id or len(video_id) < 3:
        return None
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    file_path = os.path.join(DOWNLOAD_DIR, f"{video_id}.mp4")
    if os.path.exists(file_path) and os.path.getsize(file_path) > _MIN_VIDEO_BYTES:
        return file_path
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "no_progress": True,
        "format": "best[ext=mp4]/best",
        "outtmpl": file_path,
        "noplaylist": True,
        "default_search": "auto",
    }
    cookiefile = _cookie_file_ytdlp()
    if cookiefile:
        ydl_opts["cookiefile"] = cookiefile
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([f"https://www.youtube.com/watch?v={video_id}"])
    except Exception as e:
        LOGGER(__name__).warning(
            f"[DOWNLOAD] yt-dlp video fallback failed for {video_id}: "
            f"{type(e).__name__}: {e}"
        )
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass
        return None
    if os.path.exists(file_path) and os.path.getsize(file_path) > _MIN_VIDEO_BYTES:
        return file_path
    return None


def _cookie_file_ytdlp():
    """Pick a cookies.txt for yt-dlp from SWAGGYMUSIC/assets (Lustify path)."""
    import glob as _glob
    folder = os.path.join(os.getcwd(), "SWAGGYMUSIC", "assets")
    txt_files = _glob.glob(os.path.join(folder, "*.txt"))
    if not txt_files:
        return None
    return txt_files[0]


async def download_song(link: str) -> str:
    video_id = link.split("v=")[-1].split("&")[0] if "v=" in link else link
    if not video_id or len(video_id) < 3:
        return None

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    file_path = os.path.join(DOWNLOAD_DIR, f"{video_id}.mp3")
    if os.path.exists(file_path) and os.path.getsize(file_path) > _MIN_AUDIO_BYTES:
        return file_path

    # Primary: SHRUTI API. Timeout raised from 120s -> 300s to match the
    # reference Meera Music bot, which runs reliably overnight. Some legitimate
    # songs (long mixes, live sets) take longer than 120s to fully download.
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{API_URL}/download",
                params={"url": video_id, "type": "audio", "api_key": API_KEY},
                timeout=aiohttp.ClientTimeout(total=300)
            ) as resp:
                if resp.status == 200:
                    data = await resp.read()
                    if _looks_like_audio(data):
                        with open(file_path, "wb") as f:
                            f.write(data)
                        if os.path.exists(file_path) and os.path.getsize(file_path) > _MIN_AUDIO_BYTES:
                            return file_path
                LOGGER(__name__).warning(
                    f"[DOWNLOAD] SHRUTI audio returned status={resp.status} "
                    f"for {video_id}, falling back to yt-dlp"
                )
    except Exception as e:
        LOGGER(__name__).warning(
            f"[DOWNLOAD] SHRUTI audio raised for {video_id}: "
            f"{type(e).__name__}: {e}, falling back to yt-dlp"
        )
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass

    # Fallback: yt-dlp. This is the key resilience fix — when SHRUTI is
    # rate-limited or down (which was causing AutoPlay to stop after a few
    # songs), yt-dlp can still fetch the audio directly from YouTube.
    # Run in executor because yt-dlp is synchronous and would block the
    # asyncio event loop.
    try:
        loop = asyncio.get_event_loop()
        fallback_path = await loop.run_in_executor(None, _ytdlp_audio_sync, video_id)
        if fallback_path:
            return fallback_path
    except Exception as e:
        LOGGER(__name__).warning(
            f"[DOWNLOAD] yt-dlp audio executor failed for {video_id}: "
            f"{type(e).__name__}: {e}"
        )
    return None


async def download_video(link: str) -> str:
    video_id = link.split("v=")[-1].split("&")[0] if "v=" in link else link
    if not video_id or len(video_id) < 3:
        return None

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    file_path = os.path.join(DOWNLOAD_DIR, f"{video_id}.mp4")
    if os.path.exists(file_path) and os.path.getsize(file_path) > _MIN_VIDEO_BYTES:
        return file_path

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{API_URL}/download",
                params={"url": video_id, "type": "video", "api_key": API_KEY},
                timeout=aiohttp.ClientTimeout(total=600)
            ) as resp:
                if resp.status == 200:
                    data = await resp.read()
                    if _looks_like_audio(data):
                        with open(file_path, "wb") as f:
                            f.write(data)
                        if os.path.exists(file_path) and os.path.getsize(file_path) > _MIN_VIDEO_BYTES:
                            return file_path
                LOGGER(__name__).warning(
                    f"[DOWNLOAD] SHRUTI video returned status={resp.status} "
                    f"for {video_id}, falling back to yt-dlp"
                )
    except Exception as e:
        LOGGER(__name__).warning(
            f"[DOWNLOAD] SHRUTI video raised for {video_id}: "
            f"{type(e).__name__}: {e}, falling back to yt-dlp"
        )
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass

    try:
        loop = asyncio.get_event_loop()
        fallback_path = await loop.run_in_executor(None, _ytdlp_video_sync, video_id)
        if fallback_path:
            return fallback_path
    except Exception as e:
        LOGGER(__name__).warning(
            f"[DOWNLOAD] yt-dlp video executor failed for {video_id}: "
            f"{type(e).__name__}: {e}"
        )
    return None


class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.status = "https://www.youtube.com/oembed?url="
        self.listbase = "https://youtube.com/playlist?list="
        self.reg = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

    async def exists(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        return bool(re.search(self.regex, link))

    async def url(self, message_1: Message) -> Union[str, None]:
        messages = [message_1]
        if message_1.reply_to_message:
            messages.append(message_1.reply_to_message)
        for message in messages:
            if message.entities:
                for entity in message.entities:
                    if entity.type == MessageEntityType.URL:
                        text = message.text or message.caption
                        return text[entity.offset: entity.offset + entity.length]
            elif message.caption_entities:
                for entity in message.caption_entities:
                    if entity.type == MessageEntityType.TEXT_LINK:
                        return entity.url
        return None

    async def details(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        # When videoid=True, link is now https://www.youtube.com/watch?v=<vidid>.
        # Use the canonical i.ytimg.com thumbnail URL for that exact video id
        # instead of trusting VideosSearch to return the same video as top hit.
        results = VideosSearch(link, limit=10)
        try:
            res_list = (await results.next()).get("result", []) or []
        except Exception:
            res_list = []
        chosen = None
        if videoid and res_list:
            try:
                wanted = link.split("v=")[1].split("&")[0]
            except Exception:
                wanted = None
            if wanted:
                for r in res_list:
                    if str(r.get("id", "")) == str(wanted):
                        chosen = r
                        break
            if chosen is None and res_list:
                chosen = res_list[0]
        elif res_list:
            chosen = self._pick_official(res_list, link)
        if chosen is None:
            try:
                _vid = link.split("v=")[1].split("&")[0] if "v=" in link else link
            except Exception:
                _vid = link
            return (
                "Unknown Title",
                "0:00",
                0,
                f"https://i.ytimg.com/vi/{_vid}/hqdefault.jpg",
                _vid,
            )
        title = chosen["title"]
        duration_min = chosen.get("duration") or "0:00"
        vidid = chosen["id"]
        # Canonical thumbnail — 1:1 with the chosen video id, never wrong.
        thumbnail = f"https://i.ytimg.com/vi/{vidid}/hqdefault.jpg"
        duration_sec = int(time_to_seconds(duration_min)) if duration_min else 0
        return title, duration_min, duration_sec, thumbnail, vidid

    async def title(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            return result["title"]

    async def duration(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            return result["duration"]

    async def thumbnail(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        # Canonical YouTube thumbnail URL — always 1:1 with the exact video
        # id. The previous implementation called VideosSearch and used the
        # top result's thumbnail, which could be a *different* video.
        try:
            vid = link.split("v=")[1].split("&")[0]
        except Exception:
            vid = link
        return f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg"

    async def video(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        try:
            downloaded_file = await download_video(link)
            if downloaded_file:
                return 1, downloaded_file
            return 0, "Video download failed"
        except Exception as e:
            return 0, f"Video download error: {e}"

    async def playlist(self, link, limit, user_id, videoid: Union[bool, str] = None):
        if videoid:
            link = self.listbase + link
        if "&" in link:
            link = link.split("&")[0]
        try:
            plist = await Playlist.get(link)
        except Exception:
            return []
        videos = plist.get("videos") or []
        ids = []
        for data in videos[:limit]:
            if not data:
                continue
            vid = data.get("id")
            if not vid:
                continue
            ids.append(vid)
        return ids

    async def track(self, link: str, videoid: Union[bool, str] = None):
        # When videoid=True is passed, `link` is a bare YouTube video ID
        # (e.g. "dQw4w9WgXcQ"). Build the canonical watch-URL but DO NOT
        # rely on VideosSearch returning that exact video as the top hit —
        # py_yt / youtube-search-python can surface a related video instead,
        # which would give us the wrong title/duration/thumbnail for the
        # result the user actually selected. Instead we:
        #   1. Use the canonical i.ytimg.com thumbnail URL (1:1 with vidid).
        #   2. Search with limit=10 and pick the entry whose id *exactly*
        #      matches the requested videoid. If no exact match, fall back
        #      to the first result but with the canonical thumbnail URL so
        #      the thumbnail is always correct for the chosen video.
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]

        search_query = link
        results = VideosSearch(search_query, limit=10)
        chosen = None
        try:
            res_list = (await results.next()).get("result", []) or []
        except Exception:
            res_list = []

        if videoid and res_list:
            try:
                wanted = link.split("v=")[1].split("&")[0]
            except Exception:
                wanted = None
            if wanted:
                for r in res_list:
                    if str(r.get("id", "")) == str(wanted):
                        chosen = r
                        break
            if chosen is None:
                chosen = res_list[0]
        elif res_list:
            # Text/URL search mode — prefer official / authoritative uploads
            # (official artist channels, "Topic" auto-generated audio, VEVO,
            # channels whose name contains "Official"). Falls back to the
            # first result if none of the candidates look official.
            chosen = self._pick_official(res_list, search_query)

        if chosen is None:
            # No search result at all — synthesise a minimal details dict
            # so downstream code doesn't crash.
            import config as _cfg
            try:
                _vid = link.split("v=")[1].split("&")[0] if "v=" in link else link
            except Exception:
                _vid = link
            fallback_thumb = f"https://i.ytimg.com/vi/{_vid}/hqdefault.jpg"
            track_details = {
                "title": "Unknown Title",
                "link": link,
                "vidid": _vid,
                "duration_min": "0:00",
                "thumb": fallback_thumb,
            }
            return track_details, _vid

        title = chosen["title"]
        duration_min = chosen.get("duration") or "0:00"
        vidid = chosen["id"]
        yturl = chosen.get("link") or f"https://www.youtube.com/watch?v={vidid}"
        # ALWAYS prefer the canonical i.ytimg.com thumbnail for the chosen
        # video id. This is the root-cause fix for "wrong thumbnail" reports:
        # the search API's thumbnail URL is sometimes for a different video.
        thumbnail = f"https://i.ytimg.com/vi/{vidid}/hqdefault.jpg"
        track_details = {
            "title": title,
            "link": yturl,
            "vidid": vidid,
            "duration_min": duration_min,
            "thumb": thumbnail,
        }
        return track_details, vidid

    @staticmethod
    def _pick_official(results, query):
        """Pick the most authoritative result from a list of search hits.
        Heuristics (in order):
          1. Exact title+channel match where the channel looks official
             (contains 'Official', 'Topic', 'VEVO', or ends with 'VEVO').
          2. Channel name contains 'Official' or 'Topic' or 'VEVO'.
          3. Title contains 'Official' or 'Official Audio' or 'Official Video'.
          4. First result (YouTube's relevance ranking).
        We never hard-code specific channel IDs — the choice is driven by
        the search result's own title/channel metadata, which is what the
        user actually sees in the slider."""
        if not results:
            return None

        def channel_score(r):
            ch = (r.get("channel") or {}).get("name", "") or ""
            title = r.get("title", "") or ""
            ch_l = ch.lower()
            t_l = title.lower()
            score = 0
            if "official" in ch_l:
                score += 5
            if "vevo" in ch_l or ch_l.endswith("vevo"):
                score += 5
            if "topic" in ch_l:
                score += 4
            if "music" in ch_l:
                score += 1
            if "official" in t_l:
                score += 2
            if "official audio" in t_l or "official video" in t_l:
                score += 2
            # Prefer non-live, non-shorts results with a sane duration.
            dur = r.get("duration")
            if dur and ":" in str(dur):
                score += 1
            return score

        best = max(results, key=channel_score)
        # If the best score is 0 (nothing looks official), fall back to the
        # first result — that's what YouTube's relevance ranking picked.
        if channel_score(best) == 0:
            return results[0]
        return best

    async def formats(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        ytdl_opts = {"quiet": True}
        ydl = yt_dlp.YoutubeDL(ytdl_opts)
        with ydl:
            formats_available = []
            r = ydl.extract_info(link, download=False)
            for format in r["formats"]:
                try:
                    if "dash" not in str(format["format"]).lower():
                        formats_available.append(
                            {
                                "format": format["format"],
                                "filesize": format.get("filesize"),
                                "format_id": format["format_id"],
                                "ext": format["ext"],
                                "format_note": format["format_note"],
                                "yturl": link,
                            }
                        )
                except Exception:
                    continue
        return formats_available, link

    async def slider(self, link: str, query_type: int, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        a = VideosSearch(link, limit=10)
        result = (await a.next()).get("result")
        title = result[query_type]["title"]
        duration_min = result[query_type]["duration"]
        vidid = result[query_type]["id"]
        # Canonical thumbnail for the *exact* selected slider entry — never
        # a different video's art.
        thumbnail = f"https://i.ytimg.com/vi/{vidid}/hqdefault.jpg"
        return title, duration_min, thumbnail, vidid

    async def download(
        self,
        link: str,
        mystic,
        video: Union[bool, str] = None,
        videoid: Union[bool, str] = None,
        songaudio: Union[bool, str] = None,
        songvideo: Union[bool, str] = None,
        format_id: Union[bool, str] = None,
        title: Union[bool, str] = None,
    ) -> str:
        if videoid:
            link = self.base + link
        try:
            if video:
                downloaded_file = await download_video(link)
            else:
                downloaded_file = await download_song(link)
            if downloaded_file:
                return downloaded_file, True
            return None, False
        except Exception:
            return None, False


YouTube = YouTubeAPI()
