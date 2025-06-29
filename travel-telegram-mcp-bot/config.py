# config.py
import os
import logging
from dotenv import load_dotenv

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# --- Environment Configuration ---
load_dotenv()

# --- API Keys and Tokens ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# --- Model Configuration ---
GEMINI_MODEL = "gemini-2.0-flash"
MAX_TOOL_ITERATIONS = 5

# --- Validation ---
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file.")
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN not found in .env file.")