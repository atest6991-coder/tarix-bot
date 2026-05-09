from aiogram import Router, F
from aiogram.types import *
import const
from logger import logger
from config import ADMIN_ID
import keyboards
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from services import (
    channels_service,
    subjects_service,
    classes_service,
    topics_service,
    video_lessons_service,
    audio_lessons_service,
    pdf_materials_service,
    tests_service,
    test_options_service,
    fill_blanks_tests_service,
    fill_blanks_test_answers_service,
    user_service
)
from models import (
    Channel, 
    Subject, 
    Class, 
    Topic, 
    VideoLesson,
    AudioLesson,
    PDFMaterial,
    Test,
    TestOption,
    FillBlanksTest,
    FillBlanksTestAnswer,
    User
)
import test_parser 
import os
from base import bot
import uuid
import asyncio
from datetime import datetime, timezone, timedelta


router = Router()

@router.message(F.text == "/admin")
async def show_admin_menu(message: Message):
    try:
        user_id = message.from_user.id
        if user_id != ADMIN_ID:
            return
        
        await message.answer("Admin, xush kelibsiz ⚡️", reply_markup=keyboards.admin_menu)
    except Exception as e:
        await message.reply(const.ERROR_MSG)
        logger.error(f"ERROR in show_admin_menu: {e}")

# Channels list
@router.message(F.text == "📝 Kanallar")
async def show_channels(message: Message):
    try:
        channels = await channels_service.get_all()
        if not channels or len(channels) == 0:
            await message.answer("Sizda kanallar topilmadi.")
            return
        
        result = "📝 Kanallar:\n"
        for channel in channels:
            result += "@" + channel.username + "\n"
        await message.answer(result, reply_markup=keyboards.admin_menu)

    except Exception as e:
        logger.error(f"Error in show_channels: {e}")
        await message.answer(const.ERROR_MSG)


# Add channel
class AddChannelStates(StatesGroup):
    username = State()
    link = State()

@router.message(F.text == "➕ Kanal qo'shish")
async def add_channel(message: Message, state: FSMContext):
    try:
        user_id = message.from_user.id
        if user_id != ADMIN_ID: return

        await state.set_state(AddChannelStates.username)
        await message.answer("Kanalingiz username 'ini yuboring, (masalan: @csharpchi)", reply_markup=keyboards.back)
    except Exception as e:
        logger.error(f"Error in add_channel: {e}")
        await message.answer(const.ERROR_MSG)

@router.message(AddChannelStates.username)
async def ask_link(message: Message, state: FSMContext):
    try:
        channel_username = message.text.strip()
        if channel_username.startswith("@"):
            channel_username = channel_username.replace("@", "")
        
        await state.update_data(username=channel_username)
        await state.set_state(AddChannelStates.link)
        await message.answer("Kanalingiz username 'ini yuboring, (masalan: https://t.me/csharpchi)", reply_markup=keyboards.back)
        
    except Exception as e:
        logger.error(f"Error in ask_link: {e}")
        await message.answer(const.ERROR_MSG)

@router.message(AddChannelStates.link)
async def save_channel(message: Message, state: FSMContext):
    try:
        channel_link = message.text.strip()
        if not channel_link.startswith("https://t.me/"):
            await message.answer("Noto'g'ri formatda yubordingiz, qaytadan urunib ko'ring.")
            return
        
        data = await state.get_data()
        await state.clear()
        channel_username = data['username']

        new_channel = Channel(
            username=channel_username,
            link=channel_link
        )
        await channels_service.create(new_channel)
        await message.answer("Yangi kanal qo'shildi ✅", reply_markup=keyboards.admin_menu)

    except Exception as e:
        logger.error(f"Error in save_channel: {e}")
        await message.answer(const.ERROR_MSG)


# Delete channel
@router.message(F.text == "➖ Kanal o'chirish")
async def handle_delete_channel_request(message: Message):
    try:
        user_id = message.from_user.id
        if user_id != ADMIN_ID: return
        
        channels = await channels_service.get_all()
        if not channels:
            await message.answer("⚠️ Kanallar topilmadi.")
            return
        
        await message.answer(
            "❌ O'chirib tashlamoqchi bo'lgan kanalingizni tanlang:",
            reply_markup=keyboards.channels_inline_keyboard(channels=channels)
        )
    except Exception as e:
        logger.error(f"Error in handle_delete_channel_request: {e}")
        await message.answer(const.ERROR_MSG)

@router.callback_query(F.data.startswith("delete_channel:"))
async def handle_channel_selected(callback: CallbackQuery):
    try:
        channel_id = int(callback.data.split(":")[1])
        channel = await channels_service.get_by_id(channel_id)
        if not channel:
            await callback.answer("🚫 Kanal topilmadi", show_alert=True)
            return
        
        await callback.message.edit_text(
            f"⚠️ Xaqiqatda shu kanalni o'chirmoqchimisiz: <b>{channel.username}</b>",
            reply_markup=keyboards.confirm_delete_keyboard(channel_id=channel_id),
            parse_mode="HTML"
        )

    except Exception as e:
        logger.error(f"Error in handle_channel_selected: {e}")
        await callback.answer(const.ERROR_MSG, show_alert=True)

@router.callback_query(F.data.startswith("confirm_delete_channel:"))
async def confirm_delete(callback: CallbackQuery):
    try:
        channel_id = int(callback.data.split(":")[1])
        await channels_service.delete_by_id(channel_id)
        await callback.message.edit_text("✅ Kanal muvaffaqiyatli o'chirildi.")
    except Exception as e:
        logger.error(f"Error in handle_channel_selected: {e}")
        await callback.answer(const.ERROR_MSG, show_alert=True)

@router.callback_query(F.data == "cancel_delete")
async def cancel_delete(callback: CallbackQuery):
    try:
        await callback.message.edit_text("❌ Bekor qilindi.")
    except Exception as e:
        logger.error(f"Error in handle_channel_selected: {e}")
        await callback.answer(const.ERROR_MSG, show_alert=True)

# Fanlar
class AddSubjectStates(StatesGroup):
    name = State()

# Show subjects
@router.message(F.text == "📝 Fanlar")
async def show_subjects(message: Message):
    try:
        subjects = await subjects_service.get_all()
        if not subjects:
            await message.answer("📂 Fanlar topilmadi.")
            return

        text = "📚 Fanlar ro'yxati:\n"
        for subject in subjects:
            text += f"✅ {subject.name}\n"
        await message.answer(text, reply_markup=keyboards.admin_menu)
    except Exception as e:
        logger.error(f"Error in show_subjects: {e}")
        await message.answer(const.ERROR_MSG)

# Add subject start
@router.message(F.text == "➕ Fan qo'shish")
async def add_subject(message: Message, state: FSMContext):
    try:
        if message.from_user.id != ADMIN_ID: return
        await state.set_state(AddSubjectStates.name)
        await message.answer("📚 Fan nomini yuboring:", reply_markup=keyboards.back)
    except Exception as e:
        logger.error(f"Error in add_subject: {e}")
        await message.answer(const.ERROR_MSG)

# Save subject
@router.message(AddSubjectStates.name)
async def save_subject(message: Message, state: FSMContext):
    try:
        name = message.text.strip()
        await state.clear()

        new_subject = Subject(
            id=None,
            name=name
        )
        await subjects_service.create(new_subject)
        await message.answer(f"✅ Fan '{name}' qo'shildi.", reply_markup=keyboards.admin_menu)
    except Exception as e:
        logger.error(f"Error in save_subject: {e}")
        await message.answer(const.ERROR_MSG)

# Delete subject - list
@router.message(F.text == "➖ Fan o'chirish")
async def handle_delete_subject_request(message: Message):
    try:
        if message.from_user.id != ADMIN_ID: return
        subjects = await subjects_service.get_all()
        if not subjects:
            await message.answer("⚠️ Fanlar topilmadi.")
            return

        await message.answer(
            "🗑️ O'chirmoqchi bo'lgan faningizni tanlang:",
            reply_markup=keyboards.subjects_inline_keyboard(subjects, prefix="delete_subject")
        )
    except Exception as e:
        logger.error(f"Error in handle_delete_subject_request: {e}")
        await message.answer(const.ERROR_MSG)

# Confirm subject deletion
@router.callback_query(F.data.startswith("delete_subject:"))
async def handle_subject_selected(callback: CallbackQuery):
    try:
        subject_id = int(callback.data.split(":")[1])
        subject = await subjects_service.get_by_id(subject_id)
        
        if not subject:
            await callback.answer("🚫 Fan topilmadi", show_alert=True)
            return
        
        await callback.message.edit_text(
            f"⚠️ Haqiqatdan ham shu fan '{subject.name}' ni o'chirmoqchimisiz?",
            reply_markup=keyboards.confirm_delete_subject_keyboard(subject_id)
        )
    except Exception as e:
        logger.error(f"Error in handle_subject_selected: {e}")
        await callback.answer(const.ERROR_MSG, show_alert=True)

@router.callback_query(F.data.startswith("confirm_delete_subject:"))
async def confirm_delete_subject(callback: CallbackQuery):
    try:
        subject_id = int(callback.data.split(":")[1])
        await subjects_service.delete_by_id(subject_id)
        await callback.message.edit_text("✅ Fan muvaffaqiyatli o'chirildi.")
    except Exception as e:
        logger.error(f"Error in confirm_delete_subject: {e}")
        await callback.answer(const.ERROR_MSG, show_alert=True)

@router.callback_query(F.data == "cancel_delete_subject")
async def cancel_delete_subject(callback: CallbackQuery):
    try:
        await callback.message.edit_text("❌ O'chirish bekor qilindi.")
    except Exception as e:
        logger.error(f"Error in cancel_delete_subject: {e}")
        await callback.answer(const.ERROR_MSG, show_alert=True)


# Add Class FSM
class AddClassStates(StatesGroup):
    subject = State()
    name = State()

# Show Classes
@router.message(F.text == "📝 Sinflar")
async def ask_subject_for_classes(message: Message, state: FSMContext):
    try:
        subjects = await subjects_service.get_all()
        if not subjects:
            await message.answer("❌ Avval fanlar qo'shing.")
            return

        await message.answer(
            "📚 Qaysi fan bo'yicha sinflarni ko'rmoqchisiz?",
            reply_markup=keyboards.subjects_inline_keyboard(subjects, prefix="view_classes_subject")
        )

    except Exception as e:
        logger.error(f"Error in ask_subject_for_classes: {e}")
        await message.answer(const.ERROR_MSG)

# Show Classes by Selected Subject
@router.callback_query(F.data.startswith("view_classes_subject:"))
async def show_classes_by_subject(callback: CallbackQuery):
    try:
        subject_id = int(callback.data.split(":")[1])
        classes = await classes_service.get_by_subject_id(subject_id)

        if not classes:
            await callback.message.edit_text("⚠️ Bu fan uchun hech qanday sinf topilmadi.")
            return

        subject = await subjects_service.get_by_id(subject_id)
        result = f"📚 <b>{subject.name}</b> faniga tegishli sinflar:\n\n"
        for cls in classes:
            result += f"{cls.id}. {cls.name}\n"

        await callback.message.delete()
        await bot.send_message(callback.from_user.id, result, reply_markup=keyboards.admin_menu, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Error in show_classes_by_subject: {e}")
        await callback.answer(const.ERROR_MSG, show_alert=True)

# Add Class
@router.message(F.text == "➕ Sinf qo'shish")
async def add_class(message: Message, state: FSMContext):
    try:
        subjects = await subjects_service.get_all()
        if not subjects:
            await message.answer("❌ Avval fan qo'shing.")
            return

        await state.set_state(AddClassStates.subject)
        await message.answer(
            "Fan tanlang:",
            reply_markup=keyboards.subjects_inline_keyboard(subjects)
        )
    except Exception as e:
        logger.error(f"Error in add_class: {e}")
        await message.answer(const.ERROR_MSG)

@router.callback_query(F.data.startswith("subject_select:"))
async def subject_selected(callback: CallbackQuery, state: FSMContext):
    try:
        subject_id = int(callback.data.split(":")[1])
        await state.update_data(subject_id=subject_id)
        await state.set_state(AddClassStates.name)
        await callback.message.edit_text("✏️ Yangi sinf nomini kiriting:")
    except Exception as e:
        logger.error(f"Error in subject_selected: {e}")
        await callback.answer(const.ERROR_MSG, show_alert=True)

@router.message(AddClassStates.name)
async def save_class(message: Message, state: FSMContext):
    try:
        data = await state.get_data()
        subject_id = data.get("subject_id")
        class_name = message.text.strip()

        await classes_service.create(Class(name=class_name, subject_id=subject_id))
        await state.clear()
        await message.answer("✅ Yangi sinf qo'shildi!", reply_markup=keyboards.admin_menu)
    except Exception as e:
        logger.error(f"Error in save_class: {e}")
        await message.answer(const.ERROR_MSG)

# Delete Class
@router.message(F.text == "➖ Sinf o'chirish")
async def handle_delete_class_request(message: Message):
    try:
        classes = await classes_service.get_all()
        if not classes:
            await message.answer("⚠️ Sinflar topilmadi.")
            return

        subjects = await subjects_service.get_all()

        await message.answer(
            "Fan tanlang:",
            reply_markup=keyboards.subjects_inline_keyboard(subjects=subjects, prefix="subject_for_class_delete")
        )

    except Exception as e:
        logger.error(f"Error in handle_delete_class_request: {e}")
        await message.answer(const.ERROR_MSG)

@router.callback_query(F.data.startswith("subject_for_class_delete:"))
async def handle_subject_select(callback: CallbackQuery):
    try:
        subject_id = int(callback.data.split(":")[1])
        classes = await classes_service.get_by_subject_id(subject_id=subject_id)
        if not classes:
            await callback.answer("⚠️ Bu fanga tegishli sinflar topilmadi.", show_alert=True)
            return
        
        await callback.message.edit_text(
            "O'chirmoqchi bo'lgan sinfingizni tanlang",
            reply_markup=keyboards.classes_inline_keyboard(classes=classes)
        )
    except Exception as e:
        logger.error(f"Error in handle_subject_select: {e}")
        await callback.answer(const.ERROR_MSG, show_alert=True)

@router.callback_query(F.data.startswith("delete_class:"))
async def handle_class_selected(callback: CallbackQuery):
    try:
        class_id = int(callback.data.split(":")[1])
        cls = await classes_service.get_by_id(class_id)
        if not cls:
            await callback.answer("🚫 Sinf topilmadi.", show_alert=True)
            return

        await callback.message.edit_text(
            f"⚠️ Haqiqatdan ham shu sinfni o'chirmoqchimisiz: <b>{cls.name}</b>?",
            reply_markup=keyboards.confirm_delete_class_keyboard(class_id),
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Error in handle_class_selected: {e}")
        await callback.answer(const.ERROR_MSG, show_alert=True)

@router.callback_query(F.data.startswith("confirm_delete_class:"))
async def confirm_delete_class(callback: CallbackQuery):
    try:
        class_id = int(callback.data.split(":")[1])
        await classes_service.delete_by_id(class_id)
        await callback.message.edit_text("✅ Sinf muvaffaqiyatli o'chirildi.")
    except Exception as e:
        logger.error(f"Error in confirm_delete_class: {e}")
        await callback.answer(const.ERROR_MSG, show_alert=True)

@router.callback_query(F.data == "cancel_delete_class")
async def cancel_delete_class(callback: CallbackQuery):
    try:
        await callback.message.edit_text("❌ Bekor qilindi.")
    except Exception as e:
        logger.error(f"Error in cancel_delete_class: {e}")
        await callback.answer(const.ERROR_MSG, show_alert=True)

# ------------------------
# topic handlers
# ------------------------

# Add Topic States
class AddTopicStates(StatesGroup):
    subject = State()
    class_ = State()
    name = State()

# Add Topic: Step 1 - Ask subject
@router.message(F.text == "➕ Mavzu qo'shish")
async def add_topic(message: Message, state: FSMContext):
    try:
        subjects = await subjects_service.get_all()
        if not subjects:
            await message.answer("❌ Avval fan qo'shing.")
            return

        await state.set_state(AddTopicStates.subject)
        await message.answer(
            "Fan tanlang:",
            reply_markup=keyboards.subjects_inline_keyboard(subjects, prefix="subject_for_topic_add")
        )
    except Exception as e:
        logger.error(f"Error in add_topic: {e}")
        await message.answer(const.ERROR_MSG)

# Add Topic: Step 2 - Select subject → show classes
@router.callback_query(F.data.startswith("subject_for_topic_add:"))
async def add_topic_select_subject(callback: CallbackQuery, state: FSMContext):
    try:
        subject_id = int(callback.data.split(":")[1])
        classes = await classes_service.get_by_subject_id(subject_id)
        if not classes:
            await callback.answer("⚠️ Bu fanga sinflar topilmadi.", show_alert=True)
            return

        await state.update_data(subject_id=subject_id)
        await state.set_state(AddTopicStates.class_)
        await callback.message.edit_text(
            "📚 Sinfni tanlang:",
            reply_markup=keyboards.classes_inline_keyboard(classes, prefix="class_for_topic_add")
        )
    except Exception as e:
        logger.error(f"Error in add_topic_select_subject: {e}")
        await callback.answer(const.ERROR_MSG, show_alert=True)

# Add Topic: Step 3 - Select class → ask name
@router.callback_query(F.data.startswith("class_for_topic_add:"))
async def add_topic_select_class(callback: CallbackQuery, state: FSMContext):
    try:
        class_id = int(callback.data.split(":")[1])
        await state.update_data(class_id=class_id)
        await state.set_state(AddTopicStates.name)
        await callback.message.edit_text("✏️ Mavzu nomini yuboring:")
    except Exception as e:
        logger.error(f"Error in add_topic_select_class: {e}")
        await callback.answer(const.ERROR_MSG, show_alert=True)

# Add Topic: Step 4 - Save
@router.message(AddTopicStates.name)
async def add_topic_save(message: Message, state: FSMContext):
    try:
        data = await state.get_data()
        class_id = data.get("class_id")
        topic_name = message.text.strip()

        await topics_service.create(Topic(name=topic_name, class_id=class_id))
        await state.clear()
        await message.answer("✅ Yangi mavzu qo'shildi!", reply_markup=keyboards.admin_menu)
    except Exception as e:
        logger.error(f"Error in add_topic_save: {e}")
        await message.answer(const.ERROR_MSG)


# Delete Topic
@router.message(F.text == "➖ Mavzu o'chirish")
async def delete_topic_start(message: Message):
    try:
        subjects = await subjects_service.get_all()
        if not subjects:
            await message.answer("❌ Avval fan qo'shing.")
            return

        await message.answer(
            "Fan tanlang:",
            reply_markup=keyboards.subjects_inline_keyboard(subjects, prefix="subject_for_topic_delete")
        )
    except Exception as e:
        logger.error(f"Error in delete_topic_start: {e}")
        await message.answer(const.ERROR_MSG)

# Delete Topic: Select subject → show classes
@router.callback_query(F.data.startswith("subject_for_topic_delete:"))
async def delete_topic_select_subject(callback: CallbackQuery):
    try:
        subject_id = int(callback.data.split(":")[1])
        classes = await classes_service.get_by_subject_id(subject_id)
        if not classes:
            await callback.answer("⚠️ Bu fanga sinflar topilmadi.", show_alert=True)
            return

        await callback.message.edit_text(
            "📚 Sinfni tanlang:",
            reply_markup=keyboards.classes_inline_keyboard(classes, prefix="class_for_topic_delete")
        )
    except Exception as e:
        logger.error(f"Error in delete_topic_select_subject: {e}")
        await callback.answer(const.ERROR_MSG, show_alert=True)

# Delete Topic: Select class → show topics
@router.callback_query(F.data.startswith("class_for_topic_delete:"))
async def delete_topic_select_class(callback: CallbackQuery):
    try:
        class_id = int(callback.data.split(":")[1])
        topics = await topics_service.get_by_class_id(class_id)
        if not topics:
            await callback.answer("⚠️ Bu sinfga tegishli mavzular topilmadi.", show_alert=True)
            return

        await callback.message.edit_text(
            "❌ O'chirmoqchi bo'lgan mavzuni tanlang:",
            reply_markup=keyboards.topics_inline_keyboard(topics, prefix="delete_topic")
        )
    except Exception as e:
        logger.error(f"Error in delete_topic_select_class: {e}")
        await callback.answer(const.ERROR_MSG, show_alert=True)

# Delete Topic: Confirm deletion
@router.callback_query(F.data.startswith("delete_topic:"))
async def delete_topic_confirm(callback: CallbackQuery):
    try:
        topic_id = int(callback.data.split(":")[1])
        topic = await topics_service.get_by_id(topic_id)
        if not topic:
            await callback.answer("🚫 Mavzu topilmadi.", show_alert=True)
            return

        await callback.message.edit_text(
            f"⚠️ Haqiqatdan ham shu mavzuni o'chirmoqchimisiz: <b>{topic.name}</b>?",
            reply_markup=keyboards.confirm_delete_topic_keyboard(topic_id),
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Error in delete_topic_confirm: {e}")
        await callback.answer(const.ERROR_MSG, show_alert=True)

@router.callback_query(F.data.startswith("confirm_delete_topic:"))
async def delete_topic_execute(callback: CallbackQuery):
    try:
        topic_id = int(callback.data.split(":")[1])
        await topics_service.delete_by_id(topic_id)
        await callback.message.edit_text("✅ Mavzu muvaffaqiyatli o'chirildi.")
    except Exception as e:
        logger.error(f"Error in delete_topic_execute: {e}")
        await callback.answer(const.ERROR_MSG, show_alert=True)

@router.callback_query(F.data == "cancel_delete_topic")
async def delete_topic_cancel(callback: CallbackQuery):
    try:
        await callback.message.edit_text("❌ Bekor qilindi.")
    except Exception as e:
        logger.error(f"Error in delete_topic_cancel: {e}")
        await callback.answer(const.ERROR_MSG, show_alert=True)


# Show Topics
@router.message(F.text == "📝 Mavzular")
async def show_topics_start(message: Message):
    try:
        subjects = await subjects_service.get_all()
        if not subjects:
            await message.answer("❌ Avval fan qo'shing.")
            return

        await message.answer(
            "📚 Qaysi fan bo'yicha mavzularni ko'rmoqchisiz?",
            reply_markup=keyboards.subjects_inline_keyboard(subjects, prefix="subject_for_topic_list")
        )
    except Exception as e:
        logger.error(f"Error in show_topics_start: {e}")
        await message.answer(const.ERROR_MSG)

# Step 2 - Select Subject → Show classes
@router.callback_query(F.data.startswith("subject_for_topic_list:"))
async def show_topics_select_subject(callback: CallbackQuery):
    try:
        subject_id = int(callback.data.split(":")[1])
        classes = await classes_service.get_by_subject_id(subject_id)
        if not classes:
            await callback.answer("⚠️ Bu fanga sinflar topilmadi.", show_alert=True)
            return

        await callback.message.edit_text(
            "📚 Sinfni tanlang:",
            reply_markup=keyboards.classes_inline_keyboard(classes, prefix="class_for_topic_list")
        )
    except Exception as e:
        logger.error(f"Error in show_topics_select_subject: {e}")
        await callback.answer(const.ERROR_MSG, show_alert=True)

# Step 3 - Select Class → Show Topics
@router.callback_query(F.data.startswith("class_for_topic_list:"))
async def show_topics_by_class(callback: CallbackQuery):
    try:
        class_id = int(callback.data.split(":")[1])
        topics = await topics_service.get_by_class_id(class_id)

        if not topics:
            await callback.message.edit_text("⚠️ Bu sinfga tegishli mavzular topilmadi.")
            return

        cls = await classes_service.get_by_id(class_id)
        subject = await subjects_service.get_by_id(cls.subject_id)

        result = f"📚 <b>{subject.name}</b> fanining <b>{cls.name}</b> sinfi uchun mavzular:\n\n"
        for topic in topics:
            result += f"{topic.id}. {topic.name}\n"

        await callback.message.delete()
        await bot.send_message(callback.from_user.id, result, reply_markup=keyboards.admin_menu, parse_mode="HTML")

    except Exception as e:
        logger.error(f"Error in show_topics_by_class: {e}")
        await callback.answer(const.ERROR_MSG, show_alert=True)

# ------------------------
# video_lessons handlers
# ------------------------

@router.message(F.text == "➕ Video qo'shish")
async def add_video_handler(message: Message):
    try:
        user_id = message.from_user.id
        if user_id != ADMIN_ID: return

        subjects = await subjects_service.get_all()
        if not subjects or len(subjects) == 0:
            await message.answer("⚠️Hali birorta fan qo'shilmagan")
            return
        
        await message.answer("Fanni tanlang", reply_markup=keyboards.subjects_inline_keyboard(subjects=subjects, prefix="subject_for_video_add"))
    except Exception as e:
        logger.error(f"Error in add_video_handler: {e}")
        await message.answer(const.ERROR_MSG)

@router.callback_query(F.data.startswith("subject_for_video_add:"))
async def handle_subject_select_for_video_add(callback: CallbackQuery):
    try:
        subject_id = int(callback.data.split(":")[1])
        subject = await subjects_service.get_by_id(subject_id)
        if not subject:
            await callback.answer("Fan topilmadi!", show_alert=True)
            return
        
        classes = await classes_service.get_by_subject_id(subject_id=subject_id)
        if not classes or len(classes) == 0:
            await callback.answer("Bu fan uchun sinflar topilmadi!", show_alert=True)
            await callback.message.delete()
            return
        
        await callback.message.edit_text(
            "Sinf tanlang:",
            reply_markup=keyboards.classes_inline_keyboard(classes=classes, prefix="class_for_video_add"))
        
    except Exception as e:
        logger.error(f"Error in handle_subject_select_for_video_add: {e}")
        await callback.answer(const.ERROR_MSG, show_alert=True)
        await callback.message.delete()

@router.callback_query(F.data.startswith("class_for_video_add:"))
async def handle_class_select_for_video_add(callback: CallbackQuery):
    try:
        class_id = int(callback.data.split(":")[1])
        _class = await classes_service.get_by_id(class_id)
        if not _class:
            await callback.answer("Sinf topilmadi!", show_alert=True)
            return
        
        topics = await topics_service.get_by_class_id(class_id=class_id)
        if not topics or len(topics) == 0:
            await callback.answer("Bu sinf uchun mavzular topilmadi!", show_alert=True)
            return
        
        await callback.message.edit_text(
            "Mavzu tanlang:",
            reply_markup=keyboards.topics_inline_keyboard(topics=topics, prefix="topic_for_video_add")
        )
    except Exception as e:
        logger.error(f"Error in hanele_class_select_for_video_add: {e}")
        await callback.answer(const.ERROR_MSG, show_alert=True)
        await callback.message.delete()

class AddVideoStates(StatesGroup):
    video = State()

@router.callback_query(F.data.startswith("topic_for_video_add"))
async def handle_topic_select_for_video_add(callback: CallbackQuery, state: FSMContext):
    try:
        topic_id = int(callback.data.split(":")[1])
        topic = await topics_service.get_by_id(topic_id)
        if not topic:
            await callback.answer("Mavzu topilmadi!", show_alert=True)
            return
        
        exist_video = await video_lessons_service.get_by_topic_id(topic_id=topic_id)
        if exist_video:
            await callback.answer("Bu mavzu uchun video biriktirilgan!", show_alert=True)
            return
        
        await state.update_data(topic_id=topic_id)
        await state.set_state(AddVideoStates.video)
        await callback.message.edit_text(
            f"<b>{topic.name}</b>\n\nUshbu mavzu uchun video yuboring:", 
            reply_markup=keyboards.cancel_inline,
            parse_mode="HTML")
    except Exception as e:
        logger.error(f"Error in handle_topic_select_for_video_add: {e}")
        await callback.answer(const.ERROR_MSG, show_alert=True)
        await callback.message.delete()

@router.message(AddVideoStates.video, F.video)
async def handle_video(message: Message, state: FSMContext):
    try:
        if not message.video:
            await message.answer("Iltimos, faqat video yuboring!")
            return
        
        data = await state.get_data()
        topic_id = data['topic_id']
        video = message.video
        file_id = video.file_id

        video_lesson = VideoLesson(
            file_id=file_id,
            topic_id=topic_id
        )
        await video_lessons_service.create(video_lesson)
        await state.clear()
        await message.answer("Video yuklandi✅", reply_markup=keyboards.admin_menu)

    except Exception as e:
        logger.error(f"Error in handle_video: {e}")
        await message.answer(const.ERROR_MSG)

# Video lesson o'chirish
@router.message(F.text == "➖ Video o'chirish")
async def delete_video_handler(message: Message):
    try:
        user_id = message.from_user.id
        if user_id != ADMIN_ID: return

        subjects = await subjects_service.get_all()
        if not subjects or len(subjects) == 0:
            await message.answer("⚠️Hali birorta fan qo'shilmagan")
            return
        
        await message.answer(
            "Fanni tanlang", 
            reply_markup=keyboards.subjects_inline_keyboard(
            subjects=subjects, 
            prefix="subject_for_video_delete"))
    except Exception as e:
        logger.error(f"Error in delete_video_handler: {e}")
        await message.answer(const.ERROR_MSG)

@router.callback_query(F.data.startswith("subject_for_video_delete:"))
async def handle_subject_select_for_video_delete(callback: CallbackQuery):
    try:
        subject_id = int(callback.data.split(":")[1])
        subject = await subjects_service.get_by_id(subject_id)
        if not subject:
            await callback.answer("Fan topilmadi!", show_alert=True)
            return
        
        classes = await classes_service.get_by_subject_id(subject_id=subject_id)
        if not classes or len(classes) == 0:
            await callback.answer("Bu fan uchun sinflar topilmadi!", show_alert=True)
            await callback.message.delete()
            return
        
        await callback.message.edit_text(
            "Sinf tanlang:",
            reply_markup=keyboards.classes_inline_keyboard(classes=classes, prefix="class_for_video_delete"))
        
    except Exception as e:
        logger.error(f"Error in handle_subject_select_for_video_delete: {e}")
        await callback.answer(const.ERROR_MSG, show_alert=True)
        await callback.message.delete()

@router.callback_query(F.data.startswith("class_for_video_delete:"))
async def handle_class_select_for_video_delete(callback: CallbackQuery):
    try:
        class_id = int(callback.data.split(":")[1])
        _class = await classes_service.get_by_id(class_id)
        if not _class:
            await callback.answer("Sinf topilmadi!", show_alert=True)
            return
        
        topics = await topics_service.get_by_class_id(class_id=class_id)
        if not topics or len(topics) == 0:
            await callback.answer("Bu sinf uchun mavzular topilmadi!", show_alert=True)
            return
        
        await callback.message.edit_text(
            "Mavzu tanlang:",
            reply_markup=keyboards.topics_inline_keyboard(topics=topics, prefix="topic_for_video_delete")
        )
    except Exception as e:
        logger.error(f"Error in handle_class_select_for_video_delete: {e}")
        await callback.answer(const.ERROR_MSG, show_alert=True)
        await callback.message.delete()

@router.callback_query(F.data.startswith("topic_for_video_delete"))
async def handle_topic_select_for_video_delete(callback: CallbackQuery):
    try:
        topic_id = int(callback.data.split(":")[1])
        topic = await topics_service.get_by_id(topic_id)
        if not topic:
            await callback.answer("Mavzu topilmadi!", show_alert=True)
            return
        
        exist_video = await video_lessons_service.get_by_topic_id(topic_id=topic_id)
        if not exist_video:
            await callback.answer("Bu mavzu uchun video biriktirilmagan!", show_alert=True)
            return
        
        await callback.message.edit_text(
            "Haqiqatdan ham bu mavzu uchun biriktirilgan videoni o'chirmoqchimisiz?",
            reply_markup=keyboards.yes_no_inline_keyboard(f"confirm_delete_video:{exist_video.id}", "cancel_delete_video"))
        
    except Exception as e:
        logger.error(f"Error in handle_topic_select_for_video_delete: {e}")
        await callback.answer(const.ERROR_MSG, show_alert=True)
        await callback.message.delete()

@router.callback_query(F.data.startswith("confirm_delete_video:"))
async def confirm_delete_video(callback: CallbackQuery):
    try:
        video_lesson_id = int(callback.data.split(":")[1])
        video_lesson = await video_lessons_service.get_by_id(video_lesson_id)
        if not video_lesson:
            await callback.answer("Video topilmadi!", show_alert=True)
            return
        
        await video_lessons_service.delete_by_id(video_lesson_id)
        await callback.message.edit_text("Video o'chirildi ✅")
        return
    
    except Exception as e:
        logger.error(f"Error in confirm_delete_video: {e}")
        await callback.answer(const.ERROR_MSG, show_alert=True)
        await callback.message.delete()

@router.callback_query(F.data == "cancel_delete_video")
async def cancel_delete_video(callback: CallbackQuery):
    try:
        callback.answer("Bekor qilindi...", show_alert=True)
        await callback.message.delete()
    except Exception as e:
        logger.error(f"Error in cancel_delete_video: {e}")
        await callback.answer(const.ERROR_MSG, show_alert=True)
        await callback.message.delete()

# Video ko'rish
@router.message(F.text == "📝 Video ko'rish")
async def handle_show_video(message: Message):
    try:
        user_id = message.from_user.id
        if user_id != ADMIN_ID: return

        subjects = await subjects_service.get_all()
        if not subjects or len(subjects) == 0:
            await message.answer("⚠️Hali birorta fan qo'shilmagan")
            return
        
        await message.answer(
            "Fanni tanlang", 
            reply_markup=keyboards.subjects_inline_keyboard(
            subjects=subjects, 
            prefix="subject_for_video_view"))
    except Exception as e:
        logger.error(f"Error in handle_show_video: {e}")
        await message.answer(const.ERROR_MSG)


@router.callback_query(F.data.startswith("subject_for_video_view:"))
async def handle_subject_select_for_video_view(callback: CallbackQuery):
    try:
        subject_id = int(callback.data.split(":")[1])
        subject = await subjects_service.get_by_id(subject_id)
        if not subject:
            await callback.answer("Fan topilmadi!", show_alert=True)
            return
        
        classes = await classes_service.get_by_subject_id(subject_id=subject_id)
        if not classes or len(classes) == 0:
            await callback.answer("Bu fan uchun sinflar topilmadi!", show_alert=True)
            await callback.message.delete()
            return
        
        await callback.message.edit_text(
            "Sinf tanlang:",
            reply_markup=keyboards.classes_inline_keyboard(classes=classes, prefix="class_for_video_view"))
        
    except Exception as e:
        logger.error(f"Error in handle_subject_select_for_video_view: {e}")
        await callback.answer(const.ERROR_MSG, show_alert=True)
        await callback.message.delete()

@router.callback_query(F.data.startswith("class_for_video_view:"))
async def handle_class_select_for_video_view(callback: CallbackQuery):
    try:
        class_id = int(callback.data.split(":")[1])
        _class = await classes_service.get_by_id(class_id)
        if not _class:
            await callback.answer("Sinf topilmadi!", show_alert=True)
            return
        
        topics = await topics_service.get_by_class_id(class_id=class_id)
        if not topics or len(topics) == 0:
            await callback.answer("Bu sinf uchun mavzular topilmadi!", show_alert=True)
            return
        
        await callback.message.edit_text(
            "Mavzu tanlang:",
            reply_markup=keyboards.topics_inline_keyboard(topics=topics, prefix="topic_for_video_view")
        )
    except Exception as e:
        logger.error(f"Error in handle_class_select_for_video_view: {e}")
        await callback.answer(const.ERROR_MSG, show_alert=True)
        await callback.message.delete()

@router.callback_query(F.data.startswith("topic_for_video_view:"))
async def handle_topic_select_for_video_view(callback: CallbackQuery):
    try:
        topic_id = int(callback.data.split(":")[1])
        topic = await topics_service.get_by_id(topic_id)
        if not topic:
            await callback.answer("Mavzu topilmadi!", show_alert=True)
            return
        
        video = await video_lessons_service.get_by_topic_id(topic_id=topic_id)
        if not video:
            await callback.answer("Bu mavvu uchun video topilmadi!", show_alert=True)
            return
        
        await bot.send_video(chat_id=callback.from_user.id, video=video.file_id, caption=topic.name)
    except Exception as e:
        logger.error(f"Error in handle_topic_select_for_video_view: {e}")
        await callback.answer(const.ERROR_MSG, show_alert=True)
        await callback.message.delete()



# ------------------------
# audio_lessons handlers
# ------------------------

class AddAudioStates(StatesGroup):
    audio = State()

# ➕ Add Audio
@router.message(F.text == "➕ Audio qo'shish")
async def add_audio_handler(message: Message):
    try:
        if message.from_user.id != ADMIN_ID:
            return

        subjects = await subjects_service.get_all()
        if not subjects:
            await message.answer("⚠️ Hali birorta fan qo'shilmagan")
            return

        await message.answer(
            "Fanni tanlang",
            reply_markup=keyboards.subjects_inline_keyboard(subjects, "subject_for_audio_add")
        )
    except Exception as e:
        logger.error("Error in add_audio_handler", exc_info=e)
        await message.answer(const.ERROR_MSG)

@router.callback_query(F.data.startswith("subject_for_audio_add:"))
async def handle_subject_select_for_audio_add(callback: CallbackQuery):
    try:
        subject_id = int(callback.data.split(":")[1])
        classes = await classes_service.get_by_subject_id(subject_id)
        if not classes:
            await callback.answer("Bu fan uchun sinflar topilmadi!", show_alert=True)
            await callback.message.delete()
            return

        await callback.message.edit_text(
            "Sinf tanlang:",
            reply_markup=keyboards.classes_inline_keyboard(classes, "class_for_audio_add")
        )
    except Exception as e:
        logger.error("Error in handle_subject_select_for_audio_add", exc_info=e)
        await callback.answer(const.ERROR_MSG, show_alert=True)
        await callback.message.delete()

@router.callback_query(F.data.startswith("class_for_audio_add:"))
async def handle_class_select_for_audio_add(callback: CallbackQuery):
    try:
        class_id = int(callback.data.split(":")[1])
        topics = await topics_service.get_by_class_id(class_id)
        if not topics:
            await callback.answer("Bu sinf uchun mavzular topilmadi!", show_alert=True)
            await callback.message.delete()
            return

        await callback.message.edit_text(
            "Mavzu tanlang:",
            reply_markup=keyboards.topics_inline_keyboard(topics, "topic_for_audio_add")
        )
    except Exception as e:
        logger.error("Error in handle_class_select_for_audio_add", exc_info=e)
        await callback.answer(const.ERROR_MSG, show_alert=True)
        await callback.message.delete()

@router.callback_query(F.data.startswith("topic_for_audio_add:"))
async def handle_topic_select_for_audio_add(callback: CallbackQuery, state: FSMContext):
    try:
        topic_id = int(callback.data.split(":")[1])
        exist_audio = await audio_lessons_service.get_by_topic_id(topic_id)
        if exist_audio:
            await callback.answer("Bu mavzu uchun audio biriktirilgan!", show_alert=True)
            return

        await state.update_data(topic_id=topic_id)
        await state.set_state(AddAudioStates.audio)
        await callback.message.edit_text(
            "Ushbu mavzu uchun audio yuboring:",
            reply_markup=keyboards.cancel_inline
        )
    except Exception as e:
        logger.error("Error in handle_topic_select_for_audio_add", exc_info=e)
        await callback.answer(const.ERROR_MSG, show_alert=True)
        await callback.message.delete()

@router.message(AddAudioStates.audio, F.audio)
async def handle_audio_upload(message: Message, state: FSMContext):
    try:
        audio = message.audio
        data = await state.get_data()
        topic_id = data["topic_id"]

        audio_lesson = AudioLesson(file_id=audio.file_id, topic_id=topic_id)
        await audio_lessons_service.create(audio_lesson)

        await state.clear()
        await message.answer("Audio yuklandi ✅", reply_markup=keyboards.admin_menu)

    except Exception as e:
        logger.error("Error in handle_audio_upload", exc_info=e)
        await message.answer(const.ERROR_MSG)

# 🗑️ Delete Audio
@router.message(F.text == "➖ Audio o'chirish")
async def delete_audio_handler(message: Message):
    try:
        if message.from_user.id != ADMIN_ID:
            return

        subjects = await subjects_service.get_all()
        if not subjects:
            await message.answer("⚠️ Hali birorta fan qo'shilmagan")
            return

        await message.answer(
            "Fanni tanlang",
            reply_markup=keyboards.subjects_inline_keyboard(subjects, "subject_for_audio_delete")
        )
    except Exception as e:
        logger.error("Error in delete_audio_handler", exc_info=e)
        await message.answer(const.ERROR_MSG)

@router.callback_query(F.data.startswith("subject_for_audio_delete:"))
async def handle_subject_select_for_audio_delete(callback: CallbackQuery):
    try:
        subject_id = int(callback.data.split(":")[1])
        classes = await classes_service.get_by_subject_id(subject_id)
        if not classes:
            await callback.answer("Bu fan uchun sinflar topilmadi!", show_alert=True)
            await callback.message.delete()
            return

        await callback.message.edit_text(
            "Sinf tanlang:",
            reply_markup=keyboards.classes_inline_keyboard(classes, "class_for_audio_delete")
        )
    except Exception as e:
        logger.error("Error in handle_subject_select_for_audio_delete", exc_info=e)
        await callback.answer(const.ERROR_MSG, show_alert=True)
        await callback.message.delete()

@router.callback_query(F.data.startswith("class_for_audio_delete:"))
async def handle_class_select_for_audio_delete(callback: CallbackQuery):
    try:
        class_id = int(callback.data.split(":")[1])
        topics = await topics_service.get_by_class_id(class_id)
        if not topics:
            await callback.answer("Bu sinf uchun mavzular topilmadi!", show_alert=True)
            await callback.message.delete()
            return

        await callback.message.edit_text(
            "Mavzu tanlang:",
            reply_markup=keyboards.topics_inline_keyboard(topics, "topic_for_audio_delete")
        )
    except Exception as e:
        logger.error("Error in handle_class_select_for_audio_delete", exc_info=e)
        await callback.answer(const.ERROR_MSG, show_alert=True)
        await callback.message.delete()

@router.callback_query(F.data.startswith("topic_for_audio_delete:"))
async def handle_topic_select_for_audio_delete(callback: CallbackQuery):
    try:
        topic_id = int(callback.data.split(":")[1])
        audio = await audio_lessons_service.get_by_topic_id(topic_id)
        if not audio:
            await callback.answer("Bu mavzu uchun audio biriktirilmagan!", show_alert=True)
            return

        await callback.message.edit_text(
            "Haqiqatdan ham ushbu audio faylni o'chirmoqchimisiz?",
            reply_markup=keyboards.yes_no_inline_keyboard(
                f"confirm_delete_audio:{audio.id}",
                "cancel_delete_audio"
            )
        )
    except Exception as e:
        logger.error("Error in handle_topic_select_for_audio_delete", exc_info=e)
        await callback.answer(const.ERROR_MSG, show_alert=True)
        await callback.message.delete()

@router.callback_query(F.data.startswith("confirm_delete_audio:"))
async def confirm_delete_audio(callback: CallbackQuery):
    try:
        audio_id = int(callback.data.split(":")[1])
        await audio_lessons_service.delete_by_id(audio_id)
        await callback.message.edit_text("Audio o'chirildi ✅")
    except Exception as e:
        logger.error("Error in confirm_delete_audio", exc_info=e)
        await callback.answer(const.ERROR_MSG, show_alert=True)
        await callback.message.delete()

@router.callback_query(F.data == "cancel_delete_audio")
async def cancel_delete_audio(callback: CallbackQuery):
    try:
        await callback.answer("Bekor qilindi")
        await callback.message.delete()
    except Exception as e:
        logger.error("Error in cancel_delete_audio", exc_info=e)
        await callback.answer(const.ERROR_MSG, show_alert=True)
        await callback.message.delete()

# 🎧 View Audio
@router.message(F.text == "🎧 Audio ko'rish")
async def view_audio_handler(message: Message):
    try:
        if message.from_user.id != ADMIN_ID:
            return

        subjects = await subjects_service.get_all()
        if not subjects:
            await message.answer("⚠️ Hali birorta fan qo'shilmagan")
            return

        await message.answer(
            "Fanni tanlang",
            reply_markup=keyboards.subjects_inline_keyboard(subjects, "subject_for_audio_view")
        )
    except Exception as e:
        logger.error("Error in view_audio_handler", exc_info=e)
        await message.answer(const.ERROR_MSG)

@router.callback_query(F.data.startswith("subject_for_audio_view:"))
async def handle_subject_select_for_audio_view(callback: CallbackQuery):
    try:
        subject_id = int(callback.data.split(":")[1])
        classes = await classes_service.get_by_subject_id(subject_id)
        if not classes:
            await callback.answer("Bu fan uchun sinflar topilmadi!", show_alert=True)
            await callback.message.delete()
            return

        await callback.message.edit_text(
            "Sinf tanlang:",
            reply_markup=keyboards.classes_inline_keyboard(classes, "class_for_audio_view")
        )
    except Exception as e:
        logger.error("Error in handle_subject_select_for_audio_view", exc_info=e)
        await callback.answer(const.ERROR_MSG, show_alert=True)
        await callback.message.delete()

@router.callback_query(F.data.startswith("class_for_audio_view:"))
async def handle_class_select_for_audio_view(callback: CallbackQuery):
    try:
        class_id = int(callback.data.split(":")[1])
        topics = await topics_service.get_by_class_id(class_id)
        if not topics:
            await callback.answer("Bu sinf uchun mavzular topilmadi!", show_alert=True)
            await callback.message.delete()
            return

        await callback.message.edit_text(
            "Mavzu tanlang:",
            reply_markup=keyboards.topics_inline_keyboard(topics, "topic_for_audio_view")
        )
    except Exception as e:
        logger.error("Error in handle_class_select_for_audio_view", exc_info=e)
        await callback.answer(const.ERROR_MSG, show_alert=True)
        await callback.message.delete()

@router.callback_query(F.data.startswith("topic_for_audio_view:"))
async def handle_topic_select_for_audio_view(callback: CallbackQuery):
    try:
        topic_id = int(callback.data.split(":")[1])
        topic = await topics_service.get_by_id(topic_id)
        audio = await audio_lessons_service.get_by_topic_id(topic_id)
        if not audio:
            await callback.answer("Bu mavzu uchun audio topilmadi!", show_alert=True)
            return

        await bot.send_audio(chat_id=callback.from_user.id, audio=audio.file_id, caption=topic.name)
        await callback.message.delete()
    except Exception as e:
        logger.error("Error in handle_topic_select_for_audio_view", exc_info=e)
        await callback.answer(const.ERROR_MSG, show_alert=True)
        await callback.message.delete()


# ------------------------
# pdf_materials handlers
# ------------------------
class AddPdfStates(StatesGroup):
    pdf = State()

# Add PDF
@router.message(F.text == "➕ PDF qo'shish")
async def add_pdf_handler(message: Message):
    try:
        if message.from_user.id != ADMIN_ID:
            return

        subjects = await subjects_service.get_all()
        if not subjects:
            await message.answer("⚠️ Hali birorta fan qo'shilmagan")
            return

        await message.answer("Fanni tanlang", reply_markup=keyboards.subjects_inline_keyboard(subjects, prefix="subject_for_pdf_add"))

    except Exception as e:
        logger.error(f"Error in add_pdf_handler: {e}")
        await message.answer(const.ERROR_MSG)

@router.callback_query(F.data.startswith("subject_for_pdf_add:"))
async def handle_subject_select_for_pdf_add(callback: CallbackQuery):
    try:
        subject_id = int(callback.data.split(":")[1])
        classes = await classes_service.get_by_subject_id(subject_id)
        if not classes:
            await callback.answer("Bu fan uchun sinflar topilmadi!", show_alert=True)
            await callback.message.delete()
            return

        await callback.message.edit_text("Sinf tanlang:", reply_markup=keyboards.classes_inline_keyboard(classes, prefix="class_for_pdf_add"))

    except Exception as e:
        logger.error(f"Error in handle_subject_select_for_pdf_add: {e}")
        await callback.answer(const.ERROR_MSG, show_alert=True)
        await callback.message.delete()

@router.callback_query(F.data.startswith("class_for_pdf_add:"))
async def handle_class_select_for_pdf_add(callback: CallbackQuery):
    try:
        class_id = int(callback.data.split(":")[1])
        topics = await topics_service.get_by_class_id(class_id)
        if not topics:
            await callback.answer("Bu sinf uchun mavzular topilmadi!", show_alert=True)
            await callback.message.delete()
            return

        await callback.message.edit_text("Mavzu tanlang:", reply_markup=keyboards.topics_inline_keyboard(topics, prefix="topic_for_pdf_add"))

    except Exception as e:
        logger.error(f"Error in handle_class_select_for_pdf_add: {e}")
        await callback.answer(const.ERROR_MSG, show_alert=True)
        await callback.message.delete()

@router.callback_query(F.data.startswith("topic_for_pdf_add:"))
async def handle_topic_select_for_pdf_add(callback: CallbackQuery, state: FSMContext):
    try:
        topic_id = int(callback.data.split(":")[1])
        exist_pdf = await pdf_materials_service.get_by_topic_id(topic_id)
        if exist_pdf:
            await callback.answer("Bu mavzu uchun PDF biriktirilgan!", show_alert=True)
            return

        await state.update_data(topic_id=topic_id)
        await state.set_state(AddPdfStates.pdf)
        await callback.message.edit_text("Ushbu mavzu uchun PDF yuboring:", reply_markup=keyboards.cancel_inline)

    except Exception as e:
        logger.error(f"Error in handle_topic_select_for_pdf_add: {e}")
        await callback.answer(const.ERROR_MSG, show_alert=True)
        await callback.message.delete()

@router.message(AddPdfStates.pdf, F.document)
async def handle_pdf_upload(message: Message, state: FSMContext):
    try:
        data = await state.get_data()
        topic_id = data["topic_id"]
        document = message.document

        pdf_material = PDFMaterial(file_id=document.file_id, topic_id=topic_id)
        await pdf_materials_service.create(pdf_material)

        await state.clear()
        await message.answer("✅ PDF yuklandi", reply_markup=keyboards.admin_menu)

    except Exception as e:
        logger.error(f"Error in handle_pdf_upload: {e}")
        await message.answer(const.ERROR_MSG)

# View PDF
@router.message(F.text == "📝 PDF ko'rish")
async def view_pdf_handler(message: Message):
    try:
        if message.from_user.id != ADMIN_ID:
            return

        subjects = await subjects_service.get_all()
        if not subjects:
            await message.answer("⚠️ Hali birorta fan qo'shilmagan")
            return

        await message.answer("Fanni tanlang", reply_markup=keyboards.subjects_inline_keyboard(subjects, prefix="subject_for_pdf_view"))

    except Exception as e:
        logger.error(f"Error in view_pdf_handler: {e}")
        await message.answer(const.ERROR_MSG)

@router.callback_query(F.data.startswith("subject_for_pdf_view:"))
async def handle_subject_select_for_pdf_view(callback: CallbackQuery):
    try:
        subject_id = int(callback.data.split(":")[1])
        classes = await classes_service.get_by_subject_id(subject_id)
        if not classes:
            await callback.answer("Bu fan uchun sinflar topilmadi!", show_alert=True)
            await callback.message.delete()
            return

        await callback.message.edit_text("Sinf tanlang:", reply_markup=keyboards.classes_inline_keyboard(classes, prefix="class_for_pdf_view"))

    except Exception as e:
        logger.error(f"Error in handle_subject_select_for_pdf_view: {e}")
        await callback.answer(const.ERROR_MSG, show_alert=True)
        await callback.message.delete()

@router.callback_query(F.data.startswith("class_for_pdf_view:"))
async def handle_class_select_for_pdf_view(callback: CallbackQuery):
    try:
        class_id = int(callback.data.split(":")[1])
        topics = await topics_service.get_by_class_id(class_id)
        if not topics:
            await callback.answer("Bu sinf uchun mavzular topilmadi!", show_alert=True)
            await callback.message.delete()
            return

        await callback.message.edit_text("Mavzu tanlang:", reply_markup=keyboards.topics_inline_keyboard(topics, prefix="topic_for_pdf_view"))

    except Exception as e:
        logger.error(f"Error in handle_class_select_for_pdf_view: {e}")
        await callback.answer(const.ERROR_MSG, show_alert=True)
        await callback.message.delete()

@router.callback_query(F.data.startswith("topic_for_pdf_view:"))
async def handle_topic_select_for_pdf_view(callback: CallbackQuery):
    try:
        topic_id = int(callback.data.split(":")[1])
        pdf = await pdf_materials_service.get_by_topic_id(topic_id)
        if not pdf:
            await callback.answer("Bu mavzu uchun PDF topilmadi!", show_alert=True)
            return

        await bot.send_document(chat_id=callback.from_user.id, document=pdf.file_id)

    except Exception as e:
        logger.error(f"Error in handle_topic_select_for_pdf_view: {e}")
        await callback.answer(const.ERROR_MSG, show_alert=True)
        await callback.message.delete()

@router.message(F.text == "➖ PDF o'chirish")
async def delete_pdf_handler(message: Message):
    try:
        if message.from_user.id != ADMIN_ID:
            return

        subjects = await subjects_service.get_all()
        if not subjects:
            await message.answer("⚠️ Hali birorta fan qo'shilmagan")
            return

        await message.answer(
            "Fanni tanlang",
            reply_markup=keyboards.subjects_inline_keyboard(subjects, prefix="subject_for_pdf_delete")
        )
    except Exception as e:
        logger.error(f"Error in delete_pdf_handler: {e}")
        await message.answer(const.ERROR_MSG)

@router.callback_query(F.data.startswith("subject_for_pdf_delete:"))
async def handle_subject_select_for_pdf_delete(callback: CallbackQuery):
    try:
        subject_id = int(callback.data.split(":")[1])
        classes = await classes_service.get_by_subject_id(subject_id)
        if not classes:
            await callback.answer("Bu fan uchun sinflar topilmadi!", show_alert=True)
            await callback.message.delete()
            return

        await callback.message.edit_text(
            "Sinf tanlang:",
            reply_markup=keyboards.classes_inline_keyboard(classes, prefix="class_for_pdf_delete")
        )

    except Exception as e:
        logger.error(f"Error in handle_subject_select_for_pdf_delete: {e}")
        await callback.answer(const.ERROR_MSG, show_alert=True)
        await callback.message.delete()

@router.callback_query(F.data.startswith("class_for_pdf_delete:"))
async def handle_class_select_for_pdf_delete(callback: CallbackQuery):
    try:
        class_id = int(callback.data.split(":")[1])
        topics = await topics_service.get_by_class_id(class_id)
        if not topics:
            await callback.answer("Bu sinf uchun mavzular topilmadi!", show_alert=True)
            await callback.message.delete()
            return

        await callback.message.edit_text(
            "Mavzu tanlang:",
            reply_markup=keyboards.topics_inline_keyboard(topics, prefix="topic_for_pdf_delete")
        )

    except Exception as e:
        logger.error(f"Error in handle_class_select_for_pdf_delete: {e}")
        await callback.answer(const.ERROR_MSG, show_alert=True)
        await callback.message.delete()

@router.callback_query(F.data.startswith("topic_for_pdf_delete:"))
async def handle_topic_select_for_pdf_delete(callback: CallbackQuery):
    try:
        topic_id = int(callback.data.split(":")[1])
        pdf = await pdf_materials_service.get_by_topic_id(topic_id)
        if not pdf:
            await callback.answer("Bu mavzu uchun PDF biriktirilmagan!", show_alert=True)
            return

        await callback.message.edit_text(
            "Haqiqatdan ham ushbu mavzuga biriktirilgan PDFni o'chirmoqchimisiz?",
            reply_markup=keyboards.yes_no_inline_keyboard(
                yes_data=f"confirm_delete_pdf:{pdf.id}",
                no_data="cancel_delete_pdf"
            )
        )
    except Exception as e:
        logger.error(f"Error in handle_topic_select_for_pdf_delete: {e}")
        await callback.answer(const.ERROR_MSG, show_alert=True)
        await callback.message.delete()

@router.callback_query(F.data.startswith("confirm_delete_pdf:"))
async def confirm_delete_pdf(callback: CallbackQuery):
    try:
        pdf_id = int(callback.data.split(":")[1])
        await pdf_materials_service.delete_by_id(pdf_id)

        await callback.message.edit_text("✅ PDF o'chirildi")

    except Exception as e:
        logger.error(f"Error in confirm_delete_pdf: {e}")
        await callback.answer(const.ERROR_MSG, show_alert=True)
        await callback.message.delete()

@router.callback_query(F.data == "cancel_delete_pdf")
async def cancel_delete_pdf(callback: CallbackQuery):
    try:
        await callback.answer("Bekor qilindi", show_alert=True)
        await callback.message.delete()

    except Exception as e:
        logger.error(f"Error in cancel_delete_pdf: {e}")
        await callback.answer(const.ERROR_MSG, show_alert=True)
        await callback.message.delete()




# ⚙️ Parser test
class ParserTestStates(StatesGroup):
    file = State()

@router.message(F.text == "⚙️ Parser test")
async def parser_test(message: Message, state: FSMContext):
    try:
        await state.set_state(ParserTestStates.file)
        await message.reply("Ok, docx faylni yuboring: ", reply_markup=keyboards.back)
    except Exception as e:
        logger.error(f"Error in parser_test: {e}")
        await message.answer(const.ERROR_MSG)

@router.message(ParserTestStates.file, F.document)
async def handle_test_file(message: Message, state: FSMContext):
    try:
        if not message.document:
            await message.answer("⚠️ Siz doc fayl yuborishingiz kerak!")
            return

        await state.clear()

        # Ensure the upload folder exists
        os.makedirs("uploaded_files", exist_ok=True)

        file = message.document
        file_path = f"uploaded_files/{str(uuid.uuid4())}{file.file_name}"

        # ✅ Correct download method in Aiogram 3
        await bot.download(file, destination=file_path)

        await message.answer("✅ Fayl muvaffaqiyatli yuklandi. Testlarni o'qiyapman...")

        # Parse and get the path to the generated test file
        temp_tests_path = test_parser.parse_and_save(file_path)

        await message.answer_document(
            document=FSInputFile(temp_tests_path),
            caption=(
                "✅ Testlar muvaffaqiyatli o'qildi va tayyorlandi.\n"
                "Testlarni ko'zdan kechiring, agar hammasi to'g'ri bo'lsa ushbu fayl bilan testlarni qo'shishingiz mumkin."
            ),
            reply_markup=keyboards.main_menu
        )

        await state.clear()

    except Exception as e:
        logger.error(f"Error in handle_test_file: {e}")
        await message.answer(const.ERROR_MSG)


##########################
# ➕ Test qo'shish (word)
##########################
class AddTestStates(StatesGroup):
    file = State()

@router.message(F.text == "➕ Test qo'shish (word)")
async def add_tests(message: Message):
    try:
        user_id = message.from_user.id
        if ADMIN_ID != user_id: return

        subjects = await subjects_service.get_all()
        if not subjects:
            await message.answer("Birorta fan kiritilmagan!", reply_markup=keyboards.admin_menu)
            return
        
        await message.answer(
            "Fanni tanlang.",
            reply_markup=keyboards.subjects_inline_keyboard(subjects=subjects, prefix="subject_for_test_add"))
    except Exception as e:
        logger.error(f"Error in add_tests: {e}")
        await message.answer(const.ERROR_MSG)

@router.callback_query(F.data.startswith("subject_for_test_add:"))
async def handle_subject_select_for_test_add(callback: CallbackQuery):
    try:
        subject_id = int(callback.data.split(":")[1])
        classes = await classes_service.get_by_subject_id(subject_id=subject_id)
        if not classes or len(classes) == 0:
            await callback.answer("Bu fan uchun sinf yo'q!", show_alert=True)
            return
        
        await callback.message.edit_text(
            "Sinfni tanlang:",
            reply_markup=keyboards.classes_inline_keyboard(classes=classes, prefix="class_for_test_add")
        )
    except Exception as e:
        logger.error(f"Error in handle_subject_select_for_test_add: {e}")
        await callback.answer(const.ERROR_MSG, show_alert=True)

@router.callback_query(F.data.startswith("class_for_test_add:"))
async def handle_class_select_for_test_add(callback: CallbackQuery):
    try:
        class_id = int(callback.data.split(":")[1])
        topics = await topics_service.get_by_class_id(class_id=class_id)
        if not topics or len(topics) == 0:
            await callback.answer("Bu sinf uchun mavzular yo'q!", show_alert=True)
            return
        
        await callback.message.edit_text(
            "Mavzuni tanlang:",
            reply_markup=keyboards.topics_inline_keyboard(topics=topics, prefix="topic_for_test_add")
        )
    except Exception as e:
        logger.error(f"Error in handle_class_select_for_test_add: {e}")
        await callback.answer(const.ERROR_MSG, show_alert=True)
        
@router.callback_query(F.data.startswith("topic_for_test_add:"))
async def handle_topic_select_for_test_add(callback: CallbackQuery, state: FSMContext):
    try:
        topic_id = int(callback.data.split(":")[1])
        await state.set_state(AddTestStates.file)
        await state.update_data(topic_id=topic_id)
        await callback.message.edit_text("Ok, docx faylni yuboring: ", reply_markup=keyboards.cancel_inline)
    except Exception as e:
        logger.error(f"Error in handle_topic_select_for_test_add: {e}")
        await callback.answer(const.ERROR_MSG, show_alert=True)

@router.message(AddTestStates.file, F.document)
async def handle_add_tests(message: Message, state: FSMContext):
    try:
        if not message.document:
            await message.answer("⚠️ Siz doc fayl yuborishingiz kerak!")
            return

        data = await state.get_data()
        topic_id = data['topic_id']
        await state.clear()

        os.makedirs("uploaded_files", exist_ok=True)

        file = message.document
        file_path = f"uploaded_files/{str(uuid.uuid4())}{file.file_name}"

        # ✅ Correct download method in Aiogram 3
        await bot.download(file, destination=file_path)

        await message.answer(
            "✅ Fayl muvaffaqiyatli yuklandi. Testlarni o'qiyapman..."
            "‼️ Hech narsa qilmang, bu bir necha daqiqa vaqt olishi mumkin.",
            reply_markup=ReplyKeyboardRemove()
            )
        
        tests = test_parser.parse_docx_tests(file_path=file_path)
        success = 0
        done = 0
        test_count = len(tests)
        last = 10
        doing_msg = await message.answer("Boshlanmoqda....")

        for test in tests:
            try:
                new_test = Test(
                    question=test.question,
                    topic_id=topic_id
                )
                options = []
                for option in test.options:
                    new_option = TestOption()
                    new_option.option = f"{option.letter}. {option.option}"
                    new_option.is_correct = option.is_correct

                    options.append(new_option)

                await tests_service.save_test_with_options(new_test, options=options)
                success += 1
                done += 1
                if last + 10 == done:
                    await doing_msg.edit_text(f"{done}/{test_count} ✅")
                    last = done
                    
                await asyncio.sleep(0.1)
            except Exception as e:
                logger.error(f"Error saving test: {e}")
                done += 1

        await message.answer(
            "Testlar qo'shildi ✅\n" \
            f"Berilgan testlar: {test_count} ta\n" \
            f"Muvaffaqiyatli : {success} ta\n" \
            f"Xatolik bo'ldi: {test_count - success} ta.",
            reply_markup=keyboards.admin_menu
        )

        

    except Exception as e:
        logger.error(f"Error in handle_add_tests: {e}")
        await message.answer(const.ERROR_MSG)


###############################
# ➕ Test qo'shish (rasmlik) #
###############################
@router.message(F.text == "➕ Test qo'shish (rasmlik)")
async def test_add_with_image(message: Message):
    try:
        user_id = message.from_user.id
        if user_id != ADMIN_ID: return
        
        subjects = await subjects_service.get_all()
        if not subjects or len(subjects) == 0:
            await message.answer("Birorta fan topilmadi!")
            return
        
        await message.answer(
            "Fan tanlang:",
            reply_markup=keyboards.subjects_inline_keyboard(subjects=subjects, prefix="subject_for_test_add_with_image"))
    except Exception as e:
        logger.error(f"Error in test_add_with_image: {e}")
        await message.answer(const.ERROR_MSG)

@router.callback_query(F.data.startswith("subject_for_test_add_with_image:"))
async def handle_subject_select_for_test_image(callback: CallbackQuery):
    try:
        subject_id = int(callback.data.split(":")[1])
        classes = await classes_service.get_by_subject_id(subject_id=subject_id)
        if not classes or len(classes) == 0:
            await callback.answer("Bu fan uchun sinflar topilmadi!", show_alert=True)
            return
        
        await callback.message.edit_text(
            text="Sinfni tanlang:",
            reply_markup=keyboards.classes_inline_keyboard(classes=classes, prefix="class_for_test_add_with_image")
        )
    except Exception as e:
        logger.error(f"Error in handle_subject_select_for_test_image: {e}")
        await callback.answer(const.ERROR_MSG, show_alert=True)

@router.callback_query(F.data.startswith("class_for_test_add_with_image:"))
async def handle_class_select_for_test_image(callback: CallbackQuery):
    try:
        class_id = int(callback.data.split(":")[1])
        topics = await topics_service.get_by_class_id(class_id=class_id)
        if not topics or len(topics) == 0:
            await callback.answer("Bu sinf uchun mavzular topilmadi!", show_alert=True)
            return
        
        await callback.message.edit_text(
            text="Mavzuni tanlang: ",
            reply_markup=keyboards.topics_inline_keyboard(topics=topics, prefix="topic_for_test_add_with_image")
        )
    except Exception as e:
        logger.error(f"Error in handle_class_select_for_test_image: {e}")
        await callback.answer(const.ERROR_MSG, show_alert=True)

class AddTestImageStates(StatesGroup):
    test = State()
    image = State()

@router.callback_query(F.data.startswith("topic_for_test_add_with_image:"))
async def handle_topic_select_for_test_image(callback: CallbackQuery, state: FSMContext):
    try:
        topic_id = int(callback.data.split(":")[1])
        await state.set_state(AddTestImageStates.test)
        await state.update_data(topic_id=topic_id)
        await callback.message.edit_text(
            text="Ushbu mavzu uchun test textini kiriting: ",
            reply_markup=keyboards.cancel_inline
        )
    except Exception as e:
        logger.error(f"Error in handle_topic_select_for_test_image: {e}")
        await callback.answer(const.ERROR_MSG, show_alert=True)

@router.message(AddTestImageStates.test)
async def handle_test_text(message: Message, state: FSMContext):
    try:
        test = message.text
        await state.update_data(test=test)
        await state.set_state(AddTestImageStates.image)
        await message.answer("Ajoyib!, endi ushbu test uchun rasm yuboring yoki o'tkazib yuboring.", reply_markup=keyboards.skip)
    except Exception as  e:
        logger.error(f"Error in handle_test_text: {e}")
        await message.answer(const.ERROR_MSG)

@router.message(AddTestImageStates.image, F.photo)
async def handle_test_image(message: Message, state: FSMContext):
    try:
        photo = message.photo[-1]
        await message.answer("Qabul qildim, kuting...")
        data = await state.get_data()
        await state.clear()
        test_text = data['test']
        topic_id = data['topic_id']
        test = test_parser.parse_single_test(test_text)
        if not test:
            await message.answer("Test aniqlanmadi, xatolik!", reply_markup=keyboards.admin_menu)
            return
        
        new_test = Test(
            question=test.question,
            image_id=photo.file_id,
            topic_id=topic_id
        )
        options = [TestOption(option=f'{option.letter}. {option.option.replace('*', '')}', is_correct=option.is_correct) for option in test.options]

        await tests_service.save_test_with_options(new_test, options=options)
        await message.answer("Test saqlandi ✅", reply_markup=keyboards.admin_menu)
   
    except Exception as e:
        logger.error(f"Error in handle_test_image: {e}")
        await message.answer(const.ERROR_MSG)

@router.message(AddTestImageStates.image)
async def handle_test_skip(message: Message, state: FSMContext):
    try:
        text = message.text.strip()
        if text.upper() != "SKIP":
            await message.answer("Siz rasm yuborishingiz yoki o'tkazib yuborishingiz kerak!")
            return
        
        await message.answer("Qabul qildim, kuting...")
        data = await state.get_data()
        await state.clear()
        test_text = data['test']
        topic_id = data['topic_id']
        test = test_parser.parse_single_test(test_text)
        if not test:
            await message.answer("Test aniqlanmadi, xatolik!", reply_markup=keyboards.admin_menu)
            return
        
        new_test = Test(
            question=test.question,
            topic_id=topic_id
        )
        options = [TestOption(option=f'{option.letter}. {option.option.replace('*', '')}', is_correct=option.is_correct) for option in test.options]

        await tests_service.save_test_with_options(new_test, options=options)
        await message.answer("Test saqlandi ✅", reply_markup=keyboards.admin_menu)

    except Exception as e:
        logger.error(f"Error in handle_test_skip: {e}")
        await message.answer(const.ERROR_MSG)



###############################
# ❌ Test o'chirish           #
###############################

@router.message(F.text == "❌ Test o'chirish")
async def test_delete_start(message: Message):
    try:
        user_id = message.from_user.id
        if user_id != ADMIN_ID: return

        subjects = await subjects_service.get_all()
        if not subjects:
            await message.answer("Birorta fan topilmadi!")
            return

        await message.answer(
            "O'chirmoqchi bo'lgan testlar uchun fan tanlang:",
            reply_markup=keyboards.subjects_inline_keyboard(subjects=subjects, prefix="subject_for_test_delete")
        )
    except Exception as e:
        logger.error(f"Error in test_delete_start: {e}")
        await message.answer(const.ERROR_MSG)


@router.callback_query(F.data.startswith("subject_for_test_delete:"))
async def test_delete_select_subject(callback: CallbackQuery):
    try:
        subject_id = int(callback.data.split(":")[1])
        classes = await classes_service.get_by_subject_id(subject_id=subject_id)

        if not classes:
            await callback.answer("Bu fan uchun sinflar topilmadi!", show_alert=True)
            return

        await callback.message.edit_text(
            text="O'chirmoqchi bo'lgan testlar uchun sinf tanlang:",
            reply_markup=keyboards.classes_inline_keyboard(classes=classes, prefix="class_for_test_delete")
        )
    except Exception as e:
        logger.error(f"Error in test_delete_select_subject: {e}")
        await callback.answer(const.ERROR_MSG, show_alert=True)


@router.callback_query(F.data.startswith("class_for_test_delete:"))
async def test_delete_select_class(callback: CallbackQuery):
    try:
        class_id = int(callback.data.split(":")[1])
        topics = await topics_service.get_by_class_id(class_id=class_id)

        if not topics:
            await callback.answer("Bu sinf uchun mavzular topilmadi!", show_alert=True)
            return

        await callback.message.edit_text(
            text="O'chirmoqchi bo'lgan testlar uchun mavzu tanlang:",
            reply_markup=keyboards.topics_inline_keyboard(topics=topics, prefix="topic_for_test_delete")
        )
    except Exception as e:
        logger.error(f"Error in test_delete_select_class: {e}")
        await callback.answer(const.ERROR_MSG, show_alert=True)


@router.callback_query(F.data.startswith("topic_for_test_delete:"))
async def test_delete_select_topic(callback: CallbackQuery):
    try:
        topic_id = int(callback.data.split(":")[1])

        await callback.message.edit_text(
            text="❓ Ushbu mavzudagi barcha testlarni o'chirmoqchimisiz?",
            reply_markup=keyboards.yes_no_inline_keyboard(yes_data=f"confirm_delete_tests:{topic_id}", no_data="cancel_delete_tests")
        )
    except Exception as e:
        logger.error(f"Error in test_delete_select_topic: {e}")
        await callback.answer(const.ERROR_MSG, show_alert=True)

@router.callback_query(F.data.startswith("confirm_delete_tests:"))
async def test_delete_confirm(callback: CallbackQuery):
    try:
        topic_id = int(callback.data.split(":")[1])

        await tests_service.delete_by_topic_id(topic_id)

        await callback.message.edit_text(
            "✅ Testlar muvaffaqiyatli o'chirildi.",
        )
    except Exception as e:
        logger.error(f"Error in test_delete_confirm: {e}")
        await callback.answer(const.ERROR_MSG, show_alert=True)

@router.callback_query(F.data == "cancel_delete_tests")
async def test_delete_cancel(callback: CallbackQuery):
    try:
        await callback.message.edit_text("❌ Bekor qilindi.")
    except Exception as e:
        logger.error(f"Error in test_delete_cancel: {e}")
        await callback.answer(const.ERROR_MSG, show_alert=True)



########################################
# ➕ Fill Blanks Test qo'shish (word)  #
########################################

class AddFillBlanksTestStates(StatesGroup):
    file = State()

@router.message(F.text == "➕ Fill Blanks Test qo'shish (word)")
async def add_fill_blanks_tests(message: Message):
    try:
        user_id = message.from_user.id
        if ADMIN_ID != user_id: return

        subjects = await subjects_service.get_all()
        if not subjects:
            await message.answer("Birorta fan kiritilmagan!", reply_markup=keyboards.admin_menu)
            return

        await message.answer(
            "Fanni tanlang.",
            reply_markup=keyboards.subjects_inline_keyboard(subjects=subjects, prefix="subject_for_fill_blanks_add")
        )
    except Exception as e:
        logger.error(f"Error in add_fill_blanks_tests: {e}")
        await message.answer(const.ERROR_MSG)

@router.callback_query(F.data.startswith("subject_for_fill_blanks_add:"))
async def handle_subject_select_for_fill_blanks_add(callback: CallbackQuery):
    try:
        subject_id = int(callback.data.split(":")[1])
        classes = await classes_service.get_by_subject_id(subject_id=subject_id)
        if not classes:
            await callback.answer("Bu fan uchun sinflar yo'q!", show_alert=True)
            return

        await callback.message.edit_text(
            "Sinfni tanlang:",
            reply_markup=keyboards.classes_inline_keyboard(classes=classes, prefix="class_for_fill_blanks_add")
        )
    except Exception as e:
        logger.error(f"Error in handle_subject_select_for_fill_blanks_add: {e}")
        await callback.answer(const.ERROR_MSG, show_alert=True)

@router.callback_query(F.data.startswith("class_for_fill_blanks_add:"))
async def handle_class_select_for_fill_blanks_add(callback: CallbackQuery):
    try:
        class_id = int(callback.data.split(":")[1])
        topics = await topics_service.get_by_class_id(class_id=class_id)
        if not topics:
            await callback.answer("Bu sinf uchun mavzular yo'q!", show_alert=True)
            return

        await callback.message.edit_text(
            "Mavzuni tanlang:",
            reply_markup=keyboards.topics_inline_keyboard(topics=topics, prefix="topic_for_fill_blanks_add")
        )
    except Exception as e:
        logger.error(f"Error in handle_class_select_for_fill_blanks_add: {e}")
        await callback.answer(const.ERROR_MSG, show_alert=True)

@router.callback_query(F.data.startswith("topic_for_fill_blanks_add:"))
async def handle_topic_select_for_fill_blanks_add(callback: CallbackQuery, state: FSMContext):
    try:
        topic_id = int(callback.data.split(":")[1])
        await state.set_state(AddFillBlanksTestStates.file)
        await state.update_data(topic_id=topic_id)
        await callback.message.edit_text("Ok, docx faylni yuboring:", reply_markup=keyboards.cancel_inline)
    except Exception as e:
        logger.error(f"Error in handle_topic_select_for_fill_blanks_add: {e}")
        await callback.answer(const.ERROR_MSG, show_alert=True)

@router.message(AddFillBlanksTestStates.file, F.document)
async def handle_add_fill_blanks_tests(message: Message, state: FSMContext):
    try:
        if not message.document:
            await message.answer("⚠️ Siz doc fayl yuborishingiz kerak!")
            return

        data = await state.get_data()
        topic_id = data['topic_id']
        await state.clear()

        os.makedirs("uploaded_files", exist_ok=True)

        file = message.document
        file_path = f"uploaded_files/{str(uuid.uuid4())}_{file.file_name}"

        await bot.download(file, destination=file_path)

        await message.answer(
            "✅ Fayl yuklandi. Testlarni o'qiyapman..."
            "‼️ Hech narsa qilmang, bu bir necha daqiqa vaqt olishi mumkin.",
            reply_markup=ReplyKeyboardRemove()
        )

        # PARSE FILL BLANKS TESTS
        tests = test_parser.parse_docx_fill_blanks(file_path=file_path)
        test_count = len(tests)
        success = 0
        done = 0
        last = 10

        doing_msg = await message.answer("Boshlanmoqda...")

        for test in tests:
            try:
                new_test = FillBlanksTest(
                    text=test.text,
                    topic_id=topic_id
                )

                answers = [
                    FillBlanksTestAnswer(
                        fill_blanks_test_id=0,  # will be set by service
                        number=ans.number,
                        answer=ans.answer
                    )
                    for ans in test.answers
                ]

                await fill_blanks_tests_service.save_test_with_answers(new_test, answers)

                success += 1
                done += 1

                if last + 10 == done:
                    await doing_msg.edit_text(f"{done}/{test_count} ✅")
                    last = done

                await asyncio.sleep(0.05)

            except Exception as e:
                logger.error(f"Error saving fill blanks test: {e}")
                done += 1


        await message.answer(
            "Testlar qo'shildi ✅\n"
            f"Berilgan testlar: {test_count} ta\n"
            f"Muvaffaqiyatli: {success} ta\n"
            f"Xatolik bo'ldi: {test_count - success} ta.",
            reply_markup=keyboards.admin_menu
        )

    except Exception as e:
        logger.error(f"Error in handle_add_fill_blanks_tests: {e}")
        await message.answer(const.ERROR_MSG)


##############################
# ⚙️ Fill Blanks Parser test #
##############################

class ParserFillBlanksTestStates(StatesGroup):
    file = State()

@router.message(F.text == "⚙️ Fill Blanks Parser test")
async def parser_fill_blanks_test(message: Message, state: FSMContext):
    try:
        await state.set_state(ParserFillBlanksTestStates.file)
        await message.reply("Ok, docx faylni yuboring:", reply_markup=keyboards.back)
    except Exception as e:
        logger.error(f"Error in parser_fill_blanks_test: {e}")
        await message.answer(const.ERROR_MSG)

@router.message(ParserFillBlanksTestStates.file, F.document)
async def handle_fill_blanks_parser_file(message: Message, state: FSMContext):
    try:
        if not message.document:
            await message.answer("⚠️ Siz doc fayl yuborishingiz kerak!")
            return

        await state.clear()

        os.makedirs("uploaded_files", exist_ok=True)

        file = message.document
        file_path = f"uploaded_files/{str(uuid.uuid4())}_{file.file_name}"

        await bot.download(file, destination=file_path)

        await message.answer("✅ Fayl muvaffaqiyatli yuklandi. Testlarni o'qiyapman...")

        # Parse and generate .txt for verification
        tests = test_parser.parse_docx_fill_blanks(file_path)
        dest_path = f"temp_tests/{str(uuid.uuid4())}_fill_blanks_tests.txt"

        os.makedirs("temp_tests", exist_ok=True)

        with open(dest_path, "w", encoding="utf-8") as f:
            for idx, test in enumerate(tests, 1):
                f.write(f"{idx}) {test.text}\n")
                for ans in test.answers:
                    f.write(f"{ans.number}. {ans.answer}\n")
                f.write("\n")

        await message.answer_document(
            document=FSInputFile(dest_path),
            caption=(
                "✅ Fill blanks testlar muvaffaqiyatli o'qildi.\n"
                "Faylni ko'zdan kechiring, agar to'g'ri bo'lsa uni saqlash uchun ishlatishingiz mumkin."
            ),
            reply_markup=keyboards.main_menu
        )

    except Exception as e:
        logger.error(f"Error in handle_fill_blanks_parser_file: {e}")
        await message.answer(const.ERROR_MSG)




########################################
# ❌ Fill Blanks Test o'chirish       #
########################################
class DeleteFillBlanksTestStates(StatesGroup):
    topic_id = State()

@router.message(F.text == "❌ Fill Blanks Test o'chirish")
async def delete_fill_blanks_test(message: Message):
    try:
        if message.from_user.id != ADMIN_ID:
            return

        subjects = await subjects_service.get_all()
        if not subjects:
            await message.answer("Birorta fan kiritilmagan!", reply_markup=keyboards.admin_menu)
            return

        await message.answer(
            "O'chirmoqchi bo'lgan testning fanini tanlang:",
            reply_markup=keyboards.subjects_inline_keyboard(subjects, prefix="subject_for_fill_blanks_test_delete")
        )
    except Exception as e:
        logger.error(f"Error in delete_fill_blanks_test: {e}")
        await message.answer(const.ERROR_MSG)


@router.callback_query(F.data.startswith("subject_for_fill_blanks_test_delete:"))
async def handle_subject_for_fill_blanks_test_delete(callback: CallbackQuery):
    try:
        subject_id = int(callback.data.split(":")[1])
        classes = await classes_service.get_by_subject_id(subject_id)
        if not classes:
            await callback.answer("Bu fan uchun sinf yo'q!", show_alert=True)
            return

        await callback.message.edit_text(
            "Sinfni tanlang:",
            reply_markup=keyboards.classes_inline_keyboard(classes, prefix="class_for_fill_blanks_test_delete")
        )
    except Exception as e:
        logger.error(f"Error in handle_subject_for_fill_blanks_test_delete: {e}")
        await callback.answer(const.ERROR_MSG, show_alert=True)


@router.callback_query(F.data.startswith("class_for_fill_blanks_test_delete:"))
async def handle_class_for_fill_blanks_test_delete(callback: CallbackQuery):
    try:
        class_id = int(callback.data.split(":")[1])
        topics = await topics_service.get_by_class_id(class_id)
        if not topics:
            await callback.answer("Bu sinf uchun mavzular yo'q!", show_alert=True)
            return

        await callback.message.edit_text(
            "Mavzuni tanlang:",
            reply_markup=keyboards.topics_inline_keyboard(topics, prefix="topic_for_fill_blanks_test_delete")
        )
    except Exception as e:
        logger.error(f"Error in handle_class_for_fill_blanks_test_delete: {e}")
        await callback.answer(const.ERROR_MSG, show_alert=True)


@router.callback_query(F.data.startswith("topic_for_fill_blanks_test_delete:"))
async def handle_topic_for_fill_blanks_test_delete(callback: CallbackQuery):
    try:
        topic_id = int(callback.data.split(":")[1])

        count = await fill_blanks_tests_service.count_by_topic_id(topic_id)
        if count == 0:
            await callback.answer("Bu mavzu uchun testlar yo'q!", show_alert=True)
            return

        await callback.message.edit_text(
            f"Ushbu mavzu uchun {count} ta FillBlanksTest test topildi.\n"
            f"Ularni o'chirishni tasdiqlaysizmi?",
            reply_markup=keyboards.yes_no_inline_keyboard(yes_data=f"confirm_fill_blanks_test_delete:{topic_id}", no_data="cancel_fill_blanks_test_delete")
        )
    except Exception as e:
        logger.error(f"Error in handle_topic_for_fill_blanks_test_delete: {e}")
        await callback.answer(const.ERROR_MSG, show_alert=True)


@router.callback_query(F.data.startswith("confirm_fill_blanks_test_delete:"))
async def confirm_fill_blanks_test_delete(callback: CallbackQuery):
    try:
        topic_id = int(callback.data.split(":")[1])
        deleted = await fill_blanks_tests_service.delete_by_topic_id(topic_id)
        await callback.message.edit_text(f"✅ {deleted} ta FillBlanksTest test o'chirildi.")

    except Exception as e:
        logger.error(f"Error in confirm_fill_blanks_test_delete: {e}")
        await callback.answer(const.ERROR_MSG, show_alert=True)

@router.callback_query(F.data == "cancel_fill_blanks_test_delete")
async def cancel_fill_blanks_test_delete(callback: CallbackQuery):
    try:
        await callback.message.edit_text("❌ O'chirish bekor qilindi.")
    except Exception as e:
        logger.error(f"Error in cancel_fill_blanks_test_delete: {e}")
        await callback.answer(const.ERROR_MSG, show_alert=True)


###################################
# 👑  Premium berish
#################################
class AdminPremiumStates(StatesGroup):
    waiting_for_user_id = State()
    waiting_for_days = State()

@router.message(F.text == "👑 Premium berish")
async def make_user_premium(message: Message, state: FSMContext):
    try:
        user_id = message.from_user.id
        if user_id != ADMIN_ID: return
        
        await state.set_state(AdminPremiumStates.waiting_for_user_id)
        await message.answer("Premimum bermoqchi bo'lgan foydalanuvchini ID'sini kiriting: ", reply_markup=keyboards.back)
    except Exception as e:
        logger.error(f"Error in make_user_premium: {e}")
        await message.answer(const.ERROR_MSG)

@router.message(AdminPremiumStates.waiting_for_user_id)
async def handle_user_id_for_premium(message: Message, state: FSMContext):
    try:
        user_id = int(message.text.strip())
        await state.update_data(user_id=user_id)
        await state.set_state(AdminPremiumStates.waiting_for_days)
        await message.answer("Qancha kunga premium bermoqchisiz?")
    except Exception as e:
        logger.error(f"Error in handle_user_id_for_premium: {e}")
        await message.answer(const.ERROR_MSG)

@router.message(AdminPremiumStates.waiting_for_days)
async def handle_days_for_premium(message: Message, state: FSMContext):
    try:
        days = int(message.text.strip())
        data = await state.get_data()

        user_id = data['user_id']
        user = await user_service.get_by_id(user_id)
        if not user:
            await message.answer("Ushbu ID bilan foydalanuvchi topilmadi!")
            return
        
        now = datetime.now(timezone.utc)
        if user.premium_expiry_at and user.premium_expiry_at > now:
            new_expiry = user.premium_expiry_at + timedelta(days=days)
        else:
            new_expiry = now + timedelta(days=days)
        
        user.is_premium = True
        user.premium_expiry_at = new_expiry
        
        await user_service.update(user=user)

        await message.answer(
            f"✅ Foydalanuvchi {user_id} ga premium {days} kun qo'shildi.\n📅 Tugash: {new_expiry.strftime('%Y-%m-%d %H:%M')} UTC",
            reply_markup=keyboards.admin_menu
        )   

        await state.clear()
        
    except Exception as e:
        logger.error(f"Error in handle_days_for_premium: {e}")
        await message.answer(const.ERROR_MSG)
