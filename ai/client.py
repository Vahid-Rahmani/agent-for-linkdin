from rich.console import Console
from config.settings import Settings

console = Console()

SYSTEM_PROMPTS = {
    "linkedin_expert": """You are a LinkedIn content expert with 10+ years of experience creating viral professional content.
You understand the LinkedIn algorithm deeply and know how to maximize engagement while maintaining authenticity.
Your posts are always professional, engaging, and technically accurate.
You use storytelling to make technical topics accessible.
You know that posts with 150-300 words perform best on LinkedIn.
You always include a call-to-action or question to encourage engagement.""",

    "reply_expert": """You are a professional networking expert who crafts thoughtful, engaging responses.
Your replies are:
- Concise (2-4 sentences)
- Add value to the conversation
- Encourage further discussion
- Professional but warm in tone
- Never generic or copy-paste looking
- Personalized to the specific comment or message""",

    "post_improver": """You are an expert at optimizing LinkedIn posts for maximum engagement.
You know that:
- Posts with storytelling get 3x more engagement
- Questions at the end increase comments by 50%
- Emoji usage should be strategic (2-3 per post max)
- Line breaks improve readability
- Personal experiences resonate more than generic advice
- The first 2 lines are crucial (they appear before "...see more")""",
}


class AIClient:
    def __init__(self):
        self.settings = Settings()
        self.client = None
        self._init_client()

    def _init_client(self):
        try:
            from openai import OpenAI
            self.client = OpenAI(
                api_key=self.settings.OPENCODE_API_KEY,
                base_url=self.settings.OPENCODE_BASE_URL,
            )
            console.print("[green]OpenCode Zen AI client initialized (Big Pickle model)[/green]")
        except Exception as e:
            console.print(f"[red]Error initializing OpenCode client: {e}[/red]")
            console.print("[yellow]Please set OPENCODE_API_KEY in .env file[/yellow]")

    async def generate(self, prompt, system_role="linkedin_expert", temperature=0.7):
        if not self.client:
            return "AI client not initialized. Please check your API key."

        system_prompt = SYSTEM_PROMPTS.get(system_role, SYSTEM_PROMPTS["linkedin_expert"])

        try:
            response = self.client.chat.completions.create(
                model=self.settings.OPENCODE_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=2048,
            )
            return response.choices[0].message.content
        except Exception as e:
            console.print(f"[red]AI generation error: {e}[/red]")
            return f"Error generating response: {e}"
