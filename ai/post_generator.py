from rich.console import Console
from ai.client import AIClient

console = Console()


class PostGenerator:
    def __init__(self):
        self.ai = AIClient()

    async def generate_post(self, topic=None, context=None, style="professional"):
        prompt = f"""Generate a LinkedIn post based on the following:

Topic: {topic if topic else 'General professional update'}
Context: {context if context else 'Recent work, achievement, or learning'}
Style: {style}

Requirements:
1. Start with a compelling hook (first line must grab attention)
2. Tell a story or share an experience
3. Include a technical insight or lesson learned
4. End with a question to encourage engagement
5. Add 5-8 relevant hashtags
6. Total length: 150-300 words
7. Use line breaks for readability
8. Add 2-3 relevant emojis strategically
9. Make it sound authentic and personal
10. Optimize for LinkedIn algorithm

The post should be about my professional work, achievements, or technical insights.
Make it engaging, informative, and shareable."""

        console.print("[blue]Generating LinkedIn post...[/blue]")
        result = await self.ai.generate(prompt, system_role="linkedin_expert")
        return result

    async def generate_post_from_code(self, code_summary, project_name=None):
        prompt = f"""Generate a LinkedIn post based on this code/project summary:

Project: {project_name if project_name else 'Recent Development Work'}
Summary: {code_summary}

Requirements:
1. Highlight the technical challenge solved
2. Show the impact or achievement
3. Make it accessible to non-technical readers
4. Include a learning or insight
5. End with a question or call-to-action
6. Add relevant hashtags (5-8)
7. Use storytelling format
8. 150-300 words
9. Professional but engaging tone

Make it sound like I'm sharing an exciting development journey."""

        console.print("[blue]Generating post from code summary...[/blue]")
        result = await self.ai.generate(prompt, system_role="linkedin_expert")
        return result

    async def generate_multiple_variations(self, topic, num_variations=3):
        variations = []
        for i in range(num_variations):
            prompt = f"""Generate LinkedIn post variation #{i+1} about: {topic}

Make this variation unique by:
{"- Focus on personal experience and emotions" if i == 0 else ""}
{"- Focus on technical details and how-to" if i == 1 else ""}
{"- Focus on industry impact and future trends" if i == 2 else ""}

150-300 words, engaging, with hashtags."""

            result = await self.ai.generate(prompt)
            variations.append({"variation": i + 1, "content": result})

        return variations
