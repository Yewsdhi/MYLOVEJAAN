import math

from pyrogram.types import InlineKeyboardButton

from SWAGGYMUSIC.utils.formatters import time_to_seconds


def track_markup(_, videoid, user_id, channel, fplay):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["P_B_1"],
                callback_data=f"MusicStream {videoid}|{user_id}|a|{channel}|{fplay}",
            ),
            InlineKeyboardButton(
                text=_["P_B_2"],
                callback_data=f"MusicStream {videoid}|{user_id}|v|{channel}|{fplay}",
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {videoid}|{user_id}",
            )
        ],
    ]
    return buttons


def _toggle_buttons(chat_id, autoplay_status=None, thumb_status=None):
    """
    Build the AutoPlay toggle button.
    thumb_status is kept only for backward compatibility,
    so existing function calls will not raise TypeError.
    """

    if autoplay_status is True:
        ap_text = "ᴀᴜᴛᴏᴘʟᴀʏ: ʏᴇs"
    elif autoplay_status is False:
        ap_text = "ᴀᴜᴛᴏᴘʟᴀʏ: ɴᴏ"
    else:
        ap_text = "ᴀᴜᴛᴏᴘʟᴀʏ"

    return [
        InlineKeyboardButton(
            text=ap_text,
            callback_data=f"ADMIN AutoPlay|{chat_id}",
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
    played_sec = time_to_seconds(played)
    duration_sec = time_to_seconds(dur)

    if duration_sec and duration_sec > 0:
        percentage = (played_sec / duration_sec) * 100
    else:
        percentage = 0

    umm = math.floor(percentage)

    if 0 < umm <= 10:
        bar = "▰▱▱▱▱▱▱▱▱▱"
    elif 10 < umm < 20:
        bar = "▰▰▱▱▱▱▱▱▱▱"
    elif 20 <= umm < 30:
        bar = "▰▰▰▱▱▱▱▱▱▱"
    elif 30 <= umm < 40:
        bar = "▰▰▰▰▱▱▱▱▱▱"
    elif 40 <= umm < 50:
        bar = "▰▰▰▰▰▱▱▱▱▱"
    elif 50 <= umm < 60:
        bar = "▰▰▰▰▰▰▱▱▱▱"
    elif 60 <= umm < 70:
        bar = "▰▰▰▰▰▰▰▱▱▱"
    elif 70 <= umm < 80:
        bar = "▰▰▰▰▰▰▰▰▱▱"
    elif 80 <= umm < 95:
        bar = "▰▰▰▰▰▰▰▰▰▱"
    elif 95 <= umm <= 100:
        bar = "▰▰▰▰▰▰▰▰▰▰"
    else:
        bar = "▰▱▱▱▱▱▱▱▱▱"

    buttons = [
        [
            InlineKeyboardButton(
                text=f"{played} {bar} {dur}",
                callback_data="GetTimer",
            )
        ],
        [
            InlineKeyboardButton(
                text="▷",
                callback_data=f"ADMIN Resume|{chat_id}",
            ),
            InlineKeyboardButton(
                text="II",
                callback_data=f"ADMIN Pause|{chat_id}",
            ),
            InlineKeyboardButton(
                text="↻",
                callback_data=f"ADMIN Replay|{chat_id}",
            ),
            InlineKeyboardButton(
                text="‣‣I",
                callback_data=f"ADMIN Skip|{chat_id}",
            ),
            InlineKeyboardButton(
                text="▢",
                callback_data=f"ADMIN Stop|{chat_id}",
            ),
        ],
        _toggle_buttons(chat_id, autoplay_status, thumb_status),
        [
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data="close",
            )
        ],
    ]

    return buttons


def stream_markup(_, chat_id, autoplay_status=None, thumb_status=None):
    buttons = [
        [
            InlineKeyboardButton(
                text="▷",
                callback_data=f"ADMIN Resume|{chat_id}",
            ),
            InlineKeyboardButton(
                text="II",
                callback_data=f"ADMIN Pause|{chat_id}",
            ),
            InlineKeyboardButton(
                text="↻",
                callback_data=f"ADMIN Replay|{chat_id}",
            ),
            InlineKeyboardButton(
                text="‣‣I",
                callback_data=f"ADMIN Skip|{chat_id}",
            ),
            InlineKeyboardButton(
                text="▢",
                callback_data=f"ADMIN Stop|{chat_id}",
            ),
        ],
        _toggle_buttons(chat_id, autoplay_status, thumb_status),
        [
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data="close",
            )
        ],
    ]

    return buttons


def playlist_markup(_, videoid, user_id, ptype, channel, fplay):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["P_B_1"],
                callback_data=(
                    f"SwaggyPlaylists "
                    f"{videoid}|{user_id}|{ptype}|a|{channel}|{fplay}"
                ),
            ),
            InlineKeyboardButton(
                text=_["P_B_2"],
                callback_data=(
                    f"SwaggyPlaylists "
                    f"{videoid}|{user_id}|{ptype}|v|{channel}|{fplay}"
                ),
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {videoid}|{user_id}",
            ),
        ],
    ]

    return buttons


def livestream_markup(_, videoid, user_id, mode, channel, fplay):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["P_B_3"],
                callback_data=(
                    f"LiveStream "
                    f"{videoid}|{user_id}|{mode}|{channel}|{fplay}"
                ),
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {videoid}|{user_id}",
            ),
        ],
    ]

    return buttons


def slider_markup(_, videoid, user_id, query, query_type, channel, fplay):
    query = str(query)[:20]

    buttons = [
        [
            InlineKeyboardButton(
                text=_["P_B_1"],
                callback_data=f"MusicStream {videoid}|{user_id}|a|{channel}|{fplay}",
            ),
            InlineKeyboardButton(
                text=_["P_B_2"],
                callback_data=f"MusicStream {videoid}|{user_id}|v|{channel}|{fplay}",
            ),
        ],
        [
            InlineKeyboardButton(
                text="◁",
                callback_data=(
                    f"slider B|{query_type}|{query}|"
                    f"{user_id}|{channel}|{fplay}"
                ),
            ),
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {query}|{user_id}",
            ),
            InlineKeyboardButton(
                text="▷",
                callback_data=(
                    f"slider F|{query_type}|{query}|"
                    f"{user_id}|{channel}|{fplay}"
                ),
            ),
        ],
    ]

    return buttons
