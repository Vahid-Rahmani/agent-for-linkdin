import asyncio
from rich.console import Console
from config.settings import Settings
from config.constants import LinkedInUrls
from auth.session_manager import SessionManager

console = Console()


class ProfileMonitor:
    def __init__(self, session: SessionManager, page):
        self.session = session
        self.page = page
        self.settings = Settings()

    async def get_profile_views(self):
        try:
            await self.page.goto(self.settings.LINKEDIN_PROFILE_URL, wait_until="networkidle")
            await self.session.random_delay(2, 4)

            views = "N/A"
            try:
                el = await self.page.query_selector("span.profile-views__count")
                if el:
                    views = await el.inner_text()
            except Exception:
                pass

            return {"profile_views": views}
        except Exception as e:
            console.print(f"[red]Error getting profile views: {e}[/red]")
            return {"profile_views": "Error"}

    async def get_search_appearances(self):
        try:
            await self.page.goto(self.settings.LINKEDIN_PROFILE_URL, wait_until="networkidle")
            await self.session.random_delay(2, 4)

            appearances = "N/A"
            try:
                el = await self.page.query_selector("span.search-appearances__count")
                if el:
                    appearances = await el.inner_text()
            except Exception:
                pass

            return {"search_appearances": appearances}
        except Exception as e:
            console.print(f"[red]Error getting search appearances: {e}[/red]")
            return {"search_appearances": "Error"}

    async def get_connection_count(self):
        try:
            await self.page.goto(self.settings.LINKEDIN_PROFILE_URL, wait_until="networkidle")
            await self.session.random_delay(2, 4)

            count = "N/A"
            try:
                el = await self.page.query_selector("span.t-bold")
                if el:
                    count = await el.inner_text()
            except Exception:
                pass

            return {"connection_count": count}
        except Exception as e:
            console.print(f"[red]Error getting connections: {e}[/red]")
            return {"connection_count": "Error"}

    async def get_profile_summary(self):
        console.print("[bold blue]Fetching profile summary...[/bold blue]")
        views = await self.get_profile_views()
        search = await self.get_search_appearances()
        connections = await self.get_connection_count()

        summary = {
            "profile_views": views.get("profile_views", "N/A"),
            "search_appearances": search.get("search_appearances", "N/A"),
            "connections": connections.get("connection_count", "N/A"),
        }

        console.print(f"  Profile Views: [green]{summary['profile_views']}[/green]")
        console.print(f"  Search Appearances: [green]{summary['search_appearances']}[/green]")
        console.print(f"  Connections: [green]{summary['connections']}[/green]")

        return summary
