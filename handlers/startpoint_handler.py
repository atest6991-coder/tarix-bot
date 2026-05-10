from aiogram import Router, F
from aiogram.types import *
from logger import logger
import const
from aiogram.fsm.context import FSMContext
import keyboards
from services import (
    user_service,
    participants_service,
    fights_service,
    user_answers_test_containers_service,
    fight_tests_service,
    fight_fill_blanks_service,
    tests_service,
    test_options_service,
    fill_blanks_tests_service,
    user_answers_fill_blanks_test_containers_service,
    user_answers_test_service,
    user_answers_fill_blanks_test_service,
    fill_blanks_test_answers_service,
    fight_test_containers_service,
    fight_fill_blanks_containers_service
) 
from models import (
    User,
    Fight,
    Participant,
    UserAnswersTestContainer,
    FightTest,
    FightFillBlank,
    Test,
    TestOption,
    FillBlanksTest,
    FillBlanksTestAnswer,
    UserAnswersFillBlanksTestContainer,
    UserAnswersTest,
    FillBlanksTestAnswer,
    UserAnswersFillBlanksTest,
    FightTestContainer,
    FightFillBlanksContainer
)
import functions as fn
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime, timedelta, timezone

router = Router()

@router.message(F.text.startswith('/start'))
async def welcome(message: Message, state: FSMContext):
    try:
        start_info = message.text.split()
        user_id = message.from_user.id
        
        if len(start_info) <= 1:
            following_result = await fn.check_user_following(user_id=user_id)
            if not following_result:
                return

            maybe_user = await user_service.get_by_id(user_id)
            now = datetime.now(timezone.utc)
            new_expiry = now + timedelta(days=365)
            if not maybe_user:
                new_user = User(
                    id=user_id,
                    first_name=message.from_user.first_name,
                    last_name=message.from_user.last_name,
                    username=message.from_user.username,
                    is_premium=True,
                    premium_expiry_at=new_expiry
                )
                await user_service.create(new_user)
                await message.answer("Assalomu alaykum, botga xush kelibsiz.", reply_markup=keyboards.main_menu)
            else:
                await message.answer("Assalomu alaykum, siz bosh menyudasiz.", reply_markup=keyboards.main_menu)
        else:
            following_result = await fn.check_user_following(user_id=user_id)
            if not following_result:
                return
            
            if not start_info[1].strip().startswith("fight"):
                return
            
            fight_info = start_info[1].split("_")
            fight_id = int(fight_info[1])
            fight = await fights_service.get_by_id(fight_id)
            if not fight or fight.is_finished:
                await message.answer("Ushbu test ortiq faol emas!")
                return
            
            maybe_already_participant = await participants_service.get_by_user_and_fight_ids(user_id=user_id, fight_id=fight_id)
            if maybe_already_participant:
                await message.answer("Siz ushbu testda avval qatnashgansiz)")
                return
            
            new_participant = Participant(
                user_id=user_id,
                fight_id=fight_id
            )
            await participants_service.create(new_participant)
            await message.answer("🥳 Siz ushbu jang ga qo'shildingiz\n\nTest tez orada boshlanadi...")
            
            fight_tests = await fight_tests_service.get_all_by_fight_id(fight_id=fight_id)
            fight_fillblanks = await fight_fill_blanks_service.get_all_by_fight_id(fight_id=fight_id)
            
            test_container_id = await user_answers_test_containers_service.create(user_id=user_id)
            await fight_test_containers_service.create(FightTestContainer(
                user_id=user_id,
                fight_id=fight_id,
                test_container_id=test_container_id
            ))

            await state.update_data(
                fight_id=fight_id,
                user_id=user_id,
                test_container_id=test_container_id,
                fight_tests = [ftest.test_id for ftest in fight_tests],
                fight_fillblanks = [fll.fill_blanks_test_id for fll in fight_fillblanks],
                current = 0,
            )
            await send_next_test(message, state)


    except Exception as e:
        logger.error(f"Error in welcome: {e}")
        await message.answer(const.ERROR_MSG, reply_markup=keyboards.main_menu)

async def send_next_test(message: Message, state: FSMContext):
    data = await state.get_data()
    tests = data['fight_tests']
    current = data['current']

    if current >= len(tests):
        user_id = data['user_id']
        new_fillblank_container_id = await user_answers_fill_blanks_test_containers_service.create(
            UserAnswersFillBlanksTestContainer(
                user_id=user_id
            )
        )
        fight_id = data['fight_id']

        await fight_fill_blanks_containers_service.create(FightFillBlanksContainer(
           user_id=user_id,
           fight_id=fight_id,
           fill_blanks_container_id=new_fillblank_container_id
        ))

        await state.update_data(
            fill_blanks_test_container_id=new_fillblank_container_id,
            current = 0,
        )
        await send_next_fill_blanks(message, state)
        return

    test_id = tests[current]
    test = await tests_service.get_by_id(test_id)
    if not test:
        await message.answer("❌ Test topilmadi.")
        return
    test_options = await test_options_service.get_all_by_test_id(test_id=test_id)
    
    keyboard = keyboards.test_options_inline_keyboard(test_options, prefix=f"user_answer_fight:{test_id}")

    if test.image_id:
        await message.delete()
        await message.answer_photo(
            photo=test.image_id,
            caption=f"{current + 1}/{len(tests)}\n\n{test.question}",
            reply_markup=keyboard
        )
    else:
        await message.delete()
        await message.answer(
            text=f"{current + 1}/{len(tests)}\n\n{test.question}",
            reply_markup=keyboard
        )

@router.callback_query(F.data.startswith("user_answer_fight:"))
async def handle_user_test_answer_in_fight(callback: CallbackQuery, state: FSMContext):
    try:
        data = callback.data.split(":")
        test_id = int(data[1])
        selected_option_id = int(data[2])
        test_option = await test_options_service.get_by_id(selected_option_id)
        correct = test_option.is_correct if test_option else False
        
        state_data = await state.get_data()
        container_id = state_data['test_container_id']

        await user_answers_test_service.create(
            container_id=container_id,
            test_id=test_id,
            selected_option_id=selected_option_id,
            was_correct=correct
        )

        current_index = state_data.get('current', 0) + 1
        await state.update_data(current=current_index)

        await send_next_test(message=callback.message, state=state)

    except Exception as e:
        logger.error(f"Error in handle_user_test_answer_in_fight: {e}")
        await callback.answer(const.ERROR_MSG, show_alert=True)



class FightStates(StatesGroup):
    test = State()

async def send_next_fill_blanks(message: Message, state: FSMContext):
    data = await state.get_data()
    fill_blanks = data['fight_fillblanks']
    current = data['current']

    if current >= len(fill_blanks):
        await finish_fight(message, state)
        return

    fill_blank_test_id = fill_blanks[current]
    fill_blank_test = await fill_blanks_tests_service.get_by_id(fill_blank_test_id)
    if not fill_blank_test:
        await message.answer("Test topilmadi!")
        return
    
    await message.answer(
        f"✏️ Test {current+1}/{len(fill_blanks)}\n"
        "Javoblarni shu formatda yuboring:\n"
        "1. javob\n2. javob\n3. javob\n\n"
        f"<b>{fill_blank_test.text}</b>",
        parse_mode="HTML"
    )
    await state.set_state(FightStates.test)


@router.message(FightStates.test, F.text)
async def handle_fill_blanks_answers_in_fight(message: Message, state: FSMContext):
    try:
        data = await state.get_data()
        current = data['current']
        fill_blanks = data['fight_fillblanks']
        container_id = data['fill_blanks_test_container_id']

        test_id = fill_blanks[current]
        correct_answers = await fill_blanks_test_answers_service.get_by_test_id(test_id=test_id)
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

        await message.answer(f"✅ Ajoyib!\nKeyingisiga o'tyapmiz...")
        data['current'] += 1
        await state.update_data(data)
        await send_next_fill_blanks(message=message, state=state)

    except Exception as e:
        logger.error(f"Error in handle_fill_blanks_answers_in_fight: {e}")
        await message.answer(const.ERROR_MSG)


async def finish_fight(message: Message, state: FSMContext):
    data = await state.get_data()
    test_container_id = data['test_container_id']
    user_id = data['user_id']
    
    await user_answers_test_containers_service.mark_finished(test_container_id)
    test_stats = await user_answers_test_service.get_statistics(test_container_id)

    # await message.answer(
    #     f"✅ Test tugadi!\n\n"
    #     f"Jami savollar: {test_stats.total}\n"
    #     f"To'g'ri javoblar: {test_stats.correct}\n"
    #     f"Noto'g'ri javoblar: {test_stats.incorrect}\n"
    #     f"Foiz: {test_stats.percent}%",
    #     reply_markup=keyboards.main_menu
    # )

    fill_blanks_container_id = data['fill_blanks_test_container_id']
    await user_answers_fill_blanks_test_containers_service.mark_finished(fill_blanks_container_id)
    fill_blanks_stats = await user_answers_fill_blanks_test_containers_service.get_statistics(fill_blanks_container_id)

    # await message.answer(
    #     f"✅ Fill blank test yakunlandi.\n"
    #     f"Umumiy: {fill_blanks_stats.total}\n"
    #     f"To'g'ri: {fill_blanks_stats.correct}\n"
    #     f"Foiz: {fill_blanks_stats.percent}%"
    # )

    total = test_stats.total + fill_blanks_stats.total
    correct = test_stats.correct + fill_blanks_stats.correct
    incorrect = test_stats.incorrect + (fill_blanks_stats.total - fill_blanks_stats.correct)
    await message.answer(
        f"🎊 Ajoyib, sizning natijangiz:\n"
        f"📚 Umumiy: {total}\n"
        f"✅ To'g'ri: {correct}\n"
        f"❌ Noto'g'ri: {incorrect}"
    )

    await state.clear()

