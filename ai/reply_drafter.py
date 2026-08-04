from rich.console import Console
from ai.client import AIClient

console = Console()


class ReplyDrafter:
    def __init__(self):
        self.ai = AIClient()

    async def draft_reply_to_comment(self, comment, post_context, tone="professional"):
        prompt = f"""Draft a reply to this LinkedIn comment:

Comment from {comment.get('author', 'someone')}: {comment.get('content', '')}

Context (the post they commented on): {post_context[:200] if post_context else 'N/A'}

Requirements:
1. Acknowledge their specific comment
2. Add value or insight to the conversation
3. Encourage further discussion
4. Maintain a {tone} tone
5. Keep it concise (2-4 sentences)
6. Make it personalized and genuine
7. Never sound generic or copy-paste

Draft a thoughtful, engaging reply:"""

        console.print(f"[blue]Drafting reply to {comment.get('author', 'someone')}...[/blue]")
        result = await self.ai.generate(prompt, system_role="reply_expert")
        return result

    async def draft_reply_to_message(self, message, tone="professional"):
        prompt = f"""Draft a reply to this LinkedIn message:

From: {message.get('sender', 'someone')}
Message: {message.get('content', '')}

Requirements:
1. Address them appropriately
2. Respond directly to their message
3. Be helpful and informative
4. Maintain a {tone} tone
5. Keep it concise but complete
6. Sound natural and human
7. Include a follow-up if appropriate

Draft a professional reply:"""

        console.print(f"[blue]Drafting reply to message from {message.get('sender', 'someone')}...[/blue]")
        result = await self.ai.generate(prompt, system_role="reply_expert")
        return result

    async def draft_thank_you_reply(self, comment_or_message):
        prompt = f"""Draft a thank you reply for this LinkedIn interaction:

Content: {comment_or_message.get('content', '')}
From: {comment_or_message.get('author', comment_or_message.get('sender', 'someone'))}

Requirements:
1. Express genuine gratitude
2. Reference something specific from their message
3. Keep it brief and warm
4. Encourage continued engagement

Draft a sincere thank you reply:"""

        console.print("[blue]Drafting thank you reply...[/blue]")
        result = await self.ai.generate(prompt, system_role="reply_expert")
        return result
