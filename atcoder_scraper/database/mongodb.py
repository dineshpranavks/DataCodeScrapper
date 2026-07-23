import logging
from pymongo import MongoClient, UpdateOne
from pymongo.collection import Collection
from pymongo.database import Database
from typing import List, Dict, Any

from config import MONGODB_URI, MONGODB_DB_NAME
from database.models import Contest, Problem

logger = logging.getLogger(__name__)

class MongoDB:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoDB, cls).__new__(cls)
            cls._instance._init_db()
        return cls._instance

    def _init_db(self):
        try:
            self.client = MongoClient(MONGODB_URI)
            self.db: Database = self.client[MONGODB_DB_NAME]
            self.contests: Collection = self.db['contests']
            self.problems: Collection = self.db['problems']
            self._create_indexes()
            logger.info("Successfully connected to MongoDB and initialized collections.")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    def _create_indexes(self):
        # Create indexes to ensure uniqueness and fast lookup
        self.contests.create_index("contest_id", unique=True)
        self.contests.create_index("contest_name")
        self.problems.create_index("problem_id", unique=True)
        self.problems.create_index("contest_id")
        logger.info("MongoDB indexes verified/created.")

    def upsert_contests(self, contests_data: List[Contest]):
        if not contests_data:
            return
        operations = [
            UpdateOne(
                {"contest_id": contest["contest_id"]},
                {"$set": contest},
                upsert=True
            )
            for contest in contests_data
        ]
        try:
            result = self.contests.bulk_write(operations)
            logger.info(f"Contests upserted: {result.upserted_count}, modified: {result.modified_count}")
        except Exception as e:
            logger.error(f"Error upserting contests: {e}")

    def upsert_problems(self, problems_data: List[Problem]):
        if not problems_data:
            return
        operations = [
            UpdateOne(
                {"problem_id": problem["problem_id"]},
                {"$set": problem},
                upsert=True
            )
            for problem in problems_data
        ]
        try:
            result = self.problems.bulk_write(operations)
            logger.info(f"Problems upserted: {result.upserted_count}, modified: {result.modified_count}")
        except Exception as e:
            logger.error(f"Error upserting problems: {e}")

# Global instance for easy import
db = MongoDB()
