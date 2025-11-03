from loguru import logger
from pyrogram import Client, filters, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import (
    UserIsBlocked, PeerIdInvalid, ChatWriteForbidden, 
    ChannelPrivate, FloodWait, RPCError
)
import asyncio
import time
from datetime import datetime
from database import db
from config import ADMINS, PARSE_MODE

# Broadcast states storage
broadcast_states = {}

@Client.on_message(filters.command("broadcast") & filters.user(ADMINS))
async def broadcast_start(client: Client, message: Message):
    """
    Start the broadcast process
    """
    try:
        user_id = message.from_user.id
        logger.info(f"📤 Bʀᴏᴀᴅᴄᴀsᴛ ᴄᴏᴍᴍᴀɴᴅ ʀᴇᴄᴇɪᴠᴇᴅ ғʀᴏᴍ ᴀᴅᴍɪɴ: {user_id}")
        
        # Create inline cancel button
        cancel_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("☒ Cᴀɴᴄᴇʟ ☒", callback_data="cancel_broadcast_start")]
        ])
        
        broadcast_text = """<b>
📢 Cᴏᴍᴘᴏsᴇ Yᴏᴜʀ Bʀᴏᴀᴅᴄᴀsᴛ Mᴇssᴀɢᴇ ✨

Pʟᴇᴀsᴇ sᴇɴᴅ ᴛʜᴇ ᴍᴇssᴀɢᴇ ʏᴏᴜ'ᴅ ʟɪᴋᴇ ᴛᴏ sᴇɴᴅ ᴛᴏ ᴀʟʟ ᴜsᴇʀs.
Tʜɪs ᴡɪʟʟ ʙᴇ sᴇɴᴛ ᴀs ᴀ ʀᴇɢᴜʟᴀʀ (ᴜɴᴘɪɴɴᴇᴅ) ᴍᴇssᴀɢᴇ.

🖋️ Yᴏᴜ ᴄᴀɴ ɪɴᴄʟᴜᴅᴇ ᴛᴇxᴛ, ᴘʜᴏᴛᴏs, ᴠɪᴅᴇᴏs, ᴅᴏᴄᴜᴍᴇɴᴛs, ᴏʀ ᴀɴʏ ᴍᴇᴅɪᴀ.
❌ Cʟɪᴄᴋ ᴛʜᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴛᴏ ᴄᴀɴᴄᴇʟ:</b>
        """
        
        # Store broadcast state
        broadcast_states[user_id] = {"stage": "awaiting_message"}
        
        await message.reply_text(
            broadcast_text,
            parse_mode=PARSE_MODE,
            reply_markup=cancel_markup
        )
        
        logger.info(f"✅ Bʀᴏᴀᴅᴄᴀsᴛ ᴘʀᴏᴄᴇss sᴛᴀʀᴛᴇᴅ ғᴏʀ ᴀᴅᴍɪɴ: {user_id}")
        
    except Exception as e:
        logger.error(f"❌ Eʀʀᴏʀ ɪɴ ʙʀᴏᴀᴅᴄᴀsᴛ_sᴛᴀʀᴛ: {e}")
        await message.reply_text("❌ Eʀʀᴏʀ sᴛᴀʀᴛɪɴɢ ʙʀᴏᴀᴅᴄᴀsᴛ. Pʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ.")

@Client.on_message(filters.user(ADMINS) & ~filters.command("broadcast"))
async def process_broadcast_message(client: Client, message: Message):
    """
    Process the broadcast message sent by admin
    """
    try:
        user_id = message.from_user.id
        
        # Check if user is in broadcast state
        if user_id not in broadcast_states or broadcast_states[user_id].get("stage") != "awaiting_message":
            return
        
        # Get all users
        users = await get_all_users()
        if not users:
            del broadcast_states[user_id]
            await message.reply_text(
                "❌ Nᴏ ᴜsᴇʀs ғᴏᴜɴᴅ ᴛᴏ ʙʀᴏᴀᴅᴄᴀsᴛ ᴛᴏ",
                parse_mode=PARSE_MODE
            )
            logger.warning("❌ Nᴏ ᴜsᴇʀs ғᴏᴜɴᴅ ғᴏʀ ʙʀᴏᴀᴅᴄᴀsᴛ")
            return
        
        # Store message info for broadcasting
        broadcast_states[user_id] = {
            "stage": "broadcasting",
            "message": message,
            "users": users,
            "start_time": time.time()
        }
        
        # Show confirmation with message preview
        confirmation_text = await get_message_preview(message)
        confirmation_text += f"\n\n<b>Tᴏᴛᴀʟ Rᴇᴄɪᴘɪᴇɴᴛs</b>: {len(users):,}\n\nAʀᴇ ʏᴏᴜ sᴜʀᴇ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ sᴇɴᴅ ᴛʜɪs ʙʀᴏᴀᴅᴄᴀsᴛ?"
        
        confirmation_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Yᴇs, Sᴇɴᴅ Bʀᴏᴀᴅᴄᴀsᴛ", callback_data="confirm_broadcast")],
            [InlineKeyboardButton("☒ Cᴀɴᴄᴇʟ ☒", callback_data="cancel_broadcast")]
        ])
        
        await message.reply_text(
            confirmation_text,
            parse_mode=PARSE_MODE,
            reply_markup=confirmation_keyboard,
            reply_to_message_id=message.id
        )
        
        logger.info(f"✅ Bʀᴏᴀᴅᴄᴀsᴛ ᴍᴇssᴀɢᴇ ʀᴇᴄᴇɪᴠᴇᴅ ғʀᴏᴍ ᴀᴅᴍɪɴ: {user_id}, ᴀᴡᴀɪᴛɪɴɢ ᴄᴏɴғɪʀᴍᴀᴛɪᴏɴ")
        
    except Exception as e:
        logger.error(f"❌ Eʀʀᴏʀ ɪɴ ᴘʀᴏᴄᴇss_ʙʀᴏᴀᴅᴄᴀsᴛ_ᴍᴇssᴀɢᴇ: {e}")
        await message.reply_text("❌ Eʀʀᴏʀ ᴘʀᴏᴄᴇssɪɴɢ ʙʀᴏᴀᴅᴄᴀsᴛ ᴍᴇssᴀɢᴇ. Pʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ.")

@Client.on_callback_query(filters.regex("^confirm_broadcast$"))
async def confirm_broadcast(client, callback_query):
    """
    Handle broadcast confirmation
    """
    try:
        user_id = callback_query.from_user.id
        
        if user_id not in broadcast_states or broadcast_states[user_id].get("stage") != "broadcasting":
            await callback_query.answer("❌ Nᴏ ʙʀᴏᴀᴅᴄᴀsᴛ ᴘᴇɴᴅɪɴɢ!", show_alert=True)
            return
        
        broadcast_data = broadcast_states[user_id]
        message = broadcast_data["message"]
        users = broadcast_data["users"]
        
        await callback_query.answer("🚀 Sᴛᴀʀᴛɪɴɢ ʙʀᴏᴀᴅᴄᴀsᴛ...", show_alert=False)
        
        # Send initial progress message
        progress_msg = await callback_query.message.reply_text(
            "<b>📨 Bʀᴏᴀᴅᴄᴀsᴛ Iɴɪᴛɪᴀᴛᴇᴅ</b>\n\n"
            f"<b>📊 Tᴏᴛᴀʟ Rᴇᴄɪᴘɪᴇɴᴛs</b>: {len(users):,}\n"
            "<b>⏳ Sᴛᴀᴛᴜs: Pʀᴏᴄᴇssɪɴɢ...</b>\n\n"
            "[░░░░░░░░░░] 0%",
            parse_mode=PARSE_MODE
        )
        
        # Start broadcasting
        await send_broadcast(client, user_id, message, users, progress_msg)
        
    except Exception as e:
        logger.error(f"❌ Eʀʀᴏʀ ɪɴ ᴄᴏɴғɪʀᴍ_ʙʀᴏᴀᴅᴄᴀsᴛ: {e}")
        await callback_query.answer("❌ Eʀʀᴏʀ sᴛᴀʀᴛɪɴɢ ʙʀᴏᴀᴅᴄᴀsᴛ!", show_alert=True)

@Client.on_callback_query(filters.regex("^cancel_broadcast_start$"))
async def cancel_broadcast_start(client, callback_query):
    """
    Handle broadcast cancellation from start stage
    """
    try:
        user_id = callback_query.from_user.id
        
        if user_id in broadcast_states:
            del broadcast_states[user_id]
        
        await callback_query.message.edit_text(
            "🛑 Bʀᴏᴀᴅᴄᴀsᴛ ᴄᴀɴᴄᴇʟʟᴇᴅ.",
            parse_mode=PARSE_MODE
        )
        await callback_query.answer("Bʀᴏᴀᴅᴄᴀsᴛ ᴄᴀɴᴄᴇʟʟᴇᴅ!", show_alert=False)
        logger.info(f"❌ Bʀᴏᴀᴅᴄᴀsᴛ ᴄᴀɴᴄᴇʟʟᴇᴅ ʙʏ ᴀᴅᴍɪɴ: {user_id}")
        
    except Exception as e:
        logger.error(f"❌ Eʀʀᴏʀ ɪɴ ᴄᴀɴᴄᴇʟ_ʙʀᴏᴀᴅᴄᴀsᴛ_sᴛᴀʀᴛ: {e}")
        await callback_query.answer("Eʀʀᴏʀ ᴄᴀɴᴄᴇʟʟɪɴɢ ʙʀᴏᴀᴅᴄᴀsᴛ!", show_alert=True)

@Client.on_callback_query(filters.regex("^cancel_broadcast$"))
async def cancel_broadcast(client, callback_query):
    """
    Handle broadcast cancellation from confirmation stage
    """
    try:
        user_id = callback_query.from_user.id
        
        if user_id in broadcast_states:
            del broadcast_states[user_id]
        
        await callback_query.message.edit_text(
            "<b>🛑 Bʀᴏᴀᴅᴄᴀsᴛ ᴄᴀɴᴄᴇʟʟᴇᴅ.</b>",
            parse_mode=PARSE_MODE
        )
        await callback_query.answer("Bʀᴏᴀᴅᴄᴀsᴛ ᴄᴀɴᴄᴇʟʟᴇᴅ!", show_alert=False)
        logger.info(f"❌ Bʀᴏᴀᴅᴄᴀsᴛ ᴄᴀɴᴄᴇʟʟᴇᴅ ʙʏ ᴀᴅᴍɪɴ: {user_id}")
        
    except Exception as e:
        logger.error(f"❌ Eʀʀᴏʀ ɪɴ ᴄᴀɴᴄᴇʟ_ʙʀᴏᴀᴅᴄᴀsᴛ: {e}")
        await callback_query.answer("Eʀʀᴏʀ ᴄᴀɴᴄᴇʟʟɪɴɢ ʙʀᴏᴀᴅᴄᴀsᴛ!", show_alert=True)

async def send_broadcast(client: Client, admin_id: int, message: Message, users: list, progress_msg: Message):
    """
    Send broadcast to all users with progress tracking
    """
    try:
        success = 0
        blocked = 0
        deleted = 0
        not_found = 0
        bot_users = 0
        failed = 0
        
        total_users = len(users)
        start_time = broadcast_states[admin_id]["start_time"]
        
        # Calculate update interval
        update_interval = max(1, total_users // 10)
        
        for index, user_id in enumerate(users):
            try:
                # Use copy_message to preserve ALL Telegram formatting exactly
                await client.copy_message(
                    chat_id=user_id,
                    from_chat_id=message.chat.id,
                    message_id=message.id
                )
                success += 1
                
            except UserIsBlocked:
                blocked += 1
            except PeerIdInvalid:
                deleted += 1
            except (ChatWriteForbidden, ChannelPrivate):
                not_found += 1
            except FloodWait as e:
                logger.warning(f"Fʟᴏᴏᴅ ᴡᴀɪᴛ ғᴏʀ {user_id}: {e.value}s")
                await asyncio.sleep(e.value)
                failed += 1
            except RPCError as e:
                error_msg = str(e).lower()
                if "bot" in error_msg and "send" in error_msg:
                    bot_users += 1
                else:
                    failed += 1
                logger.error(f"RPC Eʀʀᴏʀ ғᴏʀ {user_id}: {e}")
            except Exception as e:
                failed += 1
                logger.error(f"Uɴᴇxᴘᴇᴄᴛᴇᴅ ᴇʀʀᴏʀ ғᴏʀ {user_id}: {e}")
            
            # Update progress periodically
            if (index + 1) % update_interval == 0 or (index + 1) == total_users:
                progress = int((index + 1) / total_users * 100)
                progress_bar = '█' * (progress // 10) + '░' * (10 - progress // 10)
                
                progress_text = f"""<blockquote><b>📨 Bʀᴏᴀᴅᴄᴀsᴛ Pʀᴏɢʀᴇss</blockquote>

📊 Tᴏᴛᴀʟ Rᴇᴄɪᴘɪᴇɴᴛs: {total_users:,}
✅ Sᴜᴄᴄᴇssғᴜʟ: {success}
🚫 Bʟᴏᴄᴋᴇᴅ: {blocked}
🗑️ Dᴇʟᴇᴛᴇᴅ: {deleted}
🔍 Nᴏᴛ Fᴏᴜɴᴅ: {not_found}
🤖 Bᴏᴛ Usᴇʀs: {bot_users}
❌ Fᴀɪʟᴇᴅ: {failed}
⏳ Sᴛᴀᴛᴜs: Sᴇɴᴅɪɴɢ...

[{progress_bar}] {progress}%</b>"""
                
                try:
                    await progress_msg.edit_text(progress_text, parse_mode=PARSE_MODE)
                except Exception as e:
                    logger.error(f"Fᴀɪʟᴇᴅ ᴛᴏ ᴜᴘᴅᴀᴛᴇ ᴘʀᴏɢʀᴇss: {e}")
            
            # Rate limiting to avoid flooding
            await asyncio.sleep(0.1)
        
        # Calculate time taken
        elapsed_time = int(time.time() - start_time)
        minutes = elapsed_time // 60
        seconds = elapsed_time % 60
        time_taken = f"{minutes}m {seconds}s" if minutes > 0 else f"{seconds}s"
        
        # Final completion message with close button
        completion_text = f"""<blockquote><b>📣 Bʀᴏᴀᴅᴄᴀsᴛ Cᴏᴍᴘʟᴇᴛᴇᴅ Sᴜᴄᴄᴇssғᴜʟʟʏ!</blockquote>

📊 Sᴛᴀᴛɪsᴛɪᴄs:
├ 📤 Sᴇɴᴛ: {success}
├ 🚫 Bʟᴏᴄᴋᴇᴅ: {blocked}
├ 🗑️ Dᴇʟᴇᴛᴇᴅ: {deleted}
├ 🔍 Nᴏᴛ Fᴏᴜɴᴅ: {not_found}
├ 🤖 Bᴏᴛ Usᴇʀs: {bot_users}
└ ❌ Fᴀɪʟᴇᴅ: {failed}

⏱️ Tɪᴍᴇ ᴛᴀᴋᴇɴ: {time_taken}
⏰ Fɪɴɪsʜᴇᴅ ᴀᴛ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

✨ Tʜᴀɴᴋ ʏᴏᴜ ғᴏʀ ᴜsɪɴɢ ᴏᴜʀ ʙʀᴏᴀᴅᴄᴀsᴛ sʏsᴛᴇᴍ!</b>"""
        
        # Create close button for completion message
        completion_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("⌧ Cʟᴏsᴇ ⌧", callback_data="close_broadcast_completion")]
        ])
        
        # Clean up broadcast state
        if admin_id in broadcast_states:
            del broadcast_states[admin_id]
        
        await progress_msg.edit_text(
            completion_text, 
            parse_mode=PARSE_MODE,
            reply_markup=completion_markup
        )
        logger.success(f"✅ Bʀᴏᴀᴅᴄᴀsᴛ ᴄᴏᴍᴘʟᴇᴛᴇᴅ ʙʏ ᴀᴅᴍɪɴ: {admin_id}. Sᴜᴄᴄᴇss: {success}/{total_users}")
        
    except Exception as e:
        logger.error(f"❌ Eʀʀᴏʀ ɪɴ sᴇɴᴅ_ʙʀᴏᴀᴅᴄᴀsᴛ: {e}")
        if admin_id in broadcast_states:
            del broadcast_states[admin_id]
        await progress_msg.edit_text("❌ Eʀʀᴏʀ ᴅᴜʀɪɴɢ ʙʀᴏᴀᴅᴄᴀsᴛ. Pʟᴇᴀsᴇ ᴄʜᴇᴄᴋ ʟᴏɢs.")

@Client.on_callback_query(filters.regex("^close_broadcast_completion$"))
async def close_broadcast_completion(client, callback_query):
    """
    Handle close button for broadcast completion message
    """
    try:
        user_id = callback_query.from_user.id
        
        # Check if user is admin
        if user_id not in ADMINS:
            await callback_query.answer("❌ Yᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ!", show_alert=True)
            return
        
        await callback_query.message.delete()
        await callback_query.answer("Mᴇssᴀɢᴇ ᴄʟᴏsᴇᴅ!", show_alert=False)
        logger.success(f"✅ Bʀᴏᴀᴅᴄᴀsᴛ ᴄᴏᴍᴘʟᴇᴛɪᴏɴ ᴍᴇssᴀɢᴇ ᴄʟᴏsᴇᴅ ʙʏ ᴀᴅᴍɪɴ: {user_id}")
        
    except Exception as e:
        logger.error(f"❌ Eʀʀᴏʀ ɪɴ ᴄʟᴏsᴇ_ʙʀᴏᴀᴅᴄᴀsᴛ_ᴄᴏᴍᴘʟᴇᴛɪᴏɴ: {e}")
        await callback_query.answer("Eʀʀᴏʀ ᴄʟᴏsɪɴɢ ᴍᴇssᴀɢᴇ!", show_alert=True)

async def get_all_users():
    """
    Get all user IDs from database
    """
    try:
        users_cursor = db.users.find({}, {"user_id": 1})
        user_ids = [user["user_id"] for user in users_cursor]
        logger.debug(f"📋 Rᴇᴛʀɪᴇᴠᴇᴅ {len(user_ids)} ᴜsᴇʀs ғᴏʀ ʙʀᴏᴀᴅᴄᴀsᴛ")
        return user_ids
    except Exception as e:
        logger.error(f"❌ Eʀʀᴏʀ ɢᴇᴛᴛɪɴɢ ᴀʟʟ ᴜsᴇʀs: {e}")
        return []

async def get_message_preview(message: Message):
    """
    Generate a preview of the message for confirmation
    """
    try:
        preview = "📋 Mᴇssᴀɢᴇ Pʀᴇᴠɪᴇᴡ:\n\n"
        
        if message.text:
            # Show first 200 characters of text
            text_preview = message.text[:200] + "..." if len(message.text) > 200 else message.text
            preview += f"📝 Tᴇxᴛ: {text_preview}\n"
        
        if message.photo:
            preview += "🖼️ Mᴇᴅɪᴀ: Pʜᴏᴛᴏ\n"
        elif message.video:
            preview += "🎥 Mᴇᴅɪᴀ: Vɪᴅᴇᴏ\n"
        elif message.document:
            preview += "📄 Mᴇᴅɪᴀ: Dᴏᴄᴜᴍᴇɴᴛ\n"
        elif message.audio:
            preview += "🎵 Mᴇᴅɪᴀ: Aᴜᴅɪᴏ\n"
        elif message.voice:
            preview += "🎤 Mᴇᴅɪᴀ: Vᴏɪᴄᴇ Mᴇssᴀɢᴇ\n"
        elif message.sticker:
            preview += "😊 Mᴇᴅɪᴀ: Sᴛɪᴄᴋᴇʀ\n"
        elif message.animation:
            preview += "🎬 Mᴇᴅɪᴀ: GIF/Aɴɪᴍᴀᴛɪᴏɴ\n"
        
        if message.caption:
            caption_preview = message.caption[:100] + "..." if len(message.caption) > 100 else message.caption
            preview += f"📋 Cᴀᴘᴛɪᴏɴ: {caption_preview}\n"
        
        return preview
        
    except Exception as e:
        logger.error(f"❌ Eʀʀᴏʀ ɢᴇɴᴇʀᴀᴛɪɴɢ ᴍᴇssᴀɢᴇ ᴘʀᴇᴠɪᴇᴡ: {e}")
        return "📋 Mᴇssᴀɢᴇ Pʀᴇᴠɪᴇᴡ: [Uɴᴀʙʟᴇ ᴛᴏ ɢᴇɴᴇʀᴀᴛᴇ ᴘʀᴇᴠɪᴇᴡ]"