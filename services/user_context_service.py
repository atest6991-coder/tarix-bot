import db
from models import UserContext
from logger import logger

TABLE_NAME = "user_context"

async def get_all():
    conn = await db.get_db_connection()
    query = f"SELECT * FROM {TABLE_NAME}"
    try:
        rows = await conn.fetch(query)
        return [UserContext(
            id=row["id"],
            user_id=row["user_id"],
            selected_subject_id=row["selected_subject_id"],
            selected_class_id=row["selected_class_id"],
            selected_topic_id=row["selected_topic_id"]
        ) for row in rows]
    except Exception as e:
        logger.error(f"Error fetching all user_context records: {e}")
        return []
    finally:
        await conn.close()

async def get_by_id(id: int):
    conn = await db.get_db_connection()
    query = f"SELECT * FROM {TABLE_NAME} WHERE id = $1"
    try:
        row = await conn.fetchrow(query, id)
        if not row:
            logger.info(f"No user_context found with id = {id}")
            return None
        return UserContext(
            id=row["id"],
            user_id=row["user_id"],
            selected_subject_id=row["selected_subject_id"],
            selected_class_id=row["selected_class_id"],
            selected_topic_id=row["selected_topic_id"]
        )
    except Exception as e:
        logger.error(f"Error fetching user_context by ID: {e}")
        return None
    finally:
        await conn.close()

async def create(user_context: UserContext):
    conn = await db.get_db_connection()
    query = f"""
        INSERT INTO {TABLE_NAME} (
            user_id,
            selected_subject_id,
            selected_class_id,
            selected_topic_id
        ) VALUES ($1, $2, $3, $4)
    """
    try:
        await conn.execute(
            query,
            user_context.user_id,
            user_context.selected_subject_id,
            user_context.selected_class_id,
            user_context.selected_topic_id
        )
    except Exception as e:
        logger.error(f"Error creating user_context: {e}")
    finally:
        await conn.close()

async def update(user_context: UserContext):
    conn = await db.get_db_connection()
    query = f"""
        UPDATE {TABLE_NAME}
        SET
            user_id = $1,
            selected_subject_id = $2,
            selected_class_id = $3,
            selected_topic_id = $4
        WHERE id = $5
    """
    try:
        await conn.execute(
            query,
            user_context.user_id,
            user_context.selected_subject_id,
            user_context.selected_class_id,
            user_context.selected_topic_id,
            user_context.id
        )
    except Exception as e:
        logger.error(f"Error updating user_context: {e}")
    finally:
        await conn.close()

async def delete_by_id(id: int):
    conn = await db.get_db_connection()
    query = f"DELETE FROM {TABLE_NAME} WHERE id = $1"
    try:
        await conn.execute(query, id)
        logger.info(f"Deleted user_context with id = {id}")
    except Exception as e:
        logger.error(f"Error deleting user_context: {e}")
    finally:
        await conn.close()


async def get_by_user_id(user_id: int) -> UserContext | None:
    conn = await db.get_db_connection()
    query = f"SELECT * FROM {TABLE_NAME} WHERE user_id = $1"
    try:
        row = await conn.fetchrow(query, user_id)
        if not row:
            logger.info(f"No user_context found with user_id = {user_id}")
            return None
        return UserContext(
            id=row["id"],
            user_id=row["user_id"],
            selected_subject_id=row["selected_subject_id"],
            selected_class_id=row["selected_class_id"],
            selected_topic_id=row["selected_topic_id"]
        )
    except Exception as e:
        logger.error(f"Error fetching user_context by user_id: {e}")
        return None
    finally:
        await conn.close()


async def create_or_update(user_context: UserContext):
    existing = await get_by_user_id(user_context.user_id)
    if existing:
        user_context.id = existing.id 
        await update(user_context)
    else:
        await create(user_context)
