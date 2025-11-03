# imagen.py
import io
import random
import hashlib
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
from datetime import datetime
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from loguru import logger
from pyrogram import enums
from config import NOTIFICATION_CHANNEL, SUPPORT_GROUP_URL, SOURCE_CODE_URL

# ======================
# GENERATED AVATAR FUNCTION (from your sample)
# ======================
def generate_avatar(name: str, size: tuple = (500, 500)) -> Image.Image:
    """
    Generate a professional circular avatar from username.
    Uses hash → color + initials.
    """
    if not name or name.strip() == "":
        name = "Unknown"

    # Hash name for consistent color
    hash_obj = hashlib.md5(name.encode("utf-8"))
    color = tuple(int(hash_obj.hexdigest()[i:i+2], 16) for i in (0, 2, 4))  # RGB
    color = tuple(min(220, max(60, c)) for c in color)  # Keep it readable

    # Base image
    img = Image.new("RGBA", size, (*color, 255))
    draw = ImageDraw.Draw(img)

    # Circle background
    draw.ellipse((0, 0, size[0], size[1]), fill=(*color, 255))

    # Initials
    initials = "".join([part[0].upper() for part in name.split() if part])[:2]
    if not initials:
        initials = "U"

    try:
        # Try large font first
        font_size = 200
        font = ImageFont.truetype("arialbd.ttf", font_size)
    except:
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default().font_variant(size=font_size // 2)

    bbox = draw.textbbox((0, 0), initials, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (size[0] - text_width) // 2
    y = (size[1] - text_height) // 2

    draw.text((x, y), initials, font=font, fill=(255, 255, 255))

    # Apply circular mask
    mask = Image.new('L', size, 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse((0, 0, size[0], size[1]), fill=255)
    img.putalpha(mask)

    return img

# ======================
# NOTIFICATION FUNCTION (EXACTLY from your sample)
# ======================
async def generate_notification_image(user_name: str, bot_name: str, user_photo: Image.Image = None, bot_photo: Image.Image = None, action: str = "Started"):
    """Generate a pro-quality notification image - EXACT COPY from your sample"""
    try:
        # Use generated avatars if no photos provided
        if user_photo is None:
            user_photo = generate_avatar(user_name)
        if bot_photo is None:
            bot_photo = generate_avatar(bot_name)

        width, height = 1000, 500
        bg = Image.new("RGB", (width, height), (10, 15, 30))
        draw = ImageDraw.Draw(bg)

        # Gradient background
        for y in range(height):
            r = int(10 + (y/height) * 40)
            g = int(15 + (y/height) * 30)
            b = int(30 + (y/height) * 60)
            draw.line([(0, y), (width, y)], fill=(r, g, b))

        # Noise texture
        for _ in range(2000):
            x = random.randint(0, width-1)
            y = random.randint(0, height-1)
            brightness = random.randint(-10, 10)
            r, g, b = bg.getpixel((x, y))
            bg.putpixel((x, y), (
                max(0, min(255, r + brightness)),
                max(0, min(255, g + brightness)),
                max(0, min(255, b + brightness))
            ))

        # Fonts
        try:
            title_font = ImageFont.truetype("arialbd.ttf", 46)
            name_font = ImageFont.truetype("arialbd.ttf", 32)
            action_font = ImageFont.truetype("arial.ttf", 28)
            info_font = ImageFont.truetype("arial.ttf", 22)
        except:
            title_font = ImageFont.load_default().font_variant(size=28)
            name_font = ImageFont.load_default().font_variant(size=20)
            action_font = ImageFont.load_default().font_variant(size=18)
            info_font = ImageFont.load_default().font_variant(size=16)

        # Header with TikTok theme
        draw.rectangle([0, 0, width, 80], fill=(255, 0, 80))  # TikTok red
        draw.rectangle([0, 75, width, 80], fill=(0, 242, 234))  # TikTok teal
        title_text = "TikTok Downloader • User Activity"
        title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        draw.text(((width - title_width) // 2 + 2, 42), title_text, font=title_font, fill=(0, 0, 0, 128))
        draw.text(((width - title_width) // 2, 40), title_text, font=title_font, fill=(255, 255, 255))

        # Cards
        card_width = 380
        card_height = 280
        card_y = 100
        card_margin = 40
        user_card_x1 = card_margin
        bot_card_x1 = width - card_margin - card_width

        draw.rounded_rectangle([user_card_x1, card_y, user_card_x1 + card_width, card_y + card_height],
                              radius=20, fill=(25, 35, 65, 200), outline=(255, 0, 80), width=3)
        draw.rounded_rectangle([bot_card_x1, card_y, bot_card_x1 + card_width, card_y + card_height],
                              radius=20, fill=(25, 35, 65, 200), outline=(0, 242, 234), width=3)

        # Profile drawer (from your sample)
        def draw_modern_profile(base, img, card_x, card_y, card_width, img_size, display_name, actual_name, is_bot=False):
            profile_x = card_x + (card_width - img_size) // 2
            profile_y = card_y + 40

            # Glow
            glow_size = img_size + 30
            glow = Image.new("RGBA", (glow_size, glow_size), (0, 0, 0, 0))
            glow_draw = ImageDraw.Draw(glow)
            glow_color = (255, 0, 80) if not is_bot else (0, 242, 234)  # TikTok colors
            for i in range(15):
                alpha = int(100 * (1 - i/15))
                color = (*glow_color, alpha)
                glow_draw.ellipse([15-i, 15-i, glow_size-15+i, glow_size-15+i], outline=color, width=2)
            glow = glow.filter(ImageFilter.GaussianBlur(3))
            base.paste(glow, (profile_x-15, profile_y-15), glow)

            # Image + border
            img_resized = img.resize((img_size, img_size))
            mask = Image.new('L', (img_size, img_size), 0)
            ImageDraw.Draw(mask).ellipse((0, 0, img_size, img_size), fill=255)
            img_rgba = img_resized.convert('RGBA')
            img_rgba.putalpha(mask)

            border_color = (255, 0, 80) if not is_bot else (0, 242, 234)  # TikTok colors
            border_img = Image.new('RGBA', (img_size + 8, img_size + 8), (0, 0, 0, 0))
            border_draw = ImageDraw.Draw(border_img)
            border_draw.ellipse((0, 0, img_size + 7, img_size + 7), outline=border_color, width=4)
            border_img.paste(img_rgba, (4, 4), img_rgba)
            base.paste(border_img, (profile_x, profile_y), border_img)

            # Labels
            display_bg = Image.new('RGBA', (card_width - 20, 30), (0, 0, 0, 180))
            d_draw = ImageDraw.Draw(display_bg)
            bbox = d_draw.textbbox((0, 0), display_name, font=info_font)
            w = bbox[2] - bbox[0]
            d_draw.text(((card_width - 20 - w) // 2, 5), display_name, font=info_font, fill=(255, 255, 255))
            base.paste(display_bg, (card_x + 10, profile_y + img_size + 10), display_bg)

            safe_name = (actual_name[:20] + '..') if len(actual_name) > 20 else actual_name
            name_bg = Image.new('RGBA', (card_width - 10, 35), (40, 40, 40, 220))
            n_draw = ImageDraw.Draw(name_bg)
            bbox = n_draw.textbbox((0, 0), safe_name, font=name_font)
            w = bbox[2] - bbox[0]
            n_draw.text(((card_width - 10 - w) // 2, 5), safe_name, font=name_font, fill=(255, 255, 255))
            base.paste(name_bg, (card_x + 5, profile_y + img_size + 45), name_bg)

        # Draw avatars
        profile_size = 120
        draw_modern_profile(bg, user_photo, user_card_x1, card_y, card_width, profile_size, "USER", user_name, False)
        draw_modern_profile(bg, bot_photo, bot_card_x1, card_y, card_width, profile_size, "BOT", bot_name, True)

        # Action
        action_bg = Image.new('RGBA', (width - 100, 60), (255, 0, 80, 200))  # TikTok red
        a_draw = ImageDraw.Draw(action_bg)
        action_text = f"ACTION: {action.upper()}"
        bbox = a_draw.textbbox((0, 0), action_text, font=action_font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        a_draw.text(((width - 100 - w) // 2, (60 - h) // 2 - 5), action_text, font=action_font, fill=(255, 255, 255))
        bg.paste(action_bg, (50, card_y + card_height + 20), action_bg)

        # Footer
        footer_text = f"TikTok Downloader Bot • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        bbox = draw.textbbox((0, 0), footer_text, font=info_font)
        w = bbox[2] - bbox[0]
        draw.text(((width - w) // 2, height - 35), footer_text, font=info_font, fill=(200, 200, 200))

        # Save to bytes
        img_byte_arr = io.BytesIO()
        bg.save(img_byte_arr, format='PNG', quality=95)
        img_byte_arr.seek(0)
        return img_byte_arr

    except Exception as e:
        logger.error(f"❌ Image generation error: {e}")
        return await generate_fallback_image(user_name, action)

async def generate_fallback_image(user_name, action):
    """Simple fallback"""
    try:
        width, height = 800, 400
        bg = Image.new("RGB", (width, height), (255, 0, 80))  # TikTok red
        draw = ImageDraw.Draw(bg)
        title_font = ImageFont.load_default().font_variant(size=24)
        info_font = ImageFont.load_default().font_variant(size=16)
        draw.text((width//2, 100), "🎵 TikTok Downloader Bot", font=title_font, fill="white", anchor="mm")
        draw.text((width//2, 150), f"User: {user_name}", font=info_font, fill="cyan", anchor="mm")
        draw.text((width//2, 180), f"Action: {action}", font=info_font, fill="yellow", anchor="mm")
        draw.text((width//2, 250), "Powered by XP TOOLS", font=info_font, fill="lightgray", anchor="mm")
        img_byte_arr = io.BytesIO()
        bg.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        return img_byte_arr
    except:
        return None

async def send_notification(bot, user_id, username, action):
    """Send notification using generated avatars (NO profile photo download)"""
    try:
        
        if not NOTIFICATION_CHANNEL:
            logger.warning("⚠️ NOTIFICATION_CHANNEL not set, skipping notification")
            return
            
        logger.info(f"📤 Sending notification for user {username} ({user_id}), action: {action}")
        
        bot_info = await bot.get_me()
        bot_name = bot_info.first_name or bot_info.username or "TikTok Bot"
        display_username = username or "Unknown User"

        # USE GENERATED AVATARS (like your sample) - NO PROFILE DOWNLOAD
        image_bytes = await generate_notification_image(
            user_name=display_username,
            bot_name=bot_name,
            user_photo=None,  # Will use generated avatar
            bot_photo=None,   # Will use generated avatar  
            action=action
        )

        if image_bytes:
            keyboard = InlineKeyboardMarkup([[
                InlineKeyboardButton("🎵 Start Bot", url=f"https://t.me/{bot_info.username}"),
                InlineKeyboardButton("👥 Support", url=SUPPORT_GROUP_URL)
            ], [
                InlineKeyboardButton("💻 Source", url=SOURCE_CODE_URL)
            ]])

            caption = f"""🎵 **TikTok Downloader • User Activity**

👤 **User:** @{username or 'Not set'}  
🆔 **User ID:** `{user_id}`  
📥 **Action:** `{action}`  
⏰ **Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
🤖 **Bot:** @{bot_info.username}

━━━━━━━━━━━━━━━━━━━━
**Powered by XP TOOLS** ⚡"""

            await bot.send_photo(
                chat_id=NOTIFICATION_CHANNEL,
                photo=image_bytes,
                caption=caption,
                parse_mode=enums.ParseMode.MARKDOWN,
                reply_markup=keyboard
            )
            cleanup_image(image_bytes)
            logger.success(f"✅ Notification sent successfully for user {username}")
            
    except Exception as e:
        logger.error(f"❌ Error sending notification: {e}")

def cleanup_image(image_bytes):
    if image_bytes:
        image_bytes.close()