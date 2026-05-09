import db
from models import Class
from logger import logger

TABLE_NAME = "classes"

async def get_all():
    conn = await db.get_db_connection()
    query = f"SELECT * FROM {TABLE_NAME}"
    try:
        rows = await conn.fetch(query)
        return [Class(id=row["id"], name=row["name"], subject_id=row["subject_id"]) for row in rows]
    except Exception as e:
        logger.error(f"Error fetching all classes: {e}")
        return []
    finally:
        await conn.close()

async def get_by_id(id: int):
    conn = await db.get_db_connection()
    query = f"SELECT * FROM {TABLE_NAME} WHERE id = $1"
    try:
        row = await conn.fetchrow(query, id)
        if not row:
            logger.info(f"No class found with id = {id}")
            return None
        return Class(id=row["id"], name=row["name"], subject_id=row["subject_id"])
    except Exception as e:
        logger.error(f"Error fetching class by ID: {e}")
        return None
    finally:
        await conn.close()

async def get_by_name(name: str) -> Class | None:
    conn = await db.get_db_connection()
    query = f"SELECT * FROM {TABLE_NAME} WHERE name = $1"
    try:
        row = await conn.fetchrow(query, name)
        if not row:
            logger.info(f"No class found with name = '{name}'")
            return None
        return Class(id=row["id"], name=row["name"], subject_id=row["subject_id"])
    except Exception as e:
        logger.error(f"Error fetching class by name '{name}': {e}")
        return None
    finally:
        await conn.close()

async def get_by_name_and_subject(name: str, subject_id: int) -> Class | None:
    conn = await db.get_db_connection()
    query = f"SELECT * FROM {TABLE_NAME} WHERE name = $1 AND subject_id = $2"
    try:
        row = await conn.fetchrow(query, name, subject_id)
        if not row:
            logger.info(f"No class found with name = '{name}' and subject_id = {subject_id}")
            return None
        return Class(id=row["id"], name=row["name"], subject_id=row["subject_id"])
    except Exception as e:
        logger.error(f"Error fetching class by name '{name}' and subject_id {subject_id}: {e}")
        return None
    finally:
        await conn.close()


async def get_by_subject_id(subject_id: int):
    conn = await db.get_db_connection()
    query = f"SELECT * FROM {TABLE_NAME} WHERE subject_id = $1"
    try:
        rows = await conn.fetch(query, subject_id)
        return [Class(id=row['id'], name=row["name"], subject_id=row["subject_id"]) for row in rows]
    except Exception as e:
        logger.error(f"Error in fetching all classes by subject id : {e}")
        return []
    finally:
        await conn.close()

async def create(class_obj: Class):
    conn = await db.get_db_connection()
    query = f"""
        INSERT INTO {TABLE_NAME} (name, subject_id)
        VALUES ($1, $2)
    """
    try:
        await conn.execute(query, class_obj.name, class_obj.subject_id)
    except Exception as e:
        logger.error(f"Error creating class: {e}")
    finally:
        await conn.close()

async def update(class_obj: Class):
    conn = await db.get_db_connection()
    query = f"""
        UPDATE {TABLE_NAME}
        SET name = $1,
            subject_id = $2
        WHERE id = $3
    """
    try:
        await conn.execute(query, class_obj.name, class_obj.subject_id, class_obj.id)
    except Exception as e:
        logger.error(f"Error updating class: {e}")
    finally:
        await conn.close()

async def delete_by_id(id: int):
    conn = await db.get_db_connection()
    query = f"DELETE FROM {TABLE_NAME} WHERE id = $1"
    try:
        await conn.execute(query, id)
        logger.info(f"Deleted class with id = {id}")
    except Exception as e:
        logger.error(f"Error deleting class: {e}")
    finally:
        await conn.close()
