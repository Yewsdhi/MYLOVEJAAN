import math
import random

from pyrogram.types import InlineKeyboardButton
from pyrogram.enums import ButtonStyle

from SWAGGYMUSIC.utils.formatters import time_to_seconds


# Random styles for play/search buttons
styles = [
    ButtonStyle.PRIMARY,
    ButtonStyle.SUCCESS,
    ButtonStyle.DANGER,
]


def track_markup(_, videoid, user_id, channel, fplay):
    return [
        [
            InlineKeyboardButton(
                text=_["P_B_1"],
                callback_data=f"MusicStream {videoid}|{user_id}|a|{channel}|{fplay}",
                style=random.choice(styles),
            ),
            InlineKeyboardButton(
                text=_["P_B_2"],
                callback_data=f"MusicStream {videoid}|{user_id}|v|{channel}|{fplay}",
                style=random.choice(styles),
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {videoid}|{user_id}",
                style=ButtonStyle.DANGER,
            )
        ],
    ]


def _toggle_buttons(chat_id, autoplay_status=None, thumb_status=None):
    if autoplay_status is True:
        ap_text = "🔄 ᴀᴜᴛᴏᴘʟᴀʏ: ON ✅"
        style = ButtonStyle.SUCCESS
    elif autoplay_status is False:
        ap_text = "🔄 ᴀᴜᴛᴏᴘʟᴀʏ: OFF ❌"
        style = ButtonStyle.DANGER
    else:
        ap_text = "🔄 ᴀᴜᴛᴏᴘʟᴀʏ"
        style = ButtonStyle.PRIMARY

    return [
        InlineKeyboardButton(
            text=ap_text,
            callback_data=f"ADMIN AutoPlay|{chat_id}",
            style=style,
        )
    ]


def stream_markup_timer(
    _,
    chat_id,
    played,
    dur,
    autoplay_status=None,
    thumb_status=None,
):
    try:
        played_sec = time_to_seconds(played)
        duration_sec = time_to_seconds(dur)

        percentage = (
            (played_sec / duration_sec) * 100
            if duration_sec and duration_sec > 0
            else 0
        )
    except Exception:
        percentage = 0

    umm = min(max(math.floor(percentage), 0), 100)

    if umm <= 10:
        bar = "▰▱▱▱▱▱▱▱▱▱"
    elif umm < 20:
        bar = "▰▰▱▱▱▱▱▱▱▱"
    elif umm < 30:
        bar = "▰▰▰▱▱▱▱▱▱▱"
    elif umm < 40:
        bar = "▰▰▰▰▱▱▱▱▱▱"
    elif umm < 50:
        bar = "▰▰▰▰▰▱▱▱▱▱"
    elif umm < 60:
        bar = "▰▰▰▰▰▰▱▱▱▱"
    elif umm < 70:
        bar = "▰▰▰▰▰▰▰▱▱▱"
    elif umm < 80:
        bar = "▰▰▰▰▰▰▰▰▱▱"
    elif umm < 95:
        bar = "▰▰▰▰▰▰▰▰▰▱"
    else:
        bar = "▰▰▰▰▰▰▰▰▰▰"

    return [
        [
            InlineKeyboardButton(
                text=f"{played} {bar} {dur}",
                callback_data="GetTimer",
                style=ButtonStyle.PRIMARY,
            )
        ],
        [
            InlineKeyboardButton(
                text="▷",
                callback_data=f"ADMIN Resume|{chat_id}",
                style=ButtonStyle.SUCCESS,
            ),
            InlineKeyboardButton(
                text="II",
                callback_data=f"ADMIN Pause|{chat_id}",
                style=ButtonStyle.PRIMARY,
            ),
            InlineKeyboardButton(
                text="↻",
                callback_data=f"ADMIN Replay|{chat_id}",
                style=ButtonStyle.PRIMARY,
            ),
            InlineKeyboardButton(
                text="‣‣I",
                callback_data=f"ADMIN Skip|{chat_id}",
                style=ButtonStyle.SUCCESS,
            ),
            InlineKeyboardButton(
                text="▢",
                callback_data=f"ADMIN Stop|{chat_id}",
                style=ButtonStyle.DANGER,
            ),
        ],
        _toggle_buttons(chat_id, autoplay_status, thumb_status),
        [
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data="close",
                style=ButtonStyle.DANGER,
            )
        ],
    ]


def stream_markup(_, chat_id, autoplay_status=None, thumb_status=None):
    return [
        [
            InlineKeyboardButton(
                text="▷",
                callback_data=f"ADMIN Resume|{chat_id}",
                style=ButtonStyle.SUCCESS,
            ),
            InlineKeyboardButton(
                text="II",
                callback_data=f"ADMIN Pause|{chat_id}",
                style=ButtonStyle.PRIMARY,
            ),
            InlineKeyboardButton(
                text="↻",
                callback_data=f"ADMIN Replay|{chat_id}",
                style=ButtonStyle.PRIMARY,
            ),
            InlineKeyboardButton(
                text="‣‣I",
                callback_data=f"ADMIN Skip|{chat_id}",
                style=ButtonStyle.SUCCESS,
            ),
            InlineKeyboardButton(
                text="▢",
                callback_data=f"ADMIN Stop|{chat_id}",
                style=ButtonStyle.DANGER,
            ),
        ],
        _toggle_buttons(chat_id, autoplay_status, thumb_status),
        [
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data="close",
                style=ButtonStyle.DANGER,
            )
        ],
    ]


def playlist_markup(_, videoid, user_id, ptype, channel, fplay):
    return [
        [
            InlineKeyboardButton(
                text=_["P_B_1"],
                callback_data=(
                    f"SwaggyPlaylists "
                    f"{videoid}|{user_id}|{ptype}|a|{channel}|{fplay}"
                ),
                style=random.choice(styles),
            ),
            InlineKeyboardButton(
                text=_["P_B_2"],
                callback_data=(
                    f"SwaggyPlaylists "
                    f"{videoid}|{user_id}|{ptype}|v|{channel}|{fplay}"
                ),
                style=random.choice(styles),
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {videoid}|{user_id}",
                style=ButtonStyle.DANGER,
            ),
        ],
    ]


def livestream_markup(_, videoid, user_id, mode, channel, fplay):
    return [
        [
            InlineKeyboardButton(
                text=_["P_B_3"],
                callback_data=(
                    f"LiveStream "
                    f"{videoid}|{user_id}|{mode}|{channel}|{fplay}"
                ),
                style=ButtonStyle.SUCCESS,
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {videoid}|{user_id}",
                style=ButtonStyle.DANGER,
            ),
        ],
    ]


def slider_markup(_, videoid, user_id, query, query_type, channel, fplay):
    query = str(query)[:20]

    return [
        [
            InlineKeyboardButton(
                text=_["P_B_1"],
                callback_data=f"MusicStream {videoid}|{user_id}|a|{channel}|{fplay}",
                style=random.choice(styles),
            ),
            InlineKeyboardButton(
                text=_["P_B_2"],
                callback_data=f"MusicStream {videoid}|{user_id}|v|{channel}|{fplay}",
                style=random.choice(styles),
            ),
        ],
        [
            InlineKeyboardButton(
                text="◁",
                callback_data=(
                    f"slider B|{query_type}|{query}|"
                    f"{user_id}|{channel}|{fplay}"
                ),
                style=ButtonStyle.PRIMARY,
            ),
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {query}|{user_id}",
                style=ButtonStyle.DANGER,
            ),
            InlineKeyboardButton(
                text="▷",
                callback_data=(
                    f"slider F|{query_type}|{query}|"
                    f"{user_id}|{channel}|{fplay}"
                ),
                style=ButtonStyle.PRIMARY,
            ),
        ],
                ]
