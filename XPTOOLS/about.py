from loguru import logger
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery

from config import ABOUT_PAGE, PARSE_MODE
from utils.helpers import get_about_keyboard
from database import db

@Client.on_callback_query(filters.regex("^about_me$"))
async def about_me_callback(client: Client, callback_query: CallbackQuery):
    try:
        user_id = callback_query.from_user.id
        username = callback_query.from_user.username or "Unknown"
        logger.info(f"ℹ️ User {username} (ID: {user_id}) clicked 'About Me'")
        
        # Update user last active time
        await db.add_user(user_id, username, callback_query.from_user.first_name or "User")
        
        await callback_query.answer("Loading about information...", show_alert=False)
        
        about_text = f"""
{ABOUT_PAGE}

<b>Thank you for using our service!</b> 💫
        """
        
        await callback_query.message.edit_caption(
            caption=about_text,
            reply_markup=get_about_keyboard(),
            parse_mode=PARSE_MODE
        )
        
        logger.success(f"✅ About page shown to user: {username} (ID: {user_id})")
        
    except Exception as e:
        logger.error(f"❌ Error in about_me callback: {e}")
        await callback_query.answer("Error loading about page!", show_alert=True)