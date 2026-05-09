from models import FightTestContainer
import db
from logger import logger

TABLE_NAME = "fight_test_container"

async def create(fight_test_container: FightTestContainer) -> int:
    conn = await db.get_db_connection()
    try:
        row = await conn.fetchrow(
            f"""
            INSERT INTO {TABLE_NAME} (user_id, fight_id, test_container_id)
            VALUES ($1, $2, $3)
            RETURNING id
            """,
            fight_test_container.user_id,
            fight_test_container.fight_id,
            fight_test_container.test_container_id
        )
        return row["id"]
    except Exception as e:
        logger.error(f"Error creating fight_test_container: {e}")
    finally:
        await conn.close()

async def get_by_user_and_fight(user_id: int, fight_id: int) -> FightTestContainer | None:
    conn = await db.get_db_connection()
    try:
        row = await conn.fetchrow(
            f"""
            SELECT id, user_id, fight_id, test_container_id
            FROM {TABLE_NAME}
            WHERE user_id = $1 AND fight_id = $2
            """,
            user_id, fight_id
        )
        if row:
            return FightTestContainer(
                id=row["id"],
                user_id=row["user_id"],
                fight_id=row["fight_id"],
                test_container_id=row["test_container_id"]
            )
        return None
    except Exception as e:
        logger.error(f"Error getting fight_test_container: {e}")
    finally:
        await conn.close()

async def delete_by_fight_id(fight_id: int):
    conn = await db.get_db_connection()
    try:
        await conn.execute(
            f"DELETE FROM {TABLE_NAME} WHERE fight_id = $1",
            fight_id
        )
    except Exception as e:
        logger.error(f"Error deleting fight_test_container by fight_id: {e}")
    finally:
        await conn.close()
