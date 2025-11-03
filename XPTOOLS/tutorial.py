from loguru import logger
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery

from config import TUTORIAL_PAGE, PARSE_MODE
from utils.helpers import get_tutorial_keyboard
from database import db

@Client.on_callback_query(filters.regex("^how_to_use$"))
async def how_to_use_callback(client: Client, callback_query: CallbackQuery):
    try:
        user_id = callback_query.from_user.id
        username = callback_query.from_user.username or "Unknown"
        logger.info(f"📖 User {username} (ID: {user_id}) clicked 'How to Use'")
        
        # Update user last active time
        await db.add_user(user_id, username, callback_query.from_user.first_name or "User")
        
        await callback_query.answer("Loading tutorial...", show_alert=False)
        
        tutorial_text = f"""
{TUTORIAL_PAGE}

<b>Ready to start downloading?</b> 🚀
        """
        
        await callback_query.message.edit_caption(
            caption=tutorial_text,
            reply_markup=get_tutorial_keyboard(),
            parse_mode=PARSE_MODE
        )
        
        logger.success(f"✅ Tutorial page shown to user: {username} (ID: {user_id})")
        
    except Exception as e:
        logger.error(f"❌ Error in how_to_use callback: {e}")
        await callback_query.answer("Error loading tutorial!", show_alert=True)