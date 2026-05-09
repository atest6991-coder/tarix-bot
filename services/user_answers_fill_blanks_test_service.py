import db
from models import UserAnswersFillBlanksTest
from logger import logger

TABLE_NAME = "user_answers_fill_blanks_test"

async def get_all():
    conn = await db.get_db_connection()
    query = f"SELECT * FROM {TABLE_NAME}"
    try:
        rows = await conn.fetch(query)
        return [UserAnswersFillBlanksTest(
            id=row["id"],
            user_answers_fill_blanks_test_container_id=row["user_answers_fill_blanks_test_container_id"],
            fill_blanks_test_id=row["fill_blanks_test_id"],
            number=row["number"],
            answer=row["answer"],
            was_correct=row["was_correct"]
        ) for row in rows]
    except Exception as e:
        logger.error(f"Error fetching all user_answers_fill_blanks_test: {e}")
        return []
    finally:
        await conn.close()

async def get_by_container(container_id: int):
    conn = await db.get_db_connection()
    query = f"SELECT * FROM {TABLE_NAME} where user_answers_fill_blanks_test_container_id = $1"
    try:
        rows = await conn.fetch(query, container_id)
        return [UserAnswersFillBlanksTest(
            id=row["id"],
            user_answers_fill_blanks_test_container_id=row["user_answers_fill_blanks_test_container_id"],
            fill_blanks_test_id=row["fill_blanks_test_id"],
            number=row["number"],
            answer=row["answer"],
            was_correct=row["was_correct"]
        ) for row in rows]
    except Exception as e:
        logger.error(f"Error fetching all user_answers_fill_blanks_test by container id: {e}")
        return []
    finally:
        await conn.close()

async def get_by_container_and_test(container_id: int, test_id: int):
    conn = await db.get_db_connection()
    query = f"SELECT * FROM {TABLE_NAME} where user_answers_fill_blanks_test_container_id = $1 AND fill_blanks_test_id = $2"
    try:
        rows = await conn.fetch(query, container_id, test_id)
        return [UserAnswersFillBlanksTest(
            id=row["id"],
            user_answers_fill_blanks_test_container_id=row["user_answers_fill_blanks_test_container_id"],
            fill_blanks_test_id=row["fill_blanks_test_id"],
            number=row["number"],
            answer=row["answer"],
            was_correct=row["was_correct"]
        ) for row in rows]
    except Exception as e:
        logger.error(f"Error fetching all user_answers_fill_blanks_test by container and test: {e}")
        return []
    finally:
        await conn.close()

async def get_by_id(id: int):
    conn = await db.get_db_connection()
    query = f"SELECT * FROM {TABLE_NAME} WHERE id = $1"
    try:
        row = await conn.fetchrow(query, id)
        if not row:
            logger.info(f"No user_answers_fill_blanks_test found with id = {id}")
            return None
        return UserAnswersFillBlanksTest(
            id=row["id"],
            user_answers_fill_blanks_test_container_id=row["user_answers_fill_blanks_test_container_id"],
            fill_blanks_test_id=row["fill_blanks_test_id"],
            number=row["number"],
            answer=row["answer"],
            was_correct=row["was_correct"]
        )
    except Exception as e:
        logger.error(f"Error fetching user_answers_fill_blanks_test by ID: {e}")
        return None
    finally:
        await conn.close()

async def create(answer: UserAnswersFillBlanksTest):
    conn = await db.get_db_connection()
    query = f"""
        INSERT INTO {TABLE_NAME} (
            user_answers_fill_blanks_test_container_id,
            fill_blanks_test_id,
            number,
            answer,
            was_correct
        ) VALUES ($1, $2, $3, $4, $5)
    """
    try:
        await conn.execute(
            query,
            answer.user_answers_fill_blanks_test_container_id,
            answer.fill_blanks_test_id,
            answer.number,
            answer.answer,
            answer.was_correct
        )
    except Exception as e:
        logger.error(f"Error creating user_answers_fill_blanks_test: {e}")
    finally:
        await conn.close()

async def update(answer: UserAnswersFillBlanksTest):
    conn = await db.get_db_connection()
    query = f"""
        UPDATE {TABLE_NAME}
        SET
            user_answers_fill_blanks_test_container_id = $1,
            fill_blanks_test_id = $2,
            number = $3,
            answer = $4,
            was_correct = $5
        WHERE id = $6
    """
    try:
        await conn.execute(
            query,
            answer.user_answers_fill_blanks_test_container_id,
            answer.fill_blanks_test_id,
            answer.number,
            answer.answer,
            answer.was_correct,
            answer.id
        )
    except Exception as e:
        logger.error(f"Error updating user_answers_fill_blanks_test: {e}")
    finally:
        await conn.close()

async def delete_by_id(id: int):
    conn = await db.get_db_connection()
    query = f"DELETE FROM {TABLE_NAME} WHERE id = $1"
    try:
        await conn.execute(query, id)
        logger.info(f"Deleted user_answers_fill_blanks_test with id = {id}")
    except Exception as e:
        logger.error(f"Error deleting user_answers_fill_blanks_test: {e}")
    finally:
        await conn.close()
