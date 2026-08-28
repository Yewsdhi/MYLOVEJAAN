import asyncio
import time

from pyrogram import filters
from pyrogram.enums import ChatMembersFilter
from pyrogram.types import CallbackQuery, Message

from SWAGGYMUSIC import app
from SWAGGYMUSIC.core.call import Swaggy
from SWAGGYMUSIC.misc import db
from SWAGGYMUSIC.utils.database import (
    get_assistant,
    get_authuser_names,
    get_cmode,
)
from SWAGGYMUSIC.utils.decorators import (
    ActualAdminCB,
    AdminActual,
    language,
)
from SWAGGYMUSIC.utils.formatters import (
    alpha_to_int,
    get_readable_time,
)
from config import BANNED_USERS, adminlist, lyrical


rel = {}


@app.on_message(
    filters.command(
        ["admincache", "reload", "refresh"],
        prefixes=["/", "!", "%", ",", ".", "@", "#"],
    )
    & filters.group
    & ~BANNED_USERS
)
@language
async def reload_admin_cache(client, message: Message, _):
    try:
        chat_id = message.chat.id

        if chat_id not in rel:
            rel[chat_id] = 0

        saved = rel[chat_id]

        if saved > time.time():
            left = get_readable_time(int(saved - time.time()))
            return await message.reply_text(
                _["reload_1"].format(left)
            )

        adminlist[chat_id] = []

        async for user in app.get_chat_members(
            chat_id,
            filter=ChatMembersFilter.ADMINISTRATORS,
        ):
            if (
                user.privileges
                and user.privileges.can_manage_video_chats
            ):
                adminlist[chat_id].append(user.user.id)

        authusers = await get_authuser_names(chat_id)

        for user in authusers:
            user_id = await alpha_to_int(user)

            if user_id not in adminlist[chat_id]:
                adminlist[chat_id].append(user_id)

        rel[chat_id] = int(time.time()) + 180

        await message.reply_text(_["reload_2"])

    except Exception:
        await message.reply_text(_["reload_3"])


@app.on_message(
    filters.command(["reboot"])
    & filters.group
    & ~BANNED_USERS
)
@AdminActual
@language
async def restartbot(client, message: Message, _):

    mystic = await message.reply_text(
        _["reload_4"].format(app.mention)
    )

    await asyncio.sleep(1)

    try:
        db[message.chat.id] = []
        await Swaggy.stop_stream_force(message.chat.id)
    except Exception:
        pass

    try:
        userbot = await get_assistant(message.chat.id)

        if message.chat.username:
            await userbot.resolve_peer(message.chat.username)
        else:
            await userbot.resolve_peer(message.chat.id)

    except Exception:
        pass

    chat_id = await get_cmode(message.chat.id)

    if chat_id:
        try:
            got = await app.get_chat(chat_id)
            userbot = await get_assistant(chat_id)

            if got.username:
                await userbot.resolve_peer(got.username)
            else:
                await userbot.resolve_peer(chat_id)

        except Exception:
            pass

        try:
            db[chat_id] = []
            await Swaggy.stop_stream_force(chat_id)

        except Exception:
            pass

    await mystic.edit_text(
        _["reload_5"].format(app.mention)
    )


@app.on_callback_query(
    filters.regex("^close$")
    & ~BANNED_USERS
)
async def close_menu(_, query: CallbackQuery):

    try:
        await query.answer()

        await query.message.delete()

        umm = await query.message.reply_text(
            f"ᴄʟᴏꜱᴇ ʙʏ : {query.from_user.mention}"
        )

        await asyncio.sleep(2)
        await umm.delete()

    except Exception:
        pass


@app.on_callback_query(
    filters.regex("^stop_downloading$")
    & ~BANNED_USERS
)
@ActualAdminCB
async def stop_download(
    client,
    CallbackQuery: CallbackQuery,
    _,
):
    message_id = CallbackQuery.message.id

    task = lyrical.get(message_id)

    if not task:
        return await CallbackQuery.answer(
            _["tg_4"],
            show_alert=True,
        )

    if task.done() or task.cancelled():
        return await CallbackQuery.answer(
            _["tg_5"],
            show_alert=True,
        )

    try:
        task.cancel()
        lyrical.pop(message_id, None)

        await CallbackQuery.answer(
            _["tg_6"],
            show_alert=True,
        )

        return await CallbackQuery.edit_message_text(
            _["tg_7"].format(
                CallbackQuery.from_user.mention
            )
        )

    except Exception:
        return await CallbackQuery.answer(
            _["tg_8"],
            show_alert=True,
)
