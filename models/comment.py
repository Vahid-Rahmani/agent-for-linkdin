from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Comment:
    id: int = 0
    post_url: str = ""
    author_name: str = ""
    author_profile: str = ""
    content: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    processed: bool = False
    ai_response: str = ""
    response_sent: bool = False
