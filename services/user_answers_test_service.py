import db
from models import UserAnswersTest
from logger import logger

TABLE_NAME = "user_answers_test"

async def get_all():
    conn = await db.get_db_connection()
    query = f"SELECT * FROM {TABLE_NAME}"
    try:
        rows = await conn.fetch(query)
        return [UserAnswersTest(
            id=row["id"],
            user_answers_test_container_id=row["user_answers_test_container_id"],
            test_id=row["test_id"],
            selected_option_id=row["selected_option_id"],
            was_correct=row["was_correct"]
        ) for row in rows]
    except Exception as e:
        logger.error(f"Error fetching all user_answers_test: {e}")
        return []
    finally:
        await conn.close()

async def get_by_id(id: int):
    conn = await db.get_db_connection()
    query = f"SELECT * FROM {TABLE_NAME} WHERE id = $1"
    try:
        row = await conn.fetchrow(query, id)
        if not row:
            logger.info(f"No user_answers_test found with id = {id}")
            return None
        return UserAnswersTest(
            id=row["id"],
            user_answers_test_container_id=row["user_answers_test_container_id"],
            test_id=row["test_id"],
            selected_option_id=row["selected_option_id"],
            was_correct=row["was_correct"]
        )
    except Exception as e:
        logger.error(f"Error fetching user_answers_test by ID: {e}")
        return None
    finally:
        await conn.close()

async def create(answer: UserAnswersTest):
    conn = await db.get_db_connection()
    query = f"""
        INSERT INTO {TABLE_NAME} (
            user_answers_test_container_id,
            test_id,
            selected_option_id,
            was_correct
        ) VALUES ($1, $2, $3, $4)
    """
    try:
        await conn.execute(
            query,
            answer.user_answers_test_container_id,
            answer.test_id,
            answer.selected_option_id,
            answer.was_correct
        )
    except Exception as e:
        logger.error(f"Error creating user_answers_test: {e}")
    finally:
        await conn.close()

async def update(answer: UserAnswersTest):
    conn = await db.get_db_connection()
    query = f"""
        UPDATE {TABLE_NAME}
        SET
            user_answers_test_container_id = $1,
            test_id = $2,
            selected_option_id = $3,
            was_correct = $4
        WHERE id = $5
    """
    try:
        await conn.execute(
            query,
            answer.user_answers_test_container_id,
            answer.test_id,
            answer.selected_option_id,
            answer.was_correct,
            answer.id
        )
    except Exception as e:
        logger.error(f"Error updating user_answers_test: {e}")
    finally:
        await conn.close()

async def delete_by_id(id: int):
    conn = await db.get_db_connection()
    query = f"DELETE FROM {TABLE_NAME} WHERE id = $1"
    try:
        await conn.execute(query, id)
        logger.info(f"Deleted user_answers_test with id = {id}")
    except Exception as e:
        logger.error(f"Error deleting user_answers_test: {e}")
    finally:
        await conn.close()

# user_answers_test_service.py

async def create(container_id: int, test_id: int, selected_option_id: int, was_correct: bool):
    conn = await db.get_db_connection()
    try:
        query = f"""
            INSERT INTO {TABLE_NAME}
            (user_answers_test_container_id, test_id, selected_option_id, was_correct)
            VALUES ($1, $2, $3, $4)
        """
        await conn.execute(query, container_id, test_id, selected_option_id, was_correct)
    except Exception as e:
        logger.error(f"❌ Error in user_answers_test_service.create: {e}")
    finally:
        await conn.close()

class UserTestStats:
    def __init__(self, total: int, correct: int, incorrect: int):
        self.total = total
        self.correct = correct
        self.incorrect = incorrect
        self.percent = round((correct / total) * 100, 2) if total else 0

async def get_statistics(container_id: int) -> UserTestStats:
    conn = await db.get_db_connection()
    try:
        query = f"""
            SELECT
                COUNT(*) AS total,
                SUM(CASE WHEN was_correct THEN 1 ELSE 0 END) AS correct
            FROM {TABLE_NAME}
            WHERE user_answers_test_container_id = $1
        """
        row = await conn.fetchrow(query, container_id)
        total = row["total"] or 0
        correct = row["correct"] or 0
        incorrect = total - correct
        return UserTestStats(total=total, correct=correct, incorrect=incorrect)
    except Exception as e:
        logger.error(f"❌ Error in get_statistics: {e}")
        return UserTestStats(total=0, correct=0, incorrect=0)
    finally:
        await conn.close()


async def get_user_answers_by_container(container_id: int):
    conn = await db.get_db_connection()
    query = f"SELECT * FROM {TABLE_NAME} WHERE user_answers_test_container_id = $1"
    try:
        rows = await conn.fetch(query, container_id)
        return [UserAnswersTest(
            id=row["id"],
            user_answers_test_container_id=row["user_answers_test_container_id"],
            test_id=row["test_id"],
            selected_option_id=row["selected_option_id"],
            was_correct=row["was_correct"]
        ) for row in rows]
    except Exception as e:
        logger.error(f"Error fetching all user_answers_test by container id: {e}")
        return []
    finally:
        await conn.close()