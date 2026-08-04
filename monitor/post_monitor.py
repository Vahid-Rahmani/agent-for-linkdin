import asyncio
from rich.console import Console
from config.settings import Settings
from config.constants import LinkedInUrls
from database.local_db import Database
from auth.session_manager import SessionManager

console = Console()


class PostMonitor:
    def __init__(self, session: SessionManager, page):
        self.session = session
        self.page = page
        self.db = Database()
        self.settings = Settings()

    async def get_my_posts(self):
        try:
            await self.page.goto(self.settings.LINKEDIN_PROFILE_URL, wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(3)

            posts = []
            post_elements = await self.page.query_selector_all("div.feed-shared-update-v2")

            for post_el in post_elements[:10]:
                try:
                    content_el = await post_el.query_selector("span.feed-shared-text__text")
                    content = await content_el.inner_text() if content_el else ""

                    time_el = await post_el.query_selector("span.feed-shared-actor__sub-description")
                    time_text = await time_el.inner_text() if time_el else ""

                    link_el = await post_el.query_selector("a.app-aware-link")
                    link = await link_el.get_attribute("href") if link_el else ""

                    stats = await self._get_post_stats(post_el)

                    post_data = {
                        "content": content[:200],
                        "time": time_text,
                        "url": link,
                        "likes": stats.get("likes", 0),
                        "comments": stats.get("comments", 0),
                        "shares": stats.get("shares", 0),
                    }
                    posts.append(post_data)

                    if link:
                        self.db.save_post(link, "Vahid Rahmani", content)

                except Exception as e:
                    continue

            return posts

        except Exception as e:
            console.print(f"[red]Error fetching posts: {e}[/red]")
            return []

    async def _get_post_stats(self, post_el):
        stats = {"likes": 0, "comments": 0, "shares": 0}
        try:
            stats_el = await post_el.query_selector("span.social-details-social-counts__reactions-count")
            if stats_el:
                text = await stats_el.inner_text()
                stats["likes"] = self._parse_number(text)

            comments_el = await post_el.query_selector("button.social-details-social-counts__comments")
            if comments_el:
                text = await comments_el.inner_text()
                stats["comments"] = self._parse_number(text)

            shares_el = await post_el.query_selector("button.social-details-social-counts__shares")
            if shares_el:
                text = await shares_el.inner_text()
                stats["shares"] = self._parse_number(text)
        except Exception:
            pass
        return stats

    @staticmethod
    def _parse_number(text):
        text = text.strip().replace(",", "").replace(".", "")
        if "k" in text.lower():
            return int(float(text.lower().replace("k", "")) * 1000)
        if "m" in text.lower():
            return int(float(text.lower().replace("m", "")) * 1000000)
        try:
            return int(text)
        except ValueError:
            return 0

    async def update_all_post_metrics(self):
        console.print("[bold blue]Updating post metrics...[/bold blue]")
        posts = await self.get_my_posts()
        for post in posts:
            if post.get("url"):
                self.db.update_post_metrics(
                    post["url"],
                    post.get("likes", 0),
                    post.get("comments", 0),
                    post.get("shares", 0),
                    0,
                )
        console.print(f"[green]Updated metrics for {len(posts)} posts[/green]")
        return posts
