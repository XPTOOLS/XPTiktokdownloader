# XPTOOLS/startup.py
import pytz
from datetime import datetime
from pyrogram import enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from loguru import logger
from config import NOTIFICATION_CHANNEL, WELCOME_IMAGE_URL

def get_formatted_datetime():
    """Get current datetime in East Africa Time (EAT) timezone"""
    tz = pytz.timezone('Africa/Nairobi')
    now = datetime.now(tz)
    return {
        'date': now.strftime('%Y-%m-%d'),
        'time': now.strftime('%I:%M:%S %p'),
        'timezone': now.strftime('%Z')  # 'EAT'
    }

async def send_startup_message(bot, is_restart: bool = False):
    """Send bot startup or restart message to the notification channel."""
    try:
        if not NOTIFICATION_CHANNEL:
            logger.warning("⚠️ NOTIFICATION_CHANNEL not set, skipping startup message")
            return
            
        dt = get_formatted_datetime()
        status = "Rᴇꜱᴛᴀʀᴛᴇᴅ" if is_restart else "Sᴛᴀʀᴛᴇᴅ"

        bot_info = await bot.get_me()
        bot_username = bot_info.username
        bot_url = f"https://t.me/{bot_username}"

        # Try to get bot's profile picture using Pyrogram
        try:
            photos = []
            async for photo in bot.get_chat_photos(bot_info.id, limit=1):
                photos.append(photo)
            
            if photos:
                file_id = photos[0].file_id
                image_source = file_id
                logger.info("✅ Using bot's real profile photo for startup message")
            else:
                image_source = WELCOME_IMAGE_URL
                logger.info("🔄 Using fallback image for startup message")
        except Exception as e:
            image_source = WELCOME_IMAGE_URL
            logger.warning(f"⚠️ Using fallback image: {e}")

        message = f"""
<blockquote>
🚀 <b>Bᴏᴛ {status}</b> !

📅 Dᴀᴛᴇ : {dt['date']}
⏰ Tɪᴍᴇ : {dt['time']}
🌐 Tɪᴍᴇᴢᴏɴᴇ : {dt['timezone']}
🤖 Bᴏᴛ : @{bot_username}
🛠️ Bᴜɪʟᴅ Sᴛᴀᴛᴜꜱ: v2 [Sᴛᴀʙʟᴇ]
</blockquote>
"""

        # Inline button to open bot
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("🤖 Oᴘᴇɴ Bᴏᴛ", url=bot_url)]
        ])

        # Send as photo (uses bot profile or fallback image)
        await bot.send_photo(
            chat_id=NOTIFICATION_CHANNEL,
            photo=image_source,
            caption=message,
            parse_mode=enums.ParseMode.HTML,
            reply_markup=markup
        )
        
        logger.success(f"✅ Startup notification sent successfully - Bot {status}!")

    except Exception as e:
        logger.error(f"❌ Error sending startup message: {e}")