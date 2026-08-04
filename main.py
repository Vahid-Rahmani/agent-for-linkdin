"""
LinkedIn AI Agent - Main Orchestrator
Run this file to execute the full automation pipeline.
"""
import asyncio
import sys
from rich.console import Console
from rich.panel import Panel

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

console = Console()


async def main():
    from auth.session_manager import SessionManager
    from auth.login_handler import LoginHandler
    from monitor.profile_monitor import ProfileMonitor
    from monitor.post_monitor import PostMonitor
    from monitor.comment_monitor import CommentMonitor
    from monitor.message_monitor import MessageMonitor
    from ai.post_generator import PostGenerator
    from automation.comment_responder import CommentResponder
    from automation.message_responder import MessageResponder
    from reports.report_generator import ReportGenerator

    console.print(Panel(
        "[bold cyan]LinkedIn AI Agent[/bold cyan]\n"
        "Automate your LinkedIn presence with AI\n\n"
        "Commands:\n"
        "  python main.py login    - First-time login\n"
        "  python main.py monitor  - Check activity\n"
        "  python main.py post     - Generate & publish post\n"
        "  python main.py reply    - Reply to pending items\n"
        "  python main.py report   - Generate report\n"
        "  python main.py run      - Full automation cycle",
        title="LinkedIn AI Agent v1.0",
        border_style="blue",
    ))

    if len(sys.argv) < 2:
        console.print("\n[yellow]Usage: python main.py <command>[/yellow]")
        console.print("Run 'python main.py --help' for available commands.\n")
        return

    command = sys.argv[1].lower()

    session = SessionManager()
    try:
        if command == "login":
            handler = LoginHandler(session)
            await handler.manual_login()
            console.print("[bold green]Login complete![/bold green]")

        elif command == "monitor":
            page = await _get_page(session)
            profile = ProfileMonitor(session, page)
            await profile.get_profile_summary()

            post_monitor = PostMonitor(session, page)
            posts = await post_monitor.get_my_posts()
            console.print(f"\n[green]Found {len(posts)} posts[/green]")

            comment_monitor = CommentMonitor(session, page)
            await comment_monitor.scan_all_post_comments()

            msg_monitor = MessageMonitor(session, page)
            await msg_monitor.scan_messages()

        elif command == "post":
            page = await _get_page(session)

            from github.client import GitHubClient
            from ai.post_generator import PostGenerator
            from ai.image_generator import ImageGenerator
            from automation.publisher import Publisher

            gh = GitHubClient()
            summary = gh.build_summary()
            if not summary:
                summary = "Working on an open-source LinkedIn automation agent in Python."

            image_gen = ImageGenerator()
            context = await image_gen.analyze_context(summary)
            image_path = image_gen.generate_image(context)

            generator = PostGenerator()
            content = await generator.generate_post_from_github(summary, style=context["style"])

            console.print(f"\n[bold cyan]Generated Post:[/bold cyan]\n{content}\n")

            publisher = Publisher(session, page)
            await publisher.publish_post(content, image_path=image_path)

        elif command == "reply":
            page = await _get_page(session)

            comment_resp = CommentResponder(session, page)
            await comment_resp.respond_to_all_pending()

            msg_resp = MessageResponder(session, page)
            await msg_resp.respond_to_all_pending()

        elif command == "report":
            reporter = ReportGenerator()
            reporter.generate_report()

        elif command == "run":
            page = await _get_page(session)

            console.print("\n[bold]Phase 1: Monitoring...[/bold]")
            profile = ProfileMonitor(session, page)
            await profile.get_profile_summary()

            post_monitor = PostMonitor(session, page)
            await post_monitor.update_all_post_metrics()

            comment_monitor = CommentMonitor(session, page)
            await comment_monitor.scan_all_post_comments()

            msg_monitor = MessageMonitor(session, page)
            await msg_monitor.scan_messages()

            console.print("\n[bold]Phase 2: Responding...[/bold]")
            comment_resp = CommentResponder(session, page)
            await comment_resp.respond_to_all_pending()

            msg_resp = MessageResponder(session, page)
            await msg_resp.respond_to_all_pending()

            console.print("\n[bold]Phase 3: Auto-posting from GitHub activity...[/bold]")
            from github.client import GitHubClient
            from ai.post_generator import PostGenerator
            from ai.image_generator import ImageGenerator
            from automation.publisher import Publisher

            gh = GitHubClient()
            summary = gh.build_summary()
            if not summary:
                summary = "Working on an open-source LinkedIn automation agent in Python."

            image_gen = ImageGenerator()
            context = await image_gen.analyze_context(summary)
            image_path = image_gen.generate_image(context)

            generator = PostGenerator()
            content = await generator.generate_post_from_github(summary, style=context["style"])
            console.print(f"\n[bold cyan]Generated Post:[/bold cyan]\n{content}\n")

            publisher = Publisher(session, page)
            await publisher.publish_post(content, image_path=image_path)

            console.print("\n[bold]Phase 4: Report...[/bold]")
            reporter = ReportGenerator()
            reporter.generate_report()

            console.print("\n[bold green]Full cycle complete![/bold green]")

        else:
            console.print(f"[red]Unknown command: {command}[/red]")

    finally:
        await session.close()


async def _get_page(session):
    from auth.login_handler import LoginHandler
    handler = LoginHandler(session)
    return await handler.get_page()


if __name__ == "__main__":
    asyncio.run(main())
