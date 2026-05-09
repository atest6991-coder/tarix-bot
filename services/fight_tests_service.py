import db
from models import FightTest
from logger import logger

TABLE_NAME = "fight_tests"

async def get_all():
    conn = await db.get_db_connection()
    query = f"SELECT * FROM {TABLE_NAME}"
    try:
        rows = await conn.fetch(query)
        return [FightTest(
            id=row["id"],
            fight_id=row["fight_id"],
            test_id=row["test_id"]
        ) for row in rows]
    except Exception as e:
        logger.error(f"Error fetching all fight_tests: {e}")
        return []
    finally:
        await conn.close()

async def get_all_by_fight_id(fight_id: int):
    conn = await db.get_db_connection()
    query = f"SELECT * FROM {TABLE_NAME} WHERE fight_id = $1"
    try:
        rows = await conn.fetch(query, fight_id)
        return [FightTest(
            id=row["id"],
            fight_id=row["fight_id"],
            test_id=row["test_id"]
        ) for row in rows]
    except Exception as e:
        logger.error(f"Error fetching all fight_tests by fight id: {e}")
        return []
    finally:
        await conn.close()

async def get_by_id(id: int):
    conn = await db.get_db_connection()
    query = f"SELECT * FROM {TABLE_NAME} WHERE id = $1"
    try:
        row = await conn.fetchrow(query, id)
        if not row:
            logger.info(f"No fight_test found with id = {id}")
            return None
        return FightTest(
            id=row["id"],
            fight_id=row["fight_id"],
            test_id=row["test_id"]
        )
    except Exception as e:
        logger.error(f"Error fetching fight_test by ID: {e}")
        return None
    finally:
        await conn.close()

async def create(fight_test: FightTest):
    conn = await db.get_db_connection()
    query = f"""
        INSERT INTO {TABLE_NAME} (
            fight_id,
            test_id
        ) VALUES ($1, $2)
    """
    try:
        await conn.execute(
            query,
            fight_test.fight_id,
            fight_test.test_id
        )
    except Exception as e:
        logger.error(f"Error creating fight_test: {e}")
    finally:
        await conn.close()

async def update(fight_test: FightTest):
    conn = await db.get_db_connection()
    query = f"""
        UPDATE {TABLE_NAME}
        SET
            fight_id = $1,
            test_id = $2
        WHERE id = $3
    """
    try:
        await conn.execute(
            query,
            fight_test.fight_id,
            fight_test.test_id,
            fight_test.id
        )
    except Exception as e:
        logger.error(f"Error updating fight_test: {e}")
    finally:
        await conn.close()

async def delete_by_id(id: int):
    conn = await db.get_db_connection()
    query = f"DELETE FROM {TABLE_NAME} WHERE id = $1"
    try:
        await conn.execute(query, id)
        logger.info(f"Deleted fight_test with id = {id}")
    except Exception as e:
        logger.error(f"Error deleting fight_test: {e}")
    finally:
        await conn.close()
