import asyncio
import os
import re
from typing import Union

import aiohttp
import yt_dlp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from py_yt import VideosSearch

# Optional: playlist support
try:
    from py_yt import Playlist
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


def time_to_seconds(time) -> int:
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
    """Extract YouTube video ID safely."""
    if not link:
        return ""

    link = str(link).strip()

    # Already a video ID
    if (
        len(link) == 11
        and re.match(r"^[A-Za-z0-9_-]{11}$", link)
    ):
        return link

    patterns = [
        r"(?:v=)([A-Za-z0-9_-]{11})",
        r"youtu\.be/([A-Za-z0-9_-]{11})",
        r"youtube\.com/embed/([A-Za-z0-9_-]{11})",
        r"youtube\.com/live/([A-Za-z0-9_-]{11})",
        r"youtube\.com/shorts/([A-Za-z0-9_-]{11})",
    ]

    for pattern in patterns:
        match = re.search(pattern, link)
        if match:
            return match.group(1)

    return link.split("&")[0]


def normalize_youtube_url(link: str) -> str:
    if not link:
        return ""

    link = str(link).strip()

    if link.startswith("http://") or link.startswith("https://"):
        return link.split("&list=")[0]

    video_id = extract_video_id(link)

    if video_id:
        return f"https://www.youtube.com/watch?v={video_id}"

    return link


async def _download_from_api(
    video_id: str,
    file_path: str,
    media_type: str,
    timeout: int,
) -> Union[str, None]:
    """Download using Shruti API."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{API_URL}/download",
                params={
                    "url": video_id,
                    "type": media_type,
                    "api_key": API_KEY,
                },
                timeout=aiohttp.ClientTimeout(
                    total=timeout
                ),
            ) as resp:
                if resp.status != 200:
                    return None

                with open(file_path, "wb") as file:
                    async for chunk in resp.content.iter_chunked(
                        262144
                    ):
                        file.write(chunk)

        if (
            os.path.exists(file_path)
            and os.path.getsize(file_path) > 0
        ):
            return file_path

    except Exception:
        pass

    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception:
        pass

    return None


async def download_song(link: str) -> Union[str, None]:
    video_id = extract_video_id(link)

    if not video_id:
        return None

    os.makedirs(
        DOWNLOAD_DIR,
        exist_ok=True,
    )

    file_path = os.path.join(
        DOWNLOAD_DIR,
        f"{video_id}.mp3",
    )

    if (
        os.path.exists(file_path)
        and os.path.getsize(file_path) > 0
    ):
        return file_path

    result = await _download_from_api(
        video_id,
        file_path,
        "audio",
        300,
    )

    if result:
        return result

    # Fallback yt-dlp
    try:
        url = normalize_youtube_url(link)

        def download():
            opts = {
                "quiet": True,
                "no_warnings": True,
                "format": "bestaudio/best",
                "outtmpl": file_path.rsplit(
                    ".",
                    1,
                )[0] + ".%(ext)s",
                "noplaylist": True,
                "retries": 3,
                "extractor_retries": 3,
            }

            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(
                    url,
                    download=True,
                )

                filename = ydl.prepare_filename(
                    info
                )

                if os.path.exists(filename):
                    return filename

                return None

        result = await asyncio.to_thread(
            download
        )

        return result

    except Exception:
        return None


async def download_video(link: str) -> Union[str, None]:
    video_id = extract_video_id(link)

    if not video_id:
        return None

    os.makedirs(
        DOWNLOAD_DIR,
        exist_ok=True,
    )

    file_path = os.path.join(
        DOWNLOAD_DIR,
        f"{video_id}.mp4",
    )

    if (
        os.path.exists(file_path)
        and os.path.getsize(file_path) > 0
    ):
        return file_path

    result = await _download_from_api(
        video_id,
        file_path,
        "video",
        600,
    )

    if result:
        return result

    # yt-dlp fallback
    try:
        url = normalize_youtube_url(link)

        def download():
            opts = {
                "quiet": True,
                "no_warnings": True,
                "format": (
                    "bestvideo[height<=720]"
                    "+bestaudio/best[height<=720]"
                ),
                "merge_output_format": "mp4",
                "outtmpl": os.path.join(
                    DOWNLOAD_DIR,
                    f"{video_id}.%(ext)s",
                ),
                "noplaylist": True,
                "retries": 3,
                "extractor_retries": 3,
            }

            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(
                    url,
                    download=True,
                )

                filename = ydl.prepare_filename(
                    info
                )

                base = os.path.splitext(
                    filename
                )[0]

                mp4_file = base + ".mp4"

                if os.path.exists(mp4_file):
                    return mp4_file

                if os.path.exists(filename):
                    return filename

                return None

        return await asyncio.to_thread(
            download
        )

    except Exception:
        return None


class YouTubeAPI:

    def __init__(self):
        self.base = (
            "https://www.youtube.com/watch?v="
        )

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
    ) -> bool:

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

            if not message:
                continue

            text = (
                message.text
                or message.caption
                or ""
            )

            entities = (
                message.entities
                or message.caption_entities
                or []
            )

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

    async def stream(
        self,
        link: str,
        videoid: Union[bool, str] = None,
        video: bool = False,
    ):
        """
        Get a fresh direct YouTube stream URL.

        Returns:
            (url, True)  -> success
            (None, False) -> failure

        Important:
        Do NOT store the returned URL permanently in
        the queue because YouTube signed URLs expire.
        Store vid_<video_id> and generate a new URL
        whenever playback starts.
        """

        if videoid:
            link = self.base + str(link)

        url = normalize_youtube_url(
            link
        )

        # Audio / video format preferences
        if video:

            format_selector = (
                "best[protocol^=m3u8]"
                "/best[height<=720]"
                "/best"
            )

        else:

            format_selector = (
                "bestaudio[protocol^=m3u8]"
                "/bestaudio"
                "/best"
            )

        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "noplaylist": True,
            "skip_download": True,
            "format": format_selector,
            "socket_timeout": 20,
            "retries": 5,
            "extractor_retries": 5,
            "geo_bypass": True,
            "nocheckcertificate": True,
        }

        try:

            def extract():

                with yt_dlp.YoutubeDL(
                    ydl_opts
                ) as ydl:

                    return ydl.extract_info(
                        url,
                        download=False,
                    )

            info = await asyncio.to_thread(
                extract
            )

            if not info:
                return None, False

            # Playlist result
            if info.get("entries"):

                for entry in info["entries"]:

                    if (
                        entry
                        and entry.get("url")
                    ):
                        return (
                            entry["url"],
                            True,
                        )

            # Best direct stream URL
            direct_url = info.get("url")

            if direct_url:
                return (
                    direct_url,
                    True,
                )

            # Search available formats
            formats = (
                info.get("formats")
                or []
            )

            # Prefer requested media type
            for fmt in formats:

                fmt_url = fmt.get("url")

                if not fmt_url:
                    continue

                acodec = fmt.get(
                    "acodec",
                    "none",
                )

                vcodec = fmt.get(
                    "vcodec",
                    "none",
                )

                if video:

                    if (
                        vcodec
                        not in (
                            "none",
                            None,
                        )
                    ):
                        return (
                            fmt_url,
                            True,
                        )

                else:

                    if (
                        acodec
                        not in (
                            "none",
                            None,
                        )
                    ):
                        return (
                            fmt_url,
                            True,
                        )

            return None, False

        except Exception as error:

            print(
                "[YOUTUBE STREAM ERROR] "
                f"{type(error).__name__}: "
                f"{error}"
            )

            return None, False

    async def live_stream(
        self,
        link: str,
        video: bool = True,
    ):
        """
        Dedicated YouTube Live extractor.
        """

        url = normalize_youtube_url(
            link
        )

        if video:

            format_selector = (
                "best[protocol^=m3u8]"
                "/best"
            )

        else:

            format_selector = (
                "bestaudio[protocol^=m3u8]"
                "/bestaudio"
                "/best"
            )

        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "noplaylist": True,
            "skip_download": True,
            "format": format_selector,
            "socket_timeout": 30,
            "retries": 5,
            "extractor_retries": 5,
            "live_from_start": False,
            "geo_bypass": True,
            "nocheckcertificate": True,
        }

        try:

            def extract():

                with yt_dlp.YoutubeDL(
                    ydl_opts
                ) as ydl:

                    return ydl.extract_info(
                        url,
                        download=False,
                    )

            info = await asyncio.to_thread(
                extract
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

            for fmt in reversed(formats):

                fmt_url = fmt.get("url")

                if not fmt_url:
                    continue

                protocol = str(
                    fmt.get(
                        "protocol",
                        "",
                    )
                ).lower()

                if (
                    "m3u8"
                    in protocol
                ):
                    return (
                        fmt_url,
                        True,
                    )

            for fmt in formats:

                fmt_url = fmt.get("url")

                if fmt_url:
                    return (
                        fmt_url,
                        True,
                    )

            return None, False

        except Exception as error:

            print(
                "[YOUTUBE LIVE ERROR] "
                f"{type(error).__name__}: "
                f"{error}"
            )

            return None, False

    async def details(
        self,
        link: str,
        videoid: Union[bool, str] = None,
    ):

        if videoid:
            link = (
                self.base
                + str(link)
            )

        link = link.split("&")[0]

        results = VideosSearch(
            link,
            limit=1,
        )

        result = (
            await results.next()
        ).get(
            "result",
            [],
        )

        if not result:
            return (
                "Unknown",
                "0:00",
                0,
                "",
                "",
            )

        data = result[0]

        title = (
            data.get("title")
            or "Unknown"
        )

        duration_min = (
            data.get("duration")
            or "0:00"
        )

        thumbnails = (
            data.get("thumbnails")
            or []
        )

        thumbnail = (
            thumbnails[0]
            .get("url", "")
            .split("?")[0]
            if thumbnails
            else ""
        )

        vidid = (
            data.get("id")
            or extract_video_id(link)
        )

        duration_sec = (
            time_to_seconds(
                duration_min
            )
            if duration_min
            else 0
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

        details = await self.details(
            link,
            videoid,
        )

        return details[0]

    async def duration(
        self,
        link: str,
        videoid: Union[bool, str] = None,
    ):

        details = await self.details(
            link,
            videoid,
        )

        return details[1]

    async def thumbnail(
        self,
        link: str,
        videoid: Union[bool, str] = None,
    ):

        details = await self.details(
            link,
            videoid,
        )

        return details[3]

    async def video(
        self,
        link: str,
        videoid: Union[bool, str] = None,
    ):

        if videoid:
            link = (
                self.base
                + str(link)
            )

        # First get fresh stream URL
        stream_url, success = await self.live_stream(
            link,
            video=True,
        )

        if success:
            return (
                1,
                stream_url,
            )

        return (
            0,
            "Video stream extraction failed",
        )

    async def playlist(
        self,
        link,
        limit,
        user_id,
        videoid: Union[bool, str] = None,
    ):

        if videoid:
            link = (
                self.listbase
                + str(link)
            )

        if not Playlist:
            return []

        try:

            plist = await Playlist.get(
                link
            )

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
                ids.append(
                    vid
                )

        return ids

    async def track(
        self,
        link: str,
        videoid: Union[bool, str] = None,
    ):

        if videoid:
            link = (
                self.base
                + str(link)
            )

        link = link.split("&")[0]

        results = VideosSearch(
            link,
            limit=1,
        )

        result = (
            await results.next()
        ).get(
            "result",
            [],
        )

        if not result:
            return None, None

        data = result[0]

        title = (
            data.get("title")
            or "Unknown"
        )

        duration_min = (
            data.get("duration")
            or "0:00"
        )

        vidid = (
            data.get("id")
            or ""
        )

        yturl = (
            data.get("link")
            or self.base + vidid
        )

        thumbnails = (
            data.get("thumbnails")
            or []
        )

        thumbnail = (
            thumbnails[0]
            .get("url", "")
            .split("?")[0]
            if thumbnails
            else ""
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

    async def formats(
        self,
        link: str,
        videoid: Union[bool, str] = None,
    ):

        if videoid:
            link = (
                self.base
                + str(link)
            )

        link = link.split("&")[0]

        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "noplaylist": True,
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

            result = await asyncio.to_thread(
                extract
            )

        except Exception:
            return [], link

        formats_available = []

        for fmt in (
            result.get("formats")
            or []
        ):

            try:

                format_name = str(
                    fmt.get(
                        "format",
                        "",
                    )
                )

                if (
                    "dash"
                    in format_name.lower()
                ):
                    continue

                formats_available.append(
                    {
                        "format": format_name,
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

    async def slider(
        self,
        link: str,
        query_type: int,
        videoid: Union[bool, str] = None,
    ):

        if videoid:
            link = (
                self.base
                + str(link)
            )

        link = link.split("&")[0]

        search = VideosSearch(
            link,
            limit=10,
        )

        results = (
            await search.next()
        ).get(
            "result",
            [],
        )

        if not results:
            return (
                "Unknown",
                "0:00",
                "",
                "",
            )

        if query_type >= len(
            results
        ):
            query_type = 0

        data = results[
            query_type
        ]

        title = (
            data.get("title")
            or "Unknown"
        )

        duration_min = (
            data.get("duration")
            or "0:00"
        )

        vidid = (
            data.get("id")
            or ""
        )

        thumbnails = (
            data.get("thumbnails")
            or []
        )

        thumbnail = (
            thumbnails[0]
            .get("url", "")
            .split("?")[0]
            if thumbnails
            else ""
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
        mystic=None,
        video: Union[bool, str] = None,
        videoid: Union[bool, str] = None,
        songaudio: Union[bool, str] = None,
        songvideo: Union[bool, str] = None,
        format_id: Union[bool, str] = None,
        title: Union[bool, str] = None,
    ):

        # Download local file
        if videoid:
            link = (
                self.base
                + str(link)
            )

        try:

            if video:

                downloaded_file = (
                    await download_video(
                        link
                    )
                )

            else:

                downloaded_file = (
                    await download_song(
                        link
                    )
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
