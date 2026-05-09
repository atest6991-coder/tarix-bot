import db
from models import User
from logger import logger

TABLE_NAME = "users"


async def get_all():
    conn = await db.get_db_connection()
    query = f"SELECT * FROM {TABLE_NAME}"
    try:
        rows = await conn.fetch(query)
        users = [
            User(
                id=row["id"],                first_name=row["first_name"],
                last_name=row["last_name"],
                username=row["username"],
                is_premium=row["is_premium"],
                premium_expiry_at=row["premium_expiry_at"],
                total_score=row["total_score"]
            )
            for row in rows
        ]
        return users
    except Exception as e:
        logger.error(f"Error fetching all users: {e}")
        return []
    finally:
        await conn.close()


async def get_by_id(id: int):
    conn = await db.get_db_connection()
    query = f"SELECT * FROM {TABLE_NAME} WHERE id = $1"
    try:
        row = await conn.fetchrow(query, id)
        if not row:
            logger.info(f"No user found with id = {id}")
            return None
        return User(
            id=row["id"],
            first_name=row["first_name"],
            last_name=row["last_name"],
            username=row["username"],
            is_premium=row["is_premium"],
            premium_expiry_at=row["premium_expiry_at"],
            total_score=row["total_score"]
        )
    except Exception as e:
        logger.error(f"Error fetching user by ID: {e}")
        return None
    finally:
        await conn.close()


async def create(user: User):
    conn = await db.get_db_connection()
    query = f"""
        INSERT INTO {TABLE_NAME} (
            id, first_name, last_name, username, is_premium,
            premium_expiry_at, total_score
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        ON CONFLICT (id) DO NOTHING
    """
    try:
        await conn.execute(
            query,
            user.id,
            user.first_name,
            user.last_name,
            user.username,
            user.is_premium,
            user.premium_expiry_at,
            user.total_score
        )
    except Exception as e:
        logger.error(f"Error creating user: {e}")
    finally:
        await conn.close()


async def update(user: User):
    conn = await db.get_db_connection()
    query = f"""
        UPDATE {TABLE_NAME}
        SET
            first_name = $1,
            last_name = $2,
            username = $3,
            is_premium = $4,
            premium_expiry_at = $5,
            total_score = $6
        WHERE id = $7
    """
    try:
        await conn.execute(
            query,
            user.first_name,
            user.last_name,
            user.username,
            user.is_premium,
            user.premium_expiry_at,
            user.total_score,
            user.id
        )
    except Exception as e:
        logger.error(f"Error updating user: {e}")
    finally:
        await conn.close()


async def delete_by_id(id: int):
    conn = await db.get_db_connection()
    query = f"DELETE FROM {TABLE_NAME} WHERE id = $1"
    try:
        await conn.execute(query, id)
        logger.info(f"Deleted user with id = {id}")
    except Exception as e:
        logger.error(f"Error deleting user: {e}")
    finally:
        await conn.close()


async def get_top_users(limit: int = 5) -> list[User]:
    conn = await db.get_db_connection()
    rows = await conn.fetch("""
        SELECT id, first_name, last_name, username, total_score
        FROM users
        ORDER BY total_score DESC
        LIMIT $1
    """, limit)
    await conn.close()
    return [User(**dict(row)) for row in rows]


async def get_user_rank(user_id: int) -> int:
    conn = await db.get_db_connection()
    row = await conn.fetchrow("""
        SELECT COUNT(*) + 1 AS rank
        FROM users
        WHERE total_score > (
            SELECT total_score FROM users WHERE id = $1
        )
    """, user_id)
    await conn.close()
    return row["rank"] if row else None
