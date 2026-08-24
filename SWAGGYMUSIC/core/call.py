import asyncio
import os
from datetime import datetime, timedelta
from typing import Union

from ntgcalls import ConnectionNotFound, TelegramServerError
from pyrogram import Client
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pytgcalls import PyTgCalls, exceptions, types
from pytgcalls.pytgcalls_session import PyTgCallsSession

import config
from SWAGGYMUSIC import LOGGER, YouTube, app
from SWAGGYMUSIC.misc import db
from SWAGGYMUSIC.utils.database import (
    add_active_chat,
    add_active_video_chat,
    get_lang,
    get_loop,
    group_assistant,
    is_autoend,
    is_autoplay_on,
    is_thumb_on,
    music_on,
    remove_active_chat,
    remove_active_video_chat,
    set_loop,
)
from SWAGGYMUSIC.utils.autoplay import (
    fetch_autoplay_track,
    remember_played,
)
from SWAGGYMUSIC.utils.exceptions import AssistantErr
from SWAGGYMUSIC.utils.formatters import (
    check_duration,
    seconds_to_min,
    speed_converter,
)
from SWAGGYMUSIC.utils.inline.play import stream_markup
from SWAGGYMUSIC.utils.stream.autoclear import auto_clean
from SWAGGYMUSIC.utils.stream.queue import put_queue
from SWAGGYMUSIC.utils.thumbnails import get_thumb
from strings import get_string


async def delete_old_message(chat_id: int):
    try:
        old = db.get(chat_id, [{}])[0].get("mystic")
        if old:
            await old.delete()
    except Exception:
        pass


autoend = {}
counter = {}


async def _clear_(chat_id: int):
    db[chat_id] = []

    try:
        await remove_active_video_chat(chat_id)
    except Exception:
        pass

    try:
        await remove_active_chat(chat_id)
    except Exception:
        pass


class Call(PyTgCalls):
    def __init__(self):
        PyTgCallsSession.notice_displayed = True

        self.userbot1 = Client(
            name="SwaggyXAss1",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING1),
        )

        self.one = PyTgCalls(
            self.userbot1,
            cache_duration=100,
        )

        self.userbot2 = Client(
            name="SwaggyXAss2",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING2),
        )

        self.two = PyTgCalls(
            self.userbot2,
            cache_duration=100,
        )

        self.userbot3 = Client(
            name="SwaggyXAss3",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING3),
        )

        self.three = PyTgCalls(
            self.userbot3,
            cache_duration=100,
        )

        self.userbot4 = Client(
            name="SwaggyXAss4",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING4),
        )

        self.four = PyTgCalls(
            self.userbot4,
            cache_duration=100,
        )

        self.userbot5 = Client(
            name="SwaggyXAss5",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING5),
        )

        self.five = PyTgCalls(
            self.userbot5,
            cache_duration=100,
        )

        self._change_stream_locks = {}

    def _build_stream(
        self,
        source: str,
        video: bool,
        ffmpeg: str | None = None,
    ):

        return types.MediaStream(
            media_path=source,
            audio_parameters=types.AudioQuality.HIGH,
            video_parameters=types.VideoQuality.HD_720p,
            audio_flags=types.MediaStream.Flags.REQUIRED,
            video_flags=(
                types.MediaStream.Flags.AUTO_DETECT
                if video
                else types.MediaStream.Flags.IGNORE
            ),
            ffmpeg_parameters=ffmpeg,
        )

    async def _play_on_assistant(
        self,
        client: PyTgCalls,
        chat_id: int,
        stream,
    ):
        return await client.play(
            chat_id=chat_id,
            stream=stream,
            config=types.GroupCallConfig(
                auto_start=False,
            ),
        )

    async def pause_stream(
        self,
        chat_id: int,
    ):
        await delete_old_message(chat_id)

        assistant = await group_assistant(
            self,
            chat_id,
        )

        await assistant.pause(chat_id)

    async def resume_stream(
        self,
        chat_id: int,
    ):
        await delete_old_message(chat_id)

        assistant = await group_assistant(
            self,
            chat_id,
        )

        await assistant.resume(chat_id)

    async def stop_stream(
        self,
        chat_id: int,
    ):
        await delete_old_message(chat_id)

        assistant = await group_assistant(
            self,
            chat_id,
        )

        try:
            await _clear_(chat_id)
            await assistant.leave_call(
                chat_id,
                close=False,
            )
        except Exception:
            pass

    async def stop_stream_force(
        self,
        chat_id: int,
    ):
        clients = [
            (config.STRING1, self.one),
            (config.STRING2, self.two),
            (config.STRING3, self.three),
            (config.STRING4, self.four),
            (config.STRING5, self.five),
        ]

        for string, client in clients:

            if not string:
                continue

            try:
                await client.leave_call(
                    chat_id,
                    close=False,
                )
            except Exception:
                pass

        await _clear_(chat_id)

    async def skip_stream(
        self,
        chat_id: int,
        link: str,
        video: Union[bool, str] = None,
        image: Union[bool, str] = None,
    ):

        assistant = await group_assistant(
            self,
            chat_id,
        )

        stream = self._build_stream(
            link,
            video=bool(video),
        )

        await self._play_on_assistant(
            assistant,
            chat_id,
            stream,
        )

    async def seek_stream(
        self,
        chat_id,
        file_path,
        to_seek,
        duration,
        mode,
    ):

        assistant = await group_assistant(
            self,
            chat_id,
        )

        stream = self._build_stream(
            file_path,
            video=(mode == "video"),
            ffmpeg=f"-ss {to_seek} -to {duration}",
        )

        await self._play_on_assistant(
            assistant,
            chat_id,
            stream,
        )

    async def stream_call(self, link):

        assistant = await group_assistant(
            self,
            config.LOGGER_ID,
        )

        stream = self._build_stream(
            link,
            video=True,
        )

        await self._play_on_assistant(
            assistant,
            config.LOGGER_ID,
            stream,
        )

        await asyncio.sleep(0.2)

        try:
            await assistant.leave_call(
                config.LOGGER_ID,
                close=False,
            )
        except Exception:
            pass

    async def join_call(
        self,
        chat_id: int,
        original_chat_id: int,
        link,
        video: Union[bool, str] = None,
        image: Union[bool, str] = None,
    ):

        assistant = await group_assistant(
            self,
            chat_id,
        )

        language = await get_lang(chat_id)
        _ = get_string(language)

        stream = self._build_stream(
            link,
            video=bool(video),
        )

        try:

            await self._play_on_assistant(
                assistant,
                chat_id,
                stream,
            )

        except exceptions.NoActiveGroupCall:
            raise AssistantErr(_["call_8"])

        except (
            exceptions.NoAudioSourceFound,
            ConnectionNotFound,
            TelegramServerError,
        ):
            raise AssistantErr(_["call_10"])

        except Exception:
            raise AssistantErr(_["call_10"])

        await add_active_chat(chat_id)
        await music_on(chat_id)

        if video:
            await add_active_video_chat(chat_id)

    # ==========================================
    # FAST AUTOPLAY
    # ==========================================

    async def autoplay_start(
        self,
        chat_id: int,
        original_chat_id: int,
        seed_title: str,
        seed_vidid: str = None,
        client: PyTgCalls = None,
    ):

        if seed_vidid:
            remember_played(
                chat_id,
                seed_vidid,
            )

        try:

            candidates = await fetch_autoplay_track(
                chat_id,
                seed_title,
                seed_vidid,
            )

        except Exception as e:

            LOGGER(__name__).warning(
                f"[AUTOPLAY] Search error: {e}"
            )

            return False

        if not candidates:
            return False

        assistant = (
            client
            or await group_assistant(
                self,
                chat_id,
            )
        )

        for track in candidates:

            vidid = track.get("vidid")

            if not vidid:
                continue

            try:

                # FAST DIRECT STREAM
                direct_url, success = (
                    await YouTube.stream(
                        vidid,
                        videoid=True,
                        video=False,
                    )
                )

                if not success or not direct_url:
                    continue

                title = (
                    track.get(
                        "title",
                        "Unknown",
                    ).title()
                )

                duration = track.get(
                    "duration_min",
                    "LIVE",
                )

                remember_played(
                    chat_id,
                    vidid,
                )

                await put_queue(
                    chat_id,
                    original_chat_id,
                    direct_url,
                    title,
                    duration,
                    "🔁 𝐀ᴜᴛᴏᴘʟᴀʏ",
                    vidid,
                    1,
                    "audio",
                    forceplay=True,
                )

                if db.get(chat_id):

                    db[chat_id][0]["played"] = 0
                    db[chat_id][0]["speed"] = 1.0
                    db[chat_id][0]["speed_path"] = None

                stream = self._build_stream(
                    direct_url,
                    video=False,
                )

                await self._play_on_assistant(
                    assistant,
                    chat_id,
                    stream,
                )

                return True

            except Exception as e:

                LOGGER(__name__).warning(
                    f"[AUTOPLAY] {vidid} failed: "
                    f"{type(e).__name__}: {e}"
                )

                continue

        return False

    async def _try_autoplay(
        self,
        chat_id,
        popped,
        client,
    ):

        if not popped:
            return False

        if not await is_autoplay_on(chat_id):
            return False

        for attempt in range(3):

            try:

                success = await self.autoplay_start(
                    chat_id,
                    popped.get(
                        "chat_id",
                        chat_id,
                    ),
                    popped.get(
                        "title",
                        "",
                    ),
                    popped.get(
                        "vidid",
                    ),
                    client,
                )

                if success:
                    return True

            except Exception as e:

                LOGGER(__name__).warning(
                    f"[AUTOPLAY] Attempt {attempt + 1}: {e}"
                )

            await asyncio.sleep(2)

        return False

    async def _handle_queue_ended(
        self,
        chat_id,
        client,
    ):

        await _clear_(chat_id)

        try:

            buttons = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "✙ ᴀᴅᴅ ᴍᴇ ʙᴀʙʏ ✙",
                            url=(
                                f"https://t.me/"
                                f"{app.username}"
                                f"?startgroup=true"
                            ),
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            "⋞ ᴄʟᴏsᴇ ⋟",
                            callback_data=(
                                "close_message"
                            ),
                        ),
                    ],
                ]
            )

            await app.send_message(
                chat_id,
                (
                    "🎵 𝐓ʜᴇ 𝐌ᴜsɪᴄ 𝐐ᴜᴇᴜᴇ "
                    "𝐇ᴀs 𝐄ɴᴅᴇ𝐝.\n\n"
                    "➤ 𝐔𝐬𝐞 /play 𝐓ᴏ "
                    "𝐀ᴅᴅ 𝐌ᴏʀᴇ 𝐒ᴏɴɢs 🎶"
                ),
                reply_markup=buttons,
            )

        except Exception:
            pass

        try:

            await client.leave_call(
                chat_id,
                close=False,
            )

        except Exception:
            pass

    async def change_stream(
        self,
        client,
        chat_id,
    ):

        await delete_old_message(chat_id)

        if chat_id not in self._change_stream_locks:
            self._change_stream_locks[
                chat_id
            ] = asyncio.Lock()

        async with self._change_stream_locks[chat_id]:

            check = db.get(chat_id, [])

            if not check:
                return await self._handle_queue_ended(
                    chat_id,
                    client,
                )

            popped = None

            try:

                loop = await get_loop(chat_id)

                if loop == 0:
                    popped = check.pop(0)

                    try:
                        await auto_clean(popped)
                    except Exception:
                        pass

                else:

                    loop -= 1

                    await set_loop(
                        chat_id,
                        loop,
                    )

            except Exception as e:

                LOGGER(__name__).warning(
                    f"[QUEUE] Pop error: {e}"
                )

            if not check:

                if await self._try_autoplay(
                    chat_id,
                    popped,
                    client,
                ):
                    return

                return await self._handle_queue_ended(
                    chat_id,
                    client,
                )

            current = check[0]

            queued = current.get("file")

            if not queued:

                return await self._handle_queue_ended(
                    chat_id,
                    client,
                )

            language = await get_lang(chat_id)
            _ = get_string(language)

            title = (
                current.get(
                    "title",
                    "Unknown",
                ).title()
            )

            user = current.get(
                "by",
                "Unknown",
            )

            original_chat_id = current.get(
                "chat_id",
                chat_id,
            )

            streamtype = current.get(
                "streamtype",
                "audio",
            )

            videoid = current.get(
                "vidid",
                "",
            )

            video = (
                streamtype == "video"
            )

            current["played"] = 0
            current["speed"] = 1.0
            current["speed_path"] = None

            # ===================================
            # LIVE STREAM
            # ===================================

            if "live_" in str(queued):

                link, success = (
                    await YouTube.stream(
                        videoid,
                        videoid=True,
                        video=video,
                    )
                )

                if not success:

                    return await app.send_message(
                        original_chat_id,
                        _["call_6"],
                    )

                queued = link
                current["file"] = link

            # ===================================
            # YOUTUBE FAST DIRECT STREAM
            # ===================================

            elif "vid_" in str(queued):

                try:

                    link, success = (
                        await YouTube.stream(
                            videoid,
                            videoid=True,
                            video=video,
                        )
                    )

                    if not success or not link:

                        raise RuntimeError(
                            "No direct stream URL"
                        )

                    queued = link

                    # IMPORTANT:
                    # Queue ko permanent YouTube URL se
                    # replace mat karo agar original prefix
                    # logic kahin use ho raha ho.
                    # Sirf current stream ke liye use hoga.

                except Exception as e:

                    LOGGER(__name__).warning(
                        f"[FAST STREAM] {videoid}: {e}"
                    )

                    if await self._try_autoplay(
                        chat_id,
                        popped,
                        client,
                    ):
                        return

                    return await self._handle_queue_ended(
                        chat_id,
                        client,
                    )

            # ===================================
            # TELEGRAM / LOCAL FILE
            # ===================================

            elif "index_" in str(queued):

                queued = videoid

            try:

                stream = self._build_stream(
                    queued,
                    video=video,
                )

                await self._play_on_assistant(
                    client,
                    chat_id,
                    stream,
                )

            except Exception as e:

                LOGGER(__name__).warning(
                    f"[PLAY] Error: {e}"
                )

                if popped and await self._try_autoplay(
                    chat_id,
                    popped,
                    client,
                ):
                    return

                return await self._handle_queue_ended(
                    chat_id,
                    client,
                )

            # ===================================
            # NOW PLAYING MESSAGE
            # ===================================

            try:

                thumb_on_now = (
                    await is_thumb_on(chat_id)
                )

                button = stream_markup(
                    _,
                    chat_id,
                    autoplay_status=(
                        await is_autoplay_on(
                            chat_id
                        )
                    ),
                    thumb_status=thumb_on_now,
                )

                if videoid == "telegram":

                    caption = _["stream_1"].format(
                        config.SUPPORT_CHAT,
                        title[:23],
                        current.get("dur", ""),
                        user,
                    )

                    image = (
                        config.TELEGRAM_VIDEO_URL
                        if video
                        else config.TELEGRAM_AUDIO_URL
                    )

                elif videoid == "soundcloud":

                    caption = _["stream_1"].format(
                        config.SUPPORT_CHAT,
                        title[:23],
                        current.get("dur", ""),
                        user,
                    )

                    image = config.SOUNCLOUD_IMG_URL

                else:

                    caption = _["stream_1"].format(
                        (
                            f"https://t.me/"
                            f"{app.username}"
                            f"?start=info_{videoid}"
                        ),
                        title[:23],
                        current.get("dur", ""),
                        user,
                    )

                    image = await get_thumb(
                        videoid,
                        title=title,
                        duration=current.get(
                            "dur",
                            "",
                        ),
                    )

                if thumb_on_now:

                    run = await app.send_photo(
                        chat_id=original_chat_id,
                        photo=image,
                        has_spoiler=True,
                        caption=caption,
                        reply_markup=InlineKeyboardMarkup(
                            button
                        ),
                    )

                else:

                    run = await app.send_message(
                        chat_id=original_chat_id,
                        text=caption,
                        disable_web_page_preview=True,
                        reply_markup=InlineKeyboardMarkup(
                            button
                        ),
                    )

                current["mystic"] = run
                current["markup"] = "stream"

            except Exception as e:

                LOGGER(__name__).warning(
                    f"[MESSAGE] {e}"
                )

    async def ping(self):

        pings = []

        for string, client in [
            (config.STRING1, self.one),
            (config.STRING2, self.two),
            (config.STRING3, self.three),
            (config.STRING4, self.four),
            (config.STRING5, self.five),
        ]:

            if string:
                try:
                    pings.append(
                        client.ping
                    )
                except Exception:
                    pass

        if not pings:
            return "0"

        return str(
            round(
                sum(pings) / len(pings),
                3,
            )
        )

    async def start(self):

        LOGGER(__name__).info(
            "Starting PyTgCalls Client..."
        )

        for string, client in [
            (config.STRING1, self.one),
            (config.STRING2, self.two),
            (config.STRING3, self.three),
            (config.STRING4, self.four),
            (config.STRING5, self.five),
        ]:

            if string:
                await client.start()

    async def decorators(self):

        clients = [
            (config.STRING1, self.one),
            (config.STRING2, self.two),
            (config.STRING3, self.three),
            (config.STRING4, self.four),
            (config.STRING5, self.five),
        ]

        for string, client in clients:

            if not string:
                continue

            @client.on_update()
            async def _update_handler(
                _,
                update: types.Update,
                _client=client,
            ):

                if isinstance(
                    update,
                    types.StreamEnded,
                ):

                    if (
                        update.stream_type
                        == types.StreamEnded.Type.AUDIO
                    ):

                        try:

                            await self.change_stream(
                                _client,
                                update.chat_id,
                            )

                        except Exception as e:

                            LOGGER(__name__).error(
                                f"[STREAM ENDED] "
                                f"{type(e).__name__}: {e}"
                            )

                elif isinstance(
                    update,
                    types.ChatUpdate,
                ):

                    if update.status in [
                        types.ChatUpdate.Status.KICKED,
                        types.ChatUpdate.Status.LEFT_GROUP,
                        types.ChatUpdate.Status.CLOSED_VOICE_CHAT,
                    ]:

                        try:

                            await self.stop_stream(
                                update.chat_id
                            )

                        except Exception:
                            pass


Swaggy = Call()
