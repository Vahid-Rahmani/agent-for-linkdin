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

            start_post = await self.page.query_selector("button.share-box-feed-entry__trigger")
            if start_post:
                await start_post.click()
                await asyncio.sleep(3)
                await self.session.random_delay(2, 3)

            editor = await self.page.wait_for_selector(
                "div.share-creation-state__editor, div.ql-editor, div[contenteditable='true']", timeout=30000
            )
            if editor:
                await editor.click()
                await asyncio.sleep(1)
                await self.session.random_delay(1, 2)

                await editor.fill("")
                await self.page.keyboard.type(content, delay=30)
                await self.session.random_delay(2, 3)

            post_button = await self.page.query_selector(
                "button.share-actions__primary-action"
            )
            if post_button:
                await post_button.click()
                await self.session.random_delay(3, 5)

                self.db.log_action("post_publish", LinkedInUrls.HOME, content[:100], "success")
                console.print("[bold green]Post published successfully![/bold green]")
                return True
            else:
                console.print("[red]Could not find Post button[/red]")
                return False

        except Exception as e:
            console.print(f"[red]Error publishing post: {e}[/red]")
            self.db.log_action("post_publish", LinkedInUrls.HOME, content[:100], f"error: {e}")
            return False
