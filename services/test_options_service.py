import db
from models import TestOption
from logger import logger

TABLE_NAME = "test_options"

async def get_all():
    conn = await db.get_db_connection()
    query = f"SELECT * FROM {TABLE_NAME}"
    try:
        rows = await conn.fetch(query)
        return [TestOption(
            id=row["id"],
            option=row["option"],
            is_correct=row["is_correct"],
            test_id=row["test_id"]
        ) for row in rows]
    except Exception as e:
        logger.error(f"Error fetching all test options: {e}")
        return []
    finally:
        await conn.close()

async def get_all_by_test_id(test_id: int):
    conn = await db.get_db_connection()
    query = f"SELECT * FROM {TABLE_NAME} where test_id = $1"
    try:
        rows = await conn.fetch(query, test_id)
        return [TestOption(
            id=row["id"],
            option=row["option"],
            is_correct=row["is_correct"],
            test_id=row["test_id"]
        ) for row in rows]
    except Exception as e:
        logger.error(f"Error fetching all test options by test id: {e}")
        return []
    finally:
        await conn.close()

async def get_by_id(id: int):
    conn = await db.get_db_connection()
    query = f"SELECT * FROM {TABLE_NAME} WHERE id = $1"
    try:
        row = await conn.fetchrow(query, id)
        if not row:
            logger.info(f"No test option found with id = {id}")
            return None
        return TestOption(
            id=row["id"],
            option=row["option"],
            is_correct=row["is_correct"],
            test_id=row["test_id"]
        )
    except Exception as e:
        logger.error(f"Error fetching test option by ID: {e}")
        return None
    finally:
        await conn.close()

async def get_correct_option_by_test(test_id: int):
    conn = await db.get_db_connection()
    query = f"SELECT * FROM {TABLE_NAME} WHERE test_id = $1 AND is_correct = $2"
    try:
        row = await conn.fetchrow(query, test_id, True)
        if not row:
            logger.info(f"No test option found with id = {id}")
            return None
        return TestOption(
            id=row["id"],
            option=row["option"],
            is_correct=row["is_correct"],
            test_id=row["test_id"]
        )
    except Exception as e:
        logger.error(f"Error fetching test option by ID: {e}")
        return None
    finally:
        await conn.close()

async def create(test_option: TestOption):
    conn = await db.get_db_connection()
    query = f"""
        INSERT INTO {TABLE_NAME} (option, is_correct, test_id)
        VALUES ($1, $2, $3)
    """
    try:
        await conn.execute(query, test_option.option, test_option.is_correct, test_option.test_id)
    except Exception as e:
        logger.error(f"Error creating test option: {e}")
    finally:
        await conn.close()

async def update(test_option: TestOption):
    conn = await db.get_db_connection()
    query = f"""
        UPDATE {TABLE_NAME}
        SET option = $1,
            is_correct = $2,
            test_id = $3
        WHERE id = $4
    """
    try:
        await conn.execute(query, test_option.option, test_option.is_correct, test_option.test_id, test_option.id)
    except Exception as e:
        logger.error(f"Error updating test option: {e}")
    finally:
        await conn.close()

async def delete_by_id(id: int):
    conn = await db.get_db_connection()
    query = f"DELETE FROM {TABLE_NAME} WHERE id = $1"
    try:
        await conn.execute(query, id)
        logger.info(f"Deleted test option with id = {id}")
    except Exception as e:
        logger.error(f"Error deleting test option: {e}")
    finally:
        await conn.close()
