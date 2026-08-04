from rich.console import Console
from ai.client import AIClient

console = Console()


class PostImprover:
    def __init__(self):
        self.ai = AIClient()

    async def improve_post(self, original_post, improvement_focus="engagement"):
        prompt = f"""Improve this LinkedIn post for better {improvement_focus}:

Original post:
---
{original_post}
---

Improvement requirements:
1. Keep the core message intact
2. Make the hook (first line) more compelling
3. Improve readability with better line breaks
4. Add a stronger call-to-action
5. Optimize for LinkedIn algorithm
6. Make it more engaging and shareable
7. Add relevant hashtags if missing
8. Ensure 150-300 word count
9. Make it sound natural, not AI-generated

Provide the improved version with a brief explanation of changes made."""

        console.print(f"[blue]Improving post for better {improvement_focus}...[/blue]")
        result = await self.ai.generate(prompt, system_role="post_improver")
        return result

    async def make_more_engaging(self, original_post):
        prompt = f"""Make this LinkedIn post more engaging:

---
{original_post}
---

Focus on:
1. Stronger emotional hook
2. Better storytelling
3. More relatable language
4. Clearer value proposition
5. Compelling question at the end
6. Strategic emoji usage

Provide the more engaging version."""

        console.print("[blue]Making post more engaging...[/blue]")
        result = await self.ai.generate(prompt, system_role="post_improver")
        return result

    async def optimize_for_algorithm(self, original_post):
        prompt = f"""Optimize this LinkedIn post for the LinkedIn algorithm:

---
{original_post}
---

Algorithm optimization requirements:
1. First 2 lines must be a strong hook (before "...see more")
2. Use short paragraphs (1-2 sentences each)
3. Include line breaks for readability
4. Add 5-8 relevant hashtags
5. Include a question to boost comments
6. Avoid external links (they reduce reach)
7. Use "I" statements for authenticity
8. Keep under 300 words for optimal reach

Provide the optimized version."""

        console.print("[blue]Optimizing for LinkedIn algorithm...[/blue]")
        result = await self.ai.generate(prompt, system_role="post_improver")
        return result
