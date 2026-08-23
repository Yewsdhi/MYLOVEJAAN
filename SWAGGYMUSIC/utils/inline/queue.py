from typing import Union

from SWAGGYMUSIC import app
from SWAGGYMUSIC.utils.formatters import time_to_seconds
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def queue_markup(
    _,
    DURATION,
    CPLAY,
    videoid,
    played: Union[bool, int] = None,
    dur: Union[bool, int] = None,
):
    not_dur = [
        [
            InlineKeyboardButton(
                text=_["QU_B_1"],
                callback_data=f"GetQueued {CPLAY}|{videoid}",
            ),
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data="close",
            ),
        ]
    ]

    duration_buttons = [
        [
            InlineKeyboardButton(
                text=_["QU_B_2"].format(played, dur),
                callback_data="GetTimer",
            )
        ],
        [
            InlineKeyboardButton(
                text=_["QU_B_1"],
                callback_data=f"GetQueued {CPLAY}|{videoid}",
            ),
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data="close",
            ),
        ],
    ]

    return InlineKeyboardMarkup(
        not_dur if DURATION == "Unknown" else duration_buttons
    )


def queue_back_markup(_, CPLAY):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["BACK_BUTTON"],
                callback_data=f"queue_back_timer {CPLAY}",
            ),
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data="close",
            ),
        ]
    ]

    return InlineKeyboardMarkup(buttons)


def aq_markup(_, chat_id):
    buttons = [
        [
            InlineKeyboardButton(
                text="• ᴊσɪη ησω •",
                url="https://t.me/messo_network",
            ),
            InlineKeyboardButton(
                text="• ɢʀᴏᴜᴘ ᴄʜᴀᴛ •",
                url="https://t.me/+Gi7KEHVRUNlhZjg1",
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data="close",
            )
        ],
    ]

    return InlineKeyboardMarkup(buttons)
