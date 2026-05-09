from base import bot, dp
import asyncio
from aiogram import F
from aiogram.types import *
from logger import logger
from handlers.base_handler import router as  base_router
from handlers.startpoint_handler import router as startup_router
from handlers.admin_handler import router as admin_router
from handlers.user_handler import router as user_router
import tasks

dp.include_router(base_router)
dp.include_router(startup_router)
dp.include_router(admin_router)
dp.include_router(user_router)

async def main():
    logger.info("Starting....")
    asyncio.create_task(tasks.premium_watcher_task())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())    