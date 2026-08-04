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
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
    GITHUB_REPO = os.getenv("GITHUB_REPO", "Vahid-Rahmani/agent-for-linkdin")
    GITHUB_API_URL = os.getenv("GITHUB_API_URL", "https://api.github.com")
    IMAGE_OUTPUT_DIR = str(BASE_DIR / "assets" / "images")
    IMAGE_WIDTH = int(os.getenv("IMAGE_WIDTH", "1024"))
    IMAGE_HEIGHT = int(os.getenv("IMAGE_HEIGHT", "1024"))
    IMAGE_MODEL = os.getenv("IMAGE_MODEL", "turbo")
    POLLINATIONS_API_KEY = os.getenv("POLLINATIONS_API_KEY", "")
    HF_TOKEN = os.getenv("HF_TOKEN", "")
    HF_MODEL = os.getenv("HF_MODEL", "stabilityai/stable-diffusion-3-medium-diffusers")
    HF_API_URL = os.getenv("HF_API_URL", "https://router.huggingface.co/hf-inference/models")
