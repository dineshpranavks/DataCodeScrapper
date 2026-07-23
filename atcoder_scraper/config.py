import os
from pathlib import Path
from dotenv import load_dotenv

# Base Directory of the project
BASE_DIR = Path(__file__).resolve().parent

# Load environment variables from .env file
load_dotenv(BASE_DIR / ".env")

# Database configurations
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "atcoder")

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "scraper.log"

# XML Output Directory
XML_DIR = BASE_DIR / "xml"
XML_DIR.mkdir(exist_ok=True)

# Scraper Configuration
UPDATE_INTERVAL_HOURS = int(os.getenv("UPDATE_INTERVAL_HOURS", 24))
ATCODER_BASE_URL = "https://atcoder.jp"

# API Configuration
API_PORT = int(os.getenv("API_PORT", 8000))
