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
from SWAGGYMUSIC.utils.autoplay import fetch_autoplay_track, remember_played
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
    await remove_active_video_chat(chat_id)
    await remove_active_chat(chat_id)


class Call(PyTgCalls):
    def __init__(self):
        PyTgCallsSession.notice_displayed = True

        self.userbot1 = Client(
            name="SwaggyXAss1",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING1),
        )
        self.one = PyTgCalls(self.userbot1, cache_duration=100)

        self.userbot2 = Client(
            name="SwaggyXAss2",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING2),
        )
        self.two = PyTgCalls(self.userbot2, cache_duration=100)

        self.userbot3 = Client(
            name="SwaggyXAss3",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING3),
        )
        self.three = PyTgCalls(self.userbot3, cache_duration=100)

        self.userbot4 = Client(
            name="SwaggyXAss4",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING4),
        )
        self.four = PyTgCalls(self.userbot4, cache_duration=100)

        self.userbot5 = Client(
            name="SwaggyXAss5",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING5),
        )
        self.five = PyTgCalls(self.userbot5, cache_duration=100)

        self._change_stream_locks = {}

    def _build_stream(
        self,
        source: str,
        video: bool,
        ffmpeg: str | None = None,
    ) -> types.MediaStream:
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
        stream: types.MediaStream,
    ):
        await client.play(
            chat_id=chat_id,
            stream=stream,
            config=types.GroupCallConfig(auto_start=False),
        )

    async def pause_stream(self, chat_id: int):
        await delete_old_message(chat_id)
        assistant = await group_assistant(self, chat_id)
        await assistant.pause(chat_id)

    async def resume_stream(self, chat_id: int):
        await delete_old_message(chat_id)
        assistant = await group_assistant(self, chat_id)
        await assistant.resume(chat_id)

    async def stop_stream(self, chat_id: int):
        await delete_old_message(chat_id)
        assistant = await group_assistant(self, chat_id)
        try:
            await _clear_(chat_id)
            await assistant.leave_call(chat_id, close=False)
        except Exception:
            pass

    async def stop_stream_force(self, chat_id: int):
        for string, client in [
            (config.STRING1, self.one),
            (config.STRING2, self.two),
            (config.STRING3, self.three),
            (config.STRING4, self.four),
            (config.STRING5, self.five),
        ]:
            if not string:
                continue
            try:
                await client.leave_call(chat_id, close=False)
            except Exception:
                pass

        try:
            await _clear_(chat_id)
        except Exception:
            pass

    async def speedup_stream(self, chat_id: int, file_path, speed, playing):
        assistant = await group_assistant(self, chat_id)

        if str(speed) != "1.0":
            base = os.path.basename(file_path)
            chatdir = os.path.join(
                os.getcwd(),
                "playback",
                str(speed),
            )

            os.makedirs(chatdir, exist_ok=True)

            out = os.path.join(chatdir, base)

            if not os.path.isfile(out):
                if str(speed) == "0.5":
                    vs = 2.0
                elif str(speed) == "0.75":
                    vs = 1.35
                elif str(speed) == "1.5":
                    vs = 0.68
                elif str(speed) == "2.0":
                    vs = 0.5
                else:
                    vs = 1.0

                proc = await asyncio.create_subprocess_shell(
                    (
                        f'ffmpeg -y -i "{file_path}" '
                        f'-filter:v "setpts={vs}*PTS" '
                        f'-filter:a "atempo={speed}" '
                        f'"{out}"'
                    ),
                    stdin=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                await proc.communicate()
        else:
            out = file_path

        dur = await asyncio.get_event_loop().run_in_executor(
            None,
            check_duration,
            out,
        )

        dur = int(dur)
        played, con_seconds = speed_converter(
            playing[0]["played"],
            speed,
        )

        duration = seconds_to_min(dur)
        ffmpeg = f"-ss {played} -to {duration}"

        video_mode = playing[0]["streamtype"] == "video"

        stream = self._build_stream(
            out,
            video=video_mode,
            ffmpeg=ffmpeg,
        )

        if str(db[chat_id][0]["file"]) != str(file_path):
            raise AssistantErr("Umm")

        await self._play_on_assistant(
            assistant,
            chat_id,
            stream,
        )

        if str(db[chat_id][0]["file"]) == str(file_path):
            exis = playing[0].get("old_dur")

            if not exis:
                db[chat_id][0]["old_dur"] = db[chat_id][0]["dur"]
                db[chat_id][0]["old_second"] = db[chat_id][0]["seconds"]

            db[chat_id][0]["played"] = con_seconds
            db[chat_id][0]["dur"] = duration
            db[chat_id][0]["seconds"] = dur
            db[chat_id][0]["speed_path"] = out
            db[chat_id][0]["speed"] = speed

    async def force_stop_stream(self, chat_id: int):
        await delete_old_message(chat_id)
        assistant = await group_assistant(self, chat_id)

        try:
            check = db.get(chat_id)
            if check:
                check.pop(0)
        except Exception:
            pass

        await remove_active_video_chat(chat_id)
        await remove_active_chat(chat_id)

        try:
            await assistant.leave_call(chat_id, close=False)
        except Exception:
            pass

    async def skip_stream(
        self,
        chat_id: int,
        link: str,
        video: Union[bool, str] = None,
        image: Union[bool, str] = None,
    ):
        assistant = await group_assistant(self, chat_id)

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
        assistant = await group_assistant(self, chat_id)

        ffmpeg = f"-ss {to_seek} -to {duration}"

        stream = self._build_stream(
            file_path,
            video=(mode == "video"),
            ffmpeg=ffmpeg,
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
        assistant = await group_assistant(self, chat_id)

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

        if await is_autoend():
            counter[chat_id] = {}

            users = len(
                await assistant.get_participants(chat_id)
            )

            if users == 1:
                autoend[chat_id] = (
                    datetime.now()
                    + timedelta(minutes=1)
                )

    async def autoplay_start(
        self,
        chat_id: int,
        original_chat_id: int,
        seed_title: str,
        seed_vidid: str = None,
        client: PyTgCalls = None,
    ) -> bool:
        if seed_vidid:
            remember_played(chat_id, seed_vidid)

        status_msg = None

        try:
            status_msg = await app.send_message(
                original_chat_id,
                "ʜσʟᴅ ση...\n\n"
                "ᴅσᴡηʟσᴧᴅɪηɢ ηєxᴛ ϻєᴅɪᴧ "
                "ғʀσϻ ᴛʜє ǫυєυє.",
            )
        except Exception:
            pass

        async def fail():
            if status_msg:
                try:
                    await status_msg.delete()
                except Exception:
                    pass
            return False

        try:
            candidates = await fetch_autoplay_track(
                chat_id,
                seed_title,
                seed_vidid,
            )
        except Exception as e:
            LOGGER(__name__).warning(
                f"[AUTOPLAY] Candidate fetch failed: {e}"
            )
            candidates = []

        if not candidates:
            return await fail()

        language = await get_lang(chat_id)
        _ = get_string(language)

        for track in candidates:
            vidid = track.get("vidid")

            if not vidid:
                continue

            try:
                file_path, direct = await YouTube.download(
                    vidid,
                    None,
                    videoid=True,
                )
            except Exception:
                continue

            if not file_path:
                continue

            try:
                title = track["title"].title()
                duration_min = track["duration_min"]

                remember_played(chat_id, vidid)

                await put_queue(
                    chat_id,
                    original_chat_id,
                    file_path if direct else f"vid_{vidid}",
                    title,
                    duration_min,
                    "🔁 𝐀ᴜᴛᴏᴘʟᴀʏ",
                    vidid,
                    1,
                    "audio",
                    forceplay=True,
                )

                if db.get(chat_id):
                    db[chat_id][0]["played"] = 0
                    db[chat_id][0]["seconds"] = 0
                    db[chat_id][0]["speed"] = 1.0
                    db[chat_id][0]["speed_path"] = None
                    db[chat_id][0]["old_dur"] = None
                    db[chat_id][0]["old_second"] = 0

                assistant = (
                    client
                    or await group_assistant(
                        self,
                        chat_id,
                    )
                )

                stream = self._build_stream(
                    file_path,
                    video=False,
                )

                await self._play_on_assistant(
                    assistant,
                    chat_id,
                    stream,
                )

            except exceptions.NoActiveGroupCall:
                try:
                    db[chat_id].pop(0)
                except Exception:
                    pass
                return await fail()

            except Exception as e:
                LOGGER(__name__).warning(
                    f"[AUTOPLAY] Track failed {vidid}: {e}"
                )

                try:
                    db[chat_id].pop(0)
                except Exception:
                    pass

                continue

            try:
                thumb_on_now = await is_thumb_on(chat_id)

                button = stream_markup(
                    _,
                    chat_id,
                    autoplay_status=await is_autoplay_on(chat_id),
                    thumb_status=thumb_on_now,
                )

                caption = _["stream_1"].format(
                    f"https://t.me/{app.username}"
                    f"?start=info_{vidid}",
                    title[:23],
                    duration_min,
                    "𝐀ᴜᴛᴏᴘʟᴀʏ 🚩",
                )

                if thumb_on_now:
                    img = await get_thumb(
                        vidid,
                        title=title,
                        duration=duration_min,
                    )

                    run = await app.send_photo(
                        original_chat_id,
                        photo=img,
                        has_spoiler=True,
                        caption=caption,
                        reply_markup=InlineKeyboardMarkup(
                            button
                        ),
                    )
                else:
                    run = await app.send_message(
                        original_chat_id,
                        text=caption,
                        disable_web_page_preview=True,
                        reply_markup=InlineKeyboardMarkup(
                            button
                        ),
                    )

                db[chat_id][0]["mystic"] = run
                db[chat_id][0]["markup"] = "stream"

            except Exception:
                pass

            if status_msg:
                try:
                    await status_msg.delete()
                except Exception:
                    pass

            try:
                await add_active_chat(chat_id)
                await music_on(chat_id)
            except Exception:
                pass

            return True

        return await fail()

    async def _try_autoplay_with_retry(
        self,
        chat_id: int,
        popped: dict | None,
        client: PyTgCalls,
        max_retries: int = 2,
    ) -> bool:
        if not popped:
            return False

        if not await is_autoplay_on(chat_id):
            return False

        for attempt in range(max_retries + 1):
            try:
                started = await self.autoplay_start(
                    chat_id,
                    popped.get("chat_id", chat_id),
                    popped.get("title"),
                    popped.get("vidid"),
                    client=client,
                )

                if started:
                    return True

            except Exception as e:
                LOGGER(__name__).warning(
                    f"[AUTOPLAY] Retry {attempt + 1} failed: {e}"
                )

            if attempt < max_retries:
                await asyncio.sleep(5)

        return False

    async def _handle_queue_ended(
        self,
        chat_id: int,
        client: PyTgCalls,
    ):
        await _clear_(chat_id)

        try:
            buttons = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "✙ ʌᴅᴅ ϻє вᴧʙʏ ✙",
                            url=(
                                f"https://t.me/{app.username}"
                                "?startgroup=true"
                            ),
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "⋞ ᴄʟᴏsє ⋟",
                            callback_data="close_message",
                        )
                    ],
                ]
            )

            await app.send_message(
                chat_id,
                "🎵 𝐓ʜᴇ 𝐌ᴜsɪᴄ 𝐐ᴜᴇᴜᴇ "
                "𝐇𝴀s 𝐄ɴᴅᴇ𝐝.\n"
                "➤ 𝐔𝐬𝐞 /play 𝐓𝐨 𝐀ᴅᴅ "
                "𝐌ᴏʀᴇ 𝐒ᴏɴɢs 🎶",
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
        client: PyTgCalls,
        chat_id: int,
    ):
        await delete_old_message(chat_id)

        lock = self._change_stream_locks.get(chat_id)

        if lock is None:
            lock = asyncio.Lock()
            self._change_stream_locks[chat_id] = lock

        async with lock:
            await self._change_stream_inner(
                client,
                chat_id,
            )

    async def _change_stream_inner(
        self,
        client: PyTgCalls,
        chat_id: int,
    ):
        check = db.get(chat_id)

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
                await auto_clean(popped)
            else:
                loop -= 1
                await set_loop(chat_id, loop)

        except Exception as e:
            LOGGER(__name__).warning(
                f"[STREAM] Queue error: {e}"
            )

        if not check:
            if await self._try_autoplay_with_retry(
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
        title = current.get("title", "Unknown").title()
        user = current.get("by", "Unknown")
        original_chat_id = current.get(
            "chat_id",
            chat_id,
        )
        streamtype = current.get(
            "streamtype",
            "audio",
        )
        videoid = current.get("vidid")

        current["played"] = 0

        if current.get("old_dur"):
            current["dur"] = current["old_dur"]
            current["seconds"] = current.get(
                "old_second",
                0,
            )
            current["speed_path"] = None
            current["speed"] = 1.0

        video = str(streamtype) == "video"

        language = await get_lang(chat_id)
        _ = get_string(language)

        # ==================================================
        # YOUTUBE LIVE STREAM FIX
        # ==================================================
        if queued and "live_" in str(queued):

            try:
                link, success = await YouTube.stream(
                    videoid,
                    videoid=True,
                    video=video,
                )
            except Exception as e:
                LOGGER(__name__).error(
                    f"[LIVE] Extraction failed for "
                    f"{videoid}: {type(e).__name__}: {e}"
                )
                link = None
                success = False

            if not success or not link:
                return await app.send_message(
                    original_chat_id,
                    "❖ ғᴧɪʟєᴅ ᴛσ sᴛʀєᴧϻ "
                    "ʏσυᴛυʙє ʟɪᴠє sᴛʀєᴧϻ, "
                    "ησ ʟɪᴠє ꜰσʀϻᴧᴧᴛ "
                    "ꜰσυηᴅ.",
                )

            try:
                stream = self._build_stream(
                    link,
                    video=video,
                )

                await self._play_on_assistant(
                    client,
                    chat_id,
                    stream,
                )

            except Exception as e:
                LOGGER(__name__).error(
                    f"[LIVE] Playback failed: "
                    f"{type(e).__name__}: {e}"
                )

                return await app.send_message(
                    original_chat_id,
                    text=_["call_6"],
                )

            await self._send_stream_message(
                chat_id=chat_id,
                original_chat_id=original_chat_id,
                current=current,
                videoid=videoid,
                title=title,
                user=user,
                language=_,
            )

            return

        # ==================================================
        # YOUTUBE VIDEO / AUDIO
        # ==================================================
        if queued and "vid_" in str(queued):

            mystic = await app.send_message(
                original_chat_id,
                _["call_7"],
            )

            try:
                file_path, direct = await YouTube.download(
                    videoid,
                    mystic,
                    videoid=True,
                    video=video,
                )

                if not file_path:
                    raise RuntimeError(
                        "No file returned"
                    )

                stream = self._build_stream(
                    file_path,
                    video=video,
                )

                await self._play_on_assistant(
                    client,
                    chat_id,
                    stream,
                )

            except Exception as e:
                LOGGER(__name__).warning(
                    f"[STREAM] YouTube failed: {e}"
                )

                try:
                    await mystic.delete()
                except Exception:
                    pass

                if (
                    popped
                    and await is_autoplay_on(chat_id)
                ):
                    if await self._try_autoplay_with_retry(
                        chat_id,
                        popped,
                        client,
                    ):
                        return

                return await self._handle_queue_ended(
                    chat_id,
                    client,
                )

            try:
                await mystic.delete()
            except Exception:
                pass

            await self._send_stream_message(
                chat_id=chat_id,
                original_chat_id=original_chat_id,
                current=current,
                videoid=videoid,
                title=title,
                user=user,
                language=_,
            )

            return

        # ==================================================
        # DIRECT STREAM
        # ==================================================
        if queued and "index_" in str(queued):
            source = videoid
        else:
            source = queued

        try:
            stream = self._build_stream(
                source,
                video=video,
            )

            await self._play_on_assistant(
                client,
                chat_id,
                stream,
            )

        except Exception as e:
            LOGGER(__name__).warning(
                f"[STREAM] Direct stream failed: {e}"
            )

            return await app.send_message(
                original_chat_id,
                text=_["call_6"],
            )

        if videoid == "telegram":
            image = (
                config.TELEGRAM_AUDIO_URL
                if streamtype == "audio"
                else config.TELEGRAM_VIDEO_URL
            )
            link = config.SUPPORT_CHAT

        elif videoid == "soundcloud":
            image = config.SOUNCLOUD_IMG_URL
            link = config.SUPPORT_CHAT

        elif queued and "index_" in str(queued):
            image = config.STREAM_IMG_URL
            link = config.SUPPORT_CHAT

        else:
            image = None
            link = (
                f"https://t.me/{app.username}"
                f"?start=info_{videoid}"
            )

        thumb_on_now = await is_thumb_on(chat_id)

        button = stream_markup(
            _,
            chat_id,
            autoplay_status=await is_autoplay_on(chat_id),
            thumb_status=thumb_on_now,
        )

        if queued and "index_" in str(queued):
            caption = _["stream_2"].format(user)
        else:
            caption = _["stream_1"].format(
                link,
                title[:23],
                current.get("dur", "LIVE"),
                user,
            )

        try:
            if thumb_on_now:

                if image:
                    photo = image
                else:
                    photo = await get_thumb(
                        videoid,
                        title=title,
                        duration=current.get("dur", "LIVE"),
                    )

                run = await app.send_photo(
                    original_chat_id,
                    photo=photo,
                    caption=caption,
                    has_spoiler=not bool(image),
                    reply_markup=InlineKeyboardMarkup(
                        button
                    ),
                )

            else:
                run = await app.send_message(
                    original_chat_id,
                    text=caption,
                    disable_web_page_preview=True,
                    reply_markup=InlineKeyboardMarkup(
                        button
                    ),
                )

            current["mystic"] = run

            current["markup"] = (
                "tg"
                if videoid in (
                    "telegram",
                    "soundcloud",
                )
                else "stream"
            )

        except Exception as e:
            LOGGER(__name__).warning(
                f"[STREAM] Message error: {e}"
            )

    async def _send_stream_message(
        self,
        chat_id,
        original_chat_id,
        current,
        videoid,
        title,
        user,
        language,
    ):
        thumb_on_now = await is_thumb_on(chat_id)

        button = stream_markup(
            language,
            chat_id,
            autoplay_status=await is_autoplay_on(chat_id),
            thumb_status=thumb_on_now,
        )

        caption = language["stream_1"].format(
            f"https://t.me/{app.username}"
            f"?start=info_{videoid}",
            title[:23],
            current.get("dur", "LIVE"),
            user,
        )

        try:
            if thumb_on_now:

                img = await get_thumb(
                    videoid,
                    title=title,
                    duration=current.get("dur", "LIVE"),
                )

                run = await app.send_photo(
                    original_chat_id,
                    photo=img,
                    has_spoiler=True,
                    caption=caption,
                    reply_markup=InlineKeyboardMarkup(
                        button
                    ),
                )

            else:
                run = await app.send_message(
                    original_chat_id,
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
                f"[STREAM] UI message failed: {e}"
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
                    pings.append(client.ping)
                except Exception:
                    pass

        return (
            str(round(sum(pings) / len(pings), 3))
            if pings
            else "0"
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
        for string, client in [
            (config.STRING1, self.one),
            (config.STRING2, self.two),
            (config.STRING3, self.three),
            (config.STRING4, self.four),
            (config.STRING5, self.five),
        ]:
            if not string:
                continue

            @client.on_update()
            async def _update_handler(
                _,
                update: types.Update,
                _client=client,
            ):
                if isinstance(update, types.StreamEnded):

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
                                "[STREAM] change_stream error "
                                f"for {update.chat_id}: "
                                f"{type(e).__name__}: {e}"
                            )

                elif isinstance(update, types.ChatUpdate):

                    if update.status in [
                        types.ChatUpdate.Status.KICKED,
                        types.ChatUpdate.Status.LEFT_GROUP,
                        types.ChatUpdate.Status.CLOSED_VOICE_CHAT,
                    ]:
                        await self.stop_stream(
                            update.chat_id
                        )


Swaggy = Call()
