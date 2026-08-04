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

    @staticmethod
    async def human_delay(min_s=0.4, max_s=1.2):
        await asyncio.sleep(random.uniform(min_s, max_s))

    async def human_move(self, page, target):
        box = await target.bounding_box()
        if not box:
            return
        tx = box["x"] + box["width"] / 2
        ty = box["y"] + box["height"] / 2

        offset_x = random.uniform(-35, 35)
        offset_y = random.uniform(-35, 35)
        await page.mouse.move(
            tx + offset_x, ty + offset_y,
            steps=random.randint(25, 45),
        )
        await asyncio.sleep(random.uniform(0.05, 0.2))

        jitter_x = random.uniform(-3, 3)
        jitter_y = random.uniform(-3, 3)
        await page.mouse.move(
            tx + jitter_x, ty + jitter_y,
            steps=random.randint(6, 12),
        )
        await asyncio.sleep(random.uniform(0.05, 0.15))

    async def human_click(self, page, target):
        await target.scroll_into_view_if_needed()
        await asyncio.sleep(random.uniform(0.2, 0.6))
        box = await target.bounding_box()
        if not box:
            await target.click()
            return
        await self.human_move(page, target)
        await asyncio.sleep(random.uniform(0.15, 0.4))
        x = box["x"] + box["width"] / 2
        y = box["y"] + box["height"] / 2
        await page.mouse.click(x, y)
        await self.human_delay(0.4, 1.2)

    async def human_type(self, page, text):
        for char in text:
            if char == "\n":
                await page.keyboard.press("Enter")
                await asyncio.sleep(random.uniform(0.1, 0.25))
            elif char in " ,.;!?:…-":
                await asyncio.sleep(random.uniform(0.15, 0.45))
                await page.keyboard.type(char)
            elif char in " \t":
                await asyncio.sleep(random.uniform(0.05, 0.15))
                await page.keyboard.type(char)
            else:
                await asyncio.sleep(random.uniform(0.03, 0.09))
                await page.keyboard.type(char)

            if random.random() < 0.015:
                await asyncio.sleep(random.uniform(0.3, 0.9))

    async def human_scroll(self, page, max_px=600):
        total = 0
        while total < max_px:
            step = random.randint(80, 200)
            await page.mouse.wheel(0, step)
            total += step
            await asyncio.sleep(random.uniform(0.2, 0.5))
