import asyncio
from rich.console import Console
from rich.prompt import Confirm
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

    async def publish_post(self, content, auto_approve=False):
        console.print("[bold blue]Preparing to publish post...[/bold blue]")
        console.print(f"\n[bold cyan]Post Content:[/bold cyan]\n{content}\n")

        if not auto_approve:
            if not Confirm.ask("Do you want to publish this post?"):
                console.print("[yellow]Post cancelled.[/yellow]")
                return False

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

            editor = dialog.locator('div[contenteditable="true"]').first
            await self.session.human_click(self.page, editor)
            await asyncio.sleep(1)

            await self.session.human_type(self.page, content)
            await self.session.random_delay(2, 3)

            post_button = dialog.get_by_role("button", name="Post")
            for _ in range(20):
                if await post_button.is_enabled():
                    break
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
