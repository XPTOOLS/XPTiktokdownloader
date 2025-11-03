from loguru import logger
from pyrogram import Client
import asyncio
import os

from config import BOT_TOKEN, API_ID, API_HASH, BOT_NAME
from database import db

# Import keep_alive module
from utils.keep_alive import start_keep_alive
import threading

# Import handlers
from XPTOOLS.start import *
from XPTOOLS.about import *
from XPTOOLS.tutorial import *

async def main():
    """Main function to start the bot"""
    try:
        logger.info(f"🚀 Starting {BOT_NAME} Bot...")
        
        # Start keep-alive server in a separate thread
        keep_alive_thread = threading.Thread(target=start_keep_alive, daemon=True)
        keep_alive_thread.start()
        logger.info("🔗 Keep-alive server started")
        
        # Test database connection
        logger.info("🔌 Testing database connection...")
        total_users = await db.get_total_users()
        logger.info(f"📊 Database connected. Total users: {total_users}")
        
        # Create bot client
        bot = Client(
            "tiktok_downloader_bot",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            plugins=dict(root="XPTOOLS")  # Make sure this points to your handlers directory
        )
        
        logger.info("✅ Bot client created successfully")
        
        # Start the bot
        await bot.start()
        logger.success(f"🎉 {BOT_NAME} Bot started successfully!")
        
        # Get bot info
        bot_info = await bot.get_me()
        logger.info(f"🤖 Bot Info: @{bot_info.username} (ID: {bot_info.id})")
        
        # Log admin features
        from config import ADMINS
        logger.info(f"🛡️ Admin features enabled for {len(ADMINS)} users")
        
        # Keep the bot running
        await asyncio.Event().wait()
        
    except Exception as e:
        logger.error(f"❌ Failed to start bot: {e}")
    finally:
        if 'bot' in locals():
            await bot.stop()
            logger.info("🛑 Bot stopped")

if __name__ == "__main__":
    # Run the bot
    asyncio.run(main())
