from loguru import logger
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup
from utils.imagen import send_notification
from config import BOT_NAME, PARSE_MODE, WELCOME_IMAGE_URL
from utils.helpers import get_home_keyboard
from database import db

@Client.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    try:
        user_id = message.from_user.id
        username = message.from_user.username or "Unknown"
        first_name = message.from_user.first_name or "User"
        last_name = message.from_user.last_name or ""

        logger.info(f"🚀 Start command received from user: {username} (ID: {user_id})")
        
        # Add user to database FIRST
        user_added = await db.add_user(user_id, username, first_name, last_name)
        if user_added:
            logger.success(f"✅ User {username} saved to database")
        else:
            logger.warning(f"⚠️ Failed to save user {username} to database")
        
        welcome_text = f"""
<b>✨ Welcome to {BOT_NAME}!</b>

I can help you download TikTok videos without watermarks! 
<blockquote>
<b>What I offer:</b>
• 🎥 Download TikTok videos
• 🚫 No watermarks
• ⚡ Fast processing
• 🆓 Completely free
</blockquote>

<b>⟱ᴅᴏᴡɴʟᴏᴀᴅ ꜰʀᴏᴍ ᴡᴇʙꜱɪᴛᴇ⟱</b> 🎯
        """
        
        # Send welcome message with photo FIRST
        await message.reply_photo(
            photo=WELCOME_IMAGE_URL,
            caption=welcome_text,
            reply_markup=get_home_keyboard(),
            parse_mode=PARSE_MODE
        )
        
        logger.success(f"✅ Welcome message sent to user: {username} (ID: {user_id})")
        
        # Send notification AFTER the user gets their welcome message
        try:
            await send_notification(client, message.from_user.id, username, "Started Bot")
        except Exception as e:
            logger.error(f"❌ Notification failed: {e}")  # Don't break the bot if notification fails
        
    except Exception as e:
        logger.error(f"❌ Error in start command: {e}")
        await message.reply_text("❌ Sorry, something went wrong. Please try again later.")

@Client.on_callback_query(filters.regex("^go_back_home$"))
async def go_back_home_callback(client, callback_query):
    try:
        user_id = callback_query.from_user.id
        username = callback_query.from_user.username or "Unknown"
        logger.info(f"🏠 User {username} (ID: {user_id}) clicked 'Go Back Home'")
        
        # Update user last active time
        await db.add_user(user_id, username, callback_query.from_user.first_name or "User")
        
        welcome_text = f"""
<b>✨ Welcome to {BOT_NAME}!</b>

I can help you download TikTok videos without watermarks! 
<blockquote>
<b>What I offer:</b>
• 🎥 Download TikTok videos
• 🚫 No watermarks
• ⚡ Fast processing
• 🆓 Completely free
</blockquote>

<b>⟱ᴅᴏᴡɴʟᴏᴀᴅ ꜰʀᴏᴍ ᴡᴇʙꜱɪᴛᴇ⟱</b>
        """
        
        await callback_query.message.edit_caption(
            caption=welcome_text,
            reply_markup=get_home_keyboard(),
            parse_mode=PARSE_MODE
        )
        
        await callback_query.answer("Welcome back!", show_alert=False)
        logger.success(f"✅ Home page restored for user: {username} (ID: {user_id})")
        
    except Exception as e:
        logger.error(f"❌ Error in go_back_home callback: {e}")
        await callback_query.answer("Error occurred!", show_alert=True)

@Client.on_callback_query(filters.regex("^close$"))
async def close_callback(client, callback_query):
    try:
        user_id = callback_query.from_user.id
        username = callback_query.from_user.username or "Unknown"
        logger.info(f"❌ User {username} (ID: {user_id}) clicked 'Close'")
        
        await callback_query.message.delete()
        await callback_query.answer("Closed!", show_alert=False)
        logger.success(f"✅ Message closed for user: {username} (ID: {user_id})")
        
    except Exception as e:
        logger.error(f"❌ Error in close callback: {e}")
        await callback_query.answer("Error occurred!", show_alert=True)
