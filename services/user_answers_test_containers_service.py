import db
from models import UserAnswersTestContainer
from logger import logger

TABLE_NAME = "user_answers_test_containers"

async def get_all():
    conn = await db.get_db_connection()
    query = f"SELECT * FROM {TABLE_NAME}"
    try:
        rows = await conn.fetch(query)
        return [UserAnswersTestContainer(
            id=row["id"],
            user_id=row["user_id"],
            is_finished=row["is_finished"],
            got_score=row["got_score"]
        ) for row in rows]
    except Exception as e:
        logger.error(f"Error fetching all user_answers_test_containers: {e}")
        return []
    finally:
        await conn.close()

async def get_by_id(id: int):
    conn = await db.get_db_connection()
    query = f"SELECT * FROM {TABLE_NAME} WHERE id = $1"
    try:
        row = await conn.fetchrow(query, id)
        if not row:
            logger.info(f"No user_answers_test_container found with id = {id}")
            return None
        return UserAnswersTestContainer(
            id=row["id"],
            user_id=row["user_id"],
            is_finished=row["is_finished"],
            got_score=row["got_score"]
        )
    except Exception as e:
        logger.error(f"Error fetching user_answers_test_container by ID: {e}")
        return None
    finally:
        await conn.close()

async def create(container: UserAnswersTestContainer):
    conn = await db.get_db_connection()
    query = f"""
        INSERT INTO {TABLE_NAME} (user_id, is_finished, got_score)
        VALUES ($1, $2, $3)
    """
    try:
        await conn.execute(query, container.user_id, container.is_finished, container.got_score)
    except Exception as e:
        logger.error(f"Error creating user_answers_test_container: {e}")
    finally:
        await conn.close()

async def update(container: UserAnswersTestContainer):
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
        logger.error(f"Error updating user_answers_test_container: {e}")
    finally:
        await conn.close()

async def delete_by_id(id: int):
    conn = await db.get_db_connection()
    query = f"DELETE FROM {TABLE_NAME} WHERE id = $1"
    try:
        await conn.execute(query, id)
        logger.info(f"Deleted user_answers_test_container with id = {id}")
    except Exception as e:
        logger.error(f"Error deleting user_answers_test_container: {e}")
    finally:
        await conn.close()

# user_answers_test_container_service.py

async def create(user_id: int) -> int:
    conn = await db.get_db_connection()
    try:
        query = f"""
            INSERT INTO {TABLE_NAME} (user_id, is_finished, got_score)
            VALUES ($1, FALSE, FALSE)
            RETURNING id
        """
        row = await conn.fetchrow(query, user_id)
        return row["id"]
    except Exception as e:
        logger.error(f"❌ Error in user_answers_test_container_service.create: {e}")
        return 0
    finally:
        await conn.close()


async def mark_finished(container_id: int):
    conn = await db.get_db_connection()
    try:
        query = f"""
            UPDATE {TABLE_NAME}
            SET is_finished = TRUE
            WHERE id = $1
        """
        await conn.execute(query, container_id)
    except Exception as e:
        logger.error(f"❌ Error in mark_finished: {e}")
    finally:
        await conn.close()