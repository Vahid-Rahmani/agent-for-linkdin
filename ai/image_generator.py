from datetime import datetime
from pathlib import Path
from rich.console import Console
from ai.client import AIClient
from config.settings import Settings

console = Console()

SERIOUS_STYLE_PREFIX = (
    "Professional realistic conceptual image, high detail, clean modern tech aesthetic, "
    "soft studio lighting, corporate style, 4k quality, no text, no watermark"
)

FUNNY_STYLE_PREFIX = (
    "Witty humorous cartoon illustration, flat vector style, playful bright colors, "
    "meme-inspired energy, funny relatable developer scene, no text, no watermark"
)


class ImageGenerator:
    def __init__(self):
        self.settings = Settings()
        self.ai = AIClient()

    async def analyze_context(self, repo_summary):
        console.print("[blue]Analyzing repo activity to pick image style...[/blue]")

        prompt = f"""Analyze the following GitHub repository activity summary and classify the mood/vibe:

{repo_summary}

Return a JSON object with exactly these fields:
- "style": either "serious" or "funny"
  (serious = technical milestone, clean feature release, production progress, professional work;
   funny = relatable bug, silly commit messages, funny naming, chaotic development, meme-worthy moments)
- "keywords": a comma-separated list of 3-5 concrete visual keywords describing the main theme
  (e.g. "github octopus, bug in a cage, code lines, rocket launch, coffee and laptop")
- "image_prompt": one short English sentence (max 15 words) describing the scene for the image,
  matching the chosen style

Output ONLY the JSON object, no extra text."""

        raw = await self.ai.generate(prompt, system_role="linkedin_expert", temperature=0.3)
        parsed = self._parse_json(raw)
        if parsed:
            return parsed

        return {
            "style": "serious",
            "keywords": "software development, github, code",
            "image_prompt": "A developer pushing code to a repository with a rocket launch",
        }

    def _parse_json(self, raw):
        import json
        import re

        if not raw:
            return None
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not match:
            return None
        try:
            data = json.loads(match.group(0))
            style = data.get("style", "serious")
            if style not in ("serious", "funny"):
                style = "serious"
            return {
                "style": style,
                "keywords": data.get("keywords", ""),
                "image_prompt": data.get("image_prompt", ""),
            }
        except Exception:
            return None

    def build_prompt(self, context):
        style_prefix = (
            SERIOUS_STYLE_PREFIX if context.get("style") == "serious" else FUNNY_STYLE_PREFIX
        )
        base = context.get("image_prompt") or context.get("keywords", "github repository")
        return f"{style_prefix}, {base}"

    def generate_image(self, context):
        import requests
        from urllib.parse import quote

        prompt = self.build_prompt(context)
        output_dir = Path(self.settings.IMAGE_OUTPUT_DIR)
        output_dir.mkdir(parents=True, exist_ok=True)

        filename = f"post_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        output_path = output_dir / filename

        url = (
            f"https://image.pollinations.ai/prompt/{quote(prompt)}"
            f"?width={self.settings.IMAGE_WIDTH}"
            f"&height={self.settings.IMAGE_HEIGHT}"
            f"&nologo=true&model=flux"
        )

        console.print(f"[blue]Generating image via Pollinations.ai ({context.get('style')} style)...[/blue]")

        try:
            response = requests.get(url, timeout=120)
            response.raise_for_status()
            output_path.write_bytes(response.content)
            console.print(f"[green]Image saved to {output_path}[/green]")
            return str(output_path)
        except Exception as e:
            console.print(f"[red]Image generation failed: {e}[/red]")
            return None
