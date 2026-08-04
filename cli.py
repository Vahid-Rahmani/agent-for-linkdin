import asyncio
import click
from rich.console import Console
from rich.panel import Panel

console = Console()


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """LinkedIn AI Agent - Automate your LinkedIn presence with AI"""
    pass


@cli.command()
def login():
    """First-time login to LinkedIn (manual)"""
    asyncio.run(_login())


async def _login():
    from auth.session_manager import SessionManager
    from auth.login_handler import LoginHandler

    session = SessionManager()
    try:
        handler = LoginHandler(session)
        await handler.manual_login()
        console.print(Panel("[bold green]Login complete![/bold green] Session saved."))
    finally:
        await session.close()


@cli.command()
def monitor():
    """Check LinkedIn activity (profile, posts, comments, messages)"""
    asyncio.run(_monitor())


async def _monitor():
    from auth.session_manager import SessionManager
    from auth.login_handler import LoginHandler
    from monitor.profile_monitor import ProfileMonitor
    from monitor.post_monitor import PostMonitor
    from monitor.comment_monitor import CommentMonitor
    from monitor.message_monitor import MessageMonitor

    session = SessionManager()
    try:
        login_handler = LoginHandler(session)
        page = await login_handler.get_page()

        profile = ProfileMonitor(session, page)
        await profile.get_profile_summary()

        post_monitor = PostMonitor(session, page)
        posts = await post_monitor.get_my_posts()
        console.print(f"\n[green]Found {len(posts)} posts[/green]")
        for p in posts[:5]:
            console.print(f"  - [cyan]{p.get('content', '')[:80]}...[/cyan]")
            console.print(f"    Likes: {p.get('likes', 0)} | Comments: {p.get('comments', 0)}")

        comment_monitor = CommentMonitor(session, page)
        comments = await comment_monitor.scan_all_post_comments()
        console.print(f"\n[green]Found {len(comments)} new comments[/green]")

        msg_monitor = MessageMonitor(session, page)
        messages = await msg_monitor.scan_messages()
        console.print(f"[green]Found {len(messages)} new messages[/green]")

    finally:
        await session.close()


@cli.command()
def post():
    """Generate & publish a LinkedIn post from GitHub activity (automatic)"""
    asyncio.run(_post())


async def _post():
    from auth.session_manager import SessionManager
    from auth.login_handler import LoginHandler
    from github.client import GitHubClient
    from ai.post_generator import PostGenerator
    from ai.image_generator import ImageGenerator
    from automation.publisher import Publisher

    session = SessionManager()
    try:
        login_handler = LoginHandler(session)
        page = await login_handler.get_page()

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

    finally:
        await session.close()


@cli.command()
@click.argument("post_url")
@click.option("--focus", "-f", default="engagement", help="Focus: engagement, algorithm, or general")
def improve(post_url, focus):
    """Improve an existing LinkedIn post"""
    asyncio.run(_improve(post_url, focus))


async def _improve(post_url, focus):
    from auth.session_manager import SessionManager
    from auth.login_handler import LoginHandler
    from automation.post_upgrader import PostUpgrader

    session = SessionManager()
    try:
        login_handler = LoginHandler(session)
        page = await login_handler.get_page()

        upgrader = PostUpgrader(session, page)
        await upgrader.improve_post(post_url, focus=focus)

    finally:
        await session.close()


@cli.command()
def reply():
    """Reply to pending comments and messages"""
    asyncio.run(_reply())


async def _reply():
    from auth.session_manager import SessionManager
    from auth.login_handler import LoginHandler
    from automation.comment_responder import CommentResponder
    from automation.message_responder import MessageResponder

    session = SessionManager()
    try:
        login_handler = LoginHandler(session)
        page = await login_handler.get_page()

        comment_resp = CommentResponder(session, page)
        comment_results = await comment_resp.respond_to_all_pending()
        console.print(f"[green]Comment replies: {sum(comment_results)} sent[/green]")

        msg_resp = MessageResponder(session, page)
        msg_results = await msg_resp.respond_to_all_pending()
        console.print(f"[green]Message replies: {sum(msg_results)} sent[/green]")

    finally:
        await session.close()


@cli.command()
def report():
    """Generate activity report"""
    from reports.report_generator import ReportGenerator
    reporter = ReportGenerator()
    reporter.generate_report()


@cli.command()
def run():
    """Run full automation cycle: monitor -> auto-post -> reply -> report"""
    asyncio.run(_run())


async def _run():
    from auth.session_manager import SessionManager
    from auth.login_handler import LoginHandler
    from monitor.profile_monitor import ProfileMonitor
    from monitor.post_monitor import PostMonitor
    from monitor.comment_monitor import CommentMonitor
    from monitor.message_monitor import MessageMonitor
    from automation.comment_responder import CommentResponder
    from automation.message_responder import MessageResponder
    from automation.publisher import Publisher
    from github.client import GitHubClient
    from ai.post_generator import PostGenerator
    from ai.image_generator import ImageGenerator
    from reports.report_generator import ReportGenerator

    session = SessionManager()
    try:
        login_handler = LoginHandler(session)
        page = await login_handler.get_page()

        console.print("\n[bold]Phase 1: Monitoring LinkedIn...[/bold]")
        profile = ProfileMonitor(session, page)
        await profile.get_profile_summary()

        post_monitor = PostMonitor(session, page)
        await post_monitor.update_all_post_metrics()

        comment_monitor = CommentMonitor(session, page)
        await comment_monitor.scan_all_post_comments()

        msg_monitor = MessageMonitor(session, page)
        await msg_monitor.scan_messages()

        console.print("\n[bold]Phase 2: Responding to comments & messages...[/bold]")
        comment_resp = CommentResponder(session, page)
        await comment_resp.respond_to_all_pending()

        msg_resp = MessageResponder(session, page)
        await msg_resp.respond_to_all_pending()

        console.print("\n[bold]Phase 3: Auto-posting from GitHub activity...[/bold]")
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

        console.print("\n[bold]Phase 4: Generating report...[/bold]")
        reporter = ReportGenerator()
        reporter.generate_report()

        console.print("\n[bold green]Full cycle complete![/bold green]")

    finally:
        await session.close()


if __name__ == "__main__":
    cli()
