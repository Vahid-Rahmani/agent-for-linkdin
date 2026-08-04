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


MODEL_PRIORITY = ["turbo", "sana", "flux", "gptimage", "nanobanana"]
MODELS_URL = "https://image.pollinations.ai/models"
MAX_ATTEMPTS = 4
RETRY_TIMEOUT = 120
TOTAL_DEADLINE = 180
SQUARE_FALLBACK = (1024, 1024)


class ImageGenerator:
    def __init__(self):
        self.settings = Settings()
        self.ai = AIClient()
        self._models = None
        self._api_key = self.settings.POLLINATIONS_API_KEY

    def _pick_model(self):
        if self._models is None:
            self._models = self._fetch_models()
        if self._models:
            for candidate in MODEL_PRIORITY:
                if candidate in self._models:
                    return candidate
            return self._models[0]
        return self.settings.IMAGE_MODEL

    def _fetch_models(self):
        try:
            import requests

            headers = self._headers()
            response = requests.get(MODELS_URL, headers=headers, timeout=20)
            response.raise_for_status()
            models = response.json()
            if isinstance(models, list) and models:
                console.print(f"[blue]Available Pollinations models: {', '.join(models)}[/blue]")
                return models
        except Exception as e:
            console.print(f"[yellow]Could not fetch model list: {e}[/yellow]")
        return None

    def _headers(self):
        if self._api_key:
            return {"Authorization": f"Bearer {self._api_key}"}
        return {}

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
        import time

        from urllib.parse import quote

        prompt = self.build_prompt(context)
        output_dir = Path(self.settings.IMAGE_OUTPUT_DIR)
        output_dir.mkdir(parents=True, exist_ok=True)

        model = self._pick_model()
        console.print(
            f"[blue]Generating image via Pollinations.ai ({context.get('style')} style, {model})...[/blue]"
        )

        deadline = time.time() + TOTAL_DEADLINE
        size_candidates = self._size_candidates()
        stopped = False

        for attempt in range(1, MAX_ATTEMPTS + 1):
            if time.time() > deadline or stopped:
                break
            candidates = [model] if attempt == 1 else self._remaining_models(model)
            for m in candidates:
                if stopped:
                    break
                for width, height in size_candidates:
                    if time.time() > deadline or stopped:
                        break
                    url = (
                        f"https://image.pollinations.ai/prompt/{quote(prompt)}"
                        f"?width={width}"
                        f"&height={height}"
                        f"&nologo=true&model={m}"
                    )

                    result = self._request_image(url)
                    if isinstance(result, dict):
                        output_path = self._save_image(result)
                        if output_path:
                            console.print(f"[green]Image saved to {output_path}[/green]")
                            return output_path
                        return None

                    if result == "payment_required":
                        stopped = True
                        break
                    if result == "rate_limited":
                        wait = 15 + attempt * 5
                        console.print(f"[yellow]Queue full (429). Waiting {wait}s and retrying...[/yellow]")
                        time.sleep(wait)
                    else:
                        wait = 5 + attempt * 3
                        console.print(f"[yellow]Model '{m}' {width}x{height} failed. Waiting {wait}s and retrying...[/yellow]")
                        time.sleep(wait)

        if stopped:
            console.print(
                "[yellow]Image generation needs a Pollinations API key. "
                "Set POLLINATIONS_API_KEY in .env (free at https://enter.pollinations.ai).[/yellow]"
            )
        else:
            console.print("[red]Image generation failed after all retries.[/red]")
        return self._create_placeholder(output_dir)

    def _size_candidates(self):
        width = self.settings.IMAGE_WIDTH
        height = self.settings.IMAGE_HEIGHT
        if width == height:
            return [(width, height)]
        if self._api_key:
            return [(width, height)]
        return [(width, height), SQUARE_FALLBACK]

    def _remaining_models(self, current_model):
        listed = self._models or []
        ordered = MODEL_PRIORITY + [m for m in listed if m not in MODEL_PRIORITY]
        if self.settings.IMAGE_MODEL not in ordered:
            ordered.append(self.settings.IMAGE_MODEL)
        remaining = [m for m in ordered if m != current_model]
        return remaining or [current_model]

    def _request_image(self, url):
        import requests

        try:
            response = requests.get(url, headers=self._headers(), timeout=RETRY_TIMEOUT)
            if response.status_code == 200 and response.content:
                return {"content": response.content, "content_type": response.headers.get("Content-Type", "")}
            if response.status_code == 429:
                return "rate_limited"
            body = response.text or ""
            if "PAYMENT_REQUIRED" in body or "Insufficient balance" in body:
                console.print("[yellow]Pollinations anonymous image balance exhausted (402).[/yellow]")
                return "payment_required"
            console.print(f"[yellow]Pollinations returned status {response.status_code}[/yellow]")
            return f"http_{response.status_code}"
        except Exception as e:
            console.print(f"[yellow]Request error: {e}[/yellow]")
            return "request_error"

    def _save_image(self, result):
        try:
            content_type = result.get("content_type", "")
            if "png" in content_type:
                extension = "png"
            elif "webp" in content_type:
                extension = "webp"
            else:
                extension = "jpg"

            filename = f"post_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{extension}"
            output_path = Path(self.settings.IMAGE_OUTPUT_DIR) / filename
            output_path.write_bytes(result["content"])
            return str(output_path)
        except Exception as e:
            console.print(f"[red]Failed to save image: {e}[/red]")
            return None

    def _create_placeholder(self, output_dir):
        import struct
        import zlib

        width, height = self.settings.IMAGE_WIDTH, self.settings.IMAGE_HEIGHT
        r, g, b = 10, 102, 194

        ihdr_data = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
        raw = b"".join(b"\x00" + bytes((r, g, b)) * width for _ in range(height))

        def chunk(tag, data):
            return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

        png = b"\x89PNG\r\n\x1a\n"
        png += chunk(b"IHDR", ihdr_data)
        png += chunk(b"IDAT", zlib.compress(raw, 9))
        png += chunk(b"IEND", b"")

        filename = f"post_{datetime.now().strftime('%Y%m%d_%H%M%S')}_placeholder.png"
        output_path = Path(output_dir) / filename
        output_path.write_bytes(png)
        console.print(f"[yellow]Generated placeholder image: {output_path}[/yellow]")
        return str(output_path)
