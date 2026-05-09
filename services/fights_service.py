import db
from models import Fight
from logger import logger

TABLE_NAME = "fights"
TABLE_FIGHT_FILL_BLANKS = "fight_fill_blanks"
TABLE_FIGHTS = "fights"
TABLE_TESTS = "tests"
TABLE_FIGHT_TESTS = "fight_tests"
TABLE_FILL_BLANKS_TESTS = "fill_blanks_tests"

async def get_all():
    conn = await db.get_db_connection()
    query = f"SELECT * FROM {TABLE_NAME}"
    try:
        rows = await conn.fetch(query)
        return [Fight(
            id=row["id"],
            user_id=row["user_id"],
            is_finished=row["is_finished"]
        ) for row in rows]
    except Exception as e:
        logger.error(f"Error fetching all fights: {e}")
        return []
    finally:
        await conn.close()

async def get_by_id(id: int):
    conn = await db.get_db_connection()
    query = f"SELECT * FROM {TABLE_NAME} WHERE id = $1"
    try:
        row = await conn.fetchrow(query, id)
        if not row:
            logger.info(f"No fight found with id = {id}")
            return None
        return Fight(
            id=row["id"],
            user_id=row["user_id"],
            is_finished=row["is_finished"]
        )
    except Exception as e:
        logger.error(f"Error fetching fight by ID: {e}")
        return None
    finally:
        await conn.close()

async def create(fight: Fight):
    conn = await db.get_db_connection()
    query = f"""
        INSERT INTO {TABLE_NAME} (
            user_id,
            is_finished
        ) VALUES ($1, $2)
    """
    try:
        await conn.execute(
            query,
            fight.user_id,
            fight.is_finished
        )
    except Exception as e:
        logger.error(f"Error creating fight: {e}")
    finally:
        await conn.close()

async def update(fight: Fight):
    conn = await db.get_db_connection()
    query = f"""
        UPDATE {TABLE_NAME}
        SET
            user_id = $1,
            is_finished = $2
        WHERE id = $3
    """
    try:
        await conn.execute(
            query,
            fight.user_id,
            fight.is_finished,
            fight.id
        )
    except Exception as e:
        logger.error(f"Error updating fight: {e}")
    finally:
        await conn.close()

async def delete_by_id(id: int):
    conn = await db.get_db_connection()
    query = f"DELETE FROM {TABLE_NAME} WHERE id = $1"
    try:
        await conn.execute(query, id)
        logger.info(f"Deleted fight with id = {id}")
    except Exception as e:
        logger.error(f"Error deleting fight: {e}")
    finally:
        await conn.close()


async def create_fight_and_assign_tests(
    user_id: int,
    selected_topic_ids: list[int],
    include_fillblanks: bool,
    test_count: int
) -> int:
    """
    Creates a fight, assigns randomized tests and fill blanks tests as configured,
    and returns the created fight ID.
    """

    conn = await db.get_db_connection()
    try:
        async with conn.transaction():

            # 1️⃣ Create fight
            fight_row = await conn.fetchrow(
                f"""
                INSERT INTO {TABLE_FIGHTS} (user_id)
                VALUES ($1)
                RETURNING id
                """,
                user_id
            )
            fight_id = fight_row["id"]

            # 2️⃣ Determine split counts
            fillblanks_count = int(test_count * 0.3) if include_fillblanks else 0
            simple_test_count = test_count - fillblanks_count

            # 3️⃣ Fetch random test IDs
            test_rows = await conn.fetch(
                f"""
                SELECT id FROM {TABLE_TESTS}
                WHERE topic_id = ANY($1::int[])
                ORDER BY random()
                LIMIT $2
                """,
                selected_topic_ids,
                simple_test_count
            )

            # 4️⃣ Insert fight_tests
            if test_rows:
                await conn.executemany(
                    f"""
                    INSERT INTO {TABLE_FIGHT_TESTS} (fight_id, test_id)
                    VALUES ($1, $2)
                    """,
                    [(fight_id, row["id"]) for row in test_rows]
                )

            # 5️⃣ Fetch random fill blanks test IDs
            if fillblanks_count > 0:
                fb_rows = await conn.fetch(
                    f"""
                    SELECT id FROM {TABLE_FILL_BLANKS_TESTS}
                    WHERE topic_id = ANY($1::int[])
                    ORDER BY random()
                    LIMIT $2
                    """,
                    selected_topic_ids,
                    fillblanks_count
                )

                # 6️⃣ Insert fight_fill_blanks
                if fb_rows:
                    await conn.executemany(
                        f"""
                        INSERT INTO {TABLE_FIGHT_FILL_BLANKS} (fight_id, fill_blanks_test_id)
                        VALUES ($1, $2)
                        """,
                        [(fight_id, row["id"]) for row in fb_rows]
                    )

            logger.info(f"Fight {fight_id} created with {len(test_rows)} tests and {len(fb_rows) if fillblanks_count > 0 else 0} fill blanks tests.")

            return fight_id

    except Exception as e:
        logger.error(f"Error in create_fight_and_assign_tests: {e}")
        raise e

    finally:
        await conn.close()
