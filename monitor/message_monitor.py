import asyncio
from rich.console import Console
from config.settings import Settings
from config.constants import LinkedInUrls
from database.local_db import Database
from auth.session_manager import SessionManager

console = Console()


class MessageMonitor:
    def __init__(self, session: SessionManager, page):
        self.session = session
        self.page = page
        self.db = Database()
        self.settings = Settings()

    async def scan_messages(self):
        try:
            await self.page.goto(LinkedInUrls.MESSAGES, wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(3)

            messages = []
            conversation_elements = await self.page.query_selector_all("li.occludable-update")

            for conv_el in conversation_elements[:20]:
                try:
                    sender_el = await conv_el.query_selector("span.msg-conversation-list-item__participant-names")
                    sender_name = await sender_el.inner_text() if sender_el else "Unknown"

                    preview_el = await conv_el.query_selector("span.msg-conversation-list-item__subtitle")
                    preview = await preview_el.inner_text() if preview_el else ""

                    unread = await conv_el.query_selector("span.msg-conversation-list-item__badge")

                    if unread and preview:
                        conv_link = await conv_el.query_selector("a")
                        conv_url = await conv_link.get_attribute("href") if conv_link else ""

                        if conv_url:
                            full_messages = await self._read_conversation(conv_url)
                            if full_messages:
                                last_msg = full_messages[-1]
                                is_new = self.db.save_message(
                                    sender_name=sender_name.strip(),
                                    sender_profile=conv_url,
                                    content=last_msg.get("content", preview),
                                )
                                if is_new:
                                    messages.append({
                                        "sender": sender_name.strip(),
                                        "content": last_msg.get("content", preview),
                                        "profile": conv_url,
                                    })
                except Exception:
                    continue

            return messages

        except Exception as e:
            console.print(f"[red]Error scanning messages: {e}[/red]")
            return []

    async def _read_conversation(self, conv_url):
        try:
            await self.page.goto(conv_url, wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(3)

            messages = []
            msg_elements = await self.page.query_selector_all("div.msg-s-event-list")

            for msg_el in msg_elements[-5:]:
                try:
                    sender_el = await msg_el.query_selector("span.msg-s-message-group__sender-name")
                    sender = await sender_el.inner_text() if sender_el else ""

                    content_el = await msg_el.query_selector("p.msg-s-event-list-item__content")
                    content = await content_el.inner_text() if content_el else ""

                    if content:
                        messages.append({"sender": sender.strip(), "content": content.strip()})
                except Exception:
                    continue

            return messages
        except Exception:
            return []

    async def get_pending_messages(self):
        pending = self.db.get_unprocessed_messages()
        return pending
