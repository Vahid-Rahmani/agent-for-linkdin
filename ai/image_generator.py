from datetime import datetime
from pathlib import Path
from rich.console import Console
from ai.client import AIClient
from config.settings import Settings

console = Console()

PALETTES = [
    (
        "dark theme with neon accents",
        "deep charcoal-black background, electric cyan, hot magenta and lime green neon "
        "accents, glowing node edges, high contrast",
    ),
    (
        "light theme with professional pastels",
        "soft off-white background, muted mint, lavender, peach and sky-blue pastel nodes, "
        "gentle soft shadows, airy professional look",
    ),
    (
        "vibrant gradient theme",
        "deep navy background, rich blue-to-purple-to-orange gradient nodes, glossy highlights, "
        "energetic modern look",
    ),
    (
        "monochrome with a single accent",
        "clean white background, elegant shades of slate gray and charcoal, one vivid coral "
        "accent color for the path and numbers",
    ),
    (
        "glassmorphism theme",
        "dark frosted-glass background, translucent glass-like nodes with soft inner glows, "
        "thin white borders, subtle blur effects",
    ),
]

NODE_STYLES = [
    (
        "geometric nodes",
        "sharp-edged angular hexagonal and rectangular cards arranged neatly along the path",
    ),
    (
        "organic nodes",
        "soft rounded blob-like cards with smooth flowing curves and gentle gradients",
    ),
    (
        "3D depth nodes",
        "cards rendered with realistic 3D depth, thick shadows, layered perspective and "
        "beveled edges",
    ),
    (
        "flat minimal nodes",
        "clean flat 2D cards with generous padding, thin outlines and uncluttered layout",
    ),
]

DEFAULT_STEPS = [
    {"stage": "FOUNDATIONS", "icons": "Python, Git"},
    {"stage": "CORE FEATURES", "icons": "Playwright, SQLite"},
    {"stage": "AUTOMATION", "icons": "AI, GitHub API"},
    {"stage": "TESTING", "icons": "Pytest, CI"},
    {"stage": "DEPLOYMENT", "icons": "Docker, Linux"},
    {"stage": "HARDENING", "icons": "Rate Limits, Logging"},
]

DESIGN_STATE_FILE = "image_style_state.json"
MIN_STEPS = 5
MAX_STEPS = 7

ROADMAP_PROMPT_TEMPLATE = (
    "{palette} {node_style}. "
    "Create a clean, high-tech neon tech infographic: a horizontal flowchart of glowing "
    "nodes connected by luminous neon flow lines and arrows, symbolizing a project "
    "pipeline from start to finish. STRICTLY NO pyramids and NO abstract art.\n"
    "STRICT RULES - MOST IMPORTANT REQUIREMENT:\n"
    "- The image must contain ZERO text: no letters, no words, no numbers, no titles, "
    "no labels, no captions, no typography, no rendered characters, no gibberish or "
    "fake text of any kind anywhere in the image.\n"
    "- Absolutely nothing is spelled out. Every element is communicated purely through "
    "icons, shapes, colors and glow.\n"
    "Required structure:\n"
    "1. A clear, winding visual path or pipeline flowing left-to-right connecting the "
    "sequential milestone nodes.\n"
    "2. Distinct, prominent neon nodes or cards along the path. Each node contains ONLY "
    "2-3 bold, stylized vector icons symbolically representing that step's tools and "
    "concepts. No captions, no stage names, no numbers inside or around the nodes.\n"
    "3. Smooth glowing connectors, gradient flow lines and subtle arrows linking the nodes.\n"
    "4. A polished professional layout with strong visual hierarchy, consistent spacing "
    "and elegant, modern composition.\n"
    "Draw one node per icon set, in order, using only these symbolic icons:\n{steps_block}\n"
    "Render every icon crisp, legible and visually striking - with no text anywhere in the image."
)


def _with_numbers(steps):
    return [
        {"number": index, "stage": step["stage"], "icons": step["icons"]}
        for index, step in enumerate(steps, start=1)
    ]


MODEL_PRIORITY = ["turbo", "sana", "flux", "gptimage", "nanobanana"]
MODELS_URL = "https://image.pollinations.ai/models"
MAX_ATTEMPTS = 4
RETRY_TIMEOUT = 120
TOTAL_DEADLINE = 180
SQUARE_FALLBACK = (1024, 1024)
HF_MAX_ATTEMPTS = 3
HF_TIMEOUT = 180


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
        console.print("[blue]Analyzing repo activity to build roadmap structure...[/blue]")

        prompt = f"""Analyze the following GitHub repository activity summary and extract a structured project roadmap:

{repo_summary}

Return a JSON object with exactly these fields:
- "style": either "serious" or "funny"
  (serious = technical milestone, clean feature release, production progress, professional work;
   funny = relatable bug, silly commit messages, funny naming, chaotic development, meme-worthy moments)
  NOTE: this controls only the written post's tone, NOT the image design.
- "steps": an array of 5-7 sequential milestones, ordered from first to last, each an object with:
  - "icons": a comma-separated list of 2-3 real tool, technology or concept names that visually
    symbolize that stage (e.g. "Python, Git", "Playwright, SQLite", "Docker, CI")

Derive the icon sets from the actual commits, issues and tech visible in the summary.
These icons are used ONLY to draw symbolic vector icons in an image - no text will be rendered.

Output ONLY the JSON object, no extra text."""

        raw = await self.ai.generate(prompt, system_role="linkedin_expert", temperature=0.3)
        parsed = self._parse_json(raw)
        if parsed:
            return parsed

        palette, node_style = self._pick_design()
        return {
            "style": "serious",
            "steps": _with_numbers(DEFAULT_STEPS),
            "palette": palette,
            "node_style": node_style,
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
            raw_steps = data.get("steps") or []
            if not isinstance(raw_steps, list):
                raw_steps = []
            steps = []
            for step in raw_steps:
                if not isinstance(step, dict):
                    continue
                icons = (step.get("icons") or "").strip()
                if icons:
                    steps.append({"icons": icons})
            if len(steps) < MIN_STEPS:
                steps = DEFAULT_STEPS
            elif len(steps) > MAX_STEPS:
                steps = steps[:MAX_STEPS]
            steps = _with_numbers(steps)
            style = data.get("style", "serious")
            if style not in ("serious", "funny"):
                style = "serious"
            palette, node_style = self._pick_design()
            return {
                "style": style,
                "steps": steps,
                "palette": palette,
                "node_style": node_style,
            }
        except Exception:
            return None

    def _pick_design(self):
        import json
        import random

        state_path = Path(self.settings.IMAGE_OUTPUT_DIR).parent / DESIGN_STATE_FILE
        last = {}
        try:
            if state_path.exists():
                last = json.loads(state_path.read_text(encoding="utf-8"))
        except Exception:
            last = {}

        last_palette = last.get("palette")
        last_node_style = last.get("node_style")

        palette_candidates = [name for name, _ in PALETTES if name != last_palette]
        if not palette_candidates:
            palette_candidates = [name for name, _ in PALETTES]
        node_candidates = [name for name, _ in NODE_STYLES if name != last_node_style]
        if not node_candidates:
            node_candidates = [name for name, _ in NODE_STYLES]

        palette = random.choice(palette_candidates)
        node_style = random.choice(node_candidates)

        try:
            state_path.parent.mkdir(parents=True, exist_ok=True)
            state_path.write_text(
                json.dumps({"palette": palette, "node_style": node_style}),
                encoding="utf-8",
            )
        except Exception:
            pass
        return palette, node_style

    def _palette_desc(self, name):
        for palette_name, description in PALETTES:
            if palette_name == name:
                return description
        return name

    def _node_style_desc(self, name):
        for style_name, description in NODE_STYLES:
            if style_name == name:
                return description
        return name

    def build_prompt(self, context):
        palette = self._palette_desc(context.get("palette") or PALETTES[0][0])
        node_style = self._node_style_desc(context.get("node_style") or NODE_STYLES[0][0])
        steps = context.get("steps") or _with_numbers(DEFAULT_STEPS)
        if len(steps) < MIN_STEPS:
            steps = _with_numbers(DEFAULT_STEPS)

        steps_block = "\n".join(
            f"- {step.get('icons') or ''}"
            for step in steps
        )

        return ROADMAP_PROMPT_TEMPLATE.format(
            palette=palette,
            node_style=node_style,
            steps_block=steps_block,
        )

    def generate_image(self, context):
        prompt = self.build_prompt(context)
        output_dir = Path(self.settings.IMAGE_OUTPUT_DIR)
        output_dir.mkdir(parents=True, exist_ok=True)

        if self.settings.HF_TOKEN:
            console.print(
                f"[blue]Generating image via Hugging Face ({self.settings.HF_MODEL}, "
                f"palette '{context.get('palette')}', {context.get('node_style')})...[/blue]"
            )
            result = self._generate_via_hf(prompt, output_dir)
            if result:
                return result
            console.print("[yellow]Hugging Face failed, falling back to Pollinations.ai...[/yellow]")
        else:
            console.print("[yellow]No HF_TOKEN set, using Pollinations.ai...[/yellow]")

        return self._generate_via_pollinations(context)

    def _generate_via_hf(self, prompt, output_dir):
        import time

        import requests

        url = f"{self.settings.HF_API_URL}/{self.settings.HF_MODEL}"
        headers = {
            "Authorization": f"Bearer {self.settings.HF_TOKEN}",
            "Content-Type": "application/json",
        }
        payload = {
            "inputs": prompt,
            "parameters": {
                "width": self.settings.IMAGE_WIDTH,
                "height": self.settings.IMAGE_HEIGHT,
                "num_inference_steps": 28,
                "guidance_scale": 5.0,
                "negative_prompt": (
                    "blurry, low quality, watermark, logo, abstract art, concept art, "
                    "text, letters, words, numbers, typography, labels, captions, titles, gibberish"
                ),
            },
            "options": {"wait_for_model": True},
        }

        for attempt in range(1, HF_MAX_ATTEMPTS + 1):
            try:
                response = requests.post(url, headers=headers, json=payload, timeout=HF_TIMEOUT)
                if response.status_code == 200 and response.content:
                    result = {
                        "content": response.content,
                        "content_type": response.headers.get("Content-Type", ""),
                    }
                    output_path = self._save_image(result)
                    if output_path:
                        return output_path
                    return None
                body = response.text or ""
                if response.status_code in (503, 429) or "loading" in body.lower():
                    wait = 20 + attempt * 10
                    console.print(
                        f"[yellow]HF model still loading (status {response.status_code}). "
                        f"Waiting {wait}s and retrying...[/yellow]"
                    )
                    time.sleep(wait)
                    continue
                console.print(
                    f"[yellow]Hugging Face returned status {response.status_code}: {body[:200]}[/yellow]"
                )
                return None
            except requests.exceptions.Timeout:
                console.print("[yellow]Hugging Face request timed out, retrying...[/yellow]")
            except Exception as e:
                console.print(f"[yellow]Hugging Face request error: {e}[/yellow]")
                return None
            time.sleep(5)
        return None

    def _generate_via_pollinations(self, context):
        import time

        from urllib.parse import quote

        prompt = self.build_prompt(context)
        output_dir = Path(self.settings.IMAGE_OUTPUT_DIR)
        output_dir.mkdir(parents=True, exist_ok=True)

        model = self._pick_model()
        console.print(
            f"[blue]Generating image via Pollinations.ai (palette '{context.get('palette')}', "
            f"{context.get('node_style')}, {model})...[/blue]"
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
                    negative = (
                        "text, letters, words, numbers, typography, labels, captions, titles, gibberish"
                    )
                    url = (
                        f"https://image.pollinations.ai/prompt/{quote(prompt)}"
                        f"?width={width}"
                        f"&height={height}"
                        f"&negative={quote(negative)}"
                        f"&nologo=true&model={m}"
                    )

                    result = self._request_image(url)
                    if isinstance(result, dict):
                        output_path = self._save_image(result)
                        if output_path:
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
            console.print(f"[green]Image saved to {output_path}[/green]")
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
