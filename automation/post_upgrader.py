import asyncio
from rich.console import Console
from rich.prompt import Confirm
from config.settings import Settings
from database.local_db import Database
from auth.session_manager import SessionManager
from ai.post_improver import PostImprover

console = Console()


class PostUpgrader:
    def __init__(self, session: SessionManager, page):
        self.session = session
        self.page = page
        self.db = Database()
        self.settings = Settings()
        self.ai_improver = PostImprover()

    async def improve_post(self, post_url, focus="engagement", auto_approve=False):
        console.print(f"[bold blue]Improving post at: {post_url}[/bold blue]")

        try:
            await self.page.goto(post_url, wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(3)
            await self.session.random_delay(3, 5)

            content_el = await self.page.query_selector(
                "div.feed-shared-update-v2__description, span.feed-shared-text__text"
            )
            if not content_el:
                console.print("[red]Could not find post content[/red]")
                return False

            original_content = await content_el.inner_text()
            console.print(f"\n[bold cyan]Original Post:[/bold cyan]\n{original_content}\n")

            if focus == "engagement":
                improved = await self.ai_improver.make_more_engaging(original_content)
            elif focus == "algorithm":
                improved = await self.ai_improver.optimize_for_algorithm(original_content)
            else:
                improved = await self.ai_improver.improve_post(original_content, focus)

            console.print(f"\n[bold green]Improved Version:[/bold green]\n{improved}\n")

            if not auto_approve:
                if not Confirm.ask("Apply this improvement?"):
                    console.print("[yellow]Improvement cancelled.[/yellow]")
                    return False

            edit_btn = self.page.get_by_role("button", name="Edit")
            await self.session.human_click(self.page, edit_btn)
            await asyncio.sleep(3)
            await self.session.random_delay(2, 3)

            dialog = self.page.locator('div[role="dialog"]')

            editor = dialog.locator('div[contenteditable="true"]').first
            await self.session.human_click(self.page, editor)
            await self.page.keyboard.press("Control+a")
            await self.page.keyboard.press("Delete")
            await self.session.random_delay(0.5, 1)

            await self.session.human_type(self.page, improved)
            await self.session.random_delay(2, 3)

            save_btn = dialog.locator('button.share-actions__primary-action').filter(has_text="Save")
            for _ in range(20):
                if await save_btn.is_enabled():
                    break
                await asyncio.sleep(0.5)

            await self.session.human_click(self.page, save_btn)
            await self.session.random_delay(3, 5)

            self.db.log_action(
                "post_upgrade", post_url, improved[:100], "success"
            )
            console.print("[bold green]Post updated successfully![/bold green]")
            return True

        except Exception as e:
            console.print(f"[red]Error improving post: {e}[/red]")
            return False
