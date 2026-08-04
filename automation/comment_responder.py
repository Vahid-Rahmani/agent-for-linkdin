import asyncio
from rich.console import Console
from rich.prompt import Confirm
from config.settings import Settings
from database.local_db import Database
from auth.session_manager import SessionManager
from ai.reply_drafter import ReplyDrafter

console = Console()


class CommentResponder:
    def __init__(self, session: SessionManager, page):
        self.session = session
        self.page = page
        self.db = Database()
        self.settings = Settings()
        self.ai_drafter = ReplyDrafter()

    async def respond_to_comment(self, comment, post_context, auto_approve=False):
        draft = await self.ai_drafter.draft_reply_to_comment(comment, post_context)

        console.print(f"\n[bold cyan]Comment from {comment.get('author', 'Unknown')}:[/bold cyan]")
        console.print(f"  {comment.get('content', '')}")
        console.print(f"\n[bold green]AI Draft Reply:[/bold green]")
        console.print(f"  {draft}\n")

        if not auto_approve:
            if not Confirm.ask("Send this reply?"):
                console.print("[yellow]Reply skipped.[/yellow]")
                self.db.mark_comment_processed(comment["id"], draft)
                return False

        try:
            post_url = comment.get("post_url", "")
            if post_url:
                await self.page.goto(post_url, wait_until="domcontentloaded", timeout=60000)
                await asyncio.sleep(3)
                await self.session.random_delay(2, 4)

                reply_buttons = await self.page.query_selector_all(
                    "button.comments-comment-item__reply-button"
                )
                if reply_buttons:
                    await reply_buttons[0].click()
                    await self.session.random_delay(1, 2)

                comment_box = await self.page.query_selector(
                    "textarea.comments-comment-box__input"
                )
                if comment_box:
                    await comment_box.click()
                    await self.page.keyboard.type(draft, delay=30)
                    await self.session.random_delay(1, 2)

                    submit_btn = await self.page.query_selector(
                        "button.comments-comment-box__submit-button"
                    )
                    if submit_btn:
                        await submit_btn.click()
                        await self.session.random_delay(2, 3)

                        self.db.mark_comment_responded(comment["id"])
                        self.db.mark_comment_processed(comment["id"], draft)
                        self.db.log_action(
                            "comment_reply", post_url, draft[:100], "success"
                        )
                        console.print("[green]Reply sent![/green]")
                        return True

            console.print("[red]Could not send reply[/red]")
            return False

        except Exception as e:
            console.print(f"[red]Error sending reply: {e}[/red]")
            return False

    async def respond_to_all_pending(self, auto_approve=False):
        pending = self.db.get_unprocessed_comments()
        if not pending:
            console.print("[yellow]No pending comments to respond to.[/yellow]")
            return []

        console.print(f"[blue]Found {len(pending)} pending comments[/blue]")
        results = []

        for comment in pending[:self.settings.MAX_COMMENTS_PER_HOUR]:
            result = await self.respond_to_comment(comment, "", auto_approve)
            results.append(result)
            await self.session.random_delay(3, 7)

        return results
