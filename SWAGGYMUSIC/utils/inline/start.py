from pyrogram.types import InlineKeyboardButton
from pyrogram.enums import ButtonStyle

import config
from SWAGGYMUSIC import app


def start_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_1"],
                url=f"https://t.me/{app.username}?startgroup=true",
                style=ButtonStyle.PRIMARY,
            ),
            InlineKeyboardButton(
                text=_["S_B_2"],
                url=config.SUPPORT_CHAT,
                style=ButtonStyle.SUCCESS,
            ),
        ],
    ]
    return buttons


def private_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_3"],
                url=f"https://t.me/{app.username}?startgroup=true",
                style=ButtonStyle.PRIMARY,
            )
        ],
        [
            InlineKeyboardButton(
                text=_["S_B_4"],
                callback_data="MAIN_CP",
                style=ButtonStyle.SUCCESS,
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["S_B_5"],
                user_id=config.OWNER_ID,
                style=ButtonStyle.DANGER,
            ),
            InlineKeyboardButton(
                text="⌯ ᴧʙσυт ⌯",
                callback_data="ALLBOT_CP",
                style=ButtonStyle.PRIMARY,
            ),
        ],
        [
            InlineKeyboardButton(
                text="⌯ ʏᴛ-ᴀᴘɪ ⌯",
                callback_data="bot_info_data",
                style=ButtonStyle.SUCCESS,
            ),
        ],
    ]
    return buttons
