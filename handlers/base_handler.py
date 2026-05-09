from aiogram import Router, F
from aiogram.types import *
from logger import logger
import const
from aiogram.fsm.context import FSMContext
import keyboards
from config import ADMIN_ID
from base import bot
import functions as fn
from services import user_service
from models import User
from datetime import datetime, timezone, timedelta

router = Router()

@router.message(F.text == "⬅️ Bekor qilish")
async def cancel(message: Message, state: FSMContext):
    try:
        if state:
            await state.clear()

        await message.answer("Bekor qilindi✅", reply_markup=keyboards.main_menu)

    except Exception as e:
        logger.error(f"Error in cancel: {e}")
        await message.answer(const.ERROR_MSG)

@router.callback_query(F.data == "cancel_inline")
async def cancel_inline(callback: CallbackQuery, state: FSMContext):
    try:
        if state:
            await state.clear()

        await callback.message.edit_text("Bekor qilindi✅")
    except Exception as e:
        logger.error(f"Error in cancel_inline: {e}")
        await callback.answer("Bekor qilishda xatolik yuz berdi.", show_alert=True)

    
@router.message(F.text == "⬅️ Admin panel")
async def cancel(message: Message, state: FSMContext):
    try:
        user_id = message.from_user.id
        if user_id != ADMIN_ID: return

        if state:
            await state.clear()

        await message.answer("Admin paneldasiz✅", reply_markup=keyboards.admin_menu)

    except Exception as e:
        logger.error(f"Error in cancel: {e}")
        await message.answer(const.ERROR_MSG)

@router.message(F.text == "⬅️ Asosiy menyu")
async def cancel(message: Message, state: FSMContext):
    try:
        if state:
            await state.clear()

        await message.answer("Siz asosiy menyuga qaytdingiz✅", reply_markup=keyboards.main_menu)

    except Exception as e:
        logger.error(f"Error in cancel: {e}")
        await message.answer(const.ERROR_MSG)


@router.callback_query(F.data == "check_subscription")
async def check_subs(callback: CallbackQuery):
    try:
        user_id = callback.from_user.id
        result = await fn.is_user_followed_channels(user_id=user_id)
        if result:
            await bot.send_message(callback.from_user.id, "Ajoyib, siz kanallarga obuna bo'lgansiz ✅", reply_markup=keyboards.main_menu)
            await callback.message.delete()

            exist_user = await user_service.get_by_id(user_id)
            if not exist_user:
                now = datetime.now(timezone.utc)
                new_expiry = now + timedelta(days=30)
                new_user = User(
                    id=user_id,
                    first_name=callback.from_user.first_name,
                    last_name=callback.from_user.last_name,
                    username=callback.from_user.username,
                    is_premium=True,
                    premium_expiry_at=new_expiry
                )
                await user_service.create(new_user)
        else:
            await bot.send_message(callback.from_user.id, "Afsuski, siz hali barcha kanallarga obuna bo'lmagansiz ❌")
            await callback.answer()

    except Exception as e:
        logger.error(f"Error in check_subs: {e}")
        await bot.send_message(callback.from_user.id, const.ERROR_MSG)