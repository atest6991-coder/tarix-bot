import db
from models import PDFMaterial
from logger import logger

TABLE_NAME = "pdf_materials"

async def get_all():
    conn = await db.get_db_connection()
    query = f"SELECT * FROM {TABLE_NAME}"
    try:
        rows = await conn.fetch(query)
        return [PDFMaterial(id=row["id"], file_id=row["file_id"], topic_id=row["topic_id"]) for row in rows]
    except Exception as e:
        logger.error(f"Error fetching all PDF materials: {e}")
        return []
    finally:
        await conn.close()

async def get_by_id(id: int):
    conn = await db.get_db_connection()
    query = f"SELECT * FROM {TABLE_NAME} WHERE id = $1"
    try:
        row = await conn.fetchrow(query, id)
        if not row:
            logger.info(f"No PDF material found with id = {id}")
            return None
        return PDFMaterial(id=row["id"], file_id=row["file_id"], topic_id=row["topic_id"])
    except Exception as e:
        logger.error(f"Error fetching PDF material by ID: {e}")
        return None
    finally:
        await conn.close()

async def get_by_topic_id(topic_id: int):
    conn = await db.get_db_connection()
    query = f"SELECT * FROM {TABLE_NAME} WHERE topic_id = $1"
    try:
        row = await conn.fetchrow(query, topic_id)
        if not row:
            logger.info(f"No PDF material found with topic id = {topic_id}")
            return None
        return PDFMaterial(id=row["id"], file_id=row["file_id"], topic_id=row["topic_id"])
    except Exception as e:
        logger.error(f"Error fetching PDF material by topic ID: {e}")
        return None
    finally:
        await conn.close()

async def create(pdf_material: PDFMaterial):
    conn = await db.get_db_connection()
    query = f"""
        INSERT INTO {TABLE_NAME} (file_id, topic_id)
        VALUES ($1, $2)
    """
    try:
        await conn.execute(query, pdf_material.file_id, pdf_material.topic_id)
    except Exception as e:
        logger.error(f"Error creating PDF material: {e}")
    finally:
        await conn.close()

async def update(pdf_material: PDFMaterial):
    conn = await db.get_db_connection()
    query = f"""
        UPDATE {TABLE_NAME}
        SET file_id = $1,
            topic_id = $2
        WHERE id = $3
    """
    try:
        await conn.execute(query, pdf_material.file_id, pdf_material.topic_id, pdf_material.id)
    except Exception as e:
        logger.error(f"Error updating PDF material: {e}")
    finally:
        await conn.close()

async def delete_by_id(id: int):
    conn = await db.get_db_connection()
    query = f"DELETE FROM {TABLE_NAME} WHERE id = $1"
    try:
        await conn.execute(query, id)
        logger.info(f"Deleted PDF material with id = {id}")
    except Exception as e:
        logger.error(f"Error deleting PDF material: {e}")
    finally:
        await conn.close()
