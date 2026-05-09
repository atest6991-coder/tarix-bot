from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton, 
    InlineKeyboardButton, InlineKeyboardMarkup 
)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from models import Channel, Subject, Class, Topic, UserContext, TestOption
from services import (
    video_lessons_service,
    audio_lessons_service,
    pdf_materials_service,
    tests_service,
    fill_blanks_tests_service
)
from config import ADMIN as ADMIN_URL, BOT_USERNAME

main_menu = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [KeyboardButton(text="🧠 Fanlar")],
        [KeyboardButton(text="🛡️ Jang (Battle)"), KeyboardButton(text="🏆 Reyting")],
        [KeyboardButton(text="👤 Profil")]
    ]
)

admin_menu = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [KeyboardButton(text="➕ Kanal qo'shish"), KeyboardButton(text="➖ Kanal o'chirish"), KeyboardButton(text="📝 Kanallar")],
        [KeyboardButton(text="➕ Fan qo'shish"), KeyboardButton(text="➖ Fan o'chirish"), KeyboardButton(text="📝 Fanlar")],
        [KeyboardButton(text="➕ Sinf qo'shish"), KeyboardButton(text="➖ Sinf o'chirish"), KeyboardButton(text="📝 Sinflar")],
        [KeyboardButton(text="➕ Mavzu qo'shish"), KeyboardButton(text="➖ Mavzu o'chirish"), KeyboardButton(text="📝 Mavzular")],
        [KeyboardButton(text="➕ Video qo'shish"), KeyboardButton(text="➖ Video o'chirish"), KeyboardButton(text="📝 Video ko'rish")],
        [KeyboardButton(text="➕ Audio qo'shish"), KeyboardButton(text="➖ Audio o'chirish"), KeyboardButton(text="🎧 Audio ko'rish")],
        [KeyboardButton(text="➕ PDF qo'shish"), KeyboardButton(text="➖ PDF o'chirish"), KeyboardButton(text="📝 PDF ko'rish")],
        [KeyboardButton(text="⚙️ Parser test"), KeyboardButton(text="➕ Test qo'shish (word)")],
        [KeyboardButton(text="➕ Test qo'shish (rasmlik)"), KeyboardButton(text="❌ Test o'chirish")],
        [KeyboardButton(text="⚙️ Fill Blanks Parser test"), KeyboardButton(text="➕ Fill Blanks Test qo'shish (word)")],
        [KeyboardButton(text="❌ Fill Blanks Test o'chirish")],
        [KeyboardButton(text="👑 Premium berish")]
    ]
)

cancel = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [KeyboardButton(text="⬅️ Bekor qilish")]
    ]
)

cancel_inline = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_inline")]
    ]
)

back_menu = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [KeyboardButton(text="⬅️ Asosiy menyu")]
    ]
)

back = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [KeyboardButton(text="⬅️ Admin panel")]
    ]
)

skip = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [KeyboardButton(text="SKIP")]
    ]
)

def channels_inline_keyboard(channels: list[Channel]) -> InlineKeyboardMarkup:
    keyboard = []
    for channel in channels:
        keyboard.append([
            InlineKeyboardButton(
                text=channel.username,
                callback_data=f"delete_channel:{channel.id}"
            )]
        )
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    return markup

def confirm_delete_keyboard(channel_id: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Ha", callback_data=f"confirm_delete_channel:{channel_id}"),
            InlineKeyboardButton(text="❌ Yo'q", callback_data="cancel_delete")
        ]
    ])
    return keyboard

def subjects_inline_keyboard(subjects: list[Subject]) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=sub.name, callback_data=f"delete_subject:{sub.id}")]
        for sub in subjects
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def confirm_delete_subject_keyboard(subject_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Ha", callback_data=f"confirm_delete_subject:{subject_id}"),
                InlineKeyboardButton(text="❌ Yo'q", callback_data="cancel_delete_subject")
            ]
        ]
    )


def classes_inline_keyboard(classes, prefix="delete_class", include_back:bool = False, back_data:str = ''):
    buttons = [
        [InlineKeyboardButton(text=cls.name, callback_data=f"{prefix}:{cls.id}")]
        for cls in classes
    ]

    if include_back:
        buttons.append([InlineKeyboardButton(text="⬅️ Orqaga qaytish", callback_data=back_data)])

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def confirm_delete_class_keyboard(class_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Ha", callback_data=f"confirm_delete_class:{class_id}"),
            InlineKeyboardButton(text="❌ Yo'q", callback_data="cancel_delete_class")
        ]
    ])

def subjects_inline_keyboard(subjects, prefix="subject_select"):
    keyboard = InlineKeyboardBuilder()
    for subject in subjects:
        keyboard.button(
            text=subject.name,
            callback_data=f"{prefix}:{subject.id}"
        )
    keyboard.adjust(2)
    return keyboard.as_markup()


def topics_inline_keyboard(topics, prefix="topic_select"):
    keyboard = InlineKeyboardBuilder()
    for topic in topics:
        keyboard.button(
            text=topic.name,
            callback_data=f"{prefix}:{topic.id}"
        )
    keyboard.adjust(2)
    return keyboard.as_markup()

def confirm_delete_topic_keyboard(topic_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Ha", callback_data=f"confirm_delete_topic:{topic_id}"),
            InlineKeyboardButton(text="❌ Yo'q", callback_data="cancel_delete_topic")
        ]
    ])

def yes_no_inline_keyboard(yes_data, no_data):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Ha", callback_data=yes_data),
                InlineKeyboardButton(text="❌ Yo'q", callback_data=no_data)
            ]
        ]
    )

def create_subjects_keyboard(subjects: list[Subject], include_cancel=True):
    keyboard = []
    row = []

    for idx, subject in enumerate(subjects, start=1):
        row.append(KeyboardButton(text=subject.name))
        if len(row) == 2:  
            keyboard.append(row)
            row = []

    if row:  
        keyboard.append(row)

    if include_cancel:
        keyboard.append([KeyboardButton(text="⬅️ Bekor qilish")])

    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=keyboard)


def create_classes_keyboard(classes: list[Class], include_cancel=True):
    keyboard = []
    row = []

    for idx, _class in enumerate(classes, start=1):
        row.append(KeyboardButton(text=_class.name))
        if len(row) == 2:  
            keyboard.append(row)
            row = []

    if row:  
        keyboard.append(row)

    if include_cancel:
        keyboard.append([KeyboardButton(text="⬅️ Bekor qilish")])

    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=keyboard)

def create_topics_keyboard(topics: list[Topic], include_cancel=True):
    keyboard = []
    row = []

    for idx, topic in enumerate(topics, start=1):
        row.append(KeyboardButton(text=topic.name))
        if len(row) == 2:  
            keyboard.append(row)
            row = []

    if row:  
        keyboard.append(row)

    if include_cancel:
        keyboard.append([KeyboardButton(text="⬅️ Bekor qilish")])

    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=keyboard)


async def create_sources_keyboard(user_context: UserContext):
    keyboards = []
    topic_id = user_context.selected_topic_id

    video = await video_lessons_service.get_by_topic_id(topic_id=topic_id)
    if video:
        keyboards.append([KeyboardButton(text="🎥 Videodars")])
    
    audio = await audio_lessons_service.get_by_topic_id(topic_id=topic_id)
    if audio:
        keyboards.append([KeyboardButton(text="🎧 Audiodars")])
    
    pdf = await pdf_materials_service.get_by_topic_id(topic_id=topic_id)
    if pdf:
        keyboards.append([KeyboardButton(text="📄 PDF material")])

    tests = await tests_service.get_all_by_topic(topic_id=topic_id)
    if tests:
        keyboards.append([KeyboardButton(text="✅ Test")])
    
    fill_blanks = await fill_blanks_tests_service.get_all_by_topic(topic_id=topic_id)
    if fill_blanks:
        keyboards.append([KeyboardButton(text="✍️ Matnni to‘ldirish")])

    keyboards.append([KeyboardButton(text="⬅️ Bekor qilish")])

    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=keyboards)

def test_options_inline_keyboard(options: list[TestOption], prefix: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for option in options:  
        builder.button(
            text=option.option,
            callback_data=f"{prefix}:{option.id}"
        )
    builder.adjust(1)
    return builder.as_markup()


def numbers_inline_keyboard(numbers, prefix: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    # numbers = [10, 20, 30, 40, 50, 60]
    for n in numbers:
        builder.button(
            text=str(n),
            callback_data=f"{prefix}:{n}"
        )
    builder.adjust(3)  # 3 buttons per row
    return builder.as_markup()



def topics_multiselect_keyboard(
    topics: list[Topic],
    prefix: str,
    selected: list[int] = None,
    include_back: bool = False,
    include_done: bool = False,
    back_data: str = 'back_to_fight_classes',
    done_data: str = 'fight_topics_done'
) -> InlineKeyboardMarkup:
    """
    Create an inline keyboard for multiselecting topics with:
    ✅ toggle selection
    ✅ show ✅ in button if selected
    ✅ include back and done buttons if needed
    """
    builder = InlineKeyboardBuilder()
    selected = selected or []

    for topic in topics:
        is_selected = topic.id in selected
        text = f"{'✅ ' if is_selected else ''}{topic.name}"
        builder.button(
            text=text,
            callback_data=f"{prefix}:{topic.id}"
        )

    if include_back:
        builder.button(text="⬅️ Orqaga", callback_data=back_data)
    if include_done:
        builder.button(text="✅ Davom etish", callback_data=done_data)

    builder.adjust(1)

    return builder.as_markup()


# def fight_created_keyboard(fight_id: int) -> InlineKeyboardMarkup:
#     """
#     Generates a keyboard with:
#     - Share Fight Link
#     - Finish Fight (creator)
#     - Back to Main Menu
#     """

#     keyboard = InlineKeyboardMarkup(inline_keyboard=[
#         [
#             InlineKeyboardButton(
#                 text="📣 Jang havolasini ulashish",
#                 switch_inline_query=f"fight_{fight_id}"
#             )
#         ],
#         [
#             InlineKeyboardButton(
#                 text="🏁 Jangni yakunlash",
#                 callback_data=f"finish_fight:{fight_id}"
#             )
#         ]
#     ])

#     return keyboard

def fight_created_keyboard(fight_id: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        # [
        #     InlineKeyboardButton(
        #         text="📣 Jang linkini ulashish",
        #         url=f"https://t.me/{BOT_USERNAME}?start=fight_{fight_id}"
        #     )
        # ],
        [
            InlineKeyboardButton(
                text="🏁 Jangni yakunlash",
                callback_data=f"finish_fight:{fight_id}"
            )
        ]
    ])
    return keyboard


admin_url = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🧑‍💻 Admin bilan bo'glanish", url=ADMIN_URL)]
    ]
)