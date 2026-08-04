import asyncio
from pathlib import Path
from rich.console import Console
from config.settings import Settings
from config.constants import LinkedInUrls, LinkedInSelectors
from database.local_db import Database
from auth.session_manager import SessionManager

console = Console()


def _text_landed(typed, expected_words):
    typed = (typed or "").strip()
    if len(typed) < 20:
        return False
    if not expected_words:
        return True
    flat = " ".join(typed.split())
    return sum(1 for w in expected_words if w in flat) >= max(2, min(3, len(expected_words)))


class Publisher:
    def __init__(self, session: SessionManager, page):
        self.session = session
        self.page = page
        self.db = Database()
        self.settings = Settings()

    def _editor_candidates(self, dialog):
        return [
            dialog.locator('div[role="textbox"][contenteditable="true"]'),
            dialog.locator('div[contenteditable="true"]'),
            dialog.get_by_role("textbox", name="Text"),
            self.page.locator('div[role="textbox"][contenteditable="true"]'),
            self.page.locator('div[contenteditable="true"]'),
            self.page.get_by_role("textbox", name="Text"),
        ]

    async def _pick_editor(self, dialog):
        for loc in self._editor_candidates(dialog):
            try:
                if await loc.count() > 0:
                    return loc.first
            except Exception:
                continue
        return None

    async def _focus_editor(self, editor):
        try:
            await editor.focus(timeout=5000)
        except Exception:
            pass
        try:
            await self.session.human_click(self.page, editor)
        except Exception:
            pass

    async def publish_post(self, content, image_path=None):
        console.print("[bold blue]Preparing to publish post...[/bold blue]")
        console.print(f"\n[bold cyan]Post Content:[/bold cyan]\n{content}\n")

        try:
            await self.page.goto(LinkedInUrls.HOME, wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(3)
            await self.session.random_delay(3, 5)

            await self.session.human_scroll(self.page)
            await self.session.human_delay(0.5, 1.5)

            start_post = self.page.get_by_role("button", name="Start a post")
            await self.session.human_click(self.page, start_post)
            await asyncio.sleep(3)
            await self.session.random_delay(2, 3)

            dialog = self.page.locator('div[role="dialog"].share-box-v2__modal')
            if await dialog.count() == 0:
                dialog = self.page.locator('div[role="dialog"]')

            if image_path and Path(image_path).exists():
                media_btn = dialog.locator(
                    'button[aria-label="Add media"], '
                    'button[aria-label="Add a photo to your post"]'
                ).first
                await self.session.human_click(self.page, media_btn)
                file_input = dialog.locator('input[type="file"]').first
                await file_input.set_input_files(str(image_path))
                console.print("[blue]Image attached...[/blue]")
                await asyncio.sleep(2)

                next_btn = dialog.get_by_role("button", name="Next", exact=True)
                wizard_seen = False
                for _ in range(40):
                    try:
                        if await next_btn.count() > 0 and await next_btn.is_visible():
                            wizard_seen = True
                            break
                    except Exception:
                        pass
                    await asyncio.sleep(0.5)
                if not wizard_seen:
                    console.print("[yellow]Media wizard 'Next' not found; continuing without it[/yellow]")
                else:
                    await self.session.human_click(self.page, next_btn)
                    console.print("[blue]Media wizard confirmed (Next)...[/blue]")
                    await asyncio.sleep(2)
                await self.session.random_delay(2, 3)

            expected_words = [w for w in content.split() if w.isalnum()][:5]
            candidates = [loc for loc in self._editor_candidates(dialog) if await loc.count() > 0]

            editor = None
            typed_text = ""
            for attempt, candidate in enumerate(candidates, 1):
                editor = candidate.first
                await self._focus_editor(editor)
                await asyncio.sleep(0.6)
                await self.session.human_type(self.page, content)
                await asyncio.sleep(0.6)
                try:
                    typed_text = (await editor.inner_text()).strip()
                except Exception:
                    typed_text = ""
                if _text_landed(typed_text, expected_words):
                    console.print(f"[green]Composer text verified ({len(typed_text)} chars): {typed_text[:80].replace(chr(10), ' ')}...[/green]")
                    break
                console.print(
                    f"[yellow]Editor attempt {attempt} failed ({len(typed_text)} chars read back); trying next...[/yellow]"
                )
                try:
                    await editor.evaluate("el => el.innerText = ''")
                except Exception:
                    pass
                await self.session.random_delay(1, 2)
                editor = None

            if editor is None:
                console.print("[red]Could not type post text into the composer[/red]")
                self.db.log_action("post_publish", LinkedInUrls.HOME, content[:100], "error: text missing from composer")
                return False

            await self.session.random_delay(2, 3)

            post_button = None
            for loc in (
                dialog.locator('button.share-actions__primary-action').filter(has_text="Post"),
                dialog.get_by_role("button", name="Post"),
                self.page.get_by_role("button", name="Post"),
                dialog.locator('button').filter(has_text="Post"),
            ):
                try:
                    if await loc.count() > 0:
                        post_button = loc
                        break
                except Exception:
                    continue

            if post_button is None:
                console.print("[red]Post button not found in composer[/red]")
                self.db.log_action("post_publish", LinkedInUrls.HOME, content[:100], "error: post button not found")
                return False

            for _ in range(20):
                try:
                    if await post_button.is_enabled():
                        break
                except Exception:
                    pass
                await asyncio.sleep(0.5)

            await self.session.human_click(self.page, post_button)
            await self.session.random_delay(3, 5)

            self.db.log_action("post_publish", LinkedInUrls.HOME, content[:100], "success")
            console.print("[bold green]Post published successfully![/bold green]")
            return True

        except Exception as e:
            console.print(f"[red]Error publishing post: {e}[/red]")
            self.db.log_action("post_publish", LinkedInUrls.HOME, content[:100], f"error: {e}")
            return False
