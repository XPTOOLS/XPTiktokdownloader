from loguru import logger
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta

from config import PARSE_MODE, BOT_NAME, ADMINS
from database import db

@Client.on_message(filters.command("stats") & filters.user(ADMINS))
async def stats_command(client: Client, message: Message):
    """
    Display bot statistics for admins
    """
    try:
        user_id = message.from_user.id
        logger.info(f"📊 Stats command received from admin: {user_id}")
        
        # Get all statistics
        total_users = await db.get_total_users()
        active_users_today = await db.get_active_users_today()
        
        # Get user growth data
        user_growth = await get_user_growth()
        monthly_growth = user_growth.get('monthly_growth', 0)
        
        # Get average daily stats
        avg_daily_starts = await get_average_daily_starts()
        
        # Format the statistics message
        stats_text = format_stats_message(total_users, active_users_today, monthly_growth, avg_daily_starts)
        
        # Create close button
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("⌧ Cʟᴏsᴇ ⌧", callback_data="close_stats")]
        ])
        
        # Send the statistics
        await message.reply_text(
            stats_text, 
            parse_mode=PARSE_MODE, 
            disable_web_page_preview=True,
            reply_markup=keyboard
        )
        
        logger.success(f"✅ Statistics sent to admin: {user_id}")
        
    except Exception as e:
        logger.error(f"❌ Error in stats command: {e}")
        await message.reply_text("❌ Error gathering statistics. Please try again later.", parse_mode=PARSE_MODE)

async def get_user_growth():
    """
    Calculate user growth statistics
    """
    try:
        # Get total users
        total_users = await db.get_total_users()
        
        # Get users from last 30 days
        month_ago = datetime.now() - timedelta(days=30)
        monthly_users = db.users.count_documents({
            "joined_date": {"$gte": month_ago}
        })
        
        growth_data = {
            'total_users': total_users,
            'monthly_growth': monthly_users
        }
        
        logger.debug(f"📈 User growth data calculated: {growth_data}")
        return growth_data
        
    except Exception as e:
        logger.error(f"❌ Error calculating user growth: {e}")
        return {'total_users': 0, 'monthly_growth': 0}

async def get_average_daily_starts():
    """
    Calculate average daily bot starts
    """
    try:
        # Get stats for the last 7 days
        weekly_stats = []
        total_starts = 0
        days_count = 7
        
        for i in range(days_count):
            date = datetime.now() - timedelta(days=i)
            date = date.replace(hour=0, minute=0, second=0, microsecond=0)
            
            stats = await db.get_daily_stats(date)
            if stats:
                total_starts += stats.get('bot_starts', 0)
        
        avg_daily = total_starts // days_count if total_starts > 0 else 0
        logger.debug(f"📅 Average daily starts calculated: {avg_daily}")
        return avg_daily
        
    except Exception as e:
        logger.error(f"❌ Error calculating average daily starts: {e}")
        return 0

def format_stats_message(total_users, active_users_today, monthly_growth, avg_daily_starts):
    """
    Format the statistics into the requested message format
    """
    try:
        # Create statistics message in the requested format
        stats_text = f"""
<blockquote><b>⍟───[ ʙᴏᴛ sᴛᴀᴛɪꜱᴛɪᴄꜱ ]───⍟</b></blockquote>

<blockquote><b>👥 User Statistics:</b></blockquote>
├ • <b>Total Users:</b> {total_users:,}
├ • <b>Active Today:</b> {active_users_today}
└ • <b>Monthly Growth:</b> {monthly_growth:,}
└ • <b>Average Daily:</b> {avg_daily_starts}

<blockquote>🚀 <b>Bot Performance:</b></blockquote>
├ • <b>Uptime:</b> Online ✅
├ • <b>Database:</b> Connected ✅
└ • <b>Last Updated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

<b>💡 Pro Tip:</b> Use /broadcast to send announcements to all users!
"""
        
        logger.debug("✅ Statistics message formatted successfully")
        return stats_text
        
    except Exception as e:
        logger.error(f"❌ Error formatting stats message: {e}")
        return "❌ Error formatting statistics. Please check the logs."

@Client.on_callback_query(filters.regex("^close_stats$"))
async def close_stats_callback(client, callback_query):
    """
    Handle close button for stats message
    """
    try:
        user_id = callback_query.from_user.id
        logger.info(f"❌ User {user_id} clicked 'Close' on stats")
        
        # Check if user is admin
        if user_id not in ADMINS:
            await callback_query.answer("❌ You are not authorized!", show_alert=True)
            return
        
        await callback_query.message.delete()
        await callback_query.answer("Stats closed!", show_alert=False)
        logger.success(f"✅ Stats message closed by admin: {user_id}")
        
    except Exception as e:
        logger.error(f"❌ Error in close_stats callback: {e}")
        await callback_query.answer("Error occurred!", show_alert=True)