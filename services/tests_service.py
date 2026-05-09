import db
from models import Test, TestOption
from logger import logger

TABLE_NAME = "tests"
TABLE_TESTS = "tests"
TABLE_OPTIONS = "test_options"

async def get_all():
    conn = await db.get_db_connection()
    query = f"SELECT * FROM {TABLE_NAME}"
    try:
        rows = await conn.fetch(query)
        return [Test(
            id=row["id"],
            question=row["question"],
            image_id=row["image_id"],
            topic_id=row["topic_id"]
        ) for row in rows]
    except Exception as e:
        logger.error(f"Error fetching all tests: {e}")
        return []
    finally:
        await conn.close()

async def get_all_by_topic(topic_id: int):
    conn = await db.get_db_connection()
    query = f"SELECT * FROM {TABLE_NAME} where topic_id = $1"
    try:
        rows = await conn.fetch(query, topic_id)
        return [Test(
            id=row["id"],
            question=row["question"],
            image_id=row["image_id"],
            topic_id=row["topic_id"]
        ) for row in rows]
    except Exception as e:
        logger.error(f"Error fetching all tests by topic id: {e}")
        return []
    finally:
        await conn.close()

async def get_by_id(id: int) -> Test | None:
    conn = await db.get_db_connection()
    query = f"SELECT * FROM {TABLE_NAME} WHERE id = $1"
    try:
        row = await conn.fetchrow(query, id)
        if not row:
            logger.info(f"No test found with id = {id}")
            return None
        return Test(
            id=row["id"],
            question=row["question"],
            image_id=row["image_id"],
            topic_id=row["topic_id"]
        )
    except Exception as e:
        logger.error(f"Error fetching test by ID: {e}")
        return None
    finally:
        await conn.close()

async def create(test: Test):
    conn = await db.get_db_connection()
    query = f"""
        INSERT INTO {TABLE_NAME} (question, image_id, topic_id)
        VALUES ($1, $2, $3)
    """
    try:
        await conn.execute(query, test.question, test.image_id, test.topic_id)
    except Exception as e:
        logger.error(f"Error creating test: {e}")
    finally:
        await conn.close()

async def update(test: Test):
    conn = await db.get_db_connection()
    query = f"""
        UPDATE {TABLE_NAME}
        SET question = $1,
            image_id = $2,
            topic_id = $3
        WHERE id = $4
    """
    try:
        await conn.execute(query, test.question, test.image_id, test.topic_id, test.id)
    except Exception as e:
        logger.error(f"Error updating test: {e}")
    finally:
        await conn.close()

async def delete_by_id(id: int):
    conn = await db.get_db_connection()
    query = f"DELETE FROM {TABLE_NAME} WHERE id = $1"
    try:
        await conn.execute(query, id)
        logger.info(f"Deleted test with id = {id}")
    except Exception as e:
        logger.error(f"Error deleting test: {e}")
    finally:
        await conn.close()

async def save_test_with_options(test: Test, options: list[TestOption]):
    conn = await db.get_db_connection()
    try:
        async with conn.transaction():  # Ensures rollback if anything fails

            # Insert test and get its id
            query_test = f"""
                INSERT INTO {TABLE_TESTS} (question, image_id, topic_id)
                VALUES ($1, $2, $3)
                RETURNING id
            """
            test_id_row = await conn.fetchrow(query_test, test.question, test.image_id, test.topic_id)
            test_id = test_id_row["id"]

            # Insert all options
            query_option = f"""
                INSERT INTO {TABLE_OPTIONS} (option, is_correct, test_id)
                VALUES ($1, $2, $3)
            """

            for option in options:
                await conn.execute(query_option, option.option, option.is_correct, test_id)

            logger.info(f"Test with id={test_id} and {len(options)} options saved successfully.")

    except Exception as e:
        logger.error(f"❌ Error in save_test_with_options: {e}")
    finally:
        await conn.close()


async def delete_by_topic_id(topic_id: int):
    conn = await db.get_db_connection()
    query = "DELETE FROM tests WHERE topic_id = $1"
    try:
        await conn.execute(query, topic_id)
        logger.info(f"✅ Deleted all tests with topic_id={topic_id}")
    except Exception as e:
        logger.error(f"Error deleting tests by topic_id={topic_id}: {e}")
    finally:
        await conn.close()


async def get_random_tests_by_topic(topic_id: int, count: int) -> list[Test]:
    conn = await db.get_db_connection()
    try:
        query = f"""
            SELECT id, question, image_id, topic_id
            FROM {TABLE_TESTS}
            WHERE topic_id = $1
            ORDER BY RANDOM()
            LIMIT $2
        """
        rows = await conn.fetch(query, topic_id, count)
        return [Test(id=row["id"], question=row["question"], image_id=row["image_id"], topic_id=row["topic_id"]) for row in rows]
    except Exception as e:
        logger.error(f"❌ Error in get_random_tests_by_topic: {e}")
        return []
    finally:
        await conn.close()


async def get_with_options_by_id(test_id: int) -> Test | None:
    conn = await db.get_db_connection()
    try:
        query_test = f"""
            SELECT id, question, image_id, topic_id
            FROM {TABLE_TESTS}
            WHERE id = $1
        """
        row = await conn.fetchrow(query_test, test_id)
        if not row:
            return None
        
        test = Test(id=row["id"], question=row["question"], image_id=row["image_id"], topic_id=row["topic_id"])

        query_options = f"""
            SELECT id, option, is_correct, test_id
            FROM {TABLE_OPTIONS}
            WHERE test_id = $1
        """
        rows = await conn.fetch(query_options, test_id)
        test.options = [TestOption(id=r["id"], option=r["option"], is_correct=r["is_correct"], test_id=r["test_id"]) for r in rows]

        return test

    except Exception as e:
        logger.error(f"❌ Error in get_with_options_by_id: {e}")
        return None
    finally:
        await conn.close()
