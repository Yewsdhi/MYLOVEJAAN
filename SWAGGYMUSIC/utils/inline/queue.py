from typing import Union

from pyrogram.enums import ButtonStyle
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from SWAGGYMUSIC import app
from SWAGGYMUSIC.utils.formatters import time_to_seconds


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
                style=ButtonStyle.PRIMARY,
            ),
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data="close",
                style=ButtonStyle.DANGER,
            ),
        ]
    ]

    dur_buttons = [
        [
            InlineKeyboardButton(
                text=_["QU_B_2"].format(played, dur),
                callback_data="GetTimer",
                style=ButtonStyle.SUCCESS,
            )
        ],
        [
            InlineKeyboardButton(
                text=_["QU_B_1"],
                callback_data=f"GetQueued {CPLAY}|{videoid}",
                style=ButtonStyle.PRIMARY,
            ),
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data="close",
                style=ButtonStyle.DANGER,
            ),
        ],
    ]

    upl = InlineKeyboardMarkup(
        not_dur if DURATION == "Unknown" else dur_buttons
    )
    return upl


def queue_back_markup(_, CPLAY):

    upl = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text=_["BACK_BUTTON"],
                    callback_data=f"queue_back_timer {CPLAY}",
                    style=ButtonStyle.PRIMARY,
                ),
                InlineKeyboardButton(
                    text=_["CLOSE_BUTTON"],
                    callback_data="close",
                    style=ButtonStyle.DANGER,
                ),
            ]
        ]
    )

    return upl


def aq_markup(_, chat_id):

    buttons = [
        [
            InlineKeyboardButton(
                text="• ᴊσɪη ησω •",
                url="https://t.me/ll_ROYAL_ABOUT_ll",
                style=ButtonStyle.SUCCESS,
            ),
            InlineKeyboardButton(
                text="• ɢʀᴏᴜᴘ ᴄʜᴀᴛ •",
                url="https://t.me/hot_dpz_stor",
                style=ButtonStyle.PRIMARY,
            ),
        ],
    ]

    return buttons
