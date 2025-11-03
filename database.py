from loguru import logger
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from datetime import datetime
import config  # 👈 Import config instead of using os.getenv


class Database:
    def __init__(self):
        self.MONGODB_URI = config.MONGODB_URI
        self.DATABASE_NAME = config.DATABASE_NAME
        self.COLLECTION_USERS = "bot_users"
        self.COLLECTION_STATS = "bot_stats"
        
        try:
            self.client = MongoClient(self.MONGODB_URI)
            self.db = self.client[self.DATABASE_NAME]
            self.users = self.db[self.COLLECTION_USERS]
            self.stats = self.db[self.COLLECTION_STATS]
            
            # Test connection
            self.client.admin.command('ping')
            logger.info("✅ Bot Database connected successfully")
            
            # Create indexes
            self.users.create_index("user_id", unique=True)
            self.users.create_index([("joined_date", -1)])
            self.stats.create_index([("date", 1)], unique=True)
            
            logger.info("✅ Bot Database indexes created successfully")
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"❌ Bot Database connection failed: {e}")
            raise

    async def add_user(self, user_id: int, username: str, first_name: str, last_name: str = ""):
        """Add or update user in database"""
        try:
            result = self.users.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "username": username,
                        "first_name": first_name,
                        "last_name": last_name,
                        "last_active": datetime.now()
                    },
                    "$setOnInsert": {"joined_date": datetime.now()},
                    "$inc": {"total_starts": 1}
                },
                upsert=True
            )

            if result.upserted_id:
                logger.info(f"📝 New user added to database: {username} (ID: {user_id})")
            else:
                logger.info(f"📝 User updated in database: {username} (ID: {user_id})")

            await self.update_daily_stats()
            return True
            
        except Exception as e:
            logger.error(f"❌ Error adding user to database: {e}")
            return False

    async def update_daily_stats(self):
        """Update daily bot statistics"""
        try:
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            result = self.stats.update_one(
                {"date": today},
                {
                    "$inc": {"bot_starts": 1},
                    "$setOnInsert": {"date": today}
                },
                upsert=True
            )
            if result.upserted_id:
                logger.info(f"📊 New daily stats created for {today.strftime('%Y-%m-%d')}")
            else:
                logger.debug(f"📊 Daily stats updated for {today.strftime('%Y-%m-%d')}")
            return True
        except Exception as e:
            logger.error(f"❌ Error updating daily stats: {e}")
            return False

    async def get_user(self, user_id: int):
        """Get user data from database"""
        try:
            user = self.users.find_one({"user_id": user_id})
            if user:
                logger.debug(f"📖 User data retrieved: {user_id}")
            else:
                logger.debug(f"📖 User not found in database: {user_id}")
            return user
        except Exception as e:
            logger.error(f"❌ Error getting user from database: {e}")
            return None

    async def get_total_users(self):
        """Get total number of users"""
        try:
            count = self.users.count_documents({})
            logger.debug(f"👥 Total users in database: {count}")
            return count
        except Exception as e:
            logger.error(f"❌ Error getting total users: {e}")
            return 0

    async def get_daily_stats(self, date=None):
        """Get daily statistics"""
        try:
            if date is None:
                date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            stats = self.stats.find_one({"date": date})
            if stats:
                logger.debug(f"📊 Daily stats retrieved for {date.strftime('%Y-%m-%d')}")
            else:
                logger.debug(f"📊 No daily stats found for {date.strftime('%Y-%m-%d')}")
            return stats
        except Exception as e:
            logger.error(f"❌ Error getting daily stats: {e}")
            return None

    async def get_active_users_today(self):
        """Get number of active users today"""
        try:
            today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            count = self.users.count_documents({
                "last_active": {"$gte": today_start}
            })
            logger.debug(f"👥 Active users today: {count}")
            return count
        except Exception as e:
            logger.error(f"❌ Error getting active users: {e}")
            return 0


# Create global database instance
db = Database()
