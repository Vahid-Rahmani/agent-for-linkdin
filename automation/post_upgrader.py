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
            await self.page.goto(post_url, wait_until="networkidle")
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

            edit_btn = await self.page.query_selector(
                "button.feed-shared-update-v2__edit-btn, button[aria-label='Edit']"
            )
            if edit_btn:
                await edit_btn.click()
                await self.session.random_delay(2, 3)

                editor = await self.page.wait_for_selector(
                    "div.share-creation-state__editor, div.ql-editor", timeout=10000
                )
                if editor:
                    await editor.click()
                    await self.page.keyboard.press("Control+a")
                    await self.page.keyboard.press("Delete")
                    await self.session.random_delay(0.5, 1)

                    await self.page.keyboard.type(improved, delay=30)
                    await self.session.random_delay(2, 3)

                    save_btn = await self.page.query_selector(
                        "button.share-actions__primary-action"
                    )
                    if save_btn:
                        await save_btn.click()
                        await self.session.random_delay(3, 5)

                        self.db.log_action(
                            "post_upgrade", post_url, improved[:100], "success"
                        )
                        console.print("[bold green]Post updated successfully![/bold green]")
                        return True

            console.print("[red]Could not edit post (might be older than 1 hour)[/red]")
            return False

        except Exception as e:
            console.print(f"[red]Error improving post: {e}[/red]")
            return False
