from loguru import logger
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from config import WEBSITE_URL, SOURCE_CODE_URL, SUPPORT_GROUP_URL, YOUTUBE_TUTORIAL_URL

def create_keyboard(buttons):
    """Create inline keyboard from list of buttons"""
    logger.debug("🛠 Creating inline keyboard")
    keyboard = []
    for button_row in buttons:
        row = []
        for button in button_row:
            # If button has URL (starts with http), create URL button
            # If button has callback data, create callback button
            if len(button) == 2:
                if button[1].startswith('http'):
                    row.append(InlineKeyboardButton(button[0], url=button[1]))
                else:
                    row.append(InlineKeyboardButton(button[0], callback_data=button[1]))
        keyboard.append(row)
    logger.debug(f"✅ Keyboard created with {len(keyboard)} rows")
    return InlineKeyboardMarkup(keyboard)

def get_home_keyboard():
    """Create home page keyboard"""
    logger.debug("🏠 Creating home page keyboard")
    buttons = [
        [("🌐 ᴠɪꜱɪᴛ ᴡᴇʙꜱɪᴛᴇ", WEBSITE_URL)],  # This should be a URL button, not callback
        [("ℹ️ ᴀʙᴏᴜᴛ ᴍᴇ", "about_me"), ("📖 ʜᴏᴡ ᴛᴏ ᴜꜱᴇ", "how_to_use")],
        [("⌧ Cʟᴏsᴇ ⌧", "close")]
    ]
    return create_keyboard(buttons)

def get_about_keyboard():
    """Create about page keyboard"""
    logger.debug("ℹ️ Creating about page keyboard")
    
    buttons = [
        [("📦 ꜱᴏᴜʀᴄᴇ ᴄᴏᴅᴇ", SOURCE_CODE_URL)],  # URL button
        [("👥 ꜱᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ", SUPPORT_GROUP_URL)],  # URL button
        [("⇦ ɢᴏ ʙᴀᴄᴋ", "go_back_home"), ("⌧ Cʟᴏsᴇ ⌧", "close")]
    ]
    return create_keyboard(buttons)

def get_tutorial_keyboard():
    """Create tutorial page keyboard"""
    logger.debug("📖 Creating tutorial page keyboard")
    
    buttons = [
        [("🎥 ᴄʟɪᴄᴋ ᴛᴏ ᴡᴀᴛᴄʜ ᴠɪᴅᴇᴏ", YOUTUBE_TUTORIAL_URL)],  # URL button
        [("⇦ ɢᴏ ʙᴀᴄᴋ", "go_back_home"), ("⌧ Cʟᴏsᴇ ⌧", "close")]
    ]
    return create_keyboard(buttons)

def escape_html(text):
    """Escape HTML special characters"""
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')