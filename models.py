class User:
    def __init__(
        self,
        id=None,
        first_name=None,
        last_name=None,
        username=None,
        is_premium=False,
        premium_expiry_at=None,
        total_score=0
    ):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.is_premium = is_premium
        self.premium_expiry_at = premium_expiry_at
        self.total_score = total_score

class Subject:
    def __init__(self, id=None, name=None):
        self.id = id
        self.name = name

class Class:
    def __init__(self, id=None, name=None, subject_id=None):
        self.id = id
        self.name = name
        self.subject_id = subject_id

class Topic:
    def __init__(self, id=None, name=None, class_id=None):
        self.id = id
        self.name = name
        self.class_id = class_id

class VideoLesson:
    def __init__(self, id=None, file_id=None, topic_id=None):
        self.id = id
        self.file_id = file_id
        self.topic_id = topic_id

class AudioLesson:
    def __init__(self, id=None, file_id=None, topic_id=None):
        self.id = id
        self.file_id = file_id
        self.topic_id = topic_id

class PDFMaterial:
    def __init__(self, id=None, file_id=None, topic_id=None):
        self.id = id
        self.file_id = file_id
        self.topic_id = topic_id


class Test:
    def __init__(self, id=None, question=None, image_id=None, topic_id=None):
        self.id = id
        self.question = question
        self.image_id = image_id
        self.topic_id = topic_id

class TestOption:
    def __init__(self, id=None, option=None, is_correct=None, test_id=None):
        self.id = id
        self.option = option
        self.is_correct = is_correct
        self.test_id = test_id

class FillBlanksTest:
    def __init__(self, id=None, text=None, topic_id=None):
        self.id = id
        self.text = text
        self.topic_id = topic_id

class FillBlanksTestAnswer:
    def __init__(self, id=None, fill_blanks_test_id=None, number=None, answer=None):
        self.id = id
        self.fill_blanks_test_id = fill_blanks_test_id
        self.number = number
        self.answer = answer

class UserAnswersTestContainer:
    def __init__(self, id=None, user_id=None, is_finished=False, got_score=False):
        self.id = id
        self.user_id = user_id
        self.is_finished = is_finished
        self.got_score = got_score

class UserAnswersTest:
    def __init__(
        self,
        id=None,
        user_answers_test_container_id=None,
        test_id=None,
        selected_option_id=None,
        was_correct=None
    ):
        self.id = id
        self.user_answers_test_container_id = user_answers_test_container_id
        self.test_id = test_id
        self.selected_option_id = selected_option_id
        self.was_correct = was_correct

class UserAnswersFillBlanksTestContainer:
    def __init__(self, id=None, user_id=None, is_finished=False, got_score=False):
        self.id = id
        self.user_id = user_id
        self.is_finished = is_finished
        self.got_score = got_score

class UserAnswersFillBlanksTest:
    def __init__(
        self,
        id=None,
        user_answers_fill_blanks_test_container_id=None,
        fill_blanks_test_id=None,
        number=None,
        answer=None,
        was_correct=None
    ):
        self.id = id
        self.user_answers_fill_blanks_test_container_id = user_answers_fill_blanks_test_container_id
        self.fill_blanks_test_id = fill_blanks_test_id
        self.number = number
        self.answer = answer
        self.was_correct = was_correct

class Fight:
    def __init__(
        self,
        id=None,
        user_id=None,
        is_finished=False
    ):
        self.id = id
        self.user_id = user_id
        self.is_finished = is_finished

class FightTest:
    def __init__(
        self,
        id=None,
        fight_id=None,
        test_id=None
    ):
        self.id = id
        self.fight_id = fight_id
        self.test_id = test_id


class FightFillBlank:
    def __init__(
        self,
        id=None,
        fight_id=None,
        fill_blanks_test_id=None
    ):
        self.id = id
        self.fight_id = fight_id
        self.fill_blanks_test_id = fill_blanks_test_id

class Participant:
    def __init__(
        self,
        id=None,
        user_id=None,
        fight_id=None
    ):
        self.id = id
        self.user_id = user_id
        self.fight_id = fight_id

class UserContext:
    def __init__(
        self,
        id=None,
        user_id=None,
        selected_subject_id=None,
        selected_class_id=None,
        selected_topic_id=None
    ):
        self.id = id
        self.user_id = user_id
        self.selected_subject_id = selected_subject_id
        self.selected_class_id = selected_class_id
        self.selected_topic_id = selected_topic_id

class Channel:
    def __init__(self, id=None, username=None, link=None):
        self.id = id
        self.username = username
        self.link = link

class GotScore:
    def __init__(self, id=None, user_id=None, topic_id=None, test_type=None):
        self.id = id
        self.user_id = user_id
        self.topic_id = topic_id
        self.test_type = test_type


class FightTestContainer:
    def __init__(self, id=None, user_id=None, fight_id=None, test_container_id=None):
        self.id = id
        self.user_id = user_id
        self.fight_id = fight_id
        self.test_container_id = test_container_id

class FightFillBlanksContainer:
    def __init__(self, id=None, user_id=None, fight_id=None, fill_blanks_container_id=None):
        self.id = id
        self.user_id = user_id
        self.fight_id = fight_id
        self.fill_blanks_container_id = fill_blanks_container_id
