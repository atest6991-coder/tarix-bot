import db
from models import Topic
from logger import logger

TABLE_NAME = "topics"

async def get_all():
    conn = await db.get_db_connection()
    query = f"SELECT * FROM {TABLE_NAME} order by id"
    try:
        rows = await conn.fetch(query)
        return [Topic(id=row["id"], name=row["name"], class_id=row["class_id"]) for row in rows]
    except Exception as e:
        logger.error(f"Error fetching all topics: {e}")
        return []
    finally:
        await conn.close()

async def get_by_id(id: int):
    conn = await db.get_db_connection()
    query = f"SELECT * FROM {TABLE_NAME} WHERE id = $1"
    try:
        row = await conn.fetchrow(query, id)
        if not row:
            logger.info(f"No topic found with id = {id}")
            return None
        return Topic(id=row["id"], name=row["name"], class_id=row["class_id"])
    except Exception as e:
        logger.error(f"Error fetching topic by ID: {e}")
        return None
    finally:
        await conn.close()

async def create(topic: Topic):
    conn = await db.get_db_connection()
    query = f"""
        INSERT INTO {TABLE_NAME} (name, class_id)
        VALUES ($1, $2)
    """
    try:
        await conn.execute(query, topic.name, topic.class_id)
    except Exception as e:
        logger.error(f"Error creating topic: {e}")
    finally:
        await conn.close()

async def update(topic: Topic):
    conn = await db.get_db_connection()
    query = f"""
        UPDATE {TABLE_NAME}
        SET name = $1,
            class_id = $2
        WHERE id = $3
    """
    try:
        await conn.execute(query, topic.name, topic.class_id, topic.id)
    except Exception as e:
        logger.error(f"Error updating topic: {e}")
    finally:
        await conn.close()

async def delete_by_id(id: int):
    conn = await db.get_db_connection()
    query = f"DELETE FROM {TABLE_NAME} WHERE id = $1"
    try:
        await conn.execute(query, id)
        logger.info(f"Deleted topic with id = {id}")
    except Exception as e:
        logger.error(f"Error deleting topic: {e}")
    finally:
        await conn.close()

async def get_by_class_id(class_id: int):
    conn = await db.get_db_connection()
    query = f"SELECT * FROM {TABLE_NAME} WHERE class_id = $1 order by id"
    try:
        rows = await conn.fetch(query, class_id)
        return [Topic(id=row["id"], name=row["name"], class_id=row["class_id"]) for row in rows]
    except Exception as e:
        logger.error(f"Error in get_by_class_id: {e}")
        return []
    finally:
        await conn.close()

async def get_by_name(name: str) -> Topic | None:
    conn = await db.get_db_connection()
    query = f"SELECT * FROM {TABLE_NAME} WHERE name = $1 order by id"
    try:
        row = await conn.fetchrow(query, name)
        if not row:
            logger.info(f"No topic found with name = {name}")
            return None
        return Topic(id=row["id"], name=row["name"], class_id=row["class_id"])
    except Exception as e:
        logger.error(f"Error fetching topic by name: {e}")
        return None
    finally:
        await conn.close()

async def get_by_name_and_class(name: str, class_id: int) -> Topic | None:
    conn = await db.get_db_connection()
    query = f"SELECT * FROM {TABLE_NAME} WHERE name = $1 AND class_id = $2 order by id"
    try:
        row = await conn.fetchrow(query, name, class_id)
        if not row:
            logger.info(f"No topic found with name = {name} and class_id = {class_id}")
            return None
        return Topic(id=row["id"], name=row["name"], class_id=row["class_id"])
    except Exception as e:
        logger.error(f"Error fetching topic by name and class_id: {e}")
        return None
    finally:
        await conn.close()
