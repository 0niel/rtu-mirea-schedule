import os

from dotenv import load_dotenv

load_dotenv(".env")

SECRET_REFRESH_KEY = str(os.getenv("SECRET_REFRESH_KEY", None))

MAX_CONNECTIONS_COUNT = int(os.getenv("MAX_CONNECTIONS_COUNT", 10))
MIN_CONNECTIONS_COUNT = int(os.getenv("MIN_CONNECTIONS_COUNT", 10))

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://127.0.0.1:27017/")

API_V1_PREFIX = "/api"

DATABASE_NAME = "schedule"
SCHEDULE_COLLECTION_NAME = "schedule"
SESSION_COLLECTION_NAME = "session"
SCHEDULE_UPDATES_COLLECTION = "schedule_updates"
SCHEDULE_GROUPS_STATS = "schedule_groups_stats"
