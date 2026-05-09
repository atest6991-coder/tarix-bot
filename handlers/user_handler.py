from aiogram import Router, F
from logger import logger
from services import(
    subjects_service,
    user_context_service,
    classes_service,
    topics_service,
    video_lessons_service,
    audio_lessons_service,
    pdf_materials_service,
    user_answers_test_containers_service,
    tests_service,
    user_answers_test_service,
    test_options_service,
    got_scores_service,
    user_service,
    fill_blanks_tests_service,
    user_answers_fill_blanks_test_containers_service,
    user_answers_fill_blanks_test_service,
    fill_blanks_test_answers_service,
    fights_service,
    participants_service,
    fight_test_containers_service,
    fight_fill_blanks_containers_service,
    user_limit_service
    
)
from models import(
    Subject,
    UserContext,
    Class,
    Topic,
    GotScore,
    User,
    UserAnswersFillBlanksTestContainer,
    UserAnswersFillBlanksTest,
    Fight,
    Participant,
    FightTestContainer,
    FightFillBlanksContainer
)
from aiogram.types import *
import const
import keyboards
import functions as fn
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from base import bot
from config import BOT_USERNAME
from datetime import datetime, timedelta, timezone
import asyncio

router = Router()

@router.message(F.text == "🧠 Fanlar")
async def show_subjects(message: Message):
    try:
        user_id = message.from_user.id
        following_result = await fn.check_user_following(user_id=user_id)
        if not following_result:
            return
        
        subjects = await subjects_service.get_all()
        if not subjects or len(subjects) == 0:
            await message.answer("Fanlar topilmadi!")

        await message.answer("Fanni tanlang: ", reply_markup=keyboards.create_subjects_keyboard(subjects=subjects))
    except Exception as e:
        logger.error(f"Erorr in show_subjects: {e}")
        await message.answer(const.ERROR_MSG)

@router.message(F.text == "🎥 Videodars")
async def send_video_lesson(message: Message):
    try:
        user_id = message.from_user.id
        following_result = await fn.check_user_following(user_id=user_id)
        if not following_result:
            return
        
        user_context = await user_context_service.get_by_user_id(user_id=user_id)
        if not user_context:
            return
        
        topic_id = user_context.selected_topic_id
        if not topic_id:
            return
        
        video = await video_lessons_service.get_by_topic_id(topic_id=topic_id)
        if not video:
            await message.answer("Ushbu mavzu uchun video dars topilmadi.")
            return
        
        await bot.send_video(
            chat_id=message.from_user.id,
            video=video.file_id
        )
    except Exception as e:
        logger.error(f"Error in send_video_lesson: {e}")
        await message.answer(const.ERROR_MSG)

@router.message(F.text == "🎧 Audiodars")
async def send_audio_lesson(message: Message):
    try:
        user_id = message.from_user.id
        following_result = await fn.check_user_following(user_id=user_id)
        if not following_result:
            return
        
        user_context = await user_context_service.get_by_user_id(user_id=user_id)
        if not user_context:
            return
        
        topic_id = user_context.selected_topic_id
        if not topic_id:
            return
        
        audio = await audio_lessons_service.get_by_topic_id(topic_id=topic_id)
        if not audio:
            await message.answer("Ushbu mavzu uchun audio dars topilmadi.")
            return
        
        await bot.send_audio(
            chat_id=message.from_user.id,
            audio=audio.file_id
        )
    except Exception as e:
        logger.error(f"Error in send_audio_lesson: {e}")
        await message.answer(const.ERROR_MSG)

@router.message(F.text == "📄 PDF material")
async def send_pdf_lesson(message: Message):
    try:
        user_id = message.from_user.id
        following_result = await fn.check_user_following(user_id=user_id)
        if not following_result:
            return
        
        user_context = await user_context_service.get_by_user_id(user_id=user_id)
        if not user_context:
            return
        
        topic_id = user_context.selected_topic_id
        if not topic_id:
            return
        
        pdf = await pdf_materials_service.get_by_topic_id(topic_id=topic_id)
        if not pdf:
            await message.answer("Ushbu mavzu uchun pdf  topilmadi.")
            return
        
        await bot.send_document(
            chat_id=message.from_user.id,
            document=pdf.file_id
        )
    except Exception as e:
        logger.error(f"Error in send_pdf_lesson: {e}")
        await message.answer(const.ERROR_MSG)

################################
# ✅ Test
###############################
class UserTestStates(StatesGroup):
    selecting_count = State()
    testing = State()

@router.message(F.text == "✅ Test")
async def user_test_start(message: Message, state: FSMContext):
    try:
        user_id = message.from_user.id
        following_result = await fn.check_user_following(user_id=user_id)
        if not following_result:
            return
        
        user = await user_service.get_by_id(user_id)
        if not await user_limit_service.check_daily_limit(user_id=user_id, action_type='test') and not user.is_premium:
            await message.answer(const.LIMIT, reply_markup=keyboards.admin_url)
            return
        
        await user_limit_service.mark_daily_limit(user_id=user_id, action_type='test')

        context = await user_context_service.get_by_user_id(user_id)
        topic_id = context.selected_topic_id if context else None

        if not topic_id:
            await message.answer("❌ Siz hali mavzu tanlamagansiz, iltimos mavzu tanlang.")
            return

        await state.update_data(topic_id=topic_id)
        await state.update_data(user_id=user_id)

        await state.set_state(UserTestStates.selecting_count)

        await message.answer(
            "Nechta savol ishlamoqchisiz?",
            reply_markup=keyboards.numbers_inline_keyboard([20, 30, 40, 50, 60, 70, 80, 90, 100], prefix="user_test_count")
        )
    except Exception as e:
        logger.error(f"Error in user_test_start: {e}")
        await message.answer(const.ERROR_MSG)

@router.callback_query(F.data.startswith("user_test_count:"))
async def handle_user_test_count(callback: CallbackQuery, state: FSMContext):
    try:
        count = int(callback.data.split(":")[1])
        data = await state.get_data()
        topic_id = data['topic_id']
        user_id = callback.from_user.id
        exist_tests = await tests_service.get_all_by_topic(topic_id=topic_id)
        if not exist_tests or len(exist_tests) < count:
            await callback.answer(f"Ushbu mavzu uchun barcha testlar soni: {len(exist_tests)}", show_alert=True)
            return

        # Fetch random tests
        tests = await tests_service.get_random_tests_by_topic(topic_id=topic_id, count=count)
        if not tests:
            await callback.message.edit_text("❌ Testlar topilmadi.")
            return

        # Create test container
        container_id = await user_answers_test_containers_service.create(user_id)

        # Store in state
        await state.update_data(
            container_id=container_id,
            tests=[test.id for test in tests],
            current_index=0,
            total=count
        )
        await state.set_state(UserTestStates.testing)

        await send_next_question(callback.message, state)

    except Exception as e:
        logger.error(f"Error in handle_user_test_count: {e}")
        await callback.answer(const.ERROR_MSG, show_alert=True)

async def send_next_question(message: Message, state: FSMContext):
    data = await state.get_data()
    current_index = data.get('current_index', 0)
    tests = data['tests']
    total = data['total']

    if current_index >= total:
        await finish_user_test(message, state)
        return

    test_id = tests[current_index]
    test = await tests_service.get_with_options_by_id(test_id)

    if not test:
        await message.answer("❌ Test topilmadi.")
        return

    keyboard = keyboards.test_options_inline_keyboard(test.options, prefix=f"user_answer:{test_id}")

    if test.image_id:
        await message.delete()
        await message.answer_photo(
            photo=test.image_id,
            caption=f"{current_index + 1}/{total}\n\n{test.question}",
            reply_markup=keyboard
        )
    else:
        if not message.photo:
            await message.edit_text(
                text=f"{current_index + 1}/{total}\n\n{test.question}",
                reply_markup=keyboard
            )
        else:
            await message.delete()
            await message.answer(
                text=f"{current_index + 1}/{total}\n\n{test.question}",
                reply_markup=keyboard
            )

    
@router.callback_query(F.data.startswith("user_answer:"))
async def handle_user_test_answer(callback: CallbackQuery, state: FSMContext):
    try:
        data = callback.data.split(":")
        test_id = int(data[1])
        selected_option_id = int(data[2])

        test_option = await test_options_service.get_by_id(selected_option_id)
        correct = test_option.is_correct if test_option else False

        state_data = await state.get_data()
        container_id = state_data['container_id']

        # Save user answer
        await user_answers_test_service.create(
            container_id=container_id,
            test_id=test_id,
            selected_option_id=selected_option_id,
            was_correct=correct
        )

        # Increment index
        current_index = state_data.get('current_index', 0) + 1
        await state.update_data(current_index=current_index)

        await send_next_question(callback.message, state)

    except Exception as e:
        logger.error(f"Error in handle_user_test_answer: {e}")
        await callback.answer(const.ERROR_MSG, show_alert=True)

async def finish_user_test(message: Message, state: FSMContext):
    await message.delete()
    data = await state.get_data()
    container_id = data['container_id']
    user_id = data['user_id']
    topic_id = data['topic_id']

    await user_answers_test_containers_service.mark_finished(container_id)

    stats = await user_answers_test_service.get_statistics(container_id)

    if stats.percent >= 80:
        new_score = 1 if 80 <= stats.percent and stats.percent <= 89 else 2 
        got_score = await got_scores_service.get_by_user_and_topic_and_test_type(user_id=user_id, topic_id=topic_id, test_type='test')
        if not got_score:
            new_got_score = GotScore(
                user_id=user_id,
                topic_id=topic_id,
                test_type='test'
            )
            await got_scores_service.create(new_got_score)

            user = await user_service.get_by_id(user_id)
            user.total_score += new_score
            await user_service.update(user=user)
            await message.answer(
                f"Siz birinchi martta bu testdan yuqori ball to'plaganingiz uchun {new_score} ballni qo'lga kiritdingiz 🥳")

    await message.answer(
        f"✅ Test tugadi!\n\n"
        f"Jami savollar: {stats.total}\n"
        f"To'g'ri javoblar: {stats.correct}\n"
        f"Noto'g'ri javoblar: {stats.incorrect}\n"
        f"Foiz: {stats.percent}%",
        reply_markup=keyboards.main_menu
    )

    test_analyze = "📊 Test tahlili:\n"
    user_answers = await user_answers_test_service.get_user_answers_by_container(container_id=container_id)
    err = 0
    count = 1

    for user_answer in user_answers:
        test = await tests_service.get_by_id(user_answer.test_id)
        if not test:
            logger.error("No test found in test_analyze")
            err += 1
            continue

        selected_test_option = await test_options_service.get_by_id(user_answer.selected_option_id)
        if not selected_test_option:
            logger.error(f"No selected option found for id = {user_answer.selected_option_id}")
            err += 1
            continue

        correct_option = await test_options_service.get_correct_option_by_test(test.id)
        if not correct_option:
            logger.error(f"No correct option found for test_id = {test.id}")
            err += 1
            continue

        test_analyze += (
            f"{count} {'✅' if selected_test_option.is_correct else '❌'}\n❓Savol: {test.question}\n"
            f"📍 Siz tanlagan variant: {selected_test_option.option}\n"
            f"☑️ To'g'ri javob: {correct_option.option}\n\n"
        )
        count += 1

    splitted_message = fn.split_message(test_analyze)
    for split in splitted_message:
        await message.answer(split)
        await asyncio.sleep(0.5)


    # await fn.send_long_message(bot=bot, chat_id=user_id, text=test_analyze, reply_markup=keyboards.main_menu)
    await state.clear()


##################################
# ✍️ Matnni to‘ldirish          #
##################################
class UserFillBlanksTestStates(StatesGroup):
    test = State()  # waiting user answers


@router.message(F.text == "✍️ Matnni to‘ldirish")
async def start_fill_blanks_test(message: Message, state: FSMContext):
    user_id = message.from_user.id
    following_result = await fn.check_user_following(user_id=user_id)
    if not following_result:
        return
    
    user = await user_service.get_by_id(user_id)

    if not await user_limit_service.check_daily_limit(user_id=user_id, action_type='fillblanks') and not user.is_premium:
        await message.answer(const.LIMIT, reply_markup=keyboards.admin_url)
        return
    
    await user_limit_service.mark_daily_limit(user_id=user_id, action_type='fillblanks')

    user_ctx = await user_context_service.get_by_user_id(user_id)
    topic_id = user_ctx.selected_topic_id

    tests = await fill_blanks_tests_service.get_by_topic_id(topic_id)
    if not tests:
        await message.answer("Ushbu mavzu uchun fill blank testlar mavjud emas.")
        return

    container = UserAnswersFillBlanksTestContainer(user_id=user_id)
    container_id = await user_answers_fill_blanks_test_containers_service.create(container)

    await state.update_data(
        container_id=container_id,
        tests=[t.id for t in tests],
        current=0,
        topic_id=topic_id
    )
    await send_next_fill_blanks_test(message, state)

async def send_next_fill_blanks_test(message: Message, state: FSMContext):
    data = await state.get_data()
    tests = data['tests']
    current = data['current']

    if current >= len(tests):
        await finish_fill_blanks_test(message, state)
        return

    test_id = tests[current]
    test = await fill_blanks_tests_service.get_by_id(test_id)

    await message.answer(
        f"✏️ Test {current+1}/{len(tests)}\n"
        "Javoblarni shu formatda yuboring:\n"
        "1. javob\n2. javob\n3. javob\n\n"
        f"<b>{test.text}</b>",
        parse_mode="HTML"
    )
    await state.set_state(UserFillBlanksTestStates.test)


@router.message(UserFillBlanksTestStates.test, F.text)
async def handle_fill_blanks_answers(message: Message, state: FSMContext):
    try:
        data = await state.get_data()
        current = data['current']
        tests = data['tests']
        container_id = data['container_id']

        test_id = tests[current]
        correct_answers = await fill_blanks_test_answers_service.get_by_test_id(test_id)

        user_answers_text = message.text.strip()
        lines = [line.strip() for line in user_answers_text.splitlines() if line.strip()]
        user_answers = {}
        for line in lines:
            if '.' in line:
                num, ans = line.split('.', 1)
                user_answers[num.strip()] = ans.strip().lower()

        correct_count = 0
        for ans in correct_answers:
            user_ans = user_answers.get(ans.number)
            is_correct = str(user_ans).lower() == ans.answer.lower()
            if is_correct:
                correct_count += 1

            await user_answers_fill_blanks_test_service.create(
                UserAnswersFillBlanksTest(
                    user_answers_fill_blanks_test_container_id=container_id,
                    fill_blanks_test_id=test_id,
                    number=ans.number,
                    answer=user_ans or "",
                    was_correct=is_correct
                )
            )

        # await message.answer(f"✅ {correct_count}/{len(correct_answers)} to'g'ri.\nKeyingisiga o'tyapmiz...")
        await message.answer(f"✅ Ajoyib!\nKeyingisiga o'tyapmiz...")

        data['current'] += 1
        await state.update_data(data)
        await send_next_fill_blanks_test(message, state)

    except Exception as e:
        logger.error(f"Error in handle_fill_blanks_answers: {e}")
        await message.answer(const.ERROR_MSG)

async def finish_fill_blanks_test(message: Message, state: FSMContext):
    data = await state.get_data()
    container_id = data['container_id']
    topic_id = data['topic_id']
    user_id = message.from_user.id

    await user_answers_fill_blanks_test_containers_service.mark_finished(container_id)

    stats = await user_answers_fill_blanks_test_containers_service.get_statistics(container_id)
    
    await message.answer(
        f"✅ Fill blank test yakunlandi.\n"
        f"Umumiy: {stats.total}\n"
        f"To'g'ri: {stats.correct}\n"
        f"Foiz: {stats.percent}%"
    )

    if stats.percent >= 80:
        new_score = 1 if 80 <= stats.percent and stats.percent <= 89 else 2 
        got_score = await got_scores_service.get_by_user_and_topic_and_test_type(user_id=user_id, topic_id=topic_id, test_type='fillblanks')
        if not got_score:
            new_got_score = GotScore(user_id=user_id, topic_id=topic_id, test_type='fillblanks')
            await got_scores_service.create(new_got_score)
            user = await user_service.get_by_id(user_id)
            user.total_score += new_score
            await user_service.update(user=user)
            await message.answer(f"Uchbu testdan yuqori ball olganingiz uchun {new_score} ball qo'lga kiritdingiz 🎊")


    text_message  = "📝 Test tahlili\n"
    counter = 1
    fill_blanks_tests = await fill_blanks_tests_service.get_all_by_topic(topic_id=topic_id)
    for test in fill_blanks_tests:
        text_message += f"{counter}.\n{test.text}\n\n"
        test_answers = await fill_blanks_test_answers_service.get_by_test_id(test_id=test.id)
        if not test_answers or len(test_answers) == 0:
            await message.answer(f"{test.text} uchun javoblar topilmadi, xatolik")
            return
        
        user_answers = await user_answers_fill_blanks_test_service.get_by_container_and_test(container_id=container_id, test_id=test.id)
        for test_answer in test_answers:
            user_answer = next((ans for ans in user_answers if ans.number == test_answer.number), None)
            if not user_answer or not user_answer.answer:
                text_message += f"{test_answer.number} ❌\nSizning javobingiz: Javob Berilmagan!\nTo'g'ri javob: {test_answer.answer}\n"
            elif user_answer.was_correct:
                text_message += f"{test_answer.number} ✅\nSizning javobingiz: {user_answer.answer}\nTo'g'ri javob: {test_answer.answer}\n"
            else:
                text_message += f"{test_answer.number} ❌\nSizning javobingiz: {user_answer.answer}\nTo'g'ri javob: {test_answer.answer}\n"

        text_message += "\n\n"
        counter += 1

    for part in fn.split_message(text_message):
        await message.answer(part)

    await state.clear()


########################
# 🛡️ Jang (Battle)    #
########################
class CreateFightStates(StatesGroup):
    select_subject = State()
    select_class = State()
    select_topics = State()
    fill_blanks = State()
    test_count = State()


@router.message(F.text == "🛡️ Jang (Battle)")
async def create_fight_start(message: Message, state: FSMContext):
    try:
        user_id = message.from_user.id
        user = await user_service.get_by_id(user_id)
    
        if not await user_limit_service.check_daily_limit(user_id=user_id, action_type='fight') and not user.is_premium:
            await message.answer(const.LIMIT, reply_markup=keyboards.admin_url)
            return
        
        await user_limit_service.mark_daily_limit(user_id=user_id, action_type='fight')

        subjects = await subjects_service.get_all()
        if not subjects:
            await message.answer("Fanlar topilmadi!", reply_markup=keyboards.main_menu)
            return

        await state.set_state(CreateFightStates.select_subject)
        await message.answer(
            "Fanlardan birini tanlang:",
            reply_markup=keyboards.subjects_inline_keyboard(subjects, prefix="fight_subject")
        )
    except Exception as e:
        logger.error(f"Error in create_fight_start: {e}")
        await message.answer(const.ERROR_MSG)

@router.callback_query(F.data.startswith("fight_subject:"))
async def handle_fight_subject_select(callback: CallbackQuery, state: FSMContext):
    try:
        subject_id = int(callback.data.split(":")[1])
        classes = await classes_service.get_by_subject_id(subject_id)
        if not classes:
            await callback.answer("Bu fan uchun sinflar topilmadi!", show_alert=True)
            return

        await state.update_data(subject_id=subject_id)
        await state.set_state(CreateFightStates.select_class)
        await callback.message.edit_text(
            "Sinflardan birini tanlang:",
            reply_markup=keyboards.classes_inline_keyboard(
                classes, 
                prefix="fight_class", 
                include_back=True,
                back_data='back_to_fight_subjects'
            )
        )
    except Exception as e:
        logger.error(f"Error in handle_fight_subject_select: {e}")
        await callback.answer(const.ERROR_MSG, show_alert=True)

@router.callback_query(F.data.startswith("fight_class:"))
async def handle_fight_class_select(callback: CallbackQuery, state: FSMContext):
    try:
        class_id = int(callback.data.split(":")[1])
        topics = await topics_service.get_by_class_id(class_id)
        if not topics:
            await callback.answer("Bu sinf uchun mavzular topilmadi!", show_alert=True)
            return

        await state.update_data(class_id=class_id)
        await state.set_state(CreateFightStates.select_topics)
        await callback.message.edit_text(
            "Mavzulardan birini yoki bir nechtasini tanlang, keyin '✅ Davom etish' tugmasini bosing:",
            reply_markup=keyboards.topics_multiselect_keyboard(
                topics, 
                prefix="fight_topic", 
                include_back=True, 
                include_done=True,
                back_data='back_to_fight_classes'
            )
        )
    except Exception as e:
        logger.error(f"Error in handle_fight_class_select: {e}")
        await callback.answer(const.ERROR_MSG, show_alert=True)

@router.callback_query(F.data.startswith("fight_topic:"))
async def handle_fight_topic_toggle(callback: CallbackQuery, state: FSMContext):
    try:
        topic_id = int(callback.data.split(":")[1])
        data = await state.get_data()
        selected_topics = data.get("selected_topics", [])

        if topic_id in selected_topics:
            selected_topics.remove(topic_id)
        else:
            selected_topics.append(topic_id)

        await state.update_data(selected_topics=selected_topics)

        class_id = data["class_id"]
        topics = await topics_service.get_by_class_id(class_id)
        await callback.message.edit_reply_markup(
            reply_markup=keyboards.topics_multiselect_keyboard(
                topics, 
                prefix="fight_topic", 
                selected=selected_topics, 
                include_back=True, 
                include_done=True
            )
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in handle_fight_topic_toggle: {e}")
        await callback.answer(const.ERROR_MSG)


@router.callback_query(F.data == "back_to_fight_classes")
async def back_to_fight_classes(callback: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        subject_id = data.get("subject_id")
        classes = await classes_service.get_by_subject_id(subject_id)
        await state.set_state(CreateFightStates.select_class)
        await callback.message.edit_text(
            "Sinflardan birini tanlang:",
            reply_markup=keyboards.classes_inline_keyboard(classes, prefix="fight_class", include_back=True, back_data="back_to_fight_subjects")
        )
    except Exception as e:
        logger.error(f"Error in back_to_fight_classes: {e}")
        await callback.answer(const.ERROR_MSG)

@router.callback_query(F.data == "back_to_fight_subjects")
async def back_to_fight_subjects(callback: CallbackQuery, state: FSMContext):
    try:
        subjects = await subjects_service.get_all()
        await state.set_state(CreateFightStates.select_subject)
        await callback.message.edit_text(
            "Fanlardan birini tanlang:",
            reply_markup=keyboards.subjects_inline_keyboard(subjects, prefix="fight_subject")
        )
    except Exception as e:
        logger.error(f"Error in back_to_fight_subjects: {e}")
        await callback.answer(const.ERROR_MSG)

@router.callback_query(F.data == "fight_topics_done")
async def handle_fight_topics_done(callback: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        selected_topics = data.get("selected_topics", [])
        if not selected_topics:
            await callback.answer("Iltimos, kamida bitta mavzu tanlang!", show_alert=True)
            return

        await state.update_data(selected_topics=selected_topics)
        await state.set_state(CreateFightStates.fill_blanks)
        
        await callback.message.edit_text(
            "Fill blanks testlarini qo'shishni xohlaysizmi?",
            reply_markup=keyboards.yes_no_inline_keyboard(
                yes_data="yes_include_fillblanks",
                no_data="no_include_fillblanks"
            )
        )
    except Exception as e:
        logger.error(f"Error in handle_fight_topics_done: {e}")
        await callback.answer(const.ERROR_MSG)

@router.callback_query(F.data == "yes_include_fillblanks")
async def handle_yes_include_fillblanks(callback: CallbackQuery, state: FSMContext):
    try:
        await state.update_data(include_fillblanks=True)
        await state.set_state(CreateFightStates.test_count)
        await callback.message.edit_text(
            text="Nechta test hohlaysiz?",
            reply_markup=keyboards.numbers_inline_keyboard([20, 30, 40, 50, 60, 70, 80, 90, 100], "test_count")
        )
    except Exception as e:
        logger.error(f"Error in handle_yes_include_fillblanks: {e}")
        await callback.answer(const.ERROR_MSG)

@router.callback_query(F.data == "no_include_fillblanks")
async def handle_no_include_fillblanks(callback: CallbackQuery, state: FSMContext):
    try:
        await state.update_data(include_fillblanks=False)
        await state.set_state(CreateFightStates.test_count)
        await callback.message.edit_text(
            text="Nechta test hohlaysiz?",
            reply_markup=keyboards.numbers_inline_keyboard([20, 30, 40, 50, 60, 70, 80, 90, 100], "test_count")
        )
    except Exception as e:
        logger.error(f"Error in handle_no_include_fillblanks: {e}")
        await callback.answer(const.ERROR_MSG)

@router.callback_query(F.data.startswith("test_count:"))
async def handle_test_count(callback: CallbackQuery, state: FSMContext):
    try:
        test_count = int(callback.data.split(":")[1])
        data = await state.get_data()

        user_id = callback.from_user.id
        topic_ids = data["selected_topics"]
        include_fillblanks = data["include_fillblanks"]

        # Create fight and assign tests
        fight_id = await fights_service.create_fight_and_assign_tests(
            user_id=user_id,
            selected_topic_ids=topic_ids,
            test_count=test_count,
            include_fillblanks=include_fillblanks
        )   

        fight_link = f"https://t.me/{BOT_USERNAME}?start=fight_{fight_id}"

        await callback.message.edit_text(
            text=(
                f"✅ Jang muvaffaqiyatli yaratildi!\n\n"
                f"Ulashish uchun jang havolasi:\n"
                f"*{fight_link}*\n\n"
                f"Har kim ushbu havola orqali jangga qo'shilib, testlarni ishlashi mumkin.\n"
                f"Siz jangni yakunlashni xohlaganingizda \"🛑 Jangni tugatish\" tugmasini bosishingiz mumkin."
            ),
            parse_mode="Markdown",
            reply_markup=keyboards.fight_created_keyboard(fight_id=fight_id)
        )

        await state.clear()

    except Exception as e:
        logger.error(f"Error in handle_test_count: {e}")
        await callback.answer(const.ERROR_MSG)

class UserStats:
    def __init__(self, user: User, correct: int, incorrect: int):
        self.user = user
        self.correct = correct
        self.incorrect = incorrect

@router.callback_query(F.data.startswith("finish_fight:"))
async def handle_stop_fight(callback: CallbackQuery, state: FSMContext):
    try:
        fight_id = int(callback.data.split(":")[1])
        fight = await fights_service.get_by_id(fight_id)
        if not fight:
            callback.answer("Bu jang topilmadi!", show_alert=True)
            return
        
        fight.is_finished = True
        await fights_service.update(fight=fight)
        await callback.message.delete()
        await callback.message.answer("Test yakunlandi ✅")
        
        stats = "📉 Jang natijalari\n"
        participants = await participants_service.get_all_by_fight_id(fight_id=fight_id)
        if not participants or len(participants) == 0:
            await callback.answer("Bu jangda hech kim qatnashmadi!", show_alert=True)
            return
        
       
        user_stats = []
        for participant in participants:
            user = await user_service.get_by_id(participant.user_id)
            test_container = await fight_test_containers_service.get_by_user_and_fight(participant.user_id, participant.fight_id)
            if not test_container:
                continue

            fill_blanks_container = await fight_fill_blanks_containers_service.get_by_user_and_fight(
                user_id=participant.user_id,
                fight_id=participant.fight_id
            )
            if not fill_blanks_container:
                continue

            test_stats = await user_answers_test_service.get_statistics(test_container.test_container_id)
            fill_blanks_stats = await user_answers_fill_blanks_test_containers_service.get_statistics(fill_blanks_container.fill_blanks_container_id)

            total = test_stats.total + fill_blanks_stats.total
            correct = test_stats.correct + fill_blanks_stats.correct
            incorrect = test_stats.incorrect + (fill_blanks_stats.total - fill_blanks_stats.correct)

            
            user_stats.append(UserStats(
                user=user,
                correct=correct,
                incorrect=incorrect
            ))

        if not user_stats:
            await callback.message.answer("Jangda hech kim testlarni yakunlamadi.")
            return

        user_stats.sort(reverse=True, key=lambda x: x.correct)

        count = 1
        for user_stat in user_stats:
            stats += f"{count}. {user_stat.user.first_name if user_stat.user.first_name else ''} {user_stat.user.last_name if user_stat.user.last_name else ''}\n"
            stats += f"✅ To'g'ri: {user_stat.correct}\n❌ Noto'g'ri: {user_stat.incorrect}\n\n"
            count += 1

        await bot.send_message(chat_id=callback.from_user.id, text=stats)
        
        for participant in participants:
            try:
                tg_user = await bot.get_chat(participant.user_id)
                if tg_user.type == "bot":
                    continue
                await bot.send_message(chat_id=participant.user_id, text=stats)
            except Exception as e:
                logger.warning(f"Could not send fight stats to user_id={participant.user_id}: {e}")


        winner = user_stats[0].user
        if not winner:
            return

        winner.total_score += 5
        await user_service.update(winner)
        await bot.send_message(winner.id, text=f"🥳 Siz jangda g'alaba qozonib, 5 ball ga ega bo'ldingiz") 

    except Exception as e:
        logger.error(f"Error in handle_stop_fight: {e}")
        await callback.answer(const.ERROR_MSG)

############################
# 👤 Profil
#############################
@router.message(F.text == "👤 Profil")
async def show_profile(message: Message):
    try:
        user_id = message.from_user.id
        user = await user_service.get_by_id(user_id)
        if not user:
            await message.answer("Foydalanuvchi malumotlari topilmadi!")
            return
        
        user_data = f"👤 Username: {'@' + user.username if user.username else 'yoq'}\n🎯 Umumiy ball: {user.total_score}\n"
        if user.is_premium:
            user_data += f"⭐️ Premium tugash sanasi: {user.premium_expiry_at.strftime('%Y-%m-%d')}"
        else:
            user_data += "❌ Sizda premium yo'q"

        await message.answer(user_data)

    except Exception as e:
        logger.error(f"Error in handle_stop_fight: {e}")
        await message.answer(const.ERROR_MSG)

############################
# 🏆 Reyting
#############################
@router.message(F.text == "🏆 Reyting")
async def send_rating(message: Message):
    try:
        top_users = await user_service.get_top_users(limit=5)
        user_id = message.from_user.id
        user = await user_service.get_by_id(user_id)
        user_rank = await user_service.get_user_rank(user_id)

        text = "🏆 Reyting\n\n"
        for idx, usr in enumerate(top_users, start=1):
            name = usr.first_name or usr.username or "Noma'lum"
            text += f"{idx}. {name} - {usr.total_score}\n"

        if user_rank > 5:
            text += f"\nSizning o'rningiz: {user_rank}. {user.first_name or user.username or 'Noma\'lum'} - {user.total_score}"

        await message.answer(text)

    except Exception as e:
        logger.error(f"Error in send_rating: {e}")
        await message.answer("❌ Reytingni chiqarishda xatolik yuz berdi.")


@router.message()
async def handle_subject_selection(message: Message):
    user_id = message.from_user.id

    # Check for subject
    subject_names = await fn.get_subjects_name()
    if message.text in subject_names:
        subject = await subjects_service.get_by_name(message.text)
        if subject:
            new_user_context = UserContext(selected_subject_id=subject.id, user_id=user_id)
            user_context = await user_context_service.get_by_user_id(user_id=user_id)
            if user_context:
               new_user_context.selected_class_id = user_context.selected_class_id
               new_user_context.selected_topic_id = user_context.selected_topic_id

            await user_context_service.create_or_update(new_user_context) 

            classes = await classes_service.get_by_subject_id(subject_id=subject.id)
            await message.answer(f"{subject.name} tanlandi ✅", reply_markup=keyboards.create_classes_keyboard(classes))
            return

    user_context = await user_context_service.get_by_user_id(user_id=user_id)
    if not user_context:
        return
    
    classes = await classes_service.get_by_subject_id(user_context.selected_subject_id)
    class_names = await fn.get_classes_name_by_classes(classes=classes)
    if message.text in class_names:
        _class = await classes_service.get_by_name_and_subject(message.text, user_context.selected_subject_id)
        if _class:
            new_user_context = UserContext(selected_class_id=_class.id, user_id=user_id)
            user_context = await user_context_service.get_by_user_id(user_id=user_id)
            if user_context:
                new_user_context.selected_topic_id = user_context.selected_topic_id
                new_user_context.selected_subject_id = user_context.selected_subject_id
            await user_context_service.create_or_update(new_user_context) 

            topics = await topics_service.get_by_class_id(_class.id)
            await message.answer(f"{_class.name} tanlandi: ", reply_markup=keyboards.create_topics_keyboard(topics=topics))
            return

    topics = await topics_service.get_by_class_id(user_context.selected_class_id)
    topics_name = await fn.get_topics_name_by_topics(topics=topics)
    if message.text in topics_name:
        topic = await topics_service.get_by_name_and_class(message.text, user_context.selected_class_id)
        if topic:
            new_user_context = UserContext(selected_topic_id=topic.id, user_id=user_id)
            user_context = await user_context_service.get_by_user_id(user_id=user_id)
            if user_context:
                new_user_context.selected_class_id = user_context.selected_class_id
                new_user_context.selected_subject_id = user_context.selected_subject_id
            
            await user_context_service.create_or_update(new_user_context) 
            waiting = await message.answer("⚙️ Menyu tayyorlanmoqda...")
            sources_keyboard = await keyboards.create_sources_keyboard(new_user_context)
            await waiting.delete()
            await message.answer("Ajoyib, o'zingizga kerakli manba ni tanlang", reply_markup=sources_keyboard)
            