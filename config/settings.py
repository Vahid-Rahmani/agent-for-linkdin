import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


class Settings:
    GOOGLE_GEMINI_API_KEY = os.getenv("GOOGLE_GEMINI_API_KEY", "")
    LINKEDIN_PROFILE_URL = os.getenv("LINKEDIN_PROFILE_URL", "https://www.linkedin.com/in/vahid-rahmani-699944417")
    BROWSER_DATA_DIR = str(BASE_DIR / "browser_data")
    STATE_FILE = str(BASE_DIR / "linkedin_state.json")
    DATABASE_PATH = str(BASE_DIR / "linkedin_agent.db")
    GEMINI_MODEL = "gemini-2.5-flash"
    HEADLESS = False
    MIN_DELAY = 2
    MAX_DELAY = 5
    MAX_COMMENTS_PER_HOUR = 10
    MAX_MESSAGES_PER_HOUR = 20
