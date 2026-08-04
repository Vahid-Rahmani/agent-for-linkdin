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

            start_post = self.page.get_by_role("button", name="Start a post")
            await start_post.click()
            await asyncio.sleep(3)
            await self.session.random_delay(2, 3)

            editor = self.page.get_by_role("textbox", name="Text editor for creating content")
            await editor.click()
            await asyncio.sleep(1)
            await self.session.random_delay(1, 2)

            await self.page.keyboard.type(content, delay=30)
            await self.session.random_delay(2, 3)

            post_button = self.page.get_by_role("button", name="Post")
            await post_button.click()
            await self.session.random_delay(3, 5)

            self.db.log_action("post_publish", LinkedInUrls.HOME, content[:100], "success")
            console.print("[bold green]Post published successfully![/bold green]")
            return True

        except Exception as e:
            console.print(f"[red]Error publishing post: {e}[/red]")
            self.db.log_action("post_publish", LinkedInUrls.HOME, content[:100], f"error: {e}")
            return False
