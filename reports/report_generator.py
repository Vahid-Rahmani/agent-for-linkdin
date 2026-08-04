from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from database.local_db import Database

console = Console()


class ReportGenerator:
    def __init__(self):
        self.db = Database()

    def generate_report(self):
        console.print("\n[bold blue]═══════════════════════════════════════[/bold blue]")
        console.print("[bold blue]      LinkedIn AI Agent Activity Report[/bold blue]")
        console.print("[bold blue]═══════════════════════════════════════[/bold blue]\n")

        posts = self.db.get_all_posts()
        pending_comments = self.db.get_pending_comments_count()
        pending_messages = self.db.get_pending_messages_count()
        today_actions = self.db.get_actions_today()

        posts_table = Table(title="Posts Overview", show_header=True)
        posts_table.add_column("Metric", style="cyan")
        posts_table.add_column("Value", style="green")

        posts_table.add_row("Total Posts Tracked", str(len(posts)))
        total_likes = sum(p.get("likes", 0) for p in posts)
        total_comments = sum(p.get("comments_count", 0) for p in posts)
        total_shares = sum(p.get("shares", 0) for p in posts)
        posts_table.add_row("Total Likes", str(total_likes))
        posts_table.add_row("Total Comments", str(total_comments))
        posts_table.add_row("Total Shares", str(total_shares))

        console.print(posts_table)
        console.print()

        pending_table = Table(title="Pending Items", show_header=True)
        pending_table.add_column("Type", style="cyan")
        pending_table.add_column("Count", style="yellow")

        pending_table.add_row("Unprocessed Comments", str(pending_comments))
        pending_table.add_row("Unprocessed Messages", str(pending_messages))

        console.print(pending_table)
        console.print()

        actions_table = Table(title="Today's Actions", show_header=True)
        actions_table.add_column("Action", style="cyan")
        actions_table.add_column("Target", style="dim")
        actions_table.add_column("Status", style="green")

        for action in today_actions[:20]:
            actions_table.add_row(
                action.get("action_type", ""),
                action.get("target_url", "")[:50],
                action.get("status", ""),
            )

        console.print(actions_table)
        console.print()

        if posts:
            console.print("[bold cyan]Top Performing Posts:[/bold cyan]")
            sorted_posts = sorted(posts, key=lambda x: x.get("likes", 0), reverse=True)
            for i, post in enumerate(sorted_posts[:3], 1):
                console.print(
                    f"  {i}. Likes: {post.get('likes', 0)} | "
                    f"Comments: {post.get('comments_count', 0)} | "
                    f"Shares: {post.get('shares', 0)}"
                )
                content_preview = post.get("content", "")[:100]
                console.print(f"     [dim]{content_preview}...[/dim]\n")

        console.print(
            f"[dim]Report generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/dim]"
        )
        console.print("[bold blue]═══════════════════════════════════════[/bold blue]\n")

        return {
            "total_posts": len(posts),
            "total_likes": total_likes,
            "total_comments": total_comments,
            "total_shares": total_shares,
            "pending_comments": pending_comments,
            "pending_messages": pending_messages,
            "actions_today": len(today_actions),
        }
