import asyncio
from pathlib import Path
from rich.console import Console
from config.settings import Settings
from config.constants import LinkedInUrls, LinkedInSelectors
from database.local_db import Database
from auth.session_manager import SessionManager

console = Console()


class Publisher:
    def __init__(self, session: SessionManager, page):
        self.session = session
        self.page = page
        self.db = Database()
        self.settings = Settings()

    async def publish_post(self, content, image_path=None):
        console.print("[bold blue]Preparing to publish post...[/bold blue]")
        console.print(f"\n[bold cyan]Post Content:[/bold cyan]\n{content}\n")

        try:
            await self.page.goto(LinkedInUrls.HOME, wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(3)
            await self.session.random_delay(3, 5)

            await self.session.human_scroll(self.page)
            await self.session.human_delay(0.5, 1.5)

            start_post = self.page.get_by_role("button", name="Start a post")
            await self.session.human_click(self.page, start_post)
            await asyncio.sleep(3)
            await self.session.random_delay(2, 3)

            dialog = self.page.locator('div[role="dialog"]')

            editor_loc = dialog.locator('div[contenteditable="true"]')
            if await editor_loc.count() == 0:
                editor_loc = self.page.locator('div[contenteditable="true"]')
            if await editor_loc.count() == 0:
                editor_loc = self.page.get_by_role("textbox", name="Text")
            editor = editor_loc.first
            await self.session.human_click(self.page, editor)
            await asyncio.sleep(1)

            await self.session.human_type(self.page, content)
            await self.session.random_delay(2, 3)

            if image_path and Path(image_path).exists():
                media_btn = dialog.locator(
                    'button[aria-label="Add media"], '
                    'button[aria-label="Add a photo to your post"]'
                ).first
                await self.session.human_click(self.page, media_btn)
                file_input = dialog.locator('input[type="file"]').first
                await file_input.set_input_files(str(image_path))
                console.print("[blue]Image attached...[/blue]")
                await asyncio.sleep(2)
                await self.session.random_delay(3, 5)

            post_button = None
            for loc in (
                dialog.locator('button.share-actions__primary-action').filter(has_text="Post"),
                dialog.get_by_role("button", name="Post"),
                self.page.get_by_role("button", name="Post"),
                dialog.locator('button').filter(has_text="Post"),
            ):
                try:
                    if await loc.count() > 0:
                        post_button = loc
                        break
                except Exception:
                    continue

            if post_button is None:
                console.print("[red]Post button not found in composer[/red]")
                self.db.log_action("post_publish", LinkedInUrls.HOME, content[:100], "error: post button not found")
                return False

            for _ in range(20):
                try:
                    if await post_button.is_enabled():
                        break
                except Exception:
                    pass
                await asyncio.sleep(0.5)

            await self.session.human_click(self.page, post_button)
            await self.session.random_delay(3, 5)

            self.db.log_action("post_publish", LinkedInUrls.HOME, content[:100], "success")
            console.print("[bold green]Post published successfully![/bold green]")
            return True

        except Exception as e:
            console.print(f"[red]Error publishing post: {e}[/red]")
            self.db.log_action("post_publish", LinkedInUrls.HOME, content[:100], f"error: {e}")
            return False
