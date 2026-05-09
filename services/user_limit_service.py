import db

async def check_daily_limit(user_id: int, action_type: str) -> bool:
    conn = await db.get_db_connection()
    try:
        row = await conn.fetchrow(
            """
            SELECT 1 FROM user_daily_limits
            WHERE user_id = $1 AND action_type = $2 AND date = CURRENT_DATE
            """,
            user_id, action_type
        )
        return row is None  # True if user can proceed
    finally:
        await conn.close()

async def mark_daily_limit(user_id: int, action_type: str):
    conn = await db.get_db_connection()
    try:
        await conn.execute(
            """
            INSERT INTO user_daily_limits (user_id, action_type, date)
            VALUES ($1, $2, CURRENT_DATE)
            ON CONFLICT DO NOTHING
            """,
            user_id, action_type
        )
    finally:
        await conn.close()