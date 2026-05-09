import db
from models import UserAnswersFillBlanksTestContainer
from logger import logger

TABLE_NAME = "user_answers_fill_blanks_test_containers"
TABLE_USER_ANSWERS_FILL_BLANKS_TEST = "user_answers_fill_blanks_test"

class UserFillBlanksStatistics:
    def __init__(self, total: int, correct: int, percent: float):
        self.total = total
        self.correct = correct
        self.percent = percent


async def get_all():
    conn = await db.get_db_connection()
    query = f"SELECT * FROM {TABLE_NAME}"
    try:
        rows = await conn.fetch(query)
        return [UserAnswersFillBlanksTestContainer(
            id=row["id"],
            user_id=row["user_id"],
            is_finished=row["is_finished"],
            got_score=row["got_score"]
        ) for row in rows]
    except Exception as e:
        logger.error(f"Error fetching all user_answers_fill_blanks_test_containers: {e}")
        return []
    finally:
        await conn.close()


async def get_by_id(id: int):
    conn = await db.get_db_connection()
    query = f"SELECT * FROM {TABLE_NAME} WHERE id = $1"
    try:
        row = await conn.fetchrow(query, id)
        if not row:
            logger.info(f"No user_answers_fill_blanks_test_container found with id = {id}")
            return None
        return UserAnswersFillBlanksTestContainer(
            id=row["id"],
            user_id=row["user_id"],
            is_finished=row["is_finished"],
            got_score=row["got_score"]
        )
    except Exception as e:
        logger.error(f"Error fetching user_answers_fill_blanks_test_container by ID: {e}")
        return None
    finally:
        await conn.close()

async def create(container: UserAnswersFillBlanksTestContainer):
    conn = await db.get_db_connection()
    query = f"""
        INSERT INTO {TABLE_NAME} (user_id, is_finished, got_score)
        VALUES ($1, $2, $3)
    """
    try:
        await conn.execute(query, container.user_id, container.is_finished, container.got_score)
    except Exception as e:
        logger.error(f"Error creating user_answers_fill_blanks_test_container: {e}")
    finally:
        await conn.close()

async def update(container: UserAnswersFillBlanksTestContainer):
    conn = await db.get_db_connection()
    query = f"""
        UPDATE {TABLE_NAME}
        SET user_id = $1,
            is_finished = $2,
            got_score = $3
        WHERE id = $4
    """
    try:
        await conn.execute(query, container.user_id, container.is_finished, container.got_score, container.id)
    except Exception as e:
        logger.error(f"Error updating user_answers_fill_blanks_test_container: {e}")
    finally:
        await conn.close()

async def delete_by_id(id: int):
    conn = await db.get_db_connection()
    query = f"DELETE FROM {TABLE_NAME} WHERE id = $1"
    try:
        await conn.execute(query, id)
        logger.info(f"Deleted user_answers_fill_blanks_test_container with id = {id}")
    except Exception as e:
        logger.error(f"Error deleting user_answers_fill_blanks_test_container: {e}")
    finally:
        await conn.close()

async def create(container: UserAnswersFillBlanksTestContainer) -> int:
    conn = await db.get_db_connection()
    row = await conn.fetchrow(f"""
        INSERT INTO {TABLE_NAME} (user_id)
        VALUES ($1)
        RETURNING id
    """, container.user_id)
    await conn.close()
    return row["id"]

async def mark_finished(container_id: int):
    conn = await db.get_db_connection()
    await conn.execute(f"""
        UPDATE {TABLE_NAME}
        SET is_finished = TRUE
        WHERE id = $1
    """, container_id)
    await conn.close()

async def get_statistics(container_id: int) -> UserFillBlanksStatistics:
    conn = await db.get_db_connection()
    total_row = await conn.fetchrow(f"""
        SELECT COUNT(*) AS total FROM {TABLE_USER_ANSWERS_FILL_BLANKS_TEST}
        WHERE user_answers_fill_blanks_test_container_id = $1
    """, container_id)
    correct_row = await conn.fetchrow(f"""
        SELECT COUNT(*) AS correct FROM {TABLE_USER_ANSWERS_FILL_BLANKS_TEST}
        WHERE user_answers_fill_blanks_test_container_id = $1 AND was_correct = TRUE
    """, container_id)
    await conn.close()
    total = total_row["total"]
    correct = correct_row["correct"]
    percent = round(correct / total * 100, 2) if total > 0 else 0
    return UserFillBlanksStatistics(total=total, correct=correct, percent=percent)

