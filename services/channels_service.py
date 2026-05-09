import db
from models import Channel
from logger import logger

TABLE_NAME = "channels"

async def get_all():
    conn = await db.get_db_connection()
    query = f"SELECT * FROM {TABLE_NAME}"
    try:
        rows = await conn.fetch(query)
        return [
            Channel(
                id=row["id"],
                username=row["username"],
                link=row["link"]
            )
            for row in rows
        ]
    except Exception as e:
        logger.error(f"Error fetching all channels: {e}")
        return []
    finally:
        await conn.close()

async def get_by_id(id: int):
    conn = await db.get_db_connection()
    query = f"SELECT * FROM {TABLE_NAME} WHERE id = $1"
    try:
        row = await conn.fetchrow(query, id)
        if not row:
            logger.info(f"No channel found with id = {id}")
            return None
        return Channel(
            id=row["id"],
            username=row["username"],
            link=row["link"]
        )
    except Exception as e:
        logger.error(f"Error fetching channel by ID: {e}")
        return None
    finally:
        await conn.close()

async def create(channel: Channel):
    conn = await db.get_db_connection()
    query = f"""
        INSERT INTO {TABLE_NAME} (
            username,
            link
        ) VALUES ($1, $2)
    """
    try:
        await conn.execute(
            query,
            channel.username,
            channel.link
        )
        logger.info(f"Created channel: {channel.username}")
    except Exception as e:
        logger.error(f"Error creating channel: {e}")
    finally:
        await conn.close()

async def update(channel: Channel):
    conn = await db.get_db_connection()
    query = f"""
        UPDATE {TABLE_NAME}
        SET
            username = $1,
            link = $2
        WHERE id = $3
    """
    try:
        await conn.execute(
            query,
            channel.username,
            channel.link,
            channel.id
        )
        logger.info(f"Updated channel with id = {channel.id}")
    except Exception as e:
        logger.error(f"Error updating channel: {e}")
    finally:
        await conn.close()

async def delete_by_id(id: int):
    conn = await db.get_db_connection()
    query = f"DELETE FROM {TABLE_NAME} WHERE id = $1"
    try:
        await conn.execute(query, id)
        logger.info(f"Deleted channel with id = {id}")
    except Exception as e:
        logger.error(f"Error deleting channel: {e}")
    finally:
        await conn.close()
