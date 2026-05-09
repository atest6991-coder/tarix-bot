import db
from models import Subject
from logger import logger

TABLE_NAME = "subjects"

async def get_all():
    conn = await db.get_db_connection()
    query = f"SELECT * FROM {TABLE_NAME}"
    try:
        rows = await conn.fetch(query)
        return [Subject(id=row["id"], name=row["name"]) for row in rows]
    except Exception as e:
        logger.error(f"Error fetching all subjects: {e}")
        return []
    finally:
        await conn.close()

async def get_by_id(id: int) -> Subject:
    conn = await db.get_db_connection()
    query = f"SELECT * FROM {TABLE_NAME} WHERE id = $1"
    try:
        row = await conn.fetchrow(query, id)
        if not row:
            logger.info(f"No subject found with id = {id}")
            return None
        return Subject(id=row["id"], name=row["name"])
    except Exception as e:
        logger.error(f"Error fetching subject by ID: {e}")
        return None
    finally:
        await conn.close()

async def get_by_name(name: str) -> Subject | None:
    conn = await db.get_db_connection()
    query = f"SELECT * FROM {TABLE_NAME} WHERE name = $1"
    try:
        row = await conn.fetchrow(query, name)
        if not row:
            logger.info(f"No subject found with name = {name}")
            return None
        return Subject(id=row["id"], name=row["name"])
    except Exception as e:
        logger.error(f"Error fetching subject by name: {e}")
        return None
    finally:
        await conn.close()


async def create(subject: Subject):
    conn = await db.get_db_connection()
    query = f"INSERT INTO {TABLE_NAME} (name) VALUES ($1) ON CONFLICT (name) DO NOTHING"
    try:
        await conn.execute(query, subject.name)
    except Exception as e:
        logger.error(f"Error creating subject: {e}")
    finally:
        await conn.close()

async def update(subject: Subject):
    conn = await db.get_db_connection()
    query = f"UPDATE {TABLE_NAME} SET name = $1 WHERE id = $2"
    try:
        await conn.execute(query, subject.name, subject.id)
    except Exception as e:
        logger.error(f"Error updating subject: {e}")
    finally:
        await conn.close()

async def delete_by_id(id: int):
    conn = await db.get_db_connection()
    query = f"DELETE FROM {TABLE_NAME} WHERE id = $1"
    try:
        await conn.execute(query, id)
        logger.info(f"Deleted subject with id = {id}")
    except Exception as e:
        logger.error(f"Error deleting subject: {e}")
    finally:
        await conn.close()
