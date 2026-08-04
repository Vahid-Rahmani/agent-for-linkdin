from rich.console import Console
from config.settings import Settings

console = Console()


class GitHubClient:
    def __init__(self, token=None, repo=None):
        self.settings = Settings()
        self.token = token or self.settings.GITHUB_TOKEN
        self.repo = repo or self.settings.GITHUB_REPO
        self.api_url = self.settings.GITHUB_API_URL

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def _get(self, path, params=None):
        import requests

        url = f"{self.api_url}{path}"
        response = requests.get(url, headers=self._headers(), params=params, timeout=30)
        response.raise_for_status()
        return response.json()

    def get_repo_info(self):
        try:
            data = self._get(f"/repos/{self.repo}")
            return {
                "name": data.get("name", self.repo.split("/")[-1]),
                "full_name": data.get("full_name", self.repo),
                "description": data.get("description") or "",
                "language": data.get("language") or "",
                "stars": data.get("stargazers_count", 0),
                "forks": data.get("forks_count", 0),
                "updated_at": data.get("updated_at", ""),
            }
        except Exception as e:
            console.print(f"[yellow]Could not fetch repo info: {e}[/yellow]")
            return {}

    def get_latest_commits(self, limit=5):
        try:
            data = self._get(f"/repos/{self.repo}/commits", params={"per_page": limit})
            commits = []
            for item in data:
                commit = item.get("commit", {})
                author = commit.get("author", {})
                commits.append({
                    "message": commit.get("message", "").split("\n")[0],
                    "date": author.get("date", ""),
                    "author": author.get("name") or item.get("author", {}).get("login", "Unknown"),
                })
            return commits
        except Exception as e:
            console.print(f"[yellow]Could not fetch commits: {e}[/yellow]")
            return []

    def get_open_issues(self, limit=5):
        try:
            data = self._get(
                f"/repos/{self.repo}/issues",
                params={"state": "open", "per_page": limit},
            )
            issues = [
                {
                    "number": item.get("number"),
                    "title": item.get("title", ""),
                    "labels": [label.get("name", "") for label in item.get("labels", [])],
                }
                for item in data
                if "pull_request" not in item
            ]
            return issues
        except Exception as e:
            console.print(f"[yellow]Could not fetch issues: {e}[/yellow]")
            return []

    def build_summary(self):
        if not self.token:
            console.print("[red]GITHUB_TOKEN not set in .env. Skipping GitHub data.[/red]")
            return None

        console.print(f"[blue]Fetching GitHub activity for {self.repo}...[/blue]")

        info = self.get_repo_info()
        commits = self.get_latest_commits()
        issues = self.get_open_issues()

        if not info and not commits:
            console.print("[red]No GitHub data retrieved.[/red]")
            return None

        lines = []
        if info:
            lines.append(f"Repository: {info.get('full_name')}")
            if info.get("description"):
                lines.append(f"Description: {info.get('description')}")
            meta = []
            if info.get("language"):
                meta.append(f"Language: {info['language']}")
            if info.get("stars"):
                meta.append(f"Stars: {info['stars']}")
            if info.get("forks"):
                meta.append(f"Forks: {info['forks']}")
            if meta:
                lines.append(" | ".join(meta))

        if commits:
            lines.append(f"\nRecent commits ({len(commits)}):")
            for c in commits:
                lines.append(f"- {c['message']} ({c['author']}, {c['date'][:10]})")

        if issues:
            lines.append(f"\nOpen issues ({len(issues)}):")
            for i in issues:
                label_text = ", ".join(i["labels"]) if i["labels"] else "unlabeled"
                lines.append(f"- #{i['number']}: {i['title']} [{label_text}]")

        return "\n".join(lines)
