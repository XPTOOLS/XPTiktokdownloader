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
async def broadcast_command(client: Client, message: Message):
    """
    Start the broadcast process with a proper flow
    """
    try:
        user_id = message.from_user.id
        logger.info(f"📢 Broadcast command received from admin: {user_id}")
        
        # Check if there's a replied message
        if message.reply_to_message:
            # If replying to a message, use that as broadcast content
            await process_broadcast_confirmation(client, message)
        else:
            # Show instructions to reply to a message
            instruction_text = """
<b>📢 How to send a broadcast:</b>

1. <b>Create your message</b> first (text, photo, video, etc.)
2. <b>Reply to that message</b> with /broadcast
3. <b>Confirm</b> the broadcast when prompted

<blockquote>
💡 <b>Tip:</b> You can broadcast any type of message - text, photos, videos, documents, etc.
</blockquote>

<b>Current method:</b>
↳ Create your message and reply to it with /broadcast
"""
            
            await message.reply_text(
                instruction_text,
                parse_mode=PARSE_MODE,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("☒ ᴄᴀɴᴄᴇʟ ☒", callback_data="cancel_broadcast")]
                ])
            )
        
    except Exception as e:
        logger.error(f"❌ Error in broadcast command: {e}")
        await message.reply_text("❌ Error starting broadcast. Please try again.")

async def process_broadcast_confirmation(client: Client, message: Message):
    """
    Process broadcast confirmation when admin replies to a message with /broadcast
    """
    try:
        user_id = message.from_user.id
        
        if not message.reply_to_message:
            await message.reply_text("❌ Please reply to a message with /broadcast")
            return
        
        # Get all users
        users = await get_all_users()
        if not users:
            await message.reply_text("❌ No users found to broadcast to.")
            return
        
        # Store broadcast data
        broadcast_states[user_id] = {
            "message": message.reply_to_message,
            "users": users,
            "start_time": time.time()
        }
        
        # Show confirmation with message preview
        confirmation_text = await get_message_preview(message.reply_to_message)
        confirmation_text += f"\n\n<b>Total Recipients</b>: {len(users):,}\n\nAre you sure you want to send this broadcast?"
        
        confirmation_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("☑ ʏᴇꜱ, ꜱᴇɴᴅ ʙʀᴏᴀᴅᴄᴀꜱᴛ", callback_data="confirm_broadcast")],
            [InlineKeyboardButton("☒ ᴄᴀɴᴄᴇʟ ☒", callback_data="cancel_broadcast")]
        ])
        
        await message.reply_text(
            confirmation_text,
            parse_mode=PARSE_MODE,
            reply_markup=confirmation_keyboard
        )
        
        logger.info(f"📢 Broadcast confirmation sent to admin: {user_id}")
        
    except Exception as e:
        logger.error(f"❌ Error in process_broadcast_confirmation: {e}")
        await message.reply_text("❌ Error processing broadcast. Please try again.")

@Client.on_callback_query(filters.regex("^confirm_broadcast$"))
async def confirm_broadcast(client, callback_query):
    """
    Handle broadcast confirmation
    """
    try:
        user_id = callback_query.from_user.id
        
        if user_id not in broadcast_states:
            await callback_query.answer("❌ No broadcast pending!", show_alert=True)
            return
        
        broadcast_data = broadcast_states[user_id]
        message = broadcast_data["message"]
        users = broadcast_data["users"]
        
        await callback_query.answer("🚀 Starting broadcast...", show_alert=False)
        
        # Send initial progress message
        progress_msg = await callback_query.message.reply_text(
            "<b>📢 Broadcast In Progress</b>\n\n"
            f"<b>📊 Total Recipients</b>: {len(users):,}\n"
            "<b>⏳ Status: Processing...</b>\n\n"
            "[░░░░░░░░░░] 0%",
            parse_mode=PARSE_MODE
        )
        
        # Start broadcasting
        await send_broadcast(client, user_id, message, users, progress_msg)
        
    except Exception as e:
        logger.error(f"❌ Error in confirm_broadcast: {e}")
        await callback_query.answer("❌ Error starting broadcast!", show_alert=True)

@Client.on_callback_query(filters.regex("^cancel_broadcast$"))
async def cancel_broadcast(client, callback_query):
    """
    Handle broadcast cancellation
    """
    try:
        user_id = callback_query.from_user.id
        
        if user_id in broadcast_states:
            del broadcast_states[user_id]
        
        await callback_query.message.edit_text(
            "❌ Broadcast cancelled.",
            parse_mode=PARSE_MODE
        )
        await callback_query.answer("Broadcast cancelled!", show_alert=False)
        logger.info(f"❌ Broadcast cancelled by admin: {user_id}")
        
    except Exception as e:
        logger.error(f"❌ Error in cancel_broadcast: {e}")
        await callback_query.answer("Error cancelling broadcast!", show_alert=True)

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
