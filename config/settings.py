import os
from dotenv import load_dotenv

load_dotenv()

# Scraping settings
REQUEST_TIMEOUT = 10
MAX_ITEMS_PER_SOURCE = 20
USER_AGENT_ROTATION = True

# Posting settings
MORNING_POST_TIME = os.getenv('MORNING_POST_TIME', '09:00')
EVENING_POST_TIME = os.getenv('EVENING_POST_TIME', '18:00')
MAX_DAILY_POSTS = int(os.getenv('MAX_DAILY_POSTS', 5))

# Database settings
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///jobs.db')

# WhatsApp settings
WHATSAPP_SESSION_DIR = os.getenv('WHATSAPP_SESSION_DIR', '/tmp/whatsapp-session')

# Image settings
IMAGE_WIDTH = 1080
IMAGE_HEIGHT = 1080

# Logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = '/tmp/scraper.log'