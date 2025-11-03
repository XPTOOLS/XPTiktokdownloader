from loguru import logger
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from database import db
from datetime import datetime
from config import PARSE_MODE, BOT_NAME

@Client.on_message(filters.command("policy"))
async def policy_command(client: Client, message: Message):
    """
    Display bot policy and terms of service
    """
    try:
        user_id = message.from_user.id
        username = message.from_user.username or "Unknown"
        first_name = message.from_user.first_name or "User"
        
        logger.info(f"📜 Pᴏʟɪᴄʏ ᴄᴏᴍᴍᴀɴᴅ ʀᴇᴄᴇɪᴠᴇᴅ ғʀᴏᴍ ᴜsᴇʀ: {username} (ID: {user_id})")
        
        policy_text = f"""
<blockquote><b>⍟───[ {BOT_NAME} Pᴏʟɪᴄʏ & Tᴇʀᴍs ]───⍟</b></blockquote>

<blockquote><b>📜 Tᴇʀᴍs ᴏғ Sᴇʀᴠɪᴄᴇ</b></blockquote>

<blockquote><b>1. Aᴄᴄᴇᴘᴛᴀɴᴄᴇ ᴏғ Tᴇʀᴍs</b></blockquote>
Bʏ ᴜsɪɴɢ {BOT_NAME}, ʏᴏᴜ ᴀɢʀᴇᴇ ᴛᴏ ᴄᴏᴍᴘʟʏ ᴡɪᴛʜ ᴛʜᴇsᴇ ᴛᴇʀᴍs ᴀɴᴅ ᴄᴏɴᴅɪᴛɪᴏɴs.

<blockquote><b>2. Sᴇʀᴠɪᴄᴇ Dᴇsᴄʀɪᴘᴛɪᴏɴ</b></blockquote>
Oᴜʀ sᴇʀᴠɪᴄᴇ ᴀʟʟᴏᴡs ᴜsᴇʀs ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ TɪᴋTᴏᴋ ᴠɪᴅᴇᴏs ᴡɪᴛʜᴏᴜᴛ ᴡᴀᴛᴇʀᴍᴀʀᴋs.

<blockquote><b>3. Usᴇʀ Rᴇsᴘᴏɴsɪʙɪʟɪᴛɪᴇs</b></blockquote>
├ • Yᴏᴜ ᴍᴜsᴛ ʜᴀᴠᴇ ᴘᴇʀᴍɪssɪᴏɴ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ ᴀɴᴅ ᴜsᴇ ᴄᴏɴᴛᴇɴᴛ
├ • Dᴏ ɴᴏᴛ ᴠɪᴏʟᴀᴛᴇ ᴄᴏᴘʏʀɪɢʜᴛ ʟᴀᴡs
├ • Rᴇsᴘᴇᴄᴛ ᴘʀɪᴠᴀᴄʏ ᴀɴᴅ ɪɴᴛᴇʟʟᴇᴄᴛᴜᴀʟ ᴘʀᴏᴘᴇʀᴛʏ ʀɪɢʜᴛs
└ • Usᴇ ᴛʜᴇ sᴇʀᴠɪᴄᴇ ʟᴇɢᴀʟʟʏ ᴀɴᴅ ᴇᴛʜɪᴄᴀʟʟʏ

<blockquote><b>4. Pʀᴏʜɪʙɪᴛᴇᴅ Usᴇs</b></blockquote>
├ • Iʟʟᴇɢᴀʟ ᴀᴄᴛɪᴠɪᴛɪᴇs
├ • Cᴏᴘʏʀɪɢʜᴛ ɪɴғʀɪɴɢᴇᴍᴇɴᴛ
├ • Sᴘᴀᴍᴍɪɴɢ ᴏʀ ᴀʙᴜsɪᴠᴇ ʙᴇʜᴀᴠɪᴏʀ
├ • Dɪsᴛʀɪʙᴜᴛɪɴɢ ᴍᴀʟɪᴄɪᴏᴜs ᴄᴏɴᴛᴇɴᴛ
└ • Vɪᴏʟᴀᴛɪɴɢ ᴛᴇʀᴍs ᴏғ ᴘʟᴀᴛғᴏʀᴍs

<blockquote><b>5. Pʀɪᴠᴀᴄʏ Pᴏʟɪᴄʏ</b></blockquote>
├ • Wᴇ ᴄᴏʟʟᴇᴄᴛ ᴏɴʟʏ ɴᴇᴄᴇssᴀʀʏ ᴜsᴇʀ ᴅᴀᴛᴀ
├ • Yᴏᴜʀ ᴅᴀᴛᴀ ɪs sᴇᴄᴜʀᴇʟʏ sᴛᴏʀᴇᴅ
├ • Wᴇ ᴅᴏ ɴᴏᴛ sʜᴀʀᴇ ᴅᴀᴛᴀ ᴡɪᴛʜ ᴛʜɪʀᴅ ᴘᴀʀᴛɪᴇs
└ • Yᴏᴜ ᴄᴀɴ ʀᴇǫᴜᴇsᴛ ᴅᴀᴛᴀ ᴅᴇʟᴇᴛɪᴏɴ

<blockquote><b>6. Sᴇʀᴠɪᴄᴇ Mᴏᴅɪғɪᴄᴀᴛɪᴏɴs</b></blockquote>
Wᴇ ʀᴇsᴇʀᴠᴇ ᴛʜᴇ ʀɪɢʜᴛ ᴛᴏ ᴍᴏᴅɪғʏ ᴏʀ ᴅɪsᴄᴏɴᴛɪɴᴜᴇ ᴛʜᴇ sᴇʀᴠɪᴄᴇ ᴀᴛ ᴀɴʏ ᴛɪᴍᴇ.

<blockquote><b>7. Lɪᴀʙɪʟɪᴛʏ Lɪᴍɪᴛᴀᴛɪᴏɴ</b></blockquote>
Wᴇ ᴀʀᴇ ɴᴏᴛ ʟɪᴀʙʟᴇ ғᴏʀ ᴀɴʏ ᴅᴀᴍᴀɢᴇs ᴀʀɪsɪɴɢ ғʀᴏᴍ ᴜsᴇ ᴏғ ᴛʜᴇ sᴇʀᴠɪᴄᴇ.

<blockquote><b>8. Gᴏᴠᴇʀɴɪɴɢ Lᴀᴡ</b></blockquote>
Tʜᴇsᴇ ᴛᴇʀᴍs ᴀʀᴇ ɢᴏᴠᴇʀɴᴇᴅ ʙʏ ɪɴᴛᴇʀɴᴀᴛɪᴏɴᴀʟ ʟᴀᴡs ᴀɴᴅ ʀᴇɢᴜʟᴀᴛɪᴏɴs.

<blockquote><b>9. Cᴏɴᴛᴀᴄᴛ Iɴғᴏʀᴍᴀᴛɪᴏɴ</b></blockquote>
Fᴏʀ ǫᴜᴇsᴛɪᴏɴs ᴀʙᴏᴜᴛ ᴛʜᴇsᴇ ᴛᴇʀᴍs, ᴄᴏɴᴛᴀᴄᴛ ᴛʜᴇ sᴜᴘᴘᴏʀᴛ ᴛᴇᴀᴍ.

<blockquote><b>10. Aᴄᴄᴇᴘᴛᴀɴᴄᴇ</b></blockquote>
Bʏ ᴄʟɪᴄᴋɪɴɢ "I Aᴄᴄᴇᴘᴛ", ʏᴏᴜ ᴀᴄᴋɴᴏᴡʟᴇᴅɢᴇ ᴛʜᴀᴛ ʏᴏᴜ ʜᴀᴠᴇ ʀᴇᴀᴅ, ᴜɴᴅᴇʀsᴛᴏᴏᴅ, ᴀɴᴅ ᴀɢʀᴇᴇ ᴛᴏ ʙᴇ ʙᴏᴜɴᴅ ʙʏ ᴛʜᴇsᴇ ᴛᴇʀᴍs ᴀɴᴅ ᴄᴏɴᴅɪᴛɪᴏɴs.
"""

        # Create accept and close buttons
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("☑ I Aᴄᴄᴇᴘᴛ", callback_data="accept_policy")],
            [InlineKeyboardButton("⌧ Cʟᴏsᴇ ⌧", callback_data="close_policy")]
        ])
        
        await message.reply_text(
            policy_text,
            parse_mode=PARSE_MODE,
            reply_markup=keyboard,
            disable_web_page_preview=True
        )
        
        logger.success(f"✅ Pᴏʟɪᴄʏ sʜᴏᴡɴ ᴛᴏ ᴜsᴇʀ: {username} (ID: {user_id})")
        
    except Exception as e:
        logger.error(f"❌ Eʀʀᴏʀ ɪɴ ᴘᴏʟɪᴄʏ_ᴄᴏᴍᴍᴀɴᴅ: {e}")
        await message.reply_text("❌ Eʀʀᴏʀ ᴅɪsᴘʟᴀʏɪɴɢ ᴘᴏʟɪᴄʏ. Pʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ.")

@Client.on_callback_query(filters.regex("^accept_policy$"))
async def accept_policy_callback(client, callback_query):
    """
    Handle policy acceptance
    """
    try:
        user_id = callback_query.from_user.id
        username = callback_query.from_user.username or "Unknown"
        first_name = callback_query.from_user.first_name or "User"
        
        logger.info(f"✅ Usᴇʀ {username} (ID: {user_id}) ᴀᴄᴄᴇᴘᴛᴇᴅ ᴘᴏʟɪᴄʏ")
        
        # Update user in database to mark policy accepted
        await update_policy_acceptance(user_id, username, first_name)
        
        # Show acceptance confirmation
        acceptance_text = f"""
<blockquote><b>✅ Pᴏʟɪᴄʏ Aᴄᴄᴇᴘᴛᴇᴅ Sᴜᴄᴄᴇssғᴜʟʟʏ!</b></blockquote>

Tʜᴀɴᴋ ʏᴏᴜ ғᴏʀ ᴀᴄᴄᴇᴘᴛɪɴɢ ᴛʜᴇ {BOT_NAME} ᴛᴇʀᴍs ᴀɴᴅ ᴄᴏɴᴅɪᴛɪᴏɴs.

<blockquote><b>Wʜᴀᴛ's Nᴇxᴛ?</b></blockquote>
• Usᴇ /start ᴛᴏ ʙᴇɢɪɴ ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ ᴠɪᴅᴇᴏs
• Cʜᴇᴄᴋ ᴏᴜᴛ ᴏᴜʀ ᴡᴇʙsɪᴛᴇ ғᴏʀ ᴍᴏʀᴇ ғᴇᴀᴛᴜʀᴇs

Wᴇʟᴄᴏᴍᴇ ᴛᴏ {BOT_NAME}! 🎉
"""
        
        # Create close button for acceptance message
        close_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("⌧ Cʟᴏsᴇ ⌧", callback_data="close_policy_acceptance")]
        ])
        
        await callback_query.message.edit_text(
            acceptance_text,
            parse_mode=PARSE_MODE,
            reply_markup=close_keyboard,
            disable_web_page_preview=True
        )
        
        await callback_query.answer("Pᴏʟɪᴄʏ ᴀᴄᴄᴇᴘᴛᴇᴅ!", show_alert=False)
        logger.success(f"✅ Pᴏʟɪᴄʢ ᴀᴄᴄᴇᴘᴛᴀɴᴄᴇ ᴄᴏɴғɪʀᴍᴇᴅ ғᴏʀ ᴜsᴇʀ: {username} (ID: {user_id})")
        
    except Exception as e:
        logger.error(f"❌ Eʀʀᴏʀ ɪɴ ᴀᴄᴄᴇᴘᴛ_ᴘᴏʟɪᴄʏ_ᴄᴀʟʟʙᴀᴄᴋ: {e}")
        await callback_query.answer("❌ Eʀʀᴏʀ ᴀᴄᴄᴇᴘᴛɪɴɢ ᴘᴏʟɪᴄʏ!", show_alert=True)

@Client.on_callback_query(filters.regex("^close_policy$"))
async def close_policy_callback(client, callback_query):
    """
    Handle policy close button
    """
    try:
        user_id = callback_query.from_user.id
        username = callback_query.from_user.username or "Unknown"
        
        await callback_query.message.delete()
        await callback_query.answer("Pᴏʟɪᴄʏ ᴄʟᴏsᴇᴅ!", show_alert=False)
        logger.info(f"❌ Pᴏʟɪᴄʏ ᴄʟᴏsᴇᴅ ʙʏ ᴜsᴇʀ: {username} (ID: {user_id})")
        
    except Exception as e:
        logger.error(f"❌ Eʀʀᴏʀ ɪɴ ᴄʟᴏsᴇ_ᴘᴏʟɪᴄʏ_ᴄᴀʟʟʙᴀᴄᴋ: {e}")
        await callback_query.answer("Eʀʀᴏʀ ᴄʟᴏsɪɴɢ ᴘᴏʟɪᴄʏ!", show_alert=True)

@Client.on_callback_query(filters.regex("^close_policy_acceptance$"))
async def close_policy_acceptance_callback(client, callback_query):
    """
    Handle policy acceptance close button
    """
    try:
        user_id = callback_query.from_user.id
        username = callback_query.from_user.username or "Unknown"
        
        await callback_query.message.delete()
        await callback_query.answer("Mᴇssᴀɢᴇ ᴄʟᴏsᴇᴅ!", show_alert=False)
        logger.info(f"❌ Pᴏʟɪᴄʏ ᴀᴄᴄᴇᴘᴛᴀɴᴄᴇ ᴍᴇssᴀɢᴇ ᴄʟᴏsᴇᴅ ʙʏ ᴜsᴇʀ: {username} (ID: {user_id})")
        
    except Exception as e:
        logger.error(f"❌ Eʀʀᴏʀ ɪɴ ᴄʟᴏsᴇ_ᴘᴏʟɪᴄʏ_ᴀᴄᴄᴇᴘᴛᴀɴᴄᴇ_ᴄᴀʟʟʙᴀᴄᴋ: {e}")
        await callback_query.answer("Eʀʀᴏʀ ᴄʟᴏsɪɴɢ ᴍᴇssᴀɢᴇ!", show_alert=True)

async def update_policy_acceptance(user_id: int, username: str, first_name: str):
    """
    Update user record to mark policy as accepted
    """
    try:
        # Update user in database with policy acceptance
        user_data = {
            "user_id": user_id,
            "username": username,
            "first_name": first_name,
            "policy_accepted": True,
            "policy_accepted_date": datetime.now(),
            "last_active": datetime.now()
        }
        
        # Update if exists, insert if new
        result = db.users.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "username": username,
                    "first_name": first_name,
                    "policy_accepted": True,
                    "policy_accepted_date": datetime.now(),
                    "last_active": datetime.now()
                },
                "$setOnInsert": {
                    "joined_date": datetime.now()
                },
                "$inc": {"total_starts": 1}
            },
            upsert=True
        )
        
        if result.upserted_id:
            logger.info(f"📝 Nᴇᴡ ᴜsᴇʀ ᴀᴅᴅᴇᴅ ᴡɪᴛʜ ᴘᴏʟɪᴄʏ ᴀᴄᴄᴇᴘᴛᴀɴᴄᴇ: {username} (ID: {user_id})")
        else:
            logger.info(f"📝 Usᴇʀ ᴜᴘᴅᴀᴛᴇᴅ ᴡɪᴛʜ ᴘᴏʟɪᴄʏ ᴀᴄᴄᴇᴘᴛᴀɴᴄᴇ: {username} (ID: {user_id})")
            
        return True
        
    except Exception as e:
        logger.error(f"❌ Eʀʀᴏʀ ᴜᴘᴅᴀᴛɪɴɢ ᴘᴏʟɪᴄʏ ᴀᴄᴄᴇᴘᴛᴀɴᴄᴇ: {e}")
        return False