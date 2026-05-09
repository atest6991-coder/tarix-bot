from models import GotScore
import db
import logging

logger = logging.getLogger(__name__)

TABLE_NAME = "got_scores"

async def create(got_score: GotScore):
    conn = await db.get_db_connection()
    try:
        query = f"""
            INSERT INTO {TABLE_NAME} (user_id, topic_id, test_type)
            VALUES ($1, $2, $3)
            RETURNING id
        """
        row = await conn.fetchrow(query, got_score.user_id, got_score.topic_id, got_score.test_type)
        got_score.id = row["id"]
        logger.info(f"✅ GotScore created with id={got_score.id}")
        return got_score.id
    except Exception as e:
        logger.error(f"❌ Error in got_score_service.create: {e}")
    finally:
        await conn.close()

async def get_by_user_and_topic_and_test_type(user_id: int, topic_id: int, test_type: str) -> GotScore | None:
    conn = await db.get_db_connection()
    try:
        query = f"""
            SELECT id, user_id, topic_id, test_type
            FROM {TABLE_NAME}
            WHERE user_id = $1 AND topic_id = $2 AND test_type = $3
            LIMIT 1
        """
        row = await conn.fetchrow(query, user_id, topic_id, test_type)
        if row:
            return GotScore(
                id=row["id"],
                user_id=row["user_id"],
                topic_id=row["topic_id"],
                test_type=row["test_type"]
            )
        return None
    except Exception as e:
        logger.error(f"Error in got_score_service.get_by_user_and_topic_and_test_type: {e}")
    finally:
        await conn.close()


async def delete_by_id(got_score_id: int):
    conn = await db.get_db_connection()
    try:
        query = f"DELETE FROM {TABLE_NAME} WHERE id = $1"
        await conn.execute(query, got_score_id)
        logger.info(f"GotScore with id={got_score_id} deleted")
    except Exception as e:
        logger.error(f"Error in got_score_service.delete_by_id: {e}")
    finally:
        await conn.close()

async def delete_by_user_and_topic(user_id: int, topic_id: int):
    conn = await db.get_db_connection()
    try:
        query = f"DELETE FROM {TABLE_NAME} WHERE user_id = $1 AND topic_id = $2"
        await conn.execute(query, user_id, topic_id)
        logger.info(f"✅ GotScore for user_id={user_id} and topic_id={topic_id} deleted")
    except Exception as e:
        logger.error(f"❌ Error in got_score_service.delete_by_user_and_topic: {e}")
    finally:
        await conn.close()