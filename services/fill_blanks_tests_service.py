import db
from models import FillBlanksTest, FillBlanksTestAnswer
from logger import logger

TABLE_NAME = "fill_blanks_tests"
TABLE_FILL_BLANKS_TESTS = "fill_blanks_tests"
TABLE_FILL_BLANKS_TEST_ANSWERS = "fill_blanks_test_answers"

async def get_all():
    conn = await db.get_db_connection()
    query = f"SELECT * FROM {TABLE_NAME}"
    try:
        rows = await conn.fetch(query)
        return [FillBlanksTest(
            id=row["id"],
            text=row["text"],
            topic_id=row["topic_id"]
        ) for row in rows]
    except Exception as e:
        logger.error(f"Error fetching all fill blanks tests: {e}")
        return []
    finally:
        await conn.close()


async def get_all_by_topic(topic_id: int):
    conn = await db.get_db_connection()
    query = f"SELECT * FROM {TABLE_NAME} where topic_id = $1"
    try:
        rows = await conn.fetch(query, topic_id)
        return [FillBlanksTest(
            id=row["id"],
            text=row["text"],
            topic_id=row["topic_id"]
        ) for row in rows]
    except Exception as e:
        logger.error(f"Error fetching all fill blanks tests by topic id: {e}")
        return []
    finally:
        await conn.close()

async def get_by_id(id: int):
    conn = await db.get_db_connection()
    query = f"SELECT * FROM {TABLE_NAME} WHERE id = $1"
    try:
        row = await conn.fetchrow(query, id)
        if not row:
            logger.info(f"No fill blanks test found with id = {id}")
            return None
        return FillBlanksTest(
            id=row["id"],
            text=row["text"],
            topic_id=row["topic_id"]
        )
    except Exception as e:
        logger.error(f"Error fetching fill blanks test by ID: {e}")
        return None
    finally:
        await conn.close()

async def create(fill_blanks_test: FillBlanksTest):
    conn = await db.get_db_connection()
    query = f"""
        INSERT INTO {TABLE_NAME} (text, topic_id)
        VALUES ($1, $2)
    """
    try:
        await conn.execute(query, fill_blanks_test.text, fill_blanks_test.topic_id)
    except Exception as e:
        logger.error(f"Error creating fill blanks test: {e}")
    finally:
        await conn.close()

async def update(fill_blanks_test: FillBlanksTest):
    conn = await db.get_db_connection()
    query = f"""
        UPDATE {TABLE_NAME}
        SET text = $1,
            topic_id = $2
        WHERE id = $3
    """
    try:
        await conn.execute(query, fill_blanks_test.text, fill_blanks_test.topic_id, fill_blanks_test.id)
    except Exception as e:
        logger.error(f"Error updating fill blanks test: {e}")
    finally:
        await conn.close()

async def delete_by_id(id: int):
    conn = await db.get_db_connection()
    query = f"DELETE FROM {TABLE_NAME} WHERE id = $1"
    try:
        await conn.execute(query, id)
        logger.info(f"Deleted fill blanks test with id = {id}")
    except Exception as e:
        logger.error(f"Error deleting fill blanks test: {e}")
    finally:
        await conn.close()

async def save_test_with_answers(test: FillBlanksTest, answers: list[FillBlanksTestAnswer]):
    conn = await db.get_db_connection()
    try:
        async with conn.transaction():  # Ensures rollback if anything fails

            # Insert test and get its id
            query_test = f"""
                INSERT INTO {TABLE_FILL_BLANKS_TESTS} (text, topic_id)
                VALUES ($1, $2)
                RETURNING id
            """
            test_id_row = await conn.fetchrow(query_test, test.text, test.topic_id)
            test_id = test_id_row["id"]

            # Insert all answers
            query_answer = f"""
                INSERT INTO {TABLE_FILL_BLANKS_TEST_ANSWERS} (fill_blanks_test_id, number, answer)
                VALUES ($1, $2, $3)
            """

            for answer in answers:
                await conn.execute(query_answer, test_id, answer.number, answer.answer)

            logger.info(f"FillBlanksTest with id={test_id} and {len(answers)} answers saved successfully.")

    except Exception as e:
        logger.error(f"Error in save_test_with_answers: {e}")
        raise
    finally:
        await conn.close()


async def count_by_topic_id(topic_id: int) -> int:
    conn = await db.get_db_connection()
    try:
        row = await conn.fetchrow(f"SELECT COUNT(*) AS cnt FROM {TABLE_FILL_BLANKS_TESTS} WHERE topic_id=$1", topic_id)
        return row["cnt"] if row else 0
    finally:
        await conn.close()

# async def delete_by_topic_id(topic_id: int) -> int:
#     conn = await db.get_db_connection()
#     try:
#         async with conn.transaction():
#             # Delete child answers first
#             await conn.execute(
#                 f"""
#                 DELETE FROM {TABLE_FILL_BLANKS_TEST_ANSWERS}
#                 WHERE fill_blanks_test_id IN (
#                     SELECT id FROM {TABLE_FILL_BLANKS_TESTS} WHERE topic_id=$1
#                 )
#                 """, topic_id
#             )
#             # Delete the tests
#             result = await conn.execute(
#                 f"DELETE FROM {TABLE_FILL_BLANKS_TESTS} WHERE topic_id=$1", topic_id
#             )
#             deleted = int(result.split()[-1])  # e.g., "DELETE 5" => 5
#             logger.info(f"Deleted {deleted} FillBlanksTest tests for topic_id={topic_id}")
#             return deleted
#     except Exception as e:
#         logger.error(f"❌ Error in delete_by_topic_id: {e}")
#         return 0
#     finally:
#         await conn.close()

async def delete_by_topic_id(topic_id: int) -> int:
    try:
        conn = await db.get_db_connection()
        try:
            async with conn.transaction():
                # Delete dependent answers first
                await conn.execute(
                    f"""
                    DELETE FROM {TABLE_FILL_BLANKS_TEST_ANSWERS}
                    WHERE fill_blanks_test_id IN (
                        SELECT id FROM {TABLE_FILL_BLANKS_TESTS} WHERE topic_id = $1
                    )
                    """,
                    topic_id
                )

                # Delete tests and count how many were deleted using RETURNING
                deleted_tests = await conn.fetch(
                    f"""
                    DELETE FROM {TABLE_FILL_BLANKS_TESTS}
                    WHERE topic_id = $1
                    RETURNING id
                    """,
                    topic_id
                )
                deleted_count = len(deleted_tests)

                logger.info(f"✅ Deleted {deleted_count} fill_blanks_tests for topic_id={topic_id}")
                return deleted_count
        except Exception as e:
            logger.error(f"ERror in conn.transaction: {e}")

    except Exception as e:
        logger.error(f"❌ Error in delete_by_topic_id for topic_id={topic_id}: {e}")
        return 0



async def get_by_topic_id(topic_id: int) -> list[FillBlanksTest]:
    conn = await db.get_db_connection()
    rows = await conn.fetch(f"""
        SELECT * FROM {TABLE_FILL_BLANKS_TESTS}
        WHERE topic_id = $1
        ORDER BY id
    """, topic_id)
    await conn.close()
    return [FillBlanksTest(id=row["id"], text=row["text"], topic_id=row["topic_id"]) for row in rows]

async def get_by_id(id: int) -> FillBlanksTest:
    conn = await db.get_db_connection()
    row = await conn.fetchrow(f"""
        SELECT * FROM {TABLE_FILL_BLANKS_TESTS}
        WHERE id = $1
    """, id)
    await conn.close()
    if row:
        return FillBlanksTest(id=row["id"], text=row["text"], topic_id=row["topic_id"])
    return None
