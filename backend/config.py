import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")
load_dotenv(ROOT.parent / ".env")

DATABASE_PATH = os.environ.get("DATABASE_PATH", str(ROOT / "studypilot.db"))
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")
USER_ID = 1
DEFAULT_AVAILABLE_MINUTES = 180
PLAN_HORIZON_DAYS = 7
RESCHEDULE_HORIZON_DAYS = 14
SESSION_START = "09:00"
SESSION_GAP_MINUTES = 10
MIN_CHUNK = 25
MAX_CHUNK = 90
GEMINI_TIMEOUT_SECONDS = 8
