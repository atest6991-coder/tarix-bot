import db
from models import FightFillBlank
from logger import logger

TABLE_NAME = "fight_fill_blanks"

async def get_all():
    conn = await db.get_db_connection()
    query = f"SELECT * FROM {TABLE_NAME}"
    try:
        rows = await conn.fetch(query)
        return [FightFillBlank(
            id=row["id"],
            fight_id=row["fight_id"],
            fill_blanks_test_id=row["fill_blanks_test_id"]
        ) for row in rows]
    except Exception as e:
        logger.error(f"Error fetching all fight_fill_blanks: {e}")
        return []
    finally:
        await conn.close()

async def get_all_by_fight_id(fight_id: int):
    conn = await db.get_db_connection()
    query = f"SELECT * FROM {TABLE_NAME} where fight_id = $1"
    try:
        rows = await conn.fetch(query, fight_id)
        return [FightFillBlank(
            id=row["id"],
            fight_id=row["fight_id"],
            fill_blanks_test_id=row["fill_blanks_test_id"]
        ) for row in rows]
    except Exception as e:
        logger.error(f"Error fetching all fight_fill_blanks: {e}")
        return []
    finally:
        await conn.close()

async def get_by_id(id: int):
    conn = await db.get_db_connection()
    query = f"SELECT * FROM {TABLE_NAME} WHERE id = $1"
    try:
        row = await conn.fetchrow(query, id)
        if not row:
            logger.info(f"No fight_fill_blank found with id = {id}")
            return None
        return FightFillBlank(
            id=row["id"],
            fight_id=row["fight_id"],
            fill_blanks_test_id=row["fill_blanks_test_id"]
        )
    except Exception as e:
        logger.error(f"Error fetching fight_fill_blank by ID: {e}")
        return None
    finally:
        await conn.close()

async def create(fight_fill_blank: FightFillBlank):
    conn = await db.get_db_connection()
    query = f"""
        INSERT INTO {TABLE_NAME} (
            fight_id,
            fill_blanks_test_id
        ) VALUES ($1, $2)
    """
    try:
        await conn.execute(
            query,
            fight_fill_blank.fight_id,
            fight_fill_blank.fill_blanks_test_id
        )
    except Exception as e:
        logger.error(f"Error creating fight_fill_blank: {e}")
    finally:
        await conn.close()

async def update(fight_fill_blank: FightFillBlank):
    conn = await db.get_db_connection()
    query = f"""
        UPDATE {TABLE_NAME}
        SET
            fight_id = $1,
            fill_blanks_test_id = $2
        WHERE id = $3
    """
    try:
        await conn.execute(
            query,
            fight_fill_blank.fight_id,
            fight_fill_blank.fill_blanks_test_id,
            fight_fill_blank.id
        )
    except Exception as e:
        logger.error(f"Error updating fight_fill_blank: {e}")
    finally:
        await conn.close()

async def delete_by_id(id: int):
    conn = await db.get_db_connection()
    query = f"DELETE FROM {TABLE_NAME} WHERE id = $1"
    try:
        await conn.execute(query, id)
        logger.info(f"Deleted fight_fill_blank with id = {id}")
    except Exception as e:
        logger.error(f"Error deleting fight_fill_blank: {e}")
    finally:
        await conn.close()
