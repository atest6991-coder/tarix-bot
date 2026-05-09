import asyncio
from datetime import datetime, timezone
from services import user_service
from models import User
from logger import logger

async def premium_watcher_task():
    while True:
        try:
            print("premium_watcher_task is starting...")
            now = datetime.now(timezone.utc)
            users = await user_service.get_all()
            
            for user in users:
                if user.is_premium and user.premium_expiry_at and user.premium_expiry_at < now:
                    user.is_premium = False
                    user.premium_expiry_at = None
                    await user_service.update(user)
                    logger.info(f"Premium expired and removed for user {user.id}")

            await asyncio.sleep(1800)  # sleep 30 minutes

        except Exception as e:
            logger.error(f"Error in premium_watcher_task: {e}")
            await asyncio.sleep(60)  # wait 1 minute before retry on error
