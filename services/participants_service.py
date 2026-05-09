import db
from models import Participant
from logger import logger

TABLE_NAME = "participants"

async def get_all():
    conn = await db.get_db_connection()
    query = f"SELECT * FROM {TABLE_NAME}"
    try:
        rows = await conn.fetch(query)
        return [Participant(
            id=row["id"],
            user_id=row["user_id"],
            fight_id=row["fight_id"]
        ) for row in rows]
    except Exception as e:
        logger.error(f"Error fetching all participants: {e}")
        return []
    finally:
        await conn.close()

async def get_all_by_fight_id(fight_id: int):
    conn = await db.get_db_connection()
    query = f"SELECT * FROM {TABLE_NAME} where fight_id = $1"
    try:
        rows = await conn.fetch(query, fight_id)
        return [Participant(
            id=row["id"],
            user_id=row["user_id"],
            fight_id=row["fight_id"]
        ) for row in rows]
    except Exception as e:
        logger.error(f"Error fetching all participants: {e}")
        return []
    finally:
        await conn.close()

async def get_by_id(id: int):
    conn = await db.get_db_connection()
    query = f"SELECT * FROM {TABLE_NAME} WHERE id = $1"
    try:
        row = await conn.fetchrow(query, id)
        if not row:
            logger.info(f"No participant found with id = {id}")
            return None
        return Participant(
            id=row["id"],
            user_id=row["user_id"],
            fight_id=row["fight_id"]
        )
    except Exception as e:
        logger.error(f"Error fetching participant by ID: {e}")
        return None
    finally:
        await conn.close()

async def get_by_user_and_fight_ids(user_id: int, fight_id: int):
    conn = await db.get_db_connection()
    query = f"SELECT * FROM {TABLE_NAME} WHERE user_id = $1 AND fight_id = $2"
    try:
        row = await conn.fetchrow(query, user_id, fight_id)
        if not row:
            logger.info(f"No participant found with id = {id}")
            return None
        return Participant(
            id=row["id"],
            user_id=row["user_id"],
            fight_id=row["fight_id"]
        )
    except Exception as e:
        logger.error(f"Error fetching participant by ID: {e}")
        return None
    finally:
        await conn.close()

async def create(participant: Participant):
    conn = await db.get_db_connection()
    query = f"""
        INSERT INTO {TABLE_NAME} (
            user_id,
            fight_id
        ) VALUES ($1, $2)
    """
    try:
        await conn.execute(
            query,
            participant.user_id,
            participant.fight_id
        )
    except Exception as e:
        logger.error(f"Error creating participant: {e}")
    finally:
        await conn.close()

async def update(participant: Participant):
    conn = await db.get_db_connection()
    query = f"""
        UPDATE {TABLE_NAME}
        SET
            user_id = $1,
            fight_id = $2
        WHERE id = $3
    """
    try:
        await conn.execute(
            query,
            participant.user_id,
            participant.fight_id,
            participant.id
        )
    except Exception as e:
        logger.error(f"Error updating participant: {e}")
    finally:
        await conn.close()

async def delete_by_id(id: int):
    conn = await db.get_db_connection()
    query = f"DELETE FROM {TABLE_NAME} WHERE id = $1"
    try:
        await conn.execute(query, id)
        logger.info(f"Deleted participant with id = {id}")
    except Exception as e:
        logger.error(f"Error deleting participant: {e}")
    finally:
        await conn.close()
