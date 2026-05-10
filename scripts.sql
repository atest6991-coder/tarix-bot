CREATE TABLE IF NOT EXISTS users
(
    id BIGINT NOT NULL PRIMARY KEY,
    first_name TEXT,
    last_name TEXT,
    username TEXT,
    is_premium BOOLEAN NOT NULL DEFAULT FALSE,
    premium_expiry_at  TIMESTAMP WITH TIME ZONE,
    total_score  INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS subjects
(
    id SERIAL NOT NULL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS classes
(
    id SERIAL NOT NULL PRIMARY KEY,
    name TEXT NOT NULL,
    subject_id INTEGER NOT NULL REFERENCES subjects(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS topics
(
    id SERIAL NOT NULL PRIMARY KEY,
    name TEXT NOT NULL,
    class_id INTEGER NOT NULL REFERENCES classes(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS video_lessons
(
    id SERIAL NOT NULL PRIMARY KEY,
    file_id TEXT NOT NULL,
    topic_id INTEGER NOT NULL REFERENCES topics(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS audio_lessons
(
    id SERIAL NOT NULL PRIMARY KEY,
    file_id TEXT NOT NULL,
    topic_id INTEGER NOT NULL REFERENCES topics(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS pdf_materials
(
    id SERIAL NOT NULL PRIMARY KEY,
    file_id TEXT NOT NULL,
    topic_id INTEGER NOT NULL REFERENCES topics(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS tests
(
    id SERIAL NOT NULL PRIMARY KEY,
    question TEXT NOT NULL,
    image_id TEXT, -- can be null
    topic_id INTEGER NOT NULL REFERENCES topics(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS test_options
(
    id SERIAL NOT NULL PRIMARY KEY,
    option TEXT NOT NULL,
    is_correct BOOLEAN NOT NULL,
    test_id INTEGER NOT NULL REFERENCES tests(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS fill_blanks_tests
(
    id SERIAL NOT NULL PRIMARY KEY,
    text TEXT NOT NULL,
    topic_id INTEGER NOT NULL REFERENCES topics(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS fill_blanks_test_answers
(
    id SERIAL NOT NULL PRIMARY KEY,
    fill_blanks_test_id INTEGER NOT NULL REFERENCES fill_blanks_tests(id) ON DELETE CASCADE,
    number VARCHAR(10) NOT NULL, -- like: 1, 2, 3,
    answer TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS user_answers_test_containers
(
    id SERIAL NOT NULL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id),
    is_finished BOOLEAN NOT NULL DEFAULT FALSE,
    got_score BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS user_answers_test
(
    id SERIAL NOT NULL PRIMARY KEY,
    user_answers_test_container_id INTEGER NOT NULL REFERENCES user_answers_test_containers(id),
    test_id INTEGER NOT NULL REFERENCES tests(id),
    selected_option_id INTEGER NOT NULL REFERENCES test_options(id),
    was_correct BOOLEAN NOT NULL
);

CREATE TABLE IF NOT EXISTS user_answers_fill_blanks_test_containers
(
    id SERIAL NOT NULL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id),
    is_finished BOOLEAN NOT NULL DEFAULT FALSE,
    got_score BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS user_answers_fill_blanks_test
(
    id SERIAL NOT NULL PRIMARY KEY,
    user_answers_fill_blanks_test_container_id INTEGER NOT NULL REFERENCES user_answers_fill_blanks_test_containers(id),
    fill_blanks_test_id INTEGER NOT NULL REFERENCES fill_blanks_tests(id),
    number VARCHAR(10) NOT NULL,
    answer TEXT NOT NULL,
    was_correct BOOLEAN NOT NULL
);

CREATE TABLE IF NOT EXISTS fights
(
    id SERIAL NOT NULL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id), -- creator
    is_finished BOOLEAN NOT NULL DEFAULT FALSE
);

-- ALTER TABLE fights ADD COLUMN topic_ids INTEGER[] NOT NULL;


CREATE TABLE IF NOT EXISTS fight_tests
(
    id SERIAL NOT NULL PRIMARY KEY,
    fight_id INTEGER NOT NULL REFERENCES fights(id),
    test_id INTEGER NOT NULL REFERENCES tests(id)
);

CREATE TABLE IF NOT EXISTS fight_fill_blanks
(
    id SERIAL NOT NULL PRIMARY KEY,
    fight_id INTEGER NOT NULL REFERENCES fights(id),
    fill_blanks_test_id INTEGER NOT NULL REFERENCES fill_blanks_tests(id)
);

CREATE TABLE IF NOT EXISTS participants 
(
    id SERIAL NOT NULL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id),
    fight_id INTEGER NOT NULL REFERENCES fights(id)
);

CREATE TABLE IF NOT EXISTS user_context
(
    id SERIAL NOT NULL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id),
    selected_subject_id INTEGER REFERENCES subjects(id),
    selected_class_id INTEGER REFERENCES classes(id),
    selected_topic_id INTEGER REFERENCES topics(id)
);

CREATE TABLE IF NOT EXISTS channels
(
    id SERIAL NOT NULL PRIMARY KEY,
    username TEXT NOT NULL,
    link TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS got_scores(
    id SERIAL NOT NULL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id),
    topic_id INTEGER NOT NULL REFERENCES topics(id),
    test_type TEXT NOT NULL -- 'test' or 'fillblanks'
);

CREATE TABLE IF NOT EXISTS user_daily_limits(
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id),
    action_type TEXT NOT NULL, -- 'test', 'fillblanks', 'fight'
    date DATE NOT NULL, -- day the action was performed
    UNIQUE(user_id, action_type, date)
);

CREATE TABLE IF NOT EXISTS fight_test_container(
    id SERIAL NOT NULL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    fight_id INTEGER NOT NULL,
    test_container_id INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS fight_fill_blanks_container(
    id SERIAL NOT NULL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    fight_id INTEGER NOT NULL,
    fill_blanks_container_id INTEGER NOT NULL
);

-- 1
ALTER TABLE user_answers_fill_blanks_test
DROP CONSTRAINT user_answers_fill_blanks_test_fill_blanks_test_id_fkey;

ALTER TABLE user_answers_fill_blanks_test
ADD CONSTRAINT user_answers_fill_blanks_test_fill_blanks_test_id_fkey
FOREIGN KEY (fill_blanks_test_id)
REFERENCES fill_blanks_tests(id)
ON DELETE CASCADE;


-- 2
ALTER TABLE fight_fill_blanks
DROP CONSTRAINT fight_fill_blanks_fill_blanks_test_id_fkey;

ALTER TABLE fight_fill_blanks
ADD CONSTRAINT fight_fill_blanks_fill_blanks_test_id_fkey
FOREIGN KEY (fill_blanks_test_id)
REFERENCES fill_blanks_tests(id)
ON DELETE CASCADE;


-- 
-- ALTER TABLES TO ADD ON DELETE CASCADE
--
-- user_answers_test_containers.user_id
ALTER TABLE user_answers_test_containers
    DROP CONSTRAINT user_answers_test_containers_user_id_fkey,
    ADD CONSTRAINT user_answers_test_containers_user_id_fkey
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- user_answers_test.user_answers_test_container_id
ALTER TABLE user_answers_test
    DROP CONSTRAINT user_answers_test_user_answers_test_container_id_fkey,
    ADD CONSTRAINT user_answers_test_user_answers_test_container_id_fkey
        FOREIGN KEY (user_answers_test_container_id) REFERENCES user_answers_test_containers(id) ON DELETE CASCADE;

-- user_answers_test.test_id
ALTER TABLE user_answers_test
    DROP CONSTRAINT user_answers_test_test_id_fkey,
    ADD CONSTRAINT user_answers_test_test_id_fkey
        FOREIGN KEY (test_id) REFERENCES tests(id) ON DELETE CASCADE;

-- user_answers_test.selected_option_id
ALTER TABLE user_answers_test
    DROP CONSTRAINT user_answers_test_selected_option_id_fkey,
    ADD CONSTRAINT user_answers_test_selected_option_id_fkey
        FOREIGN KEY (selected_option_id) REFERENCES test_options(id) ON DELETE CASCADE;

-- user_answers_fill_blanks_test_containers.user_id
ALTER TABLE user_answers_fill_blanks_test_containers
    DROP CONSTRAINT user_answers_fill_blanks_test_containers_user_id_fkey,
    ADD CONSTRAINT user_answers_fill_blanks_test_containers_user_id_fkey
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- user_answers_fill_blanks_test.user_answers_fill_blanks_test_container_id
ALTER TABLE user_answers_fill_blanks_test
    DROP CONSTRAINT user_answers_fill_blanks_test_user_answers_fill_blanks_tes_fkey,
    ADD CONSTRAINT user_answers_fill_blanks_test_user_answers_fill_blanks_tes_fkey
        FOREIGN KEY (user_answers_fill_blanks_test_container_id) REFERENCES user_answers_fill_blanks_test_containers(id) ON DELETE CASCADE;

-- user_answers_fill_blanks_test.fill_blanks_test_id
ALTER TABLE user_answers_fill_blanks_test
    DROP CONSTRAINT user_answers_fill_blanks_test_fill_blanks_test_id_fkey,
    ADD CONSTRAINT user_answers_fill_blanks_test_fill_blanks_test_id_fkey
        FOREIGN KEY (fill_blanks_test_id) REFERENCES fill_blanks_tests(id) ON DELETE CASCADE;

-- classes.subject_id
ALTER TABLE classes
    DROP CONSTRAINT classes_subject_id_fkey,
    ADD CONSTRAINT classes_subject_id_fkey
        FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE;

-- topics.class_id
ALTER TABLE topics
    DROP CONSTRAINT topics_class_id_fkey,
    ADD CONSTRAINT topics_class_id_fkey
        FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE;

-- video_lessons.topic_id
ALTER TABLE video_lessons
    DROP CONSTRAINT video_lessons_topic_id_fkey,
    ADD CONSTRAINT video_lessons_topic_id_fkey
        FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE;

-- audio_lessons.topic_id
ALTER TABLE audio_lessons
    DROP CONSTRAINT audio_lessons_topic_id_fkey,
    ADD CONSTRAINT audio_lessons_topic_id_fkey
        FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE;

-- pdf_materials.topic_id
ALTER TABLE pdf_materials
    DROP CONSTRAINT pdf_materials_topic_id_fkey,
    ADD CONSTRAINT pdf_materials_topic_id_fkey
        FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE;

-- tests.topic_id
ALTER TABLE tests
    DROP CONSTRAINT tests_topic_id_fkey,
    ADD CONSTRAINT tests_topic_id_fkey
        FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE;

-- test_options.test_id
ALTER TABLE test_options
    DROP CONSTRAINT test_options_test_id_fkey,
    ADD CONSTRAINT test_options_test_id_fkey
        FOREIGN KEY (test_id) REFERENCES tests(id) ON DELETE CASCADE;

-- fill_blanks_tests.topic_id
ALTER TABLE fill_blanks_tests
    DROP CONSTRAINT fill_blanks_tests_topic_id_fkey,
    ADD CONSTRAINT fill_blanks_tests_topic_id_fkey
        FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE;

-- fill_blanks_test_answers.fill_blanks_test_id
ALTER TABLE fill_blanks_test_answers
    DROP CONSTRAINT fill_blanks_test_answers_fill_blanks_test_id_fkey,
    ADD CONSTRAINT fill_blanks_test_answers_fill_blanks_test_id_fkey
        FOREIGN KEY (fill_blanks_test_id) REFERENCES fill_blanks_tests(id) ON DELETE CASCADE;

-- fights.user_id
ALTER TABLE fights
    DROP CONSTRAINT fights_user_id_fkey,
    ADD CONSTRAINT fights_user_id_fkey
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- fight_tests.fight_id
ALTER TABLE fight_tests
    DROP CONSTRAINT fight_tests_fight_id_fkey,
    ADD CONSTRAINT fight_tests_fight_id_fkey
        FOREIGN KEY (fight_id) REFERENCES fights(id) ON DELETE CASCADE;

-- fight_tests.test_id
ALTER TABLE fight_tests
    DROP CONSTRAINT fight_tests_test_id_fkey,
    ADD CONSTRAINT fight_tests_test_id_fkey
        FOREIGN KEY (test_id) REFERENCES tests(id) ON DELETE CASCADE;

-- fight_fill_blanks.fight_id
ALTER TABLE fight_fill_blanks
    DROP CONSTRAINT fight_fill_blanks_fight_id_fkey,
    ADD CONSTRAINT fight_fill_blanks_fight_id_fkey
        FOREIGN KEY (fight_id) REFERENCES fights(id) ON DELETE CASCADE;

-- fight_fill_blanks.fill_blanks_test_id
ALTER TABLE fight_fill_blanks
    DROP CONSTRAINT fight_fill_blanks_fill_blanks_test_id_fkey,
    ADD CONSTRAINT fight_fill_blanks_fill_blanks_test_id_fkey
        FOREIGN KEY (fill_blanks_test_id) REFERENCES fill_blanks_tests(id) ON DELETE CASCADE;

-- participants.user_id
ALTER TABLE participants
    DROP CONSTRAINT participants_user_id_fkey,
    ADD CONSTRAINT participants_user_id_fkey
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- participants.fight_id
ALTER TABLE participants
    DROP CONSTRAINT participants_fight_id_fkey,
    ADD CONSTRAINT participants_fight_id_fkey
        FOREIGN KEY (fight_id) REFERENCES fights(id) ON DELETE CASCADE;

-- got_scores.user_id
ALTER TABLE got_scores
    DROP CONSTRAINT got_scores_user_id_fkey,
    ADD CONSTRAINT got_scores_user_id_fkey
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- got_scores.topic_id
ALTER TABLE got_scores
    DROP CONSTRAINT got_scores_topic_id_fkey,
    ADD CONSTRAINT got_scores_topic_id_fkey
        FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE;

-- user_daily_limits.user_id
ALTER TABLE user_daily_limits
    DROP CONSTRAINT user_daily_limits_user_id_fkey,
    ADD CONSTRAINT user_daily_limits_user_id_fkey
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- user_context.user_id
ALTER TABLE user_context
    DROP CONSTRAINT user_context_user_id_fkey,
    ADD CONSTRAINT user_context_user_id_fkey
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- user_context.selected_subject_id
ALTER TABLE user_context
    DROP CONSTRAINT user_context_selected_subject_id_fkey,
    ADD CONSTRAINT user_context_selected_subject_id_fkey
        FOREIGN KEY (selected_subject_id) REFERENCES subjects(id) ON DELETE CASCADE;

-- user_context.selected_class_id
ALTER TABLE user_context
    DROP CONSTRAINT user_context_selected_class_id_fkey,
    ADD CONSTRAINT user_context_selected_class_id_fkey
        FOREIGN KEY (selected_class_id) REFERENCES classes(id) ON DELETE CASCADE;

-- user_context.selected_topic_id
ALTER TABLE user_context
    DROP CONSTRAINT user_context_selected_topic_id_fkey,
    ADD CONSTRAINT user_context_selected_topic_id_fkey
        FOREIGN KEY (selected_topic_id) REFERENCES topics(id) ON DELETE CASCADE;
