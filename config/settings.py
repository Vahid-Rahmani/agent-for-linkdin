import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


class Settings:
    OPENCODE_API_KEY = os.getenv("OPENCODE_API_KEY", "")
    OPENCODE_BASE_URL = "https://opencode.ai/zen/v1"
    OPENCODE_MODEL = "big-pickle"
    LINKEDIN_PROFILE_URL = os.getenv("LINKEDIN_PROFILE_URL", "https://www.linkedin.com/in/vahid-rahmani-699944417")
    BROWSER_DATA_DIR = str(BASE_DIR / "browser_data")
    STATE_FILE = str(BASE_DIR / "linkedin_state.json")
    DATABASE_PATH = str(BASE_DIR / "linkedin_agent.db")
    HEADLESS = False
    MIN_DELAY = 2
    MAX_DELAY = 5
    MAX_COMMENTS_PER_HOUR = 10
    MAX_MESSAGES_PER_HOUR = 20
