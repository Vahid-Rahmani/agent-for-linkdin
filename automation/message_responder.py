import asyncio
from rich.console import Console
from rich.prompt import Confirm
from config.settings import Settings
from config.constants import LinkedInUrls
from database.local_db import Database
from auth.session_manager import SessionManager
from ai.reply_drafter import ReplyDrafter

console = Console()


class MessageResponder:
    def __init__(self, session: SessionManager, page):
        self.session = session
        self.page = page
        self.db = Database()
        self.settings = Settings()
        self.ai_drafter = ReplyDrafter()

    async def respond_to_message(self, message, auto_approve=False):
        draft = await self.ai_drafter.draft_reply_to_message(message)

        console.print(f"\n[bold cyan]Message from {message.get('sender', 'Unknown')}:[/bold cyan]")
        console.print(f"  {message.get('content', '')}")
        console.print(f"\n[bold green]AI Draft Reply:[/bold green]")
        console.print(f"  {draft}\n")

        if not auto_approve:
            if not Confirm.ask("Send this reply?"):
                console.print("[yellow]Reply skipped.[/yellow]")
                self.db.mark_message_processed(message["id"], draft)
                return False

        try:
            conv_url = message.get("sender_profile", "")
            if conv_url:
                await self.page.goto(conv_url, wait_until="domcontentloaded", timeout=60000)
                await asyncio.sleep(3)
                await self.session.random_delay(2, 4)

                msg_input = self.page.get_by_role("textbox", name="Write a message…")
                await msg_input.click()
                await asyncio.sleep(1)
                await self.page.keyboard.type(draft, delay=30)
                await self.session.random_delay(1, 2)

                send_btn = self.page.get_by_role("button", name="Send")
                for _ in range(20):
                    if await send_btn.is_enabled():
                        break
                    await asyncio.sleep(0.5)

                await send_btn.click()
                await self.session.random_delay(2, 3)

                self.db.mark_message_responded(message["id"])
                self.db.mark_message_processed(message["id"], draft)
                self.db.log_action(
                    "message_reply", conv_url, draft[:100], "success"
                )
                console.print("[green]Message sent![/green]")
                return True

            console.print("[red]Could not send message[/red]")
            return False

        except Exception as e:
            console.print(f"[red]Error sending message: {e}[/red]")
            return False

    async def respond_to_all_pending(self, auto_approve=False):
        pending = self.db.get_unprocessed_messages()
        if not pending:
            console.print("[yellow]No pending messages to respond to.[/yellow]")
            return []

        console.print(f"[blue]Found {len(pending)} pending messages[/blue]")
        results = []

        for message in pending[:self.settings.MAX_MESSAGES_PER_HOUR]:
            result = await self.respond_to_message(message, auto_approve)
            results.append(result)
            await self.session.random_delay(3, 7)

        return results
