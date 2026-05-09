from services import channels_service
from logger import logger
from base import bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from services import ( subjects_service, classes_service)
from models import Class, Topic
from config import BOT_USERNAME


def split_message(text, chunk_size=4096):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

async def is_user_followed_channels(user_id) -> bool:
    try:
        channels = await channels_service.get_all()
        if not channels or len(channels) == 0:
            return True
        
        for channel in channels:
            try:
                member = await bot.get_chat_member(chat_id=channel.username if str(channel.username).startswith("@") else "@" + channel.username, user_id=user_id)

                if member.status in ["left", "kicked"]:
                    return False
            except Exception as e:
                logger.error(f"Error while checking following for channel {channel.username}, exception: {e}")
                continue
        
        return True
    
    except Exception as e:
        logger.error(f"Error in is_user_followd_channels function: {e}")
        return False
    
async def check_user_following(user_id) -> bool:
    try:
        is_user_followed = await is_user_followed_channels(user_id=user_id)
        if is_user_followed: return True

        channels = await channels_service.get_all()
        keyboard = []
        for channel in channels:
            keyboard.append([
                InlineKeyboardButton(
                    text=f"🎊 {channel.username}",
                    url=channel.link
                )]
            )
        
        keyboard.append([
            InlineKeyboardButton(
                text="✅ Tekshirish",
                callback_data="check_subscription"
                # url=f"t.me/{BOT_USERNAME}?start=True"
            )]
        )

        channels_keyboard_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

        await bot.send_message(
            chat_id=user_id,
            text="❌ Iltimos, botdan foydalanish uchun quyidagi kanallarga obuna bo'ling:",
            reply_markup=channels_keyboard_markup
        )

        return False
        
    except Exception as e:
        logger.error(f"Error in check_user_following function: {e}")
        return False
    
async def get_subjects_name():
    subjects = await subjects_service.get_all()
    names = [subject.name for subject in subjects]
    return names

async def get_classes_name():
    classes = await classes_service.get_all()
    names = [_class.name for _class in classes]
    return names

async def get_classes_name_by_classes(classes: list[Class]):
    names = [_class.name for _class in classes]
    return names

async def get_topics_name_by_topics(topics: list[Topic]):
    names = [topic.name for topic in topics]
    return names


async def send_long_message(bot, chat_id, text, parse_mode=None, reply_markup=None):
    max_length = 4000  # a bit less to avoid issues with parse_mode or emojis
    for i in range(0, len(text), max_length):
        await bot.send_message(
            chat_id=chat_id,
            text=text[i:i+max_length],
            parse_mode=parse_mode,
            reply_markup=reply_markup if i + max_length >= len(text) else None  # only send keyboard with the last part
        )

def split_message(text: str, max_length: int = 4000) -> list[str]:
    """
    Splits a long text into chunks that fit within Telegram's message length limit,
    trying to split at line breaks to avoid cutting sentences mid-way.
    """
    lines = text.split('\n')
    chunks = []
    current_chunk = ""

    for line in lines:
        # +1 for the newline character
        if len(current_chunk) + len(line) + 1 <= max_length:
            current_chunk += line + '\n'
        else:
            chunks.append(current_chunk.strip())
            current_chunk = line + '\n'

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks
