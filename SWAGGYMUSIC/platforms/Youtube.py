import asyncio
import os
import re
from typing import Union

import aiohttp
import yt_dlp
from py_yt import VideosSearch
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message

try:
    from youtubesearchpython import Playlist
except Exception:
    Playlist = None


API_URL = os.environ.get(
    "SHRUTI_API_URL",
    "https://api01.shrutibots.site",
)

API_KEY = os.environ.get(
    "SHRUTI_API_KEY",
    "ShrutiBotsAlSpfeG7JItQmuoxCqKd",
)

DOWNLOAD_DIR = "downloads"


def time_to_seconds(time):
    if not time:
        return 0

    try:
        stringt = str(time)
        return sum(
            int(x) * 60 ** i
            for i, x in enumerate(
                reversed(stringt.split(":"))
            )
        )
    except Exception:
        return 0


def extract_video_id(link: str) -> str:
    """Extract a YouTube video ID from URL or return the ID itself."""
    if not link:
        return ""

    link = str(link).strip()

    if "youtu.be/" in link:
        video_id = link.split("youtu.be/", 1)[1]
        video_id = video_id.split("?", 1)[0]
        video_id = video_id.split("&", 1)[0]
        return video_id

    if "youtube.com" in link:
        match = re.search(
            r"(?:v=|embed/|shorts/|live/)([^?&/]+)",
            link,
        )

        if match:
            return match.group(1)

    return link.split("&")[0].split("?")[0]


def normalize_youtube_url(link: str) -> str:
    """Normalize video ID or YouTube URL."""
    if not link:
        return ""

    link = str(link).strip()

    if link.startswith(
        (
            "https://www.youtube.com/",
            "http://www.youtube.com/",
            "https://youtube.com/",
            "http://youtube.com/",
            "https://youtu.be/",
            "http://youtu.be/",
        )
    ):
        return link.split("&")[0]

    video_id = extract_video_id(link)

    return f"https://www.youtube.com/watch?v={video_id}"


async def download_song(link: str) -> str:
    video_id = extract_video_id(link)

    if not video_id or len(video_id) < 3:
        return None

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    file_path = os.path.join(
        DOWNLOAD_DIR,
        f"{video_id}.mp3",
    )

    if (
        os.path.exists(file_path)
        and os.path.getsize(file_path) > 0
    ):
        return file_path

    try:
        url = f"{API_URL}/download"

        params = {
            "url": normalize_youtube_url(video_id),
            "type": "audio",
            "api_key": API_KEY,
        }

        timeout = aiohttp.ClientTimeout(total=300)

        async with aiohttp.ClientSession(
            timeout=timeout
        ) as session:

            async with session.get(
                url,
                params=params,
            ) as resp:

                if resp.status != 200:
                    return None

                with open(
                    file_path,
                    "wb",
                ) as f:

                    async for chunk in resp.content.iter_chunked(
                        131072
                    ):
                        if chunk:
                            f.write(chunk)

        if (
            os.path.exists(file_path)
            and os.path.getsize(file_path) > 0
        ):
            return file_path

        return None

    except Exception:

        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception:
            pass

        return None


async def download_video(link: str) -> str:
    video_id = extract_video_id(link)

    if not video_id or len(video_id) < 3:
        return None

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    file_path = os.path.join(
        DOWNLOAD_DIR,
        f"{video_id}.mp4",
    )

    if (
        os.path.exists(file_path)
        and os.path.getsize(file_path) > 0
    ):
        return file_path

    try:
        url = f"{API_URL}/download"

        params = {
            "url": normalize_youtube_url(video_id),
            "type": "video",
            "api_key": API_KEY,
        }

        timeout = aiohttp.ClientTimeout(total=600)

        async with aiohttp.ClientSession(
            timeout=timeout
        ) as session:

            async with session.get(
                url,
                params=params,
            ) as resp:

                if resp.status != 200:
                    return None

                with open(
                    file_path,
                    "wb",
                ) as f:

                    async for chunk in resp.content.iter_chunked(
                        131072
                    ):
                        if chunk:
                            f.write(chunk)

        if (
            os.path.exists(file_path)
            and os.path.getsize(file_path) > 0
        ):
            return file_path

        return None

    except Exception:

        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception:
            pass

        return None


class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="

        self.regex = (
            r"(?:youtube\.com|youtu\.be)"
        )

        self.status = (
            "https://www.youtube.com/oembed?url="
        )

        self.listbase = (
            "https://youtube.com/playlist?list="
        )

        self.reg = re.compile(
            r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])"
        )

    async def exists(
        self,
        link: str,
        videoid: Union[bool, str] = None,
    ):
        if videoid:
            link = self.base + str(link)

        return bool(
            re.search(
                self.regex,
                str(link),
            )
        )

    async def url(
        self,
        message_1: Message,
    ) -> Union[str, None]:

        messages = [message_1]

        if message_1.reply_to_message:
            messages.append(
                message_1.reply_to_message
            )

        for message in messages:

            entities = (
                message.entities
                or message.caption_entities
            )

            text = (
                message.text
                or message.caption
                or ""
            )

            if not entities:
                continue

            for entity in entities:

                if (
                    entity.type
                    == MessageEntityType.TEXT_LINK
                ):
                    return entity.url

                if (
                    entity.type
                    == MessageEntityType.URL
                ):
                    return text[
                        entity.offset:
                        entity.offset + entity.length
                    ]

        return None

    async def details(
        self,
        link: str,
        videoid: Union[bool, str] = None,
    ):
        if videoid:
            link = self.base + str(link)

        link = str(link).split("&")[0]

        results = VideosSearch(
            link,
            limit=1,
        )

        result = (
            await results.next()
        ).get("result", [])

        if not result:
            return (
                "Unknown",
                "0:00",
                0,
                "",
                extract_video_id(link),
            )

        data = result[0]

        title = data.get(
            "title",
            "Unknown",
        )

        duration_min = (
            data.get("duration")
            or "LIVE"
        )

        duration_sec = (
            time_to_seconds(duration_min)
            if duration_min != "LIVE"
            else 0
        )

        thumbnails = (
            data.get("thumbnails")
            or []
        )

        thumbnail = ""

        if thumbnails:
            thumbnail = (
                thumbnails[0]
                .get("url", "")
                .split("?")[0]
            )

        vidid = data.get(
            "id",
            extract_video_id(link),
        )

        return (
            title,
            duration_min,
            duration_sec,
            thumbnail,
            vidid,
        )

    async def title(
        self,
        link: str,
        videoid: Union[bool, str] = None,
    ):
        data = await self.details(
            link,
            videoid,
        )

        return data[0]

    async def duration(
        self,
        link: str,
        videoid: Union[bool, str] = None,
    ):
        data = await self.details(
            link,
            videoid,
        )

        return data[1]

    async def thumbnail(
        self,
        link: str,
        videoid: Union[bool, str] = None,
    ):
        data = await self.details(
            link,
            videoid,
        )

        return data[3]

    async def video(
        self,
        link: str,
        videoid: Union[bool, str] = None,
    ):
        if videoid:
            link = self.base + str(link)

        try:
            downloaded_file = await download_video(link)

            if downloaded_file:
                return 1, downloaded_file

            return (
                0,
                "Video download failed",
            )

        except Exception as e:
            return (
                0,
                f"Video download error: {e}",
            )

    async def playlist(
        self,
        link,
        limit,
        user_id,
        videoid: Union[bool, str] = None,
    ):
        if videoid:
            link = self.listbase + str(link)

        if Playlist is None:
            return []

        try:
            plist = await Playlist.get(link)
        except Exception:
            return []

        videos = (
            plist.get("videos")
            or []
        )

        ids = []

        for data in videos[:limit]:

            if not data:
                continue

            vid = data.get("id")

            if vid:
                ids.append(vid)

        return ids

    async def track(
        self,
        link: str,
        videoid: Union[bool, str] = None,
    ):
        if videoid:
            link = self.base + str(link)

        link = str(link).split("&")[0]

        results = VideosSearch(
            link,
            limit=1,
        )

        result = (
            await results.next()
        ).get("result", [])

        if not result:
            return None, None

        data = result[0]

        title = data.get(
            "title",
            "Unknown",
        )

        duration_min = (
            data.get("duration")
            or "LIVE"
        )

        vidid = data.get(
            "id",
            extract_video_id(link),
        )

        yturl = data.get(
            "link",
            normalize_youtube_url(vidid),
        )

        thumbnails = (
            data.get("thumbnails")
            or []
        )

        thumbnail = ""

        if thumbnails:
            thumbnail = (
                thumbnails[0]
                .get("url", "")
                .split("?")[0]
            )

        track_details = {
            "title": title,
            "link": yturl,
            "vidid": vidid,
            "duration_min": duration_min,
            "thumb": thumbnail,
        }

        return (
            track_details,
            vidid,
        )

    # =============================================
    # YOUTUBE LIVE + NORMAL DIRECT STREAM
    # =============================================
    async def stream(
        self,
        link: str,
        videoid: Union[bool, str] = None,
        video: bool = False,
    ):
        """
        Extract a direct playable URL.

        Works with:
        - YouTube Live
        - Normal YouTube audio
        - Normal YouTube video
        - HLS / m3u8 streams
        """

        if videoid:
            link = self.base + str(link)

        link = normalize_youtube_url(link)

        if video:
            format_selector = (
                "bestvideo[protocol^=m3u8]+"
                "bestaudio[protocol^=m3u8]/"
                "best[protocol^=m3u8]/"
                "bestvideo+bestaudio/"
                "best"
            )
        else:
            format_selector = (
                "bestaudio[protocol^=m3u8]/"
                "bestaudio/"
                "best[protocol^=m3u8]/"
                "best"
            )

        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "noplaylist": True,
            "skip_download": True,
            "extract_flat": False,
            "format": format_selector,
            "socket_timeout": 30,
            "retries": 3,
            "fragment_retries": 3,
        }

        try:

            def extract():

                with yt_dlp.YoutubeDL(
                    ydl_opts
                ) as ydl:

                    return ydl.extract_info(
                        link,
                        download=False,
                    )

            info = await asyncio.to_thread(
                extract
            )

            if not info:
                return None, False

            if (
                info.get("_type")
                == "playlist"
            ):
                entries = (
                    info.get("entries")
                    or []
                )

                info = next(
                    (
                        entry
                        for entry in entries
                        if entry
                    ),
                    None,
                )

            if not info:
                return None, False

            direct_url = info.get("url")

            if direct_url:
                return (
                    direct_url,
                    True,
                )

            formats = (
                info.get("formats")
                or []
            )

            # =====================================
            # 1. HLS / M3U8 FORMAT
            # =====================================
            for fmt in formats:

                url = fmt.get("url")

                protocol = str(
                    fmt.get("protocol")
                    or ""
                ).lower()

                if not url:
                    continue

                if protocol not in (
                    "m3u8",
                    "m3u8_native",
                ):
                    continue

                if video:

                    if (
                        fmt.get("vcodec")
                        not in (
                            "none",
                            None,
                        )
                    ):
                        return url, True

                else:

                    if (
                        fmt.get("acodec")
                        not in (
                            "none",
                            None,
                        )
                    ):
                        return url, True

            # =====================================
            # 2. NORMAL MATCHING FORMAT
            # =====================================
            for fmt in formats:

                url = fmt.get("url")

                if not url:
                    continue

                if video:

                    if (
                        fmt.get("vcodec")
                        not in (
                            "none",
                            None,
                        )
                    ):
                        return url, True

                else:

                    if (
                        fmt.get("acodec")
                        not in (
                            "none",
                            None,
                        )
                    ):
                        return url, True

            # =====================================
            # 3. FINAL FALLBACK
            # =====================================
            for fmt in formats:

                url = fmt.get("url")

                if url:
                    return url, True

            return None, False

        except Exception as e:

            print(
                "[YOUTUBE STREAM ERROR] "
                f"{type(e).__name__}: {e}"
            )

            return None, False

    async def formats(
        self,
        link: str,
        videoid: Union[bool, str] = None,
    ):
        if videoid:
            link = self.base + str(link)

        link = normalize_youtube_url(link)

        ytdl_opts = {
            "quiet": True,
            "no_warnings": True,
            "noplaylist": True,
        }

        try:

            def extract():

                with yt_dlp.YoutubeDL(
                    ytdl_opts
                ) as ydl:

                    return ydl.extract_info(
                        link,
                        download=False,
                    )

            info = await asyncio.to_thread(
                extract
            )

            formats_available = []

            for fmt in (
                info.get("formats")
                or []
            ):

                try:

                    if (
                        "dash"
                        in str(
                            fmt.get("format")
                            or ""
                        ).lower()
                    ):
                        continue

                    formats_available.append(
                        {
                            "format": fmt.get(
                                "format"
                            ),
                            "filesize": fmt.get(
                                "filesize"
                            ),
                            "format_id": fmt.get(
                                "format_id"
                            ),
                            "ext": fmt.get(
                                "ext"
                            ),
                            "format_note": fmt.get(
                                "format_note"
                            ),
                            "yturl": link,
                        }
                    )

                except Exception:
                    continue

            return (
                formats_available,
                link,
            )

        except Exception:
            return [], link

    async def slider(
        self,
        link: str,
        query_type: int,
        videoid: Union[bool, str] = None,
    ):
        if videoid:
            link = self.base + str(link)

        results = VideosSearch(
            link,
            limit=10,
        )

        result = (
            await results.next()
        ).get("result", [])

        if not result:
            return (
                "Unknown",
                "0:00",
                "",
                "",
            )

        if query_type >= len(result):
            query_type = 0

        data = result[query_type]

        title = data.get(
            "title",
            "Unknown",
        )

        duration_min = (
            data.get("duration")
            or "LIVE"
        )

        vidid = data.get("id", "")

        thumbnails = (
            data.get("thumbnails")
            or []
        )

        thumbnail = ""

        if thumbnails:
            thumbnail = (
                thumbnails[0]
                .get("url", "")
                .split("?")[0]
            )

        return (
            title,
            duration_min,
            thumbnail,
            vidid,
        )

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
    ):
        if videoid:
            link = self.base + str(link)

        try:

            if video:
                downloaded_file = await download_video(
                    link
                )
            else:
                downloaded_file = await download_song(
                    link
                )

            if downloaded_file:
                return (
                    downloaded_file,
                    True,
                )

            return (
                None,
                False,
            )

        except Exception:
            return (
                None,
                False,
            )


YouTube = YouTubeAPI()
