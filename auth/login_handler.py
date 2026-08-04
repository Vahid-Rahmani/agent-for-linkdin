from pathlib import Path
from rich.console import Console
from config.settings import Settings
from config.constants import LinkedInUrls, LinkedInSelectors
from auth.session_manager import SessionManager

console = Console()


class LoginHandler:
    def __init__(self, session: SessionManager):
        self.session = session
        self.settings = Settings()

    async def manual_login(self):
        console.print("[bold yellow]Manual Login Mode[/bold yellow]")
        console.print("A browser window will open. Please log in to LinkedIn manually.")
        console.print("After logging in, press Enter in this terminal to continue.\n")

        context = await self.session.start(headless=False)
        page = await context.new_page()
        await page.goto(LinkedInUrls.LOGIN)
        input("\n>>> Press Enter after you have logged in to LinkedIn... ")

        await self.session.save_session()
        console.print("[bold green]Session saved![/bold green] You won't need to log in again.")
        return page

    async def auto_login(self):
        context = await self.session.start(headless=False)
        page = await context.new_page()
        await page.goto(LinkedInUrls.HOME)
        await self.session.random_delay(2, 4)

        if "login" in page.url or "authwall" in page.url:
            console.print("[bold red]Session expired![/bold red] Please log in manually.")
            await page.goto(LinkedInUrls.LOGIN)
            input("\n>>> Press Enter after you have logged in to LinkedIn... ")
            await self.session.save_session()
            console.print("[bold green]Session saved![/bold green]")

        return page

    async def get_page(self):
        if Path(self.settings.STATE_FILE).exists():
            return await self.auto_login()
        else:
            return await self.manual_login()
