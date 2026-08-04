import asyncio
from rich.console import Console
from config.settings import Settings
from database.local_db import Database
from auth.session_manager import SessionManager

console = Console()


class CommentMonitor:
    def __init__(self, session: SessionManager, page):
        self.session = session
        self.page = page
        self.db = Database()
        self.settings = Settings()

    async def scan_comments_on_post(self, post_url):
        try:
            await self.page.goto(post_url, wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(3)

            comments = []
            comment_elements = await self.page.query_selector_all("div.comments-comment-item")

            for comment_el in comment_elements:
                try:
                    author_el = await comment_el.query_selector("a.comments-comment-item__author-link")
                    author_name = await author_el.inner_text() if author_el else "Unknown"
                    author_profile = await author_el.get_attribute("href") if author_el else ""

                    content_el = await comment_el.query_selector("span.comments-comment-item__main-content")
                    content = await content_el.inner_text() if content_el else ""

                    time_el = await comment_el.query_selector("time")
                    timestamp = await time_el.get_attribute("datetime") if time_el else ""

                    if content:
                        is_new = self.db.save_comment(
                            post_url=post_url,
                            author_name=author_name.strip(),
                            author_profile=author_profile,
                            content=content.strip(),
                            timestamp=timestamp,
                        )
                        if is_new:
                            comments.append({
                                "author": author_name.strip(),
                                "content": content.strip(),
                                "profile": author_profile,
                                "time": timestamp,
                            })
                except Exception:
                    continue

            return comments

        except Exception as e:
            console.print(f"[red]Error scanning comments: {e}[/red]")
            return []

    async def scan_all_post_comments(self):
        console.print("[bold blue]Scanning for new comments...[/bold blue]")
        posts = self.db.get_all_posts()
        all_new_comments = []

        for post in posts[:5]:
            comments = await self.scan_comments_on_post(post["post_url"])
            all_new_comments.extend(comments)
            await self.session.random_delay(2, 4)

        if all_new_comments:
            console.print(f"[green]Found {len(all_new_comments)} new comments![/green]")
        else:
            console.print("[yellow]No new comments found.[/yellow]")

        return all_new_comments

    async def get_pending_comments(self):
        pending = self.db.get_unprocessed_comments()
        return pending
