import db
from models import FillBlanksTestAnswer
from logger import logger

TABLE_NAME = "fill_blanks_test_answers"

async def get_all():
    conn = await db.get_db_connection()
    query = f"SELECT * FROM {TABLE_NAME}"
    try:
        rows = await conn.fetch(query)
        return [FillBlanksTestAnswer(
            id=row["id"],
            fill_blanks_test_id=row["fill_blanks_test_id"],
            number=row["number"],
            answer=row["answer"]
        ) for row in rows]
    except Exception as e:
        logger.error(f"Error fetching all fill blanks test answers: {e}")
        return []
    finally:
        await conn.close()

async def get_by_id(id: int):
    conn = await db.get_db_connection()
    query = f"SELECT * FROM {TABLE_NAME} WHERE id = $1"
    try:
        row = await conn.fetchrow(query, id)
        if not row:
            logger.info(f"No fill blanks test answer found with id = {id}")
            return None
        return FillBlanksTestAnswer(
            id=row["id"],
            fill_blanks_test_id=row["fill_blanks_test_id"],
            number=row["number"],
            answer=row["answer"]
        )
    except Exception as e:
        logger.error(f"Error fetching fill blanks test answer by ID: {e}")
        return None
    finally:
        await conn.close()

async def create(answer: FillBlanksTestAnswer):
    conn = await db.get_db_connection()
    query = f"""
        INSERT INTO {TABLE_NAME} (fill_blanks_test_id, number, answer)
        VALUES ($1, $2, $3)
    """
    try:
        await conn.execute(query, answer.fill_blanks_test_id, answer.number, answer.answer)
    except Exception as e:
        logger.error(f"Error creating fill blanks test answer: {e}")
    finally:
        await conn.close()

async def update(answer: FillBlanksTestAnswer):
    conn = await db.get_db_connection()
    query = f"""
        UPDATE {TABLE_NAME}
        SET fill_blanks_test_id = $1,
            number = $2,
            answer = $3
        WHERE id = $4
    """
    try:
        await conn.execute(query, answer.fill_blanks_test_id, answer.number, answer.answer, answer.id)
    except Exception as e:
        logger.error(f"Error updating fill blanks test answer: {e}")
    finally:
        await conn.close()

async def delete_by_id(id: int):
    conn = await db.get_db_connection()
    query = f"DELETE FROM {TABLE_NAME} WHERE id = $1"
    try:
        await conn.execute(query, id)
        logger.info(f"Deleted fill blanks test answer with id = {id}")
    except Exception as e:
        logger.error(f"Error deleting fill blanks test answer: {e}")
    finally:
        await conn.close()

async def get_by_test_id(test_id: int) -> list[FillBlanksTestAnswer]:
    conn = await db.get_db_connection()
    rows = await conn.fetch(f"""
        SELECT * FROM {TABLE_NAME}
        WHERE fill_blanks_test_id = $1
        ORDER BY number::INT
    """, test_id)
    await conn.close()
    return [
        FillBlanksTestAnswer(
            id=row["id"],
            fill_blanks_test_id=row["fill_blanks_test_id"],
            number=row["number"],
            answer=row["answer"]
        ) for row in rows
    ]
