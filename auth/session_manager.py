import asyncio
import random
from pathlib import Path
from playwright.async_api import async_playwright, BrowserContext
from config.settings import Settings


class SessionManager:
    def __init__(self):
        self.settings = Settings()
        self.playwright = None
        self.browser = None
        self.context: BrowserContext = None

    async def start(self, headless=None):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=headless if headless is not None else self.settings.HEADLESS,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
            ],
        )

        storage = self.settings.STATE_FILE
        context_args = {
            "viewport": {"width": 1920, "height": 1080},
            "user_agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/131.0.0.0 Safari/537.36"
            ),
        }

        if Path(storage).exists():
            context_args["storage_state"] = storage

        self.context = await self.browser.new_context(**context_args)
        return self.context

    async def save_session(self):
        if self.context:
            await self.context.storage_state(path=self.settings.STATE_FILE)

    async def close(self):
        if self.context:
            await self.save_session()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    @staticmethod
    async def random_delay(min_s=None, max_s=None):
        min_s = min_s or Settings.MIN_DELAY
        max_s = max_s or Settings.MAX_DELAY
        await asyncio.sleep(random.uniform(min_s, max_s))
