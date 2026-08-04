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
            from google import genai
            self.client = genai.Client(api_key=self.settings.GOOGLE_GEMINI_API_KEY)
            console.print("[green]Google Gemini AI client initialized[/green]")
        except Exception as e:
            console.print(f"[red]Error initializing Gemini client: {e}[/red]")
            console.print("[yellow]Please set GOOGLE_GEMINI_API_KEY in .env file[/yellow]")

    async def generate(self, prompt, system_role="linkedin_expert", temperature=0.7):
        if not self.client:
            return "AI client not initialized. Please check your API key."

        system_prompt = SYSTEM_PROMPTS.get(system_role, SYSTEM_PROMPTS["linkedin_expert"])

        try:
            response = self.client.models.generate_content(
                model=self.settings.GEMINI_MODEL,
                contents=f"{system_prompt}\n\nUser request:\n{prompt}",
                config={
                    "temperature": temperature,
                    "max_output_tokens": 2048,
                },
            )
            return response.text
        except Exception as e:
            console.print(f"[red]AI generation error: {e}[/red]")
            return f"Error generating response: {e}"
