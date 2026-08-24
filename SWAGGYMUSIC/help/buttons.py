from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram import Client, filters, enums
from pyrogram.enums import ButtonStyle

import config
from SWAGGYMUSIC import app


class BUTTONS(object):

    BBUTTON = [
        [
            InlineKeyboardButton("ᴄʜᴧᴛ-ɢᴘᴛ", callback_data="TOOL_BACK HELP_01", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton("ᴧᴄᴛɪση", callback_data="TOOL_BACK HELP_14", style=ButtonStyle.SUCCESS),
            InlineKeyboardButton("ᴄσᴜᴘʟєs", callback_data="TOOL_BACK HELP_08", style=ButtonStyle.PRIMARY),
        ],
        [
            InlineKeyboardButton("sєᴧʀᴄʜ", callback_data="TOOL_BACK HELP_02", style=ButtonStyle.SUCCESS),
            InlineKeyboardButton("ᴛʀᴧηsʟᴧᴛє", callback_data="TOOL_BACK HELP_24", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton("ɪηғσ", callback_data="TOOL_BACK HELP_04", style=ButtonStyle.PRIMARY),
        ],
        [
            InlineKeyboardButton("ғσηᴛ", callback_data="TOOL_BACK HELP_05", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton("ᴡʜɪsᴘєʀ", callback_data="TOOL_BACK HELP_03", style=ButtonStyle.SUCCESS),
            InlineKeyboardButton("ᴛᴧɢᴧʟʟ", callback_data="TOOL_BACK HELP_07", style=ButtonStyle.PRIMARY),
        ],
        [
            InlineKeyboardButton("ғυη", callback_data="TOOL_BACK HELP_11", style=ButtonStyle.SUCCESS),
            InlineKeyboardButton("ǫυσᴛʟʏ", callback_data="TOOL_BACK HELP_12", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton("Ⓣ-ɢʀᴧᴘʜ", callback_data="TOOL_BACK HELP_26", style=ButtonStyle.PRIMARY),
        ],
        [
            InlineKeyboardButton("ɢᴧϻє", callback_data="TOOL_BACK HELP_21", style=ButtonStyle.SUCCESS),
            InlineKeyboardButton("sєᴛᴜᴘ", callback_data="TOOL_BACK HELP_17", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton("sᴧηɢϻᴧᴛᴧ", callback_data="TOOL_BACK HELP_23", style=ButtonStyle.PRIMARY),
        ],
        [
            InlineKeyboardButton("ɢɪᴛʜᴜʙ", callback_data="TOOL_BACK HELP_25", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton("⌯ ʙᴧᴄᴋ ⌯", callback_data="MAIN_CP", style=ButtonStyle.DANGER),
            InlineKeyboardButton("sᴛɪᴄᴋєʀs", callback_data="TOOL_BACK HELP_10", style=ButtonStyle.SUCCESS),
        ]
    ]

    ALPHABUTTON = [
        [
            InlineKeyboardButton("ᴧɪ | ᴄʜᴧᴛɢᴘᴛ", callback_data="TOOL_BACK HELP_01", style=ButtonStyle.PRIMARY),
        ],
        [
            InlineKeyboardButton("sєᴧʀᴄʜ", callback_data="TOOL_BACK HELP_02", style=ButtonStyle.SUCCESS),
            InlineKeyboardButton("ᴛᴛs", callback_data="TOOL_BACK HELP_03", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton("ɪηғσ", callback_data="TOOL_BACK HELP_04", style=ButtonStyle.PRIMARY),
        ],
        [
            InlineKeyboardButton("ғσηᴛ", callback_data="TOOL_BACK HELP_05", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton("ϻᴧᴛʜ", callback_data="TOOL_BACK HELP_06", style=ButtonStyle.SUCCESS),
            InlineKeyboardButton("ᴛᴧɢᴧʟʟ", callback_data="TOOL_BACK HELP_07", style=ButtonStyle.PRIMARY),
        ],
        [
            InlineKeyboardButton("ɪϻᴧɢє", callback_data="TOOL_BACK HELP_08", style=ButtonStyle.SUCCESS),
            InlineKeyboardButton("ʜᴧsᴛᴧɢ", callback_data="TOOL_BACK HELP_09", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton("sᴛɪᴄᴋєʀs", callback_data="TOOL_BACK HELP_10", style=ButtonStyle.PRIMARY),
        ],
        [
            InlineKeyboardButton("ғυη", callback_data="TOOL_BACK HELP_11", style=ButtonStyle.SUCCESS),
            InlineKeyboardButton("ǫυσᴛʟʏ", callback_data="TOOL_BACK HELP_12", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton("ᴛ-ᴅ", callback_data="TOOL_BACK HELP_13", style=ButtonStyle.PRIMARY),
        ],
        [
            InlineKeyboardButton("⌯ ʙᴧᴄᴋ ⌯", callback_data="MAIN_CP", style=ButtonStyle.DANGER),
        ]
    ]

    MBUTTON = [
        [
            InlineKeyboardButton("⌯ ʙᴧᴄᴋ ⌯", callback_data="MAIN_CP", style=ButtonStyle.DANGER),
        ]
    ]

    PBUTTON = [
        [
            InlineKeyboardButton("ㅤ- 𝚁𝙾𝚈𝙰𝙻 ", url="https://t.me/II_ROYALENTRY1128_II", style=ButtonStyle.PRIMARY)
        ],
        [
            InlineKeyboardButton("⌯ ʙᴧᴄᴋ ⌯", callback_data="MAIN_CP", style=ButtonStyle.DANGER),
        ]
    ]

    ABUTTON = [
        [
            InlineKeyboardButton("⌯ sυᴘᴘσʀᴛ ⌯", url="https://t.me/ll_ROYAL_ABOUT_ll", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton("⌯ υᴘᴅᴧᴛєs ⌯", url="https://t.me/hot_dpz_stor", style=ButtonStyle.SUCCESS),
        ],
        [
            InlineKeyboardButton("⌯ ʙᴧᴄᴋ ⌯", callback_data="settingsback_helper", style=ButtonStyle.DANGER),
        ]
    ]

    SBUTTON = [
        [
            InlineKeyboardButton("⌯ ϻᴜѕɪᴄ ⌯", callback_data="settings_back_helper", style=ButtonStyle.PRIMARY),
        ],
        [
            InlineKeyboardButton("ᴧʟʟ ʙσᴛ's", callback_data="MAIN_BACK HELP_ABOUT", style=ButtonStyle.SUCCESS),
            InlineKeyboardButton("⌯ ᴘʀσϻσᴛɪση ⌯", callback_data="PROMOTION_CP", style=ButtonStyle.PRIMARY),
        ],
        [
            InlineKeyboardButton("⌯ ʙᴧᴄᴋ ᴛσ ʜσϻє ⌯", callback_data="settingsback_helper", style=ButtonStyle.DANGER),
        ]
    ]
